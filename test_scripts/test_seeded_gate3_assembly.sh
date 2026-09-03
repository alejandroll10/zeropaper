#!/bin/bash
# Regression for #280: seed/faithful Gate 3 wording is mode-neutral and waives
# only Stage 2b, never a mode/extension evidence stage or Gate 4 entry check.
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }
expect_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq "$text" "$file" && pass "$label" || fail "$label"
}
reject_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq "$text" "$file" && fail "$label" || pass "$label"
}

ROOT="$(mktemp -d /tmp/seeded-gate3.XXXXXX)"
trap 'rm -rf "$ROOT"' EXIT

for shape in \
    base_seed base_faithful \
    empirical_seed empirical_faithful \
    measurement_seed measurement_faithful \
    data_seed data_faithful; do
    case "$shape" in
        base_seed)
            args=(--variant finance --seed)
            ;;
        base_faithful)
            args=(--variant finance --faithful)
            ;;
        empirical_seed)
            args=(--variant finance --mode empirical-first --seed)
            ;;
        empirical_faithful)
            args=(--variant finance --mode empirical-first --faithful)
            ;;
        measurement_seed)
            args=(--variant llm_cognition --mode measurement-first --seed)
            ;;
        measurement_faithful)
            args=(--variant llm_cognition --mode measurement-first --faithful)
            ;;
        data_seed)
            args=(--variant finance --mode data-first --seed)
            ;;
        data_faithful)
            args=(--variant finance --mode data-first --faithful)
            ;;
    esac

    if ./setup.sh "$ROOT/$shape" "${args[@]}" \
        --assemble-only --no-model-probe >/dev/null 2>&1; then
        pass "$shape assembly"
    else
        fail "$shape assembly"
        continue
    fi

    stage2="$ROOT/$shape/docs/stage_2.md"
    expect_text "$stage2" \
        "every applicable Stage 3a/3b evidence stage and audit before Gate 4" \
        "$shape preserves downstream evidence"
    expect_text "$stage2" \
        "this routing does not waive any mode- or extension-specific replacement evidence, deferred audit, or Gate 4 entry check" \
        "$shape confines the Gate 3 exception"
    reject_text "$stage2" "Gate 2's math audit has already established" \
        "$shape has no theory-first audit rationale"
    reject_text "$stage2" "different equilibrium selection" \
        "$shape has no theory-only reformulation lever"
    reject_text "$stage2" "<!-- DATA_FIRST_START -->" \
        "$shape has no unresolved data-first marker"
done

for shape in base_seed empirical_seed measurement_seed data_seed; do
    stage2="$ROOT/$shape/docs/stage_2.md"
    expect_text "$stage2" \
        "the current Stage 2 artifact in every mode" \
        "$shape explains the legacy concern filename"
    expect_text "$stage2" \
        "a different formulation, scope boundary, dimension, or other alteration" \
        "$shape uses mode-neutral reformulation levers"
done

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All seeded Gate 3 assembly checks passed."
