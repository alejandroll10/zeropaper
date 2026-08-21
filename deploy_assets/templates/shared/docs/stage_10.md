# Stage 10: Lessons

**Agents:** none. The orchestrator writes both documents.

This is the final stage. The paper is locked, all polish has stabilized, and Stage 9 has handed off. Before marking the pipeline complete, the orchestrator writes two short reflection documents — one on the paper, one on the pipeline run that produced it.

These are written by the orchestrator, not by a fresh sub-agent, because the orchestrator carries the institutional memory the docs need: which rounds were substantive vs. cosmetic, why each triage decision was made, which agents fired silently, which findings drove which revisions. A fresh agent reading the artifacts retrospectively would miss that thread.

Stage 10 owns the `"status": "complete"` flag. The pipeline is not done until both documents exist and the flag is set.

**Crash recovery.** If a session resumes with `current_stage == "stage_10"` and `status != "complete"`, restart from step 1 of the procedure below. The two documents are short and re-writing them is cheap; do not try to detect partial-write state.

## Procedure

1. **Verify the final evidence receipt before writing or committing anything.** Run `python3 code/utils/results_pipeline/results_pipeline.py verify-paper --receipt process_log/paper_evidence.receipt.json --rerender`. A missing receipt, non-PASS result, or any stale audit/paper/result/renderer byte returns to Stage 9's final evidence checkpoint. Stage 10 cannot repair, waive, or defer this failure.

2. **Write `LESSONS_PAPER.md` at the project root.** Before drafting, read the latest `paper/simulated_referee_reports/editor_decision_r*.md` (highest N) — the editor's "Within-tier outlet recommendation" block names the best-fit outlet within the active tier and is the single most informed within-tier signal you have. Treat it as a strong prior, not a binding choice. Then answer, in your own voice and as honestly as you can:
   - **How do you feel about the paper?**
   - **Did it achieve the desired quality (the target journal tier set in `pipeline_state.json`)?**
   - **If not, which journal(s) would be the best fit? Explain for every tier in this variant's ladder ({{TIER_LIST_INLINE}}, or other if you feel there's a better fit) why the paper would or would not be a good fit at that tier. For the active tier specifically, name the best-fit outlet within that tier (e.g., for finance `top-3-fin`: JF vs. JFE vs. RFS vs. JF Insights & Perspectives if the paper format-fits; for finance `field`: JFQA vs. Review of Finance vs. Management Science; for macro `top-5`: AER vs. Econometrica vs. QJE vs. JPE vs. ReStud vs. AER Insights if the paper format-fits; for llm_cognition `top-ml`: NeurIPS vs. ICML vs. ICLR; for llm_cognition `field`: TMLR vs. ACL vs. EMNLP vs. CogSci — pick one and justify based on word count, exhibit count, single-vs-multi-insight character, and the editor's recommendation if available). For format-constrained outlets (JF Insights & Perspectives ≤7k / single-insight, AER Insights ≤6k / single-mechanism), explicitly check whether the paper format-fits before recommending them.**

   Commit: `lessons: paper reflection`.

3. **Write `LESSONS_PIPELINE.md` at the project root.** Answer:
   - **How do you feel about the pipeline?**
   - **What helped vs. what hurt the paper — keeping cost/time impact separate from quality impact?**

   Commit: `lessons: pipeline reflection`.

4. **Mark complete.** Re-run the exact `verify-paper --rerender` command from step 1 immediately before changing status; this closes changes made while writing lessons or handling completion checks. First also verify `output/stage5/table_legibility.md` exists, is non-empty, and records `VERDICT: PASS` from Stage 9's final-render re-audit; any other/missing verdict returns to Stage 9 step 7 and cannot be recorded as a deferrable verification. Then apply the completion precondition in CLAUDE.md before writing the flag — an unresolved binding row in `process_log/degradation_ledger.md` means the run has not earned a clean `complete`.
   - Clean: `"status": "complete"`. Final commit: `pipeline: COMPLETE — paper ready for submission`.
   - Deferrable outage outstanding (rate/credit limit with a reset horizon, cheap re-check): `"status": "complete_pending_verification"` with the entry recorded in `pending_verification`. Final commit: `pipeline: COMPLETE (pending <core> verification) — paper ready, verification owed`. Say plainly in `LESSONS_PAPER.md` which citations or checks were never verified, so the pending state is legible from the paper's own record and not only from the state file.
   - Anything else unresolved: `"status": "halted_core_bypass"`, per the precondition.

## Notes

Free-form prose. 

- **Honesty over diplomacy.** If the paper plateaued below the target tier, say so and name the tier it does fit. If a polish round did not move quality, say so and name it. Name specific agents and specific findings, not impressions. The audience for `LESSONS_PIPELINE.md` is template maintenance.
