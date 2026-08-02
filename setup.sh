#!/bin/bash
# Auto AI Research Template — Setup & Launch
# Usage: ./setup.sh [project-name] [--variant finance|macro|llm_cognition] [--mode empirical-first|measurement-first|report]
#                  [--ext empirical|theory_llm] [--seed|--faithful|--manual] [--light]
#                  [--no-model-probe] [--local]
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
# --light   Use the cheapest capability tier for all subagents (cheaper/faster);
#           orchestrator model unchanged. Applies to every runtime through its own
#           tier table: claude `sonnet`, codex `gpt-5.6-luna`, gemini
#           `gemini-3-flash-preview` (grok is a no-op — it has one model, grok-4.5).
#           Per-agent reasoning effort is dropped along with the tier.
# --no-model-probe  Skip the live claude-CLI availability probe. Agent models are
#           still remapped off the built-in known-unavailable list (fable/mythos
#           → opus), but newly-suspended models won't be auto-detected. Use in CI
#           or offline setups where launching `claude` at setup time isn't wanted.
#
# Legacy: --variant finance_llm is shorthand for --variant finance --ext theory_llm

set -e

# ── Parse arguments ──
PROJECT_NAME=""
VARIANT="finance"
MODE=""
LOCAL=0
DEV_SKILLS=()       # meta-repo dev skills carried in by the clone; stripped before deploy
DEV_SKILL_SUMS=()   # parallel array: SKILL.md checksum at snapshot time (collision guard)
NEXT_IS_VARIANT=0
NEXT_IS_EXT=0
NEXT_IS_MODE=0
SEEDED=0
USER_PASSED_SEED=0   # distinct from SEEDED, which --faithful also sets; used to detect a --seed + --faithful collision
FAITHFUL=0
MANUAL=0
LIGHT=0
HALT_ON_CORE_BYPASS=0
MODEL_PROBE=1
EXTENSIONS=()

for arg in "$@"; do
    case "$arg" in
        --variant)     NEXT_IS_VARIANT=1 ;;
        --ext)         NEXT_IS_EXT=1 ;;
        --mode)        NEXT_IS_MODE=1 ;;
        --seed)        SEEDED=1; USER_PASSED_SEED=1 ;;
        --faithful)    FAITHFUL=1; SEEDED=1 ;;  # faithful implies seeded folder structure
        --manual)      MANUAL=1 ;;
        --light)       LIGHT=1 ;;
        --halt-on-core-bypass) HALT_ON_CORE_BYPASS=1 ;;
        --no-model-probe) MODEL_PROBE=0 ;;
        --local)       LOCAL=1 ;;
        --theory-llm)  [[ " ${EXTENSIONS[*]} " =~ " theory_llm " ]] || EXTENSIONS+=("theory_llm") ;;  # legacy alias for --ext theory_llm (does not touch --variant)
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
    echo "Error: --variant requires a value (finance, macro, llm_cognition)"
    exit 1
fi
if [ "$NEXT_IS_EXT" = "1" ]; then
    echo "Error: --ext requires a value (empirical, theory_llm)"
    exit 1
fi
if [ "$NEXT_IS_MODE" = "1" ]; then
    echo "Error: --mode requires a value (empirical-first, measurement-first, report)"
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

# --faithful sets both FAITHFUL and SEEDED above. USER_PASSED_SEED tracks whether
# --seed was *also* passed explicitly; the documented contract is "pass one or the
# other, not both" (CLAUDE.md), so honor it with a hard error rather than silently
# collapsing to faithful.
if [ "$FAITHFUL" = "1" ] && [ "$USER_PASSED_SEED" = "1" ]; then
    echo "Error: --seed and --faithful are mutually exclusive — pass one, not both."
    echo "  --faithful is a stricter variant of --seed (it already creates output/seed/ and starts at seed_triage)."
    exit 1
fi

# ── Expand legacy finance_llm variant ──
if [ "$VARIANT" = "finance_llm" ]; then
    VARIANT="finance"
    [[ " ${EXTENSIONS[*]} " =~ " theory_llm " ]] || EXTENSIONS+=("theory_llm")
fi

# ── llm_cognition implies theory_llm ──
# The variant's empirics ARE LLM experiments: its evaluators (referee, self-attacker,
# scorer) demand experimental evidence, and --ext empirical is gated off for it, so
# theory_llm is the only producer of that evidence. A bare llm_cognition deployment
# would be an armchair pipeline that never calls a language model — a defaulting
# error, not a configuration choice. Exception: --mode report generates nothing —
# report mode prunes every theory_llm agent anyway (see prune_report_mode_agents
# in the theory_llm extension block), so auto-implying the extension there would
# only install unused deps and skills.
if [ "$VARIANT" = "llm_cognition" ] && [ "$MODE" != "report" ] && [[ ! " ${EXTENSIONS[*]} " =~ " theory_llm " ]]; then
    EXTENSIONS+=("theory_llm")
    echo "Info: --variant llm_cognition implies --ext theory_llm (auto-added)."
fi

# ── Mode validation and dependency expansion ──
# Pipeline-architecture modes are orthogonal to variants (finance/macro/llm_cognition) and to
# extensions (empirical/theory_llm). A mode may auto-add an extension it depends
# on rather than erroring when the extension is missing — flipping to
# empirical-first without the empirical agents would be incoherent, so the
# script implies the dependency rather than making the user type both flags.
if [ -n "$MODE" ]; then
    case "$MODE" in
        empirical-first)
            if [ "$VARIANT" != "finance" ]; then
                echo "Error: --mode empirical-first is finance-only in v1."
                case "$VARIANT" in
                    macro)
                        echo "  Macro support requires identification tooling for macro (issue #18) before this mode can ship."
                        ;;
                    llm_cognition)
                        echo "  llm_cognition has no identification-designer/auditor, and --ext empirical"
                        echo "  (which this mode implies) is gated off for it. Its evidence-first analogue"
                        echo "  (measurement-first) is future work — see LIMITATIONS.md."
                        ;;
                esac
                exit 1
            fi
            # Auto-imply --ext empirical (idempotent).
            if [[ ! " ${EXTENSIONS[*]} " =~ " empirical " ]]; then
                EXTENSIONS+=("empirical")
                echo "Info: --mode empirical-first implies --ext empirical (auto-added)."
            fi
            ;;
        measurement-first)
            # Evidence-first pipeline shape for the modal ML cognition paper
            # (measurement, evals, probing, interpretability): construct
            # definition + task-family design → design-plausibility gate →
            # Stage 3b experiments as the evidence core → formal
            # characterization of what was measured. The llm_cognition analog
            # of empirical-first (issue #199).
            if [ "$VARIANT" != "llm_cognition" ]; then
                echo "Error: --mode measurement-first is llm_cognition-only."
                echo "  The econ variants' evidence-first shape is --mode empirical-first"
                echo "  (finance); measurement-first is built on the theory_llm experiment"
                echo "  stage, which only llm_cognition deploys by default."
                exit 1
            fi
            # theory_llm is auto-implied for llm_cognition already (above); the
            # experiments are this mode's evidence core, so the implication is
            # load-bearing here rather than merely conventional.
            ;;
        report)
            # Report mode: referee an external submission instead of generating a paper.
            # Composes with --ext empirical / --ext theory_llm (adds extension auditors
            # to the fan-out) and with --light. No auto-implied extension — a theory-
            # only submission can be refereed without empirical agents.
            case "$VARIANT" in
                finance|macro|llm_cognition) : ;;
                *)
                    echo "Error: --mode report supports --variant finance, macro, or llm_cognition."
                    echo "  A new variant needs a templates/agents/{variant}_modes/report/vocab.json"
                    echo "  overlay before this mode can ship for it."
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Unknown mode: $MODE"
            echo "Available modes: empirical-first, measurement-first, report"
            exit 1
            ;;
    esac
fi

# ── Deduplicate EXTENSIONS ──
# Belt-and-suspenders: each add site above is individually guarded, but a user can
# still reach a duplicate by combining the legacy alias with the modern form
# (e.g. --theory-llm --ext theory_llm, or --variant finance_llm --ext theory_llm).
# A duplicate would make the extension's assembly/.env steps run twice. Collapse to
# unique values once, after all add sites have run.
if [ "${#EXTENSIONS[@]}" -gt 0 ]; then
    _seen_ext=" "
    _deduped_ext=()
    for _ext in "${EXTENSIONS[@]}"; do
        if [[ "$_seen_ext" != *" $_ext "* ]]; then
            _deduped_ext+=("$_ext")
            _seen_ext+="$_ext "
        fi
    done
    EXTENSIONS=("${_deduped_ext[@]}")
fi

