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
   - **If not, which journal(s) would be the best fit? Explain for every tier in this variant's ladder ({{TIER_LIST_INLINE}}, or other if you feel there's a better fit) why the paper would or would not be a good fit at that tier.**

   Commit: `lessons: paper reflection`.

2. **Write `LESSONS_PIPELINE.md` at the project root.** Answer:
   - **How do you feel about the pipeline?**
   - **What helped vs. what hurt the paper — keeping cost/time impact separate from quality impact?**

   Commit: `lessons: pipeline reflection`.

3. **Mark complete.** Update `process_log/pipeline_state.json` with `"status": "complete"`. Final commit: `pipeline: COMPLETE — paper ready for submission`.

## Notes

Free-form prose. 

- **Honesty over diplomacy.** If the paper plateaued below the target tier, say so and name the tier it does fit. If a polish round did not move quality, say so and name it. Name specific agents and specific findings, not impressions. The audience for `LESSONS_PIPELINE.md` is template maintenance.
