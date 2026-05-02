# Stage 10: Lessons

**Agents:** none. The orchestrator writes both documents.

This is the final stage. The paper is locked, all polish has stabilized, and Stage 9 has handed off. Before marking the pipeline complete, the orchestrator writes two short reflection documents — one on the paper, one on the pipeline run that produced it.

These are written by the orchestrator, not by a fresh sub-agent, because the orchestrator carries the institutional memory the docs need: which rounds were substantive vs. cosmetic, why each triage decision was made, which agents fired silently, which findings drove which revisions. A fresh agent reading the artifacts retrospectively would miss that thread.

Stage 10 owns the `"status": "complete"` flag. The pipeline is not done until both documents exist and the flag is set.

**Crash recovery.** If a session resumes with `current_stage == "stage_10"` and `status != "complete"`, restart from step 1 of the procedure below. The two documents are short and re-writing them is cheap; do not try to detect partial-write state.

## Procedure

1. **Write `LESSONS_PAPER.md` at the project root.** Answer, in your own voice and as honestly as you can:
   - **How do you feel about the paper?**
   - **Did it achieve the desired quality (the target journal tier set in `pipeline_state.json`)?**
   - **If not, which journal would be the best fit?**

   Read the final `paper/main.tex` + `paper/sections/*.tex`, the scorer/branch-manager/referee history, and the polish reports before answering. Be specific — name results, sections, weaknesses by anchor. Vague output ("the paper is reasonable") is not enough; if you cannot say what specifically works and what specifically does not, re-read the artifacts and try again.

   Commit: `lessons: paper reflection`.

2. **Write `LESSONS_PIPELINE.md` at the project root.** Answer:
   - **How do you feel about the pipeline?**
   - **What helped vs. what hurt the paper — keeping cost/time impact separate from quality impact?**

   Read `process_log/pipeline_state.json`, the stage outputs, the triage files, and the commit history before answering. The cost/quality separation is the point: an agent that is slow but high-quality is worth keeping; an agent that is fast but low-quality is not; an agent that is slow *and* low-quality is a kill candidate. Name agents and stages by name and cite specific findings (or specific silent rounds) when making each call.

   Commit: `lessons: pipeline reflection`.

3. **Mark complete.** Update `process_log/pipeline_state.json` with `"status": "complete"`. Final commit: `pipeline: COMPLETE — paper ready for submission`.

## Notes

- **No structural template for the docs.** Free-form prose. The questions are the discipline; resist the temptation to add headings, bullet rubrics, or fill-in-the-blank scaffolds. The documents are short reflections, not reports.

- **Honesty over diplomacy.** If the paper plateaued below the target tier, say so and name the tier it does fit. If a polish round did not move quality, say so and name it. The audience for `LESSONS_PIPELINE.md` is template maintenance — diplomatic non-answers are useless feedback.

- **Aggregation across runs.** `LESSONS_PIPELINE.md` is the per-run input to a multi-run signal on which agents are net-positive. Mention specific agents and findings so the aggregation can pick them up. Generic praise of "the pipeline" is not actionable; "polish-equilibria r2 caught the σ_u/A1 isotropy mismatch that nothing upstream surfaced" is.

- **Length.** Each doc is one screen of prose, not a report. If you are over 600 words on either, you are over-explaining.
