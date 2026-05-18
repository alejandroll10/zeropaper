"""Bank Call Report / Y-9C utilities — FFIEC CDR + Chicago Fed BHCF + FDIC API.

Quarterly bank balance sheets and income statements WITHOUT WRDS's `bank`
library or S&P CIQ. Three free, no-WRDS sources, each with a different ID
scheme — see the "ID linking nightmare" note at the bottom of this docstring.

  1. FFIEC CDR bulk SDF (`call_report`) — the authoritative source for
     literal RCON-/RIAD-coded Call Report data (e.g. RCON2170 = total
     assets). Every FDIC-insured commercial bank, quarterly. Pulled by
     scripting the ASP.NET bulk-download form at
     https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx . That form is
     a stateful WebForms postback flow; it is the documented free path but
     it is brittle (see ``FFIEC_FORM_BRITTLENESS`` below). Keyed by
     **IDRSSD** (the bank's Fed RSSD ID).

  2. FR Y-9C BHCF flat files (`y9c`) — the canonical free FR Y-9C source
     for bank holding companies (≥$3B assets, quarterly), BHCK-/BHCP-coded
     (e.g. BHCK2170 = consolidated total assets). Keyed by **RSSD9001**
     (the BHC's RSSD ID). 1986Q1..2021Q1 are pulled live from the Chicago
     Fed; 2021Q2+ are user-placed from the NIC download (the Chicago Fed
     stopped hosting in-window data on 2021-06-15 — see `y9c` docstring).
     FDIC's API does NOT carry Y-9C (it is bank-level, not BHC-
     consolidated), so this is the only no-WRDS Y-9C path.

  3. FDIC Financial Data API (`fdic_financials`) — robust, no-key JSON,
     standardized (NOT RCON-coded) fields derived from the Call Report.
     Use this for multi-quarter `bank_panel` work and as the reliable
     fallback when the FFIEC form flow breaks. Keyed by **CERT** (FDIC
     certificate number); the CERT<->RSSD crosswalk comes from the
     /institutions endpoint (fdic_institutions / nic_link), NOT from
     /financials (which does not expose FED_RSSD).

Usage:
    from utils.call_reports_utils import (
        call_report, y9c, bank_panel,
        fdic_financials, fdic_institutions, nic_link,
        list_call_periods, RC_COMMON_VARS,
    )

    rc   = call_report('2023Q4', schedule='RC')       # RCON-coded, FFIEC
    rc23 = call_report('2023Q4', schedule='RC',
                        rssdids=[480228])              # one bank (JPMorgan)
    bhc  = y9c('2023Q4')                               # BHCK-coded, Chicago Fed
    pan  = bank_panel('2022Q1', '2023Q4',              # robust FDIC panel
                      vars=['ASSET', 'DEP', 'NETINC'])
    xwalk = nic_link(852218)                           # RSSD <-> CERT <-> name

--------------------------------------------------------------------------
THE ID LINKING NIGHTMARE (read before merging anything)
--------------------------------------------------------------------------
There is NO single bank identifier. The four you will meet:

  * RSSD ID  (a.k.a. "FED RSSD", IDRSSD, RSSD9001) — assigned by the
    Federal Reserve to every entity (banks AND holding companies) in the
    National Information Center. This is the join key the academic
    literature uses. Call Report -> column ``IDRSSD``. Y-9C -> ``RSSD9001``.
  * CERT — FDIC certificate number. The FDIC API's primary key. A bank
    has BOTH a CERT and an RSSD; a holding company has only an RSSD.
  * FDIC's "FED_RSSD" — the FDIC API's name for the bank's RSSD. This is
    the bridge: ``fdic_institutions`` returns CERT and FED_RSSD together,
    so CERT <-> RSSD is a lookup, never an algorithm.
  * SNL/CIQ key, RSSD9001 vs RSSD9999 (the as-of-date RSSD), and the
    "lead bank" vs "top holder" distinction — a BHC's RSSD is NOT its
    lead bank's RSSD. To roll banks up to their holder you need the NIC
    relationships table (`nic_link` documents the bulk path).

Rules of thumb:
  * Never assume RSSD == CERT. They are unrelated integers.
  * Bank-level analysis: key on RSSD (IDRSSD). Holding-company analysis:
    key on the BHC's RSSD9001 from Y-9C. To consolidate banks to holders
    use NIC relationships, not a name match.
  * The FDIC API is the cheapest reliable RSSD<->CERT crosswalk.
"""
import io
import os
import re
import time
import zipfile
from datetime import datetime

