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

env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$target" --assemble-only --no-model-probe \
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
jq '.source = {"kind": "stale-source-sentinel"}' \
    "$target/.deploy_manifest.json" > "$scratch/manifest.next"
mv "$scratch/manifest.next" "$target/.deploy_manifest.json"

setup_tmpdir_log="$scratch/update-setup-tmpdir.log"
python3 -I - "$target/process_log/.opencode-control" "$setup_tmpdir_log" <<'PY' &
import glob
import os
import sys
import time

control, output = sys.argv[1:]
deadline = time.monotonic() + 30
while time.monotonic() < deadline:
    matches = glob.glob(os.path.join(control, "update.*", "setup-tmp"))
    if matches:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(matches[0] + "\n")
        raise SystemExit
    time.sleep(0.005)
raise SystemExit("timed out waiting for protected child setup TMPDIR")
PY
setup_tmpdir_watcher=$!
if ! env PATH=/usr/bin:/bin "$repo_root/update.sh" "$target" \
    >"$scratch/update.log" 2>&1; then
    wait "$setup_tmpdir_watcher" || true
    cat "$scratch/update.log" >&2
    echo "FAIL: update.sh rejected the characterized deployment" >&2
    exit 1
fi
wait "$setup_tmpdir_watcher" \
    || { echo "FAIL: update child setup TMPDIR watcher failed" >&2; exit 1; }
grep -Eq -- "^$target/process_log/\.opencode-control/update\.[^/]+/setup-tmp$" \
    "$setup_tmpdir_log" \
    || { echo "FAIL: update child setup did not use protected control TMPDIR" >&2; exit 1; }

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
jq -e '
    .source.kind == "checkout"
    and (.source.content_digest | test("^sha256:[0-9a-f]{64}$"))
    and .source.update_channel == "checkout"
' "$target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: update did not refresh checkout source provenance" >&2; exit 1; }

# Manifest-owned update inputs follow extension lifecycle just like the agent
# and utility infrastructure they support.
extension_target="$scratch/extension-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$extension_target" \
    --assemble-only --no-model-probe --ext empirical \
    >"$scratch/extension-setup.log" 2>&1
extension_deps=".arpipeline/update_inputs/deps/extensions/empirical.txt"
[ -f "$extension_target/$extension_deps" ] \
    || { echo "FAIL: empirical update input was not deployed" >&2; exit 1; }
extension_process_log_saved="$scratch/extension-process-log.saved"
mv "$extension_target/process_log" "$extension_process_log_saved"
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$extension_target" \
    --dry-run --no-model-probe >"$scratch/extension-dry-run.log" 2>&1 \
    || { cat "$scratch/extension-dry-run.log" >&2; echo "FAIL: extension dry-run update failed" >&2; exit 1; }
[ ! -e "$extension_target/process_log" ] \
    || { echo "FAIL: dry-run update left newly created control paths" >&2; exit 1; }
grep -Fq 'No files modified' "$scratch/extension-dry-run.log" \
    || { echo "FAIL: dry-run update omitted its no-mutation contract" >&2; exit 1; }
mv "$extension_process_log_saved" "$extension_target/process_log"
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$extension_target" \
    --clear-ext --no-model-probe >"$scratch/extension-update.log" 2>&1 \
    || { cat "$scratch/extension-update.log" >&2; echo "FAIL: extension-removal update failed" >&2; exit 1; }
[ ! -e "$extension_target/$extension_deps" ] \
    || { echo "FAIL: stale empirical update input survived extension removal" >&2; exit 1; }
[ ! -e "$extension_target/.arpipeline/update_inputs/deps/extensions" ] \
    || { echo "FAIL: empty extension dependency directory survived extension removal" >&2; exit 1; }
jq -e '.extensions == []' "$extension_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: extension removal was not persisted" >&2; exit 1; }

