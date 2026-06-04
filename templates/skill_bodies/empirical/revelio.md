## ⚠ Licensed — not exercised here

**Revelio Labs is a paid subscription with no free tier.** The access path and
gotchas below are documented from vendor materials, **not** verified by a live
pull (no Revelio credentials in this environment). Treat every claim as
unverified until exercised through a licensed account, and never present a
Revelio result as provenance-verified.

## Source
- **Revelio Labs** — builds a firm-level **workforce / human-capital panel**
  from public professional profiles and online job postings: headcount, hiring
  and attrition flows, role and seniority composition, skills, education
  (including the **advanced-degree share** of staff), inferred compensation,
  and sentiment. Mapped to companies and, where listed, to tickers.
- **Vendor:** Revelio Labs (workforce intelligence from aggregated public
  professional profiles and job postings).
- **Coverage:** company-level workforce panels, keyed on a Revelio company
  identifier and, where applicable, to listed-equity tickers.
- Use for labor/human-capital channels: workforce composition, hiring/attrition
  dynamics, analyst/staff education.

## How to use (when licensed)
- **Direct from Revelio Labs.** Through their data feed, API, or a cloud data
  share (e.g. Snowflake), keyed on the Revelio company identifier.
- **Possibly via WRDS.** Some institutions *may* reach Revelio data through
  WRDS, but **availability is not confirmed** — check with your library before
  assuming this path (do not claim a WRDS route without verifying it).
- Credentials required either way; keep them in `.env`, never hard-coded.

## Gotchas (documented, not verified here)
- **Coverage skews white-collar, US, large firms.** The data derives from
  public professional profiles, which over-represent office roles, the US, and
  big employers. Headcount levels are estimates, not a census; prefer
  within-firm changes to cross-firm level comparisons.
- **Profiles are self-reported and inferred.** Roles, seniority, and dates are
  inferred from self-authored profiles, so titles and start/end dates carry
  noise. Education fields (the advanced-degree share) inherit that noise.
- **Historical panels get restated.** As the underlying models and profile
  coverage are reworked, prior periods can be revised. Pin the data vintage and
  re-pull deliberately rather than mixing vintages.
- **Entity mapping is its own step.** Join on the Revelio company identifier and
  confirm the parent/subsidiary and ticker mapping; a single listed parent can
  span many subsidiary employers, and vice versa.
- **Timing is inferred, not point-in-time disclosure.** Hiring and attrition are
  reconstructed from profile changes, which surface with a lag and irregular
  timing; do not treat a monthly series as a clean as-of snapshot.
- **Define the metric explicitly.** "Advanced-degree share" and similar measures
  depend on how degrees and the staff denominator are defined; state the
  definition so the number is reproducible.

## Rules
- **Licensed data: no provenance badge.** State explicitly that results come
  from a licensed feed not independently re-pulled in this pipeline.
- **WRDS availability unconfirmed.** Do not assert a WRDS route without checking.
- **Credentials only in `.env`.**
- **State the vintage and metric definition.** Report the data vintage pinned
  and the exact metric definition used.
- **Cite the product and vendor.** E.g. *Revelio Labs workforce data, Revelio
  Labs; data licensed and accessed YYYY-MM-DD.*
