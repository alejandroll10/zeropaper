#!/bin/bash
# Regression test for the mode-marker resolver's block-removal / marker-strip ordering.
#
# The removal pattern eats up to 2 trailing newlines so a removed block does not
# leave a stray blank line behind. Before v2.17.1 the resolver interleaved removals
# and strips by family, so a removal that ran AFTER a neighbouring block's markers
# had been stripped would see the neighbour's newly-exposed leading blank line and
# eat that too — silently deleting a blank line from content that was supposed to be
# kept. It stayed invisible while every site had at most one mode block; adding a
# MEASUREMENT_FIRST twin next to an existing NO_MODE/EMPIRICAL_FIRST pair exposed it
# (the empirical-first idea-reviewer lost the blank line under its ADVANCE header,
# gluing the ranked list onto the header and breaking the markdown list).
#
# setup.sh now runs every removal before any strip, making output independent of
# family order. These tripwires check the invariant at the real multi-block sites.
# Build-time only (test_scripts/ is removed on deploy).
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }

# Assert that $2 (a regex) is preceded by a blank line in file $1 — i.e. the
# paragraph break survived resolution.
assert_blank_before() {
    local file="$1" pattern="$2" label="$3"
    if [ ! -f "$file" ]; then fail "$label — missing $file"; return; fi
    python3 - "$file" "$pattern" <<'PY' && pass "$label" || fail "$label — paragraph break collapsed"
import re, sys
lines = open(sys.argv[1]).read().split("\n")
rx = re.compile(sys.argv[2])
hits = [i for i, l in enumerate(lines) if rx.search(l)]
if not hits:
    sys.exit(2)                      # pattern absent -> treated as failure
sys.exit(0 if all(i > 0 and lines[i-1].strip() == "" for i in hits) else 1)
PY
}

build() {  # $1 = variant, rest = extra flags
    local v="$1"; shift
    rm -rf test_output
    ./setup.sh "test_output/$v" --variant "$v" --assemble-only --no-model-probe "$@" >/dev/null 2>&1 || return 1
}

# The idea-reviewer ADVANCE site carries three sibling mode blocks
# (NO_MODE / MEASUREMENT_FIRST / EMPIRICAL_FIRST). Each mode must render its own
# ranked list as a proper markdown list, i.e. with the paragraph break intact.
echo "── idea-reviewer ADVANCE list ──"

if build finance; then
    assert_blank_before "test_output/finance/.claude/agents/idea-reviewer.md" \
        '^1\. \*\*\[Approach name\]\*\*' "theory-first (no mode): ranked list keeps its paragraph break"
else
    fail "finance default build failed"
fi

if build finance --mode empirical-first; then
    assert_blank_before "test_output/finance/.claude/agents/idea-reviewer.md" \
        '^1\. \*\*\[Approach name\]\*\*' "empirical-first: ranked list keeps its paragraph break"
else
    fail "finance --mode empirical-first build failed"
fi

if build llm_cognition --mode measurement-first; then
    assert_blank_before "test_output/llm_cognition/.claude/agents/idea-reviewer.md" \
        '^1\. \*\*\[Approach name\]\*\*' "measurement-first: ranked list keeps its paragraph break"
    # The MEASUREMENT_FIRST paper-writer / stage_5 blocks sit next to NO_MODE and
    # EMPIRICAL_FIRST twins at their own sites; a leaked marker there would mean the
    # pairing broke rather than the ordering.
    if grep -rqE '<!-- (THEORY_FIRST|EMPIRICAL_FIRST|MEASUREMENT_FIRST|NO_MODE)_(START|END) -->' \
        test_output/llm_cognition 2>/dev/null; then
        fail "measurement-first: mode markers leaked into the deployment"
    else
        pass "measurement-first: no mode markers leaked"
    fi
else
    fail "llm_cognition --mode measurement-first build failed"
fi

if build finance --mode data-first; then
    assert_blank_before "test_output/finance/.claude/agents/idea-reviewer.md" \
        '^1\. \*\*\[Architecture name\]\*\*' "data-first: ranked list keeps its paragraph break"
    # v2.30.0 added a fourth sibling family (DATA_FIRST) at several existing
    # multi-block sites — scorer-core's fidelity blocks, the idea-reviewer
    # ADVANCE site, the stage-2 gate chain. Any leaked marker here means the
    # family pairing broke rather than the ordering.
    if grep -rqE '<!-- (THEORY_FIRST|EMPIRICAL_FIRST|MEASUREMENT_FIRST|DATA_FIRST|NO_MODE)_(START|END) -->' \
        test_output/finance 2>/dev/null; then
        fail "data-first: mode markers leaked into the deployment"
    else
        pass "data-first: no mode markers leaked"
    fi
    # scorer-core carries adjacent EMPIRICAL_FIRST/DATA_FIRST fidelity blocks;
    # the kept data-first block must render with its paragraph break intact.
    assert_blank_before "test_output/finance/.claude/agents/scorer.md" \
        '^\*\*Data-first supersedes the own-design-critique' "data-first: scorer fidelity block keeps its paragraph break"
else
    fail "finance --mode data-first build failed"
fi

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All marker-resolver adjacency checks passed."
