#!/usr/bin/env bash
# Regression coverage for setup.sh's opt-in GitHub publication contract (#234).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETUP="$REPO_ROOT/setup.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-publish-test.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

expect_failure() {
    local expected="$1"
    shift
    local output="$TEST_ROOT/failure.log"
    if "$@" >"$output" 2>&1; then
        fail "command unexpectedly succeeded: $*"
    fi
    grep -Fq -- "$expected" "$output" \
        || fail "missing failure text '$expected' for: $*"
}

# Help must expose the safe default and both explicit spellings.
HELP_OUTPUT="$TEST_ROOT/help.log"
"$SETUP" --help >"$HELP_OUTPUT"
grep -Fq -- "Publishing stays off" "$HELP_OUTPUT" || fail "help omits publishing default"
grep -Fq -- "--publish" "$HELP_OUTPUT" || fail "help omits --publish"
grep -Fq -- "--no-publish" "$HELP_OUTPUT" || fail "help omits --no-publish"
grep -Fq -- "PUBLISH_ORG=<org>" "$HELP_OUTPUT" || fail "help omits PUBLISH_ORG"

# Parser errors happen before any project directory is created, independent of
# flag order.
expect_failure "--publish and --no-publish are mutually exclusive" \
    "$SETUP" parser-a --publish --no-publish
expect_failure "--publish and --no-publish are mutually exclusive" \
    "$SETUP" parser-b --no-publish --publish
expect_failure "--publish cannot be used with --assemble-only" \
    "$SETUP" parser-c --publish --assemble-only
expect_failure "--publish cannot be used with --mode report" \
    "$SETUP" parser-d --mode report --publish
expect_failure "--publish requires a non-empty PUBLISH_ORG" \
    env PUBLISH_ORG= "$SETUP" parser-e --publish
expect_failure "PUBLISH_VISIBILITY must be private, public, or internal" \
    env PUBLISH_VISIBILITY=secret "$SETUP" parser-f --publish

# Build a committed local template checkout so full setup exercises the real
# checkout-local assembly/commit/publish path without touching the network.
TEMPLATE_REPO="$TEST_ROOT/template"
git clone -q "$REPO_ROOT" "$TEMPLATE_REPO"
cp "$REPO_ROOT/setup.sh" "$TEMPLATE_REPO/setup.sh"
cp "$REPO_ROOT/VERSION" "$TEMPLATE_REPO/VERSION"
# The decomposition modules may be uncommitted in the working tree under test,
# so the temporary production source must stage them alongside setup.sh. A real
# release commit naturally carries the same files.
mkdir -p "$TEMPLATE_REPO/deploy_assets/scripts/setup"
cp "$REPO_ROOT/deploy_assets/scripts/setup/"*.sh "$TEMPLATE_REPO/deploy_assets/scripts/setup/"
cp "$REPO_ROOT/deploy_assets/scripts/apply_extension_empirical.sh" \
    "$REPO_ROOT/deploy_assets/scripts/apply_extension_theory_llm.sh" \
    "$REPO_ROOT/deploy_assets/scripts/resolve_model_fallbacks.py" \
    "$TEMPLATE_REPO/deploy_assets/scripts/"
git -C "$TEMPLATE_REPO" add setup.sh VERSION deploy_assets/scripts/setup \
    deploy_assets/scripts/apply_extension_empirical.sh \
    deploy_assets/scripts/apply_extension_theory_llm.sh \
    deploy_assets/scripts/resolve_model_fallbacks.py
if ! git -C "$TEMPLATE_REPO" diff --cached --quiet; then
    git -C "$TEMPLATE_REPO" \
        -c user.name='Publish Test' -c user.email='publish-test@example.invalid' \
        commit -qm 'test: stage working publication changes'
fi
SETUP="$TEMPLATE_REPO/setup.sh"

FAKE_BIN="$TEST_ROOT/bin"
mkdir -p "$FAKE_BIN"

