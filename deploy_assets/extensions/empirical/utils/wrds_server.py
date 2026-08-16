"""Persistent WRDS connection server.

Connects to WRDS once (triggers Duo 2FA once), then serves queries
over a private Unix-domain socket.
Scripts send SQL queries and get back
JSON-encoded DataFrames.

Usage:
    # Start the server (do this once at pipeline start):
    python3 code/utils/wrds_server.py &

    # In any script, use the client:
    from utils.wrds_client import wrds_query
    df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")

    # Or check if server is running:
    from utils.wrds_client import wrds_ping
    if wrds_ping():
        df = wrds_query(sql)
    else:
        # Stop and diagnose; never bypass the server with a direct login.
        raise RuntimeError("WRDS server unavailable")

The server is per-host (one process per machine on the fixed port). Its lock,
PID file, Unix socket, and durable authentication latch therefore live together
under ~/.local/state/zeropaper/wrds, not next to this file. Runtime sandboxes
can connect to the socket through their read-only view of the home directory,
but cannot replace the endpoint or mutate operator-only lifecycle state.

Connection recovery
--------------------
A transient `SSL SYSCALL error: EOF detected` (or any other dropped
socket) leaves the pooled psycopg2 connection in a failed-transaction
state. Every subsequent query — even `SELECT 1` — then fails with
"Can't reconnect until invalid transaction is rolled back". The server
detects connection-level errors and recovers transparently in tiers
(rollback -> one pool rebuild) before failing the query;
`ping` exercises the connection with a real `SELECT 1` so a wedged
server reports unhealthy instead of falsely reporting alive. See
GitHub issue #28.
"""
import os
import sys
import json
import socket
import stat
import tempfile
import threading
import signal
import importlib.metadata
import inspect
import hashlib
import errno
import subprocess
import shlex
import struct
import time
from pathlib import Path
from dotenv import load_dotenv

_DOTENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=_DOTENV_PATH)

PORT = 23847  # arbitrary high port
# Bump whenever daemon-side login/recovery safety semantics change. This must
# remain a literal independent of wrds_client's copy so stale daemons mismatch.
SAFETY_PROTOCOL = 'wrds-auth-latch-v6'


def _state_dir():
    """Host-owned state shared read-only with runtime sandboxes.

    Do not use ``~/.cache`` here: it is an intentional sandbox writable root.
    A same-UID agent could otherwise replace the query endpoint, erase the
    retry latch, or plant a PID-file symlink for the host-side launcher to
    follow.  ``~/.local/state`` is visible for AF_UNIX connect but is outside
    every supported runtime's writable roots.
    """
    return os.path.join(os.path.expanduser('~'), '.local', 'state',
                        'zeropaper', 'wrds')

def _pid_file_path():
    """Host-global PID path, keyed by port.

    The WRDS server is per-host (one process per machine on PORT), so its
    PID file must be host-global too — NOT next to __file__. A per-directory
    pid file meant each deployed project tracked only the server it
    personally started: project B's restart-guard never saw project A's
    server, and running the server from the template repo polluted the
    source tree. A single host path fixes both: the restart-guard works
    across every project sharing the one server, and no repo is touched.
    Keep it beside the durable latch/socket in host-owned state.
    """
    return os.path.join(_state_dir(), f'wrds_server_{PORT}.pid')


def _runtime_dir():
    """Return a writable runtime directory even inside read-only sandboxes."""
    base = os.environ.get('XDG_RUNTIME_DIR')
    if base and os.access(base, os.W_OK | os.X_OK):
        return base
    return tempfile.gettempdir()

def _auth_block_path():
    """Host-global credential-rejection latch, keyed by port.

    Co-located with the PID file for the same reason: the server is a per-host
    singleton, so its latch must be host-global too. Persisting it to disk is
    what makes the operator gate real — an in-memory latch is silently reset by
    killing and restarting the server, and `start_services.sh` runs at every
    pipeline launch, so the automated path would otherwise spend one login per
    session with no operator ever involved. Bounded per start, unbounded across
    restarts.

    Unlike the PID file, this state MUST survive logout and reboot: every new
    pipeline session starts services automatically, so runtime/temp storage
    would silently reset the retry budget. Keep the operator gate in the
    user's durable state directory. It clears only after a verified login
    approved through ``unblock``; ordinary lifecycle events never clear it.
    """
    return os.path.join(_state_dir(), f'wrds_server_{PORT}.authblock')


PID_FILE = _pid_file_path()
AUTH_BLOCK_FILE = _auth_block_path()
SOCKET_FILE = os.path.join(
    os.path.dirname(AUTH_BLOCK_FILE), f'wrds_server_{PORT}.sock')
LOCK_FILE = os.path.join(
    os.path.dirname(AUTH_BLOCK_FILE), f'wrds_server_{PORT}.lock')
CACHE_AUTH_BLOCK_FILE = os.path.join(
    os.path.expanduser('~'), '.cache', 'zeropaper', 'wrds',
    f'wrds_server_{PORT}.authblock')
LEGACY_AUTH_BLOCK_FILE = os.path.join(
    _runtime_dir(), f'.wrds_server_{PORT}.authblock')
MAX_MSG = 10 * 1024 * 1024  # 10MB max message size
MAX_RESPONSE = 512 * 1024 * 1024
MAX_RESULT_MEMORY = 48 * 1024 * 1024
MAX_RESULT_ROWS = 1_000_000
MAX_GET_TABLE_ROWS = 100_000
QUERY_TIMEOUT_SECONDS = 300
CLIENT_IO_TIMEOUT = 15
MAX_CLIENT_THREADS = 32
LOGIN_ATTEMPT_PREFIX = 'WRDS_LOGIN_ATTEMPT_IN_PROGRESS pid='
COMPAT_ACTIVE_PREFIX = 'WRDS_V5_DAEMON_ACTIVE pid='


class WrdsLatchError(RuntimeError):
    """The persistent retry latch cannot be read or written safely."""


class WrdsInstanceBusy(RuntimeError):
    """Another process owns the host-global WRDS singleton lock."""


class WrdsImplicitReconnectError(ConnectionError):
    """SQLAlchemy tried to open a DB connection outside the guarded path."""


def _prepare_auth_block_dir():
    """Create and validate the host-owned WRDS state directory.

    Walk from the filesystem root with directory descriptors and ``O_NOFOLLOW``
    at every component.  Checking only the final ``wrds`` directory is not
    sufficient: a pre-existing ``~/.local/state`` symlink could redirect all
    supposedly protected lifecycle state into a sandbox-writable cache root.
    """
    parent = os.path.dirname(AUTH_BLOCK_FILE)
    parent = os.path.abspath(parent)
    parts = [part for part in parent.split(os.sep) if part]
    flags = (os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) |
             getattr(os, 'O_NOFOLLOW', 0))
    fd = None
    try:
        fd = os.open(os.sep, flags)
        for part in parts:
            try:
                next_fd = os.open(part, flags, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(part, mode=0o700, dir_fd=fd)
                next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
    except OSError as e:
        if fd is not None:
            os.close(fd)
        raise WrdsLatchError(
            f"cannot safely access WRDS retry-latch directory {parent}: {e}"
        ) from e
    try:
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode):
            raise WrdsLatchError(
                f"WRDS retry-latch parent is not a directory: {parent}"
            )
        if hasattr(os, 'getuid') and info.st_uid != os.getuid():
            raise WrdsLatchError(
                f"WRDS retry-latch directory is not owned by this user: {parent}"
            )
        if info.st_mode & 0o022:
            raise WrdsLatchError(
                f"WRDS retry-latch directory is group/world-writable: {parent}"
            )
    finally:
        os.close(fd)


def _acquire_instance_lock():
    """Atomically create the cross-namespace singleton marker.

    This is deliberately an O_EXCL directory mutation, not ``flock``: Linux
    permits an exclusive flock through an O_RDONLY descriptor, so a sandbox
    with a read-only view could otherwise hold the daemon's restart mutex.
    """
    _prepare_auth_block_dir()
    start_token = _process_start_token(os.getpid())
    if not start_token:
        raise WrdsLatchError(
            "cannot establish this process's birth identity for the WRDS "
            "singleton marker")
    marker = json.dumps({"pid": os.getpid(), "start": start_token}) + "\n"
    for _ in range(8):
        tmp_path = None
        try:
            # Publish only a complete record. O_EXCL followed by write has an
            # empty-file window in which a concurrent starter can misclassify
            # the live owner as stale. A same-directory hard link is atomic:
            # readers see either no marker or the fully written inode.
            parent = os.path.dirname(LOCK_FILE)
            fd, tmp_path = tempfile.mkstemp(
                prefix=os.path.basename(LOCK_FILE) + '.', dir=parent)
            # Read-only after publication: intermediate v4 opens this pathname
            # O_RDWR before taking flock. Mode 0400 makes that legacy writer
            # fail before it can truncate v5's authoritative JSON inode.
            os.fchmod(fd, 0o400)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                handle.write(marker)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(tmp_path, LOCK_FILE, follow_symlinks=False)
            os.unlink(tmp_path)
            tmp_path = None
            return _lock_identity(os.lstat(LOCK_FILE))
        except FileExistsError:
            existing, identity = _read_instance_lock()
            if _lock_owner_live(existing):
                raise WrdsInstanceBusy(
                    "another WRDS server owns the host-global singleton marker")
            if not _remove_lock_if_identity(identity):
                continue
            continue
        except OSError as e:
            raise WrdsLatchError(
                f"cannot safely create WRDS singleton marker {LOCK_FILE}: {e}"
            ) from e
        finally:
            if tmp_path is not None:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
    raise WrdsLatchError("WRDS singleton marker changed repeatedly during cleanup")


