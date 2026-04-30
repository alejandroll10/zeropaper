#!/bin/bash
# Start persistent data services for the pipeline.
# Run this once at the start of each Claude session:
#   bash code/utils/start_services.sh
#
# Starts the WRDS server if credentials are configured.
# Safe to run multiple times — checks for existing server.

set -e
cd "$(dirname "$0")/../.."

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
    if PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
        echo "WRDS server already running (reusing existing connection)"
    else
        echo "Starting WRDS server (approve Duo when prompted)..."
        # wrds.Connection silently ignores the wrds_password kwarg — feed libpq via PGPASSWORD instead.
        PGPASSWORD="$WRDS_PASS" PYTHONPATH=code python3 code/utils/wrds_server.py &
        # Wait for server to be ready
        for i in $(seq 1 120); do
            sleep 1
            if PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)" 2>/dev/null; then
                echo "WRDS server ready"
                break
            fi
        done
    fi
else
    echo "WRDS: credentials not configured (set WRDS_USER and WRDS_PASS in .env), skipping"
fi

echo "Services ready."
