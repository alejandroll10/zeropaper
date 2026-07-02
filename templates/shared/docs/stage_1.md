# Stage 1: Idea Generation

**Agents:** `idea-generator` + `idea-reviewer` (iterating)

**Regeneration round.** A regeneration round fires when the prior theory attempt succeeded but ceilinged in the REVISE band for the current target tier (see `docs/stage_4.md` tier table — e.g., 60-79 for `top-5`, 55-74 for `top-3-fin`, 45-64 for `field`), branch-manager §E recommends Regenerate, and `regeneration_round == 0` for this problem (see `core.md` escalation table). It can be reached from two call sites: the Gate-4 plateau path (`docs/stage_4.md` step 7 §E Regenerate) and the Gate-5 Reject double-cosmetic path (`docs/stage_6.md` Reject row). Both route through the single **Regeneration entry procedure** below, which is the canonical definition of the state transition — the call sites reference it and must not carry their own divergent reset lists.

**Regeneration entry procedure (canonical).** The caller (branch-manager) has already written `output/stage1/learnings_r{N}.md`, where `N` = current `regeneration_round` + 1. The orchestrator then, in one commit, performs this exact transition (`learnings_r{N}.md` and `paper_archive/r{N}/` share the same post-increment `N`):

1. Set `regeneration_round = N` (single increment, matching the learnings file name).
2. **If a paper draft exists (i.e., post-Stage-5):** archive the current paper to `paper_archive/r{N}/` before generation begins, and record its best Gate-4 score as `archived_best_score_r{N}` in pipeline state (defined as `max(scores.values())` from `pipeline_state.json` at archive time — an approximate baseline, since Stage 6 referee revisions can improve the paper without producing a new numeric score). If the new attempt's eventual Gate 4 score does not strictly beat `archived_best_score_r{N}`, restore the archived paper and ship it.
3. **Reset the counter web** so no state bleeds from the abandoned theory into the regenerated one:
   - `theory_attempt → 1`, `theory_version → 1`
   - `referee_round → 0` — the regenerated paper gets its own 10-round Stage 6 budget
   - `reject_cosmetic_round → 0`, `fix_empirics_round → 0`
   - `stage2b_theory_version → null`
   - `stage2_mechanism_version → null` (under `--mode empirical-first` — else `theory_version` resetting to 1 leaves a stale `stage2_mechanism_version = 1` that false-positives the Gate 4 mechanism-plausibility block and silently skips `mechanism-auditor` on the regenerated mechanism; nulling forces it to re-fire)
   - `headline_replication_round → 0` (under `--ext empirical` — the regenerated paper goes through fresh Stage 3a execution; the replicator counter from the abandoned paper must not bleed across)
   - `triaged_lit_implications → []`
4. Re-enter Stage 1: pass `learnings_r{N}.md` to **both** idea-generator and idea-reviewer alongside the lit map, and take the explicit **Regeneration short-circuit** at step 2 below — do not consult the runner-up or unused-sketch priorities; the existing portfolio is by assumption exhausted.

Additional constraints on a regeneration entry:
- Sketches must not repeat any mechanism in `stage1_candidates.sketch_name` or the learnings file's "exhausted mechanisms" list.
- **Banned in seeded mode** — the seed is the contract. Branch-manager must not recommend Regenerate on seeded runs; the escalation row in core.md guards this with "not seeded."

**How many ideas to generate:** More candidates when the pool is weaker — more failures mean more draws needed.

| Context | Ideas per round |
|---------|----------------|
| 1st time entering Stage 1 | 5 |
| Returning from a failed theory (scorer MAJOR REWORK/ABANDON) | 10 |
| Returning from a problem-level failure (Stage 0 re-run) | 10, and explicitly explore different territory |

