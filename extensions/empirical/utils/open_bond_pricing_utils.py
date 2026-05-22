"""Open Source Bond Asset Pricing (OSBAP) utilities.

Self-contained corporate-bond data — no WRDS, no authentication. Mirrors the
chen-zimmerman helper: public download, cache locally, return a DataFrame.

    from utils.open_bond_pricing_utils import (
        get_bond_factors,   # long-short factor return series (small, ~2 MB)
        get_ml_panel,       # bond-month characteristics panel (~886 MB)
        get_ml_predictions, # ML predictions + realized returns (~200 MB)
        get_daily_trace,    # daily bond panel: returns/spreads/duration (~1.8 GB)
        list_datasets, download_osbap,
    )

Source: Dickerson, Nozawa & Robotti — https://openbondassetpricing.com
PyBondLab (portfolio sorting on top of these): pip install PyBondLab

URL ROT: OSBAP hosts each release as a date-stamped WordPress upload, so the
default URLs below go stale when a new release lands. Every getter takes a
`url=` override; if a default 404s, visit https://openbondassetpricing.com/data/
or .../machine-learning-data/ , grab the current link, and pass it through.
"""
import io
import os
import sys
import zipfile
import urllib.request
import urllib.error

import pandas as pd

# --- Dataset registry: name -> metadata. Update `url` when a release rotates. ---
# `member` is the file inside the zip to read by default (None = caller picks).
DATASETS = {
    "factors": {
        "url": "https://openbondassetpricing.com/wp-content/uploads/2024/11/Factor_Time_Series_LongShort.zip",
        "members": {
            "excess":   "ExcessLongShortVW.csv",    # value-weighted excess LS returns
            "duradj":   "DurAdjLongShortVW.csv",     # duration-adjusted LS returns
            "turnover": "TurnOverLongShortVW.csv",   # portfolio turnover
        },
        "default_member": "excess",
        "desc": "341 long-short corporate-bond factor return series, monthly from 2002-08.",
        "approx_size_mb": 2,
    },
    "ml_panel": {
        "url": "https://openbondassetpricing.com/wp-content/uploads/2024/10/OSBAP_ML_Panel_Oct_2024.zip",
        "members": {},          # discovered after extraction
        "default_member": None,
        "desc": "Bond-month panel: 341 cross-sectionally ranked bond+stock predictors, 2002-07..2022-12.",
        "approx_size_mb": 886,
    },
    "ml_predictions": {
        "url": "https://openbondassetpricing.com/wp-content/uploads/2026/04/dnr_ml_predictions.zip",
        "members": {},
        "default_member": None,
        "desc": "Machine-learning return predictions + realized bond returns (Factor Investing with Delays).",
        "approx_size_mb": 200,
    },
    "daily_trace": {
        "url": "https://openbondassetpricing.com/wp-content/uploads/2025/12/stage1_osbap_0k_volume_2025.zip",
        "members": {},
        "default_member": None,
        "desc": "Daily bond panel from cleaned Enhanced/Standard/144A TRACE: returns, credit spreads, duration, accrued interest. No volume filter.",
        "approx_size_mb": 1830,
    },
}

DEFAULT_CACHE_DIR = "data/osbap"


def list_datasets():
    """Return the dataset registry (name -> description, url, size)."""
    return {k: {"desc": v["desc"], "url": v["url"], "approx_size_mb": v["approx_size_mb"]}
            for k, v in DATASETS.items()}


def _download(url, dest_path):
    """Stream a URL to dest_path with a coarse progress line. Raises on HTTP error."""
    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    tmp = dest_path + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "osbap-helper/1.0"})
    try:
        with urllib.request.urlopen(req) as resp, open(tmp, "wb") as out:
            total = int(resp.headers.get("Content-Length", 0))
            read = 0
            chunk = 1 << 20  # 1 MB
            while True:
                buf = resp.read(chunk)
                if not buf:
                    break
                out.write(buf)
                read += len(buf)
                if total:
                    pct = 100 * read / total
                    print(f"\r  downloading {os.path.basename(dest_path)}: "
                          f"{read/1e6:,.0f}/{total/1e6:,.0f} MB ({pct:.0f}%)",
                          end="", file=sys.stderr, flush=True)
        if total:
            print(file=sys.stderr)
    except urllib.error.URLError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        if isinstance(e, urllib.error.HTTPError):
            raise RuntimeError(
                f"HTTP {e.code} for {url}\n"
                f"OSBAP URLs are date-stamped and rotate per release. Visit "
                f"https://openbondassetpricing.com/data/ (or /machine-learning-data/), "
                f"copy the current link, and pass it via url=."
            ) from e
        raise RuntimeError(f"Network error downloading {url}: {e.reason}") from e
    os.replace(tmp, dest_path)


