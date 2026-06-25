---
title: "How to Dominate the Historical Average: Li, Li, Lyu & Yu (2025)"
description: >-
  Distilled: Proposes a conservative-slope forecast for the equity premium that
  sets the predictive slope to a small positive constant (1/A), reducing bias
  relative to the historical average while matching its zero estimation variance,
  and proves ex ante that this forecast first-order stochastically dominates the
  historical average whenever the population predictive slope is nonzero. Review
  of Financial Studies 2025, CC BY-NC-ND 4.0. Seven core results with source
  locators, datasets used, the theoretical framework, and the empirical method.
sidebar:
  label: Li-Li-Lyu-Yu 2025
  order: 1
tags: [paper-summary, asset-pricing, return-forecasting, equity-premium, time-series,
       panel-regression, peer-reviewed, unreplicated, data:shiller-data, data:wrds]
paper:
  authors: Kai Li, Yingying Li, Changlei Lyu, Jialin Yu
  authorList:
    - { family: Li, given: Kai, orcid: "0000-0003-4140-3802", affiliation: "Peking University HSBC Business School and PHBS Sargent Institute of Quantitative Economics and Finance" }
    - { family: Li, given: Yingying, orcid: "0000-0003-2580-1974", affiliation: "Hong Kong University of Science and Technology" }
    - { family: Lyu, given: Changlei, orcid: "0000-0002-2334-627X", affiliation: "Shanghai University of Finance and Economics" }
    - { family: Yu, given: Jialin, orcid: "0000-0001-9349-1766", affiliation: "Hong Kong University of Science and Technology" }
  year: 2025
  venue: The Review of Financial Studies 38(10), 2025, 3086–3116
  venueShort: Rev. Fin. Stud. 2025
  doi: 10.1093/rfs/hhaf010
  jel:
    codes: [G12, G11, C53]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Financial Markets and Investment Strategies", "Financial Risk and Volatility Modeling", "Stock Market Forecasting Methods"]
  dataAccess: licensed-commercial
  outcome:
    - out-of-sample equity premium forecast accuracy
    - out-of-sample R-squared for equity premium prediction
  outcomeClass: [security-returns]
  license: >-
    CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL https://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0,
    start 2025-02-12; corroborated by artifact p.3086 licence notice)
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access (Oxford University Press, CC BY-NC-ND 4.0, 2026-06-06)"
  redistribution: extract-only (CC BY-NC-ND 4.0 does not permit derivative mirroring without permission)
  resultsCount: 7
  citedByCount: 3

  methods:
    role: proposes-method
    contributes: conservative-slope-forecast
    family: descriptive
    buildsFrom: [time-series-forecasting]
    identification: descriptive

  contributionType: [new-method, new-theory, new-fact]

  mechanisms: [estimation-variance-reduction]

  scope:
    region: US
    assetClass: US equities (CRSP value-weighted index)
    period: 1872-01..2017-12
    frequency: annual
    dataType: [market]
    granularity: [aggregate]
    n: "23 predictors, annual US market returns 1872-2017 (sample varies by predictor; dp starts 1872)"

  findings:
    - ref: R1
      outcome: out-of-sample R-squared for equity premium prediction
      metric: oos-r-squared
      value: "3.4% (p=.044) for A=50 (dp predictor)"
      direction: positive
      vsBenchmark: positive vs historical average (HM); OLS gives 0.2% (p=.477)
    - ref: R2
      outcome: out-of-sample R-squared for equity premium prediction
      metric: oos-r-squared
      value: "2.1% (p=.019) for A=100 (dp predictor)"
      direction: positive
      vsBenchmark: "positive vs HM; more statistically significant than OLS (p=.477) and CT++ (p=.286)"
    - ref: R3
      outcome: out-of-sample R-squared for equity premium prediction
      metric: oos-r-squared
      value: "0.5% (p=.009) for A=500; 0.2% (p=.008) for A=1,000 (dp predictor)"
      direction: positive
      vsBenchmark: statistically significant at 99% level despite smaller magnitude; OLS is insignificant
    - ref: R4
      outcome: out-of-sample equity premium forecast accuracy
      metric: oos-r-squared
      value: "15 of 23 predictors have significantly positive OOS R-squared at 90% level; 8 at 95% level"
      direction: positive
      vsBenchmark: "vs historical average; OLS/CT generates statistically insignificant OOS R-squared for most predictors per Goyal and Welch (2008)"
    - ref: R5
      outcome: out-of-sample equity premium forecast accuracy
      metric: oos-r-squared
      value: "Method first-order stochastically dominates HM: CDF of MSE using method is everywhere above CDF of HM MSE (Figure 6, 40-year windows)"
      direction: positive
      vsBenchmark: beats HM on every quantile of MSE distribution; confirmed empirically with dp predictor
    - ref: R6
      outcome: out-of-sample equity premium forecast accuracy
      metric: oos-r-squared
      value: "Simulation OOS R-squared distributions: A=50 centered at ~4-5 (broadest), A=100 at ~3-4, A=200 at ~2, A=500 at ~1 (narrowest); all to the right of origin, i.e. positive R-squared"
      direction: positive
      vsBenchmark: all simulation R-squared distributions are right of zero (vs HM); OLS distribution spans negative values
    - ref: R7
      outcome: out-of-sample equity premium forecast accuracy
      metric: oos-r-squared
      value: "Confidence bounds from Campbell and Shiller (1988a) generate positive OOS R-squared from 1987 onward (A=209)"
      direction: positive
      vsBenchmark: "positive OOS R-squared using confidence bound as slope; demonstrates previously published estimates add value to OOS forecasts"

  resultType: new-finding

  relatesTo:
    - { cite: "Goyal and Welch (2008)", doi: '10.1093/rfs/hhm014', relation: tests, note: "Method is applied to and outperforms HM on the same 23 predictors; directly addresses their finding that regressions fail OOS" }
    - { cite: "Goyal, Welch, and Zafirov (2024)", doi: '10.1093/rfs/hhae044', relation: cites, note: "Confirms Goyal and Welch (2008) findings on larger predictor set over longer sample" }
    - { cite: "Campbell and Thompson (2008)", doi: '10.1093/rfs/hhm055', relation: extends, note: "Method generalizes CT sign restriction to a conservative constant slope; ex ante dominance proof answers their question of whether anything can beat HM" }
    - { cite: "Stambaugh (1999)", relation: cites, note: "Documents bias in OLS predictive slope for persistent predictors; motivates bias-reduction focus" }
    - { cite: "Clark and West (2006)", doi: '10.1016/j.jeconom.2006.05.023', relation: cites, note: "Show finite-sample noise makes OLS R-squared negative under null; method avoids this by using a constant slope" }
    - { cite: "Campbell and Shiller (1988a)", doi: '10.1093/rfs/1.3.195', relation: cites, note: "Provide confidence bounds used to set A=209 in main empirical test; positive predictive slope for dp" }

  openQuestions:
    - "Whether the method extends to multivariate forecasts combining multiple predictors simultaneously (p. 3091 and conclusion p. 3113-3114)."
    - "Whether advances in time-series econometrics that improve sign estimation and tighten confidence bounds will further sharpen the bias reduction and performance advantage (conclusion p. 3114)."
    - "Whether the approach improves shrinkage estimators by replacing the historical average as the shrinkage limit, an extension explored in Internet Appendix B.5 but not the focus of the paper (p. 3100-3101)."

  replicationCode:
    url: "https://doi.org/10.7910/DVN/9VNJUN"
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 3086-3116, 31 pages); seven results extracted with source locators. Not human-verified. Not reproduced. Replication code available at Harvard Dataverse." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "All 7 Core-results rows verified against PDF (Table 3 p.3110, Fig.3 p.3105, Fig.6 p.3112, §5.4 p.3112-3113); all equations (1-14) checked term-by-term; four fixes applied: (1) broken LaTeX delimiter $$b$ → $$b$$ in Method §Step 2, (2) mechanisms limits-to-arbitrage replaced with estimation-variance-reduction (paper invokes only bias-variance tradeoff), (3) Theorem 3 B₁ ≥ corrected to B₁ > per Lemma 1 strict inequality, (4) R6 simulation centers corrected from A=50~3.5/A=100~4 to A=50~4-5/A=100~3-4 (lower A → higher R², consistent with Fig.3 and paper text p.3104)." }

  licenceVerification:
    - { source: "Crossref REST API works/10.1093/rfs/hhaf010", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=https://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-02-12" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical framework (bias-variance trade-off in OOS forecasting, first-order stochastic dominance theorems), and the method (conservative-slope forecast with parameter A): enough to understand what it found and how, without reading all 31 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1093/rfs/hhaf010).

## TL;DR

The paper proposes an OOS equity premium forecast: instead of setting the predictive slope to zero (historical average) or estimating it by OLS, use a small positive constant slope $$\delta = 1/A$$ (where A is a large positive number calibrated to the lower confidence bound of the estimated slope). The method has zero estimation variance, matching the historical average, but a lower bias when the population slope is nonzero. The paper proves theoretically (Theorems 1-4) that this forecast first-order stochastically dominates the historical average, and shows empirically on 23 predictors from Goyal and Welch (2008) that 15 of 23 generate significantly positive OOS $$R^2$$ at the 90% level. Goyal, Welch, and Zafirov (2024) confirmed the Goyal and Welch (2008) findings using a larger predictor set, providing the direct motivation for the paper. The dividend-to-price ratio achieves an OOS $$R^2$$ of 2.1% (p = .019) at A = 100, versus an insignificant 0.2% for OLS. Clark and West (2006) show finite-sample estimation noise makes OLS $$R^2$$ negative under the null of no predictability; the proposed method avoids this by using a constant slope with zero variance.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*` = 10%/5%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Method OOS $$R^2$$ for dp predictor (A=50): statistically significant improvement over HM | Table 3, p. 3110 | $$R^2 = 3.4\%$$, p-value = .044; OLS $$R^2 = 0.2\%$$, p-value = .477 |
| R2 | Method OOS $$R^2$$ for dp predictor (A=100): gains statistical power as A increases | Table 3, p. 3110 | $$R^2 = 2.1\%$$, p-value = .019; OLS $$R^2 = 0.2\%$$, p = .477; CT++ $$R^2 = 1.8\%$$, p = .286 |
| R3 | Method OOS $$R^2$$ for dp predictor (A=500, A=1,000): very conservative slopes still beat HM at 99% significance | Table 3, p. 3110 | A=500: $$R^2 = 0.5\%$$, p=.009; A=1,000: $$R^2 = 0.2\%$$, p=.008 |
| R4 | Across 23 predictors, 15 (8) have positive OOS $$R^2$$ at 90% (95%) significance | §5 / Internet Appendix C, p. 3090-3091 | 15 of 23 at 90%; 8 of 23 at 95%; OLS and CT generate statistically insignificant $$R^2$$ for most (Goyal and Welch 2008) |
| R5 | Method first-order stochastically dominates HM for dp predictor: empirical CDF of MSE everywhere above HM CDF | Figure 6, p. 3112 | A=100 CDF (MSE) > HM CDF for all MSE thresholds in 40-year rolling windows; confirmed with kernel smoothing in Internet Appendix C.5 |
| R6 | Simulations confirm method's OOS $$R^2$$ distribution is entirely to the right of zero; OLS can be negative | Figure 3, p. 3105 | A=50 centered at ~4-5 (broadest), A=100 at ~3-4, A=200 at ~2, A=500 at ~1 (narrowest spike); OLS distribution spans $[-10, +10]$ with nontrivial probability of $$R^2 < 0$$ |
| R7 | Previously published confidence bounds (Campbell and Shiller 1988a) add value to OOS forecasts when used as the predictive slope | §5.4, p. 3112-3113 | A=209 (95% lower bound from Campbell and Shiller 1988a) produces positive OOS $$R^2$$ from 1987 onward; demonstrates prior study estimates are not data mining |

**Overall (paper's conclusion).** A conservative deterministic predictive slope, calibrated to a lower confidence bound near zero, provably dominates the historical average and empirically dominates OLS and Campbell-Thompson forecasts on most of the 23 standard predictors from Goyal and Welch (2008). The method is an ex ante validated benchmark for time-varying expected return models.

## Theory / model

The paper models the equity premium return as a linear predictive relationship (Equation 1, p. 3092):

$$
r = \mu + bx + e, \tag{1}
$$

where $$b$$ is the population predictive slope coefficient of the predictor $$x$$, $$e$$ is a residual with zero mean uncorrelated with $$x$$, $$x$$ has zero mean, and $$\mu$$ is the unconditional expected return. The historical average sets the slope on $$x$$ to zero. The unknown $$\mu$$ is estimated by the historical average $$\hat{\mu}$$:

$$
\mu = \hat{\mu} + \xi, \tag{2}
$$

where $$\xi$$ has zero mean. Substituting gives (Equation 3, p. 3093):

$$
r = \hat{\mu} + bx + \epsilon, \quad \epsilon \equiv e + \xi. \tag{3}
$$

The method's forecast for the next return is $$\hat{\mu} + \delta x$$ where $$\delta = 1/A$$ if $$b > 0$$ and $$\delta = -1/A$$ if $$b < 0$$ (Equation 5, p. 3093):

$$
\delta = \begin{cases} 1/A & \text{if } b > 0 \\ -1/A & \text{if } b < 0. \end{cases} \tag{5}
$$

**Theorem 1** (p. 3092): Under conditions that $$\delta$$ is a constant between 0 and $$b$$ and the pdf of the error vector $$\mathbf{e}$$ is strictly decreasing in $$\|\mathbf{e}\|$$, the forecast $$\mu + \delta x$$ first-order stochastically dominates the forecast $$\mu$$ (population mean) for predicting return $$r$$. That is, applying loss $$-\text{MSE}$$, the forecast $$\mu + \delta x$$ gives at least as high a probability of achieving any MSE threshold, and strictly higher probability for some.

**Theorem 2** (p. 3093): The forecast $$\hat{\mu} + \delta x$$ first-order stochastically dominates the historical average $$\hat{\mu}$$ under the same conditions on $$\delta$$ and the distribution of $$\boldsymbol{\epsilon} = e + \xi$$. Since $$\xi$$ can correlate with $$x$$ (Stambaugh 1999 bias), the monotonicity condition on the pdf of $$\boldsymbol{\epsilon}$$ is imposed (the $$t$$ and normal distributions satisfy this).

**Corollary 1** (p. 3093): Under Theorem 2's assumptions, the MSE using $$\hat{\mu} + \delta x$$ satisfies:

$$
\text{MSE}_{\hat{\mu}+\delta x} \overset{d}{=} \text{MSE}_{\hat{\mu}} - \eta, \quad \eta \geq 0. \tag{4}
$$

The MSE improvement $$\eta$$ is a nonnegative random variable, so the method has weakly lower MSE in expectation and first-order stochastically lower MSE.

**Theorem 3** (p. 3095) extends stochastic dominance to the case where the sign of $$b$$ is inferred with error (probability $$p$$ correct, $$q$$ wrong). For a given predictor realization $$\mathbf{x}$$, the forecast $$\mu + dx$$ (where $$d$$ is $$\delta$$, $$-\delta$$, or 0 according to the sign inference outcome) first-order stochastically dominates the historical average when $$p/q > \max(B_1, B_2)$$, where $$B_1 > (2b+\delta)/(2b-\delta)$$ (approximately 1 when $$\delta/b$$ is near zero, and 3 at the maximum $$\delta/b = 1$$). Statistical significance at the 95% level gives $$p/q \geq 0.95/0.05 = 19$$, well above the cutoff of 3.

**Theorem 4** (p. 3097) restates Theorem 3 for the estimated-mean setting where $$\mu$$ is replaced by $$\hat{\mu}$$, yielding Corollary 2 (p. 3098, Equation 9):

$$
\text{MSE}_{\hat{\mu}+dx} \overset{d}{=} \text{MSE}_{\hat{\mu}} - \eta, \quad \eta \geq 0. \tag{9}
$$

**OOS MSE decomposition.** The expected MSE difference between the historical average and the method is (Equation 10, p. 3098):

$$
E\!\left[\text{MSE}_{\hat{\mu}} - \text{MSE}_{\hat{\mu}+\hat{b}x}\right]
= \left(b^2 - \text{Bias}(\hat{b})^2 - \text{Variance}(\hat{b})\right)x^2 - 2E\!\left[(\hat{\mu}-\mu)\hat{b}\right]x. \tag{10}
$$

The historical average's slope is zero and therefore unbiased but uses no predictive information. A regression slope reduces the first two terms but can inflate the variance term to the point where it dominates, yielding a negative OOS $$R^2$$. The method uses a deterministic $$\delta$$, so the variance of $$\hat{b}$$ is zero and Equation (10) simplifies to $$(b^2 - \text{Bias}(\hat{b})^2)x^2 > 0$$ whenever $$\hat{b}$$ is between 0 and $$b$$. This is the core intuition: a constant nonzero slope beats both the historical average (zero slope, biased) and OLS (unbiased mean but high variance).

**Gradient descent interpretation.** The method is a one-step gradient descent update of the historical average toward greater predictability, using the sign (but not the magnitude) of $$b$$ as the gradient signal and step size $$1/A$$ (Equation 11, p. 3099):

$$
a_1 = a_0 - \gamma f'(a_0), \tag{11}
$$

where $$a_0 = 0$$ (the historical average slope), $$a_1 = \delta$$, and $$\gamma = 1/A$$.

## Method

The implementation has three steps.

**Step 1: Obtain the sign of $$b$$.** Sign can come from (a) economic theory, as in Campbell and Thompson (2008), who restrict the OLS slope to have the theoretically expected sign, or (b) statistical inference: use the confidence interval $$[\hat{b}_L, \hat{b}_U]$$ for population slope $$b$$. If $$0 < \hat{b}_L$$ the slope is significantly positive; if $$\hat{b}_U < 0$$ it is significantly negative. The method builds on `time-series-forecasting` (predictive regression) but replaces the OLS slope with a constant.

**Step 2: Choose A.** Setting $$1/A$$ to the lower confidence bound $$\hat{b}_L$$ ensures with near certainty that $$\delta$$ is between 0 and $$b$$ (Equation 7, p. 3093):

$$
0 < \hat{b}_L \leq b \quad \text{with 95\% probability.} \tag{7}
$$

For the dividend-to-price ratio, Campbell and Shiller (1988a) Table 4 give a predictive slope of 0.129 (SE = 0.057); the standardized predictor has a standard deviation of 0.277, so the 95% lower confidence bound for the standardized slope is $$(0.129 - 1.96 \times 0.057) \times 0.277 = 0.0048$$, implying $$A = 209$$ (p. 3094).

**Step 3: Standardize the predictor.** Predictors are standardized to zero mean and unit variance using a 20-year rolling backward-looking window, so $$\delta = 1/A$$ measures the effect of a one-standard-deviation change in the predictor on the forecast annual return (p. 3094, 3107).

**Simulation design.** A VAR(1) for log returns $$r$$, log dividend-to-price ratio $$dp$$, and log dividend growth $$\Delta d$$ following Cochrane (2008) provides the data-generating process (Equations 12-13, p. 3101). Parameters are calibrated to the sample (Table 1, p. 3102): population predictive slope $$b_r = 0.143$$, $$\rho = 0.8911$$. The historical average (HM) uses a rolling 20-year window. OOS $$R^2$$ is computed per Equation 14 (p. 3103):

$$
R^2 = \frac{\text{MSE}_{\hat{\mu}} - \text{MSE}_{\hat{\mu}+\delta x}}{\text{MSE}_{\hat{\mu}}}. \tag{14}
$$

## Empirical specifications

**Data.** Annual value-weighted CRSP market returns (post-1926) and S&P 500 Index returns (pre-1926), 23 predictors from Goyal and Welch (2008) extended through 2017 (Table 2, p. 3105): bm, cape Shiller, cay, corpr, csp, de, dfr, dfy, dp, dy, ep, eqis, ik, infl, ltr, lty, tbl, tms, ntis, svar, and four Robert Shiller series. Predictors are standardized using rolling 20-year windows. Forecasts start 20 years after the sample start year for each predictor.

**OOS $$R^2$$ evaluation (R1-R4, R7).** For each predictor, compute annual one-step-ahead OOS forecasts using the method with $$A \in \{50, 100, 200, 500, 1000\}$$, OLS, CT+, and CT++ (Campbell and Thompson 2008). Compute $$R^2$$ via Equation (14). Report one-sided p-values using Diebold (2015) heteroscedasticity-adjusted test, cross-checked by Harvey, Leybourne, and Newbold (1997). For dp, this corresponds to a sample of 146 annual observations.

**Stochastic dominance evaluation (R5).** Estimate the empirical CDF of OOS MSE over 40-year rolling windows of annual successive one-year-ahead forecasts using dp predictor (Figure 6, p. 3112). Compare the method CDF (A=100) to the historical mean CDF. First-order dominance requires the method CDF to lie everywhere above (to the left of) the HM CDF. Kernel smoothing (Internet Appendix C.5) confirms the finding.

**Bias-variance simulation (R6).** Generate 10,000 simulation samples of the VAR in Equations (12)-(13) with parameters from Table 1. In each sample compute the OOS $$R^2$$ using a rolling 20-year window for HM and a rolling 20-year window for $$\delta = 1/A$$ for the method. Figure 3 (p. 3105) reports the kernel density of the $$R^2$$ distribution across simulations for $$A \in \{50, 100, 200, 500\}$$ and OLS.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP value-weighted index return | Annual market return post-1926 | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| S&P 500 Index returns (Shiller website) | Annual market return pre-1926 | [Shiller data](/wiki/datasets/shiller-data/) |
| Goyal and Welch (2008) predictor data (Amit Goyal's website) | 19 predictor series for equity premium forecasting, extended to 2017 | No page yet |
| Robert Shiller data (http://www.econ.yale.edu/~shiller/data.htm) | 4 additional predictors: cape Shiller, infl Shiller, lty Shiller, Trcape Shiller | [Shiller data](/wiki/datasets/shiller-data/) |

Sample: 23 predictors with start years ranging from 1872 to 1947 (Table 2, p. 3105), all ending 2017. Forecasting starts 20 years after the predictor start year. Frequency: annual.

## When to read the full paper

Use the [original](https://doi.org/10.1093/rfs/hhaf010) if you are: (a) constructing a competing equity premium forecast and need the formal ex ante dominance proofs for a given distributon assumption; (b) selecting the parameter A for a specific predictor using the confidence-bound rule (Internet Appendix C.1 contains calculations for all 23 predictors); (c) investigating whether previously published coefficient estimates add OOS value (Section 5.4); or (d) comparing to shrinkage estimators such as Ridge and Lasso (Internet Appendix C.6). The key tables are Table 3 (OOS $$R^2$$ for dp) and Internet Appendix Table C.1 (all predictors); key figures are Figure 1 (cumulative OOS performance), Figure 3 (simulation $$R^2$$ density), and Figure 6 (stochastic dominance CDF).

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(10). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY-NC-ND 4.0 licence permits non-commercial reproduction with attribution and no derivatives; the verbatim PDF is not hosted here.

> Li, Kai, Yingying Li, Changlei Lyu, and Jialin Yu. "How to Dominate the Historical Average."
> *The Review of Financial Studies* 38, no. 10 (2025): 3086-3116.
> DOI: [10.1093/rfs/hhaf010](https://doi.org/10.1093/rfs/hhaf010).
> Replication code: Harvard Dataverse, https://doi.org/10.7910/DVN/9VNJUN.
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page is a distilled extract by the Institute for Automated Research.
