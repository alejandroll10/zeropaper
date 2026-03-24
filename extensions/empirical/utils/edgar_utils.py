"""EDGAR utilities — configured connection and common queries.

Usage:
    from utils.edgar_utils import get_edgar, get_company, search_filings, get_xbrl_facts

All functions read SEC_EDGAR_NAME and SEC_EDGAR_EMAIL from .env.
"""
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_IDENTITY = None

def _get_identity():
    """Get SEC identity string from .env."""
    global _IDENTITY
    if _IDENTITY is None:
        name = os.getenv('SEC_EDGAR_NAME', 'Research')
        email = os.getenv('SEC_EDGAR_EMAIL', 'research@university.edu')
        _IDENTITY = f"{name} {email}"
    return _IDENTITY

def get_edgar():
    """Configure and return edgartools with identity from .env.

    Returns the edgar module, already configured.

    Usage:
        edgar = get_edgar()
        company = edgar.Company("AAPL")
    """
    import edgar
    edgar.set_identity(_get_identity())
    return edgar

def get_company(ticker):
    """Get a Company object by ticker.

    Args:
        ticker: Stock ticker (e.g., "AAPL")

    Returns:
        edgar.Company object
    """
    ed = get_edgar()
    return ed.Company(ticker)

def get_xbrl_facts(ticker, concept):
    """Get XBRL time series for a company and concept.

    Args:
        ticker: Stock ticker (e.g., "AAPL")
        concept: XBRL tag (e.g., "us-gaap:Revenues")

    Returns:
        pandas DataFrame with the time series
    """
    company = get_company(ticker)
    facts = company.get_facts()
    return facts.to_pandas(concept)

def search_filings_text(query, form="10-K", start_date=None, end_date=None):
    """Full-text search across SEC filings.

    Args:
        query: Search string (e.g., "climate risk")
        form: Filing type (default "10-K")
        start_date: Start date as "YYYY-MM-DD" (optional)
        end_date: End date as "YYYY-MM-DD" (optional)

    Returns:
        dict with 'total' count and 'filings' list
    """
    headers = {"User-Agent": _get_identity()}
    q = requests.utils.quote(f'"{query}"')
    url = f"https://efts.sec.gov/LATEST/search-index?q={q}&forms={form}"
    if start_date and end_date:
        url += f"&dateRange=custom&startdt={start_date}&enddt={end_date}"

    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    return {
        'total': data.get('hits', {}).get('total', {}).get('value', 0),
        'filings': data.get('hits', {}).get('hits', [])
    }

def get_company_facts_raw(cik):
    """Get all XBRL facts for a company via direct SEC API.

    Args:
        cik: CIK number (int or string, zero-padded to 10 digits)

    Returns:
        dict with all reported financial facts
    """
    headers = {"User-Agent": _get_identity()}
    cik_str = str(cik).zfill(10)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_str}.json"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()
