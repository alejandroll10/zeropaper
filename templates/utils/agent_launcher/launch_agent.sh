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
#
#   <agent-id>          basename of a file in .codex/agents/ (e.g. "scorer")
#   <task-or-taskfile>  the task prompt; if it names an existing file, that
#                       file's contents are used as the task text
#   --sandbox MODE      read-only | workspace-write (default) | danger-full-access
#                       (an agent TOML `sandbox_mode`, if present, is the default)
#   --output FILE       where to write the worker's final message
#                       (default: process_log/agent_runs/<agent-id>-<UTC>.md)
#   --add-dir DIR       grant the worker write access to an extra dir (repeatable)
#   --model MODEL       override the TOML's pinned model (rarely needed)
#
# Exit status is the worker's: nonzero means the model was unavailable (codex
# does NOT downgrade — see the model-fallback note in CLAUDE.md; only the Claude
# runtime is probed/remapped at setup) or the task itself failed. Read the error.
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
ADDDIR_ARGS=()
while [ $# -gt 0 ]; do
    case "$1" in
        --sandbox) SANDBOX="${2:?--sandbox needs a value}"; shift 2 ;;
        --output)  OUTPUT="${2:?--output needs a value}"; shift 2 ;;
        --model)   MODEL_OVERRIDE="${2:?--model needs a value}"; shift 2 ;;
        --add-dir) ADDDIR_ARGS+=(--add-dir "${2:?--add-dir needs a value}"); shift 2 ;;
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

if [ -z "$OUTPUT" ]; then
    _stamp="$(date -u +%Y%m%dT%H%M%SZ)"
    OUTPUT="$PROJECT_ROOT/process_log/agent_runs/${AGENT_ID}-${_stamp}.md"
fi
mkdir -p "$(dirname "$OUTPUT")"

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
set +e
codex exec </dev/null \
    --skip-git-repo-check \
    -C "$PROJECT_ROOT" \
    -m "$MODEL" \
    -s "$SANDBOX" \
    -c "model_reasoning_effort=\"$EFFORT\"" \
    -c 'project_doc_max_bytes=0' \
    -c "developer_instructions=$INSTRUCTIONS" \
    ${_catalog_args[@]+"${_catalog_args[@]}"} \
    ${ADDDIR_ARGS[@]+"${ADDDIR_ARGS[@]}"} \
    -o "$OUTPUT" \
    -- "$TASK"
_rc=$?
set -e

if [ "$_rc" -ne 0 ]; then
    echo "[launch_agent] worker exited $_rc — model unavailable or task failed; see output above." >&2
    exit "$_rc"
fi
echo "[launch_agent] done. Read the agent's result at: $OUTPUT"
