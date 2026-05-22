"""Test open-bond-pricing skill — OSBAP corporate-bond data, no WRDS / no auth.

Hits only the small (~2 MB) long-short factor file so the test is fast and
needs no credentials. The heavy panels (ml_panel ~886 MB, daily_trace ~1.8 GB)
go through the same code path and are not downloaded here.
"""
import os
import tempfile

# === Test 1: registry is well-formed ===
print("=== Test 1: list_datasets() ===")
from utils.open_bond_pricing_utils import list_datasets, DATASETS
ds = list_datasets()
for k in ("factors", "ml_panel", "ml_predictions", "daily_trace"):
    assert k in ds, f"missing dataset {k}"
    assert ds[k]["url"].startswith("https://openbondassetpricing.com/"), f"bad url for {k}"
print(f"  datasets: {list(ds)}")

# === Test 2: download + read the small factor file (excess VW long-short returns) ===
print("\n=== Test 2: get_bond_factors('excess') ===")
from utils.open_bond_pricing_utils import get_bond_factors
with tempfile.TemporaryDirectory() as cache:
    f = get_bond_factors("excess", cache_dir=cache)
    assert "date" in f.columns, f"no date column: {list(f.columns)[:5]}"
    assert f.shape[1] > 300, f"expected ~341 factor columns, got {f.shape[1]}"
    assert len(f) > 200, f"factor series too short: {len(f)} rows"
    print(f"  excess LS factors: {f.shape[0]} months x {f.shape[1]-1} factors, "
          f"{f['date'].min()}..{f['date'].max()}")

    # === Test 3: weighting variants resolve to different members (cached zip reused) ===
    print("\n=== Test 3: duradj + turnover variants ===")
    d = get_bond_factors("duradj", cache_dir=cache)
    t = get_bond_factors("turnover", cache_dir=cache)
    assert d.shape[1] > 300 and t.shape[1] > 300, "variant panels malformed"
    # cached zip should exist exactly once
    zips = [n for n in os.listdir(cache) if n.endswith(".zip")]
    assert len(zips) == 1, f"expected 1 cached zip, found {zips}"
    print(f"  duradj cols={d.shape[1]-1}, turnover cols={t.shape[1]-1}; cached zip: {zips[0]}")

# === Test 4: bad weighting raises ===
print("\n=== Test 4: invalid weighting rejected ===")
try:
    get_bond_factors("nonsense")
    raise AssertionError("expected ValueError for bad weighting")
except ValueError:
    print("  ValueError raised as expected")

print("\nALL TESTS PASSED")
