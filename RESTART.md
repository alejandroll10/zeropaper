# Restart — both runs stopped 2026-09-05 for travel

Both pipelines were stopped deliberately. **Neither is broken.** eventcal simply has no
driver; tradingdays is halted on purpose and wants a decision before it runs again.

Longer context, including the standing directives and a record of operator mistakes worth
not repeating, is in `OPERATOR_HANDOVER.md` in this repo.

---

## Restart eventcal (safe to do without deciding anything)

```bash
cd /mnt/data_drive/Dropbox/Dropbox/NewPapers/generated_papers/eventcal
setsid nohup ./launch.sh codex >> process_log/launch_nohup.out 2>&1 < /dev/null & disown
```

That is all. `status` is still `running`, so the orchestrator reconciles the current stage
against its artifacts on the first turn and continues.

**Where it is:** Stage 2, spec **v38** accepted at Gate 2, awaiting the fresh novelty check.
The last turn was a good one — Stage 3 caught a real R3 defect (original replication window
is June 1989–Dec 2002 while OETC starts 1994-02-04, and the spec did not separate full-roster
replication from post-1994 interoperability, so an OETC-first inner join would have silently
truncated the benchmark). v38 fixes it.

**Expect on resume:** ~79 untracked files under `code/` and `output/debug/` — scratch and
diagnostics from failed attempts. Normal, not evidence, safe to leave. No tracked file is
modified.

## Restart tradingdays (needs your decision first)

```bash
cd /mnt/data_drive/Dropbox/Dropbox/NewPapers/generated_papers/tradingdays
# 1. decide the scope question below, and write it into output/stage2/ as an operator directive
# 2. then:
python3 -c "import json,io; p='process_log/pipeline_state.json'; s=json.load(open(p)); s['status']='running'; json.dump(s, io.open(p,'w'), indent=2, ensure_ascii=False)"
setsid nohup ./launch.sh codex >> process_log/launch_nohup.out 2>&1 < /dev/null & disown
```

`loops.build_failure` is seeded **4 of cap 4** on purpose. If you resume without deciding,
the first thing it does is take the cap route back to Stage 2 rather than start a fifteenth
build. That is intended. Zero the counter explicitly if you want it to have a fresh budget.

---

## The two decisions

**1. tradingdays — is the in-house replay conformance layer in scope?**

Thirteen of the fifteen attempts spanning a112–a126 never reached a verified receipt, and
nine of those failed in the project's *own* two-isolated-root replay conformance layer while
the producer and the WRDS acquisition succeeded every time. The remaining work is a complete
bwrap mount grammar and an exact-member OS runtime closure over `/usr`, `/lib`, `/lib64`,
`.venv`, `/proc`, `/dev`.

Meanwhile the trusted runner already publishes receipts over content-hashed declared inputs
with network denied, and the data-integrity auditor already re-queries live sources from
outside the sandbox.

*My recommendation: retire the layer, and write the retirement up as a finding* — the same
treatment A2/N2 got on eventcal. A dataset paper that reports what it could not build to its
own standard is doing the genre correctly.

**2. eventcal — does R4 justify its apparatus?**

Ten build failures across v29–v37, essentially all in the sealed R4 estimator runtime:
missing transitive R imports, `Rscript CMD` vs `R CMD`, whitespace in an expression
separator, a CRAN `Archive/` 404, relative-vs-absolute library paths, a dependency-closure
mismatch across twelve packages. R4 carries ~56 spec mentions against R1's 11, and needs a
hash-pinned hermetic 13-package from-source R runtime — for one IV regression.

No scientific ceiling has been established; the mechanism auditor keeps accepting the
inclusion rules, dates, triangulation, rights boundary and portfolio. The branch-manager's
own read is that the process ceiling is **reachable, not structural**, and it pre-committed a
contingency: if a fresh implementation with the exact launcher/isolation contract still
cannot make installation and sealed execution share a closed runtime artifact, separate
runtime admission from the source build — explicitly *not* permission to drop R4, weaken
guards, narrow the portfolio, or reset the counter.

So this one is genuinely open. The cheap option is making R4 a documented non-closure like
A2/N2; the branch-manager thinks it is still winnable.

---

## State at stop

| | eventcal | tradingdays |
|---|---|---|
| status | `running`, no driver | `halted` (deliberate) |
| stage | Stage 2 | Stage 3a |
| spec version | 38 | 20 |
| `build_failure` | 10 / cap 4 (non-terminal) | 4 / 4 (seeded at cap) |
| Stage 3a receipt | **null** — never accepted, 38 versions | a61 pair active and valid |
| tracked modifications | none | none |
| disk | 82 G | 25 G |

Free space 151 G. Nothing is burning: the last several eventcal failures cost cheap
rehearsals rather than trusted builds.

## Filed upstream tonight

`LIMITATIONS.md` entries and GitHub issues, all from field evidence:

- **#308** — Stage 3a counts verdicts on produced artifacts, so an attempt dying before
  publishing a receipt increments nothing and re-fires unbounded. Fixed locally in both
  deployments as `loops.build_failure`, keyed on *counter responsibility*, not on receipt
  publication.
- **#309** — counter values quoted in narrative text go stale silently and invite adjusting
  the live counter to match. Rule added locally: the `loops` object is the only authority.
- **#310** — a spec can declare an input artifact that no step produces; Gate 2 and plan
  review both accept it.
- **#312** — a build may be the first execution of its own apparatus. Rehearsal rule added
  locally; it works, and is why recent failures cost seconds instead of hours.
- **#313** — filed and **withdrawn the same night**; the claim was falsified. Left closed
  with the correction recorded.

None of these reach a new deployment: `update.sh` is same-version-only, so only a fresh
deployment from a fixed template inherits them.

## If you want to re-arm monitoring

The watches were session-local and are gone. In a new session, ask for a monitor on each
project's git log plus `pipeline_state.json:status`, and make sure the filter catches
*failure* signatures, not just progress — a filter that only matches good news is silent
through a crashloop.
