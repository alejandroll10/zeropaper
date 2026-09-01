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
assemble macro_empirical --variant macro --ext empirical
assemble experiments --variant llm_cognition --mode measurement-first
assemble combined --variant finance --ext empirical --ext theory_llm
assemble report --variant finance --mode report
assemble macro_report --variant macro --mode report
assemble manual --variant finance --manual
assemble manual_empirical --variant finance --manual --ext empirical
assemble manual_empirical_first --variant finance --manual --mode empirical-first
assemble manual_measurement_first --variant llm_cognition --manual --mode measurement-first
assemble manual_combined --variant finance --manual --ext empirical --ext theory_llm

for shape in finance empirical experiments; do
    P="$ROOT/$shape"
    [ -x "$P/code/utils/results_pipeline/results_pipeline.py" ] \
        && pass "$shape results utility installed" || fail "$shape results utility installed"
    [ -f "$P/code/utils/results_pipeline/results-v1.schema.json" ] \
        && pass "$shape result schema installed" || fail "$shape result schema installed"
    [ -f "$P/code/utils/results_pipeline/run-plan-v1.schema.json" ] \
        && pass "$shape run-plan schema installed" || fail "$shape run-plan schema installed"
    [ -x "$P/code/utils/results_pipeline/analysis_contract.py" ] \
        && pass "$shape analysis-contract helper installed" \
        || fail "$shape analysis-contract helper installed"
    [ -f "$P/code/utils/results_pipeline/analysis-contract-v1.schema.json" ] \
        && [ -f "$P/code/utils/results_pipeline/analysis-execution-v1.schema.json" ] \
        && pass "$shape empirical lineage schemas installed" \
        || fail "$shape empirical lineage schemas installed"
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
    expect_text "$P/docs/results_evidence.md" "results.receipt.snapshot.json" \
        "$shape documentary receipt snapshots use a non-lifecycle suffix"
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
    expect_text "$P/.claude/agents/paper-writer.md" \
        'Every computed empirical or experimental claim must instead trace to an active rendered exhibit' \
        "$shape paper writer separates theoretical and computed provenance"
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

for shape in experiments combined; do
    jq -e 'has("stage3b_theory_version") and has("stage3b_results_path")
            and has("stage3b_result_receipt")
            and .stage3b_theory_version == null
            and .stage3b_results_path == null
            and .stage3b_result_receipt == null' \
        "$ROOT/$shape/process_log/pipeline_state.json" >/dev/null \
        && pass "$shape Stage 3b evidence triad initialized" \
        || fail "$shape Stage 3b evidence triad initialized"
done

# Extension agents are not assembled for Grok (tracked global extension-runtime
# limit); verify every runtime that currently supports extension agents.
for runtime in .claude .codex .gemini .opencode; do
    [ -f "$ROOT/macro_empirical/$runtime/agents/identification-designer.md" ] \
        || [ -f "$ROOT/macro_empirical/$runtime/agents/identification-designer.toml" ] \
        && pass "macro empirical $runtime identification designer installed" \
        || fail "macro empirical $runtime identification designer installed"
    [ -f "$ROOT/macro_empirical/$runtime/agents/identification-auditor.md" ] \
        || [ -f "$ROOT/macro_empirical/$runtime/agents/identification-auditor.toml" ] \
        && pass "macro empirical $runtime identification auditor installed" \
        || fail "macro empirical $runtime identification auditor installed"
done
expect_text "$ROOT/macro_empirical/.claude/agents/identification-designer.md" \
    'SVAR' "macro designer carries macro identification toolkit"
expect_text "$ROOT/macro_empirical/.claude/agents/identification-auditor.md" \
    'lpiv-horizon-weakness-hidden' "macro auditor carries named macro failure modes"
expect_text "$ROOT/macro_empirical/.claude/agents/identification-auditor.md" \
    'lucas-critique-regime-invariance' "macro auditor checks regime-invariant counterfactuals"
expect_text "$ROOT/macro_empirical/.claude/agents/polish-identification.md" \
    'act as a macroeconometrics referee' \
    "macro rendered-paper identification audit is domain-calibrated"
expect_text "$ROOT/macro_empirical/.claude/agents/polish-identification.md" \
    'Sign restrictions often set-identify' \
    "macro polish audit checks point-versus-set claims"
