# Stage 3b: LLM Experiments

1. **Experiment plan.** Launch `experiment-designer` with instruction: "Write an experiment plan only — do not execute yet." The agent identifies predictions testable via LLM calls and writes `output/stage3b/experiment_plan.md` with: hypotheses, experimental design, controls, sample sizes, and expected outcomes.
2. **Review the plan.** Check: does it test the right predictions? Are controls adequate? Is sample size sufficient? If not, provide feedback.
3. **Execute.** On the first-ever Stage 3b run (both `stage3b_result_receipt` and `stage3b_results_path` are null), set `RESULTS_REPORT_PATH = output/stage3b/experiment_results.md`, `RESULT_PLAN = output/stage3b/experiment_results.plan.json`, `RESULT_BUNDLE = output/stage3b/experiment_results.json`, `RESULT_RECEIPT = output/stage3b/experiment_results.receipt.json`, `ANALYSIS_ENTRYPOINT = output/stage3b/experiment_code/run_all.py`, `RENDER_ENTRYPOINT = output/stage3b/experiment_code/render_exhibits.py`, `INPUT_SNAPSHOT_DIR = output/stage3b/experiment_inputs_a1`, and `SUPERSEDES_ARGS = ()`. If a retained active receipt exists with a null/stale acceptance version after a theory-identity reset, use the cumulative-replacement namespace and its supersession array. Copy the approved experiment plan, theory, implications, and other mutable document inputs into the fresh snapshot before writing `RESULT_PLAN`; launch `experiment-designer` with all seven exact paths, the array, and those copies. The agent runs experiments using `llm_client.py` through the results utility. Require `python3 code/utils/results_pipeline/results_pipeline.py verify --receipt "$RESULT_RECEIPT" --rerender` to pass; a nonzero exit re-fires the producer and cannot be deferred. The verified receipt remains pending through experiment review and contradiction checking; failed/pending attempts never change accepted pointers or retire prior active evidence.
4. **Stage 3b (review):** Launch `experiment-reviewer` on the design, code, raw results, analysis, result bundle, receipt, renderer, and rendered exhibits. Evaluates methodology (internal validity, controls, sample size, statistical tests), interpretation, and the analysis→bundle→exhibit boundary.

| Decision | Action |
|----------|--------|
| **ACCEPT** | Proceed to **puzzle-triage entry check** (next step). |
| **REVISE** | Re-run specific experiments or re-analyze. Max 2 revision rounds. |
| **REDESIGN** | Fundamental methodology problem. Redesign and re-run. Max 1 redesign. |

Every execution retry under REVISE/REDESIGN, producer failure, or receipt failure increments K and uses fresh `experiment_results_aK` report/plan/bundle/receipt, `experiment_code_aK/` analysis/renderer entrypoints, artifact, and exhibit paths. If an attempt reached pending state, preserve its diagnostic and retire it with a non-empty reason before K advances. If a prior accepted Stage 3b receipt exists, a replacement is cumulative: its report/bundle/exhibits retain every prior result still used by the paper and add or recompute the repaired experiment, with the old report/bundle/receipt declared as inputs. Set `SUPERSEDES_ARGS` to one repeated `--supersedes <receipt>` pair for every absorbed active receipt and supply it to the producer; use the empty array only when no active evidence is replaced. Explicit activation after reviewer ACCEPT and contradiction checking adds the replacement to the active set, and each predecessor remains active until the state-pointer handoff succeeds and it is explicitly retired with `--superseded-by` the replacement.

5. Commit: `artifact: experiments — {ACCEPT/REVISE/REDESIGN}`

## Puzzle-triage entry check (mandatory after experiment-reviewer ACCEPT)

Before proceeding to Stage 4, you must check whether the experiment results contradict any prediction in `output/stage3/implications.md`.

