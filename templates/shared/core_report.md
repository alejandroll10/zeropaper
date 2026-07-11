# {{RUNTIME_DOC_NAME}} — {{RUNTIME_DOC_SUBTITLE}}

{{RUNTIME_DISCIPLINE}}

## Purpose

This project produces a **referee report** on an external submission under review for a {{TARGET_JOURNALS}}. The user drops the submission in `submission/`; the system fans out adversarial audits in parallel, then synthesizes them into a single editor-facing report at `report/referee_report.md`.

This is a **one-shot deliverable**, not an iterative pipeline. There is no theory to develop, no paper to write, no revision loop. The job is to read the submission as a referee would, surface every substantive concern the audits find, and write the report.

## Variant context

- **Submission domain:** {{DOMAIN_AREAS}}
- **Target journal class:** {{TARGET_JOURNALS}}

These calibrate the `referee`, `referee-freeform`, and `referee-mechanism` agents to the right journal bar. They do **not** mean the submission must look like a paper this pipeline would produce — submissions vary in form, and structural divergence from this pipeline's house style is not a defect.

## Core principle: read the paper that's there

Refereeing means evaluating what the authors wrote, not the paper you would have written on the same topic. If the framing is narrower than you'd prefer, the contribution is still whatever the results actually deliver. If a notation choice is unfamiliar but internally consistent, it is not an error. Reserve criticism for substantive defects — wrong derivations, unsupported claims, missing prior work, mischaracterized institutions, framing-content gaps — not for stylistic preference.

## Core principle: adversarial but fair

The audit agents are adversarial by design — that is their job. The synthesizer's job is to triage their findings: real defects go in the report, false positives get suppressed, ambiguous calls get framed as questions to the authors rather than verdicts. A referee report that lists every audit flag verbatim is a bad report; one that names the three or four issues that actually matter is a good one.

## Core principle: cite the audit, not your intuition

Every major concern in the final report should be traceable to a specific finding in `audits/*.md` — a line in the math audit, a citation flagged by `polish-bibliography`, a regulatory misstatement flagged by `polish-institutions`. If the synthesizer wants to raise a concern no audit surfaced, it must say so explicitly and explain why ("synthesizer note: not flagged by any audit, but ..."). This keeps the report grounded in the audit record and makes it auditable in turn.

## Core principle: the submission is read-only

The pipeline never edits `submission/`. Audit outputs go to `audits/`, the final report goes to `report/`, scratch goes to `process_log/`. If an audit needs to render LaTeX or extract figures, it does so in a working copy under `process_log/`, never in place.

## Core principle: one-shot, not iterative

There is no v2 of the report. If the editor sends back a revised submission later, that is a fresh deployment on a fresh `submission/` folder. Do not design the report around "what the authors should do next" — refereeing decides whether *this version* warrants publication; revision is the authors' job.

---

## Workflow

```
Step 1: Triage         ──→ detect submission format, extract metadata,
                            choose which audits to run
Step 2: Audit fan-out  ──→ launch all enabled audit agents in parallel
                            against submission/ paths
Step 3: Synthesis      ──→ report-synthesizer reads audits/*.md,
                            writes report/referee_report.md
```

### Step 1: Triage

Read `submission/` and decide:

- **What's there?** PDF only, `.tex` source only, or both. PDF-only runs the full fan-out, but two audits degrade: `polish-formula` cannot call `codex-math` for symbolic verification (its shell-out wants a `.tex` path and a pattern) — it falls back to manual + sympy re-derivation from the parsed PDF text, which catches typesetting-style errors but is weaker on long algebraic chains. `polish-numerics` can still re-run arithmetic from stated parameter values but cannot rerun simulations or calibration solves whose code lives in source. Each affected agent prepends a "source not available — degraded check" note to its output so the synthesizer can weigh its findings accordingly.
- **What format is the submission in?** Supported: PDF, `.tex` source bundle (with `sections/`, `refs.bib`), or both. Not supported in v1: `.docx`, `.epub`, scans without OCR, and `.md`-only drafts. If `submission/` contains only an unsupported format, halt and tell the user to convert to PDF or LaTeX source first — the audit agents are calibrated for PDF/LaTeX structure (numbered equations, `\cite` keys, section hierarchy) and would silently produce empty or hallucinated outputs on other formats.
- **What's the paper about?** Extract title, abstract, claimed contribution. Write a one-paragraph triage note to `process_log/triage.md` — the synthesizer reads it for context.
- **Is replication code shipped?** If `submission/` includes a `code/` directory, replication scripts, or a Dockerfile, note it in the triage so the base referees know to weigh reproducibility in their assessment. (In v1 the empirical-extension audit agents that would re-run such code are **not** wired into the fan-out — see the install-only block below; deep code-level adversarial auditing of external empirical submissions is a v2 feature. The base referees still evaluate empirical methodology at the editorial level.)
- **Is the submission domain in scope?** If the paper is wildly outside {{DOMAIN_AREAS}} (e.g., a pure-math paper sent to a finance pipeline), note it in `process_log/triage.md` and proceed anyway — the referee agents are calibrated for the variant but the audits are general.

### Step 2: Audit fan-out

Launch in parallel against the submission. The orchestrator passes each agent the exact output path from the **Output file** column below; the synthesizer references those filenames verbatim, so deviating breaks aggregation.

