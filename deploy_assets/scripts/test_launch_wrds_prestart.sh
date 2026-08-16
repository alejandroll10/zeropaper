#!/usr/bin/env bash
# Focused regression for launch.sh's host-side empirical service decision.
set -euo pipefail

ASSET_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-wrds-launch-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

awk '/^project_services_action\(\) \{/,/^\}/' "$ASSET_ROOT/launch.sh" \
    > "$TEST_ROOT/service-action.sh"
# shellcheck source=/dev/null
source "$TEST_ROOT/service-action.sh"

awk '/^prestart_project_services\(\) \{/,/^\}/' "$ASSET_ROOT/launch.sh" \
    > "$TEST_ROOT/prestart.sh"
# shellcheck source=/dev/null
source "$TEST_ROOT/prestart.sh"

awk '/^prepare_runtime_cache_roots\(\) \{/,/^\}/' "$ASSET_ROOT/launch.sh" \
    > "$TEST_ROOT/cache-roots.sh"
# shellcheck source=/dev/null
source "$TEST_ROOT/cache-roots.sh"

ROOT="$TEST_ROOT/project"
RUNTIME=claude
mkdir -p "$ROOT/code/utils" "$ROOT/process_log"
cp "$ASSET_ROOT/templates/utils/sandbox_cache_roots.py" "$ROOT/code/utils/"
cat > "$ROOT/code/utils/start_services.sh" <<'MOCK'
#!/usr/bin/env bash
printf 'called\n' >> "${WRDS_PRESTART_CALLS:?}"
MOCK
chmod +x "$ROOT/code/utils/start_services.sh"
export WRDS_PRESTART_CALLS="$TEST_ROOT/calls"

write_manifest() {
    local mode="$1" manual="$2"
    printf '{"mode":"%s","flags":{"manual":%s}}\n' "$mode" "$manual" \
        > "$ROOT/.deploy_manifest.json"
}

expect_calls() {
    local label="$1" expected="$2" actual=0
    [ -f "$WRDS_PRESTART_CALLS" ] && actual="$(wc -l < "$WRDS_PRESTART_CALLS" | tr -d ' ')"
    if [ "$actual" != "$expected" ]; then
        echo "FAIL: $label — expected $expected calls, got $actual" >&2
        exit 1
    fi
}

printf '{"status":"running"}\n' > "$ROOT/process_log/pipeline_state.json"
write_manifest "" false
prestart_project_services
expect_calls "running autonomous deployment starts services" 1

printf '{"status":"complete"}\n' > "$ROOT/process_log/pipeline_state.json"
prestart_project_services
expect_calls "complete deployment preserves no-preflight contract" 1

printf '{"status":"halted_core_bypass"}\n' > "$ROOT/process_log/pipeline_state.json"
prestart_project_services
expect_calls "halted deployment preserves no-preflight contract" 1

rm "$ROOT/process_log/pipeline_state.json"
write_manifest report false
prestart_project_services
expect_calls "report deployment without state starts services" 2

write_manifest "" true
prestart_project_services
expect_calls "manual deployment without state starts services" 3

write_manifest "" false
prestart_project_services
expect_calls "unknown stateless deployment fails closed" 3

RUNTIME=opencode
write_manifest report false
prestart_project_services
expect_calls "OpenCode control plane remains excluded" 3

RUNTIME=gemini
prestart_project_services
expect_calls "unconfined Gemini runtime remains excluded" 3

# A stale broad-cache deployment must not redirect a newly allowed cache root
# to arbitrary host state.
mkdir -p "$TEST_ROOT/cache-home" "$TEST_ROOT/cache-target"
chmod 700 "$TEST_ROOT/cache-home" "$TEST_ROOT/cache-target"
ln -s "$TEST_ROOT/cache-target" "$TEST_ROOT/cache-home/.cache"
if (HOME="$TEST_ROOT/cache-home" RUNTIME=codex prepare_runtime_cache_roots) 2>/dev/null; then
    echo "FAIL: planted cache-root symlink was accepted" >&2
    exit 1
fi

# Cache directories commonly arrive group-writable from package installers.
# Ownership + no-symlink identity, not an unnecessarily strict mode, is the
# grant boundary; broad ~/.cache must keep working in that ordinary state.
MODE_ROOT="$TEST_ROOT/group-mode-home"
mkdir -p "$MODE_ROOT/.codex" "$MODE_ROOT/.cache"
chmod 700 "$MODE_ROOT"
chmod 775 "$MODE_ROOT/.codex" "$MODE_ROOT/.cache"
HOME="$MODE_ROOT" RUNTIME=codex prepare_runtime_cache_roots

