"""Full integration test for WRDS skill — exercises key recipes."""
import os
from dotenv import load_dotenv
load_dotenv()
import wrds
import pandas as pd

db = wrds.Connection(
    wrds_username=os.getenv('WRDS_USER'),
    wrds_password=os.getenv('WRDS_PASS')
)

# ---------- Test 1: CRSP monthly returns with market cap ----------
print("=== Test 1: CRSP monthly returns (2020-2024, 1000 rows) ===")
crsp = db.raw_sql("""
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
print(f"Shape: {crsp.shape}")
print(crsp.head())
print(f"Ret stats: mean={crsp['ret'].mean():.4f}, std={crsp['ret'].std():.4f}")

# ---------- Test 2: Compustat annual ----------
print("\n=== Test 2: Compustat annual fundamentals (2020-2023, 500 rows) ===")
comp = db.raw_sql("""
    SELECT gvkey, datadate, fyear, at, sale, ni, ceq
    FROM comp.funda
    WHERE indfmt = 'INDL' AND datafmt = 'STD'
      AND popsrc = 'D' AND consol = 'C'
      AND datadate BETWEEN '2020-01-01' AND '2023-12-31'
    LIMIT 500
""")
print(f"Shape: {comp.shape}")
print(comp.head())

# ---------- Test 3: CCM link table ----------
print("\n=== Test 3: CRSP-Compustat link table (sample) ===")
ccm = db.raw_sql("""
    SELECT gvkey, lpermno AS permno, linkdt, linkenddt, linktype, linkprim
    FROM crsp.ccmxpf_linktable
    WHERE linktype IN ('LU', 'LC')
      AND linkprim IN ('P', 'C')
    LIMIT 10
""")
print(f"Shape: {ccm.shape}")
print(ccm)

# ---------- Test 4: IBES ----------
print("\n=== Test 4: IBES analyst summary (2020-2024, 500 rows) ===")
ibes = db.raw_sql("""
    SELECT ticker, fpedats, statpers, meanest, medest, stdev, numest
    FROM ibes.statsum_epsus
    WHERE fpi = '1'
      AND statpers BETWEEN '2020-01-01' AND '2024-12-31'
      AND numest >= 3
    LIMIT 500
""")
print(f"Shape: {ibes.shape}")
print(ibes.head())

# ---------- Test 5: Market index ----------
print("\n=== Test 5: CRSP value-weighted market return (2023) ===")
mkt = db.raw_sql("""
    SELECT date, vwretd, ewretd, sprtrn
    FROM crsp.msi
    WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
""")
print(f"Shape: {mkt.shape}")
print(mkt)
annret = (1 + mkt['vwretd']).prod() - 1
print(f"VW annual return 2023: {annret:.4f}")

# ---------- Test 6: FF factors from WRDS ----------
print("\n=== Test 6: Fama-French monthly factors (last 12 months) ===")
ff = db.raw_sql("""
    SELECT * FROM ff.factors_monthly
    ORDER BY date DESC
    LIMIT 12
""")
print(ff)

db.close()
print("\n=== All tests passed. ===")
