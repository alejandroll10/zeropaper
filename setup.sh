#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro] [--ext empirical|theory_llm] [--seed <file>] [--light] [--local]
#
# --local  Skip git clone, use templates from this repo directly.
#          Outputs to test_output/{variant}/ for inspection.
# --ext    Add an extension (can be repeated). Available: empirical, theory_llm
# --seed   Provide a pre-developed idea (file path). Pipeline starts at Gate 1b
#          instead of Stage 0, and never silently abandons the seeded idea.
# --light  Use sonnet for all subagents (cheaper/faster). Orchestrator model unchanged.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
LOCAL=0
NEXT_IS_VARIANT=0
NEXT_IS_EXT=0
NEXT_IS_SEED=0
SEED_FILE=""
LIGHT=0
EXTENSIONS=()

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --ext)         NEXT_IS_EXT=1 ;;
        --seed)        NEXT_IS_SEED=1 ;;
        --light)       LIGHT=1 ;;
        --local)       LOCAL=1 ;;
        --theory-llm)  VARIANT="finance_llm" ;;  # legacy flag
        -*)            echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                VARIANT="$arg"
                NEXT_IS_VARIANT=0
            elif [ "$NEXT_IS_EXT" = "1" ]; then
                EXTENSIONS+=("$arg")
                NEXT_IS_EXT=0
            elif [ "$NEXT_IS_SEED" = "1" ]; then
                SEED_FILE="$arg"
                NEXT_IS_SEED=0
            else
                PROJECT_NAME="$arg"
            fi
            ;;
    esac
done

if [ "$NEXT_IS_VARIANT" = "1" ]; then
    echo "Error: --variant requires a value (finance, macro)"
    exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"
    exit 1
fi
if [ "$NEXT_IS_SEED" = "1" ]; then
    echo "Error: --seed requires a file path"
    exit 1
fi
if [ -n "$SEED_FILE" ] && [ ! -f "$SEED_FILE" ]; then
    echo "Error: seed file not found: $SEED_FILE"
    exit 1
fi

# ── Expand legacy finance_llm variant ──
if [ "$VARIANT" = "finance_llm" ]; then
    VARIANT="finance"
    EXTENSIONS+=("theory_llm")
fi

# ── Variant configuration ──
case "$VARIANT" in
    finance)
        PAPER_TYPE="finance theory paper"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="finance theory — asset pricing, corporate finance, information economics, market design, financial intermediation, or behavioral finance"
        JOURNAL_LIST="Top-3 finance: JF, JFE, RFS. Also: Review of Finance, Management Science, JFQA. Top accounting: JAR, JAE, TAR, RAS. Top-5 econ: AER, Econometrica, QJE, JPE, ReStud."
        AGENT_DIR="finance"
        ;;
    macro)
        PAPER_TYPE="macroeconomics theory paper"
        TARGET_JOURNALS="top-5 economics journal (AER, Econometrica, QJE, JPE, ReStud) or leading macro field journal (JME, JEDC, AEJ:Macro)"
        DOMAIN_AREAS="macroeconomics"
        JOURNAL_LIST="Top-5 econ: AER, Econometrica, QJE, JPE, ReStud. Top-3 finance: JF, JFE, RFS. Macro field: JME, JEDC, AEJ:Macro, AEJ:Micro, JIE, JET, RED."
        AGENT_DIR="macro"
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: finance, macro"
        exit 1
        ;;
esac

# ── Resolve paths ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR_REL=".claude"
CLAUDE_AGENTS_REL="$CLAUDE_DIR_REL/agents"
CLAUDE_SKILLS_REL="$CLAUDE_DIR_REL/skills"
CLAUDE_SETTINGS_REL="$CLAUDE_DIR_REL/settings.json"
CODEX_DIR_REL=".agents"
CODEX_SUBAGENT_DIR_REL=".codex"
CODEX_AGENTS_REL="$CODEX_SUBAGENT_DIR_REL/agents"
CODEX_SKILLS_REL="$CODEX_DIR_REL/skills"

# Resolve seed file to absolute path early (before any cd)
if [ -n "$SEED_FILE" ]; then
    SEED_FILE="$(cd "$(dirname "$SEED_FILE")" && pwd)/$(basename "$SEED_FILE")"
fi

MODEL_OVERRIDE_ARGS=()
if [ "$LIGHT" = "1" ]; then
    MODEL_OVERRIDE_ARGS=(--model-override sonnet)
fi

