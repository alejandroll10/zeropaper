# Halt-path audit — all variants/modes (assembly-only, 2026-07-01)

Method: deployed 10 representative `--local` instances into `/tmp/halt_audit` covering every
distinct halt-producing code path (finance + macro base, seed, faithful, empirical-first, report,
manual, halt-on-core-bypass, --ext empirical, --ext theory_llm), then fanned out 5 auditors by
surface. Halt logic is a shared spine (core.md → CLAUDE.md/AGENTS.md/GEMINI.md + docs/*.md) plus
mode/ext deltas and a few terminal agent bodies.

## The whole design in one sentence

Almost nothing permanently stops a run. Only **7 statuses** actually terminate, and the pipeline
is deliberately biased against killing recoverable work: pre-Stage-5 failures **loop back**;
post-Stage-5 failures **ship with a limitations paragraph** (the "never-abandon" envelope). The
over-rigid cases are the exceptions to that bias.

## Every terminal status that gets SET

| Status | Where reachable | Class | Verdict |
|---|---|---|---|
| `complete` | all pipeline modes | success terminus | LEGITIMATE |
| `halted_core_bypass` | all (completion backstop by default; at bypass point with `--halt-on-core-bypass`) | integrity backstop | LEGITIMATE — blocks a false "clean success," never destroys work |
| `halted_wrds_unreachable` | --ext empirical / empirical-first | **infra-transient** | **OVER-RIGID** — halts after 1 restart, no backoff loop |
| `halted_data_audit_unreachable` | --ext empirical / empirical-first | **infra-transient** | **OVER-RIGID** — halts after 1 preflight retry, no backoff |
| `halted_replicator_self_failure` | --ext empirical | substantive (broken verifier, 3 firings) | LEGITIMATE |
| `halted_replicator_unrecognized_failure` | --ext empirical | substantive (unroutable verdict) | LEGITIMATE |
| `halted_no_identification_design` | empirical-first | structural (mode mismatch, 2 reroutes first) | LEGITIMATE |

Non-status terminal artifacts:
- `output/seed/abandon_report.md` (seed/faithful hard stops — see below)
- **undefined** "standard abandonment/escalation path" at `docs/stage_0.md:21` — the one genuine
  no-paper dead-end has **no token and no defined action** (architectural gap).

## OVER-RIGID candidates, ranked

### 1. Seed Gate-3 INCREMENTAL → terminal abandon  (= open issue #148, still live)
`finance-seed/docs/stage_2.md` Gate 3 override: a full theory that **passed Gate 2 math audit** is
abandoned (`abandon_report.md`) if novelty-checker returns KNOWN *or* INCREMENTAL and one
reformulation still returns KNOWN. INCREMENTAL is folded into the KNOWN kill path.
- Contradicts seed mode's *own* stated principle ("KNOWN → proceed if the contribution is in
  execution/proof depth; do not abandon").
- **Faithful mode already fixes this**: same signal is `[DOCUMENT-AND-PROCEED]` → logged to
  `limitations.md` + `pivot_log.md`, ships. So the fix pattern already exists in-repo.
- Fix: make seed mirror faithful — route Gate-3 INCREMENTAL (exact-package-new) to scorer with a
  novelty cap / positioning path, not abandon. Reserve abandon for KNOWN.

### 2. Transient infra → permanent halt  (= open issues #146/#147)
`halted_wrds_unreachable` (`stage_3a_empirical.md` preflight) and `halted_data_audit_unreachable`
(steps 6/7.5) fire after a **single** restart/preflight retry with no exponential/jittered backoff
at the stage level. A WRDS/Duo blip that clears in seconds stalls an unattended run pending a human.
- The recent client-level jittered-retry commit does **not** cover this stage-level preflight.
- `debugger` agent exists for exactly "a data query tool failed — tool-fit vs substantive" but is
  not on this path.
- Fix: bounded retry/backoff loop (or route through `debugger`) before setting `halted_*`.

### 3. GENUINELY-STUCK has no independent second opinion
`last-resort.md`: GENUINELY-STUCK routes straight to abandon/restructure. Its counterpart
FIX-PROPOSED always re-enters a gate for re-verification; the STUCK verdict does not. The agent body
itself flags "a false GENUINELY-STUCK abandons salvageable work" but nothing mitigates it — a
false-negative from the single strongest model ends the run unchecked.
- Fix: require a second-opinion / gate re-check before a GENUINELY-STUCK abandon is honored.

### 4. Seed prototype BLOCKED-DIFFICULTY → terminal after one retry
`finance-seed/docs/stage_1.md` Gate 1c override: BLOCKED-DIFFICULTY (a *stall*, explicitly "hard,
not foreclosed") is treated like BLOCKED-IMPOSSIBLE — one re-formalization then `prototype_blockage.md`
hard stop. Base mode's portfolio-guard + harder-technique retry are skipped in seed.
- Fix: give BLOCKED-DIFFICULTY more attempts under seed before terminating; reserve the hard stop
  for BLOCKED-IMPOSSIBLE.

### 5. Seed barren-model routing conflict (undocumented)
`docs/stage_3_implications.md` (base text, not overridden in seed): 2nd consecutive all-SUPPORTED
→ "route to Stage 1 (abandon)". But every seed override forbids Stage-1 re-entry. Resolution is
unspecified — likely collapses to `abandon_report.md`. A math-valid seed theory can be declared
"barren" and terminated with no override reconciling the conflict. Violates "no undocumented limits."

### 6. Stage-0 no-question dead-end routes into an undefined path
`docs/stage_0.md:21`: scan exhausted + re-scan used + no question ever scored → "orchestrator's
standard abandonment/escalation path" — no status token, no defined action. The only genuine
no-paper terminus is architecturally underspecified.

### 7. Fixed Gate-4 ceilings that can truncate a still-improving run (mild)
- 8-evaluation hard ceiling "regardless of trajectory" (`stage_4.md:81`) — can escalate a
  monotonically-improving REVISE-band branch (tension with "no phantom time pressure").
- branch-manager COSMETIC escalation (`stage_4.md:83`) — a false-COSMETIC call kills an improving
  branch. Judgment-dependent.
- Both mitigated: REVISE-band routes to deepening, not abandon.

## Minor spec bug
Math-audit escalation threshold is stated two ways: "3 attempts" (`CLAUDE.md:356`) vs "plateau
across 2 consecutive attempts" (`stage_2.md:31`). Same event, two thresholds — reconcile.

## Legitimate terminals (for completeness)
Gate-3 KNOWN, Gate-1c BLOCKED-IMPOSSIBLE, Gate-1b KNOWN, scorer ABANDON (theory-scoped, 5/problem,
never post-Stage-5), puzzle-triager HONEST-NULL/BACK-TO-IDEA (ship-the-null biased), all Gate-5
caps (all resolve to *ship* under the 10-round never-abandon envelope), core-bypass backstop,
empirical substantive halts, empirical-first design-mismatch halt, report-mode stops (empty/
unsupported submission, missing audit coverage — all recoverable), manual mode (no halts at all).

## Map back to open issues
- **#148** — root cause found & localized (seed `stage_2.md` Gate 3); fix pattern already exists in
  faithful mode. Highest-value, lowest-risk fix.
- **#146 / #147** — the two infra-transient halts are the concrete instances; fix = stage-level
  backoff before halt.
- New (unfiled): GENUINELY-STUCK no-second-opinion; seed BLOCKED-DIFFICULTY; seed barren-model
  routing conflict; stage-0 undefined-abandon-path; math-audit threshold inconsistency.
