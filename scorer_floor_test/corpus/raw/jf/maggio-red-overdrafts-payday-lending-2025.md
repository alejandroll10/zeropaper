---
title: "In the Red: Di Maggio, Ma & Williams (2025)"
description: >-
  Distilled: Banning high-to-low transaction reordering (HTLR) by banks
  reduces low-income consumers' payday borrowing by $85 per quarter (11%),
  improves credit scores, and raises consumption of essential goods, while also
  triggering bank branch closures in low-income areas. J. Finance 2025,
  paywalled. Seven core results with source locators, datasets used, the
  identification strategy (class-action lawsuits as natural experiment), and
  the estimating specifications.
sidebar:
  label: Di Maggio-Ma-Williams 2025
  order: 1
tags: [paper-summary, household-finance, consumer-finance, banking, overdraft,
       payday-lending, financial-inclusion, natural-experiment,
       difference-in-differences, panel-regression, peer-reviewed, unreplicated,
       data:clarity-services, data:equifax, data:fdic-summary-of-deposits, data:hmda]
paper:
  authors: Marco Di Maggio, Angela Ma, Emily Williams
  authorList:
    - { family: Di Maggio, given: Marco, orcid: "0000-0001-7051-817X", affiliation: Imperial College Business School }
    - { family: Ma, given: Angela, affiliation: Boston College Carroll School of Management }
    - { family: Williams, given: Emily, orcid: "0000-0002-8262-9181", affiliation: Harvard Business School }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1691–1738
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13447
  jel:
    codes: [G21, G28, D14]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Housing Market and Economics
    - Banking stability, regulation, efficiency
  dataAccess: licensed-commercial
  outcome:
    - payday loan borrowing (dollars and number of loans per borrower)
    - installment loan borrowing (dollars per low-income borrower)
    - consumer credit score
    - credit card balance and limit
    - total balance in good standing
    - durable and nondurable essential consumption
    - bank branch exit probability
  outcomeClass: [household-finance, credit-supply, bank-funding]
  license: >-
    Wiley standard terms and conditions (paywalled VOR);
    confirmed via Crossref DOI metadata: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-03-31.
    Artifact p.1691: (c) 2025 the American Finance Association. No CC licence.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site wrapper; not machine-fetchable; 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 1
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression]
    identification: natural-experiment
  contributionType: [new-fact, new-data]
  mechanisms: [financial-constraint, behavioral-bias, debt-overhang]
  introducesData: true
  scope:
    region: US
    assetClass: consumer credit (payday loans, installment loans, credit cards)
    period: 2005-01..2019-12
    frequency: quarterly
    dataType: [administrative, market, accounting]
    granularity: [individual, aggregate]
    n: "171,445 alternative-credit borrowers (Clarity); 680,856 traditional borrowers (Equifax); 37 class-action lawsuits"
  findings:
    - ref: R1
      outcome: payday loan borrowing (dollars per borrower per quarter)
      metric: coefficient
      value: "-$84.84*** (se 31.47), neighborhood x quarter FE; -11% relative to mean"
      direction: negative
      vsBenchmark: treated vs control zip codes (within 7 miles, sued but not HTLR-banned)
    - ref: R2
      outcome: installment loan borrowing (dollars per low-income borrower per quarter)
      metric: coefficient
      value: "-$358.3*** (se 135.8), neighborhood x quarter FE; -8% relative to mean"
      direction: negative
      vsBenchmark: treated vs control zip codes
    - ref: R3
      outcome: payday loan borrowing (dollars per borrower per quarter)
      metric: coefficient
      value: "-$84.84 (1 yr), -$72.02 (2 yr), -$50.47 (3 yr); all significant at 1% or 5%"
      direction: negative
      vsBenchmark: persistent decline over 3-year horizon; Table VIII
    - ref: R4
      outcome: consumer credit score (likelihood of 50+ point increase)
      metric: pp-effect
      value: "0.0288*** (se 0.0111) at 1 yr; 0.0315*** (se 0.0106) at 3 yr"
      direction: positive
      vsBenchmark: treated vs control zip codes (Equifax low-income installment borrowers)
    - ref: R5
      outcome: credit card balance per low-income installment borrower
      metric: coefficient
      value: "$33.96** (se 13.94) at 1 yr; $34.05** (se 15.62) at 2 yr; $26.18* (se 15.62) at 3 yr"
      direction: positive
      vsBenchmark: treated vs control zip codes (Table IX Panel A)
    - ref: R6
      outcome: durable consumption per household (home and auto expenditures)
      metric: coefficient
      value: "$45.18** (se 21.76) in dollar amount; 1.177** units (se 0.565)"
      direction: positive
      vsBenchmark: essential nondurable consumption also rises by $15.57**; nonessential nondurable unchanged (Table X)
    - ref: R7
      outcome: bank branch exit probability
      metric: pp-effect
      value: "0.00896*** (se 0.000828) higher probability of exit; concentrated in low-income zip codes"
      direction: positive
      vsBenchmark: "HTLR-banned banks 2% more likely to close branches; interaction with Low-Income: 0.00334** (se 0.00169) (Table XI)"
  resultType: new-finding
  replicationCode:
    status: available
  relatesTo:
    - { cite: "Morgan, Strain & Seblani (2012)", doi: '10.1111/j.1538-4616.2011.00499.x', relation: builds-on, note: "overdraft and payday loans as substitutes/complements; this paper argues they are complements, not substitutes" }
    - { cite: "Melzer & Morgan (2015)", doi: '10.1016/j.jfi.2014.07.001', relation: builds-on, note: "competition between overdraft providers and payday lenders" }
    - { cite: "Bertrand & Morse (2011)", doi: '10.1111/j.1540-6261.2011.01698.x', relation: builds-on, note: "disclosure about payday loans and behavioral biases; motivates the behavioral-friction channel here" }
    - { cite: "Morse (2011)", relation: cites, note: "payday loan access improves welfare in natural disasters" }
    - { cite: "Melzer (2011)", doi: '10.1093/qje/qjq009', relation: cites, note: "payday loan access raises difficulty paying bills" }
    - { cite: "Skiba & Tobacman (2019)", doi: '10.1086/706201', relation: cites, note: "payday loans increase bankruptcy rates" }
    - { cite: "Gabaix & Laibson (2006)", doi: '10.1162/qjec.2006.121.2.505', relation: builds-on, note: "shrouded attributes equilibrium explains why competition does not eliminate overdraft add-on pricing" }
    - { cite: "Dlugosz, Melzer & Morgan (2021)", doi: '10.2139/ssrn.3876646', relation: cites, note: "overdraft fee ceilings and the unbanked" }
  openQuestions:
    - "Whether branch closures triggered by HTLR bans fully offset consumer welfare gains from lower overdraft costs, especially in areas where banks exit low-income neighborhoods (p. 1723-1725, Table XI)."
    - "Whether the results generalize to planned overdrafts (contracted credit lines) vs unplanned overdraft services, since the paper focuses on the latter (pp. 1708, 1723)."
    - "The long-run equilibrium effects on bank entry and the supply of traditional financial services in affected neighborhoods, which the paper cannot fully assess (p. 1734)."
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full PDF read (pp. 1691-1738, 48 pages). Seven results extracted from Tables V, VI, VIII, IX, X, XI with exact locators. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all 7 rows confirmed correct (Tables V, VI, VIII, IX, X, XI, A.I); equations (1), (2), (4), colocation logit, and bank-level first-stage match PDF term-for-term; no fixes required."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13447
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-31. No CC licence. Artifact p.1691 confirms (c) 2025 the American Finance Association."
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification strategy (class-action lawsuits banning high-to-low transaction reordering as a natural experiment), and the estimating specifications with exact table locators: enough to know what was found and how, without reading all 48 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13447).

