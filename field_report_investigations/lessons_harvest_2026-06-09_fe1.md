# Lessons Harvest — `finance-empirical-1` (2026-06-09)

**Repo:** `automated-papers-produced/finance-empirical-1`
**Run:** `status: complete`, `current_stage: stage_9`, `problem_attempt: 1`, `seeded: false`, `mode: none`.
**Variant/mode:** `finance` base variant + `--ext empirical`, **theory-first hybrid** (structural model with descriptive empirical calibration). One of the earliest finished runs in the org (shipped April 2026; `main.pdf` committed). The **last remaining finished run** in the #68 scope after `finance-paper-1`.
**Run shape:** theory v10+, referee_round 10 (cap), polish_round 2. One puzzle-triager **PIVOT** (relief-valve theory empirically falsified — predicted +29 pp, data showed −31 pp — rebuilt as a transparency-discipline mechanism). Mechanism-referee MISATTRIBUTED at r9 → forced the v10 Path A Bayesian filing-game microfoundation → VALID at r10. Target JF/JFE/RFS; self-assessed realistic home JFI / RoF / JFQA (field-tier).
**Paper:** 41pp `paper/main.pdf` read holistically. `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md` (no `LIMITATIONS.md`).

Paper subject: captive 401(k) menu choice when sophisticated participants can exit via a self-directed brokerage window. Headline analytical result is a **closed-form regime threshold** `ρ_crit(δ) = δ − γ/(1−μ*_{B=0}(δ))` with a **counterintuitive reversal** `μ*(B=1) > μ*(B=0)` (the window *raises* the affiliated-fund threshold via litigation visibility), plus a **population-level welfare integral** and a Proposition-8 **linearized-vs-global discriminant** (global threshold 38.9% larger; welfare error 54–195% across the ρ range). Empirical leg: Form 5500 + WRDS, Bundle×B = −25.4 pp (t = −7.3, N = 46,373), descriptive calibration consistent with the high-ρ disciplining regime.

---

## Track B — holistic read (the high-value part; self-grade is blind to it)

**Reads well on:**
- **Title — GOOD.** "Brokerage Windows in Captive 401(k) Menus: A Closed-Form Regime Threshold and a Population-Level Welfare Integral." Plain-language, no acronym wall, tells you what the paper is about (a touch long but clear). Clears the `75e5c9e` bar (run predates it).
- **Author — `Anonymous` / `Anonymized institution`.** No `#81` placeholder-leak defect.
- **Cross-refs — clean.** `pdftotext | grep '??'` = **0**; every `\ref`/`\cite` resolves. No `#75` defect. (Run predates the build-verify ref/cite gate — another clean-build-without-the-gate data point.)
- **Tables — legible.** No clipping/overfull `\hbox`; no `#51`/`#85` defect.

**Defect A1 (High) — zero figures in 41 pages despite a headline regime-threshold reversal and a linearized-vs-global welfare-error curve; 35+ figures produced and unused.**
`pdfimages -list` = **0 embedded images**; no `\includegraphics`, no `figure`/`tikzpicture` environment in any of the nine `paper/sections/*.tex`. The headline is the canonical "show me the plot" object twice over: (i) a regime threshold with a *sign reversal* `μ*(B=1) > μ*(B=0)` plotted against δ, and (ii) Proposition 8's linearized-vs-global threshold gap and the 54–195% welfare-integral error across ρ. The paper presents both as **tables and inline prose** ("Tables 7 and 3 report results under both forms with linearization-error columns").

Meanwhile **35+ figures sit unused** across `output/stage1/`, `output/stage3a/`, and `output/stage3b/`, including the literal headline objects: `output/stage3a/figures/mu_star_vs_delta.png` (the threshold vs δ), `output/stage3a/figures_v3/theorem7_dW_drho.png` (the headline welfare derivative), `output/stage3a/figures_v3/continuity_mu_star_through_rho_crit.png` (the regime flip), `output/stage3a/figures_v3/sensitivity_strip_vs_rho.png`, and even `output/stage3b/figures_v7/event_study_main.{pdf,png}`. The producing agent made figures of the result; the paper shipped figureless. **LESSONS-blindness is total** — neither lessons file mentions a missing figure.

