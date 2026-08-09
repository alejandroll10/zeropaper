# setup.sh configuration resolution.
#
# This module is sourced by the root coordinator before any deployment work.
# Its public interface is:
#
#   resolve_setup_config "$@"
#       Parse and validate the CLI, resolve variant/mode/extension composition,
#       and populate the configuration globals consumed by setup.sh.
#
#   variant_wants_skill <skill-id>
#       Return whether the resolved variant should install a gated core skill.
#
#   reject_unknown_extension <extension-id>
#       Emit the historical unknown-extension diagnostic and terminate.  The
#       coordinator calls this at the extension-application boundary so error
#       ordering remains byte-for-byte compatible with pre-extraction setup.sh.
#
# Keep every internal helper/temporary prefixed with _setup_config_.  Resolved
# variables intentionally remain globals: setup.sh is the sole consumer and
# sourcing avoids a serialization layer that could corrupt multiline domain
# descriptors or ordered Bash arrays.

usage() {
    cat <<'EOF'
Usage: ./setup.sh [project-name] [options]

Create a standalone research-project deployment. Deployments stay local by
default; pass --publish explicitly to create and push a GitHub repository.

Core options:
  --variant finance|macro|llm_cognition
  --ext empirical|theory_llm             Repeatable
  --mode empirical-first|measurement-first|report
  --seed | --faithful | --manual
  --light
  --halt-on-core-bypass
  --no-model-probe
  --publish                               Create and push a GitHub repository
  --no-publish                            Explicit local-only mode (default)
  --local                                 Assembly debug mode; never publishes
  -h, --help

Publishing environment:
  PUBLISH_ORG=<org>                       Target org (default: automated-papers-produced)
  PUBLISH_VISIBILITY=private|public|internal
                                          Repository visibility (default: private)

--publish is disabled for --mode report because submissions may be confidential.
EOF
}

_setup_config_extension_enabled() {
    [[ " ${EXTENSIONS[*]} " =~ " $1 " ]]
}

_setup_config_add_extension() {
    _setup_config_extension_enabled "$1" || EXTENSIONS+=("$1")
}

_setup_config_parse_arguments() {
    PROJECT_NAME=""
    VARIANT="finance"
    MODE=""
    LOCAL=0
    SEEDED=0
    USER_PASSED_SEED=0
    FAITHFUL=0
    MANUAL=0
    LIGHT=0
    HALT_ON_CORE_BYPASS=0
    MODEL_PROBE=1
    PUBLISH=0
    USER_PASSED_PUBLISH=0
    USER_PASSED_NO_PUBLISH=0
    PUBLISH_ORG="${PUBLISH_ORG-automated-papers-produced}"
    PUBLISH_VISIBILITY="${PUBLISH_VISIBILITY-private}"
    EXTENSIONS=()

    local _setup_config_next_is_variant=0
    local _setup_config_next_is_ext=0
    local _setup_config_next_is_mode=0
    local _setup_config_arg
    for _setup_config_arg in "$@"; do
        case "$_setup_config_arg" in
            --variant)     _setup_config_next_is_variant=1 ;;
            --ext)         _setup_config_next_is_ext=1 ;;
            --mode)        _setup_config_next_is_mode=1 ;;
            --seed)        SEEDED=1; USER_PASSED_SEED=1 ;;
            --faithful)    FAITHFUL=1; SEEDED=1 ;;
            --manual)      MANUAL=1 ;;
            --light)       LIGHT=1 ;;
            --halt-on-core-bypass) HALT_ON_CORE_BYPASS=1 ;;
            --no-model-probe) MODEL_PROBE=0 ;;
            --publish)     PUBLISH=1; USER_PASSED_PUBLISH=1 ;;
            --no-publish)  PUBLISH=0; USER_PASSED_NO_PUBLISH=1 ;;
            --local)       LOCAL=1 ;;
            -h|--help)     usage; exit 0 ;;
            --theory-llm)  _setup_config_add_extension theory_llm ;;
            -*)            echo "Unknown option: $_setup_config_arg"; exit 1 ;;
            *)
                if [ "$_setup_config_next_is_variant" = "1" ]; then
                    VARIANT="$_setup_config_arg"
                    _setup_config_next_is_variant=0
                elif [ "$_setup_config_next_is_ext" = "1" ]; then
                    EXTENSIONS+=("$_setup_config_arg")
                    _setup_config_next_is_ext=0
                elif [ "$_setup_config_next_is_mode" = "1" ]; then
                    MODE="$_setup_config_arg"
                    _setup_config_next_is_mode=0
                else
                    PROJECT_NAME="$_setup_config_arg"
                fi
                ;;
        esac
    done

    if [ "$_setup_config_next_is_variant" = "1" ]; then
        echo "Error: --variant requires a value (finance, macro, llm_cognition)"
        exit 1
    fi
    if [ "$_setup_config_next_is_ext" = "1" ]; then
        echo "Error: --ext requires a value (empirical, theory_llm)"
        exit 1
    fi
    if [ "$_setup_config_next_is_mode" = "1" ]; then
        echo "Error: --mode requires a value (empirical-first, measurement-first, report)"
        exit 1
    fi
}

