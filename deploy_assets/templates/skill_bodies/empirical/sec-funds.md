## Source
- SEC EDGAR fund filings — **N-CEN** (annual census), **NPORT-P** (monthly
  portfolio), **N-1A / 485BPOS** (prospectus fee tables).
- The `edgar` skill covers 10-K/10-Q corporate filings; fund forms use
  different XML/XBRL schemas and are **not** parsed by edgartools.
- No API key. Direct HTTP to `data.sec.gov` / `www.sec.gov/Archives` with a
  User-Agent built from `SEC_EDGAR_NAME` + `SEC_EDGAR_EMAIL` in `.env`.
- WRDS only holds a filing **index** for these forms (`wrdssec_all.forms`);
  structured fields require parsing the XML yourself — which this skill does.

## Setup

```python
import os
from dotenv import load_dotenv
load_dotenv()  # SEC_EDGAR_NAME / SEC_EDGAR_EMAIL → User-Agent
```

Helper at `code/utils/sec_funds_utils.py`:

```python
from utils.sec_funds_utils import (
    list_fund_filings, find_latest_filing,
    download_ncen, download_nport,
    download_n1a_fees, n1a_fee_table,
    flag_dc_target_funds, link_to_crsp_via_cik, list_ncen_index,
)
```

Everything except `link_to_crsp_via_cik` / `list_ncen_index` works with no
WRDS server (free EDGAR only). The helper rate-limits itself to stay under
SEC's 10 req/s fair-access limit.

## How to use

Filings are filed at the **registrant (trust) CIK**, not per fund. Workflow
is always: enumerate filings for a CIK → download/parse the form you want.

### Enumerate filings (free, no WRDS)

```python
df = list_fund_filings(36405, form="N-CEN")      # Vanguard Index Funds
df = list_fund_filings(36405, form="NPORT-P", since="2024-01-01")
acc, date = find_latest_filing(36405, "485BPOS")
# df columns: accession, form, filing_date, primary_document, report_date
```

### N-CEN — annual fund census

```python
nc = download_ncen(36405)                 # latest; or accession="...."
nc["registrant"]   # dict: registrantFullName, CIK, LEI, file no, totalSeries
nc["series"]       # DataFrame, one row per series:
#   fund_name, series_id, series_lei, num_authorized_classes,
#   num_added_classes, num_terminated_classes, is_non_diversified,
#   is_securities_lending, is_expense_limitation, is_expense_waived,
#   net_income_sec_lending, fund_types, advisers, transfer_agents
```

### NPORT-P — monthly portfolio holdings

One NPORT-P filing = one series, one month. Use `list_fund_filings(cik,
"NPORT-P")` and pick the accession for the month/series you need.

```python
p = download_nport(36405, accession="0000036405-26-000074")
p["gen_info"]   # regName, seriesName, seriesId, repPdEnd (period end)
p["fund_info"]  # totAssets, totLiabs, netAssets
p["holdings"]   # DataFrame: name, lei, title, cusip, balance, units,
                #   curCd, valUSD, pctVal, payoffProfile, assetCat,
                #   issuerCat, invCountry, isRestrictedSec, fairValLevel
                # balance / valUSD / pctVal are numeric
```

**Coverage limit:** only `<invstOrSec>` long positions are parsed.
NPORT-P `<derivativeInfo>` blocks (options, swaps, forwards, futures,
warrants) are **not** in the holdings DataFrame — a real gap for
derivatives-heavy funds (managed-futures, options-overlay strategies).

### N-1A / 485BPOS — per-share-class fee table

Fee data is the Risk/Return (`rr:`) XBRL exhibit inside a 485BPOS.
`download_n1a_fees` resolves the latest 485BPOS, falling back to **N-1A**
for initial registrations (funds too new to have filed a 485BPOS).

