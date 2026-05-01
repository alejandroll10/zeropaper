# Auto AI Research Template

Autonomous research paper generator. Set up a project, launch Claude Code, Codex, or Gemini CLI, walk away. The system discovers a problem, generates a theory, verifies it adversarially, and writes a publication-ready paper.

## Responsible use — please read before running

This is a research instrument, not a submission tool. Outputs are **drafts** that require substantial human review, editing, and verification before they become your work. The pipeline's adversarial gates (math-auditor, novelty-checker, simulated referees) catch a great deal, but they are not a substitute for your own judgment as a researcher.

**Submission requires prior written notice.** Per [`LICENSE`](LICENSE) §2, any submission of pipeline-produced or pipeline-derived work to a peer-reviewed journal, preprint server (arXiv, SSRN, etc.), conference, or thesis committee requires prior written notice to **contact@instituteforautomatedresearch.org**, identifying the intended venue and including a copy of the work. If no response within 60 days, you may proceed provided (i) §3 disclosure is satisfied, (ii) §4 watermark is intact, and (iii) the notice was sent in good faith to a working address. This is a license condition, not a courtesy — submitting without notice is a material breach.

**AI-disclosure is required.** Per [`LICENSE`](LICENSE) §3, submitted work must disclose that this software was used in its production, in the form required by the venue's AI policy (or in the acknowledgments section if the venue has none). The copyright holder may waive disclosure case-by-case in writing; silence is not a waiver, and waivers do not transfer to third parties or attach to derivative works. **Keep any waiver you receive** — you bear the burden of producing the written waiver upon request, and failure to produce it is treated as conclusive evidence that no waiver was granted.

**Outputs are watermarked.** PDFs produced by this pipeline carry a non-cosmetic provenance watermark. Detection methodology is shared privately with journal editors on request. Removing, modifying, or obfuscating the watermark terminates the license automatically (§4).

**Cost.** Recommended path: a **max subscription tier** of Claude Code, Codex, or Gemini CLI (≈$200/month) supports roughly **100 papers/month**, which works out to ~**$2 per paper effective** — see the companion paper for benchmarks. Pay-per-token API access is also supported but is **substantially more expensive** (order ~$2,000 per paper at current rates), because the pipeline burns large token volumes across many subagent dispatches. Subscription is the path designed for academic use; pay-per-token is for users with credits to burn or strict per-call control needs.

**Commercial use is prohibited** without a separate written license (§5). Ordinary academic use by individual researchers, students, and non-profit institutions is unrestricted (subject to §2–§4).

By cloning, running, or distributing this repository you accept the terms in [`LICENSE`](LICENSE).

## Easiest setup (no git or CLI knowledge needed)

If you already have Claude Code installed, open it in any empty folder and paste this in:

```
Set up an autonomous finance research project in this folder.

1. Clone https://github.com/alejandroll10/zeropaper into a temp location
2. From there, run ./setup.sh my-paper --variant finance
   (or --variant finance --ext empirical if I want CRSP/Compustat data)
3. Move the resulting my-paper/ folder here
4. Check that I have the prerequisites installed (python3, uv, git; bubblewrap on Linux).
   If anything is missing, walk me through installing it on my machine (Mac or Linux).
5. When setup is done, tell me to cd into my-paper and say "Run the pipeline."
```

Claude Code will handle the clone, setup, and prereq checks for you. Works on Mac and Linux.

## How it works

1. You clone this template repo once
2. You run `setup.sh` to create a new project — each run creates an independent project folder with its own git repo
3. You open the project folder in Claude Code, Codex, or Gemini CLI and say "Run the pipeline"
4. The pipeline runs autonomously: problem discovery → idea generation → theory development → math verification → paper writing → referee simulation


## Prerequisites

```bash
# System packages
#   Linux (Ubuntu/Debian):
sudo apt-get install python3 python3-pip git bubblewrap
#   macOS (Homebrew): sandbox is built-in via Seatbelt — no bubblewrap needed
brew install python git

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Claude Code
npm install -g @anthropic-ai/claude-code

# Codex
npm install -g @openai/codex

# Gemini CLI
npm install -g @google/gemini-cli
```

