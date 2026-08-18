## Source
- WRDS: https://wrds-www.wharton.upenn.edu/
- Python package: `wrds` (pip install wrds)
- Credentials in `.env` as `WRDS_USER` and `WRDS_PASS`

## Connection

A persistent, host-wide WRDS server runs in the background (started by `launch.sh` before runtime sandbox entry). The client prefers its query-only private Unix socket under `~/.local/state/zeropaper/wrds`. On Linux, where Anthropic Sandbox Runtime blocks AF_UNIX creation, the same client transparently uses a capability-authenticated query-only relay through the sandbox's local HTTP proxy. Both routes reuse the same database connection without exposing lifecycle control. Duo 2FA fires once at the start of the server session — after that, all queries go through instantly. Just use the client:

### How to query (use this in all scripts)

```python
import sys; sys.path.insert(0, 'code')
from utils.wrds_client import wrds_query, wrds_ping

# launch.sh already established the host daemon; a failed check is terminal
assert wrds_ping(), "WRDS host daemon is unavailable — halt and escalate"

# Run queries — no Duo, no connection management
df = wrds_query("SELECT * FROM crsp.msf LIMIT 5")
```

The server handles connection persistence, threading, and cleanup. Each script just calls `wrds_query(sql)`.

The v7 transport retains v6's unsigned 64-bit binary length prefix, so the
former 90 MiB response-frame ceiling no longer exists. A deliberate 512 MiB
wire safety bound and total frame deadlines reject malformed or slow-drip
peers. Response writes use a separate payload-scaled deadline rather than
inheriting the short untrusted-request timeout; an interrupted write is logged
with byte progress and the connection closes without appending a corrupt
second frame. After the last response byte is buffered, the authenticated
relay holds the connection open until the client closes it (bounded by the
same payload-scaled budget), so a buffering intermediary on the sandboxed
path cannot discard an undelivered frame tail when it observes the relay
side close first. SQL execution, response preparation, daemon-to-relay transfer,
and relay-to-client transfer have composed—not shared—wall-clock budgets, so a
query that legitimately uses its execution deadline does not leave zero time
to deliver the resulting frame. Queueing, one guarded recovery, and its retry
share one server operation deadline; the retry receives only the time left,
never a fresh query clock, and a result returning after that clock is rejected.
DataFrame conversion and final JSON encoding run in a separately bounded
producer stage whose timed-out workers cannot touch the socket and remain
under a fixed concurrency cap until they exit. Readiness treats the serialized
database owner as live only while an in-budget command holds it; an expired
command, prior healthcheck/recovery, operator unblock, or unknown owner remains
unhealthy. Normal calls use only the DB-free version handshake before submitting
their real command, so a concurrent long query cannot create a false
WRDS-unreachable halt without masking a genuinely wedged probe.
Query execution remains more tightly bounded: one `wrds_query()` may
materialize at most 1,000,000 rows and 48 MiB in the server, and
`wrds_get_table()` requires an explicit limit of at most 100,000 rows. These
are explicit safety budgets, not fixed-width framing failures.

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

There is no direct-connection fallback. A direct `wrds.Connection()` bypasses
the host-global rejection latch and can spend another login after the server
has already learned that the credential is bad. One apparent call is not a
one-attempt guarantee: the WRDS library, SQLAlchemy, a readiness loop, or a
process supervisor may reconnect or relaunch internally. If the server is
unavailable, inspect `wrds_auth_error()` and follow the terminal escalation
rule below.

## How to query

### Option 1: raw_sql (preferred for complex queries)
```python
df = wrds_query("""
    SELECT a.permno, a.date, a.ret, a.prc, a.shrout
    FROM crsp.msf AS a
    WHERE a.date BETWEEN '2000-01-01' AND '2023-12-31'
      AND a.shrcd IN (10, 11)
    LIMIT 100
""")
```

### Option 2: simple table selection (use LIMIT or date filters)
```python
df = wrds_query("""
    SELECT permno, comnam, ticker, shrcd, exchcd
    FROM crsp.msenames
    LIMIT 1000
""")
```

### Exploration helpers
```python
from utils.wrds_client import wrds_list_tables, wrds_describe
libraries = wrds_query("SELECT DISTINCT table_schema FROM information_schema.tables")
tables = wrds_list_tables('crsp')
description = wrds_describe('crsp', 'msf')
```

## Before declaring a variable/table unavailable

"Not in WRDS" is a substantive claim — never reach it as an easy-path default. Before concluding a variable, table, code value, or time window isn't there, run this protocol and log the result to `output/stage3a/data_search_log.md`:

