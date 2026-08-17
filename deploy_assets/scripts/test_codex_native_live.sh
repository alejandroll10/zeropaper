#!/usr/bin/env bash
# Opt-in, credentialed integration test for Codex native custom roles.
# Normal CI executes this script in skip mode. A maintainer with a logged-in
# Codex CLI can run:
#   ZEROPAPER_RUN_CODEX_NATIVE_CANARY=1 bash deploy_assets/scripts/test_codex_native_live.sh
set -euo pipefail

if [ "${ZEROPAPER_RUN_CODEX_NATIVE_CANARY:-0}" != "1" ]; then
    echo "SKIP: set ZEROPAPER_RUN_CODEX_NATIVE_CANARY=1 to run the live Codex native-role canary"
    exit 0
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
command -v codex >/dev/null 2>&1 || {
    echo "FAIL: codex is not installed" >&2
    exit 1
}

CANARY_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-codex-native.XXXXXX")"
PROJECT="$CANARY_ROOT/project"
START_MARKER="$CANARY_ROOT/codex-started"
CODEX_STDOUT="$CANARY_ROOT/codex.jsonl"
TIMEOUT_MARKER="$CANARY_ROOT/timed-out"
CODEX_PID=""
WATCHDOG_PID=""
WATCHDOG_FD_OPEN=0
cleanup() {
    trap - EXIT
    if [ "$WATCHDOG_FD_OPEN" = "1" ]; then
        # EOF delegates cleanup to the isolated watcher. Before G it owns the
        # unreaped direct-child transition; after G it freezes, binds, and
        # removes the complete discovered descendant tree, including Codex
        # shell-tool groups that called setsid().
        exec 6>&-
        WATCHDOG_FD_OPEN=0
    fi
    if [ -n "$WATCHDOG_PID" ]; then
        # The watcher must finish descendant teardown before this harness may
        # reap the leader or delete the private canary tree.
        wait "$WATCHDOG_PID" 2>/dev/null || true
        WATCHDOG_PID=""
        if [ -n "$CODEX_PID" ]; then
            wait "$CODEX_PID" 2>/dev/null || true
            CODEX_PID=""
        fi
    fi
    if [ -n "$CODEX_PID" ]; then
        # Pre-arm failures leave a stopped wrapper in this shell's group; do
        # not signal the broad group. Post-arm failures are normally handled
        # above, but this identity-safe fallback covers a watcher startup error.
        cpg="$(/bin/ps -o pgid= -p "$CODEX_PID" 2>/dev/null | tr -d ' ')"
        if [ "$cpg" = "$CODEX_PID" ]; then
            kill -KILL -- "-$CODEX_PID" 2>/dev/null || true
            kill -CONT -- "-$CODEX_PID" 2>/dev/null || true
        else
            kill -KILL "$CODEX_PID" 2>/dev/null || true
            kill -CONT "$CODEX_PID" 2>/dev/null || true
        fi
        wait "$CODEX_PID" 2>/dev/null || true
    fi
    CODEX_PID=""
    rm -rf -- "$CANARY_ROOT"
}
trap cleanup EXIT

"$ROOT/setup.sh" "$PROJECT" --variant finance --assemble-only --no-model-probe >/dev/null
git -C "$PROJECT" init -q
git -C "$PROJECT" config user.name "ZeroPaper Codex canary"
git -C "$PROJECT" config user.email "codex-canary@example.invalid"
git -C "$PROJECT" add -A
git -C "$PROJECT" commit -qm "test: native role canary baseline"

# Use the deployed permission-profile helper so this probes the production
# sandbox/trust route rather than a more permissive test-only launch.
# shellcheck source=/dev/null
source "$PROJECT/code/utils/codex_preflight.sh"
codex_permission_profile_preflight
codex_permission_profile_args "$PROJECT" true
TRUSTED_ROOT="$(codex_toml_basic_string "$PROJECT")"

