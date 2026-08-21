"""Test DeepVest skill — verifies the MCP client, auth, live catalog, a typed tool, and the JSON envelope.

Run from a deployed project root (PYTHONPATH=code), or from the template repo
with PYTHONPATH=deploy_assets/extensions/empirical (the module is importable as
utils.deepvest_utils either way).
Requires DEEPVEST_API_KEY in .env. Spends ~10-15 credits (one quick_analysis
call); the dividend_history call is the vendor's cheap no-live-vendor path.
Set DEEPVEST_TEST_OFFLINE=1 to run only the network-free parser tests.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from utils import deepvest_utils as dv  # noqa: E402

# === Test 0: network-free parsers ===
print("=== Test 0: parse_markdown_tables / parse_json_blocks / _parse_sse ===")
sample = ("| date | SPY | Return (%) |\n|---|---:|---:|\n| 2023-01-31 | $388.67 | 1.59 |\n"
          "| 2023-02-28 | 378.90 | (2.51) |\n\n```json\n{\"a\": 1}\n```")
tables = dv.parse_markdown_tables(sample)
assert len(tables) == 1 and list(tables[0].columns) == ["date", "SPY", "Return (%)"], tables
assert abs(tables[0]["SPY"].iloc[0] - 388.67) < 1e-9 and abs(tables[0]["Return (%)"].iloc[1] + 2.51) < 1e-9
assert dv.parse_json_blocks(sample) == [{"a": 1}]
# edge cases: no edge pipes, a pipe-bearing prose line before the header, and two
# adjacent tables with no gap (the first must not be dropped)
assert dv.parse_markdown_tables("date | SPY\n---|---\n2023-01-31|388.67\n")[0]["SPY"].iloc[0] == 388.67
assert len(dv.parse_markdown_tables("stray x | y\n| date | SPY |\n|---|---|\n| 2023-01-31 | 388.67 |\n")) == 1
adjacent = dv.parse_markdown_tables("| a | b |\n|---|---|\n| 1 | 2 |\n| c | d |\n|---|---|\n| 3 | 4 |\n")
assert len(adjacent) == 2 and list(adjacent[0].columns) == ["a", "b"] and list(adjacent[1].columns) == ["c", "d"], adjacent
msgs = dv._parse_sse('event: message\ndata: {"jsonrpc":"2.0","id":7,"result":{"ok":true}}\n\n')
assert msgs == [{"jsonrpc": "2.0", "id": 7, "result": {"ok": True}}], msgs
fake = {"structured": {"result": json.dumps({"schema_version": "1", "prose": "x",
        "data": {"raw_asset_prices_table": "T\n=\n\n| date | SPY |\n|---|---|\n| 2023-01-31 | 388.67 |"}})},
        "text": "ignored"}
t = dv.tables_from_response(fake)
assert list(t) == ["raw_asset_prices_table"] and float(t["raw_asset_prices_table"][0]["SPY"].iloc[0]) == 388.67
print("  parsers OK")

if os.getenv("DEEPVEST_TEST_OFFLINE"):
    print("DEEPVEST_TEST_OFFLINE set — skipping live tests. PASS")
    sys.exit(0)

if not os.getenv("DEEPVEST_API_KEY"):
    print("FAIL: DEEPVEST_API_KEY not set in .env")
    sys.exit(1)

cache_dir = Path(tempfile.mkdtemp(prefix="deepvest_test_"))
client = dv.DeepVestClient(cache_dir=cache_dir)

# === Test 1: initialize (free) ===
print("\n=== Test 1: initialize / ping ===")
info = client.initialize()
assert info.get("serverInfo", {}).get("name"), info
print(f"  server={info['serverInfo'].get('name')} v{info['serverInfo'].get('version')} protocol={info.get('protocolVersion')}")

# === Test 2: tools/list (free) ===
print("\n=== Test 2: tools/list ===")
tools = {t["name"]: t for t in client.list_tools()}
for required in ("quick_analysis", "asset_analysis", "dividend_history", "stock_screener", "options_analysis"):
    assert required in tools, f"expected tool {required} missing; have {sorted(tools)[:10]}..."
assert "format" in tools["quick_analysis"].get("inputSchema", {}).get("properties", {}), "quick_analysis lost its format param"
print(f"  {len(tools)} tools; required set present")

# === Test 3: typed tool (cheap) + cache round-trip ===
print("\n=== Test 3: dividend_history SPY 2023 ===")
args = {"symbols": "SPY", "start_date": "2023-01-01", "end_date": "2023-12-31"}
res = client.call_tool("dividend_history", args)
payload = dv.parse_result(res)
events = payload["symbols"]["SPY"]["events"]
assert len(events) == 4, f"SPY paid 4 quarterly distributions in 2023, got {len(events)}"
assert all("amount_as_paid" in e and "ex_date" in e for e in events)
assert not res["cached"] and Path(res["cache_path"]).is_file()
again = client.call_tool("dividend_history", args)
assert again["cached"] and dv.parse_result(again) == payload
print(f"  {len(events)} events, total_as_paid={payload['symbols']['SPY']['summary']['total_as_paid']}; cache round-trip OK")

# === Test 4: format="json" envelope on quick_analysis (~10 credits) ===
print("\n=== Test 4: quick_analysis format=json ===")
res = client.call_tool("quick_analysis", {"query": "SPY monthly closing prices from 2023-01-01 to 2023-12-31",
                                          "format": "json"})
env = dv.parse_result(res)
assert isinstance(env, dict) and env.get("schema_version") == "1" and "data" in env, str(env)[:300]
tabs = dv.tables_from_response(res)
assert tabs, f"no tables parsed from envelope sections {list(env['data'])}"
name, frames = next(iter(tabs.items()))
df = frames[0]
assert len(df) >= 10, df
print(f"  section={name} rows={len(df)} cols={list(df.columns)}")
print(f"  first row: {df.iloc[0].to_dict()}")

print("\nAll DeepVest tests PASS")
