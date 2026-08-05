"""Treasury zero-coupon yield-curve utilities — no WRDS, no auth.

    from utils.treasury_yields_utils import (
        gsw_nominal,    # daily nominal zero curve, 1961+
        gsw_tips,       # daily TIPS real curve + breakeven, 1999+
        liu_wu,         # Liu-Wu nominal curve, daily or monthly, 1961-2025
        yield_on,       # scalar lookup at (date, maturity, source)
        ns_factors,     # published Svensson params (BETA0-3, TAU1-2) per date
        list_datasets,
    )

Sources
-------
- GSW nominal:  Gürkaynak, Sack & Wright (2007), Fed FEDS 200628.
                CSV: https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv
                Docs: https://www.federalreserve.gov/data/nominal-yield-curve.htm
- GSW TIPS:     Gürkaynak, Sack & Wright (2008), Fed FEDS 200805.
                CSV: https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv
                Docs: https://www.federalreserve.gov/data/tips-yield-curve-and-inflation-compensation.htm
- Liu-Wu:       Liu & Wu (2021), "Reconstructing the Yield Curve", JFE 142(3), 1395-1425.
                Google Sheets at https://sites.google.com/view/jingcynthiawu/yield-data

Methodology notes
-----------------
- The Fed CSVs ship Svensson (1980+) or Nelson-Siegel (pre-1980) parameters PLUS
  the implied zero yields SVENY01..SVENY30 (TIPSY02..TIPSY20 for the TIPS file).
  Pre-1980 rows have BETA3 == 0 and TAU2 == -999.99 (sentinel); the Svensson
  closed-form collapses to NS in that limit so a single evaluator handles both.
- All yields are in PERCENT, continuously compounded annualized (Fed convention).
- Liu-Wu's site hosts Google Sheets, not flat CSVs; the export URL is fragile
  and will eventually rot the same way OSBAP's WordPress uploads do — every
  getter takes a `url=` override for that case.
"""
import io
import os
import sys
import urllib.request
import urllib.error

import numpy as np
import pandas as pd


DATASETS = {
    "gsw_nominal": {
        "url": "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv",
        "format": "fed_csv",
        "yield_prefix": "SVENY",
        "max_maturity": 30,
        "desc": "GSW nominal zero-coupon Treasury curve, daily 1961+ (Svensson 1980+, NS pre-1980).",
        "approx_size_mb": 17,
    },
    "gsw_tips": {
        "url": "https://www.federalreserve.gov/data/yield-curve-tables/feds200805.csv",
        "format": "fed_csv",
        "yield_prefix": "TIPSY",
        "max_maturity": 20,
        "desc": "GSW TIPS real zero-coupon curve + inflation compensation, daily 1999+.",
        "approx_size_mb": 15,
    },
    "liu_wu_daily": {
        "url": "https://docs.google.com/spreadsheets/d/11HsxLl_u2tBNt3FyN5iXGsIKLwxvVz7t/export?format=csv",
        "format": "gsheet",
        "desc": "Liu-Wu daily nominal zero-coupon Treasury curve, 1961-2025.",
        "approx_size_mb": 60,
    },
    "liu_wu_monthly": {
        "url": "https://docs.google.com/spreadsheets/d/1-wmStGZHLx55dSYi3gQK2vb3F8dMw_Nb/export?format=csv",
        "format": "gsheet",
        "desc": "Liu-Wu monthly nominal zero-coupon Treasury curve, 1961-2025.",
        "approx_size_mb": 5,
    },
}

DEFAULT_CACHE_DIR = "data/treasury_yields"

# Sentinel the Fed uses for the second decay parameter when the row is pre-1980
# Nelson-Siegel rather than Svensson. Always coerced to NaN at load time.
_TAU2_SENTINEL = -999.99


def list_datasets():
    """Return registry: name -> {desc, url, approx_size_mb}."""
    return {k: {"desc": v["desc"], "url": v["url"], "approx_size_mb": v["approx_size_mb"]}
            for k, v in DATASETS.items()}


