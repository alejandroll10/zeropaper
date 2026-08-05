#!/usr/bin/env python3
"""Query OpenAlex for finance/economics literature.

OpenAlex is a free, no-auth bibliographic database (~250M works). This script
exposes the subset of the API that is useful for literature scouting:

  search   — keyword search, optionally filtered by venue/year/author
  cites    — works that cite a given work (forward citations)
  refs     — works that a given work references (backward citations)
  author   — all works by an author (resolved by name → OpenAlex author ID)
  work     — full record for a single work (by DOI or OpenAlex ID)
  venues   — show the resolved venue IDs used by --venue aliases

Output formats:
  default — human-readable list (for grep / eyeballing)
  --json  — one JSON object per line (for piping to jq or another script)

Reads OPENALEX_API_KEY and EMAIL from .env at the project root. The key is what
buys a usable daily budget ($1/day vs $0.10/day keyless — see the budget note
above BACKOFF); EMAIL is sent as `mailto` for identification.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import ssl
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openalex.org"
TIMEOUT = 12
RETRIES = 10

# Use a CA bundle Python can actually find. A missing local issuer cert makes
# urllib raise CERTIFICATE_VERIFY_FAILED even when the host is up (curl, which
# uses the OS trust store, succeeds against the same URL). That is a LOCAL cert
# problem, not "OpenAlex is unreachable" — prefer certifi's bundle when present
# so the call doesn't fail and get misread as the source being down.
try:
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    _SSL_CTX = ssl.create_default_context()

# ── The daily credit budget (replaces the old per-second rate limit) ─────────
# OpenAlex switched from call-rate limits to a credit/dollar DAILY BUDGET on
# 2026-02-24 and now requires an API key for anything past demo use. Measured
# from the x-ratelimit-* response headers:
#
#   with OPENALEX_API_KEY   10,000 credits/day  ($1.00)
#   keyless (mailto only)    1,000 credits/day  ($0.10)   ← demo tier only
#
# The budget is per-key: a fresh key reported its full allowance on a host whose
# keyless bucket was already part-spent, so concurrent pipelines can each carry
# their own key instead of contending for one bucket. Keyless callers share the
# tier per-IP, which is how several pipelines on one host used to exhaust it
# collectively (issue #179).
#
# Measured per-call costs: the canonical single-entity path `/works/doi:{doi}`
# and `/works/W{id}` are FREE (0 credits); list/filter = 1; the `/works/https://
# doi.org/{doi}` alias and `?filter=doi:` = 1; search = 10; PDF/XML = 100. So
# prefer `work` over `search` whenever a DOI or OpenAlex ID is in hand — same
# answer at no cost. normalize_work_id() already funnels every accepted input
# form (bare DOI, doi.org URL, W-id, openalex.org URL) onto the free path.
#
# There is no meaningful per-second cap anymore (back-to-back searches all
# return 200), so backoff now covers only two cases: a transient 5xx, and a
# budget-exhaustion 429. Jitter still keeps concurrent callers from retrying in
# lockstep. Budget exhaustion cannot be waited out inside a retry window, so
# http_get bails immediately on it (see the long-Retry-After branch).
BACKOFF = 1.5
BACKOFF_CAP = 30.0  # don't sleep longer than this per attempt

# Credits below which we warn on stderr that the daily budget is nearly gone.
# Sized so a caller has room to finish a modest bib-verify (18 entries x 10
# credits for the search path) after seeing the warning.
BUDGET_WARN_CREDITS = 200

# Last-seen budget, refreshed from x-ratelimit-* on every response. Lets a
# caller degrade deliberately ("budget nearly gone, defer") instead of
# discovering the wall by crashing into a 429 mid-run.
LAST_BUDGET: dict[str, float | None] = {
    "remaining": None,  # credits left today
    "limit": None,      # credits/day for this identity
    "reset": None,      # seconds until refill (00:00 UTC)
    "cost": None,       # credits charged for the most recent call
}
_budget_warned = False


class OpenAlexRateLimited(RuntimeError):
    """A 429 whose Retry-After is too long to wait out (OpenAlex's daily-budget
    limiter sends seconds-until-midnight-UTC — hours). Distinct from a generic
    RuntimeError so the CLI can tell the caller *why* it bailed and that the
    right response is to fall back to WebSearch, not to retry or treat the
    openalex skill as broken. Carries retry_after for anyone who wants it."""

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after

# Aliases for top venues across the pipeline's variants. The OpenAlex source
# IDs below were resolved from the search API and verified against the journal
# page. Update as OpenAlex revises its source registry.
VENUE_ALIASES = {
    # Top-3 finance
    "jf":   "S5353659",      # The Journal of Finance
    "jfe":  "S149240962",    # Journal of Financial Economics
    "rfs":  "S170137484",    # Review of Financial Studies
    # Other top finance
    "jfqa": "S193228710",    # Journal of Financial and Quantitative Analysis
    "raps": "S2735409286",   # The Review of Asset Pricing Studies
    "rcfs": "S2736251538",   # The Review of Corporate Finance Studies
    "ms":   "S33323087",     # Management Science
    # Top-5 economics
    "aer":  "S23254222",     # American Economic Review
    "qje":  "S203860005",    # The Quarterly Journal of Economics
    "jpe":  "S95323914",     # Journal of Political Economy
    "ecma": "S95464858",     # Econometrica
    "restud": "S88935262",   # The Review of Economic Studies
    # Macro
    "jme":  "S6711363",      # Journal of Monetary Economics
    # Machine learning & NLP (llm_cognition variant). OpenAlex's coverage of ML
    # *conference* proceedings is partial and fragmented: the neurips/icml/iclr
    # sources index only a fraction of each conference's papers, ACL and EMNLP
    # are split into per-year proceedings sources (no stable alias possible),
    # and TMLR's source exists but is nearly empty (deliberately not aliased —
    # an alias that always returns nothing reads as "no such literature").
    # Treat a conference-alias miss as "not indexed here," never "no such
    # paper" — cross-check arXiv/OpenReview via WebSearch. The journal aliases
    # (jmlr, tacl, cl, cogsci, nmi) have solid coverage.
    "neurips": "S4306420609",  # Neural Information Processing Systems (partial coverage)
    "icml": "S4306419644",     # International Conference on Machine Learning (partial coverage)
    "iclr": "S4306419637",     # International Conference on Learning Representations (partial coverage)
    "jmlr": "S118988714",      # Journal of Machine Learning Research
    "tacl": "S2729999759",     # Transactions of the Association for Computational Linguistics
    "cl":   "S155526855",      # Computational Linguistics
    "cogsci": "S78735424",     # Cognitive Science (journal)
    "nmi":  "S2912241403",     # Nature Machine Intelligence
}

# Default field set we extract from works. Keep small to limit response payload.
# `abstract_inverted_index` is added on demand by `work_fields(abstracts=True)` —
# abstracts can be ~250 words × N results, so we don't pay that bandwidth unless
# the caller asks.
WORK_FIELDS = (
    "id,doi,title,display_name,publication_year,publication_date,"
    "primary_location,authorships,cited_by_count,referenced_works,"
    "topics,open_access,language,type"
)


def work_fields(abstracts: bool) -> str:
    return WORK_FIELDS + (",abstract_inverted_index" if abstracts else "")


# ── env / http helpers ────────────────────────────────────────────────────────

def _load_env(name: str) -> str:
    """Read `name` from the environment, else from the nearest .env walking up.

    Stops at the first .env found (a project root shadows anything above it),
    matching the original EMAIL-only loader's behavior.
    """
    val = (os.environ.get(name) or "").strip().strip('"').strip("'")
    if val:
        return val
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        env = parent / ".env"
        if env.is_file():
            for line in env.read_text().splitlines():
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    return ""


def load_env_email() -> str:
    return _load_env("EMAIL")


_api_key_cache: str | None = None


def load_env_api_key() -> str:
    """OPENALEX_API_KEY, cached (http_get reads it on every call)."""
    global _api_key_cache
    if _api_key_cache is None:
        _api_key_cache = _load_env("OPENALEX_API_KEY")
    return _api_key_cache


def _record_budget(headers) -> None:
    """Capture the credit budget off x-ratelimit-* and warn when it runs low."""
    global _budget_warned
    if headers is None:
        return

    def _num(name: str) -> float | None:
        raw = headers.get(name)
        if raw is None:
            return None
        try:
            return float(str(raw).strip())
        except ValueError:
            return None

    remaining = _num("x-ratelimit-remaining")
    LAST_BUDGET.update({
        "remaining": remaining,
        "limit": _num("x-ratelimit-limit"),
        "reset": _num("x-ratelimit-reset"),
        "cost": _num("x-ratelimit-credits-used"),
    })
    if remaining is not None and remaining < BUDGET_WARN_CREDITS and not _budget_warned:
        _budget_warned = True
        reset = LAST_BUDGET["reset"]
        when = f", refills in {reset / 3600:.1f}h" if reset else ""
        hint = "" if load_env_api_key() else (
            " — no OPENALEX_API_KEY set, so this is the $0.10/day keyless demo "
            "tier shared across this whole host; a free key gives 10x"
        )
        print(
            f"WARN: OpenAlex daily budget nearly exhausted "
            f"({remaining:.0f} credits left{when}){hint}",
            file=sys.stderr,
        )


def _retry_after_seconds(exc: urllib.error.HTTPError) -> float | None:
    """Parse a Retry-After header (delta-seconds form) off a 429/503, if present."""
    raw = exc.headers.get("Retry-After") if exc.headers else None
    if not raw:
        return None
    try:
        secs = float(raw.strip())
    except ValueError:
        return None  # HTTP-date form — fall back to our own backoff
    return secs if secs >= 0 else None  # never feed a negative to time.sleep()


def _backoff_sleep(attempt: int, retry_after: float | None) -> None:
    """Sleep before the next attempt: honor Retry-After, else exponential + jitter.

    Jitter (full-jitter: random in [0, window]) is what keeps several pipelines
    sharing one IP from retrying in lockstep and re-tripping the rate limit
    together.

    Every sleep is capped at BACKOFF_CAP. A server-sent Retry-After can be huge
    — OpenAlex's daily-budget 429 sends seconds-until-midnight-UTC (hours) — and
    blocking a whole agent on that is pointless; http_get bails on a long
    Retry-After before ever reaching here with one.
    """
    window = min(BACKOFF * (2 ** attempt), BACKOFF_CAP)
    delay = retry_after if retry_after is not None else random.uniform(0, window)
    time.sleep(min(delay, BACKOFF_CAP))


def http_get(path: str, params: dict, mailto: str) -> dict:
    if mailto:
        params = {**params, "mailto": mailto}
    url = f"{API}{path}?{urllib.parse.urlencode(params, safe=',:|')}"
    # Key goes in the Authorization header, not the query string: OpenAlex
    # accepts either, but a header keeps the secret out of the exception
    # messages below (which embed `url`), out of logs, and out of referrers.
    headers = {}
    api_key = load_env_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    last_err: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=_SSL_CTX) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                _record_budget(resp.headers)
                return payload
        except urllib.error.HTTPError as exc:
            last_err = exc
            _record_budget(exc.headers)
            # 429 = rate-limited, 5xx = transient server error → worth retrying.
            # 4xx other than 429 (e.g. 400/404) are deterministic; don't retry.
            if exc.code != 429 and exc.code < 500:
                break
            retry_after = _retry_after_seconds(exc)
            # Fail FAST on a long Retry-After. OpenAlex's daily-budget 429 sends
            # Retry-After = seconds-until-midnight-UTC (can be hours); the budget
            # will not clear within our retry window, so blocking on it is
            # pointless — bail immediately with an actionable message so the
            # caller falls back to WebSearch instead of retrying or giving up.
            # Scoped to 429: a 5xx with a long Retry-After is a transient outage,
            # not budget exhaustion, so it takes the normal capped-backoff path
            # below (BACKOFF_CAP already bounds each sleep to 30s — no hang).
            if exc.code == 429 and retry_after is not None and retry_after > BACKOFF_CAP:
                tier = (
                    "$1/day keyed budget"
                    if load_env_api_key()
                    else "$0.10/day KEYLESS demo budget (shared across this whole "
                         "host IP) — set OPENALEX_API_KEY in .env for 10x more"
                )
                raise OpenAlexRateLimited(
                    f"OpenAlex rate-limited (HTTP 429), Retry-After={retry_after:.0f}s "
                    f"(~{retry_after / 3600:.1f}h) — daily credit budget exhausted on the "
                    f"{tier}; resets 00:00 UTC. Not waiting; fall back to WebSearch.",
                    retry_after=retry_after,
                ) from exc
            if attempt < RETRIES:
                _backoff_sleep(attempt, retry_after)
        except Exception as exc:
            last_err = exc
            if attempt < RETRIES:
                _backoff_sleep(attempt, None)
    raise RuntimeError(f"OpenAlex GET {url} failed: {last_err}")


# ── filter / venue helpers ────────────────────────────────────────────────────

def resolve_venues(spec: str | None) -> list[str]:
    """Resolve a comma-separated venue spec into OpenAlex source IDs.

    Each token is either an alias from VENUE_ALIASES, an explicit S<id>, or a
    literal name (resolved via the sources endpoint, slower).
    """
    if not spec:
        return []
    out: list[str] = []
    mailto = load_env_email()
    for tok in [t.strip() for t in spec.split(",") if t.strip()]:
        low = tok.lower()
        if low in VENUE_ALIASES:
            out.append(VENUE_ALIASES[low])
        elif tok.startswith("S") and tok[1:].isdigit():
            out.append(tok)
        else:
            payload = http_get("/sources", {"search": tok, "per-page": "1"}, mailto)
            results = payload.get("results") or []
            if not results:
                print(f"WARN: venue '{tok}' not found, skipping", file=sys.stderr)
                continue
            out.append(results[0]["id"].rsplit("/", 1)[-1])
    return out


def build_filter(venues: list[str], years: str | None, work_type: str | None) -> str:
    parts: list[str] = []
    if venues:
        parts.append("primary_location.source.id:" + "|".join(venues))
    if years:
        if "-" in years:
            lo, hi = years.split("-", 1)
            parts.append(f"publication_year:{lo}-{hi}")
        else:
            parts.append(f"publication_year:{years}")
    if work_type:
        parts.append(f"type:{work_type}")
    return ",".join(parts)


# ── projection ────────────────────────────────────────────────────────────────

def reconstruct_abstract(inverted: dict | None) -> str | None:
    """Rebuild a plain-text abstract from OpenAlex's `abstract_inverted_index`.

    OpenAlex ships abstracts as `{word: [position, ...]}` to dodge licensing
    around full-text reproduction. We invert that back into a normal string by
    sorting tokens by position and joining with single spaces. Returns None if
    the field is missing (paywalled venue, dataset record without an abstract,
    etc.).
    """
    if not inverted:
        return None
    tokens: list[tuple[int, str]] = []
    for word, positions in inverted.items():
        for pos in positions or []:
            tokens.append((pos, word))
    if not tokens:
        return None
    tokens.sort(key=lambda t: t[0])
    return " ".join(w for _, w in tokens)


def project(work: dict) -> dict:
    primary = work.get("primary_location") or {}
    src = primary.get("source") or {}
    authors = []
    author_details = []
    for au in (work.get("authorships") or [])[:8]:
        a = au.get("author") or {}
        nm = a.get("display_name")
        if not nm:
            continue
        authors.append(nm)
        orcid = a.get("orcid")
        author_details.append({
            "name": nm,
            "orcid": orcid.rsplit("/", 1)[-1] if orcid else None,
            "institutions": [
                (inst or {}).get("display_name")
                for inst in (au.get("institutions") or [])
                if (inst or {}).get("display_name")
            ],
        })
    # OpenAlex topics: a ready substitute subject classification where a venue
    # prints no JEL codes (e.g. The Journal of Finance). We do NOT emit the
    # legacy `concepts` field — OpenAlex has deprecated it, and it keyword-matches
    # titles so noisily that even a score>=0.3 filter leaves junk (e.g. "Forestry"
    # for a cross-sections-of-returns paper). `topics` is the clean replacement
    # and is what the only consumer (the IAR distiller) reads.
    topics = [
        t.get("display_name")
        for t in (work.get("topics") or [])[:4]
        if t.get("display_name")
    ]
    doi = work.get("doi") or ""
    row = {
        "openalex_id": work.get("id"),
        "doi": doi.replace("https://doi.org/", "") or None,
        "title": work.get("title") or work.get("display_name"),
        "year": work.get("publication_year"),
        "date": work.get("publication_date"),
        "authors": authors,
        "venue": src.get("display_name"),
        "venue_id": src.get("id"),
        "url": primary.get("landing_page_url") or work.get("doi") or work.get("id"),
        "cited_by_count": work.get("cited_by_count"),
        "type": work.get("type"),
        "open_access_pdf": (work.get("open_access") or {}).get("oa_url"),
        "n_references": len(work.get("referenced_works") or []),
        "author_details": author_details,
        "topics": topics,
    }
    if "abstract_inverted_index" in work:
        row["abstract"] = reconstruct_abstract(work.get("abstract_inverted_index"))
    return row


# ── output ────────────────────────────────────────────────────────────────────

def render_human(rows: list[dict], header: str = "") -> str:
    out = []
    if header:
        out.append(header)
        out.append("")
    if not rows:
        out.append("(no results)")
        return "\n".join(out)
    for i, r in enumerate(rows, 1):
        au = ", ".join(r["authors"][:3])
        if len(r["authors"]) > 3:
            au += f", +{len(r['authors']) - 3}"
        cite = f"cited={r['cited_by_count']}" if r.get("cited_by_count") is not None else ""
        out.append(f"[{i}] {cite} ({r.get('year','?')}) {au}")
        out.append(f"    \"{r['title']}\"")
        venue = r.get("venue") or ""
        doi = r.get("doi") or ""
        loc = " · ".join([s for s in (venue, doi) if s])
        if loc:
            out.append(f"    {loc}")
        out.append(f"    id: {r['openalex_id']}")
        abstract = r.get("abstract")
        if abstract:
            wrapped = textwrap.fill(abstract, width=96, initial_indent="    ", subsequent_indent="    ")
            out.append(wrapped)
            out.append("")
        elif "abstract" in r:  # asked for, not provided by OpenAlex
            out.append("    (no abstract available)")
            out.append("")
    return "\n".join(out)


def emit(rows: list[dict], as_json: bool, header: str = "") -> None:
    if as_json:
        for r in rows:
            sys.stdout.write(json.dumps(r, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(render_human(rows, header) + "\n")


# ── commands ──────────────────────────────────────────────────────────────────

def normalize_work_id(s: str) -> str:
    s = s.strip()
    if s.startswith("https://openalex.org/"):
        return s.rsplit("/", 1)[-1]
    if s.startswith("doi:"):
        return s
    if s.startswith("10."):
        return f"doi:{s}"
    if s.startswith("https://doi.org/"):
        return f"doi:{s.split('https://doi.org/', 1)[1]}"
    return s


def cmd_search(args, mailto: str) -> int:
    venues = resolve_venues(args.venue)
    flt = build_filter(venues, args.years, args.type)
    sort = "cited_by_count:desc" if args.sort == "cited" else "relevance_score:desc"
    params = {
        "search": args.query,
        "per-page": str(args.top),
        "sort": sort,
        "select": work_fields(args.abstracts),
    }
    if flt:
        params["filter"] = flt
    payload = http_get("/works", params, mailto)
    rows = [project(w) for w in (payload.get("results") or [])]
    meta = payload.get("meta") or {}
    header = f"# OpenAlex search: \"{args.query}\"  (filter={flt or 'none'}, sort={sort}, total={meta.get('count','?')})"
    emit(rows, args.json, header)
    return 0


def cmd_cites(args, mailto: str) -> int:
    wid = normalize_work_id(args.work_id)
    target = http_get(f"/works/{wid}", {"select": "id,title"}, mailto)
    target_oid = target["id"].rsplit("/", 1)[-1]
    venues = resolve_venues(args.venue)
    flt_parts = [f"cites:{target_oid}"]
    extra = build_filter(venues, args.years, args.type)
    if extra:
        flt_parts.append(extra)
    params = {
        "filter": ",".join(flt_parts),
        "per-page": str(args.top),
        "sort": "cited_by_count:desc",
        "select": work_fields(args.abstracts),
    }
    payload = http_get("/works", params, mailto)
    rows = [project(w) for w in (payload.get("results") or [])]
    header = f"# Forward citations of {target_oid} (\"{target.get('title','')}\")  total={payload.get('meta',{}).get('count','?')}"
    emit(rows, args.json, header)
    return 0


def cmd_refs(args, mailto: str) -> int:
    wid = normalize_work_id(args.work_id)
    target = http_get(f"/works/{wid}", {"select": "id,title,referenced_works"}, mailto)
    refs = target.get("referenced_works") or []
    if not refs:
        emit([], args.json, f"# No references for {wid}")
        return 0
    refs = refs[: args.top] if args.top else refs
    ids = "|".join(r.rsplit("/", 1)[-1] for r in refs)
    payload = http_get(
        "/works",
        {"filter": f"openalex_id:{ids}", "per-page": str(min(len(refs), 200)), "select": work_fields(args.abstracts)},
        mailto,
    )
    rows = [project(w) for w in (payload.get("results") or [])]
    header = f"# Backward references of {target['id'].rsplit('/',1)[-1]} (\"{target.get('title','')}\")  shown={len(rows)}/{len(refs)}"
    emit(rows, args.json, header)
    return 0


def cmd_author(args, mailto: str) -> int:
    payload = http_get("/authors", {"search": args.name, "per-page": "1"}, mailto)
    candidates = payload.get("results") or []
    if not candidates:
        print(f"ERROR: no author named '{args.name}'", file=sys.stderr)
        return 4
    author = candidates[0]
    aid = author["id"].rsplit("/", 1)[-1]
    venues = resolve_venues(args.venue)
    flt_parts = [f"author.id:{aid}"]
    extra = build_filter(venues, args.years, args.type)
    if extra:
        flt_parts.append(extra)
    params = {
        "filter": ",".join(flt_parts),
        "per-page": str(args.top),
        "sort": "cited_by_count:desc",
        "select": work_fields(args.abstracts),
    }
    works_payload = http_get("/works", params, mailto)
    rows = [project(w) for w in (works_payload.get("results") or [])]
    header = (f"# Works by {author.get('display_name','?')} ({aid}) "
              f"works_count={author.get('works_count','?')}, cited_by={author.get('cited_by_count','?')}")
    emit(rows, args.json, header)
    return 0


def cmd_work(args, mailto: str) -> int:
    wid = normalize_work_id(args.work_id)
    payload = http_get(f"/works/{wid}", {"select": work_fields(args.abstracts)}, mailto)
    rows = [project(payload)]
    emit(rows, args.json, "")
    return 0


def cmd_venues(args, mailto: str) -> int:
    width = max(len(k) for k in VENUE_ALIASES)
    print("Configured venue aliases:")
    print()
    for alias, sid in VENUE_ALIASES.items():
        info = http_get(f"/sources/{sid}", {"select": "id,display_name,issn_l,country_code,works_count"}, mailto)
        print(f"  {alias.ljust(width)}  {sid}  {info.get('display_name','?')}  ({info.get('works_count','?')} works)")
    return 0


# ── cli ───────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    common_filter = lambda x: (
        x.add_argument("--venue", help="Comma-separated venue aliases or S-ids (e.g. jf,jfe,rfs)"),
        x.add_argument("--years", help="Year range YYYY or YYYY-YYYY"),
        x.add_argument("--type", help="Work type (article, book-chapter, dataset, ...)"),
        x.add_argument("--top", type=int, default=20, help="Max results (default 20, max 200)"),
        x.add_argument("--json", action="store_true", help="Emit one JSON object per result"),
        x.add_argument("--abstracts", action="store_true", help="Include reconstructed abstracts in output"),
    )

    s = sp.add_parser("search", help="Keyword search over works")
    s.add_argument("query", help="Search query (free text)")
    s.add_argument("--sort", choices=["relevance", "cited"], default="relevance")
    common_filter(s)
    s.set_defaults(func=cmd_search)

    s = sp.add_parser("cites", help="Forward citations of a work")
    s.add_argument("work_id", help="OpenAlex W-id, full URL, or doi:10.xxx/...")
    common_filter(s)
    s.set_defaults(func=cmd_cites)

    s = sp.add_parser("refs", help="Backward references of a work")
    s.add_argument("work_id", help="OpenAlex W-id, full URL, or doi:10.xxx/...")
    s.add_argument("--top", type=int, default=50, help="Max references to fetch (default 50)")
    s.add_argument("--json", action="store_true")
    s.add_argument("--abstracts", action="store_true", help="Include reconstructed abstracts in output")
    s.set_defaults(func=cmd_refs)

    s = sp.add_parser("author", help="Works by an author (top by citations)")
    s.add_argument("name", help="Author name (free text)")
    common_filter(s)
    s.set_defaults(func=cmd_author)

    s = sp.add_parser("work", help="Full record for one work")
    s.add_argument("work_id", help="OpenAlex W-id, full URL, or doi:10.xxx/...")
    s.add_argument("--json", action="store_true")
    s.add_argument("--abstracts", action="store_true", help="Include reconstructed abstract in output")
    s.set_defaults(func=cmd_work)

    s = sp.add_parser("venues", help="Show resolved venue alias table")
    s.set_defaults(func=cmd_venues)

    args = p.parse_args()
    mailto = load_env_email()
    try:
        return args.func(args, mailto)
    except OpenAlexRateLimited as exc:
        # Distinct prefix + exit code so a caller can branch: fall back to
        # WebSearch immediately rather than treating this as a hard failure.
        print(f"RATE-LIMITED: {exc}", file=sys.stderr)
        return 7
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
