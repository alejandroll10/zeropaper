---
name: edgar
description: Access SEC EDGAR filings, financial statements, and full-text search. Use for corporate finance research — 10-K/10-Q analysis, governance, disclosure, insider trading, institutional holdings.
user-invocable: true
argument-hint: [company-name, ticker, or CIK]
allowed-tools: Bash, Read, Write
---

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
