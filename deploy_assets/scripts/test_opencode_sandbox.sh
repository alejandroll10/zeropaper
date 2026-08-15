#!/usr/bin/env bash
# Real OS-boundary canary for the OpenCode Anthropic Sandbox Runtime adapter.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
command -v srt >/dev/null 2>&1 || {
    echo "SKIP: install @anthropic-ai/sandbox-runtime to run the OpenCode sandbox canary"
    exit 0
}

# codex-math must recognize SRT as an already-active outer sandbox instead of
# attempting a nested Seatbelt/bubblewrap profile.
codex_math_mode="$(SANDBOX_RUNTIME=1 CODEX_SANDBOX= bash -c \
    '. "$1"; printf "%s" "$CODEX_SANDBOX_MODE"' _ \
    "$ROOT/templates/utils/codex_math/codex_common.sh" 2>/dev/null)"
test "$codex_math_mode" = "danger-full-access"

HOST_HOME="${HOME:?HOME must be set}"
# Keep the fake home outside /tmp: /tmp is intentionally writable, so placing
# the external-write canary there would invalidate the Linux test.
TEST_ROOT="$(mktemp -d "$HOST_HOME/.zeropaper-opencode-sandbox.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT
FAKE_HOME="$TEST_ROOT/home"
mkdir -p "$FAKE_HOME/.ssh" "$FAKE_HOME/external" "$TEST_ROOT/project"
mkdir -p "$TEST_ROOT/project/.opencode" "$TEST_ROOT/project/process_log/.opencode-control"
mkdir -p "$TEST_ROOT/project/process_log/.opencode-control/update-canary"
cp "$ROOT/templates/runtime/opencode/sandbox.json" "$TEST_ROOT/project/.opencode/sandbox.json"
cp "$ROOT/templates/utils/opencode_sandbox_exec.sh" "$TEST_ROOT/project/.opencode/"
cp "$ROOT/templates/utils/opencode_sandbox_exec.mjs" "$TEST_ROOT/project/.opencode/"
chmod +x "$TEST_ROOT/project/.opencode/opencode_sandbox_exec.sh"
printf '#!/usr/bin/env bash\n' > "$TEST_ROOT/project/launch.sh"
printf '{}\n' > "$TEST_ROOT/project/opencode.json"
printf 'OPENCODE_API_KEY=test-only\n' > "$TEST_ROOT/project/.env"
printf '{}\n' > "$TEST_ROOT/project/.deploy_manifest.json"
printf 'trusted-stage\n' > "$TEST_ROOT/project/process_log/.opencode-control/update-canary/manifest.next"
printf 'credential-canary\n' > "$FAKE_HOME/.ssh/secret"
printf 'outside-canary\n' > "$FAKE_HOME/external/existing"

(
    cd "$TEST_ROOT/project"
    HOME="$FAKE_HOME" bash .opencode/opencode_sandbox_exec.sh \
        .opencode/sandbox.json sh -c '
            test "$SANDBOX_RUNTIME" = 1
            test "$XDG_DATA_HOME" = "$PWD/process_log/.opencode-runtime/data"
            test "$XDG_STATE_HOME" = "$PWD/process_log/.opencode-runtime/state"
            printf "allowed\n" > project-write
            printf "cache-allowed\n" > "$HOME/.cache/opencode/opencode-sandbox-canary"
            mkdir -p "$HOME/.cache/zeropaper/wrds" 2>/dev/null || true
            if printf "guard-tamper\n" > "$HOME/.cache/zeropaper/wrds/authblock"; then exit 33; fi
            curl -fsS --max-time 15 https://example.com >/dev/null
            ! test -r "$HOME/.ssh/secret"
            if printf "escape\n" > "$HOME/external/new"; then exit 10; fi
            if rm "$HOME/external/existing"; then exit 11; fi
            if printf "late-credential\n" > "$HOME/.aws/late-secret"; then exit 20; fi
            if printf "stolen\n" > "$HOME/.codex/auth.json"; then exit 23; fi
            if printf "plugin\n" > "$HOME/.codex/plugins/persist"; then exit 24; fi
            if printf "relaxed\n" > .opencode/sandbox.json; then exit 13; fi
            if printf "bypass\n" > .opencode/opencode_sandbox_exec.mjs; then exit 14; fi
            if printf "bypass\n" > launch.sh; then exit 15; fi
            if printf "bypass\n" > opencode.json; then exit 16; fi
            if printf "stolen\n" > .env; then exit 25; fi
            if printf "forged\n" > .deploy_manifest.json; then exit 27; fi
            if mv .opencode .opencode-bypass; then exit 17; fi
            if mv launch.sh launch-bypass.sh; then exit 18; fi
            if mv opencode.json opencode-bypass.json; then exit 19; fi
            if mv .env env-bypass; then exit 26; fi
            if mv .deploy_manifest.json manifest-bypass.json; then exit 28; fi
            if ln launch.sh launch-hardlink; then exit 29; fi
            if ln .deploy_manifest.json manifest-hardlink; then exit 30; fi
            if printf "control-bypass\n" > process_log/.opencode-control/driver.log; then exit 21; fi
            if printf "forged-stage\n" > process_log/.opencode-control/update-canary/manifest.next; then exit 31; fi
            if rm process_log/.opencode-control/update-canary/manifest.next; then exit 32; fi
            if mv process_log/.opencode-control process_log/.opencode-control-bypass; then exit 22; fi
            printf "state-allowed\n" > process_log/.opencode-runtime/state/canary
            sh -c '\''
                ! test -r "$HOME/.ssh/secret"
                if printf "child-escape\n" > "$HOME/external/child-new"; then exit 12; fi
            '\''
        '
)

