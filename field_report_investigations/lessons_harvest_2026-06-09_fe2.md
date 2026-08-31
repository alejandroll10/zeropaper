# Lessons harvest — `finance-empirical-2-c9efedfb`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-2-c9efedfb`
**Run type:** `finance` + `--ext empirical`, theory-first hybrid (launched from "start the pipeline; reduced-form SDF, equities optional or not"; de-mechanized to empirical-only over 10 referee rounds)
**State:** `status: complete`, `current_stage: stage_10`, `problem_attempt: 1`. Shipped 2026-05-08.
**Tracks:** (A) self-graded lessons harvested; (B) 43pp `paper/main.pdf` read holistically.

---

## Summary verdict

A genuinely good *empirical-content* run — JFQA-ready, honestly scoped, methodologically careful (Driscoll-Kraay primary / two-way conservative bound / wild-cluster-bootstrap finite-sample protocol; COVID-drop placebo distribution; Frisch-Waugh decomposition of the Cao attenuation). The self-lessons are detailed and unusually honest about cost (10 rounds used; theory apparatus over-invested then deleted).

**But the holistic read surfaces three presentation defects the self-grade is blind to** — and all three are the *same classes already tracked*, here as additional corroborating instances (the run predates the fixes):

1. **Zero figures in 43 pages** despite ready headline figures → corroborates **#71** (6th figureless run).
2. **`[AUTHOR]` placeholder shipped on the title page** → corroborates **#81** (2nd run; *different literal string* — strengthens the "placeholder class" framing).
3. **Table 1 clipped at the right margin** (HY rating-bucket column ran off the page) → **ALREADY ADDRESSED** by the overfull-`\hbox` build-verify gate (`#51`, `04d51bb`, 2026-06-01; run predates it). 2nd table-clip instance after fef3-B1.

Plus two process-cost lessons that corroborate **#77** and **#78**.

No new fileable OPEN item. Everything maps to an existing open issue or is closed-on-arrival.

---

## Track B — holistic read

### Title
"Within-Firm Option-Surface Curvature Predicts the Equity-Orthogonal Bond Residual." **Not an acronym title and has a verb ("Predicts"), so it clears the `75e5c9e` acronym/notation title bar** — but it is jargon-dense ("Equity-Orthogonal Bond Residual," "Option-Surface Curvature" are opaque to a non-specialist). Borderline; **note-only**, not a fileable defect (the `75e5c9e` gate targets acronym/notation titles, which this is not; jargon-density on an otherwise descriptive title is subjective).

### Abstract
Prose-structured (no equations-as-sentences) but **notation-heavy**: `β_firm = +1.21 (t_DK6 = +2.31)`, `ρ_w = −0.056`, `+0.97, t_DK6 = +2.08`, repeated rating-subsample betas. Reads as a wall of numbers and Greek in places. → **ALREADY ADDRESSED** by `75e5c9e` (polish-prose >100-word + notation critical); run shipped 2026-05-08, predates it. Closed-on-arrival; corroborates the abstract-method-name/notation residual seen in first-4 / first-5.

### Figures — **zero, in 43 pages (Track-B headline finding → #71)**
- `pdfimages -list` empty; `grep -c -i figure` on the rendered text = **0** (not one figure, not one reference to a figure, anywhere).
- The paper has *multiple* natural headline figures it never draws:
  - The **COVID-drop placebo distribution** (COVID at the 2.3rd percentile of 86 overlapping 10-month windows, 3 SDs below the placebo mean) — a textbook histogram-with-vertical-line, and the paper's single strongest defense against a fragility critique.
  - The **12-month rolling-SD time series** of the headline regressor.
