# CLAUDE.md — Autonomous Theory Paper Pipeline

## Purpose

This project autonomously produces a **{{PAPER_TYPE}}** suitable for submission to a {{TARGET_JOURNALS}}. The system runs end-to-end with no human intervention after launch. Quality is enforced by adversarial evaluation at every stage.

The project also produces a **process log** documenting how the autonomous system worked, as a pedagogical record.

---

## How to use

### First time: set up a new project

Open an empty folder in Cursor (or any editor), start Claude Code, and say:

```
Clone the research template and set up.
```

This clones `https://github.com/alejandroll10/auto-ai-research-template.git` into the current folder, initializes pipeline state, and creates a git repo. After this, all template files are visible in your editor's file tree.

### Run the pipeline

```
Run the pipeline.
```

The system reads this file, checks `process_log/pipeline_state.json`, and continues from where it left off. No human input needed after this point.

### Resume after interruption

If the session ends mid-pipeline, start Claude Code again and say "Run the pipeline." The system reads pipeline state and picks up from the last completed stage.

### Watch progress

**Dashboard:** Open a terminal in the project folder and run:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/dashboard.html` in a browser. The dashboard auto-refreshes every 5 seconds, showing the current stage, scores, gate results, and full event history.

**Files:** All output files appear in real time:
- `output/stage0/` — problem discovery results
- `output/stage1/` — idea sketches, reviews, selected idea
- `output/stage2/` — theory drafts, audits, novelty checks
- `output/stage3/` — implications
- `output/stage4/` — self-attack, scorer decisions
- `paper/sections/` — LaTeX paper sections
- `process_log/` — full narrative log

**Git:** Commits happen compulsively after every action (`git log --oneline` shows the full history).

---

## Pipeline overview

```
Stage 0: Problem Discovery   ──→ Gate 0: Problem Viability
Stage 1: Idea Generation     ──→ Gate 1: Idea Review (iterates with generator)
                                   └── ADVANCE → best idea selected
                                Gate 1b: Novelty Check on idea
                                   ├── KNOWN → kill idea, back to Stage 1
                                   ├── INCREMENTAL → flag, proceed with caution
                                   └── NOVEL → proceed to Stage 2
Stage 2: Theory Development  ──→ Gate 2: Math Audit (structured then free-form)
                                   Gate 3: Novelty Check on full theory
Stage 3: Implications        ──→
Stage 4: Self-Attack          ──→ Gate 4: Scorer Decision (trajectory-based)
                                   ├── ADVANCE (75+) → Stage 5
                                   ├── REVISE  → back to Stage 2 (continue if Δ≥3, else escalate)
                                   ├── REWORK  → back to Stage 1 (continue if Δ≥3, else escalate)
                                   └── ABANDON → back to Stage 0 (max 3×)
Stage 5: Paper Writing        ──→
Stage 6: Style Check          ──→
Stage 7: Referee Simulation   ──→ Gate 5: Referee Decision
                                   ├── Minor/Accept → Done
                                   ├── Major Revision → back to Stage 5 (max 2×)
                                   └── Reject → back to Stage 1
