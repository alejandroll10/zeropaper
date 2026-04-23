#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_vocab_to_metadata, load_body, load_vocab

FIELD_ORDER = ["name", "description", "tools", "skills", "model", "background", "memory"]
IGNORED_FIELDS = {"codex", "gemini"}


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
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
    parser.add_argument("--shared-bodies-dir", default=None,
                        help="Directory for shared core bodies ({id}-core.md). "
                             "Checked before --bodies-dir for each agent.")
    parser.add_argument("--vocab", default=None,
                        help="Optional variant vocab JSON; substitutes {{KEY}} in bodies.")
    parser.add_argument("--model-override", default=None,
                        help="Force all agents to this model (e.g. sonnet)")
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vocab = load_vocab(args.vocab)

    for agent_id, agent_metadata in metadata.items():
        agent_metadata = apply_vocab_to_metadata(
            agent_metadata, vocab, f"{args.metadata}:{agent_id}"
        )
        if args.model_override and "model" in agent_metadata:
            agent_metadata = {**agent_metadata, "model": args.model_override}
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        rendered = render_agent(agent_metadata, body)
        (output_dir / f"{agent_id}.md").write_text(rendered)


if __name__ == "__main__":
    main()
