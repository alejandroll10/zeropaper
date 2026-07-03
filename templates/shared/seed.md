## Stage: Seed Triage

*(`current_stage: "seed_triage"` resolves here. Once triage picks an entry point and updates `current_stage`, the pipeline proceeds normally.)*

Idea files are in `output/seed/`.

### Core principle (seeded mode): execute the seed faithfully

Develop the user's idea as closely as possible to what the seed pins, while ensuring correctness. **Fidelity to the seed beats any "better" alternative you might invent.** Do not reinterpret, reframe, or swap in a different idea because you think it would be stronger.

Correctness constraints are the only legitimate reasons to deviate:
- A proof fails and cannot be repaired → restrict scope or find the tightest sufficient condition, but keep what the seed pins.
- Empirics contradict the prediction → use the puzzle-triage PIVOT path (which preserves the original theory as a nested/baseline case) or ship HONEST-NULL; do not BACK-TO-IDEA.
- Novelty check returns KNOWN → report the concern, but proceed if the contribution can be in execution/proof depth; do not abandon for a different idea.

When deviation is required, make the **smallest change** that restores correctness while preserving what the seed pins. Every deviation must be documented in `output/seed/*.md` with the specific correctness constraint that forced it.

**Robustness to scorer/referee "pivot" suggestions.** Scorer and referee agents do not know this is a seeded project and may recommend reframing, switching mechanism, or pursuing an adjacent question. Ignore those:
- Scorer suggests a different framing/mechanism would score higher → do not adopt. Address only correctness/rigor comments (math gaps, unclear derivations, missing characterizations).
- Referee says "the paper would be stronger if it were about X" → treat as `[RESPONSE]`, not `[FIX]`.
- Referee says "the mechanism is wrong, try Y" → adopt Y only if required for mathematical correctness.
- Referee Reject with "wrong topic" or "should be a different paper" → revise and resubmit with the seed intact; stop only after 2 rejections citing fundamental flaws *in the seed's own claims* (not in topic choice).

### Entry: read and triage

1. **Read the seed.** Read all files in `output/seed/` (ignore `README.md`).
2. **Build the literature map.** Launch `literature-scout` → `output/stage0/literature_map_broad.md`. Write a brief gap selection derived from the seed's topic to `output/stage0/gap_selection.md`. Then launch `gap-scout` → `output/stage0/literature_map.md`. Always done regardless of maturity.
3. **Assess maturity and enter the pipeline at the appropriate stage.** Populate all prior-stage artifacts (problem statement, selected idea, theory draft, etc.) needed to reach the entry point. The problem statement is written **directly from the seed** here — `question-poser` (Stage 0 Step 0d) and `question-referee` (Step 0e) are **not launched** in seeded mode; the seed defines the question. Preserve what the seed pins. Update `pipeline_state.json` and commit.

   **Stage 1 artifacts (if back-filled):** in seeded mode K=1, so: (a) set `loops.idea.round: 1`, (b) write `output/stage1/round_1/selected_idea_1.md` (for Gates 1b/1c), (c) write the canonical `output/stage1/selected_idea.md` (identical copy, for Stage 2). Add one entry `{round: 1, rank: 1, sketch_name: "<seed-descriptor>", novelty: null, prototype: null, reviewer_importance: null, prototype_retry: 0, eliminated: false, winner: true}` to `stage1_candidates` — the seed is winner by construction; runner-up-on-re-entry does not apply (so the `reviewer_importance` tiebreak axis is never consulted, hence `null`).
<!-- EMPIRICAL_FIRST_START -->

   **Empirical-first additional Stage 1 step.** Under `--mode empirical-first`, Stage 1 has a Step 4 (`identification-designer` produces `output/stage1/identification_design.md`) that the mechanism-mode `theory-generator` at Stage 2 has a hard dependency on. Even when seed_triage back-fills Stage 1 artifacts to enter at a later stage, **fire Step 4 of `docs/stage_1.md` before transitioning `current_stage` past `stage_1_identification_design`**. The seeded selected idea drives the launch (its empirical question is the theoretical object the design must identify); the Step 4 launch prompt in `docs/stage_1.md` is unchanged. If the designer returns `N/A` / `OUT-OF-SCOPE` / `no design feasible`, follow the same Stage 1 Step 4 N/A-routing branch — except that REENTER-STAGE-1 with a different idea is **disallowed under seeded mode** (the seed is the contract; do not swap ideas). Operator-escalate is the dominant fallback in this case; document the verdict to `output/seed/*.md` per the seeded-mode core principle.

   **Idea-prototype prerequisite for Step 4.** The empirical-first Step 4 launch prompt cites `output/stage1/idea_prototype.md`. If the back-fill is shallow enough that the idea-prototyper has not run, either (a) run the idea-prototyper on the seed-derived idea before Step 4, or (b) hand-write a minimal prototype (predicted relationship, expected magnitude from literature, identifying variation) into `output/stage1/idea_prototype.md` based on the seed content. The designer needs the predicted relationship to recommend a design class; without it, the launch prompt is missing a load-bearing input.
<!-- EMPIRICAL_FIRST_END -->

### Fallback overrides

Per-gate seeded-mode overrides are injected into each stage doc at the verdict location. Follow the "Seeded-mode override" block when one appears — it supersedes the normal verdict action. Locations:

- `docs/stage_0.md` — gap-scout "closed".
- `docs/stage_1.md` — Gate 1 REJECT ALL, Gate 1b, Gate 1c.
- `docs/stage_2.md` — Gate 2 FAIL, Gate 3 KNOWN/INCREMENTAL.
- `docs/stage_3_implications.md` — barren-model (all-SUPPORTED).
- `docs/stage_3a_empirical.md` — Gate 3a-feasibility FALSIFIED (`--ext empirical`).
- `docs/stage_4.md` — Gate 4 verdicts.
- `docs/stage_6.md` — Gate 5 Major Revision / Reject.
- `docs/stage_puzzle_triage.md` — PIVOT / BACK-TO-IDEA / HONEST-NULL.

If no override block exists for the current verdict, follow the normal action but apply the core principle: never silently abandon the seed.
