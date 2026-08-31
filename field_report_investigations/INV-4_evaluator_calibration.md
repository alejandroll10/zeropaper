# INV-4 — Evaluator Calibration & Stability (T8, T9, T10)

**Template HEAD:** d9415f4 (verified against current HEAD)
**Deployed project inspected:** `/tmp/inv_finance`
**Themes:** T8 (scrutiny at wrong level), T9 (verdict instability), T10 (sycophancy on proposal / over-penalization on evaluation)
**Root cause targeted:** R-B — the judgment/interpretation layer is the unreliable component

---

## T8 — Scrutiny Aimed at the Wrong Level

**Verdict: REPRODUCED (prompt-side gap)**

### Evidence

**self-attacker-core.md / assembled self-attacker.md**

The attack structure is a flat enumerated list of six categories: Assumption attacks, Result attacks, Mechanism attacks, Importance attacks, Completeness attacks, Literature attacks. There is no instruction to identify the *single most load-bearing assumption* before generating any other attack. The six categories are presented in reading order, not in a ranked-by-importance-to-the-core-result order.

The agent is instructed to "produce a ranked list of attacks" (line 14), but ranking is by severity tier (10 → 7-9 → 4-6 → 1-3), not by conceptual distance from the load-bearing premise. A robustness-level concern can score severity 6 and a wrong-data-choice can score severity 7, and both appear in adjacent tiers with no structural priority given to the latter.

The output format has a `## The strongest single attack` section (self-attacker-core.md line 83), which is the closest thing to a load-bearing-premise check — but it appears *at the end*, after the full enumeration. The prompt does not require this section to identify the *methodological / data* layer failure (wrong choice of data, wrong methodology, wrong framing of the question) as distinct from robustness-level content. The "strongest single attack" could be a robustness attack or an importance attack — the prompt does not instruct that data/methodology failures rank above robustness failures when they exist.

The `SELF_ATTACK_COMPLETENESS_BULLETS` category (assembled as "What obvious extensions or cases are missing? / Are there parameters ranges where the model breaks down? / What happens in the limit?") is exactly the robustness-level scrutiny the field report identifies as over-indexed. The prompt gives this category no lower structural priority than Assumption attacks.

**scorer-core.md / assembled scorer.md**

The scorer's Parsimony rubric uses "load-bearing" correctly for parsimony purposes (lines 86-99) but does not instruct the scorer to identify the single load-bearing assumption as the primary target of its evaluation. The scorer reads the self-attack report as one input but has no instruction to verify that the self-attacker attacked the load-bearing premise first.

The output format requires "one sentence" justifications for each dimension score (scorer.md lines 143-149), but none of these require quoting or referencing the specific methodological / data assumption that drives the conclusion. A scorer could generate well-formed one-sentence justifications entirely at the robustness level and satisfy the format requirement.

**Not already addressed.** The `## The strongest single attack` section is a useful partial mitigation but does not resolve the gap: it comes after the full enumeration (not before) and does not constrain the agent to classify "load-bearing premise" attacks as categorically higher priority than "completeness / robustness" attacks. No instruction in any relevant body says: before generating any robustness attacks, name the one assumption the main result most depends on, and attack that first.

### Fix direction

Add a mandatory Step 0 to the self-attacker:

> **Before enumerating any attack category, identify the single assumption the paper's headline result most depends on.** State it explicitly as: "Load-bearing premise: [assumption / data choice / methodological commitment]." Then attack that premise first, from every angle, in the Assumption attacks section. Robustness/completeness attacks come after. A robustness attack that leaves the load-bearing premise unaddressed cannot be severity 7+.

Optionally add a corresponding check to the scorer: "Does the self-attack report identify the load-bearing premise explicitly? If not, the self-attack report is incomplete — flag this in feedback."

---

## T9 — Verdict Instability Run-to-Run

**Verdict: PARTIALLY-ADDRESSED (structural / model nondeterminism; prompt-side contributors identifiable)**

