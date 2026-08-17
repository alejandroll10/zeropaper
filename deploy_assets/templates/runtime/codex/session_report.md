## Self-review after the report drafts

AFTER THE SYNTHESIZER PRODUCES `report/referee_report.md`, LAUNCH THE REGISTERED `report-reviewer` ROLE WITH A FRESH TASK IDENTITY AND FRESH CONTEXT. FOR ROUND N, REQUIRE THE EXACT ARTIFACT `process_log/report_self_review_r{N}.md`; ITS FIRST NON-EMPTY LINE MUST BE `CLEAN` OR `FIX`. THE REVIEWER CHECKS THREE THINGS: (1) IS EVERY MAJOR CONCERN TRACEABLE TO AN AUDIT FILE OR EXPLICITLY MARKED AS A SYNTHESIZER NOTE? (2) DO THE STRENGTHS ACCURATELY REFLECT WHAT THE PAPER DELIVERS? (3) IS THE VERDICT CONSISTENT WITH THE WEIGHT OF CONCERNS RAISED?

On Codex, spawn it with exact `agent_type="report-reviewer"`, a unique task name such as `report_reviewer_rN`, and `fork_turns="none"`; keep the parent turn alive until terminal, then validate that exact review file and verdict line. After each terminal review, stage exactly `report/referee_report.md`, `report/notes.md`, and that round's review artifact and commit them together as the durable round receipt. On `FIX`, launch a fresh `report-synthesizer` task with the exact review artifact named in its prompt, require it to repair the two report files only, increment N, and launch a fresh reviewer. Treat a task-owned uncommitted report/review diff after interruption as incomplete and regenerate it from the last committed round. Iterate until a committed `CLEAN` round; never accept a transient child message in place of the artifact.

The review is on the *report*, not on the submission — we never edit the submission.

## How to run a report

When the user says "start" or "run", check `submission/`. If empty, point them at `submission/README.md` and stop. Otherwise:

1. Run Step 1 (Triage) inline — read `submission/`, write `process_log/triage.md`. On Codex, initialize `process_log/audit_log.md` with the planned-audit block and submission hash described below, then stage and commit **triage plus that ledger together as the run baseline before spawning any audit**.
2. Launch the Step 2 audit fan-out in parallel. On Codex, use bounded waves of native `.codex/agents/` roles with fresh contexts: honor any smaller capacity reported by the tool, otherwise keep at most three children live because the four-slot session includes this parent. Fill free child slots, wait for a terminal child, validate its exact audit, append its matching audit-log row, then stage and commit **that audit plus `process_log/audit_log.md` together** before refilling. While another child is live, stage only those two exact paths—never use a broad add or include a live child's path. On OpenCode, dispatch every audit with native `task(background: true)` when that field exists in the task schema, then end the turn and let completion autowake the session; if the field is absent, use parallel foreground task calls. On Grok, use parallel native foreground `task` calls.
3. On Codex, a wait timeout means wait again; never end the parent turn with a requested child pending or running, because headless `codex exec` interrupts live children when the primary turn ends. The committed triage/ledger baseline defines the run; each atomic post-terminal audit-plus-ledger commit is its durable completion receipt. After an interrupted client/process, inspect git status and the commits after that baseline: an audit is complete only when one commit contains both its exact artifact and its matching ledger row. Treat every uncommitted audit/ledger diff or unmatched audit/row as incomplete; re-launch the owning role to rewrite/repair the audit, rebuild the ledger from the baseline plus committed receipts, validate both, and commit the pair before synthesis. Reconcile and deliberately retry errored, interrupted, shutdown, or missing children rather than treating their partial files as reports.
4. Once all audits have written to `audits/`, launch `report-synthesizer` with its exact registered role.
5. Run the versioned `report-reviewer` protocol above until a committed `CLEAN` round.

Each subagent invocation must include a self-contained prompt — the agent does not see this conversation. Point it at the specific `submission/` paths it should read and the `audits/<name>.md` path it should write.

## Update the audit log

At launch, record two things at the top of `process_log/audit_log.md`: the `planned_audits:` block from Step 1 triage (one agent name + output filename per line — this is the synthesizer's definition of expected coverage), and one `submission/` directory hash under a `submission_hash:` header. Use whichever of these works on this host (Linux usually has `sha256sum`; macOS usually has `shasum -a 256`):

```
find submission/ -type f | sort | xargs sha256sum   | sha256sum
find submission/ -type f | sort | xargs shasum -a 256 | shasum -a 256
```

Then, after each audit agent completes, append a row to the same log recording the agent name, the timestamp, and the output path. All audits in one run share the launch-time hash. The synthesizer reads this log and halts unless every `planned_audits:` entry has produced its output file. If you re-launched a hung background agent, log both invocations (the first as "abandoned").

**Codex override:** the shared report-core paragraph about polling file growth and re-launching a "hung background" agent does not apply to Codex. Native status is authoritative: keep the parent turn alive, never duplicate a pending/running child, and retry only after terminal error/interruption or interrupted-run reconciliation above.

### Use the subagents

The agent catalog is in `.codex/agents/` for Codex, `.opencode/agents/` for OpenCode, and `.grok/agents/` for Grok. Math audits, novelty checks, referee reads, citation verification, and institution checks belong to the agents. Do not do the audit work yourself.

### Read before you launch

- Before launching an agent, re-read its instructions in the agent file. Do not paraphrase from memory.
- Before launching the synthesizer, confirm every audit has produced a non-empty file in `audits/`.

### Adversarial agents must be adversarial

The audit agents are adversarial by design. Do not soften their outputs. The synthesizer's job — not yours — is to triage which findings make it into the final report.

## What this mode does not do

- Does not edit `submission/` for any reason.
- Does not iterate on the report after the self-review pass converges.
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

Skills in `{{SKILL_DIR}}/` load on demand. OpenCode uses its native `skill` tool against the same compatible `SKILL.md` files. In report mode the main relevant skills are `openalex` and `codex-math`. The latter is exposed to OpenCode from `.claude/skills/codex-math/SKILL.md` even though it is intentionally omitted from Codex's own catalog to prevent a recursive Codex-on-Codex invocation.
