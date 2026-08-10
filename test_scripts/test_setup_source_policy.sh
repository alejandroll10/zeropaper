#!/usr/bin/env bash
# Regression coverage for checkout-local setup source policy (#256).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/setup-source-policy.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT
source_checkout="$scratch/template"

fail() {
    echo "FAIL: $*" >&2
    exit 1
}

file_digest() {
    python3 -I -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$1"
}

file_mode() {
    python3 -I -c 'import os,stat,sys; print(format(stat.S_IMODE(os.stat(sys.argv[1]).st_mode), "o"))' "$1"
}

copy_mode() {
    python3 -I -c 'import shutil,sys; shutil.copymode(sys.argv[1], sys.argv[2])' "$1" "$2"
}

expect_failure() {
    local expected="$1"
    shift
    local log="$scratch/failure.log"
    if "$@" >"$log" 2>&1; then
        fail "command unexpectedly succeeded: $*"
    fi
    grep -Fq -- "$expected" "$log" \
        || { cat "$log" >&2; fail "missing failure text: $expected"; }
}

# Stage the working implementation in a clean temporary checkout. This keeps
# the test valid before the change itself has been committed.
git clone -q "$repo_root" "$source_checkout"
cp "$repo_root/setup.sh" "$source_checkout/setup.sh"
cp "$repo_root/update.sh" "$source_checkout/update.sh"
cp "$repo_root/scripts/update_coordinator.sh" \
    "$source_checkout/scripts/update_coordinator.sh"
cp "$repo_root/deploy_assets/scripts/setup/"*.sh \
    "$source_checkout/deploy_assets/scripts/setup/"
cp "$repo_root/deploy_assets/scripts/apply_extension_empirical.sh" \
   "$repo_root/deploy_assets/scripts/apply_extension_theory_llm.sh" \
   "$repo_root/deploy_assets/scripts/resolve_model_fallbacks.py" \
   "$source_checkout/deploy_assets/scripts/"
git -C "$source_checkout" add setup.sh update.sh scripts/update_coordinator.sh \
    deploy_assets/scripts/setup \
    deploy_assets/scripts/apply_extension_empirical.sh \
    deploy_assets/scripts/apply_extension_theory_llm.sh \
    deploy_assets/scripts/resolve_model_fallbacks.py
if ! git -C "$source_checkout" diff --cached --quiet; then
    git -C "$source_checkout" \
        -c user.name='Source Policy Test' \
        -c user.email='source-policy@example.invalid' \
        commit -qm 'test: stage source-policy implementation'
fi
git -C "$source_checkout" remote set-url origin \
    'https://user:secret@github.com/example/zeropaper.git?token=secret'

setup="$source_checkout/setup.sh"
expect_failure "update target overlaps template source checkout" \
    "$source_checkout/update.sh" "$source_checkout" --variant finance --no-model-probe
expect_failure "update target overlaps template source checkout" \
    "$source_checkout/update.sh" "$scratch" --variant finance --no-model-probe
[ ! -e "$source_checkout/process_log" ] \
    || fail "rejected checkout update created process_log in template source"
[ ! -e "$scratch/process_log" ] \
    || fail "rejected parent update created process_log above template source"

expect_failure "--assemble-only requires an explicit destination" \
    "$setup" --assemble-only --no-model-probe
expect_failure "Unknown option: --local" \
    "$setup" "$scratch/legacy" --local --no-model-probe
expect_failure "destination overlaps template build inputs" \
    "$setup" "$source_checkout/deploy_assets/nested-output" \
    --assemble-only --no-model-probe
[ ! -e "$source_checkout/deploy_assets/nested-output" ] \
    || fail "overlapping destination was created inside build inputs"

# setup-owned temporary state must never be created beneath a build-input
# directory, including through a symlink alias supplied as TMPDIR.
source_tmpdir="$source_checkout/deploy_assets/operator-tmp"
mkdir "$source_tmpdir"
tmpdir_alias="$scratch/source-tmpdir-alias"
ln -s "$source_tmpdir" "$tmpdir_alias"
expect_failure "temporary directory must be outside template build inputs" \
    env TMPDIR="$source_tmpdir" "$setup" "$scratch/tmpdir-direct-output" \
    --assemble-only --no-model-probe
expect_failure "temporary directory must be outside template build inputs" \
    env TMPDIR="$tmpdir_alias" "$setup" "$scratch/tmpdir-alias-output" \
    --assemble-only --no-model-probe
[ -z "$(find "$source_tmpdir" -mindepth 1 -print -quit)" ] \
    || fail "rejected source-overlapping TMPDIR was mutated"
rm "$tmpdir_alias"
rmdir "$source_tmpdir"

# A committed build-input symlink cannot import mutable bytes from outside the
# checkout under a digest that records only the link itself.
symlink_checkout="$scratch/symlink-template"
git clone -q "$source_checkout" "$symlink_checkout"
external_dashboard="$scratch/external-dashboard.html"
printf 'external dashboard bytes\n' > "$external_dashboard"
rm "$symlink_checkout/deploy_assets/dashboard.html"
ln -s "$external_dashboard" "$symlink_checkout/deploy_assets/dashboard.html"
git -C "$symlink_checkout" add deploy_assets/dashboard.html
git -C "$symlink_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: committed external build-input symlink'
symlink_build_output="$scratch/symlink-build-output"
expect_failure "symlink build input is not allowed" \
    "$symlink_checkout/setup.sh" "$symlink_build_output" \
    --assemble-only --no-model-probe
[ ! -e "$symlink_build_output" ] \
    || fail "external build-input symlink produced a deployment"

# The isolated launcher must reject an aliased coordinator before any external
# shell bytes run, even though the general snapshot symlink gate is later.
coordinator_symlink_checkout="$scratch/coordinator-symlink-template"
git clone -q "$source_checkout" "$coordinator_symlink_checkout"
external_coordinator="$scratch/external-coordinator.sh"
coordinator_canary="$scratch/external-coordinator-ran"
printf '%s\n' '#!/bin/bash' ": > \"$coordinator_canary\"" > "$external_coordinator"
coordinator_rel="deploy_assets/scripts/setup/coordinator.sh"
rm "$coordinator_symlink_checkout/$coordinator_rel"
ln -s "$external_coordinator" "$coordinator_symlink_checkout/$coordinator_rel"
git -C "$coordinator_symlink_checkout" add "$coordinator_rel"
git -C "$coordinator_symlink_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: committed external coordinator symlink'
expect_failure "setup coordinator must be one regular non-aliased file" \
    "$coordinator_symlink_checkout/setup.sh" \
    "$scratch/coordinator-symlink-output" --assemble-only --no-model-probe
[ ! -e "$coordinator_canary" ] \
    || fail "external coordinator bytes executed before source validation"

# Existing files are never assembly destinations, especially when they are
# source inputs. Preserve byte-for-byte sentinels around every rejection.
existing_file="$scratch/existing-file"
printf 'do-not-delete\n' > "$existing_file"
expect_failure "exists and is not a directory" \
    "$setup" "$existing_file" --assemble-only --no-model-probe