import pandas as pd
import requests

try:  # lxml is an empirical-extension dependency (used by sec_funds_utils)
    from lxml import html as lxml_html
except Exception:  # pragma: no cover - degrade to regex-only form scraping
    lxml_html = None

DATA_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "call_reports")
)

FFIEC_BULK_URL = "https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx"
# Chicago Fed BHCF (FR Y-9C) flat files: a plain COMMA-delimited .csv at
# {yymm} = 2-digit-year + 2-digit-month of the quarter end (e.g. 2012 =
# Dec 2020). The first column is RSSD9001.
#
# DOCUMENTED CUTOFF: per the Chicago Fed "Notice of Change in Data
# Availability" (effective 2021-06-15) the Chicago Fed no longer hosts the
# datasets inside the active revision/retention window. Files exist here
# for 1986Q1 .. 2021Q1 only; 2021Q2 onward must come from the NIC
# Financial Data Download (see NIC_DATADOWNLOAD_URL / y9c() docstring).
BHCF_URL = (
    "https://www.chicagofed.org/~/media/others/banking/"
    "financial-institution-reports/bhc-data/bhcf{yymm}.csv"
)
BHCF_LAST_YEAR, BHCF_LAST_QTR = 2021, 1  # last quarter Chicago Fed hosts
# Current FR Y-9C bulk (2021Q2+): the NIC Financial Data Download. It is an
# Angular SPA behind Akamai bot protection that 403s datacenter/cloud IPs,
# so y9c() cannot pull it programmatically from a server; it documents the
# manual path and reads a user-placed file instead (same pattern as the
# hrs-scf registration wall).
NIC_DATADOWNLOAD_URL = "https://www.ffiec.gov/npw/FinancialReport/DataDownload"
FDIC_API = "https://banks.data.fdic.gov/api"

_UA = {"User-Agent": "academic-research (call-reports skill)"}

# The FFIEC bulk page is ASP.NET WebForms: a GET seeds __VIEWSTATE /
# __EVENTVALIDATION, selecting the product list posts back to populate the
# reporting-period dropdown, and the final post (download button + TSV
# format radio) streams a ZIP. Any of the control names below changing on
# FFIEC's side breaks the flow; we fail LOUD with this string so the caller
# knows to (a) check the page manually or (b) fall back to fdic_financials.
FFIEC_FORM_BRITTLENESS = (
    "FFIEC CDR bulk-download form flow failed. This ASP.NET form "
    "(https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx) is the "
    "documented free path for literal RCON-coded Call Reports but its "
    "control names are not a stable API. For robust multi-quarter panels "
    "use fdic_financials()/bank_panel(source='fdic') (standardized fields, "
    "no RCON codes); for Y-9C use y9c() (Chicago Fed BHCF). To repair this "
    "path, open the page in a browser, inspect the product <select>, the "
    "reporting-period <select>, the format radio, and the download button, "
    "and update the *_CTL constants in call_reports_utils.py."
)

# ASP.NET control identifiers. The live form namespaces every control with
# a "ctl00$MainContentHolder$..." prefix, so we resolve each control by the
# *suffix* of its name attribute (robust to ASP.NET re-parenting) rather
# than hard-coding the full name. These are the suffixes / values verified
# live (Dec 2023 .. Mar 2026 periods) against the FFIEC bulk page.
_PRODUCT_CTL = "ListBox1"                       # product <select> suffix
_PRODUCT_LABEL = "Call Reports -- Single Period"  # option visible text
_PRODUCT_VALUE = "ReportingSeriesSinglePeriod"  # option value (label fallback)
_DATES_CTL = "DatesDropDownList"                # reporting-period <select>
_DOWNLOAD_CTL = "Download_0"                    # download submit button
_FORMAT_CTL = "FormatType"                      # format radio group suffix
_FORMAT_TSV_VALUE = "TSVRadioButton"            # vs "XBRLRadiobutton"

# A practical subset of RCON/RIAD MDRM codes for the banking channel.
RC_COMMON_VARS = {
    "RCON2170": "Total assets",
    "RCON2200": "Total deposits (domestic offices)",
    "RCON2122": "Total loans and leases, net of unearned income",
    "RCON3210": "Total equity capital",
    "RCONB528": "Total loans and leases held for investment",
    "RCON3123": "Allowance for loan and lease losses",
    "RCON2948": "Total liabilities",
    "RIAD4340": "Net income (year-to-date)",
    "RIAD4107": "Total interest income (YTD)",
    "RIAD4073": "Total interest expense (YTD)",
    "RIAD4079": "Total noninterest income (YTD)",
    "RCFD2170": "Total assets (consolidated, FFIEC 031 filers)",
}


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ── quarter parsing ──

