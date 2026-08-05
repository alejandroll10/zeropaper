## Source
- Paper: Chen & Zimmerman (2022), "Open Source Cross-Sectional Asset Pricing", Review of Financial Studies
- Website: https://www.openassetpricing.com
- GitHub: https://github.com/OpenSourceAP/CrossSection
- Python package: `openassetpricing` (pip install openassetpricing)
- No authentication required

A helper is available at `code/utils/chen_zimmerman_utils.py` — use `from utils.chen_zimmerman_utils import get_signals, get_portfolios`.

## How to use

### Option 1: openassetpricing package (preferred)
```python
from openassetpricing import OpenAP
ap = OpenAP()

# Download firm-level signals (IMPORTANT: predictor must be a list)
df = ap.dl_signal('pandas', ['BM', 'Mom12m', 'AssetGrowth'])
# Returns: permno, yyyymm, BM, Mom12m, AssetGrowth

# Download portfolio returns
df = ap.dl_port('op', 'pandas', ['BM'])  # Original paper methodology
# Returns: signalname, port, date, ret, signallag, Nlong, Nshort

# Available portfolio types
ap.list_port()
# op, deciles_ew, deciles_vw, quintiles_ew, quintiles_vw, etc.

# Download all 212 signals at once (large download)
df = ap.dl_all_signals('pandas')
```

### Option 2: Direct download (fallback)
```python
import pandas as pd
# Download from: https://www.openassetpricing.com/data/
# Main file: ~1.6GB zipped CSV with 209 predictors in wide format
# Cache locally in data/ after downloading
```

## Key signals

| Signal | Description | Category |
|--------|-------------|----------|
| BM | Book-to-market ratio | Value |
| Mom12m | 12-month momentum (skip most recent month) | Momentum |
| AssetGrowth | Total asset growth | Investment |
| GP | Gross profitability | Profitability |
| EP | Earnings-to-price | Value |
| Beta | CAPM beta | Risk |
| IdioVol | Idiosyncratic volatility | Risk |
| Accruals | Operating accruals | Quality |
| SUE | Standardized unexpected earnings | Earnings |
| ShareIss1Y | Net share issuance (1 year) | Issuance |

There are 212 signals total. Use `ap.dl_signal_doc('pandas')` for the full list with paper references.

## Standard operations
- **Portfolio sorts**: `ap.dl_port('deciles_vw', 'pandas', ['BM'])` — pre-computed decile returns
- **Long-short spread**: port 10 minus port 1 from decile returns
- **Fama-MacBeth**: download signals, merge with CRSP returns, run cross-sectional regressions
- **Alpha**: regress long-short portfolio on FF5 factors
- **Signal zoo**: test whether your model's mechanism maps to any known anomaly

## Notes
- Predictor arguments must be **lists**, not strings: `['BM']` not `'BM'`
- Signals require CRSP/Compustat merge, which is already done in this dataset
- Data is updated periodically — October 2025 is the latest release
- Always state which signals you use, the sample period, and weighting scheme
