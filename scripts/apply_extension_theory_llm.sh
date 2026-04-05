#!/bin/bash
set -e

TEMPLATE_ROOT="$1"
PROJECT_ROOT="$2"
AGENTS_OUT="$3"
SKILLS_OUT="$4"
LOCAL="$5"

EXT_ROOT="$TEMPLATE_ROOT/extensions/theory_llm"

cp "$EXT_ROOT/llm_client.py" "$PROJECT_ROOT/"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
    --metadata "$EXT_ROOT/agent_metadata/agents.json" \
    --bodies-dir "$EXT_ROOT/agent_bodies" \
    --output-dir "$AGENTS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
    --output-dir "$SKILLS_OUT"

mkdir -p "$PROJECT_ROOT/output/stage3b_experiments"

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

if [ "$LOCAL" = "0" ]; then
    uv pip install openai python-dotenv -q 2>/dev/null \
        || echo "Note: install deps manually: uv pip install openai python-dotenv"
fi
