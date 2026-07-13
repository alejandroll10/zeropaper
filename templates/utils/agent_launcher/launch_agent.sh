#!/usr/bin/env bash
# Launch a pipeline subagent as an isolated `codex exec` worker.
#
# WHY THIS EXISTS: codex's built-in `spawn_agent` tool (as of codex-cli 0.144.1)
# exposes only {fork_turns, message, task_name}. It cannot select a role from
# `.codex/agents/*.toml`, cannot set the per-agent model or reasoning effort, and
# defaults `fork_turns="all"` — the child inherits the orchestrator's ENTIRE
# conversation. That silently breaks the evaluators whose whole value is a fresh,
# unanchored read (referee "runs fresh with no knowledge of previous reports";
# scorer-freeform / referee-freeform "neither sees the other's output"). Codex
# discovers and parses our agent TOMLs (a malformed one warns at startup) but
# gives no way to pick one, so the `model` / `model_reasoning_effort` we pin per
# agent never take effect via `spawn_agent`.
#
# This launcher reads the agent's own `.toml` and runs a fresh worker with the
# pinned model + effort, no orchestrator context (`project_doc_max_bytes=0`
# suppresses the project's AGENTS.md so the worker does not think it IS the
# orchestrator), and its own tool sandbox. A `codex exec` process starts a clean
# session by construction — it does not inherit the caller's turns — so evaluator
# independence is restored as a side effect.
#
# Usage:
#   launch_agent.sh <agent-id> <task-or-taskfile> [--sandbox MODE]
#                    [--output FILE] [--add-dir DIR]... [--model MODEL]
#                    [--parallel] [--force]
#
#   <agent-id>          basename of a file in .codex/agents/ (e.g. "scorer")
#   <task-or-taskfile>  the task prompt; if it names an existing file, that
#                       file's contents are used as the task text
#   --sandbox MODE      read-only | workspace-write (default) | danger-full-access
#                       (an agent TOML `sandbox_mode`, if present, is the default;
#                       forced to danger-full-access when nested — see below)
#   --output FILE       where to write the worker's final message
#                       (default: process_log/agent_runs/<agent-id>-<UTC>.md)
#   --add-dir DIR       grant the worker write access to an extra dir (repeatable)
#   --model MODEL       override the TOML's pinned model (rarely needed)
#   --parallel          deliberate same-agent fan-out (e.g. the gate steps that
#                       run K novelty-checkers / idea-prototypers concurrently):
#                       skips the duplicate-launch refusal and uses a
#                       per-invocation sentinel so instances don't collide.
#                       Give each instance its own --output.
#   --force             launch even though an earlier run of this agent appears
#                       to still be in flight (duplicate-launch sentinel) — only
#                       after verifying that run is dead. Unlike --parallel this
#                       REPLACES the stale sentinel. (Narrow race, accepted: if
#                       the earlier worker was in fact alive, its exit removes
#                       the shared sentinel out from under the forced run.)
#                       Under --parallel, --force is a no-op — parallel mode has
#                       no refusal path to override.
#
# The launcher is FIRE-AND-FORGET: it exits 0 as soon as the worker is detached,
# BEFORE the worker finishes. The worker's own success/failure is therefore NOT
# the launcher's exit code — it is surfaced in the OUTPUT file: on success the
# worker writes its result there; on failure the wrapper writes a "WORKER FAILED
# (rc=N)" notice + log tail there (so a caller polling OUTPUT sees the failure
# instead of waiting forever). The caller must poll OUTPUT, never read an exit
# code, for the result. (Nonzero worker rc still usually means the model was
# unavailable — codex does NOT downgrade; see the model-fallback note in
# CLAUDE.md, only the Claude runtime is probed/remapped at setup — or the task
# failed.) Exit 3 (launcher's own, before detach): duplicate-launch sentinel
# refused the launch.
#
# The worker is DETACHED into its own process session, which is what makes the
# fire-and-forget safe: if the caller (an orchestrator whose turn ends) is killed
# after the launcher returns, the worker keeps running, still writes its output
# file, and still cleans up its sentinel — a resumed session reconnects via the
# sentinel's recorded output path. See the detachment comment above the worker
# invocation.
#
# NESTED-SANDBOX BEHAVIOR: when this launcher is itself invoked from inside a
# codex sandbox (the normal case — the pipeline orchestrator's exec tool runs it
# under codex's deny-by-default Seatbelt profile, and sets CODEX_SANDBOX in the
# child env), the worker CANNOT apply an inner sandbox of its own: macOS refuses
# the second sandbox_apply, so every apply_patch call (both the native patch tool
# and the `apply_patch` shell helper) fails with `sandbox_apply: Operation not
# permitted` / "Failed to write file", while plain exec commands still run (codex
# skips re-sandboxing exec when it detects it is already sandboxed). Observed in
# production and reproduced 2026-07-12 on codex-cli 0.144.1. The launcher
# therefore detects nesting via $CODEX_SANDBOX and runs the worker with
# `--sandbox danger-full-access`: the ORCHESTRATOR'S outer sandbox still confines
# the whole worker process tree (verified — a $HOME write from such a worker is
# still denied), so the security boundary is unchanged; the worker just stops
# trying to stack a second, broken sandbox inside it. Consequence: per-worker
# sandbox tiering (`--sandbox read-only`, TOML `sandbox_mode`) is unavailable
# when nested — it was already unenforceable (nested exec runs under the outer
# sandbox only); the override just makes that visible and fixes apply_patch.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# code/utils/agent_launcher/ -> project root is three levels up.
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
AGENTS_DIR="$PROJECT_ROOT/.codex/agents"

