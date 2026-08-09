#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro|llm_cognition] [--mode empirical-first|measurement-first|report]
#                  [--ext empirical|theory_llm] [--seed|--faithful|--manual] [--light]
#                  [--no-model-probe] [--publish|--no-publish] [--local]
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
# --light   Use the cheapest capability tier for the whole run (cheaper/faster).
#           Applies to every runtime through its own tier table: claude `sonnet`,
#           codex `gpt-5.6-luna`, gemini `gemini-3-flash-preview`. Grok and
#           OpenCode are no-ops because each has one configured model. Subagents are pinned at assembly time
#           and their per-agent reasoning effort is dropped; the ORCHESTRATOR is
#           pinned to the same tier by launch.sh, which reads it back from the
#           assembled agents rather than carrying its own copy of the table.
# --no-model-probe  Skip the live claude-CLI availability probe. Agent models are
#           still remapped off the built-in known-unavailable list (fable/mythos
#           → opus), but newly-suspended models won't be auto-detected. Use in CI
#           or offline setups where launching `claude` at setup time isn't wanted.
# --publish Create and push a GitHub repository after setup. Publishing is opt-in;
#           new deployments stay local unless this flag is present. The target
#           defaults to automated-papers-produced and can be changed with
#           PUBLISH_ORG=<org>; PUBLISH_VISIBILITY defaults to private.
# --no-publish  Explicitly keep the deployment local (the default). Useful in
#           scripts that want the safety choice visible at the call site.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Resolve configuration ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SETUP_CONFIG_MODULE="$SCRIPT_DIR/deploy_assets/scripts/setup/resolve_config.sh"
if [ ! -f "$SETUP_CONFIG_MODULE" ]; then
    echo "Error: setup configuration module not found: $SETUP_CONFIG_MODULE" >&2
    echo "  Run setup.sh from a complete zeropaper checkout." >&2
    exit 1
fi
# shellcheck source=deploy_assets/scripts/setup/resolve_config.sh
source "$SETUP_CONFIG_MODULE"
resolve_setup_config "$@"

# Argument parsing, validation, legacy expansion, implied/deduplicated
# extensions, and variant/mode descriptors are resolved by the configuration
# module above.  setup.sh now consumes that interface and coordinates assembly.

# ── Tier vocab for agent bodies ──
# The tier ladder is a setup configuration variable (resolved by
# resolve_config.sh) that the runtime-doc assembler consumes directly, but agent BODIES go
# through the vocab-substitution path. Bodies that must name the variant's tier
# slugs (editor.md's ladder/allowed-values lines) reference {{TIER_LIST_INLINE}}
# / {{TIER_LADDER_PROSE}}, resolved from this generated overlay so the ladder
# has exactly one source of truth per deploy. Passed to every base assembler
# (shared + variant, all five runtimes). Build-time only (mktemp, never
# deployed): no manifest entry. Best-effort cleanup — a leaked file holds only
# the public tier strings.
#
# No `.json` suffix on the template: BSD/macOS mktemp randomizes only a
# *trailing* run of X's, so `tier_vocab.XXXXXX.json` yields that name
# **literally** — a fixed path, which defeats mktemp entirely. Sequential
# deploys still worked (the cleanup below removes it), but any run that died
# between here and cleanup left the file behind and then bricked every
# subsequent deploy on the host: `set -e` aborts on this line with a bare
# "mkstemp failed ... File exists" that names neither setup.sh nor the tier
# vocab. Concurrent deploys collided for the same reason. The extension was
# decorative — the path is passed to the assemblers explicitly via --vocab.
# Single EXIT trap for every temp resource this script creates (tier vocab
# file here; manual-mode catalog dir and the production source clone later).
# One trap function, not per-resource `trap` lines — a later `trap ... EXIT`
# replaces the earlier one and silently leaks the first resource. Also covers
# error exits, which the old explicit `rm -f "$TIER_VOCAB_FILE"` calls missed.
# Clear same-named inherited environment values before installing the trap: the
# cleanup function must only ever remove resources created by this invocation.
SRC_TMP=""
CATALOG_TMPDIR=""
TIER_VOCAB_FILE=""
OWNERSHIP_TMPDIR=""
_setup_cleanup() {
    # Largest resource first, and `|| true` per line: under `set -e` a failing
    # rm would abort the trap function mid-way and silently leak whatever was
    # scheduled after it.
    [ -n "${SRC_TMP:-}" ] && rm -rf "$SRC_TMP" 2>/dev/null || true
    [ -n "${OWNERSHIP_TMPDIR:-}" ] && rm -rf "$OWNERSHIP_TMPDIR" 2>/dev/null || true
    [ -n "${CATALOG_TMPDIR:-}" ] && rm -rf "$CATALOG_TMPDIR" 2>/dev/null || true
    [ -n "${TIER_VOCAB_FILE:-}" ] && rm -f "$TIER_VOCAB_FILE" 2>/dev/null || true
    return 0
}
trap _setup_cleanup EXIT
TIER_VOCAB_FILE="$(mktemp "${TMPDIR:-/tmp}/tier_vocab.XXXXXX")"
TIER_LIST_INLINE="$TIER_LIST_INLINE" TIER_LADDER_PROSE="$TIER_LADDER_PROSE" python3 - "$TIER_VOCAB_FILE" <<'PYEOF'
import json, os, sys
with open(sys.argv[1], "w") as f:
    json.dump({
        "TIER_LIST_INLINE": os.environ["TIER_LIST_INLINE"],
        "TIER_LADDER_PROSE": os.environ["TIER_LADDER_PROSE"],
    }, f)
