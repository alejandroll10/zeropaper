# Lessons Harvest — `finance-paper-1` (2026-06-09)

**Repo:** `automated-papers-produced/finance-paper-1`
**Run:** `status: complete`, `current_stage: stage_9`, `problem_attempt: 1`, `seeded: false`, `mode: none`.
**Variant/mode:** `finance` base variant, **no extensions** — the **only pure-theory finance run in the entire #68 sweep**. Every other harvested repo carried `--ext empirical` or `--ext theory_llm`. Earliest finished run in the org (shipped 2026-05-02), real-author / non-anonymous (Alejandro Lopez-Lira, University of Florida).
**Run shape:** theory v17, referee_round 10 (cap), polish_round 2 (cap), scorer 66→70→74. 7 branch-manager Reject-deepens, mechanism-referee MISATTRIBUTED through all 10 rounds (capped-and-shipped). Target JF/JFE/RFS; self-assessed realistic home JFQA.
**Paper:** 43pp `paper/main.pdf` read holistically. `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md` (no `LIMITATIONS.md`).

Paper subject: rank-one correlated AI signal-extraction errors embedded in a multi-asset Admati (1985) noisy REE; a closed-form **sign-flip cubic** in pairwise return covariance across a liquidity threshold, plus an unconditional within-direction posterior-precision drop.

---

## Track B — holistic read (the high-value part; self-grade is blind to all of it)

**Reads well on:**
- **Title — GOOD.** "Correlated AI Signal Errors and the Cross-Section of Price Informativeness." Plain-language, no acronym wall, tells you what the paper is about. Clears the `75e5c9e` bar (run predates it).
- **Author — real, no placeholder.** No `#81` trigger (this run filled the author; the placeholder-leak runs are later/anonymous ones).
- **Cross-refs — clean.** `pdftotext | grep '??'` = **0**; every `\ref`/`\cite` resolves. No `#75` defect. (Run predates the build-verify ref/cite gate, so this also shows a clean theory build is achievable without it.)
- **Tables — one, legible.** Only Table 1 (Appendix D, q-asymmetry distinguisher), a simple 3-column `tabular`. No clipping/overfull. No `#51` defect.
- **References** well-formed.

**Defect H1 (High) — zero figures in 43 pages despite the headline being a 1-D comparative-statics sign-flip; 23 figures produced and unused.**
`pdfimages -list` = **0 embedded images**; `pdftotext | grep -ci figure` = **0**. The 43-page body has no figures and no figure environment at all. Yet the paper's headline result is *the* canonical "show me the plot" object — a sign-flip of pairwise covariance across a local liquidity threshold (`β_model` crossing zero in `σ_u`). The numerical illustration (§4.5) presents it as **inline prose**: "the cubic `P(r,0.6)=1.8+2.6r−1.2r²−2r³` with unique positive root `r*≈1.1695` and local threshold `σ*≈0.5407` … global threshold 2.76, a gap of 19.7%." §4.3's four Taylor-scale gap points (0.13%/6.77%/19.7%/16.5%) and §6's calibration magnitudes (β ≈ +105 bps vs −9 bps) are likewise inline.

Meanwhile **23 figures sit unused** in `output/stage3a/figures/`, including the *literal headline*: `theorem2_signflip_vs_sigmau.png`, plus `theorem2_cubic_boundary.png`, `theorem1_dominance_calibration.png`, `local_vs_global_gap_scale.png`, `empirical_magnitude_heatmap.png`, `theorem2_taylor_breakdown.png`. The producing agent made the figure of the result; the paper shipped figureless.

This is the **6th–8th-tier figureless run in the sweep, and the FIRST pure-theory one.** Every prior `#71` corroboration (fe6, fe4, fe5, fe2, fec2, fef2, fl1) was an empirical or empirical-first paper whose headline figure was an event study / placebo distribution / region table. finance-paper-1 confirms the figureless-body defect is **not empirical-specific**: a pure-theory paper whose contribution is a comparative-statics sign-flip is exactly the case the `#71` issue's "mode-agnostic — theory-first papers carry `stage2b` figures" clause was written for, but until now `#71` had **only empirical worked examples**. This is the first theory data point validating that clause is load-bearing.

LESSONS-blindness is total and vivid: `LESSONS_PAPER.md` never mentions figures **once** in its entire "what works / what doesn't" inventory; `LESSONS_PIPELINE.md` praises theory-explorer for producing "diagnostic plots" without ever noting that **none of them reached the paper**.

**Current-state verdict: closed-on-arrival → corroborate `#71`.** The dropped-headline-figure gate (`polish-consistency.md:24`, item 10) is explicitly mode-agnostic and checks `output/stage2b/figures/` (theory exploration), firing **major** when any figure exists there but the body has zero `\includegraphics`. Current theory-explorer writes figures to exactly `output/stage2b/figures/` (`theory-explorer.md:99`, `docs/stage_2.md:96`), and `paper-writer.md:181` instructs showing "the key comparative static" from `output/stage2b/` as a figure. So a **current** pure-theory run that shipped this paper figureless would be caught (the gate would name the stage2b pngs and demand inclusion). finance-paper-1 (2026-05-02) predates the gate (`3fba5cf`); the figures landed in `output/stage3a/figures/` only because this oldest run ran theory-explorer at Stage 3a before the stage was renumbered to 2b — the dir mapping is correct for current runs. **No new issue; post a `#71` corroboration as the first pure-theory worked example.**

