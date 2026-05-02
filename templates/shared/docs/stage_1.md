# Stage 1: Idea Generation

**Agents:** `idea-generator` + `idea-reviewer` (iterating)

**Regeneration round.** A regeneration round fires when the prior theory attempt succeeded but ceilinged in the REVISE band for the current target tier (see `docs/stage_4.md` tier table — e.g., 60-79 for `top-5`, 55-74 for `top-3-fin`, 45-64 for `field`), branch-manager §E recommends Regenerate, and `regeneration_round == 0` for this problem (see `core.md` escalation table). The orchestrator increments `regeneration_round` to N *before* entering Stage 1, so when this section is read, `regeneration_round` already equals the new N — and `learnings_r{N}.md` and `paper_archive/r{N}/` use the same N (the post-increment value). On a regeneration entry:
- Pass `output/stage1/learnings_r{regeneration_round}.md` (produced by branch-manager) to **both** idea-generator and idea-reviewer alongside the lit map.
- **At step 2 below, take the explicit Regeneration short-circuit** (added at the top of step 2) — do not consult the runner-up or unused-sketch priorities; the existing portfolio is by assumption exhausted.
- Sketches must not repeat any mechanism in `stage1_candidates.sketch_name` or the learnings file's "exhausted mechanisms" list.
- **If post-Stage-5:** archive the current paper to `paper_archive/r{regeneration_round}/` before generation begins; record its best Gate 4 score as `archived_best_score_r{N}` in pipeline state (if not already written by stage_4.md). If the new attempt's eventual Gate 4 score does not strictly beat that archived value, restore the archived paper and ship it.
- **Banned in seeded mode** — the seed is the contract. Branch-manager must not recommend Regenerate on seeded runs; the escalation row in core.md guards this with "not seeded."

**How many ideas to generate:** More candidates when the pool is weaker — more failures mean more draws needed.

| Context | Ideas per round |
|---------|----------------|
| 1st time entering Stage 1 | 5 |
| Returning from a failed theory (scorer MAJOR REWORK/ABANDON) | 10 |
| Returning from a problem-level failure (Stage 0 re-run) | 10, and explicitly explore different territory |

1. Read `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md`
2. **Regeneration short-circuit:** if `regeneration_round` was just incremented for this re-entry (per the "Regeneration round" section above), skip the priority list below entirely — proceed directly to step 3, launching idea-generator with the learnings file. The runner-up / unused-sketch priorities do not apply on a regeneration entry.

   Otherwise — **if returning from a failed attempt:** first reread all `output/stage1/idea_sketches_r*.md` files AND `pipeline_state.json:stage1_candidates` (which records every sketch previously screened at Gates 1b/1c along with its verdict). **Seeded-mode note:** in seeded mode this step does not apply — the orchestrator never re-nominates a different idea (the seeded-mode overrides at Gate 4 and puzzle-triage block Stage 1 re-entry for idea swapping). The re-entry logic below applies only to non-seeded runs. Selection priority on re-entry:
   1. **Pre-screened runner-up** — an entry with `eliminated: false AND winner: false` (a TRACTABLE survivor that lost the tiebreak in a prior Round). These are already vetted by novelty + prototype and are the strongest fallback. If ≥1 exists, pick the highest-ranked one and **skip idea generation entirely**. To re-advance the runner-up:
      - (a) Start a new Round: increment `idea_round` in `pipeline_state.json` (the runner-up re-advance counts as a Round and is subject to the 5-round cap). Let N = new `idea_round`. Create `output/stage1/round_{N}/` and copy the runner-up's prior indexed file `output/stage1/round_{old_round}/selected_idea_{old_rank}.md` to `output/stage1/round_{N}/selected_idea_1.md` (K=1 for a runner-up re-advance). The prior Round's files remain in place as audit trail.
      - (b) Update the runner-up's `stage1_candidates` entry: set `round: N`, `rank: 1`, and reset `novelty`, `prototype`, `surprise` to `null` (they are about to be re-run). Do not touch `eliminated` or `winner` (both remain `false`).
      - (c) Proceed directly to Gates 1b/1c Step 1 with K=1. **Conservative default: always rerun both gates** — the prior verdicts may be stale (literature has advanced since they were produced, negative_results.md has grown, prototype numerics may need re-checking). The cost of one additional novelty + prototype call is trivial relative to a full Stage 2+ run on a stale verdict. Commit: `pipeline: stage 1 re-entry — runner-up re-advanced (round {N})`.
   2. **Unused sketch** — a sketch present in `idea_sketches_r*.md` but absent from `stage1_candidates` (never advanced to Gates 1b/1c). Rank by idea-review scores and advance the best as the sole candidate (K=1). Before writing any files, increment `idea_round` in `pipeline_state.json` and let N = the new `idea_round` (this Round counts toward the 5-round cap); create `output/stage1/round_{N}/`. Then continue from step 7 with K=1.
   3. **Regenerate** — only if neither above applies. Launch idea-generator for a new Round.

   Never re-nominate an entry with `eliminated: true` (KNOWN/BLOCKED) or `winner: true` (its theory already failed). Also read the previous scorer feedback and/or failed theory to understand what went wrong — instruct the idea-generator to avoid the same failure mode
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

