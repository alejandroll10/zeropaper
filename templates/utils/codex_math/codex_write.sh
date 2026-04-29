#!/usr/bin/env bash
# Ask Codex (gpt-5.5) to write a mathematical proof or derivation.
# Accepts either a theorem statement from a file or inline text.
#
# Usage:
#   codex_write.sh <input> [reasoning_effort] [output_dir]
#
# <input> can be:
#   - A file path: reads the file as the theorem statement
#   - A file:lines spec: reads those lines
#   - Inline text (quoted): used directly as the theorem statement
#
# Examples:
#   codex_write.sh "Prove: if H'' ≈ 0 on [a,b] then demand is approximately isoelastic"
#   codex_write.sh theorem_statement.tex high
#   codex_write.sh paper/model.tex:200-210 high ./proofs
#
# reasoning_effort: low | medium (default) | high
# output_dir: where to save results (default: ./output/codex_proofs)

set -euo pipefail

INPUT="${1:?Usage: codex_write.sh <input> [reasoning_effort] [output_dir]}"
EFFORT="${2:-medium}"
OUTDIR="${3:-./output/codex_proofs}"

mkdir -p "$OUTDIR"

# Determine if input is a file, file:lines, or inline text
if echo "$INPUT" | grep -qE '^.+:[0-9]+-[0-9]+$'; then
    # file:lines format
    FILE=$(echo "$INPUT" | cut -d: -f1)
    RANGE=$(echo "$INPUT" | cut -d: -f2)
    START=$(echo "$RANGE" | cut -d- -f1)
    END=$(echo "$RANGE" | cut -d- -f2)
    CONTENT=$(sed -n "${START},${END}p" "$FILE")
    SAFE_NAME="proof_$(basename "$FILE" | tr '.' '_')_${START}_${END}"
elif [ -f "$INPUT" ]; then
    # File path
    CONTENT=$(cat "$INPUT")
    SAFE_NAME="proof_$(basename "$INPUT" | tr '.' '_')"
else
    # Inline text
    CONTENT="$INPUT"
    SAFE_NAME="proof_$(echo "$INPUT" | tr ' /:{}\\' '_' | cut -c1-60 | tr -cd '[:alnum:]_-')"
fi

OUTFILE="${OUTDIR}/${SAFE_NAME}.md"
TMP="/tmp/codex_write_${SAFE_NAME}_$$.txt"

echo "[codex-math] Writing proof (gpt-5.5, effort=$EFFORT)..."

codex exec --full-auto --skip-git-repo-check \
    -c "model_reasoning_effort=\"$EFFORT\"" \
    -o "$TMP" \
    "You are a mathematician writing a proof for a top economics journal. Write a complete, publication-ready proof.

Show every algebraic step. Do not skip intermediate calculations. Use standard LaTeX environments (\begin{proof}...\end{proof}).

Be extremely rigorous:
- Re-derive every equation — do not assert 'by standard arguments' without showing the argument
- Justify differentiating under integrals (state DCT conditions, verify Fubini applicability)
- Check boundary cases explicitly (parameters at 0, 1, infinity)
- State exactly where each assumption is used in the proof
- If a step requires a lemma, state and prove the lemma before using it
- Verify second-order conditions when claiming optima
- If the proof attempt fails or requires additional assumptions, say so explicitly rather than hand-waving

---
THEOREM / TASK:
$CONTENT
---

Write the complete LaTeX proof. If the statement needs correction, note that before the proof." 2>&1

if [ -f "$TMP" ]; then
    {
        echo "# Codex Proof: $SAFE_NAME"
        echo "**Effort:** $EFFORT"
        echo "**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        cat "$TMP"
    } > "$OUTFILE"
    echo ""
    echo "[codex-math] Proof saved to: $OUTFILE"
else
    echo "WARNING: No output file produced" >&2
    exit 1
fi
