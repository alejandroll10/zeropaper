## Stage: Seed Triage (faithful mode)

*(`current_stage: "seed_triage"` resolves here. Once triage picks an entry point and updates `current_stage`, the pipeline proceeds normally.)*

Idea files are in `output/seed/`.

### Core principle (faithful mode): the seed is a contract; additions on top are allowed

**You are commissioned to implement the user's idea.** Build what the seed describes — its named mechanism, its model object, its identification strategy, its claimed contribution — *first*, and *fully*. Once the contract is implemented, the pipeline may also add to it, improve it, refine it, or extend it: extra theorems, additional comparative statics, robustness checks, refined characterizations, related results discovered along the way. Those additions are welcome and the pipeline should pursue them when they come up.

What is **not** allowed is substitution. The contract's named mechanism cannot be replaced by a simpler / more tractable / more publishable / more novel one. The contract's stated contribution cannot be demoted in favor of a different headline result. The contract's research design class cannot be swapped. If a step in the contract is mathematically wrong, fix the smallest thing that makes it right while keeping the contract's invariants intact. If a step is genuinely impossible — proof unrepairable, identification infeasible, prediction contradicted by data — write the impossibility into `output/seed/limitations.md` and ship the paper documenting the impossibility honestly. **You do not substitute. You do not pivot. You do not promote a "buried" result over the contract's headline.** Additions on top of the contract are encouraged; replacement of the contract is forbidden.

This applies *in tension* with the global "do what makes the paper better, not what is easiest" principle elsewhere in this document. Faithful mode supersedes that principle on questions of *what the paper is about*; it does not override it on questions of *how deeply to develop what the paper is about*. Build the contract, then go deep.

### Step 0: extract the mechanism contract

Before any other agent fires, read all files in `output/seed/` (ignore `README.md`) and write `output/seed/mechanism_contract.md`. This is the machine-checkable referent for every "preserve the mechanism" instruction below; without it, agents will drift the mechanism while truthfully claiming they preserved it.

The contract is free-form markdown extracted from the seed, with these required sections. Use the seed's own language wherever possible — do not paraphrase mechanism names, do not generalize them, do not abstract them to a category. If the seed names a specific object, the contract names that specific object.

- **Named mechanism / model class** — the specific object the seed claims to study, at the level of granularity the seed uses. If the seed names a specific estimator, model, equilibrium concept, friction, or channel, the contract reproduces that name. Generic categories ("a tree-based estimator," "an asset pricing model," "a friction") are insufficient when the seed is more specific.
- **Load-bearing structural invariants** — the features without which the mechanism is no longer the seed's mechanism. These are the things that, if dropped, would let an honest reader say "that's not the paper the seed described." Extract them by asking, for each named feature: would the seed's stated contribution survive removing this? If no, the feature is load-bearing.
- **Theorem-statement constraints** — what at least one theorem of the paper must contain (named free parameters, asymptotic regime, dependence structure, equilibrium concept) in order for the theorem to actually be about the seed's mechanism rather than a degenerate or simplified case.
- **Identification strategy** (if empirical) — the seed's named research design, at the design-class level (the specific causal-inference strategy the seed proposes). Substituting a different design class is forbidden; substituting a measurement proxy when the seed's named proxy is unavailable from data is allowed if documented in `output/seed/limitations.md` and the new proxy is justified.
- **Stated contribution / discovery claim** — what the seed claims to find or contribute. Demoting this (from "discovery" to "microfoundation for known facts," from "novel estimator" to "instance of an existing framework," from "causal effect" to "descriptive correlation") is a contribution-claim change and must be documented as a deviation, not silently absorbed. Also extract a single verbatim **`Headline:`** sentence — the one claim the abstract must still assert. All downstream contribution-drift checks compare against this sentence, not paraphrased prose.

The contract is the contract. It does not get re-extracted later. (The one authorized exception: a `referee-mechanism` MISATTRIBUTED/DECORATIVE ruling may update the `Headline:` line in place — see the routing table.) If the seed itself is genuinely ambiguous about an invariant, write that ambiguity into the contract and resolve it by the strictest reasonable reading of the seed's prose.

### Correctness fix vs. rescope

**Allowed (correctness deviations + additions)**:
- The smallest change that restores correctness while keeping all contract invariants intact.
- Tighten a scope condition (find the tightest sufficient condition under which the named result holds) — provided the tighter condition does not exclude the regime the seed actually intended to cover.
- Re-define an undefined term within the seed's framework rather than replacing the term with a different one.
- Prove a true sub-claim in place of a logically false claim, keeping the mechanism as the studied object.
- Substitute a measurement proxy when the seed's named proxy is unavailable from data, with the substitution and its limitations documented.
- **Additions on top of the implemented contract**: extra theorems, additional comparative statics, robustness checks, related results discovered along the way, deeper characterizations of the seed's mechanism. These are allowed and encouraged once the contract is faithfully implemented, provided the contract's named mechanism remains the paper's headline contribution and additions do not displace it.