def parse_quarter(q):
    """Normalize a quarter spec to (year, qtr, period_end_date, MM/DD/YYYY).

    Accepts '2023Q4', '2023q4', '2023-Q4', 'Q4 2023', 'YYYYMMDD',
    'MM/DD/YYYY', a (year, qtr) tuple, or a datetime/date.
    """
    if isinstance(q, (tuple, list)) and len(q) == 2:
        year, qtr = int(q[0]), int(q[1])
    elif isinstance(q, datetime):
        year, qtr = q.year, (q.month - 1) // 3 + 1
    else:
        s = str(q).strip().upper().replace("-", "").replace(" ", "")
        m = re.match(r"^(\d{4})Q([1-4])$", s) or re.match(r"^Q([1-4])(\d{4})$", s)
        if m:
            if s.startswith("Q"):
                qtr, year = int(m.group(1)), int(m.group(2))
            else:
                year, qtr = int(m.group(1)), int(m.group(2))
        elif re.match(r"^\d{8}$", s):  # YYYYMMDD
            d = datetime.strptime(s, "%Y%m%d")
            year, qtr = d.year, (d.month - 1) // 3 + 1
        elif re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", str(q).strip()):
            d = datetime.strptime(str(q).strip(), "%m/%d/%Y")
            year, qtr = d.year, (d.month - 1) // 3 + 1
        else:
            raise ValueError(
                f"unrecognized quarter spec {q!r}; use e.g. '2023Q4' or "
                f"'12/31/2023' or (2023, 4)"
            )
    if qtr not in (1, 2, 3, 4):
        raise ValueError(f"quarter must be 1-4, got {qtr}")
    end = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}[qtr]
    pe = datetime(year, end[0], end[1])
    return year, qtr, pe, pe.strftime("%m/%d/%Y")


def _quarter_range(start, end):
    y0, q0, _, _ = parse_quarter(start)
    y1, q1, _, _ = parse_quarter(end)
    a, b = y0 * 4 + (q0 - 1), y1 * 4 + (q1 - 1)
    if a > b:
        raise ValueError(f"start {start} is after end {end}")
    return [(i // 4, i % 4 + 1) for i in range(a, b + 1)]


# ── FFIEC CDR bulk SDF (true RCON-coded Call Reports) ──

def _scrape_aspnet_state(html_text):
    """Pull the postback-relevant <input>/<select> name->value pairs out of
    an ASP.NET form so we can echo the WebForms state on the next post.

    Submit/image/button inputs are deliberately EXCLUDED — echoing the
    page's Cancel/Download-Taxonomy buttons would fire the wrong command;
    the caller adds back exactly the one submit it wants to click.
    """
    if lxml_html is None:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS + " [lxml is required for the FFIEC bulk "
            "path; it ships with the empirical extension]"
        )
    doc = lxml_html.fromstring(html_text)
    fields = {}
    for inp in doc.xpath("//input"):
        name = inp.get("name")
        if not name:
            continue
        itype = (inp.get("type") or "text").lower()
        if itype in ("submit", "image", "button", "reset"):
            continue
        if itype in ("checkbox", "radio") and inp.get("checked") is None:
            continue
        fields[name] = inp.get("value", "")
    for sel in doc.xpath("//select"):
        name = sel.get("name")
        if not name:
            continue
        opts = sel.xpath(".//option")
        chosen = [o for o in opts if o.get("selected") is not None]
        if chosen:
            fields[name] = chosen[0].get("value", "")
        elif opts:
            fields[name] = opts[0].get("value", "")
    for ta in doc.xpath("//textarea"):
        if ta.get("name"):
            fields[ta.get("name")] = ta.text or ""
    return fields, doc


def _resolve_ctl(doc, suffix):
    """Resolve the full ASP.NET control name whose name attribute equals
    `suffix` or ends with `$suffix` / `_suffix` (the live form prefixes
    every control with ctl00$MainContentHolder$...). Returns None if absent.
    """
    if doc is None:
        return None
    for el in doc.xpath("//*[@name]"):
        nm = el.get("name")
        if nm == suffix or nm.endswith("$" + suffix) or nm.endswith("_" + suffix):
            return nm
    return None


def _select_option_value(doc, ctl_full, label_substr, value_fallback=None):
    """Option value whose visible text contains label_substr; falls back to
    value_fallback if that exact option value exists in the select."""
    if doc is None or ctl_full is None:
        return None
    for sel in doc.xpath(f"//select[@name='{ctl_full}']"):
        for o in sel.xpath(".//option"):
            if label_substr.lower() in (o.text or "").lower():
                return o.get("value")
        if value_fallback is not None:
            for o in sel.xpath(".//option"):
                if o.get("value") == value_fallback:
                    return value_fallback
    return None


def _ffiec_select_product(session):
    """GET the bulk page, select 'Call Reports -- Single Period', and post
    back to populate the reporting-period dropdown. Returns
    (fields, doc, product_ctl_full, dates_ctl_full)."""
    r = session.get(FFIEC_BULK_URL, timeout=(10, 60))
    r.raise_for_status()
    fields, doc = _scrape_aspnet_state(r.text)

    prod_ctl = _resolve_ctl(doc, _PRODUCT_CTL)
    prod_val = _select_option_value(doc, prod_ctl, _PRODUCT_LABEL, _PRODUCT_VALUE)
    if prod_ctl is None or prod_val is None:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS
            + f" [product control {_PRODUCT_CTL!r} / option "
            f"{_PRODUCT_LABEL!r} not found on page]"
        )

    fields[prod_ctl] = prod_val
    fields["__EVENTTARGET"] = prod_ctl
    fields["__EVENTARGUMENT"] = ""
    r2 = session.post(FFIEC_BULK_URL, data=fields, timeout=(10, 120))
    r2.raise_for_status()
    fields, doc = _scrape_aspnet_state(r2.text)
    dates_ctl = _resolve_ctl(doc, _DATES_CTL)
    if dates_ctl is None:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS
            + f" [reporting-period control {_DATES_CTL!r} did not appear "
            "after selecting the product]"
        )
    fields[prod_ctl] = prod_val
    return fields, doc, prod_ctl, dates_ctl