1. Read `output/stage3/implications.md` and identify which implications were tested experimentally.
2. Read the exact candidate `RESULTS_REPORT_PATH` for this attempt. The accepted `pipeline_state.json:stage3b_results_path` pointer deliberately remains unchanged until step 5 below.
3. For each tested implication: did the experiment contradict it (effect in the wrong direction, magnitude outside predicted range, condition that should hold but failed)?
4. Write `output/stage3b/contradiction_check.md` with one of:
   - **NONE** — experiments confirm or are silent on every tested implication. Proceed to Stage 4.
   - **CONTRADICTIONS FOUND** — list the contradicted implications and what the experiments show. **Proceed to puzzle triage** (`docs/stage_puzzle_triage.md`), not Stage 4.
5. The reviewer-accepted candidate is now substantively complete. Run `results_pipeline.py activate --receipt "$RESULT_RECEIPT"`; only after activation succeeds atomically set `pipeline_state.json:stage3b_theory_version = theory_version`, `stage3b_results_path = RESULTS_REPORT_PATH`, and `stage3b_result_receipt = RESULT_RECEIPT`. If this was a replacement, explicitly retire the superseded prior receipt only after the pointer update. Then follow the NONE or CONTRADICTIONS FOUND route above. This activation and three-field handoff is mandatory on the initial pass and every retry.
6. Commit: `artifact: contradiction check — {NONE/CONTRADICTIONS FOUND}`

This step is mandatory and may not be skipped.

<!-- MEASUREMENT_FIRST_START -->
## Post-experiment characterization (measurement-first only — before Stage 4)

Under `--mode measurement-first` the experiments are the paper's evidence core, and the formal content is written *about them, after them*. **This section supersedes the "Proceed to Stage 4" instruction in the contradiction-check NONE bullet above:** in this mode Stage 4 is reached only through the characterization chain here. On contradiction-check **NONE** (or once puzzle triage resolves), do **not** proceed straight to Stage 4:

