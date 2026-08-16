#!/usr/bin/env python3
"""Small stdlib-only control client for ZeroPaper's persistent OpenCode server."""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


_TASK_RESULT = re.compile(r'\A<task id="([^"\n]+)" state="(?:completed|error)">')


def _base_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        raise argparse.ArgumentTypeError("server URL must be localhost HTTP")
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path.rstrip("/"):
        raise argparse.ArgumentTypeError("server URL must contain only scheme, localhost, and port")
    if parsed.port is None:
        raise argparse.ArgumentTypeError("server URL must include a port")
    return value.rstrip("/")


class Client:
    def __init__(self, url: str, password: str, timeout: float = 5.0):
        self.url = url.rstrip("/")
        token = base64.b64encode(f"opencode:{password}".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}"}
        self.timeout = timeout

    def request(self, path: str, method: str = "GET"):
        req = urllib.request.Request(
            self.url + path,
            data=b"" if method == "POST" else None,
            headers=self.headers,
            method=method,
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            body = response.read()
        return json.loads(body) if body else None

    def sessions(self) -> list[dict]:
        data = self.request("/session")
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("invalid /session response")
        if not all(_session_id(row) and isinstance(row.get("directory"), str)
                   and row["directory"] and os.path.isabs(row["directory"]) for row in data):
            raise ValueError("invalid session row")
        return data

    def children(self, session_id: str) -> list[dict]:
        quoted = urllib.parse.quote(session_id, safe="")
        data = self.request(f"/session/{quoted}/children")
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("invalid /session/{id}/children response")
        if not all(_session_id(row) for row in data):
            raise ValueError("invalid child session row")
        return data

    def statuses(self) -> dict:
        data = self.request("/session/status")
        if not isinstance(data, dict):
            raise ValueError("invalid /session/status response")
        return data

    def messages(self, session_id: str) -> list[dict]:
        quoted = urllib.parse.quote(session_id, safe="")
        data = self.request(f"/session/{quoted}/message")
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            raise ValueError("invalid /session/{id}/message response")
        return data

    def abort(self, session_id: str) -> None:
        quoted = urllib.parse.quote(session_id, safe="")
        result = self.request(f"/session/{quoted}/abort", method="POST")
        if result is not True:
            raise ValueError("invalid /session/{id}/abort response")


def _session_id(row: dict) -> str | None:
    value = row.get("id") or row.get("sessionID")
    return value if isinstance(value, str) and value else None


def _status_type(value) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, dict):
        result = value.get("type") or value.get("status")
        if isinstance(result, str) and result:
            return result
    raise ValueError("invalid per-session status value")


def _busy_tree(client: Client, parent: str) -> list[str]:
    ids = [parent]
    ids.extend(x for row in client.children(parent) if (x := _session_id(row)))
    statuses = client.statuses()
    return [sid for sid in ids if sid in statuses and _status_type(statuses[sid]) not in {"idle", "error"}]


def _generation_token(child: str, message_index: int, part_index: int) -> str:
    return f"{message_index}.{part_index}:{urllib.parse.quote(child, safe='')}"


def _generation_child(token: str) -> str:
    prefix, separator, encoded = token.partition(":")
    if not separator or not re.fullmatch(r"[0-9]+\.[0-9]+", prefix) or not encoded:
        raise ValueError("invalid background generation token")
    child = urllib.parse.unquote(encoded)
    if not child:
        raise ValueError("invalid background generation child")
    return child


