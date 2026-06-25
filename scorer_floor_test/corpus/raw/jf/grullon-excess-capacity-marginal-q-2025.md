---
title: "Excess Capacity, Marginal q, and Corporate Investment: Grullon & Ikenberry (2025)"
description: >-
  Distilled: When managers anticipate excess capacity, average q becomes a biased
  proxy for marginal q; augmenting Tobin's q model with asset utilization (sales
  scaled by total capital including intangibles) substantially improves explanatory
  power in time-series and cross-sectional investment regressions, eliminates the
  paradoxical negative q-investment relation, and explains why investment rates have
  declined for decades despite rising average q. J. Finance 2025, paywalled. Eight
  core results with source locators, the theoretical model, and the estimating
  specifications.
sidebar:
  label: Grullon-Ikenberry 2025
  order: 1
tags: [paper-summary, corporate-investment, tobin-q, excess-capacity, intangible-capital,
       panel-regression, fama-macbeth, peer-reviewed, unreplicated,
       data:wrds, data:fred]
paper:
  authors: Gustavo Grullon, David L. Ikenberry
  authorList:
    - { family: Grullon, given: Gustavo, affiliation: Rice University (Jones Graduate School of Business) }
    - { family: Ikenberry, given: David L., affiliation: University of Colorado (Leeds School of Business) }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1533-1592
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13439
  jel:
    codes: [G31, E22, G32]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Corporate Finance and Governance', 'Financial Reporting and Valuation Research', 'Auditing, Earnings Management, Governance']
  dataAccess: licensed-commercial
  outcome:
    - corporate investment rate (itot)
    - explanatory power of Tobin's q investment regression (R-squared)
    - out-of-sample investment forecast error (MSE)
    - long-run change in investment rates across industries
  outcomeClass: [firm-real-outcomes]
  license: "Wiley VOR terms and conditions (not CC); confirmed via Crossref DOI metadata: content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0, start 2025-03-11"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 2
  methods:
    role: both
    family: structural
    buildsFrom: [panel-regression, fama-macbeth, real-options]
    identification: descriptive
  contributionType: [new-theory, new-fact, measurement]
  mechanisms: [excess-capacity-wedge]
  scope:
    region: US (primary); G7 international robustness
    assetClass: US non-financial equities
    period: 1974-01..2021-12
    frequency: annual
    dataType: [accounting, market, survey]
    granularity: [aggregate, industry, firm]
    n: "140,655 firm-years (firm-level panel); 48 Fama-French industries (industry panel); 1974-2021 aggregate time-series"
  findings:
    - ref: R1
      outcome: corporate investment rate (itot)
      metric: coefficient
      value: "ln(qtot) coeff = -0.35 (t = -2.82) in traditional model; flips to +0.21 (t = 6.31) with CurrAU control (Table I Panel A, Table III Panel A)"
      direction: negative
      vsBenchmark: "traditional q model gives paradoxical negative slope; augmented model restores positive slope"
    - ref: R2
      outcome: explanatory power of Tobin's q investment regression (R-squared)
      metric: r-squared
      value: "Time-series R2 rises from 0.29 (traditional) to 0.95-0.98 (augmented with asset utilization proxies) (Table III Panel A)"
      direction: positive
      vsBenchmark: "augmented model R2 roughly 3x the traditional model R2"
    - ref: R3
      outcome: corporate investment rate (itot)
      metric: r-squared
      value: "Firm-level panel R2 rises from 0.28 to 0.35-0.45 when adding asset utilization (Table VI Panel A)"
      direction: positive
      vsBenchmark: "consistent with aggregate findings; asset utilization uniformly positive and significant across all deciles and subperiods"
    - ref: R4
      outcome: corporate investment rate (itot)
      metric: r-squared
      value: "No structural break found post-1996 after controlling for excess capacity; augmented model works equally well pre- and post-1996 (Table III Panels B-C)"
      direction: none
      vsBenchmark: "contradicts Andrei, Mann, and Moyen (2019) structural break finding; break disappears once excess capacity controlled"
    - ref: R5
      outcome: out-of-sample investment forecast error (MSE)
      metric: r-squared
      value: "Augmented model MSE = 0.0098%, 89% lower than traditional q model MSE of 0.0881%; traditional q model barely beats naive model (Figure 8)"
      direction: positive
      vsBenchmark: "augmented model MSE 89% below traditional q model; traditional q MSE similar to naive 20-year average forecast"
    - ref: R6
      outcome: long-run change in investment rates across industries
      metric: coefficient
      value: "Cross-section: ln(CurrAU) coeff = 0.83 (t = 5.80) on long-run investment change; ln(qtot) becomes insignificant at -0.10 (t = -0.85) once AU included (Table IX)"
      direction: positive
      vsBenchmark: "asset utilization fully absorbs the paradoxical negative q-investment relation in the cross-section"
    - ref: R7
      outcome: corporate investment rate (itot)
      metric: coefficient
      value: "Asset utilization elasticity positive and significant in all 10 Fama-French industries (Table IV); positive across all 10 size deciles in augmented model (Table VII Panels B-D)"
      direction: positive
      vsBenchmark: "largest improvement in largest-firm deciles; asset utilization coeff = 0.55-1.27 across deciles, inconsistent with financial constraints hypothesis"
    - ref: R8
      outcome: corporate investment rate (itot)
      metric: coefficient
      value: "G7 international analysis: augmented model R2 rises to 0.65-0.96 across countries (US: 0.93-0.96; non-US G7: 0.65-0.93); asset utilization elasticity uniformly positive and significant in all G7 countries (Table XII)"
      direction: positive
      vsBenchmark: "US paradoxical negative q-investment relation unique to US; augmented model resolves it globally"
  resultType: overturns
  relatesTo:
    - { cite: 'Hayashi (1982)', doi: '10.2307/1912538', relation: builds-on, note: 'derives conditions under which average q equals marginal q; paper shows these conditions fail when firms anticipate excess capacity' }
    - { cite: 'Precious (1985)', doi: '10.1093/oxfordjournals.oep.a041711', relation: builds-on, note: 'theoretical framework showing excess capacity drives a wedge between average and marginal q' }
    - { cite: 'Licandro (1992a)', relation: builds-on, note: 'stochastic demand model where marginal q diverges from average q under monopolistic competition' }
    - { cite: 'Licandro (1992b)', relation: builds-on, note: 'factor complementarity model linking excess capacity and marginal q bias' }
    - { cite: 'Peters and Taylor (2017)', doi: '10.1016/j.jfineco.2016.03.011', relation: builds-on, note: 'intangible capital measurement algorithm used to construct total capital (K + KINT) and adjust q and asset utilization' }
    - { cite: 'Andrei, Mann, and Moyen (2019)', doi: '10.1016/j.jfineco.2019.03.007', relation: contradicts, note: 'find a structural break in the q-investment relation around mid-1990s; this paper shows the break disappears after controlling for excess capacity' }
    - { cite: 'Jones and Philippon (2016)', relation: tests, note: 'document secular decline in corporate investment; paper links this to declining asset utilization' }
    - { cite: 'Erickson and Whited (2000)', doi: '10.1086/317670', relation: cites, note: 'measurement error in q as an alternative explanation for weak q-investment relation' }
    - { cite: 'Grullon, Hund, and Weston (2018)', doi: '10.1016/j.jfi.2017.10.001', relation: builds-on, note: "show investment-q sensitivity is negative for large firms, consistent with this paper's excess-capacity explanation" }
  openQuestions:
    - "What precisely is driving the persistent decline in asset utilization? The paper rules out M&A goodwill, automation, and production inefficiencies but notes that rigidities in labor and product markets appear to be the primary cause (pp. 1588-1589); a formal model of this mechanism is not provided."
    - "The paper studies only G7 countries; whether the results extend to emerging markets with different institutional structures and less developed intangible capital markets is left open (p. 1584)."
    - "The paper uses the Peters and Taylor (2017) algorithm to measure intangibles, which requires the assumption that 30% of SG&A is intangible investment; robustness to alternative intangible measures is checked but the sensitivity of results to fundamentally different intangible frameworks remains open (p. 1571)."
  replicationCode:
    status: available
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1533-1592, 60 pages); all results extracted from tables and figures with page locators. Not human-verified. Not reproduced." }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against source PDF; three fixes applied: R7 AU coeff range corrected 0.55-1.14 -> 0.55-1.27 (Table VII Panel B max is decile 7 at 1.27); R8 non-US G7 R2 upper bound corrected 0.65-0.92 -> 0.65-0.93 (UK Panel C = 0.93); mechanisms axis corrected from financial-constraint (paper explicitly refutes this) to excess-capacity. All equations (3)/(3a)/(3b)/(4)/(7)/(12)/(23)/(24)/(25) verified term-by-term against PDF. Table I/III/IV/VI/VII/IX/XII locators and magnitudes confirmed." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13439", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-11; paywalled (Wiley standard VOR terms, not CC)" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical model (a demand-constrained investment problem showing average q becomes biased for marginal q), and the estimating specifications that resolve the q-investment paradox: enough to understand what was found and how, without reading all 60 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13439).

