"""Test sec-funds skill — N-CEN / NPORT-P / N-1A fee parsing from live EDGAR.

Validates the paths actually used in fund research, across >=3 fund families
(per the acceptance criteria in issue #3):
  1. Filing enumeration via the free submissions API (no WRDS)
  2. N-CEN parse: registrant + per-series census (3 families)
  3. NPORT-P parse: monthly holdings table (3 families)
  4. N-1A fee table: per-share-class rr: XBRL fee ratios
  5. DC-plan share-class heuristic (documented as a heuristic, not a flag)

Run from project root:
    PYTHONPATH=code python3 test_scripts/test_sec_funds.py
"""
import sys

# Trust-level registrant CIKs for three distinct fund families.
FAMILIES = {
    "Vanguard Index Funds": 36405,
    "Fidelity Select Portfolios": 320351,
    "T. Rowe Price (New Income)": 80249,
}

# === Test 1: filing enumeration (submissions API, no WRDS) ===
print("=== Test 1: list_fund_filings — N-CEN / NPORT-P / 485BPOS counts ===")
from utils.sec_funds_utils import list_fund_filings
for name, cik in FAMILIES.items():
    df = list_fund_filings(cik)
    forms = df["form"].value_counts()
    n_ncen = int(forms.get("N-CEN", 0))
    n_nport = int(forms.get("NPORT-P", 0))
    assert n_ncen >= 1, f"{name}: no N-CEN filings found"
    assert n_nport >= 1, f"{name}: no NPORT-P filings found"
    print(f"  {name}: {len(df)} filings "
          f"(N-CEN={n_ncen}, NPORT-P={n_nport}, "
          f"485BPOS={int(forms.get('485BPOS', 0))})")

# === Test 2: N-CEN parse across 3 families ===
print("\n=== Test 2: download_ncen — registrant + per-series census ===")
from utils.sec_funds_utils import download_ncen
for name, cik in FAMILIES.items():
    nc = download_ncen(cik)
    reg = nc["registrant"]
    ser = nc["series"]
    assert reg.get("registrantFullName"), f"{name}: no registrant name"
    assert not ser.empty, f"{name}: no series parsed from N-CEN"
    assert "fund_name" in ser.columns and ser["fund_name"].notna().any(), \
        f"{name}: series rows missing fund_name"
    print(f"  {name}: '{reg['registrantFullName']}' "
          f"({reg.get('totalSeries')} series declared, "
          f"{len(ser)} parsed; accn {nc['accession']})")
    print(f"    sample series: {ser['fund_name'].dropna().iloc[0]} | "
          f"sec_lending={ser['is_securities_lending'].iloc[0]} | "
          f"advisers={str(ser['advisers'].iloc[0])[:40]}")

# === Test 3: NPORT-P monthly holdings across 3 families ===
print("\n=== Test 3: download_nport — monthly portfolio holdings ===")
from utils.sec_funds_utils import download_nport
for name, cik in FAMILIES.items():
    np_ = download_nport(cik)
    gi, fi, hold = np_["gen_info"], np_["fund_info"], np_["holdings"]
    assert gi.get("seriesName"), f"{name}: NPORT genInfo missing seriesName"
    assert not hold.empty, f"{name}: no holdings parsed from NPORT-P"
    assert "valUSD" in hold.columns, f"{name}: holdings missing valUSD"
    top = hold.sort_values("valUSD", ascending=False).iloc[0]
    print(f"  {name}: series='{gi['seriesName']}' "
          f"period={gi.get('repPdEnd')} netAssets={fi.get('netAssets')}")
    print(f"    {len(hold)} positions; top: {str(top.get('name'))[:32]} "
          f"(valUSD={top['valUSD']:,.0f}, {top.get('assetCat')})")

# === Test 4: N-1A per-class fee table (rr: XBRL) ===
print("\n=== Test 4: n1a_fee_table — per-share-class fee ratios ===")
from utils.sec_funds_utils import list_fund_filings, n1a_fee_table
fee_found = 0
for name, cik in FAMILIES.items():
    # Walk recent 485BPOS until one carries Risk/Return XBRL.
    cands = list_fund_filings(cik, form="485BPOS")["accession"].tolist()[:8]
    for accn in cands:
        try:
            wide = n1a_fee_table(cik, accession=accn)
        except LookupError:
            continue
        if wide.empty:
            continue
        cols = [c for c in ("mgmt_fee", "net_exp_ratio", "gross_exp_ratio")
                if c in wide.columns]
        assert cols, f"{name}: fee table has no expense columns: {list(wide.columns)}"
        print(f"  {name}: {len(wide)} share classes, "
              f"accn {accn} ({wide.attrs.get('rr_document')})")
        print(f"    fields: {[c for c in wide.columns if c not in ('series_id','class_id','class_member')]}")
        fee_found += 1
        break
assert fee_found >= 2, \
    f"expected rr fee tables for >=2 families, got {fee_found}"
print(f"  -> parsed fee tables for {fee_found}/3 families")

# === Test 5: DC-plan share-class heuristic ===
print("\n=== Test 5: flag_dc_target_funds — share-class name heuristic ===")
from utils.sec_funds_utils import flag_dc_target_funds
sample = ["Class R6", "R1", "Class R7", "R8", "Investor Shares", "Class K",
          "Retirement Class", "Admiral Shares", "Institutional"]
flagged = flag_dc_target_funds(sample)
got = set(flagged.loc[flagged["is_dc_share_class"], "class_name"])
expect = {"Class R6", "R1", "Class R7", "R8", "Class K", "Retirement Class"}
assert got == expect, f"DC heuristic mismatch: got {got}, expected {expect}"
print(f"  DC-tagged: {sorted(got)}")
print(f"  not-DC:    {sorted(set(sample) - got)}")

print("\nALL TESTS PASSED")
