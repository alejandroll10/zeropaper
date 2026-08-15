## Source
- **BLS public data API v2** — labor force, employment, earnings, CPI/PPI.
  `POST https://api.bls.gov/publicAPI/v2/timeseries/data/`. Works with **no
  key** (25 queries/day, ≤10 yrs, ≤25 series). A free `BLS_API_KEY` raises
  limits to 500/day, 20 yrs, 50 series. Register at
  https://data.bls.gov/registrationEngine/.
- **Census ACS5 + CPS basic** — county demographic/earnings panels and
  monthly CPS person extracts. `GET https://api.census.gov/data/{year}/...`.
  A free `CENSUS_API_KEY` is **required for every request** — the formerly
  keyless tier was retired; bare requests return an HTML "Missing Key" page,
  not JSON. Register at https://api.census.gov/data/key_signup.html.
- **SSA OACT period life table** — mortality / life-expectancy by exact
  age. The versioned 2023 table used in the 2026 Trustees Report is bundled
  locally with source provenance; **no key or network request**.
- Zero overlap with WRDS/CRSP; all free. Use for shift-share / Bartik
  instruments (cohort aging, local labor demand, retirement-channel
  shifters), labor-finance, household-finance, macro-cross-section work.

## Setup

```python
import os
from dotenv import load_dotenv
load_dotenv()  # BLS_API_KEY (optional), CENSUS_API_KEY (required for Census)
```

Helper at `code/utils/bls_census_utils.py`:

```python
from utils.bls_census_utils import (
    bls_series, census_get, acs_county, cps_basic_monthly,
    retirement_hazard_by_cohort, ssa_period_life_table,
)
```

BLS/Census fetches are memoised to `data/bls_census/*.parquet` (CSV fallback
if pyarrow is missing). Pass `refresh=True` to re-pull the current/open
period; closed-period data is immutable so cache hits are safe. SSA is the
exception: the default reads the checksummed bundle at
`code/utils/ssa_oact/` and never contacts the network.

## How to use

### BLS series (no key needed)

```python
df = bls_series("LNS11300000", 2010, 2024)          # LFPR, 16+
df = bls_series(["LNS11300000", "LNS12300000",      # multiple series
                 "CUUR0000SA0"], 2015, 2024)        # + CPI-U
# columns: series_id, year, period, periodName, date (period-end), value
```

`period` is `M01`–`M12` (monthly), `Q01`–`Q04` (quarterly), `A01`
(annual), or `S01`/`S02` (semi-annual); `date` is the period-end
Timestamp (annual and semi-annual stamp to Dec 31). Common series:

| Series ID | What |
|-----------|------|
| `LNS11300000` | Labor-force participation rate, 16+ |
| `LNS11300060` | LFPR, 25–54 (prime age) |
| `LNS11324230` | LFPR, 55+ |
| `LNS12300000` | Employment-population ratio, 16+ |
| `LNS14000000` | Unemployment rate |
| `CES0000000001` | Total nonfarm payroll employment (CES) |
| `CUUR0000SA0` | CPI-U, all items, US city avg |

