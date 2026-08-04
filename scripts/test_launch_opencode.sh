#!/usr/bin/env bash
set -euo pipefail

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-launch-test.XXXXXX")"
BIN="$TEST_ROOT/bin"
PROJECT="$TEST_ROOT/project"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$BIN" "$PROJECT/process_log" "$PROJECT/code/utils"
cp "$ROOT/launch.sh" "$PROJECT/launch.sh"
cp "$ROOT/templates/utils/opencode_driver.py" "$PROJECT/code/utils/opencode_driver.py"
chmod +x "$PROJECT/launch.sh" "$PROJECT/code/utils/opencode_driver.py"

cat > "$TEST_ROOT/mock_server.py" <<'PY'
import base64, json, os, signal, subprocess, sys, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

root = os.path.realpath(os.getcwd())
expected = "Basic " + base64.b64encode(
    (os.environ.get("OPENCODE_SERVER_USERNAME", "opencode") + ":" + os.environ["OPENCODE_SERVER_PASSWORD"]).encode()
).decode()

if os.environ.get("MOCK_SERVER_STUBBORN_DESCENDANT") == "1":
    descendant = subprocess.Popen([sys.executable, "-c", """
import os, signal, time
descendants = os.environ['MOCK_SERVER_DESCENDANTS']
term_seen = os.environ['MOCK_DESCENDANT_TERM_SEEN']
def ignore_term(_signum, _frame):
    with open(term_seen, 'a') as handle: handle.write(str(os.getpid()) + '\\n')
signal.signal(signal.SIGTERM, ignore_term)
with open(descendants, 'a') as handle: handle.write(str(os.getpid()) + '\\n')
while True: time.sleep(30)
"""])
    for _ in range(100):
        if os.path.exists(os.environ["MOCK_SERVER_DESCENDANTS"]):
            if str(descendant.pid) in open(os.environ["MOCK_SERVER_DESCENDANTS"]).read().splitlines():
                break
        time.sleep(0.01)
    else:
        raise RuntimeError("stubborn descendant did not initialize")

