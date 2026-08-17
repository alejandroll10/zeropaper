# Shared codex-math helpers. Sourced (not executed) by codex_{verify,write,explore}.sh.
#
# Purpose: keep the `codex exec` instance a codex-math script spawns a LEAF
# worker that cannot spawn its own sub-agents. codex-math is a single-shot proof
# task — it has no reason to fan out, and a spawned child (runaway depth/cost,
# and an opaque extra worker) is never what the caller wants.
#
# This standalone `codex exec` path cannot use the project role's
# `[agents] enabled=false`, so it retains its own belt-and-suspenders mechanism:
#   1. No-spawn model catalog (physical): codex ties the native multi-agent tool
#      (spawn_agent + "you're in a team" framing) to each model's
#      `multi_agent_version` in the catalog — a feature flag can't turn it off
#      (the catalog wins; openai/codex#31097). We dump the live catalog
#      (`codex debug models`, cache-backed and ~instant), blank that field for
#      every model, and hand the worker the patched copy. Any value other than
#      v1/v2 drops the tool entirely.
#   2. Leaf directive (text, via the developer channel): belt to that suspenders,
#      and the fallback when the catalog can't be built (offline/auth).

CODEX_LEAF_DIRECTIVE="You are a single leaf worker running one codex-math task. Do NOT spawn, delegate to, launch, or hand off to other agents or sub-agents (no spawn_agent, no nested codex exec). Complete the task yourself and return the result."

# Sandbox posture for codex-math leaf workers. The filesystem half mirrors the
# Codex orchestrator profile (and the deployed Claude .claude/settings.json
# allowWrite set): codex-math shells out to
# python/sympy/matplotlib and writes package-specific paths under broad
# ~/.cache, plus ~/.matplotlib, ~/Library/Caches, and its own ~/.codex session
# state. The shared permission profile grants those roots while keeping the
# narrower WRDS compatibility guard read-only.
#
# DELIBERATE DIVERGENCE from the Codex orchestrator profile: network stays OFF
# here. Native pipeline roles inherit egress because they call OpenAlex / web
# (WRDS itself now uses a filesystem socket); codex-math workers are self-contained
# proof-verify / proof-write / numeric-explore tasks with ZERO egress need. Per
# least-privilege we do not grant the sandboxed shell tool a network capability
# it has no task-relevant use for (a hallucinated "let me check online" shell-out
# then fails closed rather than reaching out). Setting it explicitly to false
# also avoids inheriting a user's broader command-network policy. This does NOT affect
# codex's own model-API traffic — the sandbox gates model-generated shell
# commands, not the codex harness's outbound API call, so the worker still runs.
# `codex_leaf_setup` populates this for each `codex exec`.
CODEX_SANDBOX_ARGS=()

# Sandbox MODE for codex-math leaf workers: workspace-write normally. When these
# scripts are invoked from inside a codex sandbox (CODEX_SANDBOX is set in the
# env — the normal case when the pipeline orchestrator's exec tool runs them
# under codex's deny-by-default Seatbelt profile), a second, inner sandbox
# cannot be applied: macOS refuses the nested sandbox_apply, so apply_patch
# fails with `sandbox_apply: Operation not permitted` while plain exec commands
# silently run under the OUTER sandbox only (codex skips re-sandboxing when it
# detects it is already sandboxed). Reproduced 2026-07-12 on codex-cli 0.144.1;
# this standalone helper therefore runs the nested worker sandbox-less and lets
# the caller's outer sandbox
# confine it — the same boundary that was actually in force anyway. Caveat: the
# network_access=false posture above is only *enforced* un-nested; nested,
# egress is whatever the outer sandbox grants. That is not a regression — it
# was already true before this guard; the guard just fixes apply_patch and
# makes the situation explicit. Pass as: --sandbox "$CODEX_SANDBOX_MODE".
if [ -n "${CODEX_SANDBOX:-}" ] || [ "${SANDBOX_RUNTIME:-}" = "1" ]; then
    CODEX_SANDBOX_MODE="danger-full-access"
    echo "[codex-math] nested inside an outer sandbox: worker runs danger-full-access; the caller's outer sandbox still confines it" >&2
else
    CODEX_SANDBOX_MODE="workspace-write"
fi

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
    # Proxy-auth version floor (issue #213): warn if this codex is old enough
    # to drop Proxy-Authorization behind an authenticated proxy. Guarded so a
    # deploy that predates the preflight never blocks. Same relative layout in
    # the template repo (templates/utils/) and deployments (code/utils/).
    local _cp_dir
    _cp_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    if [ -f "$_cp_dir/codex_preflight.sh" ]; then
        . "$_cp_dir/codex_preflight.sh"
        codex_permission_profile_preflight
        codex_proxy_auth_preflight
    else
        echo "[codex-math] ERROR: missing codex_preflight.sh — run update.sh" >&2
        return 1
    fi
    if [ "$CODEX_SANDBOX_MODE" = "workspace-write" ]; then
        /usr/bin/python3 -I "$_cp_dir/sandbox_cache_roots.py"
        codex_permission_profile_args "" false
        CODEX_SANDBOX_ARGS=(--ignore-user-config "${CODEX_PERMISSION_PROFILE_ARGS[@]}")
    else
        CODEX_SANDBOX_ARGS=(--ignore-user-config --sandbox "$CODEX_SANDBOX_MODE")
    fi
    # The literal-/tmp fallback is for Linux, where /tmp is a real directory.
    # On macOS an unset TMPDIR would hit the /tmp→/private/tmp symlink issue
    # documented in codex_verify.sh, but the deployed runtimes always set
    # TMPDIR there; if this mktemp ever fails, check that assumption first.
    _codex_scratch=$(mktemp -d "${TMPDIR:-/tmp}/codex_math.XXXXXX")
    trap 'rm -rf "$_codex_scratch"' EXIT
    codex_build_no_spawn_args "$_codex_scratch"
}
