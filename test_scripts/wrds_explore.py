"""Explore WRDS library structure for skill documentation."""
import os
from dotenv import load_dotenv
load_dotenv()
import wrds

db = wrds.Connection(wrds_username=os.getenv('WRDS_USER'), wrds_password=os.getenv('WRDS_PASS'))

# Key libraries for finance research
key_libs = ['crsp', 'comp', 'ibes', 'optionm', 'taq', 'tfn', 'tr_ds_equities',
            'ff', 'risk_bankruptcy', 'kld', 'boardex', 'execcomp', 'rpna']

for lib in key_libs:
    try:
        tables = db.list_tables(library=lib)
        print(f"\n{lib} ({len(tables)} tables): {sorted(tables)[:8]}")
    except Exception as e:
        print(f"\n{lib}: ERROR - {e}")

# Check crsp key tables schema
print("\n--- CRSP MSF (monthly stock file) columns ---")
cols = db.describe_table('crsp', 'msf')
print(cols.head(15).to_string())

print("\n--- COMP FUNDA (annual fundamentals) columns ---")
cols = db.describe_table('comp', 'funda')
print(cols.head(15).to_string())

# Check WRDS-provided merged datasets
print("\n--- CCM (CRSP-Compustat merge) ---")
try:
    tables = db.list_tables(library='crsp')
    ccm = [t for t in tables if 'ccm' in t.lower()]
    print(f"CCM tables in crsp: {ccm}")
except:
    pass

db.close()
