# {{RUNTIME_DOC_NAME}} — Autonomous Theory Paper Pipeline

{{RUNTIME_DISCIPLINE}}

## Purpose

This project autonomously produces a **{{PAPER_TYPE}}** suitable for submission to a {{TARGET_JOURNALS}}. The system runs end-to-end with no human intervention after launch. Quality is enforced by adversarial evaluation at every stage.

The project also produces a **process log** documenting how the autonomous system worked, as a pedagogical record.

## Core principle: treat prior work as sunk cost

At every stage, evaluate the current state of the paper on its merits — not on how much effort has been invested. If a result's framing, a section's structure, or even the paper's central claim needs to change based on new evidence (a failed audit, a reversed comparative static, a referee insight), change it. Don't defend a framing because you invested in it; defend it only if it's the strongest presentation.

Concretely:
- If a comparative static reverses during the math audit, update the result and rewrite the interpretation. Don't try to preserve the old claim.
- If a "central result" turns out to be a special case of something broader, elevate the broader result and demote the original.
- If the scorer finds the current theory is at a ceiling (score plateau), abandon and regenerate rather than continuing to polish.
- If empirical results contradict the theory, report honestly and revise the theory — don't cherry-pick supportive tests.

## Core principle: surprises are discoveries

When results go against well-formed priors — a comparative static flips sign, a necessary condition fails at calibration, or the model generates an unexpected pattern — that is often the most valuable finding. Lean into it.

Concretely:
- If the theory-explorer finds the result reverses in a plausible parameter region, ask: what economic force drives the reversal? That force may be the real contribution.
- If the empiricist finds the data contradicts the main prediction but confirms an auxiliary one, the auxiliary prediction might be the paper.
- Never suppress a surprising result to preserve a prior narrative. A clean surprise is more publishable than a confirmation of the expected.

## Core principle: characterize, don't just prove

For important results, characterize exactly when they hold and when they don't. "X holds if and only if condition C" is far more valuable than "X holds under assumptions A1-A5."

Concretely:
- If a result holds under CARA but not CRRA, find the exact condition on preferences that makes it work.
- If the theory-explorer finds the result breaks in some parameter region, characterize the boundary — the "if and only if" condition is often the real theorem.
- If a general proof fails, find the tightest sufficient condition, then show necessity by constructing a counterexample when it's violated.
- Don't settle for numerical verification of what should be a theorem.
- **No unproved mathematical claims.** Every proposition, lemma, and corollary must be proved. If a proof attempt fails, try a different strategy, find a sufficient condition under which it holds, or restructure the paper around what you can prove. Demoting a claim to a conjecture is not acceptable — an unproved conjecture is worthless in a theory paper. This rule applies to formal mathematical statements, not to assumptions or prose.

## Core principle: frame honestly — never inflate

The paper's framing must match what its results actually deliver. If the introduction invokes a large phenomenon (a crisis, a puzzle, a first-order question) that the results do not resolve, that is inflation. Referees detect framing-content gaps and penalize them more than they penalize honest narrow claims. A narrow-but-real result framed honestly is more publishable than a broad claim the content doesn't support.

## Core principle: do what makes the paper better, not what is easiest

At every decision point, choose the action that maximizes paper quality — even if a shortcut exists. When a proof fails, try harder proof strategies and use every available tool (including codex-math) before weakening the claim. When empirical data could strengthen a result, run the analysis instead of relying on verbal arguments. When a hard extension would add real content, pursue it instead of polishing exposition.

Concretely:
- If a math audit flags an unproved lemma, exhaust proof strategies (codex-math explore mode, alternative proof techniques, relaxed sufficient conditions) before demoting to a conjecture or an empirical regularity.
- If the scorer says "needs more mathematical substance," add a genuine extension — don't reframe the same content with better words.
- If a tool exists for the task (data skills, codex-math, theory-explorer), use it. Skipping available tools because they're unfamiliar is not acceptable.
- The path of least resistance produces thin papers. Referees can tell.

---

## Pipeline overview

