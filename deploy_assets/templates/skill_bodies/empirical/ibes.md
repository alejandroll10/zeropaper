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
| `ibes.statsumu_epsus` | **Unadjusted Summary** (consensus) statistics, US EPS | ticker, cusip, fpedats, statpers, fiscalp, fpi, estflag, curcode, meanest, medest, stdev, numest |
| `ibes.detu_epsus` | **Unadjusted Detail** — individual analyst estimates, US EPS | ticker, analys, estimator, fpedats, fpi, measure, value, anndats, anntims, actdats, acttims, revdats, revtims, report_curr, pdf |
| `ibes.actu_epsus` | Unadjusted reported ("Street") actuals, US EPS | ticker, pends, pdicity, measure, value, anndats, curr_act |
| `ibes.statsum_epsus` / `det_epsus` / `act_epsus` | Split-adjusted counterparts | same roles; adjusted Detail also carries merged actual fields |
| `ibes.recddet` | Detail recommendations (buy/sell ratings) | ticker, amaskcd, emaskcd, ireccd, anndats |
| `wrdsapps.ibcrsphist` | Date-bounded IBES-to-CRSP link (ICLINK) | ticker, permno, score, sdate, edate |
| `ibes.id` | IBES identifiers/company defaults — **not** the CRSP link | ticker, cusip, cname, dilfac, pdi, sdates |
| `ibes.*epsint*` | The **international** counterparts (separate files) | — |

The international files (`*epsint*`) are **separate objects** from the US (`*epsus*`)
files — never union them; pick the universe deliberately. In the US family, the
`u` immediately before `_epsus` denotes the unadjusted table. Prefer that family
for EPS-level work and perform the date-specific split alignment yourself.

## How to use
Use the persistent WRDS server via the `wrds` skill's client (`wrds_query` /
`wrds_ping`) — do **not** open a second `wrds.Connection`.

### Consensus dispersion (no actual required)

```python
from utils.wrds_client import wrds_query, wrds_ping
assert wrds_ping(), "host WRDS daemon unavailable"  # launcher handles Duo before sandboxing

# Consensus (Summary) — one row per ticker/horizon/statistical-period
cons = wrds_query("""
    SELECT ticker, cusip, fpedats, statpers, fpi, measure, estflag, curcode,
           meanest, medest, stdev, numest
    FROM ibes.statsumu_epsus
    WHERE fpi = '1' AND measure = 'EPS'              -- ALWAYS filter FPI + measure
      AND estflag = 'P'                              -- choose one company basis
      AND statpers BETWEEN '2000-01-01' AND '2024-12-31'
      AND numest >= 2
""")
```

`stdev` here is cross-analyst disagreement at a snapshot. It is not the
dispersion of realized forecast errors, and it needs no actuals join.

### Actuals for an annual forecast-error design

```python
# Keep currency and periodicity: ticker + period end is not unique.
act = wrds_query("""
    SELECT ticker, pends, measure, pdicity, value AS actual,
           anndats AS actual_anndats, anntims AS actual_anntims, curr_act
    FROM ibes.actu_epsus
    WHERE measure = 'EPS' AND pdicity = 'ANN'
      AND pends BETWEEN '2000-01-01' AND '2024-12-31'
""")
```

For the annual Summary example, join only when all of these hold:
`cons.ticker = act.ticker`, `cons.fpedats = act.pends`,
`cons.measure = act.measure`, `act.pdicity = 'ANN'`, and
`TRIM(cons.curcode) = TRIM(act.curr_act)`. Define which actual announcement
vintage to retain if a same-currency re-announcement remains. `estflag` selects
the Summary's primary or secondary parent/consolidated company basis; choose one
explicitly (the example keeps `P`). The current WRDS `actu_epsus` table does not
expose a corresponding `actualf`, so do not invent a nonexistent join column;
verify the chosen Summary series against the company-basis actual when the
secondary series matters. Then align the two values' split bases as described
below; matching keys alone does not make the subtraction valid.

### Detail issuance, activation, and confirmation timestamps

