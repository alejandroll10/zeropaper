---
name: edit-pipeline
description: Reference for editing this template repo itself — repository layout, how setup.sh assembles a deployment, the runtime-agnostic core vs runtime-specific packaging split, the full agent roster and its shared/variant/extension classification, subagent model pinning and fallback/heal, and the step-by-step procedures for adding a new variant, a new mode, an agent, a skill, or a vocab placeholder. Use when modifying setup.sh, update.sh, templates/, extensions/, scripts/, agent metadata or bodies, vocab.json, or fragments — and before adding any new deployed path, agent, or placeholder.
---

# Editing the pipeline template

This repo builds the pipeline; it is not the pipeline. Deployment usage (setup.sh flags, launching a deployed project) lives in the `deploy-project` skill instead.

## Conventions that bite

These four have non-obvious failure modes. The first three have a one-line trip-wire in CLAUDE.md (which fires without this skill being loaded) and their mechanism here. The fourth — meta-repo dev skills — has no CLAUDE.md trip-wire on purpose: it is zero-maintenance by design, so there is nothing to remember and nothing to get wrong.

### Deployment manifest

When adding a new infrastructure path to `setup.sh` (a dir or file that gets **deployed**), also add it to `candidate_dirs` / `candidate_files` in the manifest emission block (`# ── Emit deployment manifest ──`; `candidate_dirs = [` and `candidate_files = [`). Otherwise `update.sh` silently skips it when refreshing existing deployments — new deployments are fine, which is what makes this easy to miss.

Build-time-only paths get **no** manifest entry, because they never ship. Current examples: `VERSION`, `CHANGELOG.md`, `templates/model_fallbacks.json`, `scripts/resolve_model_fallbacks.py`, `scripts/apply_model_remap.py`, `scripts/emit_model_heal_config.py`, `templates/fragments/`, and the meta-repo dev skills. The test is not "is it new?" but "does a deployed project contain it?"

### Shared rule fragments (`templates/fragments/*.md`, issue #167)

A load-bearing block of rule text that must read **byte-identically** across many agent bodies (the substance-over-form archetype list, the policy-map axes enumeration, the institutional-acronym citation carve-out, the `irreducible_stochasticity` JSON schema) is single-sourced as a fragment and referenced with a `{{> fragment_id }}` include directive.

`scripts/agent_body_loader.py` inlines the fragment at assembly time, **before** vocab substitution — so a fragment may itself carry `{{VOCAB_KEY}}` placeholders. The directory is auto-discovered relative to the loader, so every assembler (base + extensions, all three runtimes) shares it with **no** per-call wiring. Build-time only: inlined into deployed agents, never copied out, so no manifest entry.

- Fragment IDs are lowercase (`[a-z0-9][a-z0-9_-]*`). An uppercase ID in a `{{> … }}` directive will **not** match and ships literally.
- Use a fragment only for genuinely byte-identical atoms. Do **not** fragment role-adapted prose that merely looks similar — the copies across scorer / referee / self-attacker / triager are intentionally verb- and verdict-specific, and flattening them changes behavior.
- To verify a fragment migration is zero-behavior-change: assemble before and after (`git stash` the edits) and `diff -rq` the `.claude` / `.codex` / `.gemini` agent dirs. They must be identical.

### Vocab placeholders

Since v2.9.0, **every** body — shared `{id}.md`, variant `{id}-core.md`, and extension bodies — resolves against the same layered vocab chain, later wins: `agent_bodies/shared/vocab.json` (defaults) → `agents/{variant}/vocab.json` (domain overrides) → tier vocab → mode overlay. (The extension appliers layer shared → variant → mode the same way.) When adding a new `{{KEY}}` placeholder anywhere, put its **default** in the shared vocab — or in every variant vocab — then add per-variant overrides only where the domain wording differs. A key defined in only *some* variant vocabs with no shared default breaks setup for the other variants.

`scripts/agent_body_loader.py` raises `KeyError` on unresolved placeholders — fail-loud is what enforces the rule. Because the layers merge before substitution, a key must live in exactly one *default* home (shared vocab OR all variant vocabs); do not author the same default in both, and never reuse a shared-vocab key name for an unrelated variant concept — the variant value would silently capture every shared-body use of the key.

