#!/usr/bin/env bash
# Regression tests for the WRDS credential-rejection latch.
#
# Guards the lockout bug: a PAM rejection arrives as a psycopg2
# OperationalError, which _is_conn_error() classified as a recoverable dropped
# socket. Because healthcheck() called _recover() on every unhealthy ping, and
# the old recovery tiers each performed a fresh login, ONE ping cost two
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
if ! "$PY" -c 'import sqlalchemy, dotenv, wrds' 2>/dev/null; then
    echo "ERROR: sqlalchemy/python-dotenv/wrds unavailable — run inside a project venv" >&2
    echo "      e.g. PYTHON=<project>/.venv/bin/python bash deploy_assets/scripts/test_wrds_auth_latch.sh" >&2
    exit 1
fi

PYTHON="$PY" bash "$ROOT/scripts/test_wrds_dotenv_path.sh"

PYTHONPATH="$ROOT/extensions/empirical/utils" "$PY" - <<'PY'
import importlib.metadata
import inspect
import os, sys
import types
import sqlalchemy.exc as sa_exc
import wrds
import wrds_server as S
import wrds_client as C
import wrds_utils as U
from unittest import mock

# Production latch state is durable under host-owned ~/.local/state so it
# survives logout/reboot without becoming sandbox-writable. Point this process
# at scratch storage without a deploy-time bypass.
S.AUTH_BLOCK_FILE = os.path.join(os.environ['XDG_RUNTIME_DIR'],
                                 'wrds-auth-latch-test', 'authblock')
S.CACHE_AUTH_BLOCK_FILE = os.path.join(os.environ['XDG_RUNTIME_DIR'],
                                       'wrds-auth-latch-test', 'cache-authblock')
S.LEGACY_AUTH_BLOCK_FILE = os.path.join(os.environ['XDG_RUNTIME_DIR'],
                                        '.wrds_server_23847.authblock.test')
C.LOG_FILE = os.path.join(os.environ['XDG_RUNTIME_DIR'],
                          'wrds-auth-latch-test', 'server.log')

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
class QueryCanceled(Exception):
    pgcode = '57014'
TIMEOUT = sa_exc.OperationalError(
    "s", {}, QueryCanceled("canceling statement due to statement timeout"))

try:
    raise EOFError("EOF when reading a line")
except EOFError as cause:
    WRAPPED_EOF = S.WrdsAuthError("WRDS connection setup failed")
    WRAPPED_EOF.__cause__ = cause

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

    def _Connection__make_sa_engine_conn(self, raise_err=False):
        # recovery Tier 2 == exactly one login; public connect() is forbidden
        logins["n"] += 1
        raise PAM

    def close(self):
        pass


def fake_connect(attempt_prearmed=False):  # Tier 3 / startup / unblock == one login
    logins["n"] += 1
    if not fixed["ok"]:
        raise PAM
    S._clear_auth_block(preserve_compat=True)
    return FakeDB()


def fake_raw(db, sql):
    if not fixed["ok"]:
        raise Exception("server closed the connection")
    return True


real_connect_wrds = S.connect_wrds
S.connect_wrds = fake_connect
S._safe_raw_sql = fake_raw

print("\n[1] classification — auth must not be mistaken for a recoverable drop")
check("_is_auth_error(PAM)", S._is_auth_error(PAM), True)
check("_is_conn_error(PAM)", S._is_conn_error(PAM), False)
check("_is_query_cancel_error(TIMEOUT)", S._is_query_cancel_error(TIMEOUT), True)
check("_is_conn_error(TIMEOUT)", S._is_conn_error(TIMEOUT), False)
timeout_calls = {'n': 0}
def timeout_query(db):
    timeout_calls['n'] += 1
    raise TIMEOUT
timeout_state = S.WrdsState(FakeDB())
with mock.patch.object(timeout_state, '_recover') as timeout_recover, \
     mock.patch.object(S, '_write_auth_block') as timeout_latch:
    try:
        timeout_state.run(timeout_query)
    except sa_exc.OperationalError:
        pass
check("statement timeout query executes once", timeout_calls['n'], 1)
check("statement timeout never enters reconnect", timeout_recover.call_count, 0)
check("statement timeout never writes auth latch", timeout_latch.call_count, 0)
check("statement timeout leaves in-memory auth latch clear",
      timeout_state.auth_blocked(), False)
