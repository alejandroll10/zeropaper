# INV-6: Robotic Prose, Thin Economic Story, Artifact Leakage (T13)

**Template HEAD investigated:** current (post-d9415f4)
**Files read:** `templates/agent_bodies/shared/paper-writer.md`, `style.md`, `polish-prose.md`, `polish-consistency.md`; `templates/shared/docs/stage_5.md`, `stage_7.md`, `stage_9.md`; `templates/shared/core.md`; `/tmp/inv_finance/.claude/agents/paper-writer.md` (assembled); `templates/agents/finance/vocab.json`.

---

## Sub-symptom 1: Economic-question-first framing — REPRODUCED

**Verdict:** REPRODUCED (instruction exists but is too thin to enforce; no downstream check).

**Evidence:**

`templates/agent_bodies/shared/paper-writer.md:31`:
> `- Open with the question, not the answer`

This is the *entire* positive framing mandate for the introduction. One bullet. No negative form ("do not open with the headline coefficient"), no example of the correct first sentence vs. the wrong first sentence, no enforcement checkpoint anywhere downstream. The style agent (Stage 7, `style.md`) has no rule about introduction framing — it is a mechanical copy-editor (voice, tense, word choice). The `polish-prose` agent (`polish-prose.md:22-26`) detects "buried thesis sentences" (thesis more than two paragraphs in) and "defensive framing of the contribution" (leading with what the paper does not claim), but neither of these covers the failure mode of opening sentence 1 with a coefficient or headline estimate rather than a question. The check at `polish-prose.md:23-24`:

> `7. **Buried thesis sentences.** A sentence of the form "this paper shows X" ... that is more than two paragraphs into the introduction.`

addresses *late* thesis placement, not *estimate-first* sentence 1. A paper that opens "The coefficient on bank leverage is −0.42 (t = −3.8)..." passes every currently-defined check. The `stage_5.md` outline step (`step 1`) only asks the orchestrator to check whether the outline "addresses the self-attack points" and "positioning against the literature is accurate" — framing quality is not in the outline review gate.

**Root cause:** the "Open with the question" bullet in paper-writer is neither specific enough to prevent the misfire nor backed by a checkpoint that can catch it. No agent is assigned to enforce introduction-first-sentence discipline.

**Fix direction:**
- In `paper-writer.md` introduction spec (line 31), replace the one-liner with a 2-3 sentence rule: "Open with the economic question in declarative form. The first sentence must name an economic phenomenon or a puzzle, not a coefficient, not a p-value, not a methodology. Wrong: 'We find a coefficient of −0.42 on leverage.' Right: 'Why do highly levered banks reduce lending more sharply in downturns?'" Add the negative form and one negative example.
- Add a `polish-prose` check (item 8): flag any introduction whose first sentence contains a number, percent sign, or coefficient reference (regex: `[0-9]`, `\%`, `β`, `\alpha`, `coef`, `estimate`, `p-value`, `t-stat`) — severity `critical`. This is the natural home given `polish-prose` already audits introduction structure (buried thesis, defensive framing).

---

## Sub-symptom 2: Anti-AI-style guidance — REPRODUCED

**Verdict:** REPRODUCED — the "anti-AI style" instruction is generic, positive-only, and lacks banned-construction specificity.

**Evidence:**

The full anti-AI-style mandate in `paper-writer.md` (lines 140–151, `## Style rules (mandatory)`) reads:

```
- Active voice always
- No filler before "that"
- No self-congratulatory adjectives
- No naked "this"
- No em-dashes
- No "I show that" — just state the result
- Don't "assume" model structure — state it
- Concrete language, normal sentence structure
- Abstract ≤ 100 words.
- Define every acronym at first use.
```

The `style.md` agent expands these with mechanical rules (word-choice substitutions at lines 29–42, filler-adverb deletion at lines 44–45, passive-voice rewrite at lines 47–48), but the style agent is a *copy-editor* — it operates word-by-word on violations it can identify deterministically, and it explicitly does not rewrite surrounding prose.

What is absent: any instruction against the specific AI-prose tells the operator observed — hedge stacking that makes confident claims disappear ("broadly consistent with what could be a somewhat elevated..."), generic framing that could describe any paper ("this paper contributes to the growing literature on X"), organizational clichés ("in this section we..."), summary sentences that restate the prior section opener, or flat academic boilerplate that fails the reader-attention test. `polish-prose.md` catches *over-hedging* (lines 14-17, "hedge stacking" flagging 2+ hedge tokens) and *abstract bloat* (line 17-18), which are partial coverage of the AI-prose failure — but `polish-prose` was built for the "over-armored, defensive" failure mode, not the "undifferentiated machine-generated phrasing" failure mode. There is no rule that asks: does any sentence read like a form letter? Is any paragraph structurally identical to a default LLM output template?