def _ffiec_zip(period_mmddyyyy, deadline=900):
    """Drive the FFIEC bulk-download WebForms flow; return ZIP bytes for the
    Call Report Single-Period TSV bundle at the given period end date."""
    s = requests.Session()
    s.headers.update(_UA)
    fields, doc, prod_ctl, dates_ctl = _ffiec_select_product(s)

    date_val = None
    for sel in doc.xpath(f"//select[@name='{dates_ctl}']"):
        for o in sel.xpath(".//option"):
            txt = (o.text or "").strip()
            if txt == period_mmddyyyy or txt.replace("-", "/") == period_mmddyyyy:
                date_val = o.get("value")
                break
    if date_val is None:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS
            + f" [reporting period {period_mmddyyyy} not offered; "
            "call list_call_periods() to see available periods]"
        )

    fields[dates_ctl] = date_val
    fmt_ctl = _resolve_ctl(doc, _FORMAT_CTL)
    if fmt_ctl is not None:
        fields[fmt_ctl] = _FORMAT_TSV_VALUE
    else:  # fall back to setting any radio whose value is the TSV value
        for rb in doc.xpath("//input[@type='radio']"):
            if rb.get("name") and (rb.get("value") or "") == _FORMAT_TSV_VALUE:
                fields[rb.get("name")] = _FORMAT_TSV_VALUE
    dl_ctl = _resolve_ctl(doc, _DOWNLOAD_CTL)
    if dl_ctl is None:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS
            + f" [download button {_DOWNLOAD_CTL!r} not found]"
        )
    fields["__EVENTTARGET"] = ""
    fields["__EVENTARGUMENT"] = ""
    fields[dl_ctl] = "Download"

    r3 = s.post(FFIEC_BULK_URL, data=fields, timeout=(10, deadline), stream=True)
    r3.raise_for_status()
    ctype = r3.headers.get("Content-Type", "")
    if "zip" not in ctype and "octet-stream" not in ctype:
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS
            + f" [download returned Content-Type {ctype!r}, not a ZIP]"
        )
    buf = io.BytesIO()
    start = time.monotonic()
    for chunk in r3.iter_content(64 * 1024):
        if time.monotonic() - start > deadline:
            raise TimeoutError(f"FFIEC download exceeded {deadline}s")
        if chunk:
            buf.write(chunk)
    data = buf.getvalue()
    if data[:2] != b"PK":
        raise RuntimeError(
            FFIEC_FORM_BRITTLENESS + " [response was not a ZIP archive]"
        )
    return data


