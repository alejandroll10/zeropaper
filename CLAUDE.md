# CLAUDE.md — Meta Project: Pipeline Template Development

AFTER EVERY BIG CHANGE, LAUNCH A SONNET AGENT TO REVIEW YOUR CHANGES FOR ISSUES. IF ANY ISSUES ARE FOUND, ADD A NEW ROUND OF AUDITING AFTER FIXING THE CURRENT ROUND'S ISSUES (EVEN IF THERE ARE ONLY MINOR CHANGES). ITERATE UNTIL DONE.

WHEN ADDING A NEW INFRASTRUCTURE PATH TO `setup.sh` (DIR OR FILE THAT GETS DEPLOYED), ALSO ADD IT TO THE `candidate_dirs` / `candidate_files` LIST IN THE MANIFEST EMISSION BLOCK (`setup.sh:1184`); OTHERWISE `update.sh` WILL SILENTLY SKIP IT WHEN REFRESHING EXISTING DEPLOYMENTS.

WHEN ADDING A NEW `{{KEY}}` PLACEHOLDER TO ANY AGENT BODY (SHARED, VARIANT, OR EXTENSION), ADD A DEFAULT VALUE FOR THE KEY TO EVERY EXISTING VARIANT vocab.json (`templates/agents/{finance,macro}/vocab.json` AT MINIMUM). THE LOADER (`scripts/agent_body_loader.py`) RAISES `KeyError` ON UNRESOLVED PLACEHOLDERS, SO A MISSING DEFAULT BREAKS ASSEMBLY FOR ANY VARIANT THAT DOESN'T DEFINE THE KEY — FAIL-LOUD IS THE CORRECT BEHAVIOR, BUT IT MEANS A VARIANT-ONLY EDIT WILL BREAK SETUP FOR THE OTHER VARIANTS UNTIL THE KEY IS BACKFILLED. EXTENSION-AGENT PLACEHOLDERS HAVE THE SAME RULE — ANY NEW KEY IN AN EXTENSION BODY MUST APPEAR IN EVERY VARIANT VOCAB THE EXTENSION CAN COMPOSE WITH (CURRENTLY BOTH FINANCE AND MACRO).

## What this is

This is the **template repository** for the autonomous research paper pipeline. We are building and iterating on the pipeline infrastructure itself — agents, setup scripts, CLAUDE.md templates, dashboard, etc.

This file is tracked in git but **overwritten by `setup.sh`** in cloned projects. It is for our development work only. The pipeline's CLAUDE.md that end users see is assembled by `setup.sh` from `templates/shared/core.md` + `templates/runtime/claude/session.md` + per-variant vocab substitution. (Variant-specific scorer calibrations live in `templates/agents/{variant}/vocab.json` and are substituted into the scorer agent body, not appended as a separate block.)

## Sibling repo: the IAR website + wiki

The pipeline's empirical dataset skills (`templates/skill_bodies/empirical/<dataset>.md`, mirrored into `extensions/empirical/skills/<dataset>/SKILL.md`) and the IAR wiki dataset pages (`src/content/docs/datasets/*` in `github.com/institute-for-automated-research/website`) are two mirrors of the same dataset knowledge, kept in sync both ways. When a change here affects a wiki page or a published paper PDF/landing page (dataset access or gotchas, citation format, provenance disclosure), file the issue **in the website repo** (`gh issue create --repo institute-for-automated-research/website`), not here. The website repo's CLAUDE.md carries the reciprocal rule for changes that originate there.

## Working principle: no unsolved or undocumented architectural limits

When auditing or editing the pipeline, if a known architectural limit is identified (e.g., a self-referential check, a subjective rule, an enforcement gap, a missing producer for a consumed artifact), do not leave it acknowledged-and-moved-on. Either (a) solve it in the same pass, or (b) document it explicitly — in the relevant agent body, doc file, or a dedicated `LIMITATIONS.md` — with the failure mode it can produce and what would be needed to close it. Acknowledged-but-undocumented limits accumulate silently and produce surprises in future runs.

## Working principle: no complexity budget — do what is best for the pipeline

There is no complexity budget, no edit-cost ceiling, no "this change is too big" threshold. The pipeline is designed to be run millions of times; any one-time cost of editing the template — updating three runtime assemblers, reshaping `pipeline_state.json`, rewriting the escalation table, expanding the orchestrator prompt, adding agents, writing new tests — is trivially amortized against that. Do not reject or water down a structural proposal because it is expensive to *implement*; reject it only if it is worse for the pipeline on the merits.

