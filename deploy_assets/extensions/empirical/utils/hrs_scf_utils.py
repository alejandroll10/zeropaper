"""HRS / SCF household-survey panels for retirement and wealth research.

Two free household-survey sources, zero overlap with WRDS/CRSP:

  * SCF — Survey of Consumer Finances (Federal Reserve, triennial 1989-2022).
    Cross-sectional household balance sheets with IRA/401(k)/DB-pension
    wealth, net worth, and income by age/cohort. Public-use files download
    with NO key from federalreserve.gov. Each survey carries FIVE multiply-
    imputed implicates (multiple imputation for missing/disclosure-edited
    values) — handling them correctly is the #1 silent SCF error; see the
    weight note below and scf_combine_implicates().

  * HRS — Health & Retirement Study (RAND HRS Longitudinal File). The gold-
    standard individual-level panel for retirement timing, labour-force
    transitions, and Social Security claiming (biennial since 1992). (HRS
    *the survey* also covers rollover/pension-disposition events, but those
    fields are NOT in the curated Longitudinal-File stems this helper ships
    — see hrs_retirement_panel's SCOPE LIMIT.) REGISTRATION-WALLED:
    you must create an HRS account, accept the data-use agreement, and bulk-
    download the RAND HRS file once. The helper reads a user-placed extract
    from data/hrs_scf/hrs/ — manual placement is the ONLY supported path: no
    automated/authenticated download is attempted, because the HRS site
    (hrsdata.isr.umich.edu) sits behind CDN bot protection that 403s many
    datacenter/cloud IPs even with credentials. It NEVER fails silently:
    with no file it raises a RuntimeError that states the exact registration
    step and where to drop the file (documented limit, not a silent failure
    — same posture as ssa.gov in bls_census_utils).

Usage:
    from utils.hrs_scf_utils import (
        scf_summary, scf_full, scf_replicate_weights,
        scf_combine_implicates, scf_retirement_by_cohort,
        load_rand_hrs, hrs_retirement_panel,
    )

HRS scope limit (documented, not silent): the shipped RAND-stem set covers
retirement TIMING and stocks (labour-force status, self-reported
retirement, IRA/pension assets). It does NOT include IRA-ROLLOVER /
pension-disposition event variables — those live in the HRS pension and
exit modules / RAND HRS detailed pension files, not the curated
Longitudinal-File stems. For rollover analysis pass your own stems via
hrs_retirement_panel(stems=...) against a RAND file that carries them.

Caching: every fetch is memoised to data/hrs_scf/<tag>_<hash>.parquet
(parquet preferred; transparent CSV fallback if pyarrow is unavailable).
Public-use SCF files for a given year are immutable once released, so cache
hits are safe; pass refresh=True to re-pull.

SCF WEIGHT SCALING (the silent error this skill is built to prevent):
  In the SCF Summary Extract `wgt`, and the full-set `x42001`-derived
  weight, are constructed so that summing the weight over ALL FIVE
  stacked implicates returns the U.S. household population (~131.3M in
  2022). Summing over a SINGLE implicate returns ~1/5 of the population.
  Therefore:
    - Weighted means/medians/totals over the full stacked file (all 5
      implicates) using `wgt` are correct as-is. Do NOT additionally
      divide by 5.
    - Do NOT compute a population TOTAL on one implicate with `wgt` and
      expect the right number (you get 1/5).
    - For correct standard errors use Rubin's rules: compute the point
      estimate within each implicate, then combine with the between-
      implicate variance (scf_combine_implicates() does the point-estimate
      side; replicate-weight SEs need scf_replicate_weights()).
"""
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
import zipfile

import pandas as pd

# NOTE: this module intentionally does NOT import/call dotenv. It reads no
# API keys or credentials of any kind — SCF is keyless and HRS is manual-
# placement-only (no authenticated download is attempted). Keeping dotenv
# out makes that contract obvious at the imports.

_DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "hrs_scf")
)
_HRS_DIR = os.path.join(_DATA_DIR, "hrs")
_SCF_BASE = "https://www.federalreserve.gov/econres/files"
_BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# SCF is triennial; these are the released public-use survey years.
SCF_YEARS = [1989, 1992, 1995, 1998, 2001, 2004,
             2007, 2010, 2013, 2016, 2019, 2022]

