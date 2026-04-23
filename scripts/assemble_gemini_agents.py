#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_vocab_to_metadata, load_body, load_vocab

# Claude tool name → Gemini tool name
TOOL_MAP = {
    "Read": "read_file",
    "Write": "write_file",
    "Edit": "replace",
    "Grep": "grep_search",
    "Glob": "glob",
    "Bash": "run_shell_command",
    "WebSearch": "google_web_search",
    "WebFetch": "web_fetch",
}

# Claude model → Gemini model
MODEL_MAP = {
    "opus": "gemini-3-preview",
    "sonnet": "gemini-3-flash-preview",
    "haiku": "gemini-3-flash-preview",
}


def map_tools(claude_tools_str):
    """Convert comma-separated Claude tool names to list of Gemini tool names."""
    tools = []
    for t in claude_tools_str.split(","):
        t = t.strip()
        if t in TOOL_MAP:
            tools.append(TOOL_MAP[t])
        else:
            tools.append(t.lower())
    return tools


def map_model(claude_model, gemini_override=None):
    """Map Claude model name to Gemini model name."""
    if gemini_override:
        return gemini_override
    return MODEL_MAP.get(claude_model, "gemini-3-preview")


def render_agent(metadata, body, model_override=None):
    lines = ["---"]
    lines.append(f'name: {metadata["name"]}')
    lines.append(f'description: "{metadata["description"]}"')
    lines.append("kind: local")

    # Tools
    if "tools" in metadata:
        gemini_tools = map_tools(metadata["tools"])
        lines.append("tools:")
        for tool in gemini_tools:
            lines.append(f"  - {tool}")

    # Model: prefer gemini.model from metadata, then map Claude model
    gemini_meta = metadata.get("gemini", {})
    if model_override:
        model = MODEL_MAP.get(model_override, model_override)
    elif "model" in gemini_meta:
        model = gemini_meta["model"]
    elif "model" in metadata:
        model = map_model(metadata["model"])
    else:
        model = "gemini-3-preview"
    lines.append(f"model: {model}")

    # max_turns from gemini metadata or default
    max_turns = gemini_meta.get("max_turns", 30)
    lines.append(f"max_turns: {max_turns}")

    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--bodies-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--shared-bodies-dir", default=None)
    parser.add_argument("--vocab", default=None)
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
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        rendered = render_agent(agent_metadata, body, args.model_override)
        (output_dir / f"{agent_id}.md").write_text(rendered)


if __name__ == "__main__":
    main()