cat >"$FAKE_BIN/uv" <<'EOF'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"${TEST_UV_LOG:?}"
if [ "${1:-}" = "venv" ]; then
    eval "target=\${$#}"
    mkdir -p "$target/bin" "$target/lib/python3.12/site-packages"
    cat > "$target/bin/python3" <<'PYEOF'
#!/usr/bin/env bash
venv_root="$(cd "$(dirname "$0")/.." && pwd)"
printf '%s\n' "$venv_root/lib/python3.12/site-packages"
PYEOF
    chmod +x "$target/bin/python3"
fi
exit 0
EOF
cat >"$FAKE_BIN/claude" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat >"$FAKE_BIN/bwrap" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat >"$FAKE_BIN/gh" <<'EOF'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"${TEST_GH_LOG:?}"
if [ "${1:-}" = "auth" ] && [ "${2:-}" = "status" ]; then
    if [ "${TEST_GH_AUTH_RC:-0}" != "0" ]; then
        echo "simulated gh auth failure" >&2
        exit "$TEST_GH_AUTH_RC"
    fi
    exit 0
fi
if [ "${1:-}" = "api" ] && [ "${2:-}" = "user" ]; then
    if [ "${TEST_GH_USER_RC:-0}" != "0" ]; then
        echo "simulated gh user lookup failure" >&2
        exit "$TEST_GH_USER_RC"
    fi
    echo "${TEST_GH_USER_VALUE-publish-test-user}"
    exit 0
