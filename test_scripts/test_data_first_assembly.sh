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
#   4. State fields — the spec, conditional coverage certificate, triangulation,
#      release pointers, and three data-first loops must be injected (and absent
#      from the control build).
#   5. Stage 2 artifact label — the shared filename remains theory_draft_vN.md,
#      but the operator-facing commit label must call it a dataset spec here.
#   6. Updater allowlist — scripts/update_coordinator.sh enumerates modes in two
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
assert d["dataset_spec_version"] is None and d["dataset_spec_serial"] == 0
assert d["dataset_coverage_certificate_serial"] == 0
assert d["dataset_rights_inventory"] is None
assert d["dataset_rights_inventory_sha256"] is None
assert d["dataset_coverage_certificate"] is None
assert d["dataset_coverage_certificate_sha256"] is None
assert "coverage_triangulation" in d
assert d["dataset_release_path"] is None and d["dataset_release_receipt"] is None
assert "spec_audit_revision" in d["loops"]
assert "coverage_certificate_producer" in d["loops"]
assert "coverage_audit" in d["loops"]
PY
[ -d "$D/output/dataset" ] \
    && pass "data-first: output/dataset release dir bootstrapped" \
    || fail "data-first: output/dataset missing"
if grep -q "output/stage2/source_rights_s{dataset_spec_serial}_vN.json" "$D/docs/stage_2.md" \
        && grep -q 'output/stage2/coverage_certificate_c{dataset_coverage_certificate_serial}_s{dataset_spec_serial}_vN.json' "$D/docs/stage_2.md" \
        && grep -q 'coverage-census-only' "$D/.claude/agents/empiricist.md" \
        && grep -q '\*\*Coverage certificate:\*\* REQUIRED' "$D/.claude/agents/mechanism-auditor.md" \
        && grep -q '\*\*Coverage commitments:\*\* \[' "$D/.claude/agents/mechanism-auditor.md" \
        && grep -q '"enumeration_status": "complete"' "$D/.claude/agents/empiricist.md" \
        && grep -q 'Every event row requires a non-empty `evidence` array' "$D/docs/stage_2.md" \
        && grep -q '`complete` iff `enumeration_error` is null' "$D/docs/stage_2.md" \
        && grep -q 'a `verified` row needs at least one `predicate-satisfied` record' "$D/docs/stage_2.md" \
        && grep -q 'a `gap` row needs the complete named-search attempt record' "$D/docs/stage_2.md" \
        && grep -q 'an `error` row needs at least one `operational-error` record' "$D/docs/stage_2.md" \
        && grep -q 'Every event row must have a non-empty `evidence` array' "$D/.claude/agents/empiricist.md" \
        && grep -q 'halted_coverage_certificate_invalid' "$D/docs/stage_2.md" \
        && grep -q 'dataset_coverage_certificate_sha256' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'completely re-enumerates the live authoritative universe' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'certificate-build-mismatch' "$D/.claude/agents/coverage-auditor.md" \
        && grep -q 'certificate-source-drift' "$D/.claude/agents/coverage-auditor.md" \
        && grep -q 'distinct exact-commitment check' "$D/.claude/agents/coverage-auditor.md" \
        && grep -q 'never hand them to `data-selection-auditor`' "$D/.claude/agents/coverage-auditor.md" \
        && grep -q 'RIGHTS_INVENTORY_SHA256' "$D/.claude/agents/coverage-auditor.md" \
        && grep -q 'exact `RIGHTS_INVENTORY` and `RIGHTS_INVENTORY_SHA256`' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'both `dataset_spec_version = null` and `stage3a_theory_version = null`' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'pipeline_state.json:dataset_rights_inventory' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'dataset_rights_inventory_sha256' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'RELEASE_SUPERSEDES_ARGS' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'retire-pair' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'pipeline_state.json:dataset_rights_inventory' "$D/.claude/agents/empirics-auditor.md" \
        && ! grep -q 'source_rights_s{dataset_spec_serial}' "$D/.claude/agents/empirics-auditor.md" \
        && grep -q 'pipeline_state.json:dataset_rights_inventory' "$D/docs/stage_5.md" \
        && grep -q 'network_access.*false' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'dataset_release' "$D/docs/stage_3a_empirical.md" \
        && grep -q 'activate-pair' "$D/docs/stage_3a_empirical.md"; then
    pass "data-first: Gate-2 certificate, rights inventory, and trusted offline release contract assembled"
