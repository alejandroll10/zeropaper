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
# (--mode report is supported since v2.16.0/#204 and is tested in section 6.)
for args in "--variant llm_cognition --ext empirical" \
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
# Portable string|file pairs (macOS /bin/bash is 3.2 — no associative arrays;
# the earlier declare -A version died at the loop with set -u, so these
# tripwires silently never ran on stock macOS).
TRIPWIRES=(
    "economic sense|.claude/agents/math-auditor-freeform.md"
    "senior economist|.claude/agents/scorer-freeform.md"
    "academic economics literature|.claude/agents/literature-scout.md"
    "computational economist|.claude/agents/theory-explorer.md"
    "SDF process|.claude/agents/idea-prototyper.md"
    "Economic intuition|.claude/agents/implications-deriver.md"
    "welfare/risk/policy|.claude/agents/referee.md"
    "missing economic force|.claude/agents/polish-prose.md"
    "CARA but not CRRA|CLAUDE.md"
    "top-3-fin|docs/stage_6.md"
    "falls out of economics|docs/stage_puzzle_triage.md"
    "financial analyst|.claude/skills/llm-experiments/SKILL.md"
    "V_S = V_U|.claude/agents/debugger.md"
    "PERMNO vs GVKEY|.claude/agents/debugger.md"
    "Economists have long debated|.claude/agents/style.md"
    "power utility|.claude/agents/style.md"
    "Berk-Green|.claude/agents/triager.md"
    "economic stakes|.claude/agents/triager.md"
    "equilibrium concept|.claude/agents/last-resort.md"
    "equilibrium concept|.claude/agents/debugger.md"
    "Economists have long|.claude/agents/paper-writer.md"
    "Economic intuition|.claude/agents/paper-writer.md"
)
for pair in "${TRIPWIRES[@]}"; do
    s="${pair%%|*}"
    rel="${pair##*|}"
    f="$B/$rel"
    if [ ! -f "$f" ]; then
        fail "tripwire target missing: $f"
    elif grep -qF "$s" "$f"; then
        fail "econ leak regressed: \"$s\" in $rel"
    else
        pass "clean: \"$s\" absent from $rel"
    fi
done

# ── 3b. Paper skeleton + section list (#200): ML-preprint format, ML sections ──
grep -q "doublespacing" "$B/paper/main.tex" \
    && fail "main.tex is double-spaced (econ skeleton shipped instead of ML skeleton)" \
    || pass "main.tex single-spaced ML skeleton"
grep -q "documentclass\[10pt\]" "$B/paper/main.tex" \
    && pass "main.tex 10pt single-column preamble" || fail "main.tex missing 10pt preamble"
grep -q "sections/related_work" "$B/paper/main.tex" \
    && pass "main.tex names related_work in section order" || fail "main.tex missing related_work comment"
grep -q "sections/checklist" "$B/paper/main.tex" \
    && pass "main.tex carries post-references checklist slot" || fail "main.tex missing checklist slot"
grep -q "related_work.tex" "$B/docs/stage_5.md" \
    && pass "stage_5 section list has related_work.tex" || fail "stage_5 missing related_work.tex"
grep -q "experiments.tex" "$B/docs/stage_5.md" \
    && pass "stage_5 section list has experiments.tex" || fail "stage_5 missing experiments.tex"
grep -q "checklist.tex" "$B/docs/stage_5.md" \
    && pass "stage_5 section list has checklist.tex" || fail "stage_5 missing checklist.tex"
grep -q '### `experiments.tex`' "$B/.claude/agents/paper-writer.md" \
    && pass "paper-writer carries experiments.tex guidance" || fail "paper-writer missing experiments.tex guidance"
grep -q "9-10 single-column pages" "$B/.claude/agents/paper-writer.md" \
    && pass "paper-writer page budget is ML-calibrated" || fail "paper-writer page budget not ML-calibrated"
if grep -rq "VARIANT_LLM_COGNITION" "$B" 2>/dev/null; then
    fail "VARIANT_LLM_COGNITION marker leaked into deployed files"
else
    pass "no variant-marker leakage"
fi

# ── 3c. Per-variant skill gating (#205): econ-only skills absent ──
for gated in ".claude/skills/ssj" ".claude/skills/nber-agenda" \
             ".agents/skills/ssj" ".agents/skills/nber-agenda" \
             "code/utils/ssj" "code/utils/nber_agenda"; do
    if [ -e "$B/$gated" ]; then
        fail "econ-only skill installed despite gating: $gated"
    else
        pass "gated out: $gated"
    fi
