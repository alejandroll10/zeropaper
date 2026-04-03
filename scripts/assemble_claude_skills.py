#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

FIELD_ORDER = ["name", "description", "user-invocable", "argument-hint", "allowed-tools"]


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_skill(metadata, body):
    lines = ["---"]
    for key in FIELD_ORDER:
        if key in metadata:
            lines.append(f"{key}: {format_value(metadata[key])}")
    for key, value in metadata.items():
        if key not in FIELD_ORDER:
            lines.append(f"{key}: {format_value(value)}")
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--bodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    bodies_dir = Path(args.bodies_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for skill_id, skill_metadata in metadata.items():
        body_path = bodies_dir / f"{skill_id}.md"
        body = body_path.read_text()
        skill_dir = output_dir / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(render_skill(skill_metadata, body))


if __name__ == "__main__":
    main()
