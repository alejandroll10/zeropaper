#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

FIELD_ORDER = ["name", "description"]

# Codex's bundled skill-creator validator caps `name` at 64 characters and
# `description` at 1024 CHARACTERS. Its quick_validate.py strips each string, then
# uses Python's len(), matching the character-based contract rather than UTF-8 byte
# length. The runtime loader may tolerate an overlong description, but generated
# skills should satisfy the authoring validator instead of relying on that permissive
# implementation detail.
CODEX_NAME_LIMIT_CHARS = 64
CODEX_DESCRIPTION_LIMIT_CHARS = 1024


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


def resolve_codex_metadata(skill_metadata):
    """Base fields overlaid with a `codex` override block (mirrors the `claude`
    override pattern in assemble_claude_skills.py). A `codex.description` lets a
    skill ship a shorter, Codex-safe description while keeping its full,
    discovery-rich description for Claude."""
    resolved = {key: skill_metadata[key] for key in FIELD_ORDER if key in skill_metadata}
    override = skill_metadata.get("codex")
    if isinstance(override, dict):
        for key in FIELD_ORDER:
            if key in override:
                resolved[key] = override[key]
    return resolved


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
        codex_metadata = resolve_codex_metadata(skill_metadata)
        name = codex_metadata.get("name", "")
        name_len = len(name.strip())
        if name_len > CODEX_NAME_LIMIT_CHARS:
            raise ValueError(
                f"Codex skill '{skill_id}' ({args.metadata}) has a name of "
                f"{name_len} characters, exceeding Codex's "
                f"{CODEX_NAME_LIMIT_CHARS}-character skill-authoring limit. "
                f"Add a shorter \"codex\": {{\"name\": \"...\"}} override "
                f"to this skill's metadata."
            )
        description = codex_metadata.get("description", "")
        char_len = len(description.strip())
        if char_len > CODEX_DESCRIPTION_LIMIT_CHARS:
            raise ValueError(
                f"Codex skill '{skill_id}' ({args.metadata}) has a description of "
                f"{char_len} characters, exceeding Codex's "
                f"{CODEX_DESCRIPTION_LIMIT_CHARS}-character skill-authoring limit. "
                f"Add a shorter \"codex\": {{\"description\": \"...\"}} override "
                f"to this skill's metadata."
            )
        (skill_dir / "SKILL.md").write_text(render_skill(codex_metadata, body))


if __name__ == "__main__":
    main()