### Evidence

**True run-to-run nondeterminism cannot be reproduced statically.** This is an intrinsic model characteristic. The investigation assesses only the prompt-side contributors to interpretation variance.

**scorer-core.md / assembled scorer.md — verdict anchoring**

The output format requires one-sentence justifications for each dimension score (scorer.md lines 143-149). The template text uses bracket placeholders like `[one sentence]` — no requirement that the sentence contain a specific quoted number, equation reference, section reference, or other anchoring citation. A scorer can write "The mechanism is well-identified and the equilibrium conditions are tightly stated" as the Rigor justification without quoting the specific theorem that moves it from 60 to 80. This allows interpretation variance to enter: two runs that read the same artifact can write different one-sentence justifications that each satisfy the format but reflect different implicit weights on different observations.

The H-requirements table has an `Evidence` column (scorer.md line 133) and the Importance dimension has a mandatory "in one sentence, what decision or belief this result would change" requirement (scorer.md line 57). These are the strongest anchoring instructions in the scorer. They create some pressure toward convergence for binary H checks and Importance, but the five remaining dimensions (Novelty, Surprise, Rigor, Parsimony, Fertility) have no equivalent anchor requirement — the "one sentence" can be evidence-free observation.

**self-attacker-core.md — severity assignment**

Severity (1-10) is assigned per attack group. There is no requirement that the severity assignment cite the specific text in the artifact that supports it. "Assumption D is fragile" at severity 8 can be written identically across runs without anchoring to the line/equation in the draft that confirms it is load-bearing. This allows the severity tier — which directly gates the triager's and scorer's downstream decisions — to vary based on implicit model judgment rather than explicit text-to-verdict chains.

**scorer-core.md — "Do not fetch prior scorer output"**

The prohibition on reading prior scorer outputs (scorer.md line 184, "Do not read, grep, or glob for prior scorer decision files — you score this version independently") is correctly motivated (avoiding contamination), but its side effect is that a new run cannot observe or stabilize against the prior run's anchoring. This is structurally sound but means each run is independently subject to interpretation variance rather than to a stable anchor.

**What is already addressed:**

- The `"Don't be sycophantic"` rule in scorer-core.md (line 193) and the absolute-scale calibration ("Most theories should score below 50. A 75+ is uncommon...") are anti-inflation anchors that partially constrain the interpretation variance from above.
- The Importance dimension's mandatory decision/belief identification is the most effective anchoring mechanism in the current prompt.
- The Surprise dimension's implication-tag rules (cap-30, floor-70) tie the Surprise score to a deterministic file-based artifact rather than holistic impression, which is a strong variance-reduction mechanism for that dimension.
- The H-requirements table with `Evidence` column provides some constraint for H1-H5.

**What is not addressed:**

- Novelty, Rigor, Parsimony, and Fertility justifications are free-text "one sentence" with no anchor requirement. These are the dimensions with the highest interpretation variance.
- Severity assignments in the self-attacker have no anchor requirement.
- There is no requirement to quote a theorem, equation, section number, or table in the draft when assigning any score or severity.

### Fix direction — prompt-side (the part we can fix)

Two separable fixes (as the field report notes):

**(a) Anchored justifications.** Extend the output format for the five under-constrained scoring dimensions to require: "Score: XX — anchored to: [specific theorem / proposition number / equation / section / quoted sentence in the draft]." A verdict that cannot quote the specific artifact text that moves it is not a verdict. Apply the same rule to self-attacker severity assignments: each severity-7+ group must cite the specific assumption statement, equation, or claim in the draft that the attack targets.

**(b) Deterministic specs (model-layer, not prompt-layer).** The field report notes that seeded empirical specs can be unstable run-to-run. This is a code-level fix (random seeds in empiricist scripts), not a prompt-layer fix. The prompt-side contribution is that no evaluator prompt currently requires verification that the empirical spec is deterministic before issuing a verdict on it — the empirics-auditor could flag non-deterministic specs as a FAIL condition (not just "did the numbers reproduce from cache" but "does re-running the spec from scratch reproduce the numbers?").

