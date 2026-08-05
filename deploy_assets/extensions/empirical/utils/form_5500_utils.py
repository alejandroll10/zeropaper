"""Form 5500 utilities — DOL EBSA public-use research files (ERISA pension plans).

Form 5500 is the annual ERISA filing for every pension and welfare plan with
≥100 participants (smaller plans file Form 5500-SF, available separately).
Schedules break out detail:
  - Schedule H: financial statements (asset breakdown by category — including
    INT_REG_INVST_CO_*_AMT for mutual funds)
  - Schedule R: retirement plan info (distributions, rollovers in/out)
  - Schedule C: service provider compensation
  - Schedule A: insurance contract info
  - Schedule MB / SB: defined-benefit funding info
  - Schedule D / G / I: misc

Public-use ZIPs live at:
    https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/F_{NAME}_{year}_Latest.zip
where NAME is one of {5500, SCH_H, SCH_R, SCH_C, SCH_A, SCH_D, SCH_G, SCH_I,
SCH_MB, SCH_SB}. The "Latest" path serves the most recent revision DOL has
posted (revisions can land months after a plan-year end).

Usage:
    from utils.form_5500_utils import download_5500, download_schedule

    main22 = download_5500(2022)
    sh22   = download_schedule(2022, 'h')
    sr22   = download_schedule(2022, 'r')
    merged = main22.merge(sh22, on=['ACK_ID'], suffixes=('', '_h'))
"""
import io
import os
import time
import zipfile
import pandas as pd
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'form_5500')
# DOL serves these files from www.askebsa.dol.gov; the apex domain
# `askebsa.dol.gov` 301-redirects but emits an unescaped-space Location
# header that breaks urllib's redirect follower, so we hit www directly.
BASE_URL = "https://www.askebsa.dol.gov/FOIA%20Files/{year}/Latest/F_{name}_{year}_Latest.zip"

# Map our shorthand → URL token (the {NAME} part)
_SCHEDULE_TOKENS = {
    '5500': '5500',
    'main': '5500',
    'a': 'SCH_A',
    'c': 'SCH_C',
    'd': 'SCH_D',
    'g': 'SCH_G',
    'h': 'SCH_H',
    'i': 'SCH_I',
    'r': 'SCH_R',
    'mb': 'SCH_MB',
    'sb': 'SCH_SB',
}


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _zip_url(year, schedule):
    token = _SCHEDULE_TOKENS.get(schedule.lower())
    if token is None:
        raise ValueError(
            f"unknown schedule {schedule!r}; valid: {sorted(_SCHEDULE_TOKENS)}"
        )
    return BASE_URL.format(year=year, name=token)


def _cache_path(year, schedule, suffix):
    token = _SCHEDULE_TOKENS[schedule.lower()]
    return os.path.join(DATA_DIR, f"F_{token}_{year}_Latest.{suffix}")


def _download(year, schedule, deadline_seconds=900, chunk_stall_seconds=60,
              chunk_bytes=64 * 1024, force_refresh=False, verbose=True):
    """Download (and cache) the ZIP, return its bytes.

    Hardened against DOL's slow / occasionally-stalling CDN:
    - explicit (connect, read) timeouts via requests
    - streamed in chunks; if no chunk arrives within `chunk_stall_seconds`,
      raise rather than waiting forever
    - wall-clock `deadline_seconds` budget for the entire transfer
    - writes to a .part file and renames only on full success, so a partial
      download never gets cached
    """
    _ensure_dir()
    cache = _cache_path(year, schedule, 'zip')
    if os.path.exists(cache) and not force_refresh:
        with open(cache, 'rb') as f:
            return f.read()
    url = _zip_url(year, schedule)
    part = cache + '.part'
    if os.path.exists(part):
        os.remove(part)

    headers = {'User-Agent': 'research'}
    deadline = time.monotonic() + deadline_seconds
    last_chunk = time.monotonic()
    received = 0

    with requests.get(url, headers=headers, stream=True,
                      timeout=(10, chunk_stall_seconds), allow_redirects=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('Content-Length', 0))
        if verbose:
            mb = f"{total/1e6:.1f}MB" if total else "size?"
            print(f"[form_5500] downloading {os.path.basename(cache)} ({mb}) ...", flush=True)
        with open(part, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_bytes):
                now = time.monotonic()
                if now > deadline:
                    raise TimeoutError(
                        f"download exceeded {deadline_seconds}s budget "
                        f"({received/1e6:.1f}MB of {total/1e6:.1f}MB)"
                    )
                if not chunk:  # keep-alive
                    if now - last_chunk > chunk_stall_seconds:
                        raise TimeoutError(
                            f"no data for {chunk_stall_seconds}s "
                            f"({received/1e6:.1f}MB received)"
                        )
                    continue
                f.write(chunk)
                received += len(chunk)
                last_chunk = now

    if total and received != total:
        os.remove(part)
        raise IOError(f"size mismatch: got {received}, expected {total}")
    os.rename(part, cache)
    if verbose:
        elapsed = time.monotonic() - (deadline - deadline_seconds)
        kbs = received / 1024 / max(elapsed, 0.001)
        print(f"[form_5500]   done: {received/1e6:.1f}MB in {elapsed:.1f}s "
              f"({kbs:.0f} KB/s)", flush=True)
    with open(cache, 'rb') as f:
        return f.read()


