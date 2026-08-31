# INV-1: Empirical Data Discipline — Investigation Report

**Date:** 2026-05-21  
**Themes investigated:** T1 ("not available" default), T2 (first-grabbed source), T4 (independent recomputation), T5 (thin-sourced institutional claims)  
**Template HEAD:** d9415f4 (current)  
**Method:** Static prompt inspection of source bodies, assembled deployed agents at `/tmp/inv_emp`, and stage docs. No live WRDS run.

---

## T1 — "Not Available" / Easy-Path Default in Data Discovery

**Verdict: REPRODUCED**

### What the prompts say

**WRDS skill** (`templates/skill_bodies/empirical/wrds.md`, entire file):
The skill provides connection mechanics, pre-built download templates, table/column references, and performance tips. It contains zero language about what the agent must do before declaring a variable or code "not available." The only availability-adjacent line is the empiricist rule:
> "**No hallucinated data.** Every number must come from data you actually downloaded and computed. If a data source is unavailable, say so." (empiricist.md line 89)

This rule prohibits invented data but does not require a search before declaring unavailability. "Say so" reads as: reach a conclusion and state it — not as: attempt a query first, check aliases, escalate.

**Stage 3a empirical doc** step 4 (stage_3a_empirical.md line 57):
> "Check: does it use the best available data? (If WRDS is available but the plan uses only CZ portfolios, reject the plan.)"

This review rule addresses coarse-vs-fine source selection at the plan-review step but only for the macro distinction (WRDS vs. CZ). It does not address within-WRDS variable-level availability checks. The orchestrator performs this review on the written plan, not during the empiricist's own data search.

**Feasibility step** (stage_3a_empirical.md line 26):
> "If moments are roughly consistent or **unavailable**: proceed to Stage 3."

This is a routing fork — "unavailable" sends the pipeline forward without any substantiation requirement. There is no gate that asks: did the empiricist actually try the query? Did it search for an alias?

**WRDS skill enumeration of CRSP delisting codes:** The skill (wrds.md lines 89–97) lists standard CRSP tables including `msf`, `dsf`, `msenames`, `ccmxpf_linktable`. No mention of CRSP delisting-event tables (`mse`, `dsedelist`, `dse`), the delisting return field (`dlret`), or the historical share-code changes that create "legacy code" situations. No alias or migration guidance anywhere in the skill.

**Empiricist body** (finance/empiricist.md): Contains no rule requiring the empiricist to attempt a query before concluding unavailability. The auxiliary-dataset lookup rule (line 90) says to use OpenAlex for targeted lookups but specifically flags it as "noisy for generic topical searches." No rule says: if a variable is declared not-in-WRDS, verify with `db.list_tables()` or `db.describe_table()`.

### Gap

There is no instruction anywhere in the empiricist body, WRDS skill, or stage doc that says: **"Not available" is a substantiated verdict requiring an actual query attempt, a search for aliases/legacy codes, and documented evidence of the failure.** A documentation-only check ("no documented change found") is not prohibited by the current prompts and would pass all existing gates.

### Fix direction

**File:** `templates/skill_bodies/empirical/wrds.md` — add a section "Before declaring a variable or table unavailable":
1. Run `db.list_tables(library='crsp')` (or the relevant library) and search the result programmatically.
2. Try the canonical alternative names (e.g., `dse`, `dsedelist`, `mse` for CRSP delistings; legacy field names visible in `db.describe_table()`).
3. Search `db.describe_table()` for field descriptions matching the concept.
4. WebSearch for "[WRDS library] [variable concept] table name" to catch post-migration naming.
5. Only after steps 1–4 fail is "not available" a substantiated verdict. Document the negative search in the analysis report.

**File:** `extensions/empirical/agent_bodies/finance/empiricist.md` — add a rule (parallel to the canonical-packages rule in structure):
> **"Not available" requires substantiation.** If a variable, code, or table is declared unavailable, the script must include documented evidence: the `list_tables()` output searched, the `describe_table()` results checked, and the alternative names attempted. A claim of unavailability without a query attempt is not a finding — it is a gap in the search. Write the negative-search log to `output/stage3a/data_search_log.md`.

**File:** `extensions/empirical/docs/stage_3a_empirical.md` step 4 (plan review) — extend the "best available data" check to: "For any variable the empiricist declares unavailable, confirm the analysis report contains a documented negative-search log. If not, reject the plan and require the search."

---

## T2 — Treats First-Grabbed Source/Window as Best Available

