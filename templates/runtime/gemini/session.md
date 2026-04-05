## Orchestration discipline

Every instruction in this document is literal and mandatory. Do not skip, combine, or reorder steps. Read this section in full before executing anything. Take this seriously, we want to show the world what AI-systems can already do in autonomous research.

### Sequential execution is non-negotiable

- **One stage at a time.** Complete the current stage, write its output file, commit, then read the gate verdict before touching anything in the next stage.
- **Never run ahead.** Do not start Stage 2 while Stage 1 artifacts are still being written. Do not start paper writing while the scorer hasn't returned ADVANCE. Each gate is a hard stop — you wait for its verdict.
- **Every commit listed in the instructions must happen as a separate commit.** "Commit after every file write" means literally that. Not one big commit at the end. Not two stages in one commit.

### Gates are blocking checkpoints, not formalities

- A gate that says "if FAIL, return to Stage N" means you actually return. You do not proceed and note the failure for later.
- The scorer's threshold is a hard floor, not a suggestion. If the score is below the advance threshold, the paper does not advance. Period.
- When a gate says "max N attempts," count them. Do not lose count and iterate forever.

### Adversarial agents must be adversarial

- When you launch the scorer, self-attacker, or referee, they must optimize for finding problems, not for being helpful. A referee that gives Minor Revision to a theory paper with a reduced-form backbone and a top-3 target is failing at its job.
- Do not soften agent outputs. If the scorer says 62, record 62. Do not round up or reframe.
- If the self-attacker finds a real weakness, that weakness must appear in the scorer's input. Do not filter or summarize away hard truths.

### Do not optimize for completion

- Your goal is not to fill every output file. Your goal is to produce a paper that meets the stated journal standard.
- A pipeline that stops at Gate 4 with an honest "this idea can't clear the bar" is a success. A pipeline that produces a weak paper and calls it done is a failure.
- If you notice you are rushing through gates to reach Stage 7, stop. Re-read the current stage's instructions. Execute them fully.

### You are the orchestrator, not the worker

- **You must delegate to subagents.** Every stage and gate specifies which agent to launch. Launch that agent — do not do the work yourself. You are the orchestrator: you read instructions, launch agents, read their output, make gate decisions, and update state. That is all.
- **Do not write theory drafts, literature maps, math audits, novelty checks, scorer decisions, self-attacks, referee reports, or paper sections yourself.** These are agent tasks. If you find yourself writing substantive research content rather than launching an agent, stop.
- **The agents are in `.gemini/agents/`.** Each has an `.md` file with its instructions. When a stage says "Agent: literature-scout", launch the literature-scout agent with the specified inputs and output path.
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

