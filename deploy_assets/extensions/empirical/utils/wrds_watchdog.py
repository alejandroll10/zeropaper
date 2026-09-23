"""Launcher-side WRDS watchdog: repair the host daemon without an operator.

HOST ONLY. Started by start_services.sh when ./launch.sh establishes services
before sandbox entry; never run it inside a runtime sandbox (protected state
is read-only there, and the sandbox has no business restarting anything).

The watchdog repairs exactly the failure shapes that need no judgement (#322):

  * the daemon is gone (no endpoint, no live owner) -> restart it;
  * the daemon is alive but has failed every health probe for WEDGE_SECONDS
    with no in-budget command -> stop it (identity-verified) and restart it;
  * an older-protocol daemon holds the endpoint and no launcher is running in
    its deployment -> stop it and restart the current one.

Every restart is an ordinary start_services.sh start, so it is one
credential-bearing login -- one Duo push. The durable login latch bounds that:
a login that fails (a push nobody answered included) latches until the
operator's one-attempt `wrds_client.py unblock`, and the watchdog never acts
while any latch or live login attempt exists. A login that succeeds re-arms
the allowance. WRDS_AUTO_RELOGIN=0 removes the automatic attempt entirely
(an operator's own ./launch.sh start remains their approved login).

It only acts while some registered launcher is alive and its project needs
WRDS, so a daemon that dies after every run has finished costs no push; with
no such launcher for IDLE_EXIT_SECONDS it exits.

Usage (host):
    python code/utils/wrds_watchdog.py register --root <project> --pid <launcher pid>
    python code/utils/wrds_watchdog.py status
"""
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

try:
    from utils import wrds_client as C
    from utils import wrds_server as S
except ImportError:  # run directly as a script: sys.path[0] is this directory
    import wrds_client as C
    import wrds_server as S

WATCHDOG_PROTOCOL = 'wrds-watchdog-v1'
TICK_SECONDS = 30
WEDGE_SECONDS = 600
# A daemon rejecting every probe at its connection cap is usually busy, but
# 32 threads that never free up are indistinguishable from a wedge.
SATURATION_WEDGE_SECONDS = 2 * WEDGE_SECONDS
RESTART_BACKOFF_SECONDS = 300
MAX_FAILED_RESTARTS = 3
IDLE_EXIT_SECONDS = 600
RESTART_TIMEOUT_SECONDS = 300
PROBE_TIMEOUT_SECONDS = 180
LOG_ROTATE_BYTES = 5 * 1024 * 1024

STATE_DIR = os.path.dirname(C.WATCHDOG_STATUS_FILE)
STATUS_FILE = C.WATCHDOG_STATUS_FILE
LOCK_FILE = os.path.join(STATE_DIR, 'wrds_watchdog.lock')
LOG_FILE = os.path.join(STATE_DIR, 'wrds_watchdog.log')
REGISTRY_DIR = os.path.join(STATE_DIR, 'wrds_launchers')
NEEDS_WRDS_STATUSES = frozenset({
    'not_started', 'running', 'halted_wrds_unreachable'})


def _log(message):
    print(f"[wrds_watchdog {time.strftime('%F %T')}] {message}", flush=True)


def _atomic_write_json(path, payload):
    S._prepare_auth_block_dir()
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + '.',
                               dir=os.path.dirname(path))
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _read_json(path):
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return None
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or
                info.st_mode & 0o022 or info.st_size > 65536):
            return None
        value = json.loads(os.read(fd, 65536).decode('utf-8'))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError, UnicodeError):
        return None
    finally:
        os.close(fd)


# --- launcher registry ----------------------------------------------------

def _registry_path(root):
    digest = hashlib.sha256(str(root).encode('utf-8')).hexdigest()[:24]
    return os.path.join(REGISTRY_DIR, f'{digest}.json')