In `detu_epsus`, the usable currency field is `report_curr`; the obvious-looking
`curr` field can be entirely null. Detail rows can also contain multiple
same-day submissions. `anndats`/`anntims` say when the estimate was reported,
`actdats`/`acttims` say when IBES made it retrievable, and
`revdats`/`revtims` are the latest confirmation/reissue timestamp—not the time
of a changed forecast. For one current estimate per analyst-period, restrict
announce and activation timestamps to the information cutoff before ranking,
then order by issuance first:

```python
detail = wrds_query("""
    WITH ranked AS (
        SELECT ticker, estimator, analys, fpedats, anndats, anntims,
               actdats, acttims, measure, fpi, value, report_curr, pdf,
               revdats, revtims,
               ROW_NUMBER() OVER (
                   PARTITION BY ticker, estimator, analys, fpedats, measure, fpi
                   ORDER BY anndats DESC NULLS LAST, anntims DESC NULLS LAST,
                            actdats DESC NULLS LAST, acttims DESC NULLS LAST,
                            revdats DESC NULLS LAST, revtims DESC NULLS LAST,
                            report_curr ASC NULLS LAST, pdf ASC NULLS LAST,
                            value ASC NULLS LAST
               ) AS observation_rank
        FROM ibes.detu_epsus
        WHERE measure = 'EPS' AND fpi = '1'
          AND anndats BETWEEN '2000-01-01' AND '2024-12-31'
          -- Add announce AND activation date/time <= the design's cutoff here.
    )
    SELECT * FROM ranked WHERE observation_rank = 1
""")
```

If the task is one observation per analyst-day instead, include `anndats` in
the partition but still order first by `anntims`, then activation timestamp.
The explicit `NULLS LAST` clauses keep missing times from outranking known
times. Review timestamps are only a tie-breaker after issuance and activation;
the remaining fields make otherwise tied output deterministic. Audit exact
timestamp ties rather than silently treating that arbitrary final ordering as
economic chronology. Use review timestamps to study confirmations/staleness,
not as the revision clock. Because a later vintage can overwrite the stored
latest confirmation, pin the extract vintage whenever historical confirmation
state matters.

Cache pulls to `data/*.parquet` and reuse — IBES is large.

## Key gotchas (the reason this skill exists)
- **Summary ≠ Detail.** `statsum_epsus` (consensus) and `det_epsus` (individual
  estimates) are *different objects*. Do **not** rebuild consensus from Detail and
  expect it to equal Summary — IBES applies its own staleness/exclusion rules. Use
  Summary for consensus; use Detail only when you genuinely need analyst-level data.
- **Split adjustment + rounding corrupts EPS.** Adjusted history is continually
  restated onto the current split basis. Adjusted Summary is rounded to cents;
  adjusted Detail retains four decimals, but still carries split/rounding error.
  The distortion can erase or exaggerate differences; do not claim a universal
  direction for its effect on dispersion. Prefer **unadjusted** IBES values and
  align dates with CRSP `cfacshr`. To express an unadjusted actual on the
  estimate-date share basis, use
  `actual * cfacshr_estimate_date / cfacshr_actual_report_date`; verify the
  direction on a known split before scaling a full sample. For a Summary
  snapshot use `statpers` as the estimate-side date; for Detail use the selected
  estimate's `anndats`, never its review date. Map both a non-trading
  estimate/snapshot date and a non-trading actual report date to the last CRSP
  trading day on or before that date, so the factor was valid at the event
  timestamp; audit unmatched factor dates. Never subtract values until they
  share a basis.
- **Currency is part of the key.** Summary uses `curcode`, Detail uses
  `report_curr` (not `curr`), and Actuals uses `curr_act`. A ticker-period can
  have one actual per currency, so a join that omits currency silently subtracts
  unlike units. Matching currencies is still not enough for CRSP price scaling:
  CRSP prices are USD, so restrict the EPS quantity to USD or convert it before
  dividing by price.