def _process_start_token(pid):
    """Stable per-process birth token used to reject recycled PIDs."""
    try:
        raw_stat = Path(f"/proc/{pid}/stat").read_text(encoding='ascii')
        # `comm` is parenthesized and may itself contain spaces. Fields after
        # its final ')' begin at proc-stat field 3; starttime is field 22.
        fields_after_comm = raw_stat.rsplit(')', 1)[1].split()
        start_ticks = fields_after_comm[19]
        boot_id = Path('/proc/sys/kernel/random/boot_id').read_text(
            encoding='ascii').strip()
        return f"proc:{boot_id}:{start_ticks}"
    except (OSError, IndexError):
        try:
            value = subprocess.run(
                ['/bin/ps', '-o', 'lstart=', '-p', str(pid)],
                capture_output=True, text=True, timeout=5, check=False,
            ).stdout.strip()
        except Exception:
            value = ''
        return f"ps:{value}" if value else None


def _lock_identity(info):
    return (info.st_dev, info.st_ino, info.st_ctime_ns)


def _read_instance_lock():
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(LOCK_FILE, flags)
    except FileNotFoundError:
        # A concurrent stale-owner cleanup may have removed the pathname after
        # our link attempt observed EEXIST. Let the acquisition loop retry.
        return None, None
    except OSError as e:
        raise WrdsLatchError(f"cannot safely read WRDS singleton marker: {e}") from e
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink not in (1, 2) or
                (hasattr(os, 'getuid') and info.st_uid != os.getuid()) or
                info.st_mode & 0o022):
            raise WrdsLatchError("WRDS singleton marker failed owner/type/mode checks")
        with os.fdopen(fd, encoding='utf-8') as handle:
            fd = -1
            raw = handle.read()
            try:
                marker = json.loads(raw)
            except (json.JSONDecodeError, UnicodeError) as e:
                # The intermediate v4 bridge used a persistent flock file
                # containing only `<pid>\n`. Recognize exactly that format so
                # a dead owner upgrades automatically; an ambiguous live or
                # recycled PID remains fail-closed.
                legacy = raw.strip()
                if not legacy.isascii() or not legacy.isdigit():
                    raise WrdsLatchError(
                        f"invalid WRDS singleton marker: {e}") from e
                marker = {"pid": int(legacy), "start": None, "legacy": True}
            if not isinstance(marker, dict):
                legacy = raw.strip()
                if legacy.isascii() and legacy.isdigit():
                    marker = {"pid": int(legacy), "start": None,
                              "legacy": True}
                else:
                    raise WrdsLatchError(
                        "WRDS singleton marker is not an owner record")
        return marker, _lock_identity(info)
    finally:
        if fd != -1:
            os.close(fd)


def _lock_owner_live(marker):
    try:
        pid = int(marker['pid'])
        recorded = marker['start']
    except (KeyError, TypeError, ValueError):
        return False
    if marker.get('legacy') is True:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except OSError:
            return True
    return bool(recorded and _process_start_token(pid) == recorded)


def _remove_lock_if_identity(identity):
    try:
        info = os.lstat(LOCK_FILE)
        if _lock_identity(info) != identity:
            return False
        os.unlink(LOCK_FILE)
        return True
    except OSError:
        return False


def _write_pid_file():
    """Atomically publish this PID without ever following a planted symlink."""
    _prepare_auth_block_dir()
    parent = os.path.dirname(PID_FILE)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=os.path.basename(PID_FILE) + '.', dir=parent)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='ascii') as handle:
            handle.write(str(os.getpid()))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, PID_FILE)
        tmp_path = None
    except OSError as e:
        raise WrdsLatchError(f"cannot safely publish WRDS PID file: {e}") from e
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _read_latch_file(path):
    """Securely read one latch path, returning None only when absent."""
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        return None
    except OSError as e:
        raise WrdsLatchError(
            f"cannot safely read WRDS retry latch {path}: {e}"
        ) from e
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise WrdsLatchError(
                f"WRDS retry latch is not a regular file: {path}"
            )
        if hasattr(os, 'getuid') and info.st_uid != os.getuid():
            raise WrdsLatchError(
                f"WRDS retry latch is not owned by this user: {path}"
            )
        if info.st_mode & 0o022:
            raise WrdsLatchError(
                f"WRDS retry latch is group/world-writable: {path}"
            )
        with os.fdopen(fd, encoding='utf-8') as f:
            fd = -1
            message = f.read().strip()
            if not message:
                raise WrdsLatchError(
                    f"WRDS retry latch is empty; refusing to treat existing "
                    f"state as clear: {path}"
                )
            return message
    finally:
        if fd != -1:
            os.close(fd)


def _read_auth_block():
    """Read/migrate every released durable latch without spending a login."""
    _prepare_auth_block_dir()
    message = _read_latch_file(AUTH_BLOCK_FILE)
    if message is not None:
        return message

    # v2.22.2-v2.24.7 used ~/.cache; v2.22.1 used runtime/temp. Ignoring either
    # known rejection during an upgrade would spend a fresh credential attempt.
    # Copy forward atomically and retain every old copy until verified/operator
    # clear so a concurrently invoked older daemon remains blocked too.
    for prior_path in (CACHE_AUTH_BLOCK_FILE, LEGACY_AUTH_BLOCK_FILE):
        if prior_path == CACHE_AUTH_BLOCK_FILE:
            legacy = _read_latch_file(prior_path)
            if legacy is None:
                continue
            if legacy.startswith(COMPAT_ACTIVE_PREFIX):
                # Keep a dead guard in place for _write_compat_guard() to
                # adopt without replacement. Removing it here would open a window
                # in which a released cross-namespace starter sees no latch.
                # Never use this sandbox-writable compatibility record as v5
                # authority; the protected marker + process scan own that job.
                continue
            if _compat_guard_directory_locked():
                # V5 may deliberately retain an older terminal message as the
                # no-gap released-client guard during an operator-approved
                # retry. A mode-0500 compatibility directory plus absence of
                # protected auth state means that retry later verified and
                # cleared the authoritative latch. If v5 died earlier, its
                # protected write-ahead/terminal record would still be above.
                continue
        else:
            legacy = _read_latch_file(prior_path)
        if legacy is not None:
            _write_auth_block(legacy)
            return legacy
    return None


