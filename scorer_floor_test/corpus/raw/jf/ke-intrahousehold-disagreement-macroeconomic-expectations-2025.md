---
title: "Intrahousehold Disagreement about Macroeconomic Expectations: Ke (2025)"
description: >-
  Distilled: Using the Health and Retirement Study and a preregistered randomized
  survey experiment, Da Ke documents that five in six U.S. married couples
  disagree about macroeconomic expectations (inflation, recessions, stock returns),
  and that intrahousehold belief disagreement causally reduces household stock
  market participation on both the extensive and intensive margins. J. Finance 2025,
  CC BY 4.0. Eight core results with source locators, datasets used, the empirical
  model, and the experimental specifications.
sidebar:
  label: Ke 2025
  order: 1
tags: [paper-summary, household-finance, macroeconomic-expectations, beliefs,
       portfolio-choice, survey-experiment, panel-regression, open-access, cc-by,
       peer-reviewed, unreplicated, data:hrs]
paper:
  authors: Da Ke
  authorList:
    - { family: Ke, given: Da, orcid: "0009-0000-7663-3187", affiliation: University of South Carolina }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1647–1689
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13437
  jel:
    codes: [D14, G51, E71]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Monetary Policy and Economic Impact
    - Financial Markets and Investment Strategies
  dataAccess: public
  outcome:
    - household stock market participation (extensive margin)
    - household equity share (intensive margin)
    - intrahousehold belief disagreement about stock market returns
  outcomeClass: [household-finance, expectations]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-03-09; corroborated by artifact p.1647 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 4
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, fama-macbeth]
    identification: randomized
  contributionType: [new-fact, new-data]
  introducesData: true
  mechanisms: [behavioral-bias, participation-frictions]
  scope:
    region: US
    assetClass: household portfolios
    period: 1992-01..2023-12
    frequency: mixed
    dataType: [survey, experimental]
    granularity: [individual, aggregate]
    n: "HRS: 29,549 household-year observations (stock market sample, 2004-2018); experiment: 5,000 subjects (two waves, 2021 and 2023)"
  findings:
    - ref: R1
      outcome: intrahousehold belief disagreement about stock market returns
      metric: probability
      value: "5 in 6 couples (83-85%) disagree about future macroeconomic developments; 87-89% of pseudo couples disagree, so actual couples disagree only slightly less than randomly paired strangers"
      direction: positive
      vsBenchmark: actual couples vs. randomly matched pseudo couples (Figure 1, p. 1657)
    - ref: R2
      outcome: intrahousehold belief disagreement about stock market returns
      metric: r-squared
      value: "Household FE explain 36-44% of panel variation in intrahousehold belief difference; time FE explain less than 1%"
      direction: positive
      vsBenchmark: household FE vs. time FE (Table III, p. 1663)
    - ref: R3
      outcome: household stock market participation (extensive margin)
      metric: coefficient
      value: "Mean couple belief: 0.303*** (SE 0.016); husband's belief alone: 0.170*** (SE 0.012); wife's belief alone: 0.170*** (SE 0.012)"
      direction: positive
      vsBenchmark: mean-belief sensitivity 78% higher than husband's or wife's belief alone (Table V, p. 1667)
    - ref: R4
      outcome: household stock market participation (extensive margin)
      metric: coefficient
      value: "Level of disagreement: -0.054*** (SE 0.013); 1-SD increase reduces participation by 1.1pp (2.4%)"
      direction: negative
      vsBenchmark: "conditional on mean belief and controls (Table VI, p. 1668)"
    - ref: R5
      outcome: household equity share (intensive margin)
      metric: coefficient
      value: "Level of disagreement: -0.037*** (SE 0.009); 1-SD increase reduces equity share by 0.8pp (2.9%)"
      direction: negative
      vsBenchmark: "conditional on mean belief and controls (Table VI, p. 1668)"
    - ref: R6
      outcome: household stock market participation (extensive margin)
      metric: pp-effect
      value: "Spouse more pessimistic: -8.8pp*** (SE 1.6pp) vs. control; spouse more optimistic: +4.4pp*** (SE 1.5pp) vs. control (Table VIII, p. 1678)"
      direction: negative
      vsBenchmark: randomized experiment, 10pp spousal belief shock vs. control arm
    - ref: R7
      outcome: household stock market participation (extensive margin)
      metric: pp-effect
      value: "Gender asymmetry: women respond to optimistic husband (+5.4pp***) and pessimistic husband (-9.7pp***); men respond only to pessimistic wife (-6.3pp**)"
      direction: mixed
      vsBenchmark: "Table IX female vs. male columns, p. 1679"
    - ref: R8
      outcome: household stock market participation (extensive margin)
      metric: pp-effect
      value: "Spouse pessimism vs. stranger pessimism: additional -6pp decrease (significant at 10%); spouse optimism vs. stranger optimism: additional +2pp (insignificant)"
      direction: negative
      vsBenchmark: "spouse-specific pessimism effect above and beyond that of a stranger (Table XI, p. 1682)"
  resultType: new-finding
  relatesTo:
    - { cite: "D'Acunto, Malmendier & Weber (2021)", relation: extends, note: "complements their intrahousehold gender-gap finding on inflation expectations, and extends it to stock returns and recessions with causal evidence" }
    - { cite: "Giglio, Maggiori, Stroebel & Utkus (2021)", relation: builds-on, note: "stylized fact of low portfolio sensitivity to beliefs motivates the paper's focus on collective household belief measurement" }
    - { cite: "Ameriks, Kezdi, Lee & Shapiro (2020)", doi: '10.1080/07350015.2018.1549560', relation: builds-on, note: "attenuation-puzzle literature that informs why single-spouse beliefs understate sensitivity" }
    - { cite: "Garlappi, Giammarino & Lazrak (2017)", doi: '10.1016/j.jfineco.2017.06.005', relation: cites, note: "group disagreement and underinvestment in corporate setting, analogous channel" }
    - { cite: "Lian, Ma & Wang (2019)", doi: '10.1093/rfs/hhy111', relation: cites, note: "hypothetical portfolio allocation task design used in the experiment" }
  openQuestions:
    - "Whether extending the representative-agent macro-finance framework to allow for intrahousehold belief heterogeneity would materially change quantitative predictions of macro-finance models (Conclusion, p. 1684)."
    - "The mechanisms underlying the gender asymmetry in responsiveness to spousal beliefs remain only partially explained by information acquisition; other dimensions of the intrahousehold bargaining process are noted as a promising direction (pp. 1673-1679)."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1647-1689 plus appendix); eight results extracted from the CC-BY PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "All eight Core results rows checked against source PDF: locators (Figure 1 p.1657, Table III p.1663, Table V p.1667, Table VI p.1668, Table VIII p.1678, Table IX p.1679, Table XI p.1682) and magnitudes confirmed correct; equations (1)-(11) verified term-by-term; no errors found; pass." }
  licenceVerification:
    - source: "Crossref REST API works/10.1111/jofi.13437"
      checked: 2026-06-06
      by: "paper-distiller (claude-sonnet-4-6)"
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-03-09"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it tests (intrahousehold belief aggregation), and the empirical and experimental specifications: enough to know what it found and how, without reading all 43 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13437).

