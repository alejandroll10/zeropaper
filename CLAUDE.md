# CLAUDE.md — Meta Project: Pipeline Template Development

## What this is

This is the **template repository** for the autonomous research paper pipeline. We are building and iterating on the pipeline infrastructure itself — agents, setup scripts, CLAUDE.md templates, dashboard, etc.

This file is tracked in git but **overwritten by `setup.sh`** in cloned projects. It is for our development work only. The pipeline's CLAUDE.md that end users see is assembled by `setup.sh` from `templates/shared/core.md` + `templates/runtime/claude/session.md` + variant-specific scoring blocks.

## Setting up a new project

If a user asks to create/set up/start a new research project, run `setup.sh` for them:

```bash
# Basic finance theory
./setup.sh <project-name> --variant finance

# Finance theory + empirical data (CRSP, Compustat, FRED, WRDS)
./setup.sh <project-name> --variant finance --ext empirical

# Macro theory
./setup.sh <project-name> --variant macro

# Finance theory + LLM experiments
./setup.sh <project-name> --variant finance --ext theory_llm

# Combine extensions
./setup.sh <project-name> --variant finance --ext empirical --ext theory_llm
```

This creates a standalone project folder with assembled CLAUDE.md, agents, and skills. After setup, tell the user to:

1. `cd <project-name>`
2. Edit `.env` with any required API keys (FRED, WRDS, etc.)
3. Run `claude --dangerously-skip-permissions`
4. Say "Run the pipeline."

## Repository structure

```
templates/
├── shared/
│   └── core.md              # Runtime-agnostic pipeline orchestrator template
├── runtime/
│   └── claude/
│       └── session.md       # Claude-specific session guidance (injected as {{RUNTIME_SESSION_GUIDANCE}})
├── agent_metadata/          # JSON metadata for agent assembly (tools, model, description)
│   ├── claude_shared_agents.json
│   ├── claude_finance_agents.json
│   └── claude_macro_agents.json
├── agent_bodies/            # Agent prompt bodies (plain markdown)
│   ├── shared/              # Domain-agnostic agent prompts
│   ├── finance/             # Finance variant agent prompts
│   └── macro/               # Macro variant agent prompts
├── skill_metadata/          # JSON metadata for skill assembly
│   ├── claude_codex_math_skills.json
│   ├── claude_empirical_skills.json
│   └── claude_theory_llm_skills.json
├── skill_bodies/            # Skill prompt bodies (plain markdown)
│   ├── codex_math/
│   ├── empirical/
│   └── theory_llm/
├── utils/                   # Utility scripts copied into deployed projects
│   └── codex_math/          # Codex proof verification/writing/exploration scripts
├── scoring/
│   ├── finance.md           # Scoring calibrations for finance
│   └── macro.md             # Scoring calibrations for macro
├── agents/                  # (Legacy) raw agent markdown — used as fallback if no metadata exists
│   ├── shared/
│   ├── finance/
│   └── macro/
└── gitignore_project        # .gitignore template for deployed projects

scripts/
├── assemble_claude_agents.py   # Combines agent_metadata JSON + agent_bodies markdown → .claude/agents/*.md
└── assemble_claude_skills.py   # Combines skill_metadata JSON + skill_bodies markdown → .claude/skills/*/SKILL.md

extensions/                  # Optional extensions (empirical, theory_llm)
├── empirical/
│   ├── agent_metadata/      # shared_agents.json, finance_agents.json, macro_agents.json
│   ├── agent_bodies/        # shared/, finance/, macro/
│   └── utils/               # Python/shell utilities copied into project
└── theory_llm/
    ├── agent_metadata/      # agents.json
    ├── agent_bodies/        # Agent prompt bodies
    └── llm_client.py        # LLM client copied into project

setup.sh                     # Clones repo, assembles CLAUDE.md + agents + skills for chosen variant
dashboard.html               # Live progress dashboard
test_scripts/                # Skill verification scripts (removed on deploy)
```

## Supported variants

| Variant | Flag | Status | Target journals |
|---------|------|--------|-----------------|
| `finance` | `--variant finance` (default) | Working (v2) | JF, JFE, RFS |
| `macro` | `--variant macro` | In development | AER, Econometrica, QJE, JPE, ReStud, JME |

## Supported extensions

| Extension | Flag | Status |
|-----------|------|--------|
| `empirical` | `--ext empirical` | Working |
| `theory_llm` | `--ext theory_llm` | Working (v1) |

Legacy: `--variant finance_llm` is shorthand for `--variant finance --ext theory_llm`.

## Core skills (all variants)