def _write_auth_block(msg):
    """Persist the latch atomically without following an existing symlink."""
    _prepare_auth_block_dir()
    parent = os.path.dirname(AUTH_BLOCK_FILE)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=os.path.basename(AUTH_BLOCK_FILE) + '.', dir=parent)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(msg)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, AUTH_BLOCK_FILE)
        tmp_path = None
        # Persist the directory entry as well as the file contents. The latch
        # is a write-ahead safety record: a crash after login begins must not
        # make the marker disappear on restart.
        dir_fd = os.open(parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except OSError as e:
        raise WrdsLatchError(
            f"cannot persist WRDS retry latch {AUTH_BLOCK_FILE}: {e}"
        ) from e
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _clear_auth_block(preserve_compat=False):
    """Remove the latch after verified success or operator-approved unblock."""
    removed_parents = set()
    for path in (AUTH_BLOCK_FILE, CACHE_AUTH_BLOCK_FILE,
                 LEGACY_AUTH_BLOCK_FILE):
        if preserve_compat and path == CACHE_AUTH_BLOCK_FILE:
            # Compatibility state is sandbox-writable by necessity because
            # released clients read it there. Never trust/read it on the v5
            # success path; simply retain the guard published before login.
            continue
        try:
            os.remove(path)
            removed_parents.add(os.path.dirname(path))
        except FileNotFoundError:
            continue
        except OSError as e:
            raise WrdsLatchError(
                f"cannot clear WRDS retry latch {path}: {e}"
            ) from e
    for parent in removed_parents:
        try:
            dir_fd = os.open(parent, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError as e:
            raise WrdsLatchError(
                f"cannot durably clear WRDS retry-latch directory {parent}: {e}"
            ) from e


def _begin_login_attempt(replace_blocked=False):
    """Write the durable guard that must precede every credentialed login.

    It is deliberately indistinguishable from a terminal latch after this
    process dies. Only a fully verified connection clears it. While this PID
    is alive, clients recognize it as an in-progress startup and may wait for
    Duo without interpreting the marker as a rejection.
    """
    existing = _read_auth_block()
    if existing and not replace_blocked:
        raise WrdsLatchError(
            "refusing WRDS login because a retry latch already exists: "
            f"{existing}"
        )
    if replace_blocked and not existing:
        raise WrdsLatchError(
            "operator retry requires an existing terminal WRDS latch")
    birth = _process_start_token(os.getpid())
    if not birth:
        raise WrdsLatchError(
            "cannot establish process birth identity before WRDS login")
    marker = (
        f"{LOGIN_ATTEMPT_PREFIX}{os.getpid()} start={birth}\n"
        "A WRDS login began but has not been confirmed successful. If the "
        "owning process is no longer alive, do not retry automatically; an "
        "operator must inspect the prior attempt and approve unblock."
    )
    _write_auth_block(marker)
    return marker


def _live_login_attempt(message):
    """True only for a write-ahead login marker owned by a live process."""
    first_line = str(message).splitlines()[0]
    if not first_line.startswith(LOGIN_ATTEMPT_PREFIX):
        return False
    try:
        identity = first_line[len(LOGIN_ATTEMPT_PREFIX):]
        pid_text, separator, recorded = identity.partition(' start=')
        if not separator or not recorded:
            # Released PID-only markers cannot prove identity after PID reuse
            # or reboot and therefore remain terminal until operator review.
            return False
        pid = int(pid_text)
    except ValueError:
        return False
    return _process_start_token(pid) == recorded


def _marker_owner(message, prefix):
    first_line = str(message).splitlines()[0]
    if not first_line.startswith(prefix):
        return None, None
    identity = first_line[len(prefix):]
    pid_text, separator, recorded = identity.partition(' start=')
    if not separator or not recorded:
        return None, None
    try:
        return int(pid_text), recorded
    except ValueError:
        return None, None


def _live_compat_guard(message):
    pid, recorded = _marker_owner(message, COMPAT_ACTIVE_PREFIX)
    return bool(pid and recorded and _process_start_token(pid) == recorded)


def _verify_auth_block_storage():
    """Prove latch storage works before any connection can spend a login."""
    _prepare_auth_block_dir()
    parent = os.path.dirname(AUTH_BLOCK_FILE)
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(
            prefix=os.path.basename(AUTH_BLOCK_FILE) + '.probe.', dir=parent)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write('probe')
            f.flush()
            os.fsync(f.fileno())
        os.unlink(tmp_path)
        tmp_path = None
    except OSError as e:
        raise WrdsLatchError(
            f"WRDS retry latch storage is unavailable at {parent}: {e}"
        ) from e
    finally:
        if tmp_path is not None:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

# Substrings that identify a connection-level (not query-level) failure.
# A connection error is recoverable by reconnecting; a query error
# (syntax, permissions, missing table) is not and must surface as-is.
_CONN_ERROR_NEEDLES = (
    'ssl syscall error',
    'eof detected',
    'server closed the connection',
    'connection already closed',
    'connection is closed',
    'connection not open',
    'no connection to the server',
    'terminating connection',
    'connection reset',
    'could not receive data from server',
    'could not send data to server',
    "can't reconnect until invalid transaction is rolled back",
    'invalid transaction is rolled back',
    'this connection is closed',
    'pendingrollbackerror',
)


# Substrings that identify an authentication rejection. These are NOT
# recoverable: the credential is wrong or expired, so every retry is another
# failed login against WRDS — and WRDS locks the account after enough of them.
#
# This class exists because a PAM rejection arrives as a psycopg2
# OperationalError, which _is_conn_error() classifies as a recoverable dropped
# socket. That misclassification is a lockout engine: healthcheck() calls
# _recover() on every unhealthy ping, and _recover()'s Tier 2 and Tier 3 each
# perform a fresh login — so one ping costs two failed auths, while
# start_services.sh pings up to 120 times and wrds_start() another 120. A stale
# password could therefore fire hundreds of logins and lock the account before
# anything surfaced to the operator.
#
# Auth failures are therefore terminal and *latched* (WrdsState.auth_failed):
# once seen, the server stops attempting logins entirely and every command
# fails fast with an operator-escalation message. Clearing the latch is a
# deliberate operator action — fix the credential and approve one ``unblock``.
_AUTH_ERROR_NEEDLES = (
    'pam authentication failed',
    'password authentication failed',
    'authentication failed',
    'no password supplied',
    'role does not exist',
)


class WrdsAuthError(RuntimeError):
    """WRDS rejected the credential. Terminal — never retried."""


def _auth_guidance(exc):
    """Operator-facing message for a credential rejection."""
    return (
        f"WRDS rejected the credential for user {os.getenv('WRDS_USER')!r}: {exc}. "
        "NOT retrying — repeated attempts lock the WRDS account. "
        "OPERATOR: fix WRDS_PASS in .env (reset it at wrds-www.wharton.upenn.edu "
        "if it expired), then approve exactly one retry with "
        "`python code/utils/wrds_client.py unblock` after stopping this daemon "
        "from the host. The new process reloads .env while holding the singleton; "
        "a second rejection re-latches."
    )


def _ambiguous_login_guidance(exc):
    """Terminal guidance when a login attempt failed for an unknown reason."""
    return (
        f"WRDS connection attempt failed: {exc}. NOT retrying automatically — "
        "the failure could be an unrecognized credential rejection, and another "
        "attempt could lock the account. OPERATOR: diagnose the connection and "
        "approve exactly one retry with `python code/utils/wrds_client.py unblock`."
    )


def _is_auth_error(exc):
    """True if `exc` is WRDS refusing the credential.

    Must be checked BEFORE _is_conn_error(), which would otherwise absorb a
    PAM rejection as a recoverable socket drop and retry it into a lockout.

    Inspect the full exception chain.  `connect_wrds()` deliberately wraps a
    raw EOF/PAM failure in WrdsAuthError, and SQLAlchemy commonly stores the
    driver exception on ``orig``.  Looking only at ``str(exc)`` loses both
    shapes and lets the recovery path treat the wrapper as a fresh connection
    failure.
    """
    pending = [exc]
    seen = set()
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, (WrdsAuthError, EOFError)):
            return True
        msg = str(current).lower()
        if any(n in msg for n in _AUTH_ERROR_NEEDLES):
            return True
        for attr in ('__cause__', '__context__', 'orig'):
            nested = getattr(current, attr, None)
            if isinstance(nested, BaseException):
                pending.append(nested)
    return False


def _is_conn_error(exc):
    """True if `exc` looks like a dropped/poisoned connection (recoverable),
    as opposed to a query error (syntax/permission/missing table).

    Auth rejections are excluded: they are terminal, not recoverable."""
    if _is_auth_error(exc) or _is_query_cancel_error(exc):
        return False
    pending = [exc]
    seen = set()
    sa_conn_errors = ()
    try:
        import sqlalchemy.exc as sa_exc
        sa_conn_errors = (sa_exc.OperationalError,
                          sa_exc.InterfaceError,
                          sa_exc.PendingRollbackError)
    except Exception:
        pass
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, (WrdsImplicitReconnectError,) + sa_conn_errors):
            return True
        msg = str(current).lower()
        if any(n in msg for n in _CONN_ERROR_NEEDLES):
            return True
        for attr in ('__cause__', '__context__', 'orig'):
            nested = getattr(current, attr, None)
            if isinstance(nested, BaseException):
                pending.append(nested)
    return False


def _is_query_cancel_error(exc):
    """True for PostgreSQL statement cancellation/statement-timeout errors.

    SQLAlchemy wraps psycopg2 ``QueryCanceled`` in ``OperationalError``.  An
    OperationalError is normally a candidate for connection recovery, but a
    server-enforced statement timeout is a query-level failure: retrying the
    same SQL only doubles its work and a second cancellation must never be
    mistaken for a failed credential-bearing reconnect.
    """
    pending = [exc]
    seen = set()
    needles = (
        'canceling statement due to statement timeout',
        'cancelling statement due to statement timeout',
        'statement timeout',
        'query canceled',
        'query cancelled',
    )
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        if getattr(current, 'pgcode', None) == '57014':
            return True
        if type(current).__name__.lower() in (
                'querycanceled', 'querycancelederror',
                'querycancelled', 'querycancellederror'):
            return True
        if any(needle in str(current).lower() for needle in needles):
            return True
        for attr in ('__cause__', '__context__', 'orig'):
            nested = getattr(current, attr, None)
            if isinstance(nested, BaseException):
                pending.append(nested)
    return False


def _bounded_chunks(chunks):
    """Materialize a query only while its row/deep-memory budget is bounded."""
    import pandas as pd
    collected = []
    rows = 0
    memory = 0
    try:
        for chunk in chunks:
            rows += len(chunk)
            memory += int(chunk.memory_usage(index=True, deep=True).sum())
            if rows > MAX_RESULT_ROWS or memory > MAX_RESULT_MEMORY:
                raise ValueError(
                    "WRDS query result exceeds the shared-daemon limit; add "
                    "date/entity filters and cache bounded pulls separately")
            collected.append(chunk)
    finally:
        close = getattr(chunks, 'close', None)
        if close is not None:
            close()
    return (pd.concat(collected) if collected else pd.DataFrame())


def _validate_dataframe_budget(frame):
    memory = int(frame.memory_usage(index=True, deep=True).sum())
    if len(frame) > MAX_RESULT_ROWS or memory > MAX_RESULT_MEMORY:
        raise ValueError(
            "WRDS result exceeds the shared-daemon limit; add date/entity "
            "filters and cache bounded pulls separately")
    return frame


def _safe_raw_sql(db, sql, bounded=False):
    """Run a SQL query, falling back to a manual sqlalchemy path if wrds.raw_sql trips
    the sqlalchemy 2.x immutabledict bug.

    `wrds.Connection.raw_sql()` hardcodes `dtype_backend="numpy_nullable"`, which on
    some queries (LIKE, pg_tables, information_schema, certain GROUP BY ... COUNT(*))
    raises:
        sqlalchemy.cyextension.immutabledict.immutabledict is not a sequence
    The fallback bypasses pd.read_sql_query and constructs the DataFrame from raw
    tuple rows + explicit column list.
    """
    import pandas as pd
    try:
        if bounded:
            return _bounded_chunks(db.raw_sql(
                sql, chunksize=50_000, return_iter=True))
        return db.raw_sql(sql)
    except TypeError as e:
        if 'immutabledict' not in str(e):
            raise
    except AttributeError as e:
        # pandas >= 2.2 with wrds.raw_sql: pd.read_sql_query rejects the
        # raw psycopg2 Connection ("'Connection' object has no attribute 'cursor'")
        if "'Connection' object has no attribute 'cursor'" not in str(e):
            raise
    except Exception as e:
        if 'immutabledict' not in str(e):
            raise
    # Fallback path. Reuse the already-authenticated Connection: asking the
    # Engine for a new checkout can open another physical DB connection and
    # therefore another credential-bearing login outside the latch budget.
    from sqlalchemy import text
    result = db.connection.execute(text(sql))
    cols = list(result.keys())
    if not bounded:
        rows = [tuple(r) for r in result.fetchall()]
        return pd.DataFrame(rows, columns=cols)

    def fallback_chunks():
        while True:
            rows = result.fetchmany(50_000)
            if not rows:
                return
            yield pd.DataFrame([tuple(row) for row in rows], columns=cols)
    return _bounded_chunks(fallback_chunks())