def _download(url, dest_path):
    """Stream a URL to dest_path with a coarse progress line."""
    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    tmp = dest_path + f".part.{os.getpid()}"
    req = urllib.request.Request(url, headers={"User-Agent": "treasury-yields-helper/1.0"})
    try:
        with urllib.request.urlopen(req) as resp, open(tmp, "wb") as out:
            total = int(resp.headers.get("Content-Length", 0))
            read = 0
            chunk = 1 << 20
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
                f"For GSW, check https://www.federalreserve.gov/data/nominal-yield-curve.htm "
                f"or .../tips-yield-curve-and-inflation-compensation.htm. "
                f"For Liu-Wu, the Google-Sheets ID may have rotated — visit "
                f"https://sites.google.com/view/jingcynthiawu/yield-data and pass the new URL "
                f"through `url=`."
            ) from e
        raise RuntimeError(f"Network error downloading {url}: {e.reason}") from e
    os.replace(tmp, dest_path)


def _cached_path(name, url, cache_dir):
    """Resolve cache filename for (name, url) and download if absent."""
    # Liu-Wu's export URL has no .csv extension; force one for caching.
    base = os.path.basename(url.split("?")[0]) or f"{name}.csv"
    if not base.lower().endswith((".csv", ".tsv")):
        base = f"{name}.csv"
    dest = os.path.join(cache_dir, base)
    if not os.path.exists(dest):
        _download(url, dest)
    return dest


def _find_header_line(path, header_marker="Date,BETA0"):
    """Return the 0-indexed line number of the column-header row.

    The Fed CSVs prepend a variable number of caveat/legend lines before the
    real header (``Date,BETA0,...``). Liu-Wu Google-Sheets exports prepend a
    citation block then an unnamed-first-column header whose data columns are
    labeled ``" 1 m", " 2 m", ...`` — we detect that pattern when
    `header_marker == "liu_wu"`.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i > 200:  # safety: header must be in the first 200 lines
                break
            stripped = line.lstrip("﻿").strip().strip('"')
            if header_marker == "liu_wu":
                # Liu-Wu header has empty first cell + many " N m" maturity labels.
                # Require multiple matches so prose preambles mentioning "1 m" don't false-trigger.
                if stripped.startswith(",") and "1 m" in stripped and "2 m" in stripped:
                    return i
            elif stripped.startswith(header_marker):
                return i
    raise RuntimeError(
        f"could not locate header row (looking for {header_marker!r}) in {path}; "
        f"file may be corrupt or format changed"
    )


def _load_fed_csv(name, url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Load a GSW Fed CSV (nominal or TIPS) into a DataFrame indexed by date.

    Returns the full panel with parameters (BETA0..BETA3, TAU1, TAU2) plus all
    yield columns. Date is a DatetimeIndex named 'date'. Sentinels normalized:
        - TAU2 == -999.99       -> NaN  (pre-1980 NS era)
        - "NA" / blank in yields -> NaN
    """
    meta = DATASETS[name]
    if url is None:
        url = meta["url"]
    path = _cached_path(name, url, cache_dir)
    skip = _find_header_line(path, header_marker="Date,BETA0")
    df = pd.read_csv(path, skiprows=skip, na_values=["NA", "ND", ""])
    if "Date" not in df.columns:
        raise RuntimeError(f"expected 'Date' column in {path}; got {list(df.columns)[:10]}")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"]).rename(columns={"Date": "date"}).set_index("date").sort_index()
    if "TAU2" in df.columns:
        df["TAU2"] = df["TAU2"].mask(np.isclose(df["TAU2"], _TAU2_SENTINEL), np.nan)
    return df