## TL;DR

Banks' practice of reordering transactions from high to low (HTLR) maximizes overdraft fees earned from low-income depositors. The paper exploits 37 class-action lawsuits that forced some banks to cease HTLR, comparing treated zip codes (with banned banks) to nearby control zip codes (also with sued banks but not banned) in a difference-in-differences design. After HTLR bans, low-income consumers reduce payday borrowing by $85 per borrower per quarter (11%), reduce installment borrowing by $358 per borrower per quarter (8%), improve credit scores, gain access to cheaper mainstream credit, and increase essential consumption. But HTLR bans also cause banks to close branches, especially in low-income areas, highlighting a tension between fee limits and financial access.

## Core results

Magnitudes as reported; `\*\*`, `\*\*\*` = 5%, 1% significance. Standard errors clustered at the neighborhood level (consumer specs) or bank and zip-code level (branch specs). All consumer specifications use zip code x quarter observations in below-median income zip codes.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | HTLR bans reduce **payday loan borrowing** per borrower | Table V col. (3), p. 1711 | DiD coeff. = -$84.84\*\*\* (se 31.47); 11% reduction relative to mean |
| R2 | HTLR bans reduce **installment loan borrowing** per low-income borrower | Table VI col. (3), p. 1714 | DiD coeff. = -$358.3\*\*\* (se 135.8); 8% reduction relative to mean |
| R3 | Alternative-credit declines **persist for at least 3 years** | Table VIII, p. 1717 | Payday: -$84.84 (yr 1), -$72.02 (yr 2), -$50.47\*\* (yr 3); Installment: -$358.3, -$293.2\*\*, -$276.5\*\* |
| R4 | Consumers are **more likely to experience a 50+ point credit score increase** | Table IX Panel B col. (1), p. 1719 | 0.0288 pp\*\*\* (se 0.0111) at 1 year; 0.0315 pp\*\*\* at 3 years |
| R5 | **Credit card balances and limits rise**, indicating improved access to mainstream credit | Table IX Panel A col. (1-2), p. 1719 | Credit card balance: +$33.96\*\* (yr 1); credit card limit: +$40.10\*\* (yr 1) per low-income borrower |
| R6 | Consumers **increase essential consumption** (durable and nondurable essential goods) | Table X col. (1)-(4), p. 1721 | Durable spending: +$45.18\*\* per household; nondurable essential: +$15.57\*\*; nonessential nondurable: insignificant |
| R7 | HTLR-banned banks are **significantly more likely to close branches**, concentrated in low-income areas | Table XI col. (1) and (5), p. 1724 | Branch exit probability: +0.90 pp\*\*\* overall; interaction with Low-Income dummy: +0.33 pp\*\* additional |

