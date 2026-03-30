"""Mutual fund utilities — download, filter, compute alphas and flows.

Usage:
    from utils.mutual_fund_utils import (
        download_fund_returns, download_fund_info, download_fund_holdings,
        filter_equity_funds, aggregate_to_portfolio,
        compute_alphas, compute_implied_flows
    )

All functions use the persistent WRDS server via wrds_client.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.wrds_client import wrds_query, wrds_start

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'mutual_funds')


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ── Download functions ──

def download_fund_returns(start='1990-01-01', end='2024-12-31'):
    """Download monthly returns, TNA, NAV for all funds.

    Returns:
        DataFrame with crsp_fundno, caldt, mret, mtna, mnav
    """
    _ensure_dir()
    path = os.path.join(DATA_DIR, 'monthly_returns.parquet')
    if os.path.exists(path):
        print(f"  Loading cached {path}")
        return pd.read_parquet(path)

    print("[download] Mutual fund monthly returns...")
    df = wrds_query(f"""
        SELECT crsp_fundno, caldt, mret, mtna, mnav
        FROM crsp_q_mutualfunds.monthly_tna_ret_nav
        WHERE caldt BETWEEN '{start}' AND '{end}'
    """)
    df['caldt'] = pd.to_datetime(df['caldt'])
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df


def download_fund_info():
    """Download fund header, style, and fees.

    Returns:
        dict with keys 'header', 'style', 'fees', 'portmap'
    """
    _ensure_dir()

    # Header
    path_hdr = os.path.join(DATA_DIR, 'fund_hdr.parquet')
    if os.path.exists(path_hdr):
        hdr = pd.read_parquet(path_hdr)
    else:
        print("[download] Fund headers...")
        hdr = wrds_query("""
            SELECT crsp_fundno, crsp_portno, crsp_cl_grp, fund_name, ticker,
                   first_offer_dt, end_dt, dead_flag, delist_cd, merge_fundno,
                   et_flag, index_fund_flag, retail_fund, inst_fund, mgmt_name
            FROM crsp_q_mutualfunds.fund_hdr
        """)
        hdr.to_parquet(path_hdr)
        print(f"  Saved {path_hdr} ({len(hdr):,} rows)")

    # Style
    path_sty = os.path.join(DATA_DIR, 'fund_style.parquet')
    if os.path.exists(path_sty):
        sty = pd.read_parquet(path_sty)
    else:
        print("[download] Fund styles...")
        sty = wrds_query("""
            SELECT crsp_fundno, begdt, enddt, crsp_obj_cd, lipper_class,
                   lipper_class_name, si_obj_cd, wbrger_obj_cd
            FROM crsp_q_mutualfunds.fund_style
        """)
        sty.to_parquet(path_sty)
        print(f"  Saved {path_sty} ({len(sty):,} rows)")

    # Fees
    path_fee = os.path.join(DATA_DIR, 'fund_fees.parquet')
    if os.path.exists(path_fee):
        fees = pd.read_parquet(path_fee)
    else:
        print("[download] Fund fees...")
        fees = wrds_query("""
            SELECT crsp_fundno, begdt, enddt, exp_ratio, mgmt_fee,
                   turn_ratio, actual_12b1, max_12b1
            FROM crsp_q_mutualfunds.fund_fees
        """)
        fees.to_parquet(path_fee)
        print(f"  Saved {path_fee} ({len(fees):,} rows)")

    # Portfolio map (fundno → portno)
    path_map = os.path.join(DATA_DIR, 'portnomap.parquet')
    if os.path.exists(path_map):
        portmap = pd.read_parquet(path_map)
    else:
        print("[download] Portfolio map...")
        portmap = wrds_query("""
            SELECT crsp_fundno, crsp_portno
            FROM crsp_q_mutualfunds.portnomap
        """)
        portmap.to_parquet(path_map)
        print(f"  Saved {path_map} ({len(portmap):,} rows)")

    return {'header': hdr, 'style': sty, 'fees': fees, 'portmap': portmap}


def download_fund_holdings(start='2000-01-01', end='2024-12-31', portnos=None):
    """Download CRSP mutual fund equity holdings.

    Args:
        start: Start date
        end: End date
        portnos: List of crsp_portno to download (None = all, very large!)

    Returns:
        DataFrame with crsp_portno, report_dt, permno, percent_tna, nbr_shares, market_val
    """
    _ensure_dir()
    where = f"WHERE report_dt BETWEEN '{start}' AND '{end}'"
    if portnos is not None:
        portno_str = ','.join(str(p) for p in portnos)
        where += f" AND crsp_portno IN ({portno_str})"

    print("[download] Fund holdings (may be large)...")
    df = wrds_query(f"""
        SELECT crsp_portno, report_dt, permno, percent_tna,
               nbr_shares, market_val, security_name, ticker
        FROM crsp_q_mutualfunds.holdings
        {where}
        AND permno IS NOT NULL
    """, timeout=600)
    df['report_dt'] = pd.to_datetime(df['report_dt'])
    path = os.path.join(DATA_DIR, 'holdings.parquet')
    df.to_parquet(path)
    print(f"  Saved {path} ({len(df):,} rows)")
    return df


# ── Filter functions ──

def filter_equity_funds(header, style):
    """Filter to domestic equity funds, excluding ETFs and index funds.

    Args:
        header: fund_hdr DataFrame
        style: fund_style DataFrame

    Returns:
        Set of crsp_fundno for domestic equity funds
    """
    # Equity objective codes
    equity_styles = style[style['crsp_obj_cd'].str.startswith('ED', na=False)]
    equity_fundnos = set(equity_styles['crsp_fundno'].dropna().astype(int))

    # Exclude ETFs and index funds from header
    active = header[
        (header['et_flag'] != 'Y') &
        (header['index_fund_flag'].isna() | (header['index_fund_flag'] == ''))
    ]
    active_fundnos = set(active['crsp_fundno'].dropna().astype(int))

    return equity_fundnos & active_fundnos


# ── Aggregation ──

def aggregate_to_portfolio(returns, portmap):
    """Aggregate share-class returns to portfolio level (TNA-weighted).

    Args:
        returns: DataFrame with crsp_fundno, caldt, mret, mtna
        portmap: DataFrame with crsp_fundno, crsp_portno

    Returns:
        DataFrame with crsp_portno, caldt, wret (TNA-weighted return), tna (total)
    """
    merged = returns.merge(portmap, on='crsp_fundno', how='inner')
    merged = merged.dropna(subset=['mret', 'mtna'])
    merged = merged[merged['mtna'] > 0]

    agg = (merged
        .assign(weighted_ret=lambda x: x['mret'] * x['mtna'])
        .groupby(['crsp_portno', 'caldt'])
        .agg(
            weighted_ret=('weighted_ret', 'sum'),
            tna=('mtna', 'sum'),
            n_classes=('crsp_fundno', 'nunique')
        )
        .reset_index()
        .assign(wret=lambda x: x['weighted_ret'] / x['tna'])
        .drop(columns=['weighted_ret'])
    )
    return agg


# ── Alpha computation ──

def compute_alphas(returns, factors=None, model='ff3', min_obs=24):
    """Compute fund-level alphas from factor model regressions.

    Args:
        returns: DataFrame with crsp_fundno (or crsp_portno), caldt, and a return column (mret or wret)
        factors: DataFrame with date and factor columns. If None, loads from data/ff_monthly.parquet.
        model: 'capm', 'ff3', or 'ff5'
        min_obs: Minimum months of data required

    Returns:
        DataFrame with fund identifier, alpha, t_alpha, r2, n_obs, and factor loadings
    """
    import statsmodels.api as sm

    # Detect identifier and return column
    if 'crsp_portno' in returns.columns:
        id_col = 'crsp_portno'
    else:
        id_col = 'crsp_fundno'

    ret_col = 'wret' if 'wret' in returns.columns else 'mret'
    date_col = 'caldt' if 'caldt' in returns.columns else 'date'

    # Load factors
    if factors is None:
        ff_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ff_monthly.parquet')
        if os.path.exists(ff_path):
            factors = pd.read_parquet(ff_path)
        else:
            from utils.ken_french_utils import get_factors
            factors = get_factors(model)
            factors = factors.reset_index()
            factors.columns = ['date'] + list(factors.columns[1:])

    # Standardize factor column names
    factor_cols = {
        'capm': ['mktrf'],
        'ff3': ['mktrf', 'smb', 'hml'],
        'ff5': ['mktrf', 'smb', 'hml', 'rmw', 'cma'],
    }
    cols = factor_cols[model]

    # Normalize factor names (handle case variations)
    factors.columns = [c.lower().replace('-', '').replace('_', '') for c in factors.columns]
    col_map = {'mktrf': 'mktrf', 'smb': 'smb', 'hml': 'hml', 'rmw': 'rmw', 'cma': 'cma', 'rf': 'rf'}

    # Merge returns with factors
    ret = returns.copy()
    ret['date'] = pd.to_datetime(ret[date_col]).dt.to_period('M')
    factors['date'] = pd.to_datetime(factors.iloc[:, 0]).dt.to_period('M')

    merged = ret.merge(factors, on='date', how='inner')

    # Compute excess returns
    if 'rf' in merged.columns:
        merged['exret'] = merged[ret_col] - merged['rf']
    else:
        merged['exret'] = merged[ret_col]

    # Run regressions per fund
    results = []
    for fund_id, group in merged.groupby(id_col):
        g = group.dropna(subset=['exret'] + cols)
        if len(g) < min_obs:
            continue

        y = g['exret']
        X = sm.add_constant(g[cols])

        try:
            reg = sm.OLS(y, X).fit()
            row = {
                id_col: fund_id,
                'alpha': reg.params['const'] * 12,  # annualized
                'alpha_monthly': reg.params['const'],
                't_alpha': reg.tvalues['const'],
                'r2': reg.rsquared,
                'n_obs': int(reg.nobs),
            }
            for c in cols:
                row[f'beta_{c}'] = reg.params[c]
            results.append(row)
        except Exception:
            continue

    return pd.DataFrame(results)


# ── Flow computation ──

def compute_implied_flows(returns):
    """Compute implied percentage flows (Sirri & Tufano 1998).

    Flow_t = (TNA_t - TNA_{t-1} * (1 + ret_t)) / TNA_{t-1}

    Args:
        returns: DataFrame with crsp_fundno, caldt, mret, mtna

    Returns:
        Same DataFrame with 'flow' column added
    """
    df = returns.sort_values(['crsp_fundno', 'caldt']).copy()
    df['tna_lag'] = df.groupby('crsp_fundno')['mtna'].shift(1)
    df['flow'] = (df['mtna'] - df['tna_lag'] * (1 + df['mret'])) / df['tna_lag']

    # Winsorize extreme flows
    df.loc[df['flow'].abs() > 5, 'flow'] = np.nan

    return df


if __name__ == '__main__':
    wrds_start()
    print("Downloading fund data...")
    returns = download_fund_returns()
    info = download_fund_info()

    # Filter to equity, exclude ETFs/index
    eq_funds = filter_equity_funds(info['header'], info['style'])
    eq_returns = returns[returns['crsp_fundno'].isin(eq_funds)]
    print(f"Equity funds: {len(eq_funds):,} share classes, {len(eq_returns):,} fund-months")

    # Aggregate to portfolio level
    port_ret = aggregate_to_portfolio(eq_returns, info['portmap'])
    print(f"Portfolios: {port_ret['crsp_portno'].nunique():,} portfolios")

    # Compute alphas
    print("Computing FF3 alphas...")
    alphas = compute_alphas(port_ret, model='ff3')
    print(f"Alphas computed for {len(alphas):,} portfolios")
    print(f"Mean alpha: {alphas['alpha'].mean():.4f}")
    print(f"Median alpha: {alphas['alpha'].median():.4f}")
    print(f"Fraction positive: {(alphas['alpha'] > 0).mean():.2%}")

    # Save
    _ensure_dir()
    alphas.to_parquet(os.path.join(DATA_DIR, 'fund_alphas_ff3.parquet'))
    print(f"Saved to data/mutual_funds/fund_alphas_ff3.parquet")