# ── Variant configuration ──
case "$VARIANT" in
    finance)
        PAPER_TYPE="finance theory paper"
        TARGET_JOURNALS="top-3 finance journal (JF, JFE, RFS)"
        DOMAIN_AREAS="finance — asset pricing, corporate finance, information economics, market design, financial intermediation, banking, household finance, and behavioral finance. Scope is broad, and the following are SUFFICIENT (not necessary) conditions: a model involving an asset market, a firm or manager optimizing value, risk (borne, shared, or priced), banks/credit/lending, or households allocating across assets is in finance scope even when the topic looks like IO, information economics, or regulation. These are sufficient, not necessary — a paper can be finance without any of them."
        JOURNAL_LIST="Top-3 finance: JF, JFE, RFS, JF Insights & Perspectives (JFIP — top-3-fin tier on quality bar, JF-equivalent standard; CV credit lags; ≤7k words, single-insight, no R&R). Also: Review of Finance, Management Science, JFQA. Top accounting: JAR, JAE, TAR, RAS. Top-5 econ: AER, Econometrica, QJE, JPE, ReStud."
        AGENT_DIR="finance"
        MECHANISM_QUALIFIER="economic"
        MECHANISM_QUALIFIER_AN="an economic"
        MECHANISM_QUALIFIER_ADV="economically"
        MECHANISM_DISCIPLINE="economics"
        DEEPENING_EXTENSION_TYPES="continuous time (HJB/SDEs), incomplete markets/heterogeneity (Bewley/HANK), learning/incomplete information, general preferences (CRRA/EZ/habits), higher dimensions (N assets, continuum of agents), perturbation/approximation (formal error bounds), dynamic/stochastic, moral hazard/agency, adverse selection, mechanism design, network/contagion"
        INITIAL_TIER="top-3-fin"
        TIER_LADDER_PROSE='top-5 → top-3-fin → field → letters'
        TIER_LIST_INLINE='`top-5`, `top-3-fin`, `field`, `letters`'
        TIER_DOWNGRADE_EXAMPLES='for `top-3-fin`: JF, JFE, RFS, JF Insights \& Perspectives; for `field`: JFQA, Review of Finance, Management Science; for `letters`: Economics Letters'
        ;;
    macro)
        PAPER_TYPE="macroeconomics theory paper"
        TARGET_JOURNALS="top-5 economics journal (AER, Econometrica, QJE, JPE, ReStud) or leading macro field journal (JME, JEDC, AEJ:Macro)"
        DOMAIN_AREAS="macroeconomics — monetary economics, fiscal policy and public debt, growth and technology, labor search and unemployment, international and open-economy macro, heterogeneous-agent and distributional macro, expectations and information frictions, financial frictions and macro-finance, and business-cycle measurement. Scope is broad, and the following are SUFFICIENT (not necessary) conditions: a model with an aggregate resource constraint, a policy authority or rule, a distribution of agents that aggregates, or a friction whose consequences are measured at the aggregate level is in macro scope even when the topic looks like labor, trade, IO, or finance. These are sufficient, not necessary — a paper can be macro without any of them."
        JOURNAL_LIST="Top-5 econ: AER, Econometrica, QJE, JPE, ReStud, AER Insights (top-5 tier on quality bar, AER-equivalent 'same standards'; CV credit lags; ≤6k words, single-mechanism). Top-3 finance: JF, JFE, RFS. Macro field: JME, JEDC, AEJ:Macro, AEJ:Micro, JIE, JET, RED."
        AGENT_DIR="macro"
        MECHANISM_QUALIFIER="economic"
        MECHANISM_QUALIFIER_AN="an economic"
        MECHANISM_QUALIFIER_ADV="economically"
        MECHANISM_DISCIPLINE="economics"
        DEEPENING_EXTENSION_TYPES="continuous time (HJB/SDEs), incomplete markets/heterogeneity (Bewley/HANK), learning/incomplete information, general preferences (CRRA/EZ/habits), higher dimensions (N assets, continuum of agents), perturbation/approximation (formal error bounds), dynamic/stochastic, moral hazard/agency, adverse selection, mechanism design, network/contagion"
        INITIAL_TIER="top-5"
        TIER_LADDER_PROSE='top-5 → field → letters'
        TIER_LIST_INLINE='`top-5`, `field`, `letters`'
        TIER_DOWNGRADE_EXAMPLES='for `top-5`: AER, Econometrica, QJE, JPE, ReStud, AER Insights; for `field`: JME, JEDC, AEJ:Macro, RED; for `letters`: Economics Letters'
        ;;
    llm_cognition)
        # Article-safe: PAPER_TYPE starts with a consonant sound ("language-…")
        # so the "a {{PAPER_TYPE}}" template in core.md reads correctly
        # ("a language-model cognition paper"); "LLM …" would need "an".
        PAPER_TYPE="language-model cognition paper"
        TARGET_JOURNALS="top ML venue (NeurIPS, ICML, ICLR)"
        DOMAIN_AREAS="the science of language-model cognition and evaluation — effective working memory and context use, abstraction and compression, in-context learning, reasoning limits, interference and binding, benchmark and measurement design, and scaling behavior of capabilities. Scope is broad, and the following are SUFFICIENT (not necessary) conditions: a paper that defines a construct of LLM capability or behavior, formalizes it, and measures it in real models is in scope, as are formal-only analyses of transformer computation and evaluation-methodology papers. These are sufficient, not necessary — a paper can be in scope without any of them."
        JOURNAL_LIST="Top ML venues: NeurIPS, ICML, ICLR; at parity — JMLR (selective archival journal), ACL/EMNLP (natural home for NLP-native work; lateral, not a downgrade), Nature Machine Intelligence (journal-format outlet). Nature-family (landmark results with broad scientific resonance): Nature, Science. Field: TMLR (rolling submission, correctness-over-significance bar — the default downgrade target from top-ml), CogSci, Computational Linguistics, TACL. Workshop tier: NeurIPS/ICML/ICLR workshop tracks."
        AGENT_DIR="llm_cognition"
        MECHANISM_QUALIFIER="computational"
        MECHANISM_QUALIFIER_AN="a computational"
        MECHANISM_QUALIFIER_ADV="computationally"
        MECHANISM_DISCIPLINE="computational account"
        DEEPENING_EXTENSION_TYPES="alternative task families instantiating the same construct, tighter or more general formal results (capacity bounds, error characterizations, formal error bounds), cross-model-family and cross-scale replication, discriminating experiments against the nearest alternative account, mechanistic/interpretability probes of the claimed process, connections to the human-cognition or information-theory literature, boundary/degenerate-corner characterization"
        INITIAL_TIER="top-ml"
        TIER_LADDER_PROSE='nature → top-ml → field → workshop'
        TIER_LIST_INLINE='`nature`, `top-ml`, `field`, `workshop`'
        TIER_DOWNGRADE_EXAMPLES='for `top-ml`: NeurIPS, ICML, ICLR, JMLR, ACL, EMNLP; for `field`: TMLR (default), CogSci, Computational Linguistics, TACL; for `workshop`: NeurIPS/ICML/ICLR workshop tracks'
        PRINCIPLED_MECHANISM_PHRASE="falls out of the computational account"
        CHARACTERIZE_EXAMPLE_BULLET="If a result holds under one stimulus distribution but not another, find the exact condition on the distribution that makes it work."
        NUMERICAL_VERIFICATION_BULLET="Don't settle for numerical verification of what should be a theorem — and don't force a theorem where the claim is inherently empirical: systematic measurement across models, seeds, and stimuli is first-class evidence in this domain. The rule governs claims presented as formal results."
        ;;
    *)
        echo "Unknown variant: $VARIANT"
        echo "Available variants: finance, macro, llm_cognition"
        exit 1
        ;;
esac

# Domain-example defaults for variants that didn't override them in the case above
# (finance/macro keep the pre-extraction economics text, byte-identical).
if [ -z "${PRINCIPLED_MECHANISM_PHRASE:-}" ]; then
    PRINCIPLED_MECHANISM_PHRASE="falls out of economics"
fi
if [ -z "${CHARACTERIZE_EXAMPLE_BULLET:-}" ]; then
    CHARACTERIZE_EXAMPLE_BULLET="If a result holds under CARA but not CRRA, find the exact condition on preferences that makes it work."
fi
if [ -z "${NUMERICAL_VERIFICATION_BULLET:-}" ]; then
    NUMERICAL_VERIFICATION_BULLET="Don't settle for numerical verification of what should be a theorem."
fi

# ── Per-variant skill gating (issue #205) ──
# Economics-only toolkits are dead weight in an llm_cognition deployment: since
# v2.9.0 no assembled body points llm_cognition agents at them (the advice
# bullets are vocab-keyed), but they still cost context in every session's
# skill listing and are discoverable by agents browsing the skills dir. Gate
# them out of assembly, the utils copy, the deps install, and the manual-mode
# catalogs. Removal on refresh of an existing deployment is handled by
# update.sh's stale-infrastructure sweep (dirs listed in the old manifest but
# absent from the fresh manifest are deleted), so no manifest entry changes
# are needed here — the manifest emission is presence-filtered.
VARIANT_SKILL_EXCLUDES=""
[ "$VARIANT" = "llm_cognition" ] && VARIANT_SKILL_EXCLUDES=" ssj nber_agenda "
variant_wants_skill() {
    case "$VARIANT_SKILL_EXCLUDES" in
        *" $1 "*) return 1 ;;
        *) return 0 ;;
    esac
}

# ── Variant/extension compatibility ──
# The empirical extension loads per-variant agent metadata
# (extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json), which exists
# only for finance and macro — its agents (identification-designer, empiricist)
# are calibrated to observational economic data. llm_cognition papers get their
# empirics from --ext theory_llm (LLM experiments) instead.
if [ "$VARIANT" = "llm_cognition" ] && [[ " ${EXTENSIONS[*]} " =~ " empirical " ]]; then
    echo "Error: --ext empirical is not supported with --variant llm_cognition."
    echo "  The empirical extension's per-variant agents exist only for finance/macro."
    echo "  For LLM-cognition experiments use --ext theory_llm."
    exit 1
fi

# ── Tier vocab for agent bodies ──
# The tier ladder is a setup.sh-level shell variable (set in the variant case
# above) that the runtime-doc assembler consumes directly, but agent BODIES go
# through the vocab-substitution path. Bodies that must name the variant's tier
# slugs (editor.md's ladder/allowed-values lines) reference {{TIER_LIST_INLINE}}
# / {{TIER_LADDER_PROSE}}, resolved from this generated overlay so the ladder
# has exactly one source of truth per deploy. Passed to every base assembler
# (shared + variant, all four runtimes). Build-time only (mktemp, never
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
TIER_VOCAB_FILE="$(mktemp "${TMPDIR:-/tmp}/tier_vocab.XXXXXX")"
TIER_LIST_INLINE="$TIER_LIST_INLINE" TIER_LADDER_PROSE="$TIER_LADDER_PROSE" python3 - "$TIER_VOCAB_FILE" <<'PYEOF'
import json, os, sys
with open(sys.argv[1], "w") as f:
    json.dump({
        "TIER_LIST_INLINE": os.environ["TIER_LIST_INLINE"],
        "TIER_LADDER_PROSE": os.environ["TIER_LADDER_PROSE"],
    }, f)
