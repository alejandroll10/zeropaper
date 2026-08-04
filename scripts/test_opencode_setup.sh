#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-opencode-setup.XXXXXX")"
trap 'rm -rf "$TMP_ROOT"' EXIT

build_and_check() {
    local name="$1"; shift
    local out="$TMP_ROOT/$name" log="$TMP_ROOT/$name.log"
    if ! "$ROOT/setup.sh" "$out" --local --no-model-probe "$@" > "$log" 2>&1; then
        cat "$log" >&2
        return 1
    fi
    test -f "$out/opencode.json"
    test -f "$out/.opencode/sandbox.json"
    test -d "$out/.opencode/agents"
    test -x "$out/.opencode/opencode_driver.py"
    test -x "$out/.opencode/opencode_sandbox_exec.sh"
    test -x "$out/.opencode/opencode_sandbox_exec.mjs"
    grep -q '^process_log/.opencode-control/$' "$out/.gitignore"
    grep -q '^process_log/.opencode-runtime/$' "$out/.gitignore"
    grep -q '\.claude/skills/codex-math/SKILL.md' \
        "$out/AGENTS.md" "$out/docs/start_session_codex.md"
    python3 - "$out/.deploy_manifest.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["infrastructure"]
assert ".opencode/agents" in d["dirs_replace"]
assert "opencode.json" in d["files_replace"]
assert ".opencode/sandbox.json" in d["files_replace"]
assert ".opencode/opencode_driver.py" in d["files_replace"]
assert ".opencode/opencode_sandbox_exec.sh" in d["files_replace"]
assert ".opencode/opencode_sandbox_exec.mjs" in d["files_replace"]
PY
    python3 - "$out/.opencode/agents" <<'PY'
from pathlib import Path
import sys
for path in Path(sys.argv[1]).glob("*.md"):
    text = path.read_text()
    header = text.split("---", 2)[1]
    if "  bash: allow\n" in header:
        assert "Long-running shell work (OpenCode)" in text, path
        assert "Use a harness-tracked background job instead" not in text, path
PY
    python3 - "$out/opencode.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["share"] == "disabled"
assert d["permission"]["doom_loop"] == "allow"
assert d["skills"]["paths"] == [".claude/skills"]
PY
}

build_and_check empirical --variant finance --ext empirical
test -f "$TMP_ROOT/empirical/.opencode/agents/empiricist.md"

build_and_check theory-llm --variant llm_cognition
test -f "$TMP_ROOT/theory-llm/.opencode/agents/experiment-designer.md"

build_and_check report --variant finance --mode report
test -f "$TMP_ROOT/report/.opencode/agents/report-synthesizer.md"
test ! -f "$TMP_ROOT/report/.opencode/agents/theory-generator.md"

# Refresh must fail before traversing a pre-sandbox .opencode parent alias.
mv "$TMP_ROOT/empirical/.opencode" "$TMP_ROOT/aliased-opencode-target"
ln -s "$TMP_ROOT/aliased-opencode-target" "$TMP_ROOT/empirical/.opencode"
if "$ROOT/update.sh" "$TMP_ROOT/empirical" > "$TMP_ROOT/update-alias.log" 2>&1; then
    echo "update accepted a symlinked .opencode parent" >&2
    exit 1
fi
grep -q 'managed path ancestor is not a real directory' "$TMP_ROOT/update-alias.log"
test -f "$TMP_ROOT/aliased-opencode-target/opencode_sandbox_exec.sh"
rm "$TMP_ROOT/empirical/.opencode"
mv "$TMP_ROOT/aliased-opencode-target" "$TMP_ROOT/empirical/.opencode"
mv "$TMP_ROOT/empirical/.claude" "$TMP_ROOT/aliased-claude-target"
ln -s "$TMP_ROOT/aliased-claude-target" "$TMP_ROOT/empirical/.claude"
if "$ROOT/update.sh" "$TMP_ROOT/empirical" > "$TMP_ROOT/update-claude-alias.log" 2>&1; then
    echo "update accepted a symlinked non-OpenCode managed parent" >&2
    exit 1
fi
grep -q 'managed path ancestor is not a real directory' "$TMP_ROOT/update-claude-alias.log"
test -f "$TMP_ROOT/aliased-claude-target/settings.json"

