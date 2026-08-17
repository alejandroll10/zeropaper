#!/bin/bash
# launch.sh — start a pipeline runtime for this project.
#
# Usage:
#   ./launch.sh claude              # interactive Claude Code (autowake-native)
#   ./launch.sh codex               # HEADLESS DRIVER LOOP (see below) — the
#                                   #   autonomous way to run the codex runtime
#   ./launch.sh codex --once        # single interactive codex TUI, no driver
#   ./launch.sh gemini              # interactive Gemini CLI
#   ./launch.sh grok                # interactive Grok Build
#   ./launch.sh opencode            # persistent-server OpenCode driver
#   ./launch.sh opencode --once     # interactive OpenCode TUI
#   ./launch.sh <runtime> --tmux    # same, wrapped in a detached tmux window
#
# WHY THE CODEX DRIVER EXISTS: a completed primary turn is inert until a new
# message arrives. The orchestrator therefore contains every native subagent
# cohort inside the turn that spawned it (spawn -> wait -> validate), while the
# driver makes ordinary stage-to-stage turn ends autonomous: it runs each turn
# headlessly (`codex exec`, then `codex exec resume <session>` — same session,
# full context) and immediately re-prompts until pipeline_state.json reports
# complete or halted_*. Ending a primary turn with a live native child is
# forbidden because `codex exec` shuts down its in-process agent server and
# interrupts that child.
#
# Cost guard (two ceilings; details at the guard itself): the driver aborts on
# 5 consecutive sub-60s turns that also commit NOTHING (a stuck/refusing model),
# or on a much longer run of sub-60s turns even with commits (a coarse token-burn
# backstop against a churn-committing retry loop). Native child runtime is part
# of its parent turn because the parent must wait for completion before
# returning, so no separate worker-duration accounting is needed.
set -euo pipefail

# pwd -P (physical): codex records its cwd via getcwd(), which resolves
# symlinks (macOS /tmp -> /private/tmp). find_sid matches our path against the
# recorded one, so ROOT must be the physical form or resume silently degrades
# to a fresh session on any symlinked project path.
_launch_source="${BASH_SOURCE[0]}"
case "$_launch_source" in */*) _launch_dir="${_launch_source%/*}" ;; *) _launch_dir=. ;; esac
ROOT="$(cd "$_launch_dir" && pwd -P)"
cd "$ROOT"

_launch_is_internal=0
_launch_internal_supervisor_pid=""
if [ "${ZEROPAPER_LAUNCH_INTERNAL:-}" = "1" ]; then
    # The lock-owning parent passes its already-open project descriptor as the
    # internal-child capability. Validate identity, close it immediately so no
    # runtime descendant can retain the flock, and remove the marker from the
    # runtime environment before any CLI starts.
    /usr/bin/python3 -I -c '
import os, stat, sys
fd = int(sys.argv[1])
left, right = os.fstat(fd), os.stat(sys.argv[2])
raise SystemExit(0 if stat.S_ISDIR(left.st_mode) and
                 (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)
                 else 1)
' 8 "$ROOT" || { echo "ERROR: invalid internal launcher project descriptor" >&2; exit 1; }
    _launch_internal_supervisor_pid="${ZEROPAPER_LAUNCH_SUPERVISOR_PID:-}"
    case "$_launch_internal_supervisor_pid" in
        ''|*[!0-9]*) echo "ERROR: invalid internal launcher supervisor identity" >&2; exit 1 ;;
    esac
    # Reacquire the shared lock on a private descriptor owned only by a tiny
    # direct-child keeper. This makes forged internal entry no bypass: it still
    # fails under an updater's LOCK_EX and, if admitted, keeps LOCK_SH for the
    # complete runtime-shell lifetime without leaking it into CLI descendants.
    _launch_internal_ready=""
    read -r _launch_internal_ready < <(/usr/bin/python3 -I -c '
import fcntl, os, sys, time
try:
    os.close(8)  # drop the outer parent open-file-description in this helper
except OSError:
    pass
try:
    os.close(7)  # guardian liveness/arming writer belongs to trusted shells
except OSError:
    pass
os.setsid()  # remain runnable while terminal Ctrl-Z stops the runtime group
fd = os.open(sys.argv[1], os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
try:
    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(75)
parent = os.getppid()
print("locked", flush=True)
while os.getppid() == parent:
    time.sleep(0.1)
' "$ROOT")
    _launch_internal_keeper=$!
    [ "$_launch_internal_ready" = "locked" ] \
        && kill -0 "$_launch_internal_keeper" 2>/dev/null || {
        echo "ERROR: could not reacquire the internal project runtime/update lock" >&2
        exit 1
    }
    exec 8<&-
    unset ZEROPAPER_LAUNCH_INTERNAL ZEROPAPER_LAUNCH_SUPERVISOR_PID
    _launch_is_internal=1
fi

# Every supported runtime holds a shared lock on the project-root inode for its
# full process lifetime. Bash owns descriptor 9; the short isolated-Python
# helper applies flock to that inherited open file description and exits while
# Bash keeps it live. Interactive branches remain child processes rather than
# replacing this shell. No pathname lock/readiness file exists.
if [ "$_launch_is_internal" = "0" ] && ! exec 9< .; then
    echo "ERROR: could not open the project runtime/update lock" >&2
    exit 1
fi
if [ "$_launch_is_internal" = "0" ] && ! /usr/bin/python3 -I - 9 <<'PY'
import fcntl
import os
import stat
import sys

fd = int(sys.argv[1])
info = os.fstat(fd)
if not stat.S_ISDIR(info.st_mode):
    raise SystemExit("invalid project root lock")
try:
    fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(75)
PY
then
    echo "ERROR: could not acquire the project runtime/update lock" >&2
    exit 1
fi

# A --tmux handoff keeps its original shared lock until this nested launcher has
# acquired its own. Publish through one parent-created regular file only after
# flock succeeds; failure paths in the tmux command publish `failed` instead.
if [ "$_launch_is_internal" = "0" ] && [ -n "${ZEROPAPER_LAUNCH_READY_FILE:-}" ]; then
    /usr/bin/python3 -I -c '
import os, stat, sys
path = sys.argv[1]
flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL |
         getattr(os, "O_NOFOLLOW", 0))
fd = os.open(path, flags, 0o600)
info = os.fstat(fd)
if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
        info.st_uid != os.geteuid()):
    os.close(fd)
    raise SystemExit("unsafe launcher readiness file")
os.write(fd, b"acquired\n")
os.fsync(fd)
os.close(fd)
' "$ZEROPAPER_LAUNCH_READY_FILE" || {
        echo "ERROR: could not publish nested launcher lock readiness" >&2
        exit 1
    }
    unset ZEROPAPER_LAUNCH_READY_FILE
fi

_launch_runtime_main() {
RUNTIME="${1:?Usage: ./launch.sh <claude|codex|gemini|grok|opencode> [--tmux] [--once]}"
shift
TMUX_WRAP=0
ONCE=0
while [ $# -gt 0 ]; do
    case "$1" in
        --tmux) TMUX_WRAP=1; shift ;;
        --once) ONCE=1; shift ;;
        *) echo "ERROR: unknown option '$1'" >&2; exit 2 ;;
    esac
done

# Reject before any service/cache side effect. In particular, a typo must not
# start WRDS and spend a Duo/login attempt before the runtime is diagnosed.
case "$RUNTIME" in
    claude|codex|gemini|grok|opencode) ;;
    *) echo "ERROR: unknown runtime '$RUNTIME' (claude|codex|gemini|grok|opencode)" >&2; exit 2 ;;
esac

# The Codex driver is meaningful only for an autonomous deployment. Reject a
# stateless report/manual invocation before WRDS prestart: the service must not
# spend a Duo/login attempt for a command that is guaranteed to exit later.
if [ "$RUNTIME" = "codex" ] && [ "$ONCE" != "1" ] && \
        { [ ! -f "$ROOT/process_log/pipeline_state.json" ] || \
          [ -L "$ROOT/process_log/pipeline_state.json" ]; }; then
    echo "ERROR: no regular process_log/pipeline_state.json — report/manual Codex sessions require: ./launch.sh codex --once" >&2
    exit 1
fi

# Capture the caller environment for sandboxed OpenCode children, then remove
# project/temp/cache paths before even the optional tmux re-exec. This closes
# the pre-branch shebang/dirname/tmux trust gap for an activated project venv.
OPENCODE_CALLER_PATH="${PATH:-}"
if [ "$RUNTIME" = "opencode" ]; then
    _oc_early_path=""
    IFS=: read -r -a _oc_early_entries <<< "${PATH:-}"
    for _oc_early_entry in /usr/bin /bin /usr/sbin /sbin "${_oc_early_entries[@]}"; do
        [ -n "$_oc_early_entry" ] && [ -d "$_oc_early_entry" ] || continue
        _oc_early_physical="$(cd "$_oc_early_entry" 2>/dev/null && pwd -P)" || continue
        case "$_oc_early_physical" in
            "$ROOT"|"$ROOT"/*|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var/tmp|/var/tmp/*|/private/var/folders|/private/var/folders/*|\
            "$HOME/.local/share/opencode"|"$HOME/.local/share/opencode"/*|\
            "$HOME/.local/state/opencode"|"$HOME/.local/state/opencode"/*|\
            "$HOME/.cache"|"$HOME/.cache"/*|"$HOME/Library/Caches"|"$HOME/Library/Caches"/*|\
            "$HOME/.matplotlib"|"$HOME/.matplotlib"/*|"$HOME/.codex"|"$HOME/.codex"/*)
                continue ;;
        esac
        case ":$_oc_early_path:" in *":$_oc_early_physical:"*) ;; *)
            _oc_early_path="${_oc_early_path:+$_oc_early_path:}$_oc_early_physical" ;;
        esac
    done
    [ -n "$_oc_early_path" ] || { echo "ERROR: no trusted OpenCode launcher PATH remains" >&2; exit 1; }
    PATH="$_oc_early_path"
    export PATH
    hash -r
fi

# Re-wrap into tmux first, so everything below runs inside the window.
if [ "$TMUX_WRAP" = "1" ]; then
    _win="pipeline-$RUNTIME-${ROOT##*/}"
    _tmux_ready_dir="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-launch-ready.XXXXXX")"
    chmod 700 "$_tmux_ready_dir"
    _tmux_ready="$_tmux_ready_dir/acquired"
    # `|| true`: the && chain returns 1 when ONCE=0, and an assignment's exit
    # status is its command substitution's — without the guard, set -e kills
    # the script right here, silently, on every plain `--tmux` launch.
    _cmd="cd $(printf '%q' "$ROOT") && ZEROPAPER_LAUNCH_READY_FILE=$(printf '%q' "$_tmux_ready") ./launch.sh $(printf '%q' "$RUNTIME")$( [ "$ONCE" = "1" ] && printf ' --once' || true )"
    if [ -n "${TMUX:-}" ]; then
        tmux new-window -n "$_win" "$_cmd"
    else
        tmux new-session -d -s "$_win" "$_cmd"
    fi
    _tmux_status=""
    _tmux_attempt=0
    while [ "$_tmux_attempt" -lt 1000 ]; do
        _tmux_attempt=$((_tmux_attempt + 1))
        if [ -s "$_tmux_ready" ]; then
            _tmux_status="$(cat "$_tmux_ready")"
            break
        fi
        sleep 0.01
    done
    rm -f "$_tmux_ready"
    rmdir "$_tmux_ready_dir" 2>/dev/null || true
    [ "$_tmux_status" = "acquired" ] || {
        echo "ERROR: tmux runtime failed to acquire the project lock" >&2
        exit 1
    }
    if [ -z "${TMUX:-}" ]; then
        echo "Launched in tmux session '$_win' — attach with: tmux attach -t $_win"
    fi
    exit 0
fi

# Every runtime wants the project venv active. OpenCode is different: its
# unsandboxed control plane must never source or execute project-writable venv
# files, so only the sandboxed server/client descendants receive this PATH.
OPENCODE_CHILD_PATH="$OPENCODE_CALLER_PATH"
OPENCODE_CHILD_VIRTUAL_ENV=""
if [ "$RUNTIME" = "opencode" ]; then
    if [ -f "$ROOT/.venv/bin/activate" ]; then
        OPENCODE_CHILD_PATH="$ROOT/.venv/bin:$OPENCODE_CHILD_PATH"
        OPENCODE_CHILD_VIRTUAL_ENV="$ROOT/.venv"
    else
        echo "WARNING: no .venv in this project — python deps may be missing (create with: uv venv .venv)" >&2
    fi
elif [ -f "$ROOT/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ROOT/.venv/bin/activate"
else
    echo "WARNING: no .venv in this project — python deps may be missing (create with: uv venv .venv)" >&2
fi

# Validate permission-profile support before any empirical service may spend a
# login. The CLI SessionFlags layer below has higher precedence than legacy
# sandbox keys in project/user config, including for the interactive TUI.
if [ "$RUNTIME" = "codex" ]; then
    [ -f "$ROOT/code/utils/codex_preflight.sh" ] || {
        echo "ERROR: missing code/utils/codex_preflight.sh — run update.sh to refresh this deployment" >&2
        exit 1
    }
    # shellcheck source=/dev/null
    . "$ROOT/code/utils/codex_preflight.sh"
    codex_permission_profile_preflight
fi

# Start host-wide empirical services before entering a runtime's network
# sandbox. Loopback inside Claude/Codex is a different network namespace, so a
# daemon spawned later by an agent command either disappears with that command
# or is unreachable from the next one. The WRDS client crosses back to this
# singleton over its private Unix socket under host-owned ~/.local/state.
#
# Preserve the session contract: completed and halted runs do not spend a WRDS
# login merely because somebody opened the runtime. OpenCode establishes the
# same service later through a long-lived SRT wrapper, so its unsandboxed
# control plane never executes the project venv/code. Gemini remains wholly
# unconfined (#187) and may not establish/protect the host service.
project_services_action() {
    [ -f "$ROOT/code/utils/start_services.sh" ] || { printf 'skip\n'; return 0; }
    /usr/bin/python3 -I - \
        "$ROOT/process_log/pipeline_state.json" \
        "$ROOT/.deploy_manifest.json" <<'PY' 2>/dev/null || true
import json, sys
from pathlib import Path

state_path, manifest_path = map(Path, sys.argv[1:])
try:
    if state_path.is_file() and not state_path.is_symlink():
        status = json.loads(state_path.read_text(encoding='utf-8')).get('status')
        print('start' if status in {'not_started', 'running'} else 'skip')
    elif manifest_path.is_file() and not manifest_path.is_symlink():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        flags = manifest.get('flags') or {}
        # Manual toolkits and one-shot report deployments intentionally have
        # no pipeline_state.json, but empirical tools are available there.
        print('start' if (manifest.get('mode') == 'report' or
                          flags.get('manual') is True) else 'skip')
    else:
        print('skip')
except Exception:
    print('skip')
PY
}

prestart_project_services() {
    case "$RUNTIME" in opencode|gemini) return 0 ;; esac
    local service_action
    service_action="$(project_services_action)"
    case "$service_action" in
        start)
            echo "[launch] Establishing host-wide data services before sandbox entry…" >&2
            bash "$ROOT/code/utils/start_services.sh"
            ;;
    esac
}

prestart_project_services

# Claude's bwrap backend, Codex's Landlock policy, and Grok's profile resolve
# writable roots at sandbox creation time. Materialize and descriptor-validate
# every external root first. A pre-v5 broad-cache sandbox could have planted a
# cache symlink to protected WRDS state; following it here would silently grant
# that target to the new sandbox.
prepare_runtime_cache_roots() {
    case "$RUNTIME" in claude|codex|grok) ;; *) return 0 ;; esac
    /usr/bin/python3 -I "$ROOT/code/utils/sandbox_cache_roots.py"
}

prepare_runtime_cache_roots

# ── grok helpers ─────────────────────────────────────────────────────────────
# grok's bash tool rebuilds PATH with its own dirs (~/.grok/bin, ~/.local/bin)
# and the macOS defaults ahead of every inherited entry, demoting the activated
# venv below /usr/bin — so bare python3 resolves to the system interpreter with
# none of the pipeline's deps (verified on grok 0.2.93; grok has no config knob
# to reorder its bash PATH — issue #190). Fix: VIRTUAL_ENV-keyed shims in
# ~/.local/bin, which grok's rebuild keeps ahead of /usr/bin. Transparent
# everywhere else: with no active venv the shim execs the next real binary on
# PATH, so host behavior outside grok is unchanged. Never overwrites a
# pre-existing file that isn't ours.
install_grok_venv_shims() {
    local dir="$HOME/.local/bin" marker="zeropaper-grok-venv-shim" name shim
    mkdir -p "$dir"
    for name in python3 python pip3 pip; do
        shim="$dir/$name"
        if [ -e "$shim" ] && ! grep -q "$marker" "$shim" 2>/dev/null; then
            echo "WARNING: $shim exists and is not the pipeline's venv shim — leaving it alone; grok's bare $name may bypass the project venv" >&2
            continue
        fi
        cat > "$shim" <<EOF
#!/usr/bin/env bash
# $marker v1 — routes bare $name to the active venv. grok's bash tool rebuilds
# PATH with this dir ahead of /usr/bin but the inherited venv behind it; this
# shim restores venv-first resolution. Inert without a venv: falls through to
# the next $name on PATH. Safe to delete; ./launch.sh grok reinstalls it.
if [ -n "\${VIRTUAL_ENV:-}" ] && [ -x "\$VIRTUAL_ENV/bin/$name" ]; then
    exec "\$VIRTUAL_ENV/bin/$name" "\$@"
fi
self_dir="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd -P)"
# newline-delimited read, not word-splitting: a PATH dir with a space must not
# shear a candidate path in two (a sheared path would kill the shim via exec).
while IFS= read -r cand; do
    [ -n "\$cand" ] || continue
    [ "\$(cd "\$(dirname "\$cand")" && pwd -P)" = "\$self_dir" ] && continue
    exec "\$cand" "\$@"
done < <(type -aP $name)
echo "$name: no real binary found on PATH ($marker fallback)" >&2
exit 127
EOF
        chmod +x "$shim"
    done
}

# grok's Seatbelt sandbox cannot reach the macOS keychain (the osxkeychain
# helper needs mach-lookup com.apple.SecurityServer, which grok's sandbox
# schema — filesystem+network only — cannot grant; issue #190). With an HTTPS
# remote that still uses the keychain, every pipeline `git push` fails on auth
# (commits stay local). Warn once at launch; the fix is the repo-scoped token
# store set up by code/utils/setup_push_token.sh.
warn_grok_keychain_push() {
    local url
    url="$(git -C "$ROOT" remote get-url origin 2>/dev/null || true)"
    case "$url" in
        https://*)
            if [ ! -f "$ROOT/.git/push-credentials" ]; then
                echo "NOTE: HTTPS remote + no .git/push-credentials — 'git push' will fail inside grok's sandbox (keychain unreachable)." >&2
                echo "      Commits stay local. To enable pushes: bash code/utils/setup_push_token.sh (fine-grained PAT for this repo)." >&2
            fi
            ;;
    esac
}

# Launch-time model heal (Claude only — it rewrites .claude/agents/*.md). Re-decide
# each subagent's tier against live availability: restore its ideal model when that
# recovers, fall back again when it is down. Strictly best-effort — a missing
# script/config, an absent `claude` CLI, or any probe error leaves every pin
# untouched and the launch proceeds. Never blocks or fails a launch (hence the
# guard; the healer also exits 0 on every internal skip). See docs/model_fallback.md.
heal_claude_models() {
    local dir="$ROOT/.claude/agents"
    local script="$ROOT/code/utils/model_heal/heal_agent_models.py"
    local cfg="$ROOT/code/utils/model_heal/config.json"
    [ -d "$dir" ] && [ -f "$script" ] && [ -f "$cfg" ] || return 0
    # A snappier per-probe timeout than the build-time 120s: this is on the
    # interactive launch path, and an inconclusive (slow) probe is now safe — it
    # leaves the pin untouched and the next launch retries. Worst case is bounded
    # to (distinct ideal tiers) * timeout, and only on a genuinely dead network.
    echo "Checking subagent model availability (best-effort; Ctrl-C to skip)…" >&2
    python3 "$script" --agents-dir "$dir" --config "$cfg" --timeout 30 || true
}

