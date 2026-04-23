#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_vocab_to_metadata, load_body, load_vocab


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
    parser.add_argument("--shared-bodies-dir", default=None)
    parser.add_argument("--vocab", default=None)
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vocab = load_vocab(args.vocab)

    for agent_id, agent_metadata in metadata.items():
        agent_metadata = apply_vocab_to_metadata(
            agent_metadata, vocab, f"{args.metadata}:{agent_id}"
        )
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        (output_dir / f"{agent_id}.toml").write_text(render_agent(agent_metadata, body))


if __name__ == "__main__":
    main()
