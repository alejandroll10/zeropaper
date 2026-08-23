"""DeepVest MCP client — LLM-mediated market/fundamentals/options/macro terminal.

DeepVest (https://www.deepvest.ai; formerly Benjamin AI — see
deepvest.ai/articles/benjamin-ai-rebrands-to-deepvest) exposes its data and
analytics through a single remote Model Context Protocol server:

    https://api.deepvest.ai/mcp     (Streamable HTTP transport)

This module is a dependency-free (stdlib + pandas) MCP client for that server so
the pipeline can call its tools from scripts, cache every response under
data/deepvest/, and keep the call log as provenance.

Usage:
    from utils.deepvest_utils import DeepVestClient, query, list_tools
    tools = list_tools()                              # name -> description/schema
    text  = query("quick_analysis", "SPY monthly closing prices 2015-2024 as a "
                                     "markdown table with columns date, close")
    from utils.deepvest_utils import parse_markdown_tables
    df = parse_markdown_tables(text)[0]

    client = DeepVestClient()                         # explicit session
    res = client.call_tool("black_scholes_option_price_tool",
                           {"spot_price": 100, "strike_price": 100,
                            "time_to_expiry": 0.5, "risk_free_rate": 0.04,
                            "volatility": 0.25, "option_type": "call"})
    res["text"], res["structured"], res["is_error"]

CLI (from a deployed project root):
    python3 code/utils/deepvest_utils.py ping                      # auth check, no credits
    python3 code/utils/deepvest_utils.py tools [--json]            # live tool catalog
    python3 code/utils/deepvest_utils.py query <tool> "<question>" # natural-language tools
    python3 code/utils/deepvest_utils.py call  <tool> '<json-args>' # typed tools
    python3 code/utils/deepvest_utils.py cache                     # list cached responses

Authentication (documented at https://console.deepvest.ai/docs):
  * Programmatic access uses an API key created at
    https://console.deepvest.ai/dashboard/api-keys, sent as the `X-API-Key`
    header.  The key goes in `.env` as DEEPVEST_API_KEY and is read lazily,
    inside each call — never at import time, so the module imports with no .env.
  * OAuth 2.0 (browser login) is what Claude Desktop uses; it is NOT used here
    because the pipeline runs unattended.  DEEPVEST_OAUTH_TOKEN is honoured as a
    Bearer token if an operator obtained one out of band.

Cost and limits (vendor docs, 2026-08): every account gets 1,000 free credits
per month, then $0.025/credit.  Roughly 7-16 credits per analysis tool call
(quick_analysis ~10, backtests/options ~16, long SEC filing analysis ~550),
charged on token usage.  Rate limits: 3 concurrent requests, 20 requests per
minute per key (HTTP 429 with Retry-After).  402 = out of credits.

Caching: every successful tools/call is memoised to
data/deepvest/<tool>_<sha256[:16]>.json as
{"tool", "arguments", "fetched_at", "server", "response"} — the response is
LLM-generated prose/JSON, so the cache file IS the raw-data record for
provenance.  Pass refresh=True to re-query.  The response text of the same
query is not guaranteed byte-identical across calls (it is produced by a model),
so audits should compare the numbers, not the bytes.

Protocol notes (MCP 2025-03-26 / 2025-06-18 Streamable HTTP): one POST per
JSON-RPC message; `Accept: application/json, text/event-stream`; the server may
answer with plain JSON or an SSE stream; the `Mcp-Session-Id` response header
from `initialize` is echoed on later requests; `notifications/initialized`
follows `initialize`; `tools/list` is cursor-paginated; `tools/call` returns
`content[]` (text blocks) plus optional `structuredContent` and `isError`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

DEFAULT_MCP_URL = "https://api.deepvest.ai/mcp"
PROTOCOL_VERSION = "2025-06-18"
DEFAULT_CACHE_DIR = Path("data") / "deepvest"
# Vendor limit is 20 requests/minute per key; 3.1 s spacing stays under it even
# when two processes share a key only approximately.
MIN_SECONDS_BETWEEN_CALLS = 3.1
USER_AGENT = "zeropaper-deepvest-utils/1.0 (+https://github.com/alejandroll10/zeropaper)"


class DeepVestError(RuntimeError):
    """Base class for DeepVest client failures."""


class DeepVestAuthError(DeepVestError):
    """401 — missing or invalid DEEPVEST_API_KEY."""


class DeepVestCreditsError(DeepVestError):
    """402 — the account has no credits left."""


class DeepVestRateLimitError(DeepVestError):
    """429 — still rate-limited after the bounded retry budget."""


class DeepVestToolError(DeepVestError):
    """The server ran the tool and reported isError=true (e.g. 'Error running …')."""


def _load_dotenv_once() -> None:
    if getattr(_load_dotenv_once, "_done", False):
        return
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:  # pragma: no cover — dotenv is a soft dependency here
        pass
    _load_dotenv_once._done = True  # type: ignore[attr-defined]


def _credentials() -> dict[str, str]:
    """Return the auth headers for this environment, or raise DeepVestAuthError."""
    _load_dotenv_once()
    key = (os.getenv("DEEPVEST_API_KEY") or "").strip()
    if key and key.lower() not in {"your-key-here", "changeme"}:
        return {"X-API-Key": key}
    token = (os.getenv("DEEPVEST_OAUTH_TOKEN") or "").strip()
    if token:
        return {"Authorization": f"Bearer {token}"}
    raise DeepVestAuthError(
        "DEEPVEST_API_KEY is not set. Create a key at "
        "https://console.deepvest.ai/dashboard/api-keys and put "
        "DEEPVEST_API_KEY=... in .env"
    )


def _parse_sse(body: str) -> list[dict[str, Any]]:
    """Parse an SSE stream into the JSON-RPC messages it carried."""
    messages: list[dict[str, Any]] = []
    data_lines: list[str] = []
    for raw in body.splitlines() + [""]:
        line = raw.rstrip("\r")
        if line == "":
            if data_lines:
                payload = "\n".join(data_lines)
                data_lines = []
                try:
                    messages.append(json.loads(payload))
                except json.JSONDecodeError:
                    pass
            continue
        if line.startswith(":"):
            continue
        if line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    return messages


def _content_text(result: dict[str, Any]) -> str:
    parts: list[str] = []
    for block in result.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "\n".join(parts)


class DeepVestClient:
    """Minimal Streamable-HTTP MCP client bound to one DeepVest session."""

    _throttle_lock = threading.Lock()
    _last_call_at = 0.0

    def __init__(self, api_key: str | None = None, url: str | None = None,
                 timeout: float = 300.0, cache_dir: Path | str | None = None,
                 max_retries: int = 3):
        self.url = url or os.getenv("DEEPVEST_MCP_URL") or DEFAULT_MCP_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_dir = Path(cache_dir or os.getenv("DEEPVEST_CACHE_DIR") or DEFAULT_CACHE_DIR)
        self._auth_headers = {"X-API-Key": api_key} if api_key else None
        self._session_id: str | None = None
        self._initialized = False
        self._next_id = 0
        self.server_info: dict[str, Any] = {}

    # ------------------------------------------------------------------ wire
    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": USER_AGENT,
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        }
        headers.update(self._auth_headers or _credentials())
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id
        return headers

    def _throttle(self) -> None:
        with DeepVestClient._throttle_lock:
            wait = MIN_SECONDS_BETWEEN_CALLS - (time.monotonic() - DeepVestClient._last_call_at)
            if wait > 0:
                time.sleep(wait)
            DeepVestClient._last_call_at = time.monotonic()

    def _post(self, payload: dict[str, Any], expect_response: bool = True) -> dict[str, Any] | None:
        body = json.dumps(payload).encode("utf-8")
        attempt = 0
        while True:
            attempt += 1
            self._throttle()
            req = urllib.request.Request(self.url, data=body, headers=self._headers(), method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    status = resp.status
                    ctype = resp.headers.get("Content-Type", "")
                    sid = resp.headers.get("Mcp-Session-Id")
                    if sid:
                        self._session_id = sid
                    raw = resp.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as exc:
                status = exc.code
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                if status == 401:
                    raise DeepVestAuthError(f"DeepVest rejected the credentials (401): {detail}") from exc
                if status == 402:
                    raise DeepVestCreditsError(
                        f"DeepVest account has insufficient credits (402): {detail}. "
                        "Top up at https://console.deepvest.ai/dashboard/billing") from exc
                if status == 429 or status >= 500:
                    if attempt <= self.max_retries:
                        retry_after = exc.headers.get("Retry-After") if exc.headers else None
                        try:
                            delay = float(retry_after) if retry_after else 5.0 * attempt
                        except ValueError:
                            delay = 5.0 * attempt
                        time.sleep(min(delay, 120.0))
                        continue
                    if status == 429:
                        raise DeepVestRateLimitError(f"DeepVest rate limit persisted (429): {detail}") from exc
                raise DeepVestError(f"DeepVest HTTP {status}: {detail}") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt <= self.max_retries:
                    time.sleep(5.0 * attempt)
                    continue
                raise DeepVestError(f"DeepVest transport failure: {exc}") from exc
            break

        if not expect_response:
            return None
        if status == 202 or not raw.strip():
            # Streamable HTTP allows 202 + async delivery; this client only
            # supports synchronous replies, so fail loudly instead of returning
            # an empty "success" that call_tool would cache as a result.
            raise DeepVestError(
                f"DeepVest returned HTTP {status} with no JSON-RPC body for {payload.get('method')}; "
                "asynchronous delivery is not supported by this client")
        if "text/event-stream" in ctype:
            messages = _parse_sse(raw)
        else:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise DeepVestError(f"DeepVest returned non-JSON body: {raw[:300]}") from exc
            messages = parsed if isinstance(parsed, list) else [parsed]
        wanted = payload.get("id")
        for message in messages:
            if isinstance(message, dict) and message.get("id") == wanted and ("result" in message or "error" in message):
                if "error" in message:
                    err = message["error"]
                    raise DeepVestError(f"JSON-RPC error {err.get('code')}: {err.get('message')}")
                return message["result"]
        raise DeepVestError(f"no JSON-RPC response with id={wanted} in server reply")

    def _request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._next_id += 1
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": self._next_id, "method": method}
        if params is not None:
            payload["params"] = params
        result = self._post(payload)
        return result or {}

    def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        try:
            self._post(payload, expect_response=False)
        except DeepVestError:
            # A server that rejects the optional notification still works.
            pass

    # --------------------------------------------------------------- session
    def initialize(self) -> dict[str, Any]:
        """Open the MCP session (free: no credits are charged). Idempotent."""
        if self._initialized:
            return self.server_info
        result = self._request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "zeropaper-deepvest-utils", "version": "1.0"},
        })
        self.server_info = result
        self._initialized = True
        self._notify("notifications/initialized")
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        """Full tool catalog (name, description, inputSchema), following cursors."""
        self.initialize()
        tools: list[dict[str, Any]] = []
        cursor: str | None = None
        for _ in range(50):
            params = {"cursor": cursor} if cursor else {}
            page = self._request("tools/list", params)
            tools.extend(page.get("tools") or [])
            cursor = page.get("nextCursor")
            if not cursor:
                break
        return tools

    # ------------------------------------------------------------------ cache
    def cache_path(self, tool: str, arguments: dict[str, Any]) -> Path:
        digest = hashlib.sha256(
            json.dumps({"tool": tool, "arguments": arguments}, sort_keys=True,
                       separators=(",", ":"), default=str).encode("utf-8")
        ).hexdigest()[:16]
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", tool)
        return self.cache_dir / f"{safe}_{digest}.json"

    def call_tool(self, tool: str, arguments: dict[str, Any] | None = None, *,
                  refresh: bool = False, raise_on_tool_error: bool = True) -> dict[str, Any]:
        """Invoke one MCP tool. Returns {"tool","arguments","text","structured","is_error","raw","cached","cache_path"}."""
        arguments = dict(arguments or {})
        path = self.cache_path(tool, arguments)
        if not refresh and path.is_file():
            record = json.loads(path.read_text(encoding="utf-8"))
            raw = record["response"]
            return {
                "tool": tool, "arguments": arguments, "text": _content_text(raw),
                "structured": raw.get("structuredContent"), "is_error": bool(raw.get("isError")),
                "raw": raw, "cached": True, "cache_path": str(path),
                "fetched_at": record.get("fetched_at"),
            }
        self.initialize()
        raw = self._request("tools/call", {"name": tool, "arguments": arguments})
        is_error = bool(raw.get("isError"))
        text = _content_text(raw)
        if is_error and raise_on_tool_error:
            raise DeepVestToolError(f"{tool}: {text[:500]}")
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if not is_error:
            path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "tool": tool, "arguments": arguments, "fetched_at": fetched_at,
                "server": self.server_info.get("serverInfo"), "mcp_url": self.url,
                "response": raw,
            }
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(record, indent=1, sort_keys=True, default=str), encoding="utf-8")
            tmp.replace(path)
        return {
            "tool": tool, "arguments": arguments, "text": text,
            "structured": raw.get("structuredContent"), "is_error": is_error,
            "raw": raw, "cached": False, "cache_path": str(path) if not is_error else None,
            "fetched_at": fetched_at,
        }

    def query(self, tool: str, text: str, *, refresh: bool = False, **extra: Any) -> str:
        """Natural-language tools (asset_analysis, quick_analysis, …) take one `query` string."""
        arguments: dict[str, Any] = {"query": text}
        arguments.update(extra)
        return self.call_tool(tool, arguments, refresh=refresh)["text"]


# ---------------------------------------------------------------- module API
_DEFAULT_CLIENT: DeepVestClient | None = None


def _client() -> DeepVestClient:
    global _DEFAULT_CLIENT
    if _DEFAULT_CLIENT is None:
        _DEFAULT_CLIENT = DeepVestClient()
    return _DEFAULT_CLIENT


def list_tools() -> dict[str, dict[str, Any]]:
    """name -> {"description", "inputSchema"} for every tool the key can see."""
    return {t["name"]: {"description": t.get("description", ""), "inputSchema": t.get("inputSchema", {})}
            for t in _client().list_tools()}


def call_tool(tool: str, arguments: dict[str, Any] | None = None, *, refresh: bool = False) -> dict[str, Any]:
    return _client().call_tool(tool, arguments, refresh=refresh)


def query(tool: str, text: str, *, refresh: bool = False, **extra: Any) -> str:
    return _client().query(tool, text, refresh=refresh, **extra)


def cached_calls(cache_dir: Path | str | None = None) -> list[dict[str, Any]]:
    """Inventory of cached DeepVest responses (tool, arguments, fetched_at, path)."""
    root = Path(cache_dir or os.getenv("DEEPVEST_CACHE_DIR") or DEFAULT_CACHE_DIR)
    out = []
    for path in sorted(root.glob("*.json")) if root.is_dir() else []:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        out.append({"tool": record.get("tool"), "arguments": record.get("arguments"),
                    "fetched_at": record.get("fetched_at"), "path": str(path)})
    return out


# ------------------------------------------------------- response extraction
def parse_result(response: dict[str, Any]) -> Any:
    """Unwrap a call_tool() result into its JSON payload when the tool returned one.

    Verified live (server 3.4.7): typed tools (dividend_history, the math/
    valuation tools) and the `format="json"` analysis envelope arrive as
    `structuredContent == {"result": "<JSON string>"}` with the same JSON in
    the text block.  This returns the decoded object; for a prose answer it
    returns the text unchanged (a str).
    """
    structured = response.get("structured")
    candidates: list[Any] = []
    if isinstance(structured, dict) and set(structured) == {"result"}:
        candidates.append(structured["result"])
    elif structured is not None:
        return structured
    candidates.append(response.get("text", ""))
    for cand in candidates:
        if isinstance(cand, (dict, list)):
            return cand
        if isinstance(cand, str):
            stripped = cand.strip()
            if stripped and stripped[0] in "[{":
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
    return response.get("text", "")


def tables_from_response(response: dict[str, Any]) -> dict[str, list]:
    """section_name -> [DataFrame, ...] for every markdown table in a tool response.

    Handles both shapes seen live: the `format="json"` envelope
    ({"schema_version": "1", "prose": ..., "data": {section: "<markdown table
    text>" | [records]}}) and plain prose answers (single section "prose").
    Record-list sections become one DataFrame directly.
    """
    import pandas as pd

    payload = parse_result(response)
    out: dict[str, list] = {}
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        for name, section in payload["data"].items():
            if isinstance(section, str):
                tables = parse_markdown_tables(section)
            elif isinstance(section, list) and section and all(isinstance(r, dict) for r in section):
                tables = [pd.DataFrame(section)]
            else:
                tables = []
            if tables:
                out[name] = tables
        if not out and isinstance(payload.get("prose"), str):
            tables = parse_markdown_tables(payload["prose"])
            if tables:
                out["prose"] = tables
        return out
    text = payload if isinstance(payload, str) else response.get("text", "")
    tables = parse_markdown_tables(text)
    if tables:
        out["prose"] = tables
    return out


_TABLE_ROW = re.compile(r"^\s*\|?[^|\n]*\|.*$")  # any line with a pipe; edge pipes optional
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def parse_markdown_tables(text: str):
    """Every GitHub-style markdown table in `text` as a pandas DataFrame (numeric columns coerced).

    DeepVest's analysis tools answer in prose that usually embeds one or more
    markdown tables when asked for tabular output; this pulls them out.  Columns
    that parse as numbers (after stripping $, %, commas) are converted; a '%'
    column is left in percent units (not divided by 100).  Returns [] if none.

    Known ambiguity (inherent to GFM, not fixed): a *data* row that looks like
    a separator (`| --- | --- |`) is read as the start of a new table, so the
    rows before it split off (and a zero-row table directly followed by such a
    row loses its header).  DeepVest tables do not use dash-only cells.
    """
    import pandas as pd

    tables = []
    block: list[str] = []

    def flush():
        if len(block) >= 2 and _TABLE_SEP.match(block[1]):
            rows = [block[0]] + block[2:]
            cleaned = [r.strip().strip("|") for r in rows]
            try:
                df = pd.read_csv(StringIO("\n".join(cleaned)), sep="|", engine="python",
                                 skipinitialspace=True, dtype=str)
            except Exception:
                return
            df.columns = [str(c).strip() for c in df.columns]
            df = df.apply(
                lambda col: col.str.strip()
                if (pd.api.types.is_object_dtype(col.dtype)
                    or pd.api.types.is_string_dtype(col.dtype))
                else col
            )
            for col in df.columns:
                series = df[col]
                if not (pd.api.types.is_object_dtype(series.dtype)
                        or pd.api.types.is_string_dtype(series.dtype)):
                    continue
                stripped = series.str.replace(r"[,$%\s]", "", regex=True).str.replace(
                    r"^\((.*)\)$", r"-\1", regex=True)
                numeric = pd.to_numeric(stripped, errors="coerce")
                if numeric.notna().sum() >= max(1, int(0.8 * series.notna().sum())) and series.notna().any():
                    df[col] = numeric
            tables.append(df)

    for line in text.splitlines():
        if block and _TABLE_SEP.match(line):
            # The separator fixes the header: re-anchor to the line right
            # before it so a stray earlier pipe-bearing prose line cannot
            # displace the real header and drop the whole table.  If the
            # pending block is already a complete table (two tables with no
            # gap between them), flush it first instead of discarding it.
            header = block.pop()
            if len(block) >= 2 and _TABLE_SEP.match(block[1]):
                flush()
            block = [header, line]
        elif _TABLE_ROW.match(line):
            block.append(line)
        else:
            flush()
            block = []
    flush()
    return tables


_JSON_FENCE = re.compile(r"```(?:json)?\s*\n(.*?)```", re.S)


def parse_json_blocks(text: str) -> list[Any]:
    """Every fenced ```json block (or a bare top-level JSON document) parsed from `text`."""
    found: list[Any] = []
    for body in _JSON_FENCE.findall(text):
        try:
            found.append(json.loads(body))
        except json.JSONDecodeError:
            continue
    if not found:
        stripped = text.strip()
        if stripped and stripped[0] in "[{":
            try:
                found.append(json.loads(stripped))
            except json.JSONDecodeError:
                pass
    return found


# -------------------------------------------------------------------- CLI
def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DeepVest MCP client")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ping", help="initialize a session (auth check; no credits)")
    p_tools = sub.add_parser("tools", help="list the tools this key can call")
    p_tools.add_argument("--json", action="store_true", help="full JSON incl. inputSchema")
    p_q = sub.add_parser("query", help="call a natural-language tool")
    p_q.add_argument("tool")
    p_q.add_argument("text")
    p_q.add_argument("--refresh", action="store_true")
    p_c = sub.add_parser("call", help="call any tool with a JSON arguments object")
    p_c.add_argument("tool")
    p_c.add_argument("arguments", help="JSON object, e.g. '{\"ticker\": \"AAPL\"}'")
    p_c.add_argument("--refresh", action="store_true")
    sub.add_parser("cache", help="list cached responses under data/deepvest/")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "ping":
            info = _client().initialize()
            print(json.dumps({"server": info.get("serverInfo"), "protocolVersion": info.get("protocolVersion"),
                              "capabilities": info.get("capabilities")}, indent=1))
        elif args.cmd == "tools":
            tools = _client().list_tools()
            if args.json:
                print(json.dumps(tools, indent=1))
            else:
                for t in tools:
                    desc = (t.get("description") or "").strip().splitlines()
                    print(f"{t['name']:40s} {desc[0] if desc else ''}")
                print(f"\n{len(tools)} tools")
        elif args.cmd == "query":
            print(_client().query(args.tool, args.text, refresh=args.refresh))
        elif args.cmd == "call":
            try:
                arguments = json.loads(args.arguments)
            except json.JSONDecodeError as exc:
                raise DeepVestError(f"arguments must be a JSON object: {exc}") from exc
            if not isinstance(arguments, dict):
                raise DeepVestError("arguments must be a JSON object, e.g. '{\"ticker\": \"AAPL\"}'")
            res = _client().call_tool(args.tool, arguments, refresh=args.refresh)
            if res["structured"] is not None:
                print(json.dumps(res["structured"], indent=1))
            print(res["text"])
            print(f"\n[cached={res['cached']} path={res['cache_path']}]", file=sys.stderr)
        elif args.cmd == "cache":
            for rec in cached_calls():
                print(json.dumps(rec))
    except DeepVestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main())