- **Mechanism (sharpens the fe5 sub-gap):** figures *were* produced upstream — `output/stage2b/figures/*.png` (theory exploration) and `output/stage3a/figures/{hy_signflip,itm_oom_decomposition}.png` (pre-restructure empirical scratch) — but **none live in `paper/`**, and none is the empirical headline figure. After the de-mechanization restructure, the final empirical paper rendered *no* figure and the placebo histogram was *never rendered for the paper at all*. This is the "figureless-because-never-produced-**for-the-paper**" path: the dropped-figure gate (`polish-consistency.md:24`, item 10) keys on a `\includegraphics` being present in source — with none present and none ever generated for `paper/`, the gate has nothing to fire on. The natural-headline-figure-was-never-drawn class is exactly what a rendered-PDF figure-presence + "empirical paper with a placebo/event-study result ⇒ expect ≥1 figure" check (the #71 direction) would catch.
- **LESSONS-blindness, vivid:** neither `LESSONS_PAPER.md` nor `LESSONS_PIPELINE.md` mentions the absence of figures *once*. The self-grade is entirely about inference rigor and scope honesty — confirming the systematic blindness this sweep exists to cover.

### Tables — one clipped (→ #51, closed-on-arrival)
- **Table 1** (within-firm panel by rating bucket) is **clipped at the right page margin**: the IG column's t-stats end `...t_FC = +4.01) +` with the **HY column running off the page** (the Note discusses HY firm counts for a column the reader cannot see). A plain wide `tabular` with three full stat-columns and no width management.
- The clipping is large (an entire column off-page ⇒ overfull `\hbox` well over the 40pt threshold), so the build-verify overfull gate (`stage_5.md:66`, added `#51` on 2026-06-01) **would catch it in a current run**. Run shipped 2026-05-08, predates the gate → **ALREADY ADDRESSED**, closed-on-arrival. 2nd table-clip instance after fef3-B1; reinforces #51's value.
- All **other tables read cleanly** and **every cross-ref resolves** — `grep -c '??'` = 0 (Section 6, Table 9, Section 5.1, Table 2 all live links). On cross-refs and non-clipped tables this is a clean-reading paper (no #75 "??" defect). Prose is readable, with a reader-friendly "Reader's guide to β_agg" roadmap device.

---

## Track A — self-lessons (current-state verified)

| Lesson (from LESSONS_PIPELINE / PAPER) | Current-state verdict | Disposition |
|---|---|---|
| **paper-writer hallucinated numbers in r6** — LASSO retained coefs (3 fabricated) + DD-cutoff sensitivity (3 of 4 fabricated); caught only by polish-numerics recompute. Self-lesson asks for `[VERIFY: source]` placeholders instead of guessing. | **OPEN** — paper-writer is a self-grading producer with no independent apply/source-grounding check upstream of Stage 9 | **DUPLICATE → #77** (apply-verifier). 3rd instance of the unverified-producer theme (fe3-L2 grid-count fabrication was prior); argues apply-verifier should source-ground *authored numbers*, not only check edit-landing. **Corroborate #77.** |
| **Theory apparatus over-invested then deleted** — Theorem 1 math-PASS at Gate 2 (v6), byte-identical v6→v12, demoted Prop 1 (r5) → Appendix Remark (r6) → deleted (r10). 5 rounds to reach the empirical-only restructure the r1 freeform asked for. | **OPEN** — a theory-first run that should have restructured to empirical-only early; the slow de-mechanization is the "carry full theory apparatus into a field frame for a multi-round detour" symptom | **DUPLICATE → #78** (operationalize branch-manager Gate-4 Restructure/tier-reframe). **Corroborate #78.** |
| Freeform Reject votes that are **restructure-driven, not quality-driven**, should route through a deepen-mandate Major-Revision variant rather than wait for structured convergence (self-lesson's "one thing I'd change"). | **OPEN** but subjective/cost-only routing-judgment; partially overlaps #78's tier-reframe and the editor's Rule-2 escape | **DROPPED / note-only** — real but subjective, cost-only, and hard to gate without false positives. Adjacent to #78; not separately fileable. |
| "1,320 bps/month annualized" self-contradictory unit label survived 9 rounds; caught by polish-consistency r2. | **OPEN but DROPPED** — Stage 9 polish-consistency owns it and caught it pre-ship; realized harm 0 | Stage-9-owned, same disposition as fe4-A3 / fe5 formula-typo shift-left. |
| Driscoll-Kraay SE fix / mechanism-referee de-mechanization / COVID-placebo discovery / surprises-as-discoveries | **system working** — these are *what helped*, not defects | No action. |
| `LIMITATIONS.md` = stock macro-id `#18` only (no run-authored entries) | documented-deferred | Closed-on-arrival. |

---

## Disposition for operator (pending go-ahead per method step 8)

**No new issue to file** — all OPEN candidates duplicate existing open issues. Proposed outward actions (corroboration comments only):

1. **#71** (figureless body) — 6th figureless run; figures produced only in `stage2b/stage3a` scratch dirs, none in `paper/`; placebo-distribution headline figure never rendered for the paper. Vivid LESSONS-blindness (zero mention of missing figures).
2. **#81** (placeholder ship) — 2nd run; **different literal** (`[AUTHOR]` vs fef2's `AUTHOR PLACEHOLDER`) — confirms the guard must catch the placeholder *class*, not a fixed string.
3. **#77** (apply-verifier / unverified producer) — 3rd instance; LASSO + DD-cutoff fabricated numbers caught only at Stage 9; argues apply-verifier should source-ground authored numbers.
4. **#78** (branch-manager Gate-4 Restructure) — slow 5-round de-mechanization of a theory-first run that should have restructured to empirical-only early.

**Closed-on-arrival (no action):** Table 1 clip → #51; abstract notation → `75e5c9e`; silent polish-write → `3fba5cf`; macro-id → #18. **Note-only:** jargon-dense (non-acronym) title; restructure-driven freeform-Reject routing.