## TL;DR

Da Ke documents that five in six U.S. married couples hold divergent macroeconomic beliefs, and that this disagreement is persistent within households, largely unexplained by observable characteristics, and causally reduces household stock market investment. Using the Health and Retirement Study (HRS), Ke shows that the mean belief of both spouses predicts portfolio choice 76 to 83% better than either spouse's belief alone, and that the level of spousal disagreement independently depresses participation and equity share. A preregistered MTurk randomized survey experiment confirms the causal mechanism: exogenous pessimism from a spouse reduces stock market participation by 9 percentage points, while exogenous optimism raises it by 4 percentage points, with an asymmetry that is specific to the marital context rather than generic social influence.

## Core results

Magnitudes and significance are as reported; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Five in six couples disagree** about future macroeconomic developments across all three domains; disagreement is only slightly less than among randomly matched strangers | Figure 1 (p. 1657); text p. 1656 | 83-85% of couples disagree; pseudo couples disagree 87-89%; couples agree only 15-17% of the time |
| R2 | **Intrahousehold belief differences are persistent**: household fixed effects absorb 36-44% of the panel variation; time fixed effects less than 1% | Table III (p. 1663) | Household FE R2: inflation 44.0%, recessions 43.9%, stock returns 36.3%; time FE R2 all below 0.3% |
| R3 | **Mean couple belief predicts portfolios 76-83% better** than either spouse's belief alone | Table V (p. 1667) | Participation coefficient: mean belief 0.303\*\*\* vs. husband 0.170\*\*\* or wife 0.170\*\*\*; equity share: 0.243\*\*\* vs. 0.139\*\*\* or 0.133\*\*\* |
| R4 | **Disagreement reduces stock market participation**: 1-SD higher disagreement reduces participation by 1.1pp (2.4%) | Table VI col. 1 (p. 1668) | Coefficient: -0.054\*\*\* (SE 0.013), controlling for mean belief and demographics |
| R5 | **Disagreement reduces equity share**: 1-SD higher disagreement reduces equity share by 0.8pp (2.9%) | Table VI col. 2 (p. 1668) | Coefficient: -0.037\*\*\* (SE 0.009), controlling for mean belief and demographics |
| R6 | **Causal impact confirmed by experiment**: pessimistic spouse causes -8.8pp participation decline; optimistic spouse causes +4.4pp increase | Table VIII col. 1 (p. 1678) | Pessimistic spouse: -0.088\*\*\* (SE 0.016); optimistic spouse: +0.044\*\*\* (SE 0.015) vs. control arm (same belief) |
| R7 | **Gender asymmetry in responsiveness**: women respond symmetrically to pessimistic and optimistic husbands; men respond mainly to pessimistic wives | Table IX (p. 1679) | Women: optimistic husband +5.4pp\*\*\*, pessimistic husband -9.7pp\*\*\*; men: optimistic wife +3.1pp (insig.), pessimistic wife -6.3pp\*\* |
| R8 | **Marital-context specificity**: subjects are substantially more responsive to a spouse's pessimism than a stranger's; optimism effects are indistinguishable | Table XI (p. 1682) | Spouse vs. stranger pessimism differential: -6pp additional participation decline (significant at 10%); spouse vs. stranger optimism differential: +2pp (insignificant, p > 0.5) |

