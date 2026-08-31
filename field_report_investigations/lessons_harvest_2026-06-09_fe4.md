# Lessons harvest — `finance-empirical-4-34738d99`

**Date:** 2026-06-09
**Repo:** `automated-papers-produced/finance-empirical-4-34738d99`
**Run:** finished, `status: complete`, `current_stage: stage_10`, `problem_attempt: 1`. Variant `finance` + `--ext empirical` (theory-first hybrid). 13 theory versions, 10 Stage-6 referee rounds, 2 polish rounds. Editor downgraded `top-3-fin` → `field` at R1; converged on JFIP shape (editor Reject R7/R9, Major Revision R8/R10; freeform Reject R3/R7/R9/R10).
**Paper:** "Optimal Disclosure with Peer-Comparison Feedback: An If-and-Only-If Characterization of When Disclosure Backfires" — 401(k) menu-choice peer-comparison fixed-point model; disclosure-backfire identity (Lemma 2), iff condition (Prop 2), optimal-disclosure threshold $p^\ast\approx0.196$ (Thm 4), SECURE Act event study as motivating evidence. 37pp.

---

## Track B — holistic read (the high-value part)

Read as a reader, not a referee.

- **Title — GOOD.** Plain language, no acronym, tells you what the paper is about ("when disclosure backfires"). Slightly long ("An If-and-Only-If Characterization of…") but communicative. Closed-on-arrival.
- **Abstract — prose-dominant with notation residual.** Reads as prose for the first half; the back half carries $\phi^\ast$, $u/c$, $p^\ast\approx0.196$, $\rho_I$. This is the **already-addressed** class (`75e5c9e` polish-prose >100-word + notation rule; run shipped 2026-05-17, predates it). Corroborates the Low abstract-method-name/symbol residual noted on first-5. Not filed.
- **Tables — GOOD, legible.** Tables 1–4 render cleanly; no clipped columns, no overfull truncation (verified the Table 4 page visually + `-layout` extraction of Tables 1–3). All cross-refs resolve — **zero literal `??`** in the PDF (corroborates `#51` / build-verify holding; contrast fe5 `#75`).
- **Figures — THE DEFECT (B1, see below).** The paper's one motivating empirical exhibit — the SECURE Act within-plan event study — ships **as Table 4 only**. The actual *figure* of that event study (annual coefficients with 95% CI bands around the Sept-2021 effective date) was **produced, committed as a PNG, and given a valid `\includegraphics` in the source** — but ships **absent from the reader-facing PDF**. A reader has to mentally plot 6 table rows ($k=-3\dots+2$) to see the discontinuity at $k=0$ and the peak at $k=+1$ that a figure would show at a glance. This is the 5th figureless-main-body run in the sweep, via a **new mechanism**.

### B1 (HIGH, NEW mechanism) — headline figure orphaned in a non-`\input`'d section file

**What happened.** The figure float lives in `paper/sections/empirical_results.tex`:
```latex
\includegraphics[width=0.85\linewidth]{../output/stage3a/figures/secure_act_event_study.png}
\caption{SECURE Act event study: annual coefficients with 95\% CI ...}
\label{fig:secure_event_study}
```
The PNG **exists** at exactly that path (60 KB, committed). The `\includegraphics` is valid. But `paper/main.tex` `\input`s only 8 of the 14 section files — it **omits** `empirical_results`, `empirical_strategy`, `theorem`, `mechanism_design`, `welfare_counterfactuals`, `limitations`. A late consolidation refactor emptied four of those to 0 bytes (content merged into `model.tex` / `empirical_motivation.tex`) but **left the figure float behind in the orphaned `empirical_results.tex` (87 lines) and `empirical_strategy.tex` (47 lines), which are never `\input`'d.** Result: the figure never compiles into the PDF. Confirmed in the shipped artifact — `pdfimages -list main.pdf` lists **zero** embedded images and `pdftotext | grep -c Figure` returns **0**, while the build completed (Conclusion + References render). The live text was rewritten to reference the data as `Table~\ref{tab:event_study}` ("the year-FE event study"), so there is **no dangling `\ref` / no `??`** — the figure was dropped silently.

