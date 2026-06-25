---
title: "Wealth and Insurance Choices: Gropper & Kuhnen (2025)"
description: >-
  Distilled: Using administrative data on 63,000 U.S. households, Gropper and
  Kuhnen find that wealthier individuals hold more life insurance coverage,
  contradicting canonical theory that predicts a negative wealth-insurance
  relationship. The positive correlation persists after controlling for risk
  preferences, pricing, bequest motives, background risk, financial literacy,
  employer benefits, and liquidity constraints. J. Finance 2025, paywalled.
  Seven core results with source locators, datasets used, the theoretical
  framework, and the empirical specifications.
sidebar:
  label: Gropper-Kuhnen 2025
  order: 1
tags: [paper-summary, household-finance, insurance, life-insurance, wealth,
       panel-regression, peer-reviewed, unreplicated, data:corelogic]
paper:
  authors: Michael J. Gropper, Camelia M. Kuhnen
  authorList:
    - { family: Gropper, given: Michael J., affiliation: University of Colorado at Boulder }
    - { family: Kuhnen, given: Camelia M., orcid: "0000-0002-7028-3224", affiliation: University of North Carolina at Chapel Hill }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1127–1170
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13426
  jel:
    codes: [G52, G51, D14]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Housing Market and Economics
    - Insurance, Mortality, Demography, Risk Management
  dataAccess: proprietary-confidential
  outcome:
    - term life insurance coverage limit
    - probability of having life insurance
    - probability of life insurance lapsation
  outcomeClass: [household-finance]
  license: >-
    Paywalled (Crossref license: content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-01-30; no CC licence detected; copyright 2025 the American
    Finance Association)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley OnlineLibrary, checked 2026-06-06)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 6

  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [panel-regression]
    identification: selection-on-observables
  contributionType: [new-fact, new-data]
  mechanisms: [financial-constraint, risk-sharing]
  introducesData: true
  scope:
    region: US
    assetClass: life insurance (term)
    period: 2015-09..2019-03
    frequency: monthly
    dataType: [administrative]
    granularity: [individual]
    n: "63,141 individuals; 2,500,000 person-month observations"

  findings:
    - ref: R1
      outcome: probability of having life insurance
      metric: coefficient
      value: "Financial wealth coefficient = 12.54 (t=18.94***); $100,000 increase in financial wealth associated with 11-13 pp increase in probability of owning life insurance"
      direction: positive
      vsBenchmark: contradicts Lewis (1989) prediction of negative wealth-insurance relationship
    - ref: R2
      outcome: probability of life insurance lapsation
      metric: pp-effect
      value: "$100,000 increase in financial wealth associated with 3.1 pp decrease in lapsation probability (Table III, coefficient = -3.46, t=-6.40***)"
      direction: negative
      vsBenchmark: wealthier households less likely to let policies lapse
    - ref: R3
      outcome: term life insurance coverage limit
      metric: coefficient
      value: "$1 increase in financial wealth leads to $0.64 increase in coverage limit (Table IV col 4, coefficient = 0.64, t=14.17***; col 3 without housing wealth: 0.73, t=16.17***; policyholders-only: $1.41, t=10.52***)"
      direction: positive
      vsBenchmark: contradicts Lewis (1989) model prediction of decreasing C in W
    - ref: R4
      outcome: term life insurance coverage limit
      metric: coefficient
      value: "Within-person: $1 increase in financial wealth leads to $0.05 increase in coverage limit (Table V, coefficient = 0.05, t=4.72***); $100,000 increase in financial wealth raises probability of having insurance by 2 pp (Table V, coefficient = 1.90, t=10.18***)"
      direction: positive
      vsBenchmark: person FE specification confirms cross-sectional finding; coefficient attenuated relative to cross-section
    - ref: R5
      outcome: term life insurance coverage limit
      metric: coefficient
      value: "Controlling for background risk (consumption volatility): financial wealth coefficient remains 0.62 (t=14.01***), similar to baseline 0.64 (Table VIII col 1)"
      direction: positive
      vsBenchmark: background risk explains some but not all of the wealth-insurance correlation
    - ref: R6
      outcome: term life insurance coverage limit
      metric: coefficient
      value: "Controlling for liquidity constraints (credit use ratio): financial wealth coefficient = 0.63 (t=13.76***), nearly unchanged from baseline (Table X Panel B); credit use ratio coefficient = -119.66 (t=-6.06***)"
      direction: positive
      vsBenchmark: liquidity constraints explain some lapsation but do not eliminate wealth-coverage correlation
    - ref: R7
      outcome: term life insurance coverage limit
      metric: coefficient
      value: "Education (college degree) associated with $44,000 higher coverage (Table IX Panel A, coefficient = 0.44, t=14.62***); wealth-insurance correlation persists in both government and nongovernment employee subsamples (Table IX Panel B)"
      direction: positive
      vsBenchmark: financial literacy and employer benefits do not eliminate positive wealth-insurance correlation

  resultType: overturns

  relatesTo:
    - { cite: "Lewis (1989)", relation: contradicts, note: "paper's central finding contradicts Lewis's optimal coverage formula predicting C decreasing in W under CRRA utility" }
    - { cite: "Mossin (1968)", doi: '10.1086/259427', relation: contradicts, note: "contradicts Mossin's foundational prediction that wealthier agents with DARA preferences purchase less insurance" }
    - { cite: "Rampini and Viswanathan (2019)", relation: tests, note: "results consistent with their theory that liquidity constraints reduce insurance demand, but the wealth-coverage correlation persists after controlling for liquidity" }
    - { cite: "Ericson and Sydnor (2018)", doi: '10.3386/w24993', relation: tests, note: "results consistent with their theory that insurance transfers resources across time, not just states" }
    - { cite: "Koijen, Van Nieuwerburgh & Yogo (2016)", doi: '10.1111/jofi.12273', relation: builds-on, note: "uses their framework for modeling life insurance choice; finds bequest motives do not differ by wealth tercile" }
    - { cite: "Armantier, Foncel & Treich (2023)", doi: '10.1016/j.jfineco.2023.03.003', relation: cites, note: "contemporaneous paper finding positive wealth-auto-insurance correlation using survey data; this paper extends to term life using administrative data" }

  openQuestions:
    - "Whether the wealth-related differences in insurance coverage vary with the business cycle or lead to heterogeneous effects of macroeconomic shocks; the 43-month panel does not include a recession (p. 1162)."
    - "Whether wealthier households are overinsured or less wealthy households are underinsured from a welfare perspective, and whether supply-side factors (preferential insurance product provision to the wealthy) contribute to the pattern (p. 1162)."
    - "Whether positive wealth-insurance correlations extend beyond term life insurance to other insurance products and other countries, and whether supply-side frictions not observable in this administrative dataset drive the residual correlation (p. 1162)."

  replicationCode:
    status: none

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: >-
        Full PDF read (pp. 1127-1170, Tables I-X, Figures 1-6). All results
        extracted from source tables with exact locators. Not human-verified.
        Not reproduced. Administrative data from a financial services firm;
        data are proprietary and not publicly available.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF
        (Tables II-X); one fix applied: R3 locator corrected from Table IV col 3
        to col 4 for the headline $0.64 figure (col 3 gives 0.73, t=16.17;
        col 4 with housing wealth gives 0.64, t=14.17); all other rows confirmed.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13426
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-30; no CC licence; paywalled"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical framework it tests (Lewis 1989), and the empirical specifications behind each finding: enough to know what it found and how, without reading all 44 pages. To replicate or extend it, read the full source at [https://doi.org/10.1111/jofi.13426](https://doi.org/10.1111/jofi.13426).

