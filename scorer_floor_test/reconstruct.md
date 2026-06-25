# Reconstruction task — distilled paper → pipeline internal artifacts

You translate ONE published-paper distillation into the set of internal artifacts
the autonomous research pipeline produces for a theory *before* it is evaluated.
You are reconstructing what the pipeline's own Stage-2 / Stage-3 / Stage-4 outputs
would have looked like had the pipeline produced this paper — which is an
already-published, peer-reviewed top-3 finance paper (J. Finance or RFS, 2025).

Your job is **faithful translation into a fixed artifact format**, not evaluation,
ranking, or improvement. Every claim you write must trace to the distilled page.
Do not embellish, inflate, strengthen, soften, or weaken anything. If the page
does not state something, omit it — never invent results, magnitudes, mechanisms,
or framing the page does not contain.

> You are NOT judging whether this paper is good, important, novel, or surprising,
> and you must not write any such judgment. You are transcribing the paper's
> content into the pipeline's internal artifact schemas. Tags you assign below are
> *structural classifications from a fixed rubric*, not praise.

## Input

The distilled page (YAML frontmatter + markdown prose) is at **{{PAGE_PATH}}**.
It contains: TL;DR, Core results (locators + magnitudes), Theory / model
(equations), Method, Empirical specifications, datasets, `relatesTo` (relations to
cited prior work), `openQuestions`, `findings[]`, `resultType`, `mechanisms`,
`contributionType`. Read the whole page before writing anything.

## Outputs

Write each file to the given path under **{{OUT_DIR}}**.

### 1. `theory/theory_v1.md` — reconstructed theory draft

