# Lessons Harvest — `finance-empirical-5-78d3e2ed`

**Date:** 2026-06-06
**Repo:** `automated-papers-produced/finance-empirical-5-78d3e2ed` (2026-05-22)
**Status:** `complete` (`stage_10`), `problem_attempt: 1` — finished run, full two-track harvest.
**Paper:** "What Target-Date Fund Rebalancing Cannot Explain: A Calibrated Bound on the Glide-Path Premium" (22pp, 3 tables, **0 figures**). Single-insight ruling-out result; self-targeted JFIP.

Two tracks: (A) holistic read of `paper/main.pdf`; (B) self-graded `LESSONS_PAPER/PIPELINE` + `LIMITATIONS`. Each candidate carries a current-state verdict (method step 5).

---

## Track A — holistic read (the high-value track)

The paper reads **well**. Title is plain-language and tells you what it's about (no acronym title — contrast finance-empirical-6's "LDI"). Abstract is prose-led with one residual symbol (`M_t ≤ Ω_t/4`, undefined at that point) but communicates the result in plain English ("the channel sits more than 70 times below detectability"). Sections 3.5 / 4.1 / 4.2 are clear and honest about what the empirics do and don't deliver. The math is clean.

Two reader-facing defects, neither mentioned in the run's own LESSONS:

### A1 (NEW, High) — Unresolved `\ref` → literal "??" in the rendered PDF (~10+ instances)

The main PDF ships with "Internet Appendix Section **??**" on pages 6, 8, 9, 14 (×2), 15, 16, 17 (×3), 19 — every cross-reference to the Internet Appendix rendered as a literal `??`. Intra-document refs ("see Section 4.3", "Section 3", "Section 4.1") resolved fine; **only the cross-document IA refs are dangling.** This is the signature of `\externaldocument{internet_appendix}` (xr-hyper) finding no usable `internet_appendix.aux` — the IA was referenced 10+ times but never populated/compiled into a label set the main paper could resolve. A reader hits "see Internet Appendix Section ??" and gets nothing; a referee reads it as sloppiness in the first ten minutes.

**Current-state verdict: OPEN.** The Stage 5 build-verify gate (`templates/shared/docs/stage_5.md:63-67`) has three checks: (1) `grep -c 'Citation.*undefined' main.log` = 0, (2) bibliography renders, (3) no overfull hbox > 40pt. **It checks `Citation` undefined but not `Reference` undefined.** Unresolved `\ref` emits `LaTeX Warning: Reference '...' undefined` (→ "??" in the PDF), which is a *Reference* warning, not a *Citation* warning — so all three checks pass and the build is reported clean with 10+ "??" shipped. The gate header even concedes "a passing `\ref` resolution is necessary but not sufficient" — yet **nothing actually verifies `\ref` resolution.** No polish agent greps the compiled PDF or `.log` for `??` / undefined references either.

**General class:** any dropped `\label`, typo'd label key, or cross-document IA ref to an unpopulated/uncompiled IA ships "??" to the reader. Not specific to this paper's IA.

**Proposed fix (general, cheap):** add to the Stage 5 build-verify gate (and reuse on every rebuild) a 4th check —
- `grep -c 'Reference.*undefined' main.log` returns `0` (and same on `internet_appendix.log` when the IA is populated); and
- belt-and-suspenders reader-facing check: `pdftotext main.pdf - | grep -c '??'` returns `0`.

Plus a paper-writer guard: do not emit `\ref` to an Internet Appendix section you did not populate/compile; if the IA stays a placeholder skeleton, the main text must not cross-reference it. Files: `templates/shared/docs/stage_5.md` (gate), `templates/agent_bodies/shared/paper-writer.md` (IA-ref discipline at the `\externaldocument` section, ~line 118).

### A2 (Corroborates #71, High) — Zero figures in the main body; 3rd figureless-body run

The paper has 3 tables and **zero figures**, despite the single most natural headline figure in the entire paper being absent: the **rolling 36-month equity–bond correlation over 1985–2024 with the Bai–Perron break dates (2000-09, 2019-11) marked and the channel's visibility bound overlaid**. That one plot *is* the result — "the breaks are here, the channel can't reach them." A reader must reconstruct it from prose ("sup-F = 320.8") and Table 2/3 numbers. The 70×-below-detectability safety margin is also inherently a (log-scale) figure.

