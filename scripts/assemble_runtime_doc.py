#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--scoring", default=None,
                        help="Path to scoring calibrations markdown (only consumed if {{SCORING}} placeholder exists)")
    parser.add_argument("--paper-type", required=True)
    parser.add_argument("--target-journals", required=True)
    parser.add_argument("--domain-areas", required=True)
    parser.add_argument("--doc-name", required=True)
    parser.add_argument("--agent-dir", required=True)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--seed-block", default=None,
                        help="Path to seed override markdown (omit for empty)")
    parser.add_argument("--discipline", default=None,
                        help="Path to runtime discipline markdown (omit for empty)")
    parser.add_argument("--agent-catalog", default=None,
                        help="Path to pre-generated agent catalog markdown (manual mode)")
    parser.add_argument("--skill-catalog", default=None,
                        help="Path to pre-generated skill catalog markdown (manual mode)")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = Path(args.core).read_text()
    runtime_session = Path(args.session).read_text().rstrip()
    scoring = Path(args.scoring).read_text() if args.scoring else ""

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
    content = content.replace("{{PAPER_TYPE}}", args.paper_type)
    content = content.replace("{{TARGET_JOURNALS}}", args.target_journals)
    content = content.replace("{{DOMAIN_AREAS}}", args.domain_areas)
    content = content.replace("{{AGENT_DIR}}", args.agent_dir)
    content = content.replace("{{SKILL_DIR}}", args.skill_dir)
    content = content.replace("{{SEED_OVERRIDE}}", seed_block)
    content = content.replace("{{RUNTIME_DISCIPLINE}}", discipline_block)
    content = content.replace("{{AGENT_CATALOG}}", agent_catalog)
    content = content.replace("{{SKILL_CATALOG}}", skill_catalog)
    runtime_session = runtime_session.replace("{{SKILL_DIR}}", args.skill_dir)
    content = content.replace("{{RUNTIME_SESSION_GUIDANCE}}", runtime_session)
    content = content.replace("{{SCORING}}", scoring)

    Path(args.output).write_text(content)


if __name__ == "__main__":
    main()
