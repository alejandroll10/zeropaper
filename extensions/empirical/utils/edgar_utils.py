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

# Deployed at code/utils/, so ../../data is the project data/ dir (same
# convention as the other utils' DATA_DIR).
_EDGAR_CACHE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "edgar_cache")
)

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
    # edgartools' default local data store is ~/.edgar, which is outside the
    # sandbox writable set (PermissionError on first fetch). Point it inside
    # the repo before the import; a blank .env value counts as unset.
    if not os.environ.get('EDGAR_LOCAL_DATA_DIR'):
        os.makedirs(_EDGAR_CACHE_DIR, exist_ok=True)
        os.environ['EDGAR_LOCAL_DATA_DIR'] = _EDGAR_CACHE_DIR
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
    """Get XBRL time series for a company and concept via SEC's companyfacts API.

    Args:
        ticker: Stock ticker (e.g., "AAPL") OR a 10-digit zero-padded CIK string
        concept: XBRL tag. May be bare ("Revenues") or namespaced ("us-gaap:Revenues",
            "us-gaap/Revenues"). Searched across us-gaap, dei, ifrs-full.

    Returns:
        pandas DataFrame with one row per reported fact, columns:
        end (date), val, accn, fy, fp, form, filed, unit
    """
    # Resolve ticker → CIK
    if isinstance(ticker, str) and not ticker.isdigit():
        cik = get_company(ticker).cik
    else:
        cik = int(ticker)
    facts = get_company_facts_raw(cik)

    # Strip namespace prefix if present
    if ':' in concept:
        ns_pref, tag = concept.split(':', 1)
    elif '/' in concept:
        ns_pref, tag = concept.split('/', 1)
    else:
        ns_pref, tag = None, concept

    facts_root = facts.get('facts', {})
    namespaces = [ns_pref] if ns_pref else ['us-gaap', 'dei', 'ifrs-full']
    concept_node = None
    matched_ns = None
    for ns in namespaces:
        node = facts_root.get(ns, {}).get(tag)
        if node:
            concept_node = node
            matched_ns = ns
            break
    if concept_node is None:
        raise KeyError(f"Concept {concept!r} not found in companyfacts for CIK {cik} "
                       f"(searched {namespaces})")

    rows = []
    for unit, observations in concept_node.get('units', {}).items():
        for obs in observations:
            rows.append({
                'end': obs.get('end'),
                'val': obs.get('val'),
                'accn': obs.get('accn'),
                'fy': obs.get('fy'),
                'fp': obs.get('fp'),
                'form': obs.get('form'),
                'filed': obs.get('filed'),
                'unit': unit,
                'namespace': matched_ns,
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df['end'] = pd.to_datetime(df['end'])
        df = df.sort_values('end').reset_index(drop=True)
    return df

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
