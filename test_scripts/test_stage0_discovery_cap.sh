#!/usr/bin/env bash
# Stage 0's open domain space has a numeric runaway guard whose terminal route
# stays autonomous. This is a prompt/state contract, so exercise the assembled
# artifacts every runtime consumes rather than only the source fragments.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd -P)"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
project="$scratch/project"
empirical_project="$scratch/empirical-project"

env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$project" \
    --assemble-only --no-model-probe --variant finance \
    >"$scratch/setup.log" 2>&1
env PATH=/usr/bin:/bin "$repo_root/setup.sh" "$empirical_project" \
    --assemble-only --no-model-probe --variant finance --mode empirical-first \
    >"$scratch/empirical-setup.log" 2>&1

jq -e '
    .loops.stage0_discovery == {"round": 0, "cap": 100}
    and .stage0_discovery_last_counted_attempt == null
    and .stage0_discovery_episode_start_attempt == null
    and .stage0_discovery_phase == "entry"
    and .stage0_discovery_step == null
    and .stage0_discovery_cap_context == null
    and .stage0_discovery_pending_scan == null
    and .stage0_discovery_gap_serial == 0
    and .stage0_discovery_active_gap_id == null
' \
    "$project/process_log/pipeline_state.json" >/dev/null \
    || { echo "FAIL: assembled state omitted the Stage-0 discovery cap/idempotency marker" >&2; exit 1; }

stage_doc="$project/docs/stage_0.md"
grep -Fq 'applies to **unseeded discovery**' "$stage_doc" \
    || { echo "FAIL: Stage-0 cap does not state its seeded/faithful scope" >&2; exit 1; }
grep -Fq 'regardless of the domain' "$stage_doc" \
    || { echo "FAIL: broad-scan counter still depends on domain identity" >&2; exit 1; }
grep -Fq 'both re-scan verdicts are forbidden' "$stage_doc" \
    || { echo "FAIL: Stage 0 cap does not force autonomous promotion" >&2; exit 1; }
grep -Fq 'Do not reset the run-global' "$stage_doc" \
    || { echo "FAIL: successful Stage-0 exit resets the run-global discovery budget" >&2; exit 1; }
grep -Fq 'increment `loops.stage0_discovery.round`' "$stage_doc" \
    || { echo "FAIL: Stage 0 does not charge each broad scan" >&2; exit 1; }
grep -Fq 'Before launching the agent' "$stage_doc" \
    || { echo "FAIL: broad scans are not charged before launch" >&2; exit 1; }
grep -Fq 'Durable resume guard (evaluate before any entry reset)' "$stage_doc" \
    || { echo "FAIL: crash/update resume can clear or duplicate a charged scan" >&2; exit 1; }
for phase in entry_initializing scan_charged gap_search promotion cap_routing; do
    grep -Fq "\`$phase\`" "$stage_doc" \
        || { echo "FAIL: Stage-0 resume contract omits $phase" >&2; exit 1; }
done
for step in select characterize pose review route; do
    grep -Fq "\`$step\`" "$stage_doc" \
        || { echo "FAIL: Stage-0 resume contract omits durable $step substep" >&2; exit 1; }
done
grep -Fq 'Never re-launch under the old permit.' "$stage_doc" \
    || { echo "FAIL: crash retry can reuse a consumed broad-scout permit" >&2; exit 1; }
grep -Fq 'A crash retry reaches the same phase through the `incomplete_scan` context' "$stage_doc" \
    || { echo "FAIL: crash retry bypasses the physical-launch cap" >&2; exit 1; }
grep -Fq 'mere existence never advances the step' "$stage_doc" \
    || { echo "FAIL: stale canonical artifacts can skip promotion work" >&2; exit 1; }
grep -Fq 'atomically rename that staging file to final' "$stage_doc" \
    || { echo "FAIL: partial broad-map files can masquerade as completed scans" >&2; exit 1; }
grep -Fq 'replacing an incomplete/mismatched A record rather than allocating or appending another' "$stage_doc" \
    || { echo "FAIL: crash reconciliation can duplicate a gap outcome" >&2; exit 1; }
grep -Fq 'a published episode marker can never coexist with a stale prior-episode portfolio' "$stage_doc" \
    || { echo "FAIL: new-episode crash can preserve the prior near-miss portfolio" >&2; exit 1; }
for session_doc in \
    "$project/docs/start_session_claude.md" \
    "$project/docs/start_session_codex.md" \
    "$project/docs/start_session_gemini.md"
do
    grep -Fq 'never directly re-launch an unseeded Stage 0 `literature-scout`' "$session_doc" \
        || { echo "FAIL: $(basename "$session_doc") stall recovery can bypass the Stage-0 launch permit" >&2; exit 1; }
    grep -Fq 'return through the Stage 0 scan_charged resume guard' "$session_doc" \
        || { echo "FAIL: $(basename "$session_doc") hourly loop can bypass the Stage-0 launch permit" >&2; exit 1; }
    grep -Fq 'a dispatch failure spends its committed physical-launch permit' "$session_doc" \
        || { echo "FAIL: $(basename "$session_doc") model fallback can bypass the Stage-0 launch permit" >&2; exit 1; }
