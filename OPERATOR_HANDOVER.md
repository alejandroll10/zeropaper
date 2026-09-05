# Operator handover — autonomous pipeline babysitting (written 2026-09-01)

## Role

Operator for two autonomous Codex paper pipelines plus maintainer of this template repo
(zeropaper). Monitor the runs, recover halts, fix template bugs the runs surface
(LIMITATIONS.md + GitHub issue pair for anything unsolved; independent Sonnet review
after every big change, iterate until clean; VERSION/CHANGELOG/tag/push --follow-tags).
Push-notify the user only on actionable events.

## The two runs

**Both are currently blocked on an operator scope decision. Nothing else needs you.**

1. **eventcal** — OETC-US, open event-time calendar (FOMC / Treasury auction phases /
   BEA GDP). `--variant finance --mode data-first --seed`, template ~v2.30.x.
   Path: `/mnt/data_drive/Dropbox/Dropbox/NewPapers/generated_papers/eventcal`
   **State (2026-09-05):** running, Stage 2, spec **v32**, `loops.build_failure` 6 of cap 4
   (past cap — each respecification now buys exactly one build). `stage3a_result_receipt`
   is **null**: across 32 specification versions this campaign has never accepted a full
   Stage 3a receipt. Portfolio stable at 5 novel / 0 puzzle / 3 supported; A2 and N2 are
   documented non-closures from the v26 respec.
   **The decision:** every recent cap-triggering failure is **R4 runtime apparatus** —
   a151 pinned `ivreg2r` unavailable, a152 R4 gapped-index fixture never produced, a153
   `bootstrap_r4_runtime.py` calling `Rscript CMD INSTALL` (`CMD` is an `R` subcommand).
   R4 carries 38 spec mentions against R1's 9 and R3's 1, and needs a from-source
   13-package sealed R runtime with exact closure and dual digests. Same signature as the
   v25 FOMC diagnosis: the heaviest contract consumes the campaign. Question is whether R4
   needs that apparatus or should become a documented non-closure like A2/N2. Failures are
   currently *cheap* (a152 died at preflight, a153 at its first package), so it is not
   burning disk or hours — no urgency, but it will not converge on its own.
2. **tradingdays** — verified cross-section-of-trading-days panel, coauthor Guillaume
   Coqueret (his prototype = seed inventory, never production evidence).
   `--variant finance --mode data-first --seed`, template v2.30.11.
   Path: `/mnt/data_drive/Dropbox/Dropbox/NewPapers/generated_papers/tradingdays`
   **State (2026-09-05):** **HALTED** by operator at the a126 route boundary,
   `halted_verification_layer_unbounded`. `loops.build_failure` seeded 4 of 4 deliberately,
   so resuming without a decision takes the cap route to Stage 2 rather than a fifteenth
   build. The accepted a61 analysis/release pair and all a126 evidence are intact.
   **The decision:** thirteen of the fifteen attempts spanning a112–a126 never reached a
   verified receipt, and nine of those failed in the project's *own* two-isolated-root
   replay conformance layer while the producer and the WRDS acquisition succeeded every
   time. The remaining work is a complete bwrap mount grammar and an exact-member OS
   runtime closure. Question is whether that layer is in scope at all, given the trusted
   runner already publishes receipts over content-hashed inputs with network denied and an
   external data-integrity auditor re-queries live sources from outside the sandbox.
   **Operator recommendation on file: retire it, and write the retirement up as a finding**
   (the same treatment A2/N2 got on eventcal).

Division of labor (in both seed briefs): event timing/identity belongs to eventcal's
spine; tradingdays must NOT build approximate event-timing columns. Unification plan:
after both finish, one fresh `--manual` deployment absorbs both releases (spine join =
a receipted manual results_pipeline run); pipelines for construction, manual project
for stewardship.

## GitHub / collaboration

- Private repos exist and are pushed: `alejandroll10/eventcal`, `alejandroll10/tradingdays`.
  Guillaume (`shokru`) has write on both; he was emailed (from the user's Gmail, signed
  as Claude) and told to treat them read-mostly while runs commit to main. Drivers do
  NOT auto-push; push manually on operator commits or milestones.