# Codex's permission profile must preserve the broad cache while narrowing the
# released-client WRDS compatibility path back to read-only.
# shellcheck source=/dev/null
source "$ASSET_ROOT/templates/utils/codex_preflight.sh"
codex_permission_profile_args "$TEST_ROOT/profile project" true
profile_args="$(printf '%s\n' "${CODEX_PERMISSION_PROFILE_ARGS[@]}")"
grep -Fq '"~/.cache"="write"' <<<"$profile_args"
grep -Fq '"~/.cache/zeropaper/wrds"="read"' <<<"$profile_args"
grep -Fq 'permissions.zeropaper-pipeline.network.enabled=true' <<<"$profile_args"
grep -Fq 'profile project/.git' <<<"$profile_args"
if grep -Fq 'sandbox_workspace_write' <<<"$profile_args"; then
    echo "FAIL: Codex profile fell back to legacy writable_roots" >&2
    exit 1
fi

# Claude must not disable Linux's path-blind Unix-socket seccomp filter. macOS
# can grant the one WRDS query socket precisely; Linux uses the authenticated
# loopback query bridge instead.
grep -Fq '"allowUnixSockets": ["~/.local/state/zeropaper/wrds/wrds_server_23847.sock"]' \
    "$ASSET_ROOT/templates/runtime/claude/settings.json"
grep -Fq 'allowUnixSockets: [join(' \
    "$ASSET_ROOT/templates/utils/opencode_sandbox_exec.mjs"
grep -Fq '"wrds_server_23847.sock"' \
    "$ASSET_ROOT/templates/utils/opencode_sandbox_exec.mjs"
if grep -Fq 'allowAllUnixSockets' \
        "$ASSET_ROOT/templates/runtime/claude/settings.json"; then
    echo "FAIL: Claude sandbox grants every host Unix socket" >&2
    exit 1
fi
if grep -Eq 'dotenv|WRDS_PASS|PGPASSWORD' \
        "$ASSET_ROOT/extensions/empirical/utils/wrds_query_bridge.py"; then
    echo "FAIL: query-only bridge imports or names database credentials" >&2
    exit 1
fi
grep -Fq 'env -u WRDS_USER -u WRDS_PASS -u PGPASSWORD' \
    "$ASSET_ROOT/extensions/empirical/utils/start_services.sh"

# A sandbox whose AF_UNIX syscall is blocked and whose host relay died must
# halt before any daemon/startup path can spend a login.
SERVICE_ROOT="$TEST_ROOT/service-sandbox"
mkdir -p "$SERVICE_ROOT/code/utils" "$SERVICE_ROOT/.venv/bin"
cp "$ASSET_ROOT/extensions/empirical/utils/start_services.sh" \
    "$SERVICE_ROOT/code/utils/start_services.sh"
cat > "$SERVICE_ROOT/.env" <<'ENV'
WRDS_USER=test-user
WRDS_PASS=test-pass
ENV
cat > "$SERVICE_ROOT/.venv/bin/python3" <<'MOCK'
#!/usr/bin/env bash
args="$*"
case "$args" in
  *wrds_requires_bridge*) exit 0 ;;
  *wrds_bridge_ping*) exit 1 ;;
esac
printf 'unexpected:%s\n' "$args" >> "${WRDS_SANDBOX_UNEXPECTED:?}"
exit 1
MOCK
chmod +x "$SERVICE_ROOT/.venv/bin/python3"
if (cd "$SERVICE_ROOT" && WRDS_SANDBOX_UNEXPECTED="$TEST_ROOT/unexpected-service" \
        bash code/utils/start_services.sh) >"$TEST_ROOT/service-out" 2>"$TEST_ROOT/service-err"; then
    echo "FAIL: sandbox-side missing bridge was treated as healthy" >&2
    exit 1
fi
grep -Fq 'WRDS host query bridge is unavailable inside this sandbox' \
    "$TEST_ROOT/service-err"
test ! -e "$TEST_ROOT/unexpected-service"

# The loopback bridge is a Linux-only workaround; macOS uses the exact socket
# grants above and must not expose an unnecessary TCP listener.
grep -Fq 'sys.platform.startswith("linux")' \
    "$ASSET_ROOT/extensions/empirical/utils/start_services.sh"

