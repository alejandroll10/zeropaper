# Stage 6: Referee Simulation

**Agents:** `referee` + `referee-freeform` (launched in parallel — neither sees the other's output)

1. Delete any previous referee reports in `paper/referee_reports/` matching the pattern `*_v*.md` (i.e., `YYYY-MM-DD_vN.md` and `..._vN_freeform.md`).
2. Launch both referees in parallel (fresh context, no knowledge of development process). Provide save paths: structured → `paper/referee_reports/YYYY-MM-DD_vN.md`, freeform → `paper/referee_reports/YYYY-MM-DD_vN_freeform.md`
3. Commit after both complete
4. Commit: `pipeline: stage 6 — referee reports received (structured + freeform)`

## Gate 5: Referee Decision

Read both referee reports. The structured referee provides numbered comments with action tags; the free-form referee provides editorial assessment and publishability verdict. Use both to inform the decision:

| Recommendation | Action |
|---------------|--------|
| **Accept / Minor Revision** | Fix minor comments, proceed to Stage 7 (style check). |
| **Major Revision / Revise and Resubmit** | **Triage first.** Launch `triager` with: inputs = current round structured + freeform referee reports, output path = `paper/referee_reports/triage_rN.md` (N = `referee_round`), context = `gate-5`. Triager applies the rules (no silent downgrade of referee `[FIX]`, written justifications for downgrades) and judges each round on its merits. Do not edit the triager's output — if you disagree, re-launch with explicit instructions, do not silently override. Then revise only the `[FIX]` items. When a referee challenges an assumption, first try to prove the result without it or characterize exactly when it fails — weakening claims is the last resort (per "characterize, don't just prove"). **Increment `referee_round` in `pipeline_state.json` before re-running Stage 6.** Re-run Stage 6. Max 10 rounds (i.e., stop when `referee_round >= 10`); keep going as long as the triager reports any `[FIX]` items in the current round (the triager is stateless — it does not distinguish "new" from "carried forward"; any `[FIX]` indicates outstanding work). |
| **Reject** | Read the rejection reasons. If fixable: return to Stage 2 with referee feedback. If fundamental: return to Stage 0. |

{{SEED_OVERRIDE_STAGE_6_GATE_5}}