def bump(path):
    try: value = int(open(path).read())
    except Exception: value = 0
    value += 1
    open(path, "w").write(str(value))
    return value

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args): pass
    def send_value(self, value, status=200, raw=False):
        body = value.encode() if raw else json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def auth(self):
        if self.headers.get("Authorization") == expected: return True
        self.send_value({"error": "unauthorized"}, 401); return False
    def sessions(self):
        count = bump(os.environ["MOCK_LIST_COUNT"])
        if os.environ.get("MOCK_LIST_FAIL_FIRST") == "1" and count == 1:
            return "not-json", True
        if os.path.exists(os.environ["MOCK_CREATED"]):
            return [{"id": "ses_test", "directory": root}], False
        if os.environ.get("MOCK_VALID_SID"):
            return [{"id": os.environ["MOCK_VALID_SID"], "directory": root}], False
        raw = os.environ.get("MOCK_SESSIONS", "[]")
        try: return json.loads(raw), False
        except Exception: return raw, True
    def with_prompt(self, rows):
        path = os.environ.get("MOCK_LAST_PROMPT")
        if path and os.path.exists(path):
            rows.append({"info": {"role": "user"}, "parts": [
                {"type": "text", "text": open(path).read()},
            ]})
        return rows
    def do_GET(self):
        if not self.auth(): return
        if self.path == "/global/health":
            healthy = not os.path.exists(os.environ["MOCK_UNHEALTHY_MARKER"])
            return self.send_value({"healthy": healthy, "version": "1.18.11-test"})
        if self.path == "/session":
            value, raw = self.sessions(); return self.send_value(value, raw=raw)
        if self.path.endswith("/children"):
            rows = [{"id": "ses_child", "parentID": "ses_test"}] if os.environ.get("MOCK_BACKGROUND_BUSY") == "1" else []
            return self.send_value(rows)
        if self.path == "/session/status":
            marker = os.environ.get("MOCK_REUSED_BUSY_MARKER")
            if marker and os.path.exists(marker):
                count = bump(os.environ["MOCK_REUSED_BUSY_COUNT"])
                if count < 4: return self.send_value({"ses_test": {"type": "busy"}})
                os.unlink(marker)
            if os.environ.get("MOCK_BACKGROUND_BUSY") == "1":
                count = bump(os.environ["MOCK_STATUS_COUNT"])
                if count < 3: return self.send_value({"ses_child": {"type": "busy"}})
                if count < 6: return self.send_value({})
                if count == 6: return self.send_value({"ses_test": {"type": "busy"}})
            if os.environ.get("MOCK_ABORT_DELAY") == "1" and os.path.exists(os.environ["MOCK_ABORTED"]):
                count = bump(os.environ["MOCK_ABORT_STATUS_COUNT"])
                if count < 4: return self.send_value({"ses_test": {"type": "busy"}})
            return self.send_value({})
        if self.path.endswith("/message"):
            if os.environ.get("MOCK_MESSAGE_FAIL_FIRST") == "1":
                count = bump(os.environ["MOCK_MESSAGE_COUNT"])
                if count == 1: return self.send_value({"error": "transient"}, 503)
            if os.environ.get("MOCK_BACKGROUND_BUSY") == "1":
                try: count = int(open(os.environ["MOCK_STATUS_COUNT"]).read())
                except Exception: count = 0
                if count < 6: return self.send_value([])
            text = '<task id="ses_child" state="completed"><task_result>done</task_result></task>'
            missing_marker = os.environ.get("MOCK_MISSING_NOTIFICATION_MARKER")
            if os.environ.get("MOCK_MISSING_NOTIFICATION") == "1" or (missing_marker and os.path.exists(missing_marker)):
                return self.send_value(self.with_prompt([
                    {"info": {"role": "assistant", "time": {"completed": 1}}, "parts": [{"tool": "task", "state": {
                        "metadata": {"background": True, "sessionId": "ses_child"}}}]},
                ]))
            return self.send_value(self.with_prompt([
                {"info": {"role": "assistant", "time": {"completed": 1}}, "parts": [{"tool": "task", "state": {
                    "metadata": {"background": True, "sessionId": "ses_child"}}}]},
                {"info": {"role": "user"}, "parts": [{"type": "text", "synthetic": True, "text": text}]},
                {"info": {"role": "assistant", "time": {"completed": 2}}, "parts": []},
            ]))
        return self.send_value({"error": "missing"}, 404)
    def do_POST(self):
        if not self.auth(): return
        if self.path.endswith("/abort"):
            with open(os.environ["MOCK_ABORTS"], "a") as handle: handle.write(self.path + "\n")
            open(os.environ["MOCK_ABORTED"], "w").close()
            if os.environ.get("MOCK_ABORT_FAIL") == "1" and self.path.endswith("/ses_test/abort"):
                return self.send_value({"error": "abort failed"}, 500)
            return self.send_value(True)
        return self.send_value({"error": "missing"}, 404)

time.sleep(float(os.environ.get("MOCK_SERVER_START_DELAY", "0")))
server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
print(f"opencode server listening on http://127.0.0.1:{server.server_port}", flush=True)
server.serve_forever()
PY

cat > "$BIN/opencode" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
if [ -n "${OPENCODE_API_KEY:-}" ]; then key_set=1; else key_set=0; fi
if [ "${OPENCODE_API_KEY:-}" = "${MOCK_EXPECTED_KEY:-}" ]; then key_match=1; else key_match=0; fi
echo "external_skills=${OPENCODE_DISABLE_EXTERNAL_SKILLS:-} background=${OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS:-} username=${OPENCODE_SERVER_USERNAME:-} opencode_key_set=$key_set opencode_key_match=$key_match args=$*" >> "$MOCK_CALLS"
if [ "${1:-}" = "serve" ]; then
    exec python3 "$MOCK_SERVER_SCRIPT" opencode serve