Discover series IDs with the BLS series-report builder
(https://www.bls.gov/data/) or the "Series ID formats" pages.

**Series-ID anatomy (the #1 silent error).** The first two letters are the
survey; for the CPS labour series the 3rd letter is the seasonal-adjustment
flag — `LNS…` is **seasonally adjusted**, `LNU…` is **not** (same concept,
different number). Always state which you used.

| Prefix | Survey | Common use |
|--------|--------|------------|
| `LNS` / `LNU` | CPS (household) | LFPR, emp-pop, unemployment (SA / NSA) |
| `CES` / `CEU` | CES (establishment, SA / NSA) | Payroll employment, hours, earnings |
| `CUUR` / `CUSR` | CPI-U (NSA / SA) | Consumer prices |
| `WPU` / `WPS` | PPI (NSA / SA) | Producer prices |
| `JTU` | JOLTS | Job openings, hires, quits, layoffs |
| `ENU` | QCEW | County × industry employment & wages |
| `SMU` / `SMS` | State & area CES | Sub-national payrolls (NSA / SA) |

### Census ACS by county (key required)

```python
# Median household income + median age, all FL counties, ACS 2018-2022
df = acs_county(2022, ["B19013_001E", "B01002_001E"], state="12")
df = acs_county(2022, ["B19013_001E"])              # all US counties
```

ACS variable codes end in a suffix: `_E` = **estimate** (use this), `_M` =
margin of error (90% MOE), `_PE`/`_PM` = percent estimate/MOE. Discover
codes at `https://api.census.gov/data/{year}/acs/acs5/variables.html` and
table shells via `.../groups.html` (e.g. group `B19013` = median household
income). Use ACS5 (5-yr pooled, available for all counties); ACS1 exists
only for geographies ≥65k population.

Census returns **all-string** columns — coerce yourself. Treat the jam
values as NA, not data — these include but are **not limited to**
`-666666666` (estimate unavailable), `-999999999` / `-888888888` (not
applicable / no sample), `-222222222` (suppressed), `-333333333` (MOE
not computable), `-555555555` (controlled estimate). All official jam
values are `< -1e8`, so a single `< -1e8` mask catches every one of them
robustly — prefer that over enumerating.

### Census basic monthly CPS (key required)

```python
# Jan 2023 CPS person records for Florida, labor-force core variables
df = cps_basic_monthly(2023, "jan", state="12")
# default vars: PRTAGE PESEX PEMLR PEEDUCA PRPERTYP PWSSWGT
```

`month` accepts `1`–`12` or `'jan'`…`'dec'`. For arbitrary geographies/
datasets use `census_get(year, "acs/acs5", vars, geo_for, geo_in)`
(pass `include_name=False` for CPS — that dataset has no `NAME` variable).

**CPS variable codes (verified vs Jan-2023 FL extract).** All returned as
strings; coerce. `-1` = "not in universe" for the relevant variable
(e.g. `PEEDUCA = -1` for persons under 15) — drop, don't treat as 0.

| Var | Meaning | Codes / notes |
|-----|---------|---------------|
| `PRTAGE` | Age | individual `0`–`79`; `80`=80–84 grouped; `85`=85+ grouped (both groupings since Apr 2004 — `85` is **not** a true max) |
| `PESEX` | Sex | `1` male, `2` female |
| `PEMLR` | Labour-force recode | `1,2`=employed · `3,4`=unemployed · `5,6,7`=not in labour force |
| `PEEDUCA` | Educational attainment | `31`–`46` ladder (`39`=HS grad, `43`=bachelor's); `-1` if <15yo |
| `PRPERTYP` | Person type | `1` child · `2` adult civilian · `3` adult armed forces |
| `PWSSWGT` | Final person weight | **In persons** — `df.PWSSWGT.sum()` ≈ population. The Census API does *not* apply the 4-implied-decimal scaling of the fixed-width PUMS files; do **not** divide by 10000. Always weight estimates by this. |

### Retirement-hazard shifter (convenience)

```python
h = retirement_hazard_by_cohort(2000, 2024)
# year, lfpr_55plus, lfpr_25_54, lfpr_total,
# d_lfpr_55plus, d_lfpr_25_54, exit_proxy(=-d_lfpr_55plus)
```

**This is a transparent PROXY, not a synthetic-cohort hazard.** It is the
year-over-year change in the BLS 55+ LFPR (`LNS11324230`) benchmarked
against prime-age 25–54. BLS national LNS series are not single-year-of-age,
so true birth-cohort hazards must be built from CPS microdata via
`cps_basic_monthly` (PRTAGE × PEMLR × PWSSWGT). Override the underlying
series with `series_map=`.

### SSA period life table (no key)

```python
tables = ssa_period_life_table()       # list of DataFrames
life = tables[0]                       # male/female by single year of age
life.attrs                              # source URL + table/report vintage
```

The call is offline and returns the same two-level columns as the former live
HTML scrape. `life.attrs` records `table_year=2023`,
`trustees_report_year=2026`, the official source URL, retrieval date, bundle
status, and CSV checksum. Use `refresh=True` only to perform an explicit live
upstream check from a non-datacenter network; it validates the HTML schema
and vintage but never overwrites the immutable bundle. A custom URL preserves
the helper's historical raw `pandas.read_html` plus URL-keyed-cache escape
hatch; its caller-defined schema does not receive the official default
table's validation or provenance attributes. The full refresh procedure is
in `code/utils/ssa_oact/README.md`.

## Standard operations

- **Bartik shifter from demographics:** `acs_county` for the base-period
  industry/age shares × a national `bls_series` growth shock → shift-share
  instrument. Closed-period ACS/BLS data is cached and immutable.
- **Cohort retirement rates:** prefer CPS microdata
  (`cps_basic_monthly` looped over months/years, weighted by `PWSSWGT`)
  over the `retirement_hazard_by_cohort` proxy for any headline result;
  use the proxy only for quick exploration / robustness.
- **Macro calibration moments:** `bls_series` for CPI, payrolls, LFPR;
  pair with the `fred` skill for rates/spreads (no overlap — BLS is the
  primary source for labor series, FRED re-publishes a subset).

## Rules
- **`retirement_hazard_by_cohort` is a transparent proxy, not a hazard.**
  State this explicitly in any paper; for headline results build cohort
  rates from CPS microdata via `cps_basic_monthly`.
- **`CENSUS_API_KEY` is mandatory for ACS/CPS.** The keyless tier was
  retired; document in your methods that the key is configured. `BLS_API_KEY`
  is optional (keyless works at lower limits).
- **State your sample.** Report BLS series IDs, ACS vintage and 5-year
  pooling window, geographic scope, and any CPS variable/weight filters.
- **Cache aggressively.** Closed-period BLS/ACS/CPS data is immutable —
  rely on `data/bls_census/*.parquet`; pass `refresh=True` only for the
  current (open) year.
- **Treat the bundled SSA vintage as data provenance.** Report its
  `table_year`, `trustees_report_year`, and official `source_url` from
  `life.attrs`. Do not live-refresh it during an ordinary pipeline run.