---

## T10 — Sycophancy on Proposal / Over-Penalization on Evaluation

**Verdict: REPRODUCED (two separable gaps; both prompt-side)**

### Evidence

**Gap 1: No stress-test instruction for operator-proposed directions (sycophancy side)**

`session.md` (41 lines total) contains no instruction to stress-test an operator-proposed direction before agreeing to it, and no instruction to surface the strongest objection first when an operator proposes a direction. The only operator-relevant instruction in `session.md` is the halt/recovery protocol and the data inventory procedure. There is no "when the operator proposes X, evaluate it on the merits and surface the strongest counter-argument before accepting" rule.

`core.md` contains no such instruction either. The scribe-trigger rule (core.md line 440) captures that an operator intervention happened, but contains no prescription about how the orchestrator should respond to the proposal before acting on it.

The closest text is in `core.md` / assembled `CLAUDE.md` line 13: "evaluate the current state of the paper on its merits — not on how much effort has been invested." This is a sunk-cost guard for the pipeline's own prior work, not an instruction to stress-test the operator's incoming proposal. These are different behaviors; the existing text does not cover the sycophancy case.

The only anti-sycophancy instruction in the evaluator layer is in `scorer-core.md` line 193 ("Don't be sycophantic. The generator is not your friend.") and `branch-manager.md` line 120 ("Don't be sycophantic about the current work. The orchestrator has spent hours on this. You haven't. That's your advantage."). Neither of these applies to the orchestrator's behavior when the *operator* proposes a direction — they apply to how evaluators treat the pipeline's own outputs.

**Gap 2: No protection against caveat-hunting / over-penalization (over-penalization side)**

The scorer's calibration text says "Most theories should score below 50. A 75+ is uncommon." This is an anti-inflation anchor and is correctly calibrated. However, there is no corresponding anti-deflation instruction — no rule that says "do not hunt for caveats to mark below the tier-appropriate score when the paper satisfies the tier criteria." The asymmetry creates a structural lean toward under-scoring when the evaluator is applying the "adversarial" framing it inherits from the pipeline's broader ethos (which emphasizes adversarial evaluation).

