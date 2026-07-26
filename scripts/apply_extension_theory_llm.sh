#!/bin/bash
set -e

# NOTE on --mode interaction (forward-compat gap):
# This script does NOT receive setup.sh's MODE_BODIES_OVERLAY or
# MODE_VOCAB_OVERLAY. Extension agents (experiment-designer, experiment-reviewer)
# are loaded with `--bodies-dir extensions/theory_llm/agent_bodies` and no
# `--shared-bodies-dir`, so the mode-overlay shadowing path does not reach
# them. If a future --mode wants mode-conditional behavior in a theory_llm
# agent, thread MODE_BODIES_OVERLAY/MODE_VOCAB_OVERLAY through here as
# additional positionals and append them to the assemble_* calls below.

TEMPLATE_ROOT="$1"
PROJECT_ROOT="$2"
AGENTS_OUT="$3"
CODEX_AGENTS_OUT="$4"
GEMINI_AGENTS_OUT="$5"
SKILLS_OUT="$6"
LOCAL="$7"
MODEL_OVERRIDE_ARG=()
if [ -n "$8" ]; then
    MODEL_OVERRIDE_ARG=(--model-override "$8")
fi
# $9 = base variant vocab path (templates/agents/{variant}/vocab.json).
# Layering mirrors the base assemblers: shared defaults first, then variant.
EXT_BASE_VOCAB="${9}"
EXT_VOCAB_ARGS=()
EXT_SHARED_VOCAB="$TEMPLATE_ROOT/templates/agent_bodies/shared/vocab.json"
[ -f "$EXT_SHARED_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_SHARED_VOCAB")
[ -n "$EXT_BASE_VOCAB" ] && [ -f "$EXT_BASE_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_BASE_VOCAB")

EXT_ROOT="$TEMPLATE_ROOT/extensions/theory_llm"

cp "$EXT_ROOT/llm_client.py" "$PROJECT_ROOT/"

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
    --output-dir "$CODEX_AGENTS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    "${EXT_VOCAB_ARGS[@]}" \
    --output-dir "$GEMINI_AGENTS_OUT" \
    "${MODEL_OVERRIDE_ARG[@]}"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
    --output-dir "$SKILLS_OUT"

mkdir -p "$PROJECT_ROOT/output/stage3b/figures"

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

if [ "$LOCAL" = "0" ] && [ -d "$PROJECT_ROOT/.venv" ]; then
    # Target the project venv created by setup.sh (deployed pipeline uses bare
    # python3). Dep list single-sourced in extensions/theory_llm/deps.txt (also
    # read by update.sh's venv bootstrap). Guarded on venv existence so a failed
    # venv creation in setup.sh doesn't add a second doomed install here.
    uv pip install --python "$PROJECT_ROOT/.venv" -r "$TEMPLATE_ROOT/extensions/theory_llm/deps.txt" -q 2>/dev/null \
        || echo "Note: theory_llm deps failed; install manually: source $PROJECT_ROOT/.venv/bin/activate && uv pip install openai python-dotenv"
fi