AGENT_ID="${1:?Usage: launch_agent.sh <agent-id> <task-or-taskfile> [options]}"
TASK_ARG="${2:?Usage: launch_agent.sh <agent-id> <task-or-taskfile> [options]}"
shift 2

SANDBOX=""            # empty => use TOML sandbox_mode, else workspace-write
OUTPUT=""
MODEL_OVERRIDE=""
FORCE=""
PARALLEL=""
ADDDIR_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --sandbox)  SANDBOX="${2:?--sandbox needs a value}"; shift 2 ;;
        --output)   OUTPUT="${2:?--output needs a value}"; shift 2 ;;
        --model)    MODEL_OVERRIDE="${2:?--model needs a value}"; shift 2 ;;
        --add-dir)  ADDDIR_ARGS+=(--add-dir "${2:?--add-dir needs a value}"); shift 2 ;;
        --parallel) PARALLEL=1; shift ;;
        --force)    FORCE=1; shift ;;
        *) echo "ERROR: unknown option '$1'" >&2; exit 2 ;;
    esac
done

TOML="$AGENTS_DIR/$AGENT_ID.toml"
if [ ! -f "$TOML" ]; then
    echo "ERROR: no agent '$AGENT_ID' — expected $TOML" >&2
    echo "       available:" >&2
    ( cd "$AGENTS_DIR" 2>/dev/null && ls *.toml 2>/dev/null | sed 's/\.toml$//; s/^/         /' ) >&2 || true
    exit 1
fi

# Task can be inline text or a file path. Log which branch we took — a literal
# task that happens to name a file in the CWD is read as that file, and without
# this line the substitution would be invisible until someone read the worker's
# output and wondered why it did the wrong thing.
if [ -f "$TASK_ARG" ]; then
    TASK="$(cat "$TASK_ARG")"
    echo "[launch_agent] task read from file: $TASK_ARG"
else
    TASK="$TASK_ARG"
fi

# Scratch dir for this launch (instructions payload + no-spawn catalog), cleaned
# on any exit.
_scratch="$(mktemp -d "${TMPDIR:-/tmp}/launch_agent.XXXXXX")"
trap 'rm -rf "$_scratch"' EXIT

# Parse the TOML with tomllib (Python >= 3.11). The codex assembler writes the
# instructions as a multiline literal; a hand-rolled shell/sed parser would
# mangle them, so use a real TOML reader. `developer_instructions` can be huge
# and multiline (and bash cannot hold NUL bytes), so write it to a temp file and
# return the scalars as shell-quoted assignments to `eval`.
_instr_file="$_scratch/instr"
eval "$(python3 - "$TOML" "$_instr_file" <<'PY'
import sys, tomllib, shlex
d = tomllib.load(open(sys.argv[1], "rb"))
open(sys.argv[2], "w").write(d.get("developer_instructions", ""))
print("MODEL="        + shlex.quote(str(d.get("model", ""))))
print("EFFORT="       + shlex.quote(str(d.get("model_reasoning_effort", "medium"))))
print("TOML_SANDBOX=" + shlex.quote(str(d.get("sandbox_mode", ""))))
PY
)"
INSTRUCTIONS="$(cat "$_instr_file")"

