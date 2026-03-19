#!/bin/bash
# Test variant assembly locally (no git clone, no remote operations)
# Usage: ./test-variant.sh [variant]
# Example: ./test-variant.sh macro
#
# Creates test_output/{variant}/ with the assembled CLAUDE.md and agents.
# Inspect the output to verify correctness before pushing.

set -e

VARIANT="${1:-finance}"
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$REPO_ROOT/test_output/$VARIANT"

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
        echo "Available: finance, macro, finance_llm"
        exit 1
        ;;
esac

# ── Clean and create output ──
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/agents"

echo "Testing variant: $VARIANT"
echo "Output: $OUT_DIR"
echo ""

# ── Assemble CLAUDE.md ──
CORE="$REPO_ROOT/templates/claude_md/core.md"
DOMAIN_FILE="$REPO_ROOT/templates/domains/${AGENT_DIR}.md"
SCORING_FILE="$REPO_ROOT/templates/scoring/${AGENT_DIR}.md"

for f in "$CORE" "$DOMAIN_FILE" "$SCORING_FILE"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Missing $f"
        exit 1
    fi
done

cp "$CORE" "$OUT_DIR/CLAUDE.md"

python3 -c "
with open('$OUT_DIR/CLAUDE.md', 'r') as f:
    content = f.read()
with open('$DOMAIN_FILE', 'r') as f:
    domain = f.read()
with open('$SCORING_FILE', 'r') as f:
    scoring = f.read()

content = content.replace('{{PAPER_TYPE}}', '''$PAPER_TYPE''')
content = content.replace('{{TARGET_JOURNALS}}', '''$TARGET_JOURNALS''')
content = content.replace('{{DOMAIN_AREAS}}', '''$DOMAIN_AREAS''')
content = content.replace('{{DOMAIN}}', domain)
content = content.replace('{{SCORING}}', scoring)

with open('$OUT_DIR/CLAUDE.md', 'w') as f:
    f.write(content)
"

echo "✓ CLAUDE.md assembled"

# ── Copy agents ──
cp "$REPO_ROOT/templates/agents/shared/"*.md "$OUT_DIR/agents/"
if [ -d "$REPO_ROOT/templates/agents/${AGENT_DIR}" ]; then
    cp "$REPO_ROOT/templates/agents/${AGENT_DIR}/"*.md "$OUT_DIR/agents/"
fi

echo "✓ Agents copied"

# ── Summary ──
echo ""
echo "=== Assembled CLAUDE.md ==="
echo "Lines: $(wc -l < "$OUT_DIR/CLAUDE.md")"
PLACEHOLDER_COUNT=$(grep -c '{{' "$OUT_DIR/CLAUDE.md" 2>/dev/null || true)
echo "Placeholders remaining: ${PLACEHOLDER_COUNT:-0}"
echo ""
echo "=== Agents ==="
ls -1 "$OUT_DIR/agents/"
echo ""
echo "=== CLAUDE.md first 10 lines ==="
head -10 "$OUT_DIR/CLAUDE.md"
echo ""
echo "=== Domain section ==="
grep -A 5 "^## Domain:" "$OUT_DIR/CLAUDE.md" | head -8
echo ""
echo "=== Scoring calibrations ==="
grep "Calibration:" "$OUT_DIR/CLAUDE.md" | head -5
echo ""

# ── Check for problems ──
REMAINING=$(grep -c '{{' "$OUT_DIR/CLAUDE.md" 2>/dev/null || true)
REMAINING="${REMAINING:-0}"
if [ "$REMAINING" -gt 0 ]; then
    echo "⚠  WARNING: $REMAINING unresolved placeholders found:"
    grep '{{' "$OUT_DIR/CLAUDE.md"
    exit 1
else
    echo "✓ All placeholders resolved"
fi

echo ""
echo "Full output at: $OUT_DIR/"
echo "Inspect CLAUDE.md and agents/ to verify."
