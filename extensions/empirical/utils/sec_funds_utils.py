"""SEC fund-filing utilities — N-CEN, NPORT-P, and N-1A fee tables from EDGAR.

The `edgar` skill covers 10-K/10-Q corporate filings. Fund-specific forms use
different schemas and are not parsed by edgartools; this module parses them
directly from EDGAR (no API key — just a User-Agent built from .env).

Usage:
    from utils.sec_funds_utils import (
        list_fund_filings, download_ncen, download_nport,
        download_n1a_fees, n1a_fee_table, flag_dc_target_funds,
        link_to_crsp_via_cik,
    )

What each form gives you (verified against live EDGAR, 2024-2026 filings):
  * N-CEN  (annual census, post-2018) — registrant + per-series census:
           advisers, underwriters, transfer agents, securities-lending,
           expense-waiver flags, fund types, index-fund tracking error.
  * NPORT-P (monthly portfolio, post-2019) — per-security positions, asset/
           issuer category, country, fair-value level, fund-level assets.
  * N-1A / 485BPOS (prospectus) — per-share-class fee table via the
           Risk/Return (rr:) XBRL exhibit: management fee, 12b-1, other
           expenses, gross/net expense ratio, fee waiver, expense example.

IMPORTANT — there is NO "offered to defined contribution plans" field in
N-CEN. (N-CEN Item C.7 is *securities lending*.) DC-plan targeting is
inferred from share-class names via `flag_dc_target_funds` (R1-R9/Class
R(n)/Retirement/K classes), a transparent heuristic — not a regulator-
supplied flag. R10+ and T-series names are not matched (false negatives).

Known coverage limits (documented, not silently dropped):
  * NPORT-P: only <invstOrSec> long positions are parsed. <derivativeInfo>
    blocks (options/swaps/forwards/futures/warrants) are NOT included — a
    real gap for derivatives-heavy funds.
  * download_n1a_fees resolves the latest 485BPOS, falling back to N-1A for
    initial registrations. Not every prospectus filing embeds Risk/Return
    XBRL (sticker amendments / exhibit-only filings); those raise LookupError.
  * flag_dc_target_funds is a share-class-name heuristic; spot-check against
    prospectus distribution language for the families you use.

All functions read SEC_EDGAR_NAME and SEC_EDGAR_EMAIL from .env (a generic
identity is used if unset). WRDS-dependent helpers import lazily so the rest
of the module works with no WRDS server.
"""
import io
import os
import re
import time
import zipfile

import pandas as pd
import requests
from dotenv import load_dotenv
from lxml import etree

load_dotenv()

_IDENTITY = None
# Single-process throttle. NOT thread-safe by design — the pipeline drives
# this serially; the skill body's rule says don't add your own threads.
_LAST_REQ = [0.0]
_MIN_INTERVAL = 0.12  # SEC fair-access: <=10 req/s; stay well under


def _get_identity():
    """SEC User-Agent string from .env (name + email)."""
    global _IDENTITY
    if _IDENTITY is None:
        name = os.getenv("SEC_EDGAR_NAME", "ZeroPaper Research")
        email = os.getenv("SEC_EDGAR_EMAIL", "research@university.edu")
        _IDENTITY = f"{name} {email}"
    return _IDENTITY


def _get(url, timeout=60):
    """Rate-limited GET against SEC with the required User-Agent header."""
    wait = _MIN_INTERVAL - (time.time() - _LAST_REQ[0])
    if wait > 0:
        time.sleep(wait)
    r = requests.get(url, headers={"User-Agent": _get_identity()}, timeout=timeout)
    _LAST_REQ[0] = time.time()
    r.raise_for_status()
    return r


def _cik_int(cik):
    """Accept int, '320193', or 'CIK0000320193' → int."""
    if isinstance(cik, int):
        return cik
    s = re.sub(r"\D", "", str(cik))
    if not s:
        raise ValueError(f"could not parse CIK from {cik!r}")
    return int(s)