def _parse_sdf_part(raw):
    """Parse one SDF tab-delimited file: row 0 = MDRM codes (header),
    row 1 = human descriptions (dropped), data from row 2. The first
    column is ``IDRSSD``."""
    df = pd.read_csv(io.StringIO(raw), sep="\t", dtype=str, low_memory=False)
    if (len(df) and "IDRSSD" in df.columns
            and not str(df.iloc[0]["IDRSSD"]).strip().isdigit()):
        df = df.iloc[1:].reset_index(drop=True)
    if "IDRSSD" in df.columns:
        df["IDRSSD"] = pd.to_numeric(df["IDRSSD"],
                                     errors="coerce").astype("Int64")
    return df


def _read_sdf_member(zbytes, schedule):
    """Read a schedule out of an FFIEC SDF bundle.

    Large schedules (RCB, RCL, RCN, RCO, RCQ, RCRII, RCT, ...) are split
    by the FFIEC into "(1 of N)" files that share the IDRSSD key but carry
    DIFFERENT MDRM columns. Reading only the first part would silently drop
    the rest of that schedule's variables, so every part is read and the
    parts are outer-merged on IDRSSD into the full wide table.
    """
    z = zipfile.ZipFile(io.BytesIO(zbytes))
    names = z.namelist()
    want = schedule.upper()
    # files look like "FFIEC CDR Call Schedule RC 12312023.txt" or
    # "... Schedule RCRII 12312023(3 of 4).txt"; \b after the (escaped)
    # code stops 'RC' from matching 'RCA'/'RCRII' etc.
    cand = [n for n in names
            if re.search(rf"Schedule {re.escape(want)}\b", n, re.I)]
    if not cand and want in ("POR", "BULK POR"):
        cand = [n for n in names if "POR" in n.upper()]
    if not cand:
        raise ValueError(
            f"schedule {schedule!r} not in bundle; members: "
            + ", ".join(os.path.basename(n) for n in names)
        )

    def _part_idx(name):
        m = re.search(r"\((\d+) of (\d+)\)", name)
        # 0 (not 1) for an unmarked file so it sorts strictly before an
        # explicit "(1 of N)" part, avoiding a sort-key tie if FFIEC ever
        # ships both an unlabeled and a labeled part for one schedule.
        return int(m.group(1)) if m else 0

    cand.sort(key=_part_idx)
    parts = []
    for name in cand:
        with z.open(name) as f:
            parts.append(_parse_sdf_part(f.read().decode("latin-1")))
    if len(parts) == 1:
        if "IDRSSD" not in parts[0].columns:
            raise ValueError(
                f"schedule {schedule!r} file has no IDRSSD key column — "
                "refusing to return an unkeyed table."
            )
        return parts[0]
    merged = parts[0]
    for nxt in parts[1:]:
        if "IDRSSD" not in nxt.columns or "IDRSSD" not in merged.columns:
            raise ValueError(
                f"multi-part schedule {schedule!r} cannot be merged: a "
                "part is missing the IDRSSD key — refusing to return a "
                "silently truncated table."
            )
        # keep only IDRSSD + columns not already present, so the join adds
        # the new part's MDRM codes without suffix collisions
        new_cols = ["IDRSSD"] + [c for c in nxt.columns
                                 if c != "IDRSSD" and c not in merged.columns]
        merged = merged.merge(nxt[new_cols], on="IDRSSD", how="outer")
    return merged.reset_index(drop=True)


def _ffiec_cache(period_end):
    return os.path.join(DATA_DIR, f"ffiec_call_{period_end:%Y%m%d}.zip")


def list_call_periods():
    """Return the reporting-period end dates the FFIEC bulk form currently
    offers (MM/DD/YYYY strings, most recent first). Brittle (see note)."""
    s = requests.Session()
    s.headers.update(_UA)
    _, doc, _, dates_ctl = _ffiec_select_product(s)
    out = []
    for sel in doc.xpath(f"//select[@name='{dates_ctl}']"):
        for o in sel.xpath(".//option"):
            t = (o.text or "").strip()
            if re.match(r"\d{1,2}/\d{1,2}/\d{4}$", t):
                out.append(t)
    return out


