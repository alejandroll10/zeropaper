"""WRDS utilities — single persistent connection and common queries.

Usage:
    from utils.wrds_utils import get_wrds, query, crsp_monthly, compustat_annual, ccm_link

CRITICAL: WRDS requires Duo 2FA on each new connection. This module
maintains a single connection for the entire session. Never close it
until all WRDS work is done.

All functions read WRDS_USER and WRDS_PASS from .env.
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_DB = None

def get_wrds():
    """Get or create persistent WRDS connection.

    Returns the wrds.Connection object. Reuses existing connection
    if already established (Duo 2FA only fires once).
    """
    global _DB
    if _DB is None:
        import wrds
        _DB = wrds.Connection(
            wrds_username=os.getenv('WRDS_USER'),
            wrds_password=os.getenv('WRDS_PASS')
        )
    return _DB

def query(sql):
    """Run a SQL query against WRDS and return a DataFrame.

    Args:
        sql: SQL query string

    Returns:
        pandas DataFrame
    """
    return get_wrds().raw_sql(sql)

def crsp_monthly(start='1963-07-01', end='2024-12-31', shrcd=(10, 11), exchcd=(1, 2, 3)):
    """Download CRSP monthly stock file with market cap.

    Args:
        start: Start date (default '1963-07-01')
        end: End date (default '2024-12-31')
        shrcd: Share codes to include (default ordinary common shares)
        exchcd: Exchange codes (default NYSE, AMEX, NASDAQ)

    Returns:
        DataFrame with permno, date, ret, prc, shrout, mktcap, shrcd, exchcd, siccd
    """
    shrcd_str = ','.join(str(s) for s in shrcd)
    exchcd_str = ','.join(str(e) for e in exchcd)
    return query(f"""
        SELECT a.permno, a.date, a.ret, a.prc, a.shrout,
               ABS(a.prc) * a.shrout AS mktcap,
               b.shrcd, b.exchcd, b.siccd
        FROM crsp.msf AS a
        JOIN crsp.msenames AS b
          ON a.permno = b.permno
          AND a.date BETWEEN b.namedt AND b.nameendt
        WHERE a.date BETWEEN '{start}' AND '{end}'
          AND b.shrcd IN ({shrcd_str})
          AND b.exchcd IN ({exchcd_str})
    """)

def compustat_annual(start='1963-01-01', end='2024-12-31'):
    """Download Compustat annual fundamentals.

    Args:
        start: Start date
        end: End date

    Returns:
        DataFrame with gvkey, datadate, fyear, and common accounting items
    """
    return query(f"""
        SELECT gvkey, datadate, fyear, at, sale, ni, ceq, csho, prcc_f,
               lt, dltt, che, dp, oibdp, xrd, capx, ebitda
        FROM comp.funda
        WHERE indfmt = 'INDL' AND datafmt = 'STD'
          AND popsrc = 'D' AND consol = 'C'
          AND datadate BETWEEN '{start}' AND '{end}'
    """)

def ccm_link():
    """Download CRSP-Compustat link table (valid links only).

    Returns:
        DataFrame with gvkey, permno, linkdt, linkenddt
    """
    df = query("""
        SELECT gvkey, lpermno AS permno, linkdt, linkenddt, linktype, linkprim
        FROM crsp.ccmxpf_linktable
        WHERE linktype IN ('LU', 'LC')
          AND linkprim IN ('P', 'C')
    """)
    df['linkenddt'] = pd.to_datetime(df['linkenddt'].fillna('2099-12-31'))
    df['linkdt'] = pd.to_datetime(df['linkdt'])
    return df

def market_index(start='1963-07-01', end='2024-12-31', freq='monthly'):
    """Download CRSP market index returns.

    Args:
        start: Start date
        end: End date
        freq: 'monthly' or 'daily'

    Returns:
        DataFrame with date, vwretd, ewretd, sprtrn
    """
    table = 'crsp.msi' if freq == 'monthly' else 'crsp.dsi'
    return query(f"""
        SELECT date, vwretd, ewretd, sprtrn
        FROM {table}
        WHERE date BETWEEN '{start}' AND '{end}'
    """)

def close():
    """Close WRDS connection. Call only when all WRDS work is done."""
    global _DB
    if _DB is not None:
        _DB.close()
        _DB = None
