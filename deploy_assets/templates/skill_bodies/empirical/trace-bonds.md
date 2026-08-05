## Source
- FINRA TRACE corporate-bond transactions via WRDS (`trace` library; cleaned `wrdsapps_bondret.*` if your subscription has it).
- Requires WRDS credentials (`WRDS_USER`/`WRDS_PASS` in `.env`) and the persistent WRDS server — Duo 2FA fires once per session.
- **TRACE is not in every WRDS subscription.** Call `trace_available()` first; if it reports no readable trade source, fall back to the self-contained `open-bond-pricing` skill.

A helper is available at `code/utils/trace_bonds_utils.py` — use `from utils.trace_bonds_utils import trace_available, trace_trades, bond_daily_panel, dealer_inventory_proxy, link_bond_to_crsp`.

## When to use this vs. `open-bond-pricing`
- **`open-bond-pricing` (OSBAP)** — analysis-ready, fully-cleaned bond returns/characteristics/factors. No WRDS, no auth. **Default for almost all bond research.**
- **`trace-bonds` (this skill)** — individual trade reports, intraday timing, dealer/customer flow. Use only when you genuinely need trade-level data. Raw `trace.*` tables are **lightly cleaned here** (`trc_st='T'` keep filter only), not Dick-Nielsen error-corrected.

## How to use

```python
from utils.trace_bonds_utils import trace_available, trace_trades, bond_daily_panel, dealer_inventory_proxy, link_bond_to_crsp

trace_available()
# {'wrds_clean_enhanced': False, 'wrds_clean_standard': False,
#  'raw_enhanced': True, 'raw_standard': True,
#  'bondret_monthly': False, 'bondcrsp_link': True}   # routes you to the best path

# Trade-level reports (auto-picks best source: pre-cleaned > raw enhanced > raw standard)
tr = trace_trades('2023-06-01', '2023-06-30', cusips=['00206RHJ4'])

# Volume-weighted daily price/yield by bond-day (SQL aggregation)
panel = bond_daily_panel('2023-06-01', '2023-06-30', cusips=['00206RHJ4'])
# -> cusip_id, trd_exctn_dt, vwap_prc, mean_prc, vw_yld, volume, n_trades

# Signed customer flow = dealer inventory change (positive = dealers absorbing)
flow = dealer_inventory_proxy('2023-06-01', '2023-06-30')           # market-wide, daily
flow = dealer_inventory_proxy('2023-06-01', '2023-06-30', by_bond=True)

# Merge bonds to equity: CUSIP -> CRSP permno/permco
link = link_bond_to_crsp(cusips=['00206RHJ4'])
```

## Key tables and columns
| Source | Schema.table | Notes |
|--------|--------------|-------|
| Cleaned enhanced (preferred) | `wrdsapps_bondret.trace_enhanced_clean` | often subscription-gated |
| Cleaned standard | `wrdsapps_bondret.trace_standard_clean` | often gated |
| Raw enhanced | `trace.trace_enhanced` | full institutional sizes; lightly cleaned here |
| Raw standard | `trace.trace` | dissemination-capped sizes |
| Monthly returns | `wrdsapps_bondret.bondret` | WRDS Bond Returns DB (often gated) |
| Bond↔CRSP link | `wrdsapps.bondcrsp_link` | cusip → permno/permco with date ranges |

Trade columns: `cusip_id` (≈100% populated; null only for some 144A privates, which carry `bond_sym_id`), `trd_exctn_dt`, `trd_exctn_tm`, `rptd_pr` (clean price /100), `entrd_vol_qt` (par volume), `yld_pt`, `rpt_side_cd` (B/S), `cntra_mp_id` (C=customer, D=dealer, A=affiliate, T=).

## Cleaning caveats (read before publishing)
- This module keeps only `trc_st='T'` on raw tables. It does **not** do full Dick-Nielsen cleaning: no msg-sequence cancellation/correction/reversal matching, no agency-trade dedup, no price/volume error correction.
- `bond_daily_panel.volume` **double-counts inter-dealer trades** (both dealers report) — a liquidity proxy, not exact par traded.
- `dealer_inventory_proxy` uses customer-counterparty trades (`cntra_mp_id='C'`) only, which are reported once — so it is **not** double-counted.
- For anything where cleaning matters (returns, spreads, published tables), use `open-bond-pricing` (OSBAP already error-corrects raw TRACE, incl. the +100% return truncation fix), or your account's `wrdsapps_bondret.*` / `contrib_bond_dickerson.*` schemas if available.

## Rules
- Always `trace_available()` first; degrade to `open-bond-pricing` if no trade source is readable.
- Filter on `trd_exctn_dt` — these tables have 100M+ rows; never scan unfiltered.
- State your source (`df.attrs['trace_source']`), date range, cleaning level, and CUSIP universe in any output.