# Project files a restart executes on the host. Sandboxed agents can write the
# project tree, so a restart refuses to run any of them if it changed after
# the operator's launch -- otherwise the watchdog would turn an in-run edit
# into unsandboxed execution before the operator ever relaunched.
WRDS_EXECUTED_FILES = (
    'code/utils/start_services.sh', 'code/utils/wrds_server.py',
    'code/utils/wrds_client.py', 'code/utils/wrds_query_bridge.py',
    'code/utils/wrds_utils.py', 'code/utils/__init__.py',
)


def _file_digests(root):
    digests = {}
    for rel in WRDS_EXECUTED_FILES:
        try:
            digests[rel] = hashlib.sha256(
                (Path(root) / rel).read_bytes()).hexdigest()
        except OSError:
            digests[rel] = None
    return digests


def changed_wrds_files(entry):
    recorded = entry.get('digests')
    if not isinstance(recorded, dict):
        return list(WRDS_EXECUTED_FILES)
    current = _file_digests(entry['root'])
    return [rel for rel in WRDS_EXECUTED_FILES
            if recorded.get(rel) != current.get(rel)]


def register_launcher(root, pid):
    root = str(Path(root).resolve())
    birth = S._process_start_token(int(pid))
    if not birth:
        raise RuntimeError(f'launcher {pid} is not a live process')
    S._prepare_auth_block_dir()
    os.makedirs(REGISTRY_DIR, mode=0o700, exist_ok=True)
    _atomic_write_json(_registry_path(root), {
        'root': root, 'pid': int(pid), 'start': birth,
        'registered': time.time(), 'digests': _file_digests(root)})


def project_needs_wrds(root):
    """Same predicate launch.sh uses to decide whether to start services."""
    root = Path(root)
    state = root / 'process_log' / 'pipeline_state.json'
    manifest = root / '.deploy_manifest.json'
    try:
        if state.is_file() and not state.is_symlink():
            status = json.loads(state.read_text(encoding='utf-8')).get('status')
            return status in NEEDS_WRDS_STATUSES
        if manifest.is_file() and not manifest.is_symlink():
            data = json.loads(manifest.read_text(encoding='utf-8'))
            flags = data.get('flags') or {}
            return data.get('mode') == 'report' or flags.get('manual') is True
    except (OSError, ValueError, AttributeError):
        return False
    return False


def live_launchers():
    """Registered launchers still alive whose project needs WRDS, newest first.

    Entries whose launcher has exited are pruned.
    """
    live = []
    try:
        names = os.listdir(REGISTRY_DIR)
    except OSError:
        return live
    for name in names:
        if not name.endswith('.json'):
            continue
        path = os.path.join(REGISTRY_DIR, name)
        entry = _read_json(path)
        try:
            alive = bool(entry) and S._process_alive_as(
                int(entry['pid']), entry['start'])
        except (KeyError, TypeError, ValueError):
            alive = False
        if not alive:
            try:
                os.unlink(path)
            except OSError:
                pass
            continue
        if isinstance(entry.get('root'), str) and \
                project_needs_wrds(entry['root']):
            live.append(entry)
    live.sort(key=lambda e: e.get('registered', 0), reverse=True)
    return live


# --- probing --------------------------------------------------------------

def _owner_live():
    try:
        marker, _identity = S._read_instance_lock()
    except S.WrdsLatchError:
        return True  # unreadable marker: never treat the daemon as gone
    return bool(marker) and S._lock_owner_live(marker)


def _at_connection_cap(exc):
    # The daemon closes a new connection unanswered at its client-thread cap:
    # alive and saturated, not wedged.
    return 'incomplete WRDS response frame (0/8' in str(exc)


