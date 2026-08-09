#!/usr/bin/env bash
# Base and variant agent assembly for setup.sh.
#
# Source after setup_runtime_documents has resolved mode overlays. The public
# setup_base_agents function exports only AGENTS_OUT, CODEX_AGENTS_OUT,
# GEMINI_AGENTS_OUT, GROK_AGENTS_OUT, OPENCODE_AGENTS_OUT, and
# MODEL_REMAP_ARGS for later injection, extension, remap, and manifest phases.

_setup_agents_assemble_claude_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mode overlay reaches shared agents too: a mode-specific {id}.md in
    # MODE_BODIES_OVERLAY shadows the base shared body for that one agent
    # (e.g., a future mode-specific referee-mechanism), and MODE_VOCAB_OVERLAY
    # supplies any vocab keys the override references. Variant-agent shared
    # bodies (theory-generator-core.md etc.) live in the same overlay dir
    # under -core.md and are picked up by the variant assembler, not here.
    #
    # Vocab layering (shared bodies): shared defaults first, then the variant
    # vocab (when present), then the tier vocab, then the mode overlay — later
    # layers win on duplicate keys. This is what lets domain-sensitive wording
    # in shared bodies (referee-mechanism's evaluative frame, the literature
    # agents' venue directives, fragment content) vary per variant. Contract:
    # every {{KEY}} a shared body references must have a default in
    # agent_bodies/shared/vocab.json OR appear in every variant vocab —
    # a key defined only in some variants breaks setup for the others.
    # KeyError fires loudly on unresolved {{KEY}}, so the contract is enforced.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    # Shared defaults always come first; the mode overlay (when set) is
    # layered on top and wins on duplicate keys. The default file supplies
    # values for keys referenced by shared-agent metadata or bodies in the
    # no-mode case (e.g., IDEA_PROTOTYPER_DESCRIPTION).
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    local variant_vocab="$template_root/templates/agents/${AGENT_DIR}/vocab.json"
    [ -f "$variant_vocab" ] && vocab_args+=(--vocab "$variant_vocab")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_claude_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    # Shared defaults first so variant keys win on duplicates; this also lets
    # -core bodies (and fragments they include) use shared-default keys that
    # no variant is required to define.
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -f "$vocab_file" ] && vocab_args+=(--vocab "$vocab_file")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    # Mode dir first so a per-agent override (e.g. theory-generator-core.md)
    # shadows the base shared body for that one agent only.
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_codex_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors _setup_agents_assemble_claude_shared_agents — see comment there for the
    # MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY threading rationale.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    local variant_vocab="$template_root/templates/agents/${AGENT_DIR}/vocab.json"
    [ -f "$variant_vocab" ] && vocab_args+=(--vocab "$variant_vocab")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_codex_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    # Shared defaults first so variant keys win on duplicates; this also lets
    # -core bodies (and fragments they include) use shared-default keys that
    # no variant is required to define.
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -f "$vocab_file" ] && vocab_args+=(--vocab "$vocab_file")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_gemini_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors _setup_agents_assemble_claude_shared_agents — see comment there for the
    # MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY threading rationale.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    local variant_vocab="$template_root/templates/agents/${AGENT_DIR}/vocab.json"
    [ -f "$variant_vocab" ] && vocab_args+=(--vocab "$variant_vocab")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_gemini_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    # Shared defaults first so variant keys win on duplicates; this also lets
    # -core bodies (and fragments they include) use shared-default keys that
    # no variant is required to define.
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -f "$vocab_file" ] && vocab_args+=(--vocab "$vocab_file")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_grok_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors _setup_agents_assemble_gemini_shared_agents — see _setup_agents_assemble_claude_shared_agents
    # for the MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY threading rationale.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    local variant_vocab="$template_root/templates/agents/${AGENT_DIR}/vocab.json"
    [ -f "$variant_vocab" ] && vocab_args+=(--vocab "$variant_vocab")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_grok_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_grok_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    # Shared defaults first so variant keys win on duplicates; this also lets
    # -core bodies (and fragments they include) use shared-default keys that
    # no variant is required to define.
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -f "$vocab_file" ] && vocab_args+=(--vocab "$vocab_file")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_grok_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_opencode_shared_agents() {
    local template_root="$1" dest_dir="$2"
    local bodies_args=() vocab_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    local variant_vocab="$template_root/templates/agents/${AGENT_DIR}/vocab.json"
    [ -f "$variant_vocab" ] && vocab_args+=(--vocab "$variant_vocab")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    python3 "$template_root/scripts/assemble_opencode_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" "${vocab_args[@]}" "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" "${MODEL_OVERRIDE_ARGS[@]}"
}

