---
title: "Working More to Pay the Mortgage: Zator (2025)"
description: >-
  Distilled: Using Polish administrative tax records linked to floating-rate mortgage
  payments (2005-2015), Zator shows households increase labor income by roughly PLN
  0.35 for each PLN 1 rise in mortgage interest, with an asymmetric response that is
  two to three times stronger following payment increases than decreases. J. Finance
  2025, paywalled. Seven core results with source locators, datasets used, the
  identification strategy, and the estimating equations.
sidebar:
  label: Zator 2025
  order: 1
tags: [paper-summary, household-finance, labor-supply, mortgage, interest-rates,
       monetary-policy, panel-regression, instrumental-variables, peer-reviewed,
       unreplicated]
paper:
  authors: "Michal Zator"
  authorList:
    - { family: Zator, given: "Michal", orcid: "0000-0003-1941-090X", affiliation: University of Notre Dame }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1171-1207
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13413
  jel:
    codes: [D14, E52, J22]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Housing Market and Economics
    - Housing, Finance, and Neoliberalism
    - Financial Literacy, Pension, Retirement Analysis
  dataAccess: proprietary-confidential
  outcome:
    - gross household labor income
    - probability of spousal labor market entry
    - probability of job change
    - supplemental (gig) income indicator
  outcomeClass: [household-finance, labor-careers-health]
  license: >-
    Paywalled (Crossref license: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2024-12-16; no open-access licence found)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site, 2026-06-06)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 8
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, difference-in-differences]
    identification: instrument
  contributionType: [new-fact, new-data]
  mechanisms: [financial-constraint, debt-overhang]
  introducesData: true
  scope:
    region: Poland
    assetClass: residential mortgages
    period: 2005-01..2015-12
    frequency: annual
    dataType: [administrative]
    granularity: [individual, firm]
    n: "9.8 million individuals, 100+ million observations (strongly balanced panel); 171,445 mortgage holders"
  findings:
    - ref: R1
      outcome: gross household labor income
      metric: coefficient
      value: "0.337 to 0.348*** (OLS, mortgage holders); 0.297*** (OLS, full population); se 0.020-0.021"
      direction: positive
    - ref: R2
      outcome: gross household labor income
      metric: coefficient
      value: "0.459*** (IV, mortgage holders, se 0.043); 0.348*** (IV, full population, se 0.037)"
      direction: positive
      vsBenchmark: OLS and IV estimates broadly similar, confidence intervals overlap
    - ref: R3
      outcome: gross household labor income
      metric: coefficient
      value: "0.148*** (IV, PLN/CHF currency design, mortgage holders, se 0.034); 0.145*** (all households, se 0.016)"
      direction: positive
      vsBenchmark: smaller than mortgage-size design (0.35), consistent with period of declining rates and asymmetric response
    - ref: R4
      outcome: gross household labor income
      metric: coefficient
      value: "Increase coefficient: 0.233*** to 0.313*** (interaction term, six specifications); average coefficient: 0.106 to 0.283***; response to increases 2-3x larger than to decreases"
      direction: positive
      vsBenchmark: response to payment increases roughly 2-3x response to payment decreases (Table V, all six specifications)
    - ref: R5
      outcome: gross household labor income
      metric: coefficient
      value: "Dual-earner households: significantly larger response to payment increases (coefficient ~0.48); single-earner: no significant increase response; secondary earner drives increase response (Figure 6)"
      direction: positive
      vsBenchmark: dual-earner households show strongest asymmetric response; secondary (often female) earner drives payment-increase response
    - ref: R6
      outcome: probability of spousal labor market entry
      metric: pp-effect
      value: "PLN 1,000 increase in interest payments reduces probability of being single-earner by 0.1 pp (Table VI, col 4)"
      direction: negative
    - ref: R7
      outcome: probability of job change
      metric: pp-effect
      value: "PLN 1,000 increase in interest payments raises job-change probability by 0.104*** pp (Table VI, col 6, se 0.013); mean dep var 21.9%"
      direction: positive
  resultType: new-finding
  relatesTo:
    - { cite: "Di Maggio et al. (2017)", doi: '10.1257/aer.20141313', relation: extends, note: "extends ARM-reset consumption evidence to the labor supply channel; the paper's 15% income adjustment is consistent with Di Maggio's 80% consumption reallocation" }
    - { cite: "Imbens, Rubin, and Sacerdote (2001)", doi: '10.1257/aer.91.4.778', relation: tests, note: "lottery-win estimates (labor supply response to positive income shocks) are smaller and comparable to the response to payment decreases here, supporting the asymmetry interpretation" }
    - { cite: "Cesarini et al. (2017)", doi: '10.1257/aer.20151589', relation: tests, note: "Swedish lottery estimates similarly small; this paper argues asymmetry explains the divergence from estimates based on budget-tightening shocks" }
    - { cite: "Brown and Matsa (2020)", doi: '10.1016/j.jfineco.2019.11.001', relation: builds-on, note: "indebted households apply for more local jobs and are less willing to relocate; consistent with debt driving labor supply" }
    - { cite: "Bernstein and Koudijs (2020)", doi: '10.2139/ssrn.3569252', relation: builds-on, note: "accelerating amortization raises wealth accumulation partly via labor supply; magnitudes align with this paper" }
    - { cite: "Chetty and Szeidl (2007)", doi: '10.1162/qjec.122.2.831', relation: builds-on, note: "consumption commitments model predicts stronger labor supply response when commitments are present; invoked to explain asymmetry" }
  openQuestions:
    - "Whether the labor supply response generalizes to other countries or settings with fixed-rate mortgages, where households cannot respond on short notice; and whether it is stronger during recessions (the Polish boom context may overstate the typical response, p. 1204)."
    - "The relative magnitudes of the liquidity and wealth effects are difficult to disentangle without more detailed data on consumption and balance sheets (p. 1191)."
    - "Whether the positive association between debt and labor supply documented in U.S. survey data (SCF, CPS, HRS) is causal; establishing causality in those settings is challenging (p. 1204)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1171-1207); seven results extracted from tables and figures. Data is from the Polish Ministry of Entrepreneurship and Technology (administrative tax records) and is proprietary-confidential. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; one fix: R4 interaction-coefficient lower bound corrected from 0.253 to 0.233 (Table V col 6) to reflect full six-specification range; all other locators, magnitudes, equations, and frontmatter facts confirmed correct."
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13413", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-16; no Creative Commons licence; paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification strategies, and the key
estimating equations: enough to know what it found and how, without reading all 37 pages.
To replicate or extend it, read the full source at
[10.1111/jofi.13413](https://doi.org/10.1111/jofi.13413).

## TL;DR

Using a panel of Polish income tax records linked to floating-rate mortgage interest
deductions (2005-2015), Zator shows that households increase their gross labor income
by roughly PLN 0.35 for each PLN 1 increase in mortgage interest payments. The effect
is causal: identification exploits within-household variation in mortgage size interacted
with the reference rate (WIBOR or LIBOR), instrumented to remove endogenous prepayment.
The response is sizable and asymmetric: households react two to three times more
strongly to payment increases than to decreases. Secondary earners (often women) and
dual-earner childless households drive the increase response, consistent with the fixed
costs of entering the labor market and consumption commitment models.

## Core results

Magnitudes and significance are as reported; `\*\*\*` = 1%, `\*\*` = 5%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Labor income rises PLN 0.30-0.35 for each PLN 1 increase in mortgage interest (OLS)** | Table III, p. 1185 | Coefficients 0.337 to 0.348\*\*\* (mortgage holders, cols 1-3); 0.297\*\*\* (full population, col 4); se 0.020-0.021 |
| R2 | **IV estimates confirm OLS: PLN 0.35-0.46 response; reference-rate x mortgage-size instrument** | Table III, p. 1185 | IV col 5 (mortgage holders): 0.459\*\*\* (se 0.043); IV col 6 (full pop): 0.348\*\*\* (se 0.037); OLS and IV confidence intervals overlap |
| R3 | **Currency-comparison design (PLN vs CHF loans) gives a smaller estimate of PLN 0.15, consistent with asymmetry** | Table IV, p. 1188 | IV cols 4-5: 0.148\*\*\* (se 0.034) mortgage holders, 0.145\*\*\* (se 0.016) all; smaller because the CHF/WIBOR divergence covers only the declining-rate 2013-2015 period |
| R4 | **Response to payment increases is 2-3x larger than to decreases (asymmetric labor supply)** | Table V, p. 1192; Figure 3, p. 1193 | Average coefficient 0.106-0.283\*\*\*; interaction on increases 0.233\*\*\* to 0.313\*\*\* (six specs); slope for increases roughly 2-3x slope for decreases across all six specifications |
| R5 | **Dual-earner households and secondary (often female) earners drive the increase response; women show more pronounced asymmetry** | Figure 6, p. 1198; Figure 7, p. 1199 | Dual-earner coefficient on payment increase ~0.48 vs single-earner ~0.14; secondary earner coefficient substantially higher than primary on increases; women increase income strongly on increases but do not reduce significantly on decreases |
| R6 | **Higher mortgage payments reduce the probability of remaining a single-earner household by 0.1 pp per PLN 1,000** | Table VI, col 4, p. 1201 | Coefficient -0.113\*\*\* (se 0.021); mean dep var 27.5%; consistent with spousal labor market entry as a key mechanism |
| R7 | **Higher mortgage payments raise the probability of changing jobs by 0.104 pp per PLN 1,000** | Table VI, col 6, p. 1201 | Coefficient 0.104\*\*\* (se 0.013); mean dep var 21.9%; consistent with households accepting higher-paying, less-preferred jobs to service debt |

**Overall (paper's conclusion).** Households with floating-rate mortgages adjust their
labor supply substantially in response to interest rate changes. Income adjusts by roughly
35% of the payment change on average, with a markedly stronger response to increases.
The adjustment operates through spousal labor market entry, supplemental gig income,
and job changes toward higher-paying positions. The asymmetry helps reconcile the wide
dispersion of labor supply elasticity estimates in the literature: lottery-win studies
such as Imbens, Rubin, and Sacerdote (2001) and Cesarini et al. (2017) capture responses
to budget-loosening shocks (comparable to payment decreases here), while Di Maggio et al.
(2017) document consumption responses to ARM resets consistent with the labor supply
responses this paper finds. Brown and Matsa (2020) and Bernstein and Koudijs (2020)
show correlated patterns in the relationship between household debt and labor market
outcomes.

## Theory / model

The paper has no formal structural model. It operates from a standard household
labor-leisure model in which the household equates the marginal disutility of work
with the marginal utility of consumption (p. 1184). When mortgage payments rise, the
available budget for non-housing consumption falls, raising the marginal utility of
consumption and, under concave utility, inducing greater labor supply. This mechanism
implies the response to payment increases should be stronger than to decreases when
utility is concave, which is the core theoretical prediction tested in Section IV.

The paper invokes Chetty and Szeidl (2007) to argue that consumption commitments
(housing being the canonical commitment) amplify the asymmetry. With a commitment
that cannot be adjusted downward quickly, an increase in the committed payment has
a large liquidity effect with no offsetting consumption substitution on the downside.

## Method

The paper uses two complementary identification strategies, both estimating
panel regressions with individual fixed effects and rich controls.

**Strategy 1: Reference-rate x Mortgage-size variation (equation (1), p. 1180).** The
main estimating equation is:

$$
Y_{i,t} = \alpha \cdot (\text{Interest}_{i,t} = \text{RefRate}_t \cdot \text{LoanSize}_i) + \mu_i + \xi X_{i,t} + \epsilon_{i,t} \tag{1}
$$

where $$Y_{i,t}$$ is gross household income for person $$i$$ in year $$t$$,
$$\text{Interest}_{i,t}$$ is annual mortgage interest deducted from taxable income,
$$\mu_i$$ is an individual fixed effect, and $$X_{i,t}$$ includes year-by-age-by-previous-income
bin fixed effects and county-year fixed effects. To remove endogenous variation from
prepayment decisions, interest is instrumented with the product of the reference rate
(WIBOR for PLN loans, LIBOR CHF for CHF loans) and an estimate of initial mortgage
size (the household's second observed positive interest payment). The instrument is
strong (Kleibergen-Paap F-statistics of 5.5-7.6 x 10^4 in Table III, p. 1185).

This approach resembles a shift-share design (Borusyak, Hull, and Jaravel (2022)):
the endogenous exposure measure (mortgage size) is interacted with several exogenous
shocks (11 years of reference rate changes from two correlated rates). Standard errors
are clustered at the household level throughout.

**Strategy 2: Currency-comparison design (equation (2), p. 1181).** The second design
compares PLN-indexed (WIBOR) and CHF-indexed (LIBOR) mortgages of the same size after
2012, when LIBOR hit the zero lower bound while WIBOR continued to decline:

$$
Y_{i,t} = \beta \cdot (\text{Interests}_{i,t} = \text{LoanSize}_i \cdot \text{Post2013}_t \cdot \text{PLNLoan}_i)
+ \phi \cdot \!\!\left(\text{LoanSize}_i \cdot \sum_{t=2006}^{2015} \text{Year}_t\right)
+ \mu_i + \xi X_{i,t} + \epsilon_{i,t} \tag{2}
$$

The coefficient $$\beta$$ captures the differential income change for PLN-loan households
relative to CHF-loan households of the same size after 2013. Since LIBOR was flat and
WIBOR declined, this design identifies the labor supply response to payment decreases.

**Asymmetry test (equation (3), p. 1182).** To test asymmetry, the base specification
is augmented with an interaction between the interest payment and a binary indicator
for years in which payments increased:

$$
Y_{i,t} = \alpha \cdot \text{Interests}_{i,t} + \beta \cdot \text{Interests}_{i,t} \cdot \text{Increase}_{i,t} + \mu_i + \beta X_{i,t} + \epsilon_{i,t} \tag{3}
$$

The coefficient $$\alpha$$ captures the response to payment decreases and $$\alpha + \beta$$
captures the response to payment increases; Table V (p. 1192) shows $$\beta > 0$$ and
significant across three alternative definitions of the increase indicator.

## Empirical specifications

All regressions use a strongly balanced panel with observations weighted by the inverse
of household size (one or two). Standard errors are clustered at the household level
(or by year for robustness).

**First stage (Table II, p. 1185).** Reference rate interacted with mortgage size
strongly predicts interest payments: coefficient 0.223\*\*\* (se 0.001 household-cluster;
0.012 year-cluster) on the full mortgage-holder sample. WIBOR drives PLN-loan
interest (0.145\*\*, se 0.053); LIBOR CHF drives CHF-loan interest (0.234\*\*\*, se 0.041).

**Main income regressions (Table III, p. 1185).** Specification columns:
- Col 1-3: Mortgage holders, progressively adding previous-income-year FE and county-year FE. Coefficient stable at 0.337-0.348.
- Col 4: Full population (OLS); coefficient 0.297\*\*\*.
- Col 5-6: IV (instrument = RefRate x LoanSize); coefficient rises slightly to 0.459\*\*\* (mortgage holders) and 0.348\*\*\* (full population).

**Currency-comparison regressions (Table IV, p. 1188).** First stage: PLN loan x
post-2012 x loan size reduces interest paid by PLN 0.231\*\*\* per unit loan size
(se 0.010). Second stage income coefficients: 0.148\*\*\* and 0.145\*\*\* (IV). Pre-2012
coefficients insignificant, confirming parallel trends.

**Mechanism regressions (Table VI, p. 1201).** Specifications analogous to equation
(1) with alternative outcomes: log wages (0.0037\*\*\*, se 0.0002), log pensions
(-0.0001, insig.), log business profits (0.0107\*\*\*, se 0.0012), single-earner
probability (-0.113\*\*\*, se 0.021 per PLN 1,000), supplemental income indicator
(0.013\*, se 0.007), job-change indicator (0.104\*\*\*, se 0.013).

**Consumption and savings proxies (Table VII, p. 1203).** Interest payments reduce
charitable donations (asinh coefficient -0.0012\*\*\* to -0.0020\*\*\*), private pension
contributions (-0.0004\*\* to -0.0006\*\*\*), and internet-access spending
(-0.0019\*\*\* to -0.0018\*\*\*), confirming the income response reflects labor supply
rather than differential macroeconomic sensitivity of mortgage holders.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Polish Ministry of Entrepreneurship and Technology: income tax declarations (PIT), 2005-2015 | Universe of Polish taxpayers; individual income sources (wages, business profits, pensions), mortgage interest deductions, demographics (age, sex, county), consumption proxies (charitable donations, pension contributions, internet access) | No page yet |
| Three-month WIBOR (Warsaw Interbank Offered Rate) | Reference rate for PLN-denominated mortgages; the main shock variable interacted with mortgage size | No page yet |
| Three-month LIBOR CHF | Reference rate for CHF-denominated mortgages; used in currency-comparison design | No page yet |

Sample: Strongly balanced panel, 9.8 million individuals, 2005-2015 annual (100+
million observations). Mortgage-holder subsample: 171,445 individuals (1,714,450
observations). The data are obtained from the Polish government and are not publicly
available; replication requires an access agreement with the Polish Ministry of
Entrepreneurship and Technology.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13413) if you are:
studying the labor supply channel of monetary policy (Section III-IV give the clearest
panel IV evidence in a floating-rate mortgage setting); interested in the asymmetry of
labor supply responses to income shocks (Section IV and Table V); studying intrahousehold
labor supply and the role of secondary earners or women in debt-adjustment (Sections V-VI);
or using Poland as a case study for a nearly universal floating-rate mortgage market
(99.8% floating rate as of 2016, p. 1176).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pp. 1171-1207.
DOI: [10.1111/jofi.13413](https://doi.org/10.1111/jofi.13413).
This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified
or independently reproduced**. The article is paywalled; extract-only redistribution.

> Zator, Michal. "Working More to Pay the Mortgage: Household Debt, Interest Rates,
> and Family Labor Supply." *The Journal of Finance* 80, no. 2 (April 2025): 1171-1207.
> DOI: 10.1111/jofi.13413. © 2024 the American Finance Association.
> This page is an **extraction** by the Institute for Automated Research:
> core results summarized with source locators; **not a substitute for the original**.
