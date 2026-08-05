#!/usr/bin/env bash
# Regression tests for launch.sh's wait_for_workers() — the codex driver's
# post-turn wait on detached workers.
#
# Guards issue #223: the wait used to decide a worker was finished by looking
# at its output file (non-empty ⇒ done), and that test ran BEFORE the
# wrapper-pid liveness probe. Workers that stream their report incrementally
# (the novelty-checker writes each search as it lands) therefore looked
# finished from their first bytes onward, so the driver stopped waiting and
# re-prompted immediately. The orchestrator — correctly obeying
# poll-don't-relaunch on a live sentinel — spent each resumed turn polling a
# partial report without committing, and five such ~15s turns tripped the
# fast-cycle cost guard. Two long runs died that way with a healthy worker.
#
# The function is sourced out of the real launch.sh rather than copied, so
# these tests fail if the shipped implementation drifts.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-workers-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"; [ -n "${LIVE_PID:-}" ] && kill "$LIVE_PID" 2>/dev/null; true' EXIT

awk '/^wait_for_workers\(\) \{/,/^\}/' "$ROOT/launch.sh" > "$TEST_ROOT/wait_for_workers.sh"
[ -s "$TEST_ROOT/wait_for_workers.sh" ] || { echo "FAIL: could not extract wait_for_workers() from launch.sh" >&2; exit 1; }
grep -q '^}' "$TEST_ROOT/wait_for_workers.sh" || { echo "FAIL: extracted function is truncated" >&2; exit 1; }

LOG="$TEST_ROOT/driver.log"; : > "$LOG"
OUTCOME="$TEST_ROOT/probe_outcome"
# shellcheck source=/dev/null
source "$TEST_ROOT/wait_for_workers.sh"

pass=0; fail=0
check() {  # name expected actual
    if [ "$2" = "$3" ]; then
        printf '  PASS  %s\n' "$1"; pass=$((pass + 1))
    else
        printf '  FAIL  %s — expected %s, got %s\n' "$1" "$2" "$3"; fail=$((fail + 1))
    fi
}
fresh_project() {
    ROOT="$TEST_ROOT/project"
    rm -rf "$ROOT"
    mkdir -p "$ROOT/process_log/agent_runs" "$ROOT/output"
}
exists() { [ -e "$1" ] && echo yes || echo no; }

# Does the wait return promptly, or does it block on a pending worker? Run it
# in a subshell and watch. "blocked" means the driver would correctly refrain
# from re-prompting.
#
# The subshell also writes "WAITED WAIT_CAPPED" to $OUTCOME: those globals are
# what the driver's fast-cycle guard does its arithmetic on, and they cannot be
# read back through a variable — probe() is itself called inside $( ), which
# forks. Read the FILE after a probe (see probe_outcome below), never a global.
probe() {
    local p i=0 limit="${PROBE_LIMIT:-12}" outcome="$OUTCOME"
    rm -f "$outcome"
    WORKER_WAIT_MAX="${PROBE_CAP:-25}"
    ( wait_for_workers >/dev/null 2>&1; printf '%s %s\n' "${WAITED:-?}" "${WAIT_CAPPED:-?}" > "$outcome" ) & p=$!
    while [ "$i" -lt "$limit" ]; do
        if ! kill -0 "$p" 2>/dev/null; then
            wait "$p" 2>/dev/null || true
            echo returned; return 0
        fi
        sleep 1; i=$((i + 1))
    done
    kill "$p" 2>/dev/null || true
    wait "$p" 2>/dev/null || true
    echo blocked
}
probe_outcome() {  # $1 = waited|capped — reads what the last probe recorded
    local w="" c=""
    read -r w c < "$OUTCOME" 2>/dev/null || { echo "?"; return 0; }
    case "$1" in
        waited) echo "${w:-?}" ;;
        capped) echo "${c:-?}" ;;
    esac
}
waited_at_least() {  # $1 = seconds — echoes yes/no for the recorded WAITED
    local w; w="$(probe_outcome waited)"
    case "$w" in
        ''|*[!0-9]*) echo no ;;
        *) [ "$w" -ge "$1" ] && echo yes || echo no ;;
    esac
}
dead_pid() {  # a pid that has certainly exited
    local p
    sleep 0.1 & p=$!
    wait "$p" 2>/dev/null || true
    echo "$p"
}

