#!/bin/bash
# Regression for #257: seeded Gate 4 evaluates correctness without reopening
# the fixed research direction through branch-manager or score escalation.
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }
expect_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq "$text" "$file" && pass "$label" || fail "$label"
}
reject_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq "$text" "$file" && fail "$label" || pass "$label"
}
expect_order() {
    local file="$1" first="$2" second="$3" label="$4" first_line second_line
    first_line="$(grep -nF "$first" "$file" | head -1 | cut -d: -f1)"
    second_line="$(grep -nF "$second" "$file" | head -1 | cut -d: -f1)"
    if [ -n "$first_line" ] && [ -n "$second_line" ] && [ "$first_line" -lt "$second_line" ]; then
        pass "$label"
    else
        fail "$label"
    fi
}

ROOT="$(mktemp -d /tmp/seeded-gate4.XXXXXX)"
trap 'rm -rf "$ROOT"' EXIT

for shape in base seed faithful faithful_empirical faithful_experimental; do
    args=(--variant finance --assemble-only --no-model-probe)
    [ "$shape" = seed ] && args+=(--seed)
    [ "$shape" = faithful ] && args+=(--faithful)
    [ "$shape" = faithful_empirical ] && args+=(--faithful --ext empirical)
    if [ "$shape" = faithful_experimental ]; then
        args=(--variant llm_cognition --faithful --assemble-only --no-model-probe)
    fi
    if ! ./setup.sh "$ROOT/$shape" "${args[@]}" >/dev/null 2>&1; then
        fail "$shape assembly"
    else
        pass "$shape assembly"
    fi
done

BASE="$ROOT/base/docs/stage_4.md"
SEED="$ROOT/seed/docs/stage_4.md"
FAITHFUL="$ROOT/faithful/docs/stage_4.md"
FAITHFUL_EMPIRICAL="$ROOT/faithful_empirical/docs/stage_4.md"
FAITHFUL_EXPERIMENTAL="$ROOT/faithful_experimental/docs/stage_4.md"

expect_text "$BASE" "## Unseeded score-routing path" \
    "unseeded Gate 4 retains strategic score routing"
reject_text "$BASE" "### Seeded-mode override" \
    "unseeded Gate 4 has no seeded route"

for item in "$SEED" "$FAITHFUL"; do
    label="$(basename "$(dirname "$(dirname "$item")")")"
    expect_text "$item" "do not launch branch-manager at Gate 4" \
        "$label Gate 4 skips branch-manager"
    expect_text "$item" 'The aggregate score and `ADVANCE / REVISE / MAJOR REWORK / ABANDON` label are diagnostic' \
        "$label aggregate score is diagnostic"
    expect_order "$item" "Launch both scorers in parallel" 'Read `seeded` from' \
        "$label launches both scorers before seeded routing"
    expect_text "$item" 'Read `output/stage4/triage_vN.md` as well as both scorer reports.' \
        "$label consumes triaged and scorer correctness findings"
    expect_text "$item" "return that claim to its existing owning audit" \
        "$label correctness challenges re-enter their owning audit"
    expect_text "$item" 'does not become a correctness defect merely because triager assigned `[FIX]`' \
        "$label does not promote strategic triage to correctness"
    expect_text "$item" "Otherwise, proceed to Stage 5" \
        "$label advances when correctness is clear"
    reject_text "$item" "Plateau ship rule" \
        "$label has no score-plateau wait"
    reject_text "$item" "Gate 4 ABANDON" \
        "$label has no aggregate-score abandon route"
    reject_text "$item" "{{SEED_OVERRIDE_STAGE_4_GATE_4}}" \
        "$label resolves the Gate 4 override"
done

