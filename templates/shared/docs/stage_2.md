# Stage 2: Theory Development

**Agent:** `theory-generator`

1. Read `output/stage1/selected_idea.md`, `output/stage1/idea_prototype.md`, `output/stage0/problem_statement.md`, and `output/stage0/literature_map.md`
2. Choose strategy:
   - Attempt 1: develop the selected idea into a full theory, building on the prototype's derivation. (If the selected idea's `prototype` verdict is `BLOCKED-DIFFICULTY`, the prototype has no completed derivation — build instead on its "Most promising alternative technique" note (titled "Most promising alternative angle" under `--mode empirical-first`); if that note names no specific alternative, treat this as a fresh attempt informed by where the first attempt stalled.)
   - Attempt 2+: mutate (if previous attempt had good elements) or fresh with different approach
3. Launch theory-generator with the selected idea, problem statement, literature map, **`output/stage1/negative_results.md` if it exists** (BLOCKED-IMPOSSIBLE prototypes from prior Stage-1 rounds — only proven impossibilities propagate here, not mere difficulty stalls — orchestrator must pass this in explicitly so a regenerated or re-attempted theory cannot silently re-propose a known-impossible sketch), and strategy.
<!-- THEORY_FIRST_START -->
   Pass the same file to `math-auditor` and `self-attacker` on their launches in step 4 below and at Stage 4. (theory-generator reads the prior `output/stage2/math_audit_v*.md` / `freeform_audit_v*.md` and `novelty_check_v*.md` files itself — see its body's "What you receive" — so the orchestrator does not pass them on relaunch.)
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
   Pass the negative-results file to `self-attacker` at Stage 4 too. (`math-auditor` is not launched in empirical-first mode — the math-audit form of Gate 2 below is replaced by the mechanism-plausibility gate — so prior `math_audit_v*.md` / `freeform_audit_v*.md` files do not exist; theory-generator on a mutate/pivot relaunch should instead consult the prior `output/stage2/mechanism_audit_v*.md` files for recurring plausibility-failure patterns, plus the most recent `referee-mechanism` report at Stage 6 and any `self_attack_v*.md` for prior content failures.)
<!-- EMPIRICAL_FIRST_END -->
4. Save result to `output/stage2/theory_draft_vN.md` where **N = `theory_version`** from `pipeline_state.json`. On a fresh `theory_attempt`, reset `theory_version` to 1. On each mutation (including re-launches after Gate 2 FAIL within the same attempt), increment `theory_version` and save to the new version file. N is a within-attempt counter — it does not reset across attempts within the same pipeline run, but it can collide across attempts; this is fine because attempts overwrite prior files and only the latest version matters downstream.
5. Commit: `artifact: theory draft v{N}`

<!-- THEORY_FIRST_START -->
## Gate 2: Math Audit (structured + free-form)

**Agents:** `math-auditor` then `math-auditor-freeform`

Two sequential audits — structured (step-by-step derivation check) then free-form (skeptical reader, catches conceptual issues). Both must PASS.

**Bypass recording (default mode too).** Skipping this gate, advancing past it without a result, continuing despite a FAIL, or running its task via a substitute agent is a core bypass *unless this doc sanctions it* — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

**Step 1: Structured audit**

1. Launch math-auditor on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/math_audit_vN.md`
3. Commit: `artifact: math audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the specific errors from the audit
   - If the auditor flagged a **load-bearing conjecture** (unproved claim that other results depend on): instruct the theory-generator to use `code/utils/codex_math/` (explore mode for proof strategies, write mode for proof attempts) before weakening the claim. Codex is an erratic genius — its output must be independently verified before incorporation.
   - Re-launch theory-generator in **mutate** mode with the draft + audit feedback
   - **Hard cap: 3 consecutive math-audit failures on the same theory.** At the cap, patching the current draft again is not an option — escalate to theory failure (**increment `theory_attempt` AND reset `theory_version` to 1**; the next draft is `theory_draft_v1.md` under the new attempt) or swap sketches per the authority two bullets down. Below the cap, when a fix **narrows** a claim rather than proving it, narrow *every* claim of the same shape in the draft, not only the instance the auditor named — a repair that fixes the flagged claim and leaves its siblings standing is why the same defect keeps coming back. The prior-attempt audits persist across the version-counter reset and theory-generator self-reads them (its body covers the cross-attempt case), so recurring error classes from a failed attempt still inform the fresh v1.
   - **After every 3rd theory version on the same attempt** (i.e., when `theory_version % 3 == 0`): launch branch-manager with the current draft, audit feedback, idea sketches, and literature map (no scorer output — sections A and score references will be empty). If it recommends restart, escalate to Stage 1 with a different sketch rather than continuing to patch.
   - **Pre-Stage-5 sketch-swap authority.** After **3 consecutive math-audit failures on the same theory** OR **any branch-manager RESTRUCTURE verdict**, the orchestrator must explicitly evaluate "swap to a different sketch from the Round 1 portfolio" on equal footing with "continue restructuring the current sketch." The never-abandon rule in `core.md` applies only from Stage 5 onward — before a paper draft exists, sketch-swap is a valid response to sustained theory failure. Record the evaluation in the commit message: name the candidate sketch(es), summarize why continuing might still work, and state the decision. Continuation must be justified by specific evidence that the alternative is worse, not by sunk cost. Because this bullet fires at the hard cap above, "continue restructuring the current sketch" means continuing it **under a fresh `theory_attempt`** — it is never authority to patch the capped draft again.

{{SEED_OVERRIDE_STAGE_2_GATE_2}}

5. If PASS: proceed to Step 2

**Step 2: Free-form audit**

1. Launch math-auditor-freeform on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/freeform_audit_vN.md`
3. Commit: `artifact: freeform audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the concerns from the free-form audit
   - Re-launch theory-generator in **mutate** mode with the draft + free-form audit feedback. (As above, theory-generator self-reads the prior audit files to avoid recurring error classes.)
   - After mutation, re-run **both** audits from Step 1 (the fix may have introduced new algebraic errors)
   - Same rule as Step 1: the 3-failure hard cap applies, and a narrowing fix narrows every claim of the same shape
5. If PASS: proceed to Gate 3
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
## Gate 2: Mechanism Plausibility (empirical-first)

**Agent:** `mechanism-auditor`

In empirical-first mode `theory-generator` runs in **mechanism mode** and produces a prose+DAG mechanism with at most reduced-form posits — there are no structural derivations, FOCs, or equilibrium proofs, so `math-auditor` / `math-auditor-freeform` have nothing to re-derive and are **not** launched. But a prose+DAG channel can still be *wrong as economics* — it can fail to deliver the documented sign or magnitude, contradict the Stage 1 identification design, smuggle a structural claim in as a posit, or leave the leading alternative channel un-ruled-out. Those defects do not need data to detect; catching them now costs one read, catching them at Stage 6 (`referee-mechanism`, post-data) costs a full empirical re-execution + paper rewrite + referee re-fire.

So empirical-first replaces the skipped math audit with a **lightweight plan-time plausibility gate** — the empirical-first analogue of Gate 2. It runs the *data-independent* dimensions of the `referee-mechanism` checklist; the *post-data* dimensions (does the documented heterogeneity table match the channel) remain at Stage 6 `referee-mechanism`, which is the first scrutiny against the executed empirics.

1. Launch `mechanism-auditor` with explicit paths (the body has no hardcoded defaults): the mechanism document `output/stage2/theory_draft_vN.md`, the committed identification design `output/stage1/identification_design.md`, the problem statement `output/stage0/problem_statement.md`, and — **only if empirical results already exist** (a mutate/pivot re-fire after Stage 3a) — the latest empirical analysis for the data-anchored magnitude check: the canonical `output/stage3a/empirical_analysis.md`, plus the highest-N `output/stage3a/empirical_analysis_vN.md` if Stage 3a re-fires wrote versioned files (those supersede the canonical file for the current `theory_version`; pass both and tell the auditor the versioned file is binding). Name the output path `output/stage2/mechanism_audit_vN.md`.
2. Save result to `output/stage2/mechanism_audit_vN.md`.
3. Commit: `artifact: mechanism plausibility audit v{N} — {PLAUSIBLE/REVISE}`.
4. Route:
   - **PLAUSIBLE:** set `pipeline_state.json:stage2_mechanism_version = theory_version`, then proceed to Gate 3 (novelty check).
   - **REVISE:** re-launch `theory-generator` in **mutate** mode with `mechanism_audit_vN.md` attached, increment `theory_version`, and re-run this gate on the new version. Same rule as the theory-first Gate 2 FAIL path. **Hard cap: 3 consecutive REVISEs on the same mechanism.** At the cap, re-mutating the current mechanism again is not an option — escalate, either by incrementing `theory_attempt` (reset `theory_version` to 1) or by swapping sketches per the authority below. Below the cap, where a fix narrows a posit or a claimed channel and the mechanism document makes the same move at more than one site, narrow every site rather than only the flagged one. The escalation machinery from the theory-first Gate 2 FAIL path applies here with the same triggers: the **branch-manager every-3rd-version trigger** (`theory_version % 3 == 0`, launched with the current draft + audit + idea sketches + literature map) and the **pre-Stage-5 sketch-swap authority** (after 3 consecutive REVISEs on the same mechanism OR any branch-manager RESTRUCTURE verdict, evaluate swapping to a different Round-1 sketch on equal footing with continuing — record the evaluation in the commit message: name the candidate sketch(es), why continuing might still work, and the decision; continuation must be justified by specific evidence the alternative is worse, not sunk cost).

{{SEED_OVERRIDE_STAGE_2_GATE_2}}

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `stage2_mechanism_version == theory_version` — a stale mechanism audit is a hard block, parallel to the `stage3a_theory_version` rule for the empirics (`docs/stage_3a_empirical.md` "Gate 4 enforcement") and the theory-first `stage2b_theory_version` rule. A `theory_version` that advanced without re-passing this gate cannot reach the scorer.

**Bypass recording.** This gate is a designated core step. Skipping it, advancing past a REVISE without a re-fire, or running its task via a substitute agent is a core bypass unless this doc sanctions it — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

**Re-launch on later revision.** When `referee-mechanism`, `self-attacker`, or `scorer` flags a content failure that requires the mechanism to be revised downstream, re-launch `theory-generator` in **mutate** mode with the relevant report attached, then **re-run this Gate 2 plausibility check** on the revised mechanism (which re-sets `stage2_mechanism_version` per step 4) before re-entering Stage 3 / Stage 3a — a mutate that changes the channel must re-pass the gate just as the first version did (on a post-Stage-3a re-fire the auditor uses the documented coefficients for its magnitude check). The version-counter rules (`theory_version`, `theory_attempt`) carry over.
<!-- EMPIRICAL_FIRST_END -->

## Gate 3: Novelty Check on Full Theory

**Agent:** `novelty-checker`

2nd novelty check. The idea passed at Gate 1b, but the full theory may overlap with prior work the sketch didn't reveal — novel mechanism, known result, or convergence to an existing framework.

1. Launch novelty-checker on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/novelty_check_vN.md`
3. If KNOWN: abandon this theory, return to Stage 2 with new approach (increment `theory_attempt`, reset `theory_version` to 1)
4. If INCREMENTAL: return to Stage 2 with novelty feedback (increment `theory_version`). Theory must deliver a result the literature doesn't already contain. Note the scorer does **not** blanket-fail INCREMENTAL: at H4 it cross-checks the Gate 3 report and passes an INCREMENTAL theory that carries a distinguishing result (a new comparative static, sign reversal, extra assumption that changes the conclusion, or new empirical implication), failing only INCREMENTAL with no distinguishing result. After Gate 2 + Gate 3 pass on the reworked theory, **re-run Stage 2b (exploration) AND Stage 3 (implications) before proceeding** — the theory changed, so `implications.md` and `exploration.md` are stale.
{{EMPIRICAL_STAGE2_RERUN_ADDENDUM}}
{{THEORY_LLM_STAGE2_RERUN_ADDENDUM}}

{{SEED_OVERRIDE_STAGE_2_GATE_3}}

5. If NOVEL: proceed to Stage 2b (theory exploration)
6. Commit: `artifact: novelty check v{N} — {NOVEL/INCREMENTAL/KNOWN}`

<!-- THEORY_FIRST_START -->
## Stage 2b: Theory Exploration

**Agent:** `theory-explorer`

Computational exploration — implement the key result, check at calibration, explore parameter space, produce diagnostic plots. Catches results that are correct but quantitatively zero, conditions that fail at calibration, and knife-edge assumptions.

1. Launch `theory-explorer` on the theory draft + math audit results + data inventory.
2. The agent implements the key result computationally, checks it at calibration, explores the parameter space, verifies necessary conditions, and produces diagnostic plots.
3. Save to `output/stage2b/exploration.md`, code to `code/explore/`, figures to `output/stage2b/figures/`.
4. Read the verdict:
   - If main result **holds at calibration and is quantitatively meaningful**: proceed.
   - If result **doesn't hold** or the solver/script **failed** at calibration: launch `debugger` on the failure report before concluding. Debugger diagnoses whether the failure reflects tool-fit (wrong equilibrium concept, wrong indifference conditions, sparse seed grid, etc.) or a genuine substantive failure. Only after debugger returns `SUBSTANTIVE-FAILURE` should you return to Stage 2 with the result — and even then, the theory-generator should be told "the claim doesn't hold at these parameters," not "rescope the result away." If debugger returns `TOOL-FIT-ISSUE` with a proposed fix, apply the fix and re-run theory-explorer before concluding.
   - If result is **fragile** (holds only in a narrow parameter region): flag for the scorer. Proceed but the paper should be honest about this.
   - **Surprise is judged downstream, not here.** There is no idea-stage conjecture to diverge from. Stage 2b's job is to establish *what the model yields and whether it holds*; whether that result is surprising — i.e. overturns the field's cited prior — is the scorer's call at Gate 4 against the field-prior anchor (novelty-checker), not a comparison against any author prediction. Record the headline result and its robustness in `exploration.md`; do not record a surprise verdict here.
   - **Emergent-headline selection (open approaches).** If the selected approach carried **no committed candidate answer** (an *open* approach — check `output/stage1/selected_idea.md`: its "Committed candidate answer" section is absent or marked "none — answer emerges in development"), this is where the headline is chosen. Identify **the most important result the developed model actually yielded** and **center the headline on it** — re-invoke theory-generator to make it the main result, increment `theory_version`, and re-run Gate 2 + Gate 3 **and then Stage 3 (implications)** on the re-centered theory (the headline changed, so `implications.md` is now stale and the Gate-4 SUPPORTED-cap would otherwise read the old headline's implications). This step fires **at most once per `theory_version`**: if the current Stage 2b run is itself a post-re-centering re-run, do not re-center again. (Detect a prior firing via `stage2b_theory_version == theory_version`, or a re-centering note already present in `exploration.md`. Known mild limitation: a crash *between* re-centering and the `stage2b_theory_version` update could trigger one redundant re-centering on resume — bounded and harmless, at worst a redundant theory-generator re-launch; not closed because the downside is low and the alternative is a new `pipeline_state.json` field.) Ship whatever the model proved is most important. This is discovery, not reframing. (For a **committed** approach, the committed answer is already the headline — no emergence step is needed; this bullet does not fire.) **Under `--faithful`** (`faithful: true` in `pipeline_state.json`): only emerge/re-center if the seed's `output/seed/mechanism_contract.md` `Headline:` is TBD or non-committal about the result — then update that `Headline:` in place with the emerged result (the same authorized in-place update path as the referee-mechanism narrow-framing case), so the drift auditor reads the updated headline as the referent. If the contract commits a specific result, the emerged result is an *addition*, not a replacement.
5. **Re-run on substantive revision.** If the theory revises after the first Stage 2b pass — new propositions, new sections, new extensions, or any content not explored in the prior pass — re-invoke theory-explorer on the new content before Gate 4 advances. Save targeted re-runs to `output/stage2b/exploration_vN.md` (where N is the theory version); do not overwrite the original `exploration.md`. Combined coverage must span the version that will be written into the paper. On completion, set `pipeline_state.json:stage2b_theory_version` to the current `theory_version`. Gate 4 must not advance while `stage2b_theory_version < theory_version`.
{{THEORY_LLM_STAGE3B_GATE_ADDENDUM}}
6. Commit: `artifact: theory exploration — {HOLDS/FRAGILE/FAILS}`
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
## Stage 2b: Theory Exploration — skipped in empirical-first mode

The mechanism document has no equilibrium objects to compute, no parameter space to grid-search, and no diagnostic plots that aren't already produced by the empirical analysis at Stage 3a. `theory-explorer` is not launched.

The empirical-first analogue of "does the result hold at calibration?" is the sanity check rule already inside the mechanism body: the mechanism's reduced-form posit must produce a predicted effect magnitude that matches the documented coefficient in `output/stage3a/empirical_analysis.md`. That check is in-body in `theory-generator` mechanism mode, and the body itself qualifies it for first-launch vs. mutate/pivot — at first launch the empirical results may not exist yet, in which case the mechanism states predicted magnitudes from literature/calibration that downstream Stage 3a will test; on a mutate or pivot re-launch (post-Stage-3a), the documented coefficients are the binding comparison. The Gate-4-blocking `stage2b_theory_version` rule from theory-first mode does not apply here; the analogous Gate 4 rule under empirical-first is `stage3a_theory_version == theory_version` (see `docs/stage_3a_empirical.md` "Gate 4 enforcement").

**On Gate 3 INCREMENTAL re-work:** the unguarded INCREMENTAL routing instruction earlier in this file says "re-run Stage 2b (exploration) AND Stage 3 (implications)." Under empirical-first, **skip the Stage 2b re-run** (already permanently skipped per this section). The INCREMENTAL re-work re-fires `theory-generator` (mutate), which re-enters **Gate 2 (mechanism plausibility)** on the revised mechanism — that gate must re-pass and re-set `stage2_mechanism_version` before proceeding — then re-run Gate 3 + Stage 3 + Stage 3a. The theory-version increment + the `stage2_mechanism_version` and `stage3a_theory_version` Gate-4 blocks handle staleness on both the mechanism and empirics sides.

Proceed directly from Gate 3 (novelty check on the mechanism) to Stage 3 (implications).
<!-- EMPIRICAL_FIRST_END -->

{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}
