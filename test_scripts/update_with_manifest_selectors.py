#!/usr/bin/python3 -I
"""Test-only adapter that spells a target's full selector on update invocations."""

import json
import os
import sys


root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
updater = os.path.join(root, "update.sh")
if len(sys.argv) < 2:
    raise SystemExit("usage: update_with_manifest_selectors.py PROJECT [update args]")
project = sys.argv[1]
arguments = sys.argv[2:]
try:
    with open(os.path.join(project, ".deploy_manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
except (OSError, ValueError):
    manifest = {}

variant = manifest.get("variant")
if variant not in {"finance", "macro", "llm_cognition"}:
    variant = "finance"
mode = manifest.get("mode")
if not isinstance(mode, str):
    mode = ""
extensions = manifest.get("extensions")
if not isinstance(extensions, list) or not all(isinstance(item, str) for item in extensions):
    extensions = []
flags = manifest.get("flags")
if not isinstance(flags, dict):
    flags = {}
source = manifest.get("source")
source_digest = source.get("content_digest") if isinstance(source, dict) else None

def supplied(*names: str) -> bool:
    return any(argument in names or any(argument.startswith(name + "=") for name in names)
               for argument in arguments)

selectors: list[str] = []
if not supplied("--source-digest"):
    if not isinstance(source_digest, str):
        source_digest = "sha256:" + "0" * 64
    selectors += ["--source-digest", source_digest]
if not supplied("--variant"):
    selectors += ["--variant", variant]
if not supplied("--mode", "--no-mode"):
    selectors += ["--mode", mode] if mode else ["--no-mode"]
if not supplied("--ext", "--clear-ext"):
    selectors += ["--clear-ext"]
    for extension in extensions:
        selectors += ["--ext", extension]
for positive, negative, key in (
    ("--seeded", "--no-seeded", "seeded"),
    ("--faithful", "--no-faithful", "faithful"),
    ("--manual", "--no-manual", "manual"),
    ("--light", "--no-light", "light"),
    ("--halt-on-core-bypass", "--no-halt-on-core-bypass", "halt_on_core_bypass"),
):
    if not supplied(positive, negative):
        selectors.append(positive if flags.get(key) is True else negative)

os.execv(updater, [updater, project, *selectors, *arguments])
