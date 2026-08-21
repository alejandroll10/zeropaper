# Stage 7: Style Check

**Agent:** `style`

1. Launch style agent on the paper. It edits mechanical violations directly in `paper/sections/*.tex` and writes flagged judgment calls to `paper/style_report.md`. **If `paper/internet_appendix.tex` is non-empty beyond the placeholder skeleton, also tell style explicitly to scan it (and any `paper/sections/internet_appendix/*.tex` files) — the style agent body covers IA scope, but the agent will not self-discover the IA without prompt instruction.**
2. Read `paper/style_report.md`. For each flagged item, decide whether to act — edit the section file if the fix is clear, leave it if the original reads better.
3. Run `docs/results_evidence.md` with checkpoint `stage7-style` on the post-style paper. Only its bound PASS may proceed to Stage 8.
4. Commit the style edits, any operator follow-up edits, PASS audit artifacts, and bound paper receipt together: `pipeline: stage 7 — style edits and evidence gate passed`. Do not commit unaudited paper bytes as an intermediate Stage 7 state. The `"status": "complete"` flag is set in Stage 10 (lessons), after Stage 9 polish stabilizes and the orchestrator writes the two lessons documents.
