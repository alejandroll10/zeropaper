"""Ken French Data Library utilities.

Usage:
    from utils.ken_french_utils import get_factors, get_portfolios, grs_test

No authentication needed.
"""
import pandas as pd
import pandas_datareader.data as web

def get_factors(model='ff3', start='1963-07-01', end=None):
    """Download Fama-French factor returns.

    Args:
        model: 'ff3', 'ff5', or 'mom'
        start: Start date
        end: End date (default: latest available)

    Returns:
        DataFrame with factor returns (in decimal, not percent)
    """
    datasets = {
        'ff3': 'F-F_Research_Data_Factors',
        'ff5': 'F-F_Research_Data_5_Factors_2x3',
        'mom': 'F-F_Momentum_Factor',
    }
    name = datasets.get(model, model)
    data = web.DataReader(name, 'famafrench', start=start, end=end)
    df = data[0]  # Monthly returns
    df = df / 100  # Convert from percent to decimal
    return df

def get_portfolios(name, start='1963-07-01', end=None):
    """Download portfolio returns from Ken French library.

    Args:
        name: Dataset name (e.g., '25_Portfolios_5x5', '6_Portfolios_2x3')
        start: Start date
        end: End date

    Returns:
        DataFrame with portfolio returns (in decimal)
    """
    data = web.DataReader(name, 'famafrench', start=start, end=end)
    df = data[0] / 100
    return df

def ff3_alpha(returns, start='1963-07-01'):
    """Compute FF3 alpha for a return series.

    Args:
        returns: pandas Series of excess returns (decimal)
        start: Start date for factor data

    Returns:
        dict with alpha, t_stat, r_squared, and factor loadings
    """
    import statsmodels.api as sm

    factors = get_factors('ff3', start=start)
    # Align dates
    df = pd.DataFrame({'ret': returns}).join(factors, how='inner')
    df = df.dropna()

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
        'n_obs': result.nobs,
    }
