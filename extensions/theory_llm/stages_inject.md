

---

## Stage 3c/3d: LLM Experiments

1. **Experiment plan.** Launch `experiment-designer` with instruction: "Write an experiment plan only — do not execute yet." The agent identifies predictions testable via LLM calls and writes `output/stage3b_experiments/experiment_plan.md` with: hypotheses, experimental design, controls, sample sizes, and expected outcomes.
2. **Review the plan.** Check: does it test the right predictions? Are controls adequate? Is sample size sufficient? If not, provide feedback.
3. **Execute.** Launch `experiment-designer` with the approved plan. The agent runs experiments using `llm_client.py`. Saves to `output/stage3b_experiments/`.
4. **Stage 3d:** Launch `experiment-reviewer` on the design, code, raw results, and analysis. Evaluates methodology (internal validity, controls, sample size, statistical tests) and interpretation.

| Decision | Action |
|----------|--------|
| **ACCEPT** | Proceed to Stage 4 (self-attacker receives experiment results too) |
| **REVISE** | Re-run specific experiments or re-analyze. Max 2 revision rounds. |
| **REDESIGN** | Fundamental methodology problem. Redesign and re-run. Max 1 redesign. |

5. Commit: `artifact: experiments — {ACCEPT/REVISE/REDESIGN}`
