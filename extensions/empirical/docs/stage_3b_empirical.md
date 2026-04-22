# Stage 3b/3e: Empirical Analysis

This file covers two sub-stages: **Gate 3b** (empirical feasibility, runs *before* Stage 3 implications) and **Stage 3e** (full empirical analysis, runs *after* Stage 3 implications). In `pipeline_state.json`, use `"stage_3b"` during feasibility and `"stage_3e"` during full analysis.

## Gate 3b: Empirical Feasibility (falsify-first)

Quick falsification check: can this theory be calibrated at all? Do the key empirical moments exist? A theory that predicts the wrong sign on a well-measured moment is dead regardless of how elegant the implications are. Check this BEFORE investing in implications.

1. Launch `empiricist` with a focused instruction: "Quick feasibility check only — download the 2-3 key moments this theory needs to match. Report whether the theory's predictions are in the right ballpark. Do NOT run a full analysis."
2. Save to `output/stage3b/empirical_feasibility.md`
3. If the key moments contradict the theory (wrong sign, off by an order of magnitude): flag as **FALSIFIED** — increment `theory_attempt` and reset `theory_version` to 1, then return to Stage 1 for a new idea (the theory is dead; counter must advance so the "5 theories on same problem → Stage 0" escalation rule in core.md fires correctly). Don't waste time on implications for a theory the data already rejects.

{{SEED_OVERRIDE_STAGE_3B_FALSIFIED}}
4. If moments are roughly consistent or unavailable: proceed to Stage 3.
5. Commit: `artifact: empirical feasibility — {OK/FALSIFIED}`

## Stage 3e: Full Empirical Analysis

This is the full empirical analysis — deeper than the feasibility check at Gate 3b. Now that implications are developed, the empiricist can design proper tests, calibrations, and portfolio sorts.

1. **Analysis plan.** Launch `empiricist` with instruction: "Write an analysis plan only — do not execute yet." The empiricist reads the theory, implications, data inventory, and feasibility results, then writes `output/stage3b/empirical_plan.md` describing: what tests to run, what data sources to use (and WHY those sources — reference the data inventory), what the expected results look like, and what would constitute support vs. rejection of the theory. The plan MUST include a **proxy–theory mapping** section: for each empirical proxy, state (a) which theoretical object it is standing in for, (b) which sub-class / mechanism / scope condition it captures (if the theory has heterogeneous agent types, scope-conditional predictions, or multiple mechanisms), (c) whether the proxy construction is mechanically correlated with the theoretical object (e.g., HHI as proxy for concentration-driven noise variance is mechanical; tracking-error is not), and (d) a non-mechanical alternative proxy. If the theory has multiple sub-classes, the plan must include **at least one proxy per sub-class in the primary analysis** — not deferred to robustness. If the main proxy is mechanically correlated with its theoretical object, the non-mechanical alternative is mandatory in the primary analysis as well.
2. **Review the plan.** Read the plan. Check: does it use the best available data? (If WRDS is available but the plan uses only CZ portfolios, reject the plan.) Does it test what the theory actually predicts? Is the identification strategy sound? **Does every theoretical sub-class have at least one empirical proxy in the primary analysis?** If the plan is wrong, re-launch the empiricist with specific feedback.
3. **Execute.** Launch `empiricist` with the approved plan. The agent executes the plan, fetches data via skills (FRED, Ken French, Chen-Zimmerman, WRDS, EDGAR), and runs the analysis. Saves to `output/stage3b/empirical_analysis.md` and `code/empirical.py`.
4. All code must be written to files (`code/` for final, `code/tmp/` for scratch). Never run inline `python3 -c`.
5. **Empirics audit.** Launch `empirics-auditor` on the empirical analysis + code + theory draft. The auditor runs the code, verifies results, checks methodology.
   - If **PASS**: proceed to **puzzle-triage entry check** (next step).
   - If **FAIL**: re-launch `empiricist` with the audit feedback. Keep iterating as long as the number of issues is decreasing. **Hard cap: 5 audit-fix attempts total.** Escalate if the issue count plateaus or increases across two consecutive attempts, OR if 5 attempts have been made. Escalation treats the empirical analysis as failed for this theory version → return to Stage 2 with the audit notes as input to theory-generator (the theory may be untestable as written).
6. Commit: `artifact: empirics audit — {PASS/FAIL}`

## Puzzle-triage entry check (mandatory after empirics-auditor PASS)

Before proceeding to Stage 4, you must check whether the empirical results contradict any prediction in `output/stage3/implications.md`.

1. Read `output/stage3/implications.md` and identify which implications were tested.
2. Read `output/stage3b/empirical_analysis.md` and the auditor's verification.
3. For each tested implication: did the data contradict it (sign reversal, magnitude outside the predicted range, condition that should hold but failed)?
4. Write `output/stage3b/contradiction_check.md` with one of:
   - **NONE** — empirics confirm or are silent on every tested implication. Proceed to Stage 4.
   - **CONTRADICTIONS FOUND** — list the contradicted implications and what the data shows. **Proceed to puzzle triage** (`docs/stage_puzzle_triage.md`), not Stage 4.
5. Commit: `artifact: contradiction check — {NONE/CONTRADICTIONS FOUND}`

This step is mandatory and may not be skipped — silently jumping to Stage 4 after empirics PASS bypasses the puzzle-pivot mechanism that exists to extract value from theory-empirics disagreements.
