# Stage 1: Idea Generation

**Agents:** `idea-generator` + `idea-reviewer` (iterating)

**How many ideas to generate:** More candidates when the pool is weaker — more failures mean more draws needed.

| Context | Ideas per round |
|---------|----------------|
| 1st time entering Stage 1 | 5 |
| Returning from a failed theory (scorer MAJOR REWORK/ABANDON) | 10 |
| Returning from a problem-level failure (Stage 0 re-run) | 10, and explicitly explore different territory |

1. Read `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md`
2. **If returning from a failed attempt:** first reread all `output/stage1/idea_sketches_r*.md` files. Identify which unused sketches are still viable given what the failed attempt revealed. Pick the next-best unused sketch before generating new ideas — only regenerate if no unused sketch is viable. Also read the previous scorer feedback and/or failed theory to understand what went wrong — instruct the idea-generator to avoid the same failure mode
3. Launch idea-generator with the problem statement, literature map, **and data inventory** to brainstorm candidate mechanisms (see table above for count)
4. **Increment `idea_round` in `pipeline_state.json`** (starts at 0; becomes 1 on first entry). Save sketches to `output/stage1/idea_sketches_rN.md` where N = the new `idea_round` value. This counter feeds the 5-round escalation cap and the dashboard.
5. Commit: `artifact: idea sketches round {N}`

## Gate 1: Idea Review

**Agent:** `idea-reviewer`

1. Launch idea-reviewer on the sketches + problem statement + literature map
2. If this is a return visit to Stage 1, also provide the previous scorer feedback so the reviewer knows what to screen against
3. Save review to `output/stage1/idea_review_rN.md`
4. Commit: `artifact: idea review round {N}`
5. Read the decision:

| Decision | Action |
|----------|--------|
| **ADVANCE** | Best idea identified. Proceed to Stage 2 with the reviewer's instructions for theory development. |
| **ITERATE** | Re-launch idea-generator with the reviewer's feedback. Max 5 rounds of iteration. |
| **REJECT ALL** | All ideas are weak. Return to Stage 0 for a different problem. |

6. After 5 rounds without ADVANCE, pick the highest-scored idea and advance it anyway.
7. Save the winning idea summary to `output/stage1/selected_idea.md`
8. Commit: `artifact: selected idea saved`

## Gate 1b: Novelty Check on Selected Idea

**Agent:** `novelty-checker`

1st of 2 novelty checks — runs on the selected idea *before* investing in theory development.

1. Launch novelty-checker on `output/stage1/selected_idea.md` + `output/stage0/literature_map.md`
2. Save result to `output/stage1/novelty_check_idea.md`
3. Read the verdict:

| Verdict | Action |
|---------|--------|
| **KNOWN** | Kill this idea. Pick the next-best idea from the current round's sketches (per idea-reviewer rankings) and re-run Gates 1b + 1c on it. If no viable ideas remain, re-run Stage 1 with a new round (counts toward the 5-round total cap on Stage 1 iterations). |
| **INCREMENTAL** | Proceed to Gate 1c, then Stage 2, but instruct the theory-generator: "This idea was flagged INCREMENTAL — the obvious version of this model already exists in the literature. Your job is to find a result within this framework that the existing papers do not imply: a sign reversal, an unexpected threshold, a case where the standard intuition breaks. Do not formalize the obvious version." Gate 3 will hard-fail INCREMENTAL on the full theory, so the theory must escape incrementality during development. |
| **NOVEL** | Proceed to Gate 1c. |

4. Commit: `pipeline: gate 1b — novelty check on idea {NOVEL/INCREMENTAL/KNOWN}`

{{SEED_OVERRIDE_STAGE_1_GATE_1B}}

## Gate 1c: Idea Prototype (tractability + surprise check)

**Agent:** `idea-prototyper`

Quick mathematical feasibility check — attempt the key derivation before investing in full theory development. **Always runs** (not optional), because even 1st-attempt ideas can have hidden tractability issues that the sketch doesn't reveal. Also performs a **surprise check** on TRACTABLE results: now that the math shows what the result looks like, is it non-obvious?

1. Launch idea-prototyper on `output/stage1/selected_idea.md` + `output/stage0/problem_statement.md`
2. Save result to `output/stage1/idea_prototype.md`
3. Read the verdict:

| Verdict | Surprise | Action |
|---------|----------|--------|
| **TRACTABLE** | **SURPRISING** or **POTENTIALLY SURPRISING** | Proceed to Stage 2 — pass the prototype to the theory-generator as a head start. |
| **TRACTABLE** | **OBVIOUS** | Soft kill signal. The idea is tractable but the result confirms what everyone would guess. Proceed to Stage 2, but instruct the theory-generator to find a non-obvious result within the model (unexpected comparative static, interaction effect, parameter regime where the sign flips). If the full theory also scores low on surprise at Gate 4, the idea will not advance. |
| **BLOCKED** | — | The derivation hit a wall. Read where it got stuck. If fixable: pick the next-best idea from the reviewer's rankings and re-run Gates 1b+1c. If fundamental: return to Stage 1 for a new round. |

4. Commit: `pipeline: gate 1c — idea prototype {TRACTABLE/BLOCKED}, surprise: {SURPRISING/POTENTIALLY SURPRISING/OBVIOUS}`
5. Update `process_log/pipeline_state.json` and commit: `pipeline: stage 1 complete — idea selected, novelty-checked, and prototyped`

{{SEED_OVERRIDE_STAGE_1_GATE_1C}}

{{SEED_OVERRIDE_STAGE_1_GATE_1_REJECT_ALL}}
