## Seeded idea mode

**This project was initialized with a pre-developed idea.** The idea is in `output/seed/user_idea.md`. Do NOT run Stages 0–1 from scratch. Instead, follow this modified entry sequence:

### Entry sequence

1. **Read the seed.** Read `output/seed/user_idea.md` carefully. This is the user's idea — it may be a polished sketch, a raw email, an evaluation, or a full description. Extract the core research question and proposed mechanism/method.

2. **Build the literature map.** Launch `literature-scout` to search for prior work relevant to the seeded idea. Save to `output/stage0/literature_map.md`. Commit: `pipeline: seeded — literature map built`. This step is NOT skipped — even seeded ideas need a proper lit map.

3. **Synthesize a problem statement.** From the seed + literature map, write `output/stage0/problem_statement.md`. Frame the problem the way the seed frames it — do not reinterpret or pivot the research question. Commit: `pipeline: seeded — problem statement synthesized`.

4. **Write the selected idea.** Translate the seed into the format expected by downstream stages. Save to `output/stage1/selected_idea.md`. Preserve the user's framing, mechanism, and key claims. Do not dilute or generalize. Commit: `artifact: seeded — selected idea written`.

5. **Update `process_log/pipeline_state.json`** — verify `current_stage` is `gate_1b`, add history entries (format: `{ "timestamp": "ISO-8601", "event": "description" }`) for each completed step. Commit: `pipeline: seeded idea ingested — entering at Gate 1b`.

6. **Enter at Gate 1b.** Run the novelty check on the selected idea. Then proceed through Gate 1c (prototype) and onward as normal.

### Fallback overrides for seeded ideas

The standard pipeline abandons ideas and restarts from Stage 0 or Stage 1 when gates fail. **For seeded ideas, never silently abandon the user's idea.** The overrides:

| Standard fallback | Seeded override |
|---|---|
| Gate 1b KNOWN → kill idea, back to Stage 1 | **Report the finding.** Write the novelty concern to `output/seed/novelty_concern.md` with the specific prior work found. Then proceed anyway — the user may know something the checker doesn't, or the contribution may be in the execution/proof, not the high-level idea. Flag it prominently in the theory draft so the paper addresses it head-on. |
| Gate 1c BLOCKED → back to Stage 1 | **Report the blockage** to `output/seed/prototype_blockage.md`. Attempt one alternative formalization before giving up. If still blocked, stop the pipeline and report — do not pivot to a different idea. |
| Gate 2 FAIL (math audit) → revise theory | **Same as standard** — revise the theory in place using audit feedback. The seeded idea's mechanism is preserved; only the formalization changes. After 3 failed attempts, stop and report to `output/seed/abandon_report.md` — do not generate a new idea. |
| Gate 3 KNOWN (novelty on full theory) → new approach | **Report to `output/seed/novelty_concern_theory.md`** with the specific overlap found. Attempt one reformulation that differentiates from the prior work. If still KNOWN, stop and report — do not abandon the seed for a new idea. |
| Gate 4 REWORK → back to Stage 1 | **Revise the seeded idea in place.** Return to Stage 2 with scorer feedback, keeping the seed's core mechanism. Do not generate new ideas from scratch. |
| Gate 4 ABANDON → back to Stage 0 | **Stop and report.** Write a detailed post-mortem to `output/seed/abandon_report.md` explaining why the idea cannot be developed into a publishable paper. Do not pivot to a new problem. |
| Referee Reject → back to Stage 1 | **Revise and resubmit.** Use referee feedback to strengthen the paper. Do not abandon the seeded idea. After 2 rejections with "fundamental flaw," stop and report. |

### Tone

The user trusted the pipeline with a specific idea. Treat it as a collaborator's idea, not a starting point to be improved upon. The pipeline's job is to *execute* it — validate, formalize, prove, write — not to second-guess whether a better idea exists.
