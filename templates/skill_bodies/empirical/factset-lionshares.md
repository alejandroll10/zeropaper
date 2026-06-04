## ⚠ Licensed — not exercised here

**FactSet LionShares (FactSet Ownership) is a paid subscription with no free
tier.** The access path and gotchas below are documented from vendor materials,
**not** verified by a live pull (no FactSet credentials in this environment).
Treat every claim as unverified until exercised through a licensed account, and
never present a LionShares result as provenance-verified.

## Source
- **FactSet LionShares** (now delivered as **FactSet Ownership**) — a
  commercial source for **institutional and fund equity holdings**. It
  assembles holdings from regulatory filings (US 13-F and equivalents) and fund
  disclosures into a position-level panel, and **classifies each holder** by
  type (mutual fund, hedge fund, pension, bank, insurance, etc.).
- **Vendor:** FactSet.
- **Coverage:** global institutional and fund holdings (broader than US-only
  13-F sources, which is part of the point), with holder-type classification.
- Use for ownership / institutional-investor work where you need holdings
  *and* a holder-type split (e.g. separating hedge funds from other investors).

## How to use (when licensed)
- **Direct from FactSet.** Through the FactSet workstation, the
  holdings/ownership data feed, or the API, using FactSet entity identifiers.
- **Via WRDS.** Subscribing institutions can reach FactSet ownership data
  through WRDS (the `wrds` skill); query it like any other WRDS library and
  filter on date and security before pulling.
- Credentials required either way; keep them in `.env`, never hard-coded.

## Gotchas (documented, not verified here)
- **Holdings are stale between report dates.** Positions are observed at
  disclosure dates (quarterly for US 13-F, less often for many non-US holders).
  Between dates a position is carried forward, not live. Date the panel to
  actual report dates and do not infer intra-quarter trading.
- **The 13-F lag and omissions.** US 13-F positions are reported up to 45 days
  after quarter-end, and confidential-treatment requests let filers omit
  positions. The holdings you see lag reality and can be incomplete.
- **Two levels — institution and fund — do not double-count.** The same assets
  can appear at the managing-institution level and the individual-fund level.
  Pick the level your analysis needs and aggregate consistently.
- **Holder classification is a mapping with edge cases.** The institution type
  is FactSet's classification; multi-strategy and changing managers blur the
  lines. Inspect the type field rather than assuming a clean partition.
- **Identifiers are FactSet's own.** Holders and securities use FactSet entity
  IDs; securities also carry CUSIP/ISIN/SEDOL. Build an explicit crosswalk to
  PERMNO/CIK rather than assuming a shared key.
- **International coverage is less frequent and less complete** than US 13-F —
  non-US disclosure regimes differ. Do not treat a global panel as uniformly
  dense.

## Rules
- **Licensed data: no provenance badge.** State explicitly that results come
  from a licensed feed not independently re-pulled in this pipeline.
- **Credentials only in `.env`.**
- **State the holding level and report dates.** Report whether you aggregated
  at the institution or fund level, and the report dates used.
- **Cite the product and vendor.** E.g. *FactSet Ownership (LionShares),
  FactSet Research Systems; data licensed and accessed YYYY-MM-DD.*
