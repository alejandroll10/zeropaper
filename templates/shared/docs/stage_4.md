# Stage 4: Self-Attack

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

## Gate 4: Scorer Decision

**Agents:** `scorer` + `scorer-freeform` (launched in parallel — neither sees the other's output)

1. Launch both scorers in parallel with the same inputs:
   - Theory draft: `output/stage2/theory_draft_vN.md`
   - Math audit (structured): `output/stage2/math_audit_vN.md`
   - Math audit (free-form): `output/stage2/freeform_audit_vN.md`
   - Theory exploration: `output/stage3a/exploration.md` (if available — computational verification and diagnostic plots)
   - Novelty check (idea): `output/stage1/novelty_check_idea.md`
   - Novelty check (theory): `output/stage2/novelty_check_vN.md`
   - **Implications with lit-check tags:** `output/stage3/implications.md` (for the SUPPORTED-cap / PUZZLE-CANDIDATE-floor rules on Surprise)
   - **Pipeline state:** pass `pivot_round` and `pivot_resolved` so the scorer knows whether a pivot fired and whether it resolved
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

8. Read the **structured scorer** output (`scorer_decision_vN.md`). It contains two sections:
   - **Content score + content feedback**: determines the gate decision. Only substantive theory issues (new math needed, proofs to fix, mechanisms to clarify).
   - **Presentation notes**: expositional improvements (reframe abstract, soften claims, reorder sections). These do NOT affect the score or gate decision. Save them — they are forwarded to the paper-writer at Stage 5.
   Also read the **freeform scorer** output (`scorer_freeform_vN.md`) for holistic assessment; if the freeform scorer's score estimate diverges significantly (±10 points) from the structured score, note the discrepancy and factor it into the branch-manager review.
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

{{SEED_OVERRIDE_STAGE_4_GATE_4}}
