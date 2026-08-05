"""TRACE corporate-bond transactions via WRDS (issue #8 Tier 2).

Trade-level intraday corporate-bond data from FINRA TRACE, pulled through the
persistent WRDS server (Duo 2FA fires once per session). This is the
subscription-gated complement to the self-contained `open-bond-pricing` skill:
use `open-bond-pricing` for analysis-ready returns/characteristics; use this when
you genuinely need individual trade reports, intraday timing, or dealer flow.

    from utils.trace_bonds_utils import (
        trace_available,        # which TRACE/bond sources this account can read
        trace_trades,           # trade-level reports, filtered
        bond_daily_panel,       # volume-weighted daily price/yield by bond-day
        dealer_inventory_proxy, # signed customer flow (dealer inventory change)
        link_bond_to_crsp,      # CUSIP -> permno/permco (wrdsapps.bondcrsp_link)
    )

LIGHT CLEANING ONLY. The raw `trace.*` tables need substantial cleaning
(Dick-Nielsen cancellation/correction/reversal matching, agency-trade dedup,
price/volume error correction). This module applies only a `trc_st='T'` keep
filter and documents the rest as caveats. For a fully cleaned, error-corrected
panel use `open-bond-pricing` (OSBAP) or, if your WRDS account has them, the
`wrdsapps_bondret.*` / `contrib_bond_dickerson.*` schemas (auto-preferred below).
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from utils.wrds_client import wrds_query, wrds_start  # noqa: E402

# Candidate trade sources, best (pre-cleaned) first. enhanced=full institutional sizes.
_TRADE_SOURCES = [
    {"label": "wrds_clean_enhanced", "schema": "wrdsapps_bondret", "table": "trace_enhanced_clean", "pre_cleaned": True,  "enhanced": True},
    {"label": "wrds_clean_standard", "schema": "wrdsapps_bondret", "table": "trace_standard_clean", "pre_cleaned": True,  "enhanced": False},
    {"label": "raw_enhanced",        "schema": "trace",            "table": "trace_enhanced",       "pre_cleaned": False, "enhanced": True},
    {"label": "raw_standard",        "schema": "trace",            "table": "trace",                "pre_cleaned": False, "enhanced": False},
]
_LINK = ("wrdsapps", "bondcrsp_link")
_BONDRET = ("wrdsapps_bondret", "bondret")  # WRDS Bond Returns monthly panel (often gated)

_TRADE_COLS = ["cusip_id", "bond_sym_id", "company_symbol", "trd_exctn_dt", "trd_exctn_tm",
               "rptd_pr", "entrd_vol_qt", "yld_pt", "rpt_side_cd", "cntra_mp_id", "trc_st"]


def _can_read(schema, table):
    """True if the account can SELECT from schema.table."""
    try:
        wrds_query(f"SELECT 1 FROM {schema}.{table} LIMIT 1")
        return True
    except Exception:
        return False


def trace_available():
    """Probe which TRACE/bond sources this WRDS account can actually read.

    Returns a dict: {label-or-name: bool}. TRACE is not in every WRDS
    subscription, so call this first and let it route you.
    """
    wrds_start()
    out = {s["label"]: _can_read(s["schema"], s["table"]) for s in _TRADE_SOURCES}
    out["bondret_monthly"] = _can_read(*_BONDRET)
    out["bondcrsp_link"] = _can_read(*_LINK)
    return out


def _pick_source(enhanced=True):
    """Choose the best accessible trade table (pre-cleaned > raw; preferred grain)."""
    wrds_start()
    ordered = sorted(_TRADE_SOURCES, key=lambda s: (not s["pre_cleaned"], s["enhanced"] != enhanced))
    for s in ordered:
        if _can_read(s["schema"], s["table"]):
            return s
    raise RuntimeError(
        "No TRACE table is readable by this WRDS account "
        f"(tried {[ (s['schema'], s['table']) for s in _TRADE_SOURCES ]}). "
        "TRACE is not in every subscription — use the self-contained `open-bond-pricing` "
        "skill (OSBAP) instead, or ask WRDS to enable the `trace` library."
    )


def _cusip_clause(cusips, col="cusip_id"):
    if not cusips:
        return ""
    if isinstance(cusips, str):
        cusips = [cusips]
    vals = ",".join("'" + c.replace("'", "") + "'" for c in cusips)
    return f" AND {col} IN ({vals})"


def _keep_clause(source, drop_cancels):
    """Light clean: keep disseminated trade reports only (raw tables). Pre-cleaned
    WRDS tables already handle status, so no extra filter is added there."""
    if drop_cancels and not source["pre_cleaned"]:
        return " AND trc_st = 'T'"
    return ""


def trace_trades(start, end, cusips=None, enhanced=True, drop_cancels=True, source=None, limit=None):
    """Trade-level TRACE reports between two dates (inclusive).

    Args:
        start, end: 'YYYY-MM-DD' execution-date bounds.
        cusips: optional CUSIP (str) or list to restrict to.
        enhanced: prefer the enhanced file (full institutional trade sizes).
        drop_cancels: on raw tables, keep only trc_st='T' (drops C/W/R/X/Y
            cancellations, corrections, reversals). No effect on pre-cleaned tables.
        source: force a specific source dict from `_TRADE_SOURCES` (advanced).
        limit: optional row cap (for exploration).

    Returns:
        DataFrame of trades. Key columns: cusip_id, bond_sym_id, trd_exctn_dt,
        trd_exctn_tm, rptd_pr (clean price /100), entrd_vol_qt (par volume),
        yld_pt, rpt_side_cd (B/S), cntra_mp_id (C=customer, D=dealer, A=affiliate, T=...).

    Note: raw enhanced/standard tables are NOT fully cleaned (no Dick-Nielsen
    cancellation matching beyond trc_st, no inter-dealer dedup). For analysis-ready
    data use the `open-bond-pricing` skill.
    """
    wrds_start()  # safe no-op if already up; also covers the source= bypass path
    src = source or _pick_source(enhanced=enhanced)
    sql = (f"SELECT {', '.join(_TRADE_COLS)} FROM {src['schema']}.{src['table']} "
           f"WHERE trd_exctn_dt BETWEEN DATE '{start}' AND DATE '{end}'"
           f"{_cusip_clause(cusips)}{_keep_clause(src, drop_cancels)}")
    if limit:
        sql += f" LIMIT {int(limit)}"
    df = wrds_query(sql)
    df.attrs["trace_source"] = src["label"]
    return df


def bond_daily_panel(start, end, cusips=None, enhanced=True, drop_cancels=True):
    """Volume-weighted daily price/yield panel by bond-day (SQL aggregation).

    VWAP = sum(rptd_pr * entrd_vol_qt) / sum(entrd_vol_qt) per cusip_id, trd_exctn_dt.

    Returns columns: cusip_id, trd_exctn_dt, vwap_prc, mean_prc, vw_yld, volume,
    n_trades. `volume` double-counts inter-dealer trades (both dealers report);
    treat it as a liquidity proxy, not exact par traded. For exact volume,
    dedup inter-dealer reports or use a pre-cleaned source.
    """
    src = _pick_source(enhanced=enhanced)
    sql = (f"""SELECT cusip_id, trd_exctn_dt,
                      SUM(rptd_pr * entrd_vol_qt) / NULLIF(SUM(entrd_vol_qt), 0) AS vwap_prc,
                      AVG(rptd_pr) AS mean_prc,
                      SUM(yld_pt * entrd_vol_qt) / NULLIF(SUM(entrd_vol_qt), 0) AS vw_yld,
                      SUM(entrd_vol_qt) AS volume,
                      COUNT(*) AS n_trades
               FROM {src['schema']}.{src['table']}
               WHERE trd_exctn_dt BETWEEN DATE '{start}' AND DATE '{end}'
                 AND cusip_id IS NOT NULL{_cusip_clause(cusips)}{_keep_clause(src, drop_cancels)}
               GROUP BY cusip_id, trd_exctn_dt
               ORDER BY cusip_id, trd_exctn_dt""")
    df = wrds_query(sql)
    df.attrs["trace_source"] = src["label"]
    return df


def dealer_inventory_proxy(start, end, cusips=None, by_bond=False, enhanced=True, drop_cancels=True):
    """Signed customer flow = dealer inventory change, by day (or bond-day).

    Uses customer-counterparty trades only (cntra_mp_id='C'), which are reported
    once (no inter-dealer double count). From the dealer's perspective a customer
    SELL (rpt_side_cd='B', dealer buys) adds to inventory; a customer BUY
    (rpt_side_cd='S', dealer sells) reduces it.

    Returns: [cusip_id,] trd_exctn_dt, dealer_buy_vol, dealer_sell_vol,
    net_inventory_chg (= dealer_buy_vol - dealer_sell_vol), customer_trades.
    Positive net = dealers absorbing bonds from customers.
    """
    src = _pick_source(enhanced=enhanced)
    grp = "cusip_id, trd_exctn_dt" if by_bond else "trd_exctn_dt"
    sel = ("cusip_id, trd_exctn_dt" if by_bond else "trd_exctn_dt")
    sql = (f"""SELECT {sel},
                      SUM(CASE WHEN rpt_side_cd='B' THEN entrd_vol_qt ELSE 0 END) AS dealer_buy_vol,
                      SUM(CASE WHEN rpt_side_cd='S' THEN entrd_vol_qt ELSE 0 END) AS dealer_sell_vol,
                      SUM(CASE WHEN rpt_side_cd='B' THEN entrd_vol_qt
                               WHEN rpt_side_cd='S' THEN -entrd_vol_qt ELSE 0 END) AS net_inventory_chg,
                      COUNT(*) AS customer_trades
               FROM {src['schema']}.{src['table']}
               WHERE trd_exctn_dt BETWEEN DATE '{start}' AND DATE '{end}'
                 AND cntra_mp_id = 'C'{_cusip_clause(cusips)}{_keep_clause(src, drop_cancels)}
               GROUP BY {grp}
               ORDER BY {grp}""")
    df = wrds_query(sql)
    df.attrs["trace_source"] = src["label"]
    return df


def link_bond_to_crsp(cusips=None):
    """Bond CUSIP -> CRSP permno/permco with valid date ranges (wrdsapps.bondcrsp_link).

    Replaces the issue's `link_trace_to_mergent` ask for the equity side: lets you
    merge bond trades to the issuer's stock / Compustat fundamentals via permno.
    """
    wrds_start()
    if not _can_read(*_LINK):
        raise RuntimeError(f"{_LINK[0]}.{_LINK[1]} not readable by this account.")
    sql = (f"SELECT cusip, permno, permco, trace_startdt, trace_enddt, "
           f"link_startdt, link_enddt FROM {_LINK[0]}.{_LINK[1]} "
           f"WHERE 1=1{_cusip_clause(cusips, col='cusip')}")
    return wrds_query(sql)
