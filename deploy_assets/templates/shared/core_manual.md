# {{RUNTIME_DOC_NAME}} — Research Toolkit (Manual Mode)

{{RUNTIME_DISCIPLINE}}

## Self-review after big changes

AFTER EVERY BIG CHANGE, LAUNCH A SONNET AGENT TO REVIEW YOUR CHANGES FOR ISSUES. IF ANY ISSUES ARE FOUND, ADD A NEW ROUND OF AUDITING AFTER FIXING THE CURRENT ROUND'S ISSUES (EVEN IF THERE ARE ONLY MINOR CHANGES). ITERATE UNTIL DONE.

## Purpose

This project provides research subagents and skills for the domain named under **Variant context** below. The catalog below lists what is available. When the user asks for a research task, pick the agent or skill that fits and invoke it. When the user is unsure where to start, check `paper/`, `output/`, and `references/` to see the current state of the work and propose the next concrete step from the catalog.

## Variant context

- **Paper type:** {{PAPER_TYPE}}
- **Target journals:** {{TARGET_JOURNALS}}
- **Domain:** {{DOMAIN_AREAS}}

These shape the variant-specific agents (`idea-generator`, `theory-generator`, `scorer`, `referee`, `self-attacker`, `idea-reviewer`).

## Agents

Subagents live in `{{AGENT_DIR}}/`. Invoke by name — see your runtime's docs for the exact mechanism. The summaries below are one-liners; read the agent file in `{{AGENT_DIR}}/<name>.md` for full firing rules and rationale.

{{AGENT_CATALOG}}

## Skills

{{SKILL_CATALOG}}

## File organization

```
output/                   # Free-form agent outputs — organize per task
├── evidence/             # Frozen audit inputs, audit reports, and summaries
code/
├── analysis/             # Analysis scripts
├── download/             # Data download helpers
├── explore/              # Exploration scripts
├── tmp/                  # Scratch
└── utils/                # Pre-built helpers (codex-math, openalex, bib-verify, plus variant-specific toolkits; more with extensions — the installed set is what's in this directory)
paper/
├── main.tex
├── sections/
└── simulated_referee_reports/
process_log/
├── manual_evidence_state.json  # Bounded evidence-audit retry counter
└── results_registry.json       # Pending/active/retired computed-result receipts
```

## Computed evidence and paper mutations

For any computed result, use `docs/results_evidence.md`: scripts emit reproducible bundles, renderers derive result-bearing tables/figures from those bundles, and accepted receipts become active in `process_log/results_registry.json`. The manual deployment already initializes the registry and `process_log/manual_evidence_state.json`; do not invent `pipeline_state.json` pointers. Discover accepted evidence from the active registry receipts and their bound reports/artifacts.

After an agent changes paper prose, captions, tables, figures, or citations, run a named checkpoint through `docs/results_evidence.md` before treating the edit as accepted. This launches the independent evidence and citation audits, binds the exact paper state in `process_log/paper_evidence.receipt.json`, and uses `manual_evidence_state.json:loops.evidence` for the bounded retry loop.

Reference docs for each research step are also in `docs/` if you want to read how a particular step is normally handled.

## Python environment

This project ships a self-contained virtualenv at `.venv/` holding every Python dependency the toolkit and skills need. The launch command activates it, so a bare `python3` resolves to `.venv/bin/python3`. If you hit a `ModuleNotFoundError` for a package that should be present, the venv was not activated — run `source .venv/bin/activate`, or call `.venv/bin/python3` directly. To add a dependency: `uv pip install --python .venv <package>`.

{{RUNTIME_SESSION_GUIDANCE}}