fi
if [ "${1:-}" = "api" ] && [[ "${2:-}" == orgs/*/memberships/* ]]; then
    if [ "${TEST_GH_MEMBERSHIP_RC:-0}" != "0" ]; then
        echo "simulated gh membership lookup failure" >&2
        exit "$TEST_GH_MEMBERSHIP_RC"
    fi
    echo "${TEST_GH_MEMBERSHIP_STATE-active}"
    exit 0
fi
if [ "${1:-}" = "repo" ] && [ "${2:-}" = "create" ]; then
    if [ "${TEST_GH_REPO_CREATE_RC:-0}" != "0" ]; then
        echo "simulated gh partial failure" >&2
        exit "$TEST_GH_REPO_CREATE_RC"
    fi
    exit 0
fi
exit 0
EOF
chmod +x "$FAKE_BIN/uv" "$FAKE_BIN/claude" "$FAKE_BIN/bwrap" "$FAKE_BIN/gh"

RUN_ROOT="$TEST_ROOT/runs"
mkdir -p "$RUN_ROOT"
GH_LOG="$TEST_ROOT/gh.log"
: >"$GH_LOG"
UV_LOG="$TEST_ROOT/uv.log"
: >"$UV_LOG"
TEST_HOME="$TEST_ROOT/home"
mkdir -p "$TEST_HOME"
GLOBAL_HOOKS="$TEST_ROOT/global-hooks"
GIT_TEMPLATE="$TEST_ROOT/git-template"
GIT_HOOK_MARKER="$TEST_ROOT/git-hook-ran"
mkdir -p "$GLOBAL_HOOKS" "$GIT_TEMPLATE/hooks"
printf '%s\n' \
    '#!/bin/bash' \
    ': > "${TEST_GIT_HOOK_MARKER:?}"' \
    'printf "HOOK_INJECTION\\n" >> CLAUDE.md' \
    > "$GLOBAL_HOOKS/pre-commit"
cp "$GLOBAL_HOOKS/pre-commit" "$GIT_TEMPLATE/hooks/pre-commit"
chmod +x "$GLOBAL_HOOKS/pre-commit" "$GIT_TEMPLATE/hooks/pre-commit"
printf '%s\n' \
    '[user]' \
    '    name = Publish Test' \
    '    email = publish-test@example.invalid' \
    '[core]' \
    "    hooksPath = $GLOBAL_HOOKS" \
    > "$TEST_HOME/.gitconfig"

COMMON_ENV=(
    env
    HOME="$TEST_HOME"
    PATH="$FAKE_BIN:$PATH"
    TEST_GH_LOG="$GH_LOG"
    TEST_UV_LOG="$UV_LOG"
    TEST_GIT_HOOK_MARKER="$GIT_HOOK_MARKER"
    GIT_TEMPLATE_DIR="$GIT_TEMPLATE"
    GIT_AUTHOR_NAME='Publish Test'
    GIT_AUTHOR_EMAIL='publish-test@example.invalid'
    GIT_COMMITTER_NAME='Publish Test'
    GIT_COMMITTER_EMAIL='publish-test@example.invalid'
)

# Default production setup must never invoke gh, even when gh is available and
# apparently authenticated.
DEFAULT_LOG="$TEST_ROOT/default.log"
"${COMMON_ENV[@]}" "$SETUP" "$RUN_ROOT/default-project" --no-model-probe \
    >"$DEFAULT_LOG" 2>&1
grep -Fq -- "Publishing skipped: local repository only" "$DEFAULT_LOG" \
    || fail "default production setup did not report local-only behavior"
[ ! -s "$GH_LOG" ] || fail "default production setup invoked gh"
git -C "$RUN_ROOT/default-project" rev-parse --verify HEAD >/dev/null \
    || fail "default production setup did not commit the local repository"
[ ! -e "$GIT_HOOK_MARKER" ] || fail "ambient Git hook executed during production setup"
if grep -Fq 'HOOK_INJECTION' "$RUN_ROOT/default-project/CLAUDE.md"; then
    fail "ambient Git hook altered production output"
fi
template_commit="$(git -C "$TEMPLATE_REPO" rev-parse HEAD)"
jq -e --arg commit "$template_commit" '
    .source.kind == "checkout"
    and .source.commit == $commit
    and .source.dirty == false
    and (.source.content_digest | test("^sha256:[0-9a-f]{64}$"))
    and .source.update_channel == "checkout"
' "$RUN_ROOT/default-project/.deploy_manifest.json" >/dev/null \
    || fail "default production setup recorded incorrect source provenance"
grep -Fq -- "pip install --python ./.venv -r" "$UV_LOG" \
    || fail "default production setup did not provision project dependencies"
[ -f "$RUN_ROOT/default-project/.venv/lib/python3.12/site-packages/_pipeline_dotenv_guard.pth" ] \
    || fail "default production setup did not install the dotenv guard"

# Provisioning remains ordered at its historical boundaries: core first, SSJ
# with the finance skill, then extension dependencies in the user's extension
# order. This full checkout-local path verifies the coordinator/module wiring, not
# merely the provisioning functions in isolation.
: >"$UV_LOG"
PROVISION_LOG="$TEST_ROOT/provision.log"
"${COMMON_ENV[@]}" "$SETUP" "$RUN_ROOT/provision-project" --no-model-probe \
    --ext theory_llm --ext empirical >"$PROVISION_LOG" 2>&1
python3 - "$UV_LOG" <<'PY' || fail "dependency provisioning order changed"
import sys

lines = [line.strip() for line in open(sys.argv[1]) if line.startswith("pip install ")]
needles = [
    "/.arpipeline/update_inputs/deps/core.txt",
    "/.arpipeline/update_inputs/deps/ssj.txt",
    "/.arpipeline/update_inputs/deps/extensions/theory_llm.txt",
    "/.arpipeline/update_inputs/deps/extensions/empirical.txt",
]
positions = []
for needle in needles:
    matches = [i for i, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        print(f"expected one {needle!r} install, saw {len(matches)}; uv log={lines!r}", file=sys.stderr)
        raise SystemExit(1)
    positions.append(matches[0])
if positions != sorted(positions):
    print(f"dependency order mismatch: positions={positions!r}; uv log={lines!r}", file=sys.stderr)
    raise SystemExit(1)
PY

# Full deployments use the same normalized, ancestor-validated destination for
# checking and mutation. A `symlink/..` spelling must not regain kernel-level
# traversal after validation and create a project in foreign storage.
lexical_base="$RUN_ROOT/lexical-destination"
lexical_foreign="$RUN_ROOT/lexical-foreign"
mkdir -p "$lexical_base" "$lexical_foreign/sub"
ln -s "$lexical_foreign/sub" "$lexical_base/linked-parent"
"${COMMON_ENV[@]}" "$SETUP" \
    "$lexical_base/linked-parent/../escaped-project" --no-model-probe \
    >"$TEST_ROOT/lexical-destination.log" 2>&1
[ -f "$lexical_base/escaped-project/.deploy_manifest.json" ] \
    || fail "normalized full destination was not created at its validated path"
[ ! -e "$lexical_foreign/escaped-project" ] \
    || fail "full destination escaped through symlink/.. traversal"

# Explicit publishing prints the target before mutation and reaches gh with the
# configured org/visibility. The fake gh makes this test side-effect free.
: >"$GH_LOG"
PUBLISH_LOG="$TEST_ROOT/publish.log"
"${COMMON_ENV[@]}" PUBLISH_ORG=test-org PUBLISH_VISIBILITY=private \
    "$SETUP" "$RUN_ROOT/published-project" --no-model-probe --publish \
    >"$PUBLISH_LOG" 2>&1
grep -Eq -- '^Publish requested: test-org/published-project-[0-9a-f]{8} \(private\)$' "$PUBLISH_LOG" \
    || fail "explicit publish did not print its exact target"
grep -Eq -- '^repo create test-org/published-project-[0-9a-f]{8} --private --source=\. --remote=origin --push$' "$GH_LOG" \
    || fail "explicit publish did not call gh repo create with the configured target"

# gh repo create is compound: repository creation may succeed before remote
# setup or push fails. The failure path must not claim no remote exists.
: >"$GH_LOG"
PARTIAL_LOG="$TEST_ROOT/partial.log"
"${COMMON_ENV[@]}" TEST_GH_REPO_CREATE_RC=1 PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/partial-project" --no-model-probe --publish \
    >"$PARTIAL_LOG" 2>&1
grep -Fq -- "remote state may be partial" "$PARTIAL_LOG" \
    || fail "partial publication failure did not report uncertain remote state"
grep -Fq -- "simulated gh partial failure" "$PARTIAL_LOG" \
    || fail "partial publication failure suppressed gh's diagnostic"
grep -Eq -- '^    Inspect https://github.com/test-org/partial-project-[0-9a-f]{8} before retrying\.$' "$PARTIAL_LOG" \
    || fail "partial publication failure did not print the exact target URL"
if grep -Fq -- "Repo remains local" "$PARTIAL_LOG"; then
    fail "partial publication failure falsely claimed no remote exists"
fi

# Read-only GitHub preflight failures must stay distinct from confirmed inactive
# membership and must never reach the mutating repo-create call.
: >"$GH_LOG"
USER_FAILURE_LOG="$TEST_ROOT/user-failure.log"
"${COMMON_ENV[@]}" TEST_GH_USER_RC=1 PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/user-failure-project" --no-model-probe --publish \
    >"$USER_FAILURE_LOG" 2>&1
grep -Fq -- "Could not identify the authenticated GitHub user" "$USER_FAILURE_LOG" \
    || fail "user API failure was not identified distinctly"
grep -Fq -- "simulated gh user lookup failure" "$USER_FAILURE_LOG" \
    || fail "user API failure suppressed gh's diagnostic"
if grep -Fq -- "repo create" "$GH_LOG"; then
    fail "user API failure reached gh repo create"
fi

: >"$GH_LOG"
MEMBERSHIP_FAILURE_LOG="$TEST_ROOT/membership-failure.log"
"${COMMON_ENV[@]}" TEST_GH_MEMBERSHIP_RC=1 PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/membership-failure-project" --no-model-probe --publish \
    >"$MEMBERSHIP_FAILURE_LOG" 2>&1
grep -Fq -- "Could not verify active membership in test-org" "$MEMBERSHIP_FAILURE_LOG" \
    || fail "membership API failure was mislabeled"
grep -Fq -- "simulated gh membership lookup failure" "$MEMBERSHIP_FAILURE_LOG" \
    || fail "membership API failure suppressed gh's diagnostic"
if grep -Fq -- "repo create" "$GH_LOG"; then
    fail "membership API failure reached gh repo create"
fi

: >"$GH_LOG"
INACTIVE_LOG="$TEST_ROOT/inactive-membership.log"
"${COMMON_ENV[@]}" TEST_GH_MEMBERSHIP_STATE=pending PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/inactive-project" --no-model-probe --publish \
    >"$INACTIVE_LOG" 2>&1
grep -Fq -- "GitHub membership in test-org is pending, not active" "$INACTIVE_LOG" \
    || fail "confirmed inactive membership was not reported distinctly"
if grep -Fq -- "repo create" "$GH_LOG"; then
    fail "inactive membership reached gh repo create"
fi

# The remaining preflight exits are non-mutating and must stop before any API
# or repo-create call.
: >"$GH_LOG"
MISSING_GH_LOG="$TEST_ROOT/missing-gh.log"
# setup deliberately scrubs BASH_ENV and exported functions, so exercise a
# genuinely gh-free PATH while retaining the other system prerequisites.
NO_GH_BIN="$TEST_ROOT/no-gh-bin"
mkdir "$NO_GH_BIN"
for system_tool in /usr/bin/*; do
    [ -x "$system_tool" ] || continue
    tool_name="${system_tool##*/}"
    case "$tool_name" in
        gh|uv|claude|bwrap) continue ;;
    esac
    ln -s "$system_tool" "$NO_GH_BIN/$tool_name"
