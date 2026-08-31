# Lessons harvest — `finance-empirical-first-3-b5988388`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-first-3-b5988388`
**Run status:** `complete`, `current_stage: stage_10`, `problem_attempt: 1` (finished run — full two-track harvest applies)
**Mode:** `--mode empirical-first` (finance)
**Paper:** *Short Interest and the Implied-Borrow Term Structure: A T+1 Event-Study Null* (Lopez-Lira), 26pp, watermark `date=2026-05-15`.

Tracks: (A) self-graded `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md` + `LIMITATIONS.md`; (B) independent holistic read of `paper/main.pdf`.

---

## Track B — holistic read (the high-value track)

**Overall: the paper reads well.** Prose abstract (numbers present but in sentences, not a symbol wall), plain-ish title (mild jargon: "Implied-Borrow Term Structure", "T+1"), a clearly-stated two-fact contribution (durable cross-firm slope + well-powered T+1 null), honest disclosure of every weakness (incrementality on Cocquemas 2018, author-translated practitioner range, unidentified mechanism) in the abstract and body. **Two legible figures sit in the main body** — Figure 1 (event-study coefficients, May 28 event line, CRV1 bands) and Figure 2 (placebo distribution with headline marker) — both well-placed and readable. No `??` cross-refs, references render cleanly, no dropped/IA-only headline figure.

This is the **first run in the #68 sweep whose figures are correctly placed in the main body** (finance-empirical-6, first-5, fe5 were all figureless-body or IA-only). It corroborates that the figure work in `75e5c9e` + `3fba5cf` is holding on a real run.

### B1 (High in severity, but CLOSED-ON-ARRIVAL) — Table 2 statistic column clipped off the right page margin

`Table 2` (p.13, "Tests of the practitioner T+1 amplification hypothesis: summary") **ships with its entire `Statistic` column clipped off the right edge of the page.** The reader sees test labels but no values: the header reads "Stati", the Welch row shows `0.97 (0`, the CI shows `[−3.10, +8` (should be `+8.55`), the Wald shows `40.68 (2.7 × 10` (exponent gone). Every value in the table summarizing the paper's *central* hypothesis tests is truncated. This is exactly the kind of reader-facing defect the run's own LESSONS are blind to — LESSONS_PIPELINE praised the 8-agent polish stage; none of the 8 polishers, the style pass, or six referee rounds flagged that the summary table's values are invisible.

**Root cause (confirmed from source `paper/sections/results_null.tex:45`):** a plain `\begin{tabular}{lr}` with very long non-wrapping label cells (e.g. "Un-contaminated placebos (SET-A, 10 dates Jan–Mar 2023): mean (bps/σ)") and **no width management** — no `tabularx`, no `\resizebox`, no `p{}` wrap column, no `\small`. The `l` column sets at its full natural width, the tabular exceeds `\textwidth`, and the right column falls off the page. `pdflatex` treats this as an Overfull `\hbox` warning, not an error, so it ships silently.

