#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--theory-llm]

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="theory"

for arg in "$@"; do
    case "$arg" in
        --theory-llm) VARIANT="theory_llm" ;;
        -*) echo "Unknown option: $arg"; exit 1 ;;
        *) PROJECT_NAME="$arg" ;;
    esac
done

PROJECT_NAME="${PROJECT_NAME:-my-research-paper}"

# ── Check prerequisites ──
echo "Checking prerequisites..."

missing=()

command -v python3 >/dev/null 2>&1 || missing+=("python3")
command -v git >/dev/null 2>&1 || missing+=("git")
command -v claude >/dev/null 2>&1 || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
command -v uv >/dev/null 2>&1 || missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")

# Check bubblewrap (Linux only)
if [[ "$(uname)" == "Linux" ]]; then
    command -v bwrap >/dev/null 2>&1 || missing+=("bubblewrap (sudo apt-get install bubblewrap)")
fi

if [ ${#missing[@]} -gt 0 ]; then
    echo "Missing dependencies:"
    for dep in "${missing[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Install them and re-run this script."
    exit 1
fi

echo "All prerequisites found."

# ── Clone template ──
echo "Cloning template into $PROJECT_NAME..."
git clone https://github.com/alejandroll10/auto-ai-research-template.git "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Remove template remote, start fresh
git remote remove origin

# ── Apply variant ──
if [ "$VARIANT" = "theory_llm" ]; then
    echo "Applying theory_llm extension..."

    # Copy LLM client
    cp extensions/theory_llm/llm_client.py .

    # Copy experiment agents
    cp extensions/theory_llm/agents/*.md .claude/agents/

    # Create .env placeholder
    if [ ! -f .env ]; then
        echo "# Get API key from https://api.ai.it.ufl.edu" > .env
        echo "UF_API_KEY=your-key-here" >> .env
    fi

    # Create experiment output directory
    mkdir -p output/stage3b_experiments

    # Install Python deps
    pip install openai python-dotenv -q 2>/dev/null || echo "Note: install openai and python-dotenv manually"

    # Commit the extension setup
    git add -A
    git commit -m "setup: applied theory_llm extension" -q

    echo "  ✓ llm_client.py copied to project root"
    echo "  ✓ experiment-designer and experiment-reviewer agents added"
    echo "  ✓ .env created (add your UF_API_KEY)"
    echo ""
fi

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
if [ "$VARIANT" = "theory_llm" ]; then
    echo "NOTE: Edit .env and add your UF_API_KEY before running."
    echo "Test connection: python llm_client.py"
    echo ""
fi
echo "Sandbox is pre-configured in .claude/settings.json"
echo "(Bash restricted to project folder, web access works freely)"