1. Read `output/stage0/problem_statement.md`, `output/stage0/literature_map.md`, and `output/data_inventory.md`
2. **Regeneration short-circuit:** if `regeneration_round` was just incremented for this re-entry (per the "Regeneration round" section above), skip the priority list below entirely — proceed directly to step 3, launching idea-generator with the learnings file. The runner-up / unused-sketch priorities do not apply on a regeneration entry.

   Otherwise — **if returning from a failed attempt:** first reread all `output/stage1/idea_sketches_r*.md` files AND `pipeline_state.json:stage1_candidates` (which records every sketch previously screened at Gates 1b/1c along with its verdict). **Seeded-mode note:** in seeded mode this step does not apply — the orchestrator never re-nominates a different idea (the seeded-mode overrides at Gate 4 and puzzle-triage block Stage 1 re-entry for idea swapping). The re-entry logic below applies only to non-seeded runs. Selection priority on re-entry:
   1. **Pre-screened runner-up** — an entry with `eliminated: false AND winner: false` (a TRACTABLE survivor that lost the tiebreak in a prior Round). These are already vetted by novelty + prototype and are the strongest fallback. If ≥1 exists, pick the highest-ranked one and **skip idea generation entirely**. To re-advance the runner-up:
      - (a) Start a new Round: increment `idea_round` in `pipeline_state.json` (the runner-up re-advance counts as a Round and is subject to the 5-round cap). Let N = new `idea_round`. Create `output/stage1/round_{N}/` and copy the runner-up's prior indexed file `output/stage1/round_{old_round}/selected_idea_{old_rank}.md` to `output/stage1/round_{N}/selected_idea_1.md` (K=1 for a runner-up re-advance). The prior Round's files remain in place as audit trail.
      - (b) Update the runner-up's `stage1_candidates` entry: set `round: N`, `rank: 1`, and reset `novelty`, `prototype` to `null` (they are about to be re-run). Leave `reviewer_importance` as-is (it is the reviewer's ceiling judgment, not a per-screening verdict, and idea generation/review is skipped on a runner-up re-advance). Do not touch `eliminated` or `winner` (both remain `false`).
      - (c) Proceed directly to Gates 1b/1c Step 1 with K=1. **Conservative default: always rerun both gates** — the prior verdicts may be stale (literature has advanced since they were produced, negative_results.md has grown, prototype numerics may need re-checking). The cost of one additional novelty + prototype call is trivial relative to a full Stage 2+ run on a stale verdict. Commit: `pipeline: stage 1 re-entry — runner-up re-advanced (round {N})`.
   2. **Unused sketch** — a sketch present in `idea_sketches_r*.md` but absent from `stage1_candidates` (never advanced to Gates 1b/1c). Rank by idea-review scores and advance the best as the sole candidate (K=1). Before writing any files, increment `idea_round` in `pipeline_state.json` and let N = the new `idea_round` (this Round counts toward the 5-round cap); create `output/stage1/round_{N}/`. Then continue from step 7 with K=1.
   3. **Regenerate** — only if neither above applies. Launch idea-generator for a new Round.

   Never re-nominate an entry with `eliminated: true` (KNOWN/BLOCKED) or `winner: true` (its theory already failed). Also read the previous scorer feedback and/or failed theory to understand what went wrong — instruct the idea-generator to avoid the same failure mode
3. Launch idea-generator with the problem statement, literature map, **and data inventory** to brainstorm candidate mechanisms (see table above for count)
4. **Increment `idea_round` in `pipeline_state.json`** (starts at 0; becomes 1 on first entry). Save sketches to `output/stage1/idea_sketches_rN.md` where N = the new `idea_round` value. This counter feeds the 5-round escalation cap and the dashboard.
5. Commit: `artifact: idea sketches round {N}`

## Gate 1: Idea Review

**Agent:** `idea-reviewer`

