---
title: "Lucky Survivor: Van Binsbergen, Hua, Peeters & Wachter (2025)"
description: >-
  Distilled: Using a cross-section of 55 countries from 1920 to 2020, the paper
  quantifies survivorship bias in U.S. equity market performance via a
  hierarchical Bayesian model that cross-learns crash risk across countries,
  finding that survivorship bias explains about one-third of the 6% historical
  U.S. equity premium, with luck and learning jointly accounting for roughly
  2 percentage points. J. Finance 2025, CC BY-NC-ND 4.0. Five core results
  with source locators, datasets used, the model (hierarchical Beta-Bernoulli
  crash-belief model), and the method (Hamiltonian Monte Carlo MCMC).
sidebar:
  label: Van Binsbergen-Hua-Peeters-Wachter 2025
  order: 1
tags: [paper-summary, asset-pricing, equity-premium, survivorship-bias, disaster-risk,
       bayesian, macro-finance, peer-reviewed, unreplicated,
       data:global-financial-data]
paper:
  authors: Jules van Binsbergen, Sophia Hua, Jonas Peeters, Jessica Wachter
  authorList:
    - { family: van Binsbergen, given: Jules, affiliation: University of Pennsylvania }
    - { family: Hua, given: Sophia V., orcid: "0000-0002-4505-151X", affiliation: University of Pennsylvania }
    - { family: Peeters, given: Jonas, affiliation: University of Pennsylvania }
    - { family: Wachter, given: Jessica A., orcid: "0000-0003-4162-7750", affiliation: University of Pennsylvania }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2355–2388
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13452
  jel:
    codes: [G12, G15, G17]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Monetary Policy and Economic Impact
    - Financial Risk and Volatility Modeling
    - Financial Markets and Investment Strategies
  dataAccess: licensed-commercial
  outcome:
    - subjective crash probability for each country over time
    - decomposition of the realized U.S. equity premium into expected return, luck, and learning
    - survivorship-bias-corrected equity risk premium
  outcomeClass: [security-returns, macro-aggregates]
  license: >-
    CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0,
    start 2025-04-16; corroborated by artifact p.2355 open-access notice)
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley OnlineLibrary, confirmed via Crossref 2026-06-05)"
  redistribution: extract-only (CC BY-NC-ND 4.0; no-derivatives clause prohibits adaptation mirroring)
  resultsCount: 5
  citedByCount: 2

  methods:
    role: both
    contributes: hierarchical-crash-belief-model
    family: structural
    buildsFrom: [hierarchical-bayesian-mcmc]
    identification: structural

  contributionType: [new-method, new-fact, measurement]

  mechanisms: [learning, disaster-risk-premium]

  scope:
    region: global
    assetClass: international equities
    period: 1920-01..2020-03
    frequency: annual
    dataType: [market]
    granularity: [aggregate]
    n: "55 countries, 1920-2020 (unbalanced panel)"

  findings:
    - ref: R1
      outcome: subjective crash probability for the United States
      metric: probability
      value: "6.54% posterior mean as of March 2020 vs. 5% in-sample frequency; shrinkage correction = 30.8%"
      direction: positive
      vsBenchmark: in-sample U.S. crash frequency of 5% (Figure 4, p. 2374)
    - ref: R2
      outcome: subjective crash probability for the United States vs. global average
      metric: probability
      value: "U.S. crash risk 6.54%; global average 9.16%; divergence = 2.62 percentage points as of March 2020"
      direction: negative
      vsBenchmark: global mean crash risk of 9.16% (Figure 5, p. 2376)
    - ref: R3
      outcome: decomposition of the realized U.S. equity premium into expected return, luck, and learning
      metric: return-spread
      value: >-
        "Uninformative prior: avg realized 9.40%, ex ante expected + residual 7.26%, luck 1.27%, learning 0.87%;
        Semi-informative: 9.70%, 7.42%, 1.21%, 1.08%;
        Informative: 9.11%, 7.34%, 0.96%, 0.81%"
      direction: positive
      vsBenchmark: ex ante expected return of ~7.3%-7.4% (Table IV, p. 2383)
    - ref: R4
      outcome: survivorship-bias-corrected equity risk premium
      metric: return-spread
      value: "Historical average equity premium overstated by approximately one-third; luck and learning jointly explain ~2% of the 6% measured premium"
      direction: positive
      vsBenchmark: raw historical U.S. equity premium of ~6% (pp. 2358, 2385)
    - ref: R5
      outcome: model-implied vs. realized rolling U.S. stock returns
      metric: correlation
      value: "Average correlation between model-implied realized returns and actual realized stock returns = 50% over 100-year period across 55 markets"
      direction: positive
      vsBenchmark: realized U.S. stock returns (Figure 7, p. 2384)

  resultType: new-finding

  relatesTo:
    - { cite: "Goetzmann and Jorion (1999)", doi: '10.1111/0022-1082.00133', relation: extends, note: "extends their finding that U.S. equity outperformance is an exception by quantifying the survivorship bias magnitude via a cross-sectional Bayesian model" }
    - { cite: "Barro (2006)", doi: '10.1162/qjec.121.3.823', relation: builds-on, note: "uses the rare-disaster asset pricing framework to map crash risk to the equity premium in the equilibrium section" }
    - { cite: "Wachter (2013)", doi: '10.1111/jofi.12018', relation: builds-on, note: "extends the time-varying disaster risk model to subjective Bayesian beliefs about disaster probability" }
    - { cite: "Mehra and Prescott (1985)", doi: '10.1016/0304-3932(85)90061-3', relation: tests, note: "tests the equity premium puzzle by showing that survivorship bias explains roughly one-third of the measured premium" }
    - { cite: "Jones and Shanken (2005)", doi: '10.1016/j.jfineco.2004.08.009', relation: extends, note: "applies their hierarchical learning-across-funds approach to cross-country crash risk estimation" }
    - { cite: "Lettau, Ludvigson, and Wachter (2008)", doi: '10.1093/rfs/hhm020', relation: builds-on, note: "uses their analysis of the declining equity premium as motivation for the asset pricing implications section" }

  openQuestions:
    - "Whether modeling time-varying crash risk is feasible given limited information and whether the correlated-crash extension fully addresses the independence assumption (Internet Appendix, p. 2360)."
    - "How to extend the framework to account for the magnitude (severity) of crashes, not just frequency, without losing analytical tractability (p. 2358)."
    - "The extent to which market segmentation in most of the 20th century limits the generalizability of cross-learning to a modern investor who CAN freely invest globally (p. 2370)."

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full text read (pp. 2355-2388 plus figures and tables); five results extracted from the CC-BY-NC-ND PDF. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; two fixes applied: (1) methods.buildsFrom corrected from [gmm] to [hierarchical-bayesian-mcmc] (paper uses HMC/MCMC throughout, no GMM); (2) eq. (8) Learning and Residual terms corrected: second valuation-ratio fraction changed from Z_{t+1}^D+1 to Z_t^D+1 in numerator (distiller had copied the same t+1 subscript twice, making each difference identically zero). All five Core result rows, Table IV magnitudes, Figure 4/5/7 locators, and all other equations verified correct against the PDF."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13452", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-04-16; note on p.2355 confirms this is an open access article under CC BY-NC-ND terms" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the hierarchical Bayesian model it proposes, and the HMC estimation method with defining equations: enough to know what it found and how, without reading all 34 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13452).

