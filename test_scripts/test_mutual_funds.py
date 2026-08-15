"""Test mutual-funds skill — direct WRDS query + key helpers.

Requires the persistent WRDS server on its host-wide Unix socket.
Uses small queries (LIMIT, single year) to keep test fast.
"""
import sys

# === Test 0: WRDS server reachable ===
print("=== Test 0: WRDS server ping ===")
from utils.wrds_client import wrds_ping
assert wrds_ping(), "WRDS host daemon is unavailable"
print("  ping OK")

# === Test 1: a few CRSP MFDB tables exist ===
print("\n=== Test 1: list crsp_q_mutualfunds tables ===")
from utils.wrds_client import wrds_list_tables
tables = wrds_list_tables('crsp_q_mutualfunds')
need = {'monthly_tna_ret_nav', 'fund_hdr', 'fund_style', 'fund_fees', 'portnomap', 'holdings'}
assert need.issubset(set(tables)), f"missing tables: {need - set(tables)}"
print(f"  {len(tables)} tables present; required tables found")

# === Test 2: small returns query ===
print("\n=== Test 2: small monthly_tna_ret_nav query ===")
from utils.wrds_client import wrds_query
df = wrds_query("""
    SELECT crsp_fundno, caldt, mret, mtna
    FROM crsp_q_mutualfunds.monthly_tna_ret_nav
    WHERE caldt BETWEEN '2020-01-01' AND '2020-12-31'
    LIMIT 5000
""")
assert len(df) == 5000 and {'crsp_fundno','caldt','mret','mtna'}.issubset(df.columns)
print(f"  rows: {len(df):,}, unique fundnos: {df['crsp_fundno'].nunique():,}")

# === Test 3: helper compute_implied_flows on a small slice ===
print("\n=== Test 3: compute_implied_flows on small panel ===")
import pandas as pd
small = wrds_query("""
    SELECT crsp_fundno, caldt, mret, mtna
    FROM crsp_q_mutualfunds.monthly_tna_ret_nav
    WHERE crsp_fundno IN (
        SELECT crsp_fundno FROM crsp_q_mutualfunds.monthly_tna_ret_nav
        WHERE caldt = '2020-12-31' AND mtna > 1000
        LIMIT 50
    )
    AND caldt BETWEEN '2019-01-01' AND '2020-12-31'
""")
small['caldt'] = pd.to_datetime(small['caldt'])
from utils.mutual_fund_utils import compute_implied_flows
flows = compute_implied_flows(small)
nonnull = flows['flow'].dropna()
assert len(nonnull) > 100, f"too few flow obs: {len(nonnull)}"
print(f"  flow obs: {len(nonnull):,}, mean={nonnull.mean():.4f}, median={nonnull.median():.4f}")

# === Test 4: filter_equity_funds on a small header sample ===
print("\n=== Test 4: filter_equity_funds on small header/style sample ===")
hdr = wrds_query("""
    SELECT crsp_fundno, et_flag, index_fund_flag
    FROM crsp_q_mutualfunds.fund_hdr LIMIT 2000
""")
sty = wrds_query("""
    SELECT crsp_fundno, crsp_obj_cd
    FROM crsp_q_mutualfunds.fund_style
    WHERE crsp_obj_cd LIKE 'ED%' LIMIT 2000
""")
from utils.mutual_fund_utils import filter_equity_funds
eq = filter_equity_funds(hdr, sty)
print(f"  eq fundnos in sample intersection: {len(eq)}")

print("\nALL TESTS PASSED")
