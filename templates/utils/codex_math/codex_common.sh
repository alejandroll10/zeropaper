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