**LESSONS-blindness (the #68 motivation, vividly):** `LESSONS_PAPER.md` lists "**Exhibit count: 3 in-text tables, 0 figures (≤5 exhibits) ✓**" as a *positive* JFIP-fit checkmark. The self-grade scored zero-figures as a feature. This is exactly the blindness #68 exists to catch — the run cannot see its own figure defect.

**Current-state verdict: OPEN, folds into #71.** The directives exist (`empiricist.md:100` "produce at least one headline figure"; `paper-writer.md:181` "a paper with numerical results but zero figures is a defect"), and the dropped-figure gate (commit 3fba5cf) checks whether a *produced* figure was dropped. The sub-gap this paper sharpens: **the dropped-figure gate is conditional on a figure having been produced upstream.** If the empiricist never generated the rolling-correlation plot, there is nothing to "drop," paper-writer's "include producing-agent figures" is vacuously satisfied, and the paper ships figureless — the gate checks "did you drop a produced figure," not "should a figure exist for this result." Same family as #71's reader-facing-figure-defect theme (legibility, IA-only placement) — this is the *no-figure-produced-at-all* variant.

**Disposition:** corroborate #71 (3rd figureless-body run after finance-empirical-6 and finance-empirical-first-4), citing the empiricist-never-produced-it mechanism + the self-grade-as-positive blindness as the worked example.

### A3 (Low, note only) — title/subtitle term "Glide-Path Premium" never defined in body

The subtitle promises "A Calibrated Bound on the **Glide-Path Premium**," but the body never defines or uses a "glide-path premium" — the object bounded is the equity–bond *correlation* channel, not a premium. Minor title↔body term mismatch; paper-specific, not a template class. Note only, do not file.

---

## Track B — self-graded lessons (checked against current state)

| # | Lesson (from LESSONS_PIPELINE / PAPER) | Current-state verdict | Disposition |
|---|----------------------------------------|----------------------|-------------|
| B1 | polish-numerics + polish-bibliography r1 silently did not Write their reports to disk (caught only because triager flagged the missing file) | **ALREADY ADDRESSED** — Stage 9 write-verification gate, commit 3fba5cf (in #68 dedup list) | Closed-on-arrival; 2nd run to hit the silent-polish-write class. Not filed. |
| B2 | Appendix slope-formula typo took 2 referee rounds to catch; lesson asks for a `polish-formula`-equivalent gate after the Stage 5 first LaTeX draft, before Stage 6 (math-auditor audited theory_draft, not rendered LaTeX) | **OPEN but DROP** — identical shift-left class as finance-empirical-first-4's A3 (which was DROPPED): Stage 9 polish-formula already owns rendered-LaTeX re-derivation; shifting a full re-derivation pre-Stage-6 means re-running after every referee revision (expensive) or it is incomplete. Realized harm was caught in-pipeline. | Note; do not file (consistent with A3 precedent). Operator may overrule. |
| B3 | v4→v5 deepening (continuous-time intermediary capital) consumed ~30-40% of pipeline time and did not move the structured score (64→64); should have downgraded tier one round earlier | **OPEN but not actionable as a gate** — branch-manager judgment calibration, not a missing mechanism. The downgrade *did* eventually fire and the LESSONS credit it as the single biggest quality contribution. "Downgrade one round earlier" is not operationalizable into a deterministic rule. | Note; do not file. |
| B4 | WRDS server timed out 3× between Stage 3a re-fires (each restart needs Duo + 60-180s) | **OPEN (infra, known)** — longer-lived WRDS keepalive / auto-restart-with-cached-cookie. Operational, not a paper-quality gate. | Note; out of scope for the paper-quality backlog. |

Closed-on-arrival / dedup: abstract one-symbol residual → corroborates the known abstract-notation thread (already addressed by polish-prose >100-word + notation rule, commit 75e5c9e; this paper predates it). Macro-id / SSA `LIMITATIONS.md` entries → pre-existing documented-deferred (#18 / documented), not run-authored.

---

## Prioritized backlog (this repo's net new signal)

| Item | Pri | Quality/Cost | Verdict | Action |
|------|-----|--------------|---------|--------|
| **A1** Unresolved `\ref`→"??" not caught by build-verify (checks Citation, not Reference) | **High** | Quality (reader-facing) | OPEN, NEW | **File new issue** (pending go-ahead) |
| **A2** Figureless main body; dropped-figure gate conditional on a figure being produced | High | Quality (reader-facing) | OPEN | **Corroborate #71** (3rd run) (pending go-ahead) |
| B2 formula-typo shift-left | Med | Cost | OPEN→DROP | Note only (A3 precedent) |
| B3 downgrade-tier-earlier | Med | Cost | OPEN→not-actionable | Note only |
| B4 WRDS keepalive | Low | Cost (infra) | OPEN | Out of scope |

**Pending operator go-ahead (method step 8a — outward-facing writes are confirm-first):**
1. File **A1** as a new High child issue (general framing: build-verify gate must catch unresolved `\ref`/"??", not just undefined `\cite`).
2. Post **A2** corroboration comment on **#71** (3rd figureless-body run; empiricist-never-produced-it mechanism + self-grade-scored-zero-figures-as-positive worked example).
