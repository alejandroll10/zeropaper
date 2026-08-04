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
        # Fall back to direct connection
        ...

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
(rollback -> rebuild pool -> full reconnect) before failing the query;
`ping` exercises the connection with a real `SELECT 1` so a wedged
server reports unhealthy instead of falsely reporting alive. See
GitHub issue #28.
"""
import os
import sys
import json
import socket
import tempfile
import threading
import signal
from dotenv import load_dotenv

load_dotenv()

HOST = '127.0.0.1'
PORT = 23847  # arbitrary high port

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

    Same lifetime as the PID file (XDG_RUNTIME_DIR / temp dir): a reboot or
    logout clears it. That is a deliberate reset point — better than a latch in
    $HOME outliving a credential that was fixed weeks ago.
    """
    base = os.environ.get('XDG_RUNTIME_DIR') or tempfile.gettempdir()
    return os.path.join(base, f'.wrds_server_{PORT}.authblock')


PID_FILE = _pid_file_path()
AUTH_BLOCK_FILE = _auth_block_path()
MAX_MSG = 10 * 1024 * 1024  # 10MB max message size


def _read_auth_block():
    """Operator-facing message from a persisted latch, or None."""
    try:
        with open(AUTH_BLOCK_FILE) as f:
            return f.read().strip() or None
    except OSError:
        return None


def _write_auth_block(msg):
    """Persist the latch. Best-effort: if the write fails the in-memory latch
    still holds for this process, so a failure here degrades to the old
    behaviour rather than removing the guard."""
    try:
        with open(AUTH_BLOCK_FILE, 'w') as f:
            f.write(msg)
    except OSError:
        pass


def _clear_auth_block():
    """Remove the persisted latch. Only reached via operator-approved unblock."""
    try:
        os.remove(AUTH_BLOCK_FILE)
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
# deliberate operator action — fix the credential and restart the server.
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


def _is_auth_error(exc):
    """True if `exc` is WRDS refusing the credential.

    Must be checked BEFORE _is_conn_error(), which would otherwise absorb a
    PAM rejection as a recoverable socket drop and retry it into a lockout.
    """
    msg = str(exc).lower()
    if any(n in msg for n in _AUTH_ERROR_NEEDLES):
        return True
    # wrds.Connection falls back to interactive prompting when its
    # authenticated connect fails; with no tty (nohup) that surfaces as an
    # EOFError from input(), never as an auth message.
    return isinstance(exc, EOFError)


def _is_conn_error(exc):
    """True if `exc` looks like a dropped/poisoned connection (recoverable),
    as opposed to a query error (syntax/permission/missing table).

    Auth rejections are excluded: they are terminal, not recoverable."""
    if _is_auth_error(exc):
        return False
    msg = str(exc).lower()
    if any(n in msg for n in _CONN_ERROR_NEEDLES):
        return True
    try:
        import sqlalchemy.exc as sa_exc
        # Only the exceptions that actually indicate a dead/poisoned socket.
        # Deliberately NOT DBAPIError or InvalidRequestError: those are the
        # parents of ProgrammingError/DataError/IntegrityError/NoSuchTableError
        # etc. — query-level failures that must surface as-is, not trigger a
        # needless reconnect+retry. PendingRollbackError (a subclass of
        # InvalidRequestError) is listed explicitly because it *is* a poisoned
        # connection.
        if isinstance(exc, (sa_exc.OperationalError,
                            sa_exc.InterfaceError,
                            sa_exc.PendingRollbackError)):
            return True
    except Exception:
        pass
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
    # Fallback path
    from sqlalchemy import text
    with db.engine.connect() as conn:
        result = conn.execute(text(sql))
        cols = list(result.keys())
        rows = [tuple(r) for r in result.fetchall()]
    return pd.DataFrame(rows, columns=cols)


