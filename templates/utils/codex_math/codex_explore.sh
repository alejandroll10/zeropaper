#!/usr/bin/env bash
# Ask Codex (gpt-5.6-sol) to explore a mathematical conjecture or question.
# Codex investigates rigorously: proves, disproves, or characterizes.
#
# Usage:
#   codex_explore.sh <question> [context_file] [reasoning_effort] [output_dir]
#
# Examples:
#   codex_explore.sh "Does rational inattention produce isoelastic demand?"
#   codex_explore.sh "What taste-shock distributions give logit demand?" setup.tex high
#   codex_explore.sh "Is log-concavity sufficient for approximate isoelasticity?"
#
# context_file: optional file to include as context (definitions, notation)
# reasoning_effort: low | medium (default) | high
# output_dir: where to save results (default: ./output/codex_explorations)

set -euo pipefail

# Pin the tier explicitly. The bare `gpt-5.6` alias routes to Sol today, but
# aliases are not a contract; Sol is the tier we actually want here (FrontierMath
# Tier 4: Sol 83% vs Terra 68.3%), and this is a sparingly-called co-processor,
# so its price is not load-bearing.
MODEL="gpt-5.6-sol"

QUESTION="${1:?Usage: codex_explore.sh <question> [context_file] [reasoning_effort] [output_dir]}"

# Robust argument parsing: detect if $2 is an effort level rather than a context file
CONTEXT_FILE=""
EFFORT="medium"
OUTDIR="./output/codex_explorations"

shift  # consume $1 (question)
for arg in "$@"; do
    case "$arg" in
        low|medium|high) EFFORT="$arg" ;;
        # gpt-5.6 accepts these too, but the pipeline deliberately caps at `high`
        # (see the codex-math skill). Reject loudly: the wildcard below would
        # otherwise take `max` for an output dir and quietly write to ./max.
        none|xhigh|max|ultra)
            echo "ERROR: reasoning_effort '$arg' is not used by this pipeline — use low|medium|high" >&2
            exit 1 ;;
        *) if [ -f "$arg" ]; then
               CONTEXT_FILE="$arg"
           elif [ -d "$arg" ] || [[ "$arg" == */* ]]; then
               OUTDIR="$arg"
           elif [[ "$arg" == *.* ]]; then
               echo "WARNING: '$arg' looks like a file but does not exist — skipping" >&2
           else
               echo "WARNING: '$arg' is not a file or recognized effort level — treating as output dir" >&2
               OUTDIR="$arg"
           fi ;;
    esac
done

mkdir -p "$OUTDIR"

SAFE_NAME=$(echo "$QUESTION" | tr ' /:{}\\?.' '_' | cut -c1-60 | tr -cd '[:alnum:]_-')
OUTFILE="${OUTDIR}/${SAFE_NAME}.md"
TMP="/tmp/codex_explore_${SAFE_NAME}_$$.txt"
LOG="${OUTDIR}/${SAFE_NAME}.log"

# Load context if provided
CONTEXT=""
if [ -n "$CONTEXT_FILE" ] && [ -f "$CONTEXT_FILE" ]; then
    CONTEXT=$(cat "$CONTEXT_FILE")
fi

echo "[codex-math] Exploring: '$QUESTION' ($MODEL, effort=$EFFORT)"
echo "[codex-math] Live progress: tail -f $LOG"

PROMPT="You are a mathematician investigating a conjecture for a top economics journal. Be extremely rigorous.

For each claim:
- If you can prove it, write a complete proof. Show every algebraic step. State where each assumption is used.
- If you can disprove it, give a concrete counterexample with specific parameter values. Verify the counterexample numerically.
- If you cannot resolve it, state precisely what you can prove (sufficient conditions, special cases) and what remains open.

Try multiple proof strategies if the first one fails. Do not give up after one approach.
Show all intermediate steps. Write in LaTeX where appropriate.
Do not hand-wave. 'It can be shown that' is not acceptable — show it."

if [ -n "$CONTEXT" ]; then
    PROMPT="$PROMPT

---
CONTEXT (definitions, notation, prior results):
$CONTEXT"
fi

PROMPT="$PROMPT

---
QUESTION:
$QUESTION
---

Report format:
## Summary (1-2 sentences)
## Investigation
[detailed math with proofs/counterexamples]
## Conclusions
[what is proved, what is conjectured, what is open]
## LaTeX propositions (if any new results)"

codex exec </dev/null --sandbox workspace-write --skip-git-repo-check \
    -c "model=\"$MODEL\"" \
    -c "model_reasoning_effort=\"$EFFORT\"" \
    -c 'model_reasoning_summary="detailed"' \
    -o "$TMP" \
    "$PROMPT" 2>&1 | tee "$LOG"

if [ -f "$TMP" ]; then
    {
        echo "# Codex Exploration: $QUESTION"
        echo "**Context:** ${CONTEXT_FILE:-none}"
        echo "**Model:** $MODEL"
        echo "**Effort:** $EFFORT"
        echo "**Date:** $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo ""
        cat "$TMP"
    } > "$OUTFILE"
    echo ""
    echo "[codex-math] Exploration saved to: $OUTFILE"
else
    echo "WARNING: No output file produced" >&2
    exit 1
fi