The finance `vocab.json` contains no prose-quality calibration. The scorer's `## Presentation notes` section (`scorer-core.md:183-184`) allows expositional fixes to be forwarded to paper-writer — but the scorer reads the *theory draft*, not the rendered LaTeX, so it cannot flag AI-prose in the paper itself.

**Root cause:** The instruction set is a list of mechanical prohibitions (em-dashes, "I show that"), not a positive model of what economic-paper prose sounds like or a negative list of AI-prose signatures. None of these rules would catch "This paper contributes to the growing literature on financial intermediation by providing a new theoretical framework..." — which passes all current checks.

**Fix direction:**
- In `paper-writer.md` style rules, add a "Prose tells — delete on sight" block with a short list of banned constructions that are AI signatures: "this paper contributes to the growing/nascent literature", "we shed light on", "this study examines", "in this paper we", organizational openers ("In this section we..."), summary openers ("In summary,...", "To summarize,...") not at the end of a section.
- In `style.md`, add one new rule under "Word choice — edit": a list of the above banned openers, edit to delete / restructure. The `style` agent's mechanical-edit mandate is the right home because these are pattern-matchable.
- Consider adding a `polish-prose` item: flag any sentence of the form "this paper contributes to / studies / examines / investigates" that appears in the introduction body (not abstract — the abstract's word constraints handle it separately). Severity `major`.

---

## Sub-symptom 3: Thin economic story — PARTIALLY-ADDRESSED

**Verdict:** PARTIALLY-ADDRESSED — the referee-mechanism agent (`referee-mechanism.md`) is the primary backstop; it has explicit authority to return MECHANISM-DECORATIVE and is calibrated to detect "economic story is window dressing on a structural identity." However, it operates at Stage 6 (after the paper is written), reads the rendered paper, and its verdict feeds into revision loops that may iterate without structural improvement. No agent between Stage 2 and Stage 6 is specifically assigned to ask "does the paper's introduction actually convey the economic force, not just state a result?"

**Evidence:**

`templates/agent_bodies/shared/referee-mechanism.md:3`:
> "does the economic force the paper invokes actually deliver the result the paper claims, through the channel the paper claims, for reasons a seminar audience would find convincing?"

`templates/agent_bodies/shared/referee-mechanism.md:97`:
> "MECHANISM-DECORATIVE — the economic story is window dressing on a structural identity or a standard result in a new guise."

This is real enforcement of economic-story depth. But it fires at Stage 6 (referee round), which means: (a) thin economic story in the paper draft goes through Stage 5 (paper-writer) and Stage 7 (style) without being caught; (b) a DECORATIVE verdict feeds into revision loops that have a hard cap and a fallback to "narrow-path shipping." The `polish-prose` agent (`polish-prose.md`) is explicitly prohibited from adding new prose ("You don't propose adding new prose beyond a one-sentence consolidated version..."), so it cannot install a stronger economic story; it can only remove over-hedging.

The `paper-writer.md` introduction spec at line 31 says "Open with the question, not the answer" and the framing section (lines 19-24) ties the framing choice to implication tags (PUZZLE-CANDIDATE / NOVEL / SUPPORTED). But none of this requires the introduction to name the economic *force* (the agent, friction, and channel). A paper that says "We study when financial intermediaries reduce lending" and then jumps to the coefficient satisfies "open with the question" but has no economic story in the introduction.

**Fix direction:**
- In `paper-writer.md` introduction spec (line 31-43), add: "Paragraph 1 must name the economic force: which agents face which friction, and through what channel the documented relationship emerges. 'We study whether X affects Y' is not an economic question — 'We ask why firms with exposure to X reduce Y: the friction is [Z]' is." Cross-reference the scorer-freeform and referee-mechanism criteria explicitly so paper-writer has a self-check.
- In `polish-prose.md`, add item 8: flag an introduction that lacks a named friction or economic agent by end of paragraph 1 — severity `major`. This would be a new check ("economic story absent from introduction") that is distinct from the existing structural checks.

---

## Sub-symptom 4: Pipeline artifact leakage — REPRODUCED

**Verdict:** REPRODUCED — no agent in the template scans the rendered paper for pipeline-internal strings.

**Evidence:**

A systematic search across all four agents (paper-writer.md, style.md, polish-prose.md, polish-consistency.md) and the stage docs (stage_5.md, stage_7.md, stage_9.md) found zero instructions to scan for or remove pipeline-internal strings. Specifically:

- `paper-writer.md`: Contains extensive internal path references (`output/stage3a/`, `output/stage2/`, etc.) as *inputs the agent reads*, but no instruction to *exclude* those paths from the paper text it writes. The agent is told not to hallucinate citations and not to fabricate results, but there is no "do not write pipeline filenames into the paper" rule.
- `style.md`: The mechanical style rules (lines 12-102) do not include any check for internal strings. The agent edits only voice, tense, word-choice, and formatting rules. It explicitly does not flag content-type violations.
- `polish-prose.md`: The seven checks (repeated caveats, hedge stacking, abstract bloat, undefined acronyms, section-opener resummary, defensive framing, buried thesis) do not include a check for pipeline-internal strings.
- `polish-consistency.md`: The eight checks (prediction↔proposition, heading↔text, intro↔qualification, label↔object, approximately-vs-exact, endogenous-as-exogenous, gross↔net, comparative-static contradiction) are all content-logic checks. No check for artifact strings.
- `stage_9.md`: The "what each polish agent owns" ownership table (`stage_9.md:47-58`) assigns no agent to artifact leakage detection.

The closest thing to protection is the `arpipeline.sty` / `% PIPELINE-MANAGED` discipline in `paper-writer.md:82-84` and `style.md:102`, but this prevents *deletion* of pipeline infrastructure from `main.tex` — it does not prevent pipeline-internal strings from appearing in the paper's prose sections.

The failure mode is coherent: paper-writer reads files named `output/stage3a/empirical_analysis.md`, `process_log/pipeline_state.json`, and verdict words (`ADVANCE`, `REVISE`, `PASS`, `FAIL`) in its working context. Under a confused invocation or a context-window bleed, those strings can appear literally in `paper/sections/introduction.tex`. No agent catches this before the paper is submitted.

**Fix direction — primary:**
In `polish-consistency.md`, add a new check (item 9, severity `critical`):

> **Pipeline-artifact leakage.** Scan all `paper/sections/*.tex` and `paper/internet_appendix.tex` for strings that are internal pipeline artifacts and have no legitimate place in a journal paper. Flag any instance of:
> - Pipeline path patterns: `output/`, `process_log/`, `stage3a`, `stage_3`, `stage_1`, `stage_2`, etc. (regex: `output/|process_log/|stage[0-9]`)
> - Internal verdict words standing alone as prose: `ADVANCE`, `REVISE`, `PASS`, `FAIL`, `ABANDON`, `MAJOR REWORK` (all-caps, not inside a `\verb` or code environment)
> - Agent names used as prose: `paper-writer`, `empiricist`, `scorer`, `math-auditor`, `theory-generator`, `claim-verifier`, `claim-grounder`, `claim-enumerator` (in prose context, not in a methodology citation)
> - Pipeline-state keys: `pipeline_state`, `current_stage`, `polish_round`, `bib_verify_round`
>
> Severity: `critical` for any match. Suggested fix: delete the string and rephrase the sentence without reference to the pipeline artifact.

**Fix direction — secondary (prevention):**
In `paper-writer.md` under `## Rules` (after line 157), add: "**No pipeline artifact strings in paper prose.** Do not write pipeline-internal paths (`output/`, `process_log/`), stage labels (`stage3a`, `Stage 5`), verdict words (`ADVANCE`, `REVISE`, `PASS`, `FAIL`), or agent names (`empiricist`, `paper-writer`, `scorer`) into any `paper/sections/*.tex` file. These are working-context strings; they do not belong in the manuscript."

---

## Cross-cutting assessment

The three sub-symptoms are related: paper-writer produces the first draft, and all three failure modes originate there — estimate-first framing is a paper-writer output, AI-prose tells are paper-writer output, and artifact strings are paper-writer output. The style/polish agents catch mechanical violations and consistency issues but are not designed to catch any of these three patterns. The referee-mechanism agent catches thin economic story at Stage 6, but only after the paper draft already exists and only as part of a revision loop with a hard cap.

None of the three failures would be caught by the current stage-9 polish suite as written. All three are REPRODUCED against the current template.

---

## Ownership table for proposed fixes

| Check to add | Agent / file | Severity |
|---|---|---|
| Estimate/number in introduction sentence 1 | `polish-prose.md` item 8, `paper-writer.md` intro spec | critical |
| Banned AI-prose constructions | `style.md` word-choice rules, `paper-writer.md` style rules | edit (style) / mandatory (paper-writer) |
| Named economic force in introduction paragraph 1 | `polish-prose.md` item 9, `paper-writer.md` intro spec | major |
| Pipeline artifact strings in paper prose | `polish-consistency.md` item 9 | critical |
| Prevention at source | `paper-writer.md` Rules section | rule |
