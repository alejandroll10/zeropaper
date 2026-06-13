# Stage 0: Problem Discovery

**On every Stage 0 (re-)entry (each begins a fresh problem; every `problem_attempt` increment routes through a Stage 0 entry, so this entry hook is the single authoritative reset site): reset the problem-scoped Stage-1 state in `pipeline_state.json`:**
- Reset `regeneration_round` to `0` if non-zero. Regeneration is scoped to a single problem; a new problem starts with a clean slate.
- Reset `harder_round_forced` to `false`. The Stage-1 portfolio guard (`docs/stage_1.md` Step 2a) gets a fresh once-per-problem budget.
- Reset `fallback_idea_sketch_name` to `null` and ignore any stale `output/stage1/fallback_*.md`. (If this re-entry is an *automatic* abandonment — 5-round cap exhausted or Gate 1 REJECT ALL — the Step 2a "fallback rescue" should already have shipped a non-null fallback instead of letting control reach here; this reset is the backstop for the *deliberate* Stage-0 re-entries, e.g. branch-manager's empirical-first REENTER-STAGE-0, where abandoning the prior problem's fallback is intended.)

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

## Step 0d: Problem statement

Write `output/stage0/problem_statement.md`. Requirements:
- Must reference the data inventory (if it exists)
- Must name the closest competitor identified by the gap-scout
- Must NOT specify a theoretical framework — that is the idea-generator's job
- Commit: `pipeline: stage 0 — problem statement written`

## Gate 0: Problem Viability

The orchestrator (you) evaluates:
- Is this question important enough for a top journal?
- Is there actually a gap? (The gap-scout's gap status is the primary evidence.)
- Is it tractable as a pure theory paper?
- Is the closest competitor correctly identified?
- Is the idea space left open? (If the problem statement pre-commits to a specific framework, that is a Gate 0 failure — rewrite it.)

Score 0-100. If below 50, return to Step 0b with a different gap. After 5 failures, pick the best problem and proceed.
