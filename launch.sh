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
#   ./launch.sh opencode            # persistent-server OpenCode driver
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
    # Keep the helper/server Basic-auth identity stable even if the caller has
    # a different global OpenCode server username configured.
    export OPENCODE_SERVER_USERNAME=opencode
    # OpenCode omits the `background` field from the task schema when this
    # experimental capability is unavailable. Keeping the flag at the process
    # boundary therefore degrades safely: capable versions expose native
    # background tasks; older versions continue to offer foreground task calls.
    export OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS=true
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
    OC_SERVER_LOG="$ROOT/process_log/opencode-server.log"
    OC_SERVER_PID_FILE="$ROOT/process_log/.opencode_server_pid"
    OC_SERVER_START_FILE="$ROOT/process_log/.opencode_server_start"
    OC_SERVER_IDENTITY_FILE="$ROOT/process_log/.opencode_server_identity"
    OC_SERVER_STARTING_FILE="$ROOT/process_log/.opencode_server_starting"
    OC_SERVER_URL_FILE="$ROOT/process_log/.opencode_server_url"
    OC_SERVER_PASSWORD_FILE="$ROOT/process_log/.opencode_server_password"
    OC_DRIVER_LOCK="$ROOT/process_log/.opencode_driver_lock"
    OC_PENDING_CHILDREN_FILE="$ROOT/process_log/.opencode_background_children"
    OC_PENDING_PARENT_FILE="$ROOT/process_log/.opencode_background_parent"
    OC_BACKGROUND_BASELINE_FILE="$ROOT/process_log/.opencode_background_baseline"
    OC_BACKGROUND_TRANSITION_FILE="$ROOT/process_log/.opencode_background_transition"
    OC_RECOVERY_INTENT_FILE="$ROOT/process_log/.opencode_recovery_intent"
    OC_PARENT_SERVER_EPOCH_FILE="$ROOT/process_log/.opencode_parent_server_epoch"
    OC_UNRESOLVED_SESSION_FILE="$ROOT/process_log/.opencode_unresolved_session"
    OC_HELPER="$ROOT/code/utils/opencode_driver.py"
    [ -f "$OC_HELPER" ] || OC_HELPER="$ROOT/templates/utils/opencode_driver.py"
    [ -f "$OC_HELPER" ] || { echo "ERROR: missing OpenCode driver helper" >&2; exit 1; }
    OPENCODE_TURN_TIMEOUT="${OPENCODE_TURN_TIMEOUT:-3540}"
    OPENCODE_BACKGROUND_TIMEOUT="${OPENCODE_BACKGROUND_TIMEOUT:-3540}"
    OPENCODE_ABORT_TIMEOUT="${OPENCODE_ABORT_TIMEOUT:-30}"
    OPENCODE_KILL_GRACE="${OPENCODE_KILL_GRACE:-10}"
    OPENCODE_LOOP_DELAY="${OPENCODE_LOOP_DELAY:-3}"
    OC_FIRST='Run the pipeline. You are unattended: never ask the user anything; decide from AGENTS.md and the pipeline artifacts. Use native .opencode task agents. When the task schema offers background, dispatch independent long-running agents with background=true and continue non-overlapping work; otherwise use foreground tasks. Every agent must checkpoint to its explicit artifact path.'
    OC_CONT='Continue the pipeline from process_log/pipeline_state.json. You are unattended: never ask the user anything. Use native .opencode task agents; use background=true for independent long-running work when the schema offers it, foreground otherwise. Reconcile completed child artifacts before advancing a gate, and keep working until this turn has made durable progress.'
    OC_RECOVER=' The OpenCode server was restarted, so any in-memory background jobs from its prior instance were interrupted. Inspect this session child history and the explicit artifact paths, then resume each unfinished child with its task_id or relaunch it exactly once. Never mistake a missing completion notification for successful completion.'
    OC_CANCEL_RECOVER=' The prior turn or background wait timed out and its session tree was cancelled to confirmed quiescence. Inspect child transcripts and explicit artifact paths, then resume unfinished work with its task_id or relaunch it exactly once.'
    OC_SERVER_PID=""
    OC_SERVER_START=""
    OC_SERVER_URL=""
    OPENCODE_SERVER_PASSWORD=""
    OC_DRIVER_PID="$$"
    OC_DRIVER_START="$(ps -o lstart= -p "$$" 2>/dev/null || true)"
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
        [ -n "$OC_DRIVER_START" ] || { echo "ERROR: cannot establish OpenCode driver process identity" >&2; return 1; }
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
        ready="$(mktemp "$ROOT/process_log/.opencode-lock-ready.XXXXXX")"
        python3 "$OC_HELPER" lock-hold --path "$OC_DRIVER_LOCK" --parent "$OC_DRIVER_PID" --ready "$ready" &
        OC_LOCK_KEEPER_PID=$!
        for attempt in $(seq 1 100); do
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
        starting_tmp="$(mktemp "$ROOT/process_log/.opencode-server-starting.XXXXXX")"
        printf '%s\n' pending > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_SERVER_STARTING_FILE"
        {
            python3 -c 'import os,sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' \
                opencode serve --hostname 127.0.0.1 --port 0 </dev/null >> "$OC_SERVER_LOG" 2>&1 &
            OC_SERVER_PID=$!
        }
        starting_tmp="$(mktemp "$ROOT/process_log/.opencode-server-starting.XXXXXX")"
        printf '%s\n' "$OC_SERVER_PID" > "$starting_tmp"
        chmod 600 "$starting_tmp"
        mv "$starting_tmp" "$OC_SERVER_STARTING_FILE"
        OC_SERVER_START="$(ps -o lstart= -p "$OC_SERVER_PID" 2>/dev/null || true)"
        if [ -z "$OC_SERVER_START" ]; then
            oc_reap_starting_server || echo "ERROR: failed to reap incomplete OpenCode server; startup marker retained" >&2
            echo "ERROR: OpenCode server failed to start" >&2
            return 1
        fi
        identity_tmp="$(mktemp "$ROOT/process_log/.opencode-server-identity.XXXXXX")"
        printf '%s\n%s\n' "$OC_SERVER_PID" "$OC_SERVER_START" > "$identity_tmp"
        chmod 600 "$identity_tmp"
        mv "$identity_tmp" "$OC_SERVER_IDENTITY_FILE"
        # Compatibility/observability mirrors; identity_file is authoritative.
        printf '%s\n' "$OC_SERVER_PID" > "$OC_SERVER_PID_FILE"
        printf '%s\n' "$OC_SERVER_START" > "$OC_SERVER_START_FILE"
        password_tmp="$(mktemp "$ROOT/process_log/.opencode-server-password.XXXXXX")"
        printf '%s\n' "$OPENCODE_SERVER_PASSWORD" > "$password_tmp"
        chmod 600 "$password_tmp"
        mv "$password_tmp" "$OC_SERVER_PASSWORD_FILE"
        for attempt in $(seq 1 100); do
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
        sessions_tmp="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode-sessions.XXXXXX")"
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
        after_file="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode-sessions.XXXXXX")"
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
        printf 'An OpenCode turn created or may have created a parent session whose ID could not be determined.\nReason: %s\nInspect sessions with ./launch.sh opencode --once, write the chosen ID to process_log/.opencode_session_id, then remove this marker.\n' \
            "$1" > "$OC_UNRESOLVED_SESSION_FILE"
        chmod 600 "$OC_UNRESOLVED_SESSION_FILE"
    }
    oc_mark_first_turn_in_progress() {
        local marker_tmp
        marker_tmp="$(mktemp "$ROOT/process_log/.opencode-unresolved.XXXXXX")"
        printf 'An OpenCode first turn is in progress and may create a parent session.\nIf interrupted, inspect sessions with ./launch.sh opencode --once before removing this marker.\n' > "$marker_tmp"
        chmod 600 "$marker_tmp"
        mv "$marker_tmp" "$OC_UNRESOLVED_SESSION_FILE"
    }
    oc_cache_sid() {
        local sid_tmp
        sid_tmp="$(mktemp "$ROOT/process_log/.opencode-session.XXXXXX")"
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
        epoch_tmp="$(mktemp "$ROOT/process_log/.opencode-parent-epoch.XXXXXX")"
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
        transition_tmp="$(mktemp "$ROOT/process_log/.opencode-transition.XXXXXX")"
        printf '%s %s\n' "$OC_SID" "$kind" > "$transition_tmp"
        chmod 600 "$transition_tmp"
        mv "$transition_tmp" "$OC_BACKGROUND_TRANSITION_FILE"
    }
    oc_set_background_baseline() {
        local count epoch baseline_tmp
        count="$(oc_server_api cursor --session "$OC_SID" 2>/dev/null)" || return 1
        [[ "$count" =~ ^[0-9]+$ ]] || return 1
        epoch="$(oc_server_epoch)" || return 1
        baseline_tmp="$(mktemp "$ROOT/process_log/.opencode-baseline.XXXXXX")"
        printf '%s %s %s\n' "$OC_SID" "$epoch" "$count" > "$baseline_tmp"
        chmod 600 "$baseline_tmp"
        mv "$baseline_tmp" "$OC_BACKGROUND_BASELINE_FILE"
        oc_clear_pending_children
    }
    oc_set_recovery_intent() { # $1 = restart or cancel
        local kind="$1" token intent_tmp
        case "$kind" in restart|cancel) ;; *) return 1 ;; esac
        token="zp-recovery-$(python3 -c 'import secrets; print(secrets.token_hex(16))')" || return 1
        intent_tmp="$(mktemp "$ROOT/process_log/.opencode-recovery.XXXXXX")"
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
        pending_tmp="$(mktemp "$ROOT/process_log/.opencode-pending.XXXXXX")"
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
        kill -"$1" -- "-$OC_ACTIVE_PGID" 2>/dev/null || true
    }
    oc_turn_group_alive() {
        [ -n "$OC_ACTIVE_PGID" ] && kill -0 -- "-$OC_ACTIVE_PGID" 2>/dev/null
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
    trap 'oc_signal_cleanup; trap - EXIT; exit 130' INT TERM
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
        oc_events="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode.XXXXXX")"
        oc_sessions_before=""
        oc_sessions_before_valid=0
        if [ -z "$OC_SID" ]; then
            oc_sessions_before="$(mktemp "${TMPDIR:-/tmp}/zeropaper-opencode-sessions.XXXXXX")"
            if oc_server_api list-local --root "$ROOT" > "$oc_sessions_before" 2>/dev/null; then
                oc_sessions_before_valid=1
            fi
        fi
        oc_before="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || true):$(oc_worktree_hash):$(cksum "$OC_STATE" 2>/dev/null || true)"
        oc_t0=$SECONDS
        oc_event_sid_rc=0
        set +e
        if [ -n "$OC_SID" ]; then
            run_opencode_turn opencode run --attach "$OC_SERVER_URL" --session "$OC_SID" --model opencode/deepseek-v4-flash --format json "$OC_CONT$oc_recovery_note"
            oc_rc=$?
        else
            oc_mark_first_turn_in_progress
            run_opencode_turn opencode run --attach "$OC_SERVER_URL" --model opencode/deepseek-v4-flash --format json "$OC_FIRST$oc_recovery_note"
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
# where "live" is decided by probing the recorded wrapper pid — NOT by whether
# the output file has content, which is false for every worker that streams
# its report incrementally. WORKER_WAIT_MAX caps the wait so a
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
    local w_pid w_lstart w_dead w_now out_f out_mtime out_now out_age
    WAITED=0; WAIT_CAPPED=0
    while :; do
        pending=0
        for s in "$ROOT"/process_log/agent_runs/.*.running; do
            [ -e "$s" ] || continue
            # || true on every read of "$s": the wrapper can rm the sentinel
            # between our [ -e ] test and the read; a failed assignment under
            # set -e would kill the whole driver on that poll race.
            out="$(sed -n 's/.*output=//p' "$s" 2>/dev/null | head -1 || true)"
            w_pid="$(sed -n 's/.*wrapper_pid=\([0-9][0-9]*\).*/\1/p' "$s" 2>/dev/null | head -1 || true)"
            w_lstart="$(sed -n 's/.*wrapper_lstart=\(.*\)$/\1/p' "$s" 2>/dev/null | head -1 || true)"
            # LIVENESS DECIDES; output content only breaks ties. A live
            # wrapper means the worker is still running EVEN IF its output
            # file already holds bytes: several agents (the novelty-checker
            # most visibly) STREAM their report as they go, so "non-empty" is
            # not "finished". Judging by file content first — as this did
            # before — silently unblocked the wait on every such worker: the
            # driver re-prompted instantly, the orchestrator saw the live
            # sentinel and correctly refused to relaunch or route a partial
            # report, and the resulting ~15s no-op turns tripped the
            # fast-cycle guard. Two long runs died that way with their worker
            # healthy and minutes from done.
            # kill -0 is the primary probe (signal-based — works even though
            # macOS ps/pgrep need sysmond and return NOTHING from inside
            # sandboxes, which is also why the recorded lstart may be empty:
            # the launcher runs inside the orchestrator's sandbox). lstart is
            # only a secondary pid-reuse guard when both sides captured it.
            if [ -n "$w_pid" ]; then
                w_dead=""
                if ! kill -0 "$w_pid" 2>/dev/null; then
                    w_dead=1
                elif [ -n "$w_lstart" ]; then
                    w_now="$(ps -o lstart= -p "$w_pid" 2>/dev/null || true)"
                    [ -n "$w_now" ] && [ "$w_now" != "$w_lstart" ] && w_dead=1  # pid reused
                fi
                if [ -z "$w_dead" ]; then
                    pending=1
                    continue
                fi
                # Wrapper is gone — exited before rm'ing the sentinel, killed,
                # or its pid now belongs to something else. Either way the
                # recorded worker is no longer running, so the sentinel now
                # lies, and leaving it parks the ORCHESTRATOR too — its prompt
                # reads a live sentinel as poll-don't-relaunch, so it will
                # neither route a finished report nor relaunch a lost worker.
                # Clear it; the next turn routes on the output file's presence.
                if [ -n "$out" ] && { [ -s "$out" ] || [ -s "$ROOT/$out" ]; }; then
                    echo "[driver] sentinel $(basename "$s") outlived its worker and the output exists — clearing it so the orchestrator can route the result" | tee -a "$LOG"
                else
                    echo "[driver] sentinel $(basename "$s") references a dead worker with no output — clearing the orphan" | tee -a "$LOG"
                fi
                rm -f "$s"
                continue
            fi
            # Old-format sentinel (no wrapper_pid): no liveness probe exists,
            # so the file is all we have. Require non-empty AND untouched for
            # WORKER_STALE_MTIME before calling it finished — an incrementally
            # written report keeps its mtime moving, so mtime distinguishes
            # "still streaming" from "done" where mere non-emptiness cannot.
            if [ -n "$out" ]; then
                out_f=""
                [ -s "$out" ] && out_f="$out"
                [ -z "$out_f" ] && [ -s "$ROOT/$out" ] && out_f="$ROOT/$out"
                if [ -n "$out_f" ]; then
                    # BSD (macOS) then GNU. Both probes are digit-validated
                    # rather than trusted: GNU `stat -f` is filesystem mode
                    # with a DIFFERENT format-sequence set, and an unknown
                    # sequence there can echo back literally instead of
                    # failing — feeding "%m" into $(( )) would be a fatal
                    # arithmetic syntax error under set -e, killing a driver
                    # that should merely have kept waiting. Same reason `date`
                    # is captured with || true and validated: every command
                    # substitution in this loop must degrade to "keep
                    # waiting", never to a dead driver.
                    out_mtime="$(stat -f %m "$out_f" 2>/dev/null || true)"
                    case "$out_mtime" in ''|*[!0-9]*) out_mtime="$(stat -c %Y "$out_f" 2>/dev/null || true)" ;; esac
                    case "$out_mtime" in ''|*[!0-9]*) out_mtime="" ;; esac
                    out_now="$(date +%s 2>/dev/null || true)"
                    case "$out_now" in ''|*[!0-9]*) out_now="" ;; esac
                    if [ -n "$out_mtime" ] && [ -n "$out_now" ]; then
                        out_age=$(( out_now - out_mtime ))
                        if [ "$out_age" -ge "${WORKER_STALE_MTIME:-600}" ]; then
                            continue  # output complete and idle: worker is done, sentinel stale
                        fi
                    fi
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
        # A sentinel still present at abort time changes the diagnosis
        # entirely: the orchestrator was probably obeying poll-don't-relaunch
        # on a worker the wait loop judged finished, not refusing to work.
        # Say so — the bare message above sent one post-mortem hunting a
        # "stuck model" that was in fact doing exactly what it was told.
        for s in "$ROOT"/process_log/agent_runs/.*.running; do
            [ -e "$s" ] || continue
            # cat, not `tr … < "$s"`: a redirect whose file vanished between
            # the [ -e ] test and here fails at open time, and that message
            # escapes the command's own 2>/dev/null onto the terminal.
            echo "[driver]   NOTE: sentinel $(basename "$s") is still present at abort — $(cat "$s" 2>/dev/null | tr '\n' ' ' || true)" | tee -a "$LOG"
        done
        exit 1
    fi
    if [ "$fast_any" -ge "${FAST_TURN_CEILING:-60}" ]; then
        echo "[driver] ${FAST_TURN_CEILING:-60} consecutive sub-60s cycles (even with commits) — abnormal churn; stopping to bound token burn. Inspect $LOG." | tee -a "$LOG"
        exit 1
    fi
    sleep 3
done