echo "wait_for_workers() — detached-worker wait"

echo "1. live wrapper whose report is still streaming (issue #223)"
fresh_project
sleep 600 & LIVE_PID=$!
disown %% 2>/dev/null || true
printf 'started=2026-08-04T05:25:44Z pid=%s output=output/novelty_check_1.md\nwrapper_pid=%s wrapper_lstart=\n' \
    "$LIVE_PID" "$LIVE_PID" > "$ROOT/process_log/agent_runs/.novelty-checker.running"
echo '## Search 1 of 7 …' > "$ROOT/output/novelty_check_1.md"   # non-empty but INCOMPLETE
check "waits for a live worker despite non-empty output" blocked "$(probe)"
check "leaves a live worker's sentinel alone" yes "$(exists "$ROOT/process_log/agent_runs/.novelty-checker.running")"
kill "$LIVE_PID" 2>/dev/null || true; LIVE_PID=""

echo "2. wrapper exited after writing its report (sentinel outlived it)"
fresh_project
DEAD="$(dead_pid)"
printf 'started=x pid=%s output=output/novelty_check_1.md\nwrapper_pid=%s wrapper_lstart=\n' \
    "$DEAD" "$DEAD" > "$ROOT/process_log/agent_runs/.novelty-checker.running"
echo 'Verdict: INCREMENTAL' > "$ROOT/output/novelty_check_1.md"
check "returns once the wrapper is gone" returned "$(probe)"
# Must be cleared: a sentinel outliving its wrapper also parks the ORCHESTRATOR,
# whose prompt reads a live sentinel as poll-don't-relaunch — it would neither
# route the finished report nor relaunch.
check "clears the stale sentinel so the result can be routed" no \
    "$(exists "$ROOT/process_log/agent_runs/.novelty-checker.running")"

echo "3. wrapper killed before writing anything"
fresh_project
DEAD="$(dead_pid)"
printf 'started=x pid=%s output=output/math_audit_1.md\nwrapper_pid=%s wrapper_lstart=\n' \
    "$DEAD" "$DEAD" > "$ROOT/process_log/agent_runs/.math-auditor.running"
check "returns on an orphaned sentinel" returned "$(probe)"
check "clears the orphan so the worker can be relaunched" no \
    "$(exists "$ROOT/process_log/agent_runs/.math-auditor.running")"

echo "4. old-format sentinel (no wrapper_pid), report still being written"
fresh_project
printf 'started=x pid=999999 output=output/novelty_check_1.md\n' \
    > "$ROOT/process_log/agent_runs/.novelty-checker.running"
echo '## Search 1 of 7 …' > "$ROOT/output/novelty_check_1.md"
check "mtime says still streaming — waits" blocked "$(WORKER_STALE_MTIME=600 probe)"

echo "5. old-format sentinel, report finished and idle"
fresh_project
printf 'started=x pid=999999 output=output/novelty_check_1.md\n' \
    > "$ROOT/process_log/agent_runs/.novelty-checker.running"
echo 'Verdict: KNOWN' > "$ROOT/output/novelty_check_1.md"
touch -t 202001010000 "$ROOT/output/novelty_check_1.md"
check "mtime says idle — treats as finished" returned "$(WORKER_STALE_MTIME=600 probe)"

echo "6. no workers in flight"
fresh_project
check "returns immediately on an empty agent_runs" returned "$(probe)"

echo "7. sentinel removed mid-wait (the wrapper finishing normally)"
fresh_project
sleep 600 & LIVE_PID=$!
disown %% 2>/dev/null || true
printf 'started=x pid=%s output=output/late.md\nwrapper_pid=%s wrapper_lstart=\n' \
    "$LIVE_PID" "$LIVE_PID" > "$ROOT/process_log/agent_runs/.late.running"
( sleep 3; rm -f "$ROOT/process_log/agent_runs/.late.running" ) &
check "returns when the wrapper clears its own sentinel" returned "$(probe)"
kill "$LIVE_PID" 2>/dev/null || true; LIVE_PID=""