**Verdict: REPRODUCED** (with one partial mitigation)

### What the prompts say

**Partial mitigation — plan review (stage_3a_empirical.md line 57):**
> "Check: does it use the best available data? (If WRDS is available but the plan uses only CZ portfolios, reject the plan.)"

This rule exists and is the strongest guard against coarse-vs-fine substitution. However it operates at a high level (WRDS-vs-CZ granularity), it fires only on the written plan (the empiricist has already made all source choices before this review), and it gives no guidance on within-source granularity (e.g., WRDS `funda:dltt` vs. a hand-collected field vs. a COMPUSTAT note field).

**Analysis plan instruction (stage_3a_empirical.md line 49):**
> "what data sources to use (and WHY those sources — reference the data inventory)"

The empiricist is asked to justify source choices but only by reference to the inventory, not by comparison against finer alternatives. "Why CZ" is a valid answer if the inventory lists CZ; the instruction does not require "why CZ over the WRDS field-level equivalent."

**Empiricist body:** No rule requiring a "best-available-source enumeration" before locking a source. No rule requiring window/period choices to be anchored to a specific institutional rationale. The "use standard sample periods" rule (empiricist.md line 87) provides defaults but says "state and justify any deviations" — the converse (justifying the *chosen* period as best, not just default) is not required.

**Cutoff/threshold sourcing:** No rule in the empiricist body, identification-designer body, or stage doc requires that a proposed cutoff (e.g., $1B asset threshold) be anchored to a specific regulatory rule text, precedent paper with an explicit justification, or industry convention. The identification-designer's toolkit section mentions "institutional rule with a discrete eligibility cutoff" as a description of when RD fits, but does not require the cutoff value to cite its source.

**Data-selection auditor (data-selection-auditor.md line 30):** The filter-text-vs-code-mismatch check verifies the code matches the plan, and coverage-vs-external-benchmark verifies approximate universe sizes — but neither checks whether the documented filter is the best available filter (only that it matches what was written and is roughly plausible).

**Identification-designer:** The "Available data variation" section of the output template (identification-designer.md line 117) says:
> "If a strategy hinges on auxiliary data beyond the wired skills (CRSP/Compustat/FRED/WRDS), use `openalex.py search "<query>" --type dataset` to check whether a named replication package or public deposit exists before recommending it."

This is the closest thing to a "look before you lock" rule, but it applies only to auxiliary datasets beyond the wired skills, not to within-wired-skill source/field selection.

### Gap

There is no instruction requiring the empiricist to (a) enumerate alternatives before locking a source/window/cutoff, (b) document why the chosen source dominates the finer alternatives, or (c) anchor cutoffs to rule text or precedent rather than to intuition. The plan-review step's "best available data" check is the only gate, and it is coarse-grained, post-hoc (plan already written), and does not cover within-source field granularity or cutoff justification.

### Fix direction

**File:** `extensions/empirical/docs/stage_3a_empirical.md`, step 2 (analysis plan) — extend the plan requirements:
> Before locking any data source, field, or sample window, the plan must include a **source-selection justification**: (a) what finer or longer-coverage alternatives were considered (name them explicitly); (b) why the chosen source is preferred (sample coverage, variable precision, established convention in the literature — cite a precedent if applicable); (c) for any cutoff or threshold, the rule text, regulatory document, or prior paper from which it is sourced. Intuition-based cutoffs are not acceptable. The plan is rejected in step 4 if any variable-level source or sample cutoff lacks this justification.

**File:** `extensions/empirical/agent_bodies/finance/empiricist.md` — add a rule:
> **Best-available-source obligation.** Before writing analysis code for any variable, check: is there a finer, longer-sample, or more directly-measured source in the wired skills? For regulatory/classification variables, check whether a field-level source (e.g., a FFIEC form-level field) exists before using a derived aggregate. For cutoffs, cite the rule text or prior literature precedent in both the code comment and `empirical_plan.md`.

---

## T4 — Deterministic Coding Bugs Caught Only by Independent Rederivation

**Verdict: REPRODUCED**

### What the prompts say

**Empirics-auditor "recompute" language (empirics-auditor.md lines 23, 115):**
- Step 4 of the audit procedure: "**Check every result** — recompute key numbers independently **where possible**" (emphasis added)
- Rules section: "**Write code to `code/tmp/` for your verification.** If you recompute a statistic independently, save the script."

