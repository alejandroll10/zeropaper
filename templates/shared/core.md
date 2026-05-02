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

## Core principle: no phantom time pressure

There is no deadline, no time budget, and no version-count limit. Keep iterating as long as each round is positive for the paper, even if marginal — "diminishing returns" is a stop condition only once returns are zero or negative, not merely small. If you feel worried about how long this is taking, consider the reference class: what the pipeline does in hours or days would take a human researcher months. Have faith in the process.

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
- **No unproved mathematical claims.** Every proposition, lemma, and corollary must be proved. If a proof attempt fails, try a different strategy, find a sufficient condition under which it holds, or restructure the paper around what you can prove. Demoting a claim to a conjecture to dodge an audit is not acceptable; narrowing scope when the math or computation shows the broader version fails is the correct move. This rule applies to formal mathematical statements, not to assumptions or prose.

## Core principle: frame honestly — never inflate

The paper's framing must match what its results actually deliver. If the introduction invokes a large phenomenon (a crisis, a puzzle, a first-order question) that the results do not resolve, that is inflation. Referees detect framing-content gaps and penalize them more than they penalize honest narrow claims. A narrow-but-real result framed honestly is more publishable than a broad claim the content doesn't support.

## Core principle: reframing is not progress

A revision earns score only when it adds new mathematical content. Rewording, reorganization, label promotions or demotions, and restructuring around an existing result are typos — fix when wrong, but they do not move the score. See `docs/stage_4.md` for the catalogue and the orchestrator rule.

## Core principle: scientist first

We are scientists, not marketers. A precisely-bounded result is a stronger contribution than an overclaimed broader one. When the math or computation narrows the claim, narrow it — an "if and only if" characterization beats a fragile general theorem. Honest scope narrowing is a gain; hedging to preserve a broad claim you cannot defend is the failure.

## Core principle: tool failure is not substantive failure

When a **computational or retrieval tool** fails — a numerical solver that doesn't converge, a regression that returns empty, a literature search that finds nothing, a data query that times out, a compiler that errors — the first hypothesis is that the tool was misfit to the case, not that the claim is false. Launch the `debugger` agent on the failure report. Debugger diagnoses tool-fit vs substantive failure and proposes a concrete fix. Only after debugger returns `SUBSTANTIVE-FAILURE` is the failure a signal about the claim. Do not rescope, reinterpret, or weaken a claim on the strength of a failed tool alone.

**This principle covers tool execution failures, not reasoning-agent verdicts.** A math-auditor returning FAIL on a proof, a scorer returning a low score, a referee rejecting — these are substantive outputs of reasoning agents, not tool failures. Do not launch debugger on them; handle them per the stage's revision rules.

## Core principle: do what makes the paper better, not what is easiest

At every decision point, choose the action that maximizes paper quality — even if a shortcut exists. When a proof fails, try harder proof strategies and use every available tool (including codex-math) before weakening the claim. When empirical data could strengthen a result, run the analysis instead of relying on verbal arguments. When a hard extension would add real content, pursue it instead of polishing exposition.