## TL;DR

The paper asks whether U.S. stock market outperformance is partly the result of survivorship bias: the U.S. happened to survive and thrive over the past century, and an early-1920 investor could not have known this would happen. Goetzmann and Jorion (1999) established that U.S. equity outperformance appears exceptional compared with other countries; this paper quantifies the bias by amount. Using a hierarchical Bayesian model fitted to annual total returns for 55 countries from 1920 to March 2020, the authors infer a subjective crash-belief series for each market by cross-learning from the full cross-section, applying the hierarchical-learning approach of Jones and Shanken (2005) to the cross-country setting. The U.S. crash probability, corrected for survivorship bias, is 6.54% at the end of the sample, versus its 5% in-sample frequency, and lies 2.6 percentage points below the global mean of 9.16%, a gap that widens persistently over the second half of the 20th century. The secular downward drift in perceived U.S. crash risk is attributed to positive return surprises (luck) and learning-induced valuation increases. Mapping crash risk to an Epstein-Zin equilibrium model using the rare-disaster framework of Barro (2006) as extended by Wachter (2013) to time-varying disaster risk, luck and learning jointly explain roughly 2 percentage points of the 6% historical equity premium as identified by Mehra and Prescott (1985), implying the premium has been overstated by about one-third. The declining equity premium is consistent with the trend documented by Lettau, Ludvigson, and Wachter (2008).

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | The hierarchical model raises the U.S. subjective crash risk above its in-sample frequency; the survivorship correction increases U.S. crash risk by 30.8% | Figure 4, p. 2374; §III.A | U.S. in-sample crash frequency = 5%; posterior mean at end of sample = 6.54%; adjustment = 1.54 pp (30.8%) |
| R2 | U.S. subjective crash risk diverges persistently and increasingly below the global average crash risk over the second half of the 20th century | Figure 5, p. 2376; §III.A | U.S. = 6.54%, global mean = 9.16% as of March 2020; gap = 2.62 pp; gap widens after ~1960 |
| R3 | The realized U.S. equity premium decomposes into ex ante expected return (~7.3%), luck (~1.0-1.3%), and learning (~0.9-1.1%), robust across all three prior specifications | Table IV, p. 2383; §IV.B | Average realized return 9.11-9.70%; expected + residual 7.26-7.42%; luck 0.96-1.27%; learning 0.81-1.08% |
| R4 | Survivorship bias (luck and learning jointly) explains about one-third of the measured U.S. equity premium, making the premium less of a puzzle | §V, p. 2385-2386 | ~2 pp of the measured ~6% equity premium attributable to luck + learning; true ex ante expected return ~4 pp |
| R5 | The model captures actual fluctuations in U.S. stock returns at business-cycle frequency; average cross-country correlation between model-implied and realized returns = 50% | Figure 7, p. 2384; §IV.B | 10-year rolling average of model-implied returns tracks realized U.S. returns well in levels; cross-country correlation = 50% |

