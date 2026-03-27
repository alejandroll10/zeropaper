"""Process raw CRSP monthly into analysis-ready datasets.

Reads from data/:
  - crsp_monthly_raw.parquet
  - ff_monthly.parquet

Saves to data/:
  - crsp_monthly.parquet       (filtered, with delisting-adjusted returns, ME, NYSE breakpoints)
  - crsp_monthly_signals.parquet  (STreversal, Price, Size signals)

Usage:
    python3 code/utils/process_crsp_monthly.py
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')

def process():
    print("[process] Loading raw CRSP monthly...")
    df = pd.read_parquet(os.path.join(DATA_DIR, 'crsp_monthly_raw.parquet'))
    df['date'] = pd.to_datetime(df['date'])

    # ── Delisting return adjustment ──
    # Following Johnson & Zhao (2007), Shumway & Warther (1999)
    # NYSE/AMEX performance-related delists: -35%
    # NASDAQ performance-related delists: -55%
    perf_delist = (df['dlstcd'] == 500) | ((df['dlstcd'] >= 520) & (df['dlstcd'] <= 584))

    df.loc[df['dlret'].isna() & perf_delist & df['exchcd'].isin([1, 2]), 'dlret'] = -0.35
    df.loc[df['dlret'].isna() & perf_delist & (df['exchcd'] == 3), 'dlret'] = -0.55
    df.loc[(df['dlret'] < -1) & df['dlret'].notna(), 'dlret'] = -1.0
    df['dlret'] = df['dlret'].fillna(0.0)

    # Adjust return for delisting
    df['ret_adj'] = (1 + df['ret']) * (1 + df['dlret']) - 1
    df.loc[df['ret'].isna() & (df['dlret'] != 0), 'ret_adj'] = df['dlret']

    # ── Market cap and date fields ──
    df['me'] = (df['prc'].abs() * df['shrout']) / 1000  # millions
    df['yyyymm'] = df['date'].dt.year * 100 + df['date'].dt.month

    # ── Lagged ME and exchange code ──
    lag = df[['permno', 'yyyymm', 'me', 'exchcd', 'shrcd', 'prc']].copy()
    lag['yyyymm'] = lag['yyyymm'] + 1
    lag.loc[lag['yyyymm'] % 100 == 13, 'yyyymm'] += 100 - 12
    lag = lag.rename(columns={'me': 'melag', 'exchcd': 'exchcd_lag', 'shrcd': 'shrcd_lag', 'prc': 'prc_lag'})
    lag['prc_lag'] = lag['prc_lag'].abs()

    df = df.merge(lag[['permno', 'yyyymm', 'melag', 'exchcd_lag', 'shrcd_lag', 'prc_lag']],
                  on=['permno', 'yyyymm'], how='left')

    # ── NYSE breakpoints (lagged) ──
    nyse_lag = df.loc[df['exchcd_lag'] == 1].groupby('yyyymm')['melag'].quantile([0.1, 0.2]).unstack()
    nyse_lag.columns = ['me_nyse10_lag', 'me_nyse20_lag']
    df = df.merge(nyse_lag, on='yyyymm', how='left')

    # ── Filter: ordinary common shares, major exchanges ──
    crsp_ret = df.loc[
        df['ret_adj'].notna() &
        df['exchcd_lag'].isin([1, 2, 3, 31, 32, 33]) &
        df['shrcd_lag'].isin([10, 11])
    ].copy()

    crsp_ret = crsp_ret.sort_values(['permno', 'yyyymm'])

    # ── Save filtered returns ──
    cols_ret = ['permno', 'date', 'yyyymm', 'ret_adj', 'prc', 'me', 'shrout',
                'melag', 'exchcd_lag', 'shrcd_lag', 'prc_lag',
                'me_nyse10_lag', 'me_nyse20_lag', 'siccd']
    path_ret = os.path.join(DATA_DIR, 'crsp_monthly.parquet')
    crsp_ret[[c for c in cols_ret if c in crsp_ret.columns]].to_parquet(path_ret)
    print(f"  Saved {path_ret} ({len(crsp_ret):,} rows)")

    # ── Signals from CRSP ──
    signals = df[['permno', 'yyyymm', 'ret', 'prc', 'me', 'siccd', 'exchcd', 'shrcd']].copy()
    signals['STreversal'] = -1 * signals['ret'].fillna(0)
    signals['Price'] = -1 * np.log(signals['prc'].abs().clip(lower=1e-8))
    signals['Size'] = -1 * np.log(signals['me'].clip(lower=1e-8))
    signals = signals.dropna(subset=['exchcd', 'shrcd'])

    path_sig = os.path.join(DATA_DIR, 'crsp_monthly_signals.parquet')
    signals.to_parquet(path_sig)
    print(f"  Saved {path_sig} ({len(signals):,} rows)")

    return crsp_ret

if __name__ == '__main__':
    process()
    print("[process] CRSP monthly processing complete.")