# A worker is a leaf: it does the task itself and returns. It must not fan out
# into sub-agents (runaway depth/cost, and — for evaluators — a spawned child
# that inherited context is no longer an independent read). The catalog patch
# below removes the native spawn tool entirely; this line is the belt to that
# suspenders — it also covers the fallback where the catalog can't be built, and
# is true for every agent regardless.
INSTRUCTIONS="$INSTRUCTIONS

## Execution boundary
You are a single leaf worker. Do NOT spawn, delegate to, launch, or hand off to
other agents or sub-agents (no spawn_agent, no launch_agent.sh, no codex exec).
Complete the task yourself with the tools you have and return your result."

[ -n "$MODEL_OVERRIDE" ] && MODEL="$MODEL_OVERRIDE"
if [ -z "$MODEL" ]; then
    echo "ERROR: $TOML has no 'model' — cannot launch" >&2
    exit 1
fi
# Sandbox precedence: --sandbox flag > TOML sandbox_mode > workspace-write.
# workspace-write is the default BY DESIGN: pipeline agents are meant to write
# and run (they produce verdict files and drafts, and run sympy/latex/python) —
# matching how the agents are defined (their Claude `tools` include Write, and
# most include Bash). We deliberately do NOT lock agents to read-only. A caller
# can still pass `--sandbox read-only` for a one-off pure-read task, or an agent
# can pin `sandbox_mode` in its own TOML, but there is no read-only-by-default
# tiering. (Fidelity note: codex's sandbox is filesystem-scoped, not per-tool
# like Claude's `tools` list, so a worker may have shell access even if its
# Claude def omits Bash — that is more permissive, not less, and is intended.)
[ -z "$SANDBOX" ] && SANDBOX="${TOML_SANDBOX:-workspace-write}"

# Nested-sandbox guard (see header). codex sets CODEX_SANDBOX in every process
# it sandboxes, so its presence means we are running inside the orchestrator's
# sandbox and a second, inner sandbox cannot be applied (apply_patch would fail
# with `sandbox_apply: Operation not permitted`). Run the worker sandbox-less
# and let the orchestrator's outer sandbox confine it — same boundary, working
# tools. Logged so a requested read-only tier that gets overridden is visible.
if [ -n "${CODEX_SANDBOX:-}" ] && [ "$SANDBOX" != "danger-full-access" ]; then
    echo "[launch_agent] nested inside a codex sandbox (CODEX_SANDBOX=$CODEX_SANDBOX):" \
         "overriding worker sandbox '$SANDBOX' -> danger-full-access." \
         "The caller's outer sandbox still confines this worker; inner sandboxes cannot be applied here."
    SANDBOX="danger-full-access"
fi

# Under workspace-write, mirror the Claude deploy's filesystem/network posture
# (.claude/settings.json allowWrite + open egress): workspace-write defaults to
# writable [workdir, /tmp, $TMPDIR] with network OFF, but pipeline workers write
# codex-math session state to ~/.codex and uv/matplotlib caches, and need egress
# (WRDS 127.0.0.1:23847, OpenAlex, web). Without these a worker silently cannot
# reach WRDS/OpenAlex or write its caches. codex expands ~ inside writable_roots
# (verified). These keys are no-ops unless the active sandbox is workspace-write,
# so they are harmless under --sandbox read-only / danger-full-access. Writes
# outside this set (e.g. rm in $HOME) stay blocked — the anti-destruction point.
#
# INTENTIONAL DIVERGENCE: templates/utils/codex_math/codex_common.sh has a
# counterpart array (CODEX_SANDBOX_WS_ARGS) that deliberately sets
# network_access=FALSE — codex-math workers are self-contained proof/numerics
# tasks with zero egress need (least-privilege). The writable_roots half is
# identical; the network half is not. Do NOT unify these two without reading why
# they differ (see that file's comment) — matching them would re-grant egress to
# the one call site that has no use for it.
# $PROJECT_ROOT/.git is included for the same reason the orchestrator's launch
# command carries it: codex hard-codes each root's top-level .git read-only, so
# a worker that commits (scribe) would die on index.lock without it. Only
# *enforced* when the launcher runs un-nested (nested workers run
# danger-full-access under the caller's outer sandbox — see the guard above);
# it makes the un-nested path behave the same. codex_common.sh's counterpart
# array deliberately omits it — codex-math workers never touch git.
# KNOWN EDGE (accepted): $PROJECT_ROOT is interpolated into a TOML array
# literal, so a project path containing a double quote or backslash would break
# this -c value's TOML parse — and unlike developer_instructions (where the
# raw-literal fallback is a string, the expected type) an array key has no
# graceful fallback. The same interpolation ships in the documented launch
# command (README/CLAUDE.md/setup.sh). Deploy paths are machine-generated and
# never carry those characters; do not name a project with `"` or `\`.
SANDBOX_WS_ARGS=(
    -c 'sandbox_workspace_write.network_access=true'
    -c "sandbox_workspace_write.writable_roots=[\"~/.codex\",\"~/.cache\",\"~/Library/Caches\",\"~/.matplotlib\",\"$PROJECT_ROOT/.git\"]"
)

