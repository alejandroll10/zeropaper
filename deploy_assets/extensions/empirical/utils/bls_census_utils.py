"""BLS / Census / SSA labor-force, demographic, and earnings panels.

Free public data, zero overlap with WRDS/CRSP. Enables shift-share / Bartik
instruments built on demographic and labor-market shifts (cohort aging,
local labor demand, retirement-channel shifters).

Usage:
    from utils.bls_census_utils import (
        bls_series, census_get, acs_county, cps_basic_monthly,
        retirement_hazard_by_cohort, ssa_period_life_table,
    )

Sources (verified live, May 2026):
  * BLS public data API v2 — POST timeseries/data/. Works WITH NO KEY
    (25 queries/day, <=10 yrs/query, <=25 series). A free BLS_API_KEY raises
    limits to 500/day, 20 yrs, 50 series and unlocks net-/pct-change calcs.
    Register: https://data.bls.gov/registrationEngine/
  * Census ACS5 + CPS basic — GET api.census.gov/data/{year}/...
    A free CENSUS_API_KEY is now REQUIRED for every request (the formerly
    keyless <500/day tier was retired — bare requests return an HTML
    "Missing Key" page, not JSON). Register:
    https://api.census.gov/data/key_signup.html
  * SSA OACT period life table — bundled, versioned public-domain data; no
    key or network required. Explicit refreshes parse and validate the live
    SSA page, which may 403 datacenter/cloud IPs.

Keys are read from .env (BLS_API_KEY, CENSUS_API_KEY) lazily, inside each
function — never at import time, so the module imports with no .env.

Caching: BLS/Census fetches are memoised to
data/bls_census/<hash>.parquet (parquet preferred; transparent CSV fallback
if pyarrow is unavailable). Pass refresh=True to bypass those caches.
ssa_period_life_table() instead reads its immutable bundled CSV by default;
refresh=True checks ssa.gov, while a custom URL retains its legacy live/cache
behavior. The unchanged default call is always offline.

Convenience limits (documented, not silently dropped):
  * retirement_hazard_by_cohort is a TRANSPARENT PROXY: the year-over-year
    drop in the BLS seasonally-adjusted 55+ labour-force participation rate
    (LNS11324230), benchmarked against prime-age 25-54 (LNS11300060). It is
    NOT a true synthetic-cohort hazard (BLS national LNS series are not
    single-year-of-age). For genuine cohort hazards build them from CPS
    microdata via cps_basic_monthly (PRTAGE x PEMLR x PWSSWGT). The default
    series map is overridable via the `series_map` argument.
"""
import hashlib
import html as html_lib
import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from io import StringIO

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

_DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "bls_census")
)
_BLS_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
_CENSUS_BASE = "https://api.census.gov/data"
_SSA_SOURCE_URL = "https://www.ssa.gov/oact/STATS/table4c6.html"
_SSA_BUNDLE_DIR = os.path.join(os.path.dirname(__file__), "ssa_oact")
_SSA_PROVENANCE_FILE = os.path.join(_SSA_BUNDLE_DIR, "provenance.json")
_SSA_CANONICAL_COLUMNS = (
    "age",
    "male_death_probability",
    "male_number_of_lives",
    "male_life_expectancy",
    "female_death_probability",
    "female_number_of_lives",
    "female_life_expectancy",
)
_SSA_LEGACY_COLUMNS = (
    ("Exact age", "Exact age"),
    ("Male", "Death probability a"),
    ("Male", "Number of lives b"),
    ("Male", "Life expectancy"),
    ("Female", "Death probability a"),
    ("Female", "Number of lives b"),
    ("Female", "Life expectancy"),
)
_BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Default age-band map for the retirement-hazard proxy (seasonally adjusted,
# both sexes, BLS LNS — Current Population Survey, national). Verified live.
_DEFAULT_LFPR_SERIES = {
    "lfpr_55plus": "LNS11324230",   # LFPR, 55 years and over
    "lfpr_25_54": "LNS11300060",    # LFPR, 25-54 years (prime-age benchmark)
    "lfpr_total": "LNS11300000",    # LFPR, 16 years and over
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


def _redact(url):
    """Strip a Census `key=...` query param so it never lands in logs/errors."""
    return re.sub(r"([?&]key=)[^&]+", r"\1***", url)


def _http_json(url, data=None, headers=None, timeout=60):
    """GET (data=None) or POST a JSON request; return parsed JSON.

    Raises RuntimeError with a readable message if the server returns an
    HTML page instead of JSON (the Census "Missing Key" failure mode).
    API keys are redacted from any URL echoed in an error.
    """
    hdrs = {"User-Agent": _BROWSER_UA, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    if data is not None:
        data = json.dumps(data).encode()
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=hdrs)
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read().decode(
            "utf-8", "replace"
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:200] if hasattr(e, "read") else ""
        raise RuntimeError(f"HTTP {e.code} from {_redact(url)}: {body}") from None
    s = raw.lstrip()
    if s[:1] not in ("{", "["):
        snippet = " ".join(s.split())[:200]
        raise RuntimeError(
            f"Non-JSON response from {_redact(url)} (likely a missing/invalid "
            f"API key or rate-limit page): {snippet!r}"
        )
    return json.loads(raw)


# ─────────────────────────── BLS ────────────────────────────────
def bls_series(series_id, start_year=None, end_year=None, key=None,
                refresh=False):
    """Fetch one or more BLS series from the public data API v2.

    Args:
        series_id: a BLS series ID string, or a list of them (e.g.
            'LNS11300000', 'CUUR0000SA0', 'CES0000000001').
        start_year, end_year: ints or year-strings. Default: last 10 calendar
            years (the keyless cap). With a key, up to 20 years per call.
        key: BLS registration key; defaults to BLS_API_KEY in .env.
        refresh: bypass the on-disk cache.

    Returns:
        tidy DataFrame [series_id, year, period, periodName, date, value],
        where `date` is a period-end Timestamp (monthly M01-M12, quarterly
        Q01-Q04, or annual A01) and `value` is float. Sorted by
        series_id, date.
    """
    ids = [series_id] if isinstance(series_id, str) else list(series_id)
    key = key if key is not None else os.getenv("BLS_API_KEY")
    if end_year is None:
        end_year = pd.Timestamp.today().year
    if start_year is None:
        start_year = int(end_year) - (19 if key else 9)

    # Cache key must be key-STABLE: the response for a closed period is
    # identical with or without a registration key (the key only raises
    # rate/range limits), so the key must not enter the hash payload.
    cache_payload = {
        "seriesid": sorted(ids),
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    base = _cache_path("bls", cache_payload)
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit

    payload = dict(cache_payload, seriesid=ids)
    if key:
        payload["registrationkey"] = key
    js = _http_json(_BLS_URL, data=payload)
    if js.get("status") != "REQUEST_SUCCEEDED":
        msg = "; ".join(js.get("message", [])) or js.get("status", "unknown")
        raise RuntimeError(f"BLS request failed: {msg}")

    rows = []
    for s in js["Results"]["series"]:
        sid = s["seriesID"]
        for d in s["data"]:
            per = d["period"]  # M01..M13, Q01..Q04, A01, S01..S02
            yr = int(d["year"])
            if per.startswith("M") and per != "M13":
                ts = pd.Timestamp(yr, int(per[1:]), 1) + pd.offsets.MonthEnd(0)
            elif per.startswith("Q") and per[1:] in ("01", "02", "03", "04"):
                ts = pd.Timestamp(yr, int(per[1:]) * 3, 1) + pd.offsets.MonthEnd(0)
            else:  # annual (A01), semi-annual, M13 -> stamp year-end
                ts = pd.Timestamp(yr, 12, 31)
            try:
                val = float(d["value"])
            except (TypeError, ValueError):
                val = float("nan")
            rows.append({
                "series_id": sid, "year": yr, "period": per,
                "periodName": d.get("periodName"), "date": ts, "value": val,
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["series_id", "date"]).reset_index(drop=True)
    return _cache_save(base, df)


# ────────────────────────── Census ──────────────────────────────
def census_get(year, dataset, variables, geo_for, geo_in=None, key=None,
                refresh=False, include_name=True):
    """Generic Census API pull. Returns a DataFrame (all-string from the API;
    numeric coercion is the caller's choice — Census uses sentinel negatives
    like -666666666 for suppressed cells).

    Args:
        year: vintage year (int).
        dataset: path under data/{year}/, e.g. 'acs/acs5' or 'cps/basic/jan'.
        variables: list of variable codes.
        geo_for: the 'for=' clause, e.g. 'county:*' or 'state:12'.
        geo_in: optional 'in=' clause, e.g. 'state:12'.
        key: Census key; defaults to CENSUS_API_KEY in .env. REQUIRED by the
            API — a clear RuntimeError is raised if absent.
        include_name: prepend the geography label var 'NAME'. True for ACS;
            must be False for CPS basic (that dataset has no 'NAME' variable
            and rejects the whole request with HTTP 400 if it is requested).
    """
    key = key if key is not None else os.getenv("CENSUS_API_KEY")
    if not key:
        raise RuntimeError(
            "CENSUS_API_KEY is required for every Census API request "
            "(the keyless tier was retired). Register a free key at "
            "https://api.census.gov/data/key_signup.html and add "
            "CENSUS_API_KEY=... to .env."
        )
    get_vars = [v for v in variables if v != "NAME"]
    if include_name:
        get_vars = ["NAME"] + get_vars
    params = {"get": ",".join(get_vars), "for": geo_for, "key": key}
    if geo_in:
        params["in"] = geo_in
    url = f"{_CENSUS_BASE}/{year}/{dataset}?" + urllib.parse.urlencode(params)

    # Cache key must be key-STABLE: never embed the real API key (params['key']
    # / the urlencoded url both contain it). Identify the request by what
    # actually varies the response: vintage, dataset, vars, geography.
    base = _cache_path("census", {
        "year": year, "dataset": dataset, "get": ",".join(get_vars),
        "for": geo_for, "in": geo_in or "",
    })
    if not refresh:
        hit = _cache_load(base)
        if hit is not None:
            return hit

    arr = _http_json(url)
    df = pd.DataFrame(arr[1:], columns=arr[0])
    return _cache_save(base, df)


def acs_county(year, variables, state="*", county="*", key=None,
                refresh=False):
    """ACS 5-year estimates by county.

    Args:
        year: ACS5 vintage (e.g. 2022 -> 2018-2022 pooled).
        variables: list of ACS variable codes. Suffix matters: '_E'=estimate
            (use this), '_M'=margin of error. E.g. 'B19013_001E' (median HH
            income), 'B01002_001E' (median age), 'B23025_004E' (employed).
            Codes: api.census.gov/data/{year}/acs/acs5/variables.html.
        state / county: 2-/3-digit FIPS strings or '*' wildcards.

    NOTE: values come back as strings. The Census jam values
    (-666666666, -999999999, -888888888, -222222222, -333333333,
    -555555555, ...) mean unavailable/NA, not data. The list is not
    exhaustive but all are < -1e8 — mask anything < -1e8 before numeric use.
    """
    geo_for = f"county:{county}"
    geo_in = f"state:{state}"
    return census_get(year, "acs/acs5", variables, geo_for, geo_in,
                       key=key, refresh=refresh)


def cps_basic_monthly(year, month, variables=None, state="*", key=None,
                       refresh=False):
    """Basic monthly CPS extract via the Census API.

    Args:
        year: survey year (int).
        month: 1-12, or a 3-letter lowercase abbreviation ('jan'...'dec').
        variables: list of CPS variable codes. Default pulls the labor-force
            core: PRTAGE (age: 0-79 individual, 80=80-84, 85=85+ since
            Apr 2004), PESEX (1=M, 2=F), PEMLR (labor-force recode:
            {1,2}=employed, {3,4}=unemployed, {5,6,7}=not in labor force),
            PEEDUCA (educ ladder 31-46; 39=HS, 43=bachelor's),
            PRPERTYP (1=child, 2=adult civilian, 3=adult armed forces),
            PWSSWGT (final person weight).
        state: 2-digit FIPS string or '*' wildcard.

    NOTE: all columns are strings; coerce. '-1' = "not in universe" for
    that variable (e.g. PEEDUCA=-1 for persons <15) — drop, don't zero.
    PWSSWGT is already in PERSONS via the API (sum ~= population); do NOT
    apply the fixed-width PUMS 4-implied-decimal /10000 scaling. Weight
    every population/rate estimate by PWSSWGT.
    """
    months = ["jan", "feb", "mar", "apr", "may", "jun",
              "jul", "aug", "sep", "oct", "nov", "dec"]
    mon = month if isinstance(month, str) else months[int(month) - 1]
    mon = mon.lower()[:3]
    if variables is None:
        variables = ["PRTAGE", "PESEX", "PEMLR", "PEEDUCA",
                     "PRPERTYP", "PWSSWGT"]
    # CPS basic has no 'NAME' variable — requesting it 400s the whole call.
    return census_get(year, f"cps/basic/{mon}", variables,
                       geo_for=f"state:{state}", key=key, refresh=refresh,
                       include_name=False)


# ───────────────────── convenience: retirement hazard ───────────
def retirement_hazard_by_cohort(start_year, end_year, series_map=None,
                                 key=None, refresh=False):
    """Transparent Bartik-shifter proxy for the retirement channel.

    Builds the year-over-year change in the BLS seasonally-adjusted 55+
    labour-force participation rate, benchmarked against prime-age (25-54).
    A *negative* d_lfpr_55plus is net retirement / labour-force exit among
    older workers — the shifter used in retirement-channel shift-share
    designs.

    THIS IS A PROXY, NOT A SYNTHETIC-COHORT HAZARD. BLS national LNS series
    are not single-year-of-age, so this cannot resolve true birth-cohort
    hazards. For those, build them from CPS microdata via
    cps_basic_monthly. Override the series via `series_map`
    (keys: lfpr_55plus, lfpr_25_54, lfpr_total).

    Returns:
        DataFrame indexed by year:
        [lfpr_55plus, lfpr_25_54, lfpr_total,
         d_lfpr_55plus, d_lfpr_25_54, exit_proxy]
        where exit_proxy = -d_lfpr_55plus (higher = more retirement).
    """
    smap = dict(_DEFAULT_LFPR_SERIES)
    if series_map:
        smap.update(series_map)
    raw = bls_series(list(smap.values()), start_year, end_year,
                     key=key, refresh=refresh)
    if raw.empty:
        return raw
    ann = raw[raw["period"].str.startswith(("A", "M13"))].copy()
    if ann.empty:  # series only monthly -> collapse to annual mean
        ann = (raw.groupby([raw["series_id"], raw["year"]])["value"]
               .mean().reset_index())
    else:
        # A01 (annual avg) and M13 (alt annual-avg label) can both appear and
        # differ by rounding — averaging them yields a third, wrong number.
        # Prefer the explicit A01 code; keep M13 only where A01 is absent.
        ann["_pref"] = ann["period"].eq("A01").astype(int)
        ann = (ann.sort_values("_pref", ascending=False)
               .drop_duplicates(["series_id", "year"], keep="first")
               .drop(columns="_pref"))
    inv = {v: k for k, v in smap.items()}
    ann["label"] = ann["series_id"].map(inv)
    wide = (ann.pivot_table(index="year", columns="label", values="value",
                            aggfunc="first").sort_index())
    for col in ("lfpr_55plus", "lfpr_25_54"):
        if col in wide.columns:
            wide[f"d_{col}"] = wide[col].diff()
    if "d_lfpr_55plus" in wide.columns:
        wide["exit_proxy"] = -wide["d_lfpr_55plus"]
    return wide.reset_index()


# ──────────────────────────── SSA ───────────────────────────────
def _sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_ssa_canonical(frame, context):
    """Validate and type the stable seven-column SSA representation."""
    if tuple(frame.columns) != _SSA_CANONICAL_COLUMNS:
        raise RuntimeError(
            f"SSA schema mismatch in {context}: expected "
            f"{list(_SSA_CANONICAL_COLUMNS)}, got {list(frame.columns)}"
        )

    out = frame.copy()
    for column in _SSA_CANONICAL_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    if out.isna().any().any():
        bad = out.columns[out.isna().any()].tolist()
        raise RuntimeError(f"SSA data in {context} has non-numeric/null fields: {bad}")
    if not all(
        out[column].map(math.isfinite).all()
        for column in _SSA_CANONICAL_COLUMNS
    ):
        raise RuntimeError(f"SSA data in {context} has non-finite numeric fields")

    for column in ("age", "male_number_of_lives", "female_number_of_lives"):
        if not out[column].mod(1).eq(0).all():
            raise RuntimeError(f"SSA data in {context} has non-integer {column}")
        out[column] = out[column].astype(int)

    expected_ages = list(range(120))
    if out["age"].tolist() != expected_ages:
        raise RuntimeError(
            f"SSA data in {context} must contain exact ages 0-119 once each"
        )
    for sex in ("male", "female"):
        probability = out[f"{sex}_death_probability"]
        lives = out[f"{sex}_number_of_lives"]
        expectancy = out[f"{sex}_life_expectancy"]
        if not probability.between(0, 1, inclusive="both").all():
            raise RuntimeError(f"SSA data in {context} has invalid {sex} probabilities")
        if (
            lives.iloc[0] != 100000
            or lives.lt(0).any()
            or not lives.diff().dropna().le(0).all()
        ):
            raise RuntimeError(
                f"SSA data in {context} has invalid {sex} survivor counts"
            )
        expected_next = (lives.iloc[:-1] * (1 - probability.iloc[:-1])).round()
        observed_next = lives.iloc[1:].reset_index(drop=True)
        expected_next = expected_next.reset_index(drop=True)
        if observed_next.sub(expected_next).abs().gt(1).any():
            raise RuntimeError(
                f"SSA data in {context} has inconsistent {sex} "
                "probability/survivor recurrence"
            )
        if not expectancy.gt(0).all():
            raise RuntimeError(
                f"SSA data in {context} has non-positive {sex} life expectancy"
            )
    return out


def _ssa_legacy_frame(canonical, provenance, bundled):
    """Preserve the pandas.read_html shape returned before the local bundle."""
    out = canonical.copy()
    out.columns = pd.MultiIndex.from_tuples(_SSA_LEGACY_COLUMNS)
    out.attrs.update({
        "source_url": provenance["source_url"],
        "table_year": provenance["table_year"],
        "trustees_report_year": provenance.get("trustees_report_year"),
        "retrieved_utc": provenance.get("retrieved_utc"),
        "bundled": bundled,
    })
    if provenance.get("csv_sha256"):
        out.attrs["csv_sha256"] = provenance["csv_sha256"]
    return out


def _load_bundled_ssa_period_table():
    try:
        with open(_SSA_PROVENANCE_FILE, encoding="utf-8") as fh:
            provenance = json.load(fh)
    except (OSError, ValueError) as exc:
        raise RuntimeError(
            f"Cannot read bundled SSA provenance {_SSA_PROVENANCE_FILE}: {exc}"
        ) from None

    required = {
        "source_url", "table_year", "csv_file", "csv_sha256", "rows",
        "age_min", "age_max", "columns",
    }
    missing = sorted(required - set(provenance))
    if missing:
        raise RuntimeError(f"Bundled SSA provenance is missing fields: {missing}")
    if provenance["source_url"] != _SSA_SOURCE_URL:
        raise RuntimeError("Bundled SSA provenance names an unexpected source URL")

    csv_name = provenance["csv_file"]
    if os.path.basename(csv_name) != csv_name:
        raise RuntimeError("Bundled SSA provenance contains an unsafe csv_file path")
    csv_path = os.path.join(_SSA_BUNDLE_DIR, csv_name)
    try:
        actual_hash = _sha256_file(csv_path)
    except OSError as exc:
        raise RuntimeError(f"Cannot read bundled SSA table {csv_path}: {exc}") from None
    if actual_hash != provenance["csv_sha256"]:
        raise RuntimeError(
            "Bundled SSA table checksum does not match provenance: "
            f"expected {provenance['csv_sha256']}, got {actual_hash}"
        )

    try:
        canonical = pd.read_csv(csv_path)
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Cannot parse bundled SSA table {csv_path}: {exc}") from None
    canonical = _validate_ssa_canonical(canonical, csv_path)
    if (
        len(canonical) != provenance["rows"]
        or canonical["age"].min() != provenance["age_min"]
        or canonical["age"].max() != provenance["age_max"]
        or list(canonical.columns) != provenance["columns"]
    ):
        raise RuntimeError("Bundled SSA table disagrees with its provenance metadata")
    return canonical, provenance


def _normalize_live_ssa_table(table, url):
    if table.shape[1] != len(_SSA_CANONICAL_COLUMNS):
        raise RuntimeError(
            f"SSA upstream schema changed at {url}: expected 7 columns, "
            f"got {table.shape[1]}"
        )
    labels = []
    for column in table.columns:
        parts = column if isinstance(column, tuple) else (column,)
        labels.append(" ".join(str(part) for part in parts).lower())
    expected_tokens = (
        ("exact age",),
        ("male", "death probability"),
        ("male", "number of lives"),
        ("male", "life expectancy"),
        ("female", "death probability"),
        ("female", "number of lives"),
        ("female", "life expectancy"),
    )
    for label, tokens in zip(labels, expected_tokens):
        if not all(token in label for token in tokens):
            raise RuntimeError(
                f"SSA upstream schema changed at {url}: unexpected headers "
                f"{[str(column) for column in table.columns]}"
            )

    canonical = table.iloc[:, :len(_SSA_CANONICAL_COLUMNS)].copy()
    canonical.columns = _SSA_CANONICAL_COLUMNS
    for column in _SSA_CANONICAL_COLUMNS:
        canonical[column] = (
            canonical[column].astype(str).str.replace(",", "", regex=False).str.strip()
        )
    numeric_age = pd.to_numeric(canonical["age"], errors="coerce")
    canonical = canonical.loc[numeric_age.notna()].copy()
    canonical["age"] = numeric_age.loc[numeric_age.notna()]
    return _validate_ssa_canonical(canonical, url)


def _ssa_live_provenance(page, url):
    text = html_lib.unescape(re.sub(r"<[^>]+>", " ", page))
    text = re.sub(r"\s+", " ", text)
    match = re.search(
        r"Period Life Table,\s*(\d{4})"
        r"(?:,\s*as used in the\s*(\d{4})\s*Trustees Report)?",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        raise RuntimeError(
            f"SSA upstream metadata changed at {url}: cannot identify table vintage"
        )
    return {
        "source_url": url,
        "table_year": int(match.group(1)),
        "trustees_report_year": int(match.group(2)) if match.group(2) else None,
    }


def ssa_period_life_table(url=_SSA_SOURCE_URL, refresh=False):
    """SSA OACT period life table (mortality / life-expectancy by exact age).

    The default call reads a checksummed, versioned CSV bundled with the
    empirical extension and never contacts the network. ``refresh=True`` is
    an explicit maintainer/operator check of the live SSA HTML page; the live
    table is schema-validated but does not overwrite the immutable bundle.
    SSA may return HTTP 403 to live refreshes from datacenter/cloud IPs.

    A custom ``url`` preserves the historical raw ``pandas.read_html`` and
    URL-keyed cache behavior; because its schema is caller-defined, it does
    not receive the default SSA table's validation or provenance attributes.
    Only the unchanged default URL with ``refresh=False`` selects the bundle.

    Returns:
        For the official default URL, a one-element list containing a
        DataFrame with the same two-level columns historically produced by
        ``pandas.read_html``. Provenance is available in ``frame.attrs``
        (source URL, table/report vintage, retrieval date, and bundle status).
        A custom URL retains the legacy behavior: its first table is cached,
        cache hits return that one table, and cache misses/refreshes return
        the complete raw ``pandas.read_html`` list.
    """
    if not refresh and url == _SSA_SOURCE_URL:
        canonical, provenance = _load_bundled_ssa_period_table()
        return [_ssa_legacy_frame(canonical, provenance, bundled=True)]

    custom_cache_base = None
    if url != _SSA_SOURCE_URL:
        custom_cache_base = _cache_path("ssa", {"url": url})
        if not refresh:
            hit = _cache_load(custom_cache_base)
            if hit is not None:
                return [hit]

    req = urllib.request.Request(
        url, headers={"User-Agent": _BROWSER_UA, "Accept": "text/html"}
    )
    try:
        page = urllib.request.urlopen(req, timeout=60).read().decode(
            "utf-8", "replace"
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                f"SSA returned HTTP 403 for {url}. ssa.gov blocks "
                "datacenter/cloud IPs (Akamai bot protection); run the "
                "explicit refresh check from an unblocked network."
            ) from None
        raise RuntimeError(f"HTTP {exc.code} fetching SSA table {url}") from None
    except OSError as exc:
        raise RuntimeError(f"Network error fetching SSA table {url}: {exc}") from None

    try:
        tables = pd.read_html(StringIO(page))
    except ValueError as exc:
        raise RuntimeError(f"No HTML tables parsed from {url}: {exc}") from None
    if not tables:
        raise RuntimeError(f"No HTML tables parsed from {url}")
    if custom_cache_base is not None:
        _cache_save(custom_cache_base, tables[0])
        return tables
    canonical = _normalize_live_ssa_table(tables[0], url)
    provenance = _ssa_live_provenance(page, url)
    return [_ssa_legacy_frame(canonical, provenance, bundled=False)]
