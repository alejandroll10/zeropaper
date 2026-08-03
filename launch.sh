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
#   ./launch.sh opencode            # resumable headless OpenCode driver
#   ./launch.sh opencode --once     # interactive OpenCode TUI
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
# Cost guard (two ceilings; details at the guard itself): the driver aborts on
# 5 consecutive sub-60s CYCLES that also commit NOTHING (a stuck/refusing model),
# or on a much longer run of sub-60s cycles even with commits (a coarse token-burn
# backstop against a churn-committing retry loop). A cycle is the turn PLUS the
# post-turn wait for any detached worker it launched — so a quick turn that hands
# off real work is judged by its worker's runtime, not its own. Both ceilings
# reset on any cycle that does real work; a committing progress turn never trips
# the first.
set -euo pipefail

# pwd -P (physical): codex records its cwd via getcwd(), which resolves
# symlinks (macOS /tmp -> /private/tmp). find_sid matches our path against the
# recorded one, so ROOT must be the physical form or resume silently degrades
# to a fresh session on any symlinked project path.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
cd "$ROOT"

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

# Re-wrap into tmux first, so everything below runs inside the window.
if [ "$TMUX_WRAP" = "1" ]; then
    _win="pipeline-$RUNTIME-$(basename "$ROOT")"
    # `|| true`: the && chain returns 1 when ONCE=0, and an assignment's exit
    # status is its command substitution's — without the guard, set -e kills
    # the script right here, silently, on every plain `--tmux` launch.
    _cmd="cd $(printf '%q' "$ROOT") && ./launch.sh $(printf '%q' "$RUNTIME")$( [ "$ONCE" = "1" ] && printf ' --once' || true )"
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
        exec claude ${LIGHT_ARGS[@]+"${LIGHT_ARGS[@]}"} --dangerously-skip-permissions
        ;;
    gemini)
        LIGHT_ARGS=()
        _light_model="$(light_orchestrator_model "$ROOT/.gemini/agents")"
        if [ -n "$_light_model" ]; then
            LIGHT_ARGS=(--model "$_light_model")
            echo "[launch] --light: orchestrator pinned to $_light_model" >&2
        fi
        exec gemini ${LIGHT_ARGS[@]+"${LIGHT_ARGS[@]}"} --yolo
        ;;
    grok)
        install_grok_venv_shims
        warn_grok_keychain_push
        # Per-project leader socket: all grok clients share ~/.grok/leader.sock
        # by default, and a second client on that socket TEARS DOWN the first
        # session's in-flight turn — concurrent projects would cancel each
        # other (issue #186/#190; see README).
        exec grok --sandbox pipeline --always-approve --leader-socket "$ROOT/.grok/leader.sock"
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
    # OpenCode's provider reads this key from the process environment, while
    # deployments store credentials in a gitignored project .env. Import only
    # this one value without sourcing/evaluating arbitrary shell text. An
    # already-exported value wins over the file.
    if [ -z "${OPENCODE_API_KEY:-}" ] && [ -f "$ROOT/.env" ]; then
        OPENCODE_API_KEY="$(python3 - "$ROOT/.env" <<'PY'
import ast, re, sys

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