{{SEED_OVERRIDE_STAGE_1_GATE_1_REJECT_ALL}}

6. After 5 rounds without ADVANCE, pick the top-K highest-scored ideas (up to 3, minimum 1) and advance them anyway.
7. Save each advanced idea's summary to `output/stage1/round_{N}/selected_idea_{k}.md` for k = 1..K (where K is the number of ideas idea-reviewer advanced, 1 ≤ K ≤ 3, and N is the current `idea_round`). Each file should include the development instructions for that idea plus the relevant sketch content from the round's `idea_sketches_rN.md`. The development instructions come from either:
   - **Normal ADVANCE:** the per-idea "theory-generator should focus on..." line in the idea-reviewer's ADVANCE block.
   - **Force-advance** (5 rounds with no explicit ADVANCE — step 6): synthesize development instructions for each chosen idea from that idea's `**Strengths:**` and `**Weaknesses:**` blocks in the final round's review (these are per-idea fields that always exist in a review, unlike round-level "To develop further" which may be absent or addressed to the next generator round). The synthesized instruction should be of the form: "Build on [Strengths]; the theory-generator must address [Weaknesses] during development." State in the file header that force-advance fallback was used, so Stage 2 knows the instructions are synthesized from weaknesses rather than reviewer-endorsed.

   Record the candidate list in `pipeline_state.json:stage1_candidates`. For each candidate: if an entry with the same `sketch_name` already exists (from a prior Round), **update it in place** — overwrite `round` (to the current `idea_round`) and `rank`, reset verdict fields to `null` for re-screening, keep `winner`/`eliminated` as-is (they should be false for any sketch that re-qualifies, since `eliminated: true` or `winner: true` entries are excluded at re-nomination per step 2). If no existing entry: append a new one `{round: N, rank, sketch_name, novelty: null, prototype: null, surprise: null, eliminated: false, winner: false}`.
8. Commit: `artifact: top-{K} selected ideas saved`

## Gates 1b/1c: Parallel screening on top-K candidates

**Agents:** `novelty-checker` and `idea-prototyper` (each invoked K or fewer times)

Purpose: late-bind the final idea selection. Instead of committing to idea-reviewer's #1 pick, screen the top-K advanced candidates in parallel and pick the winner based on actual novelty + tractability + surprise evidence. K is whatever idea-reviewer advanced (1 ≤ K ≤ 3).

**Seeded mode:** in seeded mode (`seeded: true` in `pipeline_state.json`), Stage 1 is typically bypassed by `seed_triage`, which populates `selected_idea_1.md` directly from the seed. When Gates 1b/1c do fire in seeded mode, K = 1 by definition and the parallel-screening structure degenerates to a single-candidate pass. The per-gate seed overrides below apply unchanged in that case. **Do not widen K beyond 1 in seeded mode** — the seed is the contract.

### Step 1: Parallel novelty check (Gate 1b)

1. Launch K `novelty-checker` agents **concurrently**, one per candidate. Each reads `output/stage1/round_{N}/selected_idea_{k}.md` (N is the current `idea_round`) + `output/stage0/literature_map.md` and saves result to `output/stage1/round_{N}/novelty_check_{k}.md`.
2. After all K return, update `pipeline_state.json:stage1_candidates` with each candidate's `novelty` verdict.
3. Commit: `pipeline: gate 1b — novelty checks {v1/v2/.../vK}` (verdicts in rank order, e.g., `NOVEL/KNOWN/INCREMENTAL`).
4. Drop any candidate with verdict KNOWN (set `eliminated: true` in its state entry). Let M = number of survivors (NOVEL or INCREMENTAL).