The phrase "where possible" is the critical defect. It transforms mandatory independent recomputation into a discretionary best-effort. A grouping or merge error in `code/empirical.py` can produce a wrong result that re-runs correctly from the same code (the bug is deterministic), passes bit-identical reproduction from the cache (the data-integrity auditor re-queries source vs. cache, not a recomputed path vs. cache), and reads coherently in the analysis report. The "where possible" qualifier gives the auditor room to read the code and declare the numbers consistent without actually computing them by a different path.

**Scope of existing auditors:** The three-auditor triad (step 7.5) covers:
- `data-integrity-auditor`: cache values vs. source (re-queries source, samples N=20–50 records, compares field by field)
- `data-selection-auditor`: who is in the cache vs. who should be (relaxed-filter diff)
- `method-checker`: canonical-package compliance

None of these auditors is tasked with independently computing a headline estimate via a different merge key or grouping. The data-integrity auditor's re-query is at the level of individual field values, not at the level of the headline aggregate computed from those fields. A correct cache can produce a wrong aggregate via a grouping or merge-duplication bug.

**Statistical checks table (empirics-auditor.md lines 44–49):**
The auditor is asked to verify "Point estimates: Do the signs match the theory's predictions? Are magnitudes plausible?" — but this is a plausibility check, not an independent computation. The output template row for statistical checks (empirics-auditor.md line 82):
> `| [key result 1] | [value] | [your value] | YES/NO | [details] |`

The "your value" column implies independent computation, but the instructions that reach the agent say "where possible," making this column potentially empty (or populated from the cache) rather than mandatorily independently computed.

**Math-auditor analogy:** The math-auditor (`templates/agent_bodies/shared/math-auditor.md`) is explicitly tasked with step-by-step re-derivation — "check derivations step-by-step." There is no empirical analogue: no agent is mandated to re-run the core aggregate from source by a different merge path.

### Gap

No agent is **mandated** to independently recompute a headline estimate from source using a different merge key, aggregation order, or grouping logic. The empirics-auditor's "where possible" qualifier and the data auditors' field-level (not aggregate-level) scope create a gap precisely at the failure mode reported: grouping/merge errors that produce wrong aggregates from correct field values.

### Fix direction

**File:** `extensions/empirical/agent_bodies/shared/empirics-auditor.md` — replace the "where possible" language and make independent recomputation mandatory for at least one headline estimate:

Replace:
> "4. **Check every result** — recompute key numbers independently where possible"

With:
> "4. **Independently recompute the headline estimate(s).** For the main coefficient(s), portfolio spread(s), or calibration moment(s), write a short verification script in `code/tmp/empirics_verify.py` that reaches the same result via a **different path**: alternative merge key, different aggregation order, or recomputed from the raw source file rather than the processed cache. A bug that is deterministic (wrong but reproducible) will survive a code-read and a cache-field-check but will fail an independent path. If your verification value differs from the reported value, that is a finding. If they agree, record both values in the output table."

Also strengthen the rules section: change "**If** you recompute a statistic independently" to "**When** you recompute the headline estimate independently (mandatory)" and add: "A verification script that does not exist is an automatic FAIL finding — the auditor cannot waive independent recomputation for the headline result."

**Note:** This does not require the auditor to recompute every result, only the headline. The scope is deliberately narrow to be actionable.

---

## T5 — Thin-Sourced Institutional/Factual Claims

**Verdict: PARTIALLY-ADDRESSED** (existing check is single-source; uncited-claim detection is absent)

### What the prompts say

**polish-institutions.md — what IS addressed:**
The agent explicitly checks:
- Regulatory mechanism accuracy (e.g., "SEC Form PF is confidential" example at lines 11–12)
- Fee/compensation convention accuracy (lines 13–14)
- Market sizes and aggregates against a citable industry source (lines 14–15)
- Contract terms against real-world practice (lines 15–16)
- Faithful characterization of cited papers via OpenAlex abstract (lines 16–17)
- Stylized facts against a citable empirical source (lines 17–18)

The agent is explicitly required to produce a primary source for each finding:
> "For every finding, include a primary source (regulatory document, official market-size release, the cited paper's abstract). A finding without a citable source is not actionable." (line 79)

**What is NOT addressed — multi-source verification:**
The agent's current instruction requires one primary source per finding *in the report*. It does not require the original claim to be cross-checked against multiple independent sources. The instruction is:
- "Verify every regulatory citation" — verify against *what*? A single regulatory document.
- "Check every claim about fee timing... against industry standard practice" — one check.
- No rule says: "a regulatory date/rule must be confirmed by ≥2 independent primary sources."

