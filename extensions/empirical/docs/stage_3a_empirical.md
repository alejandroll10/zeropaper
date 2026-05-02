# Stage 3a: Empirical Analysis

This file covers two sub-stages: **Gate 3a-feasibility** (empirical feasibility, runs *before* Stage 3 implications) and **Stage 3a** (full empirical analysis, runs *after* Stage 3 implications). In `pipeline_state.json`, use `"stage_3a_feasibility"` during feasibility and `"stage_3a"` during full analysis.

## Preflight: data-source liveness (before any `empiricist` launch in this stage)

`start_services.sh` ran once at session start and produced `output/data_inventory.md`, but a long Stage 2 iteration may have outlived the WRDS session. Before each `empiricist` launch in this stage (Gate 3a-feasibility, Stage 3a plan, Stage 3a execute, and any re-fire), the orchestrator must verify the WRDS server is still reachable:

```bash
PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; exit(0 if wrds_ping() else 1)"
```

If the ping returns False, attempt one restart with `bash code/utils/start_services.sh`. If that also fails, halt the stage by setting `pipeline_state.json:status = "halted_wrds_unreachable"` rather than launching the empiricist into a stack of failed queries — re-run when access is restored. This preflight is cheap (sub-second when healthy) and prevents the most common silent stall in empirical runs. The same rule applies to the FIX-EMPIRICS empiricist re-launch in `docs/stage_puzzle_triage.md`, the Stage 6 Reject re-fire in `docs/stage_6.md` (which routes through this stage's "Re-fire on theory revision" section), and any future empiricist launch site.

## Gate 3a-feasibility: Empirical Feasibility (falsify-first)

Quick falsification check: can this theory be calibrated at all? Do the key empirical moments exist? A theory that predicts the wrong sign on a well-measured moment is dead regardless of how elegant the implications are. Check this BEFORE investing in implications.

1. Launch `empiricist` with a focused instruction: "Quick feasibility check only — download the 2-3 key moments this theory needs to match. Report whether the theory's predictions are in the right ballpark. Do NOT run a full analysis."
2. Save to `output/stage3a/empirical_feasibility.md`
3. If the key moments contradict the theory (wrong sign, off by an order of magnitude): flag as **FALSIFIED** — increment `theory_attempt` and reset `theory_version` to 1, then return to Stage 1 for a new idea (the theory is dead; counter must advance so the "5 theories on same problem → Stage 0" escalation rule in core.md fires correctly). Don't waste time on implications for a theory the data already rejects.

{{SEED_OVERRIDE_STAGE_3A_FALSIFIED}}
4. If moments are roughly consistent or unavailable: proceed to Stage 3.
5. Commit: `artifact: empirical feasibility — {OK/FALSIFIED}`

## Stage 3a: Full Empirical Analysis

This is the full empirical analysis — deeper than the feasibility check at Gate 3a-feasibility. Now that implications are developed, the empiricist can design proper tests, calibrations, and portfolio sorts.

1. **Analysis plan.** Launch `empiricist` with instruction: "Write an analysis plan only — do not execute yet." The empiricist reads the theory, implications, data inventory, and feasibility results, then writes `output/stage3a/empirical_plan.md` describing: what tests to run, what data sources to use (and WHY those sources — reference the data inventory), what the expected results look like, and what would constitute support vs. rejection of the theory. The plan MUST include a **proxy–theory mapping** section: for each empirical proxy, state (a) which theoretical object it is standing in for, (b) which sub-class / mechanism / scope condition it captures (if the theory has heterogeneous agent types, scope-conditional predictions, or multiple mechanisms), (c) whether the proxy construction is mechanically correlated with the theoretical object (e.g., HHI as proxy for concentration-driven noise variance is mechanical; tracking-error is not), and (d) a non-mechanical alternative proxy. If the theory has multiple sub-classes, the plan must include **at least one proxy per sub-class in the primary analysis** — not deferred to robustness. If the main proxy is mechanically correlated with its theoretical object, the non-mechanical alternative is mandatory in the primary analysis as well.
2. **Review the plan.** Read the plan. Check: does it use the best available data? (If WRDS is available but the plan uses only CZ portfolios, reject the plan.) Does it test what the theory actually predicts? Is the identification strategy sound? **Does every theoretical sub-class have at least one empirical proxy in the primary analysis?** If the plan is wrong, re-launch the empiricist with specific feedback.
3. **Execute.** Launch `empiricist` with the approved plan. The agent executes the plan, fetches data via skills (FRED, Ken French, Chen-Zimmerman, WRDS, EDGAR), and runs the analysis. Saves to `output/stage3a/empirical_analysis.md` and `code/empirical.py`.
4. All code must be written to files (`code/` for final, `code/tmp/` for scratch). Never run inline `python3 -c`.
5. **Empirics audit.** Launch `empirics-auditor` on the empirical analysis + code + theory draft. The auditor runs the code, verifies results, checks methodology.
   - If **PASS**: proceed to **puzzle-triage entry check** (next step).
   - If **FAIL**: re-launch `empiricist` with the audit feedback. Keep iterating as long as the number of issues is decreasing. **Hard cap: 5 audit-fix attempts total.** Escalate if the issue count plateaus or increases across two consecutive attempts, OR if 5 attempts have been made. Escalation treats the empirical analysis as failed for this theory version → return to Stage 2 with the audit notes as input to theory-generator (the theory may be untestable as written).
6. Commit: `artifact: empirics audit — {PASS/FAIL}`

## Puzzle-triage entry check (mandatory after empirics-auditor PASS)

Before proceeding to Stage 4, you must check whether the empirical results contradict any prediction in `output/stage3/implications.md`.

1. Read `output/stage3/implications.md` and identify which implications were tested.
2. Read `output/stage3a/empirical_analysis.md` and the auditor's verification.
3. For each tested implication: did the data contradict it (sign reversal, magnitude outside the predicted range, condition that should hold but failed)?
4. Write `output/stage3a/contradiction_check.md` with one of:
   - **NONE** — empirics confirm or are silent on every tested implication. Proceed to Stage 4.
   - **CONTRADICTIONS FOUND** — list the contradicted implications and what the data shows. **Proceed to puzzle triage** (`docs/stage_puzzle_triage.md`), not Stage 4.
5. Commit: `artifact: contradiction check — {NONE/CONTRADICTIONS FOUND}`

This step is mandatory and may not be skipped — silently jumping to Stage 4 after empirics PASS bypasses the puzzle-pivot mechanism that exists to extract value from theory-empirics disagreements.

## Re-fire on theory revision

Stage 3a is not one-shot. When the theory revises after the first 3a pass — Gate 3 INCREMENTAL rework, Gate 4 REVISE→Stage 2, Stage 6 Major Revision triggering theory-generator work, or any substantive content change — the original `empirical_analysis.md` becomes stale relative to the current theory. The empiricist must re-run on the revised content before Gate 4 can advance again.

**Trigger.** Any of:
- `theory_version` advances and `stage3a_theory_version < theory_version`.
- `implications.md` is overwritten (Gate 3 INCREMENTAL rework, PIVOT, or any path that re-runs Stage 3) and the new file contains NOVEL or PUZZLE-CANDIDATE implications not present in the prior version.
- A referee identifies an empirical gap that wasn't addressed in the first 3a pass (e.g., "this prediction was deferred" or "the identification doesn't address X").
- Stage 6 Reject verdict triggers a deepen directive (see `docs/stage_6.md` Reject row): the deepen directive's empirics requirements become the focus of the re-fire.

**Procedure.**
1. Launch `empiricist` with: the revised theory, the current `implications.md`, the prior `empirical_analysis.md` (so the agent knows what's already been tested), and a focused instruction listing the specific new content to test.
2. Save targeted re-runs to `output/stage3a/empirical_analysis_vN.md` where N is the current `theory_version`. **Do not overwrite the original `empirical_analysis.md`** — combined coverage across files must span the version that will be written into the paper.
3. Run `empirics-auditor` on the new analysis (same audit-fix loop as the first pass; same 5-attempt cap).
4. **Re-run the puzzle-triage entry check** (above) on the combined evidence — a new contradiction triggers puzzle-triage as it would on the first pass.
5. On audit PASS and contradiction-check complete, set `pipeline_state.json:stage3a_theory_version = theory_version`.

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `stage3a_theory_version == theory_version`. Stale empirics are a hard block, parallel to the `stage2b_theory_version` rule for theory-explorer.

**Cap.** No hard cap on re-fires per problem — the constraint is the never-abandon rule plus the existing 10-round referee cap and the 8-evaluation hard ceiling. But re-fires that do not surface new evidence (auditor PASS with no new findings, no contradiction-check change) count toward the plateau-detection logic in Gate 4 (see `docs/stage_4.md`).
