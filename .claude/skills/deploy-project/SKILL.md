---
name: deploy-project
description: Deploy a new research paper project from this template repo with setup.sh — every flag (--variant, --ext, --mode, --seed, --faithful, --manual, --light, --halt-on-core-bypass), their compositions and mutual exclusions, plus post-setup launch instructions (launch.sh, tmux, unattended runs) and WRDS server startup. Use whenever the user asks to create/set up/start/deploy a new research project, asks which setup.sh flags to pass, asks how to launch or resume a deployed pipeline, or asks about the WRDS socket server.
---

# Deploying a project

If a user asks to create/set up/start a new research project, run `setup.sh` for them.

For editing the template repo itself — adding a variant, a mode, an agent, a skill, or a
vocab placeholder — load the `edit-pipeline` skill instead.

> **`--local` is a debug flag, never a real run.** It skips the git clone, dumps assembled output into `test_output/{variant}/` for inspection, and **exits before** the production steps (dependency install, origin detach, initial commit, cleanup). Use it *only* to verify template assembly (placeholder resolution, agent/skill files, marker stripping) — typically against a `/tmp` target. A full, deployable run is the plain `./setup.sh <project-name> ...` form **without** `--local`. The `--local` form appears only in the template repo's own "Adding a new variant" / "Adding a new mode" procedures (the `edit-pipeline` skill), because those are assembly tests, not paper runs.

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

## Variants, extensions, modes

The authoritative tables live in **CLAUDE.md** ("Supported variants" / "Supported extensions" /
"Supported modes") and are deliberately not duplicated here — CLAUDE.md is always in context,
so a second copy would only drift. This skill carries the per-flag *semantics*; CLAUDE.md
carries the roster and status.

Legacy aliases: `--variant finance_llm` is shorthand for `--variant finance --ext theory_llm`; `--theory-llm` adds the `theory_llm` extension without touching `--variant`.

## Flag semantics

### `--manual`

