#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

FIELD_ORDER = ["name", "description"]


def yaml_scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_skill(metadata, body):
    lines = ["---"]
    for key in FIELD_ORDER:
        if key in metadata:
            lines.append(f"{key}: {yaml_scalar(metadata[key])}")
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
        codex_metadata = {key: skill_metadata[key] for key in FIELD_ORDER if key in skill_metadata}
        (skill_dir / "SKILL.md").write_text(render_skill(codex_metadata, body))


if __name__ == "__main__":
    main()
