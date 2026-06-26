# Stage 0: Problem Discovery

**On every Stage 0 (re-)entry (each begins a fresh problem; every `problem_attempt` increment routes through a Stage 0 entry, so this entry hook is the single authoritative reset site): reset the problem-scoped Stage-1 state in `pipeline_state.json`:**
- Reset `regeneration_round` to `0` if non-zero. Regeneration is scoped to a single problem; a new problem starts with a clean slate.
- Reset `harder_round_forced` to `false`. The Stage-1 portfolio guard (`docs/stage_1.md` Step 2a) gets a fresh once-per-problem budget.
- Reset `fallback_idea_sketch_name` to `null` and ignore any stale `output/stage1/fallback_*.md`. (If this re-entry is an *automatic* abandonment — 5-round cap exhausted or Gate 1 REJECT ALL — the Step 2a "fallback rescue" should already have shipped a non-null fallback instead of letting control reach here; this reset is the backstop for the *deliberate* Stage-0 re-entries, e.g. branch-manager's empirical-first REENTER-STAGE-0, where abandoning the prior problem's fallback is intended.)
- Reset `gate0_revise_cycles` to `0`, `gate0_questions_rejected` to `0`, `gate0_best_question_score` to `-1`, and `gate0_rescanned` to `false` (and ignore any stale `output/stage0/best_question*.md`). These count the Gate-0 (Step 0e) REVISE cycles on the current gap and the questions rejected across gaps within this Stage-0 pass, snapshot the best question seen so far, and track whether the once-per-pass adjacent-domain re-scan (Step 0b scan-exhausted branch) has been used; a fresh problem-discovery pass starts them clean (see Step 0e routing).
- Clear `output/stage0/gap_log.md` (start an empty gap log — a fresh problem-discovery pass has no gaps tried). The log records each gap that is **closed**, **no-stake**, **weak-stake**, or **rejected** so Step 0b does not re-pick it; it accumulates within this pass and survives a crash/resume on disk.

## Step 0a: Broad literature scan

**Agent:** `literature-scout`

1. Choose a domain within {{DOMAIN_AREAS}}
2. Launch literature-scout to search for open questions, puzzles, or gaps
3. Save results to `output/stage0/literature_map_broad.md`
4. Commit: `artifact: broad literature scan`

## Step 0b: Pre-select a gap

**Scan-exhausted check (do this first):** if `output/stage0/gap_log.md` already accounts for every gap from the broad scan so no untried gap remains, do **not** loop — when `gate0_best_question_score >= 0`, apply the Step 0e REJECT-cap fallback now (restore `output/stage0/best_question.md` → `problem_statement.md` and `output/stage0/best_question_review.md` → `question_review.md`, commit `pipeline: gate 0 — cap reached, taking best question (score {gate0_best_question_score})`, and proceed to Stage 1 with it). When `gate0_best_question_score == -1` (no question was ever scored this pass): if `gate0_rescanned` is `false`, set it `true` and re-run Step 0a once for a fresh broad scan on an adjacent domain, then continue; if `gate0_rescanned` is already `true` (the one re-scan this pass still produced no scored question), treat this as a problem-discovery failure and follow the orchestrator's standard abandonment/escalation path.

Read the broad map + `output/data_inventory.md` (if it exists) + `output/stage0/gap_log.md` (if it exists — skip any gap already logged there as closed, no-stake, weak-stake, or rejected). Pick the most promising **untried** gap area, considering: **field stake** (is there a standing prior, consensus, or live debate so an answer would inform the field *whichever way it resolves* — or a consequential absence where no framework exists at all, so any answer changes practice or beliefs, Markowitz-style), gap size, tractability, data availability. Openness is necessary but not sufficient: among open gaps, prefer high field stake. Stake is not crowdedness: an untested assumption the field universally holds, or a consequential absence of any framework, is ideal (high stake, wide open); avoid a gap that is open only because no one would care about the answer. Stake is independent of difficulty: a hard gap that has resisted past attempts is still high-stake if a standing prior or consequential absence rides on the answer. Write the selection (a few sentences, naming the field stake) to `output/stage0/gap_selection.md`.

## Step 0c: Deep search on the gap

**Agent:** `gap-scout`

1. Launch gap-scout with the broad map, the gap selection, and the data inventory
2. Save results to `output/stage0/literature_map.md` (this is the canonical map used downstream)
3. Commit: `artifact: deep literature map`
4. If the gap-scout reports the gap is **closed**: append the gap name + `closed` to `output/stage0/gap_log.md`, return to Step 0b, pick the next most promising untried gap from the broad scan, re-run Step 0c
5. If the gap-scout reports **No** field stake (nothing rides on the answer either way): append the gap name + `no-stake` to `output/stage0/gap_log.md`, then treat as if closed — return to Step 0b and pick the next most promising untried gap. If field stake is **Weak**: note it in `gap_selection.md`, append the gap name + `weak-stake` to `output/stage0/gap_log.md`, and continue.

{{SEED_OVERRIDE_STAGE_0_STEP_0C}}

## Step 0d: Pose the sharp question

**Agent:** `question-poser`

