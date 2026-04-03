## Source
- FRED: https://fred.stlouisfed.org/
- API docs: https://fred.stlouisfed.org/docs/api/fred/
- Requires API key (free): https://fred.stlouisfed.org/docs/api/api_key.html
- Key goes in `.env` as `FRED_API_KEY=your-key-here`

## How to use

### Option 1: fredapi package (preferred)
```python
# pip install fredapi
from fredapi import Fred
import os
from dotenv import load_dotenv
load_dotenv()
fred = Fred(api_key=os.getenv('FRED_API_KEY'))
data = fred.get_series('GDP')
```

### Option 2: Direct API
```
https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={key}&file_type=json
```

### Option 3: No API key fallback
Download CSV directly from the FRED website:
```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP
```
This works without authentication for most series.

## Finding series
- Search the FRED website or use the API search endpoint
- Common series for finance/macro calibration:

| Series ID | Description | Frequency |
|-----------|-------------|-----------|
| GDP | Nominal GDP | Quarterly |
| GDPC1 | Real GDP | Quarterly |
| CPIAUCSL | CPI (all urban) | Monthly |
| FEDFUNDS | Fed funds rate | Monthly |
| GS10 | 10-year Treasury | Monthly |
| TB3MS | 3-month T-bill | Monthly |
| BAA10Y | Baa-10yr spread | Monthly |
| UNRATE | Unemployment rate | Monthly |
| PCE | Personal consumption | Monthly |
| PCEPILFE | Core PCE inflation | Monthly |
| VIXCLS | VIX | Daily |
| SP500 | S&P 500 | Daily |

This is not exhaustive — FRED has 800,000+ series. Search for what you need.

## Standard operations
- Compute moments: mean, std, autocorrelation of growth rates
- Business cycle statistics: HP-filter, recession indicators (USREC)
- Spreads and term structure: combine yield series
- Real vs nominal: deflate using CPI or PCE deflator
- Always state the sample period and frequency when reporting moments