ONLY_PARENT_SENTINEL="ONLY_PARENT_CONTEXT_MUST_NOT_REACH_CHILD_20260817"
CANARY_PROMPT="Use the native spawn_agent tool exactly once with agent_type=\"scorer\", task_name=\"native_scorer_live_canary\", and fork_turns=\"none\". Do not send this parent-only sentinel to the child: $ONLY_PARENT_SENTINEL. Give the child a self-contained task to write exactly NATIVE_SCORER_ROLE_OK followed by one newline to process_log/native_role_canary.txt and then reply CHILD_DONE. Keep this parent turn alive and call wait_agent exactly once with timeout_ms=3600000. After its non-timeout result and the bound terminal notification, you must call exec exactly once with the command od -An -tx1 -v process_log/native_role_canary.txt, inspect its result, and return exactly PARENT_WAITED_OK only if the bytes are 4e 41 54 49 56 45 5f 53 43 4f 52 45 52 5f 52 4f 4c 45 5f 4f 4b 0a. Do not write or repair the artifact yourself and do not use another role."

CANARY_TIMEOUT="${ZEROPAPER_CODEX_NATIVE_CANARY_TIMEOUT:-600}"
case "$CANARY_TIMEOUT" in
    ''|*[!0-9]*|0) echo "FAIL: ZEROPAPER_CODEX_NATIVE_CANARY_TIMEOUT must be a positive integer" >&2; exit 2 ;;
esac
touch "$START_MARKER"
(
    cd "$PROJECT"
    exec /usr/bin/python3 -I -c 'import os,sys
import signal
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_DFL)
# Stop before escaping the harness group. The parent arms an isolated watcher
# before allowing this wrapper to establish its nested group.
os.kill(os.getpid(), signal.SIGSTOP)
os.setpgid(0, 0)
anchor = os.fork()
if anchor == 0:
    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
        signal.signal(signum, signal.SIG_IGN)
    while True:
        signal.pause()
# Publish the anchor-backed group while still stopped; no Codex code executes
# until the parent verifies the boundary and continues the complete group.
os.kill(os.getpid(), signal.SIGSTOP)
os.execvp(sys.argv[1], sys.argv[1:])' codex exec \
        --ignore-user-config \
        --json \
        --skip-git-repo-check \
        -c 'approval_policy="never"' \
        "${CODEX_PERMISSION_PROFILE_ARGS[@]}" \
        -c "projects={${TRUSTED_ROOT}={trust_level=\"trusted\"}}" \
        -c 'features.multi_agent_v2=true' \
        -c 'model="gpt-5.6-sol"' \
        -- "$CANARY_PROMPT"
) >"$CODEX_STDOUT" &
CODEX_PID=$!
# Phase 1 must stop before the wrapper has created a new process group.
attempt=0; cpg=""; cstate=""
while [ "$attempt" -lt 200 ]; do
    attempt=$((attempt + 1))
    cpg="$(/bin/ps -o pgid= -p "$CODEX_PID" 2>/dev/null | tr -d ' ')"
    cstate="$(/bin/ps -o stat= -p "$CODEX_PID" 2>/dev/null | tr -d ' ')"
    case "$cstate" in *T*) break ;; esac
    kill -0 "$CODEX_PID" 2>/dev/null || break
    sleep 0.01
done
case "$cstate" in *T*) ;; *) echo "FAIL: canary wrapper did not reach its pre-group stop" >&2; exit 1 ;; esac
[ "$cpg" != "$CODEX_PID" ] || { echo "FAIL: canary escaped before its watcher was armed" >&2; exit 1; }

# The liveness pipe's only writer is this harness. The watcher escapes the
# harness group before readiness is acknowledged, then treats EOF—including
# abrupt harness death—as a mandatory KILL-and-wait cleanup request.
exec 6> >(/usr/bin/python3 -I -c '
import errno, os, select, signal, subprocess, sys, time
pid, timeout, marker = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
os.setpgid(0, 0)
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_IGN)

def fail_closed(message):
    print(f"FAIL: live canary cannot safely clean its Codex tree: {message}",
          file=sys.stderr, flush=True)
    while True:
        select.select([], [], [], 3600)

