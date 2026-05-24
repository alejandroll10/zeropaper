## Source
- **GSW nominal** — Gürkaynak, Sack & Wright (2007), Fed FEDS 2006-28.
  - CSV: https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv
  - Docs/FAQ: https://www.federalreserve.gov/data/nominal-yield-curve.htm
- **GSW TIPS (real)** — Gürkaynak, Sack & Wright (2008), Fed FEDS 2008-05.
  - CSV: https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv
  - Docs/FAQ: https://www.federalreserve.gov/data/tips-yield-curve-and-inflation-compensation.htm
- **Liu-Wu** — Liu & Wu, "Reconstructing the Yield Curve," JFE 2021, 142(3), 1395-1425.
  - Site: https://sites.google.com/view/jingcynthiawu/yield-data
- **No authentication, no WRDS.** Fed CSVs are static stable URLs; Liu-Wu lives in Google Sheets.

A helper is at `code/utils/treasury_yields_utils.py` — use `from utils.treasury_yields_utils import gsw_nominal, gsw_tips, liu_wu, yield_on, ns_factors, list_datasets`.

## Why this exists
FRED publishes **constant-maturity par yields** (DGS10 et al.), not the continuous-maturity **zero-coupon** curve. Term-structure, monetary-policy-surprise, duration-matched discounting, and breakeven-inflation work all require zero yields, which means GSW (nominal/real) or Liu-Wu. This skill ships those panels as cached DataFrames so you don't re-implement the download/parse + Svensson math each project.

## How to use

### GSW nominal zero curve (start here)
```python
from utils.treasury_yields_utils import gsw_nominal, yield_on
df = gsw_nominal()
# DataFrame indexed by date. Columns: BETA0..BETA3, TAU1, TAU2,
#   SVENY01..SVENY30  (zero yields, continuously compounded, %)
#   SVENPY01..SVENPY30 (par yields, coupon-equivalent, %)
#   SVENF01..SVENF30   (instantaneous forwards, cc., %)
#   SVEN1F01/04/09     (1-yr forwards at 1y/4y/9y, ce., %)

df.loc['2024-12-31', 'SVENY10']     # 10y nominal zero on 2024-12-31
yield_on('2024-12-31', 7.5, source='gsw_nominal')   # 7.5y via Svensson closed form
```

### GSW TIPS (real curve + breakeven)
```python
from utils.treasury_yields_utils import gsw_tips
tips = gsw_tips()
# Columns: BETA0..BETA3, TAU1, TAU2,
#   TIPSY02..TIPSY20 (real zero, cc., %), TIPSPY02..TIPSPY20 (real par, ce., %),
#   TIPSF02..TIPSF20 (real inst. fwd, cc.), TIPS1F02/04/09 (1y fwds),
#   TIPS5F5 (5y5y forward breakeven), plus inflation-compensation columns.
```

### Liu-Wu (alternative nominal curve)
```python
from utils.treasury_yields_utils import liu_wu
m = liu_wu(freq='monthly')   # 1961-2025, ~5 MB
d = liu_wu(freq='daily')     # 1961-2025, ~60 MB
# Indexed by date. Columns are integer-string maturities in MONTHS: '1','2',...,'360'.
# Values are annualized continuously-compounded zero yields in percent.
m['120']  # 10y (= 120 months) nominal zero, full monthly time series
```

### Svensson parameters (no refit)
```python
from utils.treasury_yields_utils import ns_factors
p = ns_factors(start='2010-01-01', source='gsw_nominal')
# BETA0 ≈ level, BETA1 ≈ -slope, BETA2 ≈ curvature 1, BETA3 ≈ curvature 2
# (BETA3 == 0 and TAU2 NaN pre-1980 — those rows are Nelson-Siegel, not Svensson.)
```

## Datasets

| Helper | Content | Grain | Sample | Size |
|--------|---------|-------|--------|------|
| `gsw_nominal()` | Svensson params + SVENY/SVENPY/SVENF/SVEN1F panels | daily | 1961-06+ | ~17 MB |
| `gsw_tips()` | Svensson params + TIPSY/TIPSPY/TIPSF panels + breakevens | daily | 1999-01+ | ~15 MB |
| `liu_wu('monthly')` | Zero yields, maturities 1..360 months | monthly | 1961-2025 | ~5 MB |
| `liu_wu('daily')` | Zero yields, maturities 1..360 months | daily | 1961-2025 | ~60 MB |
| `yield_on(date, m, source)` | Scalar yield; integer fast path, Svensson closed form otherwise | n/a | — | — |
| `ns_factors(start, end, source)` | Published BETA0-3, TAU1, TAU2 (no refit) | per-date | — | — |

## Methodology notes (read once, save grief)

- **Units.** All yields in the GSW panels are **percent, continuously compounded, annualized**. `SVENY10 = 4.20` means 4.20% cc.
- **Pre-1980 GSW rows are Nelson-Siegel, not Svensson.** They have `BETA3 == 0` and `TAU2 == -999.99` (sentinel; the loader normalizes it to NaN). The Svensson closed form collapses to NS in that limit, so the same evaluator handles both eras — but be aware that `BETA3` and `TAU2` are meaningless before 1980 and `ns_factors()` will return them as 0 / NaN.
- **Update cadence.** The Fed posts updated GSW files on Tuesdays for the period ending the previous Friday. The deployment caches the CSV under `data/treasury_yields/`; delete the cached file to refresh.
- **GSW zeros ≠ FRED par yields.** `SVENY10` is the **zero**-coupon 10y, not the constant-maturity par yield (`DGS10`). They differ by ~10–30 bp depending on the slope/curvature of the curve. Use `SVENPY10` for an apples-to-apples comparison with `DGS10`.
- **Citation.** Always cite GSW 2007 (nominal) / GSW 2008 (TIPS) / Liu-Wu 2021 (Liu-Wu) when you use these.

## URL rot
- **GSW URLs are stable** (`feds200628.csv`, `feds200805.csv`) and don't rotate per release — the file is overwritten in place each Tuesday.
- **Liu-Wu lives in Google Sheets.** The sheet IDs in the helper will rotate when the authors re-share or migrate. If the loader complains it got HTML instead of CSV (rate limiting) or hits a 404, visit https://sites.google.com/view/jingcynthiawu/yield-data, grab the current sheet URL, and pass `liu_wu(freq, url='https://docs.google.com/spreadsheets/d/<ID>/export?format=csv')`.

## When to use which curve
- **GSW nominal** is the field default for U.S. zero yields — used by ~every monetary-policy and term-structure paper.
- **GSW TIPS** is the only readily-available real zero curve and the source for breakeven inflation; use it whenever the question involves real rates or inflation expectations.
- **Liu-Wu** is the standard robustness check on GSW — it uses a different fitting method (cubic splines vs. Svensson) and a slightly different bond-inclusion rule, so divergence between the two is informative when results are fragile to curve construction.
