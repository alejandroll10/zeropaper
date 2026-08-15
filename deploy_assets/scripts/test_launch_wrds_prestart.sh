#!/usr/bin/env bash
# Focused regression for launch.sh's host-side empirical service decision.
set -euo pipefail

ASSET_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-wrds-launch-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

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
mkdir -p "$TEST_ROOT/cache-home/.cache" "$TEST_ROOT/cache-target"
chmod 700 "$TEST_ROOT/cache-home" "$TEST_ROOT/cache-home/.cache" "$TEST_ROOT/cache-target"
ln -s "$TEST_ROOT/cache-target" "$TEST_ROOT/cache-home/.cache/uv"
if (HOME="$TEST_ROOT/cache-home" RUNTIME=codex prepare_runtime_cache_roots) 2>/dev/null; then
    echo "FAIL: planted cache-root symlink was accepted" >&2
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
