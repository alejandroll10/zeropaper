---
title: "How Credit Cycles across a Financial Crisis: Krishnamurthy & Muir (2025)"
description: >-
  Distilled: Using credit spreads and credit growth across 17 countries from
  1869 to 2022, this paper shows that spread spikes at crisis onset predict
  worse output losses, especially when precrisis credit growth was high, and
  that frothy credit markets (low spreads + high credit growth) predict future
  crises. J. Finance 2025, paywalled. Seven core results with source locators,
  datasets used, the FZ model of crises, and the estimating specifications.
sidebar:
  label: Krishnamurthy-Muir 2025
  order: 1
tags: [paper-summary, credit-cycles, financial-crises, macro, credit-risk,
       panel-regression, descriptive, peer-reviewed, unreplicated,
       data:jst-macrohistory, data:barro-ursua]
paper:
  authors: Arvind Krishnamurthy, Tyler Muir
  authorList:
    - { family: Krishnamurthy, given: Arvind, orcid: "0000-0002-9505-9528", affiliation: Stanford Graduate School of Business and NBER }
    - { family: Muir, given: Tyler, affiliation: UCLA Anderson School of Management and NBER }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1339–1378
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13431
  jel:
    codes: [G01, E44, G15]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Banking stability, regulation, efficiency
    - Global Financial Crisis and Policies
    - Insurance and Financial Risk Management
  dataAccess: public
  outcome:
    - cumulative per-capita GDP growth following a financial crisis
    - probability of a financial crisis in the next five years
    - credit spread level in precrisis period
  outcomeClass: [credit-risk, macro-aggregates]
  license: >-
    Wiley terms and conditions (vor); confirmed via Crossref DOI metadata:
    content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-03-04. Not open access.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 0
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [panel-regression, logit-regression]
    identification: descriptive
  contributionType: [new-fact, new-data, measurement]
  mechanisms: [financial-constraint, intermediary-constraint, behavioral-bias, learning]
  introducesData: true
  scope:
    region: global
    assetClass: corporate and sovereign bonds; real per-capita GDP
    period: 1869-01..2022-12
    frequency: annual
    dataType: [market, accounting, administrative]
    granularity: [aggregate]
    n: "17 countries; 1,006 country-year spread observations; 40 JST-mod financial crisis episodes"
  findings:
    - ref: R1
      outcome: cumulative per-capita GDP growth following a financial crisis
      metric: coefficient
      value: "Delta-spread x crisis dummy: -2.21 (s.e. 0.74) at 3-year horizon; -1.48 (s.e. 0.60) at 5-year horizon (Table IV col 2)"
      direction: negative
      vsBenchmark: "spread change in crisis adds ~2.2% additional GDP decline per 1-sigma spread spike beyond the unconditional crisis path"
    - ref: R2
      outcome: cumulative per-capita GDP growth following a financial crisis
      metric: coefficient
      value: "Delta-cred x crisis dummy: -2.06 (s.e. 0.95) at 3-year horizon; -2.65 (s.e. 1.10) at 5-year horizon (Table IV col 3)"
      direction: negative
      vsBenchmark: "spread spike coupled with high precrisis credit growth adds ~2.1pp extra GDP loss per 1-sigma credit growth shock; independent of spread change effect"
    - ref: R3
      outcome: cumulative per-capita GDP growth following a financial crisis
      metric: coefficient
      value: "Quantile regression: coefficient on Delta-spread is -0.36 at 75th quantile, -1.12 at 25th quantile (Table V)"
      direction: negative
      vsBenchmark: "spread changes particularly informative for tail (low quantile) output outcomes; fattens the left tail of the output distribution"
    - ref: R4
      outcome: credit spread level in precrisis period
      metric: coefficient
      value: "Precrisis-period dummy (t-6 to t-4): -0.26 (s.e. 0.14) excluding year FE; -0.44 (s.e. 0.15) including year FE (Table VII col 3-4)"
      direction: negative
      vsBenchmark: "spreads are ~0.28-0.45 sigma below average in the 3-6 years preceding a crisis; not observed before nonfinancial recessions"
    - ref: R5
      outcome: probability of a financial crisis in the next five years
      metric: probability
      value: "HighFroth x HighCredit OLS: 0.27 (s.e. 0.09) full sample; 0.14 (s.e. 0.07) out-of-sample (Table VIII col 3; Table X col 3)"
      direction: positive
      vsBenchmark: "combined froth+high-credit signal raises 5-year crisis probability by ~27pp in-sample; weakens to ~14pp out-of-sample; froth does not predict nonfinancial recessions"
    - ref: R6
      outcome: cumulative per-capita GDP growth following a financial crisis
      metric: coefficient
      value: "Postwar sample (Table XI col 2): Delta-spread x crisis: -1.43 (s.e. 0.53); full-sample result -2.21 (s.e. 0.74)"
      direction: negative
      vsBenchmark: "postwar estimate statistically similar to full-sample; results robust across data periods"
    - ref: R7
      outcome: cumulative per-capita GDP growth following a financial crisis
      metric: coefficient
      value: "Alternative crisis dating (Table XV): BVX dates -2.47 (s.e. 0.71); RR dates -2.36 (s.e. 0.48); JST -2.21 (s.e. 0.74)"
      direction: negative
      vsBenchmark: "coefficient on spread-change x crisis is economically and statistically similar across JST, Reinhart-Rogoff, and Baron-Verner-Xiong chronologies"
  resultType: new-finding
  relatesTo:
    - { cite: "Schularick & Taylor (2012)", relation: extends, note: "replicates their credit-growth predictor and adds complementary credit-spread information to describe both crisis severity and predictability" }
    - { cite: "Baron & Xiong (2017)", doi: '10.1093/qje/qjx004', relation: extends, note: "confirms their froth finding and shows combined low-spread + high-credit signal is the sharpest predictor of crises" }
    - { cite: "Jorda, Schularick & Taylor (2011)", doi: '10.1057/imfer.2011.8', relation: extends, note: "builds on their JST crisis dating and credit-boom analysis; adds spread dimension" }
    - { cite: "Reinhart & Rogoff (2009)", relation: tests, note: "uses their RR crisis chronology as robustness; results hold across dating conventions" }
    - { cite: "Muir (2017)", doi: '10.1093/qje/qjw045', relation: builds-on, note: "builds on asset-pricing view that crises involve rising risk premia embedded in spread spikes" }
    - { cite: "Brunnermeier & Sannikov (2014)", doi: '10.1257/aer.104.2.379', relation: tests, note: "empirically challenges their FZ-model prediction that fragility buildup should raise precrisis spreads; data show the opposite" }
  openQuestions:
    - "Whether the froth signal (low spreads + high credit) can be sharpened to have stronger out-of-sample crisis prediction power, given that in-sample results weaken substantially in rolling out-of-sample tests (pp. 1366-1367, Table X)."
    - "Whether the low-spread precrisis pattern reflects rational falling risk-neutral default probabilities, time-varying risk premia, or agents' systematic underestimation of crisis likelihood; the regressions cannot distinguish these explanations (p. 1362, 1367-1368)."
    - "How well the documented stylized facts generalize to emerging markets and countries outside the 17-country sample (p. 1373-1374)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1339-1378 plus appendix); seven results extracted from Tables IV, V, VII, VIII, X, XI, XV. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all 7 Core-results rows confirmed correct. Fixed: (1) Theory eq (4) constant term corrected from bar-gamma_i to gamma_{i,0} per PDF p. 1359; (2) findings[R2] value label corrected from 'HighCredit x Delta-spread interaction' to 'Delta-cred x crisis dummy' to match Table IV col 3." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13431", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-04. Paywalled; not open access." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical framework it tests (the FZ model of financial crises), and the estimating specifications with exact source locators: enough to know what it found and how, without reading all 40 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13431).