PYEOF

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
elif [ "$MODE" = "measurement-first" ]; then
    case "$VARIANT" in
        llm_cognition)
            # Article-safe: starts with a consonant sound ("measurement-…"),
            # matching the base variant's "language-model …" convention.
            PAPER_TYPE="measurement-first language-model cognition paper"
            DOMAIN_AREAS="the science of language-model cognition and evaluation, measurement-first — the contribution is a construct made measurable (a formal construct definition plus a task family that operationalizes it) and the experimental evidence it yields in real models; formal characterization follows the measurements rather than preceding them. In scope: capability and behavior measurement, evaluation methodology, probing and interpretability protocols, benchmark design, scaling and context-use measurement."
            DOC_SUBTITLE="Autonomous Measurement Paper Pipeline"
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
# generated per-deploy below with the deploying user's $HOME baked in (grok's
# sandbox.toml does not expand ~/$HOME). Launched via
# `grok --sandbox pipeline --always-approve --leader-socket "$(pwd)/.grok/leader.sock"`
# (the per-project leader socket keeps concurrent grok projects from cancelling
# each other's turns — see the launch-line comment below).
GROK_SANDBOX_REL="$GROK_DIR_REL/sandbox.toml"


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
# Metadata twin of the body/vocab overlays: passed to every agent assembler so
# an agent's metadata["modes"][mode_slug] field overrides (e.g. a report-mode
# `description` matching the overlaid body) merge over its base fields.
MODE_METADATA_ARGS=()
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
    MODE_METADATA_ARGS=(--mode "$mode_slug")
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

