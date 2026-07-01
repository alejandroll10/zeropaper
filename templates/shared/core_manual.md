# {{RUNTIME_DOC_NAME}} — Research Toolkit (Manual Mode)

{{RUNTIME_DISCIPLINE}}

## Self-review after big changes

AFTER EVERY BIG CHANGE, LAUNCH A SONNET AGENT TO REVIEW YOUR CHANGES FOR ISSUES. IF ANY ISSUES ARE FOUND, ADD A NEW ROUND OF AUDITING AFTER FIXING THE CURRENT ROUND'S ISSUES (EVEN IF THERE ARE ONLY MINOR CHANGES). ITERATE UNTIL DONE.

## Purpose

This project provides research subagents and skills for {{DOMAIN_AREAS}}. The catalog below lists what is available. When the user asks for a research task, pick the agent or skill that fits and invoke it. When the user is unsure where to start, check `paper/`, `output/`, and `references/` to see the current state of the work and propose the next concrete step from the catalog.

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
└── utils/                # Pre-built helpers (codex-math, openalex, bib-verify, nber-agenda, ssj; more with extensions)
paper/
├── main.tex
├── sections/
└── simulated_referee_reports/
```

Reference docs for each research step are also in `docs/` if you want to read how a particular step is normally handled.

{{RUNTIME_SESSION_GUIDANCE}}