expect_text "$ROOT/macro_empirical/.claude/agents/polish-identification.md" \
    'regime-invariance and general-equilibrium feedback' \
    "macro polish audit checks counterfactual identification"
expect_text "$ROOT/macro_empirical/docs/stage_3a_empirical.md" \
    'N/A — no design feasible from the available variation' \
    "macro infeasible design has an explicit route"

jq -e '.kind == "manual_evidence_state" and .loops.evidence == {"round":0,"cap":3}' \
    "$ROOT/manual/process_log/manual_evidence_state.json" >/dev/null \
    && pass "manual evidence loop initialized" || fail "manual evidence loop initialized"
jq -e '.kind == "result_registry" and .active == [] and .pending == []' \
    "$ROOT/manual/process_log/results_registry.json" >/dev/null \
    && pass "manual result registry initialized" || fail "manual result registry initialized"
[ ! -e "$ROOT/manual/process_log/pipeline_state.json" ] \
    && pass "manual autonomous state remains absent" || fail "manual autonomous state remains absent"
expect_text "$ROOT/manual/CLAUDE.md" 'manual_evidence_state.json' \
    "manual runtime points to evidence state"
expect_text "$ROOT/manual/docs/stage_9.md" 'manual-stage9-final' \
    "manual polish chain binds a final evidence checkpoint"
expect_text "$ROOT/manual/docs/results_evidence.md" 'structural preflight' \
    "manual contract distinguishes schema from runtime validation"
expect_text "$ROOT/manual/.claude/agents/evidence-auditor.md" \
    'process_log/manual_evidence_state.json' \
    "manual agent surfaces core bypasses in its returned report"
expect_text "$ROOT/manual/docs/core_bypass.md" \
    'process_log/manual_evidence_state.json' \
    "manual core-bypass procedure does not invent a hidden ledger"
expect_text "$ROOT/manual/docs/core_bypass.md" \
    'returned report and do not create a' \
    "manual orchestrator bypass branch explicitly forbids the ledger"
expect_text "$ROOT/manual/.claude/agents/paper-writer.md" \
    'Manual computed evidence is registry-addressed, not stage-addressed' \
    "manual paper writer discovers active registry evidence"
expect_text "$ROOT/manual/.claude/agents/evidence-auditor.md" \
    'never infer completeness from Stage 2b/3a/3b directory names' \
    "manual evidence auditor accepts free-form output namespaces"
reject_text "$ROOT/manual/.claude/agents/paper-writer.md" \
    'No numerical claims outside rendered Stage 2b / 3a / 3b exhibits' \
    "manual paper writer does not require autonomous stage directories"

