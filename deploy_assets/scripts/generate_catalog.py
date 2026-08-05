#!/usr/bin/env python3
"""Generate a markdown catalog of agents or skills from one or more metadata JSON files.

Used by setup.sh in manual mode to produce {{AGENT_CATALOG}} and {{SKILL_CATALOG}}
blocks for core_manual.md. Reads metadata files in order; later files override earlier
entries with the same key (so extensions can shadow shared definitions if needed).
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Reuse the same vocab loader the assemblers use, so {{KEY}} placeholders in
# metadata `description` fields (e.g. {{THEORY_GEN_DESCRIPTION}} added in
# phase 4c) resolve identically here. Without this the manual catalog would
# ship literal {{KEY}} tokens to the user.
sys.path.insert(0, str(Path(__file__).parent))
from agent_body_loader import load_vocab  # noqa: E402

ORCHESTRATOR_REPLACEMENTS = [
    ("The orchestrator launches this agent at ", "Used at "),
    ("The orchestrator launches this agent twice", "Runs twice"),
    ("The orchestrator launches this agent ", "Runs "),
    ("The orchestrator launches it at ", "Used at "),
    ("Launched by the orchestrator at ", "Used at "),
    ("Launched at ", "Used at "),
]

VOCAB_KEY_PATTERN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")

# Split on period+space-before-capital. Negative lookbehinds block common
# abbreviations that would otherwise mid-sentence-truncate. Each lookbehind
# is fixed-width (Python re constraint).
SENTENCE_SPLIT = re.compile(
    r"(?<![Vv]s)"      # vs.
    r"(?<![Cc]f)"      # cf.
    r"(?<!etc)"        # etc.
    r"(?<![ei]\.g)"    # e.g.
    r"(?<![ei]\.e)"    # i.e.
    r"(?<=[a-z\)])\. (?=[A-Z])"
)
DESC_CHAR_CAP = 120


def apply_vocab(desc: str, vocab) -> str:
    if not vocab:
        return desc
    def replace(m):
        key = m.group(1)
        return vocab.get(key, m.group(0))
    return VOCAB_KEY_PATTERN.sub(replace, desc)


def shorten(desc: str) -> str:
    """First sentence, soft-capped. Ellipsis when truncated so users know to
    read the agent file in {{AGENT_DIR}}/<name>.md for the full firing rules."""
    first = SENTENCE_SPLIT.split(desc, maxsplit=1)[0].rstrip(". ")
    if len(first) > DESC_CHAR_CAP:
        cut = first[:DESC_CHAR_CAP].rsplit(" ", 1)[0]
        return cut + "…"
    return first + "."


def clean_description(desc: str, vocab=None) -> str:
    desc = apply_vocab(desc, vocab)
    for old, new in ORCHESTRATOR_REPLACEMENTS:
        desc = desc.replace(old, new)
    desc = desc.replace("{{DOMAIN}}", "")
    desc = re.sub(r"\s+", " ", desc).strip()
    return shorten(desc)


def load_items(metadata_paths):
    items = {}
    for path in metadata_paths:
        p = Path(path)
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        for k, v in data.items():
            items[k] = v
    return items


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", action="append", required=True,
                        help="Path to a metadata JSON file (repeatable)")
    parser.add_argument("--vocab", action="append", default=[],
                        help="Vocab JSON for {{KEY}} substitution in description fields. "
                             "Repeatable; merged in order (later overrides earlier on "
                             "duplicate keys), matching the assembler convention.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    vocab = load_vocab(args.vocab) or {}
    items = load_items(args.metadata)
    lines = []
    for name in sorted(items.keys()):
        meta = items[name]
        if meta.get("pipeline_only"):
            continue
        desc = clean_description(meta.get("description", ""), vocab)
        lines.append(f"- `{name}` — {desc}")

    Path(args.output).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