# SCF Summary-Extract age class (verified vs rscfp2022). Use with by="agecl".
SCF_AGECL = {1: "<35", 2: "35-44", 3: "45-54",
             4: "55-64", 5: "65-74", 6: "75+"}

# SCF Summary-Extract retirement-account variables (verified present in
# rscfp2022). These are the headline IRA/401(k)/pension-balance fields the
# issue-#5 use case is about. Definitions follow the SCF codebook; consult it
# for exact construction. `h`-prefixed twins (e.g. hretqliq) are 0/1 "has any"
# flags. retqliq is THE quasi-liquid retirement-balance variable. NB:
# irakh and thrift are COMPONENTS of retqliq — never sum them with retqliq
# (double-counts); pick retqliq for a total, or irakh/thrift to decompose.
SCF_RETIREMENT_VARS = {
    "retqliq":   "quasi-liquid retirement: IRA/Keogh + account-type "
                 "(401k/403b/thrift/SRA) + lump-sum-expected pensions",
    "irakh":     "IRA and Keogh account balances",
    "thrift":    "account-type pension balances (401k/403b/thrift/SRA), "
                 "current + past jobs",
    "reteq":     "total retirement equity (retqliq + account-type pensions "
                 "currently in pay status / annuitized equity)",
    "penacctwd": "withdrawals taken from pension accounts",
    "ssretinc":  "Social Security + retirement income (annual flow)",
    "annuit":    "value of annuities (not retirement-account specific)",
    "futpen":    "future (not-yet-received) pension benefits",
    "currpen":   "pension income currently being received",
    "anypen":    "has any pension coverage (0/1)",
}

# RAND HRS wave -> survey year (biennial; wave 1 = 1992). The 2020 (V2)
# Longitudinal File runs through wave 15. Use to label hrs_retirement_panel.
HRS_WAVE_YEAR = {w: 1990 + 2 * w for w in range(1, 16)}  # w1=1992 ... w15=2020

# Curated RAND HRS variable stems for the retirement panel. RAND HRS naming
# is stable across versions: respondent-level vars are r{wave}{stem},
# household-level h{wave}{stem}, time-invariant ra{stem}. Override via the
# `stems` argument of hrs_retirement_panel().
_HRS_R_STEMS = {
    "agey_e": "age_years",       # age in years, end of interview
    "lbrf": "labor_force",       # labour-force status (1-7 RAND recode)
    "sayret": "self_rpt_ret",    # self-reported retirement (0/1/2/3)
    "work": "working",           # working for pay (0/1)
    "retemp": "ret_then_work",   # retired then returned to work
    "iearn": "earnings",         # individual earnings
    "ssret": "ss_retire_inc",    # Social Security retirement income
}
_HRS_H_STEMS = {
    "aira": "ira_assets",        # household IRA/Keogh assets
    "atotb": "wealth_total",     # total household wealth (incl. 2nd home)
    "itot": "income_total",      # total household income
}
_HRS_RA_STEMS = {
    "gender": "gender", "byear": "birth_year", "racem": "race",
    "educ": "education", "hispan": "hispanic",
}


# ─────────────────────────── caching ────────────────────────────
def _cache_path(tag, payload):
    os.makedirs(_DATA_DIR, exist_ok=True)
    h = hashlib.md5(
        (tag + "|" + json.dumps(payload, sort_keys=True, default=str)).encode()
    ).hexdigest()[:16]
    return os.path.join(_DATA_DIR, f"{tag}_{h}")


def _cache_load(base):
    if os.path.exists(base + ".parquet"):
        try:
            return pd.read_parquet(base + ".parquet")
        except Exception:
            pass
    if os.path.exists(base + ".csv"):
        return pd.read_csv(base + ".csv")
    return None


def _cache_save(base, df):
    try:
        df.to_parquet(base + ".parquet", index=False)
    except Exception:
        df.to_csv(base + ".csv", index=False)
    return df


