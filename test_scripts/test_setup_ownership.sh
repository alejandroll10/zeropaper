#!/usr/bin/env bash
# Integration test for the infrastructure/bootstrap ownership boundary (#255).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/setup-ownership-integration.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT
target="$scratch/project"
finance_selectors=(
    --variant finance --no-mode --clear-ext --no-seeded --no-faithful
    --no-manual --no-light --no-halt-on-core-bypass
)

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
grep -Eq -- '--source-digest sha256:[0-9a-f]{64} --variant finance --no-mode --clear-ext --no-seeded --no-faithful --no-manual --no-light --no-halt-on-core-bypass' \
    "$scratch/setup.log" \
    || { cat "$scratch/setup.log" >&2; echo "FAIL: assemble-only setup omitted the canonical update attestation" >&2; exit 1; }
canonical_implied_target="$scratch/canonical-implied-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$canonical_implied_target" \
    --assemble-only --no-model-probe --variant llm_cognition \
    >"$scratch/canonical-implied-setup.log" 2>&1
grep -Eq -- '--variant llm_cognition --no-mode --clear-ext --ext theory_llm --no-seeded --no-faithful --no-manual --no-light --no-halt-on-core-bypass' \
    "$scratch/canonical-implied-setup.log" \
    || { cat "$scratch/canonical-implied-setup.log" >&2; echo "FAIL: setup attestation omitted an implied canonical extension" >&2; exit 1; }

cp "$target/CLAUDE.md" "$scratch/expected-claude.md"
printf '\nINFRASTRUCTURE_SENTINEL\n' >> "$target/CLAUDE.md"
printf 'stale\n' > "$target/.claude/agents/stale-agent.md"

printf 'PROJECT_MAIN_SENTINEL\n' > "$target/paper/main.tex"
python3 - "$target/process_log/pipeline_state.json" <<'PY'
import json, os, sys
path = sys.argv[1]
with open(path) as handle:
    state = json.load(handle)
state["history"].append({"timestamp": "2026-08-22T00:00:00Z",
                         "event": "project ownership sentinel"})
with open(path, "w") as handle:
    json.dump(state, handle, indent=2)
    handle.write("\n")
PY
printf '\nPROJECT_ENV_SENTINEL=keep\n' >> "$target/.env"

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
if ! env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$target" \
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
raise SystemExit(0 if any(
    row.get("event") == "project ownership sentinel" for row in state["history"]
) else 1)
PY
grep -Fqx 'PROJECT_ENV_SENTINEL=keep' "$target/.env" \
    || { echo "FAIL: project-owned .env value was not preserved" >&2; exit 1; }
jq -e '
    .source.kind == "checkout"
    and (.source.content_digest | test("^sha256:[0-9a-f]{64}$"))
    and .source.update_channel == "checkout"
' "$target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: update did not refresh checkout source provenance" >&2; exit 1; }

# A caller-controlled fallback PATH must not supply jq to the host-authority
# updater. Only the launcher's validated fixed installation path may run.
fake_jq_bin="$scratch/fake-jq-bin"
fake_jq_marker="$scratch/fake-jq-ran"
mkdir "$fake_jq_bin"
cat > "$fake_jq_bin/jq" <<'SH'
#!/bin/bash
: > "${FAKE_JQ_MARKER:?}"
exec /usr/bin/jq "$@"
SH
chmod +x "$fake_jq_bin/jq"
FAKE_JQ_MARKER="$fake_jq_marker" PATH="$fake_jq_bin:/usr/bin:/bin" \
    "$repo_root/test_scripts/update_with_manifest_selectors.py" "$target" \
    --dry-run --no-model-probe >"$scratch/fixed-jq-update.log" 2>&1 \
    || { cat "$scratch/fixed-jq-update.log" >&2; echo "FAIL: fixed-path jq update failed" >&2; exit 1; }
[ ! -e "$fake_jq_marker" ] \
    || { echo "FAIL: updater executed jq from caller-controlled PATH" >&2; exit 1; }

launch_mode_before="$(python3 -I -c 'import os,stat,sys; print(stat.S_IMODE(os.stat(sys.argv[1]).st_mode))' "$target/launch.sh")"
claude_mode_before="$(python3 -I -c 'import os,stat,sys; print(stat.S_IMODE(os.stat(sys.argv[1]).st_mode))' "$target/CLAUDE.md")"
(umask 077; env PATH=/usr/bin:/bin \
    "$repo_root/test_scripts/update_with_manifest_selectors.py" "$target" \
    --no-model-probe >"$scratch/hostile-umask-update.log" 2>&1) \
    || { cat "$scratch/hostile-umask-update.log" >&2; echo "FAIL: hostile-umask update failed" >&2; exit 1; }
[ "$(python3 -I -c 'import os,stat,sys; print(stat.S_IMODE(os.stat(sys.argv[1]).st_mode))' "$target/launch.sh")" = "$launch_mode_before" ] \
    || { echo "FAIL: update changed executable mode under hostile umask" >&2; exit 1; }
[ "$(python3 -I -c 'import os,stat,sys; print(stat.S_IMODE(os.stat(sys.argv[1]).st_mode))' "$target/CLAUDE.md")" = "$claude_mode_before" ] \
    || { echo "FAIL: update changed managed-file mode under hostile umask" >&2; exit 1; }

# A crash-left general transaction marker blocks launch and dry-run. A normal
# retry completes the same-version refresh and durably clears the marker.
transaction_control="$target/process_log/.opencode-control"
mkdir -p "$transaction_control"
printf '%s\n' 'zeropaper update transaction' \
    > "$transaction_control/update-in-progress"
if env PATH=/usr/bin:/bin "$target/launch.sh" codex --once \
    >"$scratch/transaction-launch.log" 2>&1; then
    echo "FAIL: launcher ignored an interrupted update marker" >&2; exit 1
fi
grep -Fq 'interrupted project update detected' "$scratch/transaction-launch.log" \
    || { cat "$scratch/transaction-launch.log" >&2; echo "FAIL: launch transaction refusal was unclear" >&2; exit 1; }
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$target" \
    --dry-run --no-model-probe >"$scratch/transaction-dry-run.log" 2>&1; then
    echo "FAIL: dry-run consumed an interrupted update marker" >&2; exit 1
fi
[ -f "$transaction_control/update-in-progress" ] \
    || { echo "FAIL: dry-run removed an interrupted update marker" >&2; exit 1; }
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$target" \
    --no-model-probe >"$scratch/transaction-resume.log" 2>&1 \
    || { cat "$scratch/transaction-resume.log" >&2; echo "FAIL: interrupted update did not resume" >&2; exit 1; }
[ ! -e "$transaction_control/update-in-progress" ] \
    || { echo "FAIL: successful retry retained the update marker" >&2; exit 1; }

# The orchestrator must not observe a registry/receipt transition before the
# results utility has recovered its durable publication journal.
printf '%s\n' '{"phase":"prepared"}' \
    > "$target/process_log/results_pipeline.transaction.json"
if env PATH=/usr/bin:/bin "$target/launch.sh" codex --once \
    >"$scratch/results-transaction-launch.log" 2>&1; then
    echo "FAIL: launcher ignored an interrupted results transaction" >&2; exit 1
fi
grep -Fq 'interrupted computed-results transaction detected' \
    "$scratch/results-transaction-launch.log" \
    || { cat "$scratch/results-transaction-launch.log" >&2; echo "FAIL: results transaction refusal was unclear" >&2; exit 1; }
rm "$target/process_log/results_pipeline.transaction.json"

# A project-writable manifest cannot authorize a different source snapshot.
# The operator's digest is supplied independently from the trusted setup record.
source_attestation_target="$scratch/source-attestation-project"
cp -a "$target" "$source_attestation_target"
trusted_source_digest="$(jq -r '.source.content_digest' "$source_attestation_target/.deploy_manifest.json")"
jq '.source.content_digest = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"' \
    "$source_attestation_target/.deploy_manifest.json" \
    > "$scratch/source-attestation-manifest.next"
mv "$scratch/source-attestation-manifest.next" \
    "$source_attestation_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$source_attestation_target" \
    --source-digest "$trusted_source_digest" --variant finance --no-mode --clear-ext \
    --no-seeded --no-faithful --no-manual --no-light \
    --no-halt-on-core-bypass --no-model-probe \
    >"$scratch/source-attestation-update.log" 2>&1; then
    echo "FAIL: project manifest authorized its own source snapshot" >&2; exit 1
fi
grep -Fq 'does not match the operator-attested trusted setup record' \
    "$scratch/source-attestation-update.log" \
    || { cat "$scratch/source-attestation-update.log" >&2; echo "FAIL: source-attestation refusal was unclear" >&2; exit 1; }
