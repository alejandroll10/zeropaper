"""Persistent WRDS connection server.

Connects to WRDS once (triggers Duo 2FA once), then serves queries
over a local TCP socket. Scripts send SQL queries and get back
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

The server is per-host (one process per machine on the fixed port). Its
PID file is therefore host-global ($XDG_RUNTIME_DIR or the system temp
dir, named .wrds_server_<port>.pid), not next to this file — see
_pid_file_path().

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
from pathlib import Path
from dotenv import load_dotenv

_DOTENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=_DOTENV_PATH)

HOST = '127.0.0.1'
PORT = 23847  # arbitrary high port
# Bump whenever daemon-side login/recovery safety semantics change. This must
# remain a literal independent of wrds_client's copy so stale daemons mismatch.
SAFETY_PROTOCOL = 'wrds-auth-latch-v2'

def _pid_file_path():
    """Host-global PID path, keyed by port.

    The WRDS server is per-host (one process per machine on PORT), so its
    PID file must be host-global too — NOT next to __file__. A per-directory
    pid file meant each deployed project tracked only the server it
    personally started: project B's restart-guard never saw project A's
    server, and running the server from the template repo polluted the
    source tree. A single host path fixes both: the restart-guard works
    across every project sharing the one server, and no repo is touched.
    Prefer $XDG_RUNTIME_DIR (per-user, tmpfs, auto-cleaned on logout);
    fall back to the system temp dir.
    """
    base = os.environ.get('XDG_RUNTIME_DIR') or tempfile.gettempdir()
    return os.path.join(base, f'.wrds_server_{PORT}.pid')

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
    user's durable cache directory. It clears only after a verified login
    approved through ``unblock``; ordinary lifecycle events never clear it.
    """
    base = os.path.join(os.path.expanduser('~'), '.cache', 'zeropaper', 'wrds')
    return os.path.join(base, f'wrds_server_{PORT}.authblock')


PID_FILE = _pid_file_path()
AUTH_BLOCK_FILE = _auth_block_path()
LEGACY_AUTH_BLOCK_FILE = os.path.join(
    os.environ.get('XDG_RUNTIME_DIR') or tempfile.gettempdir(),
    f'.wrds_server_{PORT}.authblock')
MAX_MSG = 10 * 1024 * 1024  # 10MB max message size
LOGIN_ATTEMPT_PREFIX = 'WRDS_LOGIN_ATTEMPT_IN_PROGRESS pid='


class WrdsLatchError(RuntimeError):
    """The persistent retry latch cannot be read or written safely."""


class WrdsImplicitReconnectError(ConnectionError):
    """SQLAlchemy tried to open a DB connection outside the guarded path."""


def _prepare_auth_block_dir():
    """Create and validate the private durable latch directory."""
    parent = os.path.dirname(AUTH_BLOCK_FILE)
    try:
        os.makedirs(parent, mode=0o700, exist_ok=True)
        flags = (os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) |
                 getattr(os, 'O_NOFOLLOW', 0))
        fd = os.open(parent, flags)
    except OSError as e:
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
    """Read/migrate the durable latch, failing closed on legacy state."""
    _prepare_auth_block_dir()
    message = _read_latch_file(AUTH_BLOCK_FILE)
    if message is not None:
        return message

    # v2.22.1 stored its latch beside the runtime PID file. During an upgrade,
    # ignoring that known rejection would spend a fresh login. Copy it into
    # durable storage atomically, but leave the legacy copy until a verified or
    # operator-approved clear so an older daemon also remains blocked.
    legacy = _read_latch_file(LEGACY_AUTH_BLOCK_FILE)
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


def _clear_auth_block():
    """Remove the latch after verified success or operator-approved unblock."""
    removed_parents = set()
    for path in (AUTH_BLOCK_FILE, LEGACY_AUTH_BLOCK_FILE):
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