**Current-state verdict: ALREADY ADDRESSED.** The run shipped 2026-05-15. The build-verify overfull-`\hbox` gate landed **2026-06-01** (commit `04d51bb`, #51) at `templates/shared/docs/stage_5.md:66`:
> `awk -F'(' '/Overfull \\hbox/{split($2,a,"pt"); if (a[1]+0>40) print}' main.log` must return nothing (sub-40pt boxes ignored).

I rebuilt this exact table in a minimal doc and confirmed it emits **`Overfull \hbox (171.18pt too wide)`** — far above the 40pt threshold. A current run hits the gate, and `stage_5.md:67` instructs "fix the offending table/float … before committing." So the run predates the fix; the defect class is closed. **Not filed.**

**Residual sub-gap (secondary, noted not filed):** the 40pt threshold is calibrated for *prose* lines (a word poking 10–30pt into the margin is cosmetically harmless). For *tabular/float* content, a sub-40pt overflow can still clip a digit off a numeric value — which is not harmless. No observed instance in this sweep (this run's overflow is 171pt), so this is a hypothetical generalization; flagging it here so a future run that ships a 20–30pt-clipped table value is recognized as the same class rather than re-investigated. If it recurs, the fix is a lower (or zero) overflow threshold for boxes inside `table`/`tabular`/`figure` environments, distinct from the prose 40pt tolerance.

---

## Track A — self-graded lessons, current-state-verified

LESSONS_PIPELINE lists 7 template recommendations; LESSONS_PAPER adds 2 Stage-0 "what I'd do differently". Verified against current template before disposition.

### A1 (High, OPEN, NEW) — paper-writer reports a FIX "applied" without verifying the edit landed

**Lesson (LESSONS_PIPELINE, "Hurt — quality", rec #1):** in polish r1, paper-writer's writer-notes claimed two criticals applied — chau2025 "modest"→"significant" and daniel2025+eelrr2024 removed from the "dynamic-equilibrium family" — but polish-bibliography r2 found the files **still read the original language**. 2 of 9 r1 criticals silently did not land. The only reason it was caught is that the Stage 9 polish loop re-fires polish agents whose criticals were applied (`stage_9.md:49`), which cost an **entire extra polish round** (LESSONS calls r2 "nearly a wasted round").

**Current-state verdict: OPEN.** `templates/agent_bodies/shared/paper-writer.md` has **no step requiring paper-writer to verify its own applied edits landed** (grep for any "after apply → grep/confirm" self-check returns nothing). The Stage 9 write-verification gate (`stage_9.md:31`) covers a *different* failure — a *polish agent* silently not writing its `output/polish_*_r{N}.md` file — not paper-writer's edits failing to land in `paper/sections/*.tex`. The reactive catch (polish re-fire, `stage_9.md:49`) only fires inside Stage 9 and costs a full round; it does not cover paper-writer's edit application at Stage 5 or at Gate 5 referee-fix cycles.

**Why general / file-worthy:** "paper-writer reports a fix applied; the edit silently didn't land" is a *class* that recurs on every FIX-list application — referee-fix rounds (Stage 6), claim-verifier PSE re-fires (Stage 5), and polish rounds (Stage 9). **→ FILED #77** (High, quality+cost). Resolved design (after operator discussion): not an in-agent self-grep but an **independent `apply-verifier` agent** (paper-writer is the pipeline's only self-grading producer — the separation principle says verify it with a different agent), fired at Stage 9 + Gate 5, four verdicts (LANDED / NOT-LANDED / DEFERRED-OK / UNVERIFIABLE), no new state counter (follows the `stage_9.md:31`/`:45` once-bound re-fire idiom), scope = application not quality. #77 cross-references interactions with #69 (claim-verifier family), #75/#71 (rendered-PDF gates vs source-edit check), #67 (two-pass apply ordering). Implementation deferred to a later audited pass (no-fix-this-session).

### A2 (Med, OPEN but DROP) — identification design → paper-as-rendered drift

**Lesson (rec #2):** Stage 3a step 3 audited a triple-DiD with three-way absorbed FE; the paper shipped a cross-sectional date-FE-only spec (eq. 3). `polish-identification` (Stage 9) surfaced the drift; LESSONS argues it should be re-audited at Stage 5 / 3a step 5, not Stage 9.

**Verdict: OPEN but DROP (Stage 9 owns it; realized harm ≈ 0).** `polish-identification` at Stage 9 reads `output/stage1/identification_design.md` + `output/stage3a/identification_audit.md` + the rendered paper (`stage_9.md:13,16`) and is the designated cross-check; it caught the drift here. Same disposition as first-4's A3 and fe5's formula-shift-left: a shift-left is either incomplete (paper-writer can't reliably self-audit an estimand change) or re-audits the whole design every round. Stage 9 polish-identification is the right owner and worked. **Not filed.** Note for clustering: 1st observed instance of *design→rendered estimand drift* (distinct from #73's unit-of-treatment mismatch); if a 2nd run ships a drifted spec that Stage 9 *misses*, revisit as an OPEN shift-left.

### A3 (Med, OPEN but DROP) — institutional desk-reject error caught only at Stage 9

**Lesson (rec #3):** a wrong Reg SHO claim (locate obtainable "by the next/second business day" — actually always pre-trade under 203(b)(1)) survived Stage 5 → six Stage 6 referee rounds → Stage 7 → Stage 8, and was caught only by `polish-institutions` at Stage 9. LESSONS wants an institutional-fact micro-check inside paper-writer at Stage 5.

**Verdict: OPEN but DROP (same family as A2).** `polish-institutions` (Stage 9) is the designated institutional-realism owner and caught it; the verdict trajectory (Major→Minor convergence) was unaffected, so realized harm ≈ 0. A paper-writer self-fact-check at Stage 5 has the same incompleteness problem (paper-writer can't reliably enumerate every regulatory claim needing a web-check) and duplicates a working Stage 9 agent. **Not filed.** Genuine residual: institutional errors caught at Stage 9 have *notionally* cost referee rounds of narrative built on a false premise — but no realized harm in this run. If a future run's institutional error actually drives a referee rejection, that escalates this to OPEN.

### A4 (corroborates #74) — empirics OOM on the wild-cluster bootstrap

**Lesson (rec #6, "Hurt — cost"):** OOM kill on the first OTT bootstrap at B=999, N=2.55M, G=3,114; forced a rewrite to an FWL-residual O(N)-per-replication implementation; ~2h recovery. Recommends a memory-cap parameter / O(N) default at N>1M.

**Verdict: corroborates the already-filed #74** (empirical memory-efficiency directive for large data loads). This is the **3rd run** to hit empirics OOM (first-4 A4: 2 empirics-auditor OOMs; empirical-7: empiricist 146M-row OOM; now fef3: bootstrap OOM at N=2.55M). → **Post a one-line corroboration comment on #74** (confirm-first).

### A5 (Low, cost-only — note, don't file) — Minor-Revision fast path

**Lesson (rec #5):** once the editor returns Minor, the full editor→triager→paper-writer chain is overhead-heavy for small text edits; a "Minor fast path" routing the editor's canonical list straight to paper-writer would save ~10 min/cycle. Cost-only, modest savings; the triager's canonical list has real value. **Note only.**

### A6 (Low, design-nudge — note, don't file) — cross-jurisdiction placebo / staggered-design preference at Stage 0/1

**Lesson (rec #7 + LESSONS_PAPER "what I'd do differently"):** for a single-country single-event policy design, gap-scout / identification-designer should search analogous interventions in other jurisdictions (or prefer a staggered-adoption design) at Stage 0/1. **Note only:** the run *already did* cross-jurisdiction placebo work (Canada/Mexico T+1 the prior day — `T4_country_ordering`, `T5_canada_em_placebo`, `F4_country_betas`), and gap-scout *did* explore the staggered Indian/Canadian/Mexican sequence but found it less data-available. A template change nudging the designer toward staggered designs risks overfitting against cases where the single-event design is genuinely the better-powered available substrate. Soft, low-confidence; not gate-able. **Not filed.**

### Closed-on-arrival (not filed)

- **Abstract notation residual / acronym-ish title** — run predates `75e5c9e` (prose-only abstract/title); the shipped abstract is already prose. Closed.
- **Silent polish-write failure** — covered by the Stage 9 write-verification gate (`3fba5cf`, `stage_9.md:31`). Distinct from A1 (which is paper-writer's *own* edits, still OPEN). Closed.
- **Macro identification gate** (`LIMITATIONS.md`) — tracked in #18, documented-deferred.
- **SSA / OptionMetrics-ceiling / SI-snapshot-coarseness limits** (`LIMITATIONS.md`, paper §8) — paper-specific data limits, honestly disclosed, not template defects.

---

## Disposition summary

| ID | Item | Severity | Verdict | Action |
|----|------|----------|---------|--------|
| B1 | Table 2 statistic column clipped off right margin (171pt overfull) | High | ALREADY ADDRESSED (`stage_5.md:66`, #51; run predates) | Not filed; residual sub-40pt-table-clip note |
| A1 | paper-writer reports FIX applied without verifying edit landed | High | **OPEN (new)** | **FILED #77** (independent apply-verifier agent) |
| A2 | identification design→rendered drift | Med | OPEN but DROP (Stage 9 owns) | Not filed; cluster note |
| A3 | institutional desk-reject error caught only at Stage 9 | Med | OPEN but DROP (Stage 9 owns) | Not filed; cluster note |
| A4 | empirics OOM on wild-cluster bootstrap | Med (cost) | DUPLICATE → #74 (3rd run) | **Corroborate #74 (confirm-first)** |
| A5 | Minor-Revision fast path | Low (cost) | OPEN, cost-only | Note only |
| A6 | cross-jurisdiction/staggered design check | Low | OPEN, soft nudge | Note only |

**Outward-facing writes (done 2026-06-09):**
1. **A1 → filed #77** — "paper-writer has no independent apply verification: add apply-verifier agent (Stage 9 + Gate 5)." Design captured in the issue; implementation deferred to a later audited pass.
2. **#74 corroborated** — comment posted (3rd run to hit empirics OOM).
3. **#68 progress updated** — fef3 ticked, next repo = finance-empirical-3-b36d7cdb.

No other issues to file; no figure/abstract/title defects (paper reads well).
