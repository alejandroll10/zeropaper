"""Ken French Data Library utilities.

Fetches CSV ZIPs directly from Dartmouth — no pandas-datareader dependency
(which is unmaintained and emits deprecation warnings).

Usage:
    from utils.ken_french_utils import get_factors, get_portfolios, ff3_alpha
"""
import io
import re
import zipfile
import urllib.request
import pandas as pd

BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp"

# Map our shorthand → Dartmouth ZIP filename (without _CSV.zip suffix)
DATASETS = {
    'ff3': 'F-F_Research_Data_Factors',
    'ff5': 'F-F_Research_Data_5_Factors_2x3',
    'mom': 'F-F_Momentum_Factor',
}


def _fetch_csv_zip(name):
    """Download {name}_CSV.zip from Dartmouth and return the inner CSV text."""
    url = f"{BASE_URL}/{name}_CSV.zip"
    req = urllib.request.Request(url, headers={'User-Agent': 'research'})
    with urllib.request.urlopen(req, timeout=30) as r:
        zbytes = r.read()
    with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
        # ZIPs typically contain one CSV
        inner = [n for n in z.namelist() if n.lower().endswith('.csv')][0]
        return z.read(inner).decode('latin-1')


def _parse_ff_csv(text):
    """Parse a Ken French CSV. Returns the *monthly* DataFrame.

    French CSVs have header prose, then a monthly block (YYYYMM index),
    optionally followed by an annual block (YYYY index) and footers,
    each separated by blank lines or sub-headers. We take the first block
    whose index looks like YYYYMM (6 digits).
    """
    lines = text.splitlines()
    # Find header row: first line where the leading token is empty AND the rest
    # look like column names (contain letters). French CSVs start each block
    # with a comma-prefixed header row like ",Mkt-RF,SMB,HML,RF".
    header_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(',') and any(c.isalpha() for c in stripped):
            # Confirm next non-blank line is data (starts with a digit-ish date)
            for j in range(i + 1, min(i + 5, len(lines))):
                nxt = lines[j].strip()
                if nxt and re.match(r'^\d{4,8}\b', nxt.split(',')[0]):
                    header_idx = i
                    break
            if header_idx is not None:
                break
    if header_idx is None:
        raise ValueError("Could not locate header row in French CSV")

    # Collect monthly rows (6-digit YYYYMM index) until block ends
    header = lines[header_idx]
    data_rows = [header]
    for line in lines[header_idx + 1:]:
        stripped = line.strip()
        if not stripped:
            break
        first = stripped.split(',')[0].strip()
        if not re.match(r'^\d{6}$', first):
            # Annual block (YYYY) or footer — end of monthly block
            break
        data_rows.append(line)

    csv_text = '\n'.join(data_rows)
    df = pd.read_csv(io.StringIO(csv_text), index_col=0)
    df.index = pd.to_datetime(df.index, format='%Y%m')
    df.index.name = 'date'
    df.columns = [c.strip() for c in df.columns]
    return df


def _slice(df, start, end):
    if start:
        df = df[df.index >= pd.Timestamp(start)]
    if end:
        df = df[df.index <= pd.Timestamp(end)]
    return df


def get_factors(model='ff3', start='1963-07-01', end=None):
    """Download Fama-French factor returns (decimals, not percent).

    Args:
        model: 'ff3', 'ff5', or 'mom'.
        start, end: Date filters.

    Returns:
        DataFrame indexed by month-end date. Columns vary by model:
            ff3 → Mkt-RF, SMB, HML, RF
            ff5 → Mkt-RF, SMB, HML, RMW, CMA, RF
            mom → Mom (a.k.a. UMD)
    """
    name = DATASETS.get(model, model)
    text = _fetch_csv_zip(name)
    df = _parse_ff_csv(text) / 100.0
    return _slice(df, start, end)


def get_portfolios(name, start='1963-07-01', end=None):
    """Download portfolio returns from Ken French library (decimals).

    Args:
        name: Dataset name as used by Dartmouth (e.g., '25_Portfolios_5x5',
            '6_Portfolios_2x3').
        start, end: Date filters.

    Returns:
        DataFrame indexed by month-end date.
    """
    text = _fetch_csv_zip(name)
    df = _parse_ff_csv(text) / 100.0
    return _slice(df, start, end)


def ff3_alpha(returns, start='1963-07-01'):
    """Compute FF3 alpha for a return series.

    Args:
        returns: pandas Series of *total* monthly returns (decimal). Excess
            returns are computed inside via subtracting RF from FF3.
        start: Start date for factor data.

    Returns:
        dict with alpha (monthly), alpha_t, mkt_beta, smb_beta, hml_beta,
        r_squared, n_obs.
    """
    import statsmodels.api as sm

    factors = get_factors('ff3', start=start)
    df = pd.DataFrame({'ret': returns}).join(factors, how='inner').dropna()

    y = df['ret'] - df['RF']
    X = sm.add_constant(df[['Mkt-RF', 'SMB', 'HML']])
    result = sm.OLS(y, X).fit()

    return {
        'alpha': result.params['const'],
        'alpha_t': result.tvalues['const'],
        'mkt_beta': result.params['Mkt-RF'],
        'smb_beta': result.params['SMB'],
        'hml_beta': result.params['HML'],
        'r_squared': result.rsquared,
        'n_obs': int(result.nobs),
    }
