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
    # Check if ANY wrds server is already responding on the port (could be from another project)
    if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
        echo "WRDS server already running (reusing existing connection)"
    else
        echo "Starting WRDS server (approve Duo when prompted)..."
        # wrds.Connection silently ignores the wrds_password kwarg — feed libpq via PGPASSWORD instead.
        # Redirect the daemon's stdout/stderr to a log file (not the inherited fds) and disown it.
        # Otherwise the backgrounded server holds this script's stdout open; when start_services.sh is
        # invoked through a pipe (e.g. `... | tail`), the reader never sees EOF and the caller hangs
        # indefinitely even though the script itself has finished.
        mkdir -p process_log
        # nohup/& here is deliberate: this is fixed infrastructure starting a persistent,
        # host-shared daemon meant to outlive the calling session — not an agent-improvised
        # job the harness should track (cf. templates/shared/bash_background.md).
        PGPASSWORD="$WRDS_PASS" PYTHONPATH=code nohup "$WRDS_PY" code/utils/wrds_server.py \
            >> process_log/wrds_server.log 2>&1 &
        # || true: if the daemon crashes before disown runs, no-job is not fatal under set -e;
        # the readiness loop below reports the real failure.
        disown 2>/dev/null || true
        # Wait for server to be ready
        ready=0
        for i in $(seq 1 120); do
            sleep 1
            if PYTHONPATH=code "$WRDS_PY" -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
                echo "WRDS server ready"
                ready=1
                break
            fi
        done
        # Fail loudly on timeout instead of falling through to "Services ready." with exit 0 —
        # a silent false-success would let the pipeline start Stage 0 against a dead server.
        if [ "$ready" -ne 1 ]; then
            echo "ERROR: WRDS server did not become ready within 120s." >&2
            echo "       Check process_log/wrds_server.log (Duo not approved? bad credentials? network?)." >&2
            exit 1
        fi
    fi
else
    echo "WRDS: credentials not configured (set WRDS_USER and WRDS_PASS in .env), skipping"
fi

echo "Services ready."
