# Model-tier fallback — probe once, fall back, never poll-wait

A subagent is pinned to a **model tier** in its `.claude/agents/*.md` frontmatter
(`fable` / `opus` / `sonnet` / `haiku`). A tier can become unreachable *after* a
project is deployed — a provider outage, an account entitlement/credits error, or
a suspension. When that happens the Task launch **fails at dispatch with no output
and no useful work done** (observed: `Agent terminated early due to an API error:
Usage credits are required for this model.`). This is a tool/infrastructure
failure, not a substantive one — but the tier will not fix itself on your
schedule, so the doctrine is **probe once, fall back, log, and keep moving**, never
sit and wait for the tier to recover.

This is the runtime safety net. The first line of defence is build-time: `setup.sh`
probes every pinned model and remaps unavailable tiers down their fallback chain
before assembly (see the "Subagent model availability & fallback" design). That
protects *new* deployments. A project assembled while a tier was healthy still
carries the original pin, so a tier that goes down *mid-life* is exactly the gap
this doc covers.

## Fallback chains

```
fable  → opus → sonnet
opus   → sonnet → haiku
sonnet → haiku
```

**Runtime scope.** These chains and the automatic setup-time remap are **Claude
only**. The other runtimes are *not* probed or remapped (a documented limitation —
see CLAUDE.md "Subagent model availability & fallback"), and have no automated
fallback support: codex pins `gpt-5.6-{sol,terra,luna}` (real tiers, but no
resolver/apply pass runs on them); gemini pins `gemini-3-preview`; grok collapses
every tier to a single `grok-4.5` model in v1, so it has no lower tier to fall back
to even in principle. So on codex/gemini/grok the *habit* still applies — probe a
suspect tier with `say hi`, don't poll-wait, surface a tier outage in the ledger —
but "relaunch on the next-lower tier" has no automated support: a non-Claude tier
outage is currently an open limitation to surface, not a gap the pipeline
self-heals. The tier names below (`fable`/`opus`/…) are Claude's.

`fable` is the tier to watch. It is pinned on only a handful of rare,
high-leverage agents (`last-resort`, `branch-manager`, `puzzle-triager`,
`idea-generator`, `question-poser`, `theory-generator`, `implications-deriver`),
so it is **rarely exercised and most prone to a stale entitlement** — credits
erroneously required, extra-charge gating, or an export/suspension state — that a
frequently-used tier would have surfaced hours earlier. Treat a `fable` launch as
the one most likely to fail on arrival.

## On a model-tier launch failure, in order

1. **Classify tier-vs-work.** Did the agent fail *at dispatch* (no output, an API
   error naming the model — see markers below), or did it do real work and fail on
   the task? Only tier failures use this doctrine; a substantive failure routes
   through the normal stage/gate logic.
2. **Probe the tier once** with a trivial prompt (`say hi` / `Reply with exactly:
   ok`) on the *same* tier. One token, near-zero cost, and it disambiguates a real
   tier outage from a one-off hiccup **before** you spend a full-context launch
   (the expensive `last-resort` payload is the whole failure history — never gamble
   that on a dead tier).
3. **Check the status page** when the probe confirms a failure:
   **https://status.claude.com/** . It tells you whether this is a *global outage*
   (component "Degraded"/incident open — wait it out on the fallback tier) or
   *account-scoped* (status green — an entitlement/credits problem specific to this
   account, which a relaunch or operator billing fix addresses). Both routes lead
   to the same immediate action:
4. **Fall back and continue.** Relaunch the *same agent* on the next tier in its
   chain (`fable → opus`) by forcing the model at launch. Do **not** wait for the
   pinned tier to return — the fallback chain exists precisely so no run depends on
   any one tier being up.
