## Seeded idea mode

**This project was initialized with a pre-developed idea.** The idea files are in `output/seed/`.

### Entry: read and triage

1. **Read the seed.** Read all files in `output/seed/` (ignore `README.md`). Understand what the user provided — it could be anything from a vague question to a complete theory with proofs to an empirical plan.
2. **Build the literature map.** Launch `literature-scout` → `output/stage0/literature_map.md`. Always done regardless of maturity.
3. **Assess maturity and enter the pipeline at the appropriate stage.** Populate all prior-stage artifacts (problem statement, selected idea, theory draft, etc.) as needed to bring the pipeline up to the entry point. Preserve the user's framing and mechanism — do not reinterpret. Update `pipeline_state.json` to the chosen entry point and commit.

### Fallback overrides

**Never silently abandon the seeded idea.** When a gate fails, report and attempt recovery instead of pivoting:

- **Gate 1b KNOWN**: Report to `output/seed/novelty_concern.md`, then proceed — the contribution may be in the execution/proof.
- **Gate 1c BLOCKED**: Report to `output/seed/prototype_blockage.md`. Try one alternative formalization; if still blocked, stop and report.
- **Gate 2 FAIL**: Revise theory in place (preserve mechanism). After 3 failures, stop → `output/seed/abandon_report.md`.
- **Gate 3 KNOWN**: Report to `output/seed/novelty_concern_theory.md`. Try one reformulation; if still KNOWN, stop and report.
- **Gate 4 REWORK**: Return to Stage 2 with feedback, keeping the seed's core mechanism.
- **Gate 4 ABANDON**: Stop → `output/seed/abandon_report.md` with post-mortem. Do not pivot.
- **Referee Reject**: Revise and resubmit. After 2 "fundamental flaw" rejections, stop and report.

The pipeline's job is to *execute* the user's idea — not to second-guess whether a better idea exists.