```

---

## Pipeline state

State is tracked in `process_log/pipeline_state.json`. Read this file at session start. Update it after every stage transition. Commit after every update.

```json
{
  "current_stage": "stage_0",
  "problem_attempt": 1,
  "idea_round": 0,
  "theory_attempt": 1,
  "revision_round": 0,
  "referee_round": 0,
  "status": "running",
  "scores": {},
  "history": [
    {
      "timestamp": "2026-03-17T14:00:00Z",
      "event": "Pipeline started — entering stage 0"
    }
  ]
}
```

**History array:** Append a `{ "timestamp": "ISO-8601", "event": "description" }` entry for every pipeline event. This feeds the dashboard. Use `date -u +%Y-%m-%dT%H:%M:%SZ` to get the timestamp. Never truncate or clear the history array.

---

## Stage 0: Problem Discovery

**Agent:** `literature-scout`

1. Choose a domain within {{DOMAIN_AREAS}}
2. Launch literature-scout to search for open questions, puzzles, or gaps
3. Save results to `output/stage0/literature_map.md`
4. Write a problem statement to `output/stage0/problem_statement.md`
5. Commit: `pipeline: stage 0 complete — problem identified`

### Gate 0: Problem Viability

The orchestrator (you) evaluates:
- Is this question important enough for a top journal?
- Is there actually a gap?
- Is it tractable as a pure theory paper?

Score 0-100. If below 50, re-run Stage 0 with different search terms. After 3 failures, pick the best problem and proceed.

---

## Stage 1: Idea Generation

**Agents:** `idea-generator` + `idea-reviewer` (iterating)

1. Read `output/stage0/problem_statement.md` and `output/stage0/literature_map.md`
2. Launch idea-generator to brainstorm 3-5 candidate mechanisms
3. Save sketches to `output/stage1/idea_sketches_rN.md` (N = round number)
4. Commit: `artifact: idea sketches round {N}`

### Gate 1: Idea Review

**Agent:** `idea-reviewer`

1. Launch idea-reviewer on the sketches + problem statement + literature map
2. Save review to `output/stage1/idea_review_rN.md`
3. Commit: `artifact: idea review round {N}`
4. Read the decision:

| Decision | Action |
|----------|--------|
| **ADVANCE** | Best idea identified. Proceed to Stage 2 with the reviewer's instructions for theory development. |
| **ITERATE** | Re-launch idea-generator with the reviewer's feedback. Max 3 rounds of iteration. |
| **REJECT ALL** | All ideas are weak. Return to Stage 0 for a different problem. |

5. After 3 rounds without ADVANCE, pick the highest-scored idea and advance it anyway.
6. Save the winning idea summary to `output/stage1/selected_idea.md`
7. Commit: `artifact: selected idea saved`

### Gate 1b: Novelty Check on Selected Idea

**Agent:** `novelty-checker`

This is the first of two deep novelty checks. It runs on the selected idea *before* investing in theory development.

1. Launch novelty-checker on `output/stage1/selected_idea.md` + `output/stage0/literature_map.md`
2. Save result to `output/stage1/novelty_check_idea.md`
3. Read the verdict:

| Verdict | Action |
|---------|--------|
| **KNOWN** | Kill this idea. Pick the next-best idea from the current round's sketches (per idea-reviewer rankings) and re-run Gate 1b on it. If no viable ideas remain in the current round, re-run Stage 1 with a new round of idea generation (counts toward the 3-round limit). |
| **INCREMENTAL** | Flag it. Proceed to Stage 2 but the scorer will weigh this at Gate 4. |
| **NOVEL** | Proceed to Stage 2. |

4. Commit: `pipeline: gate 1b — novelty check on idea {NOVEL/INCREMENTAL/KNOWN}`
5. Update pipeline_state.json and commit: `pipeline: stage 1 complete — idea selected and novelty-checked`

---

## Stage 2: Theory Development

**Agent:** `theory-generator`

1. Read `output/stage1/selected_idea.md`, `output/stage0/problem_statement.md`, and `output/stage0/literature_map.md`
2. Choose strategy:
   - Attempt 1: develop the selected idea into a full theory
   - Attempt 2+: mutate (if previous attempt had good elements) or fresh with different approach
3. Launch theory-generator with the selected idea, problem statement, literature map, and strategy
4. Save result to `output/stage2/theory_draft_vN.md` (N = attempt number)
5. Commit: `artifact: theory draft v{N}`

### Gate 2: Math Audit (structured + free-form)

**Agents:** `math-auditor` then `math-auditor-freeform`

Two audits run sequentially. The structured audit checks every derivation step-by-step. The free-form audit reads the theory as a skeptical reader and catches conceptual issues that step-by-step verification misses. Both must PASS before advancing.

**Step 1: Structured audit**

1. Launch math-auditor on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/math_audit_vN.md`
3. Commit: `artifact: math audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the specific errors from the audit
   - Re-launch theory-generator in **mutate** mode with the draft + audit feedback
   - Max 3 audit attempts per theory version
   - If still failing after 3: treat as theory failure, increment theory_attempt
5. If PASS: proceed to Step 2

**Step 2: Free-form audit**

1. Launch math-auditor-freeform on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/freeform_audit_vN.md`
3. Commit: `artifact: freeform audit v{N} — {PASS/FAIL}`
4. If FAIL:
   - Read the concerns from the free-form audit
   - Re-launch theory-generator in **mutate** mode with the draft + free-form audit feedback
   - After mutation, re-run **both** audits from Step 1 (the fix may have introduced new algebraic errors)
   - This counts toward the same max 3 audit attempts per theory version
