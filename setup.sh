#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro] [--mode empirical-first|report]
#                  [--ext empirical|theory_llm] [--seed|--faithful|--manual] [--light] [--local]
#
# --local   Skip git clone, use templates from this repo directly.
#           Outputs to test_output/{variant}/ for inspection.
# --ext     Add an extension (can be repeated). Available: empirical, theory_llm
# --mode    Pipeline-architecture mode (orthogonal to --variant). Available:
#             empirical-first  — flips the pipeline so identification design and
#                                empirical results lead and theory-generator runs
#                                in mechanism mode (prose+DAG, no theorem/proof).
#                                Auto-implies --ext empirical. Finance variant only
#                                in v1; macro is gated on adding identification
#                                tooling there.
#             report           — referee an external paper submission instead of
#                                generating one. Reads submission/, fans out audit
#                                agents in parallel, synthesizes report/referee_report.md.
#                                One-shot, no stages/gates/state. Mutually exclusive
#                                with --seed, --faithful, --manual. Composes with
#                                --ext empirical / --ext theory_llm / --light.
# --seed    Create a seeded-idea project. Creates output/seed/ with instructions.
#           Drop your idea files there before launching. Pipeline starts at seed_triage.
#           Soft semantics: the pipeline preserves the seed's mechanism but may
#           pivot under puzzle-triage / refine framing under scorer recommendations.
# --faithful  Stricter variant of --seed. The seed is treated as a contract; the
#           pipeline implements the seed's named mechanism faithfully and
#           documents impossibilities rather than substituting alternatives. Use
#           when you want the seed executed as written, with additions on top
#           allowed but no replacement of the seed's mechanism / headline /
#           identification strategy. Mutually exclusive with --seed and --manual.
# --manual  Manual mode: assemble agents/skills as a research toolkit, no autonomous
#           pipeline. The runtime doc lists what's available and lets you drive.
#           Mutually exclusive with --seed and --faithful.
# --light   Use sonnet for all subagents (cheaper/faster). Orchestrator model unchanged.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
MODE=""
LOCAL=0
NEXT_IS_VARIANT=0
NEXT_IS_EXT=0
NEXT_IS_MODE=0
SEEDED=0
FAITHFUL=0
MANUAL=0
LIGHT=0
HALT_ON_CORE_BYPASS=0
EXTENSIONS=()

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --ext)         NEXT_IS_EXT=1 ;;
        --mode)        NEXT_IS_MODE=1 ;;
        --seed)        SEEDED=1 ;;
        --faithful)    FAITHFUL=1; SEEDED=1 ;;  # faithful implies seeded folder structure
        --manual)      MANUAL=1 ;;
        --light)       LIGHT=1 ;;
        --halt-on-core-bypass) HALT_ON_CORE_BYPASS=1 ;;
        --local)       LOCAL=1 ;;
        --theory-llm)  VARIANT="finance_llm" ;;  # legacy flag
        -*)            echo "Unknown option: $arg"; exit 1 ;;
        *)
            if [ "$NEXT_IS_VARIANT" = "1" ]; then
                VARIANT="$arg"
                NEXT_IS_VARIANT=0
            elif [ "$NEXT_IS_EXT" = "1" ]; then
                EXTENSIONS+=("$arg")
                NEXT_IS_EXT=0
            elif [ "$NEXT_IS_MODE" = "1" ]; then
                MODE="$arg"
                NEXT_IS_MODE=0
            else
                PROJECT_NAME="$arg"
            fi
            ;;
    esac
done

if [ "$NEXT_IS_VARIANT" = "1" ]; then
    echo "Error: --variant requires a value (finance, macro)"
    exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"
    exit 1
fi
if [ "$NEXT_IS_MODE" = "1" ]; then
    echo "Error: --mode requires a value (empirical-first, report)"
    exit 1
fi

if [ "$MODE" = "report" ]; then
    if [ "$MANUAL" = "1" ]; then
        echo "Error: --mode report is mutually exclusive with --manual"
        echo "  --mode report IS a workflow (audit fan-out + synthesis); --manual would defeat the point."
        exit 1
    fi
    if [ "$SEEDED" = "1" ]; then
        echo "Error: --mode report is mutually exclusive with --seed and --faithful"
        echo "  --mode report evaluates an external submission; there is no seed to develop and no contract to honor."
        exit 1
    fi
fi

if [ "$MANUAL" = "1" ] && [ "$SEEDED" = "1" ]; then
    echo "Error: --manual is mutually exclusive with --seed and --faithful"
    echo "  --manual disables the autonomous pipeline; --seed/--faithful configure the pipeline to consume a user-supplied idea."
    exit 1
fi

# --faithful set both FAITHFUL and SEEDED above. If the user explicitly passed
# --seed in the same invocation, the modes have collapsed to faithful (which
# subsumes --seed's folder structure) — that is fine. The error case is one
# we cannot detect after the case statement: passing both flags is silently
# treated as --faithful. Document that in --help if the script grows one.

# ── Expand legacy finance_llm variant ──
if [ "$VARIANT" = "finance_llm" ]; then
    VARIANT="finance"
    EXTENSIONS+=("theory_llm")
fi

# ── Mode validation and dependency expansion ──
# Pipeline-architecture modes are orthogonal to variants (finance/macro) and to
# extensions (empirical/theory_llm). A mode may auto-add an extension it depends
# on rather than erroring when the extension is missing — flipping to
# empirical-first without the empirical agents would be incoherent, so the
# script implies the dependency rather than making the user type both flags.
if [ -n "$MODE" ]; then
    case "$MODE" in
        empirical-first)
            if [ "$VARIANT" != "finance" ]; then
                echo "Error: --mode empirical-first is finance-only in v1."
                echo "  Macro support requires identification tooling for macro (issue #18) before this mode can ship."
                exit 1
            fi
            # Auto-imply --ext empirical (idempotent).
            if [[ ! " ${EXTENSIONS[*]} " =~ " empirical " ]]; then
                EXTENSIONS+=("empirical")
                echo "Info: --mode empirical-first implies --ext empirical (auto-added)."
            fi
            ;;
        report)
            # Report mode: referee an external submission instead of generating a paper.
            # Composes with --ext empirical / --ext theory_llm (adds extension auditors
            # to the fan-out) and with --light. No auto-implied extension — a theory-
            # only submission can be refereed without empirical agents.
            case "$VARIANT" in
                finance|macro) : ;;
                *)
                    echo "Error: --mode report supports --variant finance or macro."
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Unknown mode: $MODE"
            echo "Available modes: empirical-first, report"
            exit 1
            ;;
    esac
fi

# ── Variant configuration ──
case "$VARIANT" in
    finance)
        PAPER_TYPE="finance theory paper"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="finance theory — asset pricing, corporate finance, information economics, market design, financial intermediation, or behavioral finance"
        JOURNAL_LIST="Top-3 finance: JF, JFE, RFS, JF Insights & Perspectives (JFIP — top-3-fin tier on quality bar, JF-equivalent standard; CV credit lags; ≤7k words, single-insight, no R&R). Also: Review of Finance, Management Science, JFQA. Top accounting: JAR, JAE, TAR, RAS. Top-5 econ: AER, Econometrica, QJE, JPE, ReStud."
        AGENT_DIR="finance"
        INITIAL_TIER="top-3-fin"
        TIER_LADDER_PROSE='top-5 → top-3-fin → field → letters'
        TIER_LIST_INLINE='`top-5`, `top-3-fin`, `field`, `letters`'
        TIER_DOWNGRADE_EXAMPLES='for `top-3-fin`: JF, JFE, RFS, JF Insights \& Perspectives; for `field`: JFQA, Review of Finance, Management Science; for `letters`: Economics Letters'
        ;;
    macro)
        PAPER_TYPE="macroeconomics theory paper"
        TARGET_JOURNALS="top-5 economics journal (AER, Econometrica, QJE, JPE, ReStud) or leading macro field journal (JME, JEDC, AEJ:Macro)"
        DOMAIN_AREAS="macroeconomics"
        JOURNAL_LIST="Top-5 econ: AER, Econometrica, QJE, JPE, ReStud, AER Insights (top-5 tier on quality bar, AER-equivalent 'same standards'; CV credit lags; ≤6k words, single-mechanism). Top-3 finance: JF, JFE, RFS. Macro field: JME, JEDC, AEJ:Macro, AEJ:Micro, JIE, JET, RED."
        AGENT_DIR="macro"
        INITIAL_TIER="top-5"
        TIER_LADDER_PROSE='top-5 → field → letters'
        TIER_LIST_INLINE='`top-5`, `field`, `letters`'
        TIER_DOWNGRADE_EXAMPLES='for `top-5`: AER, Econometrica, QJE, JPE, ReStud, AER Insights; for `field`: JME, JEDC, AEJ:Macro, RED; for `letters`: Economics Letters'
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: finance, macro"
        exit 1
        ;;
esac

# ── Mode-conditional overrides for variant descriptors ──
# Mode flags can re-frame what kind of paper the deploy produces. PAPER_TYPE
# and DOMAIN_AREAS feed CLAUDE.md's opening prose, the agent metadata
# descriptions, and the literature-scout's variant context — they need to
# accurately describe an empirical-first deploy as such, not as a theory
# paper. TARGET_JOURNALS does not change (top-3 finance journals publish
# both theory and empirical work). JOURNAL_LIST also unchanged.
DOC_SUBTITLE="Autonomous Theory Paper Pipeline"
if [ "$MODE" = "empirical-first" ]; then
    case "$VARIANT" in
        finance)
            # Article-safe: starts with consonant ("c") so the "a {{PAPER_TYPE}}"
            # template in core.md reads correctly. (Switching to "an" would
            # break the default-mode "a finance theory paper" wording.)
            PAPER_TYPE="causal-identification empirical finance paper"
            DOMAIN_AREAS="empirical finance — asset pricing, corporate finance, information economics, market design, financial intermediation, or behavioral finance — with the contribution resting on a credibly-identified causal estimand plus a prose+DAG mechanism"
            DOC_SUBTITLE="Autonomous Empirical Paper Pipeline"
            ;;
    esac
elif [ "$MODE" = "report" ]; then
    # Report mode reframes the project as refereeing an external submission rather
    # than generating a paper. PAPER_TYPE and DOC_SUBTITLE flow into the assembled
    # runtime doc (core_report.md). DOMAIN_AREAS keeps the variant's value — the
    # referee agents are calibrated to that domain (the journal-role string).
    PAPER_TYPE="external paper submission under review"
    DOC_SUBTITLE="Autonomous Referee Report Pipeline"
fi

# ── Resolve paths ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR_REL=".claude"
CLAUDE_AGENTS_REL="$CLAUDE_DIR_REL/agents"
CLAUDE_SKILLS_REL="$CLAUDE_DIR_REL/skills"
CLAUDE_SETTINGS_REL="$CLAUDE_DIR_REL/settings.json"
CODEX_DIR_REL=".agents"
CODEX_SUBAGENT_DIR_REL=".codex"
CODEX_AGENTS_REL="$CODEX_SUBAGENT_DIR_REL/agents"
CODEX_SKILLS_REL="$CODEX_DIR_REL/skills"
GEMINI_DIR_REL=".gemini"
GEMINI_AGENTS_REL="$GEMINI_DIR_REL/agents"
GEMINI_SETTINGS_REL="$GEMINI_DIR_REL/settings.json"


MODEL_OVERRIDE_ARGS=()
if [ "$LIGHT" = "1" ]; then
    MODEL_OVERRIDE_ARGS=(--model-override sonnet)
fi

