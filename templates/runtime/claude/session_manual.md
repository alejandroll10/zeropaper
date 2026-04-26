## How to use this toolkit

When the user gives you a research task:

1. Pick the right agent or skill from the catalog above.
2. Invoke it via the Agent tool with a self-contained prompt — the subagent does not see this conversation.
3. Read its output file, decide what to do next, and either invoke another agent or return to the user.

When the user is unsure what to do next, do not guess. Read `paper/main.tex`, list `paper/sections/`, list `output/`, and list `references/`. Use what you find to propose two or three concrete next steps from the catalog (e.g., "Stage 2 theory draft exists but no math audit — launch `math-auditor`?"; "paper draft exists, no referee report — launch `referee` + `referee-mechanism` + `referee-freeform` in parallel?"; "no paper draft yet — launch `literature-scout` to start a fresh project?").

### Agent launch and monitoring

Subagents can hang indefinitely. Launch web-dependent agents (`literature-scout`, `novelty-checker`, `gap-scout`) in the background. Check their output file every few minutes — if empty or not growing after a few checks, re-launch with the same prompt.

### Skills

User-invocable skills in `{{SKILL_DIR}}/` (and `.agents/skills/` for Codex/Gemini) can be triggered directly with `/skill-name <args>` syntax in supporting runtimes, or invoked programmatically via the Skill tool.
