#!/usr/bin/env python3
"""Print agent names matching a category from one or more metadata files.

Single source of truth for the faithful-mode developing/evaluator
classification (--category) and for the set of Bash-capable agents
(--has-tool Bash, drives the bash-background inject loop). Used by
setup.sh to drive the inject loops and by core.md/faithful.md
placeholder substitution. One name per line on stdout (deduped,
preserving first-seen order).

Categories live in each metadata entry as `"category": "developing"` or
`"category": "evaluator"`. Utility agents have no category field and
are silently skipped.

Example:
    python3 scripts/list_agents_by_category.py --category developing \\
        --metadata templates/agent_metadata/claude_shared_agents.json \\
        --metadata templates/agent_metadata/claude_variant_agents.json
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", action="append", required=True,
                        help="Path to a metadata JSON file (repeatable). "
                             "Missing files are silently skipped so the caller "
                             "can pass an extension's metadata path even when "
                             "that extension isn't installed.")
    parser.add_argument("--category",
                        choices=["developing", "evaluator"])
    parser.add_argument("--has-tool",
                        help="List agents whose `tools` field includes this "
                             "tool (e.g. Bash). Mutually exclusive with "
                             "--category; exactly one is required.")
    args = parser.parse_args()

    if bool(args.category) == bool(args.has_tool):
        parser.error("pass exactly one of --category or --has-tool")

    seen = set()
    for path in args.metadata:
        p = Path(path)
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        for name, meta in data.items():
            if name in seen:
                continue
            if args.category:
                match = meta.get("category") == args.category
            else:
                raw = meta.get("tools", "")
                # `tools` is a comma-string in every current metadata file;
                # tolerate a JSON list too rather than crash mid-deploy.
                items = raw if isinstance(raw, list) else raw.split(",")
                tools = [str(t).strip() for t in items]
                match = args.has_tool in tools
            if match:
                print(name)
                seen.add(name)


if __name__ == "__main__":
    main()
