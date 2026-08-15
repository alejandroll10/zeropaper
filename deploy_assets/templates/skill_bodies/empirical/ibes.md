## Source
- I/B/E/S (Institutional Brokers' Estimate System) — analyst EPS estimates,
  consensus summaries, and reported actuals — reached through WRDS (`ibes` library).
- Requires WRDS credentials (`WRDS_USER`/`WRDS_PASS` in `.env`) and the persistent
  WRDS server — Duo 2FA fires once per session. Use the connection from the `wrds`
  skill (`from utils.wrds_client import ...`); do not open a second connection.
- The `wrds` skill carries the generic table stub; **this skill carries the access
  path plus the IBES-specific gotchas that make the data usable.** Read both.

## Key tables
| Schema.table | What it is | Key columns |
|--------------|-----------|-------------|
| `ibes.statsum_epsus` | **Summary** (consensus) statistics, US EPS | ticker, cusip, fpedats, statpers, fpi, meanest, medest, stdev, numest |
| `ibes.det_epsus` | **Detail** — individual analyst estimates, US EPS | ticker, analys, estimator, fpedats, fpi, measure, value, anndats, revdats, actdats |
| `ibes.act_epsus` | Reported ("Street") actuals, US EPS | ticker, pends, pdicity, measure, value, anndats |
| `ibes.recddet` | Detail recommendations (buy/sell ratings) | ticker, amaskcd, emaskcd, ireccd, anndats |
| `ibes.id` | IBES identifier table (CUSIP/name/ticker) | ticker, cusip, cname, sdates |
| `ibes.*epsint*` | The **international** counterparts (separate files) | — |

The international files (`*epsint*`) are **separate objects** from the US (`*epsus*`)
files — never union them; pick the universe deliberately. Each US file also has an
**unadjusted twin** named with a `u` suffix (`detu_epsus`, and likewise for the
summary/actuals files) — prefer the unadjusted twin per the split-adjustment gotcha
below.

## How to use
Use the persistent WRDS server via the `wrds` skill's client (`wrds_query` /
`wrds_ping`) — do **not** open a second `wrds.Connection`. The example below uses
the adjusted summary for brevity; for published EPS-level work pull the unadjusted
twin (`statsumu_epsus`/`detu_epsus`) and re-adjust with CRSP `cfacshr` per gotcha #2.
```python
from utils.wrds_client import wrds_query, wrds_ping
assert wrds_ping(), "host WRDS daemon unavailable"  # launcher handles Duo before sandboxing

# Consensus (Summary) — one row per ticker/horizon/statistical-period
cons = wrds_query("""
    SELECT ticker, cusip, fpedats, statpers, fpi, measure, meanest, medest, stdev, numest
    FROM ibes.statsum_epsus
    WHERE fpi = '1' AND measure = 'EPS'              -- ALWAYS filter FPI + measure
      AND statpers BETWEEN '2000-01-01' AND '2024-12-31'
      AND numest >= 2
""")

# Street actuals — match the SAME measure/horizon you forecast against
act = wrds_query("""
    SELECT ticker, pends, value AS actual, anndats AS act_anndats
    FROM ibes.act_epsus
    WHERE measure = 'EPS' AND pdicity = 'ANN'        -- match the annual (fpi='1') consensus above
""")
```
Cache pulls to `data/*.parquet` and reuse — IBES is large.

## Key gotchas (the reason this skill exists)
- **Summary ≠ Detail.** `statsum_epsus` (consensus) and `det_epsus` (individual
  estimates) are *different objects*. Do **not** rebuild consensus from Detail and
  expect it to equal Summary — IBES applies its own staleness/exclusion rules. Use
  Summary for consensus; use Detail only when you genuinely need analyst-level data.
- **Split adjustment + cent rounding corrupts EPS.** The default IBES values are
  split-adjusted and rounded to the cent, which destroys small-cap / high-split-ratio
  EPS. Prefer **unadjusted** IBES values and re-adjust yourself with the CRSP
  cumulative adjustment factor (`cfacshr`) at a consistent date.
- **"Street" actuals ≠ GAAP / Compustat.** IBES actuals are the analyst-basis
  ("Street") number, not GAAP EPS. When computing a surprise against an IBES
  *forecast*, use the IBES *actual* — never mix an IBES forecast with a Compustat
  actual, or the surprise is contaminated by the basis difference.
- **Always filter on FPI *and* measure.** A firm-month carries many forecast
  horizons (FPI = 1 one-year-ahead, 2 two-year, 6 quarterly, etc.) and many measures
  (EPS, sales, CPS, ...). Without an `fpi` + measure filter you silently pool
  incommensurable horizons/metrics.
- **Look-ahead: use revision/activation dates, not the statistical period.** A consensus
  formed on `statpers` may embed estimates revised *after* the period label. For a
  point-in-time consensus, restrict on the estimate **revision/activation dates**
  (`revdats` = revision date, `actdats` = activation date, in Detail; build as-of
  consensus from Detail when timing must be clean) and compare actuals only after
  `anndats`.
- **Historical restatements + recoded codes — pin the vintage.** IBES restates its
  history and periodically re-codes the anonymous analyst (`analys` in Detail,
  `amaskcd` in recommendations) and broker (`estimator`/`emaskcd`) identifiers.
  Results are not reproducible across vintages
  unless you record the extraction date; analyst/broker codes are not stable across
  re-codings.
- **CUSIP-based identifiers — link via the WRDS IBES-CRSP link, not a naive merge.**
  IBES uses (historical) CUSIPs and its own `ticker`. Link to CRSP `permno` with the
  WRDS IBES-CRSP linking table / the `iclink` routine, **not** a direct CUSIP join —
  a naive CUSIP merge mis-links on reused/changed CUSIPs.
- **US vs international are separate files** (`epsus` vs `epsint`) — see the table above.

## Standard operations
- **Earnings surprise (SUE):** `(IBES actual − consensus mean/median) / price` or
  `/ stdev`. Use the IBES actual against the IBES consensus for the matched
  measure/horizon; align the consensus `statpers` to the last one *before* the
  earnings announcement (`anndats`).
- **Forecast dispersion:** `stdev` (or `stdev/|meanest|`) from `statsum_epsus` with
  `numest >= 2..3`; a standard analyst-disagreement proxy.
- **Revisions:** changes in `meanest` across consecutive `statpers`, or analyst-level
  revisions from Detail (`value` across `revdats`).
- Always state: US vs international, the FPI/measure filter, adjusted vs unadjusted +
  the adjustment you applied, the linking table used, and the extraction date/vintage.
