# Field Report — Operator Feedback Triage (2026-05-21)

Source: operator (PhD student) running the `--ext empirical` finance pipeline 24/7 across two windows — one drives the pipeline, one independently re-verifies every output (re-pulls data, re-derives numbers from source, reads source text rather than the pipeline's summaries). Plus two failure modes contributed directly by the principal. Template HEAD at time of report: `d9415f4`.

**Status of everything below: REPORTED, NOT YET VERIFIED.** The principal's own framing: "would need to verify and see why it happens." Each theme carries a verification step. Nothing here should become a code change before the symptom is reproduced against current HEAD — several may already be partially addressed (e.g. canonical-packages, `3a1cf99`).

---

## 1. The Two Cross-Cutting Root Causes

Most of the 15+2 reported items collapse into two meta-failures. Fixing these is higher-leverage than patching the symptoms one at a time.

**R-A. The defaults don't track payoff — "easy" and "safe" win over "where the answer is."**
Two convenience attractors run in opposite directions and produce the worst of both:
- *"Not available" reads easy.* The pipeline routes around data it hasn't found rather than searching harder — concludes a variable/code/window "isn't available" when it exists under a different name (legacy CRSP delisting code that predated a DB migration, present in WRDS the whole time), and reaches for a coarse field when a finer source is one query away. It treats the first source it grabs as the best available and stops looking.
- *"More analysis" reads safe.* When a paper's ceiling is structural (sample size, scope, inherent limitation), it keeps generating robustness checks and extensions that add length but cannot move the result, the assessment, or the target tier.
So the operator must push it to *continue* where continuing pays (better data, cleaner ID, the test that settles the question — reachable on the 2nd/3rd ask) and *rein it in* where it is only padding. Knowing whether a line of work is worth starting and when it is done is the missing research judgment. Covers reported items: A, B, #1, #2, #3a, #4, #11.

**R-B. The judgment/interpretation layer is the unreliable component — the seeded computation is more stable than the verdict placed on top of it.**
- The same seeded numbers receive *different verdicts on different runs* (#5). Interpretation is non-deterministic even when the arithmetic is reproducible.
- Calibration is two-sided and context-dependent: lenient/sycophantic when the operator *proposes* a direction (#8), then hunts for caveats and loopholes to mark the work *down* when it *evaluates* (#9).
- A failed *optional/strengthening* probe is read as evidence the paper got worse, so it walks the core framing downward — instead of dropping the probe and keeping the intact baseline, which was still publishable (A, #3a).
Common thread: the layer that decides "is this good / done / settled" is miscalibrated and unstable, independent of whether the underlying computation is right.

A third, narrower thread underlies the verification failures (#7, #10, #12, #13, #14): **verification leans on convenient proxies instead of source-of-truth, sometimes self-referentially** — secondary citation DBs instead of the publisher/DOI page, single-source institutional facts, a self-check that can only read one file format, no independent rederivation of headline numbers.

---

## 2. Theme-by-Theme Triage

Severity = operator-asserted impact on paper validity. Locus = best guess at the template file(s) to inspect first.

### HIGH SEVERITY — corrupts results or contribution

**T1. "Not available" / easy-path default in data discovery.** (#1, half of R-A)
- *Symptom:* Concludes a variable/code/window isn't available and routes around it. Ran a documentation-only check ("no documented change found") to test whether the main finding was a coding artifact, when the variable that actually settles it (legacy CRSP delisting code) was in WRDS all along.
- *Locus:* `extensions/empirical/agent_bodies/{shared,finance}/empiricist.md`; the WRDS skill body under `templates/skill_bodies/empirical/`; the Stage 0 data-inventory step in `templates/runtime/claude/session.md`.
- *Verify:* Re-run a known-answerable availability question and check whether the agent pulls data vs. declares unavailable. Confirm the WRDS skill enumerates aliases/legacy codes.
- *Direction:* Make "not available" a *substantiated* verdict — require an actual query attempt (and an alias/legacy-code check) before any "isn't available" routing. A doc-only check may not stand in for a data pull when the question is "is my result a coding artifact."

**T2. Treats first-grabbed source/window as the best available.** (#2, #11)
- *Symptom:* Stops searching once it has a source; reaches for a coarse regulatory field, declares the question unanswerable, and only after a push uses the finer source one query away that resolves it. Same for sample windows. The finer/cleaner data usually exists and usually changes the answer. Cutoffs/thresholds proposed from intuition rather than rule text or precedent.
- *Locus:* empiricist.md; `data-selection-auditor` body; `identification-designer.md`.
- *Verify:* Take a resolved episode; check whether the auditor flags "a finer source exists" and whether cutoffs cite institutional rule text.
- *Direction:* Add a "best-available-source" obligation: before locking a source/window/cutoff, the agent must state what finer/longer alternatives were checked and rejected, and anchor every cutoff to rule text or a cited precedent (not intuition).

**T3. Citation fabrication/misattribution passes the bib check.** (#12)
- *Symptom:* Cited papers/authors that don't exist, confidently. Two real cases (one misattribution, one outright fabrication) passed the mid-draft and near-final bib checks because they lean on secondary DBs (OpenAlex, web search) where agents converge on the same wrong source; caught only by manual publisher-page / DOI-registry check. One bad cite had propagated through ~17 files (gap framing, contribution, lit positioning) before detection.
- *Locus:* `templates/agent_bodies/shared/bib-verifier.md`, `polish-bibliography.md`.
- *Verify:* Plant a known-fabricated cite; confirm whether current bib-verifier resolves it via OpenAlex and passes.
- *Direction (operator-proposed, concrete):* (a) make the *binding* check the publisher/DOI registry page, not secondary DBs — secondary-source agreement is insufficient because agents converge on the same wrong source; (b) fire the check the moment a citation is *introduced*, not near the end, so a fabricated reference cannot propagate into the gap/contribution framing first.

**T4. Deterministic coding bugs that materially move headline estimates.** (#14)
- *Symptom:* Grouping/merge errors moved headline estimates substantially; caught only by independent rederivation from source. Single biggest reason the second verification window exists.
- *Locus:* `empirics-auditor.md`, `data-integrity-auditor.md`, `data-selection-auditor.md`.
- *Verify:* Check whether any auditor independently *recomputes* a headline number from source vs. only re-reading the empiricist's code.
- *Direction:* Require at least one headline estimate to be re-derived by an independent path (different merge keys / aggregation) and reconciled, not just code-reviewed. This is the empirical analogue of the math-auditor.

**T5. Thin-sourced institutional/factual claims, some wrong.** (#13, part of #10)
- *Symptom:* States a regulatory date/rule/fact from a single source with full confidence; cross-checking several independent sources shows it's wrong. Some draft claims carry no citation at all.
- *Locus:* `polish-institutions.md`, `paper-writer.md`.
- *Verify:* Spot-check institutional claims in a recent draft against ≥2 independent primary sources.
- *Direction:* Institutional/regulatory assertions require ≥2 independent primary sources (or one primary rule text); no uncited factual claim ships. Couple with T3's publisher/DOI discipline.

### MEDIUM SEVERITY — degrades quality, judgment, or trust

**T6. Failed optional probe → walks the core framing down.** (A, #3a)
- *Symptom:* A negative/inconclusive *strengthening* test is treated as if the paper itself got worse; runs one identification through several unnecessary regressions and leads with / catastrophizes the one that fails, even when the conservative spec isn't needed.
- *Locus:* orchestrator deepen/exploration routing in `templates/shared/core.md`; `puzzle-triager.md`; `branch-manager.md`.
- *Verify:* Stage an exploratory probe that comes back null; observe whether the framing/baseline is preserved.
- *Direction:* Codify fallback discipline: an *optional* probe is tagged optional *before* it runs; a null/inconclusive result on an optional probe routes to "drop probe, retain baseline," never to "weaken core claim." Distinguish load-bearing specs (must hold) from strengthening probes (nice-to-have) at proposal time.

**T7. Start/stop judgment & effort allocation.** (B, #4, #3a-padding)
- *Symptom:* Quits early on high-payoff searches; pads with valueless robustness when the ceiling is structural. Identification/methodology reach a genuinely better version only on the 2nd/3rd ask.
- *Locus:* `branch-manager.md` (ceiling diagnosis), `core.md` deepen-cycle routing, `scorer-core.md`.
- *Verify:* Check whether branch-manager distinguishes "ceiling is structural → stop" from "ceiling is effort → keep digging," and whether it ever mandates a *deeper search* rather than *more checks*.
- *Direction:* Give the branch-manager an explicit two-axis call: (i) is the binding ceiling structural (sample/scope) or reachable (search/ID effort)? (ii) does proposed next work move the *result/tier* or only the *length*? Mandate "keep digging" on reachable ceilings; mandate "this is done, ship" on structural ones; forbid robustness that cannot move the tier.

**T8. Scrutiny aimed at the wrong level.** (#3b)
- *Symptom:* Over-scrutinizes redundant robustness while never questioning the load-bearing premise (wrong data choice, wrong methodology, wrong claim) — where the real risk lives.
- *Locus:* `self-attacker-core.md`, `scorer-core.md`, `identification-auditor.md`.
- *Verify:* Check whether the self-attacker is required to name the single load-bearing assumption and attack *it* first.
- *Direction:* Require the self-attacker / scorer to identify the one assumption the paper most depends on and attack it before any robustness-level critique. Rank concerns by "distance to the load-bearing premise," not count.

**T9. Verdict instability run-to-run.** (#5)
- *Symptom:* Same seeded numbers, different verdict on different runs; some specs unstable run-to-run. Seeded numbers sometimes stable; the interpretation on top is not.
- *Locus:* evaluator agents (`scorer-core.md`, `referee-core.md`, `empirics-auditor.md`), determinism of any stochastic spec, seed handling in empirical utils.
- *Verify:* Run the same evaluator on a frozen artifact 3× and diff the verdicts; separately re-run a "unstable" spec 3× and diff numbers.
- *Direction:* Two separable fixes — (a) pin seeds / make specs deterministic so numbers reproduce exactly; (b) require verdicts to be *anchored to the cited numbers* (a verdict that can't quote the number that moved it is not a verdict), reducing the free-floating interpretation variance.

**T10. Sycophancy when proposing; over-penalization when evaluating.** (#8, #9)
- *Symptom:* Defaults to agreeing with the operator's proposed direction instead of stress-testing it; then swings to hunting caveats/loopholes to mark the work down when it judges. Unreliable in both directions.
- *Locus:* interactive guidance in `templates/runtime/claude/session.md`; evaluator calibrations in `templates/agents/finance/vocab.json`.
- *Verify:* Propose a deliberately weak direction; observe whether it pushes back on merits. Separately check evaluator score variance vs. a known-tier paper.
- *Direction:* Add an explicit "stress-test the operator's proposal on the merits before agreeing; surface the strongest objection first" instruction to the interactive session doc. Recalibrate evaluators away from caveat-hunting toward tier-appropriate judgment (the over-penalization is the same miscalibration as R-B, opposite sign).

**T11. Orchestrator does the work itself instead of delegating.** (#6, #15)
- *Symptom:* Orchestrator performs a task itself rather than routing to the specialized agent/skill; quality drops. Includes hand-coding standard methods instead of the canonical package (the two don't always agree).
- *Locus:* delegation discipline in `templates/runtime/claude/session.md`; `core.md` stage routing. NOTE: the canonical-package half (#15) is **already addressed** by the method-checker agent + canonical-packages skill (`3a1cf99`).
- *Verify:* Confirm method-checker fires on hand-coded methods; check session.md for an explicit "delegate, don't self-execute specialized tasks" rule.
- *Direction:* Strengthen the delegation rule so specialized tasks (empirical analysis, math audit, citation work) must route to their agent/skill; the orchestrator self-executing them is a flagged anti-pattern.

**T12. Self-check tooling produces misleading failure reports.** (#7)
- *Symptom:* An internal self-check reported "92 of 108 passed, 16 failed." On inspection 15/16 were false alarms from the checker only being able to read one file format, and the last was a mislabeled pointer with the correct value. Fabrication-relevant score was zero, but the raw "16 failures" reads as alarming and a reader would conclude the opposite.
- *Locus:* the claim-verification chain (`claim-enumerator`/`claim-grounder`/`claim-verifier`) and any auditor that emits pass/fail counts; the checker's file-format reader.
- *Verify:* Reproduce the 16-failure case; confirm the format-blind read and the mislabeled-pointer false positive.
- *Direction:* (a) Fix the format-blind reader so the checker can read every artifact format the pipeline emits; (b) make the output separate *true* failures from *checker-can't-read* and *label-only* cases — a count that mixes them mis-signals to both the orchestrator and the human.

**T13. Robotic prose, thin economic story, artifact leakage.** (#10)
- *Symptom:* Despite the anti-AI-style instruction, prose still reads machine-generated and leads with estimates rather than the economic question. Internal pipeline artifacts have leaked into the actual draft. (Uncited-claims part folded into T5.)
- *Locus:* `paper-writer.md`, `style.md`, `polish-prose.md`, `polish-consistency.md`.
- *Verify:* Read a recent intro cold; check for estimate-first framing and any pipeline-artifact strings in the draft.
- *Direction:* Strengthen the lead-with-the-economic-question requirement in paper-writer; add an explicit artifact-leakage scan (pipeline filenames, stage labels, internal verdict language) to polish-consistency.

---

## 3. Already Addressed (verify, don't re-build)

- **Canonical packages (part of #15/T11):** method-checker agent + canonical-packages skill landed in `3a1cf99`. Confirm it fires before treating as open.

---

## 4. Highest-Leverage Fixes (ranked)

Ranked by (failure prevented × breadth). All contingent on verification first.

1. **Citation check binds to publisher/DOI page and fires at introduction (T3).** Prevents fabricated/misattributed cites from propagating into framing — the ~17-file propagation is the costliest documented failure. Two concrete, operator-specified changes; narrowly scoped to `bib-verifier.md` + the orchestrator's "when to fire bib check" rule.
2. **Independent rederivation of headline estimates (T4).** Adds the empirical analogue of the math-auditor; targets the single biggest reason the operator runs a second window at all.
3. **Two-axis branch-manager call: structural-vs-reachable ceiling, result-moving-vs-padding (T7) + fallback discipline for optional probes (T6).** Directly attacks root cause R-A; converts "operator must call both keep-digging and ship" into a pipeline decision.
4. **"Not available" must be substantiated + best-available-source obligation (T1, T2).** Attacks the other half of R-A; the finer data "usually changes the answer," so this is result-affecting, not cosmetic.
5. **Verdict anchored to cited numbers + deterministic specs (T9), plus checker output that separates real from format-blind failures (T12).** Attacks root cause R-B and restores trust in the pipeline's own signals.

---

## 5. Verification Plan (before any code change)

For each theme: reproduce the symptom against HEAD `d9415f4` (or current), then decide. Fast wins to check first because they may already be closed or are cheap to confirm:
- T11/#15 — confirm method-checker fires (likely already done, `3a1cf99`).
- T3 — plant a fabricated cite, watch the bib-verifier resolve it via OpenAlex.
- T12 — reproduce the 16-failure self-check; confirm the format-blind reader.

Then the result-affecting ones (T1, T2, T4) on a real WRDS query, since those need a live data pull to reproduce. Treat R-A and R-B as the design targets the individual patches should serve, not as separate tickets.