5. **Log it — as a non-binding, non-blocking row.** Append a row to
   `process_log/degradation_ledger.md` (the same ledger `docs/core_bypass.md`
   uses as the single surfacing surface), using the full schema of that doc:
   `condition = source-unavailable`, `core = <agent>`, `fallback = <tier used>`,
   **`binding? = no`**, `action = recorded`. Log **every** tier fallback, for any
   of the pinned agents — not only the two named below.

   Two deliberate points, so this doesn't collide with core-bypass semantics:
   - **This is a deliberate reuse of `source-unavailable` for a different failure
     class.** `core_bypass.md` defines that condition for a *binding external data
     source* (WRDS/OpenAlex/…) going down. Here the unavailable "source" is an
     *internal compute tier*, and the agent runs the same task on a lower tier. We
     reuse the ledger because it is the pipeline's one honest surfacing surface, not
     because this is a binding-verification bypass.
   - **A tier fallback is always `binding? = no`, so it never blocks completion.**
     The tiered-down agents (`last-resort`, `branch-manager`, `puzzle-triager`, the
     generative spine) are **not binding verification sources** — by design the
     routine evaluators/auditors are pinned off the top tier, and `last-resort`/
     `branch-manager` are advisory or re-verified by an existing gate (they never
     self-certify). So a lower-tier relaunch can dull a strategic recommendation but
     cannot falsely pass a gate. Record it (`binding? = no` rows are surfaced but do
     not block `status = "complete"`, per `core_bypass.md`); do not mark it a
     binding bypass, and do not invent a "restore the tier and re-verify" resolution
     step — there is nothing binding to re-verify. It matters most for
     `last-resort`/`branch-manager` (a weaker strategic read), which is why they are
     worth calling out — but log them all.

## Never poll-wait (as in core-bypass routing, with one added exception)

Do **not** hold work in a probe-the-tier-again loop. An outage horizon is hours,
not turns; per-turn probes burn tokens and trip the runtime's stuck guards
(observed: a codex driver run halted by the fast-turn guard after five sub-60s
no-commit poll turns). Fall back to the working tier immediately and re-probe the
downed tier only at **natural boundaries** — the next gate/stage transition, or
after a stated `Retry-After` has actually elapsed. When a re-probe shows recovery,
you *may* return to the pinned tier for subsequent launches; in-flight work stays
where it is.

The one narrow exception is a genuinely-transient error (HTTP 5xx, throttle) on a
tier that is otherwise up: there a short **bounded** retry-with-backoff is correct
(cap it — e.g. 3 attempts / a few minutes — then fall back or escalate). "Bounded
retry on a live tier" is not the same as "poll-wait for a dead tier"; only the
former is ever open to a retry loop, and even it is capped.

## Probing before an expensive rare-tier launch

You do **not** need to probe before every agent — the setup/launch guard and the
common opus/sonnet path make that a needless per-launch tax. Probe proactively in
exactly two situations:

- **Before committing an expensive full-context launch to a rarely-used high tier**
  — above all `last-resort` on `fable`, whose payload (stuck artifact + full
  failure history) is too costly to lose to a dead-on-arrival dispatch. A `say hi`
  first is cheap insurance.
- **After any tier failure**, to classify it (step 2 above).

## Marker examples (recognise semantically, don't exact-match)

A dispatch-time tier failure reads like one of:

- `Usage credits are required for this model.`
- `<model> is currently unavailable` (suspension message)
- `model not found` / `unknown model` / `invalid model`

These are *examples*, not an exhaustive allow-list — recognise the shape ("the
launch was refused because of the model tier, before any work happened") rather
than string-matching. When in doubt, the `say hi` probe settles it. (The
build-time probe in `scripts/resolve_model_fallbacks.py` keeps its own
programmatic marker list — `UNAVAILABLE_MARKERS` — for the automated setup-time
classification; all three examples above are covered there, so the setup guard
catches the same failures this runtime doctrine does. They need not stay
byte-identical, but when you add a runtime marker, add it to `UNAVAILABLE_MARKERS`
too, or the setup probe will ship an agent pinned to a tier the runtime knows is
down.)