_setup_config_validate_flag_composition() {
    if [ "$USER_PASSED_PUBLISH" = "1" ] && [ "$USER_PASSED_NO_PUBLISH" = "1" ]; then
        echo "Error: --publish and --no-publish are mutually exclusive."
        exit 1
    fi
    if [ "$PUBLISH" = "1" ] && [ "$LOCAL" = "1" ]; then
        echo "Error: --publish cannot be used with --local."
        echo "  --local is assembly-only debug mode and never creates a deployable repository."
        exit 1
    fi
    if [ "$PUBLISH" = "1" ] && [ "$MODE" = "report" ]; then
        echo "Error: --publish cannot be used with --mode report."
        echo "  Report deployments may contain confidential submissions and are kept local; push manually only after review."
        exit 1
    fi
    if [ "$PUBLISH" = "1" ] && [ -z "$PUBLISH_ORG" ]; then
        echo "Error: --publish requires a non-empty PUBLISH_ORG."
        echo "  Omit PUBLISH_ORG to use automated-papers-produced, or set PUBLISH_ORG=<org>."
        exit 1
    fi
    if [ "$PUBLISH" = "1" ]; then
        case "$PUBLISH_VISIBILITY" in
            private|public|internal) ;;
            *)
                echo "Error: PUBLISH_VISIBILITY must be private, public, or internal."
                exit 1
                ;;
        esac
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

    # --faithful sets SEEDED itself.  USER_PASSED_SEED distinguishes that from
    # an explicit --seed + --faithful collision, which remains a hard error.
    if [ "$FAITHFUL" = "1" ] && [ "$USER_PASSED_SEED" = "1" ]; then
        echo "Error: --seed and --faithful are mutually exclusive — pass one, not both."
        echo "  --faithful is a stricter variant of --seed (it already creates output/seed/ and starts at seed_triage)."
        exit 1
    fi
}

_setup_config_resolve_variant_and_modes() {
    # Legacy spelling changes the variant and contributes an extension without
    # disturbing extension order.
    if [ "$VARIANT" = "finance_llm" ]; then
        VARIANT="finance"
        _setup_config_add_extension theory_llm
    fi

    # LLM-cognition's evidence is produced by theory_llm experiments.  A report
    # build generates no evidence and prunes those agents, so it is the one
    # variant/mode composition where the extension is not implied.
    if [ "$VARIANT" = "llm_cognition" ] && [ "$MODE" != "report" ] \
        && ! _setup_config_extension_enabled theory_llm; then
        EXTENSIONS+=("theory_llm")
        echo "Info: --variant llm_cognition implies --ext theory_llm (auto-added)."
    fi

    # Modes are orthogonal to variants and explicit extensions, but may constrain
    # supported variants or imply the extension required to make the route
    # coherent (empirical-first → empirical).
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
                if ! _setup_config_extension_enabled empirical; then
                    EXTENSIONS+=("empirical")
                    echo "Info: --mode empirical-first implies --ext empirical (auto-added)."
                fi
                ;;
            measurement-first)
                if [ "$VARIANT" != "llm_cognition" ]; then
                    echo "Error: --mode measurement-first is llm_cognition-only."
                    echo "  The econ variants' evidence-first shape is --mode empirical-first"
                    echo "  (finance); measurement-first is built on the theory_llm experiment"
                    echo "  stage, which only llm_cognition deploys by default."
                    exit 1
                fi
                ;;
            report)
                case "$VARIANT" in
                    finance|macro|llm_cognition) : ;;
                    *)
                        echo "Error: --mode report supports --variant finance, macro, or llm_cognition."
                        echo "  A new variant needs a deploy_assets/templates/agents/{variant}_modes/report/vocab.json"
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

    # Collapse duplicates after every explicit, legacy, and implied add site.
    # Preserve first occurrence: extension application order is characterized.
    if [ "${#EXTENSIONS[@]}" -gt 0 ]; then
        local _setup_config_seen_ext=" "
        local -a _setup_config_deduped_ext=()
        local _setup_config_ext
        for _setup_config_ext in "${EXTENSIONS[@]}"; do
            if [[ "$_setup_config_seen_ext" != *" $_setup_config_ext "* ]]; then
                _setup_config_deduped_ext+=("$_setup_config_ext")
                _setup_config_seen_ext+="$_setup_config_ext "
            fi
        done
        EXTENSIONS=("${_setup_config_deduped_ext[@]}")
    fi
}