def probe():
    """Classify the daemon as (kind, detail). Never logs in or starts anything.

    kinds: healthy, saturated, login_in_progress, latched, unhealthy, down,
    incompatible.
    """
    try:
        C._safety_hello()
    except C._WrdsBusyAnswer:
        return 'saturated', 'WRDS service answered busy'
    except C.WrdsSafetyBlocked as e:
        return 'incompatible', str(e)
    except (OSError, ValueError) as e:
        persisted, message = C._persisted_auth_state()
        if persisted == 'in_progress':
            return 'login_in_progress', 'WRDS login in progress (approve Duo)'
        if persisted in ('blocked', 'unavailable'):
            return 'latched', message
        if _at_connection_cap(e):
            return 'saturated', 'WRDS daemon at its client-connection cap'
        if _owner_live():
            return 'unhealthy', f'daemon alive but not answering: {e!r}'
        try:
            others = S._legacy_server_pids()
        except S.WrdsLatchError:
            others = []
        if others:
            return 'incompatible', (
                'no current WRDS endpoint, but other wrds_server.py '
                f'process(es) are live: {others}')
        return 'down', f'no WRDS endpoint ({e!r})'
    try:
        resp = C._send_request({'cmd': 'safe_ping_v7'},
                               timeout=PROBE_TIMEOUT_SECONDS)
    except (OSError, ValueError) as e:
        if _at_connection_cap(e):
            return 'saturated', 'WRDS daemon at its client-connection cap'
        return 'unhealthy', f'health probe failed: {e!r}'
    if resp.get('status') == 'ok':
        return 'healthy', str(resp.get('db', 'ok'))
    if C._is_busy(resp):
        return 'saturated', resp.get('msg') or 'WRDS service answered busy'
    if resp.get('error_kind') == 'auth':
        return 'latched', resp.get('msg') or 'WRDS login latched'
    if resp.get('error_kind') == 'safety':
        return 'incompatible', resp.get('msg') or 'safety protocol mismatch'
    return 'unhealthy', resp.get('msg') or 'health probe failed'


# --- decisions (pure; unit-tested) ----------------------------------------

def decide(kind, detail, memory, now, auto_relogin=True, launch_epoch=0):
    """Map one probe to (action, state, detail); updates ``memory`` in place.

    action: None | 'restart' | 'stop_restart' | 'replace_incompatible'.
    state (published for clients): 'monitoring' | 'healing' |
    'operator_required'. Clients wait only while monitoring/healing.
    """
    if kind == 'healthy':
        memory.update(unhealthy_since=None, saturated_since=None,
                      failed_restarts=0)
        return None, 'monitoring', 'WRDS daemon healthy'
    if kind == 'saturated':
        # Answering "at capacity" proves the accept loop is alive, so it
        # clears the ordinary wedge clock -- but not forever: if no probe
        # gets through for SATURATION_WEDGE_SECONDS, every worker is stuck.
        memory['unhealthy_since'] = None
        since = memory.get('saturated_since')
        if since is None:
            memory['saturated_since'] = since = now
        if now - since < SATURATION_WEDGE_SECONDS:
            return None, 'monitoring', detail
        kind = 'unhealthy'
        memory['unhealthy_since'] = now - WEDGE_SECONDS
        detail = f'{detail} for {now - since:.0f}s with no probe served'
    else:
        memory['saturated_since'] = None
    if kind == 'login_in_progress':
        memory['unhealthy_since'] = None
        return None, 'healing', detail
    if kind == 'latched':
        memory['unhealthy_since'] = None
        return None, 'operator_required', (
            f'{detail} -- OPERATOR: fix the cause, then run '
            'python code/utils/wrds_client.py unblock (one login attempt).')
    if memory.get('failed_restarts', 0) >= MAX_FAILED_RESTARTS and (
            launch_epoch > memory.get('failed_epoch', 0) or
            (memory.get('failed_kind') == 'incompatible' and
             kind != 'incompatible')):
        # Only operator action lifts the cap: a new launch (fresh digests,
        # fresh intent) or removal of the blocking older daemon. A failure
        # kind that merely oscillates must not re-arm unbounded repairs.
        memory['failed_restarts'] = 0
    if memory.get('failed_restarts', 0) >= MAX_FAILED_RESTARTS:
        return None, 'operator_required', (
            f'{MAX_FAILED_RESTARTS} watchdog repairs failed without a login '
            f'outcome; last: {memory.get("last_failure", "?")}. OPERATOR: '
            f'inspect {LOG_FILE} and relaunch.')
    if auto_relogin is not True:
        source = (f" in {auto_relogin}/.env" if isinstance(auto_relogin, str)
                  else '')
        return None, 'operator_required', (
            f'{detail}; automatic re-login is disabled (WRDS_AUTO_RELOGIN=0'
            f'{source}). '
            'OPERATOR: run code/utils/start_services.sh on the host.')
    backoff_left = (memory.get('last_restart') or -1e18) + \
        RESTART_BACKOFF_SECONDS - now
    if kind == 'down':
        if backoff_left > 0:
            return None, 'healing', (
                f'{detail}; next repair in {backoff_left:.0f}s')
        return 'restart', 'healing', f'{detail}; restarting'
    if kind == 'unhealthy':
        since = memory.get('unhealthy_since')
        if since is None:
            memory['unhealthy_since'] = since = now
        elapsed = now - since
        if elapsed < WEDGE_SECONDS or backoff_left > 0:
            return None, 'healing', (
                f'{detail}; unhealthy for {elapsed:.0f}s, restart after '
                f'{WEDGE_SECONDS}s')
        return 'stop_restart', 'healing', (
            f'{detail}; unhealthy for {elapsed:.0f}s; restarting')
    if kind == 'incompatible':
        if backoff_left > 0:
            return None, 'healing', (
                f'{detail}; next repair in {backoff_left:.0f}s')
        return 'replace_incompatible', 'healing', detail
    return None, 'operator_required', f'unclassified WRDS state: {detail}'