assemble_claude_variant_agents() {
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

assemble_codex_variant_agents() {
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

assemble_gemini_variant_agents() {
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

assemble_grok_shared_agents() {
    local template_root="$1"
    local dest_dir="$2"
    # Mirrors assemble_gemini_shared_agents — see assemble_claude_shared_agents
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

assemble_grok_variant_agents() {
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
    mkdir -p "$OUT_DIR/$GROK_AGENTS_REL"
    # Copy shared project files. (The runtime settings files themselves are
    # installed by the shared install_runtime_settings block below, which serves
    # both --local and production.)
    mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL"
    mkdir -p "$OUT_DIR/$GEMINI_DIR_REL"
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
        # Variant-correct subtitle (title-cased PAPER_TYPE; renders the historical
        # "Autonomous Finance Theory Paper Generator" byte-identically for finance).
        DASHBOARD_SUBTITLE="Autonomous $(python3 -c "import sys; print(sys.argv[1].title())" "$PAPER_TYPE") Generator"
        sed -i.bak "s|Autonomous Finance Theory Paper Generator|$DASHBOARD_SUBTITLE|" "$OUT_DIR/dashboard.html" && rm "$OUT_DIR/dashboard.html.bak"
    fi
    # launch.sh must be present in the fresh --local deploy so update.sh's
    # manifest copy can propagate it into existing deployments (production
    # deploys get it via the clone). All modes: the non-driver runtimes and
    # `codex --once` apply everywhere; the codex driver self-refuses cleanly
    # when there is no pipeline_state.json (manual/report).
    cp "$SCRIPT_DIR/launch.sh" "$OUT_DIR/"

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
    # Clone source is overridable via ZEROPAPER_REPO (a local path or alternate
    # URL) for offline/local testing of un-pushed template changes; defaults to
    # the public repo. A local-path clone only sees committed state.
    git clone "${ZEROPAPER_REPO:-https://github.com/alejandroll10/zeropaper.git}" "$PROJECT_NAME"
    cd "$PROJECT_NAME"
    git remote remove origin
    rm -rf .git
    git init -q -b main

    # Snapshot the meta-repo's own dev-facing skills (currently deploy-project).
    # Anything under .claude/skills/ at this point arrived with the clone and is
    # template-development tooling; the deployed project's real skills are assembled
    # later from templates/skill_bodies/. Removed in the cleanup block below, so no
    # deployment-manifest entry (build-time only, same as VERSION/CHANGELOG.md).
    # Snapshot-based rather than a name list: adding a dev skill needs no setup.sh edit.
    #
    # The checksum is a collision guard. assemble_claude_skills.py does mkdir(exist_ok)
    # + write_text, so a future skill_id matching a dev-skill directory name would
    # overwrite it in place — and a name-only cleanup would then delete a legitimate
    # assembled project skill. Recording the checksum lets cleanup tell the two apart
    # and fail safe (keep the project skill) rather than fail destructive.
    for d in .claude/skills/*/; do
        [ -d "$d" ] || continue
        DEV_SKILLS+=("$d")
        if [ -f "$d/SKILL.md" ]; then
            DEV_SKILL_SUMS+=("$(cksum < "$d/SKILL.md")")
        else
            DEV_SKILL_SUMS+=("")
        fi
    done

    TEMPLATE_ROOT="."
    OUT_DIR="."
fi

# ── Install per-runtime settings files (install_runtime_settings) ──
# Runs for BOTH --local and production, and is the only writer of these two
# paths. In production the clone carries this repo's own .claude/settings.json /
# .gemini/settings.json into the project folder; those are the template repo's
# DEV settings and must not survive, so the copies below overwrite them
# unconditionally rather than merging. Fail loud on a missing source: shipping a
# project with the dev sandbox posture (or none) is worse than not shipping.
# .grok/sandbox.toml needs no entry here — it is generated per-deploy further
# down, with the deploying user's $HOME baked in.
mkdir -p "$OUT_DIR/$CLAUDE_DIR_REL" "$OUT_DIR/$GEMINI_DIR_REL"
for _rt_pair in "$CLAUDE_SETTINGS_SRC_REL:$CLAUDE_SETTINGS_REL" "$GEMINI_SETTINGS_SRC_REL:$GEMINI_SETTINGS_REL"; do
    _rt_src="$TEMPLATE_ROOT/${_rt_pair%%:*}"
    _rt_dst="$OUT_DIR/${_rt_pair##*:}"
    if [ ! -f "$_rt_src" ]; then
        echo "Error: runtime settings template not found: $_rt_src" >&2
        exit 1
    fi
    cp "$_rt_src" "$_rt_dst"
done

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
    # Variant-gated core skills (issue #205): keep the catalogs consistent with
    # what the install blocks below actually assemble for this variant.
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
    --mechanism-qualifier "$MECHANISM_QUALIFIER" \
    --mechanism-qualifier-adv "$MECHANISM_QUALIFIER_ADV" \
    --deepening-extension-types "$DEEPENING_EXTENSION_TYPES" \
    --characterize-example-bullet "$CHARACTERIZE_EXAMPLE_BULLET" \
    --numerical-verification-bullet "$NUMERICAL_VERIFICATION_BULLET" \
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
    --mechanism-qualifier "$MECHANISM_QUALIFIER" \
    --mechanism-qualifier-adv "$MECHANISM_QUALIFIER_ADV" \
    --deepening-extension-types "$DEEPENING_EXTENSION_TYPES" \
    --characterize-example-bullet "$CHARACTERIZE_EXAMPLE_BULLET" \
    --numerical-verification-bullet "$NUMERICAL_VERIFICATION_BULLET" \
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
    --mechanism-qualifier "$MECHANISM_QUALIFIER" \
    --mechanism-qualifier-adv "$MECHANISM_QUALIFIER_ADV" \
    --deepening-extension-types "$DEEPENING_EXTENSION_TYPES" \
    --characterize-example-bullet "$CHARACTERIZE_EXAMPLE_BULLET" \
    --numerical-verification-bullet "$NUMERICAL_VERIFICATION_BULLET" \
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
    GROK_AGENTS_OUT="$OUT_DIR/$GROK_AGENTS_REL"
else
    AGENTS_OUT="$CLAUDE_AGENTS_REL"
    CODEX_AGENTS_OUT="$CODEX_AGENTS_REL"
    GEMINI_AGENTS_OUT="$GEMINI_AGENTS_REL"
    GROK_AGENTS_OUT="$GROK_AGENTS_REL"
    mkdir -p "$AGENTS_OUT"
    mkdir -p "$CODEX_AGENTS_OUT"
    mkdir -p "$GEMINI_AGENTS_OUT"
    mkdir -p "$GROK_AGENTS_OUT"
fi

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

assemble_claude_shared_agents "$TEMPLATE_ROOT" "$AGENTS_OUT"
assemble_codex_shared_agents "$TEMPLATE_ROOT" "$CODEX_AGENTS_OUT"
assemble_gemini_shared_agents "$TEMPLATE_ROOT" "$GEMINI_AGENTS_OUT"
assemble_grok_shared_agents "$TEMPLATE_ROOT" "$GROK_AGENTS_OUT"

if [ -f "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json" ]; then
    assemble_claude_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$AGENTS_OUT"
    assemble_codex_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$CODEX_AGENTS_OUT"
    assemble_gemini_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GEMINI_AGENTS_OUT"
    assemble_grok_variant_agents "$TEMPLATE_ROOT" "$AGENT_DIR" "$GROK_AGENTS_OUT"
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

echo "  ✓ Agents assembled (shared + ${AGENT_DIR})"

# ── Prune agents not used in --mode report ──
# Report mode only invokes the audit fan-out + report-synthesizer. Generative,
# pipeline-management, scoring, broad-survey, and writing-style agents have no
# job here. Removing them at assembly time prevents accidental invocation and
# keeps the deployed .claude/agents/ catalog focused. Audit, polish-*, referee*,
# bib-verifier, novelty-checker, self-attacker, debugger, report-synthesizer
# stay; extension generative agents (empiricist, identification-designer,
# experiment-designer) are pruned per-extension below by the same function.
# Delete assembled agent output files across all three runtimes. The
# mode/flag-conditional prune passes below decide *when* to call this; this
# helper just does the removal, so a new runtime output dir is wired in one
# place, not once per prune pass.
prune_agents() {
    local _name
    for _name in "$@"; do
        rm -f "$AGENTS_OUT/${_name}.md" "$CODEX_AGENTS_OUT/${_name}.toml" "$GEMINI_AGENTS_OUT/${_name}.md" "$GROK_AGENTS_OUT/${_name}.md"
    done
}

prune_report_mode_agents() {
    [ "$MODE" = "report" ] || return 0
    prune_agents "$@"
}

# Mode-conditional ADDITION (inverse of prune_report_mode_agents): an agent that
# is assembled for all --ext empirical deploys (it lives in the empirical
# extension metadata) but is meaningful ONLY under --mode empirical-first — the
# prose+DAG mechanism it audits exists only in that mode. We assemble it
# unconditionally with the rest of the empirical agents, then delete its output
# files in every other mode. This keeps the agent off the theory-first /
# macro / report build surface without adding a mode-conditional metadata path.
prune_non_empirical_first_agents() {
    [ "$MODE" = "empirical-first" ] && return 0
    prune_agents "$@"
}

# Inverse of prune_report_mode_agents (#164): report-synthesizer is invoked ONLY
# under --mode report (it aggregates audits/*.md into report/referee_report.md).
# It lives in shared agent metadata, so it assembles into every build; delete it
# in every non-report build so it never sits in the orchestrator's
# available-agents list where it can never fire (and can't be improvised into,
# e.g., a Stage-6 aggregation the `editor` agent owns).
prune_non_report_mode_agents() {
    [ "$MODE" = "report" ] && return 0
    prune_agents "$@"
}

# faithful-drift-auditor is launched ONLY on --faithful runs. It too assembles
# from shared metadata into every build; delete it in every non-faithful build.
# (This subsumes the report-mode case — report ⊥ faithful — so it need not be
# listed in prune_report_mode_agents.) (#164)
prune_non_faithful_agents() {
    [ "$FAITHFUL" = "1" ] && return 0
    prune_agents "$@"
}

# Core agents not deployed in report mode (rationale documented in
# templates/runtime/{claude,codex,gemini}/session_report.md's "What this mode
# does not do" block). Extension generative agents are pruned in the extension
# block below after they have been assembled.
prune_report_mode_agents \
    theory-generator \
    paper-writer \
    question-poser \
    question-referee \
    idea-generator \
    idea-reviewer \
    idea-prototyper \
    theory-explorer \
    implications-deriver \
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
    style

if [ "$MODE" = "report" ]; then
    echo "  ✓ Pruned generative / management agents for --mode report"
fi

# ── Prune agents meaningful only in a mode/flag this build didn't select (#164) ──
# Symmetric to prune_report_mode_agents: these ship from shared metadata but can
# only ever fire in one mode/flag. Removing them keeps the deployed
# .claude/agents/ catalog to agents this build can actually invoke.
prune_non_report_mode_agents report-synthesizer
prune_non_faithful_agents faithful-drift-auditor

# ── Inject variant context into agents ──
VARIANT_BLOCK="
## Variant context
- **Paper type:** ${PAPER_TYPE}
- **Target journals:** ${JOURNAL_LIST}
- **Domain:** ${DOMAIN_AREAS}
"

for agent in literature-scout gap-scout novelty-checker theory-explorer implications-deriver referee referee-freeform referee-mechanism scorer scorer-freeform editor branch-manager last-resort paper-writer style report-synthesizer; do
    if [ -f "$AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$AGENTS_OUT/$agent.md"
    fi
    if [ -f "$CODEX_AGENTS_OUT/$agent.toml" ]; then
        # Insert before the closing ''' in the TOML multiline string
        # Use awk to find the LAST ''' and insert the block before it.
        # Pass the (multi-line) block via the environment, not `-v`: BSD awk
        # (stock macOS) rejects literal newlines in a `-v` value; ENVIRON is
        # portable across BSD and GNU awk.
        VARIANT_BLOCK="$VARIANT_BLOCK" awk '
        { lines[NR] = $0 }
        /^'\'''\'''\''$/ { last = NR }
        END {
            for (i = 1; i <= NR; i++) {
                if (i == last) print ENVIRON["VARIANT_BLOCK"]
                print lines[i]
            }
        }' "$CODEX_AGENTS_OUT/$agent.toml" > "$CODEX_AGENTS_OUT/$agent.toml.tmp" \
        && mv "$CODEX_AGENTS_OUT/$agent.toml.tmp" "$CODEX_AGENTS_OUT/$agent.toml"
    fi
    if [ -f "$GEMINI_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GEMINI_AGENTS_OUT/$agent.md"
    fi
    if [ -f "$GROK_AGENTS_OUT/$agent.md" ]; then
        echo "$VARIANT_BLOCK" >> "$GROK_AGENTS_OUT/$agent.md"
    fi
done
echo "  ✓ Variant context injected into agents"

# ── Agent body inject helpers ──
# `inject_block_into_agents <inject_file> <agent>...` appends the contents of
# <inject_file> to the assembled body of each named agent across all three runtimes
# (claude `.md`, codex `.toml`, gemini `.md`). The codex append uses awk to splice
# the block in just before the closing `'''` of the TOML prompt body; the claude/
# gemini appends are plain. File-existence guards make a not-yet-assembled agent a
# harmless no-op. Single source of the per-runtime append logic for every inject
# loop below (faithful, bash-background, core-bypass, efficiency).
inject_block_into_agents() {
    local _inject_file="$1"; shift
    if [ ! -f "$_inject_file" ]; then
        echo "Error: inject template not found: $_inject_file" >&2
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
            # Multi-line block via environment, not `-v` (BSD-awk-safe; see note above).
            _block="$_block" awk '
            { lines[NR] = $0 }
            /^'\'''\'''\''$/ { last = NR }
            END {
                for (i = 1; i <= NR; i++) {
                    if (i == last) print ENVIRON["_block"]
                    print lines[i]
                }
            }' "$CODEX_AGENTS_OUT/$_agent.toml" > "$CODEX_AGENTS_OUT/$_agent.toml.tmp" \
            && mv "$CODEX_AGENTS_OUT/$_agent.toml.tmp" "$CODEX_AGENTS_OUT/$_agent.toml"
        fi
        if [ -f "$GEMINI_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GEMINI_AGENTS_OUT/$_agent.md"
        fi
        if [ -f "$GROK_AGENTS_OUT/$_agent.md" ]; then
            printf '\n%s\n' "$_block" >> "$GROK_AGENTS_OUT/$_agent.md"
        fi
    done
}

# ── Faithful-mode contract pointer for developing agents (--faithful only) ──
# Faithful mode adds a short pointer to *developing* agents — those that
# produce paper content — directing them to read `output/seed/mechanism_contract.md`
# before producing output. *Evaluators* (scorer, referees, auditors, novelty-checker,
# self-attacker, idea-{prototyper,reviewer}, branch-manager) stay impartial: quoting
# the contract into them would corrupt the evaluation signal. The faithful constraint
# enters at the orchestrator's routing of evaluator verdicts (see faithful.md),
# not at the evaluators themselves.
#
# Called once after core agent assembly and once inside each extension block (after
# the extension finishes assembling its own agents) so extension developing agents
# (empiricist, identification-designer, experiment-designer, etc.) also get the
# pointer. A no-op when FAITHFUL=0.
inject_faithful_into_agents() {
    [ "$FAITHFUL" = "1" ] || return 0
    inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/faithful_inject.md" "$@"
}

# `inject_bash_background_into_agents` appends the no-nohup / use-a-harness-
# tracked-background-job note to every Bash-capable agent. Unconditional (unlike
# the faithful injector): subagents never see the runtime doc, so a heavy job
# launched by e.g. theory-explorer/empiricist/experiment-designer would otherwise
# go unmonitored. Called after core assembly and inside each extension block.
inject_bash_background_into_agents() {
    inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/bash_background.md" "$@"
}

# `inject_efficiency_into_agents` appends the compute-efficiency mandate (issue
# #74) — be mindful of memory/runtime/cost, size the data and method before
# running, stream rather than eager-load, test on a subsample — to the explicit
# set of data/compute-heavy agents (theory-explorer; the empirical empiricist/
# auditors/replicator; the theory_llm experiment-designer). Unconditional like the
# bash-background injector: subagents never see the runtime doc, and an OOM /
# runaway-cost run is a recurring cross-repo cost (see issue #74's evidence). The
# heavy set is an explicit list, not metadata-derived — "compute-heavy" is not a
# metadata category, and an explicit auditable list is clearer than approximating
# it via --has-tool Bash, which over-injects into read-only agents (scribe,
# literature-scout, polish-prose, ...). Called after core assembly and inside each
# extension block; file-existence guards make a not-yet-assembled agent a no-op.
inject_efficiency_into_agents() {
    inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/efficiency_inject.md" "$@"
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
    inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/core_bypass_inject.md" "$@"
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
_core_developing_agents=()
while IFS= read -r _line; do _core_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --category developing \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: empty here means the lister errored (the read loop masks it under set -e),
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
_core_bash_agents=()
while IFS= read -r _line; do _core_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
    --has-tool Bash \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_shared_agents.json" \
    --metadata "$TEMPLATE_ROOT/templates/agent_metadata/claude_variant_agents.json")
# Fail loud: the read loop masks python failure under set -e, so an empty list here
# means the lister errored or metadata is missing — never a real empty result.
if [ "${#_core_bash_agents[@]}" -eq 0 ]; then
    echo "Error: Bash-capable core agent list is empty (lister failed or metadata missing)" >&2
    exit 1
fi
inject_bash_background_into_agents "${_core_bash_agents[@]}"
echo "  ✓ Background-job note injected into Bash-capable core agents"

# Efficiency mandate (issue #74): inject into the explicit set of data/compute-
# heavy core agents. theory-explorer is the only core agent that runs real
# computation/simulation; the empirical/theory_llm heavy agents get the mandate in
# their own extension blocks.
_core_heavy_agents=(theory-explorer)
inject_efficiency_into_agents "${_core_heavy_agents[@]}"
echo "  ✓ Efficiency mandate injected into compute-heavy core agents"

# ── Report-mode context for pipeline-native audit agents (--mode report only) ──
# The report-mode fan-out reuses audit agents whose bodies were written for this
# pipeline's own drafts: they hardcode reads of pipeline artifacts
# (output/stage*/ theory drafts, negative_results, prior audit rounds) and writes
# to pipeline paths (output/polish_*_r{N}.md). In report mode neither exists —
# inputs live in submission/ and outputs go to the prompt-passed audits/<name>.md
# path. This block re-anchors those bodies: prompt paths win, pipeline artifacts
# don't exist, PDF-only submissions degrade with an explicit note, and
# submission/ is read-only. Excluded on purpose: the referee trio and
# polish-identification (report-native body overlays in
# templates/agent_bodies/shared_modes/report/), report-synthesizer (report-native
# shared body), and debugger (reactive tool-failure diagnosis, not a
# submission-facing audit). Keep this list in sync with the Step 2 fan-out table
# in templates/shared/core_report.md.
inject_report_mode_into_agents() {
    [ "$MODE" = "report" ] || return 0
    inject_block_into_agents "$TEMPLATE_ROOT/templates/shared/report_mode_inject.md" "$@"
}
_report_pipeline_native_audit_agents=(
    math-auditor
    math-auditor-freeform
    self-attacker
    novelty-checker
    bib-verifier
    polish-formula
    polish-numerics
    polish-consistency
    polish-equilibria
    polish-prose
    polish-bibliography
    polish-institutions
)
inject_report_mode_into_agents "${_report_pipeline_native_audit_agents[@]}"
if [ "$MODE" = "report" ]; then
    echo "  ✓ Report-mode context injected into pipeline-native audit agents"
fi

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
# Version stamp = human-readable semver (from the VERSION file, the single
# source of truth) + exact build provenance (git short hash), e.g.
# "2.6.0+73b6911". VERSION is build-time only (read here, never deployed), so
# it needs no deployment-manifest entry. If VERSION is missing or empty we fall
# back to the bare hash — identical to the pre-versioning behavior, fail-safe.
ARP_HASH=$(cd "$TEMPLATE_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
ARP_SEMVER=$(tr -d '[:space:]' < "$TEMPLATE_ROOT/VERSION" 2>/dev/null || true)
if [ -n "$ARP_SEMVER" ]; then
    ARP_VERSION="${ARP_SEMVER}+${ARP_HASH}"
else
    ARP_VERSION="$ARP_HASH"
fi
# Watermark mode field (LICENSE §2): "manual" marks a research-toolkit
# deployment whose output is human-directed Assisted Output; anything else
# is "autonomous". The pdfsubject provenance phrase softens accordingly so
# the watermark doesn't misattribute assisted work as pipeline-generated.
if [ "$MANUAL" = "1" ]; then
    ARP_MODE="manual"
    ARP_PROVENANCE="Produced with assistance from"
else
    ARP_MODE="autonomous"
    ARP_PROVENANCE="Generated by"
fi
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
        -e "s|{{ARP_MODE}}|$ARP_MODE|g" \
        -e "s|{{ARP_PROVENANCE}}|$ARP_PROVENANCE|g" \
        "$TEMPLATE_ROOT/templates/paper_skeleton/arpipeline.sty.template" \
        > "$P/paper/arpipeline.sty"
    # Don't clobber an existing main.tex (e.g. --seed mode where the user has
    # pre-populated paper/main.tex). The .sty above is always overwritten —
    # it is pipeline infrastructure with a fresh UUID per deployment.
    # Skeleton templates are variant-aware: templates/paper_skeleton/{VARIANT}/
    # overrides the shared root template when present (llm_cognition ships an
    # ML-preprint main.tex — single-column, numeric citations — instead of the
    # economics working-paper format). Root templates are the fallback, so a
    # new variant needs no skeleton files unless its format genuinely differs.
    if [ ! -f "$P/paper/main.tex" ]; then
        MAIN_TEX_TEMPLATE="$TEMPLATE_ROOT/templates/paper_skeleton/main.tex.template"
        [ -f "$TEMPLATE_ROOT/templates/paper_skeleton/$VARIANT/main.tex.template" ] \
            && MAIN_TEX_TEMPLATE="$TEMPLATE_ROOT/templates/paper_skeleton/$VARIANT/main.tex.template"
        cp "$MAIN_TEX_TEMPLATE" "$P/paper/main.tex"
    fi
    # Internet appendix skeleton. paper-writer only populates it when a proof
    # exceeds ~3 pages or the in-paper appendix would otherwise blow past ~30%
    # of main-text length; otherwise it stays a no-op placeholder. Same skip-
    # if-exists guard and variant-override lookup as main.tex above.
    if [ ! -f "$P/paper/internet_appendix.tex" ]; then
        IA_TEX_TEMPLATE="$TEMPLATE_ROOT/templates/paper_skeleton/internet_appendix.tex.template"
        [ -f "$TEMPLATE_ROOT/templates/paper_skeleton/$VARIANT/internet_appendix.tex.template" ] \
            && IA_TEX_TEMPLATE="$TEMPLATE_ROOT/templates/paper_skeleton/$VARIANT/internet_appendix.tex.template"
        cp "$IA_TEX_TEMPLATE" "$P/paper/internet_appendix.tex"
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
    # --mode empirical-first and --mode measurement-first (piloting is part
    # of the design step there); don't create the empty dir in either.
    STAGE2B_DIRS=()
    [ "$MODE" != "empirical-first" ] && [ "$MODE" != "measurement-first" ] && STAGE2B_DIRS=("$P/output/stage2b/figures")
    mkdir -p "$P/output/stage0" "$P/output/stage1" "$P/output/stage2" "${STAGE2B_DIRS[@]}" "$P/output/stage3" "$P/output/stage4" "$P/output/puzzle_triage" "$P/output/post_pipeline"
    mkdir -p "$P/process_log/sessions" "$P/process_log/decisions"
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
        sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$_docfile" && rm "${_docfile}.bak"
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
    # Stage 1 INCREMENTAL-forwarding override) get stripped cleanly in regular
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
- Implement your seed faithfully — its named mechanism, object of study, and
  identification strategy stay intact. Predicted results (signs, thresholds,
  existence claims, comparative statics) are hypotheses the pipeline tests, not
  frozen conclusions: specify the setup, not the result. A falsified prediction
  gets corrected and documented, not defended.
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
  "theory_attempt": 1,
  "theory_version": 1,
  "regeneration_round": 0,
  "gate0_best_question_score": -1,
  "loops": {
    "gate0_revise":      {"round": 0, "cap": 3},
    "gate0_reject":      {"round": 0, "cap": 5},
    "idea":              {"round": 0, "cap": 5},
    "reject_cosmetic":   {"round": 0, "cap": 2},
    "downgrade_enrich":  {"round": 0, "cap": 2},
    "last_resort_stuck": {"round": 0, "cap": 2},
    "pivot":             {"round": 0, "cap": 2},
    "fix_empirics":      {"round": 0, "cap": 2},
    "referee":           {"round": 0, "cap": 10},
    "bib_verify":        {"round": 0, "cap": 2},
    "polish":            {"round": 0, "cap": 2}
  },
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "target_journal_tier": "__INITIAL_TIER__",
  "initial_journal_tier": "__INITIAL_TIER__",
  "status": "not_started",
  "seeded": true,
  "faithful": $([ "$FAITHFUL" = "1" ] && echo true || echo false),
  "halt_on_core_bypass": $([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo true || echo false),
  "pending_verification": [],
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
  "theory_attempt": 1,
  "theory_version": 1,
  "regeneration_round": 0,
  "gate0_best_question_score": -1,
  "loops": {
    "gate0_revise":      {"round": 0, "cap": 3},
    "gate0_reject":      {"round": 0, "cap": 5},
    "idea":              {"round": 0, "cap": 5},
    "reject_cosmetic":   {"round": 0, "cap": 2},
    "downgrade_enrich":  {"round": 0, "cap": 2},
    "last_resort_stuck": {"round": 0, "cap": 2},
    "pivot":             {"round": 0, "cap": 2},
    "fix_empirics":      {"round": 0, "cap": 2},
    "referee":           {"round": 0, "cap": 10},
    "bib_verify":        {"round": 0, "cap": 2},
    "polish":            {"round": 0, "cap": 2}
  },
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "target_journal_tier": "__INITIAL_TIER__",
  "initial_journal_tier": "__INITIAL_TIER__",
  "seeded": false,
  "faithful": false,
  "halt_on_core_bypass": __HALT_ON_CORE_BYPASS__,
  "status": "not_started",
  "pending_verification": [],
  "scores": {},
  "stage2b_theory_version": null,
  "stage1_candidates": [],
  "history": []
}
JSONEOF
    sed -i.bak "s|__INITIAL_TIER__|$INITIAL_TIER|g; s|__HALT_ON_CORE_BYPASS__|$([ "$HALT_ON_CORE_BYPASS" = "1" ] && echo true || echo false)|g" "$P/process_log/pipeline_state.json" && rm "$P/process_log/pipeline_state.json.bak"
fi

# pipeline_state.json: measurement-first adds stage2_design_version — the
# plan-time design gate's version pointer (Gate 4 blocks while it lags
# theory_version), mirroring empirical-first's stage2_mechanism_version. The
# theory_llm extension adds stage3b_theory_version separately below.
if [ "$MODE" = "measurement-first" ] && [ -f "$P/process_log/pipeline_state.json" ]; then
    python3 - "$P/process_log/pipeline_state.json" <<'PYMF'
import json, sys
p = sys.argv[1]
with open(p) as f:
    data = json.load(f)
if "stage2_design_version" not in data:
    new = {}
    for k, v in data.items():
        new[k] = v
        if k == "stage2b_theory_version":
            new["stage2_design_version"] = None
    with open(p, "w") as f:
        json.dump(new, f, indent=2)
        f.write("\n")
PYMF
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
*unresolved* until the verification is re-run as binding and its `action` is set
to `resolved`. An unresolved binding row blocks a plain `status = "complete"` even
in the default deploy. Which way it blocks depends on the outage: a **deferrable**
one (a rate/credit limit with a stated reset horizon, where re-checking is a cheap
lookup) finishes the run and sets `status = "complete_pending_verification"` with
the owed check recorded in `pending_verification`; anything else sets
`status = "halted_core_bypass"`. Either way the run never reports clean success on
a downgraded core — that is the terminal backstop. A running session may set a row
`resolved` only for a binding verification it re-ran itself and that came back
clean; every other resolution is operator-driven. Report mode has no
`pipeline_state.json` / `status` machine, so the blocking rule does not apply
there — rows are recorded and surfaced in the returned report only.

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
# Falls back to the committed .env.example so a fresh clone (which has no .env,
# since it is gitignored) still lands a scaffold in the project to fill in,
# rather than no file at all.
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$P/.env"
    # A final line with no trailing newline is silently dropped by update.sh's
    # line-by-line merge, so normalize on the way out.
    [ -n "$(tail -c1 "$P/.env")" ] && printf '\n' >> "$P/.env"
    echo "  ✓ .env copied from template repo"
    # The repo's personal .env can predate keys later added to .env.example; a
    # plain copy would propagate that staleness into every new deployment —
    # silently, since consumers fall back to placeholder defaults rather than
    # fail (e.g. the SEC_EDGAR_* identity). Union in whatever is missing, with
    # the same merge routine update.sh uses on existing deployments.
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        . "$SCRIPT_DIR/scripts/merge_env_keys.sh"
        merge_env_missing_keys "$SCRIPT_DIR/.env.example" "$P/.env" 0
        [ "$MERGE_ENV_ADDED" -gt 0 ] \
            && echo "  ✓ $MERGE_ENV_ADDED key(s) added from .env.example — fill in values if you use them"
    fi
elif [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$P/.env"
    echo "  ✓ .env scaffolded from .env.example — fill in your credentials"
fi

# ── Create the project virtualenv ──
# The deployed pipeline (and agent-generated code) call a bare `python3`. Rather
# than depend on the launch machine's ambient interpreter (Apple ships an EOL
# 3.9 as /usr/bin/python3; Linux varies), every project gets its own `.venv`
# that the runtimes activate at launch (see the launch instructions printed at
# the end + the "Python environment" note in the runtime doc). `.venv/` is
# gitignored (templates/gitignore_project) so it is never committed/published.
# A pinned 3.12 keeps the interpreter reproducible across macOS and Linux; fall
# back to uv's ambient pick, then to a bare venv, so a machine that can't fetch a
# managed CPython still gets *a* venv. All dep installs below target it via
# `uv pip install --python "$P/.venv"`.
if [ "$LOCAL" = "0" ]; then
    # `--clear` on the retries makes them idempotent: if a first attempt dies
    # after creating the dir (interrupted download, disk full), a bare `uv venv`
    # would otherwise error "already exists". Safe here — this is a fresh clone
    # with no pre-existing venv to preserve.
    uv venv --python 3.12 "$P/.venv" 2>/dev/null \
        || uv venv --python 3.12 --clear "$P/.venv" 2>/dev/null \
        || uv venv --clear "$P/.venv" 2>/dev/null \
        || { rm -rf "$P/.venv"; echo "  ⚠ could not create $P/.venv — create it manually (uv venv $P/.venv) before launching"; }
fi

# ── Install core Python deps ──
# Dep list is single-sourced in templates/deps/core.txt (also read by update.sh).
# Guard on venv existence so a failed venv creation above yields a single warning
# (the "could not create" one) rather than also a doomed install attempt.
if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
    uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/templates/deps/core.txt" -q 2>/dev/null \
        || echo "Note: core deps failed; install manually: source $P/.venv/bin/activate && uv pip install sympy matplotlib certifi"
fi

# ── Install the stdin-safe dotenv guard into the venv ──
# Bare load_dotenv() asserts inside python-dotenv's find_dotenv() when python
# runs from stdin (`python - <<'PY'` heredocs — the natural shape of
# agent-written ad-hoc checks); the guard wraps it to fall back to a cwd
# search. Installed as module + .pth (activated by site at every interpreter
# start) rather than sitecustomize.py, which Homebrew's stdlib copy shadows —
# see templates/utils/pipeline_dotenv_guard.py for the mechanism. Lives inside
# the gitignored .venv, so it is intentionally NOT in the deployment manifest —
# update.sh refreshes it as a dedicated step (like the .env merge).
if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
    _venv_sp="$("$P/.venv/bin/python3" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])' 2>/dev/null)"
    if [ -n "$_venv_sp" ] && [ -d "$_venv_sp" ]; then
        cp "$TEMPLATE_ROOT/templates/utils/pipeline_dotenv_guard.py" "$_venv_sp/_pipeline_dotenv_guard.py"
        printf 'import _pipeline_dotenv_guard\n' > "$_venv_sp/_pipeline_dotenv_guard.pth"
    else
        echo "  ⚠ could not locate venv site-packages — dotenv stdin guard not installed"
    fi
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

# Copy the codex subagent launcher. codex's built-in spawn_agent (v0.144.1)
# cannot select a role from .codex/agents/*.toml nor set per-agent model/effort,
# and defaults to inheriting the caller's full context — so the codex
# orchestrator launches agents via this wrapper instead (see
# templates/runtime/codex/session.md and CLAUDE.md's "codex tier" note). Harmless
# on the claude/gemini runtimes, which use native subagents.
mkdir -p "$P/code/utils/agent_launcher"
cp "$TEMPLATE_ROOT/templates/utils/agent_launcher/launch_agent.sh" "$P/code/utils/agent_launcher/"
chmod +x "$P/code/utils/agent_launcher/launch_agent.sh"

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

# NBER conference agenda skill (loaded by literature-scout, gap-scout — the
# pre-publication research frontier: who is presenting what, right now).
# Variant-gated (issue #205): economics conferences are dead weight for
# llm_cognition, whose frontier bullets point at arXiv/OpenReview instead.
if variant_wants_skill nber_agenda; then
    assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/nber_agenda" \
        "$SKILLS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
        --metadata "$TEMPLATE_ROOT/templates/skill_metadata/nber_agenda_skills.json" \
        --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/nber_agenda" \
        --output-dir "$CODEX_SKILLS_OUT"

    # Copy NBER agenda utility script
    mkdir -p "$P/code/utils/nber_agenda"
    cp "$TEMPLATE_ROOT/templates/utils/nber_agenda/"nber_agenda.py "$P/code/utils/nber_agenda/"
    chmod +x "$P/code/utils/nber_agenda/"nber_agenda.py
fi

# Copy the sandbox-safe git-push credential setup (repo-scoped PAT store; the
# grok sandbox cannot reach the macOS keychain — issue #190). Opt-in: the user
# runs it once per project if they want `git push` to work under grok.
cp "$TEMPLATE_ROOT/templates/utils/setup_push_token.sh" "$P/code/utils/"
chmod +x "$P/code/utils/setup_push_token.sh"

# Copy the codex CLI preflight (proxy-auth version-floor warning, issue #213).
# Sourced by launch.sh's codex branch and codex_math/codex_common.sh.
cp "$TEMPLATE_ROOT/templates/utils/codex_preflight.sh" "$P/code/utils/"

# ── Launch-time model heal ──
# The build-time model remap (resolve_model_fallbacks.py + apply_model_remap.py)
# runs ONCE and cannot reach an already-deployed project. Deploy a runtime twin so
# `./launch.sh claude` re-decides each agent's tier at every launch, in both
# directions: restore the ideal when it recovers, fall back again when it is down.
# config.json records each agent's IDEAL model (the deployed *.md only carries the
# current, possibly-remapped pin, so the ideal must be captured here from the same
# metadata). Emitted with --light-model when --light collapsed subagents to sonnet,
# so the healer restores to the model the assembler actually wrote.
mkdir -p "$P/code/utils/model_heal"
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
    assemble_claude_skills \
        "$TEMPLATE_ROOT" \
        "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json" \
        "$TEMPLATE_ROOT/templates/skill_bodies/ssj" \
        "$SKILLS_OUT"

    python3 "$TEMPLATE_ROOT/scripts/assemble_codex_skills.py" \
        --metadata "$TEMPLATE_ROOT/templates/skill_metadata/ssj_skills.json" \
        --bodies-dir "$TEMPLATE_ROOT/templates/skill_bodies/ssj" \
        --output-dir "$CODEX_SKILLS_OUT"

    # Copy SSJ driver + worked finance example model
    mkdir -p "$P/code/utils/ssj"
    cp "$TEMPLATE_ROOT/templates/utils/ssj/"ssj_solve.py "$TEMPLATE_ROOT/templates/utils/ssj/"example_asset_pricing.py "$P/code/utils/ssj/"
    chmod +x "$P/code/utils/ssj/"ssj_solve.py

    # Install sequence-jacobian (non-fatal -- pulls in numba, which can be finicky to
    # build; warn like the codex CLI rather than failing setup). The package declares
    # no deps, so an unpinned install backtracks to a Python-incompatible numba -- pin
    # numpy/scipy/numba>=0.59 explicitly.
    if [ "$LOCAL" = "0" ] && [ -d "$P/.venv" ]; then
        uv pip install --python "$P/.venv" -r "$TEMPLATE_ROOT/templates/deps/ssj.txt" -q 2>/dev/null \
            || echo "  ⚠ sequence-jacobian install failed (likely a numba build issue). The ssj skill will not work until you run: source $P/.venv/bin/activate && uv pip install sequence-jacobian numpy scipy 'numba>=0.59'"
    fi
fi

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
                "$LIGHT_MODEL" \
                "$TEMPLATE_ROOT/templates/agents/${AGENT_DIR}/vocab.json"

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
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
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
            _tllm_developing_agents=()
            while IFS= read -r _line; do _tllm_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_developing_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_faithful_into_agents "${_tllm_developing_agents[@]}"

            _tllm_bash_agents=()
            while IFS= read -r _line; do _tllm_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/theory_llm/agent_metadata/agents.json")
            if [ "${#_tllm_bash_agents[@]}" -eq 0 ]; then
                echo "Error: theory_llm Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_bash_background_into_agents "${_tllm_bash_agents[@]}"

            # Efficiency mandate (issue #74): experiment-designer runs the LLM
            # experiments, where the "cost" dimension of the mandate bites hardest.
            _tllm_heavy_agents=(experiment-designer)
            inject_efficiency_into_agents "${_tllm_heavy_agents[@]}"

            # Core-bypass guard: the LLM API is a binding source for both the
            # designer (runs experiments) and the reviewer (re-checks them).
            # polish-experiments included: its reproducibility spot-check re-runs
            # an experiment slice against the LLM backend — a backend outage must
            # not be misread as "nothing to verify, pass."
            inject_core_bypass_into_agents experiment-designer experiment-reviewer polish-experiments

            # Report mode: --ext theory_llm is install-only (skills + LLM client).
            # experiment-designer (generative), experiment-reviewer (audit of
            # pipeline-produced experiments), and polish-experiments (audit of
            # pipeline-produced stage3b artifacts) are all pruned — there are no
            # pipeline-produced experiments on an external submission.
            prune_report_mode_agents experiment-designer experiment-reviewer polish-experiments
            if [ "$MODE" = "report" ]; then
                rm -f "$P/docs/stage_3b_experiments.md"
                # Mirror the stage3a cleanup below: the applier creates
                # output/stage3b/figures/ unconditionally, and a report
                # deployment has no stages, so both must go (child first —
                # rmdir only removes empty dirs). core_report.md promises
                # "no output/stage*/"; without this the promise is false.
                rmdir "$P/output/stage3b/figures" 2>/dev/null || true
                rmdir "$P/output/stage3b" 2>/dev/null || true
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
                    sed -i.bak "s|{{DOMAIN_AREAS}}|$DOMAIN_AREAS|g; s|{{PAPER_TYPE}}|$PAPER_TYPE|g; s|{{TARGET_JOURNALS}}|$TARGET_JOURNALS|g; s|{{INITIAL_TIER}}|$INITIAL_TIER|g; s|{{TIER_LADDER_PROSE}}|$TIER_LADDER_PROSE|g; s|{{TIER_LIST_INLINE}}|$TIER_LIST_INLINE|g; s|{{TIER_DOWNGRADE_EXAMPLES}}|$TIER_DOWNGRADE_EXAMPLES|g; s|{{MECHANISM_QUALIFIER_AN}}|$MECHANISM_QUALIFIER_AN|g; s|{{MECHANISM_QUALIFIER}}|$MECHANISM_QUALIFIER|g; s|{{MECHANISM_DISCIPLINE}}|$MECHANISM_DISCIPLINE|g; s|{{PRINCIPLED_MECHANISM_PHRASE}}|$PRINCIPLED_MECHANISM_PHRASE|g" "$P/docs/$_name" && rm "$P/docs/${_name}.bak"
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
                "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" "$GROK_AGENTS_OUT/scorer.md" \
                "$TEMPLATE_ROOT/extensions/empirical/state_loop_fields_inject.md" <<'PYEOF'
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
# Four scorer files, not three — Grok is the fourth runtime (.grok/agents/scorer.md).
# These slices are hand-indexed against the argv list above; when you add a call
# site, re-count BOTH the slice end and every index after it. Getting this wrong is
# silent: an off-by-one previously made `state_loop` read the grok scorer body and
# splice that whole agent prompt into the deployed runtime docs.
scorer_files = sys.argv[11:15]
state_loop = open(sys.argv[15]).read()

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
        ("{{EMPIRICAL_LOOP_FIELDS}}", state_loop),
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
    # Two empirical version-pointer fields, inserted after stage2b_theory_version to
    # preserve key order. Null/no-op in theory-first --ext empirical runs.
    if "stage3a_theory_version" not in data:
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage2b_theory_version":
                new["stage3a_theory_version"] = None
        data = new
    if "stage2_mechanism_version" not in data:
        new = {}
        for k, v in data.items():
            new[k] = v
            if k == "stage3a_theory_version":
                new["stage2_mechanism_version"] = None
        data = new
    # Empirical audit loops: merge into the generic `loops` object (see CLAUDE.md
    # "Audit-loop scoping" rule + Loop Registry). setdefault is idempotent across
    # re-runs / update refreshes and needs no hand-anchored key order — the whole point
    # of the loops:{} restructure (issue #166): a new empirical gate is added here in one
    # line and is loop-capped everywhere for free.
    emp_loops = {
        "identification_plan_revision": {"round": 0, "cap": 3},
        "headline_replication":         {"round": 0, "cap": 3},
        "replicator_self_refire":       {"round": 0, "cap": 3},
        "data_integrity":               {"round": 0, "cap": 3},
        "method_check":                 {"round": 0, "cap": 3},
        "claim_grounding":              {"round": 0, "cap": 3},
        "paper_writer_pse":             {"round": 0, "cap": 3},
        "claim_format_reexport":        {"round": 0, "cap": 2},
    }
    data.setdefault("loops", {})
    for _lid, _cfg in emp_loops.items():
        data["loops"].setdefault(_lid, dict(_cfg))
    with open(state_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
PYEOF

            # Empirical extension developing agents — from metadata.
            # Variant-aware via $AGENT_DIR (finance metadata adds identification-designer;
            # macro currently has empiricist only). The metadata is the source of truth.
            _empirical_developing_agents=()
            while IFS= read -r _line; do _empirical_developing_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --category developing \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_developing_agents[@]}" -eq 0 ]; then
                echo "Error: empirical developing-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_faithful_into_agents "${_empirical_developing_agents[@]}"

            _empirical_bash_agents=()
            while IFS= read -r _line; do _empirical_bash_agents+=("$_line"); done < <(python3 "$TEMPLATE_ROOT/scripts/list_agents_by_category.py" \
                --has-tool Bash \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/shared_agents.json" \
                --metadata "$TEMPLATE_ROOT/extensions/empirical/agent_metadata/${AGENT_DIR}_agents.json")
            if [ "${#_empirical_bash_agents[@]}" -eq 0 ]; then
                echo "Error: empirical Bash-agent list is empty (lister failed or metadata missing)" >&2
                exit 1
            fi
            inject_bash_background_into_agents "${_empirical_bash_agents[@]}"

            # Efficiency mandate (issue #74): the empirical agents that load/run
            # large tables — the source of every documented OOM. method-checker is
            # excluded (it reads code, doesn't run analyses); claim-enumerator/
            # claim-verifier do lightweight regex/file checks, not data analysis.
            _empirical_heavy_agents=(empiricist empirics-auditor headline-replicator data-integrity-auditor data-selection-auditor)
            inject_efficiency_into_agents "${_empirical_heavy_agents[@]}"

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
                mechanism-auditor \
                headline-replicator \
                claim-enumerator claim-grounder claim-verifier
            # mechanism-auditor is meaningful only under --mode empirical-first
            # (it audits the prose+DAG mechanism that only that mode produces).
            # Assembled with the empirical agents above; removed in every other
            # mode (theory-first, macro, report — report is already covered by
            # the report prune list above, but the non-empirical-first prune is
            # the canonical guard).
            prune_non_empirical_first_agents mechanism-auditor
            # Empirical extension also creates output/stage3a/ unconditionally
            # and copies stage_3a_empirical.md into docs/. Both are pipeline-
            # workflow artifacts irrelevant to report mode — remove them.
            if [ "$MODE" = "report" ]; then
                # Remove the figures/ child before the parent: the extension
                # applier creates output/stage3a/figures/, so a bare rmdir on
                # the parent fails (non-empty) and silently leaves the whole
                # tree behind, contradicting core_report.md's "no output/stage*/"
                # invariant. Both stay rmdir (not rm -rf) on purpose — they must
                # only vanish when empty, which at setup time they always are.
                rmdir "$P/output/stage3a/figures" 2>/dev/null || true
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
    "$AGENTS_OUT/scorer.md" "$CODEX_AGENTS_OUT/scorer.toml" "$GEMINI_AGENTS_OUT/scorer.md" "$GROK_AGENTS_OUT/scorer.md" <<'PYEOF'
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
    # {{EMPIRICAL_LOOP_FIELDS}} is inline (appended to the last base loops entry inside
    # the loops object), so LINE_PAT does not catch it. Strip it inline when empirical is
    # off; when empirical is on the injector already replaced it, so this is a no-op.
    new = new.replace("{{EMPIRICAL_LOOP_FIELDS}}", "")
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
python3 - "$EMPIRICAL_ENABLED" "$AGENTS_OUT/branch-manager.md" "$CODEX_AGENTS_OUT/branch-manager.toml" "$GEMINI_AGENTS_OUT/branch-manager.md" "$GROK_AGENTS_OUT/branch-manager.md" <<'PYEOF'
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
python3 - "$MODE" "$EXT_EMPIRICAL_ON" "$VARIANT" "$P/docs/"*.md "$CLAUDE_MD_OUT" "$AGENTS_MD_OUT" "$GEMINI_MD_OUT" \
    "$AGENTS_OUT"/*.md "$CODEX_AGENTS_OUT"/*.toml "$GEMINI_AGENTS_OUT"/*.md "$GROK_AGENTS_OUT"/*.md <<'PYEOF'
import os, re, sys
mode = sys.argv[1]  # "", "empirical-first", "measurement-first", "report"
xe = sys.argv[2] == "1"
variant = sys.argv[3].upper()

def keep(name):
    """Marker-family semantics per mode. THEORY_FIRST = any theory-shaped
    pipeline (the no-mode default AND measurement-first, whose output is still
    a theory paper produced evidence-first). NO_MODE = strictly the modeless
    default — use it for THEORY_FIRST sites whose content a mode-specific
    block replaces (a site carrying both a NO_MODE and a MEASUREMENT_FIRST
    block renders exactly one of them in every mode). Report mode copies no
    stage docs and prunes the marker-carrying generative agents, so it takes
    the default branch."""
    if mode == "empirical-first":
        return name == "EMPIRICAL_FIRST"
    if mode == "measurement-first":
        return name in ("THEORY_FIRST", "MEASUREMENT_FIRST")
    return name in ("THEORY_FIRST", "NO_MODE")

patterns = []  # list of (regex, replacement) applied in order
# Trailing \n after END markers is optional so a marker at EOF (no final
# newline) still matches; otherwise the literal HTML comment leaks into the
# deployed file.
# ORDER MATTERS: every block REMOVAL runs before any marker STRIP. The removal
# pattern eats up to 2 trailing newlines (to collapse the blank line a removed
# block would otherwise leave behind). If a neighbouring block's markers were
# already stripped, that removal sees the neighbour's exposed leading blank line
# and eats it too — silently deleting a blank line from the kept content. That
# is invisible in single-block files and only shows up once two mode blocks sit
# adjacent at the same site (e.g. NO_MODE + MEASUREMENT_FIRST before an
# EMPIRICAL_FIRST twin). Doing all removals first makes the result independent
# of family order, so adding a mode block at an existing site cannot perturb the
# other modes' output.
_families = ("THEORY_FIRST", "EMPIRICAL_FIRST", "MEASUREMENT_FIRST", "NO_MODE")
for fam in _families:
    if not keep(fam):
        patterns.append((re.compile(r"<!-- " + fam + r"_START -->\n.*?<!-- " + fam + r"_END -->\n{0,2}", re.DOTALL), ""))
for fam in _families:
    if keep(fam):
        patterns.append((re.compile(r"<!-- " + fam + r"_(?:START|END) -->\n?"), ""))
if xe:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_(?:START|END) -->\n?"), ""))
else:
    patterns.append((re.compile(r"<!-- EXT_EMPIRICAL_START -->\n.*?<!-- EXT_EMPIRICAL_END -->\n{0,2}", re.DOTALL), ""))
# Variant markers: <!-- VARIANT_{NAME}_START/END --> blocks are kept (markers
# stripped) when {NAME} matches the deploying variant (uppercased) and removed
# wholesale otherwise. Generic — a new variant needs no resolver edit. The
# matching-variant unwrap runs first so the wholesale pattern (backreference-
# paired, so mismatched START/END names never span) only sees foreign blocks.
# CAUTION: never INTERLEAVE two differently-named marker blocks
# (A_START … B_START … A_END … B_END) — the non-greedy wholesale removal
# would swallow the embedded B_START and leak an orphaned B_END into the
# deployed file. Nesting (B fully inside A) and siblings are both fine.
# The same fragility exists in the mode-marker patterns above.
patterns.append((re.compile(r"<!-- VARIANT_" + re.escape(variant) + r"_(?:START|END) -->\n?"), ""))
patterns.append((re.compile(r"<!-- VARIANT_([A-Z0-9_]+)_START -->\n.*?<!-- VARIANT_\1_END -->\n{0,2}", re.DOTALL), ""))
for p in sys.argv[4:]:
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

# ── Apply model-availability remap to assembled Claude agents ──
# Single post-assembly pass (after base + variant + every extension agent exists):
# rewrite the `model:` frontmatter for any model the probe found unavailable,
# repointing it to the resolved fallback. Claude agents dir only — see the
# "Resolve unavailable Claude subagent models" block above for rationale.
if [ ${#MODEL_REMAP_ARGS[@]} -gt 0 ]; then
    python3 "$TEMPLATE_ROOT/scripts/apply_model_remap.py" --dir "$AGENTS_OUT" "${MODEL_REMAP_ARGS[@]}"
    echo "  ✓ Subagent model remap applied to $AGENTS_OUT"
fi

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
    ".grok/agents",
    "docs",
    "code/utils/codex_math",
    "code/utils/agent_launcher",
    "code/utils/bib_verify",
    "code/utils/openalex",
    "code/utils/nber_agenda",
    "code/utils/model_heal",
    "code/utils/ssj",
    # NOTE: the project .venv is intentionally NOT listed here. It is generated
    # per-host by uv (not a copied template artifact), and manifest paths get
    # nuke-and-copied by update.sh -- which would wipe user-installed packages
    # and break the venv's baked-in absolute interpreter paths. update.sh instead
    # bootstraps a missing venv from the single-sourced deps files (see its
    # venv-bootstrap block), so refreshing an older deploy still gets a venv.
]
candidate_files = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "launch.sh",
    "docs/start_session_claude.md",
    "docs/start_session_codex.md",
    "docs/start_session_gemini.md",
    ".claude/settings.json",
    ".gemini/settings.json",
    ".grok/sandbox.toml",
    ".gitignore",
    "dashboard.html",
    "code/utils/setup_push_token.sh",
    "code/utils/codex_preflight.sh",
]

# Extension-installed files. The empirical extension drops *.py / *.sh
# directly into code/utils/ (flat, alongside the codex_math/bib_verify/
# openalex/nber_agenda subdirs that core setup creates). The theory_llm extension
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
        # dict.fromkeys: order-preserving dedupe — a file can be registered both
        # statically and by an extension's code/utils glob (e.g. setup_push_token.sh
        # under --ext empirical); update.sh should see each entry once.
        "dirs_replace": [d for d in dict.fromkeys(candidate_dirs) if (project / d).is_dir()],
        "files_replace": [f for f in dict.fromkeys(candidate_files) if (project / f).is_file()],
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
    # The rendered fingerprint .sty is a sed-substitution target too
    # ({{ARP_UUID}}/{{ARP_VERSION}}/{{ARP_DATE}}/{{ARP_MODE}}/{{ARP_PROVENANCE}});
    # absent in report mode, where no paper skeleton is installed.
    STY_OUT="$P/paper/arpipeline.sty"
    STY_REMAINING=0
    if [ -f "$STY_OUT" ]; then
        STY_REMAINING=$(grep -c '{{' "$STY_OUT" 2>/dev/null || true)
        STY_REMAINING="${STY_REMAINING:-0}"
        echo "=== Rendered paper/arpipeline.sty ==="
        echo "Placeholders remaining: $STY_REMAINING"
        echo ""
    fi
    echo "=== Agents ($CLAUDE_AGENTS_REL/) ==="
    ls -1 "$AGENTS_OUT/"
    echo ""
    echo "=== Codex Agents ($CODEX_AGENTS_REL/) ==="
    ls -1 "$CODEX_AGENTS_OUT/"
    echo ""
    echo "=== Gemini Agents ($GEMINI_AGENTS_REL/) ==="
    ls -1 "$GEMINI_AGENTS_OUT/"
    echo ""
    echo "=== Grok Agents ($GROK_AGENTS_REL/) ==="
    ls -1 "$GROK_AGENTS_OUT/"
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
    elif [ "$STY_REMAINING" -gt 0 ]; then
        echo "WARNING: $STY_REMAINING unresolved placeholders in paper/arpipeline.sty:"
        grep '{{' "$STY_OUT"
        exit 1
    else
        echo "✓ All placeholders resolved"
    fi
    echo ""
    echo "Output at: $OUT_DIR/"
    rm -f "$TIER_VOCAB_FILE"
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
rm -rf scorer_floor_test/   # build-time scorer-calibration harness (#102); never ships
rm -f setup.sh
rm -f README.md
rm -f CLAUDE_REFACTOR_PLAN.md
rm -f requirements.system
rm -f texput.log
rm -f LIMITATIONS.md   # meta-project architectural-limits doc; dev-facing, never ships
rm -f VERSION CHANGELOG.md   # build-time version stamp + template changelog; read at setup, never ships
# Meta-repo dev skills snapshotted right after the clone (see the DEV_SKILLS block there).
# Dev-facing template tooling — a research project has no use for instructions on how to
# deploy or edit the template. The project's own skills were assembled separately and are
# not in this list, so they survive.
if [ ${#DEV_SKILLS[@]} -gt 0 ]; then
    dev_skill_i=0
    dev_skill_removed=0
    for d in "${DEV_SKILLS[@]}"; do
        dev_skill_want="${DEV_SKILL_SUMS[$dev_skill_i]}"
        dev_skill_i=$((dev_skill_i + 1))
        dev_skill_now=""
        [ -f "$d/SKILL.md" ] && dev_skill_now="$(cksum < "$d/SKILL.md")"
        if [ "$dev_skill_now" = "$dev_skill_want" ]; then
            rm -rf "$d"
            dev_skill_removed=$((dev_skill_removed + 1))
        else
            # Contents changed since the snapshot: an assembled project skill now owns
            # this directory. Keep it — deleting it would drop a real skill from the
            # deployed project. The dev content is already gone (overwritten), so
            # nothing leaks; only the name needs fixing upstream.
            echo "  ⚠ $d was overwritten by an assembled project skill — keeping it."
            echo "    A skill_id in templates/skill_metadata/ collides with a meta-repo"
            echo "    dev-skill directory name. Rename one so they cannot share a path."
        fi
    done
    echo "  ✓ Meta-repo dev skills removed ($dev_skill_removed/${#DEV_SKILLS[@]})"
fi
if [ "$MANUAL" = "1" ] || [ "$MODE" = "report" ]; then
    rm -f dashboard.html
elif [ -f dashboard.html ]; then
    # Variant-correct subtitle (mirrors the --local branch; production gets
    # dashboard.html via the clone, so it must be re-titled here too — the
    # title-cased PAPER_TYPE renders the historical "Autonomous Finance Theory
    # Paper Generator" byte-identically for finance).
    DASHBOARD_SUBTITLE="Autonomous $(python3 -c "import sys; print(sys.argv[1].title())" "$PAPER_TYPE") Generator"
    sed -i.bak "s|Autonomous Finance Theory Paper Generator|$DASHBOARD_SUBTITLE|" dashboard.html && rm -f dashboard.html.bak
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
echo "  # Activate the project venv first so the pipeline's python3 finds its deps:"
echo "  source .venv/bin/activate"
echo ""
echo "Preferred: ./launch.sh <claude|codex|gemini|grok>   (activates the venv and applies each runtime's flags)"
echo ""
echo "Claude:"
echo "  source .venv/bin/activate && claude --dangerously-skip-permissions"
echo ""
echo "Codex (headless driver loop — codex has no autowake, so this is the autonomous form):"
echo "  ./launch.sh codex          # add --tmux for a detached window; --once for a plain TUI"
echo ""
echo "Gemini:"
echo "  source .venv/bin/activate && gemini --yolo"
echo ""
echo "Grok (reads the shared AGENTS.md; agents in .grok/agents/):"
echo "  ./launch.sh grok           # per-project leader socket + venv python shims applied automatically"
echo "  # Manual equivalent (run from the project root — the per-project --leader-socket is required"
echo "  # when you run more than one grok project on this host: all grok clients share"
echo "  # ~/.grok/leader.sock by default, and a second client on that socket TEARS DOWN the"
echo "  # first session's in-flight turn):"
echo "  source .venv/bin/activate && grok --sandbox pipeline --always-approve --leader-socket \"\$(pwd)/.grok/leader.sock\""
echo "  # grok demotes the venv in its bash PATH (bare python3 = system python) — ./launch.sh grok"
echo "  # installs transparent VIRTUAL_ENV shims in ~/.local/bin to fix this; manual launches need them too."
echo "  # git push under grok's sandbox cannot use the macOS keychain; to enable pushes:"
echo "  #   bash code/utils/setup_push_token.sh   (repo-scoped fine-grained PAT; otherwise commits stay local)"
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
    echo "Mode: light (all subagents drop to the cheapest tier: claude sonnet, codex gpt-5.6-luna, gemini flash; per-agent effort dropped)"
fi
if [ "$FAITHFUL" = "1" ]; then
    echo "Mode: faithful (the seed is a contract; the pipeline implements it as written)"
    echo "Drop your idea files in output/seed/ before launching"
    echo "Pipeline will extract a mechanism contract first, then triage entry-stage"
elif [ "$SEEDED" = "1" ]; then
    echo "Seeded: drop your idea files in output/seed/ before launching"
    echo "Pipeline will triage seed maturity and enter at the appropriate stage"
fi
echo "Sandbox is pre-configured for Claude ($CLAUDE_SETTINGS_REL) and Grok ($GROK_SANDBOX_REL)"
echo "(writes/deletes restricted to the project folder + caches, web access works freely)"
rm -f "$TIER_VOCAB_FILE"
