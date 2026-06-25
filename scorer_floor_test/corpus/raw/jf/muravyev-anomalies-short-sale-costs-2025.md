---
title: "Anomalies and Their Short-Sale Costs: Muravyev, Pearson & Pollet (2025)"
description: >-
  Distilled: across 162 asset pricing anomalies, average long-short abnormal
  returns of 0.14%/month vanish once stock borrow fees are accounted for,
  either by fee adjustment or by dropping high-fee stocks; the result holds
  for subsets including microcaps, high-fee anomalies, and factor-mimicking
  portfolios. J. Finance 2025, CC BY 4.0. Nine core results with source
  locators, datasets used, the identification strategy, and the estimating
  specifications with exact panel-regression equations.
sidebar:
  label: Muravyev-Pearson-Pollet 2025
  order: 1
tags: [paper-summary, anomalies, short-selling, asset-pricing, limits-to-arbitrage, portfolio-sort, panel-regression, open-access, cc-by, peer-reviewed, unreplicated, data:wrds, data:open-source-asset-pricing, data:markit-securities-finance]
paper:
  authors: Dmitriy Muravyev, Neil D. Pearson, Joshua M. Pollet
  authorList:
    - { family: Muravyev, given: "Dmitriy", affiliation: "Gies College of Business, University of Illinois at Urbana-Champaign; Canadian Derivatives Institute" }
    - { family: Pearson, given: "Neil D.", affiliation: "Gies College of Business, University of Illinois at Urbana-Champaign; Canadian Derivatives Institute" }
    - { family: Pollet, given: "Joshua M.", affiliation: "Gies College of Business, University of Illinois at Urbana-Champaign" }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3639-3694
  venueShort: J. Finance 2025
  licenseShort: CC BY 4.0
  resultsCount: 9
  citedByCount: 5
  jel:
    codes: [G12, G14]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Insurance and Financial Risk Management']
  dataAccess: licensed-commercial
  outcome:
    - cross-sectional anomaly long-short returns
    - net-of-fee long-short abnormal returns across 162 anomalies
  outcomeClass: [security-returns]
  doi: 10.1111/jofi.13501
  license: 'CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-09-30; corroborated by artifact p.3639 Creative Commons Attribution License statement)'
  access: open
  machineAccess: 'blocked-paywall (Wiley site wrapper; not tested directly 2026-05-31; CC-BY VOR licence confirmed in Crossref DOI metadata)'
  redistribution: 'extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)'
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [portfolio-sort, panel-regression]
    identification: descriptive
  contributionType: [new-fact, measurement]
  mechanisms: [limits-to-arbitrage]
  scope:
    region: US
    assetClass: US equities (CRSP common stocks)
    period: 2006-07..2020-12
    frequency: monthly
    dataType: [market, accounting]
    granularity: [security]
    n: "554,253 stock-months (162 anomaly signals, Jul 2006-Dec 2020)"
  findings:
    - { ref: R1, outcome: cross-sectional anomaly long-short returns, metric: alpha, value: "0.14%/mo, t=2.87", direction: positive }
    - { ref: R2, outcome: net-of-fee long-short abnormal returns across 162 anomalies, metric: alpha, value: "0.04%/mo, t=0.84", direction: none, vsBenchmark: "below unadjusted full-sample mean of 0.14%/mo" }
    - { ref: R3, outcome: net-of-fee long-short abnormal returns across 162 anomalies, metric: alpha, value: "-0.01%/mo, t=-0.24", direction: none }
    - { ref: R4, outcome: cross-sectional anomaly long-short returns, metric: coefficient, value: "-0.0883, t=-1.96", direction: negative }
    - { ref: R5, outcome: cross-sectional anomaly long-short returns, metric: alpha, value: "before-fee L/S +0.36% (t=5.06); excl. high-fee +0.11% (t=1.39); net-of-fee -0.05% (t=-0.62)", direction: mixed, vsBenchmark: "net-of-fee vs. before-fee microcap L/S" }
    - { ref: R6, outcome: net-of-fee long-short abnormal returns across 162 anomalies, metric: alpha, value: "excl. high-fee -0.04% (t=-0.21); net-of-fee 0.02% (t=0.10)", direction: none }
    - { ref: R7, outcome: net-of-fee long-short abnormal returns across 162 anomalies, metric: alpha, value: "momentum -0.01% (t=-0.11); profitability 0.21% (t=0.59)", direction: none }
    - { ref: R8, outcome: cross-sectional anomaly long-short returns, metric: alpha, value: "CAPM L/S 0.45% (t=0.81); tail-risk L/S 0.43% (t=0.97)", direction: none }
    - { ref: R9, outcome: net-of-fee long-short abnormal returns across 162 anomalies, metric: alpha, value: "0.03%, t=0.47", direction: none, vsBenchmark: "vs. -0.24% (t=-2.92) in unadjusted Panel A" }
  resultType: overturns
  relatesTo:
    - { cite: 'Chen & Zimmermann (2021)', doi: '10.1561/104.00000112', relation: builds-on, note: 'Uses their 162 anomaly signals from openassetpricing.com as the universe of tested anomalies (p. 3648)' }
    - { cite: 'Drechsler & Drechsler (2021)', relation: contradicts, note: 'That paper finds positive net-of-fee returns on eight anomalies using lender-side fees; this paper uses buy-side fees and a longer, more recent sample and finds near-zero net-of-fee returns (pp. 3643, 3646)' }
    - { cite: 'Hou, Xue & Zhang (2020)', relation: tests, note: 'Tests their claim that anomaly returns are concentrated in microcaps; finds that even microcap anomaly returns disappear once borrow fees are accounted for (pp. 3642, 3668)' }
    - { cite: 'Nagel (2005)', doi: '10.1016/j.jfineco.2004.08.008', relation: builds-on, note: 'Limits-to-arbitrage framework connecting short-sale constraints to anomaly persistence (p. 3643)' }
    - { cite: 'Stambaugh, Yu & Yuan (2012)', doi: '10.1016/j.jfineco.2011.12.001', relation: builds-on, note: 'Framework connecting short-sale costs to anomaly persistence via sentiment (p. 3643)' }
    - { cite: 'Daniel, Grinblatt, Titman & Wermers (1997)', doi: '10.1111/j.1540-6261.1997.tb02724.x', relation: builds-on, note: 'Characteristics-matched DGTW benchmark used to compute abnormal returns throughout (p. 3654)' }
  openQuestions:
    - 'Why long-side investors continue to hold high-borrow-fee decile 1 stocks despite bearing negative expected returns; candidate explanations include index-fund tracking constraints, capital-gains tax consequences, and inability to identify high-fee stocks (pp. 3679-3680, 3692).'
    - 'Whether the results hold at daily or weekly strategy frequencies, which the paper leaves outside its scope because execution costs scale with trade frequency differently than borrow fees (p. 3644 fn. 4).'
    - 'Whether the causality runs primarily from mispricing to borrow fees or from borrow fees to the absence of short arbitrage; the paper notes that both directions likely operate simultaneously (pp. 3642-3643).'
  replicationCode:
    status: available
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13501
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-09-30'
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full text read (pp. 3639-3694, 12 tables, 12 figures); nine results extracted from the CC-BY PDF. Not human-verified. Not reproduced. Replication code is published as Supporting Information but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-01
      role: extracted
      note: Augment pass. Added methods, scope, relatesTo, openQuestions, replicationCode, proposedVocab frontmatter blocks and three formal body sections (Theory / model, Method, Empirical specifications) with equations and panel-regression specifications transcribed from pp. 3654-3671 of the source PDF read this session. Core results table and Attribution preserved verbatim from the verified version. New sections are extracted, not yet re-verified.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-01
      role: verified
      note: 'Locators and reported magnitudes re-checked against source PDF for all 9 rows; all confirmed correct. One fix applied: decile 2 fee-adjustment treatment corrected from "long-side" to "short-side" (full fee added), matching p. 3650 of the PDF. No em-dashes found; no colorful adjectives found.'
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Added classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) from a fresh PDF read; existing results and
        sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) re-checked against the source PDF; all axes
        confirmed correct - no fixes required.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the page's already-verified Core-results table and
        relatesTo edges; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; all 9 values confirmed exact matches to Tables III,
        IV, V, VI, IX, XI, XII - no fixes required.
  rightsSignalConflict: false