**Overall (paper's conclusion).** Aggressive overdraft pricing via HTLR creates demand for alternative credit, trapping low-income consumers in a cycle of high-cost borrowing. Ceasing HTLR reduces payday and installment borrowing, improves consumer credit health, and unlocks access to cheaper mainstream credit. However, HTLR bans also prompt banks to exit low-income neighborhoods, an unintended spillover that may offset some consumer gains and raise new concerns about financial access.

## Theory / model

The paper has no formal model. It develops two competing hypotheses for the relationship between overdraft pricing and demand for alternative credit, and tests them empirically.

**Hypothesis 1 (complements / debt-trap):** Consumers improperly estimate overdraft costs (as in Bertrand and Morse (2011)) and turn to payday lenders to repay unaffordable overdraft balances and fees. Morgan, Strain, and Seblani (2012) and Melzer and Morgan (2015) document that overdraft providers and payday lenders compete and that consumers use both as substitutes; the paper's findings challenge that view, showing they are better described as complements. A reduction in overdraft costs reduces payday demand.

**Hypothesis 2 (substitutes / price-reduction supply shift):** Overdraft credit and payday loans are substitutes for short-term liquidity. If HTLR bans reduce the supply of overdraft services (banks become less willing to provide the service at lower fee revenue), excess demand for short-term credit shifts to payday lenders. In this case, payday borrowing rises after HTLR bans.

Related literature: Melzer (2011) and Skiba and Tobacman (2019) provide evidence on the real costs of payday loan access. Dlugosz, Melzer, and Morgan (2021) study overdraft fee ceilings and the unbanked. Gabaix and Laibson (2006) formalize how shrouded attributes enable add-on pricing to persist in competitive markets, motivating why HTLR pricing is not competed away.

**Identification logic.** The key source of variation is the lawsuit outcome: within the same geographic neighborhood, some zip codes contain branches of banks required to cease HTLR, and neighboring zip codes contain branches of banks that were sued but not required to stop. The two groups operate in similar local economic conditions and share similar consumer demand dynamics. Within-neighborhood-quarter fixed effects additionally absorb any time-varying shocks (such as local unemployment changes) correlated with both HTLR bans and credit demand. The paper argues that lawsuit outcomes are quasi-exogenous because they depend on contract-level arbitration clauses and litigation strategy, not on bank or consumer characteristics, and tests this with a battery of balance checks (Table III Panel B, Internet Appendix Tables IV-V, pp. 1706, 1728-1729).

## Method

The primary estimator is a zip-code-by-quarter-level difference-in-differences regression. The treatment group is zip codes containing branches of banks required to cease HTLR; the control group is zip codes within seven miles of a treated zip code that contain branches of sued banks not required to cease HTLR. This design restricts variation to local areas subject to similar lawsuit contexts.

The paper builds on the `difference-in-differences` and `panel-regression` primitives. The key structural feature is that the control group is not the general population of zip codes but rather nearby zip codes sharing the same lawsuit environment, selected to match on local consumer demand dynamics.

For colocation motivating evidence (Table IV, p. 1707), a conditional logit regression is estimated at the bank branch by year level:

$$
\Pr(\text{AltFin within } d)_{bz} = F\left(\gamma \cdot \text{HTLR}_{b} + \eta_z\right) \tag{4-IV}
$$

where $$\text{HTLR}_b$$ is an indicator for whether branch $$b$$ belongs to an HTLR bank, $$\eta_z$$ are zip code fixed effects, and $$F(\cdot)$$ is the logistic CDF. This within-zip-code test avoids comparing geographic areas with different demographic compositions.

For bank-level first-stage evidence (Table A.I, p. 1735), the estimating equation is a bank by quarter DiD:

$$
\Delta \text{BankOutcome}_{bt} = \beta \cdot \text{HTLRBan}_b \cdot \text{Post}_t + \eta_b + \eta_t + \varepsilon_{bt} \tag{FS}
$$

where bank and quarter fixed effects are included and standard errors are clustered at bank and quarter levels. This confirms HTLR bans reduced overdraft-related revenue by 6.44% (Table A.I col. 1, p. 1735).

## Empirical specifications

All consumer-outcome specifications are estimated at the zip-code by quarter level, restricted to zip codes with below-median income.

**Main DiD for payday and installment borrowing (R1, R2; equations 1 and 2 from the paper, p. 1712 and p. 1718):**

$$
\text{PaydayBorrowing}_{zt} = \beta \cdot \text{HTLRBan}_z \cdot \text{Post}_t + \eta_{nt} + \varepsilon_{zt} \tag{1}
$$

$$
\text{FinancialHealth}_{zt} = \beta \cdot \text{HTLRBan}_z \cdot \text{Post}_t + \eta_{nt} + \varepsilon_{zt} \tag{2}
$$

where $$\text{PaydayBorrowing}_{zt}$$ is average dollars of payday loans disbursed per payday borrower in zip code $$z$$ in quarter $$t$$; $$\text{HTLRBan}_z$$ is a dummy for whether the zip code contains branches of a bank required to cease HTLR; $$\text{Post}_t$$ is a dummy for quarters after the HTLR ban; and $$\eta_{nt}$$ are neighborhood-by-quarter fixed effects (the most conservative specification, where neighborhood = all zip codes within seven miles). Standard errors are clustered at the neighborhood level. The window is two quarters before and four quarters after the HTLR ban.

The coefficient of interest $$\beta$$ measures the differential effect of the ban on consumer alternative borrowing in treated relative to control zip codes within the same neighborhood. Tables V (Clarity payday) and VI (Equifax installment) present six columns each, varying between neighborhood FE, quarter FE, and neighborhood-by-quarter FE.

**Long-term horizon test (R3; Table VIII, p. 1717):** The same DiD specification but extending the post window to one, two, or three years. The results show that the decline in both payday and installment borrowing persists without reverting to pre-ban levels, ruling out a temporary substitution explanation.

**Credit health and consumption (R4, R5, R6; Tables IX and X, pp. 1719, 1721):** The same zip-code-by-quarter DiD structure (equation 2) applied to credit card balances, credit card limits, probability of a 50+ point credit-score increase, total balance in good standing, and household expenditure (durable, essential nondurable, nonessential nondurable) from Earnest transaction data. Credit card variables come from Equifax; consumption variables are from Earnest Research's transaction-level data for 6 million U.S. households. Consumption tests use an 8-quarter post window and 4-quarter pre window.

**Branch exit spillovers (R7; Table XI, equation 4 from the paper, p. 1723):**

$$
\text{Exit}_{izt} = \beta \cdot \text{HTLRBan}_i \cdot \text{Post}_t + \eta_{zt} + \varepsilon_{izt} \tag{4}
$$

where $$\text{Exit}_{izt}$$ is a dummy for bank $$i$$ exiting zip code $$z$$ in year $$t$$; the specification includes zip-code-by-year and bank-by-zip-code fixed effects; $$\text{Post}_t$$ covers up to three years after the HTLR ban. The interaction $$\text{HTLRBan}_i \cdot \text{Post}_t \cdot \text{LowIncome}_{zt}$$ shows that exits are concentrated in below-median income zip codes. Standard errors are clustered at the bank and zip-code level.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Clarity Services (alternative credit bureau) | Primary outcome: payday and alternative installment loans disbursed 2013-2019; random sample of 171,445 alternative borrowers | No page yet |
| Equifax (traditional credit bureau) | Installment loan borrowing, credit card balances and limits, credit scores, total balances in good standing; representative 10% sample of 680,856 borrowers, 2005-2018 | No page yet |
| Pew Charitable Trusts bank study (2012-2015) | HTLR practice indicator for the largest 50 US banks; four annual waves | No page yet |
| FDIC Summary of Deposits | Bank branch locations and deposit-level data for 50 largest banks | [FDIC Summary of Deposits](/wiki/datasets/fdic-summary-of-deposits/) |
| FR Y-9C call report data (FFIEC 031/041) | Bank-level overdraft revenue, all-other-loans balances, and income statement items | No page yet |
| Earnest Research expenditure data | Household consumption: credit/debit card transaction-level data for 6 million US households; durable, essential nondurable, and nonessential nondurable spending | No page yet |
| Infogroup Historical Business Database | Payday lender and check-casher locations (SIC codes 609903 and 614113), 1997-2018 | No page yet |
| Hand-collected lawsuit data set | 37 class-action lawsuits against HTLR banks: event dates, settlement terms, behavior relief (HTLR ban or not), cash settlement amounts | No page yet |
| American Community Survey (Census) | Zip-code-level demographics: age, race, income, poverty, housing, employment, 2011-2018 | No page yet |
| HMDA and SBA lending data | Bank branch exit spillovers to mortgage and small business lending (Table XII) | [HMDA](/wiki/datasets/hmda/) (no page yet) |

Sample: Clarity data 2012-2019; Equifax data 2005-2018; bank lawsuit events concentrated 2008-2015. Analysis at the zip-code by quarter level; 6,975 zip-code-quarter observations for Clarity (main spec), 30,487 for Equifax.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13447) if you are:
studying the link between bank overdraft practices and the alternative lending market; estimating causal effects of fee policies on consumer financial health; interested in spillover effects of banking regulation (branch closures, financial deserts); or evaluating the "banked vs. underbanked" distinction as a policy target. The Appendix (Tables A.I-A.III, pp. 1735-1736) contains the first-stage bank-level DiD results. The Internet Appendix contains the full lawsuit data set (Table I), balance tests (Tables IV-V), and additional robustness tables (Tables VI-XIV).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled; extract-only redistribution applies.

> Di Maggio, Marco, Angela Ma, and Emily Williams. "In the Red: Overdrafts, Payday Lending, and the Underbanked." *The Journal of Finance* 80, no. 3 (June 2025): 1691-1738. DOI: 10.1111/jofi.13447. © 2025 the American Finance Association.
