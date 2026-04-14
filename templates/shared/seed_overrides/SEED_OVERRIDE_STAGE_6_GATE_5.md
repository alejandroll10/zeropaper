### Seeded-mode override (applies because `seeded: true` in `pipeline_state.json`)

Referees do not know this is a seeded project. They may recommend reframing the paper, switching to a different mechanism, or pursuing a "more important" adjacent question. **Filter referee recommendations against the seed's contract.**

**Reject**: revise and resubmit with the seed's mechanism intact. Stop and write a post-mortem to `output/seed/abandon_report.md` only after **2 rejections citing genuinely fundamental flaws in the seed's own claims** (not in the choice of topic or framing). Do NOT return to Stage 0 or Stage 1.

**Major Revision**: when triaging referee comments, apply these rules in addition to the normal `[FIX]`/`[LIMITS]`/`[RESPONSE]`/`[NOTE]` tags:
- "Paper would be stronger if about X instead" → `[RESPONSE]` (response letter only, no main-text change).
- "The mechanism is wrong, try Y" → adopt Y ONLY if required for mathematical correctness. If Y is merely "more publishable," classify as `[RESPONSE]`.
- "Scope is too narrow" → if the seed intentionally constrains scope, classify as `[LIMITS]` (one sentence in limitations) rather than `[FIX]`.
- Comments on math, derivations, missing proofs, identification → `[FIX]` as normal.

The seed is the contract. Referee feedback refines execution, not direction.
