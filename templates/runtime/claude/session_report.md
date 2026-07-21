## Self-review after the report drafts

AFTER THE SYNTHESIZER PRODUCES `report/referee_report.md`, LAUNCH A SONNET AGENT TO REVIEW THE REPORT AGAINST `audits/*.md` AND `submission/`. IT CHECKS THREE THINGS: (1) IS EVERY MAJOR CONCERN TRACEABLE TO AN AUDIT FILE OR EXPLICITLY MARKED AS A SYNTHESIZER NOTE? (2) DO THE STRENGTHS ACCURATELY REFLECT WHAT THE PAPER DELIVERS? (3) IS THE VERDICT CONSISTENT WITH THE WEIGHT OF CONCERNS RAISED? IF ANY OF THE THREE FAIL, FIX AND RE-REVIEW. ITERATE UNTIL CLEAN.

Use the `general-purpose` subagent on the `sonnet` model. The review is on the *report*, not on the submission — we never edit the submission.

## How to run a report

When the user says "start" or "run", check `submission/`. If empty, point them at `submission/README.md` and stop. Otherwise:

1. Run Step 1 (Triage) inline — read `submission/`, write `process_log/triage.md`.
2. Launch the Step 2 audit fan-out in parallel via the Agent tool. Background-launch the web-dependent ones (`novelty-checker`, `polish-bibliography`, `polish-institutions`, `bib-verifier`); foreground the rest.
3. Poll background agents' output files every few minutes. If a file is empty or not growing after a few checks, re-launch with the same prompt.
4. Once all audits have written to `audits/`, launch `report-synthesizer`.
5. Run the self-review pass above.

Each subagent invocation must include a self-contained prompt — the agent does not see this conversation. Point it at the specific `submission/` paths it should read and the `audits/<name>.md` path it should write.

## Update the audit log

At launch, record two things at the top of `process_log/audit_log.md`: the `planned_audits:` block from Step 1 triage (one agent name + output filename per line — this is the synthesizer's definition of expected coverage), and one `submission/` directory hash under a `submission_hash:` header. Use whichever of these works on this host (Linux usually has `sha256sum`; macOS usually has `shasum -a 256`):

```
find submission/ -type f | sort | xargs sha256sum   | sha256sum
find submission/ -type f | sort | xargs shasum -a 256 | shasum -a 256
```

Then, after each audit agent completes, append a row to the same log recording the agent name, the timestamp, and the output path. All audits in one run share the launch-time hash. The synthesizer reads this log and halts unless every `planned_audits:` entry has produced its output file. If you re-launched a hung background agent, log both invocations (the first as "abandoned").

## What this mode does not do

- Does not edit `submission/` for any reason.
- Does not iterate on the report after the self-review pass converges. If the editor sends a revised submission, that is a fresh deployment on a fresh `submission/`.
- Does not write a recommendation letter, response-to-authors document, or revision plan — only the referee report.
- Does not invoke generative agents in this mode: `theory-generator`, `paper-writer`, `idea-generator`, `idea-reviewer`, `idea-prototyper`, `theory-explorer`, `implications-deriver`.
- Does not invoke pipeline-management agents: `scribe`, `triager`, `puzzle-triager`, `branch-manager`, `editor` (the synthesizer plays the editor-aggregation role here).
- Does not invoke the pipeline's internal scoring agents `scorer` / `scorer-freeform` (their verdicts are ADVANCE/REVISE/ABANDON, calibrated for revising our own draft — not editor-facing).
- Does not invoke broad-survey agents `literature-scout`, `gap-scout` (refereeing evaluates a specific submission, not a literature map).
- Does not invoke `style` (a style editor that modifies LaTeX in place — and we never modify the submission).
- Does not invoke `faithful-drift-auditor` (there is no mechanism contract for an external submission to drift from).
- Does not invoke `last-resort` (the stronger-model escalation agent for stubborn pipeline problems — report mode is one-shot, with no stuck pipeline to unstick).
- Does not invoke extension *generative* agents: `empiricist`, `identification-designer` (`--ext empirical`), `experiment-designer` (`--ext theory_llm`) — these design and run new analyses; in report mode we only audit what the submission already contains.

**Exception — reactive launches only:** `debugger` may be launched if an audit agent's tool call fails (e.g., a `polish-formula` `codex-math` shell-out errors). It is not part of the parallel fan-out; launch it only on a specific tool-failure report from another agent.

## Skills

User-invocable skills in `{{SKILL_DIR}}/` (and `.agents/skills/` for Codex/Gemini) can be triggered directly with `/skill-name <args>` syntax in supporting runtimes, or invoked programmatically via the Skill tool. In report mode the main relevant skills are `openalex` (for sanity-checking citations the synthesizer wants to verify) and `codex-math` (for spot-checking a derivation the math auditors flagged).
