"""Regression test for WRDS connection recovery (GitHub issue #28).

Induces a real connection drop by terminating our own Postgres backend
(`pg_terminate_backend(pg_backend_pid())`) — the same failure mode as a
transient `SSL SYSCALL error: EOF detected`, which leaves the pooled
connection poisoned so that every later query (even `SELECT 1`) fails
with "Can't reconnect until invalid transaction is rolled back".

Asserts:
  1. A healthy server pings True.
  2. After the induced drop, the next query transparently recovers and
     succeeds — server reports resp['recovered'] == True on that call.
  3. wrds_ping() is True again afterwards.

Note on the issue's "wrds_ping() returns False when wedged": ping
auto-recovers, so it returns False only when the connection cannot be
recovered at all (host unreachable / auth failed). That is the intended
behavior for the autonomous pipeline (ping is a liveness gate; a False
that flips True on the next call would cause spurious aborts) and is
not exercised here — it would require taking WRDS itself offline.

Integration test: requires the WRDS server running (live network + the
one-time Duo already completed). Run from a deployed empirical project:

    PYTHONPATH=code python3 test_scripts/test_wrds_reconnect.py
"""
from utils.wrds_client import wrds_query, wrds_ping, wrds_start, _send_request

wrds_start()
assert wrds_ping(), "WRDS server not running / not healthy on start"
print("[1] healthy server pings True ............ OK")

# Sanity query before poisoning.
df = wrds_query("SELECT 1 AS ok")
assert int(df.iloc[0, 0]) == 1
print("[2] baseline SELECT 1 .................... OK")

# --- poison the connection ------------------------------------------------
# Killing our own backend either errors immediately or succeeds and leaves
# the socket dead; either way the *next* query hits the poisoned pool.
print("[3] terminating backend (inducing drop) ...")
try:
    wrds_query("SELECT pg_terminate_backend(pg_backend_pid())")
    print("    terminate returned (connection now dead)")
except RuntimeError as e:
    print(f"    terminate raised (expected): {e}")

# --- the recovery assertion ----------------------------------------------
# Go through the raw protocol so we can inspect resp['recovered']: the
# server must report that the _recover() path actually fired, AND return
# correct data. (wrds_query() discards the 'recovered' field.)
resp = _send_request({'cmd': 'query', 'sql': 'SELECT 42 AS answer'})
assert resp['status'] == 'ok', f"recovering query failed: {resp}"
assert resp['recovered'] is True, (
    "server did not report recovery after an induced connection drop "
    f"(resp['recovered']={resp.get('recovered')})")
import pandas as pd
from io import StringIO
df = pd.read_json(StringIO(resp['data']), orient='split')
assert int(df.iloc[0, 0]) == 42
print("[4] post-drop query recovered & correct .. OK")

assert wrds_ping(), "ping still False after recovery"
print("[5] server pings True after recovery ..... OK")

# A second drop, then confirm list-style commands recover too.
try:
    wrds_query("SELECT pg_terminate_backend(pg_backend_pid())")
except RuntimeError:
    pass
df = wrds_query("SELECT 7 AS n")
assert int(df.iloc[0, 0]) == 7
print("[6] second drop also recovered ........... OK")

print("\nPASS: WRDS connection recovery works (issue #28).")