else
    fail "data-first: Gate-2 certificate, rights inventory, or trusted offline release contract missing"
fi
for reset_doc in stage_0.md stage_1.md stage_puzzle_triage.md; do
    grep -q 'dataset_spec_version' "$D/docs/$reset_doc" \
        && pass "data-first: $reset_doc resets spec acceptance" \
        || fail "data-first: $reset_doc omits spec-acceptance reset"
done
grep -Fq 'Commit: `artifact: dataset spec v{N}`' "$D/docs/stage_2.md" \
    && pass "data-first: Stage 2 commit labels the dataset spec" \
    || fail "data-first: Stage 2 commit still mislabels the artifact"

# Manual composition keeps the scientific/release contract but has no autonomous state.
if ! ./setup.sh test_output/df_manual --variant finance --mode data-first --manual --assemble-only --no-model-probe >/dev/null 2>&1; then
    fail "data-first manual build failed"
else
    M="test_output/df_manual"
    python3 - "$M" <<'PY' \
        && pass "data-first manual: caller authority and registry handoff assembled" \
        || fail "data-first manual: release authority still depends on pipeline state"
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
manifest = json.loads((root / ".deploy_manifest.json").read_text())
assert manifest["mode"] == "data-first"
assert manifest["flags"]["manual"] is True
assert not (root / "process_log/pipeline_state.json").exists()
stage = (root / "docs/stage_3a_empirical.md").read_text()
evidence = (root / "docs/results_evidence.md").read_text()
auditor = (root / ".claude/agents/empirics-auditor.md").read_text()
utility = (root / "code/utils/results_pipeline/results_pipeline.py").read_text()
assert 'RIGHTS_AUTHORITY = "manual-caller"' in stage
assert "COVERAGE_CERTIFICATE_DECISION" in stage
assert "COVERAGE_COMMITMENTS" in stage
assert "exact `RIGHTS_INVENTORY` and `RIGHTS_INVENTORY_SHA256`" in stage
coverage_auditor = (root / ".claude/agents/coverage-auditor.md").read_text()
assert "RIGHTS_INVENTORY_SHA256" in coverage_auditor
assert "independently supplied rights path/digest" in coverage_auditor
assert "exhaustively re-enumerate each certificate-governed universe" in coverage_auditor
assert "never hand them to `data-selection-auditor`" in coverage_auditor
assert "both `dataset_spec_version = null` and `stage3a_theory_version = null`" in stage
assert "Never create pipeline state" in stage
assert "manual-caller" in evidence and "manual-caller" in auditor
assert "rights_authority" in utility
assert "require `FRESH`" not in auditor
PY
fi

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
    if grep -rl 'dataset_coverage_certificate' "$E/docs" >/dev/null 2>&1; then
        fail "empirical-first control: data-first certificate prose leaked into docs"
    else
        pass "empirical-first control: no data-first certificate prose leak"
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
    if grep -q 'coverage-census-only' "$E/.claude/agents/empiricist.md"; then
        fail "empirical-first control: census-only launch leaked into empiricist"
    else
        pass "empirical-first control: empiricist has no census-only launch"
    fi
    python3 - "$E" <<'PY' && pass "empirical-first control: no data-first state fields" || fail "empirical-first control: data-first state fields leaked"
import json, sys
d = json.load(open(sys.argv[1] + "/process_log/pipeline_state.json"))
assert "dataset_spec_version" not in d and "dataset_spec_serial" not in d
assert "dataset_coverage_certificate_serial" not in d
assert "dataset_rights_inventory" not in d
assert "dataset_rights_inventory_sha256" not in d
assert "dataset_coverage_certificate" not in d
assert "dataset_coverage_certificate_sha256" not in d
assert "coverage_triangulation" not in d
assert "dataset_release_path" not in d and "dataset_release_receipt" not in d
assert "spec_audit_revision" not in d["loops"]
assert "coverage_certificate_producer" not in d["loops"]
assert "coverage_audit" not in d["loops"]
PY
    grep -Fq 'Commit: `artifact: theory draft v{N}`' "$E/docs/stage_2.md" \
        && pass "empirical-first control: Stage 2 commit label unchanged" \
        || fail "empirical-first control: Stage 2 commit label changed"
fi

# 6. Updater allowlist static check (both hardcoded sites).
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
