#!/usr/bin/env bash
# Regression coverage for checkout-local setup source policy (#256).
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/setup-source-policy.XXXXXX")"
cleanup_scratch() {
    chmod -R u+rwX "$scratch" 2>/dev/null || true
    rm -rf "$scratch"
}
trap cleanup_scratch EXIT
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
cp "$repo_root/test_scripts/update_with_manifest_selectors.py" \
    "$source_checkout/test_scripts/update_with_manifest_selectors.py"
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

# Setup's externally recorded command authenticates the updater launcher, which
# captures and verifies the complete build-input snapshot before any coordinator
# or setup module can execute. A later checkout edit must fail first.
attested_target="$scratch/attested-update-project"
attested_log="$scratch/attested-setup.log"
"$setup" "$attested_target" --assemble-only --no-model-probe >"$attested_log" 2>&1
attested_command="$(awk '/Trusted update attestation/{getline; sub(/^  /, ""); print; exit}' "$attested_log")"
[ -n "$attested_command" ] || fail "setup did not print an attested update command"
/bin/bash -c "$attested_command --dry-run --no-model-probe" \
    >"$scratch/attested-update-success.log" 2>&1 \
    || { cat "$scratch/attested-update-success.log" >&2; fail "attested update command did not execute"; }
# Ambient TMPDIR is untrusted. It must not redirect the updater's source
# snapshot into either the target or a recursively copied build-input tree.
env TMPDIR="$attested_target" /bin/bash -c \
    "$attested_command --dry-run --no-model-probe" \
    >"$scratch/target-tmpdir-update.log" 2>&1 \
    || { cat "$scratch/target-tmpdir-update.log" >&2; fail "updater trusted target TMPDIR"; }
env TMPDIR="$source_checkout/deploy_assets" /bin/bash -c \
    "$attested_command --dry-run --no-model-probe" \
    >"$scratch/source-tmpdir-update.log" 2>&1 \
    || { cat "$scratch/source-tmpdir-update.log" >&2; fail "updater trusted source TMPDIR"; }
[ -z "$(find "$attested_target" "$source_checkout/deploy_assets" \
    -name 'zeropaper-update-source-*' -print -quit)" ] \
    || fail "updater created its source snapshot beneath an ambient TMPDIR"
fakebin="$scratch/fake-update-path"
mkdir "$fakebin"
fake_bash_marker="$scratch/fake-bash-ran"
printf '%s\n' '#!/bin/sh' ": > '$fake_bash_marker'" 'exec /bin/bash "$@"' \
    > "$fakebin/bash"
chmod +x "$fakebin/bash"
PATH="$fakebin:/usr/bin:/bin" /bin/bash -c \
    "$attested_command --dry-run --no-model-probe" \
    >"$scratch/fixed-bash-update.log" 2>&1 \
    || { cat "$scratch/fixed-bash-update.log" >&2; fail "fixed-Bash update failed"; }
[ ! -e "$fake_bash_marker" ] || fail "updater executed caller-controlled bash"
coordinator_canary="$scratch/changed-update-coordinator-ran"
coordinator_path="$source_checkout/scripts/update_coordinator.sh"
cp "$coordinator_path" "$scratch/update-coordinator.before"
{
    printf '%s\n' '#!/bin/bash' ": > '$coordinator_canary'"
    tail -n +2 "$scratch/update-coordinator.before"
} > "$coordinator_path"
chmod +x "$coordinator_path"
if /bin/bash -c "$attested_command --no-model-probe" \
    >"$scratch/changed-update-coordinator.log" 2>&1; then
    fail "attested command executed changed updater bytes"
fi
grep -Fq 'does not match the operator-attested trusted setup digest' "$scratch/changed-update-coordinator.log" \
    || { cat "$scratch/changed-update-coordinator.log" >&2; fail "changed updater refusal was unclear"; }
[ ! -e "$coordinator_canary" ] || fail "changed update coordinator executed before attestation"
cp "$scratch/update-coordinator.before" "$coordinator_path"

