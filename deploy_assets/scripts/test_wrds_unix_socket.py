#!/usr/bin/env python3
"""Offline adversarial regression for the cross-sandbox WRDS transport."""

import json
import errno
import io
import multiprocessing
import os
import socket
import stat
import struct
import subprocess
import sys
import tempfile
import time
import threading
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
UTILS = ROOT / "extensions" / "empirical" / "utils"
sys.path.insert(0, str(UTILS))

import wrds_client as client  # noqa: E402
import wrds_query_bridge as bridge  # noqa: E402
import wrds_server as server  # noqa: E402


class HealthyState:
    def healthcheck(self):
        return True, "SELECT 1 ok"

    def auth_blocked(self):
        return False

    def unblock(self):
        return True, "operator retry accepted"


class FailingResponseSocket:
    """Socket double that permits one partial payload write, then times out."""

    def __init__(self, incoming):
        self.incoming = bytearray(incoming)
        self.send_calls = 0
        self.closed = False
        self.timeouts = []

    def recv(self, size):
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def send(self, payload):
        self.send_calls += 1
        if self.send_calls == 1:
            return len(payload)  # complete frame header
        if self.send_calls == 2:
            return min(5, len(payload))
        raise TimeoutError("simulated stalled response peer")

    def settimeout(self, value):
        self.timeouts.append(value)

    def close(self):
        self.closed = True


class TricklingProxySocket:
    """Proxy double whose byte trickle must not reset a setup deadline."""

    def __init__(self):
        self.closed = False
        self.timeouts = []

    def settimeout(self, value):
        self.timeouts.append(value)

    def sendall(self, payload):
        pass

    def recv(self, size):
        time.sleep(0.03)
        return b"x"

    def close(self):
        self.closed = True


def _capture_error(errors, operation):
    try:
        operation()
    except Exception as exc:
        errors.append(exc)


def compete_for_lock(state_dir, start, release, results):
    """Spawn-safe contender used to prove exclusive atomic publication."""
    base = Path(state_dir)
    server.AUTH_BLOCK_FILE = str(base / "authblock")
    server.CACHE_AUTH_BLOCK_FILE = str(base / "cache-authblock")
    server.LEGACY_AUTH_BLOCK_FILE = str(base / "legacy-authblock")
    server.SOCKET_FILE = str(base / "server.sock")
    server.LOCK_FILE = str(base / "server.lock")
    server.PID_FILE = str(base / "server.pid")
    start.wait(timeout=10)
    try:
        identity = server._acquire_instance_lock()
    except server.WrdsInstanceBusy:
        results.put("busy")
        return
    results.put("acquired")
    release.wait(timeout=10)
    server._remove_lock_if_identity(identity)


def request_over_socketpair(state, cmd):
    left, right = socket.socketpair()
    payload = json.dumps({"cmd": cmd,
                          "safety_protocol": server.SAFETY_PROTOCOL}).encode()
    left.sendall(struct.pack("!Q", len(payload)) + payload)
    worker = threading.Thread(
        target=server.handle_client,
        args=(right, state),
        daemon=True,
    )
    worker.start()
    size = struct.unpack("!Q", client._recv_exact(left, 8))[0]
    chunks = []
    while sum(map(len, chunks)) < size:
        chunks.append(left.recv(size - sum(map(len, chunks))))
    left.close()
    worker.join(timeout=2)
    assert not worker.is_alive()
    return json.loads(b"".join(chunks).decode())


