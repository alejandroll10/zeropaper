# Stage 0: Problem Discovery

**On every Stage 0 (re-)entry (each begins a fresh problem; every `problem_attempt` increment routes through a Stage 0 entry, so this entry hook is the single authoritative reset site): reset the problem-scoped Stage-1 state in `pipeline_state.json`:**
- Reset `regeneration_round` to `0` if non-zero. Regeneration is scoped to a single problem; a new problem starts with a clean slate.
- Reset `harder_round_forced` to `false`. The Stage-1 portfolio guard (`docs/stage_1.md` Step 2a) gets a fresh once-per-problem budget.
- Reset `fallback_idea_sketch_name` to `null` and ignore any stale `output/stage1/fallback_*.md`. (If this re-entry is an *automatic* abandonment — 5-round cap exhausted or Gate 1 REJECT ALL — the Step 2a "fallback rescue" should already have shipped a non-null fallback instead of letting control reach here; this reset is the backstop for the *deliberate* Stage-0 re-entries, e.g. branch-manager's empirical-first REENTER-STAGE-0, where abandoning the prior problem's fallback is intended.)
- Reset `gate0_revise_cycles` to `0` and `gate0_questions_rejected` to `0`. These count the Gate-0 (Step 0e) REVISE cycles on the current gap and the questions rejected across gaps within this Stage-0 pass; a fresh problem-discovery pass starts both at zero (see Step 0e routing).

## Step 0a: Broad literature scan

**Agent:** `literature-scout`

1. Choose a domain within {{DOMAIN_AREAS}}
2. Launch literature-scout to search for open questions, puzzles, or gaps
3. Save results to `output/stage0/literature_map_broad.md`
4. Commit: `artifact: broad literature scan`

## Step 0b: Pre-select a gap

Read the broad map + `output/data_inventory.md` (if it exists). Pick the most promising gap area, considering: gap size, tractability, data availability, room between existing papers. Write the selection (a few sentences) to `output/stage0/gap_selection.md`.

## Step 0c: Deep search on the gap

**Agent:** `gap-scout`

1. Launch gap-scout with the broad map, the gap selection, and the data inventory
2. Save results to `output/stage0/literature_map.md` (this is the canonical map used downstream)
3. Commit: `artifact: deep literature map`
4. If the gap-scout reports the gap is **closed**: return to Step 0b, pick the next most promising gap from the broad scan, re-run Step 0c

{{SEED_OVERRIDE_STAGE_0_STEP_0C}}

## Step 0d: Pose the sharp question

**Agent:** `question-poser`

The question is the pipeline's generative primitive. Stage 0 owns it: the poser turns the validated gap into one sharp research question; Stage 1 will generate *approaches* that answer it. (This mirrors the Stage 1 generator→evaluator pairing — `question-poser` → `question-referee` here, `idea-generator` → `idea-reviewer` there.)

**Seeded / faithful mode bypass.** In `--seed` and `--faithful` runs the seed *is* the question, so `question-poser` (this step) and the Gate-0 `question-referee` vetting (Step 0e) are **not launched** — the `seed_triage` entry procedure (the "Stage: Seed Triage" section of your runtime doc, e.g. CLAUDE.md) back-fills `output/stage0/problem_statement.md` directly from the seed (faithful: reproducing the contract's question verbatim), and the pipeline enters at the appropriate downstream stage. Do not pose a fresh question from the literature map in seeded mode; that would let an unconstrained poser drift off the committed seed.

1. Launch `question-poser` with `output/stage0/literature_map.md` (the canonical deep map), `output/stage0/gap_selection.md`, and `output/data_inventory.md` (if it exists).
2. The agent poses **one** sharp question and pre-argues the three axes (important · unsolved · not-obvious) for the referee to vet. It saves `output/stage0/problem_statement.md`. Requirements the body enforces (re-check on return):
   - References the data inventory (if it exists)
   - Names the closest competitor identified by the gap-scout
   - Does **NOT** specify a theoretical framework, mechanism, estimator, or candidate answer — choosing the approach is Stage 1's job, and pre-committing one here forecloses the search.
3. Commit: `pipeline: stage 0 — question posed`

## Step 0e: Question Viability (Gate 0)

**Agent:** `question-referee`

This **replaces the former orchestrator-self-graded Gate 0** — the orchestrator scoring its own problem statement was the same self-referential evaluation flaw as #102, at the very top of the pipeline. The `question-referee` is search-grounded and independent: it confirms openness and non-obviousness against the actual literature, not the poser's say-so. (Bypassed in seeded / faithful mode — see the bypass note under Step 0d.)

1. Launch `question-referee` with `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md` (if it exists).
2. The agent scores the question on **important · unsolved · not-obvious** (with an **answerable** floor), produces a 0–100 viability score and a verdict, and saves `output/stage0/question_review.md`.
3. Commit: `pipeline: gate 0 — question review ({verdict}, score {N})`
4. Route on the verdict. The two caps below are tracked in `pipeline_state.json` so they survive a crash/resume (both are reset to `0` on every Stage 0 (re-)entry per the reset hook at the top of this doc):

| Verdict | Action |
|---------|--------|
| **ADVANCE** | The question is vetted. Proceed to Stage 1 — `idea-generator` generates solution approaches to this fixed question. |
| **REVISE** | Fixable sharpening. If `gate0_revise_cycles >= 3`, do **not** revise again — treat this as REJECT (route to the REJECT row). Otherwise: increment `gate0_revise_cycles`; re-launch `question-poser` with the referee's "required changes" section quoted in the prompt; re-run this gate (0e) on the sharpened question. (Three REVISE cycles per gap.) |
| **REJECT** | The question on this gap is not worth pursuing. Increment `gate0_questions_rejected` and reset `gate0_revise_cycles` to `0` (a new gap gets a fresh REVISE budget). If `gate0_questions_rejected >= 5`, stop searching: pick the highest viability-scored question seen so far across all gaps this pass and proceed to Stage 1 with it. Otherwise return to Step 0b, pick the next most promising gap from the broad scan, and re-run Steps 0c–0e. |

Note: viability is governed by the three quality axes; **Answerable** is a floor, never a difficulty penalty — a hard question that needs a non-obvious approach is exactly what a top question looks like, and cracking it is Stage 1's job, not grounds to fail it here.