for shape in manual manual_empirical manual_empirical_first manual_measurement_first manual_combined; do
    expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        'Manual computed evidence is registry-addressed, not stage-addressed' \
        "$shape paper writer uses the manual registry contract"
    expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        '## Framing' \
        "$shape paper writer retains framing guidance"
    expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        '## Paper structure' \
        "$shape paper writer retains section guidance"
    expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        '## Style rules (mandatory)' \
        "$shape paper writer retains style guidance"
    expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        'Define every acronym at first use' \
        "$shape paper writer retains acronym guidance"
    expect_text "$ROOT/$shape/.claude/agents/idea-reviewer.md" \
        '1. **[Approach name]**' \
        "$shape idea reviewer retains its ranked recommendation schema"
    reject_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        'pipeline_state.json:stage3a_analysis_path' \
        "$shape paper writer has no autonomous Stage 3a pointer"
    reject_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
        'pipeline_state.json:stage3b_results_path' \
        "$shape paper writer has no autonomous Stage 3b pointer"
    for agent in polish-consistency polish-numerics polish-identification; do
        expect_text "$ROOT/$shape/.claude/agents/$agent.md" \
            'Manual-source override' \
            "$shape $agent resolves evidence from active receipts"
    done
    reject_text "$ROOT/$shape/.claude/agents/polish-consistency.md" \
        'pipeline_state.json:stage3a_analysis_path' \
        "$shape consistency audit has no autonomous Stage 3a input"
    reject_text "$ROOT/$shape/.claude/agents/polish-numerics.md" \
        'pipeline_state.json:stage3b_results_path' \
        "$shape numerics audit has no autonomous Stage 3b input"
    reject_text "$ROOT/$shape/.claude/agents/polish-identification.md" \
        'pipeline_state.json:stage3a_analysis_path' \
        "$shape identification audit has no autonomous Stage 3a input"
    case "$shape" in
        manual|manual_empirical|manual_combined)
            expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
                '### `model.tex`' "$shape paper writer retains model guidance"
            expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
                '### `results.tex`' "$shape paper writer retains result-section guidance"
            ;;
        manual_empirical_first)
            for section in data identification results mechanism robustness; do
                expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
                    "### \`$section.tex\`" \
                    "$shape paper writer retains $section guidance"
            done
            ;;
        manual_measurement_first)
            expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
                '### `model.tex`' "$shape paper writer retains model guidance"
            expect_text "$ROOT/$shape/.claude/agents/paper-writer.md" \
                '### `experiments.tex`' "$shape paper writer retains experiment guidance"
            expect_text "$ROOT/$shape/.claude/agents/experiment-reviewer.md" \
                '## Two invocations — read this first' \
                "$shape experiment reviewer retains plan-review routing"
            expect_text "$ROOT/$shape/.claude/agents/experiment-reviewer.md" \
                '# Design Review' \
                "$shape experiment reviewer retains plan-review output schema"
            expect_text "$ROOT/$shape/.claude/agents/experiment-reviewer.md" \
                'Manual-source override' \
                "$shape experiment reviewer resolves evidence from active receipts"
            expect_text "$ROOT/$shape/.claude/agents/experiment-reviewer.md" \
                'Any later instruction in this body that assumes an autonomous stage' \
                "$shape experiment reviewer makes autonomous design paths inapplicable"
            ;;
    esac
done

# Any callable manual agent that still mentions an autonomous result namespace
# must carry the uniform override that makes those paths inapplicable and
# resolves evidence from caller inputs plus active receipts.  Scan every
# runtime package so a mode overlay or runtime-specific assembler cannot
# silently reintroduce a pointer-only consumer.
if python3 -I - "$ROOT" \
    manual manual_empirical manual_empirical_first manual_measurement_first manual_combined <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
stage_source = re.compile(
    r"pipeline_state\.json:stage(?:2b|3a|3b)_|output/stage(?:2b|3a|3b)(?:/|`)",
)
failures = []
for shape in sys.argv[2:]:
    project = root / shape
    agent_roots = (
        project / ".claude" / "agents",
        project / ".codex" / "agents",
        project / ".gemini" / "agents",
        project / ".grok" / "agents",
        project / ".opencode" / "agents",
    )
    for agent_root in agent_roots:
        if not agent_root.is_dir():
            continue
        for path in agent_root.iterdir():
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if stage_source.search(text) and "Manual-source override" not in text:
                failures.append(f"{shape}:{path.relative_to(project)}")
if failures:
    raise SystemExit("manual stage source without registry override: " + ", ".join(failures))
PY
then
    pass "every manual result-consuming agent carries the registry source override"
else
    fail "every manual result-consuming agent carries the registry source override"
fi

for shape in manual manual_empirical manual_empirical_first manual_measurement_first manual_combined; do
    expect_text "$ROOT/$shape/.claude/agents/theory-explorer.md" \
        'Manual-source override' \
        "$shape theory producer uses caller/receipt paths"
    reject_text "$ROOT/$shape/.claude/agents/theory-explorer.md" \
        'Atomically update the stage report/receipt pointers' \
        "$shape theory producer does not invent a stage pointer"
done
for shape in manual_empirical manual_empirical_first manual_combined; do
    expect_text "$ROOT/$shape/.claude/agents/empiricist.md" \
        'Manual-source override' \
        "$shape empirical producer uses caller/receipt paths"
    reject_text "$ROOT/$shape/.claude/agents/empiricist.md" \
        'Atomically update the stage report/receipt pointers' \
        "$shape empirical producer does not invent a stage pointer"
done
expect_text "$ROOT/manual_measurement_first/.claude/agents/experiment-designer.md" \
    'Manual-source override' \
    "manual measurement producer uses caller/receipt paths"
