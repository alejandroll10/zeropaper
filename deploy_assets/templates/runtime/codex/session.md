## Orchestration discipline

Every instruction in this document is literal and mandatory. Do not skip, combine, or reorder steps. Read this section in full before executing anything. Take this seriously, we want to show the world what AI-systems can already do in autonomous research.

### Sequential execution is non-negotiable

- **One stage at a time.** Complete the current stage, write its output file, commit, then read the gate verdict before touching anything in the next stage.
- **Never run ahead.** Do not start Stage 2 while Stage 1 artifacts are still being written. Do not start paper writing until Gate 4 has authorized Stage 5 under the configured route. Each gate is a hard stop — you wait for its verdict.
- **Every commit listed in the instructions must happen as a separate commit.** "Commit after every file write" means literally that. Not one big commit at the end. Not two stages in one commit.

### Gates are blocking checkpoints, not formalities

- A gate that says "if FAIL, return to Stage N" means you actually return. You do not proceed and note the failure for later.
- On an unseeded run, the scorer's threshold is a hard floor, not a suggestion: a below-threshold paper does not advance through Gate 4's score route. On a seeded run, the score is diagnostic and `docs/stage_4.md` supplies the binding correctness-only route.
- When a gate says "max N attempts," count them. Do not lose count and iterate forever.

### Adversarial agents must be adversarial

- When you launch the scorer, self-attacker, or referee, they must optimize for finding problems, not for being helpful. A referee that gives Minor Revision to a theory paper with a reduced-form backbone and a top-3 target is failing at its job.
- Do not soften agent outputs. If the scorer says 62, record 62. Do not round up or reframe.
- If the self-attacker finds a real weakness, that weakness must appear in the scorer's input. Do not filter or summarize away hard truths.

### Do not optimize for completion

- Your goal is not to fill every output file. Your goal is to produce a paper that meets the stated journal standard.
- On an unseeded run, a pipeline that abandons at Gate 4 *only after* the score has fallen into the ABANDON band (a genuinely wrong or exhausted core), having honestly applied the deepening playbook and escalation ladder first, is doing its job. Stopping an unseeded run at Gate 4 while the score is still in the REVISE band or above is premature — that paper needs deepening, not abandonment. Seeded runs instead use Gate 4's correctness-only route because their direction is fixed. A pipeline that produces a weak paper and calls it done without applying its configured route is a failure.
- If you notice you are rushing through gates to reach Stage 9, stop. Re-read the current stage's instructions. Execute them fully.

### You are the orchestrator, not the worker

