#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def toml_string(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def toml_multiline(value):
    escaped = value.replace("'''", "''\\'")
    return f"'''\n{escaped.rstrip()}\n'''"


def render_agent(metadata, body):
    lines = [
        f'name = {toml_string(metadata["name"])}',
        f'description = {toml_string(metadata["description"])}',
        f'developer_instructions = {toml_multiline(body)}',
    ]

    codex = metadata.get("codex", {})
    if "model" in codex:
        lines.append(f'model = {toml_string(codex["model"])}')
    if "model_reasoning_effort" in codex:
        lines.append(
            f'model_reasoning_effort = {toml_string(codex["model_reasoning_effort"])}'
        )
    if "sandbox_mode" in codex:
        lines.append(f'sandbox_mode = {toml_string(codex["sandbox_mode"])}')
    return "\n".join(lines) + "\n"


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

    for agent_id, agent_metadata in metadata.items():
        body_path = bodies_dir / f"{agent_id}.md"
        body = body_path.read_text()
        (output_dir / f"{agent_id}.toml").write_text(render_agent(agent_metadata, body))


if __name__ == "__main__":
    main()