done
grep -Fq 'neither tier fallback nor transient retry is a direct relaunch' \
    "$project/docs/model_fallback.md" \
    || { echo "FAIL: shared model fallback can bypass the Stage-0 launch permit" >&2; exit 1; }
for context in downstream_return incomplete_scan; do
    grep -Fq "\`$context\`" "$stage_doc" \
        || { echo "FAIL: Stage-0 cap routing omits $context" >&2; exit 1; }
    grep -Fq "\`$context\`" "$project/.claude/agents/branch-manager.md" \
        || { echo "FAIL: branch-manager cap contract omits $context" >&2; exit 1; }
done
if grep -Eq 'legacy_reroute|legacy_update' \
    "$stage_doc" "$project/.claude/agents/branch-manager.md"; then
    echo "FAIL: removed updater-only Stage-0 compatibility routes still ship" >&2
    exit 1
fi
grep -Fq 'preserve the pending payload' "$stage_doc" \
    || { echo "FAIL: permit-100 crash discards its only scan instruction" >&2; exit 1; }
grep -Fq 'never launch scan 101' "$stage_doc" \
    || { echo "FAIL: a later Stage-0 return can exceed the run-global scan cap" >&2; exit 1; }
grep -Fq 'REJECT takes the best scored snapshot directly to Stage 1' \
    "$project/.claude/agents/branch-manager.md" \
    || { echo "FAIL: no-scan promotion can fall back into nonexistent broad-gap search" >&2; exit 1; }
grep -Fq 'promotion REJECT (including a REVISE-cap conversion) does not increment `loops.gate0_reject`' \
    "$stage_doc" \
    || { echo "FAIL: promotion REJECT falls through the ordinary gap-routing table" >&2; exit 1; }
grep -Fq 'on REJECT (including a REVISE-cap conversion), first restore `output/stage0/best_question.md`' \
    "$stage_doc" \
    || { echo "FAIL: promotion REJECT does not restore the best snapshot for Stage 1" >&2; exit 1; }
grep -Fq 'set `stage0_discovery_last_counted_attempt`, `stage0_discovery_episode_start_attempt`, and `stage0_discovery_active_gap_id` to `null`' \
    "$stage_doc" \
    || { echo "FAIL: Stage-0 handoff leaves transient ownership state behind" >&2; exit 1; }
grep -Fq 'only this episode' "$stage_doc" \
    || { echo "FAIL: promotion inputs are not scoped to the current discovery episode" >&2; exit 1; }
grep -Fq 'discovery_e{E}/literature_map_broad_p*.md' "$stage_doc" \
    || { echo "FAIL: broad-map archives are not episode-scoped" >&2; exit 1; }

for agent in \
    "$project/.claude/agents/branch-manager.md" \
    "$project/.codex/agents/branch-manager.toml" \
    "$project/.gemini/agents/branch-manager.md" \
    "$project/.grok/agents/branch-manager.md" \
    "$project/.opencode/agents/branch-manager.md"
do
    grep -Fq 'The numeric budget is binding and domain-name-independent.' "$agent" \
        || { echo "FAIL: $(basename "$agent") omitted the domain-independent cap" >&2; exit 1; }
    grep -Fq 'PROMOTE-NEAR-MISS' "$agent" \
        || { echo "FAIL: $(basename "$agent") omitted autonomous near-miss promotion" >&2; exit 1; }
done
if [ "$(grep -Fc 'set `current_stage = "stage_1"`' "$stage_doc")" -ne 4 ]; then
    echo "FAIL: every Stage-0 handoff must atomically publish current_stage=stage_1" >&2
    exit 1
fi
if [ "$(grep -Fc 'never resume or directly relaunch an unseeded Stage 0 literature-scout' "$project/launch.sh")" -ne 2 ]; then
    echo "FAIL: OpenCode recovery can bypass the Stage-0 launch permit" >&2
    exit 1
fi

stage1_doc="$project/docs/stage_1.md"
[ "$(grep -ci 'increment `problem_attempt`.*return to Stage 0' "$stage1_doc")" -eq 3 ] \
    || { echo "FAIL: not every Stage-1-to-Stage-0 route creates a unique discovery episode" >&2; exit 1; }
grep -Fq 'except `loops.stage0_discovery.round`' "$stage1_doc" \
    || { echo "FAIL: regeneration reopens the run-global broad-scan budget" >&2; exit 1; }
stage4_doc="$project/docs/stage_4.md"
stage6_doc="$project/docs/stage_6.md"
grep -Fq 'preserving run-global `loops.stage0_discovery.round`' "$stage4_doc" \
    || { echo "FAIL: Gate-4 regeneration resets the broad-scan budget" >&2; exit 1; }
grep -Fq 'preserving run-global `loops.stage0_discovery.round`' "$stage6_doc" \
    || { echo "FAIL: Gate-5 regeneration resets the broad-scan budget" >&2; exit 1; }
grep -Fq 'Unseeded theory scored ABANDON | 5 theories on same problem | Increment `problem_attempt`' \
    "$project/CLAUDE.md" \
    || { echo "FAIL: Gate-4 abandonment reuses the failed problem namespace" >&2; exit 1; }
