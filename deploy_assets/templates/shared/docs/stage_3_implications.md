# Stage 3: Implications

**`implications-deriver` + `gap-scout` per implication**

## Step 1: Derive implications from the theory

Launch `implications-deriver` on the current theory draft. Pass it the paths to the latest `output/stage2/theory_draft_vN.md`, the exact accepted exploration report at `pipeline_state.json:stage2b_exploration_path` with exhibits bound by `stage2b_result_receipt` (plus any prior active reports explicitly retained for combined coverage), `output/stage1/selected_idea.md`, and `output/data_inventory.md` (if present). Its body carries the derivation guidance (what counts as an implication, distinctness, sign/sharpness, fragility annotations); it derives 3–6 distinct testable implications and writes `output/stage3/implications_derived.md` — **untagged and with no literature claims**. The agent is web-blind by design: the lit-check is Step 2, per implication, via `gap-scout`; the tagging (Step 3) and routing (Step 5) stay with the orchestrator.

If the deriver returns fewer than 3 implications, or any implication is untestable as stated (no observable variables, no direction), re-launch it once with that feedback before proceeding — a thin implications list caps every downstream stage.
<!-- EMPIRICAL_FIRST_START -->

**Empirical-first mode.** The deriver's inputs change: pass the Stage 2 mechanism document (`output/stage2/theory_draft_vN.md` — prose + DAG + ≤2 reduced-form posits, not a structural model) and Stage 1's `output/stage1/identification_design.md`; there is no `exploration.md` (Stage 2b is skipped in mechanism mode). The **headline causal estimate** is already committed — Stage 1's design pins the estimand and the Stage 2 posits commit to the predicted sign and magnitude — and the deriver's empirical-first body derives **auxiliary** predictions only (heterogeneity panels, falsification/placebo predictions, alternative-channel discriminators; no nested baselines), without re-deriving the headline. If its output flags predictions "Untestable within design", carry them into the paper's limitations section rather than dropping them.

The output schema (Step 4) is unchanged — auxiliary predictions get the same SUPPORTED / NOVEL / PUZZLE-CANDIDATE / DEAD tagging. The empiricist at Stage 3a reads the tagged list and tests the NOVEL ones; the contradiction check fires on any NOVEL prediction the data does not support.
<!-- EMPIRICAL_FIRST_END -->

## Step 2: Lit-check each implication

For every implication, launch `gap-scout` with a focused query: *"Has the literature tested or documented [implication]? What does the data say?"* Provide the implication and the relevant section of the literature map as context.

Save each gap-scout result to `output/stage3/lit_check_impl_N.md`.

## Step 3: Tag each implication

Based on the lit-check, assign one of four tags:

| Tag | Meaning | Pipeline consequence |
|-----|---------|---------------------|
| **SUPPORTED** | Already confirmed in the literature, robust evidence | Low priority for empirical testing — note as consistency check, not novel test |
| **NOVEL** | Never tested empirically | High priority for empirical testing — a fresh prediction |
| **PUZZLE-CANDIDATE** | Literature shows a SIGN REVERSAL or an ORDER-OF-MAGNITUDE discrepancy vs. what the theory predicts | Launch puzzle-triager immediately (see Step 5) — gap-scout's lit-check is the contradicting evidence. Do not wait for Stage 3a/3b. |
| **DEAD** | Already proven to be uninteresting / always-true / always-false | Drop from the implications list |

Drop DEAD implications from the final list. Keep SUPPORTED, NOVEL, and PUZZLE-CANDIDATE.

## Step 4: Write `output/stage3/implications.md`

Assemble from `output/stage3/implications_derived.md` + the Step 2 lit-checks: carry over each surviving implication's statement, **Mechanism**, and **Test design hint** verbatim (plus **Fragility**/**Family** lines where present), and add the **Tag** and **Lit status**. Use this canonical schema so downstream agents (empiricist, paper-writer, scorer) can parse the tags:

```markdown
# Implications

## Implication 1: [one-sentence statement]
**Tag:** NOVEL
**Mechanism:** [why the theory generates this]
**Lit status:** [one-line summary from gap-scout]
**Test design hint:** [if applicable — what data, what method]

## Implication 2: ...
```

## Step 5: Sanity check

If ALL implications come back SUPPORTED, the theory is reinventing known results — this is a **routing decision, not just a flag**: return to Stage 2 to find a non-obvious result within the model, or, if none exists, to Stage 1 to abandon the idea. Do not proceed to paper-writing on the hope of a Gate-4 rescue. (Record the finding in the file regardless.) **This is the primary barren-model detector.** With the idea-stage surprise rating removed, there is no upstream conjecture to flag a predictable model; an all-SUPPORTED outcome here is the *first* hard evidence the model yielded nothing the literature does not already imply — for an open approach (whose answer emerged in development) especially, but for any developed theory. **Bounded — do not cycle Stage 2↔3:** the *first* all-SUPPORTED returns to Stage 2 once to find a non-obvious result; a *second consecutive* all-SUPPORTED on the same idea routes to **Stage 1 (abandon)**, not back to Stage 2 — the idea is barren. (This loop is pre-Gate-4, so the Gate-4 evaluation ceiling does not bound it; this two-strike rule does.)

{{SEED_OVERRIDE_STAGE_3_BARREN}}
<!-- EMPIRICAL_FIRST_START -->

Under empirical-first, interpret this flag against the novelty of the **identification design** (Stage 1), not the auxiliary predictions alone. An empirical-first paper's contribution lives in the identified causal estimate; auxiliary predictions (heterogeneity, falsification, channel discriminators) being all-SUPPORTED is consistent with a well-understood mechanism where the novelty rests on the design + sample. Flag the all-SUPPORTED case only when the *identification design itself* is also derivative (a re-application of a well-trodden instrument or natural experiment), not when the auxiliary predictions happen to align with existing literature.
<!-- EMPIRICAL_FIRST_END -->

If ANY implication is PUZZLE-CANDIDATE, **launch `puzzle-triager` now** with the gap-scout lit-check report(s) as the contradicting evidence — do not wait for Stage 3a/3b. The literature contradiction (sign reversal or order-of-magnitude discrepancy) is itself the contradiction. Follow `docs/stage_puzzle_triage.md`. A literature-grounded contradiction in a well-audited theory is the highest-value pivot opportunity; defaulting to "ship as a noted puzzle" leaves real signal on the table.

**Re-fire guard (prevents loops on Stage 3 re-runs).** Before launching the triager, check `pipeline_state.json:triaged_lit_implications`. For each PUZZLE-CANDIDATE implication, canonicalize its one-sentence statement (lowercase + whitespace-collapsed) and look up the resulting `implication_key`. Fire the triager only if no entry with `verdict: "FIX-EMPIRICS-b"` matches — that is the sole terminal verdict that blocks re-firing. RECONCILE, BACK-TO-IDEA, HONEST-NULL, and PIVOT do not block; the orchestrator clears the relevant entries when those verdicts fire (full schema, canonicalization rule, and reset semantics in `docs/stage_puzzle_triage.md` "Re-fire guard for the Stage-3 lit-check trigger"). After each Stage-3 triager run, the orchestrator (not the triager agent) appends the new entry. When in doubt about whether wording matches, prefer firing — false re-fires are cheap, silent blocks are not.

## Step 6: Commit

`pipeline: stage 3 — implications developed and lit-checked (N novel, M puzzle-candidate, K supported)`
