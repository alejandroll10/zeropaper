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
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

_DOTENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=_DOTENV_PATH)

HOST = '127.0.0.1'
PORT = 23847
# Bump with the server whenever login/recovery safety semantics change. Keep a
# literal here: importing the deployed module cannot identify a stale process.
SAFETY_PROTOCOL = 'wrds-auth-latch-v2'

def _send_request(request, timeout=300):
    """Send a request to the wrds_server and return the response."""
    request = {**request, 'safety_protocol': SAFETY_PROTOCOL}
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


class WrdsSafetyBlocked(RuntimeError):
    """The live daemon cannot prove the current no-retry safety contract."""


def _safety_message(got=None):
    return (
        f"WRDS daemon safety protocol mismatch (got {got!r}, expected "
        f"{SAFETY_PROTOCOL!r}). Do not query, retry, or auto-restart it. "
        "OPERATOR: stop the stale daemon, then start the deployed server; if "
        "a credential latch is reported, use the one-attempt unblock procedure."
    )


def _validate_protocol(resp):
    if resp.get('safety_protocol') != SAFETY_PROTOCOL:
        raise WrdsSafetyBlocked(_safety_message(resp.get('safety_protocol')))


def _safety_hello():
    """DB-free handshake; legacy servers reject this as an unknown command."""
    resp = _send_request({'cmd': 'safety_hello_v2'}, timeout=5)
    _validate_protocol(resp)
    if resp.get('status') != 'ok':
        raise WrdsSafetyBlocked(resp.get('msg') or _safety_message())


def _ensure_safe_server(allow_auth=False):
    """Handshake before any command an old daemon could execute unsafely."""
    _safety_hello()
    resp = _send_request({'cmd': 'safe_ping_v2'}, timeout=5)
    _validate_protocol(resp)
    if resp.get('status') == 'error':
        if allow_auth and resp.get('error_kind') == 'auth':
            return
        _raise("WRDS server unavailable", resp)


def _checked_request(request, timeout=300):
    _ensure_safe_server()
    resp = _send_request(request, timeout=timeout)
    _validate_protocol(resp)
    return resp


def wrds_ping():
    """Check if wrds_server is running. Returns True/False."""
    try:
        _safety_hello()
        resp = _send_request({'cmd': 'safe_ping_v2'}, timeout=5)
        return (resp.get('status') == 'ok' and
                resp.get('safety_protocol') == SAFETY_PROTOCOL)
    except (ConnectionRefusedError, OSError, WrdsSafetyBlocked):
        return False


def wrds_auth_error():
    """Return the operator-facing message if the server has latched a
    credential rejection, else None.

    Callers that poll for readiness MUST consult this: a latched server stays
    up and answers pings forever, so a plain `while not wrds_ping()` loop would
    spin for its full budget on a failure no amount of waiting can fix.
    """
    try:
        _safety_hello()
        resp = _send_request({'cmd': 'safe_ping_v2'}, timeout=5)
    except WrdsSafetyBlocked as e:
        return str(e)
    except (ConnectionRefusedError, OSError):
        # Server down — the latch persists on disk precisely so a restart is
        # not a free way around the operator gate. Report it, or a caller
        # would spawn a server that instantly exits 2 and then wait out its
        # full readiness budget for a process already gone.
        return _persisted_auth_block()
    if resp.get('safety_protocol') != SAFETY_PROTOCOL:
        return _safety_message(resp.get('safety_protocol'))
    if resp.get('error_kind') == 'safety':
        return resp.get('msg') or _safety_message()
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


def _persisted_auth_state():
    try:
        server = _server_module()
        message = server._read_auth_block()
        # During the one live process's startup, the write-ahead marker means
        # "wait for Duo", not "credentials were rejected". If that process
        # dies, the exact same marker becomes a terminal persisted latch.
        if message and server._live_login_attempt(message):
            return 'in_progress', message
        if message:
            return 'blocked', message
        return 'none', None
    except Exception as e:
        # Unreadable latch state is not evidence that no rejection occurred.
        # Refuse automatic startup until the operator repairs the state path.
        return ('blocked',
                f"WRDS retry latch is unreadable; refusing automatic start: {e}")


def _persisted_auth_block():
    kind, message = _persisted_auth_state()
    return message if kind == 'blocked' else None


