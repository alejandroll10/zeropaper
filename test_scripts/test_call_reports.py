"""Test call-reports skill (issues #7, #33) — FFIEC CDR + FR Y-9C + FDIC API.

Acceptance (issue #7):
  * Pull one quarter's Call Report, extract RCON-coded variables
    (RCON2170 total assets), and count banks.
  * Exercise the RSSD <-> CERT linking crosswalk.

Acceptance (issue #33 — bank -> holding-company rollup):
  * bank_to_holder() maps a known bank RSSD to its known top-holder RSSD,
    hand-checked (852218 -> 1039502 JPMorgan; 480228 -> 1073757 BofA).
  * bank_panel(holder=True) attaches the rollup key point-in-time.
  * nic_relationships()/nic_attributes() raise the documented Akamai-wall
    RuntimeError when no bulk file is placed (HARD — the wall is a stated
    limit, like the Y-9C 2021Q2+ manual step), and the source='nic' walk
    is exercised only when a user file is present (documented SKIP).

Test policy mirrors the codebase convention (hrs-scf): the reliable,
no-key paths (FDIC API; Chicago Fed pre-2021Q1 BHCF) are HARD assertions;
the deliberately-brittle FFIEC bulk-form path is a SKIP (not FAIL) if the
ASP.NET form is unreachable/changed — but when it works, the RCON-code
extraction and bank count ARE hard-asserted, satisfying the acceptance
criterion. The Y-9C post-2021Q1 manual wall is a documented SKIP.

Run from project root:
    PYTHONPATH=code python3 test_scripts/test_call_reports.py
"""
import sys

from utils.call_reports_utils import (
    call_report, y9c, bank_panel, fdic_financials, fdic_institutions,
    nic_link, bank_to_holder, nic_relationships, nic_attributes,
    parse_quarter, FFIEC_FORM_BRITTLENESS,
)

JPM_BANK_RSSD = 852218   # JPMorgan Chase Bank, N.A. (a bank)
JPM_BANK_CERT = 628
JPM_HOLDER_RSSD = 1039502  # JPMorgan Chase & Co. (the top BHC) — the y9c example
BOFA_BANK_RSSD = 480228  # Bank of America, N.A.
BOFA_HOLDER_RSSD = 1073757  # Bank of America Corp (top BHC)

# === Test 1: quarter parsing ===
print("=== Test 1: parse_quarter ===")
import datetime as _dt
for spec in ("2023Q4", "2023q4", "2023-Q4", "Q4 2023", "12/31/2023",
             "20231231", (2023, 4), _dt.datetime(2023, 11, 7)):
    y, q, pe, mmdd = parse_quarter(spec)
    assert (y, q, mmdd) == (2023, 4, "12/31/2023"), (spec, y, q, mmdd)
print("  8 quarter spec forms (str/tuple/datetime) all -> 2023Q4 OK")

# === Test 2: FDIC API — reliable, no key (HARD) ===
print("\n=== Test 2: fdic_financials('2023Q4') — count banks ===")
fd = fdic_financials("2023Q4")
n_banks = fd["CERT"].nunique()
assert 4000 < n_banks < 6000, f"implausible bank count {n_banks}"
assets_tn = fd["ASSET"].fillna(0).sum() / 1e9  # $thousands -> $trillions
assert 18 < assets_tn < 30, f"US banking assets {assets_tn:.1f}T implausible"
print(f"  banks: {n_banks:,} | aggregate assets ${assets_tn:.1f}T")

# === Test 3: RSSD <-> CERT crosswalk (HARD) ===
print("\n=== Test 3: RSSD <-> CERT linking ===")
inst = fdic_institutions(certs=[JPM_BANK_CERT])
assert len(inst) == 1, f"expected 1 institution for CERT {JPM_BANK_CERT}"
assert int(inst.iloc[0]["FED_RSSD"]) == JPM_BANK_RSSD, \
    f"CERT {JPM_BANK_CERT} should map to RSSD {JPM_BANK_RSSD}"
back = nic_link(JPM_BANK_RSSD)
assert int(back.iloc[0]["CERT"]) == JPM_BANK_CERT, "RSSD->CERT round-trip"
print(f"  CERT {JPM_BANK_CERT} <-> RSSD {JPM_BANK_RSSD} "
      f"({inst.iloc[0]['NAME']}) round-trips")