## Quick start

### Step 1: Clone this template (once)

```bash
git clone https://github.com/alejandroll10/zeropaper.git
cd zeropaper
```

### Step 2: Create a project

```bash
# Pure finance theory (default)
./setup.sh my-paper

# Finance theory + empirical analysis (CRSP, Compustat, FRED, etc.)
./setup.sh my-paper --variant finance --ext empirical

# Macro theory
./setup.sh my-paper --variant macro

# Finance theory + LLM experiments
./setup.sh my-paper --variant finance --ext theory_llm

# Combine extensions
./setup.sh my-paper --variant finance --ext empirical --ext theory_llm

# Seeded idea (creates output/seed/ — drop your files there before launching)
./setup.sh my-paper --seed

# Manual mode (research toolkit — no autonomous pipeline, you drive the agents)
./setup.sh my-toolkit --manual

# Light mode (use sonnet for all subagents — cheaper/faster)
./setup.sh my-paper --light

# Combine flags
./setup.sh my-paper --variant finance --ext empirical --seed --light
```

This creates `my-paper/` with everything assembled and ready — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, agents for all three runtimes, skills, and pipeline state. The folder is a standalone git repo detached from this template.

You can create as many projects as you want from the same template.

### Step 3: Configure credentials (if using extensions)

```bash
cd my-paper
# Edit .env with your API keys (created by setup.sh)
nano .env
```