check("_is_auth_error(EOFError)", S._is_auth_error(EOFError("EOF when reading a line")), True)
check("_is_auth_error(wrapped EOF)", S._is_auth_error(WRAPPED_EOF), True)
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

print("\n[4a] a v2.22.1 runtime latch migrates without spending a login")
S._clear_auth_block()
with open(S.LEGACY_AUTH_BLOCK_FILE, 'w', encoding='utf-8') as f:
    f.write('legacy credential rejection')
os.chmod(S.LEGACY_AUTH_BLOCK_FILE, 0o600)
check("legacy-only latch is read", S._read_auth_block(),
      'legacy credential rejection')
check("legacy latch copied to durable storage",
      os.path.exists(S.AUTH_BLOCK_FILE), True)
check("legacy copy retained for old daemon",
      os.path.exists(S.LEGACY_AUTH_BLOCK_FILE), True)
check("migration spends no login", logins["n"], 0)

print("\n[4b] the released cache latch migrates without spending a login")
S._clear_auth_block()
os.makedirs(os.path.dirname(S.CACHE_AUTH_BLOCK_FILE), exist_ok=True)
with open(S.CACHE_AUTH_BLOCK_FILE, 'w', encoding='utf-8') as f:
    f.write('v2-v4 cache credential rejection')
os.chmod(S.CACHE_AUTH_BLOCK_FILE, 0o600)
check("cache-only latch is read", S._read_auth_block(),
      'v2-v4 cache credential rejection')
check("cache latch copied to protected state",
      os.path.exists(S.AUTH_BLOCK_FILE), True)
check("cache copy retained for old daemon",
      os.path.exists(S.CACHE_AUTH_BLOCK_FILE), True)
check("cache migration spends no login", logins["n"], 0)

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

print("\n[7] lazy auth failure in healthcheck latches before recovery")
fixed["ok"] = False
logins["n"] = 0
st3 = S.WrdsState(FakeDB())
S._safe_raw_sql = lambda db, sql: (_ for _ in ()).throw(WRAPPED_EOF)
ok, _ = st3.healthcheck()
check("healthcheck succeeded", ok, False)
check("lazy failure latched", st3.auth_blocked(), True)
check("recovery logins after lazy auth", logins["n"], 0)

print("\n[8] auth failure on the post-recovery retry latches")
S._clear_auth_block()
logins["n"] = 0
st4 = S.WrdsState(FakeDB())
calls = {"n": 0}
st4._recover = lambda: 'rolled_back'
def drop_then_auth(db):
    calls["n"] += 1
    if calls["n"] == 1:
        raise DROP
    raise WRAPPED_EOF
try:
    st4.run(drop_then_auth)
except S.WrdsAuthError:
    pass
check("operation calls", calls["n"], 2)
check("post-retry failure latched", st4.auth_blocked(), True)
check("extra logins after post-retry auth", logins["n"], 0)

print("\n[9] every client API preserves the terminal auth signal")
auth_response = {'status': 'error', 'msg': 'latched', 'error_kind': 'auth',
                 'safety_protocol': C.SAFETY_PROTOCOL}
hello_response = {'status': 'ok', 'msg': 'hello',
                  'safety_protocol': C.SAFETY_PROTOCOL}
C._send_request = lambda request, **kwargs: (
    hello_response if request.get('cmd') == 'safety_hello_v6' else auth_response)
for label, call in (
    ('query', lambda: C.wrds_query('SELECT 1')),
    ('list_tables', lambda: C.wrds_list_tables('crsp')),
    ('list_libraries', C.wrds_list_libraries),
    ('get_table', lambda: C.wrds_get_table('crsp', 'msf', rows=1)),
    ('describe', lambda: C.wrds_describe('crsp', 'msf')),
):
    try:
        call()
    except C.WrdsAuthBlocked:
        typed = True
    except Exception:
        typed = False
    else:
        typed = False
    check(f"{label} raises WrdsAuthBlocked", typed, True)

legacy_response = {'status': 'ok', 'msg': 'legacy server'}
legacy_commands = []
def legacy_server_response(request, **kwargs):
    legacy_commands.append(request.get('cmd'))
    return legacy_response
C._send_request = legacy_server_response
with mock.patch.object(C.subprocess, 'Popen') as legacy_spawn:
    try:
        C.wrds_start()
    except C.WrdsAuthBlocked:
        legacy_refused = True
    else:
        legacy_refused = False