[ "$(cat "$existing_file")" = "do-not-delete" ] \
    || fail "arbitrary existing destination file was changed"

version_hash_before="$(file_digest "$source_checkout/VERSION")"
expect_failure "destination overlaps template build inputs" \
    "$setup" "$source_checkout/VERSION" --assemble-only --no-model-probe
[ "$(file_digest "$source_checkout/VERSION")" = "$version_hash_before" ] \
    || fail "VERSION was changed through destination handling"

setup_hash_before="$(file_digest "$source_checkout/setup.sh")"
expect_failure "destination overlaps template build inputs" \
    "$setup" "$source_checkout/setup.sh" --assemble-only --no-model-probe
[ "$(file_digest "$source_checkout/setup.sh")" = "$setup_hash_before" ] \
    || fail "setup.sh was changed through destination handling"

newline_destination="$scratch/newline-destination"$'\n'
expect_failure "destination cannot contain control characters" \
    "$setup" "$newline_destination" --assemble-only --no-model-probe
[ ! -e "$newline_destination" ] \
    || fail "control-character destination was created"
[ ! -e "$scratch/newline-destination" ] \
    || fail "trailing newline destination was silently retargeted"

foreign_output="$scratch/foreign/test_output/project"
mkdir -p "$foreign_output"
printf 'foreign-owner\n' > "$foreign_output/sentinel"
expect_failure "already exists and is not empty" \
    "$setup" "$foreign_output" --assemble-only --no-model-probe
[ "$(cat "$foreign_output/sentinel")" = "foreign-owner" ] \
    || fail "foreign test_output directory was overwritten"

# Directory inspection must not encode filenames into shell text: command
# substitution strips newlines and previously misclassified this as empty.
newline_output="$scratch/newline-only-directory"
mkdir "$newline_output"
newline_entry=$'\n'
printf 'newline-owner\n' > "$newline_output/$newline_entry"
expect_failure "already exists and is not empty" \
    "$setup" "$newline_output" --assemble-only --no-model-probe
[ "$(cat "$newline_output/$newline_entry")" = "newline-owner" ] \
    || fail "newline-named foreign destination entry was changed"

symlink_target="$scratch/symlink-target"
mkdir -p "$symlink_target"
ln -s "$symlink_target" "$scratch/symlink-output"
expect_failure "is a symbolic link" \
    "$setup" "$scratch/symlink-output" --assemble-only --no-model-probe
[ -L "$scratch/symlink-output" ] \
    || fail "assembly destination symlink was replaced"
expect_failure "is a symbolic link" \
    "$setup" "$scratch/symlink-output/" --assemble-only --no-model-probe
expect_failure "is a symbolic link" \
    "$setup" "$scratch/symlink-output/." --assemble-only --no-model-probe
[ -L "$scratch/symlink-output" ] \
    || fail "trailing-component destination symlink was replaced"

# An absent or empty final destination cannot be reached through a symlinked
# ancestor, including outside checkout-owned scratch.
ancestor_base="$scratch/ancestor-base"
ancestor_foreign="$scratch/ancestor-foreign"
mkdir -p "$ancestor_base" "$ancestor_foreign/empty-project"
ln -s "$ancestor_foreign" "$ancestor_base/linked-parent"
expect_failure "destination ancestor is a symbolic link" \
    "$setup" "$ancestor_base/linked-parent/absent-project" \
    --assemble-only --no-model-probe
expect_failure "destination ancestor is a symbolic link" \
    "$setup" "$ancestor_base/linked-parent/empty-project" \
    --assemble-only --no-model-probe
[ ! -e "$ancestor_foreign/absent-project" ] \
    || fail "absent destination escaped through an intermediate symlink"
[ -z "$(find "$ancestor_foreign/empty-project" -mindepth 1 -print -quit)" ] \
    || fail "empty destination escaped through an intermediate symlink"

# A checkout-level test_output symlink does not turn its foreign target into
# setup-owned disposable scratch.
foreign_scratch="$scratch/foreign-scratch"
mkdir -p "$foreign_scratch/project"
printf 'foreign-symlink-owner\n' > "$foreign_scratch/project/sentinel"
ln -s "$foreign_scratch" "$source_checkout/test_output"
expect_failure "destination ancestor is a symbolic link" \
    "$setup" "$source_checkout/test_output/project" \
    --assemble-only --no-model-probe
[ "$(cat "$foreign_scratch/project/sentinel")" = "foreign-symlink-owner" ] \
    || fail "symlinked test_output target was overwritten"
rm "$source_checkout/test_output"

mkdir -p "$source_checkout/test_output" "$scratch/nested-scratch-foreign"
ln -s "$scratch/nested-scratch-foreign" \
    "$source_checkout/test_output/linked-parent"
expect_failure "destination ancestor is a symbolic link" \
    "$setup" "$source_checkout/test_output/linked-parent/project" \
    --assemble-only --no-model-probe
[ ! -e "$scratch/nested-scratch-foreign/project" ] \
    || fail "nested test_output symlink escaped checkout-owned scratch"
rm "$source_checkout/test_output/linked-parent"

# Revalidate the exact final directory after creation. Instrument a disposable,
# committed coordinator to swap it for a foreign symlink immediately after the
# mkdir; setup must fail before any assembly write follows that link.
post_create_output="$scratch/post-create-output"
post_create_foreign="$scratch/post-create-foreign"
mkdir "$post_create_foreign"
post_create_checkout="$scratch/post-create-template"
git clone -q "$source_checkout" "$post_create_checkout"
/usr/bin/python3 -I - "$post_create_checkout/deploy_assets/scripts/setup/coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = '''    mkdir -p "$OUT_DIR"
    _setup_validate_destination_ancestors "$OUT_DIR"
'''
replacement = '''    mkdir -p "$OUT_DIR"
    if [ -n "${SOURCE_POLICY_POST_CREATE_FOREIGN:-}" ]; then
        rmdir "$OUT_DIR"
        ln -s "$SOURCE_POLICY_POST_CREATE_FOREIGN" "$OUT_DIR"
        : > "$SOURCE_POLICY_POST_CREATE_SWAPPED"
    fi
    _setup_validate_destination_ancestors "$OUT_DIR"
