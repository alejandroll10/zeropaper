#!/usr/bin/env python3
"""Launch-time model heal: set every Claude subagent to its best AVAILABLE tier.

Setup pins each agent to an *ideal* model (e.g. `fable`) and, if that model is
unavailable at setup time, bakes in a fallback (`opus`). But availability changes
after deployment — a provider outage clears, or a healthy tier goes down mid-life.
This script re-decides at every launch, in BOTH directions:

  * ideal available   -> restore the ideal (undo an earlier fallback)
  * ideal unavailable -> walk its fallback chain to the first available tier

so an agent is never left on a downgraded tier once its ideal recovers, and never
left pinned to a dead tier. It is the runtime twin of setup.sh's build-time remap
(scripts/resolve_model_fallbacks.py + apply_model_remap.py); it exists because that
remap runs ONCE, at setup, and cannot reach an already-deployed project.

Config (config.json, deployed alongside this script):
  {
    "agents":    {"<agent-file-stem>": "<ideal-model>", ...},  # the first choice
    "fallbacks": {"<model>": ["<next>", "<next>", ...], ...}    # ordered chains
  }
`agents` is the memory of each agent's ideal — the deployed *.md only carries the
current (possibly-downgraded) pin, so the ideal must be recorded separately or a
restore is impossible.

Probing mirrors resolve_model_fallbacks.py exactly: run the SAME `claude` CLI the
agents run on, classify by output CONTENT (the unavailable/credits messages return
rc=0, so exit code alone is unreliable), cache one probe per distinct model.

Fail-safe by construction: any probe that is inconclusive (CLI missing, timeout,
network) leaves that agent's current pin UNTOUCHED. A launch must never be blocked
or degraded by an unreachable probe — worst case we do nothing and the existing
build-time pin (or the orchestrator's mid-run fallback doctrine) still applies.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Same markers as scripts/resolve_model_fallbacks.py — keep the two in sync (see
# docs/model_fallback.md "Marker examples"). Specific to provider/status phrasing
# so a chatty-but-available model can't be falsely downgraded.
UNAVAILABLE_MARKERS = [
    "is currently unavailable",
    "fable-mythos-access",
    "usage credits are required",
    "model not found",
    "unknown model",
    "invalid model",
]
PROBE_PROMPT = "Reply with exactly: ok"
MODEL_LINE = re.compile(r'^(\s*model:\s*)(["\']?)([^"\'#\n]+?)\2(\s*)$')


def probe(model, timeout):
    """'available' | 'unavailable' | 'inconclusive' — content-classified."""
    try:
        r = subprocess.run(["claude", "-p", "--model", model], input=PROBE_PROMPT,
                            capture_output=True, text=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "inconclusive"
    out = (r.stdout + "\n" + r.stderr).lower()
    if any(m in out for m in UNAVAILABLE_MARKERS):
        return "unavailable"
    if r.returncode == 0 and out.strip():
        return "available"
    return "inconclusive"


def current_model(path):
    lines = path.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = MODEL_LINE.match(line)
        if m:
            return m.group(3).strip()
    return None


def set_model(path, new_val):
    lines = path.read_text().splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return False
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            break
        m = MODEL_LINE.match(line)
        if m:
            if m.group(3).strip() == new_val:
                return False
            # group(4) already captures the line's trailing newline (\s includes
            # \n, greedy to $) — do NOT append another, or every rewrite inserts a
            # stray blank line. Mirrors apply_model_remap.py exactly.
            lines[i] = f'{m.group(1)}"{new_val}"{m.group(4)}'
            path.write_text("".join(lines))
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agents-dir", required=True, help="Dir of assembled .claude agent *.md files.")
    ap.add_argument("--config", required=True, help="Path to model_heal config.json.")
    ap.add_argument("--timeout", type=int, default=60, help="Per-probe timeout (s).")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    def log(msg):
        if not args.quiet:
            print(f"[model-heal] {msg}", file=sys.stderr)

    adir = Path(args.agents_dir)
    cfgp = Path(args.config)
    if not adir.is_dir() or not cfgp.is_file():
        log(f"skip: missing agents dir ({adir}) or config ({cfgp})")
        return 0  # never block a launch

    try:
        cfg = json.loads(cfgp.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log(f"skip: unreadable config {cfgp}: {e}")
        return 0  # never block a launch on a bad config
    ideals = cfg.get("agents", {})
    fallbacks = cfg.get("fallbacks", {})

    status = {}  # model -> availability (one probe per distinct model)

    def avail(model):
        if model not in status:
            status[model] = probe(model, args.timeout)
        return status[model]

    def desired_model(ideal, cur):
        """The tier this agent should be on, given live availability.

        Only ever moves to a CONFIRMED-available tier; anything less than a
        confirmed verdict leaves the current pin in place. In particular an
        *inconclusive* probe of the ideal (CLI missing, timeout, network) returns
        `cur` — it must NOT be treated as 'unavailable' and trigger a downgrade
        (matches resolve_model_fallbacks.py's keep-on-inconclusive rule)."""
        s = avail(ideal)
        if s == "available":
            return ideal                       # restore / keep the ideal
        if s != "unavailable":
            return cur                         # inconclusive -> leave untouched
        for cand in fallbacks.get(ideal, []):  # ideal CONFIRMED down: fall back
            if avail(cand) == "available":      # only to a confirmed-available tier
                return cand
        return cur                             # nothing confirmed-available -> keep

    changed = restored = downgraded = 0
    for p in sorted(adir.glob("*.md")):
        try:
            ideal = ideals.get(p.stem)
            if not ideal:
                continue  # agent not tracked (no recorded first choice) — leave as-is
            cur = current_model(p)
            target = desired_model(ideal, cur)
            if target == cur:
                continue  # already correct, or nothing confirmed-available to move to
            if set_model(p, target):
                changed += 1
                if target == ideal:
                    restored += 1
                    log(f"{p.stem}: {cur} -> {target} (ideal restored)")
                else:
                    downgraded += 1
                    log(f"{p.stem}: {cur} -> {target} ({ideal} unavailable, fell back)")
        except Exception as e:  # incl. UnicodeDecodeError (a ValueError, not OSError)
            log(f"{p.name}: skipped (unreadable/odd): {e}")  # never abort the loop

    if changed:
        log(f"{changed} agent(s) repinned ({restored} restored to ideal, {downgraded} fell back)")
    else:
        log("all agents already on their best available tier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
