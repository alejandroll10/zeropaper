#!/usr/bin/env bash
# Deterministic, credential-free exercise of the production Codex turn
# watchdog. The first fake turn and its descendant ignore TERM, so the test
# covers KILL escalation and proves cleanup finishes before a resumed turn.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-codex-watchdog.XXXXXX")"
PROJECT="$TEST_ROOT/project \"\\ identity"
CUSTOM_CODEX_HOME="$TEST_ROOT/codex \"\\ state"
FAKE_BIN="$TEST_ROOT/bin"
FAKE_CHILD_PID_FILE="$TEST_ROOT/fake-child.pid"
FAKE_COUNT_FILE="$TEST_ROOT/fake-count"
OUTPUT="$TEST_ROOT/launch.log"
ABORT_OUTPUT="$TEST_ROOT/abort.log"
LOCK_READY="$TEST_ROOT/lock-contender.ready"
LOCK_RESULT="$TEST_ROOT/lock-contender.result"
LOCK_PID=""

cleanup() {
    trap - EXIT
    if [ -n "$LOCK_PID" ]; then
        kill -KILL "$LOCK_PID" 2>/dev/null || true
        wait "$LOCK_PID" 2>/dev/null || true
    fi
    if [ -s "$FAKE_CHILD_PID_FILE" ]; then
        fake_child_pid="$(cat "$FAKE_CHILD_PID_FILE")"
        kill -KILL "$fake_child_pid" 2>/dev/null || true
    fi
    rm -rf -- "$TEST_ROOT"
}
trap cleanup EXIT

mkdir -p "$FAKE_BIN" "$TEST_ROOT/home"
"$ROOT/setup.sh" "$PROJECT" --variant finance --assemble-only --no-model-probe >/dev/null

# Seed one project-bound session so a timed-out first turn takes the actual
# resume path instead of exiting early because no rollout was recorded.
SESSION_ID="01a00000-0000-7000-8000-watchdog0001"
SESSION_DIR="$CUSTOM_CODEX_HOME/sessions/2026/08/17"
mkdir -p "$SESSION_DIR"
/usr/bin/python3 -I -c 'import json,sys
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    json.dump({"payload": {"cwd": sys.argv[2], "session_id": sys.argv[3]}}, handle)
    handle.write("\n")' \
    "$SESSION_DIR/rollout-2026-08-17T00-00-00-$SESSION_ID.jsonl" "$PROJECT" "$SESSION_ID"

# launch.sh asks for a version during preflight, then runs `codex exec resume`.
# Turn one deliberately ignores TERM throughout its group. Turn two records
# that the driver really resumed only after cleanup, marks the toy pipeline
# complete, and exits normally.
cat > "$FAKE_BIN/codex" <<'FAKE_CODEX'
#!/usr/bin/env bash
set -euo pipefail
if [ "${1:-}" = "--version" ]; then
    echo "codex-cli 0.147.0"
    exit 0
fi
v2_parent=0
for arg in "$@"; do
    [ "$arg" != "features.multi_agent_v2=true" ] || v2_parent=1
done
[ "$v2_parent" = "1" ] || {
    echo "fake Codex did not receive the parent MultiAgent V2 pin" >&2
    exit 64
}
count=0
[ ! -f "${FAKE_COUNT_FILE:?}" ] || count="$(cat "$FAKE_COUNT_FILE")"
count=$((count + 1))
printf '%s\n' "$count" > "$FAKE_COUNT_FILE"
if [ "$count" -gt 1 ]; then
    python3 -c 'import json,sys
p=sys.argv[1]
data=json.load(open(p))
data["status"]="complete"
with open(p,"w") as handle: json.dump(data,handle)' "${FAKE_STATE_FILE:?}"
    exit 0
fi
trap '' TERM
# Match Codex 0.147 shell execution: redirected shell tools call setsid() and
# therefore escape the turn wrapper PGID. Ignoring TERM proves the production
# watcher recursively contains and reaps that distinct session before resume.
/usr/bin/python3 -I -c 'import os, signal, time
os.setsid()
signal.signal(signal.SIGTERM, signal.SIG_IGN)
while True:
    time.sleep(120)' &
child_pid=$!
printf '%s\n' "$child_pid" > "${FAKE_CHILD_PID_FILE:?}"
wait "$child_pid"
FAKE_CODEX
chmod +x "$FAKE_BIN/codex"

start=$SECONDS
set +e
(
    cd "$PROJECT"
    PATH="$FAKE_BIN:/usr/bin:/bin" \
        HOME="$TEST_ROOT/home" \
        CODEX_HOME="$CUSTOM_CODEX_HOME" \
        FAKE_CHILD_PID_FILE="$FAKE_CHILD_PID_FILE" \
        FAKE_COUNT_FILE="$FAKE_COUNT_FILE" \
        FAKE_STATE_FILE="$PROJECT/process_log/pipeline_state.json" \
        TURN_TIMEOUT=1 \
        MAX_TURNS=2 \
        ./launch.sh codex
) >"$OUTPUT" 2>&1
rc=$?
set -e
elapsed=$((SECONDS - start))

if [ "$rc" -ne 0 ]; then
    echo "FAIL: driver did not resume successfully after timeout" >&2
    cat "$OUTPUT" >&2
    exit 1
