---
title: "Pockets of Predictability (Replication): Cakici, Fieberg, Neumaier, Poddig & Zaremba (2025)"
description: >-
  Distilled: Cakici et al. replicate Farmer-Schmidt-Timmermann (2023) and find
  a critical one-sided vs two-sided kernel lookahead error in the original code;
  correcting it collapses average integral R-squared by roughly 20-fold and
  invalidates most FST conclusions about exploitable pockets of predictability.
  J. Finance 80(6), December 2025, CC BY 4.0. Eight core results with source
  locators, datasets used, and the identification strategy.
sidebar:
  label: Cakici et al. 2025 (Pockets Replication)
  order: 1
tags: [paper-summary, return-predictability, replication, market-timing, time-series, panel-regression, open-access, cc-by, peer-reviewed, data:wrds, data:ken-french]
paper:
  authors: Nusret Cakici, Christian Fieberg, Tobias Neumaier, Thorsten Poddig, Adam Zaremba
  authorList:
    - { family: Cakici, given: Nusret, affiliation: "Gabelli School of Business, Fordham University" }
    - { family: Fieberg, given: Christian, affiliation: "HSB Hochschule Bremen - City University of Applied Sciences, University of Luxembourg, and Concordia University" }
    - { family: Neumaier, given: Tobias, affiliation: "University of Bremen" }
    - { family: Poddig, given: Thorsten, affiliation: "University of Bremen" }
    - { family: Zaremba, given: Adam, affiliation: "MBS School of Business, Poznan University of Economics and Business, and Monash University" }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3771–3790
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13484
  license: 'CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-08-25; corroborated by artifact p.3771 Creative Commons Attribution License statement)'
  licenseShort: CC BY 4.0
  access: open
  machineAccess: 'blocked-paywall (Wiley site wrapper; not tested directly 2026-05-31; CC-BY VOR licence confirmed in publisher DOI metadata)'
  redistribution: 'extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)'
  resultsCount: 8
  citedByCount: 8
  jel:
    codes: [G12, G14, G17]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Monetary Policy and Economic Impact', 'Financial Risk and Volatility Modeling']
  dataAccess: licensed-commercial
  outcome:
    - aggregate stock market excess return
    - in-pocket vs out-of-pocket return predictability
    - market-timing alpha
  outcomeClass: [security-returns]

  # --- methodological identity ---
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [kernel-regression, time-series-forecasting]
    identification: descriptive
  contributionType: [replication, new-fact]
  # --- sample scope ---
  scope:
    region: US
    assetClass: US equities (aggregate market, CRSP)
    period: 1926-01..2016-12
    frequency: daily
    dataType: [market]
    granularity: [aggregate]
    n: "23,786 daily obs for dp (1926-2016); 23,727 for rvar (1927-2016); 15,860 for tbl (1954-2016); 13,846 for tsp (1962-2016) (Table I, p. 3777)"
  # --- the "what works" effectiveness axis ---
  findings:
    - ref: R1
      outcome: aggregate stock market excess return
      metric: r-squared
      value: "Mean integral R² (daily, two-sided): dp 1.51%, tbl 1.70%, tsp 2.92%, rvar 2.77%"
      direction: positive
      vsBenchmark: in-sample (two-sided kernel) reproduces FST; in-pocket vs out-of-pocket asymmetry large
    - ref: R2
      outcome: aggregate stock market excess return
      metric: r-squared
      value: "Mean integral R² (daily, one-sided): dp 0.18%, tbl 0.09%, tsp 0.09%, rvar 0.28%"
      direction: none
      vsBenchmark: ~20x collapse vs two-sided kernel (R1); in-pocket predictability effectively vanishes
    - ref: R3
      outcome: in-pocket vs out-of-pocket return predictability
      metric: t-stat
      value: "In-pocket CW (two-sided, unrestricted): dp 3.00***, tbl 4.75***, tsp 3.04***; In-pocket CW (one-sided, unrestricted): dp -0.47, tbl 0.10, tsp -1.06"
      direction: none
      vsBenchmark: strong in-pocket CW t-stats under two-sided code disappear entirely under one-sided correction
    - ref: R4
      outcome: market-timing alpha
      metric: sharpe-ratio
      value: "Average SR 0.71 (two-sided) vs 0.44 (one-sided); annualised alphas drop from 0.76-6.38% to -0.44-2.51%"
      direction: negative
      vsBenchmark: one-sided SR 0.44 falls below prevailing-mean benchmark (0.46)
    - ref: R5
      outcome: aggregate stock market excess return
      metric: t-stat
      value: "Out-of-pocket CW (two-sided, unrestricted): dp -1.62†, tbl -1.33†, tsp -1.52†, rvar -1.77††"
      direction: negative
      vsBenchmark: benchmark prevailing-mean beats kernel model out-of-pocket even under two-sided code
    - ref: R6
      outcome: in-pocket vs out-of-pocket return predictability
      metric: t-stat
      value: "All Panel B in-pocket CW entries insignificant across all bandwidth and window combinations (Table IV)"
      direction: none
      vsBenchmark: no configuration of the corrected code recovers in-pocket predictability vs prevailing mean
    - ref: R7
      outcome: aggregate stock market excess return
      metric: t-stat
      value: "Monthly in-pocket CW (one-sided, unrestricted): dp 0.90, tbl 1.22, tsp 0.57, rvar 1.01"
      direction: none
      vsBenchmark: monthly one-sided results match daily null; two-sided monthly in-pocket CW strong (tbl 3.55***, tsp 2.44**)
  resultType: overturns
  # --- finding-lineage edges ---
  relatesTo:
    - { cite: 'Farmer, Schmidt & Timmermann (2023)', relation: replicates, doi: 10.1111/jofi.13229, note: 'audits FST code; finds two-sided kernel in pocket-ID step introduces lookahead bias that accounts for all claimed predictability' }
    - { cite: 'Campbell & Thompson (2008)', doi: '10.1093/rfs/hhm055', relation: builds-on, note: 'economic restrictions on forecasts (non-negative return, sign-consistent coefficients) follow their framework' }
    - { cite: 'Clark & West (2007)', doi: '10.1016/j.jeconom.2006.05.023', relation: builds-on, note: 'primary statistical test for out-of-sample forecast comparison is the CW test' }
  # --- open questions from the paper ---
  openQuestions:
    - 'Whether the partial improvement from economic restrictions on forecasts (sign constraints on predicted returns and slope coefficients) reflects genuine predictability or a variance-reduction artefact from the constraint mechanics, rather than forecasting model quality (p. 3784, §II.B).'
    - 'Whether time-varying predictability in factor returns (SMB, HML) found in Internet Appendix Section IV survives a fully out-of-sample design, given the paper only reports Internet Appendix results qualitatively (pp. 3788-3789, §II.E).'
  # --- replication code ---
  replicationCode:
    url: https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.13484
    status: available
  # --- vocab to mint ---
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full text read (pp. 3771–3790, 20 pages); eight results extracted from the PDF. Not human-verified. Not reproduced. Replication code is published as Supporting Information on the journal website but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-01
      role: extracted
      note: >-
        Augment pass. Full PDF read (pp. 3771-3790) this session. Added methods,
        scope, relatesTo, openQuestions, replicationCode, proposedVocab frontmatter
        blocks, and the three formal body sections (Theory / model, Method, Empirical
        specifications) with equations transcribed from the PDF (eqs. 1-5, pp.
        3774-3775). Core results table and prior provenance preserved verbatim.
        New formal sections are extracted, not yet re-verified.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-01
      role: verified
      note: 'Full PDF re-read (pp. 3771-3790, all 20 pages); all 8 result rows, equations 1-5, and frontmatter re-checked. One fix: R2 tbl mean integral R² corrected from 0.12% to 0.09% (Table II Panel B, p. 3779). All other locators and magnitudes confirmed correct. Equations 1-5 verified term-by-term. No em-dashes or colorful adjectives found.'
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: Added classification axes (identification, contributionType, mechanisms, introducesData, data-scope) from a fresh PDF read; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: Classification axes (identification, contributionType, mechanisms, introducesData, data-scope) re-checked against the source PDF; one fix applied - scope.n corrected from approximate "~22,700" to exact per-series counts from Table I (dp 23,786, rvar 23,727, tbl 15,860, tsp 13,846); all other axes confirmed correct.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the results table and confirmed against the PDF;
        7 findings for 8 rows (R8 is qualitative-only, no reported magnitude, so
        it carries no finding); existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; one fix applied - R5 tbl out-of-pocket CW
        corrected from "insignificant" to -1.33† (Table III Panel A.1, p. 3781);
        all other entries and resultType confirmed correct.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13484
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-25'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, datasets, and identification
strategy: enough to know what it found without reading all 20 pages. To
replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13484) (open access).