Concretely:
- If a change makes the pipeline produce better papers, do it — even if it touches every runtime, rewrites state, and requires new agents.
- Do not propose a "narrower variant" to save implementation effort. Propose the narrower variant only if it is genuinely better for the output.
- Do not invoke "complexity cost," "maintenance burden," or "surface area" as reasons to decline. These are real for a one-shot project; here they are rounding errors against millions of runs.
- The only legitimate reasons to decline a structural proposal are: it makes the output worse, it introduces a correctness/safety regression, or a strictly better alternative exists on the merits.

## Setting up a new project

If a user asks to create/set up/start a new research project, run `setup.sh` for them:

```bash
# Basic finance theory
./setup.sh <project-name> --variant finance

# Finance theory + empirical data (CRSP, Compustat, FRED, WRDS)
./setup.sh <project-name> --variant finance --ext empirical

# Empirical-first finance (causal-identification paper). The identification
# design becomes the primary Stage 1 deliverable; Stage 2 writes a prose+DAG
# mechanism (no theorem-and-proof structural model); math-auditor is skipped.
# Auto-implies --ext empirical. Finance variant only in v1.
./setup.sh <project-name> --variant finance --mode empirical-first

# Macro theory
./setup.sh <project-name> --variant macro

# Finance theory + LLM experiments
./setup.sh <project-name> --variant finance --ext theory_llm

# Combine extensions
./setup.sh <project-name> --variant finance --ext empirical --ext theory_llm

# Light mode (sonnet for all subagents — cheaper/faster, orchestrator unchanged)
./setup.sh <project-name> --variant finance --light

# Halt-on-core-bypass (issue #51): make a silently-bypassed core a hard stop, not
# a fallback. Composes with any variant/extension/mode/seed/faithful/light.
./setup.sh <project-name> --variant finance --halt-on-core-bypass

# Seeded idea (creates output/seed/ — drop your files there before launching)
./setup.sh <project-name> --variant finance --seed

# Seeded idea + empirical
./setup.sh <project-name> --variant finance --seed --ext empirical

# Faithful mode (stricter --seed: implement the seed as a contract)
./setup.sh <project-name> --variant finance --faithful

# Faithful + empirical
./setup.sh <project-name> --variant finance --faithful --ext empirical

# Manual mode (research toolkit — agents and skills only, no autonomous pipeline)
./setup.sh <project-name> --variant finance --manual

# Manual mode + empirical extension
./setup.sh <project-name> --variant finance --manual --ext empirical

# Report mode (referee an external submission instead of generating one)
./setup.sh <project-name> --variant finance --mode report
./setup.sh <project-name> --variant macro --mode report
./setup.sh <project-name> --variant finance --mode report --ext empirical
```

