## How to use this toolkit

There is no autonomous pipeline. The user drives — they will ask for specific research tasks (build a literature map, audit a proof, get a referee read, write a section, run an empirical test).

### Use the subagents

The agent catalog above lists subagents in `.codex/agents/` — that's the value of this toolkit. When the user asks for something an agent does, launch the agent with the appropriate prompt and inputs. Do not do the work yourself. Math audits, novelty checks, referee reads, theory exploration, paper sections, empirical analyses — these belong to the agents.

### Read before you write

- Before launching an agent, re-read its instructions in the agent file. Do not paraphrase from memory.
- Before writing any artifact, read the relevant input files.

### Adversarial agents must be adversarial

When you launch the scorer, self-attacker, or referee, they must optimize for finding problems, not for being helpful. Do not soften their outputs.

### Agent launch and monitoring

Subagents can hang indefinitely. Launch web-dependent agents (`literature-scout`, `novelty-checker`, `gap-scout`) in the background. Check their output file every few minutes — if empty or not growing after a few checks, re-launch with the same prompt.

### Skills

User-invocable skills in `{{SKILL_DIR}}/` can be triggered with `/skill-name <args>` in Codex.
