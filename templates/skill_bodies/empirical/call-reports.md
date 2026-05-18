## Source

Quarterly bank balance sheets and income statements **without** WRDS's
`bank` library or S&P CIQ. Three free, no-key sources — each with a
*different* primary key (see "The ID linking nightmare" below):

- **FFIEC CDR bulk SDF** (`call_report`) — the authoritative source for
  literal **RCON-/RIAD-coded** Call Report data (e.g. `RCON2170` = total
  assets). Every FDIC-insured commercial bank, quarterly. Pulled by
  scripting the ASP.NET bulk-download form at
  `https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx` (product
  "Call Reports -- Single Period", Tab-Delimited format). This is the
  documented free path; it is a stateful WebForms postback flow and is
  **brittle by design** — the helper fails loud (`FFIEC_FORM_BRITTLENESS`)
  with repair instructions if FFIEC changes a control. Keyed by **IDRSSD**.
- **FR Y-9C BHCF flat files** (`y9c`) — consolidated statements for bank
  **holding companies** (≥$3B assets), **BHCK-/BHCP-coded** (`BHCK2170` =
  consolidated total assets). 1986Q1–2021Q1 pulled live from the Chicago
  Fed; **2021Q2 onward is user-placed** (the Chicago Fed stopped hosting
  in-window data on 2021-06-15; the current NIC Financial Data Download is
  behind Akamai bot protection — same documented manual-step pattern as
  `hrs-scf`'s registration wall). Keyed by **RSSD9001**.
- **FDIC Financial Data API** (`fdic_financials`) — robust, no-key JSON,
  **standardized (NOT RCON-coded)** fields derived from the Call Report.
  The reliable multi-quarter path. Keyed by **CERT**; the RSSD↔CERT
  crosswalk comes from the `/institutions` endpoint (`fdic_institutions`),
  not `/financials`.

All three are free and require no API key. Opens the banking /
monetary-transmission / intermediary-asset-pricing channel (bank lending
shocks, deposits, liquidity regulation, CET1 capital, NIM).

## Setup

Helper at `code/utils/call_reports_utils.py`:

```python
from utils.call_reports_utils import (
    call_report, y9c, bank_panel,
    fdic_financials, fdic_institutions, nic_link,
    list_call_periods, parse_quarter, RC_COMMON_VARS,
)
```

No `.env` keys. Every fetch caches under `data/call_reports/` (FFIEC SDF
ZIPs, BHCF parquet, FDIC API responses are re-pulled per call but cheap).
Quarter specs are flexible: `'2023Q4'`, `'12/31/2023'`, `'20231231'`,
`(2023, 4)`, or a `datetime` — all via `parse_quarter`.

## How to use

### Literal RCON-coded Call Reports (FFIEC CDR, brittle path)

```python
list_call_periods()                       # ['03/31/2026', '12/31/2025', ...]
rc = call_report('2023Q4', schedule='RC') # balance sheet, RCON columns
ri = call_report('2023Q4', schedule='RI') # income statement, RIAD columns
jpm = call_report('2023Q4', schedule='RC', rssdids=[852218])  # one bank
```

Schedule codes are the SDF bundle's: `RC` (balance sheet), `RI` (income),
`RCRI`/`RCRII` (regulatory capital parts I/II — there is **no** `RCR`
file), `RCB`, `RCO`, `RCN`, `POR` (Panel of Reporters — bank identity,
incl. an in-file `FDIC Certificate Number` you can use as a free
RSSD→CERT crosswalk), etc. Columns are literal **MDRM codes**. An unknown
code raises a `ValueError` listing every member file in the bundle.

**Large schedules are FFIEC-split across `(1 of N)` files** (RCB, RCL,
RCN, RCO, RCQ, RCRII, RCT, …): the parts share `IDRSSD` but carry
*different* MDRM columns. `call_report` reads **all** parts and
outer-merges them on `IDRSSD` into the full wide table — you get every
variable, one row per bank, never a silently truncated subset.

**The RCON vs RCFD trap.** Total assets is `RCON2170` *or* `RCFD2170`,
never both populated for a given bank: `RCON…` = domestic-offices-only
(FFIEC 041/051 filers, the vast majority), `RCFD…` = consolidated incl.
foreign offices (FFIEC 031 filers — the largest banks). To get every
bank's total assets, coalesce: `RCFD2170` where present else `RCON2170`.
The same prefix split applies to most balance-sheet items. `RC_COMMON_VARS`
documents a practical banking-channel subset. **RCON/RIAD dollar fields
are in $thousands** (the FR MDRM convention, same as FDIC `ASSET`), so
`RCON2170 / 1e6` gives total assets in $billions.

The SDF tab-delimited files have an MDRM-code header row, a human-readable
description row (the helper drops it automatically — its `IDRSSD` cell is
non-numeric), then data. `IDRSSD` is coerced to a nullable integer.

If `call_report` raises `RuntimeError` containing the
`FFIEC_FORM_BRITTLENESS` text, the FFIEC form changed: either repair the
`_*_CTL` constants per the message, or switch to `fdic_financials` /
`bank_panel(source='fdic')` for standardized fields.

### Consolidated holding-company data (FR Y-9C)

```python
bhc = y9c('2020Q4')                       # BHCK/BHCP cols, keyed RSSD9001
bhc = y9c('2020Q4', rssdids=[1039502])    # one BHC (JPMorgan & Co.)
```

For **2021Q2 or later** the helper raises an instructive `RuntimeError`:
download the BHCF "Financial Data" bundle for that quarter from the NIC
Financial Data Download page (`www.ffiec.gov/npw/FinancialReport/DataDownload`,
Akamai-protected so it cannot be fetched server-side) and drop the file at
`data/call_reports/bhcfYYYYMM.csv`. Pre-2021Q2 quarters need no manual
step. The helper sniffs comma vs caret delimiting automatically.

### Robust standardized panel (FDIC API — the workhorse)

```python
q = fdic_financials('2023Q4')             # all ~4,600 banks, this quarter
q = fdic_financials('2023Q4', certs=[628],
        fields=['CERT','REPDTE','NAME','ASSET','DEP','NETINC','RBCT1J'])
panel = bank_panel('2021Q1', '2023Q4',    # long panel across quarters
        vars=['ASSET','DEP','LNLSNET','NETINC','NIMY'], source='fdic')
```

FDIC field codes (NOT RCON): `ASSET` total assets, `DEP` deposits,
`LNLSNET` net loans & leases, `EQ` equity, `NETINC` net income, `NIMY`
net interest margin, `RBCT1J` tier-1 capital, `ROA`, `ROE`. **FDIC dollar
fields are in $thousands.** `bank_panel(source='ffiec')` instead stacks
literal-RCON `call_report` pulls (brittle, slower).

### The RSSD ↔ CERT crosswalk

```python
fdic_institutions(certs=[628])            # -> NAME, FED_RSSD, ...
fdic_institutions(rssdids=[852218])       # reverse lookup
nic_link(852218)                          # RSSD -> CERT + identity
```

## The ID linking nightmare

There is **no single bank identifier**. The four you will meet:

| ID | Who assigns | Where | Notes |
|----|-------------|-------|-------|
| **RSSD** (a.k.a. FED RSSD, IDRSSD, RSSD9001) | Federal Reserve / NIC | Call Report `IDRSSD`, Y-9C `RSSD9001`, FDIC `FED_RSSD` | The key the academic literature joins on. Exists for **both** banks and holding companies. |
| **CERT** | FDIC | FDIC API primary key | Banks only. A bank has *both* CERT and RSSD; a BHC has only RSSD. |
| **FDIC "FED_RSSD"** | FDIC | `fdic_institutions` | The bridge: it *is* the bank's RSSD, returned alongside CERT, so CERT↔RSSD is a **lookup, never an algorithm**. |
| **SNL/CIQ key** | S&P | (paid) | Not used here; mentioned because the literature mixes it in. |

Rules of thumb:

- **Never assume RSSD == CERT.** They are unrelated integers.
- **Bank-level** analysis → key on RSSD (`IDRSSD`). **Holding-company**
  analysis → key on the BHC's `RSSD9001` from Y-9C.
- A BHC's RSSD is **not** its lead bank's RSSD. To roll banks up to their
  holder, do **not** name-match — use the NIC bulk relationships/attributes
  CSVs (`CSV_RELATIONSHIPS`, `CSV_ATTRIBUTES`) from the NIC Financial Data
  Download, joined on `ID_RSSD`. `nic_link`'s docstring documents this; it
  itself only does the reliable RSSD↔CERT lookup via the FDIC API.
- `RSSD9001` (reporter) vs `RSSD9999` (as-of date) — `9001` is the entity.

## Standard operations

- **Bank lending / deposit shock panel:** `bank_panel(start, end,
  vars=['LNLSNET','DEP','ASSET'], source='fdic')` — robust across many
  quarters. Use `source='ffiec'` only when a referee needs literal RCON
  provenance.
- **Regulatory-capital (CET1/tier-1) study:** FFIEC `call_report(q,
  schedule='RCRII')` for the RCON-coded capital schedule (auto-merged
  across its 4 SDF parts), or FDIC `RBCT1J` for a standardized tier-1
  series.
- **Intermediary asset pricing (holding-company leverage):** `y9c` BHCK
  equity / assets at the consolidated BHC level; bank-level Call Reports
  miss the holding-company leverage that the He–Kelly–Manela channel uses.
- **Merge banks to holders:** FDIC `FED_RSSD` → NIC relationships table →
  top-holder RSSD; aggregate Call Report items by holder.

## Rules

- **State which total-assets field you used.** `RCON2170` vs `RCFD2170`
  (or FDIC `ASSET` in $thousands) — and that you coalesced. Silent use of
  one drops the largest (031-filing) banks.
- **The FFIEC bulk path is brittle and acknowledged as such.** It is the
  only free literal-RCON source; if it breaks, the helper says so loudly.
  Don't paper over a `FFIEC_FORM_BRITTLENESS` error — repair the control
  constants or fall back to FDIC and say so in the methods.
- **Y-9C 2021Q2+ requires a documented one-time manual download.** This is
  a stated NIC bot-protection limit, not a helper bug; report it in the
  data appendix the way the `hrs-scf` registration step is reported.
- **Never join on a guessed ID.** RSSD↔CERT is a lookup
  (`fdic_institutions`); bank↔holder is the NIC relationships table. No
  name matching for entity resolution.
- **Report the source per series.** FFIEC RCON, Chicago-Fed/NIC BHCK, and
  FDIC standardized fields are *not* interchangeable line items; state
  which produced each number.
- **Cache aggressively.** FFIEC SDF ZIPs and BHCF tables are cached under
  `data/call_reports/` and closed-quarter bank data is immutable — reuse
  it. The FDIC API is **not** cached per call: `bank_panel(source='fdic')`
  over many quarters re-pulls (and pages) the rate-limited public API, so
  filter by `certs=` to the banks you need and persist the returned panel
  yourself (e.g. to parquet) rather than re-running the sweep.