`--manual` is mutually exclusive with `--seed` and `--faithful`. It assembles `core_manual.md` instead of `core.md`, auto-generates an agent/skill catalog from the metadata files, swaps in per-runtime `session_manual.md` files, and skips creating `process_log/pipeline_state.json`, the `output/stage*` subdirs, and `dashboard.html`. Pipeline-only agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`) are still assembled into `.claude/agents/` etc. but flagged `pipeline_only: true` in metadata so `scripts/generate_catalog.py` hides them from the user-facing catalog.

`--mode empirical-first` flips the pipeline from theory-first to identification-first for empirical papers whose contribution is a causal estimate rather than a theorem. Finance-only in v1 (macro requires identification tooling — see [issue #18](https://github.com/alejandroll10/zeropaper/issues/18)); auto-implies `--ext empirical` (the empirical agents and skills are mandatory for this mode). The flag composes with `--seed` and `--faithful` (a seeded empirical idea or a faithful identification contract is coherent) and with `--light`; it is independent of `--manual` (which skips the autonomous pipeline entirely). Concretely: Stage 1 produces `output/stage1/identification_design.md` as a first-class artifact (the identification-designer fires at Stage 1 Step 4, before any mechanism work); Stage 2 produces a prose + DAG + ≤2 reduced-form posits mechanism document (no derivations, no theorems); Gate 2 (math audit) and Stage 2b (theory exploration) are permanently skipped because mechanism mode has no derivations or equilibria to audit; the scorer's H3 hard requirement swaps from "math audit passed" to "identification audit passed AND empirics audit passed"; Stage 3 derives auxiliary predictions (heterogeneity, falsification, alternative-channel discriminators) rather than the headline causal estimate (already committed in Stage 1); evaluator vocab (scorer, referee, self-attacker, empirics-auditor, referee-mechanism) is recalibrated for the identification-first framing via `templates/agents/finance_modes/empirical_first/vocab.json` and body overrides under `templates/agent_bodies/shared_modes/empirical_first/`. The deployed runtime doc's H1 title becomes "Autonomous Empirical Paper Pipeline" to reflect the route; the body's PAPER_TYPE / DOMAIN_AREAS placeholders are also mode-substituted (`setup.sh:168-186`). An optional `--ext theory` for post-results structural-model support is deferred to v2 — see [issue #26](https://github.com/alejandroll10/zeropaper/issues/26).

`--faithful` is a stricter variant of `--seed`; pass one or the other, not both, and not alongside `--manual` (also mutually exclusive). The flag implies `--seed`'s folder structure (creates `output/seed/`, starts at `seed_triage`) but supersedes its semantics with the faithful contract. At seed_triage the orchestrator extracts `output/seed/mechanism_contract.md` (the seed's named mechanism, structural invariants, theorem-statement constraints, identification strategy, stated contribution); developing agents must respect every invariant. Substitution / pivot / headline-replacement are forbidden; additions on top of the faithfully-implemented contract (extra theorems, comparative statics, robustness checks) are encouraged. Genuine impossibilities get documented in `output/seed/limitations.md` and the paper ships documenting them honestly. Evaluators (scorer, scorer-freeform, math-auditor, math-auditor-freeform, novelty-checker, referee, referee-freeform, referee-mechanism, self-attacker, idea-prototyper, idea-reviewer, branch-manager, plus the extension evaluators empirics-auditor, identification-auditor under `--ext empirical` and experiment-reviewer under `--ext theory_llm`) stay impartial — corrupting the evaluation signal corrupts the paper. The faithful constraint enters at the orchestrator's routing of evaluator verdicts (per `templates/shared/faithful.md`) and via a static "read `mechanism_contract.md` first" pointer appended to each developing agent body. A `process_log/pivot_log.md` is seeded for auditing every potentially-mechanism-affecting routing decision.

`--halt-on-core-bypass` (issue #51) guards against silent degradation when a **core** (binding source, verification gate, or designated agent/step) is bypassed: default is record-and-surface (agent pointer → `process_log/degradation_ledger.md`, verdict marked NON-BINDING; nothing added to the runtime doc), and the flag adds a halt (`status = "halted_core_bypass"`). See `docs/core_bypass.md` (the deployed doctrine); wiring lives in `inject_core_bypass_into_agents` (setup.sh) and the `{{CORE_BYPASS_GUARD}}` placeholder in `core.md`.

This creates a standalone project folder with assembled CLAUDE.md, AGENTS.md, GEMINI.md, agents for all runtimes, and skills. After setup, tell the user to:

1. `cd <project-name>`
2. Edit `.env` with any required API keys (FRED, WRDS, etc.)
3. Launch any runtime: `claude --dangerously-skip-permissions` / `codex --sandbox danger-full-access --ask-for-approval never` / `gemini --yolo`
4. Say "Run the pipeline."

### WRDS server (only with `--ext empirical`)

The empirical extension talks to WRDS through a long-running local socket server (port 23847) so the Duo 2FA push happens once per session, not per query. The pipeline's data-inventory step starts it automatically (`templates/runtime/claude/session.md` runs `code/utils/start_services.sh` before Stage 0), but you can also start it manually:

```bash
cd <project-name>
bash code/utils/start_services.sh   # idempotent; reuses an existing server if one is up
```

The server is per-host, not per-project — once it's running, every project that has the WRDS skill reuses it. If you are working in the template repo itself (no `.env`, no `code/utils/`), `cd` into any existing deployed empirical project on this host and run `bash code/utils/start_services.sh` from there; the resulting server will serve the template's future deployments too.

To check if it's already running on this machine:

```bash
ss -tlnp | grep 23847                                                  # is anything listening?
PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; print(wrds_ping())"
```

`True` from the ping means it's healthy.

## Repository structure

```
templates/
├── shared/
│   ├── core.md              # Runtime-agnostic pipeline orchestrator template
│   ├── core_manual.md       # Slim manual-mode runtime doc (no pipeline, just catalogs)
│   ├── seed.md              # Seeded-idea override block (injected when --seed is used)
│   ├── faithful.md          # Stricter seeded-mode block (injected when --faithful is used)
│   ├── faithful_inject.md   # Short pointer appended to developing-agent bodies under --faithful
│   ├── seed_overrides/      # Per-stage overrides for --seed (gate doc placeholders)
│   └── faithful_overrides/  # Per-stage overrides for --faithful (supersedes seed_overrides)
├── runtime/
│   ├── claude/
│   │   ├── session.md           # Claude-specific session guidance (autonomous mode)
│   │   └── session_manual.md    # Claude-specific session guidance (manual mode)
│   ├── codex/
│   │   ├── session.md           # Codex orchestration discipline (autonomous mode)
│   │   └── session_manual.md    # Codex toolkit guidance (manual mode)
│   └── gemini/
│       ├── session.md           # Gemini orchestration discipline (autonomous mode)
│       └── session_manual.md    # Gemini toolkit guidance (manual mode)
├── agent_metadata/          # JSON metadata for agent assembly (tools, model, description)
│   ├── claude_shared_agents.json
│   ├── claude_finance_agents.json
│   └── claude_macro_agents.json
├── agent_bodies/            # Shared/extension agent prompt bodies (plain markdown)
│   └── shared/              # Domain-agnostic shared agent prompts
├── skill_metadata/          # JSON metadata for skill assembly
│   ├── codex_math_skills.json
│   ├── empirical_skills.json
│   └── theory_llm_skills.json
├── skill_bodies/            # Skill prompt bodies (plain markdown)
│   ├── codex_math/
│   ├── empirical/
│   └── theory_llm/
├── utils/                   # Utility scripts copied into deployed projects
│   └── codex_math/          # Codex proof verification/writing/exploration scripts
├── agents/                  # Variant agent prompt bodies (source of truth; no frontmatter)
│   ├── shared/
│   ├── finance/
│   └── macro/
└── gitignore_project        # .gitignore template for deployed projects

