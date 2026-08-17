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
  - **If you are Codex:** the agents are native custom roles in `.codex/agents/` (each a `.toml`). Spawn every prescribed agent with the native `spawn_agent` tool, set `agent_type` to the filename stem (for example `scorer`), give every instance a unique `task_name`, and set `fork_turns="none"` for a fresh context. Never omit any of those fields, never pass a full-history fork, and never substitute the built-in `worker`/`default` role. The launcher pins this exact V2 schema; a missing field is compatibility failure, not a reason to improvise a legacy call. The role file pins the model and reasoning effort, suppresses this orchestrator AGENTS.md, and disables recursive delegation. Give the child a self-contained task naming every input path, required output path, decision, and output format.
  - **Native children are same-turn work, not detached jobs.** After spawning an agent or fan-out, keep this parent turn alive and use the native wait/status tools until every requested child is terminal. A wait timeout is not completion: wait again. Do not return a final answer, end the turn, or advance the gate while any requested child is pending or running—under headless `codex exec`, ending the primary turn shuts down the in-process agent server and interrupts live children. Treat `errored`, `interrupted`, `shutdown`, or missing status as an infrastructure failure to reconcile and deliberately retry, not as a substantive verdict. A completion notification is not enough by itself: verify the promised artifact exists and is complete before using it. Preserve the current stage's exact commit boundary: a combined fan-out commit stays combined, and a gate that says "commit nothing" stays uncommitted; do not invent per-child commits. Before routing or ending the turn, make every commit that the stage requires. After an aborted/interrupted turn, never accept a task-owned uncommitted diff merely because its file exists or looks complete: compare it with the last committed state, re-launch its owning agent to rewrite/repair the exact output, validate it, and then follow the stage's required commit/routing sequence. Fan-outs use bounded waves: honor any smaller capacity reported by the native tool; otherwise keep at most three children live because the four-slot session includes this parent. Give every instance a distinct task name and output path. Fill the available child slots, wait for at least one terminal child, validate its exact artifact without staging a live child's path, then refill until the fan-out is exhausted. Commit at the stage-defined boundary only. "Parallel" never means submitting a fourth live child and treating capacity rejection as an agent verdict.
  - **If you are Grok:** the agents are in `.grok/agents/` (each a `.md`). Spawn each with the native `task` tool, setting `subagent_type` to the agent's name (e.g. `subagent_type: literature-scout`). Native subagents are on by default — do not disable them. The evaluators are already assembled with `agents_md: false`, so they run without this AGENTS.md in their context and stay independent; because of that, pass every input an evaluator needs as an explicit file path (it cannot see anything you only discussed in-session).
  - **If you are OpenCode:** the agents are in `.opencode/agents/` (each a `.md`). Spawn each with the native `task` tool, setting `subagent_type` to the filename stem (for example `literature-scout`) and providing a self-contained `description` and `prompt`. When the task schema exposes `background`, set `background: true` for independent long-running work: dispatch every independent member of a fan-out, continue only non-overlapping work, or end your response and let native completion autowake you. Do not poll or duplicate a running child. Use foreground only when its result is required before you can do anything else, or when the installed OpenCode version does not expose `background`. Every task prompt must name all input and output paths explicitly, especially for evaluators; a completion notification is not a substitute for checking the promised artifact before advancing a gate. All agents are pinned to `opencode/deepseek-v4-flash`; there is currently no cheaper or stronger OpenCode tier in this deployment.
- **OpenCode-only skill supplement:** OpenCode also exposes `codex-math` from `.claude/skills/codex-math/SKILL.md`, even though the shared catalog below omits it to keep Codex from recursively invoking its own backend. OpenCode may invoke it through the native `skill` tool; Codex must not.
- When a stage says "Agent: literature-scout", launch that agent (per your runtime's mechanism above) with the specified inputs and output path.
- **Model-tier failure.** A model-tier outage (credits required / model unavailable / outage) is infrastructure, not a substantive failure — do not route it through the stage logic, and do not poll-wait for the tier to recover.
  - **If you are Codex:** the native child reaches a terminal error status and its completion/error notification names the model-tier failure. Probe the tier once (`say hi`) to confirm and surface the outage in `process_log/degradation_ledger.md` (`condition = source-unavailable`, `binding? = no`).
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