def _background_state(client: Client, parent: str, after: int = 0) -> tuple[set[str], set[str], set[str]]:
    if after < 0:
        raise ValueError("invalid background history baseline")
    launched: set[str] = set()
    notified: set[str] = set()
    notified_at: dict[str, int] = {}
    unmatched: dict[str, list[str]] = {}
    completed_assistant_at: list[int] = []
    messages = client.messages(parent)
    if after > len(messages):
        raise ValueError("background history shrank below its persisted baseline")
    for index, message in enumerate(messages):
        if index < after:
            continue
        info = message.get("info")
        parts = message.get("parts")
        if not isinstance(info, dict) or not isinstance(info.get("role"), str):
            raise ValueError("invalid parent message info")
        if not isinstance(parts, list) or not all(isinstance(x, dict) for x in parts):
            raise ValueError("invalid parent message shape")
        if info.get("role") == "assistant":
            timing = info.get("time", {})
            if not isinstance(timing, dict):
                raise ValueError("invalid assistant timing")
            completed = timing.get("completed")
            if completed is not None and (isinstance(completed, bool) or not isinstance(completed, (int, float))):
                raise ValueError("invalid assistant completion timestamp")
            error = info.get("error")
            if error is not None and not isinstance(error, dict):
                raise ValueError("invalid assistant error")
            if completed is not None or error is not None:
                completed_assistant_at.append(index)
        for part_index, part in enumerate(parts):
            if part.get("tool") == "task":
                state = part.get("state")
                if not isinstance(state, dict):
                    raise ValueError("invalid task part state")
                metadata = state.get("metadata", {})
                if not isinstance(metadata, dict):
                    raise ValueError("invalid task part metadata")
                if "background" in metadata and not isinstance(metadata["background"], bool):
                    raise ValueError("invalid background task flag")
                if metadata.get("background") is True:
                    child = metadata.get("sessionId") or metadata.get("sessionID") or metadata.get("jobId")
                    if not isinstance(child, str) or not child:
                        raise ValueError("background task is missing its child session ID")
                    token = _generation_token(child, index, part_index)
                    launched.add(token)
                    unmatched.setdefault(child, []).append(token)
            if "synthetic" in part and not isinstance(part["synthetic"], bool):
                raise ValueError("invalid synthetic text flag")
            if part.get("type") == "text" and part.get("synthetic") is True:
                if info.get("role") != "user":
                    raise ValueError("synthetic task notification must have user role")
                text = part.get("text")
                if not isinstance(text, str):
                    raise ValueError("invalid synthetic text part")
                envelope = _TASK_RESULT.match(text)
                if envelope:
                    child = envelope.group(1)
                    # A resumed task_id reuses its child session ID. Pair a
                    # notification with the newest unmatched generation,
                    # never with every historical launch of that ID.
                    candidates = unmatched.get(child, [])
                    if candidates:
                        token = candidates.pop()
                        notified.add(token)
                        notified_at[token] = index
    settled = {token for token, index in notified_at.items() if any(x > index for x in completed_assistant_at)}
    return launched, notified, settled


def _notified_children(client: Client, parent: str, after: int = 0) -> set[str]:
    return _background_state(client, parent, after)[1]


def _pending_children(client: Client, parent: str, after: int = 0) -> set[str]:
    launched, _, settled = _background_state(client, parent, after)
    return launched - settled


def _client(args) -> Client:
    return Client(args.url, args.password, args.request_timeout)


def cmd_health(args) -> int:
    data = _client(args).request("/global/health")
    if not isinstance(data, dict) or data.get("healthy") is not True:
        return 1
    print(data.get("version", "unknown"))
    return 0


def cmd_list_local(args) -> int:
    root = os.path.realpath(args.root)
    for row in _client(args).sessions():
        directory = row.get("directory")
        if isinstance(directory, str) and os.path.realpath(directory) == root:
            sid = _session_id(row)
            if sid:
                print(sid)
    return 0


def cmd_busy(args) -> int:
    busy = _busy_tree(_client(args), args.session)
    print(json.dumps(busy))
    return 0 if not busy else 3


def cmd_pending(args) -> int:
    for generation in sorted(_pending_children(_client(args), args.session, args.after)):
        print(generation)
    return 0


def cmd_cursor(args) -> int:
    print(len(_client(args).messages(args.session)))
    return 0


def cmd_has_text(args) -> int:
    for message in _client(args).messages(args.session):
        info = message.get("info")
        parts = message.get("parts")
        if not isinstance(info, dict) or not isinstance(info.get("role"), str):
            raise ValueError("invalid parent message info")
        if not isinstance(parts, list) or not all(isinstance(part, dict) for part in parts):
            raise ValueError("invalid parent message shape")
        for part in parts:
            if "text" in part and not isinstance(part["text"], str):
                raise ValueError("invalid parent text part")
            if info.get("role") == "user" and part.get("type") == "text" and args.needle in part.get("text", ""):
                return 0
    return 3


def cmd_wait_idle(args) -> int:
    client = _client(args)
    deadline = time.monotonic() + args.timeout
    stable = 0
    last_busy: list[str] = []
    required = set(args.generation)
    for generation in required:
        _generation_child(generation)
    missing = set(required)
    unsettled = set(required)
    while True:
        # An autowoken parent can itself launch another background generation.
        # Discover all task parts on every sample, including children that
        # completed between polls, and require the assistant response after
        # each synthetic notification (the causal autowake barrier).
        if getattr(args, "status_only", False):
            growth: set[str] = set()
            missing = set()
            unsettled = set()
        else:
            launched, notified, settled = _background_state(client, args.session, args.after)
            growth = launched - required
            if growth:
                required.update(growth)
                stable = 0
            missing = required - notified
            unsettled = required - settled
        last_busy = _busy_tree(client, args.session)
        if last_busy or missing or unsettled or growth:
            stable = 0
        else:
            stable += 1
            if stable >= args.stable_samples:
                return 0
        if time.monotonic() >= deadline:
            print(json.dumps({"busy": last_busy,
                              "missing_notifications": sorted(_generation_child(x) for x in missing),
                              "missing_autowake_responses": sorted(_generation_child(x) for x in unsettled)}))
            return 3
        time.sleep(args.poll)