**Overall (paper's conclusion).** Measuring the U.S. equity premium based on realized stock market returns leads to an overestimation of the ex ante expected return by approximately one-third. After correcting for survivorship bias via cross-learning from 55 international equity markets, the U.S. equity premium puzzle becomes substantially smaller. The secular decline in perceived U.S. crash risk implies a declining equity premium going forward, a slow-moving upward trend in valuation ratios, and reduced global diversification benefits as markets become more integrated.

## Theory / model

The paper sets up a hierarchical Bayesian framework in which a representative investor infers country-specific crash risk by cross-learning from the full cross-section of countries. Crash risk for country $$i$$ is modeled as a latent constant $$p_i$$, drawn from a common Beta distribution (Section I.A, p. 2361):

$$
p_i | \alpha, \beta \sim \text{Beta}(\alpha, \beta) \quad \forall i. \tag{Prior}
$$

Each period the investor observes crash realizations $$D_{i,t} \in \{0,1\}$$ (1 if annual return below -30%), which are i.i.d. across time and countries conditional on $$p_i$$:

$$
D_{i,t} | p_i \overset{\text{i.i.d.}}{\sim} \text{Bernoulli}(p_i). \tag{Likelihood}
$$

Let $$Y_{i,\tau} = [D_{i,1}, D_{i,2}, \ldots, D_{i,\tau}]$$ be the crash history of country $$i$$ up to time $$\tau$$. The joint posterior of all parameters follows Bayes rule (eq. 1, p. 2361):

$$
f(\{p_i\}_{i=1}^n, \alpha, \beta | \{D_{j,t}\}_{j=1,t=1}^{n,\tau}) \propto \prod_{i=1}^n p_i^{Y_{i,\tau} \mathbf{1}^\top + \alpha - 1}(1-p_i)^{\tau - Y_{i,\tau} \mathbf{1}^\top + \beta - 1} f(\alpha, \beta). \tag{1}
$$

Conditional on $$\alpha$$ and $$\beta$$, the country-specific crash probability has a conjugate Beta posterior (eq. 2, p. 2362):

$$
p_i | \alpha, \beta, \{D_{j,t}\}_{j=1,t=1}^{n,\tau} \sim \text{Beta}(Y_{i,\tau}\mathbf{1}^\top + \alpha, \; \tau - Y_{i,\tau}\mathbf{1}^\top + \beta) \quad \forall i. \tag{2}
$$

The posterior mean of $$p_i$$ (eq. 5, p. 2362) is a weighted average of the country's own crash frequency and the global mean $$\alpha/(\alpha+\beta)$$:

$$
\mathbb{E}(p_i | \alpha, \beta, \{D_{j,t}\}_{j=1,t=1}^{n,\tau}) = \frac{Y_{i,\tau}\mathbf{1}^\top}{\tau} \cdot \frac{\tau}{\tau + \alpha + \beta} + \frac{\alpha}{\alpha+\beta} \left(1 - \frac{\tau}{\tau+\alpha+\beta}\right). \tag{5}
$$

The effective sample size $$\alpha+\beta$$ controls the strength of the global shrinkage; for large $$\tau$$ the estimate converges to the country-specific frequency. The hyperpriors on $$\phi = \alpha/(\alpha+\beta)$$ (global mean crash risk) and $$\lambda = \alpha+\beta$$ (effective sample size) span three specifications: uninformative ($$\phi \sim \text{Uniform}[0,1]$$, $$\lambda \sim \text{Pareto}(1, 0.5)$$), semi-informative ($$\phi \sim \text{Uniform}[0, 0.35]$$, $$\lambda \sim \text{Pareto}(1, 2.5)$$), and informative ($$\phi \sim \text{Beta}(2,98)$$, $$\lambda \sim \text{Pareto}(1, 2.5)$$; mean crash risk 2%).

**Asset pricing.** In Section IV (pp. 2377-2384), the paper maps the declining crash belief into an equilibrium equity premium. Log consumption growth follows a random walk with drift $$\mu$$, standard deviation $$\sigma$$, and a Poisson jump $$v_{t+1}$$ that drops by $$b$$ upon a crash (with subjective probability $$p_t$$):

$$
\Delta c_{t+1} = \mu + \sigma \epsilon_{t+1} + v_{t+1}, \qquad v_{t+1} = \begin{cases} \log(1-b) & \text{w.p. } p_t \\ 0 & \text{w.p. } 1-p_t \end{cases}.
$$

The investor has Epstein-Zin utility with risk aversion $$\gamma$$, EIS $$\psi$$, and discount rate $$\delta$$. With CRRA ($$\gamma = 1/\psi$$), the equity premium increases in subjective disaster risk (eq. 7, p. 2378):

$$
\log \frac{\mathbb{E}_t(1 + R_{t+1})}{1+R_f} = \gamma\sigma^2 + b[(1-b)^{-\gamma} - 1]p_t. \tag{7}
$$

The realized excess return decomposes into ex ante expected return, luck, learning, and a residual (eq. 8, p. 2381):

$$
R_{t+1}^D - \mathbb{E}_t[R_{t+1}^D] = \underbrace{\mathbb{E}_t\left[\frac{D_{t+1}}{D_t}\right]\left(\frac{Z_{t+1}^D+1}{Z_t^D} - \frac{Z_t^D+1}{Z_t^D}\right)}_{\text{Learning}} + \underbrace{\frac{Z_t^D+1}{Z_t^D}\left(\frac{D_{t+1}}{D_t} - \mathbb{E}_t\left[\frac{D_{t+1}}{D_t}\right]\right)}_{\text{Luck}} + \underbrace{\left(\frac{Z_{t+1}^D+1}{Z_t^D} - \frac{Z_t^D+1}{Z_t^D}\right)\left(\frac{D_{t+1}}{D_t} - \mathbb{E}_t\left[\frac{D_{t+1}}{D_t}\right]\right)}_{\text{Residual}}. \tag{8}
$$

Parameters are calibrated at $$\gamma=3$$, $$\beta=0.98$$, $$\mu=0.0252$$, $$\sigma=0.02$$, $$\lambda=2.6$$, $$\psi=1$$, $$b=0.3$$.

## Method

The posterior is computed using Hamiltonian Monte Carlo (HMC), specifically the No-U-Turn Sampler of Hoffman and Gelman (2011) (Section II.B, p. 2373). The algorithm is initialized with four Markov chains at randomly selected starting values; each chain draws 10,000 samples with the first 2,000 as burn-in. Chains are pooled for the posterior distribution.

The model is estimated with an expanding window: starting from an initial period, the investor updates her beliefs each year as new data arrive across the cross-section. This replicates real-time belief formation and avoids look-ahead bias. The crash indicator for each country-year is defined as an annual return below -30% (Section II, p. 2373); robustness checks use -20% and -35% thresholds (Internet Appendix). Standard MCMC diagnostics compare within- and between-chain variation via the Gelman and Rubin (1992) potential scale reduction factor.

The hierarchical Beta-Bernoulli structure (`hierarchical-bayesian-mcmc`) provides a conjugate update: integrating out $$\alpha$$ and $$\beta$$ via equation (4) (p. 2362) yields the marginal posterior for country-specific crash risk, with cross-learning strength governed by $$\alpha + \beta$$. For long-history markets (such as the U.S. with 100 years), cross-learning is attenuated relative to short-history emerging markets (e.g., Estonia with 23 years), where the global prior exerts stronger influence.

## Empirical specifications

The key empirical exercise is computing the posterior distribution of crash beliefs for each of the 55 countries at each point in time, then mapping those to equity premium components. No standard panel regression with fixed effects is run; the model is entirely Bayesian.

**Cross-sectional comparison (R1, R2).** At the end of the sample (March 2020), the posterior mean $$\mathbb{E}[p_i | \{D_{j,t}\}]$$ is compared to the in-sample crash frequency $$p^c/N$$ for each country (Figure 4, p. 2374). For the United States: in-sample frequency = 5% (6 crashes out of 100 years), posterior mean = 6.54%, correction = 30.8%. For Turkey: posterior mean shrinks by roughly half relative to the in-sample frequency of 15.5%.

**Time-series evolution (R2).** Figure 5 (p. 2376) plots the U.S. posterior mean crash risk against the global average $$\alpha/(\alpha+\beta)$$ from 1921 to 2020. The U.S. crash belief starts near the global mean, departs upward during the Great Depression (1931-1937), then drifts steadily downward relative to the global average through the remainder of the century.

**Equity premium decomposition (R3, R4).** Using equation (8) with the calibrated Epstein-Zin model parameters, the paper computes the time-average of each component for the United States over 1931-2020. This is repeated for all three prior specifications; Table IV (p. 2383) reports the results. The decomposition is not identified econometrically but derived from the model: luck is the term involving realized minus expected dividend growth, learning is the valuation-ratio revision term.

**Model fit (R5).** Model-implied realized returns are compared to actual returns in the data (Figure 7, p. 2384). The correlation between model-implied and data-realized returns, averaged across all 55 countries, is 50% over the 100-year period.

**Robustness.** Results are repeated for all three hyperprior specifications (uninformative, semi-informative, informative); all converge to similar values after 10 years of data accumulate (Figure 2, p. 2366). The crash threshold is varied from -20% to -35% in the Internet Appendix with similar results.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Global Financial Data (GFD) | Annual stock total return indices (price level + monthly reinvested dividends) for 55 countries, 1920-2020; the main source for all return data | [no page yet](/wiki/datasets/) |
| CRSP (U.S.) | U.S. total return series (replaces GFD U.S. series with CRSP proxy for S&P 500 universe) | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Robert Shiller historical data | Used to calibrate the informative hyperprior: one crash in U.S. data 1870-1920 | no page yet |

Sample: 55 countries, unbalanced annual panel from 1920 to March 2020. Crashes defined as annual return below -30%. Several markets experience total loss episodes (nationalization, wartime closure) treated as -100% returns following Bialkowski and Ronn (2016).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13452) if you are: building a model of the equity premium that corrects for international survivorship bias; studying how Bayesian cross-country learning disciplines rare-event probability estimates; extending the hierarchical crash-risk model to time-varying crash probabilities or multi-period disasters; or evaluating the magnitude of the equity premium puzzle in a broad international sample. The Internet Appendix contains the correlated-crash extension (Section I), additional prior robustness (Section II), and full proofs.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. Licensed CC BY-NC-ND 4.0; non-commercial, no-derivatives; extract-only redistribution.

> van Binsbergen, Jules, Sophia Hua, Jonas Peeters, and Jessica Wachter.
> "Is the United States a Lucky Survivor? A Hierarchical Bayesian Approach."
> *The Journal of Finance* 80, no. 4 (August 2025): 2355-2388.
> DOI: 10.1111/jofi.13452. © 2025 The Author(s).
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page is a distillation by the Institute for Automated Research: LLM-extracted summary; extract-only; no PDF mirrored.