## TL;DR

Tobin's q predicts firms should invest more when market value exceeds replacement cost, yet average q has been rising for decades while corporate investment has been declining. This paper shows the paradox arises because average q is a biased proxy for marginal q whenever managers anticipate excess capacity: the prospect of underutilizing new capital lowers its marginal benefit, creating a wedge between average and marginal q. Augmenting investment regressions with asset utilization (sales scaled by total capital including intangibles, following Peters and Taylor (2017)) restores a positive q-investment relation, raises time-series R-squared from 0.29 to over 0.95, lowers out-of-sample MSE by 89%, and explains why the investment decline has been most severe in industries with the greatest drop in asset utilization. The findings hold across all 10 Fama-French industries, all firm-size deciles, and all G7 countries. Economic rigidities in labor and product markets, not financial constraints or automation, appear to be the primary cause of the secular capacity buildup.

## Core results

Magnitudes and significance are as reported in the source. `*`/`**`/`***` = 10%/5%/1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **q-investment relation flips from negative to positive** when asset utilization is included as a control | Table I Panel A (p. 1545), Table III Panel A (p. 1555) | Traditional model: ln(qtot) coeff = -0.35 (t = -2.82); augmented model (CurrAU proxy): coeff = +0.21 (t = 6.31) |
| R2 | **Augmented model R-squared triples** in time-series investment regressions | Table III Panel A (p. 1555) | Traditional R2 = 0.29; augmented model R2 = 0.95-0.98 depending on asset utilization proxy; asset utilization coeff approx 1.0-1.2 (t = 23-39) |
| R3 | **Firm-level panel confirms results**: augmented model R2 rises significantly after controlling for asset utilization | Table VI Panel A (p. 1561) | Traditional within-firm R2 = 0.28 (N = 140,655); augmented R2 = 0.35-0.45; asset utilization coeff = 0.43-0.63 (t = 14-29) |
| R4 | **No structural break in q-investment relation post-1996** once excess capacity is controlled | Table III Panels B-C (pp. 1555-1556) | Pre-1996: augmented q coeff = 0.24-0.32 (all positive and significant); post-1996: augmented q coeff = 0.09-0.23 (all positive and significant); break disappears |
| R5 | **Augmented model outperforms out-of-sample**: MSE 89% below traditional q model | Figure 8 (p. 1568) | Augmented model MSE = 0.0098%; traditional q model MSE = 0.0881%; naive model MSE = 0.0902%; traditional q model barely beats naive |
| R6 | **Decline in investment rates across industries fully explained by decline in asset utilization** | Table IX (p. 1574) | ln(CurrAU) coeff = 0.83 (t = 5.80); ln(qtot) coeff = -0.10 (t = -0.85, insignificant); long-run cross-industry R2 rises from 0.51 to 0.79 |
| R7 | **Effect is strongest in largest firms** (consistent with excess capacity, not financial constraints): augmented model improvement increases monotonically with firm size | Table VII Panels B-D (pp. 1563-1564) | Asset utilization coeff = 0.55-1.27 across all 10 size deciles (all significant); q coeff flips from -0.36 (largest decile, traditional) to +0.17 (augmented); largest improvement in decile 10 (R2 rises from 0.31 to 0.94-0.98) |
| R8 | **International evidence (G7) confirms results**: asset utilization resolves negative q-investment relation in all G7 countries | Table XII (p. 1586) | US augmented R2 = 0.93-0.96; other G7 R2 = 0.65-0.93; asset utilization elasticity positive and significant in all countries; US unique in showing negative traditional q relation |

