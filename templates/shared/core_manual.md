# {{RUNTIME_DOC_NAME}} — Research Toolkit (Manual Mode)

{{RUNTIME_DISCIPLINE}}

## Purpose

This project gives you a curated set of research subagents and skills for {{DOMAIN_AREAS}}. **You drive — there is no autonomous pipeline running.** Read the catalog below, pick the agent or skill that fits the task, and invoke it directly.

For autonomous end-to-end paper generation instead, re-run `setup.sh` without `--manual`.

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