5. If PASS: proceed to Gate 3

### Gate 3: Novelty Check on Full Theory

**Agent:** `novelty-checker`

This is the second of two deep novelty checks. The idea was already checked at Gate 1b, but the full theory may overlap with prior work in ways the sketch did not reveal — the mechanism may be novel while the result is not, or the developed model may converge to a known framework.

1. Launch novelty-checker on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/novelty_check_vN.md`
3. If KNOWN: abandon this theory, return to Stage 2 with new approach
4. If INCREMENTAL: flag it, proceed with caution (scorer will weigh this)
5. If NOVEL: proceed to Stage 3
6. Commit: `artifact: novelty check v{N} — {NOVEL/INCREMENTAL/KNOWN}`

---

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

---

## Stage 3b/3c: LLM Experiments (optional — finance_llm variant only)

**These stages run only if** `llm_client.py` exists in the project root and `experiment-designer` agent exists in `.claude/agents/`. If not present, skip to Stage 4.

If present, read `STAGES.md` for full instructions. Summary:

1. **Stage 3b:** Launch `experiment-designer` to design and run experiments testing theoretical predictions via gpt-oss models
2. **Stage 3c:** Launch `experiment-reviewer` to evaluate methodology and results
3. If ACCEPT: proceed to Stage 4 (self-attacker receives experiment results too)
4. If REVISE/REDESIGN: iterate (max 2 rounds), then proceed

---

## Stage 4: Self-Attack

**Agent:** `self-attacker`

1. Launch self-attacker on the theory draft + implications
2. Save result to `output/stage4/self_attack_vN.md`
3. Commit: `artifact: self-attack v{N}`

### Gate 4: Scorer Decision

**Agent:** `scorer`

1. Launch scorer with:
   - Theory draft: `output/stage2/theory_draft_vN.md`
   - Math audit (structured): `output/stage2/math_audit_vN.md`
   - Math audit (free-form): `output/stage2/freeform_audit_vN.md`
   - Novelty check (idea): `output/stage1/novelty_check_idea.md`
   - Novelty check (theory): `output/stage2/novelty_check_vN.md`
   - Self-attack: `output/stage4/self_attack_vN.md`
2. Save result to `output/stage4/scorer_decision_vN.md`
3. Read the decision using **state-dependent escalation**:

**First scorer evaluation** (no prior score): use band logic.

| Decision | Action |
|----------|--------|
| **ADVANCE** (75+) | Proceed to Stage 5 |
| **REVISE** (55-74) | Return to Stage 2 in mutate mode with scorer feedback. |
| **MAJOR REWORK** (35-54) | Return to Stage 1 to generate new ideas with scorer feedback. |
| **ABANDON** (<35) | Increment theory_attempt. Return to Stage 1. After 3 abandons on same problem, return to Stage 0. |

**Subsequent scorer evaluations** (has prior score): use score trajectory.

| Condition | Action |
|-----------|--------|
| Score ≥ 75 | **ADVANCE** — always, regardless of trajectory |
| Score < 35 | **ABANDON** — always, regardless of trajectory |
| Delta ≥ 3 points | **CONTINUE** — one more iteration in current band: REVISE returns to Stage 2, MAJOR REWORK returns to Stage 1 (improving, worth continuing) |
| Delta < 3 points | **ESCALATE** — move up one level: REVISE → MAJOR REWORK (Stage 1) → ABANDON (plateau or decline, not converging) |

**Hard ceiling:** After 4 total scorer evaluations on the same problem, escalate one level regardless of trajectory. This prevents slow-but-never-arriving loops (e.g., +3, +3, +3 but still at 69).

Record all scores in `pipeline_state.json` under `"scores"` so the trajectory can be computed: `"scores": { "v1": 60, "v2": 63, "v3": 67 }`.

4. Update pipeline_state.json accordingly
5. Commit: `pipeline: gate 4 — scorer {DECISION} (score: {N})`

---

## Stage 5: Paper Writing

**Agent:** `paper-writer`

1. Launch paper-writer with:
   - Theory draft (latest version)
   - Literature map
   - Scorer assessment
   - Self-attack report (so the paper preemptively addresses weaknesses)
2. Paper-writer creates files in `paper/sections/`:
   - `introduction.tex`
   - `model.tex`
   - `results.tex`
   - `discussion.tex`
   - `conclusion.tex`
   - `appendix.tex` (if needed)
3. Paper-writer updates `paper/main.tex` with `\input` commands
4. Commit: `pipeline: stage 5 — paper draft written`

---

## Stage 6: Style Check

**Agent:** `style`

1. Launch style agent on the paper
2. Read the style report
3. Fix all violations by editing the section files directly
4. Commit: `pipeline: stage 6 — style violations fixed`

---

## Stage 7: Referee Simulation

**Agent:** `referee`

1. Delete any previous reports in `paper/referee_reports/`
2. Launch referee agent (fresh context, no knowledge of development process)
3. Save report to `paper/referee_reports/YYYY-MM-DD_vN.md`
4. Commit: `pipeline: stage 7 — referee report received`

### Gate 5: Referee Decision

Read the referee's recommendation:

| Recommendation | Action |
|---------------|--------|
| **Accept / Minor Revision** | Fix minor comments, commit final version. Pipeline complete. |
| **Major Revision** | Revise the paper addressing major comments. Re-run Stages 6-7. Max 2 referee rounds. |
| **Reject** | Read the rejection reasons. If fixable: return to Stage 2 with referee feedback. If fundamental: return to Stage 0. |

Update pipeline_state.json with `"status": "complete"` when done.

Final commit: `pipeline: COMPLETE — paper ready for submission`

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

## Escalation rules (prevent infinite loops)

| Situation | After N failures | Action |
|-----------|-----------------|--------|
| Idea review iterates | 3 rounds | Pick the best idea and advance to Gate 1b |
| Idea review rejects all | 1 rejection | Return to Stage 0 for a different problem |
| Idea novelty check (Gate 1b) KNOWN | All ideas from current round exhausted | New round of Stage 1 (counts toward 3-round limit) |
| Math audit fails | 3 attempts | Abandon this theory version |
| Scorer: delta ≥ 3 | — | Allow one more iteration in current band |
| Scorer: delta < 3 (plateau/decline) | — | Escalate one level (REVISE → MAJOR REWORK → ABANDON) |
| Scorer: hard ceiling | 4 total evaluations on same problem | Escalate one level from current band regardless of trajectory (REVISE → MAJOR REWORK → ABANDON) |
| Theory scored ABANDON | 3 theories on same problem | Change the problem (Stage 0) |
| Problem viability fails | 3 problems | Pick the best scoring problem and proceed anyway |
| Referee rejects | 2 rejections | Return to Stage 0 with entirely new topic |

---

## File organization

```
dashboard.html              # Live progress dashboard (serve with python3 -m http.server)
output/
├── stage0/
│   ├── problem_statement.md
│   └── literature_map.md
├── stage1/
│   ├── idea_sketches_r1.md
│   ├── idea_review_r1.md
│   ├── idea_sketches_r2.md
│   ├── idea_review_r2.md
│   ├── selected_idea.md
│   └── novelty_check_idea.md    # overwritten if idea is KNOWN and next-best is checked
├── stage2/
│   ├── theory_draft_v1.md
│   ├── theory_draft_v2.md
│   ├── math_audit_v1.md
│   ├── math_audit_v2.md
│   ├── freeform_audit_v1.md
│   ├── freeform_audit_v2.md
│   ├── novelty_check_v1.md
│   └── novelty_check_v2.md
├── stage3/
│   └── implications.md
├── stage4/
│   ├── self_attack_v1.md
│   └── scorer_decision_v1.md
├── post_pipeline/
│   ├── pending_audit_1.md
│   └── audit_result_1.md
paper/
├── main.tex
├── sections/
│   ├── introduction.tex
│   ├── model.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── conclusion.tex
│   └── appendix.tex
├── referee_reports/
│   └── YYYY-MM-DD_v1.md
process_log/
├── pipeline_state.json
├── history.md
├── sessions/
├── discussions/
├── decisions/
└── patterns/
```

---

## Commit protocol — COMPULSIVE COMMITS

**Commit early, commit often.** This pipeline runs autonomously and may be interrupted at any time. Every piece of work that hits disk must be committed immediately so progress is never lost and the dashboard stays current.

### When to commit

- **After every file write.** If you wrote or updated a file, commit it. Do not batch.
- **After every stage transition.** Update `pipeline_state.json` first, then commit.
- **After every gate decision.** The gate result file + updated state = one commit.
- **After every agent output.** When a subagent returns and you save its output, commit immediately.
- **After every edit to the paper.** Each section edit gets its own commit.
- **Before launching a subagent.** If you updated state or wrote input files, commit first so the state on disk matches reality if the session dies mid-agent.

### Commit message format

| Prefix | When |
|--------|------|
| `pipeline:` | Stage transitions, gate decisions, pipeline state changes |
| `artifact:` | Saving agent output (theory drafts, audits, novelty checks, etc.) |
| `paper:` | Paper section writes and edits |
| `scribe:` | Documentation updates (scribe agent) |

Examples:
- `pipeline: stage 0 complete — problem identified`
- `artifact: theory draft v2 saved`
- `artifact: math audit v2 — PASS`
- `pipeline: gate 4 — scorer ADVANCE (score: 78)`
- `paper: introduction.tex written`
- `pipeline: state updated — entering stage 4`

### Rules

- **Never batch commits.** One logical action = one commit.
- **Always update `pipeline_state.json` before committing stage transitions.**
- **Always update `pipeline_state.json` history array** with a timestamped entry for every event, so the dashboard can display progress.
- **If in doubt, commit.** An extra commit costs nothing. Lost work costs everything.

The scribe agent runs in the background and commits with `scribe:` prefix for documentation updates.

---

{{DOMAIN}}

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

## How to start a session

1. Check if CLAUDE.md exists in the current directory
   - If NO: user said "clone the template" → clone the repo into current folder, then:
     - Run `git remote remove origin` (detach from the public template repo so commits stay local)
     - Run `git init` if needed, commit initial state
     - Stop and wait for "Run the pipeline"
   - If YES: continue below
2. If a git remote named `origin` points to `auto-ai-research-template`, remove it: `git remote remove origin`
3. Read `process_log/pipeline_state.json`
   - If `status` is `"not_started"`: set to `"running"`, begin Stage 0
   - If `status` is `"running"`: read `current_stage` and continue from there
   - If `status` is `"complete"`: report that the pipeline is done
4. No human confirmation needed — just run

---

## Documentation

The **scribe** agent runs in the background after each stage, logging:
- What happened (discussions, decisions)
- What was tried and failed (dead ends)
- The full pipeline history (`process_log/history.md`)

The scribe's role is pedagogical — recording the process for the AI-assisted research guide.