def call_report(quarter, rssdids=None, schedule="RC", refresh=False):
    """One quarter of FFIEC Call Report data, literal RCON/RIAD columns.

    Args:
        quarter: '2023Q4', '12/31/2023', (2023, 4), etc.
        rssdids: optional iterable of IDRSSD (Fed RSSD) ints to filter to.
        schedule: SDF schedule code — 'RC' (balance sheet), 'RI' (income),
            'RCRI'/'RCRII' (regulatory capital parts I/II; no plain 'RCR'),
            'POR' (panel of reporters: bank identity + FDIC cert), etc.
            Default 'RC'. Multi-part schedules are auto-merged on IDRSSD;
            an unknown code raises ValueError listing the bundle members.
        refresh: re-download even if the bundle is cached.

    Returns: DataFrame keyed by IDRSSD with that schedule's MDRM columns.

    Raises RuntimeError (FFIEC_FORM_BRITTLENESS) if the bulk form flow
    breaks — fall back to fdic_financials() for standardized fields.
    """
    _ensure_dir()
    year, qtr, pe, mmddyyyy = parse_quarter(quarter)
    cache = _ffiec_cache(pe)
    if refresh or not os.path.exists(cache):
        zbytes = _ffiec_zip(mmddyyyy)
        # atomic: never leave a half-written ZIP that later raises an
        # opaque BadZipFile instead of FFIEC_FORM_BRITTLENESS
        with open(cache + ".part", "wb") as f:
            f.write(zbytes)
        os.replace(cache + ".part", cache)
    else:
        with open(cache, "rb") as f:
            zbytes = f.read()
    df = _read_sdf_member(zbytes, schedule)
    df.insert(0, "quarter", f"{year}Q{qtr}")
    df.insert(1, "period_end", pe)
    if rssdids is not None:
        keep = set(int(x) for x in rssdids)
        df = df[df["IDRSSD"].isin(keep)].reset_index(drop=True)
    return df


# ── Chicago Fed BHCF (FR Y-9C, holding companies) ──

def _bhcf_cache(pe):
    return os.path.join(DATA_DIR, f"bhcf_{pe:%Y%m}.parquet")


def _user_bhcf_path(pe):
    """Where a user drops a NIC-downloaded BHCF file for 2021Q2+ quarters
    (the realistic workflow given NIC's bot protection — mirrors the
    hrs-scf user-placed-extract pattern)."""
    return [
        os.path.join(DATA_DIR, f"bhcf{pe:%Y%m}.csv"),
        os.path.join(DATA_DIR, f"BHCF{pe:%Y%m}.csv"),
        os.path.join(DATA_DIR, f"bhcf{pe:%Y%m}.txt"),
    ]


