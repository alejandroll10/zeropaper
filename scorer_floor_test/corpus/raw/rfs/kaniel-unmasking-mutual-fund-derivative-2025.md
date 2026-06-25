---
title: "Unmasking Mutual Fund Derivative Use: Kaniel & Wang (2025)"
description: >-
  Distilled: Using SEC Form N-PORT data, this paper shows that most
  mutual funds (59%) use derivatives to amplify, not hedge, equity returns,
  contrary to prior belief. Five derivative strategy clusters are identified
  via K-Means Clustering; long index users dominate and underperform
  nonusers despite attracting abnormally high institutional flows.
  Review of Financial Studies 2025, paywalled. Eight core results with
  source locators, datasets used, the method, and empirical specifications.
sidebar:
  label: Kaniel-Wang 2025
  order: 1
tags: [paper-summary, mutual-funds, derivatives, fund-behavior, asset-pricing,
       panel-regression, machine-learning, peer-reviewed, unreplicated,
       data:wrds, data:edgar]
paper:
  authors: Ron Kaniel, Pingle Wang
  authorList:
    - { family: Kaniel, given: Ron, affiliation: Simon Business School, University of Rochester; FISF, Fudan; CEPR }
    - { family: Wang, given: Pingle, orcid: "0000-0003-2585-7062", affiliation: Jindal School of Management, The University of Texas at Dallas }
  year: 2025
  venue: The Review of Financial Studies 38(4), 2025, 1120–1166
  venueShort: Rev. Financ. Stud. 2025
  doi: 10.1093/rfs/hhaf001
  jel:
    codes: [G11, G12, G23]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Financial Markets and Investment Strategies", "Banking stability, regulation, efficiency", "Housing Market and Economics"]
  dataAccess: licensed-commercial
  outcome:
    - derivative-induced returns of mutual funds
    - derivative relative contribution to fund returns
    - fund flows by derivative strategy
    - fund risk-adjusted performance by derivative strategy
  outcomeClass: [fund-behavior, security-returns]
  license: >-
    OUP standard publication reuse rights (content-version vor,
    URL https://academic.oup.com/pages/standard-publication-reuse-rights,
    delay-in-days 0, start 2025-01-09); not CC-licensed; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (OUP site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 11

  methods:
    role: both
    contributes: derivative-strategy-clustering
    family: descriptive
    buildsFrom: [panel-regression, fama-macbeth]
    identification: descriptive
  contributionType: [new-data, new-fact, measurement]
  introducesData: true
  mechanisms: [agency, information-asymmetry]
  scope:
    region: US
    assetClass: US active equity mutual funds
    period: 2019-07..2022-12
    frequency: monthly
    dataType: [market, accounting, administrative]
    granularity: [firm, security]
    n: "3,106 active domestic equity funds; 1,079 derivative users (34.7%); July 2019 to December 2022"

  findings:
    - ref: R1
      outcome: derivative-induced returns of mutual funds
      metric: basis-points
      value: "average monthly DIR = -6.5 bps; average monthly non-DIR = 20.7 bps (std dev 531 bps vs 78 bps)"
      direction: negative
      vsBenchmark: nonderivative positions outweigh derivative positions 40x by magnitude; std dev of non-DIR only 6x larger
    - ref: R2
      outcome: derivative relative contribution to fund returns
      metric: probability
      value: "59% of derivative users have positive DIR-non-DIR correlation; median correlation 0.17; equity derivative users 64% positive, median 0.43"
      direction: positive
      vsBenchmark: contradicts prior hedging view; majority amplify equity returns
    - ref: R3
      outcome: derivative-induced returns of mutual funds
      metric: coefficient
      value: "long index: persistence AR coef 0.832*** (t=21.82, N=1,624); long stock 0.915*** (t=12.16); short index 0.883*** (t=22.53); short stock 0.956*** (t=10.15); nonequity 0.776*** (t=18.99)"
      direction: positive
      vsBenchmark: token users AR coef only 0.084 (t=3.95), confirming strategy persistence among nontoken users
    - ref: R4
      outcome: fund flows by derivative strategy
      metric: pp-effect
      value: "long index users receive 0.2% more monthly fund flows than nonusers (2.4% annually); significant at 5% level; driven by institutional share classes (columns 4-6)"
      direction: positive
      vsBenchmark: all other derivative users receive 0.1% more flows monthly vs nonusers; retail flows not significantly higher
    - ref: R5
      outcome: fund risk-adjusted performance by derivative strategy
      metric: alpha
      value: "long index FF5 alpha = -1.450*** (t=-2.91) vs nonusers -0.834* (t=-1.90); long index - nonusers difference = -0.617** (t=-2.20) annualized pp; benchmark-adj. underperformance 0.36-0.62 pp depending on measure"
      direction: negative
      vsBenchmark: long index users underperform nonusers by 0.36-0.62 pp annually on all five performance measures (2011-2022 extended CRSP sample)
    - ref: R6
      outcome: derivative-induced returns of mutual funds
      metric: basis-points
      value: "COVID outbreak: long index users underperformed other derivative users by 4.85% per month; 0.85% from DIR (-47.60 vs +37.11 bps gap = -84.71*** bps), 4% from non-DIR (Table 8, Panel A)"
      direction: negative
      vsBenchmark: derivatives contributed 18% of long index underperformance gap during outbreak; active equity trading drove the rest
    - ref: R7
      outcome: derivative-induced returns of mutual funds
      metric: basis-points
      value: "COVID recovery: long index users gained from DIR by only 6.3 bps per month; all others DIR = -54.92 bps; long index - all others total DIR gap = +61.22** bps; active DIR component difference = 5.42 bps (n.s.) (Table 8, Panel B)"
      direction: mixed
      vsBenchmark: long index users neither outperformed in outbreak nor recovery, despite doubling derivative use
    - ref: R8
      outcome: fund flows by derivative strategy
      metric: pp-effect
      value: "high-CTE long index users received abnormally high institutional flows pre-COVID (coef 0.284***, t=3.16) consistent with risk-shifting channel; low-CTE users did not (coef 0.089, t=1.11) (Table 10)"
      direction: positive
      vsBenchmark: supports risk-shifting over flow-management channel for institutional investor allocation to long index funds

  resultType: overturns

  relatesTo:
    - { cite: "Koski and Pontiff (1999)", doi: '10.1111/0022-1082.00126', relation: contradicts, note: "prior survey evidence suggested most funds use derivatives to hedge; this paper shows 59% amplify equity returns using granular N-PORT PnL data" }
    - { cite: "Cao, Ghysels, and Hatheway (2011)", doi: '10.1002/fut.20489', relation: extends, note: "extends their finding of derivative effects on fund returns by adding monthly-level PnL decomposition and K-Means strategy classification" }
    - { cite: "An, Huang, Lou, and Shi (2021)", relation: extends, note: "extends their long/short equity fund anatomy with the derivative-strategy classification and flow-management evidence for long index users" }
    - { cite: "Frino, Lepone, and Wong (2009)", doi: '10.1016/j.jbankfin.2008.10.001', relation: tests, note: "tests their flow-management hypothesis as alternative explanation for institutional flows to long index users; evidence is mixed" }
    - { cite: "Glode (2011)", relation: tests, note: "tests their model that mutual funds underperform in normal times but outperform in crises; long index users fail the crisis-period outperformance prediction" }

  openQuestions:
    - "Why funds use derivatives and quantifying the benefits more comprehensively is left for future studies; the paper notes this likely deserves a paper on its own (p. 1165)."
    - "The sample is short (3 years of N-PORT) to reliably estimate performance over market cycles; the paper relies on imperfect CRSP data since 2010 for the extended sample (p. 1126, 1158)."
    - "The paper cannot fully separate the risk-shifting and flow-management explanations for institutional flows to long index users; both remain plausible (pp. 1162-1163)."

  replicationCode:
    url: "https://doi.org/10.7910/DVN/TQCGER"
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1120-1166, RFS 38(4) 2025). Eight results extracted from the paywalled PDF. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; four fixes applied: (1) R3 short stock t-stat corrected from t=18.84 to t=10.15 per Table 3 col 5; (2) R3 Core table magnitude updated to include all t-stats; (3) R6 all-others DIR during outbreak corrected from -54.92 to +37.11 bps per Table 8 Panel A (−54.92 is the Panel B recovery value); (4) R7 DIR gap corrected from '5.42* bps' (active DIR component, not significant) to the total DIR gap of 61.22** bps per Table 8 Panel B."

  licenceVerification:
    - { source: "Crossref REST API works/10.1093/rfs/hhaf001", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-01-09; no CC licence present; paywalled" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the data and method it contributes (SEC Form N-PORT derivative positions with monthly PnL plus K-Means Clustering of derivative strategies), and the empirical specifications behind each result: enough to know what it found and how, without reading all 47 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1093/rfs/hhaf001).

## TL;DR

Using newly available SEC Form N-PORT data (July 2019 to December 2022), Kaniel and Wang (2025) are the first to directly measure how mutual fund derivative positions contribute to fund returns. Contrary to the common belief that funds use derivatives to hedge, the paper finds that 59% of derivative users employ derivatives to amplify equity returns (positive derivative-nonderivative return correlation). Using K-Means Clustering on the allocation of derivative underlying assets, the paper identifies five persistent derivative strategy clusters. Long index users (41% of derivative users) dominate: they use long equity index derivatives to gain market exposure and amplify fund returns, and they contribute the bulk of the measured amplification. Despite this strategy, long index users do not outperform nonusers in normal times or during crisis periods. During COVID-19, they doubled derivative use to short indices, suffered losses when the Fed announced emergency measures on March 23, 2020, and then lost again on newly opened short positions as markets rebounded.

## Core results

Magnitudes and significance are as reported; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Derivatives contribute substantially to fund returns: **average monthly DIR is -6.5 bps** but with a standard deviation of 78 bps; the *derivative relative contribution* exceeds 0.1 for 30% of fund-month observations | Table 1 Panel B, p. 1130; Figure 1, p. 1132 | mean DIR = -6.5 bps (std 78); mean non-DIR = 20.7 bps (std 531); 10% of obs have derivative relative contribution > 0.6 |
| R2 | **59% of derivative users have a positive correlation between DIR and non-DIR**, indicating amplification, not hedging; median correlation 0.17; equity derivative users 64% positive, median 0.43 | Figure 4, p. 1144; Table 4 Panel A, p. 1144 | median DIR-non-DIR correlation: long index = 0.67; long stock = 0.12; short index = -0.58; short stock = -0.25; nonequity = -0.06 |
| R3 | **Derivative strategies are highly persistent**: gross notional exposure auto-regresses at 0.83-0.96 across nontoken strategy groups; probability of staying in major user group 85-94% throughout sample | Table 3, p. 1139; Figure 2 Panel C, p. 1138 | AR coefficient: long index 0.832\*\*\* (t=21.82); long stock 0.915\*\*\* (t=12.16); short index 0.883\*\*\* (t=22.53); short stock 0.956\*\*\* (t=10.15); token users only 0.084 (t=3.95) |
| R4 | **Long index users receive 0.2% more monthly flows than nonusers** (2.4% annually), driven by institutional share classes; all other derivative users receive 0.1% more | Table 9 Panel B, p. 1161; Table 10 Panel A, p. 1163 | long index dummy coef = 0.201\*\* (t=2.21) in col 1; institutional-flow channels confirmed via share-class regressions; retail flows not significantly different |
| R5 | **Long index users underperform nonusers by 0.36-0.62 pp annually** on all five risk-adjusted performance measures over 2011-2022; all derivative users underperform slightly but the gap is largest for long index | Table 9 Panel A, p. 1161 | long index FF5 alpha: -1.45\*\*\* vs nonusers -0.83\*; long index minus nonusers difference = -0.62\*\* (t=-2.20) annually |
| R6 | **During COVID-19 outbreak, long index users underperformed other derivative users by 4.85% per month**; derivatives accounted for 0.85% (18%) of the gap; active equity trading drove the rest | Table 8 Panel A, p. 1153; Figure 5, p. 1154 | long index DIR contribution: -47.60 bps/month; all others DIR: +37.11 bps during outbreak; long index - all others DIR gap = -84.71\*\*\* bps |
| R7 | **During COVID-19 recovery, long index users also failed to outperform**, gaining only 6.3 bps from DIR vs all others DIR of -54.92 bps (total DIR gap = +61.22\*\*); active DIR gap = 5.42 bps (n.s.), so active derivative trading was negligible | Table 8 Panel B, p. 1153; Figure 5, p. 1154 | long index fund return vs all others difference: 260.29 bps\*\*\* monthly during recovery; but driven by equities (non-DIR = 199.08\*\*), not derivatives |
| R8 | **Institutional investors allocated extra flows to high-tracking-error long index funds pre-COVID** (consistent with a risk-shifting channel), which then shifted to short derivative positions during the crash but still failed to outperform | Table 10, p. 1163 | high-CTE long index dummy coef = 0.284\*\*\* (t=3.16) for institutional flows; high-CTE users increased short notional exposure by 17.5\*\*\* pp vs low-CTE users |

**Overall (paper's conclusion).** The majority of derivative-using mutual funds, especially long index users, employ derivatives to amplify equity returns rather than hedge. This amplification strategy does not yield superior performance in normal times or in crises, yet these funds attract abnormally high institutional flows. The paper tests the prediction of Glode (2011) that mutual funds underperform in normal times but outperform in crises: long index users fail the crisis-period outperformance prediction. Institutional investors appear to seek funds that deviate from benchmarks during crises (a risk-shifting rationale), but the strategy failed on the realized price path due to the unexpected Fed intervention during COVID-19.

## Theory / model

The paper has no formal theoretical model. It develops and tests the following testable hypotheses against the N-PORT data:

**H1 (Amplification vs. Hedging).** Prior work by Koski and Pontiff (1999) surveyed mutual fund managers and found most claimed to use derivatives for hedging, with only a small minority reporting amplification. Cao, Ghysels, and Hatheway (2011) use N-SAR data and find hedging evidence by comparing return distributions. Frino, Lepone, and Wong (2009) study derivative use and fund flows with options and futures. All three relied on coarse data that could not directly estimate the derivative PnL contribution. This paper tests the hedging hypothesis directly: if funds amplify, the derivative-induced return (DIR) and the nonderivative-induced return (non-DIR) will be positively correlated. If funds hedge, the correlation will be negative. The key metric is the *signed derivative relative contribution*, the ratio of DIR to non-DIR (p. 1133):

$$
\text{DIR}_t = \frac{\text{PnL}_t^{\text{Realized}} + \text{PnL}_t^{\text{Unrealized}} - \text{PnL}_{t-1}^{\text{Unrealized}}}{\text{TNA}_{t-1}}
$$

$$
\text{Derivative Relative Contribution}_t = \left| \frac{\text{DIR}_t}{\text{non-DIR}_t} \right|
$$

where $$\text{PnL}^{\text{Realized}}$$ and $$\text{PnL}^{\text{Unrealized}}$$ are monthly realized and unrealized profit-and-loss from all derivative positions as reported in N-PORT, scaled by total net assets in the previous month (p. 1133). Non-DIR is defined as fund return minus DIR.

**H2 (Strategy Clustering).** Funds with similar derivative strategies will cluster along the dimension of their underlying-asset allocation. K-Means Clustering on the 12-dimensional allocation vector should yield economically interpretable clusters corresponding to recognized trading motives (amplification, hedging, information trading, nonequity risk management).

**H3 (Performance).** Amplifying derivative users should not necessarily outperform in normal markets (the strategy adds risk without guaranteed alpha). In crises, performance depends on the realized path; a strategy that bets against the market could succeed or fail depending on the crisis trajectory.

**Identification.** There is no causal identification strategy. All results are descriptive. The paper exploits the granularity of N-PORT (monthly fund-level PnL by derivative position, including swaps not previously covered in CRSP or N-SAR) to document facts not measurable with prior data.

## Method

**K-Means Clustering (Section 3.1, pp. 1134-1136).** The key input for each fund-quarter is the 12-dimensional allocation vector $$x = (x_1, \ldots, x_{12})$$ of notional amounts across 12 categories (equity index long/short, individual stock long/short, interest rate long/short, FX long/short, commodity long/short, other long/short). K-Means minimizes intracluster Euclidean distances and maximizes intercluster distances:

$$
\min_{C_1,\ldots,C_k} \sum_{j=1}^{k} \sum_{x_i \in C_j} \| x_i - \mu_j \|^2
$$

where $$\mu_j$$ is the centroid of cluster $$j$$. The optimal number of clusters $$k$$ is chosen by the Silhouette Method, yielding $$k = 5$$. The five clusters are labeled: long index (41.4% of derivative users), long stock (12.6%), short stock (8.5%), short index (11.4%), and nonequity (26.1%) (Table 2, p. 1136). This builds on `panel-regression` for the persistence and performance analyses that follow.

**Derivative Performance Measurement.** N-PORT provides monthly realized and unrealized PnL for each derivative instrument. The paper hand-collects daily security-level returns for each derivative position by matching security names in N-PORT to Yahoo Finance and Bloomberg, allowing construction of *hypothetical DIR* (return assuming static quarterly holdings). The difference between actual DIR and hypothetical DIR isolates active within-quarter derivative trading (p. 1152).

**Extended Sample via CRSP (Section 5, pp. 1158-1161).** For performance and flow analysis, the paper extends to 2011-2022 using CRSP mutual fund holdings. Because CRSP does not provide gross notional exposure, the paper identifies long index users as funds where over 80% of derivative positions are long equity index contracts, using intensive manual matching of security names. Equal-weighted portfolio returns are then regressed on Fama-French factor models.

## Empirical specifications

All regressions use standard errors clustered at the fund level. The main specifications are:

**Derivative strategy persistence (Table 3, p. 1139).** For each derivative user type $$g$$:

$$
\text{GrossNotionalExposure}_{f,t} = \alpha + \beta \cdot \text{GrossNotionalExposure}_{f,t-1} + \varepsilon_{f,t} \tag{1}
$$

with fund fixed effects and Lipper-style fixed effects. Results (R3): $$\hat{\beta}$$ ranges from 0.832 (long index) to 0.956 (short stock), with R-squared 0.68-0.96 for nontoken users.

**Excess cash and equity holdings response to flows (Table 5, p. 1148).** Separate panel regressions by derivative strategy group:

$$
\Delta \text{ExcessCash}_{f,t} = \alpha + \beta \cdot \text{Flow}_{f,t} + \text{Controls}_{f,t} + \text{TimeFE}_t + \text{StyleFE}_f + \varepsilon_{f,t} \tag{2}
$$

where excess cash is fund cash minus 20% of gross notional exposure (excluding call/put purchases and short equity positions), following An and others (2021). Long index users show $$\hat{\beta} = -0.0383^{**}$$ (t=-2.21), the only group with a negative relation, while all others show positive relations consistent with standard cash management.

**Flow-performance sensitivity (Table 6, p. 1149).** Fund next-month flows on past-year performance, controlling for lagged flows, expense ratio, turnover ratio, log TNA, past-year return volatility, with Lipper-style and time fixed effects:

$$
\text{Flow}_{f,t+1} = \alpha + \gamma \cdot \text{Perf}_{f,t-12:t} + \text{Controls}_{f,t} + \text{TimeFE}_t + \text{StyleFE}_f + \varepsilon_{f,t} \tag{3}
$$

Short equity users show the highest flow-performance sensitivity ($$\hat{\gamma} = 10.46^{***}$$ on raw return), consistent with hedge-fund-like investor base.

**Long-run performance (Table 9, p. 1161).** Equal-weighted portfolios formed by derivative user type; excess returns regressed on Fama-French factor returns using a 2011-2022 CRSP sample. Long index users show FF5 alpha of -1.45\*\*\* (t=-2.91) vs nonusers -0.83\* (t=-1.90), a -0.62\*\* difference (t=-2.20) annually (R5).

**Fund flows by strategy (Table 9 Panel B, p. 1161).** Monthly fund-level flow regressions on derivative strategy dummies and their interaction with a retail-share-class indicator:

$$
\text{Flow}_{f,t} = \alpha + \delta_{\text{LI}} \cdot \mathbf{1}[\text{LongIndex}]_f + \delta_{\text{AO}} \cdot \mathbf{1}[\text{AllOthers}]_f + \text{Controls}_{f,t} + \text{TimeFE}_t + \text{StyleFE}_f + \varepsilon_{f,t} \tag{4}
$$

Two-way clustered standard errors at fund and time levels. Long index coefficient: 0.201\*\* (t=2.21) through 0.184\*\* (t=2.15) across performance-measure variants.

**COVID return decomposition (Table 8, p. 1153).** Monthly fund returns decomposed into DIR and non-DIR; each further split into hypothetical (passive) and active components using hand-collected daily security returns. Comparisons made separately for outbreak (Feb-Mar 2020) and recovery (Apr-Jun 2020) periods. Long index - all others DIR gap = -84.71\*\*\* bps during outbreak.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| SEC Form N-PORT (monthly, quarterly) | Primary data: derivative holdings, notional amounts, monthly realized and unrealized PnL by instrument; fund total net assets; portfolio weights | No page yet |
| CRSP Mutual Fund Database (2010-2022) | Extended sample for performance and flow analysis; fund characteristics and returns; derivative identification via holdings | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Morningstar Direct | Fund reported benchmarks (Lipper investment styles) | No page yet |
| SEC EDGAR Form N-1A (prospectus) | Principal Investment Strategy section; textual analysis of derivative-related discussions and keywords | [SEC EDGAR](/wiki/datasets/edgar/) |
| Yahoo Finance and Bloomberg (hand-collected) | Daily security-level returns for individual derivative positions; matched to N-PORT security names manually | No page yet |
| County-level COVID-19 statistics (New York Times) | Pandemic severity measures for cross-sectional variation analysis (Section IA.2) | No page yet |

Sample: N-PORT primary sample July 2019 to December 2022 (3,106 active domestic equity funds, 1,079 derivative users). Extended CRSP sample 2011-2022.

## When to read the full paper

Read the [original](https://doi.org/10.1093/rfs/hhaf001) if you are studying: (i) mutual fund derivative regulation, since the paper documents that most amplification is unhedged and questions whether derivative access benefits investors; (ii) constructing fund classification schemes using N-PORT data (Section 3 with the K-Means approach); (iii) measuring how derivatives affect fund tracking error during crises (Figures 6 and 9 in the source); or (iv) analyzing the flow-performance puzzle for derivative-using funds, particularly the risk-shifting channel evidence (Section 5 and Table 10). The Internet Appendix contains additional cross-sectional variation tests (SAH orders, industry concentration) and robustness checks for the COVID analysis.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(4), 2025, pp. 1120-1166. Published by Oxford University Press on behalf of The Society for Financial Studies. All rights reserved. Standard OUP publication-reuse rights; not CC-licensed. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**.

> Kaniel, Ron, and Pingle Wang. "Unmasking Mutual Fund Derivative Use."
> *The Review of Financial Studies* 38, no. 4 (2025): 1120-1166.
> DOI: 10.1093/rfs/hhaf001.
> Replication code: Harvard Dataverse, https://doi.org/10.7910/DVN/TQCGER.
> Extract-only; paywalled source.
