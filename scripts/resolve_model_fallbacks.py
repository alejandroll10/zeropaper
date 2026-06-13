#!/usr/bin/env python3
"""Resolve unavailable Claude subagent models to available fallbacks at setup time.

Scans the agent metadata JSON files for distinct top-level `model` values, probes
each for availability using the *same* `claude` CLI that will run the agents
(runtime-accurate: an API-key probe can disagree with the CLI's account access),
and for any unavailable model walks its fallback chain (templates/model_fallbacks.json)
to the first available model.

Emits one `ideal=resolved` line per REMAPPED model to stdout (consumed by setup.sh).
Human-readable progress goes to stderr. Models that are available, or unavailable
with no available fallback, produce no stdout line (the latter logs a WARNING).

Probing is by output content, not exit code: the suspended-model message
("... is currently unavailable") returns rc=0, so we match markers in the output.

Scope: Claude models only. Codex (gpt-5.5) and Gemini (gemini-3-preview) subagent
models are a different provider/CLI and are not probed here.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Lowercased substrings that mean "this model is not usable on this account".
# Kept deliberately specific to provider/status phrasing — generic phrases like
# "do not have access" are excluded because a chatty-but-available model could
# emit them (e.g. "I don't have access to the internet, but here's: ok") and get
# falsely downgraded. The known-unavailable safety list is the backstop for any
# suspension whose message isn't matched here.
UNAVAILABLE_MARKERS = [
    "is currently unavailable",   # the Fable/Mythos suspension message (rc=0)
    "fable-mythos-access",        # URL in that message
    "model not found",
    "unknown model",
    "invalid model",
]

PROBE_PROMPT = "Reply with exactly: ok"


def probe(model, timeout):
    """Return 'available' | 'unavailable' | 'inconclusive'."""
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", model],
            input=PROBE_PROMPT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return "inconclusive"  # claude CLI not on PATH
    except subprocess.TimeoutExpired:
        return "inconclusive"
    out = (r.stdout + "\n" + r.stderr).lower()
    if any(m in out for m in UNAVAILABLE_MARKERS):
        return "unavailable"
    if r.returncode == 0 and out.strip():
        return "available"
    return "inconclusive"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", action="append", default=[],
                    help="Agent metadata JSON file(s) to scan for `model` values. Repeatable.")
    ap.add_argument("--fallbacks", required=True, help="Path to model_fallbacks.json")
    ap.add_argument("--known-unavailable", default="",
                    help="Comma-separated models treated as unavailable when probing "
                         "is off or inconclusive (safety net for known suspensions).")
    ap.add_argument("--no-probe", action="store_true",
                    help="Skip the live claude-CLI probe; rely on --known-unavailable only.")
    ap.add_argument("--timeout", type=int, default=120, help="Per-probe timeout (s).")
    ap.add_argument("--extra-model", action="append", default=[],
                    help="Additional model string(s) to consider (e.g. a --light override).")
    args = ap.parse_args()

    fallbacks = json.loads(Path(args.fallbacks).read_text())
    known_unavail = {m.strip() for m in args.known_unavailable.split(",") if m.strip()}

    # Collect the distinct set of models referenced in metadata.
    models = set(m for m in args.extra_model if m)
    for mf in args.metadata:
        p = Path(mf)
        if not p.exists():
            continue
        try:
            md = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"[model-probe] WARN: could not read {mf}: {e}", file=sys.stderr)
            continue
        for agent in md.values():
            if isinstance(agent, dict) and agent.get("model"):
                models.add(agent["model"])

    status = {}  # model -> availability, cached so each model is probed at most once

    def availability(model):
        if model in status:
            return status[model]
        if args.no_probe:
            s = "unavailable" if model in known_unavail else "inconclusive"
        else:
            s = probe(model, args.timeout)
            # A flaky/inconclusive probe still downgrades a model we KNOW is suspended.
            if s == "inconclusive" and model in known_unavail:
                s = "unavailable"
        status[model] = s
        return s

    remaps = {}
    for model in sorted(models):
        s = availability(model)
        if s == "available":
            continue
        if s == "inconclusive":
            print(f"[model-probe] {model}: inconclusive (not in known-unavailable) — keeping",
                  file=sys.stderr)
            continue
        # unavailable -> walk the chain to the first candidate that is not itself
        # unavailable. Under live probing this is normally a confirmed-available
        # model; under --no-probe (or a flaky probe) an "inconclusive" candidate
        # is accepted optimistically, since the alternative is leaving the
        # known-broken model pinned.
        chain = fallbacks.get(model, [])
        chosen = next((c for c in chain if availability(c) != "unavailable"), None)
        if chosen:
            remaps[model] = chosen
            print(f"[model-probe] {model} UNAVAILABLE -> remapping to {chosen}", file=sys.stderr)
        else:
            print(f"[model-probe] WARNING: {model} unavailable and no available fallback "
                  f"in chain {chain or '[]'} — leaving pinned (agents using it will fail)",
                  file=sys.stderr)

    for k, v in remaps.items():
        print(f"{k}={v}")


if __name__ == "__main__":
    main()
