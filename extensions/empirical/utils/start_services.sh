#!/bin/bash
# Start persistent data services for the pipeline.
# Run this once at the start of each Claude session:
#   bash code/utils/start_services.sh
#
# Starts the WRDS server if credentials are configured.
# Safe to run multiple times — checks for existing server.

set -e
cd "$(dirname "$0")/../.."

# Load .env (handles values with spaces)
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
        export "$key=$value"
    done < .env
fi

# Start WRDS server if credentials are configured
if [ -n "$WRDS_USER" ] && [ "$WRDS_USER" != "your-username" ]; then
    if [ -f code/utils/.wrds_server.pid ]; then
        PID=$(cat code/utils/.wrds_server.pid)
        if kill -0 "$PID" 2>/dev/null; then
            echo "WRDS server already running (PID $PID)"
        else
            echo "Starting WRDS server (approve Duo when prompted)..."
            PYTHONPATH=code python3 code/utils/wrds_server.py &
        fi
    else
        echo "Starting WRDS server (approve Duo when prompted)..."
        PYTHONPATH=code python3 code/utils/wrds_server.py &
    fi
else
    echo "WRDS: no credentials configured, skipping"
fi

echo "Services ready."