def download_osbap(name=None, url=None, cache_dir=DEFAULT_CACHE_DIR, force=False):
    """Download (and cache) an OSBAP release zip, returning the local zip path.

    Args:
        name: registry key (see list_datasets()). Optional if url is given.
        url:  explicit download URL, overriding the registry (use when a default 404s).
        cache_dir: where the zip is stored; re-used on subsequent calls.
        force: re-download even if a cached copy exists.

    Returns:
        Path to the cached .zip file.
    """
    if url is None:
        if name not in DATASETS:
            raise ValueError(f"unknown dataset {name!r}; known: {list(DATASETS)}")
        url = DATASETS[name]["url"]
    fname = os.path.basename(url.split("?")[0]) or f"{name}.zip"
    dest = os.path.join(cache_dir, fname)
    if force or not os.path.exists(dest):
        _download(url, dest)
    return dest


def _read_member(zip_path, member=None):
    """Read a member of a cached zip into a DataFrame (csv/parquet/dta)."""
    with zipfile.ZipFile(zip_path) as z:
        tabular = [n for n in z.namelist()
                   if n.lower().endswith((".csv", ".parquet", ".dta"))
                   and not n.startswith("__MACOSX")
                   and not os.path.basename(n).startswith("._")]
        if not tabular:
            raise RuntimeError(f"no csv/parquet/dta members in {zip_path}; contents: {z.namelist()[:20]}")
        if member is None:
            member = tabular[0]
        if member not in tabular:
            raise ValueError(f"member {member!r} not found among tabular (csv/parquet/dta) "
                             f"members in zip; available tabular: {tabular}")
        data = z.read(member)
    lo = member.lower()
    if lo.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data))
    if lo.endswith(".parquet"):
        return pd.read_parquet(io.BytesIO(data))
    return pd.read_stata(io.BytesIO(data))


def get_bond_factors(weighting="excess", url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Long-short corporate-bond factor return series (monthly, ~341 factors).

    Args:
        weighting: 'excess' (VW excess LS), 'duradj' (duration-adjusted), or 'turnover'.
        url: override the default release URL (see module docstring on URL rot).
        cache_dir: download cache location.

    Returns:
        DataFrame indexed by 'date' with one column per factor's long-short return.
    """
    members = DATASETS["factors"]["members"]
    if weighting not in members:
        raise ValueError(f"weighting must be one of {list(members)}; got {weighting!r}")
    zip_path = download_osbap("factors", url=url, cache_dir=cache_dir)
    return _read_member(zip_path, members[weighting])


def get_ml_panel(member=None, url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Bond-month characteristics panel (341 ranked predictors). ~886 MB download.

    Heavy. Downloaded once and cached. Pass `member` to pick a specific file if
    the zip holds several; otherwise the first tabular member is read.
    """
    zip_path = download_osbap("ml_panel", url=url, cache_dir=cache_dir)
    return _read_member(zip_path, member)


def get_ml_predictions(member=None, url=None, cache_dir=DEFAULT_CACHE_DIR):
    """ML return predictions + realized bond returns. ~200 MB download."""
    zip_path = download_osbap("ml_predictions", url=url, cache_dir=cache_dir)
    return _read_member(zip_path, member)


def get_daily_trace(member=None, url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Daily bond panel from cleaned TRACE: returns, credit spreads, duration. ~1.8 GB download."""
    zip_path = download_osbap("daily_trace", url=url, cache_dir=cache_dir)
    return _read_member(zip_path, member)