for shape in seed faithful; do
    for runtime_doc in AGENTS.md GEMINI.md; do
        runtime="$ROOT/$shape/$runtime_doc"
        expect_text "$runtime" "Gate 4 has authorized Stage 5 under the configured route" \
            "$shape $runtime_doc waits for the configured Gate 4 route"
        expect_text "$runtime" "On a seeded run, the score is diagnostic" \
            "$shape $runtime_doc preserves diagnostic score routing"
        reject_text "$runtime" "scorer hasn't returned ADVANCE" \
            "$shape $runtime_doc has no stale ADVANCE-only prerequisite"
        reject_text "$runtime" "If the score is below the advance threshold, the paper does not advance. Period." \
            "$shape $runtime_doc has no stale universal score floor"
    done
    for agent_doc in \
        .claude/agents/paper-writer.md \
        .codex/agents/paper-writer.toml \
        .gemini/agents/paper-writer.md \
        .grok/agents/paper-writer.md \
        .opencode/agents/paper-writer.md; do
        expect_text "$ROOT/$shape/$agent_doc" \
            "after Gate 4 authorizes Stage 5 under the configured route" \
            "$shape $agent_doc uses route-neutral Stage 5 authorization"
        reject_text "$ROOT/$shape/$agent_doc" "after the scorer returns ADVANCE" \
            "$shape $agent_doc has no stale ADVANCE-only launch rule"
    done
done

expect_text "$FAITHFUL" '`faithful-drift-auditor` remains binding' \
    "faithful Gate 4 retains independent drift audit"
expect_text "$FAITHFUL" 'current `output/stage2/theory_draft_vN.md`' \
    "faithful Gate 4 passes the current theory draft to drift audit"
expect_text "$FAITHFUL_EMPIRICAL" '`pipeline_state.json:stage3a_analysis_path`' \
    "faithful empirical Gate 4 passes contribution-bearing empirical results"
expect_text "$FAITHFUL_EXPERIMENTAL" '`pipeline_state.json:stage3b_results_path`' \
    "faithful experimental Gate 4 passes contribution-bearing experiment results"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    'do not substitute a guessed canonical sibling, scorer, triage, audit, or self-attack report merely because it is newer.' \
    "faithful drift auditor cannot fall back to the newest scorer artifact"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    'check the current theory draft and every applicable Stage 3a/3b evidence result' \
    "faithful drift auditor checks seed-fixed numbers across Gate 4 evidence"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    "each evidence artifact's own headline/contribution claims, named mechanism" \
    "faithful drift auditor checks contribution framing inside Gate 4 evidence"
expect_text "$FAITHFUL_EMPIRICAL" 'never alter the finding to match the seed' \
    "faithful empirical Gate 4 preserves verified discrepant evidence"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    'Never instruct the orchestrator to change an actual finding to match the seed.' \
    "faithful drift remedy cannot overwrite honest findings"
expect_text "$ROOT/faithful/docs/stage_6.md" 'never rewrite evidence to the seed value' \
    "faithful Gate 5 also preserves verified discrepant evidence"
expect_text "$ROOT/faithful_empirical/docs/stage_6.md" \
    'every applicable current Stage 3a empirical-analysis and Stage 3b experiment-result artifact' \
    "faithful Gate 5 receives verified evidence artifacts"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    'Agreement with the contract is not enough when verified evidence differs.' \
    "faithful Gate 5 catches reversion to a disproved seed value"
expect_text "$ROOT/faithful_empirical/.claude/agents/empiricist.md" \
    'Never replace or omit a verified finding to match the seed.' \
    "faithful producer injection preserves verified evidence"
reject_text "$ROOT/faithful_empirical/.claude/agents/empiricist.md" \
    "the seed's stated result remains the contribution" \
    "faithful producer injection has no stale result freeze"
expect_text "$ROOT/faithful/CLAUDE.md" \
    'Fidelity fixes the research direction and contribution framing, not the answer.' \
    "faithful orchestrator doctrine preserves scientific answers"
reject_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" \
    'silently replaced in the abstract' \
    "faithful drift criteria are not abstract-only at Gate 4"
expect_text "$ROOT/faithful/.claude/agents/faithful-drift-auditor.md" "Gate 4 (before advancing to Stage 5)" \
    "faithful agent description names the new advance point"
reject_text "$ROOT/faithful/CLAUDE.md" "Gate 4 ABANDON" \
    "faithful runtime guidance has no stale Gate 4 halt"
reject_text "$ROOT/faithful/CLAUDE.md" "Branch-manager RESTART/REGENERATE" \
    "faithful runtime guidance has no stale Gate 4 branch-manager halt"
for shape in seed faithful; do
    reject_text "$ROOT/$shape/CLAUDE.md" '| Scorer plateau in the REVISE band' \
        "$shape core has no universal scorer-plateau route"
    reject_text "$ROOT/$shape/CLAUDE.md" '| Theory scored ABANDON' \
        "$shape core has no universal scorer-abandon route"
done

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All seeded Gate 4 assembly checks passed."