fi
if [ "${1:-}" = "run" ]; then
    count=0
    [ -f "$MOCK_COUNT" ] && count="$(cat "$MOCK_COUNT")"
    count=$((count + 1)); printf '%s\n' "$count" > "$MOCK_COUNT"
    printf '%s\n' "${!#}" > "$MOCK_LAST_PROMPT"
    : > "$MOCK_CREATED"
    if ! { [ "${MOCK_NO_EVENT_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; }; then
        if [ "${MOCK_MALFORMED_SID_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; then
            printf '%s\n' '{"type":"step_start","sessionID":7,"part":{"type":"step-start"}}'
        else
            printf '%s\n' '{"type":"step_start","sessionID":"ses_test","part":{"type":"step-start"}}'
        fi
    fi
    if [ "${MOCK_CHILD_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; then
        (trap '' TERM; while :; do sleep 30; done) &
        printf '%s\n' "$!" > "$MOCK_CHILD_PID"
    fi
    if [ "${MOCK_TIMEOUT_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; then sleep 30; fi
    if [ -n "${MOCK_RUN_SLEEP:-}" ]; then sleep "$MOCK_RUN_SLEEP"; fi
    if [ "${MOCK_TOOL_TYPE:-task}" != "none" ]; then
        printf '{"type":"tool_use","sessionID":"ses_test","part":{"tool":"%s","state":{"status":"completed","metadata":{"background":true,"sessionId":"ses_child"}}}}\n' "${MOCK_TOOL_TYPE:-task}"
    fi
    if [ "$count" -ge "${MOCK_COMPLETE_AFTER:-1}" ]; then
        printf '%s\n' '{"status":"complete"}' > process_log/pipeline_state.json
    fi
fi
MOCK
chmod +x "$BIN/opencode"

export PATH="$BIN:$PATH"
export MOCK_SERVER_SCRIPT="$TEST_ROOT/mock_server.py"
export MOCK_CALLS="$TEST_ROOT/calls"
export MOCK_COUNT="$TEST_ROOT/count"
export MOCK_LIST_COUNT="$TEST_ROOT/list-count"
export MOCK_STATUS_COUNT="$TEST_ROOT/status-count"
export MOCK_CREATED="$TEST_ROOT/created"
export MOCK_CHILD_PID="$TEST_ROOT/child-pid"
export MOCK_ABORTS="$TEST_ROOT/aborts"
export MOCK_ABORTED="$TEST_ROOT/aborted"
export MOCK_ABORT_STATUS_COUNT="$TEST_ROOT/abort-status-count"
export MOCK_MESSAGE_COUNT="$TEST_ROOT/message-count"
export MOCK_LAST_PROMPT="$TEST_ROOT/last-prompt"
export MOCK_UNHEALTHY_MARKER="$TEST_ROOT/unhealthy"
export MOCK_MISSING_NOTIFICATION_MARKER="$TEST_ROOT/missing-notification"
export MOCK_REUSED_BUSY_MARKER="$TEST_ROOT/reused-busy"
export MOCK_REUSED_BUSY_COUNT="$TEST_ROOT/reused-busy-count"
export MOCK_SERVER_DESCENDANTS="$TEST_ROOT/server-descendants"
export MOCK_DESCENDANT_TERM_SEEN="$TEST_ROOT/descendant-term-seen"
export OPENCODE_LOOP_DELAY=0
export MOCK_EXPECTED_KEY=test-only-secret

stop_mock_server() {
    local pid command descendant_pid
    if [ -s "$PROJECT/process_log/.opencode_server_pid" ]; then
        pid="$(cat "$PROJECT/process_log/.opencode_server_pid")"
        if [[ "$pid" =~ ^[0-9]+$ ]]; then
            command="$(ps -o command= -p "$pid" 2>/dev/null || true)"
            case "$command" in
                *"$MOCK_SERVER_SCRIPT"*)
                    kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
                    for _ in $(seq 1 50); do kill -0 -- "-$pid" 2>/dev/null || break; sleep 0.02; done
                    kill -KILL -- "-$pid" 2>/dev/null || true
                    for _ in $(seq 1 50); do kill -0 -- "-$pid" 2>/dev/null || break; sleep 0.02; done
                    ;;
            esac
        fi
    fi
    if [ -s "$MOCK_SERVER_DESCENDANTS" ]; then
        while IFS= read -r descendant_pid; do
            [[ "$descendant_pid" =~ ^[0-9]+$ ]] || continue
            command="$(ps -o command= -p "$descendant_pid" 2>/dev/null || true)"
            case "$command" in
                *MOCK_SERVER_DESCENDANTS*) kill -KILL "$descendant_pid" 2>/dev/null || true ;;
            esac
        done < "$MOCK_SERVER_DESCENDANTS"
    fi
}
trap 'stop_mock_server; rm -rf "$TEST_ROOT"' EXIT

reset_project() {
    stop_mock_server
    printf '%s\n' '{"status":"running"}' > "$PROJECT/process_log/pipeline_state.json"
    printf '%s\n' 'OPENCODE_API_KEY=test-only-secret' > "$PROJECT/.env"
    rm -f "$PROJECT/process_log/.opencode_session_id" "$PROJECT/process_log/.opencode_server_"* \
        "$PROJECT/process_log/.opencode_background_children" \
        "$PROJECT/process_log/.opencode_background_parent" "$PROJECT/process_log"/.opencode-server-password.* \
        "$PROJECT/process_log/.opencode_background_baseline" "$PROJECT/process_log"/.opencode-baseline.* \
        "$PROJECT/process_log/.opencode_background_transition" "$PROJECT/process_log"/.opencode-transition.* \
        "$PROJECT/process_log/.opencode_recovery_intent" "$PROJECT/process_log"/.opencode-recovery.* \
        "$PROJECT/process_log/.opencode_parent_server_epoch" "$PROJECT/process_log"/.opencode-parent-epoch.* \
        "$PROJECT/process_log"/.opencode-unresolved.* "$PROJECT/process_log"/.opencode-session.* \
        "$PROJECT/process_log/.opencode_unresolved_session" "$PROJECT/process_log"/.opencode-server-identity.* \
        "$PROJECT/process_log/.opencode_driver_lock" "$PROJECT/process_log"/.opencode-lock-ready.* \
        "$MOCK_CALLS" "$MOCK_COUNT" "$MOCK_LIST_COUNT" "$MOCK_STATUS_COUNT" \
        "$MOCK_ABORT_STATUS_COUNT" "$MOCK_MESSAGE_COUNT" "$MOCK_CREATED" "$MOCK_CHILD_PID" "$MOCK_ABORTS" "$MOCK_ABORTED"
    rm -f "$MOCK_SERVER_DESCENDANTS" "$MOCK_DESCENDANT_TERM_SEEN"
    rm -f "$MOCK_LAST_PROMPT"
    rm -f "$MOCK_UNHEALTHY_MARKER"
    rm -f "$MOCK_MISSING_NOTIFICATION_MARKER"
    rm -f "$PROJECT/process_log/opencode-driver.log" "$PROJECT/process_log/opencode-server.log"
    rm -f "$MOCK_REUSED_BUSY_MARKER" "$MOCK_REUSED_BUSY_COUNT"
}

# Interactive launch imports the credential safely and enables native background
# task schema discovery without using --auto.
reset_project
(cd "$PROJECT" && env -u OPENCODE_API_KEY OPENCODE_SERVER_USERNAME=custom ./launch.sh opencode --once)
grep -q '^external_skills=1 background=true username=opencode opencode_key_set=1 opencode_key_match=1 args=--model opencode/deepseek-v4-flash$' "$MOCK_CALLS"
! grep -q 'test-only-secret' "$MOCK_CALLS"
! grep -q -- '--auto' "$MOCK_CALLS"

# Standard quoted dotenv values, parent precedence, and literal shell-looking
# values retain the v2.20.0 safety contract.
reset_project
printf '%s\n' 'OPENCODE_API_KEY="double-quoted" # local key' > "$PROJECT/.env"
(cd "$PROJECT" && env -u OPENCODE_API_KEY MOCK_EXPECTED_KEY=double-quoted ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"
reset_project
(cd "$PROJECT" && OPENCODE_API_KEY=parent-key MOCK_EXPECTED_KEY=parent-key ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"
reset_project
side_effect="$TEST_ROOT/should-not-exist"
printf 'OPENCODE_API_KEY=$(touch %s) `touch %s`\n' "$side_effect" "$side_effect" > "$PROJECT/.env"
literal_key="\$(touch $side_effect) \`touch $side_effect\`"
(cd "$PROJECT" && env -u OPENCODE_API_KEY MOCK_EXPECTED_KEY="$literal_key" ./launch.sh opencode --once)
test ! -e "$side_effect"

# Fresh headless work is attached to an authenticated persistent server; a
# terminal pipeline stops that server and clears its runtime state.
reset_project
(cd "$PROJECT" && ./launch.sh opencode)
grep -q '^ses_test$' "$PROJECT/process_log/.opencode_session_id"
grep -q 'args=serve --hostname 127.0.0.1 --port 0' "$MOCK_CALLS"
grep -q 'args=run --attach http://127.0.0.1:' "$MOCK_CALLS"
test ! -e "$PROJECT/process_log/.opencode_server_pid"

# A crash between announcing startup and publishing a complete identity must
# block a later launcher instead of allowing an overlapping server.
reset_project
printf '%s\n' pending > "$PROJECT/process_log/.opencode_server_starting"
if (cd "$PROJECT" && ./launch.sh opencode); then
    echo "incomplete startup marker allowed a replacement server" >&2; exit 1
fi
test "$(cat "$PROJECT/process_log/.opencode_server_starting")" = pending
test ! -e "$MOCK_CALLS"

# Cached sessions are accepted only when the persistent server reports that
# they belong to this physical checkout.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_VALID_SID=good ./launch.sh opencode)
grep -q -- '--session good --model opencode/deepseek-v4-flash' "$MOCK_CALLS"
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_SESSIONS='[{"id":"good","directory":"/another/project"}]' ./launch.sh opencode)
! grep -q -- '--session good ' "$MOCK_CALLS"

# A ledger from a stale parent is discarded rather than imposed on the fresh
# replacement session.
reset_project
printf '%s\n' stale > "$PROJECT/process_log/.opencode_session_id"
printf '%s\n' old-child > "$PROJECT/process_log/.opencode_background_children"
printf '%s\n' stale > "$PROJECT/process_log/.opencode_background_parent"
(cd "$PROJECT" && ./launch.sh opencode)
test ! -e "$PROJECT/process_log/.opencode_background_children"

# A wedged attached client is killed without killing the persistent server;
# the parent session is aborted through the HTTP API and then resumed.
reset_project
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_CHILD_FIRST=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=1 ./launch.sh opencode)
grep -q -- '--session ses_test --model opencode/deepseek-v4-flash' "$MOCK_CALLS"
grep -q '/session/ses_test/abort' "$MOCK_ABORTS"
child_pid="$(cat "$MOCK_CHILD_PID")"
! kill -0 "$child_pid" 2>/dev/null

# If the first JSON event is unavailable after timeout, reconcile exactly the
# one session created since a valid pre-run server snapshot.
reset_project
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_NO_EVENT_FIRST=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode)
grep -q -- '--session ses_test --model opencode/deepseek-v4-flash' "$MOCK_CALLS"
reset_project
if (cd "$PROJECT" && MOCK_LIST_FAIL_FIRST=1 MOCK_TIMEOUT_FIRST=1 MOCK_NO_EVENT_FIRST=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode); then
    echo "invalid session-list baseline was reconciled" >&2; exit 1
fi
grep -q 'timed-out first turn returned no session id' "$PROJECT/process_log/opencode-driver.log"
test -s "$PROJECT/process_log/.opencode_unresolved_session"
if (cd "$PROJECT" && ./launch.sh opencode); then
    echo "unresolved first-turn marker allowed a duplicate parent" >&2; exit 1
fi
test "$(cat "$MOCK_COUNT")" = 1

# A malformed event SID cannot clear the pre-dispatch quarantine or fall back
# to session-list reconciliation, even if the server did create one session.
reset_project
if (cd "$PROJECT" && MOCK_MALFORMED_SID_FIRST=1 ./launch.sh opencode); then
    echo "malformed first-turn SID was accepted" >&2; exit 1
fi
test -s "$PROJECT/process_log/.opencode_unresolved_session"
test "$(cat "$MOCK_COUNT")" = 1

# Native background work delays the external continuation through child busy,
# parent autowake-busy, and two stable idle samples.
reset_project
(cd "$PROJECT" && MOCK_BACKGROUND_BUSY=1 MOCK_COMPLETE_AFTER=2 ./launch.sh opencode)
test "$(cat "$MOCK_COUNT")" = 2
test "$(cat "$MOCK_STATUS_COUNT")" -ge 8

# Cancellation is a barrier, not a fire-and-forget POST: delayed server
# quiescence must be observed before the parent is resumed.
reset_project
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_ABORT_DELAY=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode)
test "$(cat "$MOCK_ABORT_STATUS_COUNT")" -ge 4

# Cancellation quiescence is status-only: an aborted launch that never emitted
# a synthetic completion is retired by the persisted post-cancel epoch.
reset_project
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_MISSING_NOTIFICATION=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode)
test -s "$PROJECT/process_log/.opencode_background_baseline"
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2