[ ! -e "$source_attestation_target/process_log/.opencode-control/update-in-progress" ] \
    || { echo "FAIL: source-attestation preflight created a launch barrier" >&2; exit 1; }

# SIGKILL of the visible updater must not release LOCK_EX while an orphaned
# refresh body can still write. The detached guardian kills/drains that body;
# only then may a second exclusive lock be acquired.
killed_update_target="$scratch/killed-update-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$killed_update_target" \
    --assemble-only --no-model-probe >"$scratch/killed-update-setup.log" 2>&1
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/killed-update-snapshots.before"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$killed_update_target" \
    --no-model-probe >"$scratch/killed-update.log" 2>&1 &
killed_update_pid=$!
killed_marker="$killed_update_target/process_log/.opencode-control/update-in-progress"
for _ in $(seq 1 1000); do
    [ -f "$killed_marker" ] && break
    kill -0 "$killed_update_pid" 2>/dev/null || break
    sleep 0.01
done
[ -f "$killed_marker" ] \
    || { cat "$scratch/killed-update.log" >&2; echo "FAIL: updater marker was never published" >&2; exit 1; }
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/killed-update-snapshots.during"
killed_update_snapshot="$(comm -13 \
    "$scratch/killed-update-snapshots.before" \
    "$scratch/killed-update-snapshots.during")"
[ -n "$killed_update_snapshot" ] \
    && [ "$(printf '%s\n' "$killed_update_snapshot" | wc -l)" -eq 1 ] \
    || { echo "FAIL: killed updater did not isolate one source snapshot" >&2; exit 1; }
kill -KILL "$killed_update_pid"
wait "$killed_update_pid" 2>/dev/null || true
/usr/bin/python3 -I - "$killed_update_target" <<'PY'
import fcntl
import hashlib
import os
import sys
import time

root = sys.argv[1]
fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
fcntl.flock(fd, fcntl.LOCK_EX)
path = os.path.join(root, "CLAUDE.md")
before = hashlib.sha256(open(path, "rb").read()).digest()
time.sleep(0.5)
after = hashlib.sha256(open(path, "rb").read()).digest()
if before != after:
    raise SystemExit("orphaned updater wrote while a successor held LOCK_EX")
PY
for _ in $(seq 1 1500); do
    [ ! -e "$killed_update_snapshot" ] && break
    sleep 0.02
done
[ ! -e "$killed_update_snapshot" ] \
    || { echo "FAIL: killed public updater leaked its source snapshot" >&2; exit 1; }
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$killed_update_target" \
    --no-model-probe >"$scratch/killed-update-recovery.log" 2>&1 \
    || { cat "$scratch/killed-update-recovery.log" >&2; echo "FAIL: killed update did not recover" >&2; exit 1; }
[ ! -e "$killed_marker" ] \
    || { echo "FAIL: killed update recovery retained its marker" >&2; exit 1; }

# update.sh intentionally supports only the current v2.28 manifest generation.
# Older and pre-manifest deployments fail before managed infrastructure changes.
unsupported_target="$scratch/unsupported-generation-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$unsupported_target" \
    --assemble-only --no-model-probe >"$scratch/unsupported-generation-setup.log" 2>&1
unsupported_claude_inode="$(ls -di "$unsupported_target/CLAUDE.md")"
jq '.template_version = "2.27.0+old"' "$unsupported_target/.deploy_manifest.json" \
    > "$scratch/unsupported-generation-manifest.json"
mv "$scratch/unsupported-generation-manifest.json" \
    "$unsupported_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$unsupported_target" \
    --no-model-probe >"$scratch/unsupported-generation-update.log" 2>&1; then
    echo "FAIL: updater accepted an older deployment generation" >&2; exit 1
fi
grep -Fq 'update requires a 2.28.1 deployment' \
    "$scratch/unsupported-generation-update.log" \
    || { echo "FAIL: older-generation rejection was unclear" >&2; exit 1; }
[ "$(ls -di "$unsupported_target/CLAUDE.md")" = "$unsupported_claude_inode" ] \
    || { echo "FAIL: older-generation rejection changed infrastructure" >&2; exit 1; }
jq '.manifest_version = 0 | .legacy_selector_journal = {}' \
    "$unsupported_target/.deploy_manifest.json" \
    > "$scratch/unsupported-manifest-generation.json"
mv "$scratch/unsupported-manifest-generation.json" \
    "$unsupported_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$unsupported_target" \
    --no-model-probe >"$scratch/unsupported-manifest-generation.log" 2>&1; then
    echo "FAIL: updater accepted an obsolete manifest schema" >&2; exit 1
fi
grep -Eq 'unsupported deployment manifest generation|exact current-generation shape' \
    "$scratch/unsupported-manifest-generation.log" \
    || { cat "$scratch/unsupported-manifest-generation.log" >&2; echo "FAIL: manifest-generation rejection was unclear" >&2; exit 1; }
jq 'del(.legacy_selector_journal) | .manifest_version = 1 | .template_version = "2.28.0+adjacent"' \
    "$unsupported_target/.deploy_manifest.json" \
    > "$scratch/unsupported-adjacent-manifest.json"
mv "$scratch/unsupported-adjacent-manifest.json" \
    "$unsupported_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$unsupported_target" \
    --no-model-probe >"$scratch/unsupported-adjacent-update.log" 2>&1; then
    echo "FAIL: updater accepted an adjacent template version" >&2; exit 1
fi
grep -Fq 'update requires a 2.28.1 deployment' \
    "$scratch/unsupported-adjacent-update.log" \
    || { echo "FAIL: adjacent-version rejection was unclear" >&2; exit 1; }
rm "$unsupported_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$unsupported_target" \
    --no-model-probe >"$scratch/pre-manifest-update.log" 2>&1; then
    echo "FAIL: updater accepted a pre-manifest deployment" >&2; exit 1
fi
grep -Fq 'supports only same-version manifest-backed deployments' \
    "$scratch/pre-manifest-update.log" \
    || { echo "FAIL: pre-manifest rejection was unclear" >&2; exit 1; }

# Manifest selectors must be typed before Bash consumes them; a string-valued
# manual flag may not bypass the autonomous/manual layout guard.
invalid_manifest_target="$scratch/invalid-manifest-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$invalid_manifest_target" \
    --assemble-only --no-model-probe >"$scratch/invalid-manifest-setup.log" 2>&1
printf '\nMANIFEST_PREFLIGHT_SENTINEL\n' >> "$invalid_manifest_target/CLAUDE.md"
jq '.flags.manual = "true"' "$invalid_manifest_target/.deploy_manifest.json" \
    > "$scratch/invalid-manifest.next"
mv "$scratch/invalid-manifest.next" "$invalid_manifest_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$invalid_manifest_target" \
    --no-model-probe >"$scratch/invalid-manifest-update.log" 2>&1; then
    echo "FAIL: updater accepted a string-valued manual flag" >&2; exit 1
fi
grep -Fq 'deployment manifest flags are malformed' \
    "$scratch/invalid-manifest-update.log" \
    || { cat "$scratch/invalid-manifest-update.log" >&2; echo "FAIL: malformed-manifest rejection was unclear" >&2; exit 1; }
grep -Fq 'MANIFEST_PREFLIGHT_SENTINEL' "$invalid_manifest_target/CLAUDE.md" \
    || { echo "FAIL: malformed-manifest rejection changed infrastructure" >&2; exit 1; }

# A managed file leaf with an incompatible type fails before any replacement.
managed_leaf_target="$scratch/managed-leaf-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$managed_leaf_target" \
    --assemble-only --no-model-probe >"$scratch/managed-leaf-setup.log" 2>&1
printf '\nLEAF_PREFLIGHT_SENTINEL\n' \
    >> "$managed_leaf_target/.claude/agents/paper-writer.md"
rm "$managed_leaf_target/CLAUDE.md"
mkdir "$managed_leaf_target/CLAUDE.md"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$managed_leaf_target" \
    --no-model-probe >"$scratch/managed-leaf-update.log" 2>&1; then
    echo "FAIL: updater accepted a directory at a managed file leaf" >&2; exit 1
fi
grep -Fq 'managed file target has an incompatible type' \
    "$scratch/managed-leaf-update.log" \
    || { cat "$scratch/managed-leaf-update.log" >&2; echo "FAIL: managed-leaf rejection was unclear" >&2; exit 1; }
grep -Fq 'LEAF_PREFLIGHT_SENTINEL' \
    "$managed_leaf_target/.claude/agents/paper-writer.md" \
    || { echo "FAIL: managed-leaf rejection happened after replacement" >&2; exit 1; }

