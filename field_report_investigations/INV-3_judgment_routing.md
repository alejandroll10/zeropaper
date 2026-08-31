# INV-3 — Judgment/Effort/Routing Investigation
**Themes:** T6 (failed optional probe → framing walkdown), T7 (start/stop judgment, effort allocation)
**Root cause:** R-A (defaults don't track payoff — "easy" and "safe" win over "where the answer is")
**Date:** 2026-05-21
**Template HEAD at investigation:** d9415f4
**Investigator note:** Static-code forensics only. No live run executed.

---

## Summary verdict

| Theme | Verdict |
|-------|---------|
| T6 — optional probe → framing walkdown | **REPRODUCED** — no distinction between load-bearing and optional specs exists anywhere in the template |
| T7 — start/stop judgment / effort allocation | **REPRODUCED** — branch-manager's Section B has one ceiling concept with no structural/reachable axis; no language forbids tier-inert robustness |

Both symptoms are traceable to missing decision rules that the pipeline currently lacks entirely (not weakly stated — absent). The fix requires adding new language in two agents and one orchestrator doc.

---

## T6 — Failed Optional Probe → Walks the Core Framing Down

### VERDICT: REPRODUCED

### Evidence

**Q: Is there any language distinguishing a load-bearing spec (must hold) from an optional strengthening probe (nice-to-have), and routing a null on the latter to "drop probe, keep baseline"?**

The answer is: **no such distinction exists anywhere in the template.**

The relevant files were searched exhaustively:

**`templates/agent_bodies/shared/puzzle-triager.md`** — the entire agent addresses a different question: did empirical results *contradict a theory prediction*? The decision tree (lines 39–62) fires on sign reversals and order-of-magnitude discrepancies against theory. It has no axis for "was this spec load-bearing or exploratory?" The triager cannot distinguish "the baseline spec must hold" from "this strengthening robustness check is optional" — both route identically through the decision tree. On a null strengthening spec, the triager sees a contradiction and (given strong priors + standard measurement + audited theory + sign reversal + pivot_round < 2) routes to **PIVOT** — the worst possible outcome for an optional probe that merely failed to strengthen the result.

**`templates/agent_bodies/shared/branch-manager.md`** — no mention of optional or strengthening probes. Section B (Ceiling Assessment, lines 73–76) asks "has the approach ceilinged?" and "evidence against ceiling" (specific dimensions where the draft could gain 5+ points). It has no probe-classification axis. The branch-manager will read a failed optional spec as evidence of a ceiling in whatever dimension the spec was targeting, without knowing it was optional.

**`templates/shared/core.md`** — the pipeline principles section (lines 12–77) contains "surprises are discoveries" (line 27) and "do what makes the paper better" (line 67). These principles push the pipeline toward treating any anomalous result as potentially valuable — which is correct for load-bearing specs but actively harmful for optional strengthening probes. No fallback discipline exists to say "drop the probe when null, retain the baseline."

**`templates/shared/docs/stage_3_implications.md`** — implications are tagged SUPPORTED / NOVEL / PUZZLE-CANDIDATE / DEAD (lines 43–48). There is no "OPTIONAL-PROBE" or "STRENGTHENING-ONLY" tag. A strengthening spec that comes back null gets no special treatment; it enters the same pipeline as a theory-contradicting empirical result.

**`extensions/empirical/docs/stage_3a_empirical.md`** — the contradiction check (lines 73–85) is binary: NONE or CONTRADICTIONS FOUND. No concept of "this contradiction arose from an optional spec and the baseline is still intact." A null optional probe that contradicts the strengthening prediction flows to puzzle triage without the orchestrator ever knowing the spec was optional.

**`extensions/empirical/agent_bodies/finance/empiricist.md`** — the empiricist plans and executes analysis but has no instruction to tag specs as "load-bearing" vs. "strengthening probe" (lines 17–95). The output template (lines 57–78) has an "Assessment" section but no probe-status field. The empiricist cannot signal to downstream agents that a particular result is optional.

### Mechanism by which T6 manifests

1. The empiricist runs a conservative / strengthening spec (e.g., a subsample or alternative identification cut that would reinforce the baseline if positive).
2. The spec returns null or negative.
3. The contradiction check at `stage_3a_empirical.md` lines 73–85 records CONTRADICTIONS FOUND.
4. Puzzle-triager fires with the null as the contradicting evidence.
5. The triager — having no probe-type axis — evaluates the null on its merits: prior strength, measurement quality, theory formality, contradiction magnitude. If the null is a sign reversal on a well-measured moment with a well-audited theory, the triager routes PIVOT.
6. The pipeline rebuilds the theory around explaining the sign reversal in the optional spec, weakening or abandoning the baseline claim.

The "catastrophize" behavior in the field report (item A, #3a) is exactly this path: the pipeline treats a null strengthening check as a structural threat to the theory rather than dropping the optional check and retaining the intact baseline.

### Victor-1 postmortem corroboration

The postmortem documents a related failure at puzzle-triage (p1, RECONCILE verdict) where scope broadening happened without verifying the broadened claim's identifiability — the RECONCILE path in puzzle-triager has a similar missing check. The postmortem's direction for fixing it (`victor1_postmortem.md` line 137) involves adding a surviving-causal-claim verification requirement. The optional-probe problem is the same structural gap: the triager applies its full decision tree regardless of the epistemic status of the failing spec.

### Fix direction

**File:** `extensions/empirical/agent_bodies/finance/empiricist.md` (and shared/macro equivalents) — add a spec-classification rule to the analysis plan schema.

Add to the "Analysis plan" section: each specification in the plan must be labeled with one of two roles:
- `LOAD-BEARING`: the paper's core claim depends on this result holding. A null triggers puzzle triage as today.
- `STRENGTHENING-PROBE`: this spec would add robustness or confidence if positive, but its null does not contradict the theory's load-bearing predictions. A null on this spec routes to "drop probe, retain baseline" without triggering the contradiction check.

**File:** `extensions/empirical/docs/stage_3a_empirical.md` — modify the contradiction check (lines 73–85) to exclude STRENGTHENING-PROBE nulls from the CONTRADICTIONS FOUND routing. A null result on a STRENGTHENING-PROBE is written to `empirical_analysis.md` as "probe returned null — dropped from primary analysis, baseline intact" and does not trigger puzzle triage.

**File:** `templates/shared/docs/stage_puzzle_triage.md` — add to the "Entry check" (lines 15–27) a preflight: before launching the triager, verify that the contradicted implication is load-bearing (the theory commits to it holding). If the contradiction arises from a strengthening probe tagged in the plan, skip the triager and record "optional probe null — baseline retained."

**File:** `templates/agent_bodies/shared/branch-manager.md` — Section B should note whether the spec that revealed the ceiling was load-bearing or optional. An optional-probe null is not ceiling evidence; the section's "Evidence for ceiling" criterion should name only failures on LOAD-BEARING specs.

---

## T7 — Start/Stop Judgment and Effort Allocation

### VERDICT: REPRODUCED

### Evidence

**Q1: Does branch-manager distinguish a STRUCTURAL ceiling (→ stop, ship) from a REACHABLE ceiling (→ keep digging via deeper search, not more checks)?**

**No.** Branch-manager's Section B (Ceiling Assessment) reads:

> "Has the current approach ceilinged? Yes / No / Unclear"
> "Evidence for ceiling: Specific weaknesses that CANNOT be fixed within the current framework — theoretical dead ends, framing traps, structural problems."
> "Evidence against ceiling: Specific dimensions where the current draft could plausibly gain 5+ points with targeted work."

(`branch-manager.md`, lines 73–76)

The language describes one axis: has the approach ceilinged or not? It does not decompose the ceiling into:
- **Structural** — binding constraint is intrinsic to the setting (sample size, identification scarcity, scope limitation). No amount of additional work moves the result.
- **Reachable** — binding constraint is effort or search (better data exists, cleaner identification is available, the settling test has not been run). One more targeted pass unlocks progress.

Without this distinction, a branch-manager facing a structurally-ceilinged paper (e.g., sample too small for the test that settles the question) has no vocabulary to recommend "stop and ship" with confidence — both structural and reachable ceilings look like "evidence of ceiling: binding constraint." Similarly, a paper facing a reachable ceiling (better data available, not yet tried) has no vocabulary to produce a "keep digging" mandate that specifically targets the reachable constraint rather than defaulting to more robustness checks.

The field report symptom (quits early on high-payoff searches, defaults to "not available") is the reachable-ceiling case. The branch-manager says "ceiling" and the orchestrator stops — but the ceiling was reachable if one more data query had been tried.

The padding symptom (pads with robustness when ceiling is structural) is the structural-ceiling case. The branch-manager says "ceiling — structural" but the orchestrator, having no "ship now" mandate, continues to generate extensions per the deepening playbook in `core.md` (lines 337–352), which lists extension types (continuous time, heterogeneity, learning, etc.) without gating them on whether the ceiling is structural or reachable.

**`branch-manager.md` Section C** is closer, asking "Is the paper getting longer without getting better?" (line 85) and "What would a referee's first-order concern be?" — these are softer signals that a human reader can interpret as ceiling evidence, but they do not resolve to a binary "STRUCTURAL ceiling — stop" vs. "REACHABLE ceiling — keep digging" call.

**Q2: Does anything forbid robustness that cannot move the tier?**

**No.** The deepening playbook in `core.md` (lines 337–352) lists extension types and instructs the orchestrator to "pick 1-2 extensions that test whether the channel survives under realistic features." There is no gate asking "would this extension, if positive, change the branch-manager's §E verdict from Continue to anything else?" There is no prohibition on "extensions that add length but cannot move the result/assessment/tier."

The branch-manager's rules (lines 115–127) include:

> "Distinguish 'better paper' from 'more paper.'" (line 121)
> "Is the paper getting longer without getting better?" (line 85)

These are Section C diagnostic questions, not binding constraints. The branch-manager can flag that robustness is padding and still recommend Continue (the recommendation is in Section E). Even if §E recommends Restructure or Restart, the orchestrator can grant one more iteration on a delta ≥ 3 score increase from cosmetic changes — the escalation table in `core.md` (lines 354–384) allows this if branch-manager's §A is SUBSTANTIVE.

Critically: **there is no line in any agent body or orchestrator doc that says "if the ceiling is structural, robustness that cannot move the tier is forbidden as next work."** The closest is the §A COSMETIC escalation rule: if the branch-manager classifies the revision as COSMETIC, the orchestrator escalates instead of continuing. But COSMETIC means "reframing or organizational changes" (stage_4.md lines 92–93), not "substantive robustness that cannot move the tier." A new robustness check that is genuinely substantive (a new regression, new control, new sample split) classifies as SUBSTANTIVE and earns another iteration even if that iteration cannot change the tier outcome because the ceiling is structural.

**Q3: Does branch-manager distinguish "keep digging via deeper search" from "keep digging via more checks"?**

**No.** Section D (Alternative Courses of Action, lines 89–112) requires "at least one alternative must be a restart from Stage 1 using a specific unused sketch" and "at least one alternative must be a structural reframe." The alternatives template does not include a "go back and search harder / try a different data source / revisit the identification approach" option as a distinct branch. The Regenerate option (line 106) is available but only under specific conditions (score in REVISE band, regeneration_round == 0, not seeded). A "deeper search on the same idea" — the field report's "identification/methodology reach a genuinely better version only on the 2nd/3rd ask" — is not a named action type in branch-manager's alternatives vocabulary.

### Victor-1 postmortem corroboration

The postmortem (`victor1_postmortem.md`) confirms the padding pattern at sections 3 and 5:

> "The empiricist's prompt does not distinguish between those two classes of output [deepening causal claim vs. critique of paper's own design]." (line 63)

> "The substantive-deepen mandate pushed the empiricist toward contribution-shape drift rather than causal identification improvement." (line 91)

This is the structural-ceiling case playing out: the identify-better-identification ceiling is structural (the paper lacks a clean instrument), but the pipeline kept generating substantive work (per-cohort placebos, robustness batteries) that could never move the tier because it never addressed the identification question.

The branch-manager at v4 "correctly diagnosed the paper was at its top-3-fin ceiling" (`victor1_postmortem.md` line 91) but the recommendation was ADVANCE — which shows the branch-manager correctly identified the ceiling but had no language to say "structural ceiling: stop here, ship" or "the gap-to-reachable-tier requires data you don't have, not more analysis."

### Fix direction

**File:** `templates/agent_bodies/shared/branch-manager.md` — restructure Section B (Ceiling Assessment) to require a two-axis call:

**Axis 1 — ceiling type:**
- `STRUCTURAL`: the binding constraint is intrinsic to the setting. Examples: sample too small for the test that settles the claim; instrument does not exist in the available data; scope is inherently limited to a narrow phenomenon. Additional work along the current path cannot move the result or the tier.
- `REACHABLE`: the binding constraint is effort or search. Examples: a finer data source exists and was not tried; the identification design has not used the strongest available variation; a specific sub-population test has not been run. One more targeted pass could unlock progress.
- `UNCERTAIN`: not enough information to classify.

**Axis 2 — tier-movement test:**
For each proposed next action (including extensions in the deepening playbook), the branch-manager must ask: "If this action returns a positive result, would the revised paper clear the next decision threshold (advance vs. REVISE band) — or would it remain in the same band?" Actions that cannot move the threshold regardless of their result are tier-inert. Branch-manager §E must forbid tier-inert next steps when Axis 1 = STRUCTURAL.

**Binding rule (new hard rule in §E, branch-manager):**
- If Axis 1 = STRUCTURAL and proposed next work is tier-inert: recommend "Ship at current tier — further work cannot move the ceiling. Deepening playbook does not apply." Log the structural constraint explicitly.
- If Axis 1 = REACHABLE: §E must name the specific reachable action (concrete data query, specific identification design, specific sub-sample test) — not a generic "run more robustness checks." The "deeper search" path is a named action class parallel to Restart and Restructure.

**File:** `templates/shared/core.md` — add to the escalation table:

> If branch-manager §E recommends "Ship at current tier — STRUCTURAL ceiling": proceed to Stage 5 regardless of the current score band. Do not invoke the deepening playbook. Do not grant another robustness iteration. Record the ceiling classification in `process_log/pipeline_state.json` as `"ceiling_type": "structural"`.

**File:** `templates/shared/docs/stage_4.md` — add to the Gate 4 orchestrator rules (after step 9):

> Before routing to the deepening playbook, verify that branch-manager §B classifies the ceiling as REACHABLE. If §B = STRUCTURAL, skip the deepening playbook entirely and route to Stage 5 with the current draft. A structural ceiling means more analysis cannot move the tier; the deepening playbook exists for reachable ceilings only.

---

## Cross-theme finding: puzzle-triager lacks probe-type input

The T6 and T7 symptoms share a common upstream failure: no agent in the pipeline classifies empirical specs by their epistemic role (load-bearing vs. strengthening probe, tier-moving vs. tier-inert) at the time the spec is proposed. This classification needs to happen at the empiricist's plan stage — not post-hoc at puzzle triage, where the information about the spec's role has been lost and the triager only sees "null result on a prediction."

The fix for both themes converges on the same intervention point: the empiricist's analysis plan (step 2 of `stage_3a_empirical.md`) should require each specification to carry a role tag (`LOAD-BEARING` vs. `STRENGTHENING-PROBE`) and a tier-movement tag (`TIER-MOVING` vs. `TIER-INERT`). Downstream agents (contradiction check, branch-manager, puzzle-triager) route on these tags rather than treating every result as equally consequential.

---

## Files examined

| File | Lines examined | Relevant negative finding |
|------|---------------|--------------------------|
| `templates/agent_bodies/shared/branch-manager.md` | All (173 lines) | Section B has one ceiling concept (no structural/reachable axis); no mention of optional probes |
| `templates/agent_bodies/shared/puzzle-triager.md` | All (112 lines) | Decision tree has no probe-type axis; null optional spec routes identically to load-bearing contradiction |
| `templates/shared/core.md` | Lines 1–384 (full pipeline doc) | Deepening playbook has no tier-movement gate; no "STRUCTURAL ceiling → ship" rule |
| `templates/shared/docs/stage_4.md` | All (102 lines) | No gate asking whether proposed next work moves the tier |
| `templates/shared/docs/stage_6.md` | Full | No probe-classification in deepen routing; deepen mandate blanket-fires on Reject |
| `templates/shared/docs/stage_3_implications.md` | All | Tags are SUPPORTED/NOVEL/PUZZLE-CANDIDATE/DEAD — no OPTIONAL-PROBE or STRENGTHENING-ONLY |
| `extensions/empirical/docs/stage_3a_empirical.md` | All | Contradiction check is binary (NONE/CONTRADICTIONS FOUND); no probe-role awareness |
| `extensions/empirical/agent_bodies/finance/empiricist.md` | All (95 lines) | No spec-role classification in plan schema or rules |
| `templates/agent_bodies/shared/scorer-core.md` | All (200 lines) | No probe-type or tier-inert awareness |
| `victor1_postmortem.md` | All | Corroborates structural-ceiling padding (§3, §5) and triager routing without probe classification (§2 H2) |
