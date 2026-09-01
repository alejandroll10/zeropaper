---
name: deploy-project
description: Deploy or update a research paper project from this template checkout with setup.sh/update.sh — checkout-local source policy, every setup flag (--variant, --ext, --mode, --seed, --faithful, --manual, --light, --halt-on-core-bypass, --publish, --assemble-only), their compositions and mutual exclusions, update quiescence, safe opt-in GitHub publishing, plus post-setup launch instructions (launch.sh, tmux, unattended runs) and WRDS server startup. Use whenever the user asks to create/set up/start/deploy/update a research project, asks which setup.sh flags to pass, asks how to launch or resume a deployed pipeline, or asks about the WRDS socket server.
---

# Deploying a project

If a user asks to create/set up/start a new research project, run `setup.sh` for them.

For editing the template repo itself — adding a variant, a mode, an agent, a skill, or a
vocab placeholder — load the `edit-pipeline` skill instead.

> **Every setup uses this checkout.** `setup.sh` never fetches or clones the template repository. Check out the desired release tag or commit first, then run its `setup.sh`; a full deployment rejects changes or untracked files in `setup.sh`, `VERSION`, `LICENSE`, `.env.example`, or `deploy_assets/`. `.env` is separate operator configuration and does not dirty the template source.

> **`--assemble-only` is the non-production fast path.** It requires an explicit destination, permits dirty development inputs, assembles and validates the complete output there, and **exits before** dependency provisioning, project Git initialization, the initial commit, or publishing. Use it for template tests and `update.sh`, not for a runnable new project.

> **Publishing is opt-in.** A normal production setup creates and commits a standalone local repository but does not create or push a GitHub repository. Add `--publish` only when the operator deliberately wants setup to create and push a remote repository. `--no-publish` is an explicit spelling of the default for scripts and test runs.

```bash
# Basic finance theory
./setup.sh <project-name> --variant finance

# Basic finance theory + deliberate GitHub publication
./setup.sh <project-name> --variant finance --publish

# Finance theory + empirical data (CRSP, Compustat, FRED, WRDS)
./setup.sh <project-name> --variant finance --ext empirical

# Empirical-first finance (causal-identification paper). The identification
# design becomes the primary Stage 1 deliverable; Stage 2 writes a prose+DAG
# mechanism (no theorem-and-proof structural model); math-auditor is skipped.
# Auto-implies --ext empirical. Finance variant only in v1.
./setup.sh <project-name> --variant finance --mode empirical-first

# Data-first finance (dataset-contribution paper, Chen-Zimmermann genre). The
# deliverable is an open, documented, validated dataset plus a fact portfolio;
# Gate 2 is a spec audit plus a conditional exact-coverage census; coverage
# triangulation is independently verified;
# identification agents are pruned (facts are descriptive by design).
# Auto-implies --ext empirical. Finance variant only in v1. Pairs naturally
# with --seed (a seeded dataset idea is the primary use case).
./setup.sh <project-name> --variant finance --mode data-first --seed

# Macro theory
./setup.sh <project-name> --variant macro

# LLM-cognition science (formal frameworks + benchmarks for language-model
# cognition/evaluation; targets NeurIPS/ICML/ICLR, tier ladder
# nature → top-ml → field → workshop). --ext theory_llm is AUTO-IMPLIED
# (since v2.10.0): the variant's evidence base is LLM experiments, so setup.sh
# adds the extension with an Info message even if the flag is omitted (skipped
# under --mode report, which prunes those agents anyway).
# --ext empirical is gated off for this variant (setup.sh errors with a
# pointer; see the llm_cognition entry in LIMITATIONS.md). --mode report is
# supported since v2.16.0 — the referee fan-out runs ML-calibrated (top-ML
# venue role, conference-cadence verdict semantics).
./setup.sh <project-name> --variant llm_cognition

# Finance theory + LLM experiments
./setup.sh <project-name> --variant finance --ext theory_llm

# Combine extensions
./setup.sh <project-name> --variant finance --ext empirical --ext theory_llm

# Light mode (cheapest tier for all subagents and the orchestrator)
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

# Evidence-first LLM-cognition measurement paper (construct spec + design gate →
# experiments as the evidence core → post-experiment formal characterization).
# llm_cognition-only; theory_llm auto-implied as usual.
./setup.sh <project-name> --variant llm_cognition --mode measurement-first
```

