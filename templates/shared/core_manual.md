# {{RUNTIME_DOC_NAME}} — Research Toolkit (Manual Mode)

{{RUNTIME_DISCIPLINE}}

## Purpose

This project provides research subagents and skills for {{DOMAIN_AREAS}}. The catalog below lists what is available. When the user asks for a research task, pick the agent or skill that fits and invoke it. When the user is unsure where to start, check `paper/`, `output/`, and `references/` to see the current state of the work and propose the next concrete step from the catalog.

## Variant context

- **Paper type:** {{PAPER_TYPE}}
- **Target journals:** {{TARGET_JOURNALS}}
- **Domain:** {{DOMAIN_AREAS}}

These shape the variant-specific agents (`idea-generator`, `theory-generator`, `scorer`, `referee`, `self-attacker`, `idea-reviewer`).

## Agents

Subagents live in `{{AGENT_DIR}}/`. Invoke by name — see your runtime's docs for the exact mechanism.

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
└── utils/                # Pre-built helpers (codex-math, openalex, bib-verify; more with extensions)
paper/
├── main.tex
├── sections/
└── referee_reports/
```

Per-stage reference docs from the autonomous pipeline are also in `docs/` if you want to read how the autonomous version handles a particular step.

{{RUNTIME_SESSION_GUIDANCE}}