scripts/
├── assemble_claude_agents.py   # Combines agent metadata + bodies → .claude/agents/*.md
├── assemble_claude_skills.py   # Combines skill metadata + skill bodies → .claude/skills/*/SKILL.md
├── assemble_codex_skills.py    # Combines skill metadata + skill bodies → .agents/skills/*/SKILL.md
├── assemble_codex_subagents.py # Combines agent metadata + bodies → .codex/agents/*.toml
├── assemble_gemini_agents.py   # Combines agent metadata + bodies → .gemini/agents/*.md
└── generate_catalog.py         # Manual mode: emits agent/skill catalog markdown from metadata

extensions/                  # Optional extensions (empirical, theory_llm)
├── empirical/
│   ├── agent_metadata/      # shared_agents.json, finance_agents.json, macro_agents.json
│   ├── agent_bodies/        # shared/, finance/, macro/
│   └── utils/               # Python/shell utilities copied into project
└── theory_llm/
    ├── agent_metadata/      # agents.json
    ├── agent_bodies/        # Agent prompt bodies
    └── llm_client.py        # LLM client copied into project

setup.sh                     # Clones repo, assembles CLAUDE.md + AGENTS.md + GEMINI.md + agents + skills
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

## Supported modes

| Mode | Flag | Status | Variants | Notes |
|------|------|--------|----------|-------|
| `empirical-first` | `--mode empirical-first` | Working (v1) | `finance` | Auto-implies `--ext empirical`. Stage 1's identification design is the primary deliverable; Stage 2 produces a prose+DAG mechanism (no theorems); Gate 2 / Stage 2b skipped; scorer H3 = identification+empirics audits; H1 subtitle becomes "Autonomous Empirical Paper Pipeline". Optional `--ext theory` for post-results structural support deferred to v2 ([#26](https://github.com/alejandroll10/zeropaper/issues/26)).
| `report` | `--mode report` | Working (v1) | `finance`, `macro` | Reframes the project as refereeing an external submission. User drops the paper in `submission/`; the orchestrator runs a triage step, fans out all audit agents (`math-auditor` + freeform, `polish-{formula,numerics,consistency,equilibria,identification,prose,bibliography,institutions}`, `bib-verifier`, `novelty-checker`, `self-attacker`, `referee` / `referee-freeform` / `referee-mechanism`) in parallel against the submission, then `report-synthesizer` aggregates `audits/*.md` into `report/referee_report.md` with a single verdict (Accept / Minor revision / Major revision / Reject). One-shot, no stages, no `pipeline_state.json`, no `dashboard.html`. Mutually exclusive with `--seed`, `--faithful`, `--manual`, `--mode empirical-first`. Composes with `--light`. Composes with `--ext empirical` and `--ext theory_llm` in **install-only** mode: the extension's *skills* install (WRDS/FRED/Census/SEC helpers, OpenAlex, LLM-experiment client) so the audit agents can spot-check external data or call an LLM if needed, but the extensions' *audit agents* (`empirics-auditor`, `identification-auditor`, `data-integrity-auditor`, `data-selection-auditor`, `method-checker`, `claim-{enumerator,grounder,verifier}`, `experiment-reviewer`) are pruned — they were designed against the pipeline's own empiricist output and would need substantial rewrites for external submissions. The base referees evaluate empirical submissions holistically (identification, magnitude, robustness at editorial level); deep code-level adversarial auditing of external empirical submissions is a v2 feature. Generative agents (`theory-generator`, `paper-writer`, `idea-*`, `theory-explorer`), the `last-resort` escalation agent (one-shot report mode has no stuck pipeline to unstick), pipeline-management agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`, `editor`), scoring agents (`scorer`, `scorer-freeform`), broad-survey agents (`literature-scout`, `gap-scout`), the `style` editor, `faithful-drift-auditor`, and extension generative agents (`empiricist`, `identification-designer`, `experiment-designer`) are pruned at assembly time via `prune_report_mode_agents` in `setup.sh`. H1 subtitle becomes "Autonomous Referee Report Pipeline".