This is the **9th figureless-body run in the sweep** (fe6, fe4, fe5, fe2, fec2, fef2, fl1, fp1, now fe1) and the **first theory-first-hybrid (`finance` + `--ext empirical`) worked example** — prior empirical examples were `empirical-first` or empiricist-produced; fp1 was pure-theory `stage2b`. fe1 confirms the defect spans the theory-first-hybrid route too.

**Current-state verdict: closed-on-arrival → corroborate `#71` with a NEW sub-gap.** The dropped-headline-figure gate (`polish-consistency.md:24`, item 10) under `--ext empirical` checks `output/stage3a/figures/`, which **is** non-empty here, with no `\includegraphics` anywhere → the gate **fires (major) on a current run**. fe1 (Apr 2026) predates the gate (`3fba5cf`). BUT this run exposes a **literal-directory matching sub-gap that `#71` does not yet cover**: item 10 scans exactly three hard-coded dirs — `output/stage2b/figures/`, `output/stage3a/figures/`, `output/stage3b/figures/` — while this run's **post-pivot headline** figures live in **version/pivot-suffixed siblings**: `stage3a/figures_v3/`, `stage3a/figures_pivot/`, `stage3b/figures_v7/`, `stage3b/figures_smallplan/`, `stage3b/figures_v5/`, `stage3b/figures_v6/`. The gate fires here only **by luck** — the unsuffixed base `stage3a/figures/` happens to also be non-empty, but with the *stale pre-pivot* figures. Two consequences: (1) the gate names the wrong (stale base-dir) figure to the paper-writer, not the current `figures_v3`/`figures_v7` headline; and (2) **a run whose figures land ONLY in a suffixed subdir — common after a pivot or any vN theory iteration, where the latest exploration writes to `figures_vN/` — would slip the literal-path gate entirely and false-pass figureless.** Proposed general fix: broaden item 10's scan to a recursive glob `output/stage{2b,3a,3b}/figures*/**/*.{png,pdf}` (capture suffixed siblings), and when multiple version-suffixed dirs exist prefer the highest-version / pivot-latest subdir when naming the headline figure to include. **No new issue; post a `#71` corroboration (9th figureless run; new suffixed-subdir sub-gap).**

**Defect A2 (presentation) — notation-dense abstract.**
The abstract interleaves heavy structural notation throughout: `ρ`, `ΔΠ_S^reg = ρ·B·(1−μ)·1{τ=S}`, `ρ_crit(δ) = δ − γ/(1−μ*_{B=0}(δ))`, `ρ = λθ_p φc α*_S μ_eq`, plus bolded mid-abstract caveats about A4 being "a parameterization choice, not a derivation." Inside-baseball and hard to read cold.
**Current-state verdict: closed-on-arrival** (`75e5c9e`). `polish-prose.md:20` criterion (a) (>100-word abstract → critical) and (e) (inline math / parameter expressions / cross-refs) both fire on a current run. Run predates the mandate. Nothing to file.

---

## Track A — self-graded pipeline lessons (current-state checked)