done
ln -s "$FAKE_BIN/uv" "$NO_GH_BIN/uv"
ln -s "$FAKE_BIN/claude" "$NO_GH_BIN/claude"
ln -s "$FAKE_BIN/bwrap" "$NO_GH_BIN/bwrap"
"${COMMON_ENV[@]}" PATH="$NO_GH_BIN" PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/missing-gh-project" --no-model-probe --publish \
    >"$MISSING_GH_LOG" 2>&1
grep -Fq -- "GitHub CLI (gh) not found" "$MISSING_GH_LOG" \
    || fail "missing gh was not reported"
[ ! -s "$GH_LOG" ] || fail "missing-gh branch invoked gh"

: >"$GH_LOG"
AUTH_FAILURE_LOG="$TEST_ROOT/auth-failure.log"
"${COMMON_ENV[@]}" TEST_GH_AUTH_RC=1 PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/auth-failure-project" --no-model-probe --publish \
    >"$AUTH_FAILURE_LOG" 2>&1
grep -Fq -- "GitHub CLI is not authenticated" "$AUTH_FAILURE_LOG" \
    || fail "failed gh authentication was not reported"
if grep -Fq -- "api " "$GH_LOG" || grep -Fq -- "repo create" "$GH_LOG"; then
    fail "failed gh authentication reached an API or mutation call"
fi

: >"$GH_LOG"
EMPTY_USER_LOG="$TEST_ROOT/empty-user.log"
"${COMMON_ENV[@]}" TEST_GH_USER_VALUE= PUBLISH_ORG=test-org \
    "$SETUP" "$RUN_ROOT/empty-user-project" --no-model-probe --publish \
    >"$EMPTY_USER_LOG" 2>&1
grep -Fq -- "empty authenticated-user login" "$EMPTY_USER_LOG" \
    || fail "empty authenticated-user login was not reported"
if grep -Fq -- "memberships/" "$GH_LOG" || grep -Fq -- "repo create" "$GH_LOG"; then
    fail "empty authenticated-user login reached membership or mutation calls"
fi

echo "PASS: setup publication is local by default and explicit under --publish"