# Server replacement is not complete when only the leader exits. A descendant
# in the same PGID ignores TERM; the launcher must KILL and confirm the whole
# group is gone before publishing the replacement server/baseline.
reset_project
(cd "$PROJECT" && MOCK_SERVER_STUBBORN_DESCENDANT=1 MOCK_TIMEOUT_FIRST=1 \
    OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=1 ./launch.sh opencode)
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2
test "$(wc -l < "$MOCK_DESCENDANT_TERM_SEEN" | tr -d ' ')" -ge 2
while IFS= read -r descendant_pid; do
    for _ in $(seq 1 50); do kill -0 "$descendant_pid" 2>/dev/null || break; sleep 0.02; done
    ! kill -0 "$descendant_pid" 2>/dev/null
done < "$MOCK_SERVER_DESCENDANTS"
test -s "$PROJECT/process_log/.opencode_background_baseline"

# A failed abort is fail-closed: no overlapping continuation is submitted.
reset_project
if (cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_ABORT_FAIL=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode); then
    echo "failed cancellation resumed the parent" >&2; exit 1
fi
test "$(cat "$MOCK_COUNT")" = 1
failed_server_pid="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -TERM -- "-$failed_server_pid" 2>/dev/null || true
for _ in $(seq 1 50); do kill -0 "$failed_server_pid" 2>/dev/null || break; sleep 0.1; done