PYEOF

# ── Resolve paths ──
CLAUDE_DIR_REL=".claude"
CLAUDE_AGENTS_REL="$CLAUDE_DIR_REL/agents"
CLAUDE_SKILLS_REL="$CLAUDE_DIR_REL/skills"
CLAUDE_SETTINGS_REL="$CLAUDE_DIR_REL/settings.json"
# Source of the DEPLOYED Claude settings (the sandbox profile a research project
# runs under). Deliberately NOT this repo's own .claude/settings.json: that file
# configures the template-development session, and a single file cannot be both
# — the template repo wants a permissive dev posture while a deployed project
# wants the sandbox on. Build-time only (lives under templates/, removed in the
# cleanup block), so no deployment-manifest entry; the *destination*
# .claude/settings.json is manifested, so update.sh refreshes it.
CLAUDE_SETTINGS_SRC_REL="templates/runtime/claude/settings.json"
CODEX_DIR_REL=".agents"
CODEX_SUBAGENT_DIR_REL=".codex"
CODEX_AGENTS_REL="$CODEX_SUBAGENT_DIR_REL/agents"
CODEX_SKILLS_REL="$CODEX_DIR_REL/skills"
GEMINI_DIR_REL=".gemini"
GEMINI_AGENTS_REL="$GEMINI_DIR_REL/agents"
GEMINI_SETTINGS_REL="$GEMINI_DIR_REL/settings.json"
# Same split as CLAUDE_SETTINGS_SRC_REL above: deployed Gemini settings ship from
# templates/, not from a dual-role file at this repo's root.
GEMINI_SETTINGS_SRC_REL="templates/runtime/gemini/settings.json"
# Grok Build (xAI `grok` CLI). Reads project instructions from the shared root
# AGENTS.md (same file as Codex — see the labeled-dispatch block in
# templates/runtime/codex/session.md), and its subagents from .grok/agents/*.md.
GROK_DIR_REL=".grok"
GROK_AGENTS_REL="$GROK_DIR_REL/agents"
# Grok's OS-kernel sandbox profile (Seatbelt on macOS / Landlock on Linux),
# generated by scripts/setup/base_agents.sh with the deploying user's $HOME baked in (grok's
# sandbox.toml does not expand ~/$HOME). Launched via
# `grok --sandbox pipeline --always-approve --leader-socket "$(pwd)/.grok/leader.sock"`
# (the per-project leader socket keeps concurrent grok projects from cancelling
# each other's turns — see the launch-line comment below).
GROK_SANDBOX_REL="$GROK_DIR_REL/sandbox.toml"
OPENCODE_DIR_REL=".opencode"
OPENCODE_AGENTS_REL="$OPENCODE_DIR_REL/agents"
OPENCODE_CONFIG_REL="opencode.json"
OPENCODE_CONFIG_SRC_REL="templates/runtime/opencode/opencode.json"
OPENCODE_SANDBOX_REL="$OPENCODE_DIR_REL/sandbox.json"
OPENCODE_SANDBOX_SRC_REL="templates/runtime/opencode/sandbox.json"


MODEL_OVERRIDE_ARGS=()
if [ "$LIGHT" = "1" ]; then
    MODEL_OVERRIDE_ARGS=(--model-override sonnet)
fi

# Mode-overlay paths are resolved after the LOCAL/production branch sets
# TEMPLATE_ROOT, inside scripts/setup/runtime_documents.sh. They used to be
# resolved here against $SCRIPT_DIR, which in production silently mixed
# local-checkout overlays with clone-sourced everything else.

