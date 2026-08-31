# Lessons harvest — `finance-empirical-codex-2-d148cb33`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-codex-2-d148cb33`
**Run profile:** `finance` + `--ext empirical`, theory-first hybrid, **Codex runtime**. `status: complete`, `stage_10`, `problem_attempt: 1`. Shipped 2026-05-07. ~10 referee rounds; theory v3→v5 at Gate 4; Stage 6 ceilinged at field tier (editor Major Revision, MECHANISM-PARTIAL); converged JFQA. 48-page finance-theory paper ("Censorable Secondary Prices at a Financing Boundary").
**Tracks:** (A) self-graded lessons harvested; (B) `paper/main.pdf` (48pp) read holistically.

---

## Holistic read (Track B — the high-value part)

The paper **reads reasonably well on most presentation axes that earlier runs failed:**

- **Title** — `Censorable Secondary Prices at a Financing Boundary`. Jargony ("censorable") but **not an acronym**; clears the `75e5c9e` bar.
- **Abstract** — **prose, no notation wall** (clears `75e5c9e`). Dense with domain terms (retained veto, financing boundary, low signed prices) but no inline math / Greek.
- **Author** — `Anonymous` (the correct intentional anonymization value; **not** an `AUTHOR PLACEHOLDER` literal — #81 not triggered).
- **Cross-refs** — **all resolve, zero `??`** in the rendered PDF (#75 not present). `pdftotext | grep '??'` = 0.
- **Tables 3–7** — clean, legible, well-formatted; no clipping, no overfull `\hbox` (#51 gate fine).
- **Stage-9 gates worked** — polish-formula caught the load-bearing late error (missing no-opportunity continuation term in `eq:VVlambda`); polish-consistency caught the issuer-premium decomposition inconsistency; polish-prose stripped referee-response caveat stacking off page 1. These are exactly the substantive saves the gates are for.

Two reader-facing defects the self-grade is **totally blind to** (LESSONS never mention either):

### B1 (High, **NEW class**) — wide tables silently shrunk to **illegible** font via `\resizebox{\textwidth}{!}`; the #51 overfull gate is structurally blind to it

**Symptom.** Table 8 ("Direct model primitives unavailable in selected public records") and especially **Table 9** ("Proxy-to-primitive mapping and non-identification") render in **microscopic, unreadable font** in the shipped PDF (p46). Table 9 is a multi-column block of text too small to read at any normal zoom; Table 8 nearly so. These are not decorative — Table 8/9 are the **non-identification mapping that backs the paper's central empirical claim** (public records cannot identify the mechanism). The reader cannot extract any of it.

**Mechanism (confirmed in source).** Every table in `paper/sections/appendix.tex` is wrapped in `\resizebox{\textwidth}{!}{...}` (lines 11, 40, 78, 100, **135**, **142**). For narrow 2–3-column tables this scales them *up* to text width (fine). For the two **wide** auto-generated stage3a tables —
`\resizebox{\textwidth}{!}{\input{../output/stage3a/tables/direct_unavailable_primitives_v12.tex}}` (Table 8) and
`...proxy_theory_mapping_v12.tex` (Table 9) — it scales a very wide table *down* to text width, driving the font to microscopic.

**Why every current gate misses it — structurally, not by luck.** `\resizebox{\textwidth}{!}{}` forces the box to **exactly** `\textwidth`. It therefore **can never emit an `Overfull \hbox`**. The Stage-5 build-verify gate (`stage_5.md:66`, the #51 `04d51bb` overfull check: `awk` for `Overfull \hbox (NNNpt too wide)` > 40pt) is *guaranteed* to pass on a `\resizebox`-shrunk table — the very command that fixes the overflow is the command that destroys legibility. No polish agent reads rendered-table font size (verified: polish-numerics re-checks table *numbers*; polish-consistency checks figure *inclusion*; polish-identification checks diagnostic *presence* — none reads the rendered table's legibility). paper-writer has **zero** guidance on wide-table handling (no mention of `\resizebox`, landscape, column wrapping, or a font floor) — it appears to default to wrapping every table in unconstrained `\resizebox`, so the anti-pattern is uniform across all 7 of this paper's tables.

**Current-state verdict: OPEN.** Distinct from #51 (overfull-only; `\resizebox`-to-textwidth never overflows) and distinct from #71 (figure legibility — scoped explicitly to figures). It is the **table sibling of #71's "no agent reads the rendered exhibit for legibility" principle**, but with a *cheaply deterministic source signal* #71's render-and-read approach doesn't cover.

**Proposed fix (general, two complementary levers):**
1. **Source-level anti-pattern gate (cheap, deterministic).** Flag `\resizebox{\textwidth}{!}{...}` (and `\scalebox`/`adjustbox` with scale<1) wrapping a `tabular`/`\input` of a results table. The fix paper-writer should use instead: `\footnotesize`/`\scriptsize` + a wrappable column type (`p{}`/`\multicolumn`/`tabularx`), `\sidewaystable`/`landscape` for genuinely wide tables, or move the wide table to the IA in full-page landscape. A `\resizebox` *down* on a table is the defect; *up* (narrow→textwidth) is harmless and should not flag.
2. **Rendered-PDF legibility floor.** Estimate effective font size of the rendered table (e.g., glyph height from the table's bbox vs. row count, or detect `\resizebox` scale factor < ~0.6) and flag when it falls below a print-legible floor. This is the table analog of #71's option-(a) `polish-figures` rendered-legibility check — the same agent could own both.

**Severity: High** — a load-bearing table shipped unreadable, the anti-pattern is a paper-writer *default* (uniform across the paper), and it recurs for **any** paper with a wide auto-generated results/mapping table (every `--ext empirical` run that `\input`s a wide stage3a table is exposed). Keep general: the rule is "a results table is rendered illegibly small," not "this paper's proxy-mapping table." Skip in `--mode report`.

### B2 (High) — zero figures in 48 pages; contribution is a parameter-space operating region presented entirely as slack tables → **7th figureless run, folds into #71**

**Symptom.** `pdfimages -list` empty; the 7 "figure" matches in `pdftotext` are all the substring in *"con**figure**d"*. **No figure anywhere in 48 pages.** The paper's entire contribution is a **multi-condition operating region in parameter space** — Table 4 ("Operating-domain checks") lists 8 conditions each with a calibration slack; Table 6 ("Selected model-domain sensitivities") gives the holding interval per primitive. The canonical theory headline figure — a 2-D projection of the operating region (e.g., the (η_F, ρ_D) plane shading where all conditions jointly hold), or comparative statics of the issuer premium V_R−V_V across the financing boundary μ — is exactly what is rendered as slack tables. The reader must reverse-engineer the region from a table of numbers instead of *seeing* it.

**LESSONS blindness.** LESSONS_PAPER is broadly positive and **never mentions the absence of figures** — same self-grade blind spot as fe6/fe5/fe3/fe4/fe2.

**Mechanism = "never produced."** Like fe5/fe2, the figure was never produced upstream (theory-explorer emitted no region plot), so there is no `\includegraphics` for polish-consistency item 10's source-grep to fire on. paper-writer.md:181 *says* to write `[NEEDS THEORY-EXPLORER: headline figure]` when the headline warrants one and none exists, but nothing **enforces** that a region-characterization theory paper recognizes it warrants a figure. This is the residual #71 doesn't close: the gate is conditional on a figure being *produced*; figureless-because-never-produced slips through.

**New angle for #71's generality.** This is the cleanest **theory-paper** instance in the sweep (the natural figure is a region-in-parameter-space, not an event study), confirming the figureless floor spans theory and empirical runs alike — it strengthens #71's "keep general" clause (a rendered-exhibit / headline-warranted-figure check must help a paper whose figures look nothing like an event study). **Current-state: OPEN/PARTIAL, folds into #71** → corroborate #71 (7th figureless run; 3rd "never-produced" instance, 2nd in a theory-first paper after fe3).

---

## Self-lessons (Track A)

### A1 (Med, cost+quality-tail) — caveat treadmill after the theory ceilinged → **corroborates #78**

LESSONS_PIPELINE, verbatim diagnosis: *"What hurt quality was … repeated paper-level revision after Stage 6 once the theory had already hit a field-tier ceiling. Rounds r6–r10 kept improving exposition but also encouraged defensive caveats. The Stage 9 prose pass had to undo that accumulation. A future pipeline should detect this pattern earlier: if the same referee class keeps saying 'conditional but interesting,' the response should be to center the conditional result sooner, not keep adding caveats around a broader frame."*

This is the **same class as #78** (branch-manager's non-Regenerate Gate-4 strategic verdicts — here *center the conditional result / reframe away from the broad-transparency frame* — are not operationalized, so the run kept defending a broader frame for ~5 rounds instead of restructuring around the conditional headline). It also overlaps the within-tier early-convergence-exit note (fe3-L4 / fe4-A2). **Current-state: OPEN** (the machinery gap #78 describes). → **corroborate #78** (run carried a broad frame through ~10 rounds when r1-equivalent already wanted the conditional centered; Stage 9 had to undo the accreted caveats).

### A2 (note-only) — "some empirical work raises contribution; some only disciplines scope"

LESSONS_PIPELINE observes the Stage-3a descriptive audit *prevented overclaiming* (public records can't identify the mechanism) but *did not raise the tier* — and asks the pipeline to "track this distinction explicitly." Genuine and interesting, but it's a subjective scorer/contribution-accounting nuance with no clean gate. **Note-only**, not filed.

### A3 (out of scope) — Codex active-thread batching friction

LESSONS_PIPELINE flags operational friction launching agents in batches under active-thread limits (Codex runtime). Infra/runtime, not a template-quality defect. Out of scope.

---

## Closed-on-arrival / already-tracked

- **Abstract prose / non-acronym title** — clears `75e5c9e` (run shipped 2026-05-07, *predates* it, yet reads clean — corroborates the bar holding).
- **Clean cross-refs (no `??`)** — #75 defect absent.
- **No `PLACEHOLDER` on title page** — "Anonymous" is the correct value; #81 not triggered.
- **Tables 3–7 legible** — #51 overfull gate fine (these don't shrink).
- **Stage-9 substantive saves** — polish-formula/consistency/prose all caught real errors; gates worked as designed.
- **LIMITATIONS.md** — stock macro-id #18 only (no run-authored entries).

---

## Filing recommendation (pending operator go-ahead — outward-facing writes)

| # | Item | Sev | Current state | Action |
|---|------|-----|---------------|--------|
| B1 | Wide tables shrunk to illegibility via `\resizebox{\textwidth}{!}`; #51 overfull gate structurally blind | **High** | OPEN | **File new issue** (table sibling of #71; cross-ref #71 + #51) |
| B2 | 48pp theory paper, zero figures; contribution is a parameter-space region shown only as slack tables | High | OPEN/PARTIAL | **Corroborate #71** (7th figureless run; cleanest theory-paper / never-produced instance) |
| A1 | Caveat treadmill after theory ceilinged; "center the conditional sooner" | Med | OPEN | **Corroborate #78** |

No item duplicates an item that is ALREADY ADDRESSED/SUPERSEDED beyond what's noted. The single **new** issue is B1; B2/A1 are corroborations of existing open issues.
