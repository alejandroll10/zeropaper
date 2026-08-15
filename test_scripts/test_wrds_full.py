"""Full integration test for WRDS skill — exercises key recipes.

Uses the persistent WRDS server (utils.wrds_client). Does NOT open a fresh
wrds.Connection (which would trigger another Duo prompt).
"""
from utils.wrds_client import wrds_query, wrds_ping
assert wrds_ping(), "WRDS host daemon is unavailable"

# ---------- Test 1: CRSP monthly returns with market cap ----------
print("=== Test 1: CRSP monthly returns (2020-2024, 1000 rows) ===")
crsp = wrds_query("""
    SELECT a.permno, a.date, a.ret, ABS(a.prc) * a.shrout AS mktcap,
           b.shrcd, b.exchcd
    FROM crsp.msf AS a
    JOIN crsp.msenames AS b
      ON a.permno = b.permno
      AND a.date BETWEEN b.namedt AND b.nameendt
    WHERE a.date BETWEEN '2020-01-01' AND '2024-12-31'
      AND b.shrcd IN (10, 11)
      AND b.exchcd IN (1, 2, 3)
    LIMIT 1000
""")
assert len(crsp) == 1000
print(f"  shape: {crsp.shape}, ret mean={crsp['ret'].mean():.4f}, std={crsp['ret'].std():.4f}")

# ---------- Test 2: Compustat annual fundamentals ----------
print("\n=== Test 2: Compustat funda (2020-2023, 500 rows) ===")
comp = wrds_query("""
    SELECT gvkey, datadate, fyear, at, sale, ni, ceq
    FROM comp.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD'
      AND popsrc = 'D' AND consol = 'C'
      AND datadate BETWEEN '2020-01-01' AND '2023-12-31'
    LIMIT 500
""")
assert len(comp) == 500
print(f"  shape: {comp.shape}")

# ---------- Test 3: CCM link ----------
print("\n=== Test 3: CRSP-Compustat link table (sample) ===")
ccm = wrds_query("""
    SELECT gvkey, lpermno AS permno, linkdt, linkenddt, linktype, linkprim
    FROM crsp.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
    LIMIT 10
""")
assert len(ccm) == 10
print(f"  shape: {ccm.shape}")

# ---------- Test 4: IBES ----------
print("\n=== Test 4: IBES analyst summary (2020-2024, 500 rows) ===")
ibes = wrds_query("""
    SELECT ticker, fpedats, statpers, meanest, medest, stdev, numest
    FROM ibes.statsum_epsus
    WHERE fpi = '1'
      AND statpers BETWEEN '2020-01-01' AND '2024-12-31'
      AND numest >= 3
    LIMIT 500
""")
assert len(ibes) == 500
print(f"  shape: {ibes.shape}")

# ---------- Test 5: CRSP market index 2023 ----------
print("\n=== Test 5: CRSP VW market return (2023) ===")
mkt = wrds_query("""
    SELECT date, vwretd, ewretd, sprtrn
    FROM crsp.msi
    WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
""")
assert len(mkt) == 12
annret = (1 + mkt['vwretd']).prod() - 1
print(f"  shape: {mkt.shape}, VW annual ret 2023 = {annret:.4f}")

# ---------- Test 6: FF factors from WRDS ----------
print("\n=== Test 6: ff.factors_monthly (last 12 rows) ===")
ff = wrds_query("""
    SELECT * FROM ff.factors_monthly
    ORDER BY date DESC
    LIMIT 12
""")
assert len(ff) == 12
print(f"  shape: {ff.shape}, columns: {list(ff.columns)}")

print("\nALL TESTS PASSED")
