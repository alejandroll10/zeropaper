#!/bin/bash
# Cross-shape assembly regression for the computed-results evidence contract.
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }
expect_text() { grep -Fq -- "$2" "$1" && pass "$3" || fail "$3"; }
reject_text() { grep -Fq -- "$2" "$1" && fail "$3" || pass "$3"; }
expect_count_at_least() {
    local count
    count="$(grep -Fc -- "$2" "$1")"
    [ "$count" -ge "$3" ] && pass "$4" || fail "$4"
}

ROOT="$(mktemp -d /tmp/results-evidence-assembly-test.XXXXXX)"
trap 'rm -rf "$ROOT"' EXIT

assemble() {
    local name="$1"
    shift
    ./setup.sh "$ROOT/$name" --assemble-only --no-model-probe "$@" >/dev/null 2>&1 \
        && pass "$name assembly" || fail "$name assembly"
}

assemble finance --variant finance
assemble empirical --variant finance --ext empirical
assemble experiments --variant llm_cognition --mode measurement-first
assemble combined --variant finance --ext empirical --ext theory_llm
assemble report --variant finance --mode report

for shape in finance empirical experiments; do
    P="$ROOT/$shape"
    [ -x "$P/code/utils/results_pipeline/results_pipeline.py" ] \
        && pass "$shape results utility installed" || fail "$shape results utility installed"
    [ -f "$P/code/utils/results_pipeline/results-v1.schema.json" ] \
        && pass "$shape result schema installed" || fail "$shape result schema installed"
    [ -f "$P/code/utils/results_pipeline/run-plan-v1.schema.json" ] \
        && pass "$shape run-plan schema installed" || fail "$shape run-plan schema installed"
    [ -f "$P/docs/results_evidence.md" ] \
        && pass "$shape evidence procedure installed" || fail "$shape evidence procedure installed"
    jq -e '.loops.evidence == {"round": 0, "cap": 3}' \
        "$P/process_log/pipeline_state.json" >/dev/null \
        && pass "$shape evidence loop initialized" || fail "$shape evidence loop initialized"
    jq -e '.stage2b_exploration_path == null and .stage2b_result_receipt == null' \
        "$P/process_log/pipeline_state.json" >/dev/null \
        && pass "$shape Stage 2b evidence pointers initialized" \
        || fail "$shape Stage 2b evidence pointers initialized"
    jq -e '.kind == "result_registry" and .registry_version == 1 and .active == [] and .pending == [] and .receipt_fingerprints == {}' \
        "$P/process_log/results_registry.json" >/dev/null \
        && pass "$shape result registry initialized" || fail "$shape result registry initialized"
    jq -e '([.infrastructure.dirs_replace[]?, .infrastructure.files_replace[]?]
            | index("process_log/results_registry.json")) == null' \
        "$P/.deploy_manifest.json" >/dev/null \
        && pass "$shape result registry remains mutable" || fail "$shape result registry remains mutable"
    jq -e '.infrastructure.dirs_replace | index("code/utils/results_pipeline")' \
        "$P/.deploy_manifest.json" >/dev/null \
        && pass "$shape utility replacement-owned" || fail "$shape utility replacement-owned"
    expect_text "$P/.gitignore" "process_log/.results_registry.update.tmp" \
        "$shape updater registry temporary ignored"
    expect_text "$P/.gitignore" "output/**/.*.publish.*" \
        "$shape result publication temporaries ignored"
    for agent in \
        .claude/agents/evidence-auditor.md \
        .codex/agents/evidence-auditor.toml \
        .gemini/agents/evidence-auditor.md \
        .grok/agents/evidence-auditor.md \
        .opencode/agents/evidence-auditor.md; do
        [ -f "$P/$agent" ] && pass "$shape $agent installed" || fail "$shape $agent installed"
    done
    expect_text "$P/docs/stage_9.md" "stage9-final" "$shape final evidence checkpoint"
    expect_text "$P/docs/results_evidence.md" "--citation-summary" \
        "$shape paper receipt binds citation audit"
    expect_text "$P/docs/results_evidence.md" "prepare-audit" \
        "$shape freezes common audit input"
    expect_text "$P/docs/results_evidence.md" "--audit-input" \
        "$shape binding consumes frozen audit input"
    expect_text "$P/.claude/agents/evidence-auditor.md" "AUDIT_INPUT_DIGEST" \
        "$shape evidence verdict echoes frozen digest"
    expect_text "$P/.claude/agents/polish-bibliography.md" \
        "Checkpoint citation-provenance mode" \
        "$shape citation agent has checkpoint mode"
    expect_text "$P/.claude/agents/polish-bibliography.md" \
        '"sources"' "$shape citation inventory records per-key sources"
    expect_text "$P/.claude/agents/polish-bibliography.md" \
        '"occurrence_id"' "$shape citation inventory is occurrence-complete"
    expect_text "$P/.claude/agents/evidence-auditor.md" \
        'included_result_exhibits' "$shape exhibit inventory is dependency-derived"
    expect_text "$P/docs/stage_10.md" \
        'verify-paper --receipt process_log/paper_evidence.receipt.json --rerender' \
        "$shape completion re-verifies bound evidence"
    reject_text "$P/docs/stage_5.md" "Claim grounding (three-agent pipeline" \
        "$shape old claim pipeline absent"
    if (cd "$P" && python3 code/utils/results_pipeline/results_pipeline.py prepare-audit \
            --output output/evidence/skeleton_audit_input.json \
            --checkpoint skeleton-smoke >/dev/null 2>&1); then
        pass "$shape shipped skeleton enters evidence audit"
    else
        fail "$shape shipped skeleton enters evidence audit"
    fi
