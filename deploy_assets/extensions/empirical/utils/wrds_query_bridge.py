#!/usr/bin/env python3
"""Authenticated TCP-to-Unix bridge for sandboxed WRDS query clients.

Claude's Linux sandbox deliberately blocks ``socket(AF_UNIX, ...)`` with a
seccomp filter.  The sandbox's authenticated HTTP proxy can still reach host
loopback, so this process exposes the existing query-only Unix endpoint on a
second loopback port.  A rotating 256-bit capability in host-owned WRDS state
prevents other local OS users from using the TCP listener.

The bridge has no database credentials and implements no lifecycle commands.
It accepts only the v5 query command set, strips its own authentication fields,
and relays the original bounded frame to the existing Unix-domain daemon.
"""

import errno
import hmac
import json
import os
import secrets
import signal
import socket
import stat
import subprocess
import threading
import time
from pathlib import Path

SERVER_PORT = 23847
BRIDGE_PORT = 23848
BRIDGE_PROTOCOL = "wrds-query-bridge-v1"
BRIDGE_PREFACE_MAGIC = b"WRDS-BRIDGE-V1:"
SAFETY_PROTOCOL = "wrds-auth-latch-v5"
STATE_DIR = os.path.join(
    os.path.expanduser("~"), ".local", "state", "zeropaper", "wrds")
SOCKET_FILE = os.path.join(STATE_DIR, f"wrds_server_{SERVER_PORT}.sock")
TOKEN_FILE = os.path.join(STATE_DIR, f"wrds_query_bridge_{BRIDGE_PORT}.token")
PID_FILE = os.path.join(STATE_DIR, f"wrds_query_bridge_{BRIDGE_PORT}.pid")
MAX_MSG = 10 * 1024 * 1024
MAX_RESPONSE = 90 * 1024 * 1024
CLIENT_IO_TIMEOUT = 15
AUTH_PREFACE_TIMEOUT = 1
# A WRDS statement may legitimately run for the daemon's full five-minute
# deadline.  Keep untrusted client framing short, but never reuse that timeout
# while awaiting the authenticated daemon's query response.
UPSTREAM_RESPONSE_TIMEOUT = 315
MAX_CLIENT_THREADS = 32
MAX_AUTH_THREADS = 64
ALLOWED_COMMANDS = frozenset({
    "safety_hello_v5",
    "safe_ping_v5",
    "safe_query_v5",
    "safe_list_tables_v5",
    "safe_list_libraries_v5",
    "safe_get_table_v5",
    "safe_describe_v5",
})


def _prepare_state_dir():
    """Create/validate every state ancestor without following symlinks."""
    parent = os.path.abspath(STATE_DIR)
    parts = [part for part in parent.split(os.sep) if part]
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    fd = os.open(os.sep, flags)
    try:
        for part in parts:
            try:
                next_fd = os.open(part, flags, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(part, mode=0o700, dir_fd=fd)
                next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        info = os.fstat(fd)
        if (not stat.S_ISDIR(info.st_mode) or
                (hasattr(os, "getuid") and info.st_uid != os.getuid()) or
                info.st_mode & 0o022):
            raise OSError("unsafe WRDS bridge state directory")
    finally:
        os.close(fd)


def _process_start_token(pid):
    try:
        raw_stat = Path(f"/proc/{pid}/stat").read_text(encoding="ascii")
        fields_after_comm = raw_stat.rsplit(")", 1)[1].split()
        start_ticks = fields_after_comm[19]
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(
            encoding="ascii").strip()
        return f"proc:{boot_id}:{start_ticks}"
    except (OSError, IndexError):
        try:
            value = subprocess.run(
                ["/bin/ps", "-o", "lstart=", "-p", str(pid)],
                capture_output=True, text=True, timeout=5, check=False,
            ).stdout.strip()
        except Exception:
            value = ""
        return f"ps:{value}" if value else None


def _recv_exact(conn, size):
    chunks = []
    received = 0
    while received < size:
        chunk = conn.recv(size - received)
        if not chunk:
            raise ConnectionError(
                f"incomplete WRDS bridge frame ({received}/{size} bytes)")
        chunks.append(chunk)
        received += len(chunk)
    return b"".join(chunks)


def _recv_exact_before(conn, size, timeout):
    """Receive a small authentication preface under a total wall deadline."""
    deadline = time.monotonic() + timeout
    chunks = []
    received = 0
    while received < size:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("WRDS bridge authentication timed out")
        conn.settimeout(remaining)
        chunk = conn.recv(size - received)
        if not chunk:
            raise ConnectionError("incomplete WRDS bridge authentication")
        chunks.append(chunk)
        received += len(chunk)
    return b"".join(chunks)


def _recv_frame(conn, maximum):
    raw_len = _recv_exact(conn, 8)
    try:
        size = int(raw_len.decode("ascii").strip())
    except (UnicodeError, ValueError) as exc:
        raise ValueError("invalid WRDS bridge frame length") from exc
    if size <= 0 or size > maximum:
        raise ValueError(f"WRDS bridge frame must be 1..{maximum} bytes")
    return _recv_exact(conn, size)


def _send_frame(conn, payload):
    conn.sendall(f"{len(payload):8d}".encode("ascii") + payload)


def _atomic_state_file(path, payload, mode):
    """Publish one protected regular file without following path aliases."""
    _prepare_state_dir()
    parent = os.path.dirname(path)
    if os.path.abspath(parent) != os.path.abspath(STATE_DIR):
        raise OSError("WRDS bridge state escaped the protected directory")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
             getattr(os, "O_NOFOLLOW", 0))
    dir_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                 getattr(os, "O_NOFOLLOW", 0))
    dir_fd = os.open(parent, dir_flags)
    leaf = os.path.basename(path)
    temp_leaf = f".{leaf}.{os.getpid()}.{secrets.token_hex(8)}"
    fd = -1
    try:
        fd = os.open(temp_leaf, flags, mode, dir_fd=dir_fd)
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            fd = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_leaf, leaf, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
        temp_leaf = None
        os.fsync(dir_fd)
        info = os.stat(leaf, dir_fd=dir_fd, follow_symlinks=False)
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
                (hasattr(os, "getuid") and info.st_uid != os.getuid()) or
                stat.S_IMODE(info.st_mode) != mode):
            raise OSError(f"unsafe WRDS bridge state file: {path}")
        return (info.st_dev, info.st_ino, info.st_ctime_ns)
    finally:
        if fd != -1:
            os.close(fd)
        if temp_leaf is not None:
            try:
                os.unlink(temp_leaf, dir_fd=dir_fd)
            except OSError:
                pass
        os.close(dir_fd)