# The verified updater must authenticate and pin every build input before the
# fresh-assembly setup launcher can execute. Authenticating only update.sh and
# its coordinator would still let a changed setup.sh obtain host authority.
setup_canary="$scratch/unattested-setup-ran"
setup_path="$source_checkout/setup.sh"
cp "$setup_path" "$scratch/setup.before-attested-update"
{
    head -n 1 "$scratch/setup.before-attested-update"
    printf '%s\n' "import pathlib; pathlib.Path('$setup_canary').write_text('ran\\n')"
    tail -n +2 "$scratch/setup.before-attested-update"
} > "$setup_path"
chmod +x "$setup_path"
if /bin/bash -c "$attested_command --dry-run --no-model-probe" \
    >"$scratch/changed-setup.log" 2>&1; then
    fail "attested command accepted changed setup bytes"
fi
grep -Fq 'does not match the operator-attested trusted setup digest' \
    "$scratch/changed-setup.log" \
    || { cat "$scratch/changed-setup.log" >&2; fail "changed setup refusal was unclear"; }
[ ! -e "$setup_canary" ] || fail "changed setup executed before full-source attestation"
cp "$scratch/setup.before-attested-update" "$setup_path"

# Operator .env is intentionally outside build provenance, but update must
# transport a private point-in-time copy so newly configured keys can merge.
# It remains the primary source while missing attested .env.example keys are
# appended exactly as they are during fresh setup.
printf 'SOURCE_POLICY_OPERATOR_KEY=from-updated-env\n' > "$source_checkout/.env"
/usr/bin/python3 -I - "$attested_target/.env" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
path.write_text(
    "".join(line for line in lines if not line.startswith("OPENALEX_API_KEY=")),
    encoding="utf-8",
)
PY
if grep -Fq 'OPENALEX_API_KEY=' "$attested_target/.env"; then
    fail "test setup did not remove the example-only environment key"
fi
/bin/bash -c "$attested_command --dry-run --no-model-probe" \
    >"$scratch/operator-env-dry-run.log" 2>&1 \
    || { cat "$scratch/operator-env-dry-run.log" >&2; fail "operator .env dry-run failed"; }
grep -Fq 'OPENALEX_API_KEY=' "$attested_target/.env" \
    && fail "operator .env dry-run mutated the target environment"
/bin/bash -c "$attested_command --no-model-probe" \
    >"$scratch/operator-env-update.log" 2>&1 \
    || { cat "$scratch/operator-env-update.log" >&2; fail "operator .env update failed"; }
grep -Fq 'SOURCE_POLICY_OPERATOR_KEY=from-updated-env' "$attested_target/.env" \
    || fail "same-snapshot update did not merge a new source .env key"
grep -Fq 'OPENALEX_API_KEY=' "$attested_target/.env" \
    || fail "operator .env update did not restore a missing .env.example key"

# Special-file substitutions must fail promptly rather than block while the
# project-wide update lock is held. Both the operator .env transport and the
# externally recorded launcher authentication open before their type check.
mv "$source_checkout/.env" "$scratch/operator-env.regular"
mkfifo "$source_checkout/.env"
ATTESTED_FIFO_COMMAND="$attested_command --dry-run --no-model-probe" \
    /usr/bin/python3 -I - <<'PY' >"$scratch/fifo-env-update.log" 2>&1 \
    || fail "FIFO source .env blocked or succeeded unexpectedly"
import os
import subprocess

command = os.environ["ATTESTED_FIFO_COMMAND"]
try:
    result = subprocess.run(["/bin/bash", "-c", command], timeout=3)
except subprocess.TimeoutExpired as error:
    raise SystemExit("FIFO source .env blocked the updater") from error
if result.returncode == 0:
    raise SystemExit("FIFO source .env was accepted")
PY
rm "$source_checkout/.env"
mv "$scratch/operator-env.regular" "$source_checkout/.env"

mv "$source_checkout/update.sh" "$scratch/update-launcher.regular"
mkfifo "$source_checkout/update.sh"
ATTESTED_FIFO_COMMAND="$attested_command --dry-run --no-model-probe" \
    /usr/bin/python3 -I - <<'PY' >"$scratch/fifo-launcher-update.log" 2>&1 \
    || fail "FIFO attested update launcher blocked or succeeded unexpectedly"
import os
import subprocess

command = os.environ["ATTESTED_FIFO_COMMAND"]
try:
    result = subprocess.run(["/bin/bash", "-c", command], timeout=3)
except subprocess.TimeoutExpired as error:
    raise SystemExit("FIFO update launcher blocked authentication") from error
