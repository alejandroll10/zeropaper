# Core-bypass guard — fail-loud against silent degradation

A **core** is a component whose substitution by a weaker path changes the *basis*
on which the run succeeds, not just its speed. A run that "succeeds" with a core
silently bypassed has shipped a weaker result than the design requires. This is
`tool failure is not substantive failure`, generalized: a core is never silently
replaced, skipped, or downgraded.

**Cores:** (a) binding external sources verified against — OpenAlex / Crossref for
citations, WRDS / EDGAR / FRED for data ("binding" = the verdict is only
trustworthy if it came from this source; a fallback like WebSearch can inform but
not certify); (b) audit/verification gates — `math-auditor`, `bib-verifier`,
`empirics-auditor`, `identification-auditor`, `data-*-auditor`, `evidence-auditor`,
`scorer`, `referee`/`editor`, polish auditors; (c) the canonical stage order and
its designated agents.

## Bypass conditions

1. **Source unavailable → weaker fallback** (binding source unreachable, work
   falls back to a non-binding substitute).
2. **Gate skipped or overridden** (not run, advanced past without a result, or
   continued *despite* a FAIL).
3. **Designated agent substituted** (assigned agent replaced by another in passing).
4. **Tool failure misclassified as source unavailability** — e.g. a
   `CERTIFICATE_VERIFY_FAILED` (a local CA-cert problem; the same lookup succeeds
   via `curl`) read as "OpenAlex unreachable." A connectivity/cert/dependency
   failure is a tool-fit failure for the `debugger` agent, never grounds to
   downgrade a binding verification.

## On hitting a bypass condition, in order

1. **Rule out tool-fit first** (conditions 1, 4): confirm a binding source is
   genuinely down — not a local tool/cert problem — before treating it as
   unavailable. Do not pivot or weaken on an un-triaged tool failure.
2. **Record it** — append a row to `process_log/degradation_ledger.md` (create it
   from the header below if absent). A manual deployment is identified by
   `process_log/manual_evidence_state.json`; it intentionally has no degradation
   ledger, so state the facts prominently in your returned report instead — never
   as a buried aside.
3. **Mark non-binding** — any verdict via a non-binding fallback is NON-BINDING and
   cannot be reported as "checked"; it does not satisfy a gate.
4. **Surface it** — a non-empty ledger appears in the run summary.

## Orchestrator-detected bypasses (conditions 2–3)

Conditions 1 and 4 are agent-detectable (a binding-source agent sees its own
source go down). Conditions 2 (gate-skipped / advanced-past / continued despite
FAIL) and 3 (designated-agent-substituted) are *orchestrator* decisions — no agent
can see that a gate was skipped or its task handed to a substitute. So the
orchestrator records these itself. **When you skip a verification gate, advance
past one without a result, continue despite a FAIL, or run a designated agent's
task via a substitute path, first check the deployment shape:** when
`process_log/manual_evidence_state.json` exists, state the `gate-skipped` /
`agent-substituted` facts prominently in the returned report and do not create a
ledger; otherwise append that row to `process_log/degradation_ledger.md` before
continuing. This applies in default mode too, not only under
`--halt-on-core-bypass`. This is the recording half; the terminal completion-block
(below) does the enforcing.

**Scope — only *unsanctioned* skips.** A skip a stage doc explicitly sanctions is
not a bypass and gets no row: e.g. empirical-first permanently skips Stage 2b and the
*math-audit* form of Gate 2 by design (`docs/stage_2.md`). Note empirical-first does
**not** skip Gate 2 wholesale — it replaces the math audit with the mechanism-plausibility
gate (`mechanism-auditor`), which is itself a designated core gate; skipping *that* IS a
bypass and must be recorded. Record only a skip or
substitution that the stage's own routing does **not** authorize. When unsure
whether a skip is sanctioned, record it (`binding? = no` if you judge it
non-degrading) — a surfaced false positive is cheaper than a silent bypass.

## Routing on a non-binding verdict — the pipeline does not stall

A non-binding verdict cannot *satisfy* a gate, but it does not park the pipeline
either: in default mode the run continues (that is the point of
record-and-surface), and the unresolved `binding? = yes` row already guarantees
the run cannot report success without the binding re-check (see the
completion block below). At a gate whose deciding verdict is non-binding:

- **Conservative verdict** (FAIL / REVISE / INCREMENTAL / KNOWN — anything that
  sends work back): route on it normally. Acting on a conservative fallback
  signal costs at most extra revision, never a falsely-passed gate — and the
  revised artifact faces a binding check once the source recovers.
- **Permissive verdict** (PASS / NOVEL — anything that would clear the gate):
  advance **provisionally**. The gate is not satisfied; the unresolved row
  stands, and the run cannot report `complete` until the verification is
  re-run as binding (the terminal backstop blocks it — it does not itself
  trigger the re-run). Weigh blast radius: the earlier the gate, the more
  downstream work rides on the provisional verdict (a provisional NOVEL at
  Gate 3 puts every later stage at risk of rework; a provisional pass at a
  late polish gate risks little). Where genuinely independent work exists —
  a parallel task that stays valuable under either outcome of the binding
  re-check — prefer it first. And while any unresolved binding row is open,
  re-probe the downed source at **every** subsequent gate/stage boundary and
  re-run the binding verification at the first recovery, so the worst case is
  caught at the next boundary, not at completion.
- **Never poll-wait.** Do not hold the gate in a probe-the-source-again loop.
  With a stated reset horizon of hours, per-turn probes burn tokens and trip
  the runtime's stuck guards (observed live: a codex driver run was halted by
  the fast-turn guard after five sub-60s no-commit poll turns at a blocked
  Gate 3). Re-probe a downed source at natural boundaries — the next gate or
  stage transition, or after a stated `Retry-After` has actually elapsed — not
  every turn. When a re-probe shows the source recovered, re-run the binding
  verification then; note the re-run in the row's `why`/`fallback` text, but
  leave `action` to the operator (below).