def cmd_abort_tree(args) -> int:
    client = _client(args)
    busy = _busy_tree(client, args.session)
    failed = False
    # Children first, then the parent, but attempt every abort even if one
    # request fails. The caller verifies quiescence before it may resume.
    for sid in [x for x in busy if x != args.session] + [args.session]:
        try:
            client.abort(sid)
            print(sid)
        except (OSError, urllib.error.HTTPError, json.JSONDecodeError, ValueError) as exc:
            print(f"abort failed for {sid}: {exc}", file=sys.stderr)
            failed = True
    return 2 if failed else 0


def cmd_lock_hold(args) -> int:
    # The launcher runs its runtime body in a Bash subshell. Bash's `$$` keeps
    # the outer shell PID there (not the subshell's OS PID), so accepting a PID
    # from shell caused this helper to see a parent mismatch and release flock
    # immediately. Bind to the kernel-reported direct parent instead; reparenting
    # on launcher exit is then the release signal and cannot suffer PID reuse.
    parent = os.getppid()
    with open(args.path, "a+", encoding="utf-8") as handle:
        try:
            operation = fcntl.LOCK_EX
            if not args.wait:
                operation |= fcntl.LOCK_NB
            fcntl.flock(handle.fileno(), operation)
        except BlockingIOError:
            return 3
        handle.seek(0)
        handle.truncate()
        handle.write(f"{parent}\n")
        handle.flush()
        with open(args.ready, "w", encoding="utf-8") as ready:
            ready.write("ready\n")
        while os.getppid() == parent:
            time.sleep(0.2)
    return 0


def cmd_worktree_hash(args) -> int:
    """Hash repository changes while running inside the outer SRT boundary."""
    digest = hashlib.sha256()
    git_base = ["git", "-C", args.root]
    for command in (
        ["diff", "--binary", "--no-ext-diff", "--no-textconv"],
        ["diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv"],
    ):
        result = subprocess.run(git_base + command, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=args.timeout, check=False)
        digest.update(result.stdout)
        digest.update(str(result.returncode).encode())
    listed = subprocess.run(git_base + ["ls-files", "--others", "--exclude-standard", "-z"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=args.timeout, check=False)
    digest.update(str(listed.returncode).encode())
    for encoded in listed.stdout.split(b"\0"):
        if not encoded:
            continue
        relative = os.fsdecode(encoded)
        if os.path.isabs(relative) or ".." in relative.split(os.sep):
            continue
        path = os.path.join(args.root, relative)
        try:
            flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(path, flags)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                os.close(fd)
                continue
            with os.fdopen(fd, "rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
        except OSError:
            continue
    print(digest.hexdigest())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=_base_url)
    parser.add_argument("--password", default=os.environ.get("OPENCODE_SERVER_PASSWORD"))
    parser.add_argument("--request-timeout", type=float, default=5.0)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health").set_defaults(func=cmd_health)

    local = sub.add_parser("list-local")
    local.add_argument("--root", required=True)
    local.set_defaults(func=cmd_list_local)

    busy = sub.add_parser("busy")
    busy.add_argument("--session", required=True)
    busy.set_defaults(func=cmd_busy)

    pending = sub.add_parser("pending")
    pending.add_argument("--session", required=True)
    pending.add_argument("--after", type=int, default=0)
    pending.set_defaults(func=cmd_pending)

    cursor = sub.add_parser("cursor")
    cursor.add_argument("--session", required=True)
    cursor.set_defaults(func=cmd_cursor)

    has_text = sub.add_parser("has-text")
    has_text.add_argument("--session", required=True)
    has_text.add_argument("--needle", required=True)
    has_text.set_defaults(func=cmd_has_text)

    wait = sub.add_parser("wait-idle")
    wait.add_argument("--session", required=True)
    wait.add_argument("--timeout", type=float, required=True)
    wait.add_argument("--poll", type=float, default=0.5)
    wait.add_argument("--stable-samples", type=int, default=2)
    wait.add_argument("--after", type=int, default=0)
    wait.add_argument("--generation", action="append", default=[])
    wait.add_argument("--status-only", action="store_true")
    wait.set_defaults(func=cmd_wait_idle)

    abort = sub.add_parser("abort-tree")
    abort.add_argument("--session", required=True)
    abort.set_defaults(func=cmd_abort_tree)

    lock = sub.add_parser("lock-hold")
    lock.add_argument("--path", required=True)
    lock.add_argument("--ready", required=True)
    lock.add_argument("--wait", action="store_true")
    lock.set_defaults(func=cmd_lock_hold)

    worktree = sub.add_parser("worktree-hash")
    worktree.add_argument("--root", required=True)
    worktree.add_argument("--timeout", type=float, default=10.0)
    worktree.set_defaults(func=cmd_worktree_hash)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command not in {"lock-hold", "worktree-hash"} and (not args.url or not args.password):
        print("OpenCode server password is required", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except (OSError, urllib.error.HTTPError, json.JSONDecodeError, ValueError) as exc:
        print(f"OpenCode server request failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
