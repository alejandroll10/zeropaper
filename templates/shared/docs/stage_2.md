# Stage 2: Theory Development

**Agent:** `theory-generator`

1. Read `output/stage1/selected_idea.md`, `output/stage1/idea_prototype.md`, `output/stage0/problem_statement.md`, and `output/stage0/literature_map.md`
2. Choose strategy:
   - Attempt 1: develop the selected idea into a full theory, building on the prototype's derivation
   - Attempt 2+: mutate (if previous attempt had good elements) or fresh with different approach
3. Launch theory-generator with the selected idea, problem statement, literature map, and strategy
4. Save result to `output/stage2/theory_draft_vN.md` where **N = `theory_version`** from `pipeline_state.json`. On a fresh `theory_attempt`, reset `theory_version` to 1. On each mutation (including re-launches after Gate 2 FAIL within the same attempt), increment `theory_version` and save to the new version file. N is a within-attempt counter — it does not reset across attempts within the same pipeline run, but it can collide across attempts; this is fine because attempts overwrite prior files and only the latest version matters downstream.
5. Commit: `artifact: theory draft v{N}`

## Gate 2: Math Audit (structured + free-form)

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
   - Keep iterating as long as the error count is decreasing (making progress). Escalate only if errors plateau or increase across two consecutive attempts — treat as theory failure, **increment `theory_attempt` AND reset `theory_version` to 1** (the next draft is `theory_draft_v1.md` under the new attempt)
   - **After every 3rd theory version on the same attempt** (i.e., when `theory_version % 3 == 0`): launch branch-manager with the current draft, audit feedback, idea sketches, and literature map (no scorer output — sections A and score references will be empty). If it recommends restart, escalate to Stage 1 with a different sketch rather than continuing to patch.
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

## Gate 3: Novelty Check on Full Theory

**Agent:** `novelty-checker`

2nd novelty check. The idea passed at Gate 1b, but the full theory may overlap with prior work the sketch didn't reveal — novel mechanism, known result, or convergence to an existing framework.

1. Launch novelty-checker on `output/stage2/theory_draft_vN.md`
2. Save result to `output/stage2/novelty_check_vN.md`
3. If KNOWN: abandon this theory, return to Stage 2 with new approach (increment `theory_attempt`, reset `theory_version` to 1)
4. If INCREMENTAL: return to Stage 2 with novelty feedback (increment `theory_version`). Theory must deliver a result the literature doesn't already contain — scorer will hard-fail H4 on INCREMENTAL. After Gate 2 + Gate 3 pass on the reworked theory, **re-run Stage 3a (exploration) AND Stage 3 (implications) before proceeding** — the theory changed, so `implications.md` and `exploration.md` are stale.
5. If NOVEL: proceed to Stage 3a (theory exploration)
6. Commit: `artifact: novelty check v{N} — {NOVEL/INCREMENTAL/KNOWN}`

## Stage 3a: Theory Exploration

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