The T5 symptom is specifically that a fact was wrong despite the agent having checked a source — the single source was wrong or misread, and a second source would have caught it. The current prompt design does not guard against this because single-source verification is the standard, not a fallback.

**What is NOT addressed — uncited factual claims:**
The agent's seven check categories (regulatory, fee, market size, contract, citation characterization, stylized facts, data sources) all target *cited* claims — the agent reads the paper and checks whether what it says is accurate. There is no instruction that says: **scan the paper for factual assertions that have no citation at all and flag them.** A regulatory date stated confidently without a footnote would pass the current agent's checklist unless the agent happens to spot the missing citation while verifying a different claim in the same paragraph.

**paper-writer.md:** Contains no rule prohibiting uncited factual claims. The rule "No hallucinated citations. Only cite papers from the literature map or that you can find in `references/references.md`" prohibits fabricated citations but says nothing about whether a factual claim requires any citation at all.

**polish-consistency.md:** Not read for this investigation but is a candidate location for an uncited-claim scan.

### Gap

Two distinct gaps:
1. **Multi-source gap:** No instruction requires regulatory dates/rules to be cross-checked against ≥2 independent primary sources. Single-source verification can pass a wrong fact.
2. **Uncited-claim detection gap:** No agent is tasked with scanning the draft for confident factual assertions that carry no citation.

### Fix direction

**Gap 1 — Multi-source requirement:**
**File:** `templates/agent_bodies/shared/polish-institutions.md` — add to the "What you check" opening:
> For any regulatory date, rule, or mechanism your search finds in one source: find a second independent primary source (a different regulatory document, an industry association survey, or a prior academic paper that cites the same rule) before recording the fact as verified. A single-source confirmation is not verification for regulatory claims — document both sources in the finding's "Source" field as: "Source 1: [...] Source 2: [...]." If a second independent source cannot be found, flag the claim as **single-source** in the severity rubric and treat it as major, not minor.

**Gap 2 — Uncited-claim detection:**
**File:** `templates/agent_bodies/shared/polish-institutions.md` — add as item 8 (new check category):
> **8. Uncited factual assertions.** Scan the prose for confident factual claims (regulatory dates, enforcement rates, market sizes, contract terms, stylized facts stated as established) that carry no inline citation or footnote. Every such claim is a finding. Severity minor if the fact is uncontroversial and easily verified; severity major if the fact is specific (a date, a rate, a threshold) and not supported by an obvious reference.

Alternatively, this scan could be added to `polish-consistency.md` (which already focuses on internal consistency checks) with a cross-reference from the institutions agent.

---

## Summary of Verdicts

| Theme | Verdict | Core gap | Primary file(s) to fix |
|-------|---------|----------|------------------------|
| T1 — "Not available" default | **REPRODUCED** | No query-attempt requirement before declaring unavailability; no alias/legacy-code search protocol | `wrds.md` (add substantiation protocol), `empiricist.md` (add rule), `stage_3a_empirical.md` step 4 |
| T2 — First-grabbed source as best | **REPRODUCED** | No best-available-source enumeration in plan; no cutoff-citation rule; plan-review check is coarse-grained and post-hoc | `stage_3a_empirical.md` step 2, `empiricist.md` |
| T4 — Coding bugs caught only by rederivation | **REPRODUCED** | "where possible" qualifier makes headline independent recomputation discretionary; no agent mandated to compute headline via a different merge/grouping path | `empirics-auditor.md` (strengthen recomputation mandate) |
| T5 — Thin-sourced institutional claims | **PARTIALLY-ADDRESSED** | Single-source verification standard (≥2 required); no uncited-claim scan exists | `polish-institutions.md` (multi-source rule + uncited scan) |

### Key finding

The four failures share a structural pattern: each guard that exists operates at the wrong granularity or with the wrong obligation level.
- T1/T2: The "best available data" plan-review check exists (step 4) but fires after source choices are already made, at the WRDS-vs-CZ level, with no within-source or alias-search requirement.
- T4: The independent recomputation instruction exists ("recompute key numbers") but the "where possible" qualifier removes the mandate precisely in the cases where it matters (a determined auditor can always explain why a different merge path was "not possible").
- T5: The institutions-check infrastructure exists and is well-specified for catching wrong facts — but it verifies cited claims against one source per claim, and has no scan for uncited claims at all.

None of these gaps requires a new agent; each requires a targeted instruction addition (≤5 sentences each) to an existing agent body or stage doc.
