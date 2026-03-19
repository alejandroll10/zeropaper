#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro|finance_llm] [--local]
#
# --local  Skip git clone, use templates from this repo directly.
#          Outputs to test_output/{variant}/ for inspection.

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
LOCAL=0
NEXT_IS_VARIANT=0

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --local)       LOCAL=1 ;;
        --theory-llm)  VARIANT="finance_llm" ;;  # legacy flag
        -*)            echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                VARIANT="$arg"
                NEXT_IS_VARIANT=0
            else
                PROJECT_NAME="$arg"
            fi
            ;;
    esac
done

if [ "$NEXT_IS_VARIANT" = "1" ]; then
    echo "Error: --variant requires a value (finance, macro, finance_llm)"
    exit 1
fi

# ── Variant configuration ──
case "$VARIANT" in
    finance)
        PAPER_TYPE="finance theory paper"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="asset pricing or corporate finance"
        AGENT_DIR="finance"
        ;;
    macro)
        PAPER_TYPE="macroeconomics theory paper"
        TARGET_JOURNALS="top-5 economics journal (AER, Econometrica, QJE, JPE, ReStud) or leading macro field journal (JME, JEDC, AEJ:Macro)"
        DOMAIN_AREAS="monetary policy, fiscal policy, business cycles, inequality and macro, or expectations"
        AGENT_DIR="macro"
        ;;
    finance_llm)
        PAPER_TYPE="finance theory paper with LLM experiments"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="asset pricing or corporate finance"
        AGENT_DIR="finance"
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: finance, macro, finance_llm"
        exit 1
        ;;
esac

# ── Resolve paths ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$LOCAL" = "1" ]; then
    # Local test mode — no clone, no git, no prereq checks
    PROJECT_NAME="${PROJECT_NAME:-test_output/$VARIANT}"
    TEMPLATE_ROOT="$SCRIPT_DIR"
    OUT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR/.claude/agents"

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

CORE="$TEMPLATE_ROOT/templates/claude_md/core.md"
DOMAIN_FILE="$TEMPLATE_ROOT/templates/domains/${AGENT_DIR}.md"
SCORING_FILE="$TEMPLATE_ROOT/templates/scoring/${AGENT_DIR}.md"

for f in "$CORE" "$DOMAIN_FILE" "$SCORING_FILE"; do
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

python3 - "$CORE" "$DOMAIN_FILE" "$SCORING_FILE" "$PAPER_TYPE" "$TARGET_JOURNALS" "$DOMAIN_AREAS" "$CLAUDE_MD_OUT" <<'PYEOF'
import sys

core_path, domain_path, scoring_path, paper_type, target_journals, domain_areas, out_path = sys.argv[1:8]

with open(core_path) as f:
    content = f.read()
with open(domain_path) as f:
    domain = f.read()
with open(scoring_path) as f:
    scoring = f.read()

content = content.replace('{{PAPER_TYPE}}', paper_type)
content = content.replace('{{TARGET_JOURNALS}}', target_journals)
content = content.replace('{{DOMAIN_AREAS}}', domain_areas)
content = content.replace('{{DOMAIN}}', domain)
content = content.replace('{{SCORING}}', scoring)

with open(out_path, 'w') as f:
    f.write(content)
PYEOF

echo "  ✓ CLAUDE.md assembled"

# ── Assemble agents ──
echo "Copying agents..."

if [ "$LOCAL" = "1" ]; then
    AGENTS_OUT="$OUT_DIR/.claude/agents"
else
    AGENTS_OUT=".claude/agents"
    rm -f "$AGENTS_OUT"/*.md
fi

cp "$TEMPLATE_ROOT/templates/agents/shared/"*.md "$AGENTS_OUT/"

if [ -d "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}" ]; then
    cp "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/"*.md "$AGENTS_OUT/"
fi

echo "  ✓ Agents copied (shared + ${AGENT_DIR})"

# ── Apply finance_llm extension if needed ──
if [ "$VARIANT" = "finance_llm" ] && [ "$LOCAL" = "0" ]; then
    echo "Applying LLM experiment extension..."

    cp extensions/theory_llm/llm_client.py .
    cp extensions/theory_llm/agents/*.md .claude/agents/

    if [ ! -f .env ]; then
        echo "# Get API key from https://api.ai.it.ufl.edu" > .env
        echo "UF_API_KEY=your-key-here" >> .env
    fi

    mkdir -p output/stage3b_experiments

    # Copy STAGES.md to project root so core.md reference works after extensions/ cleanup
    cp extensions/theory_llm/STAGES.md .

    uv pip install --system openai python-dotenv -q 2>/dev/null || echo "Note: install openai and python-dotenv manually"

    echo "  ✓ LLM experiment extension applied"
fi

# ── Local mode: summary and exit ──
if [ "$LOCAL" = "1" ]; then
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Agents (.claude/agents/) ==="
    ls -1 "$AGENTS_OUT/"
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
rm -rf templates/
rm -rf extensions/
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
if [ "$VARIANT" = "finance_llm" ]; then
    echo "NOTE: Edit .env and add your UF_API_KEY before running."
    echo "Test connection: python llm_client.py"
    echo ""
fi
echo "Variant: $VARIANT"
echo "Sandbox is pre-configured in .claude/settings.json"
echo "(Bash restricted to project folder, web access works freely)"
