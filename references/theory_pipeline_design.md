# Autonomous Theory Paper Pipeline — Design Notes

## Inspiration: AutomaticTheory harness

The Python harness runs this pipeline per theory:

0. **Analyze problem** — deep puzzle analysis
1. **Evolve/propose** — generate theory (random/mutate/crossover + personas)
1b. **Math audit** — verify derivations (audit → fail → fix → re-audit)
2. **Pseudocode** — structured intermediate representation (with review)
3. **Translate to code** — executable implementation (with code-vs-pseudocode review)
4. **Calibrate** — LLM sets parameter bounds
5. **Optimize** — numerical optimizer hits targets
6. **Score** — quantitative (fit, plausibility, parsimony)
7. **Referee** — LLM qualitative evaluation
8. **Auto-save** — register with lineage

Key patterns: checkpointing at every stage, retry/fix loops, multiple reviewers, parallel runs with persona diversity.

---

## Design principle: Fully autonomous, no human intervention

The system must run end-to-end after a single launch command. No human approvals, no "confirm direction" steps. This means:

- **Every decision must be made by the system.** Topic selection, modeling choices, when to iterate vs. advance — all autonomous.
- **Quality is enforced by adversarial scoring.** Since no human catches bad ideas, the system must be its own harshest critic. Weak evaluation = garbage output.
- **Kill bad paths early.** Without a human to say "this isn't working," adversarial gates must reject and restart aggressively.

---

## Pipeline: Pure theory, no code

### Phase 1: Discovery

**Stage 0: Problem discovery**
- Literature search (WebSearch/WebFetch)
- Identify open questions, puzzles, gaps in finance theory
- Survey existing approaches and their limitations
- Output: `problem_statement.md` + `literature_map.md`

**Gate 0: Problem viability score**
- Is this problem important enough for a top journal?
- Is there actually a gap, or has this been solved?
- Is it tractable within a theory paper?
- Score 0-100. Threshold to proceed. If fail → search for different problem.

### Phase 2: Theory development

**Stage 1: Theory generation**
- Propose a model/mechanism
- State assumptions explicitly
- Derive key results (propositions, lemmas, corollaries)
- Strategies: fresh proposal, mutation of previous attempt, crossover of two attempts
- Persona diversity (mathematician, game theorist, behavioral, contrarian, etc.)
- Output: `theory_draft.md` (assumptions + derivations + results)

**Gate 1: Math audit (adversarial)**
- Separate agent with no access to the generator's reasoning
- Verify every derivation step-by-step
- Check: logical consistency, unstated assumptions, hand-waving, sign errors, boundary cases
- Retry loop: audit → fail → fix → re-audit (max 3 attempts)
- If fail after retries → reject theory, return to Stage 1 with different strategy/persona
- Output: `math_audit.md` (PASS/FAIL + detailed feedback)

**Gate 2: Novelty check (adversarial)**
- WebSearch to find if the result already exists
- Compare against literature map from Stage 0
- Is this a known result repackaged? A trivial extension?
- Score: novel / incremental / known
- If "known" → reject, return to Stage 1
- If "incremental" → flag, may proceed if execution is strong
- Output: `novelty_assessment.md`

### Phase 3: Development

**Stage 2: Implications & predictions**
- Testable predictions / comparative statics
- Special cases that recover known results (nests existing models)
- Surprising or counterintuitive implications
- Economic intuition for each result
- Output: `implications.md`

**Stage 3: Self-attack**
- What would a hostile referee say?
- What are the weakest assumptions? Can any be relaxed?
- What's the strongest competing explanation?
- Are there counterexamples?
- Output: `self_attack.md` with severity scores per weakness

**Gate 3: Viability decision**
- Aggregate scores from all prior gates + self-attack
- Decision: advance to writing / revise theory / abandon and restart
- This is the critical autonomous decision point
- Scoring must be calibrated to be harsh — better to restart than polish garbage

### Phase 4: Revision loop

**Stage 4: Address weaknesses**
- Take self-attack output and strengthen the theory
- Relax assumptions where possible
- Add robustness results
- Tighten derivations
- Output: revised `theory_draft.md`

**Gate 4: Re-audit**
- Full math audit on revised theory
- Must pass clean

**Stage 5: Referee simulation**
- Fresh agent, no context from development
- Reads only the theory as a paper would present it
- Top-journal R1 report
- Output: `referee_report.md`

**Gate 5: Referee score**
- If "Reject" → return to Stage 4 with referee comments (max 2 revision rounds)
- If "Major Revision" → return to Stage 4
- If "Minor Revision" or better → advance to writing

### Phase 5: Paper assembly

