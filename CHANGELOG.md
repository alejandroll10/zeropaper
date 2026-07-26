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

## [2.8.1] — 2026-07-26 (current)
`setup.sh`'s tier-vocab temp file no longer bricks every future deploy on a host.

- **BSD/macOS `mktemp` randomizes only a *trailing* run of `X`s.** `tier_vocab.XXXXXX.json`
  (2.7.0) therefore produced that path **literally** — a fixed name, which defeats `mktemp`.
  Sequential deploys still worked because the cleanup removes it, so this passed unnoticed.
- **The failure mode was latent and disproportionate.** Any run that died between creating the
  file and the cleanup left it behind; from then on *every* deploy on that host aborted at that
  line under `set -e` with a bare `mkstemp failed ... File exists` naming neither `setup.sh` nor
  the tier vocab. Concurrent deploys collided identically. Reproduced, then verified fixed: with
  a stale file present the deploy now succeeds.
- The `.json` extension was decorative — the path reaches the assemblers explicitly via `--vocab`.

## [2.8.0] — 2026-07-26
Figures are readable by the agent that has to caption them, and poppler is a declared dependency.

- **The trigger.** `paper-writer` has no Bash (deliberately — the claim-grounding stack requires
  every number in the paper to trace to a *producing agent's* output, and a shell would let the
  writer compute its own). In a field run it could not open either of two figure `.pdf`s because
  `pdftoppm` was absent. Granting Bash was the wrong lever twice over: it weakens the grounding
  invariant, and with no poppler on the host it would not have fixed anything.
- **Figures now ship as a `.pdf`+`.png` pair.** New `templates/fragments/figure_dual_format.md`,
  included by all four producers (`empiricist` finance/macro, `theory-explorer`,
  `experiment-designer`). The vector `.pdf` is what the paper `\includegraphics`es; the raster
  `.png` is what `paper-writer` reads to pick the headline figure and caption what is actually
  plotted. Producers that emit PDF-only (pgfplots/TikZ, R/Stata) rasterize with `pdftoppm`.
- **A build gate that could silently invert is now fail-closed.** Stage 5 build-verify check 5
  ran `pdftotext main.pdf - | grep -c PLACEHOLDER` and required `0`. With `pdftotext` missing the
  pipe is empty and `grep -c` prints exactly that `0` — so a paper whose title page read
  `TITLE PLACEHOLDER` passed. It now probes for the binary first and treats absence as a failure.
- **`poppler-utils` is declared** in `requirements.system` with its four consumers, and `update.sh`
  warns when it is absent — `requirements.system` is build-time-only, so a refreshed deployment
  otherwise had no signal that the host needed it.
- **Report mode halts instead of fabricating.** `--mode report` on a PDF-only submission now
  verifies poppler before fanning out; an agent handed an unreadable file does not reliably report
  that it read nothing, it produces a plausible audit of a paper it never saw.
- Also: `output/stage{3a,3b}/figures/` are created at deploy (with matching report-mode cleanup —
  a bare `rmdir` on a now-non-empty parent was leaving stray `output/stage*/` trees in report
  deployments, contradicting `core_report.md`); `polish-consistency` counts a `.pdf`/`.png` pair as
  one figure; `stage_5.md` carves the figure-rasterization marker out of the versioned claim-refire
  procedure it would otherwise be misrouted through.

## [2.7.0] — 2026-07-25
New `llm_cognition` variant: papers on the science of LLM cognition & evaluation (formal
frameworks + benchmark designs; NeurIPS/ICML/ICLR target, tier ladder
`nature → top-ml → field → workshop`; pairs with `--ext theory_llm`). Economics wording
previously hardcoded in the variant-agent bodies and the editor's tier ladder is now
vocab-parameterized (finance/macro output byte-identical); `referee-mechanism` now
receives the variant-context block. `--ext empirical` and `--mode report` are gated off
for the new variant (see LIMITATIONS.md "llm_cognition variant" entry).

## [2.6.7] — 2026-07-25
Cut 2.6.6 down to the two clauses that were doing the work.

