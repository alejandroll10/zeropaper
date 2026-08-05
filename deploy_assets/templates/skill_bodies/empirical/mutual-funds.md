## Source
- CRSP Survivor-Bias-Free Mutual Fund Database: `crsp_q_mutualfunds` on WRDS
- Thomson Reuters Mutual Fund Holdings: `tr_mutualfunds` on WRDS
- MFLINKS (CRSP-Thomson link): `mfl` on WRDS
- Uses the persistent WRDS server via `wrds_query()`

## Key concepts

### Identifiers
- **crsp_fundno** — identifies a share class (e.g., Class A vs Class I of the same fund). Each share class has its own returns, fees, and TNA.
- **crsp_portno** — identifies a portfolio (the actual pool of holdings). Multiple share classes map to one portfolio. Use this for holdings data.
- **crsp_cl_grp** — identifies a fund group/family.
- **wficn** — Thomson fund identifier. Use MFLINKS (`mfl.mflink1`) to link crsp_fundno → wficn → Thomson holdings.

### Share class vs portfolio
Most analyses should aggregate to the **portfolio level** (crsp_portno) to avoid double-counting. Multiple share classes of the same fund hold identical assets but differ in fees and investor type. Common approach:
- For returns: use the oldest or largest share class per portfolio, OR compute TNA-weighted average across share classes
- For holdings: use crsp_portno directly (holdings are at portfolio level)
- For flows: sum across share classes within a portfolio

## Key tables

### Returns, NAV, TNA
| Table | Description | Frequency | Key columns |
|-------|-------------|-----------|-------------|
| `crsp_q_mutualfunds.monthly_tna_ret_nav` | Monthly returns, TNA, NAV | Monthly | crsp_fundno, caldt, mret, mtna, mnav |
| `crsp_q_mutualfunds.daily_nav_ret` | Daily returns and NAV | Daily | crsp_fundno, caldt, dret, dnav |
| `crsp_q_mutualfunds.monthly_returns` | Monthly returns only | Monthly | crsp_fundno, caldt, mret |
| `crsp_q_mutualfunds.monthly_tna` | Monthly TNA only | Monthly | crsp_fundno, caldt, mtna |

### Fund characteristics
| Table | Description | Key columns |
|-------|-------------|-------------|
| `crsp_q_mutualfunds.fund_hdr` | Fund header (name, ticker, CUSIP, manager, dates) | crsp_fundno, fund_name, ticker, first_offer_dt, dead_flag, et_flag, index_fund_flag |
| `crsp_q_mutualfunds.fund_names` | Historical name/identifier changes | crsp_fundno, chgdt, chgenddt, fund_name, ticker |
| `crsp_q_mutualfunds.fund_style` | Style/objective codes over time | crsp_fundno, begdt, enddt, crsp_obj_cd, lipper_class, lipper_class_name |
| `crsp_q_mutualfunds.fund_fees` | Expense ratios, management fees, turnover | crsp_fundno, begdt, enddt, exp_ratio, mgmt_fee, turn_ratio, actual_12b1 |

### Flows
| Table | Description | Key columns |
|-------|-------------|-------------|
| `crsp_q_mutualfunds.fund_flows` | Sales and redemptions | crsp_portno, report_dt, new_sls, rein_sls, redemp |

### Holdings (CRSP)
| Table | Description | Key columns |
|-------|-------------|-------------|
| `crsp_q_mutualfunds.holdings` | Portfolio equity holdings | crsp_portno, report_dt, permno, percent_tna, nbr_shares, market_val, security_name |

### Holdings (Thomson Reuters)
| Table | Description | Key columns |
|-------|-------------|-------------|
| `tr_mutualfunds.s12` | 13F equity holdings | fundno, fdate, rdate, cusip, shares, change, assets |
| `tr_mutualfunds.s12type1` | Type 1 holdings (complete reports) | fundno, fdate, cusip, shares |

### Linking tables
| Table | Description |
|-------|-------------|
| `mfl.mflink1` | crsp_fundno → wficn (Thomson) |
| `mfl.mflink2` | wficn → Thomson fund details |
| `crsp_q_mutualfunds.portnomap` | crsp_fundno → crsp_portno mapping |

## Standard recipes

### Monthly returns with fund characteristics
```python
from utils.wrds_client import wrds_query

# Monthly returns + TNA for equity funds, post-1990
funds = wrds_query("""
    SELECT a.crsp_fundno, a.caldt, a.mret, a.mtna, a.mnav,
           b.crsp_obj_cd, b.lipper_class, b.lipper_class_name
    FROM crsp_q_mutualfunds.monthly_tna_ret_nav AS a
    LEFT JOIN crsp_q_mutualfunds.fund_style AS b
      ON a.crsp_fundno = b.crsp_fundno
      AND a.caldt BETWEEN b.begdt AND b.enddt
    WHERE a.caldt >= '1990-01-01'
      AND b.crsp_obj_cd LIKE 'ED%'  -- domestic equity
""")
```

