# Stage 9: Polish

**Agents:** `polish-consistency`, `polish-formula`, `polish-numerics`, `polish-institutions`, `polish-equilibria`, `polish-bibliography`, `polish-prose`

This is the final substantive pass before the pipeline marks the paper complete. It runs *after* style edits (Stage 7) and *after* bibliography verification (Stage 8) — by this point the references file is clean, mechanical style is fixed, and the prose is in its final form. The seven polish agents read that final form with disjoint, focused checklists and produce structured fix lists. Together they catch the failure modes that referees flag immediately and that earlier pipeline stages systematically miss — because the upstream auditors ran against `output/theory.md`, not the rendered LaTeX, and because cross-section consistency, calibration sanity, institutional realism, and prose economy were never anyone's job.

Stage 9 hands off to Stage 10 (Lessons), which owns the `"status": "complete"` flag. The pipeline is not done until polish has either applied its fixes or judged that nothing actionable remains *and* the orchestrator has written the two lessons documents.

## Procedure

1. **Initialize the round.** Read `polish_round` from `process_log/pipeline_state.json`. On first entry to Stage 9, increment it from 0 to 1 (so the first round writes `_r1.md` files). On a re-run after step 6 below, increment again. All polish artifacts in this round use the suffix `_r{N}.md` so prior rounds are preserved on disk.

2. **Launch all seven polish agents in parallel.** Pass each agent the current `polish_round` value `{N}` in its prompt. Each reads `paper/main.tex`, the included sections, and (where relevant) `output/theory.md`. **Extension-aware inputs:** if `--ext empirical` is enabled and `output/stage3a/empirical_analysis.md` exists, also pass that path to `polish-numerics` (so it can verify numerical claims grounded in regression output) and `polish-consistency` (so it can catch prose that contradicts the empirical findings). If `--ext theory_llm` is enabled and `output/stage3b/experiment_results.md` exists, pass that path to `polish-numerics` and `polish-consistency` for the same reasons. Each agent writes its own report:
   - `output/polish_consistency_r{N}.md`
   - `output/polish_formula_r{N}.md`
   - `output/polish_numerics_r{N}.md`
   - `output/polish_institutions_r{N}.md`
   - `output/polish_equilibria_r{N}.md`
   - `output/polish_bibliography_r{N}.md`
   - `output/polish_prose_r{N}.md`

   Run them in parallel — they have no dependencies on each other and write to disjoint output paths.