assemble_claude_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        --bodies-dir "$template_root/templates/agent_bodies/shared" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_claude_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_${variant}_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_codex_subagents_from_parts() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

assemble_claude_agents_from_parts() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_codex_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    assemble_codex_subagents_from_parts \
        "$template_root" \
        "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "$template_root/templates/agent_bodies/shared" \
        "$dest_dir"
}

assemble_codex_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"

    assemble_codex_subagents_from_parts \
        "$template_root" \
        "$template_root/templates/agent_metadata/claude_${variant}_agents.json" \
        "$template_root/templates/agents/${variant}" \
        "$dest_dir"
}

assemble_claude_skills() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_skills.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

if [ "$LOCAL" = "1" ]; then
    # Local test mode — no clone, no git, no prereq checks
    PROJECT_NAME="${PROJECT_NAME:-test_output/$VARIANT}"
    TEMPLATE_ROOT="$SCRIPT_DIR"
    OUT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR/$CLAUDE_AGENTS_REL"
    mkdir -p "$OUT_DIR/$CODEX_AGENTS_REL"
    # Copy shared project files
    mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL"
    cp "$SCRIPT_DIR/$CLAUDE_SETTINGS_REL" "$OUT_DIR/$CLAUDE_DIR_REL/"
    cp "$SCRIPT_DIR/.gitignore" "$OUT_DIR/"
    cp "$SCRIPT_DIR/dashboard.html" "$OUT_DIR/"

    echo "Local test mode: $VARIANT → $OUT_DIR"
else
    # Production mode — clone, check prereqs, full setup
    PROJECT_NAME="${PROJECT_NAME:-my-research-paper}"

    echo "Checking prerequisites..."
    missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")
    command -v claude >/dev/null 2>&1 || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
    command -v uv >/dev/null 2>&1 || missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")
    if [[ "$(uname)" == "Linux" ]]; then
        command -v bwrap >/dev/null 2>&1 || missing+=("bubblewrap (sudo apt-get install bubblewrap)")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing dependencies:"
        for dep in "${missing[@]}"; do echo "  - $dep"; done
        exit 1
    fi
    echo "All prerequisites found."

    if [ -e "$PROJECT_NAME" ]; then
        echo "Error: $PROJECT_NAME already exists"
        exit 1
    fi

    echo "Cloning template into $PROJECT_NAME..."
    git clone https://github.com/alejandroll10/auto-ai-research-template.git "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    git remote remove origin

    TEMPLATE_ROOT="."
    OUT_DIR="."
fi

# ── Assemble runtime docs ──
echo "Assembling runtime docs for variant: $VARIANT..."

CORE="$TEMPLATE_ROOT/templates/shared/core.md"
RUNTIME_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session.md"
SCORING_FILE="$TEMPLATE_ROOT/templates/scoring/${AGENT_DIR}.md"

for f in "$CORE" "$RUNTIME_SESSION" "$SCORING_FILE"; do
    if [ ! -f "$f" ]; then
        echo "Error: $f not found"
        exit 1
    fi
done

if [ "$LOCAL" = "1" ]; then
    CLAUDE_MD_OUT="$OUT_DIR/CLAUDE.md"
    AGENTS_MD_OUT="$OUT_DIR/AGENTS.md"
else
    CLAUDE_MD_OUT="CLAUDE.md"
    AGENTS_MD_OUT="AGENTS.md"
fi

SEED_ARGS=()
if [ -n "$SEED_FILE" ]; then
    SEED_TEMPLATE="$TEMPLATE_ROOT/templates/shared/seed.md"
    if [ ! -f "$SEED_TEMPLATE" ]; then
        echo "Error: seed template not found: $SEED_TEMPLATE"
        exit 1
    fi
    SEED_ARGS=(--seed-block "$SEED_TEMPLATE")
fi

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$RUNTIME_SESSION" \
    --scoring "$SCORING_FILE" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --doc-name "CLAUDE.md" \
    --agent-dir "$CLAUDE_AGENTS_REL" \
    --skill-dir "$CLAUDE_SKILLS_REL" \
    "${SEED_ARGS[@]}" \
    --output "$CLAUDE_MD_OUT"

CODEX_DISCIPLINE="$TEMPLATE_ROOT/templates/runtime/codex/session.md"

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$RUNTIME_SESSION" \
    --scoring "$SCORING_FILE" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --doc-name "AGENTS.md" \
    --agent-dir "$CODEX_AGENTS_REL" \
    --skill-dir "$CODEX_SKILLS_REL" \
    --discipline "$CODEX_DISCIPLINE" \
    "${SEED_ARGS[@]}" \
    --output "$AGENTS_MD_OUT"

