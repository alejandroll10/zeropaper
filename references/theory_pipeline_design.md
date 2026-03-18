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
- Output: `output/stage0/problem_statement.md` + `output/stage0/literature_map.md`

**Gate 0: Problem viability score**
- Is this problem important enough for a top journal?
- Is there actually a gap, or has this been solved?
- Is it tractable within a theory paper?
- Score 0-100. Threshold to proceed. If fail → search for different problem.

### Phase 2: Idea generation (iterative)

**Stage 1: Idea generation**
- Brainstorm 3-5 candidate mechanisms for the problem (short sketches, no proofs)
- Each sketch: mechanism, key assumption, expected result, novelty angle
- Iterate with reviewer feedback: refine promising ideas, combine, drop weak ones
- Output: `output/stage1/idea_sketches_rN.md` per round

**Gate 1: Idea review**
- Evaluate each idea on novelty potential, tractability, importance, clarity
- Quick web searches to sanity-check novelty before committing to full theory
- Decision: ADVANCE (pick best idea) / ITERATE (refine with feedback) / REJECT ALL (new problem)
- Max 3 rounds of iteration, then pick best idea anyway
- Output: `output/stage1/idea_review_rN.md` + `output/stage1/selected_idea.md`

### Phase 3: Theory development

**Stage 2: Theory development**
- Develop the selected idea into a full model with proofs
- State assumptions explicitly
- Derive key results (propositions, lemmas, corollaries)
- Strategies: fresh development of selected idea, mutation of previous attempt, crossover of two attempts
- Output: `output/stage2/theory_draft_vN.md`

**Gate 2: Math audit (adversarial)**
- Separate agent with no access to the generator's reasoning
- Verify every derivation step-by-step
- Check: logical consistency, unstated assumptions, hand-waving, sign errors, boundary cases
- Retry loop: audit → fail → fix → re-audit (max 3 attempts)
- If fail after retries → reject theory, return to Stage 2 with different strategy
- Output: `output/stage2/math_audit_vN.md` (PASS/FAIL + detailed feedback)

**Gate 3: Novelty check (adversarial)**
- WebSearch to find if the result already exists
- Compare against literature map from Stage 0
- Is this a known result repackaged? A trivial extension?
- Score: NOVEL / INCREMENTAL / KNOWN
- If KNOWN → reject, return to Stage 2 with new approach
- If INCREMENTAL → flag, proceed with caution (scorer will weigh this)
- Output: `output/stage2/novelty_check_vN.md`

### Phase 4: Evaluation

**Stage 3: Implications**
- Testable predictions / comparative statics
- Special cases that recover known results (nests existing models)
- Surprising or counterintuitive implications
- Economic intuition for each result
- Output: `output/stage3/implications.md`

**Stage 4: Self-attack**
- What would a hostile referee say?
- What are the weakest assumptions? Can any be relaxed?
- What's the strongest competing explanation?
- Are there counterexamples?
- Output: `output/stage4/self_attack_vN.md` with severity scores per weakness

**Gate 4: Scorer decision**
- Aggregate scores from all prior gates + self-attack
- Five dimensions: importance (30%), novelty (25%), rigor (20%), parsimony (15%), fertility (10%)
- Decision thresholds:
  - 75+: ADVANCE to paper writing
  - 55-74: REVISE (back to Stage 2, mutate mode, max 2 rounds)
  - 35-54: MAJOR REWORK (back to Stage 1 for new ideas, max 2 rounds)
  - <35: ABANDON (back to Stage 1; after 3 abandons on same problem, back to Stage 0)
- Scoring must be calibrated to be harsh — better to restart than polish garbage
- Output: `output/stage4/scorer_decision_vN.md`

### Phase 5: Paper assembly

**Stage 5: Paper writing**
- Assemble into LaTeX: introduction, model, results, discussion, conclusion
- Follow style guide (CLAUDE.md rules)
- Proper citations from literature map
- Preemptively address self-attack weaknesses
- Output: `paper/sections/*.tex`

**Stage 6: Style check**
- Run style agent
- Fix all violations
- Output: polished `paper/sections/*.tex`

**Stage 7: Referee simulation**
- Fresh agent, no context from development
- Reads only the paper as a journal submission
- Top-journal R1 report
- Output: `paper/referee_reports/YYYY-MM-DD_vN.md`

**Gate 5: Referee decision**
- Accept / Minor Revision → fix comments, pipeline complete
- Major Revision → revise paper, re-run Stages 6-7 (max 2 rounds)
- Reject → return to Stage 2 with referee feedback, or Stage 0 if fundamental

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
- Each gate produces a numeric score or binary decision
- Thresholds are set high (math audit must PASS with zero errors)
- Aggregate scorer uses weighted dimensions with 75+ to advance
- Suggested calibration:
  - Math audit: PASS = zero errors, re-derive every step
  - Novelty: NOVEL or strong INCREMENTAL to proceed
  - Self-attack: no severity-10 weaknesses unaddressed
  - Scorer: 75+ to advance (rare — most theories score below 50)
  - Referee: Minor Revision or better to complete