'''
if text.count(anchor) != 1:
    raise SystemExit("post-create validation anchor changed")
path.write_text(text.replace(anchor, replacement))
PY
git -C "$post_create_checkout" add deploy_assets/scripts/setup/coordinator.sh
git -C "$post_create_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: instrument post-create destination race'
expect_failure "destination must be a real directory" env \
    SOURCE_POLICY_POST_CREATE_FOREIGN="$post_create_foreign" \
    SOURCE_POLICY_POST_CREATE_SWAPPED="$scratch/post-create-swapped" \
    "$post_create_checkout/setup.sh" "$post_create_output" --assemble-only --no-model-probe
[ -e "$scratch/post-create-swapped" ] \
    || fail "post-create destination hook did not fire"
[ -z "$(find "$post_create_foreign" -mindepth 1 -print -quit)" ] \
    || fail "assembly wrote through a post-create destination symlink"
rm "$post_create_output"

# Standard macOS compatibility aliases are canonicalized before the strict
# ancestor walk; `/tmp` must remain a supported documented destination.
if [ -L /tmp ] && [ "$(python3 -I -c 'import os; print(os.path.realpath("/tmp"))')" = "/private/tmp" ]; then
    darwin_tmp_output="/tmp/zeropaper-source-policy-$$"
    "$setup" "$darwin_tmp_output" --assemble-only --no-model-probe \
        >"$scratch/darwin-tmp.log" 2>&1
    [ -f "/private/tmp/zeropaper-source-policy-$$/.deploy_manifest.json" ] \
        || fail "macOS /tmp alias was not canonicalized to /private/tmp"
    rm -rf "/private/tmp/zeropaper-source-policy-$$"
fi

# Default macOS filesystems resolve path components case-insensitively while
# preserving caller spelling. Inode identity, not string casing, must enforce
# both temporary-state and destination containment.
if [ -d "$source_checkout/DEPLOY_ASSETS" ] \
   && python3 -I -c 'import os,sys; raise SystemExit(0 if os.path.samefile(*sys.argv[1:]) else 1)' \
        "$source_checkout/deploy_assets" "$source_checkout/DEPLOY_ASSETS"; then
    mkdir -p "$source_checkout/deploy_assets/venv/case-tmp"
    expect_failure "temporary directory must be outside template build inputs" \
        env TMPDIR="$source_checkout/DEPLOY_ASSETS/VENV/case-tmp" \
        "$setup" "$scratch/case-tmp-output" --assemble-only --no-model-probe
    expect_failure "destination overlaps template build inputs" \
        "$setup" "$source_checkout/DEPLOY_ASSETS/VENV/case-output" \
        --assemble-only --no-model-probe
    [ ! -e "$source_checkout/deploy_assets/venv/case-output" ] \
        || fail "case-insensitive destination alias wrote inside build inputs"
    rm -rf "$source_checkout/deploy_assets/venv"
fi

# Relative assembly destinations remain anchored to the invoking checkout, not
# the private source snapshot that the wrapper deletes after setup exits.
relative_output="$source_checkout/test_output/relative-assembly"
mkdir -p "$relative_output"
printf 'stale relative scratch\n' > "$relative_output/stale-sentinel"
(cd "$scratch" && "$setup" "test_output/relative-assembly" \
    --assemble-only --no-model-probe) >"$scratch/relative-output.log" 2>&1
[ -f "$relative_output/.deploy_manifest.json" ] \
    || fail "relative assembly output did not persist under the live checkout"
[ ! -e "$relative_output/stale-sentinel" ] \
    || fail "relative checkout-owned scratch was not refreshed"

# A failed status inspection is not equivalent to a clean checkout.
mv "$source_checkout/.git/index" "$source_checkout/.git/index.saved"
mkdir "$source_checkout/.git/index"
unreadable_index_project="$scratch/unreadable-index-project"
expect_failure "could not verify template source cleanliness" \
    "$setup" "$unreadable_index_project" --no-model-probe
[ ! -e "$unreadable_index_project" ] \
    || fail "failed clean-status check created a full-setup destination"
rmdir "$source_checkout/.git/index"
mv "$source_checkout/.git/index.saved" "$source_checkout/.git/index"

mv "$source_checkout/.git/index" "$source_checkout/.git/index.saved"
expect_failure "could not verify template source cleanliness" \
    "$setup" "$scratch/missing-index-project" --no-model-probe
[ ! -e "$scratch/missing-index-project" ] \
    || fail "missing index was accepted as a healthy clean checkout"
mv "$source_checkout/.git/index.saved" "$source_checkout/.git/index"

# Source inspection must not execute ambient global/system Git helpers. In
# particular, core.fsmonitor is executable code that `git status` would run
# before setup established provenance.
hostile_git_home="$scratch/hostile-git-home"
hostile_fsmonitor="$scratch/hostile-fsmonitor"
hostile_fsmonitor_marker="$scratch/hostile-fsmonitor-ran"
mkdir "$hostile_git_home"
printf '%s\n' '#!/bin/bash' ': > "${SOURCE_POLICY_FSMONITOR_MARKER:?}"' 'exit 0' \
    > "$hostile_fsmonitor"
chmod +x "$hostile_fsmonitor"
git config --file "$hostile_git_home/.gitconfig" core.fsmonitor "$hostile_fsmonitor"
HOME="$hostile_git_home" SOURCE_POLICY_FSMONITOR_MARKER="$hostile_fsmonitor_marker" \
    "$setup" "$scratch/hostile-git-config-assembly" \
    --assemble-only --no-model-probe >"$scratch/hostile-git-config.log" 2>&1
[ ! -e "$hostile_fsmonitor_marker" ] \
    || fail "source inspection executed ambient core.fsmonitor code"

# Only this checkout's own test_output descendants are recognized as
# disposable scratch space.
clean_output="$source_checkout/test_output/clean-quote\"assembly"
mkdir -p "$clean_output"
printf 'owned-scratch\n' > "$clean_output/stale-sentinel"
ZEROPAPER_REPO="$scratch/does-not-exist" \
    "$setup" "$clean_output" --assemble-only --no-model-probe \
    >"$scratch/clean.log" 2>&1
[ ! -e "$clean_output/stale-sentinel" ] \
    || fail "checkout-owned test_output directory was not refreshed"
[ ! -e "$scratch/does-not-exist" ] \
    || fail "setup unexpectedly used ZEROPAPER_REPO"
if grep -Fq -- "Fetching template" "$scratch/clean.log"; then
    fail "assembly-only setup attempted to fetch template source"
fi

expected_commit="$(git -C "$source_checkout" rev-parse HEAD)"
clean_digest="$(jq -r '.source.content_digest' "$clean_output/.deploy_manifest.json")"
jq -e --arg commit "$expected_commit" '
    .source.kind == "checkout"
    and .source.commit == $commit
    and .source.repository == "https://github.com/example/zeropaper.git"
    and .source.dirty == false
    and (.source.content_digest | test("^sha256:[0-9a-f]{64}$"))
    and .source.update_channel == "checkout"
' "$clean_output/.deploy_manifest.json" >/dev/null \
    || fail "clean assembly manifest has incorrect source provenance"

# Ambient Git repository/path configuration cannot redirect shell-level source
# identity or cleanliness checks away from the checkout containing setup.sh.
alternate_repo="$scratch/alternate-git-repository"
git clone -q "$source_checkout" "$alternate_repo"
git -C "$alternate_repo" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit --allow-empty -qm 'test: alternate repository identity'
alternate_output="$scratch/alternate-git-env-assembly"
GIT_DIR="$alternate_repo/.git" \
GIT_WORK_TREE="$source_checkout" \
GIT_CONFIG_COUNT=1 \
GIT_CONFIG_KEY_0=core.worktree \
GIT_CONFIG_VALUE_0="$alternate_repo" \
    "$setup" "$alternate_output" --assemble-only --no-model-probe \
    >"$scratch/alternate-git-env.log" 2>&1
jq -e --arg commit "$expected_commit" '
    .source.commit == $commit
    and .source.repository == "https://github.com/example/zeropaper.git"
    and .source.dirty == false
' "$alternate_output/.deploy_manifest.json" >/dev/null \
    || fail "ambient Git path environment redirected source provenance"

# Cleanliness must bind to the commit recorded before status inspection. A ref
# flip cannot make commit A provenance describe commit B worktree bytes.
ref_race_checkout="$scratch/ref-race-template"
git clone -q "$source_checkout" "$ref_race_checkout"
ref_commit_a="$(git -C "$ref_race_checkout" rev-parse HEAD)"
printf '\nROUND9_COMMIT_B\n' >> "$ref_race_checkout/deploy_assets/dashboard.html"
git -C "$ref_race_checkout" add deploy_assets/dashboard.html
git -C "$ref_race_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: alternate build-input commit'
ref_commit_b="$(git -C "$ref_race_checkout" rev-parse HEAD)"
git -C "$ref_race_checkout" update-ref HEAD "$ref_commit_a"
# Instrument only commit B in this disposable checkout at the exact
# source-commit boundary. The marker proves the A→B→A synchronization ran,
# so the expected dirty-source failure cannot pass from the starting mismatch
# alone and does not depend on a PATH-interposed Git executable.
/usr/bin/python3 -I - "$ref_race_checkout/deploy_assets/scripts/setup/coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = '    SOURCE_COMMIT="$(_setup_source_git -C "$SOURCE_CHECKOUT_ROOT" rev-parse HEAD)"\n'
injected = anchor + '''    if [ -n "${SOURCE_POLICY_REF_COMMIT_B:-}" ]; then
        git -C "$SOURCE_CHECKOUT_ROOT" update-ref HEAD "$SOURCE_POLICY_REF_COMMIT_B"
        : > "$SOURCE_POLICY_REF_RACE_FIRED"
    fi
