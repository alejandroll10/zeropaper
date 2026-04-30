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
    """Establish WRDS connection (triggers Duo 2FA)."""
    import wrds
    # wrds.Connection silently drops the wrds_password kwarg (sql.py:62 hardcodes
    # self._password = ""). Set PGPASSWORD so libpq picks it up — makes this function
    # self-sufficient when launched directly (without start_services.sh / wrds_client).
    wrds_pass = os.getenv('WRDS_PASS')
    if wrds_pass:
        os.environ['PGPASSWORD'] = wrds_pass
    db = wrds.Connection(
        wrds_username=os.getenv('WRDS_USER'),
        wrds_password=wrds_pass
    )
    print(f"[wrds_server] Connected to WRDS as {os.getenv('WRDS_USER')}")
    return db

def handle_client(conn, db, lock):
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
            response = {'status': 'ok', 'msg': 'wrds_server alive'}
        elif cmd == 'query':
            sql = request['sql']
            with lock:
                df = _safe_raw_sql(db, sql)
            # Convert to JSON-serializable format
            response = {
                'status': 'ok',
                'columns': list(df.columns),
                'data': df.to_json(orient='split', date_format='iso'),
                'shape': list(df.shape)
            }
        elif cmd == 'list_tables':
            lib = request['library']
            with lock:
                tables = db.list_tables(library=lib)
            response = {'status': 'ok', 'tables': tables}
        elif cmd == 'describe':
            lib = request['library']
            table = request['table']
            with lock:
                desc = db.describe_table(lib, table)
            response = {
                'status': 'ok',
                'data': desc.to_json(orient='split', date_format='iso')
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
            send_response(conn, {'status': 'error', 'msg': str(e)})
        except:
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
    db = connect_wrds()
    lock = threading.Lock()

    # Start server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[wrds_server] Listening on {HOST}:{PORT}")

    def cleanup(signum, frame):
        print("\n[wrds_server] Shutting down...")
        db.close()
        server.close()
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        try:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, db, lock))
            t.daemon = True
            t.start()
        except Exception as e:
            print(f"[wrds_server] Error: {e}")

if __name__ == '__main__':
    main()
