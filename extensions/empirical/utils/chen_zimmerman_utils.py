"""Chen-Zimmerman Open Source Asset Pricing utilities.

Usage:
    from utils.chen_zimmerman_utils import get_signals, get_portfolios, list_signals

Uses the openassetpricing package. No authentication needed.
"""
import pandas as pd

_AP = None

def _get_ap():
    """Get or create OpenAP instance."""
    global _AP
    if _AP is None:
        from openassetpricing import OpenAP
        _AP = OpenAP()
    return _AP

def get_signals(predictors, signed=False, backend='pandas'):
    """Download firm-level signals.

    Args:
        predictors: list of signal names (e.g., ['BM', 'Mom12m', 'AssetGrowth'])
        signed: if True, sign signals so higher = higher expected return
        backend: 'pandas' or 'polars'

    Returns:
        DataFrame with permno, yyyymm, and signal columns
    """
    if isinstance(predictors, str):
        predictors = [predictors]
    return _get_ap().dl_signal(backend, predictors, signed=signed)

def get_portfolios(predictors, port_type='op', backend='pandas'):
    """Download portfolio returns for signals.

    Args:
        predictors: list of signal names
        port_type: portfolio construction method. Options:
            'op' — original paper methodology
            'deciles_ew' — equal-weighted deciles
            'deciles_vw' — value-weighted deciles
            'quintiles_ew' — equal-weighted quintiles
            'quintiles_vw' — value-weighted quintiles
        backend: 'pandas' or 'polars'

    Returns:
        DataFrame with signalname, port, date, ret, and other columns
    """
    if isinstance(predictors, str):
        predictors = [predictors]
    return _get_ap().dl_port(port_type, backend, predictors)

def list_portfolio_types():
    """List available portfolio construction methods."""
    return _get_ap().list_port()

def signal_doc():
    """Download signal documentation (maps signals to original papers)."""
    return _get_ap().dl_signal_doc('pandas')
