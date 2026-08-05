### Faithful-mode override (applies because `faithful: true` in `pipeline_state.json`; supersedes the seeded-mode override)

The triager's verdict table is modified in faithful mode:

- **NORMAL-PROCEED**: unchanged.
- **FIX-EMPIRICS**: unchanged.
- **RECONCILE**: allowed only if the added scope condition does not exclude a contract invariant. A scope condition that collapses the seed's named mechanism to a trivial sub-case is a rescope, not a scope tightening, and is **forbidden**. If the only available reconciliation excludes a contract invariant, route to HONEST-NULL instead.
- **PIVOT**: **forbidden in faithful mode.** Reroute to HONEST-NULL. The faithful run does not produce a paper whose headline contribution is a mechanism the seed never proposed; documenting an honest contradiction is the correct outcome.
- **BACK-TO-IDEA**: **forbidden in faithful mode.** The seed is the contract. If neither RECONCILE nor FIX-EMPIRICS resolves the contradiction, escalate to HONEST-NULL.
- **HONEST-NULL**: the dominant fallback in faithful mode. Document the failed prediction in `output/seed/limitations.md` and ship the paper with the seed's mechanism intact, framed honestly as "we implemented X faithfully; the data contradicts X; we report this as a null result." Do NOT return to Stage 0 or Stage 1.

Append a row to `process_log/pivot_log.md` recording the triager's verdict, the faithful-mode classification, and the rationale.
