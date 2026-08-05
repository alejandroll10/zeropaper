### Seeded-mode override (applies because `seeded: true` in `pipeline_state.json`)

Gap-scout runs for **context only**. Its verdict of "closed" or "heavily crowded" does **NOT** trigger Step 0b re-entry — the seed is the gap, the pipeline is committed. Instead:
- Save the concern to `output/seed/novelty_concern.md` (if not already written by Gate 1b).
- Extract the closest-competitor list and pass it forward to idea-generator (Stage 1) and paper-writer (Stage 5) so the paper positions against it.
- Proceed regardless of the verdict. Do not loop. **The seed is the question** — do NOT launch `question-poser` (Step 0d) or `question-referee` (Step 0e). Instead back-fill `output/stage0/problem_statement.md` from the seed per the `seed_triage` entry procedure (faithful: reproduce the contract's question verbatim), then continue from the appropriate downstream stage.
