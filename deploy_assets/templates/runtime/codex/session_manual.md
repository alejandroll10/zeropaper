## How to use this toolkit

The user will ask for specific research tasks (build a literature map, audit a proof, get a referee read, write a section, run an empirical test). When the user is unsure what to do next, read `paper/main.tex`, list `paper/sections/`, check `paper/internet_appendix.tex` (ships as a placeholder skeleton; if populated beyond that, long proofs / extensions live there — and `paper/sections/internet_appendix/` may exist), list `output/`, and list `references/`. Use what you find to propose two or three concrete next steps from the catalog rather than guessing.

Also detect which "shape" the paper is in by checking `paper/`: empty `paper/sections/` with no `paper/.git` → ask whether to import an existing paper or launch `paper-writer`; `paper/.git` exists → user has dropped in a separate paper repo, confirm `.gitignore` has a bare `paper/` line and add it if missing; `paper/sections/*.tex` exist with no `paper/.git` → flat-files pattern, proceed.

### Use the subagents

The agent catalog above is packaged for each runtime. Codex reads `.codex/agents/`; OpenCode reads `.opencode/agents/`; Grok reads `.grok/agents/`. When the user asks for something an agent does, launch it with the appropriate prompt and inputs. Math audits, novelty checks, referee reads, theory exploration, paper sections, and empirical analyses belong to the agents.

Codex agents are native custom roles in `.codex/agents/`. Spawn them with the native `spawn_agent` tool, setting `agent_type` to the filename stem, a unique `task_name`, and `fork_turns="none"` for a fresh context. Never omit those fields or use a full-history fork. The launcher pins this exact V2 schema; a missing field is compatibility failure, not a reason to improvise a legacy call. The role file pins its model/effort, suppresses this project AGENTS.md, and disables recursive delegation. Make each task self-contained: name every input path, required output path, decision, and output shape.

Keep the parent turn alive until every requested child is terminal. Use the native wait/status tools repeatedly; a timeout means wait again, not completion. Returning a final answer from headless `codex exec` interrupts live children. Verify every promised artifact before using the result, and deliberately reconcile/retry any errored, interrupted, shutdown, or missing child. Fan-outs use bounded waves: honor any smaller capacity reported by the tool, otherwise keep at most three children live because the four-slot session includes the parent. Give each instance a distinct task name/output path; wait for a terminal child before refilling a slot.

If you are OpenCode or Grok, ignore the Codex launcher paragraph above and use the native `task` tool with `subagent_type` set to the agent name. OpenCode task prompts must be self-contained. When its task schema exposes `background`, use `background: true` for independent long-running work and fan-outs; do not poll or duplicate a running child—the native completion wakes the session. Use foreground when the result is immediately blocking, or when `background` is absent from the installed version's schema.

### Read before you write

- Before launching an agent, re-read its instructions in the agent file. Do not paraphrase from memory.
- Before writing any artifact, read the relevant input files.

### Adversarial agents must be adversarial

When you launch the scorer, self-attacker, or referee, they must optimize for finding problems, not for being helpful. Do not soften their outputs.

### Agent launch and monitoring

Agent completion is reported by the native status/notification path. Do not infer success from elapsed time or from a partially written file; wait for terminal status and then validate the requested artifact.

### Skills

Skills in `{{SKILL_DIR}}/` are loaded on demand. Codex can invoke them by name; OpenCode discovers the same `SKILL.md` files and loads them through its native `skill` tool. OpenCode additionally exposes `codex-math` from `.claude/skills/codex-math/SKILL.md`; it is intentionally absent from Codex's catalog because invoking the Codex-backed helper from Codex itself would be recursive.
