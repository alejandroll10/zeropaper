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
`empirics-auditor`, `identification-auditor`, `data-*-auditor`, `claim-verifier`,
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
   from the header below if absent; if there is no `process_log/`, state the facts
   prominently in your returned report — never a buried aside).
3. **Mark non-binding** — any verdict via a non-binding fallback is NON-BINDING and
   cannot be reported as "checked"; it does not satisfy a gate.
4. **Surface it** — a non-empty ledger appears in the run summary.

## Record by default; halt is opt-in

Default is **record-and-surface** (steps 2–4): the run continues so an unattended
run doesn't stall, but the degradation is durable and a non-binding result can't
pass as verified. When `pipeline_state.json` has `"halt_on_core_bypass": true`
(set by `--halt-on-core-bypass`), also set `status = "halted_core_bypass"` and
stop for operator review — the session entry point treats `halted_*` as terminal.

**Completion is blocked on an unresolved binding bypass even in default mode.** A
ledger row with `binding? = yes` is *unresolved* until the binding source is
restored, that verification is re-run, and the row's `action` is set to
`resolved`. The session entry point refuses to set `status = "complete"` while any
unresolved binding row exists — it sets `status = "halted_core_bypass"` instead.
So the default never reports clean success on a non-binding verification either; it
just halts at completion (the terminal backstop) rather than at the bypass itself
(which is what the flag does). This is what makes "ran to success while a core was
silently downgraded" impossible regardless of where the bypass occurred. Resolved
rows and non-binding-flagged rows (`binding? = no`) are surfaced but do not block
completion.

## Ledger format

| timestamp | stage | core | condition | why | fallback | binding? | action |
|-----------|-------|------|-----------|-----|----------|----------|--------|

`condition` ∈ {`source-unavailable`, `gate-skipped`, `agent-substituted`,
`tool-misclassified`}; `binding?` = `yes` if the verdict is now NON-BINDING;
`action` ∈ {`recorded`, `halted`, `resolved`}. A `binding? = yes` row is
*unresolved* until its `action` is set to `resolved` (binding source restored and
the verification re-run); an unresolved binding row blocks `status = "complete"`.
Only an operator-driven recovery may mark a row `resolved` — a running session is
**not** authorized to self-clear a binding bypass (it cannot know the source was
genuinely remedied), and doing so to unblock completion is itself a core bypass.