if result.returncode == 0:
    raise SystemExit("FIFO update launcher was accepted")
PY
rm "$source_checkout/update.sh"
mv "$scratch/update-launcher.regular" "$source_checkout/update.sh"

# If a refresh child fails while leaving a descendant alive, the updater must
# not tell its detached guardian that the process group completed. Instrument
# a private same-source checkout so setup's coordinator kills its Python parent
# only during the update-time fresh assembly and leaves a sleeper behind.
guardian_checkout="$scratch/guardian-template"
git clone -q "$source_checkout" "$guardian_checkout"
/usr/bin/python3 -I - "$guardian_checkout/setup.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = '''import os
import stat
import sys
'''
injection = '''import os
import stat
import sys
import pathlib as _lock_test_pathlib
if os.environ.get("ZEROPAPER_TEST_LOCK_FD_MARKER"):
    _root = os.path.realpath(os.environ["ZEROPAPER_TEST_PROJECT_ROOT"])
    _root_info = os.stat(_root)
    _leaked = False
    for _descriptor in range(3, 256):
        try:
            _descriptor_info = os.fstat(_descriptor)
        except OSError:
            continue
        if (_descriptor_info.st_dev, _descriptor_info.st_ino) == (_root_info.st_dev, _root_info.st_ino):
            _leaked = True
            break
    _lock_test_pathlib.Path(os.environ["ZEROPAPER_TEST_LOCK_FD_MARKER"]).write_text(
        "leaked\\n" if _leaked else "clean\\n"
    )
'''
if text.count(anchor) != 1:
    raise SystemExit("setup launcher prologue changed")
path.write_text(text.replace(anchor, injection, 1))
PY
/usr/bin/python3 -I - "$guardian_checkout/deploy_assets/scripts/setup/coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = 'set -e\n'
injection = '''set -e
if [ "${ZEROPAPER_TEST_FAIL_REFRESH_CHILD:-0}" = "1" ]; then
    sleep 120 &
    printf '%s\\n' "$!" > "${ZEROPAPER_TEST_DESCENDANT_PID:?}"
    kill -KILL "$PPID"
    exit 97
fi
if [ "${ZEROPAPER_TEST_LINGER_REFRESH_CHILD:-0}" = "1" ]; then
    sleep 120 &
    printf '%s\\n' "$!" > "${ZEROPAPER_TEST_LINGER_PID:?}"
fi
'''
if text.count(anchor) != 1:
    raise SystemExit("setup coordinator prologue changed")
path.write_text(text.replace(anchor, injection, 1))
text = path.read_text()
final_anchor = '''if [ "$ASSEMBLE_ONLY" = "1" ]; then
    finalize_assemble_only_setup
    exit 0
fi
'''
final_injection = '''if [ "$ASSEMBLE_ONLY" = "1" ]; then
    finalize_assemble_only_setup
    if [ "${ZEROPAPER_TEST_PAUSE_REFRESH:-0}" = "1" ]; then
        : > "${ZEROPAPER_TEST_PAUSE_MARKER:?}"
        while [ ! -e "${ZEROPAPER_TEST_PAUSE_RELEASE:?}" ]; do sleep 0.02; done
        if [ -n "${ZEROPAPER_TEST_POST_PAUSE_MARKER:-}" ]; then
            : > "$ZEROPAPER_TEST_POST_PAUSE_MARKER"
        fi
    fi
    exit 0
fi
'''
if text.count(final_anchor) != 1:
    raise SystemExit("setup assemble-only finalizer changed")
path.write_text(text.replace(final_anchor, final_injection, 1))
PY
/usr/bin/python3 -I - "$guardian_checkout/scripts/update_coordinator.sh" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
anchor = '''fi
exec 7>&-
if wait "$_update_body_pid"; then
'''
replacement = '''fi
if [ "${ZEROPAPER_TEST_KILL_ARMING_PARENT:-0}" = "1" ]; then
    kill -KILL "$BASHPID"
fi
exec 7>&-
if wait "$_update_body_pid"; then
'''
if text.count(anchor) != 1:
    raise SystemExit("update guardian arming boundary changed")
path.write_text(text.replace(anchor, replacement, 1))
PY
/usr/bin/python3 -I - "$guardian_checkout/update.sh" \
    "$scratch/pre-status-enable" "$scratch/pre-status-snapshot-created" \
    "$scratch/pre-status-release" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
pre_status_enable = sys.argv[2]
pre_status_marker = sys.argv[3]
pre_status_release = sys.argv[4]
text = path.read_text()
owner_anchor = '''    snapshot = tempfile.mkdtemp(prefix="zeropaper-update-source-", dir=temp_root)
    os.write(status_fd, (snapshot + "\\n").encode("utf-8"))
