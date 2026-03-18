#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name]
#   or:  curl -s <raw-url> | bash -s my-paper

set -e

PROJECT_NAME="${1:-my-research-paper}"

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

echo ""
echo "============================================"
echo "  Setup complete: $PROJECT_NAME"
echo "============================================"
echo ""
echo "To run the autonomous pipeline:"
echo ""
echo "  cd $PROJECT_NAME"
echo "  claude --dangerously-skip-permissions"
echo ""
echo "Then say: \"Run the pipeline.\""
echo ""
echo "Sandbox is pre-configured in .claude/settings.json"
echo "(Bash restricted to project folder, web access works freely)"