def _set_query_deadline(db, timeout_seconds=QUERY_TIMEOUT_SECONDS):
    """Apply a bounded PostgreSQL deadline to the current transaction."""
    try:
        timeout_seconds = int(timeout_seconds)
    except (TypeError, ValueError) as e:
        raise ValueError('invalid WRDS query timeout') from e
    timeout_seconds = max(1, min(timeout_seconds, QUERY_TIMEOUT_SECONDS))
    from sqlalchemy import text
    # Integer interpolation only. SET LOCAL shares the transaction used by the
    # following read and PostgreSQL cancels it server-side even if the client
    # disappears or its local socket timeout fires.
    db.connection.execute(text(
        f'SET LOCAL statement_timeout = {timeout_seconds * 1000}'))


def _bounded_query(db, sql, timeout_seconds):
    """Run one sandbox query with a PostgreSQL deadline and result cap."""
    _set_query_deadline(db, timeout_seconds)
    return _safe_raw_sql(db, sql, bounded=True)


def _bounded_db_call(db, fn):
    _set_query_deadline(db)
    return fn(db)


def _connect_once(db):
    """Perform exactly one DB login, bypassing wrds.Connection.connect().

    The public ``connect()`` swallows its first exception and may prompt for
    credentials before attempting a second login. Automated recovery must see
    and latch the first rejection. Current wrds releases expose their
    one-attempt engine builder under this name-mangled method; fail closed if
    that contract changes.
    """
    _verify_wrds_runtime_contract()
    connect_once = getattr(db, '_Connection__make_sa_engine_conn', None)
    if connect_once is None:
        raise RuntimeError(
            "Unsupported wrds package: one-attempt connection method missing; "
            "refusing to call wrds.Connection.connect(), which may retry"
        )
    connect_once(raise_err=True)


def _verify_wrds_runtime_contract(wrds_module=None):
    """Fail closed unless the running dependency has the audited semantics.

    The requirement file is not enough: service startup can fall back to an
    ambient interpreter, and dependency installation is intentionally
    best-effort. This check runs before the write-ahead marker and before any
    credentials are touched, so a mismatched package cannot spend a login.
    """
    if wrds_module is None:
        import wrds as wrds_module
    expected = '3.5.0'
    expected_init_hash = '0030689f04717f424725616304a69f0f5e83e94f1fe9b7a4f6ac53859f7f008a'
    expected_primitive_hash = 'cec9f84ae2e75ee917af5f26e1e885a9efaa86a9ebc8ce939dad1e4af7ded3d0'
    try:
        distribution = importlib.metadata.distribution('wrds')
        actual = distribution.version
        distribution_files = {
            Path(distribution.locate_file(item)).resolve()
            for item in (distribution.files or ())
        }
        module_file = Path(wrds_module.__file__).resolve()
        constructor = wrds_module.Connection.__init__
        primitive = wrds_module.Connection._Connection__make_sa_engine_conn
        constructor_file = Path(inspect.getsourcefile(constructor)).resolve()
        primitive_file = Path(inspect.getsourcefile(primitive)).resolve()
        constructor_hash = hashlib.sha256(
            inspect.getsource(constructor).encode()).hexdigest()
        primitive_hash = hashlib.sha256(
            inspect.getsource(primitive).encode()).hexdigest()
    except Exception as e:
        raise RuntimeError(
            "cannot verify the installed wrds one-attempt login contract; "
            "refusing to connect"
        ) from e
    valid = (
        actual == expected and
        module_file in distribution_files and
        constructor_file in distribution_files and
        primitive_file in distribution_files and
        constructor_hash == expected_init_hash and
        primitive_hash == expected_primitive_hash
    )
    if not valid:
        raise RuntimeError(
            f"unsupported wrds runtime {actual!r}; expected audited {expected} "
            "with the audited constructor and one-attempt primitive hashes. "
            "Refusing to connect because a shadowed or changed API may retry."
        )


def _install_reconnect_guard(db):
    """Forbid SQLAlchemy from silently opening another physical connection.

    A SQLAlchemy ``Connection`` transparently reconnects when it has been
    invalidated. That would authenticate before ``WrdsState._recover()`` can
    write its login-attempt latch. The one explicit connect above is already
    write-ahead guarded; after it succeeds, this engine hook turns every
    implicit DBAPI reconnect into a typed connection error. Recovery then
    rebuilds the pool through the guarded one-attempt path.
    """
    import sqlalchemy as sa
    engine = getattr(db, 'engine', None)
    if engine is None:
        raise RuntimeError('WRDS connection has no engine to guard')
    if getattr(db, '_wrds_guarded_engine', None) is engine:
        return

    def refuse_implicit_connect(dialect, conn_rec, cargs, cparams):
        raise WrdsImplicitReconnectError(
            "blocked an implicit SQLAlchemy reconnect; routing through the "
            "write-ahead WRDS recovery latch"
        )

    sa.event.listen(engine, 'do_connect', refuse_implicit_connect)
    # Retain both the engine identity and listener for explicit lifecycle and
    # to avoid installing duplicates on the same pool.
    db._wrds_guarded_engine = engine
    db._wrds_reconnect_guard = refuse_implicit_connect


def connect_wrds(attempt_prearmed=False):
    """Establish WRDS connection (triggers Duo 2FA on first connect)."""
    import wrds
    # Keep PGPASSWORD for libpq compatibility, while also passing the password
    # explicitly to the current wrds package.
    wrds_pass = os.getenv('WRDS_PASS')
    if wrds_pass:
        os.environ['PGPASSWORD'] = wrds_pass
    try:
        _verify_wrds_runtime_contract(wrds)
        # Write-ahead, not after-the-fact: if this process dies anywhere in
        # Connection construction, Duo, engine setup, or the verification
        # query, a restart sees the marker and refuses another login.
        if not attempt_prearmed:
            _begin_login_attempt()
        db = wrds.Connection(
            wrds_username=os.getenv('WRDS_USER'),
            wrds_password=wrds_pass,
            autoconnect=False,
        )
        _connect_once(db)
        _install_reconnect_guard(db)
        db.load_library_list()
        _safe_raw_sql(db, 'SELECT 1')
        _clear_auth_block(preserve_compat=True)
    except Exception as e:
        # Any failed credential-bearing connection attempt is terminal until
        # an operator approves another. Known auth failures get precise
        # guidance; unknown failures are treated conservatively because an
        # automatic restart cannot prove they were harmless network errors.
        guidance = (_auth_guidance(e) if _is_auth_error(e)
                    else _ambiguous_login_guidance(e))
        raise WrdsAuthError(guidance) from e
    print(f"[wrds_server] Connected to WRDS as {os.getenv('WRDS_USER')}")
    return db