# Stage-9 recovery requires history, so the complete state contract must reject
# its absence before refreshing any managed bytes.
missing_history_target="$scratch/missing-history-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$missing_history_target" \
    --assemble-only --no-model-probe >"$scratch/missing-history-setup.log" 2>&1
python3 - "$missing_history_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
state = json.load(open(path))
state.pop("history")
state["status"] = "complete"
state["current_stage"] = "stage_10"
with open(path, "w") as handle:
    json.dump(state, handle)
    handle.write("\n")
PY
printf '\nHISTORY_PREFLIGHT_SENTINEL\n' >> "$missing_history_target/CLAUDE.md"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$missing_history_target" \
    --no-model-probe >"$scratch/missing-history-update.log" 2>&1; then
    echo "FAIL: updater accepted pipeline state without history" >&2; exit 1
fi
grep -Fq 'pipeline state history must be an array' \
    "$scratch/missing-history-update.log" \
    || { cat "$scratch/missing-history-update.log" >&2; echo "FAIL: missing-history rejection was unclear" >&2; exit 1; }
grep -Fq 'HISTORY_PREFLIGHT_SENTINEL' "$missing_history_target/CLAUDE.md" \
    || { echo "FAIL: missing-history rejection changed infrastructure" >&2; exit 1; }

# The same-version state contract validates routing fields too, not only the
# evidence-pointer subset, before any managed replacement.
malformed_status_target="$scratch/malformed-status-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$malformed_status_target" \
    --assemble-only --no-model-probe >"$scratch/malformed-status-setup.log" 2>&1
jq '.status = []' "$malformed_status_target/process_log/pipeline_state.json" \
    > "$scratch/malformed-status.next"
mv "$scratch/malformed-status.next" \
    "$malformed_status_target/process_log/pipeline_state.json"
printf '\nSTATUS_PREFLIGHT_SENTINEL\n' >> "$malformed_status_target/CLAUDE.md"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$malformed_status_target" \
    --no-model-probe >"$scratch/malformed-status-update.log" 2>&1; then
    echo "FAIL: updater accepted a non-string pipeline status" >&2; exit 1
fi
grep -Fq 'pipeline state field status has an invalid type' \
    "$scratch/malformed-status-update.log" \
    || { cat "$scratch/malformed-status-update.log" >&2; echo "FAIL: malformed-status rejection was unclear" >&2; exit 1; }
grep -Fq 'STATUS_PREFLIGHT_SENTINEL' "$malformed_status_target/CLAUDE.md" \
    || { echo "FAIL: malformed status was rejected after replacement" >&2; exit 1; }
[ ! -e "$malformed_status_target/process_log/.opencode-control/update-in-progress" ] \
    || { echo "FAIL: rejected preflight created a launch-blocking marker" >&2; exit 1; }
# Use an independent deployment to exercise the separate unknown-value case.
unknown_status_target="$scratch/unknown-status-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$unknown_status_target" \
    --assemble-only --no-model-probe >"$scratch/unknown-status-setup.log" 2>&1
jq '.status = "halted_invented_state"' \
    "$unknown_status_target/process_log/pipeline_state.json" \
    > "$scratch/unknown-status.next"
mv "$scratch/unknown-status.next" \
    "$unknown_status_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$unknown_status_target" \
    --dry-run --no-model-probe >"$scratch/unknown-status-update.log" 2>&1; then
    echo "FAIL: updater accepted an unknown pipeline status" >&2; exit 1
fi
grep -Fq 'pipeline state status is malformed' "$scratch/unknown-status-update.log" \
    || { cat "$scratch/unknown-status-update.log" >&2; echo "FAIL: unknown-status rejection was unclear" >&2; exit 1; }

# Dead pre-generation folder migrations must not move mutable paper content,
# even when a later selector error rejects the update.
no_legacy_rename_target="$scratch/no-legacy-rename-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$no_legacy_rename_target" \
    --assemble-only --no-model-probe >"$scratch/no-legacy-rename-setup.log" 2>&1
mkdir "$no_legacy_rename_target/paper/referee_reports"
printf 'operator content\n' \
    > "$no_legacy_rename_target/paper/referee_reports/operator.txt"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$no_legacy_rename_target" \
    --ext not_real --no-model-probe >"$scratch/no-legacy-rename-update.log" 2>&1; then
    echo "FAIL: updater accepted an invalid extension" >&2; exit 1
fi
[ -f "$no_legacy_rename_target/paper/referee_reports/operator.txt" ] \
    || { echo "FAIL: rejected update moved legacy-named mutable paper content" >&2; exit 1; }
[ ! -e "$no_legacy_rename_target/paper/simulated_referee_reports/operator.txt" ] \
    || { echo "FAIL: rejected update performed a dead folder migration" >&2; exit 1; }

# Manifest-owned update inputs follow extension lifecycle just like the agent
# and utility infrastructure they support.
extension_target="$scratch/extension-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$extension_target" \
    --assemble-only --no-model-probe --ext empirical \
    >"$scratch/extension-setup.log" 2>&1
extension_deps=".arpipeline/update_inputs/deps/extensions/empirical.txt"
[ -f "$extension_target/$extension_deps" ] \
    || { echo "FAIL: empirical update input was not deployed" >&2; exit 1; }
[ -f "$extension_target/code/utils/ssa_oact/period_life_table_2023.csv" ] \
    || { echo "FAIL: empirical SSA bundle was not deployed" >&2; exit 1; }
jq -e '.infrastructure.dirs_replace | index("code/utils/ssa_oact") != null' \
    "$extension_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: empirical SSA bundle lacks replacement ownership" >&2; exit 1; }
cp "$extension_target/.deploy_manifest.json" "$scratch/extension-manifest.complete"
jq '.infrastructure.files_replace -= ["code/utils/deepvest_utils.py"]' \
    "$scratch/extension-manifest.complete" > "$extension_target/.deploy_manifest.json"
extension_claude_inode="$(ls -di "$extension_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --no-model-probe >"$scratch/incomplete-ownership-update.log" 2>&1; then
    echo "FAIL: updater accepted an incomplete ownership manifest" >&2; exit 1
fi
grep -Fq 'deployment manifest infrastructure does not match' \
    "$scratch/incomplete-ownership-update.log" \
    || { cat "$scratch/incomplete-ownership-update.log" >&2; echo "FAIL: incomplete ownership rejection was unclear" >&2; exit 1; }
[ -f "$extension_target/code/utils/deepvest_utils.py" ] \
    || { echo "FAIL: rejected ownership update removed DeepVest infrastructure" >&2; exit 1; }
[ "$extension_claude_inode" = "$(ls -di "$extension_target/CLAUDE.md")" ] \
    || { echo "FAIL: incomplete manifest was rejected after replacement" >&2; exit 1; }
cp "$scratch/extension-manifest.complete" "$extension_target/.deploy_manifest.json"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --no-model-probe >"$scratch/extension-same-selector-update.log" 2>&1 \
    || { cat "$scratch/extension-same-selector-update.log" >&2; echo "FAIL: empirical same-selector update failed" >&2; exit 1; }
jq -e '
    .stage3a_analysis_path == null and has("stage3a_analysis_path")
    and .stage3a_result_receipt == null and has("stage3a_result_receipt")
' \
    "$extension_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: empirical same-selector update lost Stage 3a evidence pointers" >&2; exit 1; }
# Stale manifest-owned leaves are removed by lexical existence, including a
# dangling symlink and a FIFO; neither may silently become unowned.
rm "$extension_target/$extension_deps"
ln -s missing-dependency-spec "$extension_target/$extension_deps"
rm "$extension_target/code/utils/deepvest_utils.py"
mkfifo "$extension_target/code/utils/deepvest_utils.py"
extension_process_log_saved="$scratch/extension-process-log.saved"
mv "$extension_target/process_log" "$extension_process_log_saved"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --dry-run --no-model-probe >"$scratch/extension-dry-run.log" 2>&1; then
    echo "FAIL: updater accepted a deployment missing its current-generation state" >&2
    exit 1
fi
[ ! -e "$extension_target/process_log" ] \
    || { echo "FAIL: dry-run update left newly created control paths" >&2; exit 1; }
grep -Fq 'same-version update requires an existing process_log directory' \
    "$scratch/extension-dry-run.log" \
    || { cat "$scratch/extension-dry-run.log" >&2; echo "FAIL: missing-state rejection was unclear" >&2; exit 1; }
mv "$extension_process_log_saved" "$extension_target/process_log"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --clear-ext --no-model-probe >"$scratch/extension-update.log" 2>&1; then
    echo "FAIL: updater accepted an in-place extension removal" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' "$scratch/extension-update.log" \
    || { cat "$scratch/extension-update.log" >&2; echo "FAIL: selector-change refusal was unclear" >&2; exit 1; }
