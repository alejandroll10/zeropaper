#!/bin/bash
# Focused contract tests for the setup configuration module extracted in #255.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_MODULE="$REPO_ROOT/deploy_assets/scripts/setup/resolve_config.sh"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

assert_equal() {
    local name="$1" expected="$2" actual="$3"
    if [ "$actual" != "$expected" ]; then
        echo "FAIL: $name" >&2
        echo "--- expected ---" >&2
        printf '%s\n' "$expected" >&2
        echo "--- actual ---" >&2
        printf '%s\n' "$actual" >&2
        exit 1
    fi
}

resolve_summary() (
    unset PUBLISH_ORG PUBLISH_VISIBILITY
    # shellcheck source=../deploy_assets/scripts/setup/resolve_config.sh
    source "$CONFIG_MODULE"
    resolve_setup_config "$@"
    printf 'resolved|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n' \
        "$PROJECT_NAME" "$VARIANT" "$MODE" "$LOCAL" "$AGENT_DIR" \
        "$INITIAL_TIER" "$DOC_SUBTITLE" "$PUBLISH_ORG" \
        "$PUBLISH_VISIBILITY" "${EXTENSIONS[*]}"
)

assert_equal "default finance resolution" \
    'resolved||finance||0|finance|top-3-fin|Autonomous Theory Paper Pipeline|automated-papers-produced|private|' \
    "$(resolve_summary)"

assert_equal "empirical-first implication and descriptors" \
    $'Info: --mode empirical-first implies --ext empirical (auto-added).\nresolved|paper|finance|empirical-first|1|finance|top-3-fin|Autonomous Empirical Paper Pipeline|automated-papers-produced|private|empirical' \
    "$(resolve_summary paper --variant finance --mode empirical-first --local)"

assert_equal "llm cognition implication" \
    $'Info: --variant llm_cognition implies --ext theory_llm (auto-added).\nresolved||llm_cognition||0|llm_cognition|top-ml|Autonomous Theory Paper Pipeline|automated-papers-produced|private|theory_llm' \
    "$(resolve_summary --variant llm_cognition)"

assert_equal "report suppresses llm cognition implication" \
    'resolved||llm_cognition|report|0|llm_cognition|top-ml|Autonomous Referee Report Pipeline|automated-papers-produced|private|' \
    "$(resolve_summary --variant llm_cognition --mode report)"

assert_equal "legacy expansion and ordered deduplication" \
    'resolved|final-name|finance||0|finance|top-3-fin|Autonomous Theory Paper Pipeline|automated-papers-produced|private|theory_llm empirical' \
    "$(resolve_summary first-name --ext theory_llm --ext empirical --variant finance_llm --theory-llm --ext theory_llm final-name)"

custom_publish_summary=$(
    export PUBLISH_ORG="research-org"
    export PUBLISH_VISIBILITY="public"
    # shellcheck source=../deploy_assets/scripts/setup/resolve_config.sh
    source "$CONFIG_MODULE"
    resolve_setup_config --variant macro
    printf '%s|%s\n' "$PUBLISH_ORG" "$PUBLISH_VISIBILITY"
)
assert_equal "publishing environment overrides" 'research-org|public' "$custom_publish_summary"

reentrant_descriptor_summary=$(
    source "$CONFIG_MODULE"
    resolve_setup_config --variant llm_cognition >/dev/null
    resolve_setup_config --variant finance >/dev/null
    printf '%s|%s|%s\n' \
        "$PRINCIPLED_MECHANISM_PHRASE" \
        "$CHARACTERIZE_EXAMPLE_BULLET" \
        "$NUMERICAL_VERIFICATION_BULLET"
)
assert_equal "sequential resolution resets variant descriptors" \
    "falls out of economics|If a result holds under CARA but not CRRA, find the exact condition on preferences that makes it work.|Don't settle for numerical verification of what should be a theorem." \
    "$reentrant_descriptor_summary"

if (
    source "$CONFIG_MODULE"
    resolve_setup_config --variant llm_cognition >/dev/null
    variant_wants_skill ssj
); then
    fail "llm_cognition unexpectedly enables ssj"
fi
if ! (
    source "$CONFIG_MODULE"
    resolve_setup_config --variant finance >/dev/null
    variant_wants_skill ssj
); then
    fail "finance unexpectedly disables ssj"
fi

set +e
unknown_extension_output=$(
    source "$CONFIG_MODULE"
    reject_unknown_extension not_an_extension
)
unknown_extension_status=$?
set -e
[ "$unknown_extension_status" -eq 1 ] \
    || fail "unknown extension returned $unknown_extension_status instead of 1"
assert_equal "unknown extension diagnostic" \
    $'Unknown extension: not_an_extension\nAvailable extensions: empirical, theory_llm' \
    "$unknown_extension_output"

echo "PASS: setup configuration resolution"