if [ -z "$OUTPUT" ]; then
    _stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    OUTPUT="$PROJECT_ROOT/process_log/agent_runs/${AGENT_ID}-${_stamp}.md"
fi
mkdir -p "$(dirname "$OUTPUT")"

# Duplicate-launch sentinel. A worker runs for MINUTES; an orchestrator whose
# exec call yields early (empty output) must NOT conclude the launch failed and
# relaunch — that burned 4x tokens on identical literature scouts in production.
# The sentinel makes the accidental second launch fail loudly instead of
# silently doubling. Deliberate same-agent fan-out (the gate steps that run K
# novelty-checkers / idea-prototypers concurrently) is expressed with
# --parallel, which uses a per-invocation (pid-suffixed) sentinel and skips the
# refusal — "duplicate" vs "fan-out" is intent, so the caller states it.
# Sentinels are removed on normal exit; a hard-killed launcher (SIGKILL) leaves
# one behind, so the refusal message tells the caller how to verify + override.
_sentinel_dir="$PROJECT_ROOT/process_log/agent_runs"
mkdir -p "$_sentinel_dir"
if [ -n "$PARALLEL" ]; then
    _sentinel="$_sentinel_dir/.${AGENT_ID}.$$.running"
else
    _sentinel="$_sentinel_dir/.${AGENT_ID}.running"
    if [ -e "$_sentinel" ] && [ -z "$FORCE" ]; then
        echo "ERROR: an earlier launch of '$AGENT_ID' appears to still be running:" >&2
        sed 's/^/       /' "$_sentinel" >&2 || true
        echo "       A launched worker keeps running in the background even when your exec call" >&2
        echo "       returned early with no output — it has NOT failed. Wait and poll for the" >&2
        echo "       output file recorded above instead of relaunching." >&2
        echo "       If that output file now exists, the earlier run finished (stale sentinel)." >&2
        echo "       For a deliberate concurrent fan-out of this agent, re-run with --parallel." >&2
        echo "       Only if you have confirmed the earlier worker is gone (output file never" >&2
        echo "       appeared and no codex exec process remains): rm '$_sentinel' or re-run with --force." >&2
        exit 3
    fi
fi
printf 'started=%s pid=%s output=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$" "$OUTPUT" > "$_sentinel"
trap 'rm -rf "$_scratch"; rm -f "$_sentinel"' EXIT

# Build a no-spawn model catalog so the worker physically cannot fan out. codex
# ties the native multi-agent tool surface (spawn_agent + the "you're in a team"
# framing) to each model's `multi_agent_version` in the catalog — a feature flag
# can't turn it off (the catalog wins; see upstream openai/codex#31097). We take
# the live catalog (`codex debug models`, cache-backed and ~instant) and blank
# that field for every model, then hand the worker the patched copy. Any value
# other than v1/v2 drops the tool entirely (verified). Best-effort: if codex
# can't dump the catalog (offline/auth), we skip it and lean on the leaf directive
# above plus codex's own "don't spawn unless instructed" default.
_catalog_args=()
if codex debug models 2>/dev/null \
     | python3 -c 'import json,sys; d=json.load(sys.stdin); [m.__setitem__("multi_agent_version","none") for m in d.get("models",[])]; json.dump(d, open(sys.argv[1],"w"))' \
       "$_scratch/catalog.json" 2>/dev/null \
   && [ -s "$_scratch/catalog.json" ]; then
    _catalog_args=(-c "model_catalog_json=\"$_scratch/catalog.json\"")