if [ "$LOCAL" = "1" ]; then
    # Local test mode — no clone, no git, no prereq checks
    PROJECT_NAME="${PROJECT_NAME:-test_output/$VARIANT}"
    # SRC_ROOT = the repo checkout (VERSION lives here); TEMPLATE_ROOT = the
    # build-input tree (templates/, scripts/, extensions/) under deploy_assets/.
    SRC_ROOT="$SCRIPT_DIR"
    TEMPLATE_ROOT="$SRC_ROOT/deploy_assets"

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
    mkdir -p "$OUT_DIR"
    # (Agent output dirs, runtime settings dirs, and the opencode config files
    # are all created by shared blocks below that serve both --local and
    # production — this branch only stages the verbatim-shipped root files.)
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
    # `set -e` aborts the whole script (skipping any requested publish step) if commit
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

    # ── Fetch build inputs into a throwaway source tree; the project directory
    # only ever receives build OUTPUTS (issue #232). The clone is pure
    # transport: it lives in tmp, is read through TEMPLATE_ROOT/SRC_ROOT, and
    # is deleted wholesale by the EXIT trap. Nothing dev-only can leak into the
    # project because nothing is ever assembled inside the clone — there is no
    # strip/denylist step anymore, and a forgotten copy shows up as a MISSING
    # file in the deployment (fail-closed), not as dev content shipping.
    #
    # Clone source is overridable via ZEROPAPER_REPO (a local path or alternate
    # URL) for offline/local testing of un-pushed template changes; defaults to
    # the public repo. A local-path clone only sees committed state.
    #
    # The sparse checkout is a transport optimization, not the safety boundary:
    # cone mode materializes deploy_assets/ plus ALL root-level files (of
    # which only VERSION and LICENSE are read) and skips every other
    # top-level dir. If the git/transport combo
    # can't do partial clones, fall back to a full clone — same build, more
    # bytes. The clone keeps its .git on purpose: the version stamp reads
    # `git rev-parse` from it (the old flow ran `rm -rf .git` before stamping,
    # which is why every production manifest said "+unknown").
    SRC_TMP="$(mktemp -d "${TMPDIR:-/tmp}/zeropaper-src.XXXXXX")"
    _zp_repo="${ZEROPAPER_REPO:-https://github.com/alejandroll10/zeropaper.git}"
    echo "Fetching template into $SRC_TMP/src..."
    if ! { git clone -q --filter=blob:none --sparse "$_zp_repo" "$SRC_TMP/src" 2>/dev/null \
           && git -C "$SRC_TMP/src" sparse-checkout set deploy_assets 2>/dev/null; }; then
        echo "  (sparse clone unavailable — falling back to a full clone)"
        rm -rf "$SRC_TMP/src"
        git clone -q "$_zp_repo" "$SRC_TMP/src"
    fi
    if [ ! -d "$SRC_TMP/src/deploy_assets" ]; then
        echo "Error: clone has no deploy_assets/ — template source too old for this setup.sh?" >&2
        exit 1
    fi

    echo "Creating project $PROJECT_NAME..."
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME"

    # cwd is the fresh, empty project. SRC_ROOT = clone root (VERSION lives
    # there); TEMPLATE_ROOT = the build-input tree under deploy_assets/.
    SRC_ROOT="$SRC_TMP/src"
    TEMPLATE_ROOT="$SRC_ROOT/deploy_assets"
    OUT_DIR="."

fi

# ── Initialize infrastructure / bootstrap ownership boundary ──
P="$OUT_DIR"
FINALIZATION_MODULE="$TEMPLATE_ROOT/scripts/setup/finalization.sh"
if [ ! -f "$FINALIZATION_MODULE" ]; then
    echo "Error: setup finalization module not found: $FINALIZATION_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$FINALIZATION_MODULE"
setup_initialize_project_git

OWNERSHIP_MODULE="$TEMPLATE_ROOT/scripts/setup/ownership.sh"
if [ ! -f "$OWNERSHIP_MODULE" ]; then
    echo "Error: setup ownership module not found: $OWNERSHIP_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$OWNERSHIP_MODULE"
setup_ownership_init

# Verbatim template-owned root infrastructure. Registration is part of the
# install call, so manifest membership cannot drift from creation.
infrastructure_copy_file 220 "$TEMPLATE_ROOT/templates/gitignore_project" ".gitignore"
infrastructure_copy_file 130 "$TEMPLATE_ROOT/launch.sh" "launch.sh"
if [ "$MANUAL" = "0" ] && [ "$MODE" != "report" ]; then
    infrastructure_copy_file 230 "$TEMPLATE_ROOT/dashboard.html" "dashboard.html"
    if [ "$LOCAL" = "1" ]; then
        DASHBOARD_SUBTITLE="Autonomous $(python3 -c "import sys; print(sys.argv[1].title())" "$PAPER_TYPE") Generator"
        sed -i.bak "s|Autonomous Finance Theory Paper Generator|$DASHBOARD_SUBTITLE|" "$P/dashboard.html" && rm "$P/dashboard.html.bak"
    fi
