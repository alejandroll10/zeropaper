#!/usr/bin/env bash
# Extract a mathematical block (proposition, theorem, lemma, proof, etc.) from a file.
# Works with LaTeX (.tex) and Markdown (.md).
#
# Usage:
#   extract_block.sh <file> <pattern> [context_lines]
#
# Examples:
#   extract_block.sh paper/model.tex "Theorem 1"
#   extract_block.sh paper/model.tex "prop:crra_linear"
#   extract_block.sh paper/model.tex "Characterization" 30
#   extract_block.sh notes.md "Proposition 3"
#
# Output:
#   === CONTEXT (lines X-Y) ===
#   [definitions and notation before the block]
#   === BLOCK (lines A-B) ===
#   [the proposition/theorem + proof]
#
# The script auto-detects LaTeX vs Markdown by file extension.

set -euo pipefail

FILE="${1:?Usage: extract_block.sh <file> <pattern> [context_lines]}"
PATTERN="${2:?Usage: extract_block.sh <file> <pattern> [context_lines]}"
CONTEXT_LINES="${3:-20}"

if [ ! -f "$FILE" ]; then
    echo "ERROR: File not found: $FILE" >&2
    exit 1
fi

TOTAL=$(wc -l < "$FILE")

# Find the line containing the pattern
MATCH_LINE=$(grep -n "$PATTERN" "$FILE" | head -1 | cut -d: -f1)
if [ -z "$MATCH_LINE" ]; then
    echo "ERROR: Pattern '$PATTERN' not found in $FILE" >&2
    exit 1
fi

# Detect file type
EXT="${FILE##*.}"

if [ "$EXT" = "tex" ]; then
    # === LaTeX mode ===

    # Search backward for the nearest \begin{proposition|theorem|lemma|corollary|remark|definition}
    BLOCK_START="$MATCH_LINE"
    for i in $(seq "$MATCH_LINE" -1 1); do
        if sed -n "${i}p" "$FILE" | grep -qE '\\begin\{(proposition|theorem|lemma|corollary|remark|definition|assumption)\}'; then
            BLOCK_START="$i"
            break
        fi
    done

    # Search forward for the end: \end{proof} preferred, else \end{proposition|theorem|...}
    # We look for the FIRST \end{proof} after the match line. If none, look for \end{proposition} etc.
    BLOCK_END="$TOTAL"
    FOUND_END=0
    for i in $(seq "$MATCH_LINE" "$TOTAL"); do
        LINE=$(sed -n "${i}p" "$FILE")
        if echo "$LINE" | grep -qE '\\end\{proof\}'; then
            BLOCK_END="$i"
            FOUND_END=1
            break
        fi
        # Stop if we hit another \begin{proposition|theorem} (next result started)
        if [ "$i" -gt "$((MATCH_LINE + 2))" ] && echo "$LINE" | grep -qE '\\begin\{(proposition|theorem|lemma)\}'; then
            # Back up to the previous \end{...}
            for j in $(seq "$((i - 1))" -1 "$MATCH_LINE"); do
                if sed -n "${j}p" "$FILE" | grep -qE '\\end\{'; then
                    BLOCK_END="$j"
                    FOUND_END=1
                    break
                fi
            done
            break
        fi
    done

    # If no \end{proof} found within 200 lines, cap it
    if [ "$FOUND_END" -eq 0 ] || [ "$((BLOCK_END - BLOCK_START))" -gt 200 ]; then
        # Look for any \end{} within 200 lines
        for i in $(seq "$MATCH_LINE" "$((MATCH_LINE + 200))"); do
            [ "$i" -gt "$TOTAL" ] && break
            if sed -n "${i}p" "$FILE" | grep -qE '\\end\{(proposition|theorem|lemma|corollary|remark|definition)\}'; then
                BLOCK_END="$i"
                break
            fi
        done
    fi

    # Also grab referenced equations for context
    REFS=$(sed -n "${BLOCK_START},${BLOCK_END}p" "$FILE" | grep -oE 'eq:[a-zA-Z_]+' | sort -u 2>/dev/null || true)

else
    # === Markdown mode ===

    # Search backward for ## or ### or **Proposition** etc.
    BLOCK_START="$MATCH_LINE"
    for i in $(seq "$MATCH_LINE" -1 1); do
        LINE=$(sed -n "${i}p" "$FILE")
        if echo "$LINE" | grep -qE '^#{1,3} |^\*\*(Proposition|Theorem|Lemma|Corollary|Definition)'; then
            BLOCK_START="$i"
            break
        fi
    done

    # Search forward for the next heading or end of section
    BLOCK_END="$TOTAL"
    for i in $(seq "$((MATCH_LINE + 1))" "$TOTAL"); do
        LINE=$(sed -n "${i}p" "$FILE")
        if echo "$LINE" | grep -qE '^#{1,3} |^---$'; then
            BLOCK_END="$((i - 1))"
            break
        fi
    done

    REFS=""
fi

# Compute context range
CTX_START="$((BLOCK_START - CONTEXT_LINES))"
[ "$CTX_START" -lt 1 ] && CTX_START=1

# Output
echo "=== CONTEXT (lines ${CTX_START}-$((BLOCK_START - 1))) ==="
if [ "$CTX_START" -lt "$BLOCK_START" ]; then
    sed -n "${CTX_START},$((BLOCK_START - 1))p" "$FILE"
fi

echo ""
echo "=== BLOCK (lines ${BLOCK_START}-${BLOCK_END}) ==="
sed -n "${BLOCK_START},${BLOCK_END}p" "$FILE"

# Append referenced equations if any
if [ -n "$REFS" ]; then
    echo ""
    echo "=== REFERENCED EQUATIONS ==="
    for ref in $REFS; do
        REFLINE=$(grep -n "label{${ref}}" "$FILE" | head -1 | cut -d: -f1)
        if [ -n "$REFLINE" ]; then
            # Print 3 lines around the label
            RSTART="$((REFLINE - 1))"
            [ "$RSTART" -lt 1 ] && RSTART=1
            REND="$((REFLINE + 2))"
            [ "$REND" -gt "$TOTAL" ] && REND="$TOTAL"
            sed -n "${RSTART},${REND}p" "$FILE"
            echo ""
        fi
    done
fi