def _localname(el):
    return etree.QName(el).localname if isinstance(el.tag, str) else el.tag


# --------------------------------------------------------------------------
# Filing enumeration (submissions API — no WRDS needed)
# --------------------------------------------------------------------------

def get_fund_submissions(cik):
    """Raw submissions JSON for a registrant CIK (data.sec.gov/submissions)."""
    cik = _cik_int(cik)
    return _get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json").json()


def list_fund_filings(cik, form=None, since=None, include_old=True):
    """All filings for a registrant CIK as a DataFrame.

    Args:
        cik: registrant (trust) CIK — int or string.
        form: exact form type to filter (e.g. "N-CEN", "NPORT-P", "485BPOS").
              None returns every form.
        since: optional "YYYY-MM-DD" lower bound on filing date.
        include_old: also page through the older-filing shards
                     (filings.files), not just the recent ~1000.

    Returns:
        DataFrame[accession, form, filing_date, primary_document, report_date]
        sorted newest-first.
    """
    cik = _cik_int(cik)
    data = get_fund_submissions(cik)
    frames = []

    def _block_to_df(block):
        if not block.get("accessionNumber"):
            return None
        return pd.DataFrame({
            "accession": block["accessionNumber"],
            "form": block["form"],
            "filing_date": block["filingDate"],
            "primary_document": block.get("primaryDocument",
                                          [""] * len(block["accessionNumber"])),
            "report_date": block.get("reportDate",
                                     [""] * len(block["accessionNumber"])),
        })

    recent = _block_to_df(data["filings"]["recent"])
    if recent is not None:
        frames.append(recent)
    if include_old:
        for shard in data["filings"].get("files", []):
            try:
                j = _get(f"https://data.sec.gov/submissions/{shard['name']}").json()
            except Exception:
                continue
            df = _block_to_df(j)
            if df is not None:
                frames.append(df)

    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
        columns=["accession", "form", "filing_date", "primary_document", "report_date"])
    if form is not None:
        out = out[out["form"] == form]
    if since is not None:
        out = out[out["filing_date"] >= since]
    out = out.sort_values("filing_date", ascending=False).reset_index(drop=True)
    out.attrs["cik"] = cik
    return out


def find_latest_filing(cik, form):
    """(accession, filing_date) of the most recent `form` filing, or None."""
    df = list_fund_filings(cik, form=form)
    if df.empty:
        return None
    return df.iloc[0]["accession"], df.iloc[0]["filing_date"]


def filing_files(cik, accession):
    """List documents in a filing (EDGAR index.json directory items)."""
    cik = _cik_int(cik)
    a = accession.replace("-", "")
    j = _get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{a}/index.json").json()
    return j["directory"]["item"]


def fetch_doc(cik, accession, filename):
    """Raw bytes of one document inside a filing."""
    cik = _cik_int(cik)
    a = accession.replace("-", "")
    return _get(
        f"https://www.sec.gov/Archives/edgar/data/{cik}/{a}/{filename}").content


def _resolve_filing(cik, forms, accession):
    """Resolve (accession, primary_document) for a form or list of forms.

    `forms` may be a single form string or an ordered list — the first form
    with a filing wins (e.g. ["485BPOS", "N-1A"] so initial registrations
    fall back to N-1A). If `accession` is given it is returned as-is with an
    empty primary_document (the fast "I already know what I want" path — no
    historical enumeration); _fetch_primary_xml then resolves the right doc
    from the filing's own index, and _find_rr_instance does likewise for
    fee XBRL.
    """
    if isinstance(forms, str):
        forms = [forms]
    if accession is not None:
        return accession, ""
    for form in forms:
        df = list_fund_filings(cik, form=form)
        if not df.empty:
            return df.iloc[0]["accession"], df.iloc[0]["primary_document"]
    raise LookupError(
        f"no {'/'.join(forms)} filing found for CIK {_cik_int(cik)}")


