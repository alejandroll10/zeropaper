#!/usr/bin/env bash
set -euo pipefail

TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-launch-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
BIN="$TEST_ROOT/bin"
PROJECT="$TEST_ROOT/project"
mkdir -p "$BIN" "$PROJECT/process_log"
cp "$(cd "$(dirname "$0")/.." && pwd)/launch.sh" "$PROJECT/launch.sh"
chmod +x "$PROJECT/launch.sh"

cat > "$BIN/opencode" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail
if [ -n "${OPENCODE_API_KEY:-}" ]; then key_set=1; else key_set=0; fi
if [ "${OPENCODE_API_KEY:-}" = "${MOCK_EXPECTED_KEY:-}" ]; then key_match=1; else key_match=0; fi
echo "external_skills=${OPENCODE_DISABLE_EXTERNAL_SKILLS:-} opencode_key_set=$key_set opencode_key_match=$key_match args=$*" >> "$MOCK_CALLS"
if [ "${1:-}" = "session" ]; then
    list_count=0
    [ -f "$MOCK_LIST_COUNT" ] && list_count="$(cat "$MOCK_LIST_COUNT")"
    list_count=$((list_count + 1))
    printf '%s\n' "$list_count" > "$MOCK_LIST_COUNT"
    if [ "${MOCK_LIST_FAIL_FIRST:-0}" = "1" ] && [ "$list_count" = "1" ]; then
        exit 1
    fi
    if [ "${MOCK_LIST_CREATED:-0}" = "1" ] && [ -f "${MOCK_CREATED:-/nonexistent}" ]; then
        printf '[{"id":"ses_test","directory":"%s"}]\n' "$(pwd -P)"
        exit 0
    fi
    if [ -n "${MOCK_VALID_SID:-}" ]; then
        printf '[{"id":"%s","directory":"%s"}]\n' "$MOCK_VALID_SID" "$(pwd -P)"
    else
        printf '%s\n' "${MOCK_SESSIONS:-[]}"
    fi
    exit 0
