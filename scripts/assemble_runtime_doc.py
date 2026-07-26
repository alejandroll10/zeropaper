#!/usr/bin/env python3
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--paper-type", required=True)
    parser.add_argument("--target-journals", required=True)
    parser.add_argument("--domain-areas", required=True)
    parser.add_argument("--initial-tier", required=True,
                        help="Variant default for target_journal_tier (e.g., 'top-3-fin' for finance, 'top-5' for macro)")
    parser.add_argument("--tier-ladder-prose", required=True,
                        help="Variant tier ladder shown in prose (e.g., 'top-5 → top-3-fin → field → letters')")
    parser.add_argument("--tier-list-inline", required=True,
                        help="Variant tier enum as backtick-wrapped comma list (e.g., '`top-5`, `top-3-fin`, `field`, `letters`')")
    parser.add_argument("--mechanism-qualifier", default=None,
                        help="Variant adjective for the paper's mechanism/content "
                             "('economic' for finance/macro, 'computational' for llm_cognition)")
    parser.add_argument("--mechanism-qualifier-adv", default=None,
                        help="Adverb form of --mechanism-qualifier "
                             "('economically' / 'computationally')")
    parser.add_argument("--deepening-extension-types", default=None,
                        help="Variant menu for the deepening playbook's Extension types line")
    parser.add_argument("--characterize-example-bullet", default=None,
                        help="Domain-specific example bullet for the characterize-don't-just-prove "
                             "core principle (CARA/CRRA for finance/macro, stimulus-distribution "
                             "for llm_cognition)")
    parser.add_argument("--numerical-verification-bullet", default=None,
                        help="Domain-specific phrasing of the numerical-verification-vs-theorem "
                             "core-principle bullet (llm_cognition adds the measurement-as-"
                             "first-class-evidence converse)")
    parser.add_argument("--doc-name", required=True)
    parser.add_argument("--doc-subtitle", required=True,
                        help="H1 subtitle after the runtime doc name (e.g., "
                             "'Autonomous Theory Paper Pipeline' for the default theory-first "
                             "deploy, 'Autonomous Empirical Paper Pipeline' under --mode empirical-first).")
    parser.add_argument("--agent-dir", required=True)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--seed-block", default=None,
                        help="Path to seed override markdown (omit for empty)")
    parser.add_argument("--discipline", default=None,
                        help="Path to runtime discipline markdown (omit for empty)")
    parser.add_argument("--core-bypass-halt", action="store_true",
                        help="Inject the flag-gated halt-on-core-bypass pointer at "
                             "{{CORE_BYPASS_GUARD}}. Default (flag absent) leaves it empty: "
                             "recording is agent-driven via docs/core_bypass.md and does not "
                             "touch the runtime doc.")
    parser.add_argument("--agent-catalog", default=None,
                        help="Path to pre-generated agent catalog markdown (manual mode)")
    parser.add_argument("--skill-catalog", default=None,
                        help="Path to pre-generated skill catalog markdown (manual mode)")
    parser.add_argument("--session-out", default=None,
                        help="If set, write the substituted session guidance to this path "
                             "and replace {{RUNTIME_SESSION_GUIDANCE}} with a one-line pointer "
                             "(reduces runtime doc size).")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = Path(args.core).read_text()
    runtime_session = Path(args.session).read_text().rstrip()

    seed_block = ""
    if args.seed_block:
        seed_block = Path(args.seed_block).read_text().rstrip()

    discipline_block = ""
    if args.discipline:
        discipline_block = Path(args.discipline).read_text().rstrip()

    agent_catalog = ""
    if args.agent_catalog:
        agent_catalog = Path(args.agent_catalog).read_text().rstrip()

    skill_catalog = ""
    if args.skill_catalog:
        skill_catalog = Path(args.skill_catalog).read_text().rstrip()

    content = content.replace("{{RUNTIME_DOC_NAME}}", args.doc_name)
    content = content.replace("{{RUNTIME_DOC_SUBTITLE}}", args.doc_subtitle)
    content = content.replace("{{PAPER_TYPE}}", args.paper_type)
    content = content.replace("{{TARGET_JOURNALS}}", args.target_journals)
    content = content.replace("{{DOMAIN_AREAS}}", args.domain_areas)
    content = content.replace("{{INITIAL_TIER}}", args.initial_tier)
    content = content.replace("{{TIER_LADDER_PROSE}}", args.tier_ladder_prose)
    content = content.replace("{{TIER_LIST_INLINE}}", args.tier_list_inline)
    if args.mechanism_qualifier is not None:
        content = content.replace("{{MECHANISM_QUALIFIER}}", args.mechanism_qualifier)
    if args.mechanism_qualifier_adv is not None:
        content = content.replace("{{MECHANISM_QUALIFIER_ADV}}", args.mechanism_qualifier_adv)
    if args.deepening_extension_types is not None:
        content = content.replace("{{DEEPENING_EXTENSION_TYPES}}", args.deepening_extension_types)
    if args.characterize_example_bullet is not None:
        content = content.replace("{{CHARACTERIZE_EXAMPLE_BULLET}}", args.characterize_example_bullet)
    if args.numerical_verification_bullet is not None:
        content = content.replace("{{NUMERICAL_VERIFICATION_BULLET}}", args.numerical_verification_bullet)
    content = content.replace("{{AGENT_DIR}}", args.agent_dir)
    content = content.replace("{{SKILL_DIR}}", args.skill_dir)
    content = content.replace("{{SEED_OVERRIDE}}", seed_block)
    if args.core_bypass_halt:
        core_bypass_guard = (
            "\n**Core-bypass guard active (`--halt-on-core-bypass`).** Treat a bypassed "
            "core as a hard stop, not a fallback: if a binding source is unreachable, a "
            "verification gate would be skipped or advanced past, a designated agent is "
            "substituted, or a tool/connectivity/cert failure looks like a source outage, "
            "first rule out a local tool-fit failure, then follow `docs/core_bypass.md` — "
            "record the event in `process_log/degradation_ledger.md` and set "
            '`status = "halted_core_bypass"` for operator review instead of continuing on a '
            "weaker path.\n"
        )
    else:
        core_bypass_guard = ""
    content = content.replace("{{CORE_BYPASS_GUARD}}", core_bypass_guard)
    content = content.replace("{{RUNTIME_DISCIPLINE}}", discipline_block)
    content = content.replace("{{AGENT_CATALOG}}", agent_catalog)
    content = content.replace("{{SKILL_CATALOG}}", skill_catalog)
    runtime_session = runtime_session.replace("{{SKILL_DIR}}", args.skill_dir)
    if args.session_out:
        session_path = Path(args.session_out)
        session_path.parent.mkdir(parents=True, exist_ok=True)
        session_path.write_text(runtime_session + "\n")
        # Relative path from the runtime doc to the session file (handles both
        # in-project deploys and --local mode where output sits under OUT_DIR).
        rel_path = os.path.relpath(session_path.resolve(),
                                   Path(args.output).resolve().parent)
        pointer = (
            "## How to start a session\n\n"
            f"Read `{rel_path}` and follow it."
        )
        content = content.replace("{{RUNTIME_SESSION_GUIDANCE}}", pointer)
    else:
        content = content.replace("{{RUNTIME_SESSION_GUIDANCE}}", runtime_session)

    Path(args.output).write_text(content)


if __name__ == "__main__":
    main()
