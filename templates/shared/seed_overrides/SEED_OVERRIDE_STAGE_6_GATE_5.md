### Seeded-mode override (applies because `seeded: true` in `pipeline_state.json`)

Referees do not know this is a seeded project. They may recommend reframing the paper, switching to a different mechanism, or pursuing a "more important" adjacent question. **When triaging the editor's canonical comment list at Gate 5, apply the seed-contract filters below in addition to the normal triage rules.** The filtering is the triager's job, not the editor's — the editor aggregates referee verdicts impartially per its own rules; the seed contract enters at the triage step.

**Reject**: revise and resubmit with what the seed pins intact. Stop and write a post-mortem to `output/seed/abandon_report.md` only after **2 rounds where the editor's aggregated verdict was Reject (i.e., the Reject row in stage_6.md fired) and the rejection cites genuinely fundamental flaws in the seed's own claims** — not in the choice of topic or framing. A Reject vote that the editor escapes to Major Revision + Downgrade per its Rule 2 (tier-fit escape) does **not** count toward this 2-rejection threshold; the seed's mechanism was not judged fundamentally flawed in that case, only the journal target was. Do NOT return to Stage 0 or Stage 1.

**Major Revision**: when triaging the editor's canonical comment list, apply these rules in addition to the normal `[FIX]`/`[LIMITS]`/`[RESPONSE]`/`[NOTE]` tags:
- "Paper would be stronger if about X instead" → `[RESPONSE]` (response letter only, no main-text change).
- "The mechanism is wrong, try Y" → adopt Y ONLY if required for mathematical correctness. If Y is merely "more publishable," classify as `[RESPONSE]`.
- "Scope is too narrow" → if the seed intentionally constrains scope, classify as `[LIMITS]` (one sentence in limitations) rather than `[FIX]`.
- Comments on math, derivations, missing proofs, identification → `[FIX]` as normal.

**Mechanism referee verdicts (`referee-mechanism`)**: the mechanism referee evaluates whether the paper's economic mechanism is the one the math delivers. The default stage_6.md rules say MISATTRIBUTED forces rewriting around the actual driver and DECORATIVE forces restructure-or-narrow. In seeded mode, filter these against the seed contract:

- **MECHANISM-VALID / MECHANISM-PARTIAL** — apply normally.
- **MECHANISM-MISATTRIBUTED** — the mechanism referee has identified a different driver than the seed claims. Document the finding in `output/seed/mechanism_concern.md`. Revise the **presentation** to match what the math supports — but preserve what the seed pins where it is consistent with the math. If the actual driver is strictly different from the seed's claimed driver, adopt the narrower, math-supported framing as a limitations-acknowledged interpretation rather than rewriting the paper around an unrelated mechanism the seed never intended.
- **MECHANISM-DECORATIVE** — the mechanism referee judges the seed's mechanism to be window dressing. Document the concern in `output/seed/mechanism_concern.md`. Default action is the **narrow path** from stage_6.md's DECORATIVE rule: strip unsupported generality and present what the math actually delivers as a structural characterization, preserving the seed's topic. Do NOT switch topics or invent an unrelated mechanism. DECORATIVE does NOT count toward the 2-rejection abandon threshold.

The seed is the contract. Referee feedback refines execution, not direction.