def process_table():
    try:
        result = subprocess.run(
            ["/bin/ps", "-axo", "pid=,ppid=,pgid=,stat="],
            check=True, capture_output=True, text=True, timeout=5,
        )
    except Exception as exc:
        fail_closed(str(exc))
    rows = {}
    for line in result.stdout.splitlines():
        fields = line.split(None, 3)
        if len(fields) != 4:
            continue
        try:
            proc_pid, ppid, pgid = map(int, fields[:3])
        except ValueError:
            continue
        rows[proc_pid] = (ppid, pgid, fields[3])
    return rows

def turn_members(rows):
    candidates = {proc_pid for proc_pid, (_, pgid, _) in rows.items()
                  if proc_pid == pid or pgid == pid}
    owned_groups = {pid}
    while True:
        descendants = candidates | {
            proc_pid for proc_pid, (ppid, _, _) in rows.items()
            if ppid in candidates
        }
        groups = owned_groups | {
            pgid for proc_pid, (_, pgid, _) in rows.items()
            if proc_pid in descendants and pgid in descendants
        }
        expanded = descendants | {
            proc_pid for proc_pid, (_, pgid, _) in rows.items()
            if pgid in groups
        }
        if expanded == candidates and groups == owned_groups:
            return {
                proc_pid for proc_pid in candidates
                if proc_pid in rows and rows[proc_pid][1] in owned_groups
            }
        candidates, owned_groups = expanded, groups