## TL;DR

This paper documents how credit spreads and credit growth co-evolve across financial crises in 17 countries from 1869 to 2022. Four stylized facts emerge: (i) crises begin with a sharp spike in spreads, signaling a sudden shift in expectations; (ii) the severity of the recession depends on the size of the spread spike (losses to financial intermediaries) interacted with precrisis credit growth (financial sector fragility); (iii) precrisis spreads are unusually low ("frothy"), not high, despite high credit growth; and (iv) the combination of low spreads and high credit growth is a meaningful predictor of future crises. These facts support fragility-amplification (FZ) theories of financial crises where credit supply expansions precede collapses, but the low-precrisis-spread finding challenges standard FZ models that predict rising spreads as fragility builds, pointing instead toward belief-formation models.

## Core results

Magnitudes and significance are as reported; locators point into the source PDF. Standard errors (Driscoll-Kraay with 8 lags) in parentheses.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Spread spikes at crisis onset predict worse output**: a 1-sigma spread increase in the crisis year reduces three-year cumulative GDP growth by ~2.2% beyond the average crisis path | Table IV col 2, p. 1354 | $$\Delta\hat{s}_{i,t} \times \mathbf{1}_{\text{crisis}}$$ coeff: -2.21 (s.e. 0.74) at 3-yr; -1.48 (s.e. 0.60) at 5-yr |
| R2 | **Fragility amplifies spread shocks**: one-sigma credit growth increases the output loss from a spread spike by ~2.1pp (3-yr) and ~2.6pp (5-yr) | Table IV col 3, p. 1354 | $$\Delta\text{cred}_{i,t} \times \mathbf{1}_{\text{crisis}}$$ coeff: -2.06 (s.e. 0.95) at 3-yr; -2.65 (s.e. 1.10) at 5-yr |
| R3 | **Spread changes fatten the left tail of output**: predictive power is concentrated in bad outcomes; coefficient nearly triples from 75th to 25th quantile | Table V, p. 1357 | Quantile regression coefficient on $$\Delta\hat{s}$$: -0.36 at 75th pctile; -1.12 at 25th pctile |
| R4 | **Precrisis spreads are ~0.28-0.45 sigma too low**: in the three to six years before a crisis, spreads are significantly below the country average; not observed before ordinary recessions | Table VII col 3-4, p. 1361 | $$\mathbf{1}_{t-6,t-4}$$ coeff: -0.26 (s.e. 0.14) without year FE; -0.44 (s.e. 0.15) with year FE |
| R5 | **Low spreads + high credit growth predict crises**: the HighFroth x HighCredit interaction raises the five-year crisis probability by 27pp in-sample, but weakens to 14pp out-of-sample | Table VIII col 3, p. 1363; Table X col 3, p. 1367 | HighFroth x HighCredit OLS: 0.27 (s.e. 0.09) full sample; 0.14 (s.e. 0.07) OOS; froth does not predict nonfinancial recessions |
| R6 | **Results hold in postwar data**: postwar-only (post-1950) estimates are economically similar to full-sample estimates, albeit with larger standard errors | Table XI col 2, p. 1368 | $$\Delta\hat{s} \times \mathbf{1}_{\text{crisis}}$$ postwar: -1.43 (s.e. 0.53) vs. full-sample -2.21 (s.e. 0.74) at 3-yr |
| R7 | **Results robust to crisis dating chronology**: coefficients on spread-change x crisis are economically and statistically similar across JST, Reinhart-Rogoff (2009), and Baron-Verner-Xiong (2021) crisis dates | Table XV, p. 1371 | JST: -2.21 (s.e. 0.74); BVX: -2.47 (s.e. 0.71); RR: -2.36 (s.e. 0.48) |

