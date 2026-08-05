"""Download CRSP daily stock file + FF daily factors from WRDS.

Downloads year-by-year with caching (daily file is very large).
Saves to data/:
  - crsp_daily_raw/YYYY.parquet  (one file per year, cached)
  - ff_daily.parquet             (FF3 + momentum daily factors)

Usage:
    PYTHONPATH=code python3 code/utils/download_crsp_daily.py

Uses the persistent WRDS server (wrds_client). Start the server first.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.wrds_client import wrds_query, wrds_start
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'crsp_daily_raw')

INITIAL_YEAR = 1926
CURRENT_YEAR = datetime.now().year

def download_crsp_daily():
    """Download CRSP daily stock file year-by-year with caching."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    for year in range(INITIAL_YEAR, CURRENT_YEAR + 1):
        cache_path = os.path.join(CACHE_DIR, f'{year}.parquet')

        # Use cache for past years, always re-download current year
        if os.path.exists(cache_path) and year != CURRENT_YEAR:
            print(f"  {year}: cached")
            continue

        print(f"  {year}: downloading...")
        df = wrds_query(f"""
            SELECT a.permno, a.date, a.ret, a.shrout, a.prc, a.cfacshr,
                   b.shrcd, b.exchcd, b.siccd, b.ticker, b.shrcls
            FROM crsp.dsf AS a
            LEFT JOIN crsp.dsenames AS b
              ON a.permno = b.permno
              AND b.namedt <= a.date
              AND a.date <= b.nameendt
            WHERE a.date >= '{year}-01-01'
              AND a.date <= '{year}-12-31'
        """, timeout=300)
        df['date'] = pd.to_datetime(df['date'])
        df.to_parquet(cache_path)
        print(f"    {len(df):,} rows")

    print(f"[download] CRSP daily complete ({INITIAL_YEAR}-{CURRENT_YEAR})")

def download_ff_daily():
    """Download Fama-French daily factors."""
    print("[download] FF daily factors...")
    df = wrds_query("""
        SELECT date, mktrf, smb, hml, rf, umd
        FROM ff.factors_daily
    """)
    df['date'] = pd.to_datetime(df['date'])
    path = os.path.join(DATA_DIR, 'ff_daily.parquet')
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df

def load_crsp_daily(start_year=None, end_year=None):
    """Load cached CRSP daily data for a year range.

    Args:
        start_year: first year to load (default: all)
        end_year: last year to load (default: all)

    Returns:
        pandas DataFrame
    """
    start = start_year or INITIAL_YEAR
    end = end_year or CURRENT_YEAR
    dfs = []
    for year in range(start, end + 1):
        path = os.path.join(CACHE_DIR, f'{year}.parquet')
        if os.path.exists(path):
            dfs.append(pd.read_parquet(path))
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

if __name__ == '__main__':
    wrds_start()
    download_crsp_daily()
    download_ff_daily()
    print("[download] All CRSP daily downloads complete.")
