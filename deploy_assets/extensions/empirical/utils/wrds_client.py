"""WRDS client — sends queries to the persistent wrds_server.

Usage:
    from utils.wrds_client import wrds_query, wrds_ping

    # The trusted launcher starts the daemon before entering the sandbox
    assert wrds_ping(), "host WRDS daemon unavailable"

    # Run a query
    df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")

    # List tables
    tables = wrds_list_tables("crsp")

The client prefers the server's private Unix-domain socket. On Linux, Claude
and OpenCode's sandbox runtime blocks AF_UNIX creation with a path-blind
seccomp filter; there the client uses the launcher's capability-authenticated,
query-only host-loopback bridge through the sandbox's local HTTP proxy. Host
lifecycle control is never available over either transport. If the server or
bridge is down, relaunch the runtime so its trusted host-side launcher can
restore it.
"""
import json
import socket
import subprocess
import time
import os
import stat
import sys
import base64
import errno
import struct
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pandas as pd
from dotenv import dotenv_values, load_dotenv

_DOTENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=_DOTENV_PATH)

PORT = 23847
BRIDGE_PORT = 23848
BRIDGE_PROTOCOL = 'wrds-query-bridge-v2'
BRIDGE_PREFACE_MAGIC = b'WRDS-BRIDGE-V2:'
SOCKET_FILE = os.path.join(
    os.path.expanduser('~'), '.local', 'state', 'zeropaper', 'wrds',
    f'wrds_server_{PORT}.sock')
LOG_FILE = os.path.join(
    os.path.dirname(SOCKET_FILE), f'wrds_server_{PORT}.log')
BRIDGE_TOKEN_FILE = os.path.join(
    os.path.dirname(SOCKET_FILE),
    f'wrds_query_bridge_{BRIDGE_PORT}.token')
# Bump with the server whenever login/recovery safety semantics change. Keep a
# literal here: importing the deployed module cannot identify a stale process.
SAFETY_PROTOCOL = 'wrds-auth-latch-v6'
_BRIDGE_FALLBACK_ERRNOS = frozenset({
    errno.EPERM, errno.EACCES, errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT,
})
MAX_RESPONSE = 512 * 1024 * 1024


def _recv_exact(sock, size, deadline=None):
    chunks = []
    received = 0
    while received < size:
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('WRDS response frame deadline exceeded')
            sock.settimeout(remaining)
        chunk = sock.recv(size - received)
        if not chunk:
            raise ConnectionError(
                f'incomplete WRDS response frame ({received}/{size} bytes)')
        chunks.append(chunk)
        received += len(chunk)
    return b''.join(chunks)

def _read_bridge_token():
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(BRIDGE_TOKEN_FILE, flags)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                (hasattr(os, 'getuid') and info.st_uid != os.getuid()) or
                info.st_mode & 0o077):
            raise OSError('unsafe WRDS bridge capability file')
        token = os.read(fd, 256).decode('ascii').strip()
        if len(token) != 64 or any(c not in '0123456789abcdef' for c in token):
            raise OSError('invalid WRDS bridge capability')
        return token
    finally:
        os.close(fd)