echo "  ✓ Runtime docs assembled (CLAUDE.md + AGENTS.md)"

# ── Assemble agents ──
echo "Copying agents..."

if [ "$LOCAL" = "1" ]; then
    AGENTS_OUT="$OUT_DIR/$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$OUT_DIR/$CODEX_AGENTS_REL"
else
    AGENTS_OUT="$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$CODEX_AGENTS_REL"
    mkdir -p "$AGENTS_OUT"
    mkdir -p "$CODEX_AGENTS_OUT"
fi

assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"
assemble_codex_shared_agents "$TEMPLATE_ROOT" "$CODEX_AGENTS_OUT"

if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_${AGENT_DIR}_agents.json" ]; then
    assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
    assemble_codex_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$CODEX_AGENTS_OUT"
fi

echo "  ✓ Agents assembled (shared + ${AGENT_DIR})"

# ── Inject variant context into agents ──
VARIANT_BLOCK="
## Variant context
- **Paper type:** ${PAPER_TYPE}
- **Target journals:** ${JOURNAL_LIST}
- **Domain:** ${DOMAIN_AREAS}
"

for agent in literature-scout novelty-checker theory-explorer referee scorer paper-writer style; do
    if [ -f "$AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$AGENTS_OUT/$agent.md"
    fi
done
echo "  ✓ Variant context injected into agents"

# ── Create project directories and initial files ──
echo "Creating project structure..."

if [ "$LOCAL" = "1" ]; then
    P="$OUT_DIR"
else
    P="."
fi

mkdir -p "$P/code/analysis" "$P/code/download" "$P/code/tmp" "$P/code/explore"
mkdir -p "$P/data"
mkdir -p "$P/output/stage0" "$P/output/stage1" "$P/output/stage2" "$P/output/stage3" "$P/output/stage4" "$P/output/post_pipeline"
mkdir -p "$P/paper/sections" "$P/paper/referee_reports"
mkdir -p "$P/process_log/sessions" "$P/process_log/decisions" "$P/process_log/discussions" "$P/process_log/patterns"
mkdir -p "$P/references"

# Copy seed file if provided
if [ -n "$SEED_FILE" ]; then
    mkdir -p "$P/output/seed"
    cp "$SEED_FILE" "$P/output/seed/user_idea.md"
    echo "  ✓ Seed idea copied to output/seed/user_idea.md"
fi

# Initial pipeline state
if [ -n "$SEED_FILE" ]; then
cat > "$P/process_log/pipeline_state.json" <<'JSONEOF'
{
  "current_stage": "gate_1b",
  "problem_attempt": 1,
  "idea_round": 1,
  "theory_attempt": 1,
  "revision_round": 0,
  "referee_round": 0,
  "status": "not_started",
  "seeded": true,
  "scores": {},
  "history": []
}
JSONEOF
else
cat > "$P/process_log/pipeline_state.json" <<'JSONEOF'
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "revision_round": 0,
  "referee_round": 0,
  "status": "not_started",
  "scores": {},
  "history": []
}
JSONEOF
fi

touch "$P/process_log/history.md"

echo "  ✓ Project structure created"

# ── Copy .env if available ──
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$P/.env"
    echo "  ✓ .env copied from template repo"
fi

# ── Install core Python deps ──
if [ "$LOCAL" = "0" ]; then
    uv pip install sympy matplotlib -q 2>/dev/null \
        || echo "Note: install core deps manually: uv pip install sympy matplotlib"
fi

# ── Assemble core skills ──
echo "Assembling core skills..."

if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

# Codex math skill (available for all variants)
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy codex-math utility scripts
mkdir -p "$P/code/utils/codex_math"
cp "$TEMPLATE_ROOT/templates/utils/codex_math/"*.sh "$P/code/utils/codex_math/"
chmod +x "$P/code/utils/codex_math/"*.sh

# Create codex output directories
mkdir -p "$P/output/codex_audits" "$P/output/codex_proofs" "$P/output/codex_explorations"

# Check for codex CLI (optional dependency — warn, don't fail)
if ! command -v codex >/dev/null 2>&1; then
    echo "  ⚠ codex CLI not found. Install with: npm install -g @openai/codex"
    echo "  ⚠ The codex-math skill will not work until codex is installed."
fi

echo "  ✓ Core skills assembled"

# ── Apply extensions ──
if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