Concretely:
- If a math audit flags an unproved lemma, exhaust proof strategies (codex-math explore mode, alternative proof techniques, relaxed sufficient conditions) before demoting to a conjecture or an empirical regularity.
- If the scorer says "needs more mathematical substance," add a genuine extension — don't reframe the same content with better words.
- When referee or self-attack pressure targets **framing** (a claim's label, its scope, an abstract phrasing), the substance response is to strengthen the underlying result until the framing concern becomes moot — prove the stronger version that actually deserves the label, add the extension that fills the perceived gap, nail down the empirics that ground the claim. Under such pressure, a pure rename or softening settles the referee for one round and invites the same class of concern next round. A framing-only edit in response to pressure is acceptable only when the substance already holds and the prior label was merely inaccurate, or when new evidence (failed audit, empirical pivot, new result) has changed what the paper actually delivers. This rule is about cosmetic responses to pressure — not about prose or structural edits for clarity, or framing updates that track genuine changes in the content.
- If a tool exists for the task (data skills, codex-math, theory-explorer), use it. Skipping available tools because they're unfamiliar is not acceptable.
- The path of least resistance produces thin papers. Referees can tell.

---

## Pipeline overview

```
Stage 0: Problem Discovery   ──→ Gate 0: Problem Viability
Stage 1: Idea Generation     ──→ Gate 1: Idea Review (iterates with generator)
                                   └── ADVANCE → top-K ideas ranked (1 ≤ K ≤ 3)
                                Gates 1b/1c: Parallel screening on top-K
                                   Step 1: K novelty-checkers in parallel
                                     └── drop KNOWN; survivors continue
                                   Step 2: prototypers on survivors in parallel
                                     └── drop BLOCKED (Negative results →
                                         stage1/negative_results.md, sequential append)
                                   Step 3: tiebreak among TRACTABLE survivors
                                     (novelty tier > surprise tier > reviewer rank)
                                     → winner copied to canonical files
                                   ├── all K eliminated → new Round of Stage 1
                                   └── ≥1 survives → proceed to Stage 2
Stage 2: Theory Development  ──→ Gate 2: Math Audit (structured then free-form)
                                   Gate 3: Novelty Check on full theory
                                   Stage 2b: Theory Exploration (compute, verify, plot)
                                      ├── FAILS → back to Stage 2
                                      └── HOLDS/FRAGILE → proceed
Gate 3a-feasibility: Empirical Feasibility   (only if --ext empirical)
                                   ├── FALSIFIED → back to Stage 1
                                   └── OK → proceed
Stage 3: Implications        ──→ derive predictions + gap-scout each → tag
                                   NOVEL / PUZZLE-CANDIDATE / SUPPORTED / DEAD
Stage 3a: Empirical Analysis     (only if --ext empirical, full test + audit)
Stage 3b: Experiments         (only if --ext theory_llm, design + review)
Puzzle Triage                ──→ fires if empirics/experiments contradict, OR Stage 3 PUZZLE-CANDIDATE
                                   ├── NORMAL-PROCEED → Stage 4
                                   ├── FIX-EMPIRICS → re-run empirics
                                   ├── RECONCILE → add scope condition, Gate 2
                                   ├── BACK-TO-IDEA → Stage 1
                                   ├── PIVOT → rebuild theory around contradiction
                                   │            (re-run Gate 2, Gate 3, Stage 2b, Stage 3, empirics; max 2 pivots)
                                   └── HONEST-NULL → Stage 5 with limits, or Stage 0
Stage 4: Self-Attack          ──→ Gate 4: Scorer Decision (trajectory-based)
                                   ├── ADVANCE (75+) → Stage 5
                                   ├── REVISE  → back to Stage 2 (continue if Δ≥3, else escalate)
                                   ├── MAJOR REWORK → back to Stage 1 (continue if Δ≥3, else escalate)
                                   └── ABANDON → back to Stage 0 (max 5×)
Stage 5: Paper Writing        ──→
Stage 6: Referee Simulation   ──→ editor (aggregates 3 reports → canonical comment list +
                                                aggregated verdict + journal-fit verdict)
                                Gate 5: Referee Decision (routed by editor verdict)
                                   ├── Minor/Accept → Stage 7
                                   ├── Major Revision → triage editor's canonical list, revise,
                                                       re-run Stage 6 (max 10×)
                                   ├── Reject → triage → deepen directive → deepen the core
                                                (theory or empirics; never extend); branch-manager
                                                substantive/cosmetic check; cosmetic ×2 → theory failure
                                   └── (editor may also recommend Downgrade tier, which lowers
                                       target_journal_tier and may immediately ship Accept/Minor)
Stage 7: Style Check          ──→
Stage 8: Bibliography Verify  ──→
Stage 9: Polish               ──→ (seven parallel polish agents + triage + paper-writer + style re-run; max 2 rounds)
Stage 10: Lessons             ──→ Done (orchestrator writes LESSONS_PAPER.md + LESSONS_PIPELINE.md)
```

**Stage labels.** Letter suffixes (`2b`, `3a`, `3b`) are extension-conditional or sequence-internal sub-stages within a block, not top-level stages. `2b` runs after Gates 2/3 inside Stage 2's block; `3a`/`3b` are the empirical / theory_llm extensions paired with Stage 3 (Implications). `Gate 3a-feasibility` carries the `3a` label because it is the empirical extension's pre-check, not because it sits inside Stage 3.

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
  "theory_version": 1,
  "referee_round": 0,
  "reject_cosmetic_round": 0,
  "target_journal_tier": "top-5",
  "pivot_round": 0,
  "fix_empirics_round": 0,
  "bib_verify_round": 0,
  "polish_round": 0,
  "regeneration_round": 0,
  "pivot_resolved": null,
  "pivot_history": [],
  "triaged_lit_implications": [],
  "seeded": false,
  "status": "not_started",
  "scores": {},
  "stage2b_theory_version": null,
  "archived_best_score_r1": null,
{{EMPIRICAL_STATE_FIELDS}}
{{THEORY_LLM_STATE_FIELDS}}
  "stage1_candidates": [],
  "history": []
}
```

When `--seed` is used, setup.sh also adds `"seeded": true` and sets `"current_stage": "seed_triage"`. In that case, a **Seeded idea mode** section is injected below with the entry procedure.

When you start the pipeline, set `"status": "running"` and begin appending to the history array.

**History array:** Append a `{ "timestamp": "ISO-8601", "event": "description" }` entry for every pipeline event. This feeds the dashboard. Use `date -u +%Y-%m-%dT%H:%M:%SZ` to get the timestamp. Never truncate or clear the history array.

**`stage2b_theory_version`:** Set to the `theory_version` that Stage 2b last fully explored. Before advancing at Gate 4, the orchestrator must verify this equals the current `theory_version`; if it is stale, re-run Stage 2b on the new content (see `docs/stage_2.md` Stage 2b step 5).

**`reject_cosmetic_round`:** Tracks consecutive cosmetic-deepening attempts when responding to a Stage 6 Reject verdict. Increments when branch-manager (gate-5-reject context) returns COSMETIC on a deepen attempt; resets to 0 on a SUBSTANTIVE deepen, on a Regeneration Round entry, or on falling back to standard Major Revision after the deepen path is exhausted. See `docs/stage_6.md` Reject row for the full state machine.

**`target_journal_tier`:** The active journal tier for Gate 4 advance threshold and Stage 6 referee variant context. Initialized to `top-5`. The Stage 6 `editor` agent may recommend a tier change (Downgrade or Upgrade) based on cross-referee tier-fit signals; on Downgrade, the orchestrator updates this field and recomputes the Gate 4 advance threshold per `docs/stage_4.md`. Allowed values: `top-5` / `field` / `letters`. See `docs/stage_6.md` "Journal-fit handling" for the procedure.

**`archived_best_score_r{N}`:** Records the best Gate 4 score achieved on the pre-regeneration paper at the moment Regeneration Round N begins. Initialized to `null` (key `archived_best_score_r1` is in the initial schema; for N>1 the orchestrator appends `archived_best_score_r{N}` dynamically at regeneration entry). Consumers in `docs/stage_1.md` step 2 (regeneration re-entry) read this to compare the regenerated attempt's eventual Gate 4 score against the archived value; if the regenerated attempt does not strictly beat the archive, restore the archived paper from `paper_archive/r{N}/` and ship. A `null` value means no archive comparison applies (no regeneration has fired on this branch).

{{EMPIRICAL_STATE3A_DOC}}
{{THEORY_LLM_STATE3B_DOC}}
**`stage1_candidates`:** Records every sketch screened at Gates 1b/1c during Stage 1. Each entry: `{round, rank, sketch_name, novelty, prototype, surprise, eliminated, winner}` — `round` is the `idea_round` value when the entry was last written; `rank` is the idea-reviewer ADVANCE position (1..K) **within that round** (rank is unique per-round, NOT unique across the array); verdict fields are `null` until the agent runs. The flags mean:
- `eliminated: true` — screened as dead. Set **only** for KNOWN at 1b or BLOCKED at 1c. Never re-nominate.
- `winner: true` — the sketch whose theory is currently being developed downstream. If the theory later fails, this sketch has already been tried and should not be re-nominated.
- `eliminated: false AND winner: false` — a TRACTABLE survivor that lost the tiebreak. **This is a pre-vetted runner-up** and is the preferred re-nomination on re-entry after a failed theory (see `docs/stage_1.md` step 2).

Entries accumulate across Rounds — do not clear between Rounds. **Deduplicate by `sketch_name`**: if an entry with the same `sketch_name` already exists when Step 7 of Stage 1 runs, update it in place (new `round`, new `rank`, verdict fields reset to `null` for re-screening) rather than appending a duplicate. Lookups that need "the current winner" must filter by `winner: true` (at most one such entry should exist at any time during a run); lookups that need "pre-vetted runner-ups" filter by `eliminated: false AND winner: false`.

**Per-round indexed file namespace.** Stage 1 writes indexed candidate files (`selected_idea_{k}.md`, `novelty_check_{k}.md`, `idea_prototype_{k}.md`) under `output/stage1/round_{N}/` where N is the current `idea_round`. This keeps each Round's artifacts self-contained and prevents stale indexed files from a prior Round being mistaken for current state. The canonical winner files (`output/stage1/selected_idea.md`, `novelty_check_idea.md`, `idea_prototype.md`) are written at the top level of `output/stage1/` and are the authoritative inputs for Stage 2.

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

---

## Stage 3: Implications

Read `docs/stage_3_implications.md` and proceed accordingly.

{{EXTENSION_STAGES}}

---

## Stage: Puzzle Triage

Read `docs/stage_puzzle_triage.md` and proceed accordingly. Skip only if (a) no empirical/experimental contradiction was produced AND (b) Stage 3 tagged no implication PUZZLE-CANDIDATE — see `docs/stage_puzzle_triage.md` "Fires when" for the full trigger.

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

## Stage 8: Bibliography Verification

Read `docs/stage_8.md` and proceed accordingly.

---

## Stage 9: Polish

Read `docs/stage_9.md` and proceed accordingly.

---

## Stage 10: Lessons

Read `docs/stage_10.md` and proceed accordingly.

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

**Once a paper draft exists (Stage 5+), the pipeline must produce a finished paper.** Do not loop back to Stage 0 after investing in paper writing. Instead, use the deepening playbook below to strengthen the paper. A regeneration round per the escalation table is permitted post-Stage-5; it re-enters at Stage 1, not Stage 0.

If the scorer plateaus in the 55-74 range or the referee gives Major Revision with structural concerns (result is fragile, too narrow, or shallow):

### Deepening playbook

When the core result is correct but thin, extend it with mathematically hard, economically interesting analyses that uncover new content the simple model hid. The goal is characterization, not robustness.

**Extension types:** continuous time (HJB/SDEs), incomplete markets/heterogeneity (Bewley/HANK), learning/incomplete information, general preferences (CRRA/EZ/habits), higher dimensions (N assets, continuum of agents), perturbation/approximation (formal error bounds), dynamic/stochastic, moral hazard/agency, adverse selection, mechanism design, network/contagion.
{{EMPIRICAL_PLAYBOOK_ADDENDUM}}

**How to apply:** Identify the specific economic weakness from scorer/self-attack feedback. Pick 1-2 extensions that test whether the channel survives under realistic features. Prove the result or prove it breaks (a counterexample is as valuable as a positive result). Re-run Gate 2 + Gate 4 on extensions.

**When to extend vs. start over:** Score 55+ with correct core → extend. Score < 35 or core wrong → start over. Novelty KNOWN → start over.

---

## Escalation rules (prevent infinite loops)

| Situation | After N failures | Action |
|-----------|-----------------|--------|
| Idea review iterates | 5 rounds | Pick the best idea and advance to Gate 1b |
| Idea review rejects all | 1 rejection | Return to Stage 0 for a different problem |
| Gates 1b/1c parallel screening eliminates all candidates | All top-K KNOWN at 1b OR BLOCKED at 1c | New Round of Stage 1 (counts toward 5-round limit) |
| Gate 3 novelty INCREMENTAL | 3 rework attempts at Stage 2 | Abandon this idea, return to Stage 1 for a new one |
| Math audit fails | 3 attempts | Abandon this theory version |
| Scorer: delta ≥ 3 with substantive content change | — | Allow one more iteration in current band |
| Scorer: delta ≥ 3 from reframing only | — | Treat as plateau — escalate. Reframing is not progress (see `stage_4.md`). |
| Scorer: delta < 3 (plateau/decline) | — | Escalate one level (REVISE → MAJOR REWORK → ABANDON) |
| Scorer: hard ceiling | 8 total evaluations on same problem | If score ≥ 55: switch to deepening playbook. If score < 55: escalate one level. |
| Scorer plateau 55-74 | 2 consecutive delta < 3 | Switch to deepening playbook — the core idea works, it needs mathematical depth, not reworking. |
| Scorer plateau 55-74, branch-manager §E = Regenerate, no prior regen on this problem (`regeneration_round == 0`), **not seeded** | — | Fire regeneration round at Stage 1 (see `docs/stage_1.md` "Regeneration round"). Increment `regeneration_round` *before* re-entering Stage 1. **Takes precedence over the deepening-playbook row above when both fire** — Regenerate is the §E verdict that supersedes the default plateau routing. **At most one regeneration per problem:** if the regenerated attempt also plateaus, this row no longer fires (`regeneration_round > 0`) and the "Scorer plateau 55-74" row directly above applies — switch to the deepening playbook. |
| Theory scored ABANDON | 5 theories on same problem | Change the problem (Stage 0) |
| Problem viability fails | 5 problems | Pick the best scoring problem and proceed anyway |
| Editor: Major Revision (aggregated verdict) | Structural concerns (fragile, narrow, shallow) | Use deepening playbook. Triage editor's canonical comment list; revise; re-run Stage 6. Be patient — keep going as long as each round surfaces any new issue. Max 10 rounds. |
| Mechanism referee: MISATTRIBUTED unresolved | Still MISATTRIBUTED at `referee_round >= 10` | Adopt the mechanism referee's identified driver as the paper's mechanism; rewrite introduction/mechanism sections and ship. **Force-adoption at round-10 resolves all outstanding locked mechanism `[FIX]` items as satisfied — no further revision cycle is required.** In seeded mode, prefer the narrow-framing path from the seed override (present what the math delivers under the seed's topic, acknowledge the mechanism-claim divergence in limitations) rather than adopting an unrelated driver. Never return to Stage 0 (never-abandon). |
| Mechanism referee: DECORATIVE unresolved | Still DECORATIVE at `referee_round >= 10` | Ship the narrow-path version: after 10 rounds the restructure path has failed to surface real economic content, so narrow is the principled default. Present what the math delivers as a structural characterization, strip mechanism framing, add a limitations paragraph. **Round-10 narrow-adoption resolves all outstanding locked mechanism `[FIX]` items as satisfied.** Never return to Stage 0 (never-abandon, scientist-first). |
| Editor: Reject (aggregated verdict) | — | Stage 6 fires only post-Stage-5, so a paper draft always exists; never-abandon. Reject routes through triage → deepen directive → deepen mandate (see `docs/stage_6.md` Reject row for full procedure). The pre-Stage-5 "Stage 0 / Stage 2" branches do not exist at this point. On two consecutive cosmetic deepen attempts, the orchestrator routes through the Regeneration Round protocol if eligible (`regeneration_round == 0`, not seeded), otherwise falls back to standard Major Revision (never-abandon). |
| Editor: Downgrade tier recommendation | — | Update `target_journal_tier` in pipeline state, recompute Gate 4 advance threshold per the new tier. If aggregated verdict is Accept/Minor Revision at the new tier (current paper clears the new threshold), proceed to Stage 7. If Major Revision, continue the loop targeting the lower tier; the next round's referees inherit the updated tier in their variant context. See `docs/stage_6.md` "Journal-fit handling". |

Before granting another iteration on a Δ≥3 score increase, the orchestrator classifies the v(N)→v(N−1) diff as substantive or cosmetic. Branch-manager emits this verdict at every Gate 4 (Section A); when it reports COSMETIC, the orchestrator escalates rather than continue. Definitions and the cosmetic-edit catalogue live in `docs/stage_4.md`.

---

## File organization

```
output/                   # Pipeline outputs by stage
├── seed/                 # (--seed mode only) user idea files + pipeline reports
├── stage0/               # literature_map_broad.md, gap_selection.md, literature_map.md, problem_statement.md
├── stage1/               # idea sketches, reviews, selected_idea.md, novelty + prototype
├── stage2/               # theory drafts, math audits, novelty checks (versioned _v1, _v2…)
├── stage2b/              # theory exploration report + figures/
├── stage3/               # implications.md
├── stage3a/              # empirical feasibility + full analysis (if --ext empirical)
├── stage3b/  # LLM experiments (if --ext theory_llm)
├── stage4/               # self-attack + scorer decision (versioned)
├── debug/                # debugger reports (launched on tool-execution failures)
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