### Filter to equity funds (common approach)
```python
# CRSP objective codes for domestic equity:
# ED = equity domestic, EDCI = cap appreciation, EDYB = equity income
# Lipper classes: EIEI, LCCE, LCGE, LCVE, MCCE, MCGE, MCVE, SCCE, SCGE, SCVE, etc.

equity_funds = wrds_query("""
    SELECT DISTINCT a.crsp_fundno
    FROM crsp_q_mutualfunds.fund_style AS a
    WHERE a.crsp_obj_cd LIKE 'ED%'
      AND a.lipper_class NOT IN ('S')  -- exclude short
""")
```

### Expense ratios and fees
```python
fees = wrds_query("""
    SELECT crsp_fundno, begdt, enddt, exp_ratio, mgmt_fee,
           turn_ratio, actual_12b1, max_12b1
    FROM crsp_q_mutualfunds.fund_fees
    WHERE exp_ratio IS NOT NULL
""")
```

### Aggregate to portfolio level (avoid share class double-counting)
```python
# Get the portnomap to identify share classes of the same portfolio
portmap = wrds_query("""
    SELECT crsp_fundno, crsp_portno
    FROM crsp_q_mutualfunds.portnomap
""")

# Merge, then aggregate (TNA-weighted returns, sum TNA)
import pandas as pd
merged = returns.merge(portmap, on='crsp_fundno')
portfolio_ret = (merged
    .groupby(['crsp_portno', 'caldt'])
    .apply(lambda g: pd.Series({
        'wret': (g['mret'] * g['mtna']).sum() / g['mtna'].sum() if g['mtna'].sum() > 0 else None,
        'tna': g['mtna'].sum()
    }))
    .reset_index()
)
```

### Compute implied flows (Sirri & Tufano 1998)
```python
# Flow = TNA_t - TNA_{t-1} * (1 + ret_t)
# Requires monthly TNA and returns at share class level
flows = wrds_query("""
    SELECT crsp_fundno, caldt, mtna, mret
    FROM crsp_q_mutualfunds.monthly_tna_ret_nav
    WHERE caldt >= '1990-01-01'
    ORDER BY crsp_fundno, caldt
""")

flows['tna_lag'] = flows.groupby('crsp_fundno')['mtna'].shift(1)
flows['implied_flow'] = (flows['mtna'] - flows['tna_lag'] * (1 + flows['mret'])) / flows['tna_lag']
```

### Link CRSP funds to Thomson holdings
```python
# Step 1: CRSP fundno -> wficn via MFLINKS
mflinks = wrds_query("""
    SELECT crsp_fundno, wficn
    FROM mfl.mflink1
    WHERE wficn IS NOT NULL
""")

# Step 2: wficn -> Thomson holdings via MFLINKS2 + s12
# mflink2.fundno = s12.fundno
link2 = wrds_query("""
    SELECT wficn, fundno
    FROM mfl.mflink2
""")

# Step 3: Get Thomson holdings
holdings = wrds_query("""
    SELECT fundno, fdate, cusip, shares, change
    FROM tr_mutualfunds.s12type1
    WHERE fdate >= '2000-01-01'
""")
```

### Fund header with active/dead status
```python
fund_info = wrds_query("""
    SELECT crsp_fundno, fund_name, ticker, first_offer_dt, end_dt,
           dead_flag, delist_cd, et_flag, index_fund_flag,
           retail_fund, inst_fund
    FROM crsp_q_mutualfunds.fund_hdr
""")

# Common filters:
# dead_flag = 'N' for active funds only
# et_flag = 'N' to exclude ETFs
# index_fund_flag IS NULL or = '' to exclude index funds
```

### Active share (Cremers-Petajisto 2009)

`ActiveShare = ½ · Σ_i |w_fund,i − w_bench,i|` over the union of stocks held by
the fund or the benchmark — the fraction of the portfolio that differs from the
index. Two inputs: **fund weights** (CRSP holdings) and **benchmark weights**
(constructed). Concretely:

1. **Fund equity weights** — from `crsp_q_mutualfunds.holdings`
   (`crsp_portno, report_dt, permno, percent_tna`). `percent_tna` is share of
   *total* assets, so it sums to <100% (cash/bonds). **Renormalize to the equity
   book**: `w_fund,i = percent_tna_i / Σ_j percent_tna_j` over equity `permno`s,
   so fund weights sum to 1 before differencing against the index.