def freeze_turn_tree():
    try:
        os.killpg(pid, signal.SIGSTOP)
    except ProcessLookupError:
        return {}, set()
    previous = None
    while True:
        rows = process_table()
        members = turn_members(rows)
        live = {proc_pid for proc_pid in members
                if proc_pid in rows and not rows[proc_pid][2].startswith("Z")}
        groups = {rows[proc_pid][1] for proc_pid in live}
        if any(group <= 1 or group == os.getpgrp() for group in groups):
            fail_closed(f"unsafe descendant groups: {sorted(groups)}")
        for group in groups:
            try:
                os.killpg(group, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        for proc_pid in live:
            try:
                os.kill(proc_pid, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        select.select([], [], [], 0.02)
        check_rows = process_table()
        signature = frozenset(
            (proc_pid, check_rows[proc_pid][0], check_rows[proc_pid][1])
            for proc_pid in turn_members(check_rows)
            if proc_pid in check_rows and
               not check_rows[proc_pid][2].startswith("Z")
        )
        if signature == previous:
            return check_rows, {item[0] for item in signature}
        previous = signature

def bind_identities(rows, members):
    bindings = []
    kqueue = None
    for proc_pid in members:
        if proc_pid not in rows or rows[proc_pid][2].startswith("Z"):
            continue
        if hasattr(os, "pidfd_open"):
            try:
                bindings.append(("pidfd", os.pidfd_open(proc_pid), proc_pid))
            except ProcessLookupError:
                continue
            except OSError:
                pass
            else:
                continue
        if sys.platform.startswith("linux"):
            try:
                proc_fd = os.open(f"/proc/{proc_pid}", os.O_RDONLY |
                                  os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
            except ProcessLookupError:
                continue
            except OSError as exc:
                fail_closed(f"cannot bind descendant {proc_pid}: {exc}")
            else:
                bindings.append(("procfd", proc_fd, proc_pid))
        elif hasattr(select, "kqueue"):
            if kqueue is None:
                kqueue = select.kqueue()
            try:
                event = select.kevent(proc_pid, filter=select.KQ_FILTER_PROC,
                                      flags=select.KQ_EV_ADD,
                                      fflags=select.KQ_NOTE_EXIT)
                kqueue.control([event], 0, 0)
            except ProcessLookupError:
                continue
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    continue
                fail_closed(f"cannot bind descendant {proc_pid}: {exc}")
            else:
                bindings.append(("kqueue", kqueue, proc_pid))
        else:
            fail_closed("no kernel-bound process identity API")
    return bindings

def wait_identities(bindings):
    pending = list(bindings)
    while pending:
        next_pending = []
        kqueue_seen = {}
        for kind, handle, proc_pid in pending:
            if kind == "pidfd":
                if not select.select([handle], [], [], 0)[0]:
                    next_pending.append((kind, handle, proc_pid))
            elif kind == "procfd":
                try:
                    stat_fd = os.open("stat", os.O_RDONLY, dir_fd=handle)
                except OSError:
                    pass
                else:
                    os.close(stat_fd)
                    next_pending.append((kind, handle, proc_pid))
            else:
                exited = kqueue_seen.get(handle)
                if exited is None:
                    exited = {event.ident for event in
                              handle.control(None, 1024, 0)}
                    kqueue_seen[handle] = exited
                if proc_pid not in exited:
                    next_pending.append((kind, handle, proc_pid))
        pending = next_pending
        if pending:
            select.select([], [], [], 0.02)
    for kind, handle, _ in bindings:
        if kind in {"pidfd", "procfd"}:
            os.close(handle)

def terminate_turn_tree():
    rows, members = freeze_turn_tree()
    if not members:
        return
    bindings = bind_identities(rows, members)
    bound_pids = {proc_pid for _, _, proc_pid in bindings}
    groups = {pid}
    groups.update(rows[proc_pid][1] for proc_pid in bound_pids
                  if proc_pid in rows and
                  not rows[proc_pid][2].startswith("Z"))
    for group in groups:
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    wait_identities(bindings)

def wait_group_gone():
    while True:
        try:
            os.killpg(pid, 0)
        except ProcessLookupError:
            return
        except PermissionError:
            pass
        select.select([], [], [], 0.02)

def kill_group(signum):
    try:
        os.killpg(pid, signum)
    except ProcessLookupError:
        pass

def cleanup_parent_eof(group_armed):
    if not group_armed:
        # Before the G handshake, the unreaped direct wrapper PID is the stable
        # identity. Kill it first so it cannot cross setpgid, then cover the
        # possibility that the transition already completed.
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        kill_group(signal.SIGKILL)
        wait_group_gone()
        return
    terminate_turn_tree()

# The parent writes G only after it has verified the anchor-backed PGID. EOF
# before G uses the direct child identity; EOF after G must never signal the
# now-reapable/reusable bare PID.
armed = False
deadline = time.monotonic() + timeout
while True:
    remaining = max(0.0, deadline - time.monotonic())
    ready, _, _ = select.select([0], [], [], remaining)
    if not ready:
        break
    data = os.read(0, 1)
    if not data:
        cleanup_parent_eof(armed)
        raise SystemExit(0)
    if data == b"G":
        armed = True

try:
    with open(marker, "x", encoding="utf-8"):
        pass
except OSError:
    pass
if not armed:
    cleanup_parent_eof(False)
    raise SystemExit(0)
terminate_turn_tree()
' "$CODEX_PID" "$CANARY_TIMEOUT" "$TIMEOUT_MARKER")
WATCHDOG_PID=$!
WATCHDOG_FD_OPEN=1

# Prove the watcher has escaped before the wrapper does. This closes the
# start-to-arm window under harness cancellation.
attempt=0; wpg=""
while [ "$attempt" -lt 200 ]; do
    attempt=$((attempt + 1))
    wpg="$(/bin/ps -o pgid= -p "$WATCHDOG_PID" 2>/dev/null | tr -d ' ')"
    [ "$wpg" = "$WATCHDOG_PID" ] && break
    kill -0 "$WATCHDOG_PID" 2>/dev/null || break
    sleep 0.01
done
[ "$wpg" = "$WATCHDOG_PID" ] || { echo "FAIL: canary watcher did not arm" >&2; exit 1; }

# Phase 2 creates the anchor-backed Codex group and stops again before exec.
kill -CONT "$CODEX_PID"
attempt=0; cpg=""; cstate=""
while [ "$attempt" -lt 200 ]; do
    attempt=$((attempt + 1))
    cpg="$(/bin/ps -o pgid= -p "$CODEX_PID" 2>/dev/null | tr -d ' ')"
    cstate="$(/bin/ps -o stat= -p "$CODEX_PID" 2>/dev/null | tr -d ' ')"
    if [ "$cpg" = "$CODEX_PID" ]; then
        case "$cstate" in *T*) break ;; esac
    fi
    kill -0 "$CODEX_PID" 2>/dev/null || break
    sleep 0.01
done
case "$cstate" in *T*) ;; *) cpg="" ;; esac
[ "$cpg" = "$CODEX_PID" ] || { echo "FAIL: canary anchor group was not established" >&2; exit 1; }
# Publish the identity transition before Codex runs. After this byte, the
# watcher signals only the stable anchored group and never the bare PID.
printf G >&6
kill -CONT -- "-$CODEX_PID"
set +e
wait "$CODEX_PID"
CODEX_RC=$?
set -e
CODEX_PID=""
exec 6>&-
WATCHDOG_FD_OPEN=0
wait "$WATCHDOG_PID" 2>/dev/null || true
WATCHDOG_PID=""
if [ -e "$TIMEOUT_MARKER" ]; then
    echo "FAIL: live Codex canary exceeded ${CANARY_TIMEOUT}s" >&2
    exit 1
