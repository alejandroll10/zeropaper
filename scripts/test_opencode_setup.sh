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
    test -d "$out/.opencode/agents"
    grep -q '\.claude/skills/codex-math/SKILL.md' \
        "$out/AGENTS.md" "$out/docs/start_session_codex.md"
    python3 - "$out/.deploy_manifest.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))["infrastructure"]
assert ".opencode/agents" in d["dirs_replace"]
assert "opencode.json" in d["files_replace"]
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

echo "OpenCode setup integration tests passed"