- **2.6.6 was a rule stack, not a metric swap.** `stage_2.md`'s Gate-2 loop went from 2 clauses to
  7, the seed override gained 3 more, and a `LIMITATIONS.md` entry existed only to record that one
  of the new rules was unenforceable. That accretion pattern is the thing issue #193 is *about* —
  each audit round found a hole and it got patched with more prose.
- **The class-recurrence metric is gone.** It was a judgment with no artifact behind it (no auditor
  emits a class label), it needed the hard cap as a backstop anyway, and the hard cap alone would
  have stopped the incident that motivated it — that run went ~10 versions; a cap of 3 stops it at
  3. Its only marginal benefit was firing one version earlier, which is not worth a rule.
- **What survives is what was load-bearing.** Two clauses per gate: (1) a judgment-free hard cap —
  3 consecutive math-audit failures (theory-first), 3 consecutive REVISEs (empirical-first
  mechanism), 5 audit-fix attempts (Stage 3a) — at which patching the current artifact again is not
  an option; (2) when a fix *narrows* a claim, narrow every claim of the same shape, not just the
  flagged instance. Clause (2) is the actual lesson from the field incident (one version narrowed
  the `T` axis, left `h` universal, blew up four versions later) and it needs no recurrence
  detection — it applies to any narrowing, first time or fifth.