empirical_stage1_doc="$empirical_project/docs/stage_1.md"
grep -Fq 'REENTER-STAGE-0' "$empirical_stage1_doc" \
    || { echo "FAIL: empirical-first Stage-0 return disappeared" >&2; exit 1; }
grep -Fq 'REENTER-STAGE-0**: the data inventory is the bottleneck. Set `current_stage = "stage_0"`. Increment `problem_attempt`' "$empirical_stage1_doc" \
    || { echo "FAIL: empirical-first Stage-0 return does not create a unique episode" >&2; exit 1; }
puzzle_doc="$project/docs/stage_puzzle_triage.md"
grep -Fq 'return to Stage 0 with the failure notes (also increment `problem_attempt`)' "$puzzle_doc" \
    || { echo "FAIL: puzzle-triage Stage-0 return does not create a unique episode" >&2; exit 1; }

# The orchestrator is prompt-driven, so validate the transition ordering in the
# assembled contract and model the adversarial trajectory that originally
# escaped the cap: every scan scores, Stage 1 repeatedly returns, and a
# regeneration occurs in between.
python3 -I - "$stage_doc" "$stage1_doc" "$stage4_doc" "$stage6_doc" <<'PY'
from pathlib import Path
import sys

stage0, stage1, stage4, stage6 = (Path(p).read_text(encoding="utf-8") for p in sys.argv[1:])
cap_check = stage0.index("Binding pre-scan cap check")
step0a = stage0.index("## Step 0a")
step0b = stage0.index("## Step 0b")
charge = stage0.index("increment `loops.stage0_discovery.round`", step0a, step0b)
launch = stage0.index("Launch literature-scout", step0a, step0b)
if not cap_check < step0a < charge < launch < step0b:
    raise SystemExit("FAIL: Stage-0 cap/charge/launch ordering is not fail-closed")
if "increment `loops.stage0_discovery.round`" in stage0[step0b:]:
    raise SystemExit("FAIL: discovery budget is charged only on an outcome-specific route")
if "whether that scan eventually exhausted here or produced a scored question" not in stage0:
    raise SystemExit("FAIL: scored-question scans can evade the global budget")
for doc, label in ((stage1, "canonical"), (stage4, "Gate 4"), (stage6, "Gate 5")):
    if "stage0_discovery.round" not in doc:
        raise SystemExit(f"FAIL: {label} regeneration omits the run-global exception")

rounds = 0
cap = 100
physical_launches = 0
for attempt in range(1, 101):
    if rounds >= cap:
        raise SystemExit("FAIL: model bound before scan 100")
    rounds += 1  # pre-launch permit, independent of scan outcome
    physical_launches += 1
    if attempt == 50:
        audit_loops = {"stage0_discovery": rounds, "referee": 7}
        for key in tuple(audit_loops):
            if key != "stage0_discovery":
                audit_loops[key] = 0
        rounds = audit_loops["stage0_discovery"]
if rounds != cap:
    raise SystemExit("FAIL: model did not consume exactly 100 scans")
can_launch_101 = rounds < cap
if can_launch_101:
    raise SystemExit("FAIL: adversarial scored-question trajectory permits scan 101")

# A lost result consumes its permit. At the boundary, resume must promote
# without physically retrying; below it, a retry receives a new permit.
rounds = 98
physical_launches = 98
rounds += 1
physical_launches += 1  # permit 99 launches, then crashes before durable output
if rounds >= cap:
    raise SystemExit("FAIL: model reached cap too early")
rounds += 1  # retry gets permit 100 before launch
physical_launches += 1
if rounds < cap or physical_launches != 100:
    raise SystemExit("FAIL: crash retry did not consume a distinct permit")
retry_after_second_crash = rounds < cap
if retry_after_second_crash:
    physical_launches += 1
if physical_launches > cap:
    raise SystemExit("FAIL: crash trajectory permits physical broad-scout launch 101")
PY

if grep -q 'halted_no_viable_question' \
    "$project/CLAUDE.md" "$project/AGENTS.md" "$project/GEMINI.md" \
    "$project/docs/stage_0.md"; then
    echo "FAIL: assembled Stage-0/runtime contract still exposes the retired human halt" >&2
    exit 1
fi

# The Stage-0 section itself must not retain OPERATOR-ESCALATE. The same agent
# legitimately uses that verdict for empirical-first's no-identification route,
# so scope the negative assertion to the discovery-exhausted section.
python3 -I - "$project/.claude/agents/branch-manager.md" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
section = text.split("## Stage 0 discovery-exhausted report", 1)[1]
if "OPERATOR-ESCALATE" in section:
    raise SystemExit("FAIL: Stage-0 branch-manager route still returns ordinary discovery to a human")
if "round >= cap" not in section or "global termination guarantee" not in section:
    raise SystemExit("FAIL: Stage-0 branch-manager cap is not an unconditional terminal route")
PY

echo "PASS: Stage-0 discovery cap is domain-independent and autonomously promotes a near miss"
