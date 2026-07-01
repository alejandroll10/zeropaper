#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

FIELD_ORDER = ["name", "description"]

# Codex rejects (and silently skips) any skill whose `description` metadata
# exceeds this many BYTES — see issue #143. The limit is measured in UTF-8 bytes,
# not characters: Codex validates with Rust's `str::len()` (openai/codex #7730),
# so a description under 1024 *characters* can still trip the limit once multi-byte
# characters (em-dashes "—", accented letters "ü", math glyphs "≈"/"↔") are counted.
# Enforced fail-loud at assembly so an over-long description breaks the build (and
# assembly tests) instead of silently dropping the skill from Codex at runtime.
CODEX_DESCRIPTION_LIMIT = 1024


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
        description = codex_metadata.get("description", "")
        byte_len = len(description.encode("utf-8"))
        if byte_len > CODEX_DESCRIPTION_LIMIT:
            raise ValueError(
                f"Codex skill '{skill_id}' ({args.metadata}) has a description of "
                f"{byte_len} UTF-8 bytes ({len(description)} chars), exceeding Codex's "
                f"{CODEX_DESCRIPTION_LIMIT}-byte limit; Codex would silently skip it "
                f"(issue #143). Add a shorter \"codex\": {{\"description\": \"...\"}} "
                f"override to this skill's metadata (note the limit is bytes, not chars)."
            )
        (skill_dir / "SKILL.md").write_text(render_skill(codex_metadata, body))


if __name__ == "__main__":
    main()