def wrds_login_in_progress():
    """True while another live server owns the write-ahead login marker."""
    return _persisted_auth_state()[0] == 'in_progress'


def _wait_for_ready(proc=None):
    """Wait for either a server we spawned or an already-starting peer."""
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        time.sleep(1)
        if wrds_ping():
            print("[wrds_client] WRDS server is ready.")
            return True
        latched = wrds_auth_error()
        if latched:
            raise WrdsAuthBlocked(latched)
        if proc is not None and proc.poll() is not None:
            # Two starters can both spawn before the winner writes its marker.
            # The loser exits on PID/port ownership; that is a cue to join the
            # peer, not report failure to an outer supervisor that may retry.
            if proc.returncode == 0 or wrds_login_in_progress():
                print("[wrds_client] Starter lost the singleton race; waiting "
                      "for the existing WRDS server.")
                proc = None
                continue
            err = (proc.stderr.read() or b'').decode(errors='replace')
            out = (proc.stdout.read() or b'').decode(errors='replace')
            detail = (out + err).strip()[-800:]
            if proc.returncode == 2:
                raise WrdsAuthBlocked(
                    "WRDS server exited on a safety/authentication gate — not "
                    f"retrying. {detail}"
                )
            raise RuntimeError(
                f"WRDS server exited (code {proc.returncode}) before becoming "
                f"ready: {detail}"
            )
    raise TimeoutError("WRDS server did not start within 2 minutes. Check Duo.")


def wrds_wait_for_existing():
    """Wait for a peer's live write-ahead attempt without spawning a process."""
    if not wrds_login_in_progress():
        raise RuntimeError('no live WRDS login attempt to wait for')
    return _wait_for_ready()

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
    if wrds_login_in_progress():
        print("[wrds_client] Another WRDS login is in progress; waiting for it.")
        return _wait_for_ready()

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

    return _wait_for_ready(proc)

def _raise(prefix, resp):
    """Raise the typed client exception represented by an error response."""
    kind = resp.get('error_kind')
    tag = f" [{kind} error]" if kind else ""
    if kind == 'auth':
        raise WrdsAuthBlocked(f"{prefix}{tag}: {resp['msg']}")
    if kind == 'safety':
        raise WrdsSafetyBlocked(f"{prefix}{tag}: {resp['msg']}")
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
    resp = _checked_request({'cmd': 'safe_query_v2', 'sql': sql}, timeout=timeout)
    if resp['status'] == 'error':
        _raise("WRDS query failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_list_tables(library):
    """List tables in a WRDS library."""
    resp = _checked_request({'cmd': 'safe_list_tables_v2', 'library': library})
    if resp['status'] == 'error':
        _raise("WRDS list_tables failed", resp)
    return resp['tables']

def wrds_list_libraries():
    """List WRDS libraries via the persistent server."""
    resp = _checked_request({'cmd': 'safe_list_libraries_v2'})
    if resp['status'] == 'error':
        _raise("WRDS list_libraries failed", resp)
    return resp['libraries']

def wrds_get_table(library, table, rows=-1, obs=None, offset=0, columns=None,
                   coerce_float=True, index_col=None, date_cols=None):
    """Compatibility wrapper for ``wrds.Connection.get_table``."""
    kwargs = {
        'rows': rows,
        'obs': obs,
        'offset': offset,
        'columns': columns,
        'coerce_float': coerce_float,
        'index_col': index_col,
        'date_cols': date_cols,
    }
    resp = _checked_request({
        'cmd': 'safe_get_table_v2', 'library': library, 'table': table,
        'kwargs': kwargs,
    })
    if resp['status'] == 'error':
        _raise("WRDS get_table failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_describe(library, table):
    """Describe a WRDS table (columns, types, row count)."""
    resp = _checked_request(
        {'cmd': 'safe_describe_v2', 'library': library, 'table': table})
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
        _ensure_safe_server(allow_auth=True)
        resp = _send_request({'cmd': 'safe_unblock_v2'}, timeout=180)
        _validate_protocol(resp)
    except ConnectionRefusedError:
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
        # DB-free hello + versioned lifecycle command: never let an updated
        # client kill a stale daemon and invite an automated replacement.
        _safety_hello()
        resp = _send_request({'cmd': 'safe_shutdown_v2'}, timeout=5)
        _validate_protocol(resp)
    except Exception:
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