for raw in open(sys.argv[1], encoding="utf-8"):
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
    if [ "$ONCE" = "1" ]; then
        exec opencode --model opencode/deepseek-v4-flash
    fi
    OC_STATE="$ROOT/process_log/pipeline_state.json"
    if [ ! -f "$OC_STATE" ]; then
        echo "ERROR: no process_log/pipeline_state.json — use ./launch.sh opencode --once for manual/report work." >&2
        exit 1
    fi
    oc_status() {
        python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status","?"))' "$OC_STATE" 2>/dev/null || echo "?"
    }
    oc_worktree_hash() {
        {
            git -C "$ROOT" diff --binary --no-ext-diff 2>/dev/null || true
            git -C "$ROOT" diff --cached --binary --no-ext-diff 2>/dev/null || true
            git -C "$ROOT" ls-files --others --exclude-standard -z 2>/dev/null \
                | while IFS= read -r -d '' _oc_file; do
                    cksum "$ROOT/$_oc_file" 2>/dev/null || true
                done
        } | cksum
    }
    OC_SID_CACHE="$ROOT/process_log/.opencode_session_id"
    OC_LOG="$ROOT/process_log/opencode-driver.log"
    OPENCODE_TURN_TIMEOUT="${OPENCODE_TURN_TIMEOUT:-3540}"
    OPENCODE_KILL_GRACE="${OPENCODE_KILL_GRACE:-10}"
    OPENCODE_LOOP_DELAY="${OPENCODE_LOOP_DELAY:-3}"
    OC_FIRST='Run the pipeline. You are running unattended: never ask the user anything; decide from AGENTS.md and the pipeline artifacts. Use native task calls for .opencode subagents and wait for their foreground results.'
    OC_CONT='Continue the pipeline from process_log/pipeline_state.json. You are unattended: never ask the user anything. Use native task calls for .opencode subagents and keep working until this turn has made durable progress.'
    oc_sid_exists() {
        opencode session list --format json 2>/dev/null | python3 -c 'import json,os,sys
sid,root=sys.argv[1:]
try: rows=json.load(sys.stdin)
except Exception: raise SystemExit(1)
def local(x):
    directory=x.get("directory")
    return isinstance(directory,str) and os.path.realpath(directory) == root
raise SystemExit(0 if any((x.get("id") or x.get("sessionID")) == sid and local(x) for x in rows) else 1)' "$1" "$ROOT"
    }
    oc_reconcile_new_sid() { # $1 = JSON snapshot from before the fresh run
        local before_file="$1" after_file candidate
        after_file="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode-sessions.XXXXXX")"
        if ! opencode session list --format json > "$after_file" 2>/dev/null; then
            rm -f "$after_file"
            return 1
        fi
        candidate="$(python3 - "$before_file" "$after_file" "$ROOT" <<'PY'
import json, os, sys
try:
    root = os.path.realpath(sys.argv[3])
    before_rows = json.load(open(sys.argv[1]))
    after_rows = json.load(open(sys.argv[2]))
except Exception:
    raise SystemExit(1)
def local(x):
    directory = x.get("directory")
    return isinstance(directory, str) and os.path.realpath(directory) == root
before = {x.get("id") or x.get("sessionID") for x in before_rows if local(x)}
after = [x.get("id") or x.get("sessionID") for x in after_rows if local(x)]
new = [x for x in after if x and x not in before]
if len(new) != 1:
    raise SystemExit(1)
