#!/usr/bin/env python3
"""Assemble OpenCode subagents from shared metadata and prompt bodies."""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_mode_overrides, apply_vocab_to_metadata, load_body, load_vocab

OPENCODE_DEFAULT_MODEL = "opencode/deepseek-v4-flash"
MODEL_MAP = {tier: OPENCODE_DEFAULT_MODEL for tier in ("fable", "opus", "sonnet", "haiku")}

TOOL_MAP = {
    "Read": ("read",),
    "Write": ("edit",),
    "Edit": ("edit",),
    "Glob": ("glob", "list"),
    "Grep": ("grep",),
    "Bash": ("bash",),
    "WebSearch": ("websearch",),
    "WebFetch": ("webfetch",),
}


def map_model(claude_model, opencode_override=None, model_override=None):
    if model_override:
        return MODEL_MAP.get(model_override, model_override)
    if opencode_override:
        return opencode_override
    return MODEL_MAP.get(claude_model, OPENCODE_DEFAULT_MODEL)


def allowed_permissions(tools):
    allowed = set()
    for tool in tools.split(","):
        allowed.update(TOOL_MAP.get(tool.strip(), ()))
    return allowed


def yaml_quote(value):
    value = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{value}"'


def render_agent(metadata, body, model_override=None):
    runtime_meta = metadata.get("opencode", {})
    allowed = allowed_permissions(metadata.get("tools", ""))
    model = map_model(metadata.get("model"), runtime_meta.get("model"), model_override)
    lines = [
        "---",
        f"description: {yaml_quote(metadata['description'])}",
        "mode: subagent",
        f"model: {yaml_quote(model)}",
        "permission:",
    ]
    for permission in ("read", "edit", "glob", "grep", "list", "bash", "websearch", "webfetch"):
        lines.append(f'  {permission}: {"allow" if permission in allowed else "deny"}')
    # Pipeline workers are leaves. This prevents recursive orchestration and
    # keeps evaluator/developer boundaries explicit.
    lines.extend(["  task: deny", "  external_directory: deny"])
    skills = metadata.get("skills", [])
    if isinstance(skills, str):
        skills = [item.strip() for item in skills.split(",") if item.strip()]
    if skills:
        lines.append("  skill:")
        lines.append('    "*": deny')
        for skill in skills:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill):
                raise ValueError(f"Invalid OpenCode skill id: {skill!r}")
            lines.append(f"    {yaml_quote(skill)}: allow")
    else:
        lines.append("  skill: deny")
    if runtime_meta.get("steps") is not None:
        steps = runtime_meta["steps"]
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError(f"OpenCode steps must be a positive integer, got {steps!r}")
        lines.append(f"steps: {steps}")
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--bodies-dir", action="append", default=[], required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--shared-bodies-dir", action="append", default=[])
    parser.add_argument("--vocab", action="append", default=[])
    parser.add_argument("--mode", default=None)
    parser.add_argument("--model-override", default=None)
    args = parser.parse_args()

    metadata = json.loads(Path(args.metadata).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    vocab = load_vocab(args.vocab)
    for agent_id, agent_metadata in metadata.items():
        agent_metadata = apply_mode_overrides(agent_metadata, args.mode)
        agent_metadata = apply_vocab_to_metadata(agent_metadata, vocab, f"{args.metadata}:{agent_id}")
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        (output_dir / f"{agent_id}.md").write_text(
            render_agent(agent_metadata, body, args.model_override)
        )


if __name__ == "__main__":
    main()
