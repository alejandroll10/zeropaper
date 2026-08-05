### Seeded-mode override (applies because `seeded: true` in `pipeline_state.json`)

**Gate 3a-feasibility FALSIFIED does NOT return to Stage 1 for a new idea.** Empirics contradicting the seed's core prediction is a **puzzle**, not a reason to abandon. Instead:

1. Jump immediately to **puzzle triage** (`docs/stage_puzzle_triage.md`) with the falsification as the contradiction.
2. The triager's PIVOT verdict is the preferred route — the seed's theory becomes the baseline/nested case, and a new mechanism is built to *explain why the seed's prediction failed*. This keeps the seed alive as the foil.
3. If PIVOT fails or is not viable, HONEST-NULL is acceptable; BACK-TO-IDEA is forbidden in seeded mode.
4. Do NOT increment `theory_attempt` or reset `theory_version` as the normal FALSIFIED path does — the seed's theory is preserved.

Write a note to `output/seed/falsified_at_feasibility.md` documenting the contradiction and which triage path was taken.