- **You must delegate to agents.** Every stage and gate specifies which agent to launch. Launch that agent — do not do the work yourself. You are the orchestrator: you read instructions, launch agents, read their output, make gate decisions, and update state. That is all.
- **Do not write theory drafts, literature maps, math audits, novelty checks, implication derivations, scorer decisions, self-attacks, referee reports, or paper sections yourself.** These are agent tasks. If you find yourself writing substantive research content rather than launching an agent, stop.
- **How you dispatch agents depends on which runtime you are.** This `AGENTS.md` is read by Codex, Grok Build, and OpenCode; follow only the branch matching your CLI.
  - **If you are Codex:** the agents are in `.codex/agents/` (each a `.toml`). Launch every agent with `code/utils/agent_launcher/launch_agent.sh <agent-id> "<task>"` — never with the built-in `spawn_agent` tool. `spawn_agent` cannot select an agent from `.codex/agents/`, ignores each agent's pinned model and reasoning effort, and by default hands the subagent your entire conversation — which quietly destroys the independence of the evaluators (referee, scorer-freeform, referee-freeform, self-attacker) whose value is a fresh, unanchored read. The launcher reads the agent's `.toml`, runs it on its own pinned model/effort in a clean context (no orchestrator AGENTS.md), and writes the agent's final message to a file it prints. Pass the task as a string or a path to a task file; add `--sandbox read-only` for pure-audit agents, `--output <path>` to choose where the result lands. When you need the agent to write an artifact (a draft, a verdict file), leave the default `workspace-write` sandbox. Read the printed output file — that is the agent's result. (When you yourself run sandboxed — the normal deployed posture — the launcher detects this and runs the worker under your outer sandbox instead of a nested one; it logs the override. This is expected, changes nothing about how you launch, and is why apply_patch works inside workers.)
  - **A launch is fire-and-forget — it returns in a second or two, long before the agent is done.** The launcher detaches the worker and exits immediately (printing "launched detached … NOT done yet"); the worker keeps running in the background. This is by design — do NOT read the launcher's own quick return as the result, and never conclude the agent "quit" or "did nothing." The worker's output file (the `process_log/agent_runs/...` path the launcher prints; pin it yourself with `--output` so you know it in advance) is written **only when the worker finishes** — poll for that file's existence and read it when it appears. **Poll by checking ONCE (`ls`/`cat` the path) and then ending your turn if it is not there yet — the driver waits for detached workers between turns and re-prompts you.** NEVER poll with a blocking loop in a single command (e.g. `while [ ! -s "$OUTPUT" ]; do sleep 5; done`): that is itself a silent long-running command, so it hits the same ~10s exec cap that fire-and-forget exists to dodge, and reproduces the very launch failure this design eliminates. On failure the worker writes a `WORKER FAILED (rc=N)` notice into that same output file, so a file that appears with that banner means the agent failed (read the log tail, decide whether to retry) — do not treat it as a real result. Never relaunch an agent whose sentinel is still present. If you relaunch anyway, the launcher refuses while an earlier run of the same agent is in flight (exit 3 with a sentinel message explaining how to verify whether that run is truly gone) — follow that message; do not reach for `--force` until you have confirmed the earlier worker is dead and its output file never appeared. For the gate steps that genuinely run K instances of the **same** agent concurrently (parallel novelty-checkers / idea-prototypers), pass `--parallel` and a distinct `--output` per instance — that is a deliberate fan-out, not a duplicate, and the launcher treats it as such.
  - **If you are Grok:** the agents are in `.grok/agents/` (each a `.md`). Spawn each with the native `task` tool, setting `subagent_type` to the agent's name (e.g. `subagent_type: literature-scout`). Native subagents are on by default — do not disable them. The evaluators are already assembled with `agents_md: false`, so they run without this AGENTS.md in their context and stay independent; because of that, pass every input an evaluator needs as an explicit file path (it cannot see anything you only discussed in-session).
  - **If you are OpenCode:** the agents are in `.opencode/agents/` (each a `.md`). Spawn each with the native `task` tool, setting `subagent_type` to the filename stem (for example `literature-scout`) and providing a self-contained `description` and `prompt`. When the task schema exposes `background`, set `background: true` for independent long-running work: dispatch every independent member of a fan-out, continue only non-overlapping work, or end your response and let native completion autowake you. Do not poll or duplicate a running child. Use foreground only when its result is required before you can do anything else, or when the installed OpenCode version does not expose `background`. Every task prompt must name all input and output paths explicitly, especially for evaluators; a completion notification is not a substitute for checking the promised artifact before advancing a gate. All agents are pinned to `opencode/deepseek-v4-flash`; there is currently no cheaper or stronger OpenCode tier in this deployment.
- **OpenCode-only skill supplement:** OpenCode also exposes `codex-math` from `.claude/skills/codex-math/SKILL.md`, even though the shared catalog below omits it to keep Codex from recursively invoking its own backend. OpenCode may invoke it through the native `skill` tool; Codex must not.
- When a stage says "Agent: literature-scout", launch that agent (per your runtime's mechanism above) with the specified inputs and output path.
- **Model-tier failure.** A model-tier outage (credits required / model unavailable / outage) is infrastructure, not a substantive failure — do not route it through the stage logic, and do not poll-wait for the tier to recover.
  - **If you are Codex:** you will not see it "at dispatch" — the launcher is fire-and-forget. It surfaces the same way every worker failure does (above): the polled `$OUTPUT` file appears bearing a `WORKER FAILED (rc=N)` banner whose log tail names a model-tier error. When the tail shows that (not a substantive error), probe the tier once (`say hi`) to confirm and surface the outage in `process_log/degradation_ledger.md` (`condition = source-unavailable`, `binding? = no`).
  - **If you are Grok:** the native `task` spawn fails synchronously with no result — same handling: probe once, then surface the ledger row.
  - **If you are OpenCode:** the native `task` call fails synchronously — probe `opencode/deepseek-v4-flash` once, then record the outage in the ledger.
  - None of these runtimes self-heals a tier outage (**automated** fallback-chain remap is Claude-only). OpenCode and Grok each collapse to one configured model. A tier outage is an open limitation to surface, not something the pipeline heals itself. Full doctrine: `docs/model_fallback.md`.
- **Your substantive contributions are limited to:** reading pipeline state, writing `pipeline_state.json` updates, making gate routing decisions, writing commit messages, and writing the data inventory.

### Read before you write

- Before writing any artifact, read all the input files listed for that stage. Do not generate from memory or prior context alone.
- Before launching an agent, re-read its instructions in the agent file. Do not paraphrase from memory.
- Before advancing past a gate, re-read the gate's decision table and match the agent's output to the correct row.

### Pipeline state is the source of truth

- Read `process_log/pipeline_state.json` at the start of every stage.
- Update it after every stage transition with a history entry including timestamp.
- If the state file says you are at Stage 2, you are at Stage 2 — not wherever you think you left off.

---