fi
if [ "${1:-}" = "run" ]; then
    count=0
    [ -f "$MOCK_COUNT" ] && count="$(cat "$MOCK_COUNT")"
    count=$((count + 1))
    printf '%s\n' "$count" > "$MOCK_COUNT"
    : > "${MOCK_CREATED:-/dev/null}"
    if ! { [ "${MOCK_NO_EVENT_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; }; then
        printf '%s\n' '{"type":"step_start","sessionID":"ses_test","part":{"type":"step-start"}}'
    fi
    if [ "${MOCK_CHILD_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; then
        (trap '' TERM; while :; do sleep 30; done) &
        printf '%s\n' "$!" > "$MOCK_CHILD_PID"
    fi
    if [ "${MOCK_TIMEOUT_FIRST:-0}" = "1" ] && [ "$count" = "1" ]; then
        sleep 30
    fi
    if [ "${MOCK_TOOL_TYPE:-task}" != "none" ]; then
        printf '{"type":"tool_use","sessionID":"ses_test","part":{"tool":"%s","state":{"status":"completed"}}}\n' "${MOCK_TOOL_TYPE:-task}"
    fi
    if [ "$count" -ge "${MOCK_COMPLETE_AFTER:-1}" ]; then
        printf '%s\n' '{"status":"complete"}' > process_log/pipeline_state.json
    fi
    exit 0
fi
exit 0
MOCK
chmod +x "$BIN/opencode"

export PATH="$BIN:$PATH"
export MOCK_CALLS="$TEST_ROOT/calls"
export MOCK_COUNT="$TEST_ROOT/count"
export MOCK_LIST_COUNT="$TEST_ROOT/list-count"
export MOCK_CREATED="$TEST_ROOT/created"
export MOCK_CHILD_PID="$TEST_ROOT/child-pid"
export OPENCODE_LOOP_DELAY=0
export MOCK_EXPECTED_KEY=test-only-secret

reset_project() {
    printf '%s\n' '{"status":"running"}' > "$PROJECT/process_log/pipeline_state.json"
    printf '%s\n' 'OPENCODE_API_KEY=test-only-secret' > "$PROJECT/.env"
    rm -f "$PROJECT/process_log/.opencode_session_id" "$MOCK_CALLS" "$MOCK_COUNT" "$MOCK_LIST_COUNT" "$MOCK_CREATED" "$MOCK_CHILD_PID"
}

# Interactive launch selects the canonical skill tree and does not use --auto.
reset_project
(cd "$PROJECT" && env -u OPENCODE_API_KEY ./launch.sh opencode --once)
grep -q '^external_skills=1 opencode_key_set=1 opencode_key_match=1 args=--model opencode/deepseek-v4-flash$' "$MOCK_CALLS"
! grep -q 'test-only-secret' "$MOCK_CALLS"
! grep -q -- '--auto' "$MOCK_CALLS"

# Standard quoted dotenv values may carry trailing comments.
reset_project
printf '%s\n' 'OPENCODE_API_KEY="double-quoted" # local key' > "$PROJECT/.env"
(cd "$PROJECT" && env -u OPENCODE_API_KEY MOCK_EXPECTED_KEY=double-quoted ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"
reset_project
printf '%s\n' "OPENCODE_API_KEY='single-quoted' # local key" > "$PROJECT/.env"
(cd "$PROJECT" && env -u OPENCODE_API_KEY MOCK_EXPECTED_KEY=single-quoted ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"

# A parent-shell credential wins, and shell-looking dotenv text stays literal.
reset_project
(cd "$PROJECT" && OPENCODE_API_KEY=parent-key MOCK_EXPECTED_KEY=parent-key ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"
reset_project
side_effect="$TEST_ROOT/should-not-exist"
printf 'OPENCODE_API_KEY=$(touch %s) `touch %s`\n' "$side_effect" "$side_effect" > "$PROJECT/.env"
literal_key="\$(touch $side_effect) \`touch $side_effect\`"
(cd "$PROJECT" && env -u OPENCODE_API_KEY MOCK_EXPECTED_KEY="$literal_key" ./launch.sh opencode --once)
grep -q 'opencode_key_match=1' "$MOCK_CALLS"
test ! -e "$side_effect"

# Fresh headless run records a session and stops when state becomes complete.
reset_project
(cd "$PROJECT" && ./launch.sh opencode)
grep -q '^ses_test$' "$PROJECT/process_log/.opencode_session_id"
grep -q 'args=run --model opencode/deepseek-v4-flash --format json' "$MOCK_CALLS"

# A stale or malformed cached session is discarded and replaced.
reset_project
printf '%s\n' stale > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_SESSIONS='not-json' ./launch.sh opencode)
grep -q '^ses_test$' "$PROJECT/process_log/.opencode_session_id"

# A valid cached session is resumed.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_VALID_SID=good ./launch.sh opencode)
grep -q 'args=run --session good --model opencode/deepseek-v4-flash --format json' "$MOCK_CALLS"

# A cached ID belonging to another checkout is never resumed.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_SESSIONS='[{"id":"good","directory":"/another/project"}]' ./launch.sh opencode)
! grep -q 'args=run --session good ' "$MOCK_CALLS"
grep -q 'args=run --model opencode/deepseek-v4-flash --format json' "$MOCK_CALLS"

# A wedged first turn is terminated, then the recorded session is resumed.
reset_project
started=$SECONDS
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_CHILD_FIRST=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=2 ./launch.sh opencode)
elapsed=$((SECONDS - started))
[ "$elapsed" -ge 3 ]
grep -q 'args=run --session ses_test --model opencode/deepseek-v4-flash --format json' "$MOCK_CALLS"
child_pid="$(cat "$MOCK_CHILD_PID")"
! kill -0 "$child_pid" 2>/dev/null

# If the first event was buffered, reconcile the one newly listed session.
reset_project
(cd "$PROJECT" && MOCK_TIMEOUT_FIRST=1 MOCK_NO_EVENT_FIRST=1 MOCK_LIST_CREATED=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=1 ./launch.sh opencode)
grep -q 'args=run --session ses_test --model opencode/deepseek-v4-flash --format json' "$MOCK_CALLS"

# Without a valid pre-run snapshot, a post-timeout global session must not be
# mistaken for the session created by this invocation.
reset_project
if (cd "$PROJECT" && MOCK_LIST_FAIL_FIRST=1 MOCK_TIMEOUT_FIRST=1 MOCK_NO_EVENT_FIRST=1 MOCK_LIST_CREATED=1 OPENCODE_TURN_TIMEOUT=1 OPENCODE_KILL_GRACE=0 ./launch.sh opencode); then
    echo "invalid session-list baseline was reconciled" >&2
    exit 1
fi
! grep -q 'args=run --session ses_test ' "$MOCK_CALLS"
grep -q 'timed-out first turn returned no session id' "$PROJECT/process_log/opencode-driver.log"

# Completed substantive non-task tools count as useful progress.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
(cd "$PROJECT" && MOCK_VALID_SID=good MOCK_TOOL_TYPE=websearch MOCK_COMPLETE_AFTER=6 NO_PROGRESS_CEILING=2 ./launch.sh opencode)
test "$(cat "$MOCK_COUNT")" = 6

# Empty rapid turns still trip the narrow no-progress guard.
reset_project
printf '%s\n' good > "$PROJECT/process_log/.opencode_session_id"
if (cd "$PROJECT" && MOCK_VALID_SID=good MOCK_TOOL_TYPE=none MOCK_COMPLETE_AFTER=99 NO_PROGRESS_CEILING=2 ./launch.sh opencode); then
    echo "empty-turn guard did not fire" >&2
    exit 1
fi
grep -q '2 fast turns without repository progress or completed substantive tool work' "$PROJECT/process_log/opencode-driver.log"

echo "OpenCode launcher tests passed"
