# Lessons harvest — `finance-empirical-first-2-e7fc624b`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-first-2-e7fc624b`
**Run:** finished, `status: complete`, `current_stage: stage_10`, `problem_attempt: 1`. **Empirical-first mode** (`pipeline_state.json` `mode` field unpopulated/`None`, but LESSONS + section structure — `identification`/`mechanism`/`data`/`results`, no `model`/`theorem`, Stage 2/2b math-auditor skipped — confirm empirical-first). 6 theory/mechanism versions, 1 puzzle-triager PIVOT, 1 Stage-6 Reject-deepen, 2 polish rounds. Tier downgraded twice: top-3-fin → field (Gate 4 v4) → letters (Gate 5 r1); converged JFIP/letters. **Shipped 2026-05-16.**
**Paper:** "Long-Run Plan-Asset Effects of Recession-Driven 401(k) Match Suspensions: Bounds from Identification Choice" — Form 5500 DiD/SDID on 2009 match suspensions; headline is a bounds-from-identification-choice characterization (|ATT| ∈ [0.072, 0.245] depending on whether you condition on post-suspension participant count). 25pp main + 11pp IA.

---

## Track B — holistic read (the high-value part)

- **Title — GOOD.** Plain language, no acronym, names the economic object and the finding ("Bounds from Identification Choice" is an abstract-but-honest subtitle). Reads well.
- **Abstract — GOOD.** Prose-dominant, states the result up front (−7.2% lower / −24.5% upper bound, the single specification choice that drives it). Method-acronym-dense (TWFE, SDID, AAHIW, NAICS2 in one paragraph) but each is a standard name; no notation wall.
- **Figure 1 (mechanism DAG) — GOOD, legible.** Clean TikZ per-cohort causal DAG, self-contained caption defining every node and the bound logic. One of the better mechanism exhibits in the sweep. Renders fine (it's vector/TikZ, so `pdfimages` shows 0 *raster* images but the figure is present).
- **Tables — legible.** No clipping/truncation signature (contrast fef3 Table 2).

### D1 (HIGH, NEW) — `AUTHOR PLACEHOLDER` shipped on the title page

The title block reads **`AUTHOR PLACEHOLDER`** — a literal unfilled skeleton token, on page 1, the first thing any reader sees. (`main.tex:35` = `\author{AUTHOR PLACEHOLDER}`.) fe4 shipped a real author ("Alejandro Lopez-Lira"), so this is intermittent, not universal — which points straight at a guard gap.

**Current-state verdict: OPEN.** The skeleton ships `\author{AUTHOR PLACEHOLDER}` (`templates/paper_skeleton/main.tex.template:32`, `internet_appendix.tex.template:59`). paper-writer is told to "Edit `\title`, `\author`, `\date`… freely" (`paper-writer.md:144`) and has an explicit **never-ship guard for the *title* only** — `paper-writer.md:161`: "Replace `TITLE PLACEHOLDER` — never ship the placeholder." **There is no equivalent guard for `AUTHOR PLACEHOLDER`** (nor for `\date`/abstract tokens), and the Stage-5 build-verify gate (`stage_5.md:64-66`) greps `main.log` for undefined citations + overfull-`\hbox` but **never greps the rendered PDF (or `main.tex`) for residual `PLACEHOLDER` tokens.** So an unfilled author (or any other skeleton placeholder) ships silently.

**Proposed general fix (placeholder *class*, not just author):**
1. Extend the paper-writer never-ship guard from `TITLE PLACEHOLDER` to the **full skeleton-placeholder class** — `AUTHOR PLACEHOLDER`, and any `… PLACEHOLDER` token the skeleton ships (`paper-writer.md:161` + the file-list at `:144-145`).
2. Add a **Stage-5 build-verify residual-placeholder grep**: `pdftotext main.pdf | grep -i PLACEHOLDER` (and/or grep `main.tex`/`internet_appendix.tex`) must return nothing — fail the gate if any survives. This is a cheap, deterministic, mode-agnostic check that catches *any* unfilled token, not just the author.

Generality: helps any paper that leaves any skeleton token unfilled, regardless of which field; reader-facing (title page) and desk-reject-grade when it fires. Natural sibling of #75 (both are Stage-5 *rendered-PDF sanity greps*) — could be implemented together as one "rendered-PDF sanity sweep" (residual `??` + residual `PLACEHOLDER` + (per #75) `Reference.*undefined`).

### C2 (#75, 2nd run) — 7× "Internet Appendix `??`" dangling cross-document refs

The body says "Internet Appendix **??**" seven times (e.g. "Internet Appendix ?? reports the full sensitivity grid"; "Internet Appendix ??–?? report the full event-study…"). These are `\ref`s to labels in the **separately-compiled `internet_appendix.tex`**, which `main.pdf` cannot resolve → literal `??`. This is **exactly the #75 mechanism** (cross-document IA refs ship as `??`; intra-doc refs fine). **fef2 is the 2nd run to hit #75** (fe5 was the 1st). Worse here: the IA the prose points to (11pp) contains **0 figures and 0 of the referenced exhibits** (see C1) — so even a resolved ref would point at nothing.

**Current-state verdict: OPEN.** Build-verify (`stage_5.md:64`) greps `Citation.*undefined`, not `Reference.*undefined`, and nothing greps the rendered PDF for `??`. → **Corroborate #75** (2nd run; 7 instances; all cross-document IA refs).

### C1 (figure: event-study result figure produced but included nowhere) — ALREADY ADDRESSED

Four event-study figures were produced (`output/stage3a/figures/{event_study_g2008,event_study_g2009,log_ec_trajectory,sdid_decomposition}.pdf`) but are **`\includegraphics`'d nowhere** — 0 references in any section, in `main.tex`, or in `internet_appendix.tex`. The IA PDF (11pp) has 0 embedded images and 0 figure captions, despite the body repeatedly saying the IA "reports the full event-study." So the **headline empirical *result* figure of a causal event-study paper is absent from the entire document.**

**Current-state verdict: ALREADY ADDRESSED (run predates the fix by 3 weeks).** The dropped-figure gate (`polish-consistency.md:24`, item 10) + mandatory-empirical-headline-figure rule both landed **2026-06-05** (`3fba5cf`, `75e5c9e`); fef2 shipped **2026-05-16**. In a current run, item 10 fires **major** here (stage3a/figures has PDFs and `\includegraphics` count is 0 everywhere). Closed-on-arrival.

**Residual (corroborates #71).** item 10 fires only if **no** `\includegraphics` appears *anywhere*. fef2 escaped masking only because its one figure (the DAG) is TikZ, not `\includegraphics`, so the count stayed at 0. A paper with a `\includegraphics`'d schematic/DAG/logo + missing *result* figures would have count ≥ 1 and item 10 would **not** fire — exactly #71's case for a **rendered-result-figure-specific** check (not "any figure exists"). → light **corroborate #71**.

---

## Track A — self-graded lessons, current-state checked

| Lesson | Current-state verdict | Disposition |
|---|---|---|
| **Add a lightweight "mechanism-plausibility" auditor between Stage 2 and Stage 3 in empirical-first mode** (channel-ambiguity Pathway A/B/firm-fundamentals slipped to Stage 5/6 referees; empirical-first has no math-auditor and referee-mechanism fires only at Stage 6) | **OPEN.** Empirical-first Stage 2 produces a prose+DAG mechanism with no auditor between it and Stage 3; nothing gates mechanism plausibility until referee-mechanism at Stage 6. 2nd run wanting earlier mechanism checks in empirical-first (fe4's LESSONS wanted earlier mechanism validation too, theory-first). | **Surface to operator** (Med, design question — "mechanism plausibility" at prose+DAG stage is partly subjective and overlaps identification-auditor/referee-mechanism). Operator discretion. |
| Empirical-first mechanism **posit arithmetic unaudited until Stage 9** (M̄ = 1.486→1.489 error survived 3 revision rounds, caught only by polish-formula) | **OPEN but DROP.** math-auditor is correctly not launched in empirical-first (`stage_2.md:60`); polish-formula owns the final check and *did* catch it. Realized harm = a wrong value propagated into the IA + referee reports for a few rounds (cost), not a ship defect. Same disposition as fe5/fe4 formula shift-left. | DROP (Stage 9 owns). Note. |
| **Identification design → rendered-paper drift** (Stage 1 committed bacondecomp+Callaway-Sant'Anna; rendered paper uses TWFE primary + SDID upper-bound; divergence unexplained until polish-identification r1) | **OPEN but DROP.** Stage 9 polish-identification owns it and caught it pre-ship. **3rd run on this theme** (fe3-A2, fef3-A2 were 1st/2nd — all DROPPED, Stage 9 owns). | DROP (Stage 9 owns). Note recurring. |
| Raise polish hard cap 2→3 when round-1 triage ≥30 Apply items (round-2-introduced-by-round-1 contradictions) | OPEN, subjective cap-tuning; the run judged the cap "right, just needed more rounds." | Note-only. |
| `robustness.tex` not `\input` by `main.tex` (potential orphan, cf. fe4) | **Benign.** It is an intentional 5-line no-op stub (all comment lines, 0 content). fe4's proposed orphan-detection gate keys on ">0 **non-comment** lines unreachable" → correctly would **not** flag this. **Validates the fe4/#71 orphan-gate design.** | Note (positive validation of the proposed gate). |
| scribe not launched / stall-check cron `*/59` cadence | Operational/infra. | Out of scope. |
| Macro-id (LIMITATIONS stock) | `#18`. | Documented-deferred. |

---

## Backlog (prioritized)

| ID | Pri | Type | Item | Verdict | Disposition |
|----|-----|------|------|---------|-------------|
| D1 | **High** | Quality | `AUTHOR PLACEHOLDER` (skeleton token) ships on the title page; only `TITLE PLACEHOLDER` is guarded, no rendered-PDF placeholder grep | OPEN | **File** (pending go-ahead): extend never-ship guard to the placeholder class + Stage-5 residual-`PLACEHOLDER` grep. Sibling of #75. |
| C2 | High | Quality | 7× "Internet Appendix `??`" dangling cross-document refs | OPEN (#75) | **Corroborate #75** (2nd run). |
| C1 | — | Quality | Event-study result figure produced but `\includegraphics`'d nowhere (incl. IA) | ALREADY ADDRESSED (`3fba5cf`/`75e5c9e`; predates) | Closed-on-arrival; residual → **light corroborate #71** (result-figure-specific check). |
| A-mech | Med | Quality | No mechanism-plausibility auditor in empirical-first between Stage 2 and Stage 3 | OPEN | Surface to operator; design question. |

**Closed-on-arrival / DROP / note:** mechanism-arithmetic shift-left (DROP, Stage 9 owns); id-design→rendered drift (DROP, Stage 9 owns, 3rd run); polish cap 2→3 (note, subjective); `robustness.tex` orphan (benign — validates fe4 orphan-gate design); macro-id `#18`; scribe/cron infra.

## Outward-facing writes — DONE (operator go-ahead 2026-06-09)
1. **D1 filed as #81** — extend never-ship guard to the placeholder class + Stage-5 residual-`PLACEHOLDER` grep (sibling of #75).
2. **#75 corroboration posted** — 2nd run, 7× "Internet Appendix `??`" (sharper: IA has 0 referenced exhibits).
3. **#71 light-corroboration posted** — result-figure-specific residual (item 10 masked by a single non-result figure; here TikZ DAG kept count at 0).
4. **#68 progress list updated** — fef2 ticked, count → 25, next repo TBD (verify `complete` first).
5. **A-mech filed as #82** — empirical-first mechanism-plausibility gate between Stage 2 and Stage 3. Confirmed OPEN and **self-documented as a v1 deferral** (`stage_2.md:62`: the mechanism "audit equivalent" read happens only at Stage 6 via `referee-mechanism`); the plan-time checklist already exists in `referee-mechanism.md:26-38`, so the fix is to fire it earlier. Corroborates the run's own LESSONS_PIPELINE recommendation #1.