# The project lock rejects a concurrent driver before it can attach another
# prompt to the same parent or stop the first driver's server.
reset_project
(cd "$PROJECT" && exec env MOCK_RUN_SLEEP=2 ./launch.sh opencode) &
first_driver=$!
for _ in $(seq 1 50); do [ -f "$PROJECT/process_log/.opencode_driver_lock" ] && break; sleep 0.02; done
if (cd "$PROJECT" && ./launch.sh opencode); then
    echo "concurrent OpenCode driver acquired the project" >&2; exit 1
fi
wait "$first_driver"

# A signal during the server-start window reaps the detached server and frees
# the lock even before its URL/password state is complete.
reset_project
(cd "$PROJECT" && exec env MOCK_SERVER_START_DELAY=5 ./launch.sh opencode) &
starting_driver=$!
for _ in $(seq 1 50); do [ -s "$PROJECT/process_log/.opencode_server_pid" ] && break; sleep 0.1; done
starting_server="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -TERM "$starting_driver"
wait "$starting_driver" 2>/dev/null || true
! kill -0 "$starting_server" 2>/dev/null
test -f "$PROJECT/process_log/.opencode_driver_lock"

# Quarantine parent creation before the first attached command. A signal after
# the server creates the session but before the CLI returns cannot permit a
# later launcher to submit a duplicate first prompt.
reset_project
(cd "$PROJECT" && exec env MOCK_RUN_SLEEP=5 ./launch.sh opencode) &
first_turn_driver=$!
for _ in $(seq 1 50); do [ -e "$MOCK_CREATED" ] && break; sleep 0.1; done
kill -TERM "$first_turn_driver"
wait "$first_turn_driver" 2>/dev/null || true
test -s "$PROJECT/process_log/.opencode_unresolved_session"
if (cd "$PROJECT" && ./launch.sh opencode); then
    echo "interrupted first-turn quarantine allowed a duplicate parent" >&2; exit 1
