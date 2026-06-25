# Scorer floor test — pilot findings

6 reconstructed top-3 finance papers (corpus `f6e0791a`), scored by the real
assembled finance scorer (`opus`), **routed per paper** to the scorer config its
pipeline route would use, ×2 runs/fixture (means). Re-derive with
`run_floor_test.py --report-only` on a machine that has run the scorer.

## Final routed result

| Paper | route | total | Imp | Nov | Sur | Rig | Par | Fer | verdict |
|---|---|---|---|---|---|---|---|---|---|
| betermier  | theory-first    | 82.6 | 85 | 82.5 | 81 | 80 | 80 | 85 | ADVANCE |
| bhutta     | empirical-first | 82.3 | 85 | 85 | 79 | 80 | 82.5 | 80 | ADVANCE |
| clayton    | theory-first    | 76.9 | 83.5 | 76.5 | **62.5** | 80 | 83.5 | 75 | ADVANCE (Surprise breach) |
| donaldson  | theory-first    | 81.0 | 83.5 | 85 | 75 | 80 | 80 | 82.5 | ADVANCE |
| dugast     | theory-first    | 81.4 | 83.5 | 80 | 80 | 80 | 80 | 83.5 | ADVANCE |
| greenwood  | descriptive     | 71.8 | 74.5 | 65.5 | 63 | 76.5 | 85 | 70 | OUT-OF-SCOPE |

**In-scope decision-level false-negatives: 0/5.** Every paper the pipeline could
produce advances (76.9–82.6). Dimension breaches: Surprise 1/5 (clayton only).

## What the test established (in order)

1. **Surprise was systematically harsh for theory papers.** First run: 4/6 below
   the 75 bar (incl. pure-theory clayton/donaldson), median 72. The scorer reserved
   ≥75 almost entirely for sign/magnitude *reversals*, dumping novel-mechanism
   results on a `= 60` anchor with nothing between 60 and 85.

2. **The most recent Surprise edit (`8fd9012`) had aimed at exactly this and not
   landed.** It broadened the top tier in wording but kept the 60 anchor and the
   60→85 void, so the scorer kept choosing 60. The floor test is what showed the
   edit under-delivered — a family-internal A/B could not have.

3. **Fix applied + A/B-verified.** Inserted a `= 75` rung
   (`SURPRISE_CALIBRATION`, all 3 variant vocabs) for "a result a knowledgeable
   reader could not have called ex-ante — a novel mechanism / non-obvious structural
   result / a comparative static whose sign the field could not predict — even with
   no documented prior to overturn, and even when it holds only under stated
   assumptions," plus "a sign/magnitude reversal is *sufficient but not necessary*."
   Result: theory papers moved to 75–81 (betermier 81, dugast 80, donaldson 75).
   A review confirmed **no leniency hole** (the 60/75 boundary turns on the crisp
   "could the field call it ex-ante" gate; mediocre work stays at 60).

4. **Parsimony was already well-calibrated** (0/5 below, the `acedcbb` retune is
   sound) — the test cleared it, not just flagged harshness.

5. **A contamination bug in the fixtures, caught by replication.** clayton ×3
   surfaced a `0` run: a real H4 (novelty) FAIL because the reconstructed drafts
   carried source **page numbers** and an **author-named title** — tells that a
   fresh Stage-2 draft never has. Fixed `reconstruct.md` to forbid provenance tells
   and scrubbed all locators from every scorer-input file. (This is why
   `--repeat N` exists: a single draw hid it.)

6. **Empirical papers were mis-scored by the theory-first scorer — and routing
   fixed it.** Pre-routing, bhutta scored 68.0 (REVISE) under the theory-first
   scorer (no empirical H3, theory Surprise/Novelty anchors). Routed to the
   empirical-first scorer it would actually face, **bhutta scores 82.3** (Surprise
   58 → 79). The ~14-point swing *was* the wrong-scorer artifact, now closed.

## clayton — the one holdout (accepted)

clayton's Surprise is genuinely **unstable**: 60–76 across runs (this run 60–65,
an earlier clean run 68–76 — non-overlapping). It is a mechanism-surprise theory
paper the scorer keeps half-wanting a sign reversal from; the `=75` rung lifted it
off a flat 60 but it straddles the bar. It **advances at 76.9** regardless. Accepted
as a borderline, high-variance case rather than tuned further against noise — which
is exactly the call `--repeat N` lets us make on evidence.

## Routes

The pipeline has two scoring routes; the corpus needs a third *exclusion*:
- **theory-first** — formal-model papers (betermier, clayton, donaldson, dugast).
- **empirical-first** — causal-identification papers (bhutta). Scored with the
  finance+empirical_first vocab overlay, ef/xe markers on, the injected Fertility
  addendum, and the Stage-3a audit chain for H3.
- **descriptive** (greenwood) — reduced-form measurement, no model and no causal
  estimand. Fits *neither* route (empirical-first's causal-estimand guard hard-fails
  a descriptive H1/H5). Scored theory-first for reference but **excluded from the
  verdict** — the pipeline does not target descriptive papers, so its low score is
  out-of-distribution, not a rubric bias. A real finding about the scorer's coverage.

## Scope reminder

One-sided by construction — anchors the bar from below only. It cannot detect a
*lenient* scorer (no negatives in the corpus); that is #98.
