#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--scoring", required=True)
    parser.add_argument("--paper-type", required=True)
    parser.add_argument("--target-journals", required=True)
    parser.add_argument("--domain-areas", required=True)
    parser.add_argument("--doc-name", required=True)
    parser.add_argument("--agent-dir", required=True)
    parser.add_argument("--skill-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = Path(args.core).read_text()
    runtime_session = Path(args.session).read_text().rstrip()
    scoring = Path(args.scoring).read_text()

    content = content.replace("{{RUNTIME_DOC_NAME}}", args.doc_name)
    content = content.replace("{{PAPER_TYPE}}", args.paper_type)
    content = content.replace("{{TARGET_JOURNALS}}", args.target_journals)
    content = content.replace("{{DOMAIN_AREAS}}", args.domain_areas)
    content = content.replace("{{AGENT_DIR}}", args.agent_dir)
    content = content.replace("{{SKILL_DIR}}", args.skill_dir)
    runtime_session = runtime_session.replace("{{SKILL_DIR}}", args.skill_dir)
    content = content.replace("{{RUNTIME_SESSION_GUIDANCE}}", runtime_session)
    content = content.replace("{{SCORING}}", scoring)

    Path(args.output).write_text(content)


if __name__ == "__main__":
    main()
