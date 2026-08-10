#!/usr/bin/env bash
# Runtime-document assembly for setup.sh.
#
# This file is sourced after TEMPLATE_ROOT and OUT_DIR are resolved.  The
# public setup_runtime_documents function deliberately runs in setup.sh's
# shell. Its only outputs are MODE_BODIES_OVERLAY, MODE_VOCAB_OVERLAY, and
# MODE_METADATA_ARGS for the agent assemblers that follow, plus CATALOG_TMPDIR
# for setup.sh's shared EXIT cleanup trap. Runtime-document destinations are
# explicit inputs initialized by setup.sh before this function is called.

setup_runtime_documents() {
    local mode_slug candidate_bodies candidate_vocab
    local _rt_pair _rt_src _rt_dst
    local CORE CLAUDE_SESSION CODEX_SESSION GEMINI_SESSION f
    local AGENT_CATALOG_FILE SKILL_CATALOG_FILE CODEX_SKILL_CATALOG_FILE ext
    local SEED_TEMPLATE
    local -a REQUIRED_FILES CATALOG_ARGS CODEX_CATALOG_ARGS
    local -a AGENT_METADATA_ARGS SKILL_METADATA_ARGS CODEX_SKILL_METADATA_ARGS
    local -a CATALOG_VOCAB_ARGS BYPASS_HALT_ARGS SEED_ARGS
    local -a CODEX_DISCIPLINE_ARGS GEMINI_DISCIPLINE_ARGS common_args

    # ── Mode-overlay paths ──
    # When --mode is set, the variant assemblers append a mode-specific shared
    # bodies dir (consulted before the base shared dir; first match wins, so a
    # mode override of `theory-generator-core.md` shadows the base body) and a
    # mode-specific vocab overlay (merged onto the base variant vocab; later
    # layer wins on duplicate keys, so mode-specific values override defaults).
    # Sourcing both via per-mode dirs lets future modes drop in their own
    # overrides without further setup.sh wiring.
    #
    # Resolved against TEMPLATE_ROOT, so overlays come from the same invoking
    # checkout as every other build input in both full and assembly-only runs.
    MODE_BODIES_OVERLAY=""
    MODE_VOCAB_OVERLAY=""
    # Metadata twin of the body/vocab overlays: passed to every agent assembler
    # so an agent's metadata["modes"][mode_slug] field overrides merge over its
    # base fields.
    MODE_METADATA_ARGS=()
    if [ -n "$MODE" ]; then
        mode_slug="${MODE//-/_}"
        candidate_bodies="$TEMPLATE_ROOT/templates/agent_bodies/shared_modes/${mode_slug}"
        candidate_vocab="$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}_modes/${mode_slug}/vocab.json"
        if [ -d "$candidate_bodies" ]; then
            MODE_BODIES_OVERLAY="$candidate_bodies"
        fi
        if [ -f "$candidate_vocab" ]; then
            MODE_VOCAB_OVERLAY="$candidate_vocab"
        fi
        MODE_METADATA_ARGS=(--mode "$mode_slug")
        if [ -z "$MODE_BODIES_OVERLAY" ] && [ -z "$MODE_VOCAB_OVERLAY" ]; then
            echo "Error: --mode $MODE has no overlay assets for variant $VARIANT."
            echo "  Expected at least one of:"
            echo "    $candidate_bodies/"
            echo "    $candidate_vocab"
            exit 1
        fi
    fi

    # ── Install per-runtime settings files ──
    # This is the only writer of deployed Claude/Gemini settings. Grok's
    # sandbox file is generated later because it embeds an absolute home path.
    mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL" "$OUT_DIR/$GEMINI_DIR_REL"
    infrastructure_dir 80 "docs"
    for _rt_pair in "$CLAUDE_SETTINGS_SRC_REL:$CLAUDE_SETTINGS_REL" "$GEMINI_SETTINGS_SRC_REL:$GEMINI_SETTINGS_REL"; do
        _rt_src="$TEMPLATE_ROOT/${_rt_pair%%:*}"
        _rt_dst="$OUT_DIR/${_rt_pair##*:}"
        if [ ! -f "$_rt_src" ]; then
            echo "Error: runtime settings template not found: $_rt_src" >&2
            exit 1
        fi
        case "${_rt_pair##*:}" in
            "$CLAUDE_SETTINGS_REL") infrastructure_copy_file 170 "$_rt_src" "$CLAUDE_SETTINGS_REL" ;;
            "$GEMINI_SETTINGS_REL") infrastructure_copy_file 180 "$_rt_src" "$GEMINI_SETTINGS_REL" ;;
        esac
    done

    # ── Assemble runtime docs ──
    echo "Assembling runtime docs for variant: $VARIANT..."

    if [ "$MANUAL" = "1" ]; then
        CORE="$TEMPLATE_ROOT/templates/shared/core_manual.md"
        CLAUDE_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session_manual.md"
        CODEX_SESSION="$TEMPLATE_ROOT/templates/runtime/codex/session_manual.md"
        GEMINI_SESSION="$TEMPLATE_ROOT/templates/runtime/gemini/session_manual.md"
    elif [ "$MODE" = "report" ]; then
        CORE="$TEMPLATE_ROOT/templates/shared/core_report.md"
        CLAUDE_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session_report.md"
        CODEX_SESSION="$TEMPLATE_ROOT/templates/runtime/codex/session_report.md"
        GEMINI_SESSION="$TEMPLATE_ROOT/templates/runtime/gemini/session_report.md"
    else
        CORE="$TEMPLATE_ROOT/templates/shared/core.md"
        CLAUDE_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session.md"
        CODEX_SESSION="$CLAUDE_SESSION"
        GEMINI_SESSION="$CLAUDE_SESSION"
    fi
    REQUIRED_FILES=("$CORE" "$CLAUDE_SESSION" "$CODEX_SESSION" "$GEMINI_SESSION")
    for f in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$f" ]; then
            echo "Error: $f not found"
            exit 1
        fi
    done

    # Manual mode embeds generated agent and skill catalogs in each runtime doc.
    CATALOG_ARGS=()
    CODEX_CATALOG_ARGS=()
    if [ "$MANUAL" = "1" ]; then
        CATALOG_TMPDIR="$(mktemp -d)"
        AGENT_CATALOG_FILE="$CATALOG_TMPDIR/agents.md"
        SKILL_CATALOG_FILE="$CATALOG_TMPDIR/skills.md"
        CODEX_SKILL_CATALOG_FILE="$CATALOG_TMPDIR/skills_codex.md"

        AGENT_METADATA_ARGS=(
            --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json"
            --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json"
        )
        SKILL_METADATA_ARGS=(
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/sympy_skills.json"
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json"
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json"
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json"
        )
        CODEX_SKILL_METADATA_ARGS=(
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/sympy_skills.json"
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json"
            --metadata "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json"
        )
        if variant_wants_skill nber_agenda; then
            SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json")
            CODEX_SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json")
        fi
        if variant_wants_skill ssj; then
            SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json")
            CODEX_SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json")
        fi
        for ext in "${EXTENSIONS[@]}"; do
            case "$ext" in
                empirical)
                    AGENT_METADATA_ARGS+=(
                        --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json"
                        --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json"
                    )
                    SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json")
                    CODEX_SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json")
                    ;;
                theory_llm)
                    AGENT_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
                    SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json")
                    CODEX_SKILL_METADATA_ARGS+=(--metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json")
                    ;;
            esac
        done

        CATALOG_VOCAB_ARGS=(--vocab "$TEMPLATE_ROOT/templates/agent_bodies/shared/vocab.json")
        [ -f "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json" ] && \
            CATALOG_VOCAB_ARGS+=(--vocab "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json")
        [ -n "$MODE_VOCAB_OVERLAY" ] && CATALOG_VOCAB_ARGS+=(--vocab "$MODE_VOCAB_OVERLAY")

        python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
            "${AGENT_METADATA_ARGS[@]}" "${CATALOG_VOCAB_ARGS[@]}" --output "$AGENT_CATALOG_FILE"
        python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
            "${SKILL_METADATA_ARGS[@]}" "${CATALOG_VOCAB_ARGS[@]}" --output "$SKILL_CATALOG_FILE"
        python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
            "${CODEX_SKILL_METADATA_ARGS[@]}" "${CATALOG_VOCAB_ARGS[@]}" --output "$CODEX_SKILL_CATALOG_FILE"

        CATALOG_ARGS=(--agent-catalog "$AGENT_CATALOG_FILE" --skill-catalog "$SKILL_CATALOG_FILE")
        CODEX_CATALOG_ARGS=(--agent-catalog "$AGENT_CATALOG_FILE" --skill-catalog "$CODEX_SKILL_CATALOG_FILE")
    fi

    BYPASS_HALT_ARGS=()
    if [ "$HALT_ON_CORE_BYPASS" = "1" ]; then
        BYPASS_HALT_ARGS=(--core-bypass-halt)
    fi

    SEED_ARGS=()
    if [ "$FAITHFUL" = "1" ]; then
        SEED_TEMPLATE="$TEMPLATE_ROOT/templates/shared/faithful.md"
        if [ ! -f "$SEED_TEMPLATE" ]; then
            echo "Error: faithful template not found: $SEED_TEMPLATE"
            exit 1
        fi
        SEED_ARGS=(--seed-block "$SEED_TEMPLATE")
    elif [ "$SEEDED" = "1" ]; then
        SEED_TEMPLATE="$TEMPLATE_ROOT/templates/shared/seed.md"
        if [ ! -f "$SEED_TEMPLATE" ]; then
            echo "Error: seed template not found: $SEED_TEMPLATE"
            exit 1
        fi
        SEED_ARGS=(--seed-block "$SEED_TEMPLATE")
    fi

    common_args=(
        --core "$CORE"
        --paper-type "$PAPER_TYPE"
        --target-journals "$TARGET_JOURNALS"
        --domain-areas "$DOMAIN_AREAS"
        --initial-tier "$INITIAL_TIER"
        --tier-ladder-prose "$TIER_LADDER_PROSE"
        --tier-list-inline "$TIER_LIST_INLINE"
        --mechanism-qualifier "$MECHANISM_QUALIFIER"
        --mechanism-qualifier-adv "$MECHANISM_QUALIFIER_ADV"
        --deepening-extension-types "$DEEPENING_EXTENSION_TYPES"
        --characterize-example-bullet "$CHARACTERIZE_EXAMPLE_BULLET"
        --numerical-verification-bullet "$NUMERICAL_VERIFICATION_BULLET"
        --doc-subtitle "$DOC_SUBTITLE"
    )

    python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
        "${common_args[@]}" \
        --session "$CLAUDE_SESSION" \
        --doc-name "CLAUDE.md" \
        --agent-dir "$CLAUDE_AGENTS_REL" \
        --skill-dir "$CLAUDE_SKILLS_REL" \
        --session-out "$SESSION_OUT_DIR/start_session_claude.md" \
        "${SEED_ARGS[@]}" "${BYPASS_HALT_ARGS[@]}" "${CATALOG_ARGS[@]}" \
        --output "$CLAUDE_MD_OUT"
    infrastructure_file 100 "CLAUDE.md"
    infrastructure_file 140 "docs/start_session_claude.md"

    CODEX_DISCIPLINE_ARGS=()
    if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
        CODEX_DISCIPLINE_ARGS=(--discipline "$TEMPLATE_ROOT/templates/runtime/codex/session.md")
    fi
    python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
        "${common_args[@]}" \
        --session "$CODEX_SESSION" \
        --doc-name "AGENTS.md" \
        --agent-dir "$CODEX_AGENTS_REL" \
        --skill-dir "$CODEX_SKILLS_REL" \
        --session-out "$SESSION_OUT_DIR/start_session_codex.md" \
        "${CODEX_DISCIPLINE_ARGS[@]}" "${SEED_ARGS[@]}" "${BYPASS_HALT_ARGS[@]}" "${CODEX_CATALOG_ARGS[@]}" \
        --output "$AGENTS_MD_OUT"
    infrastructure_file 110 "AGENTS.md"
    infrastructure_file 150 "docs/start_session_codex.md"

    GEMINI_DISCIPLINE_ARGS=()
    if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
        GEMINI_DISCIPLINE_ARGS=(--discipline "$TEMPLATE_ROOT/templates/runtime/gemini/session.md")
    fi
    python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
        "${common_args[@]}" \
        --session "$GEMINI_SESSION" \
        --doc-name "GEMINI.md" \
        --agent-dir "$GEMINI_AGENTS_REL" \
        --skill-dir "$GEMINI_DIR_REL/skills" \
        --session-out "$SESSION_OUT_DIR/start_session_gemini.md" \
        "${GEMINI_DISCIPLINE_ARGS[@]}" "${SEED_ARGS[@]}" "${BYPASS_HALT_ARGS[@]}" "${CATALOG_ARGS[@]}" \
        --output "$GEMINI_MD_OUT"
    infrastructure_file 120 "GEMINI.md"
    infrastructure_file 160 "docs/start_session_gemini.md"

    echo "  ✓ Runtime docs assembled (CLAUDE.md + AGENTS.md + GEMINI.md)"
}
