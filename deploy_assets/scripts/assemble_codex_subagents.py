#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import apply_mode_overrides, apply_vocab_to_metadata, load_body, load_vocab


# Claude tier alias → codex capability tier, one-for-one (the mapping the agent
# metadata already follows agent-by-agent). Used only for --model-override, so a
# `--light` deployment collapses codex subagents the way it collapses the Claude
# ones. An unrecognized value is assumed to already be a codex model id and
# passes through raw (matches the gemini/grok siblings).
MODEL_MAP = {
    "fable": "gpt-5.6-sol",
    "opus": "gpt-5.6-terra",
    "sonnet": "gpt-5.6-luna",
    "haiku": "gpt-5.6-luna",
}


def toml_string(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def toml_multiline(value):
    escaped = value.replace("'''", "''\\'")
    return f"'''\n{escaped.rstrip()}\n'''"


def render_agent(metadata, body, model_override=None):
    lines = [
        f'name = {toml_string(metadata["name"])}',
        f'description = {toml_string(metadata["description"])}',
        f'developer_instructions = {toml_multiline(body)}',
    ]

    codex = metadata.get("codex", {})
    if model_override and "model" in codex:
        # --light collapses every subagent to one tier. Map the Claude alias
        # through the tier table and drop model_reasoning_effort, mirroring how
        # assemble_claude_agents.py drops `effort`: the pinned levels are tuned
        # for the agent's ideal tier, and leaving `high` on a Luna worker would
        # defeat the cost-reduction intent of --light. Codex supplies the
        # selected model's default effort when the field is absent.
        codex = {
            **{k: v for k, v in codex.items() if k != "model_reasoning_effort"},
            "model": MODEL_MAP.get(model_override, model_override),
        }
    if "model" in codex:
        lines.append(f'model = {toml_string(codex["model"])}')
    if "model_reasoning_effort" in codex:
        lines.append(
            f'model_reasoning_effort = {toml_string(codex["model_reasoning_effort"])}'
        )
    if "sandbox_mode" in codex:
        lines.append(f'sandbox_mode = {toml_string(codex["sandbox_mode"])}')
    # Native role dispatch must remain independent of the orchestrator. A
    # clean spawn omits the parent's conversation, while this setting omits
    # the project's AGENTS.md (which tells the parent that it is the
    # orchestrator). Disable both multi-agent selectors: Codex 0.147 checks
    # features.multi_agent_v2 before agents.enabled, so the latter alone is
    # overridden by a parent CLI or ordinary user-config V2 flag. The role
    # layer has session-flag precedence and pins both selectors off for the
    # child in that normal stack. Higher legacy managed/MDM layers and separate
    # enterprise feature requirements remain the documented #240 edge.
    lines.append("project_doc_max_bytes = 0")
    lines.extend(
        [
            "",
            "[features.multi_agent_v2]",
            "enabled = false",
            "",
            "[agents]",
            "enabled = false",
        ]
    )
    return "\n".join(lines) + "\n"


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
    parser.add_argument("--model-override", default=None,
                        help="Force every agent that pins a codex model onto this one "
                             "(e.g. `sonnet` under --light, mapped through MODEL_MAP). "
                             "Also drops model_reasoning_effort.")
    parser.add_argument("--mode", default=None,
                        help="Active --mode slug (underscored, e.g. report). Merges each "
                             "agent's metadata['modes'][slug] field overrides over its base "
                             "fields; the 'modes' key itself is always stripped from output.")
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
        (output_dir / f"{agent_id}.toml").write_text(
            render_agent(agent_metadata, body, args.model_override)
        )


if __name__ == "__main__":
    main()