def _unlink_if_identity(path, identity):
    try:
        info = os.lstat(path)
        current = (info.st_dev, info.st_ino, info.st_ctime_ns)
        if current == identity:
            os.unlink(path)
    except OSError:
        pass


def _error_payload(message):
    return json.dumps({
        "status": "error",
        "error_kind": "safety",
        "msg": message,
        "safety_protocol": SAFETY_PROTOCOL,
        "bridge_protocol": BRIDGE_PROTOCOL,
    }).encode("utf-8")


def _relay_client(conn, token, query_slots, auth_slots=None):
    query_slot_acquired = False
    try:
        expected_preface = BRIDGE_PREFACE_MAGIC + token.encode("ascii") + b"\n"
        supplied_preface = _recv_exact_before(
            conn, len(expected_preface), AUTH_PREFACE_TIMEOUT)
        if not hmac.compare_digest(supplied_preface, expected_preface):
            _send_frame(conn, _error_payload(
                "WRDS bridge authentication failed; relaunch through "
                "./launch.sh to refresh the protected query capability."))
            return
        if not query_slots.acquire(blocking=False):
            _send_frame(conn, _error_payload(
                "WRDS query bridge is busy; retry after another query finishes."))
            return
        query_slot_acquired = True
        conn.settimeout(CLIENT_IO_TIMEOUT)
        raw_request = _recv_frame(conn, MAX_MSG)
        request = json.loads(raw_request.decode("utf-8"))
        if not isinstance(request, dict):
            raise ValueError("WRDS bridge request must be an object")
        supplied = request.pop("bridge_token", "")
        protocol = request.pop("bridge_protocol", None)
        if (protocol != BRIDGE_PROTOCOL or not isinstance(supplied, str) or
                not hmac.compare_digest(supplied, token)):
            _send_frame(conn, _error_payload(
                "WRDS bridge authentication failed; relaunch through "
                "./launch.sh to refresh the protected query capability."))
            return
        if request.get("cmd") not in ALLOWED_COMMANDS:
            _send_frame(conn, _error_payload(
                "WRDS bridge accepts query protocol commands only."))
            return
        if request.get("safety_protocol") != SAFETY_PROTOCOL:
            _send_frame(conn, _error_payload(
                "WRDS bridge client safety protocol mismatch."))
            return

        upstream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            upstream.settimeout(UPSTREAM_RESPONSE_TIMEOUT)
            upstream.connect(SOCKET_FILE)
            encoded = json.dumps(request).encode("utf-8")
            _send_frame(upstream, encoded)
            response = _recv_frame(upstream, MAX_RESPONSE)
        finally:
            upstream.close()
        _send_frame(conn, response)
    except Exception as exc:
        try:
            _send_frame(conn, _error_payload(
                f"WRDS query bridge failed safely: {exc}"))
        except Exception:
            pass
    finally:
        conn.close()
        if query_slot_acquired:
            query_slots.release()
        if auth_slots is not None:
            auth_slots.release()


def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listener.bind(("127.0.0.1", BRIDGE_PORT))
        listener.listen(32)
    except OSError as exc:
        listener.close()
        if exc.errno == errno.EADDRINUSE:
            print("[wrds_bridge] another host bridge owns 127.0.0.1:23848",
                  flush=True)
            return 3
        raise

    token = secrets.token_hex(32)
    token_identity = _atomic_state_file(
        TOKEN_FILE, (token + "\n").encode("ascii"), 0o400)
    birth = _process_start_token(os.getpid()) or "unknown"
    pid_payload = json.dumps({"pid": os.getpid(), "start": birth}) + "\n"
    pid_identity = _atomic_state_file(
        PID_FILE, pid_payload.encode("ascii"), 0o600)

    stopping = threading.Event()

    def stop(_signum, _frame):
        stopping.set()
        try:
            listener.close()
        except OSError:
            pass

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    query_slots = threading.BoundedSemaphore(MAX_CLIENT_THREADS)
    auth_slots = threading.BoundedSemaphore(MAX_AUTH_THREADS)
    print(
        f"[wrds_bridge] query-only bridge listening on "
        f"127.0.0.1:{BRIDGE_PORT}", flush=True)
    try:
        while not stopping.is_set():
            try:
                conn, _address = listener.accept()
            except OSError as exc:
                if stopping.is_set() or exc.errno in (errno.EBADF, errno.EINVAL):
                    break
                raise
            if not auth_slots.acquire(blocking=False):
                conn.close()
                continue
            threading.Thread(
                target=_relay_client,
                args=(conn, token, query_slots, auth_slots), daemon=True,
            ).start()
    finally:
        try:
            listener.close()
        except OSError:
            pass
        _unlink_if_identity(TOKEN_FILE, token_identity)
        _unlink_if_identity(PID_FILE, pid_identity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
