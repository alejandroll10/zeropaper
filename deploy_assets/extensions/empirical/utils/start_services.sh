#!/bin/bash
# Start persistent data services for the pipeline.
# Run this once at the start of each Claude session:
#   bash code/utils/start_services.sh
#
# Starts the WRDS server if credentials are configured.
# Safe to run multiple times — checks for existing server.

set -e
cd "$(dirname "$0")/../.."

# Pin the project venv interpreter (same PATH-demotion hazard as
# launch_agent.sh — issue #191): a macOS login shell runs path_helper, which
# puts /usr/bin ahead of any inherited venv PATH entry, and the system python
# has no pandas/dotenv — so the ping probe below fails silently even when a
# healthy server is up, and the restart path dies on imports after a
# misleading 120s timeout. Bare python3 only as a last resort (no venv).
WRDS_PY="$(pwd)/.venv/bin/python3"
[ -x "$WRDS_PY" ] || WRDS_PY="python3"

# Load .env (handles values with spaces; strips trailing CR for CRLF-edited files)
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^[[:space:]]*# || -z "$key" ]] && continue
        value="${value%$'\r'}"
        export "$key=$value"
    done < .env
fi

# Start WRDS server if credentials are configured
if [ -n "$WRDS_USER" ] && [ "$WRDS_USER" != "your-username" ] && [ -n "$WRDS_PASS" ] && [ "$WRDS_PASS" != "your-password" ]; then
    # Check whether the host-wide query socket already responds (possibly from
    # another project).
    if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
        echo "WRDS server already running (reusing existing connection)"
    elif LATCHED="$(PYTHONPATH=code "$WRDS_PY" -c "
from utils.wrds_client import wrds_auth_error
print(wrds_auth_error() or '')" 2>/dev/null)" && [ -n "$LATCHED" ]; then
        # A server is up but has latched a credential rejection. Spawning another
        # would only lose the port race and rediscover this 120s later.
        echo "ERROR: WRDS login safety gate blocked startup — not retrying." >&2
        echo "       $LATCHED" >&2
        echo "       An operator must resolve the reported condition. For a credential" >&2
        echo "       latch, fix WRDS_PASS in .env, then approve one retry with:" >&2
        echo "       $WRDS_PY code/utils/wrds_client.py unblock" >&2
        exit 2
    elif IN_PROGRESS="$(PYTHONPATH=code "$WRDS_PY" -c "
from utils.wrds_client import wrds_login_in_progress
print('1' if wrds_login_in_progress() else '0')" 2>/dev/null)" && [ "$IN_PROGRESS" = "1" ]; then
        # Another project won the singleton race and is already waiting for
        # Duo. Join that readiness wait; spawning a losing child creates a
        # false startup failure that caller-level supervisors may retry.
        echo "WRDS login already in progress; waiting for the existing server..."
        if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_wait_for_existing; wrds_wait_for_existing()"; then
            echo "WRDS server ready (reusing existing connection)"
        else
            echo "ERROR: existing WRDS startup did not become ready; not spawning a replacement." >&2
            exit 1
        fi
    else
        echo "Starting WRDS server (approve Duo when prompted)..."
        # wrds.Connection silently ignores the wrds_password kwarg — feed libpq via PGPASSWORD instead.
        # Redirect the daemon's stdout/stderr to a log file (not the inherited fds) and disown it.
        # Otherwise the backgrounded server holds this script's stdout open; when start_services.sh is
        # invoked through a pipe (e.g. `... | tail`), the reader never sees EOF and the caller hangs
        # indefinitely even though the script itself has finished.
        WRDS_STATE_DIR="${HOME:?HOME must be set}/.local/state/zeropaper/wrds"
        mkdir -p -m 700 "$WRDS_STATE_DIR"
        chmod 700 "$WRDS_STATE_DIR"
        WRDS_LOG="$WRDS_STATE_DIR/wrds_server_23847.log"
        # nohup/& here is deliberate: this is fixed infrastructure starting a persistent,
        # host-shared daemon meant to outlive the calling session — not an agent-improvised
        # job the harness should track (cf. templates/shared/bash_background.md).
        # A separate session survives runtime and tmux teardown. The daemon is
        # host-wide and exposes a private Unix socket to network-isolated
        # sandboxes, so it must outlive the launcher that established it.
        WRDS_SETSID=""
        command -v setsid >/dev/null 2>&1 && WRDS_SETSID="setsid"
        PGPASSWORD="$WRDS_PASS" PYTHONPATH=code nohup $WRDS_SETSID "$WRDS_PY" -u code/utils/wrds_server.py \
            >> "$WRDS_LOG" 2>&1 &
        wrds_server_pid=$!
        # Wait for server to be ready.
        #
        # The loop must distinguish "not ready yet" from "credential rejected".
        # Polling a rejection is what locks the WRDS account: the server latches
        # after the first refusal, but a poll that only asks "ready?" would keep
        # asking for the full 120s while every earlier revision of this loop
        # drove a fresh login attempt per probe. Break out the moment the server
        # reports an auth latch.
        ready=0
        auth_blocked=""
        for i in $(seq 1 120); do
            sleep 1
            if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
                echo "WRDS server ready"
                ready=1
                break
            fi
            auth_blocked="$(PYTHONPATH=code "$WRDS_PY" -c "
