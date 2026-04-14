# Stage 6: Referee Simulation

**Agents:** `referee` + `referee-freeform` (launched in parallel — neither sees the other's output)

1. Delete any previous reports in `paper/referee_reports/`
2. Launch both referees in parallel (fresh context, no knowledge of development process). Provide save paths: structured → `paper/referee_reports/YYYY-MM-DD_vN.md`, freeform → `paper/referee_reports/YYYY-MM-DD_vN_freeform.md`
3. Commit after both complete
4. Commit: `pipeline: stage 6 — referee reports received (structured + freeform)`

## Gate 5: Referee Decision

Read both referee reports. The structured referee provides numbered comments with action tags; the free-form referee provides editorial assessment and publishability verdict. Use both to inform the decision:

| Recommendation | Action |
|---------------|--------|
| **Accept / Minor Revision** | Fix minor comments, proceed to Stage 7 (style check). |
| **Major Revision / Revise and Resubmit** | **Triage first.** Categorize each referee comment using the referee's own tags (`[FIX]`/`[LIMITS]`/`[RESPONSE]`/`[NOTE]`) as a starting point. Only `[FIX]` items trigger main-text revisions. `[LIMITS]` items get one sentence in limitations. `[RESPONSE]` items go in the response letter only. Save triage to `paper/referee_reports/triage_rN.md` where N = `referee_round` from state. Then revise only the `[FIX]` items. When a referee challenges an assumption, first try to prove the result without it or characterize exactly when it fails — weakening claims is the last resort (per "characterize, don't just prove"). **Increment `referee_round` in `pipeline_state.json` before re-running Stage 6.** Re-run Stage 6. Max 10 rounds (i.e., stop when `referee_round >= 10`); keep going as long as each round surfaces at least one genuinely new issue (not a variant of a previously-triaged concern). |
| **Reject** | Read the rejection reasons. If fixable: return to Stage 2 with referee feedback. If fundamental: return to Stage 0. |