## Core skills (all variants)

| Skill | Description |
|-------|-------------|
| `codex-math` | OpenAI Codex (gpt-5.5) for proof verification, writing, and exploration. Erratic genius — substantial false-positive rate, always triage. Scripts at `code/utils/codex_math/`. |

## How setup.sh works

1. Clones this repo into a new project folder
2. Reads `--variant` flag (default: `finance`)
3. Assembles runtime docs (CLAUDE.md, AGENTS.md, GEMINI.md):
   - Reads `templates/shared/core.md` (runtime-agnostic orchestrator)
   - Injects runtime-specific session guidance from `templates/runtime/{runtime}/session.md`
   - Substitutes per-variant scorer calibrations from `templates/agents/{variant}/vocab.json` into the scorer agent body
   - If `--seed`: injects `templates/shared/seed.md` as `{{SEED_OVERRIDE}}`
   - If `--faithful`: injects `templates/shared/faithful.md` instead (supersedes seed.md at the same placeholder)
   - Replaces `{{PAPER_TYPE}}`, `{{TARGET_JOURNALS}}`, `{{DOMAIN_AREAS}}`, `{{RUNTIME_DOC_NAME}}`, `{{AGENT_DIR}}`, `{{SKILL_DIR}}`
4. Assembles agents from metadata + prompt bodies:
   - Shared: `agent_metadata/claude_shared_agents.json` + `agent_bodies/shared/*.md`
   - Variant: `agent_metadata/claude_{variant}_agents.json` + `agents/{variant}/*.md`
   - Claude agents → `.claude/agents/*.md`, Codex → `.codex/agents/*.toml`, Gemini → `.gemini/agents/*.md`
5. Injects variant context (paper type, journal list, domain) into key agents
   - If `--faithful`: also appends `templates/shared/faithful_inject.md` (a short "read `output/seed/mechanism_contract.md` first" pointer) to *developing* agent bodies only — theory-generator, idea-generator, paper-writer, polish-* (all 8: prose, consistency, equilibria, formula, numerics, institutions, bibliography, identification), bib-verifier, last-resort (categorized `developing` precisely so a fix it proposes for a stuck artifact respects the contract), plus extension developers (empiricist, identification-designer under `--ext empirical`; experiment-designer under `--ext theory_llm`). Evaluators (scorer, scorer-freeform, math-auditor, math-auditor-freeform, novelty-checker, referee, referee-freeform, referee-mechanism, self-attacker, idea-prototyper, idea-reviewer, branch-manager, plus extension evaluators empirics-auditor, identification-auditor, experiment-reviewer) explicitly do **not** receive the pointer — corrupting the evaluation signal corrupts the paper.