check("updated client refuses legacy daemon", legacy_refused, True)
check("legacy daemon mismatch is never auto-restarted", legacy_spawn.call_count, 0)
try:
    C.wrds_query('SELECT 1')
except C.WrdsSafetyBlocked:
    legacy_query_refused = True
else:
    legacy_query_refused = False
check("legacy daemon cannot execute updated-client query", legacy_query_refused, True)
check("legacy daemon receives only DB-free hello",
      set(legacy_commands), {'safety_hello_v6'})

with mock.patch.object(C, 'wrds_ping', return_value=False), \
     mock.patch.object(C, 'wrds_auth_error', return_value=None), \
     mock.patch.object(C, 'wrds_login_in_progress', return_value=True), \
     mock.patch.object(C, '_wait_for_ready', return_value=True) as peer_wait, \
     mock.patch.object(C.subprocess, 'Popen') as peer_spawn:
    peer_result = C.wrds_start()
check("concurrent starter joins existing wait", peer_result, True)
check("concurrent starter waits once", peer_wait.call_count, 1)
check("concurrent starter spawns no losing child", peer_spawn.call_count, 0)

with mock.patch.object(C, 'wrds_ping', return_value=False), \
     mock.patch.object(C, 'wrds_auth_error', return_value=None), \
     mock.patch.object(C, 'wrds_login_in_progress', return_value=False), \
     mock.patch.object(C.subprocess, 'Popen') as absent_spawn:
    try:
        C.wrds_start()
    except RuntimeError as e:
        absent_detail = str(e)
    else:
        absent_detail = ''
check("sandbox-side absent daemon is host-repair error",
      'host daemon is down' in absent_detail, True)
check("sandbox-side absent daemon never spawns", absent_spawn.call_count, 0)

class LosingStarter:
    returncode = 0
    def poll(self):
        return 0
losing_starter = LosingStarter()
with mock.patch.object(C, 'wrds_ping', side_effect=[False, True]), \
     mock.patch.object(C, 'wrds_auth_error', return_value=None), \
     mock.patch.object(C, 'wrds_login_in_progress', return_value=False), \
     mock.patch.object(C.time, 'sleep'), \
     mock.patch.object(C.time, 'monotonic', side_effect=[0, 0, 1, 1]):
    loser_joined = C._wait_for_ready(losing_starter)
check("post-spawn singleton loser joins winner", loser_joined, True)

print("\n[10] recovery bypasses wrds.Connection.connect() hidden retry")
attempts = {"private": 0, "public": 0}
class HiddenRetryDB:
    def _Connection__make_sa_engine_conn(self, raise_err=False):
        attempts["private"] += 1
        raise PAM
    def connect(self):
        attempts["public"] += 2
        raise PAM
try:
    S._connect_once(HiddenRetryDB())
except Exception:
    pass
check("one-attempt engine calls", attempts["private"], 1)
check("public hidden-retry calls", attempts["public"], 0)

check("wrds dependency pinned version", importlib.metadata.version('wrds'), '3.5.0')
private_connect = wrds.Connection._Connection__make_sa_engine_conn
private_source = inspect.getsource(private_connect)
check("installed primitive accepts raise_err",
      'raise_err' in inspect.signature(private_connect).parameters, True)
check("installed primitive has one engine login",
      private_source.count('self.engine.connect()'), 1)
check("installed primitive does not call public connect",
      private_source.count('self.connect()'), 0)
with mock.patch.object(wrds.Connection, 'connect') as installed_public_connect:
    wrds.Connection(wrds_username='offline-test',
                    wrds_password='offline-test', autoconnect=False)
check("installed autoconnect=False performs no public connect",
      installed_public_connect.call_count, 0)
installed_distribution = importlib.metadata.distribution('wrds')
mismatched_distribution = types.SimpleNamespace(
    version='9.9.9', files=installed_distribution.files,
    locate_file=installed_distribution.locate_file)
with mock.patch.object(S.importlib.metadata, 'distribution',
                       return_value=mismatched_distribution), \
     mock.patch.object(S, '_begin_login_attempt') as mismatched_begin:
    try:
        real_connect_wrds()
    except S.WrdsAuthError:
        mismatch_refused = True
    else:
        mismatch_refused = False
check("mismatched ambient wrds runtime refused", mismatch_refused, True)
check("runtime contract fails before login marker",
      mismatched_begin.call_count, 0)