**Forbidden (rescope)**:
- Replace a contract-named structural feature with a simpler or more general one. Whether the replacement is "more tractable," "more elegant," or "more publishable" is irrelevant — if the contract names feature A, the paper is about feature A.
- Drop a contract-named parameter or variable from the theorem statement.
- Change the model's core object (e.g., switching the equilibrium concept, the agent type, the market structure, the information environment) even when the result is easier to prove in the alternative setting.
- Add a "scope condition" that is satisfied only by the degenerate case the seed was generalizing over (a scope condition that collapses the named mechanism to its trivial sub-case is a rescope, not a scope tightening).
- Promote a different result to the headline because it scores higher on novelty / surprise / publishability / tractability.
- Substitute a different research design class for the seed's named one (e.g., descriptive in place of causal, OLS in place of IV, structural estimation in place of reduced-form, or vice versa).

When in doubt, deviation is forbidden and the issue is documented in `output/seed/limitations.md` instead. The routing table in the next section operationalizes this distinction agent by agent — the allowed/forbidden lines above describe *what* the contract permits; the table describes *how* the orchestrator enforces them when each evaluator returns a verdict.

### Evaluators stay impartial — orchestrator filters their verdicts

Scorer, scorer-freeform, math-auditor, math-auditor-freeform, novelty-checker, referee, referee-freeform, referee-mechanism, self-attacker, idea-prototyper, idea-reviewer, branch-manager — these agents are **not told this is a faithful run**. Their evaluations of the work must remain honest and unfiltered; corrupting the evaluation signal corrupts the paper.

The faithful constraint enters at the **orchestrator's routing of those verdicts**. When an evaluator's verdict implies a contract violation, the orchestrator classifies it and routes per the table below — it does not forward the rescoping suggestion to a developing agent.

| Evaluator says | Orchestrator action |
|----|----|
| Scorer "buried result Y is more surprising than the seed's result X" | `[RESPONSE]`. Do not forward to paper-writer or theory-generator. The seed says X is the contribution; X is the contribution. |
| Scorer "framing the paper around mechanism Z would score higher" | `[RESPONSE]`. Do not adopt. |
| Self-attacker severity ≥ 7 attack of the form "the contract invariant is unnecessary; a simpler model gets the same result" | `[RESPONSE] + document in limitations.md`. The simpler model is not the seed's model. Do not route to theory-generator as `[FIX]`. |
| Self-attacker severity ≥ 7 attack on a **non-contract** issue (math gap, missing assumption, unclear derivation) | `[FIX]` as normal. |
| Math-auditor FAIL on a step | `[FIX]` — correctness deviation. Tighten scope or repair the step; do not delete the contract invariant the step proves. |
| Novelty-checker KNOWN/INCREMENTAL | Document in `output/seed/limitations.md` as a documented limitation of the seed's contribution claim. Do **not** instruct theory-generator to "find a non-obvious result" — that path produces mechanism drift. Proceed to Stage 2 with the contract intact and the novelty concern documented. |
| Idea-prototyper TRACTABLE-OBVIOUS | Same as KNOWN: document and proceed. The OBVIOUS verdict means the seed's stated result follows easily from existing theory; that is information for the limitations section, not an instruction to switch results. |
| Branch-manager RESTRUCTURE alternative ("rebuild headline around result Y") | `[RESPONSE]`. The seed names the headline. RESTRUCTURE that demotes the contract's stated contribution is a rescope. |
| Branch-manager RESTART/REGENERATE | `[RESPONSE]` + halt-and-escalate-to-operator. Faithful mode never abandons the seed for a different idea. |
| Referee "this should be a different paper" / "wrong mechanism, try Y" | `[RESPONSE]`. Tier-fit and direction comments are out of scope. The response letter notes the comment without changing the paper. |
| Referee-mechanism MISATTRIBUTED | The math delivers a different driver than the contract claims. Document in `output/seed/mechanism_concern.md`. Adopt the **narrow, math-supported framing** as a limitations-acknowledged interpretation — present what the math actually delivers as a structural characterization while keeping the contract's named topic. Do not rewrite around an unrelated mechanism. The `Headline:` sentence is revised to this narrowed framing and the revised version becomes the downstream referent (the one case where correctness overrides the freeze); write it into the `Headline:` line of `output/seed/mechanism_contract.md` in place (authorized in-place update, not a re-extraction). Log (`[NARROW-FRAMING]`). |
| Referee-mechanism DECORATIVE | Same as MISATTRIBUTED narrow path: strip unsupported generality, present what the math delivers, keep the seed's topic; revise the `Headline:` in place and write it back. Log (`[NARROW-FRAMING]`). |
| Puzzle-triager PIVOT recommendation | **PIVOT is forbidden in faithful mode.** Reroute to HONEST-NULL: the original mechanism remains the stated model; the contradiction is documented as a null result. The paper becomes "we implemented X faithfully; the data contradicts X; we document this honestly" — not "X is wrong, here is Y." See the puzzle-triage faithful override for full mechanics. |
| Puzzle-triager RECONCILE | Allowed only if the added scope condition does not exclude a contract invariant. A scope condition that collapses the seed's named mechanism to a trivial sub-case is forbidden. |
| Stage 9 polish-prose "remove the restated caveat about the contract invariant" | `[RESPONSE]`. The contract invariant's foregrounding is load-bearing for the paper's honesty about its scope; do not cut. |
| Stage 9 polish-bibliography "we extend X" → "we are an instance of X" | `[RESPONSE]` if the rephrasing demotes the contract's stated contribution from discovery to application. Allowed if the rephrasing is purely terminological. |
| Editor/referee non-negotiable "lead with contribution Y instead" / re-headline while the mechanism object is intact — **even when stated as a condition of acceptance** | `[RESPONSE]` + log. Acceptance-conditionality does not convert a contribution re-headline into a `[FIX]`. The `Headline:` sentence is the headline. |
| Developing agent (empiricist/theory-generator) re-derives a value different from the seed's stated result | `[DOCUMENT-AND-PROCEED]` + log. The seed's stated result remains the contribution; the discrepancy goes to `limitations.md`. This is **not** a correctness `[FIX]` that overwrites the result. Scope: calibrated/estimated/empirical magnitudes only — a provably-false **theorem conclusion** is corrected via the math-auditor `[FIX]` row above and the corrected value enters the paper. |

