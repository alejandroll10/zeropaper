# INV-5: Delegation & Self-Check Tooling (T11, T12)

**Date:** 2026-05-21
**HEAD at investigation:** d9415f4 (template repo); deployed project inspected: `/tmp/inv_emp`
**Themes:** T11 — Orchestrator does work itself instead of delegating; T12 — Self-check tooling produces misleading failure reports

---

## T11 — Orchestrator Self-Execution Instead of Delegation

### Verdict: PARTIALLY-ADDRESSED

### Sub-question A: Does session.md / core.md contain an explicit delegation rule?

**Finding: The explicit "delegate, don't self-execute" rule exists for Codex and Gemini but is ABSENT from the Claude runtime.**

Evidence:

- `templates/runtime/codex/session.md:31`:
  > "**You must delegate to agents.** Every stage and gate specifies which agent to launch. Launch that agent — do not do the work yourself. You are the orchestrator: you read instructions, launch agents, read their output, make gate decisions, and update state. That is all."
  The same paragraph continues: "**Do not write theory drafts, literature maps, math audits, novelty checks, scorer decisions, self-attacks, referee reports, or paper sections yourself.**"

- `templates/runtime/gemini/session.md:31`:
  Identical rule: "**You must delegate to subagents.** … Launch that agent — do not do the work yourself."

- `templates/runtime/claude/session.md` (41 lines total): Contains session-start procedure, data inventory, agent launch monitoring, and hourly self-check setup. **No delegation anti-pattern rule appears anywhere in the file.** The file is silent on whether the Claude orchestrator may perform agent tasks directly.

- `templates/shared/core.md`: Contains many core principles (sunk cost, no phantom time pressure, surprises as discoveries, tool failure, "do what makes the paper better"). The closest rule is at line 75: "If a tool exists for the task (data skills, codex-math, theory-explorer), use it. Skipping available tools because they're unfamiliar is not acceptable." This addresses tool-skipping but does not name self-execution as an anti-pattern and does not reference agent delegation.

The deployed `CLAUDE.md` at `/tmp/inv_emp` inherits from `templates/shared/core.md` (which provides the core principles) plus `templates/runtime/claude/session.md` (which provides session guidance). Neither source contains the prohibition that Codex and Gemini both carry. A `grep` for "delegate", "anti-pattern", "orchestrator.*itself", "do not.*yourself", or "not the worker" in the deployed CLAUDE.md returns zero hits.

**Gap:** The Claude runtime is missing the explicit "you are the orchestrator, not the worker" prohibition that exists in both other runtimes. Claude is the primary runtime the operator uses (the field report describes a 24/7 Claude Code pipeline). The missing rule is the one most likely to be violated in practice.

### Sub-question B: Is method-checker actually wired into the pipeline?

**Finding: method-checker IS wired in. Issue #15 is substantively closed, but with one structural gap worth noting.**

Evidence:

1. **Stage 3a step 7.5** (`extensions/empirical/docs/stage_3a_empirical.md`, lines 63-71): After `empirics-auditor` PASS, the orchestrator must "Launch THREE auditors **in parallel** (single message, three Agent calls): `data-integrity-auditor`, `data-selection-auditor`, and `method-checker`." The wiring is explicit and mandatory.

2. **The stage doc requires the output file to exist before aggregating** (line 63): "Before aggregating, verify all three output files exist on disk — `output/stage3a/data_integrity_audit.md`, `output/stage3a/data_selection_audit.md`, `output/stage3a/method_check.md`. If any is absent … re-launch only that absent agent … A silently-missing method_check.md treated as PASS-by-omission is exactly the issue-36 failure mode this triad exists to prevent."

3. **Post-pipeline enforcement**: `templates/shared/core.md` (lines 321-322, empirical-first post-pipeline rule) explicitly includes: "If the edit introduced any new named econometric method — a new test statistic, a new estimator, a new sensitivity-analysis routine — also re-fire `method-checker` per the same step 7.5 to verify the new code uses the canonical package."

4. **The agent is assembled in the deployed project**: `/tmp/inv_emp/.claude/agents/method-checker.md` exists and carries the full method-checker body. The skill `/tmp/inv_emp/.claude/skills/canonical-packages/SKILL.md` also exists.