1. Launch idea-reviewer on the sketches + problem statement + literature map + `output/data_inventory.md` (if it exists — the reviewer's tractability axis checks empirical feasibility against it)
2. If this is a return visit to Stage 1, also provide the previous scorer feedback so the reviewer knows what to screen against
3. Save review to `output/stage1/idea_review_rN.md`
4. Commit: `artifact: idea review round {N}`
5. Read the decision:

| Decision | Action |
|----------|--------|
| **ADVANCE** | Best idea identified. Proceed to Stage 2 with the reviewer's instructions for theory development. |
| **ITERATE** | Re-launch idea-generator with the reviewer's feedback. Max 5 rounds of iteration. |
| **REJECT ALL** | All ideas are weak. **First apply the Step 2a "fallback rescue":** if `fallback_idea_sketch_name` is non-null (the portfolio guard fired earlier this problem and a screened TRACTABLE fallback is snapshotted), advance that fallback as the winner instead of abandoning. Only if no fallback is pending, return to Stage 0 for a different problem. |

{{SEED_OVERRIDE_STAGE_1_GATE_1_REJECT_ALL}}

6. After 5 rounds without ADVANCE, pick the top-K highest-scored ideas (target 3, up to 5; fewer only if fewer than 3 viable non-proven-dead ideas exist) and advance them anyway.
7. Save each advanced idea's summary to `output/stage1/round_{N}/selected_idea_{k}.md` for k = 1..K (where K is the number of ideas idea-reviewer advanced — target ≥ 3, up to 5, fewer only if fewer than 3 viable approaches exist; and N is the current `idea_round`). Each file should include the development instructions for that idea plus the relevant sketch content from the round's `idea_sketches_rN.md`. The development instructions come from either:
   - **Normal ADVANCE:** the per-idea development-instructions line in the idea-reviewer's ADVANCE block. Under theory-first, this line begins "theory-generator should focus on..."; under `--mode empirical-first`, it begins "the Stage 2 mechanism writer should focus on..." (the reviewer emits the empirical phrasing under empirical-first per the mode-conditional ADVANCE template in `idea-reviewer-core.md`). Match on the "should focus on:" colon — both phrasings end with that token, so parsing is mode-agnostic.
   - **Force-advance** (5 rounds with no explicit ADVANCE — step 6): synthesize development instructions for each chosen idea from that idea's `**Strengths:**` and `**Weaknesses:**` blocks in the final round's review (these are per-idea fields that always exist in a review, unlike round-level "To develop further" which may be absent or addressed to the next generator round). The synthesized instruction should be of the form: "Build on [Strengths]; the Stage 2 agent must address [Weaknesses] during development." State in the file header that force-advance fallback was used, so Stage 2 knows the instructions are synthesized from weaknesses rather than reviewer-endorsed.

   Record the candidate list in `pipeline_state.json:stage1_candidates`. For each candidate set `reviewer_importance` to the idea-reviewer's **Importance-of-the-answer** score (1–5) for that approach from this round's review (the Step 3 tiebreak criterion (b) reads it). For each candidate: if an entry with the same `sketch_name` already exists (from a prior Round), **update it in place** — overwrite `round` (to the current `idea_round`), `rank`, and `reviewer_importance` (from the current review), reset the *screening* verdict fields (`novelty`, `prototype`) to `null` for re-screening, keep `winner`/`eliminated` as-is (they should be false for any sketch that re-qualifies, since `eliminated: true` or `winner: true` entries are excluded at re-nomination per step 2). If no existing entry: append a new one `{round: N, rank, sketch_name, novelty: null, prototype: null, reviewer_importance: <score>, prototype_retry: 0, eliminated: false, winner: false}`.
8. Commit: `artifact: top-{K} selected ideas saved`

## Gates 1b/1c: Parallel screening on top-K candidates

**Agents:** `novelty-checker` and `idea-prototyper` (each invoked K or fewer times)

Purpose: late-bind the final idea selection. Instead of committing to idea-reviewer's #1 pick, screen the top-K advanced candidates in parallel and pick the winner based on actual novelty + tractability evidence (broken, if needed, by the reviewer's importance-of-the-answer ceiling). K is whatever idea-reviewer advanced — typically **3–5** (the reviewer carries ≥3 whenever ≥3 viable approaches exist, capped at 5; fewer only when fewer than 3 are viable), except seeded mode where K = 1.

**Seeded mode:** in seeded mode (`seeded: true` in `pipeline_state.json`), Stage 1 is typically bypassed by `seed_triage`, which populates `selected_idea_1.md` directly from the seed. When Gates 1b/1c do fire in seeded mode, K = 1 by definition and the parallel-screening structure degenerates to a single-candidate pass. The per-gate seed overrides below apply unchanged in that case. **Do not widen K beyond 1 in seeded mode** — the seed is the contract.

### Step 1: Parallel novelty check (Gate 1b)

