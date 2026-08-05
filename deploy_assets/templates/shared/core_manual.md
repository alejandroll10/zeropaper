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
```

Reference docs for each research step are also in `docs/` if you want to read how a particular step is normally handled.

## Python environment

This project ships a self-contained virtualenv at `.venv/` holding every Python dependency the toolkit and skills need. The launch command activates it, so a bare `python3` resolves to `.venv/bin/python3`. If you hit a `ModuleNotFoundError` for a package that should be present, the venv was not activated — run `source .venv/bin/activate`, or call `.venv/bin/python3` directly. To add a dependency: `uv pip install --python .venv <package>`.

{{RUNTIME_SESSION_GUIDANCE}}
