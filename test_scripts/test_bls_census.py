"""Test bls-census skill — BLS / Census / SSA free panels (issue #4).

Acceptance: pull one BLS series, one ACS variable, one Census CPS extract;
SSA tables key-free.

Run from project root:
    PYTHONPATH=code python3 test_scripts/test_bls_census.py

Key handling (verified live, May 2026):
  * BLS works WITH NO KEY — Tests 1-2 are hard requirements.
  * Census now requires a free CENSUS_API_KEY for every request. Tests 3-4
    run fully if CENSUS_API_KEY is set, else SKIP (not FAIL) after asserting
    the helper raises the correct instructive error.
  * SSA 403s datacenter IPs (Akamai). Test 5 is best-effort: PASS on data,
    SKIP on the documented 403/network block.
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()

# === Test 1: bls_series — single series, keyless ===
print("=== Test 1: bls_series(LNS11300000) — LFPR 16+, no key ===")
from utils.bls_census_utils import bls_series

df = bls_series("LNS11300000", 2018, 2023)
assert not df.empty, "BLS returned no rows for LNS11300000"
assert {"series_id", "year", "period", "date", "value"} <= set(df.columns), \
    f"missing expected columns: {list(df.columns)}"
assert df["value"].notna().any(), "all BLS values are NaN"
assert df["value"].between(55, 70).mean() > 0.8, \
    f"LFPR out of plausible 55-70 range: {df['value'].describe()}"
last = df.sort_values("date").iloc[-1]
print(f"  {len(df)} obs, {df['series_id'].nunique()} series; "
      f"latest {last['periodName']} {last['year']} = {last['value']}")

# === Test 2: bls_series — multiple series + cache round-trip ===
print("\n=== Test 2: bls_series multi-series + parquet cache ===")
multi = bls_series(["LNS11300000", "LNS14000000", "CUUR0000SA0"], 2020, 2023)
got = set(multi["series_id"].unique())
assert {"LNS11300000", "LNS14000000", "CUUR0000SA0"} <= got, \
    f"missing series in multi-fetch: {got}"
cached = bls_series(["LNS11300000", "LNS14000000", "CUUR0000SA0"], 2020, 2023)
assert cached.equals(multi), "cache round-trip changed the DataFrame"
print(f"  3 series, {len(multi)} obs; cache round-trip identical")

# === Test 3: acs_county — one ACS variable (key-gated) ===
print("\n=== Test 3: acs_county — median household income ===")
from utils.bls_census_utils import acs_county

if os.getenv("CENSUS_API_KEY"):
    acs = acs_county(2022, ["B19013_001E"], state="12")  # Florida counties
    assert not acs.empty, "ACS returned no rows"
    assert "B19013_001E" in acs.columns, f"missing ACS var: {list(acs.columns)}"
    inc = acs["B19013_001E"].astype(float)
    inc = inc[inc > 0]
    assert (inc.between(20000, 200000)).mean() > 0.8, \
        f"median income out of range: {inc.describe()}"
    print(f"  {len(acs)} FL counties; "
          f"median HH income range ${inc.min():,.0f}-${inc.max():,.0f}")
else:
    from utils.bls_census_utils import census_get
    try:
        census_get(2022, "acs/acs5", ["B19013_001E"], "county:*", "state:12")
        print("  UNEXPECTED: census_get succeeded without a key")
        sys.exit(1)
    except RuntimeError as e:
        assert "CENSUS_API_KEY" in str(e), f"wrong error: {e}"
    print("  SKIP: CENSUS_API_KEY not set; helper raised the correct "
          "instructive error (Census key is mandatory).")

# === Test 4: cps_basic_monthly — one CPS extract (key-gated) ===
print("\n=== Test 4: cps_basic_monthly(2023, 'jan') ===")
from utils.bls_census_utils import cps_basic_monthly

if os.getenv("CENSUS_API_KEY"):
    cps = cps_basic_monthly(2023, "jan", state="12")
    assert not cps.empty, "CPS returned no rows"
    assert "PRTAGE" in cps.columns and "PEMLR" in cps.columns, \
        f"missing CPS core vars: {list(cps.columns)}"
    age = cps["PRTAGE"].astype(int)
    assert age.between(-1, 100).all(), f"PRTAGE out of range: {age.describe()}"
    print(f"  {len(cps)} FL person records; "
          f"age {age[age >= 0].min()}-{age.max()}, "
          f"{cps['PEMLR'].nunique()} PEMLR levels")
else:
    try:
        cps_basic_monthly(2023, "jan", state="12")
        print("  UNEXPECTED: cps_basic_monthly succeeded without a key")
        sys.exit(1)
    except RuntimeError as e:
        assert "CENSUS_API_KEY" in str(e), f"wrong error: {e}"
    print("  SKIP: CENSUS_API_KEY not set; helper raised the correct "
          "mandatory-key error.")

# === Test 4b: retirement_hazard_by_cohort — keyless proxy ===
print("\n=== Test 4b: retirement_hazard_by_cohort(2015, 2023) ===")
from utils.bls_census_utils import retirement_hazard_by_cohort

h = retirement_hazard_by_cohort(2015, 2023)
assert not h.empty, "retirement_hazard_by_cohort returned no rows"
assert {"year", "lfpr_55plus", "exit_proxy"} <= set(h.columns), \
    f"missing expected columns: {list(h.columns)}"
assert h["exit_proxy"].notna().any(), "exit_proxy is all-NaN"
assert h["lfpr_55plus"].dropna().between(30, 50).all(), \
    f"55+ LFPR out of plausible 30-50 range: {h['lfpr_55plus'].describe()}"
yr = h.dropna(subset=["exit_proxy"]).iloc[-1]
print(f"  {len(h)} years; latest {int(yr['year'])}: "
      f"lfpr_55plus={yr['lfpr_55plus']:.1f} exit_proxy={yr['exit_proxy']:+.2f}")

# === Test 5: ssa_period_life_table — keyless, best-effort ===
print("\n=== Test 5: ssa_period_life_table (no key; SSA may 403 on DC IPs) ===")
from utils.bls_census_utils import ssa_period_life_table

try:
    tables = ssa_period_life_table()
    assert tables and not tables[0].empty, "SSA returned no usable table"
    print(f"  OK: {len(tables)} tables; first shape {tables[0].shape}")
except RuntimeError as e:
    msg = str(e)
    assert "403" in msg or "SSA" in msg, f"unexpected SSA error: {msg}"
    print(f"  SKIP (documented limit): {msg[:120]}")

print("\nALL TESTS PASSED")