class WrdsState:
    """Holds the live wrds.Connection behind a lock and recovers it when the
    underlying socket is dropped/poisoned.

    The lock serializes both queries (wrds.raw_sql is not thread-safe) and
    recovery, so a reconnect triggered by one client is visible to all others.
    """

    def __init__(self, db):
        self.db = db
        self.lock = threading.Lock()
        # Sticky login-safety latch. Set on a known credential rejection or an
        # ambiguous failed reconnect; while set, no code path attempts another
        # login. Only an operator-approved unblock clears it.
        self.auth_failed = None

    # --- recovery ---------------------------------------------------------
    def _healthy(self, db):
        """Return True iff `SELECT 1` succeeds on `db`."""
        try:
            _safe_raw_sql(db, 'SELECT 1')
            return True
        except Exception as e:
            # A lazy driver may not authenticate until the first statement.
            # Never turn that rejection into False and then call _recover(),
            # which would spend another login before the real cause surfaces.
            self._latch_auth_failure(e)
            return False

    def _latch_auth_failure(self, exc):
        """Set the sticky auth latch and abort if `exc` is a credential
        rejection. Called from every recovery edge so the first rejection
        arms the latch before any later health probe can spend another login."""
        if not _is_auth_error(exc):
            return
        # connect_wrds() already translates the low-level rejection into the
        # complete operator message.  Preserve that wrapper verbatim instead
        # of recursively wrapping it every time it crosses a recovery layer.
        self.auth_failed = (str(exc) if isinstance(exc, WrdsAuthError)
                            else _auth_guidance(exc))
        try:
            _write_auth_block(self.auth_failed)
        except WrdsLatchError as storage_error:
            # The in-memory latch is already armed. Stay alive and fail every
            # request closed; never turn persistence trouble into another
            # login from this process.
            self.auth_failed += (
                f" LATCH STORAGE ERROR: {storage_error}. This server remains "
                "blocked; do not restart it automatically."
            )
        print(f"[wrds_server] AUTH FAILURE — halting retries. {self.auth_failed}",
              flush=True)
        raise WrdsAuthError(self.auth_failed) from exc

    def _latch_login_failure(self, exc):
        """Latch any failed credential-bearing reconnect, even if ambiguous."""
        if _is_auth_error(exc):
            self._latch_auth_failure(exc)
        self.auth_failed = _ambiguous_login_guidance(exc)
        try:
            _write_auth_block(self.auth_failed)
        except WrdsLatchError as storage_error:
            self.auth_failed += (
                f" LATCH STORAGE ERROR: {storage_error}. This server remains "
                "blocked; do not restart it automatically."
            )
        print(f"[wrds_server] LOGIN FAILURE — halting retries. {self.auth_failed}",
              flush=True)
        raise WrdsAuthError(self.auth_failed) from exc

    def _recover(self):
        """Restore a working connection. Caller must hold self.lock.

        Tiered, cheapest first. At most one credential-bearing reconnect is
        allowed: rollback uses the existing socket, then the pool rebuild gets
        one login. Any rebuild failure latches, including ambiguous failures.
        Returns a short string describing which tier succeeded.
        """
        # Latched credential rejection: every tier below would issue another
        # login, so refuse before spending one.
        if self.auth_failed:
            raise WrdsAuthError(self.auth_failed)

        db = self.db

        # Tier 1: roll back the poisoned transaction on the existing socket.
        # Handles the common case where the socket is alive but the
        # transaction is aborted.
        try:
            db.connection.rollback()
            if self._healthy(db):
                return 'rolled_back'
        except Exception as e:
            self._latch_auth_failure(e)

        # Tier 2: rebuild the engine/connection pool in place with exactly one
        # login attempt. Dispose the old pool first so the dead socket is not
        # leaked.
        try:
            try:
                db.connection.close()
            except Exception:
                pass
            try:
                if db.engine is not None:
                    db.engine.dispose()
            except Exception:
                pass
            _begin_login_attempt()
            _connect_once(db)  # exactly one login; public connect() may retry
            _install_reconnect_guard(db)
            # Rebuilding the connection does NOT refresh db.insp; the inspector still
            # points at the old, closed connection, which would re-poison
            # list_tables()/describe_table() immediately. Rebind it. Do NOT
            # swallow a failure here: if inspect() throws, the new connection
            # is itself bad, so the one-attempt handler latches and stops.
            import sqlalchemy as sa
            db.insp = sa.inspect(db.connection)
            if self._healthy(db):
                _clear_auth_block(preserve_compat=True)
                return 'pool_rebuilt'
            raise RuntimeError('connection remained unhealthy after one reconnect')
        except Exception as e:
            # This tier already spent the one permitted credential-bearing
            # attempt. Never fall through to a second full reconnect, even if
            # the exception text is not a recognized auth string.
            self._latch_login_failure(e)

    def run(self, fn):
        """Run fn(db) under the lock. On a connection-level error, recover
        once and retry. Returns (result, recovered: bool).

        Query-level errors (bad SQL, permissions) are not retried — they
        propagate so the caller sees the real error.
        """
        with self.lock:
            if self.auth_failed:
                raise WrdsAuthError(self.auth_failed)
            try:
                return fn(self.db), False
            except Exception as e:
                self._latch_auth_failure(e)
                if not _is_conn_error(e):
                    raise
                print(f"[wrds_server] connection error ({e}); recovering...")
                tier = self._recover()
                print(f"[wrds_server] recovered via {tier}; retrying query")
                try:
                    return fn(self.db), True
                except Exception as retry_error:
                    # Authentication can be lazy: rebuilding the pool may look
                    # successful and the rejection arrives only when the
                    # original operation is retried.  This is still the same
                    # one recovery attempt; latch it instead of letting the
                    # next health probe initiate another login.
                    if _is_auth_error(retry_error) or _is_conn_error(retry_error):
                        self._latch_login_failure(retry_error)
                    raise

    def healthcheck(self):
        """Exercise the connection with SELECT 1, recovering if wedged.
        Returns (ok: bool, detail: str). Used by the `ping` command so
        wrds_ping() reflects true connection health, not just socket
        liveness."""
        with self.lock:
            # Answer from the latch without touching the network. This is the
            # hot path for the lockout: every ping used to drive _recover().
            if self.auth_failed:
                return False, self.auth_failed
            try:
                if self._healthy(self.db):
                    return True, 'ok'
                tier = self._recover()
                return True, f'recovered:{tier}'
            except WrdsAuthError as e:
                return False, str(e)
            except Exception as e:
                return False, str(e)

    def unblock(self):
        """Operator-approved retry after a latched credential rejection.

        Spends EXACTLY ONE login attempt per approval. If WRDS refuses again the
        latch re-arms immediately, so an operator who approves without actually
        fixing the credential costs one attempt — never a loop. This is the only
        way the latch clears; nothing in the automated path can call it.

        Reloads .env with override first: the operator's fix landed in the file,
        while this process still holds the stale value it was spawned with.
        """
        with self.lock:
            if not self.auth_failed:
                return True, 'not blocked'

            load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
            wrds_pass = os.getenv('WRDS_PASS')
            if wrds_pass:
                os.environ['PGPASSWORD'] = wrds_pass

            # Cleared only for the duration of this single attempt.
            self.auth_failed = None
            try:
                # Atomically replace the terminal latch with the durable live
                # attempt. There is never a clear window that an automated
                # start could interpret as permission for another login.
                _begin_login_attempt(replace_blocked=True)
                try:
                    self.db.close()
                except Exception:
                    pass
                self.db = connect_wrds(attempt_prearmed=True)
                if not self._healthy(self.db):
                    raise RuntimeError('connection unhealthy after reconnect')
                print("[wrds_server] unblocked — credential accepted", flush=True)
                return True, 'reconnected'
            except Exception as e:
                if _is_auth_error(e):
                    self.auth_failed = (str(e) if isinstance(e, WrdsAuthError)
                                        else _auth_guidance(e))
                else:
                    self.auth_failed = (
                        f"Unblock attempt failed, and not on authentication: {e}. "
                        "Re-latched rather than retried — diagnose first, then "
                        "approve another unblock."
                    )
                try:
                    _write_auth_block(self.auth_failed)
                except WrdsLatchError as storage_error:
                    self.auth_failed += (
                        f" LATCH STORAGE ERROR: {storage_error}. This server "
                        "remains blocked; do not restart it automatically."
                    )
                print(f"[wrds_server] unblock failed — re-latched. {self.auth_failed}",
                      flush=True)
                return False, self.auth_failed

    def auth_blocked(self):
        """True once WRDS has refused the credential. Lets callers report an
        operator-actionable auth failure instead of a generic outage."""
        return self.auth_failed is not None


def _recv_exact(conn, size, deadline=None):
    chunks = []
    received = 0
    while received < size:
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('WRDS request frame deadline exceeded')
            conn.settimeout(remaining)
        chunk = conn.recv(size - received)
        if not chunk:
            raise ConnectionError(
                f'incomplete WRDS request frame ({received}/{size} bytes)')
        chunks.append(chunk)
        received += len(chunk)
    return b''.join(chunks)