---

**What this is.** The paper's core results, datasets, identification strategy, and the estimating equations: enough to know what it found and how without reading all 56 pages. To replicate or extend it, read the original at
[doi.org/10.1111/jofi.13501](https://doi.org/10.1111/jofi.13501).

## TL;DR

Using 162 anomalies from Chen and Zimmermann (2021) and stock borrow fee data
from Markit (July 2006 to December 2020), the paper shows that the average
long-short abnormal return of 0.14%/month is entirely due to high-fee stocks
(borrow fee greater than 1%/year, roughly 12% of stock-month observations).
Once high-fee stocks are excluded, or once returns are adjusted for the borrow
fee, the average long-short abnormal return collapses to 0.04% or -0.01%/month,
respectively, neither significantly different from zero. The result holds across
microcap stocks, the 20 anomalies with the highest fees, four factor-mimicking
portfolios (momentum, profitability, investment, book-to-market), and five
individually named anomalies. Portfolios sorted on theoretically grounded risk
measures (CAPM beta, tail-risk beta) are unaffected, serving as a placebo.
A short-interest-to-institutional-holdings ratio (from Compustat/13F) works as
a publicly available proxy for borrow fees, eliminating the need for Markit data
to test exploitability.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Average long-short **abnormal return across 162 anomalies is 0.14%/month before fees**, significantly positive | Table III Panel A, p. 3659 | Mean = 0.14%/mo, t-stat = 2.87\*\*\* |
| R2 | **High-fee stocks drive the long-short return**: excluding stocks with borrow fee > 1%/yr, long-short abnormal return drops to 0.04% and is insignificant | Table III Panel B, p. 3659 | Mean = 0.04%/mo, t-stat = 0.84 |
| R3 | **Fee-adjusted long-short return is near zero** (borrow fee added back to short-side returns for full sample) | Table III Panel C, p. 3659 | Mean = -0.01%/mo, t-stat = -0.24 |
| R4 | **Unadjusted decile 1 abnormal returns are approximately linear in the borrow fee**, slope -0.088 (approx. -1/12 per 1 ppt fee) | Table V col. 1, p. 3671 | Slope = -0.0883, t-stat = -1.96\* |
| R5 | **Microcap anomaly returns are also entirely due to high-fee stocks**: before fees decile 1 = -0.48%/mo (t = -2.92); excluding high-fee stocks decile 1 = +0.09% (t = 0.76); fee-adjusted = +0.08% (t = 0.50) | Table IV, p. 3669 | Before-fee L/S = +0.36% (t = 5.06); after drop = +0.11% (t = 1.39); net-of-fee = -0.05% (t = -0.62) |
| R6 | **High-fee anomaly subset (20 anomalies, avg fee > 4%/yr)**: before-fee long-short = 0.41%/mo (t = 2.08); excluding high-fee stocks = -0.04%/mo; fee-adjusted long-short = 0.02%/mo (near zero, insignificant) | Table VI, p. 3673 | Exclud. high-fee L/S = -0.04% (t = -0.21); net-of-fee = 0.02% (t = 0.10) |
| R7 | **Momentum and profitability factor long-short returns are eliminated by borrow fees**: momentum L/S drops from 0.21% to 0.03%/mo after excluding high-fee stocks, profitability from 0.61% to 0.09%/mo; net-of-fee momentum = -0.01%, profitability = 0.21%/mo (annualizes to 2.52%/yr, insignificant) | Table XI, p. 3688 | Momentum net-of-fee L/S: -0.01% (t = -0.11); profitability net-of-fee: 0.21% (t = 0.59) |
| R8 | **CAPM-beta and tail-risk-beta sorted portfolios are unaffected** by borrow fee exclusion or adjustment (placebo): CAPM L/S net-of-fee = 0.45%/mo (t = 0.81), tail-risk L/S net-of-fee = 0.43%/mo (t = 0.97) | Table XII, p. 3690 | Net-of-fee CAPM L/S = 0.45%, tail-risk L/S = 0.43%; both insignificant |
| R9 | **Short-interest-to-institutional-holdings ratio (Compustat/13F, no Markit needed) replicates the main result**: excluding stocks with SI/IO > 18% reduces decile 1 abnormal return by 0.27%/mo relative to Panel A | Table IX Panel D, p. 3682 | SI/IO exclusion decile 1: 0.03% (t = 0.47) vs. -0.24% (t = -2.92) in Panel A |

**Overall (paper's conclusion).** Stock borrow fees function as a common limit
to arbitrage that is sufficient to explain the persistence of anomaly returns
for marginal investors. The average anomaly cannot be profitably exploited via
long-short strategies once shorting costs are incorporated. The residual puzzle
is why long-side investors continue to hold high-fee stocks despite bearing
negative expected returns relative to low-fee benchmarks.

## Theory / model

The paper has no original structural model. It is an applied empirical study
operating in the limits-to-arbitrage tradition (Lee, Shleifer, and Thaler (1991);
Nagel (2005); Stambaugh, Yu, and Yuan (2012)). The tested hypothesis is:

> Stock borrow fees are a common, binding limit to arbitrage that prevents
> exploitation of cross-sectional return anomalies and explains their
> apparent out-of-sample persistence.

**Conceptual identity: borrow fee as shadow dividend.** A short seller pays the
daily borrow fee for every day a short position is open. A long-side investor
whose shares are lent receives the fee less prime-broker intermediation spreads,
but only on the fraction of shares actually borrowed. The fee is therefore a
shadow dividend not recorded in CRSP stock returns. The paper's identification
logic follows directly (pp. 3640-3641, 3650):

$$
\begin{aligned}
R^{\text{short,adj}} &= R_{\text{stock}} + f \\
R^{\text{long,adj}}  &= R_{\text{stock}} + \text{utilization} \times (1 - \text{spread\_fraction}) \times f \\
                     &\approx R_{\text{stock}} + \text{utilization} \times 0.7 \times f
\end{aligned}
$$

- $$f$$ = indicative borrow fee (annualized, converted to monthly)
- $$\text{utilization}$$ = shares on loan / lendable shares
- D'Avolio (2002) estimates the spread fraction at approximately 0.3

In contrast to Drechsler and Drechsler (2021), who find positive net-of-fee
returns on eight anomalies using lender-side fees, this paper uses buy-side
fees over a longer and more recent sample and finds near-zero net-of-fee
returns.

**Identification design.** Two complementary approaches test whether anomaly
returns survive after accounting for fees (p. 3640):

1. Exclude high-fee stocks: drop stock-month observations with indicative borrow
   fee > 1%/year from the sorted portfolios (without resorting). Approximately
   12% of stock-months qualify as high-fee; 21% of decile 1 observations do.
2. Fee-adjust returns: add the full fee to returns for short-side portfolios
   (deciles 1 and 2); add $$\text{utilization} \times 0.7 \times f$$ to returns for long-side
   portfolios (deciles 3-10).

Both approaches use a DGTW characteristics-matched benchmark that excludes
high-fee stocks from the benchmark portfolios to avoid contaminating the
abnormal-return calculation (p. 3654 fn. 16).

**Placebo test.** Portfolios sorted by CAPM beta and tail-risk beta (Kelly and
Jiang (2014)) are theoretically grounded risk measures, not behavioral anomalies.
If borrow fees reflect arbitrage frictions specific to mispriced stocks, these
sorted portfolios should be insensitive to borrow-fee adjustments. The
insensitivity result (Table XII, p. 3690) provides placebo support.

## Method

The paper applies `portfolio-sort` and `panel-regression` methods. There is no
newly proposed estimator; the methodological contribution is the systematic
application of buy-side borrow fees to a comprehensive, out-of-sample anomaly
universe.

**DGTW abnormal return construction (pp. 3654-3655).** For each stock $$i$$ and
month $$t$$, the abnormal return is:

$$
\text{DGTW\_ETB}_{i,t} = R_{i,t} - R_{\text{benchmark},i,t}
$$

- $$R_{\text{benchmark},i,t}$$ is the equal-weighted return of the DGTW characteristics-matched portfolio, constructed excluding stocks with borrow fee > 1%/year (to prevent high-fee benchmark contamination). The benchmark portfolios match on market capitalization, book-to-market, and prior six-month momentum, following Daniel et al. (1997).

**Portfolio-level aggregation.** The abnormal return on a sorted decile
portfolio in month $$t$$ is the cross-sectional average of stock-level abnormal
returns within that decile. For each anomaly, the time-series average is
computed over the performance evaluation period (July 2006 to December 2020,
14.5 years). The cross-sectional mean across the 162 anomalies is the headline
statistic (p. 3654).

**Fee adjustment procedure (pp. 3650, 3666-3667).** The monthly fee is the
simple average of daily indicative fees over the 21-trading-day return
evaluation window. For decile 1 stocks (short side), the full fee is added to
the stock return. For decile 3-10 stocks (long side, held or lent), the
expected fee received is:

$$
\text{fee\_received}_{i,t} = \text{utilization}_{i,t} \times 0.7 \times f_{i,t}
$$

This is added to the stock return. Decile 2 uses the same adjustment as decile
1 in both the fee-exclusion analysis and the fee-adjustment analysis (i.e., the
full fee is added to decile 2 stock returns, treating it as short-side).

**Standard-error treatment.** All t-statistics on cross-sectional averages are
computed using a panel regression in which the monthly portfolio return for each
anomaly is regressed onto decile fixed effects; standard errors are
double-clustered by anomaly and month. The estimate for each decile fixed effect
is the average return on the corresponding decile with the appropriate
t-statistic (pp. 3655-3656).

## Empirical specifications

The paper's results come from three types of portfolio-performance constructions
rather than a single OLS regression. Each is described below with the estimating
equation.

**Specification 1: Cross-sectional mean of decile abnormal returns (R1-R3,
R5-R6, Table III p. 3659).**

For each anomaly $$a$$, the time-series average abnormal return on decile $$d$$ is:

$$
\mu_{a,d} = \frac{1}{T} \sum_{t=1}^{T} \text{DGTW\_ETB}_{a,d,t}
$$

The cross-sectional mean across anomalies (the headline statistic) and the
corresponding t-statistic are extracted from the panel regression:

$$
\text{DGTW\_ETB}_{a,d,t} = \alpha_d + \epsilon_{a,d,t}
$$

- LHS: monthly decile portfolio abnormal return for anomaly $$a$$, decile $$d$$, month $$t$$
- RHS: decile fixed effects $$\alpha_d$$ (one per decile 1-10)
- SE: double-clustered by anomaly $$a$$ and month $$t$$
- Sample: 162 anomalies, July 2006 to December 2020, varying N per anomaly

The long-short result is $$\alpha_1 - \alpha_{10}$$ (decile 1 minus decile 10, since
anomaly signals are signed so decile 1 is the short side). The procedure is
applied in three versions: (A) all stocks, no fee adjustment; (B) excluding
high-fee stocks (fee > 1%/yr); (C) fee-adjusted returns.

**Specification 2: Relation between anomaly returns and borrow fees (R4,
Table V p. 3671).**

For each anomaly, the average decile 1 borrow fee $$f_a$$ is regressed on the
average abnormal return to show the approximately linear relationship:

$$
\mu_{a,1} = \beta_0 + \beta_1 f_a + u_a
$$

- LHS: time-series average abnormal return on decile 1 portfolio, anomaly $$a$$
- RHS: average indicative borrow fee for decile 1 stocks of anomaly $$a$$ at portfolio formation date
- SE: double-clustered by anomaly and month (panel version with month controls)
- Key result: $$\beta_1 = -0.0883$$ (t = -1.96*), approximately $$-1/12$$

The slope of approximately $$-1/12$$ means a 1 percentage-point increase in the
annual fee corresponds to roughly $$-1/12$$ percentage points per month in abnormal
return, consistent with complete fee absorption of the anomaly signal (p. 3671).

**Specification 3: SI/IO exclusion as Markit substitute (R9, Table IX Panel D
p. 3682).**

The same Specification 1 panel regression is applied after excluding
stock-months where short interest divided by institutional holdings (SI/IO,
from Compustat monthly short interest and 13F filings) exceeds 18%:

$$
\text{DGTW\_ETB}_{a,d,t} = \alpha_d + \epsilon_{a,d,t} \quad \text{[restricted sample]}
$$

- Restriction: drop stock-months with $$(\text{short\_interest}_{i,t-1} / \text{inst\_holdings}_{i,t-1}) > 0.18$$
- Cutoff 18% chosen to match approximately 12% of stock-months excluded by fee > 1% cutoff
- SE: double-clustered by anomaly and month
- Key result: decile 1 $$\alpha$$ changes by +0.27%/mo relative to unadjusted baseline, decile 1 $$\alpha$$ = +0.03% (t = 0.47) vs. -0.24% (t = -2.92) with all stocks

Robustness: microcap extension (all stocks, market cap below 20th percentile
NYSE, Table IV p. 3669), which tests the claim of Hou, Xue, and Zhang (2020)
that anomaly returns are concentrated in microcaps and finds that even microcap
anomaly returns disappear once borrow fees are accounted for; 20 highest-fee anomalies (Table VI p. 3673); subsets
by t-statistic, pre-sample Sharpe ratio, and publication venue (Table VII
p. 3674); long-side investor perspective with varying intermediation fractions
(Table VIII p. 3678); five specific anomalies (Table X p. 3685); four
factor-based long-short portfolios (Table XI p. 3688).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Chen and Zimmermann (2021) anomaly signals (openassetpricing.com), Jan 2000 to Dec 2020; 202 anomalies, 162 retained | Anomaly signal construction; decile portfolio assignment | [Open Source Asset Pricing](/wiki/datasets/open-source-asset-pricing/) |
| Markit Securities Finance Buy Side Analytics Data Feed, daily from Jun 28 2006 | Stock borrow fees (indicative fee = buy-side expected borrow cost); utilization | no page yet |
| CRSP (via WRDS) common stocks, returns, delisting returns | Stock returns, market cap filters, sample construction | [WRDS / CRSP / Compustat](/wiki/licensed/wrds/) (licensed) |
| Compustat (via WRDS) short interest + 13F institutional holdings | Proxy for borrow fee (SI/IO ratio) for researchers without Markit access | [WRDS / CRSP / Compustat](/wiki/licensed/wrds/) (licensed) |

Sample: 554,253 stock-months (162 anomaly signals, Jul 2006 to Dec 2020),
after dropping stocks below $1 price or $50 mn market cap and requiring at
least 4 days of borrow fee observations per month.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13501) if you are: replicating
(code in the journal's Supporting Information); extending the borrow fee
adjustment methodology; examining the specific anomaly-by-anomaly results in
the Internet Appendix; or auditing factor return attrition (Section VI). The
locators above point to the exact tables. For "what did this paper find," the
table above is the intended default.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was
extracted by an LLM on 2026-05-31 and augmented on 2026-06-01; it is **not
human-verified or independently reproduced**. CC BY 4.0 permits this adaptation;
the verbatim PDF is not hosted in this batch but CC permits mirroring.

> **Attribution (CC BY 4.0).** Muravyev, Dmitriy, Neil D. Pearson, and Joshua
> M. Pollet. "Anomalies and Their Short-Sale Costs." *The Journal of Finance*
> 80, no. 6 (December 2025): 3639-3694. DOI: 10.1111/jofi.13501.
> Copyright 2025 The Author(s). Licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
