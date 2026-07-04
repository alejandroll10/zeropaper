# Stage 4: Self-Attack

**Agent:** `self-attacker`

1. Launch self-attacker on the theory draft + implications + theory exploration results (if available) **+ `output/stage1/negative_results.md` if it exists** (BLOCKED-IMPOSSIBLE prototypes from prior Stage-1 rounds — only proven impossibilities propagate here, not difficulty stalls — orchestrator must pass this in explicitly; agent self-reads are defense-in-depth, not the primary delivery mechanism).
2. Save result to `output/stage4/self_attack_vN.md`
3. Commit: `artifact: self-attack v{N}`
3a. **Load-bearing premise header check (string-presence only).** Confirm `output/stage4/self_attack_vN.md` contains a `**Load-bearing premise:**` line (or one `**Load-bearing premise [piece K — label]:**` line per piece for a multi-piece contribution). This is a string check, not a judgment call — the self-attacker body owns the substantive requirement (the premise must be theory-anchored, headline-critical, and attacked exhaustively before any other category). If the header is absent, re-launch self-attacker once with: "your prior report omitted the mandatory load-bearing-premise header — re-run and state it (one line, or one line per independently-load-bearing piece) at the top of the output, then attack each named premise exhaustively under Assumption attacks before any other category." Overwrite `output/stage4/self_attack_vN.md` and commit `artifact: self-attack v{N} (premise re-fire)`. If the header is still absent after the re-fire, write a one-line note to `process_log/self_attack_premise_skip_vN.md` and proceed — do not loop more than one re-fire per version N. This is a self-attacker-side gate: a missing premise line never routes back to theory-generator.
4. **Triage the concerns.** Launch `triager` with: input = `output/stage4/self_attack_vN.md`, output path = `output/stage4/triage_vN.md`, context = `gate-4`. Triager applies the rules (severity-≥7 defaults to `[FIX]`; downgrades require a written justification) and produces the triage file. Only `[FIX]` items feed into the theory-generator for revision; the rest are held for Stage 5 (paper-writer) or the response letter. Do not edit the triager's output — if you disagree with a classification, re-launch the triager with explicit instructions, do not silently override.
5. Commit: `artifact: concern triage v{N}`

## Gate 4: Scorer Decision

