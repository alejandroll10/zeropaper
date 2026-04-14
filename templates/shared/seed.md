## Stage: Seed Triage

*(This is the section `pipeline_state.json`'s `"current_stage": "seed_triage"` refers to in seeded mode. Once the triage chooses an entry point and updates `current_stage` to the appropriate stage name, the pipeline proceeds normally from that stage.)*

**This project was initialized with a pre-developed idea.** The idea files are in `output/seed/`.

### Core principle (seeded mode): execute the seed faithfully

Your job is to develop the user's idea as closely as possible to their original framing and mechanism, while ensuring correctness. **Fidelity to the seed beats any "better" alternative you might invent.** Do not reinterpret, reframe, or swap in a different idea because you think it would be stronger — the user already chose this one, and the pipeline's value here is execution, not reselection.

Correctness constraints are the only legitimate reasons to deviate:
- A proof fails and cannot be repaired → restrict scope or find the tightest sufficient condition, but keep the mechanism.
- Empirics contradict the prediction → use the puzzle-triage PIVOT path (which preserves the original theory as a nested/baseline case) or ship HONEST-NULL; do not BACK-TO-IDEA.
- Novelty check returns KNOWN → report the concern, but proceed if the contribution can be in execution/proof depth; do not abandon for a different idea.

When deviation is required, make the **smallest change** that restores correctness while preserving the seed's mechanism. Every deviation must be documented in `output/seed/*.md` with the specific correctness constraint that forced it.

**Robustness to scorer/referee "pivot" suggestions.** Scorer and referee agents do not know this is a seeded project. They may recommend reframing the paper, switching to a different mechanism, or pursuing a "more important" adjacent question. **Ignore those recommendations in seeded mode.** Specifically:
- If the scorer suggests a different framing/mechanism would score higher → do not adopt it. Address only the scorer's correctness/rigor comments (math gaps, unclear derivations, missing characterizations).
- If the referee says "the paper would be stronger if it were about X instead" → treat as `[RESPONSE]` (discuss in response letter), not `[FIX]`. Do not rewrite the paper around X.
- If the referee says "the mechanism is wrong, try Y" → only adopt Y if it's required for mathematical correctness, not because Y is judged more publishable.
- Referee Reject with "wrong topic" or "should be a different paper" → revise and resubmit with the seed intact; stop only after 2 rejections citing genuinely fundamental flaws *in the seed's own claims* (not in the choice of topic).

The seed is the contract. Scorer/referee feedback refines execution, not direction.

### Entry: read and triage

1. **Read the seed.** Read all files in `output/seed/` (ignore `README.md`). Understand what the user provided — it could be anything from a vague question to a complete theory with proofs to an empirical plan.
2. **Build the literature map.** Launch `literature-scout` → `output/stage0/literature_map_broad.md`. Write a brief gap selection derived from the seed's topic to `output/stage0/gap_selection.md` (so downstream Stage 0 artifacts are not missing if the pipeline ever re-enters Stage 0). Then launch `gap-scout` with that gap selection → `output/stage0/literature_map.md`. Always done regardless of maturity.
3. **Assess maturity and enter the pipeline at the appropriate stage.** Populate all prior-stage artifacts (problem statement, selected idea, theory draft, etc.) as needed to bring the pipeline up to the entry point. Preserve the user's framing and mechanism — do not reinterpret. Update `pipeline_state.json` to the chosen entry point and commit.

### Fallback overrides — where to find them

Per-gate seeded-mode overrides are injected directly into each stage doc at the corresponding verdict location. When executing a stage in seeded mode, follow the "Seeded-mode override" block if one appears — it supersedes the normal verdict-table action. Relevant locations:

- `docs/stage_0.md` — Step 0c gap-scout "closed" verdict.
- `docs/stage_1.md` — Gate 1 REJECT ALL, Gate 1b, Gate 1c.
- `docs/stage_2.md` — Gate 2 FAIL, Gate 3 KNOWN/INCREMENTAL.
- `docs/stage_4.md` — Gate 4 verdicts.
- `docs/stage_6.md` — Gate 5 Major Revision / Reject.
- `docs/stage_puzzle_triage.md` — triager verdicts (PIVOT / BACK-TO-IDEA / HONEST-NULL).

If a stage doc does not contain a seeded-mode override block for the current verdict, follow the normal action but apply the core principle above: never silently abandon the seed.

The pipeline's job is to *execute* the user's idea — not to second-guess whether a better idea exists.