def _fetch_primary_xml(cik, accession, primary_document, root_tag):
    """Fetch a filing's primary XML robustly.

    Tries raw "primary_doc.xml" first (the canonical XML for N-CEN/NPORT;
    the submissions-declared primaryDocument is often an XSL *viewer* path
    that returns rendered HTML), then the basename of primary_document,
    then scans the filing index for an .xml whose root is `root_tag`
    (e.g. "edgarSubmission"). Every candidate is content-checked for
    `root_tag` so an HTML viewer page is rejected, not parsed. Raises
    LookupError if none is found. The content check inspects only the
    first 4000 bytes — safe for EDGAR (the root element always appears in
    the first few hundred bytes); it is a cheap heuristic, not a parse.
    """
    needle = root_tag.encode()
    candidates = ["primary_doc.xml"]
    if primary_document:
        base = os.path.basename(primary_document)  # strip xsl viewer dir
        if base.endswith(".xml") and base not in candidates:
            candidates.append(base)
    last_err = None
    for fn in candidates:
        try:
            b = fetch_doc(cik, accession, fn)
        except requests.HTTPError as e:
            last_err = e
            continue
        if needle in b[:4000]:
            return b
    for it in filing_files(cik, accession):
        n = it["name"]
        if n.endswith(".xml") and not re.match(r"0\d{6,}", os.path.basename(n)):
            try:
                b = fetch_doc(cik, accession, n)
            except requests.HTTPError:
                continue
            if needle in b[:4000]:
                return b
    raise LookupError(
        f"no primary XML (<{root_tag}>) found in {accession} "
        f"for CIK {_cik_int(cik)} ({last_err})")


# --------------------------------------------------------------------------
# N-CEN  (annual fund census)
# --------------------------------------------------------------------------

# Registrant-level scalar fields worth surfacing (others are easy to add).
_NCEN_REG_FIELDS = [
    "registrantFullName", "registrantCik", "registrantLei",
    "investmentCompFileNo", "totalSeries", "registrantClassificationType",
    "isRegistrantFirstFiling", "isRegistrantLastFiling",
    "isMaterialWeakness", "isAccountingPrincipleChange",
]


def parse_ncen(xml_bytes):
    """Parse an N-CEN primary_doc.xml.

    Returns dict:
        {"registrant": {field: value, ...},
         "series": DataFrame — one row per series (management investment
                   company question block)}
    """
    root = etree.fromstring(xml_bytes)
    by_name = {}
    for el in root.iter():
        ln = _localname(el)
        if ln not in by_name and el.text and el.text.strip():
            by_name[ln] = el.text.strip()

    registrant = {f: by_name.get(f) for f in _NCEN_REG_FIELDS}

    rows = []
    for q in root.iter():
        if _localname(q) != "managementInvestmentQuestion":
            continue
        rec = {}

        def first(tag):
            for d in q.iter():
                if _localname(d) == tag and d.text and d.text.strip():
                    return d.text.strip()
            return None

        rec["fund_name"] = first("mgmtInvFundName")
        rec["series_id"] = first("mgmtInvSeriesId")
        rec["series_lei"] = first("mgmtInvLei")
        rec["num_authorized_classes"] = first("numAuthorizedClass")
        rec["num_added_classes"] = first("numAddedClass")
        rec["num_terminated_classes"] = first("numTerminatedClass")
        rec["is_non_diversified"] = first("isNonDiversifiedCompany")
        rec["is_securities_lending"] = first("isFundSecuritiesLending")
        rec["is_expense_limitation"] = first("isExpenseLimitationInPlace")
        rec["is_expense_waived"] = first("isExpenseReducedOrWaived")
        rec["net_income_sec_lending"] = first("netIncomeSecuritiesLending")
        rec["fund_types"] = ";".join(sorted({
            d.text.strip() for d in q.iter()
            if _localname(d) == "fundType" and d.text and d.text.strip()}))
        rec["advisers"] = ";".join(sorted({
            d.text.strip() for d in q.iter()
            if _localname(d) == "investmentAdviserName"
            and d.text and d.text.strip()}))
        rec["transfer_agents"] = ";".join(sorted({
            d.text.strip() for d in q.iter()
            if _localname(d) == "transferAgentName"
            and d.text and d.text.strip()}))
        rows.append(rec)

    return {"registrant": registrant, "series": pd.DataFrame(rows)}