**Stage 6: Paper writing**
- Assemble into LaTeX: introduction, model, results, discussion, conclusion
- Follow style guide (CLAUDE.md rules)
- Proper citations from literature map
- Output: `paper/sections/*.tex`

**Stage 7: Style check**
- Run style agent
- Fix all violations
- Output: polished `paper/sections/*.tex`

**Stage 8: Final referee**
- One more fresh referee read of the complete paper
- Output: final `referee_report.md`
- If major issues → one more revision pass
- Otherwise → done

---

## Adversarial scoring design

The system's integrity depends on evaluation being harder than generation. Key principles:

### 1. Separation of concerns
- The agent that generates never evaluates its own work
- Evaluator agents start with fresh context (no access to generator's reasoning)
- Multiple independent evaluators, not one

### 2. Specific, not vague
- No "this looks good" — every score must point to specific lines, equations, assumptions
- Math audit checks step-by-step, not "overall impression"
- Novelty check cites specific existing papers

### 3. Asymmetric standards
- Generation can be creative and speculative
- Evaluation must be conservative and skeptical
- Default is reject; the theory must earn advancement

### 4. Quantitative gates
- Each gate produces a numeric score (0-100)
- Thresholds are set high (e.g., math audit must be 90+ to pass)
- Aggregate score determines advance/revise/abandon
- Suggested thresholds:
  - Math audit: 90+ to pass
  - Novelty: 60+ to proceed (above "incremental")
  - Self-attack: no severity-10 weaknesses unaddressed
  - Referee: "Minor Revision" or better to proceed to writing

### 5. Multiple referee personas
- Not one referee — simulate 2-3 with different perspectives
- A theorist, an empiricist, a skeptic
- Consensus required to advance

---

## Subagent architecture (Claude Code)

| Agent | Role | Model | Tools | Background? |
|-------|------|-------|-------|-------------|
| **orchestrator** | Main pipeline controller | opus | All | No |
| **literature-scout** | WebSearch + paper discovery | sonnet | WebSearch, WebFetch, Read, Write | Yes |
| **theory-generator** | Propose theories | opus | Read, Write | No |
| **math-auditor** | Verify derivations | opus | Read, Write | No |
| **novelty-checker** | Compare to literature | sonnet | WebSearch, WebFetch, Read, Write | No |
| **self-attacker** | Find weaknesses | opus | Read, Write | No |
| **referee** | Simulate journal referee | opus | Read, Write, Glob | No |
| **paper-writer** | Write LaTeX sections | opus | Read, Write, Edit | No |
| **style-checker** | Enforce writing rules | sonnet | Read, Glob, Grep | No |
| **scribe** | Log everything | sonnet | Read, Write, Edit, Bash | Yes |
| **scorer** | Aggregate scores, decide advance/revise/abandon | sonnet | Read, Write | No |

### Key: orchestrator is CLAUDE.md itself

The orchestrator isn't a subagent — it's the main Claude session running the pipeline. CLAUDE.md contains the full pipeline logic. The main session:
1. Reads the pipeline state (which stage are we at?)
2. Launches the appropriate subagent
3. Reads the result
4. Applies the gate logic
5. Decides next step
6. Repeats until paper is done

### State management

Pipeline state lives in `process_log/pipeline_state.json`:
```json
{
  "current_stage": "math_audit",
  "attempt": 2,
  "theory_version": 3,
  "scores": {
    "problem_viability": 82,
    "math_audit": null,
    "novelty": 71,
    "self_attack_max_severity": 7,
    "referee_recommendation": null
  },
  "history": [
    {"stage": "theory_generation", "attempt": 1, "result": "rejected_math_audit"},
    {"stage": "theory_generation", "attempt": 2, "result": "rejected_novelty"},
    {"stage": "theory_generation", "attempt": 3, "result": "pending"}
  ]
}
```

Git commits at every stage transition = checkpointing.

---

## Failure modes to design against

1. **Sycophantic evaluation** — evaluator agrees with generator because same model. Mitigation: fresh context, adversarial prompts, explicit instruction to find flaws.

2. **Infinite loops** — theory keeps failing audit, never advances. Mitigation: max attempts per stage, escalation logic (after N failures, change problem not just theory).

3. **Trivial theories** — system produces something technically correct but boring. Mitigation: novelty gate + referee "importance" score.

4. **Hallucinated literature** — fake citations. Mitigation: WebSearch verification of every cited paper, explicit "no hallucinated references" rule.

5. **Scope creep** — theory grows too complex trying to address every critique. Mitigation: parsimony score, "add one thing or cut one thing" revision rule.

6. **Style without substance** — beautiful writing around weak theory. Mitigation: adversarial gates run on the math, not the prose. Paper writing comes last.