def handle_client(conn, state):
    """Handle one query request; lifecycle control is never on the wire."""
    try:
        # A same-UID sandbox may connect, but must not be able to pin a daemon
        # thread forever with a partial frame or allocate from a forged size.
        conn.settimeout(CLIENT_IO_TIMEOUT)
        # Receive the full message (unsigned 64-bit network-order length).
        # v5's fixed-width ASCII header corrupted every frame at 100,000,000
        # bytes; v6 can represent the explicit 512 MiB wire-safety budget.
        request_deadline = time.monotonic() + CLIENT_IO_TIMEOUT
        raw_len = _recv_exact(conn, 8, request_deadline)
        msg_len = struct.unpack('!Q', raw_len)[0]
        if msg_len <= 0 or msg_len > MAX_MSG:
            raise ValueError(
                f'WRDS request frame must be 1..{MAX_MSG} bytes')

        chunks = []
        received = 0
        while received < msg_len:
            chunk = _recv_exact(
                conn, min(65536, msg_len - received), request_deadline)
            chunks.append(chunk)
            received += len(chunk)

        if received != msg_len:
            raise ValueError('incomplete WRDS request frame')

        request = json.loads(b''.join(chunks).decode())
        cmd = request.get('cmd', 'query')

        # The daemon outlives deployment updates. Refuse every command from an
        # old client before it can reach the database; conversely, updated
        # clients preflight this version so they never trust an old daemon's
        # hidden-retry behavior.
        if request.get('safety_protocol') != SAFETY_PROTOCOL:
            response = {
                'status': 'error',
                'msg': (
                    "WRDS client/server safety protocol mismatch. Do not query, "
                    "retry, or auto-restart. An operator must replace the stale "
                    "daemon with the deployed version."
                ),
                'error_kind': 'safety',
            }
            send_response(conn, response)
            return

        if cmd == 'safety_hello_v6':
            # Deliberately DB-free. Updated clients send this before `ping` so
            # probing a legacy daemon cannot invoke its vulnerable healthcheck.
            response = {'status': 'ok', 'msg': 'safety protocol confirmed'}
        elif cmd == 'safe_ping_v6':
            ok, detail = state.healthcheck()
            if ok:
                response = {'status': 'ok', 'msg': 'wrds_server alive',
                            'db': detail}
            elif state.auth_blocked():
                # Distinct kind so callers stop polling instead of looping a
                # readiness wait that can never succeed.
                response = {'status': 'error',
                            'msg': detail,
                            'error_kind': 'auth'}
            else:
                response = {'status': 'error',
                            'msg': f'connection unhealthy: {detail}',
                            'error_kind': 'connection'}
        elif cmd == 'safe_query_v6':
            sql = request['sql']
            query_timeout = request.get('timeout', QUERY_TIMEOUT_SECONDS)
            df, recovered = state.run(
                lambda db: _bounded_query(db, sql, query_timeout))
            # Convert to JSON-serializable format
            response = {
                'status': 'ok',
                'columns': list(df.columns),
                'data': df.to_json(orient='split', date_format='iso'),
                'shape': list(df.shape),
                'recovered': recovered,
            }
        elif cmd == 'safe_list_tables_v6':
            lib = request['library']
            tables, recovered = state.run(
                lambda db: _bounded_db_call(
                    db, lambda active: active.list_tables(library=lib)))
            response = {'status': 'ok', 'tables': tables,
                        'recovered': recovered}
        elif cmd == 'safe_list_libraries_v6':
            libraries, recovered = state.run(
                lambda db: _bounded_db_call(
                    db, lambda active: active.list_libraries()))
            response = {'status': 'ok', 'libraries': libraries,
                        'recovered': recovered}
        elif cmd == 'safe_get_table_v6':
            kwargs = request.get('kwargs') or {}
            requested_rows = kwargs.get('obs')
            if requested_rows is None:
                requested_rows = kwargs.get('rows')
            try:
                requested_rows = int(requested_rows)
            except (TypeError, ValueError) as e:
                raise ValueError(
                    'WRDS get_table requires an explicit positive row limit') from e
            if not 1 <= requested_rows <= MAX_GET_TABLE_ROWS:
                raise ValueError(
                    f'WRDS get_table row limit must be 1..{MAX_GET_TABLE_ROWS}; '
                    'use filtered wrds_query pulls for larger extracts')
            df, recovered = state.run(
                lambda db: _bounded_db_call(
                    db, lambda active: active.get_table(
                        request['library'], request['table'], **kwargs)))
            df = _validate_dataframe_budget(df)
            response = {
                'status': 'ok',
                'data': df.to_json(orient='split', date_format='iso'),
                'recovered': recovered,
            }
        elif cmd == 'safe_describe_v6':
            lib = request['library']
            table = request['table']
            desc, recovered = state.run(
                lambda db: _bounded_db_call(
                    db, lambda active: active.describe_table(lib, table)))
            response = {
                'status': 'ok',
                'data': desc.to_json(orient='split', date_format='iso'),
                'recovered': recovered,
            }
        else:
            response = {'status': 'error', 'msg': f'unknown command: {cmd}'}

        send_response(conn, response)
    except Exception as e:
        try:
            # Three-way, not two: _is_conn_error() deliberately excludes auth
            # rejections, so without this branch they would be mislabelled
            # 'query' and read as a bad-SQL problem by the caller.
            if _is_auth_error(e) or isinstance(e, WrdsAuthError):
                error_kind = 'auth'
            elif _is_conn_error(e):
                error_kind = 'connection'
            else:
                error_kind = 'query'
            send_response(conn, {'status': 'error', 'msg': str(e),
                                 'error_kind': error_kind})
        except Exception:
            pass
    finally:
        conn.close()

def send_response(conn, response):
    """Send a binary-length-prefixed JSON response."""
    response = {**response, 'safety_protocol': SAFETY_PROTOCOL}
    data = json.dumps(response, default=str).encode()
    if len(data) > MAX_RESPONSE:
        data = json.dumps({
            'status': 'error',
            'error_kind': 'query',
            'msg': ('WRDS response exceeds the 512 MiB wire-safety bound; '
                    'use documented deterministic windowed pulls'),
            'safety_protocol': SAFETY_PROTOCOL,
        }).encode()
    conn.sendall(struct.pack('!Q', len(data)))
    conn.sendall(data)


def _bind_unix_server():
    """Bind cross-sandbox transport after the caller owns ``LOCK_FILE``.

    A live socket is never unlinked. The atomic singleton marker serializes
    stale cleanup, and inode identity keeps shutdown from deleting a
    successor's endpoint after an external operator repair.
    """
    if not hasattr(socket, 'AF_UNIX'):
        raise WrdsLatchError('WRDS sandbox transport requires AF_UNIX support')
    _prepare_auth_block_dir()
    try:
        info = os.lstat(SOCKET_FILE)
    except FileNotFoundError:
        info = None
    if info is not None:
        if not stat.S_ISSOCK(info.st_mode):
            raise WrdsLatchError(
                f"WRDS socket path is not a socket: {SOCKET_FILE}")
        if hasattr(os, 'getuid') and info.st_uid != os.getuid():
            raise WrdsLatchError(
                f"WRDS socket is not owned by this user: {SOCKET_FILE}")
        probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        probe.settimeout(0.25)
        try:
            probe.connect(SOCKET_FILE)
        except OSError as e:
            if e.errno not in (errno.ECONNREFUSED, errno.ENOENT):
                raise WrdsLatchError(
                    f"cannot prove existing WRDS socket is stale: {e}"
                ) from e
        else:
            raise WrdsInstanceBusy(
                "a live WRDS Unix socket exists without the current lock; "
                "stop and upgrade that daemon explicitly"
            )
        finally:
            probe.close()
        try:
            current = os.lstat(SOCKET_FILE)
        except FileNotFoundError:
            current = None
        if current is not None:
            if _socket_identity(current) != _socket_identity(info):
                raise WrdsLatchError(
                    "WRDS socket changed during stale cleanup; refusing to unlink")
            os.unlink(SOCKET_FILE)

    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    old_umask = os.umask(0o177)
    try:
        listener.bind(SOCKET_FILE)
    except Exception:
        listener.close()
        raise
    finally:
        os.umask(old_umask)
    os.chmod(SOCKET_FILE, 0o600)
    listener.listen(5)
    info = os.lstat(SOCKET_FILE)
    return listener, _socket_identity(info)


def _socket_identity(info):
    """Identity robust to immediate inode-number reuse after replacement."""
    return (info.st_dev, info.st_ino, info.st_ctime_ns)


def _unlink_socket_if_identity(identity):
    """Remove only the exact socket inode created by this daemon."""
    if identity is None:
        return False
    try:
        info = os.lstat(SOCKET_FILE)
        if _socket_identity(info) != identity:
            return False
        os.unlink(SOCKET_FILE)
        return True
    except (FileNotFoundError, OSError):
        return False


def _legacy_server_pids():
    """Find same-user WRDS server scripts independent of network namespace."""
    def is_server_argv(args):
        """Recognize the released Python launch shape, not arbitrary mentions."""
        if len(args) < 2:
            return False
        interpreter = os.path.basename(args[0]).lower()
        if not (interpreter.startswith('python') or
                interpreter.startswith('pypy')):
            return False
        index = 1
        # Released launchers may use unbuffered/isolated Python switches before
        # the script. -c and -m are intentionally not skipped: a filename in
        # their program arguments is not an executed server script.
        no_arg_switches = {
            '-b', '-bb', '-B', '-d', '-E', '-I', '-O', '-OO', '-q', '-s',
            '-S', '-u', '-v', '-x', '-Xdev',
        }
        while index < len(args) and args[index] in no_arg_switches:
            index += 1
        return (index < len(args) and
                os.path.basename(args[index]) == 'wrds_server.py')

    found = []
    proc_root = Path('/proc')
    if proc_root.is_dir():
        try:
            entries = list(proc_root.iterdir())
        except OSError as e:
            raise WrdsLatchError(
                f'cannot enumerate processes for legacy WRDS safety: {e}') from e
        for entry in entries:
            if not entry.name.isdigit() or int(entry.name) == os.getpid():
                continue
            try:
                if (hasattr(os, 'getuid') and
                        entry.stat().st_uid != os.getuid()):
                    continue
                args = [a.decode(errors='replace') for a in
                        (entry / 'cmdline').read_bytes().split(b'\0') if a]
            except (FileNotFoundError, ProcessLookupError):
                # The process exited between directory enumeration and read.
                continue
            except PermissionError as e:
                raise WrdsLatchError(
                    f'cannot inspect same-user process {entry.name}: {e}') from e
            except OSError as e:
                raise WrdsLatchError(
                    f'process discovery failed at {entry}: {e}') from e
            if is_server_argv(args):
                found.append(int(entry.name))
        return sorted(found)

    # macOS/other fallback. Exact token parsing avoids matching an editor or
    # grep whose free-form command merely mentions the filename.
    try:
        result = subprocess.run(
            ['/bin/ps', '-axo', 'pid=,uid=,command='], capture_output=True,
            text=True, timeout=5, check=False)
    except Exception as e:
        raise WrdsLatchError(
            f'cannot enumerate processes for legacy WRDS safety: {e}') from e
    if result.returncode != 0:
        raise WrdsLatchError(
            'process enumeration failed for legacy WRDS safety: ' +
            (result.stderr.strip() or f'ps exit {result.returncode}'))
    for line in result.stdout.splitlines():
        pieces = line.strip().split(None, 2)
        if len(pieces) != 3:
            continue
        try:
            pid, uid = map(int, pieces[:2])
            args = shlex.split(pieces[2])
        except (ValueError, TypeError):
            continue
        if (pid != os.getpid() and
                (not hasattr(os, 'getuid') or uid == os.getuid()) and
                is_server_argv(args)):
            found.append(pid)
    return sorted(found)


def _cwd_is_deployed_wrds_runtime(cwd):
    """Whether ``cwd`` is inside an assembled deployment with WRDS support."""
    cwd = Path(cwd)
    for candidate in (cwd, *cwd.parents):
        if ((candidate / '.deploy_manifest.json').is_file() and
                (candidate / 'code' / 'utils' / 'wrds_client.py').is_file()):
            return True
    return False