| Agent | Audit | Output file | Background-launch? |
|-------|-------|-------------|--------------------|
| `math-auditor` | Step-by-step derivation check | `audits/math.md` | no |
| `math-auditor-freeform` | Skeptical-reader pass on the math | `audits/math_freeform.md` | no |
| `polish-formula` | Re-derive numbered equations from surrounding text | `audits/formula.md` | no |
| `polish-numerics` | Re-do calibrations, examples, back-of-envelopes | `audits/numerics.md` | no |
| `polish-consistency` | Intra-paper contradictions | `audits/consistency.md` | no |
| `polish-equilibria` | Unstated multiple equilibria, missing assumptions | `audits/equilibria.md` | no |
| `polish-identification` | Identification claims aligned with what the design delivers | `audits/identification_polish.md` | no |
| `polish-prose` | Over-armored / defensive prose that buries the contribution | `audits/prose.md` | no |
| `polish-bibliography` | For every citation, verify the in-text claim about it | `audits/bibliography.md` | yes (OpenAlex + WebSearch) |
| `polish-institutions` | Real-world claims (regulations, conventions, market facts) | `audits/institutions.md` | yes (WebSearch) |
| `bib-verifier` | Cite-key existence + title/year correctness vs OpenAlex | `audits/bib_verify.md` | yes (OpenAlex) |
| `novelty-checker` | Has this result already been published? | `audits/novelty.md` | yes (web) |
| `self-attacker` | Adversarial weakness finder | `audits/weaknesses.md` | no |
| `referee` | Structured referee report (rubric-driven) | `audits/referee_structured.md` | no |
| `referee-freeform` | Free-form editorial read | `audits/referee_freeform.md` | no |
| `referee-mechanism` | Does the claimed mechanism deliver the claimed result? | `audits/referee_mechanism.md` | no |

Background-launched agents (web-dependent) can hang — poll their output file every few minutes; if empty or not growing after a few checks, re-launch with the same prompt.

**Extension composition is install-only in v1.** `--ext empirical` and `--ext theory_llm` compose with `--mode report` to install their *skills* (WRDS / FRED / Census / SEC data helpers, OpenAlex, LLM-experiment client) so the audit agents can spot-check external data or call an external LLM if needed — but the *audit agents* those extensions ship (`empirics-auditor`, `identification-auditor`, `data-integrity-auditor`, `data-selection-auditor`, `method-checker`, `claim-enumerator` / `claim-grounder` / `claim-verifier`, `experiment-reviewer`) are **not** added to the report-mode fan-out and are pruned at assembly time. Those agents were designed against the pipeline's *own* empiricist output (`output/stage3a/empirical_analysis.md`, `code/empirical.py`, etc.) and would need substantial rewrites to operate on an external submission. The base referees (`referee`, `referee-freeform`, `referee-mechanism`) already evaluate empirical submissions holistically — they raise identification, magnitude, and robustness concerns at the editorial level. Full code-level adversarial auditing of external empirical submissions is a v2 feature.

### Step 3: Synthesis

After all audits complete (or after a maximum wait with explicit notes on any that timed out), launch `report-synthesizer`. It reads every file in `audits/`, the triage note, and the submission itself, and writes `report/referee_report.md` with this structure:

```
# Referee report: <submission title>

## Summary
<one paragraph: what the paper claims, what it actually delivers>

## Strengths
<bulleted, 2–5 items>

## Major concerns
<numbered, evidence-backed; each cites the audit file(s) that grounds it>

## Minor concerns
<numbered, terser>

## Questions to authors
<optional — for ambiguous calls the synthesizer didn't want to commit on>

## Verdict
<one of: Accept | Minor revision | Major revision | Reject>
<one paragraph of rationale>
```

The synthesizer is not a rubber-stamp aggregator. It deduplicates concerns raised by multiple audits, downgrades false positives (with a one-line justification in `report/notes.md`), and weighs concerns by how much they affect the paper's claimed contribution.

---

## File organization

```
submission/               # READ-ONLY: paper.pdf and/or main.tex + sections/ + refs.bib
                          # Drop the submission here before launching.
audits/                   # One file per audit agent
report/
├── referee_report.md     # Final editor-facing deliverable
└── notes.md              # Synthesizer's working notes (false-positive triage, etc.)
process_log/
├── triage.md             # Step 1 output
└── audit_log.md          # Which agents ran, on what input hash, when
{{AGENT_DIR}}/            # Subagent definitions (do not edit at runtime)
{{SKILL_DIR}}/            # Skill definitions
docs/                     # Reference docs on the pipeline's audit conventions
```

There is no `paper/`, no `output/stage*/`, no `pipeline_state.json`, no `dashboard.html` — this mode does not produce a paper, has no stages, has no state machine, and has no live progress to track beyond the audit log. (`output/codex_audits/`, `output/codex_proofs/`, `output/codex_explorations/` may exist as working dirs for the `codex-math` skill that polish-formula and math-auditor invoke; that is the only `output/` content in report mode.)

## Python environment

This project ships a self-contained virtualenv at `.venv/` holding every Python dependency the audit agents and skills need. The launch command activates it, so a bare `python3` resolves to `.venv/bin/python3`. If you hit a `ModuleNotFoundError` for a package that should be present, the venv was not activated — run `source .venv/bin/activate`, or call `.venv/bin/python3` directly. To add a dependency: `uv pip install --python .venv <package>`.

{{RUNTIME_SESSION_GUIDANCE}}