- **Removed as scaffolding for the deleted metric:** reactive-retirement verification, the
  fires-earlier/never-defers reconciliation, the seeded core/auxiliary cut restriction and its
  never-fire-early guard (the base path no longer carries a narrowing instruction that needs
  gating; the ship-honest check's own referent test was always the right home), the verdict-keyed
  counter clause, the "or earlier, as soon as a class survives" qualifiers on three `core.md`
  escalation rows, and the `LIMITATIONS.md` entry.
- Net vs. 2.6.5: the count metric is **deleted** and replaced by a hard cap — fewer moving parts
  than before 2.6.6, not more. The `core.md` row alignment that closed #157, the new Gate-2
  mechanism REVISE row, and the Stage 3a fix all stand.

## [2.6.6] — 2026-07-25
Gate 2's revision loop now measures progress by **error classes retired**, not by the error
count falling (issue #193).
- **The count metric was the bug.** `docs/stage_2.md` told the orchestrator to keep iterating
  while the error count decreased and to escalate only on a plateau. A run can patch one
  instance of the same defect per version, watch the total tick down, and never register that
  it is hitting an identical class repeatedly. Observed in `ai-trading-breadth` (`--faithful`):
  ~10 theory versions burned on one recurring class — a universally-quantified claim inferred
  from a computation whose quantifier range was strictly narrower — while the mathematical core
  sat frozen and certified across seven consecutive diffs. Every defect was in the
  attribution/presentation layer.
- **New rule, same length: retire the class.** A class still flagged after a fix aimed at it
  means patching is not working. The response is to prove the general version or cut the claims
  it attaches to back to what was actually verified — **across every claim of that shape, not
  just the flagged instance**. Instance-scoped narrowing is precisely why the class recurred:
  one version narrowed the `T` axis and left the `h` axis universal, and it blew up four
  versions later on the paper's own census grid. Attempt-increment / `theory_version` reset is
  now the *last resort*, reached only if the class survives being retired.
- **No new mechanism, by design.** The run's own conclusion was that "a fourth ledger would fail
  the same way" — new verification machinery is new claim surface carrying the same defect. So
  this ships as a metric swap against machinery that already exists: `math-auditor` is already
  instructed to skim prior `math_audit_v*.md` for recurring error classes, `core.md`'s
  "frame honestly — never inflate" principle already licenses narrowing when the substance holds
  and only the label was inaccurate, and the seeded ship-honest check already knew how to cut an
  overclaim. Nothing was added to `pipeline_state.json` and no agent was created.
- **Empirical-first transplant made explicit rather than assumed.** `mechanism-auditor` returns
  seven fixed dimension labels, not a multiplicity of same-shaped claims, so a dimension label is
  only a coarse proxy for an error class. The empirical-first text now names both failure
  directions: the same dimension failing twice for unrelated reasons is not recurrence, and a
  defect resurfacing under a *different* dimension label after a cosmetic dodge is.
- **Seeded/faithful convergence.** `SEED_OVERRIDE_STAGE_2_GATE_2.md` superseded the base
  escalation wholesale, which under `--faithful` (where the seed pins the contribution, so
  neither attempt-increment nor sketch-swap is available) left "add another ledger" as the only
  move the docs did not forbid. It now supersedes only the base path's *last resort*; the
  retire-the-class first move is shared, and the ship-honest check gained the same
  every-claim-of-that-shape scoping. No `--faithful` branch was needed.
- **New judgment-free floors, because neither metric was self-bounding.** Class-recurrence is a
  judgment, so it is layered on top of mechanical bounds rather than replacing them — but auditing
  the change surfaced that the *old* metric had no real floor either: an error-count plateau never
  fires against a run that patches one instance per version, which is exactly how the field
  incident reached ~10 versions. Gate 2 therefore gains hard caps it never had: **3 consecutive
  math-audit failures** (theory-first) and **3 consecutive REVISEs** (empirical-first mechanism).
  At the cap, patching the current artifact again is not an option — escalate by incrementing
  `theory_attempt` or by swapping sketches. The pre-Stage-5 sketch-swap bullet is amended so
  "continue restructuring the current sketch" means continuing it under a *fresh attempt*, closing
  the loophole where a mandatory-evaluation step could be satisfied while patching forever.
- **The class trigger only ever fires *earlier*; it never defers a floor.** The seeded ship-honest
  counter is explicitly re-stated as keyed to consecutive Gate-2 *verdicts*, not to class
  judgments, so it cannot be deferred by calling every recurrence a new class. Retirement is
  verified reactively — if the next audit re-finds the class, it was not retired.
- **Seeded/faithful routing at the cap.** Both escapes the base path offers at the hard cap
  (increment `theory_attempt`, swap sketches) are forbidden under `--seed`/`--faithful`, so the
  override now states explicitly that the cap still *binds* there and routes into the ship-honest
  check — which fires at the identical 3-consecutive-failure threshold. Without this, a seeded run
  at the cap was told to take an action the override forbids, with no stated alternative.
- **Seeded/faithful safety restriction.** Retire-the-class may only cut claims that are
  `auxiliary` under the override's existing core/auxiliary referent test. A recurring class that
  attaches to a seed-pinned *core* claim must be proved, never cut — without this, the base-path
  retire instruction could have narrowed a pinned core claim before the referent check was ever
  reached. The restriction is explicitly barred from firing the ship-honest check *early*: a
  core-attached class is decided at the 3-failure cap like any other, so it cannot short-circuit a
  seeded run into `abandon_report.md` on a second recurrence.
- **Same fix applied to the Stage 3a empirics-auditor loop** (`--ext empirical`), which carried the
  identical count-based anti-pattern; its hard cap of 5 is retained as the mechanical floor.
- `core.md`'s escalation table gains a **Gate 2 mechanism REVISE** row (the empirical-first gate
  had none at all) and its **Empirics audit fails** row now states the earlier class trigger
  alongside the 5-attempt cap, matching how the math-audit row reads.
- `core.md`'s "Math audit fails" escalation row now reads "3 consecutive audit failures on the
  same theory (hard cap) — or earlier, as soon as an error class survives being retired." This
  closes #157 on both axes: the two docs previously stated different *thresholds* for the same
  event (2 vs 3), and `core.md`'s action ("Abandon this theory version") was stronger than what
  `stage_2.md` actually required (a mandatory *evaluation*, which permitted continuing). The
  Gate-2 hard cap makes the stronger action mandatory, so the row and the SOP now agree.
- **Documented, not silently accepted:** the auditors emit no class-shaped field, so recurrence is
  a prose judgment and "retire across every claim of that shape" has no demonstrated-sweep
  requirement. Both are recorded in `LIMITATIONS.md` with the reason they were not closed by
  adding a ledger (the mechanism #193 documents failing three times) and what would close them (a
  structured `class` field on audit findings — a change to what the auditor *emits*, not a new
  verification pass).

## [2.6.5] — 2026-07-23
Split dev settings from deployed settings, and fixed a silent corruption of the deployed
runtime docs in every `--ext empirical` build.
- **Runtime settings now ship from `templates/`, not from this repo's root.** `.claude/settings.json`
  and `.gemini/settings.json` at the repo root were dual-role: they configured the
  template-development session *and* were the artifact deployed into every research project
  (via the clone in production, via an explicit `cp` under `--local`). The two roles want
  opposite postures — the template repo deploys into arbitrary paths and needs write access
  there, a research project wants the sandbox on. Deployed settings moved to
  `templates/runtime/{claude,gemini}/settings.json`, installed by a new
  `install_runtime_settings` block that serves both branches and overwrites what the clone
  carried in. The repo root keeps its own `.claude/settings.json` for dev work only. Deployed
  paths and their manifest entries are unchanged, so `update.sh` still refreshes them.
- **Fixed: the grok `scorer` agent body was being spliced into deployed CLAUDE.md / AGENTS.md /
  GEMINI.md.** The empirical extension's placeholder-fill step hand-indexes its argv; when
  `.grok/agents/scorer.md` was added as the fourth scorer call site, the slice end and the
  following index were not re-counted. `scorer_files` silently dropped grok (so grok's scorer
  never got the fertility addendum) and `state_loop` read the grok scorer file instead of
  `state_loop_fields_inject.md` — splicing ~300 lines of agent prompt into the `loops` object
  of the pipeline-state spec in all three runtime docs, and dropping the empirical audit-loop
  counters entirely. Affected every `--ext empirical` deployment, theory-first included.
- **Fixed: `--mode report --ext empirical` aborted setup.** Same off-by-one: report mode prunes
  `scorer`, so the misread `open(sys.argv[14])` hit a nonexistent path and killed the run at the
  extension step. The correctly-indexed inject file always exists, so the composition now builds.

## [2.6.4] — 2026-07-21
Report-mode audit: the fan-out reused pipeline-native agent definitions that referenced
artifacts which do not exist in a report deployment. Four fixes, one new assembly layer.
- **`polish-identification` was dead-on-arrival in report mode** — its body auto-N/As when
  the pipeline design artifacts are absent, which they always are in report mode, so every
  report run silently skipped identification auditing. New report-native body overlay
  (`shared_modes/report/polish-identification.md`) audits the submission's *own stated
  design*: estimand-vs-claim, 2026-standard diagnostics, cluster-vs-variation level,
  internal coherence of the identification narrative. Scope decided by the submission's
  content, never by deployment flags
- **Report-mode context inject** (`templates/shared/report_mode_inject.md`) appended to the
  12 pipeline-native audit agents in the fan-out: prompt-passed `submission/` + `audits/`
  paths win over the bodies' pipeline paths, missing pipeline artifacts are skipped not
  fished for, PDF-only submissions get an explicit degraded-check note exactly where the
  missing source weakens the audit's tooling (and no note where it doesn't), helper
  scripts with hardcoded `output/` paths are scratch to be copied into `audits/`,
  `submission/` is read-only
- **Mode metadata overrides** — new `"modes": {"<slug>": {...}}` key in agent metadata,
  merged by all four assemblers (new `--mode` arg, `apply_mode_overrides` in the loader)
  so a mode can re-aim an agent's orchestrator-facing `description`; 16 report-mode
  descriptions added. Zero-behavior-change verified: default and empirical-first builds
  byte-identical to a HEAD baseline
- **Synthesizer coverage halt now has a defined expected set** — Step-1 triage writes a
  `planned_audits:` block into `process_log/audit_log.md`; the synthesizer halts against
  that list (it cannot see the orchestrator's fan-out table, notably under codex where
  workers deliberately do not read AGENTS.md)
- PDF-only degradation list extended from 2 to 6 audits (`math-auditor`,
  `math-auditor-freeform`, `bib-verifier`, `polish-bibliography` join `polish-formula`,
  `polish-numerics`), with the 10 full-strength audits named as explicitly un-noted;
  synthesizer no longer told to expect extension audit files that v1's install-only
  composition never produces

## [2.6.3] — 2026-07-20
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