- **Periodicity is part of the key.** `fpi` 1–5 are annual horizons, 6–9 are
  quarterly, and 0 is long-term growth. Match annual forecasts to
  `pdicity='ANN'` actuals (and quarterly forecasts to the appropriate quarterly
  actuals). On Summary, `fpi='1'` already selects `fiscalp='ANN'`; an extra
  `fiscalp` filter is redundant there, but the `pdicity` filter on the separate
  Actuals table is not.
- **Do not mistake confirmation time for revision time.** A changed forecast is
  a new announce timestamp. Review date/time records the most recent confirmation
  that an existing estimate remained valid. Apply announce and activation
  availability restrictions first; rank analyst-period values by
  `(anndats, anntims)` and use activation time to resolve same-announce ties.
- **`pdf` is received-basis provenance, not the stored value's basis.** IBES
  converts a Detail estimate received on a different Primary/Diluted basis to
  the company's current basis; `pdf` records how the analyst submitted it.
  Do not split or discard stored estimates merely to make their units comparable.
  If the research question needs the received basis, reconstruct it deliberately
  with the company-level `ibes.id.pdi`/`dilfac` history and document the method.
  Summary `estflag` is a different dimension: P/S selects the primary/secondary
  parent-versus-consolidated company series, not Primary/Diluted EPS. Select one
  `estflag` rather than pooling both.
- **"Street" actuals ≠ GAAP / Compustat.** IBES actuals are the analyst-basis
  ("Street") number, not GAAP EPS. When computing a surprise against an IBES
  *forecast*, use the IBES *actual* — never mix an IBES forecast with a Compustat
  actual, or the surprise is contaminated by the basis difference.
- **Always filter on FPI *and* measure.** A firm-month carries many forecast
  horizons and many measures (EPS, sales, CPS, ...). Without an `fpi` + measure
  filter you silently pool incommensurable horizons/metrics.
- **Look-ahead: use announce/activation dates, not the statistical period.** A consensus
  formed on `statpers` may embed estimates revised *after* the period label. For a
  point-in-time consensus, restrict Detail on both reported
  (`anndats`/`anntims`) and retrievable (`actdats`/`acttims`) timestamps; build
  the as-of consensus from eligible Detail when timing must be clean. Do not use
  `revdats` as value availability—it is the latest confirmation timestamp.
- **Historical restatements + recoded codes — pin the vintage.** IBES restates its
  history and periodically re-codes the anonymous analyst (`analys` in Detail,
  `amaskcd` in recommendations) and broker (`estimator`/`emaskcd`) identifiers.
  Results are not reproducible across vintages
  unless you record the extraction date; analyst/broker codes are not stable across
  re-codings.
- **Use ICLINK for CRSP — `ibes.id` is not that link.** Join IBES `ticker` to
  CRSP `permno` through `wrdsapps.ibcrsphist`, normally keeping `score <= 2`
  and requiring the observation date to fall between `sdate` and `edate`.
  Lower scores are higher-quality links. `ibes.id` supplies IBES identifiers and
  historical CUSIPs but no PERMNO, link-quality score, or complete validity
  interval; a direct current-CUSIP merge can silently mis-link.
- **US vs international are separate files** (`epsus` vs `epsint`) — see the table above.

## Standard operations
- **Earnings surprise (SUE):** `(IBES actual − consensus mean/median) / price` or
  `/ stdev`. Use the IBES actual against the IBES consensus for the matched
  measure, periodicity, currency, and split basis; align the consensus `statpers`
  to the last one *before* the earnings announcement (`anndats`). If scaling by
  CRSP price, use USD EPS or convert currencies first.
- **Forecast dispersion:** `stdev` (or `stdev/|meanest|`) from `statsumu_epsus` with
  `numest >= 2..3`; a standard analyst-disagreement proxy.
- **Revisions:** changes in `meanest` across consecutive `statpers`, or changed
  analyst-level `value` records ordered by `(anndats, anntims)` after activation
  availability filtering. Review timestamps measure confirmation/staleness.
- Always state: US vs international; FPI, measure, and periodicity; currency;
  `estflag` company basis and any use of received-basis `pdf`; adjusted vs
  unadjusted plus the exact `cfacshr` dates/formula; the ICLINK score/date rule;
  announce/activation selection; and extraction date/vintage.
