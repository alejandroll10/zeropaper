"""Test WRDS connection — run interactively to check if Duo is needed."""
import os
from dotenv import load_dotenv
load_dotenv()

import wrds

# Try connecting with explicit credentials (avoids interactive prompt)
db = wrds.Connection(
    wrds_username=os.getenv('WRDS_USER'),
    wrds_password=os.getenv('WRDS_PASS')
)

# Quick smoke test: list libraries
libs = db.list_libraries()
print(f"Connected. {len(libs)} libraries available.")
print("Sample libraries:", sorted(libs)[:10])

# Test a tiny query
df = db.raw_sql("SELECT date, vwretd FROM crsp.dsi ORDER BY date DESC LIMIT 5")
print("\nCRSP daily index (last 5 rows):")
print(df)

db.close()
print("\nConnection test passed.")
