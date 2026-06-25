---
title: "Baby Booms and Asset Booms: Francke & Korevaar (2025)"
description: >-
  Distilled: Using centuries of data from Amsterdam and Paris, this paper shows
  that lagged birth rates are a major predictable driver of house prices, with
  high birth rates 25 to 29 years ago raising rent-price ratios and high birth
  rates 60 to 64 years ago lowering them; the effect concentrates in house
  prices rather than rents, consistent with age-dependent entry into and exit
  from homeownership. J. Finance 2025, CC BY 4.0. Six core results with source
  locators, datasets used, the estimating equation, and the mechanism analysis.
sidebar:
  label: Francke-Korevaar 2025
  order: 1
tags: [paper-summary, real-estate, demographics, housing, macro, panel-regression,
       time-series, open-access, cc-by, peer-reviewed, unreplicated,
       data:amsterdam-housing-transactions, data:paris-rents]
paper:
  authors: Marc Francke, Matthijs Korevaar
  authorList:
    - { family: Francke, given: Marc, affiliation: Amsterdam Business School, University of Amsterdam and Ortec Finance }
    - { family: Korevaar, given: Matthijs, affiliation: Erasmus School of Economics, Erasmus University Rotterdam }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 3021-3056
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13480
  licenseShort: CC BY 4.0
  resultsCount: 6
  citedByCount: 3
  jel:
    codes: [R21, G12, J11]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ['Demographics and Housing Markets', 'Asset Prices and Demographic Change', 'Historical Urban Economics']
  dataAccess: hand-collected
  outcome:
    - five-year change in rent-price ratio (log)
    - five-year change in house prices (log)
    - five-year change in rent prices (log)
    - probability of housing sale
    - bond and dividend yields
  outcomeClass: [asset-prices, household-finance]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-08-14; corroborated by artifact p.3021 Creative Commons
    Attribution License notice)
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC BY VOR licence confirmed in Crossref DOI metadata 2026-06-05)
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  introducesData: true
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [panel-regression, time-series-forecasting, survival-analysis, bayesian-repeat-sales]
    identification: descriptive
  contributionType: [new-fact, new-data, measurement]
  mechanisms: [participation-frictions, demand-elasticity]
  scope:
    region: Netherlands (Amsterdam), France (Paris)
    assetClass: residential real estate, government bonds, equities (VOC dividend yields)
    period: 1550-01..1884-12
    frequency: annual
    dataType: [market, administrative, other]
    granularity: [aggregate, security, transaction]
    n: "Amsterdam 256 five-year observations (1550-1884); Paris 242-331 annual observations (1500-1831)"
  findings:
    - ref: R1
      outcome: five-year change in rent-price ratio (log)
      metric: coefficient
      value: "B_{t-25/29} = -4.251*** (SE 1.130); B_{t-60/64} = 4.001*** (SE 0.837); adjusted R2 = 0.448"
      direction: mixed
      vsBenchmark: two birth-rate lags explain 18.4% of total variation in rent-price ratios over 250-year horizon (Table II col 3, p.3040)
    - ref: R2
      outcome: five-year change in house prices (log)
      metric: coefficient
      value: "B_{t-25/29} = 4.457*** (SE 1.314); B_{t-60/64} = -4.033*** (SE 1.377); adjusted R2 = 0.587"
      direction: mixed
      vsBenchmark: effect on house prices large and significant across all control specifications (Table III cols 1-3, p.3041)
    - ref: R3
      outcome: five-year change in rent prices (log)
      metric: coefficient
      value: "B_{t-25/29} = -0.562 (SE 0.651), insignificant; B_{t-60/64} = -0.862* (SE 0.509); adjusted R2 = 0.310"
      direction: none
      vsBenchmark: rent effect near zero and much smaller than house price effect; confirms price not rent channel (Table III cols 4-6, p.3041)
    - ref: R4
      outcome: probability of housing sale
      metric: probability
      value: "Cohort arrival at purchasing age (lag ~37 yrs): +0.1 pp probability of sale (+4%); effect is slow, peaking years after price effects (Figure 5, p.3047)"
      direction: positive
      vsBenchmark: price effects peak at lag ~25, sale-probability effects peak at lag ~37, confirming sluggish supply response
    - ref: R5
      outcome: five-year change in house prices (log)
      metric: coefficient
      value: "Young cohort (teen lag): ~2% higher house price growth in low- vs high-homeownership areas; early-30s lag: ~1% higher growth in high-homeownership areas (Figure 6, p.3049)"
      direction: positive
      vsBenchmark: "spatial segmentation pattern matches housing life-cycle: renters in low-HO areas, buyers in high-HO areas"
    - ref: R6
      outcome: bond and dividend yields
      metric: coefficient
      value: "B_{t-25/29} on bond yield i: 1.555 (SE 1.318), insignificant; B_{t-25/29} on dividend yield d: -1.192 (SE 0.792), insignificant; B_{t-60/64} on dividend yield: 1.525** (SE 0.751)"
      direction: none
      vsBenchmark: no significant effect of young-cohort birth rates on other asset yields; confirms housing-specificity of main result (Table V, p.3053)
  resultType: new-finding
  relatesTo:
    - { cite: "Mankiw and Weil (1989)", relation: extends, note: "extends their cross-sectional age-demand approach to long historical time series using lagged birth rates rather than current age structure" }
    - { cite: "Poterba (2001)", doi: '10.1162/003465301753237650', relation: tests, note: "tests and finds limited support for general demographic asset-price effects; young-cohort effect is housing-specific, not broad asset demand" }
    - { cite: "DellaVigna and Pollet (2007)", doi: '10.1257/aer.97.5.1667', relation: builds-on, note: "builds on their idea that predictable demographic demand shifts cause price effects because investors do not fully anticipate them" }
    - { cite: "Eichholtz, Korevaar, and Lindenthal (2020)", relation: builds-on, note: "uses their Amsterdam and Paris repeat-rent indices as the rent price series" }
  openQuestions:
    - "Whether findings generalize beyond pre-demographic-transition Amsterdam and Paris to modern contexts with higher life expectancy, welfare-state pensions, and rental regulation; OECD panel results are more limited and correlational (p.3044, Section III.C)."
    - "Difficulty separately identifying housing consumption from investment demand effects in the data; cannot observe the exact tenure-transition decision at the individual level (p.3045)."
    - "The role of credit availability in moderating or amplifying demographic price effects; credit was more limited historically and varies across modern markets (pp.3022, 3030)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-05", role: extracted, note: "Full text read (pp. 3021-3056); six results extracted from the CC-BY PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: "2026-06-05", role: verified, note: "Locators and reported magnitudes re-checked against source PDF; all six Core-results rows confirmed correct; fixed one Theory-section background equation subscript (B_{t-lag/4+lag} -> B_{t-lag}, matching PDF p.3037 intermediate derivation)." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13480", checked: "2026-06-05", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-14" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the empirical model, and the mechanism
