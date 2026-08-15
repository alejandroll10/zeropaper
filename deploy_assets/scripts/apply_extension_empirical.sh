#!/bin/bash
set -e

# Mode threading: positional $11 = MODE_BODIES_OVERLAY, $12 = MODE_VOCAB_OVERLAY,
# $13 = base variant vocab path, $14 = active underscored mode slug. The variant vocab supplies default values for
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
OPENCODE_AGENTS_OUT="$6"
SKILLS_OUT="$7"
AGENT_DIR="$8"
ASSEMBLE_ONLY="$9"
MODEL_OVERRIDE_ARG=()
if [ -n "${10}" ]; then
    MODEL_OVERRIDE_ARG=(--model-override "${10}")
fi
EXT_MODE_BODIES_OVERLAY="${11}"
EXT_MODE_VOCAB_OVERLAY="${12}"
EXT_BASE_VOCAB="${13}"
EXT_MODE="${14}"

# Build vocab args: shared defaults first, then base variant vocab, then mode
# overlay (last-write-wins) — same layering as the base assemblers in setup.sh.
EXT_VOCAB_ARGS=()
EXT_SHARED_VOCAB="$TEMPLATE_ROOT/templates/agent_bodies/shared/vocab.json"
[ -f "$EXT_SHARED_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_SHARED_VOCAB")
[ -n "$EXT_BASE_VOCAB" ] && [ -f "$EXT_BASE_VOCAB" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_BASE_VOCAB")
[ -n "$EXT_MODE_VOCAB_OVERLAY" ] && [ -f "$EXT_MODE_VOCAB_OVERLAY" ] && EXT_VOCAB_ARGS+=(--vocab "$EXT_MODE_VOCAB_OVERLAY")

# Build both body-tier args: a mode directory may contain `{id}.md` for a
# shared extension agent or `{id}-core.md` for a variant extension agent.
# Both lookups are first-match-wins, so the overlay precedes the extension's
# base body directory in each assembler call.
EXT_SHARED_ARGS=()
[ -n "$EXT_MODE_BODIES_OVERLAY" ] && [ -d "$EXT_MODE_BODIES_OVERLAY" ] && EXT_SHARED_ARGS+=(--shared-bodies-dir "$EXT_MODE_BODIES_OVERLAY")
EXT_BODIES_ARGS=()
[ -n "$EXT_MODE_BODIES_OVERLAY" ] && [ -d "$EXT_MODE_BODIES_OVERLAY" ] && EXT_BODIES_ARGS+=(--bodies-dir "$EXT_MODE_BODIES_OVERLAY")

EXT_MODE_ARGS=()
[ -n "$EXT_MODE" ] && EXT_MODE_ARGS=(--mode "$EXT_MODE")

EXT_ROOT="$TEMPLATE_ROOT/extensions/empirical"
# shellcheck source=/dev/null
source "$TEMPLATE_ROOT/scripts/setup/ownership.sh"
P="$PROJECT_ROOT"

python3 "$TEMPLATE_ROOT/scripts/assemble_claude_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
    --output-dir "$SKILLS_OUT"

if [ -f "$EXT_ROOT/agent_metadata/shared_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$CODEX_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$GEMINI_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_opencode_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/shared_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/shared" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$OPENCODE_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"
fi

if [ -f "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" ]; then
    python3 "$TEMPLATE_ROOT/scripts/assemble_claude_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_subagents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$CODEX_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_gemini_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$GEMINI_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"

    python3 "$TEMPLATE_ROOT/scripts/assemble_opencode_agents.py" \
        --metadata "$EXT_ROOT/agent_metadata/${AGENT_DIR}_agents.json" \
        "${EXT_BODIES_ARGS[@]}" \
        --bodies-dir "$EXT_ROOT/agent_bodies/${AGENT_DIR}" \
        "${EXT_SHARED_ARGS[@]}" \
        "${EXT_VOCAB_ARGS[@]}" \
        "${EXT_MODE_ARGS[@]}" \
        --output-dir "$OPENCODE_AGENTS_OUT" \
        "${MODEL_OVERRIDE_ARG[@]}"
else
    echo "  ⚠ No empiricist agent for variant '${AGENT_DIR}' — Stage 3a will be skipped at runtime"
fi

mkdir -p "$PROJECT_ROOT/code/utils"
for _infra_src in "$EXT_ROOT/utils/"*.py "$EXT_ROOT/utils/"*.sh; do
    [ -f "$_infra_src" ] || continue
    infrastructure_copy_file 1000 "$_infra_src" "code/utils/$(basename "$_infra_src")"
done
infrastructure_dir 1000 "code/utils/ssa_oact"
cp "$EXT_ROOT/utils/ssa_oact/period_life_table_2023.csv" \
    "$PROJECT_ROOT/code/utils/ssa_oact/"
cp "$EXT_ROOT/utils/ssa_oact/provenance.json" \
    "$PROJECT_ROOT/code/utils/ssa_oact/"
cp "$EXT_ROOT/utils/ssa_oact/README.md" \
    "$PROJECT_ROOT/code/utils/ssa_oact/"
chmod +x "$PROJECT_ROOT/code/utils/"*.sh 2>/dev/null || true
if [ ! -f "$PROJECT_ROOT/code/utils/__init__.py" ]; then
    touch "$PROJECT_ROOT/code/utils/__init__.py"
fi
infrastructure_file 1000 "code/utils/__init__.py"

bootstrap_dir "output/stage3a/figures"

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