# ── Mode-overlay paths ──
# When --mode is set, the variant assemblers append a mode-specific shared
# bodies dir (consulted before the base shared dir; first match wins, so a
# mode override of `theory-generator-core.md` shadows the base body) and a
# mode-specific vocab overlay (merged onto the base variant vocab; later
# layer wins on duplicate keys, so mode-specific values override defaults).
# Sourcing both via per-mode dirs lets future modes drop in their own
# overrides without further setup.sh wiring.
MODE_BODIES_OVERLAY=""
MODE_VOCAB_OVERLAY=""
if [ -n "$MODE" ]; then
    mode_slug="${MODE//-/_}"  # 'empirical-first' → 'empirical_first'
    candidate_bodies="$SCRIPT_DIR/templates/agent_bodies/shared_modes/${mode_slug}"
    candidate_vocab="$SCRIPT_DIR/templates/agents/${AGENT_DIR}_modes/${mode_slug}/vocab.json"
    if [ -d "$candidate_bodies" ]; then
        MODE_BODIES_OVERLAY="$candidate_bodies"
    fi
    if [ -f "$candidate_vocab" ]; then
        MODE_VOCAB_OVERLAY="$candidate_vocab"
    fi
    # Either layer may be empty if the mode has no overrides at that layer
    # (e.g., a pure-vocab mode with no body overrides). But shipping a mode
    # name with neither layer present is a configuration error.
    if [ -z "$MODE_BODIES_OVERLAY" ] && [ -z "$MODE_VOCAB_OVERLAY" ]; then
        echo "Error: --mode $MODE has no overlay assets for variant $VARIANT."
        echo "  Expected at least one of:"
        echo "    $candidate_bodies/"
        echo "    $candidate_vocab"
        exit 1
    fi
fi

assemble_claude_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mode overlay reaches shared agents too: a mode-specific {id}.md in
    # MODE_BODIES_OVERLAY shadows the base shared body for that one agent
    # (e.g., a future mode-specific referee-mechanism), and MODE_VOCAB_OVERLAY
    # supplies any vocab keys the override references. Variant-agent shared
    # bodies (theory-generator-core.md etc.) live in the same overlay dir
    # under -core.md and are picked up by the variant assembler, not here.
    #
    # Vocab boundary: shared-agent bodies must not reference base variant
    # vocab keys ({{DOMAIN}}, {{SUBMISSION_TIER}}, etc.) — the variant vocab
    # is intentionally not passed here. If a future shared body needs vocab
    # composition, the substitution must come from MODE_VOCAB_OVERLAY only,
    # which means it can only differ across modes, not across variants.
    # KeyError fires loudly on unresolved {{KEY}}, so the boundary is enforced.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    # Shared defaults always come first; the mode overlay (when set) is
    # layered on top and wins on duplicate keys. The default file supplies
    # values for keys referenced by shared-agent metadata or bodies in the
    # no-mode case (e.g., IDEA_PROTOTYPER_DESCRIPTION).
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_claude_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_claude_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")
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
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_codex_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors assemble_claude_shared_agents — see comment there for the
    # MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY threading rationale.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir"
}

assemble_codex_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_codex_subagents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir"
}

assemble_gemini_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors assemble_claude_shared_agents — see comment there for the
    # MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY threading rationale.
    local bodies_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && bodies_args+=(--bodies-dir "$MODE_BODIES_OVERLAY")
    bodies_args+=(--bodies-dir "$template_root/templates/agent_bodies/shared")
    local vocab_args=()
    vocab_args+=(--vocab "$template_root/templates/agent_bodies/shared/vocab.json")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_shared_agents.json" \
        "${bodies_args[@]}" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_gemini_variant_agents() {
    local template_root="$1"
    local variant="$2"
    local dest_dir="$3"
    local vocab_file="$template_root/templates/agents/${variant}/vocab.json"
    local vocab_args=()
    [ -f "$vocab_file" ] && vocab_args=(--vocab "$vocab_file")
    [ -n "$MODE_VOCAB_OVERLAY" ] && vocab_args+=(--vocab "$MODE_VOCAB_OVERLAY")
    local shared_args=()
    [ -n "$MODE_BODIES_OVERLAY" ] && shared_args+=(--shared-bodies-dir "$MODE_BODIES_OVERLAY")
    shared_args+=(--shared-bodies-dir "$template_root/templates/agent_bodies/shared")

    python3 "$template_root/scripts/assemble_gemini_agents.py" \
        --metadata "$template_root/templates/agent_metadata/claude_variant_agents.json" \
        --bodies-dir "$template_root/templates/agents/${variant}" \
        "${shared_args[@]}" \
        "${vocab_args[@]}" \
        --output-dir "$dest_dir" \
        "${MODEL_OVERRIDE_ARGS[@]}"
}

assemble_claude_skills() {
    local template_root="$1"
    local metadata_file="$2"
    local bodies_dir="$3"
    local dest_dir="$4"

    python3 "$template_root/scripts/assemble_claude_skills.py" \
        --metadata "$metadata_file" \
        --bodies-dir "$bodies_dir" \
        --output-dir "$dest_dir"
}