# ── Light-mode orchestrator pin ──────────────────────────────────────────────
# --light drops every SUBAGENT to the cheapest tier its runtime offers, but the
# orchestrator is launched by this script and would otherwise keep running on
# whatever the CLI's session default is — so a "light" run was light everywhere
# except the process doing the most work. These two helpers close that.
#
# The tier string is NOT hardcoded here. It is read back from the assembled
# agents, the only copy guaranteed to be current: it survives update.sh, it
# already reflects each runtime's own tier table (the assemblers' MODEL_MAPs),
# and for claude it reflects the launch-time heal that runs just above. A pin is
# emitted only when the manifest says --light AND every assembled agent agrees
# on one model — belt and braces, since a mixed roster means something other
# than --light produced it. Grok is excluded by design: its table is a single
# model (grok-4.5), so its roster is uniform in every deployment and there is
# no cheaper tier to drop to.
#
# Best-effort throughout: a missing manifest (pre-manifest deployment), absent
# python3, or an unreadable agents dir yields no pin and the CLI default stands.
deploy_is_light() {
    local mf="$ROOT/.deploy_manifest.json"
    [ -f "$mf" ] || return 1
    python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))["flags"]["light"] else 1)' \
        "$mf" 2>/dev/null
}

light_orchestrator_model() {   # $1 = assembled-agents dir; echoes the model or nothing
    local dir="$1" models
    deploy_is_light || return 0
    [ -d "$dir" ] || return 0
    models=$(grep -h -E '^model[[:space:]]*[:=]' "$dir"/* 2>/dev/null \
        | sed -E 's/^model[[:space:]]*[:=][[:space:]]*//; s/^"//; s/"$//' \
        | sort -u) || true
    [ -n "$models" ] || return 0
    [ "$(printf '%s\n' "$models" | wc -l | tr -d ' ')" = "1" ] || return 0
    printf '%s\n' "$models"
}

case "$RUNTIME" in
    claude)
        heal_claude_models
        # Pinned after the heal, so a healed tier (not the pre-heal one) is what
        # the orchestrator gets.
        LIGHT_ARGS=()
        _light_model="$(light_orchestrator_model "$ROOT/.claude/agents")"
        if [ -n "$_light_model" ]; then
            LIGHT_ARGS=(--model "$_light_model")
            echo "[launch] --light: orchestrator pinned to $_light_model" >&2
        fi
        claude ${LIGHT_ARGS[@]+"${LIGHT_ARGS[@]}"} --dangerously-skip-permissions
        exit
        ;;
    gemini)
        LIGHT_ARGS=()
        _light_model="$(light_orchestrator_model "$ROOT/.gemini/agents")"
        if [ -n "$_light_model" ]; then
            LIGHT_ARGS=(--model "$_light_model")
            echo "[launch] --light: orchestrator pinned to $_light_model" >&2
        fi
        gemini ${LIGHT_ARGS[@]+"${LIGHT_ARGS[@]}"} --yolo
        exit
        ;;
    grok)
        install_grok_venv_shims
        warn_grok_keychain_push
        # Per-project leader socket: all grok clients share ~/.grok/leader.sock
        # by default, and a second client on that socket TEARS DOWN the first
        # session's in-flight turn — concurrent projects would cancel each
        # other (issue #186/#190; see README).
        grok --sandbox pipeline --always-approve --leader-socket "$ROOT/.grok/leader.sock"
        exit
        ;;
    codex|opencode) ;;  # falls through to the appropriate driver below
    *)
        echo "ERROR: unknown runtime '$RUNTIME' (claude|codex|gemini|grok|opencode)" >&2
        exit 2
        ;;
esac

