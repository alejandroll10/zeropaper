"""Test the latched WRDS server — run interactively if Duo may be needed."""
import sys
from pathlib import Path

UTILS = (Path(__file__).resolve().parents[1] / 'deploy_assets' / 'extensions' /
         'empirical' / 'utils')
sys.path.insert(0, str(UTILS))

from wrds_client import wrds_list_libraries, wrds_query, wrds_start

wrds_start()

# Quick smoke test: list libraries
libs = wrds_list_libraries()
print(f"Connected. {len(libs)} libraries available.")
print("Sample libraries:", sorted(libs)[:10])

# Test a tiny query
df = wrds_query("SELECT date, vwretd FROM crsp.dsi ORDER BY date DESC LIMIT 5")
print("\nCRSP daily index (last 5 rows):")
print(df)

print("\nConnection test passed.")