1. Launch K `novelty-checker` agents **concurrently**, one per candidate. Each reads `output/stage1/round_{N}/selected_idea_{k}.md` (N is the current `idea_round`) + `output/stage0/literature_map.md` and saves result to `output/stage1/round_{N}/novelty_check_{k}.md`.
2. After all K return, update `pipeline_state.json:stage1_candidates` with each candidate's `novelty` verdict.
3. Commit: `pipeline: gate 1b — novelty checks {v1/v2/.../vK}` (verdicts in rank order, e.g., `NOVEL/KNOWN/INCREMENTAL`).
4. Drop any candidate with verdict KNOWN (set `eliminated: true` in its state entry). Let M = number of survivors (NOVEL or INCREMENTAL).

| Case | Action |
|------|--------|
| M = 0 (all KNOWN) | No viable ideas from this top-K. Start a new Round of Stage 1 (counts toward the 5-round cap). **If starting it would exhaust the 5-round cap and `fallback_idea_sketch_name` is non-null, apply the Step 2a fallback rescue (ship the snapshotted fallback) instead of leaving for Stage 0.** |
| M ≥ 1 | Proceed to Step 2. |

{{SEED_OVERRIDE_STAGE_1_GATE_1B}}

### Step 2: Parallel prototype (Gate 1c)

1. Launch M `idea-prototyper` agents **concurrently**, one per surviving candidate. Each reads its `output/stage1/round_{N}/selected_idea_{k}.md` + `output/stage0/problem_statement.md` + `output/data_inventory.md` (if it exists — the empirical-first prototyper stress-tests data availability against it) and saves result to `output/stage1/round_{N}/idea_prototype_{k}.md`.
2. After all M return, update `pipeline_state.json:stage1_candidates` with each candidate's `prototype` verdict (one of `TRACTABLE`, `BLOCKED-DIFFICULTY`, `BLOCKED-IMPOSSIBLE`). The prototyper no longer emits a surprise tier — there is no `surprise` field to record. Initialize `prototype_retry: 0` on each entry if the field is absent.
3. **Harder-technique retry (NOVEL ideas only; skipped under `seeded: true` — the `SEED_OVERRIDE_STAGE_1_GATE_1C` block below supersedes this item in seeded/faithful mode).** The prototyper gives each idea one single-shot attempt; a NOVEL result whose proof needs a non-textbook technique will often return `BLOCKED-DIFFICULTY` on that one attempt — that is *difficulty*, not *impossibility*, and killing it here is the bias this gate must not reintroduce. (Under `--mode empirical-first` the prototyper is an empirical-feasibility checker: "technique" reads as "alternative identification angle — a different design class, narrower population, or different outcome proxy" throughout this item.) For each candidate that **(a)** returned `BLOCKED-DIFFICULTY`, **(b)** has novelty verdict `NOVEL` from Gate 1b, **(c)** filled in a concrete alternative in the prototype's named-alternative field — titled **"Most promising alternative technique"** in the default body and **"Most promising alternative angle"** in the empirical-first body (match either); i.e., the field holds a specific technique/angle and is *not* the "no specific alternative … identified" escape text — and **(d)** has `prototype_retry == 0`: re-launch `idea-prototyper` **once** with the same inputs plus an instruction to attempt the result using that named technique/angle (pass it verbatim). The retry overwrites `output/stage1/round_{N}/idea_prototype_{k}.md`, preserving the first attempt under a `## First attempt (pre-retry)` heading. Set `prototype_retry: 1` and overwrite the candidate's `prototype` with the retry's verdict. **INCREMENTAL candidates and `BLOCKED-IMPOSSIBLE` candidates get no retry** — the cheap single-shot screen stands. Run eligible retries concurrently; commit `pipeline: gate 1c retry — candidate {k} re-attempted via {technique}` after each.
4. **Propagate Negative results sequentially** (not in parallel — serialize to avoid file-append races). For each candidate whose **final** verdict is `BLOCKED-IMPOSSIBLE` with a "Negative result" section, in rank order: append that section verbatim to `output/stage1/negative_results.md` (create or append), then commit `artifact: negative result from candidate {k}`. Negative results constrain all subsequent theory-generator, math-auditor, and self-attacker calls on this problem — they must be quoted into those agents' prompts and the new theory must escape them. **Do not propagate `BLOCKED-DIFFICULTY` blocks** — a difficulty stall is not a proven impossibility, and feeding it into `negative_results.md` would wrongly constrain every later theory on this problem with a barrier that was never established (the failure mode this gate fixes).
5. Commit: `pipeline: gate 1c — idea prototypes {v1/v2/.../vM}` (final verdicts in rank order, e.g., `TRACTABLE/BLOCKED-IMPOSSIBLE/BLOCKED-DIFFICULTY`).
6. Drop any candidate whose final verdict is `BLOCKED-IMPOSSIBLE` or `BLOCKED-DIFFICULTY` (set `eliminated: true`). The two stay distinct in the `prototype` field for the audit trail: only `BLOCKED-IMPOSSIBLE` propagated a negative result (item 4) and represents a proven dead end; `BLOCKED-DIFFICULTY` is "hard, unresolved this round" — eliminated from *this* round's selection but not a proven no-go. Let S = number of `TRACTABLE` survivors (including any rescued by the retry in item 3).

