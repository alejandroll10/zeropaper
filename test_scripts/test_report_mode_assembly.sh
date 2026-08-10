#!/bin/bash
# Regression test for --mode report assembly on the econ variants (finance/macro).
# Exists because the report referee-mechanism's evaluative frame migrated from
# hardcoded text to the vocab chain in v2.16.0 (#204): if a {variant}_modes/report/
# vocab.json is deleted or truncated, setup.sh silently falls back to the SHARED
# MECH_EVAL_FRAME default ("another referee handles that") with no assembly error.
# These tripwires make that silent degradation loud. The llm_cognition report
# build is covered separately in test_llm_cognition_assembly.sh section 6.
# Build-time only (test_scripts/ is removed on deploy).
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }

for v in finance macro; do
    rm -rf test_output
    if ! ./setup.sh "test_output/$v" --variant "$v" --mode report --assemble-only --no-model-probe >/dev/null 2>&1; then
        fail "$v --mode report build failed"
        continue
    fi
    B="test_output/$v"
    RM="$B/.claude/agents/referee-mechanism.md"
    if [ ! -f "$RM" ]; then
        fail "$v report: referee-mechanism.md missing"
        continue
    fi
    # The report overlay's MECH_EVAL_FRAME names the math-auditor explicitly.
    grep -q "math-auditor handles that" "$RM" \
        && pass "$v report: eval frame names the math-auditor" \
        || fail "$v report: eval frame lost the math-auditor anchor (overlay vocab not applied?)"
    grep -q "another referee handles that" "$RM" \
        && fail "$v report: shared MECH_EVAL_FRAME default leaked (overlay vocab missing)" \
        || pass "$v report: no shared-default frame leak"
    # Econ variants have an empty REFEREE_VERDICT_NOTE — the conference-cadence
    # note is llm_cognition-only and must not appear here.
    grep -q "Verdict semantics for this variant" "$B/.claude/agents/referee.md" \
        && fail "$v report: llm verdict note leaked into econ referee" \
        || pass "$v report: no verdict-note leak"
done

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All report-mode assembly checks passed."
