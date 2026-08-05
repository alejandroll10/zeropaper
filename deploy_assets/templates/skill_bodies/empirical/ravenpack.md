## ⚠ Licensed — not exercised here

**RavenPack is a paid subscription with no free tier.** The access path and
gotchas below are documented from vendor materials, **not** verified by a live
pull (no RavenPack credentials in this environment). Treat every claim as
unverified until exercised through a licensed account, and never present a
RavenPack result as provenance-verified.

## Source
- **RavenPack News Analytics** — a commercial feed that converts unstructured
  news and other text into structured, machine-readable **entity-event
  records**: each detected company, person, or place in a story gets a
  timestamped row with sentiment, relevance, novelty, and a topic taxonomy.
- **Vendor:** RavenPack. The analytics product is versioned (a legacy **1.0**
  and later editions) with different fields and taxonomies — confirm the
  edition against current vendor docs before coding against field names.
- **Coverage:** global news (newswires such as Dow Jones, plus web and
  press-release sources); millions of entity-event records per day.
- Use for news-based signals: event studies, attention/sentiment measures,
  mapping stories to tickers.

## How to use (when licensed)
- **Direct from the vendor.** Historical flat-file dumps plus an ongoing feed
  (SFTP / API / cloud share). You pull dated files and the point-in-time
  analytics for each story.
- **Via WRDS.** Subscribing institutions can reach RavenPack News Analytics
  through WRDS (the `wrds` skill) — the easiest academic route if your
  university licenses it. Query it like any other WRDS library; filter on date
  and relevance **before** pulling.
- Credentials required either way; keep them in `.env`, never hard-coded.

## Gotchas (documented, not verified here)
- **Filter on relevance first.** Each record has a `RELEVANCE` score (0–100). A
  story that merely mentions a company in passing scores low; keep
  `RELEVANCE = 100` (or a high threshold) for stories that are *about* the
  entity, or the signal is mostly noise.
- **Deduplicate with the novelty score.** Newswires re-run and syndicate the
  same story. The Event Novelty Score (`ENS`) flags the first report
  (`ENS = 100`) versus echoes; without it you double-count one event.
- **Timestamps are UTC; align to the trading calendar.** The production
  timestamp is when the record was created, in UTC. Convert to the market
  timezone and decide deliberately how to treat after-close and weekend news
  before forming a daily signal.
- **Use the point-in-time timestamp, not the story date, to avoid look-ahead.**
  Build signals from when the analytics were *available*, not when the event
  nominally happened.
- **Sentiment scales differ by version.** Event Sentiment Score and Composite
  Sentiment Score conventions changed between 1.0 and later editions (e.g. a
  0–100 scale with 50 neutral). Confirm the edition and scale before
  thresholding.
- **Entity mapping is its own step.** Records key on `RP_ENTITY_ID`, not a
  ticker or PERMNO. Use RavenPack's mapping files to join to security
  identifiers; entities include private firms, people, and places, not just
  listed equities.
- **Volume.** The raw feed is large — filter on entity, relevance, and date at
  read time rather than loading everything.

## Rules
- **Licensed data: no provenance badge.** State explicitly that results come
  from a licensed feed that was not independently re-pulled in this pipeline.
- **Credentials only in `.env`.**
- **State the filters that define the sample.** Report the relevance and
  novelty thresholds — they materially change the sample.
- **Cite the product and edition.** E.g. *RavenPack News Analytics
  (RavenPack 1.0), RavenPack; data licensed and accessed YYYY-MM-DD.*