**Defect H2 (presentation) — most extreme abstract-notation wall in the sweep.**
The ~400-word abstract is a near-unbroken stream of inline math and symbol names: `P(r,ρ,φ)`, `r*(ρ,φ)`, `ℓ=0`, `Q(t;s,·)=0`, `t=b∥/c∥`, `∂Q/∂t>0`, `sign(1−t/t⊥)`, `K∥(s)<K∥(0)`, `tr(Σ⁻¹_post(f|p))(s)`, `d∥²s`, `Δ≥0`, "see Conjecture 32," etc. It is unreadable to anyone who has not seen the model.
**Current-state verdict: closed-on-arrival** (`75e5c9e`). `polish-prose.md:20` criterion (a) makes any >100-word abstract `critical` (this is ~4×), and criterion (e) flags inline math / Greek / parameter expressions / cross-refs — both fire decisively on a current run, and the same rule applies to the title (which here is already clean). This is the **strongest single validation of the prose-abstract mandate in the sweep**; nothing to file.

---

## Track A — self-graded lessons, checked against current template state

| # | Lesson (source) | Current-state verdict | Disposition |
|---|---|---|---|
| A1 | **`#71` proper** — paper shipped figureless despite ready plots (holistic, not in self-grade) | **Closed-on-arrival** — item 10 mode-agnostic gate covers current theory papers; run predates `3fba5cf` | Corroborate `#71` (1st pure-theory example) |
| A2 | Silent polish-write failure: 5/6 polish agents hit usage limits in r1 without writing files; operator reconstructed two reports (LESSONS_PIPELINE "r1 partial-failure recovery" + Rec 1) | **ALREADY ADDRESSED** (`3fba5cf` Stage 9 write-verification gate, `stage_9.md:31`). Nth run to hit it pre-fix | Closed-on-arrival |
| A3 | Mechanism-MISATTRIBUTED unresolved through r10; "trigger forced framing/mechanism choice at r5 not r10" (LESSONS_PIPELINE Rec 5) | **OPEN-but-NOTE-ONLY** — editor sets Major Revision under MISATTRIBUTED every round (`stage_6.md:70`) but nothing forces a binary "mechanism is X / framing is Y, pick one" at a fixed round. **However** `fl1` observed MISATTRIBUTED discharged in **2 rounds** in a recent run (working-as-intended), so the 10-round persistence looks like an artifact of this earliest run predating editor maturity. Subjective + likely-superseded-in-practice | Not filed (note) |
| A4 | "No empirical-commitment gate: default `--ext empirical` on for theory papers with named tests" (LESSONS_PIPELINE Rec 3) — paper shipped Tests 1–4 as a *design*, ran none | **WON'T-DO / operator-discretion** — the extension is a setup-time flag chosen before the idea exists; the pipeline can't know at setup that the idea will spawn named tests. Running unrun-test designs is a scope choice, not a gate gap | Not filed (note) |
| A5 | Shift-left institutional-realism + equilibrium-multiplicity to Stage 2 (LESSONS_PIPELINE Rec 4 + "load imbalance"); polish-institutions caught the IBES→LSEG rename, polish-equilibria caught the σ_u/A1 mismatch + black-box-selection at Stage 9 | **OPEN-but-DROP** — same disposition as fe4-A3 / fe5 / fe3-L3: Stage 9 owns it, realized harm ≈ 0 (all caught pre-ship), and shift-left re-audits the whole paper each round. **3rd–4th run on this theme; consistently dropped** | Not filed (drop) |
| A6 | Persist branch-manager substantive/cosmetic verdict in `pipeline_state.json` (LESSONS_PIPELINE Rec 2 + architectural obs) | **PARTIAL/note** — `reject_cosmetic_round` *is* persisted for the Gate-5 Reject loop (`stage_6.md:70`); the Gate-4 branch-manager cosmetic verdict drives `core.md:395` escalation. Minor observability ask, cost-only | Not filed (note) |
| A7 | Cache bib-verifier across passes keyed on (cite_key, refs.bib hash); same 8 SSRN preprints re-resolved 3× (LESSONS_PIPELINE Rec 6) | **OPEN, cost-only** — corroborates the re-checking-accretion theme (grounder caching @ `#69`, inference-battery @ `#67`); pure compute, no quality effect | Not filed (note) |
| A8 | Skip polish-numerics in r2 if r1 had 0 critical / ≤1 major (LESSONS_PIPELINE Rec 7) | **OPEN, cost-only, subjective** — polish is intentionally unconditional (`stage_9.md:7`, the "polish even on ACCEPT" → SUPERSEDED finding from fef5); selective-skip trades robustness for compute | Not filed (note) |

---

## Net

**Pure-corroboration repo** (like `fe2`, `fef1`). The single high-value finding is **H1 → `#71`**, notable as the **first pure-theory data point** in the sweep: it confirms the figureless-body defect class generalizes beyond empirical papers and that `#71`'s mode-agnostic / theory-`stage2b` gate language is genuinely load-bearing (a real theory paper, with its literal headline plot `theorem2_signflip_vs_sigmau.png` produced and unused, exhibited it). Closed-on-arrival for current runs (gate added `3fba5cf`); **corroborate `#71`**, no new issue.

The abstract (H2) is the most extreme notation wall in the sweep — closed-on-arrival via `75e5c9e`, strong validation of the prose-abstract mandate.

All Track-A self-lessons are either ALREADY ADDRESSED (`3fba5cf` write-gate), repeatedly-DROPPED (Stage-2 shift-left, 3rd–4th run), operator-discretion (`--ext empirical` default), or note-only/cost (bib-cache, polish-skip, verdict-persistence). The MISATTRIBUTED-at-r10 lesson (A3) is the one genuinely-interesting recurring smell but is subjective and **observed working-as-intended in a more recent run (`fl1`)**, so it is recorded as a note, not filed.

**No new issue filed.** Recommended outward-facing write: one `#71` corroboration comment (first pure-theory worked example).
