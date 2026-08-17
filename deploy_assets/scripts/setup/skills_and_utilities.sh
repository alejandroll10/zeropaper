#!/usr/bin/env bash
# Core-skill and utility assembly for setup.sh.
#
# Source after project scaffolding. setup_skills_and_utilities has no shell
# outputs: later phases consume only the files it assembles under OUT_DIR.

_setup_skills_assemble_claude_skills() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_skills.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

setup_skills_and_utilities() {
    local SKILLS_OUT CODEX_SKILLS_OUT _ext _cand _mf
    local -a _heal_light_arg _heal_meta_args
    # ── Assemble core skills ──
    echo "Assembling core skills..."

    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
    infrastructure_dir 20 "$CLAUDE_SKILLS_REL"
    infrastructure_dir 40 "$CODEX_SKILLS_REL"

    # SymPy skill (available for all variants — preloaded into math-touching subagents)
    _setup_skills_assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/sympy_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/sympy" \
        "$SKILLS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
        --metadata "$TEMPLATE_ROOT/templates/skill_metadata/sympy_skills.json" \
        --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/sympy" \
        --output-dir "$CODEX_SKILLS_OUT"

    # Codex math skill (Claude-only — would be circular under the codex runtime,
    # which is itself the proof-verification backend the skill shells out to)
    _setup_skills_assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
        "$SKILLS_OUT"

    # Copy codex-math utility scripts
    infrastructure_dir 90 "code/utils/codex_math"
    cp "$TEMPLATE_ROOT/templates/utils/codex_math/"*.sh "$P/code/utils/codex_math/"
    chmod +x "$P/code/utils/codex_math/"*.sh

    # Create codex output directories
    mkdir -p "$P/output/codex_audits" "$P/output/codex_proofs" "$P/output/codex_explorations"

    # Check for codex CLI (optional dependency — warn, don't fail)
    if ! command -v codex >/dev/null 2>&1; then
        echo "  ⚠ codex CLI not found. Install with: npm install -g @openai/codex"
        echo "  ⚠ The codex-math skill will not work until codex is installed."
    fi

    # Bibliography verification skill (available for all variants)
    _setup_skills_assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
        "$SKILLS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
        --metadata "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
        --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
        --output-dir "$CODEX_SKILLS_OUT"

    # Copy bib-verify utility scripts
    infrastructure_dir 110 "code/utils/bib_verify"
    cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"
    cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"verify_bib.sh "$P/code/utils/bib_verify/"
    chmod +x "$P/code/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"verify_bib.sh

    # OpenAlex literature search skill (loaded by literature-scout, gap-scout, novelty-checker)
    _setup_skills_assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
        "$SKILLS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
        --metadata "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
        --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
        --output-dir "$CODEX_SKILLS_OUT"

    # Copy OpenAlex utility script
    infrastructure_dir 120 "code/utils/openalex"
    cp "$TEMPLATE_ROOT/templates/utils/openalex/"openalex.py "$P/code/utils/openalex/"
    chmod +x "$P/code/utils/openalex/"openalex.py

    # NBER conference agenda skill (loaded by literature-scout, gap-scout — the
    # pre-publication research frontier: who is presenting what, right now).
    # Variant-gated (issue #205): economics conferences are dead weight for
    # llm_cognition, whose frontier bullets point at arXiv/OpenReview instead.
    if variant_wants_skill nber_agenda; then
        _setup_skills_assemble_claude_skills \
            "$TEMPLATE_ROOT" \
            "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json" \
            "$TEMPLATE_ROOT/templates/skill_bodies/nber_agenda" \
            "$SKILLS_OUT"

        python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json" \
            --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/nber_agenda" \
            --output-dir "$CODEX_SKILLS_OUT"

        # Copy NBER agenda utility script
        infrastructure_dir 130 "code/utils/nber_agenda"
        cp "$TEMPLATE_ROOT/templates/utils/nber_agenda/"nber_agenda.py "$P/code/utils/nber_agenda/"
        chmod +x "$P/code/utils/nber_agenda/"nber_agenda.py
    fi

    # Copy the sandbox-safe git-push credential setup (repo-scoped PAT store; the
    # grok sandbox cannot reach the macOS keychain — issue #190). Opt-in: the user
    # runs it once per project if they want `git push` to work under grok.
    infrastructure_copy_file 240 "$TEMPLATE_ROOT/templates/utils/setup_push_token.sh" "code/utils/setup_push_token.sh"
    chmod +x "$P/code/utils/setup_push_token.sh"

    # Shared no-follow validator for every Codex/Claude/Grok external writable
    # root. The launcher and direct, un-nested Codex worker entrypoints all use
    # the same deployed implementation before handing paths to a sandbox.
    infrastructure_copy_file 245 "$TEMPLATE_ROOT/templates/utils/sandbox_cache_roots.py" "code/utils/sandbox_cache_roots.py"
    chmod +x "$P/code/utils/sandbox_cache_roots.py"

    # Copy the codex CLI preflight (proxy-auth version-floor warning, issue #213).
    # Sourced by launch.sh's codex branch and codex_math/codex_common.sh.
    infrastructure_copy_file 250 "$TEMPLATE_ROOT/templates/utils/codex_preflight.sh" "code/utils/codex_preflight.sh"

    # Stdlib-only control client used by launch.sh's persistent OpenCode server
    # driver (health, session-tree quiescence, timeout abort, and reconciliation).
    infrastructure_copy_file 260 "$TEMPLATE_ROOT/templates/utils/opencode_driver.py" ".opencode/opencode_driver.py"
    chmod +x "$P/.opencode/opencode_driver.py"

    # Fail-closed Anthropic Sandbox Runtime adapter. The headless server is the
    # execution owner for task/Bash tools, and both it and each attached client are
    # wrapped so their whole native child trees share the filesystem boundary. The
    # narrow Python lifecycle/HTTP control driver remains host-side.
    infrastructure_copy_file 270 "$TEMPLATE_ROOT/templates/utils/opencode_sandbox_exec.sh" ".opencode/opencode_sandbox_exec.sh"
    chmod +x "$P/.opencode/opencode_sandbox_exec.sh"
    infrastructure_copy_file 280 "$TEMPLATE_ROOT/templates/utils/opencode_sandbox_exec.mjs" ".opencode/opencode_sandbox_exec.mjs"
    chmod +x "$P/.opencode/opencode_sandbox_exec.mjs"

    # ── Launch-time model heal ──
    # The build-time model remap (resolve_model_fallbacks.py + apply_model_remap.py)
    # runs ONCE and cannot reach an already-deployed project. Deploy a runtime twin so
    # `./launch.sh claude` re-decides each agent's tier at every launch, in both
    # directions: restore the ideal when it recovers, fall back again when it is down.
    # config.json records each agent's IDEAL model (the deployed *.md only carries the
    # current, possibly-remapped pin, so the ideal must be captured here from the same
    # metadata). Emitted with --light-model when --light collapsed subagents to sonnet,
    # so the healer restores to the model the assembler actually wrote.
    infrastructure_dir 140 "code/utils/model_heal"
    cp "$TEMPLATE_ROOT/templates/utils/model_heal/heal_agent_models.py" "$P/code/utils/model_heal/"
    chmod +x "$P/code/utils/model_heal/heal_agent_models.py"
    _heal_light_arg=()
    [ "$LIGHT" = "1" ] && _heal_light_arg=(--light-model sonnet)
    # Metadata scoped to what is ACTUALLY deployed — by both variant and selected
    # extension — NOT the deliberately-broad _model_meta_args the probe uses. The config
    # is keyed by agent name, so two kinds of over-inclusion must be avoided: the OTHER
    # variant's extension metadata (a same-named agent's ideal from the undeployed
    # variant could silently win) and an UNSELECTED extension's metadata (entries for
    # agents with no deployed .md). So: core shared + the selected variant's core, then
    # for each SELECTED extension its shared + this-variant + variant-agnostic (agents.json,
    # e.g. theory_llm) files, whichever exist. Base core is already variant-scoped
    # (claude_variant_agents.json is the copied selected variant).
    _heal_meta_args=(--metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json")
    [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" ] && \
        _heal_meta_args+=(--metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
    for _ext in "${EXTENSIONS[@]}"; do
        for _cand in shared_agents.json "${VARIANT}_agents.json" agents.json; do
            _mf="$TEMPLATE_ROOT/extensions/$_ext/agent_metadata/$_cand"
            [ -f "$_mf" ] && _heal_meta_args+=(--metadata "$_mf")
        done
    done
    python3 "$TEMPLATE_ROOT/scripts/emit_model_heal_config.py" \
        --fallbacks "$TEMPLATE_ROOT/templates/model_fallbacks.json" \
        "${_heal_light_arg[@]}" "${_heal_meta_args[@]}" \
        --out "$P/code/utils/model_heal/config.json"

    # Sequence-space Jacobian (SSJ) skill — solve/analyze heterogeneous-agent GE
    # models (theory-explorer Stage 2b, idea-prototyper tractability pre-check)
    # Variant-gated (issue #205): the macro-GE toolkit is dead weight for
    # llm_cognition, whose prototyping bullets point at toy-scale simulation.
    if variant_wants_skill ssj; then
        _setup_skills_assemble_claude_skills \
            "$TEMPLATE_ROOT" \
            "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json" \
            "$TEMPLATE_ROOT/templates/skill_bodies/ssj" \
            "$SKILLS_OUT"

        python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json" \
            --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/ssj" \
            --output-dir "$CODEX_SKILLS_OUT"

        # Copy SSJ driver + worked finance example model
        infrastructure_dir 150 "code/utils/ssj"
        cp "$TEMPLATE_ROOT/templates/utils/ssj/"ssj_solve.py "$TEMPLATE_ROOT/templates/utils/ssj/"example_asset_pricing.py "$P/code/utils/ssj/"
        chmod +x "$P/code/utils/ssj/"ssj_solve.py

        provision_ssj_dependencies
    fi

    echo "  ✓ Core skills assembled"

}