**B1 (High, quality, NEW issue candidate) — the idea-prototyper systematically selects for INCREMENTAL ideas over NOVEL ones.**
LESSONS_PIPELINE's lead lesson: the single-shot prototyper attempts the headline derivation once and returns BLOCKED if it doesn't go through. But NOVEL ideas are often novel *precisely because* nobody has done the derivation — they need a harder proof technique (different equilibrium concept, continuous-time reformulation, fixed-point argument) a one-shot attempt won't try. So "doesn't go through quickly" gets conflated with "fundamentally intractable," and the survival filter selects for ideas where the standard playbook works on the first try — which correlates almost perfectly with INCREMENTAL/OBVIOUS. In this run both NOVEL sketches (wage-kickback substitution, common-agency amplification) got BLOCKED at prototype; the surviving, shipped idea was the tractable INCREMENTAL one.
**Current-state verdict: OPEN.** Confirmed in the current template:
- `idea-prototyper.md:33` — binary `Verdict: TRACTABLE / BLOCKED`; no "blocked-in-easy-mode vs blocked-after-hard-attempt" distinction.
- `idea-prototyper.md:78` — **"One attempt per idea. Don't try multiple approaches. The sketch should have specified the proof strategy. Try that strategy. If it fails, report the failure."** (explicitly forbids attempting a harder technique).
- No orchestrator rule anywhere ("when all NOVEL sketches BLOCK and only INCREMENTAL/OBVIOUS survives, force a second Stage 1 round on harder problems") — Gate 1b/1c routing has no such guard.
This is the **highest-leverage stage** (problem selection determines the ceiling). **Distinct from `#70`** — #70 is a *false positive* on the surprise axis (over-crediting a surprise that holds only at a knife-edge); B1 is a *false negative* on the tractability axis (killing a NOVEL idea because the single-shot prototype failed). Both touch idea-prototyper; the mechanisms are opposite. → **File a new issue** (general: distinguish proof-difficulty-blocked from impossibility-blocked; allow ≥1 harder-technique retry on NOVEL sketches; force a second Stage 1 round when the NOVEL portfolio is wiped and only INCREMENTAL survives). Cross-ref #70.

