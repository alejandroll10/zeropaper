#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro] [--ext empirical|theory_llm] [--local]
#
# --local  Skip git clone, use templates from this repo directly.
#          Outputs to test_output/{variant}/ for inspection.
# --ext    Add an extension (can be repeated). Available: empirical, theory_llm
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
LOCAL=0
NEXT_IS_VARIANT=0
NEXT_IS_EXT=0
EXTENSIONS=()

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --ext)         NEXT_IS_EXT=1 ;;
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

copy_agent_markdown() {
    local src_dir="$1"
    local dest_dir="$2"

    [ -d "$src_dir" ] || return 0
    mkdir -p "$dest_dir"
    cp "$src_dir/"*.md "$dest_dir/"
}

assemble_claude_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        --bodies-dir "$template_root/templates/agent_bodies/shared" \
        --output-dir "$dest_dir"
}

assemble_claude_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_${variant}_agents.json" \
        --bodies-dir "$template_root/templates/agent_bodies/${variant}" \
        --output-dir "$dest_dir"
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

# ── Assemble CLAUDE.md ──
echo "Assembling CLAUDE.md for variant: $VARIANT..."

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
else
    CLAUDE_MD_OUT="CLAUDE.md"
fi

python3 - "$CORE" "$RUNTIME_SESSION" "$SCORING_FILE" "$PAPER_TYPE" "$TARGET_JOURNALS" "$DOMAIN_AREAS" "$CLAUDE_MD_OUT" "$CLAUDE_AGENTS_REL" "$CLAUDE_SKILLS_REL" <<'PYEOF'
import sys

core_path, runtime_session_path, scoring_path, paper_type, target_journals, domain_areas, out_path, agent_dir, skill_dir = sys.argv[1:10]

with open(core_path) as f:
    content = f.read()
with open(runtime_session_path) as f:
    runtime_session = f.read().rstrip()
with open(scoring_path) as f:
    scoring = f.read()

content = content.replace('{{RUNTIME_DOC_NAME}}', 'CLAUDE.md')
content = content.replace('{{PAPER_TYPE}}', paper_type)
content = content.replace('{{TARGET_JOURNALS}}', target_journals)
content = content.replace('{{DOMAIN_AREAS}}', domain_areas)
content = content.replace('{{AGENT_DIR}}', agent_dir)
content = content.replace('{{SKILL_DIR}}', skill_dir)
runtime_session = runtime_session.replace('{{SKILL_DIR}}', skill_dir)
content = content.replace('{{RUNTIME_SESSION_GUIDANCE}}', runtime_session)
content = content.replace('{{SCORING}}', scoring)

with open(out_path, 'w') as f:
    f.write(content)
PYEOF

echo "  ✓ CLAUDE.md assembled"

# ── Assemble agents ──
echo "Copying agents..."

if [ "$LOCAL" = "1" ]; then
    AGENTS_OUT="$OUT_DIR/$CLAUDE_AGENTS_REL"
else
    AGENTS_OUT="$CLAUDE_AGENTS_REL"
    mkdir -p "$AGENTS_OUT"
fi

assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"

if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_${AGENT_DIR}_agents.json" ]; then
    assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
elif [ -d "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}" ]; then
    copy_agent_markdown "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}" "$AGENTS_OUT"
fi

echo "  ✓ Agents copied (shared + ${AGENT_DIR})"

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

# Initial pipeline state
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

touch "$P/process_log/history.md"

echo "  ✓ Project structure created"

# ── Apply extensions ──
if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
fi