## TL;DR

Standard models of insurance demand (Mossin (1968), Lewis (1989), Gollier (2003)) predict that wealthier agents, having greater risk-bearing capacity, purchase less insurance. Using administrative records from a U.S. financial services firm covering 63,000 individuals and 2.5 million person-month observations (September 2015 to March 2019), Gropper and Kuhnen document the opposite: wealthier households hold larger term life insurance coverage limits, are more likely to have insurance, and are less likely to let policies lapse. This positive wealth-insurance correlation survives controls for risk preferences, pricing, bequest motives, background risk, financial literacy, employer-provided benefits, and liquidity constraints. Liquidity constraints and background risk each explain a portion of the pattern, but a significant positive wealth effect remains. The findings support newer theories that view insurance as consumption-smoothing across time (Rampini and Viswanathan (2019), Ericson and Sydnor (2018), Casaburi and Willis (2018)) but call for further empirical work to identify supply-side or other demand-side mechanisms not yet studied. A contemporaneous paper by Armantier, Foncel and Treich (2023) finds a similar positive wealth-insurance correlation for auto insurance using survey data; this paper complements it by using administrative data on term life insurance with direct dollar-coverage measures. Koijen, Van Nieuwerburgh and Yogo (2016) document that households fail to rebalance portfolios away from life insurance as they age; the patterns here suggest persistence in the wealth-coverage relationship as well.

