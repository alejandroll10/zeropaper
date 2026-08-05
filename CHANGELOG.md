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

## [2.22.2] — 2026-08-05 (current)

**A Codex session started in the template repo now gets the same instructions and dev skills a Claude session does.** Codex loads `AGENTS.md` automatically and discovers repo skills under `.agents/skills`, but `AGENTS.md` here was a three-line pointer at `CLAUDE.md` and the two dev skills (`edit-pipeline`, `deploy-project`) existed only under `.claude/skills` — so Codex could begin template work having read neither. `CLAUDE.md` and `.claude/skills/` stay canonical; `scripts/sync_dev_instructions.sh` regenerates `AGENTS.md` as a copy carrying a generated-file header, and exposes each dev skill as a relative symlink at `.agents/skills/<name> -> ../../.claude/skills/<name>`. The script is idempotent, discovers skills rather than hardcoding a name list (matching the snapshot-based dev-skill handling in `setup.sh`), verifies each link actually resolves to a readable `SKILL.md`, prunes stale links, and refuses outright to overwrite a real file or directory sitting at a mirror path rather than silently clobbering it. It also checks the frontmatter against Codex's two caps, which behave differently and are both measured in **characters**, not bytes — a distinction that bites here, since every one of our descriptions uses em-dashes and `edit-pipeline`'s is 586 characters against 590 bytes. `name` > 64 is a hard failure, because `codex-rs/skills/src/parser.rs` calls `validate_len()` on it and the skill fails to parse. An over-long `description` only warns: openai/codex#29006 (merged 2026-06-19) removed length rejection at load — the parser now checks only that the description is non-empty — and moved the cap to model-visible rendering, where the catalog entry is truncated to 1021 characters plus `...` while the skill itself still loads and `$skill` injection and `skills.read` stay full-fidelity. What degrades is implicit skill selection, which routes off the truncated text. Refusing to sync would therefore be stricter than Codex is. The separate aggregate skills-metadata budget across all rendered descriptions (openai/codex#24299), which also truncates, is deliberately not checked: it is 2% of the context window in **tokens**, not characters — `skill_metadata_budget()` returns `SkillMetadataBudget::Tokens` and falls back to `Characters` only when the context window is unknown, so the `budget_limit=5440` in that issue is `272_000 × 2%` in tokens. It depends on the model and on what else is installed, so it is not knowable from this repo. The shape is a **real** `.agents/skills` directory containing **symlinked skill folders**. The real directory is a `setup.sh` requirement rather than a Codex one — Codex does follow a symlinked `.agents/skills` (per the maintainer on openai/codex#11314, with unit tests for both the global and per-project paths), but in a deployed project that path is where `assemble_codex_skills.py` writes the real Codex skills, so it must be real and writable there, and a wholesale symlink into `.claude/skills` would let a colliding `skill_id` write straight through into the meta-repo's canonical skill. Symlinking `SKILL.md` itself *is* unsupported (openai/codex#9365 — "We support symlinks to a skill directory, not the SKILL.md file itself"). The relative target is `../../.claude/skills/{name}`, and getting that depth wrong fails silently: openai/codex#11314 was closed not-planned precisely because it was never a bug, only an invalid relative target. Codex's live-reload watcher also does not fire through a symlink, so canonical `SKILL.md` edits require relaunching the Codex CLI. `AGENTS.md` is deliberately a copy rather than a symlink to `CLAUDE.md`: `setup.sh` writes `CLAUDE.md` and then `AGENTS.md` by bare filename inside the clone, so a link would be followed and would clobber the deployed `CLAUDE.md` with the Codex runtime doc. Because `.agents/skills` is tracked (a fresh clone has the skills immediately) and deployment happens by `git clone`, `setup.sh` now breaks those symlinks right after the clone, before `assemble_codex_skills.py` — which does `mkdir(exist_ok)` + `write_text` and never wipes — writes the deployed project's real skills into the same directory. That strip needs no checksum guard, unlike the `.claude/skills` one: the assembler only ever creates real directories, so a symlink at that depth is unambiguously a dev exposure. It runs at clone time rather than in the cleanup block because deferring is unsafe — `mkdir(exist_ok)` on a symlink-to-dir succeeds, and a future `skill_id` colliding with a dev-skill name would then have `write_text` write *through* the link into the meta-repo's own `.claude/skills/<name>/SKILL.md`. Both mirrors are dev-only and get no manifest entry. Nothing in git enforces that the generator ran, so the mirrors can still drift silently — a known, open gap tracked in #233. A validator was written and cut before merge: adversarial review found it wrong seven times across four rewrites of its core comparison, twice reintroducing the very false PASS the previous fix had closed, so it is filed as unsolved work rather than shipped half-right. The idempotent generator is the interim answer — running it tells you whether you were out of sync. The generator normalises the environment it inherits before anything depends on it, because each of these can only break them and several did: bash applies an exported `SHELLOPTS` *before* a script's own `set` line, so `noglob` made the mirror globs expand to literal pattern strings — the sync silently did nothing while exiting 0, and the check then reported PASS with a mirror genuinely missing — while `noclobber` turned a leftover `.tmp` into a hard failure; `CDPATH` made `cd` with a bare relative operand echo its resolved path into the command substitutions that derive the repo root, which broke `git commit` outright once the check was wired as a hook; and `GIT_DIR`/`GIT_WORK_TREE` pointed the check at an entirely different repository, reporting PASS while real drift sat unreported (`GIT_INDEX_FILE` is deliberately left alone — a pre-commit hook sets it to the index being committed, which is exactly what should be read). An `EXIT` trap removes the `AGENTS.md` staging file so an interrupted run cannot strand one. It resolves its own path before deriving the repo root, so invoking it through a symlink cannot anchor it outside the checkout. The generator also refuses when `.agents` or `.agents/skills` is itself a symlink: `mkdir -p` no-ops on a symlink-to-directory, after which every link it writes lands inside that target while its `../../` string still assumes the intended location — scattering broken links through a directory the operator never chose, then failing with an error blaming the skill rather than the hijacked path. The post-change review rule in `CLAUDE.md` now names the reviewer per client (Sonnet under Claude, GPT Sol under Codex) instead of "Sonnet-like".

## [2.22.1] — 2026-08-04

**A rejected WRDS credential no longer retries itself into an account lockout.** A PAM rejection arrives as a psycopg2 `OperationalError`, which `_is_conn_error()` classified as a recoverable dropped socket — so it was retried, though retrying a wrong password can never succeed. Because `healthcheck()` calls `_recover()` on every unhealthy ping and `_recover()`'s Tier 2 and Tier 3 each perform a fresh login, a single ping cost two failed authentications, while `start_services.sh` pings up to 120 times and `wrds_start()` another 120. One readiness run against an expired password could therefore fire hundreds of logins; WRDS locked the shared account, taking the empirical pipeline down for every project on the host. Authentication is now a third error class, distinct from connection and query: checked *before* `_is_conn_error()` (which explicitly excludes it), terminal rather than recoverable, and **latched** — the first rejection sets `WrdsState.auth_failed`, after which no code path attempts another login and every command fails fast with `error_kind: 'auth'`. `_latch_auth_failure()` fires from each recovery tier so a Tier-2 rejection cannot fall through and spend Tier 3 on the same doomed credential; `healthcheck()` answers from the latch without touching the network; the server exits 2 at startup instead of dumping a traceback whose proximate cause (`EOFError` from `wrds`'s interactive prompt fallback, under `nohup`) hid the real one. The latch persists to a host-global file beside the pid file, so restarting the server — which `start_services.sh` does at every pipeline launch — is not a free way around the gate; it clears on reboot or logout so a stale latch cannot outlive a fixed credential. Clearing it is an operator action: `python code/utils/wrds_client.py unblock` reloads `.env` with override (the fix lands in the file, while the running server holds the value it was spawned with) and spends exactly one attempt, re-latching on a second rejection and resetting the budget on success; the same command clears a persisted latch and starts the server when none is running. Both readiness loops in `start_services.sh` break on a latch and exit 2 with operator instructions rather than grinding out a generic 120s timeout, and `wrds_start()`'s wait now has three exits (ready / rejected / timeout) including detection of the child's exit code. The WRDS skill gains an escalation rule: a credential rejection is terminal, agents halt and record it in `process_log/degradation_ledger.md`, and must never call `unblock` — that is the operator's approval gate. `scripts/test_wrds_auth_latch.sh` imports the shipped module and stubs only its network edges, covering classification against a real PAM string, one login across 25 pings, zero while latched, restart non-bypass, and both unblock outcomes.