shadowed_wrds = types.SimpleNamespace(Connection=wrds.Connection,
                                      __file__='/tmp/shadowed-wrds.py')
try:
    S._verify_wrds_runtime_contract(shadowed_wrds)
except RuntimeError:
    shadow_refused = True
else:
    shadow_refused = False
check("shadowed wrds module refused", shadow_refused, True)

real_getsource = S.inspect.getsource
def looped_primitive_source(fn):
    if fn is wrds.Connection._Connection__make_sa_engine_conn:
        return ('def __make_sa_engine_conn(self, raise_err=False):\n'
                '    for address in self.addresses:\n'
                '        self.connection = self.engine.connect()\n')
    return real_getsource(fn)
with mock.patch.object(S.inspect, 'getsource', side_effect=looped_primitive_source):
    try:
        S._verify_wrds_runtime_contract(wrds)
    except RuntimeError:
        looped_refused = True
    else:
        looped_refused = False
check("loop-containing one-call source refused by hash", looped_refused, True)

print("\n[10.1] SQLAlchemy implicit reconnect is blocked before authentication")
S._clear_auth_block()
sqlite_engine = __import__('sqlalchemy').create_engine('sqlite://')
sqlite_connection = sqlite_engine.connect()
sqlite_db = types.SimpleNamespace(engine=sqlite_engine,
                                  connection=sqlite_connection)
S._install_reconnect_guard(sqlite_db)
sqlite_connection.invalidate()
try:
    sqlite_connection.execute(__import__('sqlalchemy').text('SELECT 1'))
except Exception as implicit_error:
    implicit_blocked = S._is_conn_error(implicit_error)
else:
    implicit_blocked = False
check("invalidated connection cannot reconnect implicitly", implicit_blocked, True)
check("implicit reconnect routes as connection failure",
      S._is_conn_error(S.WrdsImplicitReconnectError('blocked')), True)
check("implicit reconnect spent no WRDS latch/login",
      os.path.exists(S.AUTH_BLOCK_FILE), False)
sqlite_connection.close()
sqlite_engine.dispose()

print("\n[10a] every credentialed startup is guarded before its first login")
S._clear_auth_block()
guard_observations = []
class GuardedConnection:
    def __init__(self, **kwargs):
        guard_observations.append(('construct', S._read_auth_block()))
    def _Connection__make_sa_engine_conn(self, raise_err=False):
        guard_observations.append(('login', S._read_auth_block()))
    def load_library_list(self):
        guard_observations.append(('libraries', S._read_auth_block()))
guarded_module = types.SimpleNamespace(Connection=GuardedConnection)
with mock.patch.dict(sys.modules, {'wrds': guarded_module}), \
     mock.patch.object(S, '_verify_wrds_runtime_contract'), \
     mock.patch.object(S, '_install_reconnect_guard'), \
     mock.patch.object(S, '_safe_raw_sql', return_value=True):
    guarded_db = real_connect_wrds()
check("startup returned guarded connection", isinstance(guarded_db, GuardedConnection), True)
check("all startup edges saw write-ahead marker",
      all(S.LOGIN_ATTEMPT_PREFIX in msg for _, msg in guard_observations), True)
check("verified startup clears marker", os.path.exists(S.AUTH_BLOCK_FILE), False)

class FailedGuardedConnection(GuardedConnection):
    def _Connection__make_sa_engine_conn(self, raise_err=False):
        guard_observations.append(('failed-login', S._read_auth_block()))
        raise PAM
failed_module = types.SimpleNamespace(Connection=FailedGuardedConnection)
with mock.patch.dict(sys.modules, {'wrds': failed_module}), \
     mock.patch.object(S, '_verify_wrds_runtime_contract'), \
     mock.patch.object(S, '_install_reconnect_guard'), \
     mock.patch.object(S, '_safe_raw_sql', return_value=True):
    try:
        real_connect_wrds()
    except S.WrdsAuthError:
        pass
failed_marker = S._read_auth_block()
check("failed startup leaves write-ahead marker",
      failed_marker.startswith(S.LOGIN_ATTEMPT_PREFIX), True)
C._server_module = lambda: S
check("live startup marker lets readiness wait", C._persisted_auth_block(), None)
with mock.patch.object(S, '_process_start_token', return_value='different-birth'):
    dead_marker = C._persisted_auth_block()
