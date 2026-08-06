"""WRDS utilities — compatibility wrappers over the persistent server.

Usage:
    from utils.wrds_utils import get_wrds, query, crsp_monthly, compustat_annual, ccm_link

This module never opens a direct ``wrds.Connection``. All calls route through
wrds_client so the host-global credential-rejection latch remains authoritative
across scripts and processes.
"""
import pandas as pd

_DB = None


def _client_api():
    try:
        from .wrds_client import (wrds_query, wrds_list_tables, wrds_describe,
                                  wrds_list_libraries, wrds_get_table)
    except ImportError:
        from wrds_client import (wrds_query, wrds_list_tables, wrds_describe,
                                 wrds_list_libraries, wrds_get_table)
    return (wrds_query, wrds_list_tables, wrds_describe,
            wrds_list_libraries, wrds_get_table)


class WrdsDirectAccessDisabled(RuntimeError):
    """A legacy caller requested a DB handle that would bypass the latch."""


class _ServerConnectionProxy:
    """Small compatibility surface for older callers of get_wrds()."""

    def raw_sql(self, sql, coerce_float=True, date_cols=None, index_col=None,
                params=None, chunksize=500000, return_iter=False, dtype=None,
                dtype_backend='numpy_nullable'):
        unsupported = {
            'date_cols': date_cols,
            'index_col': index_col,
            'params': params,
            'return_iter': return_iter or None,
            'dtype': dtype,
        }
        requested = [name for name, value in unsupported.items()
                     if value is not None]
        if requested:
            raise WrdsDirectAccessDisabled(
                "get_wrds().raw_sql compatibility mode does not support "
                f"{', '.join(requested)}; use wrds_query() and transform the "
                "returned DataFrame explicitly"
            )
        # Keep the upstream call signature so ordinary legacy calls continue
        # to work. coerce_float/chunksize/dtype_backend affect transfer details
        # in wrds.Connection; the server returns the same completed DataFrame.
        return _client_api()[0](sql)

    def list_tables(self, library):
        return _client_api()[1](library)

    def describe_table(self, library, table):
        return _client_api()[2](library, table)

    def list_libraries(self):
        return _client_api()[3]()

    def get_table(self, library, table, rows=-1, obs=None, offset=0,
                  columns=None, coerce_float=True, index_col=None,
                  date_cols=None):
        return _client_api()[4](
            library, table, rows=rows, obs=obs, offset=offset,
            columns=columns, coerce_float=coerce_float,
            index_col=index_col, date_cols=date_cols)

    @property
    def engine(self):
        raise WrdsDirectAccessDisabled(
            "get_wrds().engine is unavailable: direct database handles bypass "
            "the host-global authentication latch; use wrds_query() instead"
        )

    @property
    def connection(self):
        raise WrdsDirectAccessDisabled(
            "get_wrds().connection is unavailable: use the persistent WRDS "
            "client API instead"
        )

    @property
    def insp(self):
        raise WrdsDirectAccessDisabled(
            "get_wrds().insp is unavailable: use list_tables() or "
            "describe_table() on this proxy"
        )

    def close(self):
        # The server is host-shared; one script must never close it for others.
        return None


def get_wrds():
    """Return a server-backed compatibility proxy; never connect directly."""
    global _DB
    if _DB is None:
        _DB = _ServerConnectionProxy()
    return _DB


def query(sql):
    """Run a SQL query against WRDS and return a DataFrame.

    Args:
        sql: SQL query string

    Returns:
        pandas DataFrame
    """
    return _client_api()[0](sql)

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
    """Release this process's proxy; the host-shared server remains open."""
    global _DB
    if _DB is not None:
        _DB.close()
        _DB = None
