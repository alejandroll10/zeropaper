#!/bin/bash
set -e

# NOTE on --mode interaction (forward-compat gap):
# This script does NOT receive setup.sh's MODE_BODIES_OVERLAY or
# MODE_VOCAB_OVERLAY. Extension agents (experiment-designer, experiment-reviewer,
# polish-experiments) are loaded with `--bodies-dir extensions/theory_llm/agent_bodies`
# and no `--shared-bodies-dir`, so the mode-overlay shadowing path does not reach
# them. If a future --mode wants mode-conditional behavior in a theory_llm
# agent, thread MODE_BODIES_OVERLAY/MODE_VOCAB_OVERLAY through here as
# additional positionals and append them to the assemble_* calls below.
#
# NOTE on per-variant metadata (forward-compat gap): the assemble_* calls below
# hardcode agent_metadata/agents.json, while setup.sh's model-heal emitter probes
# shared_agents.json / ${VARIANT}_agents.json / agents.json. A future
# extensions/theory_llm/agent_metadata/{variant}_agents.json would land in the
# heal config but never be assembled into an agent file — if per-variant
# theory_llm agents are ever added, loop the metadata paths here the way the
# empirical applier does.

TEMPLATE_ROOT="$1"
PROJECT_ROOT="$2"
AGENTS_OUT="$3"
CODEX_AGENTS_OUT="$4"
GEMINI_AGENTS_OUT="$5"
OPENCODE_AGENTS_OUT="$6"
SKILLS_OUT="$7"
ASSEMBLE_ONLY="$8"
MODEL_OVERRIDE_ARG=()
if [ -n "$9" ]; then
    MODEL_OVERRIDE_ARG=(--model-override "$9")
fi
# $10 = base variant vocab path (templates/agents/{variant}/vocab.json).
# Layering mirrors the base assemblers: shared defaults first, then variant.
EXT_BASE_VOCAB="${10}"
EXT_VOCAB_ARGS=()
EXT_SHARED_VOCAB="$TEMPLATE_ROOT/templates/agent_bodies/shared/vocab.json"
[ -f "$EXT_SHARED_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_SHARED_VOCAB")
[ -n "$EXT_BASE_VOCAB" ] && [ -f "$EXT_BASE_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_BASE_VOCAB")

EXT_ROOT="$TEMPLATE_ROOT/extensions/theory_llm"

# shellcheck source=/dev/null
source "$TEMPLATE_ROOT/scripts/setup/ownership.sh"
P="$PROJECT_ROOT"
infrastructure_copy_file 1100 "$EXT_ROOT/llm_client.py" "llm_client.py"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    "${EXT_VOCAB_ARGS[@]}" \
    --output-dir "$AGENTS_OUT" \
    "${MODEL_OVERRIDE_ARG[@]}"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    "${EXT_VOCAB_ARGS[@]}" \
    --output-dir "$CODEX_AGENTS_OUT" \
    "${MODEL_OVERRIDE_ARG[@]}"

python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    "${EXT_VOCAB_ARGS[@]}" \
    --output-dir "$GEMINI_AGENTS_OUT" \
    "${MODEL_OVERRIDE_ARG[@]}"

python3 "$TEMPLATE_ROOT/scripts/assemble_opencode_agents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    "${EXT_VOCAB_ARGS[@]}" \
    --output-dir "$OPENCODE_AGENTS_OUT" \
    "${MODEL_OVERRIDE_ARG[@]}"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
    --output-dir "$SKILLS_OUT"

bootstrap_dir "output/stage3b/figures"

# Amend the deployed Stage 9 doc: theory_llm adds a ninth polish agent.
# Guarded (grep) so update.sh re-runs don't append twice; skipped when the
# deploy has no stage_9.md (e.g. --mode report prunes the pipeline docs).
STAGE9_DOC="$PROJECT_ROOT/docs/stage_9.md"
if [ -f "$STAGE9_DOC" ] && ! grep -q "polish-experiments" "$STAGE9_DOC"; then
    cat >> "$STAGE9_DOC" <<'STAGE9EOF'

## theory_llm extension: ninth polish agent — `polish-experiments`

This run has `--ext theory_llm`, which adds **`polish-experiments`** to Stage 9. Read the eight-agent lists above as nine-agent lists:

- **Launch** it in the same parallel batch, with the same `loops.polish.round` value. Pass it `paper/main.tex`, the included sections, the IA files when non-empty, and `output/stage3b/` (it reads `experiment_design.md`, `experiment_results.md` and any `experiment_results_vN.md`, `experiment_code/`, `raw_results/`).
- **It writes** `output/polish_experiments_r{N}.md`; include that path in the triager's input list alongside the other eight reports. Its findings triage on the same Apply/Investigate/Drop rules, and its correction rows belong to pass 1 of the two-pass paper-writer application.
- **Ownership:** paper↔raw-results agreement for experimental numbers, stimulus-contamination status, model snapshot pinning and decoding-parameter disclosure, error-bar integrity across stimuli and sampled runs, scope honesty of capability claims, artifact reproducibility (code + seeds regenerate the battery). It does **not** own experimental design quality (experiment-reviewer, Stage 3b), formula derivations (polish-formula), non-experimental numbers (polish-numerics), or citation faithfulness (polish-bibliography). The deliberate overlap with polish-numerics/polish-consistency on stage3b-grounded prose numbers is fine — the triager dedupes by anchor.
STAGE9EOF
fi

ENV_FILE="$PROJECT_ROOT/.env"
if ! grep -q 'UF_API_KEY' "$ENV_FILE" 2>/dev/null; then
    cat >> "$ENV_FILE" <<'ENVEOF'

# LLM experiment backends (set one or both)
# UF NaviGator (free for UF researchers): https://api.ai.it.ufl.edu
UF_API_KEY=your-key-here
# DeepInfra (pay-per-token): https://deepinfra.com
DEEPINFRA_TOKEN=your-key-here
ENVEOF
fi