# ── opencode ─────────────────────────────────────────────────────────────────
# OpenCode discovers the deployed Claude-compatible and Agent-compatible
# SKILL.md files natively. Its custom subagents are separately assembled into
# .opencode/agents because Claude agent frontmatter is not compatible.
if [ "$RUNTIME" = "opencode" ]; then
    # The server and attached OpenCode clients run inside SRT, but this driver
    # deliberately remains outside so it can supervise/restart them. Remove
    # every sandbox-writable directory (including a caller-activated project
    # venv) from its executable search path. Resolve symlinks now so a trusted
    # lexical PATH entry cannot point back into a writable tree.
    OC_CONTROL_PATH=""
    IFS=: read -r -a _oc_path_entries <<< "${PATH:-}"
    for _oc_path_entry in "${_oc_path_entries[@]}" /usr/bin /bin /usr/sbin /sbin; do
        [ -n "$_oc_path_entry" ] && [ -d "$_oc_path_entry" ] || continue
        _oc_path_physical="$(cd "$_oc_path_entry" 2>/dev/null && pwd -P)" || continue
        case "$_oc_path_physical" in
            "$ROOT"|"$ROOT"/*|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var/tmp|/var/tmp/*|/private/var/folders|/private/var/folders/*|\
            "$HOME/.local/share/opencode"|"$HOME/.local/share/opencode"/*|\
            "$HOME/.local/state/opencode"|"$HOME/.local/state/opencode"/*|\
            "$HOME/.cache"|"$HOME/.cache"/*|"$HOME/Library/Caches"|"$HOME/Library/Caches"/*|\
            "$HOME/.matplotlib"|"$HOME/.matplotlib"/*|"$HOME/.codex"|"$HOME/.codex"/*)
                continue
                ;;
        esac
        case ":$OC_CONTROL_PATH:" in
            *":$_oc_path_physical:"*) ;;
            *) OC_CONTROL_PATH="${OC_CONTROL_PATH:+$OC_CONTROL_PATH:}$_oc_path_physical" ;;
        esac
    done
    [ -n "$OC_CONTROL_PATH" ] || { echo "ERROR: no trusted control-plane PATH remains" >&2; exit 1; }
    PATH="$OC_CONTROL_PATH"
    export PATH
    unset VIRTUAL_ENV PYTHONHOME PYTHONPATH PYTHONSTARTUP PYTHONINSPECT
    export PYTHONNOUSERSITE=1
    hash -r
    # Prefer the OS interpreter over user-managed/Conda shims. Besides being a
    # smaller trust path, this avoids rejecting legitimate Conda package-cache
    # hard links when a safe system interpreter is available.
    if [ -f /usr/bin/python3 ] && [ -x /usr/bin/python3 ]; then
        OC_CONTROL_PYTHON=/usr/bin/python3
    else
        OC_CONTROL_PYTHON="$(command -v python3 || true)"
    fi
    [ -n "$OC_CONTROL_PYTHON" ] || { echo "ERROR: trusted python3 is unavailable" >&2; exit 1; }
    _oc_python_depth=0
    while [ -L "$OC_CONTROL_PYTHON" ]; do
        _oc_python_depth=$((_oc_python_depth + 1))
        [ "$_oc_python_depth" -le 16 ] || {
            echo "ERROR: trusted python3 has an excessive or cyclic symlink chain" >&2; exit 1;
        }
        _oc_python_link="$(readlink "$OC_CONTROL_PYTHON")" || {
            echo "ERROR: cannot resolve trusted python3" >&2; exit 1;
        }
        case "$_oc_python_link" in
            /*) OC_CONTROL_PYTHON="$_oc_python_link" ;;
            *) OC_CONTROL_PYTHON="$(cd "$(dirname "$OC_CONTROL_PYTHON")" && pwd -P)/$_oc_python_link" ;;
        esac
    done
    OC_CONTROL_PYTHON="$(cd "$(dirname "$OC_CONTROL_PYTHON")" 2>/dev/null && pwd -P)/$(basename "$OC_CONTROL_PYTHON")"
    case "$OC_CONTROL_PYTHON" in
        "$ROOT"|"$ROOT"/*|/tmp|/tmp/*|/private/tmp|/private/tmp/*|/var/tmp|/var/tmp/*|/private/var/folders|/private/var/folders/*|\
        "$HOME/.cache"|"$HOME/.cache"/*|"$HOME/Library/Caches"|"$HOME/Library/Caches"/*|\
        "$HOME/.matplotlib"|"$HOME/.matplotlib"/*|"$HOME/.codex"|"$HOME/.codex"/*)
            echo "ERROR: trusted python3 resolves inside a sandbox-writable path: $OC_CONTROL_PYTHON" >&2
            exit 1
            ;;
    esac
    [ -f "$OC_CONTROL_PYTHON" ] && [ -x "$OC_CONTROL_PYTHON" ] || {
        echo "ERROR: resolved trusted python3 is not executable: $OC_CONTROL_PYTHON" >&2; exit 1;
    }
    case "$(/usr/bin/uname -s)" in
        Darwin) _oc_python_stat="$(/usr/bin/stat -f '%l %u' "$OC_CONTROL_PYTHON")" ;;
        *) _oc_python_stat="$(/usr/bin/stat -c '%h %u' "$OC_CONTROL_PYTHON")" ;;
    esac
    _oc_python_nlink="${_oc_python_stat%% *}"
    _oc_python_uid="${_oc_python_stat##* }"
    if [ "$_oc_python_nlink" != "1" ] && [ "$_oc_python_uid" = "$EUID" ]; then
        echo "ERROR: user-owned trusted python3 has alternate hard links: $OC_CONTROL_PYTHON" >&2
        exit 1
    fi
    # -I also removes cwd and user site-packages from sys.path, preventing a
    # sandboxed run from planting json.py/sitecustomize.py for the driver.
    python3() { "$OC_CONTROL_PYTHON" -I "$@"; }
    export ZEROPAPER_OPENCODE_CHILD_PATH="$OPENCODE_CHILD_PATH"
    export ZEROPAPER_OPENCODE_CHILD_VIRTUAL_ENV="$OPENCODE_CHILD_VIRTUAL_ENV"

    # OpenCode's provider reads this key from the process environment, while
    # deployments store credentials in a gitignored project .env. Import only
    # this one value without sourcing/evaluating arbitrary shell text. An
    # already-exported value wins over the file.
    if [ -z "${OPENCODE_API_KEY:-}" ] && { [ -e "$ROOT/.env" ] || [ -L "$ROOT/.env" ]; }; then
        OPENCODE_API_KEY="$(python3 - "$ROOT/.env" <<'PY'
import ast, os, re, stat, sys

def strip_inline_comment(text):
    quote = None
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if quote:
            if quote == '"' and char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip()
    return text.strip()

flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    os.close(fd)
    raise SystemExit("unsafe .env: expected one regular non-aliased file")

for raw in os.fdopen(fd, encoding="utf-8"):
    line = raw.strip()
    if line.startswith("export "):
        line = line[7:].lstrip()
    match = re.match(r"OPENCODE_API_KEY\s*=\s*(.*)$", line)
    if not match:
        continue
    value = strip_inline_comment(match.group(1).strip())
    if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            value = value[1:-1]
    print(value, end="")
    break
PY
)"
        [ -z "$OPENCODE_API_KEY" ] || export OPENCODE_API_KEY
    fi
    # Select the Claude-compatible skill tree explicitly. Deployments also
    # contain .agents/skills; scanning both would create duplicate skill IDs.
    export OPENCODE_DISABLE_EXTERNAL_SKILLS=1
    # Keep the helper/server Basic-auth identity stable even if the caller has
    # a different global OpenCode server username configured.
    export OPENCODE_SERVER_USERNAME=opencode
    # OpenCode omits the `background` field from the task schema when this
    # experimental capability is unavailable. Keeping the flag at the process
    # boundary therefore degrades safely: capable versions expose native
    # background tasks; older versions continue to offer foreground task calls.
    export OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true
    OC_SRT="$(command -v srt || true)"
    [ -n "$OC_SRT" ] || {
        echo "ERROR: OpenCode requires Anthropic Sandbox Runtime: npm install -g @anthropic-ai/sandbox-runtime" >&2
        exit 1
    }
    OC_RUNTIME_DIR="$ROOT/.opencode"
    OC_SANDBOX_SETTINGS="$OC_RUNTIME_DIR/sandbox.json"
    OC_SANDBOX_EXEC="$OC_RUNTIME_DIR/opencode_sandbox_exec.sh"
    OC_SANDBOX_RUNNER="$OC_RUNTIME_DIR/opencode_sandbox_exec.mjs"
    OC_HELPER="$OC_RUNTIME_DIR/opencode_driver.py"
    OC_WRDS_SUPERVISOR="$OC_RUNTIME_DIR/wrds_srt_service.py"
    # These files are executed by the unsandboxed control plane or establish
    # its sandbox policy. Reject ancestor/leaf symlinks, special files, and
    # alternate hard-link aliases before opening any of them.
    _oc_protected_leaves=(
        "$OC_SANDBOX_SETTINGS" "$OC_SANDBOX_EXEC" "$OC_SANDBOX_RUNNER"
        "$OC_HELPER" "$ROOT/launch.sh" "$ROOT/opencode.json"
    )
    [ -e "$OC_WRDS_SUPERVISOR" ] && _oc_protected_leaves+=("$OC_WRDS_SUPERVISOR")
    python3 - "$OC_RUNTIME_DIR" "${_oc_protected_leaves[@]}" <<'PY'
import os, stat, sys

runtime, *leaves = sys.argv[1:]
try:
    runtime_stat = os.lstat(runtime)
    if stat.S_ISLNK(runtime_stat.st_mode) or not stat.S_ISDIR(runtime_stat.st_mode):
        raise ValueError(f"OpenCode runtime path is not a real directory: {runtime}")
    if os.path.realpath(runtime) != os.path.abspath(runtime):
        raise ValueError(f"OpenCode runtime path did not resolve in place: {runtime}")
    for path in leaves:
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise ValueError(f"OpenCode protected file is not a regular non-symlink: {path}")
        if info.st_nlink != 1:
            raise ValueError(f"OpenCode protected file has alternate hard links: {path}")
except (OSError, ValueError) as error:
    print(f"ERROR: {error} (refresh this deployment with update.sh)", file=sys.stderr)
    raise SystemExit(1)
PY
    [ -x "$OC_SANDBOX_EXEC" ] || {
        echo "ERROR: OpenCode sandbox handoff is not executable: $OC_SANDBOX_EXEC (refresh this deployment with update.sh)" >&2
        exit 1
    }
    OC_STATE="$ROOT/process_log/pipeline_state.json"
    if [ "$ONCE" != "1" ]; then
        python3 - "$OC_STATE" <<'PY' || {
import os, stat, sys
try:
    info = os.lstat(sys.argv[1])
except FileNotFoundError:
    raise SystemExit(1)
raise SystemExit(0 if stat.S_ISREG(info.st_mode) and info.st_nlink == 1 else 1)
PY
            echo "ERROR: pipeline_state.json must be one regular non-aliased file; use ./launch.sh opencode --once for manual/report work." >&2
            exit 1
        }
    fi
    OC_CONTROL_DIR="$ROOT/process_log/.opencode-control"
    OC_PROCESS_LOG="$ROOT/process_log"
    if [ -L "$OC_PROCESS_LOG" ] || { [ -e "$OC_PROCESS_LOG" ] && [ ! -d "$OC_PROCESS_LOG" ]; }; then
        echo "ERROR: OpenCode process_log must be a real directory: $OC_PROCESS_LOG" >&2
        exit 1
    fi
    mkdir -p "$OC_PROCESS_LOG"
    [ "$(cd "$OC_PROCESS_LOG" && pwd -P)" = "$OC_PROCESS_LOG" ] || {
        echo "ERROR: OpenCode process_log did not resolve inside the project: $OC_PROCESS_LOG" >&2
        exit 1
    }
    if [ -L "$OC_CONTROL_DIR" ]; then
        echo "ERROR: OpenCode control directory must not be a symlink: $OC_CONTROL_DIR" >&2
        exit 1
    fi
    (umask 077 && mkdir -p "$OC_CONTROL_DIR")
    [ "$(cd "$OC_CONTROL_DIR" && pwd -P)" = "$OC_CONTROL_DIR" ] || {
        echo "ERROR: OpenCode control directory did not resolve in place: $OC_CONTROL_DIR" >&2
        exit 1
    }
    oc_status() {
        python3 - "$OC_STATE" 2>/dev/null <<'PY' || echo "?"
import json, os, stat, sys
flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit(1)
with os.fdopen(fd, encoding="utf-8") as handle:
    print(json.load(handle).get("status", "?"))
PY
    }
    oc_state_hash() {
        python3 - "$OC_STATE" 2>/dev/null <<'PY' || echo "state-hash-failed"
import hashlib, os, stat, sys
flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit(1)
digest = hashlib.sha256()
with os.fdopen(fd, "rb") as handle:
    while chunk := handle.read(1024 * 1024):
        digest.update(chunk)
print(digest.hexdigest())
PY
    }
    oc_worktree_hash() {
        "$OC_CONTROL_PYTHON" -I - "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" \
            "$OC_CONTROL_PYTHON" "$OC_HELPER" "$ROOT" <<'PY'
import os, signal, subprocess, sys

command = [sys.argv[1], sys.argv[2], sys.argv[3], "-I", sys.argv[4],
           "worktree-hash", "--root", sys.argv[5], "--timeout", "10"]
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, start_new_session=True)
try:
    output, _ = process.communicate(timeout=20)
except subprocess.TimeoutExpired:
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
    print("worktree-hash-timeout")
    raise SystemExit(0)
if process.returncode == 0 and output.strip():
    print(output.strip())
else:
    print("worktree-hash-failed")
PY
    }
    OC_SID_CACHE="$OC_CONTROL_DIR/session_id"
    OC_LOG="$OC_CONTROL_DIR/driver.log"
    OC_SERVER_LOG="$OC_CONTROL_DIR/server.log"
    OC_SERVER_PID_FILE="$OC_CONTROL_DIR/server_pid"
    OC_SERVER_START_FILE="$OC_CONTROL_DIR/server_start"
    OC_SERVER_IDENTITY_FILE="$OC_CONTROL_DIR/server_identity"
    OC_SERVER_STARTING_FILE="$OC_CONTROL_DIR/server_starting"
    OC_SERVER_URL_FILE="$OC_CONTROL_DIR/server_url"
    OC_SERVER_PASSWORD_FILE="$OC_CONTROL_DIR/server_password"
    OC_WRDS_CONTROL_DIR="${HOME:?HOME must be set}/.local/state/zeropaper/opencode-control"
    OC_WRDS_SERVICE_LOG="$OC_WRDS_CONTROL_DIR/wrds_service.log"
    OC_WRDS_SERVICE_IDENTITY_FILE="$OC_WRDS_CONTROL_DIR/wrds_service_identity"
    OC_WRDS_SERVICE_STARTING_FILE="$OC_WRDS_CONTROL_DIR/wrds_service_starting"
    OC_WRDS_SERVICE_APPROVAL_FILE="$OC_WRDS_CONTROL_DIR/wrds_service_approval"
    OC_WRDS_GLOBAL_LOCK="$OC_WRDS_CONTROL_DIR/wrds_service_lock"
    OC_DRIVER_LOCK="$OC_CONTROL_DIR/driver_lock"
    OC_PENDING_CHILDREN_FILE="$OC_CONTROL_DIR/background_children"
    OC_PENDING_PARENT_FILE="$OC_CONTROL_DIR/background_parent"
    OC_BACKGROUND_BASELINE_FILE="$OC_CONTROL_DIR/background_baseline"
    OC_BACKGROUND_TRANSITION_FILE="$OC_CONTROL_DIR/background_transition"
    OC_RECOVERY_INTENT_FILE="$OC_CONTROL_DIR/recovery_intent"
    OC_PARENT_SERVER_EPOCH_FILE="$OC_CONTROL_DIR/parent_server_epoch"
    OC_UNRESOLVED_SESSION_FILE="$OC_CONTROL_DIR/unresolved_session"
    OC_LEGACY_UNCONFINED_FILE="$OC_CONTROL_DIR/legacy_unconfined"
    # v2.21 stored control state directly in process_log/. Migrate it before
    # starting any sandboxed process so update.sh cannot orphan/reuse an old
    # unconfined server or duplicate its parent session. Legacy state was
    # model-writable, so accept regular files only and let the normal identity,
    # PGID, command, and API checks validate their contents after the move.
    OC_LEGACY_SERVER_MIGRATED=0
    _oc_legacy_lock="$ROOT/process_log/.opencode_driver_lock"
    if [ -d "$_oc_legacy_lock" ] && [ ! -L "$_oc_legacy_lock" ]; then
        _oc_legacy_owner="$(python3 - "$_oc_legacy_lock" <<'PY'
import os, stat, sys

root = sys.argv[1]
names = set(os.listdir(root))
if names - {"pid", "start"}:
    raise SystemExit("unexpected legacy driver-lock entries")
values = []
for name in ("pid", "start"):
    path = os.path.join(root, name)
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags)
    except FileNotFoundError:
        values.append("")
        continue
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        os.close(fd)
        raise SystemExit("unsafe legacy driver-lock entry")
    with os.fdopen(fd, encoding="utf-8") as handle:
        values.append(handle.read().strip())
print("|".join(values))
PY
)" || { echo "ERROR: unsafe pre-v2.21 OpenCode driver lock" >&2; exit 1; }
        _oc_legacy_owner_pid="${_oc_legacy_owner%%|*}"
        _oc_legacy_owner_start="${_oc_legacy_owner#*|}"
        if [[ "$_oc_legacy_owner_pid" =~ ^[0-9]+$ ]] && \
           kill -0 "$_oc_legacy_owner_pid" 2>/dev/null && \
           [ "$(ps -o lstart= -p "$_oc_legacy_owner_pid" 2>/dev/null | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' || true)" = "$_oc_legacy_owner_start" ]; then
            echo "ERROR: a pre-v2.21 OpenCode driver is still running (pid=$_oc_legacy_owner_pid); stop it before launching the updated runtime" >&2
            exit 1
        fi
        rm -f "$_oc_legacy_lock/pid" "$_oc_legacy_lock/start"
        rmdir "$_oc_legacy_lock" || {
            echo "ERROR: cannot remove stale pre-v2.21 OpenCode driver lock" >&2
            exit 1
        }
    fi
    if { [ -e "$_oc_legacy_lock" ] || [ -L "$_oc_legacy_lock" ]; } && [ ! -d "$_oc_legacy_lock" ]; then
        [ -f "$_oc_legacy_lock" ] && [ ! -L "$_oc_legacy_lock" ] || {
            echo "ERROR: legacy OpenCode driver lock is not a regular file; inspect $_oc_legacy_lock" >&2
            exit 1
        }
        python3 - "$_oc_legacy_lock" <<'PY' || {
import os, sys
raise SystemExit(0 if os.lstat(sys.argv[1]).st_nlink == 1 else 1)
PY
            echo "ERROR: legacy OpenCode driver lock has alternate hard links: $_oc_legacy_lock" >&2
            exit 1
        }
        if ! python3 - "$_oc_legacy_lock" <<'PY'
import fcntl, os, sys
flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit(1)
finally:
    os.close(fd)
PY
        then
            echo "ERROR: a pre-v2.22 OpenCode driver is still running; stop it before launching the updated runtime" >&2
            exit 1
        fi
    fi
    _oc_legacy_pairs=(
        ".opencode_session_id|session_id"
        "opencode-driver.log|driver.log"
        "opencode-server.log|server.log"
        ".opencode_server_pid|server_pid"
        ".opencode_server_start|server_start"
        ".opencode_server_identity|server_identity"
        ".opencode_server_starting|server_starting"
        ".opencode_server_url|server_url"
        ".opencode_server_password|server_password"
        ".opencode_driver_lock|driver_lock"
        ".opencode_background_children|background_children"
        ".opencode_background_parent|background_parent"
        ".opencode_background_baseline|background_baseline"
        ".opencode_background_transition|background_transition"
        ".opencode_recovery_intent|recovery_intent"
        ".opencode_parent_server_epoch|parent_server_epoch"
        ".opencode_unresolved_session|unresolved_session"
    )
    for _oc_legacy_pair in "${_oc_legacy_pairs[@]}"; do
        _oc_legacy_name="${_oc_legacy_pair%%|*}"
        _oc_control_name="${_oc_legacy_pair#*|}"
        _oc_legacy_path="$ROOT/process_log/$_oc_legacy_name"
        _oc_control_path="$OC_CONTROL_DIR/$_oc_control_name"
        if [ -e "$_oc_legacy_path" ] || [ -L "$_oc_legacy_path" ]; then
            if [ "$_oc_control_name" = "driver_lock" ] && [ -d "$_oc_legacy_path" ] && [ ! -L "$_oc_legacy_path" ]; then
                : # pre-2.21 directory lock; oc_acquire_lock validates/reaps it
            else
                [ -f "$_oc_legacy_path" ] && [ ! -L "$_oc_legacy_path" ] || {
                    echo "ERROR: legacy OpenCode state is not a regular file: $_oc_legacy_path" >&2
                    exit 1
                }
                python3 - "$_oc_legacy_path" <<'PY' || {
import os, sys
raise SystemExit(0 if os.lstat(sys.argv[1]).st_nlink == 1 else 1)
PY
                    echo "ERROR: legacy OpenCode state has alternate hard links: $_oc_legacy_path" >&2
                    exit 1
                }
            fi
            [ ! -e "$_oc_control_path" ] || {
                echo "ERROR: both legacy and v2.22 OpenCode state exist for $_oc_control_name; inspect process_log" >&2
                exit 1
            }
            mv "$_oc_legacy_path" "$_oc_control_path"
            case "$_oc_control_name" in server_*) OC_LEGACY_SERVER_MIGRATED=1 ;; esac
        fi
    done
    if [ "$OC_LEGACY_SERVER_MIGRATED" = "1" ]; then
        python3 - "$OC_LEGACY_UNCONFINED_FILE" <<'PY'
import os, sys
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags, 0o600)
os.close(fd)
PY
    fi
    if [ -e "$OC_LEGACY_UNCONFINED_FILE" ]; then
        _oc_legacy_pid=""
        if [ -s "$OC_SERVER_IDENTITY_FILE" ]; then
            _oc_legacy_pid="$(python3 - "$OC_SERVER_IDENTITY_FILE" <<'PY'
import os, stat, sys
flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit(1)
with os.fdopen(fd, encoding="utf-8") as handle:
    print(handle.readline().strip())
PY
)" || { echo "ERROR: unsafe migrated OpenCode server identity" >&2; exit 1; }
        elif [ -s "$OC_SERVER_PID_FILE" ]; then
            _oc_legacy_pid="$(python3 - "$OC_SERVER_PID_FILE" <<'PY'
import os, stat, sys
flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(sys.argv[1], flags)
info = os.fstat(fd)
if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
    raise SystemExit(1)
with os.fdopen(fd, encoding="utf-8") as handle:
    print(handle.read().strip())
PY
)" || { echo "ERROR: unsafe migrated OpenCode server pid" >&2; exit 1; }
        fi
        if [[ "$_oc_legacy_pid" =~ ^[0-9]+$ ]] && \
           { kill -0 "$_oc_legacy_pid" 2>/dev/null || kill -0 -- "-$_oc_legacy_pid" 2>/dev/null; }; then
            echo "ERROR: a pre-v2.22 unconfined OpenCode server/process group is still alive (pid=$_oc_legacy_pid). Stop it before launching the updated runtime; no replacement was started." >&2
            exit 1
        fi
        rm -f "$OC_LEGACY_UNCONFINED_FILE"
    fi
    # A pre-v2.22 unconfined process could have planted control-path symlinks
    # before the policy existed. Once legacy liveness is ruled out, reject every
    # non-regular entry before the host driver opens logs/state. The one allowed
    # directory is the old pid/start lock format, validated by oc_acquire_lock.
    [ ! -L "$OC_CONTROL_DIR" ] && [ "$(cd "$OC_CONTROL_DIR" && pwd -P)" = "$OC_CONTROL_DIR" ] || {
        echo "ERROR: unsafe OpenCode control directory: $OC_CONTROL_DIR" >&2
        exit 1
    }
    for _oc_control_entry in "$OC_CONTROL_DIR"/* "$OC_CONTROL_DIR"/.[!.]* "$OC_CONTROL_DIR"/..?*; do
        [ -e "$_oc_control_entry" ] || [ -L "$_oc_control_entry" ] || continue
        if [ -L "$_oc_control_entry" ]; then
            echo "ERROR: symlink found in OpenCode control state: $_oc_control_entry" >&2
            exit 1
        fi
        if [ -d "$_oc_control_entry" ]; then
            [ "$(basename "$_oc_control_entry")" = "driver_lock" ] || {
                echo "ERROR: unexpected directory in OpenCode control state: $_oc_control_entry" >&2
                exit 1
            }
        elif [ ! -f "$_oc_control_entry" ]; then
            echo "ERROR: non-regular OpenCode control state: $_oc_control_entry" >&2
            exit 1
        elif ! python3 - "$_oc_control_entry" <<'PY'
import os, sys
raise SystemExit(0 if os.lstat(sys.argv[1]).st_nlink == 1 else 1)
PY
        then
            echo "ERROR: hard-linked OpenCode control state: $_oc_control_entry" >&2
            exit 1
        fi
    done
    OC_WRDS_SERVICE_PID=""
    OC_WRDS_SERVICE_START=""
    OC_WRDS_LOCK_KEEPER_PID=""
    oc_wrds_service_health() {
        [ -x "$ROOT/.venv/bin/python3" ] || return 1
        "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" \
            "$ROOT/.venv/bin/python3" -I -c \
            'import sys; sys.path.insert(0, "code"); from utils.wrds_client import wrds_bridge_ping, wrds_ping; raise SystemExit(0 if wrds_ping() and (not sys.platform.startswith("linux") or wrds_bridge_ping()) else 1)' \
            >/dev/null 2>&1
    }
    oc_wrds_service_group_alive() {
        [[ "$OC_WRDS_SERVICE_PID" =~ ^[0-9]+$ ]] && \
            kill -0 -- "-$OC_WRDS_SERVICE_PID" 2>/dev/null
    }
    oc_wrds_service_process_matches() {
        local now pgid command
        [[ "$OC_WRDS_SERVICE_PID" =~ ^[0-9]+$ ]] || return 1
        kill -0 "$OC_WRDS_SERVICE_PID" 2>/dev/null || return 1
        now="$(ps -o lstart= -p "$OC_WRDS_SERVICE_PID" 2>/dev/null || true)"
        [ -n "$OC_WRDS_SERVICE_START" ] && [ "$now" = "$OC_WRDS_SERVICE_START" ] || return 1
        pgid="$(ps -o pgid= -p "$OC_WRDS_SERVICE_PID" 2>/dev/null | tr -d ' ' || true)"
        [ "$pgid" = "$OC_WRDS_SERVICE_PID" ] || return 1
        command="$(ps -o command= -p "$OC_WRDS_SERVICE_PID" 2>/dev/null || true)"
        case "$command" in
            *wrds_srt_service.py*zeropaper-wrds-srt-service-v6*) return 0 ;;
            *) return 1 ;;
        esac
    }
    oc_wrds_service_load_identity() {
        [ -s "$OC_WRDS_SERVICE_IDENTITY_FILE" ] || return 1
        OC_WRDS_SERVICE_PID="$(sed -n '1p' "$OC_WRDS_SERVICE_IDENTITY_FILE")"
        OC_WRDS_SERVICE_START="$(sed -n '2p' "$OC_WRDS_SERVICE_IDENTITY_FILE")"
        oc_wrds_service_process_matches
    }
    oc_wrds_service_clear_dead_state() {
        rm -f "$OC_WRDS_SERVICE_IDENTITY_FILE" "$OC_WRDS_SERVICE_STARTING_FILE" \
            "$OC_WRDS_SERVICE_APPROVAL_FILE"
        OC_WRDS_SERVICE_PID=""
        OC_WRDS_SERVICE_START=""
    }
    oc_wrds_service_acquire_lock() {
        local ready attempt=0
        ready="$(mktemp "$OC_CONTROL_DIR/wrds-lock-ready.XXXXXX")"
        "$OC_CONTROL_PYTHON" -I "$OC_HELPER" lock-hold \
            --path "$OC_WRDS_GLOBAL_LOCK" --ready "$ready" --wait &
        OC_WRDS_LOCK_KEEPER_PID=$!
        while [ "$attempt" -lt 1500 ]; do
            attempt=$((attempt + 1))
            if [ -s "$ready" ]; then
                rm -f "$ready"
                return 0
            fi
            kill -0 "$OC_WRDS_LOCK_KEEPER_PID" 2>/dev/null || break
            sleep 0.1
        done
        rm -f "$ready"
        kill "$OC_WRDS_LOCK_KEEPER_PID" 2>/dev/null || true
        wait "$OC_WRDS_LOCK_KEEPER_PID" 2>/dev/null || true
        OC_WRDS_LOCK_KEEPER_PID=""
        echo "ERROR: timed out waiting for the host-wide OpenCode WRDS startup lock" >&2
        return 1
    }
    oc_wrds_service_release_lock() {
        [ -n "$OC_WRDS_LOCK_KEEPER_PID" ] || return 0
        kill "$OC_WRDS_LOCK_KEEPER_PID" 2>/dev/null || true
        wait "$OC_WRDS_LOCK_KEEPER_PID" 2>/dev/null || true
        OC_WRDS_LOCK_KEEPER_PID=""
    }
    oc_wrds_control_state_safe() {
        "$OC_CONTROL_PYTHON" -I - "$OC_WRDS_CONTROL_DIR" \
            "$OC_WRDS_SERVICE_LOG" "$OC_WRDS_SERVICE_IDENTITY_FILE" \
            "$OC_WRDS_SERVICE_STARTING_FILE" "$OC_WRDS_SERVICE_APPROVAL_FILE" \
            "$OC_WRDS_GLOBAL_LOCK" <<'PY'
import os, stat, sys

root, *leaves = sys.argv[1:]
info = os.lstat(root)
if (stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or
        os.path.realpath(root) != os.path.abspath(root) or
        (hasattr(os, "getuid") and info.st_uid != os.getuid()) or
        info.st_mode & 0o077):
    raise SystemExit(1)
for path in leaves:
    try:
        leaf = os.lstat(path)
    except FileNotFoundError:
        continue
    if (not stat.S_ISREG(leaf.st_mode) or leaf.st_nlink != 1 or
            (hasattr(os, "getuid") and leaf.st_uid != os.getuid())):
        raise SystemExit(1)
PY
    }
    oc_wrds_service_wait_healthy() {
        local attempt=0
        while [ "$attempt" -lt 1250 ]; do
            attempt=$((attempt + 1))
            if grep -q '^WRDS_SRT_SERVICE_READY$' "$OC_WRDS_SERVICE_LOG"; then
                if oc_wrds_service_health; then
                    echo "[opencode-driver] WRDS SRT service ready" | tee -a "$OC_LOG"
                    return 0
                fi
                echo "ERROR: WRDS SRT service reported ready but its endpoints are unreachable; preserving its identity" >&2
                return 1
            fi
            oc_wrds_service_process_matches || return 1
            sleep 0.1
        done
        echo "ERROR: WRDS SRT service is still starting; preserving its identity and login attempt" >&2
        return 1
    }
    oc_wrds_service_approve_pid_namespace() {
        local line inner_pid inner_start host_start inner_pgid
        line="$(sed -n 's/^WRDS_SRT_IDENTITY //p' "$OC_WRDS_SERVICE_LOG" | tail -1)"
        inner_pid="${line%% *}"
        inner_start="${line#* }"
        [[ "$inner_pid" =~ ^[0-9]+$ ]] || return 1
        [ -n "$inner_start" ] && [ "$inner_start" != "$line" ] || return 1
        host_start="$(ps -o lstart= -p "$inner_pid" 2>/dev/null | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' || true)"
        [ -n "$host_start" ] && [ "$host_start" = "$inner_start" ] || return 1
        inner_pgid="$(ps -o pgid= -p "$inner_pid" 2>/dev/null | tr -d ' ' || true)"
        [ "$inner_pgid" = "$OC_WRDS_SERVICE_PID" ] || return 1
        "$OC_CONTROL_PYTHON" -I - "$OC_WRDS_SERVICE_APPROVAL_FILE" <<'PY'
import os, stat, sys
path = sys.argv[1]
flags = os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
fd = os.open(path, flags)
info = os.fstat(fd)
if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or
        (hasattr(os, "getuid") and info.st_uid != os.getuid()) or
        info.st_mode & 0o077):
    os.close(fd)
    raise SystemExit(1)
os.ftruncate(fd, 0)
os.write(fd, b"approved\n")
os.fsync(fd)
os.close(fd)
PY
    }
    oc_wrds_service_start() {
        local identity_tmp approval_tmp starting_tmp attempt=0
        : > "$OC_WRDS_SERVICE_LOG"
        approval_tmp="$(mktemp "$OC_WRDS_CONTROL_DIR/wrds-service-approval.XXXXXX")"
        chmod 600 "$approval_tmp"
        mv "$approval_tmp" "$OC_WRDS_SERVICE_APPROVAL_FILE"
        starting_tmp="$(mktemp "$OC_WRDS_CONTROL_DIR/wrds-service-starting.XXXXXX")"
        printf 'pending\n' > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_WRDS_SERVICE_STARTING_FILE"
        {
            ZEROPAPER_OPENCODE_WRDS_SERVICE=1 \
            "$OC_CONTROL_PYTHON" -I -c \
                'import os,sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
                "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" \
                "$OC_CONTROL_PYTHON" -I .opencode/wrds_srt_service.py \
                zeropaper-wrds-srt-service-v6 "$OC_WRDS_SERVICE_APPROVAL_FILE" \
                </dev/null >> "$OC_WRDS_SERVICE_LOG" 2>&1 &
            OC_WRDS_SERVICE_PID=$!
        }
        starting_tmp="$(mktemp "$OC_WRDS_CONTROL_DIR/wrds-service-starting.XXXXXX")"
        printf '%s\n' "$OC_WRDS_SERVICE_PID" > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_WRDS_SERVICE_STARTING_FILE"
        OC_WRDS_SERVICE_START="$(ps -o lstart= -p "$OC_WRDS_SERVICE_PID" 2>/dev/null || true)"
        [ -n "$OC_WRDS_SERVICE_START" ] || {
            echo "ERROR: OpenCode WRDS SRT wrapper failed to start" >&2
            return 1
        }
        identity_tmp="$(mktemp "$OC_WRDS_CONTROL_DIR/wrds-service-identity.XXXXXX")"
        printf '%s\n%s\n' "$OC_WRDS_SERVICE_PID" "$OC_WRDS_SERVICE_START" > "$identity_tmp"
        chmod 600 "$identity_tmp"
        mv "$identity_tmp" "$OC_WRDS_SERVICE_IDENTITY_FILE"

        while [ "$attempt" -lt 150 ]; do
            attempt=$((attempt + 1))
            if grep -q '^WRDS_SRT_SERVICE_SKIPPED credentials-not-configured$' \
                    "$OC_WRDS_SERVICE_LOG"; then
                wait "$OC_WRDS_SERVICE_PID" 2>/dev/null || true
                oc_wrds_service_clear_dead_state
                return 10
            fi
            if grep -q '^WRDS_SRT_IDENTITY ' "$OC_WRDS_SERVICE_LOG"; then
                if ! oc_wrds_service_process_matches || \
                        ! oc_wrds_service_approve_pid_namespace; then
                    echo "ERROR: SRT hides WRDS service PIDs from the host; no login was attempted" >&2
                    return 1
                fi
                # The supervisor already holds this inode open. Unlink the
                # approved gate before it can become a replayable project path.
                rm -f "$OC_WRDS_SERVICE_APPROVAL_FILE"
                rm -f "$OC_WRDS_SERVICE_STARTING_FILE"
                return 0
            fi
            oc_wrds_service_process_matches || break
            sleep 0.1
        done
        if grep -q '^WRDS_SRT_SERVICE_SKIPPED credentials-not-configured$' \
                "$OC_WRDS_SERVICE_LOG"; then
            wait "$OC_WRDS_SERVICE_PID" 2>/dev/null || true
            oc_wrds_service_clear_dead_state
            return 10
        fi
        echo "ERROR: WRDS SRT service did not publish a host-visible identity; no login was approved" >&2
        return 1
    }
    oc_prepare_wrds_service_locked() {
        local starting_pid service_start_rc
        if oc_wrds_service_load_identity; then
            echo "[opencode-driver] joining existing WRDS SRT service startup" | tee -a "$OC_LOG"
            oc_wrds_service_wait_healthy
            return
        fi
        if [ -e "$OC_WRDS_SERVICE_STARTING_FILE" ]; then
            starting_pid="$(cat "$OC_WRDS_SERVICE_STARTING_FILE" 2>/dev/null || true)"
            if [[ "$starting_pid" =~ ^[0-9]+$ ]] && kill -0 "$starting_pid" 2>/dev/null; then
                echo "ERROR: an incompletely recorded WRDS SRT wrapper may still be alive; refusing replacement" >&2
                return 1
            fi
        fi
        if oc_wrds_service_group_alive; then
            echo "ERROR: WRDS SRT leader identity is stale but its process group remains; refusing replacement" >&2
            return 1
        fi
        oc_wrds_service_clear_dead_state
        echo "[opencode-driver] establishing host-wide WRDS inside Sandbox Runtime…" | tee -a "$OC_LOG"
        if oc_wrds_service_start; then
            :
        else
            service_start_rc=$?
            if [ "$service_start_rc" -eq 10 ]; then
                echo "[opencode-driver] WRDS credentials are not configured; skipping host service" | tee -a "$OC_LOG"
                return 0
            fi
            return 1
        fi
        oc_wrds_service_wait_healthy
    }

    oc_prepare_wrds_service() {
        local action prepare_rc
        action="$(project_services_action)"
        [ "$action" = "start" ] || return 0
        [ -x "$ROOT/.venv/bin/python3" ] || {
            echo "ERROR: OpenCode empirical service requires the project .venv" >&2
            return 1
        }
        # The fast path is lock-free. A missing/unhealthy endpoint enters one
        # host-wide lock, then rechecks so concurrent projects cannot create
        # duplicate privileged supervisors or cross-approve shared state.
        if oc_wrds_service_health; then
            echo "[opencode-driver] reusing host-wide WRDS service" | tee -a "$OC_LOG"
            return 0
        fi
        oc_wrds_control_state_safe || {
            echo "ERROR: unsafe host-wide OpenCode WRDS control state" >&2
            return 1
        }
        oc_wrds_service_acquire_lock || return 1
        if oc_wrds_service_health; then
            echo "[opencode-driver] reusing host-wide WRDS service after serialized startup" | tee -a "$OC_LOG"
            prepare_rc=0
        elif oc_prepare_wrds_service_locked; then
            prepare_rc=0
        else
            prepare_rc=$?
        fi
        oc_wrds_service_release_lock
        return "$prepare_rc"
    }

    oc_prepare_wrds_service

    if [ "$ONCE" = "1" ]; then
        "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" \
            opencode --model opencode/deepseek-v4-flash
        exit
    fi
    OPENCODE_TURN_TIMEOUT="${OPENCODE_TURN_TIMEOUT:-3540}"
    OPENCODE_BACKGROUND_TIMEOUT="${OPENCODE_BACKGROUND_TIMEOUT:-3540}"
    OPENCODE_ABORT_TIMEOUT="${OPENCODE_ABORT_TIMEOUT:-30}"
    OPENCODE_KILL_GRACE="${OPENCODE_KILL_GRACE:-10}"
    OPENCODE_LOOP_DELAY="${OPENCODE_LOOP_DELAY:-3}"
    OC_FIRST='Run the pipeline. You are unattended: never ask the user anything; decide from AGENTS.md and the pipeline artifacts. Use native .opencode task agents. When the task schema offers background, dispatch independent long-running agents with background=true and continue non-overlapping work; otherwise use foreground tasks. Every agent must checkpoint to its explicit artifact path.'
    OC_CONT='Continue the pipeline from process_log/pipeline_state.json. You are unattended: never ask the user anything. Use native .opencode task agents; use background=true for independent long-running work when the schema offers it, foreground otherwise. Reconcile completed child artifacts before advancing a gate, and keep working until this turn has made durable progress.'
    OC_RECOVER=' The OpenCode server was restarted, so any in-memory background jobs from its prior instance were interrupted. Inspect this session child history and the explicit artifact paths, then resume each unfinished child with its task_id or relaunch it exactly once. Exception: never resume or directly relaunch an unseeded Stage 0 literature-scout; return through the Stage 0 scan_charged resume guard so it commits a fresh physical-launch permit first or takes the no-scan cap route. Never mistake a missing completion notification for successful completion.'
    OC_CANCEL_RECOVER=' The prior turn or background wait timed out and its session tree was cancelled to confirmed quiescence. Inspect child transcripts and explicit artifact paths, then resume unfinished work with its task_id or relaunch it exactly once. Exception: never resume or directly relaunch an unseeded Stage 0 literature-scout; return through the Stage 0 scan_charged resume guard so it commits a fresh physical-launch permit first or takes the no-scan cap route.'
    OC_SERVER_PID=""
    OC_SERVER_START=""
    OC_SERVER_URL=""
    OPENCODE_SERVER_PASSWORD=""
    OC_LOCK_HELD=0
    OC_LOCK_KEEPER_PID=""
    OC_SERVER_REUSED=0
    OC_SERVER_STARTING=0
    oc_server_api() {
        python3 "$OC_HELPER" --url "$OC_SERVER_URL" "$@"
    }
    oc_server_process_matches() {
        local now pgid command
        [[ "$OC_SERVER_PID" =~ ^[0-9]+$ ]] || return 1
        kill -0 "$OC_SERVER_PID" 2>/dev/null || return 1
        now="$(ps -o lstart= -p "$OC_SERVER_PID" 2>/dev/null || true)"
        [ -n "$OC_SERVER_START" ] && [ "$now" = "$OC_SERVER_START" ] || return 1
        pgid="$(ps -o pgid= -p "$OC_SERVER_PID" 2>/dev/null | tr -d ' ' || true)"
        [ "$pgid" = "$OC_SERVER_PID" ] || return 1
        command="$(ps -o command= -p "$OC_SERVER_PID" 2>/dev/null || true)"
        case "$command" in *opencode*serve*) return 0 ;; *) return 1 ;; esac
    }
    oc_driver_owner_matches() {
        local pid="$1" start="$2" now
        [[ "$pid" =~ ^[0-9]+$ ]] || return 1
        kill -0 "$pid" 2>/dev/null || return 1
        now="$(ps -o lstart= -p "$pid" 2>/dev/null || true)"
        [ -n "$start" ] && [ "$now" = "$start" ]
    }
    oc_acquire_lock() {
        local owner_pid owner_start ready attempt
        # Migrate a stale directory-format lock from the pre-2.21 driver.
        if [ -d "$OC_DRIVER_LOCK" ]; then
            owner_pid="$(cat "$OC_DRIVER_LOCK/pid" 2>/dev/null || true)"
            owner_start="$(cat "$OC_DRIVER_LOCK/start" 2>/dev/null || true)"
            if oc_driver_owner_matches "$owner_pid" "$owner_start"; then
                echo "ERROR: another OpenCode driver owns this project (pid=$owner_pid)" >&2
                return 1
            fi
            rm -f "$OC_DRIVER_LOCK/pid" "$OC_DRIVER_LOCK/start"
            rmdir "$OC_DRIVER_LOCK" 2>/dev/null || { echo "ERROR: cannot recover stale OpenCode driver lock" >&2; return 1; }
        fi
        ready="$(mktemp "$OC_CONTROL_DIR/lock-ready.XXXXXX")"
        "$OC_CONTROL_PYTHON" -I "$OC_HELPER" lock-hold --path "$OC_DRIVER_LOCK" --ready "$ready" &
        OC_LOCK_KEEPER_PID=$!
        attempt=0
        while [ "$attempt" -lt 100 ]; do
            attempt=$((attempt + 1))
            if [ -s "$ready" ]; then
                rm -f "$ready"
                OC_LOCK_HELD=1
                return 0
            fi
            kill -0 "$OC_LOCK_KEEPER_PID" 2>/dev/null || break
            sleep 0.05
        done
        rm -f "$ready"
        wait "$OC_LOCK_KEEPER_PID" 2>/dev/null || true
        OC_LOCK_KEEPER_PID=""
        echo "ERROR: another OpenCode driver owns this project" >&2
        return 1
    }
    oc_release_lock() {
        [ "$OC_LOCK_HELD" = "1" ] || return 0
        kill "$OC_LOCK_KEEPER_PID" 2>/dev/null || true
        wait "$OC_LOCK_KEEPER_PID" 2>/dev/null || true
        OC_LOCK_KEEPER_PID=""
        OC_LOCK_HELD=0
    }
    oc_clear_server_state() {
        rm -f "$OC_SERVER_PID_FILE" "$OC_SERVER_START_FILE" "$OC_SERVER_URL_FILE" "$OC_SERVER_PASSWORD_FILE" \
            "$OC_SERVER_IDENTITY_FILE" "$OC_SERVER_STARTING_FILE" "$ROOT/process_log"/.opencode-server-password.* \
            "$ROOT/process_log"/.opencode-server-identity.*
        OC_SERVER_PID=""
        OC_SERVER_START=""
        OC_SERVER_URL=""
        OPENCODE_SERVER_PASSWORD=""
    }
    oc_server_group_alive() {
        [[ "$OC_SERVER_PID" =~ ^[0-9]+$ ]] && kill -0 -- "-$OC_SERVER_PID" 2>/dev/null
    }
    oc_wait_server_group_gone() { # $1 = absolute SECONDS deadline
        local deadline="$1"
        while oc_server_group_alive && [ "$SECONDS" -lt "$deadline" ]; do sleep 0.1; done
        ! oc_server_group_alive
    }
    oc_shutdown_authorized_group() { # $1 = diagnostic label
        local label="$1" deadline final_deadline
        kill -TERM -- "-$OC_SERVER_PID" 2>/dev/null || true
        deadline=$((SECONDS + OPENCODE_KILL_GRACE))
        oc_wait_server_group_gone "$deadline" || true
        if oc_server_group_alive; then kill -KILL -- "-$OC_SERVER_PID" 2>/dev/null || true; fi
        wait "$OC_SERVER_PID" 2>/dev/null || true
        final_deadline=$((SECONDS + 5))
        if ! oc_wait_server_group_gone "$final_deadline"; then
            echo "[opencode-driver] $label process group did not terminate; retaining identity and refusing replacement" | tee -a "$OC_LOG"
            return 1
        fi
    }
    oc_reap_starting_server() {
        local marker now pgid deadline
        [[ "$OC_SERVER_PID" =~ ^[0-9]+$ ]] || return 1
        marker="$(cat "$OC_SERVER_STARTING_FILE" 2>/dev/null || true)"
        [ "$marker" = "$OC_SERVER_PID" ] || return 1
        if kill -0 "$OC_SERVER_PID" 2>/dev/null && [ -n "$OC_SERVER_START" ]; then
            now="$(ps -o lstart= -p "$OC_SERVER_PID" 2>/dev/null || true)"
            [ "$now" = "$OC_SERVER_START" ] || return 1
        fi
        pgid="$(ps -o pgid= -p "$OC_SERVER_PID" 2>/dev/null | tr -d ' ' || true)"
        if [ "$pgid" = "$OC_SERVER_PID" ] || oc_server_group_alive; then
            oc_shutdown_authorized_group "starting server" || return 1
        elif kill -0 "$OC_SERVER_PID" 2>/dev/null; then
            # The setsid wrapper has not created its private group yet. Only
            # target the direct child PID, then re-check whether it became the
            # leader of its private group before escalating.
            kill -TERM "$OC_SERVER_PID" 2>/dev/null || true
            deadline=$((SECONDS + OPENCODE_KILL_GRACE))
            while kill -0 "$OC_SERVER_PID" 2>/dev/null && [ "$SECONDS" -lt "$deadline" ]; do
                pgid="$(ps -o pgid= -p "$OC_SERVER_PID" 2>/dev/null | tr -d ' ' || true)"
                [ "$pgid" = "$OC_SERVER_PID" ] && break
                sleep 0.1
            done
            if oc_server_group_alive; then
                oc_shutdown_authorized_group "starting server" || return 1
            elif kill -0 "$OC_SERVER_PID" 2>/dev/null; then
                # It is still the same direct child; never KILL a reused PID.
                if [ -n "$OC_SERVER_START" ]; then
                    now="$(ps -o lstart= -p "$OC_SERVER_PID" 2>/dev/null || true)"
                    [ "$now" = "$OC_SERVER_START" ] || return 1
                fi
                pgid="$(ps -o pgid= -p "$OC_SERVER_PID" 2>/dev/null | tr -d ' ' || true)"
                if [ "$pgid" = "$OC_SERVER_PID" ]; then
                    oc_shutdown_authorized_group "starting server" || return 1
                else
                    kill -KILL "$OC_SERVER_PID" 2>/dev/null || true
                    wait "$OC_SERVER_PID" 2>/dev/null || true
                    kill -0 "$OC_SERVER_PID" 2>/dev/null && return 1
                    # Catch a private group created immediately before leader exit.
                    oc_server_group_alive && oc_shutdown_authorized_group "starting server" || true
                    oc_server_group_alive && return 1
                fi
            else
                wait "$OC_SERVER_PID" 2>/dev/null || true
                if oc_server_group_alive; then
                    oc_shutdown_authorized_group "starting server" || return 1
                fi
            fi
        fi
        OC_SERVER_STARTING=0
        oc_clear_server_state
        return 0
    }
    oc_stop_server() {
        if oc_server_process_matches; then
            # Authorization happens once while PID/start/PGID/command all
            # match. From here on, signal only the authorized process group:
            # its PGID cannot be reused while any member remains alive.
            oc_shutdown_authorized_group "server" || return 1
        elif [ "$OC_SERVER_STARTING" = "1" ]; then
            oc_reap_starting_server || return 1
            return 0
        elif oc_server_group_alive; then
            # The leader is gone, so its start/command identity can no longer
            # be revalidated. Preserve the group and state for operator
            # inspection rather than signaling an unauthenticated target.
            echo "[opencode-driver] recorded server leader is gone but its process group remains; refusing unsafe replacement" | tee -a "$OC_LOG"
            return 1
        fi
        oc_clear_server_state
        return 0
    }
    oc_load_server_state() {
        local health_attempt
        if [ -s "$OC_SERVER_IDENTITY_FILE" ]; then
            OC_SERVER_PID="$(sed -n '1p' "$OC_SERVER_IDENTITY_FILE")"
            OC_SERVER_START="$(sed -n '2p' "$OC_SERVER_IDENTITY_FILE")"
        elif [ -s "$OC_SERVER_PID_FILE" ] && [ -s "$OC_SERVER_START_FILE" ]; then
            # Compatibility with a server cached by the initial v2.21 driver.
            OC_SERVER_PID="$(cat "$OC_SERVER_PID_FILE")"
            OC_SERVER_START="$(cat "$OC_SERVER_START_FILE")"
        else
            return 1
        fi
        [ -s "$OC_SERVER_URL_FILE" ] && [ -s "$OC_SERVER_PASSWORD_FILE" ] || return 1
        OC_SERVER_URL="$(cat "$OC_SERVER_URL_FILE")"
        OPENCODE_SERVER_PASSWORD="$(cat "$OC_SERVER_PASSWORD_FILE")"
        export OPENCODE_SERVER_PASSWORD
        oc_server_process_matches || return 1
        for health_attempt in 1 2 3; do
            oc_server_api health >/dev/null 2>&1 && return 0
            sleep 0.1
        done
        # Identity, credentials, and the exact process are all still valid.
        # A short API outage must not be converted into registry destruction.
        return 3
    }
    oc_start_server() {
        local attempt url password_tmp identity_tmp starting_tmp
        OPENCODE_SERVER_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
        export OPENCODE_SERVER_PASSWORD
        : > "$OC_SERVER_LOG"
        OC_SERVER_STARTING=1
        starting_tmp="$(mktemp "$OC_CONTROL_DIR/server-starting.XXXXXX")"
        printf '%s\n' pending > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_SERVER_STARTING_FILE"
        {
            "$OC_CONTROL_PYTHON" -I -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
                "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" \
                opencode serve --hostname 127.0.0.1 --port 0 \
                </dev/null >> "$OC_SERVER_LOG" 2>&1 &
            OC_SERVER_PID=$!
        }
        starting_tmp="$(mktemp "$OC_CONTROL_DIR/server-starting.XXXXXX")"
        printf '%s\n' "$OC_SERVER_PID" > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_SERVER_STARTING_FILE"
        OC_SERVER_START="$(ps -o lstart= -p "$OC_SERVER_PID" 2>/dev/null || true)"
        if [ -z "$OC_SERVER_START" ]; then
            oc_reap_starting_server || echo "ERROR: failed to reap incomplete OpenCode server; startup marker retained" >&2
            echo "ERROR: OpenCode server failed to start" >&2
            return 1
        fi
        identity_tmp="$(mktemp "$OC_CONTROL_DIR/server-identity.XXXXXX")"
        printf '%s\n%s\n' "$OC_SERVER_PID" "$OC_SERVER_START" > "$identity_tmp"
        chmod 600 "$identity_tmp"
        mv "$identity_tmp" "$OC_SERVER_IDENTITY_FILE"
        # Compatibility/observability mirrors; identity_file is authoritative.
        printf '%s\n' "$OC_SERVER_PID" > "$OC_SERVER_PID_FILE"
        printf '%s\n' "$OC_SERVER_START" > "$OC_SERVER_START_FILE"
        password_tmp="$(mktemp "$OC_CONTROL_DIR/server-password.XXXXXX")"
        printf '%s\n' "$OPENCODE_SERVER_PASSWORD" > "$password_tmp"
        chmod 600 "$password_tmp"
        mv "$password_tmp" "$OC_SERVER_PASSWORD_FILE"
        attempt=0
        while [ "$attempt" -lt 100 ]; do
            attempt=$((attempt + 1))
            url="$(sed -nE 's#.*(http://(127\.0\.0\.1|localhost):[0-9]+).*#\1#p' "$OC_SERVER_LOG" | tail -1)"
            if [ -n "$url" ]; then
                OC_SERVER_URL="$url"
                if oc_server_api health >/dev/null 2>&1; then
                    printf '%s\n' "$OC_SERVER_URL" > "$OC_SERVER_URL_FILE"
                    OC_SERVER_STARTING=0
                    rm -f "$OC_SERVER_STARTING_FILE"
                    echo "[opencode-driver] persistent server ready at $OC_SERVER_URL" | tee -a "$OC_LOG"
                    return 0
                fi
            fi
            kill -0 "$OC_SERVER_PID" 2>/dev/null || break
            sleep 0.1
        done
        tail -20 "$OC_SERVER_LOG" >&2 || true
        oc_stop_server || return 1
        echo "ERROR: OpenCode server did not become healthy" >&2
        return 1
    }
    oc_prepare_server() {
        local load_rc
        if oc_load_server_state; then
            load_rc=0
        else
            load_rc=$?
        fi
        if [ "$load_rc" = "0" ]; then
            rm -f "$OC_SERVER_STARTING_FILE"
            OC_SERVER_REUSED=1
            echo "[opencode-driver] reusing persistent server at $OC_SERVER_URL" | tee -a "$OC_LOG"
            return 0
        fi
        if [ "$load_rc" = "3" ]; then
            OC_SERVER_REUSED=1
            echo "[opencode-driver] exact cached server is alive but temporarily unhealthy; preserving it and failing closed" | tee -a "$OC_LOG"
            return 3
        fi
        if [ -e "$OC_SERVER_STARTING_FILE" ]; then
            OC_SERVER_PID="$(cat "$OC_SERVER_STARTING_FILE" 2>/dev/null || true)"
            if [[ "$OC_SERVER_PID" =~ ^[0-9]+$ ]] && ! kill -0 "$OC_SERVER_PID" 2>/dev/null && ! oc_server_group_alive; then
                rm -f "$OC_SERVER_STARTING_FILE"
                OC_SERVER_PID=""
            else
                echo "[opencode-driver] incomplete server startup may still be alive; retaining marker and refusing replacement" | tee -a "$OC_LOG"
                return 3
            fi
        fi
        # Kill only the exact process whose PID and start token we recorded;
        # never act on a reused PID or an unvalidated state file.
        if oc_server_process_matches || oc_server_group_alive; then
            oc_stop_server || return 1
        else
            oc_clear_server_state
        fi
        OC_SERVER_REUSED=0
        oc_start_server
    }
    oc_sid_exists() {
        local sessions_tmp rc
        sessions_tmp="$(mktemp "$OC_CONTROL_DIR/sessions.XXXXXX")"
        if ! oc_server_api list-local --root "$ROOT" > "$sessions_tmp" 2>/dev/null; then
            rm -f "$sessions_tmp"
            return 2
        fi
        if grep -qxF "$1" "$sessions_tmp"; then rc=0; else rc=1; fi
        rm -f "$sessions_tmp"
        return "$rc"
    }
    oc_reconcile_new_sid() { # $1 = newline-delimited local-session snapshot
        local before_file="$1" after_file candidate
        after_file="$(mktemp "$OC_CONTROL_DIR/sessions.XXXXXX")"
        if ! oc_server_api list-local --root "$ROOT" > "$after_file" 2>/dev/null; then
            rm -f "$after_file"
            return 1
        fi
        candidate="$(python3 - "$before_file" "$after_file" <<'PY'
import sys
before = {x.strip() for x in open(sys.argv[1]) if x.strip()}
after = [x.strip() for x in open(sys.argv[2]) if x.strip()]
new = [x for x in after if x not in before]
if len(new) != 1:
    raise SystemExit(1)
print(new[0])
PY
)" || { rm -f "$after_file"; return 1; }
        rm -f "$after_file"
        printf '%s\n' "$candidate"
    }
    oc_clear_pending_children() {
        rm -f "$OC_PENDING_CHILDREN_FILE" "$OC_PENDING_PARENT_FILE"
    }
    oc_clear_background_state() {
        oc_clear_pending_children
        rm -f "$OC_BACKGROUND_BASELINE_FILE" "$OC_BACKGROUND_TRANSITION_FILE" "$OC_RECOVERY_INTENT_FILE" \
            "$OC_PARENT_SERVER_EPOCH_FILE"
    }
    oc_mark_unresolved_session() {
        printf 'An OpenCode turn created or may have created a parent session whose ID could not be determined.\nReason: %s\nInspect sessions with ./launch.sh opencode --once, write the chosen ID to process_log/.opencode-control/session_id, then remove this marker.\n' \
            "$1" > "$OC_UNRESOLVED_SESSION_FILE"
        chmod 600 "$OC_UNRESOLVED_SESSION_FILE"
    }
    oc_mark_first_turn_in_progress() {
        local marker_tmp
        marker_tmp="$(mktemp "$OC_CONTROL_DIR/unresolved.XXXXXX")"
        printf 'An OpenCode first turn is in progress and may create a parent session.\nIf interrupted, inspect sessions with ./launch.sh opencode --once before removing this marker.\n' > "$marker_tmp"
        chmod 600 "$marker_tmp"
        mv "$marker_tmp" "$OC_UNRESOLVED_SESSION_FILE"
    }
    oc_cache_sid() {
        local sid_tmp
        sid_tmp="$(mktemp "$OC_CONTROL_DIR/session.XXXXXX")"
        printf '%s\n' "$OC_SID" > "$sid_tmp"
        chmod 600 "$sid_tmp"
        mv "$sid_tmp" "$OC_SID_CACHE"
        oc_set_parent_server_epoch || return 1
        rm -f "$OC_UNRESOLVED_SESSION_FILE"
    }
    oc_bind_pending_parent() {
        if [ -s "$OC_PENDING_CHILDREN_FILE" ] && \
                { [ ! -s "$OC_PENDING_PARENT_FILE" ] || [ "$(cat "$OC_PENDING_PARENT_FILE")" != "$OC_SID" ]; }; then
            oc_clear_pending_children
        fi
        printf '%s\n' "$OC_SID" > "$OC_PENDING_PARENT_FILE"
    }
    oc_background_after() {
        local parent epoch count extra current_epoch
        if [ ! -e "$OC_BACKGROUND_BASELINE_FILE" ]; then
            printf '0\n'
            return 0
        fi
        [ "$(wc -l < "$OC_BACKGROUND_BASELINE_FILE" | tr -d ' ')" = "1" ] || return 1
        IFS=' ' read -r parent epoch count extra < "$OC_BACKGROUND_BASELINE_FILE" || return 1
        current_epoch="$(oc_server_epoch)" || return 1
        [ -z "$extra" ] && [ "$parent" = "$OC_SID" ] && [ "$epoch" = "$current_epoch" ] && [[ "$count" =~ ^[0-9]+$ ]] || return 1
        printf '%s\n' "$count"
    }
    oc_server_epoch() {
        local start_sum
        [ -n "$OC_SERVER_PID" ] && [ -n "$OC_SERVER_START" ] || return 1
        start_sum="$(printf '%s' "$OC_SERVER_START" | cksum | awk '{print $1 ":" $2}')" || return 1
        printf '%s:%s\n' "$OC_SERVER_PID" "$start_sum"
    }
    oc_set_parent_server_epoch() {
        local epoch epoch_tmp
        epoch="$(oc_server_epoch)" || return 1
        epoch_tmp="$(mktemp "$OC_CONTROL_DIR/parent-epoch.XXXXXX")"
        printf '%s %s\n' "$OC_SID" "$epoch" > "$epoch_tmp"
        chmod 600 "$epoch_tmp"
        mv "$epoch_tmp" "$OC_PARENT_SERVER_EPOCH_FILE"
    }
    oc_parent_server_epoch_status() {
        local parent epoch extra current_epoch
        [ -e "$OC_PARENT_SERVER_EPOCH_FILE" ] || return 1
        [ "$(wc -l < "$OC_PARENT_SERVER_EPOCH_FILE" | tr -d ' ')" = "1" ] || return 2
        IFS=' ' read -r parent epoch extra < "$OC_PARENT_SERVER_EPOCH_FILE" || return 2
        [ -z "$extra" ] && [ "$parent" = "$OC_SID" ] && [ -n "$epoch" ] || return 2
        current_epoch="$(oc_server_epoch)" || return 2
        [ "$epoch" = "$current_epoch" ] && return 0
        return 3
    }
    oc_background_baseline_status() {
        local parent epoch count extra current_epoch
        [ -e "$OC_BACKGROUND_BASELINE_FILE" ] || return 1
        [ "$(wc -l < "$OC_BACKGROUND_BASELINE_FILE" | tr -d ' ')" = "1" ] || return 2
        IFS=' ' read -r parent epoch count extra < "$OC_BACKGROUND_BASELINE_FILE" || return 2
        if [ -n "$extra" ] || [ "$parent" != "$OC_SID" ] || [ -z "$epoch" ] || ! [[ "$count" =~ ^[0-9]+$ ]]; then
            return 2
        fi
        current_epoch="$(oc_server_epoch)" || return 2
        [ "$epoch" = "$current_epoch" ] && return 0
        return 3
    }
    oc_begin_background_transition() { # $1 = restart or cancel
        local transition_tmp kind="$1"
        case "$kind" in restart|cancel) ;; *) return 1 ;; esac
        transition_tmp="$(mktemp "$OC_CONTROL_DIR/transition.XXXXXX")"
        printf '%s %s\n' "$OC_SID" "$kind" > "$transition_tmp"
        chmod 600 "$transition_tmp"
        mv "$transition_tmp" "$OC_BACKGROUND_TRANSITION_FILE"
    }
    oc_set_background_baseline() {
        local count epoch baseline_tmp
        count="$(oc_server_api cursor --session "$OC_SID" 2>/dev/null)" || return 1
        [[ "$count" =~ ^[0-9]+$ ]] || return 1
        epoch="$(oc_server_epoch)" || return 1
        baseline_tmp="$(mktemp "$OC_CONTROL_DIR/baseline.XXXXXX")"
        printf '%s %s %s\n' "$OC_SID" "$epoch" "$count" > "$baseline_tmp"
        chmod 600 "$baseline_tmp"
        mv "$baseline_tmp" "$OC_BACKGROUND_BASELINE_FILE"
        oc_clear_pending_children
    }
    oc_set_recovery_intent() { # $1 = restart or cancel
        local kind="$1" token intent_tmp
        case "$kind" in restart|cancel) ;; *) return 1 ;; esac
        token="zp-recovery-$(python3 -c 'import secrets; print(secrets.token_hex(16))')" || return 1
        intent_tmp="$(mktemp "$OC_CONTROL_DIR/recovery.XXXXXX")"
        printf '%s %s %s\n' "$OC_SID" "$kind" "$token" > "$intent_tmp"
        chmod 600 "$intent_tmp"
        mv "$intent_tmp" "$OC_RECOVERY_INTENT_FILE"
    }
    oc_finish_background_transition() { # $1 = restart or cancel
        local kind="$1"
        oc_set_background_baseline || return 1
        oc_set_parent_server_epoch || return 1
        oc_set_recovery_intent "$kind" || return 1
        rm -f "$OC_BACKGROUND_TRANSITION_FILE"
    }
    oc_recovery_note_from_intent() {
        local parent kind token extra rc
        [ -e "$OC_RECOVERY_INTENT_FILE" ] || return 0
        [ "$(wc -l < "$OC_RECOVERY_INTENT_FILE" | tr -d ' ')" = "1" ] || return 1
        IFS=' ' read -r parent kind token extra < "$OC_RECOVERY_INTENT_FILE" || return 1
        [ -z "$extra" ] && [ "$parent" = "$OC_SID" ] && [ -n "$token" ] || return 1
        case "$kind" in restart|cancel) ;; *) return 1 ;; esac
        if oc_server_api has-text --session "$OC_SID" --needle "$token" >/dev/null 2>&1; then
            rm -f "$OC_RECOVERY_INTENT_FILE"
            return 0
        else
            rc=$?
        fi
        [ "$rc" = "3" ] || return 1
        if [ "$kind" = "cancel" ]; then
            printf '%s Recovery intent token: %s.' "$OC_CANCEL_RECOVER" "$token"
        else
            printf '%s Recovery intent token: %s.' "$OC_RECOVER" "$token"
        fi
    }
    oc_ack_recovery_intent() {
        local parent kind token extra rc
        [ -e "$OC_RECOVERY_INTENT_FILE" ] || return 0
        [ "$(wc -l < "$OC_RECOVERY_INTENT_FILE" | tr -d ' ')" = "1" ] || return 1
        IFS=' ' read -r parent kind token extra < "$OC_RECOVERY_INTENT_FILE" || return 1
        [ -z "$extra" ] && [ "$parent" = "$OC_SID" ] && [ -n "$token" ] || return 1
        if oc_server_api has-text --session "$OC_SID" --needle "$token" >/dev/null 2>&1; then
            rm -f "$OC_RECOVERY_INTENT_FILE"
            return 0
        else
            rc=$?
        fi
        [ "$rc" = "3" ] && return 1
        return 1
    }
    oc_refresh_pending_children() {
        local pending_tmp after
        after="$(oc_background_after)" || return 1
        pending_tmp="$(mktemp "$OC_CONTROL_DIR/pending.XXXXXX")"
        if ! oc_server_api pending --session "$OC_SID" --after "$after" > "$pending_tmp" 2>/dev/null; then
            rm -f "$pending_tmp"
            return 1
        fi
        oc_bind_pending_parent
        if [ -s "$pending_tmp" ]; then
            chmod 600 "$pending_tmp"
            mv "$pending_tmp" "$OC_PENDING_CHILDREN_FILE"
        else
            rm -f "$pending_tmp" "$OC_PENDING_CHILDREN_FILE"
        fi
    }
    oc_wait_for_quiescence() {
        local generation after rc=0 args=()
        after="$(oc_background_after)" || return 2
        if [ -s "$OC_PENDING_CHILDREN_FILE" ]; then
            while IFS= read -r generation; do [ -n "$generation" ] && args+=(--generation "$generation"); done < "$OC_PENDING_CHILDREN_FILE"
            oc_server_api wait-idle --session "$OC_SID" --timeout "$OPENCODE_BACKGROUND_TIMEOUT" \
                --poll 0.5 --stable-samples 2 --after "$after" "${args[@]}" >> "$OC_LOG" 2>&1 || rc=$?
        else
            oc_server_api wait-idle --session "$OC_SID" --timeout "$OPENCODE_BACKGROUND_TIMEOUT" \
                --poll 0.5 --stable-samples 2 --after "$after" >> "$OC_LOG" 2>&1 || rc=$?
        fi
        if [ "$rc" = "0" ]; then
            oc_clear_pending_children
            return 0
        fi
        return "$rc"
    }
    oc_abort_tree_and_wait() {
        local failed=0
        oc_begin_background_transition cancel || return 1
        oc_server_api abort-tree --session "$OC_SID" >> "$OC_LOG" 2>&1 || failed=1
        oc_server_api wait-idle --session "$OC_SID" --timeout "$OPENCODE_ABORT_TIMEOUT" \
            --poll 0.2 --stable-samples 2 --status-only >> "$OC_LOG" 2>&1 || failed=1
        if [ "$failed" = "0" ]; then
            # Killing the server instance is the hard edge of cancellation:
            # no delayed notification or parent autowake from its process-local
            # registry can cross the new history baseline.
            oc_stop_server || return 1
            OC_SERVER_REUSED=0
            oc_start_server || return 1
            oc_sid_exists "$OC_SID" || {
                echo "[opencode-driver] cancelled parent is unavailable after server replacement; refusing to resume" | tee -a "$OC_LOG"
                return 1
            }
            oc_finish_background_transition cancel || {
                echo "[opencode-driver] cancellation settled but its recovery epoch/intent could not be persisted; refusing to resume" | tee -a "$OC_LOG"
                return 1
            }
            return 0
        fi
        echo "[opencode-driver] cancellation did not reach confirmed quiescence; refusing to resume" | tee -a "$OC_LOG"
        return 1
    }
    OC_ACTIVE_PGID=""
    OC_WATCHDOG_PID=""
    oc_kill_turn_group() { # $1 = TERM or KILL
        [ -n "$OC_ACTIVE_PGID" ] || return 0
        if kill -0 -- "-$OC_ACTIVE_PGID" 2>/dev/null; then
            kill -"$1" -- "-$OC_ACTIVE_PGID" 2>/dev/null || true
        else
            # The Python wrapper may not have completed setsid yet. Its PID is
            # unreaped and therefore identity-stable; signal that direct child
            # so it cannot detach after cleanup has already checked the group.
            kill -"$1" "$OC_ACTIVE_PGID" 2>/dev/null || true
        fi
    }
    oc_turn_group_alive() {
        [ -n "$OC_ACTIVE_PGID" ] && {
            kill -0 -- "-$OC_ACTIVE_PGID" 2>/dev/null \
                || kill -0 "$OC_ACTIVE_PGID" 2>/dev/null
        }
    }
    oc_turn_cleanup() {
        if [ -n "$OC_WATCHDOG_PID" ]; then
            kill "$OC_WATCHDOG_PID" 2>/dev/null || true
            wait "$OC_WATCHDOG_PID" 2>/dev/null || true
        fi
        if oc_turn_group_alive; then
            oc_kill_turn_group TERM
            sleep "$OPENCODE_KILL_GRACE"
            oc_kill_turn_group KILL
        fi
    }
    oc_signal_cleanup() {
        oc_turn_cleanup
        if [ -n "${OC_SID:-}" ]; then oc_server_api abort-tree --session "$OC_SID" >/dev/null 2>&1 || true; fi
        oc_stop_server || true
        oc_release_lock
    }
    oc_exit_cleanup() {
        oc_turn_cleanup
        if [ "$OC_SERVER_STARTING" = "1" ]; then
            oc_reap_starting_server || true
        fi
        oc_release_lock
    }
    trap oc_exit_cleanup EXIT
    oc_exit_signal() {
        local exit_code="$1"
        # Cleanup includes bounded waits and API shutdown. Coalesce a second or
        # mixed terminal/disconnect signal so it cannot re-enter this function
        # and exit before the detached turn/server groups are gone.
        trap '' HUP INT QUIT TERM
        oc_signal_cleanup
        trap - EXIT
        exit "$exit_code"
    }
    trap 'oc_exit_signal 130' INT
    trap 'oc_exit_signal 143' TERM
    trap 'oc_exit_signal 129' HUP
    trap 'oc_exit_signal 131' QUIT
    oc_acquire_lock
    if [ -s "$OC_UNRESOLVED_SESSION_FILE" ]; then
        echo "ERROR: unresolved OpenCode parent session; inspect $OC_UNRESOLVED_SESSION_FILE before launching again" >&2
        exit 1
    fi
    oc_prepare_server
    run_opencode_turn() {
        local oc_pid oc_start oc_now watchdog_pid rc timeout_marker="${oc_events}.timeout"
        # Capture to a regular file, then replay into the durable log after the
        # turn. Avoid process substitution here: restricted shells can reject
        # writes through /dev/fd even when the project itself is writable.
        # The attached CLI gets its own process group, separate from the server
        # and its native background jobs. A turn timeout can therefore reap a
        # wedged client without destroying unrelated children or autowake.
        "$OC_CONTROL_PYTHON" -I -c 'import os,signal,sys; signal.signal(signal.SIGINT, signal.SIG_DFL); signal.signal(signal.SIGQUIT, signal.SIG_DFL); signal.signal(signal.SIGTERM, signal.SIG_DFL); os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
            "$@" </dev/null > "$oc_events" 2>&1 &
        oc_pid=$!
        OC_ACTIVE_PGID="$oc_pid"
        oc_start="$(ps -o lstart= -p "$oc_pid" 2>/dev/null || true)"
        (
            sleep "$OPENCODE_TURN_TIMEOUT"
            oc_now="$(ps -o lstart= -p "$oc_pid" 2>/dev/null || true)"
            # ps may be unavailable inside a restricted parent sandbox. In
            # that case kill -0 still gives the watchdog a usable liveness
            # check; when ps works, lstart additionally protects against reuse.
            if kill -0 "$oc_pid" 2>/dev/null && { [ -z "$oc_start" ] || [ -z "$oc_now" ] || [ "$oc_now" = "$oc_start" ]; }; then
                : > "$timeout_marker"
                echo "[opencode-driver] turn exceeded OPENCODE_TURN_TIMEOUT=${OPENCODE_TURN_TIMEOUT}s; terminating and resuming" | tee -a "$OC_LOG"
                oc_kill_turn_group TERM
                sleep "$OPENCODE_KILL_GRACE"
                if oc_turn_group_alive; then
                    oc_kill_turn_group KILL
                fi
            fi
        ) &
        watchdog_pid=$!
        OC_WATCHDOG_PID="$watchdog_pid"
        wait "$oc_pid"
        rc=$?
        if [ -f "$timeout_marker" ]; then
            # The watchdog has already sent TERM. Let its configured grace
            # period expire before it kills descendants that are checkpointing.
            wait "$watchdog_pid" 2>/dev/null || true
        else
            kill "$watchdog_pid" 2>/dev/null || true
            wait "$watchdog_pid" 2>/dev/null || true
            # A normally exiting attached client should have no descendants.
            if oc_turn_group_alive; then
                oc_kill_turn_group TERM
                sleep "$OPENCODE_KILL_GRACE"
                oc_kill_turn_group KILL
            fi
        fi
        OC_WATCHDOG_PID=""
        OC_ACTIVE_PGID=""
        tee -a "$OC_LOG" < "$oc_events"
        return "$rc"
    }
    OC_SID=""
    if [ -s "$OC_SID_CACHE" ]; then
        _cached_oc_sid="$(cat "$OC_SID_CACHE")"
        if oc_sid_exists "$_cached_oc_sid"; then
            OC_SID="$_cached_oc_sid"
        else
            oc_sid_rc=$?
            if [ "$oc_sid_rc" = "2" ]; then
                echo "[opencode-driver] cannot validate the cached session through the live server; refusing to create a duplicate parent" | tee -a "$OC_LOG"
                exit 1
            fi
            echo "[opencode-driver] cached session is stale; starting a fresh session" | tee -a "$OC_LOG"
            rm -f "$OC_SID_CACHE"
            oc_clear_background_state
        fi
    fi
    oc_turn=0
    oc_no_progress=0
    oc_fast_any=0
    oc_recovery_note=""
    oc_parent_epoch_missing=0
    if [ -n "$OC_SID" ] && [ -e "$OC_BACKGROUND_TRANSITION_FILE" ]; then
        [ "$(wc -l < "$OC_BACKGROUND_TRANSITION_FILE" | tr -d ' ')" = "1" ] || {
            echo "[opencode-driver] malformed background transition; refusing recovery" | tee -a "$OC_LOG"
            exit 1
        }
        IFS=' ' read -r oc_transition_parent oc_transition_kind oc_transition_extra < "$OC_BACKGROUND_TRANSITION_FILE" || true
        if [ -n "${oc_transition_extra:-}" ] || [ "${oc_transition_parent:-}" != "$OC_SID" ]; then
            echo "[opencode-driver] background transition belongs to an unexpected parent; refusing recovery" | tee -a "$OC_LOG"
            exit 1
        fi
        case "${oc_transition_kind:-}" in
            cancel)
                # Re-abort idempotently, replace the server, and finish the epoch.
                oc_abort_tree_and_wait || exit 1
                ;;
            restart)
                oc_finish_background_transition restart || exit 1
                ;;
            *) echo "[opencode-driver] malformed background transition; refusing recovery" | tee -a "$OC_LOG"; exit 1 ;;
        esac
    fi
    if [ -n "$OC_SID" ]; then
        if oc_parent_server_epoch_status; then
            oc_parent_epoch_rc=0
        else
            oc_parent_epoch_rc=$?
        fi
        case "$oc_parent_epoch_rc" in
            0) ;;
            1)
                if [ "$OC_SERVER_REUSED" = "1" ]; then
                    # Migration/manual quarantine repair on the exact live
                    # server: reconstruct from history zero and quiesce before
                    # adopting the epoch. Do not retire possibly-live work.
                    oc_parent_epoch_missing=1
                    rm -f "$OC_BACKGROUND_BASELINE_FILE"
                    oc_clear_pending_children
                else
                    oc_begin_background_transition restart || exit 1
                    oc_finish_background_transition restart || exit 1
                fi
                ;;
            3)
                # A mismatch proves that process-local work belonged to a
                # different server instance and requires durable recovery.
                oc_begin_background_transition restart || exit 1
                oc_finish_background_transition restart || exit 1
                ;;
            *) echo "[opencode-driver] malformed parent/server epoch; refusing recovery" | tee -a "$OC_LOG"; exit 1 ;;
        esac
    fi
    if [ -n "$OC_SID" ] && [ "$OC_SERVER_REUSED" = "1" ]; then
        if [ -e "$OC_BACKGROUND_BASELINE_FILE" ]; then
            set +e
            oc_background_baseline_status
            oc_baseline_rc=$?
            set -e
            if [ "$oc_baseline_rc" = "3" ]; then
                # The server identity was committed before this driver's epoch
                # update. Since registries are process-local, pre-instance launches
                # cannot notify here; retire them before sending recovery work.
                oc_begin_background_transition restart || exit 1
                oc_finish_background_transition restart || exit 1
            elif [ "$oc_baseline_rc" != "0" ]; then
                echo "[opencode-driver] malformed background history baseline; refusing recovery" | tee -a "$OC_LOG"
                exit 1
            fi
        fi
        if ! oc_refresh_pending_children; then
            oc_prepare_server
            if [ "$OC_SERVER_REUSED" = "1" ]; then
                echo "[opencode-driver] transient API failure while reconstructing background work; refusing to prompt the live session" | tee -a "$OC_LOG"
                exit 1
            fi
            oc_begin_background_transition restart || exit 1
            oc_finish_background_transition restart || exit 1
        fi
        # A previous driver may have exited while the parent itself was still
        # producing an autowake response, even when no child remains in the
        # reconstructed ledger. Never overlap that work with a new prompt.
        set +e
        oc_wait_for_quiescence
        oc_pending_rc=$?
        set -e
        if [ "$oc_pending_rc" = "3" ]; then
            oc_abort_tree_and_wait || exit 1
        elif [ "$oc_pending_rc" != "0" ]; then
            oc_prepare_server
            if [ "$OC_SERVER_REUSED" = "1" ]; then
                echo "[opencode-driver] transient API failure while awaiting existing session work; refusing to prompt the live session" | tee -a "$OC_LOG"
                exit 1
            fi
            oc_begin_background_transition restart || exit 1
            oc_finish_background_transition restart || exit 1
        fi
        if [ "$oc_parent_epoch_missing" = "1" ] && [ ! -e "$OC_PARENT_SERVER_EPOCH_FILE" ]; then
            # The full history-zero barrier passed. Publish its current cursor
            # before adopting this server; a crash between the two safely
            # repeats history-zero reconstruction on the next launch.
            oc_set_background_baseline || exit 1
            oc_set_parent_server_epoch || exit 1
        fi
    fi
    oc_recovery_note="$(oc_recovery_note_from_intent)" || {
        echo "[opencode-driver] cannot reconcile durable recovery intent; refusing to prompt" | tee -a "$OC_LOG"
        exit 1
    }
    while :; do
        oc_st="$(oc_status)"
        case "$oc_st" in
            complete|complete_pending_verification)
                echo "[opencode-driver] pipeline $oc_st after $oc_turn turn(s)" | tee -a "$OC_LOG"; oc_stop_server || exit 1; exit 0 ;;
            halted_*)
                echo "[opencode-driver] pipeline halted: $oc_st" | tee -a "$OC_LOG"; oc_stop_server || exit 1; exit 0 ;;
            '?') echo "[opencode-driver] cannot read $OC_STATE" | tee -a "$OC_LOG"; exit 1 ;;
        esac
        oc_turn=$((oc_turn + 1))
        if [ "$oc_turn" -gt "${MAX_TURNS:-300}" ]; then
            echo "[opencode-driver] MAX_TURNS reached (status=$oc_st)" | tee -a "$OC_LOG"; exit 1
        fi
        oc_events="$(mktemp "$OC_CONTROL_DIR/events.XXXXXX")"
        oc_sessions_before=""
        oc_sessions_before_valid=0
        if [ -z "$OC_SID" ]; then
            oc_sessions_before="$(mktemp "$OC_CONTROL_DIR/sessions.XXXXXX")"
            if oc_server_api list-local --root "$ROOT" > "$oc_sessions_before" 2>/dev/null; then
                oc_sessions_before_valid=1
            fi
        fi
        oc_before="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true):$(oc_worktree_hash):$(oc_state_hash)"
        oc_t0=$SECONDS
        oc_event_sid_rc=0
        set +e
        if [ -n "$OC_SID" ]; then
            run_opencode_turn "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" opencode run --attach "$OC_SERVER_URL" --session "$OC_SID" --model opencode/deepseek-v4-flash --format json "$OC_CONT$oc_recovery_note"
            oc_rc=$?
        else
            oc_mark_first_turn_in_progress
            run_opencode_turn "$OC_SANDBOX_EXEC" "$OC_SANDBOX_SETTINGS" opencode run --attach "$OC_SERVER_URL" --model opencode/deepseek-v4-flash --format json "$OC_FIRST$oc_recovery_note"
            oc_rc=$?
            OC_SID="$(python3 -c 'import json,sys
ids=[]
for line in open(sys.argv[1]):
    try: event=json.loads(line)
    except Exception: continue
    if not isinstance(event, dict): continue
    for key in ("sessionID", "sessionId"):
        if key not in event: continue
        sid=event[key]
        if not isinstance(sid, str) or not sid: raise SystemExit(2)
        ids.append(sid)
if not ids: raise SystemExit(1)
if len(set(ids)) != 1: raise SystemExit(2)
print(ids[0])' "$oc_events")"
            oc_event_sid_rc=$?
            if [ "$oc_event_sid_rc" = "0" ]; then
                if oc_sid_exists "$OC_SID"; then
                    oc_clear_background_state
                    if ! oc_cache_sid; then
                        OC_SID=""
                        oc_event_sid_rc=2
                    fi
                else
                    OC_SID=""
                    oc_event_sid_rc=2
                fi
            fi
        fi
        set -e
        if [ -n "$oc_recovery_note" ] && oc_server_api health >/dev/null 2>&1; then
            oc_ack_recovery_intent || {
                echo "[opencode-driver] recovery prompt is not observable in the parent transcript; refusing to continue" | tee -a "$OC_LOG"
                rm -f "$oc_events" "${oc_events}.timeout"
                exit 1
            }
        fi
        oc_recovery_note=""
        oc_timed_out=0
        [ -f "${oc_events}.timeout" ] && oc_timed_out=1
        oc_substantive_tool_completed=0
        if python3 -c 'import json,sys
for line in open(sys.argv[1]):
    try: event=json.loads(line)
    except Exception: continue
    part=event.get("part") or {}
    state=part.get("state") or {}
    if event.get("type") == "tool_use" and part.get("tool") in {"task", "bash", "skill", "websearch", "webfetch"} and state.get("status") == "completed":
        raise SystemExit(0)
raise SystemExit(1)' "$oc_events"; then
            oc_substantive_tool_completed=1
        fi
        if [ "$oc_event_sid_rc" = "2" ]; then
            [ -n "$oc_sessions_before" ] && rm -f "$oc_sessions_before"
            oc_mark_unresolved_session "first-turn events contained an invalid, conflicting, or non-local session ID"
            echo "[opencode-driver] first-turn session ID failed validation; refusing reconciliation" | tee -a "$OC_LOG"
            rm -f "$oc_events" "${oc_events}.timeout"
            exit 1
        fi
        if [ -z "$OC_SID" ] && [ "$oc_sessions_before_valid" = "1" ]; then
            OC_SID="$(oc_reconcile_new_sid "$oc_sessions_before" || true)"
            if [ -n "$OC_SID" ]; then
                oc_clear_background_state
                oc_cache_sid
            fi
        fi
        [ -n "$oc_sessions_before" ] && rm -f "$oc_sessions_before"
        if [ "$oc_timed_out" = "1" ]; then
            if [ -z "$OC_SID" ]; then
                echo "[opencode-driver] timed-out first turn returned no session id; cannot resume" | tee -a "$OC_LOG"
                oc_mark_unresolved_session "timed-out first turn had no event ID and no unique session-list reconciliation"
                rm -f "$oc_events" "${oc_events}.timeout"
                # With no session handle there is nothing a later invocation
                # can safely resume or inspect. Do not strand the otherwise
                # reusable server (and any unaddressable work) on this path.
                oc_stop_server || exit 1
                exit 1
            fi
            oc_abort_tree_and_wait || { rm -f "$oc_events" "${oc_events}.timeout"; exit 1; }
            oc_recovery_note="$(oc_recovery_note_from_intent)" || exit 1
            rm -f "$oc_events" "${oc_events}.timeout"
            sleep "$OPENCODE_LOOP_DELAY"
            continue
        fi
        if [ "$oc_rc" -ne 0 ]; then
            rm -f "$oc_events" "${oc_events}.timeout"
            if [ -z "$OC_SID" ]; then
                oc_mark_unresolved_session "failed first turn returned no session ID"
                echo "[opencode-driver] failed first turn has no resolvable session ID; refusing automatic recovery" | tee -a "$OC_LOG"
                exit "$oc_rc"
            fi
            if ! oc_server_api health >/dev/null 2>&1; then
                echo "[opencode-driver] server disappeared; restarting and reconciling child sessions" | tee -a "$OC_LOG"
                oc_prepare_server
                if [ "$OC_SERVER_REUSED" = "1" ]; then
                    echo "[opencode-driver] server recovered but the attached turn failed; leaving it running without an automatic retry" | tee -a "$OC_LOG"
                    exit "$oc_rc"
                fi
                oc_begin_background_transition restart || exit 1
                oc_finish_background_transition restart || exit 1
                oc_recovery_note="$(oc_recovery_note_from_intent)" || exit 1
                sleep "$OPENCODE_LOOP_DELAY"
                continue
            fi
            echo "[opencode-driver] turn failed (exit $oc_rc); server left running for inspection/resume" | tee -a "$OC_LOG"
            exit "$oc_rc"
        fi
        if [ -z "$OC_SID" ]; then
            oc_mark_unresolved_session "successful first turn returned no event ID and no unique session-list reconciliation"
            echo "[opencode-driver] no session id returned; unresolved marker written" | tee -a "$OC_LOG"
            exit 1
        fi
        # Native background completions inject a synthetic user message and
        # autowake the parent inside the persistent server. Wait for both the
        # parent and all leaf children to be stably idle before an external
        # continuation, preventing a race with that internal parent turn.
        set +e
        oc_wait_for_quiescence
        oc_wait_rc=$?
        set -e
        if [ "$oc_wait_rc" = "3" ]; then
            echo "[opencode-driver] background/session tree exceeded OPENCODE_BACKGROUND_TIMEOUT=${OPENCODE_BACKGROUND_TIMEOUT}s; aborting busy sessions" | tee -a "$OC_LOG"
            oc_abort_tree_and_wait || exit 1
            oc_recovery_note="$(oc_recovery_note_from_intent)" || exit 1
        elif [ "$oc_wait_rc" != "0" ]; then
            echo "[opencode-driver] server disappeared while awaiting background work; restarting and reconciling" | tee -a "$OC_LOG"
            oc_prepare_server
            if [ "$OC_SERVER_REUSED" = "1" ]; then
                echo "[opencode-driver] server recovered after a transient API failure; refusing to prompt until a later inspected resume" | tee -a "$OC_LOG"
                exit 1
            fi
            oc_begin_background_transition restart || exit 1
            oc_finish_background_transition restart || exit 1
            oc_recovery_note="$(oc_recovery_note_from_intent)" || exit 1
        fi
        rm -f "$oc_events" "${oc_events}.timeout"
        oc_after="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true):$(oc_worktree_hash):$(oc_state_hash)"
        oc_dt=$((SECONDS - oc_t0))
        if [ "$oc_dt" -lt 60 ]; then
            oc_fast_any=$((oc_fast_any + 1))
        else
            oc_fast_any=0
        fi
        if [ "$oc_after" = "$oc_before" ] && [ "$oc_substantive_tool_completed" = "0" ] && [ "$oc_dt" -lt 60 ]; then
            oc_no_progress=$((oc_no_progress + 1))
        else
            oc_no_progress=0
        fi
        if [ "$oc_no_progress" -ge "${NO_PROGRESS_CEILING:-5}" ]; then
            echo "[opencode-driver] ${NO_PROGRESS_CEILING:-5} fast turns without repository progress or completed substantive tool work; stopping to bound cost" | tee -a "$OC_LOG"
            exit 1
        fi
        if [ "$oc_fast_any" -ge "${FAST_TURN_CEILING:-60}" ]; then
            echo "[opencode-driver] ${FAST_TURN_CEILING:-60} consecutive fast turns; stopping abnormal churn" | tee -a "$OC_LOG"
            exit 1
        fi
        sleep "$OPENCODE_LOOP_DELAY"
    done
fi

# ── codex ───────────────────────────────────────────────────────────────────
# Sandbox posture: a named permission profile mirrors the Claude deploy (open
# egress and broad ~/.cache compatibility) while carving the WRDS compatibility
# guard back to read-only. Legacy writable_roots cannot express that narrower
# exception. $ROOT/.git is a separate workspace root because Codex otherwise
# makes each workspace's top-level .git read-only and `git commit` dies on
# index.lock. The profile is expressed as -c keys because exec resume accepts
# them on every turn.
codex_permission_profile_args "$ROOT" true
CODEX_ARGS=(
    --skip-git-repo-check
    -c 'approval_policy="never"'
    # Keep the parent on the one native-agent schema the runtime instructions
    # use. This defeats an ordinary user `[agents] enabled=false` in --once and
    # keeps --light Luna on V2; each child role later pins V2 and V1 off in its
    # own SessionFlags layer and therefore remains a leaf.
    -c 'features.multi_agent_v2=true'
    "${CODEX_PERMISSION_PROFILE_ARGS[@]}"
)
# Headless sessions ignore user config so a legacy global sandbox_mode cannot
# silently select the old broad-root system over this more-specific profile.
# Authentication and session storage still use CODEX_HOME.
CODEX_EXEC_ONLY_ARGS=(--ignore-user-config)

# --ignore-user-config intentionally drops ambient trust state. Native custom
# roles are project-scoped, so restore trust for exactly this physical project
# on the command line; without it Codex silently omits `.codex/agents/` and an
# `agent_type=scorer` dispatch fails as unknown. The shared encoder handles the
# JSON/TOML DEL difference and fails loudly on unrepresentable path bytes.
_codex_trusted_root="$(codex_toml_basic_string "$ROOT")" || exit 1
CODEX_ARGS+=(-c "projects={${_codex_trusted_root}={trust_level=\"trusted\"}}")

# --light: pin the orchestrator to the same tier the subagents were assembled
# on (see light_orchestrator_model above). Config form, not --model, because
# `codex exec resume` accepts only -c — and the driver resumes on every turn
# after the first, so a flag-form pin would silently apply to turn 1 alone.
_light_model="$(light_orchestrator_model "$ROOT/.codex/agents")"
if [ -n "$_light_model" ]; then
    CODEX_ARGS+=(-c "model=\"$_light_model\"")
    echo "[launch] --light: orchestrator pinned to $_light_model" >&2
fi

# Proxy-auth version floor (issue #213): preserve the dedicated diagnostic even
# though the permission-profile floor is now newer than the affected clients.
codex_proxy_auth_preflight

if [ "$ONCE" = "1" ]; then
    codex "${CODEX_ARGS[@]}"
    exit
fi

STATE="$ROOT/process_log/pipeline_state.json"
if [ ! -f "$STATE" ]; then
    echo "ERROR: no process_log/pipeline_state.json — this looks like a --manual (toolkit) deployment." >&2
    echo "       The driver loop only applies to the autonomous pipeline; use: ./launch.sh codex --once" >&2
    exit 1
fi

status() {
    python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status","?"))' "$STATE" 2>/dev/null || echo "?"
}

# Session discovery, two tiers. Tier 1: a project-local cache written the
# first time a session is found/created — survives driver restarts, immune to
# other codex sessions on the host, and validated against the rollout store
# (rollout filenames embed the session id) so a pruned session can't be
# resumed blindly. Tier 2: scan recent rollout JSONLs
# (~/.codex/sessions/Y/M/D/) for one whose recorded cwd is this project —
# only needed on first adoption or if the cache is lost.
# (process_log/ existence is guaranteed: the driver hard-exits above when
# process_log/pipeline_state.json is missing.)
SID_CACHE="$ROOT/process_log/.codex_session_id"
CODEX_STATE_HOME="${CODEX_HOME:-$HOME/.codex}"

sid_exists() {
    /usr/bin/python3 -I - "$CODEX_STATE_HOME" "$1" <<'PY'
from pathlib import Path
import sys

state_home, sid = Path(sys.argv[1]), sys.argv[2]
try:
    found = any(
        path.name.endswith(f"-{sid}.jsonl")
        for path in state_home.glob("sessions/*/*/*/rollout-*.jsonl")
    )
except OSError:
    found = False
raise SystemExit(0 if found else 1)
PY
}

find_sid() {
    local sid
    if [ -s "$SID_CACHE" ]; then
        sid="$(cat "$SID_CACHE")"
        if sid_exists "$sid"; then echo "$sid"; return 0; fi
    fi
    # Parse metadata instead of matching its serialized JSON: cwd may contain
    # quotes, backslashes, or controls, and CODEX_HOME may contain whitespace.
    /usr/bin/python3 -I - "$CODEX_STATE_HOME" "$ROOT" <<'PY'
import json
from pathlib import Path
import sys

state_home, root = Path(sys.argv[1]), sys.argv[2]
candidates = []
for path in state_home.glob("sessions/*/*/*/rollout-*.jsonl"):
    try:
        candidates.append((path.stat().st_mtime_ns, path))
    except OSError:
        pass
for _, path in sorted(candidates, key=lambda item: item[0], reverse=True)[:50]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.loads(handle.readline(1 << 20)).get("payload", {})
    except (OSError, UnicodeError, json.JSONDecodeError):
        continue
    if payload.get("cwd") == root:
        sid = payload.get("session_id") or payload.get("id")
        if isinstance(sid, str) and sid:
            print(sid)
            raise SystemExit(0)
raise SystemExit(1)
PY
}

FIRST_PROMPT='Run the pipeline. You are running unattended — never stop to ask the user anything; make every decision from the pipeline documents.'
CONT_PROMPT='Continue the pipeline from process_log/pipeline_state.json. You are running unattended — never stop to ask the user anything. If the prior turn was aborted or interrupted, reconcile the current stage against its required artifacts and git status. A task-owned uncommitted diff is incomplete even when its file exists: re-launch its owning agent to rewrite or repair it, validate it, and then follow the current stage exact commit/routing sequence. Keep every native subagent cohort inside one parent turn: spawn, wait to terminal status, validate its artifact, preserve the stage-defined commit boundary, then and only then finish the turn.'
if [ -f "$ROOT/code/utils/start_services.sh" ]; then
    _service_notice=' The launcher has confirmed that the shared WRDS connection is up. Treat any earlier sandbox-network outage as stale and use the shipped WRDS client normally.'
    FIRST_PROMPT+="$_service_notice"
    CONT_PROMPT+="$_service_notice"
fi

LOG="$ROOT/process_log/driver.log"
MAX_TURNS="${MAX_TURNS:-300}"
# Per-turn wall-clock cap (the "ping codex every 59 minutes" guarantee): a
# turn still running at the cap is killed and the session resumed on the next
# loop iteration. This bounds the damage of a hung turn or native child. The
# in-process children are interrupted with their parent, so recovery relies on
# the pipeline's durable state/artifact protocol: a routed child output has a
# stage-defined durable commit boundary, while task-owned uncommitted diffs are
# retried rather than accepted after resume. 59 min, not 60 — the
# user-visible promise is "the session is re-prompted at least hourly".
TURN_TIMEOUT="${TURN_TIMEOUT:-3540}"
case "$TURN_TIMEOUT" in
    ''|*[!0-9]*|0)
        echo "ERROR: TURN_TIMEOUT must be a positive integer (got '$TURN_TIMEOUT')" >&2
        exit 2
        ;;
esac

# Run one codex turn with the watchdog. Args: the full codex command. A tiny
# Python exec shim creates a new process group and a same-group anchor.
# The anchor prevents PGID reuse and remains until the watcher removes the
# group after every normal, failed, timed-out, or parent-aborted turn. A first
# stop occurs before setpgid(), while the wrapper is still covered by the outer
# runtime guardian; only after this parent arms the watcher may the wrapper
# create the nested group. A second stop lets the parent verify that boundary
# before any Codex-controlled code starts. This gives timeout cleanup a stable
# identity for the complete turn cohort (including tool-command descendants)
# without signaling the driver or relying on a non-portable setsid(1) binary.
run_turn() {
    local cpid wpid rc cpg cstate wpg attempt
    /usr/bin/python3 -I -c '
import os, signal, sys
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_DFL)
# Phase 1: no escaped process group exists until the Bash parent has armed its
# watcher. If that parent dies here, the outer launch guardian owns this pid.
os.kill(os.getpid(), signal.SIGSTOP)
os.setpgid(0, 0)
anchor = os.fork()
if anchor == 0:
    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
        signal.signal(signum, signal.SIG_IGN)
    while True:
        signal.pause()
# Phase 2: publish a verifiable, anchor-backed PGID before agent-controlled
# code. The watcher is already armed and contains this group plus discovered
# descendant-owned tool groups if the parent dies.
os.kill(os.getpid(), signal.SIGSTOP)
os.execvp(sys.argv[1], sys.argv[1:])
' "$@" </dev/null > >(tee -a "$LOG") 2>&1 &
    cpid=$!
    attempt=0; cpg=""; cstate=""
    while [ "$attempt" -lt 200 ]; do
        attempt=$((attempt + 1))
        cpg="$(/bin/ps -o pgid= -p "$cpid" 2>/dev/null | tr -d ' ')"
        cstate="$(/bin/ps -o stat= -p "$cpid" 2>/dev/null | tr -d ' ')"
        case "$cstate" in *T*) break ;; esac
        kill -0 "$cpid" 2>/dev/null || break
        sleep 0.01
    done
    case "$cstate" in *T*) ;; *)
        kill -KILL "$cpid" 2>/dev/null || true
        kill -CONT "$cpid" 2>/dev/null || true
        wait "$cpid" 2>/dev/null || true
        echo "[driver] ERROR: could not establish the Codex turn pre-group guard" | tee -a "$LOG"
        return 75
        ;;
    esac
    if [ "$cpg" = "$cpid" ]; then
        kill -KILL -- "-$cpid" 2>/dev/null || kill -KILL "$cpid" 2>/dev/null || true
        kill -CONT -- "-$cpid" 2>/dev/null || kill -CONT "$cpid" 2>/dev/null || true
        wait "$cpid" 2>/dev/null || true
        echo "[driver] ERROR: Codex turn escaped before its watcher was armed" | tee -a "$LOG"
        return 75
    fi
    # The watchdog reads a private control/liveness pipe whose only writer is
    # this parent and which the already-started Codex/tee processes never
    # inherited. The parent sends one post-group arm byte, then only closes it.
    # EOF means the parent died or finished waiting, so the watcher cleans the
    # anchored group rather than signaling a bare PID. While the pipe is open,
    # this Bash is alive until this function closes it. EOF always removes the
    # anchor-backed group: after an ordinary Codex exit that is normal residual
    # cleanup; after a driver crash it is orphan recovery. Thus no numeric PID/start-time
    # identity guess and no parent-side cleanup window is involved.
    exec 6> >(/usr/bin/python3 -I -c '
import errno, fcntl, os, select, signal, stat, subprocess, sys
pid, timeout, root = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
# Escape the outer runtime group: its independent guardian uses SIGKILL after
# visible-supervisor death, while this watcher must survive long enough to
# observe parent-pipe EOF and reap the nested turn group. This trusted process
# has no descendants and exits on EOF or after the bounded timeout path.
lock_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
if not stat.S_ISDIR(os.fstat(lock_fd).st_mode):
    raise SystemExit(75)
# Acquire before publishing the isolated watcher PGID. The visible launcher
# still holds LOCK_SH, so an updater cannot win this handoff. This independent
# shared lock remains through nested-group teardown even if SIGKILL destroys
# the visible supervisor and the original runtime guardian.
fcntl.flock(lock_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
os.setpgid(0, 0)
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_IGN)

def fail_closed(message):
    print(f"[driver] ERROR: {message}; holding the project lock", flush=True)
    while True:
        select.select([], [], [], 3600)

def process_table():
    try:
        result = subprocess.run(
            ["/bin/ps", "-axo", "pid=,ppid=,pgid=,stat="],
            check=True, capture_output=True, text=True, timeout=5,
        )
    except Exception as exc:
        fail_closed(f"cannot inspect the Codex descendant tree: {exc}")
    rows = {}
    for line in result.stdout.splitlines():
        fields = line.split(None, 3)
        if len(fields) != 4:
            continue
        try:
            proc_pid, ppid, pgid = map(int, fields[:3])
        except ValueError:
            continue
        rows[proc_pid] = (ppid, pgid, fields[3])
    return rows

def turn_members(rows):
    # Include every root-group anchor/member, close over descendants, and adopt
    # only process groups whose leader is itself in that descendant closure.
    # This captures Codex setsid() tool groups without expanding through a
    # trusted process-substitution `tee` that remains in the outer runtime group.
    candidates = {proc_pid for proc_pid, (_, pgid, _) in rows.items()
                  if proc_pid == pid or pgid == pid}
    owned_groups = {pid}
    while True:
        descendants = candidates | {
            proc_pid for proc_pid, (ppid, pgid, _) in rows.items()
            if ppid in candidates
        }
        groups = owned_groups | {
            pgid for proc_pid, (_, pgid, _) in rows.items()
            if proc_pid in descendants and pgid in descendants
        }
        expanded = descendants | {
            proc_pid for proc_pid, (_, pgid, _) in rows.items()
            if pgid in groups
        }
        if expanded == candidates and groups == owned_groups:
            managed = {proc_pid for proc_pid in candidates
                       if proc_pid in rows and rows[proc_pid][1] in owned_groups}
            return managed, owned_groups
        candidates, owned_groups = expanded, groups

def freeze_turn_tree():
    try:
        os.killpg(pid, signal.SIGSTOP)
    except ProcessLookupError:
        return {}, set()
    previous = None
    while True:
        rows = process_table()
        members, _ = turn_members(rows)
        live = {proc_pid for proc_pid in members
                if proc_pid in rows and not rows[proc_pid][2].startswith("Z")}
        groups = {rows[proc_pid][1] for proc_pid in live}
        unsafe_groups = {group for group in groups
                         if group <= 1 or group == os.getpgrp()}
        if unsafe_groups:
            details = {proc_pid: rows[proc_pid] for proc_pid in live}
            fail_closed(f"unsafe groups {sorted(unsafe_groups)} in descendant tree {details}")
        # Stop groups first to close fork races, then each observed member.
        for group in groups:
            try:
                os.killpg(group, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        for proc_pid in live:
            try:
                os.kill(proc_pid, signal.SIGSTOP)
            except ProcessLookupError:
                pass
        select.select([], [], [], 0.02)
        check_rows = process_table()
        check_members, _ = turn_members(check_rows)
        signature = frozenset(
            (proc_pid, check_rows[proc_pid][0], check_rows[proc_pid][1])
            for proc_pid in check_members
            if proc_pid in check_rows and
               not check_rows[proc_pid][2].startswith("Z")
        )
        if signature == previous:
            return check_rows, {item[0] for item in signature}
        previous = signature

def bind_identities(rows, members):
    bindings = []
    kqueue = None
    for proc_pid in members:
        if proc_pid not in rows or rows[proc_pid][2].startswith("Z"):
            continue
        if hasattr(os, "pidfd_open"):
            try:
                bindings.append(("pidfd", os.pidfd_open(proc_pid), proc_pid))
            except ProcessLookupError:
                continue
            except OSError:
                # Older kernels/seccomp can reject pidfd_open even when this
                # Python exposes it; fall through to the bound /proc handle.
                pass
            else:
                continue
        if sys.platform.startswith("linux"):
            try:
                proc_fd = os.open(f"/proc/{proc_pid}",
                                  os.O_RDONLY | os.O_DIRECTORY |
                                  getattr(os, "O_NOFOLLOW", 0))
            except ProcessLookupError:
                continue
            except OSError as exc:
                fail_closed(f"cannot bind descendant {proc_pid}: {exc}")
            else:
                bindings.append(("procfd", proc_fd, proc_pid))
        elif hasattr(select, "kqueue"):
            if kqueue is None:
                kqueue = select.kqueue()
            try:
                event = select.kevent(proc_pid, filter=select.KQ_FILTER_PROC,
                                      flags=select.KQ_EV_ADD,
                                      fflags=select.KQ_NOTE_EXIT)
                kqueue.control([event], 0, 0)
            except ProcessLookupError:
                continue
            except OSError as exc:
                if exc.errno == errno.ESRCH:
                    continue
                fail_closed(f"cannot bind descendant {proc_pid}: {exc}")
            else:
                bindings.append(("kqueue", kqueue, proc_pid))
        else:
            fail_closed("no kernel-bound process identity API is available")
    return bindings

def wait_identities(bindings):
    pending = list(bindings)
    while pending:
        next_pending = []
        kqueue_seen = {}
        for kind, handle, proc_pid in pending:
            if kind == "pidfd":
                if not select.select([handle], [], [], 0)[0]:
                    next_pending.append((kind, handle, proc_pid))
            elif kind == "procfd":
                try:
                    stat_fd = os.open("stat", os.O_RDONLY, dir_fd=handle)
                except OSError:
                    pass
                else:
                    os.close(stat_fd)
                    next_pending.append((kind, handle, proc_pid))
            else:
                exited = kqueue_seen.get(handle)
                if exited is None:
                    exited = {event.ident for event in handle.control(None, 1024, 0)}
                    kqueue_seen[handle] = exited
                if proc_pid not in exited:
                    next_pending.append((kind, handle, proc_pid))
        pending = next_pending
        if pending:
            select.select([], [], [], 0.02)
    for kind, handle, _ in bindings:
        if kind in {"pidfd", "procfd"}:
            os.close(handle)

def terminate_turn_tree():
    rows, members = freeze_turn_tree()
    if not members:
        return
    bindings = bind_identities(rows, members)
    # Only a successfully bound live member may pin a discovered numeric PGID.
    # The root PGID is separately safe because its persistent anchor is the
    # identity from which this snapshot was taken.
    bound_pids = {proc_pid for _, _, proc_pid in bindings}
    groups = {pid}
    groups.update(rows[proc_pid][1] for proc_pid in bound_pids
                  if proc_pid in rows and not rows[proc_pid][2].startswith("Z"))
    for group in groups:
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    # Kernel-bound identities keep LOCK_SH until every stopped writer has
    # actually exited. D-state descendants intentionally hold recovery closed.
    wait_identities(bindings)

def parent_closed(delay):
    ready, _, _ = select.select([0], [], [], delay)
    if not ready:
        return False
    os.read(0, 1)  # EOF (the one arm byte was consumed before this function)
    return True

def wait_until_armed():
    # The timeout clock starts only after Bash has verified the nested,
    # anchor-backed group. Before then EOF means the parent/outer guardian owns
    # any still-outer wrapper; if the transition already occurred, the tree
    # terminator removes it. No Codex-controlled code has started yet.
    while True:
        ready, _, _ = select.select([0], [], [])
        if not ready:
            continue
        data = os.read(0, 1)
        if not data:
            terminate_turn_tree()
            raise SystemExit(0)
        if data == b"G":
            return

wait_until_armed()
if parent_closed(timeout):
    terminate_turn_tree()
    raise SystemExit(0)
message = (f"[driver] turn exceeded TURN_TIMEOUT={timeout}s — "
           "stopping the bound descendant tree and resuming from durable state")
print(message, flush=True)
terminate_turn_tree()
' "$cpid" "$TURN_TIMEOUT" "$ROOT")
    wpid=$!
    # Do not release the turn wrapper from its outer-group stop until the
    # watcher has demonstrably escaped that group. Otherwise a visible-launcher
    # SIGKILL in this small arm window could remove the only process capable of
    # reaping the soon-to-be nested turn group.
    attempt=0; wpg=""
    while [ "$attempt" -lt 200 ]; do
        attempt=$((attempt + 1))
        wpg="$(/bin/ps -o pgid= -p "$wpid" 2>/dev/null | tr -d ' ')"
        [ "$wpg" = "$wpid" ] && break
        kill -0 "$wpid" 2>/dev/null || break
        sleep 0.01
    done
    if [ "$wpg" != "$wpid" ]; then
        exec 6>&-
        kill -KILL "$cpid" 2>/dev/null || true
        kill -CONT "$cpid" 2>/dev/null || true
        wait "$wpid" 2>/dev/null || true
        wait "$cpid" 2>/dev/null || true
        echo "[driver] ERROR: could not establish isolated Codex turn watcher" | tee -a "$LOG"
        return 75
    fi
    # Allow the wrapper to create its group and anchor, then require its second
    # stop before any Codex code is allowed to run.
    kill -CONT "$cpid" 2>/dev/null || true
    attempt=0; cpg=""; cstate=""
    while [ "$attempt" -lt 200 ]; do
        attempt=$((attempt + 1))
        cpg="$(/bin/ps -o pgid= -p "$cpid" 2>/dev/null | tr -d ' ')"
        cstate="$(/bin/ps -o stat= -p "$cpid" 2>/dev/null | tr -d ' ')"
        if [ "$cpg" = "$cpid" ]; then
            case "$cstate" in *T*) break ;; esac
        fi
        kill -0 "$cpid" 2>/dev/null || break
        sleep 0.01
    done
    case "$cstate" in *T*) ;; *) cpg="" ;; esac
    if [ "$cpg" != "$cpid" ]; then
        exec 6>&-
        kill -KILL -- "-$cpid" 2>/dev/null || kill -KILL "$cpid" 2>/dev/null || true
        kill -CONT -- "-$cpid" 2>/dev/null || kill -CONT "$cpid" 2>/dev/null || true
        # Reap the group leader before joining the watcher: its group-gone
        # proof deliberately includes zombies and would otherwise wait on the
        # very child this Bash still owns.
        wait "$cpid" 2>/dev/null || true
        wait "$wpid" 2>/dev/null || true
        echo "[driver] ERROR: could not establish anchored Codex turn process group" | tee -a "$LOG"
        return 75
    fi
    # Publish the verified identity transition before any Codex-controlled
    # code runs. This also starts the watcher wall clock; setup time cannot
    # consume a tiny TURN_TIMEOUT and leave the released turn unwatched.
    printf G >&6
    kill -CONT -- "-$cpid" 2>/dev/null || kill -CONT "$cpid" 2>/dev/null || true
    wait "$cpid"
    rc=$?
    exec 6>&-
    wait "$wpid" 2>/dev/null
    return "$rc"
}

turn=0
fast_nocommit=0
fast_any=0
SID="$(find_sid || true)"
if [ -n "$SID" ]; then
    echo "[driver] resuming existing session $SID" | tee -a "$LOG"
    printf '%s\n' "$SID" > "$SID_CACHE"
fi

# Rotate the driver log past 10MB: it accumulates each turn's full codex
# output, and an orchestrator that ever dumps the log mid-turn would compound
# it (the dump is itself tee'd back in). One rotation generation is enough.
rotate_log() {
    if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt 10485760 ]; then
        # || true: a failed mv (disk full, permissions) must degrade to
        # "log keeps growing", not kill the driver under set -e.
        mv "$LOG" "$LOG.1" 2>/dev/null || true
        echo "[driver] rotated driver.log (>10MB) to driver.log.1" | tee -a "$LOG"
    fi
}

while :; do
    rotate_log
    st="$(status)"
    case "$st" in
        complete)
            echo "[driver] pipeline COMPLETE after $turn driver turn(s)" | tee -a "$LOG"; exit 0 ;;
        complete_pending_verification)
            # Terminal for the driver: the paper is finished, but a binding
            # verification is still owed because its source was rate/budget
            # limited (see docs/core_bypass.md). Re-prompting cannot help —
            # the source resets on its own clock — so stop rather than burn
            # turns, and say loudly what is outstanding.
            echo "[driver] pipeline COMPLETE *PENDING VERIFICATION* after $turn driver turn(s)" | tee -a "$LOG"
            echo "[driver] A binding verification was never run — the paper is NOT fully verified." | tee -a "$LOG"
            python3 -c 'import json,sys
try:
    p=json.load(open(sys.argv[1])).get("pending_verification") or []
except Exception:
    p=[]
for e in p:
    if isinstance(e,dict):
        print("[driver]   pending: %s (stage %s) — %s; retry after %s" % (
            e.get("core","?"), e.get("stage","?"), e.get("why","?"),
            e.get("earliest_retry_utc","?")))
    else:
        print("[driver]   pending: %s" % (e,))' "$STATE" 2>/dev/null | tee -a "$LOG"
            echo "[driver] Re-run ./launch.sh codex after that time; the session re-runs the check and self-completes." | tee -a "$LOG"
            exit 0 ;;
        halted_*)
            echo "[driver] pipeline halted: $st — operator intervention needed (see the runtime doc's halted_* recovery notes)" | tee -a "$LOG"; exit 0 ;;
        '?')
            echo "[driver] ERROR: cannot read $STATE" | tee -a "$LOG"; exit 1 ;;
    esac
    turn=$((turn + 1))
    if [ "$turn" -gt "$MAX_TURNS" ]; then
        echo "[driver] MAX_TURNS=$MAX_TURNS reached (status=$st) — stopping; re-run ./launch.sh codex to continue" | tee -a "$LOG"; exit 1
    fi
    echo "[driver] === turn $turn ($(date '+%F %T'), status=$st) ===" | tee -a "$LOG"
    # Progress anchor for the fast-turn guard: HEAD before the turn. A turn that
    # advances HEAD did durable work no matter how short it was (collecting a
    # finished worker and committing its artifact is a legitimately quick turn);
    # only short turns that ALSO commit nothing look like a stuck/refusing model.
    head_before="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
    t0=$SECONDS
    set +e
    if [ -z "$SID" ]; then
        run_turn codex exec "${CODEX_EXEC_ONLY_ARGS[@]}" "${CODEX_ARGS[@]}" -- "$FIRST_PROMPT"
        SID="$(find_sid || true)"
        [ -z "$SID" ] && { echo "[driver] ERROR: no session recorded for this project after first turn" | tee -a "$LOG"; exit 1; }
        printf '%s\n' "$SID" > "$SID_CACHE"
    else
        run_turn codex exec resume "$SID" "${CODEX_EXEC_ONLY_ARGS[@]}" "${CODEX_ARGS[@]}" -- "$CONT_PROMPT"
    fi
    set -e
    # Native subagent time is already inside the parent turn: the runtime doc
    # forbids returning while a requested child is live.
    dt=$((SECONDS - t0))
    head_after="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
# Two ceilings on short turns. Native child execution is included in `dt`,
# because the parent waits in-turn:
    #   fast_nocommit — short cycle AND HEAD unchanged. A model producing and
    #     committing NOTHING whose workers (if any) also end instantly is
    #     wedged, refusing, or poll-spinning on a blocked external source;
    #     trip quickly (5). A turn whose native child actually runs resets via
    #     dt; a collect-and-commit turn resets via HEAD.
    #   fast_any — short cycle regardless of commits. Backstop against a
    #     fail-retry loop that commits churn every turn (e.g. a native child
    #     terminal-error receipt or a retry-count bump), which advances HEAD and would
    #     otherwise slip past fast_nocommit all the way to MAX_TURNS. This is
    #     a COARSE token-burn ceiling, NOT a progress detector: HEALTHY
    #     loop-routing cycles whose worker finishes fast (collect a small gate
    #     output → commit → launch next) can still be sub-60s. A live
    #     gate0_revise loop was observed doing 5 such short turns in a row,
    #     and stacked loops (referee cap=10, gate0 reject×revise, Stage 3a)
    #     can run several dozen. The default therefore sits well above
    #     realistic loop depth; only a much longer unbroken run of sub-60s
    #     cycles (any ≥60s cycle — a long worker, or a turn that reads a full
    #     draft/referee report — resets it) is abnormal. MAX_TURNS remains the
    #     hard cap; tune via FAST_TURN_CEILING against real driver.log turn
    #     durations if needed.
    if [ "$dt" -lt 60 ]; then
        fast_any=$((fast_any + 1))
        if [ "$head_after" = "$head_before" ]; then fast_nocommit=$((fast_nocommit + 1)); else fast_nocommit=0; fi
    else
        fast_any=0; fast_nocommit=0
    fi
    if [ "$fast_nocommit" -ge 5 ]; then
        echo "[driver] 5 consecutive sub-60s turns with no new commit — model appears stuck, refusing, or poll-spinning; stopping to avoid burning tokens. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    if [ "$fast_any" -ge "${FAST_TURN_CEILING:-60}" ]; then
        echo "[driver] ${FAST_TURN_CEILING:-60} consecutive sub-60s cycles (even with commits) — abnormal churn; stopping to bound token burn. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    sleep 3
done

}

if [ "$_launch_is_internal" = "1" ]; then
    trap - HUP INT QUIT TERM
    # Normal completion can release the private lock keeper synchronously;
    # its PPID polling remains only the SIGKILL/crash fallback. Without this
    # explicit reap an updater can observe a short, scheduler-dependent lock
    # tail after the visible launcher has fully returned.
    _launch_internal_keeper_close() {
        kill "$_launch_internal_keeper" 2>/dev/null || true
        wait "$_launch_internal_keeper" 2>/dev/null || true
    }
    trap _launch_internal_keeper_close EXIT
    _launch_runtime_main "$@"
    exit
fi

# Only this parent Bash owns descriptor 9. The complete runtime/control tree
# executes in a child subshell with that descriptor closed, so it can neither
# unlock the parent's open file description nor leak the lock into detached
# descendants. Keep stdin explicit: Bash otherwise gives asynchronous commands
# /dev/null when job control is off, which would break interactive runtimes.
#
# The parent also forwards termination and waits for cleanup. Without this
# handshake, killing the visible launch.sh PID could orphan the runtime
# subshell (and an OpenCode server/driver lock) while prematurely releasing the
# project update lock held here.
_launch_requested_runtime="${1:-}"
_launch_child_pid=""
_launch_parent_pgid="$(/bin/ps -o pgid= -p "$$" | tr -d ' ')"
_launch_tty_transferred=0
_launch_transfer_tty() {
    /usr/bin/python3 -I -c '
import os, signal, sys
signal.signal(signal.SIGTTOU, signal.SIG_IGN)
os.tcsetpgrp(0, int(sys.argv[1]))
' "$_launch_child_pid" 2>/dev/null || return 1
    _launch_tty_transferred=1
}
_launch_restore_tty() {
    [ "$_launch_tty_transferred" = "1" ] || return 0
    /usr/bin/python3 -I -c '
import os, signal, sys
signal.signal(signal.SIGTTOU, signal.SIG_IGN)
try:
    os.tcsetpgrp(0, int(sys.argv[1]))
except OSError:
    pass
' "$_launch_parent_pgid" 2>/dev/null || true
    _launch_tty_transferred=0
}
_launch_supervisor_is_foreground() {
    /usr/bin/python3 -I -c '
import os, sys
raise SystemExit(0 if os.tcgetpgrp(0) == int(sys.argv[1]) else 1)
' "$_launch_parent_pgid" 2>/dev/null
}
_launch_suspend_event=0
_launch_resume_failed=0
_launch_handle_suspend() {
    # The internal runtime shell sends USR1 when its foreground group receives
    # terminal Ctrl-Z. This event interrupts wait(1), so no lifetime polling is
    # needed. Freeze the full runtime group, restore the invoking job's TTY,
    # and stop this supervisor. `fg` continues us; we then hand the TTY back.
    trap '' USR1
    if [ "$_launch_tty_transferred" = "1" ] \
            && [ -n "$_launch_child_pid" ] \
            && kill -0 "$_launch_child_pid" 2>/dev/null; then
        kill -STOP -- "-$_launch_child_pid" 2>/dev/null || true
        _launch_restore_tty
        kill -STOP "$$"
        # `bg` also sends SIGCONT, but deliberately leaves the invoking shell
        # in the foreground. Do not steal its terminal. Stop this job again,
        # just as a background terminal reader would via SIGTTIN, until `fg`
        # transfers foreground ownership to the supervisor PGID.
        while ! _launch_supervisor_is_foreground; do
            kill -STOP "$$"
        done
        if kill -0 "$_launch_child_pid" 2>/dev/null; then
            if ! _launch_transfer_tty; then
                kill -KILL -- "-$_launch_child_pid" 2>/dev/null || true
                kill -CONT -- "-$_launch_child_pid" 2>/dev/null || true
                _launch_resume_failed=1
            else
                kill -CONT -- "-$_launch_child_pid" 2>/dev/null || true
            fi
        fi
    fi
    _launch_suspend_event=1
    trap _launch_handle_suspend USR1
}
_launch_cleanup_group() {
    local signal="${1:-TERM}" attempt grace minimum_grace kill_grace abort_timeout
    [ -n "$_launch_child_pid" ] || return 0
    kill -0 -- "-$_launch_child_pid" 2>/dev/null || return 0
    kill -"$signal" -- "-$_launch_child_pid" 2>/dev/null || true
    # A signal can arrive while the exec wrapper is deliberately stopped for
    # publication/TTY handoff. Resume it so INT/TERM and runtime cleanup traps
    # can actually run instead of consuming the entire grace period stopped.
    kill -CONT -- "-$_launch_child_pid" 2>/dev/null || true
    grace="${LAUNCH_SIGNAL_GRACE:-10}"
    case "$grace" in ''|*[!0-9]*) grace=10 ;; esac
    if [ "$_launch_requested_runtime" = "opencode" ]; then
        # OpenCode's runtime trap must first stop an active setsid turn, confirm
        # abort-tree quiescence, and terminate its separate setsid server. Do
        # not SIGKILL the outer shell before that authoritative cleanup can
        # finish; these are the inner routine's own bounded waits plus margin.
        kill_grace="${OPENCODE_KILL_GRACE:-10}"
        abort_timeout="${OPENCODE_ABORT_TIMEOUT:-30}"
        case "$kill_grace" in ''|*[!0-9]*) kill_grace=10 ;; esac
        case "$abort_timeout" in ''|*[!0-9]*) abort_timeout=30 ;; esac
        minimum_grace=$((kill_grace * 2 + abort_timeout + 20))
        [ "$grace" -ge "$minimum_grace" ] || grace="$minimum_grace"
    fi
    attempt=0
    while [ "$attempt" -lt $((grace * 10)) ]; do
        attempt=$((attempt + 1))
        # The guardian's bound notifier deliberately keeps the PGID alive.
        # Wait for the authoritative runtime leader, not group emptiness.
        kill -0 "$_launch_child_pid" 2>/dev/null || return 0
        sleep 0.1
    done
    if [ -n "${_launch_guard_pid:-}" ] && kill -0 "$_launch_guard_pid" 2>/dev/null; then
        _launch_guard_close
        return 0
    fi
    # Guardian failure is detected fail-closed while the known runtime group
    # is still present; only this fallback signals it numerically.
    kill -KILL -- "-$_launch_child_pid" 2>/dev/null || true
    # Killed processes can remain briefly visible until their own parents reap
    # them. They cannot write after SIGKILL, so a bounded confirmation is
    # sufficient before the lock owner returns.
    attempt=0
    while [ "$attempt" -lt 50 ]; do
        attempt=$((attempt + 1))
        kill -0 -- "-$_launch_child_pid" 2>/dev/null || return 0
        sleep 0.02
    done
}
_launch_forward_signal() {
    local signal="$1" exit_code="$2"
    # Coalesce a second Ctrl-C/TERM instead of letting the lock-owning parent
    # take the default action halfway through cleanup.
    trap '' HUP INT QUIT TERM
    if [ -n "$_launch_child_pid" ] && kill -0 "$_launch_child_pid" 2>/dev/null; then
        _launch_cleanup_group "$signal"
    fi
    [ -z "$_launch_child_pid" ] || wait "$_launch_child_pid" 2>/dev/null || true
    _launch_guard_close
    _launch_restore_tty
    exit "$exit_code"
}
# Defer (do not discard) operator signals across the fork→PID/publication
# handshake. The child stops itself after setpgid, so no runtime code can
# escape; once the group identity is published, any pending request is routed
# through the ordinary bounded cleanup path.
_launch_pending_signal=""
trap '_launch_pending_signal=HUP' HUP
trap '_launch_pending_signal=INT' INT
trap '_launch_pending_signal=QUIT' QUIT
trap '_launch_pending_signal=TERM' TERM
# A detached guardian inherits descriptor 9 and an anonymous pipe whose only
# writer is this supervisor. If the supervisor is killed without running traps
# (including `kill -KILL %job` while Ctrl-Z-suspended), pipe EOF wakes the
# guardian, which kills the stopped runtime PGID before releasing its copy of
# the project lock. The guardian self-stops after setsid so startup can prove it
# escaped the supervisor/job-control group before any runtime exists.
_launch_guard_pid=""
_launch_guard_close() {
    trap - EXIT
    printf 'clean\n' >&7 2>/dev/null || true
    exec 7>&-
    [ -z "$_launch_guard_pid" ] || wait "$_launch_guard_pid" 2>/dev/null || true
    _launch_guard_pid=""
}
exec 7> >(/usr/bin/python3 -I -c '
import os, select, signal, sys, time
os.setsid()
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_IGN)
os.kill(os.getpid(), signal.SIGSTOP)
line = sys.stdin.readline().strip()
if not line:
    raise SystemExit(0)
try:
    runtime_pgid = int(line)
except ValueError:
    raise SystemExit(1)
# The internal shell publishes a persistent same-PGID notifier before any CLI
# starts. It ignores catchable termination signals and therefore stabilizes the
# group identity even after the leader exits, until this guardian kills it.
anchor_line = sys.stdin.readline().strip()
try:
    anchor_pid = int(anchor_line)
except ValueError:
    raise SystemExit(1)
try:
    if os.getpgid(anchor_pid) != runtime_pgid:
        raise SystemExit(1)
except ProcessLookupError:
    raise SystemExit(1)

identity_kind = None
identity_fd = None
kqueue = None
try:
    if hasattr(os, "pidfd_open"):
        try:
            identity_fd = os.pidfd_open(anchor_pid)
        except OSError:
            identity_fd = None
        else:
            identity_kind = "pidfd"
    if identity_kind is None and sys.platform.startswith("linux"):
        # Python 3.8 lacks os.pidfd_open. An open proc-directory descriptor is
        # also the fallback when an older kernel/seccomp profile rejects the
        # syscall: it is tied to this process instance, and after exit opening
        # `stat` relative to it cannot follow a reused numeric PID.
        identity_fd = os.open(f"/proc/{anchor_pid}",
                              os.O_RDONLY | os.O_DIRECTORY |
                              getattr(os, "O_NOFOLLOW", 0))
        identity_kind = "procfd"
    if identity_kind is None and hasattr(select, "kqueue"):
        kqueue = select.kqueue()
        event = select.kevent(anchor_pid, filter=select.KQ_FILTER_PROC,
                              flags=select.KQ_EV_ADD,
                              fflags=select.KQ_NOTE_EXIT)
        kqueue.control([event], 0, 0)
        identity_kind = "kqueue"
    if identity_kind is None:
        raise SystemExit(1)
except (OSError, ProcessLookupError):
    raise SystemExit(1)
# The shell waits for this acknowledgement before closing its arming writer or
# starting agent-controlled code.
os.kill(runtime_pgid, signal.SIGUSR2)
completion = sys.stdin.read()
# Both clean completion and bare EOF terminate the residual runtime group. On
# clean completion the leader has already exited or completed its authoritative
# teardown; on bare EOF this is supervisor-death recovery. In both cases the
# live bound anchor makes killpg identity-safe.
alive = False
if identity_kind == "pidfd":
    alive = not bool(select.select([identity_fd], [], [], 0)[0])
elif identity_kind == "procfd":
    try:
        stat_fd = os.open("stat", os.O_RDONLY, dir_fd=identity_fd)
    except OSError:
        alive = False
    else:
        os.close(stat_fd)
        alive = True
elif identity_kind == "kqueue":
    alive = not bool(kqueue.control(None, 1, 0))
if not alive:
    raise SystemExit(0)
try:
    os.killpg(runtime_pgid, signal.SIGKILL)
except ProcessLookupError:
    pass
for _ in range(50):
    if identity_kind == "pidfd":
        if select.select([identity_fd], [], [], 0)[0]:
            break
    elif identity_kind == "procfd":
        try:
            stat_fd = os.open("stat", os.O_RDONLY, dir_fd=identity_fd)
        except OSError:
            break
        else:
            os.close(stat_fd)
    elif kqueue.control(None, 1, 0):
        break
    time.sleep(0.02)
')
_launch_guard_pid=$!
_launch_guard_attempt=0
while [ "$_launch_guard_attempt" -lt 100 ]; do
    _launch_guard_attempt=$((_launch_guard_attempt + 1))
    _launch_guard_pgid="$(/bin/ps -o pgid= -p "$_launch_guard_pid" 2>/dev/null | tr -d ' ')"
    _launch_guard_state="$(/bin/ps -o stat= -p "$_launch_guard_pid" 2>/dev/null | tr -d ' ')"
    if [ "$_launch_guard_pgid" = "$_launch_guard_pid" ]; then
        case "$_launch_guard_state" in *T*) break ;; esac
    fi
    kill -0 "$_launch_guard_pid" 2>/dev/null || break
    sleep 0.01
done
case "${_launch_guard_state:-}" in *T*) _launch_guard_stopped=1 ;; *) _launch_guard_stopped=0 ;; esac
if [ "${_launch_guard_pgid:-}" != "$_launch_guard_pid" ] || [ "$_launch_guard_stopped" != "1" ]; then
    kill -KILL "$_launch_guard_pid" 2>/dev/null || true
    kill -CONT "$_launch_guard_pid" 2>/dev/null || true
    exec 7>&-
    wait "$_launch_guard_pid" 2>/dev/null || true
    echo "ERROR: could not establish isolated runtime lock guardian" >&2
    exit 1
fi
trap _launch_guard_close EXIT
kill -CONT "$_launch_guard_pid" 2>/dev/null || {
    echo "ERROR: could not continue isolated runtime lock guardian" >&2
    exit 1
}
# A separate process group gives the runtime one stable shutdown identity. A
# tiny trusted Python exec wrapper establishes it before Bash or a CLI can
# spawn; the new Bash re-reads this trusted script through a descriptor-gated
# internal entrypoint and receives no startup-hook environment. Non-job-control
# Bash otherwise makes an ordinary async subshell inherit ignored INT/QUIT.
/usr/bin/python3 -I -c '
import os, signal, sys, time
os.setpgid(0, 0)
for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
    signal.signal(signum, signal.SIG_DFL)
# Build and publish the persistent same-PGID anchor entirely child-side before
# this wrapper stops. Thus supervisor SIGKILL in any fork/publication window
# still leaves a runnable writer that completes guardian arming, closes fd7,
# and lets bare EOF trigger identity-safe group cleanup.
supervisor = int(sys.argv[2])
armed = False
def arm(_signum, _frame):
    global armed
    armed = True
signal.signal(signal.SIGUSR2, arm)
anchor_pid = os.fork()
if anchor_pid == 0:
    for fd in (7, 8):
        try:
            os.close(fd)
        except OSError:
            pass
    def notify(_signum, _frame):
        try:
            os.kill(supervisor, signal.SIGUSR1)
        except ProcessLookupError:
            pass
    signal.signal(signal.SIGTSTP, notify)
    for signum in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM):
        signal.signal(signum, signal.SIG_IGN)
    while True:
        signal.pause()
published = False
try:
    os.write(7, (str(os.getpid()) + "\n" + str(anchor_pid) + "\n").encode())
    published = True
    deadline = time.monotonic() + 2
    while not armed and time.monotonic() < deadline:
        time.sleep(0.01)
except OSError:
    pass
finally:
    os.close(7)
if not published or not armed:
    os.kill(anchor_pid, signal.SIGKILL)
    raise SystemExit(75)
signal.signal(signal.SIGUSR2, signal.SIG_DFL)
os.kill(os.getpid(), signal.SIGSTOP)  # Parent transfers any TTY before SIGCONT.
env = os.environ.copy()
for key in ("BASH_ENV", "ENV", "BASHOPTS", "SHELLOPTS", "CDPATH", "GLOBIGNORE"):
    env.pop(key, None)
env["ZEROPAPER_LAUNCH_INTERNAL"] = "1"
env["ZEROPAPER_LAUNCH_SUPERVISOR_PID"] = sys.argv[2]
argv = ["bash", "--noprofile", "--norc", sys.argv[1], *sys.argv[3:]]
os.execve("/bin/bash", argv, env)
' "$ROOT/launch.sh" "$$" "$@" 8<&9 9<&- <&0 &
_launch_child_pid=$!
# Confirm the wrapper established and stopped the promised group before
# transferring a TTY or accepting an operator signal.
_launch_group_attempt=0
while [ "$_launch_group_attempt" -lt 100 ]; do
    _launch_group_attempt=$((_launch_group_attempt + 1))
    _launch_group_now="$(/bin/ps -o pgid= -p "$_launch_child_pid" 2>/dev/null | tr -d ' ')"
    _launch_group_state="$(/bin/ps -o stat= -p "$_launch_child_pid" 2>/dev/null | tr -d ' ')"
    if [ "$_launch_group_now" = "$_launch_child_pid" ]; then
        case "$_launch_group_state" in *T*) break ;; esac
    fi
    kill -0 "$_launch_child_pid" 2>/dev/null || break
    sleep 0.01
done
case "${_launch_group_state:-}" in *T*) _launch_group_stopped=1 ;; *) _launch_group_stopped=0 ;; esac
if [ "${_launch_group_now:-}" != "$_launch_child_pid" ] || [ "$_launch_group_stopped" != "1" ]; then
    # The wrapper may already be stopped even when ps output was incomplete or
    # surprising. Never wait indefinitely for a stopped, unpublished child.
    kill -KILL -- "-$_launch_child_pid" 2>/dev/null || kill -KILL "$_launch_child_pid" 2>/dev/null || true
    kill -CONT -- "-$_launch_child_pid" 2>/dev/null || kill -CONT "$_launch_child_pid" 2>/dev/null || true
    wait "$_launch_child_pid" 2>/dev/null || true
    echo "ERROR: could not establish isolated runtime process group" >&2
    exit 1
fi
if [ -t 0 ]; then
    if ! _launch_transfer_tty; then
        kill -KILL -- "-$_launch_child_pid" 2>/dev/null || true
        kill -CONT -- "-$_launch_child_pid" 2>/dev/null || true
        wait "$_launch_child_pid" 2>/dev/null || true
        echo "ERROR: could not transfer the controlling terminal to the runtime" >&2
        exit 1
    fi
fi
trap '_launch_forward_signal HUP 129' HUP
trap '_launch_forward_signal INT 130' INT
trap '_launch_forward_signal QUIT 131' QUIT
trap '_launch_forward_signal TERM 143' TERM
trap _launch_handle_suspend USR1
kill -CONT -- "-$_launch_child_pid" 2>/dev/null || {
    _launch_restore_tty
    wait "$_launch_child_pid" 2>/dev/null || true
    echo "ERROR: could not continue isolated runtime process group" >&2
    exit 1
}
case "$_launch_pending_signal" in
    HUP) _launch_forward_signal HUP 129 ;;
    INT) _launch_forward_signal INT 130 ;;
    QUIT) _launch_forward_signal QUIT 131 ;;
    TERM) _launch_forward_signal TERM 143 ;;
esac
# USR1 from the runtime's TSTP trap interrupts Bash wait with status 138. The
# handler performs the complete stop/fg/continue handshake; then wait again on
# the same identity. There is no polling or per-runtime helper churn.
while :; do
    _launch_suspend_event=0
    if wait "$_launch_child_pid"; then
        _launch_child_rc=0
    else
        _launch_child_rc=$?
    fi
    if [ "$_launch_suspend_event" = "1" ] \
            && kill -0 "$_launch_child_pid" 2>/dev/null; then
        continue
    fi
    break
done
[ "$_launch_resume_failed" = "0" ] || _launch_child_rc=1
# With a controlling TTY, Ctrl-C goes directly to the foreground runtime group,
# not this lock-owning parent. The leader may exit while an ignoring or
# shutdown-spawned member remains. Verify and drain the group after *every*
# leader exit before restoring the TTY or releasing descriptor 9.
_launch_cleanup_group TERM
_launch_guard_close
_launch_restore_tty
trap - HUP INT QUIT TERM USR1
exit "$_launch_child_rc"