```
Stage 0: Problem Discovery   ──→ Gate 0: Problem Viability
Stage 1: Idea Generation     ──→ Gate 1: Idea Review (iterates with generator)
                                   └── ADVANCE → best idea selected
                                Gate 1b: Novelty Check on idea
                                   ├── KNOWN → kill idea, back to Stage 1
                                   ├── INCREMENTAL → flag, proceed with caution
                                   └── NOVEL → Gate 1c
                                Gate 1c: Idea Prototype (tractability)
                                   ├── BLOCKED → try next idea or back to Stage 1
                                   └── TRACTABLE → proceed to Stage 2
Stage 2: Theory Development  ──→ Gate 2: Math Audit (structured then free-form)
                                   Gate 3: Novelty Check on full theory
                                   Stage 3a: Theory Exploration (compute, verify, plot)
                                      ├── FAILS → back to Stage 2
                                      └── HOLDS/FRAGILE → proceed
Stage 3: Implications        ──→ (extension stages injected here if applicable)
Stage 4: Self-Attack          ──→ Gate 4: Scorer Decision (trajectory-based)
                                   ├── ADVANCE (75+) → Stage 5
                                   ├── REVISE  → back to Stage 2 (continue if Δ≥3, else escalate)
                                   ├── MAJOR REWORK → back to Stage 1 (continue if Δ≥3, else escalate)
                                   └── ABANDON → back to Stage 0 (max 5×)
Stage 5: Paper Writing        ──→
Stage 6: Referee Simulation   ──→ Gate 5: Referee Decision
                                   ├── Minor/Accept → Stage 7
                                   ├── Major Revision → revise, re-run Stage 6 (max 10×)
                                   └── Reject → back to Stage 2 (fixable) or Stage 0 (fundamental)
Stage 7: Style Check          ──→ Done
```

---

## Pipeline state

State is tracked in `process_log/pipeline_state.json`. Read this file at session start. Update it after every stage transition. Commit after every update.

Initial state (created by setup.sh):
```json
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "revision_round": 0,
  "referee_round": 0,
  "status": "not_started",
  "scores": {},
  "history": []
}
```

When `--seed` is used, setup.sh also adds `"seeded": true` and sets `"current_stage": "seed_triage"`. See the seeded idea mode section below.

When you start the pipeline, set `"status": "running"` and begin appending to the history array.

**History array:** Append a `{ "timestamp": "ISO-8601", "event": "description" }` entry for every pipeline event. This feeds the dashboard. Use `date -u +%Y-%m-%dT%H:%M:%SZ` to get the timestamp. Never truncate or clear the history array.

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

## Stage 3: Implications

Read `docs/stage_3.md` and proceed accordingly.

{{EXTENSION_STAGES}}

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

## Post-pipeline math audit rule

After the pipeline is complete (`"status": "complete"`), any new or modified proposition, lemma, or corollary in `paper/sections/*.tex` must pass a math audit before being committed. This applies to all post-pipeline edits — referee response fixes, manual revisions, additions requested by co-authors, etc.

**Procedure:**
1. Write the new/modified content to a temporary file: `output/post_pipeline/pending_audit_N.md`
2. Launch `math-auditor` on that file
3. Save result to `output/post_pipeline/audit_result_N.md`
4. If FAIL: fix the content and re-audit. Do not commit to `paper/sections/` until it passes.
5. If PASS: commit the content to the paper section file.
6. Commit format: `paper: post-pipeline edit — [description] (audited)`

**Never commit unaudited mathematical content to paper sections after pipeline completion.** The pipeline's v1 runs showed 3/3 post-pipeline audits failed — this rule exists to prevent that.

---

## Never-abandon rule

**Once a paper draft exists (Stage 5+), the pipeline must produce a finished paper.** Do not loop back to Stage 0 after investing in paper writing. Instead, use the extension playbook below to strengthen the paper.

If the scorer plateaus in the 55-74 range or the referee gives Major Revision with structural concerns (result is fragile, too narrow, or shallow):

### Extension playbook

When the core result is correct but thin, extend it with mathematically hard, economically interesting analyses that uncover new content the simple model hid. The goal is characterization, not robustness.

**Extension types:** continuous time (HJB/SDEs), incomplete markets/heterogeneity (Bewley/HANK), learning/incomplete information, general preferences (CRRA/EZ/habits), higher dimensions (N assets, continuum of agents), perturbation/approximation (formal error bounds), dynamic/stochastic, moral hazard/agency, adverse selection, mechanism design, network/contagion.

