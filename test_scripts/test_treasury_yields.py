"""Test treasury-yields skill — GSW + Liu-Wu zero-coupon Treasury curves.

Hits only the small GSW nominal CSV (~17 MB) so the test is fast and needs no
credentials. Liu-Wu's Google-Sheets export is rate-limited and brittle, so it's
gated behind TREASURY_TEST_LIU_WU=1.
"""
import os
import tempfile

import numpy as np
import pandas as pd

# === Test 1: registry is well-formed ===
print("=== Test 1: list_datasets() ===")
from utils.treasury_yields_utils import list_datasets, DATASETS
ds = list_datasets()
for k in ("gsw_nominal", "gsw_tips", "liu_wu_daily", "liu_wu_monthly"):
    assert k in ds, f"missing dataset {k}"
expected_fed_host = "federalreserve.gov"
expected_lw_host = "docs.google.com"
assert expected_fed_host in ds["gsw_nominal"]["url"], "bad GSW nominal URL"
assert expected_fed_host in ds["gsw_tips"]["url"], "bad GSW TIPS URL"
assert expected_lw_host in ds["liu_wu_daily"]["url"], "bad Liu-Wu daily URL"
print(f"  datasets: {list(ds)}")

# === Test 2: gsw_nominal() downloads + parses ===
print("\n=== Test 2: gsw_nominal() shape + schema ===")
from utils.treasury_yields_utils import gsw_nominal
with tempfile.TemporaryDirectory() as cache:
    df = gsw_nominal(cache_dir=cache)
    required = ["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2",
                "SVENY01", "SVENY05", "SVENY10", "SVENY30"]
    for col in required:
        assert col in df.columns, f"missing column {col}"
    assert df.index.name == "date", f"expected DatetimeIndex named 'date', got {df.index.name}"
    assert isinstance(df.index, pd.DatetimeIndex), "index must be DatetimeIndex"
    assert len(df) > 15000, f"expected >15k daily rows from 1961+; got {len(df)}"
    assert df.index.min() <= pd.Timestamp("1962-01-01"), f"sample start too late: {df.index.min()}"
    # TAU2 sentinel must be normalized to NaN
    assert not np.isclose(df["TAU2"].dropna(), -999.99).any(), "TAU2 sentinel -999.99 leaked"
    # Sentinel should appear in pre-1980 (TAU2 should be NaN there, finite post-1980)
    pre = df.loc[:"1979-12-31", "TAU2"]
    post = df.loc["1985-01-01":"1990-12-31", "TAU2"]
    assert pre.isna().all(), f"pre-1980 TAU2 should be NaN; got {pre.dropna().head()}"
    assert post.notna().mean() > 0.95, f"post-1980 TAU2 should be finite; got {post.notna().mean():.2%}"
    print(f"  {len(df)} rows, {df.index.min().date()}..{df.index.max().date()}, "
          f"{df.shape[1]} columns")

    # === Test 3: Svensson closed form reproduces SVENY10 ===
    print("\n=== Test 3: Svensson closed form matches SVENY10 ===")
    from utils.treasury_yields_utils import _svensson_yield
    # Pick a recent Svensson-era date (skip pre-1980 NS, skip latest in case of NaN)
    svensson_rows = df.dropna(subset=["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2", "SVENY10"])
    svensson_rows = svensson_rows.loc["2000-01-01":]
    assert len(svensson_rows) > 1000, f"too few Svensson rows: {len(svensson_rows)}"
    sample = svensson_rows.iloc[len(svensson_rows) // 2]   # middle of the panel
    reconstructed = float(_svensson_yield(
        10.0, sample.BETA0, sample.BETA1, sample.BETA2, sample.BETA3,
        sample.TAU1, sample.TAU2))
    published = float(sample.SVENY10)
    diff = abs(reconstructed - published)
    assert diff < 1e-4, (
        f"Svensson reconstruction off by {diff:.2e} bp at {sample.name}: "
        f"computed {reconstructed:.6f}, published {published:.6f}"
    )
    print(f"  10y reconstruction at {sample.name.date()}: computed {reconstructed:.6f}, "
          f"published {published:.6f}, diff {diff:.2e}")

    # === Test 4: yield_on integer fast path matches column exactly ===
    print("\n=== Test 4: yield_on integer fast path ===")
    from utils.treasury_yields_utils import yield_on
    test_date = sample.name
    direct = yield_on(test_date, 10, source="gsw_nominal", cache_dir=cache)
    assert direct == published, f"integer fast path returned {direct}, expected {published}"
    # Continuous maturity matches closed form
    cont = yield_on(test_date, 10.0, source="gsw_nominal", cache_dir=cache)
    # 10.0 also hits the integer fast path; check a true non-integer
    cont75 = yield_on(test_date, 7.5, source="gsw_nominal", cache_dir=cache)
    expected75 = float(_svensson_yield(
        7.5, sample.BETA0, sample.BETA1, sample.BETA2, sample.BETA3,
        sample.TAU1, sample.TAU2))
    assert abs(cont75 - expected75) < 1e-10, f"7.5y mismatch: {cont75} vs {expected75}"
    print(f"  10y exact match; 7.5y closed-form {cont75:.6f}")

    # === Test 5: pre-1980 NS path returns finite yields ===
    print("\n=== Test 5: pre-1980 Nelson-Siegel path ===")
    ns_rows = df.loc[:"1979-12-31"].dropna(subset=["BETA0", "BETA1", "BETA2", "TAU1", "SVENY05"])
    assert len(ns_rows) > 100, f"expected pre-1980 NS rows; got {len(ns_rows)}"
    ns_sample = ns_rows.iloc[len(ns_rows) // 2]
    assert pd.isna(ns_sample.TAU2), f"pre-1980 TAU2 should be NaN; got {ns_sample.TAU2}"
    # BETA3 should be 0 (Nelson-Siegel)
    assert ns_sample.BETA3 == 0 or pd.isna(ns_sample.BETA3), \
        f"pre-1980 BETA3 should be 0/NaN; got {ns_sample.BETA3}"
    ns_y5 = float(_svensson_yield(
        5.0, ns_sample.BETA0, ns_sample.BETA1, ns_sample.BETA2,
        ns_sample.BETA3 if pd.notna(ns_sample.BETA3) else 0.0,
        ns_sample.TAU1, ns_sample.TAU2))
    assert np.isfinite(ns_y5), f"NS yield non-finite at {ns_sample.name}: {ns_y5}"
    assert 0 < ns_y5 < 30, f"NS 5y yield out of plausible range: {ns_y5}"
    diff5 = abs(ns_y5 - float(ns_sample.SVENY05))
    assert diff5 < 1e-4, f"NS reconstruction off by {diff5:.2e} at {ns_sample.name}"
    print(f"  NS 5y at {ns_sample.name.date()}: {ns_y5:.6f} (published {ns_sample.SVENY05:.6f})")

    # === Test 6: ns_factors returns published params with sentinel cleaned ===
    print("\n=== Test 6: ns_factors() ===")
    from utils.treasury_yields_utils import ns_factors
    params = ns_factors(start="2020-01-01", end="2023-12-31", source="gsw_nominal",
                        cache_dir=cache)
    assert set(["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]).issubset(params.columns)
    assert len(params) > 800, f"expected ~1000 daily rows 2020-2023; got {len(params)}"
    assert not np.isclose(params["TAU2"].dropna(), -999.99).any(), "sentinel leaked through ns_factors"
    print(f"  {len(params)} param rows; BETA0 range {params.BETA0.min():.2f}..{params.BETA0.max():.2f}")

    # === Test 7: yield_on rejects bad inputs ===
    print("\n=== Test 7: input validation ===")
    try:
        yield_on(test_date, -1, source="gsw_nominal", cache_dir=cache)
        raise AssertionError("expected ValueError for negative maturity")
    except ValueError:
        pass
    try:
        yield_on(test_date, 10, source="liu_wu_daily", cache_dir=cache)
        raise AssertionError("expected ValueError for unsupported source")
    except ValueError:
        pass
    try:
        yield_on("1850-01-01", 10, source="gsw_nominal", cache_dir=cache)
        raise AssertionError("expected KeyError for date outside range")
    except KeyError:
        pass
    print("  ValueError/KeyError raised as expected")

# === Test 8: Liu-Wu (gated; Google Sheets is rate-limited) ===
if os.environ.get("TREASURY_TEST_LIU_WU") == "1":
    print("\n=== Test 8: liu_wu('monthly') ===")
    from utils.treasury_yields_utils import liu_wu
    with tempfile.TemporaryDirectory() as cache:
        lw = liu_wu(freq="monthly", cache_dir=cache)
        assert isinstance(lw.index, pd.DatetimeIndex), f"index must be DatetimeIndex; got {type(lw.index)}"
        assert lw.index.name == "date", f"index name must be 'date'; got {lw.index.name}"
        assert len(lw) > 600, f"expected ~700+ monthly rows; got {len(lw)}"
        # Maturity columns are integer-string month labels: '1', '2', ..., '360'.
        assert "1" in lw.columns and "12" in lw.columns and "360" in lw.columns, (
            f"missing expected maturity columns; got {list(lw.columns)[:8]}..."
        )
        # Sanity-check a known yield value: first row should be 1961-06.
        assert lw.index.min().year == 1961, f"sample start expected 1961; got {lw.index.min()}"
        y12 = lw["12"].dropna()
        assert (y12 > 0).all() and (y12 < 25).all(), "12-month yields out of plausible range"
        print(f"  Liu-Wu monthly: {len(lw)} rows, {lw.shape[1]} maturity columns, "
              f"{lw.index.min().date()}..{lw.index.max().date()}")
else:
    print("\n=== Test 8: liu_wu (skipped; set TREASURY_TEST_LIU_WU=1 to enable) ===")

print("\nALL TESTS PASSED")
