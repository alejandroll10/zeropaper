#!/usr/bin/env python3
"""Generate a markdown catalog of agents or skills from one or more metadata JSON files.

Used by setup.sh in manual mode to produce {{AGENT_CATALOG}} and {{SKILL_CATALOG}}
blocks for core_manual.md. Reads metadata files in order; later files override earlier
entries with the same key (so extensions can shadow shared definitions if needed).
"""
import argparse
import json
import re
from pathlib import Path

ORCHESTRATOR_REPLACEMENTS = [
    ("The orchestrator launches this agent at ", "Used at "),
    ("The orchestrator launches this agent twice", "Runs twice"),
    ("The orchestrator launches this agent ", "Runs "),
    ("The orchestrator launches it at ", "Used at "),
    ("Launched by the orchestrator at ", "Used at "),
    ("Launched at ", "Used at "),
]


def clean_description(desc: str) -> str:
    for old, new in ORCHESTRATOR_REPLACEMENTS:
        desc = desc.replace(old, new)
    desc = desc.replace("{{DOMAIN}}", "")
    desc = re.sub(r"\s+", " ", desc).strip()
    return desc


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
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    items = load_items(args.metadata)
    lines = []
    for name in sorted(items.keys()):
        meta = items[name]
        if meta.get("pipeline_only"):
            continue
        desc = clean_description(meta.get("description", ""))
        lines.append(f"- `{name}` — {desc}")

    Path(args.output).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