1. Launch `theory-generator` in **characterization mode** with the construct spec (`output/stage2/theory_draft_vN.md`), the exact current experiment report at `pipeline_state.json:stage3b_results_path` plus the analysis artifacts bound by `pipeline_state.json:stage3b_result_receipt`, and any prior math-audit reports. It appends the formal characterization as a new `theory_draft_v{N+1}.md`; increment `theory_version`. **The characterization must end with a `NEW-TESTABLE-CONTENT:` line** (theory-generator's characterization-mode rules define it). A draft lacking that line is *incomplete output, not a new version*: re-fire `theory-generator` at the same `theory_version`, overwriting the incomplete draft, exactly as any agent whose output omits a mandatory header is re-fired. Do not audit or commit a characterization that lacks it — the line is part of the artifact, so it is written once, at creation, and every step below can rely on it.
2. Run the **deferred Gate 2 math audits** on the characterization per `docs/stage_2.md` ("Deferred math audits") — structured then free-form, 3-failure cap, characterization-mode re-fires on FAIL. Each FAIL re-fire produces a fresh characterization, so the `NEW-TESTABLE-CONTENT:` check from step 1 re-applies to every one of them; `docs/stage_2.md` carries that rule at the audit itself.
3. **Read the characterization's `NEW-TESTABLE-CONTENT:` line and route on it** — theory-generator emits it in characterization mode (step 1 guarantees it is present), and this is its call to make, not yours:
   - **`NONE`** (the normal case — the characterization formalizes evidence already collected, so the experiments remain current for it): in the same commit, **re-set `stage3b_theory_version = theory_version`** (mirroring the design-gate re-set below). Without this, the "Re-fire on theory revision" trigger below would demand a spurious experiment re-run and the Gate 4 staleness check would hard-block on every characterization.
   - **A named claim** (rare — a formal prediction the experiments did not measure): do **not** re-set. Route through the Re-fire procedure below to measure it, then re-enter characterization. Never re-set on a characterization whose declaration you have not read — that is how a formal claim nothing ever measured reaches Gate 4 with H3 reporting clean, the one failure this mode exists to prevent.
4. The design gate does not re-fire for the characterization version unless the measurement plan changed — re-set `stage2_design_version = theory_version` with a one-line commit note when the plan is unchanged (see `docs/stage_2.md` "Gate 4 enforcement").
5. Only then proceed to Stage 4. H3 gates on all three: design-gate ACCEPT, this chain's completion (`stage3b_theory_version` current per step 3), and both audit PASSes on the characterization.

<!-- MEASUREMENT_FIRST_END -->

## Re-fire on theory revision

Stage 3b is not one-shot. When the theory revises after the first 3b pass — Gate 3 INCREMENTAL rework, Gate 4 REVISE→Stage 2, Stage 6 Major Revision triggering theory-generator work, or any substantive content change — the report at `pipeline_state.json:stage3b_results_path` becomes stale relative to the current theory. The experiment-designer must re-run on the revised content before Gate 4 can advance again.

**Trigger.** Any of:
- `stage3b_theory_version` is null or differs from `theory_version` (including after a theory-identity reset).
- `implications.md` is overwritten (Gate 3 INCREMENTAL rework, PIVOT, or any path that re-runs Stage 3) and the new file contains NOVEL or PUZZLE-CANDIDATE implications not present in the prior version.
- A referee identifies an experimental gap that wasn't addressed in the first 3b pass (e.g., "this prediction was deferred" or "the manipulation doesn't isolate X").
- Stage 6 Reject verdict triggers a deepen directive (see `docs/stage_6.md` Reject row): the deepen directive's experimental requirements become the focus of the re-fire.

**Procedure.** Attempt K is a run-global Stage 3b serial: always choose the next unused value and never reset it on a new theory or Regeneration.
1. Allocate attempt K and set `RESULTS_REPORT_PATH = output/stage3b/experiment_results_vN_aK.md`, `RESULT_PLAN = output/stage3b/experiment_results_vN_aK.plan.json`, `RESULT_BUNDLE = output/stage3b/experiment_results_vN_aK_results.json`, `RESULT_RECEIPT = output/stage3b/experiment_results_vN_aK_results.receipt.json`, `ANALYSIS_ENTRYPOINT = output/stage3b/experiment_code_vN_aK/run_all.py`, `RENDER_ENTRYPOINT = output/stage3b/experiment_code_vN_aK/render_exhibits.py`, and `INPUT_SNAPSHOT_DIR = output/stage3b/experiment_inputs_vN_aK`, where N is the current `theory_version`. Copy the revised theory, current implications, revised experiment plan, and every other mutable document input into that fresh directory. Also declare the exact prior accepted report, bundle, receipt, and still-needed artifacts as producer inputs. Set `SUPERSEDES_ARGS` to one repeated `--supersedes <receipt>` pair for every absorbed active Stage 3b receipt. Launch `experiment-designer` with all seven exact paths, this exact array, and a focused instruction listing the new content while requiring one self-contained cumulative report/bundle/exhibit set.
2. Save the cumulative re-run to those versioned paths. **Do not overwrite the original report, bundle, or receipt.** Reproduce or carry forward every still-valid prior result/result ID and exhibit into the fresh namespace, add or recompute the newly targeted evidence, and pass every absorbed Stage 3b receipt through `--supersedes`. Require the step-3 receipt verification to pass. A partial new-experiment bundle cannot replace the singular Stage 3b pointers.
3. Run `experiment-reviewer` on the new analysis/bundle/receipt/exhibits (same review loop as the first pass; same caps on REVISE/REDESIGN rounds).
4. **Re-run the puzzle-triage entry check** (above) on the cumulative evidence — a new contradiction triggers puzzle-triage as it would on the first pass.
5. Confirm that step 5 of the puzzle-triage entry check already performed the one activation, atomic three-field handoff, and predecessor retirement. Do not activate or hand off a second time. Every downstream experiment consumer uses those exact cumulative pointers.

**Gate 4 enforcement.** Before any Gate 4 advance, the orchestrator must verify `stage3b_theory_version == theory_version`. Stale experiments are a hard block, parallel to the `stage2b_theory_version` rule for theory-explorer and the `stage3a_theory_version` rule for empirical analysis.

**Cap.** No hard cap on re-fires per problem — the constraint is the never-abandon rule plus the existing 10-round referee cap and, on unseeded runs, the 8-evaluation Gate 4 hard ceiling. On unseeded runs, re-fires that do not surface new evidence (reviewer ACCEPT with no new findings, no contradiction-check change) count toward Gate 4 plateau detection (see `docs/stage_4.md`). Seeded runs use Gate 4's correctness-only route instead.
