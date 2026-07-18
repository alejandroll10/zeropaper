#!/usr/bin/env python3
"""Emit the deployed model-heal config.json (build-time only, not itself deployed).

Records each agent's IDEAL model — the model it would be pinned to if every tier
were available — so the launch-time healer (code/utils/model_heal/heal_agent_models.py)
can restore that ideal after an earlier fallback, or fall back again if it is down.
The deployed *.md only carries the current (possibly-remapped) pin, so the ideal has
to be captured separately here, at build time, from the SAME metadata the assemblers
and resolve_model_fallbacks.py read.

Output shape (consumed by heal_agent_models.py):
  {
    "agents":    {"<agent-key>": "<ideal-model>", ...},   # keyed by *.md file stem
    "fallbacks": {"<model>": ["<next>", ...], ...}         # from model_fallbacks.json
  }

The agent key is the metadata key, which is exactly the assembled *.md filename stem
(verified: metadata key "branch-manager" -> .claude/agents/branch-manager.md).

Under --light every subagent assembles as `--light-model` (sonnet), so the ideal is
that model, not the metadata's top-tier pin — mirroring what the assembler actually
wrote, so the healer restores to the right target.
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", action="append", default=[],
                    help="Agent metadata JSON file(s). Repeatable.")
    ap.add_argument("--fallbacks", required=True, help="Path to model_fallbacks.json")
    ap.add_argument("--light-model", default="",
                    help="If set (e.g. 'sonnet'), every agent's ideal is this model "
                         "(mirrors setup.sh --light --model-override).")
    ap.add_argument("--out", required=True, help="Where to write config.json")
    args = ap.parse_args()

    agents = {}
    for mf in args.metadata:
        p = Path(mf)
        if not p.exists():
            continue
        try:
            md = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"[heal-config] WARN: could not read {mf}: {e}", file=sys.stderr)
            continue
        for key, agent in md.items():
            if isinstance(agent, dict) and agent.get("model"):
                agents[key] = args.light_model or agent["model"]

    fb = json.loads(Path(args.fallbacks).read_text())
    fallbacks = {k: v for k, v in fb.items() if not k.startswith("_")}

    Path(args.out).write_text(json.dumps({"agents": agents, "fallbacks": fallbacks},
                                         indent=2, sort_keys=True) + "\n")
    print(f"[heal-config] wrote {len(agents)} agent ideals -> {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
