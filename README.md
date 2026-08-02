# Auto AI Research Template

Autonomous research paper generator. Set up a project, launch Claude Code, Codex, or Gemini CLI, walk away. The system discovers a problem, generates a theory, verifies it adversarially, and writes a publication-ready paper.

## Responsible use — please read before running

This is a research instrument, not a submission tool. Outputs are **drafts** that require substantial human review, editing, and verification before they become your work. The pipeline's adversarial gates (math-auditor, novelty-checker, simulated referees) catch a great deal, but they are not a substitute for your own judgment as a researcher.

**Submission requires prior written notice.** Per [`LICENSE`](LICENSE) §2, any submission of pipeline-produced or pipeline-derived work to a peer-reviewed journal, preprint server (arXiv, SSRN, etc.), conference, or thesis committee requires prior written notice to **contact@instituteforautomatedresearch.org**, identifying the intended venue and including a copy of the work. If no response within 60 days, you may proceed provided (i) §3 disclosure is satisfied, (ii) §4 watermark is intact, and (iii) the notice was sent in good faith to a working address. This is a license condition, not a courtesy — submitting without notice is a material breach.

**AI-disclosure is required.** Per [`LICENSE`](LICENSE) §3, submitted work must disclose that this software was used in its production, in the form required by the venue's AI policy (or in the acknowledgments section if the venue has none). The copyright holder may waive disclosure case-by-case in writing; silence is not a waiver, and waivers do not transfer to third parties or attach to derivative works. **Keep any waiver you receive** — you bear the burden of producing the written waiver upon request, and failure to produce it is treated as conclusive evidence that no waiver was granted.

