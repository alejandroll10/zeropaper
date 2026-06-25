---
title: "The Disappearing Index Effect: Greenwood & Sammon (2025)"
description: >-
  Distilled: The abnormal return from being added to or removed from the S&P 500
  fell from an average of 7.4% in the 1990s to statistically indistinguishable
  from zero in the 2010s, driven by index migrations from the S&P MidCap and an
  overall rise in market liquidity around index events. J. Finance 2025, paywalled.
  Seven core results with source locators, datasets used, the model (demand-curve
  price impact), and the empirical decomposition.
sidebar:
  label: Greenwood-Sammon 2025
  order: 1
tags: [paper-summary, asset-pricing, equities, passive-investing, index-funds,
       market-microstructure, panel-regression, event-study, peer-reviewed,
       unreplicated, data:wrds, data:siblis-research]
paper:
  authors: Robin Greenwood, Marco Sammon
  authorList:
    - { family: Greenwood, given: Robin, affiliation: Harvard Business School }
    - { family: Sammon, given: Marco, orcid: "0000-0001-6502-1695", affiliation: Harvard Business School }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 657–698
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13410
  jel:
    codes: [G12, G14, G23]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Markets and Investment Strategies
    - Market Microstructure and Liquidity
    - Passive Investing and Indexation
  dataAccess: licensed-commercial
  outcome:
    - cumulative abnormal return around S&P 500 index additions
    - cumulative abnormal return around S&P 500 index deletions
    - demand-curve multiplier (price impact per unit demand shock)
  outcomeClass: [security-returns, market-microstructure]
  license: >-
    Wiley VOR terms and conditions (content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2024-12-20); not CC-licensed; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/JF site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 17

  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [event-study, panel-regression, fama-macbeth]
    identification: descriptive

  contributionType: [new-fact, measurement]

  mechanisms: [demand-elasticity, limits-to-arbitrage, liquidity]

  scope:
    region: US
    assetClass: US equities (S&P 500 additions and deletions)
    period: 1980-01..2020-12
    frequency: daily
    dataType: [market, accounting]
    granularity: [security, firm]
    n: "736 additions and 731 deletions to the S&P 500, 1980-2020 (matched to CRSP)"

  findings:
    - ref: R1
      outcome: cumulative abnormal return around S&P 500 index additions
      metric: car
      value: "1990s avg 7.4%; 2000s avg 5.2%; 2010s avg 0.8% (statistically indistinguishable from zero)"
      direction: negative
      vsBenchmark: decline of 4.3pp (***) from 2000s to 2010s (Table I, p. 667)
    - ref: R2
      outcome: cumulative abnormal return around S&P 500 index deletions
      metric: car
      value: "1980s avg -4.6%; 1990s avg -16.1%; 2000s avg -12.4%; 2010s avg -0.6% (statistically indistinguishable from zero)"
      direction: negative
      vsBenchmark: decline of 11.8pp (***) from 2000s to 2010s (Table I, p. 667)
    - ref: R3
      outcome: cumulative abnormal return around S&P 500 index additions
      metric: car
      value: "Composition controls explain only small fraction of decline: decade effects shrink from 6.6% to 5.6% (1990s vs 2010s) after adding turnover, size, arbitrage risk, analyst coverage"
      direction: negative
      vsBenchmark: "residual decade decline remains large and significant (p=0.000) after controls (Table II, p. 672)"
    - ref: R4
      outcome: cumulative abnormal return around S&P 500 index additions
      metric: car
      value: "Direct additions: 10.2% (1990s), 8.8% (2000s), 5.4% (2010s); Migrations from MidCap: 6.7% (1990s), 2.7% (2000s), -1.8% (2010s)"
      direction: negative
      vsBenchmark: "migration-nonmigration gap grows from 3.6pp in 1990s to 7.2pp in 2010s (Table III, p. 676)"
    - ref: R5
      outcome: demand-curve multiplier (price impact per unit demand shock)
      metric: coefficient
      value: "M falls from 6.75 in 1995-1999 to 3.58 in 2000-2009 to 0.37 in 2010-2020 for additions (implied elasticity -0.15 to -2.72); from 10.76 to 4.52 to 0.70 for deletions (implied elasticity -0.09 to -1.44)"
      direction: negative
      vsBenchmark: "factor-of-20 decline in multiplier for additions from late 1990s to 2010s (Table V, p. 683)"
    - ref: R6
      outcome: demand-curve multiplier (price impact per unit demand shock)
      metric: coefficient
      value: "After controlling for firm characteristics, M falls from 6.6 to 0.7 for additions (Table VI col 2); with longer window (Ann-20 to Eff+1), M falls from 9.1 to 1.3 (col 3), still a factor-of-7 decline"
      direction: negative
      vsBenchmark: "decline robust to composition controls and longer pre-announcement windows (Table VI, pp. 684-685)"
    - ref: R7
      outcome: cumulative abnormal return around S&P 500 index additions
      metric: car
      value: "Pooled across Russell 1000/2000, S&P MidCap, SmallCap, Nasdaq 100: addition effect declines 4.2pp (significant at 5%); deletion effect shrinks 10.3pp (significant at 1%) from 2000s to 2010s"
      direction: negative
      vsBenchmark: "pattern extends to other index families though less statistically sharp (Table VIII col 9-10, p. 693)"

  resultType: new-finding

  relatesTo:
    - { cite: "Shleifer (1986)", doi: '10.1111/j.1540-6261.1986.tb04518.x', relation: builds-on, note: "documents the original S&P 500 index inclusion effect (~3% around announcement) as evidence of downward-sloping demand" }
    - { cite: "Harris and Gurel (1986)", doi: '10.1111/j.1540-6261.1986.tb04550.x', relation: builds-on, note: "documents price and volume effects of S&P 500 index changes" }
    - { cite: "Bennett, Stulz, and Wang (2020)", doi: '10.3386/w27593', relation: extends, note: "first notes decline in the index inclusion effect between 1997 and 2017; this paper extends the sample, adds deletions, and provides an economic decomposition" }
    - { cite: "Wurgler and Zhuravskaya (2002)", doi: '10.1086/341636', relation: builds-on, note: "provides the arbitrage-risk measure (WZ) used as a control; shows arbitrage risk correlates with index price impact magnitude" }
    - { cite: "McLean and Pontiff (2016)", doi: '10.1111/jofi.12365', relation: cites, note: "documents that anomalies decline after academic publication; authors analogize the index effect decay to this literature" }
    - { cite: "Preston and Soe (2021)", relation: cites, note: "also documents decline in index inclusion and deletion effects beginning in 1995" }
    - { cite: "Vijh and Wang (2022)", doi: '10.1111/fima.12391', relation: cites, note: "documents smaller absolute returns for S&P 500 to MidCap migrations" }
    - { cite: "Chinco and Sammon (2024)", doi: '10.1016/j.jfineco.2024.103860', relation: cites, note: "estimates the passive-ownership share is larger than commonly thought; used to calibrate the size of the index-tracking industry" }

  openQuestions:
    - "Why did it take until the 2010s for arbitrage to eliminate the index effect, despite S&P 500 index changes existing since 1957 and demand shocks continuing to grow? (p. 696)"
    - "Why did the market adapt to index changes more slowly than to other informational anomalies documented in the literature? (p. 696)"
    - "A complete analysis of index-effect decline in the Russell 1000/2000 and Nasdaq 100, including differences in announcement predictability and capital tracked, is left to future work (p. 691)"

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 657-698, 44 pages); seven results extracted from Tables I-VIII and Figures 1-9. DOI confirmed via Crossref; licence confirmed paywalled (Wiley VOR terms). OpenAlex cited_by_count=17. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (Tables I-VIII, equations 1-5, pp. 657-698); two fixes applied: (1) R5 implied-elasticity label corrected from 'additions' to correctly distinguish additions (-0.15 to -2.72) and deletions (-0.09 to -1.44) per Table V; (2) topics field corrected (removed off-topic 'Housing Market and Economics', replaced with accurate topics). All other locators, magnitudes, equations, and significance stars confirmed correct."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13410", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-20; NOT CC-licensed" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model (demand-curve price impact decomposition), and the empirical method behind the decline of the S&P 500 index effect: enough to know what changed and why, without reading all 42 pages. To replicate or extend, read the original at [https://doi.org/10.1111/jofi.13410](https://doi.org/10.1111/jofi.13410).