check("dead startup marker blocks restart", dead_marker, failed_marker)
pid_only_marker = (
    f"{S.LOGIN_ATTEMPT_PREFIX}{os.getpid()}\n"
    "legacy marker without a process birth token"
)
S._write_auth_block(pid_only_marker)
check("legacy PID-only attempt is terminal, not live",
      C._persisted_auth_block(), pid_only_marker)
S._write_auth_block(failed_marker)

print("\n[10a.1] a live-server timeout can never clear the durable latch")
with mock.patch.object(C, '_send_request', side_effect=TimeoutError('live timeout')), \
     mock.patch.object(S, '_clear_auth_block') as timeout_clear:
    try:
        C.wrds_unblock()
    except TimeoutError:
        timeout_propagated = True
    else:
        timeout_propagated = False
check("live timeout propagates", timeout_propagated, True)
check("live timeout does not clear latch", timeout_clear.call_count, 0)
with mock.patch.object(C, '_safety_hello',
                       side_effect=C.WrdsSafetyBlocked('legacy daemon')), \
     mock.patch.object(C.subprocess, 'Popen') as mismatch_spawn, \
     mock.patch.object(S, '_clear_auth_block') as mismatch_clear:
    mismatch_ok, mismatch_detail = C.wrds_unblock()
check("live protocol mismatch refuses unblock", mismatch_ok, False)
check("live protocol mismatch requires host stop",
      'stop it from the host' in mismatch_detail, True)
check("live protocol mismatch spawns no replacement", mismatch_spawn.call_count, 0)
check("live protocol mismatch does not clear latch", mismatch_clear.call_count, 0)
operator_env = os.path.join(os.environ['XDG_RUNTIME_DIR'], 'operator.env')
with open(operator_env, 'w', encoding='utf-8') as env_handle:
    env_handle.write('WRDS_USER=fixed-file-user\nWRDS_PASS=fixed-file-secret\n')
with mock.patch.object(C, '_DOTENV_PATH', operator_env), \
     mock.patch.dict(os.environ, {'WRDS_USER': 'stale-shell-user',
                                  'WRDS_PASS': 'stale-shell-secret',
                                  'PGPASSWORD': 'stale-shell-secret'}), \
     mock.patch.object(C, '_safety_hello', side_effect=ConnectionRefusedError()), \
     mock.patch.object(S, '_read_auth_block', return_value='blocked'), \
     mock.patch.object(C, '_wait_for_ready', return_value=True), \
     mock.patch.object(C.subprocess, 'Popen') as logged_spawn:
    logged_spawn.return_value = object()
    logged_ok, _ = C.wrds_unblock()
logged_kwargs = logged_spawn.call_args.kwargs
check("operator-unblock starts successfully with durable logging", logged_ok, True)
check("operator-unblock does not use stdout PIPE",
      logged_kwargs['stdout'] != C.subprocess.PIPE, True)
check("operator-unblock merges stderr into durable log",
      logged_kwargs['stderr'], C.subprocess.STDOUT)
check("operator-unblock overrides stale exported WRDS_PASS",
      logged_kwargs['env']['WRDS_PASS'], 'fixed-file-secret')
check("operator-unblock overrides stale exported WRDS_USER",
      logged_kwargs['env']['WRDS_USER'], 'fixed-file-user')
check("operator-unblock derives PGPASSWORD from corrected .env",
      logged_kwargs['env']['PGPASSWORD'], 'fixed-file-secret')

print("\n[10a.2] operator approval is never cleared before fallible setup")
S._write_auth_block('terminal operator latch')
listener = mock.Mock()
common_main_patches = (
    mock.patch.object(S, '_acquire_instance_lock', return_value=('lock',)),
    mock.patch.object(S, '_refuse_live_legacy_processes'),
    mock.patch.object(S, '_bind_legacy_refusal_listener', return_value=listener),
    mock.patch.object(S.threading, 'Thread', return_value=mock.Mock()),
    mock.patch.object(S, '_read_auth_block', return_value='terminal operator latch'),
    mock.patch.object(S, '_write_compat_guard', return_value=('compat',)),
    mock.patch.object(S, '_remove_lock_if_identity'),
)
with common_main_patches[0], common_main_patches[1], common_main_patches[2], \
     common_main_patches[3], common_main_patches[4], common_main_patches[5], \
     common_main_patches[6], \
     mock.patch.object(S, '_verify_compat_guard'), \
     mock.patch.object(S, '_bind_unix_server', side_effect=OSError('bind failed')), \
     mock.patch.object(S, '_begin_login_attempt') as bind_begin, \
     mock.patch.object(S, '_clear_auth_block') as bind_clear:
    try:
        S.main(operator_unblock=True)
    except SystemExit:
        pass