**Why it's distinct from the existing #71 sub-gaps.** The figure cluster now has four mechanisms:
| Run | Mechanism |
|-----|-----------|
| fe6 | figure produced upstream, **never placed** in source |
| fef4 | figure placed in **IA only**, not main body |
| fe5 / fe3 | figureless because the figure was **never produced** |
| **fe4 (new)** | figure produced + committed PNG + **valid `\includegraphics` in source**, but the source file is **orphaned (non-`\input`'d)** → absent from rendered PDF |

**Current-state verdict: PARTIAL / OPEN.** The dropped-figure gate (`polish-consistency.md:24`, item 10) fires only if **no** `\includegraphics` appears in any `paper/sections/*.tex`. In fe4 the `\includegraphics` string **is** present (in the orphaned file), so the gate **passes clean** — it checks for the *presence of the string*, not (a) that the containing file is reachable from `main.tex`'s `\input` graph, nor (b) that the *rendered PDF* actually contains an image. The Stage-5 build-verify gate (`stage_5.md:64-66`) greps `main.log` for undefined citations + overfull-`\hbox`, but runs **no rendered-PDF figure-presence check and no `\input`-graph reachability check**. Grep across `templates/` confirms **no orphaned-section check and no `pdfimages`-style rendered-figure check exists anywhere.** fe4 is the cleanest motivation in the cluster because here the source-grep gate is *guaranteed* to pass yet the reader sees nothing.

**Proposed general fix (two complementary, both root-cause-level, neither overfit to event studies):**
1. **Rendered-PDF figure-presence check** at Stage-5 build-verify: after the final `pdflatex`, assert the compiled `main.pdf` contains the expected figures — e.g. `pdfimages -list main.pdf` image count ≥ 1 (or ≥ the count of `\includegraphics` in `\input`-reachable sections), or `pdftotext main.pdf | grep -c "Figure"` ≥ expected. This single check catches **all four** cluster mechanisms (fe6/fef4/fe5/fe3/fe4 all ship a PDF with zero rendered figures despite a producible/produced exhibit) because it verifies the *artifact a reader opens*, not the source tree.
2. **Orphaned-section detection** (the deeper root cause, more general than figures): flag any `paper/sections/*.tex` with >0 non-comment lines that is **not reachable from `main.tex`'s `\input` graph**. This catches orphaned *content of any kind* left behind by a consolidation refactor — here a figure, but elsewhere it could be a whole results subsection, a robustness table, or a proof. A consolidation that empties some files to 0 bytes but strands others with live content is the recurring refactor hazard; the gate makes stranded content fail loud.

**Disposition: fold into #71 as a 5th-run corroboration + new sub-gap, and propose fixes (1) and (2) there.** The generality principle holds — fix (1) helps any paper whose figure looks nothing like an event study; fix (2) helps any paper whose orphaned content isn't a figure at all.

---

## Track A — self-graded lessons, current-state checked

| Lesson (from LESSONS_PIPELINE / LESSONS_PAPER) | Current-state verdict | Disposition |
|---|---|---|
| **#4 identification-auditor should run estimand-vs-claim at Stage 3a** (Year-FE absorbs the aggregate; design identifies the moderator interaction the prose elsewhere disowns; surfaced only at Stage 9 polish-identification) | **ALREADY ADDRESSED.** `identification-auditor.md:112-117` has an `Estimand-vs-theory mismatch (always check)` block whose canonical example is *verbatim* this failure: "Theory predicts a level effect; design identifies a difference-in-differences that absorbs the level into the fixed effect." Plus line 17 (estimand-vs-theory match) and line 1 ("does the design actually identify what it claims"). Run predates this. Residual: the auditor checks estimand-vs-*theory*; fe4's was estimand-vs-*prose-claim*, but line 1 framing covers it. | Closed-on-arrival; corroborates the existing check's value. Not filed. |
| **#1 add sympy/math-audit inside SUBSTANTIVE branch-manager checks on Reject-deepen** (R6→R7 wrong-direction restructure: convergent referee advice "lead with κ=0 baseline" was mathematically wrong — κ=0 forces θ*≥1/2, contradicting the empirical sign — caught only by the *next* round's structured-referee sympy) | **OPEN.** branch-manager at `gate-5-reject` (`branch-manager.md:8`, `:62-69`) produces a substantive-vs-cosmetic verdict by diffing v(N) vs v(N−1) against the deepen directive — it runs **no math validation** on the new content. So convergent-but-mathematically-wrong advice executes cleanly and is caught one round late. | **Surface to operator** (Med, theory-first only, quality-positive-but-~1-round-cost; the existing flow *did* self-correct in one round, so the realized harm is bounded). Operator discretion to file. |
| **#3 Stage-6 cap should fire on a within-tier (JFIP) convergence signal at round 5-6** (10 rounds run; structured Major-Revision all 10; freeform + editor converged on JFIP from R5/R8; rounds 6-10 traded one framing concern for another with no verdict movement) | **OPEN but subjective.** `editor.md:78` has an *advisory* within-tier outlet recommendation but **no encoded early-exit rule** (e.g. "if 3 referees converge on a within-tier outlet AND structured is stuck at the same concerns for N rounds → rebase to that outlet"). **2nd run on this theme** (fe3's L4 "editor treadmill one round earlier" was the 1st; noted OPEN/cost-only, not filed). | **Surface to operator** (cost, recurring across fe3+fe4, but genuinely subjective: "when is convergence real vs premature?"). Operator discretion. |
| Polish agents should reliably write to file (4 of 8 r1 polish agents returned inline) | **ALREADY ADDRESSED** (`3fba5cf` Stage-9 write-verification gate). 3rd+ run to hit it. | Closed-on-arrival; corroborates. |
| Abstract notation residual ($\phi^\ast$, $u/c$) | **ALREADY ADDRESSED** (`75e5c9e`; run predates). | Closed-on-arrival. |
| Caveat repetition / over-armored prose across polish rounds | polish-prose flags it; net the run self-corrected. | Note-only; no template gap (polish-prose owns it). |
| macro-id; SSA / Form-5500 data limits (LIMITATIONS.md = stock) | `#18` / documented-deferred. | — |

---

## Backlog (prioritized)

| ID | Pri | Type | Item | Verdict | Disposition |
|----|-----|------|------|---------|-------------|
| B1 | **High** | Quality | Headline figure orphaned in a non-`\input`'d section → absent from rendered PDF; source-grep figure gate passes clean (5th figureless run, new mechanism) | OPEN/PARTIAL | **Fold into #71** + propose (1) rendered-PDF figure-presence check and (2) orphaned-section detection at Stage-5 build-verify. **Corroborate #71.** |
| A1 | **High** | Quality/cost | No math validation on SUBSTANTIVE branch-manager Reject-deepens (convergent advice can be mathematically wrong, caught a round late; `math-auditor` is Gate-2-only, never re-fired at Stage 6) | OPEN | **Filed #80** (operator go-ahead: "any new math should be rechecked"). Diff-scoped math-auditor re-fire on formal-content-introducing Stage-6 Reject-deepens; theory-first only. |
| A2 | Med | Cost | No encoded Stage-6 early within-tier-convergence exit (2nd run, with fe3-L4) | OPEN/subjective | Note-only (subjective; fe3-L4 1st instance also not filed). |

**Closed-on-arrival (not filed):** estimand-vs-claim id-auditor check (ADDRESSED, `identification-auditor.md:112-117`); polish-write-to-file (ADDRESSED, `3fba5cf`); abstract notation (ADDRESSED, `75e5c9e`); macro-id `#18`; SSA/Form-5500 documented-deferred.

## Outward-facing writes — DONE (operator go-ahead 2026-06-09)
1. **#71 corroboration posted** — new orphaned-figure mechanism + proposed rendered-PDF figure-presence check + orphaned-section detection (5th figureless run; cleanest motivation — source-grep gate guaranteed to pass).
2. **A1 filed as #80** — math-auditor re-fire on formal-content-introducing Stage-6 Reject-deepens (operator: "any new math should be rechecked").
3. **A2 — note-only** (subjective; fe3-L4 1st instance also not filed).
4. **#68 progress list updated** — fe4 ticked, count → 26, next target `finance-empirical-first-2-e7fc624b`.
