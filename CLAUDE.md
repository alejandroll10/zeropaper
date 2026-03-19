# CLAUDE.md — Meta Project: Pipeline Template Development

## What this is

This is the **template repository** for the autonomous research paper pipeline. We are building and iterating on the pipeline infrastructure itself — agents, setup scripts, CLAUDE.md templates, dashboard, etc.

This file is tracked in git but **overwritten by `setup.sh`** in cloned projects. It is for our development work only. The pipeline's CLAUDE.md that end users see is assembled by `setup.sh` from `templates/claude_md/core.md` + variant-specific domain/scoring blocks.

## Repository structure

```
templates/
├── agents/
│   ├── shared/          # Agents used by all variants (literature-scout, math-auditor, etc.)
│   ├── finance/         # Finance theory variant agents (idea-generator, scorer, etc.)
│   └── macro/           # Macro variant agents
├── domains/
│   ├── finance.md       # Domain knowledge block for finance
│   └── macro.md         # Domain knowledge block for macro
├── scoring/
│   ├── finance.md       # Scoring calibrations for finance
│   └── macro.md         # Scoring calibrations for macro
└── claude_md/
    └── core.md          # Pipeline orchestrator template (with {{DOMAIN}}, {{SCORING}} placeholders)

.claude/agents/          # Currently deployed agents (for the finance variant — legacy, will be assembled by setup.sh)
extensions/              # Optional extensions (theory_llm, etc.)
setup.sh                 # Clones repo, assembles CLAUDE.md + agents for chosen variant
dashboard.html           # Live progress dashboard
output/                  # Pipeline output directories (empty in template)
paper/                   # Paper output directories (empty in template)
process_log/             # Pipeline state (initial state in template)
```

## Supported variants

| Variant | Flag | Status | Target journals |
|---------|------|--------|-----------------|
| `finance` | `--variant finance` (default) | Working (v2) | JF, JFE, RFS |
| `macro` | `--variant macro` | In development | AER, Econometrica, QJE, JPE, ReStud, JME |
| `finance_llm` | `--variant finance_llm` | Working (v1) | JF, JFE, RFS + CS venues |

## How setup.sh works

1. Clones this repo into a new project folder
2. Reads `--variant` flag (default: `finance`)
3. Assembles CLAUDE.md:
   - Reads `templates/claude_md/core.md`
   - Replaces `{{DOMAIN}}` with contents of `templates/domains/{variant}.md`
   - Replaces `{{SCORING}}` with contents of `templates/scoring/{variant}.md`
   - Replaces `{{PAPER_TYPE}}`, `{{TARGET_JOURNALS}}`, `{{DOMAIN_AREAS}}` with variant-specific strings
4. Copies agents: `templates/agents/shared/*` + `templates/agents/{variant}/*` → `.claude/agents/`
5. Removes template infrastructure (the `templates/` dir itself) from the cloned project
6. Detaches from origin, commits initial state

## Adding a new variant

1. Create `templates/agents/{variant}/` with variant-specific agents
2. Create `templates/domains/{variant}.md` with domain knowledge
3. Create `templates/scoring/{variant}.md` with scoring calibrations
4. Add variant config to `setup.sh` (paper type, target journals, domain areas)
5. Test: `./setup.sh --variant {variant} --local`

## Agent classification

Agents are either **shared** (identical across variants) or **variant-specific** (different prompts per domain).

**Shared** (domain-agnostic):
- `literature-scout` — searches any topic
- `math-auditor` — checks derivations step-by-step
- `math-auditor-freeform` — reads as skeptical reader
- `novelty-checker` — searches web for prior work
- `paper-writer` — writes LaTeX from inputs
- `style` — checks writing style
- `scribe` — documents the process

**Variant-specific** (domain knowledge matters):
- `idea-generator` — needs domain-specific brainstorming patterns
- `idea-reviewer` — needs domain-specific evaluation criteria
- `theory-generator` — needs domain-specific model structure guidance
- `scorer` — needs domain-specific calibrations
- `self-attacker` — needs domain-specific attack vectors
- `referee` — needs domain-specific journal standards

## Current work

Working on `feature/variant-infrastructure` branch. Goal: refactor the monolithic pipeline into a variant-aware template system, with macro as the first additional variant.