**B2 (the run's #1 missing-component recommendation) — "an identification-strategist agent at Stage 3b." → ALREADY ADDRESSED.**
LESSONS_PIPELINE calls this "probably the single biggest pipeline change that would move papers from field-tier to top-3": an adversarial design check that enumerates identifying variation in the data, scores each strategy on relevance/exclusion/power, and either proposes a design or forces the theory toward a shock-response prediction the data can identify (the run left Tibble-2015 DD, recordkeeper-bundling IV, and cross-state ERISA case-law variation on the table).
**Current-state verdict: ALREADY ADDRESSED** — the pipeline now ships exactly this pair under `--ext empirical` (run predates both):
- `identification-designer` fires at **Stage 3a step 1** on every pass *before* the empiricist plans (`stage_3a_empirical.md:35`), as "the single authority on whether the empirical work needs identification at all," producing a ranked menu of strategies with assumptions/diagnostics/estimand/theory-match/relevance — verbatim the LESSONS spec.
- `identification-auditor` (step 3, `stage_3a_empirical.md:53`) adversarially audits the plan with severity-ranked named failure modes and an estimand-vs-theory match, PASS/REVISE/FAIL routing.
- The "force the theory toward an identifiable prediction or accept field-tier" leg is the FAIL routing (`stage_3a_empirical.md:57`): exhausted strategies → reframe descriptive OR puzzle-triage (HONEST-NULL / BACK-TO-IDEA).
The strongest validation in the sweep that a load-bearing LESSONS recommendation is now built. **Not filed.**

**B3 — "no late-stage novelty re-check on post-pivot mechanism." → ALREADY ADDRESSED.**
The pivot reconstructs the mechanism to fit the contradiction; the run says novelty was never re-checked afterward. Current pivot sequence re-runs Gate 3 on the pivoted theory: `stage_puzzle_triage.md:58` ("**Re-run Gate 3.** Novelty check on the pivoted theory. KNOWN/INCREMENTAL → escalate") and step 5 (`theory_draft_v1` under the incremented `theory_attempt`, fresh novelty `_vN.md`). Run predates the explicit pivot-sequence wiring. **Not filed.**

**B4 — "empirical-design revisit gate after the first 3a pass." → ALREADY ADDRESSED (subsumed).**
Subsumed by the identification-designer re-fire on theory revision (`stage_3a_empirical.md:101–113`): Stage 3a is not one-shot; on any substantive theory change the designer re-fires and the menu is re-derived before Gate 4 can advance. **Not filed.**

**B5 — "Stage 6 round count too generous (10 rounds)." → note-only / subjective; corroborates the editor-treadmill cluster.**
The run earned ~3 content-bearing rounds (Path A integration, Prop 8, mechanism-VALID); the rest tightened language. This is the same theme as fe3-L4 / fe4-A2 / fec2-A1 / fe2 (Stage-6 treadmill, no encoded early-within-tier-convergence exit, cost-only/subjective). No clean gate; `editor.md` has no encoded treadmill rule. **Note-only, no issue** (cost-only, subjective — consistent with prior sweep dispositions).

**B6 — "self-attacker redundant with referee triplet." → WON'T-DO / by-design.** Self-attacker is a Stage-4 *pre-referee* catch; merging it into Stage 6 forfeits the find-before-referee value. Note-only.

**B7 — "branch-manager has no journal-fit veto; never-abandon shipped field-tier aimed at top-3." → by-design.** Never-abandon is deliberate; branch-manager already issues a course/re-target recommendation (it called field-tier at v5, per LESSONS_PAPER). WON'T-DO (deliberate design; consistent with the tier-downgrade WON'T-DO disposition in #68).

**B8 — "when a pivot fires, re-enter at Stage 0 with the contradiction as the central question." → note-only / by-design.** puzzle-triager already has HONEST-NULL→Stage 0 and BACK-TO-IDEA routes; the bar is deliberately high. Subjective. Note-only.

---

## Closed-on-arrival summary

| Candidate | Verdict | Disposition |
|-----------|---------|-------------|
| A1 zero figures (35+ produced, post-pivot headline in `figures_v3`/`figures_v7`) | closed-on-arrival (gate fires today) + NEW sub-gap | **corroborate #71** (9th run; suffixed-subdir literal-path sub-gap) |
| A2 notation-dense abstract | ALREADY ADDRESSED (`75e5c9e`) | not filed |
| Plain title / `Anonymous` author / clean cross-refs / legible tables | clean | no #75/#81/#51 defect |
| B1 idea-prototyper selects INCREMENTAL over NOVEL | **OPEN** | **filed #90** (distinct from #70) |
| B2 identification-strategist (run's #1 ask) | ALREADY ADDRESSED (identification-designer + -auditor, Stage 3a) | not filed — strongest validation in sweep |
| B3 post-pivot novelty re-check | ALREADY ADDRESSED (`stage_puzzle_triage.md:58`) | not filed |
| B4 empirical-design revisit gate | ALREADY ADDRESSED (3a re-fire on theory revision) | not filed |
| B5 Stage 6 10-round cap | note-only / subjective | editor-treadmill cluster (fe3-L4/fe4-A2/fec2-A1/fe2) |
| B6 self-attacker redundant | WON'T-DO (by-design pre-referee catch) | note-only |
| B7 branch-manager journal-fit veto | WON'T-DO (never-abandon by design) | note-only |
| B8 pivot → re-enter Stage 0 | note-only / by-design | subjective |

## Actions

1. **Filed #90** (operator go-ahead 2026-06-09) — idea-prototyper systematically selects INCREMENTAL over NOVEL (single-shot "one attempt per idea"; binary TRACTABLE/BLOCKED; no force-second-round when the NOVEL portfolio is wiped). High / quality. Cross-ref #70.
2. **Corroborated #71** (operator go-ahead 2026-06-09; comment posted). 9th figureless run (first theory-first-hybrid worked example) + NEW sub-gap: item 10's literal three-dir scan misses version/pivot-suffixed figure subdirs (`figures_v3/`, `figures_v7/`); fires here only by luck on the stale base dir; a figures-only-in-suffixed-subdir run false-passes. Proposed fix: recursive `figures*` glob + prefer highest-version subdir.
3. **#68 progress list** — ticked `finance-empirical-1`; last finished run in scope (sweep substantially complete; remaining repos are known INCOMPLETE / seeded-never-launched / report-mode-deferred).