# Adding an extension before launch merges its complete project-owned state
# schema and bootstrap directories from the verified fresh assembly.
schema_target="$scratch/schema-migration-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$schema_target" \
    --assemble-only --no-model-probe >"$scratch/schema-setup.log" 2>&1
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$schema_target" \
    --ext empirical --no-model-probe >"$scratch/schema-update.log" 2>&1 \
    || { cat "$scratch/schema-update.log" >&2; echo "FAIL: extension schema migration failed" >&2; exit 1; }
jq -e '
    . as $state
    | .stage2_mechanism_version == null
    and .stage3a_theory_version == null
    and ([
      "identification_plan_revision", "headline_replication", "replicator_self_refire",
      "data_integrity", "method_check", "claim_grounding", "paper_writer_pse",
      "claim_format_reexport"
    ] | all(. as $key | ($state.loops[$key].cap | numbers)))
' "$schema_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: empirical update omitted required pipeline-state schema" >&2; exit 1; }
[ -d "$schema_target/output/stage3a/figures" ] \
    || { echo "FAIL: empirical update omitted project-owned stage3a directories" >&2; exit 1; }
jq -e '.extensions == ["empirical"]' "$schema_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: empirical selector was not persisted" >&2; exit 1; }

# Once work starts, mode/extension route changes fail before managed mutation.
python3 - "$schema_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
data = json.load(open(path))
data["status"] = "running"
with open(path, "w") as handle:
    json.dump(data, handle, indent=2)
    handle.write("\n")
PY
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$schema_target" \
    --clear-ext --no-model-probe >"$scratch/schema-started-update.log" 2>&1; then
    echo "FAIL: started project accepted an extension-route migration" >&2; exit 1
fi
grep -Fq 'mode/extension/seed migration is supported only before' \
    "$scratch/schema-started-update.log" \
    || { cat "$scratch/schema-started-update.log" >&2; echo "FAIL: started selector refusal was unclear" >&2; exit 1; }
jq -e '.extensions == ["empirical"]' "$schema_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: rejected started selector migration changed manifest" >&2; exit 1; }

# Cross-variant updates fail before mutation because project-owned paper/state
# semantics cannot be reconciled safely in place.
variant_target="$scratch/variant-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$variant_target" \
    --assemble-only --no-model-probe --variant finance \
    >"$scratch/variant-setup.log" 2>&1
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$variant_target" \
    --variant llm_cognition --no-model-probe >"$scratch/variant-update.log" 2>&1; then
    echo "FAIL: cross-variant update unexpectedly succeeded" >&2; exit 1
fi
grep -Fq 'cannot migrate project-owned paper/state across variants' "$scratch/variant-update.log" \
    || { cat "$scratch/variant-update.log" >&2; echo "FAIL: variant boundary error was unclear" >&2; exit 1; }
jq -e '.variant == "finance"' "$variant_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: rejected variant migration changed the manifest" >&2; exit 1; }
grep -Fq 'finance theory paper' "$variant_target/CLAUDE.md" \
    || { echo "FAIL: rejected variant migration changed runtime documents" >&2; exit 1; }

# Faithful is an independent deployment selector, not merely seeded=true.
faithful_target="$scratch/faithful-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$faithful_target" \
    --assemble-only --no-model-probe --faithful \
    >"$scratch/faithful-setup.log" 2>&1
jq -e '.flags.seeded == true and .flags.faithful == true' \
    "$faithful_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: faithful setup did not persist its selector" >&2; exit 1; }
[ -f "$faithful_target/.claude/agents/faithful-drift-auditor.md" ] \
    || { echo "FAIL: faithful setup omitted its drift auditor" >&2; exit 1; }
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$faithful_target" \
    --no-model-probe >"$scratch/faithful-update.log" 2>&1 \
    || { cat "$scratch/faithful-update.log" >&2; echo "FAIL: faithful update failed" >&2; exit 1; }
