---
title: "In Too Deep: Guenzel (2025)"
description: >-
  Distilled: Quasi-random cost shocks in fixed-exchange-ratio stock mergers
  show that higher acquisition costs reduce subsequent divestiture rates by 8%
  to 9%, providing the first cleanly identified field evidence that sunk costs
  distort corporate investment decisions. J. Finance 2025, paywalled. Seven
  core results with source locators, the conceptual framework, the identification
  design, and the estimating equations.
sidebar:
  label: Guenzel 2025
  order: 1
tags: [paper-summary, behavioral-corporate-finance, mergers-acquisitions,
       divestitures, sunk-cost-effect, ceo-behavior, natural-experiment,
       survival-analysis, panel-regression, peer-reviewed, unreplicated,
       data:wrds, data:sdc-platinum, data:edgar]
paper:
  authors: Marius Guenzel
  authorList:
    - { family: Guenzel, given: Marius, affiliation: "University of Pennsylvania (Wharton School)" }
  year: 2025
  venue: "The Journal of Finance 80(3), June 2025, 1593–1646"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13430
  jel:
    codes: [G34, G41, D91]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Corporate Finance and Governance", "Financial Markets and Investment Strategies", "Auditing, Earnings Management, Governance"]
  dataAccess: hand-collected
  outcome:
    - corporate divestiture rate of previously acquired businesses
    - propensity to abandon an acquisition
  outcomeClass: [firm-real-outcomes]
  license: >-
    Paywalled (Wiley VOR; Crossref license block: content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0,
    start=2025-03-04; no CC licence detected; standard AFA/Wiley subscription access)
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/J. Finance; checked 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 5
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [survival-analysis, panel-regression, instrumental-variables, difference-in-differences]
    identification: natural-experiment
  contributionType: [new-fact, new-data]
  mechanisms: [behavioral-bias]
  introducesData: true
  scope:
    region: US
    assetClass: US corporate acquisitions and divestitures
    period: 1980-01..2018-12
    frequency: annual
    dataType: [market, accounting, administrative, other]
    granularity: [firm, transaction]
    n: "558 Fixed Shares acquisitions (279 divested), 4,461 firm-year observations in main sample"
  findings:
    - ref: R1
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Cox coefficient on delta-C = -0.065 (z=-2.77); interquartile cost increase reduces divestiture rate by 8%"
      direction: negative
      vsBenchmark: "acquirers facing higher quasi-random acquisition costs are 8% less likely to divest in any given year (Table III, col. 1)"
    - ref: R2
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Cox coefficient on delta-C = -0.068 (z=-2.89) with time-varying controls; interquartile effect ~8-9%"
      direction: negative
      vsBenchmark: "effect robust with 12-month return and industry distress controls (Table III, col. 2)"
    - ref: R3
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Placebo delta-C (post-completion window): coefficient ~0.010, z=0.33; coefficients insignificant across all five columns"
      direction: none
      vsBenchmark: "no effect when market fluctuations occur after deal completion rather than during transaction period (Table IV)"
    - ref: R4
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Within-divestiture sample (N=279): delta-C coefficient -0.070 to -0.065 (z=-2.29 to -2.50); interquartile effect 8.0-8.1%"
      direction: negative
      vsBenchmark: "sunk cost effect holds in divested-only sample, independent of case-control matching (Table V)"
    - ref: R5
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Unconstrained firms: delta-C coefficient -0.113 to -0.106 (z=-3.42 to -3.94); constrained firms: -0.047 to -0.046 (z=-1.45 to -1.37)"
      direction: negative
      vsBenchmark: "distortions ~13% for unconstrained vs ~6% for constrained acquirers; financial constraints dampen sunk cost effects (Table VII)"
    - ref: R6
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Acquiring CEO regime: delta-C coefficient -0.105 (z=-2.51); New CEO regime: -0.060 (z=-1.65, insignificant)"
      direction: negative
      vsBenchmark: "sunk cost effect driven by the CEO who made the acquisition; 30-50% lower after CEO turnover (Table VIII)"
    - ref: R7
      outcome: corporate divestiture rate of previously acquired businesses
      metric: coefficient
      value: "Diversifying acquisitions: delta-C coefficient -0.068 to -0.079 (z=-2.89 to -3.20); same-industry: -0.011 to -0.035 (z=-0.05 to -0.21)"
      direction: negative
      vsBenchmark: "sunk cost distortions concentrated in diversifying acquisitions (a proxy for inferior deal quality); no significant effect for same-industry deals (Table X)"
  resultType: new-finding
  relatesTo:
    - { cite: "Kaplan and Weisbach (1992)", relation: builds-on, note: "prior work on divestiture propensity following acquisitions; this paper adds sunk cost channel to explain timing" }
    - { cite: "Malmendier and Tate (2005)", relation: cites, note: "investment distortions from nonstandard managerial preferences (overconfidence); this paper adds sunk costs as a distinct behavioral friction" }
    - { cite: "Staw and Hoang (1995)", relation: extends, note: "escalation of commitment in NBA draft picks; this paper tests sunk cost effects in a high-stakes M&A corporate setting with cleaner identification" }
    - { cite: "Weisbach (1995)", relation: contradicts, note: "higher divestiture propensity after CEO replacement is typically attributed to general strategy shifts; this paper shows it reflects CEO-specific sunk cost effects via the acquiring CEO channel" }
    - { cite: "Cronqvist and Pely (2024)", relation: cites, note: "contemporaneous work concluding many divestitures are corrections of failure; complements the sunk cost delay documented here" }
    - { cite: "Kahneman and Tversky (1979)", relation: builds-on, note: "prospect theory microfoundation for sunk cost disutility under loss aversion and diminishing sensitivity" }
  openQuestions:
    - "Directly estimating the NPV paths and efficiency costs of sunk cost-induced delays requires detailed segment-level cash flow and divestiture transaction price data, which is largely unavailable; the paper can only provide suggestive evidence through counterfactual analysis (pp. 1632-1635, Section V.D)."
    - "Future research should cleanly identify sunk cost effects in other high-stakes investment settings (R&D, financial intermediation, VC) by exploiting analogous intensity-based identification designs (p. 1638, Section V.F)."
    - "Whether the documented CEO-specific sunk cost mechanism operates primarily through direct CEO behavioral biases or through CEOs responding to the sunk-cost thinking of external evaluators (board members, analysts) remains difficult to disentangle (pp. 1629-1632, Section V.C)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1593-1646, 54 pages); seven results extracted from Tables III-X; conceptual framework equations transcribed from pp. 1599-1601; estimating equations from pp. 1610-1612. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against source PDF (Tables III-X, pp. 1617-1633); all seven core result rows confirmed; R4 z-stat range corrected from -2.32 to -2.50 to the full PDF range -2.29 to -2.50 (Table V, five columns); equations (1), (1'), (2'), (3), (4) verified term-by-term; relatesTo edges have no doi fields; dataAccess and classification axes consistent with PDF." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13430", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-04; no CC licence; standard Wiley/AFA paywalled access" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the conceptual framework formalizing sunk cost effects on divestiture decisions, and the identification strategy: enough to know what it found and how, without reading all 54 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13430).