# Both persistent WRDS processes use Python's portable session primitive;
# stock macOS has no external `setsid` utility. Prove the exact wrapper makes
# its exec target a session/process-group leader without that command.
SERVICE_SOURCE="$ASSET_ROOT/extensions/empirical/utils/start_services.sh"
test "$(grep -Fc 'os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
    "$SERVICE_SOURCE")" = 2
if grep -q 'command -v setsid' "$SERVICE_SOURCE"; then
    echo "FAIL: WRDS persistence still depends on an external setsid command" >&2
    exit 1
fi
DETACH_RECORD="$TEST_ROOT/detach-record"
python3 -c 'import os, sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
    "$(command -v python3)" -c \
    'import os,sys; open(sys.argv[1], "w").write(f"{os.getpid()} {os.getpgrp()}\n")' \
    "$DETACH_RECORD" &
detach_wrapper_pid=$!
wait "$detach_wrapper_pid"
read -r detached_pid detached_pgid < "$DETACH_RECORD"
if [ "$detached_pid" != "$detached_pgid" ]; then
    echo "FAIL: portable WRDS detachment wrapper did not create a new session" >&2
    exit 1
fi

# The OpenCode supervisor cannot touch credentials or service code before the
# trusted control plane confirms that its SRT PID is host-visible. Once the
# one-shot gate opens it starts exactly once, publishes readiness, and remains
# alive until explicitly terminated.
SRT_SERVICE_ROOT="$TEST_ROOT/srt-service"
mkdir -p "$SRT_SERVICE_ROOT/code/utils" "$SRT_SERVICE_ROOT/process_log/.opencode-control"
mkdir -p "$SRT_SERVICE_ROOT/.opencode"
cp "$ASSET_ROOT/templates/utils/wrds_srt_service.py" \
    "$SRT_SERVICE_ROOT/.opencode/wrds_srt_service.py"
printf 'WRDS_USER=test-user\nWRDS_PASS=test-pass\n' > "$SRT_SERVICE_ROOT/.env"
cat > "$SRT_SERVICE_ROOT/code/utils/start_services.sh" <<'MOCK'
#!/usr/bin/env bash
printf 'called\n' >> "${WRDS_SRT_START_CALLS:?}"
MOCK
cat > "$SRT_SERVICE_ROOT/code/utils/wrds_client.py" <<'PY'
def wrds_ping(): return True
def wrds_bridge_ping(): return True
PY
chmod +x "$SRT_SERVICE_ROOT/code/utils/start_services.sh"
SRT_APPROVAL="$SRT_SERVICE_ROOT/process_log/.opencode-control/wrds_service_approval"
: > "$SRT_APPROVAL"
chmod 600 "$SRT_APPROVAL"
(cd "$SRT_SERVICE_ROOT" && SANDBOX_RUNTIME=1 WRDS_SRT_START_CALLS="$TEST_ROOT/srt-start-calls" \
    python3 -I .opencode/wrds_srt_service.py zeropaper-wrds-srt-service-v6 \
        "$SRT_APPROVAL") >"$TEST_ROOT/srt-service-log" 2>&1 &
srt_service_pid=$!
for _attempt in {1..200}; do
    grep -q '^WRDS_SRT_IDENTITY ' "$TEST_ROOT/srt-service-log" 2>/dev/null && break
    kill -0 "$srt_service_pid" 2>/dev/null || break
    sleep 0.02
done
grep -q '^WRDS_SRT_IDENTITY ' "$TEST_ROOT/srt-service-log"
test ! -e "$TEST_ROOT/srt-start-calls"
printf 'approved\n' > "$SRT_APPROVAL"
for _attempt in {1..200}; do
    grep -q '^WRDS_SRT_SERVICE_READY$' "$TEST_ROOT/srt-service-log" 2>/dev/null && break
    kill -0 "$srt_service_pid" 2>/dev/null || break
    sleep 0.02
done
grep -q '^WRDS_SRT_SERVICE_READY$' "$TEST_ROOT/srt-service-log"
test "$(wc -l < "$TEST_ROOT/srt-start-calls" | tr -d ' ')" = 1
kill -TERM "$srt_service_pid"
wait "$srt_service_pid"

# The stage doctrine binds its halt to the second authoritative service probe,
# not the initial observation or auth-diagnosis proxy.
STAGE3A="$ASSET_ROOT/extensions/empirical/docs/stage_3a_empirical.md"
grep -Fq 'immediately run the exact `wrds_ping()` command above one final time' "$STAGE3A"
grep -Fq 'Only if the final ping also returns False' "$STAGE3A"
grep -Fq 'PYTHONPATH=code .venv/bin/python3' "$STAGE3A"