jq -e '.flags.seeded == true and .flags.faithful == true' \
    "$faithful_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: faithful update degraded persisted selector state" >&2; exit 1; }
[ -f "$faithful_target/.claude/agents/faithful-drift-auditor.md" ] \
    || { echo "FAIL: faithful update pruned its drift auditor" >&2; exit 1; }

# Explicit pre-launch seed migration updates mutable bootstrap state as well as
# the refreshed manifest/runtime files.
seed_validation_target="$scratch/seed-validation-project"
seed_validation_foreign="$scratch/seed-validation-foreign"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$seed_validation_target" \
    --assemble-only --no-model-probe >"$scratch/seed-validation-setup.log" 2>&1
mv "$seed_validation_target/.claude" "$scratch/seed-validation-claude.saved"
mkdir "$seed_validation_foreign"
ln -s "$seed_validation_foreign" "$seed_validation_target/.claude"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$seed_validation_target" \
    --seeded --no-model-probe >"$scratch/seed-validation-update.log" 2>&1; then
    echo "FAIL: seed migration ignored an unsafe managed parent" >&2; exit 1
fi
jq -e '.seeded == false and .faithful == false and .current_stage == "stage_0"' \
    "$seed_validation_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: failed update partially migrated seed state" >&2; exit 1; }
[ ! -e "$seed_validation_target/output/seed" ] \
    || { echo "FAIL: failed update partially created seed bootstrap paths" >&2; exit 1; }
rm "$seed_validation_target/.claude"
mv "$scratch/seed-validation-claude.saved" "$seed_validation_target/.claude"
seed_validation_env="$scratch/seed-validation.env"
mv "$seed_validation_target/.env" "$seed_validation_env"
ln -s "$seed_validation_env" "$seed_validation_target/.env"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$seed_validation_target" \
    --seeded --no-model-probe >"$scratch/seed-env-validation-update.log" 2>&1; then
    echo "FAIL: seed migration ignored an aliased environment target" >&2; exit 1
fi
jq -e '.seeded == false and .faithful == false and .current_stage == "stage_0"' \
    "$seed_validation_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: env validation failure partially migrated seed state" >&2; exit 1; }
[ ! -e "$seed_validation_target/output/seed" ] \
    || { echo "FAIL: env validation failure partially created seed paths" >&2; exit 1; }
rm "$seed_validation_target/.env"
mv "$seed_validation_env" "$seed_validation_target/.env"

# A filesystem failure while creating bootstrap content must leave the mutable
# state and persisted selector unchanged.
chmod 0555 "$seed_validation_target/output"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$seed_validation_target" \
    --seeded --no-model-probe >"$scratch/seed-readonly-update.log" 2>&1; then
    chmod 0755 "$seed_validation_target/output"
    echo "FAIL: seed migration unexpectedly wrote through a read-only output directory" >&2
    exit 1
fi
chmod 0755 "$seed_validation_target/output"
jq -e '.seeded == false and .faithful == false and .current_stage == "stage_0"' \
    "$seed_validation_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: seed bootstrap failure partially migrated pipeline state" >&2; exit 1; }
[ ! -e "$seed_validation_target/output/seed" ] \
    || { echo "FAIL: seed bootstrap failure left partial seed content" >&2; exit 1; }
jq -e '.flags.seeded == false and .flags.faithful == false' \
    "$seed_validation_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: seed bootstrap failure partially persisted selector state" >&2; exit 1; }

# A failure after seed content was prepared must invoke the update-wide journal
# rollback rather than leaving that content ahead of state/manifest selectors.
seed_deps_dir="$seed_validation_target/.arpipeline/update_inputs/deps"
chmod 0555 "$seed_deps_dir"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$seed_validation_target" \
    --seeded --no-model-probe >"$scratch/seed-late-failure-update.log" 2>&1; then
    chmod 0755 "$seed_deps_dir"
    echo "FAIL: staged seed rollback regression did not reach its later failure" >&2
    exit 1