| Case | Action |
|------|--------|
| S = 0 (no TRACTABLE survivor) | Start a new Round of Stage 1 (counts toward the 5-round cap). Any `BLOCKED-IMPOSSIBLE` negative results are already propagated and will constrain the next round. **If starting it would exhaust the 5-round cap and `fallback_idea_sketch_name` is non-null, apply the Step 2a fallback rescue (ship the snapshotted fallback) instead of leaving for Stage 0.** |
| S ≥ 1 | Proceed to **Step 2a (portfolio guard)**, then Step 3. |

{{SEED_OVERRIDE_STAGE_1_GATE_1C}}

### Step 2a: Portfolio guard — don't silently ship the incremental survivor

Problem selection sets the ceiling on the whole pipeline, so a round that kills its NOVEL ideas on *difficulty* and advances only an INCREMENTAL survivor is among the most costly silent failures Stage 1 can produce. This guard forces one harder idea-generation round before that happens. It fires **at most once per problem** and never costs a shippable idea (the current survivor is preserved as a fallback).

**Skip this guard entirely in seeded or faithful mode** (`seeded: true`): K = 1, the seed is the contract, and forcing harder rounds is not permitted (consistent with the "Regenerate banned in seeded mode" rule). Proceed directly to Step 3.

Fire the guard when **all** of these hold:
- **(a)** No `TRACTABLE` survivor has novelty verdict `NOVEL` (every survivor is INCREMENTAL); **and**
- **(b)** at least one candidate this round had novelty `NOVEL` at Gate 1b and ended — after any retry — at `BLOCKED-DIFFICULTY` (a novel idea left on the table for *difficulty*, not impossibility). A novel idea that ended `BLOCKED-IMPOSSIBLE` does **not** trigger the guard — it was genuinely foreclosed; **and**
- **(c)** `harder_round_forced` is not already `true` for this `problem_attempt` (fires at most once per problem); **and**
- **(d)** `idea_round < 5` (room under the round cap).

If any condition fails, **do not fire** — proceed directly to Step 3.

When it fires:
1. **Snapshot the fallback.** Among the current `TRACTABLE` survivors, pick the best by the Step 3 tiebreak criteria and copy its files to `output/stage1/fallback_idea.md`, `output/stage1/fallback_novelty_check.md`, `output/stage1/fallback_idea_prototype.md`. Record `fallback_idea_sketch_name` in `pipeline_state.json`. These survivors also remain in `stage1_candidates` with `eliminated: false, winner: false` (do **not** eliminate them) — the snapshot is the explicit, resume-safe pointer; the state entries are the audit trail and keep them re-nominable.
2. Set `harder_round_forced: true`.
3. Start a new Round of Stage 1 (increment `idea_round`; counts toward the 5-round cap). Instruct `idea-generator` to target **harder, higher-novelty mechanisms** in the territory of the blocked novel ideas: pass the blocked `NOVEL` sketches and their named-alternative notes ("Most promising alternative technique"/"angle") as seeds, and tell it to push past the textbook framing rather than retreat to safer mechanisms. The prototyper retry budget (item 3 above) applies in this round too.
4. Commit: `pipeline: stage 1 — forcing harder round (novel ideas blocked on difficulty, only incremental survived)`.