6. Creates project structure (output/, paper/, code/, etc.) and initial pipeline state
   - If `--seed`: creates `output/seed/` with a README, sets `pipeline_state.json` to start at `seed_triage` with `"seeded": true, "faithful": false`
   - If `--faithful`: creates `output/seed/` with a faithful-mode README, sets `pipeline_state.json` to start at `seed_triage` with `"seeded": true, "faithful": true`, and seeds `process_log/pivot_log.md` with a header + table skeleton for auditing routing decisions
7. Installs core Python deps (sympy, matplotlib) via `uv pip install`
8. Assembles core skills:
   - Claude skills into `.claude/skills/`
   - Codex/Gemini skills into `.agents/skills/` (shared)
   - Copies utility scripts to `code/utils/`
9. Applies extensions (`--ext empirical`, `--ext theory_llm`):
   - Assembles extension agents for all three runtimes
   - Assembles extension skills from shared skill metadata + bodies
   - Copies utilities, creates dirs, appends API keys to `.env`
10. Removes template infrastructure, detaches from origin, commits initial state

## Adding a new variant

1. Create agent metadata: `templates/agent_metadata/claude_{variant}_agents.json`
2. Create agent bodies: `templates/agents/{variant}/` with markdown prompts
3. Create `templates/agents/{variant}/vocab.json` with the per-variant vocabulary keys (scorer calibrations, importance/novelty/surprise rubrics, mechanism term, referee role, etc.) — see `templates/agents/finance/vocab.json` for the full set.
4. Add variant config to `setup.sh` (paper type, target journals, journal list, domain areas)
5. Test: `./setup.sh --variant {variant} --local`

## Adding a new mode

A *mode* re-frames the pipeline's orchestration (theory-first → identification-first, or another orientation) without forking a variant. It is layered on top of `--variant {finance|macro|...}` via two overlay mechanisms: a vocab overlay (mode-specific overrides to variant vocab keys) and a body overlay (mode-specific shared-agent bodies that replace the base shared body for that mode). The `empirical-first` mode is the reference implementation.

1. **Choose the slug.** Mode flag is `--mode {slug}`; setup.sh lowercases `-` → `_` for directory lookups (`setup.sh:218`). So `--mode foo-bar` looks under `foo_bar/`.
2. **Vocab overlay:** create `templates/agents/{variant}_modes/{mode_slug}/vocab.json` with only the keys whose meaning changes under this mode. Loaded by `setup.sh:220` and layered on top of the base variant vocab — later wins on duplicate keys. Reference: `templates/agents/finance_modes/empirical_first/vocab.json`.
3. **Body overlay (optional):** create `templates/agent_bodies/shared_modes/{mode_slug}/` with per-agent body overrides. Files are named `{agent_id}-core.md` (variant agent overrides) or `{agent_id}.md` (shared agent overrides) — the loader's suffix discrimination at `scripts/agent_body_loader.py:50-95` handles both. Reference: `templates/agent_bodies/shared_modes/empirical_first/{theory-generator-core.md, idea-generator-core.md, idea-prototyper.md, referee-mechanism.md}`.
4. **Stage-doc guards (optional):** add `<!-- {MODE}_FIRST_START -->` / `<!-- {MODE}_FIRST_END -->` markers in `templates/shared/docs/*.md` for content that should activate under this mode. The marker resolver at `setup.sh:1513-1569` strips the markers under the matching mode and removes the whole block otherwise. A complementary `<!-- THEORY_FIRST_START -->` marker exists for content that should *only* render under the no-mode (theory-first) default. Currently only `EMPIRICAL_FIRST` markers are wired into the resolver; adding a new mode's markers means adding a parallel `else if` branch.
5. **Mode-conditional descriptors in setup.sh:** add a `case "$VARIANT"` branch in the `if [ "$MODE" = "{mode}" ]; then` block (around `setup.sh:175-186`) that overrides `PAPER_TYPE`, `DOMAIN_AREAS`, `DOC_SUBTITLE`, and any other variant descriptors the mode reframes.
6. **Validation block in setup.sh:** add the mode to the `case` in the mode-flag validator (~line 117) that decides which `--variant` combinations the mode supports. If the mode implies an extension (as `empirical-first` implies `--ext empirical`), auto-add it with an Info message.
7. **Tests:** `./setup.sh /tmp/test_{mode} --variant {variant} --mode {mode} --local` should resolve cleanly with `✓ All placeholders resolved` and no `{{KEY}}` leakage. Inspect the deployed CLAUDE.md and `.claude/agents/*.md` for marker leakage (`grep -c '{MODE}_FIRST_START'` should be 0).
8. **Document:** add a row to the "Supported modes" table above. If the mode has cross-variant compatibility nuances (auto-implied extensions, mutual exclusions with other flags), document them in a prose paragraph in the "Setting up a new project" section parallel to the `--mode empirical-first` paragraph.