'''
if text.count(anchor) != 1:
    raise SystemExit("source-commit race anchor changed")
text = text.replace(anchor, injected)
restore_anchor = '''fi

_setup_reject_build_input_destination() {
'''
restore = '''fi
if [ -n "${SOURCE_POLICY_REF_COMMIT_A:-}" ]; then
    git -C "$SOURCE_CHECKOUT_ROOT" update-ref HEAD "$SOURCE_POLICY_REF_COMMIT_A"
fi

_setup_reject_build_input_destination() {
'''
if text.count(restore_anchor) != 1:
    raise SystemExit("source-commit restore anchor changed")
path.write_text(text.replace(restore_anchor, restore))
PY
git -C "$ref_race_checkout" add deploy_assets/scripts/setup/coordinator.sh
git -C "$ref_race_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit --amend --no-edit -q
ref_commit_b="$(git -C "$ref_race_checkout" rev-parse HEAD)"
git -C "$ref_race_checkout" update-ref HEAD "$ref_commit_a"
ref_race_fired="$scratch/ref-race-fired"
expect_failure "template build inputs are dirty" env \
    SOURCE_POLICY_REF_COMMIT_A="$ref_commit_a" \
    SOURCE_POLICY_REF_COMMIT_B="$ref_commit_b" \
    SOURCE_POLICY_REF_RACE_FIRED="$ref_race_fired" \
    "$ref_race_checkout/setup.sh" "$scratch/ref-race-project" --no-model-probe
[ -e "$ref_race_fired" ] || fail "commit-ref race synchronization did not run"
[ ! -e "$scratch/ref-race-project" ] \
    || fail "commit-ref race passed the full-setup clean gate"

# Caller shell hooks and PATH-selected interpreters are never part of the
# effective source. The absolute isolated launcher runs before Bash startup.
bash_env_hook="$scratch/hostile-bash-env.sh"
printf '%s\n' \
    'export ZEROPAPER_SETUP_CLEAN_SHELL=1' \
    'cp() {' \
    '  command cp "$@"' \
    '  case "${!#}" in */.gitignore) printf "\nBASH_ENV_LEAK\n" >> "${!#}" ;; esac' \
    '}' \
    'export -f cp' \
    'trap '\''if [ -f "$SOURCE_POLICY_BASH_ENV_OUTPUT/.gitignore" ]; then printf "\nBASH_ENV_LEAK\n" >> "$SOURCE_POLICY_BASH_ENV_OUTPUT/.gitignore"; fi'\'' EXIT' \
    > "$bash_env_hook"
hostile_setup_bin="$scratch/hostile-setup-bin"
hostile_setup_python_marker="$scratch/hostile-setup-python-ran"
mkdir "$hostile_setup_bin"
cat > "$hostile_setup_bin/python3" <<'SH'
#!/bin/bash
: > "${SOURCE_POLICY_SETUP_PYTHON_MARKER:?}"
exec /usr/bin/python3 "$@"
SH
chmod +x "$hostile_setup_bin/python3"
bash_env_output="$scratch/bash-env-assembly"
BASH_ENV="$bash_env_hook" \
SOURCE_POLICY_BASH_ENV_OUTPUT="$bash_env_output" \
SOURCE_POLICY_SETUP_PYTHON_MARKER="$hostile_setup_python_marker" \
PATH="$hostile_setup_bin:$PATH" \
    "$setup" "$bash_env_output" --assemble-only --no-model-probe \
    >"$scratch/bash-env.log" 2>&1
if grep -Fq 'BASH_ENV_LEAK' "$bash_env_output/.gitignore"; then
    fail "caller BASH_ENV altered assembled output"
fi
[ ! -e "$hostile_setup_python_marker" ] \
    || fail "setup control flow selected python3 from caller PATH"
[ "$(jq -r '.source.content_digest' "$bash_env_output/.deploy_manifest.json")" = "$clean_digest" ] \
    || fail "scrubbed BASH_ENV changed source provenance"

# Empty/forged internal handoff variables cannot preserve attacker-supplied
# provider pins. Activated virtualenv paths and lexical symlinks out of them are
# skipped in favor of the next safe provider, and the provider's neighboring
# python3 never becomes setup's control interpreter.
active_env="$scratch/active-provider-env"
provider_targets="$scratch/provider-targets"
safe_provider_bin="$scratch/safe-provider-bin"
mkdir -p "$active_env/bin" "$provider_targets" "$safe_provider_bin"
malicious_provider_marker="$scratch/malicious-provider-ran"
provider_python_marker="$scratch/provider-python-ran"
safe_provider_marker="$scratch/safe-provider-ran"
printf '%s\n' \
    '#!/bin/bash' \
    ': > "${SOURCE_POLICY_MALICIOUS_PROVIDER_MARKER:?}"' \
    'printf "model not found\n"' \
    > "$provider_targets/claude"
chmod +x "$provider_targets/claude"
ln -s "$provider_targets/claude" "$active_env/bin/claude"
printf '%s\n' \
    '#!/bin/bash' \
    ': > "${SOURCE_POLICY_SAFE_PROVIDER_MARKER:?}"' \
    'printf "model not found\n"' \
    > "$safe_provider_bin/claude"
printf '%s\n' \
    '#!/bin/bash' \
    ': > "${SOURCE_POLICY_PROVIDER_PYTHON_MARKER:?}"' \
    'exec /usr/bin/python3 "$@"' \
    > "$safe_provider_bin/python3"
chmod +x "$safe_provider_bin/claude" "$safe_provider_bin/python3"
provider_output="$scratch/provider-assembly"
ZEROPAPER_SETUP_HANDOFF= \
ZEROPAPER_SETUP_TOOL_CLAUDE="$provider_targets/claude" \
VIRTUAL_ENV="$active_env" \
PATH="$active_env/bin:$safe_provider_bin:/usr/bin:/bin" \
SOURCE_POLICY_MALICIOUS_PROVIDER_MARKER="$malicious_provider_marker" \
SOURCE_POLICY_SAFE_PROVIDER_MARKER="$safe_provider_marker" \
SOURCE_POLICY_PROVIDER_PYTHON_MARKER="$provider_python_marker" \
    "$setup" "$provider_output" --assemble-only \
    >"$scratch/provider.log" 2>&1
[ -e "$safe_provider_marker" ] || fail "safe provider executable was not selected"
[ ! -e "$malicious_provider_marker" ] \
    || fail "forged or activated-environment provider executable ran"
[ ! -e "$provider_python_marker" ] \
    || fail "provider directory supplied setup's Python interpreter"
if [ -d "$active_env/BIN" ] \
   && python3 -I -c 'import os,sys; raise SystemExit(0 if os.path.samefile(*sys.argv[1:]) else 1)' \
        "$active_env/bin" "$active_env/BIN"; then
    rm -f "$malicious_provider_marker" "$provider_python_marker"
    case_provider_output="$scratch/case-provider-assembly"
    VIRTUAL_ENV="$active_env" \
    PATH="$active_env/BIN:$safe_provider_bin:/usr/bin:/bin" \
    SOURCE_POLICY_MALICIOUS_PROVIDER_MARKER="$malicious_provider_marker" \
    SOURCE_POLICY_SAFE_PROVIDER_MARKER="$safe_provider_marker" \
    SOURCE_POLICY_PROVIDER_PYTHON_MARKER="$provider_python_marker" \
        "$setup" "$case_provider_output" --assemble-only \
        >"$scratch/case-provider.log" 2>&1
    [ ! -e "$malicious_provider_marker" ] \
        || fail "case-insensitive activated provider alias ran"
    [ ! -e "$provider_python_marker" ] \
        || fail "case-insensitive provider alias supplied setup's Python interpreter"
fi

# Cleanliness is an effective-tree comparison against HEAD, not an index/status
# hint. assume-unchanged and ignore rules cannot hide consumed bytes.
git -C "$source_checkout" update-index --assume-unchanged VERSION
printf '9.24.0\n' > "$source_checkout/VERSION"
expect_failure "template build inputs are dirty" \
    "$setup" "$scratch/assume-unchanged-project" --no-model-probe
assume_output="$scratch/assume-unchanged-assembly"
"$setup" "$assume_output" --assemble-only --no-model-probe \
    >"$scratch/assume-unchanged.log" 2>&1
jq -e '.source.dirty == true' "$assume_output/.deploy_manifest.json" >/dev/null \
    || fail "assume-unchanged modification was recorded clean"
git -C "$source_checkout" update-index --no-assume-unchanged VERSION
git -C "$source_checkout" restore VERSION

exclude_file="$source_checkout/.git/info/exclude"
exclude_backup="$scratch/git-info-exclude.backup"
cp "$exclude_file" "$exclude_backup"
ignored_rel="deploy_assets/templates/shared/docs/source_policy_ignored.md"
printf '%s\n' "$ignored_rel" >> "$exclude_file"
printf 'ignored effective input\n' > "$source_checkout/$ignored_rel"
expect_failure "template build inputs are dirty" \
    "$setup" "$scratch/ignored-effective-project" --no-model-probe
ignored_output="$scratch/ignored-effective-assembly"
"$setup" "$ignored_output" --assemble-only --no-model-probe \
    >"$scratch/ignored-effective.log" 2>&1
jq -e '.source.dirty == true' "$ignored_output/.deploy_manifest.json" >/dev/null \
    || fail "Git-excluded effective input was recorded clean"
grep -Fq 'ignored effective input' "$ignored_output/docs/source_policy_ignored.md" \
    || fail "ignored effective-input regression did not affect assembly"
rm "$source_checkout/$ignored_rel"
cp "$exclude_backup" "$exclude_file"

# Atomically replace the coordinator after the isolated launcher starts but
# before snapshot capture; only the replacement bytes may enter provenance.
coordinator="$source_checkout/deploy_assets/scripts/setup/coordinator.sh"
coordinator_replacement="$scratch/setup-coordinator-replacement.sh"
sed '/infrastructure_copy_file 130 .*"launch.sh"/a\
infrastructure_copy_file 131 "$TEMPLATE_ROOT/launch.sh" "coordinator-race-marker.sh"' \
    "$coordinator" > "$coordinator_replacement"
copy_mode "$coordinator" "$coordinator_replacement"
setup_original="$scratch/setup-original.py"
cp "$setup" "$setup_original"
python3 -I - "$setup" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
needle = 'os.execve("/bin/bash", ["bash", coordinator, *sys.argv[1:]], clean)\n'
pause = '''with open(os.environ["SOURCE_POLICY_COORDINATOR_READY"], "w"):
    pass
while not os.path.exists(os.environ["SOURCE_POLICY_COORDINATOR_CONTINUE"]):
    __import__("time").sleep(0.01)
'''
if text.count(needle) != 1:
    raise SystemExit("setup coordinator handoff point changed")
path.write_text(text.replace(needle, pause + needle))
PY
coordinator_output="$scratch/coordinator-atomic-assembly"
coordinator_ready="$scratch/coordinator-ready"
coordinator_continue="$scratch/coordinator-continue"
SOURCE_POLICY_COORDINATOR_READY="$coordinator_ready" \
SOURCE_POLICY_COORDINATOR_CONTINUE="$coordinator_continue" \
    "$setup" "$coordinator_output" --assemble-only --no-model-probe \
    >"$scratch/coordinator-atomic.log" 2>&1 &
coordinator_pid=$!
for _attempt in $(seq 1 1000); do
    [ ! -e "$coordinator_ready" ] || break
    kill -0 "$coordinator_pid" 2>/dev/null \
        || { wait "$coordinator_pid" || true; cat "$scratch/coordinator-atomic.log" >&2; fail "coordinator setup exited before snapshot pause"; }
    sleep 0.01
done
[ -e "$coordinator_ready" ] || fail "coordinator snapshot pause did not fire"
cp "$coordinator_replacement" "$coordinator.next"
mv "$coordinator.next" "$coordinator"
cp "$setup_original" "$setup"
: > "$coordinator_continue"
wait "$coordinator_pid" \
    || { cat "$scratch/coordinator-atomic.log" >&2; fail "coordinator replacement assembly failed"; }
[ -f "$coordinator_output/coordinator-race-marker.sh" ] \
    || fail "assembly continued on the pre-snapshot live coordinator inode"
jq -e '.source.dirty == true' "$coordinator_output/.deploy_manifest.json" >/dev/null \
    || fail "atomic coordinator replacement was not represented in provenance"
git -C "$source_checkout" restore deploy_assets/scripts/setup/coordinator.sh

# update.sh must consume only the completed fresh assembly after setup's source
# stability check. Mutating the live checkout immediately after that assembly
# must not change the applied version, venv guard, or dependency specifications.
expected_update_version="$(jq -r '.template_version' "$clean_output/.deploy_manifest.json")"
expected_guard="$scratch/expected-pipeline-dotenv-guard.py"
expected_core_deps="$scratch/expected-core-deps.txt"
cp "$clean_output/.arpipeline/update_inputs/pipeline_dotenv_guard.py" "$expected_guard"
cp "$clean_output/.arpipeline/update_inputs/deps/core.txt" "$expected_core_deps"
fake_site_packages="$clean_output/.venv/lib/python3.12/site-packages"
mkdir -p "$fake_site_packages"
printf 'stale guard\n' > "$fake_site_packages/_pipeline_dotenv_guard.py"
update_coordinator="$source_checkout/scripts/update_coordinator.sh"
python3 -I - "$update_coordinator" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
needle = 'echo "  ✓ fresh deploy ok ($(wc -l < "$TMP/deploy.log") log lines)"\n'
inject = r'''if [ -n "${SOURCE_POLICY_UPDATE_MUTATED:-}" ]; then
    printf '99.99.99\n' > "$SOURCE_POLICY_UPDATE_ROOT/VERSION"
    printf 'raise RuntimeError("live guard leaked")\n' \
        > "$SOURCE_POLICY_UPDATE_ROOT/deploy_assets/templates/utils/pipeline_dotenv_guard.py"
    printf 'live-dependency-leak\n' \
        > "$SOURCE_POLICY_UPDATE_ROOT/deploy_assets/templates/deps/core.txt"
    : > "$SOURCE_POLICY_UPDATE_MUTATED"
fi
'''
if text.count(needle) != 1:
    raise SystemExit("update post-assembly injection point changed")
path.write_text(text.replace(needle, needle + inject))
PY
post_assembly_hook="$scratch/post-assembly-update-hook.sh"
cat > "$post_assembly_hook" <<'SH'
cp() {
    command cp "$@"
    case "${!#}" in */CLAUDE.md) printf '\nUPDATE_BASH_ENV_LEAK\n' >> "${!#}" ;; esac
}
export -f cp
trap 'if [ -f "$SOURCE_POLICY_UPDATE_OUTPUT/CLAUDE.md" ]; then printf "\nUPDATE_BASH_ENV_LEAK\n" >> "$SOURCE_POLICY_UPDATE_OUTPUT/CLAUDE.md"; fi' EXIT
SH
hostile_update_bin="$clean_output/.venv/bin"
hostile_update_python_marker="$scratch/hostile-update-python-ran"
mkdir -p "$hostile_update_bin"
cat > "$hostile_update_bin/python3" <<'SH'
#!/bin/bash
if [ "${2:-}" = "${SOURCE_POLICY_UPDATE_LAUNCHER:-}" ]; then
    : > "${SOURCE_POLICY_UPDATE_PYTHON_MARKER:?}"
fi
exec /usr/bin/python3 "$@"
SH
chmod +x "$hostile_update_bin/python3"
SOURCE_POLICY_UPDATE_ROOT="$source_checkout" \
SOURCE_POLICY_UPDATE_MUTATED="$scratch/update-source-mutated" \
SOURCE_POLICY_UPDATE_OUTPUT="$clean_output" \
SOURCE_POLICY_UPDATE_LAUNCHER="$source_checkout/update.sh" \
SOURCE_POLICY_UPDATE_PYTHON_MARKER="$hostile_update_python_marker" \
BASH_ENV="$post_assembly_hook" \
PATH="$hostile_update_bin:$PATH" \
    "$source_checkout/update.sh" "$clean_output" --no-model-probe \
    >"$scratch/update-source-consistency.log" 2>&1
[ -e "$scratch/update-source-mutated" ] \
    || fail "post-assembly update source hook did not fire"
if grep -Fq 'UPDATE_BASH_ENV_LEAK' "$clean_output/CLAUDE.md"; then
    fail "caller BASH_ENV altered refreshed update output"
fi
[ ! -e "$hostile_update_python_marker" ] \
    || fail "update launcher selected python3 from activated target venv"
[ "$(jq -r '.template_version' "$clean_output/.deploy_manifest.json")" = \
  "$expected_update_version" ] \
    || fail "update version was reread from live source after fresh assembly"
cmp -s "$fake_site_packages/_pipeline_dotenv_guard.py" "$expected_guard" \
    || fail "update installed a live post-assembly guard instead of the verified copy"
cmp -s "$clean_output/.arpipeline/update_inputs/deps/core.txt" "$expected_core_deps" \
    || fail "update applied live post-assembly dependency bytes"
git -C "$source_checkout" restore VERSION \
    scripts/update_coordinator.sh \
    deploy_assets/templates/utils/pipeline_dotenv_guard.py \
    deploy_assets/templates/deps/core.txt
rm -rf "$clean_output/.venv"

# Ignored checkout bytecode is excluded from provenance only because setup
# routes imports to a private cache. Install timestamp-valid poisoned bytecode
# for a module every assembler imports; it must neither execute nor alter the
# effective-source digest.
pyc_marker="$scratch/poisoned-pyc-executed"
python3 -I - "$source_checkout/deploy_assets/scripts/agent_body_loader.py" <<'PY'
import importlib.util
import marshal
import os
import struct
import sys

source = sys.argv[1]
info = os.stat(source)
payload = compile(
    'import os\n'
    'open(os.environ["SOURCE_POLICY_PYC_MARKER"], "w").write("executed")\n'
    'raise RuntimeError("poisoned checkout bytecode executed")\n',
    source,
    "exec",
)
cache = importlib.util.cache_from_source(source)
os.makedirs(os.path.dirname(cache), exist_ok=True)
header = importlib.util.MAGIC_NUMBER + struct.pack(
    "<III", 0, int(info.st_mtime) & 0xFFFFFFFF, info.st_size & 0xFFFFFFFF
)
with open(cache, "wb") as handle:
    handle.write(header)
    marshal.dump(payload, handle)
PY
pyc_output="$scratch/pyc-assembly"
SOURCE_POLICY_PYC_MARKER="$pyc_marker" \
    "$setup" "$pyc_output" --assemble-only --no-model-probe \
    >"$scratch/pyc.log" 2>&1
[ ! -e "$pyc_marker" ] || fail "ignored checkout bytecode executed"
[ "$(jq -r '.source.content_digest' "$pyc_output/.deploy_manifest.json")" = "$clean_digest" ] \
    || fail "non-input checkout cache changed the source digest"
jq -e '.source.dirty == false' "$pyc_output/.deploy_manifest.json" >/dev/null \
    || fail "ignored private-cache bytecode changed Git cleanliness"
rm -rf "$source_checkout/deploy_assets/scripts/__pycache__"

# Every artifact class omitted by the digest is also omitted from the private
# snapshot. Otherwise a semantic glob could consume ignored bytes (for example
# extensions/*/agent_metadata/*.json under a globally ignored venv/ directory).
poison_metadata_dir="$source_checkout/deploy_assets/extensions/venv/agent_metadata"
mkdir -p "$poison_metadata_dir"
printf 'this is deliberately invalid metadata json\n' \
    > "$poison_metadata_dir/poison.json"
ignored_glob_output="$scratch/ignored-glob-assembly"
"$setup" "$ignored_glob_output" --assemble-only --no-model-probe \
    >"$scratch/ignored-glob.log" 2>&1
[ "$(jq -r '.source.content_digest' "$ignored_glob_output/.deploy_manifest.json")" = "$clean_digest" ] \
    || fail "excluded artifact directory changed the source digest"
jq -e '.source.dirty == false' "$ignored_glob_output/.deploy_manifest.json" >/dev/null \
    || fail "excluded artifact directory changed Git cleanliness"
rm -rf "$source_checkout/deploy_assets/extensions/venv"

# Embedded stdlib snippets run isolated from both the checkout root and caller
# cwd. An untracked root hashlib.py is outside SOURCE_INPUT_PATHS and must never
# become an implicit executable input.
hostile_marker="$scratch/hostile-hashlib-executed"
printf '%s\n' \
    'import os' \
    'open(os.environ["SOURCE_POLICY_HOSTILE_MARKER"], "w").write("executed")' \
    'raise RuntimeError("hostile cwd hashlib executed")' \
    > "$source_checkout/hashlib.py"
hostile_output="$scratch/hostile-cwd-assembly"
(cd "$source_checkout" && \
    SOURCE_POLICY_HOSTILE_MARKER="$hostile_marker" \
    ./setup.sh "$hostile_output" --assemble-only --no-model-probe) \
    >"$scratch/hostile-cwd.log" 2>&1
[ ! -e "$hostile_marker" ] || fail "caller-CWD hashlib.py executed"
[ "$(jq -r '.source.content_digest' "$hostile_output/.deploy_manifest.json")" = "$clean_digest" ] \
    || fail "non-input caller-CWD module changed the source digest"
jq -e '.source.dirty == false' "$hostile_output/.deploy_manifest.json" >/dev/null \
    || fail "non-build caller-CWD module changed Git cleanliness"
rm "$source_checkout/hashlib.py"

# Assembly reads only the verified private snapshot. Instrument a disposable,
# committed coordinator to mutate the live dashboard throughout assembly and
# restore it immediately before final verification. The transient live bytes
# must not leak into output under unchanged provenance.
transient_checkout="$scratch/transient-template"
git clone -q "$source_checkout" "$transient_checkout"
/usr/bin/python3 -I - "$transient_checkout/deploy_assets/scripts/setup/coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
start_anchor = '''SETUP_TOOL_UV="${ZEROPAPER_SETUP_TOOL_UV:-}"
'''
start = '''if [ -n "${SOURCE_POLICY_LIVE_DASHBOARD:-}" ]; then
    cp -p "$SOURCE_POLICY_LIVE_DASHBOARD" "$SOURCE_POLICY_DASHBOARD_BACKUP"
    printf '\\ntransient-live-canary\\n' >> "$SOURCE_POLICY_LIVE_DASHBOARD"
    : > "$SOURCE_POLICY_TRANSIENT_FIRED"
fi

SETUP_TOOL_UV="${ZEROPAPER_SETUP_TOOL_UV:-}"
'''
finish_anchor = '''_setup_verify_source_stable() {
    local final_digest snapshot_digest final_commit final_status
'''
finish = '''_setup_verify_source_stable() {
    local final_digest snapshot_digest final_commit final_status
    if [ -n "${SOURCE_POLICY_LIVE_DASHBOARD:-}" ]; then
        cp -p "$SOURCE_POLICY_DASHBOARD_BACKUP" "$SOURCE_POLICY_LIVE_DASHBOARD"
    fi
'''
if text.count(start_anchor) != 1 or text.count(finish_anchor) != 1:
    raise SystemExit("transient-source instrumentation anchor changed")
path.write_text(text.replace(start_anchor, start).replace(finish_anchor, finish))
PY
git -C "$transient_checkout" add deploy_assets/scripts/setup/coordinator.sh
git -C "$transient_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: instrument transient live-source mutation'
transient_dashboard="$transient_checkout/deploy_assets/dashboard.html"
transient_backup="$scratch/dashboard.backup"
transient_fired="$scratch/transient-fired"
transient_hash_before="$(file_digest "$transient_dashboard")"
transient_clean_output="$scratch/transient-clean-assembly"
"$transient_checkout/setup.sh" "$transient_clean_output" --assemble-only --no-model-probe \
    >"$scratch/transient-clean.log" 2>&1
transient_clean_digest="$(jq -r '.source.content_digest' "$transient_clean_output/.deploy_manifest.json")"
transient_output="$scratch/transient-assembly"
SOURCE_POLICY_LIVE_DASHBOARD="$transient_dashboard" \
SOURCE_POLICY_DASHBOARD_BACKUP="$transient_backup" \
SOURCE_POLICY_TRANSIENT_FIRED="$transient_fired" \
    "$transient_checkout/setup.sh" "$transient_output" --assemble-only --no-model-probe \
    >"$scratch/transient.log" 2>&1
[ -e "$transient_fired" ] || fail "transient source hook did not fire"
[ "$(file_digest "$transient_dashboard")" = "$transient_hash_before" ] \
    || fail "transient test did not restore the live source"
cmp -s "$transient_output/dashboard.html" "$transient_clean_output/dashboard.html" \
    || fail "transient live source bytes leaked into snapshot assembly"
[ "$(jq -r '.source.content_digest' "$transient_output/.deploy_manifest.json")" = "$transient_clean_digest" ] \
    || fail "transient restored source changed recorded provenance"

# Local remotes expose only a basename, including file:// URLs.
git -C "$source_checkout" remote set-url origin \
    'file:///private/operator/checkouts/secret-template.git'
file_url_output="$scratch/file-url-assembly"
"$setup" "$file_url_output" --assemble-only --no-model-probe \
    >"$scratch/file-url.log" 2>&1
jq -e '.source.repository == "local:secret-template.git"' \
    "$file_url_output/.deploy_manifest.json" >/dev/null \
    || fail "file URL leaked its absolute checkout path"
git -C "$source_checkout" remote set-url origin \
    'private/operator/checkouts/relative-template.git'
relative_url_output="$scratch/relative-url-assembly"
"$setup" "$relative_url_output" --assemble-only --no-model-probe \
    >"$scratch/relative-url.log" 2>&1
jq -e '.source.repository == "local:relative-template.git"' \
    "$relative_url_output/.deploy_manifest.json" >/dev/null \
    || fail "relative local remote leaked its checkout path"
git -C "$source_checkout" remote set-url origin \
    'https://user:secret@github.com/example/zeropaper.git?token=secret'

# Permission bits that cp can propagate are part of effective provenance, not
# just the executable bits Git tracks.
launch_mode_before="$(file_mode "$source_checkout/deploy_assets/launch.sh")"
chmod a-w "$source_checkout/deploy_assets/launch.sh"
mode_output="$scratch/mode-assembly"
"$setup" "$mode_output" --assemble-only --no-model-probe \
    >"$scratch/mode.log" 2>&1
mode_digest="$(jq -r '.source.content_digest' "$mode_output/.deploy_manifest.json")"
[ "$mode_digest" != "$clean_digest" ] \
    || fail "source digest ignored effective permission changes"
[ "$(file_mode "$mode_output/launch.sh")" != \
  "$(file_mode "$clean_output/launch.sh")" ] \
    || fail "permission regression did not exercise changed deployment output"
chmod "$launch_mode_before" "$source_checkout/deploy_assets/launch.sh"

# Linked and detached worktrees are still first-class checkouts; their Git
# top-level is the worktree root even though the common Git directory lives in
# the original checkout.
linked_worktree="$scratch/linked-worktree"
git -C "$source_checkout" worktree add -q --detach "$linked_worktree" HEAD
linked_output="$scratch/linked-assembly"
"$linked_worktree/setup.sh" "$linked_output" --assemble-only --no-model-probe \
    >"$scratch/linked.log" 2>&1
jq -e --arg commit "$expected_commit" '
    .source.kind == "checkout"
    and .source.commit == $commit
    and .source.dirty == false
' "$linked_output/.deploy_manifest.json" >/dev/null \
    || fail "detached linked-worktree provenance is incorrect"

# Full setup must reject dirty build inputs before creating the destination,
# while assembly-only deliberately permits and records them.
printf '\nsource-policy-dirty-canary\n' >> "$source_checkout/deploy_assets/dashboard.html"
dirty_project="$scratch/dirty-project"
expect_failure "template build inputs are dirty" \
    "$setup" "$dirty_project" --no-model-probe
[ ! -e "$dirty_project" ] \
    || fail "dirty full setup created its destination before rejection"

dirty_output="$scratch/dirty-assembly"
"$setup" "$dirty_output" --assemble-only --no-model-probe \
    >"$scratch/dirty.log" 2>&1
dirty_digest="$(jq -r '.source.content_digest' "$dirty_output/.deploy_manifest.json")"
jq -e '.source.dirty == true' "$dirty_output/.deploy_manifest.json" >/dev/null \
    || fail "dirty assembly did not record source.dirty=true"
[ "$dirty_digest" != "$clean_digest" ] \
    || fail "source digest did not change with build-input content"

# .env.example is a build input because it determines the deployed .env.
git -C "$source_checkout" restore deploy_assets/dashboard.html
printf '\nSOURCE_POLICY_EXAMPLE_CANARY=from-template\n' >> "$source_checkout/.env.example"
env_example_project="$scratch/env-example-project"
expect_failure "template build inputs are dirty" \
    "$setup" "$env_example_project" --no-model-probe
[ ! -e "$env_example_project" ] \
    || fail "dirty .env.example created a full-setup destination"

env_example_output="$scratch/env-example-assembly"
"$setup" "$env_example_output" --assemble-only --no-model-probe \
    >"$scratch/env-example.log" 2>&1
env_example_digest="$(jq -r '.source.content_digest' "$env_example_output/.deploy_manifest.json")"
[ "$env_example_digest" != "$clean_digest" ] \
    || fail "source digest did not change with .env.example"
grep -Fq 'SOURCE_POLICY_EXAMPLE_CANARY=from-template' "$env_example_output/.env" \
    || fail "modified .env.example did not affect assembled .env"
jq -e '.source.dirty == true' "$env_example_output/.deploy_manifest.json" >/dev/null \
    || fail "dirty .env.example was not recorded in provenance"

# A persistent live-input change after the snapshot coordinator has sourced its
# private config must still trip the final live-tree stability check. Keep the
# race deterministic with a committed, disposable coordinator instrument.
race_checkout="$scratch/race-template"
git clone -q "$source_checkout" "$race_checkout"
/usr/bin/python3 -I - "$race_checkout/deploy_assets/scripts/setup/coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = '''source "$SETUP_CONFIG_MODULE"
resolve_setup_config "$@"
'''
replacement = '''source "$SETUP_CONFIG_MODULE"
if [ -n "${SOURCE_POLICY_RACE_CONFIG:-}" ]; then
    printf '\\n# concurrent source-policy canary\\n' >> "$SOURCE_POLICY_RACE_CONFIG"
    : > "$SOURCE_POLICY_RACE_FIRED"
fi
resolve_setup_config "$@"
'''
if text.count(anchor) != 1:
    raise SystemExit("late source-stability anchor changed")
path.write_text(text.replace(anchor, replacement))
PY
git -C "$race_checkout" add deploy_assets/scripts/setup/coordinator.sh
git -C "$race_checkout" \
    -c user.name='Source Policy Test' \
    -c user.email='source-policy@example.invalid' \
    commit -qm 'test: instrument late live-source mutation'
race_output="$scratch/race-assembly"
race_log="$scratch/race.log"
if SOURCE_POLICY_RACE_CONFIG="$race_checkout/deploy_assets/scripts/setup/resolve_config.sh" \
   SOURCE_POLICY_RACE_FIRED="$scratch/race-fired" \
   "$race_checkout/setup.sh" "$race_output" --assemble-only --no-model-probe \
   >"$race_log" 2>&1; then
    fail "assembly accepted a build-input change after early consumption"
fi
[ -e "$scratch/race-fired" ] || fail "live-source stability shim did not fire"
grep -Fq 'template build inputs changed during assembly' "$race_log" \
    || { cat "$race_log" >&2; fail "early source change missed stability error"; }
git -C "$race_checkout" restore deploy_assets/scripts/setup/resolve_config.sh

# Non-build documentation and .env are not template build provenance. After
# restoring build inputs, these changes must pass the cleanliness gate and
# reach prerequisite checking even though ZEROPAPER_REPO is invalid.
git -C "$source_checkout" restore .env.example
printf '\nnon-build-doc-change\n' >> "$source_checkout/README.md"
printf 'OPENAI_API_KEY=operator-config\n' > "$source_checkout/.env"
clean_gate_project="$scratch/clean-gate-project"
if env ZEROPAPER_REPO="$scratch/does-not-exist" PATH=/usr/bin:/bin \
    "$setup" "$clean_gate_project" --no-model-probe \
    >"$scratch/prereq.log" 2>&1; then
    fail "full setup unexpectedly passed deliberately missing prerequisites"
fi
grep -Fq -- "Checking prerequisites" "$scratch/prereq.log" \
    || { cat "$scratch/prereq.log" >&2; fail "non-build changes tripped source cleanliness"; }
if grep -Fq -- "Fetching template" "$scratch/prereq.log"; then
    fail "full setup attempted an internal template fetch"
fi
[ ! -e "$clean_gate_project" ] \
    || fail "prerequisite failure created a project destination"

echo "PASS: setup uses one checkout-local source with explicit provenance"