_setup_agents_assemble_opencode_variant_agents() {
    local template_root="$1" variant="$2" dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=() shared_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -f "$vocab_file" ] && vocab_args+=(--vocab "$vocab_file")
    vocab_args+=(--vocab "$TIER_VOCAB_FILE")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")
    python3 "$template_root/scripts/assemble_opencode_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" "${vocab_args[@]}" "${MODE_METADATA_ARGS[@]}" \
        --output-dir "$dest_dir" "${MODEL_OVERRIDE_ARGS[@]}"
}


setup_base_agents() {
    local _mf _model_resolver_out _pair GROK_DIR_OUT
    local -a _model_meta_args _model_probe_flag _model_extra_args _model_remap_pairs
    # ── Assemble agents ──
    echo "Copying agents..."

    # Both modes write into $OUT_DIR. The pre-#232 production branch carried
    # alias guards here (the clone could have brought in a symlinked .opencode);
    # the project directory is now created empty by this very script, so nothing
    # can pre-exist to alias.
    AGENTS_OUT="$OUT_DIR/$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$OUT_DIR/$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$OUT_DIR/$GEMINI_AGENTS_REL"
    GROK_AGENTS_OUT="$OUT_DIR/$GROK_AGENTS_REL"
    OPENCODE_AGENTS_OUT="$OUT_DIR/$OPENCODE_AGENTS_REL"
    infrastructure_dir 10 "$CLAUDE_AGENTS_REL"
    infrastructure_dir 30 "$CODEX_AGENTS_REL"
    infrastructure_dir 50 "$GEMINI_AGENTS_REL"
    infrastructure_dir 60 "$GROK_AGENTS_REL"
    infrastructure_dir 70 "$OPENCODE_AGENTS_REL"
    infrastructure_copy_file 210 "$TEMPLATE_ROOT/$OPENCODE_CONFIG_SRC_REL" "$OPENCODE_CONFIG_REL"
    infrastructure_copy_file 200 "$TEMPLATE_ROOT/$OPENCODE_SANDBOX_SRC_REL" "$OPENCODE_SANDBOX_REL"

    # ── Resolve unavailable Claude subagent models → fallbacks ──
    # Agent metadata pins an *ideal* model per agent (e.g. `fable`). If that model is
    # unavailable on this account at setup time (a provider suspension, or no access),
    # the pinned subagent would hard-fail at launch with no fallback. Probe each
    # distinct model with the *same* claude CLI that will run the agents (runtime-
    # accurate), and compute a remap of any unavailable model → the first available
    # entry in its fallback chain (templates/model_fallbacks.json). Applied as a
    # single post-assembly pass below (after extensions), so base + variant + every
    # extension agent is covered. Self-healing: when a suspended model is restored
    # the probe passes and no remap is applied. `--no-model-probe` skips the live
    # probe and relies on the known-unavailable safety list. Claude models only —
    # Codex (gpt-5.6-{sol,terra,luna}) / Gemini (gemini-3-preview) subagents use a
    # different provider.
    _model_meta_args=()
    for _mf in "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
               "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" \
               "$TEMPLATE_ROOT"/extensions/*/agent_metadata/*.json; do
        [ -f "$_mf" ] && _model_meta_args+=(--metadata "$_mf")
    done
    _model_probe_flag=()
    [ "$MODEL_PROBE" = "0" ] && _model_probe_flag=(--no-probe)
    _model_extra_args=()
    [ "$LIGHT" = "1" ] && _model_extra_args=(--extra-model sonnet)
    if [ "$MODEL_PROBE" = "1" ]; then
        echo "Probing subagent model availability (use --no-model-probe to skip)..."
    else
        echo "Resolving subagent models (live probe disabled; using known-unavailable list)..."
    fi
    MODEL_REMAP_ARGS=()
    _model_remap_pairs=()
    # Capture into a variable (not `< <(...)`): process substitution does not
    # propagate the resolver's exit status under `set -e`, so a resolver crash
    # would silently leave unavailable models pinned. Fail loud instead — a
    # nonzero exit means a template bug (bad JSON, python error), not a benign
    # probe miss (the resolver handles a missing claude CLI internally, exit 0).
    if ! _model_resolver_out=$(python3 "$TEMPLATE_ROOT/scripts/resolve_model_fallbacks.py" \
        --fallbacks "$TEMPLATE_ROOT/templates/model_fallbacks.json" \
        --known-unavailable "fable,mythos,claude-fable-5,claude-mythos-5" \
        "${_model_probe_flag[@]}" "${_model_extra_args[@]}" "${_model_meta_args[@]}"); then
        echo "Error: subagent model resolver failed — aborting rather than shipping agents pinned to an unavailable model." >&2
        exit 1
    fi
    while IFS= read -r _pair; do
        [ -n "$_pair" ] && _model_remap_pairs+=("$_pair") && MODEL_REMAP_ARGS+=(--remap "$_pair")
    done <<< "$_model_resolver_out"
    if [ ${#_model_remap_pairs[@]} -gt 0 ]; then
        echo "  ✓ Model fallback resolved — remapping: ${_model_remap_pairs[*]}"
    else
        echo "  ✓ Model fallback resolved — all pinned models available"
    fi

    _setup_agents_assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"
    _setup_agents_assemble_codex_shared_agents "$TEMPLATE_ROOT" "$CODEX_AGENTS_OUT"
    _setup_agents_assemble_gemini_shared_agents "$TEMPLATE_ROOT" "$GEMINI_AGENTS_OUT"
    _setup_agents_assemble_grok_shared_agents "$TEMPLATE_ROOT" "$GROK_AGENTS_OUT"
    _setup_agents_assemble_opencode_shared_agents "$TEMPLATE_ROOT" "$OPENCODE_AGENTS_OUT"

    if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" ]; then
        _setup_agents_assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
        _setup_agents_assemble_codex_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$CODEX_AGENTS_OUT"
        _setup_agents_assemble_gemini_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GEMINI_AGENTS_OUT"
        _setup_agents_assemble_grok_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GROK_AGENTS_OUT"
        _setup_agents_assemble_opencode_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$OPENCODE_AGENTS_OUT"
    fi

    # ── Grok filesystem/network sandbox profile ──
    # Grok Build enforces an OS-kernel sandbox (Seatbelt on macOS, Landlock on Linux)
    # over the whole grok process + its child commands via `grok --sandbox <profile>`.
    # Ship a per-project custom profile `pipeline` that mirrors .claude/settings.json
    # on the property that matters: destructive writes/deletes OUTSIDE this project are
    # blocked, while the pipeline's real work keeps working — write+run scripts, temp
    # writes, the uv/matplotlib/codex caches, WRDS loopback, and open network egress.
    # Launch is `grok --sandbox pipeline --always-approve --leader-socket
    # "$(pwd)/.grok/leader.sock"` (wired into the launch line below; the per-project
    # leader socket is a separate concern from the sandbox — see that comment).
    # `extends = "workspace"` already gives read-everywhere / write-{CWD,
    # ~/.grok,temp} / network-on; we add the pipeline's out-of-project cache+state dirs
    # as read_write and kernel-deny the credential dirs. Grok's `deny` blocks READS as
    # well as writes, so this also closes the secret-read gap the codex runtime had to
    # defer (codex workspace-write is write-confinement only). Writes to ~/.claude,
    # /etc, /root need no explicit denyWrite: the workspace base already blocks every
    # write outside {CWD, ~/.grok, temp}, and they stay readable (unlike a `deny`).
    #
    # Grok's sandbox.toml does NOT expand ~ or $HOME (verified on grok 0.2.93 — a ~/…
    # read_write silently grants nothing and a ~/… deny matches an in-workspace
    # literal), so the absolute paths are baked in here from the deploying user's
    # $HOME. This is host-local, like the per-host .venv; because .grok/sandbox.toml
    # is in the deployment manifest's files_replace, update.sh regenerates it from a
    # fresh same-host setup run (same $HOME → correct paths). Non-glob paths that do
    # not exist are tolerated (no refuse-to-start), so the cross-platform-absent dirs
    # (~/Library/Caches, ~/.matplotlib on Linux) are safe to list unconditionally.
    GROK_DIR_OUT="$(dirname "$GROK_AGENTS_OUT")"
    mkdir -p "$GROK_DIR_OUT"
    cat > "$GROK_DIR_OUT/sandbox.toml" <<GROKSB
# Grok Build sandbox profile for the deployed pipeline (issue #186).
# Launch: grok --sandbox pipeline --always-approve --leader-socket "\$(pwd)/.grok/leader.sock"
# (the per-project leader socket keeps concurrent grok projects from cancelling
#  each other's in-flight turns; it is orthogonal to this filesystem profile.)
# Kernel-enforced (Seatbelt/Landlock). Absolute paths are baked at deploy time
# because grok does not expand ~ or \$HOME; update.sh regenerates on refresh.
[profiles.pipeline]
extends = "workspace"
# Out-of-project caches/state the pipeline legitimately writes.
read_write = [
  "$HOME/.codex",
  "$HOME/.cache",
  "$HOME/Library/Caches",
  "$HOME/.matplotlib",
]
# Credential dirs: kernel read+write deny (blocks cat/grep/subagents, not just writes).
deny = [
  "$HOME/.ssh",
  "$HOME/.aws",
]
GROKSB
    infrastructure_file 190 "$GROK_SANDBOX_REL"

    echo "  ✓ Agents assembled for five runtimes (shared + ${AGENT_DIR})"
}
