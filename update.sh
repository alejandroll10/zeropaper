#!/usr/bin/python3 -I
"""Start the updater without allowing Bash startup hooks to run first."""

import atexit
import fcntl
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile


live_checkout_root = os.path.dirname(os.path.realpath(__file__))
if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
    raise SystemExit("Error: usage: update.sh <project> [explicit selector flags]")
project_candidate = os.path.realpath(os.path.abspath(sys.argv[1]))
try:
    common = os.path.commonpath((project_candidate, live_checkout_root))
except ValueError:
    common = ""
if common == project_candidate:
    raise SystemExit("ERROR: update target overlaps template source checkout")
if common == live_checkout_root:
    scratch_root = os.path.join(live_checkout_root, "test_output")
    try:
        scratch_common = os.path.commonpath((project_candidate, scratch_root))
    except ValueError:
        scratch_common = ""
    if (scratch_common != scratch_root or not os.path.isdir(scratch_root)
            or os.path.islink(scratch_root)):
        raise SystemExit("ERROR: update target overlaps template source checkout")
manifest_path = os.path.join(project_candidate, ".deploy_manifest.json")
try:
    manifest_info = os.lstat(manifest_path)
except OSError as error:
    raise SystemExit(
        "ERROR: update supports only same-version manifest-backed deployments"
    ) from error
if not stat.S_ISREG(manifest_info.st_mode) or manifest_info.st_nlink != 1:
    raise SystemExit(
        "ERROR: update supports only same-version manifest-backed deployments"
    )

