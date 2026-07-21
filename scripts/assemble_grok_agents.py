#!/usr/bin/env python3
"""Assemble Grok Build agent definitions from shared metadata + prompt bodies.

Grok Build (xAI `grok` CLI, agent format `.grok/agents/*.md`) uses the same
file shape as Claude's `.claude/agents/*.md`: YAML frontmatter + a system-prompt
body. This assembler is the Grok twin of `assemble_gemini_agents.py`; it takes
the identical CLI so setup.sh wiring is a copy of the gemini call sites.

Key mappings (Claude metadata -> Grok frontmatter):
  tools:  Read,Write,Bash   -> allowed_tools: [read_file, write_file, run_terminal_cmd]
                               + capability_mode derived (read-only|read-write|all)
  model:  opus/sonnet/fable -> grok-4.5   (xAI ships one general tier in v1)
  effort: low/high          -> reasoning_effort
  category == "evaluator"   -> agents_md: false  (evaluator independence: the
                               orchestrator's AGENTS.md is NOT loaded into the
                               agent's context -- the native equivalent of the
                               codex-runtime launcher shim). Non-evaluators keep
                               agents_md: true so developers see project context.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_mode_overrides, apply_vocab_to_metadata, load_body, load_vocab

# Claude tool name -> Grok built-in tool name.
# Names verified against ~/.grok/bundled/agents/*.md and the grok binary.
TOOL_MAP = {
    "Read": "read_file",
    "Write": "write_file",
    "Edit": "edit_file",
    "Grep": "grep",
    "Glob": "list_dir",
    "Bash": "run_terminal_cmd",
    "WebSearch": "web_search",
    "WebFetch": "web_fetch",
}

# Claude model tier -> Grok model. xAI exposes a single general-purpose model in
# v1 (grok-4.5); every tier collapses to it. When xAI ships capability tiers,
# this table is the one place to split fable/opus vs sonnet.
GROK_DEFAULT_MODEL = "grok-4.5"
MODEL_MAP = {
    "fable": GROK_DEFAULT_MODEL,
    "opus": GROK_DEFAULT_MODEL,
    "sonnet": GROK_DEFAULT_MODEL,
    "haiku": GROK_DEFAULT_MODEL,
}


def map_tools(claude_tools_str):
    """Comma-separated Claude tool names -> list of Grok tool names."""
    tools = []
    for t in claude_tools_str.split(","):
        t = t.strip()
        if not t:
            continue
        tools.append(TOOL_MAP.get(t, t.lower()))
    return tools


def derive_capability_mode(claude_tools_str):
    """Map a Claude tool list to Grok's four capability tiers.

    read-only   : pure reader (Read/Grep/Glob/Web*), no Write/Edit/Bash
    read-write  : can edit files but not run shell
    execute     : can run shell but not edit files (rare — audit/probe agents)
    all         : can both edit files and run shell
    """
    tools = {t.strip() for t in claude_tools_str.split(",")}
    has_write = bool(tools & {"Write", "Edit"})
    has_exec = "Bash" in tools
    if has_write and has_exec:
        return "all"
    if has_write:
        return "read-write"
    if has_exec:
        return "execute"
    return "read-only"


def map_model(claude_model, grok_override=None, model_override=None):
    # A --model-override that names a Claude tier (e.g. `sonnet` under --light)
    # maps through the tier table; an unrecognized value is assumed to already
    # be a valid Grok model id and passes through raw (matches the gemini sibling).
    if model_override:
        return MODEL_MAP.get(model_override, model_override)
    if grok_override:
        return grok_override
    return MODEL_MAP.get(claude_model, GROK_DEFAULT_MODEL)


def yaml_list(items):
    return "[" + ", ".join(items) + "]"


def render_agent(metadata, body, model_override=None):
    grok_meta = metadata.get("grok", {})
    category = metadata.get("category", "")
    is_evaluator = category == "evaluator"

    lines = ["---"]
    lines.append(f'name: {metadata["name"]}')
    # description is a YAML double-quoted scalar: escape backslashes first, then
    # embedded quotes (order matters — backslash is the escape char).
    desc = metadata["description"].replace("\\", "\\\\").replace('"', '\\"')
    lines.append(f'description: "{desc}"')
    lines.append(f'model: {map_model(metadata.get("model"), grok_meta.get("model"), model_override)}')

    if "tools" in metadata:
        lines.append(f'capability_mode: {derive_capability_mode(metadata["tools"])}')
        lines.append(f'allowed_tools: {yaml_list(map_tools(metadata["tools"]))}')

    effort = grok_meta.get("reasoning_effort", metadata.get("effort"))
    if effort:
        lines.append(f'reasoning_effort: {effort}')

    # Evaluator independence: keep the orchestrator's AGENTS.md and parent
    # conversation out of an evaluator's context so its verdict is uncorrupted.
    # This is the native-frontmatter equivalent of the codex launch_agent.sh
    # shim (which suppresses AGENTS.md by running an isolated `codex exec`).
    lines.append(f'agents_md: {"false" if is_evaluator else "true"}')
    lines.append("prompt_mode: full")

    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--bodies-dir", action="append", default=[], required=True,
                        help="Directory for variant/extension bodies ({id}.md). "
                             "Repeatable; checked in order, first match wins.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--shared-bodies-dir", action="append", default=[],
                        help="Directory for shared core bodies ({id}-core.md). "
                             "Repeatable; checked in order, first match wins.")
    parser.add_argument("--vocab", action="append", default=[],
                        help="Variant vocab JSON. Repeatable; later overlays override earlier.")
    parser.add_argument("--mode", default=None,
                        help="Active --mode slug (underscored, e.g. report). Merges each "
                             "agent's metadata['modes'][slug] field overrides over its base "
                             "fields; the 'modes' key itself is always stripped from output.")
    parser.add_argument("--model-override", default=None,
                        help="Force all agents to this model tier (e.g. sonnet). "
                             "Collapses to grok-4.5 in v1 like every tier.")
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
        body = load_body(agent_id, args.bodies_dir, args.shared_bodies_dir, vocab)
        rendered = render_agent(agent_metadata, body, args.model_override)
        (output_dir / f"{agent_id}.md").write_text(rendered)


if __name__ == "__main__":
    main()