fi
chmod 0755 "$seed_deps_dir"
jq -e '.seeded == false and .faithful == false and .current_stage == "stage_0"' \
    "$seed_validation_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: later update failure partially migrated seed state" >&2; exit 1; }
[ ! -e "$seed_validation_target/output/seed" ] \
    || { echo "FAIL: later update failure did not roll back prepared seed content" >&2; exit 1; }
jq -e '.flags.seeded == false and .flags.faithful == false' \
    "$seed_validation_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: later update failure partially persisted seed selectors" >&2; exit 1; }

seed_target="$scratch/seed-migration-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$seed_target" \
    --assemble-only --no-model-probe >"$scratch/seed-setup.log" 2>&1
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$seed_target" \
    --seeded --no-model-probe >"$scratch/seed-update.log" 2>&1 \
    || { cat "$scratch/seed-update.log" >&2; echo "FAIL: seed migration failed" >&2; exit 1; }
jq -e '.flags.seeded == true and .flags.faithful == false' \
    "$seed_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: seed migration selector was not persisted" >&2; exit 1; }
jq -e '.seeded == true and .faithful == false and .current_stage == "seed_triage"' \
    "$seed_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: seed migration did not update mutable pipeline state" >&2; exit 1; }
[ -f "$seed_target/output/seed/README.md" ] \
    || { echo "FAIL: seed migration did not create the seed bootstrap directory" >&2; exit 1; }

# An activated environment may not supply updater uv, even when its lexical
# bin entry symlinks to an executable outside the environment.
active_update_env="$scratch/activated-update-env"
active_update_target="$scratch/activated-update-tools"
active_uv_marker="$scratch/activated-uv-ran"
mkdir -p "$active_update_env/bin" "$active_update_target"
printf '%s\n' '#!/bin/bash' ': > "${ACTIVE_UV_MARKER:?}"' 'exit 99' \
    > "$active_update_target/uv"
chmod +x "$active_update_target/uv"
ln -s "$active_update_target/uv" "$active_update_env/bin/uv"
ACTIVE_UV_MARKER="$active_uv_marker" VIRTUAL_ENV="$active_update_env" \
PATH="$active_update_env/bin:/usr/bin:/bin" \
    "$repo_root/update.sh" "$variant_target" --no-model-probe \
    >"$scratch/activated-update.log" 2>&1 \
    || { cat "$scratch/activated-update.log" >&2; echo "FAIL: update with activated environment failed" >&2; exit 1; }
[ ! -e "$active_uv_marker" ] \
    || { echo "FAIL: updater executed uv from an activated environment" >&2; exit 1; }

# Supported launchers hold a shared fcntl lock on the project directory inode
# for their lifetime; update must fail before mutation while any runtime owns
# that lock. Conversely, a launch must fail while an exclusive update lock is
# held, without consulting an activated project venv first.
runtime_lock_ready="$scratch/runtime-lock-ready"
manual_lock_target="$scratch/manual-lock-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$manual_lock_target" \
    --assemble-only --manual --no-model-probe >"$scratch/manual-lock-setup.log" 2>&1
runtime_lock_mode=shared
/usr/bin/python3 -I - "$manual_lock_target" "$runtime_lock_ready" "$runtime_lock_mode" <<'PY' &
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
fcntl.flock(fd, fcntl.LOCK_SH)
open(sys.argv[2], "w").write("ready\n")
time.sleep(30)
PY
runtime_lock_pid=$!
for _ in $(seq 1 100); do [ -s "$runtime_lock_ready" ] && break; sleep 0.02; done
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$manual_lock_target" \
    --no-model-probe >"$scratch/manual-lock-update.log" 2>&1; then
    kill "$runtime_lock_pid" 2>/dev/null || true
    wait "$runtime_lock_pid" 2>/dev/null || true
    echo "FAIL: locked manual project accepted an update" >&2; exit 1
