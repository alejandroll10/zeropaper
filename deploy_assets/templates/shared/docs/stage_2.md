# Stage 2: Theory Development

**Agent:** `theory-generator`

1. Read `output/stage1/selected_idea.md`, `output/stage1/idea_prototype.md`, `output/stage0/problem_statement.md`, and `output/stage0/literature_map.md`
2. Choose strategy:
   - Attempt 1: develop the selected idea into a full theory, building on the prototype's derivation. (If the selected idea's `prototype` verdict is `BLOCKED-DIFFICULTY`, the prototype has no completed derivation — build instead on its "Most promising alternative technique" note (titled "Most promising alternative angle" under `--mode empirical-first` and `--mode measurement-first`); if that note names no specific alternative, treat this as a fresh attempt informed by where the first attempt stalled.)
   - Attempt 2+: mutate (if previous attempt had good elements) or fresh with different approach
3. Launch theory-generator with the selected idea, problem statement, literature map, **`output/stage1/negative_results.md` if it exists** (BLOCKED-IMPOSSIBLE prototypes from prior Stage-1 rounds — only proven impossibilities propagate here, not mere difficulty stalls — orchestrator must pass this in explicitly so a regenerated or re-attempted theory cannot silently re-propose a known-impossible sketch), and strategy.
<!-- NO_MODE_START -->
   Pass the same file to `math-auditor` and `self-attacker` on their launches in step 4 below and at Stage 4. (theory-generator reads the prior `output/stage2/math_audit_v*.md` / `freeform_audit_v*.md` and `novelty_check_v*.md` files itself — see its body's "What you receive" — so the orchestrator does not pass them on relaunch.)
<!-- NO_MODE_END -->
<!-- MEASUREMENT_FIRST_START -->
   Pass the negative-results file to `self-attacker` at Stage 4 too. (`math-auditor` is not launched at Stage 2 in measurement-first mode — both math audits fire on the post-Stage-3b characterization; see Gate 2 below. theory-generator on a mutate/pivot relaunch should consult the prior `output/stage2/design_review_v*.md` files for recurring design-failure patterns, plus the most recent `referee-mechanism` report and any `self_attack_v*.md` for prior content failures.)
<!-- MEASUREMENT_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
   Pass the negative-results file to `self-attacker` at Stage 4 too. (`math-auditor` is not launched in empirical-first mode — the math-audit form of Gate 2 below is replaced by the mechanism-plausibility gate — so prior `math_audit_v*.md` / `freeform_audit_v*.md` files do not exist; theory-generator on a mutate/pivot relaunch should instead consult the prior `output/stage2/mechanism_audit_v*.md` files for recurring plausibility-failure patterns, plus the most recent `referee-mechanism` report at Stage 6 and any `self_attack_v*.md` for prior content failures.)
<!-- EMPIRICAL_FIRST_END -->
<!-- DATA_FIRST_START -->
   Pass the negative-results file to `self-attacker` at Stage 4 too. (`math-auditor` is not launched in data-first mode — the math-audit form of Gate 2 below is replaced by the dataset-specification audit gate — so prior `math_audit_v*.md` / `freeform_audit_v*.md` files do not exist; theory-generator on a mutate/pivot relaunch should instead consult the prior `output/stage2/mechanism_audit_v*.md` files for recurring spec-failure patterns, plus the most recent `referee-mechanism` report at Stage 6 and any `self_attack_v*.md` for prior content failures.)
<!-- DATA_FIRST_END -->
4. Save result to `output/stage2/theory_draft_vN.md` where **N = `theory_version`** from `pipeline_state.json`. On a fresh `theory_attempt`, reset `theory_version` to 1 and atomically apply the fresh-theory identity reset in `core.md` before any gate can resume. On each mutation (including re-launches after Gate 2 FAIL within the same attempt), increment `theory_version` and save to the new version file. N is a within-attempt counter: it resets and can collide across attempts, so prior filenames may be overwritten while durable result receipts remain as history; the acceptance-version reset is what prevents same-number evidence from the abandoned attempt from satisfying a current gate.
5. Commit: `artifact: theory draft v{N}`

<!-- NO_MODE_START -->
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
   - **Hard cap: 3 consecutive math-audit failures on the same theory.** At the cap, patching the current draft again is not an option — escalate to theory failure (**increment `theory_attempt`, reset `theory_version` to 1, and atomically apply the fresh-theory identity reset from `core.md`**; the next draft is `theory_draft_v1.md` under the new attempt) or swap sketches per the authority two bullets down. Below the cap, when a fix **narrows** a claim rather than proving it, narrow *every* claim of the same shape in the draft, not only the instance the auditor named — a repair that fixes the flagged claim and leaves its siblings standing is why the same defect keeps coming back. The prior-attempt audits persist across the version-counter reset and theory-generator self-reads them (its body covers the cross-attempt case), so recurring error classes from a failed attempt still inform the fresh v1.
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
<!-- NO_MODE_END -->
<!-- EMPIRICAL_FIRST_START -->
## Gate 2: Mechanism Plausibility (empirical-first)

**Agent:** `mechanism-auditor`

In empirical-first mode `theory-generator` runs in **mechanism mode** and produces a prose+DAG mechanism with at most reduced-form posits — there are no structural derivations, FOCs, or equilibrium proofs, so `math-auditor` / `math-auditor-freeform` have nothing to re-derive and are **not** launched. But a prose+DAG channel can still be *wrong as economics* — it can fail to deliver the documented sign or magnitude, contradict the Stage 1 identification design, smuggle a structural claim in as a posit, or leave the leading alternative channel un-ruled-out. Those defects do not need data to detect; catching them now costs one read, catching them at Stage 6 (`referee-mechanism`, post-data) costs a full empirical re-execution + paper rewrite + referee re-fire.

So empirical-first replaces the skipped math audit with a **lightweight plan-time plausibility gate** — the empirical-first analogue of Gate 2. It runs the *data-independent* dimensions of the `referee-mechanism` checklist; the *post-data* dimensions (does the documented heterogeneity table match the channel) remain at Stage 6 `referee-mechanism`, which is the first scrutiny against the executed empirics.

1. Launch `mechanism-auditor` with explicit paths (the body has no hardcoded defaults): the mechanism document `output/stage2/theory_draft_vN.md`, the committed identification design `output/stage1/identification_design.md`, the problem statement `output/stage0/problem_statement.md`, and — **only if empirical results already exist** (a mutate/pivot re-fire after Stage 3a) — the exact empirical report at `pipeline_state.json:stage3a_analysis_path` for the data-anchored magnitude check, plus any prior active reports explicitly retained for combined coverage. Name the output path `output/stage2/mechanism_audit_vN.md`.
2. Save result to `output/stage2/mechanism_audit_vN.md`.
3. Commit: `artifact: mechanism plausibility audit v{N} — {PLAUSIBLE/REVISE}`.
4. Route:
   - **PLAUSIBLE:** set `pipeline_state.json:stage2_mechanism_version = theory_version`, then proceed to Gate 3 (novelty check).
   - **REVISE:** re-launch `theory-generator` in **mutate** mode with `mechanism_audit_vN.md` attached, increment `theory_version`, and re-run this gate on the new version. Same rule as the theory-first Gate 2 FAIL path. **Hard cap: 3 consecutive REVISEs on the same mechanism.** At the cap, re-mutating the current mechanism again is not an option — escalate, either by incrementing `theory_attempt`, resetting `theory_version` to 1, and atomically applying the fresh-theory identity reset from `core.md`, or by swapping sketches per the authority below. Below the cap, where a fix narrows a posit or a claimed channel and the mechanism document makes the same move at more than one site, narrow every site rather than only the flagged one. The escalation machinery from the theory-first Gate 2 FAIL path applies here with the same triggers: the **branch-manager every-3rd-version trigger** (`theory_version % 3 == 0`, launched with the current draft + audit + idea sketches + literature map) and the **pre-Stage-5 sketch-swap authority** (after 3 consecutive REVISEs on the same mechanism OR any branch-manager RESTRUCTURE verdict, evaluate swapping to a different Round-1 sketch on equal footing with continuing — record the evaluation in the commit message: name the candidate sketch(es), why continuing might still work, and the decision; continuation must be justified by specific evidence the alternative is worse, not sunk cost).

{{SEED_OVERRIDE_STAGE_2_GATE_2}}

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `stage2_mechanism_version == theory_version` — a stale mechanism audit is a hard block, parallel to the `stage3a_theory_version` rule for the empirics (`docs/stage_3a_empirical.md` "Gate 4 enforcement") and the theory-first `stage2b_theory_version` rule. A `theory_version` that advanced without re-passing this gate cannot reach the scorer.

**Bypass recording.** This gate is a designated core step. Skipping it, advancing past a REVISE without a re-fire, or running its task via a substitute agent is a core bypass unless this doc sanctions it — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

**Re-launch on later revision.** When `referee-mechanism`, `self-attacker`, or `scorer` flags a content failure that requires the mechanism to be revised downstream, re-launch `theory-generator` in **mutate** mode with the relevant report attached, then **re-run this Gate 2 plausibility check** on the revised mechanism (which re-sets `stage2_mechanism_version` per step 4) before re-entering Stage 3 / Stage 3a — a mutate that changes the channel must re-pass the gate just as the first version did (on a post-Stage-3a re-fire the auditor uses the documented coefficients for its magnitude check). The version-counter rules (`theory_version`, `theory_attempt`) carry over.
<!-- EMPIRICAL_FIRST_END -->
<!-- DATA_FIRST_START -->
## Gate 2: Dataset Specification Audit (data-first)

**Agent:** `mechanism-auditor` (spec-audit role)

In data-first mode `theory-generator` runs in **dataset-spec mode** and produces the binding dataset specification — schema, dating conventions, inclusion/reconciliation rules, validation plan, redistribution-rights inventory, fact-portfolio plan. There are no derivations, so `math-auditor` / `math-auditor-freeform` have nothing to re-derive and are **not** launched. But a spec can be broken before any build: an inclusion rule a third party cannot operationalize, a "triangulation" whose second source is a mirror of the first, an `open` rights classification resting on assumption, a replication target with no expected value, a coverage claim the Stage 1 pilot contradicted. Those defects do not need a build to detect; catching them now costs one read, catching them at Stage 3a costs a full build against a broken spec.

So data-first replaces the skipped math audit with a **plan-time specification audit** — the data-first analogue of Gate 2. It checks the build-independent dimensions (rules operational, conventions complete, triangulation real, rights cleared, portfolio checkable, incumbent comparison honest, claims pilot-consistent); the *post-build* dimensions (does the built dataset conform to the spec, was the triangulation executed) belong to the Stage 3a audit chain (`empirics-auditor`, `data-selection-auditor`, `coverage-auditor`).

1. Launch `mechanism-auditor` with explicit paths (the body has no hardcoded defaults): the dataset specification `output/stage2/theory_draft_vN.md`, the pilot-build report `output/stage1/idea_prototype.md`, the problem statement `output/stage0/problem_statement.md`, and — **only if construction results already exist** (a mutate/pivot re-fire after Stage 3a) — the exact build report at `pipeline_state.json:stage3a_analysis_path` for the build-anchored coverage-count check. Name the output path `output/stage2/mechanism_audit_vN.md`.
2. Save result to `output/stage2/mechanism_audit_vN.md`.
3. Commit: `artifact: dataset spec audit v{N} — {PLAUSIBLE/REVISE}`.
4. Route:
   - **PLAUSIBLE:** set `pipeline_state.json:dataset_spec_version = theory_version` and reset `loops.spec_audit_revision.round` to 0, then proceed to Gate 3 (novelty check).
   - **REVISE:** increment `loops.spec_audit_revision.round`, re-launch `theory-generator` in **mutate** mode with `mechanism_audit_vN.md` attached, increment `theory_version`, and re-run this gate on the new version. **Hard cap: `loops.spec_audit_revision.cap` (3) consecutive REVISEs on the same spec.** At the cap, re-mutating the current spec again is not an option — escalate, either by incrementing `theory_attempt`, resetting `theory_version` to 1, and atomically applying the fresh-theory identity reset from `core.md`, or by swapping sketches per the authority below. Below the cap, where a fix tightens a rule or narrows a coverage promise and the spec makes the same move at more than one site, tighten every site rather than only the flagged one. The escalation machinery from the theory-first Gate 2 FAIL path applies here with the same triggers: the **branch-manager every-3rd-version trigger** (`theory_version % 3 == 0`, launched with the current spec + audit + architecture sketches + literature map) and the **pre-Stage-5 sketch-swap authority** (after 3 consecutive REVISEs on the same spec OR any branch-manager RESTRUCTURE verdict, evaluate swapping to a different Round-1 architecture on equal footing with continuing — record the evaluation in the commit message: name the candidate sketch(es), why continuing might still work, and the decision; continuation must be justified by specific evidence the alternative is worse, not sunk cost).

{{SEED_OVERRIDE_STAGE_2_GATE_2}}

**Seeded runs only — data-first reading of the seeded Gate-2 override.** When `seeded: true`, the seeded-mode override (injected above on seeded deployments) applies with this reading: The Gate 2 negative verdict here is **REVISE in the dataset-specification audit**; the cap is 3 consecutive REVISEs on the same spec (`loops.spec_audit_revision.cap`); "theory/mechanism" throughout means the dataset specification. The ship-honest check's narrowing moves are dataset-native: drop or explicitly waive an untriangulable event class, narrow a coverage promise to the span the sources actually support, reclassify an unverifiable `open` right as `restricted` (build-from-source-only), or demote an adjudication target to a documented discrepancy — each applied to *every* site of the same shape in the spec, and each acceptable only while what the seed pins (the dataset gap and its core event classes) still ships. Only if the seed's core classes themselves cannot be built and validated does the abandon-report branch fire.

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `dataset_spec_version == theory_version` — a stale spec audit is a hard block, parallel to the `stage3a_theory_version` rule for the build (`docs/stage_3a_empirical.md` "Gate 4 enforcement") and the empirical-first `stage2_mechanism_version` rule. A `theory_version` that advanced without re-passing this gate cannot reach the scorer. (`stage2_mechanism_version` stays null in this mode — the spec audit's acceptance pointer is `dataset_spec_version`.)

**Bypass recording.** This gate is a designated core step. Skipping it, advancing past a REVISE without a re-fire, or running its task via a substitute agent is a core bypass unless this doc sanctions it — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

**Re-launch on later revision.** When `referee-mechanism`, `self-attacker`, `scorer`, or `puzzle-triager` (a PIVOT rewriting the fact portfolio) flags a content failure that requires the spec to be revised downstream, re-launch `theory-generator` in **mutate** (or **pivot**) mode with the relevant report attached, then **re-run this Gate 2 spec audit** on the revised spec (which re-sets `dataset_spec_version` per step 4) before re-entering Stage 3 / Stage 3a — a revision that changes rules, conventions, coverage promises, or the fact portfolio must re-pass the gate just as the first version did (on a post-Stage-3a re-fire the auditor uses the observed build counts for its coverage check). The version-counter rules (`theory_version`, `theory_attempt`) carry over.
<!-- DATA_FIRST_END -->
<!-- MEASUREMENT_FIRST_START -->
## Gate 2: Design Plausibility (measurement-first)

**Agent:** `experiment-reviewer` (plan-time launch)

In measurement-first mode `theory-generator` runs in **construct mode** and produces a construct spec + measurement plan — the formal characterization (and with it the math-audit pair) comes *after* Stage 3b, written about what was measured. But a construct spec can be wrong before any experiment runs: the task family may not operationalize the construct, the scoring rule may admit a shortcut or saturate, the plan may be under-powered or name unreachable models, the contamination argument may be verbal-only. Catching these now costs one read; catching them at Stage 3b costs the experiment budget, and at Stage 6 a full re-run + rewrite.

So measurement-first replaces the Stage-2-time math audit with a **binding plan-time design gate**: launch `experiment-reviewer` on the *measurement plan* (no results exist yet — this is a design review, the plan-time counterpart of its standard Stage 3b results review).

1. Launch `experiment-reviewer` with explicit paths: the construct spec `output/stage2/theory_draft_vN.md`, the feasibility prototype `output/stage1/idea_prototype.md`, and the problem statement `output/stage0/problem_statement.md`. Instruct it: "Plan-time design review — no results exist yet. Evaluate the construct spec's task family, scoring rule, contamination-resistance argument, power sketch, and model plan against your methodology checklist; ignore the results-analysis items. Verdict ACCEPT / REVISE / REDESIGN." Name the output path `output/stage2/design_review_vN.md`.
2. Save result to `output/stage2/design_review_vN.md`.
3. Commit: `artifact: design review v{N} — {ACCEPT/REVISE/REDESIGN}`.
4. Route:
   - **ACCEPT:** set `pipeline_state.json:stage2_design_version = theory_version`, then proceed to Gate 3 (novelty check).
   - **REVISE / REDESIGN:** re-launch `theory-generator` in **mutate** mode with `design_review_vN.md` attached, increment `theory_version`, and re-run this gate on the new version. **Hard cap: 3 consecutive non-ACCEPT verdicts on the same construct spec.** At the cap, escalate — increment `theory_attempt`, reset `theory_version` to 1, and atomically apply the fresh-theory identity reset from `core.md`, or swap sketches. The escalation machinery from the theory-first Gate 2 FAIL path applies with the same triggers: the **branch-manager every-3rd-version trigger** (`theory_version % 3 == 0`) and the **pre-Stage-5 sketch-swap authority** (after 3 consecutive non-ACCEPTs OR any branch-manager RESTRUCTURE verdict, evaluate swapping to a different Round-1 sketch on equal footing with continuing; record the evaluation in the commit message).

{{SEED_OVERRIDE_STAGE_2_GATE_2}}

**Deferred math audits (the second half of Gate 2, fired after Stage 3b).** When the Stage 3b chain completes and `theory-generator` (characterization mode) has appended the formal characterization as a new `theory_draft_vN.md` version, run the full math-audit pair on it, exactly as the theory-first Gate 2 specifies:

> **Before every audit pass — the first one and each re-audit after a FAIL — confirm the characterization ends with its `NEW-TESTABLE-CONTENT:` line** (`docs/stage_3b_experiments.md` step 1 defines it). A characterization lacking it is incomplete output, not a new version: re-fire `theory-generator` at the same `theory_version`, overwriting the incomplete draft, and audit only once the line is there. The FAIL re-fire below produces a fresh characterization each time, so checking only at Stage 3b step 1 would leave every re-fire unchecked — and Stage 3b's routing step relies on the line being present.
 `math-auditor` (structured) then `math-auditor-freeform`, saving `output/stage2/math_audit_vN.md` / `freeform_audit_vN.md`, committing each with its PASS/FAIL. On FAIL, re-launch `theory-generator` in **characterization mode** with the audit attached (the construct spec and the measurements are fixed; only the characterization revises), increment `theory_version`, and re-audit — **hard cap: 3 consecutive audit failures on the same characterization**, at which point escalate per the sketch-swap authority (the *measurements* survive; what failed is the formal account of them, so the usual first escalation is a narrower claim class, not a new construct). The codex-math escalation for load-bearing conjectures applies here as in theory-first mode. Gate 4 must not advance unless both audits PASS on the current `theory_version` (H3).

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `stage2_design_version == theory_version` **and** both math-audit files exist with PASS for the current `theory_version` — a stale design review or an unaudited characterization is a hard block, parallel to the `stage2_mechanism_version` rule in empirical-first. (A characterization-mode re-fire increments `theory_version`; the design gate does **not** re-fire for it unless the revision changed the *measurement plan* — re-set `stage2_design_version = theory_version` with a one-line note in the commit message when the plan is unchanged, or re-run the design gate when it changed.)

**Bypass recording.** This gate — both halves — is a designated core step. Skipping either half, advancing past a non-ACCEPT or FAIL without a re-fire, or running its task via a substitute agent is a core bypass unless this doc sanctions it — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

**Re-launch on later revision.** When `referee-mechanism`, `self-attacker`, or `scorer` flags a content failure requiring the construct spec or characterization to revise downstream, re-launch `theory-generator` in the appropriate mode with the report attached, then re-pass the corresponding gate half (design gate for a spec/plan change; math audits for a characterization change) before re-entering later stages. The version-counter rules (`theory_version`, `theory_attempt`) carry over.
<!-- MEASUREMENT_FIRST_END -->

## Gate 3: Novelty Check on Full Theory

**Agent:** `novelty-checker`

2nd novelty check. The idea passed at Gate 1b, but the full theory may overlap with prior work the sketch didn't reveal — novel mechanism, known result, or convergence to an existing framework.

1. Launch novelty-checker on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/novelty_check_vN.md`
3. If KNOWN: abandon this theory, return to Stage 2 with a new approach: increment `theory_attempt`, reset `theory_version` to 1, and atomically apply the fresh-theory identity reset from `core.md`.
4. If INCREMENTAL: return to Stage 2 with novelty feedback (increment `theory_version`). Theory must deliver a result the literature doesn't already contain. Note the scorer does **not** blanket-fail INCREMENTAL: at H4 it cross-checks the Gate 3 report and passes an INCREMENTAL theory that carries a distinguishing result (a new comparative static, sign reversal, extra assumption that changes the conclusion, or new empirical implication), failing only INCREMENTAL with no distinguishing result. After Gate 2 + Gate 3 pass on the reworked theory, **re-run Stage 2b (exploration) AND Stage 3 (implications) before proceeding** — the theory changed, so `implications.md` and `exploration.md` are stale.
{{EMPIRICAL_STAGE2_RERUN_ADDENDUM}}
{{THEORY_LLM_STAGE2_RERUN_ADDENDUM}}

{{SEED_OVERRIDE_STAGE_2_GATE_3}}

5. If NOVEL: proceed to Stage 2b (theory exploration)
6. Commit: `artifact: novelty check v{N} — {NOVEL/INCREMENTAL/KNOWN}`

<!-- DATA_FIRST_START -->
## Stage 2b: Theory Exploration — skipped in data-first mode

The dataset specification has no equilibrium objects to compute, no parameter space to grid-search, and no diagnostic plots that aren't already produced by the construction analysis at Stage 3a. The Stage 1 pilot build already played the exploratory role on real source slices. `theory-explorer` is not launched.

The data-first analogue of "does the result hold at calibration?" is the sanity check rule already inside the spec body: the spec's expected per-class coverage counts must match the pilot's observed counts (first launch) or the build report's actual counts at `pipeline_state.json:stage3a_analysis_path` (mutate/pivot re-launch). The Gate-4-blocking `stage2b_theory_version` rule from theory-first mode does not apply here; the analogous Gate 4 rules under data-first are `dataset_spec_version == theory_version` (see Gate 2 above) and `stage3a_theory_version == theory_version` (see `docs/stage_3a_empirical.md` "Gate 4 enforcement").

**On Gate 3 INCREMENTAL re-work:** the unguarded INCREMENTAL routing instruction earlier in this file says "re-run Stage 2b (exploration) AND Stage 3 (implications)." Under data-first, **skip the Stage 2b re-run** (already permanently skipped per this section). The INCREMENTAL re-work re-fires `theory-generator` (mutate), which re-enters **Gate 2 (spec audit)** on the revised spec — that gate must re-pass and re-set `dataset_spec_version` before proceeding — then re-run Gate 3 + Stage 3 + Stage 3a. The theory-version increment + the `dataset_spec_version` and `stage3a_theory_version` Gate-4 blocks handle staleness on both the spec and build sides.

Proceed directly from Gate 3 (novelty check on the spec) to Stage 3 (implications).
<!-- DATA_FIRST_END -->
<!-- NO_MODE_START -->
## Stage 2b: Theory Exploration

**Agent:** `theory-explorer`

Computational exploration — implement the key result, check at calibration, explore parameter space, produce diagnostic plots. Catches results that are correct but quantitatively zero, conditions that fail at calibration, and knife-edge assumptions.

Attempt K is a run-global Stage 2b serial: always choose the next unused value and never reset it on a new theory or Regeneration.

1. On the first-ever Stage 2b run (both `stage2b_result_receipt` and `stage2b_exploration_path` are null), set `EXPLORATION_PATH = output/stage2b/exploration.md`, `RESULT_PLAN = output/stage2b/results.plan.json`, `RESULT_BUNDLE = output/stage2b/results.json`, `RESULT_RECEIPT = output/stage2b/results.receipt.json`, `ANALYSIS_ENTRYPOINT = code/explore/run_all.py`, `RENDER_ENTRYPOINT = code/explore/render_exhibits.py`, `INPUT_SNAPSHOT_DIR = output/stage2b/inputs_a1`, and `SUPERSEDES_ARGS = ()`. Copy the theory draft, math-audit results, and data-inventory document into that fresh directory before writing `RESULT_PLAN`; launch `theory-explorer` on those copies and supply all seven exact paths plus the empty array. If a retained active receipt exists with a null/stale acceptance version after a theory-identity reset, use step 5's cumulative-replacement namespace and supersession array.
2. The agent implements the key result computationally, checks it at calibration, explores the parameter space, verifies necessary conditions, and produces diagnostic plots.
3. Require the report, run-plan-v1 declaration, schema-v1 bundle, receipt, analysis code, separate renderer, and declared exhibits. Run `python3 code/utils/results_pipeline/results_pipeline.py verify --receipt "$RESULT_RECEIPT" --rerender`; a nonzero exit re-fires `theory-explorer` and cannot be deferred. Every re-fire—including a debugger `TOOL-FIT-ISSUE`, failed `run`, failed render, or receipt-verification failure—allocates attempt `aK+1` with fresh report/plan/bundle/receipt/code/artifact/exhibit paths. If the failed attempt reached pending state, preserve its diagnostic and retire that receipt with reason `failed Stage 2b attempt aK`; never reuse its namespace.
4. Read the verdict:
   - If main result **holds at calibration and is quantitatively meaningful**: activate `RESULT_RECEIPT`; atomically set `stage2b_theory_version = theory_version`, `stage2b_exploration_path = EXPLORATION_PATH`, and `stage2b_result_receipt = RESULT_RECEIPT`; then explicitly retire any superseded prior receipt and proceed.
   - If result **doesn't hold** or the solver/script **failed** at calibration: launch `debugger` on the failure report before concluding. Debugger diagnoses whether the failure reflects tool-fit (wrong equilibrium concept, wrong indifference conditions, sparse seed grid, etc.) or a genuine substantive failure. After `SUBSTANTIVE-FAILURE`, preserve the diagnostic and explicitly retire the pending `RESULT_RECEIPT` with reason `Stage 2b substantive failure` before returning to Stage 2; tell theory-generator "the claim doesn't hold at these parameters," not "rescope the result away." If debugger returns `TOOL-FIT-ISSUE`, retire the current pending receipt with that diagnostic, allocate the next complete fresh attempt namespace, apply the proposed fix there, and re-run theory-explorer.
   - If result is **fragile** (holds only in a narrow parameter region): flag for the scorer, perform the same activate → atomic three-field pointer handoff → explicit prior-retirement sequence, and proceed, but the paper should be honest about this.
   - **Surprise is judged downstream, not here.** There is no idea-stage conjecture to diverge from. Stage 2b's job is to establish *what the model yields and whether it holds*; whether that result is surprising — i.e. overturns the field's cited prior — is the scorer's call at Gate 4 against the field-prior anchor (novelty-checker), not a comparison against any author prediction. Record the headline result and its robustness in `exploration.md`; do not record a surprise verdict here.
   - **Emergent-headline selection (open approaches).** If the selected approach carried **no committed candidate answer** (an *open* approach — check `output/stage1/selected_idea.md`: its "Committed candidate answer" section is absent or marked "none — answer emerges in development"), this is where the headline is chosen. Identify **the most important result the developed model actually yielded** and **center the headline on it** — re-invoke theory-generator to make it the main result, increment `theory_version`, and re-run Gate 2 + Gate 3 **and then Stage 3 (implications)** on the re-centered theory (the headline changed, so `implications.md` is now stale and the Gate-4 SUPPORTED-cap would otherwise read the old headline's implications). This step fires **at most once per `theory_version`**: if the current Stage 2b run is itself a post-re-centering re-run, do not re-center again. (Detect a prior firing via `stage2b_theory_version == theory_version`, or a re-centering note already present in `exploration.md`. Known mild limitation: a crash *between* re-centering and the `stage2b_theory_version` update could trigger one redundant re-centering on resume — bounded and harmless, at worst a redundant theory-generator re-launch; not closed because the downside is low and the alternative is a new `pipeline_state.json` field.) Ship whatever the model proved is most important. This is discovery, not reframing. (For a **committed** approach, the committed answer is already the headline — no emergence step is needed; this bullet does not fire.) **Under `--faithful`** (`faithful: true` in `pipeline_state.json`): only emerge/re-center if the seed's `output/seed/mechanism_contract.md` `Headline:` is TBD or non-committal about the result — then update that `Headline:` in place with the emerged result (the same authorized in-place update path as the referee-mechanism narrow-framing case), so the drift auditor reads the updated headline as the referent. If the contract commits a specific result, the emerged result is an *addition*, not a replacement.
5. **Re-run on substantive revision.** If the theory revises after the first Stage 2b pass, allocate attempt K for that theory version: `EXPLORATION_PATH = output/stage2b/exploration_vN_aK.md`, `RESULT_PLAN = output/stage2b/exploration_vN_aK_results.plan.json`, `RESULT_BUNDLE = output/stage2b/exploration_vN_aK_results.json`, `RESULT_RECEIPT = output/stage2b/exploration_vN_aK_results.receipt.json`, `ANALYSIS_ENTRYPOINT = code/explore/run_all_vN_aK.py`, `RENDER_ENTRYPOINT = code/explore/render_exhibits_vN_aK.py`, and `INPUT_SNAPSHOT_DIR = output/stage2b/inputs_vN_aK` (N = theory version). Copy every current mutable document input into that fresh directory and supply all seven exact paths plus fresh artifact and exhibit paths. Do not overwrite any prior attempt. Because Stage 2b has one report/receipt pointer, every replacing re-fire is cumulative: declare the prior accepted report, bundle, receipt, and still-needed artifacts as inputs; reproduce or carry forward every still-valid old result/result ID and exhibit into the fresh namespace; add or recompute the revised results; set `SUPERSEDES_ARGS` to one repeated `--supersedes <receipt>` pair for every absorbed active Stage 2b receipt, and supply that exact array to `theory-explorer`. A partial targeted bundle may not replace the pointer. A failed pending attempt is retired before K advances. Require step-3 verification and a HOLDS/FRAGILE verdict; activate the new receipt, atomically update `stage2b_theory_version`, `stage2b_exploration_path`, and `stage2b_result_receipt`, and only then retire every absorbed predecessor with `--superseded-by RESULT_RECEIPT`. Gate 4 must not advance while the version or either pointer is stale.
{{THEORY_LLM_STAGE3B_GATE_ADDENDUM}}
6. Commit: `artifact: theory exploration — {HOLDS/FRAGILE/FAILS}`
<!-- NO_MODE_END -->
<!-- EMPIRICAL_FIRST_START -->
## Stage 2b: Theory Exploration — skipped in empirical-first mode

The mechanism document has no equilibrium objects to compute, no parameter space to grid-search, and no diagnostic plots that aren't already produced by the empirical analysis at Stage 3a. `theory-explorer` is not launched.

The empirical-first analogue of "does the result hold at calibration?" is the sanity check rule already inside the mechanism body: the mechanism's reduced-form posit must produce a predicted effect magnitude that matches the documented coefficient in the exact report at `pipeline_state.json:stage3a_analysis_path`. That check is in-body in `theory-generator` mechanism mode, and the body itself qualifies it for first-launch vs. mutate/pivot — at first launch the empirical results may not exist yet, in which case the mechanism states predicted magnitudes from literature/calibration that downstream Stage 3a will test; on a mutate or pivot re-launch (post-Stage-3a), the documented coefficients are the binding comparison. The Gate-4-blocking `stage2b_theory_version` rule from theory-first mode does not apply here; the analogous Gate 4 rule under empirical-first is `stage3a_theory_version == theory_version` (see `docs/stage_3a_empirical.md` "Gate 4 enforcement").

**On Gate 3 INCREMENTAL re-work:** the unguarded INCREMENTAL routing instruction earlier in this file says "re-run Stage 2b (exploration) AND Stage 3 (implications)." Under empirical-first, **skip the Stage 2b re-run** (already permanently skipped per this section). The INCREMENTAL re-work re-fires `theory-generator` (mutate), which re-enters **Gate 2 (mechanism plausibility)** on the revised mechanism — that gate must re-pass and re-set `stage2_mechanism_version` before proceeding — then re-run Gate 3 + Stage 3 + Stage 3a. The theory-version increment + the `stage2_mechanism_version` and `stage3a_theory_version` Gate-4 blocks handle staleness on both the mechanism and empirics sides.

Proceed directly from Gate 3 (novelty check on the mechanism) to Stage 3 (implications).
<!-- EMPIRICAL_FIRST_END -->
<!-- MEASUREMENT_FIRST_START -->
## Stage 2b: Theory Exploration — skipped in measurement-first mode

The construct spec has no equilibrium objects to compute and no parameter space to grid-search; the feasibility pilot at Stage 1 already played the "does anything separate at all" role, and the real evidence is Stage 3b itself. `theory-explorer` is not launched.

The measurement-first analogue of "does the result hold at calibration?" is the in-body sanity check of construct mode: the predicted headline contrast instantiated at the pilot's parameters must clear the pilot's observed variance. The Gate-4-blocking `stage2b_theory_version` rule from theory-first mode does not apply here; the analogous Gate 4 rules are `stage2_design_version == theory_version` plus the deferred math-audit PASS requirement (see Gate 2 above) and the Stage 3b chain completion (H3).

**On Gate 3 INCREMENTAL re-work:** the unguarded INCREMENTAL routing instruction earlier in this file says "re-run Stage 2b (exploration) AND Stage 3 (implications)." Under measurement-first, **skip the Stage 2b re-run** (permanently skipped per this section). The INCREMENTAL re-work re-fires `theory-generator` (mutate, construct mode), which re-enters **Gate 2 (design gate)** on the revised spec — that gate must re-pass and re-set `stage2_design_version` before proceeding — then re-run Gate 3 + Stage 3 + Stage 3b; the deferred audits then re-fire on the new characterization.

Proceed directly from Gate 3 (novelty check on the construct) to Stage 3 (implications).
<!-- MEASUREMENT_FIRST_END -->

{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}