## TL;DR

The abnormal return earned by a stock added to (or removed from) the S&P 500 peaked at roughly 7-16% in the 1990s and has since fallen to essentially zero in the 2010s, despite index-tracking assets growing from near zero to approximately 7% of market capitalization. Greenwood and Sammon (2025) show this is not explained by changing firm composition. The primary drivers are (i) the growing share of "migrations" from the S&P MidCap 400, where simultaneous forced selling by MidCap trackers offsets forced buying by S&P 500 trackers, and (ii) a factor-of-20 decline in the demand-curve multiplier M (the price impact per unit demand shock), reflecting that active managers and non-S12 institutions now step in to absorb the index demand shock. The paper interprets this as the market adapting to a predictable, repeated trading opportunity, consistent with Lo's (2004) adaptive markets hypothesis.

Early studies by Shleifer (1986) and Harris and Gurel (1986) documented the original index inclusion effect. Bennett, Stulz, and Wang (2020) first noted its decline between 1997 and 2017; this paper extends their analysis to the full 1980-2020 period and covers both additions and deletions. Preston and Soe (2021) also document the decline, and Vijh and Wang (2022) document smaller returns for MidCap-to-S&P migrations. McLean and Pontiff (2016) provide the analogy that anomalies decay after academic publication. Chinco and Sammon (2024) estimate the passive-ownership share is larger than conventionally measured, which implies even larger mechanical demand shocks than previously assumed.