'''
owner_replacement = '''    snapshot = tempfile.mkdtemp(prefix="zeropaper-update-source-", dir=temp_root)
    if os.path.exists({enable!r}):
        with open({marker!r}, "w", encoding="utf-8"):
            pass
        while not os.path.exists({release!r}):
            import time
            time.sleep(0.02)
    os.write(status_fd, (snapshot + "\\n").encode("utf-8"))
'''.format(
    enable=pre_status_enable,
    marker=pre_status_marker,
    release=pre_status_release,
)
if text.count(owner_anchor) != 1:
    raise SystemExit("snapshot-owner pre-status boundary changed")
text = text.replace(owner_anchor, owner_replacement, 1)
anchor = '''for protected_root in (project_candidate, live_checkout_root):
'''
replacement = '''if os.environ.get("ZEROPAPER_TEST_PAUSE_SNAPSHOT_OWNER") == "1":
    import time
    with open(os.environ["ZEROPAPER_TEST_SNAPSHOT_OWNER_MARKER"], "w", encoding="utf-8"):
        pass
    while not os.path.exists(os.environ["ZEROPAPER_TEST_SNAPSHOT_OWNER_RELEASE"]):
        time.sleep(0.02)
''' + anchor
if text.count(anchor) != 1:
    raise SystemExit("snapshot-owner startup boundary changed")
path.write_text(text.replace(anchor, replacement, 1))
PY
# Preserve a valid read-only build-input directory in the pinned snapshot.
# Cleanup must repair only its private copy rather than silently leaking it.
mkdir "$guardian_checkout/deploy_assets/readonly_cleanup_probe"
printf 'read-only snapshot cleanup probe\n' \
    > "$guardian_checkout/deploy_assets/readonly_cleanup_probe/value.txt"
chmod 0555 "$guardian_checkout/deploy_assets/readonly_cleanup_probe"
guardian_target="$scratch/guardian-project"
guardian_setup_log="$scratch/guardian-setup.log"
printf 'SOURCE_POLICY_NAMED_SECRET=must-not-enter-refresh\n' > "$guardian_checkout/.env"
"$guardian_checkout/setup.sh" "$guardian_target" --assemble-only --no-model-probe \
    >"$guardian_setup_log" 2>&1
guardian_command="$(awk '/Trusted update attestation/{getline; sub(/^  /, ""); print; exit}' "$guardian_setup_log")"
[ -n "$guardian_command" ] || fail "guardian fixture omitted update attestation"

# Kill before the cleanup owner can report its newly created snapshot path.
# Broken status-pipe publication must enter the owner's own cleanup path; the
# public launcher has not learned the path yet and cannot help.
pre_status_enable="$scratch/pre-status-enable"
pre_status_marker="$scratch/pre-status-snapshot-created"
touch "$pre_status_enable"
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/pre-status-snapshots.before"
/bin/bash -c "exec $guardian_command --dry-run --no-model-probe" \
    >"$scratch/pre-status-death.log" 2>&1 &
pre_status_pid=$!
for _ in $(seq 1 1500); do
    [ -e "$pre_status_marker" ] && break
    kill -0 "$pre_status_pid" 2>/dev/null || break
    sleep 0.02
done
[ -e "$pre_status_marker" ] \
    || { cat "$scratch/pre-status-death.log" >&2; \
         kill "$pre_status_pid" 2>/dev/null || true; \
         fail "pre-status snapshot fixture did not reach its pause"; }
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/pre-status-snapshots.during"
pre_status_snapshot="$(comm -13 "$scratch/pre-status-snapshots.before" \
    "$scratch/pre-status-snapshots.during")"
[ -n "$pre_status_snapshot" ] \
    && [ "$(printf '%s\n' "$pre_status_snapshot" | wc -l)" -eq 1 ] \
    || fail "pre-status fixture did not isolate one source snapshot"
kill -KILL "$pre_status_pid"
wait "$pre_status_pid" 2>/dev/null || true
rm -f "$pre_status_enable"
touch "$scratch/pre-status-release"
for _ in $(seq 1 1500); do
    [ ! -e "$pre_status_snapshot" ] && break
    sleep 0.02
done
[ ! -e "$pre_status_snapshot" ] \
    || fail "pre-status launcher death leaked its source snapshot"

pause_marker="$scratch/refresh-paused"
pause_release="$scratch/refresh-release"
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/normal-source-snapshots.before"
ZEROPAPER_TEST_PAUSE_REFRESH=1 \
ZEROPAPER_TEST_PAUSE_MARKER="$pause_marker" \
ZEROPAPER_TEST_PAUSE_RELEASE="$pause_release" \
/bin/bash -c "$guardian_command --dry-run --no-model-probe" \
    >"$scratch/anonymous-env-update.log" 2>&1 &
pause_update_pid=$!
for _ in $(seq 1 1500); do
    [ -e "$pause_marker" ] && break
    sleep 0.02
done
[ -e "$pause_marker" ] \
    || { kill "$pause_update_pid" 2>/dev/null || true; \
         cat "$scratch/anonymous-env-update.log" >&2; \
         fail "fresh assembly did not reach environment-residue probe"; }
if grep -R -l --include='.env' 'SOURCE_POLICY_NAMED_SECRET=must-not-enter-refresh' \
       /tmp/zeropaper-update.* 2>/dev/null | grep -q .; then
    touch "$pause_release"
    wait "$pause_update_pid" || true
    fail "operator environment was materialized in the named refresh workspace"
fi
touch "$pause_release"
wait "$pause_update_pid" \
    || { cat "$scratch/anonymous-env-update.log" >&2; fail "environment-residue probe update failed"; }
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/normal-source-snapshots.after"
cmp -s "$scratch/normal-source-snapshots.before" "$scratch/normal-source-snapshots.after" \
    || fail "successful update leaked a read-only pinned source snapshot"

# Kill the public launcher immediately after the cleanup owner creates the
# snapshot but before source copying or execution-supervisor handoff.  Because
# the owner creates the directory, there is no earlier mkdtemp-to-guardian gap.
pre_handoff_marker="$scratch/pre-handoff-snapshot-created"
pre_handoff_release="$scratch/pre-handoff-release"
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/pre-handoff-snapshots.before"
ZEROPAPER_TEST_PAUSE_SNAPSHOT_OWNER=1 \
ZEROPAPER_TEST_SNAPSHOT_OWNER_MARKER="$pre_handoff_marker" \
ZEROPAPER_TEST_SNAPSHOT_OWNER_RELEASE="$pre_handoff_release" \
/bin/bash -c "exec $guardian_command --dry-run --no-model-probe" \
    >"$scratch/pre-handoff-death.log" 2>&1 &
pre_handoff_pid=$!
for _ in $(seq 1 1500); do
    [ -e "$pre_handoff_marker" ] && break
    kill -0 "$pre_handoff_pid" 2>/dev/null || break
    sleep 0.02
done
[ -e "$pre_handoff_marker" ] \
    || { cat "$scratch/pre-handoff-death.log" >&2; \
         kill "$pre_handoff_pid" 2>/dev/null || true; \
         fail "pre-handoff snapshot fixture did not reach its pause"; }
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/pre-handoff-snapshots.during"
pre_handoff_snapshot="$(comm -13 "$scratch/pre-handoff-snapshots.before" \
    "$scratch/pre-handoff-snapshots.during")"
[ -n "$pre_handoff_snapshot" ] \
    && [ "$(printf '%s\n' "$pre_handoff_snapshot" | wc -l)" -eq 1 ] \
    || fail "pre-handoff fixture did not isolate one source snapshot"
kill -KILL "$pre_handoff_pid"
wait "$pre_handoff_pid" 2>/dev/null || true
for _ in $(seq 1 1500); do
    [ ! -e "$pre_handoff_snapshot" ] && break
    sleep 0.02
done
[ ! -e "$pre_handoff_snapshot" ] \
    || fail "pre-handoff launcher death leaked its read-only source snapshot"

# SIGKILL of the public Python launcher is observable as EOF by the trusted
# supervisor.  It must cancel the coordinator before the paused fresh setup
# can publish a later mutation, drain the project lock, and remove the pinned
# source snapshot without relying on launcher atexit/finally handlers.
launcher_pause_marker="$scratch/launcher-death-refresh-paused"
launcher_pause_release="$scratch/launcher-death-refresh-release"
launcher_post_marker="$scratch/launcher-death-post-pause"
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/source-snapshots.before"
ZEROPAPER_TEST_PAUSE_REFRESH=1 \
ZEROPAPER_TEST_PAUSE_MARKER="$launcher_pause_marker" \
ZEROPAPER_TEST_PAUSE_RELEASE="$launcher_pause_release" \
ZEROPAPER_TEST_POST_PAUSE_MARKER="$launcher_post_marker" \
/bin/bash -c "exec $guardian_command --dry-run --no-model-probe" \
    >"$scratch/public-launcher-death.log" 2>&1 &
public_launcher_pid=$!
for _ in $(seq 1 1500); do
    [ -e "$launcher_pause_marker" ] && break
    kill -0 "$public_launcher_pid" 2>/dev/null || break
    sleep 0.02
done
[ -e "$launcher_pause_marker" ] \
    || { cat "$scratch/public-launcher-death.log" >&2; \
         kill "$public_launcher_pid" 2>/dev/null || true; \
         fail "public-launcher death fixture did not reach its pause"; }
find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
    | sort > "$scratch/source-snapshots.during"
launcher_snapshot="$(comm -13 "$scratch/source-snapshots.before" "$scratch/source-snapshots.during")"
[ -n "$launcher_snapshot" ] && [ "$(printf '%s\n' "$launcher_snapshot" | wc -l)" -eq 1 ] \
    || fail "public-launcher death fixture did not isolate one pinned source snapshot"
kill -KILL "$public_launcher_pid"
wait "$public_launcher_pid" 2>/dev/null || true
for _ in $(seq 1 1500); do
    [ ! -e "$launcher_snapshot" ] && break
    sleep 0.02
done
[ ! -e "$launcher_snapshot" ] \
    || fail "public-launcher death leaked its pinned source snapshot"
[ ! -e "$launcher_post_marker" ] \
    || fail "public-launcher death allowed the paused refresh to continue"
/usr/bin/python3 -I - "$guardian_target" <<'PY'
import fcntl
import os
import sys

fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
finally:
    os.close(fd)
PY

# The execution supervisor is not itself an irreplaceable cleanup owner.
# After handoff, kill only that child while the coordinator is paused. The
# independent snapshot owner must wait for the coordinator/guardian lock to
# drain and remove the pinned source tree even though the public launcher lives.
if [ -r "/proc/$$/task/$$/children" ]; then
    supervisor_pause_marker="$scratch/supervisor-death-refresh-paused"
    supervisor_pause_release="$scratch/supervisor-death-refresh-release"
    find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
        | sort > "$scratch/supervisor-snapshots.before"
    ZEROPAPER_TEST_PAUSE_REFRESH=1 \
    ZEROPAPER_TEST_PAUSE_MARKER="$supervisor_pause_marker" \
    ZEROPAPER_TEST_PAUSE_RELEASE="$supervisor_pause_release" \
    /bin/bash -c "exec $guardian_command --dry-run --no-model-probe" \
        >"$scratch/supervisor-death.log" 2>&1 &
    supervisor_launcher_pid=$!
    supervisor_pid=""
    for _ in $(seq 1 1500); do
        if [ -e "$supervisor_pause_marker" ]; then
            supervisor_pid="$(/usr/bin/python3 -I - "$supervisor_launcher_pid" <<'PY'
from pathlib import Path
import sys

parent = sys.argv[1]
children_path = Path(f"/proc/{parent}/task/{parent}/children")
try:
    children = children_path.read_text(encoding="ascii").split()
except OSError:
    children = []
for child in children:
    try:
        command = Path(f"/proc/{child}/cmdline").read_bytes()
    except OSError:
        continue
    if b"def stop_child():" in command:
        print(child)
        break
PY
)"
            [ -n "$supervisor_pid" ] && break
        fi
        kill -0 "$supervisor_launcher_pid" 2>/dev/null || break
        sleep 0.02
    done
    [ -n "$supervisor_pid" ] \
        || { cat "$scratch/supervisor-death.log" >&2; \
             kill "$supervisor_launcher_pid" 2>/dev/null || true; \
             fail "execution-supervisor death fixture did not find the supervisor"; }
    find /tmp -maxdepth 1 -type d -name 'zeropaper-update-source-*' -print \
        | sort > "$scratch/supervisor-snapshots.during"
    supervisor_snapshot="$(comm -13 "$scratch/supervisor-snapshots.before" \
        "$scratch/supervisor-snapshots.during")"
    [ -n "$supervisor_snapshot" ] \
        && [ "$(printf '%s\n' "$supervisor_snapshot" | wc -l)" -eq 1 ] \
        || fail "execution-supervisor fixture did not isolate one source snapshot"
    kill -KILL "$supervisor_pid"
    wait "$supervisor_launcher_pid" 2>/dev/null || true
    for _ in $(seq 1 1500); do
        [ ! -e "$supervisor_snapshot" ] && break
        sleep 0.02
    done
    [ ! -e "$supervisor_snapshot" ] \
        || fail "execution-supervisor death leaked its pinned source snapshot"
fi

descendant_pid_file="$scratch/failed-refresh-descendant.pid"
lock_fd_marker="$scratch/refresh-lock-fd.marker"
if ZEROPAPER_TEST_FAIL_REFRESH_CHILD=1 \
   ZEROPAPER_TEST_DESCENDANT_PID="$descendant_pid_file" \
   ZEROPAPER_TEST_LOCK_FD_MARKER="$lock_fd_marker" \
   ZEROPAPER_TEST_PROJECT_ROOT="$guardian_target" \
   /bin/bash -c "$guardian_command --no-model-probe" \
   >"$scratch/guardian-failure.log" 2>&1; then
    fail "instrumented failed refresh unexpectedly succeeded"
fi
[ -s "$descendant_pid_file" ] || { cat "$scratch/guardian-failure.log" >&2; fail "failed refresh did not create descendant fixture"; }
[ "$(cat "$lock_fd_marker")" = "clean" ] \
    || fail "refresh body inherited the trusted project-lock descriptor"
failed_descendant_pid="$(cat "$descendant_pid_file")"
if kill -0 "$failed_descendant_pid" 2>/dev/null; then
    fail "failed refresh descendant survived guardian teardown"
fi
/usr/bin/python3 -I - "$guardian_target" <<'PY'
import fcntl
import os
import sys

fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
finally:
    os.close(fd)
PY

lingering_pid_file="$scratch/successful-refresh-descendant.pid"
if ! ZEROPAPER_TEST_LINGER_REFRESH_CHILD=1 \
   ZEROPAPER_TEST_LINGER_PID="$lingering_pid_file" \
   /bin/bash -c "$guardian_command --no-model-probe" \
   >"$scratch/guardian-success.log" 2>&1; then
    cat "$scratch/guardian-success.log" >&2
    fail "instrumented successful refresh failed"
fi
[ -s "$lingering_pid_file" ] \
    || { cat "$scratch/guardian-success.log" >&2; fail "successful refresh omitted descendant fixture"; }
lingering_pid="$(cat "$lingering_pid_file")"
if kill -0 "$lingering_pid" 2>/dev/null; then
    fail "successful refresh descendant survived guardian drain"
fi

# Once the guardian reports armed it, rather than the visible coordinator,
# has already released the body. Killing the coordinator at that boundary
# must not strand the body or retain LOCK_EX forever.
if ZEROPAPER_TEST_KILL_ARMING_PARENT=1 \
   /bin/bash -c "$guardian_command --dry-run --no-model-probe" \
   >"$scratch/guardian-arming-parent-death.log" 2>&1; then
    fail "arming-parent death fixture unexpectedly succeeded"
fi
grep -Fq 'Dry run complete. No files modified.' \
    "$scratch/guardian-arming-parent-death.log" \
    || { cat "$scratch/guardian-arming-parent-death.log" >&2; \
         fail "guardian did not keep the source snapshot alive through body completion"; }
/usr/bin/python3 -I - "$guardian_target" <<'PY'
import fcntl
import os
import sys
import time

deadline = time.monotonic() + 15
while True:
    fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise SystemExit("guardian retained project lock after arming-parent death")
            time.sleep(0.05)
            continue
        break
    finally:
        os.close(fd)
PY

expect_failure "update target overlaps template source checkout" \
    "$source_checkout/test_scripts/update_with_manifest_selectors.py" \
    "$source_checkout" --variant finance --no-model-probe
expect_failure "update target overlaps template source checkout" \
    "$source_checkout/test_scripts/update_with_manifest_selectors.py" \
    "$scratch" --variant finance --no-model-probe
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
    || { jq '.source' "$clean_output/.deploy_manifest.json" >&2;
         git -C "$source_checkout" status --short >&2;
         fail "clean assembly manifest has incorrect source provenance"; }

# The isolated launcher fixes the process umask, so setup bytes and executable
# modes are independent of the caller and updates can converge exactly.
umask_output_022="$scratch/umask-022-assembly"
umask_output_077="$scratch/umask-077-assembly"
(umask 022; "$setup" "$umask_output_022" --assemble-only --no-model-probe \
    >"$scratch/umask-022.log" 2>&1)
(umask 077; "$setup" "$umask_output_077" --assemble-only --no-model-probe \
    >"$scratch/umask-077.log" 2>&1)
[ "$(file_mode "$umask_output_022/launch.sh")" = \
  "$(file_mode "$umask_output_077/launch.sh")" ] \
    || fail "setup launch mode depends on caller umask"
[ "$(file_mode "$umask_output_022/CLAUDE.md")" = \
  "$(file_mode "$umask_output_077/CLAUDE.md")" ] \
    || fail "setup managed-file mode depends on caller umask"

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
# stability check. Mutating the live checkout after that assembly must not
# change the applied version or dependency specifications. The updater
# deliberately never mutates an existing project virtualenv.
expected_update_version="$(jq -r '.template_version' "$clean_output/.deploy_manifest.json")"
expected_core_deps="$scratch/expected-core-deps.txt"
cp "$clean_output/.arpipeline/update_inputs/deps/core.txt" "$expected_core_deps"
fake_site_packages="$clean_output/.venv/lib/python3.12/site-packages"
mkdir -p "$fake_site_packages"
printf 'stale guard\n' > "$fake_site_packages/_pipeline_dotenv_guard.py"
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
python3 -I - "$clean_output/process_log/.opencode-control" "$source_checkout" \
    "$scratch/update-source-mutated" <<'PY' &
import glob
import os
import sys
import time

control, source, marker = sys.argv[1:]
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    if glob.glob(os.path.join(control, "update.*", "refresh", ".deploy_manifest.json")):
        with open(os.path.join(source, "VERSION"), "w", encoding="utf-8") as handle:
            handle.write("99.99.99\n")
        with open(os.path.join(source, "deploy_assets/templates/utils/pipeline_dotenv_guard.py"),
                  "w", encoding="utf-8") as handle:
            handle.write('raise RuntimeError("live guard leaked")\n')
        with open(os.path.join(source, "deploy_assets/templates/deps/core.txt"),
                  "w", encoding="utf-8") as handle:
            handle.write("live-dependency-leak\n")
        with open(marker, "w", encoding="utf-8") as handle:
            handle.write("mutated\n")
        raise SystemExit
    time.sleep(0.005)
raise SystemExit("timed out waiting for completed fresh update assembly")
PY
post_assembly_watcher=$!
SOURCE_POLICY_UPDATE_OUTPUT="$clean_output" \
SOURCE_POLICY_UPDATE_LAUNCHER="$source_checkout/update.sh" \
SOURCE_POLICY_UPDATE_PYTHON_MARKER="$hostile_update_python_marker" \
BASH_ENV="$post_assembly_hook" \
PATH="$hostile_update_bin:$PATH" \
    "$source_checkout/test_scripts/update_with_manifest_selectors.py" \
    "$clean_output" --no-model-probe \
    >"$scratch/update-source-consistency.log" 2>&1 \
    || { cat "$scratch/update-source-consistency.log" >&2; fail "pinned-source update failed"; }
wait "$post_assembly_watcher" || fail "post-assembly source watcher failed"
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
grep -Fxq 'stale guard' "$fake_site_packages/_pipeline_dotenv_guard.py" \
    || fail "update mutated the existing project virtualenv"
cmp -s "$clean_output/.arpipeline/update_inputs/deps/core.txt" "$expected_core_deps" \
    || fail "update applied live post-assembly dependency bytes"
git -C "$source_checkout" restore VERSION \
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