## TL;DR

Farmer, Schmidt, and Timmermann (2023, FST) claimed that U.S. aggregate stock
market returns exhibit "pockets of predictability" identifiable ex ante via
one-sided kernel regressions. Cakici et al. audit the FST replication package
and find that the pocket-identification step in FST's code uses a two-sided
kernel, not the one-sided kernel described in the paper. A two-sided kernel
draws on data both before and after the forecast date, making the procedure
in-sample rather than out-of-sample and leaking future information into the
model. Correcting this single error reduces average integral R-squared by a
factor of roughly 20 (e.g., from 1.51-3.70% to 0.09-0.28% for daily
forecasts). The in-pocket vs out-of-pocket return predictability difference
largely disappears, and market-timing alphas become mostly insignificant.
Economic restrictions on forecasts offer partial improvement but cannot
restore the original conclusions.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Original (two-sided) code reproduces FST exactly**: in-pocket average integral R-squared ranges from 1.48% to 3.70% (daily), with strong in-pocket/out-of-pocket asymmetry | Table II Panel A, p. 3779; Figure 1 p. 3773 | Mean integral R² (daily): dp 1.51%, tbl 1.70%, tsp 2.92%, rvar 2.77% (two-sided kernel) |
| R2 | **Corrected (one-sided) code collapses predictability**: pockets become roughly 20x more frequent, 10x shorter, and far less predictable | Table II Panel B, p. 3779 | Mean integral R² (daily): dp 0.18%, tbl 0.09%, tsp 0.09%, rvar 0.28% (one-sided kernel) |
| R3 | **In-pocket CW t-statistics vanish with the one-sided kernel**: under the two-sided code in-pocket CW t-stats commonly exceed 3-4; under the corrected code they are insignificant for nearly all 27 model-predictor combinations | Table III Panel A.1 vs A.2, pp. 3781-3782 | Two-sided in-pocket CW (unrestricted): dp 3.00\*\*\*, tbl 4.75\*\*\*, tsp 3.04\*\*\*; one-sided in-pocket CW (unrestricted): dp -0.47, tbl 0.10, tsp -1.06 |
| R4 | **In-pocket alphas drop sharply**: unrestricted in-pocket annualised alphas fall from 0.76-6.38% (two-sided) to -0.44-2.51% (one-sided); only one out of nine individual/composite predictors exceeds 1% significance under the one-sided kernel | Table III Panel B.1 vs B.2, pp. 3782-3783 | Average Sharpe ratio drops from 0.71 (two-sided) to 0.44 (one-sided), below the prevailing-mean benchmark 0.46 |
| R5 | **Benchmark model beats kernel models out-of-pocket (two-sided code)**: out-of-pocket CW t-stats are significantly negative (at 10%) for most individual predictors under the original code | Table III Panel A.1, p. 3781 | Out-of-pocket CW: dp -1.62†, tbl -1.33†, tsp -1.52†, rvar -1.77†† (two-sided, unrestricted) |
| R6 | **Alternative bandwidth robustness: corrected code always fails to identify in-pocket predictability** across 2-, 2.5-, and 3-year estimation windows and 6-, 12-, 18-month SED windows; not a single significant in-pocket CW t-stat in Panel B | Table IV Panel B, pp. 3785-3786 | All Panel B in-pocket CW entries insignificant across all bandwidth/window combinations |
| R7 | **Monthly data confirms the result**: monthly in-pocket CW t-stats are strong under the two-sided kernel (e.g., tbl 3.55\*\*\*, tsp 2.44\*\*\*) but mostly insignificant under the one-sided kernel | Table V Panels A and B, p. 3788 | One-sided in-pocket monthly CW: dp 0.90, tbl 1.22, tsp 0.57, rvar 1.01 |
| R8 | **Partial exception: factor returns (SMB, HML) retain some time-varying predictability** even with the corrected one-sided kernel, though weaker than FST documented with the two-sided approach | §II.E, p. 3788-3789 (Internet Appendix Section IV) | Qualitative finding: significant CW stats and market-timing gains persist for factor portfolios; aggregate equity market is the null result |

