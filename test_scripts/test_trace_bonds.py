"""Test trace-bonds skill — trade-level TRACE via WRDS (issue #8 Tier 2).

Needs the WRDS server up and a subscription that includes TRACE. If no trade
source is readable (TRACE not in this account's subscription), the test SKIPS
gracefully (exit 0) rather than failing — that is the documented fallback.

Hits a single in-sample date and small CUSIP sets to stay fast.
"""
import sys

from utils.trace_bonds_utils import (trace_available, trace_trades, bond_daily_panel,
                                     dealer_inventory_proxy, link_bond_to_crsp)

D = "2023-06-15"

# === Test 1: subscription probe ===
print("=== Test 1: trace_available() ===")
av = trace_available()
print(f"  {av}")
trade_ok = any(av.get(k) for k in ("wrds_clean_enhanced", "wrds_clean_standard", "raw_enhanced", "raw_standard"))
if not trade_ok:
    print("  No readable TRACE trade source for this WRDS account — SKIP "
          "(use the open-bond-pricing skill instead).")
    sys.exit(0)

# === Test 2: trace_trades pulls trade-level rows ===
print("\n=== Test 2: trace_trades(one day, limit) ===")
tr = trace_trades(D, D, limit=1000)
for col in ("cusip_id", "trd_exctn_dt", "rptd_pr", "entrd_vol_qt", "rpt_side_cd", "cntra_mp_id"):
    assert col in tr.columns, f"missing column {col}: {list(tr.columns)}"
assert len(tr) > 0, "no trades returned"
print(f"  source={tr.attrs.get('trace_source')}, rows={len(tr)}")
cusips = tr["cusip_id"].dropna().value_counts().head(3).index.tolist()
assert cusips, "no non-null cusips in sample"
print(f"  active cusips: {cusips}")

# === Test 3: bond_daily_panel computes a sane VWAP ===
print("\n=== Test 3: bond_daily_panel(one day, 3 cusips) ===")
p = bond_daily_panel(D, D, cusips=cusips)
assert {"cusip_id", "trd_exctn_dt", "vwap_prc", "volume", "n_trades"} <= set(p.columns), list(p.columns)
assert len(p) >= 1, "no bond-day rows returned"
assert p["vwap_prc"].notna().any(), "all vwap_prc rows are null"
assert (p["vwap_prc"].dropna() > 0).all(), "vwap_prc has non-positive values"
assert (p["n_trades"] > 0).all() and (p["volume"] > 0).all()
print(p.to_string())

# === Test 4: dealer_inventory_proxy nets out ===
print("\n=== Test 4: dealer_inventory_proxy(one day) ===")
di = dealer_inventory_proxy(D, D)
assert {"trd_exctn_dt", "dealer_buy_vol", "dealer_sell_vol", "net_inventory_chg",
        "customer_trades"} <= set(di.columns), list(di.columns)
assert len(di) == 1, f"expected one market-wide day row, got {len(di)}"
row = di.iloc[0]
assert abs(row["net_inventory_chg"] - (row["dealer_buy_vol"] - row["dealer_sell_vol"])) < 1.0, \
    "net_inventory_chg should equal dealer_buy_vol - dealer_sell_vol"
print(f"  net dealer inventory change on {D}: {row['net_inventory_chg']:,.0f} par "
      f"over {int(row['customer_trades']):,} customer trades")

# === Test 5: link_bond_to_crsp resolves permno ===
print("\n=== Test 5: link_bond_to_crsp(cusips) ===")
if av.get("bondcrsp_link"):
    lk = link_bond_to_crsp(cusips=cusips)
    assert {"cusip", "permno", "permco"} <= set(lk.columns), list(lk.columns)
    print(f"  linked {len(lk)} cusips; sample permnos: {lk['permno'].dropna().tolist()[:3]}")
else:
    print("  bondcrsp_link not readable — skipped")

print("\nALL TESTS PASSED")