**Agents:** `scorer` + `scorer-freeform` (launched in parallel — neither sees the other's output)

**Bypass recording (default mode too).** Skipping this gate, advancing past it without a result, or running its task via a substitute agent is a core bypass *unless this doc sanctions it* — record a `gate-skipped` / `agent-substituted` row in `process_log/degradation_ledger.md` before continuing (`docs/core_bypass.md`).

1. Launch both scorers in parallel with the same inputs:
   - Theory draft: `output/stage2/theory_draft_vN.md`
<!-- THEORY_FIRST_START -->
   - Math audit (structured): `output/stage2/math_audit_vN.md`
   - Math audit (free-form): `output/stage2/freeform_audit_vN.md`
   - Theory exploration: `output/stage2b/exploration.md` (if available — computational verification and diagnostic plots)
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
   - Identification audit: `output/stage3a/identification_audit.md` (Stage 1 design + Stage 3a plan; H3 gates on this)
   - Empirics audit: `output/stage3a/empirics_audit.md` (H3 gates on this)
   - Data-integrity audit: `output/stage3a/data_integrity_audit.md` (H3 gates on this — step 7.5)
   - Data-selection audit: `output/stage3a/data_selection_audit.md` (H3 gates on this — step 7.5)
   - Mechanism plausibility audit: `output/stage2/mechanism_audit_v{N}.md` (the empirical-first Gate 2 verdict; **context, not an H3 hard gate in v1** — H3 still gates on the four audits above). Read it so the holistic score reflects the plan-time channel verdict, and **confirm the gate is current**: the audit file for the version being scored must exist with a PLAUSIBLE verdict and `pipeline_state.json:stage2_mechanism_version` must equal `theory_version`. If it is missing or stale, the mechanism gate was bypassed — do not advance; flag it and route back to Gate 2 (this mirrors the orchestrator's own Gate-4 enforcement and gives the scorer an independent second line on it). Folding mechanism-plausibility into the H3 hard requirement is the deferred #142 Stage-4 item ([#142]).
   - (Math audit and theory exploration files do not exist under empirical-first; do NOT attempt to read `output/stage2/math_audit_*.md` or `output/stage2b/exploration.md`.)
<!-- EMPIRICAL_FIRST_END -->
   - Novelty check (idea): `output/stage1/novelty_check_idea.md`
   - Novelty check (theory): `output/stage2/novelty_check_vN.md`
   - **Implications with lit-check tags:** `output/stage3/implications.md` (for the SUPPORTED-cap / PUZZLE-CANDIDATE-floor rules on Surprise)
   - **Puzzle-triage report(s):** any `output/puzzle_triage/triage_pN.md` files that exist (needed for the Surprise-floor rule's measurement-quality gate on PUZZLE-CANDIDATE)
   - **Pipeline state:** pass `loops.pivot.round` and `pivot_resolved` so the scorer knows whether a pivot fired and whether it resolved
   - Self-attack: `output/stage4/self_attack_vN.md`
<!-- THEORY_FIRST_START -->
   - **Structured scorer only, on revisions (N ≥ 2):** also pass the prior theory draft (`output/stage2/theory_draft_v{N-1}.md`) and the `## Unverified claims` section of the prior math audit (`output/stage2/math_audit_v{N-1}.md`). Do NOT pass any prior scorer output or prior score to either agent — the structured scorer scores independently; the freeform scorer is history-blind.
<!-- THEORY_FIRST_END -->
<!-- EMPIRICAL_FIRST_START -->
   - **Structured scorer only, on revisions (N ≥ 2):** also pass the prior theory draft (`output/stage2/theory_draft_v{N-1}.md`) and the prior identification, empirics, data-integrity, and data-selection audit reports if they were re-fired alongside the theory revision. (Empirical-first has no math audit's `## Unverified claims` section to read; the analogous "what was unresolved last round" content lives in the prior audit REVISE notes from `output/stage3a/`.) Do NOT pass any prior scorer output or prior score to either agent.
<!-- EMPIRICAL_FIRST_END -->
2. Save results to `output/stage4/scorer_decision_vN.md` and `output/stage4/scorer_freeform_vN.md`
3. Commit: `artifact: scorer decisions v{N} (structured + freeform)`

**Agent:** `branch-manager`

4. Launch branch-manager with:
   - Theory draft: `output/stage2/theory_draft_vN.md`
   - Both scorer outputs: `output/stage4/scorer_decision_vN.md`, `output/stage4/scorer_freeform_vN.md`
   - Full score history from `process_log/pipeline_state.json`
   - Stage 1 idea sketches: all `output/stage1/idea_sketches_r*.md` files (all rounds, not just r1)
   - Stage 1 candidate selection: `output/stage1/candidate_selection.md` (which top-K candidates were screened and why the current idea won — so branch-manager does not recommend returning to already-eliminated sketches)
   - Pipeline state: `process_log/pipeline_state.json`
   - Self-attack + triage: `output/stage4/self_attack_vN.md`, `output/stage4/triage_vN.md`
   - **Self-attack quality flag:** if `process_log/self_attack_premise_skip_vN.md` exists (step 3a re-fire failed) OR the scorer output's prepended `Self-attack quality:` line flags a missing load-bearing premise, instruct branch-manager to treat severity ≥ 7 Completeness/robustness attacks in the triage with skepticism — they are not anchored to the load-bearing question and should not by themselves drive a REWORK or escalation. The branch-manager's read of Rigor/Parsimony should mirror the scorer's calibration, not amplify it.
<!-- THEORY_FIRST_START -->
   - Free-form audit: `output/stage2/freeform_audit_vN.md`
<!-- THEORY_FIRST_END -->
<!-- EXT_EMPIRICAL_START -->
   - Identification audit: `output/stage3a/identification_audit.md`; empirics audit: `output/stage3a/empirics_audit.md`
<!-- EXT_EMPIRICAL_END -->
   - Literature map: `output/stage0/literature_map.md`
5. Save result to `output/stage4/branch_manager_vN.md`
6. Commit: `artifact: branch-manager report v{N}`
7. Read the branch-manager report. The gate decision must be consistent with its recommendation. If you disagree, log the disagreement and your reasoning in the commit message — do not silently override. **Gate 4 is invalid without a fresh `output/stage4/branch_manager_vN.md` for the current version N. If the file does not exist or is from an earlier version, re-run branch-manager before any gate decision — no exceptions.** If §E recommends **Regenerate**, branch-manager writes `output/stage1/learnings_r{N}.md` with N = (current `regeneration_round` + 1); the orchestrator then runs the canonical **Regeneration entry procedure** (`docs/stage_1.md` "Regeneration entry procedure (canonical)") — increment `regeneration_round`, archive the paper + record `archived_best_score_r{N}`, reset state per that procedure (the non-loop version fields plus **every** `loops.<id>.round → 0` via the generic Audit-loop scoping rule), and re-enter Stage 1. Do not perform a partial reset here and do not re-derive a counter list — the canonical procedure zeroes every loop in full to prevent stale-budget bleed into the regenerated paper.

8. Read the **structured scorer** output (`scorer_decision_vN.md`). It contains two sections:
   - **Content score + content feedback**: determines the gate decision. Only substantive theory issues (new math needed, proofs to fix, mechanisms to clarify).
   - **Presentation notes**: expositional improvements (reframe abstract, soften claims, reorder sections). These do NOT affect the score or gate decision. Save them — they are forwarded to the paper-writer at Stage 5.
   Also read the **freeform scorer** output (`scorer_freeform_vN.md`) for holistic assessment; if the freeform scorer's score estimate diverges significantly (±10 points) from the structured score, note the discrepancy and factor it into the branch-manager review.
9. Use the **content score** for state-dependent escalation. **Read `target_journal_tier` from `process_log/pipeline_state.json`** to select the correct row of the table below — this field is initialized to `{{INITIAL_TIER}}` at setup but may be updated mid-run by the Stage 6 `editor` agent (Downgrade or Upgrade recommendations, see `docs/stage_6.md` "Journal-fit handling"). Do not assume the original target tier; always read the current value. The variant's tier ladder is `{{TIER_LADDER_PROSE}}`.

**Scoring is absolute** — 80 means top-5 journal quality regardless of target. The advance threshold depends on the target journal tier. Default tiers (variant-specific):

{{TIER_TABLE}}

**1st scorer evaluation** (no prior score): use the band from the table above.

**Subsequent evaluations** (has a prior score): the CONTINUE-vs-ESCALATE call is driven by `branch-manager`'s **SUBSTANTIVE / COSMETIC** verdict on the v(N)→v(N−1) diff (a content judgment about whether the draft actually changed), *not* by a raw numeric delta — a few points of score movement is not, by itself, the signal.

| Condition | Action |
|-----------|--------|
| Score ≥ advance threshold | **ADVANCE** |
| Score < abandon threshold | **ABANDON** |
| Change is **SUBSTANTIVE** (per branch-manager) | **CONTINUE** — the deepening is working; one more iteration in the current band |
| Change is **COSMETIC** (per branch-manager) | **ESCALATE** — reframing is not progress (see "Substantive vs cosmetic delta" below) |
| Score < (advance threshold + 5) on attempt 3+ | **Deepening check first.** In the REVISE band, apply the deepening playbook before escalating — close-but-below after two revisions usually means the core needs more depth, not a new core; escalate only if deepening yields no substantive gain. In the REWORK/ABANDON band, escalate (toward Regenerate) regardless. |

**Hard ceiling:** after 8 total scorer evaluations on the same problem, escalate one level regardless of trajectory.

**Substantive vs cosmetic delta.** Branch-manager classifies the v(N)→v(N−1) diff at every Gate 4 (Section A of its report). The orchestrator uses that verdict; on COSMETIC, escalate even if the score rose.

- **Substantive:** new theorem/lemma/proposition with proof, new proof of a previously-conjectured claim, removed or narrowed unverified claim, new mechanism with economic content, new comparative static derived from the model, new load-bearing extension or scope condition, empirical/numerical result that changes a calibration.
- **Cosmetic** (treat as typos — fixable when wrong, but score-neutral): rewording the contribution sentence, reorganizing sections, sharper or narrower abstract framing, broader-interpretation paragraphs invoking larger phenomena without new results, label promotions or demotions (Lemma ↔ Theorem) without new content, restructuring the paper around an already-existing result (promoting a different result to the headline) without new math, renaming a variable or mechanism, additional defensive prose.
  - *Emergent-headline carve-out:* selecting or centering the headline on a result that was **newly developed in this cycle** (emergent-headline selection at Stage 2b, for an open approach) is **substantive, not cosmetic** — the result is new content the development produced, not a relabelling. Cosmetic covers only re-headlining among results that already existed without new math.

Record all content scores in `process_log/pipeline_state.json` under `"scores"` so the trajectory can be computed: `"scores": { "v1": 60, "v2": 63, "v3": 67 }`.

{{SEED_OVERRIDE_STAGE_4_GATE_4}}

10. If REVISE/REWORK: pass only the **content feedback** to the theory-generator. Do NOT pass presentation notes — those are for the paper-writer.
11. Update `process_log/pipeline_state.json` accordingly
12. Commit: `pipeline: gate 4 — scorer {DECISION} (score: {N})`