def download_ncen(cik, accession=None):
    """Download + parse the latest (or a specific) N-CEN for a registrant.

    Args:
        cik: registrant CIK.
        accession: specific accession; None → most recent N-CEN.

    Returns: dict from parse_ncen, plus key "accession".
    """
    accession, pdoc = _resolve_filing(cik, "N-CEN", accession)
    xml = _fetch_primary_xml(cik, accession, pdoc, "edgarSubmission")
    out = parse_ncen(xml)
    out["accession"] = accession
    return out


# --------------------------------------------------------------------------
# NPORT-P  (monthly portfolio holdings)
# --------------------------------------------------------------------------

_NPORT_HOLDING_FIELDS = [
    "name", "lei", "title", "cusip", "balance", "units", "curCd",
    "valUSD", "pctVal", "payoffProfile", "assetCat", "issuerCat",
    "invCountry", "isRestrictedSec", "fairValLevel",
]


def parse_nport(xml_bytes):
    """Parse an NPORT-P primary_doc.xml.

    Returns dict:
        {"gen_info": {...}, "fund_info": {...},
         "holdings": DataFrame — one row per invstOrSec position}
    """
    root = etree.fromstring(xml_bytes)

    def grab(parent_tag, fields):
        node = next((e for e in root.iter()
                     if _localname(e) == parent_tag), None)
        if node is None:
            return {}
        out = {}
        for child in node:
            ln = _localname(child)
            if ln in fields and child.text and child.text.strip():
                out[ln] = child.text.strip()
        return out

    gen = grab("genInfo", {"regName", "regCik", "regLei", "regFileNumber",
                           "seriesName", "seriesId", "seriesLei",
                           "repPdEnd", "repPdDate", "isFinalFiling"})
    fund = grab("fundInfo", {"totAssets", "totLiabs", "netAssets"})

    rows = []
    for sec in root.iter():
        if _localname(sec) != "invstOrSec":
            continue
        rec = {}
        for child in sec.iter():
            ln = _localname(child)
            if ln in _NPORT_HOLDING_FIELDS and ln not in rec \
                    and child.text and child.text.strip():
                rec[ln] = child.text.strip()
        rows.append(rec)

    hold = pd.DataFrame(rows)
    for col in ("balance", "valUSD", "pctVal"):
        if col in hold.columns:
            hold[col] = pd.to_numeric(hold[col], errors="coerce")
    return {"gen_info": gen, "fund_info": fund, "holdings": hold}


def download_nport(cik, accession=None):
    """Download + parse the latest (or a specific) NPORT-P for a registrant.

    NPORT-P is filed per registrant; one filing covers one series for one
    month. Use list_fund_filings(cik, "NPORT-P") to find the month you want.
    """
    accession, pdoc = _resolve_filing(cik, "NPORT-P", accession)
    xml = _fetch_primary_xml(cik, accession, pdoc, "edgarSubmission")
    out = parse_nport(xml)
    out["accession"] = accession
    return out


# --------------------------------------------------------------------------
# N-1A / 485BPOS  fee table  (Risk/Return "rr:" XBRL exhibit)
# --------------------------------------------------------------------------

