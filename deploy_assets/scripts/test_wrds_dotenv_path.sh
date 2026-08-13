#!/usr/bin/env bash
# Regression test for project-relative WRDS credential loading (#229).
# Uses dummy credentials and imports only; it never starts the server or opens
# a WRDS connection.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-wrds-dotenv.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

PY="${PYTHON:-python3}"
if ! "$PY" -c 'import dotenv, pandas' 2>/dev/null; then
    echo "ERROR: pandas/python-dotenv unavailable — run inside a project venv" >&2
    exit 1
fi

DOTENV_PROJECT="$TEST_ROOT/project"
DOTENV_OUTSIDE="$TEST_ROOT/outside"
mkdir -p "$DOTENV_PROJECT/code/utils" "$DOTENV_OUTSIDE"
cp "$ROOT/extensions/empirical/utils/wrds_client.py" \
   "$ROOT/extensions/empirical/utils/wrds_server.py" \
   "$DOTENV_PROJECT/code/utils/"
printf 'WRDS_USER=dotenv-path-user\nWRDS_PASS=dotenv-path-pass\n' \
    > "$DOTENV_PROJECT/.env"

echo "[1] module-relative .env loading under python -c"
for module in wrds_client wrds_server; do
    (
        cd "$DOTENV_OUTSIDE"
        env -u WRDS_USER -u WRDS_PASS \
            PYTHONPATH="$DOTENV_PROJECT/code/utils" \
            "$PY" -c '
import importlib
import os
import sys

importlib.import_module(sys.argv[1])
assert os.environ.get("WRDS_USER") == "dotenv-path-user"
assert os.environ.get("WRDS_PASS") == "dotenv-path-pass"
' "$module"
    )
    echo "  PASS  $module loads the project .env outside the project cwd"
done

echo "All WRDS dotenv-path tests passed (no connection attempted)."