echo "8. pid reuse — the recorded wrapper pid is alive but is a DIFFERENT process"
fresh_project
sleep 600 & LIVE_PID=$!
disown %% 2>/dev/null || true
if [ -n "$(ps -o lstart= -p "$LIVE_PID" 2>/dev/null || true)" ]; then
    # A start time that cannot match the running process means the pid was
    # recycled: the real worker is gone and its sentinel must not park us.
    printf 'started=x pid=%s output=output/report.md\nwrapper_pid=%s wrapper_lstart=Thu Jan  1 00:00:00 1970\n' \
        "$LIVE_PID" "$LIVE_PID" > "$ROOT/process_log/agent_runs/.reused.running"
    echo 'partial' > "$ROOT/output/report.md"
    check "treats a mismatched start time as a recycled pid" returned "$(probe)"
    check "clears the recycled-pid sentinel" no "$(exists "$ROOT/process_log/agent_runs/.reused.running")"
else
    # ps returns nothing without sysmond (e.g. inside a codex sandbox) — the
    # documented reason wrapper_lstart is often empty. The guard is inert
    # there by design, so assert that rather than skipping silently.
    printf 'started=x pid=%s output=output/report.md\nwrapper_pid=%s wrapper_lstart=Thu Jan  1 00:00:00 1970\n' \
        "$LIVE_PID" "$LIVE_PID" > "$ROOT/process_log/agent_runs/.reused.running"
    echo 'partial' > "$ROOT/output/report.md"
    check "ps unavailable: falls back to kill -0 and keeps waiting" blocked "$(probe)"
fi
kill "$LIVE_PID" 2>/dev/null || true; LIVE_PID=""

echo "9. wedged worker — the wait cap must fire and report WAIT_CAPPED"
fresh_project
sleep 600 & LIVE_PID=$!
disown %% 2>/dev/null || true
printf 'started=x pid=%s output=output/wedged.md\nwrapper_pid=%s wrapper_lstart=\n' \
    "$LIVE_PID" "$LIVE_PID" > "$ROOT/process_log/agent_runs/.wedged.running"
# The cap is what stops a hung worker from parking the driver forever.
check "gives up at WORKER_WAIT_MAX" returned "$(PROBE_CAP=1 probe)"
# WAIT_CAPPED=1 is load-bearing: the driver subtracts a capped wait from the
# cycle duration so a hung worker feeds the stuck-guard instead of resetting
# it forever. A wait credited as work would make the guard unreachable.
check "reports the cap through WAIT_CAPPED" 1 "$(probe_outcome capped)"
check "still reports the wall-clock wait" yes "$(waited_at_least 1)"
kill "$LIVE_PID" 2>/dev/null || true; LIVE_PID=""

echo "10. WORKER_STALE_MTIME actually moves the threshold"
fresh_project
printf 'started=x pid=999999 output=output/report.md\n' \
    > "$ROOT/process_log/agent_runs/.old.running"
echo 'written a while ago' > "$ROOT/output/report.md"
touch -t "$(date -v-1H +%Y%m%d%H%M 2>/dev/null || date -d '1 hour ago' +%Y%m%d%H%M)" "$ROOT/output/report.md"
# Same fixture, both sides of the threshold — otherwise these tests only
# re-confirm the built-in default rather than the override taking effect.
check "1h-old output is stale at a 60s threshold" returned "$(WORKER_STALE_MTIME=60 probe)"
check "1h-old output is fresh at a 24h threshold" blocked "$(WORKER_STALE_MTIME=86400 probe)"

echo "11. a broken stat must not kill the driver"
fresh_project
mkdir -p "$TEST_ROOT/badbin"
# GNU `stat -f` is filesystem mode with a different format-sequence set; an
# unknown sequence can echo back literally. "%m" reaching $(( )) would be a
# fatal arithmetic error, killing a driver that should merely keep waiting.
printf '#!/bin/sh\necho "%%m"\n' > "$TEST_ROOT/badbin/stat"
chmod +x "$TEST_ROOT/badbin/stat"
printf 'started=x pid=999999 output=output/report.md\n' \
    > "$ROOT/process_log/agent_runs/.old.running"
echo 'streaming' > "$ROOT/output/report.md"
check "non-numeric stat output is rejected, wait continues" blocked \
    "$(PATH="$TEST_ROOT/badbin:$PATH" probe)"

echo
echo "pass=$pass fail=$fail"
[ "$fail" = "0" ]