fi
if [ "$CODEX_RC" -ne 0 ]; then
    echo "FAIL: live Codex canary exited $CODEX_RC" >&2
    tail -40 "$CODEX_STDOUT" >&2 || true
    exit "$CODEX_RC"
fi

python3 - "$PROJECT" "$START_MARKER" "$ONLY_PARENT_SENTINEL" <<'PY'
import json
import os
from pathlib import Path
import re
import sys
import tomllib

project = Path(sys.argv[1])
marker = Path(sys.argv[2])
parent_sentinel = sys.argv[3]

artifact = project / "process_log/native_role_canary.txt"
if not artifact.exists() or artifact.read_bytes() != b"NATIVE_SCORER_ROLE_OK\n":
    raise SystemExit("FAIL: scorer did not produce the exact requested artifact")

codex_state = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
sessions = codex_state / "sessions"
marker_ns = marker.stat().st_mtime_ns
child_candidates = []
parent_candidates = []
for path in sessions.glob("*/*/*/rollout-*.jsonl"):
    try:
        if path.stat().st_mtime_ns < marker_ns:
            continue
        with path.open() as handle:
            first = json.loads(next(handle))
    except (OSError, StopIteration, json.JSONDecodeError):
        continue
    payload = first.get("payload", {})
    if payload.get("cwd") != str(project):
        continue
    candidate = (path.stat().st_mtime_ns, path, payload)
    if payload.get("agent_role") == "scorer":
        child_candidates.append(candidate)
    elif payload.get("agent_role") is None:
        parent_candidates.append(candidate)
if len(child_candidates) != 1:
    raise SystemExit(f"FAIL: expected exactly one scorer child rollout, found {len(child_candidates)}")
if len(parent_candidates) != 1:
    raise SystemExit(f"FAIL: expected exactly one parent rollout, found {len(parent_candidates)}")

_, rollout, meta = max(child_candidates)
version_match = re.search(r"(\d+)\.(\d+)\.(\d+)", str(meta.get("cli_version", "")))
if not version_match or tuple(map(int, version_match.groups())) < (0, 147, 0):
    raise SystemExit(f"FAIL: unexpected Codex CLI version {meta.get('cli_version')!r}")
if meta.get("multi_agent_version") != "disabled":
    raise SystemExit("FAIL: scorer role was not assembled as a leaf")

events = []
raw = rollout.read_text(errors="replace")
for line in raw.splitlines():
    try:
        events.append(json.loads(line))
    except json.JSONDecodeError:
        raise SystemExit(f"FAIL: malformed child rollout line in {rollout}")

turns = [event.get("payload", {}) for event in events if event.get("type") == "turn_context"]
if not turns or turns[0].get("model") != "gpt-5.6-terra" or turns[0].get("effort") != "high":
    raise SystemExit("FAIL: scorer did not run on its declared Terra/high tier")