**Manual-mode output is exempt from the notice and disclosure duties.** Per [`LICENSE`](LICENSE) §2 (Assisted Output exemption), work produced with a `--manual` (research toolkit) deployment where *you* directed the research — problem selection, step sequencing, accept/revise decisions — with the agents as discrete assistive tools is **Assisted Output**: no §2 notice, no §3 disclosure (your venue's own AI policy still applies). The exemption is defined by conduct, not by the flag — running the staged pipeline end-to-end inside a manual deployment produces Pipeline Output regardless. Assisted Output stays fully subject to the watermark (§4) and commercial-use (§5) terms; its watermark carries `mode=manual`.

**Outputs are watermarked.** PDFs produced by this software carry a non-cosmetic provenance watermark that encodes, among other things, the deployment mode (`autonomous` vs `manual`), so pipeline-generated and toolkit-assisted papers are distinguishable. Detection methodology is shared privately with journal editors on request. Removing, modifying, or obfuscating the watermark terminates the license automatically (§4) — in every mode, including manual.

**Cost.** Recommended path: a **max subscription tier** of Claude Code, Codex, or Gemini CLI (≈$200/month) supports roughly **100 papers/month**, which works out to ~**$2 per paper effective** — see the [companion paper](https://instituteforautomatedresearch.org/papers/iar-m/iar-m-001) for benchmarks. Pay-per-token API access is also supported but is **substantially more expensive** (order ~$2,000 per paper at current rates), because the pipeline burns large token volumes across many subagent dispatches. Subscription is the path designed for academic use; pay-per-token is for users with credits to burn or strict per-call control needs.

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

# Git identity (one-time, used by every setup.sh run)
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
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

# Empirical-first finance: causal-identification paper (mechanism written
# as prose+DAG, not theorem; identification design is the primary Stage 1
# deliverable). Auto-implies --ext empirical.
./setup.sh my-paper --variant finance --mode empirical-first

# Macro theory
./setup.sh my-paper --variant macro

# Finance theory + LLM experiments
./setup.sh my-paper --variant finance --ext theory_llm

# Combine extensions
./setup.sh my-paper --variant finance --ext empirical --ext theory_llm

# Seeded idea (creates output/seed/ — drop your files there before launching)
./setup.sh my-paper --seed

# Faithful mode (stricter --seed: implement the seed as a contract)
./setup.sh my-paper --faithful

# Manual mode (research toolkit — no autonomous pipeline, you drive the agents)
./setup.sh my-toolkit --manual

# Light mode (cheapest tier for all subagents — cheaper/faster)
./setup.sh my-paper --light

# Combine flags
./setup.sh my-paper --variant finance --ext empirical --seed --light
```

This creates `my-paper/` with everything assembled and ready — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, agents for all three runtimes, skills, and pipeline state. The folder is a standalone git repo detached from this template.

You can create as many projects as you want from the same template.

### Step 3: Configure credentials

```bash
cd my-paper
# setup.sh puts a .env here — copied from the template repo's own .env if you
# have one, otherwise scaffolded from .env.example with every key blank.
nano .env
```

Set this one for **every** variant, extensions or not:

| Credential | Why |
|------------|-----|
| `OPENALEX_API_KEY` | Free, no card — make an account at [openalex.org](https://openalex.org), then copy the key from [openalex.org/settings/api](https://openalex.org/settings/api). Every variant leans on OpenAlex for literature search, novelty checks, and bibliography verification. It bills a **daily credit budget**: a key gives you 10,000 credits/day *per key*, while going keyless drops you to a 1,000/day demo tier **shared by every process on the host**. A title search costs 10 credits and a DOI lookup is free, so a keyless machine gets ~100 searches/day total — which concurrent pipelines exhaust quickly, and the resulting 429s persist until 00:00 UTC. |

Then, per extension:

| Extension | Credentials needed |
|-----------|-------------------|
| `--ext empirical` | `FRED_API_KEY` (free, from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)), `WRDS_USER` + `WRDS_PASS` (from [WRDS](https://wrds-www.wharton.upenn.edu/)), `CENSUS_API_KEY` (free, from [Census](https://api.census.gov/data/key_signup.html) — **required** for any ACS/CPS call; the keyless tier was retired), `SEC_EDGAR_NAME` + `SEC_EDGAR_EMAIL` (no registration; SEC requires a real identity in the User-Agent). Optional: `BLS_API_KEY` (free, raises the daily cap — keyless still works) |
| `--ext theory_llm` | `UF_API_KEY` (from [UF NaviGator](https://api.ai.it.ufl.edu)); `DEEPINFRA_TOKEN` for cross-family replication. Or run against a self-hosted model with no key at all: set `LOCAL_LLM_MODEL` (+ `LOCAL_LLM_BASE_URL`, defaults to Ollama's) |

`EMAIL` identifies your API traffic to OpenAlex and Crossref (the `mailto` parameter) — worth setting regardless. Note that **no identity value reaches the manuscript**: papers ship `\author{[Author names withheld for double-blind review]}` and the pipeline is forbidden to de-anonymize them.

To add a key to projects you already deployed, put it in this repo's `.env` and run `./update.sh <project>`; the merge appends keys the project is missing without touching values it already has.

### Step 4: Launch

Activate the project venv first (created by `setup.sh`; holds all Python deps) so the pipeline's `python3` resolves to it — every agent subshell inherits the activated environment.

Claude Code:

```bash
cd my-paper
source .venv/bin/activate && claude --dangerously-skip-permissions
```

Codex:

```bash
cd my-paper
./launch.sh codex        # headless driver loop — the autonomous way to run codex
./launch.sh codex --once # plain interactive TUI, if you want a single session
```

`./launch.sh codex` is a **driver loop**, not a TUI: codex has no autowake, so an
interactive codex session stalls whenever the model ends its turn between stages.
The driver re-prompts the same session (`codex exec resume`) until
`pipeline_state.json` reports `complete` or `halted_*`, with a stuck-model cost
guard. It applies the full sandbox posture automatically, including the
`$(pwd)/.git` writable root that pipeline `git commit`s require (codex hard-codes
each root's top-level `.git` as read-only; listing `.git` as its own root
sidesteps the carve-out — verified on codex-cli 0.144.1). Manual equivalent:

```bash
source .venv/bin/activate && codex --sandbox workspace-write --ask-for-approval never \
  -c 'sandbox_workspace_write.network_access=true' \
  -c "sandbox_workspace_write.writable_roots=[\"~/.codex\",\"~/.cache\",\"~/Library/Caches\",\"~/.matplotlib\",\"$(pwd)/.git\"]"
```

Gemini CLI:

```bash
cd my-paper
source .venv/bin/activate && gemini --yolo
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
| **llm_cognition** | `--variant llm_cognition` | NeurIPS, ICML, ICLR (TMLR as field tier) | The science of LLM cognition & evaluation. Auto-implies `--ext theory_llm` (the experiments are the evidence); `--ext empirical` and `--mode report` are gated off (see LIMITATIONS.md) |

## Extensions

| Extension | Flag | What it adds |
|-----------|------|-------------|
| **empirical** | `--ext empirical` | Stage 3a: empirical analysis with real data (CRSP, Compustat, FRED, Ken French, Chen-Zimmerman, WRDS) |
| **theory_llm** | `--ext theory_llm` | Stage 3b: test predictions via LLM experiments using gpt-oss models (UF NaviGator) |

Extensions are additive and combinable — they inject extra agents and skills without changing the core pipeline. Use multiple `--ext` flags to combine them.

## Modes

Modes flip the pipeline architecture. Orthogonal to `--variant` and `--ext`.

| Mode | Flag | What it does |
|------|------|-------------|
| **empirical-first** | `--mode empirical-first` | Causal-identification empirical paper. The identification design becomes the primary Stage 1 deliverable (not a Stage 3a check). The mechanism section is prose + DAG + ≤2 reduced-form posits — no theorem-and-proof. Gate 2 (math audit) and Stage 2b (theory exploration) are skipped because mechanism mode has no derivations or equilibria to audit. Scorer's H3 hard requirement swaps from "math audit passed" to "identification + empirics audits passed." Auto-implies `--ext empirical`. Finance variant only in v1 (macro requires identification tooling — see [issue #18](https://github.com/alejandroll10/zeropaper/issues/18)). |

If `identification-designer` returns `N/A — no causal claim` at Stage 1 (the question is irreducibly non-causal), the pipeline halts with `status = halted_no_identification_design` and prompts the operator to rerun `update.sh --no-mode` to convert the deployment back to theory-first. After the update, the operator must also reset `current_stage` in `process_log/pipeline_state.json` (to `"stage_1"` to re-pick the idea, or `"stage_2"` if the selected idea is still valid in theory-first) and flip `status` back to `"running"` before relaunching — leaving `current_stage = "stage_1_identification_design"` in place would point the resume logic at a stage doc that no longer exists in the converted deployment. The full procedure is in the runtime's halted-status handler.

## Additional flags

| Flag | What it does |
|------|-------------|
| `--seed` | Create a seeded-idea project. Creates `output/seed/` — drop your idea files there (markdown, PDFs, drafts, etc.) before launching. Pipeline triages seed maturity and enters at the appropriate stage. Never silently abandons the seeded idea, but **may** pivot under puzzle-triage / refine framing under scorer recommendations. |
| `--faithful` | Stricter variant of `--seed`. Treats the seed as a **contract**. At seed_triage the orchestrator extracts `output/seed/mechanism_contract.md` (the seed's named mechanism, structural invariants, theorem-statement constraints, identification strategy, stated contribution); developing agents must respect every invariant. Substitution / pivot / headline-replacement are forbidden — additions on top of the faithfully-implemented contract (extra theorems, comparative statics, robustness checks) are allowed and encouraged once the contract is in place. Genuine impossibilities (proof unrepairable, identification infeasible, prediction contradicted by data) get documented in `output/seed/limitations.md` and the paper ships documenting them honestly. Evaluators (scorers, referees, auditors) stay impartial — the constraint enters only at the orchestrator's routing of their verdicts, with every routing decision logged to `process_log/pivot_log.md` for auditability. Use `--faithful` when you want the seed implemented as written; use `--seed` when you want the pipeline to preserve the seed but allow puzzle-triage pivots and scorer-driven framing refinements. Mutually exclusive with `--seed` and `--manual`. |
| `--manual` | Set up the same agents and skills as a research toolkit — no autonomous pipeline. The runtime doc lists every agent and skill with a one-line description; you invoke them yourself. Useful when you want the math-auditor, novelty-checker, theory-explorer, paper-writer, polish-* agents, etc. as standalone helpers without committing to the end-to-end loop. Mutually exclusive with `--seed` and `--faithful`. **Paths are fixed**: agents read from `paper/main.tex`, `paper/sections/*.tex`, `output/`, `references/`. **Bringing your own paper:** (1) existing paper as its own git repo → drop the whole repo into `paper/` and add a bare `paper/` line to `.gitignore` so the outer git ignores the nested repo entirely (the existing `paper/*.aux`/`paper/*.pdf`/etc. lines become harmless once `paper/` is excluded); (2) flat `.tex` files → drop them into `paper/sections/` + `paper/main.tex`, the default `.gitignore` handles them; (3) no paper yet → launch `paper-writer` to create one from scratch. **License note:** human-directed manual-mode work is *Assisted Output* — exempt from the §2 submission notice and §3 disclosure (LICENSE §2, Assisted Output exemption; your venue's own AI policy still applies). The watermark still installs (`mode=manual`) and §4 applies in full. |
| `--light` | Run the whole pipeline on the cheapest tier its runtime offers (cheaper/faster) — **orchestrator included**, and each agent's pinned reasoning effort dropped with it. Applies to all four runtimes through their own tier tables — claude `sonnet`, codex `gpt-5.6-luna`, gemini `gemini-3-flash-preview`; grok has a single model, so it is already a no-op there. Subagents are pinned at assembly time; `launch.sh` pins the orchestrator at launch. Good for drafts or iteration — but note the orchestrator makes the stage-routing and gate decisions, so this is the setting where a cheaper model costs the most. |

These flags combine freely with `--variant` and `--ext` (except `--manual` and `--seed`/`--faithful`, which are mutually exclusive).

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
Stage 9: Polish               → Done (eight parallel polish agents — consistency,
                                 formula, numerics, institutions, equilibria,
                                 identification, bibliography, prose — triaged
                                 + applied; max 2 rounds)
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
| `polish-equilibria` | Catches multiple equilibria, missing LLN/continuum assumptions, reduced-form/structural bridges (theory papers) |
| `polish-identification` | Audits identification-coherence in the rendered paper: estimand-vs-claim, diagnostics-vs-design, cluster level, identification.tex faithfulness, heterogeneity-population coherence (empirical papers) |
| `polish-bibliography` | Per-citation prose-claim verification via OpenAlex |
| `polish-prose` | Prose economy: repeated caveats, hedge stacking, abstract bloat, defensive contribution framing |
| `bib-verifier` | Verifies cite-key validity against OpenAlex |
| `scribe` | Background documentation of the process |
| `empiricist` | Empirical analysis (if `--ext empirical`) |
| `empirics-auditor` | Verifies empirical code and results (if `--ext empirical`) |
| `experiment-designer` | Designs and runs LLM experiments (if `--ext theory_llm`) |
| `experiment-reviewer` | Verifies experiment design and results (if `--ext theory_llm`) |

## Core skills

| Skill | Runtime | Purpose |
|-------|---------|---------|
| `codex-math` | Claude + Codex | OpenAI Codex (gpt-5.6-sol) for proof verification, proof writing, derivation checking, and conjecture exploration |

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
│   └── simulated_referee_reports/
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

- Preferred: `./launch.sh <claude|codex|gemini|grok>` — activates the venv and applies each runtime's correct flags (`--tmux` wraps in a detached tmux window)
- Claude Code: `claude --dangerously-skip-permissions`
- Codex: `./launch.sh codex` runs the headless driver loop (codex has no autowake; an interactive TUI stalls at every turn-end). Manual posture: `codex --sandbox workspace-write --ask-for-approval never -c 'sandbox_workspace_write.network_access=true' -c "sandbox_workspace_write.writable_roots=[\"~/.codex\",\"~/.cache\",\"~/Library/Caches\",\"~/.matplotlib\",\"$(pwd)/.git\"]"` (write-confined to the project; run from the project root — the `$(pwd)/.git` root is required for pipeline commits; see Safety)
- Gemini CLI: `gemini --yolo`
- All runtimes read the same pipeline state and produce identical artifacts — you can switch runtimes mid-pipeline.

## Safety

**Claude** — sandbox pre-configured in `.claude/settings.json`:
- Bash restricted to the project folder (writes/deletes outside the project blocked)
- Cannot read SSH keys or AWS credentials
- WebSearch and WebFetch work freely (for literature search)
- `bubblewrap` (Linux) / Seatbelt (macOS) enforces restrictions at the OS level

**Codex** — launched under `--sandbox workspace-write` (see Runtime notes): the orchestrator and every sub-agent worker are **write-confined** to the project plus a few cache roots (`~/.codex`, `~/.cache`, `~/Library/Caches`, `~/.matplotlib`), with network egress on. Writes/deletes outside the project are blocked. Unlike Claude, codex's native sandbox confines only *writes* — it does **not** block *reads* of `~/.ssh`/`~/.aws` (documented gap, `LIMITATIONS.md` / #186). Codex-math workers run the same posture with network off.

**Grok** — launched under `grok --sandbox pipeline --always-approve --leader-socket "$(pwd)/.grok/leader.sock"` (a per-project `.grok/sandbox.toml` profile extending grok's built-in `workspace`): writes/deletes outside the project are blocked, network egress and WRDS loopback stay on, and the caches (`~/.codex`, `~/.cache`, `~/Library/Caches`, `~/.matplotlib`) remain writable. Grok's kernel `deny` list blocks reads *and* writes, so it goes one better than codex — `~/.ssh`/`~/.aws` are also unreadable. Enforced by Seatbelt (macOS) / Landlock (Linux) at the OS level. The **per-project `--leader-socket`** is required whenever you run more than one grok project on a host (the recommended one-tmux-window-per-project layout): every grok client shares `~/.grok/leader.sock` by default, and a second client connecting to that socket **tears down the first session's in-flight turn**. Pointing each project at its own `.grok/leader.sock` isolates the leaders so concurrent projects don't cancel each other — `./launch.sh grok` passes it automatically.

Two further grok-sandbox consequences (issue #190) — the launcher fixes the first and warns about the second (whose fix is a one-time opt-in script): **(1) venv PATH demotion** — grok's bash tool rebuilds PATH with the macOS defaults ahead of inherited entries, so the activated `.venv` lands below `/usr/bin` and bare `python3` resolves to the system interpreter (no `sympy`, no `wrds`). `./launch.sh grok` installs transparent `VIRTUAL_ENV`-keyed shims (`python3`/`python`/`pip3`/`pip`) into `~/.local/bin`, which grok keeps ahead of `/usr/bin`; the shims are inert outside grok (no active venv → they exec the next real binary on PATH) and are never installed over a pre-existing non-shim file. **(2) `git push` cannot use the macOS keychain** — the `osxkeychain` helper needs `mach-lookup com.apple.SecurityServer`, which grok's sandbox schema (filesystem+network only) cannot grant, so pushes to an HTTPS remote fail on auth while local commits succeed. To enable pushes, run `bash code/utils/setup_push_token.sh` once per project: it stores a **fine-grained PAT scoped to that project's backup repo** in `.git/push-credentials` (untracked, 0600) and switches the repo to a local credential store — the narrowest blast radius (a compromised agent can reach only that one repo's token, never the keychain). Without it, runs proceed normally but stay local-only.

**Gemini** — currently launches unconfined (`--yolo`); filesystem-confinement parity is tracked in #186.

## License

Released under the **Auto Research Pipeline — Research Use License v1.1**. See [`LICENSE`](LICENSE) for full terms.

Summary (non-binding — the LICENSE text controls):

- **Free for non-commercial research and education.** Use, modify, fork, redistribute &mdash; provided this license travels with the work (see Share-alike below).
- **Submission requires prior written notice** to contact@instituteforautomatedresearch.org (§2). 60-day fallback if no response.
- **AI-disclosure required** on submitted work (§3); waivable case-by-case in writing.
- **Assisted Output is exempt from §2/§3**: human-directed work from a `--manual` toolkit deployment needs no notice or disclosure (§2, Assisted Output exemption) — defined by conduct, not the flag; §4 and §5 still apply.
- **Watermark must be preserved** — removal terminates the license (§4). Applies to all modes, including manual.
- **No commercial use** without a separate license (§5). Ordinary academic use is exempt from the §5 prohibition but remains subject to §2–§4.
- **Share-alike**: derivative works inherit this same license verbatim (§6) and **may not be relicensed under any other license**, including open-source or permissive licenses.

For licensing inquiries: contact@instituteforautomatedresearch.org

## Citation

If you use this software in research, please cite the companion paper:

> Lopez-Lira, Alejandro. *ZeroPaper: An Autonomous Research System.* IAR Methodology Papers No. IAR-M-001, Institute for Automated Research, May 2026. https://instituteforautomatedresearch.org/papers/iar-m/iar-m-001 — doi:[10.5281/zenodo.20127843](https://doi.org/10.5281/zenodo.20127843)

```bibtex
@techreport{lopezlira2026zeropaper,
  author      = {Lopez-Lira, Alejandro},
  title       = {{ZeroPaper: An Autonomous Research System}},
  institution = {Institute for Automated Research},
  type        = {IAR Methodology Papers},
  number      = {IAR-M-001},
  year        = {2026},
  month       = {5},
  doi         = {10.5281/zenodo.20127843},
  url         = {https://instituteforautomatedresearch.org/papers/iar-m/iar-m-001}
}
```