done

expect_text "$ROOT/finance/.claude/agents/theory-explorer.md" \
    "Paper-facing computation contract" "theory producer receives result contract"
expect_text "$ROOT/finance/.claude/agents/theory-explorer.md" \
    '--plan "$RESULT_PLAN"' "theory producer declares inputs before execution"
expect_text "$ROOT/finance/.claude/agents/theory-explorer.md" \
    '"${SUPERSEDES_ARGS[@]}" --' "theory producer passes explicit supersession array"
expect_text "$ROOT/finance/.claude/agents/theory-explorer.md" \
    "report path must appear in the run plan's \`artifacts\` array" \
    "theory producer declares its prose report as an artifact"
expect_text "$ROOT/finance/.claude/agents/theory-explorer.md" \
    'RESULTS_EXHIBIT_ROOT' "theory renderer uses staged exhibit root"
expect_text "$ROOT/finance/docs/stage_3_implications.md" \
    'stage2b_result_receipt' \
    "theory consumers resolve accepted Stage 2b receipt pointer"
expect_text "$ROOT/finance/docs/stage_2.md" \
    "every replacing re-fire is cumulative" \
    "theory re-fire preserves all accepted coverage in one receipt"
expect_text "$ROOT/empirical/.claude/agents/empiricist.md" \
    'RENDER_ENTRYPOINT' "empirical producer has separate renderer"
expect_text "$ROOT/empirical/.claude/agents/empiricist.md" \
    '"${SUPERSEDES_ARGS[@]}" --' "empirical producer passes explicit supersession array"
expect_text "$ROOT/empirical/.claude/agents/empiricist.md" \
    "report path must appear in the run plan's \`artifacts\` array" \
    "empirical producer declares its prose report as an artifact"
expect_text "$ROOT/empirical/docs/stage_3a_empirical.md" \
    "A partial bundle that covers only the newly targeted claim" \
    "empirical re-fire preserves all accepted coverage in one receipt"
expect_text "$ROOT/empirical/docs/stage_3a_empirical.md" \
    "mechanical verification leaves the candidate **pending**" \
    "empirical feasibility waits for substantive acceptance"
expect_text "$ROOT/empirical/docs/stage_2.md" \
    "empirical_analysis_vN_aK.md" \
    "empirical Gate 4 mirror allocates a fresh attempt namespace"
expect_text "$ROOT/experiments/.claude/agents/experiment-designer.md" \
    "experiment_results.receipt.json" "experiment producer has result receipt"
expect_text "$ROOT/experiments/.claude/agents/experiment-designer.md" \
    "report path must appear in the run plan's \`artifacts\` array" \
    "experiment producer declares its prose report as an artifact"
expect_text "$ROOT/experiments/.claude/agents/experiment-designer.md" \
    '"${SUPERSEDES_ARGS[@]}" --' "experiment producer passes explicit supersession array"
expect_text "$ROOT/experiments/docs/stage_3b_experiments.md" \
    "A partial new-experiment bundle cannot replace" \
    "experiment re-fire preserves all accepted coverage in one receipt"
expect_text "$ROOT/empirical/docs/stage_puzzle_triage.md" \
    'stage3a_theory_version`, `stage3b_theory_version' \
    "empirical pivot reset names downstream evidence versions"
expect_text "$ROOT/experiments/docs/stage_puzzle_triage.md" \
    'stage3a_theory_version`, `stage3b_theory_version' \
    "experimental pivot reset names downstream evidence versions"
