## Source
- SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar
- Direct API: https://data.sec.gov (no auth, just User-Agent header)
- Python package: `edgartools` (pip install edgartools) — no API key, just name+email
- Credentials in `.env` as `SEC_EDGAR_NAME` and `SEC_EDGAR_EMAIL`

## Setup

```python
from edgar import *
import os
from dotenv import load_dotenv
load_dotenv()

name = os.getenv('SEC_EDGAR_NAME', 'Research')
email = os.getenv('SEC_EDGAR_EMAIL', 'research@university.edu')
set_identity(f"{name} {email}")
```

A helper is available at `code/utils/edgar_utils.py` — use `from utils.edgar_utils import get_edgar` to get a configured connection.

## How to use

### Option 1: edgartools (preferred — structured data)

```python
from edgar import *
set_identity("Your Name your@email.edu")

# Company lookup
company = Company("AAPL")
print(company.name, company.cik)

# Get filings
filings_10k = company.get_filings(form="10-K")
filings_10q = company.get_filings(form="10-Q")
filings_8k = company.get_filings(form="8-K")

# Access a specific filing
filing = filings_10k[0]
print(filing.filing_date, filing.accession_no)

# XBRL financial facts (structured, cross-company comparable)
facts = company.get_facts()
revenue = facts.to_pandas("us-gaap:Revenues")
assets = facts.to_pandas("us-gaap:Assets")

# Insider trading (Form 4)
form4s = company.get_filings(form="4")
insider = form4s[0].obj()
print(insider.transactions)  # DataFrame of trades

# Institutional holdings (13F)
from edgar import get_filings
thirteenf = get_filings(form="13F-HR")[0].obj()
print(thirteenf.holdings)  # Portfolio positions

# Search across all companies
from edgar import get_filings
recent = get_filings(form="10-K", date="2024-01-01:2024-12-31")
```

### Option 2: Direct SEC API (no package needed)

```python
import requests

headers = {"User-Agent": "Your Name your@email.edu"}

# Company XBRL facts
url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
r = requests.get(url, headers=headers)
data = r.json()
# data['facts']['us-gaap'] contains all reported financial items

# Company concept (single item across time)
url = "https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Revenues.json"
r = requests.get(url, headers=headers)
# Returns time series of revenue filings

# Full-text search
url = "https://efts.sec.gov/LATEST/search-index?q=%22stock+buyback%22&forms=10-K&dateRange=custom&startdt=2024-01-01&enddt=2024-12-31"
r = requests.get(url, headers=headers)
# Returns filing matches with snippets

# Company submissions (all filings for a company)
url = "https://data.sec.gov/submissions/CIK0000320193.json"
r = requests.get(url, headers=headers)
# Returns recent filings, company info, SIC code, etc.
```

## Key filing types

| Form | What it contains | Use for |
|------|-----------------|---------|
| `10-K` | Annual report | Financial statements, risk factors, business description |
| `10-Q` | Quarterly report | Interim financials |
| `8-K` | Current report | Material events (M&A, earnings, management changes) |
| `DEF 14A` | Proxy statement | Executive comp, board composition, governance |
| `4` | Insider trades | Director/officer buy/sell transactions |
| `13F-HR` | Institutional holdings | Quarterly portfolio positions of large investors |
| `S-1` | IPO registration | Pre-IPO financials, risk factors |
| `SC 13D/G` | Beneficial ownership | Large shareholder positions (>5%) |
| `N-1A` | Open-end fund registration | Mutual fund / ETF prospectus, strategy, fees, classification |

## Gotchas (the ones that bite pipelines)

- **No `User-Agent` → HTTP 403.** The #1 EDGAR failure. A request with no (or a
  default `python-requests`) User-Agent is rejected outright. Always send a
  descriptive `Name email` string.
- **Rate limit: 10 requests/second, hard.** `edgartools` throttles for you; for
  the direct API add `time.sleep(0.1)` between calls and never parallelize
  blindly — sustained bursts get the host IP blocked, not just throttled.
- **CIK must be 10-digit zero-padded** in `data.sec.gov` URLs (`CIK0000320193`,
  not `CIK320193` or `320193`). `Company("TICKER")` hides this; the raw API
  does not.
- **Use XBRL for cross-company work, not filing text.** Narrative text and table
  formatting vary by filer and year; `us-gaap:*` facts are standardized.
- **XBRL coverage starts ~2009** and tag usage drifts: revenue may be
  `us-gaap:Revenues` *or*
  `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`. Check both.
- **Amendments & restatements.** `10-K/A` supersedes `10-K`; a company can
  restate prior XBRL facts. Pin the accession number when reproducibility
  matters.

## Common XBRL facts