# Untrusted legacy manifests cannot turn stale sweeping into deletion of user
# content or repository metadata. A project venv interpreter is never executed,
# and the old predictable manifest temp alias is ignored.
rm "$TMP_ROOT/empirical/.claude"
mv "$TMP_ROOT/aliased-claude-target" "$TMP_ROOT/empirical/.claude"
mkdir -p "$TMP_ROOT/empirical/paper" "$TMP_ROOT/empirical/.git" \
    "$TMP_ROOT/empirical/.venv/bin" "$TMP_ROOT/empirical/.venv/lib/python3.11/site-packages"
printf 'paper-canary\n' > "$TMP_ROOT/empirical/paper/user-canary"
printf 'git-canary\n' > "$TMP_ROOT/empirical/.git/user-canary"
printf '#!/usr/bin/env bash\nprintf escaped > "%s"\n' "$TMP_ROOT/venv-executed" \
    > "$TMP_ROOT/empirical/.venv/bin/python3"
chmod +x "$TMP_ROOT/empirical/.venv/bin/python3"
printf '#!/usr/bin/env bash\nprintf escaped > "%s"\n' "$TMP_ROOT/jq-executed" \
    > "$TMP_ROOT/empirical/.venv/bin/jq"
chmod +x "$TMP_ROOT/empirical/.venv/bin/jq"
printf 'manifest-target\n' > "$TMP_ROOT/manifest-temp-target"
ln -s "$TMP_ROOT/manifest-temp-target" "$TMP_ROOT/empirical/.deploy_manifest.json.tmp"
python3 - "$TMP_ROOT/empirical/.deploy_manifest.json" <<'PY'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["infrastructure"]["dirs_replace"] += ["paper", ".git"]
open(p, "w").write(json.dumps(d, indent=2) + "\n")
PY
PATH="$TMP_ROOT/empirical/.venv/bin:$PATH" "$ROOT/update.sh" "$TMP_ROOT/empirical" \
    > "$TMP_ROOT/update-forged-stale.log" 2>&1
test "$(cat "$TMP_ROOT/empirical/paper/user-canary")" = paper-canary
test "$(cat "$TMP_ROOT/empirical/.git/user-canary")" = git-canary
test ! -e "$TMP_ROOT/venv-executed"
test ! -e "$TMP_ROOT/jq-executed"
test "$(cat "$TMP_ROOT/manifest-temp-target")" = manifest-target

# The pre-manifest paper migration and state/env updates reject aliased parents
# or leaves without modifying their external targets.
mv "$TMP_ROOT/theory-llm/paper" "$TMP_ROOT/theory-paper-real"
mkdir "$TMP_ROOT/external-paper"
printf 'external-paper\n' > "$TMP_ROOT/external-paper/referee_reports"
ln -s "$TMP_ROOT/external-paper" "$TMP_ROOT/theory-llm/paper"
if "$ROOT/update.sh" "$TMP_ROOT/theory-llm" > "$TMP_ROOT/update-paper-alias.log" 2>&1; then
    echo "update accepted a symlinked paper parent" >&2; exit 1
fi
test "$(cat "$TMP_ROOT/external-paper/referee_reports")" = external-paper

printf 'external-env\n' > "$TMP_ROOT/external-env-target"
rm "$TMP_ROOT/report/.env"
ln -s "$TMP_ROOT/external-env-target" "$TMP_ROOT/report/.env"
if "$ROOT/update.sh" "$TMP_ROOT/report" > "$TMP_ROOT/update-env-alias.log" 2>&1; then
    echo "update accepted a symlinked environment file" >&2; exit 1
fi
test "$(cat "$TMP_ROOT/external-env-target")" = external-env

mkdir -p "$TMP_ROOT/report-state/process_log"
cp "$TMP_ROOT/report/.deploy_manifest.json" "$TMP_ROOT/report-state/.deploy_manifest.json"
printf '{"status":"running"}\n' > "$TMP_ROOT/external-state-target"
ln -s "$TMP_ROOT/external-state-target" "$TMP_ROOT/report-state/process_log/pipeline_state.json"
if "$ROOT/update.sh" "$TMP_ROOT/report-state" --variant finance > "$TMP_ROOT/update-state-alias.log" 2>&1; then
    echo "update accepted a symlinked pipeline state" >&2; exit 1
fi
test "$(cat "$TMP_ROOT/external-state-target")" = '{"status":"running"}'

echo "OpenCode setup integration tests passed"
