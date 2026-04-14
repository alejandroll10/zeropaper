### Seeded-mode override (applies because `seeded: true` in `pipeline_state.json`)

The triager's verdict table is modified in seeded mode:

- **NORMAL-PROCEED**: unchanged.
- **FIX-EMPIRICS**: unchanged.
- **RECONCILE**: unchanged — adding scope conditions preserves the seed.
- **PIVOT**: **allowed and encouraged**. The PIVOT strategy preserves the original theory as a nested / baseline case — it does NOT abandon the seed. The seed's mechanism becomes the "what naive intuition would predict" baseline, and the pivoted theory explains the contradiction. Note the pivot in `output/seed/pivot_note.md`. Normal 2-pivot cap still applies.
- **BACK-TO-IDEA**: **forbidden in seeded mode**. Do NOT return to Stage 1. Instead, first try RECONCILE (add scope conditions) or FIX-EMPIRICS (improve measurement). If neither is possible, force-escalate to HONEST-NULL; the seed's idea stays intact.
- **HONEST-NULL**: acceptable and often the right call. Document the failed prediction in the paper's limitations; ship with the seed's idea framed honestly as "a model whose prediction the data contradicted, with explanation limited to what the current theory supports." Do NOT return to Stage 0.
