# theory_llm Extension — Experiment Stages

This extension adds LLM-based experiments between Implications (Stage 3) and Self-Attack (Stage 4). The pipeline tests theoretical predictions by running controlled experiments against gpt-oss models via UF NaviGator.

## Modified pipeline flow

```
... → Stage 3: Implications → Stage 3b: Experiment Design & Execution
    → Stage 3c: Experiment Review → Stage 4: Self-Attack → ...
```

Stages 3b and 3c are **optional**. They run only when:
1. `llm_client.py` exists in the project root
2. `UF_API_KEY` is set in `.env`

If either is missing, skip straight to Stage 4.

---

## Stage 3b: Experiment Design & Execution

**Agent:** `experiment-designer`

1. Read the theory draft and implications
2. Identify predictions testable via LLM calls (error rates, detection rates, idea quality distributions, etc.)
3. Design controlled experiments with ground truth, proper controls, and sufficient sample sizes
4. Write and execute experiment code using `llm_client.py`
5. Save all outputs to `output/stage3b_experiments/`:
   - `experiment_design.md`
   - `experiment_code/*.py`
   - `raw_results/*.json`
   - `experiment_analysis.md`
6. Commit: `artifact: experiments designed and executed`

---

## Stage 3c: Experiment Review

**Agent:** `experiment-reviewer`

1. Read the theory, experiment design, code, raw results, and analysis
2. Evaluate methodology: internal validity, controls, sample size, statistical tests
3. Evaluate interpretation: overclaiming, null results, effect sizes
4. Save review to `output/stage3b_experiments/experiment_review.md`
5. Read the decision:

| Decision | Action |
|----------|--------|
| **ACCEPT** | Results are sound. Proceed to Stage 4 (Self-Attack sees experiment results too). |
| **REVISE** | Re-run specific experiments or re-analyze. Max 2 revision rounds. |
| **REDESIGN** | Fundamental methodology problem. Redesign and re-run. Max 1 redesign. |

6. Commit: `artifact: experiment review — {ACCEPT/REVISE/REDESIGN}`

---

## Impact on downstream stages

- **Self-attacker** (Stage 4): receives experiment results in addition to theory draft. Can attack experimental methodology, not just theory.
- **Scorer** (Gate 4): receives experiment review. Strong experimental support can compensate for marginal theory scores. Contradicted predictions are a serious negative signal.
- **Paper-writer** (Stage 5): includes an empirical section with tables and results. The paper structure adds a `experiments.tex` section between `results.tex` and `discussion.tex`.

---

## Available models

| Model | Use case |
|-------|----------|
| `gpt-oss-120b` | Main experiments (complex reasoning, math) |
| `gpt-oss-20b` | Comparison condition (smaller model, different error patterns) |

Both are free via UF NaviGator. Reasoning effort levels: `low`, `medium`, `high`.

---

## Setup

```bash
# From project root after setup.sh:
cp extensions/theory_llm/llm_client.py .
cp extensions/theory_llm/agents/* .claude/agents/
echo "UF_API_KEY=your-key-here" > .env
pip install openai python-dotenv  # or: uv add openai python-dotenv

# Test connection:
python llm_client.py
```