Mutually exclusive with `--seed` and `--faithful`. It assembles `core_manual.md` instead of `core.md`, auto-generates an agent/skill catalog from the metadata files, swaps in per-runtime `session_manual.md` files, and skips creating `process_log/pipeline_state.json`, the `output/stage*` subdirs, and `dashboard.html`. Pipeline-only agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`) are still assembled into `.claude/agents/` etc. but flagged `pipeline_only: true` in metadata so `scripts/generate_catalog.py` hides them from the user-facing catalog.

### `--mode empirical-first`

Flips the pipeline from theory-first to identification-first for empirical papers whose contribution is a causal estimate rather than a theorem. Finance-only in v1 (macro requires identification tooling — see [issue #18](https://github.com/alejandroll10/zeropaper/issues/18)); auto-implies `--ext empirical` (the empirical agents and skills are mandatory for this mode). The flag composes with `--seed` and `--faithful` (a seeded empirical idea or a faithful identification contract is coherent) and with `--light`; it is independent of `--manual` (which skips the autonomous pipeline entirely). Concretely: Stage 1 produces `output/stage1/identification_design.md` as a first-class artifact (the identification-designer fires at Stage 1 Step 4, before any mechanism work); Stage 2 produces a prose + DAG + ≤2 reduced-form posits mechanism document (no derivations, no theorems); Gate 2's math audit (`math-auditor` + freeform) is replaced by a lightweight plan-time **mechanism-plausibility gate** (`mechanism-auditor`, #82) — there are no derivations to re-check, but a prose+DAG channel can still fail to deliver the documented sign/magnitude, contradict the identification design, or leave the leading alternative un-ruled-out, and catching that at plan time costs one read instead of a Stage-6 re-execution; Stage 2b (theory exploration) is permanently skipped because mechanism mode has no equilibria to grid-search; the scorer's H3 hard requirement swaps from "math audit passed" to "identification audit passed AND empirics audit passed"; Stage 3 derives auxiliary predictions (heterogeneity, falsification, alternative-channel discriminators) rather than the headline causal estimate (already committed in Stage 1); evaluator vocab (scorer, referee, self-attacker, empirics-auditor, referee-mechanism) is recalibrated for the identification-first framing via `templates/agents/finance_modes/empirical_first/vocab.json` and body overrides under `templates/agent_bodies/shared_modes/empirical_first/`. The deployed runtime doc's H1 title becomes "Autonomous Empirical Paper Pipeline" to reflect the route; the body's PAPER_TYPE / DOMAIN_AREAS placeholders are also mode-substituted (grep `DOC_SUBTITLE=` in `setup.sh`). An optional `--ext theory` for post-results structural-model support is deferred to v2 — see [issue #26](https://github.com/alejandroll10/zeropaper/issues/26).

### `--mode report`

Reframes the project as refereeing an external submission. User drops the paper in `submission/`; the orchestrator runs a triage step, fans out all audit agents (`math-auditor` + freeform, `polish-{formula,numerics,consistency,equilibria,identification,prose,bibliography,institutions}`, `bib-verifier`, `novelty-checker`, `self-attacker`, `referee` / `referee-freeform` / `referee-mechanism`) in parallel against the submission, then `report-synthesizer` aggregates `audits/*.md` into `report/referee_report.md` with a single verdict (Accept / Minor revision / Major revision / Reject). One-shot, no stages, no `pipeline_state.json`, no `dashboard.html`. Mutually exclusive with `--seed`, `--faithful`, `--manual`, `--mode empirical-first`. Composes with `--light`.

Composes with `--ext empirical` and `--ext theory_llm` in **install-only** mode: the extension's *skills* install (WRDS/FRED/Census/SEC helpers, the LLM-experiment client) so the audit agents can spot-check external data or call an LLM if needed, but the extensions' *audit agents* (`empirics-auditor`, `identification-auditor`, `mechanism-auditor`, `headline-replicator`, `data-integrity-auditor`, `data-selection-auditor`, `method-checker`, `claim-{enumerator,grounder,verifier}`, `experiment-reviewer`) are pruned — they were designed against the pipeline's own empiricist output and would need substantial rewrites for external submissions. The base referees evaluate empirical submissions holistically (identification, magnitude, robustness at editorial level); deep code-level adversarial auditing of external empirical submissions is a v2 feature.

Pruned at assembly time via `prune_report_mode_agents` in `setup.sh`, by category: generative agents (`theory-generator`, `paper-writer`, `idea-*`, `question-poser`, `question-referee`, `theory-explorer`, `implications-deriver`), the `last-resort` escalation agent (one-shot report mode has no stuck pipeline to unstick), pipeline-management agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`, `editor`), scoring agents (`scorer`, `scorer-freeform`), broad-survey agents (`literature-scout`, `gap-scout`), the `style` editor, and extension generative agents (`empiricist`, `identification-designer`, `experiment-designer`). (`faithful-drift-auditor` is also absent from a report build, but via a different mechanism — `prune_non_faithful_agents`, which drops it from any non-`--faithful` build; report mode simply can't be faithful.) For the exact current set — it changes as agents are added — grep the `prune_report_mode_agents` call sites in `setup.sh` rather than trusting this list.

`--mode report` also carries its own vocab, body, and metadata overlays like any mode: `templates/agents/{variant}_modes/report/vocab.json`; `templates/agent_bodies/shared_modes/report/{referee-core,referee-freeform,referee-mechanism,polish-identification}.md` re-aim the referees and the identification audit at an external submission (polish-identification audits the submission's *own stated design* — its pipeline body would otherwise N/A on every report run for lack of a pipeline design artifact); report-native `description` overrides in the agent metadata (`"modes": {"report": ...}`); and `templates/shared/report_mode_inject.md`, appended to the 12 remaining pipeline-native audit agents so prompt-passed `submission/` + `audits/` paths win over their bodies' pipeline paths, with an explicit degraded-check note on PDF-only submissions.

H1 subtitle becomes "Autonomous Referee Report Pipeline".

### `--faithful`

A stricter variant of `--seed`; pass one or the other, not both, and not alongside `--manual` (also mutually exclusive). The flag implies `--seed`'s folder structure (creates `output/seed/`, starts at `seed_triage`) but supersedes its semantics with the faithful contract. At seed_triage the orchestrator extracts `output/seed/mechanism_contract.md` (the seed's named mechanism, structural invariants, theorem-statement constraints, identification strategy, stated contribution); developing agents must respect every invariant. Substitution / pivot / headline-replacement are forbidden; additions on top of the faithfully-implemented contract (extra theorems, comparative statics, robustness checks) are encouraged. Genuine impossibilities get documented in `output/seed/limitations.md` and the paper ships documenting them honestly. Agents marked `category: evaluator` in their metadata stay impartial and receive no contract pointer — corrupting the evaluation signal corrupts the paper. The developing/evaluator split is derived from that metadata field at assembly time (`scripts/list_agents_by_category.py`), not from a hardcoded list; run that script for current membership. The faithful constraint enters at the orchestrator's routing of evaluator verdicts (per `templates/shared/faithful.md`) and via a static "read `mechanism_contract.md` first" pointer appended to each developing agent body. A `process_log/pivot_log.md` is seeded for auditing every potentially-mechanism-affecting routing decision.

UNDER `--faithful` THE SEED FREEZES INTO A CONTRACT AT STEP 0, SO SPECIFY THE SETUP (MODEL CLASS, STRUCTURAL INVARIANTS, THEOREM-STATEMENT CONSTRAINTS) AND NEVER THE RESULT — DERIVING RESULTS IS WHAT THE PIPELINE IS FOR.

### `--halt-on-core-bypass`

(issue #51) Guards against silent degradation when a **core** (binding source, verification gate, or designated agent/step) is bypassed: default is record-and-surface (agent pointer → `process_log/degradation_ledger.md`, verdict marked NON-BINDING; nothing added to the runtime doc), and the flag adds a halt (`status = "halted_core_bypass"`). See `docs/core_bypass.md` (the deployed doctrine); wiring lives in `inject_core_bypass_into_agents` (setup.sh) and the `{{CORE_BYPASS_GUARD}}` placeholder in `core.md`.

## After setup

Setup creates a standalone project folder with assembled CLAUDE.md, AGENTS.md, GEMINI.md, agents for all runtimes, and skills. Tell the user to:

1. `cd <project-name>`
2. Edit `.env` with any required API keys (FRED, WRDS, etc.)
3. Launch a runtime with the deployed launcher: `./launch.sh claude` / `./launch.sh codex` / `./launch.sh gemini` / `./launch.sh grok` (add `--tmux` to wrap in a detached tmux window). The script activates the project venv (`.venv/`, created by `setup.sh`, gitignored — bare `python3` resolves to it and every agent Bash subshell inherits it) and applies each runtime's correct flags. **`./launch.sh codex` is a headless driver loop, not a TUI**: codex has no autowake (verified: a parent whose turn ended is never woken by a completing child, native `spawn_agent` included), so an interactive codex session stalls at every turn-end; the driver re-prompts via `codex exec resume` until `pipeline_state.json` says `complete`/`halted_*`, making turn-ends harmless. `./launch.sh codex --once` gives a plain interactive TUI when you want one. Manual equivalent of the codex sandbox posture (run from the project root; the `$(pwd)/.git` writable root is load-bearing — codex hard-codes each root's top-level `.git` read-only, so without it every pipeline `git commit` dies on `index.lock`): `codex --sandbox workspace-write --ask-for-approval never -c 'sandbox_workspace_write.network_access=true' -c "sandbox_workspace_write.writable_roots=[\"~/.codex\",\"~/.cache\",\"~/Library/Caches\",\"~/.matplotlib\",\"$(pwd)/.git\"]"`.
4. Say "Run the pipeline." (interactive runtimes; the codex driver sends it itself)

### Long unattended runs

**codex** is already headless-safe via the driver loop — `./launch.sh codex --tmux` is the complete unattended form.

For **Claude**, launch each project in its own **interactive** `tmux` window (e.g. `tmux new-window -c <project-name> 'source .venv/bin/activate && claude --dangerously-skip-permissions'`, then send "Run the pipeline." to it) so it keeps driving the orchestrator turn-after-turn and survives detach — do **not** use headless `claude -p "Run the pipeline."`, which terminates at the ~600s background-task wait ceiling while a subagent is still running. The orchestrator resumes from `process_log/pipeline_state.json` + committed `output/` artifacts, so a fresh interactive session picks up where an interrupted run left off.

## WRDS server (only with `--ext empirical`)

The empirical extension talks to WRDS through a long-running local socket server (port 23847) so the Duo 2FA push happens once per session, not per query. The pipeline's data-inventory step starts it automatically (`templates/runtime/claude/session.md` runs `code/utils/start_services.sh` before Stage 0), but you can also start it manually:

```bash
cd <project-name>
bash code/utils/start_services.sh   # idempotent; reuses an existing server if one is up
```

The server is per-host, not per-project — once it's running, every project that has the WRDS skill reuses it. If you are working in the template repo itself (no `.env`, no `code/utils/`), `cd` into any existing deployed empirical project on this host and run `bash code/utils/start_services.sh` from there; the resulting server will serve the template's future deployments too.

To check if it's already running on this machine:

```bash
lsof -iTCP:23847 -sTCP:LISTEN                                           # is anything listening? (Linux: ss -tlnp | grep 23847)
PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; print(wrds_ping())"
```

`True` from the ping means it's healthy.
