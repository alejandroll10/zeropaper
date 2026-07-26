#!/bin/bash
# Regression test for the llm_cognition variant: assembly, flag gating, and
# econ-leakage tripwires. Build-time only (test_scripts/ is removed on deploy).
#
# Usage: ./test_scripts/test_llm_cognition_assembly.sh
# Runs setup.sh --local (output to test_output/llm_cognition/), so it clobbers
# any existing test_output — same caveat as any --local build.
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }

# ── 1. Gating: these must all exit non-zero ──
for args in "--variant llm_cognition --ext empirical" \
            "--variant llm_cognition --mode report" \
            "--variant llm_cognition --mode empirical-first"; do
    if ./setup.sh /tmp/llmcog_gate_test $args --local >/dev/null 2>&1; then
        fail "gate did not fire: setup.sh $args"
    else
        pass "gate fired: $args"
    fi
done

# ── 2. Assembly: bare llm_cognition must build, auto-imply theory_llm, resolve all placeholders ──
rm -rf test_output
BUILD_LOG="$(./setup.sh --variant llm_cognition --local 2>&1)"
if [ $? -ne 0 ]; then
    fail "bare --variant llm_cognition build failed"
    echo "$BUILD_LOG" | tail -5
    exit 1
fi
echo "$BUILD_LOG" | grep -q "implies --ext theory_llm" \
    && pass "theory_llm auto-implied" || fail "theory_llm not auto-implied"
echo "$BUILD_LOG" | grep -q "All placeholders resolved" \
    && pass "placeholders resolved" || fail "unresolved placeholders reported"

B=test_output/llm_cognition
[ -f "$B/.claude/agents/experiment-designer.md" ] \
    && pass "experiment-designer assembled" || fail "experiment-designer missing (auto-imply broken?)"
[ -f "$B/.claude/agents/polish-experiments.md" ] \
    && pass "polish-experiments assembled" || fail "polish-experiments missing"
grep -q "polish-experiments" "$B/docs/stage_9.md" \
    && pass "stage_9 doc amended with polish-experiments" || fail "stage_9 doc not amended"

# ── 3. Leakage tripwires: strings that must NOT appear in an llm_cognition build ──
# Each of these was a confirmed load-bearing leak closed in v2.10.0. A hit means
# a vocab default regressed or a new hardcode slipped in.
declare -A TRIPWIRES=(
    ["economic sense"]=".claude/agents/math-auditor-freeform.md"
    ["senior economist"]=".claude/agents/scorer-freeform.md"
    ["academic economics literature"]=".claude/agents/literature-scout.md"
    ["computational economist"]=".claude/agents/theory-explorer.md"
    ["SDF process"]=".claude/agents/idea-prototyper.md"
    ["Economic intuition"]=".claude/agents/implications-deriver.md"
    ["welfare/risk/policy"]=".claude/agents/referee.md"
    ["missing economic force"]=".claude/agents/polish-prose.md"
    ["CARA but not CRRA"]="CLAUDE.md"
    ["top-3-fin"]="docs/stage_6.md"
    ["falls out of economics"]="docs/stage_puzzle_triage.md"
    ["financial analyst"]=".claude/skills/llm-experiments/SKILL.md"
)
for s in "${!TRIPWIRES[@]}"; do
    f="$B/${TRIPWIRES[$s]}"
    if [ ! -f "$f" ]; then
        fail "tripwire target missing: $f"
    elif grep -qF "$s" "$f"; then
        fail "econ leak regressed: \"$s\" in ${TRIPWIRES[$s]}"
    else
        pass "clean: \"$s\" absent from ${TRIPWIRES[$s]}"
    fi
done

# ── 4. ML venue aliases present in deployed openalex script ──
grep -q '"neurips"' "$B/code/utils/openalex/openalex.py" \
    && pass "openalex ML venue aliases deployed" || fail "openalex ML venue aliases missing"

# ── 5. Contamination guidance present in experiment-designer ──
grep -q "Procedurally generate stimuli" "$B/.claude/agents/experiment-designer.md" \
    && pass "contamination-resistant ground-truth rule present" || fail "ground-truth rule missing"

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All llm_cognition assembly checks passed."