def y9c(quarter, rssdids=None, refresh=False):
    """One quarter of FR Y-9C consolidated BHC data, BHCK-/BHCP-coded
    (e.g. BHCK2170 = consolidated total assets), keyed by RSSD9001.

    Source by vintage (see module docstring + BHCF_URL note):
      * 1986Q1 .. 2021Q1 — pulled live from the Chicago Fed BHCF
        comma-delimited .csv (no key, reliable).
      * 2021Q2 onward — the Chicago Fed stopped hosting in-window data
        (2021-06-15 notice). The current source is the NIC Financial Data
        Download (www.ffiec.gov/npw/FinancialReport/DataDownload), an
        Angular SPA behind Akamai bot protection that
        403s server/datacenter IPs. y9c() therefore does NOT scrape it; it
        reads a user-placed file from data/call_reports/ (bhcfYYYYMM.csv —
        unzip the NIC "Financial Data" bundle there) and raises an
        instructive RuntimeError if absent. This is the same
        registration/bot-wall pattern as the hrs-scf skill: documented,
        never silent.

    Args:
        quarter: as in call_report.
        rssdids: optional iterable of RSSD9001 (the BHC's RSSD) ints.
        refresh: re-download / re-read even if cached.

    Returns: DataFrame keyed by RSSD9001 with BHCK/BHCP columns.
    """
    _ensure_dir()
    year, qtr, pe, _ = parse_quarter(quarter)
    pq = _bhcf_cache(pe)
    if not refresh and os.path.exists(pq):
        df = pd.read_parquet(pq)
        if df.empty or "RSSD9001" not in df.columns:
            # a bad parquet cached by a pre-guard version: delete & re-fetch
            os.remove(pq)
            return y9c(quarter, rssdids=rssdids, refresh=True)
    else:
        within_chicago = (year, qtr) <= (BHCF_LAST_YEAR, BHCF_LAST_QTR)
        raw = None
        if within_chicago:
            url = BHCF_URL.format(yymm=pe.strftime("%y%m"))
            r = requests.get(url, headers=_UA, timeout=(10, 300))
            body = r.content.lstrip()
            if r.status_code == 200 and body and body[:1] != b"<":
                raw = r.content.decode("latin-1")
            else:
                raise RuntimeError(
                    f"Chicago Fed BHCF not retrievable for {year}Q{qtr} "
                    f"(HTTP {r.status_code} at {url}). Check "
                    "https://www.chicagofed.org/banking/financial-institution-reports/bhc-data "
                    "for the current naming."
                )
        else:
            placed = next((p for p in _user_bhcf_path(pe)
                           if os.path.exists(p)), None)
            if placed is None:
                raise RuntimeError(
                    f"FR Y-9C for {year}Q{qtr} is past the Chicago Fed "
                    f"hosting cutoff ({BHCF_LAST_YEAR}Q{BHCF_LAST_QTR}). "
                    "Download the BHCF/Y-9C 'Financial Data' bundle for "
                    f"{pe:%Y-%m} from the NIC Financial Data Download page "
                    f"({NIC_DATADOWNLOAD_URL}) — it is behind Akamai bot "
                    "protection so it cannot be fetched server-side — and "
                    f"place the file at {DATA_DIR}/bhcf{pe:%Y%m}.csv "
                    "(or .txt). Pre-2021Q2 quarters are fetched "
                    "automatically; only in-window vintages need this "
                    "one-time manual step."
                )
            with open(placed, "rb") as f:
                raw = f.read().decode("latin-1")
        # Chicago Fed CSVs are comma-delimited (the legacy caret-delimited
        # ASCII files predate 2001); NIC bundles are caret-delimited. Sniff.
        first = raw.split("\n", 1)[0]
        sep = "^" if first.count("^") > first.count(",") else ","
        df = pd.read_csv(io.StringIO(raw), sep=sep, dtype=str,
                         low_memory=False)
        if df.empty or "RSSD9001" not in df.columns:
            raise RuntimeError(
                f"FR Y-9C source for {year}Q{qtr} parsed to an empty / "
                "malformed table (no RSSD9001 column). Refusing to cache a "
                "bad file; re-check the source URL or the user-placed file."
            )
        df.to_parquet(pq)
    if "RSSD9001" in df.columns:
        df["RSSD9001"] = pd.to_numeric(df["RSSD9001"], errors="coerce").astype("Int64")
    df = df.copy()
    df.insert(0, "quarter", f"{year}Q{qtr}")
    df.insert(1, "period_end", pe)
    if rssdids is not None and "RSSD9001" in df.columns:
        keep = set(int(x) for x in rssdids)
        df = df[df["RSSD9001"].isin(keep)].reset_index(drop=True)
    return df


# ── FDIC Financial Data API (robust, standardized, no key) ──

def _fdic_get(endpoint, params, max_retries=5):
    """One FDIC API GET with polite exponential backoff on 429/5xx (the
    public endpoint rate-limits bursty paging)."""
    delay = 1.0
    for attempt in range(max_retries):
        r = requests.get(f"{FDIC_API}/{endpoint}", params=params,
                          headers=_UA, timeout=(10, 120))
        if r.status_code in (429, 500, 502, 503, 504):
            ra = r.headers.get("Retry-After")
            wait = float(ra) if (ra and ra.isdigit()) else delay
            if attempt == max_retries - 1:
                r.raise_for_status()
            time.sleep(min(wait, 30))
            delay *= 2
            continue
        r.raise_for_status()
        return r
    return r  # pragma: no cover


def _fdic_paged(endpoint, params, max_pages=200):
    """Page through a FDIC banks.data API endpoint, return list of records."""
    rows = []
    offset = 0
    limit = int(params.get("limit", 1000))
    for _ in range(max_pages):
        p = dict(params)
        p["limit"] = limit
        p["offset"] = offset
        r = _fdic_get(endpoint, p)
        js = r.json()
        batch = js.get("data", [])
        if not batch:
            break
        rows.extend(d.get("data", d) for d in batch)
        if len(batch) < limit:
            break
        offset += limit
    return rows