def main():
    if not hasattr(socket, "AF_UNIX"):
        print("SKIP: platform has no AF_UNIX")
        return

    with tempfile.TemporaryDirectory(prefix="wrds-unix-test-") as temp:
        state_dir = Path(temp) / "private"
        cache_dir = Path(temp) / "cache"
        cache_dir.mkdir(mode=0o700)
        os.chmod(cache_dir, 0o700)
        server.AUTH_BLOCK_FILE = str(state_dir / "authblock")
        server.CACHE_AUTH_BLOCK_FILE = str(cache_dir / "cache-authblock")
        server.LEGACY_AUTH_BLOCK_FILE = str(state_dir / "legacy-authblock")
        server.SOCKET_FILE = str(state_dir / "server.sock")
        server.LOCK_FILE = str(state_dir / "server.lock")
        server.PID_FILE = str(state_dir / "server.pid")
        client.SOCKET_FILE = server.SOCKET_FILE
        # Atomic creation, not advisory flock, is authoritative across network
        # namespaces. A read-only observer cannot hold or recreate it.
        lock = server._acquire_instance_lock()
        try:
            assert stat.S_IMODE(os.lstat(server.LOCK_FILE).st_mode) == 0o400
            try:
                fd = os.open(server.LOCK_FILE, os.O_RDWR)
            except PermissionError:
                pass
            else:
                os.close(fd)
                raise AssertionError("v4-style O_RDWR open could rewrite v5 marker")
            try:
                server._acquire_instance_lock()
                raise AssertionError("second singleton lock unexpectedly succeeded")
            except server.WrdsInstanceBusy:
                pass
        finally:
            assert server._remove_lock_if_identity(lock)

        # The intermediate v4 flock marker was plain `<pid>\n`: a live or
        # recycled PID remains fail-closed, while a provably dead owner
        # migrates through normal stale cleanup.
        Path(server.LOCK_FILE).write_text(str(os.getpid()) + "\n",
                                          encoding="ascii")
        os.chmod(server.LOCK_FILE, 0o600)
        try:
            server._acquire_instance_lock()
            raise AssertionError("live legacy lock owner was replaced")
        except server.WrdsInstanceBusy:
            pass
        Path(server.LOCK_FILE).write_text("999999999\n", encoding="ascii")
        os.chmod(server.LOCK_FILE, 0o600)
        migrated = server._acquire_instance_lock()
        assert server._remove_lock_if_identity(migrated)

        context = multiprocessing.get_context("spawn")
        start = context.Event()
        release = context.Event()
        results = context.Queue()
        contenders = [context.Process(
            target=compete_for_lock,
            args=(str(state_dir), start, release, results),
        ) for _ in range(2)]
        for contender in contenders:
            contender.start()
        start.set()
        outcomes = sorted(results.get(timeout=10) for _ in contenders)
        assert outcomes == ["acquired", "busy"], outcomes
        release.set()
        for contender in contenders:
            contender.join(timeout=10)
            assert contender.exitcode == 0, contender.exitcode

        os.chmod(state_dir, 0o500)
        try:
            try:
                server._acquire_instance_lock()
                raise AssertionError("read-only state unexpectedly created lock")
            except server.WrdsLatchError:
                pass
        finally:
            os.chmod(state_dir, 0o700)

        # A released TCP listener is rejected, while SO_REUSEADDR permits an
        # immediate upgrade after a stopped accepted connection left TIME_WAIT.
        legacy_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        legacy_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        legacy_tcp.bind(("127.0.0.1", 0))
        legacy_tcp.listen(1)
        old_port = server.PORT
        server.PORT = legacy_tcp.getsockname()[1]
        try:
            try:
                server._bind_legacy_refusal_listener()
                raise AssertionError("live legacy TCP daemon was ignored")
            except server.WrdsInstanceBusy:
                pass
        finally:
            legacy_tcp.close()

        timewait_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        timewait_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        timewait_listener.bind(("127.0.0.1", server.PORT))
        timewait_listener.listen(1)
        timewait_client = socket.create_connection(("127.0.0.1", server.PORT))
        accepted = timewait_listener.accept()[0]
        accepted.close()
        timewait_client.close()
        timewait_listener.close()

        tcp_guard = server._bind_legacy_refusal_listener()
        try:
            refusal_worker = threading.Thread(
                target=server._legacy_refusal_loop,
                args=(tcp_guard,), daemon=True)
            refusal_worker.start()
            old_client = socket.create_connection(("127.0.0.1", server.PORT))
            request = json.dumps({"cmd": "safety_hello_v2"}).encode()
            old_client.sendall(f"{len(request):8d}".encode() + request)
            response_size = int(old_client.recv(8).decode().strip())
            response = json.loads(old_client.recv(response_size).decode())
            old_client.close()
            assert response["error_kind"] == "safety"
            assert response["safety_protocol"] == server.SAFETY_PROTOCOL

            competitor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            competitor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                try:
                    competitor.bind(("127.0.0.1", server.PORT))
                    competitor.listen(1)
                    raise AssertionError("legacy TCP port reservation was stolen")
                except OSError:
                    pass
            finally:
                competitor.close()
        finally:
            tcp_guard.close()
            server.PORT = old_port

        # Process discovery is transport-independent, so an old daemon in a
        # different network namespace is still visible before v5 connects.
        legacy_dir = Path(temp) / "legacy-process"
        legacy_dir.mkdir()
        legacy_script = legacy_dir / "wrds_server.py"
        legacy_script.write_text("import time; time.sleep(30)\n", encoding="utf-8")
        legacy_process = subprocess.Popen([sys.executable, str(legacy_script)])
        try:
            for _ in range(50):
                if legacy_process.pid in server._legacy_server_pids():
                    break
                time.sleep(0.02)
            assert legacy_process.pid in server._legacy_server_pids()
        finally:
            legacy_process.terminate()
            legacy_process.wait(timeout=5)

        # Merely mentioning that filename as data (or opening it in an editor)
        # is not a daemon launch and must not block an upgrade.
        mention_process = subprocess.Popen([
            sys.executable, "-c", "import time; time.sleep(30)",
            str(legacy_script),
        ])
        try:
            time.sleep(0.05)
            assert mention_process.pid not in server._legacy_server_pids()
        finally:
            mention_process.terminate()
            mention_process.wait(timeout=5)

        # A same-user system session helper can deliberately hide its cwd and
        # ns/net link. Classify it through the first readable ancestor before
        # namespace inspection: a systemd-style root cwd is irrelevant, while
        # an opaque child of a deployed launcher remains a candidate.
        fake_proc = Path(temp) / "fake-proc"
        opaque_entry = fake_proc / "3205"
        parent_entry = fake_proc / "3204"
        opaque_entry.mkdir(parents=True)
        parent_entry.mkdir()
        (opaque_entry / "status").write_text(
            "Name:\t(sd-pam)\nPPid:\t3204\n", encoding="utf-8")

        def opaque_readlink(path):
            if Path(path) == opaque_entry / "cwd":
                raise PermissionError("ptrace-protected session helper")
            if Path(path) == parent_entry / "cwd":
                return "/"
            raise AssertionError(f"unexpected readlink: {path}")

        with mock.patch.object(server.os, "readlink",
                               side_effect=opaque_readlink):
            assert not server._process_is_deployed_wrds_runtime(
                opaque_entry, fake_proc)

        deployed_parent = Path(temp) / "opaque-deployment"
        (deployed_parent / "code" / "utils").mkdir(parents=True)
        (deployed_parent / ".deploy_manifest.json").write_text(
            "{}\n", encoding="utf-8")
        (deployed_parent / "code" / "utils" / "wrds_client.py").write_text(
            "# marker\n", encoding="utf-8")

        def deployed_parent_readlink(path):
            if Path(path) == opaque_entry / "cwd":
                raise PermissionError("opaque sandbox child")
            if Path(path) == parent_entry / "cwd":
                return str(deployed_parent)
            raise AssertionError(f"unexpected readlink: {path}")

        with mock.patch.object(server.os, "readlink",
                               side_effect=deployed_parent_readlink):
            assert server._process_is_deployed_wrds_runtime(
                opaque_entry, fake_proc)

        changed_cwd_entry = fake_proc / "3305"
        changed_cwd_entry.mkdir()
        (changed_cwd_entry / "status").write_text(
            "Name:\tpython\nPPid:\t3204\n", encoding="utf-8")

        def changed_cwd_readlink(path):
            if Path(path) == changed_cwd_entry / "cwd":
                return "/tmp"
            if Path(path) == parent_entry / "cwd":
                return str(deployed_parent)
            raise AssertionError(f"unexpected readlink: {path}")

        with mock.patch.object(server.os, "readlink",
                               side_effect=changed_cwd_readlink):
            assert server._process_is_deployed_wrds_runtime(
                changed_cwd_entry, fake_proc)

        # First-upgrade quiescence covers a released client paused after its
        # latch read but before Popen, when no wrds_server.py exists to scan.
        original_foreign_scan = server._foreign_network_namespace_pids
        server._foreign_network_namespace_pids = lambda: [424242]
        try:
            try:
                server._refuse_live_legacy_processes()
                raise AssertionError("live foreign sandbox was ignored")
            except server.WrdsInstanceBusy:
                pass
        finally:
            server._foreign_network_namespace_pids = original_foreign_scan

        # The exact durable cache latch released v2/v3 starters already read
        # stays armed for v5's lifetime. V5 recognizes its own marker, and a
        # dead marker is identity-safely retired on the next v5 start.
        compat_identity = server._write_compat_guard()
        compat_message = Path(server.CACHE_AUTH_BLOCK_FILE).read_text(
            encoding="utf-8")
        assert compat_message.startswith(server.COMPAT_ACTIVE_PREFIX)
        assert stat.S_IMODE(os.stat(server.CACHE_AUTH_BLOCK_FILE).st_mode) == 0o400
        assert stat.S_IMODE(cache_dir.stat().st_mode) == 0o500
        try:
            os.unlink(server.CACHE_AUTH_BLOCK_FILE)
            raise AssertionError("active compatibility guard was cache-writable")
        except PermissionError:
            pass
        try:
            fd = os.open(server.CACHE_AUTH_BLOCK_FILE, os.O_WRONLY)
        except PermissionError:
            pass
        else:
            os.close(fd)
            raise AssertionError("active compatibility guard was directly writable")
        assert server._read_auth_block() is None
        server._clear_auth_block(preserve_compat=True)
        assert Path(server.CACHE_AUTH_BLOCK_FILE).exists()
        assert server._remove_compat_guard(compat_identity)
        assert stat.S_IMODE(cache_dir.stat().st_mode) == 0o700

        # A released daemon's concurrent write-ahead marker wins publication,
        # is never overwritten, and is copied into protected v5 latch state.
        old_attempt = "WRDS_LOGIN_ATTEMPT_IN_PROGRESS pid=999999999\nold attempt"
        Path(server.CACHE_AUTH_BLOCK_FILE).write_text(old_attempt, encoding="utf-8")
        os.chmod(server.CACHE_AUTH_BLOCK_FILE, 0o600)
        retained_identity = server._write_compat_guard()
        assert Path(server.CACHE_AUTH_BLOCK_FILE).read_text(
            encoding="utf-8") == old_attempt
        assert stat.S_IMODE(os.stat(server.CACHE_AUTH_BLOCK_FILE).st_mode) == 0o400
        try:
            server._verify_compat_guard()
            raise AssertionError("released auth attempt was treated as v5 guard")
        except server.WrdsInstanceBusy:
            pass
        assert Path(server.AUTH_BLOCK_FILE).read_text(encoding="utf-8") == old_attempt
        server._clear_auth_block(preserve_compat=True)
        assert server._read_auth_block() is None
        adopted = server._adopted_legacy_guard()
        assert adopted == old_attempt
        server._verify_compat_guard(adopted)
        assert server._remove_compat_guard(retained_identity)

        Path(server.CACHE_AUTH_BLOCK_FILE).write_text(
            f"{server.COMPAT_ACTIVE_PREFIX}999999999 start=dead\n",
            encoding="utf-8")
        os.chmod(server.CACHE_AUTH_BLOCK_FILE, 0o600)
        assert server._read_auth_block() is None
        assert Path(server.CACHE_AUTH_BLOCK_FILE).exists()
        replacement_identity = server._write_compat_guard()
        assert Path(server.CACHE_AUTH_BLOCK_FILE).read_text(
            encoding="utf-8").startswith(server.COMPAT_ACTIVE_PREFIX)
        assert server._remove_compat_guard(replacement_identity)

        # A live socket is never unlinked or replaced.
        listener, identity = server._bind_unix_server()
        try:
            try:
                server._bind_unix_server()
                raise AssertionError("live Unix socket was replaced")
            except server.WrdsInstanceBusy:
                pass
            assert server._socket_identity(os.lstat(server.SOCKET_FILE)) == identity
        finally:
            listener.close()

        # Once its listener is gone, that exact stale socket is replaced.
        replacement, replacement_identity = server._bind_unix_server()
        mode = stat.S_IMODE(os.lstat(server.SOCKET_FILE).st_mode)
        assert mode == 0o600, oct(mode)

        state = HealthyState()

        def serve_ping():
            # wrds_ping performs a DB-free hello and then safe_ping.
            for _ in range(2):
                server.handle_client(replacement.accept()[0], state)

        worker = threading.Thread(target=serve_ping, daemon=True)
        worker.start()
        assert client.wrds_ping() is True
        worker.join(timeout=2)
        assert not worker.is_alive()
        replacement.close()

        # Linux Claude blocks socket(AF_UNIX) with seccomp.  Its authenticated
        # loopback HTTP proxy can reach a host-only TCP bridge, which must
        # require a protected capability and forward query commands only.
        bridge_upstream, bridge_upstream_identity = server._bind_unix_server()
        bridge_token = "a" * 64
        bridge.STATE_DIR = str(state_dir)
        bridge.SOCKET_FILE = server.SOCKET_FILE
        bridge.TOKEN_FILE = str(state_dir / "bridge.token")
        client.BRIDGE_TOKEN_FILE = bridge.TOKEN_FILE
        bridge_publish_victim = state_dir / "bridge-publish-victim"
        bridge_publish_victim.write_text("preserve", encoding="ascii")
        os.symlink(bridge_publish_victim, bridge.TOKEN_FILE)
        bridge._atomic_state_file(
            bridge.TOKEN_FILE, (bridge_token + "\n").encode("ascii"), 0o400)
        assert bridge_publish_victim.read_text(encoding="ascii") == "preserve"
        assert not os.path.islink(bridge.TOKEN_FILE)
        assert stat.S_IMODE(os.stat(bridge.TOKEN_FILE).st_mode) == 0o400

        proxy_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_listener.bind(("127.0.0.1", 0))
        proxy_listener.listen(1)
        proxy_port = proxy_listener.getsockname()[1]
        expected_auth = "Basic dXNlcjpwYXNz"
        bridge_slots = threading.BoundedSemaphore(1)

        def serve_bridge_upstream():
            server.handle_client(bridge_upstream.accept()[0], state)

        def serve_authenticated_proxy():
            conn, _ = proxy_listener.accept()
            header = bytearray()
            while b"\r\n\r\n" not in header:
                header.extend(conn.recv(1024))
            text = header.decode("ascii")
            assert f"CONNECT 127.0.0.1:{client.BRIDGE_PORT}" in text
            assert f"Proxy-Authorization: {expected_auth}" in text
            conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            bridge._relay_client(conn, bridge_token, bridge_slots)

        upstream_worker = threading.Thread(
            target=serve_bridge_upstream, daemon=True)
        proxy_worker = threading.Thread(
            target=serve_authenticated_proxy, daemon=True)
        upstream_worker.start()
        proxy_worker.start()
        with mock.patch.dict(os.environ, {
                "HTTPS_PROXY": f"http://user:pass@127.0.0.1:{proxy_port}",
                "HTTP_PROXY": "",
        }, clear=False):
            response = client._send_request(
                {"cmd": "safety_hello_v7"}, timeout=5, force_bridge=True)
        assert response["status"] == "ok"
        upstream_worker.join(timeout=2)
        proxy_worker.join(timeout=2)
        assert not upstream_worker.is_alive()
        assert not proxy_worker.is_alive()
        proxy_listener.close()

        # The client must never send its query capability through an arbitrary
        # ambient proxy; it falls back to fixed host loopback instead.
        with mock.patch.dict(os.environ, {
                "HTTPS_PROXY": "http://user:secret@example.invalid:3128",
        }, clear=False):
            assert client._proxy_endpoint() is None

        # Proxy CONNECT uses one total setup clock; trickled header bytes do
        # not reset a per-recv timeout indefinitely.
        trickling_proxy = TricklingProxySocket()
        trickle_started = time.monotonic()
        with mock.patch.object(
                client, "_read_bridge_token", return_value=bridge_token), \
                mock.patch.object(
                    client, "_proxy_endpoint",
                    return_value=("127.0.0.1", proxy_port, None)), \
                mock.patch.object(
                    client.socket, "create_connection",
                    return_value=trickling_proxy):
            try:
                client._connect_bridge(0.05)
                raise AssertionError("proxy trickle reset the setup deadline")
            except TimeoutError:
                pass
        assert time.monotonic() - trickle_started < 0.15
        assert trickling_proxy.closed

        def bridge_pair_request(token, command):
            left, right = socket.socketpair()
            slots = threading.BoundedSemaphore(1)
            request = json.dumps({
                "cmd": command,
                "safety_protocol": server.SAFETY_PROTOCOL,
                "bridge_protocol": bridge.BRIDGE_PROTOCOL,
                "bridge_token": token,
            }).encode()
            left.sendall(
                bridge.BRIDGE_PREFACE_MAGIC + token.encode("ascii") + b"\n")
            left.sendall(struct.pack("!Q", len(request)) + request)
            relay = threading.Thread(
                target=bridge._relay_client,
                args=(right, bridge_token, slots), daemon=True)
            relay.start()
            size = struct.unpack("!Q", client._recv_exact(left, 8))[0]
            result = json.loads(client._recv_exact(left, size))
            left.close()
            relay.join(timeout=2)
            assert not relay.is_alive()
            return result

        rejected = bridge_pair_request("b" * 64, "safety_hello_v7")
        assert rejected["status"] == "error"
        assert "authentication failed" in rejected["msg"]
        rejected = bridge_pair_request(bridge_token, "safe_unblock_v7")
        assert rejected["status"] == "error"
        assert "query protocol commands only" in rejected["msg"]

        # Authentication is a fixed-size preface with a total deadline. An
        # unauthenticated local slowloris never consumes a query worker slot,
        # and trickling bytes cannot reset the authentication deadline.
        slow_left, slow_right = socket.socketpair()
        slow_slots = threading.BoundedSemaphore(1)
        with mock.patch.object(bridge, "AUTH_PREFACE_TIMEOUT", 0.08):
            slow_worker = threading.Thread(
                target=bridge._relay_client,
                args=(slow_right, bridge_token, slow_slots), daemon=True)
            slow_worker.start()
            for _ in range(3):
                try:
                    slow_left.sendall(b"x")
                except OSError:
                    break
                time.sleep(0.03)
            slow_worker.join(timeout=0.5)
        assert not slow_worker.is_alive()
        assert slow_slots.acquire(blocking=False)
        slow_slots.release()
        slow_left.close()

        # Client framing remains aggressively bounded without imposing that
        # short deadline on a legitimate long-running upstream WRDS query.
        def serve_delayed_bridge_upstream():
            upstream_conn, _ = bridge_upstream.accept()
            time.sleep(0.1)
            server.handle_client(upstream_conn, state)

        delayed_worker = threading.Thread(
            target=serve_delayed_bridge_upstream, daemon=True)
        delayed_worker.start()
        with mock.patch.object(bridge, "CLIENT_IO_TIMEOUT", 0.05), \
                mock.patch.object(
                    bridge, "UPSTREAM_CONTROL_TIMEOUT", 0.5):
            delayed = bridge_pair_request(
                bridge_token, "safety_hello_v7")
        assert delayed["status"] == "ok"
        delayed_worker.join(timeout=2)
        assert not delayed_worker.is_alive()

        # Execution and each transfer hop have distinct wall deadlines.  The
        # fake daemon spends most of the query budget before publishing its
        # header, then pauses again mid-body.  The relay must renew its clock
        # for the upstream body, and the bridge client must allow the relay's
        # buffered upstream transfer before renewing for its downstream body.
        composed_client, composed_relay = socket.socketpair()
        composed_slots = threading.BoundedSemaphore(1)
        composed_payload = json.dumps({
            "status": "ok",
            "columns": ["x"],
            "data": '{"columns":["x"],"index":[0],"data":[[1]]}',
            "shape": [1, 1],
            "recovered": False,
            "safety_protocol": server.SAFETY_PROTOCOL,
        }).encode()

        def serve_composed_upstream():
            upstream_conn, _ = bridge_upstream.accept()
            request_size = struct.unpack(
                "!Q", bridge._recv_exact(upstream_conn, 8))[0]
            bridge._recv_exact(upstream_conn, request_size)
            time.sleep(0.04)
            upstream_conn.sendall(struct.pack("!Q", len(composed_payload)))
            upstream_conn.sendall(composed_payload[:16])
            time.sleep(0.08)
            upstream_conn.sendall(composed_payload[16:])
            upstream_conn.close()

        composed_upstream_worker = threading.Thread(
            target=serve_composed_upstream, daemon=True)
        def serve_composed_relay():
            # Exercise the client allowance for authenticated relay setup and
            # scheduling before the relay opens its upstream Unix socket.
            time.sleep(0.12)
            bridge._relay_client(
                composed_relay, bridge_token, composed_slots)

        composed_relay_worker = threading.Thread(
            target=serve_composed_relay, daemon=True)
        composed_upstream_worker.start()
        composed_relay_worker.start()
        with mock.patch.object(
                client, "_connect",
                return_value=(composed_client, bridge_token)), \
                mock.patch.object(client, "QUERY_TIMEOUT_FLOOR_SECONDS", 0.01), \
                mock.patch.object(client, "RECOVERY_GRACE_SECONDS", 0.02), \
                mock.patch.object(
                    client, "SERVER_REQUEST_ALLOWANCE_SECONDS", 0.01), \
                mock.patch.object(
                    client, "RESPONSE_PREPARATION_GRACE_SECONDS", 0.05), \
                mock.patch.object(
                    client, "BRIDGE_SETUP_ALLOWANCE_SECONDS", 0.15), \
                mock.patch.object(
                    client, "RESPONSE_TRANSFER_BASE_SECONDS", 0.1), \
                mock.patch.object(
                    client, "RESPONSE_TRANSFER_MAX_SECONDS", 0.1), \
                mock.patch.object(bridge, "QUERY_TIMEOUT_FLOOR_SECONDS", 0.01), \
                mock.patch.object(bridge, "RECOVERY_GRACE_SECONDS", 0.02), \
                mock.patch.object(
                    bridge, "UPSTREAM_REQUEST_ALLOWANCE_SECONDS", 0.01), \
                mock.patch.object(
                    bridge, "RESPONSE_PREPARATION_GRACE_SECONDS", 0.1), \
                mock.patch.object(bridge, "RESPONSE_WRITE_BASE_SECONDS", 0.1), \
                mock.patch.object(bridge, "RESPONSE_WRITE_MAX_SECONDS", 0.1):
            composed = client._send_request({
                "cmd": "safe_query_v7",
                "sql": "SELECT 1 AS x",
                "timeout": 0.01,
            }, timeout=0.01, force_bridge=True)
        assert composed["status"] == "ok"
        assert composed["shape"] == [1, 1]
        composed_upstream_worker.join(timeout=2)
        composed_relay_worker.join(timeout=2)
        assert not composed_upstream_worker.is_alive()
        assert not composed_relay_worker.is_alive()

        # A buffering intermediary on the relayed path (the sandbox proxy
        # chain) discards its undelivered bytes the moment the bridge closes
        # first, truncating large responses mid-frame at a wobbling offset
        # (#263/#266).  The bridge must instead hold an authenticated
        # connection open until the client — who closes only after reading
        # the whole frame — closes its end.  The relay double forwards
        # eagerly from the bridge into a userspace buffer, trickles toward
        # the client, and drops the buffer if it ever sees bridge-side EOF
        # while bytes remain undelivered.
        drain_response = json.dumps({
            "status": "ok",
            "columns": ["x"],
            "data": "x" * 600000,
            "shape": [1, 1],
            "recovered": False,
            "safety_protocol": server.SAFETY_PROTOCOL,
        }).encode()

        def serve_drain_upstream():
            upstream_conn, _ = bridge_upstream.accept()
            request_size = struct.unpack(
                "!Q", bridge._recv_exact(upstream_conn, 8))[0]
            bridge._recv_exact(upstream_conn, request_size)
            upstream_conn.sendall(struct.pack("!Q", len(drain_response)))
            upstream_conn.sendall(drain_response)
            upstream_conn.close()

        drain_request = json.dumps({
            "cmd": "safe_query_v7",
            "sql": "SELECT 1 AS x",
            "timeout": 5,
            "safety_protocol": server.SAFETY_PROTOCOL,
            "bridge_protocol": bridge.BRIDGE_PROTOCOL,
            "bridge_token": bridge_token,
        }).encode()
        drain_preface = (bridge.BRIDGE_PREFACE_MAGIC +
                         bridge_token.encode("ascii") + b"\n")
        bridge_conn, relay_to_bridge = socket.socketpair()
        client_conn, relay_to_client = socket.socketpair()
        relay_outcomes = []

        def discarding_relay():
            try:
                inbound = len(drain_preface) + 8 + len(drain_request)
                forwarded = 0
                while forwarded < inbound:
                    chunk = relay_to_client.recv(inbound - forwarded)
                    relay_to_bridge.sendall(chunk)
                    forwarded += len(chunk)
                buffered = bytearray()
                upstream_eof = False
                while True:
                    if not upstream_eof:
                        relay_to_bridge.settimeout(0.001)
                        try:
                            chunk = relay_to_bridge.recv(1 << 20)
                            if chunk:
                                buffered.extend(chunk)
                            else:
                                upstream_eof = True
                        except socket.timeout:
                            pass
                    if upstream_eof and buffered:
                        relay_outcomes.append("discarded")
                        return
                    if buffered:
                        sent = relay_to_client.send(bytes(buffered[:4096]))
                        del buffered[:sent]
                        time.sleep(0.002)
                        continue
                    if upstream_eof:
                        relay_outcomes.append("drained")
                        return
                    relay_to_client.settimeout(0.001)
                    try:
                        if relay_to_client.recv(4096) == b"":
                            relay_outcomes.append("client-closed")
                            return
                    except socket.timeout:
                        pass
            except OSError:
                relay_outcomes.append("relay-error")
            finally:
                relay_to_client.close()
                relay_to_bridge.close()

        drain_slots = threading.BoundedSemaphore(1)
        drain_upstream_worker = threading.Thread(
            target=serve_drain_upstream, daemon=True)
        drain_relay_worker = threading.Thread(
            target=discarding_relay, daemon=True)
        drain_bridge_worker = threading.Thread(
            target=bridge._relay_client,
            args=(bridge_conn, bridge_token, drain_slots), daemon=True)
        drain_upstream_worker.start()
        drain_relay_worker.start()
        drain_bridge_worker.start()
        client_conn.sendall(drain_preface)
        client_conn.sendall(struct.pack("!Q", len(drain_request)))
        client_conn.sendall(drain_request)
        drain_size = struct.unpack(
            "!Q", client._recv_exact(client_conn, 8))[0]
        assert drain_size == len(drain_response)
        drain_received = client._recv_exact(client_conn, drain_size)
        assert drain_received == drain_response
        client_conn.close()
        drain_bridge_worker.join(timeout=5)
        drain_relay_worker.join(timeout=5)
        drain_upstream_worker.join(timeout=5)
        assert not drain_bridge_worker.is_alive()
        assert not drain_relay_worker.is_alive()
        assert not drain_upstream_worker.is_alive()
        assert relay_outcomes and relay_outcomes[0] != "discarded"

        # A planted token symlink is never followed into another owned file.
        os.unlink(bridge.TOKEN_FILE)
        bridge_victim = state_dir / "bridge-victim"
        bridge_victim.write_text("a" * 64 + "\n", encoding="ascii")
        os.chmod(bridge_victim, 0o400)
        os.symlink(bridge_victim, bridge.TOKEN_FILE)
        try:
            client._read_bridge_token()
            raise AssertionError("bridge token symlink was followed")
        except OSError:
            pass
        os.unlink(bridge.TOKEN_FILE)

        # Seccomp's EPERM at AF_UNIX creation selects the bridge; ordinary
        # Unix endpoint errors remain fail-closed rather than hiding outages.
        real_socket_constructor = client.socket.socket
        def deny_unix(family, *args, **kwargs):
            if family == socket.AF_UNIX:
                raise OSError(errno.EPERM, "seccomp")
            return real_socket_constructor(family, *args, **kwargs)
        marker = object()
        with mock.patch.object(client.socket, "socket", side_effect=deny_unix), \
                mock.patch.object(
                    client, "_connect_bridge",
                    return_value=(marker, bridge_token)) as fallback:
            assert client._connect(
                5, bridge_timeout=32) == (marker, bridge_token)
            fallback.assert_called_once_with(32)

        for blocked_errno in client._BRIDGE_FALLBACK_ERRNOS:
            def deny_with_errno(family, *args, _errno=blocked_errno, **kwargs):
                if family == socket.AF_UNIX:
                    raise OSError(_errno, "unavailable Unix transport")
                return real_socket_constructor(family, *args, **kwargs)
            with mock.patch.object(
                    client.socket, "socket", side_effect=deny_with_errno):
                assert client.wrds_requires_bridge() is True
        unix_family = client.socket.AF_UNIX
        del client.socket.AF_UNIX
        try:
            assert client.wrds_requires_bridge() is True
        finally:
            client.socket.AF_UNIX = unix_family

        bridge_upstream.close()
        assert server._socket_identity(
            os.lstat(server.SOCKET_FILE)) == bridge_upstream_identity

        # Lifecycle commands do not exist on any wire endpoint.
        denied = request_over_socketpair(state, "safe_unblock_v7")
        assert denied["status"] == "error"
        assert "unknown command" in denied["msg"]
        denied = request_over_socketpair(state, "safe_shutdown_v7")
        assert denied["status"] == "error"

        # Oversized and incomplete frames are bounded and rejected promptly.
        left, right = socket.socketpair()
        oversized = threading.Thread(
            target=server.handle_client, args=(right, state), daemon=True)
        oversized.start()
        left.sendall(struct.pack("!Q", server.MAX_MSG + 1))
        response_size = struct.unpack("!Q", client._recv_exact(left, 8))[0]
        response = json.loads(left.recv(response_size).decode())
        assert response["status"] == "error"
        assert "frame" in response["msg"]
        left.close()
        oversized.join(timeout=2)
        assert not oversized.is_alive()

        # Client framing tolerates fragmented headers/bodies. The uint64
        # prefix accepts the first formerly-corrupt nine-digit length rather
        # than imposing v5's accidental 90 MiB ceiling.
        client_side, peer_side = socket.socketpair()
        original_connect = client._connect
        client._connect = lambda timeout, force_bridge=False, bridge_timeout=None: (
            client_side, None)
        payload = json.dumps({
            "status": "ok", "msg": "fragmented",
            "safety_protocol": client.SAFETY_PROTOCOL,
        }).encode()
        def fragmented_peer():
            header = b""
            while len(header) < 8:
                header += peer_side.recv(8 - len(header))
            request_size = struct.unpack("!Q", header)[0]
            remaining = request_size
            while remaining:
                part = peer_side.recv(remaining)
                remaining -= len(part)
            response_header = struct.pack("!Q", len(payload))
            for byte in response_header:
                peer_side.sendall(bytes([byte]))
            for offset in range(0, len(payload), 3):
                peer_side.sendall(payload[offset:offset + 3])
            peer_side.close()
        fragmented = threading.Thread(target=fragmented_peer, daemon=True)
        fragmented.start()
        try:
            response = client._send_request({"cmd": "safety_hello_v7"})
            assert response["msg"] == "fragmented"
        finally:
            client._connect = original_connect
        fragmented.join(timeout=2)
        assert not fragmented.is_alive()

        large_frame_client, large_frame_peer = socket.socketpair()
        client._connect = lambda timeout, force_bridge=False, bridge_timeout=None: (
            large_frame_client, None)
        def formerly_oversized_peer():
            header = b""
            while len(header) < 8:
                header += large_frame_peer.recv(8 - len(header))
            request_size = struct.unpack("!Q", header)[0]
            remaining = request_size
            while remaining:
                part = large_frame_peer.recv(remaining)
                remaining -= len(part)
            large_frame_peer.sendall(struct.pack("!Q", 100_000_000))
            large_frame_peer.sendall(b"{}")
            large_frame_peer.close()
        formerly_oversized = threading.Thread(
            target=formerly_oversized_peer, daemon=True)
        formerly_oversized.start()
        assert struct.unpack("!Q", struct.pack("!Q", 100_000_000))[0] == \
            100_000_000
        try:
            try:
                client._send_request({"cmd": "safety_hello_v7"})
                raise AssertionError("incomplete large frame was accepted")
            except ConnectionError as exc:
                assert "incomplete WRDS response frame" in str(exc)
        finally:
            client._connect = original_connect
        formerly_oversized.join(timeout=2)
        assert not formerly_oversized.is_alive()

        bounded_client, bounded_peer = socket.socketpair()
        client._connect = lambda timeout, force_bridge=False, bridge_timeout=None: (
            bounded_client, None)
        def over_bound_peer():
            request_size = struct.unpack(
                "!Q", client._recv_exact(bounded_peer, 8))[0]
            client._recv_exact(bounded_peer, request_size)
            bounded_peer.sendall(struct.pack("!Q", client.MAX_RESPONSE + 1))
            bounded_peer.close()
        over_bound = threading.Thread(target=over_bound_peer, daemon=True)
        over_bound.start()
        try:
            try:
                client._send_request({"cmd": "safety_hello_v7"})
                raise AssertionError("response above wire-safety bound was accepted")
            except ConnectionError as exc:
                assert "frame must be" in str(exc)
        finally:
            client._connect = original_connect
        over_bound.join(timeout=2)
        assert not over_bound.is_alive()
        assert client.MAX_RESPONSE == bridge.MAX_RESPONSE == server.MAX_RESPONSE

        old_memory_cap = server.MAX_RESULT_MEMORY
        server.MAX_RESULT_MEMORY = 1
        try:
            try:
                server._bounded_chunks(iter([client.pd.DataFrame({"x": [1]})]))
                raise AssertionError("oversized query result was materialized")
            except ValueError:
                pass
        finally:
            server.MAX_RESULT_MEMORY = old_memory_cap

        class DeadlineConnection:
            def __init__(self):
                self.statements = []
            def execute(self, statement):
                self.statements.append(str(statement))
        class BoundedQueryDB:
            def __init__(self):
                self.connection = DeadlineConnection()
            def raw_sql(self, sql, chunksize=None, return_iter=False):
                assert chunksize == 50_000 and return_iter is True
                return iter([client.pd.DataFrame({"x": [1, 2]})])
        bounded_db = BoundedQueryDB()
        bounded_df = server._bounded_query(bounded_db, "SELECT 1", 999999)
        assert len(bounded_df) == 2
        assert str(server.QUERY_TIMEOUT_SECONDS * 1000) in \
            bounded_db.connection.statements[0]

        # Readiness is nonblocking while the serialized database owner is
        # busy, and queued commands honor their own total operation deadline.
        busy_state = server.WrdsState(None)
        busy_entered = threading.Event()
        busy_release = threading.Event()

        def bounded_busy_command(db):
            busy_entered.set()
            busy_release.wait(timeout=1)
            return "done"

        busy_worker = threading.Thread(
            target=lambda: busy_state.run(
                bounded_busy_command, deadline=time.monotonic() + 1),
            daemon=True,
        )
        busy_worker.start()
        assert busy_entered.wait(timeout=1)
        started = time.monotonic()
        busy_ok, busy_detail = busy_state.healthcheck()
        assert time.monotonic() - started < 0.05
        assert busy_ok and "bounded query" in busy_detail
        busy_release.set()
        busy_worker.join(timeout=1)
        assert not busy_worker.is_alive()

        queued_state = server.WrdsState(None)
        queued_state.lock.acquire()
        try:
            try:
                queued_state.run(
                    lambda db: "unreachable",
                    deadline=time.monotonic() + 0.05,
                )
                raise AssertionError("queued command exceeded its deadline")
            except server.WrdsOperationTimeout:
                pass
        finally:
            queued_state.lock.release()

        # Contention from a healthcheck/recovery owner is never called live.
        wedged_state = server.WrdsState(object())
        health_entered = threading.Event()
        health_release = threading.Event()
        first_health = []

        def wedged_healthy(db, deadline=None):
            health_entered.set()
            health_release.wait(timeout=1)
            return True

        with mock.patch.object(
                wedged_state, "_healthy", side_effect=wedged_healthy):
            wedged_worker = threading.Thread(
                target=lambda: first_health.append(wedged_state.healthcheck()),
                daemon=True,
            )
            wedged_worker.start()
            assert health_entered.wait(timeout=1)
            wedged_ok, wedged_detail = wedged_state.healthcheck()
            assert not wedged_ok
            assert "healthcheck" in wedged_detail
            health_release.set()
            wedged_worker.join(timeout=1)
        assert not wedged_worker.is_alive()
        assert first_health == [(True, "ok")]

        # Recovery and retry share the original operation clock. A slow
        # recovery after a first connection failure cannot start a fresh full
        # query allowance or leave the client waiting for a second deadline.
        retry_state = server.WrdsState(object())
        retry_calls = []

        def fail_then_retry(db):
            retry_calls.append(time.monotonic())
            raise ConnectionResetError(
                errno.ECONNRESET, "connection reset by peer")

        def slow_recovery(deadline=None):
            time.sleep(0.08)
            return "test_recovery"

        with mock.patch.object(
                retry_state, "_recover", side_effect=slow_recovery):
            try:
                retry_state.run(
                    fail_then_retry,
                    deadline=time.monotonic() + 0.05,
                )
                raise AssertionError("recovery restarted the command deadline")
            except server.WrdsOperationTimeout:
                pass
        assert len(retry_calls) == 1

        late_success_state = server.WrdsState(object())
        late_entered = threading.Event()
        late_errors = []

        def late_success(db):
            late_entered.set()
            time.sleep(0.1)
            return "late success"

        late_worker = threading.Thread(
            target=lambda: _capture_error(
                late_errors,
                lambda: late_success_state.run(
                    late_success, deadline=time.monotonic() + 0.05)),
            daemon=True,
        )
        late_worker.start()
        assert late_entered.wait(timeout=1)
        time.sleep(0.06)
        late_ok, late_detail = late_success_state.healthcheck()
        assert not late_ok and "exceeded" in late_detail
        late_worker.join(timeout=1)
        assert not late_worker.is_alive()
        assert len(late_errors) == 1
        assert isinstance(late_errors[0], server.WrdsOperationTimeout)

        # High-level requests need only the DB-free version handshake before
        # sending their real command; they never issue a lock-taking ping.
        checked_commands = []

        def checked_response(request, **kwargs):
            checked_commands.append(request["cmd"])
            if request["cmd"] == "safety_hello_v7":
                return {
                    "status": "ok",
                    "safety_protocol": client.SAFETY_PROTOCOL,
                }
            return {
                "status": "ok",
                "tables": [],
                "safety_protocol": client.SAFETY_PROTOCOL,
            }

        with mock.patch.object(client, "_send_request", checked_response):
            assert client.wrds_list_tables("crsp") == []
        assert checked_commands == ["safety_hello_v7", "safe_list_tables_v7"]
        try:
            client.wrds_get_table("crsp", "msf")
            raise AssertionError("unbounded get_table call was accepted")
        except ValueError:
            pass

        response_client, response_server = socket.socketpair()
        try:
            server.send_response(response_server, {
                "status": "ok", "data": "x" * 1000,
            })
            response_size = struct.unpack(
                "!Q", client._recv_exact(response_client, 8))[0]
            response = json.loads(client._recv_exact(
                response_client, response_size))
            assert response["status"] == "ok"
            assert len(response["data"]) == 1000
        finally:
            response_client.close()
            response_server.close()

        # A direct client's SQL budget ends before response transfer begins.
        # Delay the query beyond the caller's tiny test timeout; the server's
        # response must still arrive under the separate preparation/transport
        # budgets instead of inheriting an already-expired query clock.
        class DelayedQueryState(HealthyState):
            def run(self, operation, deadline=None):
                time.sleep(0.08)
                return client.pd.DataFrame({"x": [1]}), False

        delayed_query_client, delayed_query_server = socket.socketpair()
        delayed_query_worker = threading.Thread(
            target=server.handle_client,
            args=(delayed_query_server, DelayedQueryState()),
            daemon=True,
        )
        delayed_query_worker.start()
        with mock.patch.object(
                client, "_connect",
                return_value=(delayed_query_client, None)), \
                mock.patch.object(client, "QUERY_TIMEOUT_FLOOR_SECONDS", 0.01), \
                mock.patch.object(
                    client, "RESPONSE_PREPARATION_GRACE_SECONDS", 0.2), \
                mock.patch.object(
                    client, "RESPONSE_TRANSFER_BASE_SECONDS", 0.2):
            delayed_query_response = client._send_request({
                "cmd": "safe_query_v7",
                "sql": "SELECT 1 AS x",
                "timeout": 0.01,
            }, timeout=0.01)
        assert delayed_query_response["status"] == "ok"
        delayed_query_worker.join(timeout=2)
        assert not delayed_query_worker.is_alive()

        # DataFrame conversion and final JSON encoding run in a bounded
        # producer stage. If preparation overruns, the worker never owns the
        # socket and the handler can still send one clean timeout frame.
        class SlowFrame:
            columns = ["x"]
            shape = (1, 1)

            def to_json(self, orient=None, date_format=None):
                time.sleep(0.08)
                return '{"columns":["x"],"index":[0],"data":[[1]]}'

        class SlowPreparationState(HealthyState):
            def run(self, operation, deadline=None):
                return SlowFrame(), False

        prep_client, prep_server = socket.socketpair()
        prep_worker = threading.Thread(
            target=server.handle_client,
            args=(prep_server, SlowPreparationState()), daemon=True)
        prep_worker.start()
        with mock.patch.object(
                client, "_connect", return_value=(prep_client, None)), \
                mock.patch.object(
                    server, "RESPONSE_PREPARATION_TIMEOUT_SECONDS", 0.05), \
                mock.patch.object(
                    client, "RESPONSE_PREPARATION_GRACE_SECONDS", 0.2):
            prep_response = client._send_request({
                "cmd": "safe_query_v7",
                "sql": "SELECT 1 AS x",
                "timeout": 1,
            }, timeout=1)
        assert prep_response["status"] == "error"
        assert "preparation deadline exceeded" in prep_response["msg"]
        prep_worker.join(timeout=2)
        assert not prep_worker.is_alive()

        # Even control responses renew the body deadline after their header.
        # This isolates the client-side half of #263 from daemon behavior.
        renewed_client, renewed_peer = socket.socketpair()
        renewed_payload = json.dumps({
            "status": "ok", "safety_protocol": server.SAFETY_PROTOCOL,
        }).encode()

        def serve_renewed_body():
            request_size = struct.unpack(
                "!Q", client._recv_exact(renewed_peer, 8))[0]
            client._recv_exact(renewed_peer, request_size)
            renewed_peer.sendall(struct.pack("!Q", len(renewed_payload)))
            renewed_peer.sendall(renewed_payload[:4])
            time.sleep(0.08)
            renewed_peer.sendall(renewed_payload[4:])
            renewed_peer.close()

        renewed_worker = threading.Thread(
            target=serve_renewed_body, daemon=True)
        renewed_worker.start()
        with mock.patch.object(
                client, "_connect", return_value=(renewed_client, None)), \
                mock.patch.object(
                    client, "RESPONSE_TRANSFER_BASE_SECONDS", 0.2):
            renewed_response = client._send_request(
                {"cmd": "safety_hello_v7"}, timeout=0.05)
        assert renewed_response["status"] == "ok"
        renewed_worker.join(timeout=2)
        assert not renewed_worker.is_alive()

        # A multi-megabyte response must replace the stale 15-second request
        # timeout before writing. Use tiny test deadlines and delay the reader
        # past the stale timeout: old behavior truncates; the scaled response
        # deadline completes on both the direct daemon and relay paths.
        large_text = "x" * 2_000_000
        slow_client, slow_server = socket.socketpair()
        slow_server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        slow_server.settimeout(0.05)
        slow_client.settimeout(3)
        slow_errors = []
        with mock.patch.object(server, "RESPONSE_WRITE_BASE_SECONDS", 1), \
                mock.patch.object(
                    server, "RESPONSE_WRITE_MIN_BYTES_PER_SECOND", 100_000_000), \
                mock.patch.object(server, "RESPONSE_WRITE_MAX_SECONDS", 2):
            slow_writer = threading.Thread(
                target=lambda: _capture_error(
                    slow_errors,
                    lambda: server.send_response(
                        slow_server, {"status": "ok", "data": large_text})),
                daemon=True,
            )
            slow_writer.start()
            time.sleep(0.1)
            slow_size = struct.unpack(
                "!Q", client._recv_exact(slow_client, 8))[0]
            slow_response = json.loads(
                client._recv_exact(slow_client, slow_size))
            slow_writer.join(timeout=3)
        assert not slow_writer.is_alive()
        assert slow_errors == []
        assert slow_response["data"] == large_text
        slow_client.close()
        slow_server.close()

        bridge_payload = b"y" * 2_000_000
        bridge_slow_client, bridge_slow_server = socket.socketpair()
        bridge_slow_server.setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, 4096)
        bridge_slow_server.settimeout(0.05)
        bridge_slow_client.settimeout(3)
        bridge_slow_errors = []
        with mock.patch.object(bridge, "RESPONSE_WRITE_BASE_SECONDS", 1), \
                mock.patch.object(
                    bridge, "RESPONSE_WRITE_MIN_BYTES_PER_SECOND", 100_000_000), \
                mock.patch.object(bridge, "RESPONSE_WRITE_MAX_SECONDS", 2):
            bridge_slow_writer = threading.Thread(
                target=lambda: _capture_error(
                    bridge_slow_errors,
                    lambda: bridge._send_response_frame(
                        bridge_slow_server, bridge_payload)),
                daemon=True,
            )
            bridge_slow_writer.start()
            time.sleep(0.1)
            bridge_slow_size = struct.unpack(
                "!Q", client._recv_exact(bridge_slow_client, 8))[0]
            bridge_slow_response = client._recv_exact(
                bridge_slow_client, bridge_slow_size)
            bridge_slow_writer.join(timeout=3)
        assert not bridge_slow_writer.is_alive()
        assert bridge_slow_errors == []
        assert bridge_slow_response == bridge_payload
        bridge_slow_client.close()
        bridge_slow_server.close()

        # Once a partial frame has escaped, neither component may append a
        # second error frame. It must log exact progress and close instead.
        hello = json.dumps({
            "cmd": "safety_hello_v7",
            "safety_protocol": server.SAFETY_PROTOCOL,
        }).encode()
        failing_server = FailingResponseSocket(
            struct.pack("!Q", len(hello)) + hello)
        server_stderr = io.StringIO()
        with redirect_stderr(server_stderr):
            server.handle_client(failing_server, state)
        assert failing_server.closed
        assert failing_server.send_calls == 3
        assert "[wrds_server] response write failed" in server_stderr.getvalue()
        assert "frame stopped at 13/" in server_stderr.getvalue()

        bridge_token_for_failure = "c" * 64
        rejected_request = json.dumps({
            "cmd": "safe_unblock_v7",
            "safety_protocol": bridge.SAFETY_PROTOCOL,
            "bridge_protocol": bridge.BRIDGE_PROTOCOL,
            "bridge_token": bridge_token_for_failure,
        }).encode()
        bridge_incoming = (
            bridge.BRIDGE_PREFACE_MAGIC +
            bridge_token_for_failure.encode("ascii") + b"\n" +
            struct.pack("!Q", len(rejected_request)) + rejected_request
        )
        failing_bridge = FailingResponseSocket(bridge_incoming)
        bridge_stderr = io.StringIO()
        with redirect_stderr(bridge_stderr):
            bridge._relay_client(
                failing_bridge, bridge_token_for_failure,
                threading.BoundedSemaphore(1),
                None,
            )
        assert failing_bridge.closed
        assert failing_bridge.send_calls == 3
        assert "[wrds_bridge] response write failed" in bridge_stderr.getvalue()
        assert "frame stopped at 13/" in bridge_stderr.getvalue()

        old_wire_cap = server.MAX_RESPONSE
        server.MAX_RESPONSE = 512
        capped_client, capped_server = socket.socketpair()
        try:
            server.send_response(capped_server, {
                "status": "ok", "data": "x" * 1000,
            })
            capped_size = struct.unpack(
                "!Q", client._recv_exact(capped_client, 8))[0]
            capped = json.loads(client._recv_exact(capped_client, capped_size))
            assert capped["status"] == "error"
            assert "wire-safety bound" in capped["msg"]
        finally:
            server.MAX_RESPONSE = old_wire_cap
            capped_client.close()
            capped_server.close()

        # Cleanup must not unlink a successor inode.
        os.unlink(server.SOCKET_FILE)
        successor = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        successor.bind(server.SOCKET_FILE)
        try:
            assert not server._unlink_socket_if_identity(replacement_identity)
            assert Path(server.SOCKET_FILE).exists()
        finally:
            successor.close()
            os.unlink(server.SOCKET_FILE)

        # Atomic PID publication replaces a planted symlink itself rather than
        # truncating its target.
        victim = state_dir / "victim"
        victim.write_text("do not overwrite", encoding="utf-8")
        os.symlink(victim, server.PID_FILE)
        server._write_pid_file()
        assert victim.read_text(encoding="utf-8") == "do not overwrite"
        assert not os.path.islink(server.PID_FILE)
        assert Path(server.PID_FILE).read_text(encoding="ascii") == str(os.getpid())

    print("PASS: WRDS Unix/bridge transport, singleton, lifecycle isolation, and PID safety")


if __name__ == "__main__":
    main()