The forced round runs Gates 1b/1c normally. At its **Step 3 tiebreak** the candidate pool is the harder round's `TRACTABLE` survivors **plus the snapshotted fallback** (Step 3 loads it as an additional ranked candidate). If a harder-round survivor wins, the fallback is discarded; if nothing beats the fallback on the tiebreak criteria, the fallback is selected and shipped. Because `harder_round_forced` is now `true`, the guard cannot fire again on this problem: if the harder round *also* yields only incremental survivors, Step 3 proceeds normally and the best available idea (harder-round survivor or fallback) advances.

**Fallback rescue (never lose a shippable idea to the guard).** The forced harder round is steered toward hard, high-novelty mechanisms, so it can plausibly return `S = 0` (all blocked) and start yet another Round (per the Step 2 table) *without* reaching a Step 3 tiebreak — and that can repeat to the round cap. The fallback must not be abandoned in that tail: **whenever Stage 1 is about to leave for Stage 0** (the 5-round cap is exhausted, or Gate 1 returns REJECT ALL) while `fallback_idea_sketch_name` is non-null, do **not** abandon the problem — advance the snapshotted fallback as the winner instead. **Route it through Step 3's canonicalization, not a bare file copy:** treat the fallback as the tiebreak winner and run Step 3 steps 3-5 for it — set its candidate `winner: true` (step 3); copy `output/stage1/fallback_idea.md` → `selected_idea.md` and its siblings to the canonical names (step 4); and **apply the INCREMENTAL forwarding (step 5)** — the snapshotted fallback is always INCREMENTAL (the guard fires only when every survivor is, condition (a)), so the "escape the obvious version" instruction is mandatory or the rescued idea will predictably hard-fail Gate 3. (In empirical-first mode, likewise carry the fallback into the Step 4 identification-design handoff.) Then complete the normal Stage-1 close-out (steps 6-7 in theory-first; steps 6-8 then Step 4 in empirical-first: update `pipeline_state.json` and emit the stage-completion / empirical-first resume-marker commit) and clear the pointer. Because the rescue ships the fallback *with* the same forwarding Step 3 would have attached, shipping it is always at least as good as the pre-guard behavior (which would have shipped that same incremental survivor immediately, with that same forwarding) and strictly better than abandoning the problem. With this rescue the guard's worst case is "one or more extra idea-generation rounds, then ship the same idea we'd have shipped without the guard" — it can cost rounds, but never a shippable idea.

**Pointer lifecycle.** `fallback_idea_sketch_name` is set only when the guard fires and is cleared in exactly three places: (i) the next Step 3 tiebreak that consumes it (win or lose), (ii) the fallback-rescue above, and (iii) **whenever `problem_attempt` increments** (a Stage 0 re-run is a fresh problem — clear the pointer and ignore any stale `output/stage1/fallback_*.md`, alongside the `harder_round_forced` reset documented in `core.md`). Because of (iii), any non-null `fallback_idea_sketch_name` Step 3 sees necessarily belongs to the current problem — that is what makes the Step 3 inclusion test a plain "non-null" check.

### Step 3: Tiebreak and canonicalization

1. Among the S TRACTABLE survivors, rank by these criteria in order (advance to the next criterion only to break a tie):
   - (a) **Novelty tier:** NOVEL > INCREMENTAL (from the novelty-checker — the one independent, non-reviewer signal)
   - (b) **idea-reviewer Importance-of-the-answer score** (the ceiling axis, `reviewer_importance` in `stage1_candidates`, 1–5): higher wins. With the idea-stage surprise rating removed, the ceiling of the answer the approach would deliver is the discriminator — answer *surprise* is now a development-stage outcome the scorer judges at Gate 4, not a Stage-1 selection signal.
   - (c) **idea-reviewer ADVANCE rank:** lower position number wins (position 1 > 2 > … > K, for whatever K the reviewer advanced)

   **Portfolio-guard fallback inclusion:** if `fallback_idea_sketch_name` is non-null (a fallback was snapshotted by Step 2a for the current problem — the pointer-lifecycle rules guarantee it cannot belong to a prior problem), include it as an additional ranked candidate here using its recorded `novelty`/`reviewer_importance` verdicts (its files are `output/stage1/fallback_idea.md` and siblings). After this tiebreak resolves — whether the fallback wins or loses — clear the pointer (`fallback_idea_sketch_name = null`) so it is not reconsidered in a later Round. If the fallback wins, treat its files as the winner in step 4 below (copy `fallback_idea.md` → `selected_idea.md`, etc.).
