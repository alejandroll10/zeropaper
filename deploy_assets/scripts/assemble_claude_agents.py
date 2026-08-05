#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_mode_overrides, apply_vocab_to_metadata, load_body, load_vocab

FIELD_ORDER = ["name", "description", "tools", "skills", "model", "effort", "background", "memory"]
IGNORED_FIELDS = {"codex", "gemini", "pipeline_only", "category"}


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    s = str(value)
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


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
    parser.add_argument("--bodies-dir", action="append", default=[], required=True,
                        help="Directory for variant/extension bodies ({id}.md). "
                             "Repeatable; checked in order, first match wins. "
                             "Pass a --mode overlay dir before the base bodies dir to "
                             "shadow shared-agent bodies while inheriting the rest.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--shared-bodies-dir", action="append", default=[],
                        help="Directory for shared core bodies ({id}-core.md). "
                             "Repeatable; checked in order, first match wins. "
                             "Pass a --mode overlay dir before the base shared dir to "
                             "shadow variant-agent shared bodies while inheriting the rest.")
    parser.add_argument("--vocab", action="append", default=[],
                        help="Variant vocab JSON; substitutes {{KEY}} in bodies. "
                             "Repeatable; later overlays override earlier on duplicate keys.")
    parser.add_argument("--mode", default=None,
                        help="Active --mode slug (underscored, e.g. report). Merges each "
                             "agent's metadata['modes'][slug] field overrides over its base "
                             "fields; the 'modes' key itself is always stripped from output.")
    parser.add_argument("--model-override", default=None,
                        help="Force all agents to this model (e.g. sonnet)")
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vocab = load_vocab(args.vocab)

    for agent_id, agent_metadata in metadata.items():
        agent_metadata = apply_mode_overrides(agent_metadata, args.mode)
        agent_metadata = apply_vocab_to_metadata(
            agent_metadata, vocab, f"{args.metadata}:{agent_id}"
        )
        if args.model_override and "model" in agent_metadata:
            agent_metadata = {**agent_metadata, "model": args.model_override}
            # --light overrides model to sonnet; drop effort so the sonnet
            # subagent uses its default allocation rather than inheriting
            # the opus-tuned xhigh/high levels (which would defeat the
            # cost-reduction intent of --light).
            agent_metadata.pop("effort", None)
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        rendered = render_agent(agent_metadata, body)
        (output_dir / f"{agent_id}.md").write_text(rendered)


if __name__ == "__main__":
    main()
