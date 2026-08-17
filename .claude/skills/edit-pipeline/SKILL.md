---
name: edit-pipeline
description: Reference for editing this template repo itself — repository layout, how setup.sh assembles a deployment, the runtime-agnostic core vs runtime-specific packaging split, the full agent roster and its shared/variant/extension classification, subagent model pinning and fallback/heal, and the step-by-step procedures for adding a new variant, a new mode, an agent, a skill, or a vocab placeholder. Use when modifying setup.sh, update.sh, deploy_assets/ (templates/, extensions/, scripts/), agent metadata or bodies, vocab.json, or fragments — and before adding any new deployed path, agent, or placeholder.
---

# Editing the pipeline template

This repo builds the pipeline; it is not the pipeline. Deployment usage (setup.sh flags, launching a deployed project) lives in the `deploy-project` skill instead.

## Conventions that bite

These four have non-obvious failure modes. Each has a one-line trip-wire in CLAUDE.md (which fires without this skill being loaded) and its mechanism here. Adding a meta-repo dev *skill* is zero-maintenance for deployments — dev skills live outside `deploy_assets/`, so a build never even sees them — but since v2.22.2 the dev skills and CLAUDE.md are mirrored for Codex, and **that** part is not automatic: edit the canonical copy, then run `scripts/sync_dev_instructions.sh`.

### Deployment manifest