2. Save the tiebreak rationale to `output/stage1/candidate_selection.md` — list all K original candidates with their verdicts, note which were dropped at which step and why, and state the winner with the specific criterion that determined selection. This file is Round-scoped and each new Round overwrites it; the full cross-Round audit trail lives in `pipeline_state.json:stage1_candidates`.
3. In `pipeline_state.json:stage1_candidates`, set `winner: true` on the winning entry. Leave non-winning TRACTABLE survivors with `eliminated: false` — they passed both gates and remain valid fallback candidates on re-entry after a failed theory (this is the main operational payoff of parallel screening). Only KNOWN-at-1b and BLOCKED-at-1c entries are `eliminated: true`.
4. Copy the winner's files to the canonical top-level names Stage 2 consumes:
   - `output/stage1/round_{N}/selected_idea_{k_win}.md` → `output/stage1/selected_idea.md`
   - `output/stage1/round_{N}/novelty_check_{k_win}.md` → `output/stage1/novelty_check_idea.md`
   - `output/stage1/round_{N}/idea_prototype_{k_win}.md` → `output/stage1/idea_prototype.md`
   Keep the per-round indexed files under `round_{N}/` as well (do not delete them) — they are the audit trail for this Round's screening.
5. **INCREMENTAL forwarding:** if the winner's novelty verdict is INCREMENTAL, extract the "escape the obvious version" instruction — *"This approach was flagged INCREMENTAL — the obvious version of this model already exists in the literature. Your job is to find a result within this framework that the existing papers do not imply: a sign reversal, an unexpected threshold, a case where the standard intuition breaks. Do not formalize the obvious version."* — and include it verbatim in the Stage 2 theory-generator prompt. Gate 3 will hard-fail INCREMENTAL on the full theory, so the theory must escape incrementality during development.

{{SEED_OVERRIDE_STAGE_1_INCREMENTAL_FORWARD}}

6. Update `pipeline_state.json`.
<!-- THEORY_FIRST_START -->
7. Commit: `pipeline: stage 1 complete — winner selected from {K} candidates`.
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
7. **Set `pipeline_state.json:current_stage = "stage_1_identification_design"`** — this is the resume marker. The session-level resume path reads `current_stage` and routes to Step 4 below as long as it holds this value. Without setting this, an interruption between this commit and Step 4 would leave `current_stage = "stage_1"` and the orchestrator could plausibly re-run the whole tiebreak or skip to Stage 2 reading the commit message alone.
8. Commit: `pipeline: stage 1 tiebreak complete — winner selected from {K} candidates; identification design pending`. (The "stage 1 complete" commit is held until Step 4 below finishes — a resume between this commit and Step 4 must therefore re-enter Stage 1 at Step 4, not skip ahead to Stage 2; `current_stage` makes that routing automatic.)

## Step 4: Identification design (empirical-first mode)

**Agent:** `identification-designer`

In empirical-first mode the identification design is a Stage 1 deliverable, not a Stage 3a check. The selected idea names the empirical question; the identification-designer now decides how to answer it credibly. Stage 2 (mechanism mode) reads this artifact and writes a mechanism whose channel matches the design's recovered estimand.

Under `--mode empirical-first` the `identification-designer` body is **mode-aware** (assembled from the empirical-first override at `templates/agent_bodies/shared_modes/empirical_first/identification-designer-core.md`): it identifies the empirical question (there is no theorem), commits to a single design plus top-2 alternatives rather than a ranked menu, escapes the obvious version when the question is flagged INCREMENTAL, applies a question-match (not theory-match) rule, and reads its inputs / writes its output from the paths the launch instruction names. The launch instruction therefore supplies only the **context-specific paths** and the **INCREMENTAL flag** — the output structure and the no-theory-file framing already live in the body, so they cannot be lost to paraphrase.

1. Read the canonical idea files written in Step 3:
   - `output/stage1/selected_idea.md`
   - `output/stage1/idea_prototype.md`
   - `output/stage1/novelty_check_idea.md`
   - `output/data_inventory.md`
   - `output/stage0/literature_map.md`