## Core results

Magnitudes and significance are as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. Locators point into the source PDF. Wealth variables are in hundreds of thousands of dollars in all OLS tables, so a coefficient of 12.54 on financial wealth means a $100,000 increase in wealth raises the dependent variable by 12.54 percentage points (Tables II-III) or $12,540 (Table IV-V when DV is in dollars).

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Financial wealth predicts higher probability of having life insurance**, opposite to theory | Table II col 3, p. 1138 | Coefficient = 12.54 (t=18.94\*\*\*); $100,000 increase associated with 11-13 pp higher probability of owning life insurance |
| R2 | **Wealthier individuals are less likely to lapse their life insurance policies** | Table III col 3, p. 1139 | Coefficient = -3.46 (t=-6.40\*\*\*); $100,000 increase in financial wealth associated with 3.1 pp decrease in lapsation probability |
| R3 | **Financial wealth predicts larger coverage limits** at both extensive and intensive margins | Table IV col 4, p. 1142; Table IV col 5 (policyholders only) | Full sample: $1 increase in wealth raises coverage by $0.64 (t=14.17\*\*\*; col 3 without housing wealth: 0.73, t=16.17\*\*\*); policyholders only: $1.41 (t=10.52\*\*\*) |
| R4 | **Within-person wealth increases predict higher coverage**, ruling out fixed individual omitted variables | Table V, p. 1145 | $100,000 within-person increase in financial wealth raises probability of having insurance by 2 pp (t=10.18\*\*\*) and coverage limit by $0.05 per $1 (t=4.72\*\*\*); coefficient attenuated relative to cross-section due to inertia/adjustment costs |
| R5 | **Background risk (consumption and income volatility) explains part of the wealth-insurance correlation** but does not eliminate it | Table VIII, p. 1154 | Controlling for consumption volatility: financial wealth coefficient = 0.62 (t=14.01\*\*\*), nearly the same as baseline 0.64; consumption volatility itself is a positive predictor of coverage (coefficient = 1.96, t=5.37\*\*\*) |
| R6 | **Liquidity constraints reduce coverage and increase lapsation** but cannot account for the wealth-coverage correlation | Table X Panel B, p. 1160 | Credit use ratio positively predicts lapsation (coefficient = 0.04, t=5.39\*\*\*) and negatively predicts coverage (coefficient = -119.66, t=-6.06\*\*\*); after controlling for it, financial wealth coefficient remains 0.63 (t=13.76\*\*\*) |
| R7 | **Education and employer-provided insurance do not eliminate the positive wealth effect** on coverage | Table IX, p. 1156 | College degree associated with $44,000 higher coverage (coefficient = 0.44, t=14.62\*\*\*); wealth effect persists in both government (coefficient = 0.40, t=11.11\*\*\*) and nongovernment subsamples (coefficient = 0.72, t=10.52\*\*\*) |