# OpenCode's first-start path is long-lived, service-profiled, identity-bound,
# and executed through SRT; the unsandboxed control plane never invokes the
# project venv directly.
grep -Fq 'ZEROPAPER_OPENCODE_WRDS_SERVICE=1' "$ASSET_ROOT/launch.sh"
grep -Fq 'oc_wrds_service_approve_pid_namespace' "$ASSET_ROOT/launch.sh"
grep -Fq 'zeropaper-wrds-srt-service-v6' "$ASSET_ROOT/launch.sh"
grep -Fq '"$OC_CONTROL_PYTHON" -I .opencode/wrds_srt_service.py' \
    "$ASSET_ROOT/launch.sh"
if grep -Fq '"$ROOT/.venv/bin/python3" -I code/utils/wrds_srt_service.py' \
    "$ASSET_ROOT/launch.sh"; then
    echo "FAIL: privileged WRDS profile still invokes the model-writable venv" >&2
    exit 1
fi
grep -Fq 'allowAllUnixSockets: true' \
    "$ASSET_ROOT/templates/utils/opencode_sandbox_exec.mjs"

FAKE_CODEX_BIN="$TEST_ROOT/fake-codex-bin"
mkdir -p "$FAKE_CODEX_BIN"
cat > "$FAKE_CODEX_BIN/codex" <<'FAKE'
#!/usr/bin/env bash
printf 'codex-cli %s\n' "${FAKE_CODEX_VERSION:?}"
FAKE
chmod +x "$FAKE_CODEX_BIN/codex"
if PATH="$FAKE_CODEX_BIN:$PATH" FAKE_CODEX_VERSION=0.146.9 \
        codex_permission_profile_preflight 2>/dev/null; then
    echo "FAIL: pre-permission-profile Codex version was accepted" >&2
    exit 1
fi
PATH="$FAKE_CODEX_BIN:$PATH" FAKE_CODEX_VERSION=0.147.0 \
    codex_permission_profile_preflight

# The shipped launcher supports stock macOS: SIGSTOP is not Linux's numeric 19
# there, and `seq` is not a declared prerequisite.
grep -q 'signal\.SIGSTOP' "$ASSET_ROOT/launch.sh"
if grep -Eq 'os\.kill\(os\.getpid\(\),[[:space:]]*[0-9]+\)|(^|[^[:alnum:]_])seq([^[:alnum:]_]|$)' \
        "$ASSET_ROOT/launch.sh"; then
    echo "FAIL: launcher retained a Linux-only signal number or undeclared seq dependency" >&2
    exit 1
fi

# Runtime validation precedes service startup, so a typo never spends Duo.
INVALID_ROOT="$TEST_ROOT/invalid-runtime"
mkdir -p "$INVALID_ROOT/code/utils" "$INVALID_ROOT/process_log"
cp "$ASSET_ROOT/launch.sh" "$INVALID_ROOT/launch.sh"
cp "$ROOT/code/utils/start_services.sh" "$INVALID_ROOT/code/utils/start_services.sh"
printf '{"status":"running"}\n' > "$INVALID_ROOT/process_log/pipeline_state.json"
if (cd "$INVALID_ROOT" && WRDS_PRESTART_CALLS="$TEST_ROOT/invalid-calls" \
        bash ./launch.sh nonsense) >/dev/null 2>&1; then
    echo "FAIL: invalid runtime was accepted" >&2
    exit 1
fi
test ! -e "$TEST_ROOT/invalid-calls"

# Terminating the visible launcher must terminate a non-OpenCode runtime's
# complete child tree before releasing the project lock. The runtime wrapper is
# asynchronous internally, so this also catches inherited ignored-INT/QUIT
# dispositions and direct-child-only TERM forwarding.
SIGNAL_ROOT="$TEST_ROOT/signal-project"
SIGNAL_HOME="$TEST_ROOT/signal-home"
SIGNAL_BIN="$TEST_ROOT/signal-bin"
mkdir -p "$SIGNAL_ROOT/code/utils" "$SIGNAL_ROOT/process_log" \
    "$SIGNAL_HOME/.cache" "$SIGNAL_HOME/.codex" "$SIGNAL_BIN"
cp "$ASSET_ROOT/launch.sh" "$SIGNAL_ROOT/launch.sh"
cp "$ASSET_ROOT/templates/utils/sandbox_cache_roots.py" \
    "$SIGNAL_ROOT/code/utils/sandbox_cache_roots.py"