def _read_zip_csv(zbytes):
    """Read the first CSV from a Form-5500 ZIP into a DataFrame."""
    z = zipfile.ZipFile(io.BytesIO(zbytes))
    csvs = [n for n in z.namelist() if n.lower().endswith('.csv')]
    if not csvs:
        raise ValueError(f"no CSV in zip; contents: {z.namelist()}")
    with z.open(csvs[0]) as f:
        return pd.read_csv(f, encoding='latin-1', low_memory=False)


def download_schedule(year, schedule, parquet_cache=True):
    """Download a Form 5500 main form or schedule for a given plan year.

    Args:
        year: Plan year (e.g., 2022). Public files are typically posted ~6
            months after year-end; `Latest` is a moving target until DOL
            stops revising.
        schedule: One of '5500'/'main', 'a','c','d','g','h','i','r','mb','sb'.
        parquet_cache: If True, cache as parquet for faster reload.

    Returns:
        DataFrame.
    """
    _ensure_dir()
    pq = _cache_path(year, schedule, 'parquet')
    if parquet_cache and os.path.exists(pq):
        return pd.read_parquet(pq)
    df = _read_zip_csv(_download(year, schedule))
    if parquet_cache:
        df.to_parquet(pq)
    return df


def download_5500(year, parquet_cache=True):
    """Convenience: main Form 5500 for a plan year."""
    return download_schedule(year, '5500', parquet_cache=parquet_cache)


def link_schedule(main_df, sched_df, sched_suffix='_sh'):
    """Inner-join a schedule onto the main form by ACK_ID (the canonical
    filing-level key). EIN+PN identifies the *plan*, not the *filing*; for
    panel work where you want one row per filing, ACK_ID is the right key."""
    return main_df.merge(sched_df, on='ACK_ID', how='inner', suffixes=('', sched_suffix))


# ── Asset-breakdown convenience (Schedule H) ──

# Subset of Schedule H asset columns most useful for retirement-investment
# research. Pair BOY (beginning-of-year) and EOY (end-of-year) to get flows.
SCHEDULE_H_ASSET_COLS = [
    'TOT_ASSETS_BOY_AMT', 'TOT_ASSETS_EOY_AMT',
    'INT_REG_INVST_CO_BOY_AMT', 'INT_REG_INVST_CO_EOY_AMT',  # mutual funds
    'INT_COMMON_TR_BOY_AMT', 'INT_COMMON_TR_EOY_AMT',        # CCTs
    'INT_POOL_SEP_ACCT_BOY_AMT', 'INT_POOL_SEP_ACCT_EOY_AMT',  # PSAs
    'INT_MASTER_TR_BOY_AMT', 'INT_MASTER_TR_EOY_AMT',        # master trusts
    'COMMON_STOCK_BOY_AMT', 'COMMON_STOCK_EOY_AMT',
    'EMPLR_CONTRIB_BOY_AMT', 'EMPLR_CONTRIB_EOY_AMT',
    'PARTCP_CONTRIB_BOY_AMT', 'PARTCP_CONTRIB_EOY_AMT',
    'PARTCP_LOANS_BOY_AMT', 'PARTCP_LOANS_EOY_AMT',
]


def schedule_h_asset_panel(years, schedule='h'):
    """Stack Schedule H asset breakdowns across years into one panel.

    Args:
        years: Iterable of plan years.
        schedule: Default 'h' (financial statements).

    Returns:
        DataFrame with ACK_ID, EIN, PN, year, plus the SCHEDULE_H_ASSET_COLS
        that are present in each year. Columns absent in a given year are
        filled with NaN.
    """
    frames = []
    for y in years:
        df = download_schedule(y, schedule)
        ein_col = next((c for c in ('SCH_H_EIN', 'EIN') if c in df.columns), None)
        pn_col = next((c for c in ('SCH_H_PN', 'PN') if c in df.columns), None)
        keep = ['ACK_ID']
        if ein_col:
            keep.append(ein_col)
        if pn_col:
            keep.append(pn_col)
        keep += [c for c in SCHEDULE_H_ASSET_COLS if c in df.columns]
        sub = df[keep].copy()
        sub['year'] = y
        if ein_col and ein_col != 'EIN':
            sub = sub.rename(columns={ein_col: 'EIN'})
        if pn_col and pn_col != 'PN':
            sub = sub.rename(columns={pn_col: 'PN'})
        frames.append(sub)
    return pd.concat(frames, ignore_index=True, sort=False)
