## ⚠ Metered, LLM-mediated vendor terminal — read this first

DeepVest is **not** a raw-data API. It is an AI research terminal for RIAs
(formerly Benjamin AI — deepvest.ai/articles/benjamin-ai-rebrands-to-deepvest)
exposed as one remote **MCP server**; most tools take a
natural-language `query` and an LLM on the vendor side decides what data to
pull and how to present it. That has three consequences for this pipeline:

1. **The answer is model output, not a database row.** The same query can come
   back formatted differently (and occasionally with different numbers) on a
   second call. Ask for raw tables, never for interpretation, and keep the
   cached response as the provenance record.
2. **Identifiers are tickers, not PERMNO/gvkey/CUSIP.** No point-in-time
   security master, no delisting returns, no documented vendor for the
   underlying prices/fundamentals. It cannot replace CRSP/Compustat for a
   top-journal cross-section; it *can* supply things WRDS doesn't give you
   (options analytics/chains, ETF fund flows and holdings, earnings
   transcripts, dividend payment records, 13F/N-PORT via EDGAR) and it is the
   practical price/fundamentals source for a deployment **without WRDS**.
3. **It costs credits.** 1,000 free credits/month per account, then
   $0.025/credit; ~7–16 credits per analysis call, ~550 for long SEC-filing
   analysis. Budget the pull before you script a loop over 500 tickers.

Access path verified live 2026-08-21 (auth, `tools/list`, `dividend_history`,
`quick_analysis` with `format="json"`); the coverage claims below are from the
vendor's tool descriptions and docs, not from an exhaustive pull.

## Source
- **DeepVest** — https://www.deepvest.ai ; developer docs
  https://console.deepvest.ai/docs (the page is behind a bot challenge — use a
  real browser, `curl` returns 403).
- **MCP server:** `https://api.deepvest.ai/mcp` (Streamable HTTP). 54 tools as
  of server 3.4.7. The portal's "REST API" tab is a *Coming Soon* placeholder
  (checked 2026-08-21); the MCP server is the only API today. If the REST API
  ships, prefer it for raw pulls and re-check the gotchas below.
- **Auth:** API key from https://console.deepvest.ai/dashboard/api-keys sent
  as `X-API-Key` (what this skill uses), or OAuth 2.0 browser login (what
  Claude Desktop uses — not for an unattended pipeline).
- **Key goes in `.env` as `DEEPVEST_API_KEY=...`**, read lazily by
  `code/utils/deepvest_utils.py`. Never hard-code it; never commit it.
- **Limits:** 3 concurrent requests, 20 requests/minute per key (HTTP 429,
  `Retry-After`); 401 = bad key, 402 = out of credits. Typical latency 5–30 s,
  backtests/optimization up to 2 min.

## How to use

A helper lives at `code/utils/deepvest_utils.py` (stdlib MCP client; no extra
dependency). Every successful call is cached to `data/deepvest/<tool>_<hash>.json`
— `{tool, arguments, fetched_at, server, response}` — and re-read on the next
identical call (`refresh=True` to re-query).

```bash
python3 code/utils/deepvest_utils.py ping                        # auth check, costs nothing
python3 code/utils/deepvest_utils.py tools                       # live catalog (free)
python3 code/utils/deepvest_utils.py query quick_analysis \
   "SPY monthly closing prices from 2015-01-01 to 2024-12-31"   # prose answer
python3 code/utils/deepvest_utils.py call quick_analysis \
   '{"query":"SPY monthly closing prices 2015-2024","format":"json"}'  # JSON envelope
python3 code/utils/deepvest_utils.py call dividend_history \
   '{"symbols":"SPY,QQQ","start_date":"2010-01-01","end_date":"2024-12-31"}'
python3 code/utils/deepvest_utils.py cache                       # what has been pulled
```