jq -e '.extensions == ["empirical"]' "$extension_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: rejected extension removal changed the manifest" >&2; exit 1; }
[ ! -e "$extension_target/process_log/.opencode-control/update-in-progress" ] \
    || { echo "FAIL: rejected selector change created a launch barrier" >&2; exit 1; }

# A selector mismatch must fail before the updater can execute or mutate an
# agent-writable existing venv.
mkdir -p "$extension_target/.venv/lib/python3.12/site-packages"
mkdir -p "$extension_target/.venv/bin"
venv_interpreter_marker="$scratch/project-venv-interpreter-ran"
printf '%s\n' '#!/bin/bash' \
    ': > "${VENV_INTERPRETER_MARKER:?}"' \
    'exec /usr/bin/python3 "$@"' \
    > "$extension_target/.venv/bin/python3"
chmod +x "$extension_target/.venv/bin/python3"
if env PATH=/usr/bin:/bin VENV_INTERPRETER_MARKER="$venv_interpreter_marker" \
    "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --dry-run --clear-ext --no-model-probe \
    >"$scratch/extension-add-dry-run.log" 2>&1; then
    echo "FAIL: selector-change dry-run accepted an existing venv" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' \
    "$scratch/extension-add-dry-run.log" \
    || { cat "$scratch/extension-add-dry-run.log" >&2; echo "FAIL: selector-change rejection was unclear" >&2; exit 1; }
if env PATH=/usr/bin:/bin VENV_INTERPRETER_MARKER="$venv_interpreter_marker" \
    "$repo_root/test_scripts/update_with_manifest_selectors.py" "$extension_target" \
    --clear-ext --no-model-probe \
    >"$scratch/extension-add-update.log" 2>&1; then
    echo "FAIL: selector change committed beside an existing venv" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' \
    "$scratch/extension-add-update.log" \
    || { cat "$scratch/extension-add-update.log" >&2; echo "FAIL: selector-change failure was unclear" >&2; exit 1; }
jq -e '.extensions == ["empirical"]' "$extension_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: rejected selector change committed the selector" >&2; exit 1; }
[ ! -e "$extension_target/process_log/.opencode-control/update-in-progress" ] \
    || { echo "FAIL: rejected extension addition created a launch barrier" >&2; exit 1; }
[ ! -e "$venv_interpreter_marker" ] \
    || { echo "FAIL: updater executed the project-owned venv interpreter" >&2; exit 1; }

# Current-generation projects must retain the complete receipt-backed state
# schema; unsupported pre-receipt or recovery fields fail before replacement.
completed_target="$scratch/completed-evidence-migration-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$completed_target" \
    --assemble-only --no-model-probe >"$scratch/completed-evidence-setup.log" 2>&1
rm -r "$completed_target/output/evidence"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --dry-run --no-model-probe >"$scratch/completed-evidence-dry-run.log" 2>&1; then
    echo "FAIL: same-version update recreated missing evidence state" >&2; exit 1
fi
[ ! -e "$completed_target/output/evidence" ] \
    || { echo "FAIL: evidence-skeleton dry-run created output/evidence" >&2; exit 1; }
grep -Fq 'update requires output/evidence from the same template version' \
    "$scratch/completed-evidence-dry-run.log" \
    || { echo "FAIL: missing evidence-state rejection was unclear" >&2; exit 1; }
mkdir "$completed_target/output/evidence"
python3 - "$completed_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as handle:
    state = json.load(handle)
state.pop("stage2b_result_receipt", None)
with open(path, "w") as handle:
    json.dump(state, handle, indent=2)
    handle.write("\n")
PY
legacy_preflight_inode="$(ls -di "$completed_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --no-model-probe >"$scratch/unsupported-legacy-evidence.log" 2>&1; then
    echo "FAIL: updater reconstructed a pre-receipt evidence schema" >&2; exit 1
fi
grep -Fq 'missing required receipt-backed evidence fields' \
    "$scratch/unsupported-legacy-evidence.log" \
    || { cat "$scratch/unsupported-legacy-evidence.log" >&2; echo "FAIL: unsupported legacy-evidence error was unclear" >&2; exit 1; }
[ "$(ls -di "$completed_target/CLAUDE.md")" = "$legacy_preflight_inode" ] \
    || { echo "FAIL: unsupported legacy evidence mutated infrastructure before rejection" >&2; exit 1; }
python3 - "$completed_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as handle:
    state = json.load(handle)
state["stage2b_result_receipt"] = None
state["stage2b_legacy_recovery_inputs"] = ["output/stage2b/exploration.md"]
with open(path, "w") as handle:
    json.dump(state, handle, indent=2)
    handle.write("\n")
PY
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --no-model-probe >"$scratch/unsupported-recovery-array.log" 2>&1; then
    echo "FAIL: updater retained a legacy evidence-recovery array" >&2; exit 1
fi
grep -Fq 'legacy computed-evidence recovery fields are unsupported' \
    "$scratch/unsupported-recovery-array.log" \
    || { cat "$scratch/unsupported-recovery-array.log" >&2; echo "FAIL: legacy recovery-array error was unclear" >&2; exit 1; }
python3 - "$completed_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
with open(path) as handle:
    state = json.load(handle)
state.pop("stage2b_legacy_recovery_inputs", None)
with open(path, "w") as handle:
    json.dump(state, handle, indent=2)
    handle.write("\n")
PY
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --no-model-probe >"$scratch/completed-state-recovery.log" 2>&1 \
    || { cat "$scratch/completed-state-recovery.log" >&2; echo "FAIL: corrected state did not clear interrupted update" >&2; exit 1; }
invalid_paper_target="$scratch/invalid-paper-receipt-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$invalid_paper_target" \
    --assemble-only --no-model-probe >"$scratch/invalid-paper-setup.log" 2>&1
python3 - "$invalid_paper_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
value = json.load(open(path))
value["status"] = "complete"
value["current_stage"] = "stage_10"
with open(path, "w") as handle:
    json.dump(value, handle)
    handle.write("\n")
PY
printf '%s\n' '{"kind":"paper_evidence","receipt_version":2}' \
    > "$invalid_paper_target/process_log/paper_evidence.receipt.json"
printf '%s\n' '{"crash_left":"partial state"}' \
    > "$invalid_paper_target/process_log/.pipeline-state.reaudit.next"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$invalid_paper_target" \
    --no-model-probe >"$scratch/invalid-paper-update.log" 2>&1 \
    || { cat "$scratch/invalid-paper-update.log" >&2; echo "FAIL: same-version refresh failed" >&2; exit 1; }
jq -e '
    .status == "running" and .current_stage == "stage_9"
    and (.history[-1].event | contains("reopened Stage 9"))
' \
    "$invalid_paper_target/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: updater did not reopen stale completed paper evidence" >&2; exit 1; }
[ ! -e "$invalid_paper_target/process_log/.pipeline-state.reaudit.next" ] \
    || { echo "FAIL: updater retained crash-left Stage-9 state staging" >&2; exit 1; }

# Paper-receipt inspection during update uses the trusted fresh utility in an
# explicitly lock-free/read-only mode. Neither a modified project utility nor
# transaction recovery may run, including under --dry-run.
dry_paper_target="$scratch/dry-paper-receipt-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$dry_paper_target" \
    --assemble-only --no-model-probe >"$scratch/dry-paper-setup.log" 2>&1
python3 - "$dry_paper_target/process_log/pipeline_state.json" <<'PY'
import json, sys
path = sys.argv[1]
value = json.load(open(path))
value["status"] = "complete"
value["current_stage"] = "stage_10"
with open(path, "w") as handle:
    json.dump(value, handle)
    handle.write("\n")
PY
printf '%s\n' '{"kind":"paper_evidence","receipt_version":2}' \
    > "$dry_paper_target/process_log/paper_evidence.receipt.json"
dry_project_marker="$scratch/project-results-utility-ran"
python3 - "$dry_paper_target/code/utils/results_pipeline/results_pipeline.py" \
    "$dry_project_marker" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
marker = sys.argv[2]
text = path.read_text()
needle = "from __future__ import annotations\n"
payload = f"__import__('pathlib').Path({marker!r}).write_text('ran')\n"
path.write_text(text.replace(needle, needle + payload, 1))
PY
rm -f "$dry_paper_target/process_log/results_pipeline.lock"
printf '%s\n' '{"phase":"prepared","sentinel":"must-remain"}' \
    > "$dry_paper_target/process_log/.results_pipeline-transaction.json"
