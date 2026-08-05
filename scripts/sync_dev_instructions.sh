#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

CLAUDE_INSTRUCTIONS="$ROOT_DIR/CLAUDE.md"
AGENTS_INSTRUCTIONS="$ROOT_DIR/AGENTS.md"
AGENTS_SKILLS_DIR="$ROOT_DIR/.agents/skills"
CANONICAL_SKILLS_DIR="$ROOT_DIR/.claude/skills"
SKILL_NAMES=("edit-pipeline" "deploy-project")
DESC_LIMIT=1024

if [ ! -f "$CLAUDE_INSTRUCTIONS" ]; then
  echo "ERROR: $CLAUDE_INSTRUCTIONS not found." >&2
  exit 1
fi

cp "$CLAUDE_INSTRUCTIONS" "$AGENTS_INSTRUCTIONS"
echo "Synced $CLAUDE_INSTRUCTIONS -> $AGENTS_INSTRUCTIONS"

mkdir -p "$AGENTS_SKILLS_DIR"

for skill in "${SKILL_NAMES[@]}"; do
  src="$CANONICAL_SKILLS_DIR/$skill"
  dst="$AGENTS_SKILLS_DIR/$skill"

  if [ ! -d "$src" ]; then
    echo "ERROR: Canonical skill directory $src not found." >&2
    exit 1
  fi

  rel_target="../.claude/skills/$skill"
  if [ -L "$dst" ]; then
    current="$(readlink "$dst")"
    if [ "$current" != "$rel_target" ]; then
      rm "$dst"
      ln -s "$rel_target" "$dst"
      echo "Fixed symlink $dst"
    fi
  else
    rm -rf "$dst"
    ln -s "$rel_target" "$dst"
    echo "Created symlink $dst"
  fi

  skill_md="$src/SKILL.md"
  if [ ! -f "$skill_md" ]; then
    echo "ERROR: $skill_md not found." >&2
    exit 1
  fi

  description=$(awk '/^---$/{x++; next} x==1 && /^description:/{sub(/^description: */, ""); print; exit}' "$skill_md")
  if [ -z "$description" ]; then
    echo "ERROR: Skill '$skill' missing description in frontmatter." >&2
    exit 1
  fi
  desc_len=${#description}
  if [ "$desc_len" -gt "$DESC_LIMIT" ]; then
    echo "ERROR: Skill '$skill' description exceeds $DESC_LIMIT bytes ($desc_len)." >&2
    exit 1
  fi
  echo "Validated $skill (${desc_len} bytes)"
done

echo "Sync complete."
