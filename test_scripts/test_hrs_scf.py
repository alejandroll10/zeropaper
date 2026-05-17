"""Test hrs-scf skill — SCF (no key) + HRS registration-walled (issue #5).

Acceptance:
  * Pull one SCF year with NO key, verify implicate structure and the
    weight-scaling invariant (sum of wgt over all 5 implicates ~= US
    household population).
  * MI-combine (within-implicate then average) gives plausible 2022 net
    worth (median ~$190k, mean ~$1.06M per the Fed 2022 bulletin).
  * Verify the HRS download path: with no file and no credentials,
    load_rand_hrs / hrs_retirement_panel must raise the instructive
    registration RuntimeError (SKIP, not FAIL — HRS is registration-walled
    by design). If a user-placed RAND HRS file exists, exercise the reshape.

Run from project root:
    PYTHONPATH=code python3 test_scripts/test_hrs_scf.py
"""
import os

from dotenv import load_dotenv

load_dotenv()

# === Test 1: scf_summary — one SCF year, NO key ===
print("=== Test 1: scf_summary(2022) — no key ===")
from utils.hrs_scf_utils import scf_summary

df = scf_summary(2022)
assert not df.empty, "SCF summary returned no rows"
assert {"yy1", "y1", "wgt", "networth", "income", "retqliq"} <= set(df.columns), \
    f"missing expected SCF columns: {list(df.columns)[:20]}"
n_imp = (df["y1"].astype("int64") % 10).nunique()
assert n_imp == 5, f"expected 5 implicates, got {n_imp}"
print(f"  {len(df)} rows = {df['yy1'].nunique()} households x {n_imp} implicates")

# === Test 2: the SCF weight-scaling invariant ===
print("\n=== Test 2: sum(wgt) over all 5 implicates ~= US households ===")
tot = df["wgt"].sum()
assert 1.2e8 < tot < 1.45e8, \
    f"sum(wgt) over 5 implicates = {tot:,.0f}, not ~1.31e8 (US households)"
one_imp = df[(df["y1"].astype("int64") % 10) == 1]["wgt"].sum()
assert abs(one_imp - tot / 5) / tot < 0.01, \
    "single-implicate wgt sum should be ~1/5 of the all-implicate sum"
print(f"  all 5: {tot:,.0f}   one implicate: {one_imp:,.0f} (~1/5) — invariant holds")

# === Test 3: MI-combined net worth (within-implicate then averaged) ===
print("\n=== Test 3: scf_combine_implicates — 2022 net worth ===")
from utils.hrs_scf_utils import scf_combine_implicates

med = scf_combine_implicates(df, "networth", stat="median")["networth"].iloc[0]
mean = scf_combine_implicates(df, "networth", stat="mean")["networth"].iloc[0]
assert 1.5e5 < med < 2.4e5, f"2022 median net worth implausible: {med:,.0f}"
assert 8e5 < mean < 1.3e6, f"2022 mean net worth implausible: {mean:,.0f}"
by = scf_combine_implicates(df, "retqliq", by="agecl", stat="median")
assert by["agecl"].nunique() >= 5 and by["retqliq"].max() > 0, \
    "retqliq-by-agecl looks wrong"
print(f"  median net worth ${med:,.0f}, mean ${mean:,.0f}; "
      f"retqliq by {by['agecl'].nunique()} age classes OK")

# === Test 3b: cache round-trip ===
print("\n=== Test 3b: SCF parquet cache round-trip ===")
assert scf_summary(2022).equals(df), "cache round-trip changed the DataFrame"
print("  identical on re-read")

# === Test 3c: scf_retirement_by_cohort — headline issue-#5 convenience ===
print("\n=== Test 3c: scf_retirement_by_cohort(2022) ===")
from utils.hrs_scf_utils import scf_retirement_by_cohort, SCF_AGECL

rc = scf_retirement_by_cohort(2022, stat="mean")  # mean has the lifecycle hump
assert {"agecl", "age_band", "retqliq", "irakh"} <= set(rc.columns), \
    f"missing expected retirement-cohort columns: {list(rc.columns)}"
assert rc["agecl"].nunique() == 6, f"expected 6 age classes, got {rc['agecl'].tolist()}"
assert set(rc["age_band"]) == set(SCF_AGECL.values()), \
    f"age_band labels wrong: {rc['age_band'].tolist()}"
rc = rc.sort_values("agecl")
# Mean retqliq is hump-shaped over the lifecycle: peaks at pre-/at-retirement
# (agecl 4-5), and the youngest cohort holds far less than the peak.
peak = rc.loc[rc["retqliq"].idxmax(), "agecl"]
assert peak in (4, 5), f"mean retqliq peaks at age class {peak}, expected 4-5"
assert rc.iloc[0]["retqliq"] < rc["retqliq"].max(), \
    "youngest cohort should hold less retirement wealth than the peak"
print(f"  6 cohorts; mean retqliq peaks at age band "
      f"{rc.loc[rc['retqliq'].idxmax(), 'age_band']} "
      f"(${rc['retqliq'].max():,.0f}), youngest "
      f"${rc.iloc[0]['retqliq']:,.0f}")

# === Test 4: HRS download path — registration-walled by design ===
print("\n=== Test 4: load_rand_hrs / hrs_retirement_panel ===")
from utils.hrs_scf_utils import load_rand_hrs, hrs_retirement_panel

try:
    panel = hrs_retirement_panel()
    # Only reachable if the user placed a RAND HRS file in data/hrs_scf/hrs/.
    assert {"hhidpn", "wave"} <= set(panel.columns), \
        f"HRS panel missing id/wave: {list(panel.columns)}"
    assert panel["wave"].nunique() >= 1, "HRS panel has no waves"
    print(f"  user RAND HRS file found: {len(panel)} person-wave rows, "
          f"{panel['wave'].nunique()} waves — reshape OK")
except RuntimeError as e:
    msg = str(e)
    assert "hrsdata.isr.umich.edu" in msg and "data/hrs_scf/hrs" in msg, \
        f"HRS error not instructive enough: {msg[:200]}"
    # load_rand_hrs raises the same instructive error directly.
    try:
        load_rand_hrs()
        print("  UNEXPECTED: load_rand_hrs succeeded with no file")
        raise SystemExit(1)
    except RuntimeError as e2:
        assert "registration" in str(e2).lower(), f"wrong error: {e2}"
    print("  SKIP (registration-walled by design): helper raised the exact "
          "registration + manual-placement instructions, no silent failure.")

print("\nALL TESTS PASSED")