cp "$dry_paper_target/process_log/pipeline_state.json" "$scratch/dry-paper-state.before"
cp "$dry_paper_target/.deploy_manifest.json" "$scratch/dry-paper-manifest.before"
dry_process_log_metadata="$(python3 - "$dry_paper_target/process_log" <<'PY'
import os, sys
value = os.stat(sys.argv[1])
print(f"{value.st_mtime_ns}:{value.st_ctime_ns}")
PY
)"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$dry_paper_target" \
    --dry-run --no-model-probe >"$scratch/dry-paper-update.log" 2>&1 \
    || { cat "$scratch/dry-paper-update.log" >&2; echo "FAIL: paper-receipt dry-run failed" >&2; exit 1; }
[ ! -e "$dry_project_marker" ] \
    || { echo "FAIL: updater executed the project's results utility" >&2; exit 1; }
[ ! -e "$dry_paper_target/process_log/results_pipeline.lock" ] \
    || { echo "FAIL: paper-receipt dry-run created a results lock" >&2; exit 1; }
grep -Fq 'must-remain' "$dry_paper_target/process_log/.results_pipeline-transaction.json" \
    || { echo "FAIL: paper-receipt dry-run recovered a live transaction" >&2; exit 1; }
cmp -s "$scratch/dry-paper-state.before" "$dry_paper_target/process_log/pipeline_state.json" \
    || { echo "FAIL: paper-receipt dry-run changed pipeline state" >&2; exit 1; }
cmp -s "$scratch/dry-paper-manifest.before" "$dry_paper_target/.deploy_manifest.json" \
    || { echo "FAIL: paper-receipt dry-run changed the manifest" >&2; exit 1; }
dry_process_log_metadata_after="$(python3 - "$dry_paper_target/process_log" <<'PY'
import os, sys
value = os.stat(sys.argv[1])
print(f"{value.st_mtime_ns}:{value.st_ctime_ns}")
PY
)"
[ "$dry_process_log_metadata" = "$dry_process_log_metadata_after" ] \
    || { echo "FAIL: dry-run changed process_log directory metadata" >&2; exit 1; }

# Same-version update never reconstructs a missing mutable registry, regardless
# of whether receipt-shaped history is absent, unreadable, or malformed.
rm "$completed_target/process_log/results_registry.json"
mkdir -p "$completed_target/output/unreadable-history"
chmod 000 "$completed_target/output/unreadable-history"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --dry-run --no-model-probe >"$scratch/unreadable-receipt-scan.log" 2>&1; then
    chmod 700 "$completed_target/output/unreadable-history"
    echo "FAIL: update silently skipped an unreadable result-history subtree" >&2
    exit 1
fi
chmod 700 "$completed_target/output/unreadable-history"
grep -Fq 'update requires process_log/results_registry.json from the same template version' \
    "$scratch/unreadable-receipt-scan.log" \
    || { cat "$scratch/unreadable-receipt-scan.log" >&2; echo "FAIL: unreadable history failure was unclear" >&2; exit 1; }
[ ! -e "$completed_target/process_log/results_registry.json" ] \
    || { echo "FAIL: unreadable history scan fabricated an empty registry" >&2; exit 1; }

mkdir -p "$completed_target/output/stagex"
mkdir "$completed_target/output/stagex/directory_results.receipt.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --no-model-probe >"$scratch/missing-registry-shaped-directory.log" 2>&1; then
    echo "FAIL: update ignored a receipt-shaped directory while rebuilding the registry" >&2
    exit 1
fi
grep -Fq 'update requires process_log/results_registry.json from the same template version' \
    "$scratch/missing-registry-shaped-directory.log" \
    || { cat "$scratch/missing-registry-shaped-directory.log" >&2; echo "FAIL: receipt-shaped directory failure was unclear" >&2; exit 1; }
[ ! -e "$completed_target/process_log/results_registry.json" ] \
    || { echo "FAIL: receipt-shaped directory caused an empty registry bootstrap" >&2; exit 1; }
rmdir "$completed_target/output/stagex/directory_results.receipt.json"
printf '%s\n' '{"kind":"result"}' > \
    "$completed_target/output/stagex/legacy_results.receipt.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$completed_target" \
    --no-model-probe >"$scratch/missing-registry-history.log" 2>&1; then
    echo "FAIL: update reconstructed registry over existing receipt history" >&2
    exit 1
fi
grep -Fq 'update requires process_log/results_registry.json from the same template version' \
    "$scratch/missing-registry-history.log" \
    || { cat "$scratch/missing-registry-history.log" >&2; echo "FAIL: missing-registry history failure was unclear" >&2; exit 1; }
[ ! -e "$completed_target/process_log/results_registry.json" ] \
    || { echo "FAIL: failed history migration fabricated an empty registry" >&2; exit 1; }

# Downstream updater checks use an undeformed current-generation empirical
# deployment. Historical state-shape migrations are intentionally unsupported.
schema_target="$scratch/current-schema-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$schema_target" \
    --assemble-only --no-model-probe --ext empirical \
    >"$scratch/schema-setup.log" 2>&1
cp "$schema_target/process_log/pipeline_state.json" "$scratch/schema-state.valid"
jq '.stage3a_theory_version = "bad"
    | .stage3a_analysis_path = []
    | .stage3a_result_receipt = 42' \
    "$scratch/schema-state.valid" > "$schema_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/malformed-result-pointer-types.log" 2>&1; then
    echo "FAIL: updater accepted malformed stage-result pointer types" >&2; exit 1
fi
grep -Fq 'stage3a_theory_version must be a positive integer or null' \
    "$scratch/malformed-result-pointer-types.log" \
    || { cat "$scratch/malformed-result-pointer-types.log" >&2; echo "FAIL: malformed pointer-type rejection was unclear" >&2; exit 1; }
jq '.stage3a_theory_version = 1
    | .stage3a_analysis_path = "output/stage3a/analysis.md"
    | .stage3a_result_receipt = "output/stage3a/results.receipt.json"' \
    "$scratch/schema-state.valid" > "$schema_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/inactive-result-pointer.log" 2>&1; then
    echo "FAIL: updater accepted a non-active stage receipt pointer" >&2; exit 1
fi
grep -Fq 'stage3a_result_receipt must name an active result receipt' \
    "$scratch/inactive-result-pointer.log" \
    || { cat "$scratch/inactive-result-pointer.log" >&2; echo "FAIL: inactive receipt-pointer rejection was unclear" >&2; exit 1; }
jq '.stage3a_theory_version = null
    | .stage3a_analysis_path = "output/stage3a/analysis.md"
    | .stage3a_result_receipt = "output/stage3a/results.receipt.json"' \
    "$scratch/schema-state.valid" > "$schema_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/pending-version-reset-pointer.log" 2>&1; then
    echo "FAIL: updater accepted an inactive retained receipt" >&2; exit 1
fi
grep -Fq 'stage3a_result_receipt must name an active result receipt' \
    "$scratch/pending-version-reset-pointer.log" \
    || { cat "$scratch/pending-version-reset-pointer.log" >&2; echo "FAIL: null acceptance version did not preserve the report/receipt pair" >&2; exit 1; }
cp "$scratch/schema-state.valid" "$schema_target/process_log/pipeline_state.json"
cp "$schema_target/process_log/results_registry.json" "$scratch/valid-results-registry.json"
jq '.active = ["output/../bad_results.receipt.json"]' \
    "$scratch/valid-results-registry.json" > "$schema_target/process_log/results_registry.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/malformed-results-registry.log" 2>&1; then
    echo "FAIL: updater accepted a result registry the runtime rejects" >&2
    exit 1
fi
grep -Fq 'result receipt paths must be normalized' "$scratch/malformed-results-registry.log" \
    || { cat "$scratch/malformed-results-registry.log" >&2; echo "FAIL: malformed registry failure was unclear" >&2; exit 1; }
jq '.active = [{}]' "$scratch/valid-results-registry.json" \
    > "$schema_target/process_log/results_registry.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/unhashable-results-registry.log" 2>&1; then
    echo "FAIL: updater accepted an object-valued active receipt" >&2; exit 1
fi
grep -Fq 'results registry has malformed active entries' \
    "$scratch/unhashable-results-registry.log" \
    || { cat "$scratch/unhashable-results-registry.log" >&2; echo "FAIL: object-valued registry failure was unclear" >&2; exit 1; }
if grep -Fq 'Traceback' "$scratch/unhashable-results-registry.log"; then
    cat "$scratch/unhashable-results-registry.log" >&2
    echo "FAIL: malformed registry escaped as a traceback" >&2; exit 1
fi
cp "$scratch/valid-results-registry.json" "$schema_target/process_log/results_registry.json"
python3 - "$schema_target/process_log/results_registry.json" <<'PY'
import pathlib, sys
path = pathlib.Path(sys.argv[1])
text = path.read_text()
path.write_text(text.replace('"active": []', '"active": [], "active": []', 1))
PY
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/duplicate-results-registry.log" 2>&1; then
    echo "FAIL: updater accepted duplicate JSON object keys" >&2; exit 1
