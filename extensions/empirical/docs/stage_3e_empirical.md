# Stage 3e: Empirical Analysis (Gate 3b + Full Analysis)

## Gate 3b: Empirical Feasibility (falsify-first)

Quick falsification check: can this theory be calibrated at all? Do the key empirical moments exist? A theory that predicts the wrong sign on a well-measured moment is dead regardless of how elegant the implications are. Check this BEFORE investing in implications.

1. Launch `empiricist` with a focused instruction: "Quick feasibility check only — download the 2-3 key moments this theory needs to match. Report whether the theory's predictions are in the right ballpark. Do NOT run a full analysis."
2. Save to `output/stage3b/empirical_feasibility.md`
3. If the key moments contradict the theory (wrong sign, off by an order of magnitude): flag as **FALSIFIED** — return to Stage 1 for a new idea. Don't waste time on implications for a theory the data already rejects.
4. If moments are roughly consistent or unavailable: proceed to Stage 3.
5. Commit: `artifact: empirical feasibility — {OK/FALSIFIED}`

## Stage 3e: Full Empirical Analysis

This is the full empirical analysis — deeper than the feasibility check at Gate 3b. Now that implications are developed, the empiricist can design proper tests, calibrations, and portfolio sorts.

1. **Analysis plan.** Launch `empiricist` with instruction: "Write an analysis plan only — do not execute yet." The empiricist reads the theory, implications, data inventory, and feasibility results, then writes `output/stage3b/empirical_plan.md` describing: what tests to run, what data sources to use (and WHY those sources — reference the data inventory), what the expected results look like, and what would constitute support vs. rejection of the theory.
2. **Review the plan.** Read the plan. Check: does it use the best available data? (If WRDS is available but the plan uses only CZ portfolios, reject the plan.) Does it test what the theory actually predicts? Is the identification strategy sound? If the plan is wrong, re-launch the empiricist with specific feedback.
3. **Execute.** Launch `empiricist` with the approved plan. The agent executes the plan, fetches data via skills (FRED, Ken French, Chen-Zimmerman, WRDS, EDGAR), and runs the analysis. Saves to `output/stage3b/empirical_analysis.md` and `code/empirical.py`.
4. All code must be written to files (`code/` for final, `code/tmp/` for scratch). Never run inline `python3 -c`.
5. **Empirics audit.** Launch `empirics-auditor` on the empirical analysis + code + theory draft. The auditor runs the code, verifies results, checks methodology.
   - If **PASS**: proceed to Stage 4. Self-attacker and scorer receive empirical results alongside the theory.
   - If **FAIL**: re-launch `empiricist` with the audit feedback. Keep iterating as long as the number of issues is decreasing. Escalate only if the issue count plateaus or increases across two consecutive attempts.
6. Commit: `artifact: empirics audit — {PASS/FAIL}`