else
    echo "[launch_agent] warning: could not build no-spawn catalog; worker keeps native multi-agent tools (leaf directive still applies)" >&2
fi

echo "[launch_agent] $AGENT_ID  model=$MODEL  effort=$EFFORT  sandbox=$SANDBOX"
echo "[launch_agent] final message -> $OUTPUT"

# The agent's own prompt goes in via `developer_instructions` (the developer
# channel, layered on top of codex's base instructions) — the same place a
# native codex role would land it — so the worker *is* the agent, rather than
# reading its role as a wall of user text. The concrete task is the user turn.
# The `-c value` is parsed as TOML and, failing that (our bodies are prose, not
# valid TOML), used as a raw literal — which preserves backslashes (LaTeX in
# paper-writer/math agents) and embedded quotes verbatim; verified on the 31KB
# paper-writer body (all 37 backslashes intact). CONSTRAINT ON AGENT BODIES: a
# body must not *open* with a token TOML would parse successfully (`true`/`false`,
# a digit, `[`, `{`, or a leading `"`), or codex would coerce the value's type
# instead of taking it as a literal string. Every current body opens with prose
# ("You …"); keep it that way.
#
# `--` before "$TASK" stops codex's own CLI parser from treating a task that
# starts with `-` (e.g. a markdown bullet "- Verify …") as a flag — without it,
# such a task aborts with a clap usage error before any model call.
#
# `project_doc_max_bytes=0` suppresses the orchestrator's AGENTS.md so the worker
# runs on its own instructions, not the pipeline driver's. `-C` roots it at the
# project so it can read/write output/ under the chosen sandbox.
#
# DETACHMENT: the worker runs in its OWN process session (python
# start_new_session=True — macOS ships no setsid binary), via a wrapper script
# that owns the sentinel lifecycle. Why: when this launcher is run by a codex
# orchestrator and that orchestrator's turn ends, codex SIGKILLs the exec
# process group — verified 2026-07-12: a plain nohup'd child died with the
# parent, a start_new_session child survived and finished. With detachment, a
# turn-end mid-launch kills the launcher but NOT the worker: the worker still
# writes its output file and the wrapper still removes the sentinel, so a
# resumed orchestrator turn (or the launch.sh driver's next `codex exec
# resume`) reconnects by polling the output path recorded in the sentinel.
# The launcher is FIRE-AND-FORGET: once the worker is detached it returns
# immediately rather than blocking for the result, because the headless codex
# driver caps a silent long-running exec after ~10s and would reap a blocking
# launcher as `UnknownProcessId` (fuller note at the return below). The scratch
# dir therefore always outlives the launcher and leaks until OS cleanup (the
# still-running wrapper is writing worker.log/rc in there; $TMPDIR is
# OS-cleaned; the sentinel and output file are what matter).
_worker_cmd=(
    codex exec
    --skip-git-repo-check
    -C "$PROJECT_ROOT"
    -m "$MODEL"
    -s "$SANDBOX"
    -c "model_reasoning_effort=\"$EFFORT\""
    -c 'project_doc_max_bytes=0'
    "${SANDBOX_WS_ARGS[@]}"
    -c "developer_instructions=$INSTRUCTIONS"
    ${_catalog_args[@]+"${_catalog_args[@]}"}
    ${ADDDIR_ARGS[@]+"${ADDDIR_ARGS[@]}"}
    -o "$OUTPUT"
    -- "$TASK"
)
# Clear any stale content at $OUTPUT from a PRIOR run at this same path before
# the worker starts. The pipeline deliberately reuses version-numbered output
# paths across attempts (see the stage docs: "attempts overwrite prior files").
# Fire-and-forget uses "$OUTPUT non-empty" as the sole success signal, and the
# wrapper only writes a WORKER FAILED notice when $OUTPUT is empty — so without
# this clear, a fresh attempt that fails before writing anything would leave the
# previous attempt's result sitting there and be mistaken for this attempt's
# success, with no failure signal anywhere. Runs AFTER the duplicate-launch
# sentinel check above, so a refused duplicate never clears an in-flight run's
# output; the default (timestamped) path never pre-exists, so this is a no-op
# there and only matters for an explicit reused --output.
rm -f "$OUTPUT"
{
    printf '#!/bin/bash\n'
    printf '%q ' "${_worker_cmd[@]}"
    printf ' </dev/null > %q 2>&1\n' "$_scratch/worker.log"
    printf '_rc=$?\n'
    printf 'echo "$_rc" > %q\n' "$_scratch/rc"
    # Fire-and-forget means the caller learns the outcome only by polling
    # $OUTPUT. So if the worker failed and wrote no result of its own, surface
    # the reason INTO $OUTPUT (rc + log tail). Without this a failed worker is
    # indistinguishable from a slow one — the file simply never appears, the
    # orchestrator waits, then relaunches blind. `[ ! -s ]` guards a worker that
    # did produce output before a nonzero exit (don't clobber a real result).
    printf 'if [ "$_rc" -ne 0 ] && [ ! -s %q ]; then { echo "[launch_agent] WORKER FAILED (rc=$_rc) — task did not complete; log tail:"; tail -n 40 %q; } > %q; fi\n' \
        "$OUTPUT" "$_scratch/worker.log" "$OUTPUT"
    # Sentinel removal is LAST — after $OUTPUT is settled — so a supervisor that
    # keys on "sentinel gone" never observes it before the result is in place.
    printf 'rm -f %q\n' "$_sentinel"
} > "$_scratch/run_worker.sh"
chmod +x "$_scratch/run_worker.sh"