worlds = [event.get("payload", {}).get("state", {}) for event in events if event.get("type") == "world_state"]
if not worlds or worlds[0].get("agents_md") != {}:
    raise SystemExit("FAIL: scorer inherited project AGENTS.md")

role = tomllib.loads((project / ".codex/agents/scorer.toml").read_text())
developer_messages = []
for event in events:
    payload = event.get("payload", {})
    if event.get("type") != "response_item" or payload.get("role") != "developer":
        continue
    for part in payload.get("content", []):
        if part.get("type") == "input_text":
            developer_messages.append(part.get("text", ""))
if role["developer_instructions"] not in developer_messages:
    raise SystemExit("FAIL: scorer rollout did not receive its declared role instructions")
if parent_sentinel in raw:
    raise SystemExit("FAIL: fork_turns=none leaked parent-only context into the child")

_, parent_rollout, parent_meta = max(parent_candidates)
if meta.get("parent_thread_id") != parent_meta.get("id"):
    raise SystemExit("FAIL: selected scorer rollout is not parented by the selected parent rollout")
parent_events = []
for line in parent_rollout.read_text(errors="replace").splitlines():
    try:
        parent_events.append(json.loads(line))
    except json.JSONDecodeError:
        raise SystemExit(f"FAIL: malformed parent rollout line in {parent_rollout}")

spawn_calls = []
wait_calls = []
function_outputs = []
started_events = []
terminal_events = []
artifact_read_calls = []
artifact_read_outputs = []
finals = []
for index, event in enumerate(parent_events):
    payload = event.get("payload", {})
    if event.get("type") == "response_item" and payload.get("type") == "function_call":
        if payload.get("name") == "spawn_agent":
            try:
                arguments = json.loads(payload.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}
            spawn_calls.append((index, payload.get("call_id"), arguments))
        elif payload.get("name") == "wait_agent":
            try:
                arguments = json.loads(payload.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}
            wait_calls.append((index, payload.get("call_id"), arguments))
    if event.get("type") == "response_item" and payload.get("type") == "function_call_output":
        function_outputs.append((index, payload.get("call_id"), payload.get("output", "")))
    if (event.get("type") == "response_item" and payload.get("type") == "custom_tool_call"
            and payload.get("name") == "exec"):
        artifact_read_calls.append((index, payload.get("call_id"), payload.get("input", "")))
    if event.get("type") == "response_item" and payload.get("type") == "custom_tool_call_output":
        artifact_read_outputs.append((index, payload.get("call_id"), payload.get("output", [])))
    if event.get("type") == "event_msg" and payload.get("type") == "sub_agent_activity":
        if payload.get("kind") == "started":
            started_events.append((index, payload))
    if event.get("type") == "response_item" and payload.get("role") == "user":
        for part in payload.get("content", []):
            value = part.get("text", "")
            prefix = "<subagent_notification>\n"
            suffix = "\n</subagent_notification>"
            if not value.startswith(prefix) or not value.endswith(suffix):
                continue
            try:
                notification = json.loads(value[len(prefix):-len(suffix)])
            except json.JSONDecodeError:
                continue
            if notification.get("status") == {"completed": "CHILD_DONE"}:
                terminal_events.append((index, notification))
    if (event.get("type") == "response_item" and payload.get("role") == "assistant"
            and payload.get("phase") == "final_answer"):
        texts = [part.get("text", "") for part in payload.get("content", [])]
        finals.append((index, texts))

if len(spawn_calls) != 1:
    raise SystemExit(f"FAIL: expected exactly one parent spawn_agent call, found {len(spawn_calls)}")
spawn_index, spawn_call_id, spawn_args = spawn_calls[0]
if (spawn_args.get("agent_type"), spawn_args.get("fork_turns"), spawn_args.get("task_name")) != (
        "scorer", "none", "native_scorer_live_canary"):
    raise SystemExit("FAIL: parent spawn did not use the exact declared scorer/fresh/task identity")
spawn_outputs = [item for item in function_outputs if item[1] == spawn_call_id]
if len(spawn_outputs) != 1:
    raise SystemExit("FAIL: spawn call lacks exactly one bound function output")