Deployment ownership is declared once, at the write site, through `deploy_assets/scripts/setup/ownership.sh`. Template-owned replacement units use `infrastructure_dir`, `infrastructure_copy_file`, `infrastructure_file`, or `infrastructure_optional_file`; those helpers create or verify the output and register it in the same operation. `emit_deployment_manifest` derives `dirs_replace` / `files_replace` only from those registries. There is no second candidate list to maintain (#236).

Mutable project content uses `bootstrap_dir`, `bootstrap_copy_file`, or a plainly visible project-bootstrap write and never enters replacement ownership. `.env` is the one explicit merge-managed bootstrap file (`bootstrap_env_merge` → `files_env_merge`). The distinction is semantic, not "written by setup": `paper/main.tex`, pipeline state, seed material, outputs, and credentials are initialized by setup but owned by the project afterward. Extension appliers inherit the exported registries, so their infrastructure copies use the same helpers. All ownership paths are validated before mutation, including traversal, control characters, symlinks, and non-regular file targets.

Build-time-only paths get **no** registration, because they never ship. Current examples: `VERSION`, `CHANGELOG.md`, every `deploy_assets/scripts/setup/*.sh` module, `deploy_assets/templates/model_fallbacks.json`, the model-remap emitters, `deploy_assets/templates/fragments/`, and the meta-repo dev skills. The test is not "is it new?" but "does a deployed project contain it?"

### Shared rule fragments (`deploy_assets/templates/fragments/*.md`, issue #167)

A load-bearing block of rule text that must read **byte-identically** across many agent bodies (the substance-over-form archetype list, the policy-map axes enumeration, the institutional-acronym citation carve-out, the `irreducible_stochasticity` JSON schema) is single-sourced as a fragment and referenced with a `{{> fragment_id }}` include directive.

`deploy_assets/scripts/agent_body_loader.py` inlines the fragment at assembly time, **before** vocab substitution — so a fragment may itself carry `{{VOCAB_KEY}}` placeholders. The directory is auto-discovered relative to the loader, so every assembler (base + extensions, all five runtimes) shares it with **no** per-call wiring. Build-time only: inlined into deployed agents, never copied out, so no manifest entry.

- Fragment IDs are lowercase (`[a-z0-9][a-z0-9_-]*`). An uppercase ID in a `{{> … }}` directive will **not** match and ships literally.
- Use a fragment only for genuinely byte-identical atoms. Do **not** fragment role-adapted prose that merely looks similar — the copies across scorer / referee / self-attacker / triager are intentionally verb- and verdict-specific, and flattening them changes behavior.
- To verify a fragment migration is zero-behavior-change: assemble before and after (`git stash` the edits) and `diff -rq` the `.claude` / `.codex` / `.gemini` agent dirs. They must be identical.

### Vocab placeholders

Since v2.9.0, **every** body — shared `{id}.md`, variant `{id}-core.md`, and extension bodies — resolves against the same layered vocab chain, later wins: `agent_bodies/shared/vocab.json` (defaults) → `agents/{variant}/vocab.json` (domain overrides) → tier vocab → mode overlay. (The extension appliers layer shared → variant → mode the same way.) When adding a new `{{KEY}}` placeholder anywhere, put its **default** in the shared vocab — or in every variant vocab — then add per-variant overrides only where the domain wording differs. A key defined in only *some* variant vocabs with no shared default breaks setup for the other variants.

`deploy_assets/scripts/agent_body_loader.py` raises `KeyError` on unresolved placeholders — fail-loud is what enforces the rule. Because the layers merge before substitution, a key must live in exactly one *default* home (shared vocab OR all variant vocabs); do not author the same default in both, and never reuse a shared-vocab key name for an unrelated variant concept — the variant value would silently capture every shared-body use of the key.

Two vocab layers are generated at setup time rather than authored: the **tier vocab** (`TIER_VOCAB_FILE` in `setup.sh` — `TIER_LIST_INLINE` / `TIER_LADDER_PROSE` resolved by `_setup_config_resolve_variant_descriptors` in `deploy_assets/scripts/setup/resolve_config.sh`, then passed to every base assembler so bodies like `editor.md` can name the variant's tier ladder), and the mode overlays.

Domain wording extracted from previously hardcoded economics prose lives in two override blocks: `_comment_domain_phrases` in each variant vocab (for the `-core` bodies — scorer tier bands, `FORCE_TERM`, referee exemplars, self-attacker archetype examples) and `_comment_shared_body_overrides` in `agents/llm_cognition/vocab.json` (for shared bodies and fragments — referee-mechanism's evaluative frame, literature-agent venue directives, `POLICY_MAP_AXES`, the ssj/nber-agenda advice bullets), with the matching defaults in the shared vocab's `_comment_domain_defaults` block. When editing any body, prefer extending these keys over re-hardcoding domain language; the econ defaults must stay byte-identical to the pre-extraction text unless a behavior change is intended (verify with a before/after `--assemble-only` build diff of finance and macro).

### Meta-repo dev skills

`.claude/skills/` is tracked in this repo (it is **not** gitignored, unlike `.claude/agents/`) and lives **outside** `deploy_assets/`, so a build never sees it: since v2.23.0 (#232) `setup.sh` assembles a deployed project's skills from `deploy_assets/templates/skill_bodies/` into an empty project directory. There is no strip/snapshot machinery anymore — the v2.22.x `DEV_SKILLS` checksum guard and the `.agents/skills` early strip were deleted with the clone-then-strip flow, and a `skill_id` colliding with a dev-skill directory name is no longer a hazard (the dev tree and the assembly destination never coexist). **Adding a new dev skill requires no `setup.sh` edit** — it does require a sync run (next paragraph).

**The Codex mirror (v2.22.2).** Codex loads `AGENTS.md` automatically and discovers repo skills under `.agents/skills`, so the meta-repo mirrors both: `AGENTS.md` is a generated copy of `CLAUDE.md`, and `.agents/skills/{name}` is a relative symlink to `../../.claude/skills/{name}`. `CLAUDE.md` and `.claude/skills/` are canonical — edit those, then run `scripts/sync_dev_instructions.sh`. Never hand-edit a mirror. Under `.agents/skills` the script refuses to overwrite any entry that does not already point at that skill's canonical directory — being a symlink does not exempt it, since a foreign link at a colliding name is as much someone else's content as a foreign file is. (The one thing it *does* rewrite is the plain file git leaves when symlinks are unavailable, and only once the content proves it is that skill's own link.) An edit to `AGENTS.md`, by contrast, is simply lost on the next sync.

**The clean-checkout guard (#233).** `.github/workflows/dev-instruction-sync.yml` runs the generator on every pull request and push to `main`, force-stages only `AGENTS.md` and `.agents/skills`, and fails if those generated paths differ from the proposed commit. Running in a fresh checkout is deliberate: it compares the commit with the generator's actual output without reproducing the working-tree/index/ignore-state logic that made the discarded pre-commit checker repeatedly report false PASSes. The workflow also runs the mirror regression suite before checking the live tree. It blocks merges only when its status is required by GitHub branch protection; without that setting, a direct push is detected after it lands.

The developer workflow does not change: edit `CLAUDE.md` or `.claude/skills/`, run `scripts/sync_dev_instructions.sh`, and commit the generated mirrors with their canonical sources. Adding a dev skill still needs no `setup.sh` edit, but it does need that sync run.

Constraints that still shape the mirror, none arbitrary:

- **Link the folder, never the file.** Codex follows a symlinked skill *directory* — the maintainer on openai/codex#11314: *"Codex does support symlinking the `/.agents/skills` directory (both global and per-project)… We even have unit tests in place."* Symlinking `SKILL.md` itself is genuinely unsupported (openai/codex#9365 — *"We support symlinks to a skill directory, not the SKILL.md file itself"*).
- **Get the relative depth right; wrong is silent.** A link at `.agents/skills/{name}` resolves its first `..` to `.agents/`, so the target is `../../.claude/skills/{name}`. openai/codex#11314 was closed *not planned* because it was never a bug — the reporter's symlink simply had an invalid relative target. Note also that Codex's live-reload file watcher does not fire through a symlink, so edits to a canonical `SKILL.md` appear only after relaunching the Codex CLI.
- **`AGENTS.md` is a copy, never a symlink to `CLAUDE.md`.** `sync_dev_instructions.sh` regenerates it wholesale; through a symlink that regeneration would overwrite the canonical `CLAUDE.md` instead. (The old clone-then-strip flow had a second, harder reason — `setup.sh` used to write both files inside a clone that carried the dev mirror — but deployments no longer contain the dev mirrors at all.)
- **Codex skill frontmatter must satisfy the complete bundled authoring validator.** The source of truth is `codex-rs/skills/src/assets/samples/skill-creator/scripts/quick_validate.py`: only `name`, `description`, `license`, `allowed-tools`, and `metadata` are allowed; `name` and `description` are required strings; names are lowercase hyphen-case with no edge/doubled hyphens; `name` is capped at 64 characters; `description` is capped at 1024 characters and may contain neither `<` nor `>`. Both caps count Unicode characters, not UTF-8 bytes. `deploy_assets/scripts/codex_skill_validation.py` mirrors those rules once and is called by both `sync_dev_instructions.sh` and `assemble_codex_skills.py`; it also retains this repository's stricter non-empty-field requirement (the runtime requires a non-empty description and otherwise derives a fallback name). The current runtime loader is more permissive than the authoring contract for overlong or angle-bracketed descriptions, but generated skills must not rely on that implementation detail. A separate aggregate skills-metadata budget across all rendered descriptions also truncates — and it is **tokens**, not characters: `skill_metadata_budget()` returns `SkillMetadataBudget::Tokens(2% of context window)`, falling back to `Characters` only when the context window is unknown, so openai/codex#24299's `budget_limit=5440` is `272_000 × 2%` tokens. It depends on the model and on what else is installed, so it is not checked.
- **In a deployed project, `.agents/skills` is a real directory, freshly created** by `assemble_codex_skills.py` and manifest-managed (`CODEX_SKILLS_REL`, i.e. `$CODEX_DIR_REL/skills`). The dev repo's symlinked entries never enter a build, so the old write-through-the-link collision hazard (and the early strip that guarded it) is gone.

Both mirrors are dev-only and get **no** manifest entry.

### Dev settings vs deployed settings

This repo's `.claude/settings.json` configures the **template-development** session and ships
nowhere. The settings a deployed project runs under — including the sandbox profile — live in
`deploy_assets/templates/runtime/{claude,gemini}/settings.json` and are installed by the
`setup_runtime_documents` function in `deploy_assets/scripts/setup/runtime_documents.sh`,
which runs for both `--assemble-only` and production and is the only writer of those paths (the
project directory starts empty).

Keep the two apart. They want opposite things: the template repo needs a permissive posture
(it deploys projects into arbitrary paths), a research project wants the sandbox on. A single
dual-role file at the repo root cannot be both, which is exactly what it used to be.

Sandbox config is per-runtime and lives in three different shapes: Claude's `.claude/settings.json`
(copied from templates), Gemini's `.gemini/settings.json` (copied), and Grok's `.grok/sandbox.toml`
(**generated** per-deploy, because grok's TOML does not expand `~`/`$HOME` and needs the deploying
user's absolute paths baked in). Codex takes its sandbox posture from `launch.sh` flags, not a file.

## Repository structure

> This tree is a **snapshot** and has drifted before. `deploy_assets/scripts/` and the top level of
> `deploy_assets/templates/` and `deploy_assets/extensions/*/` are complete. Everything nested deeper —
> `skill_metadata/`, `skill_bodies/`, `agent_bodies/`, `utils/`, `shared/docs/` — is
> illustrative, not exhaustive. When it matters, `ls` the directory rather than trusting
> the diagram.

```
deploy_assets/templates/
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
│   │                        #  .grok/sandbox.toml is generated per-deploy by base_agents.sh)
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
│   │                        # model_heal/,
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
│   ├── llm_cognition/vocab.json
│   └── llm_cognition_modes/       # report/ (v2.16.0) + measurement_first/ (v2.17.0)
└── gitignore_project        # .gitignore template for deployed projects

deploy_assets/scripts/
├── setup/
│   ├── resolve_config.sh          # CLI validation + variant/mode/extension resolution
│   ├── ownership.sh               # Infrastructure/bootstrap boundary + derived manifest
│   ├── runtime_documents.sh       # Mode overlays, runtime settings, catalogs, runtime docs
│   ├── base_agents.sh             # Five-runtime base/variant agents + model fallback resolution
│   ├── extensions_and_injections.sh # Agent pruning/injects + optional extensions + final remap
│   ├── project_bootstrap.sh       # Mutable structure/state/seed/.env initialization
│   ├── infrastructure_docs.sh     # Template-owned stage-document installation
│   ├── skills_and_utilities.sh    # Core skills/utilities + launch-time heal
│   ├── provisioning.sh            # Host-local venv + core/SSJ/extension dependencies
│   └── finalization.sh            # Git init/commit, opt-in publish, completion output
├── assemble_claude_agents.py   # Combines agent metadata + bodies → .claude/agents/*.md
├── assemble_claude_skills.py   # Combines skill metadata + skill bodies → .claude/skills/*/SKILL.md
├── assemble_codex_skills.py    # Combines skill metadata + skill bodies → .agents/skills/*/SKILL.md
├── codex_skill_validation.py   # Shared complete Codex skill-authoring validator (build-time only)
├── assemble_codex_subagents.py # Combines agent metadata + bodies → .codex/agents/*.toml
├── assemble_gemini_agents.py   # Combines agent metadata + bodies → .gemini/agents/*.md
├── assemble_grok_agents.py     # Combines agent metadata + bodies → .grok/agents/*.md
├── assemble_opencode_agents.py # Combines agent metadata + bodies → .opencode/agents/*.md
├── assemble_runtime_doc.py     # Builds CLAUDE.md / AGENTS.md / GEMINI.md from core + session
├── agent_body_loader.py        # Resolves bodies ({id}.md vs {id}-core.md), fragments, vocab
├── test_agent_body_loader.py   # Tests for the loader
├── test_launch_opencode.sh     # Tests launch.sh's opencode server/quiescence driver
├── test_assemble_codex_subagents.py # Deterministic native-role/config/protocol tests
├── test_codex_native_live.sh   # Opt-in credentialed native-role lifecycle canary
├── list_agents_by_category.py  # Source of truth for the developing/evaluator split
├── generate_catalog.py         # Manual mode: emits agent/skill catalog markdown from metadata
├── apply_extension_empirical.sh    # Wires the empirical extension into a deployment
├── apply_extension_theory_llm.sh   # Wires the theory_llm extension into a deployment
├── resolve_model_fallbacks.py  # Probes model availability (build-time only)
├── apply_model_remap.py        # Rewrites model: frontmatter post-assembly (build-time only)
└── emit_model_heal_config.py   # Emits code/utils/model_heal/config.json (build-time only)

deploy_assets/extensions/                  # Optional extensions (empirical, theory_llm)
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

deploy_assets/launch.sh      # Runtime launcher, shipped verbatim into every deployment
deploy_assets/dashboard.html # Live progress dashboard, shipped verbatim (pipeline modes only)

setup.sh                     # Repo root. Assembles from this checkout into an empty project dir
update.sh                    # Repo root. Refreshes deployed projects from a fresh --assemble-only build
scripts/                     # Repo root: dev-only tooling (sync_dev_instructions.sh) — NOT build input
test_scripts/                # Repo root: skill verification scripts, dev-only
```

`deploy_assets/` is the complete deployable-asset tree (templates/, scripts/,
extensions/, plus the verbatim-shipped `launch.sh` and `dashboard.html`). The root
coordinator additionally reads root `setup.sh`, `VERSION` for stamping, `LICENSE`
for production bootstrap, and `.env.example` to seed deployed configuration. Root
`.env` is separate operator configuration and is not a build input. Dev-only tooling
stays at the repo root and is never read by a build.

## Architecture: runtime-agnostic core + runtime-specific packaging

The pipeline is split into two layers:

- **Runtime-agnostic**: `deploy_assets/templates/shared/core.md` (orchestrator logic, pipeline stages), `deploy_assets/templates/agent_bodies/shared/` and `deploy_assets/templates/agents/{variant}/vocab.json` (agent prompts and per-variant vocab including scorer calibrations) — these are the same regardless of runtime.
- **Runtime-specific**: session guidance under `deploy_assets/templates/runtime/`, shared metadata with per-runtime overrides, and `deploy_assets/scripts/assemble_{claude_agents,codex_subagents,gemini_agents,grok_agents,opencode_agents}.py`.

**Five** runtimes share the same core + agent bodies: Claude, Codex, Gemini, Grok, and OpenCode. Grok and OpenCode read the shared `AGENTS.md`; their generated agents live in `.grok/agents/*.md` and `.opencode/agents/*.md`. Every base/variant agent change has five assembly call sites. Extension appliers currently cover Claude, Codex, Gemini, and OpenCode; Grok extension agents remain a documented gap.

## How setup.sh works

Root `setup.sh` is an isolated Python launcher; the fail-fast Bash coordinator is `deploy_assets/scripts/setup/coordinator.sh`. Build behavior lives behind explicit sourced-module interfaces under `deploy_assets/scripts/setup/`; the modules are build-time-only and never enter a deployment.

1. Root `setup.sh` always starts outside Bash through the absolute OS interpreter (`/usr/bin/python3 -I`), never a caller/venv `PATH` selection, removes `BASH_ENV`, exported functions, inherited shell options, shell path-control variables, activated-environment state, and ambient Git repository/object/index/config overrides, then executes `deploy_assets/scripts/setup/coordinator.sh` in a sanitized Bash environment. Core setup commands resolve from system directories first; the launcher selects operator `uv`, `claude`, and `gh` providers independently by exact executable path, skipping checkout/active-environment paths and their symlink or case aliases. Before sourcing any build-input module, the coordinator fixes `SOURCE_CHECKOUT_ROOT` to the checkout containing `setup.sh`, captures a deterministic content + permission-mode digest of `setup.sh`, `VERSION`, `LICENSE`, `.env.example`, and `deploy_assets/`, copies exactly those inputs into a private local snapshot, and verifies both snapshot and live checkout against the baseline. The outer coordinator then executes the snapshot's own isolated launcher/coordinator pair through a validated internal handoff; output-affecting coordinator code and every module/asset are therefore consumed through snapshot-backed `SRC_ROOT`/`TEMPLATE_ROOT`, so an atomic replacement of the live coordinator or a live change that is later restored cannot leak into output under mismatched provenance. Containment uses filesystem identity rather than case-sensitive path spelling, and symlink build inputs fail closed rather than importing bytes from outside the checkout. Embedded Python runs with `-I`; ambient import-path controls are cleared; and local assembler imports use a private temporary bytecode prefix, so ignored checkout caches and caller-CWD modules cannot become undeclared executable inputs. In a Git checkout, effective files/directories are compared directly to the initially recorded source commit, so assume-unchanged flags and ignore/exclude rules cannot hide consumed bytes; a config-neutral `ls-files` read separately verifies index health without executing ambient fsmonitor/filter code. `resolve_config.sh` then parses and validates the CLI, expands legacy/implied extensions, preserves and deduplicates extension order, and resolves variant/mode descriptors. Unknown-extension rejection remains at the historical extension boundary so diagnostics and sequencing do not change.
2. The live capture phase installs an EXIT trap for early failures, then transfers snapshot cleanup to a fixed wrapper when it executes the pinned coordinator. The inner snapshot phase owns later cache, tier-vocab, catalog, and ownership temporary state with its own shared EXIT trap. Setup never fetches/clones source. A full deployment requires clean, committed build inputs and fails closed if Git cannot inspect their status; `--assemble-only` requires an explicit destination and permits dirty development state. Both assemble into an empty output directory, and final snapshot + live digest/HEAD checks reject persistent concurrent changes. `.env.example` is an input because it seeds deployed configuration, while `.env` is operator configuration and excluded from source cleanliness/provenance hashing.
3. `finalization.sh:setup_initialize_project_git` initializes only the production project's repository through an empty private Git template and hook/attribute/fsmonitor-neutral command wrapper; ambient `GIT_TEMPLATE_DIR`, global hooks, filters, fsmonitor hooks, and commit signing cannot execute after source verification. `ownership.sh:setup_ownership_init` then creates the structural ownership registries. Root infrastructure copies use `infrastructure_copy_file`; this includes verified update/provisioning inputs under `.arpipeline/update_inputs/` (dependency specifications plus the dotenv guard). `LICENSE` uses `bootstrap_copy_file`.
4. `runtime_documents.sh:setup_runtime_documents` resolves mode overlays, installs runtime settings, and assembles CLAUDE.md, AGENTS.md, GEMINI.md, and session documents from the runtime-agnostic core plus runtime-specific guidance.
5. `base_agents.sh:setup_base_agents` resolves Claude fallbacks and assembles shared + variant agents across all five runtimes. `extensions_and_injections.sh:setup_core_agent_injections_and_pruning` then applies core flag/mode pruning and context injection.
6. `project_bootstrap.sh` initializes mutable project structure, paper skeletons, fingerprint/state/log files, seed material, and `.env`. `infrastructure_docs.sh` installs template-owned stage documents between the bootstrap phases, preserving the historical producer order. Bootstrap outputs never enter replacement ownership; `.env` alone is registered for merge.
7. `provisioning.sh:setup_python_environment` creates the production-only `.venv`, installs core dependencies, and installs the dotenv guard from those manifest-owned verified inputs. `skills_and_utilities.sh:setup_skills_and_utilities` assembles core skills/utilities and invokes the same provisioning module for variant-gated SSJ dependencies. Root `update.sh` first enters its distinct coordinator through an isolated `/usr/bin/python3 -I` launcher that removes Bash startup hooks, exported functions, and active virtual/Conda environment paths. Its coordinator pins `uv` only after the full project/template/temp/cache control-PATH filter. It rejects targets at/above its template checkout or inside `deploy_assets/` before mutation, reads only the fresh assembly's `.arpipeline/update_inputs/`, never post-assembly live source bytes, and removes any newly created empty control directories on exit. Every supported deployed `launch.sh` keeps a shared `fcntl` lock on a parent-Bash-owned project-directory descriptor for the runtime lifetime; update acquires the exclusive side before creating any target path. The trusted parent waits while the complete runtime/update body executes in a child subshell with the descriptor closed, so descendants can neither unlock nor leak it. Live legacy OpenCode is also refused; validation/replacement is quiescent against supported agents without a pathname lock, holder process, or readiness file. Non-launcher same-UID writers remain the documented #259 boundary. Compatible pre-launch autonomous mode/extension overrides recursively merge their missing state schema and output-directory skeleton from the verified fresh assembly; same-layout manual/report extension refreshes need only managed infrastructure. Seed/faithful overrides prepare no-follow seed bootstrap content. The journal rolls prepared content back on update failure and commits pipeline state only at the final manifest boundary; a started autonomous run rejects every mode/extension/seed route change. Cross-variant, autonomous↔manual, and report↔autonomous layout changes require a fresh deployment.
8. `extensions_and_injections.sh:setup_extensions_injections_and_pruning` applies extensions in resolved user order, assembles their agents/skills/utilities/docs, appends bootstrap `.env` keys, calls `provision_extension_dependencies` once per extension, performs extension pruning/injections, resolves markers, and applies the final Claude model remap. Extension appliers use the exported ownership registries for their infrastructure writes.
9. `ownership.sh:emit_deployment_manifest` derives the replacement and merge lists from the producer registries; there is no hand-maintained candidate list. It also records checkout provenance (sanitized repository, commit, dirty state, deterministic build-input digest, and `update_channel=checkout`) plus every replayed deployment selector, including faithful independently from seeded. The exact historical array order is retained through numeric compatibility order plus lexical tie-breaking.
10. `finalization.sh` validates assembly-only placeholder resolution and reports the output, or, in a full deployment, finalizes the dashboard, commits the initial project, performs GitHub publication only under explicit `--publish`, and prints launch instructions. On exit, the inner phase trap removes its cache/catalog/ownership state and the fixed outer wrapper removes the source snapshot.

The full 39-shape characterization fixture in `test_scripts/test_setup_characterization.py` compares complete trees, file modes, empty directories, symlinks, manifests, and CLI contracts. `test_setup_source_policy.sh` covers checkout-only source selection, clean-input enforcement, and provenance. `test_setup_ownership.sh` covers update preservation and adversarial ownership paths; `test_setup_publish.sh` exercises a committed checkout, provisioning order, git commit, and every publish-safety branch with fake `uv`/`gh`.

## Agent classification

Agents are either **shared** (identical across variants) or **variant-specific** (one body, specialized per domain by vocab substitution). Each agent is defined as:
- **Metadata**: `agent_metadata/claude_shared_agents.json` (shared agents) or `agent_metadata/claude_variant_agents.json` (variant agents — a single file covering every variant, *not* one file per variant). Claude frontmatter plus Codex and Gemini overrides, and a `category` field (`developing` / `evaluator`) that drives faithful-mode injection.
- **Body**: `agent_bodies/shared/{id}.md` for shared agents, `agent_bodies/shared/{id}-core.md` for variant agents. Both live in the same directory — the `-core` suffix is what marks a body as variant-specialized, and `deploy_assets/scripts/agent_body_loader.py` (`load_body`) tries `{id}-core.md` first, then `{id}.md`. `deploy_assets/templates/agents/{variant}/` holds **only** `vocab.json`; no agent bodies live there.
- **Vocab**: *both* kinds get placeholder substitution, and since v2.9.0 both resolve against the same layered chain: `agent_bodies/shared/vocab.json` (defaults) → `agents/{variant}/vocab.json` (domain overrides) → tier vocab → mode overlay, later wins. So a `{{KEY}}` added to *any* body or fragment needs a default in the shared vocab (or in every variant vocab); variant vocabs override only where the domain wording differs. This layering is what makes shared bodies (referee-mechanism's evaluative frame, the literature agents' venue directives, the fragments) variant-aware — see the `_comment_shared_body_overrides` block in `agents/llm_cognition/vocab.json` for the full override set.

**Shared** (domain-agnostic, receive variant context via injection). All 33 live in `claude_shared_agents.json`; the authoritative list is that file, and `python3 deploy_assets/scripts/list_agents_by_category.py` prints current membership by category.

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
- `report-reviewer` — `--mode report` only: independently gates the synthesized report and writes a versioned `process_log/report_self_review_r{N}.md` CLEAN/FIX artifact
- `table-auditor` — independent rendered-page evaluator at Stage 5 and after final polish; gates native/custom/image-table legibility after the source-level `arpipeline.sty` checks

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
- `branch-manager` — strategic advisor at unseeded Gate 4 + Stage 2 audit loop (every 3rd theory version); diagnoses ceiling/alternatives. Seeded Gate 4 skips it because the research direction is fixed. Pinned `fable`
- `last-resort` — general-purpose escalation for stubborn problems; launched at orchestrator discretion (no auto-trigger) when normal escalation is exhausted and the alternative is abandonment. Pinned `fable`, broad tool access; receives full failure history; returns `FIX-PROPOSED` (re-verified by the existing gate — never self-certifies) or `GENUINELY-STUCK`. Visible in the manual-mode catalog; pruned in `--mode report`
- `debugger` — launched when a computational or retrieval tool (solver, regression, symbolic verifier, literature/data query, compiler) has failed; determines whether the failure is the tool or the input
- `faithful-drift-auditor` — `--faithful` only: independent contribution-drift check at Gate 4 (before advancing to Stage 5) and Gate 5 (before ship)
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
- `mechanism-auditor` — plan-time mechanism-plausibility gate at empirical-first Gate 2 (Stage 2, before any empirical execution); runs the data-independent dimensions of the `referee-mechanism` checklist against the prose+DAG mechanism + Stage 1 identification design; returns PLAUSIBLE / REVISE (shared body, `--ext empirical`; **assembled then pruned in every mode except `--mode empirical-first`** via `_setup_extensions_prune_non_empirical_first_agents` in `extensions_and_injections.sh`)
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

If that model is unavailable on the account at setup time (a provider suspension — as happened when Claude Fable 5 / Mythos 5 were suspended by US export-control directive on 2026-06-12 — or simply no access), a pinned subagent would **hard-fail at launch with no fallback** (the Task tool returns "<model> is currently unavailable"; it does **not** silently downgrade to another model). To prevent that, `setup_base_agents` in `deploy_assets/scripts/setup/base_agents.sh` resolves models at assembly time:

- **Probe** (`deploy_assets/scripts/resolve_model_fallbacks.py`): for each distinct model pinned across the Claude agent metadata, run the *same* `claude` CLI that will run the agents (`claude -p --model <id>`) and classify by output content (the unavailable message returns rc=0, so detection is by marker string `"is currently unavailable"` / the fable-mythos-access URL, not exit code). Runtime-accurate by construction — an API-key probe can disagree with the CLI's account access.
- **Fallback chains** (`deploy_assets/templates/model_fallbacks.json`): each model maps to an ordered chain (`fable → opus → sonnet`, etc.). An unavailable model is remapped to the first chain entry that is not itself unavailable.
- **Apply** (`deploy_assets/scripts/apply_model_remap.py`): a single post-assembly pass rewrites the `model:` frontmatter in every assembled `.claude/agents/*.md` (base + variant + every extension), so one pass covers all agents without threading remap args through each assembler call site.
- **Self-healing:** because metadata declares the *ideal* model, when a suspended model is restored the probe passes and no remap is applied — new deployments use the ideal again with no template edit.
- **Launch-time re-heal (Claude only):** the build-time remap runs *once* and cannot reach an already-deployed project whose tier goes down (or recovers) *after* setup. `./launch.sh claude` therefore re-decides each agent's tier at every launch via the **deployed** `code/utils/model_heal/heal_agent_models.py` + `config.json` — restoring the ideal when it recovers and falling back when it's down, in both directions. `config.json` records each agent's *ideal* model (emitted at build time by `deploy_assets/scripts/emit_model_heal_config.py`, keyed by `.md` stem, variant-scoped) because the deployed `.md` only carries the current, possibly-remapped pin. Best-effort: an inconclusive probe leaves pins untouched and never blocks a launch (`set -euo pipefail`-safe guard in `launch.sh`). Codex/Gemini/Grok have no launch-heal — see `docs/model_fallback.md`.
- **Flags / safety net:** `--no-model-probe` skips the live probe (CI / offline) and relies on a static known-unavailable list (`fable,mythos,...`), which also catches the known suspension when the launcher cannot select a safe `claude` executable. The launcher passes that exact executable to the isolated resolver rather than placing its directory ahead of setup's control tools. The list is the `--known-unavailable` argument in `setup_base_agents`; update it if a new model is suspended and you can't probe.

**Codex tier mirrors the Claude tier.** Each agent's `codex.model` is the same capability tier as its Claude `model`, one-for-one: `fable → gpt-5.6-sol`, `opus → gpt-5.6-terra`, `sonnet → gpt-5.6-luna`. (OpenAI describes Sol/Terra/Luna as *durable capability tiers* that advance on their own cadence, so the mapping survives the next generation bump — only the `5.6` changes.) When you add an agent, pin both, and pin them to matching tiers; a `fable` agent whose codex twin is Terra is a silent cross-runtime capability mismatch, not a build error.

**Codex model/effort pins take effect through native custom roles (codex-cli 0.147.0+).** Production uses exactly MultiAgent V2: the orchestrator calls native `spawn_agent` with `agent_type` equal to the `.codex/agents/{id}.toml` role, a unique `task_name`, and `fork_turns="none"`. Do not fall back to the incompatible V1 schema if any field is missing. `launch.sh` pins the parent to `features.multi_agent_v2=true` even in interactive `--once` sessions, so ordinary user config cannot remove its role tool surface and `--light` Luna keeps the same V2 task/wait schema. Codex 0.147 exposes `agent_type` in V2 whenever project roles are loaded; its default hidden-metadata option removes service-tier/output metadata, not the role selector, and overriding that default breaks the provider-reserved tool schema. The role file's `model` and `model_reasoning_effort` override the parent. `assemble_codex_subagents.py` also emits `project_doc_max_bytes = 0`, `[features.multi_agent_v2] enabled = false`, and `[agents] enabled = false`, so the child omits the orchestrator AGENTS.md and remains a leaf against parent/session and ordinary user-config overrides. `launch.sh` uses `--ignore-user-config` for deterministic headless sessions and restores trust for exactly the physical project through a command-line `projects={...}` override; project roles are otherwise silently undiscoverable. Empirical session metadata verified `agent_type=scorer` on Terra/high with the scorer developer instructions and zero parent/AGENTS context despite a hostile parent V2 session override. Legacy managed_config/MDM layers can override the SessionFlags role, while separate enterprise/system feature requirements can force V2 despite `agents.enabled=false`; both are explicit #240 residuals in `LIMITATIONS.md`. Native children are process-resident: the parent must wait to terminal status and validate the artifact before ending its turn, because primary `codex exec` completion shuts down and interrupts live children. See the Codex native-subagent entry in `LIMITATIONS.md` for crash/timeout recovery. (Claude, Gemini, Grok, and OpenCode keep their own native dispatch mechanisms.)

**Reasoning effort is capped at `high`.** gpt-5.6 also accepts `xhigh` and `max` (plus `ultra`, a four-agent parallel mode), and nothing in the pipeline uses them. On Agents' Last Exam — the long-horizon agentic benchmark whose shape most resembles this pipeline — GPT-5.6 Sol's score *peaks below its top effort setting*: the most expensive point on the cost curve scores below the one preceding it. Effort past `high` buys latency and tokens, not correctness. This is a claim about *our workload*, not about `max` in general (on ARC-AGI-3, `max` is the only setting that scores at all), so do not generalize it to a future benchmark without rechecking. The `codex_math` scripts reject `xhigh`/`max`/`ultra` at the CLI boundary.

**`--light` also pins the orchestrator (v2.19.0).** The subagent pinning below happens at assembly time; the orchestrator is launched by `launch.sh`, which pins it separately (`--model` for claude/gemini, `-c model="…"` for codex — `codex exec resume` accepts only the config form, and the driver resumes every turn after the first). `light_orchestrator_model` in `launch.sh` **reads the tier back from the assembled agents** instead of carrying a fourth copy of the tier table: it fires only when `.deploy_manifest.json` has `flags.light` and every assembled agent agrees on one model, so it tracks the assemblers automatically and cannot drift from them. Grok's branch never calls it (single-model table, and its roster is uniform in *every* deployment — which is exactly why the manifest check, not roster uniformity alone, is the trigger). When you add a runtime, its launch branch is a call site.

**`--light` reaches every runtime.** `MODEL_OVERRIDE_ARGS` in `setup.sh` is consumed by all five base assemblers in `base_agents.sh`; extension appliers receive the matching light-model argument from `extensions_and_injections.sh`. each maps the Claude alias through its tier table. Claude, Codex, and Gemini select their cheap tiers. Grok and OpenCode each expose one configured model, so the override is a no-op for them. Base and variant assembly have five call sites; extension assembly covers Claude, Codex, Gemini, and OpenCode, with Grok's missing extension path documented in `LIMITATIONS.md`.

**Known limitation (documented, not solved):** only **Claude** subagent models are probed/remapped. Codex (`gpt-5.6-{sol,terra,luna}`) and Gemini (`gemini-3-preview`) subagents use a different provider/CLI; their availability is not checked. If an OpenAI/Google model used by the codex/gemini runtimes is withdrawn, those agents would hard-fail the same way — closing that would require per-provider probes (an `openai`/`gemini` CLI check) and provider-specific fallback chains. The `model_fallbacks.json` schema and the resolver/apply split are already provider-agnostic; what's missing is the per-runtime probe command and wiring the apply pass over `.codex/agents` / `.gemini/agents`.

These four paths (`deploy_assets/templates/model_fallbacks.json`, `deploy_assets/scripts/resolve_model_fallbacks.py`, `deploy_assets/scripts/apply_model_remap.py`, `deploy_assets/scripts/emit_model_heal_config.py`) are **build-time only** — used during `setup.sh`, never copied into deployed projects — so they are intentionally absent from the deployment manifest. The launch-time heal is the exception that proves the rule: its script (`deploy_assets/templates/utils/model_heal/heal_agent_models.py`) and generated `config.json` **are** deployed (to `code/utils/model_heal/`) and registered together through `infrastructure_dir`, precisely because they must run at every launch, not just at setup.

## Core skills (all variants)

Four skills install unconditionally for every variant (`sympy`, `codex-math`, `bib-verify`, `openalex`); `ssj` and `nber-agenda` are **variant-gated** (issue #205). `codex-math` is absent from `.agents/skills` to prevent Codex self-reference, but OpenCode deliberately consumes the complete `.claude/skills` tree and therefore can use it. When retiring any deployed path, the update sweep can remove it only if it was manifested.

| Skill | Description |
|-------|-------------|
| `sympy` | Symbolic math — the workhorse for derivations and verification. Used by 6+ core agents. |
| `codex-math` | OpenAI Codex (gpt-5.6-sol) for proof verification, writing, and exploration. Scripts at `code/utils/codex_math/`. Available to Claude and OpenCode; excluded from Codex to prevent self-reference. |
| `bib-verify` | Bibliography verification — the tool behind the `bib-verifier` agent. |
| `openalex` | OpenAlex literature queries. Used by `literature-scout`, `gap-scout`, `novelty-checker`, all three referees (`referee`, `referee-freeform`, `referee-mechanism`), `polish-institutions`, `polish-bibliography`. |
| `ssj` | Sequence-space Jacobian toolkit. Used by `idea-prototyper` and `theory-explorer`. |
| `nber-agenda` | Fetch any NBER conference/meeting agenda (titles, authors, discussants, paper links) as text or JSON. NBER agenda pages render client-side; the skill resolves the hidden `conference.nber.org/agenda/simple_printable?conf_id=<ID>` endpoint. Loaded by `literature-scout` and `gap-scout` (pre-publication frontier). Script at `code/utils/nber_agenda/`. |

> **Using `nber-agenda` from this dev repo:** the script is runnable directly without a deployment — `python3 deploy_assets/templates/utils/nber_agenda/nber_agenda.py <conference-slug> [--json] [--papers-only]` (e.g. `si-2026-asset-pricing`). Handy for surveying the research frontier or harvesting new technique candidates for skills while working in the template repo.

## Adding a new variant

Adding a variant is mostly **writing one `vocab.json`** — the agent bodies are already shared. There is no per-variant metadata file and no per-variant body directory; both were consolidated away.

1. Create `deploy_assets/templates/agents/{variant}/vocab.json` with the per-variant vocabulary keys (scorer calibrations, importance/novelty/surprise rubrics, mechanism term, referee role, etc.) — see `deploy_assets/templates/agents/finance/vocab.json` for the full set. Every key referenced by any `{id}-core.md` body must be present in this file or defaulted in `deploy_assets/templates/agent_bodies/shared/vocab.json`, or `agent_body_loader.py` raises `KeyError`. If the new domain is not economics, also override the shared-body domain keys (the `_comment_shared_body_overrides` block in `agents/llm_cognition/vocab.json` is the reference list — referee-mechanism frame, literature-agent venues, `POLICY_MAP_AXES`, skill-advice bullets) and add the `MECHANISM_QUALIFIER*` / `MECHANISM_DISCIPLINE` / `DEEPENING_EXTENSION_TYPES` shell vars in `_setup_config_resolve_variant_descriptors` (`deploy_assets/scripts/setup/resolve_config.sh`); leaving them econ-defaulted silently re-opens the domain-slippage failure modes documented in LIMITATIONS.md.
2. Only if the new domain needs genuinely different *structure* (not just different words) from an existing variant agent: add a body override. Variant agent bodies are `deploy_assets/templates/agent_bodies/shared/{id}-core.md`, shared across all variants — so edit with care, and prefer a mode overlay (`deploy_assets/templates/agent_bodies/shared_modes/`) over forking a body.
3. Register the variant in `deploy_assets/templates/agent_metadata/claude_variant_agents.json` only if it needs an agent the other variants don't have — the existing eight (`question-poser`, `question-referee`, `idea-generator`, `idea-reviewer`, `referee`, `scorer`, `self-attacker`, `theory-generator`) are variant-agnostic in metadata and specialize purely through vocab.
4. Add variant config to `_setup_config_resolve_variant_descriptors` in `deploy_assets/scripts/setup/resolve_config.sh` (paper type, target journals, journal list, domain areas, `INITIAL_TIER` + the three `TIER_*` descriptor vars) **and** a tier table at `deploy_assets/templates/shared/tier_tables/{variant}.md` (the `TIER_TABLE_FILE` lookup is by variant name). Update the module's "Available variants" diagnostics and its `usage` text. If the variant's paper *format* differs from the econ working-paper default, drop per-file overrides in `deploy_assets/templates/paper_skeleton/{variant}/` (root templates are the fallback) and add any variant-specific section-list / section-guidance blocks via `VARIANT_{NAME}` markers in `docs/stage_5.md` + `paper-writer.md` (see the mode procedure's step 4 for marker semantics; llm_cognition is the reference).
5. Decide extension/mode compatibility explicitly: `--ext empirical` requires a `deploy_assets/extensions/empirical/agent_metadata/{variant}_agents.json`; `--mode report` requires a `deploy_assets/templates/agents/{variant}_modes/report/vocab.json` overlay *and* domain-appropriate shared audit bodies. Enforce unsupported compositions in `_setup_config_resolve_variant_and_modes` / `_setup_config_resolve_variant_descriptors`.
6. Test: `./setup.sh /tmp/test_{variant} --variant {variant} --assemble-only` — plus a rebuild of the *existing* variants diffed against a pre-change baseline (`--assemble-only` output) to prove the new vocab keys changed nothing for them.
7. Document: add a row to the "Supported variants" table in CLAUDE.md and an invocation example + variant note in the `deploy-project` skill.

## Adding a new mode

A *mode* re-frames the pipeline's orchestration (theory-first → identification-first, or another orientation) without forking a variant. It is layered on top of `--variant {finance|macro|...}` via two overlay mechanisms: a vocab overlay (mode-specific overrides to variant vocab keys) and a body overlay (mode-specific shared-agent bodies that replace the base shared body for that mode). The `empirical-first` mode is the reference implementation.

1. **Choose the slug.** Mode flag is `--mode {slug}`; `setup_runtime_documents` in `deploy_assets/scripts/setup/runtime_documents.sh` lowercases `-` → `_` for directory lookups (`mode_slug="${MODE//-/_}"`). So `--mode foo-bar` looks under `foo_bar/`.
2. **Vocab overlay:** create `deploy_assets/templates/agents/{variant}_modes/{mode_slug}/vocab.json` with only the keys whose meaning changes under this mode. Loaded via `candidate_vocab` next to the `mode_slug` assignment and layered on top of the base variant vocab — later wins on duplicate keys. Reference: `deploy_assets/templates/agents/finance_modes/empirical_first/vocab.json`.
3. **Body overlay (optional):** create `deploy_assets/templates/agent_bodies/shared_modes/{mode_slug}/` with per-agent body overrides. Files are named `{agent_id}-core.md` (variant agent overrides) or `{agent_id}.md` (shared agent overrides) — the loader's suffix discrimination in `load_body` (`deploy_assets/scripts/agent_body_loader.py`) handles both. Reference: `deploy_assets/templates/agent_bodies/shared_modes/empirical_first/` — all six overrides are `theory-generator-core.md`, `idea-generator-core.md`, `identification-designer-core.md`, `idea-prototyper.md`, `implications-deriver.md`, `referee-mechanism.md`.
3b. **Metadata overlay (optional):** when a mode re-frames what an agent *does* (not just how it phrases things), its orchestrator-facing metadata should match — chiefly `description`, which the orchestrator reads when choosing and prompting agents. Add a `"modes": {"{mode_slug}": {"description": "..."}}` key to the agent's entry in `claude_shared_agents.json`, `claude_variant_agents.json`, or an extension's metadata file; any metadata field can be overridden, not just `description`. All five base assemblers receive `--mode {mode_slug}` (threaded via `MODE_METADATA_ARGS`, resolved by `setup_runtime_documents` in `deploy_assets/scripts/setup/runtime_documents.sh`), and both extension appliers receive the same slug plus the mode body/vocab paths for their four supported runtimes. Every assembler merges matching metadata overrides over the base fields via `apply_mode_overrides` in `deploy_assets/scripts/agent_body_loader.py`; the `"modes"` key itself is always stripped from assembled output, in every mode and in no-mode builds. Reference: the 16 report-mode fan-out agents (report-native descriptions replacing the pipeline-stage ones). Mode-override strings get vocab substitution like base metadata (merge runs before `apply_vocab_to_metadata`).
3c. **Body inject (alternative to a full overlay):** when a mode reuses many pipeline-native agents whose bodies just need re-anchoring (different input/output paths, artifacts that don't exist in this mode), prefer one appended context block over N forked bodies: a `deploy_assets/templates/shared/{mode}_inject.md` appended via `_setup_extensions_inject_block_into_agents` to an explicit agent list, gated on the mode. Reference: `deploy_assets/templates/shared/report_mode_inject.md` + `_setup_extensions_inject_report_mode_into_agents` in `deploy_assets/scripts/setup/extensions_and_injections.sh` (12 pipeline-native audit agents; the referee trio and `polish-identification` instead carry full report-native body overlays because their *task* changes, not just their paths).
4. **Stage-doc guards (optional):** add mode markers in `deploy_assets/templates/shared/docs/*.md` (and extension docs — the resolver runs over everything copied into `docs/`) for content that should activate under this mode. The marker resolver (search `def keep` in `deploy_assets/scripts/setup/extensions_and_injections.sh`) handles four families generically: `EMPIRICAL_FIRST` (kept only under `--mode empirical-first`), `MEASUREMENT_FIRST` (kept only under `--mode measurement-first`), `THEORY_FIRST` (kept under any *theory-shaped* pipeline — the modeless default AND measurement-first, whose output is still a theory paper produced evidence-first), and `NO_MODE` (kept strictly in the modeless default — use it for a `THEORY_FIRST` site whose content a mode-specific sibling block replaces, so exactly one of the pair renders in every mode). Adding a new mode means extending `keep()`'s mode table — one line — plus writing the mode's blocks. The same resolver also handles **variant markers** — `<!-- VARIANT_{NAME}_START/END -->` blocks (name = variant uppercased, e.g. `VARIANT_LLM_COGNITION`) are kept for the matching variant and removed wholesale otherwise, generically: a new variant needs no resolver edit. Use variant markers for *additive* variant-specific blocks in stage docs and shared agent bodies (the llm_cognition Related Work / Experiments / checklist sections in `stage_5.md` + `paper-writer.md` are the reference); use vocab keys when existing text needs different *wording* per variant. Never **interleave** two differently-named marker blocks (`A_START … B_START … A_END … B_END`) — the wholesale-removal regex would leak an orphaned `B_END` into the deployed file; nesting and siblings are both safe. This applies to mode markers too.
5. **Mode-conditional descriptors:** add a `case "$VARIANT"` branch to `_setup_config_apply_mode_descriptors` in `deploy_assets/scripts/setup/resolve_config.sh` (search `DOC_SUBTITLE=`) that overrides `PAPER_TYPE`, `DOMAIN_AREAS`, `DOC_SUBTITLE`, and any other variant descriptors the mode reframes.
6. **Validation and dependency expansion:** add the mode to `_setup_config_resolve_variant_and_modes` in the same module (search `Unknown mode:`) to decide which `--variant` combinations it supports. If the mode implies an extension (as `empirical-first` implies `--ext empirical`), add it there with an Info message.
7. **Tests:** `./setup.sh /tmp/test_{mode} --variant {variant} --mode {mode} --assemble-only` should resolve cleanly with `✓ All placeholders resolved` and no `{{KEY}}` leakage. Inspect the deployed CLAUDE.md and `.claude/agents/*.md` for marker leakage (`grep -c '{MODE}_FIRST_START'` should be 0).
8. **Document:** add a one-line row to the "Supported modes" table in CLAUDE.md, then write the mode's full semantics (stage/gate changes, pruned agents, cross-variant compatibility nuances, auto-implied extensions, mutual exclusions with other flags) as a `### --mode {slug}` section in the `deploy-project` skill, parallel to the `--mode empirical-first` section there. Add an invocation example to that skill's command block too.

## Adding a new extension — no written procedure (known gap)

Variants and modes have step-by-step procedures above; extensions do not. Nothing has been
written down for adding a third `--ext`, even though the two existing ones establish the shape.

**Failure mode:** an extension added by pattern-matching `deploy_assets/extensions/empirical/` will probably
get the agent metadata and bodies right (those are the visible parts) and miss the dispersed
wiring — the `.env` key append, the ordered `EXTENSIONS` deduplication in `deploy_assets/scripts/setup/resolve_config.sh`, dependency installation through `provision_extension_dependencies`, the per-mode pruning lists
(`_setup_extensions_prune_report_mode_agents`, `_setup_extensions_prune_non_empirical_first_agents` in `extensions_and_injections.sh`), write-site ownership registration for every new deployed infrastructure unit, and the faithful-mode developing-vs-evaluator
categorization that decides which new agents receive the contract pointer. Each of those is
silent when missed: assembly still succeeds, and the defect surfaces at run time or only in
`--faithful` / `--mode report` deployments.

**An extension is not self-contained — `deploy_assets/extensions/<ext>/` is only part of it.** Two pieces
live outside that directory entirely:

- **Skills.** There is no `skills/` dir under `deploy_assets/extensions/`. An extension's skills live in
  `deploy_assets/templates/skill_metadata/<ext>_skills.json` + `deploy_assets/templates/skill_bodies/<ext>/`, wired in by
  `deploy_assets/scripts/apply_extension_<ext>.sh` — the same place core skills live.
- **Orchestrator injections.** The `*_inject.md` files at the root of `deploy_assets/extensions/<ext>/`
  splice extension-specific stages, gates, and `pipeline_state.json` fields into the
  assembled runtime doc (they fill `{{EXTENSION_STAGES}}`,
  `{{EMPIRICAL_STAGE3A_GATE_ADDENDUM}}`, `{{EMPIRICAL_STATE_FIELDS}}`,
  `{{EMPIRICAL_LOOP_FIELDS}}` and friends). All eight for empirical: `stages_inject.md`,
  `stage2_rerun_inject.md`, `stage3a_gate_inject.md`, `state_fields_inject.md`,
  `state_loop_fields_inject.md` (the audit-loop counters), `state3a_doc_inject.md`,
  `playbook_inject.md`, `scorer_fertility_inject.md`. An extension whose agents assemble
  correctly but whose injects are missing produces agents the orchestrator never calls.

**Reference implementations:** `deploy_assets/extensions/empirical/` (the full-size case: agent metadata +
bodies for shared and both variants, `utils/`, `docs/`, `deps.txt`, and eight `*_inject.md`
fragments) and `deploy_assets/extensions/theory_llm/` (the minimal case: shared agents only, `llm_client.py`,
`docs/`, `deps.txt`, five `*_inject.md` fragments).

**To close it:** trace one extension end-to-end through `deploy_assets/scripts/setup/extensions_and_injections.sh` and its applier, then write the procedure in
the form used by "Adding a new variant" / "Adding a new mode" above, including a
composability checklist (does the new extension compose with `--manual`, `--mode report`
install-only, `--faithful`, `--light`?).

> Pointers in this file use grep-able anchors rather than line numbers on purpose — the previous line-number references had drifted by hundreds of lines before anyone noticed. If you add a pointer, name a searchable string.
