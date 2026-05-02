# Stage: Puzzle Triage

**Agent:** `puzzle-triager`

**Fires when:** (a) an empirical analysis (`output/stage3a/empirical_analysis.md`) or experimental result (`output/stage3b/`) **contradicts** at least one prediction in `output/stage3/implications.md`, OR (b) Stage 3 tagged at least one implication **PUZZLE-CANDIDATE** — gap-scout reports the literature shows a sign reversal or order-of-magnitude discrepancy vs. the prediction (the lit-check report is the contradiction evidence; fire before any formal empirics). If results confirm the theory or are silent on its predictions, **skip this stage** — proceed directly to Stage 4.

This stage operationalizes the principle that surprises are discoveries: when a well-grounded theory predicts X and well-measured data shows not-X, the contradiction itself is often the most valuable contribution. The triager decides whether to pivot the paper around that puzzle, fix the empirics, restrict the theory's scope, abandon the idea, or ship an honest null.

## Entry check

Before launching the triager, verify the contradiction is real:

1. Read `output/stage3/implications.md` and identify which implications were tested.
2. Read every result file that exists:
   - `output/stage3a/empirical_analysis.md` (if `--ext empirical`)
   - `output/stage3b/experiment_results.md` (if `--ext theory_llm`)
   Both may exist when both extensions are enabled — use all of them.
3. For each tested implication: did the data contradict it (sign reversal, magnitude mismatch outside predicted range)?
4. If no contradiction across any result source: **skip this stage**, proceed to Stage 4.
5. If at least one tested implication was contradicted by at least one result source: launch the puzzle-triager.

## Procedure

