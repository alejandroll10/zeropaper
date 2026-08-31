# Lessons Harvest — Issue #68

Date: 2026-06-06
Method: per issue #68 (two tracks — self-graded lessons + independent holistic paper read — with mandatory current-state verification against today's template before filing). **One repo per session, by hand. Finished runs only.**

## Repos examined this session

| Repo | pushedAt | `status` | Disposition |
|------|----------|----------|-------------|
| `finance-empirical-7-fedf5723` | 2026-06-02 | `running` (stage_3a) | **INCOMPLETE — skipped.** No paper, no LESSONS. (recorded in #68 progress) |
| `finance-empirical-first-6-73c46736` | 2026-06-01 | `running` (stage_1, problem_attempt 5) | **INCOMPLETE — skipped.** Never reached a paper. (recorded in #68 progress) |
| `referee-c31e5f30` | 2026-05-25 | (report mode, no state) | **Deferred** — report-mode run, no paper / no pipeline_state; needs a report-mode-specific method. |
| **`finance-empirical-first-4-90b646d3`** | 2026-05-22 | **`complete` (stage_10)** | **HARVESTED** (this is the session's real sweep). |

---

## `finance-empirical-first-4-90b646d3` — full harvest

**Run profile:** `finance` variant, `--mode empirical-first`, `--ext empirical`. Finished: shipped `paper/main.pdf` (36pp), full `paper/sections/*`, `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md`. 10 Stage-6 referee rounds, 2 polish rounds, 1 mechanism pivot, 1 cross-tier downgrade (top-3-fin → field), 1 within-tier outlet pivot (JFIP → JFQA). Final: JFQA-targeted credibly-identified bounded null.

**Paper:** *The Borrower-Side of EGRRCPA's Capital Relief: A Credibly-Identified Null in the 2019 Tailoring Cohort.* Bounds borrower-side AISD pass-through of the 2019 EGRRCPA tailoring cohort to roughly [−3.5, +5.2] bps via a within-firm-quarter Khwaja-Mian DiD on strict-lead-arranger syndicated facilities.

### Track B — holistic read (highest value)

- **Title:** mostly clean prose; "EGRRCPA" is a statute acronym (defensible — it's the named law), subtitle is clear. Acceptable. (Run predates the `75e5c9e` prose-title rule.)
- **Abstract: notation-and-method-name wall.** Opens fine ("We bound the borrower-side pass-through…") then becomes a slog of estimator names and inferential numerics: TWFE β̂=−0.77 bps (WB 95% CI [−3.39,+1.86]), BJS β̂=−1.51 (p=0.149), +5.21 (p=0.053) de-trended, TOST PASS/FAIL at ±5/±10, Rambachan-Roth M̄*≈1.1. The cohort label "K2" is used **before definition**. A general reader cannot parse the result. (Run predates `75e5c9e`.)
- **Figures: present in the repo, but the headline result figure is NOT in the main body.** `paper/figures/` holds `event_study.pdf`, `k2_event_study.pdf`, `aisd_ts.pdf`, `aisd_by_quarter_strict_lead.pdf` — the natural headline figures for a credibly-identified-null event study. The main body has **zero `\includegraphics`**; the only main-body figure is a TikZ **DAG** of the *posited mechanism* (Figure 1, p27, mechanism section). The event-study coefficient plot — the figure that lets the reader *see* the null — is `\includegraphics`'d **only in the Internet Appendix** (`internet_appendix.tex:89`). A reader of the main paper cannot see the headline; they reverse-engineer it from tables. (Run predates `3fba5cf`/`75e5c9e`.)
- **Contribution locatable:** yes — "a tight bound on the 2019 tailoring cohort pass-through" (p3), honest dual-verdict framing.
- **Reads well?** The honesty and identification rigor are genuine, but the abstract + intro are an estimator-name slog; the economics ("does freed bank capital reach borrowers?") is buried under the inference machinery.

Holistic defects: (1) **headline event-study figure relegated to the Internet Appendix; main body figureless** — *systematic*; (2) **abstract = method-name + p-value wall, undefined "K2"** — *systematic* (predates the fix); (3) **estimator-name density in body crowds out economics** — *systematic*.

### Track A — lessons found
`LESSONS_PAPER.md`, `LESSONS_PIPELINE.md`, `LIMITATIONS.md` (= stock template: macro-id #18 + SSA documented-deferred; no run-authored additions).

### Candidates — current-state verdicts (method step 5, mandatory)

| # | Candidate (source) | systematic? | Current-state verdict (+cite) | Disposition |
|---|--------------------|-------------|-------------------------------|-------------|
| **A1** | Headline result figure shipped in the **Internet Appendix only**; main body figureless. Holistic read. | yes | **PARTIAL** — `polish-consistency.md:24` (item 10) counts an `\includegraphics` in `paper/internet_appendix.tex` as satisfying the dropped-figure gate, so an IA-only / main-body-figureless paper **passes**. `paper-writer.md:180` says "main text" but is a generation-side instruction, not a gate. No gate enforces ≥1 result figure in `paper/sections/*.tex`. | **FOLDED INTO #71** (2026-06-06) — added as a 2nd sub-gap of the existing figure-gate issue (legibility + placement, same `polish-consistency.md:24`); title broadened. 2nd figureless-main-body run (finance-empirical-6 was 1st). |
| **A2** | identification-designer + identification-auditor missed the **any-role vs strict-lead-arranger cell-definition** error (cell pooled syndicate participants who don't set AISD with the lead who does). Run's "**worst silent failure** / most consequential design error" — slipped past designer + auditor + first empirics-auditor. `LESSONS_PIPELINE`. | yes | **OPEN** — `identification-auditor.md:34-118` DiD + banking-regulation + estimand-match checklist has no named failure mode for "within-cell variation must come from the unit that actually sets the outcome variable; non-deciding units pooled into the cell contaminate the estimate." Closest (`estimand-mismatch`, `se-not-clustered-at-treatment-level`) don't cover it. | **FILED #73** (2026-06-06) — framed general (treatment attributed to a non-controlling unit in multi-party settings: lead vs participant, bookrunner vs syndicate, lead vs co-advisor), scoped **conditional** (fires only when one outcome is attached to multiple parties and one sets it), placed in the **estimand-mismatch family** to avoid a low-precision standalone mode; + a who-sets-the-outcome prompt on identification-designer. |
| **A3** | Mischaracterized citation (Shahhosseini/BSS +27 bps anchor: wrong journal + interpretive-vs-direct share) survived **10 referee rounds**; only `polish-institutions`/`polish-bibliography` caught it at Stage 9. `LESSONS_PIPELINE`. | yes | **OPEN** — prose-claim citation scoring (FAITHFUL/APPROXIMATE/MISCHARACTERIZED) is a Stage 9 job (`polish-bibliography`). `bib-verifier.md` checks **cite-key validity only**; stage_5 / stage_8 docs have no prose-claim audit. | **DROPPED — not filed** (2026-06-06, operator decision). Scheduling tweak on a capability that already exists and worked: Stage 9 polish is unconditional, caught it, paper shipped correct; realized harm ≈ 0 (didn't drive the 10 rounds). Naive shift-left is either incomplete (Stage-5-only misses later-round citations) or expensive (re-audits whole bib every round); Stage 9 once-on-final-draft is the right home. Narrow "verify load-bearing anchors early" version was considered and judged low value-to-noise. Stage 9 owns it. |
| **A4** | empirics-auditor **OOM-killed twice** mid-execution (full re-execution under RAM pressure). `LESSONS_PIPELINE`. **2nd repo with an empirics-agent OOM** — finance-empirical-7's empiricist OOM-killed on a 146M-row `mf_holdings` full `pd.read_parquet`. | yes (cluster) | **PARTIAL/OPEN** — empirics-auditor already scopes the cache-bypassed rerun to *stochastic LOAD-BEARING* specs (`empirics-auditor.md:17,42-44`), but neither it nor `empiricist.md:100` carries **memory-safe large-table guidance** (polars streaming scan, column projection, avoid full-file `pd.read_parquet`). | **FILED #74** (2026-06-06) — framed general (a memory-efficiency directive for all data-handling agents: don't materialize what you'll filter; lazy scan + column projection + predicate pushdown), not a WRDS-specific patch; + per-skill scale notes on `wrds.md`/`mutual-funds.md`. Cross-repo OOM cluster. |
| C2 | On a mechanism pivot, paper-writer preserved stale prior-posit content → `polish-consistency` r1 found 4 critical internal contradictions. Lesson: give paper-writer an explicit "remove all references to the superseded posit" instruction. `LESSONS_PIPELINE`. | partly | **PARTIAL** — `polish-consistency` (Stage 9) catches the contradictions downstream (it did here); no prevention-side "purge prior posit" instruction at the pivot handoff. Adjacent to #67. | **Note-only** — prevention-vs-detection; operator's call. |
| C5 | Stage 6 cycled the full **10 rounds** though the structural ceiling was hit at r5/r6. Lesson: a more aggressive ship-now trigger (2 consecutive freeform <60, no new criticals). `LESSONS_PIPELINE`. | partly | **PARTIAL / borderline** — in tension with never-abandon ("keep going as long as each round surfaces any new issue", `stage_6.md:69`) + the existing tier-downgrade / branch-manager ceiling machinery. Deliberate design choice, not a clear gap. | **Note-only** — cost; operator's call. |
| C6 | `polish-prose` "verbatim cut" not aggressive enough (pre-trend caveat 9→5→3 mentions, target 2-3 never hit). | partly | **PARTIAL** — calibration of existing rule. | **Note-only (Low).** |
| H2 | Abstract notation/method-name wall + undefined "K2". Holistic. | yes | **ALREADY ADDRESSED** — `polish-prose.md:20` (>100-word critical + notation + referee-numerics) + `paper-writer.md:159` (prose-only abstract). Run predates `75e5c9e`. | Closed-on-arrival. **Corroborates** the Low "name the robustness-engine-enumeration anti-pattern in the abstract rubric" residual flagged in the first-5 harvest (2nd instance). |
| H3 | Estimator-name density in body crowds out economics. Holistic + lesson. | yes | **DUPLICATE-adjacent of #67** (here born-dense rather than accreted across rounds). | Mild corroboration of #67. |
| L1 | LIMITATIONS = macro-id gate. | — | **TRACKED (#18).** | Not new. |
| L2 | LIMITATIONS = SSA tables. | — | **Documented-deferred.** | Not new. |

### Net-new actionable (OPEN/PARTIAL) — dispositions (2026-06-06)
- **A1 (High, quality)** — main-body headline-figure gate (IA-only must not satisfy). 2nd run. **→ FOLDED INTO #71.**
- **A2 (High, quality)** — multi-party unit-of-treatment vs unit-of-control mismatch. **→ FILED #73** (general framing, conditional, estimand-mismatch family).
- **A3 (Med)** — shift-left citation audit. **→ DROPPED** (operator decision; Stage 9 already owns it, realized harm ≈ 0).
- **A4 (Med, cost)** — general memory-efficiency directive for data-handling agents (OOM cluster, ≥2 repos). **→ FILED #74.**
- **#67 corroboration** — **POSTED** (estimator-name density; 2nd data point).
- **A2 (High, quality)** — identification within-cell decision-unit contamination check. Run's worst silent failure.
- **A3 (Med, quality/cost)** — shift prose-claim citation audit left to Stage 5/8.
- **A4 (Med, cost)** — empirics memory discipline on large WRDS tables. Cross-repo cluster (≥2).

### Corroborations (pending go-ahead to comment)
- **#67** — estimator-name density / inference machinery crowding economics (mild; born-dense here).
- (first-5 residual) — abstract method-name-pileup anti-pattern, 2nd instance.

---

## Prioritized backlog (this session)

| Priority | Item | Proposed template change | File(s) touched |
|----------|------|--------------------------|-----------------|
| **High (quality)** | **A1 — main-body headline-figure gate** | Tighten `polish-consistency` item 10: require ≥1 result figure `\includegraphics`'d in the **main body** (`paper/sections/*.tex`); an inclusion that appears *only* in `paper/internet_appendix.tex` does NOT satisfy the headline-figure requirement (additional IA figures remain fine). Flag major when a figure-producing stage emitted figures but the main body has zero. | `templates/agent_bodies/shared/polish-consistency.md`; possibly a one-line reinforcement in `templates/agent_bodies/shared/paper-writer.md:180`. |
| **High (quality)** | **A2 — within-cell decision-unit contamination** | Add a named failure mode to the identification-auditor DiD/within-cell + general-hygiene checklist (e.g. `cell-pools-non-treating-units` — within-cell variation must come from the unit that actually sets the outcome variable; flag if non-deciding units are pooled into the matched cell), and a matching probe in `identification-designer`'s checklist. General across lead-vs-participant / lead-vs-co-manager / controlling-vs-minority designs. | `extensions/empirical/agent_bodies/finance/identification-auditor.md`, `.../identification-designer.md`. |
| **Med (quality/cost)** | **A3 — shift-left prose-claim citation audit** | Run a lightweight prose-claim citation check (FAITHFUL/APPROXIMATE/MISCHARACTERIZED) at Stage 5 (or Stage 8 bib-verify) alongside the existing cite-key existence check, so a mischaracterized anchor doesn't survive 10 referee rounds before Stage 9 catches it. | `templates/agent_bodies/shared/bib-verifier.md` or `polish-bibliography.md`; `templates/shared/docs/stage_5*.md` / `stage_8*.md`. |
| **Med (cost)** | **A4 — empirics memory discipline** | Add memory-safe large-table guidance to `empiricist` (polars streaming scan + column projection; never full-file `pd.read_parquet` on multi-100M-row WRDS tables) and make the empirics-auditor cache-bypassed rerun memory-aware. Cross-repo cluster. | `extensions/empirical/agent_bodies/{finance,macro}/empiricist.md`, `extensions/empirical/agent_bodies/shared/empirics-auditor.md`; possibly the `wrds`/`mutual-funds` skill bodies. |
| — | Note-only | C2 (purge-prior-posit on pivot), C5 (ship-now trigger), C6 (aggressive verbatim cut). | (not filed — operator's call) |

## Closed-on-arrival (not filed)
- **H2** abstract notation wall — `75e5c9e` (prose-only abstract; predates this run). Corroborates first-5's Low residual.
- **L1** macro-id → #18; **L2** SSA → documented-deferred.