def connect_wrds():
    """Establish WRDS connection (triggers Duo 2FA on first connect)."""
    import wrds
    # wrds.Connection silently drops the wrds_password kwarg (sql.py:62 hardcodes
    # self._password = ""). Set PGPASSWORD so libpq picks it up — makes this function
    # self-sufficient when launched directly (without start_services.sh / wrds_client).
    # libpq password auth also means a *reconnect* does not re-trigger Duo.
    wrds_pass = os.getenv('WRDS_PASS')
    if wrds_pass:
        os.environ['PGPASSWORD'] = wrds_pass
    try:
        db = wrds.Connection(
            wrds_username=os.getenv('WRDS_USER'),
            wrds_password=wrds_pass
        )
    except Exception as e:
        # A rejected credential must never look like a transient failure: the
        # caller (start_services.sh, wrds_start) would otherwise keep relaunching
        # this and burn the account's login budget.
        if _is_auth_error(e):
            raise WrdsAuthError(_auth_guidance(e)) from e
        raise
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
        # Sticky credential-rejection latch. Set to an operator-facing message
        # the first time WRDS refuses the credential; while set, no code path
        # attempts another login. Only an operator clears it, by fixing the
        # credential and restarting the server.
        self.auth_failed = None

    # --- recovery ---------------------------------------------------------
    def _healthy(self, db):
        """Return True iff `SELECT 1` succeeds on `db`."""
        try:
            _safe_raw_sql(db, 'SELECT 1')
            return True
        except Exception:
            return False

    def _latch_auth_failure(self, exc):
        """Set the sticky auth latch and abort if `exc` is a credential
        rejection. Called from every recovery tier so the *first* rejection
        stops the cascade — otherwise Tier 2 failing on a bad password would
        fall through to Tier 3 and spend a second login on the same doomed
        credential."""
        if not _is_auth_error(exc):
            return
        self.auth_failed = _auth_guidance(exc)
        _write_auth_block(self.auth_failed)
        print(f"[wrds_server] AUTH FAILURE — halting retries. {self.auth_failed}",
              flush=True)
        raise WrdsAuthError(self.auth_failed) from exc

    def _recover(self):
        """Restore a working connection. Caller must hold self.lock.

        Tiered, cheapest first. None of these re-trigger Duo: the WRDS
        Postgres engine authenticates with the libpq password (PGPASSWORD),
        not the interactive 2FA that only fires on the very first connect.
        Returns a short string describing which tier succeeded.
        Raises the last error if every tier fails.
        """
        # Latched credential rejection: every tier below would issue another
        # login, so refuse before spending one.
        if self.auth_failed:
            raise WrdsAuthError(self.auth_failed)

        db = self.db
        last_err = None

        # Tier 1: roll back the poisoned transaction on the existing socket.
        # Handles the common case where the socket is alive but the
        # transaction is aborted.
        try:
            db.connection.rollback()
            if self._healthy(db):
                return 'rolled_back'
        except Exception as e:
            self._latch_auth_failure(e)
            last_err = e

        # Tier 2: rebuild the engine/connection pool in place. wrds.connect()
        # re-runs the sqlalchemy engine creation against the same (password)
        # credentials and resets db.connection. Dispose the old pool first so
        # the dead socket is not leaked.
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
            db.connect()  # rebuilds self.engine + self.connection (no Duo)
            # db.connect() does NOT refresh db.insp; the inspector still
            # points at the old, closed connection, which would re-poison
            # list_tables()/describe_table() immediately. Rebind it. Do NOT
            # swallow a failure here: if inspect() throws, the new connection
            # is itself bad, so let it propagate to the Tier-2 handler and
            # fall through to the Tier-3 full reconnect.
            import sqlalchemy as sa
            db.insp = sa.inspect(db.connection)
            if self._healthy(db):
                return 'pool_rebuilt'
        except Exception as e:
            self._latch_auth_failure(e)
            last_err = e

        # Tier 3: full reconnect — replace the wrds.Connection object
        # entirely. Still no Duo (PGPASSWORD), just heavier.
        try:
            try:
                db.close()
            except Exception:
                pass
            self.db = connect_wrds()
            if self._healthy(self.db):
                return 'reconnected'
        except Exception as e:
            self._latch_auth_failure(e)
            last_err = e

        raise RuntimeError(
            f"WRDS connection recovery failed after all tiers: {last_err}"
        )

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
                return fn(self.db), True

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
            if self._healthy(self.db):
                return True, 'ok'
            try:
                tier = self._recover()
                return True, f'recovered:{tier}'
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

            load_dotenv(override=True)
            wrds_pass = os.getenv('WRDS_PASS')
            if wrds_pass:
                os.environ['PGPASSWORD'] = wrds_pass

            # Cleared only for the duration of this single attempt.
            self.auth_failed = None
            try:
                try:
                    self.db.close()
                except Exception:
                    pass
                self.db = connect_wrds()
                if not self._healthy(self.db):
                    raise RuntimeError('connection unhealthy after reconnect')
                _clear_auth_block()
                print("[wrds_server] unblocked — credential accepted", flush=True)
                return True, 'reconnected'
            except Exception as e:
                if _is_auth_error(e):
                    self.auth_failed = _auth_guidance(e)
                else:
                    self.auth_failed = (
                        f"Unblock attempt failed, and not on authentication: {e}. "
                        "Re-latched rather than retried — diagnose first, then "
                        "approve another unblock."
                    )
                _write_auth_block(self.auth_failed)
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

        if cmd == 'ping':
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
        elif cmd == 'query':
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
        elif cmd == 'list_tables':
            lib = request['library']
            tables, recovered = state.run(
                lambda db: db.list_tables(library=lib))
            response = {'status': 'ok', 'tables': tables,
                        'recovered': recovered}
        elif cmd == 'describe':
            lib = request['library']
            table = request['table']
            desc, recovered = state.run(
                lambda db: db.describe_table(lib, table))
            response = {
                'status': 'ok',
                'data': desc.to_json(orient='split', date_format='iso'),
                'recovered': recovered,
            }
        elif cmd == 'unblock':
            # Operator-only. No automated caller may issue this — see the
            # auth-latch note above and the WRDS skill's escalation rule.
            ok, detail = state.unblock()
            if ok:
                response = {'status': 'ok', 'msg': detail}
            else:
                response = {'status': 'error', 'msg': detail,
                            'error_kind': 'auth'}
        elif cmd == 'shutdown':
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
    blocked = _read_auth_block()
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
        # Exit clean and loud instead of dumping a traceback whose proximate
        # cause (EOFError from wrds's interactive prompt fallback) hides the
        # real one. Release the port and pid file so the next attempt, after
        # the operator fixes the credential, starts from a clean slate.
        _write_auth_block(str(e))
        print(f"[wrds_server] {e}", flush=True)
        try:
            server.close()
        finally:
            try:
                os.remove(PID_FILE)
            except OSError:
                pass
        sys.exit(2)
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