cat > "$SIGNAL_BIN/claude" <<'MOCK'
#!/usr/bin/env bash
if [ -n "${LAUNCH_EXIT_CHILD_PID:-}" ]; then
    trap '' HUP INT QUIT TERM
    sleep 30 &
    printf '%s\n' "$!" > "$LAUNCH_EXIT_CHILD_PID"
    runtime_shell="$PPID"
    supervisor="$(ps -o ppid= -p "$runtime_shell" | tr -d ' ')"
    # Freeze the supervisor before this CLI and its runtime-shell leader exit,
    # creating the exact leader-gone/stubborn-member guardian window.
    kill -STOP "$supervisor"
    exit 0
fi
on_term() {
    trap '' TERM INT
    sleep 30 &
    printf '%s\n' "$!" > "${LAUNCH_ESCAPED_PID:?}"
    # Exit immediately without Bash waiting for its new background child.
    kill -KILL "$$"
}
trap on_term TERM INT
sleep 30 &
printf '%s\n' "$!" > "${LAUNCH_DESCENDANT_PID:?}"
wait "$!"
MOCK
chmod +x "$SIGNAL_BIN/claude"

# An inherited/forged readiness variable must never truncate an existing owned
# file. Only O_EXCL creation of a previously absent leaf is accepted.
printf 'preserve-me\n' > "$TEST_ROOT/readiness-sentinel"
if ZEROPAPER_LAUNCH_READY_FILE="$TEST_ROOT/readiness-sentinel" \
        HOME="$SIGNAL_HOME" PATH="$SIGNAL_BIN:$PATH" \
        bash "$SIGNAL_ROOT/launch.sh" claude \
        >"$TEST_ROOT/readiness-output" 2>&1; then
    echo "FAIL: existing file was accepted as nested-launch readiness" >&2
    exit 1
fi
test "$(cat "$TEST_ROOT/readiness-sentinel")" = "preserve-me"

# The internal reentry marker and fd8 are not themselves trusted. Even a
# forged same-user invocation must start its own SH-lock keeper and therefore
# fail while an updater holds LOCK_EX on the project root.
read -r forged_lock_ready < <(/usr/bin/python3 -I - "$SIGNAL_ROOT" <<'PY'
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
print("locked", flush=True)
while True:
    time.sleep(1)
PY
)
forged_lock_holder=$!
[ "$forged_lock_ready" = "locked" ]
if ZEROPAPER_LAUNCH_INTERNAL=1 ZEROPAPER_LAUNCH_SUPERVISOR_PID="$$" HOME="$SIGNAL_HOME" \
        PATH="$SIGNAL_BIN:$PATH" bash "$SIGNAL_ROOT/launch.sh" claude \
        8<"$SIGNAL_ROOT" >"$TEST_ROOT/forged-output" 2>&1; then
    echo "FAIL: forged internal launch bypassed updater LOCK_EX" >&2
    exit 1
fi
kill "$forged_lock_holder" 2>/dev/null || true
wait "$forged_lock_holder" 2>/dev/null || true

LAUNCH_DESCENDANT_PID="$TEST_ROOT/launch-descendant-pid" \
LAUNCH_ESCAPED_PID="$TEST_ROOT/launch-escaped-pid" \
LAUNCH_SIGNAL_GRACE=1 \
HOME="$SIGNAL_HOME" PATH="$SIGNAL_BIN:$PATH" \
    bash "$SIGNAL_ROOT/launch.sh" claude >"$TEST_ROOT/signal-output" 2>&1 &
signal_launcher=$!
for _ in $(seq 1 100); do
    [ -s "$TEST_ROOT/launch-descendant-pid" ] && break
    sleep 0.02
done
[ -s "$TEST_ROOT/launch-descendant-pid" ] || {
    echo "FAIL: signal canary runtime never started" >&2
    exit 1
}
signal_descendant="$(cat "$TEST_ROOT/launch-descendant-pid")"
kill -TERM "$signal_launcher"
signal_rc=0
wait "$signal_launcher" || signal_rc=$?
[ "$signal_rc" = 143 ] || {
    echo "FAIL: terminated launcher returned $signal_rc instead of 143" >&2
    exit 1
}
if kill -0 "$signal_descendant" 2>/dev/null; then
    echo "FAIL: terminating launch.sh orphaned its runtime descendant" >&2
    exit 1