The `substance-over-form leeway` clause in scorer-core.md (lines 196-199) partially addresses one specific form of over-penalization (applying rubric clauses inappropriate to the paper's archetype), but it does not address the more general caveat-hunting pattern: generating many small concerns to mark a paper down from tier-appropriate to below-tier.

The scorer's `+10 directions` table (scorer.md lines 153-165) implicitly pushes toward identifying weaknesses (what would improve each dimension), but does not require the scorer to state when a dimension is already at tier-ceiling and no action is warranted. The "at ceiling (score ≥ 90)" exception only applies at 90+, meaning a scorer can generate marginal-improvement suggestions for every dimension at scores like 75, 80, or 85, creating the appearance of many weaknesses even on a paper that already clears the tier advance bar.

The self-attacker's adversarial framing ("You are hostile... You are destructive... Your job is to break it") is by design. But the triager that processes the self-attack output has no instruction to weight attacks by their relevance to the load-bearing premise vs. the robustness envelope — which means a long list of severity-4-6 robustness attacks with no severity-7+ attacks can still create the impression of a weak paper, contributing to the evaluator's over-penalization pattern.

**What is already addressed:**

- scorer-core.md: absolute-scale calibration anchors prevent pure inflation ("most theories score below 50"). This is correct.
- scorer-core.md: tier-dependent advance thresholds prevent a paper from being penalized for not clearing a higher-tier bar when it's targeting a lower tier. Correct.
- scorer-core.md: `substance-over-form leeway` prevents over-penalization for archetype-misapplied clauses.
- branch-manager.md: anti-sycophancy for the pipeline's own work.

**What is not addressed:**

- No instruction to stress-test the operator's incoming proposal before agreeing.
- No instruction to surface the strongest objection to an operator-proposed direction first.
- No anti-deflation guard in the scorer: "if the paper satisfies H1-H5 and scores at or above the tier advance threshold on at least four of six dimensions, it advances — do not manufacture below-tier concerns."
- No instruction to distinguish "the paper has weaknesses at the caveat level" from "the paper fails the tier test" — these require different responses and the current prompts treat weakness-identification as always relevant to the scoring outcome.

### Fix direction

**Sycophancy (operator proposal):** Add to `session.md` or `core.md` under a heading "When the operator proposes a direction mid-pipeline":

> Before agreeing to a proposed direction, state the strongest single objection to it on the merits. If no serious objection exists, say so explicitly and proceed. Never proceed directly from proposal to agreement without first naming the strongest counter-argument (even if overridden by the operator's judgment). This is not about refusing — it is about ensuring the operator's proposal has been stress-tested before resources are committed.

**Over-penalization (evaluator calibration):** Add to scorer-core.md under Rules:

> **Don't hunt for caveats.** If the paper passes all H requirements and its content score is at or above the tier advance threshold, it advances — the presence of additional weaknesses at the robustness or extension level does not pull a paper below the threshold. A paper is not weak because you can name further improvements; every paper can be improved. Score on what the paper delivers, not on the delta to a hypothetical perfect paper. The adversarial posture belongs to the self-attacker; the scorer's job is calibration, not destruction.

A complementary fix: require the self-attacker to tag each attack with a scope label: `[LOAD-BEARING]` (threatens the headline result) or `[ROBUSTNESS]` (relevant to strengthening but not to result validity). The triager and scorer then have a machine-readable signal to weight load-bearing attacks above robustness attacks when assessing overall quality.

---

## Cross-Cutting Notes

**Separating prompt-side from intrinsic model nondeterminism (for T9):**

The investigation identifies the following as prompt-side contributors (fixable): un-anchored one-sentence justifications in four dimensions, un-anchored severity assignments in the self-attacker, no determinism check in the empirics-auditor. The following are intrinsic model nondeterminism (dampable, not eliminable): temperature-driven variation in how the model weights implicit considerations that are not externalized to text. The fix for the prompt-side reduces the surface area for intrinsic nondeterminism to operate, but does not eliminate it.

**Interaction between T8 and T10 (over-penalization direction):**

The over-penalization pattern (T10) and the wrong-level scrutiny pattern (T8) have the same structural root: the evaluators have no ordering principle that distinguishes load-bearing concerns from robustness concerns. The T8 fix (load-bearing-premise-first requirement) also directly attacks T10's over-penalization: a self-attacker that has been required to exhaust load-bearing attacks first will produce fewer uninstructed robustness attacks at high severity tiers, reducing the input signal that drives the scorer toward caveat-hunting.

**Files and lines (summary):**

| File | Lines | Gap |
|------|-------|-----|
| `templates/agent_bodies/shared/self-attacker-core.md` | 1-14, 19-43 | No load-bearing-premise-first step; no anchor requirement for severity assignments |
| `templates/agent_bodies/shared/scorer-core.md` | 143-149, 153-165, 193 | No anchor requirement for Novelty/Rigor/Parsimony/Fertility justifications; no anti-deflation guard; anti-sycophancy applies only to generator, not operator |
| `templates/runtime/claude/session.md` | entire file (41 lines) | No stress-test / strongest-objection instruction for operator-proposed directions |
| `templates/shared/core.md` | 440 (scribe trigger) | Captures intervention occurred; no prescription on how to evaluate proposal before acting |
| `templates/agents/finance/vocab.json` | (calibration strings) | Calibration is anti-inflation only; no anti-deflation anchor in any dimension string |