## Core results

Magnitudes and significance as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **S&P 500 addition CAR fell from 7.4% in the 1990s to statistically indistinguishable from zero in the 2010s** | Table I, p. 667; Figure 2, p. 667 | 1980s: 3.4%, 1990s: 7.4%\*\*\*, 2000s: 5.2%\*\*\*, 2010s: 0.8% (insignificant). Decline 2000s to 2010s: -4.3pp\*\*\* (SE 0.93) |
| R2 | **S&P 500 deletion CAR (removal effect) likewise collapsed to zero** | Table I, p. 667; Figure 2, p. 667 | 1980s: -4.6%\*\*, 1990s: -16.1%\*\*\*, 2000s: -12.4%\*\*\*, 2010s: -0.6% (insignificant). Decline 2000s to 2010s: +11.8pp\*\*\* (SE 2.56) |
| R3 | **Changing firm composition (size, arbitrage risk, turnover, analyst coverage) explains only a small part of the decline** | Table II, pp. 671-672 | With controls, decade fixed effects fall from 7.4% to 7.4% (1990s) and from 0.8% to 1.8% (2010s); residual 2010s vs 1990s gap remains -5.6pp\*\*\* (p=0.000) |
| R4 | **Index migrations from MidCap explain a large portion of the decline in addition returns** | Table III, p. 676; Figure 6, p. 677 | Direct additions: 10.2% (1990s), 8.8% (2000s), 5.4% (2010s). Migrations: 6.7% (1990s), 2.7% (2000s), -1.8% (2010s). Migration-nonmigration gap widens from 3.6pp to 7.2pp |
| R5 | **The demand-curve multiplier M declined by a factor of roughly 20 for additions from the 1990s to 2010s** | Table V, p. 683 | Additions M: 6.75 (1995-99), 3.58 (2000-09), 0.37 (2010-20); implied elasticity -0.15 to -2.72. Deletions M: 10.76 (1995-99), 4.52 (2000-09), 0.70 (2010-20); implied elasticity -0.09 to -1.44 |
| R6 | **Decline in M is robust to composition controls and to extended windows that capture front-running** | Table VI, pp. 684-685 | With controls (col 2): M falls from 6.6 to 0.7 (additions). Extended window Ann-20 to Eff+1 (col 3): M falls from 9.1 to 1.3. Factor-of-7 decline even under the most generous front-running window |
| R7 | **Index effect decline extends to other index families (Russell 1000/2000, S&P MidCap, SmallCap, Nasdaq 100)** | Table VIII, p. 693 | Pooled additions: 4.2pp decline from 2000s to 2010s (5% significant). Pooled deletions: 10.3pp decline (1% significant). Individual index results weaker statistically |