The question is the pipeline's generative primitive. Stage 0 owns it: the poser turns the validated gap into one sharp research question; Stage 1 will generate *approaches* that answer it. (This mirrors the Stage 1 generator→evaluator pairing — `question-poser` → `question-referee` here, `idea-generator` → `idea-reviewer` there.)

**Seeded / faithful mode bypass.** In `--seed` and `--faithful` runs the seed *is* the question, so `question-poser` (this step) and the Gate-0 `question-referee` vetting (Step 0e) are **not launched** — the `seed_triage` entry procedure (the "Stage: Seed Triage" section of your runtime doc, e.g. CLAUDE.md) back-fills `output/stage0/problem_statement.md` directly from the seed (faithful: reproducing the contract's question verbatim), and the pipeline enters at the appropriate downstream stage. Do not pose a fresh question from the literature map in seeded mode; that would let an unconstrained poser drift off the committed seed.

1. Launch `question-poser` with `output/stage0/literature_map.md` (the canonical deep map), `output/stage0/gap_selection.md`, and `output/data_inventory.md` (if it exists).
2. The agent poses **one** sharp question and pre-argues the four axes (important · unsolved · not-obvious · interesting-either-way) for the referee to vet. It saves `output/stage0/problem_statement.md`. Requirements the body enforces (re-check on return):
   - References the data inventory (if it exists)
   - Names the closest competitor identified by the gap-scout (or notes the gap-scout's missing-framework finding if there is no single competitor)
   - Argues **interesting either way** — names what the field learns under each plausible answer, flagging any dead branch
   - Does **NOT** specify a theoretical framework, mechanism, estimator, or candidate answer — choosing the approach is Stage 1's job, and pre-committing one here forecloses the search.
3. Commit: `pipeline: stage 0 — question posed`

## Step 0e: Question Viability (Gate 0)

**Agent:** `question-referee`

This **replaces the former orchestrator-self-graded Gate 0** — the orchestrator scoring its own problem statement was the same self-referential evaluation flaw as #102, at the very top of the pipeline. The `question-referee` is search-grounded and independent: it confirms openness and non-obviousness against the actual literature, not the poser's say-so. (Bypassed in seeded / faithful mode — see the bypass note under Step 0d.)

1. Launch `question-referee` with `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md` (if it exists).
2. The agent scores the question on **important · unsolved · not-obvious** (three binding axes), with an **answerable** floor and an advisory **interesting-either-way** axis (a dead branch routes to REVISE, never REJECT — see the question-referee body), produces a 0–100 viability score and a verdict, and saves `output/stage0/question_review.md`.
3. **Snapshot the best question seen so far.** If this evaluation's viability score `N` is greater than `gate0_best_question_score` (initialized `-1`, so the first question always wins), copy `output/stage0/problem_statement.md` → `output/stage0/best_question.md` and `output/stage0/question_review.md` → `output/stage0/best_question_review.md`, and set `gate0_best_question_score = N`. Do this on **every** verdict (ADVANCE / REVISE / REJECT) before routing — "best seen so far across all gaps this pass" must include questions that were sharpened or rejected, not just the one that finally advances. (This is what makes the REJECT cap-5 fallback below executable: without the snapshot, each gap overwrites `problem_statement.md` and the best-scoring question is lost.)
4. Commit: `pipeline: gate 0 — question review ({verdict}, score {N})`
5. Route on the verdict. The two caps below are tracked in `pipeline_state.json` so they survive a crash/resume (both are reset on every Stage 0 (re-)entry per the reset hook at the top of this doc):

| Verdict | Action |
|---------|--------|
| **ADVANCE** | The question is vetted. Proceed to Stage 1 — `idea-generator` generates solution approaches to this fixed question. |
| **REVISE** | Fixable sharpening. If `gate0_revise_cycles >= 3`, do **not** revise again — treat this as REJECT (route to the REJECT row). Otherwise: increment `gate0_revise_cycles`; re-launch `question-poser` with the referee's "required changes" section quoted in the prompt; re-run this gate (0e) on the sharpened question. (Three REVISE cycles per gap.) |
| **REJECT** | The question on this gap is not worth pursuing. Increment `gate0_questions_rejected` and reset `gate0_revise_cycles` to `0` (a new gap gets a fresh REVISE budget). If `gate0_questions_rejected >= 5`, stop searching: take the best question seen so far — restore the snapshot by copying `output/stage0/best_question.md` → `output/stage0/problem_statement.md` (and `best_question_review.md` → `question_review.md` for the log), commit `pipeline: gate 0 — cap reached, taking best question (score {gate0_best_question_score})`, and proceed to Stage 1 with it. (The snapshot is guaranteed non-empty: step 3 above writes it on the first evaluation, so `gate0_best_question_score >= 0` by the time the 5th REJECT lands.) Otherwise append the gap name + `rejected` to `output/stage0/gap_log.md`, return to Step 0b, pick the next most promising **untried** gap from the broad scan, and re-run Steps 0c–0e. |

Note: viability is governed by the three binding quality axes (important, unsolved, not-obvious); **interesting-either-way** is advisory and never drives REJECT on its own (a dead branch is a REVISE). **Answerable** is a floor, never a difficulty penalty — a hard question that needs a non-obvious approach is exactly what a top question looks like, and cracking it is Stage 1's job, not grounds to fail it here.