**Overall (paper's conclusion).** The FST pocket-of-predictability evidence
is an artefact of in-sample kernel estimation. Once the identification step
is restricted to information available before the forecast date, the pockets
shrink to one-day artefacts, predictability inside and outside pockets
becomes statistically indistinguishable, and market-timing strategies based
on the pockets offer no reliable abnormal returns.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP U.S. stock market excess return (daily and monthly, 1926-2016) | Dependent variable: aggregate market excess return (CRSP return minus short T-bill) | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Dividend-price ratio (dp), 1926-2016 | Predictor variable (sourced from FST replication package) | no page yet |
| 3-month T-bill rate (tbl), 1954-2016 | Predictor variable (sourced from FST replication package) | no page yet |
| Term spread (tsp), 1962-2016 | Predictor variable (sourced from FST replication package) | no page yet |
| Realized variance (rvar), 1927-2016 | Predictor variable (sourced from FST replication package) | no page yet |
| Ken French Data Library (SMB, HML factor returns) | Used in Section II.E robustness for factor-level predictability | [Ken French](/wiki/datasets/ken-french/) |

Study period: 1926-2016 (predictor-dependent; see Table I, p. 3777). Data
sourced directly from the FST replication package ("Replication-code
20190881.zip", Journal of Finance website).

## Theory / model

This paper has no original structural economic model. It is a methodological
audit and replication of Farmer, Schmidt, and Timmermann (2023, FST). The
theoretical object under scrutiny is the claim that aggregate equity market
return predictability is time-varying and can be identified ex ante using
one-sided kernel regressions. The testable hypothesis is:

- **Null**: market-timing strategies built on FST's "pockets" offer no reliable
  abnormal returns once a correctly out-of-sample pocket-identification kernel
  is used.
- **Identification**: the two-framework comparison is the entire identification
  strategy. Every FST analysis is run twice with all other parameters held
  fixed; only the kernel type in the second estimation stage differs. Any
  difference in results is attributed to the kernel type (one-sided vs
  two-sided), since that is the sole deviation from the FST code.

**The FST return prediction model** (eq. 1, p. 3774):

$$
r_{t+1} = x_t' \beta_t + \epsilon_{t+1} \tag{1}
$$

- $$r_{t+1}$$ is the excess U.S. stock market return
- $$x_t$$ is a vector of predictor variables (dp, tbl, tsp, rvar)
- $$\beta_t$$ are time-varying regression coefficients
- $$\sigma_t^2 = E[\epsilon_{t+1}^2 \mid x_t]$$ allows for conditional heteroskedasticity

The $$\beta_t$$ are estimated by the local constant model (eq. 2, p. 3774):

$$
\hat{\beta}_t = \operatorname*{arg\,min}_{\beta_0} \sum_{s=1}^{T} K_{hT}(s-t) \cdot [r_{s+1} - x_s' \beta_0]^2 \tag{2}
$$

with kernel weights $$K_{hT}(u) = K(u/hT)/(hT)$$ and bandwidth $$h$$. FST use a
2.5-year bandwidth in this step with a one-sided Epanechnikov kernel (eq. 3,
p. 3775):

$$
K(u) = \tfrac{3}{2}(1 - u^2) \cdot \mathbf{1}\{-1 < u < 0\} \tag{3}
$$

Only data from before time $$t$$ receives positive weight under the one-sided
kernel, making the $$\beta_t$$ estimation genuinely out-of-sample. The discrepancy
arises in the second stage.

## Method

The method builds on `kernel-regression` for both the return-prediction
estimation and the pocket-identification step, and on `time-series-forecasting`
for evaluating out-of-sample performance against the prevailing-mean benchmark.
The paper applies these techniques, it does not propose a new one.

**Squared error differential (SED)** (eq. 4, p. 3775) measures whether the
kernel model outperforms the prevailing-mean benchmark at each date $$t$$:

$$
\text{SED}_t = (r_t - \bar{r}_{t|t-1})^2 - (r_t - \hat{r}_{t|t-1})^2 \tag{4}
$$

- $$\bar{r}_{t|t-1}$$ is the prevailing-mean forecast
- $$\hat{r}_{t|t-1}$$ is the kernel model forecast
- Positive $$\text{SED}_t$$ means the kernel model has smaller forecast error that period

**Pocket identification** (eq. 5, p. 3775): a pocket begins when the fitted
SED trend is positive:

$$
\widehat{\text{SED}}_t = \gamma_{0,t} + \gamma_{1,t} \cdot t > 0 \tag{5}
$$

- $$\gamma_{0,t}$$ and $$\gamma_{1,t}$$ should be estimated with a one-sided Epanechnikov kernel and one-year bandwidth
- FST's published code instead uses a two-sided kernel with a 24-month symmetric window (12 months before and 12 months after day $$t$$), so the identification draws on data that is unavailable at forecast time

**Two-framework comparison design**: the paper runs the complete FST analysis
twice, in parallel, changing only this kernel choice. Panel A results use the
original (two-sided) code; Panel B results use the corrected (one-sided) code.
All other parameters, bandwidth choices, predictor series, and performance
metrics are identical. This clean design means the contrast of Panel A vs
Panel B isolates the kernel-type effect.

**Performance metrics** (§II.B, pp. 3780-3783):
- Clark-West (2007) t-statistic comparing kernel-model forecasts to the
  prevailing-mean benchmark
- Annualised alpha from a stock/T-bill timing strategy (holding stocks when the
  kernel model predicts positive returns, T-bills otherwise), with Newey-West
  (1987) t-statistics
- Annualised Sharpe ratio of the timing strategy
- Three forecast restriction variants following Campbell and Thompson (2008):
  unrestricted, non-negative excess return forecasts only, and sign restrictions
  on both forecasts and slope coefficients

## Empirical specifications

All regressions use daily U.S. excess stock market returns as the dependent
variable unless noted (monthly robustness in Table V). The sample varies by
predictor (Table I, p. 3777): dp starts November 5, 1926; tbl starts January
4, 1954; tsp starts January 2, 1962; rvar starts January 15, 1927; all end
December 2016.

**Constant-coefficient replication regressions (Table I, p. 3777).**
Univariate OLS of daily excess return on each lagged predictor, separately
for full sample, in-pocket, and out-of-pocket subsamples. Slope coefficients
and Newey-West (1987) adjusted t-statistics and R-squared reported. The pocket
partition is the only thing that differs between Panel A and Panel B in this
table; the regression itself is identical.

**Pocket statistics (Table II, p. 3779).**
For each predictor and kernel type, counts the number of pockets, their
fraction of sample, duration (min/mean/max days), and integral R-squared
(min/mean/max). Integral R-squared $$IR^2$$ is computed as in FST (p. 1289):
the average within-pocket R-squared, weighting by pocket length. Results
reported separately for daily and monthly data.

**Clark-West prediction performance (Table III, pp. 3781-3782).**
CW t-statistic comparing kernel model to the prevailing-mean benchmark
$$\bar{r}_{t+1} = (1/t)\sum_{s=1}^{t} r_s$$. Reported separately for:
- full sample, in-pocket subperiod, out-of-pocket subperiod
- Panel A.1 (in-sample / two-sided kernel), Panel A.2 (one-sided kernel)
- nine predictor/composite specifications (dp, tbl, tsp, rvar, pc, mv,
  comb1, comb2, comb3)
- three forecast restriction variants
Significance under one-tailed test (positive direction) for alphas; two-tailed
for CW tests.

**Economic significance (Table III Panel B, pp. 3782-3783).**
Annualised alpha, Newey-West t-statistic, and Sharpe ratio of the asset
allocation strategy (stocks when forecast is positive, T-bills otherwise).
Reported for the same nine predictor/composite specifications and three
restriction variants, separately for the two kernel approaches.

**Bandwidth robustness (Table IV, pp. 3785-3786).**
CW t-statistics for coefficient estimation windows of 2-, 2.5-, 3-year and
SED estimation windows of 6-month, 12-month, 15-month. Panel A uses the
two-sided kernel; Panel B uses the corrected one-sided kernel. Nine predictor
and composite specifications, daily data.

**Monthly data robustness (Table V, p. 3788).**
Reproduces Table III (Panel A and Panel B) using monthly returns, following
FST Table VII Panel A. Estimation period is 2.5 years for monthly forecasts.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13484) (open access) if you
are: auditing the FST replication package directly; extending the
kernel-regression methodology to other predictors or markets; or assessing
whether the partial improvements from economic restrictions (sign constraints
on slope coefficients and forecasts) restore the FST conclusions. The
locators above point to the exact tables. For "what did this paper find,"
the table above is sufficient.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025,
pp. 3771-3790. This distillation was extracted by an LLM on 2026-05-31 and
is **not human-verified or independently reproduced**. The article is open
access under CC BY 4.0; PDF mirroring is permitted by the licence but the
PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Cakici, Nusret, Christian Fieberg, Tobias
> Neumaier, Thorsten Poddig, and Adam Zaremba. "Pockets of Predictability:
> A Replication." *The Journal of Finance* 80, no. 6 (December 2025):
> 3771-3790. DOI: 10.1111/jofi.13484. © 2025 The Author(s). Licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
