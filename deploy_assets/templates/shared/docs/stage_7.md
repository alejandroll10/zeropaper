# Stage 7: Style Check

**Agent:** `style`

1. Launch style agent on the paper, and in the same message launch Stage 8's first `bib-verifier` pass (`docs/stage_8.md` step 1): style never edits citations or the bibliography, so that check does not have to wait for it. It edits mechanical violations directly in `paper/sections/*.tex` and writes flagged judgment calls to `paper/style_report.md`. **If `paper/internet_appendix.tex` is non-empty beyond the placeholder skeleton, also tell style explicitly to scan it (and any `paper/sections/internet_appendix/*.tex` files) — the style agent body covers IA scope, but the agent will not self-discover the IA without prompt instruction.**
2. Read `paper/style_report.md`. For each flagged item, decide whether to act — edit the section file if the fix is clear, leave it if the original reads better.
3. Commit the style edits and any operator follow-up edits: `pipeline: stage 7 — style edits`. No evidence checkpoint runs here; `stage9-final` re-checks the final bytes (`docs/results_evidence.md`). The `"status": "complete"` flag is set in Stage 10 (lessons), after Stage 9 polish stabilizes and the orchestrator writes the two lessons documents.