- Correspondence with Guillaume goes through the user; his personal email is
  guillaume.coqueret@gmail.com (thread "Trading days & co." in the user's Gmail).

## WRDS daemon (critical protocol)

Per-host singleton (port 23847), one-login-attempt safety latch, durable across
reboots. State dir: `~/.local/state/zeropaper/wrds/`.
- Health check: from either project,
  `.venv/bin/python3 -c "import sys; sys.path.insert(0,'code'); from utils.wrds_client import wrds_ping; print(wrds_ping())"`
  (cwd = project root). CLI: `code/utils/wrds_client.py [status|unblock]`.
- If AUTH BLOCKED: diagnose first (DNS? TCP to wrds-pgdata.wharton.upenn.edu:9737?),
  then run unblock as a **background task with no timeout** (a 120s Bash timeout once
  killed it mid-login and made things worse). Duo push may fire — **requires the user
  present**. If the user is away and can't Duo: DO NOT unblock or restart; let
  pipelines halt safely (`halted_wrds_unreachable`) until they return.
- If unblock says "daemon still running": kill the recorded PID
  (`~/.local/state/zeropaper/wrds/wrds_server_23847.pid`), then rerun unblock once.
- Never let a legacy (pre-v7) wrds_server take the port.

## Halt recovery pattern

Driver exits on halt. Procedure: read `process_log/pipeline_state.json` history +
`output/debug/` diagnostics; fix/decide as operator; flip `status` back to `running`
with a history entry documenting basis + exact scope of any authorization; commit
(`operator: ...`); push to the GitHub remote; relaunch driver **detached**:
`cd <project> && setsid nohup ./launch.sh codex >> process_log/relaunch_console.log 2>&1 < /dev/null & disown`
(detached matters: harness-tracked background tasks get killed by session cleanup).
Known halt types seen: `halted_wrds_unreachable`, `halted_replication_artifact_collision`
(relocate stray reserved-namespace files, re-run `code/utils/empirical_input_manifest.py
check-all` until artifact_errors empty), `halted_core_bypass` (source-outage judgment
call — see 74be8fc/f7e6af0 in tradingdays for the authorization pattern).

## Monitoring (re-arm in a new session; survives /compact)

Two Monitor tasks per project:
1. Commit watcher: poll `git rev-parse HEAD` every 60s in the project dir, emit
   `git log --oneline` for new commits.
2. Halt watcher: `tail -F -n 0 process_log/driver.log | grep -E --line-buffered
   "pipeline halted|driver\] ERROR|consecutive sub-60s|MAX_TURNS|driver\] stopping|pipeline complete"`.
Persistent: true. Respond to routine events with one line; investigate on: repeated
same-scope failures (3+), audit finding counts rising, halts, anything template-shaped.

## Template repo state (this repo)

- HEAD ~ab6b6be + 2 upstream commits from the user's parallel template session
  (expect tag collisions — always `git pull --rebase` before commit; renumber your
  version if the parallel stream took it; v2.31.0 was taken that way).
- Shipped this arc: v2.30.6 (WRDS deadline fix #291), v2.30.8 (tracked-job doc
  mandate), v2.30.12 (runner startup banner), **v2.32.0** (run/run-empirical require
  `--caller-allowance-seconds` >= 1200, refusal before lock; 3 review rounds clean).
- **Filed 2026-09-05 from a single night's field evidence, all three invisible until
  something expensive fails:** **#308** (Stage 3a counts verdicts on produced artifacts,
  so an attempt dying before publishing a receipt increments nothing and re-fires
  unbounded — tradingdays ran thirteen such builds with no counter moving; the fix is a
  counter keyed on *counter responsibility*, not on receipt publication, and it is live
  locally in both deployments as `loops.build_failure`), **#309** (counter values quoted
  in narrative text go stale silently and invite adjusting the live counter to match —
  three occurrences in one evening), **#310** (a spec can declare an input artifact that
  no step produces; Gate 2 and plan review both accept it — cost eventcal a full accepted
  specification plus its only remaining build).
- Open tracked issues from earlier field observations: **#293** (reopened: honor-system
  allowance + receipt-safe acquisition checkpointing; 5 occurrences logged),
  **#294** (registry suffix-scan misclassifies documentary receipt snapshots),
  **#295** (data-first coverage predicates cost one full pipeline cycle per gap event;
  census/ledger/amendment-lane candidates), **#299** (single-shot debug probes blind
  to burst-triggered rate limits — the Nasdaq RPCHandler.axd lesson: ~10 rapid POSTs
  → HTTP-200 bot-challenge page, clears ~60s, 15s pacing safe).
- Deployed projects stay on their pinned templates — no hot-patching (receipt v2
  environment fingerprinting); template fixes benefit new deployments only.

## Standing user directives

- Don't restart/unblock WRDS when the user is away (Duo). Ping-only checks are fine.
- Don't delete receipt-bound artifacts unilaterally; quarantine instead.
- Standing authorization (given 2026-09-04) to modify `pipeline_state.json` and recover
  runs autonomously when the user is not answering, and to apply template fixes locally
  in the deployments since `update.sh` is same-version-only and they can never receive
  them. Operator *scope* directives are different: those have been written only on the
  user's explicit say-so, one per project (eventcal v26, tradingdays v20), and a third
  should not be written unprompted.
- **A cap may not be changed while its round is within one of it.** Learned the hard way:
  a raise from 4 to 6 at 3/4 was made and reverted the same hour, on a rationale that the
  deployment's own debug directory falsified.
- No em dashes in emails written for them; keep them short and plain.
- One product eventually: unify post-completion via a manual-mode deployment.
