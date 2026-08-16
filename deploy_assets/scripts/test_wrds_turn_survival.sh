#!/usr/bin/env bash
# Codex-like process-group teardown must not kill the freshly started daemon.
set -euo pipefail

ASSET_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-wrds-turn.XXXXXX")"
PROJECT="$TEST_ROOT/project"
DAEMON_PID=""
cleanup() {
    if [[ "$DAEMON_PID" =~ ^[0-9]+$ ]]; then
        command="$(ps -o command= -p "$DAEMON_PID" 2>/dev/null || true)"
        case "$command" in
            *"$PROJECT/code/utils/fake_server.py"*) kill "$DAEMON_PID" 2>/dev/null || true ;;
        esac
    fi
    if [ "${KEEP_WRDS_TURN_TEST_ROOT:-0}" = "1" ]; then
        echo "kept WRDS turn test root: $TEST_ROOT" >&2
    else
        rm -rf "$TEST_ROOT"
    fi
}
trap cleanup EXIT

mkdir -p "$PROJECT/code/utils" "$PROJECT/.venv/bin"
cp "$ASSET_ROOT/extensions/empirical/utils/start_services.sh" \
    "$PROJECT/code/utils/start_services.sh"
cat > "$PROJECT/.env" <<'ENV'
WRDS_USER=test-user
WRDS_PASS=test-pass
ENV
cat > "$PROJECT/code/utils/fake_server.py" <<'PY'
import os, signal, sys, time

pid_path, ready_path = os.environ["WRDS_FAKE_PID"], os.environ["WRDS_FAKE_READY"]
with open(pid_path, "w", encoding="ascii") as handle:
    handle.write(f"{os.getpid()}\n")
with open(ready_path, "w", encoding="ascii") as handle:
    handle.write("ready\n")
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
signal.signal(signal.SIGHUP, signal.SIG_IGN)
while True:
    time.sleep(30)
PY
cat > "$PROJECT/.venv/bin/python3" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
args="$*"
case "$args" in
    *wrds_requires_bridge*) exit 1 ;;
    *wrds_bridge_ping*) exit 1 ;;
    *wrds_ping*)
        [ -s "${WRDS_FAKE_READY:?}" ] && [ -s "${WRDS_FAKE_PID:?}" ] || exit 1
        exit 0
        ;;
    *wrds_auth_error*) exit 0 ;;
    *wrds_login_in_progress*) printf '0\n'; exit 0 ;;
    *sys.platform.startswith*) exit 1 ;;
    *"os.setsid(); os.execv"*) exec /usr/bin/python3 "$@" ;;
    *"-u code/utils/wrds_server.py"*) exec /usr/bin/python3 code/utils/fake_server.py ;;
esac
printf 'unexpected fake-python call: %s\n' "$args" >&2
exit 1
SH
chmod +x "$PROJECT/.venv/bin/python3"

export WRDS_FAKE_PID="$TEST_ROOT/daemon.pid"
export WRDS_FAKE_READY="$TEST_ROOT/daemon.ready"
export HOME="$TEST_ROOT/home"
mkdir -p "$HOME"

# The managed group stays alive after start_services returns so the test can
# tear down the exact originating tool group, then probe from a fresh process.
/usr/bin/python3 -c \
    'import os,sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
    /bin/bash -c 'cd "$1"; bash code/utils/start_services.sh; printf ready > "$2"; while :; do sleep 30; done' \
    _ "$PROJECT" "$TEST_ROOT/tool.ready" \
    >"$TEST_ROOT/tool.log" 2>&1 &
TOOL_PID=$!
for _attempt in {1..200}; do
    [ -s "$TEST_ROOT/tool.ready" ] && break
    kill -0 "$TOOL_PID" 2>/dev/null || break
    sleep 0.02
done
[ -s "$TEST_ROOT/tool.ready" ] || {
    cat "$TEST_ROOT/tool.log" >&2
    echo "FAIL: managed startup tool did not become ready" >&2
    exit 1
}
read -r DAEMON_PID < "$WRDS_FAKE_PID"
DAEMON_PGID="$(ps -o pgid= -p "$DAEMON_PID" | tr -d ' ')"
[ "$DAEMON_PID" = "$DAEMON_PGID" ] || {
    echo "FAIL: WRDS daemon is not its own process-group leader" >&2
    exit 1
}

kill -TERM -- "-$TOOL_PID"
wait "$TOOL_PID" 2>/dev/null || true
kill -0 "$DAEMON_PID"
(cd "$PROJECT" && .venv/bin/python3 -c \
    'from utils.wrds_client import wrds_ping; raise SystemExit(0 if wrds_ping() else 1)')

echo "PASS: WRDS daemon survives originating managed process-group teardown"