**How to apply:** Identify the specific economic weakness from scorer/self-attack feedback. Pick 1-2 extensions that test whether the channel survives under realistic features. Prove the result or prove it breaks (a counterexample is as valuable as a positive result). Re-run Gate 2 + Gate 4 on extensions.

**When to extend vs. start over:** Score 55+ with correct core → extend. Score < 35 or core wrong → start over. Novelty KNOWN → start over.

---

## Escalation rules (prevent infinite loops)

| Situation | After N failures | Action |
|-----------|-----------------|--------|
| Idea review iterates | 5 rounds | Pick the best idea and advance to Gate 1b |
| Idea review rejects all | 1 rejection | Return to Stage 0 for a different problem |
| Idea novelty check (Gate 1b) KNOWN | All ideas from current round exhausted | New round of Stage 1 (counts toward 5-round limit) |
| Gate 3 novelty INCREMENTAL | 3 rework attempts at Stage 2 | Abandon this idea, return to Stage 1 for a new one |
| Math audit fails | 3 attempts | Abandon this theory version |
| Scorer: delta ≥ 3 | — | Allow one more iteration in current band |
| Scorer: delta < 3 (plateau/decline) | — | Escalate one level (REVISE → MAJOR REWORK → ABANDON) |
| Scorer: hard ceiling | 8 total evaluations on same problem | If score ≥ 55: switch to extension playbook. If score < 55: escalate one level. |
| Scorer plateau 55-74 | 2 consecutive delta < 3 | Switch to extension playbook — the core idea works, it needs mathematical depth, not reworking. |
| Theory scored ABANDON | 5 theories on same problem | Change the problem (Stage 0) |
| Problem viability fails | 5 problems | Pick the best scoring problem and proceed anyway |
| Referee: Major Revision | Structural concerns (fragile, narrow, shallow) | Use extension playbook. Be patient — keep going as long as each round surfaces any new issue. Max 10 rounds. |
| Referee rejects | 2 rejections with "fundamental flaw" | Return to Stage 0 with entirely new topic |

---

## File organization

```
output/                   # Pipeline outputs by stage
├── seed/                 # (--seed mode only) user idea files + pipeline reports
├── stage0/               # literature_map_broad.md, gap_selection.md, literature_map.md, problem_statement.md
├── stage1/               # idea sketches, reviews, selected_idea.md, novelty + prototype
├── stage2/               # theory drafts, math audits, novelty checks (versioned _v1, _v2…)
├── stage3a/              # theory exploration report + figures/
├── stage3/               # implications.md
├── stage3b/              # empirical feasibility + full analysis (if --ext empirical)
├── stage3b_experiments/  # LLM experiments (if --ext theory_llm)
├── stage4/               # self-attack + scorer decision (versioned)
├── post_pipeline/        # post-pipeline math audits
code/
├── utils/                # pre-built helpers (wrds_client, codex-math, download templates)
├── explore/              # theory-explorer scripts
├── tmp/                  # scratch/intermediate scripts
paper/
├── main.tex
├── sections/             # introduction, model, results, discussion, conclusion, appendix
├── referee_reports/
process_log/
├── pipeline_state.json   # current stage, scores, history
├── history.md
```

---

## Commit protocol

**Commit after every file write, stage transition, gate decision, and agent output.** Never batch. Update `process_log/pipeline_state.json` (including history array with timestamp) before committing stage transitions.

Prefixes: `pipeline:` (state changes), `artifact:` (agent output), `paper:` (LaTeX), `scribe:` (docs).

---

{{RUNTIME_SESSION_GUIDANCE}}

---

## Documentation

The orchestrator's own commit messages and `process_log/pipeline_state.json` history array are the primary record — usually sufficient on their own.

The **scribe** agent is a supplementary pedagogical recorder for discussions, dead ends, and decision rationale that don't fit in a commit message. Launch it whenever the user intervenes mid-pipeline — any course correction, redirection, feedback, or answer to a question. The intervention itself is the trigger; the user may not ask for scribe explicitly, so capture it. Do not launch scribe automatically between stages when no intervention occurred.