## Updating an existing project

Run the complete attested command printed by setup from the exact
checkout/source snapshot that assembled the deployment:

```bash
./update.sh <project> --source-digest sha256:<trusted-setup-digest> \
  --variant finance --no-mode --clear-ext \
  --no-seeded --no-faithful --no-manual --no-light \
  --no-halt-on-core-bypass
# Add --dry-run without changing the selector declaration.
```

Record that complete command outside the project. Every invocation explicitly
provides its trusted source digest plus all eight resolved canonical selector dimensions:
`--variant`; `--mode`/`--no-mode`; repeated `--ext`/`--clear-ext`; and the
positive or negative forms of seeded, faithful, manual, light, and
halt-on-core-bypass. Setup's command has already expanded implied extensions and
legacy aliases, and its embedded bootstrap authenticates the recorded updater
launcher, locks the project, and verifies a full source snapshot before that
snapshot's coordinator or setup modules execute. Do not simplify it to a
direct `update.sh` invocation or derive/reconstruct it from project-writable files. The updater accepts no in-place
selector change. Any different variant, mode, extension, seed, faithful,
manual, light, or halt-policy choice requires a fresh deployment.

The updater accepts only a complete manifest-backed deployment assembled from
the exact same v2.28.1 source snapshot. Every other version or source snapshot
must stay on its original template or be redeployed fresh; update does not
sniff its shape, create missing mutable state, or migrate historical state.

