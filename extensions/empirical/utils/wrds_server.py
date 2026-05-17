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

Server writes its PID to code/utils/.wrds_server.pid for cleanup.

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
import threading
import signal
from dotenv import load_dotenv

load_dotenv()

HOST = '127.0.0.1'
PORT = 23847  # arbitrary high port
PID_FILE = os.path.join(os.path.dirname(__file__), '.wrds_server.pid')
MAX_MSG = 10 * 1024 * 1024  # 10MB max message size

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


def _is_conn_error(exc):
    """True if `exc` looks like a dropped/poisoned connection (recoverable),
    as opposed to a query error (syntax/permission/missing table)."""
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
    db = wrds.Connection(
        wrds_username=os.getenv('WRDS_USER'),
        wrds_password=wrds_pass
    )
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

    # --- recovery ---------------------------------------------------------
    def _healthy(self, db):
        """Return True iff `SELECT 1` succeeds on `db`."""
        try:
            _safe_raw_sql(db, 'SELECT 1')
            return True
        except Exception:
            return False

    def _recover(self):
        """Restore a working connection. Caller must hold self.lock.

        Tiered, cheapest first. None of these re-trigger Duo: the WRDS
        Postgres engine authenticates with the libpq password (PGPASSWORD),
        not the interactive 2FA that only fires on the very first connect.
        Returns a short string describing which tier succeeded.
        Raises the last error if every tier fails.
        """
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
            try:
                return fn(self.db), False
            except Exception as e:
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
            if self._healthy(self.db):
                return True, 'ok'
            try:
                tier = self._recover()
                return True, f'recovered:{tier}'
            except Exception as e:
                return False, str(e)


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
        elif cmd == 'shutdown':
            response = {'status': 'ok', 'msg': 'shutting down'}
            send_response(conn, response)
            conn.close()
            os._exit(0)
        else:
            response = {'status': 'error', 'msg': f'unknown command: {cmd}'}

        send_response(conn, response)
    except Exception as e:
        try:
            error_kind = 'connection' if _is_conn_error(e) else 'query'
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
    # Check if already running
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)  # Check if process exists
            print(f"[wrds_server] Already running (PID {old_pid})")
            return
        except OSError:
            pass  # Old process is dead, continue

    # Write PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # Connect to WRDS (triggers Duo)
    print("[wrds_server] Connecting to WRDS (check Duo notification)...")
    state = WrdsState(connect_wrds())

    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[wrds_server] Listening on {HOST}:{PORT}")

    def cleanup(signum, frame):
        print("\n[wrds_server] Shutting down...")
        try:
            state.db.close()
        except Exception:
            pass
        server.close()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
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
