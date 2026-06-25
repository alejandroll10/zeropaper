# Scorer floor test — pilot findings

12 reconstructed top-3 finance papers (corpus `f6e0791a`), scored by the real
assembled finance scorer (`opus`), **routed per paper** to the scorer config its
pipeline route would use, ×2 runs/fixture (means). Balanced 6 theory-first /
4 empirical-first / 2 descriptive. Re-derive with `run_floor_test.py --report-only`.

## Calibration result (12 papers, committed 5-anchor Surprise)

| Paper | route | total | Sur | verdict |
|---|---|---|---|---|
| betermier | theory-first    | 82.8 | 80   | ADVANCE |
| bolton    | theory-first    | 81.5 | 82.5 | ADVANCE |
| donaldson | theory-first    | 82.0 | 78.5 | ADVANCE |
| dugast    | theory-first    | 81.7 | 79   | ADVANCE |
| buffa     | theory-first    | 78.8 | 73.5 | ADVANCE (Surprise breach) |
| clayton   | theory-first    | 77.5 | 70   | ADVANCE (Surprise breach) |
| bhutta    | empirical-first | 80.7 | 76   | ADVANCE |
| frame     | empirical-first | 81.3 | 75   | ADVANCE |
| custodio  | empirical-first | 81.4 | 67.5 | ADVANCE (Surprise breach) |
| andreani  | empirical-first | 77.1 | 71.5 | ADVANCE (Surprise breach) |
| cakici    | descriptive     | 76.4 | 81   | OUT-OF-SCOPE |
| greenwood | descriptive     | 71.3 | 62.5 | OUT-OF-SCOPE |

**In-scope decision-level false-negatives: 0/10.** Every paper the pipeline could
produce advances (77.1–82.8) — the scorer's *aggregate* gate calibration is sound
across a balanced 10-paper set. Dimension breaches: Surprise 4/10.

**The 4 Surprise breaches split into two kinds, only one of which is a problem:**
- *Genuinely-surprising theory near the bar* (buffa 73.5, clayton 70) — the residual
  harshness the `=75` rung narrowed but didn't fully close on the most borderline
  cases. High run-variance (clayton 60–76 across runs); both still advance.
- *Confirmatory-direction empirical* (custodio 67.5, andreani 71.5) — **arguably
  correct.** custodio (a financial-education RCT that improves financial practices)
  and andreani (CEOs rewarded for luck, extending a known phenomenon) are valuable
  for identification + importance, not for surprising direction. A low Surprise here
  is the rubric working, not failing — and they advance on aggregate regardless.

This is the per-dimension-floor's known limitation surfacing cleanly: a published
top-3 paper can be legitimately moderate on Surprise while clearing the gate. The
*decision-level* guard (0/10) is the trustworthy signal; per-dimension Surprise is
a diagnostic, and on 12 papers it points at "a couple of borderline theory papers,"
not systematic harshness.

## Simplification A/B — 3-tier Surprise rubric, REJECTED

Tested whether the 5-anchor `SURPRISE_CALIBRATION` (+ the two patch-clauses) could
be replaced by a cleaner 3-band rubric (high / anticipatable / unsurprising), per
the "prefer removing rules" principle. Matched A/B, 12 papers ×2.

**Verdict: the floor test rejected it.** The 3-tier did not lift its targets
(buffa 73.5→74.5 still sub-bar; clayton 70→68.5 *worse*), it *regressed* a clean
paper (betermier 80→74.5, a new breach), in-scope Surprise breaches went 4→5, and
the confirmatory empirical custodio drifted *up* (67.5→71.5, the leniency
direction). Most deltas are within run-noise, but the burden was on the
simplification to prove "at least as good," and it didn't.

**Why — the useful lesson:** collapsing the explicit `=75` anchor into a "75–89
band" gave the grader less to grip, so it reverted to its sign-reversal instinct and
drifted *down*. **The explicit 75-anchor is load-bearing, not decorative.** A real
data point for the #101/"remove rules" debate: here, the over-specified rule earns
its keep, and the floor test is what let us find that out empirically instead of
assuming. Kept the committed 5-anchor version.

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