def _process_is_deployed_wrds_runtime(entry, proc_root):
    """Classify a process before inspecting its protected namespace links.

    Linux session helpers such as systemd's same-UID ``(sd-pam)`` deliberately
    deny both ``cwd`` and namespace reads even to their owner.  They are not a
    released pipeline runtime and must not make every v5 daemon unstartable.
    Walk the parent chain until a deployment cwd is found or PID 1 is reached:
    a released client can change to /tmp while still resolving wrds_server.py
    from its deployed ``__file__``. Opaque children are handled by the same
    ancestry walk, so one descended from a deployed launcher remains inside
    the fail-closed gate.
    """
    current = entry
    seen = set()
    for _ in range(64):
        try:
            pid = int(current.name)
        except ValueError:
            return False
        if pid in seen or pid <= 1:
            return False
        seen.add(pid)
        try:
            cwd = os.readlink(current / 'cwd')
        except (FileNotFoundError, ProcessLookupError):
            return False
        except PermissionError:
            cwd = None
        except OSError as e:
            raise WrdsLatchError(
                f'cannot inspect same-user process cwd {pid}: {e}') from e
        if cwd is not None and _cwd_is_deployed_wrds_runtime(cwd):
            return True
        try:
            status_text = (current / 'status').read_text(
                encoding='utf-8', errors='replace')
            parent_line = next(
                line for line in status_text.splitlines()
                if line.startswith('PPid:'))
            parent_pid = int(parent_line.split(':', 1)[1].strip())
        except (FileNotFoundError, ProcessLookupError):
            return False
        except (OSError, StopIteration, ValueError) as e:
            raise WrdsLatchError(
                f'cannot classify same-user process ancestry {pid}: {e}') from e
        current = proc_root / str(parent_pid)
    raise WrdsLatchError(
        f'cannot classify same-user process ancestry from {entry.name}')


def _foreign_network_namespace_pids():
    """Find live same-UID processes outside this Linux network namespace.

    A released sandbox client checks the cache latch before it spawns its v2
    server. It can therefore be paused after that check while no server process
    exists yet. Requiring the first v5 upgrade to occur with every old network
    namespace quiescent closes that delayed-Popen race; processes created after
    guard publication necessarily observe the guard before their own spawn.
    Host-namespace released servers remain excluded by the reserved TCP port.
    """
    proc_root = Path('/proc')
    self_ns = proc_root / 'self' / 'ns' / 'net'
    if not self_ns.exists():
        return []  # macOS/other platforms have one host loopback namespace.
    try:
        own = os.stat(self_ns)
        entries = list(proc_root.iterdir())
    except OSError as e:
        raise WrdsLatchError(
            f'cannot enumerate network namespaces for WRDS upgrade safety: {e}') from e
    own_identity = (own.st_dev, own.st_ino)
    found = []
    for entry in entries:
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            if (hasattr(os, 'getuid') and entry.stat().st_uid != os.getuid()):
                continue
            # Scope the upgrade gate before touching namespace links. Common
            # same-user system helpers intentionally deny ns/net reads; only a
            # deployed runtime can carry the released delayed-Popen race.
            if not _process_is_deployed_wrds_runtime(entry, proc_root):
                continue
            candidate = os.stat(entry / 'ns' / 'net')
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as e:
            raise WrdsLatchError(
                f'cannot inspect same-user network namespace {entry.name}: {e}') from e
        except OSError as e:
            raise WrdsLatchError(
                f'network-namespace discovery failed at {entry}: {e}') from e
        if (candidate.st_dev, candidate.st_ino) != own_identity:
            found.append(int(entry.name))
    return sorted(found)


def _refuse_live_legacy_processes():
    pids = _legacy_server_pids()
    if pids:
        raise WrdsInstanceBusy(
            "older WRDS server process(es) still live across namespaces: " +
            ', '.join(map(str, pids)))
    namespace_pids = _foreign_network_namespace_pids()
    if namespace_pids:
        raise WrdsInstanceBusy(
            "foreign network namespace(s) are still active during the first "
            "WRDS protocol upgrade; stop old sandbox runs before starting WRDS: " +
            ', '.join(map(str, namespace_pids)))