fi
test "$(cat "$MOCK_COUNT")" = 1

# A restart can recover a partial cached-server bundle: PID/start identity is
# enough to reap the exact old process before creating a replacement.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "partial-state fixture did not preserve its server" >&2; exit 1
fi
partial_server="$(cat "$PROJECT/process_log/.opencode_server_pid")"
rm -f "$PROJECT/process_log/.opencode_server_url" "$PROJECT/process_log/.opencode_server_password"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
! kill -0 "$partial_server" 2>/dev/null
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2

# A one-shot API failure followed by healthy reuse is not called a restart and
# never triggers an automatic duplicate prompt/relaunch instruction.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
if (cd "$PROJECT" && MOCK_VALID_SID=good MOCK_MESSAGE_FAIL_FIRST=1 ./launch.sh opencode); then
    echo "transient message failure prompted the live session" >&2; exit 1
fi
test ! -e "$MOCK_COUNT"
transient_server="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -0 "$transient_server"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 1

# A transient session-list failure never converts a cached parent into a fresh,
# duplicate session. The same server can be inspected/resumed on the next run.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
if (cd "$PROJECT" && MOCK_VALID_SID=good MOCK_LIST_FAIL_FIRST=1 ./launch.sh opencode); then
    echo "session-list failure created a replacement parent" >&2; exit 1
