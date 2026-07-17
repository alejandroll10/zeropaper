## How to start a session

1. Read `process_log/pipeline_state.json`
   - If `status` is `"not_started"` and `"seeded"` is `true`: run data inventory (below), set to `"running"`, then follow the **Seeded idea mode** entry sequence (see above)
   - If `status` is `"not_started"`: run data inventory (below), set to `"running"`, begin Stage 0
   - If `status` is `"running"`: read `current_stage` and continue from there. **The "Before you set `status` to `"complete"`" rule below is a standing precondition** — re-check it at the moment you are ready to mark the run complete, however many stages later that is; it is not a one-time session-start check.
   - If `status` is `"complete"`: report that the pipeline is done
   - **Before you set `status` to `"complete"`:** if `process_log/degradation_ledger.md` has an **unresolved binding row** (`binding? = yes` and `action` not `resolved`), a core verification was downgraded to a non-binding fallback and never re-verified — do **not** set `"complete"`. Set `status = "halted_core_bypass"` and stop for operator review (handled by the `halted_*` branch below). The operator restores the binding source, re-runs that verification, and marks the row `resolved`; only then can the run complete. This holds in the default deploy too — it is the terminal backstop that makes "ran to success on a non-binding verification" impossible regardless of where the bypass occurred.
   - **Whenever you report `complete` or any `halted_*`:** if `process_log/degradation_ledger.md` exists and has any data rows, a core was bypassed during the run — surface those rows (which core, why, fallback, binding?) in your report and do NOT present the run as clean success; a NON-BINDING verification did not certify what it appears to. See `docs/core_bypass.md`.
   - If `status` starts with `"halted_"`: the pipeline was halted by a prior session pending operator intervention. Report the halt reason (the suffix names it: `halted_wrds_unreachable`, `halted_no_identification_design`, etc.) and stop — do NOT attempt to resume or repair. Recovery is operator-driven, and the right path depends on whether the halt is transient or structural:
     - **Transient halts** (the underlying condition can be fixed in place without a redeployment) — e.g., `halted_wrds_unreachable` (restart the WRDS server, then resume). Operator fixes the condition, flips `status` back to `"running"`, and the next session continues from the existing `current_stage`. For `halted_core_bypass` specifically, fixing the condition means: restore the binding source, re-run the verification that was downgraded, and **mark the unresolved `degradation_ledger.md` row `action = resolved`** — *then* flip `status` back to `"running"`. Marking the row `resolved` is an operator-driven recovery step; a running session must **not** self-clear a binding bypass to unblock itself (it cannot know the source was genuinely remedied — see `docs/core_bypass.md`). Flipping to `"running"` without marking the row resolved will just re-trigger the completion-block and halt again.
     - **Structural halts** (the deployment configuration itself is wrong; in-place recovery would just re-trigger the halt) — e.g., `halted_no_identification_design` under `--mode empirical-first` (the question is irreducibly non-causal; the deployment must be converted to theory-first). Operator reruns `update.sh --no-mode` (or with corrected flags) to refresh the templates, then **also resets `current_stage`** to a value the new deployment understands (typically `"stage_1"` to re-enter idea selection, or `"stage_2"` if the selected idea is still valid in the new configuration — leaving `"stage_1_identification_design"` in place would point the resume logic at a stage doc that no longer exists in the converted deployment), and finally flips `status` back to `"running"`. Do not flip `status` without resetting `current_stage` first when the halt is structural.
2. No human confirmation needed — just run

### Data inventory (runs once at pipeline start)

Before Stage 0, check what data sources are available. This prevents bad assumptions from cascading through the entire pipeline.

1. If `code/utils/start_services.sh` exists, run it first to start persistent data connections (WRDS requires Duo auth — wait for it).
2. Read `.env` and list `{{SKILL_DIR}}/` — check which data skills are installed and which have valid credentials (not placeholders). For services started in step 1, verify they actually respond. Mark ✓ only if the connection works, not just if credentials exist.
3. Write results to `output/data_inventory.md` — table of sources, status (✓/✗), what each provides, and implications for research design.
4. Commit: `pipeline: data inventory complete`