# Acquire the same kernel lock held by every supported launcher before copying
# or exposing any source snapshot. This excludes project agents for the full
# attestation/assembly interval, rather than only after the coordinator starts.
project_lock_fd = os.open(
    project_candidate,
    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
)
try:
    fcntl.flock(project_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError as error:
    os.close(project_lock_fd)
    raise SystemExit(
        "ERROR: project runtime is active; stop every launch.sh session before update."
    ) from error
os.set_inheritable(project_lock_fd, True)


def attested_source_digest(arguments):
    values = []
    for index, argument in enumerate(arguments):
        if argument == "--source-digest" and index + 1 < len(arguments):
            values.append(arguments[index + 1])
        elif argument.startswith("--source-digest="):
            values.append(argument.split("=", 1)[1])
    if len(values) != 1 or not values[0].startswith("sha256:") or len(values[0]) != 71:
        raise SystemExit("Error: update requires exactly one valid --source-digest attestation")
    return values[0]


source_inputs = (
    "setup.sh", "update.sh", "scripts/update_coordinator.sh",
    "VERSION", "LICENSE", ".env.example", "deploy_assets",
)


def ignored_source_name(name):
    return (
        name in {"__pycache__", ".ipynb_checkpoints", ".venv", "venv"}
        or name.endswith(".egg-info")
    )


def source_digest(root):
    hasher = hashlib.sha256()

    def emit(kind, logical, mode, payload=b""):
        hasher.update(kind.encode() + b"\0")
        hasher.update(logical.encode() + b"\0")
        hasher.update(f"{stat.S_IMODE(mode):o}".encode() + b"\0")
        hasher.update(payload)
        hasher.update(b"\0")

    def visit(logical, actual):
        info = os.lstat(actual)
        if stat.S_ISLNK(info.st_mode):
            raise SystemExit(f"Error: symlink build input is not allowed: {logical}")
        if stat.S_ISDIR(info.st_mode):
            emit("dir", logical, info.st_mode)
            for name in sorted(os.listdir(actual)):
                if ignored_source_name(name):
                    continue
                visit(f"{logical}/{name}", os.path.join(actual, name))
            return
        if stat.S_ISREG(info.st_mode):
            if logical.endswith(".pyc"):
                raise SystemExit(f"Error: standalone bytecode build input is not allowed: {logical}")
            if logical.endswith(("/.DS_Store", "/Thumbs.db")):
                return
            with open(actual, "rb") as handle:
                emit("file", logical, info.st_mode, handle.read())
            return
        raise SystemExit(f"Error: unsupported build-input file type: {logical}")

    for logical in source_inputs:
        actual = os.path.join(root, logical)
        if not os.path.lexists(actual):
            raise SystemExit(f"Error: missing build input: {actual}")
        visit(logical, actual)
    return "sha256:" + hasher.hexdigest()


def validate_selector_arguments(arguments):
    counts = {
        "source": 0, "variant": 0, "mode": 0, "clear_ext": 0,
        "seeded": 0, "faithful": 0, "manual": 0, "light": 0, "halt": 0,
        "dry_run": 0, "model_probe": 0,
    }
    extensions = []
    value_options = {
        "--source-digest": "source", "--variant": "variant",
        "--mode": "mode", "--ext": "ext",
    }
    boolean_options = {
        "--no-mode": "mode", "--clear-ext": "clear_ext",
        "--seeded": "seeded", "--no-seeded": "seeded",
        "--faithful": "faithful", "--no-faithful": "faithful",
        "--manual": "manual", "--no-manual": "manual",
        "--light": "light", "--no-light": "light",
        "--halt-on-core-bypass": "halt",
        "--no-halt-on-core-bypass": "halt",
        "--dry-run": "dry_run", "--no-model-probe": "model_probe",
    }
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        matched = False
        for option, key in value_options.items():
            if argument == option:
                if index + 1 >= len(arguments) or arguments[index + 1].startswith("--"):
                    raise SystemExit(f"ERROR: {option} requires a value")
                value = arguments[index + 1]
                index += 2
                matched = True
            elif argument.startswith(option + "="):
                value = argument.split("=", 1)[1]
                index += 1
                matched = True
            else:
                continue
            if key == "ext":
                extensions.append(value)
            else:
                if key == "mode" and value == "":
                    raise SystemExit(
                        "ERROR: empty --mode is unsupported; use explicit --no-mode"
                    )
                counts[key] += 1
            break
        if matched:
            continue
        if argument in boolean_options:
            if argument == "--clear-ext" and extensions:
                raise SystemExit(
                    "ERROR: --clear-ext must precede every --ext selector"
                )
            counts[boolean_options[argument]] += 1
            index += 1
            continue
        raise SystemExit(f"ERROR: unsupported or duplicate-position update argument: {argument}")
    required_once = ("source", "variant", "mode", "seeded", "faithful",
                     "manual", "light", "halt")
    if any(counts[key] != 1 for key in required_once):
        raise SystemExit(
            "ERROR: update requires each deployment selector exactly once"
        )
    if counts["clear_ext"] > 1 or (not extensions and counts["clear_ext"] != 1):
        raise SystemExit(
            "ERROR: extension selector requires one --clear-ext for an empty list"
        )
    if (any(value not in {"empirical", "theory_llm"} for value in extensions)
            or len(extensions) != len(set(extensions))):
        raise SystemExit("ERROR: extension selector contains empty, unknown, or duplicate values")
    if counts["dry_run"] > 1 or counts["model_probe"] > 1:
        raise SystemExit("ERROR: update controls may not be repeated")


validate_selector_arguments(sys.argv[2:])


expected_source_digest = attested_source_digest(sys.argv[1:])
system_temp_root = os.path.realpath("/tmp")
if not os.path.isdir(system_temp_root) or os.path.islink(system_temp_root):
    raise SystemExit("Error: updater requires a real system /tmp directory")

# A separate cleanup owner creates the private snapshot itself.  Starting the
# owner before the directory exists closes the otherwise unavoidable SIGKILL
# window between mkdtemp() and guardian startup.  Until the execution
# supervisor accepts handoff, EOF from this launcher makes the owner wait for
# the project lock and then remove the snapshot without following symlinks.
snapshot_owner_source = r'''
import fcntl
import os
import select
import stat
import sys
import tempfile

project, temp_root = sys.argv[1:3]
liveness_fd, supervisor_fd, control_fd, status_fd, ack_fd = map(int, sys.argv[3:8])
snapshot = None
cleanup_done = False
handed_off = False


def remove_private_tree(root):
    if not os.path.lexists(root):
        return
    root_info = os.lstat(root)
    if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
        raise RuntimeError(f"unsafe updater snapshot root: {root}")
    directories = []
    pending = [root]
    while pending:
        current = pending.pop()
        info = os.lstat(current)
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise RuntimeError(f"unsafe updater snapshot directory: {current}")
        os.chmod(current, 0o700)
        directories.append(current)
        with os.scandir(current) as entries:
            for entry in entries:
                child_info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(child_info.st_mode) and not stat.S_ISLNK(child_info.st_mode):
                    pending.append(entry.path)
                else:
                    os.unlink(entry.path)
    for directory in reversed(directories):
        os.rmdir(directory)
    if os.path.lexists(root):
        raise RuntimeError(f"updater snapshot cleanup incomplete: {root}")


try:
    snapshot = tempfile.mkdtemp(prefix="zeropaper-update-source-", dir=temp_root)
    os.write(status_fd, (snapshot + "\n").encode("utf-8"))
    os.close(status_fd)
    status_fd = -1
    while True:
        watched_liveness = supervisor_fd if handed_off else liveness_fd
        watched = [watched_liveness]
        if control_fd >= 0:
            watched.append(control_fd)
        readable, _, _ = select.select(watched, [], [])
        if control_fd >= 0 and control_fd in readable:
            command = os.read(control_fd, 1)
            if command == b"H" and not handed_off:
                handed_off = True
                os.close(liveness_fd)
                liveness_fd = -1
                os.write(ack_fd, b"handed-off\n")
                os.close(ack_fd)
                ack_fd = -1
                os.close(control_fd)
                control_fd = -1
                continue
            if command == b"":
                # The launcher vanished without completing a handoff.
                owner_lost = True
            else:
                owner_lost = False
        else:
            owner_lost = False
        if (watched_liveness in readable
                and os.read(watched_liveness, 1) == b""):
            owner_lost = True
        if owner_lost:
            project_fd = os.open(
                project,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_NOFOLLOW", 0),
            )
            try:
                fcntl.flock(project_fd, fcntl.LOCK_EX)
                remove_private_tree(snapshot)
                cleanup_done = True
            finally:
                os.close(project_fd)
            raise SystemExit(0)
except BaseException:
    if status_fd >= 0:
        try:
            os.write(status_fd, b"failed\n")
        except OSError:
            pass
        os.close(status_fd)
        status_fd = -1
    if ack_fd >= 0:
        try:
            os.write(ack_fd, b"failed\n")
        except OSError:
            pass
        os.close(ack_fd)
        ack_fd = -1
    # This exception path includes launcher death before or during the initial
    # status write. Close the status pipe first so a live launcher can unwind
    # and release LOCK_EX, then remove every created snapshot unless ownership
    # was explicitly handed to the execution supervisor.
    if snapshot is not None and not handed_off and not cleanup_done:
        project_fd = os.open(
            project,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            fcntl.flock(project_fd, fcntl.LOCK_EX)
            remove_private_tree(snapshot)
            cleanup_done = True
        finally:
            os.close(project_fd)
    raise
finally:
    for descriptor in (liveness_fd, supervisor_fd, control_fd, ack_fd):
        try:
            os.close(descriptor)
        except OSError:
            pass
'''

snapshot_liveness_read_fd, snapshot_liveness_write_fd = os.pipe()
snapshot_supervisor_read_fd, snapshot_supervisor_write_fd = os.pipe()
snapshot_control_read_fd, snapshot_control_write_fd = os.pipe()
snapshot_status_read_fd, snapshot_status_write_fd = os.pipe()
snapshot_ack_read_fd, snapshot_ack_write_fd = os.pipe()
snapshot_owner = subprocess.Popen(
    [
        sys.executable, "-I", "-c", snapshot_owner_source,
        project_candidate, system_temp_root,
        str(snapshot_liveness_read_fd), str(snapshot_supervisor_read_fd),
        str(snapshot_control_read_fd), str(snapshot_status_write_fd),
        str(snapshot_ack_write_fd),
    ],
    env={"PATH": "/usr/bin:/bin"},
    pass_fds=(
        snapshot_liveness_read_fd, snapshot_supervisor_read_fd,
        snapshot_control_read_fd, snapshot_status_write_fd,
        snapshot_ack_write_fd,
    ),
)
os.close(snapshot_liveness_read_fd)
snapshot_liveness_read_fd = -1
os.close(snapshot_supervisor_read_fd)
snapshot_supervisor_read_fd = -1
os.close(snapshot_control_read_fd)
snapshot_control_read_fd = -1
os.close(snapshot_status_write_fd)
snapshot_status_write_fd = -1
os.close(snapshot_ack_write_fd)
snapshot_ack_write_fd = -1
with os.fdopen(snapshot_status_read_fd, "rb", closefd=True) as snapshot_status:
    snapshot_status_read_fd = -1
    snapshot_line = snapshot_status.readline()
try:
    source_snapshot_tmp = snapshot_line.rstrip(b"\n").decode("utf-8")
except UnicodeDecodeError as error:
    raise SystemExit("Error: updater snapshot cleanup owner returned an invalid path") from error
if (
    os.path.dirname(source_snapshot_tmp) != system_temp_root
    or re.fullmatch(r"zeropaper-update-source-[A-Za-z0-9_-]+",
                    os.path.basename(source_snapshot_tmp)) is None
):
    raise SystemExit("Error: updater snapshot cleanup owner failed to start")


def abandon_snapshot_owner():
    # Do not wait here: this launcher still owns LOCK_EX until interpreter
    # teardown.  EOF wakes the owner, and lock acquisition orders cleanup after
    # every launcher-side write has stopped.
    for descriptor_name in (
        "snapshot_control_write_fd", "snapshot_liveness_write_fd",
        "snapshot_supervisor_write_fd", "snapshot_ack_read_fd",
    ):
        descriptor = globals().get(descriptor_name, -1)
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
            globals()[descriptor_name] = -1


atexit.register(abandon_snapshot_owner)
for protected_root in (project_candidate, live_checkout_root):
    try:
        overlap = os.path.commonpath((source_snapshot_tmp, protected_root))
    except ValueError:
        overlap = ""
    if overlap in {source_snapshot_tmp, protected_root}:
        raise SystemExit(
            "Error: updater temporary snapshot overlaps project or template source"
        )
checkout_root = os.path.join(source_snapshot_tmp, "source")
os.mkdir(checkout_root)
try:
    for logical in source_inputs:
        source = os.path.join(live_checkout_root, logical)
        destination = os.path.join(checkout_root, logical)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        if os.path.isdir(source) and not os.path.islink(source):
            shutil.copytree(
                source, destination, symlinks=True,
                ignore=lambda _directory, names: {
                    name for name in names
                    if ignored_source_name(name)
                    or name in {".DS_Store", "Thumbs.db"}
                },
            )
        else:
            shutil.copy2(source, destination, follow_symlinks=False)
    # `.env` is operator-owned secret material, not an attested build input.
    # Carry a framed point-in-time copy through an inherited pipe rather than
    # a named temporary file. Pipes are genuinely unnamed on Linux and macOS;
    # a truncated frame after parent death is rejected by the coordinator.
    live_dotenv = os.path.join(live_checkout_root, ".env")
    try:
        dotenv_fd = os.open(
            live_dotenv, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
        )
    except FileNotFoundError:
        dotenv_fd = None
    dotenv_payload = None
    if dotenv_fd is not None:
        try:
            dotenv_info = os.fstat(dotenv_fd)
            if not stat.S_ISREG(dotenv_info.st_mode) or dotenv_info.st_nlink != 1:
                raise SystemExit("Error: source .env must be one regular non-aliased file")
            chunks = []
            while True:
                chunk = os.read(dotenv_fd, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            dotenv_bytes = b"".join(chunks)
            header = (
                "ZEROPAPER_DOTENV_V1 "
                f"{len(dotenv_bytes)} {hashlib.sha256(dotenv_bytes).hexdigest()}\n"
            ).encode("ascii")
            dotenv_payload = header + dotenv_bytes
        finally:
            os.close(dotenv_fd)
    # Preserve checkout provenance without copying mutable Git internals into
    # the attested build-input set. Git accepts a regular .git indirection file;
    # setup's source wrapper disables hooks, attributes, replacements, and
    # external configuration before reading this metadata.
    live_git_marker = os.path.join(live_checkout_root, ".git")
    git_directory = None
    if os.path.isdir(live_git_marker) and not os.path.islink(live_git_marker):
        git_directory = os.path.realpath(live_git_marker)
    elif os.path.isfile(live_git_marker) and not os.path.islink(live_git_marker):
        with open(live_git_marker, encoding="utf-8") as handle:
            marker = handle.read().strip()
        if marker.startswith("gitdir:"):
            git_directory = marker.split(":", 1)[1].strip()
            if not os.path.isabs(git_directory):
                git_directory = os.path.realpath(
                    os.path.join(live_checkout_root, git_directory)
                )
    if git_directory is not None:
        with open(os.path.join(checkout_root, ".git"), "x", encoding="utf-8") as handle:
            handle.write(f"gitdir: {git_directory}\n")
    captured_digest = source_digest(checkout_root)
    if captured_digest != expected_source_digest:
        raise SystemExit(
            "Error: checkout does not match the operator-attested trusted setup digest"
        )
except BaseException:
    raise

coordinator = os.path.join(checkout_root, "scripts", "update_coordinator.sh")
coordinator_info = os.lstat(coordinator)
if not stat.S_ISREG(coordinator_info.st_mode) or coordinator_info.st_nlink != 1:
    raise SystemExit("Error: snapshotted update coordinator is not one regular file")

clean = {
    key: value
    for key, value in os.environ.items()
    if key
    not in {
        "BASH_ENV",
        "ENV",
        "BASHOPTS",
        "SHELLOPTS",
        "BASH_COMPAT",
        "POSIXLY_CORRECT",
        "CDPATH",
        "GLOBIGNORE",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_PROMPT_MODIFIER",
        "PIPENV_ACTIVE",
        "POETRY_ACTIVE",
    }
    and not key.startswith("BASH_FUNC_")
}
activation_roots = []
for key in ("VIRTUAL_ENV", "CONDA_PREFIX"):
    value = os.environ.get(key)
    if value:
        activation_roots.append((os.path.abspath(value), os.path.realpath(value)))


def is_at_or_within_identity(candidate, ancestor):
    current = candidate
    while True:
        try:
            if os.path.samefile(current, ancestor):
                return True
        except OSError:
            pass
        parent = os.path.dirname(current)
        if parent == current:
            return False
        current = parent


def path_is_activated_or_checkout(path):
    logical = os.path.abspath(path)
    physical = os.path.realpath(path)
    parts = {part.lower() for part in (*logical.split(os.sep), *physical.split(os.sep))}
    if {".venv", "venv"} & parts:
        return True
    for candidate in (logical, physical):
        if (is_at_or_within_identity(candidate, checkout_root)
                or is_at_or_within_identity(candidate, live_checkout_root)):
            return True
        for active_logical, active_physical in activation_roots:
            if is_at_or_within_identity(candidate, active_logical) \
                    or is_at_or_within_identity(candidate, active_physical):
                return True
    return False


safe_path = []
for raw in os.environ.get("PATH", "").split(os.pathsep):
    if not raw:
        continue
    physical = os.path.realpath(os.path.abspath(raw))
    if path_is_activated_or_checkout(raw) or not os.path.isdir(physical):
        continue
    if physical not in safe_path:
        safe_path.append(physical)
trusted_jq = ""
candidate_roots = (
    ("/usr/bin/jq", ("/usr",)),
    ("/bin/jq", ("/usr", "/bin")),
    ("/opt/homebrew/bin/jq", ("/opt/homebrew",)),
    ("/usr/local/bin/jq", ("/usr/local",)),
    ("/opt/local/bin/jq", ("/opt/local",)),
    ("/run/current-system/sw/bin/jq", ("/nix/store",)),
)
for candidate, allowed_roots in candidate_roots:
    physical = os.path.realpath(candidate)
    if path_is_activated_or_checkout(candidate) or not os.path.isfile(physical):
        continue
    if not any(
        os.path.commonpath((physical, root)) == root
        for root in allowed_roots
    ):
        continue
    try:
        info = os.stat(physical)
    except OSError:
        continue
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or not os.access(physical, os.X_OK)
        or (
            info.st_uid != os.geteuid()
            and info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)
        )
    ):
        continue
    trusted_jq = physical
    break