from utils.wrds_client import wrds_auth_error
print(wrds_auth_error() or '')" 2>/dev/null)"
            if [ -n "$auth_blocked" ]; then
                break
            fi
            # Do not wait out the full readiness budget after an ordinary
            # startup crash.  Retaining the child PID also lets us distinguish
            # "still waiting for Duo" from "there is no process left that can
            # ever become ready" without launching a replacement.
            if [ -n "$wrds_server_pid" ] && ! kill -0 "$wrds_server_pid" 2>/dev/null; then
                if wait "$wrds_server_pid"; then
                    wrds_server_rc=0
                else
                    wrds_server_rc=$?
                fi
                # The winner may have armed its marker between this loop's
                # earlier status checks and the losing child exit.
                peer_in_progress="$(PYTHONPATH=code "$WRDS_PY" -c "
from utils.wrds_client import wrds_login_in_progress
print('1' if wrds_login_in_progress() else '0')" 2>/dev/null)"
                if [ "$peer_in_progress" = "1" ]; then
                    echo "WRDS peer login detected; joining its readiness wait..."
                    wrds_server_pid=""
                    continue
                fi
                if [ "$wrds_server_rc" -eq 4 ]; then
                    echo "ERROR: a pre-v5 WRDS daemon is still active; no replacement was started." >&2
                    echo "       Stop the legacy daemon from the host, then relaunch. See $WRDS_LOG." >&2
                    exit 1
                fi
                if [ "$wrds_server_rc" -eq 5 ]; then
                    echo "ERROR: WRDS released-client compatibility state is unavailable." >&2
                    echo "       Repair the cache-state path shown in $WRDS_LOG; no login was attempted." >&2
                    exit 1
                fi
                if [ "$wrds_server_rc" -eq 3 ]; then
                    # Allow a concurrently scheduled winner a short bounded
                    # window to publish its endpoint or write-ahead login
                    # marker. Duo itself may take minutes, but reaching one of
                    # these two states should not.
                    for _wrds_peer_probe in 1 2 3 4 5; do
                        if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
                            echo "WRDS server ready (concurrent starter won)"
                            ready=1
                            break
                        fi
                        peer_in_progress="$(PYTHONPATH=code "$WRDS_PY" -c "
from utils.wrds_client import wrds_login_in_progress
print('1' if wrds_login_in_progress() else '0')" 2>/dev/null)"
                        [ "$peer_in_progress" = "1" ] && break
                        sleep 1
                    done
                    [ "$ready" -eq 1 ] && break
                    if [ "$peer_in_progress" = "1" ]; then
                        echo "WRDS peer login detected; joining its readiness wait..."
                        wrds_server_pid=""
                        continue
                    fi
                    echo "ERROR: WRDS singleton is locked but has no query endpoint or live login attempt." >&2
                    echo "       The owning daemon may be wedged; inspect the PID in ~/.local/state/zeropaper/wrds/wrds_server_23847.lock." >&2
                    echo "       Not waiting 120s and not starting a replacement." >&2
                    exit 1
                fi
                echo "ERROR: WRDS server exited (code $wrds_server_rc) before becoming ready." >&2
                echo "       Check $WRDS_LOG; not starting another process." >&2
                exit 1
            fi
        done
        # Credential rejection is terminal and operator-actionable — report it as
        # its own failure (exit 2) rather than burying it in a generic timeout.
        if [ -n "$auth_blocked" ]; then
            echo "ERROR: WRDS login safety gate blocked startup — not retrying." >&2
            echo "       $auth_blocked" >&2
            echo "       An operator must resolve the reported condition. For a credential" >&2
            echo "       latch, fix WRDS_PASS in .env, then approve one retry with:" >&2
            echo "       $WRDS_PY code/utils/wrds_client.py unblock" >&2
            exit 2
        fi
        # Fail loudly on timeout instead of falling through to "Services ready." with exit 0 —
        # a silent false-success would let the pipeline start Stage 0 against a dead server.
        if [ "$ready" -ne 1 ]; then
            echo "ERROR: WRDS server did not become ready within 120s." >&2
            echo "       Check $WRDS_LOG (Duo not approved? bad credentials? network?)." >&2
            exit 1
        fi
    fi
else
    echo "WRDS: credentials not configured (set WRDS_USER and WRDS_PASS in .env), skipping"
fi

echo "Services ready."
