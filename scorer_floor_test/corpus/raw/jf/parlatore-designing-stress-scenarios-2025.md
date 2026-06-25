---
title: "Designing Stress Scenarios: Parlatore & Philippon (2025)"
description: >-
  Distilled: Parlatore and Philippon model the optimal design of bank stress
  test scenarios as an information-acquisition problem, solving it via a
  Kalman filter. Capital requirements cover losses under an adverse scenario
  while targeted interventions depend on covariances among residual exposures;
  calibration shows information is far more valuable for targeted interventions
  than for broad capital requirements. J. Finance 2025, paywalled. Five core
  results with source locators, the model, and the method.
sidebar:
  label: Parlatore-Philippon 2025
  order: 1
tags: [paper-summary, banking, stress-testing, financial-regulation, prudential-regulation,
       information-acquisition, theory, peer-reviewed, unreplicated]
paper:
  authors: Cecilia Parlatore, Thomas Philippon
  authorList:
    - { family: Parlatore, given: Cecilia, orcid: "0009-0008-1656-1263", affiliation: New York University, Stern School of Business }
    - { family: Philippon, given: Thomas, affiliation: New York University, Stern School of Business }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 833-873
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13422
  jel:
    codes: [G21, G28, D82]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Banking stability, regulation, efficiency
    - Economic theories and models
  dataAccess: public
  outcome:
    - optimal stress test scenario design
    - welfare gain from stress testing
    - optimal capital requirements
    - optimal targeted interventions
  outcomeClass: [bank-funding, credit-risk]
  license: "Wiley VOR licence (http://onlinelibrary.wiley.com/termsAndConditions#vor, content-version vor, delay-in-days 0, start 2025-01-24); paywalled, not CC"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 5
  citedByCount: 6
  methods:
    role: both
    contributes: optimal-stress-scenario-design
    family: theory
    buildsFrom: [principal-agent]
    identification: structural
  contributionType: [new-theory]
  mechanisms: [information-asymmetry, moral-hazard]
  scope:
    region: US
    assetClass: bank loans (credit losses)
    period: 1991-01..2013-12
    frequency: quarterly
    dataType: [administrative, accounting]
    granularity: [aggregate, firm]
    n: "1 representative bank (aggregate US banking system); DFAST panel of banks 1991-2013"
  findings:
    - ref: R1
      outcome: optimal capital requirements
      metric: coefficient
      value: "Optimal capital requirements are linear in expected losses under distress: W-bar* = sum_i E[y_i | Distress, S] + W-tilde - (kappa - p*theta)/(p*gamma) (Lemma 2, p. 848)"
      direction: positive
    - ref: R2
      outcome: welfare gain from stress testing
      metric: pp-effect
      value: "Welfare gain from learning under pure capital requirements is ~20 bps (stress test distinguishing adverse from severely adverse scenario); this is significant but not large relative to a 10% capital cost reduction (Figure 4, p. 861)"
      direction: positive
      vsBenchmark: "4-5x smaller than welfare gain under targeted interventions at same uncertainty level"
    - ref: R3
      outcome: welfare gain from stress testing
      metric: pp-effect
      value: "Welfare gains from stress testing with targeted interventions are 4 to 5 times larger than under pure capital requirements; interventions can achieve welfare gains of the same order of magnitude as a 10% decrease in bank capital costs (Figure 4, p. 861-862)"
      direction: positive
      vsBenchmark: "4-5x larger than pure capital requirements case"
    - ref: R4
      outcome: optimal stress test scenario design
      metric: coefficient
      value: "Optimal scenario weight on factor j is hump-shaped in the regulator's prior mean: weight is increasing in expected exposure at low values (intervention more likely and information more valuable) then decreasing at high values (posterior remains high regardless of test results, reducing learning) (Section IV.C.1, p. 855, Figure 2 Panel A)"
      direction: mixed
    - ref: R5
      outcome: optimal stress test scenario design
      metric: coefficient
      value: "Optimal scenario places higher weight on factors with correlated exposures across banks; if cross-bank correlation is high enough, the regulator stresses only the correlated factor (Section IV.C.2, p. 856, Figure 2 Panel B)"
      direction: positive
      vsBenchmark: "correlated factors receive outsized scenario weight vs uncorrelated factors"
  resultType: new-finding
  relatesTo:
    - { cite: "Orlov, Zryumov & Skrzypacz (2023)", doi: '10.1093/rfs/hhad040', relation: builds-on, note: "model's predictions are consistent with their result that optimal sequential capital requirements involve precautionary recapitalization followed by contingent recapitalization on stress test results (p. 849)" }
    - { cite: "Faria-e-Castro, Martinez & Philippon (2017)", relation: builds-on, note: "fiscal backstop reduces lemon-market costs, allows more informative stress tests; Parlatore and Philippon model the design stage rather than disclosure (p. 834)" }
    - { cite: "Goldstein & Leitner (2018)", doi: '10.1016/j.jet.2018.05.013', relation: cites, note: "risk-sharing trade-off when disclosing stress test results: revealing too much destroys sharing opportunities (p. 836)" }
    - { cite: "Van Nieuwerburgh & Veldkamp (2010)", doi: '10.1111/j.1467-937x.2009.00583.x', relation: builds-on, note: "information acquisition framework: cost of acquiring information pins down feasible precisions and whether signals are complements or substitutes (p. 837)" }
    - { cite: "Shapiro & Skeie (2015)", doi: '10.1093/rfs/hhv010', relation: cites, note: "reputation concerns of regulator with moral hazard and bank runs (p. 834)" }
  openQuestions:
    - "The model focuses on aggregate credit risk captured by two macro factors (GDP growth and real estate prices); accounting for trading and derivative losses as well as interest rate risk might increase the welfare gains from stress testing and highlight additional factors (p. 862)."
    - "The welfare function assumes simple aggregation of capital across banks (sum of net worths), which limits the role of heterogeneity and may understate contagion effects in the case of bank runs (p. 862)."
    - "The number and cost of additional stress test scenarios as a function of institutional details (insurance portfolios vs bank credit books) is left for future applied work (p. 852)."
  replicationCode:
    status: available
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-06, role: extracted, note: "Full text read (pp. 833-874); five core results extracted from the PDF. Not human-verified. Not reproduced. Replication code is referenced in the paper (Supporting Information) but has not been run here." }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; two fixes applied: (1) asymptotic variance of GDP coefficient corrected from 0.0038 to 0.0037 (PDF Appendix D p.871: 0.00370976); (2) methods.buildsFrom corrected from [bayesian-persuasion, gmm] to [principal-agent] (paper uses Kalman filter + linear-quadratic regulator, no GMM used, and bayesian-persuasion describes cited literature not the paper's own method). All five core result rows verified against PDF (eqs. 20, 22, 25, 28, Figure 4 p.861-862, Figure 2 panels A/B p.855-856); all theory equations (eqs. 2, 3, 5, 9, 10-11, 12, 15, 20, 22, 23, 25, 28) checked term-by-term against PDF; calibration parameters confirmed against Table II (p.857) and Appendix D (p.871); no em-dashes or colorful adjectives found; all relatesTo cites locatable in body." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13422", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-24; paywalled Wiley VOR, not CC" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model (a Kalman filter learning problem with linear-quadratic regulator preferences), and the method it contributes (optimal stress scenario design as information acquisition) with defining equations: enough to know what it found and how, without reading all 42 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13422).

## TL;DR

Parlatore and Philippon develop the first formal theory of how a financial regulator should design stress test scenarios. They model stress testing as a two-stage process: a risk-discovery stage (the regulator learns banks' hidden exposures from reported losses under hypothetical scenarios) and a risk-mitigation stage (the regulator chooses capital requirements or targeted interventions). By mapping the scenario-design problem into a Kalman filter information-acquisition problem, they derive optimal scenarios and show that their design depends critically on what the regulator plans to do with the information. Information from stress tests is only modestly valuable for setting broad capital requirements (worth about 20 bps of welfare gain), but is four to five times more valuable when the regulator can make targeted interventions such as loan-to-value limits or supervisory matters requiring attention. The paper also calibrates the model to U.S. bank data (DFAST 2015, 1991-2013 quarterly NCO rates) and finds that optimal scenarios focus on factors with correlated exposures across banks and have a hump-shaped dependence on prior mean exposures.

## Core results

Magnitudes and significance as reported; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%. Locators point to the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Optimal capital requirements are linear in expected losses under distress and set to cover the adverse scenario | Lemma 2, eq. (20), p. 848 | $$\overline{W}^* = \sum_i \mathbb{E}[y_i \mid \text{Distress}, \mathcal{S}] + \tilde{W} - \frac{\kappa - p\theta}{p\gamma}$$; requirements increase in risk aversion and estimated exposures |
| R2 | Welfare gain from learning under pure capital requirements is modest: ~20 bps, significantly below the gain from a 10% reduction in capital costs | Figure 4, p. 861 | Stress tests distinguishing adverse from severely adverse scenario raise welfare about 20 bps; this is less than one-quarter of the gain from a 10% lower capital cost |
| R3 | Welfare gains from stress testing with targeted interventions are 4-5x larger than under pure capital requirements | Figure 4, p. 861-862 | At high prior uncertainty, targeted interventions raise welfare gains to the same order of magnitude as a 10% decrease in the cost of bank capital; robust across calibrations |
| R4 | Optimal scenario weight on a factor is hump-shaped in the regulator's prior mean exposure | Section IV.C.1, p. 855; Figure 2 Panel A | Weight increases in expected exposure at low values (intervention more likely and information more valuable) but decreases at high values (posterior anchored to prior, reducing learning value) |
| R5 | Optimal scenario stresses factors with correlated exposures across banks more; if correlation is high enough, only the correlated factor is stressed | Section IV.C.2, p. 856; Figure 2 Panel B | Cross-bank correlated factors are more systemic and receive outsized scenario weight; specialization may be complete when correlation is sufficiently high |

**Overall (paper's conclusion).** Stress tests are best understood as an information tool whose value depends on what the regulator plans to do. When limited to setting broad capital requirements, scenarios should match the plausible adverse state and scenario design matters little for learning. When targeted interventions are available, optimal scenarios deviate from the average bad state to elicit information about specific exposures, and their design can generate welfare gains comparable to a significant reduction in the cost of bank capital. This is consistent with the sequential recapitalization characterization of Orlov, Zryumov, and Skrzypacz (2023).

## Theory / model

The model builds on the information-acquisition framework of Van Nieuwerburgh and Veldkamp (2010), the disclosure literature of Goldstein and Leitner (2018), and the stress-test design context studied by Faria-e-Castro, Martinez, and Philippon (2017) and Shapiro and Skeie (2015). It has three stages: scenario design, stress testing, and intervention. There are $$N$$ banks indexed by $$i \in \{1,\dots,N\}$$, each exposed to $$J$$ macroeconomic risk factors gathered in the $$J \times 1$$ state vector $$\mathbf{s}$$ with $$\mathbb{E}[\mathbf{s}] = 0$$ (p. 838). Bank $$i$$'s cumulative losses in state $$\mathbf{s}$$ are (eq. 2, p. 838):

$$
y_i(\mathbf{s}) = \sum_{j=1}^{J} x_{i,j} s_j, \tag{2}
$$

where $$x_{i,j}$$ is bank $$i$$'s unobserved exposure to factor $$j$$. Exposures are stacked in the $$NJ \times 1$$ vector $$\mathbf{x}$$. The aggregate banking system capital is (eq. 3, p. 839):

$$
W(\mathbf{s}) \equiv \sum_{i=1}^{N} w_i(\mathbf{s}) = \overline{W} - \sum_{i=1}^{N} y_i(\mathbf{s}). \tag{3}
$$

The regulator has prior beliefs $$\mathbf{x} \sim \mathcal{N}(\overline{\mathbf{x}}, \Sigma_x)$$ over the $$NJ \times 1$$ vector of exposures (p. 840). A stress scenario $$\hat{\mathbf{s}} = (\hat{s}_1,\dots,\hat{s}_J)'$$ is a realization of the state vector (Definition 1, p. 840). A stress test is a collection of $$M$$ scenarios $$\{\hat{\mathbf{s}}^m\}_{m=1}^M$$ and reported losses $$\{\hat{y}_i^m\}$$ (Definition 2, p. 841). Bank $$i$$'s estimated loss under scenario $$\hat{\mathbf{s}}^m$$ is (eq. 5, p. 841):

$$
\hat{y}_i(\hat{\mathbf{s}}^m, M) = \hat{\mathbf{s}}^m \cdot \mathbf{x}_i + \hat{\varepsilon}_{i,m}(\|\hat{\mathbf{s}}\|, M), \tag{5}
$$

where $$\hat{\varepsilon}_i$$ captures measurement error whose variance increases in scenario severity $$\|\hat{\mathbf{s}}\|$$. In state-space form (eq. 9, p. 844):

$$
\hat{\mathbf{y}} = \hat{\mathbf{S}} \mathbf{x} + \hat{\boldsymbol{\varepsilon}}, \tag{9}
$$

where $$\hat{\mathbf{S}} \equiv (\mathbf{I}_N \otimes \hat{S})$$ stacks the scenario matrix across banks.

The regulator has pseudo mean-variance (linear-quadratic) preferences over aggregate banking system wealth $$W$$. With probability $$p$$ the economy lands in a distress region around $$\tilde{W}$$, and the regulator uses a second-order approximation of marginal utility (eq. 15, p. 847):

$$
U'(W) = \begin{cases} 1 & \text{with probability } 1-p \\ 1 + \theta - \gamma(W - \tilde{W}) & \text{with probability } p, \end{cases} \tag{15}
$$

where $$\theta \equiv U'(\tilde{W}) - 1 > 0$$ and $$\gamma \equiv -U''(\tilde{W}) > 0$$. The regulator designs $$\hat{S}$$ to maximize ex-ante expected utility given that she will choose optimal actions $$(\overline{W}, \mathbf{a})$$ after observing stress test results (eq. 8, p. 843):

$$
\mathbb{E}_{\mathcal{S}}\left[\mathbb{E}\!\left[U\!\left(W\!\left(\mathbf{s},\mathbf{x};\mathbf{a}^*(\mathcal{S}),\overline{W}^*(\mathcal{S})\right)\right)\!\Big|\mathcal{S}\right] - \mathcal{C}(\mathbf{a}^*(\mathcal{S})) - \mathcal{K}\!\left(\overline{W}^*(\mathcal{S})\right)\right]. \tag{8}
$$

## Method

**Learning via the Kalman filter.** The model's key analytical insight is that stress test results $$\hat{\mathbf{y}}$$ are signals about latent exposures $$\mathbf{x}$$ in the linear Gaussian system (eq. 9). By Lemma 1 (p. 844), the posterior beliefs are:

$$
\mathbf{x} \mid \hat{\mathbf{y}} \sim \mathcal{N}(\hat{\mathbf{x}}, \hat{\Sigma}_{\mathbf{x}}), \tag{Lemma 1}
$$

with posterior mean $$\hat{\mathbf{x}}$$ and posterior covariance $$\hat{\Sigma}_{\mathbf{x}}$$ given by (eqs. 10-11, p. 844):

$$
\hat{\mathbf{x}} = \left(\mathbf{I}_{NJ} - K\hat{\mathbf{S}}\right)\overline{\mathbf{x}} + K\hat{\mathbf{y}} \quad \text{and} \quad \hat{\Sigma}_{\mathbf{x}} = \Sigma_x - K\hat{\mathbf{S}}\Sigma_x, \tag{10-11}
$$

where the $$NJ \times MN$$ Kalman gain matrix is $$K = \Sigma_x \hat{\mathbf{S}}' \left(\hat{\mathbf{S}}\Sigma_x\hat{\mathbf{S}}' + \Sigma_\varepsilon\right)^{-1}$$. The expected learning is $$\Sigma_{\hat{x}} \equiv \Sigma_x - \hat{\Sigma}_x = K\hat{\mathbf{S}}\Sigma_x$$ (eq. 12, p. 845).

**Optimal interventions.** Under Assumption L (linear costs: $$\mathcal{K}(\overline{W}) = (1+\kappa)\overline{W}$$ and $$\mathcal{C}(\mathbf{a}) = \Phi'\mathbf{a}$$), optimal capital requirements are given by Lemma 2 (eq. 20, p. 848):

$$
\overline{W}^* = \sum_{i=1}^{N} \mathbb{E}[y_i \mid \text{Distress}, \mathcal{S}] + \tilde{W} - \frac{\kappa - p\theta}{p\gamma}. \tag{20}
$$

Optimal targeted interventions are given by (eq. 22, p. 850):

$$
\mathbf{a}^* = (p\gamma\tilde{\mathbb{V}})^{-1}\!\left(\kappa(\mathbf{1}_{N\times 1} \otimes \tilde{\mathbf{s}}) \circ \hat{\mathbf{x}} - \Phi + p\gamma\tilde{\mathbb{V}}\mathbf{1}_{NJ\times 1}\right), \tag{22}
$$

where $$\tilde{\mathbb{V}} \equiv \mathbb{C}\mathbb{O}\mathbb{V}[(\mathbf{1}_N \otimes \mathbf{s}) \circ \mathbf{x} \mid \mathcal{S}, \mathcal{D}=1]$$ is the distress uncertainty matrix (eq. 23, p. 850). The distress uncertainty matrix $$\tilde{\mathbb{V}}$$ decomposes into two terms: uncertainty about the macro state under distress interacted with expected exposures, and residual uncertainty about bank exposures from the Kalman filter.

**Optimal scenario design.** The scenario design problem for pure capital requirements reduces to (Lemma 3, eq. 25, p. 852):

$$
\min_{\hat{\Sigma}_{\mathbf{x}} \in \Sigma} \mathbf{1}_{1\times NJ} \mathbb{E}[\tilde{\mathbb{V}}] \mathbf{1}_{NJ\times 1}, \tag{25}
$$

that is, the regulator minimizes residual uncertainty, choosing the posterior covariance matrix $$\hat{\Sigma}_{\mathbf{x}}$$ in the feasible set $$\Sigma$$ implied by the Kalman filter. With targeted interventions, by Lemma 4, the design problem is (eq. 28, p. 853):

$$
\min_{\hat{\Sigma}_{\mathbf{x}} \in \Sigma} \mathbb{E}_{\hat{\mathbf{x}}}\!\left[\kappa\overline{W}^* + \Phi'\mathbf{a}^*\right], \tag{28}
$$

which trades off capital costs against the cost of targeted actions, weighted by intervention responsiveness to new information.

## Empirical specifications

The paper's quantitative results come from calibration of the model to U.S. bank-level and macroeconomic data, not from panel regressions. The calibration targets moments from the 2015 Dodd-Frank Act Stress Test (DFAST) and quarterly bank NCO rates from 1991 to 2013 (Table I, p. 856; Table II, p. 857; Appendix D, p. 870-871).

**Step 1: Identifying macro risk factors.** Following Hirtle et al. (2014), the authors regress aggregate banking system NCO rates on standard macroeconomic variables (GDP growth, short-term and long-term interest rates, unemployment, housing prices, equity prices, and credit spreads) over 1991-2013 at the quarterly frequency. GDP growth and a real estate price index (equal-weighted average of residential and commercial) explain more than 80% of the variation in NCO rates. The two risk factors are standardized to have mean zero and unit variance (Table D.1, p. 871).

**Step 2: Calibrating exposure priors.** The regressor coefficients are approximately $$-0.357$$ (GDP) and $$-0.303$$ (real estate). The asymptotic variances of the coefficient estimates ($$0.0037$$ and $$0.0035$$ respectively) are used to calibrate the regulator's prior uncertainty. Prior mean exposures are set to $$\bar{x}_1 = \bar{x}_2 = 0.015$$ and prior standard deviation $$\Sigma_x^{1/2} = \text{diag}(0.006, 0.006)$$.

**Step 3: Calibrating preferences.** The adverse scenario corresponds to $$\tilde{W} = 10\%$$ of RWA and $$\overline{W}^* = 13\%$$. Distress probability $$p = 0.1$$, marginal cost of capital $$\kappa = 0.3$$ (matching shadow-cost estimates of Kisin and Manela (2016)), marginal value of capital in distress $$\theta = 3$$, and risk-aversion curvature $$\gamma = 100$$.

**Step 4: Calibrating measurement error.** The standard deviation of bank model errors $$\sigma_\varepsilon = \alpha + \beta\|\mathbf{s}\|^2$$ is estimated by regressing the CLASS model's cross-sectional forecasting errors against the squared norm of macro factors, giving $$\alpha = 0.55\%$$, $$\beta = 0.11\%$$.

**Welfare comparisons (Figure 4, p. 861).** The authors solve four problems: (1) two scenarios freely chosen optimally, (2) one scenario fixed at the adverse state, one chosen optimally, (3) one fixed at adverse, two chosen optimally, and (4) two freely chosen optimally with targeted interventions. Welfare gains are normalized by the gain from a 10% reduction in the cost of bank capital ($$\kappa' = 0.9\kappa$$). Problems 1-3 yield welfare gains less than one-quarter of this benchmark; Problem 4 yields gains of the same order of magnitude.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| DFAST (Dodd-Frank Act Stress Test) 2015 summary statistics | Calibration targets: Tier 1 capital ratio (ex-ante 13.5%, adverse 10.4%, severely adverse 8.4%), Tier 1 leverage, loan loss rate (Table I, p. 856) | No page yet |
| Quarterly aggregate U.S. bank NCO rates (1991-2013) | Identifying macro risk factors and calibrating exposure priors; regression of NCO rate on GDP growth, real estate prices (Appendix D, p. 870-871) | No page yet |
| Capital Loss Assessment under Stress Scenarios (CLASS) model, Hirtle et al. (2014) | Bank-level panel regressions to calibrate regulator priors and measurement error (Table D.1, p. 871) | No page yet |

Sample: quarterly, 1991 Q1 to 2013 Q4 for the macro calibration; one representative bank (aggregate U.S. banking system) plus DFAST cross-section.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13422) if you are: designing stress test frameworks and want the formal characterization of optimal scenario choice (Section IV, pp. 851-856); interested in the calibration details and the four welfare comparison problems (Section V, pp. 856-862); extending the model to multiple banks, trading losses, interest rate risk, or contagion; or reading the proofs of Lemmas 1-4 in Appendices A-C (pp. 863-867).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pp. 833-873. DOI: 10.1111/jofi.13422. Published under the Wiley VOR licence (paywalled, not CC). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract-only: the verbatim PDF is not hosted here.

> Parlatore, Cecilia, and Thomas Philippon. "Designing Stress Scenarios."
> *The Journal of Finance* 80, no. 2 (April 2025): 833-873.
> DOI: 10.1111/jofi.13422. © 2025 the American Finance Association.