def _begin_login_attempt():
    """Write the durable guard that must precede every credentialed login.

    It is deliberately indistinguishable from a terminal latch after this
    process dies. Only a fully verified connection clears it. While this PID
    is alive, clients recognize it as an in-progress startup and may wait for
    Duo without interpreting the marker as a rejection.
    """
    existing = _read_auth_block()
    if existing:
        raise WrdsLatchError(
            "refusing WRDS login because a retry latch already exists: "
            f"{existing}"
        )
    marker = (
        f"{LOGIN_ATTEMPT_PREFIX}{os.getpid()}\n"
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
        pid = int(first_line[len(LOGIN_ATTEMPT_PREFIX):])
        os.kill(pid, 0)
    except (OSError, ValueError):
        return False
    return True


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
        "`python code/utils/wrds_client.py unblock` — the server reloads .env "
        "and reconnects in place, no restart needed. A second rejection re-latches."
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
    if _is_auth_error(exc):
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


def _safe_raw_sql(db, sql):
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
    rows = [tuple(r) for r in result.fetchall()]
    return pd.DataFrame(rows, columns=cols)


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


def connect_wrds():
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
        _clear_auth_block()
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
                _clear_auth_block()
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
                # Removing the terminal latch is the operator's approval. The
                # connection routine immediately replaces it with a durable
                # in-progress marker before touching credentials.
                _clear_auth_block()
                try:
                    self.db.close()
                except Exception:
                    pass
                self.db = connect_wrds()
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


def handle_client(conn, state):
    """Handle a single client query."""
    try:
        # Receive the full message (length-prefixed)
        raw_len = conn.recv(8)
        if not raw_len:
            return
        msg_len = int(raw_len.decode().strip())

        chunks = []
        received = 0
        while received < msg_len:
            chunk = conn.recv(min(65536, msg_len - received))
            if not chunk:
                break
            chunks.append(chunk)
            received += len(chunk)

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

        if cmd == 'safety_hello_v2':
            # Deliberately DB-free. Updated clients send this before `ping` so
            # probing a legacy daemon cannot invoke its vulnerable healthcheck.
            response = {'status': 'ok', 'msg': 'safety protocol confirmed'}
        elif cmd == 'safe_ping_v2':
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
        elif cmd == 'safe_query_v2':
            sql = request['sql']
            df, recovered = state.run(lambda db: _safe_raw_sql(db, sql))
            # Convert to JSON-serializable format
            response = {
                'status': 'ok',
                'columns': list(df.columns),
                'data': df.to_json(orient='split', date_format='iso'),
                'shape': list(df.shape),
                'recovered': recovered,
            }
        elif cmd == 'safe_list_tables_v2':
            lib = request['library']
            tables, recovered = state.run(
                lambda db: db.list_tables(library=lib))
            response = {'status': 'ok', 'tables': tables,
                        'recovered': recovered}
        elif cmd == 'safe_list_libraries_v2':
            libraries, recovered = state.run(lambda db: db.list_libraries())
            response = {'status': 'ok', 'libraries': libraries,
                        'recovered': recovered}
        elif cmd == 'safe_get_table_v2':
            kwargs = request.get('kwargs') or {}
            df, recovered = state.run(lambda db: db.get_table(
                request['library'], request['table'], **kwargs))
            response = {
                'status': 'ok',
                'data': df.to_json(orient='split', date_format='iso'),
                'recovered': recovered,
            }
        elif cmd == 'safe_describe_v2':
            lib = request['library']
            table = request['table']
            desc, recovered = state.run(
                lambda db: db.describe_table(lib, table))
            response = {
                'status': 'ok',
                'data': desc.to_json(orient='split', date_format='iso'),
                'recovered': recovered,
            }
        elif cmd == 'safe_unblock_v2':
            # Operator-only. No automated caller may issue this — see the
            # auth-latch note above and the WRDS skill's escalation rule.
            ok, detail = state.unblock()
            if ok:
                response = {'status': 'ok', 'msg': detail}
            else:
                response = {'status': 'error', 'msg': detail,
                            'error_kind': 'auth'}
        elif cmd == 'safe_shutdown_v2':
            response = {'status': 'ok', 'msg': 'shutting down'}
            send_response(conn, response)
            conn.close()
            # Signal the main process instead of os._exit(0) so the
            # registered cleanup() runs: closes the WRDS connection and
            # removes the (now host-global) pid file. Falls back to a hard
            # exit if signalling fails for any reason.
            try:
                os.kill(os.getpid(), signal.SIGTERM)
                return
            except Exception:
                os._exit(0)
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
    """Send length-prefixed JSON response."""
    response = {**response, 'safety_protocol': SAFETY_PROTOCOL}
    data = json.dumps(response, default=str).encode()
    header = f"{len(data):8d}".encode()
    conn.sendall(header + data)

def main():
    # Cheap pre-check: a recorded, still-alive PID means a server is up.
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)  # Check if process exists
            print(f"[wrds_server] Already running (PID {old_pid})")
            return
        except (OSError, ValueError):
            pass  # Old process is dead / pid file junk — continue

    # Persisted credential latch. Checked before binding or connecting: a
    # restart must NOT be a free way around the operator gate, or the automated
    # path (start_services.sh at every pipeline launch) would spend a login per
    # session against a credential already known to be rejected.
    try:
        blocked = _read_auth_block()
        if not blocked:
            _verify_auth_block_storage()
    except WrdsLatchError as e:
        print(f"[wrds_server] RETRY LATCH UNAVAILABLE — refusing to connect: {e}",
              flush=True)
        sys.exit(2)
    if blocked:
        print(f"[wrds_server] AUTH BLOCKED — refusing to start. {blocked}",
              flush=True)
        sys.exit(2)

    # Bind FIRST, before the expensive WRDS connect + Duo. The port is the
    # authoritative per-host singleton guard: if another server is already
    # listening (e.g. started by a different project, with a stale/missing
    # pid file), bind() fails with EADDRINUSE and we exit cleanly WITHOUT
    # touching the pid file the live server owns. Note SO_REUSEADDR does not
    # let a second process steal an actively-listened socket, so this is a
    # true mutual-exclusion check.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
    except OSError as e:
        print(f"[wrds_server] Port {PORT} already in use ({e}); "
              f"another server is running. Exiting.")
        server.close()
        return
    server.listen(5)

    # We own the port — record our PID (overwrites a stale one).
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # Connect to WRDS (triggers Duo on first connect)
    print("[wrds_server] Connecting to WRDS (check Duo notification)...")
    try:
        state = WrdsState(connect_wrds())
    except WrdsAuthError as e:
        # Keep owning the port with an in-memory latch even if persistence has
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
    print(f"[wrds_server] Listening on {HOST}:{PORT}")

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

    def cleanup(signum, frame):
        print("\n[wrds_server] Shutting down...")
        try:
            state.db.close()
        except Exception:
            pass
        server.close()
        _remove_pid_if_ours()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        try:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, state))
            t.daemon = True
            t.start()
        except Exception as e:
            print(f"[wrds_server] Error: {e}")

if __name__ == '__main__':
    main()
