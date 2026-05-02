## How to start a session

1. Read `process_log/pipeline_state.json`
   - If `status` is `"not_started"` and `"seeded"` is `true`: run data inventory (below), set to `"running"`, then follow the **Seeded idea mode** entry sequence (see above)
   - If `status` is `"not_started"`: run data inventory (below), set to `"running"`, begin Stage 0
   - If `status` is `"running"`: read `current_stage` and continue from there
   - If `status` is `"complete"`: report that the pipeline is done
2. No human confirmation needed — just run

### Data inventory (runs once at pipeline start)

Before Stage 0, check what data sources are available. This prevents bad assumptions from cascading through the entire pipeline.

1. If `code/utils/start_services.sh` exists, run it first to start persistent data connections (WRDS requires Duo auth — wait for it).
2. Read `.env` and list `{{SKILL_DIR}}/` — check which data skills are installed and which have valid credentials (not placeholders). For services started in step 1, verify they actually respond. Mark ✓ only if the connection works, not just if credentials exist.
3. Write results to `output/data_inventory.md` — table of sources, status (✓/✗), what each provides, and implications for research design.
4. Commit: `pipeline: data inventory complete`

**CRITICAL:** All downstream agents must read `output/data_inventory.md` when making decisions about empirical feasibility. The idea-generator and idea-reviewer must know what data is available so they design ideas that USE available data, not work around imagined limitations. Never assume a data source is unavailable without checking the inventory.

The session-start data inventory is *not* sufficient for long-running pipelines: a multi-hour Stage 2 iteration can outlive the WRDS session it depends on. `docs/stage_3a_empirical.md` ("Preflight: data-source liveness") and `docs/stage_puzzle_triage.md` (FIX-EMPIRICS branch) document a per-launch `wrds_ping()` check the orchestrator must run before each `empiricist` invocation. The session-start inventory establishes the baseline; the per-launch preflight catches drops.

### Agent launch and monitoring

Subagents can hang indefinitely. Launch web-dependent agents (`literature-scout`, `novelty-checker`) in the background. Check their output file every 5 minutes — if empty or not growing after a few checks, re-launch with the same prompt.