expect_text "$ROOT/combined/docs/stage_puzzle_triage.md" \
    'stage3a_theory_version`, `stage3b_theory_version' \
    "combined pivot reset invalidates both evidence branches"
expect_text "$ROOT/combined/CLAUDE.md" \
    "Fresh-theory identity reset (mandatory and atomic)" \
    "combined runtime carries fresh-theory identity invariant"
for shape in finance empirical experiments combined; do
    P="$ROOT/$shape"
    expect_text "$P/docs/stage_0.md" \
        'set `theory_attempt = 1` and `theory_version = 1`' \
        "$shape fresh-problem entry restarts theory identity"
    expect_text "$P/docs/stage_0.md" \
        '`stage2b_theory_version`, `stage2_mechanism_version`, `stage2_design_version`, `stage3a_theory_version`, and `stage3b_theory_version`' \
        "$shape fresh-problem entry invalidates every acceptance branch"
    expect_text "$P/docs/stage_0.md" \
        'keep accepted report/receipt path pointers unchanged' \
        "$shape fresh-problem reset preserves cumulative-replacement pointers"
    expect_text "$P/docs/stage_0.md" \
        'retire every active Gate-3a feasibility receipt' \
        "$shape fresh-problem reset retires abandoned feasibility evidence"
    expect_text "$P/docs/stage_1.md" \
        'Apply the mandatory fresh-theory identity reset in `core.md`' \
        "$shape regeneration invokes the complete identity reset"
    expect_text "$P/docs/stage_puzzle_triage.md" \
        'BACK-TO-IDEA** | Return to Stage 1' \
        "$shape BACK-TO-IDEA route remains explicit"
    expect_count_at_least "$P/docs/stage_puzzle_triage.md" \
        'fresh-theory identity reset' 2 \
        "$shape BACK-TO-IDEA and PIVOT both reset theory identity"
    expect_count_at_least "$P/docs/stage_2.md" \
        'fresh-theory identity reset' 3 \
        "$shape Gate-2 caps and Gate-3 KNOWN cannot retain old acceptance"
done
for shape in empirical combined; do
    expect_text "$ROOT/$shape/docs/stage_3a_empirical.md" \
        'For non-seeded **FALSIFIED**' \
        "$shape feasibility falsification has a fresh-identity route"
    expect_text "$ROOT/$shape/docs/stage_3a_empirical.md" \
        'apply the fresh-theory identity reset in `core.md`' \
        "$shape feasibility falsification invalidates accepted versions"
    expect_text "$ROOT/$shape/docs/stage_3a_empirical.md" \
        'step 7.5 already activated `RESULT_RECEIPT`' \
        "$shape contradiction routing does not repeat activation"
    expect_text "$ROOT/$shape/docs/stage_2.md" \
        'Stage 3a step 7.5 is the sole activation/handoff owner' \
        "$shape Stage 3a injection delegates activation to step 7.5"
done
expect_text "$ROOT/empirical/CLAUDE.md" \
    'Every Gate-4 check requires equality against a non-null acceptance version' \
    "empirical resume blocks same-number stale evidence"
expect_text "$ROOT/experiments/CLAUDE.md" \
    'Every Gate-4 check requires equality against a non-null acceptance version' \
    "experimental resume blocks same-number stale evidence"
expect_text "$ROOT/combined/CLAUDE.md" \
    'Every Gate-4 check requires equality against a non-null acceptance version' \
    "combined resume blocks same-number stale evidence"

for runtime in .claude .codex .gemini .grok .opencode; do
    if find "$ROOT/empirical/$runtime/agents" -maxdepth 1 -type f \
        \( -name 'claim-enumerator*' -o -name 'claim-grounder*' -o -name 'claim-verifier*' \) \
        | grep -q .; then
        fail "empirical $runtime retained old claim agents"
    else
        pass "empirical $runtime old claim agents absent"
    fi
done

[ -x "$ROOT/report/code/utils/results_pipeline/results_pipeline.py" ] \
    && pass "report keeps shared utility" || fail "report keeps shared utility"
[ ! -e "$ROOT/report/.claude/agents/evidence-auditor.md" ] \
    && pass "report prunes paper evidence auditor" || fail "report prunes paper evidence auditor"
[ ! -e "$ROOT/report/docs/results_evidence.md" ] \
    && pass "report prunes paper evidence procedure" || fail "report prunes paper evidence procedure"

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All computed-results evidence assembly checks passed."