# rr: concepts that make up the standard prospectus fee table.
_RR_FEE_CONCEPTS = {
    "ManagementFeesOverAssets": "mgmt_fee",
    "DistributionAndService12b1FeesOverAssets": "fee_12b1",
    "OtherExpensesOverAssets": "other_exp",
    "ExpensesOverAssets": "gross_exp_ratio",
    "NetExpensesOverAssets": "net_exp_ratio",
    "FeeWaiverOrReimbursementOverAssets": "fee_waiver",
    "AcquiredFundFeesAndExpensesOverAssets": "acq_fund_fees",
    "RedemptionFeeOverRedemption": "redemption_fee",
    "MaximumSalesChargeImposedOnPurchasesOverOther": "max_front_load",
    "MaximumDeferredSalesChargeOverOther": "max_deferred_load",
    "ExpenseExampleYear01": "example_1yr",
    "ExpenseExampleYear03": "example_3yr",
    "ExpenseExampleYear05": "example_5yr",
    "ExpenseExampleYear10": "example_10yr",
}


def _find_rr_instance(cik, accession):
    """Locate the Risk/Return XBRL instance document inside a 485BPOS/N-1A.

    The rr instance is the .xml document (not a *_cal/_def/_lab/_pre.xml
    linkbase, not the complete-submission .txt/.xml) that contains
    <rr:...> elements. Falls back to scanning the -xbrl.zip if no loose
    instance is present.
    """
    items = filing_files(cik, accession)
    names = [it["name"] for it in items]

    def _skip(path):
        base = os.path.basename(path)
        return (re.search(r"_(cal|def|lab|pre)\.xml$|-xbrl\.zip$", base)
                or re.match(r"0\d{6,}", base))

    for n in names:
        if n.endswith(".xml") and not _skip(n):
            try:
                b = fetch_doc(cik, accession, n)
            except Exception:
                continue
            if b"<rr:" in b or b'"http://xbrl.sec.gov/rr/' in b:
                return n, b
    # fallback: the XBRL zip
    zname = next((n for n in names if n.endswith("-xbrl.zip")), None)
    if zname:
        zb = fetch_doc(cik, accession, zname)
        z = zipfile.ZipFile(io.BytesIO(zb))
        for n in z.namelist():
            if n.endswith(".xml") and not _skip(n):
                b = z.read(n)
                if b"<rr:" in b:
                    return n, b
    return None, None


def parse_rr_xbrl(xml_bytes):
    """Parse a Risk/Return XBRL instance into a tidy per-class fee table.

    Class identity is recovered from the XBRL context: the contextRef
    encodes the series id (S#########) and class id (C#########), and the
    context segment's explicitMember gives the prospectus share-class
    member. Both are returned so results link cleanly to CRSP/N-CEN.

    Returns DataFrame[series_id, class_id, class_member, concept, field,
    value] (long form). Use n1a_fee_table() for the wide pivot.
    """
    root = etree.fromstring(xml_bytes)
    rr_ns = [v for v in set(root.nsmap.values())
             if v and "/rr/" in v] + ["http://xbrl.sec.gov/rr/2023"]
    rr_ns = set(rr_ns)

    # Map context id → (series_id, class_id, member label)
    ctx = {}
    for c in root.iter():
        if _localname(c) != "context":
            continue
        cid = c.get("id")
        member = None
        for m in c.iter():
            if _localname(m) == "explicitMember" and m.text:
                member = m.text.strip().split(":")[-1]
        sid = re.search(r"(S\d{9,})", cid or "")
        clid = re.search(r"(C\d{9,})", cid or "")
        ctx[cid] = (sid.group(1) if sid else None,
                    clid.group(1) if clid else None,
                    member)

    rows = []
    for el in root.iter():
        q = etree.QName(el)
        if q.namespace not in rr_ns:
            continue
        concept = q.localname
        if concept not in _RR_FEE_CONCEPTS:
            continue
        cref = el.get("contextRef")
        sid, clid, member = ctx.get(cref, (None, None, None))
        val = (el.text or "").strip()
        try:
            val = float(val)
        except ValueError:
            continue  # textblock / narrative concept, not a number
        rows.append({
            "series_id": sid, "class_id": clid, "class_member": member,
            "context": cref, "concept": concept,
            "field": _RR_FEE_CONCEPTS[concept], "value": val,
        })
    return pd.DataFrame(rows)