| Concept | Tag |
|---------|-----|
| Revenue | `us-gaap:Revenues` or `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` |
| Net income | `us-gaap:NetIncomeLoss` |
| Total assets | `us-gaap:Assets` |
| Total equity | `us-gaap:StockholdersEquity` |
| EPS | `us-gaap:EarningsPerShareBasic` |
| Shares outstanding | `us-gaap:CommonStockSharesOutstanding` |
| Cash | `us-gaap:CashAndCashEquivalentsAtCarryingValue` |
| Long-term debt | `us-gaap:LongTermDebt` |
| R&D expense | `us-gaap:ResearchAndDevelopmentExpense` |
| Dividends per share | `us-gaap:CommonStockDividendsPerShareDeclared` |

## Standard recipes

### Panel of financial ratios across firms
```python
from edgar import Company
import pandas as pd

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
rows = []
for t in tickers:
    facts = Company(t).get_facts()
    rev = facts.to_pandas("us-gaap:Revenues")
    assets = facts.to_pandas("us-gaap:Assets")
    # Merge and compute ratios...
    rows.append({'ticker': t, 'rev_latest': rev.iloc[-1] if len(rev) else None})

df = pd.DataFrame(rows)
```

### Full-text search for research topics
```python
import requests
headers = {"User-Agent": "Your Name your@email.edu"}

# Find 10-Ks mentioning "climate risk"
url = 'https://efts.sec.gov/LATEST/search-index?q=%22climate+risk%22&forms=10-K&dateRange=custom&startdt=2023-01-01&enddt=2024-12-31'
r = requests.get(url, headers=headers)
data = r.json()
print(f"Found {data['hits']['total']['value']} filings")
```

### Insider trading analysis
```python
from edgar import Company
company = Company("TSLA")
form4s = company.get_filings(form="4").head(20)
for f in form4s:
    trade = f.obj()
    print(f"{f.filing_date}: {trade.reporting_owner} — {trade.transactions}")
```

## Form N-1A: open-end fund registration

`N-1A` is the registration statement and prospectus for **open-end investment
companies** — mutual funds and most ETFs. It is the EDGAR source for what a
fund *says it is*: investment objective, strategy, fee table, share classes,
adviser. Papers that classify funds (growth vs value, active vs index) read
N-1A prospectus text. Pull it like any other form (also matches `N-1A/A`):

```python
from edgar import Company
filings = Company("0002100194").get_filings(form="N-1A")
# Or across all registrants via full-text search: forms=N-1A on efts.sec.gov
```

### N-1A gotchas (fund filings are not company filings)

- **No `us-gaap` XBRL facts.** N-1A is a registration document, not a financial
  report; its XBRL is the **risk/return summary** taxonomy (`rr:*`), not
  `us-gaap:*`. `get_facts()` financials do not apply here. (The `rr:` fee-table
  parsing lives in the `sec-funds` skill.)
- **One trust filer covers many series and classes.** A single N-1A filer (the
  trust) can cover dozens of funds (**series**) each with multiple share
  **classes**, keyed by EDGAR `S######` / `C######` identifiers, not tickers.
  Resolve series/class before attributing a prospectus to a fund.
- **`485BPOS` / `485APOS` carry the updates.** The initial `N-1A` is filed once;
  ongoing annual prospectus updates arrive as `485BPOS` (immediately effective)
  and `485APOS` (post-effective amendment). For a *current* prospectus, follow
  the 485 stream, not the original N-1A.
- **ETFs file N-1A too.** Most ETFs register as open-end funds, so they are
  N-1A filers; only a few structures (e.g. some commodity pools) are not.
- **Classification is prose, not a tagged field.** Objective and strategy are
  text in the prospectus; a clean style label means parsing text or mapping the
  SEC series/class metadata, not reading one field.

For investment-adviser registration (not on EDGAR — CRD/IARD, not CIK), see the
`form-adv` skill. For N-CEN / NPORT-P / 485BPOS fee-table parsing, see
`sec-funds`.

## Performance tips
- **CIK lookup:** Use `Company("TICKER")` — edgartools resolves ticker to CIK automatically.
- **Rate limiting:** SEC allows 10 requests/second. edgartools handles this. For direct API, add `time.sleep(0.1)` between requests.
- **Cache large downloads.** Save XBRL facts to `data/` as parquet. Don't re-download.
- **Use XBRL for cross-company comparisons.** Filing text varies; XBRL facts are standardized.

## Rules
- **Credentials only in `.env`.** Never hardcode name/email.
- **Respect rate limits.** 10 req/sec max for SEC API.
- **Cache aggressively.** Save to `data/*.parquet` and check before re-downloading.
- **State your sample.** Always report: date range, filing type, number of firms, any filters applied.