spawn_output_index, _, spawn_output_raw = spawn_outputs[0]
try:
    spawn_output = json.loads(spawn_output_raw)
except json.JSONDecodeError:
    spawn_output = {}
if spawn_output.get("task_name") != "/root/native_scorer_live_canary":
    raise SystemExit("FAIL: spawn output does not name the requested canonical child task")
matching_starts = [item for item in started_events if item[1].get("event_id") == spawn_call_id]
if len(matching_starts) != 1:
    raise SystemExit("FAIL: spawn call did not produce exactly one bound child-start event")
started_index, started = matching_starts[0]
child_id = meta.get("id")
child_path = meta.get("agent_path")
if started.get("agent_thread_id") != child_id or started.get("agent_path") != child_path:
    raise SystemExit("FAIL: selected child rollout is not the child created by the spawn call")
if child_path != "/root/native_scorer_live_canary":
    raise SystemExit(f"FAIL: unexpected child task path {child_path!r}")
matching_terminals = [item for item in terminal_events if item[1].get("agent_path") == child_path]
if len(matching_terminals) != 1:
    raise SystemExit("FAIL: expected exactly one terminal notification bound to the spawned child")
terminal_index, _ = matching_terminals[0]
if len(wait_calls) != 1:
    raise SystemExit(f"FAIL: expected exactly one wait_agent call, found {len(wait_calls)}")
wait_index, wait_call_id, wait_args = wait_calls[0]
if wait_args.get("timeout_ms") != 3600000:
    raise SystemExit("FAIL: parent wait_agent did not use the requested bounded long wait")
wait_outputs = [item for item in function_outputs if item[1] == wait_call_id]
if len(wait_outputs) != 1:
    raise SystemExit("FAIL: wait call lacks exactly one bound function output")
wait_output_index, _, wait_output_raw = wait_outputs[0]
try:
    wait_output = json.loads(wait_output_raw)
except json.JSONDecodeError:
    wait_output = {}
if wait_output.get("timed_out") is not False:
    raise SystemExit(f"FAIL: parent wait did not return a non-timeout result: {wait_output_raw}")

if len(artifact_read_calls) != 1:
    raise SystemExit(f"FAIL: expected exactly one parent artifact-read exec, found {len(artifact_read_calls)}")
read_index, read_call_id, read_input = artifact_read_calls[0]
if "od -An -tx1 -v process_log/native_role_canary.txt" not in read_input:
    raise SystemExit("FAIL: parent did not issue the required exact-byte artifact read")
read_outputs = [item for item in artifact_read_outputs if item[1] == read_call_id]
if len(read_outputs) != 1:
    raise SystemExit("FAIL: artifact read lacks exactly one bound tool output")
read_output_index, _, read_output_parts = read_outputs[0]
read_output_text = read_output_parts[-1].get("text", "") if read_output_parts else ""
expected_hex = "4e 41 54 49 56 45 5f 53 43 4f 52 45 52 5f 52 4f 4c 45 5f 4f 4b 0a".split()
# Current exec envelopes include a hexadecimal chunk ID and decimal wall time
# before the command output, while od wraps after 16 bytes. Parse only the
# envelope's final-output payload and require its complete token stream.
output_payload = read_output_text.rsplit("Final output:\n", 1)[-1]
observed_hex = [value.lower() for value in re.findall(
    r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{2}(?![0-9A-Fa-f])", output_payload
)]
if observed_hex != expected_hex:
    raise SystemExit(f"FAIL: parent artifact read returned unexpected bytes: {observed_hex}")

if len(finals) != 1 or finals[0][1] != ["PARENT_WAITED_OK"]:
    raise SystemExit(f"FAIL: expected one exact parent final answer, found {finals}")
final_index = finals[0][0]
if not (spawn_index < started_index < spawn_output_index < wait_index < wait_output_index
        < terminal_index < read_index < read_output_index < final_index):
    raise SystemExit("FAIL: parent lifecycle evidence is missing or causally out of order")

print(f"PASS: native scorer role/model/context/wait canary ({parent_rollout.name}, {rollout.name})")
PY
