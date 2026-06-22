# Stage 3: Implications

**Orchestrator task + `gap-scout` per implication**

## Step 1: Derive implications from the theory

Read the theory draft. Work out:

- Testable predictions (signed comparative statics, magnitude predictions, qualitative patterns)
- Comparative statics (how results move with parameters)
<!-- THEORY_FIRST_START -->
- Special cases that recover known results (nested baselines)
<!-- THEORY_FIRST_END -->
- Economic intuition for each result (in words, not algebra)

Aim for 3–6 distinct implications. Quality over quantity — each should be a sentence a reader could test.
<!-- EMPIRICAL_FIRST_START -->

**Empirical-first mode.** "The theory draft" here is the Stage 2 mechanism document (`output/stage2/theory_draft_vN.md`) — prose + DAG + ≤2 reduced-form posits, not a structural model. The **headline causal estimate** is already committed: Stage 1's `identification_design.md` pins the estimand and the Stage 2 posits commit to the predicted sign and magnitude. Do not re-derive the headline prediction in Step 1.

Stage 3 under empirical-first has a distinct job: derive **auxiliary** predictions that the mechanism implies and the empiricist will need at Stage 3a beyond the headline coefficient. Focus on:

- **Heterogeneity predictions** — where the channel implies the effect should be stronger / weaker / reverse (e.g., by firm size, by leverage, by exposure intensity, by sub-period). These become the heterogeneity panels at Stage 3a.
- **Falsification predictions** — sub-populations or settings where the channel predicts *no* effect. These become the placebo tests at Stage 3a.
- **Alternative-channel discriminators** — patterns the claimed channel predicts that the leading alternative channel does *not* predict (or predicts in the opposite direction). These pin the channel attribution at Stage 3a.

Do not derive "nested baselines / special cases" — the mechanism mode has no model parameters to take limits of. Skip that bullet.

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

Use this canonical schema so downstream agents (empiricist, paper-writer, scorer) can parse the tags:

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
<!-- EMPIRICAL_FIRST_START -->

Under empirical-first, interpret this flag against the novelty of the **identification design** (Stage 1), not the auxiliary predictions alone. An empirical-first paper's contribution lives in the identified causal estimate; auxiliary predictions (heterogeneity, falsification, channel discriminators) being all-SUPPORTED is consistent with a well-understood mechanism where the novelty rests on the design + sample. Flag the all-SUPPORTED case only when the *identification design itself* is also derivative (a re-application of a well-trodden instrument or natural experiment), not when the auxiliary predictions happen to align with existing literature.
<!-- EMPIRICAL_FIRST_END -->

If ANY implication is PUZZLE-CANDIDATE, **launch `puzzle-triager` now** with the gap-scout lit-check report(s) as the contradicting evidence — do not wait for Stage 3a/3b. The literature contradiction (sign reversal or order-of-magnitude discrepancy) is itself the contradiction. Follow `docs/stage_puzzle_triage.md`. A literature-grounded contradiction in a well-audited theory is the highest-value pivot opportunity; defaulting to "ship as a noted puzzle" leaves real signal on the table.

**Re-fire guard (prevents loops on Stage 3 re-runs).** Before launching the triager, check `pipeline_state.json:triaged_lit_implications`. For each PUZZLE-CANDIDATE implication, canonicalize its one-sentence statement (lowercase + whitespace-collapsed) and look up the resulting `implication_key`. Fire the triager only if no entry with `verdict: "FIX-EMPIRICS-b"` matches — that is the sole terminal verdict that blocks re-firing. RECONCILE, BACK-TO-IDEA, HONEST-NULL, and PIVOT do not block; the orchestrator clears the relevant entries when those verdicts fire (full schema, canonicalization rule, and reset semantics in `docs/stage_puzzle_triage.md` "Re-fire guard for the Stage-3 lit-check trigger"). After each Stage-3 triager run, the orchestrator (not the triager agent) appends the new entry. When in doubt about whether wording matches, prefer firing — false re-fires are cheap, silent blocks are not.

## Step 6: Commit

`pipeline: stage 3 — implications developed and lit-checked (N novel, M puzzle-candidate, K supported)`