fi
grep -Fq 'duplicate JSON object key' "$scratch/duplicate-results-registry.log" \
    || { cat "$scratch/duplicate-results-registry.log" >&2; echo "FAIL: duplicate JSON rejection was unclear" >&2; exit 1; }
cp "$scratch/valid-results-registry.json" "$schema_target/process_log/results_registry.json"
jq '.archived_best_scores = {"r1": 4.2, "r2": 4.5}' \
    "$scratch/schema-state.valid" > "$schema_target/process_log/pipeline_state.json"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --dry-run --no-model-probe >"$scratch/archived-score-map.log" 2>&1 \
    || { cat "$scratch/archived-score-map.log" >&2; echo "FAIL: updater rejected valid later-round archived scores" >&2; exit 1; }
cp "$scratch/schema-state.valid" "$schema_target/process_log/pipeline_state.json"
jq -e '.extensions == ["empirical"]' "$schema_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: empirical selector was not persisted" >&2; exit 1; }

# Even selector-absent stage pointers are untrusted mutable state: normalize
# every populated pair before opening either path, and validate every retired
# receipt fingerprint rather than only the three active state pointers.
pointer_escape_target="$scratch/pointer-escape-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$pointer_escape_target" \
    --assemble-only --no-model-probe >"$scratch/pointer-escape-setup.log" 2>&1
cp "$pointer_escape_target/process_log/pipeline_state.json" \
    "$scratch/pointer-escape-state.valid"
jq '.stage3a_analysis_path = "/etc/passwd"
    | .stage3a_result_receipt = "output/stage3a/results.receipt.json"' \
    "$scratch/pointer-escape-state.valid" \
    > "$pointer_escape_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$pointer_escape_target" \
    --dry-run --no-model-probe >"$scratch/pointer-escape-update.log" 2>&1; then
    echo "FAIL: updater accepted a report pointer outside the project" >&2; exit 1
fi
grep -Fq 'result report paths must be normalized output Markdown files' \
    "$scratch/pointer-escape-update.log" \
    || { cat "$scratch/pointer-escape-update.log" >&2; echo "FAIL: escaped report rejection was unclear" >&2; exit 1; }
cp "$scratch/pointer-escape-state.valid" \
    "$pointer_escape_target/process_log/pipeline_state.json"
jq '.retired = [{
      "receipt":"output/stagex/missing_results.receipt.json",
      "reason":"withdrawn",
      "last_fingerprint":{
        "path":"output/stagex/missing_results.receipt.json",
        "kind":"file",
        "sha256":"sha256:0000000000000000000000000000000000000000000000000000000000000000"
      }
    }]' "$pointer_escape_target/process_log/results_registry.json" \
    > "$scratch/registry-with-missing-retired.json"
mv "$scratch/registry-with-missing-retired.json" \
    "$pointer_escape_target/process_log/results_registry.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$pointer_escape_target" \
    --dry-run --no-model-probe >"$scratch/missing-retired-update.log" 2>&1; then
    echo "FAIL: updater accepted a missing retired receipt" >&2; exit 1
fi
grep -Fq 'cannot safely read retired receipt' "$scratch/missing-retired-update.log" \
    || { cat "$scratch/missing-retired-update.log" >&2; echo "FAIL: missing retired receipt rejection was unclear" >&2; exit 1; }

# Current-generation state preflight traverses deployment directories by
# no-follow descriptors; a mutable parent symlink must fail before inspection.
stage0_symlink_target="$scratch/stage0-symlink-project"
stage0_symlink_outside="$scratch/stage0-symlink-outside"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$stage0_symlink_target" \
    --assemble-only --no-model-probe >"$scratch/stage0-symlink-setup.log" 2>&1
mkdir "$stage0_symlink_outside"
mv "$stage0_symlink_target/output/stage0" "$stage0_symlink_target/output/stage0-real"
ln -s "$stage0_symlink_outside" "$stage0_symlink_target/output/stage0"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$stage0_symlink_target" \
    --no-model-probe >"$scratch/stage0-symlink-update.log" 2>&1; then
    echo "FAIL: updater followed a symlinked output/stage0 migration parent" >&2; exit 1
fi
grep -Fq 'output/stage0 must be a real directory' \
    "$scratch/stage0-symlink-update.log" \
    || { cat "$scratch/stage0-symlink-update.log" >&2; echo "FAIL: Stage-0 symlink rejection was unclear" >&2; exit 1; }
[ -z "$(find "$stage0_symlink_outside" -mindepth 1 -print -quit)" ] \
    || { echo "FAIL: updater touched the outside Stage-0 symlink target" >&2; exit 1; }

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
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$schema_target" \
    --clear-ext --no-model-probe >"$scratch/schema-started-update.log" 2>&1; then
    echo "FAIL: started project accepted an extension-route migration" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' \
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
variant_source_digest="$(jq -r '.source.content_digest' "$variant_target/.deploy_manifest.json")"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$variant_target" --dry-run \
    >"$scratch/missing-selector-update.log" 2>&1; then
    echo "FAIL: update accepted implicit project-writable selectors" >&2; exit 1
fi
grep -Fq 'requires each deployment selector exactly once' \
    "$scratch/missing-selector-update.log" \
    || { cat "$scratch/missing-selector-update.log" >&2; echo "FAIL: missing-selector refusal was unclear" >&2; exit 1; }
[ ! -e "$variant_target/process_log/.opencode-control" ] \
    || { echo "FAIL: missing-selector refusal created target control state" >&2; exit 1; }

# A project agent cannot authorize a cross-variant rewrite by forging the
# manifest selector; the independent operator-supplied selector wins.
forged_variant_target="$scratch/forged-variant-project"
cp -R "$variant_target" "$forged_variant_target"
jq '.variant = "macro"' "$forged_variant_target/.deploy_manifest.json" \
    > "$scratch/forged-variant-manifest.json"
mv "$scratch/forged-variant-manifest.json" "$forged_variant_target/.deploy_manifest.json"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$forged_variant_target" \
    --source-digest "$variant_source_digest" "${finance_selectors[@]}" \
    --dry-run --no-model-probe \
    >"$scratch/forged-variant-update.log" 2>&1; then
    echo "FAIL: updater trusted a forged manifest selector" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' \
    "$scratch/forged-variant-update.log" \
    || { cat "$scratch/forged-variant-update.log" >&2; echo "FAIL: forged-selector refusal was unclear" >&2; exit 1; }
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$variant_target" \
    --variant llm_cognition --no-model-probe >"$scratch/variant-update.log" 2>&1; then
    echo "FAIL: cross-variant update unexpectedly succeeded" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' "$scratch/variant-update.log" \
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
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$faithful_target" \
    --no-model-probe >"$scratch/faithful-update.log" 2>&1 \
    || { cat "$scratch/faithful-update.log" >&2; echo "FAIL: faithful update failed" >&2; exit 1; }
jq -e '.flags.seeded == true and .flags.faithful == true' \
    "$faithful_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: faithful update degraded persisted selector state" >&2; exit 1; }
[ -f "$faithful_target/.claude/agents/faithful-drift-auditor.md" ] \
    || { echo "FAIL: faithful update pruned its drift auditor" >&2; exit 1; }

# No selector can change in place, even before first launch. The refusal happens
# before managed mutation and leaves project-owned state/bootstrap bytes absent.
seed_validation_target="$scratch/seed-validation-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$seed_validation_target" \
    --assemble-only --no-model-probe >"$scratch/seed-validation-setup.log" 2>&1
cp "$seed_validation_target/.deploy_manifest.json" "$scratch/seed-validation-manifest.before"
cp "$seed_validation_target/process_log/pipeline_state.json" "$scratch/seed-validation-state.before"
seed_validation_claude_inode="$(ls -di "$seed_validation_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$seed_validation_target" \
    --seeded --no-model-probe >"$scratch/seed-validation-update.log" 2>&1; then
    echo "FAIL: updater accepted an in-place seed selector change" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' "$scratch/seed-validation-update.log" \
    || { cat "$scratch/seed-validation-update.log" >&2; echo "FAIL: seed selector refusal was unclear" >&2; exit 1; }
cmp -s "$scratch/seed-validation-manifest.before" "$seed_validation_target/.deploy_manifest.json" \
    || { echo "FAIL: rejected seed selector changed the manifest" >&2; exit 1; }
cmp -s "$scratch/seed-validation-state.before" "$seed_validation_target/process_log/pipeline_state.json" \
    || { echo "FAIL: rejected seed selector changed pipeline state" >&2; exit 1; }