analysis: enough to know what it found and how, without reading all 36 pages.
To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13480).

## TL;DR

Using centuries of housing transaction data from Amsterdam (1550-1884) and rent
data from Paris (1500-1831), Francke and Korevaar show that lagged birth rates
are a major and predictable driver of house prices. A high birth rate 25 to 29
years ago, when a large cohort enters prime home-buying years, raises house
prices relative to rents by about 4% per percentage-point increase in the
five-year birth rate. A high birth rate 60 to 64 years ago, when a large cohort
exits homeownership at death or through a move to senior housing, lowers
rent-price ratios by a similar magnitude. These effects concentrate
in house prices and not in rent prices, pointing to age-concentrated entry into
and exit from homeownership rather than general housing consumption demand. The
two lags together explain about 18% of total variation in rent-price ratios over
250 years. Mechanism analysis finds that sale probabilities respond sluggishly to
demographic demand shocks, and that spatial segmentation between rental and
owner-occupied markets contributes to the large price effects.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Lagged birth rates 25-29 and 60-64 years ago predict rent-price ratios**, with the two lags explaining 18.4% of total variation over 250 years | Table II col. 3, p. 3040 | Birth rate 25-29 yrs ago: coeff. -4.251\*\*\* (SE 1.130); birth rate 60-64 yrs ago: coeff. 4.001\*\*\* (SE 0.837); adj. R2 = 0.448 |
| R2 | **Effect concentrates in house prices**, with birth rates 25-29 yrs ago raising house prices and birth rates 60-64 yrs ago lowering them | Table III cols. 1-3, p. 3041 | Coeff. on B_{t-25/29} = 4.457\*\*\* (SE 1.314); coeff. on B_{t-60/64} = -4.033\*\*\* (SE 1.377); adj. R2 = 0.587 |
| R3 | **Rent prices show little to no response** to lagged birth rates in Amsterdam or Paris; rents are not the channel | Table III cols. 4-9, p. 3041 | B_{t-25/29} on Amsterdam rents: -0.562 (SE 0.651), insignificant; B_{t-60/64}: -0.862\* (SE 0.509); Paris rents: similarly weak |
| R4 | **Transaction probability responds to demographic shocks but with a delay**, peaking years after price effects, consistent with slow supply adjustment | Figure 5, p. 3047 | Birth-rate lag ~37 yrs raises sale probability by 0.1 pp (+4%); price effects peak at lag ~25, sale-probability effects at lag ~37 |
| R5 | **Spatial segmentation supports the mechanism**: young cohorts raise prices in low-homeownership (rental) areas; homeownership-age cohorts raise prices in high-homeownership areas | Figure 6, p. 3049 | Young-cohort (teen) lag: ~2% higher house price growth in low- vs high-homeownership areas; early-30s lag: ~1% excess growth in high-homeownership areas |
| R6 | **No significant effect on bond or young-cohort dividend yields**, confirming the effect is housing-specific and not general asset demand | Table V, p. 3053 | B_{t-25/29} on bond yield: 1.555 (SE 1.318), insignificant; on dividend yield: -1.192 (SE 0.792), insignificant; only old-cohort lag shows weak positive dividend yield effect |