fi
if [ -s "$TEST_ROOT/launch-escaped-pid" ]; then
    signal_escaped="$(cat "$TEST_ROOT/launch-escaped-pid")"
    if kill -0 "$signal_escaped" 2>/dev/null; then
        echo "FAIL: shutdown-spawned runtime descendant escaped the process group" >&2
        exit 1
    fi
fi

# The guardian binds a persistent group member, not only the leader. If the
# runtime leader exits with a stubborn child while the supervisor is stopped,
# SIGKILL of the supervisor must still kill that original group and release SH.
rm -f "$TEST_ROOT/leader-exit-child-pid"
LAUNCH_EXIT_CHILD_PID="$TEST_ROOT/leader-exit-child-pid" \
HOME="$SIGNAL_HOME" PATH="$SIGNAL_BIN:$PATH" \
    bash "$SIGNAL_ROOT/launch.sh" claude >"$TEST_ROOT/leader-exit-output" 2>&1 &
leader_exit_launcher=$!
for _ in $(seq 1 100); do
    [ -s "$TEST_ROOT/leader-exit-child-pid" ] && break
    sleep 0.02
done
[ -s "$TEST_ROOT/leader-exit-child-pid" ] || {
    echo "FAIL: leader-exit guardian canary never started" >&2
    exit 1
}
leader_exit_child="$(cat "$TEST_ROOT/leader-exit-child-pid")"
kill -KILL "$leader_exit_launcher"
wait "$leader_exit_launcher" 2>/dev/null || true
for _ in $(seq 1 100); do
    kill -0 "$leader_exit_child" 2>/dev/null || break
    sleep 0.02
done
if kill -0 "$leader_exit_child" 2>/dev/null; then
    echo "FAIL: guardian missed a stubborn member after runtime leader exit" >&2
    exit 1
fi
if ! /usr/bin/python3 -I - "$SIGNAL_ROOT" <<'PY'
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
deadline = time.monotonic() + 5
while True:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        break
    except BlockingIOError:
        if time.monotonic() >= deadline:
            raise
        time.sleep(0.05)
PY
then
    echo "FAIL: leader-exit guardian path retained the project SH lock" >&2
    exit 1
fi

# Model terminal Ctrl-C: after tcsetpgrp, INT is delivered to the runtime PGID
# rather than the lock-owning parent. The parent's post-wait drain must still
# reap the handler-spawned, INT-ignoring member before it releases the lock.
rm -f "$TEST_ROOT/launch-descendant-pid" "$TEST_ROOT/launch-escaped-pid"
LAUNCH_DESCENDANT_PID="$TEST_ROOT/launch-descendant-pid" \
LAUNCH_ESCAPED_PID="$TEST_ROOT/launch-escaped-pid" \
LAUNCH_SIGNAL_GRACE=1 \
HOME="$SIGNAL_HOME" PATH="$SIGNAL_BIN:$PATH" \
    bash "$SIGNAL_ROOT/launch.sh" claude >"$TEST_ROOT/int-output" 2>&1 &
int_launcher=$!
for _ in $(seq 1 100); do
    [ -s "$TEST_ROOT/launch-descendant-pid" ] && break
    sleep 0.02
done
int_runtime="$(/bin/ps -Ao pid=,ppid= | awk -v p="$int_launcher" '$2 == p { print $1; exit }')"
[ -n "$int_runtime" ] || { echo "FAIL: could not find runtime process group" >&2; exit 1; }
kill -INT -- "-$int_runtime"
wait "$int_launcher" 2>/dev/null || true
int_descendant="$(cat "$TEST_ROOT/launch-descendant-pid")"
if kill -0 "$int_descendant" 2>/dev/null; then
    echo "FAIL: terminal-style Ctrl-C orphaned the original runtime child" >&2
    exit 1
fi
if [ -s "$TEST_ROOT/launch-escaped-pid" ]; then
    int_escaped="$(cat "$TEST_ROOT/launch-escaped-pid")"
    if kill -0 "$int_escaped" 2>/dev/null; then
        echo "FAIL: terminal-style Ctrl-C orphaned a shutdown-spawned child" >&2
        exit 1
    fi
fi

# Real controlling-terminal job control: Ctrl-Z must return to the invoking
# shell, and `fg` must re-transfer the TTY and resume the isolated runtime.
# This uses a PTY rather than approximating terminal delivery with kill(1).
rm -f "$TEST_ROOT/launch-descendant-pid" "$TEST_ROOT/launch-escaped-pid"
/usr/bin/python3 -I - "$SIGNAL_ROOT" "$SIGNAL_HOME" "$SIGNAL_BIN" \
    "$TEST_ROOT/launch-descendant-pid" "$TEST_ROOT/launch-escaped-pid" <<'PY'
