# Changelog

All notable milestones of the autonomous research-paper pipeline template.

Versions follow [semantic versioning](https://semver.org/): **MAJOR** = a fundamental
change in what the pipeline *is*, **MINOR** = a new additive capability, **PATCH** = fixes.

This history was reconstructed retroactively from the git log (505 commits, Feb–Jul 2026)
and back-filled as annotated git tags on the anchor commits shown. Dates are the anchor
commit's authored date. The `VERSION` file at the repo root is the single source of truth
going forward; `setup.sh` stamps `<version>+<git-hash>` into every deployment.

> Note: the informal `v1`/`v2` labels in `CLAUDE.md` denote **variant maturity**
> (e.g. finance), a separate axis from this template version.

---

## [2.6.3] — 2026-07-20 (current)
Resumed Claude sessions were starting unguarded. The hourly `/loop` stall guard and
`start_services.sh` were both tied to the fresh-start path, so a session relaunched with
"continue" (`status: "running"`) got neither — no stall detection for the rest of the run,
and dead data connections whose liveness `data_inventory.md` still asserted.
- **Session preflight** (`templates/runtime/claude/session.md`) — start services, establish the hourly loop, write-or-re-verify the data inventory. Runs on every session, fresh or resumed
- Invoked from the `not_started` and `running` branches **only**: a `complete` or `halted_*` session reports and stops, and on `halted_wrds_unreachable` restarting the service is the operator-driven repair that branch forbids
- The loop is documented as session-lifetime, not Stage 0 — it lives in the Claude Code session and dies with it, so every relaunch re-establishes it; when in doubt, set it up (a duplicate stall check is harmless, a missing one is not)
- Re-verify passes correct stale ✓ rows and commit only if a row changed, rather than rewriting the inventory's research-design implications
- Claude-only: `/loop` is a Claude Code skill and the other runtimes have no session-start block

## [2.6.2] — 2026-07-20
CLAUDE.md slimmed to the always-on layer; repo-editing reference moved to a skill. Nine audit
rounds found the moved content was substantively stale, so this is a correctness pass as much
as a docs move.
- `edit-pipeline` skill — repo layout, setup.sh assembly, agent classification, model pinning/fallback, and the add-a-variant / add-a-mode procedures. CLAUDE.md 284 → 87 lines (369 at session start)
- **Corrected: "Adding a new variant"** named a per-variant metadata file `setup.sh` never reads and a body dir nothing loads (stale since the `784b01f` consolidation) — following it produced a broken variant. Variant agents are one `claude_variant_agents.json` + `{id}-core.md` bodies in `agent_bodies/shared/`, specialized by `vocab.json`
- **Corrected: vocab trip-wire** sent shared-body `{{KEY}}` defaults to the variant vocabs; shared bodies resolve against `templates/agent_bodies/shared/vocab.json`
- **Corrected: agent rosters** — 16 of 31 shared agents were undocumented (all 8 `polish-*`, `bib-verifier`, `editor`, `report-synthesizer`, `referee-mechanism`, `triager`, `puzzle-triager`, `faithful-drift-auditor`, `debugger`); `question-poser`/`question-referee` were in neither list; `headline-replicator`/`method-checker` missing from the empirical roster
- **Corrected: Grok** was absent entirely — architecture said "three runtimes"; it is a fourth assembly call site
- **Corrected: fable generative spine** was printed backwards (`question-poser` is Stage 0, `idea-generator` is Stage 1)
- **Corrected:** 4 of 6 unconditionally-installed core skills missing from the table; `extensions/empirical/skills/` path never existed; all literal `setup.sh:NNN` pointers had drifted (one by ~2200 lines) and are now grep anchors
- Enumerations that can rot are replaced by the mechanism that generates them (`scripts/list_agents_by_category.py`, grep the `prune_report_mode_agents` call sites)
- Documented gap: no written "Adding a new extension" procedure, with its failure mode

## [2.6.1] — 2026-07-19
Meta-repo dev tooling: CLAUDE.md slimmed by moving deployment docs into a skill.
- `deploy-project` skill (`.claude/skills/deploy-project/`) — all `setup.sh` flags, compositions, mutual exclusions, post-setup launch guidance, WRDS server startup. Loaded on demand instead of sitting in every session's context; CLAUDE.md 369 → 284 lines
- `.claude/skills/` is now tracked in the meta-repo; `setup.sh` snapshots the cloned dev skills after clone and strips them in the cleanup block, so they never ship into deployed projects (build-time only — no deployment-manifest entry)
- Strip is checksum-guarded: if a future `skill_id` ever collides with a dev-skill directory name, the assembled project skill is kept and a rename warning is emitted, rather than being silently deleted

## [2.6.0] — 2026-07
Production-hardened, four-runtime era. Introduces formal semantic versioning (`VERSION` file
+ `setup.sh` version stamp + this changelog).
- **Grok** runtime added — fourth runtime alongside Claude, Codex, Gemini (`cf0f112`)
- `pipeline_state.json` schema overhaul: ~17 bespoke loop counters → one generic `loops:{}` object (`7783945`) — breaking for in-flight deployments (handled by `update.sh`)
- Launch-time model heal: bidirectional tier correction at every `launch.sh claude` (`b592724`)
- Shared rule-fragment system (`templates/fragments/`, `{{> id}}` includes) (`0982043`)
- Codex retier to `gpt-5.6-{sol,terra,luna}` + isolated `codex exec` launcher replacing broken `spawn_agent` (`0d1245c`)
- macOS portability (bash 3.2 / BSD awk) + per-project `.venv/` (`6f9cdbf`)

## [2.5.0] — 2026-06-13 — `126f79e`
Resilience infrastructure.
- Subagent model-availability probe + assembly-time fallback chains (`126f79e`), prompted by the fable/mythos export-control suspension (2026-06-12)
- `--halt-on-core-bypass` guard + degradation ledger (`52a6a27`)

## [2.4.0] — 2026-05-25 — `90d501c`
`--mode report`: referee an external submission instead of generating one (one-shot, no stages).

## [2.3.0] — 2026-05-06 — `e4a133f`
`--faithful` mode: stricter `--seed` that implements the seed as a frozen contract.

## [2.2.0] — 2026-05-03 — `97ae4c5`
`--mode empirical-first`: identification-first pipeline for causal-estimate papers.

## [2.1.0] — 2026-04-25 — `7855435`
`--manual` mode (research toolkit) plus the April evaluation-topology work: editor Gate 5 aggregation, freeform scorer/referee, puzzle-pivot gate, Stage 9 polish layer.

## [2.0.0] — 2026-04-05 — `e01693b`
**Multi-runtime.** Runtime-agnostic core + per-runtime packaging; **Codex** and **Gemini** runtimes join Claude. The shift from Claude-only to three runtimes.

## [1.3.0] — 2026-03-23 — `ff49622`
Composable extensions: `theory_llm` becomes a proper `--ext` (was a variant).

## [1.2.0] — 2026-03-20 — `00df890`
Empirical extension: data skills (FRED, Ken French, WRDS, …) + calibrator/empiricist agents.

## [1.1.0] — 2026-03-19 — `00ab22b`
Multi-variant infrastructure: `templates/` split, `macro` variant, per-`--variant` assembly.

## [1.0.0] — 2026-03-17 — `1b65f05`
**Autonomous pipeline born.** `setup.sh`, orchestrator with stages/gates, `pipeline_state.json`, dashboard, and the core pipeline agents. The shift from manual toolkit to autonomous pipeline.

## [0.1.0] — 2026-02-28 — `849f7db`
Initial manual research toolkit: 3 agents (scribe, referee, style), flat `CLAUDE.md`, no pipeline.