def _download(url, timeout=300):
    """GET bytes with a browser UA. Raises a readable RuntimeError on HTTP
    errors (the federalreserve.gov host serves files cleanly; a 404 here
    almost always means a non-existent survey year or a typo'd file stem)."""
    req = urllib.request.Request(url, headers={"User-Agent": _BROWSER_UA})
    try:
        return urllib.request.urlopen(req, timeout=timeout).read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"HTTP {e.code} fetching {url}. For SCF this usually means the "
            f"survey year is not a triennial public-use year "
            f"(valid: {SCF_YEARS})."
        ) from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching {url}: {e.reason}") from None


def _read_only_dta_in_zip(raw):
    """Read the single .dta member of a downloaded SCF zip. The inner file
    name varies by year/product (rscfp2022.dta, p22i6.dta, p22_rw1.dta, ...),
    so select it generically rather than hardcoding."""
    zf = zipfile.ZipFile(io.BytesIO(raw))
    dtas = [n for n in zf.namelist() if n.lower().endswith(".dta")]
    if not dtas:
        raise RuntimeError(
            f"No .dta member in SCF zip (members: {zf.namelist()})."
        )
    if len(dtas) > 1:
        print(f"  [hrs_scf] SCF zip has multiple .dta members {dtas}; "
              f"reading the first ({dtas[0]}).")
    with zf.open(dtas[0]) as fh:
        return pd.read_stata(io.BytesIO(fh.read()), convert_categoricals=False)


# ─────────────────────────── SCF ────────────────────────────────
def scf_summary(year, refresh=False):
    """SCF Summary Extract Public Data (analysis-ready derived variables).

    This is the file most household-finance papers use: ~350 constructed
    variables — net worth, income, asset/debt categories, and the key
    retirement aggregates RETQLIQ (quasi-liquid retirement: IRAs + thrift/
    401(k)-type accounts), and the survey weight `wgt`.

    Args:
        year: an SCF triennial year (see SCF_YEARS). NO key required.
        refresh: bypass the on-disk cache.

    Returns:
        DataFrame with all 5 implicates STACKED (rows = households x 5).
        Key columns: `yy1` (household id), `y1` (implicate id = yy1*10+m),
        `wgt` (population weight — see the module-level WEIGHT SCALING note:
        sum over ALL 5 implicates ~= population; do not also divide by 5),
        `age`, `agecl`, `networth`, `income`, `retqliq`, ...
    """
    base = _cache_path("scf_summary", {"year": int(year)})
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit
    raw = _download(f"{_SCF_BASE}/scfp{int(year)}s.zip")
    return _cache_save(base, _read_only_dta_in_zip(raw))


def scf_full(year, replicates=False, refresh=False):
    """SCF Full Public Data Set (every survey variable, Stata).

    The full file is large (~250-290 MB uncompressed) and uses the raw
    X-coded variable names (e.g. X42001 = raw weight). Prefer scf_summary()
    unless you need a variable not in the summary extract.

    Args:
        year: an SCF triennial year (see SCF_YEARS). NO key required.
        replicates: if True, also fetch the bootstrap replicate-weight file
            and return it merged on the household id (`yy1`). The full file
            then carries the wt1b1..wt1b999 replicate-weight columns for
            replication-based standard errors.
        refresh: bypass the on-disk cache.

    Returns:
        DataFrame with all 5 implicates stacked. Household id `yy1`,
        implicate id `y1`.
    """
    base = _cache_path("scf_full", {"year": int(year), "rw": bool(replicates)})
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit
    raw = _download(f"{_SCF_BASE}/scf{int(year)}s.zip")
    df = _read_only_dta_in_zip(raw)
    if replicates:
        rw = scf_replicate_weights(year, refresh=refresh)
        key = "yy1" if ("yy1" in df.columns and "yy1" in rw.columns) else "y1"
        df = df.merge(rw, on=key, how="left", suffixes=("", "_rw"))
    return _cache_save(base, df)