if [ "$LOCAL" = "1" ]; then
    # Local test mode — no clone, no git, no prereq checks
    PROJECT_NAME="${PROJECT_NAME:-test_output/$VARIANT}"
    TEMPLATE_ROOT="$SCRIPT_DIR"

    # Resolve OUT_DIR: absolute path stays absolute, relative anchors to SCRIPT_DIR
    case "$PROJECT_NAME" in
        /*) OUT_DIR="$PROJECT_NAME" ;;
        *)  OUT_DIR="$SCRIPT_DIR/$PROJECT_NAME" ;;
    esac

    # Safety: refuse non-empty target unless it's under test_output/ (the dev scratch path).
    # The previous unconditional rm -rf wiped a real folder — see git log.
    if [ -d "$OUT_DIR" ] && [ "$(ls -A "$OUT_DIR" 2>/dev/null)" ]; then
        case "$OUT_DIR" in
            */test_output/*)
                : # dev scratch — wipe and continue
                ;;
            *)
                echo "Error: $OUT_DIR already exists and is not empty."
                echo "Refusing to overwrite. Move or delete the directory first, or pick a different project name."
                exit 1
                ;;
        esac
    fi

    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR/$CLAUDE_AGENTS_REL"
    mkdir -p "$OUT_DIR/$CODEX_AGENTS_REL"
    mkdir -p "$OUT_DIR/$GEMINI_AGENTS_REL"
    # Copy shared project files
    mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL"
    cp "$SCRIPT_DIR/$CLAUDE_SETTINGS_REL" "$OUT_DIR/$CLAUDE_DIR_REL/"
    mkdir -p "$OUT_DIR/$GEMINI_DIR_REL"
    cp "$SCRIPT_DIR/$GEMINI_SETTINGS_REL" "$OUT_DIR/$GEMINI_DIR_REL/"
    # Project-specific gitignore (tracks paper/, output/, code/; ignores data
    # blobs + build artifacts). Production mode copies this at the cleanup step
    # (line ~1878), but --local exits before reaching it, so copy it here too.
    # Using the template repo's own .gitignore would ignore paper/, output/,
    # code/, process_log/ — and since .gitignore is in the manifest's
    # files_replace list, update.sh would then clobber a real project's correct
    # gitignore with one that untracks the entire research output.
    cp "$SCRIPT_DIR/templates/gitignore_project" "$OUT_DIR/.gitignore"
    # dashboard.html visualizes pipeline_state.json; report mode (one-shot audit
    # fan-out) doesn't produce one, so the dashboard would be empty/misleading.
    if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
        cp "$SCRIPT_DIR/dashboard.html" "$OUT_DIR/"
    fi

    echo "Local test mode: $VARIANT → $OUT_DIR"
else
    # Production mode — clone, check prereqs, full setup
    PROJECT_NAME="${PROJECT_NAME:-my-research-paper}"

    echo "Checking prerequisites..."
    missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git >/dev/null 2>&1 || missing+=("git")
    command -v claude >/dev/null 2>&1 || missing+=("claude (npm install -g @anthropic-ai/claude-code)")
    command -v uv >/dev/null 2>&1 || missing+=("uv (curl -LsSf https://astral.sh/uv/install.sh | sh)")
    if [[ "$(uname)" == "Linux" ]]; then
        command -v bwrap >/dev/null 2>&1 || missing+=("bubblewrap (sudo apt-get install bubblewrap)")
    fi
    # Git identity is required: setup.sh runs `git commit` on the new project, and
    # `set -e` aborts the whole script (skipping the auto-publish step) if commit
    # fails with "Author identity unknown". Check both global and local config.
    if ! git config --get user.email >/dev/null 2>&1 || ! git config --get user.name >/dev/null 2>&1; then
        missing+=("git identity (run: git config --global user.email \"you@example.com\" && git config --global user.name \"Your Name\")")
    fi
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing dependencies:"
        for dep in "${missing[@]}"; do echo "  - $dep"; done
        exit 1
    fi
    echo "All prerequisites found."

    if [ -e "$PROJECT_NAME" ]; then
        echo "Error: $PROJECT_NAME already exists"
        exit 1
    fi

    echo "Cloning template into $PROJECT_NAME..."
    git clone https://github.com/alejandroll10/zeropaper.git "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    git remote remove origin
    rm -rf .git
    git init -q -b main

    TEMPLATE_ROOT="."
    OUT_DIR="."
fi

# ── Assemble runtime docs ──
echo "Assembling runtime docs for variant: $VARIANT..."

if [ "$MANUAL" = "1" ]; then
    CORE="$TEMPLATE_ROOT/templates/shared/core_manual.md"
    # In manual mode, each runtime gets its own session guidance and no discipline block.
    CLAUDE_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session_manual.md"
    CODEX_SESSION="$TEMPLATE_ROOT/templates/runtime/codex/session_manual.md"
    GEMINI_SESSION="$TEMPLATE_ROOT/templates/runtime/gemini/session_manual.md"
elif [ "$MODE" = "report" ]; then
    CORE="$TEMPLATE_ROOT/templates/shared/core_report.md"
    # Report mode follows the manual-mode pattern of per-runtime session files
    # (each runtime has slightly different orchestration affordances), with no
    # discipline block (the workflow IS the discipline).
    CLAUDE_SESSION="$TEMPLATE_ROOT/templates/runtime/claude/session_report.md"
    CODEX_SESSION="$TEMPLATE_ROOT/templates/runtime/codex/session_report.md"
    GEMINI_SESSION="$TEMPLATE_ROOT/templates/runtime/gemini/session_report.md"
else
    CORE="$TEMPLATE_ROOT/templates/shared/core.md"
    # In autonomous mode, all runtimes share the Claude session block and codex/gemini add discipline.
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

# ── Manual mode: pre-generate agent and skill catalogs for runtime docs ──
CATALOG_ARGS=()
CODEX_CATALOG_ARGS=()
if [ "$MANUAL" = "1" ]; then
    CATALOG_TMPDIR="$(mktemp -d)"
    trap 'rm -rf "$CATALOG_TMPDIR"' EXIT
    AGENT_CATALOG_FILE="$CATALOG_TMPDIR/agents.md"
    SKILL_CATALOG_FILE="$CATALOG_TMPDIR/skills.md"
    CODEX_SKILL_CATALOG_FILE="$CATALOG_TMPDIR/skills_codex.md"

    AGENT_METADATA_ARGS=(
        --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json"
        --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json"
    )
    # Skill metadata for the Claude/Gemini catalog. Codex's catalog is built
    # separately below — codex-math is omitted there because the codex runtime
    # IS the proof-verification backend the skill shells out to.
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
    for ext in "${EXTENSIONS[@]}"; do
        case "$ext" in
            empirical)
                AGENT_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json"
                    --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json"
                )
                SKILL_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json"
                )
                CODEX_SKILL_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json"
                )
                ;;
            theory_llm)
                AGENT_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json"
                )
                SKILL_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json"
                )
                CODEX_SKILL_METADATA_ARGS+=(
                    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json"
                )
                ;;
        esac
    done

    # Vocab args mirror the assembler convention: shared defaults first, then
    # base variant vocab, then mode overlay (last-write-wins on duplicate keys).
    # Without the shared defaults the catalog leaks shared-agent {{KEY}} tokens
    # like {{IDEA_PROTOTYPER_DESCRIPTION}}; without the variant vocab it leaks
    # variant-agent {{KEY}} tokens like {{THEORY_GEN_DESCRIPTION}}.
    CATALOG_VOCAB_ARGS=(--vocab "$TEMPLATE_ROOT/templates/agent_bodies/shared/vocab.json")
    [ -f "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json" ] && \
        CATALOG_VOCAB_ARGS+=(--vocab "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json")
    [ -n "$MODE_VOCAB_OVERLAY" ] && CATALOG_VOCAB_ARGS+=(--vocab "$MODE_VOCAB_OVERLAY")

    python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
        "${AGENT_METADATA_ARGS[@]}" \
        "${CATALOG_VOCAB_ARGS[@]}" \
        --output "$AGENT_CATALOG_FILE"
    python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
        "${SKILL_METADATA_ARGS[@]}" \
        "${CATALOG_VOCAB_ARGS[@]}" \
        --output "$SKILL_CATALOG_FILE"
    python3 "$TEMPLATE_ROOT/scripts/generate_catalog.py" \
        "${CODEX_SKILL_METADATA_ARGS[@]}" \
        "${CATALOG_VOCAB_ARGS[@]}" \
        --output "$CODEX_SKILL_CATALOG_FILE"

    CATALOG_ARGS=(--agent-catalog "$AGENT_CATALOG_FILE" --skill-catalog "$SKILL_CATALOG_FILE")
    CODEX_CATALOG_ARGS=(--agent-catalog "$AGENT_CATALOG_FILE" --skill-catalog "$CODEX_SKILL_CATALOG_FILE")
fi

if [ "$LOCAL" = "1" ]; then
    CLAUDE_MD_OUT="$OUT_DIR/CLAUDE.md"
    AGENTS_MD_OUT="$OUT_DIR/AGENTS.md"
    GEMINI_MD_OUT="$OUT_DIR/GEMINI.md"
    SESSION_OUT_DIR="$OUT_DIR/docs"
else
    CLAUDE_MD_OUT="CLAUDE.md"
    AGENTS_MD_OUT="AGENTS.md"
    GEMINI_MD_OUT="GEMINI.md"
    SESSION_OUT_DIR="docs"
fi

# Flag-gated halt pointer at {{CORE_BYPASS_GUARD}} in the orchestrator doc. Default
# (flag absent) leaves the placeholder empty — recording stays agent-driven via the
# injected pointer + docs/core_bypass.md and the runtime doc does not grow. No-op
# for core_manual.md / core_report.md, which lack the placeholder.
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

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$CLAUDE_SESSION" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --initial-tier "$INITIAL_TIER" \
    --tier-ladder-prose "$TIER_LADDER_PROSE" \
    --tier-list-inline "$TIER_LIST_INLINE" \
    --doc-name "CLAUDE.md" \
    --doc-subtitle "$DOC_SUBTITLE" \
    --agent-dir "$CLAUDE_AGENTS_REL" \
    --skill-dir "$CLAUDE_SKILLS_REL" \
    --session-out "$SESSION_OUT_DIR/start_session_claude.md" \
    "${SEED_ARGS[@]}" \
    "${BYPASS_HALT_ARGS[@]}" \
    "${CATALOG_ARGS[@]}" \
    --output "$CLAUDE_MD_OUT"

CODEX_DISCIPLINE_ARGS=()
# Discipline injection is autonomous-pipeline orchestration guidance (Stage 0→10
# routing, gate handling, etc.). Manual mode has no pipeline; report mode has its
# own runtime workflow in core_report.md and session_report.md and would only get
# noise from the autonomous orchestrator's discipline.
if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
    CODEX_DISCIPLINE_ARGS=(--discipline "$TEMPLATE_ROOT/templates/runtime/codex/session.md")
fi

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$CODEX_SESSION" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --initial-tier "$INITIAL_TIER" \
    --tier-ladder-prose "$TIER_LADDER_PROSE" \
    --tier-list-inline "$TIER_LIST_INLINE" \
    --doc-name "AGENTS.md" \
    --doc-subtitle "$DOC_SUBTITLE" \
    --agent-dir "$CODEX_AGENTS_REL" \
    --skill-dir "$CODEX_SKILLS_REL" \
    --session-out "$SESSION_OUT_DIR/start_session_codex.md" \
    "${CODEX_DISCIPLINE_ARGS[@]}" \
    "${SEED_ARGS[@]}" \
    "${BYPASS_HALT_ARGS[@]}" \
    "${CODEX_CATALOG_ARGS[@]}" \
    --output "$AGENTS_MD_OUT"

GEMINI_DISCIPLINE_ARGS=()
# See CODEX_DISCIPLINE_ARGS comment above; same rationale for report mode.
if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
    GEMINI_DISCIPLINE_ARGS=(--discipline "$TEMPLATE_ROOT/templates/runtime/gemini/session.md")
fi

python3 "$TEMPLATE_ROOT/scripts/assemble_runtime_doc.py" \
    --core "$CORE" \
    --session "$GEMINI_SESSION" \
    --paper-type "$PAPER_TYPE" \
    --target-journals "$TARGET_JOURNALS" \
    --domain-areas "$DOMAIN_AREAS" \
    --initial-tier "$INITIAL_TIER" \
    --tier-ladder-prose "$TIER_LADDER_PROSE" \
    --tier-list-inline "$TIER_LIST_INLINE" \
    --doc-name "GEMINI.md" \
    --doc-subtitle "$DOC_SUBTITLE" \
    --agent-dir "$GEMINI_AGENTS_REL" \
    --skill-dir "$GEMINI_DIR_REL/skills" \
    --session-out "$SESSION_OUT_DIR/start_session_gemini.md" \
    "${GEMINI_DISCIPLINE_ARGS[@]}" \
    "${SEED_ARGS[@]}" \
    "${BYPASS_HALT_ARGS[@]}" \
    "${CATALOG_ARGS[@]}" \
    --output "$GEMINI_MD_OUT"

echo "  ✓ Runtime docs assembled (CLAUDE.md + AGENTS.md + GEMINI.md)"

# ── Assemble agents ──
echo "Copying agents..."

if [ "$LOCAL" = "1" ]; then
    AGENTS_OUT="$OUT_DIR/$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$OUT_DIR/$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$OUT_DIR/$GEMINI_AGENTS_REL"
else
    AGENTS_OUT="$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$GEMINI_AGENTS_REL"
    mkdir -p "$AGENTS_OUT"
    mkdir -p "$CODEX_AGENTS_OUT"
    mkdir -p "$GEMINI_AGENTS_OUT"
fi

assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"
assemble_codex_shared_agents "$TEMPLATE_ROOT" "$CODEX_AGENTS_OUT"
assemble_gemini_shared_agents "$TEMPLATE_ROOT" "$GEMINI_AGENTS_OUT"

if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" ]; then
    assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
    assemble_codex_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$CODEX_AGENTS_OUT"
    assemble_gemini_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GEMINI_AGENTS_OUT"
fi

echo "  ✓ Agents assembled (shared + ${AGENT_DIR})"

# ── Prune agents not used in --mode report ──
# Report mode only invokes the audit fan-out + report-synthesizer. Generative,
# pipeline-management, scoring, broad-survey, and writing-style agents have no
# job here. Removing them at assembly time prevents accidental invocation and
# keeps the deployed .claude/agents/ catalog focused. Audit, polish-*, referee*,
# bib-verifier, novelty-checker, self-attacker, debugger, report-synthesizer
# stay; extension generative agents (empiricist, identification-designer,
# experiment-designer) are pruned per-extension below by the same function.
prune_report_mode_agents() {
    [ "$MODE" = "report" ] || return 0
    local _name
    for _name in "$@"; do
        rm -f "$AGENTS_OUT/${_name}.md" "$CODEX_AGENTS_OUT/${_name}.toml" "$GEMINI_AGENTS_OUT/${_name}.md"
    done
}

# Core agents not deployed in report mode (rationale documented in
# templates/runtime/{claude,codex,gemini}/session_report.md's "What this mode
# does not do" block). Extension generative agents are pruned in the extension
# block below after they have been assembled.
prune_report_mode_agents \
    theory-generator \
    paper-writer \
    idea-generator \
    idea-reviewer \
    idea-prototyper \
    theory-explorer \
    last-resort \
    scribe \
    triager \
    puzzle-triager \
    branch-manager \
    editor \
    scorer \
    scorer-freeform \
    literature-scout \
    gap-scout \
    style \
    faithful-drift-auditor

if [ "$MODE" = "report" ]; then
    echo "  ✓ Pruned generative / management agents for --mode report"
fi

# ── Inject variant context into agents ──
VARIANT_BLOCK="
## Variant context
- **Paper type:** ${PAPER_TYPE}
- **Target journals:** ${JOURNAL_LIST}
- **Domain:** ${DOMAIN_AREAS}
"

for agent in literature-scout gap-scout novelty-checker theory-explorer referee referee-freeform scorer scorer-freeform editor branch-manager last-resort paper-writer style report-synthesizer; do
    if [ -f "$AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$AGENTS_OUT/$agent.md"
    fi
    if [ -f "$CODEX_AGENTS_OUT/$agent.toml" ]; then
        # Insert before the closing ''' in the TOML multiline string
        # Use awk to find the LAST ''' and insert the block before it
        awk -v block="$VARIANT_BLOCK" '
        { lines[NR] = $0 }
        /^'\'''\'''\''$/ { last = NR }
        END {
            for (i = 1; i <= NR; i++) {
                if (i == last) print block
                print lines[i]
            }
        }' "$CODEX_AGENTS_OUT/$agent.toml" > "$CODEX_AGENTS_OUT/$agent.toml.tmp" \
        && mv "$CODEX_AGENTS_OUT/$agent.toml.tmp" "$CODEX_AGENTS_OUT/$agent.toml"
    fi
    if [ -f "$GEMINI_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GEMINI_AGENTS_OUT/$agent.md"
    fi
done
echo "  ✓ Variant context injected into agents"

# ── Faithful-mode contract pointer for developing agents (--faithful only) ──
# Faithful mode adds a short pointer to *developing* agents — those that
# produce paper content — directing them to read `output/seed/mechanism_contract.md`
# before producing output. *Evaluators* (scorer, referees, auditors, novelty-checker,
# self-attacker, idea-{prototyper,reviewer}, branch-manager) stay impartial: quoting
# the contract into them would corrupt the evaluation signal. The faithful constraint
# enters at the orchestrator's routing of evaluator verdicts (see faithful.md),
# not at the evaluators themselves.
#
# `inject_faithful_into_agents` is called once after core agent assembly and once
# inside each extension block (after the extension finishes assembling its own
# agents) so extension developing agents (empiricist, identification-designer,
# experiment-designer, etc.) also get the pointer. A no-op when FAITHFUL=0.
inject_faithful_into_agents() {
    [ "$FAITHFUL" = "1" ] || return 0
    local _inject_file="$TEMPLATE_ROOT/templates/shared/faithful_inject.md"
    if [ ! -f "$_inject_file" ]; then
        echo "Error: faithful inject template not found: $_inject_file" >&2
        exit 1
    fi
    local _block
    _block=$(cat "$_inject_file")
    local _agent
    for _agent in "$@"; do
        if [ -f "$AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$CODEX_AGENTS_OUT/$_agent.toml" ]; then
            awk -v block="$_block" '
            { lines[NR] = $0 }
            /^'\'''\'''\''$/ { last = NR }
            END {
                for (i = 1; i <= NR; i++) {
                    if (i == last) print block
                    print lines[i]
                }
            }' "$CODEX_AGENTS_OUT/$_agent.toml" > "$CODEX_AGENTS_OUT/$_agent.toml.tmp" \
            && mv "$CODEX_AGENTS_OUT/$_agent.toml.tmp" "$CODEX_AGENTS_OUT/$_agent.toml"
        fi
        if [ -f "$GEMINI_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GEMINI_AGENTS_OUT/$_agent.md"
        fi
    done
}

# `inject_bash_background_into_agents` appends the no-nohup / use-a-harness-
# tracked-background-job note to every Bash-capable agent. Unconditional (unlike
# the faithful injector): subagents never see the runtime doc, so a heavy job
# launched by e.g. theory-explorer/empiricist/experiment-designer would otherwise
# go unmonitored. Called after core assembly and inside each extension block;
# the file-existence guards make it a no-op for not-yet-assembled agents.
inject_bash_background_into_agents() {
    local _inject_file="$TEMPLATE_ROOT/templates/shared/bash_background.md"
    if [ ! -f "$_inject_file" ]; then
        echo "Error: bash-background inject template not found: $_inject_file" >&2
        exit 1
    fi
    local _block
    _block=$(cat "$_inject_file")
    local _agent
    for _agent in "$@"; do
        if [ -f "$AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$CODEX_AGENTS_OUT/$_agent.toml" ]; then
            awk -v block="$_block" '
            { lines[NR] = $0 }
            /^'\'''\'''\''$/ { last = NR }
            END {
                for (i = 1; i <= NR; i++) {
                    if (i == last) print block
                    print lines[i]
                }
            }' "$CODEX_AGENTS_OUT/$_agent.toml" > "$CODEX_AGENTS_OUT/$_agent.toml.tmp" \
            && mv "$CODEX_AGENTS_OUT/$_agent.toml.tmp" "$CODEX_AGENTS_OUT/$_agent.toml"
        fi
        if [ -f "$GEMINI_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GEMINI_AGENTS_OUT/$_agent.md"
        fi
    done
}

# `inject_core_bypass_into_agents` appends the core-bypass guard pointer (issue
# #51) to agents that, mid-run, depend on a binding external source or a binding
# verification tool and could silently downgrade to a non-binding fallback when it
# is unavailable — i.e. agents that can themselves *detect* a bypass (source/cert
# failure, or a tool failure being misread as "source down", bypass conditions 1
# and 4 in docs/core_bypass.md). Gate-skip / agent-substitution (conditions 2-3)
# are orchestrator-only events an agent can't see while running, so they are not
# recorded by this inject; the orchestrator records them itself in default mode via
# the per-gate "Bypass recording" pointer in docs/stage_{2,4,5,6}.md (issue #61,
# off the runtime-doc char budget since stage docs are read on demand). The
# --halt-on-core-bypass flag additionally injects an orchestrator-side halt pointer
# into the runtime doc. Unconditional like the
# bash-background injector (subagents never see the runtime doc, and recording is
# the default behavior regardless of the --halt-on-core-bypass flag; the flag only
# adds the orchestrator-side halt pointer in the runtime doc). The pointer text
# degrades gracefully when there is no process_log/ (manual mode). File-existence
# guards make passing a not-yet-assembled agent a harmless no-op.
inject_core_bypass_into_agents() {
    local _inject_file="$TEMPLATE_ROOT/templates/shared/core_bypass_inject.md"
    if [ ! -f "$_inject_file" ]; then
        echo "Error: core-bypass inject template not found: $_inject_file" >&2
        exit 1
    fi
    local _block
    _block=$(cat "$_inject_file")
    local _agent
    for _agent in "$@"; do
        if [ -f "$AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$CODEX_AGENTS_OUT/$_agent.toml" ]; then
            awk -v block="$_block" '
            { lines[NR] = $0 }
            /^'\'''\'''\''$/ { last = NR }
            END {
                for (i = 1; i <= NR; i++) {
                    if (i == last) print block
                    print lines[i]
                }
            }' "$CODEX_AGENTS_OUT/$_agent.toml" > "$CODEX_AGENTS_OUT/$_agent.toml.tmp" \
            && mv "$CODEX_AGENTS_OUT/$_agent.toml.tmp" "$CODEX_AGENTS_OUT/$_agent.toml"
        fi
        if [ -f "$GEMINI_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GEMINI_AGENTS_OUT/$_agent.md"
        fi
    done
}

# Core (shared + variant) agents with a binding runtime dependency they could
# silently downgrade. Explicit list (not metadata-derived): "depends on a binding
# source/tool at run time" is not an existing metadata category, and an explicit,
# auditable list is clearer than approximating it via --has-tool. Keep in sync
# when adding such an agent. Extension agents get the pointer in their own blocks.
#   bib-verifier / novelty-checker / polish-bibliography / polish-institutions
#     — external lit sources (OpenAlex / Crossref / WebSearch).
#   math-auditor{,-freeform} — the codex-math tool; covered by bypass condition 4
#     (a codex-math outage must not be misread as "unverifiable, pass anyway").
_core_bypass_agents=(
    bib-verifier
    novelty-checker
    polish-bibliography
    polish-institutions
    math-auditor
    math-auditor-freeform
)
inject_core_bypass_into_agents "${_core_bypass_agents[@]}"
echo "  ✓ Core-bypass guard pointer injected into binding-source agents"

# Core developing agents — list comes from metadata `category: "developing"`,
# the single source of truth (see scripts/list_agents_by_category.py).
mapfile -t _core_developing_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --category developing \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: empty here means the lister errored (mapfile masks it under set -e),
# never a real result — there are always developing agents. Harmless when
# FAITHFUL=0 (injector is a no-op) but prevents a silent skip under --faithful.
if [ "${#_core_developing_agents[@]}" -eq 0 ]; then
    echo "Error: core developing-agent list is empty (lister failed or metadata missing)" >&2
    exit 1
fi
inject_faithful_into_agents "${_core_developing_agents[@]}"
if [ "$FAITHFUL" = "1" ]; then
    echo "  ✓ Faithful pointer injected into core developing agents"
fi

# Bash-capable core agents — list comes from metadata `tools` containing Bash.
mapfile -t _core_bash_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --has-tool Bash \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: mapfile masks python failure under set -e, so an empty list here
# means the lister errored or metadata is missing — never a real empty result.
if [ "${#_core_bash_agents[@]}" -eq 0 ]; then
    echo "Error: Bash-capable core agent list is empty (lister failed or metadata missing)" >&2
    exit 1
fi
inject_bash_background_into_agents "${_core_bash_agents[@]}"
echo "  ✓ Background-job note injected into Bash-capable core agents"

# ── Create project directories and initial files ──
echo "Creating project structure..."

if [ "$LOCAL" = "1" ]; then
    P="$OUT_DIR"
else
    P="."
fi

if [ "$MODE" = "report" ]; then
    # Report mode: read-only `submission/` (user drops the paper here), parallel
    # `audits/` outputs, single `report/referee_report.md` deliverable, and a
    # process log. No `paper/`, `code/`, `data/`, or `references/` — there is no
    # paper to write, no code to run on behalf of the authors, no data to fetch.
    # (The empirical extension still installs `code/utils/` for shared skills,
    # but no `code/analysis/` etc.)
    mkdir -p "$P/submission" "$P/audits" "$P/report" "$P/process_log"
    cat > "$P/submission/README.md" <<'SUBREADME'
# submission/ — drop the paper to be refereed here

Supported formats:

- PDF only — `submission/paper.pdf`
- LaTeX source bundle — `submission/main.tex` + `submission/sections/*.tex` + `submission/refs.bib` (optionally `submission/tables/`, `submission/figures/`, an internet appendix)
- Both — PDF for the audit agents that prefer typeset output, source for the
  agents that re-derive equations or verify cite keys

The pipeline treats this directory as **read-only**. Audit agents read from
here; they write to `audits/<name>.md`. The synthesizer writes the final
report to `report/referee_report.md`. The original submission is never
modified.

After dropping the submission, launch the runtime (claude / codex / gemini)
and say "run" or "start". The orchestrator runs Step 1 triage, fans out the
audit agents in parallel, then launches `report-synthesizer` to produce the
editor-facing referee report.

Each deployment is one-shot. If the editor sends a revised submission later,
that is a fresh `setup.sh --mode report ...` deployment on a fresh
`submission/` folder; this folder is not designed for v1/v2 cycling.
SUBREADME
else
    mkdir -p "$P/code/analysis" "$P/code/download" "$P/code/tmp" "$P/code/explore"
    mkdir -p "$P/data"
    mkdir -p "$P/paper/sections" "$P/paper/simulated_referee_reports"
    mkdir -p "$P/references"
fi

# ---------------------------------------------------------------------
# Pipeline fingerprint: arpipeline.sty + main.tex skeleton
# Bakes a deployment-unique UUID into four layers (LaTeX source commands,
# hyperref PDF metadata, custom /Info dict entries, and per-page white-
# on-white grep marker) so every paper produced by this deployment
# carries the magic prefix ARPIPELINE-FP-V1 for distribution detection.
# ---------------------------------------------------------------------
ARP_UUID=$(python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null)
ARP_DATE=$(date -u +%Y-%m-%d)
ARP_VERSION=$(cd "$TEMPLATE_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
if [ -z "$ARP_UUID" ]; then
    echo "ERROR: failed to generate fingerprint UUID (python3 unavailable or stdlib broken)." >&2
    echo "       Aborting setup; install python3 and retry." >&2
    exit 1
fi
# Skip the paper-skeleton install entirely under --mode report — there is no
# paper being produced, so the fingerprint .sty, main.tex, and IA template
# have nothing to attach to. The ARP_UUID is still recorded in the deployment
# manifest below for traceability.
if [ "$MODE" != "report" ]; then
    sed -e "s|{{ARP_UUID}}|$ARP_UUID|g" \
        -e "s|{{ARP_VERSION}}|$ARP_VERSION|g" \
        -e "s|{{ARP_DATE}}|$ARP_DATE|g" \
        "$TEMPLATE_ROOT/templates/paper_skeleton/arpipeline.sty.template" \
        > "$P/paper/arpipeline.sty"
    # Don't clobber an existing main.tex (e.g. --seed mode where the user has
    # pre-populated paper/main.tex). The .sty above is always overwritten —
    # it is pipeline infrastructure with a fresh UUID per deployment.
    if [ ! -f "$P/paper/main.tex" ]; then
        cp "$TEMPLATE_ROOT/templates/paper_skeleton/main.tex.template" "$P/paper/main.tex"
    fi
    # Internet appendix skeleton. paper-writer only populates it when a proof
    # exceeds ~3 pages or the in-paper appendix would otherwise blow past ~30%
    # of main-text length; otherwise it stays a no-op placeholder. Same skip-
    # if-exists guard as main.tex above.
    if [ ! -f "$P/paper/internet_appendix.tex" ]; then
        cp "$TEMPLATE_ROOT/templates/paper_skeleton/internet_appendix.tex.template" "$P/paper/internet_appendix.tex"
    fi
fi

if [ "$MANUAL" = "1" ]; then
    mkdir -p "$P/output"
elif [ "$MODE" = "report" ]; then
    # Report mode has no stages, no pipeline_state.json, no session/decision/
    # discussion/pattern logs to accumulate. The submission/audits/report/
    # process_log skeleton was created above; nothing else here.
    :
else
    # Stage 2b (theory exploration) is permanently skipped under
    # --mode empirical-first; don't create the empty dir there.
    STAGE2B_DIRS=()
    [ "$MODE" != "empirical-first" ] && STAGE2B_DIRS=("$P/output/stage2b/figures")
    mkdir -p "$P/output/stage0" "$P/output/stage1" "$P/output/stage2" "${STAGE2B_DIRS[@]}" "$P/output/stage3" "$P/output/stage4" "$P/output/puzzle_triage" "$P/output/post_pipeline"
    mkdir -p "$P/process_log/sessions" "$P/process_log/decisions" "$P/process_log/discussions" "$P/process_log/patterns"
fi

# Copy per-stage documentation (referenced from CLAUDE.md/AGENTS.md/GEMINI.md pointer blocks).
# Skipped in report mode — there are no stages to document, and the audit
# conventions live in core_report.md itself. The session pointer files
# (start_session_*.md) are written into docs/ separately by --session-out.
mkdir -p "$P/docs"
if [ "$MODE" != "report" ]; then
    cp "$TEMPLATE_ROOT/templates/shared/docs/"*.md "$P/docs/"
    # Substitute variant placeholders (same ones assemble_runtime_doc.py handles for core.md)
    for _docfile in "$P/docs/"*.md; do
        sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g" "$_docfile" && rm "${_docfile}.bak"
    done

    # Inject the variant-specific tier table into stage_4.md (multi-line content via sed -r)
    TIER_TABLE_FILE="$TEMPLATE_ROOT/templates/shared/tier_tables/${VARIANT}.md"
    if [ -f "$TIER_TABLE_FILE" ] && [ -f "$P/docs/stage_4.md" ]; then
        sed -i.bak -e "/{{TIER_TABLE}}/r $TIER_TABLE_FILE" -e "/{{TIER_TABLE}}/d" "$P/docs/stage_4.md" && rm "$P/docs/stage_4.md.bak"
    fi
else
    # Report mode skips the bulk stage-doc copy, but the core-bypass guard still
    # applies (the audit agents verify an external submission against binding
    # sources like OpenAlex). Copy just the doctrine doc the injected agent
    # pointer references. It has no variant placeholders, so no substitution.
    cp "$TEMPLATE_ROOT/templates/shared/docs/core_bypass.md" "$P/docs/"
fi

# Function to substitute {{SEED_OVERRIDE_*}} placeholders in all docs in $P/docs/.
# Called after shared docs copy AND after each extension copies its own docs, so
# extension-specific stage docs (e.g., stage_3a_empirical.md) also get substituted.
#
# Resolution order for each placeholder:
#   1. Collect placeholder keys: union of seed_overrides/*.md and (if FAITHFUL=1)
#      faithful_overrides/*.md basenames.
#   2. For each key, pick the override body:
#      - FAITHFUL=1: prefer faithful_overrides/<key>.md, fall back to
#        seed_overrides/<key>.md if no faithful version exists. This lets us
#        write only the *strict-delta* faithful overrides — for placeholders
#        where seeded behavior is already strict enough, faithful mode reuses
#        the seeded text.
#      - SEEDED=1 (and not FAITHFUL): use seed_overrides/<key>.md only.
#      - Neither: strip the placeholder.
apply_seed_overrides() {
    local seed_override_dir="$TEMPLATE_ROOT/templates/shared/seed_overrides"
    local faithful_override_dir="$TEMPLATE_ROOT/templates/shared/faithful_overrides"

    # Build the union of placeholder keys across both dirs.
    local _keys=()
    if [ -d "$seed_override_dir" ]; then
        for _f in "$seed_override_dir"/*.md; do
            [ -f "$_f" ] && _keys+=("$(basename "$_f" .md)")
        done
    fi
    # Always include faithful_overrides keys in the union — even when FAITHFUL=0.
    # This ensures placeholders that exist only in the faithful set (e.g., the
    # new Stage 1 OBVIOUS-forwarding override) get stripped cleanly in regular
    # and soft-seed modes rather than leaking into the deployed docs as raw
    # `{{SEED_OVERRIDE_*}}` text. The body-resolution step below still picks
    # the faithful body only when FAITHFUL=1.
    if [ -d "$faithful_override_dir" ]; then
        for _f in "$faithful_override_dir"/*.md; do
            [ -f "$_f" ] || continue
            local _k="$(basename "$_f" .md)"
            # Only add if not already in _keys (dedupe).
            local _found=0
            for _existing in "${_keys[@]:-}"; do
                [ "$_existing" = "$_k" ] && { _found=1; break; }
            done
            [ "$_found" = "0" ] && _keys+=("$_k")
        done
    fi

    [ "${#_keys[@]}" -eq 0 ] && return 0

    for _key in "${_keys[@]}"; do
        # Pick the override body for this key per the resolution order above.
        local _override=""
        if [ "$FAITHFUL" = "1" ] && [ -f "$faithful_override_dir/$_key.md" ]; then
            _override="$faithful_override_dir/$_key.md"
        elif [ "$SEEDED" = "1" ] && [ -f "$seed_override_dir/$_key.md" ]; then
            _override="$seed_override_dir/$_key.md"
        fi

        for _docfile in "$P/docs/"*.md; do
            grep -q "{{$_key}}" "$_docfile" || continue
            if [ -n "$_override" ]; then
                python3 -c "
import sys, pathlib
doc = pathlib.Path(sys.argv[1])
override = pathlib.Path(sys.argv[2]).read_text().rstrip()
doc.write_text(doc.read_text().replace('{{' + sys.argv[3] + '}}', override))
" "$_docfile" "$_override" "$_key"
            else
                # Strip placeholder and any immediately surrounding blank lines.
                python3 -c "
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
key = sys.argv[2]
p.write_text(re.sub(r'\n*\{\{' + re.escape(key) + r'\}\}\n*', '\n\n', p.read_text()))
" "$_docfile" "$_key"
            fi
        done
    done
}

apply_seed_overrides

# Create seed folder with instructions if --seed
if [ "$SEEDED" = "1" ]; then
    mkdir -p "$P/output/seed"
    if [ "$FAITHFUL" = "1" ]; then
    cat > "$P/output/seed/README.md" <<'SEEDREADME'
# Seed folder (faithful mode)

Drop your idea files here before launching the pipeline. The pipeline will read
everything in this folder as the seeded idea.

You can put anything here: markdown notes, PDFs, paper drafts, evaluation
reports, emails, code snippets — whatever describes the idea you want the
pipeline to develop.

This is a **faithful** run: the seed is treated as a contract. Before any other
agent fires, the orchestrator extracts `output/seed/mechanism_contract.md` from
your files — its named mechanism, structural invariants, theorem-statement
constraints, identification strategy, and stated contribution. That contract is
then quoted into every developing agent's launch prompt as a non-negotiable.

What the pipeline will do:
- Implement your seed faithfully — its named mechanism, headline result, and
  identification strategy stay intact.
- Add to / refine / extend the implementation where it can — extra theorems,
  comparative statics, robustness checks.
- Document any genuine impossibility (proof unrepairable, identification
  infeasible, prediction contradicted by data) in `output/seed/limitations.md`
  and ship the paper documenting the impossibility honestly.

What the pipeline will **not** do:
- Substitute a different mechanism, model class, or research design.
- Pivot to a more publishable framing.
- Promote a "buried" result over your stated headline.

If you wanted softer behavior — pipeline preserves the seed but may pivot under
puzzle-triage / refine framing under scorer recommendations — re-run setup with
`--seed` instead of `--faithful`.
SEEDREADME
        echo "  ✓ Seed folder created at output/seed/ (faithful mode) — drop your idea files there before launching"
    else
    cat > "$P/output/seed/README.md" <<'SEEDREADME'
# Seed folder

Drop your idea files here before launching the pipeline. The pipeline will read
everything in this folder as the seeded idea.

You can put anything here: markdown notes, PDFs, paper drafts, evaluation
reports, emails, code snippets — whatever describes the idea you want the
pipeline to develop.

The pipeline reads your files, builds a literature map, assesses maturity, and
enters at the appropriate stage. It will never silently abandon your seeded idea.
If a gate fails, it reports the issue rather than pivoting.
SEEDREADME
        echo "  ✓ Seed folder created at output/seed/ — drop your idea files there before launching"
    fi
fi

# Initial pipeline state (skipped in manual mode — no autonomous pipeline; also
# skipped in report mode — no stages or routing to track, just the audit log)
if [ "$MANUAL" = "1" ]; then
    : # no pipeline state
elif [ "$MODE" = "report" ]; then
    # Seed the audit log so the synthesizer has a stable file to read at the end.
    # The orchestrator appends the launch-time submission hash + per-agent rows
    # per session_report.md's "Update the audit log" instructions.
    cat > "$P/process_log/audit_log.md" <<'AUDITLOG'
# Audit log

The orchestrator computes one submission_hash at launch and records it here,
then appends one row per audit agent on completion. The synthesizer reads this
log before producing the report to confirm coverage.

submission_hash: <not yet computed — set at launch>

| agent | started | completed | output |
|-------|---------|-----------|--------|
AUDITLOG
elif [ "$SEEDED" = "1" ]; then
cat > "$P/process_log/pipeline_state.json" <<JSONEOF
{
  "current_stage": "seed_triage",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "theory_version": 1,
  "referee_round": 0,
  "reject_cosmetic_round": 0,
  "pivot_round": 0,
  "fix_empirics_round": 0,
  "bib_verify_round": 0,
  "polish_round": 0,
  "regeneration_round": 0,
  "harder_round_forced": false,
  "fallback_idea_sketch_name": null,
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "target_journal_tier": "__INITIAL_TIER__",
  "initial_journal_tier": "__INITIAL_TIER__",
  "status": "not_started",
  "seeded": true,
  "faithful": $([ "$FAITHFUL" = "1" ] && echo true || echo false),
  "halt_on_core_bypass": $([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo true || echo false),
  "scores": {},
  "stage2b_theory_version": null,
  "stage1_candidates": [],
  "history": []
}
JSONEOF
    sed -i.bak "s|__INITIAL_TIER__|$INITIAL_TIER|g" "$P/process_log/pipeline_state.json" && rm "$P/process_log/pipeline_state.json.bak"
else
cat > "$P/process_log/pipeline_state.json" <<'JSONEOF'
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "theory_version": 1,
  "referee_round": 0,
  "reject_cosmetic_round": 0,
  "pivot_round": 0,
  "fix_empirics_round": 0,
  "bib_verify_round": 0,
  "polish_round": 0,
  "regeneration_round": 0,
  "harder_round_forced": false,
  "fallback_idea_sketch_name": null,
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "target_journal_tier": "__INITIAL_TIER__",
  "initial_journal_tier": "__INITIAL_TIER__",
  "seeded": false,
  "faithful": false,
  "halt_on_core_bypass": __HALT_ON_CORE_BYPASS__,
  "status": "not_started",
  "scores": {},
  "stage2b_theory_version": null,
  "stage1_candidates": [],
  "history": []
}
JSONEOF
    sed -i.bak "s|__INITIAL_TIER__|$INITIAL_TIER|g; s|__HALT_ON_CORE_BYPASS__|$([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo true || echo false)|g" "$P/process_log/pipeline_state.json" && rm "$P/process_log/pipeline_state.json.bak"
fi

if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
    touch "$P/process_log/history.md"
fi

# Core-bypass degradation ledger (issue #51). Seeded for every autonomous mode
# that has a process_log/ (i.e. non-manual, including report mode). Agents and the
# orchestrator append one row per silent-degradation event per docs/core_bypass.md;
# a non-empty ledger must surface in the run summary. Manual mode has no process_log/,
# so the agent pointer there degrades to "state it in your returned report."
if [ "$MANUAL" = "0" ]; then
    cat > "$P/process_log/degradation_ledger.md" <<'LEDGEREOF'
# Degradation ledger — core-bypass events

Each row records a point where a **core** (a binding external source, a
verification gate, or a designated agent / stage step) was unavailable, skipped,
substituted, or replaced by a weaker fallback. See `docs/core_bypass.md` for the
guard. Default behavior is record-and-surface; under `--halt-on-core-bypass`
(`"halt_on_core_bypass": true` in pipeline_state.json) the run halts after
recording. A non-empty ledger MUST appear in the run summary — a degraded run
never reports clean success. Empty = no core was bypassed.

`action` ∈ {`recorded`, `halted`, `resolved`}. A `binding? = yes` row is
*unresolved* until the binding source is restored, the verification is re-run, and
its `action` is set to `resolved`. An unresolved binding row blocks
`status = "complete"` even in the default deploy: the session refuses to complete
and sets `status = "halted_core_bypass"` instead. This is the terminal backstop.
Only an operator-driven recovery may set a row `resolved` (a running session is not
authorized to self-clear). Report mode has no `pipeline_state.json` / `status`
machine, so the blocking rule does not apply there — rows are recorded and
surfaced in the returned report only.

| timestamp | stage | core | condition | why | fallback | binding? | action |
|-----------|-------|------|-----------|-----|----------|----------|--------|
LEDGEREOF
fi

# Faithful mode: seed pivot_log.md with a header + table skeleton so the
# orchestrator has a target to append to. Each routing decision that could
# affect the mechanism contract appends a row per faithful.md's instructions.
if [ "$FAITHFUL" = "1" ]; then
    cat > "$P/process_log/pivot_log.md" <<'PIVOTLOG'
# Pivot log (faithful mode)

Every potentially-mechanism-affecting routing decision is logged here. See
`CLAUDE.md` (the assembled `faithful.md` block) for the routing rules. Each row
records what an evaluator agent reported, how the orchestrator classified it
under the faithful contract, and why.

| timestamp | stage | agent | verdict | classification | rationale |
|-----------|-------|-------|---------|----------------|-----------|
PIVOTLOG
fi

echo "  ✓ Project structure created"

# ── Copy .env if available ──
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$P/.env"
    echo "  ✓ .env copied from template repo"
fi

# ── Install core Python deps ──
if [ "$LOCAL" = "0" ]; then
    uv pip install sympy matplotlib certifi -q 2>/dev/null \
        || echo "Note: install core deps manually: uv pip install sympy matplotlib certifi"
fi

# ── Assemble core skills ──
echo "Assembling core skills..."

if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

# SymPy skill (available for all variants — preloaded into math-touching subagents)
assemble_claude_skills \
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
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/codex_math_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/codex_math" \
    "$SKILLS_OUT"

# Copy codex-math utility scripts
mkdir -p "$P/code/utils/codex_math"
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
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/bib_verify_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/bib_verify" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy bib-verify utility scripts
mkdir -p "$P/code/utils/bib_verify"
cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"
cp "$TEMPLATE_ROOT/templates/utils/bib_verify/"verify_bib.sh "$P/code/utils/bib_verify/"
chmod +x "$P/code/utils/bib_verify/"openalex_check.py "$P/code/utils/bib_verify/"verify_bib.sh

# OpenAlex literature search skill (loaded by literature-scout, gap-scout, novelty-checker)
assemble_claude_skills \
    "$TEMPLATE_ROOT" \
    "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
    "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
    "$SKILLS_OUT"

python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
    --metadata "$TEMPLATE_ROOT/templates/skill_metadata/openalex_skills.json" \
    --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/openalex" \
    --output-dir "$CODEX_SKILLS_OUT"

# Copy OpenAlex utility script
mkdir -p "$P/code/utils/openalex"
cp "$TEMPLATE_ROOT/templates/utils/openalex/"openalex.py "$P/code/utils/openalex/"
chmod +x "$P/code/utils/openalex/"openalex.py

echo "  ✓ Core skills assembled"

# ── Apply extensions ──
if [ "$LOCAL" = "1" ]; then
    SKILLS_OUT="$OUT_DIR/$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$OUT_DIR/$CODEX_SKILLS_REL"
else
    SKILLS_OUT="$CLAUDE_SKILLS_REL"
    CODEX_SKILLS_OUT="$CODEX_SKILLS_REL"
fi

for ext in "${EXTENSIONS[@]}"; do
    case "$ext" in
        theory_llm)
            echo "Applying LLM experiment extension..."
            if [ -n "$MODE" ]; then
                echo "  Note: --mode $MODE does not currently propagate into the theory_llm extension agents."
                echo "        See scripts/apply_extension_theory_llm.sh header comment for the forward-compat path."
            fi
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            # NOTE: MODE_BODIES_OVERLAY / MODE_VOCAB_OVERLAY are intentionally NOT
            # threaded here yet — see apply_extension_theory_llm.sh header comment.
            # If a future mode wants mode-conditional theory_llm content, add the
            # three positionals (mirroring apply_extension_empirical.sh) and
            # remove the warning above.
            bash "$TEMPLATE_ROOT/scripts/apply_extension_theory_llm.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$LOCAL" \
                "$LIGHT_MODEL"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/theory_llm_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/theory_llm" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/theory_llm/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -c "
import sys; p=sys.argv[1]; d=sys.argv[2]
content=open(d).read(); inject=open(p).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', inject.rstrip()+'\n\n{{EXTENSION_STAGES}}'))
" "$INJECT" "$doc"
            done

            # Copy extension docs into project docs/ with placeholder substitution
            if [ -d "$TEMPLATE_ROOT/extensions/theory_llm/docs" ]; then
                cp "$TEMPLATE_ROOT/extensions/theory_llm/docs/"*.md "$P/docs/"
                for _docfile in "$TEMPLATE_ROOT/extensions/theory_llm/docs/"*.md; do
                    _name=$(basename "$_docfile")
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            # Fill theory_llm-only placeholders in shared docs / runtime docs.
            # Theory-only runs leave these placeholders to be stripped by the post-extension cleanup.
            python3 - \
                "$TEMPLATE_ROOT/extensions/theory_llm/stage2_rerun_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/stage3b_gate_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/state_fields_inject.md" \
                "$TEMPLATE_ROOT/extensions/theory_llm/state3b_doc_inject.md" \
                "$P/docs/stage_2.md" \
                "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" <<'PYEOF'
import json, os, sys
stage2 = open(sys.argv[1]).read()
stage3b_gate = open(sys.argv[2]).read()
state = open(sys.argv[3]).read()
state3b_doc = open(sys.argv[4]).read()
stage2_md = sys.argv[5]
runtime_docs = sys.argv[6:9]

def patch(path, pairs):
    if not os.path.exists(path):
        return
    with open(path) as f: t = f.read()
    new = t
    for needle, repl in pairs:
        new = new.replace(needle, repl)
    if new != t:
        with open(path, "w") as f: f.write(new)

patch(stage2_md, [
    ("{{THEORY_LLM_STAGE2_RERUN_ADDENDUM}}", stage2),
    ("{{THEORY_LLM_STAGE3B_GATE_ADDENDUM}}", stage3b_gate),
])

for d in runtime_docs:
    patch(d, [
        ("{{THEORY_LLM_STATE_FIELDS}}", state),
        ("{{THEORY_LLM_STATE3B_DOC}}", state3b_doc),
    ])

# pipeline_state.json: add stage3b_theory_version field, mirroring stage2b_theory_version.
state_path = os.path.join(os.path.dirname(stage2_md), "..", "process_log", "pipeline_state.json")
state_path = os.path.normpath(state_path)
if os.path.exists(state_path):
    with open(state_path) as f: data = json.load(f)
    if "stage3b_theory_version" not in data:
        # Insert immediately after stage3a_theory_version (if --ext empirical) or stage2b_theory_version.
        new = {}
        anchor = "stage3a_theory_version" if "stage3a_theory_version" in data else "stage2b_theory_version"
        for k, v in data.items():
            new[k] = v
            if k == anchor:
                new["stage3b_theory_version"] = None
        data = new
        with open(state_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
PYEOF

            # Theory_LLM extension developing agents — from metadata.
            mapfile -t _tllm_developing_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_developing_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_faithful_into_agents "${_tllm_developing_agents[@]}"

            mapfile -t _tllm_bash_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_bash_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_bash_background_into_agents "${_tllm_bash_agents[@]}"

            # Core-bypass guard: the LLM API is a binding source for both the
            # designer (runs experiments) and the reviewer (re-checks them).
            inject_core_bypass_into_agents experiment-designer experiment-reviewer

            # Report mode: --ext theory_llm is install-only (skills + LLM client).
            # Both experiment-designer (generative) and experiment-reviewer (audit
            # of pipeline-produced experiments) are pruned — there are no
            # pipeline-produced experiments to review on an external submission.
            prune_report_mode_agents experiment-designer experiment-reviewer
            if [ "$MODE" = "report" ]; then
                rm -f "$P/docs/stage_3b_experiments.md"
            fi
            echo "  ✓ LLM experiment extension applied"
            ;;
        empirical)
            echo "Applying empirical extension..."
            LIGHT_MODEL=""
            if [ "$LIGHT" = "1" ]; then LIGHT_MODEL="sonnet"; fi
            bash "$TEMPLATE_ROOT/scripts/apply_extension_empirical.sh" \
                "$TEMPLATE_ROOT" \
                "$P" \
                "$AGENTS_OUT" \
                "$CODEX_AGENTS_OUT" \
                "$GEMINI_AGENTS_OUT" \
                "$SKILLS_OUT" \
                "$AGENT_DIR" \
                "$LOCAL" \
                "$LIGHT_MODEL" \
                "$MODE_BODIES_OVERLAY" \
                "$MODE_VOCAB_OVERLAY" \
                "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json"

            python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
                --metadata "$TEMPLATE_ROOT/templates/skill_metadata/empirical_skills.json" \
                --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/empirical" \
                --output-dir "$CODEX_SKILLS_OUT"

            # Inject stage instructions into runtime docs at {{EXTENSION_STAGES}} placeholder
            INJECT="$TEMPLATE_ROOT/extensions/empirical/stages_inject.md"
            for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
                python3 -c "
import sys; p=sys.argv[1]; d=sys.argv[2]
content=open(d).read(); inject=open(p).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', inject.rstrip()+'\n\n{{EXTENSION_STAGES}}'))
" "$INJECT" "$doc"
            done

            # Copy extension docs into project docs/ with placeholder substitution
            if [ -d "$TEMPLATE_ROOT/extensions/empirical/docs" ]; then
                cp "$TEMPLATE_ROOT/extensions/empirical/docs/"*.md "$P/docs/"
                for _docfile in "$TEMPLATE_ROOT/extensions/empirical/docs/"*.md; do
                    _name=$(basename "$_docfile")
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
                done
            fi

            # Fill empirical-only placeholders in shared docs / runtime docs / scorer agent body.
            # Theory-only runs leave these placeholders to be stripped by the post-extension cleanup.
            python3 - \
                "$TEMPLATE_ROOT/extensions/empirical/stage2_rerun_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/stage3a_gate_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state_fields_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state3a_doc_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/playbook_inject.md" \
                "$TEMPLATE_ROOT/extensions/empirical/scorer_fertility_inject.md" \
                "$P/docs/stage_2.md" \
                "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
                "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" <<'PYEOF'
import json, os, sys
# Inject files are read raw — each file is responsible for its own leading/trailing
# whitespace. The final newline left by the editor IS content (it determines whether
# a blank line follows the substitution).
stage2 = open(sys.argv[1]).read()
stage3a_gate = open(sys.argv[2]).read()
state = open(sys.argv[3]).read()
state3a_doc = open(sys.argv[4]).read()
playbook = open(sys.argv[5]).read()
fertility = open(sys.argv[6]).read()
stage2_md = sys.argv[7]
runtime_docs = sys.argv[8:11]
scorer_files = sys.argv[11:14]

def patch(path, pairs):
    if not os.path.exists(path):
        return
    with open(path) as f: t = f.read()
    new = t
    for needle, repl in pairs:
        new = new.replace(needle, repl)
    if new != t:
        with open(path, "w") as f: f.write(new)

# Stage_2.md: two placeholders. Each placeholder lives on its own line; the
# placeholder line's trailing newline is preserved by replacing only the
# placeholder text (no extra "\n" appended).
patch(stage2_md, [
    ("{{EMPIRICAL_STAGE2_RERUN_ADDENDUM}}", stage2),
    ("{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}", stage3a_gate),
])

# Runtime docs (CLAUDE.md / AGENTS.md / GEMINI.md): state JSON field + state-doc paragraph + playbook addendum.
for d in runtime_docs:
    patch(d, [
        ("{{EMPIRICAL_STATE_FIELDS}}", state),
        ("{{EMPIRICAL_STATE3A_DOC}}", state3a_doc),
        ("{{EMPIRICAL_PLAYBOOK_ADDENDUM}}", playbook),
    ])

# Scorer agent bodies: replace the comment marker with the empirical fertility addendum.
for s in scorer_files:
    patch(s, [
        ("<!-- EMPIRICAL_FERTILITY_ADDENDUM -->", fertility),
    ])

# pipeline_state.json: add stage3a_theory_version field, mirroring stage2b_theory_version.
# Manual mode skips state file creation (see setup.sh ~line 626), so guard on existence.
state_path = os.path.join(os.path.dirname(stage2_md), "..", "process_log", "pipeline_state.json")
state_path = os.path.normpath(state_path)
if os.path.exists(state_path):
    with open(state_path) as f: data = json.load(f)
    if "stage3a_theory_version" not in data:
        # Insert immediately after stage2b_theory_version to preserve key order in the file.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage2b_theory_version":
                new["stage3a_theory_version"] = None
        data = new
    if "identification_plan_revision_round" not in data:
        # Insert immediately after stage3a_theory_version. Initial value 0 (counter, not version).
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage3a_theory_version":
                new["identification_plan_revision_round"] = 0
        data = new
    if "headline_replication_round" not in data:
        # Insert immediately after identification_plan_revision_round. Counter for the
        # Stage 3a step 6.5 headline-replicator substantive-disagreement re-fire loop
        # (hard cap 3). Resets to 0 on PASS, on no_headline_tags / source_unreachable /
        # trivially_equivalent_path routings, on step-7.5 substantive data FAIL re-execution,
        # on any step-7 empirics-auditor re-fire that materially changes code/empirical.py
        # or headline content, on Stage 3a re-fire entry per "Re-fire on theory revision",
        # and on puzzle-triage FIX-EMPIRICS re-entry. Anchored on identification_plan_revision_round
        # (Stage 3a step 3) so the key order reflects pipeline-execution order:
        # identification_plan_revision_round -> headline_replication_round -> data_integrity_round
        # -> method_check_round.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "identification_plan_revision_round":
                new["headline_replication_round"] = 0
        data = new
    if "data_integrity_round" not in data:
        # Insert immediately after headline_replication_round. Counter for the
        # Stage 3a step 7.5 data-integrity + data-selection auditor REVISE loop (hard cap 3).
        # Anchor on headline_replication_round (added immediately above) so the documented
        # key order is preserved on fresh deploys where both keys are added in this pass.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "headline_replication_round":
                new["data_integrity_round"] = 0
        data = new
    if "method_check_round" not in data:
        # Insert immediately after data_integrity_round. Counter for the Stage 3a step 7.5
        # method-checker REVISE loop (hard cap 3) — tracked separately from data audits because
        # the method REVISE fix loop edits code/imports rather than re-running the cache.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "data_integrity_round":
                new["method_check_round"] = 0
        data = new
    if "claim_grounding_round" not in data:
        # Insert immediately after method_check_round. Counter for the Stage 5 step 5a
        # claim-grounding pipeline (enumerator -> grounder -> verifier) GROUNDER-ERROR
        # re-fire loop (hard cap 3). PAPER-SIDE-ERROR re-fires reset this to 0.
        # Anchor on method_check_round (not data_integrity_round) so the documented
        # key order data_integrity_round -> method_check_round -> claim_grounding_round
        # is preserved on fresh deploys where all three keys are added in this pass.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "method_check_round":
                new["claim_grounding_round"] = 0
        data = new
    if "paper_writer_pse_round" not in data:
        # Insert immediately after claim_grounding_round. Counter for consecutive
        # PAPER-SIDE-ERROR re-fires of paper-writer at Stage 5 step 5a; resets to 0
        # on claim-verifier PASS or on a PAPER-SIDE-ERROR cycle whose failure-claim-ID
        # set overlaps <50% with the prior cycle (substantively different failures).
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "claim_grounding_round":
                new["paper_writer_pse_round"] = 0
        data = new
    if "paper_writer_pse_claim_ids" not in data:
        # Insert immediately after paper_writer_pse_round. Stores the claim_id set from
        # the most recent PAPER-SIDE-ERROR claim_verification.md so the orchestrator can
        # compute >50% overlap against the next PSE cycle without re-reading prior reports.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "paper_writer_pse_round":
                new["paper_writer_pse_claim_ids"] = []
        data = new
    if "claim_format_reexport_round" not in data:
        # Insert immediately after paper_writer_pse_claim_ids. Counter for consecutive
        # VERIFIER-LIMITATION (format-unsupported) re-fires at Stage 5 step 5a: a claim
        # whose value exists only in a non-parseable file (CSV/parquet/pickle) routes to
        # the empiricist for a JSON re-export, NOT to paper-writer to drop. Hard cap 2;
        # independent of claim_grounding_round and the PSE counters. Resets to 0 on
        # claim-verifier PASS.
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "paper_writer_pse_claim_ids":
                new["claim_format_reexport_round"] = 0
        data = new
    with open(state_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
PYEOF

            # Empirical extension developing agents — from metadata.
            # Variant-aware via $AGENT_DIR (finance metadata adds identification-designer;
            # macro currently has empiricist only). The metadata is the source of truth.
            mapfile -t _empirical_developing_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_developing_agents[@]}" -eq 0 ]; then
                echo "Error: empirical developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_faithful_into_agents "${_empirical_developing_agents[@]}"

            mapfile -t _empirical_bash_agents < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_bash_agents[@]}" -eq 0 ]; then
                echo "Error: empirical Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_bash_background_into_agents "${_empirical_bash_agents[@]}"

            # Core-bypass guard: empirical agents that read a binding data source
            # (WRDS/EDGAR/FRED) or verify the pipeline's empirics against it. The
            # injector's file-existence guards make pruned/absent agents a no-op
            # (e.g. macro has no identification-auditor; report mode prunes these).
            inject_core_bypass_into_agents \
                empiricist empirics-auditor headline-replicator \
                data-integrity-auditor data-selection-auditor method-checker \
                claim-grounder claim-verifier identification-auditor

            # Report mode: --ext empirical is install-only (WRDS/FRED/Census/SEC
            # skills + utility scripts). All audit agents that ship with the
            # empirical extension are pruned — they were designed against the
            # pipeline's own empiricist output (output/stage3a/empirical_analysis.md,
            # code/empirical.py) and would need substantial rewrites to operate on
            # an external submission. The base referees handle empirical refereeing
            # at the editorial level. Full code-level empirical auditing of
            # external submissions is a v2 feature. The generative empiricist /
            # identification-designer are pruned for the usual reason.
            prune_report_mode_agents \
                empiricist identification-designer \
                empirics-auditor identification-auditor \
                data-integrity-auditor data-selection-auditor method-checker \
                headline-replicator \
                claim-enumerator claim-grounder claim-verifier
            # Empirical extension also creates output/stage3a/ unconditionally
            # and copies stage_3a_empirical.md into docs/. Both are pipeline-
            # workflow artifacts irrelevant to report mode — remove them.
            if [ "$MODE" = "report" ]; then
                rmdir "$P/output/stage3a" 2>/dev/null || true
                rm -f "$P/docs/stage_3a_empirical.md"
            fi
            echo "  ✓ Empirical extension applied (skills + agents)"
            ;;
        *)
            echo "Unknown extension: $ext"
            echo "Available extensions: empirical, theory_llm"
            exit 1
            ;;
    esac
done

# Clean up leftover {{EXTENSION_STAGES}} placeholder from runtime docs
for doc in "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT"; do
    python3 -c "
import sys; d=sys.argv[1]
content=open(d).read()
open(d,'w').write(content.replace('{{EXTENSION_STAGES}}', '').rstrip()+'\n')
" "$doc"
done

# Extension-disabled cleanup: strip any unfilled {{EMPIRICAL_*}} / {{THEORY_LLM_*}}
# placeholders and the <!-- EMPIRICAL_FERTILITY_ADDENDUM --> marker. When the
# corresponding extension is on, the inject blocks above already substituted real
# content; this is a no-op for those placeholders. When an extension is off, this
# leaves the docs and scorer body identical to the pre-edit baseline (lines
# containing only the placeholder are removed whole).
python3 - \
    "$P/docs/stage_2.md" \
    "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
    "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" <<'PYEOF'
import os, re, sys
# Match a whole line that is just {{EMPIRICAL_*}} or {{THEORY_LLM_*}} (with optional
# surrounding whitespace), including its trailing newline. Inline (mid-line)
# occurrences are not used.
LINE_PAT = re.compile(r"^[ \t]*\{\{(EMPIRICAL|THEORY_LLM)_[A-Z0-9_]+\}\}[ \t]*\n", re.MULTILINE)
MARKER_PAT = re.compile(r"^[ \t]*<!-- EMPIRICAL_FERTILITY_ADDENDUM -->[ \t]*\n", re.MULTILINE)
for p in sys.argv[1:]:
    if not os.path.exists(p):
        continue
    with open(p) as f: t = f.read()
    new = LINE_PAT.sub("", t)
    new = MARKER_PAT.sub("", new)
    if new != t:
        with open(p, "w") as f: f.write(new)
PYEOF

# Resolve THEORY_ONLY_GUARD markers in branch-manager across the three runtimes.
# Empirical mode: strip the whole guarded block (body + markers).
# Theory-only mode: strip just the marker lines, keep the rule text.
EMPIRICAL_ENABLED=0
for ext in "${EXTENSIONS[@]}"; do
    [ "$ext" = "empirical" ] && EMPIRICAL_ENABLED=1
done
python3 - "$EMPIRICAL_ENABLED" "$AGENTS_OUT/branch-manager.md" "$CODEX_AGENTS_OUT/branch-manager.toml" "$GEMINI_AGENTS_OUT/branch-manager.md" <<'PYEOF'
import re, sys
emp = sys.argv[1] == "1"
if emp:
    pat = re.compile(r"<!-- THEORY_ONLY_GUARD_START -->\n.*?<!-- THEORY_ONLY_GUARD_END -->\n\n?", re.DOTALL)
    repl = ""
else:
    pat = re.compile(r"<!-- THEORY_ONLY_GUARD_(?:START|END) -->\n")
    repl = ""
for p in sys.argv[2:]:
    try:
        with open(p) as f: t = f.read()
    except OSError:
        continue
    new = pat.sub(repl, t)
    if new != t:
        try:
            with open(p, "w") as f: f.write(new)
        except OSError as e:
            print(f"  warn: could not resolve guard in {p}: {e}", file=sys.stderr)
PYEOF

# Resolve EMPIRICAL_FIRST / THEORY_FIRST guard markers in stage docs.
# Pattern mirrors THEORY_ONLY_GUARD: pairs of HTML-comment markers wrap
# alternative content for theory-first vs. empirical-first orchestration.
# When --mode empirical-first is set:
#   - EMPIRICAL_FIRST blocks: keep content, strip just the marker lines
#   - THEORY_FIRST blocks: strip the whole block (markers + content)
# When --mode is unset:
#   - EMPIRICAL_FIRST blocks: strip the whole block
#   - THEORY_FIRST blocks: keep content, strip just the marker lines
# Applied to docs/ only (agent-side mode-conditional content goes via vocab
# overlays in phase 4, not markers).
EMPIRICAL_FIRST_ON=0
[ "$MODE" = "empirical-first" ] && EMPIRICAL_FIRST_ON=1
# EXT_EMPIRICAL_ON gates content that should activate whenever the empirical
# extension is present, regardless of mode. Note: --mode empirical-first
# auto-adds --ext empirical (line ~124), so EMPIRICAL_FIRST_ON=1 implies
# EXT_EMPIRICAL_ON=1; the converse is not true (theory-first --ext empirical).
EXT_EMPIRICAL_ON=0
[[ " ${EXTENSIONS[*]} " =~ " empirical " ]] && EXT_EMPIRICAL_ON=1
# Resolver runs over stage docs, the three runtime docs (CLAUDE.md /
# AGENTS.md / GEMINI.md, assembled from templates/shared/core.md), AND the
# three runtimes' assembled agent files. The agent-file coverage lets shared
# agent bodies (e.g., paper-writer.md) carry inline EMPIRICAL_FIRST /
# THEORY_FIRST / EXT_EMPIRICAL markers — the alternative is a parallel body
# in templates/agent_bodies/shared_modes/{mode}/, which is more duplication
# when the body's mode-specific delta is small. Vocab substitution runs at
# assembly time (before this resolver fires), so {{KEY}} placeholders are
# already resolved when the resolver sees the agent files.
python3 - "$EMPIRICAL_FIRST_ON" "$EXT_EMPIRICAL_ON" "$P/docs/"*.md "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
    "$AGENTS_OUT"/*.md "$CODEX_AGENTS_OUT"/*.toml "$GEMINI_AGENTS_OUT"/*.md <<'PYEOF'
import os, re, sys
ef = sys.argv[1] == "1"
xe = sys.argv[2] == "1"
patterns = []  # list of (regex, replacement) applied in order
# Trailing \n after END markers is optional so a marker at EOF (no final
# newline) still matches; otherwise the literal HTML comment leaks into the
# deployed file.
if ef:
    patterns.append((re.compile(r"<!-- THEORY_FIRST_START -->\n.*?<!-- THEORY_FIRST_END -->\n{0,2}", re.DOTALL), ""))
    patterns.append((re.compile(r"<!-- EMPIRICAL_FIRST_(?:START|END) -->\n?"), ""))
else:
    patterns.append((re.compile(r"<!-- EMPIRICAL_FIRST_START -->\n.*?<!-- EMPIRICAL_FIRST_END -->\n{0,2}", re.DOTALL), ""))
    patterns.append((re.compile(r"<!-- THEORY_FIRST_(?:START|END) -->\n?"), ""))
if xe:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_(?:START|END) -->\n?"), ""))
else:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_START -->\n.*?<!-- EXT_EMPIRICAL_END -->\n{0,2}", re.DOTALL), ""))
for p in sys.argv[3:]:
    if not os.path.exists(p):
        continue
    with open(p) as f: t = f.read()
    new = t
    for rx, repl in patterns:
        new = rx.sub(repl, new)
    if new != t:
        with open(p, "w") as f: f.write(new)
PYEOF

# Re-run seed-override substitution now that extension docs have been copied into $P/docs/.
# Extensions may ship stage docs (e.g., stage_3a_empirical.md) containing {{SEED_OVERRIDE_*}} placeholders.
apply_seed_overrides

echo "  ✓ Codex custom agents assembled"

# ── Emit deployment manifest ──
# Records what setup.sh produced as "infrastructure" — paths that update.sh
# may overwrite when refreshing a deployed project against a newer template.
# Anything not in this manifest is preserved on update (paper content,
# output/, process_log/, .env values, references.bib, git history, paper/
# arpipeline.sty fingerprint, paper/main.tex, paper/internet_appendix.tex).
EXT_JSON=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "${EXTENSIONS[@]}")
# Capitalised for Python literal substitution into the heredoc below.
SEEDED_BOOL=$([ "$SEEDED" = "1" ] && echo True || echo False)
MANUAL_BOOL=$([ "$MANUAL" = "1" ] && echo True || echo False)
LIGHT_BOOL=$([ "$LIGHT" = "1" ] && echo True || echo False)
HALT_ON_CORE_BYPASS_BOOL=$([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo True || echo False)

python3 <<PYEMIT
import json
from pathlib import Path

project = Path("$P")
manifest_path = project / ".deploy_manifest.json"

# Allow-list of paths setup.sh produces. update.sh nukes-and-replaces each
# present entry; absent entries are skipped. Only well-known infrastructure
# paths belong here. Adding a new agent dir / script dir to setup.sh? Add
# it here too.
candidate_dirs = [
    ".claude/agents",
    ".claude/skills",
    ".codex/agents",
    ".agents/skills",
    ".gemini/agents",
    "docs",
    "code/utils/codex_math",
    "code/utils/bib_verify",
    "code/utils/openalex",
]
candidate_files = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "docs/start_session_claude.md",
    "docs/start_session_codex.md",
    "docs/start_session_gemini.md",
    ".claude/settings.json",
    ".gemini/settings.json",
    ".gitignore",
    "dashboard.html",
]

# Extension-installed files. The empirical extension drops *.py / *.sh
# directly into code/utils/ (flat, alongside the codex_math/bib_verify/
# openalex subdirs that core setup creates). The theory_llm extension
# drops llm_client.py at the project root. Both are setup-managed
# infrastructure that update.sh must refresh.
extensions = $EXT_JSON
if "empirical" in extensions:
    utils = project / "code" / "utils"
    if utils.is_dir():
        for f in sorted(utils.iterdir()):
            if f.is_file() and f.suffix in {".py", ".sh"}:
                candidate_files.append(str(f.relative_to(project)))
if "theory_llm" in extensions:
    if (project / "llm_client.py").is_file():
        candidate_files.append("llm_client.py")

manifest = {
    "manifest_version": 1,
    "template_version": "$ARP_VERSION",
    "deploy_date": "$ARP_DATE",
    "deploy_fingerprint": "$ARP_UUID",
    "variant": "$VARIANT",
    "mode": "$MODE",
    "extensions": extensions,
    "flags": {
        "seeded": $SEEDED_BOOL,
        "manual": $MANUAL_BOOL,
        "light": $LIGHT_BOOL,
        "halt_on_core_bypass": $HALT_ON_CORE_BYPASS_BOOL,
    },
    "infrastructure": {
        "dirs_replace": [d for d in candidate_dirs if (project / d).is_dir()],
        "files_replace": [f for f in candidate_files if (project / f).is_file()],
        "files_env_merge": [".env"] if (project / ".env").is_file() else [],
    },
}

manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
PYEMIT
echo "  ✓ deployment manifest written: .deploy_manifest.json"

# ── Local mode: summary and exit ──
if [ "$LOCAL" = "1" ]; then
    echo ""
    echo "=== Assembled CLAUDE.md ==="
    echo "Lines: $(wc -l < "$CLAUDE_MD_OUT")"
    REMAINING=$(grep -c '{{' "$CLAUDE_MD_OUT" 2>/dev/null || true)
    REMAINING="${REMAINING:-0}"
    echo "Placeholders remaining: $REMAINING"
    echo ""
    echo "=== Assembled AGENTS.md ==="
    echo "Lines: $(wc -l < "$AGENTS_MD_OUT")"
    AGENTS_REMAINING=$(grep -c '{{' "$AGENTS_MD_OUT" 2>/dev/null || true)
    AGENTS_REMAINING="${AGENTS_REMAINING:-0}"
    echo "Placeholders remaining: $AGENTS_REMAINING"
    echo ""
    echo "=== Assembled GEMINI.md ==="
    echo "Lines: $(wc -l < "$GEMINI_MD_OUT")"
    GEMINI_REMAINING=$(grep -c '{{' "$GEMINI_MD_OUT" 2>/dev/null || true)
    GEMINI_REMAINING="${GEMINI_REMAINING:-0}"
    echo "Placeholders remaining: $GEMINI_REMAINING"
    echo ""
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    echo ""
    echo "=== Codex Agents ($CODEX_AGENTS_REL/) ==="
    ls -1 "$CODEX_AGENTS_OUT/"
    echo ""
    echo "=== Gemini Agents ($GEMINI_AGENTS_REL/) ==="
    ls -1 "$GEMINI_AGENTS_OUT/"
    if [ -d "$OUT_DIR/$CLAUDE_SKILLS_REL" ]; then
        echo ""
        echo "=== Skills ($CLAUDE_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CLAUDE_SKILLS_REL/"
    fi
    if [ -d "$OUT_DIR/$CODEX_SKILLS_REL" ]; then
        echo ""
        echo "=== Codex Skills ($CODEX_SKILLS_REL/) ==="
        ls -1 "$OUT_DIR/$CODEX_SKILLS_REL/"
    fi
    echo ""
    echo "=== First 10 lines ==="
    head -10 "$CLAUDE_MD_OUT"
    echo ""
    echo "=== Domain section ==="
    grep -A 5 "^## Domain:" "$CLAUDE_MD_OUT" | head -8
    echo ""

    if [ "$REMAINING" -gt 0 ]; then
        echo "WARNING: $REMAINING unresolved placeholders:"
        grep '{{' "$CLAUDE_MD_OUT"
        exit 1
    elif [ "$AGENTS_REMAINING" -gt 0 ]; then
        echo "WARNING: $AGENTS_REMAINING unresolved placeholders:"
        grep '{{' "$AGENTS_MD_OUT"
        exit 1
    elif [ "$GEMINI_REMAINING" -gt 0 ]; then
        echo "WARNING: $GEMINI_REMAINING unresolved placeholders:"
        grep '{{' "$GEMINI_MD_OUT"
        exit 1
    else
        echo "✓ All placeholders resolved"
    fi
    echo ""
    echo "Output at: $OUT_DIR/"
    exit 0
fi

# ── Production mode: clean up and commit ──
echo "Cleaning up template files..."

# Replace template .gitignore with project-specific one (before deleting templates/)
cp templates/gitignore_project .gitignore

rm -rf templates/
rm -rf extensions/
rm -rf meta_paper/
rm -rf test_scripts/
rm -rf scripts/
rm -rf codex_inspect/
rm -rf test_output/
rm -f setup.sh
rm -f README.md
rm -f CLAUDE_REFACTOR_PLAN.md
rm -f requirements.system
rm -f texput.log
if [ "$MANUAL" = "1" ] || [ "$MODE" = "report" ]; then
    rm -f dashboard.html
fi
echo "  ✓ Template files removed"

git add -A
if [ "$MANUAL" = "1" ]; then
    git commit -m "setup: initialized ${VARIANT} variant toolkit (manual mode)" -q
elif [ "$MODE" = "report" ]; then
    git commit -m "setup: initialized ${VARIANT} variant referee-report deployment" -q
else
    git commit -m "setup: initialized ${VARIANT} variant pipeline" -q
fi

# ── Optional: auto-publish to a GitHub org if the current user is a member ──
# Set PUBLISH_ORG=<org> (or leave the default) to opt in. Silently skipped for
# non-members so other users of this template just get a local repo.
#
# Opt-out paths:
#   - PUBLISH_ORG= ./setup.sh ...      (single -, so an explicit empty string
#                                       is honored — :- would substitute the
#                                       default and re-enable publishing)
#   - --mode report runs auto-disable below (refereeing external submissions
#     involves someone else's unpublished work; default-publish is unsafe).
PUBLISH_ORG="${PUBLISH_ORG-automated-papers-produced}"
PUBLISH_VISIBILITY="${PUBLISH_VISIBILITY-private}"
# Report mode handles external (often confidential) submissions; never auto-
# publish those. The user can still push manually if they want.
if [ "$MODE" = "report" ] && [ -n "$PUBLISH_ORG" ]; then
    echo "  (skipping publish — --mode report deploys are kept local by default)"
    PUBLISH_ORG=""
fi
# GitHub repo name = <project>-<first 8 chars of ARP_UUID>. The suffix is the
# same deployment fingerprint baked into paper/arpipeline.sty (and every PDF
# the pipeline produces), so the repo URL is a 1:1 lookup for the deployment.
# Always-suffixing eliminates name collisions between unrelated projects that
# happen to share a project name (e.g., two charlie-2 folders on different hosts).
PUBLISH_SUFFIX="${ARP_UUID:0:8}"
# PROJECT_NAME may be an absolute or relative path; GitHub repo names can't
# contain slashes, so use just the basename for the repo name.
PUBLISH_NAME="$(basename "$PROJECT_NAME")-${PUBLISH_SUFFIX}"
if [ -n "$PUBLISH_ORG" ] && command -v gh >/dev/null 2>&1 \
   && gh auth status >/dev/null 2>&1; then
    gh_user=$(gh api user --jq .login 2>/dev/null || true)
    if [ -n "$gh_user" ] \
       && gh api "orgs/$PUBLISH_ORG/memberships/$gh_user" >/dev/null 2>&1; then
        echo "Publishing to $PUBLISH_ORG/$PUBLISH_NAME ($PUBLISH_VISIBILITY)..."
        if gh repo create "$PUBLISH_ORG/$PUBLISH_NAME" \
               "--$PUBLISH_VISIBILITY" \
               --source=. --remote=origin --push >/dev/null 2>&1; then
            echo "  ✓ Pushed to $PUBLISH_ORG/$PUBLISH_NAME"
            echo "    (deployment fingerprint: $ARP_UUID)"
        else
            echo "  ⚠ gh repo create failed. Repo remains local."
            echo "    (would have published to $PUBLISH_ORG/$PUBLISH_NAME)"
        fi
    else
        echo "  (skipping $PUBLISH_ORG push — not a member)"
    fi
fi

echo ""
echo "============================================"
if [ "$MANUAL" = "1" ]; then
    echo "  Setup complete: $PROJECT_NAME ($VARIANT, manual mode)"
elif [ "$MODE" = "report" ]; then
    echo "  Setup complete: $PROJECT_NAME ($VARIANT, --mode report)"
else
    echo "  Setup complete: $PROJECT_NAME ($VARIANT)"
fi
echo "============================================"
echo ""
echo "  cd $PROJECT_NAME"
echo ""
echo "Claude:"
echo "  claude --dangerously-skip-permissions"
echo ""
echo "Codex:"
echo "  codex --sandbox danger-full-access --ask-for-approval never"
echo ""
echo "Gemini:"
echo "  gemini --yolo"
echo ""
if [ "$MANUAL" = "1" ]; then
    echo "Manual mode — read the runtime doc for the agent and skill catalog, then drive."
elif [ "$MODE" = "report" ]; then
    echo "Drop the submission to be refereed in submission/ (PDF or LaTeX source bundle), then say: \"run\""
    echo "  - core_report.md fans out the audit agents in parallel"
    echo "  - report-synthesizer aggregates them into report/referee_report.md"
    echo "  - one-shot; for a revised submission re-run setup.sh on a fresh folder"
else
    echo "Then say: \"Run the pipeline.\""
fi
echo ""
echo "Variant: $VARIANT"
echo "Extensions: ${EXTENSIONS[*]:-none}"
if [ "$LIGHT" = "1" ]; then
    echo "Mode: light (all subagents use sonnet)"
fi
if [ "$FAITHFUL" = "1" ]; then
    echo "Mode: faithful (the seed is a contract; the pipeline implements it as written)"
    echo "Drop your idea files in output/seed/ before launching"
    echo "Pipeline will extract a mechanism contract first, then triage entry-stage"
elif [ "$SEEDED" = "1" ]; then
    echo "Seeded: drop your idea files in output/seed/ before launching"
    echo "Pipeline will triage seed maturity and enter at the appropriate stage"
fi
echo "Sandbox is pre-configured in $CLAUDE_SETTINGS_REL"
echo "(Bash restricted to project folder, web access works freely)"
