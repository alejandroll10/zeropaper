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
| **PUZZLE-CANDIDATE** | Literature shows the OPPOSITE of what the theory predicts | High priority + flag for puzzle-pivot mode if empirics confirm the contradiction |
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

If ANY implication is PUZZLE-CANDIDATE, note that the empirical stage may trigger a puzzle-pivot if the data confirms the contradiction. The paper's framing may pivot from "theory + tests" to "puzzle + resolving mechanism."

## Step 6: Commit

`pipeline: stage 3 — implications developed and lit-checked (N novel, M puzzle-candidate, K supported)`