print(new[0])
PY
)" || { rm -f "$after_file"; return 1; }
        rm -f "$after_file"
        printf '%s\n' "$candidate"
    }
    OC_ACTIVE_PGID=""
    OC_WATCHDOG_PID=""
    oc_kill_turn_group() { # $1 = TERM or KILL
        [ -n "$OC_ACTIVE_PGID" ] || return 0
        kill -"$1" -- "-$OC_ACTIVE_PGID" 2>/dev/null || true
    }
    oc_turn_group_alive() {
        [ -n "$OC_ACTIVE_PGID" ] && kill -0 -- "-$OC_ACTIVE_PGID" 2>/dev/null
    }
    oc_driver_cleanup() {
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
    trap oc_driver_cleanup EXIT
    trap 'oc_driver_cleanup; trap - EXIT; exit 130' INT TERM
    run_opencode_turn() {
        local oc_pid oc_start oc_now watchdog_pid rc timeout_marker="${oc_events}.timeout"
        # Capture to a regular file, then replay into the durable log after the
        # turn. Avoid process substitution here: restricted shells can reject
        # writes through /dev/fd even when the project itself is writable.
        # Python's os.setsid is available on every supported Unix host and
        # makes the turn leader its own process-group leader. Killing the group
        # therefore reaches Bash commands and subagents as well as OpenCode.
        python3 -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
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
            # A normally exiting CLI should have no live descendants. If one
            # remains, give it the same orderly shutdown window.
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
            echo "[opencode-driver] cached session is stale; starting a fresh session" | tee -a "$OC_LOG"
            rm -f "$OC_SID_CACHE"
        fi
    fi
    oc_turn=0
    oc_no_progress=0
    oc_fast_any=0
    while :; do
        oc_st="$(oc_status)"
        case "$oc_st" in
            complete|complete_pending_verification)
                echo "[opencode-driver] pipeline $oc_st after $oc_turn turn(s)" | tee -a "$OC_LOG"; exit 0 ;;
            halted_*)
                echo "[opencode-driver] pipeline halted: $oc_st" | tee -a "$OC_LOG"; exit 0 ;;
            '?') echo "[opencode-driver] cannot read $OC_STATE" | tee -a "$OC_LOG"; exit 1 ;;
        esac
        oc_turn=$((oc_turn + 1))
        if [ "$oc_turn" -gt "${MAX_TURNS:-300}" ]; then
            echo "[opencode-driver] MAX_TURNS reached (status=$oc_st)" | tee -a "$OC_LOG"; exit 1
        fi
        oc_events="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode.XXXXXX")"
        oc_sessions_before=""
        oc_sessions_before_valid=0
        if [ -z "$OC_SID" ]; then
            oc_sessions_before="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode-sessions.XXXXXX")"
            if opencode session list --format json > "$oc_sessions_before" 2>/dev/null && \
                    python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$oc_sessions_before" 2>/dev/null; then
                oc_sessions_before_valid=1
            fi
        fi
        oc_before="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true):$(oc_worktree_hash):$(cksum "$OC_STATE" 2>/dev/null || true)"
        oc_t0=$SECONDS
        set +e
        if [ -n "$OC_SID" ]; then
            run_opencode_turn opencode run --session "$OC_SID" --model opencode/deepseek-v4-flash --format json "$OC_CONT"
            oc_rc=$?
        else
            run_opencode_turn opencode run --model opencode/deepseek-v4-flash --format json "$OC_FIRST"
            oc_rc=$?
            OC_SID="$(python3 -c 'import json,sys
for line in open(sys.argv[1]):
    try: event=json.loads(line)
    except Exception: continue
    sid=event.get("sessionID") or event.get("sessionId")
    if sid: print(sid); break' "$oc_events")"
            [ -n "$OC_SID" ] && printf '%s\n' "$OC_SID" > "$OC_SID_CACHE"
        fi
        set -e
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
        if [ -z "$OC_SID" ] && [ "$oc_sessions_before_valid" = "1" ]; then
            OC_SID="$(oc_reconcile_new_sid "$oc_sessions_before" || true)"
            [ -n "$OC_SID" ] && printf '%s\n' "$OC_SID" > "$OC_SID_CACHE"
        fi
        [ -n "$oc_sessions_before" ] && rm -f "$oc_sessions_before"
        rm -f "$oc_events"
        rm -f "${oc_events}.timeout"
        if [ "$oc_timed_out" = "1" ]; then
            if [ -z "$OC_SID" ]; then
                echo "[opencode-driver] timed-out first turn returned no session id; cannot resume" | tee -a "$OC_LOG"
                exit 1
            fi
            sleep "$OPENCODE_LOOP_DELAY"
            continue
        fi
        if [ "$oc_rc" -ne 0 ]; then
            echo "[opencode-driver] turn failed (exit $oc_rc); stopping for inspection" | tee -a "$OC_LOG"
            exit "$oc_rc"
        fi
        [ -n "$OC_SID" ] || { echo "[opencode-driver] no session id returned" | tee -a "$OC_LOG"; exit 1; }
        oc_after="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true):$(oc_worktree_hash):$(cksum "$OC_STATE" 2>/dev/null || true)"
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