if not trusted_jq:
    raise SystemExit(
        "Error: update requires jq at a fixed host installation path "
        "(/usr/bin, /bin, Homebrew, MacPorts, or Nix system profile)"
    )
clean["PATH"] = os.pathsep.join(safe_path)
clean["ZEROPAPER_UPDATE_LAUNCH_ROOT"] = checkout_root
clean["ZEROPAPER_UPDATE_JQ"] = trusted_jq
clean["ZEROPAPER_UPDATE_PROJECT_LOCK_FD"] = str(project_lock_fd)
dotenv_read_fd = None
dotenv_write_fd = None
if dotenv_payload is not None:
    dotenv_read_fd, dotenv_write_fd = os.pipe()
    os.set_inheritable(dotenv_read_fd, True)
    clean["ZEROPAPER_UPDATE_DOTENV_FD"] = str(dotenv_read_fd)
def trusted_bash_executable():
    if sys.platform == "darwin":
        candidates = (
            "/opt/homebrew/bin/bash", "/usr/local/bin/bash", "/opt/local/bin/bash"
        )
    else:
        candidates = ("/bin/bash", "/usr/bin/bash")
    for candidate in candidates:
        try:
            bash_info = os.stat(candidate)
        except OSError:
            continue
        if (not stat.S_ISREG(bash_info.st_mode)
                or not os.access(candidate, os.X_OK)
                or bash_info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)):
            continue
        try:
            version = subprocess.run(
                [candidate, "--version"], stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, timeout=5,
                env={"PATH": "/usr/bin:/bin"}, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        match = re.search(r"version\s+([0-9]+)\.", version.stdout)
        if version.returncode == 0 and match and int(match.group(1)) >= 4:
            return candidate
    raise SystemExit(
        "Error: updater requires protected Bash 4+ at a fixed system/Homebrew path"
    )


trusted_bash = trusted_bash_executable()
os.umask(0o022)

# Run the coordinator beneath a small trusted supervisor rather than making it
# a direct child of this public launcher.  The supervisor owns cleanup after
# handoff: if this launcher is SIGKILLed, EOF on the liveness pipe makes the
# supervisor terminate the coordinator.  The coordinator's own detached
# guardian then drains its refresh body while retaining LOCK_EX.  Only after a
# fresh lock acquisition proves that every updater writer is gone does the
# supervisor remove the pinned source snapshot.  This works on both Linux and
# macOS and does not depend on parent-death signals.
supervisor_source = r'''
import fcntl
import os
import select
import signal
import stat
import subprocess
import sys
import time

project, snapshot = sys.argv[1:3]
lock_fd, liveness_fd, status_fd, dotenv_fd, backup_fd = map(int, sys.argv[3:8])
trusted_bash, coordinator = sys.argv[8:10]
arguments = sys.argv[10:]
child = None
spawned = False
exit_status = 1


def remove_private_tree(root):
    if not os.path.lexists(root):
        return
    root_info = os.lstat(root)
    if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
        raise RuntimeError(f"unsafe updater snapshot root: {root}")
    directories = []
    pending = [root]
    while pending:
        current = pending.pop()
        info = os.lstat(current)
        if not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode):
            raise RuntimeError(f"unsafe updater snapshot directory: {current}")
        os.chmod(current, 0o700)
        directories.append(current)
        with os.scandir(current) as entries:
            for entry in entries:
                child_info = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(child_info.st_mode) and not stat.S_ISLNK(child_info.st_mode):
                    pending.append(entry.path)
                else:
                    os.unlink(entry.path)
    for directory in reversed(directories):
        os.rmdir(directory)
    if os.path.lexists(root):
        raise RuntimeError(f"updater snapshot cleanup incomplete: {root}")


def remove_snapshot():
    fd = os.open(
        project,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        remove_private_tree(snapshot)
    finally:
        os.close(fd)


def stop_child():
    if child is None or child.poll() is not None:
        return
    for sent_signal, duration in ((signal.SIGTERM, 2.0), (signal.SIGKILL, 5.0)):
        try:
            child.send_signal(sent_signal)
        except ProcessLookupError:
            return
        deadline = time.monotonic() + duration
        while time.monotonic() < deadline:
            if child.poll() is not None:
                return
            time.sleep(0.02)


try:
    child_fds = [lock_fd, liveness_fd]
    if dotenv_fd >= 0:
        child_fds.append(dotenv_fd)
    child = subprocess.Popen(
        [trusted_bash, coordinator, *arguments],
        env=os.environ.copy(),
        pass_fds=tuple(child_fds),
    )
    spawned = True
    os.write(status_fd, b"spawned\n")
    os.close(status_fd)
    status_fd = -1
    os.close(lock_fd)
    lock_fd = -1
    if dotenv_fd >= 0:
        os.close(dotenv_fd)
        dotenv_fd = -1

    launcher_died = False
    while child.poll() is None:
        readable, _, _ = select.select([liveness_fd], [], [], 0.1)
        if readable and os.read(liveness_fd, 1) == b"":
            launcher_died = True
            stop_child()
            break
    returncode = child.wait()
    remove_snapshot()
    exit_status = 143 if launcher_died else returncode
except BaseException:
    stop_child()
    if lock_fd >= 0:
        os.close(lock_fd)
        lock_fd = -1
    if dotenv_fd >= 0:
        os.close(dotenv_fd)
        dotenv_fd = -1
    try:
        if spawned:
            remove_snapshot()
    except BaseException:
        pass
    raise
finally:
    if status_fd >= 0:
        try:
            os.write(status_fd, b"failed\n")
        except OSError:
            pass
        os.close(status_fd)
    for descriptor in (lock_fd, liveness_fd, dotenv_fd, backup_fd):
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
raise SystemExit(exit_status)
'''

liveness_read_fd, liveness_write_fd = os.pipe()
status_read_fd, status_write_fd = os.pipe()
clean["ZEROPAPER_UPDATE_LAUNCHER_LIVENESS_FD"] = str(liveness_read_fd)
supervisor = None
try:
    inherited_fds = [
        project_lock_fd, liveness_read_fd, status_write_fd,
        snapshot_supervisor_write_fd,
    ]
    if dotenv_read_fd is not None:
        inherited_fds.append(dotenv_read_fd)
    supervisor = subprocess.Popen(
        [
            sys.executable, "-I", "-c", supervisor_source,
            project_candidate, source_snapshot_tmp,
            str(project_lock_fd), str(liveness_read_fd), str(status_write_fd),
            str(dotenv_read_fd if dotenv_read_fd is not None else -1),
            str(snapshot_supervisor_write_fd),
            trusted_bash, coordinator, *sys.argv[1:],
        ],
        env=clean,
        pass_fds=tuple(inherited_fds),
    )
    os.close(snapshot_supervisor_write_fd)
    snapshot_supervisor_write_fd = -1
    os.close(liveness_read_fd)
    liveness_read_fd = -1
    os.close(status_write_fd)
    status_write_fd = -1
    with os.fdopen(status_read_fd, "rb", closefd=True) as status_reader:
        status_read_fd = -1
        if status_reader.readline() != b"spawned\n":
            raise SystemExit("Error: update supervisor failed to start coordinator")
    # The execution supervisor owns writer teardown and primary snapshot
    # cleanup. Keep the creation-time owner as an independent fallback: the
    # supervisor alone holds its liveness pipe, so SIGKILL/OOM wakes the owner,
    # which waits for the project lock before removing the snapshot.
    os.write(snapshot_control_write_fd, b"H")
    with os.fdopen(snapshot_ack_read_fd, "rb", closefd=True) as ack_reader:
        snapshot_ack_read_fd = -1
        if ack_reader.readline() != b"handed-off\n":
            raise SystemExit("Error: updater snapshot cleanup owner handoff failed")
    os.close(snapshot_control_write_fd)
    snapshot_control_write_fd = -1
    os.close(snapshot_liveness_write_fd)
    snapshot_liveness_write_fd = -1
    atexit.unregister(abandon_snapshot_owner)
    # The coordinator and its detached guardian now own the original lock OFD.
    # Closing this copy also lets the supervisor's fresh-OFD drain check finish
    # after they exit.
    os.close(project_lock_fd)
    project_lock_fd = -1
    if dotenv_read_fd is not None:
        os.close(dotenv_read_fd)
        dotenv_read_fd = None
        assert dotenv_write_fd is not None and dotenv_payload is not None
        try:
            with os.fdopen(dotenv_write_fd, "wb", closefd=True) as writer:
                dotenv_write_fd = None
                writer.write(dotenv_payload)
        except BrokenPipeError:
            pass
    returncode = supervisor.wait()
    # If the supervisor itself died, its coordinator may still be waiting on
    # this launcher-liveness pipe while holding the project lock. Close our
    # write end before waiting for the backup owner so the coordinator guardian
    # drains, releases the lock, and lets snapshot cleanup complete.
    if liveness_write_fd >= 0:
        os.close(liveness_write_fd)
        liveness_write_fd = -1
    if snapshot_owner.wait() != 0:
        raise SystemExit("Error: updater snapshot cleanup owner failed")
finally:
    if liveness_write_fd >= 0:
        os.close(liveness_write_fd)
        liveness_write_fd = -1
    if liveness_read_fd >= 0:
        os.close(liveness_read_fd)
    if status_read_fd >= 0:
        os.close(status_read_fd)
    if status_write_fd >= 0:
        os.close(status_write_fd)
    if dotenv_read_fd is not None:
        os.close(dotenv_read_fd)
    if dotenv_write_fd is not None:
        os.close(dotenv_write_fd)
    if project_lock_fd >= 0:
        os.close(project_lock_fd)
raise SystemExit(returncode)
