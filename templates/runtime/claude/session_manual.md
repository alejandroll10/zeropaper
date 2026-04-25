## How to use this toolkit

You drive. There is no autonomous pipeline state to read. When the user gives you a research task:

1. Pick the right agent or skill from the catalog above.
2. Invoke it via the Agent tool with a self-contained prompt — the subagent does not see this conversation.
3. Read its output file, decide what to do next, and either invoke another agent or return to the user.

### Agent launch and monitoring

Subagents can hang indefinitely. Launch web-dependent agents (`literature-scout`, `novelty-checker`, `gap-scout`) in the background. Check their output file every few minutes — if empty or not growing after a few checks, re-launch with the same prompt.

### Skills

User-invocable skills in `{{SKILL_DIR}}/` (and `.agents/skills/` for Codex/Gemini) can be triggered directly with `/skill-name <args>` syntax in supporting runtimes, or invoked programmatically via the Skill tool.
