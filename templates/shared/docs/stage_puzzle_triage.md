# Stage: Puzzle Triage

**Agent:** `puzzle-triager`

**Fires only when:** an empirical analysis (`output/stage3b/empirical_analysis.md`) or experimental result (`output/stage3b_experiments/`) **contradicts** at least one prediction in `output/stage3/implications.md`. If results confirm the theory or are silent on its predictions, **skip this stage** — proceed directly to Stage 4.

This stage operationalizes the principle that surprises are discoveries: when a well-grounded theory predicts X and well-measured data shows not-X, the contradiction itself is often the most valuable contribution. The triager decides whether to pivot the paper around that puzzle, fix the empirics, restrict the theory's scope, abandon the idea, or ship an honest null.

## Entry check

Before launching the triager, verify the contradiction is real:

1. Read `output/stage3/implications.md` and identify which implications were tested.
2. Read the empirical / experimental result file.
3. For each tested implication: did the data contradict it (sign reversal, magnitude mismatch outside predicted range)?
4. If no contradiction: **skip this stage**, proceed to Stage 4.
5. If at least one tested implication was contradicted: launch the puzzle-triager.

## Procedure

1. Read `pipeline_state.json` for current `pivot_round` (default 0).
2. Launch `puzzle-triager` with: theory draft, `implications.md`, empirical/experiment result file, literature map, math audit results, pipeline state.
3. Triager saves to `output/puzzle_triage/triage_pN.md` where N = `pivot_round + 1`.
4. Commit: `artifact: puzzle triage round {N+1} — {VERDICT}`.

## Acting on the verdict

| Verdict | Pipeline action |
|---------|----------------|
| **NORMAL-PROCEED** | (Triager flags an inconsistency — empirics did not actually contradict.) Proceed to Stage 4 and review the entry check. |
| **FIX-EMPIRICS** | Re-launch `empiricist` with the triager's notes on what to improve. Re-enter at `empirical_analysis`. Theory unchanged. Do not increment `pivot_round`. |
| **RECONCILE** | Launch `theory-generator` in `mutate` mode with instruction: "Add an explicit scope condition stating where the result holds. Empirical results show data sits outside that scope." Re-run Gate 2 (math audit) on the revised theory. Do not increment `pivot_round`. |
| **BACK-TO-IDEA** | Return to Stage 1 with the triager report as input to the idea-reviewer. Increment `problem_attempt`. Skip if Stage 5 has begun (paper exists) — use HONEST-NULL instead. |
| **PIVOT** | Increment `pivot_round` in pipeline state. Append entry to `pivot_history`. Launch `theory-generator` in `pivot` strategy mode (see theory-generator agent for the prompt). After the pivoted theory passes Gate 2 + Gate 3, re-run `empirical_analysis` against the new predictions. The original theory becomes a baseline; the new theory must explain the contradiction. |
| **HONEST-NULL** | Two paths: (a) if Stage 5 has begun, document the failed prediction in the limitations section and proceed; (b) if no paper exists yet, return to Stage 0 with the failure notes. Do not pivot a third time. |

## State updates

When PIVOT verdict fires, update `pipeline_state.json`:

```json
{
  "pivot_round": <previous + 1>,
  "pivot_history": [
    ...,
    {
      "round": <new round>,
      "contradiction": "<one sentence>",
      "prior_source": "<which paper / data source set the prior>",
      "new_mechanism_hint": "<what the triager suggested>"
    }
  ]
}
```

Append to `history` array as usual:
```json
{ "timestamp": "...", "event": "puzzle-pivot round N — <new mechanism hint>" }
```

## Hard cap

`pivot_round` ≥ 2 → triager is forbidden from recommending PIVOT. Two pivots without resolution means the problem is not tractable on this approach. Default to HONEST-NULL.

## Downstream effects

When `pivot_round > 0`:
- **Paper-writer**: frames the introduction around the puzzle, not the original prediction. The original theory becomes a baseline / null; the new mechanism is the contribution.
- **Scorer**: Surprise dimension floor is 70 (resolved puzzle is by construction surprising). Importance benefits if the puzzle was field-visible.
- **Referee simulation**: should specifically probe whether the resolving mechanism is principled (falls out of economics) vs. ad-hoc (curve-fit to the data). This is the main failure mode of pivot papers.
