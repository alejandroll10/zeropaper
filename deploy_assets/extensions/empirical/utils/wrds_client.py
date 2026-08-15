"""WRDS client — sends queries to the persistent wrds_server.

Usage:
    from utils.wrds_client import wrds_query, wrds_ping

    # The trusted launcher starts the daemon before entering the sandbox
    assert wrds_ping(), "host WRDS daemon unavailable"

    # Run a query
    df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")

    # List tables
    tables = wrds_list_tables("crsp")

The client prefers the server's private Unix-domain socket, which remains
reachable through a sandbox's read-only home view when it has its own network
namespace. It exposes query operations only; host lifecycle control is never
available over the wire. If the server is down, relaunch the runtime so its
trusted host-side launcher can restore it.
"""
import json
import socket
import subprocess
import time
import os
import stat
import sys
from pathlib import Path

import pandas as pd
from dotenv import dotenv_values, load_dotenv

_DOTENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=_DOTENV_PATH)

PORT = 23847
SOCKET_FILE = os.path.join(
    os.path.expanduser('~'), '.local', 'state', 'zeropaper', 'wrds',
    f'wrds_server_{PORT}.sock')
LOG_FILE = os.path.join(
    os.path.dirname(SOCKET_FILE), f'wrds_server_{PORT}.log')
# Bump with the server whenever login/recovery safety semantics change. Keep a
# literal here: importing the deployed module cannot identify a stale process.
SAFETY_PROTOCOL = 'wrds-auth-latch-v5'
MAX_RESPONSE = 90 * 1024 * 1024


def _recv_exact(sock, size):
    chunks = []
    received = 0
    while received < size:
        chunk = sock.recv(size - received)
        if not chunk:
            raise ConnectionError(
                f'incomplete WRDS response frame ({received}/{size} bytes)')
        chunks.append(chunk)
        received += len(chunk)
    return b''.join(chunks)

def _connect(timeout):
    """Connect to the host-wide daemon across sandbox boundaries.

    Network-isolated sandboxes have a private 127.0.0.1, but their approved
    read-only home view is shared with the host.
    """
    if not hasattr(socket, 'AF_UNIX'):
        raise OSError('WRDS sandbox transport requires AF_UNIX support')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(SOCKET_FILE)
        return sock
    except OSError:
        sock.close()
        raise


def _send_request(request, timeout=300):
    """Send a request to the wrds_server and return the response."""
    request = {**request, 'safety_protocol': SAFETY_PROTOCOL}
    sock = _connect(timeout)
    try:
        data = json.dumps(request).encode()
        header = f"{len(data):8d}".encode()
        sock.sendall(header + data)

        # Receive response
        raw_len = _recv_exact(sock, 8)
        try:
            msg_len = int(raw_len.decode('ascii').strip())
        except (UnicodeError, ValueError) as e:
            raise ConnectionError('invalid WRDS response frame length') from e
        if msg_len <= 0 or msg_len > MAX_RESPONSE:
            raise ConnectionError(
                f'WRDS response frame must be 1..{MAX_RESPONSE} bytes')

        chunks = []
        received = 0
        while received < msg_len:
            chunk = _recv_exact(sock, min(65536, msg_len - received))
            chunks.append(chunk)
            received += len(chunk)
        return json.loads(b''.join(chunks).decode())
    finally:
        sock.close()

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
    resp = _send_request({'cmd': 'safety_hello_v5'}, timeout=5)
    _validate_protocol(resp)
    if resp.get('status') != 'ok':
        raise WrdsSafetyBlocked(resp.get('msg') or _safety_message())


