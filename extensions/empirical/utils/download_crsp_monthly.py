"""Download CRSP monthly stock file + CCM link + FF factors from WRDS.

Saves to data/:
  - crsp_monthly_raw.parquet  (msf + msenames + delistings)
  - ccm_link.parquet          (CRSP-Compustat link table)
  - ff_monthly.parquet        (FF3 + FF5 + momentum)
  - wrds_ratios.parquet       (WRDS firm ratios, if available)

Usage:
    PYTHONPATH=code python3 code/utils/download_crsp_monthly.py

Uses the persistent WRDS server (wrds_client). Start the server first.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.wrds_client import wrds_query, wrds_start
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def download_crsp_monthly():
    """Download CRSP monthly stock file with delistings."""
    print("[download] CRSP monthly stock file...")
    df = wrds_query("""
        SELECT a.permno, a.permco, a.date, a.ret, a.retx, a.vol, a.shrout,
               a.prc, a.cfacshr, a.bidlo, a.askhi,
               b.shrcd, b.exchcd, b.siccd, b.ticker, b.shrcls,
               c.dlstcd, c.dlret
        FROM crsp.msf AS a
        LEFT JOIN crsp.msenames AS b
          ON a.permno = b.permno
          AND b.namedt <= a.date
          AND a.date <= b.nameendt
        LEFT JOIN crsp.msedelist AS c
          ON a.permno = c.permno
          AND date_trunc('month', a.date) = date_trunc('month', c.dlstdt)
    """)
    df['date'] = pd.to_datetime(df['date'])
    path = os.path.join(DATA_DIR, 'crsp_monthly_raw.parquet')
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df

def download_ccm_link():
    """Download CRSP-Compustat linking table."""
    print("[download] CCM linking table...")
    df = wrds_query("""
        SELECT a.gvkey, a.conm, a.tic, a.cusip, a.cik, a.sic, a.naics,
               b.linkprim, b.linktype, b.liid,
               b.lpermno AS permno, b.lpermco, b.linkdt, b.linkenddt
        FROM comp.names AS a
        INNER JOIN crsp.ccmxpf_lnkhist AS b
          ON a.gvkey = b.gvkey
        WHERE b.linktype IN ('LC', 'LU')
          AND b.linkprim IN ('P', 'C')
        ORDER BY a.gvkey
    """)
    df['linkdt'] = pd.to_datetime(df['linkdt'])
    df['linkenddt'] = pd.to_datetime(df['linkenddt'].fillna('2099-12-31'))
    path = os.path.join(DATA_DIR, 'ccm_link.parquet')
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df

def download_ff_monthly():
    """Download Fama-French monthly factors (3+5+momentum)."""
    print("[download] FF monthly factors...")
    ff3 = wrds_query("""
        SELECT dateff AS date, mktrf, smb, hml, umd, rf
        FROM ff.factors_monthly
    """)
    ff5 = wrds_query("""
        SELECT dateff AS date, rmw, cma
        FROM ff.fivefactors_monthly
    """)
    ff3['date'] = pd.to_datetime(ff3['date'])
    ff5['date'] = pd.to_datetime(ff5['date'])
    df = ff3.merge(ff5, on='date', how='left')
    path = os.path.join(DATA_DIR, 'ff_monthly.parquet')
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df

def download_wrds_ratios():
    """Download WRDS firm ratios (large table, may take a while)."""
    print("[download] WRDS firm ratios (this may take several minutes)...")
    try:
        df = wrds_query("""
            SELECT * FROM wrdsapps.firm_ratio_ibes_ccm
        """, timeout=600)
        path = os.path.join(DATA_DIR, 'wrds_ratios.parquet')
        df.to_parquet(path)
        print(f"  Saved {path} ({len(df):,} rows)")
        return df
    except Exception as e:
        print(f"  WRDS ratios not available: {e}")
        return None

if __name__ == '__main__':
    wrds_start()
    download_crsp_monthly()
    download_ccm_link()
    download_ff_monthly()
    download_wrds_ratios()
    print("[download] All CRSP monthly downloads complete.")
