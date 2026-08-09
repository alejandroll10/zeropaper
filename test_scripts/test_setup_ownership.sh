#!/usr/bin/env bash
# Integration test for the infrastructure/bootstrap ownership boundary (#255).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/setup-ownership-integration.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT
target="$scratch/project"

# Ownership helpers must reject unsafe or non-canonical paths before touching
# the filesystem. In particular, a copy destination that names a directory
# must not fall back to cp's "copy inside directory" behavior.
P="$scratch/ownership-api"
TMPDIR="$scratch"
export TMPDIR
mkdir -p "$P"
# shellcheck source=../deploy_assets/scripts/setup/ownership.sh
source "$repo_root/deploy_assets/scripts/setup/ownership.sh"
setup_ownership_init
printf 'payload\n' > "$scratch/payload"

expect_invalid_path() {
    local rel="$1"
    if (infrastructure_copy_file 1 "$scratch/payload" "$rel") \
        >"$scratch/invalid-path.log" 2>&1; then
        echo "FAIL: ownership helper accepted invalid path '$rel'" >&2
        exit 1
    fi
}

expect_invalid_path ""
expect_invalid_path "."
expect_invalid_path ".."
expect_invalid_path "../outside"
expect_invalid_path "nested/../../outside"
expect_invalid_path "/absolute"
expect_invalid_path "carriage"$'\r'"return"
expect_invalid_path "vertical"$'\v'"tab"
expect_invalid_path "form"$'\f'"feed"
[ ! -e "$scratch/outside" ] \
    || { echo "FAIL: invalid ownership path wrote outside the project" >&2; exit 1; }
[ ! -e "$P/payload" ] \
    || { echo "FAIL: '.' destination copied a payload before rejection" >&2; exit 1; }

mkdir -p "$P/existing-dir"
if (infrastructure_copy_file 1 "$scratch/payload" "existing-dir") \
    >"$scratch/directory-destination.log" 2>&1; then
    echo "FAIL: ownership helper accepted a directory as a file destination" >&2
    exit 1
fi
[ ! -e "$P/existing-dir/payload" ] \
    || { echo "FAIL: directory destination was mutated before rejection" >&2; exit 1; }

mkdir -p "$scratch/outside-parent"
ln -s "$scratch/outside-parent" "$P/linked-parent"
if (infrastructure_copy_file 1 "$scratch/payload" "linked-parent/infra") \
    >"$scratch/infra-parent-symlink.log" 2>&1; then
    echo "FAIL: infrastructure copy traversed a parent symlink" >&2
    exit 1
fi
if (bootstrap_copy_file "$scratch/payload" "linked-parent/bootstrap") \
    >"$scratch/bootstrap-parent-symlink.log" 2>&1; then
    echo "FAIL: bootstrap copy traversed a parent symlink" >&2
    exit 1
fi
if (infrastructure_dir 1 "linked-parent/infra-dir") \
    >"$scratch/infra-dir-parent-symlink.log" 2>&1; then
    echo "FAIL: infrastructure directory traversed a parent symlink" >&2
    exit 1
fi
if (bootstrap_dir "linked-parent/bootstrap-dir") \
    >"$scratch/bootstrap-dir-parent-symlink.log" 2>&1; then
    echo "FAIL: bootstrap directory traversed a parent symlink" >&2
    exit 1
fi
[ -z "$(find "$scratch/outside-parent" -mindepth 1 -print -quit)" ] \
    || { echo "FAIL: parent symlink target was mutated before rejection" >&2; exit 1; }

printf 'outside-original\n' > "$scratch/outside-file"
ln -s "$scratch/outside-file" "$P/linked-file"
if (infrastructure_copy_file 1 "$scratch/payload" "linked-file") \
    >"$scratch/infra-target-symlink.log" 2>&1; then
    echo "FAIL: infrastructure copy accepted an exact symlink destination" >&2
    exit 1
fi
if (bootstrap_copy_file "$scratch/payload" "linked-file") \
    >"$scratch/bootstrap-target-symlink.log" 2>&1; then
    echo "FAIL: bootstrap copy accepted an exact symlink destination" >&2
    exit 1
fi
if (infrastructure_file 1 "linked-file") \
    >"$scratch/infra-register-symlink.log" 2>&1; then
    echo "FAIL: infrastructure_file registered a symlink" >&2
    exit 1
fi
grep -Fqx 'outside-original' "$scratch/outside-file" \
    || { echo "FAIL: exact symlink target was overwritten before rejection" >&2; exit 1; }

env PATH=/usr/bin:/bin bash "$repo_root/setup.sh" "$target" --local --no-model-probe \
    >"$scratch/setup.log" 2>&1

cp "$target/CLAUDE.md" "$scratch/expected-claude.md"
printf '\nINFRASTRUCTURE_SENTINEL\n' >> "$target/CLAUDE.md"
printf 'stale\n' > "$target/.claude/agents/stale-agent.md"

printf 'PROJECT_MAIN_SENTINEL\n' > "$target/paper/main.tex"
python3 - "$target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as handle:
    state = json.load(handle)
state["project_ownership_sentinel"] = "keep"
with open(path, "w") as handle:
    json.dump(state, handle, indent=2)
    handle.write("\n")
PY
printf '\nPROJECT_ENV_SENTINEL=keep\n' >> "$target/.env"

if ! env PATH=/usr/bin:/bin bash "$repo_root/update.sh" "$target" \
    >"$scratch/update.log" 2>&1; then
    cat "$scratch/update.log" >&2
    echo "FAIL: update.sh rejected the characterized deployment" >&2
    exit 1
fi

cmp -s "$scratch/expected-claude.md" "$target/CLAUDE.md" \
    || { echo "FAIL: template-owned CLAUDE.md was not refreshed" >&2; exit 1; }
[ ! -e "$target/.claude/agents/stale-agent.md" ] \
    || { echo "FAIL: stale file survived infrastructure-dir replacement" >&2; exit 1; }
grep -Fqx 'PROJECT_MAIN_SENTINEL' "$target/paper/main.tex" \
    || { echo "FAIL: project-owned paper/main.tex was overwritten" >&2; exit 1; }
python3 - "$target/process_log/pipeline_state.json" <<'PY' \
    || { echo "FAIL: project-owned pipeline state was overwritten" >&2; exit 1; }
import json, sys
with open(sys.argv[1]) as handle:
    state = json.load(handle)
raise SystemExit(0 if state.get("project_ownership_sentinel") == "keep" else 1)
PY
grep -Fqx 'PROJECT_ENV_SENTINEL=keep' "$target/.env" \
    || { echo "FAIL: project-owned .env value was not preserved" >&2; exit 1; }

echo "PASS: infrastructure refreshes and project bootstrap content is preserved"