# --- actions --------------------------------------------------------------

def _protocol_number(text):
    match = re.search(r'wrds-auth-latch-v(\d+)', text or '')
    return int(match.group(1)) if match else None


def _directory_has_flock(root):
    """Whether any process holds a flock on the directory ``root``.

    Every supported launcher keeps LOCK_SH on its project root for its whole
    lifetime. Read /proc/locks rather than probing with our own lock so a
    launcher starting at the same instant can never lose its non-blocking
    acquisition to us. Unknown -> True (never treat a project as abandoned).
    """
    try:
        info = os.stat(root)
        lines = Path('/proc/locks').read_text(encoding='ascii').splitlines()
    except OSError:
        return True
    want = (os.major(info.st_dev), os.minor(info.st_dev), info.st_ino)
    for line in lines:
        fields = line.split()
        if 'FLOCK' not in fields:
            continue
        for field in fields:
            parts = field.split(':')
            if len(parts) != 3:
                continue
            try:
                got = (int(parts[0], 16), int(parts[1], 16), int(parts[2]))
            except ValueError:
                continue
            if got == want:
                return True
    return False


def orphaned_incompatible_daemons():
    """Older-protocol wrds_server.py processes with no live launcher.

    Returns [(pid, birth)] when EVERY live server process is an older release
    whose deployment has no running launcher; otherwise None (not safe to
    act: a same/newer daemon means this watchdog is the stale party, and a
    live launcher means someone is still using that daemon).
    """
    ours = _protocol_number(C.SAFETY_PROTOCOL)
    try:
        pids = S._legacy_server_pids()
    except S.WrdsLatchError:
        return None
    found = []
    for pid in pids:
        birth = S._process_start_token(pid)
        try:
            cwd = os.readlink(f'/proc/{pid}/cwd')
        except OSError:
            return None
        root = S._deployed_wrds_root(cwd)
        if root is None:
            return None
        theirs = S._deployment_client_protocol(root)
        if theirs is not None and ours is not None and theirs >= ours:
            return None
        if _directory_has_flock(root):
            return None
        if not birth:
            return None
        found.append((pid, birth))
    return found or None