# --light: pin the orchestrator to the same tier the subagents were assembled
# on (see light_orchestrator_model above). Config form, not --model, because
# `codex exec resume` accepts only -c — and the driver resumes on every turn
# after the first, so a flag-form pin would silently apply to turn 1 alone.
_light_model="$(light_orchestrator_model "$ROOT/.codex/agents")"
if [ -n "$_light_model" ]; then
    CODEX_ARGS+=(-c "model=\"$_light_model\"")
    echo "[launch] --light: orchestrator pinned to $_light_model" >&2
fi

# Proxy-auth version floor (issue #213): codex ≤0.144.x is a silent total
# outage behind an authenticated proxy. Warn-only; guarded so a pre-preflight
# deploy (or a refresh not yet run) never blocks the launch.
if [ -f "$ROOT/code/utils/codex_preflight.sh" ]; then
    . "$ROOT/code/utils/codex_preflight.sh"
    codex_proxy_auth_preflight
fi

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
# Outcome globals for the fast-cycle guard: WAITED = seconds this call
# blocked; WAIT_CAPPED = 1 when it gave up at WORKER_WAIT_MAX with a sentinel
# still live. A wait that ENDED because the worker finished is evidence of
# real work and counts toward the cycle's duration; a wait that ended because
# we gave up on a wedged worker is not — crediting a cap-timeout as work
# would let a hung worker reset the stuck-guard forever.
wait_for_workers() {
    local waited=0 cap="${WORKER_WAIT_MAX:-14400}" s out pending wait_start=$SECONDS
    WAITED=0; WAIT_CAPPED=0
    while :; do
        pending=0
        for s in "$ROOT"/process_log/agent_runs/.*.running; do
            [ -e "$s" ] || continue
            # || true on every read of "$s": the wrapper can rm the sentinel
            # between our [ -e ] test and the read; a failed assignment under
            # set -e would kill the whole driver on that poll race.
            out="$(sed -n 's/.*output=//p' "$s" 2>/dev/null | head -1 || true)"
            if [ -n "$out" ] && { [ -s "$out" ] || [ -s "$ROOT/$out" ]; }; then
                continue  # output already written: worker is done, sentinel stale
            fi
            # Liveness check via the wrapper pid the launcher recorded: a
            # dead wrapper with no output means worker AND wrapper were
            # externally killed — the sentinel is an orphan that would
            # otherwise park us until the wait cap. Clear it and move on; the
            # resumed orchestrator sees the missing output and relaunches.
            # kill -0 is the primary probe (signal-based — works even though
            # macOS ps/pgrep need sysmond and return NOTHING from inside
            # sandboxes, which is also why the recorded lstart may be empty:
            # the launcher runs inside the orchestrator's sandbox). lstart is
            # only a secondary pid-reuse guard when both sides captured it.
            # Old-format sentinels without wrapper_pid keep plain waiting.
            w_pid="$(sed -n 's/.*wrapper_pid=\([0-9][0-9]*\).*/\1/p' "$s" 2>/dev/null | head -1 || true)"
            w_lstart="$(sed -n 's/.*wrapper_lstart=\(.*\)$/\1/p' "$s" 2>/dev/null | head -1 || true)"
            if [ -n "$w_pid" ]; then
                w_dead=""
                if ! kill -0 "$w_pid" 2>/dev/null; then
                    w_dead=1
                elif [ -n "$w_lstart" ]; then
                    w_now="$(ps -o lstart= -p "$w_pid" 2>/dev/null || true)"
                    [ -n "$w_now" ] && [ "$w_now" != "$w_lstart" ] && w_dead=1  # pid reused
                fi
                if [ -n "$w_dead" ]; then
                    echo "[driver] sentinel $(basename "$s") references a dead worker with no output — clearing the orphan" | tee -a "$LOG"
                    rm -f "$s"
                    continue
                fi
            fi
            pending=1
        done
        # WAITED is wall-clock (not the nominal tick counter `waited`): the
        # loop body itself costs time per tick, and over the 4h default cap
        # that drift reaches tens of seconds — enough to leak into dt and
        # falsely reset the fast-cycle guard if WAITED undercounted.
        [ "$pending" = "0" ] && { WAITED=$((SECONDS - wait_start)); return 0; }
        if [ "$waited" -ge "$cap" ]; then
            echo "[driver] worker-wait cap (${cap}s) reached with a sentinel still live — resuming anyway" | tee -a "$LOG"
            WAITED=$((SECONDS - wait_start)); WAIT_CAPPED=1
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

# Startup wait: a previous driver may have died while a detached worker was
# still in flight (its sentinel survives). Wait it out once before the first
# turn; from then on the post-turn wait inside the loop is the only wait, so
# each cycle's worker time is counted exactly once by the fast-cycle guard.
wait_for_workers

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
        run_turn codex exec "${CODEX_ARGS[@]}" -- "$FIRST_PROMPT"
        SID="$(find_sid || true)"
        [ -z "$SID" ] && { echo "[driver] ERROR: no session recorded for this project after first turn" | tee -a "$LOG"; exit 1; }
        printf '%s\n' "$SID" > "$SID_CACHE"
    else
        run_turn codex exec resume "$SID" "${CODEX_ARGS[@]}" -- "$CONT_PROMPT"
    fi
    set -e
    # Absorb the post-turn worker wait into the turn's duration signal BEFORE
    # judging the turn: a sub-60s no-commit turn that handed off a detached
    # worker which then ran for minutes did real work — the wait is part of
    # that turn's cycle. Without this, strike 5 can land on a legitimate
    # launch turn (observed live: a Gate 3 recovery re-check launch was the
    # 5th "fast" turn; the driver exited while its worker ran on). A spin loop
    # is unaffected: it launches nothing (or instant-failing workers), so its
    # wait is ~0 and dt stays sub-60. A wait that hit WORKER_WAIT_MAX with the
    # sentinel still live is NOT credited (WAIT_CAPPED): a wedged worker that
    # never finishes must feed the guard, not reset it — otherwise a hung
    # worker turns the ~5-strike bound into MAX_TURNS-many multi-hour waits.
    wait_for_workers
    if [ "$WAIT_CAPPED" = "1" ]; then
        dt=$((SECONDS - t0 - WAITED))
    else
        dt=$((SECONDS - t0))   # measured after the wait, so a worker's runtime counts as this turn's work
    fi
    head_after="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true)"
    # Two ceilings on short CYCLES (dt = the turn plus the post-turn wait for
    # any detached worker it launched — see the wait_for_workers call above),
    # because a healthy turn is often itself <60s (it commits its stage
    # artifact and hands off to a detached worker), so raw turn time alone
    # false-positives:
    #   fast_nocommit — short cycle AND HEAD unchanged. A model producing and
    #     committing NOTHING whose workers (if any) also end instantly is
    #     wedged, refusing, or poll-spinning on a blocked external source;
    #     trip quickly (5). A launch turn whose worker actually runs resets
    #     via dt; a collect-and-commit turn resets via HEAD.
    #   fast_any — short cycle regardless of commits. Backstop against a
    #     fail-retry loop that commits churn every turn (e.g. a WORKER FAILED
    #     notice or a retry-count bump), which advances HEAD and would
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
        echo "[driver] 5 consecutive sub-60s cycles (turn + worker wait) with no new commit — model appears stuck, refusing, or poll-spinning; stopping to avoid burning tokens. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    if [ "$fast_any" -ge "${FAST_TURN_CEILING:-60}" ]; then
        echo "[driver] ${FAST_TURN_CEILING:-60} consecutive sub-60s cycles (even with commits) — abnormal churn; stopping to bound token burn. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    sleep 3
done
