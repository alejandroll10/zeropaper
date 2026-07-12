# Shared codex-math helpers. Sourced (not executed) by codex_{verify,write,explore}.sh.
#
# Purpose: keep the `codex exec` instance a codex-math script spawns a LEAF
# worker that cannot spawn its own sub-agents. codex-math is a single-shot proof
# task — it has no reason to fan out, and a spawned child (runaway depth/cost,
# and an opaque extra worker) is never what the caller wants.
#
# Mechanism mirrors code/utils/agent_launcher/launch_agent.sh (belt + suspenders):
#   1. No-spawn model catalog (physical): codex ties the native multi-agent tool
#      (spawn_agent + "you're in a team" framing) to each model's
#      `multi_agent_version` in the catalog — a feature flag can't turn it off
#      (the catalog wins; openai/codex#31097). We dump the live catalog
#      (`codex debug models`, cache-backed and ~instant), blank that field for
#      every model, and hand the worker the patched copy. Any value other than
#      v1/v2 drops the tool entirely.
#   2. Leaf directive (text, via the developer channel): belt to that suspenders,
#      and the fallback when the catalog can't be built (offline/auth).

CODEX_LEAF_DIRECTIVE="You are a single leaf worker running one codex-math task. Do NOT spawn, delegate to, launch, or hand off to other agents or sub-agents (no spawn_agent, no launch_agent.sh, no nested codex exec). Complete the task yourself and return the result."

# Sandbox posture for codex-math leaf workers. The writable-roots half mirrors
# code/utils/agent_launcher/launch_agent.sh (and the deployed Claude
# .claude/settings.json allowWrite set): workspace-write defaults writable to
# [workdir, /tmp, $TMPDIR], and codex-math shells out to python/sympy/matplotlib
# (font/uv caches under ~/.cache, ~/.matplotlib, ~/Library/Caches) and writes its
# own session state under ~/.codex, so those roots must be writable. codex
# expands ~ inside writable_roots (verified). Writes outside this set (e.g. rm in
# $HOME) stay blocked — the anti-destruction property.
#
# DELIBERATE DIVERGENCE from launch_agent.sh: network stays OFF here. That
# launcher enables egress because general pipeline agents call WRDS
# (127.0.0.1:23847) / OpenAlex / web; codex-math workers are self-contained
# proof-verify / proof-write / numeric-explore tasks with ZERO egress need. Per
# least-privilege we do not grant the sandboxed shell tool a network capability
# it has no task-relevant use for (a hallucinated "let me check online" shell-out
# then fails closed rather than reaching out). Setting it explicitly to false
# (not just relying on the default) also overrides any network_access=true a
# user's global ~/.codex/config.toml might carry. Note this does NOT affect
# codex's own model-API traffic — the sandbox gates model-generated shell
# commands, not the codex harness's outbound API call, so the worker still runs.
# These keys are no-ops unless the active sandbox is workspace-write.
# Pass "${CODEX_SANDBOX_WS_ARGS[@]}" into each `codex exec`.
CODEX_SANDBOX_WS_ARGS=(
    -c 'sandbox_workspace_write.network_access=false'
    -c 'sandbox_workspace_write.writable_roots=["~/.codex","~/.cache","~/Library/Caches","~/.matplotlib"]'
)

# codex_build_no_spawn_args <scratch_dir>
# Populates the global array CODEX_NO_SPAWN_ARGS with `codex exec -c ...` flags
# that make the worker leaf-only. Best-effort on the catalog: if `codex debug
# models` can't be dumped, the leaf directive still applies.
codex_build_no_spawn_args() {
    local scratch="$1"
    mkdir -p "$scratch"
    CODEX_NO_SPAWN_ARGS=()
    if codex debug models 2>/dev/null \
         | python3 -c 'import json,sys; d=json.load(sys.stdin); [m.__setitem__("multi_agent_version","none") for m in d.get("models",[])]; json.dump(d, open(sys.argv[1],"w"))' \
           "$scratch/catalog.json" 2>/dev/null \
       && [ -s "$scratch/catalog.json" ]; then
        CODEX_NO_SPAWN_ARGS+=(-c "model_catalog_json=\"$scratch/catalog.json\"")
    else
        echo "[codex-math] warning: could not build no-spawn catalog; relying on leaf directive only" >&2
    fi
    CODEX_NO_SPAWN_ARGS+=(-c "developer_instructions=$CODEX_LEAF_DIRECTIVE")
}

# codex_leaf_setup
# One-call setup for a leaf `codex exec`: makes a scratch dir, registers an EXIT
# trap to remove it, and builds the no-spawn args. Sets globals _codex_scratch
# and CODEX_NO_SPAWN_ARGS. Call once right before `codex exec`, then pass
# "${CODEX_NO_SPAWN_ARGS[@]}" into it.
codex_leaf_setup() {
    _codex_scratch=$(mktemp -d "${TMPDIR:-/tmp}/codex_math.XXXXXX")
    trap 'rm -rf "$_codex_scratch"' EXIT
    codex_build_no_spawn_args "$_codex_scratch"
}