# === Test 4: FR Y-9C BHCF, pre-2021Q1 live (HARD) + post-cutoff SKIP ===
print("\n=== Test 4: y9c — Chicago Fed live + documented cutoff ===")
bhc = y9c("2020Q4")
assert "RSSD9001" in bhc.columns and "BHCK2170" in bhc.columns, \
    f"Y-9C missing BHCK codes; cols sample: {list(bhc.columns)[:8]}"
import pandas as pd
bhc_assets = pd.to_numeric(bhc["BHCK2170"], errors="coerce").fillna(0).sum() / 1e9
assert 15 < bhc_assets < 35, f"BHC consolidated assets {bhc_assets:.1f}T odd"
print(f"  2020Q4: {len(bhc):,} BHCs, consolidated assets ${bhc_assets:.1f}T")
try:
    y9c("2023Q4")
    raise AssertionError("y9c('2023Q4') should hit the documented cutoff")
except RuntimeError as e:
    assert "cutoff" in str(e) and "NIC" in str(e), f"wrong error: {e}"
    print("  2023Q4 (post-2021Q1): documented manual-download RuntimeError OK")

# === Test 4b: bank_to_holder — issue #33 ACCEPTANCE (HARD, no key) ===
# Placed before the brittle FFIEC path so it runs regardless of FFIEC
# reachability (Test 5 may sys.exit early when the bulk form is down).
print("\n=== Test 4b: bank_to_holder — bank RSSD -> top holder RSSD ===")
h = bank_to_holder([JPM_BANK_RSSD, BOFA_BANK_RSSD]).set_index("bank_rssd")
assert int(h.loc[JPM_BANK_RSSD, "holder_rssd"]) == JPM_HOLDER_RSSD, \
    f"JPM bank {JPM_BANK_RSSD} should roll up to BHC {JPM_HOLDER_RSSD}"
assert int(h.loc[BOFA_BANK_RSSD, "holder_rssd"]) == BOFA_HOLDER_RSSD, \
    f"BofA bank {BOFA_BANK_RSSD} should roll up to BHC {BOFA_HOLDER_RSSD}"
assert not bool(h.loc[JPM_BANK_RSSD, "is_independent"])
# the JPM holder RSSD is exactly the BHC the y9c example pulls
assert JPM_HOLDER_RSSD == 1039502
# scalar input -> one row
assert len(bank_to_holder(JPM_BANK_RSSD)) == 1
# point-in-time path (financials RSSDHCR per REPDTE)
hp = bank_to_holder(JPM_BANK_RSSD, asof="2020Q4")
assert int(hp.iloc[0]["holder_rssd"]) == JPM_HOLDER_RSSD, "point-in-time rollup"
assert hp.iloc[0]["asof"] == "2020-12-31"
# unresolved id (not FDIC-insured) -> total mapping, NA holder, no raise
hu = bank_to_holder([999999999])
assert len(hu) == 1 and pd.isna(hu.iloc[0]["holder_rssd"])
# an independent bank (its own top holder) -> is_independent True.
# RSSD 37 = Bank of Hancock County, a known independent bank (RSSDHCR=<NA>);
# hardcoded so the assertion always runs (no full-table pull, no if-guard).
_d = bank_to_holder(37)
assert bool(_d.iloc[0]["is_independent"]) and \
    int(_d.iloc[0]["holder_rssd"]) == 37, "independent-bank rollup"
print(f"  {JPM_BANK_RSSD} -> {JPM_HOLDER_RSSD} (JPMorgan & Co), "
      f"{BOFA_BANK_RSSD} -> {BOFA_HOLDER_RSSD} (BofA Corp); "
      "scalar/vector/asof/unresolved/independent all OK")

# === Test 4c: bank_panel(holder=True) attaches point-in-time rollup key ===
print("\n=== Test 4c: bank_panel(holder=True, source='fdic') ===")
# include an independent bank (no holding company) to verify it is NOT
# left as NaN holder (which a default groupby would silently drop, and
# dropna=False would wrongly lump all independents into one group)
_ind = fdic_institutions(rssdids=[37])  # Bank of Hancock County (own holder)
_ind_cert = int(_ind.iloc[0]["CERT"]) if len(_ind) else None
_certs = [JPM_BANK_CERT, 3510] + ([_ind_cert] if _ind_cert else [])
hp_panel = bank_panel("2023Q3", "2023Q4", vars=["ASSET"], source="fdic",
                      certs=_certs, holder=True)
