#!/bin/bash
set -e

# Mode threading: positional $10 = MODE_BODIES_OVERLAY, $11 = MODE_VOCAB_OVERLAY,
# $12 = base variant vocab path. The variant vocab supplies default values for
# placeholders the extension bodies use (e.g. {{EMPIRICS_AUDITOR_MODE_BLOCK}}
# is empty in the base vocab and populated only by the empirical-first
# overlay). The base vocab MUST be passed even outside mode-empirical-first
# deploys, because the extension bodies now reference shared placeholders.
# Phase 6 added the EMPIRICS_AUDITOR_MODE_BLOCK placeholder to empirics-auditor;
# future mode-conditional content in extension agents follows the same
# pattern (placeholder in body + default in base vocab + override in mode
# overlay).

TEMPLATE_ROOT="$1"
PROJECT_ROOT="$2"
AGENTS_OUT="$3"
CODEX_AGENTS_OUT="$4"
GEMINI_AGENTS_OUT="$5"
SKILLS_OUT="$6"
AGENT_DIR="$7"
LOCAL="$8"
MODEL_OVERRIDE_ARG=()
if [ -n "$9" ]; then
    MODEL_OVERRIDE_ARG=(--model-override "$9")
fi
EXT_MODE_BODIES_OVERLAY="${10}"
EXT_MODE_VOCAB_OVERLAY="${11}"
EXT_BASE_VOCAB="${12}"

# Build vocab args: base variant vocab first, then mode overlay (last-write-wins).
EXT_VOCAB_ARGS=()
[ -n "$EXT_BASE_VOCAB" ] && [ -f "$EXT_BASE_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_BASE_VOCAB")
[ -n "$EXT_MODE_VOCAB_OVERLAY" ] && [ -f "$EXT_MODE_VOCAB_OVERLAY" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_MODE_VOCAB_OVERLAY")

# Build shared-bodies args: mode overlay first (first-match-wins for any
# {id}-core.md override). This dir does not currently host extension-agent
# overrides, but threading it now means a future mode override of an
# extension agent's body works without further apply_extension changes.
EXT_SHARED_ARGS=()
[ -n "$EXT_MODE_BODIES_OVERLAY" ] && [ -d "$EXT_MODE_BODIES_OVERLAY" ] && EXT_SHARED_ARGS+=(--shared-bodies-dir "$EXT_MODE_BODIES_OVERLAY")

EXT_ROOT="$TEMPLATE_ROOT/extensions/empirical"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
    --output-dir "$SKILLS_OUT"

if [ -f "$EXT_ROOT/agent_metadata/shared_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$CODEX_AGENTS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$GEMINI_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"
fi

if [ -f "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$CODEX_AGENTS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        --output-dir "$GEMINI_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"
else
    echo "  ⚠ No empiricist agent for variant '${AGENT_DIR}' — Stage 3a will be skipped at runtime"
fi

mkdir -p "$PROJECT_ROOT/code/utils"
cp "$EXT_ROOT/utils/"*.py "$PROJECT_ROOT/code/utils/"
cp "$EXT_ROOT/utils/"*.sh "$PROJECT_ROOT/code/utils/" 2>/dev/null || true
chmod +x "$PROJECT_ROOT/code/utils/"*.sh 2>/dev/null || true
touch "$PROJECT_ROOT/code/utils/__init__.py"

mkdir -p "$PROJECT_ROOT/output/stage3a/figures"

ENV_FILE="$PROJECT_ROOT/.env"
if ! grep -q 'FRED_API_KEY' "$ENV_FILE" 2>/dev/null; then
    cat >> "$ENV_FILE" <<'ENVEOF'
# FRED API key (free): https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your-key-here

# BLS public data API key (OPTIONAL — keyless works at lower limits).
# Free: https://data.bls.gov/registrationEngine/
BLS_API_KEY=your-key-here

# Census API key (REQUIRED for any ACS/CPS request — keyless tier retired).
# Free: https://api.census.gov/data/key_signup.html
CENSUS_API_KEY=your-key-here

# WRDS credentials: https://wrds-www.wharton.upenn.edu/
WRDS_USER=your-username
WRDS_PASS=your-password

# SEC EDGAR identity (required, no API key needed)
SEC_EDGAR_NAME=Your Name
SEC_EDGAR_EMAIL=your@email.edu
ENVEOF
fi

if [ "$LOCAL" = "0" ] && [ -d "$PROJECT_ROOT/.venv" ]; then
    # Target the project venv created by setup.sh (deployed pipeline uses bare
    # python3). Dep list single-sourced in extensions/empirical/deps.txt (also
    # read by update.sh's venv bootstrap). Guarded on venv existence so a failed
    # venv creation in setup.sh doesn't add a second doomed install here.
    uv pip install --python "$PROJECT_ROOT/.venv" -r "$TEMPLATE_ROOT/extensions/empirical/deps.txt" -q 2>/dev/null \
        || echo "Note: empirical deps failed; install manually: source $PROJECT_ROOT/.venv/bin/activate && uv pip install pandas numpy polars pyarrow statsmodels scipy fredapi pandas-datareader wrds edgartools openassetpricing gdown python-dotenv"
fi
