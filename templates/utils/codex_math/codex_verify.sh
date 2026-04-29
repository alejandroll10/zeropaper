#!/usr/bin/env bash
# Verify a mathematical proof using OpenAI Codex (gpt-5.5).
# Extracts the block, pipes it to Codex, saves the result.
#
# Usage:
#   codex_verify.sh <file> <pattern> [reasoning_effort] [output_dir]
#
# Examples:
#   codex_verify.sh paper/model.tex "Theorem 1"
#   codex_verify.sh paper/model.tex "prop:crra" high
#   codex_verify.sh notes.md "Proposition 3" high /tmp/audits
#
# reasoning_effort: low | medium (default) | high
# output_dir: where to save results (default: ./output/codex_audits)

set -euo pipefail

FILE="${1:?Usage: codex_verify.sh <file> <pattern> [reasoning_effort] [output_dir]}"
PATTERN="${2:?Usage: codex_verify.sh <file> <pattern> [reasoning_effort] [output_dir]}"
EFFORT="${3:-medium}"
OUTDIR="${4:-./output/codex_audits}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUTDIR"

# Sanitize pattern for filename
SAFE_NAME=$(echo "$PATTERN" | tr ' /:{}\\' '_' | tr -cd '[:alnum:]_-')
OUTFILE="${OUTDIR}/${SAFE_NAME}.md"
TMP="/tmp/codex_verify_${SAFE_NAME}_$$.txt"

echo "[codex-math] Extracting: '$PATTERN' from $FILE"
CONTENT=$("$SCRIPT_DIR/extract_block.sh" "$FILE" "$PATTERN")

if [ -z "$CONTENT" ]; then
    echo "ERROR: Could not extract content" >&2
    exit 1
fi

echo "[codex-math] Sending to Codex (gpt-5.5, effort=$EFFORT)..."

codex exec --full-auto --skip-git-repo-check \
    -c "model_reasoning_effort=\"$EFFORT\"" \
    -o "$TMP" \
    "You are a mathematical proof auditor at a top academic journal. Verify the following proof with extreme rigor.

For each logical step, report PASS or FAIL.
If FAIL, explain exactly which step is wrong and why — give the specific algebra that breaks.

Check:
1. Algebraic correctness — re-derive every equation from the previous step. Show your work.
2. Logical completeness — identify any gaps where a step is asserted without justification.
3. Assumptions — are stated hypotheses actually sufficient? Are there unstated assumptions being used?
4. Boundary cases — what happens at 0, 1, infinity? Does the result degenerate?
5. Second-order conditions — if an optimum is claimed, verify it is a maximum, not a minimum or saddle point.
6. Domain issues — does any denominator vanish? Is any function evaluated outside its domain?

Be adversarial. Assume there are errors until you verify otherwise. Do not give the benefit of the doubt.
If a step is correct, show why it follows. If a step is wrong, give a specific counterexample or the exact algebraic error.

---
$CONTENT
---

Report format:
## Verdict: PASS or FAIL
## Step-by-step verification
[numbered steps, each with PASS/FAIL]
## Errors found (if any)
[specific errors with exact equation/line references]
## Concerns (non-blocking issues)
[things that are technically correct but could be improved]" 2>&1

# Save result
if [ -f "$TMP" ]; then
    {
        echo "# Codex Verify: $PATTERN"
        echo "**File:** $FILE"
        echo "**Effort:** $EFFORT"
        echo "**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        cat "$TMP"
    } > "$OUTFILE"
    echo ""
    echo "[codex-math] Result saved to: $OUTFILE"
    echo "[codex-math] Verdict: $(grep -oE 'PASS|FAIL' "$TMP" | head -1 || echo 'UNKNOWN')"
else
    echo "WARNING: No output file produced" >&2
    exit 1
fi