def _load_gsheet_csv(name, url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Load a Liu-Wu Google-Sheets export into a DataFrame indexed by date.

    Liu-Wu format: 3 citation/legend lines, blank rows, then a header at ~line 9
    whose first cell is empty and whose data columns are labeled ' 1 m', ' 2 m',
    ..., ' 360 m'. Date column has no header; values are YYYYMM (monthly) or
    YYYYMMDD (daily). We rename to 'date', parse with the detected format, and
    rename maturity columns to integer strings so they're easier to index.
    """
    meta = DATASETS[name]
    if url is None:
        url = meta["url"]
    path = _cached_path(name, url, cache_dir)
    # Detect throttling / sheet-id rotation: Google can serve HTML instead of CSV.
    with open(path, "rb") as fh:
        head = fh.read(200).lstrip().lower()
    if head.startswith(b"<!doctype") or head.startswith(b"<html"):
        os.remove(path)
        raise RuntimeError(
            f"Google Sheets returned HTML (not CSV) for {url} — likely rate-limited or the "
            f"sheet ID rotated. Visit https://sites.google.com/view/jingcynthiawu/yield-data, "
            f"export the sheet manually, drop it under {cache_dir}/, or pass a fresh export URL "
            f"via url=."
        )
    skip = _find_header_line(path, header_marker="liu_wu")
    df = pd.read_csv(path, skiprows=skip, na_values=["NA", "ND", ""])
    # First column is unnamed in source — name it 'date'.
    first_col = df.columns[0]
    df = df.rename(columns={first_col: "date"})
    # Maturity columns are ' 1 m', ' 2 m', ... — strip to integer-string month labels.
    rename_map = {}
    for c in df.columns[1:]:
        cs = str(c).strip().rstrip("m").strip()
        if cs.isdigit():
            rename_map[c] = cs
    df = df.rename(columns=rename_map)
    # Date parse: monthly = YYYYMM (6 digits), daily = YYYYMMDD (8 digits).
    # Strip trailing ".0" that appears when pandas reads the integer date column as
    # float64 (happens whenever any date cell is blank and '' is in na_values, promoting
    # the column from int64 to float64 — e.g. 196106 → "196106.0", length 8 instead of 6,
    # which would fool the length-based format detector and produce all-NaT parses).
    date_str = df["date"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    plausible = date_str[date_str.str.len().isin([6, 8])].str.len()
    fmt = "%Y%m" if (not plausible.empty and plausible.mode().iloc[0] == 6) else "%Y%m%d"
    df["date"] = pd.to_datetime(date_str, format=fmt, errors="coerce")
    df = df.dropna(subset=["date"]).set_index("date").sort_index()
    return df


def gsw_nominal(url=None, cache_dir=DEFAULT_CACHE_DIR):
    """GSW nominal zero-coupon Treasury curve, daily 1961+.

    Columns: BETA0..BETA3, TAU1, TAU2, SVENY01..SVENY30 (zero, cc.),
    SVENPY01..SVENPY30 (par, ce.), SVENF01..SVENF30 (inst. fwd, cc.),
    SVEN1F01/04/09 (1y fwd at 1/4/9y, ce.). All yields in percent.
    """
    return _load_fed_csv("gsw_nominal", url=url, cache_dir=cache_dir)


def gsw_tips(url=None, cache_dir=DEFAULT_CACHE_DIR):
    """GSW TIPS real zero-coupon curve + inflation compensation, daily 1999+.

    Columns: BETA0..BETA3, TAU1, TAU2, TIPSY02..TIPSY20 (real zero, cc.),
    TIPSPY02..TIPSPY20 (real par, ce.), TIPSF02..TIPSF20 (inst. fwd, cc.),
    TIPS1F02/04/09 (1y fwd, ce.), TIPS5F5 (5y5y fwd), plus breakeven
    inflation columns. All in percent.
    """
    return _load_fed_csv("gsw_tips", url=url, cache_dir=cache_dir)


def liu_wu(freq="monthly", url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Liu-Wu nominal zero-coupon Treasury curve.

    Args:
        freq: 'monthly' (1961-2025, ~5 MB) or 'daily' (1961-2025, ~60 MB).
        url:  override the default Google-Sheets export URL (the sheet ID
              will eventually rotate).

    Returns:
        DataFrame indexed by date. Columns are zero-coupon yields at maturities
        in MONTHS — typically 1..360. Cite: Liu & Wu, JFE 2021, 142(3), 1395-1425.
    """
    if freq not in ("monthly", "daily"):
        raise ValueError(f"freq must be 'monthly' or 'daily'; got {freq!r}")
    return _load_gsheet_csv(f"liu_wu_{freq}", url=url, cache_dir=cache_dir)


def _svensson_yield(m, b0, b1, b2, b3, t1, t2):
    """Svensson (1994) zero-coupon yield, continuously compounded, in percent.

    y(m) = β0 + β1 · g(m/τ1) + β2 · h(m/τ1) + β3 · h(m/τ2)
    where g(x) = (1 - e^-x)/x and h(x) = (1 - e^-x)/x - e^-x.

    Pre-1980 GSW rows have β3 == 0 and τ2 == NaN; the β3 term is masked out
    and the formula collapses to 4-parameter Nelson-Siegel.
    """
    m = np.asarray(m, dtype=float)
    x1 = m / t1
    # Guard the x→0 limit of (1 - e^-x)/x → 1.
    with np.errstate(divide="ignore", invalid="ignore"):
        g1 = np.where(x1 == 0, 1.0, (1.0 - np.exp(-x1)) / x1)
        h1 = g1 - np.exp(-x1)
        y = b0 + b1 * g1 + b2 * h1
    if pd.notna(t2) and t2 > 0 and pd.notna(b3) and b3 != 0:
        x2 = m / t2
        with np.errstate(divide="ignore", invalid="ignore"):
            g2 = np.where(x2 == 0, 1.0, (1.0 - np.exp(-x2)) / x2)
            h2 = g2 - np.exp(-x2)
        y = y + b3 * h2
    return y


def yield_on(date, maturity_years, source="gsw_nominal", url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Zero-coupon yield (in percent) at a given date and maturity.

    Integer maturities 1..max are read directly from the SVENY/TIPSY column
    (deterministic, matches Fed published values exactly). Non-integer
    maturities are evaluated from the row's Svensson/NS parameters.

    Args:
        date: anything pd.to_datetime accepts ('2024-12-31', a Timestamp, ...).
              Returns the yield for the exact trading day. Raises KeyError if the
              date is not in the panel (weekends, holidays, future dates). This is
              intentional — silent fallback to a nearby date would mask stale-data
              bugs in event studies and monetary-policy-surprise regressions. Callers
              that genuinely want the nearest prior trading day should do:
              ``df.index.asof(pd.to_datetime(date))``.
        maturity_years: positive scalar; integer fast path for source's
              published maturities, Svensson closed form otherwise.
        source: 'gsw_nominal' or 'gsw_tips'. Liu-Wu uses a different schema
              (maturities in months, no Svensson params) — read it via liu_wu()
              and index directly.

    Returns:
        Scalar yield in percent. NaN if the parameters are missing for that row.
    """
    if source not in ("gsw_nominal", "gsw_tips"):
        raise ValueError(
            f"yield_on supports 'gsw_nominal' or 'gsw_tips'; for Liu-Wu, call "
            f"liu_wu(freq) and index the panel directly. got source={source!r}"
        )
    meta = DATASETS[source]
    df = _load_fed_csv(source, url=url, cache_dir=cache_dir)
    ts = pd.to_datetime(date)
    if ts not in df.index:
        raise KeyError(f"{ts.date()} not in {source} panel (range "
                       f"{df.index.min().date()}..{df.index.max().date()})")
    row = df.loc[ts]
    m = float(maturity_years)
    if m <= 0:
        raise ValueError(f"maturity_years must be positive; got {m}")
    # Integer fast path
    if abs(m - round(m)) < 1e-9:
        mi = int(round(m))
        col = f"{meta['yield_prefix']}{mi:02d}"
        if col in df.columns and mi <= meta["max_maturity"]:
            v = row[col]
            if pd.notna(v):
                return float(v)
            # Column exists but blank for this row — fall through to closed form
    # Closed-form evaluation
    b0, b1, b2, b3 = row.get("BETA0"), row.get("BETA1"), row.get("BETA2"), row.get("BETA3")
    t1, t2 = row.get("TAU1"), row.get("TAU2")
    if pd.isna(b0) or pd.isna(b1) or pd.isna(b2) or pd.isna(t1):
        return float("nan")
    return float(_svensson_yield(m, b0, b1, b2, b3 if pd.notna(b3) else 0.0, t1, t2))


def ns_factors(start=None, end=None, source="gsw_nominal", url=None, cache_dir=DEFAULT_CACHE_DIR):
    """Published Svensson/NS parameters per date — no refitting.

    Returns the BETA0..BETA3, TAU1, TAU2 columns the Fed already estimated.
    Convenient identification:
        BETA0  ≈ level         (long-run rate)
        BETA1  ≈ -slope        (short minus long)
        BETA2  ≈ curvature 1   (medium-maturity hump)
        BETA3  ≈ curvature 2   (Svensson's second hump; ZERO pre-1980)
        TAU2   = NaN pre-1980 (was -999.99 sentinel in source; row is NS not Svensson)

    Args:
        start, end: optional date bounds (anything pd.to_datetime accepts).
        source: 'gsw_nominal' or 'gsw_tips'.
    """
    if source not in ("gsw_nominal", "gsw_tips"):
        raise ValueError(f"source must be 'gsw_nominal' or 'gsw_tips'; got {source!r}")
    df = _load_fed_csv(source, url=url, cache_dir=cache_dir)
    cols = [c for c in ("BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2") if c in df.columns]
    out = df[cols].copy()
    if start is not None:
        out = out.loc[pd.to_datetime(start):]
    if end is not None:
        out = out.loc[:pd.to_datetime(end)]
    return out
