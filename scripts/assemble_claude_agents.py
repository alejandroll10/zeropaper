#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

FIELD_ORDER = ["name", "description", "tools", "skills", "model", "background", "memory"]
IGNORED_FIELDS = {"codex"}


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_agent(metadata, body):
    lines = ["---"]
    for key in FIELD_ORDER:
        if key in metadata:
            lines.append(f"{key}: {format_value(metadata[key])}")
    for key, value in metadata.items():
        if key not in FIELD_ORDER and key not in IGNORED_FIELDS:
            lines.append(f"{key}: {format_value(value)}")
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--bodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-override", default=None,
                        help="Force all agents to this model (e.g. sonnet)")
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    bodies_dir = Path(args.bodies_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for agent_id, agent_metadata in metadata.items():
        if args.model_override and "model" in agent_metadata:
            agent_metadata = {**agent_metadata, "model": args.model_override}
        body_path = bodies_dir / f"{agent_id}.md"
        body = body_path.read_text()
        rendered = render_agent(agent_metadata, body)
        (output_dir / f"{agent_id}.md").write_text(rendered)


if __name__ == "__main__":
    main()
