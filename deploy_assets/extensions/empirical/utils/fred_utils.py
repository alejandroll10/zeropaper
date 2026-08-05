"""FRED utilities — configured connection and common series.

Usage:
    from utils.fred_utils import get_fred, get_series, macro_moments

Reads FRED_API_KEY from .env.
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_FRED = None

def get_fred():
    """Get or create FRED connection.

    Returns:
        fredapi.Fred object
    """
    global _FRED
    if _FRED is None:
        from fredapi import Fred
        _FRED = Fred(api_key=os.getenv('FRED_API_KEY'))
    return _FRED

def get_series(series_id, start=None, end=None):
    """Fetch a FRED series.

    Args:
        series_id: FRED series ID (e.g., 'GDP', 'FEDFUNDS')
        start: Start date (optional)
        end: End date (optional)

    Returns:
        pandas Series
    """
    kwargs = {}
    if start:
        kwargs['observation_start'] = start
    if end:
        kwargs['observation_end'] = end
    return get_fred().get_series(series_id, **kwargs)

def macro_moments(start='1947-01-01', end='2024-12-31'):
    """Compute standard macro moments used in calibration.

    Returns:
        dict with mean, std, autocorrelation for key macro series
    """
    series_ids = {
        'gdp_growth': 'A191RL1Q225SBEA',  # Real GDP growth (annualized)
        'consumption_growth': 'DPCERL1Q225SBEA',  # Real PCE growth
        'inflation': 'PCEPILFE',  # Core PCE
        'fed_funds': 'FEDFUNDS',
        'tbill_3m': 'TB3MS',
        'treasury_10y': 'GS10',
        'baa_spread': 'BAA10Y',
        'unemployment': 'UNRATE',
    }

    moments = {}
    for name, sid in series_ids.items():
        try:
            s = get_series(sid, start, end)
            moments[name] = {
                'mean': s.mean(),
                'std': s.std(),
                'autocorr': s.autocorr() if len(s) > 1 else None,
                'n_obs': len(s),
                'start': str(s.index[0].date()),
                'end': str(s.index[-1].date()),
            }
        except Exception as e:
            moments[name] = {'error': str(e)}

    return moments
