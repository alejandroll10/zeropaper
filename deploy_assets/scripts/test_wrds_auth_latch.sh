#!/usr/bin/env bash
# Regression tests for the WRDS credential-rejection latch.
#
# Guards the lockout bug: a PAM rejection arrives as a psycopg2
# OperationalError, which _is_conn_error() classified as a recoverable dropped
# socket. Because healthcheck() calls _recover() on every unhealthy ping, and
# _recover()'s Tier 2 and Tier 3 each perform a fresh login, ONE ping cost two
# failed authentications — while start_services.sh pings up to 120 times and
# wrds_start() another 120. A stale password could therefore fire hundreds of
# logins and lock the shared WRDS account for every project on the host, which
# is exactly what happened on 2026-08-04.
#
# The contract these tests pin down:
#   * a rejected credential costs exactly ONE login, then latches
#   * a latched server spends ZERO further logins, however hard it is polled
#   * the latch persists to disk, so restarting the server is not a free way
#     around the operator gate (start_services.sh runs at every launch)
#   * an operator-approved unblock spends exactly ONE attempt; failure
#     re-latches, success clears the latch and resets the budget
#
# The real wrds_server module is imported and only its network edges are
# stubbed, so these fail if the shipped implementation drifts.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-wrds-latch.XXXXXX")"
trap 'rm -rf "$TEST_ROOT"' EXIT

# Latch and pid paths are keyed off XDG_RUNTIME_DIR, so pointing it at the
# scratch dir keeps the test from touching the host's real server state.
export XDG_RUNTIME_DIR="$TEST_ROOT"

PY="${PYTHON:-python3}"
if ! "$PY" -c 'import sqlalchemy, dotenv' 2>/dev/null; then
    echo "SKIP: sqlalchemy/python-dotenv unavailable — run inside a project venv" >&2
    echo "      e.g. PYTHON=<project>/.venv/bin/python bash scripts/test_wrds_auth_latch.sh" >&2
    exit 0
fi

PYTHONPATH="$ROOT/extensions/empirical/utils" "$PY" - <<'PY'
import os, sys
import sqlalchemy.exc as sa_exc
import wrds_server as S

FAILURES = []

def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)

PAM = sa_exc.OperationalError(
    "s", {}, Exception('FATAL:  PAM authentication failed for user "someuser"'))
DROP = sa_exc.OperationalError(
    "s", {}, Exception("server closed the connection unexpectedly"))

logins = {"n": 0}
fixed = {"ok": False}


class FakeDB:
    class connection:
        @staticmethod
        def rollback():
            raise Exception("server closed the connection")

        @staticmethod
        def close():
            pass

    engine = None

    def connect(self):          # recovery Tier 2 == one login
        logins["n"] += 1
        raise PAM

    def close(self):
        pass


def fake_connect():             # Tier 3 / startup / unblock == one login
    logins["n"] += 1
    if not fixed["ok"]:
        raise PAM
    return FakeDB()


def fake_raw(db, sql):
    if not fixed["ok"]:
        raise Exception("server closed the connection")
    return True


S.connect_wrds = fake_connect
S._safe_raw_sql = fake_raw

print("\n[1] classification — auth must not be mistaken for a recoverable drop")
check("_is_auth_error(PAM)", S._is_auth_error(PAM), True)
check("_is_conn_error(PAM)", S._is_conn_error(PAM), False)
check("_is_auth_error(EOFError)", S._is_auth_error(EOFError("EOF when reading a line")), True)
check("_is_conn_error(socket drop)", S._is_conn_error(DROP), True)
check("_is_auth_error(socket drop)", S._is_auth_error(DROP), False)

print("\n[2] a rejected credential costs one login, however hard it is polled")
st = S.WrdsState(FakeDB())
for _ in range(25):
    st.healthcheck()
check("logins after 25 pings", logins["n"], 1)
check("latched", st.auth_blocked(), True)
check("latch persisted to disk", os.path.exists(S.AUTH_BLOCK_FILE), True)

print("\n[3] polling a latched server spends nothing")
logins["n"] = 0
for _ in range(25):
    st.healthcheck()
check("logins while latched", logins["n"], 0)

print("\n[4] restart does not bypass the operator gate")
logins["n"] = 0
check("fresh process reads latch", bool(S._read_auth_block()), True)
check("logins spent by restart", logins["n"], 0)

print("\n[5] operator approves, credential still broken -> one attempt, re-latch")
logins["n"] = 0
st2 = S.WrdsState(FakeDB())
st2.auth_failed = S._read_auth_block()
ok, _ = st2.unblock()
check("unblock succeeded", ok, False)
check("logins spent", logins["n"], 1)
check("re-latched", st2.auth_blocked(), True)
check("latch still on disk", os.path.exists(S.AUTH_BLOCK_FILE), True)

print("\n[6] operator approves, credential fixed -> one attempt, budget resets")
fixed["ok"] = True
logins["n"] = 0
ok, detail = st2.unblock()
check("unblock succeeded", ok, True)
check("logins spent", logins["n"], 1)
check("latch cleared", st2.auth_blocked(), False)
check("latch removed from disk", os.path.exists(S.AUTH_BLOCK_FILE), False)
check("healthy afterwards", st2.healthcheck()[0], True)

print()
if FAILURES:
    print(f"FAILED ({len(FAILURES)}): " + ", ".join(FAILURES))
    sys.exit(1)
print("All WRDS auth-latch tests passed.")
PY
