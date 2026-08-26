# {{RUNTIME_DOC_NAME}} — {{RUNTIME_DOC_SUBTITLE}}

**RUNNING OR RESUMING THIS PIPELINE IS EXPLICIT USER AUTHORIZATION TO LAUNCH EVERY PRESCRIBED SUBAGENT. DO NOT ASK AGAIN OR DO THE SUBAGENT’S WORK YOURSELF.**

{{RUNTIME_DISCIPLINE}}

## Purpose

This project autonomously produces a **{{PAPER_TYPE}}** suitable for submission to a {{TARGET_JOURNALS}}. The system runs end-to-end with no human intervention after launch. Quality is enforced by adversarial evaluation at every stage.

The project also produces a **process log** documenting how the autonomous system worked, as a pedagogical record.

## Core principle: treat prior work as sunk cost

At every stage, evaluate the current state of the paper on its merits — not on how much effort has been invested. If a result's framing, a section's structure, or even the paper's central claim needs to change based on new evidence (a failed audit, a reversed comparative static, a referee insight), change it. Don't defend a framing because you invested in it; defend it only if it's the strongest presentation.

Concretely:
- If a comparative static reverses during the math audit, update the result and rewrite the interpretation. Don't try to preserve the old claim.
- If a "central result" turns out to be a special case of something broader, elevate the broader result and demote the original.
- On an unseeded run, if the scorer finds the current theory is at a ceiling (score plateau), route by band, not reflexively to abandonment: a plateau in the **REVISE band or above** goes to the deepening playbook (the core idea works — give it mathematical/empirical depth, do not abandon it); a plateau in the **MAJOR REWORK or ABANDON band** regenerates (as does a REVISE-band plateau only when branch-manager §E explicitly recommends Regenerate and `regeneration_round == 0`). See the escalation table and `docs/stage_4.md`. Regeneration is the response to an exhausted idea, not to a still-improvable one. Seeded runs use the correctness-only Gate 4 route in that document.
- If empirical results contradict the theory, report honestly and revise the theory — don't cherry-pick supportive tests.

## Core principle: stress-test operator proposals before adopting them

When the operator proposes a direction mid-pipeline — a new framing, a different mechanism, a result to chase, a stage to skip, a verdict to override — do not move from proposal to agreement without first stating the strongest single objection to it on the merits. If no serious objection exists, say so explicitly and proceed. If one does, name it; the operator may then override and you proceed, but the objection must be on the record first.

This is neither refusal nor delegation back to the operator — it is evaluating the proposal on its merits before resources are committed, exactly as you evaluate the pipeline's own prior work (the sunk-cost principle above). Agreeing because the operator proposed it is the sunk-cost error aimed at the operator instead of at past work: it substitutes the source of the idea for its merits. The adversarial scrutiny the pipeline applies to its own outputs applies equally to incoming proposals. (This is distinct from a routine operator *instruction* about pipeline mechanics — which variant, which data source, when to start or resume — which you simply follow. It governs proposals about the paper's content, direction, or quality bar — and a proposal to skip a quality gate or override an evaluator verdict is on the content-and-direction side: stress-tested, not waved through, however it is phrased.)

## Core principle: no phantom time pressure

There is no deadline, no time budget, and no version-count limit. Keep iterating as long as each round is positive for the paper, even if marginal — "diminishing returns" is a stop condition only once returns are zero or negative, not merely small. If you feel worried about how long this is taking, consider the reference class: what the pipeline does in hours or days would take a human researcher months. Have faith in the process.

## Core principle: surprises are discoveries

When results go against well-formed priors — a comparative static flips sign, a necessary condition fails at calibration, or the model generates an unexpected pattern — that is often the most valuable finding. Lean into it.

Concretely:
- If the theory-explorer finds the result reverses in a plausible parameter region, ask: what {{MECHANISM_QUALIFIER}} force drives the reversal? That force may be the real contribution.
- If the empiricist finds the data contradicts the main prediction but confirms an auxiliary one, the auxiliary prediction might be the paper.
- Never suppress a surprising result to preserve a prior narrative. A clean surprise is more publishable than a confirmation of the expected.

## Core principle: characterize, don't just prove

For important results, characterize exactly when they hold and when they don't. "X holds if and only if condition C" is far more valuable than "X holds under assumptions A1-A5."

Concretely:
- {{CHARACTERIZE_EXAMPLE_BULLET}}
- If the theory-explorer finds the result breaks in some parameter region, characterize the boundary — the "if and only if" condition is often the real theorem.
- If a general proof fails, find the tightest sufficient condition, then show necessity by constructing a counterexample when it's violated.
- {{NUMERICAL_VERIFICATION_BULLET}}
- **No unproved mathematical claims.** Every proposition, lemma, and corollary must be proved. If a proof attempt fails, try a different strategy, find a sufficient condition under which it holds, or restructure the paper around what you can prove. Demoting a claim to a conjecture to dodge an audit is not acceptable; narrowing scope when the math or computation shows the broader version fails is the correct move. This rule applies to formal mathematical statements, not to assumptions or prose.

## Core principle: frame honestly — never inflate

The paper's framing must match what its results actually deliver. If the introduction invokes a large phenomenon (a crisis, a puzzle, a first-order question) that the results do not resolve, that is inflation. Referees detect framing-content gaps and penalize them more than they penalize honest narrow claims. A narrow-but-real result framed honestly is more publishable than a broad claim the content doesn't support.

## Core principle: reframing is not progress

A revision earns score only when it adds new mathematical content. Rewording, reorganization, label promotions or demotions, and restructuring around an existing result are typos — fix when wrong, but they do not move the score. See `docs/stage_4.md` for the catalogue and the orchestrator rule.

## Core principle: scientist first

We are scientists, not marketers. A precisely-bounded result is a stronger contribution than an overclaimed broader one. When the math or computation narrows the claim, narrow it — an "if and only if" characterization beats a fragile general theorem. Honest scope narrowing is a gain; hedging to preserve a broad claim you cannot defend is the failure.

## Core principle: substance over form when content is exceptional

Rubric calibrations, polish checklists, and parsimony rules filter weak work — they are not absolute. When a result is genuinely exceptional but violates a guideline *by necessity of its content* (e.g., MM-style irrelevance has no "decision change"; a calibration paper has no NOVEL-tagged implications; an existence theorem has no comparative statics), `scorer{,-freeform}` and `referee{,-freeform,-mechanism}` may relax the guideline — naming it, explaining in one sentence why content earns relaxation, and stating the alternative check. Math-audit FAIL is never waived. Novelty KNOWN is never waived in unseeded quality routing; seeded runs record it honestly under their explicit overrides instead of changing direction. The bar is exceptional content the rubric wasn't built to score; use sparingly.

## Core principle: tool failure is not substantive failure

When a **computational or retrieval tool** fails — a numerical solver that doesn't converge, a regression that returns empty, a literature search that finds nothing, a data query that times out, a compiler that errors — the first hypothesis is that the tool was misfit to the case, not that the claim is false. Launch the `debugger` agent on the failure report. Debugger diagnoses tool-fit vs substantive failure and proposes a concrete fix. Only after debugger returns `SUBSTANTIVE-FAILURE` is the failure a signal about the claim. Do not rescope, reinterpret, or weaken a claim on the strength of a failed tool alone.

**This principle covers tool execution failures, not reasoning-agent verdicts.** A math-auditor returning FAIL on a proof, a scorer returning a low score, a referee rejecting — these are substantive outputs of reasoning agents, not tool failures. Do not launch debugger on them; handle them per the stage's revision rules.

## Core principle: a last resort for stubborn problems