| Skill | Description |
|-------|-------------|
| `codex-math` | OpenAI Codex (gpt-5.4) for proof verification, writing, and exploration. Erratic genius — ~50% false positive rate, always triage. Scripts at `code/utils/codex_math/`. |

## How setup.sh works

1. Clones this repo into a new project folder
2. Reads `--variant` flag (default: `finance`)
3. Assembles CLAUDE.md:
   - Reads `templates/shared/core.md` (runtime-agnostic orchestrator)
   - Injects `templates/runtime/claude/session.md` as `{{RUNTIME_SESSION_GUIDANCE}}`
   - Injects `templates/scoring/{variant}.md` as `{{SCORING}}`
   - Replaces `{{PAPER_TYPE}}`, `{{TARGET_JOURNALS}}`, `{{DOMAIN_AREAS}}`, `{{RUNTIME_DOC_NAME}}`, `{{AGENT_DIR}}`, `{{SKILL_DIR}}`
4. Assembles agents via `scripts/assemble_claude_agents.py`:
   - Shared: `agent_metadata/claude_shared_agents.json` + `agent_bodies/shared/*.md`
   - Variant: `agent_metadata/claude_{variant}_agents.json` + `agent_bodies/{variant}/*.md`
   - Falls back to raw `templates/agents/{variant}/*.md` if no metadata JSON exists
5. Injects variant context (paper type, journal list, domain) into key agents
6. Creates project structure (output/, paper/, code/, etc.) and initial pipeline state
7. Installs core Python deps (sympy, matplotlib) via `uv pip install`
8. Assembles core skills (codex-math) and copies utility scripts to `code/utils/`
9. Applies extensions (`--ext empirical`, `--ext theory_llm`):
   - Assembles extension agents via `assemble_claude_agents.py` from extension metadata + bodies
   - Assembles extension skills via `scripts/assemble_claude_skills.py` from skill metadata + bodies
   - Copies utilities, creates dirs, appends API keys to `.env`
10. Removes template infrastructure, detaches from origin, commits initial state

## Adding a new variant

1. Create agent metadata: `templates/agent_metadata/claude_{variant}_agents.json`
2. Create agent bodies: `templates/agent_bodies/{variant}/` with markdown prompts
3. Create `templates/scoring/{variant}.md` with scoring calibrations
4. Add variant config to `setup.sh` (paper type, target journals, journal list, domain areas)
5. Test: `./setup.sh --variant {variant} --local`

## Architecture: runtime-agnostic core + runtime-specific packaging

The pipeline is split into two layers:

- **Runtime-agnostic**: `templates/shared/core.md` (orchestrator logic, pipeline stages, scoring), `templates/agent_bodies/` (agent prompts), `templates/scoring/` — these are the same regardless of runtime.
- **Runtime-specific**: `templates/runtime/claude/session.md` (Claude Code session guidance), `templates/agent_metadata/claude_*.json` (Claude agent frontmatter — tools, model, description), `templates/skill_metadata/claude_*.json`, `scripts/assemble_claude_*.py`.

This separation is designed to support future runtimes (e.g., Codex/Antigravity) by reusing the same core + agent bodies while swapping in different metadata and session guidance.

## Agent classification

Agents are either **shared** (identical across variants) or **variant-specific** (different prompts per domain). Each agent is defined as:
- **Metadata** (`agent_metadata/claude_*.json`): runtime-specific frontmatter (tools, model, description)
- **Body** (`agent_bodies/{shared,variant}/*.md`): runtime-agnostic prompt content

**Shared** (domain-agnostic, receive variant context via injection):
- `literature-scout` — searches for papers (variant context provides target journals)
- `idea-prototyper` — quick math feasibility + surprise check
- `theory-explorer` — computational verification, calibration, parameter exploration, plots
- `math-auditor` — checks derivations step-by-step
- `math-auditor-freeform` — reads as skeptical reader
- `novelty-checker` — searches web for prior work
- `paper-writer` — writes LaTeX from inputs
- `style` — checks writing style
- `scribe` — documents the process

**Variant-specific** (different prompts per domain):
- `idea-generator` — needs domain-specific brainstorming patterns
- `idea-reviewer` — needs domain-specific evaluation criteria
- `theory-generator` — needs domain-specific model structure guidance
- `scorer` — needs domain-specific calibrations
- `self-attacker` — needs domain-specific attack vectors
- `referee` — needs domain-specific journal standards

**Extension agents** (added by `--ext` flags):
- `empiricist` — empirical analysis (variant-specific, `--ext empirical`)
- `empirics-auditor` — verifies empirical code/results (shared, `--ext empirical`)
- `experiment-designer` — LLM experiments (shared, `--ext theory_llm`)
- `experiment-reviewer` — validates experiment methodology (shared, `--ext theory_llm`)
