# Auto AI Research Template

Autonomous finance theory paper generator. Clone, launch, walk away. The system discovers a problem, generates a theory, verifies it adversarially, and writes a publication-ready paper.

## Quick start

```bash
./setup.sh my-paper
cd my-paper
claude --dangerously-skip-permissions
```

Then say: **"Run the pipeline."**

## Prerequisites

### System packages (Ubuntu/Debian)

```bash
sudo apt-get install python3 python3-pip git bubblewrap
```

### Python tools

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

## What happens

The pipeline runs autonomously through these stages:

```
Problem Discovery → Theory Generation → Math Audit → Novelty Check
→ Implications → Self-Attack → Scorer Gate → Paper Writing
→ Style Check → Referee Simulation → Done
```

Each stage has adversarial quality gates. Failed theories get revised, reworked, or abandoned. The system loops until it produces a paper that passes a simulated referee review.

## Agents

| Agent | Role |
|-------|------|
| `literature-scout` | Web search for papers, builds literature map |
| `theory-generator` | Proposes models (fresh/mutate/crossover strategies) |
| `math-auditor` | Adversarial step-by-step derivation verification |
| `novelty-checker` | Web search to verify result is genuinely new |
| `self-attacker` | Hostile weakness finder, severity-ranked attacks |
| `scorer` | Quality gate: advance/revise/abandon decisions |
| `paper-writer` | Assembles LaTeX paper from scored theory |
| `referee` | Simulates top-journal R1 review |
| `style` | Enforces writing style guide |
| `scribe` | Background documentation of the process |

## Safety

Sandbox is pre-configured in `.claude/settings.json`:
- Bash restricted to project folder only
- Cannot read SSH keys or AWS credentials
- WebSearch and WebFetch work freely (for literature)
- `bubblewrap` enforces restrictions at OS level

## Project structure

```
├── CLAUDE.md                 # Pipeline orchestration logic
├── setup.sh                  # One-command setup
├── .claude/
│   ├── settings.json         # Sandbox config
│   └── agents/               # 10 custom subagents
├── output/
│   ├── stage0/               # Problem discovery
│   ├── stage1/               # Theory drafts, audits, novelty checks
│   ├── stage2/               # Implications
│   └── stage3/               # Self-attack, scorer decisions
├── paper/
│   ├── main.tex
│   ├── sections/             # One .tex file per section
│   └── referee_reports/
├── process_log/
│   ├── pipeline_state.json   # Current stage, attempt counts
│   └── history.md            # Full narrative record
└── references/
```

## License

MIT
