"""Explore WRDS library structure for skill documentation."""
import sys
from pathlib import Path

UTILS = (Path(__file__).resolve().parents[1] / 'deploy_assets' / 'extensions' /
         'empirical' / 'utils')
sys.path.insert(0, str(UTILS))

from wrds_client import wrds_describe, wrds_list_tables, wrds_start

wrds_start()

# Key libraries for finance research
key_libs = ['crsp', 'comp', 'ibes', 'optionm', 'taq', 'tfn', 'tr_ds_equities',
            'ff', 'risk_bankruptcy', 'kld', 'boardex', 'execcomp', 'rpna']

for lib in key_libs:
    try:
        tables = wrds_list_tables(lib)
        print(f"\n{lib} ({len(tables)} tables): {sorted(tables)[:8]}")
    except Exception as e:
        print(f"\n{lib}: ERROR - {e}")

# Check crsp key tables schema
print("\n--- CRSP MSF (monthly stock file) columns ---")
cols = wrds_describe('crsp', 'msf')
print(cols.head(15).to_string())

print("\n--- COMP FUNDA (annual fundamentals) columns ---")
cols = wrds_describe('comp', 'funda')
print(cols.head(15).to_string())

# Check WRDS-provided merged datasets
print("\n--- CCM (CRSP-Compustat merge) ---")
try:
    tables = wrds_list_tables('crsp')
    ccm = [t for t in tables if 'ccm' in t.lower()]
    print(f"CCM tables in crsp: {ccm}")
except Exception:
    pass