reject_text "$ROOT/manual_measurement_first/.claude/agents/experiment-designer.md" \
    'Atomically update the stage report/receipt pointers' \
    "manual measurement producer does not invent a stage pointer"
reject_text "$ROOT/manual_measurement_first/.claude/agents/experiment-designer.md" \
    'Stage 9 resolves them from `stage3b_result_receipt`' \
    "manual measurement producer does not name an autonomous Stage 3b pointer"
expect_text "$ROOT/manual_combined/.claude/agents/experiment-designer.md" \
    'Manual-source override' \
    "manual combined experiment producer uses caller/receipt paths"
expect_text "$ROOT/manual_combined/.claude/agents/experiment-reviewer.md" \
    'Manual-source override' \
    "manual combined experiment reviewer resolves evidence from active receipts"
reject_text "$ROOT/manual_combined/.claude/agents/experiment-designer.md" \
    'Stage 9 resolves them from `stage3b_result_receipt`' \
    "manual combined experiment producer has no autonomous Stage 3b pointer"

for shape in manual_empirical manual_empirical_first manual_combined; do
    [ ! -e "$ROOT/$shape/output/stage3a" ] \
        && pass "$shape does not bootstrap a Stage 3a namespace" \
        || fail "$shape does not bootstrap a Stage 3a namespace"
done
[ ! -e "$ROOT/manual_measurement_first/output/stage3b" ] \
    && pass "manual measurement-first does not bootstrap a Stage 3b namespace" \
    || fail "manual measurement-first does not bootstrap a Stage 3b namespace"
[ ! -e "$ROOT/manual_combined/output/stage3b" ] \
    && pass "manual combined does not bootstrap a Stage 3b namespace" \
    || fail "manual combined does not bootstrap a Stage 3b namespace"

expect_text "$ROOT/manual_measurement_first/docs/stage_9.md" \
    'process_log/results_registry.json' \
    "manual Stage 9 resolves experiment evidence from the registry"
reject_text "$ROOT/manual_measurement_first/docs/stage_9.md" \
    'pipeline_state.json:stage3b_result' \
    "manual Stage 9 has no autonomous Stage 3b pointer"
reject_text "$ROOT/manual_measurement_first/docs/results_evidence.md" \
    'activate, move the stage pointer' \
    "manual evidence lifecycle has no stage-pointer handoff"

for shape in manual_measurement_first manual_combined; do
for agent_path in \
    .claude/agents/polish-experiments.md \
    .codex/agents/polish-experiments.toml \
    .gemini/agents/polish-experiments.md \
    .opencode/agents/polish-experiments.md; do
    expect_text "$ROOT/$shape/$agent_path" \
        'Manual-source override' \
        "manual $agent_path resolves active experimental receipts"
    reject_text "$ROOT/$shape/$agent_path" \
        'pipeline_state.json:stage3b_' \
        "manual $agent_path has no autonomous Stage 3b pointer"
    reject_text "$ROOT/$shape/$agent_path" \
        'If `output/stage3b/` does not exist' \
        "manual $agent_path does not infer applicability from a stage directory"
done
done

expect_text "$ROOT/macro_report/.claude/agents/polish-identification.md" \
    'SVAR / proxy-SVAR' \
    "macro report identification audit covers macro designs"
expect_text "$ROOT/macro_report/.claude/agents/polish-identification.md" \
    'Point identification cannot be claimed' \
    "macro report audit distinguishes point from set identification"
expect_text "$ROOT/macro_report/.claude/agents/polish-identification.md" \
    'regime-invariance/Lucas-critique analysis' \
    "macro report audit checks policy-counterfactual invariance"
reject_text "$ROOT/macro_report/.claude/agents/polish-identification.md" \
    'Feng-Giglio-Xiu' \
    "macro report audit excludes finance-only factor diagnostics"
expect_text "$ROOT/macro_empirical/.claude/agents/polish-identification.md" \
    'authoritative design artifact supplied above' \
    "macro theory-first identification polish uses the Stage 3a design source"
reject_text "$ROOT/macro_empirical/.claude/agents/polish-identification.md" \
    "Stage 1 design's" \
    "macro theory-first polish does not hard-code a missing Stage 1 artifact"

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
