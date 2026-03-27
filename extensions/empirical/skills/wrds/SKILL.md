---
name: wrds
description: Query WRDS (Wharton Research Data Services) for CRSP, Compustat, IBES, options, insider trading, and other financial databases. Use for firm-level stock returns, accounting data, analyst forecasts, and cross-sectional/panel analysis.
user-invocable: true
argument-hint: [library.table or description]
allowed-tools: Bash, Read, Write
---

## Source
- WRDS: https://wrds-www.wharton.upenn.edu/
- Python package: `wrds` (pip install wrds)
- Credentials in `.env` as `WRDS_USER` and `WRDS_PASS`

## Connection

A persistent WRDS server runs in the background (started at pipeline launch). Duo 2FA fires once at the start of the session — after that, all queries go through instantly. Just use the client:

### How to query (use this in all scripts)

```python
import sys; sys.path.insert(0, 'code')
from utils.wrds_client import wrds_query, wrds_ping, wrds_start

# Ensure server is running (no-op if already started)
wrds_start()

# Run queries — no Duo, no connection management
df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")
```

The server handles connection persistence, threading, and cleanup. Each script just calls `wrds_query(sql)`.

## Pre-built download templates

Standard CRSP/Compustat downloads are available as ready-to-run scripts in `code/utils/`. Use these instead of writing downloads from scratch:

| Script | What it downloads | Output |
|--------|------------------|--------|
| `download_crsp_monthly.py` | CRSP monthly (msf + delistings) + CCM link + FF factors + WRDS ratios | `data/crsp_monthly_raw.parquet`, `data/ccm_link.parquet`, `data/ff_monthly.parquet` |
| `process_crsp_monthly.py` | Delisting adjustment, ME, NYSE breakpoints, filtered dataset | `data/crsp_monthly.parquet`, `data/crsp_monthly_signals.parquet` |
| `download_crsp_daily.py` | CRSP daily (year-by-year with caching) + FF daily factors | `data/crsp_daily_raw/YYYY.parquet`, `data/ff_daily.parquet` |
| `process_crsp_daily.py` | Filter, ME, NYSE breakpoints, merge with FF, excess returns | `data/crsp_daily.parquet` |

Run the download scripts first, then the processing scripts:
```bash
PYTHONPATH=code python3 code/utils/download_crsp_monthly.py
python3 code/utils/process_crsp_monthly.py
```

### Fallback: Direct connection (single-script only)

If the server isn't available, connect directly — but keep all WRDS queries in one script:

```python
import os
from dotenv import load_dotenv
load_dotenv()
import wrds

db = wrds.Connection(
    wrds_username=os.getenv('WRDS_USER'),
    wrds_password=os.getenv('WRDS_PASS')
)

# ... all queries here, using the same db object ...

db.close()  # only at the very end
```

## How to query

### Option 1: raw_sql (preferred for complex queries)
```python
df = db.raw_sql("""
    SELECT a.permno, a.date, a.ret, a.prc, a.shrout
    FROM crsp.msf AS a
    WHERE a.date BETWEEN '2000-01-01' AND '2023-12-31'
      AND a.shrcd IN (10, 11)
    LIMIT 100
""")
```

### Option 2: get_table (full table download — use LIMIT or date filters)
```python
df = db.get_table('crsp', 'msenames', columns=['permno', 'comnam', 'ticker', 'shrcd', 'exchcd'])
```

### Exploration helpers
```python
db.list_libraries()                    # all available libraries
db.list_tables(library='crsp')         # tables in a library
db.describe_table('crsp', 'msf')       # columns, types, row count
```

## Key libraries and tables

### CRSP (crsp) — Stock returns and prices
| Table | Description | Key columns |
|-------|-------------|-------------|
| `msf` | Monthly stock file | permno, date, ret, prc, shrout, vol |
| `dsf` | Daily stock file | permno, date, ret, prc, vol |
| `msenames` | Security names/identifiers | permno, comnam, ticker, shrcd, exchcd, siccd |
| `msi` / `dsi` | Market index returns | date, vwretd, ewretd, sprtrn |
| `ccmxpf_linktable` | CRSP-Compustat link | gvkey, lpermno, linkdt, linkenddt, linktype |
| `mcti` | Treasury/index returns | date, caldt, t30ret, t90ret |
| `mport1` | Mutual fund returns | crsp_fundno, caldt, mret |

**Common filters:**
- `shrcd IN (10, 11)` — ordinary common shares only
- `exchcd IN (1, 2, 3)` — NYSE, AMEX, NASDAQ
- Always filter on date to avoid pulling the entire table

### Compustat (comp) — Accounting fundamentals
| Table | Description | Key columns |
|-------|-------------|-------------|
| `funda` | Annual fundamentals | gvkey, datadate, fyear, at, sale, ni, ceq, csho, prcc_f |
| `fundq` | Quarterly fundamentals | gvkey, datadate, fqtr, atq, saleq, niq |
| `company` | Company identifiers | gvkey, conm, tic, cusip, sic, naics |
| `secd` | Daily security data | gvkey, datadate, prccd, cshoc |

**Common filters for funda:**
- `indfmt = 'INDL'` — industrial format
- `datafmt = 'STD'` — standardized data
- `popsrc = 'D'` — domestic
- `consol = 'C'` — consolidated