def scf_replicate_weights(year, refresh=False):
    """SCF bootstrap replicate-weight file (one row per household).

    999 replicate weights (wt1b1..wt1b999) keyed by household id `yy1`/`y1`.
    Use these for design-correct standard errors (the SCF is a dual-frame
    stratified sample; naive SEs understate uncertainty).

    Args:
        year: an SCF triennial year (see SCF_YEARS). NO key required.
        refresh: bypass the on-disk cache.
    """
    base = _cache_path("scf_rw", {"year": int(year)})
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit
    raw = _download(f"{_SCF_BASE}/scf{int(year)}rw1s.zip")
    return _cache_save(base, _read_only_dta_in_zip(raw))


def scf_combine_implicates(df, value_cols, weight_col="wgt", by=None,
                           stat="mean"):
    """Multiple-imputation point estimates across the 5 SCF implicates.

    Computes the weighted statistic WITHIN each implicate, then averages
    the five implicate estimates (Rubin's rule for the point estimate).
    This is the correct way to summarise the stacked file — a single
    weighted statistic over the pooled 22,975-ish rows is NOT wrong for a
    mean/share (the weight scaling makes it numerically equal) but IS wrong
    for any nonlinear statistic (median, quantiles, inequality measures)
    because those do not commute with stacking.

    Args:
        df: a stacked SCF DataFrame (from scf_summary/scf_full).
        value_cols: column name or list of columns to summarise.
        weight_col: population weight (default 'wgt').
        by: optional grouping column(s) (e.g. 'agecl').
        stat: 'mean' or 'median'.

    Returns:
        DataFrame of the implicate-averaged statistic. The implicate id is
        derived as `y1 % 10` (SCF convention y1 = yy1*10 + implicate).
    """
    vcols = [value_cols] if isinstance(value_cols, str) else list(value_cols)
    g = df.copy()
    g["_imp"] = g["y1"].astype("int64") % 10
    grp = (["_imp"] + ([by] if isinstance(by, str) else list(by))) if by \
        else ["_imp"]

    def _wstat(block):
        w = block[weight_col].to_numpy(dtype=float)
        out = {}
        for c in vcols:
            x = block[c].to_numpy(dtype=float)
            if stat == "mean":
                out[c] = (x * w).sum() / w.sum()
            elif stat == "median":
                order = x.argsort()
                x, cw = x[order], w[order].cumsum()
                out[c] = x[(cw >= 0.5 * w.sum()).argmax()]
            else:
                raise ValueError("stat must be 'mean' or 'median'")
        return pd.Series(out)

    # Select only the columns _wstat touches before grouping. This avoids
    # needing include_groups=False (a kwarg that only exists in pandas
    # >= 2.2): weight_col and vcols are never grouping keys, so the result
    # is correct on every pandas version. (A DeprecationWarning about
    # operating on grouping columns still fires on pandas 2.2 — harmless.)
    sub = g[grp + vcols + [weight_col]]
    per_imp = (sub.groupby(grp).apply(_wstat).reset_index())
    avg_by = [c for c in per_imp.columns
              if c not in vcols and c != "_imp"]
    return (per_imp.groupby(avg_by)[vcols].mean().reset_index()
            if avg_by else per_imp[vcols].mean().to_frame().T)


def scf_retirement_by_cohort(year, vars=None, by="agecl", stat="median",
                             refresh=False):
    """Headline issue-#5 convenience: IRA/401(k)/pension balances by cohort.

    Pulls scf_summary(year) and returns the MI-correct (within-implicate
    then averaged) retirement-account balances by age class. This is the
    one-call path for "retirement wealth by cohort"; it is exactly
    scf_combine_implicates restricted to the verified retirement-variable
    set with the age-class label attached.

    Args:
        year: an SCF triennial year (see SCF_YEARS). NO key required.
        vars: subset of SCF_RETIREMENT_VARS keys (default: all present in
            the file — retqliq/irakh/thrift/reteq/...).
        by: grouping column (default 'agecl'; the returned frame adds an
            'age_band' label column from SCF_AGECL when by == 'agecl').
        stat: 'median' (default) or 'mean'. Medians/quantiles MUST be
            implicate-combined (they do not commute with stacking) — this
            helper does that for you.
        refresh: bypass the on-disk cache.

    Returns:
        DataFrame [<by>, (age_band), <retirement vars>], one row per cohort.
    """
    df = scf_summary(year, refresh=refresh)
    keys = list(vars) if vars else list(SCF_RETIREMENT_VARS)
    present = [c for c in keys if c in df.columns]
    missing = [c for c in keys if c not in df.columns]
    if missing:
        print(f"  [scf_retirement_by_cohort] not in SCF {year} summary "
              f"extract, skipped: {missing}")
    if not present:
        raise RuntimeError(
            f"No retirement variables present in SCF {year} "
            f"(looked for {keys})."
        )
    out = scf_combine_implicates(df, present, by=by, stat=stat)
    if by == "agecl":
        out.insert(1, "age_band", out["agecl"].map(SCF_AGECL))
    return out