Use exactly this section structure (it is the pipeline's theory-draft schema):

```
# [Model Name]
## One-sentence contribution
## Setup
### Environment
## Analysis
### Key result
### Proof
### Economic mechanism
## Comparative statics
## Connection to literature
## Implications
```

- **Model Name** — the paper's model/method name, or a short descriptive name.
- **One-sentence contribution** — the paper's single thesis in one sentence, from
  the TL;DR / abstract. (The form "X changes Y through mechanism Z" is fine.)
- **Setup / Environment** — primitives, agents, assumptions, from "Theory / model".
- **Key result** — the main proposition(s), stated precisely. Transcribe the key
  equations/propositions verbatim from "Theory / model" with their numbers.
- **Proof** — a faithful *sketch* of the derivation as the page presents it. You are
  not re-deriving anything; summarize the page's stated derivation and cite its
  equation references. If the page gives only an empirical method (no formal proof),
  write the identifying argument the page states instead, and say so.
- **Economic mechanism** — the economic story for why the result holds, from the
  TL;DR + "Theory / model".
- **Comparative statics** — directional / heterogeneity results the page reports
  (from Core results / `findings[]`), with their reported signs.
- **Connection to literature** — one line per `relatesTo` edge: what the cited prior
  does and how this paper builds-on / extends / tests it.
- **Implications** — the paper's headline empirical findings, from "Core results".

### 2. `output/stage3/implications.md` — tagged implications

Canonical schema (one block per headline implication):

```markdown
# Implications

## Implication 1: [one-sentence statement]
**Tag:** NOVEL
**Mechanism:** [why the theory generates this]
**Lit status:** [one line: what the literature established before this paper]
**Test design hint:** [data / method, if applicable]
```

Assign each implication exactly one tag by its **actual epistemic status relative
to the prior literature**, judged from the page's `relatesTo` edges, `resultType`,
and the paper's own confirming evidence — NOT by any desired outcome:

| Tag | Use when |
|-----|----------|
| **SUPPORTED** | The result restates something the literature already establishes (a `relatesTo` confirms/replicates edge, no new content). |
| **NOVEL** | A prediction/finding the literature had not established (`resultType` new-finding / new-method; `relatesTo` extends / first-to). |
| **PUZZLE-CANDIDATE** | The paper documents a sign reversal or order-of-magnitude discrepancy vs. a documented prior. |
| **DEAD** | Already proven uninteresting / always-true / always-false — drop from the list. |

Tag honestly and structurally. A faithful reconstruction of a genuinely new
published finding will carry NOVEL implications because that is what the paper is;
a paper that merely reconfirms known facts will carry SUPPORTED ones. Do not tune
tags toward any target — read the `relatesTo` relations and `resultType` and report
what they say. Keep SUPPORTED / NOVEL / PUZZLE-CANDIDATE; drop DEAD.

### 3. `output/stage4/self_attack.md` — adversarial self-critique

Schema:

```markdown
# Self-attack report

**Load-bearing premise:** [the single assumption the main result most depends on]

## Assumption attacks (target the load-bearing premise)
- [attack] — **Severity: N/10** — [why it threatens the result]

## Robustness attacks
- [attack] — **Severity: N/10** — [scope/edge-case concern]
```

Reconstruct the strongest objections a referee would raise, drawn from the page's
`openQuestions` and the tensions in its `relatesTo` edges. Name the load-bearing
premise honestly. Score each attack severity 1–10. This paper was accepted at a
top-3 journal, so its load-bearing premise survived peer review — reflect that
(do not manufacture a fatal attack the paper does not actually suffer), but do not
suppress real limitations the page itself flags in `openQuestions`. Robustness-style
attacks should be severity ≤ 6 unless the page itself flags a fatal one.

### 4. `process_log/pipeline_state.json`

Write exactly:

```json
{
  "current_stage": "stage_4",
  "theory_attempt": 1,
  "theory_version": 1,
  "pivot_round": 0,
  "pivot_resolved": false,
  "triaged_lit_implications": [],
  "target_journal_tier": "top-3-fin",
  "initial_journal_tier": "top-3-fin",
  "status": "in_progress",
  "seeded": false,
  "faithful": false,
  "scores": {}
}
```

### 5. Stipulated audit stubs

The paper was published in a top-3 finance journal, so it is rigorous, novel, and
well-posed by construction. Write thin PASS/NOVEL stubs (these stand in for audits
the pipeline ran and passed):

- `audits/math_audit.md` — `PASS`. One line: the transcribed equations are internally
  consistent as presented. Add a `## Unverified claims` heading with `(none)` under it.
- `audits/math_audit_freeform.md` — `PASS`. One line.
- `audits/novelty_idea.md` — `NOVEL` (Gate 1b). One line referencing the contribution's
  novelty vs. the `relatesTo` priors.
- `audits/novelty_theory.md` — `NOVEL` (Gate 3). One line.

### 6. `meta.json`

```json
{
  "slug": "{{SLUG}}",
  "journal": "{{JOURNAL}}",
  "source_page": "corpus/raw/{{JOURNAL}}/{{SLUG}}.md",
  "reconstructed_from": "frozen IAR distilled-lit snapshot",
  "note": "Rubric-blind reconstruction for the scorer floor test (#102). Frozen — do not regenerate except on an input-schema change."
}
```

## Provenance scrub (critical — the reconstruction must look like a *fresh* draft)

The pipeline's own Stage-2 theory draft is generated from scratch; it has **no idea
it corresponds to any published paper.** So the reconstructed `theory_v1.md` must
carry **none of the tells that it was transcribed from a published article** —
otherwise the scorer correctly flags it as a reproduced/known result and fails the
novelty hard-requirement (H4), which is a fixture artifact, not a real signal.

Strip every one of these from `theory_v1.md` (they do NOT belong in a fresh draft):
- **Page locators of the source** — no `p. 1743`, `pp. 2815–2841`, `(Section I, p. …)`.
  Keep equation/proposition/section *numbers* (`eq. 1`, `Proposition 3`, `Section I.B`) —
  a fresh draft has those — but never a page number into the source PDF.
- **The paper's own authors as the source of the model** — no author-named model title
  (e.g. `… (Clayton & Schaab)`), no "as shown in [thisauthor] (2025)" for the current
  result. Use a descriptive model name only.
- **Journal / DOI / volume / "published" framing** of the current paper.

Citing *prior* literature by name+year (the `relatesTo` edges, in Setup and
Connection-to-literature) is correct and expected — a real draft cites the work it
builds on. The prohibition is on the draft betraying that it *is itself* a specific
published article.

## Hard rules

1. **Faithful, not flattering.** Trace every claim to the page. No invented content.
2. **No editorial judgment.** Do not write that the paper is important/surprising/
   novel/strong/weak in your own voice anywhere. Transcribe; classify with the fixed
   tags; stop.
3. **Tags are structural, not strategic.** Read `relatesTo`/`resultType` and report.
4. When the page gives an empirical (not theoretical) paper, the "theory draft" is the
   paper's identifying argument + reduced-form mechanism; keep the same section
   skeleton, write the proof section as the identification argument, and say so.
