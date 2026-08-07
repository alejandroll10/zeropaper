#!/usr/bin/env python3
"""Validate skill frontmatter against Codex's bundled authoring contract.

The rule source mirrored here is openai/codex's bundled
``skill-creator/scripts/quick_validate.py``.  Keep this module dependency-free at
import time: ``setup.sh`` imports it before project dependencies are installed.
The standalone SKILL.md validator imports PyYAML lazily for the dev-instruction
sync path, which already requires PyYAML.
"""

import argparse
import re
import sys
from collections.abc import Mapping
from pathlib import Path


CODEX_NAME_LIMIT_CHARS = 64
CODEX_DESCRIPTION_LIMIT_CHARS = 1024
CODEX_ALLOWED_FRONTMATTER_PROPERTIES = frozenset(
    {"name", "description", "license", "allowed-tools", "metadata"}
)


class CodexSkillValidationError(ValueError):
    """A skill violates Codex's bundled skill-authoring contract."""


def validate_codex_skill_frontmatter(frontmatter):
    """Validate parsed frontmatter and return stripped name and description.

    Codex's bundled validator only requires the two keys to exist, but its runtime
    parser rejects an empty description.  Generated skills therefore enforce
    non-empty values as a strict, runtime-safe superset of the authoring checks.
    """
    if not isinstance(frontmatter, Mapping):
        raise CodexSkillValidationError("frontmatter must be a YAML mapping")

    unexpected = set(frontmatter) - CODEX_ALLOWED_FRONTMATTER_PROPERTIES
    if unexpected:
        allowed = ", ".join(sorted(CODEX_ALLOWED_FRONTMATTER_PROPERTIES))
        names = ", ".join(sorted(map(str, unexpected)))
        raise CodexSkillValidationError(
            f"unexpected frontmatter key(s): {names}. Allowed properties are: {allowed}"
        )

    for field in ("name", "description"):
        if field not in frontmatter:
            raise CodexSkillValidationError(f"missing frontmatter field '{field}'")
        if not isinstance(frontmatter[field], str):
            value_type = type(frontmatter[field]).__name__
            raise CodexSkillValidationError(
                f"frontmatter field '{field}' must be a string, got {value_type}"
            )

    name = frontmatter["name"].strip()
    description = frontmatter["description"].strip()
    if not name:
        raise CodexSkillValidationError("frontmatter field 'name' must be non-empty")
    if not description:
        raise CodexSkillValidationError(
            "frontmatter field 'description' must be non-empty"
        )

    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise CodexSkillValidationError(
            f"name '{name}' must be hyphen-case (lowercase letters, digits, and hyphens only)"
        )
    if name.startswith("-") or name.endswith("-") or "--" in name:
        raise CodexSkillValidationError(
            f"name '{name}' cannot start or end with a hyphen or contain consecutive hyphens"
        )
    if len(name) > CODEX_NAME_LIMIT_CHARS:
        raise CodexSkillValidationError(
            f"name is {len(name)} characters, exceeding Codex's "
            f"{CODEX_NAME_LIMIT_CHARS}-character skill-authoring limit"
        )

    if "<" in description or ">" in description:
        raise CodexSkillValidationError(
            "description cannot contain angle brackets (< or >)"
        )
    if len(description) > CODEX_DESCRIPTION_LIMIT_CHARS:
        raise CodexSkillValidationError(
            f"description is {len(description)} characters, exceeding Codex's "
            f"{CODEX_DESCRIPTION_LIMIT_CHARS}-character skill-authoring limit"
        )

    return name, description


def load_skill_frontmatter(skill_md):
    """Parse a SKILL.md frontmatter block using the bundled validator's format."""
    try:
        import yaml
    except ImportError as exc:
        raise CodexSkillValidationError(
            "PyYAML is required to validate SKILL.md frontmatter"
        ) from exc

    skill_md = Path(skill_md)
    if not skill_md.is_file():
        raise CodexSkillValidationError("SKILL.md not found")
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        raise CodexSkillValidationError("no YAML frontmatter found")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise CodexSkillValidationError("invalid frontmatter format")
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise CodexSkillValidationError(f"invalid YAML frontmatter: {exc}") from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_md")
    parser.add_argument("--label")
    args = parser.parse_args()

    label = args.label or str(args.skill_md)
    try:
        fields = load_skill_frontmatter(args.skill_md)
        name, description = validate_codex_skill_frontmatter(fields)
    except (OSError, CodexSkillValidationError) as exc:
        print(f"ERROR: {label} SKILL.md {exc}", file=sys.stderr)
        return 1

    print(
        f"  {label}: name {len(name)}/{CODEX_NAME_LIMIT_CHARS}, "
        f"description {len(description)}/{CODEX_DESCRIPTION_LIMIT_CHARS} chars"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
