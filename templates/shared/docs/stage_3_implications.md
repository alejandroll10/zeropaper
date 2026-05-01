# Stage 3: Implications

**Orchestrator task + `gap-scout` per implication**

## Step 1: Derive implications from the theory

Read the theory draft. Work out:

- Testable predictions (signed comparative statics, magnitude predictions, qualitative patterns)
- Comparative statics (how results move with parameters)
- Special cases that recover known results (nested baselines)
- Economic intuition for each result (in words, not algebra)

Aim for 3–6 distinct implications. Quality over quantity — each should be a sentence a reader could test.

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

If ALL implications come back SUPPORTED, the theory may be reinventing known results. Note this in the file and flag for the scorer at Gate 4 — likely a low Surprise / low Novelty score, possibly grounds for theory revision before paper-writing.

If ANY implication is PUZZLE-CANDIDATE, **launch `puzzle-triager` now** with the gap-scout lit-check report(s) as the contradicting evidence — do not wait for Stage 3a/3b. The literature contradiction (sign reversal or order-of-magnitude discrepancy) is itself the contradiction. Follow `docs/stage_puzzle_triage.md`. A literature-grounded contradiction in a well-audited theory is the highest-value pivot opportunity; defaulting to "ship as a noted puzzle" leaves real signal on the table.

**Re-fire guard (prevents loops on Stage 3 re-runs).** Before launching the triager, check `pipeline_state.json:triaged_lit_implications`. For each PUZZLE-CANDIDATE implication, canonicalize its one-sentence statement (lowercase + whitespace-collapsed) and look up the resulting `implication_key`. Fire the triager only if no entry with `verdict: "FIX-EMPIRICS-b"` matches — that is the sole terminal verdict that blocks re-firing. RECONCILE, BACK-TO-IDEA, HONEST-NULL, and PIVOT do not block; the orchestrator clears the relevant entries when those verdicts fire (full schema, canonicalization rule, and reset semantics in `docs/stage_puzzle_triage.md` "Re-fire guard for the Stage-3 lit-check trigger"). After each Stage-3 triager run, the orchestrator (not the triager agent) appends the new entry. When in doubt about whether wording matches, prefer firing — false re-fires are cheap, silent blocks are not.

## Step 6: Commit

`pipeline: stage 3 — implications developed and lit-checked (N novel, M puzzle-candidate, K supported)`