**Overall (paper's conclusion).** The recessions surrounding financial crises are longer and deeper than nonfinancial recessions. The severity depends on the product of the spread spike (losses) and precrisis credit growth (fragility). Crises are preceded by frothy credit markets, indicating credit supply expansions, not demand. Standard FZ amplification models match the crisis-period facts but miss the low-precrisis-spread evidence. Models with time-varying beliefs (Moreira and Savov (2017); Krishnamurthy and Li (2025)) are better positioned to simultaneously fit both sets of stylized facts. The two prior-work pillars for this paper are Schularick and Taylor (2012), who established that credit booms predict crises and worse recoveries, and Baron and Xiong (2017), who showed that credit expansion coupled with an indicator of investor neglected crash risk predicts crises; this paper adds the credit-spread dimension to both. The crisis-dating framework relies on Jorda, Schularick, and Taylor (2011) (JST), and the risk-premium interpretation of spreads builds on Muir (2017), who documented that risk premia - not default probabilities - drive spread spikes in financial crises.

## Theory / model

The paper does not develop a new formal model. It instead tests a class of theoretical models of financial crises, which the authors label the "FZ model" (fragility-amplification), encompassing Kiyotaki and Moore (1997), Gertler and Kiyotaki (2010), He and Krishnamurthy (2013), Brunnermeier and Sannikov (2014), and Moreira and Savov (2017).

**The FZ structure.** Denote credit losses (p. 1341) as $$z_{i,t}$$, with $$\mathbb{E}_t[z_{i,t}] = 0$$, for country $$i$$ at time $$t$$. Denote the financial sector fragility as $$\mathcal{F}_{i,t}$$. The severity of the crisis depends on $$\mathcal{F}_{i,t} \times z_{i,t}$$: a large shock to a fragile sector triggers bank runs, credit contraction, and deep recession. Credit spreads proxy for both losses and financial sector assets:

$$
s_{i,t-1} = \gamma_{i,0} + \gamma_1 \text{Prob}^{\mathcal{Q}}(z_{i,t} > \underline{z}) \times \mathbb{E}_t^{\mathcal{Q}}[\text{Loss}_{i,t} | \text{crisis}] + \gamma_2 \text{Prob}^{\mathcal{Q}}(z_{i,t} \leq \underline{z}) \times \mathbb{E}_t^{\mathcal{Q}}[\text{Loss}_{i,t} | \text{no-crisis}] \tag{4}
$$

(p. 1359), where $$\text{Loss}_{i,t}$$ is increasing in $$\mathcal{F}_{i,t}$$. Precrisis, as $$\mathcal{F}_{i,t}$$ rises, spreads should rise - but the data show they fall. The reconciliation offered is that $$\text{Prob}^{\mathcal{Q}}(z_{i,t} > \underline{z})$$, the risk-neutral probability of a large loss, falls as credit growth rises, more than offsetting the fragility effect on spreads. This is consistent with models in which agents underestimate crisis likelihood during credit booms (Moreira and Savov (2017); Gennaioli, Shleifer, and Vishny (2013); Bordalo, Gennaioli, and Shleifer (2018)).

**The spread decomposition in a crisis.** In a crisis, illiquidity/fire-sale effects cause $$l_{i,t}$$ (an illiquidity component of spreads) to spike, leading to unexpected losses:

$$
s_{i,t} = \bar{\gamma}_i + \gamma_1 \mathbb{E}_t[\text{Loss}_{i,t}] + l_{i,t} \tag{\text{crisis}}
$$

Outside crises, spreads are better represented without the liquidity spike component and are passive forecasters of output, consistent with existing findings in the literature (Friedman and Kuttner (1992); Gertler and Lown (1999); Gilchrist and Zakrajsek (2012)).

## Method

The paper is a descriptive empirical study. The primary estimator is panel regression with Driscoll-Kraay standard errors allowing arbitrary serial correlation and cross-sectional dependence (8 lags), applied to an annual country-year panel. The paper also uses quantile regressions (Parente and Silva (2016)) and Logit specifications for crisis prediction.

**Spread normalization.** Raw spreads differ in level across countries (junk vs. investment grade). The paper normalizes by dividing by the country's unconditional mean spread (p. 1349, equation 2):

$$
\hat{s}_{i,t} \equiv \text{Spread}_{i,t} / \overline{\text{Spread}}^i \tag{2}
$$

This mean normalization exploits the homogeneity assumption that the sensitivity of spreads to the cycle is proportional to the average spread. The normalization is validated by showing that the coefficient on spread/mean is similar across pre-1940 (IMM bond data, mean spread 5.21%) and post-1940 (multiple sources, mean spread 1.13%) subsamples (Table III, cols 6-7).

**Fragility indicator.** The high-credit-growth variable $$\text{HighCredit}_{i,t}$$ counts the number of years in the past three years in which annual credit growth exceeded the full-sample median (divided by 3, so range 0 to 1); when $$\text{HighCredit}_{i,t} = 1$$ credit has been above median in each of the last three years. The froth indicator $$\text{HighFroth}_{i,t}$$ takes the residual of spread normalized on lagged GDP growth and five-year lagged spreads, averages the below-median dummy over the past five years (p. 1362-1363).

## Empirical specifications

**Main crisis-interaction regression (produces R1, R2, R6, R7).** Run on a panel of country-year observations with crisis and non-crisis dates (p. 1352, equation 3):

$$
\ln\!\left(\frac{y_{i,t+k}}{y_{i,t}}\right) = a_i + a_t + \mathbf{1}_{\text{crisis},i,t} \times b_{\text{crisis}}' Z_{i,t} + \mathbf{1}_{\text{no-crisis},i,t} \times b_{\text{no-crisis}}' Z_{i,t} + c' x_t + \varepsilon_{i,t+k} \tag{3}
$$

where $$y_{i,t}$$ is real per-capita GDP, $$k \in \{3, 5\}$$ years, $$Z_{i,t}$$ includes the normalized spread $$\hat{s}_{i,t}$$, the spread change $$\Delta\hat{s}_{i,t}$$, and credit growth $$\Delta\text{cred}_{i,t}$$, and $$x_t$$ includes two lags of GDP growth. Fixed effects: country ($$a_i$$) and year ($$a_t$$). Standard errors: Driscoll-Kraay with 8 lags. The key coefficient of interest is $$b_{\text{crisis}}$$ on $$\Delta\hat{s}_{i,t}$$ and its interaction with $$\Delta\text{cred}_{i,t}$$ (Table IV). Sample: 826 observations, 15 country groups.

**Quantile regression (produces R3).** Quantile regression of one-year output growth on $$\Delta\hat{s}_{i,t}$$ and $$\Delta\text{Credit}_{i,t}$$ at quantiles 90th, 75th, 50th, 25th, 10th (Table V, p. 1357). Controls: two lags of GDP growth, early-bond-data dummy, country and year fixed effects. Standard errors clustered by year. Sample: 826 observations, 826 at each quantile.

**Precrisis-spread regression (produces R4).** Regression of normalized spreads on crisis-time dummies from $$t - 6$$ to $$t + 5$$ (Table VII, p. 1361):

$$
\hat{s}_{i,t} = a_i + \sum_{\tau=-6}^{5} \delta_\tau \mathbf{1}_{t=\tau} + \text{controls} + \varepsilon_{i,t}
$$

with country fixed effects, early-bond-data dummy, and five-year lagged spread (controls for slow level changes). Standard errors: Driscoll-Kraay with 8 lags. The precrisis window $$t-6$$ to $$t-4$$ is combined into a single dummy in columns (3)-(4) to summarize the "too low" result.

**Crisis prediction (produces R5).** OLS and Logit specifications predicting the cumulative crisis indicator over a five-year horizon (whether any JST-mod crisis occurs in the next five years), on $$\text{HighFroth}_{i,t}$$, $$\text{HighCredit}_{i,t}$$, and their interaction (Tables VIII-IX, pp. 1363-1365). Country fixed effects, no time fixed effects (crisis prediction uses only pre-date information). Standard errors: Driscoll-Kraay with 8 lags (OLS), double-clustered by country and year (Logit). Out-of-sample version (Table X) constructs froth and credit variables in a rolling manner from 20 years after sample start.

All regressions exclude war periods (both world wars) because government intervention distorts bond prices and spread information.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Investors Monthly Manual (IMM), London Stock Exchange bond data, 1869-1929 | Corporate and sovereign bond yields for 17 countries; primary source for pre-1930 credit spreads | No page yet |
| Moody's Baa-Aaa spread (US, 1920-2014) | US credit spread in the modern period | No page yet |
| Global Financial Data (GFD) | Corporate and government bond yields for Australia, Belgium, Canada, Germany, Norway, Sweden, UK, Korea | No page yet |
| Datastream | Bond yields for Ireland, Portugal, Greece (2000-2014); European spreads | No page yet |
| Banque de France nonfinancial corporate spreads (Germany, France, Italy, Spain, 1999-2022) | European corporate credit spreads relative to German Bunds | No page yet |
| Swiss National Bank (SNB) data | Switzerland spreads from 2001 | No page yet |
| JST Macrohistory Database (Jorda, Schularick, Taylor (2017)) | Crisis dates, credit-to-GDP, real GDP per capita for 17 advanced economies | [JST Macrohistory](/wiki/datasets/jst-macrohistory/) (no page yet) |
| Barro-Ursua Macroeconomic Database | Real per-capita GDP; long historical series for advanced economies | [Barro-Ursua](/wiki/datasets/barro-ursua/) |

Sample: 17 countries; spread data 1869-2022 (by country); 1,006 country-year observations total for spreads; 40 financial crisis episodes with spread, credit, and output data available (the "JST mod." crises). Annual frequency.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13431) if you are: building a quantitative model of financial crises that needs empirical targets for spread dynamics and output losses; calibrating a fragility or amplification model to the interaction of losses x fragility; studying the credit-cycle predictor literature and want the international evidence on low-spread precrisis conditions; or interested in why standard FZ models with forward-looking spreads cannot match the frothy precrisis stylized fact. The tables are comprehensive: Table IV for the crisis-interaction results, Table VII for precrisis spread dynamics, Tables VIII-X for crisis prediction.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. Published under Wiley terms and conditions (paywalled; not open access). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Redistribution: extract-only.

> Krishnamurthy, Arvind, and Tyler Muir. "How Credit Cycles across a Financial Crisis."
> *The Journal of Finance* 80, no. 3 (June 2025): 1339–1378.
> DOI: 10.1111/jofi.13431. © 2025 the American Finance Association.
