# Lessons harvest — `finance-llm-1-96cea289`

**Swept:** 2026-06-09. **Run:** `finance-llm-1-96cea289` — `finance` variant `+ --ext theory_llm` (legacy `finance_llm`), **seeded** (`seeded: true`), `status: complete`, `current_stage: complete`, `problem_attempt: 1`. Shipped **2026-05-03** (the most-recent not-yet-swept finished run; everything newer is swept or known-skip). 5 theory versions, 5 referee rounds, 1 puzzle-triager RECONCILE, 2 polish rounds; tier marched the full finance ladder `top-3-fin → field → letters` and shipped at **`letters`**.

Tracks: (A) self-graded `LESSONS_PAPER.md` + `LESSONS_PIPELINE.md` (no `LIMITATIONS.md` committed); (B) holistic read of `paper/main.pdf` (39pp).

## Holistic read — how the paper reads

The seed is an LLM-evaluator-architecture question (within-session vs. fresh-session vs. clean-rubric evaluators under misspecified self-evaluation), developed as a closed-form misspecified-Bayesian model + a pre-registered 720-call six-cell experiment whose load-bearing result is a **reinforcement-cell falsification** of additive separability (Δ(+,+)=+0.15 vs predicted +2.51, power ≈ 0.92).

Reads **mostly clean**, with one real reader-facing defect:

- **Title — GOOD.** "Within-Session vs. Fresh-Session LLM Evaluation: An Architectural Characterization Under Misspecified Self-Evaluation." Plain-language, no acronym wall. Clears the `75e5c9e` bar (run predates it).
- **Abstract — prose but notation-heavy.** Communicates the result in prose, but the back half is a symbol run: "the gap signed by βμ_E with non-monotone (inverted-U) dependence on … α, the additively decomposed bias threshold β²_*, and the three-region welfare partition over (β², κ) … Δ(+,+) ≈ +2.5 … power ≈ 0.92." → **closed-on-arrival** (run shipped 2026-05-03, predates `75e5c9e`'s polish-prose >100-word + notation flag; corroborates the recurring abstract-notation residual). Not filed.
- **Cross-refs — CLEAN.** 0 "??" in the rendered PDF, 0 undefined `\cite`. No #75/#81 defect. Author = "Anonymous Pipeline Author" (correct, not a placeholder).
- **Tables — legible.** Table 1 (twelve-cell matrix) reads fine; no clipping/overfull.
- **Figure — see B1 below.** Exactly **one** included figure (the *theory* partition, Fig 1, p16). The **headline empirical result has no figure.**

## Outcomes

### B1 (High, NEW) — venue/tier mismatch: `theory_llm` has no ML/LLM venue ladder + no seed-triage domain-fit check → paper mis-bucketed to `letters`

**The headline finding of this repo, and the run's own #1 pipeline recommendation.** The seed's topic (LLM-evaluator architecture) lives entirely outside the `finance` variant's journal tier-ladder (`top-3-fin → field → letters`; journals JF/JFE/RFS/JFQA/Economics Letters). The `--ext theory_llm` extension — whose entire purpose is LLM-experiment papers — **does not override `JOURNAL_LIST`, `TARGET_JOURNALS`, or the tier ladder** (confirmed: `extensions/theory_llm/` has zero journal/venue/tier strings; `setup.sh:175-182` sets the finance ladder unconditionally for the finance variant regardless of `--ext`). So an LLM-evaluation paper produced by `theory_llm` inherits a finance ladder with **no ML venue anywhere** (no TMLR, NeurIPS/EMNLP/NAACL Findings, JMLR).

Consequence, in the run's own words:
- *"the seed locked the pipeline into a domain mismatch from minute one … The variant ladder was exhausted under that mismatch."*
- *"Three referee rounds (rounds 1–3 at top-3-fin and field) burned on a journal-fit pretense the math could never satisfy … **This is the single biggest quality drag in the run** — three rounds of revision under journal-fit pressure that the seed could not satisfy."*
- *"TMLR … was named by the round-3 referees as a natural home and remains the strongest single candidate … the variant ladder did not include TMLR because the variant is finance-tiered; if the variant had been an ML-tiered ladder, the pipeline would have stopped one rung earlier."*

So the pipeline marched the finance ladder to `letters` and shipped, while the paper's actual best home (TMLR per the referees) was never on the ladder. This is a real **quality + cost** drag: 3 wasted referee rounds optimizing prose for a referee class that could never accept on journal-fit grounds, then a ship at a tier that is a *journal-fit verdict on a mis-bucketed variant, not a quality verdict on the paper*.

**Two complementary gaps, both confirmed OPEN in current template:**

1. **Structural (theory_llm has no ML venue ladder).** `theory_llm` should contribute ML/LLM venues to `JOURNAL_LIST` + the tier ladder (TMLR, NeurIPS/EMNLP/NAACL Findings, JMLR), so `finance --ext theory_llm` (and a future `ms` variant) route LLM-evaluation papers to their real home and the editor/scorer stop invoking finance journal-fit as the rejection grounds. Touches `setup.sh` (extension-conditional `JOURNAL_LIST`/`TIER_LADDER`/`TARGET_JOURNALS`), the scorer/referee tier vocab.
2. **Detection (seed-triage has no domain/variant-fit check).** `templates/shared/seed.md` reads the seed and develops it but **never compares the seed's topic domain against the variant's journal ladder** (confirmed: no `variant`/`domain`/`tier`/`fit` check in seed.md's triage steps). At seed-triage we already know the seed is LLM-evaluator architecture and the variant is finance-tiered. The run's recommendation: *"Compare the seed's domain to the variant's tier-ladder before committing. If they are misaligned, either flip the variant or escalate explicitly. This would have saved 3 referee rounds."*

**Generality.** Affects **every** `theory_llm` run, not just this seeded one: the LLM-paper-on-finance-ladder mis-bucketing is structural. The seed-triage check generalizes to any seed whose topic lives outside its variant's journals.

**Relationship to #20.** #20 proposes a *new* `--variant ms` (Management Science) for LLM-experiment-first papers. That is adjacent but does **not** close this gap: (a) it leaves the existing `finance --ext theory_llm` path mis-bucketed, and (b) MS/MSOM/OR/ISR are OM/IS journals, **not** TMLR/EMNLP — the ML venues the referees named as this paper's actual home. So this is a distinct issue: give the `theory_llm` *extension* an ML venue ladder + a seed-triage domain-fit check. Cross-reference #20.

→ **Disposition: DUPLICATE → corroborate #20** (operator steer 2026-06-09: the MS variant + broader journal support is the intended home for LLM-experiment papers; no new issue). Corroboration posted on #20 (issue-comment-4662645643) recording this as a 2nd motivating case + the two specifics #20 didn't cover (extension-level venue ladder for the existing `theory_llm` path; ML venues TMLR/EMNLP distinct from MS's OM/IS list) + the seed-triage domain-fit-check detection half.

### B2 (High) — #71 corroboration: a non-headline figure satisfies the gate while the headline result ships figureless (NEW 3rd sub-gap) + cluttered-legend legibility

The paper ships **one** included figure: the *theory* welfare partition (Fig 1, p16, `v4_parameter_free_partition.png`). The dropped-figure gate (`polish-consistency.md:24` item 10, fires only if **no** `\includegraphics` appears anywhere) is therefore **satisfied**. But the paper's **headline result** — the reinforcement-cell falsification, which the run's own `LESSONS_PAPER` calls *"probably the single most publishable thing in the paper"* — is presented as **numbers in prose + Table 1 only, with no figure**, even though `output/stage3b/figures/delta_per_cell.png` (a per-cell Δ plot, the natural headline visualization) **was produced upstream**.

This is a **new, 3rd sub-gap of #71**, distinct from the two on file:
- Sub-gap 1 (legibility): a figure is illegible.
- Sub-gap 2 (IA-only): the headline figure is in the Internet Appendix, body figureless.
- **Sub-gap 3 (this run): the body has a figure, but it's the *secondary* (theory) result; the *headline* (empirical) result is figureless although its figure was produced.** The gate's "≥1 `\includegraphics` exists" condition is satisfied by a non-headline figure, so it never fires. Same family as #71 (reader can't *see* the headline), new mechanism: the gate checks *figure-presence*, not *headline-result-is-figured*.

Proposed sharpening for #71: the headline-figure check should verify the included figure(s) correspond to the paper's **central/headline result**, not merely that *some* figure exists. General, conservative form: if a figure-producing stage emitted figures for the paper's *main-contribution* stage (here `stage3b` empirical) and **none of that stage's figures are `\includegraphics`'d** while a figure from a *different* stage is, flag for review — a non-headline figure must not silently satisfy the headline-figure requirement.

**Plus legibility corroboration (sub-gap 1):** Fig 1 carries **two dense, overlapping legend/annotation boxes** (top-left welfare-arm legend collides with the B0_hard marker annotation; bottom-right deployment-readout box is crowded small text). Lower-confidence than fef5's clean axis-title overlap, but corroborates the legend/label-collision class.

This is the **9th figureless-*headline* run** in the sweep (fe6, fef4, fe5, fe3, fe4, fef2, fe2, fec2, fef1 prior — though several of those were zero-figures; this is the **1st "wrong-figure-present" mechanism**, the strongest case that "≥1 figure" is the wrong gate condition).

→ **Propose: post #71 corroboration comment** (3rd sub-gap + legibility) (pending go-ahead).

### Closed-on-arrival / already-tracked (not filed)

- **Polish-agent file-write enforcement.** 3 of 7 polish-r1 agents printed reports inline instead of saving to disk (orchestrator recovered from transcript). → **ALREADY ADDRESSED** by the Stage-9 write-verification gate (`3fba5cf`, `stage_9.md` write-gate). Nth run to hit it pre-fix; not filed.
- **Abstract notation residual** → closed-on-arrival (predates `75e5c9e`), see holistic read.
- **Clean cross-refs / correct author** → no #75/#81 defect; reads clean.
- **Agent hangs** (puzzle-triager ~50min, theory-v4 mutate watchdog 600s) → infra/operational, out of scope.

### Note-only (no gate, or subjective)

- **Free-form scorer tier-recommendation adopted by paper-writer as a buried-lede restructure at v4** ("lead with Corollary 4.1" reorganized the paper around what the scorer thought was the headline rather than what the empirics support — a reframing-as-progress event; branch-manager caught most, some lingered into §1). Adjacent to **#78** (Gate-4 strategic-verdict operationalization) — the scorer-presentation-channel being adopted as a structural reframe. Light corroboration of #78's theme; not separately actionable.
- **"+2.51 vs +2.5" over-armored abstract footnote** lived 2 rounds before polish-prose r2 removed it — polish-prose over-armoring, caught as designed. Note-only.
- **Mechanism-referee MISATTRIBUTED (r3) took 2 rounds to discharge** (relabel "characterize architectural choice" → "characterize the additive envelope + document its falsification"). Working-as-intended; the bar is correct. Note-only.

## Proposed backlog (pending operator go-ahead — outward-facing writes)

| ID | Pri | Disposition | Action |
|----|-----|-------------|--------|
| B1 | High | DUPLICATE → #20 | **Corroborated #20** (not filed; operator steer): `theory_llm` mis-buckets LLM papers to the finance ladder. Recorded as 2nd motivating case + extension-level venue ladder + ML venues (TMLR/EMNLP) + seed-triage domain-fit check. |
| B2 | High | OPEN (#71 family) | **Corroborate #71**: 3rd sub-gap (non-headline figure satisfies the gate while the headline result is figureless) + cluttered-legend legibility. |
| — | — | #78 | Light corroboration optional (scorer-recommendation-as-restructure); operator discretion. |