def _ensure_safe_server(allow_auth=False):
    """Handshake before any command an old daemon could execute unsafely."""
    _safety_hello()
    resp = _send_request({'cmd': 'safe_ping_v5'}, timeout=5)
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
        resp = _send_request({'cmd': 'safe_ping_v5'}, timeout=5)
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
        resp = _send_request({'cmd': 'safe_ping_v5'}, timeout=5)
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
        # Unreadable state remains fail-closed because this client never
        # auto-starts. Keep it distinct from a credential rejection so a
        # sandbox write denial is not mislabeled as an auth lockout.
        return ('unavailable',
                f"WRDS retry latch is unreadable; host repair required: {e}")


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
            # The loser exits on filesystem-lock ownership; that is a cue to join the
            # peer, not report failure to an outer supervisor that may retry.
            if proc.returncode == 0 or wrds_login_in_progress():
                print("[wrds_client] Starter lost the singleton race; waiting "
                      "for the existing WRDS server.")
                proc = None
                continue
            err_stream = getattr(proc, 'stderr', None)
            out_stream = getattr(proc, 'stdout', None)
            err = ((err_stream.read() or b'').decode(errors='replace')
                   if err_stream is not None else '')
            out = ((out_stream.read() or b'').decode(errors='replace')
                   if out_stream is not None else '')
            detail = (out + err).strip()[-800:]
            if not detail:
                detail = f"see durable service log {LOG_FILE}"
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
    """Verify/reuse the host-started daemon; never spawn from a sandbox."""
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

    raise RuntimeError(
        "WRDS host daemon is down. Sandboxed code cannot safely recreate its "
        "protected singleton/latch state. Stop this runtime and relaunch it "
        "through ./launch.sh (or ask the operator to run "
        "code/utils/start_services.sh on the host); do not retry here."
    )

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
    resp = _checked_request(
        {'cmd': 'safe_query_v5', 'sql': sql, 'timeout': timeout}, timeout=timeout)
    if resp['status'] == 'error':
        _raise("WRDS query failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_list_tables(library):
    """List tables in a WRDS library."""
    resp = _checked_request({'cmd': 'safe_list_tables_v5', 'library': library})
    if resp['status'] == 'error':
        _raise("WRDS list_tables failed", resp)
    return resp['tables']

def wrds_list_libraries():
    """List WRDS libraries via the persistent server."""
    resp = _checked_request({'cmd': 'safe_list_libraries_v5'})
    if resp['status'] == 'error':
        _raise("WRDS list_libraries failed", resp)
    return resp['libraries']

def wrds_get_table(library, table, rows=-1, obs=None, offset=0, columns=None,
                   coerce_float=True, index_col=None, date_cols=None):
    """Compatibility wrapper for ``wrds.Connection.get_table``.

    The shared daemon requires an explicit positive ``rows``/``obs`` limit no
    larger than 100,000. Use filtered ``wrds_query`` pulls for larger extracts.
    """
    requested_rows = obs if obs is not None else rows
    try:
        requested_rows = int(requested_rows)
    except (TypeError, ValueError) as e:
        raise ValueError('wrds_get_table requires an explicit row limit') from e
    if not 1 <= requested_rows <= 100_000:
        raise ValueError(
            'wrds_get_table row limit must be 1..100000; use filtered '
            'wrds_query pulls for larger extracts')
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
        'cmd': 'safe_get_table_v5', 'library': library, 'table': table,
        'kwargs': kwargs,
    })
    if resp['status'] == 'error':
        _raise("WRDS get_table failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_describe(library, table):
    """Describe a WRDS table (columns, types, row count)."""
    resp = _checked_request(
        {'cmd': 'safe_describe_v5', 'library': library, 'table': table})
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
    # Lifecycle operations are intentionally absent from the query socket. An
    # operator must first stop the live daemon from the host; otherwise an
    # autonomous agent could turn one network request into another login.
    try:
        _safety_hello()
        return False, (
            'WRDS daemon is still running. OPERATOR: stop its recorded PID '
            'from the host, then rerun this unblock command exactly once.'
        )
    except WrdsSafetyBlocked as e:
        # A protocol mismatch still proves that a process answered the socket.
        # Never start a second credentialed daemon beside an old live one.
        return False, (
            'A live WRDS endpoint has an incompatible safety protocol. '
            f'OPERATOR: stop it from the host before unblock. {e}'
        )
    except (ConnectionRefusedError, FileNotFoundError):
        pass

    srv = _server_module()
    if not srv._read_auth_block():
        return False, 'no WRDS server running, and no latch to clear'
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(utils_dir, 'wrds_server.py')
    # The operator may have corrected .env while their shell still exports the
    # rejected credential.  The approved retry must use the reviewed file, not
    # silently inherit stale WRDS_PASS/PGPASSWORD values from that shell.
    load_dotenv(dotenv_path=_DOTENV_PATH, override=True)
    server_env = {**os.environ}
    file_credentials = dotenv_values(dotenv_path=_DOTENV_PATH)
    for credential_key in ('WRDS_USER', 'WRDS_PASS', 'PGPASSWORD'):
        server_env.pop(credential_key, None)
    for credential_key in ('WRDS_USER', 'WRDS_PASS'):
        credential_value = file_credentials.get(credential_key)
        if credential_value is not None:
            server_env[credential_key] = credential_value
    wrds_pass = server_env.get('WRDS_PASS')
    if wrds_pass:
        server_env['PGPASSWORD'] = wrds_pass
    srv._prepare_auth_block_dir()
    flags = (os.O_WRONLY | os.O_CREAT | os.O_APPEND |
             getattr(os, 'O_NOFOLLOW', 0))
    try:
        log_fd = os.open(LOG_FILE, flags, 0o600)
        info = os.fstat(log_fd)
        if (not stat.S_ISREG(info.st_mode) or
                (hasattr(os, 'getuid') and info.st_uid != os.getuid())):
            raise OSError(f"unsafe WRDS service log: {LOG_FILE}")
        os.fchmod(log_fd, 0o600)
        proc = subprocess.Popen(
            [sys.executable, server_script, '--operator-unblock'],
            stdout=log_fd,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=server_env,
        )
    finally:
        if 'log_fd' in locals():
            os.close(log_fd)
    try:
        _wait_for_ready(proc)
        return True, 'latch cleared; server started and credential accepted'
    except WrdsAuthBlocked as e:
        return False, str(e)
    except Exception as e:
        return False, f'approved retry did not start a healthy server: {e}'


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