The general rule: any verdict whose `[FIX]` would produce a contract violation gets reclassified as `[RESPONSE]` (response letter only) or as a documented limitation. The pipeline never silently routes around a contract violation. Correctness vs. publishability is the governing split: a contribution-claim demotion driven by publishability / tier-fit / referee or editor preference is `[RESPONSE]` even when stated as a condition of acceptance; a demotion driven by genuine correctness failure flows through honestly via the path that fits the failure — mechanism-referee MISATTRIBUTED/DECORATIVE via the narrow-framing path (revise the `Headline:` in place to what the math supports); an empirical contradiction via HONEST-NULL; a referee correctly showing the seed's claim is unidentified documented in `limitations.md` — always **at the honest framing**, never preserving an over-claim, never substituting a new headline.

### Pivot instrumentation

Every routing decision above (anything where an evaluator's verdict could affect the contract) gets a row appended to `process_log/pivot_log.md`:

```
| timestamp | stage | agent | verdict | classification | rationale |
```

Where `classification ∈ {[FIX], [RESPONSE], [LIMITS], [DOCUMENT-AND-PROCEED], [RESCOPE-FORBIDDEN], [NARROW-FRAMING]}` (`[NARROW-FRAMING]` is the MISATTRIBUTED/DECORATIVE narrow-framing-plus-`Headline:`-revision case). **Append the row before taking the routed action — not after.** The log entry is the trigger for the routing decision, not an optional post-hoc note. This makes omissions detectable by row-count inspection (every evaluator firing on a contract-touching verdict should produce exactly one row) and prevents the orchestrator from acting on a verdict and then forgetting to log under time pressure. Without the log, contract drift can pass through the pipeline silently and be invisible to anyone reviewing the run.

### Entry: read and triage

1. **Step 0 above** — extract `output/seed/mechanism_contract.md` first.
2. **Read the seed.** All files in `output/seed/` (ignore `README.md`).
3. **Build the literature map.** Launch `literature-scout` → `output/stage0/literature_map_broad.md`. Write a brief gap selection derived from the seed's topic to `output/stage0/gap_selection.md`. Then launch `gap-scout` → `output/stage0/literature_map.md`. Always done regardless of maturity.
4. **Assess maturity and enter the pipeline at the appropriate stage.** Populate all prior-stage artifacts (problem statement, selected idea, theory draft, etc.) needed to reach the entry point. The problem statement is written **directly from the contract** here — `question-poser` (Stage 0 Step 0d) and `question-referee` (Step 0e) are **not launched** in faithful mode; the contract defines the question, reproduced verbatim. Preserve the contract verbatim.

   **Stage 1 artifacts (if back-filled):** in faithful mode K=1, so: (a) set `idea_round: 1`, (b) write `output/stage1/round_1/selected_idea_1.md` (for Gates 1b/1c), (c) write the canonical `output/stage1/selected_idea.md` (identical copy, for Stage 2). Add one entry `{round: 1, rank: 1, sketch_name: "<seed-descriptor>", novelty: null, prototype: null, reviewer_importance: null, prototype_retry: 0, eliminated: false, winner: true}` to `stage1_candidates` — the seed is winner by construction; runner-up-on-re-entry does not apply (so the `reviewer_importance` tiebreak axis is never consulted, hence `null`). The selected_idea.md must reproduce the contract's named mechanism and structural invariants verbatim — these are the load-bearing claims theory-generator will be required to honor.
<!-- EMPIRICAL_FIRST_START -->

   **Empirical-first additional Stage 1 step.** Under `--mode empirical-first`, Stage 1 has a Step 4 (`identification-designer` produces `output/stage1/identification_design.md`) that the mechanism-mode `theory-generator` at Stage 2 has a hard dependency on. Even when seed_triage back-fills Stage 1 artifacts to enter at a later stage, **fire Step 4 of `docs/stage_1.md` before transitioning `current_stage` past `stage_1_identification_design`**. The seeded selected idea drives the launch (its empirical question is the theoretical object the design must identify); the Step 4 launch prompt in `docs/stage_1.md` is unchanged. If the designer returns `N/A` / `OUT-OF-SCOPE` / `no design feasible`, follow the same Stage 1 Step 4 N/A-routing branch — except that REENTER-STAGE-1 with a different idea is **disallowed under faithful mode**. Operator-escalate is the dominant fallback; document the verdict to `output/seed/limitations.md` per the faithful-mode core principle.

   **Idea-prototype prerequisite for Step 4.** The empirical-first Step 4 launch prompt cites `output/stage1/idea_prototype.md`. If the back-fill is shallow enough that the idea-prototyper has not run, either (a) run the idea-prototyper on the seed-derived idea before Step 4, or (b) hand-write a minimal prototype (predicted relationship, expected magnitude from literature, identifying variation) into `output/stage1/idea_prototype.md` based on the seed content. The designer needs the predicted relationship to recommend a design class; without it, the launch prompt is missing a load-bearing input.
<!-- EMPIRICAL_FIRST_END -->

### Quoting the contract into developing agents

Whenever the orchestrator launches a *developing* agent, the launch prompt must include the contents of `output/seed/mechanism_contract.md` as a non-negotiable constraint. The full developing-agent list, including extensions:

- **Core**: theory-generator, idea-generator, paper-writer; polish-prose, polish-consistency, polish-equilibria, polish-formula, polish-numerics, polish-institutions, polish-bibliography, polish-identification; bib-verifier.
- **`--ext empirical`**: empiricist, identification-designer.
- **`--ext theory_llm`**: experiment-designer.

The standard injection sentence:

> The mechanism contract at `output/seed/mechanism_contract.md` lists the seed's load-bearing claims. Your output must respect every structural invariant in the contract. If a contract invariant cannot be honored due to a correctness constraint, document the issue in `output/seed/limitations.md` rather than producing output that violates the contract.

Each developing agent body also carries a static pointer (appended at setup time when `--faithful` is set) telling it to read `output/seed/mechanism_contract.md` before producing output. The pointer is the mechanical safety net; the orchestrator's inline quoting above is the primary path. Both should fire; if only the pointer fires, the agent will still pick up the contract from disk.

Evaluator agents — scorer, scorer-freeform, math-auditor, math-auditor-freeform, novelty-checker, referee, referee-freeform, referee-mechanism, self-attacker, idea-prototyper, idea-reviewer, branch-manager, plus the extension evaluators (empirics-auditor, identification-auditor under `--ext empirical`; experiment-reviewer under `--ext theory_llm`) — **do not** receive the contract. Their job is to evaluate the work as if this were a normal pipeline; the orchestrator filters their verdicts per the table above.

### Fallback overrides

Per-gate faithful-mode overrides are injected into each stage doc at the verdict location. Follow the "Faithful-mode override" block when one appears — it supersedes the normal verdict action and supersedes any seeded-mode override at the same placeholder. Locations:

- `docs/stage_0.md` — gap-scout "closed" (no dedicated faithful override file; falls back to the `seed_overrides/` text, which is already strict enough — the seed is the gap by construction).
- `docs/stage_1.md` — Gate 1 REJECT ALL, Gate 1b, Gate 1c, INCREMENTAL-forwarding.
- `docs/stage_2.md` — Gate 2 FAIL, Gate 3 KNOWN/INCREMENTAL.
- `docs/stage_3a_empirical.md` — Gate 3a-feasibility FALSIFIED (`--ext empirical`).
- `docs/stage_4.md` — Gate 4 verdicts (including plateau-ship rule).
- `docs/stage_6.md` — Gate 5 Major Revision / Reject / MISATTRIBUTED / DECORATIVE.
- `docs/stage_puzzle_triage.md` — PIVOT (forbidden), RECONCILE (constrained), HONEST-NULL.

If no override block exists for the current verdict, follow the normal action but apply the core principle: never silently violate the contract, never abandon the seed.