for ext in "${EXTENSIONS[@]}"; do
    case "$ext" in
        theory_llm)
            echo "Applying LLM experiment extension..."

            EXT_ROOT="$TEMPLATE_ROOT/extensions/theory_llm"

            cp "$EXT_ROOT/llm_client.py" "$P/"
            copy_agent_markdown "$EXT_ROOT/agents" "$AGENTS_OUT"

            assemble_claude_skills \
                "$TEMPLATE_ROOT" \
                "$TEMPLATE_ROOT/templates/skill_metadata/claude_theory_llm_skills.json" \
                "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
                "$SKILLS_OUT"

            mkdir -p "$P/output/stage3b_experiments"

            # Add LLM API keys to .env (append if file exists, create if not)
            ENV_FILE="$P/.env"
            if ! grep -q 'UF_API_KEY' "$ENV_FILE" 2>/dev/null; then
                cat >> "$ENV_FILE" <<'ENVEOF'

# LLM experiment backends (set one or both)
# UF NaviGator (free for UF researchers): https://api.ai.it.ufl.edu
UF_API_KEY=your-key-here
# DeepInfra (pay-per-token): https://deepinfra.com
DEEPINFRA_TOKEN=your-key-here
ENVEOF
            fi

            # Install Python deps
            if [ "$LOCAL" = "0" ]; then
                pip install openai python-dotenv -q 2>/dev/null \
                    || echo "Note: install deps manually: pip install openai python-dotenv"
            fi

            echo "  ✓ LLM experiment extension applied"
            ;;
        empirical)
            echo "Applying empirical extension..."

            EXT_ROOT="$TEMPLATE_ROOT/extensions/empirical"

            assemble_claude_skills \
                "$TEMPLATE_ROOT" \
                "$TEMPLATE_ROOT/templates/skill_metadata/claude_empirical_skills.json" \
                "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
                "$SKILLS_OUT"

            # Copy empirical agents (shared + variant-specific)
            if [ -d "$EXT_ROOT/agents/shared" ]; then
                copy_agent_markdown "$EXT_ROOT/agents/shared" "$AGENTS_OUT"
            fi
            if [ -d "$EXT_ROOT/agents/${AGENT_DIR}" ]; then
                copy_agent_markdown "$EXT_ROOT/agents/${AGENT_DIR}" "$AGENTS_OUT"
            else
                echo "  ⚠ No empiricist agent for variant '${AGENT_DIR}' — Stage 3b will be skipped at runtime"
            fi

            # Copy utility scripts and startup
            mkdir -p "$P/code/utils"
            cp "$EXT_ROOT/utils/"*.py "$P/code/utils/"
            cp "$EXT_ROOT/utils/"*.sh "$P/code/utils/" 2>/dev/null || true
            chmod +x "$P/code/utils/"*.sh 2>/dev/null || true
            touch "$P/code/utils/__init__.py"

            # Create empirical output directory
            mkdir -p "$P/output/stage3b"

            # Add API keys to .env (append if file exists)
            ENV_FILE="$P/.env"
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

            # Install Python deps
            if [ "$LOCAL" = "0" ]; then
                pip install pandas numpy statsmodels scipy fredapi pandas-datareader wrds edgartools openassetpricing gdown python-dotenv -q 2>/dev/null \
                    || echo "Note: install empirical deps manually: pip install pandas numpy statsmodels scipy fredapi pandas-datareader wrds edgartools openassetpricing gdown python-dotenv"
            fi

            echo "  ✓ Empirical extension applied (skills + agents)"
            ;;
        *)
            echo "Unknown extension: $ext"
            echo "Available extensions: empirical, theory_llm"
            exit 1
            ;;
    esac
done

# ── Local mode: summary and exit ──
if [ "$LOCAL" = "1" ]; then
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    if [ -d "$OUT_DIR/$CLAUDE_SKILLS_REL" ]; then
        echo ""
        echo "=== Skills ($CLAUDE_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CLAUDE_SKILLS_REL/"
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
rm -f setup.sh
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
echo "  claude --dangerously-skip-permissions"
echo ""
echo "Then say: \"Run the pipeline.\""
echo ""
echo "Variant: $VARIANT"
echo "Extensions: ${EXTENSIONS[*]:-none}"
echo "Sandbox is pre-configured in $CLAUDE_SETTINGS_REL"
echo "(Bash restricted to project folder, web access works freely)"