```python
wide = n1a_fee_table(36405)               # one row per share class
# index cols: series_id (S#########), class_id (C#########), class_member
# ratio cols (decimals, 0.01 = 1%): mgmt_fee, fee_12b1, other_exp,
#   gross_exp_ratio, net_exp_ratio, fee_waiver, acq_fund_fees,
#   redemption_fee, max_front_load, max_deferred_load
# expense-example cols ($ per $10,000 invested, NOT decimals):
#   example_1yr / 3yr / 5yr / 10yr
long = download_n1a_fees(36405)           # long form (one row per fact)
```

**Not every 485BPOS embeds Risk/Return XBRL** (sticker amendments and some
exhibit-only filings do not), and a filing can carry an rr instance with no
numeric fee facts. Either case raises `LookupError` naming the filing —
walk earlier 485BPOS accessions:

```python
for accn in list_fund_filings(cik, "485BPOS")["accession"][:8]:
    try:
        wide = n1a_fee_table(cik, accession=accn)
        break
    except LookupError:
        continue
```

### Defined-contribution targeting — heuristic, not a filed flag

**There is no "offered to defined contribution plans" field in N-CEN.**
(N-CEN Item C.7 is *securities lending*.) DC-channel targeting is inferred
from share-class names — the R1–R9 / Class R(n) / Retirement / Class K
conventions the DC channel uses (R10+ and T-series names are not matched —
false negatives; spot-check against prospectus distribution language):

```python
tagged = flag_dc_target_funds(n1a_fee_table(cik))   # adds is_dc_share_class
flag_dc_target_funds(["Class R6", "Admiral", "Class K"])  # or a name list
```

Always describe this as a name-based heuristic in the paper and spot-check
against prospectus language for the families you use. For a regulator-grade
DC signal, cross to Form 5500 Schedule H (the `form-5500` skill).

### Link to CRSP (optional, WRDS)

```python
# crsp.crsp_cik_map = [crsp_fundno, comp_cik, series_cik, contract_cik].
# A trust CIK joins comp_cik and expands 1->many (one row per series x
# class) — aggregate downstream. Join series_cik/contract_cik instead via
# crsp_cik_col= if you carry those ids.
merged = link_to_crsp_via_cik(nc["series"].assign(cik=36405))
# list_ncen_index → DataFrame[cik, coname, form, fdate, fname]
# (wrdssec_all.forms has no form_type/accession; fname = EDGAR path)
idx = list_ncen_index(year=2024)   # population enumeration from wrdssec_all.forms
```

## Standard recipes

### Fee panel across a fund family
```python
from utils.sec_funds_utils import n1a_fee_table, flag_dc_target_funds
wide = n1a_fee_table(80249)                       # T. Rowe trust
panel = flag_dc_target_funds(wide)
print(panel.groupby("is_dc_share_class")["net_exp_ratio"].mean())
```

### Holdings overlap between two funds (same month)
```python
from utils.sec_funds_utils import download_nport
a = download_nport(CIK_A, accession=ACC_A)["holdings"]
b = download_nport(CIK_B, accession=ACC_B)["holdings"]
overlap = set(a["cusip"].dropna()) & set(b["cusip"].dropna())
```

## Performance tips
- **Enumerate once.** `list_fund_filings` pages every historical shard;
  cache the returned frame to `data/*.parquet` and filter locally.
- **Cache parsed filings.** NPORT-P holdings frames are large — save to
  `data/` as parquet keyed by accession; never re-download.
- For population-scale studies prefer `list_ncen_index` (WRDS index) to
  enumerate, then fetch only the primary docs you need from free EDGAR.
- The helper already throttles to <10 req/s; don't add your own threads.

## Rules
- **Credentials only in `.env`.** Identity is built from `SEC_EDGAR_NAME` /
  `SEC_EDGAR_EMAIL`; never hardcode.
- **DC targeting is a heuristic.** State the share-class rule explicitly;
  do not present it as a filed indicator.
- **State your sample.** Report form, date range, # registrants/series,
  filings with missing XBRL, and any class-name filters applied.
- **Cache aggressively.** Save to `data/*.parquet` and check before
  re-downloading.
