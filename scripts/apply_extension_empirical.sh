#!/bin/bash
set -e

TEMPLATE_ROOT="$1"
PROJECT_ROOT="$2"
AGENTS_OUT="$3"
CODEX_AGENTS_OUT="$4"
SKILLS_OUT="$5"
AGENT_DIR="$6"
LOCAL="$7"

EXT_ROOT="$TEMPLATE_ROOT/extensions/empirical"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
    --output-dir "$SKILLS_OUT"

if [ -f "$EXT_ROOT/agent_metadata/shared_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        --output-dir "$AGENTS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        --output-dir "$CODEX_AGENTS_OUT"
fi

if [ -f "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        --output-dir "$AGENTS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        --output-dir "$CODEX_AGENTS_OUT"
else
    echo "  ⚠ No empiricist agent for variant '${AGENT_DIR}' — Stage 3b will be skipped at runtime"
fi

mkdir -p "$PROJECT_ROOT/code/utils"
cp "$EXT_ROOT/utils/"*.py "$PROJECT_ROOT/code/utils/"
cp "$EXT_ROOT/utils/"*.sh "$PROJECT_ROOT/code/utils/" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/code/utils/"*.sh 2>/dev/null || true
touch "$PROJECT_ROOT/code/utils/__init__.py"

mkdir -p "$PROJECT_ROOT/output/stage3b"

ENV_FILE="$PROJECT_ROOT/.env"
if ! grep -q 'FRED_API_KEY' "$ENV_FILE" 2>/dev/null; then
    cat >> "$ENV_FILE" <<'ENVEOF'
# FRED API key (free): https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your-key-here

# WRDS credentials: https://wrds-www.wharton.upenn.edu/
WRDS_USER=your-username
WRDS_PASS=your-password

# SEC EDGAR identity (required, no API key needed)
SEC_EDGAR_NAME=Your Name
SEC_EDGAR_EMAIL=your@email.edu
ENVEOF
fi

if [ "$LOCAL" = "0" ]; then
    uv pip install pandas numpy statsmodels scipy fredapi pandas-datareader wrds edgartools openassetpricing gdown python-dotenv -q 2>/dev/null \
        || echo "Note: install empirical deps manually: uv pip install pandas numpy statsmodels scipy fredapi pandas-datareader wrds edgartools openassetpricing gdown python-dotenv"
fi