Before updating, stop every process that may create, delete, rename, or modify files in the
target project, and keep the project quiescent until the update finishes. Supported deployments'
installed `./launch.sh` holds the cooperative lock, so `update.sh` detects and refuses active
launcher sessions automatically. Processes that bypass `launch.sh`—for example
directly started runtimes, scripts, file watchers, cron jobs, or an editor that may save
files—also do not hold the lock and must be stopped manually. An idle editor need not be closed
if it will not write during the update. This is the operational boundary tracked in [issue
#259](https://github.com/alejandroll10/zeropaper/issues/259) and documented in `LIMITATIONS.md`.

Within the supported generation, state must already satisfy the complete receipt-backed contract.
A stale paper receipt is handled by the ordinary Stage-9 re-audit; malformed or
historical state fails before managed replacement. The updater never executes
or mutates the agent-writable project `.venv`, and no selector change is
supported even for an assemble-only or not-yet-launched target.

## Variants, extensions, modes

The authoritative tables live in **CLAUDE.md** ("Supported variants" / "Supported extensions" /
"Supported modes") and are deliberately not duplicated here — CLAUDE.md is always in context,
so a second copy would only drift. This skill carries the per-flag *semantics*; CLAUDE.md
carries the roster and status.

Legacy aliases: `--variant finance_llm` is shorthand for `--variant finance --ext theory_llm`; `--theory-llm` adds the `theory_llm` extension without touching `--variant`.

## Flag semantics

### `--publish` / `--no-publish`

Publishing is **off by default**. `--publish` opts a production deployment into creating and pushing a GitHub repository after the local initial commit; setup prints the exact target before calling GitHub. `--no-publish` explicitly selects the default local-only behavior and is useful in automation where the safety decision should be visible. Passing both is an error, and `--publish` is incompatible with `--assemble-only` because assembly-only builds do not initialize a project repository.

The target defaults to `automated-papers-produced`; override it with `PUBLISH_ORG=<org>`. Visibility defaults to private and can be set with `PUBLISH_VISIBILITY=private|public|internal`. These environment variables configure an explicit `--publish` request—they do not enable publishing by themselves. An empty `PUBLISH_ORG` with `--publish` is an error; without `--publish`, including `PUBLISH_ORG=` has no effect because the deployment remains local.

`--mode report` rejects `--publish`: report deployments can contain someone else's confidential submission. An operator who has reviewed the contents and intentionally wants a remote can push it manually afterward. Missing `gh` authentication, a failed user/membership API lookup, or a confirmed non-active organization membership leaves the committed local repository intact and prints a distinct warning; API failures are not mislabeled as non-membership. A failed `gh repo create --push` also preserves the local commit, but GitHub state may be partial if repository creation succeeded before the remote or push step failed; setup prints the exact URL to inspect before retrying and preserves `gh`'s error output.

### `--manual`

Mutually exclusive with `--seed` and `--faithful`. It assembles `core_manual.md` instead of `core.md`, auto-generates an agent/skill catalog from the metadata files, swaps in per-runtime `session_manual.md` files, and skips creating `process_log/pipeline_state.json`, the `output/stage*` subdirs, and `dashboard.html`. It still creates `process_log/results_registry.json`, `process_log/manual_evidence_state.json`, and `output/evidence/` so manual paper edits use the same computed-evidence and citation checkpoints. Pipeline-only agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`) are still assembled into `.claude/agents/` etc. but flagged `pipeline_only: true` in metadata so `deploy_assets/scripts/generate_catalog.py` hides them from the user-facing catalog.

### `--mode empirical-first`

Flips the pipeline from theory-first to identification-first for empirical papers whose contribution is a causal estimate rather than a theorem. Finance-only in v1 (macro has theory-first identification tooling, but its empirical-first mechanism/vocabulary calibration is not implemented — see [issue #18](https://github.com/alejandroll10/zeropaper/issues/18)); auto-implies `--ext empirical` (the empirical agents and skills are mandatory for this mode). The flag composes with `--seed` and `--faithful` (a seeded empirical idea or a faithful identification contract is coherent) and with `--light`; it is independent of `--manual` (which skips the autonomous pipeline entirely). Concretely: Stage 1 produces `output/stage1/identification_design.md` as a first-class artifact (the identification-designer fires at Stage 1 Step 4, before any mechanism work); Stage 2 produces a prose + DAG + ≤2 reduced-form posits mechanism document (no derivations, no theorems); Gate 2's math audit (`math-auditor` + freeform) is replaced by a lightweight plan-time **mechanism-plausibility gate** (`mechanism-auditor`, #82) — there are no derivations to re-check, but a prose+DAG channel can still fail to deliver the documented sign/magnitude, contradict the identification design, or leave the leading alternative un-ruled-out, and catching that at plan time costs one read instead of a Stage-6 re-execution; Stage 2b (theory exploration) is permanently skipped because mechanism mode has no equilibria to grid-search; the scorer's H3 hard requirement swaps from "math audit passed" to "identification audit passed AND empirics audit passed"; Stage 3 derives auxiliary predictions (heterogeneity, falsification, alternative-channel discriminators) rather than the headline causal estimate (already committed in Stage 1); evaluator vocab (scorer, referee, self-attacker, empirics-auditor, referee-mechanism) is recalibrated for the identification-first framing via `deploy_assets/templates/agents/finance_modes/empirical_first/vocab.json` and body overrides under `deploy_assets/templates/agent_bodies/shared_modes/empirical_first/`. The deployed runtime doc's H1 title becomes "Autonomous Empirical Paper Pipeline" to reflect the route; the body's PAPER_TYPE / DOMAIN_AREAS placeholders are also mode-substituted (grep `DOC_SUBTITLE=` in `deploy_assets/scripts/setup/resolve_config.sh`). An optional `--ext theory` for post-results structural-model support is deferred to v2 — see [issue #26](https://github.com/alejandroll10/zeropaper/issues/26).

### `--mode data-first`

Reframes the pipeline for **dataset-contribution papers** (issue #278): the primary contribution is an open, documented, validated dataset plus a portfolio of documented facts — the Chen & Zimmermann (Review of Finance 2022) genre; other exemplars: Jensen-Kelly-Pedersen, Welch-Goyal, Hoberg-Phillips, Baker-Bloom-Davis. Finance-only in v1 (macro calibration: [issue #279](https://github.com/alejandroll10/zeropaper/issues/279)); auto-implies `--ext empirical` (the empiricist + data auditors are the construction/validation engine). Composes with `--seed` (the primary use case — a seeded dataset idea), `--faithful` (a faithful data-spec contract), and `--light`; independent of `--manual`. Concretely: Stage 1 sketches are **dataset architectures** and the `idea-prototyper` runs a **pilot build** (real slices pulled from each named source); Stage 2's `theory-generator` runs in **dataset-spec mode** and emits both the prose contract and a machine-readable, versioned rights inventory (schema, dating/timestamp conventions, inclusion/reconciliation rules, redistribution classifications and evidence, validation plan, fact-portfolio plan — no theorems). Gate 2 replaces the math audit with a plan-time **dataset-specification audit** (`mechanism-auditor`, PLAUSIBLE/REVISE) that also emits a machine-routed commitment list and classifies exact coverage as REQUIRED/NOT-REQUIRED. REQUIRED finite enumerable commitments trigger the existing `empiricist` in census-only mode: it exhausts every authoritative enumerator through its terminal condition, writes one machine-readable certificate bound to the exact spec/rights digests, reports all gaps together, and blocks acceptance unless every row verifies; a GAPS result mutates at Gate 2 before novelty, portfolio derivation, or Stage 3a, malformed output has a bounded same-version retry/halt, and operational ERROR routes to debugging rather than scope repair. Acceptance is tracked by `dataset_spec_version` plus the conditional certificate path/digest with a Gate-4 staleness hard-block. Stage 2b is permanently skipped; Stage 3 derives the **fact portfolio** (replication targets with expected sign/magnitude, adjudication targets, new-fact candidates, construction-sensitivity checks); Stage 3a becomes **construction + validation** — the identification steps never fire (`identification-designer`/`identification-auditor` are pruned), and a mandatory **coverage-triangulation protocol** (≥2 independent sources per event class, written reconciliation, spec-stated waivers) is independently verified by the **`coverage-auditor`**, which re-enumerates the live universe and compares certificate/live/build key sets when a certificate exists, routing build omissions to a fresh build and source drift to Gate 2. Its PASS is an H3 leg alongside the empirics/integrity/selection audits and headline replication. The public dataset is not an output of that networked analysis run: a paired, credential-free offline producer receives only declared inputs, and the trusted results runner rejects publication unless every data input maps to `open` source IDs and every non-manifest staged file is role-labelled and checksummed in the release manifest. Its plan declares `rights_authority: gate2-state` in autonomous mode or `manual-caller` under `--manual`; the runner checks that choice against the deployment manifest. The analysis and release receipts activate together in the registry; autonomous mode then binds their paths in pipeline state, while manual mode returns the active paths to the caller and creates no pipeline state; a manual caller also supplies the exact coverage decision/list and any required certificate pair. `puzzle-triager` runs with data-first semantics — a **failed replication** with its side-by-side construction isolation is the mode's highest-value outcome, and PIVOT promotes it to a headline adjudication (re-anchoring the fact portfolio; the dataset carries forward); Stage 5 writes the data-paper structure (`related_datasets`/`construction`/`validation`/`facts`/`availability` sections; restricted sources appear only in build-from-source instructions); `referee-mechanism` runs as a **fact-validity referee** (are the facts features of the world or artifacts of the construction?), and `polish-identification` re-targets as the causal-overreach backstop (facts are descriptive by design; causal language is flagged for restatement). The scorer's novelty calibration is explicitly two-tier: dataset + adjudication/new facts competes top-3; infrastructure-plus-replications alone calibrates honestly to the field tier. The autonomous runtime doc's H1 becomes "Autonomous Data Paper Pipeline". Known v1 limits (each tracked): coverage completeness has no ground truth (#281), source-license interpretation and provenance semantics cannot be proven mechanically (#282), the release is a static snapshot (#283), and the descriptive-facts boundary is prompt-and-polish (#284).

### `--mode measurement-first`

The llm_cognition analog of `empirical-first` (issue #199): flips the pipeline from theory-first to evidence-first for the modal ML cognition paper (measurement, evals, probing, interpretability), where the experiments ARE the contribution. llm_cognition-only (`setup.sh` errors on other variants); `--ext theory_llm` is auto-implied as in every llm_cognition deploy, and here the implication is load-bearing — Stage 3b is the mode's evidence core. Composes with `--seed`, `--faithful`, and `--light`; independent of `--manual`. Concretely: Stage 1 approach sketches carry candidate constructs + task families (`idea-generator`/`idea-prototyper` body overlays; the prototyper may run a **toy-scale pilot** to check generability/scoring/detectability, and its BLOCKED verdicts follow the standard DIFFICULTY/IMPOSSIBLE split); Stage 2 `theory-generator` runs in **construct mode**, producing a construct spec (formal construct definition + task family + scoring rule + measurement plan — no theorems); Gate 2's binding half is a **plan-time design gate** — `experiment-reviewer` launched on the measurement plan, verdicts ACCEPT/REVISE/REDESIGN, tracked by the `stage2_design_version` state field — while the **math-audit pair is deferred, not skipped**: after Stage 3b completes, `theory-generator` re-enters in **characterization mode** to formalize what was measured, and both math audits fire on that characterization (full audits, later — see `docs/stage_2.md` "Deferred math audits" and `docs/stage_3b_experiments.md` "Post-experiment characterization"); Stage 2b is permanently skipped (the pilot plays its role); Stage 3 derives auxiliary contrasts (gradients, falsifications, alternative-account discriminators); the scorer's H3 gates on all three legs (design-gate ACCEPT + Stage 3b chain + characterization audits). Evaluator vocab is recalibrated via `deploy_assets/templates/agents/llm_cognition_modes/measurement_first/vocab.json` and body overlays under `deploy_assets/templates/agent_bodies/shared_modes/measurement_first/` (including a construct-validity `referee-mechanism`). The runtime doc's title becomes "Autonomous Measurement Paper Pipeline".

### `--mode report`

Reframes the project as refereeing an external submission. User drops the paper in `submission/`; the orchestrator runs a triage step, fans out all audit agents (`math-auditor` + freeform, `polish-{formula,numerics,consistency,equilibria,identification,prose,bibliography,institutions}`, `bib-verifier`, `novelty-checker`, `self-attacker`, `referee` / `referee-freeform` / `referee-mechanism`) in parallel against the submission, then `report-synthesizer` aggregates `audits/*.md` into `report/referee_report.md` with a single verdict (Accept / Minor revision / Major revision / Reject). One-shot, no stages, no `pipeline_state.json`, no `dashboard.html`. Mutually exclusive with `--seed`, `--faithful`, `--manual`, `--mode empirical-first`. Composes with `--light`. Supported variants: `finance`, `macro`, and (since v2.16.0) `llm_cognition` — the llm_cognition report referees run ML-calibrated (top-ML venue role, conference-cadence verdict semantics: Minor/Major Revision read as rebuttal-cycle / resubmit-next-cycle routing tokens), and the theory_llm auto-imply is skipped (report mode prunes those agents; the flag can still be passed explicitly for install-only skills).

Composes with `--ext empirical` and `--ext theory_llm` in **install-only** mode: the extension's *skills* install (WRDS/FRED/Census/SEC helpers, the LLM-experiment client) so the audit agents can spot-check external data or call an LLM if needed, but the extensions' *audit agents* (`empirics-auditor`, `identification-auditor`, `mechanism-auditor`, `headline-replicator`, `data-integrity-auditor`, `data-selection-auditor`, `method-checker`, `experiment-reviewer`) are pruned — they were designed against the pipeline's own producer output and would need substantial rewrites for external submissions. The base referees evaluate empirical submissions holistically (identification, magnitude, robustness at editorial level); deep code-level adversarial auditing of external empirical submissions is a v2 feature.

Pruned at assembly time via `_setup_extensions_prune_report_mode_agents` in `deploy_assets/scripts/setup/extensions_and_injections.sh`, by category: generative agents (`theory-generator`, `paper-writer`, `idea-*`, `question-poser`, `question-referee`, `theory-explorer`, `implications-deriver`), the `last-resort` escalation agent (one-shot report mode has no stuck pipeline to unstick), pipeline-management agents (`scribe`, `triager`, `puzzle-triager`, `branch-manager`, `editor`), scoring agents (`scorer`, `scorer-freeform`), broad-survey agents (`literature-scout`, `gap-scout`), the `style` editor, and extension generative agents (`empiricist`, `identification-designer`, `experiment-designer`). (`faithful-drift-auditor` is also absent from a report build, but via a different mechanism — `_setup_extensions_prune_non_faithful_agents`, which drops it from any non-`--faithful` build; report mode simply can't be faithful.) For the exact current set — it changes as agents are added — grep the `_setup_extensions_prune_report_mode_agents` call sites in `deploy_assets/scripts/setup/extensions_and_injections.sh` rather than trusting this list.

`--mode report` also carries its own vocab, body, and metadata overlays like any mode: `deploy_assets/templates/agents/{variant}_modes/report/vocab.json`; `deploy_assets/templates/agent_bodies/shared_modes/report/{referee-core,referee-freeform,referee-mechanism,polish-identification}.md` re-aim the referees and the identification audit at an external submission (polish-identification audits the submission's *own stated design* — its pipeline body would otherwise N/A on every report run for lack of a pipeline design artifact); report-native `description` overrides in the agent metadata (`"modes": {"report": ...}`); and `deploy_assets/templates/shared/report_mode_inject.md`, appended to the 12 remaining pipeline-native audit agents so prompt-passed `submission/` + `audits/` paths win over their bodies' pipeline paths, with an explicit degraded-check note on PDF-only submissions.

H1 subtitle becomes "Autonomous Referee Report Pipeline".

### `--faithful`

A stricter variant of `--seed`; pass one or the other, not both, and not alongside `--manual` (also mutually exclusive). The flag implies `--seed`'s folder structure (creates `output/seed/`, starts at `seed_triage`) but supersedes its semantics with the faithful contract. At seed_triage the orchestrator extracts `output/seed/mechanism_contract.md` (the seed's named mechanism, structural invariants, theorem-statement constraints, identification strategy, stated contribution); developing agents must respect every invariant. Substitution / pivot / headline-replacement are forbidden; additions on top of the faithfully-implemented contract (extra theorems, comparative statics, robustness checks) are encouraged. Genuine impossibilities get documented in `output/seed/limitations.md` and the paper ships documenting them honestly. Agents marked `category: evaluator` in their metadata stay impartial and receive no contract pointer — corrupting the evaluation signal corrupts the paper. The developing/evaluator split is derived from that metadata field at assembly time (`deploy_assets/scripts/list_agents_by_category.py`), not from a hardcoded list; run that script for current membership. The faithful constraint enters at the orchestrator's routing of evaluator verdicts (per `deploy_assets/templates/shared/faithful.md`) and via a static "read `mechanism_contract.md` first" pointer appended to each developing agent body. A `process_log/pivot_log.md` is seeded for auditing every potentially-mechanism-affecting routing decision.

UNDER `--faithful` THE SEED FREEZES INTO A CONTRACT AT STEP 0, SO SPECIFY THE SETUP (MODEL CLASS, STRUCTURAL INVARIANTS, THEOREM-STATEMENT CONSTRAINTS) AND NEVER THE RESULT — DERIVING RESULTS IS WHAT THE PIPELINE IS FOR.

### `--light`

Runs the **whole pipeline** on the cheapest capability tier its runtime offers — subagents *and* orchestrator. Composes with every other flag. Each runtime maps through its own tier table: claude `sonnet`, codex `gpt-5.6-luna`, gemini `gemini-3-flash-preview`. Grok is a no-op because its table is a single model (`grok-4.5`).

Two mechanisms, because the two halves are pinned at different times:

- **Subagents, at assembly time.** `MODEL_OVERRIDE_ARGS` in `setup.sh` passes `--model-override sonnet` through `deploy_assets/scripts/setup/base_agents.sh` to all five base assemblers and through the extension appliers (cross-runtime since v2.18.2 — before that the codex assembler had no override argument, so `./launch.sh codex` on a light deployment silently ran the full Sol/Terra pinning). The override also drops each agent's per-runtime reasoning effort (`effort` on claude, `model_reasoning_effort` on codex), since those levels are calibrated to the agent's *ideal* tier; a light Codex role therefore runs Luna at that model's native default effort.
- **Orchestrator, at launch time** (since v2.19.0). `launch.sh` pins it: `--model <tier>` for claude/gemini, `-c model="<tier>"` for codex (config form, not the flag, because `codex exec resume` accepts only `-c` and the driver resumes on every turn after the first). The tier is **read back from the assembled agents**, not hardcoded a fourth time — so it tracks the assemblers' tables automatically, survives `update.sh`, and for claude reflects the launch-time heal that runs immediately before. The pin fires only when `.deploy_manifest.json` records `flags.light` **and** every assembled agent agrees on one model; anything else leaves the CLI default alone. Grok's branch never consults it.

Both halves are best-effort in the safe direction: a pre-manifest deployment, a missing `python3`, or an unreadable agents dir means no orchestrator pin and the launch proceeds normally.

**Worth a deliberate choice, not a default.** The orchestrator makes the stage-routing and gate decisions — it is the single process where a cheaper model degrades the most. Prefer `--light` for drafts, smoke tests, and runtime shakedowns; think twice before running a paper you intend to submit on it.

What `--light` does **not** touch: the codex-math skill (pinned `gpt-5.6-sol` independently — it is a tool, not a subagent) and the Claude launch-time model heal, which re-decides tiers against the `--light-model` recorded in `code/utils/model_heal/config.json` rather than against the ideal pins.

### `--halt-on-core-bypass`

(issue #51) Guards against silent degradation when a **core** (binding source, verification gate, or designated agent/step) is bypassed: default is record-and-surface (agent pointer → `process_log/degradation_ledger.md`, verdict marked NON-BINDING; nothing added to the runtime doc), and the flag adds a halt (`status = "halted_core_bypass"`). See `docs/core_bypass.md` (the deployed doctrine); wiring lives in `_setup_extensions_inject_core_bypass_into_agents` in `deploy_assets/scripts/setup/extensions_and_injections.sh` and the `{{CORE_BYPASS_GUARD}}` placeholder in `core.md`.

## After setup

Setup creates a standalone local git repository with assembled CLAUDE.md, AGENTS.md, GEMINI.md, agents for all runtimes, and skills. A successful `--publish` adds and pushes its GitHub remote. If publication reports a failure, inspect the printed target URL before retrying because GitHub may have created the repository before a later step failed. Tell the user to:

1. `cd <project-name>`
2. Edit `.env` with any required API keys (FRED, WRDS, etc.)
3. Launch a runtime with the deployed launcher: `./launch.sh claude` / `./launch.sh codex` / `./launch.sh gemini` / `./launch.sh grok` (add `--tmux` to wrap in a detached tmux window). For stateless `--mode report` and `--manual` deployments, use `./launch.sh codex --once`; the Codex driver requires the autonomous pipeline's `pipeline_state.json`. The script activates the project venv (`.venv/`, created by `setup.sh`, gitignored — bare `python3` resolves to it and every agent Bash subshell inherits it) and applies each runtime's correct flags. **`./launch.sh codex` is a headless driver loop, not a TUI**: native child completion wakes an active parent that is still waiting in the same turn, but Codex has no cross-turn autowake—a parent whose turn has ended is never resurrected by a child. The driver therefore re-prompts via `codex exec resume` until `pipeline_state.json` says `complete`/`halted_*`, making top-level turn ends harmless; the native-role protocol keeps each spawning turn alive until its own children are terminal. `./launch.sh codex --once` gives a plain interactive TUI when you want one. Codex launches require codex-cli >=0.147.0 for permission profiles and fail with an upgrade instruction on older installations. Do not reproduce the Codex command manually: the launcher validates/materializes the broad cache root, applies the exact WRDS read-only carve-out, preserves `.git` writes, and establishes WRDS before sandbox entry; omitting any of those is not an equivalent safety posture.
4. Say "Run the pipeline." (interactive runtimes; the codex driver sends it itself)

### Long unattended runs

**codex** is already headless-safe via the driver loop — `./launch.sh codex --tmux` is the complete unattended form.

For **Claude**, use `./launch.sh claude --tmux`, then attach/send "Run the pipeline." in that interactive window. This preserves the launcher-owned WRDS prestart and cache-root validation while surviving detach. Do **not** invoke Claude directly and do **not** use headless `claude -p "Run the pipeline."`, which terminates at the ~600s background-task wait ceiling while a subagent is still running. The orchestrator resumes from `process_log/pipeline_state.json` + committed `output/` artifacts, so a fresh interactive session picks up where an interrupted run left off.

## WRDS server (only with `--ext empirical`)

The empirical extension talks to WRDS through one long-running host-wide server so the Duo 2FA push happens once per server session, not per query. `launch.sh` starts it before Claude/Codex/Grok enter their network sandboxes (including report/manual deployments, which intentionally have no pipeline state). OpenCode starts or joins it through a launcher-owned, long-lived SRT service wrapper: a model-immutable stdlib gatekeeper runs from `.opencode` with the trusted system Python, a host-wide protected lock serializes first-start, and the unsandboxed control plane validates PID/birth/process-group identity and host-visible PID semantics before approving any login. Only after approval may the project venv, `.env`, and service code execute inside SRT; missing credentials skip cleanly without executing them. Clients prefer the private query-only `~/.local/state/zeropaper/wrds/wrds_server_23847.sock` transport through the read-only home view. macOS grants only that socket path. Anthropic Sandbox Runtime's Linux seccomp filter cannot distinguish socket paths and blocks AF_UNIX creation for model processes, so Claude/OpenCode clients instead use a separately authenticated query-only relay through their local sandbox HTTP proxy: the relay has no credentials, accepts only v7 query commands, and requires a rotating 256-bit capability from protected WRDS state. Never enable `sandbox.network.allowAllUnixSockets` for a model process; the launcher-only OpenCode service profile uses that capability solely inside its narrower, project-read-only service sandbox. No lifecycle command is exposed on either wire. Unconfined Gemini remains excluded (#187). The pipeline's data-inventory step also runs the idempotent `code/utils/start_services.sh` health check before Stage 0, and you can run that check manually on the host:

```bash
cd <project-name>
bash code/utils/start_services.sh   # idempotent; reuses an existing server if one is up
```

The server and query relay are per-host, not per-project — once they are running, every project that has the WRDS skill reuses them, including commands in isolated network namespaces. If you are working in the template repo itself (no `.env`, no `code/utils/`), `cd` into any existing deployed empirical project on this host and run `bash code/utils/start_services.sh` from there; the resulting services will serve the template's future deployments too.

For the first upgrade from a pre-v5 deployment, stop every older empirical runtime/tmux window before starting the new daemon. A released client can otherwise already be paused after its legacy latch check inside another network namespace. V5 checks for deployed foreign namespaces and refuses the login until they are quiescent; relaunch them only after the v5 host daemon is healthy.

The v7 safety protocol is intentionally incompatible with older daemons/relays. After updating a deployment, stop the old host service once and relaunch through `launch.sh`; the safety handshake then prevents mixed-version queries. V7 retains v6's binary framing, 512 MiB malformed-peer wire bound, and total frame deadlines, and adds payload-scaled response-write deadlines plus durable partial-write diagnostics. SQL execution, response preparation, daemon-to-relay transfer, and relay-to-client transfer receive separate composed deadlines, so a query may use its full execution budget without consuming its frame-delivery budget. Queue wait, one guarded recovery, and retry share a single server operation deadline, with late-returning work rejected; DataFrame/final-JSON preparation runs in a separately timed, concurrency-bounded producer stage whose expired workers cannot write the socket. Only an in-budget command holding the serialized database owner is busy-but-live; an expired command, healthcheck/recovery, unblock, or unknown owner remains unhealthy, preventing concurrent pings from both declaring real work down and masking a genuinely wedged probe. The WRDS skill continues to enforce tighter row/materialization budgets and windowed pulls for genuinely large extracts.

To check if it's already running on this machine:

```bash
test -S ~/.local/state/zeropaper/wrds/wrds_server_23847.sock           # cross-sandbox endpoint exists
PYTHONPATH=code python3 -c "from utils.wrds_client import wrds_ping; print(wrds_ping())"
```

`True` from the ping means it's healthy.