**Overall (paper's conclusion).** Wealthier U.S. households have more life insurance coverage along every dimension examined: ownership, coverage limits, and lapsation behavior. This contradicts the core prediction of canonical insurance demand models. Several frictions, including background risk and liquidity constraints, explain part of the positive correlation. However, a substantial, economically meaningful positive wealth-insurance relationship remains after all examined channels are controlled for simultaneously (Appendix Table A.VI), pointing to supply-side mechanisms or demand-side factors not yet studied empirically.

## Theory / model

The paper does not develop a new model. It uses the Lewis (1989) framework as the theoretical benchmark. The model of Lewis (1989) yields the following formula for optimal term life insurance coverage (p. 1133), under CRRA utility with risk aversion parameter $$\gamma$$:

$$
C_t = \frac{1}{(1 - \lambda\pi_t)} \left[\frac{(1-\lambda\pi_t)}{\lambda(1-\pi_t)}\right]^{\frac{1}{\gamma}} A_t - \frac{1}{(1-\lambda\pi_t)} W_t \tag{1}
$$

where $$C_t$$ is the extent of life insurance coverage purchased, $$A_t$$ is the value of the asset to be insured (the NPV of dependents' future consumption), $$W_t$$ is the financial wealth of the individual (net of the insured asset), $$\pi_t$$ is the per-period probability of death, $$\lambda$$ is the insurance loading factor ($$\lambda = 1$$ implies actuarially fair insurance; $$\lambda > 1$$ means insurance is costly), and $$\gamma$$ is the CRRA coefficient.

The key theoretical prediction is $$\partial C_t / \partial W_t < 0$$: holding the value of the insured asset $$A_t$$ fixed, wealthier individuals purchase less insurance because they have greater risk-bearing capacity (p. 1133). The model also predicts $$\partial C_t / \partial A_t > 0$$: more valuable insured assets generate higher coverage demand. The paper confirms this second prediction empirically but finds that the first prediction fails in the data: $$\partial C_t / \partial W_t > 0$$ in all specifications (p. 1141).

The paper also sketches why newer theoretical frameworks (Rampini and Viswanathan (2019), Ericson and Sydnor (2018), Casaburi and Willis (2018)) can generate a positive wealth-insurance relationship when insurance is viewed as a savings instrument (state-contingent Arrow-Debreu securities) rather than pure risk transfer: poorer households face higher marginal utility of current consumption and therefore choose to save less through insurance. These theories predict that liquidity-constrained individuals buy less insurance, consistent with the authors' evidence that more constrained individuals lapse more (p. 1158).

## Method

The paper applies linear OLS panel regressions with state fixed effects (cross-sectional) and person-plus-state fixed effects (within-person panel). There is no single proposed estimating equation; the paper runs variants of the following cross-sectional specification for each outcome (pp. 1138-1146):

$$
Y_i = \alpha + \beta_1 \, W_i^{\text{financial}} + \beta_2 \, W_i^{\text{housing}} + \mathbf{X}_i' \boldsymbol{\delta} + \text{StateFE}_i + \varepsilon_i \tag{2}
$$

where $$Y_i$$ is either an insurance-ownership indicator, a lapsation indicator, or the dollar coverage limit; $$W_i^{\text{financial}}$$ is average financial wealth (in hundreds of thousands of dollars); $$W_i^{\text{housing}}$$ is estimated housing wealth; and $$\mathbf{X}_i$$ is a vector of controls including the NPV of future dependents' spending (the theoretical value of the insured asset $$A_i$$), dependents-times-mortgage and dependents-times-other-loans interactions, and the probability of death in the next year. Standard errors are clustered by state (pp. 1138-1139).

For the within-person analysis (Table V), the specification adds person fixed effects and is estimated at the person-month level:

$$
Y_{it} = \alpha_i + \alpha_s + \beta_1 \, W_{it}^{\text{financial}} + \beta_2 \, W_{it}^{\text{housing}} + \mathbf{X}_{it}' \boldsymbol{\delta} + \varepsilon_{it} \tag{3}
$$

with $$\alpha_i$$ a person fixed effect, $$\alpha_s$$ a state fixed effect, and standard errors clustered by person (p. 1145). The within-person estimator eliminates fixed unobserved individual heterogeneity (e.g., permanent risk aversion, innate financial literacy) that could confound the cross-sectional estimates.

The paper builds on `panel-regression` throughout. It does not use an instrumental variable or a natural experiment; identification rests on conditional ignorability (controlling for observables). The authors acknowledge that supply-side mechanisms or unobserved demand-side factors may drive the residual correlation (p. 1161).

## Empirical specifications

**Coverage ownership (Table II).** The dependent variable is an indicator equal to 100 if the individual ever had a term life insurance policy. OLS with state FEs and ~59,722 individuals. Specifications progressively add controls; the headline coefficient on financial wealth is 12.54 (t=18.94\*\*\*) in column (3) and 10.98 (t=19.04\*\*\*) when housing wealth is also included (column 4). The NPV of dependents' future spending (the insured asset $$A$$) has the theoretically predicted positive sign (coefficient = 0.47, t=12.08\*\*\*), validating the approach.

**Lapsation (Table III).** Dependent variable: indicator equal to 100 if the individual ever let a term life insurance policy lapse. OLS with state FEs and ~19,875 individuals (those who ever had a policy). Financial wealth coefficient = -3.46 (t=-6.40\*\*\*); housing wealth = -3.07 (t=-5.41\*\*\*) with the housing wealth measure.

**Coverage limits (Table IV).** Dependent variable: dollar coverage limit (zero for non-policyholders). OLS with state FEs and 57,586 observations (56,519 in column 4 with housing wealth). Financial wealth coefficient = 0.73 (t=16.17\*\*\*) in the full sample (column 3) and 0.64 (t=14.17\*\*\*) adding housing wealth (column 4). The paper's headline figure of "$0.64" refers to column 4. Among policyholders only: financial wealth coefficient = 1.41 (t=10.52\*\*\*) (column 5). Housing wealth coefficient = 0.10 (t=7.83\*\*\*).

**Within-person analysis (Table V).** Person-month level, 2,027,159 observations, 55,696 unique individuals. Person plus state FEs. Financial wealth coefficient = 1.90 (t=10.18\*\*\*) for the ownership indicator and 0.05 (t=4.72\*\*\*) for the coverage limit (in dollar terms per dollar of wealth). Smaller magnitudes than cross-section due to inertia in coverage rebalancing.

**Insurance pricing (Table VI).** Dependent variable: annual premium in cents per dollar of coverage (N=8,212 policyholders with observed premiums). Financial wealth has a positive coefficient (0.04, t=4.17\*\*\*), meaning wealthier individuals pay somewhat higher prices per dollar of coverage. This runs counter to the Rampini and Viswanathan (2019) pricing channel but may reflect longer policy terms among the wealthy (p. 1150).

**Background risk (Table VII, Table VIII).** Background risk is measured as the annualized standard deviation of monthly consumption, income, and wealth. Wealthier individuals face more volatile consumption and income (Table VII: financial wealth coefficient on consumption volatility = 0.03, t=12.04\*\*\*). Adding background risk controls barely changes the financial wealth coefficient on coverage (Table VIII: from 0.64 baseline to 0.62-0.66 with different volatility measures).

**Liquidity constraints (Table X).** Credit use ratio (monthly credit card spend divided by credit limit) negatively predicts coverage (-119.66, t=-6.06\*\*\*) and positively predicts lapsation (0.04, t=5.39\*\*\*). After controlling for liquidity constraints, the financial wealth coefficient on coverage remains 0.63 (t=13.76\*\*\*).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Proprietary administrative data from a U.S. financial services firm | Primary dataset: individual-level bank account balances, monthly income/spending flows, term life insurance coverage limits and premiums, demographic information; 63,141 individuals, Sep 2015-Mar 2019 | No page yet |
| Corelogic transaction prices | Housing wealth estimates: zip-code home price percentiles by income quintile; used to assign housing wealth to homeowners | [CoreLogic](/wiki/licensed/corelogic/) (licensed) |
| American Community Survey (5-year tables) | Income quintile boundaries by zip code, used to assign homeowners to income quintiles for housing wealth estimation | No page yet |
| CDC National Vital Statistics System | Age-sex specific probability of death in the next year, merged at the individual level | No page yet |
| Survey of Consumer Finances (2016 SCF) | Representativeness check: income and wealth distribution comparison (Appendix Table A.I) | No page yet |
| Zillow Home Value Index (ZHVI) | Housing wealth volatility: standard deviation of monthly zip-code ZHVI as the measure of housing wealth volatility | No page yet |

Sample: 63,141 individuals, September 2015 to March 2019 (43 months). 2,500,000 person-month observations. Individuals broadly represent the middle 50% of the U.S. income distribution (Table I, p. 1137).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13426) if you are: studying the determinants of household insurance demand using administrative data; investigating whether canonical insurance theories hold in household-level data; evaluating the role of liquidity constraints in insurance choice; or extending the analysis to supply-side mechanisms, business-cycle variation, or other insurance products. The appendix (Tables A.I-A.VI) contains robustness checks and alternative insured-asset definitions (NPV of future labor income vs. consumption).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2). Paywalled; copyright 2025 the American Finance Association. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract-only; no PDF hosted here.

> Gropper, Michael J., and Camelia M. Kuhnen.
> "Wealth and Insurance Choices: Evidence from U.S. Households."
> *The Journal of Finance* 80, no. 2 (April 2025): 1127–1170.
> DOI: 10.1111/jofi.13426.
