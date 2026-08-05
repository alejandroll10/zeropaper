"""WRDS client — sends queries to the persistent wrds_server.

Usage:
    from utils.wrds_client import wrds_query, wrds_ping, wrds_start

    # Check if server is running, start if not
    wrds_start()

    # Run a query
    df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")

    # List tables
    tables = wrds_list_tables("crsp")

The client connects to the local wrds_server on port 23847.
If the server isn't running, wrds_start() launches it in the background
and waits for the Duo 2FA to complete.
"""
import json
import socket
import subprocess
import time
import os
import sys

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

HOST = '127.0.0.1'
PORT = 23847

def _send_request(request, timeout=300):
    """Send a request to the wrds_server and return the response."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((HOST, PORT))

    data = json.dumps(request).encode()
    header = f"{len(data):8d}".encode()
    sock.sendall(header + data)

    # Receive response
    raw_len = sock.recv(8)
    msg_len = int(raw_len.decode().strip())

    chunks = []
    received = 0
    while received < msg_len:
        chunk = sock.recv(min(65536, msg_len - received))
        if not chunk:
            break
        chunks.append(chunk)
        received += len(chunk)

    sock.close()
    return json.loads(b''.join(chunks).decode())

class WrdsAuthBlocked(RuntimeError):
    """WRDS refused the credential. Terminal — the server has latched and will
    not attempt another login until an operator fixes it. Never retry this."""


def wrds_ping():
    """Check if wrds_server is running. Returns True/False."""
    try:
        resp = _send_request({'cmd': 'ping'}, timeout=5)
        return resp.get('status') == 'ok'
    except (ConnectionRefusedError, OSError):
        return False


def wrds_auth_error():
    """Return the operator-facing message if the server has latched a
    credential rejection, else None.

    Callers that poll for readiness MUST consult this: a latched server stays
    up and answers pings forever, so a plain `while not wrds_ping()` loop would
    spin for its full budget on a failure no amount of waiting can fix.
    """
    try:
        resp = _send_request({'cmd': 'ping'}, timeout=5)
    except (ConnectionRefusedError, OSError):
        # Server down — the latch persists on disk precisely so a restart is
        # not a free way around the operator gate. Report it, or a caller
        # would spawn a server that instantly exits 2 and then wait out its
        # full readiness budget for a process already gone.
        return _persisted_auth_block()
    if resp.get('error_kind') == 'auth':
        return resp.get('msg') or 'WRDS credential rejected'
    return None


def _server_module():
    """Import wrds_server either as a package member (`utils.wrds_server`, the
    normal pipeline import path) or as a sibling module (when this file is run
    directly as a CLI, where sys.path[0] is its own directory)."""
    try:
        from utils import wrds_server as m
    except ImportError:
        import wrds_server as m
    return m


def _persisted_auth_block():
    try:
        return _server_module()._read_auth_block()
    except Exception:
        return None

def wrds_start():
    """Start the wrds_server if not already running.

    This triggers Duo 2FA exactly once. Blocks until the server is ready.
    """
    if wrds_ping():
        return True

    # A latched server is alive but refusing to log in again. Spawning another
    # one would bind-fail anyway, and polling it would burn the full readiness
    # budget on an unfixable condition — so stop here and escalate.
    latched = wrds_auth_error()
    if latched:
        raise WrdsAuthBlocked(latched)

    # Find the server script
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(utils_dir, 'wrds_server.py')

    if not os.path.exists(server_script):
        raise FileNotFoundError(f"wrds_server.py not found at {server_script}")

    print("[wrds_client] Starting WRDS server (check Duo notification)...")
    # wrds.Connection silently drops the wrds_password kwarg, so the spawned server
    # needs PGPASSWORD in its env for libpq to authenticate.
    server_env = {**os.environ}
    wrds_pass = os.getenv('WRDS_PASS')
    if wrds_pass:
        server_env['PGPASSWORD'] = wrds_pass
    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
        env=server_env,
    )

    # Wait for server to be ready (Duo can take a while).
    #
    # Three exits, not one: ready, credential rejected, or timeout. Only the
    # last is worth waiting out. wrds_server exits 2 on a credential rejection,
    # so a dead child with that code means "operator must act" — waiting the
    # remaining budget would just delay the report.
    for i in range(120):  # 2 minutes max
        time.sleep(1)
        if wrds_ping():
            print("[wrds_client] WRDS server is ready.")
            return True
        latched = wrds_auth_error()
        if latched:
            raise WrdsAuthBlocked(latched)
        if proc.poll() is not None:
            err = (proc.stderr.read() or b'').decode(errors='replace')
            out = (proc.stdout.read() or b'').decode(errors='replace')
            detail = (out + err).strip()[-800:]
            if proc.returncode == 2:
                raise WrdsAuthBlocked(
                    "WRDS server exited on a credential rejection — not retrying. "
                    f"{detail}"
                )
            raise RuntimeError(
                f"WRDS server exited (code {proc.returncode}) before becoming "
                f"ready: {detail}"
            )

    raise TimeoutError("WRDS server did not start within 2 minutes. Check Duo.")

def _raise(prefix, resp):
    """Raise a RuntimeError from an error response, tagging connection-level
    failures so callers can distinguish a wedged server from bad SQL."""
    kind = resp.get('error_kind')
    tag = f" [{kind} error]" if kind else ""
    raise RuntimeError(f"{prefix}{tag}: {resp['msg']}")

def wrds_query(sql, timeout=300):
    """Run a SQL query against WRDS via the persistent server.

    Args:
        sql: SQL query string
        timeout: seconds to wait for response (default 5 min for large queries)

    Returns:
        pandas DataFrame

    The server transparently recovers a dropped/poisoned connection and
    retries once before returning an error; resp['recovered'] is True when
    that happened.
    """
    resp = _send_request({'cmd': 'query', 'sql': sql}, timeout=timeout)
    if resp['status'] == 'error':
        _raise("WRDS query failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_list_tables(library):
    """List tables in a WRDS library."""
    resp = _send_request({'cmd': 'list_tables', 'library': library})
    if resp['status'] == 'error':
        _raise("WRDS list_tables failed", resp)
    return resp['tables']

def wrds_describe(library, table):
    """Describe a WRDS table (columns, types, row count)."""
    resp = _send_request({'cmd': 'describe', 'library': library, 'table': table})
    if resp['status'] == 'error':
        _raise("WRDS describe failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_unblock():
    """OPERATOR ONLY — approve one retry after a latched credential rejection.

    Returns (ok, detail). The server reloads .env and spends exactly one login
    attempt; if WRDS refuses again it re-latches, so calling this in a loop is
    the one thing that recreates the lockout this design exists to prevent.

    Agents must never call this. A latched credential is an operator decision:
    escalate and stop. See the WRDS skill's escalation rule.

        python code/utils/wrds_client.py unblock
    """
    try:
        resp = _send_request({'cmd': 'unblock'}, timeout=180)
    except (ConnectionRefusedError, OSError):
        # Server down with a latch on disk: approving means clearing the latch
        # and spending the one approved attempt on a fresh start. Without this
        # the persisted latch would be unclearable except by hand.
        srv = _server_module()
        if not srv._read_auth_block():
            return False, 'no WRDS server running, and no latch to clear'
        srv._clear_auth_block()
        try:
            wrds_start()
            return True, 'latch cleared; server started and credential accepted'
        except WrdsAuthBlocked as e:
            return False, str(e)
        except Exception as e:
            return False, f'latch cleared but server did not start: {e}'
    if resp.get('status') == 'ok':
        return True, resp.get('msg', 'unblocked')
    return False, resp.get('msg', 'unblock failed')


def wrds_shutdown():
    """Shut down the wrds_server."""
    try:
        _send_request({'cmd': 'shutdown'}, timeout=5)
    except:
        pass


if __name__ == '__main__':
    # Small operator CLI. Deliberately minimal: `status` reports whether the
    # server has latched a credential rejection, `unblock` approves exactly one
    # retry. Neither is for agent use — see the WRDS skill's escalation rule.
    _cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if _cmd == 'status':
        if wrds_ping():
            print('WRDS server: healthy')
        else:
            _msg = wrds_auth_error()
            if _msg:
                print(f'WRDS server: AUTH BLOCKED\n  {_msg}')
                sys.exit(2)
            print('WRDS server: down or unhealthy (no auth latch)')
            sys.exit(1)
    elif _cmd == 'unblock':
        _ok, _detail = wrds_unblock()
        print(('OK: ' if _ok else 'FAILED: ') + str(_detail))
        sys.exit(0 if _ok else 2)
    else:
        print(f'usage: {sys.argv[0]} [status|unblock]')
        sys.exit(64)
