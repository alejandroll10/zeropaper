#!/usr/bin/env python3
"""Offline adversarial regression for the cross-sandbox WRDS transport."""

import json
import errno
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
                {"cmd": "safety_hello_v6"}, timeout=5, force_bridge=True)
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

        rejected = bridge_pair_request("b" * 64, "safety_hello_v6")
        assert rejected["status"] == "error"
        assert "authentication failed" in rejected["msg"]
        rejected = bridge_pair_request(bridge_token, "safe_unblock_v6")
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
                    bridge, "UPSTREAM_RESPONSE_TIMEOUT", 0.5):
            delayed = bridge_pair_request(
                bridge_token, "safety_hello_v6")
        assert delayed["status"] == "ok"
        delayed_worker.join(timeout=2)
        assert not delayed_worker.is_alive()

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
            assert client._connect(5) == (marker, bridge_token)
            fallback.assert_called_once_with(5)

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
        denied = request_over_socketpair(state, "safe_unblock_v6")
        assert denied["status"] == "error"
        assert "unknown command" in denied["msg"]
        denied = request_over_socketpair(state, "safe_shutdown_v6")
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
        client._connect = lambda timeout, force_bridge=False: (client_side, None)
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
            response = client._send_request({"cmd": "safety_hello_v6"})
            assert response["msg"] == "fragmented"
        finally:
            client._connect = original_connect
        fragmented.join(timeout=2)
        assert not fragmented.is_alive()

        large_frame_client, large_frame_peer = socket.socketpair()
        client._connect = lambda timeout, force_bridge=False: (large_frame_client, None)
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
                client._send_request({"cmd": "safety_hello_v6"})
                raise AssertionError("incomplete large frame was accepted")
            except ConnectionError as exc:
                assert "incomplete WRDS response frame" in str(exc)
        finally:
            client._connect = original_connect
        formerly_oversized.join(timeout=2)
        assert not formerly_oversized.is_alive()

        bounded_client, bounded_peer = socket.socketpair()
        client._connect = lambda timeout, force_bridge=False: (bounded_client, None)
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
                client._send_request({"cmd": "safety_hello_v6"})
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
