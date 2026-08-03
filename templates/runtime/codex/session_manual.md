## How to use this toolkit

The user will ask for specific research tasks (build a literature map, audit a proof, get a referee read, write a section, run an empirical test). When the user is unsure what to do next, read `paper/main.tex`, list `paper/sections/`, check `paper/internet_appendix.tex` (ships as a placeholder skeleton; if populated beyond that, long proofs / extensions live there — and `paper/sections/internet_appendix/` may exist), list `output/`, and list `references/`. Use what you find to propose two or three concrete next steps from the catalog rather than guessing.

Also detect which "shape" the paper is in by checking `paper/`: empty `paper/sections/` with no `paper/.git` → ask whether to import an existing paper or launch `paper-writer`; `paper/.git` exists → user has dropped in a separate paper repo, confirm `.gitignore` has a bare `paper/` line and add it if missing; `paper/sections/*.tex` exist with no `paper/.git` → flat-files pattern, proceed.

### Use the subagents

The agent catalog above is packaged for each runtime. Codex reads `.codex/agents/`; OpenCode reads `.opencode/agents/`; Grok reads `.grok/agents/`. When the user asks for something an agent does, launch it with the appropriate prompt and inputs. Math audits, novelty checks, referee reads, theory exploration, paper sections, and empirical analyses belong to the agents.

Launch agents with `code/utils/agent_launcher/launch_agent.sh <agent-id> "<task>"`, not the built-in `spawn_agent` tool. `spawn_agent` cannot pick an agent from `.codex/agents/`, ignores each agent's pinned model and reasoning effort, and hands the subagent your whole conversation by default. The launcher reads the agent's `.toml`, runs it on its pinned model/effort in a clean context, and writes the result to a file it prints (add `--sandbox read-only` for pure-audit agents; default `workspace-write` lets an agent write its artifact; when your own session is sandboxed the launcher logs that it runs the worker under your outer sandbox instead of a nested one — expected, not an error). The launcher refuses to start an agent whose earlier run is still in flight (exit 3, with instructions); use `--parallel` with distinct `--output` paths for a deliberate concurrent fan-out of the same agent, and `--force` only after verifying the earlier run is dead.

If you are OpenCode or Grok, ignore the Codex launcher paragraph above and use the native `task` tool with `subagent_type` set to the agent name. OpenCode task prompts must be self-contained. When its task schema exposes `background`, use `background: true` for independent long-running work and fan-outs; do not poll or duplicate a running child—the native completion wakes the session. Use foreground when the result is immediately blocking, or when `background` is absent from the installed version's schema.

### Read before you write

- Before launching an agent, re-read its instructions in the agent file. Do not paraphrase from memory.
- Before writing any artifact, read the relevant input files.

### Adversarial agents must be adversarial

When you launch the scorer, self-attacker, or referee, they must optimize for finding problems, not for being helpful. Do not soften their outputs.

### Agent launch and monitoring

Every launch is fire-and-forget: `launch_agent.sh` detaches the worker and returns in ~1s while the agent runs for minutes, so an early return is normal operation, not failure. Poll the output file the launcher prints by checking it ONCE and moving on — never a blocking `sleep`-loop in a single command (it hits codex's ~10s silent-exec cap). The file appears only when the worker finishes; if it appears with a `WORKER FAILED (rc=N)` banner, the agent failed (read the tail, relaunch deliberately) — it is not a real result. Do not re-launch on silence: the launcher's duplicate sentinel will refuse (exit 3) while the earlier run is alive. Re-launch only after confirming the earlier worker is gone (no codex exec process, output file never appeared), via `rm` of the sentinel it names or `--force`.

### Skills

Skills in `{{SKILL_DIR}}/` are loaded on demand. Codex can invoke them by name; OpenCode discovers the same `SKILL.md` files and loads them through its native `skill` tool. OpenCode additionally exposes `codex-math` from `.claude/skills/codex-math/SKILL.md`; it is intentionally absent from Codex's catalog because invoking the Codex-backed helper from Codex itself would be recursive.
