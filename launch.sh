#!/usr/bin/env bash
# launch.sh — start a pipeline runtime for this project.
#
# Usage:
#   ./launch.sh claude              # interactive Claude Code (autowake-native)
#   ./launch.sh codex               # HEADLESS DRIVER LOOP (see below) — the
#                                   #   autonomous way to run the codex runtime
#   ./launch.sh codex --once        # single interactive codex TUI, no driver
#   ./launch.sh gemini              # interactive Gemini CLI
#   ./launch.sh grok                # interactive Grok Build
#   ./launch.sh <runtime> --tmux    # same, wrapped in a detached tmux window
#
# WHY THE CODEX DRIVER EXISTS: codex has no autowake. When the orchestrator
# model ends its turn, the session is inert until a new message arrives — with
# native spawn_agent AND with the pipeline's launcher alike (verified
# empirically on codex-cli 0.144.1: a parent that ended its turn was never
# woken by its completing child). An interactive codex TUI is therefore only
# pseudo-autonomous: any turn-end between stages stalls the pipeline until a
# human types. The driver makes turn-ends harmless instead of forbidden: it
# runs each turn headlessly (`codex exec`, then `codex exec resume <session>`
# — same session, full context) and immediately re-prompts whenever a turn
# ends, until pipeline_state.json reports complete or halted_*. Workers
# launched by code/utils/agent_launcher/launch_agent.sh are detached into
# their own process sessions, so a turn ending mid-launch does not kill them;
# the resumed turn reconnects via the sentinel + output-file protocol.
#
# Cost guard: five consecutive sub-60s turns aborts the driver (a healthy
# pipeline turn does real work; rapid-fire short turns mean the model is stuck
# or refusing, and re-prompting would only burn tokens).
set -euo pipefail

# pwd -P (physical): codex records its cwd via getcwd(), which resolves
# symlinks (macOS /tmp -> /private/tmp). find_sid matches our path against the
# recorded one, so ROOT must be the physical form or resume silently degrades
# to a fresh session on any symlinked project path.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

RUNTIME="${1:?Usage: ./launch.sh <claude|codex|gemini|grok> [--tmux] [--once]}"
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

# Re-wrap into tmux first, so everything below runs inside the window.
if [ "$TMUX_WRAP" = "1" ]; then
    _win="pipeline-$RUNTIME-$(basename "$ROOT")"
    _cmd="cd $(printf '%q' "$ROOT") && ./launch.sh $(printf '%q' "$RUNTIME")$( [ "$ONCE" = "1" ] && printf ' --once' )"
    if [ -n "${TMUX:-}" ]; then
        tmux new-window -n "$_win" "$_cmd"
    else
        tmux new-session -d -s "$_win" "$_cmd"
        echo "Launched in tmux session '$_win' — attach with: tmux attach -t $_win"
    fi
    exit 0
fi

# Every runtime wants the project venv active (bare python3 resolves to it,
# and agent subshells inherit it).
if [ -f "$ROOT/.venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$ROOT/.venv/bin/activate"
else
    echo "WARNING: no .venv in this project — python deps may be missing (create with: uv venv .venv)" >&2
fi

case "$RUNTIME" in
    claude)
        exec claude --dangerously-skip-permissions
        ;;
    gemini)
        exec gemini --yolo
        ;;
    grok)
        exec grok --sandbox pipeline --always-approve
        ;;
    codex) ;;  # falls through to the driver below
    *)
        echo "ERROR: unknown runtime '$RUNTIME' (claude|codex|gemini|grok)" >&2
        exit 2
        ;;
esac

# ── codex ───────────────────────────────────────────────────────────────────
# Sandbox posture: workspace-write mirroring the Claude deploy (open egress,
# cache roots writable) plus $ROOT/.git as its own writable root — codex marks
# each root's top-level .git read-only with no toggle, and listing .git as its
# own root is the verified workaround; without it every pipeline `git commit`
# dies on index.lock. Expressed as -c config keys (not -s/-C flags) because
# `codex exec resume` accepts only the config form.
CODEX_ARGS=(
    --skip-git-repo-check
    -c 'sandbox_mode="workspace-write"'
    -c 'approval_policy="never"'
    -c 'sandbox_workspace_write.network_access=true'
    -c "sandbox_workspace_write.writable_roots=[\"~/.codex\",\"~/.cache\",\"~/Library/Caches\",\"~/.matplotlib\",\"$ROOT/.git\"]"
)

if [ "$ONCE" = "1" ]; then
    exec codex "${CODEX_ARGS[@]}"
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

sid_exists() {
    ls "$HOME"/.codex/sessions/*/*/*/rollout-*"$1".jsonl >/dev/null 2>&1
}

find_sid() {
    local f sid
    if [ -s "$SID_CACHE" ]; then
        sid="$(cat "$SID_CACHE")"
        if sid_exists "$sid"; then echo "$sid"; return 0; fi
    fi
    for f in $(ls -t "$HOME"/.codex/sessions/*/*/*/rollout-*.jsonl 2>/dev/null | head -50); do
        if head -1 "$f" | grep -qF "\"cwd\":\"$ROOT\""; then
            head -1 "$f" | python3 -c 'import json,sys; print(json.load(sys.stdin)["payload"]["session_id"])'
            return 0
        fi
    done
    return 1
}