2. Launch `identification-designer` with this launch instruction:

   > "You are operating under `--mode empirical-first` at Stage 1. Read `output/stage1/selected_idea.md`, `output/stage1/idea_prototype.md`, `output/stage1/novelty_check_idea.md`, `output/data_inventory.md`, and `output/stage0/literature_map.md`. The object to identify is the empirical question the selected idea poses; the idea-prototyper's predicted relationship (sign, channel, population) is the substantive content your design must support. Save the committed design to `output/stage1/identification_design.md`."

   **If the winning idea's novelty verdict is INCREMENTAL** (per Step 3 step 5 / `novelty_check_idea.md`), append to the launch instruction: *"This question was flagged INCREMENTAL — the obvious version of this empirical approach already exists. Aim the committed design at evidence the obvious version cannot deliver, and note how it escapes it (your body's INCREMENTAL guidance applies)."* This is the identification-side counterpart to the Step 3 step 5 forwarding that already reaches the Stage 2 mechanism writer — in empirical-first the design, not just the mechanism, is where incrementality gets escaped.
3. The artifact at `output/stage1/identification_design.md` must answer:
   - Which design class (RD, IV, DiD, narrative, RCT, event study, asset-pricing test, etc.) and why
   - The named identifying assumptions and the diagnostics that defend each one
   - The estimand the design recovers, in the language of the empirical question
   - The data sources required (cross-referenced with `data_inventory.md`)
   - Top-2 alternative designs with why they were not selected
4. **Handle non-design outcomes.** If the designer returns `N/A — no causal claim` (the question is purely descriptive / calibration / model-fit despite empirical-first framing), `OUT-OF-SCOPE` (macro toolkit required), or `N/A — no design feasible from the available data variation`: do **not** route to `puzzle-triager` (its entry check requires `output/stage3/implications.md` and `output/stage3a/empirical_analysis.md`, neither of which exists yet). Instead, treat as a Stage-1 escalation:
   - Save the designer's verdict to `output/stage1/identification_design.md`.
   - Launch `branch-manager` with context = `stage-1-empirical-first-no-design`, the designer's verdict, the selected idea content, and `data_inventory.md`. Output path: `output/stage1/escalation_no_design_r{idea_round}.md`. Branch-manager (see its body's `## Stage 1 escalation report` section) produces one of three recommendations.
   - Apply the recommendation as follows:
     - **REENTER-STAGE-1**: branch-manager named a runner-up sketch. Set `current_stage = "stage_1"`. Apply the runner-up re-advance protocol in step 2 above (`Pre-screened runner-up`) using the named sketch. Commit `pipeline: stage 1 re-entry — empirical-first no-design escalation, advancing runner-up {sketch_name}`.
     - **REENTER-STAGE-0**: the data inventory is the bottleneck. Set `current_stage = "stage_0"`. Increment `problem_attempt` in `pipeline_state.json`. Stage 0 fires fresh on a new problem statement; pass branch-manager's named data-gap as a constraint to `literature-scout`. Commit `pipeline: stage 0 re-entry — empirical-first no-design escalation, data inventory bottleneck`.
     - **OPERATOR-ESCALATE**: the question is irreducibly non-causal and theory-first may be the right deployment. **Set `status = "halted_no_identification_design"`** in `pipeline_state.json` and leave `current_stage = "stage_1_identification_design"` unchanged. The session-level resume logic treats `halted_*` statuses as terminal — the orchestrator stops; auto-resume will not advance. Commit `pipeline: halted — empirical-first no-design escalation, operator intervention required`. The operator must rerun `update.sh` without `--mode empirical-first` (or with `--no-mode`) to convert the deployment to theory-first, or decide the question should be abandoned. Do not attempt the conversion mid-run.
5. Set `current_stage = "stage_2"`. Commit: `pipeline: stage 1 complete — identification design saved`.

The Stage 2 mechanism-mode `theory-generator` consumes `output/stage1/identification_design.md` directly (its body says "consult docs/stage_1.md in this deployment" — that pointer resolves here). Stage 3a's identification-designer step is skipped on first pass since the design already exists; it re-fires only if a Stage 3a re-fire on theory revision introduces a new causal claim or changes the theoretical object the empirics must identify.
<!-- EMPIRICAL_FIRST_END -->