# ─────────────────────────── HRS ────────────────────────────────
def _find_local_hrs(version):
    """Find a user-placed RAND HRS extract under data/hrs_scf/hrs/.
    Accepts .dta / .sav / .sas7bdat / .parquet / .csv. A filename
    containing the version letter (e.g. 'v2', 'Q') is preferred."""
    if not os.path.isdir(_HRS_DIR):
        return None
    exts = (".parquet", ".dta", ".sav", ".sas7bdat", ".csv")
    cands = [os.path.join(_HRS_DIR, f) for f in sorted(os.listdir(_HRS_DIR))
             if f.lower().endswith(exts)]
    if not cands:
        return None
    tagged = [c for c in cands
              if str(version).lower() in os.path.basename(c).lower()]
    return (tagged or cands)[0]


def _read_any(path):
    p = path.lower()
    if p.endswith(".parquet"):
        return pd.read_parquet(path)
    if p.endswith(".csv"):
        return pd.read_csv(path)
    if p.endswith(".dta"):
        return pd.read_stata(path, convert_categoricals=False)
    if p.endswith(".sav"):
        return pd.read_spss(path)          # needs pyreadstat
    if p.endswith(".sas7bdat"):
        return pd.read_sas(path)
    raise RuntimeError(f"Unsupported RAND HRS file type: {path}")


def load_rand_hrs(version="Q", path=None, refresh=False):
    """Load the RAND HRS Longitudinal File (the standard analysis-ready
    HRS panel: wide, one row per person, wave-suffixed variables).

    Access model (HRS is registration-walled — this is by design, not a
    helper limitation):
      1. Cached parquet  -> returned immediately.
      2. Explicit `path=` -> read that file, cache it.
      3. A file the user placed under data/hrs_scf/hrs/ -> read, cache.
      4. Otherwise -> RuntimeError stating the exact registration step.

    To enable HRS:
      * Register at https://hrsdata.isr.umich.edu (free), request the RAND
        HRS Longitudinal File, accept the data-use agreement.
      * Download the Stata/SPSS/SAS bundle, unzip it, and drop the data
        file (e.g. randhrs1992_2020v2.dta) into:
            data/hrs_scf/hrs/
      * Re-run; the helper will read and cache it.

    The HRS host (hrsdata.isr.umich.edu) is behind CDN bot protection that
    403s many datacenter/cloud IPs, so automated download is unreliable
    even with credentials — the manual-placement path is the supported one.
    This is a documented limit (same posture as ssa.gov in
    bls_census_utils), not a silent failure.

    Args:
        version: RAND HRS version tag (letter or 'vN'); used to pick among
            multiple local files and to tag the cache. Default 'Q'.
        path: explicit path to a downloaded RAND HRS data file.
        refresh: bypass the on-disk cache.
    """
    base = _cache_path("rand_hrs", {"version": str(version)})
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit
    src = path or _find_local_hrs(version)
    if src and os.path.isfile(src):
        return _cache_save(base, _read_any(src))
    raise RuntimeError(
        "RAND HRS file not found. HRS is registration-walled and cannot be "
        "fetched without an approved account. To enable it:\n"
        "  1. Register (free) at https://hrsdata.isr.umich.edu and request "
        "the RAND HRS Longitudinal File; accept the data-use agreement.\n"
        "  2. Download + unzip the Stata/SPSS/SAS bundle.\n"
        f"  3. Place the data file (e.g. randhrs1992_2020v2.dta) in:\n"
        f"       {_HRS_DIR}\n"
        "  4. Re-run load_rand_hrs(). (The HRS host 403s many cloud IPs, so "
        "automated download is unreliable even with credentials — manual "
        "placement is the supported path. Documented limit, not a silent "
        "failure.)"
    )


