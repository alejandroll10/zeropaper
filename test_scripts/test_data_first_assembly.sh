#!/bin/bash
# Regression test for --mode data-first assembly (#278, v2.30.0).
# Tripwires for the failure modes the mode's implementation specifically guards:
#   1. Marker leakage — a DATA_FIRST (or any mode-family) marker surviving into a
#      deployed doc/agent means the resolver's family table and keep() drifted.
#   2. Dangling identification references — the identification agents are pruned
#      under data-first; a deployed stage_3a_empirical.md that still instructs
#      launching them sends the orchestrator at agents that don't exist.
#   3. Mode-gated assembly — coverage-auditor must exist ONLY under data-first;
#      the identification pair must NOT exist under data-first; both must be
#      untouched in an empirical-first control build.
#   4. State fields — dataset_spec_version / coverage_triangulation / the two
#      data-first loops must be injected (and absent from the control build).
#   5. Updater allowlist — scripts/update_coordinator.sh enumerates modes in two
#      hardcoded sites independently of resolve_config.sh; losing data-first
#      there makes deployed data-first projects un-updatable (static check).
# Build-time only (test_scripts/ is removed on deploy).
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }

rm -rf test_output
if ! ./setup.sh test_output/df --variant finance --mode data-first --assemble-only --no-model-probe >/dev/null 2>&1; then
    fail "data-first build failed"
    exit 1
fi
D="test_output/df"

# 1. Marker leakage — zero mode-family markers anywhere reader-facing.
if grep -rlE '<!-- (THEORY_FIRST|EMPIRICAL_FIRST|MEASUREMENT_FIRST|DATA_FIRST|NO_MODE|MANUAL|AUTONOMOUS)_(START|END) -->' \
        "$D/docs" "$D/CLAUDE.md" "$D/.claude/agents" >/dev/null 2>&1; then
    fail "data-first: mode-family marker leaked into deployed docs/agents"
else
    pass "data-first: no marker leakage"
fi

# 2. Dangling identification references in the deployed construction stage doc.
if grep -qE 'identification-auditor|identification-designer|identification_menu' "$D/docs/stage_3a_empirical.md"; then
    fail "data-first: stage_3a_empirical.md references pruned identification machinery"
else
    pass "data-first: stage_3a doc clean of identification references"
fi

# 3. Mode-gated assembly.
[ -f "$D/.claude/agents/coverage-auditor.md" ] \
    && pass "data-first: coverage-auditor assembled" \
    || fail "data-first: coverage-auditor missing"
[ -f "$D/.claude/agents/mechanism-auditor.md" ] \
    && pass "data-first: mechanism-auditor (spec-audit role) assembled" \
    || fail "data-first: mechanism-auditor missing"
grep -q "dataset specification" "$D/.claude/agents/mechanism-auditor.md" \
    && pass "data-first: mechanism-auditor carries the spec-audit body" \
    || fail "data-first: mechanism-auditor body is not the data-first overlay"
for a in identification-designer identification-auditor; do
    [ -f "$D/.claude/agents/$a.md" ] \
        && fail "data-first: $a should be pruned" \
        || pass "data-first: $a pruned"
done

# 4. State fields + loops + release dir.
python3 - "$D" <<'PY' && pass "data-first: state fields and loops injected" || fail "data-first: state fields/loops missing"
import json, sys
d = json.load(open(sys.argv[1] + "/process_log/pipeline_state.json"))
assert "dataset_spec_version" in d and "coverage_triangulation" in d
assert "spec_audit_revision" in d["loops"] and "coverage_audit" in d["loops"]
PY
[ -d "$D/output/dataset" ] \
    && pass "data-first: output/dataset release dir bootstrapped" \
    || fail "data-first: output/dataset missing"
grep -q "output/dataset/manifest.json" "$D/docs/stage_3a_empirical.md" \
    && pass "data-first: release-assembly producer step present in stage_3a doc" \
    || fail "data-first: no release-assembly producer step in stage_3a doc"

# Control build: empirical-first must be unaffected.
if ! ./setup.sh test_output/ef --variant finance --mode empirical-first --assemble-only --no-model-probe >/dev/null 2>&1; then
    fail "empirical-first control build failed"
else
    E="test_output/ef"
    [ -f "$E/.claude/agents/coverage-auditor.md" ] \
        && fail "empirical-first control: coverage-auditor leaked" \
        || pass "empirical-first control: coverage-auditor absent"
    [ -f "$E/.claude/agents/identification-designer.md" ] \
        && pass "empirical-first control: identification-designer present" \
        || fail "empirical-first control: identification-designer missing"
    if grep -rli "data-first" "$E/docs" >/dev/null 2>&1; then
        fail "empirical-first control: data-first prose leaked into docs"
    else
        pass "empirical-first control: no data-first prose leak"
    fi
    if grep -rlE '<!-- (THEORY_FIRST|EMPIRICAL_FIRST|MEASUREMENT_FIRST|DATA_FIRST|NO_MODE|MANUAL|AUTONOMOUS)_(START|END) -->' \
            "$E/docs" "$E/CLAUDE.md" "$E/.claude/agents" >/dev/null 2>&1; then
        fail "empirical-first control: mode-family marker leaked"
    else
        pass "empirical-first control: no marker leakage"
    fi
    if grep -rl "DATA_FIRST" "$E/.claude/agents" >/dev/null 2>&1; then
        fail "empirical-first control: DATA_FIRST content leaked into agents"
    else
        pass "empirical-first control: agents clean of DATA_FIRST content"
    fi
    python3 - "$E" <<'PY' && pass "empirical-first control: no data-first state fields" || fail "empirical-first control: data-first state fields leaked"
import json, sys
d = json.load(open(sys.argv[1] + "/process_log/pipeline_state.json"))
assert "dataset_spec_version" not in d and "coverage_triangulation" not in d
assert "spec_audit_revision" not in d["loops"] and "coverage_audit" not in d["loops"]
PY
fi

# 5. Updater allowlist static check (both hardcoded sites).
grep -q 'empirical-first, measurement-first, data-first, report.*--no-mode' scripts/update_coordinator.sh \
    && pass "updater: --mode diagnostic lists data-first" \
    || fail "updater: --mode diagnostic missing data-first"
grep -q '"empirical-first", "measurement-first", "data-first", "report"' scripts/update_coordinator.sh \
    && pass "updater: manifest-selector allowlist lists data-first" \
    || fail "updater: manifest-selector allowlist missing data-first"

rm -rf test_output
if [ "$FAILS" -gt 0 ]; then
    echo "FAIL: $FAILS data-first assembly check(s) failed"
    exit 1
fi
echo "All data-first assembly checks passed."