## TL;DR

This paper provides the first cleanly identified field evidence that sunk costs distort corporate investment decisions. In fixed-exchange-ratio (Fixed Shares) stock mergers, the final dollar acquisition cost is unknown at agreement signing. Aggregate market fluctuations between merger agreement and completion create plausibly exogenous variation in acquisition costs. Higher quasi-random acquisition costs strongly predict that acquiring firms hold on to the acquired business rather than divesting it: an interquartile cost increase reduces annual divestiture rates by 8% to 9%. Placebo tests using post-completion market fluctuations find no effect, supporting the sunk cost interpretation. The effect is concentrated in firm-years when the acquiring CEO (who personally incurred the cost) is still in office, and in financially unconstrained firms. Mechanism tests rule out learning, investment budget constraints, and CEO entrenchment as primary explanations; the evidence is most consistent with managerial behavioral frictions generated by sunk cost thinking.

## Core results

Magnitudes and significance are as reported; `\*\*`/`\*\*\*` = 5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Quasi-random acquisition cost increases reduce divestiture rates by ~8%**: the main sunk cost effect, robust to controls | Table III, col. (1), p. 1617 | Cox coefficient on delta-C = -0.065 (z=-2.77`\*\*\*`); interquartile cost increase (1.28 pp of market cap) reduces divestiture rate 8% |
| R2 | **Effect robust to time-varying controls** (acquirer prior-year return, industry distress indicator): coefficient barely changes | Table III, col. (2), p. 1617 | Coefficient -0.068 (z=-2.89`\*\*\*`); with time-varying interactions up to -0.077 (col. 4); interquartile effect 8-9.4% |
| R3 | **Placebo: post-completion market fluctuations do NOT predict divestiture rates**: only pre-completion (sunk) cost variation matters | Table IV (Panel A), p. 1621 | All five placebo coefficients between 0.009 and 0.011, z-stats 0.30-0.40, all insignificant |
| R4 | **Within-divestiture sample (divested-only) replicates**: sunk cost effect holds without case-control matching | Table V, p. 1622 | Coefficient -0.070 to -0.065 (z=-2.29 to -2.50`\*\*`); interquartile effect 8.0-8.1% |
| R5 | **Financial constraints dampen the effect**: distortions ~13% for unconstrained firms, ~6% for constrained | Table VII (Panel A), p. 1626 | Unconstrained: -0.113 to -0.106 (z=-3.42 to -3.94`\*\*\*`); Constrained: -0.047 to -0.046 (insignificant) |
| R6 | **Effect is CEO-specific**: concentrated in firm-years when the acquiring CEO is still at the helm; 30-50% lower once that CEO departs | Table VIII, col. (2), p. 1628 | Acquiring CEO: -0.105 (z=-2.51`\*\*`); New CEO: -0.060 (z=-1.65, insignificant); New CEO base effect +0.575`\*\*\*` |
| R7 | **Concentrated in diversifying acquisitions** (a proxy for inferior deal quality): no significant effect for same-industry deals | Table X, p. 1633 | Diversifying: -0.068 to -0.079 (z=-2.89 to -3.20`\*\*\*`); Same-industry: -0.011 to -0.035 (all insignificant) |