import fcntl, os, pty, select, shlex, signal, sys, time

root, home, bindir, descendant, escaped = sys.argv[1:]
prompt = b"ZT_PROMPT> "
pid, fd = pty.fork()
if pid == 0:
    env = os.environ.copy()
    env.update({
        "HOME": home,
        "PATH": bindir + ":" + env.get("PATH", ""),
        "PS1": prompt.decode(),
        "LAUNCH_DESCENDANT_PID": descendant,
        "LAUNCH_ESCAPED_PID": escaped,
        "LAUNCH_SIGNAL_GRACE": "1",
    })
    os.execve("/bin/bash", ["bash", "--noprofile", "--norc", "-i"], env)

def read_until(needle, timeout):
    data = b""
    deadline = time.monotonic() + timeout
    while needle not in data and time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.1)
        if not ready:
            continue
        try:
            data += os.read(fd, 4096)
        except OSError:
            break
    if needle not in data:
        raise RuntimeError(f"PTY timeout waiting for {needle!r}: {data[-500:]!r}")
    return data

try:
    read_until(prompt, 5)
    command = f"cd {shlex.quote(root)} && bash ./launch.sh claude\n"
    os.write(fd, command.encode())
    deadline = time.monotonic() + 5
    while not os.path.exists(descendant) and time.monotonic() < deadline:
        time.sleep(0.02)
    if not os.path.exists(descendant):
        raise RuntimeError("PTY runtime did not start")
    os.write(fd, b"\x1a")  # terminal Ctrl-Z
    read_until(prompt, 5)
    os.write(fd, b"bg\n")
    read_until(prompt, 5)
    time.sleep(0.25)
    os.write(fd, b"jobs\n")
    jobs_output = read_until(prompt, 5)
    if b"Stopped" not in jobs_output:
        raise RuntimeError(f"background resume stole TTY or did not restop: {jobs_output!r}")
    os.write(fd, b"fg\n")
    time.sleep(0.25)
    os.write(fd, b"\x03")  # terminal Ctrl-C after resume
    read_until(prompt, 8)

    # A shell-side SIGKILL of the suspended launcher cannot run its traps. The
    # detached pipe guardian must kill the stopped runtime and release SH flock.
    for path in (descendant, escaped):
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
    os.write(fd, command.encode())
    deadline = time.monotonic() + 5
    while not os.path.exists(descendant) and time.monotonic() < deadline:
        time.sleep(0.02)
    if not os.path.exists(descendant):
        raise RuntimeError("second PTY runtime did not start")
    os.write(fd, b"\x1a")
    read_until(prompt, 5)
    os.write(fd, b"kill -KILL %+\n")
    read_until(prompt, 5)
    lock_fd = os.open(root, os.O_RDONLY)
    deadline = time.monotonic() + 5
    while True:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise RuntimeError("SIGKILLed suspended launcher retained SH flock")
            time.sleep(0.05)
    os.close(lock_fd)
    os.write(fd, b"exit\n")
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        done, _ = os.waitpid(pid, os.WNOHANG)
        if done == pid:
            break
        time.sleep(0.05)
    else:
        raise RuntimeError("interactive shell did not exit")
finally:
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
PY
pty_descendant="$(cat "$TEST_ROOT/launch-descendant-pid")"
if kill -0 "$pty_descendant" 2>/dev/null; then
    echo "FAIL: Ctrl-Z/fg/Ctrl-C PTY flow orphaned the runtime child" >&2
    exit 1
fi
if [ -s "$TEST_ROOT/launch-escaped-pid" ]; then
    pty_escaped="$(cat "$TEST_ROOT/launch-escaped-pid")"
    if kill -0 "$pty_escaped" 2>/dev/null; then
        echo "FAIL: Ctrl-Z/fg/Ctrl-C PTY flow orphaned a shutdown child" >&2
        exit 1
    fi
fi

# --tmux must retain the original shared lock until the nested launcher has
# acquired its own. A delayed fake tmux creates the historical handoff gap;
# an exclusive update contender must remain blocked throughout it.
TMUX_ROOT="$TEST_ROOT/tmux-project"
TMUX_HOME="$TEST_ROOT/tmux-home"
TMUX_BIN="$TEST_ROOT/tmux-bin"
mkdir -p "$TMUX_ROOT/code/utils" "$TMUX_ROOT/process_log" \
    "$TMUX_HOME/.cache" "$TMUX_HOME/.codex" "$TMUX_BIN"
