#!/usr/bin/env python3
"""Rewrite the `model:` frontmatter line in assembled Claude agent files.

Single post-assembly pass: applies a model remap (computed by
resolve_model_fallbacks.py) to every `*.md` in the Claude agents output dir, so
agents pinned to an unavailable model are repointed to their available fallback.
Centralizing this here means base, variant, and every extension's agents are
covered without threading remap args through each assembler call site.

Only the `model:` line inside the leading YAML frontmatter block is touched, and
only when its value matches a remap key — everything else is left byte-identical.
Idempotent: re-running with the same remap is a no-op once values are remapped.
"""
import argparse
import re
import sys
from pathlib import Path

# model: <value>  or  model: "<value>"  or  model: '<value>'  (frontmatter line)
MODEL_LINE = re.compile(r'^(\s*model:\s*)(["\']?)([^"\'#\n]+?)\2(\s*)$')


def remap_file(path, remap):
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return False  # no frontmatter block
    changed = False
    in_frontmatter = True
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if in_frontmatter and line.strip() == "---":
            in_frontmatter = False
            break
        m = MODEL_LINE.match(line)
        if m and m.group(3).strip() in remap:
            new_val = remap[m.group(3).strip()]
            lines[i] = f'{m.group(1)}"{new_val}"{m.group(4)}'
            changed = True
    if changed:
        path.write_text("".join(lines))
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="Directory of assembled agent *.md files.")
    ap.add_argument("--remap", action="append", default=[],
                    help="ideal=resolved pair. Repeatable.")
    args = ap.parse_args()

    remap = {}
    for r in args.remap:
        k, sep, v = r.partition("=")
        if sep and k.strip() and v.strip():
            remap[k.strip()] = v.strip()
    if not remap:
        return

    d = Path(args.dir)
    if not d.is_dir():
        # Fail loud: a remap was requested (non-empty) but the agents dir is
        # missing — that's a setup bug, not a benign skip. setup.sh's `set -e`
        # turns this nonzero exit into an abort.
        print(f"[model-remap] ERROR: {d} is not a directory", file=sys.stderr)
        sys.exit(1)

    changed = 0
    for p in sorted(d.glob("*.md")):
        if remap_file(p, remap):
            changed += 1
            print(f"[model-remap] {p.name}: model remapped", file=sys.stderr)
    print(f"[model-remap] {changed} agent file(s) updated in {d}", file=sys.stderr)


if __name__ == "__main__":
    main()