**Overall (paper's conclusion).** After correcting for the measurement error induced by anticipated excess capacity, Tobin's q model of investment works as theory predicts: average q is positively related to investment throughout 1974-2021, with no structural break post-1996 (contra Andrei, Mann, and Moyen (2019)). The secular decline in corporate investment rates (documented by Jones and Philippon (2016)) is explained by a secular buildup of excess capacity, driven by economic rigidities that prevent firms from fully adjusting output prices and production costs during negative demand shocks. Tobin's marginal q theory has always worked; measurement error from ignoring excess capacity has obscured the relation.

## Theory / model

The paper builds a continuous-time model of a price-taking firm that maximizes the present value of cash flows, subject to a demand constraint and convex capital adjustment costs (Section III.A, p. 1546). The model follows the intuition in Precious (1985) and the analytical framework of Licandro (1992a) and Licandro (1992b), who show that excess capacity drives a wedge between average and marginal q. The maximization problem is:

$$
\max V(t) = \int_t^\infty e^{-r(s-t)} \{ p(s) F[K(s), L(s)] - w(s)L(s) - I(s) - C[I(s), K(s)] \} \, ds \tag{3}
$$

subject to the law of motion for capital:

$$
I(t) = \dot{K}(t) \tag{3a}
$$

and a demand constraint (the key addition relative to Hayashi (1982)):

$$
F[K(t), L(t)] \leq \bar{Q}(t) \tag{3b}
$$

where $$r$$ is the discount rate, $$p$$ is the output price, $$F[K,L]$$ is the production function, $$w$$ is the wage rate, $$K$$ is capital, $$L$$ is labor, $$I$$ is investment, $$C[I,K]$$ is the capital installation cost, and $$\bar{Q}$$ is the demand ceiling.

Using a Lagrangian with costate variable $$q$$ (average/market q) and Lagrange multiplier $$\lambda_1$$ on the demand constraint (p. 1546):

$$
\mathcal{L} = pF[K,L] - wL - I - C[I,K] + qI + \lambda_1(\bar{Q} - F[K,L]) \tag{4}
$$

The first-order condition for capital (Euler equation) is:

$$
\dot{q} - rq = -pF_K[K,L] + C_K[I,K] + \lambda_1 F_K[K,L] \tag{7}
$$

Solving forward and imposing the transversality condition yields:

$$
q(t) = \int_t^\infty e^{-r(s-t)} \{ (p(s) - \lambda_1(s)) F_K[K(s),L(s)] - C_K[I(s),K(s)] \} \, ds \tag{12}
$$

This shows that when the firm is demand-constrained ($$\lambda_1 > 0$$), the shadow value of capital (marginal $$q$$) declines, because some of the productivity of additional capital cannot be monetized. Marginal $$q$$ is a decreasing function of expected excess capacity.

Under Hayashi's (1982) homogeneity assumption (production function $$F$$ and installation cost $$C$$ both homogeneous of degree one), integrating the Euler equation forward yields the key result (equation 23, p. 1548):

$$
q(t) = \frac{V(t)}{K(t)} - \int_t^\infty e^{-r(s-t)} \frac{\lambda_1(s) F[K(s),L(s)]}{K(t)} \, ds \tag{23}
$$

When there is no demand constraint ($$\lambda_1 = 0$$ for all $$s$$), marginal $$q$$ equals average $$q$$ as in Hayashi (1982). As $$\lambda_1$$ increases (demand more binding), the wedge between marginal and average $$q$$ grows, making average $$q$$ a progressively worse proxy for marginal $$q$$. The wedge equals the present value of future output that cannot be sold due to demand constraints, scaled by current capital.

## Method

The paper applies two complementary empirical strategies. The first (aggregate time-series) closely follows the standard investment literature; the second (firm-level panel) uses fixed effects to control for unobserved heterogeneity. Both build on `panel-regression` and `fama-macbeth` as technique primitives. Prior explanations for weak q-investment relations include measurement error in q (Erickson and Whited (2000)), intangible assets, financial frictions, and declining competition; this paper adds anticipated excess capacity as a previously unexplored source. The finding that the augmented model works best for the largest firms corroborates Grullon, Hund, and Weston (2018), who document that investment-q sensitivity is negative specifically for large firms.

**Measuring total investment and total q.** Following Peters and Taylor (2017), the paper adjusts both investment and average $$q$$ for intangible capital. Total investment is (equation 1, p. 1539):

$$
itot_t = \frac{\sum_{i=1}^N (I_{i,t} + 0.3 \times SG\&A_{i,t} + R\&D_{i,t})}{\sum_{i=1}^N (K_{i,t-1} + KINT_{i,t-1})} \tag{1}
$$

where $$I$$ is capital expenditure, $$SG\&A$$ is selling, general, and administrative expenses (net of R&D), $$R\&D$$ is research and development, $$K$$ is net PP&E, and $$KINT$$ is the replacement cost of intangible capital from Peters and Taylor (2017). Total average $$q$$ is (equation 2, p. 1539):

$$
qtot_t = \frac{\sum_{i=1}^N V_{i,t}}{\sum_{i=1}^N (K_{i,t} + KINT_{i,t})} \tag{2}
$$

where $$V$$ is adjusted market value (market equity plus long-term debt minus net working capital).

**Asset utilization proxy.** Aggregate asset utilization is defined as (equation 24, p. 1549):

$$
au_t = \frac{\sum_{i=1}^N S_{i,t}}{\sum_{i=1}^N (K_{i,t} + KINT_{i,t})} \tag{24}
$$

where $$S$$ denotes total sales. Three proxies for expected asset utilization are used: $$CurrAU_{t-1}$$ (sales-to-total-capital ratio at $$t-1$$, available to managers at the start of year $$t$$), $$ExpAU_{t-1}$$ (realized sales at $$t$$ scaled by total capital at $$t-1$$, a proxy for managers' one-year-ahead expectation), and $$AvgAU_{t-1}$$ (average of the previous two, smoothing temporary shocks).

The predictive validity of these proxies is established via Fama and MacBeth (1973) cross-sectional regressions relating future $$AU_{t+n}$$ to current $$AU_{t-1}$$ across horizons $$n = 1, 3, 5$$ years (Table II, p. 1552): elasticities range from 0.76 to 0.91 with R-squared of 0.65-0.85, confirming current utilization reliably predicts future utilization.

## Empirical specifications

**Aggregate time-series specification (Table III, p. 1555).** The augmented investment equation, estimated in log-log form on annual aggregate Compustat data 1974-2021 with Newey-West (1987) standard errors:

$$
\ln(itot_t) = \alpha + \beta_1 \ln(qtot_{t-1}) + \beta_2 \ln(AU_{t-1}) + \varepsilon_t \tag{}
$$

where $$AU_{t-1}$$ is one of the three proxies. No fixed effects (aggregate time-series). Newey-West with one lag corrects for autocorrelation. This specification produces the headline results (R1, R2): $$\beta_1$$ flips from -0.35 (t = -2.82, traditional) to +0.21 (t = 6.31, augmented with CurrAU), and R-squared jumps from 0.29 to 0.95.

**Industry-level time-series specification (Table IV, p. 1557).** The same log-log form estimated separately for each of the 10 Fama and French (1997) industries on annual aggregated firm-level data:

$$
\ln(itot_{j,t}) = \alpha_j + \beta_1 \ln(qtot_{j,t-1}) + \beta_2 \ln(AU_{j,t-1}) + \varepsilon_{j,t} \tag{}
$$

where $$j$$ denotes industry. No pooled fixed effects; separate intercepts. Asset utilization is uniformly positive and significant across all 10 industries.

**Firm-level panel specification (Table VI, p. 1561).** Annual firm-level data 1974-2021 (N = 140,655 firm-years) with firm and year fixed effects:

$$
\ln(itot_{i,t}) = \alpha_i + \gamma_t + \beta_1 \ln(qtot_{i,t-1}) + \beta_2 \ln(AU_{i,t-1}) + \varepsilon_{i,t} \tag{}
$$

Standard errors are Newey-West with one lag. All ratios winsorized at the 1st and 99th percentiles to mitigate outliers. The within-firm R-squared rises from 0.28 to 0.35-0.45 (result R3).

**Size-decile analysis (Table VII, p. 1563).** The time-series specification re-estimated separately by total-capital decile (tangible plus intangible capital). Identifies the excess-capacity-versus-financial-constraints distinction (result R7): augmented model improvement is largest for the largest firms, where financial constraints are least binding.

**Long-run cross-industry specification (Table IX, p. 1574).** Cross-sectional OLS of long-run investment change on long-run q change and long-run asset utilization change, where long-run change is defined as (equation 25, p. 1572):

$$
\Delta \ln(X) = \ln(\bar{X}_{Post}) - \ln(\bar{X}_{Pre}) \tag{25}
$$

with $$\bar{X}_{Post}$$ the 2019-2021 average and $$\bar{X}_{Pre}$$ the 1974-1976 average. No constant (first differences). Establishes that declining asset utilization, not rising q, explains the secular decline in investment rates (result R6).

**Out-of-sample forecasting (Figure 8, p. 1568).** Rolling 20-year windows forecast $$itot_t$$ using information available at $$t-1$$; the augmented model MSE (0.0098%) is compared to the traditional q model (0.0881%) and a naive model (0.0902%) using rolling and expanding windows.

**International analysis (Table XII, p. 1586).** The aggregate time-series specification replicated country by country on Worldscope data for G7 countries, 1981-2021. Market value defined as equity plus total assets minus book equity minus net working capital (Worldscope lacks the long-term debt decomposition available in Compustat).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Compustat (WRDS) annual fundamentals | Primary dataset: PP&E, sales, R&D, SG&A, market value, long-term debt, working capital; intangible capital (KINT) via Peters and Taylor (2017) algorithm; firm sample 1974-2021 | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Federal Reserve capacity utilization (FRED) | Survey-based capacity utilization at industry level (manufacturing, mining, electric/gas utilities); used to validate asset utilization as a proxy for capacity utilization (Figures 6, 9, 13) | [FRED](/wiki/datasets/fred/) |
| Worldscope | International accounting data for G7 countries (Canada, France, Germany, Italy, Japan, UK, US), 1981-2021; used for Section VII international robustness | No page yet |
| USPTO patent data | Patents granted 1974-2021; used as supplementary evidence for rising intangible capital (Figure 1, Panel B) | No page yet |
| BEA National Income and Product Accounts (NIPA) | Aggregate capital and value-added data (Table S.5.a); used in Section V.C to document government underreporting of intangibles | No page yet |

Sample: Compustat non-financial, non-utility firms (SIC 4900-4999 and 6000-6999 excluded) with at least $5 million in PP&E or sales, annual frequency, 1974-2021. N = 140,655 firm-years.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13439) if you are: (i) building investment models that control for capacity utilization or intangible capital, (ii) testing or extending Tobin's q theory, (iii) investigating why corporate investment rates have declined since the 1980s, (iv) examining the role of economic rigidities (price and wage stickiness) in generating persistent excess capacity, or (v) using Peters and Taylor (2017) intangible capital measures. The locators above point to the exact tables and figures for each result.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. This distillation was extracted by an LLM (claude-sonnet-4-6) on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled under Wiley standard VOR terms; extract-only.

> Grullon, Gustavo, and David L. Ikenberry. "Excess Capacity, Marginal *q*, and Corporate Investment." *The Journal of Finance* 80, no. 3 (June 2025): 1533-1592. DOI: 10.1111/jofi.13439. © 2025 the American Finance Association.