def fdic_financials(quarter, certs=None, fields=None):
    """One quarter of FDIC-API bank financials (standardized, NOT RCON).

    Robust no-key path; use for `bank_panel` and as the fallback when the
    FFIEC bulk form breaks. Keyed by CERT.

    Args:
        quarter: as in call_report. Mapped to REPDTE = YYYYMMDD.
        certs: optional iterable of FDIC CERT ints to filter to.
        fields: optional list of FDIC field codes (default: a banking-
            channel core set). Common: ASSET, DEP, LNLSNET, EQ, NETINC,
            NIMY, RBCT1J (tier-1 capital), ROA, ROE, NETINC.

    Returns: DataFrame.
    """
    _, _, pe, _ = parse_quarter(quarter)
    repdte = pe.strftime("%Y%m%d")
    # NOTE: the /financials endpoint does NOT expose FED_RSSD (it silently
    # drops unknown fields). Get the CERT<->RSSD bridge from
    # fdic_institutions()/nic_link(), not from here.
    core = fields or ["CERT", "REPDTE", "NAME", "STALP", "ASSET", "DEP",
                      "LNLSNET", "EQ", "NETINC", "NIMY", "RBCT1J", "ROA",
                      "ROE"]
    flt = f"REPDTE:{repdte}"
    if certs is not None:
        cl = " OR ".join(f"CERT:{int(c)}" for c in certs)
        flt = f"{flt} AND ({cl})"
    rows = _fdic_paged("financials", {
        "filters": flt, "fields": ",".join(core), "limit": 1000,
    })
    df = pd.DataFrame(rows)
    for c in df.columns:
        if c not in ("NAME", "STALP", "REPDTE"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def fdic_institutions(certs=None, rssdids=None, active_only=True):
    """FDIC institution directory — the CERT <-> FED_RSSD crosswalk.

    Returns CERT, NAME, FED_RSSD, CITY, STALP, ACTIVE, etc. Either filter
    by `certs`, by `rssdids` (FED_RSSD), or pull all (active) institutions.
    """
    parts = []
    if active_only:
        parts.append("ACTIVE:1")
    if certs is not None:
        parts.append("(" + " OR ".join(f"CERT:{int(c)}" for c in certs) + ")")
    if rssdids is not None:
        parts.append("(" + " OR ".join(f"FED_RSSD:{int(r)}" for r in rssdids) + ")")
    flt = " AND ".join(parts) if parts else ""
    params = {
        "fields": "CERT,NAME,FED_RSSD,CITY,STALP,ACTIVE,BKCLASS,ESTYMD",
        "limit": 1000,
    }
    if flt:
        params["filters"] = flt
    return pd.DataFrame(_fdic_paged("institutions", params))


def nic_link(rssdid):
    """Resolve an RSSD ID to its FDIC CERT and identifying info.

    Practical RSSD <-> CERT crosswalk via the FDIC institutions API
    (reliable, no key). Returns a one-row DataFrame (or empty if the RSSD
    is a holding company / non-FDIC entity — those have an RSSD but no
    CERT).

    True NIC ownership *hierarchy* (parent/child, lead bank vs top holder)
    is NOT a name match: download the NIC bulk relationships/attributes
    CSVs from https://www.ffiec.gov/npw/FinancialReport/DataDownload
    (CSV_RELATIONSHIPS, CSV_ATTRIBUTES) and join on ID_RSSD. That bulk
    file is the only correct way to roll banks up to their holding company.
    """
    inst = fdic_institutions(rssdids=[int(rssdid)], active_only=False)
    return inst


# ── multi-quarter panel ──

def bank_panel(start_quarter, end_quarter, vars=None, source="fdic",
               rssdids=None, certs=None, schedule="RC"):
    """Stack quarterly bank data into a long panel.

    Args:
        start_quarter, end_quarter: inclusive range, e.g. '2020Q1' .. '2023Q4'.
        vars: columns to keep (plus the keys). For source='ffiec' these are
            RCON/RIAD MDRM codes; for source='fdic' they are FDIC field
            codes. None keeps everything.
        source: 'fdic' (robust, standardized, default) or 'ffiec' (literal
            RCON codes via the brittle bulk form).
        rssdids: filter by IDRSSD (ffiec) — ignored for fdic (use certs).
        certs: filter by FDIC CERT (fdic source).
        schedule: SDF schedule for source='ffiec' (default 'RC').

    Returns: long DataFrame with a 'quarter' column.
    """
    frames = []
    for (y, q) in _quarter_range(start_quarter, end_quarter):
        if source == "ffiec":
            df = call_report((y, q), rssdids=rssdids, schedule=schedule)
            keycols = ["quarter", "period_end", "IDRSSD"]
        elif source == "fdic":
            df = fdic_financials((y, q), certs=certs)
            df.insert(0, "quarter", f"{y}Q{q}")
            keycols = ["quarter", "CERT", "REPDTE", "NAME"]
        else:
            raise ValueError(f"source must be 'fdic' or 'ffiec', got {source!r}")
        if vars is not None:
            cols = [c for c in keycols if c in df.columns] + \
                   [v for v in vars if v in df.columns]
            df = df[cols]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
