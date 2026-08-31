# Lessons Harvest — `finance-empirical-3-b36d7cdb`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-3-b36d7cdb`
**Status:** `complete` (`stage_10`, `problem_attempt: 1`) — finished run, full two-track harvest applies.
**Variant/mode:** `finance` + `--ext empirical` (theory-first hybrid: theory model + empirical measurement). 6 referee rounds; target tier downgraded `top-3-fin` → `field`, converged JFIP Minor/Minor/VALID.
**Issue:** #68 (lessons-harvest sweep).

Paper: *"Per-Prospectus Glidepath-Revision Costs for Target-Date Funds: A \$251K Anchor and a Corrected Revision Cadence."* 23 pp. A narrow, honest JFIP measurement note: a \$251K bottom-up per-prospectus revision-cost anchor + a text-classified 1.3% glidepath-revision rate from 157 EDGAR 485APOS filings (hand-coded κ=0.78), tied by a 7.2-yr break-even that sits above the 3–5yr ERISA fiduciary-review window.

---

## Track B — holistic read (read as a reader, not a referee)

**What reads well (closed-on-arrival, corroborates prior fixes holding):**
- **Title** — plain-language, descriptive, carries a memorable number (\$251K). No acronym title. Corroborates `75e5c9e` holding.
- **Abstract** — prose, communicates the two measurements + the break-even in plain language; minimal symbols, **no notation wall**. Corroborates `75e5c9e`/`polish-prose.md` holding.
- **Tables 1–3** — clean, legible, no clipping / no overfull `\hbox` (contrast fef3's clipped Table 2 — already addressed by `stage_5.md:66`).
- **Cross-references** — all resolved (Section 2, Table 1, Appendix A/B/C all numbered; **no literal "??"** anywhere). The fe5 `\ref`→"??" defect (#75) is **not** present here.

This is, with fef3, one of the cleanest-reading papers in the sweep on the title/abstract/table/cross-ref axes — direct evidence the `75e5c9e`/`3fba5cf`/#51 presentation fixes hold.

**The dominant holistic defect — H1 (High): zero main-body figures; self-grade hallucinated a figure that does not exist.**
- 23 pages, headline result = "7.2-yr break-even sits *above* the 3–5yr ERISA review window," plus an 81-cell κ×γ×r×α_gap sensitivity analysis. **All of it is reported as numeric tables (Tables 1–3 + an Appendix B prose summary). Zero figures.** The result is something a reader reverse-engineers from Table 2, not something they *see*. An obvious headline figure exists in the material: T_rev^max as a function of κ (or α_gap) with the 3–5yr ERISA band shaded and the 100%/71.6%-of-cells annotation — i.e., a one-panel "break-even clears the review window" chart.
- **Vivid LESSONS-blindness:** `LESSONS_PAPER.md:5` claims the primitives are "sensitivity-**graphed** across an 81-cell joint κ×γ×r×α_gap grid." There is **no graph** — it is Table 2 + Appendix B prose. The self-grade asserts a figure that was never produced. This is the exact #71 thesis (the run's own LESSONS are blind to how the paper reads), in its sharpest form yet: not silence about a missing figure, but a positive false claim that one exists.

---

## Track A — self-graded lessons (LESSONS_PAPER / LESSONS_PIPELINE / LIMITATIONS)

`LIMITATIONS.md` is the **stock template file** — only the macro-id `#18` entry (pre-existing documented-deferred). No run-authored architectural limits.

Candidates extracted from LESSONS_PIPELINE "Hurt — quality/cost" + "What I would change about the template":

| ID | Lesson | Quality/Cost | Current-state verdict | Disposition |
|----|--------|--------------|-----------------------|-------------|
| **H1** | Zero main-body figures; self-grade hallucinates a "sensitivity graph" | Quality | **OPEN** — figure gate is conditional on upstream production (see below) | **Corroborate #71** (4th figureless run; 2nd never-produced instance) |
| **L1** | Branch-manager's Gate-4 strategic verdicts beyond Regenerate (Restructure / Restart / tier-reframe) are unoperationalized — same RESTRUCTURE verdict is honored at Stage 2 but dropped at Gate 4, so the run carried the full v10 apparatus into a JFIP frame (2–3 extra referee rounds) | Cost (quality tail) | **OPEN** — confirmed below | **File (Med, operator discretion)** — NEW, general |
| **L2** | "16 of 27" grid-count fabrication survived 6 referee rounds + bib-verify + style; paper-writer transcribed counts not in `sensitivity_report_r3.md` | Quality | **OPEN** (theory-side claims ungrounded — below) | **DROP** (Stage 9 polish-numerics owns it; caught pre-ship). Corroborate #77 |
| **L3** | κ-anchor citation chain (PVW/Mitchell-Utkus/Viceira/Madrian-Shea) mischaracterized 4 rounds; bib-verify checks existence not prose-claim | Quality | **OPEN** (Stage 8 bib-verify = cite-key only) | **DROP** (polish-bibliography Stage 9 caught it). Same as fe4-A3 |
| **L4** | Editor treadmill detection should fire one round earlier (2 consecutive freeform-Reject same-diagnostic → escalate to FIX) | Cost | **OPEN** — `editor.md` has no encoded treadmill rule (r3 warning was emergent) | **Note-only** (cost; "same diagnostic" detector is subjective; run converged) |
| **L5** | polish-formula 0-finding should surface as "strong pass" to calibrate orchestrator confidence | Calibration | OPEN (cosmetic) | **Note-only** |

---

## Current-state verification (method step 5 — mandatory)

### H1 — figure gate is conditional on upstream production (confirms the #71 never-produced sub-gap)
- `polish-consistency.md:24` (dropped-headline-figure, deterministic): fires only if a figure dir (`stage2b/`, `stage3a/`, `stage3b/`) contains a `.pdf`/`.png` **but** no `\includegraphics` ships. Explicitly: **"If every figure directory is empty or absent, do not fire."**
- `paper-writer.md:181` ("show the headline result as a figure"): includes the producing agent's figure if one exists; **fallback is a soft self-judgment** — `[NEEDS EMPIRICIST/THEORY-EXPLORER: …]` "if no figure exists but the headline **plainly warrants** one."
- **Gap:** the **figureless-because-never-produced** case slips both. The deterministic gate is silent (no upstream figure), and paper-writer's judgment that "the headline plainly warrants one" failed (it shipped figureless and even the self-grade believed a figure existed). fe3 is the **4th figureless-body run** (fe6, fe5, fe4-IA-only, fe3) and the **2nd to demonstrate never-produced** (fe5 was first; fe5's A2 folded into #71). The generalized fix #71's never-produced sub-gap already calls for — a **figure-presence gate not conditional on upstream production** (e.g., a Stage 9/Gate-5 check: "≥1 main-body figure, or paper-writer must justify the headline as genuinely non-visualizable") — would catch fe3. **→ corroborate #71, do not file new.**

### L1 — branch-manager's Gate-4 strategic verdicts beyond Regenerate are unoperationalized (OPEN, file-worthy)

Full map of the §E "Recommended action" set (`branch-manager.md:117,79`) against whether the orchestrator has a defined route:

| §E verdict | Routed? | Where |
|---|---|---|
| **Regenerate** | ✅ fully | escalation row `core.md:385`, learnings file, Stage-1 protocol; `stage_4.md:67` |
| **Continue / Ship-at-current-tier** | ✅ (default) | the advance/continue path |
| **COSMETIC** (Section A diff verdict) | ✅ | `core.md:395`, `stage_4.md:94`, gate-5-reject state machine `stage_6.md:70` |
| **Restructure around [headline]** | ⚠️ **pre-paper only** | routed at **Stage 2** (`stage_2.md:39` mandatory sketch-swap evaluation) — **not at Gate 4**: no escalation row, drops into ADVANCE, never reaches paper-writer |
| **Tier / outlet reframe** ("right journal", `bm.md:88`) | ⚠️ partial | `target_tier` may be updated, but the reframe's *paper-construction* implications (write a field/JFIP-shaped paper, not top-3) don't propagate to paper-writer |
| **Restart with [unused sketch]** | ⚠️ ambiguous at Gate 4 | sketch-swap explicit at Stage 2 (`stage_2.md:39`); at Gate 4 no escalation row (only Regenerate) |

**The sharpest evidence: an internal inconsistency, not a missing intent.** The template *already* says the orchestrator must honor branch-manager (`stage_4.md:67` "the gate decision must be consistent with its recommendation"). And the *same* RESTRUCTURE verdict **is** operationalized at **Stage 2** (`stage_2.md:39`, "any branch-manager RESTRUCTURE verdict" → mandatory sketch-swap evaluation). It is simply **dropped at Gate 4** — the last gate before the paper is written, which is exactly where fe3 needed it. `Regenerate` proves the Gate-4 forwarding machinery is buildable; scorer **presentation notes** (`stage_4.md:71`, explicitly forwarded to the Stage 5 paper-writer) prove the paper-writer channel already exists. So an orchestrator that *wants* to comply with a Gate-4 "Restructure" has no lever: once the score clears the (downgraded) threshold, its only consistent action is ADVANCE, and ADVANCE carries the draft to Stage 5 with the restructure instruction attached nowhere.

- **Consequence (run's own diagnosis, LESSONS_PIPELINE:7,20,37, corroborated by the referee trajectory):** v10 branch-manager said "RESTRUCTURE to JFIP single-insight," but the first paper draft carried the full v10 apparatus (formal Prop 1, three bargaining conventions, higher-order correction, drift, cross-sectional regression) into a JFIP frame. The freeform's "30 pages for a 7-page idea" (r2/r3) and the editor's r3 Path-A escalation are exactly what an un-applied restructure looks like — a 2–3 round detour. The run converged to the right paper because the editor eventually forced it, so realized **quality** harm ≈ 0; realized **cost** = the detour.
- **Verdict: OPEN (Med — cost item with a quality tail).** Not a downgrade-routing item (survives the move-away-from-downgrades policy) — it is about making the system *act on its trusted strategic advisor* at the one gate where it currently doesn't. **General fix:** give branch-manager's non-Regenerate Gate-4 strategic verdicts (Restructure / Restart / tier-reframe) defined Gate-4 routes mirroring Regenerate, and where the verdict's action is a paper-construction change, forward the recommendation to paper-writer at Stage 5 on the presentation-notes channel. The COSMETIC and Regenerate paths are solid and need no change.

### L2 — theory-side numerical claims have no Stage-5 source-grounding verifier (OPEN, but DROP)
- The `--ext empirical` claim triple (`stage_5.md` step 5a: claim-enumerator → claim-grounder → claim-verifier) grounds enumerated numerical claims against **`output/stage3a/`** (empiricist outputs) only. The grounder does not read **`output/stage2b/`** (theory-explorer / sensitivity grids). The fabricated "16 of 27" came from a theory-exploration sensitivity report (stage2b-class), so the triple would tag it `NEEDS_EMPIRICIST` (no stage3a source) rather than catch the transcription against its real source — and for a **pure theory** paper (no `--ext empirical`) the triple does not run at all. Theory-side numerical claims are therefore checked only by **polish-numerics at Stage 9**.
- **Verdict: OPEN, but DROP** — same disposition as fe4-A3 / fe5 formula-shift-left: Stage 9 owns it, the error was caught **pre-ship** (polish-numerics r1), realized harm = wasted polish bandwidth + survival through referee rounds (no shipped error). Extending the claim triple to stage2b duplicates polish-numerics. **Corroborate #77** (paper-writer is the pipeline's only self-grading producer): fe3 adds a 2nd run showing paper-writer authoring numbers it cannot source (16/27) + citations it cannot support (κ-anchor), strengthening the case that paper-writer needs an **independent output-verifier**, not only the apply-landing check #77 currently scopes.

### L3 — κ-anchor citation mischaracterization (OPEN, DROP — = fe4-A3)
- Stage 8 `bib-verifier` checks cite-key existence + metadata, not prose-claim accuracy; `polish-bibliography` (Stage 9) caught all four mischaracterized anchors. Shift-left to Stage 8 either re-audits the whole bib every round or is incomplete. **DROP** (Stage 9 owns it, harm 0). This is the **2nd run** to surface the bib prose-claim shift-left (fe4-A3 was first, also DROPPED).

### L4 — editor treadmill timing (OPEN, note-only)
- `editor.md` contains **no** encoded treadmill / consecutive-round escalation rule (0 hits for "treadmill"/"consecutive"). The r3 "treadmill warning" the LESSONS credit was **emergent editor behavior**, not a template rule. Making "2 consecutive freeform-Reject with the same diagnostic → escalate to FIX immediately" deterministic is a real cost win, but requires a subjective "same diagnostic" detector and the run still converged. **Note-only.**

---

## Dispositions summary

| # | Item | Disposition | Action |
|---|------|-------------|--------|
| H1 | Figureless body + hallucinated-figure self-grade | **Corroborate #71** | 4th figureless run; 2nd never-produced; vivid LESSONS-blindness |
| L1 | Branch-manager Gate-4 strategic verdicts beyond Regenerate unoperationalized (Restructure honored at Stage 2, dropped at Gate 4) | **File (Med)** — pending go-ahead | NEW, general, OPEN. Touches `core.md` escalation table + `stage_4.md` step 7 + `stage_5.md` step 1 (forward on presentation-notes channel) |
| L2 | Theory-side claim fabrication (16/27) | **DROP** + corroborate #77 | Stage 9 owns; paper-writer-unverified-producer theme |
| L3 | κ-anchor citation mischaracterization | **DROP** (= fe4-A3) | Stage 9 polish-bibliography owns |
| L4 | Editor treadmill one round earlier | Note-only | Cost; subjective detector |
| L5 | polish 0-finding "strong pass" signal | Note-only | Calibration nicety |

**Closed-on-arrival:** clean title/abstract/tables/cross-refs (corroborates `75e5c9e`/`3fba5cf`/#51 holding); `LIMITATIONS.md` = stock macro-id `#18`.

## Pending operator decisions (method step 8 — confirm before any outward-facing write)
1. **File L1** as a child issue (Med): "Operationalize branch-manager's Gate-4 strategic verdicts beyond Regenerate." Motivating evidence = the internal inconsistency (the same RESTRUCTURE verdict is honored at Stage 2 via sketch-swap authority, `stage_2.md:39`, but has no Gate-4 route); `Regenerate` is the buildable-machinery precedent, scorer presentation notes (`stage_4.md:71`) the paper-writer-channel precedent. Worked example = fe3 carrying the full v10 apparatus into a JFIP frame for a 2–3 round detour. Fix: defined Gate-4 routes for Restructure/Restart/tier-reframe + forward paper-construction verdicts to paper-writer at Stage 5.
2. **Corroborate #71** (comment): "4th figureless-body run: `finance-empirical-3`, 23 pp / 0 figures; 2nd never-produced instance; self-grade hallucinated a non-existent 'sensitivity graph' (LESSONS_PAPER:5)."
3. **Corroborate #77** (comment): "2nd run showing paper-writer as unverified producer: `finance-empirical-3` shipped a fabricated '16 of 27' grid count + 4 mischaracterized κ-anchor citations past 6 referee rounds; both caught only at Stage 9. Argues the apply-verifier should also source-ground paper-writer's authored numbers/citations, not only check edit-landing."

No issues filed / comments posted yet — awaiting go-ahead.