for ext in "${EXTENSIONS[@]}"; do
    case "$ext" in
        theory_llm)
            echo "Applying LLM experiment extension..."
            bash "$TEMPLATE_ROOT/scripts/apply_extension_theory_llm.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$LOCAL"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
                --output-dir "$CODEX_SKILLS_OUT"

            echo "  ✓ LLM experiment extension applied"
            ;;
        empirical)
            echo "Applying empirical extension..."
            bash "$TEMPLATE_ROOT/scripts/apply_extension_empirical.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$AGENT_DIR" \
                "$LOCAL"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
                --output-dir "$CODEX_SKILLS_OUT"

            echo "  ✓ Empirical extension applied (skills + agents)"
            ;;
        *)
            echo "Unknown extension: $ext"
            echo "Available extensions: empirical, theory_llm"
            exit 1
            ;;
    esac
done

echo "  ✓ Codex custom agents assembled"

# ── Local mode: summary and exit ──
if [ "$LOCAL" = "1" ]; then
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Assembled AGENTS.md ==="
    echo "Lines: $(wc -l < "$AGENTS_MD_OUT")"
    AGENTS_REMAINING=$(grep -c '{{' "$AGENTS_MD_OUT" 2>/dev/null || true)
    AGENTS_REMAINING="${AGENTS_REMAINING:-0}"
    echo "Placeholders remaining: $AGENTS_REMAINING"
    echo ""
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    echo ""
    echo "=== Codex Agents ($CODEX_AGENTS_REL/) ==="
    ls -1 "$CODEX_AGENTS_OUT/"
    if [ -d "$OUT_DIR/$CLAUDE_SKILLS_REL" ]; then
        echo ""
        echo "=== Skills ($CLAUDE_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CLAUDE_SKILLS_REL/"
    fi
    if [ -d "$OUT_DIR/$CODEX_SKILLS_REL" ]; then
        echo ""
        echo "=== Codex Skills ($CODEX_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CODEX_SKILLS_REL/"
    fi
    echo ""
    echo "=== First 10 lines ==="
    head -10 "$CLAUDE_MD_OUT"
    echo ""
    echo "=== Domain section ==="
    grep -A 5 "^## Domain:" "$CLAUDE_MD_OUT" | head -8
    echo ""

    if [ "$REMAINING" -gt 0 ]; then
        echo "WARNING: $REMAINING unresolved placeholders:"
        grep '{{' "$CLAUDE_MD_OUT"
        exit 1
    elif [ "$AGENTS_REMAINING" -gt 0 ]; then
        echo "WARNING: $AGENTS_REMAINING unresolved placeholders:"
        grep '{{' "$AGENTS_MD_OUT"
        exit 1
    else
        echo "✓ All placeholders resolved"
    fi
    echo ""
    echo "Output at: $OUT_DIR/"
    exit 0
fi

# ── Production mode: clean up and commit ──
echo "Cleaning up template files..."

# Replace template .gitignore with project-specific one (before deleting templates/)
cp templates/gitignore_project .gitignore

rm -rf templates/
rm -rf extensions/
rm -rf meta_paper/
rm -rf test_scripts/
rm -rf scripts/
rm -rf codex_inspect/
rm -rf test_output/
rm -f setup.sh
rm -f README.md
rm -f CLAUDE_REFACTOR_PLAN.md
rm -f requirements.system
rm -f texput.log
echo "  ✓ Template files removed"

git add -A
git commit -m "setup: initialized ${VARIANT} variant pipeline" -q

echo ""
echo "============================================"
echo "  Setup complete: $PROJECT_NAME ($VARIANT)"
echo "============================================"
echo ""
echo "To run the autonomous pipeline:"
echo ""
echo "  cd $PROJECT_NAME"
echo ""
echo "Claude:"
echo "  claude --dangerously-skip-permissions"
echo ""
echo "Codex:"
echo "  codex --sandbox danger-full-access --ask-for-approval never"
echo ""
echo "Then say: \"Run the pipeline.\""
echo ""
echo "Variant: $VARIANT"
echo "Extensions: ${EXTENSIONS[*]:-none}"
if [ "$LIGHT" = "1" ]; then
    echo "Mode: light (all subagents use sonnet)"
fi
if [ -n "$SEED_FILE" ]; then
    echo "Seed: $(basename "$SEED_FILE") → output/seed/user_idea.md"
    echo "Pipeline will start at Gate 1b (novelty check on seeded idea)"
fi
echo "Sandbox is pre-configured in $CLAUDE_SETTINGS_REL"
echo "(Bash restricted to project folder, web access works freely)"