1. **List tables.** `wrds_list_tables(library)` and grep the names for the concept. CRSP delisting/event tables (`mse`, `dsedelist`, `dse`, `dlret`) are easy to miss because they aren't in the headline table list below.
2. **Try canonical alternates.** Tables and field names get renamed across DB migrations. For delisting info try `mse` / `dsedelist` / `dlret`. For legacy CRSP fields, check `describe_table()` for the modern name. For Compustat fundamentals, try both `funda` (annual) and `fundq` (quarterly) plus `compm` variants.
3. **Search column descriptions.** `wrds_describe(lib, tbl)` returns a dataframe with column descriptions — grep those for the concept, not just exact field names.
4. **WebSearch for renames.** Query "WRDS [library] [concept] table name" or "[concept] CRSP [year] migration" — vendors publish migration notes that reveal the post-rename home.
5. **Only then is "not available" substantiated.** Write the negative-search log: what you queried, what came back, what alternates you tried, and the WebSearch results. A documentation-only check ("the docs don't mention it") is not a substitute when the question is whether a result is a coding artifact — pull the data.

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

**Documented universe sizes (order-of-magnitude sanity checks).** After applying the canonical screens above, expect roughly:
- CRSP monthly common-stock panel (`shrcd 10/11`, `exchcd 1/2/3`, full 1925/1963–present): **~3–5M firm-months**.
- Compustat annual fundamentals (`indfmt='INDL'`, `datafmt='STD'`, `popsrc='D'`, `consol='C'`, US firms): **~0.4–0.6M firm-years**.
An N that is off by an order of magnitude from these (e.g. 500K or 50M firm-months) signals an over-restrictive filter, a failed merge, or a duplicated join — investigate before trusting downstream results. These figures are approximate and drift with the sample window; use them as a smell test, not an exact target.

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
ccm = wrds_query("""
    SELECT gvkey, lpermno AS permno, linkdt, linkenddt, linktype, linkprim
    FROM crsp.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
""")

# Step 2: Get Compustat annual data
comp = wrds_query("""
    SELECT gvkey, datadate, fyear, at, sale, ni, ceq, csho, prcc_f, lt
    FROM comp.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD'
      AND popsrc = 'D' AND consol = 'C'
      AND datadate BETWEEN '1963-01-01' AND '2024-12-31'
""")

# Step 3: Get CRSP monthly returns
crsp = wrds_query("""
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
df = wrds_query("""
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
df = wrds_query("""
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
- **Window pulls that exceed a query budget.** Split by non-overlapping date or stable identifier ranges, cache each window separately, verify that boundaries neither overlap nor gap, then concatenate/scan the partitions locally. Do not respond to a row/materialization-budget error by removing filters or bypassing the shared client.
- **Download once, cache locally.** For large pulls, save to `data/` as parquet: `df.to_parquet('data/crsp_monthly.parquet')`. Check for cached files before re-querying.
- **Stream large local parquets — don't eager-load.** When reloading a cached pull (CRSP daily ~100M rows, TAQ, 13F/`s34` holdings), never `pd.read_parquet(<whole file>)`; use `polars.scan_parquet(path).select([...]).filter(...).collect()` (column projection + predicate pushdown) so you filter before materializing and never hold the full table in RAM.
- **Use SQL aggregation** when possible — faster than downloading raw data and aggregating in pandas.

## Rules
- **Use only the persistent client.** Never instantiate `wrds.Connection()` in a pipeline script; direct connections bypass the shared latch, and a library call that looks singular may retry internally. Never put WRDS startup or queries under a generic retry decorator, shell retry loop, supervisor restart policy, or fallback process, and never build another proxy/tunnel—the shipped client already owns the authenticated Linux relay. A `WrdsSafetyBlocked`/protocol-mismatch error is terminal for agents: an operator must replace the stale service with the deployed version; do not restart it yourself.
- **A credential rejection is terminal — never retry it, and never work around it.** WRDS locks the account after enough failed logins, and a locked account takes the whole empirical pipeline down for everyone on this host. The server distinguishes the two failure modes for you: a dropped socket recovers silently, but a refused credential *latches* and every later call fails fast with `[auth error]` (client side: `WrdsAuthBlocked`, or `wrds_auth_error()` returns a message; `start_services.sh` exits 2). When you see that, **halt and escalate to the operator** — report it as a blocked core per `docs/core_bypass.md` and record it in `process_log/degradation_ledger.md`. Do not re-run `wrds_start()`, do not restart the server, do not loop on `wrds_ping()`, and do not try alternate credentials. **Never call `wrds_unblock()` or `python code/utils/wrds_client.py unblock`** — that is the operator's approval gate. Lifecycle commands do not exist on the query socket. The operator stops the daemon on the host, fixes `WRDS_PASS`, then runs the unblock CLI once; the server holds the singleton while clearing the latch and reconnecting. A second rejection re-latches, so each approval costs exactly one login attempt.
- **Credentials only in `.env`.** Never hardcode username/password.
- **Filter aggressively.** Specify date ranges, shrcd, exchcd, indfmt/datafmt/popsrc/consol filters.
- **Cache large downloads.** Save to `data/*.parquet` and check before re-querying.
- **State your sample.** Always report: date range, share code filter, exchange filter, number of firm-months.
