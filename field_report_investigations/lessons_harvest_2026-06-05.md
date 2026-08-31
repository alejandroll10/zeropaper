# Lessons Harvest — Issue #68

Date: 2026-06-05
Method: per issue #68 (two tracks — self-graded lessons + independent holistic paper read — with mandatory current-state verification against today's template before filing).

## Repos swept this session

- **`finance-empirical-first-5-067efc37`** (pushed 2026-05-28; run May 25–26, 2026) — DONE. Both tracks complete.

### Selection note (PDF-and-lessons gate)

Per the operator instruction "most recent repo that already has a PDF and lessons," scanned by recency:

| Repo | pushedAt | Lessons | paper/main.pdf | Selected |
|------|----------|---------|----------------|----------|
| `finance-empirical-7-fedf5723` | 2026-06-02 | none (only `LIMITATIONS.md`) | **absent** (only `main.tex`) | skip |
| `finance-empirical-first-6-73c46736` | 2026-06-01 | `PROBLEM_LESSONS.md` only | **absent** (only figure PDFs) | skip |
| `finance-empirical-first-5-067efc37` | 2026-05-28 | `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md` | **present** | ✓ |
| `finance-empirical-6-4fad27ba` | 2026-05-28 | (already swept — issue #68 progress list) | — | done prior |

> Side-flag for the #68 progress tracker: repos #7 and first-6 ship **no `paper/main.pdf`** in the repo tree (the LaTeX is committed but the compiled PDF is not). If the harvest's holistic-read track depends on a committed PDF, those two repos will need a `pdflatex` build from `paper/main.tex` at sweep time, or they fall back to the `.tex` read. Not a template defect — just a sweep-logistics note.

---

## The paper, read as a reader (holistic track — highest value)

**Title:** *A Wrong-Sign Credit-Spread Response to the PJM 2025/26 Capacity-Market Regime Change: One Documented Regularity and Three Failed Mechanisms.*

This run **predates** the title/abstract fix (`75e5c9e`, June) and the headline-figure fix (`3fba5cf`, June), yet reads *well* on exactly the dimensions those fixes target — useful as positive confirmation that the target quality is organically reachable:

- **Title is clean prose**, not an acronym (contrast finance-empirical-6's "LDI"). It tells you the finding (wrong-sign credit-spread response), the setting (PJM capacity-market regime change), and the structure (one regularity, three failed mechanisms). Good.
- **Abstract is prose, not notation** — no `l̄*=Δ*/(γλN)`-style symbol wall. It opens with the institutional fact ($269.92/MW-day, 9.3-fold jump) and states the result in words.
- **It has a figure** (Figure 1, event study) — clears the zero-figures bar.
- **Contribution is locatable** — the "fourth answer" framing (p3) and the honest-null contribution statement are explicit and consistent end to end. The HONEST-NULL discipline ("a fact and three failed explanations; the field's task is to find the fourth") reads as genuinely disciplined, not evasive.

Holistic **defects** that degrade the reading experience:

1. **Figure 1 axis-label collision (visual/layout defect).** The x-axis title — "Event time k (months relative to July 30, 2024)" — is rendered **across the middle of the plot**, overlapping the zero-line and the plotted coefficient points near y=0. It reads as garbled at first glance; you have to mentally subtract the label from the data. The one figure in the paper is partly illegible. *This is the headline holistic finding* (see candidate H1 below).
2. **Abstract is dense with named inference engines.** Even as prose, the abstract names five inference engines (Frisch–Waugh, Ibragimov–Müller, coarsened-FE wild-cluster bootstrap, stratified randomization inference, Callaway–Goodman-Bacon) and carries `β=−13.2 bps, p=0.91`. A general reader's eyes glaze; the robustness machinery crowds out the economics. (Current-state: largely caught today — see H2.)
3. **The inference battery dominates the body; the economics is thin.** Section 3 (Inference) and §4.1 are wall-to-wall method names (CR1/CR2/CR3, WCB, FW, IM, CGBS, ACRT, Satterthwaite df, Pustejovsky–Tipton, Goodman-Bacon), and Table 3 is **12 rows of inference engines**. The paper reads as a methods-defense exercise; "why does the spread narrow?" gets less airtime than "does the estimate survive small-G correction?" The battery grew across referee rounds (R1 added 5 engines) with no pruning. (Current-state: manifestation of #67 — see H3.)

---

## Candidates — current-state verdicts (method step 5, mandatory)

| # | Candidate (source) | Current-state verdict | Disposition |
|---|--------------------|-----------------------|-------------|
| **H1** | **No agent inspects the *rendered* figure for visual legibility** (Figure 1 axis-title overlaps the plot). Holistic read. | **OPEN** | **Filed #71 — High (quality)** |
| H2 | Abstract method-name pileup / dense abstract. Holistic read. | **ALREADY ADDRESSED** | Closed-on-arrival (note a possible minor refinement) |
| H3 | Inference battery dominates; economics thin; battery accreted across referee rounds with no pruning. Holistic read + `LESSONS_PIPELINE` §3. | **DUPLICATE of #67** | Add corroboration to #67 |
| P1 | claim-grounder LLM design hit 32K-token output cap / timed out on a 423-claim paper. `LESSONS_PIPELINE` §"didn't work". | **DUPLICATE of #69** | Add corroboration to #69 (2nd run) |
| P2 | WCB singular-system / small-G pathology caught late (Stage 6 R1 referee), not proactively by the empiricist. `LESSONS_PIPELINE` §3, §"didn't work". | **OPEN (narrow)** | **Filed #72 — Med (quality/cost)** |
| P3 | claim-verifier tolerance tighter than paper-prose rounding → false PSE flags. `LESSONS_PIPELINE` §"didn't work". | **PARTIAL** | Note-only — Low |
| P4 | "Run polish even on a Stage 6 ACCEPT paper" — polish caught §48E/§48C, 8.3-vs-9.3-fold, citation mischaracterizations referees missed. `LESSONS_PIPELINE` §"what worked", §"next operator". | **ALREADY ADDRESSED / SUPERSEDED** | Closed-on-arrival (positive confirmation) |
| L1 | Macro empirical has no identification gate. `LIMITATIONS.md`. | **TRACKED (#18)** | Not new |
| L2 | `bls-census` SSA life tables unreachable from datacenter hosts. `LIMITATIONS.md`. | **Documented-deferred** | Not new |

### Verdict detail + citations

**H1 — figure-legibility gap. OPEN.** Every current figure gate checks **existence/inclusion/content**, never *rendered legibility*:
- `templates/agent_bodies/shared/polish-consistency.md:24` — deterministic *existence* check (figure produced but not `\includegraphics`'d).
- `templates/agent_bodies/shared/paper-writer.md:180` — instruction to *include* the headline figure.
- `extensions/empirical/agent_bodies/finance/empiricist.md:100` (and `macro/empiricist.md:113`) — instruct the *producing* agent to make "labeled, titled axes and a self-contained meaning," but this is a generation-side instruction, not a verification gate that reads the compiled PDF.
- `templates/agent_bodies/shared/polish-numerics.md:7,21` — re-checks figure *numbers*, not layout.
No agent opens the rendered figure image and asks "is the text legible, do labels/titles/legends collide with the data or each other, is anything clipped?" The axis-label overlap in Figure 1 passes all gates. **Systematic** (any matplotlib/pgfplots figure can collide labels, clip legends, or render illegible ticks); the recently-added headline-figure-mandatory fix raises the floor from "no figure" to "a figure exists," and the natural next floor is "the figure is legible."

**H2 — dense abstract. ALREADY ADDRESSED.** Current rules would flag this exact abstract on three independent counts:
- `templates/agent_bodies/shared/polish-prose.md:20` — criterion (a) **>100 words = `critical`** (this abstract spills onto p2, well over 100 words); criterion (b) referee-response numerics (`β=−13.2 bps, p=0.91`); criterion (e) notation.
- `templates/agent_bodies/shared/paper-writer.md:159` — abstract-is-prose / no-symbol rule.
The >100-word critical alone forces the abstract down, which squeezes out the five-engine enumeration. *Minor residual refinement (not filed):* none of the named criteria explicitly says "do not enumerate robustness engines by name in the abstract"; the word cap catches the symptom but not the cause. Could be a one-line addition to polish-prose criterion set if the pattern recurs in post-`75e5c9e` papers.

**H3 — battery dominates / accretion. DUPLICATE of #67.** #67 is "multi-round revision causes monotonic paper bloat (accretion with no pruning step)." This paper is a clean worked example: the inference battery went from ~1 engine to 5 (Table 3 = 12 rows) across R1→R3, with nothing pruned, and the methods-defense crowded out the economics. Corroborating evidence for #67, not a separate issue.

**P1 — grounder token cap. DUPLICATE of #69.** #69 is the claim-grounder cap/sharding fix (filed off finance-empirical-6, which hit limits at 341/822 tool uses on an 822-claim paper). This run is a **second independent hit**: the LLM-judgment grounder hit the 32K-token output cap and timed out at 600s with 100/423 entries written, forcing a rewrite to a deterministic Python matcher (`code/utils/ground_claims.py`) + 22-entry manual override map, converging in 8 rounds. Strengthens #69's priority (≥2 runs, different claim counts).

**P2 — late small-G detection. OPEN (narrow).** No proactive small-G guidance exists in the empiricist or the auditors. `extensions/empirical/agent_bodies/finance/empiricist.md` knows wild-cluster bootstrap as a *method* (`:87` canonical-packages) and seeds it (`:97`), but there is no instruction of the form: "when your design has a small effective cluster count interacting with high-dimensional fixed effects (the WCB/CR2 Satterthwaite-df degeneracy regime), add Frisch–Waugh partialling + Ibragimov–Müller + coarsened-FE + randomization inference as the principled small-G battery *proactively*, rather than waiting for a referee." Here the WCB singular-system error on NAICS-4-by-month FE (Satterthwaite df ≈ 1.13) was not flagged as a known pathology until Stage 6 R1 — a load-bearing referee comment that cost a Major-revision-equivalent empiricist re-fire (v9). Catching it at Stage 3a would save that cycle. *Narrow* (specific econometric scenario), so Med, not High.

**P3 — verifier tolerance. PARTIAL.** The current claim-verifier resolves values "within the declared rounding tolerance" via a per-entry `entry.tolerance_used` mechanism (`extensions/empirical/agent_bodies/shared/claim-verifier.md:1,46`), and the run's own in-flight fix tightened grounder type-tolerant matching + instructed paper-prose-aware tolerance. The mechanism exists; whether its *default* still over-flags last-digit ULP rounding is a calibration question, not a structural gap. Note-only, Low.

**P4 — polish on ACCEPT. ALREADY ADDRESSED / SUPERSEDED.** Stage 9 polish is **unconditional** — the pipeline always routes Stage 8 → Stage 9 → Stage 10 regardless of the Stage 6 verdict (`templates/shared/docs/stage_9.md:7`; `templates/shared/core.md:154`; Stage 8 hand-off at `templates/shared/docs/stage_8.md:10`). The lesson ("run polish even on a Stage 6 ACCEPT") describes the pipeline operating as designed; eight parallel polish agents always fire. Positive confirmation, not a gap.

---

## Prioritized backlog

| Priority | Item | Proposed template change | File(s) touched |
|----------|------|--------------------------|-----------------|
| **High (quality)** | **H1 — figure-legibility verification** | Add a rendered-figure legibility check. Two options: (a) extend `polish-consistency` (or a new lightweight `polish-figures`) to read each compiled figure image and flag overlapping labels/titles/legends, clipped elements, and illegible text — severity major when the *headline* figure is affected; or (b) add a generation-side render-and-inspect step to the empiricist/theory-explorer (compile the figure, read the PNG back, self-check legibility before shipping). (a) is more robust (catches paper-writer's `\includegraphics` sizing too). | `templates/agent_bodies/shared/polish-consistency.md` (or new `polish-figures` body + metadata + 3 assemblers); possibly `extensions/empirical/agent_bodies/{finance,macro}/empiricist.md`, `templates/agent_bodies/shared/theory-explorer.md` |
| **Med (quality/cost)** | **P2 — proactive small-G battery** | Add an empiricist instruction: detect the small-effective-cluster × high-dim-FE regime (e.g., effective G small relative to absorbed FE dimensions; WCB/CR2 Satterthwaite df collapse) and proactively report the FW + IM + coarsened-FE + RI battery, rather than a single CR-robust engine. Optionally a matching identification-auditor / empirics-auditor check. | `extensions/empirical/agent_bodies/finance/empiricist.md` (+ `macro/` once macro empirical exists); possibly `extensions/empirical/agent_bodies/shared/empirics-auditor.md` |
| Low | H2 residual — name the "robustness-engine enumeration" anti-pattern explicitly in the abstract rubric | One-line addition to `polish-prose.md:20` criterion set (only if the pattern recurs post-`75e5c9e`) | `templates/agent_bodies/shared/polish-prose.md` |
| Low | P3 — verifier default tolerance calibration | Confirm/adjust default last-digit-ULP tolerance | `extensions/empirical/agent_bodies/shared/claim-verifier.md` |
| — | Corroboration only | Add this run as a 2nd data point to **#69** (grounder cap) and **#67** (revision bloat) | (GitHub) |

## Closed-on-arrival (not filed, per method step 5)

- **H2** (dense abstract) — caught by `polish-prose.md:20` (>100-word critical + notation + referee-numerics) and `paper-writer.md:159`.
- **P4** (polish on ACCEPT) — polish is unconditional, `stage_9.md:7` + `core.md:154`.
- **L1** (macro identification gate) — #18. **L2** (SSA tables) — documented-deferred in `bls-census` skill.

## Progress note for #68

After this session, mark in the #68 progress list:
- [x] `finance-empirical-first-5-067efc37` — DONE (2026-06-05). Lessons + holistic read. Outcomes: figure-legibility gap → **filed #71 (High)**; proactive small-G battery → **filed #72 (Med)**; grounder cap → corroborated on #69; revision bloat → corroborated on #67; dense abstract + polish-on-accept → closed-on-arrival.
