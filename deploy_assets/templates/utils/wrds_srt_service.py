#!/usr/bin/env python3
"""Gate project WRDS startup inside one durable, privileged SRT boundary.

This stdlib-only module is deployed under the model-immutable ``.opencode``
runtime and executed with the launcher's trusted system Python.  No project
interpreter, import, or executable runs until the host validates the published
PID identity and opens the one-shot approval gate.
"""

import os
import re
import signal
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path


SERVICE_MARKER = "zeropaper-wrds-srt-service-v6"
POLL_SECONDS = 15


def _credentials_configured():
    """Mirror start_services.sh's non-placeholder credential predicate."""
    values = dict(os.environ)
    try:
        with open(".env", encoding="utf-8") as handle:
            for raw_line in handle:
                key, separator, value = raw_line.partition("=")
                if not separator or not key or re.match(r"^[ \t]*#", key):
                    continue
                values[key] = value.rstrip("\n").rstrip("\r")
    except FileNotFoundError:
        pass
    user = values.get("WRDS_USER", "")
    password = values.get("WRDS_PASS", "")
    return bool(user and user != "your-username" and
                password and password != "your-password")


def main():
    if len(sys.argv) != 3 or sys.argv[1] != SERVICE_MARKER:
        raise SystemExit("WRDS SRT service requires its launcher marker")
    if os.environ.get("SANDBOX_RUNTIME") != "1":
        raise SystemExit("WRDS SRT service refuses to run outside Sandbox Runtime")

    # Credential-free empirical deployments are supported. Decide this using
    # trusted code inside SRT, before opening a gate or executing project code.
    if not _credentials_configured():
        print("WRDS_SRT_SERVICE_SKIPPED credentials-not-configured", flush=True)
        return 0

    approval_path = sys.argv[2]
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    approval_fd = os.open(approval_path, flags)
    approval_info = os.fstat(approval_fd)
    if (not stat.S_ISREG(approval_info.st_mode) or
            approval_info.st_nlink != 1 or
            (hasattr(os, "getuid") and approval_info.st_uid != os.getuid()) or
            approval_info.st_mode & 0o077):
        os.close(approval_fd)
        raise SystemExit("unsafe WRDS SRT approval gate")

    # The daemon's write-ahead latch names its PID. Prove before any login that
    # SRT did not put this service in a private PID namespace whose numbers are
    # meaningless to host-side peers. The trusted launcher verifies this exact
    # PID/start tuple and opens the one-shot approval gate.
    started = subprocess.run(
        ["/bin/ps", "-o", "lstart=", "-p", str(os.getpid())],
        capture_output=True, text=True, timeout=5, check=False,
    ).stdout.strip()
    if not started:
        os.close(approval_fd)
        raise SystemExit("cannot obtain WRDS SRT service birth token")
    print(f"WRDS_SRT_IDENTITY {os.getpid()} {started}", flush=True)
    deadline = time.monotonic() + 15
    approved = False
    while time.monotonic() < deadline:
        os.lseek(approval_fd, 0, os.SEEK_SET)
        if os.read(approval_fd, 64) == b"approved\n":
            approved = True
            break
        time.sleep(0.05)
    os.close(approval_fd)
    if not approved:
        raise SystemExit("WRDS SRT service was not approved by its launcher")

    completed = subprocess.run(
        ["/bin/bash", "code/utils/start_services.sh"],
        check=False,
    )
    if completed.returncode != 0:
        return completed.returncode

    # Imports from project code happen only after the trusted approval above.
    sys.path.insert(0, str(Path.cwd() / "code"))
    from utils.wrds_client import wrds_bridge_ping, wrds_ping

    needs_bridge = sys.platform.startswith("linux")
    if not wrds_ping() or (needs_bridge and not wrds_bridge_ping()):
        print("WRDS SRT service startup returned without healthy endpoints",
              file=sys.stderr, flush=True)
        return 1

    stopping = threading.Event()

    def stop(_signum, _frame):
        stopping.set()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    print("WRDS_SRT_SERVICE_READY", flush=True)

    while not stopping.wait(POLL_SECONDS):
        if not wrds_ping() or (needs_bridge and not wrds_bridge_ping()):
            print("WRDS SRT service lost a required endpoint; refusing restart",
                  file=sys.stderr, flush=True)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