| Extension | Credentials needed |
|-----------|-------------------|
| `--ext empirical` | `FRED_API_KEY` (free, from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)), `WRDS_USER` + `WRDS_PASS` (from [WRDS](https://wrds-www.wharton.upenn.edu/)) |
| `--ext theory_llm` | `UF_API_KEY` (from [UF NaviGator](https://api.ai.it.ufl.edu)) |

### Step 4: Launch

Claude Code:

```bash
cd my-paper
claude --dangerously-skip-permissions
```

Codex:

```bash
cd my-paper
codex --sandbox danger-full-access --ask-for-approval never
```

Gemini CLI:

```bash
cd my-paper
gemini --yolo
```

Then say: **"Run the pipeline."**

That's it. Claude Code reads `CLAUDE.md`; Codex reads `AGENTS.md`; Gemini reads `GEMINI.md`. In any runtime, the pipeline checks its state and runs autonomously from there. If the session ends mid-pipeline, relaunch the runtime and say "Run the pipeline" — it picks up where it left off.

## Watch progress

Open a second terminal:

```bash
cd my-paper
python3 -m http.server 8000
```

Open `http://localhost:8000/dashboard.html`. It auto-refreshes every 5 seconds showing current stage, scores, gate results, and event history.

You can also watch files appear in real time in your editor, or run `git log --oneline` to see the commit history (the pipeline commits at stage transitions and gate decisions).

## Variants

| Variant | Flag | Target journals | What it does |
|---------|------|-----------------|-------------|
| **finance** | `--variant finance` (default) | JF, JFE, RFS | Pure finance theory paper |
| **macro** | `--variant macro` | AER, Econometrica, QJE, JPE, ReStud, JME | Macro theory paper |

## Extensions

| Extension | Flag | What it adds |
|-----------|------|-------------|
| **empirical** | `--ext empirical` | Stage 3a: empirical analysis with real data (CRSP, Compustat, FRED, Ken French, Chen-Zimmerman, WRDS) |
| **theory_llm** | `--ext theory_llm` | Stage 3b: test predictions via LLM experiments using gpt-oss models (UF NaviGator) |

Extensions are additive and combinable — they inject extra agents and skills without changing the core pipeline. Use multiple `--ext` flags to combine them.

## Additional flags

| Flag | What it does |
|------|-------------|
| `--seed` | Create a seeded-idea project. Creates `output/seed/` — drop your idea files there (markdown, PDFs, drafts, etc.) before launching. Pipeline triages seed maturity and enters at the appropriate stage. Never silently abandons the seeded idea. |
| `--manual` | Set up the same agents and skills as a research toolkit — no autonomous pipeline. The runtime doc lists every agent and skill with a one-line description; you invoke them yourself. Useful when you want the math-auditor, novelty-checker, theory-explorer, paper-writer, polish-* agents, etc. as standalone helpers without committing to the end-to-end loop. Mutually exclusive with `--seed`. **Paths are fixed**: agents read from `paper/main.tex`, `paper/sections/*.tex`, `output/`, `references/`. **Bringing your own paper:** (1) existing paper as its own git repo → drop the whole repo into `paper/` and add a bare `paper/` line to `.gitignore` so the outer git ignores the nested repo entirely (the existing `paper/*.aux`/`paper/*.pdf`/etc. lines become harmless once `paper/` is excluded); (2) flat `.tex` files → drop them into `paper/sections/` + `paper/main.tex`, the default `.gitignore` handles them; (3) no paper yet → launch `paper-writer` to create one from scratch. |
| `--light` | Use sonnet for all subagents (cheaper/faster). The orchestrator model is unchanged. Good for drafts or iteration. |

These flags combine freely with `--variant` and `--ext` (except `--manual` and `--seed`).

## Pipeline stages

```
Stage 0: Problem Discovery   → Gate 0: Problem Viability
Stage 1: Idea Generation     → Gate 1: Idea Review (iterates)
                                Gate 1b: Novelty Check on idea
                                Gate 1c: Idea Prototype (tractability)
Stage 2: Theory Development  → Gate 2: Math Audit (structured + free-form)
                                Gate 3: Novelty Check on theory
                                Stage 2b: Theory Exploration (compute, verify, plot)
                                Gate 3a-feasibility: Empirical Feasibility (optional)
Stage 3: Implications
Stage 3a: Full Empirical Analysis (optional, if --ext empirical)
Stage 3b: LLM Experiments         (optional, if --ext theory_llm)
Stage 4: Self-Attack          → Gate 4: Scorer Decision
Stage 5: Paper Writing
Stage 6: Referee Simulation   → Gate 5: Referee Decision
Stage 7: Style Check
Stage 8: Bibliography Verify
Stage 9: Polish               → Done (six parallel polish agents — consistency,
                                 formula, numerics, institutions, equilibria,
                                 bibliography — triaged + applied; max 2 rounds)
```

Each gate is adversarial. Failed theories get revised, reworked, or abandoned. The system loops until it produces a paper that passes simulated referee review.

## Agents

| Agent | Role |
|-------|------|
| `literature-scout` | Web search for papers, builds literature map |
| `idea-generator` | Brainstorms candidate mechanisms |
| `idea-reviewer` | Evaluates and ranks idea sketches |
| `idea-prototyper` | Quick math feasibility check before full theory |
| `theory-generator` | Develops selected idea into full model with proofs |
| `math-auditor` | Step-by-step derivation verification |
| `math-auditor-freeform` | Skeptical reader audit |
| `novelty-checker` | Web search to verify result is genuinely new |
| `theory-explorer` | Computational verification — calibration, parameter space, plots |
| `self-attacker` | Finds every possible weakness |
| `scorer` | Quality gate: advance/revise/abandon decisions |
| `paper-writer` | Assembles LaTeX paper |
| `referee` | Simulates top-journal R1 review |
| `style` | Enforces writing style guide |
| `polish-consistency` | Cross-section contradictions, label/object mismatches, headings vs. text |
| `polish-formula` | Re-derives every numbered equation in the rendered paper (codex-math + sympy) |
| `polish-numerics` | Recomputes every numerical claim from stated parameters |
| `polish-institutions` | Verifies real-world claims and faithful characterization of cited papers |
| `polish-equilibria` | Catches multiple equilibria, missing LLN/continuum assumptions, reduced-form/structural bridges |
| `polish-bibliography` | Per-citation prose-claim verification via OpenAlex |
| `bib-verifier` | Verifies cite-key validity against OpenAlex |
| `scribe` | Background documentation of the process |
| `empiricist` | Empirical analysis (if `--ext empirical`) |
| `empirics-auditor` | Verifies empirical code and results (if `--ext empirical`) |
| `experiment-designer` | Designs and runs LLM experiments (if `--ext theory_llm`) |
| `experiment-reviewer` | Verifies experiment design and results (if `--ext theory_llm`) |

## Core skills

| Skill | Runtime | Purpose |
|-------|---------|---------|
| `codex-math` | Claude + Codex | OpenAI Codex (gpt-5.4) for proof verification, proof writing, derivation checking, and conjecture exploration |

## Data skills (with `--ext empirical`)

| Skill | Source | Auth |
|-------|--------|------|
| `edgar` | SEC EDGAR filings, statements, and full-text filing search | None (identity header required) |
| `flex-mining` | Flexible empirical spec and robustness workflow support | None |
| `fred` | FRED — 800K+ macro/financial time series | API key (free) |
| `ken-french` | Ken French Data Library — factor returns, portfolios | None |
| `chen-zimmerman` | Open Source Asset Pricing — 200+ anomaly signals | None |
| `mutual-funds` | Mutual fund holdings and fund-level empirical workflows | None |
| `wrds` | WRDS — CRSP, Compustat, IBES, options, insider trading | Username + password |

## Project structure (after setup)

```
my-paper/
├── CLAUDE.md                 # Claude Code orchestration (assembled by setup.sh)
├── AGENTS.md                 # Codex orchestration (assembled by setup.sh)
├── GEMINI.md                 # Gemini CLI orchestration (assembled by setup.sh)
├── .env                      # API keys (gitignored)
├── dashboard.html            # Live progress dashboard
├── .claude/
│   ├── settings.json         # Sandbox config
│   ├── agents/               # Claude subagents (.md)
│   └── skills/               # Claude skills
├── .codex/
│   └── agents/               # Codex custom agents (.toml)
├── .gemini/
│   ├── settings.json         # Gemini config
│   └── agents/               # Gemini subagents (.md)
├── .agents/
│   └── skills/               # Shared skills (Codex + Gemini)
├── output/                   # Pipeline outputs by stage
├── paper/                    # LaTeX paper
│   ├── main.tex
│   ├── sections/
│   └── referee_reports/
├── code/
│   ├── analysis/             # Analysis and verification scripts
│   ├── download/             # Data download helpers
│   ├── explore/              # Exploration scripts and diagnostics
│   ├── tmp/                  # Scratch files
│   └── utils/                # Utility scripts (including codex-math; more with extensions)
└── process_log/
    ├── pipeline_state.json   # Current stage, scores, history
    └── history.md
```

## Runtime notes

- Claude Code: `claude --dangerously-skip-permissions`
- Codex: `codex --sandbox danger-full-access --ask-for-approval never`
- Gemini CLI: `gemini --yolo`
- All runtimes read the same pipeline state and produce identical artifacts — you can switch runtimes mid-pipeline.

## Safety

Sandbox is pre-configured in `.claude/settings.json`:
- Bash restricted to project folder only
- Cannot read SSH keys or AWS credentials
- WebSearch and WebFetch work freely (for literature search)
- `bubblewrap` enforces restrictions at OS level

## License

Released under the **Auto Research Pipeline — Research Use License v1**. See [`LICENSE`](LICENSE) for full terms.

Summary (non-binding — the LICENSE text controls):

- **Free for non-commercial research and education.** Use, modify, fork, redistribute &mdash; provided this license travels with the work (see Share-alike below).
- **Submission requires prior written notice** to contact@instituteforautomatedresearch.org (§2). 60-day fallback if no response.
- **AI-disclosure required** on submitted work (§3); waivable case-by-case in writing.
- **Watermark must be preserved** — removal terminates the license (§4).
- **No commercial use** without a separate license (§5). Ordinary academic use is exempt from the §5 prohibition but remains subject to §2–§4.
- **Share-alike**: derivative works inherit this same license verbatim (§6) and **may not be relicensed under any other license**, including open-source or permissive licenses.

For licensing inquiries: contact@instituteforautomatedresearch.org