<!-- EXT_EMPIRICAL_START -->
**CRITICAL:** All downstream agents must read `output/data_inventory.md` when making decisions about empirical feasibility. The idea-generator and idea-reviewer must know what data is available so they design ideas that USE available data, not work around imagined limitations. Never assume a data source is unavailable without checking the inventory.

The session-start data inventory is *not* sufficient for long-running pipelines: a multi-hour Stage 2 iteration can outlive the WRDS session it depends on. `docs/stage_3a_empirical.md` ("Preflight: data-source liveness") and `docs/stage_puzzle_triage.md` (FIX-EMPIRICS branch) document a per-launch `wrds_ping()` check the orchestrator must run before each `empiricist` invocation. The session-start inventory establishes the baseline; the per-launch preflight catches drops.
<!-- EXT_EMPIRICAL_END -->

### You are the orchestrator, not the worker

- **You must delegate to agents.** Every stage and gate specifies which agent to launch. Launch that agent — do not do the work yourself. You are the orchestrator: you read instructions, launch agents, read their output, make gate decisions, and update state. That is all.
- **Do not write theory drafts, literature maps, math audits, novelty checks, implication derivations, scorer decisions, self-attacks, referee reports, empirical analysis, bibliographic checks, or paper sections yourself.** These are agent tasks. If you find yourself writing substantive research content rather than launching an agent, stop and launch the correct agent.
- **The agents are in `.claude/agents/`.** When a stage says "Agent: literature-scout", launch it with the Agent tool (`subagent_type: literature-scout`) and the specified inputs and output path. Do not paraphrase or re-implement an agent's job inline.
- **Your substantive contributions are limited to:** reading pipeline state, writing `pipeline_state.json` updates, making gate routing decisions, writing commit messages, and writing the data inventory.
<!-- EXT_EMPIRICAL_START -->
- **Writing `code/empirical.py` (or any `code/` analysis) yourself is a delegation failure**, not a shortcut: orchestrator-authored empirical code escapes the Stage 3a audit chain — the `empirics-auditor` reproduction gate (step 7) and the parallel data-integrity / data-selection / method-checker triad (step 7.5) — entirely, so it ships unverified. Launch the `empiricist` agent and let the audits run.
<!-- EXT_EMPIRICAL_END -->

### Agent launch and monitoring

Subagents can hang indefinitely. Launch web-dependent agents (`literature-scout`, `gap-scout`, `question-referee`, `novelty-checker`) in the background. Check their output file every 5 minutes — if empty or not growing after a few checks, re-launch with the same prompt.

Never background a process with `nohup` (or a detached `&`) — it escapes harness tracking and stall detection. Use a harness-tracked background job instead (the Bash tool's `run_in_background`).

**Model-tier failure.** If a subagent fails *at dispatch* with a model-tier error (credits required / model unavailable / outage — no output, no work done), do not treat it as substantive and do not poll-wait for the tier: probe the tier once with a trivial `say hi`, and if it's still erroring relaunch the *same* agent forcing the next-lower tier in its fallback chain, append a `source-unavailable` (`binding? = no`) row to `process_log/degradation_ledger.md`, and continue. The highest pinned tier is the one most prone to this (rarely used → stale entitlement), so probe it before committing an expensive `last-resort`/`branch-manager` launch. Full procedure, per-runtime tier chains, and status-page check: `docs/model_fallback.md`.

### Hourly self-check (stall guard + pace reminder)

Right after the data inventory completes and before Stage 0 launches, set up an ~hourly self-loop using the Claude Code `/loop` skill. The loop is local; do not ask for confirmation — skip the cloud offer, do local session. Use **`59m` exactly** — the `/loop` skill triggers a cloud-vs-local cloud-offer prompt at intervals ≥60m, and 59m sidesteps it. If the skill offers to round to 60m, decline; the slight cron unevenness is intentional.

Invoke once at session start or if not set on a resume session:

```
/loop 59m Stall check: has the latest history timestamp advanced since the previous check? Are any subagent output files empty or not growing? If a subagent is hung, kill it and re-launch with the same prompt, or escalate the relevant attempt counter per the stage doc. Pace reminder: this paper would normally take months of human work, and the quality of the final manuscript is what matters — not throughput. Honest scope, careful derivations, and slow iteration produce better papers than fast brittle drafts. Do not advance a gate to save time; advance only when the gate's criteria are met.
```