## Record by default; halt is opt-in

Default is **record-and-surface** (steps 2–4): the run continues so an unattended
run doesn't stall, but the degradation is durable and a non-binding result can't
pass as verified. When `pipeline_state.json` has `"halt_on_core_bypass": true`
(set by `--halt-on-core-bypass`), also set `status = "halted_core_bypass"` and
stop for operator review — the session entry point treats `halted_*` as terminal.

**Completion is never clean while a binding bypass is unresolved.** A ledger row
with `binding? = yes` is *unresolved* until that verification is re-run as binding
and the row's `action` is set to `resolved`. What an unresolved row does at
completion depends on whether the outage is **deferrable**.

### Deferrable outages complete as pending, not halted

An outage is **deferrable** when both hold:

- the source is down for a **stated, bounded horizon** — a rate limit or credit
  budget with a reset time (e.g. OpenAlex's daily budget, which resets 00:00 UTC
  and reports `Retry-After`), not an indefinite outage or a removed record; and
- **re-running the verification is cheap** — it is a lookup, not a re-derivation
  or a re-estimation.

**When the classification is ambiguous, it is not deferrable — halt.** The two
errors are not symmetric: a wrongly-halted run costs one operator poke, while a
wrongly-deferred one ships a status containing the word "complete" over a check
that may never have been possible. Same asymmetry, same answer as the
sanctioned-skip rule above.

**Under `--halt-on-core-bypass` nothing is deferrable.** That flag exists to make
a bypassed core a hard stop for strict and audit runs; deferring one would defeat
it. When `"halt_on_core_bypass": true`, take the halt path for every unresolved
binding row regardless of horizon.

A deferrable outage does **not** halt a finished run. Record the row
(`binding? = yes`, `action = recorded`), append an entry to
`pipeline_state.json`'s `pending_verification` array, and let the pipeline finish
its remaining work. At completion, set `status = "complete_pending_verification"`
instead of `"complete"`. Use exactly these keys — the driver loop reads them to
print what is outstanding:

```json
{"core": "OpenAlex bib-verify", "stage": "stage_8",
 "why": "daily credit budget exhausted; 6 cites unchecked (smith2020, ...)",
 "earliest_retry_utc": "2026-07-28T00:00:00Z"}
```

That status is the loud mark: it is not `complete`, it names itself in every
report and on the dashboard, and the pending array says exactly what was never
checked. The invariant the halt existed to protect — *never report clean success
on a core that was downgraded* — is preserved, because
`complete_pending_verification` is not clean success. What it drops is the part
that was pure friction: parking finished work in a terminal state that needed a
human to sign off on a lookup the pipeline can simply redo.

**It self-clears.** A session that opens on `complete_pending_verification`
re-probes each pending core; when one is back, it re-runs that binding
verification, and on a clean result marks the row `resolved`, removes the entry,
and sets `status = "complete"` once the array is empty. Keep the two stores in
step: resolve the ledger row and drop the array entry in the same commit. If they
ever disagree, the **ledger wins** — it is the audit record, and an unresolved
binding row means the check is still owed no matter what the array says.

If the source is still down, leave everything as is and report; nothing degrades
by waiting.

**If the re-run comes back dirty**, do not complete. The run is past Stage 10, so
re-enter the fix path explicitly: set `current_stage` back to the stage that owns
the check (`stage_8` for bibliography), `status` back to `"running"`, and work the
findings through that stage's normal loop, then Stage 9 and Stage 10 again. The
owning stage's loop cap governs as usual. If the cap is exhausted and a finding
genuinely cannot be cleared, apply that stage's documented last-resort (for
Stage 8, drop the unresolvable cites) — that is a real fix, so the row may then be
`resolved`. What you may **not** do is mark the row `resolved` while a known-bad
citation stays in the paper; if that is where you land, the run halts as
`halted_core_bypass` for an operator instead.

### Non-deferrable outages still halt

Anything not meeting both tests above — an indefinite outage, a withdrawn record,
a credential failure, a source whose re-check is expensive — keeps the old
behavior: the session entry point refuses `status = "complete"` and sets
`status = "halted_core_bypass"` for operator review. Resolved rows and
non-binding rows (`binding? = no`) are surfaced but block nothing.

### Who may mark a row resolved

A running session may set `action = resolved` **only when it has itself re-run
the binding verification to completion and it came back clean.** That is evidence,
not faith: a verification that returns a verdict proves the source answered. Note
in the row's `why`/`fallback` text that the session re-ran it and when.

A session may **not** mark a row resolved on any other basis — not because a
fallback looked clean, not because a probe returned 200, not to unblock itself.
Doing so is itself a core bypass. Everything outside the re-ran-it-and-it-passed
case remains operator-driven.

## Ledger format

| timestamp | stage | core | condition | why | fallback | binding? | action |
|-----------|-------|------|-----------|-----|----------|----------|--------|

`condition` ∈ {`source-unavailable`, `gate-skipped`, `agent-substituted`,
`tool-misclassified`}; `binding?` = `yes` if the verdict is now NON-BINDING;
`action` ∈ {`recorded`, `halted`, `resolved`}. A `binding? = yes` row is
*unresolved* until its `action` is set to `resolved` (the verification re-run as
binding). An unresolved binding row blocks a plain `status = "complete"`: a
deferrable outage completes as `complete_pending_verification`, anything else
halts. See "Who may mark a row resolved" above — a session may self-clear only a
verification it actually re-ran and passed.