done
# The gated dirs must also be absent from the manifest, or update.sh would
# try to refresh paths the deploy never creates.
if grep -q "code/utils/ssj\|code/utils/nber_agenda" "$B/.deploy_manifest.json" 2>/dev/null; then
    fail "manifest still lists gated skill util dirs"
else
    pass "manifest clean of gated skill util dirs"
fi
# And the always-on core skills must still be present.
for kept in ".claude/skills/sympy" ".claude/skills/codex-math" \
            ".claude/skills/openalex" ".claude/skills/bib-verify"; do
    if [ -d "$B/$kept" ]; then
        pass "core skill kept: $kept"
    else
        fail "core skill missing: $kept"
    fi
done

# ── 4. ML venue aliases present in deployed openalex script ──
grep -q '"neurips"' "$B/code/utils/openalex/openalex.py" \
    && pass "openalex ML venue aliases deployed" || fail "openalex ML venue aliases missing"

# ── 5. Contamination guidance present in experiment-designer ──
grep -q "Procedurally generate stimuli" "$B/.claude/agents/experiment-designer.md" \
    && pass "contamination-resistant ground-truth rule present" || fail "ground-truth rule missing"

# ── 6. Report mode (#204): llm_cognition report build assembles ML-calibrated referees ──
rm -rf test_output
REPORT_LOG="$(./setup.sh --variant llm_cognition --mode report --local 2>&1)"
if [ $? -ne 0 ]; then
    fail "llm_cognition --mode report build failed"
    echo "$REPORT_LOG" | tail -5
else
    pass "llm_cognition --mode report builds"
    echo "$REPORT_LOG" | grep -q "All placeholders resolved" \
        && pass "report-mode placeholders resolved" || fail "report-mode unresolved placeholders"
    R=test_output/llm_cognition
    if echo "$REPORT_LOG" | grep -q "implies --ext theory_llm"; then
        fail "theory_llm auto-implied under report mode (should be skipped — agents get pruned anyway)"
    else
        pass "theory_llm auto-imply skipped under report mode"
    fi
    for s in "senior economist|.claude/agents/referee-mechanism.md" \
             "economic force|.claude/agents/referee-mechanism.md" \
             "works as economics|.claude/agents/referee-mechanism.md" \
             "theory/economics or empirics|.claude/agents/referee.md" \
             "a top journal would expect|.claude/agents/referee.md"; do
        str="${s%%|*}"; rel="${s##*|}"
        if [ ! -f "$R/$rel" ]; then fail "report tripwire target missing: $rel"
        elif grep -qF "$str" "$R/$rel"; then fail "report econ leak: \"$str\" in $rel"
        else pass "report clean: \"$str\" absent from $rel"; fi
    done
    grep -q "top ML venue" "$R/.claude/agents/referee.md" \
        && pass "report referee anchored to ML venue role" || fail "report referee missing ML venue role"
    grep -q "Verdict semantics for this variant" "$R/.claude/agents/referee.md" \
        && pass "conference-cadence verdict note present" || fail "verdict note missing in report referee"
    # The note must be the REPORT-anchored override, not the pipeline one:
    # report mode has no editor agent and no tier table to route through.
    if grep -q "the editor can route\|tier table" "$R/.claude/agents/referee.md"; then
        fail "report referee carries the pipeline verdict note (names editor/tier table)"
    else
        pass "verdict note is report-anchored (no editor/tier-table routing)"
    fi
    grep -q "report-synthesizer can aggregate" "$R/.claude/agents/referee.md" \
        && pass "verdict note routes via report-synthesizer" || fail "verdict note missing synthesizer routing"
    grep -q "math-auditor handles that" "$R/.claude/agents/referee-mechanism.md" \
        && pass "report mech frame names the math-auditor" || fail "report mech frame missing math-auditor anchor"
    [ -f "$R/.claude/agents/report-synthesizer.md" ] \
        && pass "report-synthesizer assembled" || fail "report-synthesizer missing"
    [ -e "$R/.claude/skills/ssj" ] \
        && fail "ssj installed in llm report build (skill gating regressed)" || pass "skill gating holds in report mode"
fi

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All llm_cognition assembly checks passed."