test "$(cat "$TEST_ROOT/project/project-write")" = "allowed"
test "$(cat "$FAKE_HOME/.cache/opencode/opencode-sandbox-canary")" = "cache-allowed"
test "$(cat "$FAKE_HOME/external/existing")" = "outside-canary"
test ! -e "$FAKE_HOME/external/new"
test ! -e "$FAKE_HOME/external/child-new"
test -d "$FAKE_HOME/.aws"
test ! -e "$FAKE_HOME/.aws/late-secret"
test "$(cat "$TEST_ROOT/project/process_log/.opencode-runtime/state/canary")" = "state-allowed"
test "$(cat "$TEST_ROOT/project/process_log/.opencode-control/update-canary/manifest.next")" = "trusted-stage"
python3 - "$TEST_ROOT/project/launch.sh" "$TEST_ROOT/project/.deploy_manifest.json" <<'PY'
import os, sys
assert all(os.lstat(path).st_nlink == 1 for path in sys.argv[1:])
PY

SYMLINK_HOME="$TEST_ROOT/symlink-home"
mkdir -p "$SYMLINK_HOME/credential-target"
ln -s credential-target "$SYMLINK_HOME/.ssh"
if symlink_error="$(HOME="$SYMLINK_HOME" bash "$TEST_ROOT/project/.opencode/opencode_sandbox_exec.sh" \
    "$TEST_ROOT/project/.opencode/sandbox.json" true 2>&1)"; then
    echo "ERROR: sandbox adapter accepted a symlinked credential directory" >&2
    exit 1
fi
case "$symlink_error" in
    *"protected path must not be a symlink"*) ;;
    *) echo "ERROR: symlink canary failed for the wrong reason: $symlink_error" >&2; exit 1 ;;
esac

SYMLINK_CODEX_HOME="$TEST_ROOT/symlink-codex-home"
mkdir -p "$SYMLINK_CODEX_HOME/codex-target"
ln -s codex-target "$SYMLINK_CODEX_HOME/.codex"
if codex_symlink_error="$(HOME="$SYMLINK_CODEX_HOME" bash "$TEST_ROOT/project/.opencode/opencode_sandbox_exec.sh" \
    "$TEST_ROOT/project/.opencode/sandbox.json" true 2>&1)"; then
    echo "ERROR: sandbox adapter accepted a symlinked Codex state directory" >&2
    exit 1
fi
case "$codex_symlink_error" in
    *"protected path must not be a symlink"*) ;;
    *) echo "ERROR: Codex ancestor canary failed for the wrong reason: $codex_symlink_error" >&2; exit 1 ;;
esac

SYMLINK_LOG_PROJECT="$TEST_ROOT/symlink-log-project"
mkdir -p "$SYMLINK_LOG_PROJECT/.opencode" "$SYMLINK_LOG_PROJECT/external-log"
cp "$TEST_ROOT/project/.opencode/"* "$SYMLINK_LOG_PROJECT/.opencode/"
ln -s external-log "$SYMLINK_LOG_PROJECT/process_log"
if process_log_error="$(cd "$SYMLINK_LOG_PROJECT" && HOME="$FAKE_HOME" \
    bash .opencode/opencode_sandbox_exec.sh .opencode/sandbox.json true 2>&1)"; then
    echo "ERROR: sandbox adapter accepted a symlinked process_log" >&2
    exit 1
fi
case "$process_log_error" in
    *"process_log must be a real directory"*) ;;
    *) echo "ERROR: process_log canary failed for the wrong reason: $process_log_error" >&2; exit 1 ;;
esac
test ! -e "$SYMLINK_LOG_PROJECT/external-log/.opencode-runtime"

HARDLINK_CODEX_HOME="$TEST_ROOT/hardlink-codex-home"
mkdir -p "$HARDLINK_CODEX_HOME/.codex"
printf '{}\n' > "$HARDLINK_CODEX_HOME/.codex/auth.json"
ln "$HARDLINK_CODEX_HOME/.codex/auth.json" "$HARDLINK_CODEX_HOME/.codex/auth-alias"
if hardlink_error="$(HOME="$HARDLINK_CODEX_HOME" bash "$TEST_ROOT/project/.opencode/opencode_sandbox_exec.sh" \
    "$TEST_ROOT/project/.opencode/sandbox.json" true 2>&1)"; then
    echo "ERROR: sandbox adapter accepted a hard-linked Codex auth file" >&2
    exit 1
fi
case "$hardlink_error" in
    *"protected file has alternate hard links"*) ;;
    *) echo "ERROR: Codex hard-link canary failed for the wrong reason: $hardlink_error" >&2; exit 1 ;;
esac
echo "OpenCode sandbox real-boundary canaries passed"