| Case | Action |
|------|--------|
| M = 0 (all KNOWN) | No viable ideas from this top-K. Start a new Round of Stage 1 (counts toward the 5-round cap). |
| M ≥ 1 | Proceed to Step 2. |

{{SEED_OVERRIDE_STAGE_1_GATE_1B}}

### Step 2: Parallel prototype (Gate 1c)

1. Launch M `idea-prototyper` agents **concurrently**, one per surviving candidate. Each reads its `output/stage1/round_{N}/selected_idea_{k}.md` + `output/stage0/problem_statement.md` and saves result to `output/stage1/round_{N}/idea_prototype_{k}.md`.
2. After all M return, update `pipeline_state.json:stage1_candidates` with each candidate's `prototype` verdict and `surprise` tier.
3. **Propagate Negative results sequentially** (not in parallel — serialize to avoid file-append races). For each candidate that returned BLOCKED with a "Negative result" section in its prototype, in rank order: append that section verbatim to `output/stage1/negative_results.md` (create or append), then commit `artifact: negative result from candidate {k}`. Negative results constrain all subsequent theory-generator, math-auditor, and self-attacker calls on this problem — they must be quoted into those agents' prompts and the new theory must escape them.
4. Commit: `pipeline: gate 1c — idea prototypes {v1/v2/.../vM}` (e.g., `TRACTABLE-SURPRISING/BLOCKED/TRACTABLE-OBVIOUS`).
5. Drop any BLOCKED candidate (set `eliminated: true`). Let S = number of TRACTABLE survivors.

| Case | Action |
|------|--------|
| S = 0 (all BLOCKED) | Start a new Round of Stage 1 (counts toward the 5-round cap). Negative results are already propagated and will constrain the next round. |
| S ≥ 1 | Proceed to Step 3. |

{{SEED_OVERRIDE_STAGE_1_GATE_1C}}

### Step 3: Tiebreak and canonicalization

1. Among the S TRACTABLE survivors, rank by these criteria in order (advance to the next criterion only to break a tie):
   - (a) **Novelty tier:** NOVEL > INCREMENTAL
   - (b) **Surprise tier:** SURPRISING > POTENTIALLY SURPRISING > OBVIOUS
   - (c) **idea-reviewer ADVANCE rank:** position 1 > position 2 > position 3
2. Save the tiebreak rationale to `output/stage1/candidate_selection.md` — list all K original candidates with their verdicts, note which were dropped at which step and why, and state the winner with the specific criterion that determined selection. This file is Round-scoped and each new Round overwrites it; the full cross-Round audit trail lives in `pipeline_state.json:stage1_candidates`.
3. In `pipeline_state.json:stage1_candidates`, set `winner: true` on the winning entry. Leave non-winning TRACTABLE survivors with `eliminated: false` — they passed both gates and remain valid fallback candidates on re-entry after a failed theory (this is the main operational payoff of parallel screening). Only KNOWN-at-1b and BLOCKED-at-1c entries are `eliminated: true`.
4. Copy the winner's files to the canonical top-level names Stage 2 consumes:
   - `output/stage1/round_{N}/selected_idea_{k_win}.md` → `output/stage1/selected_idea.md`
   - `output/stage1/round_{N}/novelty_check_{k_win}.md` → `output/stage1/novelty_check_idea.md`
   - `output/stage1/round_{N}/idea_prototype_{k_win}.md` → `output/stage1/idea_prototype.md`
   Keep the per-round indexed files under `round_{N}/` as well (do not delete them) — they are the audit trail for this Round's screening.
5. **INCREMENTAL forwarding:** if the winner's novelty verdict is INCREMENTAL, extract the "escape the obvious version" instruction — *"This idea was flagged INCREMENTAL — the obvious version of this model already exists in the literature. Your job is to find a result within this framework that the existing papers do not imply: a sign reversal, an unexpected threshold, a case where the standard intuition breaks. Do not formalize the obvious version."* — and include it verbatim in the Stage 2 theory-generator prompt. Gate 3 will hard-fail INCREMENTAL on the full theory, so the theory must escape incrementality during development.
6. **OBVIOUS forwarding:** if the winner's prototype verdict is TRACTABLE + OBVIOUS, instruct the theory-generator to find a non-obvious result within the model (unexpected comparative static, interaction effect, parameter regime where the sign flips). If the full theory also scores low on surprise at Gate 4, the idea will not advance.
7. Update `pipeline_state.json` and commit: `pipeline: stage 1 complete — winner selected from {K} candidates`.