_setup_config_resolve_variant_descriptors() {
    # These values are the single configuration source consumed by runtime-doc,
    # agent, tier-vocab, dashboard, state, and manifest assembly downstream.
    # Start from the economics defaults on every call so the resolver is
    # re-entrant; llm_cognition overrides all three in its branch below.
    PRINCIPLED_MECHANISM_PHRASE="falls out of economics"
    CHARACTERIZE_EXAMPLE_BULLET="If a result holds under CARA but not CRRA, find the exact condition on preferences that makes it work."
    NUMERICAL_VERIFICATION_BULLET="Don't settle for numerical verification of what should be a theorem."
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

    # Economics-only discovery/tooling skills are dead weight for LLM cognition.
    # update.sh's stale-infrastructure sweep handles removals on refresh.
    VARIANT_SKILL_EXCLUDES=""
    [ "$VARIANT" = "llm_cognition" ] && VARIANT_SKILL_EXCLUDES=" ssj nber_agenda "

    # The empirical extension's per-variant agents exist only for finance/macro;
    # LLM cognition uses theory_llm instead.
    if [ "$VARIANT" = "llm_cognition" ] && _setup_config_extension_enabled empirical; then
        echo "Error: --ext empirical is not supported with --variant llm_cognition."
        echo "  The empirical extension's per-variant agents exist only for finance/macro."
        echo "  For LLM-cognition experiments use --ext theory_llm."
        exit 1
    fi
}

_setup_config_apply_mode_descriptors() {
    # Modes may reframe the produced paper while leaving the base variant's
    # journal ladder intact.  Values here feed runtime docs, agent context, and
    # the dashboard subtitle.
    DOC_SUBTITLE="Autonomous Theory Paper Pipeline"
    if [ "$MODE" = "empirical-first" ]; then
        case "$VARIANT" in
            finance)
                PAPER_TYPE="causal-identification empirical finance paper"
                DOMAIN_AREAS="empirical finance — asset pricing, corporate finance, information economics, market design, financial intermediation, or behavioral finance — with the contribution resting on a credibly-identified causal estimand plus a prose+DAG mechanism"
                DOC_SUBTITLE="Autonomous Empirical Paper Pipeline"
                ;;
        esac
    elif [ "$MODE" = "measurement-first" ]; then
        case "$VARIANT" in
            llm_cognition)
                PAPER_TYPE="measurement-first language-model cognition paper"
                DOMAIN_AREAS="the science of language-model cognition and evaluation, measurement-first — the contribution is a construct made measurable (a formal construct definition plus a task family that operationalizes it) and the experimental evidence it yields in real models; formal characterization follows the measurements rather than preceding them. In scope: capability and behavior measurement, evaluation methodology, probing and interpretability protocols, benchmark design, scaling and context-use measurement."
                DOC_SUBTITLE="Autonomous Measurement Paper Pipeline"
                ;;
        esac
    elif [ "$MODE" = "report" ]; then
        PAPER_TYPE="external paper submission under review"
        DOC_SUBTITLE="Autonomous Referee Report Pipeline"
    fi
}

resolve_setup_config() {
    _setup_config_parse_arguments "$@"
    _setup_config_validate_flag_composition
    _setup_config_resolve_variant_and_modes
    _setup_config_resolve_variant_descriptors
    _setup_config_apply_mode_descriptors
}

variant_wants_skill() {
    case "$VARIANT_SKILL_EXCLUDES" in
        *" $1 "*) return 1 ;;
        *) return 0 ;;
    esac
}

reject_unknown_extension() {
    echo "Unknown extension: $1"
    echo "Available extensions: empirical, theory_llm"
    exit 1
}