fi
kill "$runtime_lock_pid" 2>/dev/null || true
wait "$runtime_lock_pid" 2>/dev/null || true
[ ! -e "$manual_lock_target/process_log" ] \
    || { echo "FAIL: refused update created control paths before locking" >&2; exit 1; }
env PATH=/usr/bin:/bin "$repo_root/update.sh" "$manual_lock_target" \
    --ext empirical --no-model-probe >"$scratch/manual-extension-update.log" 2>&1 \
    || { cat "$scratch/manual-extension-update.log" >&2; echo "FAIL: manual extension refresh failed" >&2; exit 1; }
jq -e '.flags.manual == true and .extensions == ["empirical"]' \
    "$manual_lock_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: manual extension refresh did not persist its selector" >&2; exit 1; }
[ ! -e "$manual_lock_target/process_log" ] \
    || { echo "FAIL: manual extension refresh left autonomous/control state" >&2; exit 1; }

: > "$runtime_lock_ready"
runtime_lock_mode=exclusive
/usr/bin/python3 -I - "$variant_target" "$runtime_lock_ready" "$runtime_lock_mode" <<'PY' &
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
mode = fcntl.LOCK_EX if sys.argv[3] == "exclusive" else fcntl.LOCK_SH
fcntl.flock(fd, mode)
open(sys.argv[2], "w").write("ready\n")
time.sleep(30)
PY
runtime_lock_pid=$!
for _ in $(seq 1 100); do [ -s "$runtime_lock_ready" ] && break; sleep 0.02; done
mkdir -p "$variant_target/.venv/bin"
launch_mkdir_marker="$scratch/launch-project-mkdir-ran"
printf '%s\n' '#!/bin/bash' ': > "${LAUNCH_MKDIR_MARKER:?}"' 'exec /bin/mkdir "$@"' \
    > "$variant_target/.venv/bin/mkdir"
chmod +x "$variant_target/.venv/bin/mkdir"
if LAUNCH_MKDIR_MARKER="$launch_mkdir_marker" \
    PATH="$variant_target/.venv/bin:/usr/bin:/bin" \
    "$variant_target/launch.sh" opencode --once \
    >"$scratch/runtime-lock-launch.log" 2>&1; then
    kill "$runtime_lock_pid" 2>/dev/null || true
    wait "$runtime_lock_pid" 2>/dev/null || true
    echo "FAIL: launch ran concurrently with an exclusive project update lock" >&2
    exit 1
fi
[ ! -e "$launch_mkdir_marker" ] \
    || { echo "FAIL: launch used project mkdir before acquiring its runtime lock" >&2; exit 1; }
grep -Fq 'could not acquire the project runtime/update lock' "$scratch/runtime-lock-launch.log" \
    || { cat "$scratch/runtime-lock-launch.log" >&2; echo "FAIL: launch lock refusal was unclear" >&2; exit 1; }
kill "$runtime_lock_pid" 2>/dev/null || true
wait "$runtime_lock_pid" 2>/dev/null || true

: > "$runtime_lock_ready"
runtime_lock_mode=shared
/usr/bin/python3 -I - "$variant_target" "$runtime_lock_ready" "$runtime_lock_mode" <<'PY' &
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
mode = fcntl.LOCK_EX if sys.argv[3] == "exclusive" else fcntl.LOCK_SH
fcntl.flock(fd, mode)
open(sys.argv[2], "w").write("ready\n")
time.sleep(30)
PY
runtime_lock_pid=$!
for _ in $(seq 1 100); do [ -s "$runtime_lock_ready" ] && break; sleep 0.02; done
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$variant_target" \
    --no-model-probe >"$scratch/runtime-lock-update.log" 2>&1; then
    kill "$runtime_lock_pid" 2>/dev/null || true
    wait "$runtime_lock_pid" 2>/dev/null || true
    echo "FAIL: update ran concurrently with a locked project runtime" >&2; exit 1