5. **The empiricist body** (`extensions/empirical/agent_bodies/finance/empiricist.md:83`) warns the empiricist directly: "The `method-checker` agent will REVISE you at Stage 3a step 7.5 if any custom implementation of a canonical-available method lacks justification."

**Structural gap — the method-checker does not cover Stage 0 data-inventory through Stage 2b:** method-checker fires at Stage 3a step 7.5 (after the empiricist runs) and on post-pipeline edits. It does not fire during the data-inventory step or during orchestrator activities in earlier stages. If the orchestrator itself (not the empiricist) writes code during an earlier stage — which is exactly the T11 scenario — method-checker would not catch it at Stage 3a because method-checker scans `code/empirical.py` and `code/empirical_post_v*.py`, not orchestrator-authored scripts. This is a narrow but real gap: if T11 self-execution includes writing data-handling code that the empiricist later inherits, that code escapes method-checker unless the empiricist re-touches the relevant file.

**Overall assessment for #15:** The hand-coded-vs-canonical half of T11 is genuinely closed for the empiricist's code path. The remaining gap is the broader delegation failure mode: the orchestrator does work the empiricist should do (or does tasks agents handle), and neither core.md nor claude/session.md names this as forbidden.

### Fix Direction for T11

Add to `templates/runtime/claude/session.md` (in the orchestration discipline section, matching the Codex/Gemini pattern) an explicit rule:

> "**You must delegate to agents.** Every stage and gate specifies which agent to launch. Launch that agent — do not do the work yourself. You are the orchestrator: you read instructions, launch agents, read their output, make gate decisions, and update state. **Do not write theory drafts, literature maps, math audits, novelty checks, scorer decisions, self-attacks, referee reports, empirical analysis, bibliographic checks, or paper sections yourself.** These are agent tasks. If you find yourself writing substantive research content rather than launching an agent, stop and launch the correct agent instead."

This is a direct port of the Codex/Gemini rule to Claude. The session.md currently has no analogous section; the rule should be inserted before the "How to start a session" section or as a dedicated "Orchestration discipline" heading that mirrors the Codex structure.

Additionally, the empirical extension should explicitly note that the orchestrator writing any `code/tmp/` or `code/empirical.py` content directly — rather than via the empiricist agent — is a delegation failure, since such code escapes the Stage 3a step 7.5 method-checker triad.

---

## T12 — Self-Check Tooling Produces Misleading Failure Reports

### Verdict: REPRODUCED (by design gap in the verifier's format handling)

### Symptom recap

The operator reports "92 of 108 passed, 16 failed"; 15/16 were false alarms because the checker could only read one file format; the last was a mislabeled pointer with the correct value. The raw "16 failures" mis-signals fabrication risk when actual risk is zero.

### Finding A: The claim-verifier parses exactly two artifact formats; other formats silently fail as PAPER-SIDE-ERROR

**File:** `extensions/empirical/agent_bodies/shared/claim-verifier.md`

Gate 3 (field-path resolution) documents two — and only two — source artifact formats the verifier knows how to parse:

1. **JSON files** (line 40): "For JSON files: parse the file with `python3 -c "import json,sys; ..."` and walk `entry.field_path` using a deterministic resolver. Dot-paths, bracket-indexed paths, and mixed forms must all resolve via the same resolver."

2. **LaTeX-table sources** (line 41): "For LaTeX-table sources: parse `entry.field_path` as `table_label::row_label::col_N` and confirm the table file contains that label, that row, and that column. A simple Grep + awk pattern suffices."

The empiricist's output format rule (`extensions/empirical/agent_bodies/finance/empiricist.md:94`) says: "**Structured output.** Save results as JSON (`output/stage3a/results.json`) for machine readability AND LaTeX tables (`output/stage3a/tables/`) for direct inclusion in the paper."