def _bind_legacy_refusal_listener():
    """Reserve released v2 TCP transport and answer only upgrade refusals."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(('127.0.0.1', PORT))
        listener.listen(5)
    except OSError as e:
        listener.close()
        raise WrdsInstanceBusy(
            f"legacy WRDS TCP port 127.0.0.1:{PORT} is already owned; "
            "stop the older daemon before upgrading") from e
    return listener


def _legacy_refusal_loop(listener):
    """Never dispatch TCP commands; only tell released clients to upgrade.

    This retired endpoint deliberately retains the old ASCII header so a v2-v5
    client can decode the refusal. The live Unix/query-bridge endpoints use
    v6's binary header exclusively.
    """
    while True:
        try:
            conn, _ = listener.accept()
        except OSError:
            return
        try:
            conn.settimeout(1)
            raw_len = conn.recv(8)
            if raw_len:
                response = {
                    'status': 'error',
                    'error_kind': 'safety',
                    'msg': ('WRDS TCP transport is retired. Stop this old '
                            'runtime and relaunch an updated deployment.'),
                }
                payload = json.dumps({
                    **response, 'safety_protocol': SAFETY_PROTOCOL,
                }).encode()
                conn.sendall(f'{len(payload):8d}'.encode('ascii'))
                conn.sendall(payload)
        except Exception:
            pass
        finally:
            conn.close()


def _open_compat_dir(create):
    """Open the old cache directory by descriptor without following symlinks."""
    flags = (os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) |
             getattr(os, 'O_NOFOLLOW', 0))
    parent = os.path.abspath(os.path.dirname(CACHE_AUTH_BLOCK_FILE))
    try:
        fd = os.open(os.path.sep, flags)
        for component in Path(parent).parts[1:]:
            if create:
                try:
                    os.mkdir(component, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        info = os.fstat(fd)
        if (not stat.S_ISDIR(info.st_mode) or
                (hasattr(os, 'getuid') and info.st_uid != os.getuid()) or
                info.st_mode & 0o022):
            raise OSError('legacy compatibility directory failed owner/type checks')
        return fd
    except Exception:
        if 'fd' in locals():
            try:
                os.close(fd)
            except OSError:
                pass
        raise


def _compat_guard_directory_locked():
    """True only for the v5-owned read/execute-only compatibility directory."""
    dir_fd = None
    try:
        dir_fd = _open_compat_dir(create=False)
        return stat.S_IMODE(os.fstat(dir_fd).st_mode) == 0o500
    except OSError:
        return False
    finally:
        if dir_fd is not None:
            os.close(dir_fd)


def _write_compat_guard():
    """Publish, without replacement, the latch released starters honor.

    The cache pathname is legacy API surface, not v5 authority. Publication is
    no-clobber so an older process's concurrent write-ahead login marker can
    never be erased. While the daemon owns the guard, the final directory is
    mode 0500: ordinary cache cleanup and released code cannot unlink it.
    """
    birth = _process_start_token(os.getpid())
    if not birth:
        raise WrdsLatchError('cannot identify compatibility-guard owner')
    message = (f"{COMPAT_ACTIVE_PREFIX}{os.getpid()} start={birth}\n"
               "A v5 host daemon is active; released clients must not start "
               "another WRDS session.")
    basename = os.path.basename(CACHE_AUTH_BLOCK_FILE)
    dir_fd = None
    tmp_name = f'.{basename}.{os.getpid()}.{threading.get_ident()}.tmp'
    try:
        dir_fd = _open_compat_dir(create=True)
        os.fchmod(dir_fd, 0o700)
        try:
            fd = os.open(tmp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                         0o600, dir_fd=dir_fd)
        except FileExistsError:
            os.unlink(tmp_name, dir_fd=dir_fd)
            fd = os.open(tmp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                         0o600, dir_fd=dir_fd)
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(message)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp_name, basename, src_dir_fd=dir_fd,
                    dst_dir_fd=dir_fd, follow_symlinks=False)
        except FileExistsError:
            # Never replace: this may be a released daemon's write-ahead auth
            # record. The post-publication verifier distinguishes a retained
            # compatibility marker from real legacy auth state.
            pass
        os.unlink(tmp_name, dir_fd=dir_fd)
        tmp_name = None
        os.fsync(dir_fd)
        info = os.stat(basename, dir_fd=dir_fd, follow_symlinks=False)
        guard_fd = os.open(
            basename, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0), dir_fd=dir_fd)
        try:
            guard_info = os.fstat(guard_fd)
            if (not stat.S_ISREG(guard_info.st_mode) or
                    (hasattr(os, 'getuid') and
                     guard_info.st_uid != os.getuid()) or
                    guard_info.st_mode & 0o022):
                raise OSError(
                    'released-client compatibility guard failed owner/type checks')
            # Directory mode 0500 blocks unlink/replace; file mode 0400 also
            # blocks an already-resolved same-UID cache writer from truncating
            # the marker in place. Updated sandboxes deny this path as a
            # second, kernel-enforced boundary.
            os.fchmod(guard_fd, 0o400)
            info = os.fstat(guard_fd)
        finally:
            os.close(guard_fd)
        parent_info = os.fstat(dir_fd)
        current_parent = os.stat(os.path.dirname(CACHE_AUTH_BLOCK_FILE),
                                 follow_symlinks=False)
        if ((parent_info.st_dev, parent_info.st_ino) !=
                (current_parent.st_dev, current_parent.st_ino)):
            raise OSError('legacy compatibility directory changed during publish')
        os.fchmod(dir_fd, 0o500)
        return _lock_identity(info)
    except OSError as e:
        raise WrdsLatchError(
            f"cannot publish released-client compatibility guard: {e}") from e
    finally:
        if dir_fd is not None:
            if tmp_name is not None:
                try:
                    os.unlink(tmp_name, dir_fd=dir_fd)
                except OSError:
                    pass
            try:
                os.stat(basename, dir_fd=dir_fd, follow_symlinks=False)
                os.fchmod(dir_fd, 0o500)
            except OSError:
                pass
            os.close(dir_fd)


def _remove_compat_guard(identity):
    if identity is None:
        return False
    dir_fd = None
    try:
        dir_fd = _open_compat_dir(create=False)
        os.fchmod(dir_fd, 0o700)
        basename = os.path.basename(CACHE_AUTH_BLOCK_FILE)
        info = os.stat(basename, dir_fd=dir_fd, follow_symlinks=False)
        if _lock_identity(info) != identity:
            os.fchmod(dir_fd, 0o500)
            return False
        os.unlink(basename, dir_fd=dir_fd)
        os.fsync(dir_fd)
        return True
    except OSError:
        return False
    finally:
        if dir_fd is not None:
            os.close(dir_fd)


def _verify_compat_guard(accepted_legacy_message=None):
    """Fail closed if a released starter won the publication race."""
    message = _read_latch_file(CACHE_AUTH_BLOCK_FILE)
    if message is None:
        raise WrdsLatchError(
            'released-client compatibility guard disappeared after publication')
    if message.startswith(COMPAT_ACTIVE_PREFIX):
        return
    if (accepted_legacy_message is not None and
            message == accepted_legacy_message):
        # Operator retry: the exact terminal record already copied into
        # protected state doubles as the no-gap guard for released clients.
        return
    # Preserve the old process's write-ahead state in protected v5 storage
    # before refusing our own login. Do not clear or overwrite the cache copy.
    _write_auth_block(message)
    raise WrdsInstanceBusy(
        'a released WRDS starter published authentication state concurrently')


def _adopted_legacy_guard():
    """Return a crash-surviving, already-resolved old guard, if present."""
    if not _compat_guard_directory_locked():
        return None
    message = _read_latch_file(CACHE_AUTH_BLOCK_FILE)
    if message and not message.startswith(COMPAT_ACTIVE_PREFIX):
        # Protected auth state was checked first and is clear. The only v5 path
        # that leaves this terminal-looking cache record under mode 0500/0400
        # is a verified operator retry retaining it as the old-client guard.
        return message
    return None


def main(operator_unblock=False):
    # Filesystem creation, not loopback TCP, is the authoritative singleton:
    # each sandbox has its own network namespace but all see this host-owned
    # state directory.  Never trust a PID file as a liveness oracle.
    try:
        instance_lock = _acquire_instance_lock()
    except WrdsInstanceBusy as e:
        print(f"[wrds_server] Already starting/running: {e}")
        sys.exit(3)
    except WrdsLatchError as e:
        print(f"[wrds_server] SINGLETON LOCK UNAVAILABLE — refusing to connect: {e}",
              flush=True)
        sys.exit(2)

    try:
        _refuse_live_legacy_processes()
        legacy_tcp_listener = _bind_legacy_refusal_listener()
    except WrdsInstanceBusy as e:
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] LEGACY DAEMON DETECTED — refusing to connect: {e}",
              flush=True)
        sys.exit(4)
    except WrdsLatchError as e:
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] PROCESS SAFETY CHECK FAILED — refusing to connect: {e}",
              flush=True)
        sys.exit(2)
    legacy_thread = threading.Thread(
        target=_legacy_refusal_loop, args=(legacy_tcp_listener,), daemon=True)
    legacy_thread.start()

    # Persisted credential latch. Checked before binding or connecting: a
    # restart must NOT be a free way around the operator gate, or the automated
    # path (start_services.sh at every pipeline launch) would spend a login per
    # session against a credential already known to be rejected.
    try:
        blocked = _read_auth_block()
        if not blocked:
            _verify_auth_block_storage()
    except WrdsLatchError as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] RETRY LATCH UNAVAILABLE — refusing to connect: {e}",
              flush=True)
        sys.exit(2)
    operator_retry = bool(blocked and operator_unblock)
    if blocked and not operator_retry:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] AUTH BLOCKED — refusing to start. {blocked}",
              flush=True)
        sys.exit(2)

    try:
        adopted_legacy_guard = (
            _adopted_legacy_guard() if not blocked else None)
    except WrdsLatchError as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] LEGACY COMPATIBILITY STATE UNAVAILABLE: {e}",
              flush=True)
        sys.exit(5)

    # Released v2/v3 starters already consult this cache latch before binding
    # their namespace-local transports. Publish it after any real old latch was
    # copied into protected state, then rescan processes to close the
    # scan-to-publish race. It remains for this daemon's full lifetime.
    try:
        compat_identity = _write_compat_guard()
    except WrdsLatchError as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] LEGACY COMPATIBILITY STATE UNAVAILABLE: {e}",
              flush=True)
        sys.exit(5)
    try:
        _refuse_live_legacy_processes()
        accepted_guard = (blocked if operator_retry else adopted_legacy_guard)
        _verify_compat_guard(accepted_guard)
    except WrdsInstanceBusy as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] LEGACY DAEMON DETECTED — refusing to connect: {e}",
              flush=True)
        sys.exit(4)
    except WrdsLatchError as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] LEGACY COMPATIBILITY STATE UNAVAILABLE: {e}",
              flush=True)
        sys.exit(5)

    # Bind transport before the expensive WRDS connect + Duo. A single private
    # Unix endpoint is global across network namespaces and, unlike loopback
    # TCP, carries filesystem owner permissions and exposes no admin commands.
    try:
        unix_server, unix_identity = _bind_unix_server()
    except (OSError, WrdsLatchError, WrdsInstanceBusy) as e:
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        print(f"[wrds_server] Cannot establish sandbox transport: {e}",
              flush=True)
        sys.exit(1)
    try:
        _write_pid_file()
    except WrdsLatchError as e:
        print(f"[wrds_server] PID STATE UNAVAILABLE — refusing to connect: {e}",
              flush=True)
        unix_server.close()
        _unlink_socket_if_identity(unix_identity)
        legacy_tcp_listener.close()
        _remove_lock_if_identity(instance_lock)
        sys.exit(2)

    if operator_retry:
        try:
            _begin_login_attempt(replace_blocked=True)
            print("[wrds_server] Operator approved one credential retry",
                  flush=True)
        except WrdsLatchError as e:
            print(f"[wrds_server] UNBLOCK FAILED — latch remains armed: {e}",
                  flush=True)
            unix_server.close()
            _unlink_socket_if_identity(unix_identity)
            legacy_tcp_listener.close()
            _remove_lock_if_identity(instance_lock)
            sys.exit(2)

    # Connect to WRDS (triggers Duo on first connect)
    print("[wrds_server] Connecting to WRDS (check Duo notification)...")
    try:
        state = WrdsState(connect_wrds(attempt_prearmed=operator_retry))
    except WrdsAuthError as e:
        # Keep owning the endpoint with an in-memory latch even if persistence has
        # just failed. That prevents an automated supervisor from replacing us
        # with a fresh process and spending another login. The operator can
        # still unblock this state in place after diagnosing the credential.
        state = WrdsState(None)
        state.auth_failed = str(e)
        try:
            _write_auth_block(state.auth_failed)
        except WrdsLatchError as storage_error:
            state.auth_failed += (
                f" LATCH STORAGE ERROR: {storage_error}. This server remains "
                "blocked; do not restart it automatically."
            )
        print(f"[wrds_server] AUTH BLOCKED — staying alive without retrying. "
              f"{state.auth_failed}", flush=True)
    print(f"[wrds_server] Listening on {SOCKET_FILE} "
          f"(TCP {PORT} is upgrade-refusal only)")

    def _remove_pid_if_ours():
        # Only remove the pid file if it still records THIS process — a
        # racing server that took over the port must not have its pid
        # file deleted out from under it.
        try:
            with open(PID_FILE) as f:
                if int(f.read().strip()) == os.getpid():
                    os.remove(PID_FILE)
        except (OSError, ValueError):
            pass

    def _remove_unix_socket_if_ours():
        _unlink_socket_if_identity(unix_identity)

    def cleanup(signum, frame):
        print("\n[wrds_server] Shutting down...")
        try:
            state.db.close()
        except Exception:
            pass
        if unix_server is not None:
            unix_server.close()
        legacy_tcp_listener.close()
        _remove_compat_guard(compat_identity)
        _remove_unix_socket_if_ours()
        _remove_pid_if_ours()
        _remove_lock_if_identity(instance_lock)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    def accept_loop(listener):
        slots = threading.BoundedSemaphore(MAX_CLIENT_THREADS)

        def serve_one(conn):
            try:
                handle_client(conn, state)
            finally:
                slots.release()

        while True:
            try:
                conn, _ = listener.accept()
                if not slots.acquire(blocking=False):
                    conn.close()
                    continue
                t = threading.Thread(target=serve_one, args=(conn,))
                t.daemon = True
                t.start()
            except OSError as e:
                if e.errno in (9, 22):  # listener closed during shutdown
                    return
                print(f"[wrds_server] Error: {e}")

    accept_loop(unix_server)

if __name__ == '__main__':
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and
                             sys.argv[1] != '--operator-unblock'):
        print(f"usage: {sys.argv[0]} [--operator-unblock]", file=sys.stderr)
        sys.exit(64)
    main(operator_unblock=(len(sys.argv) == 2))