cp "$ASSET_ROOT/launch.sh" "$TMUX_ROOT/launch.sh"
cp "$ASSET_ROOT/templates/utils/sandbox_cache_roots.py" \
    "$TMUX_ROOT/code/utils/sandbox_cache_roots.py"
cat > "$TMUX_BIN/claude" <<'MOCK'
#!/usr/bin/env bash
sleep 2
MOCK
cat > "$TMUX_BIN/tmux" <<'MOCK'
#!/usr/bin/env bash
command="${@: -1}"
printf 'called\n' > "${FAKE_TMUX_CALLED:?}"
( sleep 0.5; /bin/bash -c "$command" ) &
MOCK
chmod +x "$TMUX_BIN/claude" "$TMUX_BIN/tmux"
FAKE_TMUX_CALLED="$TEST_ROOT/fake-tmux-called" HOME="$TMUX_HOME" \
PATH="$TMUX_BIN:$PATH" TMUX= \
    bash "$TMUX_ROOT/launch.sh" claude --tmux >"$TEST_ROOT/tmux-output" 2>&1 &
tmux_launcher=$!
for _ in $(seq 1 100); do
    [ -s "$TEST_ROOT/fake-tmux-called" ] && break
    sleep 0.01
done
if /usr/bin/python3 -I - "$TMUX_ROOT" <<'PY'
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(1)
PY
then
    echo "FAIL: update lock acquired inside tmux launcher handoff" >&2
    exit 1
fi
wait "$tmux_launcher"
grep -q "Launched in tmux session" "$TEST_ROOT/tmux-output"

# Stateless Codex uses the interactive form. The incompatible driver command
# must fail before its otherwise-valid report manifest can prestart WRDS.
STATELESS_ROOT="$TEST_ROOT/stateless-codex"
mkdir -p "$STATELESS_ROOT/code/utils" "$STATELESS_ROOT/process_log"
cp "$ASSET_ROOT/launch.sh" "$STATELESS_ROOT/launch.sh"
cp "$ROOT/code/utils/start_services.sh" \
    "$STATELESS_ROOT/code/utils/start_services.sh"
printf '{"mode":"report","flags":{"manual":false}}\n' \
    > "$STATELESS_ROOT/.deploy_manifest.json"
if (cd "$STATELESS_ROOT" && WRDS_PRESTART_CALLS="$TEST_ROOT/stateless-calls" \
        bash ./launch.sh codex) >"$TEST_ROOT/stateless-error" 2>&1; then
    echo "FAIL: stateless Codex driver invocation was accepted" >&2
    exit 1
fi
grep -q "report/manual Codex sessions require: ./launch.sh codex --once" \
    "$TEST_ROOT/stateless-error"
test ! -e "$TEST_ROOT/stateless-calls"

# OpenCode's separate policy materializer rejects the same planted-cache-link
# upgrade state before it reaches the SRT executable lookup.
OC_ROOT="$TEST_ROOT/opencode-symlink"
mkdir -p "$OC_ROOT/project/.opencode" "$OC_ROOT/home" "$OC_ROOT/cache-target"
cp "$ASSET_ROOT/templates/runtime/opencode/sandbox.json" \
    "$OC_ROOT/project/.opencode/sandbox.json"
cp "$ASSET_ROOT/templates/utils/opencode_sandbox_exec.sh" \
    "$OC_ROOT/project/.opencode/opencode_sandbox_exec.sh"
cp "$ASSET_ROOT/templates/utils/opencode_sandbox_exec.mjs" \
    "$OC_ROOT/project/.opencode/opencode_sandbox_exec.mjs"
ln -s "$OC_ROOT/cache-target" "$OC_ROOT/home/.cache"
if (cd "$OC_ROOT/project" && HOME="$OC_ROOT/home" \
        bash .opencode/opencode_sandbox_exec.sh .opencode/sandbox.json true) \
        >"$OC_ROOT/error" 2>&1; then
    echo "FAIL: OpenCode accepted a symlinked cache ancestor" >&2
    exit 1
fi
grep -q "unsafe OpenCode sandbox writable root" "$OC_ROOT/error"

echo "PASS: WRDS prestart modes, early runtime validation, and cache-root safety"
