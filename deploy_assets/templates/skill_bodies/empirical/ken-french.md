## Source
- Website: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
- No authentication required
- Updated monthly

## How to use

### Option 1: pandas-datareader (preferred)
```python
# pip install pandas-datareader
import pandas_datareader.data as web
ff3 = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start='1963')
# Returns a dict of DataFrames (monthly, annual)
ff3[0].head()  # Monthly factors: Mkt-RF, SMB, HML, RF
```

### Option 2: Direct CSV download
```python
import pandas as pd
import zipfile, io, requests

url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip'
r = requests.get(url)
z = zipfile.ZipFile(io.BytesIO(r.content))
df = pd.read_csv(z.open(z.namelist()[0]), skiprows=3)
```

## Key datasets

| Dataset | What it contains |
|---------|-----------------|
| F-F_Research_Data_Factors | Mkt-RF, SMB, HML, RF (monthly/annual) |
| F-F_Research_Data_5_Factors_2x3 | Mkt-RF, SMB, HML, RMW, CMA, RF |
| F-F_Momentum_Factor | MOM (monthly) |
| 25_Portfolios_5x5 | Size × BM sorted portfolios |
| 100_Portfolios_10x10 | Size × BM sorted portfolios |
| 6_Portfolios_2x3 | Size × BM (used to construct factors) |

Browse the website for the full list — there are 100+ datasets covering industry portfolios, sorts on various characteristics, international factors, etc.

## Data format notes
- Returns are in **percent** (not decimal). Divide by 100 for most calculations.
- Monthly data dates are YYYYMM format (e.g., 202401 = January 2024)
- CSV files have a header section — skip rows until numeric data starts
- Some files contain both monthly and annual tables separated by blank lines

## Standard operations
- Factor model estimation: regress excess returns on FF3/FF5/FF6
- GRS test: test if a set of alphas are jointly zero
- Sharpe ratios: mean/std of factor returns (annualize appropriately)
- Fama-MacBeth: cross-sectional regression using portfolio returns as test assets
- Always report sample period, whether returns are value- or equal-weighted