def _proxy_endpoint():
    """Return the trusted loopback HTTP proxy and optional Basic credential."""
    raw = (os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy') or
           os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy'))
    if not raw:
        return None
    parsed = urlsplit(raw)
    # Never send the bridge capability through an arbitrary ambient proxy.
    # Outside Claude's sandbox, use the fixed direct host-loopback endpoint.
    if parsed.scheme.lower() != 'http' or parsed.hostname not in (
            'localhost', '127.0.0.1', '::1'):
        return None
    try:
        proxy_port = parsed.port
    except ValueError as exc:
        raise OSError('WRDS bridge proxy has an invalid port') from exc
    if proxy_port is None:
        raise OSError('WRDS bridge proxy has no port')
    credential = None
    if parsed.username is not None:
        user = unquote(parsed.username)
        password = unquote(parsed.password or '')
        if '\r' in user or '\n' in user or '\r' in password or '\n' in password:
            raise OSError('WRDS bridge proxy credential contains a newline')
        credential = base64.b64encode(
            f'{user}:{password}'.encode('utf-8')).decode('ascii')
    return parsed.hostname, proxy_port, credential


def _connect_bridge(timeout):
    """Reach the authenticated host bridge through Claude's local proxy."""
    token = _read_bridge_token()
    proxy = _proxy_endpoint()
    if proxy is None:
        sock = socket.create_connection(('127.0.0.1', BRIDGE_PORT), timeout)
        return sock, token
    host, port, credential = proxy
    sock = socket.create_connection((host, port), timeout)
    sock.settimeout(timeout)
    try:
        lines = [
            f'CONNECT 127.0.0.1:{BRIDGE_PORT} HTTP/1.1',
            f'Host: 127.0.0.1:{BRIDGE_PORT}',
            'Proxy-Connection: Keep-Alive',
        ]
        if credential is not None:
            lines.append(f'Proxy-Authorization: Basic {credential}')
        sock.sendall(('\r\n'.join(lines) + '\r\n\r\n').encode('ascii'))
        header = bytearray()
        while b'\r\n\r\n' not in header:
            chunk = sock.recv(1024)
            if not chunk:
                raise ConnectionError('WRDS bridge proxy closed during CONNECT')
            header.extend(chunk)
            if len(header) > 16384:
                raise ConnectionError('WRDS bridge proxy response is oversized')
        first_line = bytes(header).split(b'\r\n', 1)[0]
        parts = first_line.split()
        if len(parts) < 2 or parts[1] != b'200':
            status = parts[1].decode('ascii', 'replace') if len(parts) > 1 else '?'
            raise ConnectionError(
                f'WRDS bridge proxy CONNECT failed with HTTP {status}')
        return sock, token
    except Exception:
        sock.close()
        raise


def _new_unix_socket_or_none():
    """Return a Unix socket, or None only when the syscall is unavailable."""
    if not hasattr(socket, 'AF_UNIX'):
        return None
    try:
        return socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    except OSError as exc:
        if exc.errno in _BRIDGE_FALLBACK_ERRNOS:
            return None
        raise


def wrds_requires_bridge():
    """Whether this runtime cannot create the preferred Unix transport."""
    sock = _new_unix_socket_or_none()
    if sock is None:
        return True
    sock.close()
    return False


def _connect(timeout, force_bridge=False):
    """Connect to the host-wide daemon across sandbox boundaries.

    Network-isolated sandboxes have a private 127.0.0.1, but their approved
    read-only home view is shared with the host. Linux SRT blocks AF_UNIX at
    socket creation, so only that explicit syscall denial selects the
    authenticated bridge fallback.
    """
    if not force_bridge:
        sock = _new_unix_socket_or_none()
        if sock is not None:
            sock.settimeout(timeout)
            try:
                sock.connect(SOCKET_FILE)
                return sock, None
            except OSError:
                sock.close()
                raise
    return _connect_bridge(timeout)


def _send_request(request, timeout=300, force_bridge=False):
    """Send a request to the wrds_server and return the response."""
    request = {**request, 'safety_protocol': SAFETY_PROTOCOL}
    sock, bridge_token = _connect(timeout, force_bridge=force_bridge)
    try:
        if bridge_token is not None:
            request = {
                **request,
                'bridge_protocol': BRIDGE_PROTOCOL,
                'bridge_token': bridge_token,
            }
            sock.sendall(
                BRIDGE_PREFACE_MAGIC + bridge_token.encode('ascii') + b'\n')
        data = json.dumps(request).encode()
        sock.sendall(struct.pack('!Q', len(data)))
        sock.sendall(data)

        # Receive response
        response_deadline = time.monotonic() + timeout
        raw_len = _recv_exact(sock, 8, response_deadline)
        msg_len = struct.unpack('!Q', raw_len)[0]
        if msg_len <= 0 or msg_len > MAX_RESPONSE:
            raise ConnectionError(
                f'WRDS response frame must be 1..{MAX_RESPONSE} bytes')

        chunks = []
        received = 0
        while received < msg_len:
            chunk = _recv_exact(
                sock, min(65536, msg_len - received), response_deadline)
            chunks.append(chunk)
            received += len(chunk)
        return json.loads(b''.join(chunks).decode())
    finally:
        sock.close()


def wrds_bridge_ping():
    """Host-side readiness check for the authenticated fallback bridge."""
    try:
        resp = _send_request(
            {'cmd': 'safety_hello_v6'}, timeout=5, force_bridge=True)
        return (resp.get('status') == 'ok' and
                resp.get('safety_protocol') == SAFETY_PROTOCOL)
    except (ConnectionRefusedError, OSError, WrdsSafetyBlocked,
            ConnectionError):
        return False

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
    resp = _send_request({'cmd': 'safety_hello_v6'}, timeout=5)
    _validate_protocol(resp)
    if resp.get('status') != 'ok':
        raise WrdsSafetyBlocked(resp.get('msg') or _safety_message())


def _ensure_safe_server(allow_auth=False):
    """Handshake before any command an old daemon could execute unsafely."""
    _safety_hello()
    resp = _send_request({'cmd': 'safe_ping_v6'}, timeout=5)
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
        resp = _send_request({'cmd': 'safe_ping_v6'}, timeout=5)
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
        resp = _send_request({'cmd': 'safe_ping_v6'}, timeout=5)
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
        {'cmd': 'safe_query_v6', 'sql': sql, 'timeout': timeout}, timeout=timeout)
    if resp['status'] == 'error':
        _raise("WRDS query failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_list_tables(library):
    """List tables in a WRDS library."""
    resp = _checked_request({'cmd': 'safe_list_tables_v6', 'library': library})
    if resp['status'] == 'error':
        _raise("WRDS list_tables failed", resp)
    return resp['tables']

def wrds_list_libraries():
    """List WRDS libraries via the persistent server."""
    resp = _checked_request({'cmd': 'safe_list_libraries_v6'})
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
        'cmd': 'safe_get_table_v6', 'library': library, 'table': table,
        'kwargs': kwargs,
    })
    if resp['status'] == 'error':
        _raise("WRDS get_table failed", resp)
    from io import StringIO
    return pd.read_json(StringIO(resp['data']), orient='split')

def wrds_describe(library, table):
    """Describe a WRDS table (columns, types, row count)."""
    resp = _checked_request(
        {'cmd': 'safe_describe_v6', 'library': library, 'table': table})
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