**Overall (paper's conclusion).** Demographics have been a major, predictable
driver of house prices relative to rents over multiple centuries. The effect
arises because entry into and exit from homeownership are strongly
age-concentrated, and because other market participants respond slowly to shifts
in ownership demand rather than immediately converting rental units to
owner-occupied ones and vice versa. The effect is specific to housing: there is
no evidence of similar effects on bond yields and only weak evidence for
dividend yields, ruling out a general life-cycle asset-demand explanation.

## Theory / model

The paper has no formal dynamic equilibrium model. Instead, it builds on the
insight that total housing demand in year $$t$$ can be written as
$$D_t = \sum_j \hat{\alpha}_j N_{jt}$$, where $$N_{jt}$$ is the number of individuals
aged $$j$$ and $$\hat{\alpha}_j$$ is a (constant) age-specific demand weight estimated
from cross-sectional data on residents' housing choices. This is the
Mankiw and Weil (1989) framework (p. 3036). The aggregate house price or index
$$h_t$$ then depends on $$D_t$$ via a simple time-series regression:

$$
h_t = \delta_0 + D_t \delta_1 + \varepsilon_t \tag{background}
$$

Since the authors do not observe age-specific population counts $$N_{jt}$$ in the
historical setting, they substitute a linear approximation: the change in demand
$$\Delta D_t$$ is a linear function of lagged birth rates $$B_{t-\text{lag}}$$, so
that changes in house prices (in logs) become:

$$
\Delta h_t \approx \alpha + \sum_{\text{lag}} B_{t-\text{lag}} \beta_{\text{lag}} + \varepsilon_t
$$

**Identification logic.** The paper uses lagged birth rates as the key predictor
rather than current demographic structure, for three reasons stated on p. 3023:
(i) lagged birth rates predate the outcomes by decades and so are less likely to
be jointly driven by current economic conditions; (ii) migration, which is
endogenous to economic opportunity, induces endogeneity in current age structure
but not in birth rates from generations ago; and (iii) using lags allows a test
for predictability, since birth cohorts and their eventual housing demand are
known far in advance. The paper focuses on rent-price ratios (rather than price
levels) to further reduce sensitivity to shared confounders: if past birth rates
correlate with current economic activity, that would affect house prices and
rents similarly, but the ratio difference would remain.

The identification strategy builds on the idea from DellaVigna and Pollet (2007)
that predictable demographic demand shifts generate price effects because
investors do not fully anticipate them. It also updates the findings of
Poterba (2001), who found limited evidence that demographic shifts affect
aggregate asset prices; the present paper shows the housing market is the
exception, not a general effect across all assets.

No causal identification device (instrument, natural experiment, RDD) is
deployed; the strategy is predictive/descriptive using deep historical variation
to exploit many decades of pre-demographic-transition fluctuations in birth
rates.

## Method

The main estimating equation is a time-series predictive regression of five-year
log changes in rent-price ratios, house prices, or rents on lagged five-year
birth rates (equation 1, p. 3037):

$$
y_t - y_{t-5} = \alpha + \sum_{\text{lag} \in L} B_{t - \text{lag}/4 + \text{lag}} \beta_{\text{lag}} + z_t' \gamma + \varepsilon_t \tag{1}
$$

where $$y$$ is the log rent-price ratio $$(r - h)$$, the log house price index
$$h$$, or the log rent index $$r$$; $$B_{t - \text{lag}/4 + \text{lag}}$$ is the total
five-year birth rate summed over lags $$t-\text{lag}$$ through $$t-\text{lag}+4$$;
$$z_t$$ is a vector of contemporaneous control variables (birth rate, mortality,
nuptiality, migration, wage growth, inflation, GDP per capita log change); and
$$L$$ is a set of lag lengths between 15 and 70 years (in five-year steps,
corresponding to cohorts aged 15 to 74 at time $$t$$).

Serial correlation from overlapping five-year differences is addressed by
Newey-West standard errors with a lag length of five (p. 3037). The paper
estimates equation (1) for various sets $$L$$: a single lag, two lags (young and
old cohort), and all lags jointly. The main reported results use two lags
corresponding to birth rates 25-29 years ago (peak homeownership-entry cohort)
and 60-64 years ago (peak exit cohort).

The probability-of-sale mechanism is tested using a discrete-time hazard model
for the probability that property $$i$$ sells at holding duration $$d = t_i - s_i$$
(equations 2a-2b, p. 3046):

$$
\Pr(D_{is} = t_i - s_i) = H_{is}(t_i - s_i) S_i(t_i - s_i - 1) \tag{2a}
$$

$$
\Pr(D_{it} > T - s_i) = S_i(T - s_i) \tag{2b}
$$

where $$H_{is}(d) = (1 + \exp(-x_{isd}' \beta))^{-1}$$ is a logistic hazard function
and $$S_{is}(d) = \prod_{j=1}^d (1 - H_{is}(j))$$ is the survival probability.
This is estimated by logistic regression in property-period format.

## Empirical specifications

**Main specification (Table II, p. 3040; Table III, p. 3041).** The baseline
uses five-year log changes in the Amsterdam rent-price ratio as the dependent
variable, with two birth-rate lags (25-29 yrs and 60-64 yrs). All variables are
in five-year differences to address unit-root concerns (unit-root tests reject
the null in levels; p. 3038). Six columns vary the control set:

- Column (1): no controls (adj. R2 = 0.178)
- Column (2): demographic controls (birth rate, mortality, nuptiality, migration)
- Column (3): demographic + economic controls (wage growth, inflation, GDP per capita); baseline
- Column (4): baseline + lagged controls matching the birth-rate lag windows
- Column (5): baseline + housing-quality growth control
- Column (6): baseline + interest rate

The coefficients on the two main birth-rate lags are stable across all six
specifications: approximately -4 (young cohort) and +4 (old cohort), both
significant at 1%.

**House prices vs. rents (Table III).** The same specification is run separately
for Amsterdam house prices, Amsterdam rents, and Paris rents. House prices show
large significant effects (coeff. ~4.5 and -4.0). Rents show near-zero and
generally insignificant effects, both in Amsterdam and Paris, confirming that
the rent-price ratio result is driven by house prices.

**Robustness: supply constraints (Table IV, p. 3051).** The baseline is
interacted with a supply-constrained dummy (SC = 1 before 1668 and after 1855,
the two Amsterdam expansion episodes). Interaction effects are insignificant,
and the main birth-rate coefficients are unchanged, ruling out that results are
driven by periods of constrained supply.

**Other assets (Table V, p. 3053).** The same two-lag specification is run for
five-year changes in Dutch government bond yields and Dutch East India Company
dividend yields. The young-cohort lag is insignificant for both. The old-cohort
lag shows a weakly significant positive effect only on dividend yields
(coeff. 1.525\*\*, SE 0.751), consistent with estate sales rather than general
life-cycle asset demand.

**Segmentation (Figure 6, p. 3049).** Separate house price indices for streets
with low, medium, and high homeownership rates (from the 1805 Amsterdam rental
census) are estimated via repeat-sales and regressed on the same birth-rate
lags. The spatial pattern of coefficients by lag length matches the predicted
housing life-cycle: young cohorts raise prices in low-HO (rental) areas,
mature cohorts raise prices in high-HO (owner-occupied) areas.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Amsterdam housing transaction data (mandatory aldermen registrations, 1620-1811; 19th-century repeat-sales on Herengracht) | Main house price index via Bayesian repeat-sales (Francke 2010); segmentation analysis | [Amsterdam housing](/wiki/datasets/amsterdam-housing-transactions/) |
| Paris repeat-rent indices (Eichholtz, Korevaar, and Lindenthal 2020) | Rent price series for Paris 1500-1831 (new rental contracts only) | [Paris rents](/wiki/datasets/paris-rents/) |
| Amsterdam repeat-rent index (Eichholtz, Korevaar, and Lindenthal 2020) | Rent price series for Amsterdam 1550-1884 | [Amsterdam housing](/wiki/datasets/amsterdam-housing-transactions/) |
| Amsterdam archival civil registers (Amsterdam City Archives, from 1554) | Annual births, deaths, marriages for demographic rates | No page yet |
| Paris demographic data (historians + official Paris statistics) | Annual births, deaths, marriages for demographic rates 1500-1831 | No page yet |
| Dutch government bond yields (provincial debt pre-1810, national debt post-1810) | Test of general asset-demand mechanism | No page yet |
| Dutch East India Company (VOC) dividend yields (Golez and Koudijs 2018) | Test of general asset-demand mechanism, 1629-1782 | No page yet |
| 1805 Amsterdam rental census (Amsterdam City Archives) | Street-level homeownership rates for segmentation analysis | [Amsterdam housing](/wiki/datasets/amsterdam-housing-transactions/) |
| OECD panel on house prices, rents, demographics (1970-2020) | Modern-context robustness check (Internet Appendix Section VI) | No page yet |

Sample: Amsterdam rent-price ratio 1550-1884 (N=256 five-year observations);
Paris rents 1500-1831 (N=242-331 observations); probability-of-sale sample
covers all Amsterdam repeat-sales pairs 1620-1811. Annual frequency, aggregated
to five-year differences for main regressions.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13480) if you are:
investigating demographic drivers of house prices or rent-price ratios, building
a model of the housing life-cycle and its aggregate price implications, or
studying the historical Amsterdam or Paris housing and rental markets. The
Internet Appendix (available online) contains the full list of historical data
sources (Table IA.V), the age-distribution evidence for the United States
(Section II.A), the OECD modern-context replication (Section VI), and further
robustness checks including all-lag regressions (Table IA.VI) and the
probability-of-sale two-lag results (Table IA.VII).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was
extracted by an LLM on 2026-06-05 and is **not human-verified or independently
reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not
hosted in this batch.

> **Attribution (CC BY 4.0).** Francke, Marc, and Matthijs Korevaar.
> "Baby Booms and Asset Booms: Demographic Change and the Housing Market."
> *The Journal of Finance* 80, no. 5 (October 2025): 3021-3056.
> DOI: 10.1111/jofi.13480. (C) 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