# Detach. From here the wrapper owns the sentinel; the launcher returns right
# after (fire-and-forget), so hand cleanup ownership over (early-exit paths
# above still had the full trap). The wrapper's pid + start time are appended to the sentinel so a
# supervisor (launch.sh's wait_for_workers) can distinguish "worker still
# running" from "worker AND wrapper externally killed, sentinel orphaned, no
# output ever coming" — without this, an orphaned sentinel parks the driver
# until its wait cap. The [ -f ] guard: a wrapper that finishes instantly has
# already removed the sentinel; appending would resurrect it as a permanent
# orphan (microscopic TOCTOU window between test and append — accepted).
# DEVNULL stdio is load-bearing: without it the wrapper inherits python's
# stdout — which is THIS command substitution's pipe — and $() reads to EOF,
# i.e. blocks until the wrapper exits. That would defeat fire-and-forget
# entirely: the launcher would hang here for the worker's whole life, the pid
# append would never fire (the wrapper has already cleaned the sentinel), and
# the EXIT trap would stay armed the whole time. The wrapper redirects
# everything per-command anyway, so DEVNULL loses nothing.
_wrapper_pid="$(python3 -c 'import subprocess, sys; print(subprocess.Popen([sys.argv[1]], start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).pid)' \
    "$_scratch/run_worker.sh")"
_wrapper_lstart="$(ps -o lstart= -p "$_wrapper_pid" 2>/dev/null || true)"
if [ -f "$_sentinel" ]; then
    printf 'wrapper_pid=%s wrapper_lstart=%s\n' "$_wrapper_pid" "$_wrapper_lstart" >> "$_sentinel"
fi
trap - EXIT

# FIRE-AND-FORGET. The worker now runs detached in its own session; it writes
# $OUTPUT (or, on failure, a failure notice there) and removes the sentinel when
# it finishes. We deliberately do NOT block waiting for it.
#
# Why: under the headless codex driver (`codex exec resume`), the exec tool caps
# a silent, long-running command after ~10s and reaps the launcher — surfacing
# as `UnknownProcessId`. A blocking wait can therefore never win, and worse, the
# reap races the detached worker: sometimes codex returns benignly (the model
# sees an early empty yield and polls, which is correct), sometimes as a hard
# error the model reads as "the launch failed" — stalling the pipeline and
# tripping the driver's stuck-model guard on a launch that actually succeeded.
# (Observed 2026-07-12: a Gate 0 run halted this way while its worker went on to
# finish one minute later.) Returning now — well under the cap — makes every
# launch take the clean early-yield path the rest of the system already assumes:
# this launcher's own duplicate-launch sentinel and launch.sh's wait_for_workers
# were both built for "exec yields early; the worker keeps running; poll the
# output file." The caller polls $OUTPUT; the driver blocks between turns in
# wait_for_workers until the sentinel clears.
echo "[launch_agent] $AGENT_ID launched detached (wrapper pid $_wrapper_pid) — NOT done yet."
echo "[launch_agent] Its result is written only when the worker finishes; poll for it at:"
echo "               $OUTPUT"
echo "[launch_agent] Do not relaunch while the sentinel is present ($_sentinel)."
exit 0