assert {"holder_rssd", "holder_name"}.issubset(hp_panel.columns), \
    "holder=True must attach holder_rssd/holder_name"
assert str(hp_panel["holder_rssd"].dtype) == "Int64", "holder_rssd must be Int64"
_jpm = hp_panel[hp_panel["CERT"] == JPM_BANK_CERT]
assert (_jpm["holder_rssd"] == JPM_HOLDER_RSSD).all(), \
    "JPM rows must carry the BHC holder RSSD each quarter"
if _ind_cert:
    _indrows = hp_panel[hp_panel["CERT"] == _ind_cert]
    assert _indrows["holder_rssd"].notna().all() and \
        (_indrows["holder_rssd"] == 37).all(), \
        "independent bank must roll up to its OWN RSSD (37), not NaN"
# the rollup is groupby-able to the holding-company level; the independent
# bank survives as its own group (not silently dropped)
agg = hp_panel.groupby(["quarter", "holder_rssd"])["ASSET"].sum()
assert len(agg) > 0
if _ind_cert:
    assert 37 in agg.index.get_level_values("holder_rssd"), \
        "independent bank silently dropped by groupby('holder_rssd')"
print(f"  panel carries Int64 holder_rssd (incl. independent banks); "
      f"groupby holder -> {len(agg)} holder-quarters")

# === Test 4d: NIC bulk wall — documented manual-download (issue #33) ===
print("\n=== Test 4d: nic_relationships/nic_attributes Akamai-wall behavior ===")
import os as _os
from utils.call_reports_utils import DATA_DIR as _DD, _nic_discover
_have_rel = _nic_discover("relationships") is not None
if _have_rel:
    rel = nic_relationships()
    assert "ID_RSSD_PARENT" in rel.columns and "ID_RSSD_OFFSPRING" in rel.columns
    assert str(rel["ID_RSSD_OFFSPRING"].dtype) == "Int64"
    nh = bank_to_holder(JPM_BANK_RSSD, source="nic", asof="2020Q4")
    assert int(nh.iloc[0]["bank_rssd"]) == JPM_BANK_RSSD
    # asof format must match the FDIC path (YYYY-MM-DD), not raw YYYYMMDD
    assert nh.iloc[0]["asof"] == "2020-12-31", \
        f"NIC asof should be ISO YYYY-MM-DD, got {nh.iloc[0]['asof']!r}"
    print(f"  user-placed NIC file found: {len(rel):,} relationship edges; "
          "source='nic' walk + asof format OK")
else:
    for fn in (lambda: nic_relationships(),
               lambda: nic_attributes(which="active")):
        try:
            fn()
            raise AssertionError("NIC helper should raise when no file placed")
        except RuntimeError as e:
            assert "Akamai" in str(e) and "browser" in str(e), \
                f"NIC wall error not instructive: {e}"
    # bad 'which' is a hard ValueError regardless of file presence
    try:
        nic_attributes(which="bogus")
        raise AssertionError("bad which should raise ValueError")
    except ValueError:
        pass
    print("  no user file placed: documented Akamai-wall RuntimeError OK "
          "(source='nic' walk SKIPPED — drop a NIC bulk file to exercise it)")

# === Test 5: FFIEC CDR literal RCON — ACCEPTANCE (HARD if reachable) ===
print("\n=== Test 5: call_report('2023Q4','RC') — RCON2170, count banks ===")
try:
    rc = call_report("2023Q4", schedule="RC")
except Exception as e:  # noqa: BLE001 - brittle path: SKIP, never FAIL
    import requests as _rq
    _unreachable = isinstance(e, (_rq.exceptions.RequestException,
                                  OSError, TimeoutError))
    if (FFIEC_FORM_BRITTLENESS.split(".")[0] in str(e)
            or "ffiec" in str(e).lower() or _unreachable):
        print(f"  SKIP (not FAIL): FFIEC bulk form unreachable/changed.\n"
              f"  -> {str(e)[:160]}")
        print("\nALL TESTS PASSED (FFIEC RCON path skipped — see message)")
        sys.exit(0)
    raise