So the intended output types match the two formats the verifier handles. However, this assumes the empiricist never writes intermediate results to CSV, parquet, pickle, or other formats that the verifier body does not mention. In practice:
- The WRDS utilities in the deployed project (`/tmp/inv_emp/code/utils/`) download data in structured formats.
- An empiricist that saves a result as `output/stage3a/result.csv` (e.g., a simple table that doesn't warrant a full JSON schema) would cause the grounder to cite it with a field path the verifier cannot resolve.
- When the field path resolution attempt fails on an unrecognized format, the verifier has no explicit handling path — the file exists (Gate 2 passes), but the field path cannot be resolved by either the JSON or LaTeX parsers (Gate 3 fails).

Gate 3 failure classification distinguishes "near-match" (GROUNDER-ERROR/field-typo) from "no near-match" (PAPER-SIDE-ERROR/field-nonexistent). A CSV or parquet source file would fail Gate 3 in the "no-match-anywhere" branch and register as **PAPER-SIDE-ERROR / field-nonexistent** — indistinguishable from a fabricated claim. The verifier has no "unsupported format" failure tag, so there is no way for the orchestrator (or the human reading the report) to distinguish a format-blindness failure from a real fabrication.

This is the structural mechanism that produces the reported "15/16 false alarms": the grounder cited a field in a file format the verifier cannot parse; the verifier flagged it as PAPER-SIDE-ERROR/field-nonexistent; the raw count reads as failures.

### Finding B: The output does NOT separate format-blind failures from substantive failures

The claim-verifier's markdown report (`output/stage5/claim_verification.md`) outputs failures in two GROUNDER-ERROR / PAPER-SIDE-ERROR buckets. There is no third bucket or tag for "verifier could not parse the source file format." The machine-readable summary (`claim_verification_summary.json`) has tags: `field-typo`, `coverage-shortfall`, `cited-vs-source-mismatch`, `invalid-derivation-tag`, `file-missing`, `field-nonexistent`, `value-mismatch`, `derivation-invalid`, `tolerance-undefined`, `needs-empiricist`. None of these is a "format-unsupported" tag. The orchestrator reads `failure_index` entries and the summary counts; it cannot distinguish format-blindness from fabrication.

The "mislabeled-pointer" case in the operator report maps to what the verifier would classify as GROUNDER-ERROR/cited-vs-source-mismatch (the grounder cited a field path whose value does not match the paper) or PAPER-SIDE-ERROR/value-mismatch — both of which look substantive in the count even when the underlying value is correct and only the pointer label is wrong.

### Finding C: The output summary conflates all failures in a single count

The markdown summary table:
```
| Gate | Pass | Fail | Failure breakdown |
| 2 — File existence | | | file-missing: X |
| 3 — Field-path | | | grounder/field-typo: X; paper/field-nonexistent: Y |
| 4 — Value match | | | ... |
```

The "16 failed" headline is the sum of all failure rows across all gates. The breakdown within each gate is present in the table, but:
1. There is no "format-blind" subcategory that a reader can subtract to get the "real" fabrication count.
2. The machine-readable JSON `totals.paper_side_error_count` and `totals.grounder_error_count` are the fields the orchestrator uses for routing. A `paper_side_error_count = 15` (all from format-blind failures) and `paper_side_error_count = 15` (from actual fabrications) are indistinguishable.

### Finding D: The grounder has no format-restriction rule

The claim-grounder body (`extensions/empirical/agent_bodies/shared/claim-grounder.md`) instructs the grounder to "search `output/stage3a/` for a file containing this value in a position consistent with the claim's context." It does not restrict the grounder to JSON or LaTeX files. The grounder can cite a CSV file, a pickle file, or any other artifact format it finds in `output/stage3a/`. Once the grounder cites a non-JSON/non-LaTeX file, the verifier's Gate 3 has no path to resolve the field path, and the failure registers as PAPER-SIDE-ERROR/field-nonexistent.

The grounder body does say to use `Read` to "visually confirm the path lands on the value you intend to cite," but for a CSV the grounder's visual read would succeed (it can see the value) while the verifier's programmatic read fails (it has no CSV parser). This is the exact mismatch the operator encountered.

### Fix Direction for T12

**Fix 1 — Add format-unsupported failure tag to the verifier:**
Add a new Gate 3 failure path: when the source file exists (Gate 2 passes) but the format is neither JSON nor a LaTeX table the verifier can parse, emit **VERIFIER-LIMITATION / format-unsupported** rather than PAPER-SIDE-ERROR/field-nonexistent. This tag must appear as a distinct bucket in both the markdown summary and the machine-readable JSON (`totals.verifier_limitation_count`, with a `verifier_limitation_claim_ids` list). The orchestrator routing on PAPER-SIDE-ERROR must NOT fire on format-unsupported entries; instead, fire the empiricist to re-write the output in JSON format, or implement the format parser.

**Fix 2 — Add format-restriction to the empiricist and grounder:**
The empiricist body should strengthen "structured output" to explicitly prohibit non-JSON/non-LaTeX intermediate results that carry claims: "All claim-bearing numerical outputs must be saved as JSON (`output/stage3a/*.json`) — never as CSV, pickle, parquet, or other formats that the claim-grounding pipeline cannot parse programmatically. Intermediate data files may use any format, but any value that will appear in the paper must have a JSON source."

The grounder body should similarly be constrained: "Cite only sources in JSON or LaTeX-table format (`paper/tables/*.tex`). If the best source for a value is in a non-JSON/non-LaTeX file (CSV, parquet, etc.), emit `NEEDS_EMPIRICIST` with a note requesting the empiricist re-export the value to a JSON output — do not cite the non-parseable file because the verifier cannot resolve field paths in it."

**Fix 3 — "Mislabeled-pointer with correct value" case:**
The verifier should distinguish between "cited value does not match source value" (genuine mismatch) and "field path is a near-match to an existing field where the value is correct." Currently Gate 3 catches near-match paths as GROUNDER-ERROR/field-typo but does not additionally verify that the value at the correct field path matches the paper value. Adding this step — if the near-match field contains a value that matches the paper's `paper_value` within tolerance — would allow the verifier to emit a GROUNDER-ERROR/field-typo with a "note: value at corrected path matches paper text" annotation. The human and orchestrator can then see the typo is pure path label, not a fabrication.

---

## Summary Table

| Theme | Verdict | Root cause | Key files |
|-------|---------|-----------|-----------|
| T11-A: Delegation rule in Claude runtime | REPRODUCED | `templates/runtime/claude/session.md` has no "delegate, don't self-execute" rule; Codex and Gemini both have it at line 31 | `templates/runtime/claude/session.md` (41 lines, rule absent); `templates/runtime/codex/session.md:31`; `templates/runtime/gemini/session.md:31` |
| T11-B: method-checker wiring (#15) | ALREADY-ADDRESSED | method-checker fires at Stage 3a step 7.5 in the three-agent parallel triad; assembled in deployed project; post-pipeline rule also covers it | `extensions/empirical/docs/stage_3a_empirical.md:63-71`; `/tmp/inv_emp/.claude/agents/method-checker.md`; `templates/shared/core.md:321-322` |
| T12-A: Format-blind verifier | REPRODUCED | claim-verifier Gate 3 handles only JSON and LaTeX tables; non-JSON/non-LaTeX sources fail as PAPER-SIDE-ERROR/field-nonexistent, indistinguishable from fabrication | `extensions/empirical/agent_bodies/shared/claim-verifier.md:40-41`; `extensions/empirical/agent_bodies/shared/claim-grounder.md:20-21` |
| T12-B: Output doesn't separate real from format-blind failures | REPRODUCED | No "format-unsupported" tag exists; `totals.paper_side_error_count` conflates both failure types; orchestrator cannot distinguish | `extensions/empirical/agent_bodies/shared/claim-verifier.md:149-210` (JSON schema has no format-unsupported field) |

---

## Explicit Status of Issue #15

**#15 is CLOSED for its stated scope** (empiricist hand-coding standard methods instead of canonical packages). The method-checker agent fires at Stage 3a step 7.5, is assembled in the deployed project, has a hard cap, and requires its output file to exist before the triad aggregates. The canonical-packages skill documents the policy the empiricist must follow before writing any code. The post-pipeline rule explicitly re-fires method-checker on new estimator introductions.

**The residual gap is not #15's scope:** if the orchestrator (not the empiricist) writes code directly — the T11 self-execution failure mode — that code is not in `code/empirical.py` and escapes method-checker entirely. Closing this requires the delegation rule fix described under T11-A, not an extension of method-checker.
