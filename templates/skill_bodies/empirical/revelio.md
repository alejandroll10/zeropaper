## Source
- **Revelio Labs** — a firm-level **workforce / human-capital panel** built from
  aggregated public professional profiles and online job postings: headcount,
  hiring/attrition flows, role and seniority composition, skills, education,
  inferred compensation, layoffs, and employer sentiment. Keyed on a Revelio
  company id (`rcid`) and, for listed firms, mapped to `gvkey` / `cusip` / `cik`
  / `ticker`.
- **Access: WRDS schema `revelio`** (confirmed live on this entitlement,
  2026-06-27 — see entitlement map in pipeline issue #91). Queried through the
  persistent WRDS server via `wrds_query()`, exactly like `crsp.*` / `comp.*`.
- Use for labor / human-capital channels: workforce composition, hiring
  dynamics (postings flow vs. realized headcount stock), skill mix (e.g. AI/ML
  talent share), layoffs, and employer sentiment.

> **Still a licensed commercial source.** It is reachable on WRDS here, but it is
> not free/public — cite the vendor and product, and respect the entitlement.

## Identifiers & linking (the make-or-break step)
- **`rcid`** — Revelio company id. The join key for every table.
- **`ultimate_parent_rcid`** — corporate-parent rollup. A single listed parent
  spans many subsidiary employers; decide parent-level vs. establishment-level
  *before* aggregating.
- **`revelio.company_mapping`** carries the bridge to the research stack:
  `rcid → gvkey, cusip, cik, ticker, isin, sedol, naics_code`. So Revelio merges
  directly into Compustat (`gvkey`), CRSP (`cusip → permno` via `crsp.stocknames`
  / CCM), and EDGAR / Capital-IQ transcripts (`cik` / `gvkey`).
- **Coverage of the listed link is the binding constraint.** Of ~32.7M `rcid`s,
  only **~65k have a `gvkey`**, ~96k a `cusip`, ~52k a `ticker` — the rest are
  private companies. For a listed-equity study, **filter to `gvkey IS NOT NULL`**
  and treat the panel as the public-firm subset, not the whole Revelio universe.

## Key tables
| Table | Grain | Use | Key columns |
|-------|-------|-----|-------------|
| `revelio.company_mapping` | one row per `rcid` | entity bridge to gvkey/cusip/cik/ticker | `rcid, gvkey, cusip, cik, ticker, naics_code, ultimate_parent_rcid` |
| `revelio.postings_cosmos` | one row per job posting (**~2.6B rows**, 2008→present) | **hiring flow** / new-business-line demand | `job_id, rcid, post_date, remove_date, role_k1500_v2, role_k17000_v3, onet_code, salary*, expected_hires` |
| `revelio.individual_positions` | one row per person-position | **realized headcount stock**, seniority/role mix, attrition | `user_id, rcid, startdate, enddate, role_k1500_v2, role_k17000_v3, onet_code, seniority, weight, salary` |
| `revelio.individual_user_skills` | one row per user-skill | skill mix (AI/ML talent) — join to positions via `user_id` for the firm | `user_id, skill_translated, skill_k35000, first_reported` |
| `revelio.individual_user_skill_lookup` | skill taxonomy | roll skills up to coarser buckets | `skill_k15 … skill_k35000` |
| `revelio.sentiment_scores` | snapshot per `rcid` (**no date col**) | employer sentiment, incl. `innovative_technology_sentiment` | `rcid, num_reviews, *_sentiment` |
| `revelio.layoffs` | one row per layoff event | workforce contraction events | `rcid, notice_date, layoff_date, num_employees, layoff_type` |
| `revelio.workforce_dynamics_geo` | **pre-aggregated monthly** panel (`rcid`×geo×`role_k10`×`seniority`) | ready-made headcount + hiring/attrition **flows** — often cleaner than rebuilding from raw positions | `rcid, datemonth, country, state, metro_area, role_k10, seniority, count, inflow, outflow, external_inflow, external_outflow` (+ `scaled_*` / `raw_*` variants) |

Role taxonomies are hierarchical (`role_k1500_v2` coarse → `role_k17000_v3` fine,
plus standard `onet_code`); skills likewise (`skill_k15 … skill_k35000`). Pick a
granularity and a fixed mapping (e.g. an explicit list of AI/ML/data `onet_code`s
or `role_k1500_v2` values) and **document it** — never define the bucket by a
free-text `LIKE` on raw titles alone.

## Standard recipes

### Map a listed universe to rcid (do this first, cache it)
```python
from utils.wrds_client import wrds_query
link = wrds_query("""
    SELECT rcid, gvkey, cusip, ticker, naics_code, ultimate_parent_rcid
    FROM revelio.company_mapping
    WHERE gvkey IS NOT NULL
""")
# link.gvkey -> Compustat; link.cusip (8-digit) -> CRSP permno via crsp.stocknames
```

### Firm-quarter hiring intensity in target roles (postings flow)
```python
# wrds_query() takes a plain SQL string (NO parameter binding) — materialize any
# list yourself; a Python list spliced with %s renders invalid SQL like IN ([1,2]).
ai_onet = "'15-2051.00','11-3021.00'"      # explicit quoted O*NET list for AI/ML/data roles
# postings_cosmos is ~2.6B rows. Filter server-side by date + role (small result),
# then keep the listed universe by merging to `link` in pandas — avoids a
# 65k-element rcid IN-list. (For a handful of firms instead: AND rcid IN (1,2,3).)
postings = wrds_query(f"""
    SELECT rcid,
           date_trunc('quarter', post_date) AS yq,
           count(*)            AS n_postings,
           sum(expected_hires) AS exp_hires
    FROM revelio.postings_cosmos
    WHERE post_date >= '2010-01-01'
      AND onet_code IN ({ai_onet})
    GROUP BY rcid, date_trunc('quarter', post_date)
""")
postings = postings.merge(link[['rcid', 'gvkey']], on='rcid')   # -> listed firms only
```

### Realized headcount stock / role share as of a date (point-in-time aware)
```python
# A person is "at" rcid on date D if startdate <= D < coalesce(enddate, now).
# `weight` corrects sampling; sum weights, don't count rows.
ai_onet = "'15-2051.00','11-3021.00'"
rcid_in = ",".join(map(str, link['rcid'].unique()))    # integer rcids -> "1,2,3"
stock = wrds_query(f"""
    SELECT rcid,
           sum(weight) FILTER (WHERE onet_code IN ({ai_onet})) AS ai_headcount,
           sum(weight)                                         AS total_headcount
    FROM revelio.individual_positions
    WHERE startdate <= DATE '2018-12-31'
      AND (enddate IS NULL OR enddate > DATE '2018-12-31')
      AND rcid IN ({rcid_in})
    GROUP BY rcid
""")
# For very large rcid sets, a temp-table JOIN beats a giant IN-list. Or use the
# pre-aggregated revelio.workforce_dynamics_geo (monthly count/inflow/outflow).
```

### AI/ML skill share of staff
```python
# Join skills to positions on user_id to attribute a skill to a firm-period.
# `first_reported` dates the skill; use it for point-in-time, not "as known today".
```

### Sentiment (cross-sectional snapshot — note the limitation)
```python
sent = wrds_query("""
    SELECT rcid, num_reviews, innovative_technology_sentiment,
           management_sentiment, culture_sentiment
    FROM revelio.sentiment_scores
""")
# No time dimension on sentiment_scores: it is a current snapshot, not a panel.
# For a sentiment time series, aggregate revelio.sentiment_individual_reviews,
# which carries review_date + per-review rating_* columns (rating_overall,
# rating_business_outlook, rating_senior_leadership, …) keyed on rcid.
```

## Gotchas
- **Look-ahead / backfill is the #1 hazard for return prediction.** Revelio
  reconstructs history from profiles scraped *now*; a firm's 2015 headcount,
  computed today, includes people whose profiles were created later. This bakes
  future information into a "past" snapshot. For any forecasting/return-
  predictability design, restrict to data observable **as of the formation date**
  (use `post_date` / `startdate` / `first_reported` and a fixed vintage), or
  document the residual point-in-time risk explicitly. The data-integrity auditor
  should treat a Revelio-based predictor as backfill-suspect until this is shown.
- **Levels are estimates, not a census.** Coverage skews white-collar, US, and
  large firms. **Prefer within-firm changes** to cross-firm level comparisons,
  and use `weight` rather than raw row counts.
- **Profiles are self-reported and inferred.** Titles, seniority, and start/end
  dates carry noise; role/skill buckets inherit it.
- **Historical panels get restated across vintages.** Pin the pull date; do not
  mix vintages within a study.
- **Entity mapping is its own step.** Decide `rcid` vs. `ultimate_parent_rcid`
  and confirm the gvkey/cusip mapping; one listed parent spans many subsidiary
  employers (and the gvkey link covers only the ~65k listed `rcid`s).
- **Huge tables — filter or die.** `postings_cosmos` (~2.6B) and the positions
  table will time out unfiltered. Always constrain by `rcid` list + date range
  (+ role) and cache results to `data/revelio/` as parquet.
- **Define every metric explicitly.** "AI talent share", "hiring intensity", and
  the role/skill bucket each depend on the taxonomy level and denominator —
  state them so the number is reproducible.

## Rules
- **Filter to the listed universe** (`company_mapping.gvkey IS NOT NULL`) for
  equity studies; state how many firms link.
- **Point-in-time discipline.** Address backfill/look-ahead before using Revelio
  as a predictor; report the construction and the vintage date.
- **Weight, don't count.** Use `weight` for headcount/share aggregates.
- **Cache large pulls** to `data/revelio/` as parquet; never re-scan the billion-
  row tables.
- **State the sample.** Date range, role/skill bucket definition, parent vs.
  establishment level, number of linked firms, and the pull/vintage date.
- **Cite the vendor.** E.g. *Revelio Labs workforce data, via WRDS; accessed
  YYYY-MM-DD.* It is licensed commercial data — not a free/public source.