**Overall (paper's conclusion).** Accounting for interactions between household members would be a potentially important extension of the representative-agent framework in the macrofinance literature. Intrahousehold belief heterogeneity is substantial, persistent, and a genuine driver of portfolio under-investment, consistent with the analogy to group disagreement and underinvestment documented by Garlappi, Giammarino, and Lazrak (2017) in corporate settings. The paper builds on D'Acunto, Malmendier, and Weber (2021), who document a gender gap in inflation expectations within households; extends the stylized fact of low portfolio sensitivity to beliefs from Giglio, Maggiori, Stroebel, and Utkus (2021) and Ameriks, Kezdi, Lee, and Shapiro (2020); and uses the hypothetical portfolio allocation design of Lian, Ma, and Wang (2019).

## Theory / model

The paper has no formal structural model. It tests the following empirical hypotheses motivated by the household macrofinance literature:

**H1 (Belief heterogeneity).** If households consist of members with divergent beliefs, standard models that treat the household as a single agent with a representative belief will mischaracterize how beliefs map to portfolio choices.

**H2 (Mean belief sufficiency).** If the intrahousehold financial decision-making process is truly collective (not dictatorial), the couple's mean belief should predict portfolio outcomes better than either spouse's belief alone.

**H3 (Disagreement effect).** Holding mean belief fixed, a higher level of intrahousehold disagreement should independently reduce stock market participation and equity share, analogous to the group-disagreement underinvestment result of Garlappi, Giammarino, and Lazrak (2017).

**Variance decomposition.** To characterize the nature of the heterogeneity, the paper decomposes the overall cross-sectional variance of macroeconomic expectations into between- and within-household components (pp. 1661-1663). For household $$h$$ with members $$i \in h$$ and belief $$y_i$$ in wave $$t$$:

$$
\sigma^2_Y = \sigma^2_{\text{Between}} + \sigma^2_{\text{Within}} \tag{1}
$$

$$
\sigma^2_{\text{Between}} = \frac{1}{n}\sum_h n_h (\bar{y}_h - \bar{y})^2, \qquad \sigma^2_{\text{Within}} = \frac{1}{n}\sum_h\sum_{i \in h}(y_i - \bar{y}_h)^2 \tag{2-4}
$$

The within-household component accounts for 40-45% of the total cross-sectional variance in stock market expectations (Figure 2, p. 1662), and the result is almost identical after demeaning beliefs by gender, ruling out the gender gap as the sole driver.

To assess persistence, the paper estimates regressions of the intrahousehold belief difference $$y_{h,t}$$ on time fixed effects $$\chi_t$$, household fixed effects $$\phi_h$$, and their combination (pp. 1663):

$$
y_{h,t} = \chi_t + \varepsilon_{1,h,t} \tag{5}
$$

$$
y_{h,t} = \phi_h + \varepsilon_{2,h,t} \tag{6}
$$

$$
y_{h,t} = \phi_{3,h} + \chi_{3,t} + \varepsilon_{3,h,t} \tag{7}
$$

Table III (p. 1663) shows that household fixed effects absorb 36-44% of the panel variation across domains, while time fixed effects absorb less than 1%, confirming that disagreement is a persistent household-level characteristic.

## Method

The paper uses two complementary empirical approaches.

**Observational approach (HRS panel).** Ordinary least squares with household-clustered standard errors, region and survey-wave fixed effects, and a rich set of demographic and economic controls (equation 8, p. 1666):

$$
y_i = \alpha + \beta \cdot \text{Belief}_i + \gamma' \mathbf{X}_i + \varepsilon_i \tag{8}
$$

where $$y_i$$ is stock market participation or equity share for household $$i$$, $$\text{Belief}_i$$ is the husband's belief, the wife's belief, or the couple's mean belief, and $$\mathbf{X}_i$$ contains race, age, education, family income, homeownership, and household wealth. To test the disagreement effect, the specification is extended to (equation 9, p. 1668):

$$
y_i = \alpha + \beta_1 \cdot \text{Mean belief}_i + \beta_2 \cdot \text{Level of belief disagreement}_i + \gamma'\mathbf{X}_i + \varepsilon_i \tag{9}
$$

where level of belief disagreement is the absolute value of the spousal belief difference. Standard errors are clustered at the household level; Probit and Tobit robustness results are reported in the Internet Appendix.

**Experimental approach (MTurk RCT).** The paper uses a two-stage randomized survey experiment preregistered in the AEA RCT Registry (#0007897). Stage one elicits subjects' own one-year stock market return expectations and provides an information treatment (S&P 500 price chart and textual description of recent performance) to a random subsample. Stage two randomly assigns subjects to one of three arms: spouse more optimistic (+10pp vs. subject's belief), spouse more pessimistic (-10pp), or control (same belief). The portfolio allocation task asks subjects to divide $10,000 between a risk-free savings account and the S&P 500 for one year. The main regression is (equation 10, p. 1676):

$$
y_i = \alpha + \beta_1 E_i[R_{1y}] + \beta_2 \cdot \text{Spousemoreoptimistic}_i + \beta_3 \cdot \text{Spousemorepessimistic}_i + \gamma'\mathbf{X}_i + \varepsilon_i \tag{10}
$$

Heteroskedasticity-robust standard errors are reported. The second wave (2023, N=2,000) replaces the spouse's exogenous belief with that of a stranger for a random subsample, enabling the spouse-versus-stranger comparison in equation (11) (p. 1681):

$$
y_i = \alpha + \beta_1 \cdot \text{Spouse}_i + \beta_2 \cdot \text{More optimistic}_i + \beta_3 \cdot \text{More pessimistic}_i + \beta_4 \cdot \text{More optimistic}_i \times \text{Spouse}_i + \beta_5 \cdot \text{More pessimistic}_i \times \text{Spouse}_i + \eta \cdot E_i[R_{1y}] + \gamma'\mathbf{X}_i + \varepsilon_i \tag{11}
$$

where $$\beta_1 + \beta_5$$ captures the differential impact of a pessimistic spouse versus a pessimistic stranger.

## Empirical specifications

**Specification 1: Beliefs and portfolio choice (Table V, p. 1667).** OLS with stock market participation (indicator) or equity share as the dependent variable. Regressors: husband's belief only (col. 1/4), wife's belief only (col. 2/5), or couple mean belief (col. 3/6), plus the full control vector. N=29,549 household-year observations. Household-clustered SEs. The key comparison is whether the mean belief coefficient is more than additive relative to individual spouse coefficients.

**Specification 2: Disagreement and portfolio choice (Table VI, p. 1668).** OLS with participation or equity share as dependent variable. Regressors: level of belief disagreement (absolute spousal belief difference) and mean belief jointly, plus controls. N=29,549. Identifies the independent effect of disagreement holding the average level of optimism constant.

**Specification 3: Sources of intrahousehold disagreement (Table IV, p. 1665).** OLS regressing the belief difference between spouses on spousal differences and averages in age, education, income, cognition, self-efficacy, neuroticism, and information acquisition. N=19,655. Identifies correlates of disagreement (not causal).

**Specification 4: Causal impact of heterogeneity (Table VIII, p. 1678).** OLS (equation 10) on the main experimental sample (N=3,980), with wave fixed effects and controls from Table VII. The key coefficients $$\beta_2$$ and $$\beta_3$$ on the treatment indicators identify the causal impact of a 10pp spousal belief shock on household portfolio choice.

**Specification 5: Heterogeneous effects by gender (Table IX, p. 1679).** Equation 10 estimated separately for female (N=2,481) and male (N=1,499) subjects. Documents the gender asymmetry in responsiveness to spousal beliefs.

**Specification 6: Causal impact of information (Table X, p. 1680).** Adds interactions between the information treatment dummy and the treatment arm indicators, identifying whether information alters the weighting of spousal beliefs at the aggregation stage.

**Specification 7: Spouse versus stranger (Table XI, p. 1682).** Equation 11 on the second-wave subsample (N=2,000). The expressions $$\beta_1 + \beta_4$$ (optimistic spouse vs. optimistic stranger) and $$\beta_1 + \beta_5$$ (pessimistic spouse vs. pessimistic stranger) identify whether the causal effect is specific to the marital context.

**Specification 8: Experimental disagreement effect (Table XII, p. 1683).** Replicates the observational disagreement regressions (equation 9) on the experimental sample, replacing the treatment arm indicators with the mean belief and level of disagreement implied by the experimental assignment.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Health and Retirement Study (HRS) | Primary observational data source: biannual panel of married-couple households over age 50; macroeconomic expectations of both spouses (inflation 1992-2000, recessions 1992-2008, stock returns 2004-2018), portfolio outcomes (stock market participation, equity share), and individual demographic and cognitive characteristics | [HRS](/wiki/datasets/hrs/) |
| Amazon Mechanical Turk (MTurk) survey experiment | Randomized survey experiment; two waves (2021 N=3,000, 2023 N=2,000) of married U.S. residents age 25-64; exogenous variation in spousal beliefs about one-year stock market returns; hypothetical portfolio allocation task | no page yet |

Sample: HRS main sample 29,549 household-year observations (stock returns domain, 2004-2018); inflation sample 18,396 observations (1992-2000); recession sample 24,167 observations (1992-2008). Experiment: 5,000 total subjects across two waves.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13437) if you are: (i) studying collective household decision-making and belief aggregation (exact HRS variable construction in the Appendix, pp. 1684-1686); (ii) designing information experiments in household finance (the two-stage experimental design and preregistration details are in Section II and the Internet Appendix); (iii) extending macrofinance models to allow for intrahousehold heterogeneity (the paper's conclusion identifies this as the key unresolved question); (iv) examining the gender gap in macroeconomic expectations and how it differs from intrahousehold disagreement; or (v) replicating the robustness checks on measurement error, nonlinearity, risk aversion heterogeneity, and the placebo analysis on matched single individuals (Tables IA.III-IA.IX in the Internet Appendix).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Ke, Da. "Intrahousehold Disagreement about Macroeconomic Expectations."
> *The Journal of Finance* 80, no. 3 (June 2025): 1647–1689.
> DOI: 10.1111/jofi.13437. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