check("UDS failure occurs before approved-attempt transition",
      bind_begin.call_count, 0)
check("UDS failure never clears terminal latch", bind_clear.call_count, 0)

unix_listener = mock.Mock()
with mock.patch.object(S, '_acquire_instance_lock', return_value=('lock',)), \
     mock.patch.object(S, '_refuse_live_legacy_processes'), \
     mock.patch.object(S, '_bind_legacy_refusal_listener', return_value=listener), \
     mock.patch.object(S.threading, 'Thread', return_value=mock.Mock()), \
     mock.patch.object(S, '_read_auth_block', return_value='terminal operator latch'), \
     mock.patch.object(S, '_write_compat_guard', return_value=('compat',)), \
     mock.patch.object(S, '_verify_compat_guard'), \
     mock.patch.object(S, '_remove_lock_if_identity'), \
     mock.patch.object(S, '_bind_unix_server',
                       return_value=(unix_listener, ('socket',))), \
     mock.patch.object(S, '_write_pid_file',
                       side_effect=S.WrdsLatchError('pid failed')), \
     mock.patch.object(S, '_begin_login_attempt') as pid_begin, \
     mock.patch.object(S, '_clear_auth_block') as pid_clear:
    try:
        S.main(operator_unblock=True)
    except SystemExit:
        pass
check("PID failure occurs before approved-attempt transition",
      pid_begin.call_count, 0)
check("PID failure never clears terminal latch", pid_clear.call_count, 0)

# Once setup is complete, approval replaces the terminal record atomically;
# there is no absent-latch intermediate state.
S._write_auth_block('terminal operator latch')
approved_marker = S._begin_login_attempt(replace_blocked=True)
check("operator approval atomically publishes live attempt",
      S._read_auth_block(), approved_marker)
check("approved attempt carries process birth identity",
      S._live_login_attempt(approved_marker), True)
S._clear_auth_block()

print("\n[10b] ambiguous reconnect failure also stops automatic polling")
S._clear_auth_block()
ambiguous_logins = {"n": 0}
class AmbiguousDB(FakeDB):
    def _Connection__make_sa_engine_conn(self, raise_err=False):
        ambiguous_logins["n"] += 1
        raise RuntimeError('TLS handshake ended without an auth marker')
S._safe_raw_sql = lambda db, sql: (_ for _ in ()).throw(DROP)
st_ambiguous = S.WrdsState(AmbiguousDB())
for _ in range(25):
    st_ambiguous.healthcheck()
check("ambiguous login attempts after 25 pings", ambiguous_logins["n"], 1)
check("ambiguous failure latched", st_ambiguous.auth_blocked(), True)

print("\n[11] latch persistence is atomic and fails closed")
S._clear_auth_block()
production_latch = S._auth_block_path()
check("production latch survives runtime-dir cleanup",
      production_latch.startswith(os.environ['XDG_RUNTIME_DIR']), False)
check("production latch uses host-owned durable per-user state",
      os.path.join('.local', 'state', 'zeropaper', 'wrds') in production_latch, True)
S._write_auth_block('blocked')
check("latch mode", oct(os.stat(S.AUTH_BLOCK_FILE).st_mode & 0o777), '0o600')
check("atomic latch readable", S._read_auth_block(), 'blocked')
with mock.patch.object(S.os, 'open', side_effect=PermissionError('denied')):
    C._server_module = lambda: S
    unreadable_kind, unreadable = C._persisted_auth_state()
check("unreadable latch remains fail-closed but distinct from auth",
      unreadable_kind, 'unavailable')
check("unreadable latch reports host repair", 'host repair' in unreadable, True)

S._clear_auth_block()
with open(S.AUTH_BLOCK_FILE, 'w', encoding='utf-8'):
    pass
os.chmod(S.AUTH_BLOCK_FILE, 0o600)
try:
    S._read_auth_block()
except S.WrdsLatchError:
    refused_empty = True
else:
    refused_empty = False