FIRST_PROMPT='Run the pipeline. You are running unattended — never stop to ask the user anything; make every decision from the pipeline documents.'
CONT_PROMPT='Continue the pipeline from process_log/pipeline_state.json. You are running unattended — never stop to ask the user anything. If process_log/agent_runs/ contains a .<agent>.running sentinel, a detached worker from a previous turn may still be executing: poll the output file recorded in the sentinel and collect it (do NOT relaunch that agent) before doing anything else.'

LOG="$ROOT/process_log/driver.log"
MAX_TURNS="${MAX_TURNS:-300}"
# Per-turn wall-clock cap (the "ping codex every 59 minutes" guarantee): a
# turn still running at the cap is killed and the session resumed on the next
# loop iteration. This bounds the damage of a hung turn (network stall, model
# wedged mid-turn — nothing else can recover those, since codex accepts no
# mid-turn input). Killing a healthy long turn is safe by construction:
# detached workers survive, state lives in files/commits, and the resumed
# turn re-reads both. 59 min, not 60 — the user-visible promise is "the
# session is re-prompted at least hourly".
TURN_TIMEOUT="${TURN_TIMEOUT:-3540}"

# Run one codex turn with the watchdog. Args: the full codex command.
# Uses process substitution (not a pipe) so $! is the codex pid.
run_turn() {
    local cpid cstart wpid rc
    "$@" </dev/null > >(tee -a "$LOG") 2>&1 &
    cpid=$!
    # Identity anchor for the watchdog: pid + process start time. If the
    # driver is SIGKILLed, the orphaned watchdog sleeps out its timer and
    # would otherwise TERM a possibly-REUSED pid belonging to an unrelated
    # process; a start-time mismatch (or empty = gone) means "not our codex,
    # don't touch". Name-matching (ps -o comm=) is NOT reliable here — comm
    # shows the interpreter for script wrappers.
    cstart="$(ps -o lstart= -p "$cpid" 2>/dev/null)"
    (
        sleep "$TURN_TIMEOUT"
        if [ -n "$cstart" ] && [ "$(ps -o lstart= -p "$cpid" 2>/dev/null)" = "$cstart" ]; then
            echo "[driver] turn exceeded TURN_TIMEOUT=${TURN_TIMEOUT}s — killing it and resuming (detached workers are unaffected)" | tee -a "$LOG"
            kill -TERM "$cpid" 2>/dev/null
            sleep 10
            if [ "$(ps -o lstart= -p "$cpid" 2>/dev/null)" = "$cstart" ]; then
                kill -KILL "$cpid" 2>/dev/null
            fi
        fi
    ) &
    wpid=$!
    wait "$cpid"
    rc=$?
    kill "$wpid" 2>/dev/null
    wait "$wpid" 2>/dev/null
    return "$rc"
}

# Wake-on-worker-finish: if the previous turn ended while a detached worker
# (launch_agent.sh) was still in flight, do NOT re-prompt immediately — a
# resumed turn would have nothing to do but babysit the sentinel, and a model
# that keeps ending such turns would trip the fast-turn guard. Wait until
# every live sentinel clears (the worker's wrapper removes it on completion),
# treating a sentinel whose recorded output file already exists as finished
# (wrapper died before cleanup — rare). WORKER_WAIT_MAX caps the wait so a
# truly wedged worker can't park the driver forever; on cap the orchestrator
# is resumed anyway and its prompt tells it how to handle a live sentinel.
wait_for_workers() {
    local waited=0 cap="${WORKER_WAIT_MAX:-14400}" s out pending
    while :; do
        pending=0
        for s in "$ROOT"/process_log/agent_runs/.*.running; do
            [ -e "$s" ] || continue
            out="$(sed -n 's/.*output=//p' "$s" | head -1)"
            if [ -n "$out" ] && { [ -s "$out" ] || [ -s "$ROOT/$out" ]; }; then
                continue  # output already written: worker is done, sentinel stale
            fi
            pending=1
        done
        [ "$pending" = "0" ] && return 0
        if [ "$waited" -ge "$cap" ]; then
            echo "[driver] worker-wait cap (${cap}s) reached with a sentinel still live — resuming anyway" | tee -a "$LOG"
            return 0
        fi
        if [ "$waited" = "0" ]; then
            echo "[driver] detached worker(s) still running after turn end — waiting for them to finish before re-prompting" | tee -a "$LOG"
        fi
        sleep 10
        waited=$((waited + 10))
    done
}

turn=0
fast=0
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
    wait_for_workers
    st="$(status)"
    case "$st" in
        complete)
            echo "[driver] pipeline COMPLETE after $turn driver turn(s)" | tee -a "$LOG"; exit 0 ;;
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
    t0=$SECONDS
    set +e
    if [ -z "$SID" ]; then
        run_turn codex exec "${CODEX_ARGS[@]}" -- "$FIRST_PROMPT"
        SID="$(find_sid || true)"
        [ -z "$SID" ] && { echo "[driver] ERROR: no session recorded for this project after first turn" | tee -a "$LOG"; exit 1; }
        printf '%s\n' "$SID" > "$SID_CACHE"
    else
        run_turn codex exec resume "$SID" "${CODEX_ARGS[@]}" -- "$CONT_PROMPT"
    fi
    set -e
    dt=$((SECONDS - t0))
    if [ "$dt" -lt 60 ]; then fast=$((fast + 1)); else fast=0; fi
    if [ "$fast" -ge 5 ]; then
        echo "[driver] 5 consecutive sub-60s turns — model appears stuck or refusing; stopping to avoid burning tokens. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    sleep 3
done
