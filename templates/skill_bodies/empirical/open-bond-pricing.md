## Source
- Project: Open Source Bond Asset Pricing (OSBAP) — Dickerson, Nozawa & Robotti
- Website: https://openbondassetpricing.com
- Data tabs: https://openbondassetpricing.com/data/ , https://openbondassetpricing.com/machine-learning-data/
- Portfolio-sorting package: `PyBondLab` (pip install PyBondLab)
- **No authentication, no WRDS.** Public downloads. This is the bond analog of the `chen-zimmerman` equity skill.

A helper is available at `code/utils/open_bond_pricing_utils.py` — use `from utils.open_bond_pricing_utils import get_bond_factors, get_ml_panel, list_datasets`.

## Why this exists
OSBAP already cleans raw TRACE (Enhanced/Standard/144A), applies error-correction and the +100% return-truncation fix, and ships the result as downloadable panels. Consume those — do **not** re-clean raw TRACE. If you need intraday/trade-level data beyond these panels (individual trade reports, dealer/customer flow), use the **`trace-bonds`** skill — a separate, subscription-gated WRDS `trace`-library pull, not this skill.

## How to use

### Long-short factor return series (small, start here)
```python
from utils.open_bond_pricing_utils import get_bond_factors
f = get_bond_factors('excess')          # 'excess' | 'duradj' | 'turnover'
# DataFrame: 'date' column + ~341 columns, one long-short return series per factor.
# Monthly, from 2002-08. ~2 MB download, cached under data/osbap/.
```

### Bond-month characteristics panel (heavy)
```python
from utils.open_bond_pricing_utils import get_ml_panel
panel = get_ml_panel()                  # ~886 MB download, cached. 341 ranked predictors, 2002-07..2022-12.
```

### Other datasets
```python
from utils.open_bond_pricing_utils import get_ml_predictions, get_daily_trace, list_datasets
list_datasets()                          # name -> {desc, url, approx_size_mb}
preds = get_ml_predictions()             # ~200 MB: ML predictions + realized returns
daily = get_daily_trace()                # ~1.8 GB: daily bond panel — returns, credit spreads, duration, accrued interest
```

## Datasets

| Helper | Content | Grain | Size |
|--------|---------|-------|------|
| `get_bond_factors` | ~341 long-short factor returns (excess / duration-adjusted / turnover) | monthly time series | ~2 MB |
| `get_ml_panel` | 341 cross-sectionally ranked bond+stock predictors | bond × month, 2002-07..2022-12 | ~886 MB |
| `get_ml_predictions` | ML return predictions + realized bond returns | bond × month | ~200 MB |
| `get_daily_trace` | Cleaned TRACE: returns, credit spreads, duration, accrued interest, no volume filter | bond × day | ~1.8 GB |

## Portfolio sorting (PyBondLab)
`PyBondLab` builds bond factors/portfolios from a bond panel. Pure-Python; the OSBAP panels above feed it directly. The `PyBondLab[wrds]` extra (for pulling fresh raw factors from WRDS) is **not** needed for any of the public downloads here.

## URL rot — important
OSBAP hosts each release as a **date-stamped WordPress upload** (e.g. `.../2024/10/OSBAP_ML_Panel_Oct_2024.zip`). When a new release lands, the old URL 404s. The helper's `_download` raises a clear error pointing you to the data pages. To recover:
1. Open https://openbondassetpricing.com/data/ or https://openbondassetpricing.com/machine-learning-data/
2. Copy the current link for the dataset you want.
3. Pass it through: `get_ml_panel(url='https://openbondassetpricing.com/.../NEW.zip')`.
   (Or update the `DATASETS` registry URLs in `open_bond_pricing_utils.py`.)

## Notes
- Downloads are cached under `data/osbap/`; re-runs reuse the cached zip. Pass `force=True` to `download_osbap` to refresh.
- The factor file holds three CSVs (excess / duration-adjusted / turnover); `get_bond_factors(weighting=...)` selects which.
- Reading parquet (the daily/ML panels) needs `pyarrow` — present in empirical deployments.
- Always state which dataset, release date, sample period, and weighting you used.
- Bond–Compustat/CRSP link table: https://openbondassetpricing.com/bond-compustat-crsp-link/ (download separately if you need to merge bonds to equity/fundamentals).