### IBES (ibes) — Analyst forecasts
| Table | Description | Key columns |
|-------|-------------|-------------|
| `statsum_epsus` | Summary statistics | ticker, fpedats, statpers, meanest, medest, numest |
| `det_epsus` | Individual estimates | ticker, analys, fpedats, value, revdats |
| `act_epsus` | Actual EPS | ticker, pends, value, anndats |
| `id` | Identifier mapping | ticker, cusip, cname |

### Options (optionm) — OptionMetrics
| Table | Description | Key columns |
|-------|-------------|-------------|
| `opprcd{YYYY}` | Option prices by year | secid, date, cp_flag, strike_price, best_bid, best_offer, impl_volatility, delta |
| `securd` | Security identifiers | secid, cusip, effect_date |

### Insider Trading (tfn) — Thomson Reuters
| Table | Description | Key columns |
|-------|-------------|-------------|
| `table1` | Transactions | cusip, trandate, shares, tprice, trancode |
| `idfnames` | Insider names | cusip, ownername |

### Fama-French (ff) — Factors on WRDS
| Table | Description |
|-------|-------------|
| `factors_daily` | Daily FF3 factors |
| `factors_monthly` | Monthly FF3 factors |
| `fivefactors_daily` | Daily FF5 factors |
| `fivefactors_monthly` | Monthly FF5 factors |

### ExecuComp (execcomp) — Executive compensation
| Table | Description | Key columns |
|-------|-------------|-------------|
| `anncomp` | Annual compensation | gvkey, year, execid, tdc1, tdc2, salary, bonus |

### BoardEx (boardex) — Board composition
| Table | Description |
|-------|-------------|
| `na_wrds_company_profile` | Company-level board data |
| `na_wrds_org_composition` | Individual director records |

## Standard recipes

### CRSP-Compustat merged panel
```python
# Step 1: Get the link table
ccm = db.raw_sql("""
    SELECT gvkey, lpermno AS permno, linkdt, linkenddt, linktype, linkprim
    FROM crsp.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
""")

# Step 2: Get Compustat annual data
comp = db.raw_sql("""
    SELECT gvkey, datadate, fyear, at, sale, ni, ceq, csho, prcc_f, lt
    FROM comp.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD'
      AND popsrc = 'D' AND consol = 'C'
      AND datadate BETWEEN '1963-01-01' AND '2024-12-31'
""")

# Step 3: Get CRSP monthly returns
crsp = db.raw_sql("""
    SELECT permno, date, ret, prc, shrout
    FROM crsp.msf
    WHERE date BETWEEN '1963-01-01' AND '2024-12-31'
      AND shrcd IN (10, 11)
""")

# Step 4: Merge via link table (in pandas)
import pandas as pd
comp['datadate'] = pd.to_datetime(comp['datadate'])
crsp['date'] = pd.to_datetime(crsp['date'])
ccm['linkdt'] = pd.to_datetime(ccm['linkdt'])
ccm['linkenddt'] = pd.to_datetime(ccm['linkenddt'].fillna('2099-12-31'))

# Merge comp with ccm
comp_ccm = comp.merge(ccm, on='gvkey')
# Keep valid link periods
comp_ccm = comp_ccm[
    (comp_ccm['datadate'] >= comp_ccm['linkdt']) &
    (comp_ccm['datadate'] <= comp_ccm['linkenddt'])
]
# Merge with CRSP on permno + date alignment
```

### Monthly returns with market cap
```python
df = db.raw_sql("""
    SELECT a.permno, a.date, a.ret, ABS(a.prc) * a.shrout AS mktcap,
           b.shrcd, b.exchcd, b.siccd
    FROM crsp.msf AS a
    JOIN crsp.msenames AS b
      ON a.permno = b.permno
      AND a.date BETWEEN b.namedt AND b.nameendt
    WHERE a.date BETWEEN '1963-07-01' AND '2024-12-31'
      AND b.shrcd IN (10, 11)
      AND b.exchcd IN (1, 2, 3)
""")
```

### Analyst forecast dispersion
```python
df = db.raw_sql("""
    SELECT ticker, fpedats, statpers, meanest, medest, stdev, numest
    FROM ibes.statsum_epsus
    WHERE fpi = '1'
      AND statpers BETWEEN '2000-01-01' AND '2024-12-31'
      AND numest >= 3
""")
```

## Performance tips
- **Always filter on date.** CRSP daily has ~100M rows. Never `SELECT *` without a WHERE clause.
- **Use LIMIT when exploring.** Add `LIMIT 1000` to test queries before running the full version.
- **Download once, cache locally.** For large pulls, save to `data/` as parquet: `df.to_parquet('data/crsp_monthly.parquet')`. Check for cached files before re-querying.
- **Use SQL aggregation** when possible — faster than downloading raw data and aggregating in pandas.

## Rules
- **One connection per session.** Duo 2FA fires on each `wrds.Connection()`. Never reconnect unnecessarily.
- **Credentials only in `.env`.** Never hardcode username/password.
- **Filter aggressively.** Specify date ranges, shrcd, exchcd, indfmt/datafmt/popsrc/consol filters.
- **Cache large downloads.** Save to `data/*.parquet` and check before re-querying.
- **State your sample.** Always report: date range, share code filter, exchange filter, number of firm-months.