fi

# LICENSE is bootstrap content: setup creates it for publishability, but
# update.sh has never owned or refreshed it.
if [ "$LOCAL" = "0" ]; then
    bootstrap_copy_file "$SRC_ROOT/LICENSE" "LICENSE"
fi

# ── Runtime-document assembly ──
# Source from TEMPLATE_ROOT so production uses the fetched build inputs and
# --local uses this checkout. The module also resolves the mode overlays
# consumed by the agent assemblers below.
CLAUDE_MD_OUT="$OUT_DIR/CLAUDE.md"
AGENTS_MD_OUT="$OUT_DIR/AGENTS.md"
GEMINI_MD_OUT="$OUT_DIR/GEMINI.md"
SESSION_OUT_DIR="$OUT_DIR/docs"
RUNTIME_DOCUMENTS_MODULE="$TEMPLATE_ROOT/scripts/setup/runtime_documents.sh"
if [ ! -f "$RUNTIME_DOCUMENTS_MODULE" ]; then
    echo "Error: setup runtime-doc module not found: $RUNTIME_DOCUMENTS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$RUNTIME_DOCUMENTS_MODULE"
setup_runtime_documents
# ── Base and variant agent assembly ──
BASE_AGENTS_MODULE="$TEMPLATE_ROOT/scripts/setup/base_agents.sh"
if [ ! -f "$BASE_AGENTS_MODULE" ]; then
    echo "Error: setup base-agent module not found: $BASE_AGENTS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$BASE_AGENTS_MODULE"
setup_base_agents

# ── Core agent pruning and injections ──
EXTENSIONS_INJECTIONS_MODULE="$TEMPLATE_ROOT/scripts/setup/extensions_and_injections.sh"
if [ ! -f "$EXTENSIONS_INJECTIONS_MODULE" ]; then
    echo "Error: setup extensions/injections module not found: $EXTENSIONS_INJECTIONS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$EXTENSIONS_INJECTIONS_MODULE"
setup_core_agent_injections_and_pruning
# ── Mutable project bootstrap (phase 1) ──
PROJECT_BOOTSTRAP_MODULE="$TEMPLATE_ROOT/scripts/setup/project_bootstrap.sh"
if [ ! -f "$PROJECT_BOOTSTRAP_MODULE" ]; then
    echo "Error: setup project-bootstrap module not found: $PROJECT_BOOTSTRAP_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$PROJECT_BOOTSTRAP_MODULE"
setup_project_bootstrap_before_docs
# ── Template-owned stage documentation ──
INFRASTRUCTURE_DOCS_MODULE="$TEMPLATE_ROOT/scripts/setup/infrastructure_docs.sh"
if [ ! -f "$INFRASTRUCTURE_DOCS_MODULE" ]; then
    echo "Error: setup infrastructure-docs module not found: $INFRASTRUCTURE_DOCS_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$INFRASTRUCTURE_DOCS_MODULE"
setup_infrastructure_docs

# Create seed folder with instructions if --seed
# ── Mutable project bootstrap (phase 2) ──
setup_project_bootstrap_after_docs
# ── Mutable environment bootstrap ──
setup_project_environment_bootstrap
# ── Host-local Python environment and dependency provisioning ──
PROVISIONING_MODULE="$TEMPLATE_ROOT/scripts/setup/provisioning.sh"
if [ ! -f "$PROVISIONING_MODULE" ]; then
    echo "Error: setup provisioning module not found: $PROVISIONING_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$PROVISIONING_MODULE"
setup_python_environment
# ── Skills and utilities ──
SKILLS_UTILITIES_MODULE="$TEMPLATE_ROOT/scripts/setup/skills_and_utilities.sh"
if [ ! -f "$SKILLS_UTILITIES_MODULE" ]; then
    echo "Error: setup skills/utilities module not found: $SKILLS_UTILITIES_MODULE" >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$SKILLS_UTILITIES_MODULE"
setup_skills_and_utilities
# ── Extensions, extension injections/pruning, and final model remap ──
setup_extensions_injections_and_pruning
# ── Emit deployment manifest from structural ownership registries ──
emit_deployment_manifest
# ── Finalization ──
if [ "$LOCAL" = "1" ]; then
    finalize_local_setup
    exit 0
fi
finalize_production_setup
# temp resources are removed by the shared _setup_cleanup EXIT trap