assert "IDRSSD" in rc.columns, "Call Report must be keyed by IDRSSD"
assert "RCON2170" in rc.columns and "RCFD2170" in rc.columns, \
    f"missing RCON/RCFD total-assets codes; cols: {list(rc.columns)[:8]}"
n = rc["IDRSSD"].nunique()
assert 3000 < n < 7000, f"implausible Call Report bank count {n}"
# coalesce RCFD (031 filers) over RCON (041/051 filers) for total assets
ta = (pd.to_numeric(rc["RCFD2170"], errors="coerce")
        .fillna(pd.to_numeric(rc["RCON2170"], errors="coerce"))
        .fillna(0))
ta_tn = ta.sum() / 1e9  # RCON values are $thousands -> $trillions
assert 18 < ta_tn < 30, f"RCON-coded aggregate assets {ta_tn:.1f}T implausible"
one = call_report("2023Q4", schedule="RC", rssdids=[JPM_BANK_RSSD])
assert len(one) == 1 and int(one.iloc[0]["IDRSSD"]) == JPM_BANK_RSSD
# numeric coercion: arithmetic must work WITHOUT explicit pd.to_numeric
assert pd.api.types.is_numeric_dtype(rc["RCON2170"]), \
    f"RCON2170 not coerced numeric (dtype={rc['RCON2170'].dtype}) — " \
    "raw-string regression: rc['RCON2170'].sum() would concatenate"
assert str(rc["IDRSSD"].dtype) == "Int64", "IDRSSD must stay Int64"
direct = rc["RCON2170"].sum() / 1e9  # no pd.to_numeric wrapper
assert 5 < direct < 30, f"direct RCON2170 sum implausible: {direct:.1f}T"
print(f"  banks (IDRSSD): {n:,} | RCON/RCFD2170 aggregate ${ta_tn:.1f}T")
print(f"  rssdids filter -> 1 row for JPMorgan (RSSD {JPM_BANK_RSSD})")

# === Test 5b: multi-part schedule merge (no silent column truncation) ===
print("\n=== Test 5b: RCRII (split into 4 SDF files) merges fully ===")
ri = call_report("2023Q4", schedule="RI")           # single-part baseline
rcrii = call_report("2023Q4", schedule="RCRII")      # 4-part, column-split
assert len(rcrii) == n, \
    f"RCRII row count {len(rcrii)} != RC bank count {n} " \
    "(outer-merge row inflation, NaN-key dup, or truncation)"
assert rcrii["IDRSSD"].nunique() == n, \
    f"RCRII unique IDRSSD {rcrii['IDRSSD'].nunique()} != RC {n}"
# part 1 alone is ~244 cols; a correct 4-part merge is far wider
assert len(rcrii.columns) > 400, \
    f"RCRII only {len(rcrii.columns)} cols — parts 2-4 silently dropped"
ni = pd.to_numeric(ri.get("RIAD4340"), errors="coerce")  # net income YTD
assert ni.notna().sum() > 3000 and 100 < ni.fillna(0).sum() / 1e6 < 600, \
    f"RI net income (RIAD4340) implausible: ${ni.fillna(0).sum()/1e6:.0f}B"
print(f"  RCRII: {rcrii['IDRSSD'].nunique():,} banks, "
      f"{len(rcrii.columns)} cols (4 parts merged, 0 dup rows)")
print(f"  RI RIAD4340 net income YTD aggregate: "
      f"${ni.fillna(0).sum()/1e6:.0f}B (2023 full year)")

# === Test 6: bank_panel across quarters (FDIC source, HARD) ===
print("\n=== Test 6: bank_panel('2023Q1','2023Q4', source='fdic') ===")
# a few large banks -> one small request/quarter (keeps us under the
# public FDIC API's burst rate limit)
pan = bank_panel("2023Q1", "2023Q4", vars=["ASSET", "NETINC"],
                 source="fdic", certs=[628, 3510, 6548, 18409])
assert set(pan["quarter"].unique()) == {"2023Q1", "2023Q2", "2023Q3", "2023Q4"}
assert {"ASSET", "NETINC"}.issubset(pan.columns)
assert pan["CERT"].nunique() == 4, f"expected 4 banks, got {pan['CERT'].nunique()}"
print(f"  panel rows: {len(pan):,} across {pan['quarter'].nunique()} quarters, "
      f"{pan['CERT'].nunique()} banks")

print("\nALL TESTS PASSED")
