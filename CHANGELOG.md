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

## [2.6.0] — 2026-07 (current)
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