Two vocab layers are generated at setup time rather than authored: the **tier vocab** (`TIER_VOCAB_FILE` in `setup.sh` — `TIER_LIST_INLINE` / `TIER_LADDER_PROSE` from the variant case, passed to every base assembler so bodies like `editor.md` can name the variant's tier ladder), and the mode overlays.

Domain wording extracted from previously hardcoded economics prose lives in two override blocks: `_comment_domain_phrases` in each variant vocab (for the `-core` bodies — scorer tier bands, `FORCE_TERM`, referee exemplars, self-attacker archetype examples) and `_comment_shared_body_overrides` in `agents/llm_cognition/vocab.json` (for shared bodies and fragments — referee-mechanism's evaluative frame, literature-agent venue directives, `POLICY_MAP_AXES`, the ssj/nber-agenda advice bullets), with the matching defaults in the shared vocab's `_comment_domain_defaults` block. When editing any body, prefer extending these keys over re-hardcoding domain language; the econ defaults must stay byte-identical to the pre-extraction text unless a behavior change is intended (verify with a before/after `--local` build diff of finance and macro).

### Meta-repo dev skills

`.claude/skills/` is tracked in this repo (it is **not** gitignored, unlike `.claude/agents/`). `setup.sh` snapshots whatever dev skills the clone carried in, immediately after `git init` (`DEV_SKILLS`), and removes them in the cleanup block before the initial commit — so they never ship into a research project.

The mechanism is snapshot-based, not a name list: **adding a new dev skill requires no `setup.sh` edit.** The strip is checksum-guarded, so if a future `skill_id` in `templates/skill_metadata/` ever collides with a dev-skill directory name, the assembled project skill is kept and a rename warning is printed rather than the skill being silently deleted.

### Dev settings vs deployed settings

This repo's `.claude/settings.json` configures the **template-development** session and ships
nowhere. The settings a deployed project runs under — including the sandbox profile — live in
`templates/runtime/{claude,gemini}/settings.json` and are installed by the
`install_runtime_settings` block in `setup.sh` (grep that string), which runs for both `--local`
and production and overwrites whatever the clone carried in.

Keep the two apart. They want opposite things: the template repo needs a permissive posture
(it deploys projects into arbitrary paths), a research project wants the sandbox on. A single
dual-role file at the repo root cannot be both, which is exactly what it used to be.

Sandbox config is per-runtime and lives in three different shapes: Claude's `.claude/settings.json`
(copied from templates), Gemini's `.gemini/settings.json` (copied), and Grok's `.grok/sandbox.toml`
(**generated** per-deploy, because grok's TOML does not expand `~`/`$HOME` and needs the deploying
user's absolute paths baked in). Codex takes its sandbox posture from `launch.sh` flags, not a file.

## Repository structure

> This tree is a **snapshot** and has drifted before. `scripts/` and the top level of
> `templates/` and `extensions/*/` are complete. Everything nested deeper —
> `skill_metadata/`, `skill_bodies/`, `agent_bodies/`, `utils/`, `shared/docs/` — is
> illustrative, not exhaustive. When it matters, `ls` the directory rather than trusting
> the diagram.

```
templates/
├── shared/
│   ├── core.md              # Runtime-agnostic pipeline orchestrator template
│   ├── core_manual.md       # Slim manual-mode runtime doc (no pipeline, just catalogs)
│   ├── core_report.md       # Report-mode runtime doc (--mode report)
│   ├── seed.md              # Seeded-idea override block (injected when --seed is used)
│   ├── faithful.md          # Stricter seeded-mode block (injected when --faithful is used)
│   ├── faithful_inject.md   # Short pointer appended to developing-agent bodies under --faithful
│   ├── core_bypass_inject.md    # {{CORE_BYPASS_GUARD}} content
│   ├── efficiency_inject.md
│   ├── bash_background.md
│   ├── docs/                # Per-stage docs (stage_0.md … ) + core_bypass.md, model_fallback.md
│   ├── tier_tables/
│   ├── seed_overrides/      # Per-stage overrides for --seed (gate doc placeholders)
│   └── faithful_overrides/  # Per-stage overrides for --faithful (supersedes seed_overrides)
├── runtime/                 # Each of claude/, codex/, gemini/ has THREE session files:
│   │                        #   session.md         (autonomous mode)
│   │                        #   session_manual.md  (--manual)
│   │                        #   session_report.md  (--mode report)
│   ├── claude/              # + settings.json → deployed .claude/settings.json (sandbox profile)
│   │                        # (no grok/ — Grok reads the shared AGENTS.md; its
│   │                        #  .grok/sandbox.toml is generated per-deploy in setup.sh)
│   ├── codex/
│   └── gemini/              # + settings.json → deployed .gemini/settings.json
├── agent_metadata/          # JSON metadata for agent assembly (tools, model, description, category)
│   ├── claude_shared_agents.json     # domain-agnostic agents
│   └── claude_variant_agents.json    # ONE file for all variants (not per-variant)
├── agent_bodies/            # Agent prompt bodies (plain markdown)
│   ├── shared/              # Both kinds live here:
│   │                        #   {id}.md      → domain-agnostic shared agent
│   │                        #   {id}-core.md → variant agent, composed with variant vocab
│   │                        #   vocab.json   → defaults for SHARED-agent placeholders
│   └── shared_modes/        # Per-mode body overrides: empirical_first/, report/
├── skill_metadata/          # JSON metadata for skill assembly
│   ├── codex_math_skills.json
│   ├── empirical_skills.json
│   └── theory_llm_skills.json
├── skill_bodies/            # Skill prompt bodies (plain markdown)
│   ├── codex_math/
│   ├── empirical/
│   └── theory_llm/
├── utils/                   # Utility scripts copied into deployed projects → code/utils/
│   │                        # codex_math/, nber_agenda/, openalex/, bib_verify/, ssj/,
│   │                        # model_heal/, agent_launcher/,
│   │                        # pipeline_dotenv_guard.py, setup_push_token.sh
├── deps/                    # Python dependency lists (core.txt, ssj.txt)
├── fragments/               # Shared byte-identical rule fragments ({{> id}} includes)
├── paper_skeleton/          # LaTeX .template files for the initial paper scaffold
│   │                        # Root templates are the econ default; a variant dir
│   │                        # (llm_cognition/main.tex.template — ML preprint format)
│   │                        # overrides per-file, root is the fallback
├── model_fallbacks.json     # Model → ordered fallback chain (build-time only)
├── agents/                  # Per-variant VOCAB ONLY — no agent bodies live here
│   ├── finance/vocab.json
│   ├── finance_modes/       # Mode vocab overlays: empirical_first/, report/
│   ├── macro/vocab.json
│   ├── macro_modes/
│   └── llm_cognition/vocab.json   # no _modes yet: report mode is gated off (LIMITATIONS.md)
└── gitignore_project        # .gitignore template for deployed projects

scripts/
├── assemble_claude_agents.py   # Combines agent metadata + bodies → .claude/agents/*.md
├── assemble_claude_skills.py   # Combines skill metadata + skill bodies → .claude/skills/*/SKILL.md
├── assemble_codex_skills.py    # Combines skill metadata + skill bodies → .agents/skills/*/SKILL.md
├── assemble_codex_subagents.py # Combines agent metadata + bodies → .codex/agents/*.toml
├── assemble_gemini_agents.py   # Combines agent metadata + bodies → .gemini/agents/*.md
├── assemble_grok_agents.py     # Combines agent metadata + bodies → .grok/agents/*.md
├── assemble_runtime_doc.py     # Builds CLAUDE.md / AGENTS.md / GEMINI.md from core + session
├── agent_body_loader.py        # Resolves bodies ({id}.md vs {id}-core.md), fragments, vocab
├── test_agent_body_loader.py   # Tests for the loader
├── list_agents_by_category.py  # Source of truth for the developing/evaluator split
├── generate_catalog.py         # Manual mode: emits agent/skill catalog markdown from metadata
├── apply_extension_empirical.sh    # Wires the empirical extension into a deployment
├── apply_extension_theory_llm.sh   # Wires the theory_llm extension into a deployment
├── resolve_model_fallbacks.py  # Probes model availability (build-time only)
├── apply_model_remap.py        # Rewrites model: frontmatter post-assembly (build-time only)
└── emit_model_heal_config.py   # Emits code/utils/model_heal/config.json (build-time only)

extensions/                  # Optional extensions (empirical, theory_llm)
├── empirical/
│   ├── agent_metadata/      # shared_agents.json, finance_agents.json, macro_agents.json
│   ├── agent_bodies/        # shared/, finance/, macro/
│   ├── utils/               # Python/shell utilities copied into project
│   ├── docs/                # stage_3a_empirical.md (stage doc for the empirical stage)
│   ├── deps.txt             # extension-specific Python deps
│   └── *_inject.md          # 8 orchestrator injections — see "Adding a new extension"
└── theory_llm/
    ├── agent_metadata/      # agents.json
    ├── agent_bodies/        # Agent prompt bodies
    ├── docs/                # stage_3b_experiments.md
    ├── deps.txt
    ├── llm_client.py        # LLM client copied into project
    └── *_inject.md          # 5 orchestrator injections

Note: extension *skills* do NOT live here — see "Adding a new extension" below.

setup.sh                     # Clones repo, assembles CLAUDE.md + AGENTS.md + GEMINI.md + agents + skills
dashboard.html               # Live progress dashboard
test_scripts/                # Skill verification scripts (removed on deploy)
```

## Architecture: runtime-agnostic core + runtime-specific packaging

The pipeline is split into two layers:

- **Runtime-agnostic**: `templates/shared/core.md` (orchestrator logic, pipeline stages), `templates/agent_bodies/shared/` and `templates/agents/{variant}/vocab.json` (agent prompts and per-variant vocab including scorer calibrations) — these are the same regardless of runtime.
- **Runtime-specific**: `templates/runtime/{claude,codex,gemini}/session.md` (session guidance per runtime), `templates/agent_metadata/claude_*.json` (shared metadata with per-runtime overrides via `codex` and `gemini` keys), `scripts/assemble_{claude_agents,codex_subagents,gemini_agents,grok_agents}.py`.

**Four** runtimes share the same core + agent bodies, with runtime-specific packaging: Claude, Codex, Gemini, and **Grok**. Grok is the odd one — it has no `templates/runtime/grok/session.md` (it reads the shared AGENTS.md, per the comment in `setup.sh`), but it is otherwise fully wired: `assemble_grok_shared_agents` / `assemble_grok_variant_agents` in `setup.sh`, `scripts/assemble_grok_agents.py`, output to `.grok/agents/*.md`, a generated `.grok/sandbox.toml`, and manifest entries for both. When you add an agent or change assembly, Grok is a fourth call site that is easy to miss precisely because it has no session.md next to the others.

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
   - Shared: `agent_metadata/claude_shared_agents.json` + `agent_bodies/shared/{id}.md`, composed with `agent_bodies/shared/vocab.json` (shared agents get vocab substitution too — mode overlays layer on top)
   - Variant: `agent_metadata/claude_variant_agents.json` (one file, all variants) + `agent_bodies/shared/{id}-core.md`, composed with `agents/{variant}/vocab.json`
   - Claude → `.claude/agents/*.md`, Codex → `.codex/agents/*.toml`, Gemini → `.gemini/agents/*.md`, Grok → `.grok/agents/*.md` (four call sites — don't miss Grok)
5. Injects variant context (paper type, journal list, domain) into key agents
   - If `--faithful`: also appends `templates/shared/faithful_inject.md` (a short "read `output/seed/mechanism_contract.md` first" pointer) to *developing* agent bodies only. **The split is data-driven, not hardcoded**: each agent's `category` field in its metadata (`developing` or `evaluator`) decides, and `scripts/list_agents_by_category.py` derives the two lists at assembly time — so a new agent is classified by setting `category`, with no `setup.sh` edit. Evaluators deliberately receive **no** pointer: corrupting the evaluation signal corrupts the paper. `last-resort` is categorized `developing` precisely so a fix it proposes for a stuck artifact respects the contract. To see the current membership, run `python3 scripts/list_agents_by_category.py` rather than trusting any prose list — earlier hardcoded enumerations in this repo's docs had drifted out of sync with the metadata.
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

## Agent classification

Agents are either **shared** (identical across variants) or **variant-specific** (one body, specialized per domain by vocab substitution). Each agent is defined as:
- **Metadata**: `agent_metadata/claude_shared_agents.json` (shared agents) or `agent_metadata/claude_variant_agents.json` (variant agents — a single file covering every variant, *not* one file per variant). Claude frontmatter plus Codex and Gemini overrides, and a `category` field (`developing` / `evaluator`) that drives faithful-mode injection.
- **Body**: `agent_bodies/shared/{id}.md` for shared agents, `agent_bodies/shared/{id}-core.md` for variant agents. Both live in the same directory — the `-core` suffix is what marks a body as variant-specialized, and `scripts/agent_body_loader.py` (`load_body`) tries `{id}-core.md` first, then `{id}.md`. `templates/agents/{variant}/` holds **only** `vocab.json`; no agent bodies live there.
- **Vocab**: *both* kinds get placeholder substitution, and since v2.9.0 both resolve against the same layered chain: `agent_bodies/shared/vocab.json` (defaults) → `agents/{variant}/vocab.json` (domain overrides) → tier vocab → mode overlay, later wins. So a `{{KEY}}` added to *any* body or fragment needs a default in the shared vocab (or in every variant vocab); variant vocabs override only where the domain wording differs. This layering is what makes shared bodies (referee-mechanism's evaluative frame, the literature agents' venue directives, the fragments) variant-aware — see the `_comment_shared_body_overrides` block in `agents/llm_cognition/vocab.json` for the full override set.

**Shared** (domain-agnostic, receive variant context via injection). All 31 live in `claude_shared_agents.json`; the authoritative list is that file, and `python3 scripts/list_agents_by_category.py` prints current membership by category.

*Literature & framing*
- `literature-scout` — broad literature survey (variant context provides target journals)
- `gap-scout` — deep search on a pre-selected gap (adjacent literatures, closest competitor, gap validation)
- `novelty-checker` — searches web for prior work; fires twice (Gate 1b on the selected idea, and again later)

*Theory development & checking*
- `idea-prototyper` — quick math feasibility + surprise check
- `implications-deriver` — derives the theory's testable implications at Stage 3 Step 1 (web-blind; the orchestrator lit-checks each via gap-scout and tags). Pinned `fable`; has an empirical-first body override (auxiliary predictions only)
- `theory-explorer` — computational verification, calibration, parameter exploration, plots (Stage 2b)
- `math-auditor` — checks derivations step-by-step at Gate 2
- `math-auditor-freeform` — reads the theory as a skeptical reader, after the structured audit passes

*Scoring & refereeing*
- `scorer-freeform` — free-form quality assessment at Gate 4 (holistic read, no rubric)
- `referee-freeform` — free-form referee report at Stage 6 (editorial assessment)
- `referee-mechanism` — Stage 6 referee focused on whether the mechanism delivers the claimed result *for the claimed reason*
- `editor` — aggregates the three Stage 6 referee reports into one Gate 5 routing verdict + canonical comment list
- `report-synthesizer` — `--mode report` only: aggregates `audits/*.md` into `report/referee_report.md` with a single verdict

*Writing & polish* (all `developing`)
- `paper-writer` — writes and revises the LaTeX paper
- `bib-verifier` — verifies the bibliography against OpenAlex (WebSearch fallback for SSRN/recent)
- `polish-formula` — re-derives every numbered equation/lemma/proposition from surrounding text
- `polish-numerics` — re-does every numerical example, calibration, back-of-envelope claim
- `polish-consistency` — flags where the rendered paper contradicts itself
- `polish-equilibria` — hunts unstated multiple equilibria, missing LLN/continuum assumptions
- `polish-identification` — hunts estimand-vs-claim mismatches (says ATE, design recovers LATE)
- `polish-institutions` — verifies real-world claims (regulation, fee conventions, market sizes)
- `polish-bibliography` — verifies each in-text citation actually supports the prose claim
- `polish-prose` — audits prose economy (hedge stacking, restated caveats, abstract bloat)
- `style` — mechanical style violations at Stage 7

*Routing, triage & escalation*
- `triager` — mechanically applies triage rules to self-attack concerns, referee comments, polish findings
- `puzzle-triager` — triages contradictions between theory predictions and empirical results. Pinned `fable`
- `branch-manager` — strategic advisor at Gate 4 + Stage 2 audit loop (every 3rd theory version); diagnoses ceiling/alternatives. Pinned `fable`
- `last-resort` — general-purpose escalation for stubborn problems; launched at orchestrator discretion (no auto-trigger) when normal escalation is exhausted and the alternative is abandonment. Pinned `fable`, broad tool access; receives full failure history; returns `FIX-PROPOSED` (re-verified by the existing gate — never self-certifies) or `GENUINELY-STUCK`. Visible in the manual-mode catalog; pruned in `--mode report`
- `debugger` — launched when a computational or retrieval tool (solver, regression, symbolic verifier, literature/data query, compiler) has failed; determines whether the failure is the tool or the input
- `faithful-drift-auditor` — `--faithful` only: independent contribution-drift check at Gate 4 (before the plateau-ship decision) and Gate 5 (before ship)
- `scribe` — documents the process after every stage transition and gate decision

**Variant-specific** (different prompts per domain) — all eight are in `claude_variant_agents.json`:
- `question-poser` — turns the selected literature gap into one sharp research question at Stage 0 step 0d, after gap-scout; ceiling-setting, so pinned `fable` (web-blind by cost discipline)
- `question-referee` — vets the posed question on importance, openness, non-obviousness, and answer-symmetry (interesting either way) at Stage 0 step 0e; pinned `opus`
- `idea-generator` — needs domain-specific brainstorming patterns
- `idea-reviewer` — needs domain-specific evaluation criteria
- `theory-generator` — needs domain-specific model structure guidance
- `scorer` — needs domain-specific calibrations
- `self-attacker` — needs domain-specific attack vectors
- `referee` — needs domain-specific journal standards

**Extension agents** (added by `--ext` flags):
- `empiricist` — empirical analysis (variant-specific, `--ext empirical`)
- `empirics-auditor` — verifies empirical code/results (shared, `--ext empirical`)
- `headline-replicator` — independent recomputation of `[HEADLINE]` claims at Stage 3a step 6.5; drives the `headline_replication` / `replicator_self_refire` loop counters (shared, `--ext empirical`)
- `method-checker` — adversarial canonical-package review at Stage 3a step 7.5 (shared, `--ext empirical`)
- `mechanism-auditor` — plan-time mechanism-plausibility gate at empirical-first Gate 2 (Stage 2, before any empirical execution); runs the data-independent dimensions of the `referee-mechanism` checklist against the prose+DAG mechanism + Stage 1 identification design; returns PLAUSIBLE / REVISE (shared body, `--ext empirical`; **assembled then pruned in every mode except `--mode empirical-first`** via `prune_non_empirical_first_agents`)
- `data-integrity-auditor` — verifies cached field-content against source (shared, `--ext empirical`)
- `data-selection-auditor` — verifies cached sample against documented inclusion rule (shared, `--ext empirical`)
- `identification-designer` — designs the identification strategy at Stage 1 step 4 (variant-specific, finance only in v1, `--ext empirical`)
- `identification-auditor` — adversarial audit of identification strategy at Stage 3a step 3 (variant-specific, finance only in v1, `--ext empirical`)
- `claim-enumerator` — deterministic regex enumeration of numerical claims in the paper draft → `paper_claims.json` (shared, `--ext empirical`, Stage 5 step 5a)
- `claim-grounder` — LLM-judgment match of every enumerated claim to its empiricist-output source → `paper_source_map.json` (shared, `--ext empirical`, Stage 5 step 5a)
- `claim-verifier` — programmatic file/field/value verification of grounder citations with coverage check → REVISE feeds back to grounder or paper-writer (shared, `--ext empirical`, Stage 5 step 5a)
- `experiment-designer` — LLM experiments (shared, `--ext theory_llm`)
- `experiment-reviewer` — validates experiment methodology (shared, `--ext theory_llm`)

## Subagent model availability & fallback

Agent metadata pins an **ideal** model per agent. Seven agents currently pin `fable`: the rare strategic-routing agents `branch-manager`, `last-resort`, `puzzle-triager`, and the web-blind generative spine `question-poser` (Stage 0: the ceiling-setting research question) → `idea-generator` (Stage 1: approaches that answer it) → `theory-generator` (the mechanism/theory itself) → `implications-deriver` (its testable implications). The order matters: Stage 0 fixes the question, Stage 1 generates approaches *to* it — an earlier version of this doc had the first two reversed. These four are web-blind by **cost discipline, not capability**: fable tokens are far more expensive, so it is reserved for high-leverage, low-token reasoning, and token-heavy work — web search above all — is delegated to cheaper `opus` agents (`literature-scout`, `gap-scout`, `novelty-checker`). Fable *can* search; we just don't spend its tokens on the fetched-content volume, so a fable agent that needs the literature pairs with an opus searcher rather than searching itself. The selection rule that follows: **high-leverage + low-token reasoning → fable; token-heavy or search-bound work → opus.** All other agents pin `opus`/`sonnet` — notably the routine evaluators (`scorer`, `referee`, `self-attacker`, `math-auditor`) stay off `fable` on purpose: they run per-gate (cost), their rubrics in `vocab.json` are calibrated to `opus` behavior (a model swap would drift the thresholds), and keeping the generator and its judge on different tiers is a deliberate decorrelation.

If that model is unavailable on the account at setup time (a provider suspension — as happened when Claude Fable 5 / Mythos 5 were suspended by US export-control directive on 2026-06-12 — or simply no access), a pinned subagent would **hard-fail at launch with no fallback** (the Task tool returns "<model> is currently unavailable"; it does **not** silently downgrade to another model). To prevent that, `setup.sh` resolves models at assembly time:

- **Probe** (`scripts/resolve_model_fallbacks.py`): for each distinct model pinned across the Claude agent metadata, run the *same* `claude` CLI that will run the agents (`claude -p --model <id>`) and classify by output content (the unavailable message returns rc=0, so detection is by marker string `"is currently unavailable"` / the fable-mythos-access URL, not exit code). Runtime-accurate by construction — an API-key probe can disagree with the CLI's account access.
- **Fallback chains** (`templates/model_fallbacks.json`): each model maps to an ordered chain (`fable → opus → sonnet`, etc.). An unavailable model is remapped to the first chain entry that is not itself unavailable.
- **Apply** (`scripts/apply_model_remap.py`): a single post-assembly pass rewrites the `model:` frontmatter in every assembled `.claude/agents/*.md` (base + variant + every extension), so one pass covers all agents without threading remap args through each assembler call site.
- **Self-healing:** because metadata declares the *ideal* model, when a suspended model is restored the probe passes and no remap is applied — new deployments use the ideal again with no template edit.
- **Launch-time re-heal (Claude only):** the build-time remap runs *once* and cannot reach an already-deployed project whose tier goes down (or recovers) *after* setup. `./launch.sh claude` therefore re-decides each agent's tier at every launch via the **deployed** `code/utils/model_heal/heal_agent_models.py` + `config.json` — restoring the ideal when it recovers and falling back when it's down, in both directions. `config.json` records each agent's *ideal* model (emitted at build time by `scripts/emit_model_heal_config.py`, keyed by `.md` stem, variant-scoped) because the deployed `.md` only carries the current, possibly-remapped pin. Best-effort: an inconclusive probe leaves pins untouched and never blocks a launch (`set -euo pipefail`-safe guard in `launch.sh`). Codex/Gemini/Grok have no launch-heal — see `docs/model_fallback.md`.
- **Flags / safety net:** `--no-model-probe` skips the live probe (CI / offline) and relies on a static known-unavailable list (`fable,mythos,...`), which also catches the known suspension when the probe is inconclusive (e.g. `claude` not on PATH). The list is the `--known-unavailable` arg in `setup.sh`; update it if a new model is suspended and you can't probe.

**Codex tier mirrors the Claude tier.** Each agent's `codex.model` is the same capability tier as its Claude `model`, one-for-one: `fable → gpt-5.6-sol`, `opus → gpt-5.6-terra`, `sonnet → gpt-5.6-luna`. (OpenAI describes Sol/Terra/Luna as *durable capability tiers* that advance on their own cadence, so the mapping survives the next generation bump — only the `5.6` changes.) When you add an agent, pin both, and pin them to matching tiers; a `fable` agent whose codex twin is Terra is a silent cross-runtime capability mismatch, not a build error.

**The codex model/effort only take effect through the launcher.** codex's built-in `spawn_agent` tool (codex-cli 0.144.1) exposes no `model`/`reasoning_effort`/`agent_type` parameter and cannot select a role from `.codex/agents/` at all, so the `codex.model` we pin is inert if the orchestrator uses `spawn_agent`. The codex runtime therefore dispatches every agent through `code/utils/agent_launcher/launch_agent.sh`, which reads the agent TOML and runs an isolated `codex exec` worker: the agent body goes in the developer channel (the worker *is* the agent), on the pinned model/effort, with the orchestrator's AGENTS.md suppressed (restoring evaluator independence, which `spawn_agent`'s default `fork_turns="all"` otherwise breaks) and the native multi-agent tool removed so a worker is a leaf that cannot spawn its own sub-agents (via a patched no-spawn model catalog — codex ties the tool to the catalog's `multi_agent_version`, not a feature flag). This is a codex-CLI-version dependency with no setup-time probe — see the codex-dispatch entry in `LIMITATIONS.md`. (Claude and Gemini use native subagents and are unaffected.)

**Reasoning effort is capped at `high`.** gpt-5.6 also accepts `xhigh` and `max` (plus `ultra`, a four-agent parallel mode), and nothing in the pipeline uses them. On Agents' Last Exam — the long-horizon agentic benchmark whose shape most resembles this pipeline — GPT-5.6 Sol's score *peaks below its top effort setting*: the most expensive point on the cost curve scores below the one preceding it. Effort past `high` buys latency and tokens, not correctness. This is a claim about *our workload*, not about `max` in general (on ARC-AGI-3, `max` is the only setting that scores at all), so do not generalize it to a future benchmark without rechecking. The `codex_math` scripts reject `xhigh`/`max`/`ultra` at the CLI boundary.

**Known limitation (documented, not solved): `--light` does not reach the codex runtime.** `setup.sh` passes `--model-override sonnet` to `assemble_claude_agents.py` and `assemble_gemini_agents.py`; `assemble_codex_subagents.py` has no `--model-override` argument, so codex subagents keep their pinned tier under `--light`. This was invisible when every codex agent was a flat `gpt-5.5`; now a `--light` deployment still runs seven agents on Sol. Closing it means adding `--model-override` to the codex assembler (mapping the Claude alias through the same tier table, and dropping `model_reasoning_effort` the way the Claude assembler drops `effort`) and threading `MODEL_OVERRIDE_ARGS` into its four call sites.

**Known limitation (documented, not solved):** only **Claude** subagent models are probed/remapped. Codex (`gpt-5.6-{sol,terra,luna}`) and Gemini (`gemini-3-preview`) subagents use a different provider/CLI; their availability is not checked. If an OpenAI/Google model used by the codex/gemini runtimes is withdrawn, those agents would hard-fail the same way — closing that would require per-provider probes (an `openai`/`gemini` CLI check) and provider-specific fallback chains. The `model_fallbacks.json` schema and the resolver/apply split are already provider-agnostic; what's missing is the per-runtime probe command and wiring the apply pass over `.codex/agents` / `.gemini/agents`.

These four paths (`templates/model_fallbacks.json`, `scripts/resolve_model_fallbacks.py`, `scripts/apply_model_remap.py`, `scripts/emit_model_heal_config.py`) are **build-time only** — used during `setup.sh`, never copied into deployed projects — so they are intentionally absent from the deployment manifest. The launch-time heal is the exception that proves the rule: its script (`templates/utils/model_heal/heal_agent_models.py`) and generated `config.json` **are** deployed (to `code/utils/model_heal/`) and **are** manifested (in `candidate_dirs`), precisely because they must run at every launch, not just at setup.

## Core skills (all variants)

Four skills install unconditionally for every variant (`sympy`, `codex-math`, `bib-verify`, `openalex`); `ssj` and `nber-agenda` are **variant-gated** (issue #205): `variant_wants_skill` in `setup.sh` drops them from llm_cognition deployments (assembly, `code/utils/` copy, deps install, and the manual-mode catalogs all consult it), and `update.sh`'s stale-infrastructure sweep removes them from pre-gating llm_cognition deployments on refresh. `empirical_skills.json` and `theory_llm_skills.json` are extension-gated. Note `codex-math` is Claude-only — it is absent from `CODEX_SKILL_METADATA_ARGS`. When retiring any deployed path (skill or otherwise), the sweep handles old deployments automatically **only if the path was manifested** — a never-manifested path is invisible to it.

| Skill | Description |
|-------|-------------|
| `sympy` | Symbolic math — the workhorse for derivations and verification. Used by 6+ core agents. |
| `codex-math` | OpenAI Codex (gpt-5.6-sol, pinned explicitly rather than via the `gpt-5.6` alias) for proof verification, writing, and exploration. Erratic genius — substantial false-positive rate, always triage. Scripts at `code/utils/codex_math/`. Claude runtime only. |
| `bib-verify` | Bibliography verification — the tool behind the `bib-verifier` agent. |
| `openalex` | OpenAlex literature queries. Used by `literature-scout`, `gap-scout`, `novelty-checker`, all three referees (`referee`, `referee-freeform`, `referee-mechanism`), `polish-institutions`, `polish-bibliography`. |
| `ssj` | Sequence-space Jacobian toolkit. Used by `idea-prototyper` and `theory-explorer`. |
| `nber-agenda` | Fetch any NBER conference/meeting agenda (titles, authors, discussants, paper links) as text or JSON. NBER agenda pages render client-side; the skill resolves the hidden `conference.nber.org/agenda/simple_printable?conf_id=<ID>` endpoint. Loaded by `literature-scout` and `gap-scout` (pre-publication frontier). Script at `code/utils/nber_agenda/`. |

> **Using `nber-agenda` from this dev repo:** the script is runnable directly without a deployment — `python3 templates/utils/nber_agenda/nber_agenda.py <conference-slug> [--json] [--papers-only]` (e.g. `si-2026-asset-pricing`). Handy for surveying the research frontier or harvesting new technique candidates for skills while working in the template repo.

## Adding a new variant

Adding a variant is mostly **writing one `vocab.json`** — the agent bodies are already shared. There is no per-variant metadata file and no per-variant body directory; both were consolidated away.

1. Create `templates/agents/{variant}/vocab.json` with the per-variant vocabulary keys (scorer calibrations, importance/novelty/surprise rubrics, mechanism term, referee role, etc.) — see `templates/agents/finance/vocab.json` for the full set. Every key referenced by any `{id}-core.md` body must be present in this file or defaulted in `agent_bodies/shared/vocab.json`, or `agent_body_loader.py` raises `KeyError`. If the new domain is not economics, also override the shared-body domain keys (the `_comment_shared_body_overrides` block in `agents/llm_cognition/vocab.json` is the reference list — referee-mechanism frame, literature-agent venues, `POLICY_MAP_AXES`, skill-advice bullets) and add the `MECHANISM_QUALIFIER*` / `MECHANISM_DISCIPLINE` / `DEEPENING_EXTENSION_TYPES` shell vars in the `setup.sh` variant case; leaving them econ-defaulted silently re-opens the domain-slippage failure modes documented in LIMITATIONS.md.
2. Only if the new domain needs genuinely different *structure* (not just different words) from an existing variant agent: add a body override. Variant agent bodies are `templates/agent_bodies/shared/{id}-core.md`, shared across all variants — so edit with care, and prefer a mode overlay (`templates/agent_bodies/shared_modes/`) over forking a body.
3. Register the variant in `templates/agent_metadata/claude_variant_agents.json` only if it needs an agent the other variants don't have — the existing eight (`question-poser`, `question-referee`, `idea-generator`, `idea-reviewer`, `referee`, `scorer`, `self-attacker`, `theory-generator`) are variant-agnostic in metadata and specialize purely through vocab.
4. Add variant config to `setup.sh` (paper type, target journals, journal list, domain areas, `INITIAL_TIER` + the three `TIER_*` descriptor vars) **and** a tier table at `templates/shared/tier_tables/{variant}.md` (the `TIER_TABLE_FILE` lookup is by variant name). Update the two "Available variants" error strings and the usage comment. If the variant's paper *format* differs from the econ working-paper default, drop per-file overrides in `templates/paper_skeleton/{variant}/` (root templates are the fallback) and add any variant-specific section-list / section-guidance blocks via `VARIANT_{NAME}` markers in `docs/stage_5.md` + `paper-writer.md` (see the mode procedure's step 4 for marker semantics; llm_cognition is the reference).
5. Decide extension/mode compatibility explicitly: `--ext empirical` requires an `extensions/empirical/agent_metadata/{variant}_agents.json`; `--mode report` requires a `templates/agents/{variant}_modes/report/vocab.json` overlay *and* domain-appropriate shared audit bodies (see the llm_cognition entry in LIMITATIONS.md for why that variant gates both off in `setup.sh` instead).
6. Test: `./setup.sh /tmp/test_{variant} --variant {variant} --local` — plus a rebuild of the *existing* variants diffed against a pre-change baseline (`--local` output) to prove the new vocab keys changed nothing for them.
7. Document: add a row to the "Supported variants" table in CLAUDE.md and an invocation example + variant note in the `deploy-project` skill.

## Adding a new mode

A *mode* re-frames the pipeline's orchestration (theory-first → identification-first, or another orientation) without forking a variant. It is layered on top of `--variant {finance|macro|...}` via two overlay mechanisms: a vocab overlay (mode-specific overrides to variant vocab keys) and a body overlay (mode-specific shared-agent bodies that replace the base shared body for that mode). The `empirical-first` mode is the reference implementation.

1. **Choose the slug.** Mode flag is `--mode {slug}`; setup.sh lowercases `-` → `_` for directory lookups (`mode_slug="${MODE//-/_}"`). So `--mode foo-bar` looks under `foo_bar/`.
2. **Vocab overlay:** create `templates/agents/{variant}_modes/{mode_slug}/vocab.json` with only the keys whose meaning changes under this mode. Loaded via `candidate_vocab` next to the `mode_slug` assignment and layered on top of the base variant vocab — later wins on duplicate keys. Reference: `templates/agents/finance_modes/empirical_first/vocab.json`.
3. **Body overlay (optional):** create `templates/agent_bodies/shared_modes/{mode_slug}/` with per-agent body overrides. Files are named `{agent_id}-core.md` (variant agent overrides) or `{agent_id}.md` (shared agent overrides) — the loader's suffix discrimination in `load_body` (`scripts/agent_body_loader.py`) handles both. Reference: `templates/agent_bodies/shared_modes/empirical_first/` — all six overrides are `theory-generator-core.md`, `idea-generator-core.md`, `identification-designer-core.md`, `idea-prototyper.md`, `implications-deriver.md`, `referee-mechanism.md`.
3b. **Metadata overlay (optional):** when a mode re-frames what an agent *does* (not just how it phrases things), its orchestrator-facing metadata should match — chiefly `description`, which the orchestrator reads when choosing and prompting agents. Add a `"modes": {"{mode_slug}": {"description": "..."}}` key to the agent's entry in `claude_shared_agents.json` / `claude_variant_agents.json`; any metadata field can be overridden, not just `description`. All four assemblers receive `--mode {mode_slug}` (threaded via `MODE_METADATA_ARGS` in `setup.sh`) and merge the matching overrides over the base fields via `apply_mode_overrides` in `scripts/agent_body_loader.py`; the `"modes"` key itself is always stripped from assembled output, in every mode and in no-mode builds. Reference: the 16 report-mode fan-out agents (report-native descriptions replacing the pipeline-stage ones). Mode-override strings get vocab substitution like base metadata (merge runs before `apply_vocab_to_metadata`).
3c. **Body inject (alternative to a full overlay):** when a mode reuses many pipeline-native agents whose bodies just need re-anchoring (different input/output paths, artifacts that don't exist in this mode), prefer one appended context block over N forked bodies: a `templates/shared/{mode}_inject.md` appended via `inject_block_into_agents` to an explicit agent list, gated on the mode. Reference: `templates/shared/report_mode_inject.md` + `inject_report_mode_into_agents` in `setup.sh` (12 pipeline-native audit agents; the referee trio and `polish-identification` instead carry full report-native body overlays because their *task* changes, not just their paths).
4. **Stage-doc guards (optional):** add `<!-- {MODE}_FIRST_START -->` / `<!-- {MODE}_FIRST_END -->` markers in `templates/shared/docs/*.md` for content that should activate under this mode. The marker resolver (search `EMPIRICAL_FIRST_START` in `setup.sh`) strips the markers under the matching mode and removes the whole block otherwise. A complementary `<!-- THEORY_FIRST_START -->` marker exists for content that should *only* render under the no-mode (theory-first) default. Currently only `EMPIRICAL_FIRST` markers are wired into the resolver; adding a new mode's markers means adding a parallel `else if` branch. The same resolver also handles **variant markers** — `<!-- VARIANT_{NAME}_START/END -->` blocks (name = variant uppercased, e.g. `VARIANT_LLM_COGNITION`) are kept for the matching variant and removed wholesale otherwise, generically: a new variant needs no resolver edit. Use variant markers for *additive* variant-specific blocks in stage docs and shared agent bodies (the llm_cognition Related Work / Experiments / checklist sections in `stage_5.md` + `paper-writer.md` are the reference); use vocab keys when existing text needs different *wording* per variant. Never **interleave** two differently-named marker blocks (`A_START … B_START … A_END … B_END`) — the wholesale-removal regex would leak an orphaned `B_END` into the deployed file; nesting and siblings are both safe. This applies to mode markers too.
5. **Mode-conditional descriptors in setup.sh:** add a `case "$VARIANT"` branch in the `if [ "$MODE" = "{mode}" ]; then` block (search `DOC_SUBTITLE=`) that overrides `PAPER_TYPE`, `DOMAIN_AREAS`, `DOC_SUBTITLE`, and any other variant descriptors the mode reframes.
6. **Validation block in setup.sh:** add the mode to the `case "$MODE" in` validator (search `Unknown mode:`) that decides which `--variant` combinations the mode supports. If the mode implies an extension (as `empirical-first` implies `--ext empirical`), auto-add it with an Info message.
7. **Tests:** `./setup.sh /tmp/test_{mode} --variant {variant} --mode {mode} --local` should resolve cleanly with `✓ All placeholders resolved` and no `{{KEY}}` leakage. Inspect the deployed CLAUDE.md and `.claude/agents/*.md` for marker leakage (`grep -c '{MODE}_FIRST_START'` should be 0).
8. **Document:** add a one-line row to the "Supported modes" table in CLAUDE.md, then write the mode's full semantics (stage/gate changes, pruned agents, cross-variant compatibility nuances, auto-implied extensions, mutual exclusions with other flags) as a `### --mode {slug}` section in the `deploy-project` skill, parallel to the `--mode empirical-first` section there. Add an invocation example to that skill's command block too.

## Adding a new extension — no written procedure (known gap)

Variants and modes have step-by-step procedures above; extensions do not. Nothing has been
written down for adding a third `--ext`, even though the two existing ones establish the shape.

**Failure mode:** an extension added by pattern-matching `extensions/empirical/` will probably
get the agent metadata and bodies right (those are the visible parts) and miss the dispersed
wiring — the `.env` key append, the `EXTENSIONS` dedup guard, the per-mode pruning lists
(`prune_report_mode_agents`, `prune_non_empirical_first_agents`), the deployment-manifest
entries for any new deployed util dir, and the faithful-mode developing-vs-evaluator
categorization that decides which new agents receive the contract pointer. Each of those is
silent when missed: assembly still succeeds, and the defect surfaces at run time or only in
`--faithful` / `--mode report` deployments.

**An extension is not self-contained — `extensions/<ext>/` is only part of it.** Two pieces
live outside that directory entirely:

- **Skills.** There is no `skills/` dir under `extensions/`. An extension's skills live in
  `templates/skill_metadata/<ext>_skills.json` + `templates/skill_bodies/<ext>/`, wired in by
  `scripts/apply_extension_<ext>.sh` — the same place core skills live.
- **Orchestrator injections.** The `*_inject.md` files at the root of `extensions/<ext>/`
  splice extension-specific stages, gates, and `pipeline_state.json` fields into the
  assembled runtime doc (they fill `{{EXTENSION_STAGES}}`,
  `{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}`, `{{EMPIRICAL_STATE_FIELDS}}`,
  `{{EMPIRICAL_LOOP_FIELDS}}` and friends). All eight for empirical: `stages_inject.md`,
  `stage2_rerun_inject.md`, `stage3a_gate_inject.md`, `state_fields_inject.md`,
  `state_loop_fields_inject.md` (the audit-loop counters), `state3a_doc_inject.md`,
  `playbook_inject.md`, `scorer_fertility_inject.md`. An extension whose agents assemble
  correctly but whose injects are missing produces agents the orchestrator never calls.

**Reference implementations:** `extensions/empirical/` (the full-size case: agent metadata +
bodies for shared and both variants, `utils/`, `docs/`, `deps.txt`, and eight `*_inject.md`
fragments) and `extensions/theory_llm/` (the minimal case: shared agents only, `llm_client.py`,
`docs/`, `deps.txt`, five `*_inject.md` fragments).

**To close it:** trace one extension end-to-end through `setup.sh` and write the procedure in
the form used by "Adding a new variant" / "Adding a new mode" above, including a
composability checklist (does the new extension compose with `--manual`, `--mode report`
install-only, `--faithful`, `--light`?).

> Pointers in this file use grep-able anchors rather than line numbers on purpose — the previous line-number references had drifted by hundreds of lines before anyone noticed. If you add a pointer, name a searchable string.
