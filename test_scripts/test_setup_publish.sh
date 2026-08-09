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
grep -Fq -- "Deployments stay local by" "$HELP_OUTPUT" || fail "help omits local default"
grep -Fq -- "--publish" "$HELP_OUTPUT" || fail "help omits --publish"
grep -Fq -- "--no-publish" "$HELP_OUTPUT" || fail "help omits --no-publish"
grep -Fq -- "PUBLISH_ORG=<org>" "$HELP_OUTPUT" || fail "help omits PUBLISH_ORG"

# Parser errors happen before any project directory is created, independent of
# flag order.
expect_failure "--publish and --no-publish are mutually exclusive" \
    "$SETUP" parser-a --publish --no-publish
expect_failure "--publish and --no-publish are mutually exclusive" \
    "$SETUP" parser-b --no-publish --publish
expect_failure "--publish cannot be used with --local" \
    "$SETUP" parser-c --publish --local
expect_failure "--publish cannot be used with --mode report" \
    "$SETUP" parser-d --mode report --publish
expect_failure "--publish requires a non-empty PUBLISH_ORG" \
    env PUBLISH_ORG= "$SETUP" parser-e --publish
expect_failure "PUBLISH_VISIBILITY must be private, public, or internal" \
    env PUBLISH_VISIBILITY=secret "$SETUP" parser-f --publish

# Build a committed local template source so production-mode setup exercises
# the real clone/assembly/commit/publish path without touching the network.
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
    "$TEMPLATE_REPO/deploy_assets/scripts/"
git -C "$TEMPLATE_REPO" add setup.sh VERSION deploy_assets/scripts/setup \
    deploy_assets/scripts/apply_extension_empirical.sh \
    deploy_assets/scripts/apply_extension_theory_llm.sh
if ! git -C "$TEMPLATE_REPO" diff --cached --quiet; then
    git -C "$TEMPLATE_REPO" \
        -c user.name='Publish Test' -c user.email='publish-test@example.invalid' \
        commit -qm 'test: stage working publication changes'
fi

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

# Bash has no PATH-level way to hide one real command while retaining the rest
# of /usr/bin. This test-only BASH_ENV shim lets one case make `command -v gh`
# fail without changing any other command lookup.
BASH_ENV_FILE="$TEST_ROOT/bash_env"
cat >"$BASH_ENV_FILE" <<'EOF'
if [ "${TEST_FORCE_GH_MISSING:-0}" = "1" ]; then
    command() {
        if [ "$#" -eq 2 ] && [ "$1" = "-v" ] && [ "$2" = "gh" ]; then
            return 1
        fi
        builtin command "$@"
    }
fi
EOF

RUN_ROOT="$TEST_ROOT/runs"
mkdir -p "$RUN_ROOT"
GH_LOG="$TEST_ROOT/gh.log"
: >"$GH_LOG"
UV_LOG="$TEST_ROOT/uv.log"
: >"$UV_LOG"

COMMON_ENV=(
    env
    PATH="$FAKE_BIN:$PATH"
    BASH_ENV="$BASH_ENV_FILE"
    TEST_GH_LOG="$GH_LOG"
    TEST_UV_LOG="$UV_LOG"
    ZEROPAPER_REPO="$TEMPLATE_REPO"
    GIT_CONFIG_GLOBAL=/dev/null
    GIT_CONFIG_NOSYSTEM=1
    GIT_CONFIG_COUNT=2
    GIT_CONFIG_KEY_0=user.name
    GIT_CONFIG_VALUE_0='Publish Test'
    GIT_CONFIG_KEY_1=user.email
    GIT_CONFIG_VALUE_1='publish-test@example.invalid'
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
grep -Fq -- "pip install --python ./.venv -r" "$UV_LOG" \
    || fail "default production setup did not provision project dependencies"
[ -f "$RUN_ROOT/default-project/.venv/lib/python3.12/site-packages/_pipeline_dotenv_guard.pth" ] \
    || fail "default production setup did not install the dotenv guard"

# Provisioning remains ordered at its historical boundaries: core first, SSJ
# with the finance skill, then extension dependencies in the user's extension
# order. This production clone path verifies the coordinator/module wiring, not
# merely the provisioning functions in isolation.
: >"$UV_LOG"
PROVISION_LOG="$TEST_ROOT/provision.log"
"${COMMON_ENV[@]}" "$SETUP" "$RUN_ROOT/provision-project" --no-model-probe \
    --ext theory_llm --ext empirical >"$PROVISION_LOG" 2>&1
python3 - "$UV_LOG" <<'PY' || fail "dependency provisioning order changed"
import sys

lines = [line.strip() for line in open(sys.argv[1]) if line.startswith("pip install ")]
needles = [
    "/templates/deps/core.txt",
    "/templates/deps/ssj.txt",
    "/extensions/theory_llm/deps.txt",
    "/extensions/empirical/deps.txt",
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
"${COMMON_ENV[@]}" TEST_FORCE_GH_MISSING=1 PUBLISH_ORG=test-org \
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
