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
                                   └── ABANDON → back to Stage 0 (max 3×)
Stage 5: Paper Writing        ──→
Stage 6: Referee Simulation   ──→ Gate 5: Referee Decision
                                   ├── Minor/Accept → Stage 7
                                   ├── Major Revision → revise, re-run Stage 6 (max 10×)
                                   └── Reject → back to Stage 1
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

### Step 0a: Broad literature scan

**Agent:** `literature-scout`

1. Choose a domain within {{DOMAIN_AREAS}}
2. Launch literature-scout to search for open questions, puzzles, or gaps
3. Save results to `output/stage0/literature_map_broad.md`
4. Commit: `artifact: broad literature scan`

### Step 0b: Pre-select a gap

Read the broad map + `output/data_inventory.md` (if it exists). Pick the most promising gap area, considering: gap size, tractability, data availability, room between existing papers. Write the selection (a few sentences) to `output/stage0/gap_selection.md`.

### Step 0c: Deep search on the gap

**Agent:** `gap-scout`

1. Launch gap-scout with the broad map, the gap selection, and the data inventory
2. Save results to `output/stage0/literature_map.md` (this is the canonical map used downstream)
3. Commit: `artifact: deep literature map`
4. If the gap-scout reports the gap is **closed**: return to Step 0b, pick the next most promising gap from the broad scan, re-run Step 0c

### Step 0d: Problem statement

Write `output/stage0/problem_statement.md`. Requirements:
- Must reference the data inventory (if it exists)
- Must name the closest competitor identified by the gap-scout
- Must NOT specify a theoretical framework — that is the idea-generator's job
- Commit: `pipeline: stage 0 — problem statement written`

### Gate 0: Problem Viability

