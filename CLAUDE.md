# CLAUDE.md — Meta Project: Pipeline Template Development

AFTER EVERY BIG CHANGE, LAUNCH AN INDEPENDENT REVIEW AGENT TO REVIEW YOUR CHANGES FOR ISSUES — **SONNET** WHEN RUNNING UNDER CLAUDE, **GPT SOL** WHEN RUNNING UNDER CODEX. IF ANY ISSUES ARE FOUND, ADD A NEW ROUND OF AUDITING AFTER FIXING THE CURRENT ROUND'S ISSUES (EVEN IF THERE ARE ONLY MINOR CHANGES). ITERATE UNTIL DONE.

`CLAUDE.md` AND `.claude/skills/` ARE CANONICAL. `AGENTS.md` AND `.agents/skills/` ARE GENERATED MIRRORS FOR CODEX. EDIT ONLY THE CANONICAL PAIR, THEN RUN `scripts/sync_dev_instructions.sh` — NEVER EDIT THE MIRRORS BY HAND. BOTH MIRRORS ARE DEV-ONLY: SINCE v2.23.0 (#232) A DEPLOYMENT IS ASSEMBLED FROM `deploy_assets/` INTO AN EMPTY PROJECT DIRECTORY, SO NEITHER MIRROR EVER ENTERS ONE — `setup.sh` GENERATES A PROJECT'S OWN `AGENTS.md` AND `.agents/skills` FROM SCRATCH. NEITHER GETS A MANIFEST ENTRY.

EVERY TEMPLATE-OWNED PATH DEPLOYED BY `setup.sh` MUST BE CREATED OR REGISTERED THROUGH THE `infrastructure_*` HELPERS IN `deploy_assets/scripts/setup/ownership.sh`; THAT WRITE-SITE REGISTRATION IS THE SOLE SOURCE OF `.deploy_manifest.json` REPLACEMENT OWNERSHIP. MUTABLE PROJECT CONTENT USES `bootstrap_*` HELPERS OR PLAIN WRITES AND MUST NEVER ENTER REPLACEMENT OWNERSHIP (`.env` IS EXPLICITLY MERGE-MANAGED). BUILD-TIME-ONLY PATHS GET NO REGISTRATION.

VERSIONING (`VERSION` = SINGLE SOURCE OF TRUTH; `setup.sh`/`update.sh` STAMP `<version>+<git-hash>` INTO DEPLOYMENTS): WHEN YOU SHIP SOMETHING NOTABLE, BUMP `VERSION` (**PATCH** = FIXES, **MINOR** = NEW MODE/CAPABILITY, **MAJOR** = IDENTITY SHIFT), ADD A `CHANGELOG.md` LINE, COMMIT, THEN `git tag -a vX.Y.Z -m "…"` AND PUSH WITH `--follow-tags`. `VERSION`/`CHANGELOG.md` ARE BUILD-TIME ONLY (READ FROM THE SOURCE TREE AT SETUP, NEVER COPIED INTO A DEPLOYMENT) — SO **NO** MANIFEST ENTRY.

RULE TEXT THAT MUST READ BYTE-IDENTICALLY ACROSS MANY AGENT BODIES BELONGS IN `deploy_assets/templates/fragments/*.md`, INCLUDED VIA `{{> fragment_id }}` (LOWERCASE IDS ONLY — AN UPPERCASE ID SILENTLY SHIPS LITERALLY). DO **NOT** FRAGMENT ROLE-ADAPTED PROSE THAT MERELY LOOKS SIMILAR: THE scorer/referee/self-attacker/triager COPIES ARE INTENTIONALLY VERB- AND VERDICT-SPECIFIC, AND FLATTENING THEM CHANGES BEHAVIOR. MECHANISM + THE ZERO-BEHAVIOR-CHANGE VERIFICATION PROCEDURE: `edit-pipeline` SKILL.

WHEN ADDING A NEW `{{KEY}}` PLACEHOLDER TO ANY AGENT BODY OR FRAGMENT (SHARED `{id}.md` OR VARIANT `{id}-core.md` — SINCE v2.9.0 **BOTH** RESOLVE AGAINST THE LAYERED VOCAB shared → variant → tier → mode, LATER WINS): PUT ITS DEFAULT IN `deploy_assets/templates/agent_bodies/shared/vocab.json` (OR IN **EVERY** VARIANT VOCAB `deploy_assets/templates/agents/{finance,macro,llm_cognition}/vocab.json`), THEN ADD PER-VARIANT OVERRIDES ONLY WHERE THE DOMAIN WORDING DIFFERS. ECON DEFAULTS MUST STAY BYTE-IDENTICAL TO THE PRE-EXTRACTION TEXT UNLESS A BEHAVIOR CHANGE IS INTENDED. THE LOADER RAISES `KeyError` ON UNRESOLVED PLACEHOLDERS, SO A KEY DEFINED IN ONLY SOME VARIANT VOCABS BREAKS SETUP FOR THE OTHERS.

## What this is

This is the **template repository** for the autonomous research paper pipeline. We are building and iterating on the pipeline infrastructure itself — agents, setup scripts, CLAUDE.md templates, dashboard, etc.

Deployable assets live under `deploy_assets/` (templates/, scripts/, extensions/, launch.sh, dashboard.html). Root `setup.sh`, `update.sh`, `scripts/update_coordinator.sh`, `VERSION`, `LICENSE`, and `.env.example` are also authenticated assembly/update inputs; other root files and scripts are dev-only tooling. Since v2.23.0 (#232) `setup.sh` assembles a deployment from these inputs into an **empty** project directory — there is no clone-then-strip step, so a path that isn't explicitly produced simply never ships (fail-closed).

This file is tracked in git but **overwritten by `setup.sh`** in cloned projects. It is for our development work only. The pipeline's CLAUDE.md that end users see is assembled by `setup.sh` from `deploy_assets/templates/shared/core.md` + `deploy_assets/templates/runtime/claude/session.md` + per-variant vocab substitution. (Variant-specific scorer calibrations live in `deploy_assets/templates/agents/{variant}/vocab.json` and are substituted into the scorer agent body, not appended as a separate block.)

## Sibling repo: the IAR website + wiki

The pipeline's empirical dataset skills (`deploy_assets/templates/skill_bodies/empirical/<dataset>.md` + `deploy_assets/templates/skill_metadata/empirical_skills.json`, assembled into a deployed project's `.claude/skills/<dataset>/SKILL.md`) and the IAR wiki dataset pages (`src/content/docs/datasets/*` in `github.com/institute-for-automated-research/website`) are two mirrors of the same dataset knowledge, kept in sync both ways. When a change here affects a wiki page or a published paper PDF/landing page (dataset access or gotchas, citation format, provenance disclosure), file the issue **in the website repo** (`gh issue create --repo institute-for-automated-research/website`), not here. The website repo's CLAUDE.md carries the reciprocal rule for changes that originate there.

## Working principle: the pipeline is not ground truth

The pipeline is the current best we have, not necessarily correct. Do not assume the pipeline's current way of doing things is the right way — it is a candidate to be questioned and improved, not a baseline to defer to.

## Working principle: no unsolved, undocumented, or untracked architectural limits

When auditing or editing the pipeline, if a known architectural limit is identified (e.g., a self-referential check, a subjective rule, an enforcement gap, a missing producer for a consumed artifact), do not leave it acknowledged-and-moved-on. Either (a) solve it in the same pass, or (b) document it in `LIMITATIONS.md` with the failure mode it can produce and what would be needed to close it, **and open a corresponding GitHub issue linked from that entry**. Add explanation to the relevant agent body or doc file when it helps operators, but that does not replace the mandatory `LIMITATIONS.md` entry + GitHub issue pair. Acknowledged-but-untracked limits accumulate silently and produce surprises in future runs.

## Working principle: no implementation-complexity budget — do what is best for the pipeline

There is no implementation-complexity budget, no edit-cost ceiling, no "this change is too big" threshold. The pipeline is designed to be run millions of times; any one-time cost of editing the template — updating five runtime assemblers, reshaping `pipeline_state.json`, rewriting the escalation table, expanding the orchestrator prompt, adding agents, writing new tests — is trivially amortized against that. Do not reject or water down a structural proposal because it is expensive to *implement*; reject it only if it is worse for the pipeline on the merits.

Concretely:
- If a change makes the pipeline produce better papers, do it — even if it touches every runtime, rewrites state, and requires new agents.
- Do not propose a "narrower variant" to save implementation effort. Propose the narrower variant only if it is genuinely better for the output.
- Do not invoke "implementation-complexity cost," "maintenance burden," or "surface area" as reasons to decline. These are real for a one-shot project; here they are rounding errors against millions of runs. (This is about *build* cost — runtime complexity in the prompts is a different axis, governed by the "prefer removing rules" principle below.)
- The only legitimate reasons to decline a structural proposal are: it makes the output worse, it introduces a correctness/safety regression, or a strictly better alternative exists on the merits.

## Working principle: prefer removing rules over adding them

When possible, avoid adding rules — prefer removing. More rules mean more overfitting and harder debugging; when a new rule and an existing one would do the same work, cut, don't stack.

## Working principle: prefer no structured classes

Prefer prose over fixed categories when agents report findings — a label set looks like coverage while checking nothing. Verdicts the pipeline routes on, and counts, are fine.

## Setting up a new project

**Load the `deploy-project` skill.** It carries every `setup.sh` flag and composition
(`--variant`, `--ext`, `--mode {empirical-first,measurement-first,report}`, `--seed`, `--faithful`, `--manual`,
`--light`, `--halt-on-core-bypass`), the mutual exclusions, post-setup launch instructions
(`launch.sh`, tmux, unattended runs), and WRDS server startup.

One thing worth knowing without loading it, because it also applies to template-assembly testing:

- **Every setup is checkout-local.** `setup.sh` never fetches the template repository; check out the desired tag/commit first. A full deployment rejects dirty build inputs. `--assemble-only <destination>` permits development state, assembles and validates there, and exits before dependency provisioning / project git init / initial commit. It has no implicit destination.

## Editing this repo

**Load the `edit-pipeline` skill.** It carries the repository layout, how `setup.sh`
assembles a deployment, the runtime-agnostic-core vs runtime-specific-packaging split,
the full agent roster and classification, subagent model pinning / fallback / launch-heal,
the core-skill catalog, and the step-by-step procedures for adding a variant, a mode, an
agent, a skill, or a vocab placeholder.

## Supported variants

| Variant | Flag | Status | Target journals |
|---------|------|--------|-----------------|
| `finance` | `--variant finance` (default) | Working (v2) | JF, JFE, RFS |
| `macro` | `--variant macro` | In development | AER, Econometrica, QJE, JPE, ReStud, JME |
| `llm_cognition` | `--variant llm_cognition` | Working (v2) | NeurIPS, ICML, ICLR (TMLR as field tier) — the science of LLM cognition & evaluation. Auto-implies `--ext theory_llm` (since v2.10.0 — the experiments are the evidence; skipped under `--mode report`, which prunes those agents); `--ext empirical` is gated off (see LIMITATIONS.md). `--mode report` supported since v2.16.0. |

## Supported extensions

| Extension | Flag | Status |
|-----------|------|--------|
| `empirical` | `--ext empirical` | Working |
| `theory_llm` | `--ext theory_llm` | Working (v1) |

Legacy: `--variant finance_llm` is shorthand for `--variant finance --ext theory_llm`.

## Supported modes

| Mode | Flag | Status | Variants | Notes |
|------|------|--------|----------|-------|
| `empirical-first` | `--mode empirical-first` | Working (v1) | `finance` | Identification-first instead of theory-first. Auto-implies `--ext empirical`. |
| `measurement-first` | `--mode measurement-first` | Working (v1) | `llm_cognition` | Evidence-first for the modal ML cognition paper: construct spec + design gate → Stage 3b experiments as the evidence core → post-experiment formal characterization (math audits fire there). |
| `report` | `--mode report` | Working (v1) | `finance`, `macro`, `llm_cognition` | Referee an external submission instead of generating one. One-shot, no stages. |

Full semantics for both modes are in the `deploy-project` skill.