## [2.22.0] — 2026-08-04

**OpenCode Bash/task execution is now OS-confined (#220).** `./launch.sh opencode` wraps the persistent authenticated server and every attached client in Anthropic Sandbox Runtime, while `--once` wraps the whole TUI. The deployed `.opencode/sandbox.json` permits project, project-scoped OpenCode state, and approved cache/runtime writes; denies reads and writes under `~/.ssh` and `~/.aws`; protects Codex auth/config/plugin trees plus project credentials/manifest; and leaves network egress unrestricted for open-ended literature, package, and data hosts. Because SRT's CLI schema requires a finite domain allowlist, a fail-closed adapter uses its library API to request filesystem-only confinement without isolating the host network. The policy, adapter, launcher, OpenCode config, driver helper, and control state are sandbox-immutable; the narrow host driver uses isolated Python and a PATH stripped of sandbox-writable entries, and performs repository progress hashing inside SRT so Git filters/fsmonitor cannot cross the boundary. Missing Linux paths are materialized before bubblewrap resolves policy, credential/path aliases and root execution fail closed, and legacy control state is migrated; a still-live old unconfined server/group must be stopped before either launch mode proceeds. `update.sh` likewise validates managed ancestors and no-follow state/credential files before using host authority. Setup/update, manifest, mocked lifecycle, and `scripts/test_opencode_sandbox.sh` cover deployment, process ownership, allowed project/state/cache writes, protected-control immutability and hard-link denial, denied credential reads and external writes/deletes (including a nested child), and outbound HTTPS.

## [2.21.2] — 2026-08-04

**The codex driver no longer aborts healthy runs whose worker writes its report incrementally (#223).** `wait_for_workers()` decided a detached worker was finished by looking at its output file: non-empty meant done, and that test ran *before* the wrapper-pid liveness probe, so the stronger signal was unreachable for any worker that had written a byte. Several agents — the novelty-checker most visibly — stream their report search by search, so their output file is non-empty from the first result onward. The driver therefore stopped waiting immediately and re-prompted; the orchestrator, correctly obeying poll-don't-relaunch on a live sentinel, spent each turn polling a partial report without committing; five such ~15s turns tripped the fast-cycle guard. Two long finance runs died this way with their worker healthy and minutes from finishing, one of them two minutes before its verdict landed. Liveness now decides and file content only breaks ties: a live wrapper pid means pending regardless of output, and a dead wrapper always clears its sentinel — with a distinct message for the finished-but-uncleaned case, since a sentinel outliving its wrapper also parks the *orchestrator*, which will neither route the finished report nor relaunch a lost worker. Old-format sentinels carrying no wrapper pid fall back to the file, but now require it to be both non-empty and untouched for `WORKER_STALE_MTIME` (default 600s) — a still-streaming report keeps its mtime moving, which mere non-emptiness cannot distinguish. The stuck-model abort additionally prints any sentinel still present, because that fact alone redirects the post-mortem away from "the model is refusing." Both `stat` probes and `date` are digit-validated rather than trusted, since GNU `stat -f` is filesystem mode with a different format-sequence set and a literal `%m` reaching `$(( ))` would be a fatal arithmetic error under `set -e` — killing a driver that should merely have kept waiting. `scripts/test_launch_workers.sh` sources the shipped function out of `launch.sh` and covers all of it: streaming output, both dead-wrapper cases, pid reuse, cap timeout with its `WAIT_CAPPED` accounting, the mtime threshold on both sides, and a stubbed `stat` returning junk. The opencode driver is unaffected: it tracks background work through server-side quiescence, not sentinels. One assumption this leaves standing — worker liveness is inferred from the wrapper pid, so a pid-targeted kill can orphan a still-writing worker — is now recorded in `LIMITATIONS.md`.

## [2.21.1] — 2026-08-04

**OpenCode server replacement now proves whole-process-group termination (#222 follow-up).** The v2.21.0 cancellation boundary authenticated the server leader by PID/start/PGID/command, but waited only for that leader PID to exit. A TERM-resistant Bash/tool descendant in the same server process group could therefore outlive the leader and continue mutating artifacts after a replacement server and recovery baseline were published. Shutdown now authorizes the exact group while the leader identity is still valid, tracks group liveness through TERM and KILL, and clears server state only after the entire PGID is confirmed gone. KILL escalation is group-only after authorization, avoiding a PID-reuse target; startup reaping revalidates the exact PID/start token and rechecks PGID before escalation. A durable startup marker closes the pre-identity crash gap and makes later launchers fail closed if an incomplete server may remain alive. If a later launcher finds the recorded leader gone but its group still alive, it retains the identity and fails closed rather than signaling an unauthenticated group or starting a replacement. A lifecycle fixture covers a server leader that exits on TERM while its same-PGID descendant records and ignores TERM.

## [2.21.0] — 2026-08-04

**OpenCode background subagents now work in unattended pipelines (#222).** OpenCode's experimental `task(background=true)` support is viable only while the server that owns its in-memory job registry remains alive: a plain ephemeral `opencode run` exits with its client and aborts the child, while `opencode serve` plus an attached client lets the child finish, injects its result into the parent, and autowakes the parent without another client. The launcher now uses that verified architecture. It starts or reuses an authenticated localhost server, attaches every headless turn to it, and enables `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS`; older OpenCode versions whose task schema omits `background` continue through foreground calls.

The driver does not race the native wakeup. After an attached turn exits, a new stdlib-only control client follows the parent and its direct child sessions through OpenCode's HTTP API, causally pairs each launch generation with its own persisted synthetic completion/error user notification and a later completed/error parent response, discovers further background generations spawned by that response, and only then accepts two stable all-idle samples before issuing an external continuation. Generation identity matters because resuming a `task_id` reuses its child session ID. The parent-bound pending-generation ledger is reconstructed and atomically replaced from parent messages after a driver restart; an always-present parent/server epoch plus a server-instance-bound history baseline detect replacement-publication crashes and retire generations that can no longer notify, while even a reused parent with no pending generations must reach stable quiescence before another prompt. Turn timeouts kill only the attached client's process group, cancel every child and the parent, confirm status-only quiescence, and replace the server instance before advancing the baseline, so no late notification/autowake can cross the cancellation boundary. Recovery intent is durable and idempotent: a unique token remains on disk until it is observable in a native user prompt, letting restart distinguish “not dispatched” from “already dispatched” without duplication. Terminal pipeline states and signals shut the server down; nonterminal driver failures and exact-but-temporarily-unhealthy servers are preserved so a later launch can reuse in-flight work without treating transient API failures as a restart or duplicating a prompt.

A kernel-held project `flock` prevents concurrent launchers from prompting the same parent or stopping each other's server. Server cleanup validates PID, start token, process-group leadership, and the expected `opencode serve` command before group signaling. Startup traps cover partial state, server identity is published as one atomic bundle, a partial cached state is recovered through its PID/start identity, and the random server password is created atomically at mode `0600`; the launcher also fixes the Basic-auth username rather than inheriting a conflicting caller setting. All runtime state lives under ignored `process_log/` paths, malformed API/event/state shapes fail closed, and a pre-dispatch first-turn quarantine is removed only after exactly one consistent session ID is atomically cached and validated as local, preventing interrupted parent creation from duplicating. Session discovery accepts only nonempty absolute directories resolving to the physical checkout.

The upstream boundary remains explicit: background-job state is process-local, so a server crash can still interrupt an uncheckpointed child. Recovery restarts the server and instructs the parent to reconcile child transcripts and required artifact paths before resuming or relaunching once. OpenCode session/manual/report guidance now uses background work only for independent fan-outs, forbids polling and duplicate launches, and requires artifact verification at gates. Tests cover API auth, local-session filtering, a deliberately delayed child-idle → notification → parent-autowake transition, pending-child reconstruction, partial abort failure, delayed cancellation quiescence, multiple-child abort ordering, concurrent-driver rejection, interrupted startup, partial-state recovery, fresh/reused servers, timeout recovery, fail-closed first-turn reconciliation, terminal cleanup, and deployment-manifest installation.

OpenCode still has no native `/loop` command; the persistent launcher remains the unattended continuation loop.

## [2.20.0] — 2026-08-03

**OpenCode runtime.** Deployments now include `.opencode/agents/*.md` generated from the shared agent metadata and bodies, with per-agent permissions and every tier mapped to `opencode/deepseek-v4-flash`. Base, variant, mode, and extension assembly paths all participate; pruning, injections, marker resolution, and the deployment manifest cover the fifth agent tree.

OpenCode reuses the existing Claude-compatible `SKILL.md` catalog through its native on-demand `skill` tool. The launcher selects `.claude/skills` explicitly to avoid duplicate IDs from the parallel `.agents/skills` compatibility tree. Shared `AGENTS.md` guidance now dispatches OpenCode agents through foreground native `task` calls.

`./launch.sh opencode` provides a resumable non-interactive session driver with stale-session validation, terminal-state detection, and a five-turn no-progress cost guard; `--once` opens the interactive TUI. `opencode.json` pins the model and project file-tool permissions. OpenCode Bash is not kernel-sandboxed, so the security limitation is stated in README and `LIMITATIONS.md` rather than implied away.

Follow-up hardening makes unattended execution explicit: session sharing is disabled, `doom_loop` cannot block waiting for approval, every turn has a process-group watchdog, and the cost guard distinguishes completed native subagent work from empty fast turns while retaining an absolute churn ceiling. Timeout shutdown gives Bash descendants the configured grace period before killing them. Cached and reconciled sessions must belong to the current physical checkout, and reconciliation fails closed when its pre-run session snapshot is unavailable. OpenCode agents receive foreground/checkpointed Bash guidance instead of Claude's unsupported `run_in_background` argument. A mocked launcher regression suite covers interactive launch, fresh/resumed/stale/malformed and cross-project sessions, invalid reconciliation baselines, substantive-tool progress, descendant cleanup, and forced timeout recovery.

The launcher safely exports the project `.env`'s `OPENCODE_API_KEY` without evaluating the file, while preserving an already-exported value. This makes the documented per-project credential path work for both interactive and headless launches without requiring a separate shell export or global OpenCode auth state.

---

## [2.19.0] — 2026-08-03
**`--light` now means light, including the orchestrator.** v2.18.2 fixed the flag's *subagent* half on codex; the first real light run under `./launch.sh codex` immediately exposed the other half — the banner read `model: gpt-5.6-terra`, because the orchestrator is launched by `launch.sh` and inherited the CLI's session default. Every subagent was Luna; the one process doing stage routing, gate decisions, and the whole fan-out was not. Same story on claude and gemini. The flag now pins both halves.

**Two mechanisms, because the halves are pinned at different times.** Subagents are pinned at assembly time (`--model-override` through each assembler's tier table). The orchestrator is pinned at launch: `--model <tier>` for claude and gemini, `-c model="<tier>"` for codex. The codex form is deliberate — `codex exec resume` accepts only `-c`, and the driver resumes on every turn after the first, so a flag-form pin would have applied to turn 1 and silently reverted for the rest of the run.

**The launcher does not carry a fourth copy of the tier table.** `light_orchestrator_model` reads the tier *back* from the assembled agents — the only copy guaranteed current: it already went through each runtime's own `MODEL_MAP`, it survives `update.sh`, and on claude it reflects the launch-time heal that runs immediately before. The pin fires only when `.deploy_manifest.json` records `flags.light` **and** every assembled agent agrees on one model. The manifest check is what makes it correct rather than merely plausible: grok's roster is uniform (`grok-4.5`) in *every* deployment, so roster uniformity alone would have pinned a "light" tier on runs that never asked for one. Grok's branch doesn't consult the helper at all — single-model table, nothing cheaper to drop to.

Best-effort in the safe direction throughout: a pre-manifest deployment, an absent `python3`, or an unreadable agents dir yields no pin and the launch proceeds on the CLI default. Verified against three real deployments — a light one (codex `gpt-5.6-luna`, claude `sonnet`, gemini `gemini-3-flash-preview`), a non-light one, and a pre-manifest one; only the first produces a pin.

**Stated plainly in the docs rather than buried:** the orchestrator is the single process where a cheap model costs the most, so `--light` is now documented as a deliberate choice for drafts, smoke tests, and runtime shakedowns — not a default for a paper you intend to submit. That is a real trade the flag now makes on your behalf, and it should be visible before you pick it, not after.

---

## [2.18.2] — 2026-08-02
**`--light` becomes a real flag on the codex runtime.** It was a Claude-side flag wearing a cross-runtime name: `setup.sh` passed `--model-override sonnet` to the claude, gemini, and grok assemblers, but `assemble_codex_subagents.py` had no such argument, so a `--light` deployment launched under `./launch.sh codex` ran the full pinning — 7 agents on Sol, 27 on Terra, only 17 on Luna. The gap was invisible while every codex agent was a flat `gpt-5.5` and became a silent cost bug when the per-agent Sol/Terra/Luna tiering landed. It was documented as a known limitation rather than fixed; this closes it.

The codex assembler now takes `--model-override` and maps the Claude alias through its own tier table (`fable → gpt-5.6-sol`, `opus → gpt-5.6-terra`, `sonnet/haiku → gpt-5.6-luna`), so the argument is reusable for any future non-light override, not just `--light`. All five codex call sites now carry the override — `assemble_codex_{shared,variant}_agents` in `setup.sh` (via its `MODEL_OVERRIDE_ARGS` array), plus the empirical applier's shared and variant blocks and the theory_llm applier's single block (via each applier's own `MODEL_OVERRIDE_ARG`, populated from a positional arg, since they run as separate `bash` subprocesses that inherit no arrays). The three in the appliers are the ones that would otherwise have left `--ext empirical` / `--ext theory_llm` agents at full tier in an otherwise-light build.

**The override drops `model_reasoning_effort` too**, mirroring the Claude assembler dropping `effort`. The pinned levels (37 `high` / 17 `medium` / 1 `low` across the full 55-agent metadata inventory; 33 / 17 / 1 in the 51-agent finance build below, which excludes macro's own `empiricist` plus the three agents pruned unless their flag is set — `report-synthesizer` (`--mode report`), `mechanism-auditor` (`--mode empirical-first`), `faithful-drift-auditor` (`--faithful`)) are calibrated to each agent's *ideal* tier; carrying `high` onto a Luna worker keeps the token bill the flag exists to cut. `launch_agent.sh` already defaults to `medium` when the field is absent, so a light codex agent runs Luna/medium with no launcher change.

Verified by build diff: a no-`--light` finance build with both extensions is byte-identical to its pre-change baseline (the only diffs are the per-deploy random fingerprint and the version stamp, neither of which this change touches); the `--light` build changes nothing outside `.codex/agents/`, where all 51 agents now read `model = "gpt-5.6-luna"` with no effort line. `llm_cognition --light` (40 agents) and `finance --mode report --light` (18) collapse the same way.

Grok is unaffected by construction — its tier table is a single model (`grok-4.5`), so the override is already a no-op there. Untouched by design: the `codex-math` skill (pinned `gpt-5.6-sol` as a *tool*, not a subagent) and the Claude launch-time heal (which already re-decides against the `--light-model` recorded in `code/utils/model_heal/config.json`).

An existing light deployment refreshed with `update.sh` picks the fix up automatically — the flag is replayed from `.deploy_manifest.json`.

---

## [2.18.1] — 2026-08-01
**The Stage-0 domain scope becomes checkable without becoming closed (#218).** v2.18.0's `stage-0-discovery-exhausted` branch bounded itself on "which domains are already spent," but that set lived only in the free text of every prior `branch_manager_discovery_p*.md`, so a fresh `branch-manager` had to re-derive it by reading N growing reports — and two firings could describe the same domain in different words and each read the other as untried.

Fixed by moving the record to where the choice is made rather than where it is reviewed. Step 0a now appends every domain it scans to **`output/stage0/domain_log.md`** (`{domain} — fresh scan` / `{domain} — corrected re-scan: {correction}`), a run-scoped log the Stage 0 entry hook never clears — the deliberate contrast with its sibling `gap_log.md`, which is per-pass. Dedup is now an exact read of one log written by the scanning step itself.

**The issue asked for a closed `DOMAIN_LIST`; that part was declined on the merits.** A machine-readable per-variant enumeration would make the 2 × |domains| bound numeric, but it would also let the pipeline mistake "covered the enumeration" for "covered the field" and freeze each variant's domain space at whatever `setup.sh` happened to name — the failure the repo's *prefer no structured classes* principle exists to prevent. The scope stays prose and is now explicitly documented as **starting points, not an exhaustive list**; `branch-manager` may name an in-scope domain the scope does not list. The cost is stated in `LIMITATIONS.md` rather than hidden: with an open domain space, termination rests on branch-manager's judgment that nothing materially different remains, not on an enumeration running out. What the log removes is the *silent* half of the failure.

**No migration path, deliberately.** A backfill — reconstructing the log from pre-2.18.1 reports for a deployment `update.sh`-ed mid-Stage-0 — was written and then removed. Three consecutive review rounds each found a defect in it and none in the fix proper: it demanded correction wording those reports never persisted, it parsed a report section this same diff deletes from the template, and every trigger placement left an ordering hole that let a later Step 0a create the log with only the current domain and permanently satisfy the "does it exist" check. The population it serves is v2.18.0 deployments — released the same day — that are mid-Stage-0 in exhausted discovery when the refresh lands. The residual cost is one possibly-redundant re-scan in such a run, self-correcting from that point; the gap is recorded in `LIMITATIONS.md` rather than guarded.

**Net-negative on rules, as the fix should be.** Gone from `branch-manager.md`: the "Domains already spent" report section (the log is the record), the "your report is the durable record" rule, and "every prior `branch_manager_discovery_p*.md`" from the context's input list — which also stops that input growing without bound.

**`--variant macro` gained a real domain decomposition.** Its `DOMAIN_AREAS` was the bare string `"macroeconomics"`, so RESCAN-NEW-DOMAIN had nothing to name and the branch degenerated to one corrected re-scan then OPERATOR-ESCALATE. It now names monetary, fiscal/public debt, growth, labor search, international, heterogeneous-agent, expectations, macro-finance, and business-cycle measurement, with the same sufficient-not-necessary scope clause finance and llm_cognition carry.

**Two live mid-sentence `{{DOMAIN_AREAS}}` embeds fixed** — the same class v2.18.0's round-4 review caught in agent bodies, still present in `core_manual.md` (rendered a double period under `--manual` for finance and llm_cognition) and `core_report.md`. Both now point at the **Variant context** / **Submission domain** line instead of interpolating a paragraph mid-clause. Making macro's value a paragraph would otherwise have extended the bug to a third variant.

All seven configurations (`finance`/`macro`/`llm_cognition` defaults, `--mode empirical-first`, `--mode measurement-first`, `--mode report`, `--manual`) build clean with no placeholder leakage and no double periods.

---

## [2.18.0] — 2026-08-01
**The unrouted-state cluster — five issues that were one defect.** #156, #159, #160, #215, and #216 were filed separately over five weeks; tracing them found a single shape: **a lane exits or re-enters without executing the verification its output depends on.** Fixed as one pass, and four of the five closed by *subtraction* — the change set is net-negative on pipeline rules and touches no assembly logic.

**Two of the issues described the wrong fix, and the corrected scope is smaller.**
- **#216** asserted that the Stage 6 downgrade enrich-the-core lane (2a) was the only re-entry skipping Gate 4. It is not: the **Reject deepen** lane (`stage_6.md` Gate 5 Reject → branch-manager SUBSTANTIVE) returns to Stage 6 the same way, after the same `theory_version` increment and evidence re-fire. What made 2a look unique is that the *Major Revision* lane reaches Gate 4 only when it routes through the deepening playbook — which fires on structural concerns or a plateau, not on routine `[FIX]` cycles. So instead of re-verifying staleness at 2a's return point (patching one of two instances and duplicating Gate 4's logic at a second site), `stage_6.md` gained a single **evidence-currency entry precondition**: before *any* Stage 6 run, the mode's staleness pointers must equal `theory_version`. One site, every lane, including any added later.
- **#215** reported that theory-first llm_cognition figure markers go unscanned, and proposed a fourth scan arm plus an extension-keyed marker family. The root cause was upstream: **`paper-writer.md` contradicted itself** — its numerical-claims rule said to always write `[NEEDS THEORY-EXPLORER]` while its figure rule said to name the true producer. A fourth arm would have left that in place. The numerical-claims rules now name the producer by source directory, and the three near-duplicate scan arms in `stage_5.md` step 5 (`NO_MODE` / `MEASUREMENT_FIRST` / `EMPIRICAL_FIRST`) collapsed into **one generic rule** that scans every producer form, routes each to its stage's re-fire procedure and reviewer gate via a table, and returns a marker naming a non-existent producer to paper-writer to re-name. Net −2 arms, no new marker family. It also closed an unfiled sibling: under the modeless default with `--ext empirical`, the old `NO_MODE` arm scanned only for `[NEEDS THEORY-EXPLORER]`, so a legitimate `[NEEDS EMPIRICIST]` figure marker went unscanned there too.

**Stage 0 no longer abandons a project that has not run out of places to look (#156).** Exhausted discovery routed to "the orchestrator's standard abandonment/escalation path" — which never existed anywhere in the repo. Tracing the trigger showed the dead end was also *wrong*: `gate0_best_question_score == -1` is reachable only when every gap was logged `closed`/`no-stake` at Step 0c, i.e. gap-scout killed the whole scan **before `question-poser` ever ran** — evidence about the one domain Step 0a scanned, not about the field. So the terminus is now a routed decision: a new `branch-manager` context (`stage-0-discovery-exhausted`) recommends RESCAN-NEW-DOMAIN, RESCAN-CORRECTED, or OPERATOR-ESCALATE, the last setting `status = "halted_no_viable_question"`. The loop is bounded without a new counter — one fresh scan plus at most one corrected re-scan per domain, recorded in the reports themselves.

**Seeded abandons are now mechanically terminal (#160).** Six seed/faithful sites wrote `output/seed/abandon_report.md` with no `pipeline_state.json` status token, so a resumed session could not distinguish "halted, needs a human" from "paused mid-stage" and would re-enter the stage the abandon decision was meant to end. Rather than repeat a clause six times, one rule in `seed.md` and `faithful.md` binds `status = "halted_seed_abandon"` to the act of writing the report — future abandon sites inherit it. `session.md` gained a third halt class, **decision halts**, for the case where nothing is broken and no configuration is wrong: the pipeline judged the work not worth continuing.

**The scorer's Surprise guard no longer silently no-ops (#159).** Seed/faithful Gate-3 routed straight to Stage 4, so `output/stage3/implications.md` was absent and the scorer's SUPPORTED-cap / PUZZLE-CANDIDATE-floor rules — gated on that file existing — never fired, in exactly the modes where the idea is pinned and cannot be swapped. The file turned out to be consumed in three places (scorer, `paper-writer`'s Stage 5 input list, `puzzle-triager`), so the minimal fix would have meant adding three "if it exists" qualifiers. Instead the exception was closed: both Gate-3 overrides now run Stage 3 (Stage 2b stays skipped, and the limitation note narrowed to say so), seed/faithful back-fill entry at Stage 4+ carries a Stage-3 prerequisite, and the scorer's existence-conditional was **deleted** as dead.

**Five review rounds, four of which found a real defect.** Round 2 caught two fixes applied to `seed.md` and never mirrored into `faithful.md` — including a "terminal abandon" rule that omitted faithful's Gate 2 site (`faithful_overrides/` has no Gate-2 file, so faithful falls back to the shared seed one, which branches on `--faithful` internally) and would have reproduced the very bug it was written to prevent. Round 4 caught `{{DOMAIN_AREAS}}` embedded mid-sentence at 7 sites: harmless for macro's bare `"macroeconomics"` string, but finance and llm_cognition set it to a prose paragraph ending in its own period, so deployments rendered double periods and run-ons. Fixing it removed the need for the placeholder in an agent body at all — `branch-manager` already receives the domain via its injected Variant context section — which let the entire `setup.sh` vocab-plumbing change from earlier rounds be reverted. **`setup.sh` is untouched by this release.**

All ten configurations (`finance` default/`--seed`/`--faithful`/`--mode empirical-first`/`--ext theory_llm`/`--mode report`, `macro`, `llm_cognition` default/`--mode measurement-first`/`--mode report`) build clean with no placeholder or marker leakage. LIMITATIONS.md: the theory-first marker-scan entry is marked **closed** (noting the actual fix differed from the one it predicted), and one new limit is documented — the Stage-0 re-scan bound rests on `DOMAIN_AREAS` being prose rather than an enumerated list, so it degenerates for `--variant macro`, whose scope is a single opaque string.

---

## [2.17.1] — 2026-08-01
**#199 post-ship review — measurement-first coherence fixes.** An eight-round review loop (independent reviewers per round; each round reviewed the previous round's fixes) found and closed fourteen defects in the v2.17.0 measurement-first shipment. Most shared **one root cause: `THEORY_FIRST` blocks are kept under measurement-first** (the mode is theory-shaped), so every theory-first block silently assuming *Stage-2-time* audits or Stage 2b shipped into MF unchanged. Converted to `NO_MODE` with MF twins added:
- the escalation table's math-audit row told MF to **abandon the theory version** on a failed characterization — the exact inverse of `stage_2.md`'s rule that the measurements survive and the first escalation is a narrower claim class (a run would have discarded a completed, expensive Stage 3b experiment set because the post-hoc formalization failed to audit);
- `paper-writer`'s numerical-claims rule and `stage_5.md`'s marker scan both routed to `theory-explorer` + `output/stage2b/`, neither of which exists under MF — now `experiment-designer` + `output/stage3b/`;
- `idea-reviewer`'s ADVANCE handoff instructed theory-generator to prove theorems, which construct mode's own rules refuse.

Beyond that class: `puzzle-triager`'s **Theory-formality axis** was undefined under MF and systematically forced BACK-TO-IDEA — triage always fires before any characterization exists, so "audits incomplete" was literally true on every invocation, making PIVOT unreachable for exactly the Stage-3b contradictions the mode exists to surface (the axis now scores on the design gate). `experiment-reviewer`'s body and output template assumed a completed run while Gate 2 launches it at **plan time**; it now carries a `MEASUREMENT_FIRST` "Two invocations" section with its own inputs, output template, and ACCEPT semantics, and scores the plan's *commitments* rather than faulting it for artifacts it cannot yet have. `math-auditor`'s automatic-unverified rule accepted only an `output/stage2b/` citation, so under MF **every legitimately measured number** would have been listed as unverified, inverting what the `## Unverified claims` section means to the scorer — re-pointed to `output/stage3b/`. `stage2_design_version` added to the runtime doc's state JSON and field glossary; the design-gate cap corrected from "3 consecutive REVISEs" to its actual "3 consecutive non-ACCEPT verdicts" (the verdict set includes REDESIGN); the deferred-audit MF block now explicitly supersedes the contradiction-check NONE bullet it contradicts.

**The `stage3b_theory_version` re-set no longer rests on the orchestrator's reading of prose.** `theory-generator` emits a `NEW-TESTABLE-CONTENT:` line as a **mandatory output header** of every characterization, keyed on *load-bearing* in the math audit's sense (anything else depends on it) rather than on which paragraph the claim was filed under — so the conjecture paragraph is not an exemption. A characterization lacking the line is incomplete output, not a new version: it is re-fired at the same `theory_version` before being audited or committed, and because the audit-FAIL loop re-launches characterization mode on its own, that check lives at the audit itself and re-applies to every re-fire. A wrong call here ships a formal claim nothing measured past a clean-reporting H3.

**Resolver ordering fix.** Adding a second mode block at an existing site exposed a latent bug: the resolver interleaved block-removals and marker-strips by family, and the removal pattern's `\n{0,2}` would eat a blank line that a *neighbouring* block's strip had just exposed — silently gluing the empirical-first `idea-reviewer` ranked list onto its ADVANCE header. `setup.sh` now runs every removal before any strip, making output independent of family order so a new mode block cannot perturb other modes. New `test_scripts/test_marker_resolver_adjacency.sh` guards the invariant (verified non-vacuous against the old ordering).

21 new llm_cognition tripwires. `finance`/`macro`/`llm_cognition` default, `finance --mode empirical-first`, and `llm_cognition --mode report` all verified **byte-identical** to the pre-change baseline; `macro --mode report`, `llm_cognition --manual`, and MF × `--seed`/`--faithful`/`--light` verified to build clean. One pre-existing gap found and documented rather than fixed (out of scope, affects theory-first llm builds): Stage 5's marker scan has no `experiment-designer` arm there, so a correctly-named Stage-3b figure marker goes unscanned — see LIMITATIONS.md.

## [2.17.0] — 2026-07-31
**#199 — `--mode measurement-first` ships for llm_cognition.** Evidence-first pipeline shape for the modal ML cognition paper: Stage 1 sketches candidate constructs/task families (idea-generator + idea-prototyper overlays; the prototyper may run a toy-scale pilot); Stage 2 `theory-generator` runs in **construct mode** (construct definition + task family + scoring rule + measurement plan); Gate 2's binding half is a **plan-time design gate** (`experiment-reviewer` on the plan, `stage2_design_version` state field) and the **math-audit pair is deferred, not skipped** — after Stage 3b (the evidence core) completes, theory-generator re-enters in **characterization mode** to formalize what was measured and both audits fire there, with H3 gating on all three legs. Stage 2b skipped. New overlay assets: `templates/agents/llm_cognition_modes/measurement_first/vocab.json` (27 keys) + 5 body overlays under `shared_modes/measurement_first/` (including a construct-validity `referee-mechanism`). The mode-marker resolver rewritten generically over four families — `EMPIRICAL_FIRST`, `MEASUREMENT_FIRST`, `THEORY_FIRST` (any theory-shaped pipeline: default AND measurement-first), and new `NO_MODE` (strictly modeless; used where a mode block replaces the default content) — verified byte-identical across all 8 existing build configs. 17 new regression checks. The theory_llm applier's no-mode-overlay gap is documented in LIMITATIONS.md (the design-gate framing reaches experiment-reviewer via the launch instruction). Review round 1 caught and fixed three criticals before ship: the theory-first Stage 2b procedure leaking into MF builds (converted to `NO_MODE`), the characterization's `theory_version` bump tripping the Stage 3b staleness trigger + Gate 4 block (explicit `stage3b_theory_version` re-set rule with a new-testable-content exception), and puzzle-triage lacking MF routing + the load-bearing `stage2_design_version` PIVOT reset (MF mode note + inline reset added; the PIVOT/step-3 inline additions and the stage_2 step-2 parenthetical are small intended doc deltas in all variants). Also: the MF revisions bullet in stage_4 conditions the prior-audit read on file existence, and the Gate-2 seed override names the MF verdict/cap set.

## [2.16.0] — 2026-07-31
**#204 — llm_cognition `--mode report` ships.** The report-mode overlay bodies are parameterized on the byte-identical-default pattern: the report `referee-mechanism.md` reuses the base body's `MECH_*` keys (26 substitutions; zero econ residue), so the v2.9.0 ML overrides apply for free — with `MECH_EVAL_FRAME` re-anchored per variant in the `{variant}_modes/report` overlays (report mode names the math-auditor explicitly). `referee-core`/`referee-freeform` report twins gain `REFEREE_VERDICT_NOTE` (conference-cadence verdict translation now reaches report builds), `REFEREE_RESHAPE_DISCIPLINE`, and `REFEREE_TOP_OUTLET`; `MECH_PRIMITIVES_OUTPUT_GUIDANCE` also closes a previously-uncensused econ line in the *base* referee-mechanism ("preference / information / technology / market-structure choices" → construct/stimulus/scoring for ML). New `templates/agents/llm_cognition_modes/report/vocab.json` (ML venue role + report eval frame + a report-anchored `REFEREE_VERDICT_NOTE` — review caught that the base note routes through the editor agent and tier table, neither of which a report deployment has; the override re-anchors routing to the report-synthesizer); gate flipped in `setup.sh`; theory_llm auto-imply skipped under report mode (its agents get pruned there anyway); `core_report.md` triage example neutralized. The report `polish-identification` stays content-scoped by design. Finance/macro report builds byte-identical except the neutralized triage line. Tests: the llm regression test gains a 14-check report-mode section, and a new `test_scripts/test_report_mode_assembly.sh` guards the econ variants' report frames against silent overlay-vocab loss (the migration's one new degradation surface).

## [2.15.1] — 2026-07-31
**#206 — third tonal-extraction pass.** The residual econ worked examples in shared bodies are vocab-keyed with byte-identical econ defaults + ML overrides: `debugger` (context items, model-failure/data-query bullets, the V_S=V_U fix exemplar → an exact-match-scorer exemplar), `last-resort` (binding constraints, different-avenue exemplar), `style` (philosophy-opener "Economists have long debated…" → "Large language models have transformed NLP…", the power-utility "assume" exemplar), `triager` (DECORATIVE remedy + claim wording via `MECHANISM_QUALIFIER`, Berk-Green dedup exemplar, stakes row via `PP_STAKES_TERM`), and `paper-writer`/`polish-consistency` "economic content" → `{{MECHANISM_QUALIFIER}} content`. `sympy`/`codex-math` skill docs (no vocab pass) reworded domain-neutral. Second-round review caught two survivors in `paper-writer` (the results-section "Economic intuition" bullet and the throat-clearing rule's own "Economists have long…" snippet — both now keyed) and three finance-flavored defaults inappropriate for macro (PERMNO/GVKEY data-query identifiers, the Berk-Green dedup exemplar, the V_S=V_U fix exemplar — macro overrides added: FRED/SAAR identifiers, a Smets-Wouters exemplar, a HANK steady-state exemplar). Remaining labeled cross-variant examples documented as accepted in LIMITATIONS.md — #206 closed. Finance agent bodies verified byte-identical; 10 new llm regression tripwires.

## [2.15.0] — 2026-07-31
**#205 — per-variant skill gating + stale-infrastructure sweep.** `setup.sh` gains `variant_wants_skill` (llm_cognition excludes `ssj` + `nber-agenda`): the gate covers Claude/codex skill assembly, the `code/utils/{ssj,nber_agenda}` copies, the `sequence-jacobian` deps install, and the manual-mode skill catalogs, so an llm_cognition deployment no longer carries inert economics toolkits in its skills listing (finance/macro builds byte-identical; the manifest is presence-filtered so no emission change was needed). `update.sh` gains a generic **stale-infrastructure sweep**: paths recorded in the target's old manifest but absent from the fresh manifest are removed on refresh (dry-run aware, path-traversal guarded, `.env` never swept) — pre-gating llm_cognition deployments converge on their next update, and retiring any future manifested path needs no update.sh edit. `core_manual.md`'s helper list neutralized to per-variant wording; regression test extended (gated dirs absent, manifest clean, core skills kept).

## [2.14.0] — 2026-07-31
**#200 — llm_cognition paper skeleton + ML section list.** llm_cognition deployments now ship an ML-preprint skeleton (`templates/paper_skeleton/llm_cognition/{main,internet_appendix}.tex.template` — single-column 10pt, numeric `natbib`/`unsrtnat` citations, theorem environments, a post-references checklist `\input` slot; venue-neutral by design, the official venue style file remains a manual camera-ready swap, see LIMITATIONS.md). The skeleton lookup in `setup.sh` is variant-aware with root-template fallback, so future variants opt in per-file. New **generic variant markers** in the marker resolver (`<!-- VARIANT_{NAME}_START/END -->`, kept for the matching variant, removed wholesale otherwise — no resolver edit per new variant): used to add `related_work.tex`, `experiments.tex`, and `checklist.tex` to `docs/stage_5.md`'s section list and `paper-writer`'s per-section guidance for llm_cognition only (finance/macro builds verified byte-identical). Page budget vocab-keyed as `PW_LENGTH_RULE` (econ default byte-identical; ML override calibrated to the ~9–10-page single-column norm). Checklist substance grounds in `output/stage3b/experiment_results.md` scope/seed/provenance statements (re-verified by `polish-experiments` at Stage 9). Also: the v2.10.0 econ-leak tripwires in `test_scripts/test_llm_cognition_assembly.sh` silently never ran on stock macOS (bash 3.2 misparses the `declare -A` literal and dies with an `unbound variable` under `set -u`) — rewritten portably and extended with skeleton/section-list/marker-leakage checks.

## [2.13.2] — 2026-07-31
Hardening follow-ups to v2.13.1's two investigations (issues #212, #213).
**#213 — codex proxy-auth version floor:** codex-cli ≤0.144.x sends no `Proxy-Authorization` on HTTPS CONNECT tunnels, so behind an authenticated proxy every request — including the OAuth token refresh — fails transport-level with no HTTP status, masquerading as an auth problem (fixed upstream in 0.146.0, but a pin or rollback silently reintroduces it). New `code/utils/codex_preflight.sh` (deployed + manifested) warns — never blocks — when an old codex meets a credentialed proxy env; sourced at `launch.sh codex` startup, at every `launch_agent.sh` worker dispatch (codex can auto-update or roll back mid-run), and at every codex-math `codex_leaf_setup`, with the version lookup under a 10s watchdog so a hung binary can't block a launch. Full diagnosis + the header-injecting relay standby remedy recorded in LIMITATIONS.md.
**#212 — home-dir cache sweep:** audited the declared empirical deps for the `~/.edgar` pattern (a `$HOME` default cache outside the sandbox writable sets). No unfixed hits: `wrds` writes `.pgpass` only via an interactive path that env credentials bypass, `gdown`'s `~/.cache/gdown` is writable in every confining runtime, `openassetpricing` buffers downloads in memory, `fredapi`/`pandas-datareader`/`requests` keep no persistent cache. The audit record and a check-before-adding-a-dep guard now head `extensions/empirical/deps.txt`.

## [2.13.1] — 2026-07-31
Four deployment-correctness fixes: three from the 2026-07-31 EDGAR investigation (issues #209, #210, #211) plus a codex_math output-path defect found in the same day's sandboxed-codex investigation (no issue number; the companion upstream proxy-auth finding is tracked as #213).
**#211 — stale `.env` propagation:** `setup.sh`'s `.env` copy was an either/or (`cp` personal `.env`, *else* scaffold from `.env.example`), so a personal `.env` predating a key silently deployed without it — observed as fresh projects missing `SEC_EDGAR_*` entirely, with `edgar_utils.py` falling back to its placeholder identity. The copy is now a **union**: after copying `.env`, any key present in `.env.example` but absent from the copy is appended blank. The merge routine is extracted from `update.sh` into shared `scripts/merge_env_keys.sh` (build-time only) and sourced by both scripts, so the trailing-newline guards stay single-sourced instead of re-diverging (the v2.11.1 bug class).
**#210 — EDGAR cache outside the sandbox:** edgartools writes its local data store to `~/.edgar` by default, which is outside every runtime's writable set → `PermissionError` on first fetch. Rather than widening three per-runtime sandbox configs, `get_edgar()` now defaults `EDGAR_LOCAL_DATA_DIR` to `data/edgar_cache/` inside the project before the lazy `import edgar` (blank `.env` value counts as unset); the edgar skill's Setup snippet sets the same env var before `from edgar import *` for direct callers, with a new gotcha bullet; `data/edgar_cache/` is gitignored in deployments; `.env.example` documents the override, commented out.
**codex_math `/tmp` output path:** `codex_verify.sh` / `codex_write.sh` / `codex_explore.sh` wrote their `-o` result file to a hardcoded `/tmp/...`. On macOS `/tmp` is a symlink to `/private/tmp`, which sandbox write allowlists carrying the literal `/tmp` entry don't cover after resolution — so a verification that *succeeded* still exited 1 with "No output file produced", which `math-auditor` reads as a codex failure. Now `${TMPDIR:-/tmp}`, matching `codex_common.sh`'s existing scratch-dir pattern.
**#209 — undeclared empirical deps:** `linearmodels` (policy-canonical for Fama-MacBeth/panel — method-checker REVISEs hand-rolled substitutes, yet it was never installed) and `requests` (module-scope import in `edgar_utils.py`, previously present only transitively) added to `extensions/empirical/deps.txt`; the manual-install fallback hint in `apply_extension_empirical.sh` now derives its package list from `deps.txt` instead of a second hardcoded copy.

## [2.13.0] — 2026-07-31
`GENUINELY-STUCK` is no longer terminal: the abandon decision goes to the agent that owns it (issue #153).
**Problem:** `last-resort` — the strongest model in the pipeline — had two verdicts with asymmetric
verification. `FIX-PROPOSED` always re-entered the failing gate. `GENUINELY-STUCK` routed straight to
abandon/restructure with no second opinion and no re-check, so one false negative from a single call in
a single context could end an otherwise-recoverable run. The agent body already named the hazard
("a false GENUINELY-STUCK abandons salvageable work") and nothing downstream mitigated it.
**The fix is a deletion, not an addition.** The direct `GENUINELY-STUCK → abandon` edge is gone.
The verdict now re-enters `branch-manager` — the pipeline's existing "has this path ceilinged" advisor —
at a new context `last-resort-stuck`, which produces **Sections B + E only**, the same subset
`gate-5-downgrade` already emits. No new agent, no new verdict vocabulary, no new report format: §B's
existing REACHABLE/STRUCTURAL certification bar already asks the right question ("can you still name an
untried candidate?"). Both verdicts now obey one rule instead of two — neither self-executes — which
also let the asymmetry-justification paragraph in `last-resort.md` be cut.
**Two outcomes.** REACHABLE → branch-manager names the specific untried move *and the agent that owns
the artifact* (theory-generator, empiricist, paper-writer, the relevant auditor), and the move is
dispatched there — not back to `last-resort`. STRUCTURAL (certified) → restructure, or abandon **only
where the never-abandon rule permits**: post-Stage-5 a certified ceiling routes to restructure, deepen,
or ship-at-a-lower-tier, never to abandonment. The second opinion is genuinely decorrelated: different
agent, fresh context, and a lower model tier than the one that got stuck.
**Capped like every other loop.** New `loops.last_resort_stuck` (cap 2, seeded in `pipeline_state.json`).
It carries an explicit **reset override**, because this loop has a shape the generic rule mishandles:
attempting a named move *regenerates the stuck artifact*, so artifact-scoped auto-reset would zero the
counter every iteration and defeat the cap. It is scoped to the stuck **episode** and resets only when
the impasse clears or the loop exits by certification — recorded as a third documented exception
("retry-regenerates-the-artifact") in `core.md`'s auto-reset exception list.
**Impasse-agnostic bar.** `last-resort` is launched on tool and data failures too, not just theory
ceilings, so §B's journal-tier vocabulary gets two stated substitutions at this context: "core-change
candidate" → any untried candidate on the stuck artifact (a different estimator, specification, solver,
or data source), and "a contribution at the target tier" → "clears the impasse." A wedged solver has no
journal tier. The certification logic itself is unchanged.
**Also:** `--mode report` ships neither agent, so no mode divergence. Two stale enumerations removed
rather than corrected — branch-manager's "four contexts" (there were six) and the auto-reset list's
"two exceptions" — since a hard-coded count is what drifted in the first place.

## [2.12.0] — 2026-07-27
Deferrable core-bypass: a transient outage no longer parks a finished paper (issue #179).
**Problem:** any unresolved binding row blocked `status = "complete"` and forced terminal
`halted_core_bypass` awaiting manual operator sign-off. So an OpenAlex daily-budget outage —
transient, self-healing at 00:00 UTC, with a clean WebSearch fallback already in hand — could
strand a 100%-finished, submission-ready paper until a human marked a ledger row `resolved` by
hand. v2.11.0 made that outage far less likely and stopped it hanging; this closes the routing
half that made it terminal.
**Deferrable vs not.** An outage is *deferrable* when its source is down for a **stated bounded
horizon** (a rate limit or credit budget with a reset time) **and** the re-check is a **cheap
lookup**. Deferrable outages no longer halt: the run finishes, records what it owes in
`pipeline_state.json`'s new `pending_verification` array, and completes as
`status = "complete_pending_verification"`. Everything else — indefinite outage, withdrawn
record, credential failure, expensive re-check — still halts, as does **any ambiguous
classification** (the errors are asymmetric: a wrongly-deferred outage ships a status containing
the word "complete") and **every** case under `--halt-on-core-bypass`, which by design makes a
bypassed core a hard stop.
**The invariant is unchanged:** `complete_pending_verification` is not clean success. It is the
loud mark — a distinct status, an amber dashboard badge naming the outstanding cores, a driver
loop that stops and prints them, and an array saying exactly which citations went unchecked.
What was dropped is only the friction: a terminal state and a human signature for a lookup the
pipeline can simply redo.
**Self-clearing.** A session opening on `complete_pending_verification` re-probes, re-runs the
owed verification, and on a clean result resolves the ledger row, drops the entry, and sets
`complete`. Resolution authority was **narrowed, not loosened**: a session may self-clear only a
verification **it re-ran itself that came back clean** — evidence, not faith; a probe returning
200 or a fallback looking clean still cannot. A dirty re-check resets `current_stage` to the
owning stage and re-enters that stage's loop; a row may never be resolved while a known-bad
citation remains in the paper (that halts). Ledger and array must move together, and the ledger
wins if they disagree — the completion gate reads the ledger, so a corrupted array cannot force
a false `complete`.
**Consumers:** `launch.sh`'s driver `case` matched `complete)` exactly, so the new status would
have fallen through and re-prompted a finished paper until `MAX_TURNS` — it now exits cleanly and
prints the pending entries. `dashboard.html` would have rendered the badge unstyled and shown the
run as still working on "stage_10"; it now reads *Complete — verification still owed: <cores>*
(and all underscores in status badges are spaced, which also fixes `halted_core_bypass`).
**Not changed:** `core.md` stays lean per issue #27 — it gains only the `pending_verification`
schema. All three autonomous runtimes already shared `templates/runtime/claude/session.md`
(`setup.sh` sets `CODEX_SESSION="$CLAUDE_SESSION"`), so the rule reaches codex and gemini as it
always did.

## [2.11.1] — 2026-07-27
Credential documentation + a silent `.env` merge bug found while writing it.
**Bug:** `update.sh`'s env-merge read the source `.env` with `while IFS= read -r line`, which
sets the variable but returns non-zero on a final line with no trailing newline — so the loop
body skipped it and that key was **silently dropped**. The repo's own `.env` ended exactly that
way, with `OPENALEX_API_KEY` last, so the v2.11.0 key would not have propagated to any existing
deployment. Fixed with `|| [ -n "$line" ]`, plus a receiving-side guard that newline-terminates
the *target* before appending (a bare append onto an unterminated target concatenates two keys
into one corrupt line). `setup.sh` normalizes the trailing newline when copying.
**New `.env.example`** (committed; `.env` is gitignored, so a fresh clone had none and `setup.sh`
silently created no `.env` at all — contradicting the README). `setup.sh` now falls back to it,
so a deployment always lands a scaffold. Documents all 16 credential variables with empty values.
**README Step 3 rewritten**, and three of its claims were simply false: it said `NAME`/`EMAIL`/
`UNIVERSITY` appear "on the paper's title page" (nothing reads `NAME`/`UNIVERSITY`, and papers
ship an anonymized `\author` line that `paper-writer.md` forbids changing); it listed
`CENSUS_API_KEY` as optional (it is required — `bls_census_utils.py` raises without it, the
keyless tier having been retired); and it omitted `SEC_EDGAR_NAME`/`SEC_EDGAR_EMAIL` and the
`LOCAL_LLM_*` self-hosted backend entirely. `OPENALEX_API_KEY` is now documented as an
all-variants credential with the budget rationale, plus `update.sh` propagation instructions.
**Issues:** #150 (host-level OpenAlex rate limiter) closed — its per-IP premise is obsolete now
that the budget is measured per-key; the surviving shared-verdict-cache half is tracked in #207.

## [2.11.0] — 2026-07-26
OpenAlex credit-budget adaptation — the root cause of issue #179.
**Discovery:** OpenAlex replaced its per-second rate limit with a **daily credit/dollar
budget** on 2026-02-24 and now requires an API key past demo use; both utils still modeled
the old regime ("10 req/s, 100k/day") and authenticated with `mailto` only. Every deployment
was therefore running production literature work on the **keyless $0.10/day demo tier, shared
per-IP** — ~100 title searches/day for a whole host, which is why concurrent pipelines saw
sustained 429s and why single-ID lookups kept succeeding while searches failed.
**Measured costs** (from `x-ratelimit-*`): `/works/doi:{doi}` and `/works/W{id}` = **0
credits**; the `/works/https://doi.org/…` alias and `?filter=doi:` = 1; **title search = 10**;
PDF/XML = 100. Budget is **per key**, not per IP.
**Changes:** `OPENALEX_API_KEY` support in `openalex.py` and `bib_verify/openalex_check.py`
(Bearer header, so the key stays out of URLs, logs, and error text); `verify_bib.sh` now emits
each entry's `doi` (previously parsed and discarded, incl. a fallback that scrapes DOIs out of
`url`/`howpublished`/`eprint`), and `verify()` resolves by DOI first — **a bibliography whose
DOIs match their titles now verifies for 0 credits** (measured on a 4-entry .bib); an entry whose
DOI disagrees with its title still pays the usual 10 for a cross-check. Budget is now read off every response into `LAST_BUDGET` with a low-budget stderr
warning, the exhaustion error names the tier and whether a key was in use, and the bib report
prints credits spent. Skill docs (`openalex.md`, `bib-verify.md`) teach the cost model:
prefer `work` over `search` when a DOI or ID is in hand.
**Also fixes the #179 hang itself:** `openalex_check.py`'s `_backoff_sleep` slept the raw
`Retry-After`, uncapped. On budget exhaustion that value is seconds-until-midnight-UTC, so the
first entry slept for *hours* — the mechanism behind the reported "55+ min against 18 entries
with 0/18 processed, then killed." It is now capped at `BACKOFF_CAP` and a budget-exhaustion 429
raises `OpenAlexBudgetExhausted` immediately (scoped to 429; a 5xx with a long `Retry-After` is a
transient outage and still backs off normally). `openalex.py` already had both protections; this
brings the bib-verify path to parity. Consequence: budget exhaustion now surfaces as a per-entry
`api-error` with an explicit "resets 00:00 UTC" message and a finished report, instead of a hung
run with no report — which is what made the degradation unclassifiable in the first place.
**Verification integrity:** a cited DOI is trusted on its own only when it matches the cited
title at the VERIFIED bar (0.85). Below that the entry is labeled `lookup: "doi-weak"` and the
title search runs anyway, with the DOI candidate scored *alongside* the search hits (placed last,
so a stale-year DOI cannot displace a correct-year hit on a similarity tie). On that branch the
chosen match's title-similarity is therefore never worse than the pre-change search-only path. `bib-verifier.md`
and the generated report both now warn that `doi_confirmed: true` on a `doi-weak` entry means
"the DOI is a real record," not "it is the paper this entry claims" — and the label persists even
when the cross-check search itself fails, which is precisely when a silently-trusted weak DOI
would do the most damage. Each entry also reports the `credits` it actually cost, so a run that
hit failures doesn't overstate spend. DOI scraping is restricted to structural link fields
(`url`/`howpublished`/`eprint`, never the prose `note`, which routinely cites *other* papers'
DOIs) and no longer captures closing brackets.
**Not changed:** `.env` needs no scaffolding work — `setup.sh` copies it to new deployments and
`update.sh`'s env-merge appends the new key to existing ones. *(Corrected in 2.11.1: the merge
silently dropped an unterminated final line, which is exactly where `OPENALEX_API_KEY` sat, so
propagation to existing deployments did not actually work until that release.)*

## [2.10.0] — 2026-07-26
llm_cognition hardening pass (second extraction wave + calibration + experiment rigor).
**Vocab:** ~45 new keys close every load-bearing econ leak the v2.9.0 pass missed —
math-auditor-freeform's full heuristic set (a binding Gate 2 gate), polish-prose items 8–10,
idea-prototyper primitives, implications-deriver, novelty-checker search targets,
literature-scout/theory-explorer/scorer-freeform role lines, scorer cap-30 archetypes,
editor domain guard, paper-writer exemplars, referee/branch-manager load-test predicate
(now the existing `POLICY_MAP_LOAD_TEST`), core.md CARA/CRRA + numerical-verification
bullets, stage_4 "economic content", stage_6's hardcoded `top-3-fin` (also fixes a macro
tier-name bug), stage_puzzle_triage "falls out of economics". Econ defaults byte-identical
(verified by full 8-config baseline diff). **Calibration:** llm_cognition tier table rebuilt
(JMLR/ACL/EMNLP/NMI moved to a lateral `top-ml` row, nature = Nature/Science only,
`top-ml` 75+ re-anchored to confident-accept caliber, TMLR rigor-weighting note); OpenReview
visibility claims corrected (ICLR-only public submissions); baseline-comparison referee
bullet; RIGOR_80 measurement-first anchor; conference verdict-semantics note in the referee.
**theory_llm rigor:** contamination-resistant procedural ground truth + memorization probe,
50+/condition headline floor with stimulus×run error bars, temperature>0 for headline
variance, model-snapshot/decoding/access-date provenance (llm_client already returns it),
the previously-dangling `[ROLE: LOAD-BEARING|STRENGTHENING-PROBE]` schema (unblocks
puzzle-triager's PROBE-NULL path), experiment-designer's canonical output renamed to
`experiment_results.md` (the name every consumer already reads). **New agent:**
`polish-experiments` (theory_llm, Stage 9) re-verifies the rendered paper's experimental
evidence — raw-results agreement, contamination status, pinning, statistical integrity,
artifact reproducibility; wired into stage_9 via a guarded doc amendment, core-bypass
inject, and report-mode prune. **Structural:** `--variant llm_cognition` auto-implies
`--ext theory_llm`; openalex script + skill gain ML venue aliases (verified against live
OpenAlex) with an honest conference-coverage caveat; bib-verify adds openreview.net;
update.sh learns to sniff/name llm_cognition; empirical-first rejection message is
variant-aware; extension-doc sed extended to the full placeholder set (D10); dashboard
subtitle variant-corrected; README variant table updated; regression test
`test_scripts/test_llm_cognition_assembly.sh` (gates, auto-imply, 12 leak tripwires).
**LIMITATIONS:** new entries for the theory-first ordering inversion (no measurement-first
mode yet), the ML paper section-list gap, and the pre-existing Grok extension-agent gap.

## [2.9.0] — 2026-07-26
Variant vocab now layers into shared-body assembly (shared → variant → tier → mode, later
wins; extension appliers included), making shared evaluator/search/polish bodies
variant-aware. Closes the llm_cognition routing-level economics leaks: referee-mechanism's
evaluative frame and verdict definitions, the `policy_map_axes`/`acronym_carveout`/
`iar_wiki_pointer` fragments, novelty/gap/literature search-venue directives
(SSRN/NBER → arXiv/OpenReview for llm_cognition), the deepening-playbook extension menu
and DECORATIVE remedy text (`MECHANISM_QUALIFIER*` substitution in core.md + stage docs),
polish-equilibria's N/A escape (now unconditional), the theory_llm experiment-designer's
stale finance_llm test list (+ explicit model-family scope rule), and the ssj/nber-agenda
advice bullets. llm_cognition vocab quality pass: H2/THEORY_AGENTS formal-only escape
branch, H3 measurement-first wording, landmark-anchor recalibration (Nature Human
Behaviour and PNAS dropped, JMLR reconciled), exemplar diversification, WRDS/FRED
inventory fix. All-variant fix:
"knowledgeable knowledgeable" doubling; stale finance tier-band examples removed from
core.md/stage_1.md. Finance/macro assembled output verified byte-identical except those
intended fixes. New LIMITATIONS entries: econ paper skeleton, econ-only skills install.

## [2.8.1] — 2026-07-26
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