**Overall (paper's conclusion).** The index effect grew from the 1980s through the 1990s as passive investing expanded, deepening the arbitrage opportunity. The market then adapted: active managers, institutional investors, and coordinated trading desks now provide liquidity around index events, eliminating the abnormal return on average despite continued growth in index fund assets. The primary mechanisms are migrations from the S&P MidCap (which offset demand shocks) and the rise of sophisticated liquidity provision (which lowers the multiplier M by a factor of ~20). Increased predictability of index changes plays only a minor role.

## Theory / model

The paper has no formal theoretical model but uses a simple structural equation as the organizing framework. Price impact is modeled as a constant-elasticity demand curve hit by a demand shock (equation 1, p. 658):

$$
\text{Price Impact}_{it} = M \times D_{it} \tag{1}
$$

where $$\text{Price Impact}_{it}$$ is the percentage change in price, $$D_{it}$$ is the percentage of market capitalization bought upon index addition (or sold upon deletion), and $$M$$ is minus one over the demand elasticity. Given the rise in indexation, a naive application of this model predicts that price impact should have grown since the 1980s, because the demand shock $$D$$ has been growing. The paper's puzzle is that average price impact (CAR) has instead declined, implying $$M$$ must have fallen substantially.

Taking means of equation (1) by decade and separating migrations (which face offsetting demand from MidCap trackers) from direct additions gives the decomposition (equation 4, p. 681):

$$
\overline{\text{CAR}} = M \times \bar{D} = M \times \left( w \cdot \bar{D}_{\text{Migrations}} + (1 - w) \cdot \bar{D}_{\text{NonMigrations}} \right) \tag{4}
$$

where $$w$$ is the fraction of additions or deletions that are migrations and $$\bar{D}_{\text{Migrations}}$$ and $$\bar{D}_{\text{NonMigrations}}$$ are their respective average net demand shocks. This allows the paper to back out $$M$$ as the ratio of average CAR to the average weighted demand shock, separately by decade beginning in 1995 (when MidCap data start).

**Identification.** The paper is descriptive: it documents time-series variation in event-study returns and uses a structural decomposition to separate the demand-shock channel (migrations) from the multiplier channel (liquidity). There is no causal identification design. The variation exploited is the historical widening of passive ownership and the exogenous timing of S&P 500 inclusion decisions.

## Method

The estimator for individual-event abnormal returns is the market-adjusted cumulative abnormal return (CAR), defined as (equation 2, p. 665):

$$
\text{CAR}_{it} = R_{it} - R_{S\&P\,500, t} \tag{2}
$$

where for announcement returns $$R$$ is the cumulative return from the day before to the day after the announcement, and for effective-date returns $$R$$ is the cumulative return from the day before implementation to the day after. The total return (announcement + effective window) spans the last trading day before announcement to the first trading day after the effective date; the average window is 4.8 days for additions and 5.8 days for deletions (p. 665).

To test whether composition shifts explain the trend, the authors run a cross-sectional regression on the pooled event-level sample (equation 3, p. 670):

$$
\text{CAR}_{it} = b_1 \text{Turn}_{i,t-1} + b_2 \text{Size}_{i,t-1} + b_3 \text{WZ}_{i,t-1} + b_4 \text{Cover}_{i,t-1} + \sum_{k=1}^{4} \gamma_k \mathbf{1}_{\text{era}=k} + e_{it} \tag{3}
$$

where $$\text{Turn}_{i,t-1}$$ is abnormal turnover in the month before the index change (volume/shares outstanding minus market average), $$\text{Size}_{i,t-1}$$ is market capitalization relative to total S&P 500 capitalization at announcement, $$\text{WZ}_{i,t-1}$$ is the Wurgler and Zhuravskaya (2002) arbitrage-risk measure (CAPM residual variance over the prior year), $$\text{Cover}_{i,t-1}$$ is analyst coverage from IBES, and $$\mathbf{1}_{\text{era}=k}$$ are decade fixed effects. All characteristics are demeaned. Standard errors use White (1980) heteroskedasticity-consistent variance estimators (Table II, p. 672).

For the multiplier estimation, the regression interacts the average net demand shock $$D_{\text{era}=k}$$ with decade indicators (equation 5, p. 686):

$$
\text{CAR}_{it} = b_1 \text{Turn}_{i,t-1} + b_2 \text{Size}_{i,t-1} + b_3 \text{WZ}_{i,t-1} + b_4 \text{Cover}_{i,t-1} + \sum_{k=1}^{3} \gamma_k \mathbf{1}_{\text{era}=k} \times D_{\text{era}=k} + e_{it} \tag{5}
$$

The $$\gamma_k$$ coefficients estimate the multiplier $$M$$ for each decade after controlling for firm characteristics (Table VI, pp. 684-685). The paper builds on the `event-study` and `panel-regression` primitives.

## Empirical specifications

All specifications are event-study regressions with market-adjusted returns. Key design choices:

- **Sample:** 736 S&P 500 additions and 731 deletions from Siblis Research, 1980-2020, matched to CRSP; pre-1990 announcement dates from Barberis, Shleifer, and Wurgler (2005). Observations with ACPERM within 100 days (acquisitions) and spinoffs excluded. Consistent sample for characteristic regressions requires Thompson S12 matching.
- **Return window (baseline):** Last trading day before announcement to first trading day after effective date (total window, roughly 5 days average). Sensitivity: extended to Ann-20 (20 trading days pre-announcement) to Eff+1 to capture front-running (Table VI cols 3-4, 7-8).
- **Event-study benchmark:** S&P 500 index return over the same window (market-adjusted). The market return is used rather than risk-model betas to avoid contamination from the index change itself (p. 665).
- **Composition controls (Table II):** CAR regressed on demeaned $$\text{Turn}$$, $$\text{Size}$$, $$\text{WZ}$$, $$\text{Cover}$$, and decade dummies; N=610 additions, 237 deletions; robust standard errors (White 1980). R-squared of 0.26-0.35 for additions.
- **Migration analysis (Tables III, V, VI):** MidCap changes from Siblis Research from 1995; MidCap 400 trackers identified by name/return correlation (at least 99.5% correlation to the MidCap index). Net demand shock D measured as Thompson S12 net buying by index trackers (change in split-adjusted shares held quarter before to quarter after, divided by shares outstanding).
- **Multiplier estimation (Tables V-VI):** M backed out as $$\overline{\text{CAR}} / \bar{D}$$ by decade (Table V), then via the interacted regression (equation 5) with characteristic controls (Table VI). Demand elasticity implied as $$\varepsilon = -1/M$$.
- **Institutional ownership (Table VII):** Thompson 13F ownership changes quarter before to quarter after compared to tracker net buying; active/passive distinction from Appel, Gromley, and Keim (2016).
- **Other indices (Table VIII):** Russell 1000/2000 from FTSE Russell 1990-2020; S&P MidCap/SmallCap from Siblis 1995-2020; Nasdaq 100 from Siblis 1995-2020. Returns market-adjusted; events use 10 days before effective date to one day after (no announcement dates for MidCap/SmallCap/Nasdaq); clustered by year.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP daily stock returns and shares outstanding | Cumulative abnormal returns; split-adjustment factors; market-cap computation | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Thompson S12 mutual fund holdings (quarterly) | Identifying S&P 500 and MidCap 400 tracking funds; measuring net buying/selling around index changes | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Thompson 13F institutional holdings (quarterly) | Changes in total institutional ownership around index changes (Table VII) | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Siblis Research S&P 500 addition/deletion history | Announcement and effective dates for S&P 500 changes, 1980-2020; also MidCap 400 and SmallCap changes | No page yet |
| Barberis, Shleifer, and Wurgler (2005) | Pre-1990 S&P 500 addition announcement dates not in Siblis | No page yet |
| IBES analyst coverage | Analyst coverage count for each firm at earnings announcement before the index change (control variable Cover) | [WRDS](/wiki/licensed/wrds/) (licensed) |
| WRDS Intraday Indicators (TAQ-based) | Value-weighted average effective bid-ask spread (percent effective spread) from TAQ data 1993-2022, using Holden-Jacobsen (2014) method | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Virtu Financial implementation shortfall | Implementation shortfall for midcap stocks 2009-2021 | No page yet |
| FTSE Russell index membership | Russell 1000 and Russell 2000 additions/deletions, 1990-2020 | No page yet |

Sample: S&P 500 changes 1980-2020; MidCap/SmallCap/Nasdaq/Russell changes from 1990 or 1995 depending on data source. Returns at daily frequency; holdings at quarterly frequency.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13410) if you are: replicating the demand-curve decomposition or extending the multiplier analysis to post-2020 data; studying the mechanics of passive investing and price impact around index rebalancing events; testing whether similar patterns hold for factor-index (e.g., ESG or smart-beta) additions/deletions; or evaluating the market efficiency implications of mechanical, predictable institutional demand shocks. Table I (p. 666-667) gives the full year-by-year CAR history; Tables V-VI (pp. 683-685) give the migration-adjusted M estimates; Table VIII (p. 693) gives the other-index results.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled (Wiley VOR licence); only extracts are reproduced here.

> Greenwood, Robin, and Marco Sammon. "The Disappearing Index Effect."
> *The Journal of Finance* 80, no. 2 (April 2025): 657–698.
> DOI: 10.1111/jofi.13410. © 2024 the American Finance Association.
> All rights reserved. Extract-only reproduction under fair-use/commentary.
