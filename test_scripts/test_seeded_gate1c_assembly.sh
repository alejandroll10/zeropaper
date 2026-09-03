#!/bin/bash
# Regression for #161: seeded/faithful Gate 1c uses the one-shot prototype
# contract and describes downstream feasibility without mode-specific retries.
set -u
cd "$(dirname "$0")/.."

FAILS=0
fail() { echo "✗ $1"; FAILS=$((FAILS+1)); }
pass() { echo "✓ $1"; }
expect_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq -- "$text" "$file" && pass "$label" || fail "$label"
}
reject_text() {
    local file="$1" text="$2" label="$3"
    grep -Fq -- "$text" "$file" && fail "$label" || pass "$label"
}

ROOT="$(mktemp -d /tmp/seeded-gate1c.XXXXXX)"
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

    stage1="$ROOT/$shape/docs/stage_1.md"
    expect_text "$stage1" \
        'do **not** re-run `idea-prototyper` at this gate' \
        "$shape preserves the one-shot prototype contract"
    expect_text "$stage1" \
        "The active mode's Stage 2 development and gate sequence" \
        "$shape uses mode-neutral seeded routing"
    expect_text "$stage1" \
        "the real attempt happens in Stage 2 under the active mode's development and gate sequence" \
        "$shape uses mode-neutral survivor rationale"
    expect_text "$stage1" \
        '"Most promising alternative technique" ("Most promising alternative angle" in modes whose prototyper uses that heading)' \
        "$shape carries the prototyper's existing alternative"
    reject_text "$stage1" "then try **one alternative formalization**" \
        "$shape has no obsolete seeded retry"
    reject_text "$stage1" "prototype_retry" \
        "$shape has no retired retry state"
    reject_text "$stage1" "Gate 2's math audit, with its 3-attempt budget" \
        "$shape has no theory-first Gate 2 rationale"
    reject_text "$stage1" "<!-- DATA_FIRST_START -->" \
        "$shape has no unresolved data-first marker"
done

for shape in empirical_seed empirical_faithful; do
    stage1="$ROOT/$shape/docs/stage_1.md"
    prototype="$ROOT/$shape/.claude/agents/idea-prototyper.md"
    expect_text "$stage1" \
        "The object to identify is the empirical question the selected idea poses" \
        "$shape identification object is anchored in selected idea"
    expect_text "$prototype" "## Predicted relationship" \
        "$shape prototype requires predicted-relationship section"
    for field in Sign Channel Population; do
        expect_text "$prototype" "- **$field:**" \
            "$shape prototype requires $field"
    done
done

echo
if [ "$FAILS" -gt 0 ]; then
    echo "FAILED: $FAILS check(s)"
    exit 1
fi
echo "All seeded Gate 1c assembly checks passed."