check("empty existing latch blocks startup", refused_empty, True)

S._clear_auth_block()
target = os.path.join(os.environ['XDG_RUNTIME_DIR'], 'latch-target')
with open(target, 'w', encoding='utf-8') as f:
    f.write('not a latch')
os.symlink(target, S.AUTH_BLOCK_FILE)
try:
    S._read_auth_block()
except S.WrdsLatchError:
    refused_symlink = True
else:
    refused_symlink = False
check("latch symlink refused", refused_symlink, True)
os.unlink(S.AUTH_BLOCK_FILE)
os.unlink(target)

alias_root = os.path.join(os.environ['XDG_RUNTIME_DIR'], 'state-alias-root')
writable_cache = os.path.join(os.environ['XDG_RUNTIME_DIR'], 'writable-cache')
os.mkdir(alias_root)
os.mkdir(writable_cache)
os.symlink(writable_cache, os.path.join(alias_root, 'state'))
S.AUTH_BLOCK_FILE = os.path.join(
    alias_root, 'state', 'zeropaper', 'wrds', 'authblock')
try:
    S._prepare_auth_block_dir()
except S.WrdsLatchError:
    refused_ancestor_symlink = True
else:
    refused_ancestor_symlink = False
check("state ancestor symlink into writable cache refused",
      refused_ancestor_symlink, True)

st5 = S.WrdsState(FakeDB())
with mock.patch.object(
        S, '_write_auth_block', side_effect=S.WrdsLatchError('disk unavailable')):
    try:
        st5._latch_auth_failure(PAM)
    except S.WrdsAuthError:
        pass
check("memory latch survives persistence error", st5.auth_blocked(), True)

print("\n[12] legacy wrds_utils routes through the latched client")
client_calls = []
U._DB = None
U._client_api = lambda: (
    lambda sql: client_calls.append(('query', sql)) or 'query-result',
    lambda library: client_calls.append(('tables', library)) or ['msf'],
    lambda library, table: client_calls.append(('describe', library, table)) or 'desc',
    lambda: client_calls.append(('libraries',)) or ['crsp'],
    lambda library, table, **kwargs: client_calls.append(
        ('get_table', library, table, kwargs)) or 'table-result',
)
check("wrds_utils.query result", U.query('SELECT 1'), 'query-result')
proxy = U.get_wrds()
check("proxy raw_sql result", proxy.raw_sql('SELECT 2'), 'query-result')
check("proxy list_tables result", proxy.list_tables('crsp'), ['msf'])
check("proxy describe result", proxy.describe_table('crsp', 'msf'), 'desc')
check("proxy list_libraries result", proxy.list_libraries(), ['crsp'])
check("proxy get_table result", proxy.get_table('crsp', 'msf', rows=3), 'table-result')
try:
    proxy.engine
except U.WrdsDirectAccessDisabled:
    engine_blocked = True
else:
    engine_blocked = False
check("proxy engine access fails explicitly", engine_blocked, True)
check("client route count", len(client_calls), 6)

print()
if FAILURES:
    print(f"FAILED ({len(FAILURES)}): " + ", ".join(FAILURES))
    sys.exit(1)
print("All WRDS auth-latch tests passed.")
PY

if rg -n '^[[:space:]]*(import[[:space:]]+wrds([[:space:]]|$)|from[[:space:]]+wrds([[:space:]]|$))|wrds\.Connection\(' \
    "$ROOT/extensions/empirical/utils/wrds_utils.py" \
    "$ROOT/../test_scripts/test_wrds.py" \
    "$ROOT/../test_scripts/wrds_explore.py"; then
    echo "FAILED: a compatibility/dev script contains a direct WRDS connection path" >&2
    exit 1
fi

if rg -n '\bdb\.(raw_sql|get_table|list_tables|describe_table)|^[[:space:]]*import wrds' \
    "$ROOT/templates/skill_bodies/empirical/wrds.md"; then
    echo "FAILED: WRDS skill still teaches a direct connection path" >&2
    exit 1
fi

if rg -n "['\"]cmd['\"]:[[:space:]]*['\"](query|ping|shutdown|unblock|list_tables|list_libraries|get_table|describe)['\"]" \
    "$ROOT/extensions/empirical/utils" "$ROOT/../test_scripts"; then
    echo "FAILED: legacy unversioned WRDS wire command remains" >&2
    exit 1
fi
