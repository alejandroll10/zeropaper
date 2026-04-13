# Stage 3c/3d: LLM Experiments

1. **Experiment plan.** Launch `experiment-designer` with instruction: "Write an experiment plan only — do not execute yet." The agent identifies predictions testable via LLM calls and writes `output/stage3b_experiments/experiment_plan.md` with: hypotheses, experimental design, controls, sample sizes, and expected outcomes.
2. **Review the plan.** Check: does it test the right predictions? Are controls adequate? Is sample size sufficient? If not, provide feedback.
3. **Execute.** Launch `experiment-designer` with the approved plan. The agent runs experiments using `llm_client.py`. Saves results to `output/stage3b_experiments/experiment_results.md` (canonical summary file — needed by puzzle-triager).
4. **Stage 3d:** Launch `experiment-reviewer` on the design, code, raw results, and analysis. Evaluates methodology (internal validity, controls, sample size, statistical tests) and interpretation.

| Decision | Action |
|----------|--------|
| **ACCEPT** | Proceed to **puzzle-triage entry check** (next step). |
| **REVISE** | Re-run specific experiments or re-analyze. Max 2 revision rounds. |
| **REDESIGN** | Fundamental methodology problem. Redesign and re-run. Max 1 redesign. |

5. Commit: `artifact: experiments — {ACCEPT/REVISE/REDESIGN}`

## Puzzle-triage entry check (mandatory after experiment-reviewer ACCEPT)

Before proceeding to Stage 4, you must check whether the experiment results contradict any prediction in `output/stage3/implications.md`.

1. Read `output/stage3/implications.md` and identify which implications were tested experimentally.
2. Read `output/stage3b_experiments/experiment_results.md`.
3. For each tested implication: did the experiment contradict it (effect in the wrong direction, magnitude outside predicted range, condition that should hold but failed)?
4. Write `output/stage3b_experiments/contradiction_check.md` with one of:
   - **NONE** — experiments confirm or are silent on every tested implication. Proceed to Stage 4.
   - **CONTRADICTIONS FOUND** — list the contradicted implications and what the experiments show. **Proceed to puzzle triage** (`docs/stage_puzzle_triage.md`), not Stage 4.
5. Commit: `artifact: contradiction check — {NONE/CONTRADICTIONS FOUND}`

This step is mandatory and may not be skipped.