def download_n1a_fees(cik, accession=None):
    """Download + parse the per-class fee table from a 485BPOS / N-1A.

    Resolves the latest 485BPOS, falling back to N-1A (initial
    registrations) when no 485BPOS exists. Not every prospectus filing
    embeds Risk/Return XBRL (sticker amendments / exhibit-only filings do
    not), and a filing can carry an rr instance with no numeric fee facts.
    Either case raises LookupError naming the filing — pick an earlier one
    via list_fund_filings(cik, "485BPOS").

    Returns the long-form DataFrame from parse_rr_xbrl, with "accession".
    """
    accession, _ = _resolve_filing(cik, ["485BPOS", "N-1A"], accession)
    name, xml = _find_rr_instance(cik, accession)
    if xml is None:
        raise LookupError(
            f"prospectus {accession} (CIK {_cik_int(cik)}) carries no "
            f"Risk/Return XBRL instance — try an earlier 485BPOS via "
            f"list_fund_filings(cik, '485BPOS').")
    df = parse_rr_xbrl(xml)
    if df.empty:
        raise LookupError(
            f"prospectus {accession} (CIK {_cik_int(cik)}) has a "
            f"Risk/Return XBRL instance ({name}) but no numeric fee facts "
            f"(namespace mismatch or narrative-only) — try an earlier "
            f"485BPOS via list_fund_filings(cik, '485BPOS').")
    df.attrs["accession"] = accession
    df.attrs["rr_document"] = name
    return df


def n1a_fee_table(cik, accession=None):
    """Wide per-share-class fee table: one row per class, fee fields as cols.

    Convenience wrapper over download_n1a_fees → pivot on (series_id,
    class_id, class_member).
    """
    # download_n1a_fees raises LookupError on no/empty rr data, so `long`
    # is always non-empty here.
    long = download_n1a_fees(cik, accession=accession)
    wide = (long.pivot_table(index=["series_id", "class_id", "class_member"],
                             columns="field", values="value",
                             aggfunc="first")
            .reset_index())
    wide.columns.name = None
    wide.attrs.update(long.attrs)
    return wide


# --------------------------------------------------------------------------
# DC-plan targeting heuristic (NOT a regulator-supplied flag)
# --------------------------------------------------------------------------

# Share-class naming conventions used by the industry for the
# defined-contribution / retirement-plan distribution channel.
_DC_CLASS_PATTERNS = [
    (r"\bR[1-9]\b", "R1-R9 retirement series"),
    (r"\bClass\s*R\d?\b|\bR\d?\s*Shares?\b", "R / Class R(n) share class"),
    (r"\bRetirement\b", "Retirement class"),
    (r"\bClass\s*K\b|\bK\s*Shares?\b", "K class (DC-oriented)"),
]


def flag_dc_target_funds(obj, name_col="class_member"):
    """Tag share classes likely sold through defined-contribution plans.

    There is NO N-CEN field for this (N-CEN Item C.7 is securities lending);
    this is a transparent name-based heuristic on share-class labels — the
    R1-R9 / Class R(n) / Retirement / Class K conventions the DC channel
    uses. R10+ and T-series names match no pattern and are false negatives.
    Always state it as a heuristic in the paper and spot-check against
    prospectus distribution language for the families you use.

    Args:
        obj: a DataFrame (e.g. from n1a_fee_table) or an iterable of class
             name strings.
        name_col: column holding the share-class label when obj is a frame.

    Returns:
        If a DataFrame: a copy with added columns is_dc_share_class (bool)
        and dc_match_reason (str). If an iterable: a DataFrame[class_name,
        is_dc_share_class, dc_match_reason].
    """
    pats = [(re.compile(p, re.I), why) for p, why in _DC_CLASS_PATTERNS]

    def classify(label):
        s = "" if label is None else str(label)
        for rx, why in pats:
            if rx.search(s):
                return True, why
        return False, ""

    if isinstance(obj, pd.DataFrame):
        out = obj.copy()
        flags = out[name_col].map(classify)
        out["is_dc_share_class"] = [f[0] for f in flags]
        out["dc_match_reason"] = [f[1] for f in flags]
        return out

    rows = []
    for label in obj:
        ok, why = classify(label)
        rows.append({"class_name": label,
                     "is_dc_share_class": ok, "dc_match_reason": why})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# WRDS-dependent helpers (optional — import lazily, work offline otherwise)
