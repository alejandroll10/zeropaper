#!/usr/bin/env bash
# Mocked end-to-end OpenCode WRDS first-start/reuse lifecycle.
set -euo pipefail

ASSET_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${HOME:?HOME must be set}/.zeropaper-wrds-opencode.XXXXXX")"
PROJECT="$TEST_ROOT/project"
PEER_PROJECT="$TEST_ROOT/project-peer"
BIN="$TEST_ROOT/bin"
SERVICE_PID=""
cleanup() {
    if [[ "$SERVICE_PID" =~ ^[0-9]+$ ]]; then
        command="$(ps -o command= -p "$SERVICE_PID" 2>/dev/null || true)"
        case "$command" in
            *wrds_srt_service.py*zeropaper-wrds-srt-service-v6*)
                kill -TERM -- "-$SERVICE_PID" 2>/dev/null || true
                ;;
        esac
    fi
    if [ "${KEEP_WRDS_OPENCODE_TEST_ROOT:-0}" = "1" ]; then
        echo "kept OpenCode WRDS test root: $TEST_ROOT" >&2
    else
        rm -rf "$TEST_ROOT"
    fi
}
trap cleanup EXIT

mkdir -p "$PROJECT/.opencode" "$PROJECT/.venv/bin" \
    "$PROJECT/code/utils" "$PROJECT/process_log" "$BIN"
export HOME="$TEST_ROOT/home"
mkdir -p "$HOME"
cp "$ASSET_ROOT/launch.sh" "$PROJECT/launch.sh"
cp "$ASSET_ROOT/templates/runtime/opencode/opencode.json" "$PROJECT/opencode.json"
cp "$ASSET_ROOT/templates/runtime/opencode/sandbox.json" "$PROJECT/.opencode/sandbox.json"
cp "$ASSET_ROOT/templates/utils/opencode_driver.py" "$PROJECT/.opencode/opencode_driver.py"
cp "$ASSET_ROOT/templates/utils/wrds_srt_service.py" \
    "$PROJECT/.opencode/wrds_srt_service.py"
ln -s /usr/bin/python3 "$PROJECT/.venv/bin/python3"
printf '{"mode":"report","flags":{"manual":false}}\n' > "$PROJECT/.deploy_manifest.json"
printf '{}\n' > "$PROJECT/.env"

cat > "$PROJECT/code/utils/start_services.sh" <<'SH'
#!/usr/bin/env bash
printf 'called\n' >> "${MOCK_WRDS_CALLS:?}"
printf 'ready\n' > "${MOCK_WRDS_READY:?}"
SH
cat > "$PROJECT/code/utils/wrds_client.py" <<'PY'
import os
def wrds_ping(): return os.path.exists(os.environ["MOCK_WRDS_READY"])
def wrds_bridge_ping(): return wrds_ping()
PY
cat > "$PROJECT/.opencode/opencode_sandbox_exec.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
shift
mkdir -p -m 700 "$HOME/.local/state/zeropaper/opencode-control"
chmod 700 "$HOME/.local/state/zeropaper/opencode-control"
export SANDBOX_RUNTIME=1
exec "$@"
SH
cat > "$PROJECT/.opencode/opencode_sandbox_exec.mjs" <<'JS'
// mocked protected adapter leaf; execution is delegated by the shell wrapper
JS
cat > "$BIN/opencode" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "${MOCK_OPENCODE_CALLS:?}"
SH
cat > "$BIN/srt" <<'SH'
#!/usr/bin/env bash
exit 0
SH
chmod +x "$PROJECT/launch.sh" "$PROJECT/code/utils/start_services.sh" \
    "$PROJECT/.opencode/opencode_driver.py" \
    "$PROJECT/.opencode/opencode_sandbox_exec.sh" "$BIN/opencode" "$BIN/srt"
cp -a "$PROJECT" "$PEER_PROJECT"

export MOCK_WRDS_CALLS="$TEST_ROOT/wrds-calls"
export MOCK_WRDS_READY="$TEST_ROOT/wrds-ready"
export MOCK_OPENCODE_CALLS="$TEST_ROOT/opencode-calls"
export PATH="$BIN:$PATH"

# The shipped credential-free state remains usable and never executes project
# service code under the privileged profile.
(cd "$PROJECT" && bash ./launch.sh opencode --once)
test ! -e "$MOCK_WRDS_CALLS"
test ! -e "$HOME/.local/state/zeropaper/opencode-control/wrds_service_identity"
printf 'WRDS_USER=test-user\nWRDS_PASS=test-pass\n' > "$PROJECT/.env"
printf 'WRDS_USER=test-user\nWRDS_PASS=test-pass\n' > "$PEER_PROJECT/.env"

# Concurrent first launches serialize across the host-wide control lock. Only
# one privileged supervisor is approved; the peer rechecks and reuses it.
(cd "$PROJECT" && bash ./launch.sh opencode --once) &
first_launcher=$!
(cd "$PEER_PROJECT" && bash ./launch.sh opencode --once) &
second_launcher=$!
wait "$first_launcher"
wait "$second_launcher"
IDENTITY="$HOME/.local/state/zeropaper/opencode-control/wrds_service_identity"
[ -s "$IDENTITY" ]
test ! -e "$HOME/.local/state/zeropaper/opencode-control/wrds_service_approval"
SERVICE_PID="$(sed -n '1p' "$IDENTITY")"
SERVICE_START="$(sed -n '2p' "$IDENTITY")"
kill -0 "$SERVICE_PID"
[ "$(ps -o pgid= -p "$SERVICE_PID" | tr -d ' ')" = "$SERVICE_PID" ]
case "$(ps -o command= -p "$SERVICE_PID")" in
    *wrds_srt_service.py*zeropaper-wrds-srt-service-v6*) ;;
    *) echo "FAIL: unexpected WRDS SRT service identity" >&2; exit 1 ;;
esac
test "$(wc -l < "$MOCK_WRDS_CALLS" | tr -d ' ')" = 1

(cd "$PROJECT" && bash ./launch.sh opencode --once)
test "$(sed -n '1p' "$IDENTITY")" = "$SERVICE_PID"
test "$(sed -n '2p' "$IDENTITY")" = "$SERVICE_START"
test "$(wc -l < "$MOCK_WRDS_CALLS" | tr -d ' ')" = 1
test "$(wc -l < "$MOCK_OPENCODE_CALLS" | tr -d ' ')" = 4

echo "PASS: OpenCode establishes and reuses one identity-validated SRT WRDS service"