**Overall (paper's conclusion).** Quasi-random increases in acquisition costs cause firms to hold on to acquired businesses longer, consistent with managers taking sunk costs into account when deciding whether to divest. The mechanism appears to be an intrapersonal, CEO-specific behavioral friction: the effect disappears when the CEO who made the costly acquisition is replaced, extending the observation by Weisbach (1995) that divestitures are more likely after CEO changes (here shown to reflect a sunk cost channel rather than general strategy shifts). Financial constraints partially counteract the distortion, consistent with constraints limiting Malmendier and Tate (2005)-style behavioral investment distortions. Same-industry deals are unaffected, whereas diversifying acquisitions (a proxy for inferior deal quality flagged by Kaplan and Weisbach (1992)) concentrate the distortions. These patterns are most consistent with sunk costs generating psychological frictions in managerial decision making (Staw and Hoang (1995)), and are difficult to reconcile with CEO learning, investment budgets, or CEO entrenchment as the primary driver. Contemporaneous work by Cronqvist and Pely (2024) concludes that many divestitures are "corrections of failure," consistent with the efficiency costs of delay documented here.

## Theory / model

The paper has no structural model estimated by moments. It begins with a simple three-period reduced-form conceptual framework (Section I.A, pp. 1599-1601, Figure 1) that formalizes the prediction being tested.

**Setup.** At $$t=0$$, a manager buys an asset at total cost $$\bar{C} = C + \Delta C$$, where $$C$$ is known at the investment decision and $$\Delta C$$ is a mean-zero random variable realized between $$t=0$$ and $$t=1$$. At $$t=1$$, the manager decides to keep or divest the asset. The asset's market price (divestiture value) is $$P$$, the firm-specific interim cash flow (synergy) is $$X$$, and the long-run payoff if kept is $$Z$$. A divestiture yields $$P = Z$$ (competitive buyer market). The manager has potentially nonstandard preferences.

**Standard manager.** For $$\kappa = 0$$, the manager at $$t=1$$ solves:

$$
\max_{d_1 \in \{0,1\}} \; (1-d_1)(X + Z) + d_1 P \tag{Result 1, p. 1601}
$$

where $$d_1 = 1$$ denotes divestiture. The standard manager divests if and only if $$X + Z < P$$. With $$P = Z$$, this reduces to $$X < 0$$: the divestiture decision is independent of the realized cost shock $$\Delta C$$.

**Sunk cost manager.** For $$\kappa > 0$$, the manager incurs a disutility from divesting that is increasing in the total cost $$\bar{C}$$. The manager solves (p. 1600):

$$
\max_{d_1 \in \{0,1\}} \; (1-d_1)(X + Z) + d_1 \!\!\underbrace{\!\!\left(P - \kappa\bar{C}\right)}_{\text{net of sunk cost disutility}} \tag{Result 2, p. 1601}
$$

The sunk cost manager divests if and only if $$X < -\kappa(\bar{C}) = -\kappa(C + \Delta C)$$. A larger realized cost shock $$\Delta C$$ raises the threshold and makes divestiture less likely. This is the testable prediction: the probability of divestiture at $$t=1$$ is decreasing in $$\Delta C$$ for a sunk cost manager ($$\kappa > 0$$) and independent of $$\Delta C$$ for a standard manager ($$\kappa = 0$$).

The Internet Appendix extends the framework to a prospect-theory setting (Kahneman and Tversky (1979), Thaler (1980)) showing that diminishing sensitivity to losses generates the same prediction: a higher cost shock codes as a larger loss domain for the manager, making continued holding relatively more attractive.

## Method

The paper applies three estimators to a hand-collected dataset of Fixed Shares M&A deals.

**Cox (1972) proportional hazards model (main estimator).** The primary specification models the hazard of divestiture as (Section III.E, p. 1616, equation 4):

$$
h(t \mid \mathbf{X}_i) = h_0(t) \exp(\boldsymbol{\delta}' \mathbf{X}_i) \tag{4}
$$

where $$t$$ is survival time (years since acquisition), $$h_0(t)$$ is the unspecified baseline hazard, and $$\mathbf{X}_i$$ includes the main variable of interest $$\Delta C_i$$, deal- and firm-level controls, acquirer and target industry fixed effects, and acquisition year fixed effects. The model treats nondivested acquisitions as right-censored (censoring date: December 15, 2018, or acquirer takeover date). Time-varying covariates are accommodated by reshaping data into one-year-long sub-spells. Proportional hazards assumption is tested via Schoenfeld (1982) residuals; some control variables require time-interaction corrections.

**Logit and stratified hazard models.** Robustness to using a logit model instead of the hazard model (Efron (1988), Jenter and Kanaan (2015)), and to stratified Cox (1972) models. These produce qualitatively identical results (Internet Appendix, Section IV.A).

**Two-stage control function approach.** To address concerns about endogenous acquisition cost changes, the paper also implements a two-stage approach (Wooldridge (2015)): in the first stage, regress the actual cost change on the market-induced component and controls; in the second stage, include the residual from the first stage in the hazard model to control for endogeneity. Results are stable (Internet Appendix Table IA.VII).

This paper builds on `survival-analysis` (the Cox proportional hazards model) and `panel-regression` primitives, and uses a `natural-experiment` identification design: market fluctuations during the binding merger agreement period shift acquisition costs quasi-randomly across deals in the same year, analogous to `instrumental-variables` logic.

## Empirical specifications

**Acquisition cost change construction (pp. 1610-1611, equations 1 and 1').** The endogenous change in acquisition cost induced by the acquirer's own stock price movements is (equation 1):

$$
\Delta C_i^{Acq} = \Delta R_i^{Acq} \times \%\text{stock}_i \times \frac{\text{Deal Value}_i}{\text{Market Cap}_i^{Acq}} \tag{1}
$$

where $$\%\text{stock}_i \in (0,1]$$ is the fraction of merger consideration paid in stock, relative deal value is the deal value at agreement relative to the acquirer's pre-announcement market capitalization, and $$\Delta R_i^{Acq} = \sum_{t=\tau_1+2}^{\tau_2} R_{i,t}^{Acq}$$ is the cumulative daily acquirer return during the transaction period (merger agreement date $$\tau_1$$ to completion date $$\tau_2$$).

To isolate exogenous variation, the acquirer's daily return is replaced by the daily market return, adjusted for expected market appreciation and the acquirer's industry beta (equation 2'):

$$
\Delta R_i = \sum_{t=\tau_1+2}^{\tau_2} \hat{\beta}_{i,\tau_1}\!\left(R_t^{Mkt} - E_{\tau_1}\!\left[R_t^{Mkt}\right]\right) \tag{2'}
$$

The market-driven cost change used as the main variable of interest is then (equation 1'):

$$
\Delta C_i = \Delta R_i \times \%\text{stock}_i \times \frac{\text{Deal Value}_i}{\text{Market Cap}_i^{Acq}} \tag{1'}
$$

**Main estimating equation (p. 1611, equation 3):**

$$
\Pr(\text{Divestiture}_{i,t}) = \alpha + \kappa\,\Delta C_i + \boldsymbol{\delta}'\mathbf{X}_{i,t} + \nu_{j(\text{Acq})} + \nu_{j(\text{Tar})} + \mu_{t_0} + \varepsilon_{i,t} \tag{3}
$$

where $$i$$ denotes an acquisition, $$t$$ is years elapsed since acquisition, $$t_0$$ is the acquisition (calendar) year, $$\text{Divestiture}_{i,t}$$ is an indicator for the year of divestiture, $$\Delta C_i$$ is the market-induced cost change (equation 1'), $$\nu_{j(\text{Acq})}$$ and $$\nu_{j(\text{Tar})}$$ are acquirer and target industry fixed effects, and $$\mu_{t_0}$$ are acquisition year fixed effects. The null hypothesis (no sunk cost effects) is $$\kappa = 0$$. Standard errors are clustered by quarter of acquisition (treatment is assigned by market fluctuations between merger agreement and completion, which cluster within calendar quarters).

**Identifying variation.** Market fluctuations between merger agreement and completion shift acquisition costs across deals in the same year (same $$\mu_{t_0}$$) but in different calendar quarters: Table II confirms that the market return during the transaction period (i) strongly predicts firm returns (Panel A, F-statistic above 70), and (ii) is unpredictable from deal and firm characteristics (Panel B, joint F-statistic for 8 covariates = 0.56, p-value = 0.81). This validates the "as good as randomly assigned" assumption conditional on acquisition year.

**Key robustness tests.** Placebo using post-completion market fluctuations (Table IV, pp. 1621-1622): coefficients insignificant across all 10 specifications. Fixed Dollar placebo (Table VI, p. 1624): the hypothetical cost change for Fixed Dollar deals (which do not have exchange-ratio-induced cost variation) is insignificant while the actual Fixed Shares effect remains. Results are robust to financial constraint controls, alternative clustering, alternative time specifications, and gradual removal of high-withdrawal-probability observations.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| SDC Platinum M&A database | Starting universe of domestic acquisitions by US public acquirers 1980-2016; deal characteristics and divestiture flags | [SDC Platinum](/wiki/licensed/sdc-platinum/) (licensed) |
| Nexis (LexisNexis) news search | Divestiture identification: systematic search for newspaper articles and news wires for acquisitions not flagged by SDC | No page yet |
| SEC EDGAR filings (10-K, 10-Q, 8-K, S-4, Exhibit 21) | Hand-collected merger agreement terms (exchange ratio type, deal terms); divestiture verification | [SEC EDGAR](/wiki/datasets/edgar/) |
| CRSP monthly and daily returns | Acquirer stock returns during transaction period; acquirer market capitalization; beta estimation; control variables | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat | Acquirer financial characteristics; industry market-to-book; leverage; financial constraint construction | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Execucomp | CEO tenure and compensation data for ~50% of acquirers; CEO change dates | [WRDS / Execucomp](/wiki/licensed/wrds/) (licensed) |
| SEC filings, BoardEx, Bloomberg, Capital IQ, Who's Who | Hand-collected CEO education and biographical data for CEO sophistication tests | No page yet |

Sample: US public acquirers, acquisitions 1980-2016, divestitures tracked through December 2018. Main sample: 558 Fixed Shares acquisitions (279 divested), 4,461 firm-year observations.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13430) if you are: replicating the sunk cost hazard model (the Internet Appendix contains the full identification validity tests, Schoenfeld residual analysis, and the two-stage control function approach); designing an identification strategy for sunk cost effects in other investment contexts (R&D, VC, financial intermediation); studying CEO-level behavioral mechanisms in M&A decision making; or examining efficiency costs of delayed divestitures (Section V.D, counterfactual analysis). The locators above point to the exact tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled (Wiley/American Finance Association). Extract-only; no PDF hosted.

> Guenzel, Marius. "In Too Deep: The Effect of Sunk Costs on Corporate Investment."
> *The Journal of Finance* 80, no. 3 (June 2025): 1593-1646.
> DOI: [10.1111/jofi.13430](https://doi.org/10.1111/jofi.13430).
> © 2025 the American Finance Association.
> Distilled by the Institute for Automated Research (extract-only, not reproduced).