# --------------------------------------------------------------------------

def list_ncen_index(year=None, form="N-CEN", limit=50000):
    """Filing index for fund forms from WRDS `wrdssec_all.forms`.

    Requires the WRDS server (utils.wrds_client). Use this only when you
    need a population-level enumeration of N-CEN/NPORT filers; for a known
    registrant the free submissions API (list_fund_filings) is faster and
    needs no WRDS.

    Returns DataFrame[cik, coname, form, fdate, fname]. NOTE: the
    wrdssec_all.forms column is `form` (not form_type), and there is no
    accession column — `fname` is the EDGAR file path (verified against
    live WRDS, schema: gvkey, cik, fdate, findexdate, lindexdate, form,
    coname, fname, iname, source).
    """
    from utils.wrds_client import wrds_query, wrds_start
    wrds_start()
    where = [f"form = '{form}'"]
    if year is not None:
        where.append(f"date_part('year', fdate) = {int(year)}")
    sql = (f"SELECT cik, coname, form, fdate, fname "
           f"FROM wrdssec_all.forms "
           f"WHERE {' AND '.join(where)} "
           f"ORDER BY fdate DESC LIMIT {int(limit)}")
    return wrds_query(sql)


def link_to_crsp_via_cik(df, cik_col="cik", crsp_cik_col="comp_cik"):
    """Attach crsp_fundno via the WRDS CIK↔CRSP map (crsp.crsp_cik_map).

    Verified schema (live WRDS): crsp_cik_map has columns
    [crsp_fundno, comp_cik, series_cik, contract_cik] — there is NO plain
    `cik` column. The three CIK columns are distinct grains:
      * comp_cik     — registrant/company (trust) CIK   ← default join key
      * series_cik   — fund-series-level CIK
      * contract_cik — share-class-level CIK
    Join on the level matching your input ids. A registrant/trust CIK maps
    to MANY crsp_fundno (one per series×class) — this is a 1→many expansion,
    not a bug; aggregate or restrict downstream as your design requires.

    Requires the WRDS server. Pulls the full crosswalk each call — for
    panel/loop use, fetch crsp.crsp_cik_map once and merge locally.

    Args:
        df: DataFrame with a CIK column.
        cik_col: name of the CIK column in df (zero-padding normalized).
        crsp_cik_col: which crsp_cik_map CIK column to join on
            ("comp_cik" | "series_cik" | "contract_cik").

    Returns: df left-joined to the map (adds crsp_fundno + the other
    crsp_*_cik columns). Row count grows with the 1→many expansion.
    """
    from utils.wrds_client import wrds_query, wrds_start
    wrds_start()
    cmap = wrds_query("SELECT crsp_fundno, comp_cik, series_cik, "
                      "contract_cik FROM crsp.crsp_cik_map")
    cmap.columns = [c.lower() for c in cmap.columns]
    if crsp_cik_col not in cmap.columns:
        raise ValueError(
            f"crsp_cik_col={crsp_cik_col!r} not in crsp_cik_map "
            f"{list(cmap.columns)}")
    out = df.copy()
    out["_cik_norm"] = out[cik_col].map(
        lambda x: int(re.sub(r"\D", "", str(x))) if pd.notna(x) else None)
    cmap["_cik_norm"] = pd.to_numeric(cmap[crsp_cik_col], errors="coerce")
    merged = out.merge(cmap, on="_cik_norm", how="left",
                       suffixes=("", "_crspmap"))
    return merged.drop(columns=["_cik_norm"])