def hrs_retirement_panel(version="Q", stems=None, path=None, refresh=False):
    """Reshape the wide RAND HRS file to a long person x wave panel of
    retirement-relevant variables (age, labour-force status, self-reported
    retirement, return-to-work, IRA assets, total wealth, SS income, ...).

    RAND HRS stores wave-varying variables as r{wave}{stem} (respondent)
    and h{wave}{stem} (household). This detects the waves present, melts the
    curated stem set to long, and keeps time-invariant ra{stem} attributes.
    Stems with no matching column are skipped with a warning (RAND drops or
    renames a few stems across versions) — never a silent wrong column.

    SCOPE LIMIT (documented): the default stems cover retirement TIMING and
    stocks, NOT IRA-rollover / pension-disposition events (those are in the
    HRS pension/exit modules, not the Longitudinal-File curated stems). Add
    them via stems= against a RAND file that carries them.

    Args:
        version, path, refresh: passed to load_rand_hrs().
        stems: optional dict overriding the default stem -> output-name map.
            Keys 'r','h','ra' map to respondent/household/invariant dicts;
            pass any subset.

    Returns:
        Long DataFrame [hhidpn, wave, year, <renamed retirement vars>,
        <invariant attributes>], sorted by hhidpn, wave. `year` is the
        survey year from HRS_WAVE_YEAR (wave 1 = 1992, biennial).
    """
    wide = load_rand_hrs(version=version, path=path, refresh=refresh)
    cols = {c.lower(): c for c in wide.columns}
    rmap = (stems or {}).get("r", _HRS_R_STEMS)
    hmap = (stems or {}).get("h", _HRS_H_STEMS)
    ramap = (stems or {}).get("ra", _HRS_RA_STEMS)

    id_col = cols.get("hhidpn") or cols.get("hhid")
    if id_col is None:
        raise RuntimeError(
            "No hhidpn/hhid id column in the RAND HRS file — is this the "
            "RAND HRS Longitudinal File (not a raw HRS core file)?"
        )

    # Discover waves present from any r{w}{stem} column.
    waves = set()
    for w in range(1, 20):
        for pre, mp in (("r", rmap), ("h", hmap)):
            for st in mp:
                if f"{pre}{w}{st}".lower() in cols:
                    waves.add(w)
    if not waves:
        raise RuntimeError(
            "No wave-suffixed RAND HRS variables found (expected e.g. "
            "r14lbrf, h14atotb). The stem map may not match this version; "
            "pass stems=... to override."
        )

    missing, frames = set(), []
    for w in sorted(waves):
        rec = {id_col: wide[id_col], "wave": w}
        for pre, mp in (("r", rmap), ("h", hmap)):
            for st, out in mp.items():
                src = cols.get(f"{pre}{w}{st}".lower())
                if src:
                    rec[out] = wide[src]
                else:
                    missing.add(f"{pre}*{st}")
        frames.append(pd.DataFrame(rec))
    long = pd.concat(frames, ignore_index=True)
    long.insert(2, "year", long["wave"].map(HRS_WAVE_YEAR))

    inv_cols = {}
    for st, out in ramap.items():
        src = cols.get(f"ra{st}".lower())
        if src:
            inv_cols[out] = src
        else:
            missing.add(f"ra{st}")
    if inv_cols:
        inv = wide[[id_col] + list(inv_cols.values())].rename(
            columns={v: k for k, v in inv_cols.items()})
        long = long.merge(inv, on=id_col, how="left")

    if missing:
        print(f"  [hrs_retirement_panel] stems not in this RAND HRS "
              f"version, skipped: {sorted(missing)}")
    return (long.rename(columns={id_col: "hhidpn"})
            .sort_values(["hhidpn", "wave"]).reset_index(drop=True))