[ "$seed_validation_claude_inode" = "$(ls -di "$seed_validation_target/CLAUDE.md")" ] \
    || { echo "FAIL: rejected seed selector replaced infrastructure" >&2; exit 1; }
[ ! -e "$seed_validation_target/output/seed" ] \
    || { echo "FAIL: rejected seed selector created bootstrap content" >&2; exit 1; }

# Runtime counters may advance, but source-defined loop caps and selector
# booleans and the initial journal tier are immutable state invariants. Project
# edits cannot raise the runaway ceiling or rewrite the deployment's starting
# journal target.
state_invariant_target="$scratch/state-invariant-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$state_invariant_target" \
    --assemble-only --no-model-probe >"$scratch/state-invariant-setup.log" 2>&1
jq '.loops.stage0_discovery.cap = 999999 | .seeded = true | .initial_journal_tier = "forged-tier"' \
    "$state_invariant_target/process_log/pipeline_state.json" \
    > "$scratch/state-invariant.next"
mv "$scratch/state-invariant.next" \
    "$state_invariant_target/process_log/pipeline_state.json"
state_invariant_claude_inode="$(ls -di "$state_invariant_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$state_invariant_target" --no-model-probe \
    >"$scratch/state-invariant-update.log" 2>&1; then
    echo "FAIL: updater accepted forged state caps/selectors" >&2; exit 1
fi
grep -Eq 'loop stage0_discovery is malformed|field seeded does not match its immutable setup value|field initial_journal_tier does not match its immutable setup value' \
    "$scratch/state-invariant-update.log" \
    || { cat "$scratch/state-invariant-update.log" >&2; echo "FAIL: state-invariant rejection was unclear" >&2; exit 1; }
[ "$state_invariant_claude_inode" = "$(ls -di "$state_invariant_target/CLAUDE.md")" ] \
    || { echo "FAIL: state-invariant rejection replaced infrastructure" >&2; exit 1; }

initial_tier_target="$scratch/initial-tier-invariant-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$initial_tier_target" \
    --assemble-only --no-model-probe >"$scratch/initial-tier-setup.log" 2>&1
jq '.initial_journal_tier = "forged-tier"' \
    "$initial_tier_target/process_log/pipeline_state.json" \
    > "$scratch/initial-tier.next"
mv "$scratch/initial-tier.next" \
    "$initial_tier_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$initial_tier_target" --dry-run --no-model-probe \
    >"$scratch/initial-tier-update.log" 2>&1; then
    echo "FAIL: updater accepted a rewritten initial journal tier" >&2; exit 1
fi
grep -Fq 'field initial_journal_tier does not match its immutable setup value' \
    "$scratch/initial-tier-update.log" \
    || { cat "$scratch/initial-tier-update.log" >&2; echo "FAIL: initial-tier rejection was unclear" >&2; exit 1; }

target_tier_target="$scratch/target-tier-invariant-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$target_tier_target" \
    --assemble-only --no-model-probe >"$scratch/target-tier-setup.log" 2>&1
jq '.target_journal_tier = "not-a-tier"' \
    "$target_tier_target/process_log/pipeline_state.json" \
    > "$scratch/target-tier.next"
mv "$scratch/target-tier.next" \
    "$target_tier_target/process_log/pipeline_state.json"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$target_tier_target" --dry-run --no-model-probe \
    >"$scratch/target-tier-update.log" 2>&1; then
    echo "FAIL: updater accepted a journal tier outside the variant ladder" >&2; exit 1
fi
grep -Fq 'target_journal_tier is outside the variant ladder' \
    "$scratch/target-tier-update.log" \
    || { cat "$scratch/target-tier-update.log" >&2; echo "FAIL: target-tier rejection was unclear" >&2; exit 1; }

# A valid ladder value is still impossible when it sits above this
# deployment's immutable starting tier. This relation differs by variant and
# must not be mistaken for old-state compatibility.
for tier_case in finance llm_cognition; do
    above_initial_target="$scratch/above-initial-$tier_case-project"
    case "$tier_case" in
        finance) above_initial_tier="top-5" ;;
        llm_cognition) above_initial_tier="nature" ;;
    esac
    env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$above_initial_target" \
        --variant "$tier_case" --assemble-only --no-model-probe \
        >"$scratch/above-initial-$tier_case-setup.log" 2>&1
    jq --arg tier "$above_initial_tier" '.target_journal_tier = $tier' \
        "$above_initial_target/process_log/pipeline_state.json" \
        > "$scratch/above-initial-$tier_case.next"
    mv "$scratch/above-initial-$tier_case.next" \
        "$above_initial_target/process_log/pipeline_state.json"
    if env PATH=/usr/bin:/bin \
        "$repo_root/test_scripts/update_with_manifest_selectors.py" \
        "$above_initial_target" --dry-run --no-model-probe \
        >"$scratch/above-initial-$tier_case-update.log" 2>&1; then
        echo "FAIL: updater accepted $tier_case target above its initial tier" >&2
        exit 1
    fi
    grep -Fq 'target_journal_tier is above its immutable initial tier' \
        "$scratch/above-initial-$tier_case-update.log" \
        || { cat "$scratch/above-initial-$tier_case-update.log" >&2; \
             echo "FAIL: $tier_case above-initial-tier rejection was unclear" >&2; exit 1; }
done

hostile_routing_target="$scratch/hostile-routing-state-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$hostile_routing_target" \
    --assemble-only --no-model-probe >"$scratch/hostile-routing-setup.log" 2>&1
jq '.stage0_discovery_phase = "invented" | .stage0_discovery_step = "invented" | .theory_attempt = -7 | .theory_version = -7 | .regeneration_round = -7' \
    "$hostile_routing_target/process_log/pipeline_state.json" \
    > "$scratch/hostile-routing.next"
mv "$scratch/hostile-routing.next" \
    "$hostile_routing_target/process_log/pipeline_state.json"
printf '\nROUTING_PREFLIGHT_SENTINEL\n' >> "$hostile_routing_target/CLAUDE.md"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$hostile_routing_target" --no-model-probe \
    >"$scratch/hostile-routing-update.log" 2>&1; then
    echo "FAIL: updater accepted impossible routing/counter state" >&2; exit 1
fi
grep -Eq 'stage0_discovery_phase|stage0_discovery_step|theory_attempt|theory_version|regeneration_round' \
    "$scratch/hostile-routing-update.log" \
    || { cat "$scratch/hostile-routing-update.log" >&2; echo "FAIL: routing-state rejection was unclear" >&2; exit 1; }
grep -Fq 'ROUTING_PREFLIGHT_SENTINEL' "$hostile_routing_target/CLAUDE.md" \
    || { echo "FAIL: routing state was rejected after infrastructure replacement" >&2; exit 1; }
[ ! -e "$hostile_routing_target/process_log/.opencode-control/update-in-progress" ] \
    || { echo "FAIL: routing-state preflight created a launch barrier" >&2; exit 1; }

strict_selector_digest="$(jq -r '.source.content_digest' "$initial_tier_target/.deploy_manifest.json")"
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$initial_tier_target" \
    --source-digest "$strict_selector_digest" --variant finance --mode= \
    --clear-ext --no-seeded --no-faithful --no-manual --no-light \
    --no-halt-on-core-bypass --dry-run --no-model-probe \
    >"$scratch/empty-mode-selector.log" 2>&1; then
    echo "FAIL: updater accepted empty --mode= as --no-mode" >&2; exit 1
fi
grep -Fq 'empty --mode is unsupported; use explicit --no-mode' \
    "$scratch/empty-mode-selector.log" \
    || { cat "$scratch/empty-mode-selector.log" >&2; echo "FAIL: empty mode rejection was unclear" >&2; exit 1; }

if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$initial_tier_target" \
    --source-digest "$strict_selector_digest" "${finance_selectors[@]}" \
    --ext '' --dry-run --no-model-probe \
    >"$scratch/empty-extension-selector.log" 2>&1; then
    echo "FAIL: updater accepted the obsolete empty --ext selector" >&2; exit 1
fi
grep -Fq 'empty, unknown, or duplicate' "$scratch/empty-extension-selector.log" \
    || { cat "$scratch/empty-extension-selector.log" >&2; echo "FAIL: empty extension rejection was unclear" >&2; exit 1; }

if "$repo_root/update.sh" "$initial_tier_target" \
    --source-digest "$strict_selector_digest" --variant finance --no-mode \
    --ext empirical --clear-ext --no-seeded --no-faithful --no-manual \
    --no-light --no-halt-on-core-bypass --dry-run --no-model-probe \
    >"$scratch/lossy-extension-selector.log" 2>&1; then
    echo "FAIL: updater accepted lossy --ext then --clear-ext ordering" >&2; exit 1
