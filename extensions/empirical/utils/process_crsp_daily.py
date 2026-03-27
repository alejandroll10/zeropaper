"""Process raw CRSP daily into analysis-ready dataset.

Reads from data/:
  - crsp_daily_raw/YYYY.parquet (or loads specified year range)
  - ff_daily.parquet

Saves to data/:
  - crsp_daily.parquet  (filtered, with ME, NYSE breakpoints, excess returns)

Usage:
    python3 code/utils/process_crsp_daily.py [start_year] [end_year]
"""
import os
import sys
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

def process(start_year=None, end_year=None):
    # Import the loader from download script
    sys.path.insert(0, os.path.dirname(__file__))
    from download_crsp_daily import load_crsp_daily

    print("[process] Loading raw CRSP daily...")
    df = load_crsp_daily(start_year, end_year)

    if len(df) == 0:
        print("  No data found. Run download_crsp_daily.py first.")
        return None

    # ── Filter: ordinary common shares, major exchanges ──
    df = df[df['exchcd'].isin([1, 2, 3, 31, 32, 33])]
    df = df[df['shrcd'].isin([10, 11])]
    df = df[df['ret'].notna()]

    # ── Market cap ──
    df['me'] = df['prc'].abs() * df['shrout']

    # ── NYSE 20th percentile breakpoint ──
    nyse = df[df['exchcd'].isin([1, 31]) & df['me'].notna()]
    bp = nyse.groupby('date')['me'].quantile(0.2).rename('me_nyse20')
    df = df.merge(bp, on='date', how='left')
    df['small_firm'] = df['me'] < df['me_nyse20']
    df.loc[df['small_firm'].isna(), 'small_firm'] = True

    # ── Merge with FF daily factors ──
    ff = pd.read_parquet(os.path.join(DATA_DIR, 'ff_daily.parquet'))
    df = df.merge(ff, on='date', how='left')

    # Daily returns in decimal (convention: daily decimal, monthly percent)
    df['exret'] = df['ret'] - df['rf']

    df = df.sort_values(['permno', 'date'])

    # ── Save ──
    cols = ['permno', 'date', 'ret', 'exret', 'prc', 'shrout', 'me',
            'exchcd', 'shrcd', 'siccd', 'small_firm',
            'mktrf', 'smb', 'hml', 'umd', 'rf']
    path = os.path.join(DATA_DIR, 'crsp_daily.parquet')
    df[[c for c in cols if c in df.columns]].to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")

    return df

if __name__ == '__main__':
    start = int(sys.argv[1]) if len(sys.argv) > 1 else None
    end = int(sys.argv[2]) if len(sys.argv) > 2 else None
    process(start, end)
    print("[process] CRSP daily processing complete.")