The orchestrator (you) evaluates:
- Is this question important enough for a top journal?
- Is there actually a gap? (The gap-scout's gap status is the primary evidence.)
- Is it tractable as a pure theory paper?
- Is the closest competitor correctly identified?
- Is the idea space left open? (If the problem statement pre-commits to a specific framework, that is a Gate 0 failure — rewrite it.)

Score 0-100. If below 50, return to Step 0b with a different gap. After 5 failures, pick the best problem and proceed.

---

## Stage 1: Idea Generation

**Agents:** `idea-generator` + `idea-reviewer` (iterating)

**How many ideas to generate:** More candidates when the pool is weaker — more failures mean more draws needed.

| Context | Ideas per round |
|---------|----------------|
| 1st time entering Stage 1 | 5 |
| Returning from a failed theory (scorer MAJOR REWORK/ABANDON) | 10 |
| Returning from a problem-level failure (Stage 0 re-run) | 10, and explicitly explore different territory |

1. Read `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md`
2. **If returning from a failed attempt:** first reread all `output/stage1/idea_sketches_r*.md` files. Identify which unused sketches are still viable given what the failed attempt revealed. Pick the next-best unused sketch before generating new ideas — only regenerate if no unused sketch is viable. Also read the previous scorer feedback and/or failed theory to understand what went wrong — instruct the idea-generator to avoid the same failure mode
3. Launch idea-generator with the problem statement, literature map, **and data inventory** to brainstorm candidate mechanisms (see table above for count)
4. Save sketches to `output/stage1/idea_sketches_rN.md` (N = round number)
5. Commit: `artifact: idea sketches round {N}`

### Gate 1: Idea Review

**Agent:** `idea-reviewer`

1. Launch idea-reviewer on the sketches + problem statement + literature map
2. If this is a return visit to Stage 1, also provide the previous scorer feedback so the reviewer knows what to screen against
3. Save review to `output/stage1/idea_review_rN.md`
4. Commit: `artifact: idea review round {N}`
5. Read the decision:

| Decision | Action |
|----------|--------|
| **ADVANCE** | Best idea identified. Proceed to Stage 2 with the reviewer's instructions for theory development. |
| **ITERATE** | Re-launch idea-generator with the reviewer's feedback. Max 5 rounds of iteration. |
| **REJECT ALL** | All ideas are weak. Return to Stage 0 for a different problem. |

6. After 5 rounds without ADVANCE, pick the highest-scored idea and advance it anyway.
7. Save the winning idea summary to `output/stage1/selected_idea.md`
8. Commit: `artifact: selected idea saved`

### Gate 1b: Novelty Check on Selected Idea

**Agent:** `novelty-checker`

1st of 2 novelty checks — runs on the selected idea *before* investing in theory development.

1. Launch novelty-checker on `output/stage1/selected_idea.md` + `output/stage0/literature_map.md`
2. Save result to `output/stage1/novelty_check_idea.md`
3. Read the verdict:

| Verdict | Action |
|---------|--------|
| **KNOWN** | Kill this idea. Pick the next-best idea from the current round's sketches (per idea-reviewer rankings) and re-run Gates 1b + 1c on it. If no viable ideas remain, re-run Stage 1 with a new round (counts toward the 5-round total cap on Stage 1 iterations). |
| **INCREMENTAL** | Proceed to Gate 1c, then Stage 2, but instruct the theory-generator: "This idea was flagged INCREMENTAL — the obvious version of this model already exists in the literature. Your job is to find a result within this framework that the existing papers do not imply: a sign reversal, an unexpected threshold, a case where the standard intuition breaks. Do not formalize the obvious version." Gate 3 will hard-fail INCREMENTAL on the full theory, so the theory must escape incrementality during development. |
| **NOVEL** | Proceed to Gate 1c. |

4. Commit: `pipeline: gate 1b — novelty check on idea {NOVEL/INCREMENTAL/KNOWN}`

### Gate 1c: Idea Prototype (tractability + surprise check)

**Agent:** `idea-prototyper`

Quick mathematical feasibility check — attempt the key derivation before investing in full theory development. **Always runs** (not optional), because even 1st-attempt ideas can have hidden tractability issues that the sketch doesn't reveal. Also performs a **surprise check** on TRACTABLE results: now that the math shows what the result looks like, is it non-obvious?

1. Launch idea-prototyper on `output/stage1/selected_idea.md` + `output/stage0/problem_statement.md`
2. Save result to `output/stage1/idea_prototype.md`
3. Read the verdict:

| Verdict | Surprise | Action |
|---------|----------|--------|
| **TRACTABLE** | **SURPRISING** or **POTENTIALLY SURPRISING** | Proceed to Stage 2 — pass the prototype to the theory-generator as a head start. |
| **TRACTABLE** | **OBVIOUS** | Soft kill signal. The idea is tractable but the result confirms what everyone would guess. Proceed to Stage 2, but instruct the theory-generator to find a non-obvious result within the model (unexpected comparative static, interaction effect, parameter regime where the sign flips). If the full theory also scores low on surprise at Gate 4, the idea will not advance. |
| **BLOCKED** | — | The derivation hit a wall. Read where it got stuck. If fixable: pick the next-best idea from the reviewer's rankings and re-run Gates 1b+1c. If fundamental: return to Stage 1 for a new round. |

4. Commit: `pipeline: gate 1c — idea prototype {TRACTABLE/BLOCKED}, surprise: {SURPRISING/POTENTIALLY SURPRISING/OBVIOUS}`
5. Update `process_log/pipeline_state.json` and commit: `pipeline: stage 1 complete — idea selected, novelty-checked, and prototyped`

---

## Stage 2: Theory Development

**Agent:** `theory-generator`

1. Read `output/stage1/selected_idea.md`, `output/stage1/idea_prototype.md`, `output/stage0/problem_statement.md`, and `output/stage0/literature_map.md`
2. Choose strategy:
   - Attempt 1: develop the selected idea into a full theory, building on the prototype's derivation
   - Attempt 2+: mutate (if previous attempt had good elements) or fresh with different approach
3. Launch theory-generator with the selected idea, problem statement, literature map, and strategy
4. Save result to `output/stage2/theory_draft_vN.md` (N = attempt number)
5. Commit: `artifact: theory draft v{N}`

### Gate 2: Math Audit (structured + free-form)

**Agents:** `math-auditor` then `math-auditor-freeform`

Two sequential audits — structured (step-by-step derivation check) then free-form (skeptical reader, catches conceptual issues). Both must PASS.

**Step 1: Structured audit**

1. Launch math-auditor on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/math_audit_vN.md`
3. Commit: `artifact: math audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the specific errors from the audit
   - If the auditor flagged a **load-bearing conjecture** (unproved claim that other results depend on): instruct the theory-generator to use `code/utils/codex_math/` (explore mode for proof strategies, write mode for proof attempts) before weakening the claim. Codex is an erratic genius — its output must be independently verified before incorporation.
   - Re-launch theory-generator in **mutate** mode with the draft + audit feedback
   - Keep iterating as long as the error count is decreasing (making progress). Escalate only if errors plateau or increase across two consecutive attempts — treat as theory failure, increment theory_attempt
   - **After every 3rd theory version on the same attempt:** launch branch-manager with the current draft, audit feedback, idea sketches, and literature map (no scorer output — sections A and score references will be empty). If it recommends restart, escalate to Stage 1 with a different sketch rather than continuing to patch.
5. If PASS: proceed to Step 2

**Step 2: Free-form audit**

1. Launch math-auditor-freeform on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/freeform_audit_vN.md`
3. Commit: `artifact: freeform audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the concerns from the free-form audit
   - Re-launch theory-generator in **mutate** mode with the draft + free-form audit feedback
   - After mutation, re-run **both** audits from Step 1 (the fix may have introduced new algebraic errors)
   - Same rule: keep iterating while progress is being made, escalate if concerns plateau or increase
5. If PASS: proceed to Gate 3

### Gate 3: Novelty Check on Full Theory

**Agent:** `novelty-checker`

2nd novelty check. The idea passed at Gate 1b, but the full theory may overlap with prior work the sketch didn't reveal — novel mechanism, known result, or convergence to an existing framework.

1. Launch novelty-checker on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/novelty_check_vN.md`
3. If KNOWN: abandon this theory, return to Stage 2 with new approach
4. If INCREMENTAL: return to Stage 2 with novelty feedback. Theory must deliver a result the literature doesn't already contain — scorer will hard-fail H4 on INCREMENTAL.
5. If NOVEL: proceed to Stage 3a (theory exploration)
6. Commit: `artifact: novelty check v{N} — {NOVEL/INCREMENTAL/KNOWN}`

### Stage 3a: Theory Exploration

**Agent:** `theory-explorer`

Computational exploration — implement the key result, check at calibration, explore parameter space, produce diagnostic plots. Catches results that are correct but quantitatively zero, conditions that fail at calibration, and knife-edge assumptions.

1. Launch `theory-explorer` on the theory draft + math audit results + data inventory.
2. The agent implements the key result computationally, checks it at calibration, explores the parameter space, verifies necessary conditions, and produces diagnostic plots.
3. Save to `output/stage3a/exploration.md`, code to `code/explore/`, figures to `output/stage3a/figures/`.
4. Read the verdict:
   - If main result **holds at calibration and is quantitatively meaningful**: proceed.
   - If result **doesn't hold** or is **effectively zero** at calibration: return to Stage 2 with the exploration results. The theory-generator needs to know what the computation found.
   - If result is **fragile** (holds only in a narrow parameter region): flag for the scorer. Proceed but the paper should be honest about this.
5. Commit: `artifact: theory exploration — {HOLDS/FRAGILE/FAILS}`

## Stage 3: Implications

**Orchestrator task** (no separate agent needed — you do this)

1. Read the theory draft
2. Work out:
   - Testable predictions
   - Comparative statics
   - Special cases that recover known results
   - Economic intuition for each result
3. Append to the theory draft or write to `output/stage3/implications.md`
4. Commit: `pipeline: stage 3 — implications developed`

{{EXTENSION_STAGES}}

---

## Stage 4: Self-Attack

**Agent:** `self-attacker`

1. Launch self-attacker on the theory draft + implications + theory exploration results (if available)
2. Save result to `output/stage4/self_attack_vN.md`
3. Commit: `artifact: self-attack v{N}`
4. **Triage the concerns.** Before any revision, categorize each concern from the self-attack (and any prior free-form audit concerns still open) using the agent's own tags as a starting point:
   - `[FIX]` — a load-bearing claim is wrong; revise in main text
   - `[LIMITS]` — legitimate concern; one sentence in limitations
   - `[RESPONSE]` — address in response letter only; no paper change
   - `[NOTE]` — no action
   Save the triage to `output/stage4/triage_vN.md`. Only `[FIX]` items feed into the theory-generator for revision. The rest are held for Stage 5 (paper-writer) or the response letter.
5. Commit: `artifact: concern triage v{N}`

### Gate 4: Scorer Decision

**Agents:** `scorer` + `scorer-freeform` (launched in parallel — neither sees the other's output)

1. Launch both scorers in parallel with the same inputs:
   - Theory draft: `output/stage2/theory_draft_vN.md`
   - Math audit (structured): `output/stage2/math_audit_vN.md`
   - Math audit (free-form): `output/stage2/freeform_audit_vN.md`
   - Theory exploration: `output/stage3a/exploration.md` (if available — computational verification and diagnostic plots)
   - Novelty check (idea): `output/stage1/novelty_check_idea.md`
   - Novelty check (theory): `output/stage2/novelty_check_vN.md`
   - Self-attack: `output/stage4/self_attack_vN.md`
2. Save results to `output/stage4/scorer_decision_vN.md` and `output/stage4/scorer_freeform_vN.md`
3. Commit: `artifact: scorer decisions v{N} (structured + freeform)`

**Agent:** `branch-manager`

4. Launch branch-manager with:
   - Theory draft: `output/stage2/theory_draft_vN.md`
   - Both scorer outputs: `output/stage4/scorer_decision_vN.md`, `output/stage4/scorer_freeform_vN.md`
   - Full score history from `process_log/pipeline_state.json`
   - Stage 1 idea sketches: all `output/stage1/idea_sketches_r*.md` files (all rounds, not just r1)
   - Pipeline state: `process_log/pipeline_state.json`
   - Self-attack + triage: `output/stage4/self_attack_vN.md`, `output/stage4/triage_vN.md`
   - Free-form audit: `output/stage2/freeform_audit_vN.md`
   - Literature map: `output/stage0/literature_map.md`
5. Save result to `output/stage4/branch_manager_vN.md`
6. Commit: `artifact: branch-manager report v{N}`
7. Read the branch-manager report. The gate decision must be consistent with its recommendation. If you disagree, log the disagreement and your reasoning in the commit message — do not silently override.

8. Read the scorer output. It contains two sections:
   - **Content score + content feedback**: determines the gate decision. Only substantive theory issues (new math needed, proofs to fix, mechanisms to clarify).
   - **Presentation notes**: expositional improvements (reframe abstract, soften claims, reorder sections). These do NOT affect the score or gate decision. Save them — they are forwarded to the paper-writer at Stage 5.
9. Use the **content score** for state-dependent escalation:

**Scoring is absolute** — 80 means top-5 journal quality regardless of target. The advance threshold depends on the target journal tier. Default tiers:

| Target tier | Examples | Advance | Revise | Rework | Abandon |
|-------------|----------|---------|--------|--------|---------|
| **top-5** | AER, JF, Econometrica, QJE, JPE, ReStud, JFE, RFS | 75+ | 55-74 | 35-54 | <35 |
| **field** | JME, JFQA, Rev Finance, Management Science, RED | 65+ | 45-64 | 30-44 | <30 |
| **letters** | Economics Letters, Finance Research Letters | 55+ | 40-54 | 25-39 | <25 |

**1st scorer evaluation** (no prior score): use band logic from the table above.

**Subsequent scorer evaluations** (has prior score): use score trajectory.

| Condition | Action |
|-----------|--------|
| Score ≥ advance threshold | **ADVANCE** — always, regardless of trajectory |
| Score < abandon threshold | **ABANDON** — always, regardless of trajectory |
| Delta ≥ 3 points | **CONTINUE** — one more iteration in current band (improving, worth continuing) |
| Delta < 3 points | **ESCALATE** — move up one level: REVISE → MAJOR REWORK → ABANDON (plateau, not converging) |
| Score < (advance threshold + 5) on attempt 3+ | **ESCALATE** — regardless of delta. Still below the bar after two revisions suggests a ceiling. Regenerate. |

**Hard ceiling:** After 8 total scorer evaluations on same problem, escalate one level regardless of trajectory.

Record all content scores in `process_log/pipeline_state.json` under `"scores"` so the trajectory can be computed: `"scores": { "v1": 60, "v2": 63, "v3": 67 }`.

10. If REVISE/REWORK: pass only the **content feedback** to the theory-generator. Do NOT pass presentation notes — those are for the paper-writer.
11. Update `process_log/pipeline_state.json` accordingly
12. Commit: `pipeline: gate 4 — scorer {DECISION} (score: {N})`

---

## Stage 5: Paper Writing

**Agent:** `paper-writer`

1. **Paper outline.** Launch paper-writer with instruction: "Write an outline only — do not write LaTeX yet." Provide: theory draft, literature map, scorer assessment (including the **presentation notes** section — the paper-writer must address these), self-attack report. The paper-writer produces `paper/outline.md` with: section-by-section plan, what goes where, how to address self-attack weaknesses, how to incorporate scorer presentation notes, which results to highlight, target length per section.
2. **Review the outline.** Check: does it address the self-attack points? Is the positioning against the literature accurate? Is the structure appropriate for the target journal? If not, provide feedback and re-launch.
3. **Write.** Launch paper-writer with the approved outline + all inputs. Paper-writer creates files in `paper/sections/`:
   - `introduction.tex`
   - `model.tex`
   - `results.tex`
   - `discussion.tex`
   - `conclusion.tex`
   - `appendix.tex` (if needed)
3. Paper-writer creates `paper/main.tex` with `\input` commands
4. Commit: `pipeline: stage 5 — paper draft written`

---

## Stage 6: Referee Simulation

**Agents:** `referee` + `referee-freeform` (launched in parallel — neither sees the other's output)

1. Delete any previous reports in `paper/referee_reports/`
2. Launch both referees in parallel (fresh context, no knowledge of development process). Provide save paths: structured → `paper/referee_reports/YYYY-MM-DD_vN.md`, freeform → `paper/referee_reports/YYYY-MM-DD_vN_freeform.md`
3. Commit after both complete
4. Commit: `pipeline: stage 6 — referee reports received (structured + freeform)`

### Gate 5: Referee Decision

Read both referee reports. The structured referee provides numbered comments with action tags; the free-form referee provides editorial assessment and publishability verdict. Use both to inform the decision:

| Recommendation | Action |
|---------------|--------|
| **Accept / Minor Revision** | Fix minor comments, proceed to Stage 7 (style check). |
| **Major Revision / Revise and Resubmit** | **Triage first.** Categorize each referee comment using the referee's own tags (`[FIX]`/`[LIMITS]`/`[RESPONSE]`/`[NOTE]`) as a starting point. Only `[FIX]` items trigger main-text revisions. `[LIMITS]` items get one sentence in limitations. `[RESPONSE]` items go in the response letter only. Save triage to `paper/referee_reports/triage_rN.md`. Then revise only the `[FIX]` items. When a referee challenges an assumption, first try to prove the result without it or characterize exactly when it fails — weakening claims is the last resort (per "characterize, don't just prove"). Re-run Stage 6. Max 10 rounds; keep going as long as each round surfaces at least one genuinely new issue (not a variant of a previously-triaged concern). |
| **Reject** | Read the rejection reasons. If fixable: return to Stage 2 with referee feedback. If fundamental: return to Stage 0. |

---

## Stage 7: Style Check

**Agent:** `style`

1. Launch style agent on the paper
2. Read the style report
3. Fix all violations by editing the section files directly
4. Commit: `pipeline: stage 7 — style violations fixed`
5. Update `process_log/pipeline_state.json` with `"status": "complete"`. Final commit: `pipeline: COMPLETE — paper ready for submission`

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

{{SCORING}}

---

## Paper Writing Style Guide

These rules apply when writing paper drafts.

- Active voice always. Passive voice is the enemy.
- No filler before "that": "It should be noted that X" → "X"
- No self-congratulatory adjectives (striking, novel, important)
- Clothe the naked "this" — always follow with a noun
- No em-dashes; use commas, colons, periods, or parentheses
- Don't "assume" model structure — state it: "Consumers have power utility"
- "I" is fine, but "I show that X" → just say X
- Make the object the subject: "Table 5 presents estimates" not "I present estimates in Table 5"
- No royal "we" — "we" means "you the reader and I"
- Simple words: "use" not "utilize," "several" not "diverse"
- No "I leave X for future research"
- Let the content speak for itself

---

{{RUNTIME_SESSION_GUIDANCE}}

---

## Documentation

The **scribe** agent runs in the background after each stage, logging:
- What happened (discussions, decisions)
- What was tried and failed (dead ends)
- The full pipeline history (`process_log/history.md`)

The scribe's role is pedagogical — recording the process for the AI-assisted research guide.