3. **Aggregate via `triager`** (Stage 9 context — see the triager body's "Stage 9 output format" section). Launch the `triager` agent with the seven polish report paths as input and instruct it to write `output/polish_triage_r{N}.md`. The triager classifies each finding into three buckets per its Stage 9 rules (4, 5, and 6):
   - **Apply** — concrete fixes the agents identified with sufficient evidence (verbatim quote + suggested fix); criticals default to Apply, polish-formula criticals always Apply (rule 4 override), same-anchor findings across agents are deduplicated, and polish-prose cuts that conflict with another agent's keep/fix at the same anchor are dropped (rule 6).
   - **Investigate** — major-severity findings that lack a one-token fix and need paper-writer judgment, or criticals downgraded from Apply with a concrete justified conflict.
   - **Drop** — minor-severity findings that aren't one-token edits, plus any item the triager justifies dropping. Each drop has a one-line written justification.

4. **Re-launch `paper-writer` with the triaged list.** In the prompt, pass the *resolved* path with `{N}` substituted to the current round integer (e.g., `output/polish_triage_r1.md`, not the variable form). Paper-writer's body has a "When re-invoked at Stage 9" section that handles Apply / Investigate rows. It edits `paper/sections/*.tex` to incorporate the Apply fixes and drafts candidates for Investigate items, appending a `## Investigate decisions` section to the triage file with one sentence per draft. Read that section after paper-writer returns — for each Investigate decision, accept the draft, request a revision, or revert it. Commit: `paper: stage 9 polish — round r{N} fixes applied`.

   If paper-writer's Stage 9 fixes added or removed citations (regardless of which polish agent flagged them), re-launch `bib-verifier` once on the new state to confirm. This is a one-shot confirmation, not a return to Stage 8. **Do not increment `bib_verify_round` for this call** — it is a post-polish sanity check, not a Stage 8 loop iteration. The Stage 8 cap (`bib_verify_round >= 2`) does not apply.

5. **Re-run `style` once on the post-polish prose.** Polish edits — especially polish-prose consolidations and polish-consistency rephrasings — are prose-shaped, so style violations may have been reintroduced into prose that was style-clean after Stage 7. Launch `style` with the same prompt shape it received at Stage 7; it will edit `paper/sections/*.tex` directly for mechanical fixes and append judgment calls to `paper/style_report.md` (style is idempotent on inputs it already governs and will not undo polish edits, only enforce its rules on the new prose). Commit: `paper: stage 9 polish — round r{N} style re-pass`. Skip this step only if paper-writer reported no edits in step 4 (the Apply table was empty after triage).

6. **Re-run polish if there were any Apply-bucket criticals.** If `output/polish_triage_r{N}.md` contained ≥1 row in the `Apply` table tagged `critical`, re-enter Stage 9 from step 1 (increments `polish_round` to N+1). At step 2 of the new round, launch *only the agents whose criticals were applied* — the triage file's "Re-run trigger" line in the summary names them. **Hard cap: at most 2 rounds total (N=1, N=2).** When the round-2 cycle finishes (paper-writer has applied round-2 fixes and style has re-passed), proceed to step 7 regardless of whether criticals remain. If the round-2 triage still contained Apply criticals, ship the partial fix and note the unresolved findings under a "Known limitations" paragraph in `paper/sections/discussion.tex` before Stage 10 marks the pipeline complete.

7. **Hand off to Stage 10.** When polish stabilizes (Apply table contains no `critical` rows, or `polish_round >= 2`), update `current_stage` to `stage_10` in `process_log/pipeline_state.json` and proceed to Stage 10 (`docs/stage_10.md`). Do not set `"status": "complete"` here — Stage 10 owns that flag. Commit: `paper: stage 9 polish — round r{N} stabilized`.

## What each polish agent owns

| Agent | Owns | Does not own |
|---|---|---|
| polish-consistency | Cross-section contradictions, label↔object mismatches, headings vs. text, intro vs. later qualifications | Formula correctness; numerical reproduction |
| polish-formula | Re-derivation of every numbered equation; sign / subscript / abs-value errors paper-writer introduced | Numerical examples; whether prose contradicts the formula |
| polish-numerics | Recomputing every numerical claim; stock-vs-flow; normalized-vs-unnormalized; baseline IR feasibility | Formula correctness; institutional realism of the calibration |
| polish-institutions | Real-world facts (regulatory mechanisms, fee conventions, market sizes); faithful characterization of cited papers | Cite-key validity (bib-verifier); equation correctness |
| polish-equilibria | Multiple equilibria in fixed-point regions; LLN/continuum assumptions; reduced-form↔structural bridges; benchmark choice | Anything mathematically wrong with stated equilibria |
| polish-bibliography | Per-citation prose-claim verification (FAITHFUL/APPROXIMATE/MISCHARACTERIZED/DECORATIVE) | Cite-key existence (bib-verifier) |
| polish-prose | Repeated caveats, hedge stacking, abstract bloat, defensive contribution framing, buried thesis sentences, section-opener resummary | Mechanical style (style agent); contradictions (polish-consistency); whether a caveat is correct |

The deliberate overlap between `polish-institutions` and `polish-bibliography` on egregious citation mischaracterization is fine — both will surface the same critical, the triager will dedupe by anchor. The deliberate subordination of `polish-prose` to every other polish agent (rule 5 precedence + rule 6 removal-vs-fix) is also fine — a prose cut that conflicts with another agent's keep/fix loses, because deletion eliminates the substrate the other agent was editing.

## Notes

- **Manual-mode chaining.** When a user runs polish manually (not via the autonomous orchestrator) they are their own orchestrator: pass `{N}=1` to all seven agents on the first chained run; if anything is re-run after paper-writer applies fixes, pass `{N}=2`. Agent bodies default to `N=1` when no value is supplied, so the round-1 path works out-of-the-box. Canonical four-message manual chain (round 1):
  1. **Parallel launch:** `polish-consistency`, `polish-formula`, `polish-numerics`, `polish-institutions`, `polish-equilibria`, `polish-bibliography`, `polish-prose` — invoke all seven in one batch, each with the prompt "polish_round = 1; read paper/main.tex and paper/sections/*.tex; for empirical/theory_llm projects also read output/stage3a/empirical_analysis.md and/or output/stage3b/experiment_results.md if present".
  2. **Triager:** invoke `triager` with the prompt "Stage 9 context, polish_round = 1; inputs are the seven output/polish_*_r1.md files; write output/polish_triage_r1.md".
  3. **Paper-writer:** invoke `paper-writer` with the prompt "Stage 9 polish round; read output/polish_triage_r1.md and apply the Apply table per your 'When re-invoked at Stage 9' section". Then read the appended `## Investigate decisions` section in the triage file and accept/revert each draft yourself.
  4. **Style re-pass:** invoke `style` with the same prompt shape it used at Stage 7. Skip if paper-writer reported no edits in step 3.

  If the round-1 triage contained Apply criticals, repeat with `polish_round = 2` (only the agents whose criticals were applied) and stop after round 2.
- **Why polish is last, not earlier.** Style (Stage 7) sometimes silently changes a sentence that would have been a polish-consistency finding; bibliography verification (Stage 8) sometimes drops or reanchors cites that would have been polish-bibliography findings. Running polish *after* both means the agents are reading the final form of the paper. Style is then re-run at the end of Stage 9 (step 5) on the post-polish prose so mechanical violations reintroduced by polish edits don't ship. The cost is one wall-clock pass plus one fast style call per polish round.
- **Why a separate stage rather than another referee round?** Referees evaluate the paper's contribution and mechanism; they do not re-derive every equation, recompute every number, or look up every cited paper. The polish agents have narrow, mechanical-but-substantive checklists that referees skip. Running both gets coverage of both failure modes.
- **Why seven agents instead of one?** A single "find everything wrong with this paper" prompt produces shallow coverage of every category. Disjoint, focused prompts produce deeper coverage of each. The cost of seven parallel calls is one wall-clock pass.
- **What if a polish agent contradicts a referee request?** The triager judges. A referee request that survived Stage 6 has higher priority by default — drop the polish finding with a justification. Exception: a polish-formula critical (provably wrong equation) overrides any referee request, because the equation is wrong regardless of what the referee wanted.
- **Polish does not loop with referees.** If the polish agents surfaced a new fundamental issue (rare), commit the partial fix and flag it as a known limitation in the paper's discussion section. Do not reopen Stage 6.
- **Post-pipeline math-audit rule still applies.** Polish runs *inside* the pipeline. After Stage 10 marks `"status": "complete"`, any further proposition/lemma/corollary edits go through the post-pipeline math-audit procedure documented in `core.md`.