def run_start_services(root):
    """Restart through the project's own start path (one login, latch-bound)."""
    env = {k: v for k, v in os.environ.items()
           if k not in ('ZEROPAPER_LAUNCHER_PID', 'WRDS_USER', 'WRDS_PASS',
                        'PGPASSWORD')}
    env['ZEROPAPER_WATCHDOG_CHILD'] = '1'
    script = os.path.join(root, 'code', 'utils', 'start_services.sh')
    try:
        result = subprocess.run(
            ['/bin/bash', script], cwd=root, env=env,
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            timeout=RESTART_TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired:
        return False, 'start_services.sh timed out'
    except OSError as e:
        return False, f'cannot run start_services.sh: {e}'
    output = (result.stdout + result.stderr).strip()
    for line in output.splitlines():
        _log(f'  start_services: {line}')
    return result.returncode == 0, output[-400:]


def _fail(memory, kind, detail, terminal=False):
    memory['failed_kind'] = kind
    memory['failed_epoch'] = memory.get('launch_epoch', 0)
    memory['last_failure'] = detail
    memory['failed_restarts'] = (MAX_FAILED_RESTARTS if terminal else
                                 memory.get('failed_restarts', 0) + 1)


def perform(action, kind, launchers, memory, now):
    entry = launchers[0]
    root = entry['root']
    changed = changed_wrds_files(entry)
    if changed:
        _fail(memory, kind, (
            'refusing to execute project WRDS code that changed after the '
            f'operator launched it: {", ".join(changed)}. OPERATOR: review '
            'the change, then relaunch.'), terminal=True)
        return
    if action == 'stop_restart':
        stopped, detail = S.stop_singleton_owner()
        _log(f'stop wedged daemon: {detail}')
        if not stopped:
            memory['last_restart'] = now
            _fail(memory, kind, detail)
            return
    elif action == 'replace_incompatible':
        orphans = orphaned_incompatible_daemons()
        if not orphans:
            _fail(memory, kind, (
                'an incompatible WRDS daemon is live and is not provably '
                'orphaned (same/newer protocol, a live launcher in its '
                'deployment, or an unidentifiable process); stop it from the '
                'host or update this deployment'), terminal=True)
            return
        for pid, birth in orphans:
            stopped, detail = S.stop_process(pid, birth)
            _log(f'stop orphaned older daemon: {detail}')
            if not stopped:
                _fail(memory, kind, detail, terminal=True)
                return
    memory['last_restart'] = now
    memory['unhealthy_since'] = None
    memory['saturated_since'] = None
    ok, detail = run_start_services(root)
    _log(f'restart via {root}: {"ok" if ok else "FAILED"}')
    if ok:
        memory['failed_restarts'] = 0
        return
    # A failed login latches on its own and is reported by the next probe;
    # only failures that never reached a login count toward the repair cap.
    persisted, _message = C._persisted_auth_state()
    if persisted in ('none', 'unavailable'):
        # Neither proves a login happened; an unreadable latch also makes
        # every start refuse before credentials, so it must reach the cap.
        _fail(memory, kind, detail)


# --- singleton + loop -----------------------------------------------------

def _acquire_singleton():
    """O_EXCL link marker (a read-only sandbox view cannot hold it)."""
    S._prepare_auth_block_dir()
    birth = S._process_start_token(os.getpid())
    payload = json.dumps({'pid': os.getpid(), 'start': birth,
                          'protocol': WATCHDOG_PROTOCOL}) + '\n'
    for _ in range(4):
        fd, tmp = tempfile.mkstemp(prefix='wrds_watchdog.lock.', dir=STATE_DIR)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(tmp, LOCK_FILE, follow_symlinks=False)
                return True
            except FileExistsError:
                pass
        finally:
            os.unlink(tmp)
        holder = _read_json(LOCK_FILE)
        if holder and _holder_alive(holder):
            return False
        try:
            os.unlink(LOCK_FILE)
        except FileNotFoundError:
            pass
    return False


def _holder_alive(holder):
    try:
        return S._process_alive_as(int(holder['pid']), holder['start'])
    except (KeyError, TypeError, ValueError):
        return False


def _release_singleton():
    holder = _read_json(LOCK_FILE)
    if holder and holder.get('pid') == os.getpid():
        try:
            os.unlink(LOCK_FILE)
        except OSError:
            pass


def publish(state, detail, launchers):
    _atomic_write_json(STATUS_FILE, {
        'protocol': WATCHDOG_PROTOCOL, 'pid': os.getpid(), 'state': state,
        'detail': detail, 'updated': time.time(),
        'launchers': [e['root'] for e in launchers]})


def auto_relogin_enabled(launchers):
    """Re-read every tick; any live project's .env saying 0 is a veto.

    Returns True, False (watchdog environment), or the vetoing project root
    (the shared daemon serves every project, so the most conservative wins).
    """
    if os.environ.get('WRDS_AUTO_RELOGIN', '1').strip() == '0':
        return False
    for entry in launchers:
        if S.auto_relogin_setting(os.path.join(entry['root'], '.env')) == '0':
            return entry['root']
    return True


def run():
    if not _acquire_singleton():
        _log('another watchdog is running; exiting')
        return 0
    memory = {}
    idle_since = None
    _log(f'started ({WATCHDOG_PROTOCOL})')
    last_published = None
    try:
        while True:
            now = time.monotonic()
            launchers = live_launchers()
            if not launchers:
                idle_since = idle_since if idle_since is not None else now
                if now - idle_since >= IDLE_EXIT_SECONDS:
                    publish('stopped', 'no live launcher needs WRDS', [])
                    _log('no live launcher needs WRDS; exiting')
                    return 0
                publish('idle', 'no live launcher needs WRDS', [])
                time.sleep(TICK_SECONDS)
                continue
            idle_since = None
            memory['launch_epoch'] = max(
                e.get('registered', 0) for e in launchers)
            auto_relogin = auto_relogin_enabled(launchers)
            kind, detail = probe()
            action, state, message = decide(
                kind, detail, memory, now, auto_relogin=auto_relogin,
                launch_epoch=memory['launch_epoch'])
            if (state, action) != last_published or action:
                _log(f'{kind}: {state} -- {message}')
                last_published = (state, action)
            publish(state, message, launchers)
            if action:
                perform(action, kind, launchers, memory, now)
                continue
            time.sleep(TICK_SECONDS)
    finally:
        _release_singleton()


def ensure_running(python=sys.executable):
    """Start the singleton watchdog unless a current-protocol one is live."""
    holder = _read_json(LOCK_FILE)
    if holder and _holder_alive(holder):
        if holder.get('protocol') == WATCHDOG_PROTOCOL:
            return 'already running'
        stopped, detail = S.stop_process(int(holder['pid']), holder['start'])
        if not stopped:
            return f'NOT upgraded: older watchdog could not be stopped ({detail})'
    S._prepare_auth_block_dir()
    try:
        if os.path.getsize(LOG_FILE) > LOG_ROTATE_BYTES:
            os.replace(LOG_FILE, LOG_FILE + '.1')
    except OSError:
        pass
    env = {k: v for k, v in os.environ.items()
           if k not in ('WRDS_USER', 'WRDS_PASS', 'PGPASSWORD',
                        'ZEROPAPER_LAUNCHER_PID')}
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0)
    log_fd = os.open(LOG_FILE, flags, 0o600)
    try:
        subprocess.Popen(
            [python, '-u', os.path.abspath(__file__), 'run'],
            cwd=STATE_DIR, env=env, stdin=subprocess.DEVNULL, stdout=log_fd,
            stderr=subprocess.STDOUT, start_new_session=True)
    finally:
        os.close(log_fd)
    return 'started'


def main(argv):
    if len(argv) >= 1 and argv[0] == 'run':
        return run()
    if len(argv) == 5 and argv[0] == 'register' and argv[1] == '--root' \
            and argv[3] == '--pid':
        register_launcher(argv[2], argv[4])
        print(f'WRDS watchdog: {ensure_running()}')
        return 0
    if argv == ['status']:
        status = C.wrds_watchdog_status()
        print(json.dumps(status, indent=2) if status else 'not running')
        return 0
    print('usage: wrds_watchdog.py register --root <dir> --pid <pid> | status',
          file=sys.stderr)
    return 64


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
