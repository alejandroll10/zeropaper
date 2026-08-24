### Faithful-mode override (applies because `faithful: true` in `pipeline_state.json`; supersedes the seeded-mode override)

<!-- DATA_FIRST_START -->
**Data-first reading of this override.** **RECONCILE** = a construction-scope statement (the published result under its convention, this dataset's under ours, both reported); it is allowed unless the scoping excludes a contract invariant (e.g., collapses a contract-named event class to a trivial sub-case). **PIVOT remains forbidden** — promoting the failed replication to the paper's *headline* would replace the contract's stated contribution. The evidence itself is not suppressed: document the failed replication, with the side-by-side construction analysis as far as it was run, in the validation section as a non-replication and in `output/seed/limitations.md` — reporting it as an *additional finding* under the contract's headline is allowed and encouraged; re-headlining around it is not. **HONEST-NULL** remains the dominant fallback.
<!-- DATA_FIRST_END -->
The triager's verdict table is modified in faithful mode:

- **NORMAL-PROCEED**: unchanged.
- **FIX-EMPIRICS**: unchanged.
- **RECONCILE**: allowed only if the added scope condition does not exclude a contract invariant. A scope condition that collapses the seed's named mechanism to a trivial sub-case is a rescope, not a scope tightening, and is **forbidden**. If the only available reconciliation excludes a contract invariant, route to HONEST-NULL instead.
- **PIVOT**: **forbidden in faithful mode.** Reroute to HONEST-NULL. The faithful run does not produce a paper whose headline contribution is a mechanism the seed never proposed; documenting an honest contradiction is the correct outcome.
- **BACK-TO-IDEA**: **forbidden in faithful mode.** The seed is the contract. If neither RECONCILE nor FIX-EMPIRICS resolves the contradiction, escalate to HONEST-NULL.
- **HONEST-NULL**: the dominant fallback in faithful mode. Document the failed prediction in `output/seed/limitations.md` and ship the paper with the seed's mechanism intact, framed honestly as "we implemented X faithfully; the data contradicts X; we report this as a null result." Do NOT return to Stage 0 or Stage 1.

Append a row to `process_log/pivot_log.md` recording the triager's verdict, the faithful-mode classification, and the rationale.