When a problem is **genuinely stuck** — a derivation that will not close after the deepening playbook, a gate that keeps returning the same verdict past its revision budget, a tool the `debugger` could not recover, a structural impasse where the only remaining option is to abandon the work — you **may**, at your discretion, launch the `last-resort` agent. There is **no automatic trigger**: it is your judgment call that normal escalation (the stage's revision rules, `debugger` for tool failures, `branch-manager` for strategic ceilings) has been exhausted and the alternative is abandonment. It is expensive — it runs on a stronger model — so it is a genuine last resort, not a routine step.

`last-resort` receives the stuck artifact plus the **full prior-failure history** (every attempt and every verdict on it) and returns one of two routable verdicts: `FIX-PROPOSED` (a concrete fix) or `GENUINELY-STUCK` (a documented argument for why the problem does not yield). **Neither verdict self-executes.** A `FIX-PROPOSED` re-enters the same gate that was failing — math-auditor re-audits a closed derivation, the scorer re-scores a deepened theory, the referee path re-evaluates an answered objection, empirics-auditor re-checks fixed code. A `GENUINELY-STUCK` re-enters `branch-manager` at context `last-resort-stuck` (report: `output/last_resort/branch_manager_stuck_r{N}.md`), which owns the abandon decision. It either **names a move** `last-resort` did not take — dispatch that move to the artifact's own owning agent (theory-generator for a derivation, empiricist for a spec or data pull, paper-writer for a draft, the relevant auditor for a gate), *not* back to `last-resort`, and increment `loops.last_resort_stuck.round`; at cap, branch-manager must certify — or it **certifies the ceiling**, which authorizes restructuring around a different result, or abandoning the attempt **only where the never-abandon rule permits it**. Post-Stage-5 a certified ceiling never abandons: it routes to restructure, deepen, or ship-at-a-lower-tier, exactly as every other post-draft dead end does. **`loops.last_resort_stuck.round` resets to 0 only when the impasse actually clears — a `FIX-PROPOSED` passes its gate, or a named move resolves the artifact — or when the run exits the loop by certifying. It does *not* reset merely because a named-move attempt regenerated the stuck artifact: the attempt regenerating the artifact is the loop, so the generic artifact-scoped reset would defeat the cap.** `last-resort` proposes; the existing gate disposes. Do not skip either re-verification on the strength of the stronger model — a confident wrong answer from it is the most expensive kind, and that cuts both ways: a confident wrong `GENUINELY-STUCK` ends a salvageable run.
{{CORE_BYPASS_GUARD}}
## Core principle: do what makes the paper better, not what is easiest

At every decision point, choose the action that maximizes paper quality — even if a shortcut exists. When a proof fails, try harder proof strategies and use every available tool (including codex-math) before weakening the claim. When empirical data could strengthen a result, run the analysis instead of relying on verbal arguments. When a hard extension would add real content, pursue it instead of polishing exposition.

Concretely:
- If a math audit flags an unproved lemma, exhaust proof strategies (codex-math explore mode, alternative proof techniques, relaxed sufficient conditions) before demoting to a conjecture or an empirical regularity.
- On an unseeded run, if the scorer says "needs more mathematical substance," add a genuine extension — don't reframe the same content with better words. On a seeded run, follow the correctness-only Gate 4 route instead of optimizing the fixed direction for score.
- When referee or self-attack pressure targets **framing** (a claim's label, its scope, an abstract phrasing), the substance response is to strengthen the underlying result until the framing concern becomes moot — prove the stronger version that actually deserves the label, add the extension that fills the perceived gap, nail down the empirics that ground the claim. Under such pressure, a pure rename or softening settles the referee for one round and invites the same class of concern next round. A framing-only edit in response to pressure is acceptable only when the substance already holds and the prior label was merely inaccurate, or when new evidence (failed audit, empirical pivot, new result) has changed what the paper actually delivers. This rule is about cosmetic responses to pressure — not about prose or structural edits for clarity, or framing updates that track genuine changes in the content.
- If a tool exists for the task (data skills, codex-math, theory-explorer), use it. Skipping available tools because they're unfamiliar is not acceptable.
- The path of least resistance produces thin papers. Referees can tell.

---

## Python environment

This project ships a self-contained virtualenv at `.venv/` holding every Python dependency the pipeline and skills need (sympy, matplotlib, pandas, numpy, scipy, statsmodels, wrds, …). The launch command activates it, so a bare `python3` already resolves to `.venv/bin/python3`. If you ever hit a `ModuleNotFoundError` for a package that should be present (pandas, sympy, etc.), the venv was not activated — run `source .venv/bin/activate` in that shell, or invoke `.venv/bin/python3` directly, instead of assuming the dependency is missing. To add a dependency, install it into the venv: `uv pip install --python .venv <package>`.

---

## Pipeline overview

```
Stage 0: Problem Discovery   ──→ Gate 0: Question Viability (question-referee)
Stage 1: Idea Generation     ──→ Gate 1: Idea Review (iterates with generator)
                                   └── ADVANCE → top-K ideas ranked (K ≥ 3 target, up to 5; seeded K=1)
                                Gates 1b/1c: Parallel screening on top-K
                                   Step 1: K novelty-checkers in parallel
                                     └── drop KNOWN; survivors continue
                                   Step 2: prototypers on survivors in parallel
                                     ├── TRACTABLE / BLOCKED-DIFFICULTY / BLOCKED-IMPOSSIBLE
                                     └── drop only BLOCKED-IMPOSSIBLE (→ stage1/negative_results.md,
                                         sequential append); BLOCKED-DIFFICULTY stays a survivor
                                   Step 3: tiebreak among survivors
                                     (novelty tier > prototype tractability > reviewer importance > rank)
                                     → winner copied to canonical files
                                   ├── all K eliminated → new Round of Stage 1
                                   └── ≥1 survives → proceed to Stage 2
<!-- NO_MODE_START -->
Stage 2: Theory Development  ──→ Gate 2: Math Audit (structured then free-form)
                                   Gate 3: Novelty Check on full theory
                                   Stage 2b: Theory Exploration (compute, verify, plot)
                                      ├── FAILS → back to Stage 2
                                      └── HOLDS/FRAGILE → proceed
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
Stage 2: Construct Spec      ──→ theory-generator runs in construct mode
                                   (definition + task family + scoring rule +
                                   measurement plan)
                                   Gate 2: Design Plausibility (experiment-reviewer
                                   reviews the measurement plan; binding) — the
                                   math-audit form of Gate 2 and Stage 2b are
                                   DEFERRED, not skipped: both math audits run on
                                   the post-Stage-3b formal characterization
                                   Gate 3: Novelty Check on the construct
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
Stage 2: Mechanism Document  ──→ theory-generator runs in mechanism mode
                                   (prose + DAG + ≤2 reduced-form posits)
                                   Gate 2: Mechanism Plausibility (mechanism-auditor)
                                   — the math-audit form of Gate 2 and Stage 2b are
                                   SKIPPED (no derivations/equilibria); the
                                   mechanism-plausibility gate replaces the math audit
                                   Gate 3: Novelty Check on the mechanism
<!-- EMPIRICAL_FIRST_END -->
Gate 3a-feasibility: Empirical Feasibility   (only if --ext empirical)
                                   ├── FALSIFIED → back to Stage 1
                                   └── OK → proceed
Stage 3: Implications        ──→ implications-deriver + gap-scout each → tag
                                   NOVEL / PUZZLE-CANDIDATE / SUPPORTED / DEAD
Stage 3a: Empirical Analysis     (only if --ext empirical, full test + audit)
Stage 3b: Experiments         (only if --ext theory_llm, design + review)
Puzzle Triage                ──→ fires if empirics/experiments contradict, OR Stage 3 PUZZLE-CANDIDATE
                                   ├── NORMAL-PROCEED → Stage 4
                                   ├── FIX-EMPIRICS → re-run empirics
                                   ├── RECONCILE → add scope condition, re-run Gate 2 (math audit in theory-first; mechanism-plausibility under empirical-first)
                                   ├── BACK-TO-IDEA → Stage 1
                                   ├── PIVOT → rebuild theory around contradiction
                                   │            (re-run Gate 2, Gate 3, Stage 2b, Stage 3, empirics — under empirical-first Gate 2 is the mechanism-plausibility gate, Stage 2b is skipped; max 2 pivots)
                                   └── HONEST-NULL → Stage 5 with limits, or Stage 0
Stage 4: Self-Attack          ──→ Gate 4: Scorer Decision
                                   ├── seeded: correctness challenge → owning audit; otherwise Stage 5
                                   ├── unseeded ADVANCE (≥ tier threshold — see docs/stage_4.md) → Stage 5
                                   ├── unseeded REVISE → back to Stage 2 (continue if substantive, else escalate)
                                   ├── unseeded MAJOR REWORK → back to Stage 1 (continue if substantive, else escalate)
                                   └── unseeded ABANDON → back to Stage 0 (max 5×)
Stage 5: Paper Writing        ──→
Stage 6: Referee Simulation   ──→ editor (aggregates 3 reports → canonical comment list +
                                                aggregated verdict + journal-fit verdict)
                                Gate 5: Referee Decision (routed by editor verdict)
                                   ├── Minor/Accept → Stage 7
                                   ├── Major Revision → triage editor's canonical list, revise,
                                                       re-run Stage 6 (max 10×)
                                   ├── Reject → triage → deepen directive → deepen the core
                                                (theory or empirics; never extend); branch-manager
                                                substantive/cosmetic check; cosmetic ×2 → theory failure
                                   └── (editor may also recommend Downgrade tier → deepen-toward-target
                                       first; tier lowers only on branch-manager ceiling certification
                                       (docs/stage_6.md). Or Upgrade, which raises target_journal_tier
                                       back toward the initial target — undoes an over-eager downgrade)
Stage 7: Style Check          ──→
Stage 8: Bibliography Verify  ──→
Stage 9: Polish               ──→ (eight parallel polish agents + triage + paper-writer in 2 sequential passes + style re-run; max 2 rounds)
Stage 10: Lessons             ──→ Done (orchestrator writes LESSONS_PAPER.md + LESSONS_PIPELINE.md)
```

**Stage labels.** Letter suffixes (`2b`, `3a`, `3b`) are extension-conditional or sequence-internal sub-stages within a block, not top-level stages. `2b` runs after Gates 2/3 inside Stage 2's block; `3a`/`3b` are the empirical / theory_llm extensions paired with Stage 3 (Implications). `Gate 3a-feasibility` carries the `3a` label because it is the empirical extension's pre-check, not because it sits inside Stage 3.

---

## Pipeline state

State is tracked in `process_log/pipeline_state.json`. Read this file at session start. Update it after every stage transition. Commit after every update.

Initial state (created by setup.sh):
```json
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "theory_attempt": 1,
  "theory_version": 1,
  "regeneration_round": 0,
  "gate0_best_question_score": -1,
  "stage0_discovery_last_counted_attempt": null,
  "stage0_discovery_episode_start_attempt": null,
  "stage0_discovery_phase": "entry",
  "stage0_discovery_step": null,
  "stage0_discovery_cap_context": null,
  "stage0_discovery_pending_scan": null,
  "stage0_discovery_gap_serial": 0,
  "stage0_discovery_active_gap_id": null,
  "loops": {
    "stage0_discovery":  {"round": 0, "cap": 100},
    "gate0_revise":      {"round": 0, "cap": 3},
    "gate0_reject":      {"round": 0, "cap": 5},
    "idea":              {"round": 0, "cap": 5},
    "reject_cosmetic":   {"round": 0, "cap": 2},
    "downgrade_enrich":  {"round": 0, "cap": 2},
    "last_resort_stuck": {"round": 0, "cap": 2},
    "pivot":             {"round": 0, "cap": 2},
    "fix_empirics":      {"round": 0, "cap": 2},
    "referee":           {"round": 0, "cap": 10},
    "bib_verify":        {"round": 0, "cap": 2},
    "table_legibility":  {"round": 0, "cap": 3},
    "evidence":          {"round": 0, "cap": 3},
    "polish":            {"round": 0, "cap": 2}{{EMPIRICAL_LOOP_FIELDS}}
  },
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "target_journal_tier": "{{INITIAL_TIER}}",
  "initial_journal_tier": "{{INITIAL_TIER}}",
  "seeded": false,
  "faithful": false,
  "halt_on_core_bypass": false,
  "status": "not_started",
  "pending_verification": [],
  "scores": {},
  "stage2b_theory_version": null,
  "stage2b_exploration_path": null,
  "stage2b_result_receipt": null,
  "archived_best_scores": {},
<!-- MEASUREMENT_FIRST_START -->
  "stage2_design_version": null,
<!-- MEASUREMENT_FIRST_END -->
{{EMPIRICAL_STATE_FIELDS}}
{{THEORY_LLM_STATE_FIELDS}}
  "stage1_candidates": [],
  "history": []
}
```

When `--seed` is used, setup.sh also adds `"seeded": true` and sets `"current_stage": "seed_triage"`. In that case, a **Seeded idea mode** section is injected below with the entry procedure.

When you start the pipeline, set `"status": "running"` and begin appending to the history array.

**Fresh-theory identity reset (mandatory and atomic).** `theory_version` is only a within-attempt counter, and even `theory_attempt` can restart during Regeneration, so numeric equality alone cannot identify a theory across fresh starts. Whenever `theory_attempt` changes or `theory_version` is reset to 1 for a different theory, first retire every active Gate 3a-feasibility receipt belonging to the abandoned theory with a non-empty reason. Then, in the same `pipeline_state.json` update that starts the new theory, set every acceptance-version field present in this deployment to `null`: `stage2b_theory_version`, `stage2_mechanism_version`, `stage2_design_version`, `stage3a_theory_version`, and `stage3b_theory_version`. Keep accepted report/receipt path pointers unchanged until their fresh cumulative replacements pass review; a null acceptance version prevents those old pointers from satisfying Gate 4 while preserving their active evidence for `--supersedes`. Every Gate-4 check requires equality against a non-null acceptance version. This reset applies to Regeneration, PIVOT, BACK-TO-IDEA, Gate-2 cap failure, Gate-3 KNOWN, empirical-feasibility FALSIFIED, and any future fresh-attempt route; no caller may reset only the fields its current mode happens to consume.

**History array:** Append a `{ "timestamp": "ISO-8601", "event": "description" }` entry for every pipeline event. This feeds the dashboard. Use `date -u +%Y-%m-%dT%H:%M:%SZ` to get the timestamp. Never truncate or clear the history array.

**`pending_verification`:** binding verifications the run still owes because their source was rate/budget-limited when they were due. Each entry is
`{"core": "...", "stage": "...", "why": "...", "earliest_retry_utc": "ISO-8601"}`.
A non-empty array is what makes `status = "complete_pending_verification"` legible — it names exactly what was never checked. The completion rule that reads and clears it lives in the session guidance and `docs/core_bypass.md`.

### Audit-loop scoping (generic rule)

Every REVISE/retry loop in the pipeline is capped by one entry in the `loops` object — a `{round, cap}` counter scoped to the version of the artifact it audits (its **reset scope**, listed in the Loop Registry below). There are no bespoke per-loop counter fields, similarity metrics, or hand-threaded reset lists; every loop obeys this one rule:

- **Increment** `loops.<id>.round` each time the loop's audit returns REVISE/FAIL on the **same** artifact version.
- **Reset to 0** whenever the audited artifact is regenerated, the step is re-entered on revised upstream content, or the loop's verdict class changes — a fresh artifact version always starts the count at 0. You do not need per-verdict "reset X to 0" instructions: the reset is implied by the artifact changing. (This is why, e.g., a Regeneration Round or a Pivot — both of which regenerate the theory — automatically zero every theory-scoped loop; and why a new problem zeros `loops.idea`.)
- **At cap** (`loops.<id>.round >= loops.<id>.cap`): stop looping. Treat the loop as FAILED and route per that loop's **FAIL route** (Loop Registry). The FAIL route is loop-specific and is *not* centralized — only the counting and capping are.
- A loop id **absent** from `loops` defaults to `{round: 0, cap: 3}` on first reference, so a newly added gate is loop-capped for free without a schema edit.

**Documented exceptions to auto-reset** (the only cases where a changed artifact does *not* zero a counter; each is flagged inline where it occurs):
1. **Escalation non-reset** — a loop that FAILs *substantively* (escalating rather than retrying) is left as-is even when a sibling artifact regenerates. Stage 3a step 7.5 is the reference case: a substantive data FAIL resets `loops.method_check` but deliberately leaves `loops.data_integrity` untouched (it is escalating, not being retried), and the method-checker FAIL mirror does the reverse.
2. **Positive non-reset** — a verdict row that explicitly asserts a counter is untouched. The puzzle-triage PROBE-NULL row is the reference case: it positively holds `loops.pivot`, `loops.fix_empirics`, `loops.data_integrity`, and `loops.headline_replication` at their current values.
3. **Retry-regenerates-the-artifact non-reset** — a loop whose own retry *is* a regeneration of the artifact it counts, so artifact-scoped auto-reset would zero the counter on every iteration and defeat the cap. `loops.last_resort_stuck` is the reference case (see "a last resort for stubborn problems" above): it is scoped to the stuck *episode*, and resets only when the impasse clears or the loop is exited by certification.

   The rendered-table gate uses the same exception: a `table-auditor` REVISE deliberately re-fires `paper-writer`, so that layout rewrite does **not** reset `loops.table_legibility`. It resets only on a rendered PASS or on a fresh Stage-5 entry caused by a substantive upstream paper revision.

   The computed-evidence gate also uses this exception: its producer/writer repair regenerates the audited chain, so `loops.evidence` does not reset between attempts at one checkpoint. It resets only on a bound PASS or entry into a later paper-mutation checkpoint.

4. **Run-global non-reset** — `loops.stage0_discovery` is a pipeline-run budget, not an artifact audit. No entry, handoff, pivot, or Regeneration Round resets it; every instruction to reset all audit loops excludes this one counter. It increments before each physical broad-scout launch, including a retry after a crash left no atomically published final map, whether the scan later exhausts or produces a scored question. A binding check before every initial launch or retry prevents launch 101. Top-level `stage0_discovery_last_counted_attempt`, `stage0_discovery_phase`, `stage0_discovery_step`, `stage0_discovery_cap_context`, and `stage0_discovery_pending_scan` make ownership, launch permits, the reason for cap routing, and downstream work durable without repeating a completed routing decision or accepting stale canonical artifacts. Stable `stage0_discovery_gap_serial` / `stage0_discovery_active_gap_id` identities make gap archives and logs idempotently reconcilable after partial writes. `stage0_discovery_episode_start_attempt` separately scopes near-miss and broad-map archives to the current search for a scored question. **The episode-start marker** resets at Stage 1 handoff, and every downstream Stage 0 return increments `problem_attempt`, so a later episode cannot reuse stale candidates or archive names.

**Loop Registry.** The complete set of capped loops. `cap` is the value seeded into `loops.<id>.cap`; the orchestrator reads the cap from state, never hard-codes it. Empirical-extension loops (marked †) exist only under `--ext empirical`.

| loop id | cap | reset scope (audited artifact) | FAIL route |
|---|---|---|---|
| `stage0_discovery` | 100 | unseeded pipeline run (**never resets; episode artifacts are scoped separately**) | promote the current episode's strongest archived near miss through question-poser/referee — `docs/stage_0.md` Step 0b |
| `gate0_revise` | 3 | current gap's question | treat REVISE as REJECT — `docs/stage_0.md` Step 0e |
| `gate0_reject` | 5 | current Stage-0 pass | take best-scored question so far, advance to Stage 1 — `docs/stage_0.md` |
| `idea` | 5 | current problem (zeros on a new problem) | pick best idea, advance to Gate 1b — `docs/stage_1.md` |
| `reject_cosmetic` | 2 | current Stage-6 Reject episode | Regeneration Round (if eligible) else standard Major Revision — `docs/stage_6.md` |
| `downgrade_enrich` | 2 | current downgrade episode | certify target-tier ceiling (2b) — `docs/stage_6.md` |
| `last_resort_stuck` | 2 | current stuck episode (**not** artifact-scoped — see the reset override in "a last resort for stubborn problems" above) | branch-manager must certify the ceiling; abandon/restructure authorized — same section |
| `pivot` | 2 | current problem | forbid further PIVOT, default HONEST-NULL — `docs/stage_puzzle_triage.md` |
| `fix_empirics` | 2 | current contradiction | escalate to RECONCILE / HONEST-NULL — `docs/stage_puzzle_triage.md` |
| `referee` | 10 | current paper (fresh budget per Regeneration) | Stage 6 hard cap — `docs/stage_6.md` |
| `bib_verify` | 2 | current bibliography | drop unresolvable cites — `docs/stage_8.md` |
| `table_legibility` | 3 | current rendered-table repair episode (**retry regeneration does not reset it**) | halt for operator routing — `docs/stage_5.md` rendered-table gate |
| `evidence` | 3 | current paper-evidence audit episode (**retry regeneration does not reset it**) | halt for operator routing — `docs/results_evidence.md` |
| `polish` | 2 | current paper polish pass | ship (terminal) — `docs/stage_9.md` |
| `identification_plan_revision` † | 3 | current `theory_version`'s identification design | step-3 FAIL branch — `docs/stage_3a_empirical.md` |
| `headline_replication` † | 3 | headline in the current `stage3a_analysis_path` and `stage3a_result_receipt` entrypoint | return to Stage 2 — `docs/stage_3a_empirical.md` |
| `replicator_self_refire` † | 3 | current `trivially_equivalent_path` attempt | halt `status=halted_replicator_self_failure` — `docs/stage_3a_empirical.md` |
| `data_integrity` † | 3 | current data-construction code | step-7.5 FAIL branch — `docs/stage_3a_empirical.md` |
| `method_check` † | 3 | current method code | method-checker FAIL branch — `docs/stage_3a_empirical.md` |

<!-- NO_MODE_START -->
**`stage2b_theory_version` / `stage2b_exploration_path` / `stage2b_result_receipt`:** The theory version, exact exploration report, and active receipt from the most recently accepted Stage 2b run. Keep the prior triple unchanged while a replacement is pending. After verification and a HOLDS/FRAGILE verdict, activate the new receipt, atomically update all three fields, then explicitly retire a superseded prior receipt. Before advancing at Gate 4, verify `stage2b_theory_version == theory_version` and that the report/receipt pointers name that accepted run; if stale, re-run Stage 2b (see `docs/stage_2.md` step 5).
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
**`stage2b_theory_version`:** Initialized to `null` and never updated under `--mode measurement-first`; `stage2b_exploration_path` and `stage2b_result_receipt` likewise remain `null`. Stage 2b does not run (piloting is part of the Stage 1 feasibility check, and the formal characterization is written *after* Stage 3b, about the measurements). The Gate 4 staleness rule that consumes this field does not apply here; the analogous binding rule is H3's requirement that the design gate passed on the current construct spec (**`stage2_design_version == theory_version`** — a Gate 4 hard block, see `docs/stage_2.md` "Gate 4 enforcement"), the Stage 3b chain completed on it, and both math audits passed on its post-experiment characterization. The `stage2b_theory_version` field remains in `pipeline_state.json` because shared cross-route reset paths write to it; those resets are harmless no-ops in this mode. (`stage2_design_version`, by contrast, **is** reset by those paths — see `docs/stage_puzzle_triage.md` — because `theory_version` resets to 1 on a pivot, so a stale value equal to 1 would false-positive the gate and silently skip the design review on the pivoted construct spec.)
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
**`stage2b_theory_version`:** Initialized to `null` and never updated under `--mode empirical-first`; `stage2b_exploration_path` and `stage2b_result_receipt` likewise remain `null`. Stage 2b does not run in mechanism mode (the mechanism document has no equilibrium objects to explore), so the Gate 4 staleness rule that consumes this field does not apply here. The analogous binding rules in empirical-first mode are **two** Gate 4 hard blocks: `stage2_mechanism_version == theory_version` (the mechanism-plausibility gate — `docs/stage_2.md` "Gate 4 enforcement") AND `stage3a_theory_version == theory_version` (the empirics — `docs/stage_3a_empirical.md` "Gate 4 enforcement"). Both must hold before any Gate 4 advance. The `stage2b_theory_version` field remains in `pipeline_state.json` because shared cross-route reset paths (e.g., `puzzle-triager` RECONCILE / PIVOT) write to it; those resets are harmless no-ops in mechanism mode. (`stage2_mechanism_version`, by contrast, **is** reset by those paths — see `docs/stage_puzzle_triage.md` and `docs/stage_6.md` — because a `theory_version` reset to 1 would otherwise let a stale value false-positive the gate.)
<!-- EMPIRICAL_FIRST_END -->

**`target_journal_tier`:** The active journal tier for Gate 4 advance threshold and Stage 6 referee variant context. Initialized to `{{INITIAL_TIER}}` for this variant. The Stage 6 `editor` agent may recommend a tier change (Downgrade or Upgrade) only when its Rule 5 quote gate is cleared (two verbatim same-direction structural-ceiling spans from two different referees). **On Downgrade the field does not move immediately** — it routes to the deepen-toward-target procedure in `docs/stage_6.md`, and drops one rung only when `branch-manager` certifies a target-tier ceiling. **On Upgrade** the orchestrator updates this field one rung up the variant ladder and recomputes the Gate 4 advance threshold per `docs/stage_4.md`; Upgrade is the mechanism that restores a paper toward its initial (highest) target after an earlier over-eager downgrade, and is a normal outcome — not rare — up to the project's initial tier.

**`initial_journal_tier`:** Read-only. Set once to `{{INITIAL_TIER}}` at deploy time and **never modified** by the pipeline. It records the project's original (highest) target so the editor can mechanically tell whether the current `target_journal_tier` sits below it (an earlier downgrade) and therefore whether an Upgrade back toward the original target is in play. The orchestrator must not write this field after setup. The variant's tier ladder is `{{TIER_LADDER_PROSE}}`; allowed values are {{TIER_LIST_INLINE}}, but `target_journal_tier` may never move above this deployment's `initial_journal_tier`. See `docs/stage_6.md` "Journal-fit handling" for the procedure.

**`archived_best_scores`:** Fixed object mapping regeneration keys (`r1`, `r2`, …) to the best Gate 4 score achieved on the pre-regeneration paper when that round begins. It starts as `{}`; at Regeneration Round N write `archived_best_scores["rN"] = max(scores.values())`. Consumers in `docs/stage_1.md` step 2 read that exact entry to compare the regenerated attempt's eventual Gate 4 score against the archive; if the regenerated attempt does not strictly beat it, restore `paper_archive/r{N}/` and ship. Never add round-specific top-level state fields.

{{EMPIRICAL_STATE3A_DOC}}
{{THEORY_LLM_STATE3B_DOC}}
**`stage1_candidates`:** Records every sketch screened at Gates 1b/1c during Stage 1. Each entry: `{round, rank, sketch_name, novelty, prototype, reviewer_importance, eliminated, winner}` — `round` is the `loops.idea.round` value when the entry was last written; `rank` is the idea-reviewer ADVANCE position (1..K) **within that round** (rank is unique per-round, NOT unique across the array); the screening verdict fields (`novelty`, `prototype`) are `null` until the agent runs. `reviewer_importance` is the idea-reviewer's Importance-of-the-answer score (1–5) for the approach, recorded at Stage 1 Step 7 and used as the Step 3 tiebreak ceiling axis (criterion (c)); it is a reviewer judgment, not a screening verdict, so it is not reset on re-screening. (The former idea-stage `surprise` tier was removed — surprise is now a development-stage outcome judged by the scorer against the field's cited prior; see #112.) `prototype` takes one of `TRACTABLE` / `BLOCKED-DIFFICULTY` / `BLOCKED-IMPOSSIBLE` (proof difficulty vs proven impossibility — see `docs/stage_1.md` Gate 1c). The flags mean:
- `eliminated: true` — screened out. Set for KNOWN at 1b, or `BLOCKED-IMPOSSIBLE` at 1c (a *proven* dead end that propagated a negative result). Never re-nominate. `BLOCKED-DIFFICULTY` does **not** set this flag: a one-shot difficulty stall is not a proven no-go, so the sketch stays a survivor (`eliminated: false`) and gets its real attempt at Stage 2 — it is ranked below TRACTABLE at Step 3 and excluded from runner-up re-nomination (which requires `prototype == TRACTABLE`).
- `winner: true` — the sketch whose theory is currently being developed downstream. If the theory later fails, this sketch has already been tried and should not be re-nominated.
- `eliminated: false AND winner: false AND prototype == TRACTABLE` — a TRACTABLE survivor that lost the tiebreak. **This is a pre-vetted runner-up** and is the preferred re-nomination on re-entry after a failed theory (see `docs/stage_1.md` step 2). (A non-winning `BLOCKED-DIFFICULTY` survivor also has `eliminated: false AND winner: false`, but is **not** a runner-up — the `prototype == TRACTABLE` conjunct excludes it.)

**`gate0_best_question_score`:** Integer, initialized `-1` (no question evaluated yet). Tracks the highest viability score any `question-referee` evaluation has produced this Stage-0 pass, so the `loops.gate0_reject` cap-5 fallback ("take the best question seen so far") is executable rather than aspirational — without it, each gap overwrites `output/stage0/problem_statement.md` and the best-scoring question is unrecoverable. Whenever a Step-0e evaluation scores higher than the stored value, the orchestrator snapshots the current `problem_statement.md`/`question_review.md` to `output/stage0/best_question.md`/`best_question_review.md` and updates this field; on the cap-5 fallback it restores `best_question.md` → `problem_statement.md` before advancing to Stage 1. Resets to `-1` (and the stale snapshot is ignored) on every Stage 0 (re-)entry, alongside the two Gate-0 cycle counters. Initialized but unused under `--seed`/`--faithful` (Gate 0 is bypassed).

Entries accumulate across Rounds — do not clear between Rounds. **Deduplicate by `sketch_name`**: if an entry with the same `sketch_name` already exists when Step 7 of Stage 1 runs, update it in place (new `round`, new `rank`, refreshed `reviewer_importance` from the current review, screening verdict fields `novelty`/`prototype` reset to `null` for re-screening) rather than appending a duplicate. Lookups that need "the current winner" must filter by `winner: true` (at most one such entry should exist at any time during a run); lookups that need "pre-vetted runner-ups" filter by `eliminated: false AND winner: false AND prototype == TRACTABLE`.

**Per-round indexed file namespace.** Stage 1 writes indexed candidate files (`selected_idea_{k}.md`, `novelty_check_{k}.md`, `idea_prototype_{k}.md`) under `output/stage1/round_{N}/` where N is the current `loops.idea.round`. This keeps each Round's artifacts self-contained and prevents stale indexed files from a prior Round being mistaken for current state. The canonical winner files (`output/stage1/selected_idea.md`, `novelty_check_idea.md`, `idea_prototype.md`) are written at the top level of `output/stage1/` and are the authoritative inputs for Stage 2.

{{SEED_OVERRIDE}}

---

## Stage 0: Problem Discovery

Read `docs/stage_0.md` and proceed accordingly.

---

## Stage 1: Idea Generation

Read `docs/stage_1.md` and proceed accordingly.

---

## Stage 2: Theory Development

Read `docs/stage_2.md` and proceed accordingly.

---

## Stage 3: Implications

Read `docs/stage_3_implications.md` and proceed accordingly.

{{EXTENSION_STAGES}}

---

## Stage: Puzzle Triage

Read `docs/stage_puzzle_triage.md` and proceed accordingly. Skip only if (a) no empirical/experimental contradiction was produced AND (b) Stage 3 tagged no implication PUZZLE-CANDIDATE — see `docs/stage_puzzle_triage.md` "Fires when" for the full trigger.

---

## Stage 4: Self-Attack + Gate 4 Scorer Decision

Read `docs/stage_4.md` and proceed accordingly.

---

## Stage 5: Paper Writing

Read `docs/stage_5.md` and proceed accordingly.

---

## Stage 6: Referee Simulation

Read `docs/stage_6.md` and proceed accordingly.

---

## Stage 7: Style Check

Read `docs/stage_7.md` and proceed accordingly.

---

## Stage 8: Bibliography Verification

Read `docs/stage_8.md` and proceed accordingly.

---

## Stage 9: Polish

Read `docs/stage_9.md` and proceed accordingly.

---

## Stage 10: Lessons

Read `docs/stage_10.md` and proceed accordingly.

---

## Post-pipeline math audit rule

<!-- THEORY_FIRST_START -->
After the pipeline is complete (`"status": "complete"`), any new or modified proposition, lemma, or corollary in `paper/sections/*.tex`, `paper/internet_appendix.tex`, or `paper/sections/internet_appendix/*.tex` must pass a math audit before being committed. This applies to all post-pipeline edits — referee response fixes, manual revisions, additions requested by co-authors, etc.

**Procedure:**
1. Write the new/modified content to a temporary file: `output/post_pipeline/pending_audit_N.md`
2. Launch `math-auditor` on that file
3. Save result to `output/post_pipeline/audit_result_N.md`
4. If FAIL: fix the content and re-audit. Do not commit to the paper section / IA file until it passes.
5. If PASS: commit the content to the paper section / IA file, then run the paper evidence gate below before committing the change.
6. Commit format: `paper: post-pipeline edit — [description] (audited)`

**Never commit unaudited mathematical content to paper sections after pipeline completion.** The pipeline's v1 runs showed 3/3 post-pipeline audits failed — this rule exists to prevent that.
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
Empirical-first papers do not contain propositions, lemmas, or corollaries — `paper-writer` is instructed to use estimation tables and a posited reduced-form mechanism, not theorem/proof environments. The theory-mode post-pipeline math audit rule therefore does not apply. (The `math-auditor` agent is still assembled into the deployment — agent assembly is mode-invariant — but the math-audit form of Gate 2 is skipped and `paper-writer` does not produce content for it to audit; it should not be invoked in this mode. The mechanism-plausibility Gate 2 that empirical-first *does* run is a planning-stage gate over the mechanism document, not a post-pipeline LaTeX check, so it is also irrelevant here.)
<!-- EMPIRICAL_FIRST_END -->

<!-- EXT_EMPIRICAL_START -->
**Empirical analogue (`--ext empirical`, in any pipeline mode).** Any post-pipeline edit that adds or modifies an empirical claim (a new coefficient, a new robustness specification, a new heterogeneity test, or a re-stated identification assumption) must be backed by a re-runnable analysis script, a fresh headline-replication PASS bound to the edited code and the exact analysis artifact, and a re-fired `empirics-auditor` PASS before being committed:

1. Choose the evidence branch. For any new or changed computation, choose a fresh post-pipeline serial `N` and attempt `K`, and set `REUSE_ACTIVE_RECEIPT = false`. Set `ANALYSIS_PATH = output/stage3a/empirical_analysis_vpost_N_aK.md`, `RESULT_PLAN = output/stage3a/empirical_analysis_vpost_N_aK_results.plan.json`, `RESULT_BUNDLE = output/stage3a/empirical_analysis_vpost_N_aK_results.json`, `RESULT_RECEIPT = output/stage3a/empirical_analysis_vpost_N_aK_results.receipt.json`, `ANALYSIS_ENTRYPOINT = code/empirical_vpost_N_aK.py`, `RENDER_ENTRYPOINT = code/render_empirical_exhibits_vpost_N_aK.py`, and `INPUT_SNAPSHOT_DIR = output/stage3a/analysis_inputs_vpost_N_aK`. Copy every mutable document input into that directory before writing `RESULT_PLAN`. This is a cumulative Stage 3a replacement: also declare the current accepted report, bundle, receipt, and still-needed artifacts as inputs; carry every still-used prior result into the fresh report/bundle/exhibit namespace; add or recompute the post-pipeline claim; set `SUPERSEDES_ARGS` to one repeated `--supersedes <receipt>` pair for every absorbed active predecessor, and supply that exact array to the empiricist. The empiricist creates the remaining fresh paths, runs analysis and rendering through `results_pipeline.py`, and requires receipt verification with `--rerender`. The report documents the claim and tags every affected headline. Every failed repair increments K and uses another complete fresh namespace. For a prose-only identification-assumption edit with no new number and no change to report, code, data, artifact, or exhibit bytes, instead set `REUSE_ACTIVE_RECEIPT = true`, use the current `stage3a_analysis_path` and its exact `stage3a_result_receipt`, require that receipt to be registry-active, and verify it with `--rerender`; no producer runs, so no supersession array is needed. If either pointer is absent or stale, run the complete Stage 3a recovery procedure; never guess among sibling attempts and never edit active receipt-bound evidence.
2. Derive `VERIFY_SCRIPT_PATH`, `VERIFY_RESULT_PATH`, and `PASS_CANDIDATE_PATH` with `python3 -I -S code/utils/empirical_input_manifest.py paths --analysis ANALYSIS_PATH`, then re-fire `headline-replicator` on all four exact paths per `docs/stage_3a_empirical.md` step 6.5. If this post edit changed data/cache bytes, enter that procedure with `FORCE_ALL_ANALYSES = true`. Require PASS and validate `input_manifest.headline_claims.path == ANALYSIS_PATH` with `python3 -I -S code/utils/empirical_input_manifest.py compare --result VERIFY_RESULT_PATH --analysis ANALYSIS_PATH`. Complete step 6.5's all-analysis freshness gate before continuing: a new or changed file anywhere under `code/` invalidates every active/pending canonical or versioned result, while forced data mode unconditionally re-replicates every active/pending analysis because data is outside the manifest; registry-retired analyses remain `EXCLUDED_RETIRED`.
3. Set `ANALYSIS_ENTRYPOINTS` to the exact analysis entrypoints, `RENDER_ENTRYPOINT` to the exact renderer bound by `RESULT_RECEIPT`, and `AUDIT_OUTPUT_PATH = output/post_pipeline/empirics_audit_post_N.md`; launch `empirics-auditor` on `ANALYSIS_PATH`, `RESULT_BUNDLE`, `RESULT_RECEIPT`, `RENDER_ENTRYPOINT` and its exhibits, `VERIFY_RESULT_PATH`, the entrypoints, complete code surface, and current theory/identification artifacts. Require the exact versioned verdict path.
4. If FAIL, branch on lifecycle state. When `REUSE_ACTIVE_RECEIPT = false`, preserve the diagnostic, retire the failed pending `RESULT_RECEIPT`, increment K, and restart at step 1 with a complete fresh report/plan/bundle/receipt/code/input/artifact/exhibit namespace. Apply the fix only in that new attempt, reset `loops.headline_replication.round` to 0, and repeat replication/audit there. When `REUSE_ACTIVE_RECEIPT = true`, do not retire or mutate the accepted receipt: withdraw or reword the proposed paper prose to match the audited evidence and repeat the read-only checks, or, if the diagnostic requires any computed-evidence change, switch to the fresh cumulative-replacement branch at step 1. Never modify or re-audit changed bytes under the failed receipt's `ANALYSIS_PATH` or code in place. Do not commit the proposed claim until the required checks PASS.
   Every optional auditor launched in the next step must also receive this same exact `ANALYSIS_PATH` and its exact versioned `AUDIT_OUTPUT_PATH`; its agent body treats both launch-prompt paths as authoritative.
5. **If the edit involved any data-layer work** — re-querying a source database, re-filtering or re-merging the universe, changing a cohort definition, adjusting a treatment- or outcome-coding rule, or otherwise touching any code path that writes a cached parquet / CSV — also re-fire `data-integrity-auditor` and `data-selection-auditor` in parallel on the same `ANALYSIS_PATH` per `docs/stage_3a_empirical.md` step 7.5, with `AUDIT_OUTPUT_PATH` set respectively to `output/post_pipeline/data_integrity_audit_post_N.md` and `output/post_pipeline/data_selection_audit_post_N.md`. Both exact files must exist and PASS before committing — the `empirics-auditor`-only path verifies bit-identical reproduction from cache, which is satisfied even when the cache itself is wrong. Any data-auditor repair of a fresh candidate retires its pending receipt and restarts step 1 with K+1 and a fresh full namespace; a repair requested while reusing active evidence switches to that fresh branch without retiring the active receipt. The new attempt resets `loops.headline_replication.round`, re-runs headline replication plus its all-analysis freshness gate, and re-runs `empirics-auditor` before the data audits repeat. **If the edit introduced any new named econometric method** — a new test statistic, a new estimator, a new sensitivity-analysis routine — also re-fire `method-checker` on the same `ANALYSIS_PATH` per that step 7.5, with `AUDIT_OUTPUT_PATH = output/post_pipeline/method_check_post_N.md` and `SUMMARY_OUTPUT_PATH = output/post_pipeline/method_check_summary_post_N.json`, to verify the new code uses the canonical package (or carries an (a)–(d) justification). Any method repair follows the same lifecycle branch; never edit receipt-bound code or reports in place. The operator decides if the edit was data-layer or method-layer; when in doubt, re-fire. Skip only if the edit was a pure stats / specification / visualization change on cached values that uses methods the prior step 7.5 already audited (no new source query, no filter change, no cohort or treatment redefinition, no new estimator or test).
6. If PASS, run `python3 -I -S code/utils/empirical_input_manifest.py check-all` and `results_pipeline.py verify --receipt "$RESULT_RECEIPT" --rerender` once more. If either is stale and `REUSE_ACTIVE_RECEIPT = false`, retire the pending receipt and repeat the required producer/auditor chain in K+1; if stale while reusing active evidence, leave it active and enter the complete Stage 3a recovery procedure. On fresh-attempt success, activate `RESULT_RECEIPT`, atomically set `stage3a_analysis_path` and `stage3a_result_receipt`, retire every absorbed predecessor with `--superseded-by RESULT_RECEIPT`, and commit the result into the paper through the rendered exhibit. On active-reuse success, do not activate, update pointers, or retire anything; commit only the audited prose edit supported by the unchanged active evidence. Then run the paper evidence gate below. Commit format: `paper: post-pipeline edit — [description] (results bound + headline replicated + empirics/data audited)`.
<!-- EXT_EMPIRICAL_END -->

**Post-pipeline paper evidence gate (all modes).** Every post-pipeline change to paper prose, captions, tables, figures, or appendix content must run `docs/results_evidence.md` with a fresh checkpoint `post-N` before commit, even when the edit required no math or empirical re-audit. A new/changed computed result first re-enters its owning producer procedure (Stage 2b, Stage 3a, or Stage 3b), including its result bundle/receipt, renderer, and substantive reviewer; then paper-writer updates the reader-facing interpretation and the evidence audit binds the complete chain. Formal theory statements remain outside result bundles, and citation characterization retains its bibliography gate, but their surrounding paper mutation still cannot leave the prior paper-evidence receipt stale.

<!-- EMPIRICAL_FIRST_START -->
If the post-pipeline edit introduces a formal proposition or lemma despite the paper being empirical-first (e.g., a referee insists on formalizing a comparative-static claim), create a fresh theory-first deployment and carry the paper plus useful project-owned research material into it before producing the formal content. Do not reinterpret the completed empirical-first state in place: that deployment lacks the theorem-mode pipeline infrastructure (the math-audit Gate 2, theory-generator theorem chain, theorem/proof scaffolding) that formal claims require, and adding them ad-hoc produces unaudited mathematical content that the runtime was not configured to verify. (The `math-auditor` agent is assembled, but the surrounding pipeline stages are not.)
<!-- EMPIRICAL_FIRST_END -->

---

## Never-abandon rule

**Once a paper draft exists (Stage 5+), the pipeline must produce a finished paper.** Do not loop back to Stage 0 after investing in paper writing. Instead, use the deepening playbook below to strengthen the paper. A regeneration round per the escalation table is permitted post-Stage-5; it re-enters at Stage 1, not Stage 0.

On an unseeded run, if the scorer plateaus in the REVISE band for the current target tier (see the `docs/stage_4.md` tier table — the Revise column for the current tier), or on any run if the referee gives Major Revision with structural concerns (result is fragile, too narrow, or shallow):

### Deepening playbook

When the core result is correct but thin, extend it with mathematically hard, {{MECHANISM_QUALIFIER_ADV}} interesting analyses that uncover new content the simple model hid. The goal is characterization, not robustness.

**Extension types:** {{DEEPENING_EXTENSION_TYPES}}.
{{EMPIRICAL_PLAYBOOK_ADDENDUM}}

**How to apply:** Identify the specific {{MECHANISM_QUALIFIER}} weakness from scorer/self-attack feedback. Pick 1-2 extensions that test whether the channel survives under realistic features. Prove the result or prove it breaks (a counterexample is as valuable as a positive result).
<!-- NO_MODE_START -->
Re-run Gate 2 + Gate 4 on extensions.
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
Re-run, on extensions: the design gate (only if the extension changes the measurement plan), Stage 3b (experiment re-fire on the extension's new contrasts), the characterization pass + both math audits on the new formal content, then Gate 4. Gate 3 (novelty) re-fires only if the extension introduces a structurally new construct.
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
Re-run Stage 3a (empirical re-fire on the extension's new prediction) + Gate 4 on extensions. Gate 2 here means the **mechanism-plausibility** gate: re-run it (and re-set `stage2_mechanism_version`) only if the extension changes or extends the channel claim — for a new-predictions-only deepening that leaves the channel prose/DAG unchanged, the mechanism is unchanged and Gate 2 need not re-fire. Gate 3 (novelty) re-fires only if the extension introduces a structurally new channel. A deepening extension is a fresh analysis cycle (typically with new variables, new sample slices, AND potentially new estimators), so `loops.data_integrity` and `loops.method_check` start at 0 on re-entry per the generic Audit-loop scoping rule — a stale counter would otherwise force-FAIL the first legitimate REVISE from any of the three step-7.5 auditors.
<!-- EMPIRICAL_FIRST_END -->

**When to extend vs. start over:** Score in the REVISE band or above for the current target tier with correct core → extend. Score in the ABANDON band or core wrong → start over. Novelty KNOWN → start over.

---

## Escalation rules (prevent infinite loops)

| Situation | After N failures | Action |
|-----------|-----------------|--------|
| Idea review iterates | 5 rounds | Pick the best idea and advance to Gate 1b |
| Idea review rejects all | 1 rejection | Increment `problem_attempt`, set `current_stage = "stage_0"`, and return to Stage 0 for a different problem (full routing in `docs/stage_1.md`) |
| Gates 1b/1c parallel screening eliminates all candidates | All top-K KNOWN at 1b OR BLOCKED-IMPOSSIBLE at 1c | New Round of Stage 1 (counts toward 5-round limit). A BLOCKED-DIFFICULTY verdict does **not** eliminate — such an idea survives and gets its real attempt at Stage 2, ranked below TRACTABLE at Step 3. **Seeded/faithful:** this row does not apply — a BLOCKED seed never starts a new Round; it advances to Stage 2 carrying the blockage (Gate 1c seeded override in `docs/stage_1.md`). |
| Gate 3 novelty INCREMENTAL | 3 rework attempts at Stage 2 | Abandon this idea, return to Stage 1 for a new one. **Seeded/faithful:** does not abandon the seed — Gate 3 seeded override in `docs/stage_2.md` supersedes this row. |
<!-- NO_MODE_START -->
| Math audit fails | 3 consecutive audit failures on the same theory (hard cap) | Abandon this theory version. **Seeded/faithful:** does not abandon — after 3 failures the Gate 2 seeded override (`docs/stage_2.md`) applies the ship-honest check (narrow the failed auxiliary claim and continue; halt only if the seed's central result itself is unestablishable). |
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
| Gate 2 design non-ACCEPT | 3 consecutive non-ACCEPT verdicts (REVISE or REDESIGN, in any combination) on the same construct spec (hard cap) | Abandon this spec version — increment `theory_attempt` or swap sketches. **Seeded/faithful:** does not abandon — the Gate 2 seeded override (`docs/stage_2.md`) applies the ship-honest check at the same threshold. |
| Deferred math audit fails | 3 consecutive audit failures on the same characterization (hard cap) | Do **not** abandon the theory version — the measurements survive; what failed is the formal account of them. Escalate per the sketch-swap authority, whose usual first move here is a **narrower claim class**, not a new construct (`docs/stage_2.md`, "Deferred math audits"). **Seeded/faithful:** the Gate 2 seeded override applies the ship-honest check at the same threshold. |
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
| Identification audit fails | 3 plan-revision rounds (cap from `stage_3a_empirical.md`) | Treat as FAIL — empiricist selects a different design from the menu, or escalate per `stage_3a_empirical.md` step 3 routing |
| Gate 2 mechanism REVISE | 3 consecutive REVISEs on the same mechanism (hard cap) | Abandon this mechanism version — increment `theory_attempt` or swap sketches. **Seeded/faithful:** does not abandon — the Gate 2 seeded override (`docs/stage_2.md`) applies the ship-honest check at the same threshold. |
| Empirics audit fails | 5 audit-fix attempts (cap from `stage_3a_empirical.md`) | Treat as theory-version failure — re-fire theory-generator (mechanism mode) with the audit notes as input |
<!-- EMPIRICAL_FIRST_END -->
| Unseeded scorer: **SUBSTANTIVE** diff (per branch-manager) | — | Allow one more iteration in current band — the deepening is working |
| Unseeded scorer: **COSMETIC** diff (per branch-manager) | — | Treat as plateau — escalate. Reframing is not progress (see `stage_4.md`). |
| Unseeded scorer: hard ceiling | 8 total evaluations on same problem | If score is in the REVISE band or above for the current target tier (see `docs/stage_4.md`): switch to deepening playbook. Otherwise (MAJOR REWORK or ABANDON band): escalate one level. |
| Unseeded scorer plateau in the REVISE band for the current target tier | 2 consecutive substantive revisions with no real gain | Switch to deepening playbook — the core idea works, it needs mathematical depth, not reworking. |
| Unseeded scorer plateau in the REVISE band for the current target tier, branch-manager §E = Regenerate, no prior regen on this problem (`regeneration_round == 0`) | — | Fire regeneration round at Stage 1 (see `docs/stage_1.md` "Regeneration round"). Increment `regeneration_round` *before* re-entering Stage 1. **Takes precedence over the deepening-playbook row above when both fire** — Regenerate is the §E verdict that supersedes the default plateau routing. **At most one regeneration per problem:** if the regenerated attempt also plateaus, this row no longer fires (`regeneration_round > 0`) and the plateau row directly above applies — switch to the deepening playbook. |
| Unseeded theory scored ABANDON | 5 theories on same problem | Increment `problem_attempt`, set `current_stage = "stage_0"`, set `stage0_discovery_phase = "entry"`, `stage0_discovery_step = null`, `stage0_discovery_cap_context = null`, and `stage0_discovery_pending_scan = null`, then change the problem through Stage 0. This creates a distinct discovery episode; never re-enter Stage 0 under the failed problem's artifact namespace. |
| Problem viability fails | 5 problems | Pick the best scoring problem and proceed anyway |
| Editor: Major Revision (aggregated verdict) | Structural concerns (fragile, narrow, shallow) | Use deepening playbook. Triage editor's canonical comment list; revise; re-run Stage 6. Be patient — keep going as long as each round surfaces any new issue. Max 10 rounds. |
| Mechanism referee: MISATTRIBUTED unresolved | Still MISATTRIBUTED at `loops.referee.round >= 10` | Adopt the mechanism referee's identified driver as the paper's mechanism; rewrite introduction/mechanism sections and ship. **Force-adoption at round-10 resolves all outstanding locked mechanism `[FIX]` items as satisfied — no further revision cycle is required.** In seeded mode, prefer the narrow-framing path from the seed override (present what the math delivers under the seed's topic, acknowledge the mechanism-claim divergence in limitations) rather than adopting an unrelated driver. Never return to Stage 0 (never-abandon). |
| Mechanism referee: DECORATIVE unresolved | Still DECORATIVE at `loops.referee.round >= 10` | Ship the narrow-path version: after 10 rounds the restructure path has failed to surface real {{MECHANISM_QUALIFIER}} content, so narrow is the principled default. Present what the math delivers as a structural characterization, strip mechanism framing, add a limitations paragraph. **Round-10 narrow-adoption resolves all outstanding locked mechanism `[FIX]` items as satisfied.** Never return to Stage 0 (never-abandon, scientist-first). |
| Editor: Reject (aggregated verdict) | — | Stage 6 fires only post-Stage-5, so a paper draft always exists; never-abandon. Reject routes through triage → deepen directive → deepen mandate (see `docs/stage_6.md` Reject row for full procedure). The pre-Stage-5 "Stage 0 / Stage 2" branches do not exist at this point. On two consecutive cosmetic deepen attempts, the orchestrator routes through the Regeneration Round protocol if eligible (`regeneration_round == 0`, not seeded), otherwise falls back to standard Major Revision (never-abandon). |
| Editor: Downgrade tier recommendation | — | Route to the deepen-toward-target procedure in `docs/stage_6.md` "Journal-fit handling". Do **not** lower `target_journal_tier` here — the tier moves only when `branch-manager` certifies a target-tier ceiling (`gate-5-downgrade`, step 2b). |
| Editor: Upgrade tier recommendation | — | If `target_journal_tier` is below the immutable `initial_journal_tier`, update it one rung **up** the variant ladder (`{{TIER_LADDER_PROSE}}`) without crossing that initial-tier ceiling, then recompute Gate 4 advance threshold. This undoes an earlier over-eager downgrade; the next round's referees inherit the restored tier in their variant context. If the target is already at its initial tier, do not move it. See `docs/stage_6.md` "Journal-fit handling". |

Before granting another unseeded iteration in the current band, the orchestrator classifies the v(N)→v(N−1) diff as substantive or cosmetic. Branch-manager emits this verdict at every unseeded Gate 4 (Section A); when it reports COSMETIC, the orchestrator escalates rather than continue. Definitions and the cosmetic-edit catalogue live in `docs/stage_4.md`.

---

## File organization

```
output/                   # Pipeline outputs by stage
├── seed/                 # (--seed mode only) user idea files + pipeline reports
├── stage0/               # current broad/selection/deep maps; problem_statement.md; question_review.md; best_question{,_review}.md; gap_log.md (per-pass); domain_log.md (per-run); near_miss_portfolio.md + discovery_e{E}/ versioned maps (current discovery episode)
├── stage1/               # idea sketches, reviews, selected_idea.md, novelty + prototype
<!-- NO_MODE_START -->
├── stage2/               # theory drafts, math audits, novelty checks (versioned _v1, _v2…)
├── stage2b/              # theory exploration report + figures/
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
├── stage2/               # construct specs + post-experiment characterizations, design-gate
                          #   reviews, math audits (fired after Stage 3b), novelty checks
                          # (stage2b/ is not created — piloting is part of the Stage 1 check)
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
├── stage2/               # mechanism documents, novelty checks (versioned _v1, _v2…). No math audit files in this mode.
                          # (stage2b/ is not created — theory exploration is skipped)
<!-- EMPIRICAL_FIRST_END -->
├── stage3/               # implications_derived.md (deriver output) + implications.md (tagged)
├── stage3a/              # empirical feasibility + full analysis (if --ext empirical)
├── stage3b/  # LLM experiments (if --ext theory_llm)
├── stage4/               # self-attack + scorer decision (versioned)
├── debug/                # debugger reports (launched on tool-execution failures)
├── last_resort/          # last-resort reports (launched at your discretion on stubborn problems) + the branch-manager stuck reviews of any GENUINELY-STUCK verdict
├── post_pipeline/        # post-pipeline math audits
code/
├── utils/                # pre-built helpers (wrds_client, codex-math, download templates)
├── explore/              # theory-explorer scripts
├── tmp/                  # scratch/intermediate scripts
paper/
├── main.tex
├── internet_appendix.tex # standalone IA, populated only when a single proof exceeds ~3 pages or the in-paper appendix would otherwise exceed ~30% of main-text length; otherwise a no-op placeholder
├── sections/             # one .tex per section — the authoritative per-variant list is docs/stage_5.md step 3
├── simulated_referee_reports/
process_log/
├── pipeline_state.json   # current stage, scores, history
├── history.md
```

---

## Commit protocol

**Commit after every file write, stage transition, gate decision, and agent output.** Never batch. Update `process_log/pipeline_state.json` (including history array with timestamp) before committing stage transitions. After a stage-transition or gate-decision commit, if a git remote is configured (`git remote` is non-empty), push it (`git push`, or `git push -u origin HEAD` on first push); if no remote exists, skip silently.

Prefixes: `pipeline:` (state changes), `artifact:` (agent output), `paper:` (LaTeX), `scribe:` (docs).

---

{{RUNTIME_SESSION_GUIDANCE}}

---

## Documentation

The orchestrator's own commit messages and `process_log/pipeline_state.json` history array are the primary record — usually sufficient on their own.

The **scribe** agent is a supplementary pedagogical recorder for discussions, dead ends, and decision rationale that don't fit in a commit message. Launch it whenever the user intervenes mid-pipeline — any course correction, redirection, feedback, or answer to a question. The intervention itself is the trigger; the user may not ask for scribe explicitly, so capture it. Do not launch scribe automatically between stages when no intervention occurred.