### 5. Cheap iteration before expensive work
- Stage 1 (idea generation) iterates on sketches — no proofs, no algebra
- This filters dead ends before the expensive Stage 2 (full theory with proofs)
- The idea-reviewer does quick novelty web searches to catch known results early

---

## Subagent architecture (Claude Code)

| Agent | Role | Model | Tools | Background? |
|-------|------|-------|-------|-------------|
| **orchestrator** | Main pipeline controller (CLAUDE.md) | opus | All | No |
| **literature-scout** | WebSearch + paper discovery | sonnet | WebSearch, WebFetch, Read, Write, Glob, Grep | No |
| **idea-generator** | Brainstorm candidate mechanisms | opus | Read, Write | No |
| **idea-reviewer** | Evaluate/rank idea sketches | opus | Read, Write, WebSearch, WebFetch | No |
| **theory-generator** | Develop full theories with proofs | opus | Read, Write | No |
| **math-auditor** | Verify derivations adversarially | opus | Read, Write | No |
| **novelty-checker** | Compare to existing literature | sonnet | WebSearch, WebFetch, Read, Write | No |
| **self-attacker** | Find every weakness | opus | Read, Write | No |
| **scorer** | Aggregate scores, decide advance/revise/abandon | opus | Read, Write | No |
| **paper-writer** | Write LaTeX sections | opus | Read, Write, Edit, Glob, Grep | No |
| **style** | Enforce writing rules | sonnet | Read, Glob, Grep | No |
| **referee** | Simulate journal referee | opus | Read, Glob, Grep, Write | No |
| **scribe** | Log everything | sonnet | Read, Write, Edit, Bash, Grep, Glob | Yes |

### Key: orchestrator is CLAUDE.md itself

The orchestrator isn't a subagent — it's the main Claude session running the pipeline. CLAUDE.md contains the full pipeline logic. The main session:
1. Reads the pipeline state (which stage are we at?)
2. Launches the appropriate subagent
3. Reads the result
4. Applies the gate logic
5. Decides next step
6. Commits after every action
7. Repeats until paper is done

### State management

Pipeline state lives in `process_log/pipeline_state.json`:
```json
{
  "current_stage": "stage_2",
  "problem_attempt": 1,
  "idea_round": 2,
  "theory_attempt": 1,
  "revision_round": 0,
  "referee_round": 0,
  "status": "running",
  "scores": {},
  "history": [
    {"timestamp": "2026-03-17T14:00:00Z", "event": "Pipeline started"},
    {"timestamp": "2026-03-17T14:05:00Z", "event": "Stage 0 complete — problem identified"},
    {"timestamp": "2026-03-17T14:20:00Z", "event": "Stage 1 — idea review round 2 ADVANCE"}
  ]
}
```

Git commits at every stage transition and agent output = checkpointing. The dashboard reads this file every 5 seconds.

---

## Escalation rules (prevent infinite loops)

| Situation | After N failures | Action |
|-----------|-----------------|--------|
| Idea review iterates | 3 rounds | Pick the best idea and advance to Stage 2 |
| Idea review rejects all | 1 rejection | Return to Stage 0 for a different problem |
| Math audit fails | 3 attempts | Abandon this theory version |
| Theory scored REVISE | 2 rounds | Escalate to MAJOR REWORK |
| Theory scored MAJOR REWORK | 2 rounds | Escalate to ABANDON |
| Theory scored ABANDON | 3 theories on same problem | Change the problem (Stage 0) |
| Problem viability fails | 3 problems | Pick the best scoring problem and proceed anyway |
| Referee rejects | 2 rejections | Return to Stage 0 with entirely new topic |

---

## Failure modes to design against

1. **Sycophantic evaluation** — evaluator agrees with generator because same model. Mitigation: fresh context, adversarial prompts, explicit instruction to find flaws.

2. **Infinite loops** — theory keeps failing audit, never advances. Mitigation: max attempts per stage, escalation logic (after N failures, change problem not just theory).

3. **Trivial theories** — system produces something technically correct but boring. Mitigation: idea review stage filters for importance early, novelty gate, referee "importance" score.

4. **Hallucinated literature** — fake citations. Mitigation: WebSearch verification of every cited paper, explicit "no hallucinated references" rule.

5. **Scope creep** — theory grows too complex trying to address every critique. Mitigation: parsimony score, "add one thing or cut one thing" revision rule.

6. **Style without substance** — beautiful writing around weak theory. Mitigation: adversarial gates run on the math, not the prose. Paper writing comes last.

7. **Wasted compute on bad ideas** — full theory development on the first idea that comes to mind. Mitigation: Stage 1 iterates on cheap sketches before committing to expensive proofs in Stage 2.