```python
from utils.deepvest_utils import (DeepVestClient, call_tool, query, list_tools,
                                  parse_result, tables_from_response, parse_markdown_tables)

# 1. Structured pull — ALWAYS prefer format="json" on asset_analysis / quick_analysis.
res = call_tool("quick_analysis",
                {"query": "SPY and IWM monthly closing prices from 2010-01-01 to 2024-12-31",
                 "format": "json"})
env = parse_result(res)                 # {"schema_version": "1", "prose": ..., "data": {...}}
tables = tables_from_response(res)      # {"raw_asset_prices_table": [DataFrame], ...}
prices = tables["raw_asset_prices_table"][0]    # columns: date, SPY, IWM  (numeric coerced)

# 2. Typed tools return JSON directly.
div = parse_result(call_tool("dividend_history",
                             {"symbols": "KO", "start_date": "2000-01-01", "end_date": "2024-12-31"}))
events = div["symbols"]["KO"]["events"]          # ex_date, record_date, pay_date, declared_date,
                                                 # amount_as_paid, amount_adjusted, frequency, currency
# 3. Prose tools (no format param): ask for a table and parse it.
txt = query("macroeconomic_analysis",
            "US unemployment rate and 10-year Treasury yield, monthly, 2000-01 to 2024-12, "
            "as one markdown table with columns date, unrate, gs10 — no commentary")
df = parse_markdown_tables(txt)[0]
```