fi
kill "$runtime_lock_pid" 2>/dev/null || true
wait "$runtime_lock_pid" 2>/dev/null || true
grep -Fq 'project runtime is active' "$scratch/runtime-lock-update.log" \
    || { cat "$scratch/runtime-lock-update.log" >&2; echo "FAIL: runtime-lock refusal was unclear" >&2; exit 1; }

# The launcher shell—not a killable helper—owns the shared descriptor while an
# interactive CLI child runs.
fake_runtime_bin="$scratch/fake-runtime-bin"
fake_runtime_ready="$scratch/fake-runtime-ready"
fake_runtime_pid_file="$scratch/fake-runtime-pid"
mkdir "$fake_runtime_bin"
printf '%s\n' \
    '#!/bin/bash' \
    'case " $* " in' \
    '  *" --dangerously-skip-permissions "*)' \
    '    /usr/bin/python3 -I -c '\''import fcntl; fcntl.flock(9, fcntl.LOCK_UN)'\'' 2>/dev/null || true' \
    '    if [ "${FAKE_RUNTIME_DETACH:-0}" = "1" ]; then' \
    '      sleep 30 & printf "%s\n" "$!" > "${FAKE_DETACHED_PID_FILE:?}"; exit 0' \
    '    fi' \
    '    printf "%s\n" "$$" > "${FAKE_RUNTIME_PID_FILE:?}"' \
    '    : > "${FAKE_RUNTIME_READY:?}"' \
    '    sleep 30' \
    '    ;;' \
    '  *) printf "model not found\n"; exit 1 ;;' \
    'esac' > "$fake_runtime_bin/claude"
chmod +x "$fake_runtime_bin/claude"
FAKE_RUNTIME_READY="$fake_runtime_ready" FAKE_RUNTIME_PID_FILE="$fake_runtime_pid_file" \
PATH="$fake_runtime_bin:/usr/bin:/bin" \
    "$variant_target/launch.sh" claude >"$scratch/fake-runtime.log" 2>&1 &
fake_launch_pid=$!
for _ in $(seq 1 100); do [ -e "$fake_runtime_ready" ] && break; sleep 0.02; done
[ -e "$fake_runtime_ready" ] \
    || { cat "$scratch/fake-runtime.log" >&2; echo "FAIL: fake supported runtime did not start" >&2; exit 1; }
if /usr/bin/python3 -I - "$variant_target" <<'PY'
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(1)
PY
then
    kill "$fake_launch_pid" 2>/dev/null || true
    echo "FAIL: exclusive lock bypassed a live supported runtime" >&2; exit 1
fi
kill "$fake_launch_pid" 2>/dev/null || true
wait "$fake_launch_pid" 2>/dev/null || true
if [ -s "$fake_runtime_pid_file" ]; then
    kill "$(cat "$fake_runtime_pid_file")" 2>/dev/null || true
fi
fake_detached_pid_file="$scratch/fake-detached-pid"
FAKE_RUNTIME_DETACH=1 FAKE_DETACHED_PID_FILE="$fake_detached_pid_file" \
PATH="$fake_runtime_bin:/usr/bin:/bin" \
    "$variant_target/launch.sh" claude >"$scratch/fake-detached-runtime.log" 2>&1
[ -s "$fake_detached_pid_file" ] \
    || { cat "$scratch/fake-detached-runtime.log" >&2; echo "FAIL: fake detached runtime did not start" >&2; exit 1; }
/usr/bin/python3 -I - "$variant_target" <<'PY' \
    || { echo "FAIL: detached runtime descendant leaked the project lock" >&2; exit 1; }
import fcntl, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
PY
kill "$(cat "$fake_detached_pid_file")" 2>/dev/null || true

echo "PASS: infrastructure refreshes and project bootstrap content is preserved"