2. **Benchmark weights** — market-cap weights of the index constituents on the
   nearest date to `report_dt`:
   ```python
   # S&P 500 constituents as of date D (native permno — cleanest path)
   members = wrds_query("""
       SELECT permno FROM crsp.msp500list
       WHERE start <= DATE '2018-12-31' AND ending >= DATE '2018-12-31'
   """)
   # market cap from CRSP monthly: |prc| * shrout  (prc can be negative = bid/ask avg)
   caps = wrds_query("""
       SELECT permno, abs(prc) * shrout AS mktcap
       FROM crsp.msf
       WHERE date = '2018-12-31' AND permno IN (%s)
   """ % ",".join(map(str, members['permno'])))
   caps['w_bench'] = caps['mktcap'] / caps['mktcap'].sum()
   ```
3. **Compute** — outer-join fund and benchmark on `permno`, fill missing weights
   with 0, then `active_share = 0.5 * (w_fund - w_bench).abs().sum()`.
4. **Assign the benchmark** (Cremers-Petajisto): pick the index that *minimizes*
   active share. Build the same cap-weights for the S&P MidCap 400 / SmallCap 600
   / Composite 1500 from `comp.idxcst_his` (filter `gvkeyx` to the index; names in
   `comp.idx_index`; link gvkey→permno via CCM), compute active share against
   each, and take the argmin.

**Limitation — Russell unavailable on this entitlement.** The full
`ftse_russell_us` (Russell 1000/2000/3000 constituents + weights) is
permission-denied here (only the `ftsesamp_russell_us` *sample* reads). The
constructible benchmark set is therefore the **S&P family** (500/400/600/1500).
Russell-benchmarked funds get assigned to their closest S&P proxy, which makes
their active share noisier than a true Russell-based figure — state this when the
sample is Russell-heavy (small/mid-cap funds especially). For validation against
the canonical series, Petajisto's published active-share data (his website) is a
free external cross-check, though it is not point-in-time current.

**Gotchas:** holdings are quarterly/semiannual and stale-dated — align `report_dt`
to the nearest index/`msf` date, don't assume month-end. Drop non-equity and
unmatched `permno`s before renormalizing. Active share alone identifies closet
indexers (low active share); **tracking error** is additionally needed to split
the *high*-active-share funds into concentrated stock-pickers (high AS, high TE)
and diversified factor bettors (high AS, low TE) — report both, not active share
alone.

## Common CRSP objective codes

| Code | Description |
|------|------------|
| EDCI | Equity Domestic - Capital Appreciation |
| EDYB | Equity Domestic - Equity Income |
| EDYM | Equity Domestic - Income and Growth |
| IC | International - Core |
| I | International - General |
| M | Mixed/Balanced |
| OB | Bond - General |

Use `crsp_obj_cd LIKE 'ED%'` for all domestic equity funds.

## Common Lipper classes

| Code | Description |
|------|------------|
| LCCE | Large-Cap Core |
| LCGE | Large-Cap Growth |
| LCVE | Large-Cap Value |
| MCCE | Mid-Cap Core |
| SCCE | Small-Cap Core |
| EIEI | Equity Income |

## Performance tips
- **Holdings table is huge** (438M rows in `crsp_q_mutualfunds.holdings`; the Thomson `s12` fund-holdings panel runs to ~150M+ rows). Always filter by crsp_portno and date range. When reloading a cached holdings parquet, never `pd.read_parquet(<whole file>)` — it will OOM; use `polars.scan_parquet(path).select([...]).filter(...).collect()` (column projection + predicate pushdown) and filter before materializing.
- **Daily returns** (182M rows): filter by crsp_fundno and date range.
- **Aggregate to portfolio level** before computing fund-level statistics to avoid share class bias.
- **Cache large downloads** to `data/mutual_funds/` as parquet.
- **Thomson s12 is legacy** — CRSP holdings (crsp_q_mutualfunds.holdings) is more recent and already matched to CRSP permnos.

## Rules
- **Portfolio level for most analyses.** Use crsp_portno for holdings, aggregate share classes for returns/flows.
- **Filter for fund type.** Always specify equity/bond/balanced using crsp_obj_cd or lipper_class.
- **Exclude ETFs** unless studying them: `et_flag = 'N'`.
- **Handle survivorship bias.** CRSP is survivor-bias-free — include dead funds (dead_flag = 'Y') for performance studies.
- **State your sample.** Report: date range, fund type filter, number of funds, whether dead funds are included, share class vs portfolio level.