## Architecture: runtime-agnostic core + runtime-specific packaging

The pipeline is split into two layers:

- **Runtime-agnostic**: `templates/shared/core.md` (orchestrator logic, pipeline stages), `templates/agent_bodies/shared/` and `templates/agents/{variant}/` (agent prompts and per-variant vocab including scorer calibrations) — these are the same regardless of runtime.
- **Runtime-specific**: `templates/runtime/{claude,codex,gemini}/session.md` (session guidance per runtime), `templates/agent_metadata/claude_*.json` (shared metadata with per-runtime overrides via `codex` and `gemini` keys), `scripts/assemble_{claude_agents,codex_subagents,gemini_agents}.py`.

Three runtimes share the same core + agent bodies, with runtime-specific packaging.

## Agent classification

Agents are either **shared** (identical across variants) or **variant-specific** (different prompts per domain). Each agent is defined as:
- **Metadata** (`agent_metadata/claude_*.json`): Claude frontmatter plus Codex and Gemini overrides
- **Body** (`agent_bodies/shared/*.md`, `agents/{variant}/*.md`): runtime-agnostic prompt content

**Shared** (domain-agnostic, receive variant context via injection):
- `literature-scout` — broad literature survey (variant context provides target journals)
- `gap-scout` — deep search on a pre-selected gap (adjacent literatures, closest competitor, gap validation)
- `idea-prototyper` — quick math feasibility + surprise check
- `theory-explorer` — computational verification, calibration, parameter exploration, plots
- `math-auditor` — checks derivations step-by-step
- `math-auditor-freeform` — reads as skeptical reader
- `scorer-freeform` — free-form quality assessment at Gate 4 (holistic read, no rubric)
- `referee-freeform` — free-form referee report at Stage 6 (editorial assessment)
- `novelty-checker` — searches web for prior work
- `paper-writer` — writes LaTeX from inputs
- `style` — checks writing style
- `branch-manager` — strategic advisor at Gate 4 + Stage 2 audit loop (every 3rd theory version); diagnoses ceiling/alternatives. Runs on `claude-fable-5` (rare, low-token, high-leverage strategic reasoning)
- `last-resort` — general-purpose escalation agent for stubborn problems; launched at orchestrator discretion (no auto-trigger) when normal escalation is exhausted and the alternative is abandonment. Runs on the stronger `claude-fable-5` model with broad tool access; receives the full failure history; returns `FIX-PROPOSED` (re-verified by the existing gate — never self-certifies) or `GENUINELY-STUCK`. Visible in the manual-mode catalog; pruned in `--mode report`
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
- `data-integrity-auditor` — verifies cached field-content against source (shared, `--ext empirical`)
- `data-selection-auditor` — verifies cached sample against documented inclusion rule (shared, `--ext empirical`)
- `identification-designer` — designs the identification strategy at Stage 1 step 4 (variant-specific, finance only in v1, `--ext empirical`)
- `identification-auditor` — adversarial audit of identification strategy at Stage 3a step 3 (variant-specific, finance only in v1, `--ext empirical`)
- `claim-enumerator` — deterministic regex enumeration of numerical claims in the paper draft → `paper_claims.json` (shared, `--ext empirical`, Stage 5 step 5a)
- `claim-grounder` — LLM-judgment match of every enumerated claim to its empiricist-output source → `paper_source_map.json` (shared, `--ext empirical`, Stage 5 step 5a)
- `claim-verifier` — programmatic file/field/value verification of grounder citations with coverage check → REVISE feeds back to grounder or paper-writer (shared, `--ext empirical`, Stage 5 step 5a)
- `experiment-designer` — LLM experiments (shared, `--ext theory_llm`)
- `experiment-reviewer` — validates experiment methodology (shared, `--ext theory_llm`)