fi
grep -Fq -- '--clear-ext must precede every --ext selector' "$scratch/lossy-extension-selector.log" \
    || { cat "$scratch/lossy-extension-selector.log" >&2; echo "FAIL: lossy extension ordering rejection was unclear" >&2; exit 1; }
if env PATH=/usr/bin:/bin "$repo_root/update.sh" "$initial_tier_target" \
    --source-digest "$strict_selector_digest" "${finance_selectors[@]}" \
    --seeded --dry-run --no-model-probe \
    >"$scratch/duplicate-selector.log" 2>&1; then
    echo "FAIL: updater accepted conflicting duplicate selectors" >&2; exit 1
fi
grep -Fq 'each deployment selector exactly once' "$scratch/duplicate-selector.log" \
    || { cat "$scratch/duplicate-selector.log" >&2; echo "FAIL: duplicate selector rejection was unclear" >&2; exit 1; }

# A crash-left host-authority workspace may contain copied credentials and
# hostile permissions. The next mutating update removes only the exact
# updater-owned namespace before constructing a replacement.
abandoned_target="$scratch/abandoned-workspace-project"
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$abandoned_target" \
    --assemble-only --no-model-probe >"$scratch/abandoned-workspace-setup.log" 2>&1
abandoned_control="$abandoned_target/process_log/.opencode-control"
mkdir -p "$abandoned_control/update.Ab12Z9/locked"
printf 'ABANDONED_SECRET=value\n' > "$abandoned_control/update.Ab12Z9/locked/.env"
chmod 000 "$abandoned_control/update.Ab12Z9/locked"
env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$abandoned_target" --no-model-probe \
    >"$scratch/abandoned-workspace-update.log" 2>&1 \
    || { chmod 700 "$abandoned_control/update.Ab12Z9/locked" 2>/dev/null || true; cat "$scratch/abandoned-workspace-update.log" >&2; echo "FAIL: abandoned workspace recovery failed" >&2; exit 1; }
[ ! -e "$abandoned_control/update.Ab12Z9" ] \
    || { echo "FAIL: abandoned credential workspace survived recovery" >&2; exit 1; }

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
    "$repo_root/test_scripts/update_with_manifest_selectors.py" "$variant_target" --no-model-probe \
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
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$manual_lock_target" \
    --no-model-probe >"$scratch/manual-lock-update.log" 2>&1; then
    kill "$runtime_lock_pid" 2>/dev/null || true
    wait "$runtime_lock_pid" 2>/dev/null || true
    echo "FAIL: locked manual project accepted an update" >&2; exit 1
fi
kill "$runtime_lock_pid" 2>/dev/null || true
wait "$runtime_lock_pid" 2>/dev/null || true
jq -e '.kind == "manual_evidence_state" and .loops.evidence == {"round":0,"cap":3}' \
    "$manual_lock_target/process_log/manual_evidence_state.json" >/dev/null \
    || { echo "FAIL: refused update altered/missed manual evidence state" >&2; exit 1; }
jq -e '.kind == "result_registry" and .active == [] and .pending == []' \
    "$manual_lock_target/process_log/results_registry.json" >/dev/null \
    || { echo "FAIL: refused update altered/missed manual results registry" >&2; exit 1; }

# Existing mutable evidence controls are preflighted before any managed file,
# environment merge, venv, or stale sweep can change the target.
cp "$manual_lock_target/process_log/manual_evidence_state.json" \
    "$scratch/manual-evidence-state.valid"
jq '.loops.evidence.cap = 0' "$scratch/manual-evidence-state.valid" \
    > "$manual_lock_target/process_log/manual_evidence_state.json"
cp "$manual_lock_target/CLAUDE.md" "$scratch/manual-claude.before"
cp "$manual_lock_target/.deploy_manifest.json" "$scratch/manual-manifest.before"
manual_claude_inode="$(ls -di "$manual_lock_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$manual_lock_target" \
    --no-model-probe >"$scratch/malformed-manual-state.log" 2>&1; then
    echo "FAIL: updater accepted malformed manual evidence state" >&2; exit 1
fi
grep -Fq 'manual_evidence_state.json is malformed' \
    "$scratch/malformed-manual-state.log" \
    || { cat "$scratch/malformed-manual-state.log" >&2; echo "FAIL: malformed manual-state failure was unclear" >&2; exit 1; }
cmp -s "$scratch/manual-claude.before" "$manual_lock_target/CLAUDE.md" \
    && [ "$manual_claude_inode" = "$(ls -di "$manual_lock_target/CLAUDE.md")" ] \
    || { echo "FAIL: malformed manual state was rejected after infrastructure mutation" >&2; exit 1; }
cmp -s "$scratch/manual-manifest.before" "$manual_lock_target/.deploy_manifest.json" \
    || { echo "FAIL: malformed manual state changed the manifest" >&2; exit 1; }
cp "$scratch/manual-evidence-state.valid" \
    "$manual_lock_target/process_log/manual_evidence_state.json"

jq '.loops.evidence.cap = 999' "$scratch/manual-evidence-state.valid" \
    > "$manual_lock_target/process_log/manual_evidence_state.json"
manual_claude_inode="$(ls -di "$manual_lock_target/CLAUDE.md")"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$manual_lock_target" --no-model-probe \
    >"$scratch/manual-cap-invariant.log" 2>&1; then
    echo "FAIL: updater accepted a forged manual evidence cap" >&2; exit 1
fi
grep -Fq 'manual evidence state invariants do not match' \
    "$scratch/manual-cap-invariant.log" \
    || { cat "$scratch/manual-cap-invariant.log" >&2; echo "FAIL: manual-cap refusal was unclear" >&2; exit 1; }
[ "$manual_claude_inode" = "$(ls -di "$manual_lock_target/CLAUDE.md")" ] \
    || { echo "FAIL: manual-cap rejection replaced infrastructure" >&2; exit 1; }
cp "$scratch/manual-evidence-state.valid" \
    "$manual_lock_target/process_log/manual_evidence_state.json"

if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$manual_lock_target" \
    --ext empirical --no-model-probe >"$scratch/manual-extension-update.log" 2>&1; then
    echo "FAIL: manual project accepted an in-place extension change" >&2; exit 1
fi
grep -Fq 'In-place selector changes are unsupported' "$scratch/manual-extension-update.log" \
    || { cat "$scratch/manual-extension-update.log" >&2; echo "FAIL: manual selector refusal was unclear" >&2; exit 1; }
jq -e '.flags.manual == true and .extensions == []' \
    "$manual_lock_target/.deploy_manifest.json" >/dev/null \
    || { echo "FAIL: rejected manual selector change altered the manifest" >&2; exit 1; }
[ ! -e "$manual_lock_target/process_log/pipeline_state.json" ] \
    || { echo "FAIL: manual extension refresh created autonomous pipeline state" >&2; exit 1; }
jq -e '.kind == "manual_evidence_state" and .loops.evidence == {"round":0,"cap":3}' \
    "$manual_lock_target/process_log/manual_evidence_state.json" >/dev/null \
    || { echo "FAIL: manual extension refresh lost its evidence state" >&2; exit 1; }
rm "$manual_lock_target/process_log/manual_evidence_state.json"
mv "$manual_lock_target/output/evidence" "$scratch/manual-evidence.saved"
printf '%s\n' 'not a directory' > "$manual_lock_target/output/evidence"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$manual_lock_target" \
    --no-model-probe >"$scratch/manual-evidence-rollback.log" 2>&1; then
    echo "FAIL: unsafe manual evidence path accepted an update" >&2; exit 1
fi
[ ! -e "$manual_lock_target/process_log/manual_evidence_state.json" ] \
    || { echo "FAIL: failed manual update left a newly bootstrapped evidence state" >&2; exit 1; }
rm "$manual_lock_target/output/evidence"
mv "$scratch/manual-evidence.saved" "$manual_lock_target/output/evidence"
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$manual_lock_target" \
    --no-model-probe >"$scratch/manual-evidence-migration.log" 2>&1; then
    echo "FAIL: updater recreated missing manual evidence state" >&2; exit 1
fi
grep -Fq 'manual update requires process_log/manual_evidence_state.json' \
    "$scratch/manual-evidence-migration.log" \
    || { cat "$scratch/manual-evidence-migration.log" >&2; echo "FAIL: missing manual-state rejection was unclear" >&2; exit 1; }
[ ! -e "$manual_lock_target/process_log/manual_evidence_state.json" ] \
    || { echo "FAIL: updater recreated missing manual evidence state" >&2; exit 1; }

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
if env PATH=/usr/bin:/bin "$repo_root/test_scripts/update_with_manifest_selectors.py" "$variant_target" \
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