1. Read `pipeline_state.json` for current `pivot_round` (default 0).
2. Launch `puzzle-triager` with: theory draft, `implications.md`, **every contradiction-evidence file** (post-empirics path: `empirical_analysis.md` and/or `experiment_results.md` that contradicted; Stage-3 PUZZLE-CANDIDATE path: the `output/stage3/lit_check_impl_N.md` reports for each PUZZLE-CANDIDATE implication), literature map, math audit results, pipeline state. If multiple evidence sources disagree (e.g., empirics confirm but experiments contradict, or lit-check contradicts but empirics confirm), note the disagreement in the input — the triager should flag this in its rationale and typically recommend FIX-EMPIRICS rather than PIVOT until the measurement conflict is resolved.
3. Triager saves to `output/puzzle_triage/triage_pN.md` where N = `pivot_round + 1`.
4. **(Stage-3 lit-check trigger only)** Orchestrator appends to `pipeline_state.json:triaged_lit_implications` an entry `{implication_key, verdict, triage_file}` for each PUZZLE-CANDIDATE implication just triaged. **Verdict translation:** the triager emits raw `FIX-EMPIRICS`; on the Stage-3 lit-check trigger the orchestrator records this as `"FIX-EMPIRICS-b"` (the no-empirics branch — see the FIX-EMPIRICS verdict-table row), not the raw string. All other verdicts pass through unchanged. See "Re-fire guard" below for the canonicalization rule and the verdict semantics (FIX-EMPIRICS-b blocks re-fire; RECONCILE removes this implication's entry; BACK-TO-IDEA and PIVOT reset the whole list to `[]`). Skip this step for the post-empirics trigger — that path uses `pivot_round` / `pivot_resolved` instead.
5. Commit: `artifact: puzzle triage round {N+1} — {VERDICT}`.

## Acting on the verdict

| Verdict | Pipeline action |
|---------|----------------|
| **NORMAL-PROCEED** | (Triager flags an inconsistency — empirics did not actually contradict.) Proceed to Stage 4 and review the entry check. |
| **FIX-EMPIRICS** | Two branches: <br/>**(a) Post-empirics trigger (empiricist exists):** run the data-source preflight from `docs/stage_3a_empirical.md` ("Preflight: data-source liveness") — a long puzzle-triage / Stage-4 gap may have outlived the WRDS session — then re-launch `empiricist` with the triager's notes on what to improve, re-enter at `empirical_analysis`. Theory unchanged. Do not increment `pivot_round`. **Cap (this branch only): max 2 FIX-EMPIRICS rounds per puzzle.** Track via `fix_empirics_round` counter (init 0, increment on each FIX-EMPIRICS verdict in this branch only). On the 3rd such call, force escalation to RECONCILE (if scope-restrictable) or HONEST-NULL (otherwise). <br/>**(b) Stage-3 lit-check trigger with no `--ext empirical`:** the lit evidence is rated DEBATABLE; there is no empiricist to re-run. Orchestrator leaves the PUZZLE-CANDIDATE tag in place (no re-tag, no information loss) and proceeds to Stage 4. Downstream agents (scorer, paper-writer) read `output/puzzle_triage/triage_pN.md` and gate the Surprise-floor / puzzle-framing rules on measurement-quality being STANDARD — DEBATABLE means those rules do not fire. Do not loop the triager; the cap and counter in branch (a) do not apply here. |
| **RECONCILE** | Launch `theory-generator` in `mutate` mode with instruction: "Add an explicit scope condition stating where the result holds. Empirical results show data sits outside that scope." **Increment `theory_version`. Reset `fix_empirics_round` to 0** (the reconciled theory is a fresh empirical slate) **and reset `stage2b_theory_version` to `null`** (Stage 2b in step below will repopulate it per `stage_2.md:79`; resetting prevents the Gate 4 staleness gate from passing on a stale pre-RECONCILE value). Re-run Gate 2 (math audit), Gate 3 (novelty), Stage 2b (exploration), Stage 3 (implications), AND Stage 3a (full empirical analysis, if `--ext empirical`) / Stage 3b (experiments, if `--ext theory_llm`) on the revised theory — the scope condition is a structural change and all downstream artifacts are stale. Do not increment `pivot_round`. **Remove this implication's entry from `triaged_lit_implications`** so the re-fire guard does not block re-triage of the same prediction in the mutated theory. |
| **BACK-TO-IDEA** | Return to Stage 1 with the triager report as input to the idea-reviewer. **Do NOT increment `problem_attempt`** (the problem is unchanged — only the idea is being replaced). Set `current_stage: "stage_1"`. Before re-running idea-reviewer, apply `docs/stage_1.md` step 2 re-entry logic: prefer a pre-screened runner-up from `pipeline_state.json:stage1_candidates` (entry with `eliminated: false AND winner: false`) over regenerating. Skip if Stage 5 has begun (paper exists) — use HONEST-NULL instead. **Reset `triaged_lit_implications` to `[]`** — new idea, fresh implication space. |
| **PIVOT** | Run the **pivot sequence** documented below. **Reset `triaged_lit_implications` to `[]`** as part of step 1 of the pivot sequence — new theory, new implication space. |
| **HONEST-NULL** | Set `pivot_resolved: false` in pipeline state (see State updates). Then two paths: (a) if Stage 5 has begun, document the failed prediction in the limitations section, set `current_stage: "stage_5"` and proceed; (b) if no paper exists yet, set `current_stage: "stage_0"` and return to Stage 0 with the failure notes (also increment `problem_attempt`). Do not pivot a third time. |

{{SEED_OVERRIDE_STAGE_PUZZLE_TRIAGE}}

## Pivot sequence (when verdict is PIVOT)

A pivot is a full theory revision. The new theory needs new implications, lit-checks, and validation — not just empirical re-run. Follow this sequence end-to-end:

1. **Update state.** Increment `pivot_round`. **Also increment `theory_attempt`, reset `theory_version` to 1, reset `fix_empirics_round` to 0, reset `stage2b_theory_version` to `null`, and reset `triaged_lit_implications` to `[]`** — the pivoted theory is a new theory with a fresh empirical budget and a fresh implication space, and all downstream `_vN.md` files (math audit, novelty check, self-attack, scorer) must use the new version numbers so they don't collide with the pre-pivot theory's files. The `stage2b_theory_version` reset prevents the Gate 4 staleness gate (`stage2b_theory_version < theory_version`) from passing on a stale pre-pivot value; step 5 below repopulates it. Append to `pivot_history`. Set `pivot_resolved: null` (will be set true/false after the pivoted theory's empirical run).
2. **Pivoted theory.** Launch `theory-generator` in `pivot` strategy mode with: original theory, contradicted finding, triager report, literature map. The agent rebuilds around explaining the contradiction; original theory becomes a nested case. Save the pivoted theory as `output/stage2/theory_draft_v1.md` (under the newly incremented `theory_attempt`) — all downstream `_vN.md` artifacts (audits, novelty, implications, scorer outputs) use this fresh version numbering.
3. **Re-run Gate 2.** Math audit (structured + freeform) on the pivoted theory. Iterate as in Stage 2.
4. **Re-run Gate 3.** Novelty check on the pivoted theory. KNOWN/INCREMENTAL → escalate.
5. **Re-run Stage 2b.** Theory exploration on the pivoted theory.
6. **Re-run Stage 3 (implications) IN FULL.** Derive new implications from the pivoted theory and gap-scout each one for the NOVEL/PUZZLE-CANDIDATE/SUPPORTED/DEAD tag. **Do not reuse the previous theory's implications.md** — overwrite it. Downstream agents (paper-writer, scorer, empiricist) read the current `implications.md` and assume it describes the current theory.
7. **Re-run the contradiction check on the pivoted theory.** If `--ext empirical` or `--ext theory_llm` is enabled, re-run `empirical_analysis` (and experiments, if applicable) against the new predictions and run the puzzle-triage entry check again at the end. **If neither extension is enabled (Stage-3 lit-check trigger):** the re-run reduces to the new theory's Stage 3 lit-check, with one extra requirement to prevent silent-theory false positives — the pivoted `implications.md` MUST contain at least one implication that directly addresses the originally contradicted prediction (i.e., explains why the literature shows what it shows). The orchestrator verifies this by reading the original triager report's "Contradiction" section and checking that some new implication maps onto it. Resolution rule: `pivot_resolved=true` only if (i) at least one new implication addresses the original contradiction AND (ii) no new PUZZLE-CANDIDATE appears for any new prediction. Dropping the prediction silently does not count as resolution.
8. **Set both `pivot_resolved` (top-level) AND `pivot_history[N].resolved` for this round's entry.** Set the same value to both:
   - `true` if the pivoted theory's empirics confirm its (new) predictions, or (no-empirics path) the resolution rule in step 7 is satisfied (new implication addresses the original contradiction AND no new PUZZLE-CANDIDATE appears) — the puzzle is resolved.
   - `false` if the pivoted theory's empirics also contradict and the triager (re-fired) returns HONEST-NULL or another non-PIVOT verdict, or (no-empirics path) the resolution rule fails (no new implication addresses the original contradiction, or any new PUZZLE-CANDIDATE appears).
   - If the triager returns PIVOT again, leave both fields `null` for this round and re-enter the pivot sequence (this is the second pivot; cap is 2).
9. **Proceed to Stage 4** once `pivot_resolved` is set (true or false).

## State updates

When PIVOT verdict fires, update `pipeline_state.json`:

```json
{
  "pivot_round": <previous + 1>,
  "pivot_resolved": null,    // set true/false after pivoted theory's empirical run
  "pivot_history": [
    ...,
    {
      "round": <new round>,
      "contradiction": "<one sentence>",
      "prior_source": "<which paper / data source set the prior>",
      "new_mechanism_hint": "<what the triager suggested>",
      "resolved": null         // set true/false at end of pivot sequence
    }
  ],
  "triaged_lit_implications": []   // reset on PIVOT — new theory, new implication space
}
```

**Two fields — don't confuse them:**

- **Top-level `pivot_resolved`** — overall current state. Reflects the most recent pivot's outcome. This is the **single signal** downstream agents (paper-writer, scorer) read. Values:
  - `null` — no pivot has occurred yet, or the most recent pivot is still in progress
  - `true` — the latest pivoted theory's empirics confirmed its predictions; the puzzle is resolved
  - `false` — the latest pivoted theory also contradicted, ended in HONEST-NULL or escalated; the puzzle was not solved
- **Per-round `pivot_history[N].resolved`** — the resolution of pivot round N specifically. Useful for auditing history across multiple pivots. Set to the same `true`/`false` value at the same time as `pivot_resolved`; the top-level field mirrors the latest entry.

Paper-writer and scorer should gate their puzzle-framing logic on **top-level `pivot_resolved == true`**, NOT on `pivot_round > 0`. A failed pivot is not a resolved puzzle.

Append to `history` array as usual:
```json
{ "timestamp": "...", "event": "puzzle-pivot round N — <new mechanism hint>" }
```

## Re-fire guard for the Stage-3 lit-check trigger

Stage 3 can re-run on RECONCILE, on Gate-4 REVISE→Stage 2 cycles, and after PIVOT. Without a guard, the same PUZZLE-CANDIDATE implication can re-fire the triager every time. Track triaged Stage-3 PUZZLE-CANDIDATEs in `pipeline_state.json`:

```json
"triaged_lit_implications": [
  { "implication_key": "<canonicalized text — see below>", "verdict": "FIX-EMPIRICS-b", "triage_file": "output/puzzle_triage/triage_pN.md" }
]
```

**Block-on-rerun rule.** Stage 3 step 5 checks this list before firing the triager. The ONLY terminal verdict that blocks re-firing is **FIX-EMPIRICS-b** (DEBATABLE lit — theory unchanged, lit-evidence too weak). All other verdicts must NOT block re-fires:
- **RECONCILE** mutates the theory and restarts Stage 3 — if the same implication reappears in the new theory it deserves a fresh triage. When RECONCILE fires, the orchestrator removes that implication's entry from `triaged_lit_implications`.
- **BACK-TO-IDEA** restarts Stage 1 with a new idea → reset `triaged_lit_implications` to `[]`.
- **HONEST-NULL** ends the run on this theory → moot (no further Stage 3 runs).
- **PIVOT** → reset `triaged_lit_implications` to `[]` (new theory, new implication space).

**Implication key (canonicalization).** Match on `lowercase + whitespace-collapsed` form of the implication's one-sentence statement. False negatives (re-firing on a slightly reworded implication) are cheap — the triager just runs again. False positives (silently blocking a different implication that happens to canonicalize the same) are expensive. When uncertain, prefer re-firing.

**Append responsibility.** The orchestrator updates `pipeline_state.json:triaged_lit_implications` after each Stage-3 triager run completes — the triager agent itself does not write to pipeline state, only to `output/puzzle_triage/triage_pN.md`. See Procedure step 4.

## Hard cap

`pivot_round` ≥ 2 → triager is forbidden from recommending PIVOT. Two pivots without resolution means the problem is not tractable on this approach. Default to HONEST-NULL.

## Downstream effects

When `pivot_round > 0`:
- **Paper-writer**: frames the introduction around the puzzle, not the original prediction. The original theory becomes a baseline / null; the new mechanism is the contribution.
- **Scorer**: Surprise dimension floor is 70 (resolved puzzle is by construction surprising). Importance benefits if the puzzle was field-visible.
- **Referee simulation**: should specifically probe whether the resolving mechanism is principled (falls out of economics) vs. ad-hoc (curve-fit to the data). This is the main failure mode of pivot papers.