**Where the call happens matters.** Pull DeepVest data in *your own* shell
(the empiricist's Bash) into `data/deepvest/` **before** the results-pipeline
run plan, and declare the cached JSON files as inputs. The sandboxed producer
workspace (`results_pipeline.py run`) has no `.env` and only the LLM-provider
keys can be selected into it — `DEEPVEST_API_KEY` is not one of them, so a
live DeepVest call inside `code/empirical.py` fails by design.

## Tool map (54 tools; the ones that matter for research)

| Need | Tool | Notes |
|------|------|-------|
| Price / return history, rolling beta/corr/drawdown/Sharpe, ETF fund flows + NAV, financial statements, current fundamentals | `quick_analysis` (`query`, `format`) | `format="json"` → stable envelope whose `data` sections are markdown-table strings (parse with `tables_from_response`). The only tool with fund-flow series. |
| Window summary stats (CAGR, vol, max DD, Sharpe, correlation matrix), valuation-multiple history, ETF metadata (AUM, ER, holdings, sector/region) | `asset_analysis` (`query`, `format`) | `format="json"` as above. Stocks, ETFs, indices, FX, crypto, commodities. |
| Cross-sectional screen / metrics for a ticker list, incl. **`as of YYYY-MM-DD`** historical snapshots; earnings-call-theme filters | `stock_screener` (`query`) | Surfaces a "Skipped Criteria" / "Coverage Caveat" block when it silently dropped a filter — read it. Default 50 results sorted by market cap. |
| Exact trailing-N-trading-day return/high/low/DD | `trailing_window_return` (`tickers`, `n_trading_days` 2–756, `end_date`) | Typed; ≤10 tickers per call. |
| Dividend / distribution payment records back to the 1980s | `dividend_history` (`symbols`, `start_date`, `end_date`) | Typed, cheap ("no live vendor call"). **Max 60 events per symbol per call** — pass a date window and page by year. `amount_as_paid` vs `amount_adjusted` (stale split snapshot — don't use across splits). No distribution character. |
| Macro series (GDP, CPI, unemployment, yields, spreads, ISM, money supply; optional unrevised) | `macroeconomic_analysis` (`query`) | Prose only. For the paper, prefer the `fred` skill (documented series IDs, vintages); use this for convenience or series FRED lacks. |
| Asset × macro cross-market analysis | `merged_data_analysis` (`query`) | |
| Earnings transcripts, EPS/revenue estimates vs actuals, surprise history, pre/post-earnings drift | `earnings_analysis` (`query`) | Per-symbol. |
| EDGAR: XBRL statements, MD&A/risk factors, Form 4, **13F history up to 40 quarters**, DEF 14A comp, N-PORT/N-MFP, full-text search | `sec_financial_analysis` (`query`) | Spawns a fresh analysis agent per call; **expensive** (~550 credits for long filings). The `edgar` skill does the same from source for free — use that unless you need DeepVest's cross-filing synthesis. |
| Options: symbol-level IV, OI, put/call, Greeks, skew, GEX, max pain, flow over time | `options_analysis` (`query`) | The pipeline's only non-WRDS options source. |
| Options: contract-level chain (bid/ask, OI, Greeks, IV, unusual-activity flags) | `options_chain` (`query`) | |
| Options: screen symbols by options metrics | `options_screener` (`query`) | |
| Options hedge/income strategy backtests on historical chains | `options_hedge_backtest` (`query`) | 30–120 s. |
| Indicator / event / macro-conditional backtests, portfolio optimization & comparison | `strategy_backtest`, `event_backtest`, `macro_conditional_backtest`, `portfolio_optimization`, `portfolio_comparison` | **Do not report these as your empirical results** — you cannot see the code. Use only to scout; recompute anything paper-bound yourself from the raw series. |
| ETF look-through / overlap / weighted expense | `holdings_overlap_tool`, `lookthrough_exposure_tool`, `weighted_expense_calculator_tool` | Typed. |
| News + thematic discovery (Tavily) | `search_news` (`query`) | +2-credit surcharge per call. |
| Math / option pricing / DCF / WACC / bond / tax / mortgage calculators | `black_scholes_option_price_tool`, `dcf_valuation_tool`, … | Typed, but anything here is a ten-line local function with `numpy`/`scipy` — do **not** outsource paper arithmetic to a remote LLM tool. |

`list_tools()` returns the live catalog with each tool's `inputSchema`; the
descriptions there are the authoritative routing guide (they say which tool
NOT to use for what) and are more current than this table.

## Gotchas

- **Ask for data, not analysis.** "Return X as a markdown table with columns
  a, b, c; no commentary" gets you a parseable table; "analyze X" gets prose
  with selected numbers. With `format="json"` the `data` sections are labelled
  (`raw_asset_prices_table`, `raw_volume_data_table`, …) — use those labels,
  not the prose.
- **Price basis is not stated.** A live `quick_analysis` monthly-close pull
  returned SPY 2023-01-31 = 388.67, i.e. a dividend-adjusted close (the
  unadjusted close was 406.48). Ask explicitly for *unadjusted* or *adjusted*
  prices, check one known observation against another source, and state the
  basis in the paper.
- **Ticker universe = today's tickers.** Screens and metric lookups for a
  ticker list are survivorship-biased unless you supply the historical
  constituent list yourself and use `as of YYYY-MM-DD`. Delisted names and
  ticker reuse are not handled. Not a CRSP substitute for cross-sections.
- **Not byte-reproducible.** The vendor LLM may re-phrase or re-round. Compare
  numbers (tolerance), not strings, when re-querying for an audit; keep the
  first-pull cache file as the binding record and cite its `fetched_at`.
- **Caps and silent drops.** `dividend_history` truncates at 60 events/symbol
  (the omission is listed in `data_gaps`); `stock_screener` drops unknown
  filters (listed under "Skipped Criteria"); mutual-fund fundamentals cover a
  curated subset. Read and surface those blocks.
- **Credits are token-based, so long answers cost more.** Narrow the query
  (ticker list, date window, one metric) and cache aggressively; the helper
  memoises by `(tool, arguments)`, so identical re-runs are free.
- **Rate limits bite in loops.** The helper spaces calls ≥3.1 s apart and
  retries 429/5xx with backoff, but a 500-ticker loop is ~26 min and
  thousands of credits — batch tickers into one query where the tool allows
  (`trailing_window_return` ≤10, `dividend_history` comma-separated list).
- **Coverage is undocumented.** The vendor does not publish which upstream
  price/fundamentals feed it uses or its history depth per asset class. Probe
  with one cheap call before planning an analysis around it.

## Rules
- **Credentials only in `.env`** (`DEEPVEST_API_KEY`); `ping` to verify.
- **No provenance badge for the underlying data** (vendor feed is not
  disclosed). In the paper: *Source: DeepVest (api.deepvest.ai), tool
  `<name>`, query "<text>", accessed YYYY-MM-DD.* Keep the cache JSON under
  `data/deepvest/` as the record; do not paraphrase it into a hand-typed table.
- **Paper-bound numbers come from raw series you pulled and computed on
  yourself** — never from DeepVest's own backtests, optimizations, or
  interpretations.
- **Cross-check one observation** against FRED / Ken French / WRDS / EDGAR
  (whichever overlaps) and record the check in `data_search_log.md`.
- **Budget first.** Estimate calls × credits before a loop; state the credit
  spend in the data inventory so a re-run is predictable.