fi
if [ "$elapsed" -gt 25 ]; then
    echo "FAIL: watchdog did not bound the turn (elapsed=${elapsed}s)" >&2
    cat "$OUTPUT" >&2
    exit 1
fi
if ! grep -qF "turn exceeded TURN_TIMEOUT=1s" "$OUTPUT"; then
    echo "FAIL: production watchdog timeout diagnostic was absent" >&2
    cat "$OUTPUT" >&2
    exit 1
fi
if [ "$(cat "$FAKE_COUNT_FILE" 2>/dev/null || true)" != "2" ]; then
    echo "FAIL: driver did not execute exactly one recovery turn" >&2
    cat "$OUTPUT" >&2
    exit 1
fi
if [ ! -s "$FAKE_CHILD_PID_FILE" ]; then
    echo "FAIL: fake Codex descendant never started" >&2
    cat "$OUTPUT" >&2
    exit 1
fi
fake_child_pid="$(cat "$FAKE_CHILD_PID_FILE")"
for _ in 1 2 3 4 5; do
    if ! kill -0 "$fake_child_pid" 2>/dev/null; then
        break
    fi
    sleep 1
done
if kill -0 "$fake_child_pid" 2>/dev/null; then
    echo "FAIL: launch.sh leaked fake Codex descendant $fake_child_pid" >&2
    cat "$OUTPUT" >&2
    exit 1
fi

# Exercise the other liveness-pipe edge: the visible supervisor is SIGKILLed
# while a turn is active. The escaped watcher plus nested anchor must reap the
# turn group even while the outer guardian SIGKILLs the original runtime group.
python3 -c 'import json,sys
p=sys.argv[1]
data=json.load(open(p))
data["status"]="running"
with open(p,"w") as handle: json.dump(data,handle)' "$PROJECT/process_log/pipeline_state.json"
rm -f "$FAKE_COUNT_FILE" "$FAKE_CHILD_PID_FILE"
(
    cd "$PROJECT"
    exec env \
        PATH="$FAKE_BIN:/usr/bin:/bin" \
        HOME="$TEST_ROOT/home" \
        CODEX_HOME="$CUSTOM_CODEX_HOME" \
        FAKE_CHILD_PID_FILE="$FAKE_CHILD_PID_FILE" \
        FAKE_COUNT_FILE="$FAKE_COUNT_FILE" \
        FAKE_STATE_FILE="$PROJECT/process_log/pipeline_state.json" \
        TURN_TIMEOUT=120 \
        MAX_TURNS=2 \
        ./launch.sh codex
) >"$ABORT_OUTPUT" 2>&1 &
launcher_pid=$!
for _ in $(seq 1 200); do
    [ -s "$FAKE_CHILD_PID_FILE" ] && break
    kill -0 "$launcher_pid" 2>/dev/null || break
    sleep 0.02
done
if [ ! -s "$FAKE_CHILD_PID_FILE" ]; then
    echo "FAIL: parent-abort fake Codex descendant never started" >&2
    cat "$ABORT_OUTPUT" >&2
    exit 1
fi
aborted_child_pid="$(cat "$FAKE_CHILD_PID_FILE")"
# Queue an updater-shaped exclusive-lock contender before the crash. When it
# eventually acquires, it records whether the stubborn writer is still alive;
# acquisition must not overtake watcher teardown.
python3 -c 'import fcntl, os, sys
root, ready, result, child = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
with open(ready, "x"):
    pass
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    os.kill(child, 0)
except ProcessLookupError:
    state = "dead"
else:
    state = "alive"
with open(result, "x") as handle:
    handle.write(state + "\n")' \
    "$PROJECT" "$LOCK_READY" "$LOCK_RESULT" "$aborted_child_pid" &
LOCK_PID=$!
for _ in $(seq 1 200); do
    [ -e "$LOCK_READY" ] && break
    kill -0 "$LOCK_PID" 2>/dev/null || break
    sleep 0.01
done
if [ ! -e "$LOCK_READY" ] || [ -e "$LOCK_RESULT" ]; then
    echo "FAIL: exclusive-lock contender was not blocked before supervisor death" >&2
    exit 1
fi
kill -KILL "$launcher_pid"
set +e
wait "$launcher_pid" 2>/dev/null
abort_rc=$?
set -e
if [ "$abort_rc" -eq 0 ]; then
    echo "FAIL: SIGKILL-aborted launcher unexpectedly succeeded" >&2
    cat "$ABORT_OUTPUT" >&2
    exit 1
fi
wait "$LOCK_PID"
LOCK_PID=""
if [ "$(cat "$LOCK_RESULT" 2>/dev/null || true)" != "dead" ]; then
    echo "FAIL: project exclusive lock was released before orphan cohort teardown" >&2
    cat "$ABORT_OUTPUT" >&2
    exit 1
fi
for _ in 1 2 3 4 5; do
    if ! kill -0 "$aborted_child_pid" 2>/dev/null; then
        break
    fi
    sleep 1
done
if kill -0 "$aborted_child_pid" 2>/dev/null; then
    echo "FAIL: parent death leaked fake Codex descendant $aborted_child_pid" >&2
    cat "$ABORT_OUTPUT" >&2
    exit 1
fi

echo "PASS: production Codex watchdog reaped setsid tool cohorts on timeout and parent abort before recovery (${elapsed}s timeout path)"