fi
test ! -e "$MOCK_COUNT"
list_failure_server="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -0 "$list_failure_server"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 1

# If a server dies and replacement is published before recovery setup, the
# always-present parent/server epoch still forces a tokenized recovery prompt.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "epoch fixture did not preserve its server" >&2; exit 1
fi
old_epoch_server="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -TERM -- "-$old_epoch_server" 2>/dev/null || true
for _ in $(seq 1 50); do kill -0 "$old_epoch_server" 2>/dev/null || break; sleep 0.1; done
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
grep -q 'zp-recovery-' "$MOCK_LAST_PROMPT"
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2

# A complete cached identity that is temporarily unhealthy is preserved rather
# than converting a short API outage into destructive server replacement.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "health-preservation fixture did not preserve its server" >&2; exit 1
fi
unhealthy_pid="$(cat "$PROJECT/process_log/.opencode_server_pid")"
: > "$MOCK_UNHEALTHY_MARKER"
if (cd "$PROJECT" && ./launch.sh opencode); then
    echo "temporarily unhealthy exact server was replaced" >&2; exit 1
fi
kill -0 "$unhealthy_pid"
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 1
rm -f "$MOCK_UNHEALTHY_MARKER"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)

# A crash-persisted cancellation transition is completed idempotently: the
# server instance is replaced, recovery intent is dispatched once, and the
# token becomes observable before the intent file is cleared.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "transition fixture did not preserve its server" >&2; exit 1
fi
printf '%s\n' 'ses_test cancel' > "$PROJECT/process_log/.opencode_background_transition"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
grep -q 'zp-recovery-' "$MOCK_LAST_PROMPT"
test ! -e "$PROJECT/process_log/.opencode_recovery_intent"
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2

# Missing epoch plus a surviving positive baseline still reconstructs from
# history zero; a pre-baseline unnotified launch must force cancellation.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "positive-baseline fixture did not preserve its server" >&2; exit 1
fi
saved_epoch="$(awk '{print $2}' "$PROJECT/process_log/.opencode_parent_server_epoch")"
printf 'ses_test %s 1\n' "$saved_epoch" > "$PROJECT/process_log/.opencode_background_baseline"
rm -f "$PROJECT/process_log/.opencode_parent_server_epoch"
: > "$MOCK_MISSING_NOTIFICATION_MARKER"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 OPENCODE_BACKGROUND_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode)
grep -q '/session/ses_test/abort' "$MOCK_ABORTS"
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 2

# A missing epoch with no suspicious baseline adopts the exact reused server
# only after it has passed the ordinary parent-busy and stable-idle barrier.
reset_project
if (cd "$PROJECT" && MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=1 ./launch.sh opencode); then
    echo "empty-turn guard did not fire" >&2; exit 1
fi
server_pid="$(cat "$PROJECT/process_log/.opencode_server_pid")"
kill -0 "$server_pid"
rm -f "$PROJECT/process_log/.opencode_parent_server_epoch"
: > "$MOCK_REUSED_BUSY_MARKER"
(cd "$PROJECT" && MOCK_COMPLETE_AFTER=1 ./launch.sh opencode)
test "$(grep -c 'args=serve ' "$MOCK_CALLS")" = 1
test "$(cat "$MOCK_REUSED_BUSY_COUNT")" -ge 4
test -s "$PROJECT/process_log/.opencode_parent_server_epoch"
! kill -0 "$server_pid" 2>/dev/null

echo "OpenCode launcher tests passed"
