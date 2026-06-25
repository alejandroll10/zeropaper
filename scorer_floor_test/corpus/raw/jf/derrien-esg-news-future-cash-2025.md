---
title: "ESG News, Future Cash Flows, and Firm Value: Derrien, Kruger, Landier & Yao (2025)"
description: >-
  Distilled: Using RepRisk ESG incident data and IBES analyst forecasts across
  9,737 firms in 49 countries from 2008 to 2019, the paper shows that negative
  ESG news causes analysts to significantly downgrade earnings forecasts at short
  and longer horizons, driven primarily by expected sales declines rather than
  higher costs, and that forecast revisions can account for most of the negative
  impact of ESG incidents on firm value. J. Finance 2025, paywalled. Ten core
  results with source locators, datasets used, the model (Gordon / dividend
  discount decomposition), and the empirical specifications.
sidebar:
  label: Derrien-Kruger-Landier-Yao 2025
  order: 1
tags: [paper-summary, esg, corporate-finance, analyst-forecasts, cash-flows,
       panel-regression, event-study, peer-reviewed, unreplicated,
       data:wrds, data:ibes, data:reprisk, data:capital-iq]
paper:
  authors: Francois Derrien, Philipp Kruger, Augustin Landier, Tianhao Yao
  authorList:
    - { family: Derrien, given: Francois, orcid: "0009-0003-3163-2262", affiliation: HEC Paris }
    - { family: Kruger, given: Philipp, affiliation: University of Geneva (GSEM, GFRI, SFI) and ECGI }
    - { family: Landier, given: Augustin, orcid: "0000-0001-7928-295X", affiliation: HEC Paris }
    - { family: Yao, given: Tianhao, orcid: "0009-0003-7470-6938", affiliation: Singapore Management University }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3499–3554
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13498
  jel:
    codes: [G14, G32, M14]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Corporate Finance and Governance
    - Financial Reporting and Valuation Research
    - Financial Markets and Investment Strategies
  dataAccess: licensed-commercial
  outcome:
    - analyst EPS forecast revision
    - analyst sales forecast revision
    - gross margin forecast revision
    - implied discount rate change
    - realized firm earnings and sales
  outcomeClass: [expectations, firm-real-outcomes]
  license: >-
    Paywalled (Wiley VOR terms and conditions; license[] content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0,
    start=2025-09-30; no CC licence found in Crossref metadata)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley Online Library; confirmed via Crossref DOI metadata 2026-06-03)
  redistribution: extract-only
  resultsCount: 10
  citedByCount: 20
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, event-study, difference-in-differences]
    identification: selection-on-observables
  contributionType: [new-fact, measurement]
  mechanisms: [esg-reputation, learning]
  scope:
    region: global
    assetClass: global equities
    period: 2008-01..2019-12
    frequency: monthly
    dataType: [market, accounting, text]
    granularity: [firm, security]
    n: "744,858 firm-months; 9,737 firms in 49 countries; 81,749 ESG incidents"
  findings:
    - { ref: R1, outcome: analyst EPS forecast revision, metric: coefficient, value: "Q1: -0.142*** (t=-2.09); one-year: -0.130*** (t=-3.08); two-year: -0.148*** (t=-3.76); three-year: -0.157*** (t=-4.18)", direction: negative }
    - { ref: R2, outcome: analyst EPS forecast revision, metric: coefficient, value: "PTG: -0.168*** (t=-6.20); Return: -0.177*** (t=-5.08)", direction: negative }
    - { ref: R3, outcome: analyst EPS forecast revision, metric: coefficient, value: "1 incident: -0.001 to -0.119 across horizons; 2+ incidents: -0.113 to -0.277 across horizons", direction: negative, vsBenchmark: "2+ incidents roughly twice as large as 1 incident" }
    - { ref: R4, outcome: analyst EPS forecast revision, metric: coefficient, value: "S incidents one-year: -0.175*** (t=-4.23); G incidents one-year: -0.150*** (t=-3.13); E incidents one-year: -0.100 (t=-1.70, n.s.)", direction: mixed }
    - { ref: R5, outcome: analyst EPS forecast revision, metric: coefficient, value: "Three-year/one-year ratio: 1.21 for ESG vs. 0.58 for average KD events; F-test p < 0.01", direction: positive, vsBenchmark: "ESG term structure ratio 1.21 vs. 0.58 for other negative corporate events" }
    - { ref: R6, outcome: analyst sales forecast revision, metric: coefficient, value: "Sales one-year: -0.036*** (t=-3.81); two-year: -0.055*** (t=-4.75); gross margin one-year: -0.027** (t=-2.53)", direction: negative }
    - { ref: R7, outcome: implied discount rate change, metric: coefficient, value: "Discount rate change -0.01% (t=-0.11, n.s.); forecast-implied value change -0.41% (t=-2.16); market return -0.30% (t=-1.84)", direction: none }
    - { ref: R8, outcome: analyst EPS forecast revision, metric: coefficient, value: "Large-firm interaction 0.670*** (t=5.39)", direction: mixed, vsBenchmark: "small-firm effect roughly 0.67 pp larger than large-firm effect" }
    - { ref: R9, outcome: realized firm earnings and sales, metric: coefficient, value: "Earnings [t-1 to t]: -0.088*** (t=-4.79); [t-1 to t+1]: -0.118*** (t=-4.79); Sales [t-1 to t+1]: -0.026*** (t=-6.66)", direction: negative }
    - { ref: R10, outcome: analyst EPS forecast revision, metric: coefficient, value: "One-year: -0.002** (t=-2.84); two-year: -0.003*** (t=-3.56); three-year: -0.004*** (t=-3.98)", direction: negative, vsBenchmark: "analysts who downward-adjust after ESG incidents vs. those who do not" }
  resultType: new-finding
  relatesTo:
    - { cite: "Glosner (2021)", relation: builds-on, note: "documents that negative ESG shocks predict negative future stock returns, suggesting underreaction; motivates studying the analyst channel" }
    - { cite: "Pedersen, Fitzgibbons & Pomorski (2021)", doi: '10.1016/j.jfineco.2020.11.001', relation: builds-on, note: "models the cash flow channel through which ESG information affects expected returns" }
    - { cite: "Berk & van Binsbergen (2024)", relation: tests, note: "argues theoretically that ESG divestment has no detectable cost-of-capital effect; this paper finds empirically that discount rate changes are small and insignificant" }
    - { cite: "Hommel, Landier & Thesmar (2023)", doi: '10.3386/w30898', relation: builds-on, note: "discounted dividends approach used to decompose ESG valuation effects into cash flow and discount rate components" }
    - { cite: "Servaes & Tamayo (2013)", doi: '10.1287/mnsc.1120.1630', relation: cites, note: "shows ESG policies influence consumer behavior and future firm cash flows; motivates the customer-demand channel hypothesis" }
    - { cite: "Duan, Li & Michaely (2024)", doi: '10.2139/ssrn.4584361', relation: cites, note: "shows consumer demand decreases following negative ESG incidents using retail store data, corroborating the sales-channel finding" }
    - { cite: "Berg, Koelbel & Rigobon (2022)", doi: '10.1093/rof/rfac033', relation: cites, note: "documents ESG rating disagreement across providers, motivating use of ESG news rather than ratings" }
  openQuestions:
    - "Whether the test for discount rate changes lacks sufficient statistical power to fully rule out a change in implied discount rates after ESG incidents (p. 3529)."
    - "The IRR analysis for cost-of-capital changes was run only for the U.S. sample; ESG incidents could potentially affect discount rates differently outside the United States (p. 3529, footnote 12)."
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Full text read (pp. 3499-3554); ten results extracted from the PDF.
        Not human-verified. Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; three
        corrections applied: R3 upper bound for 1-incident range corrected from
        -0.113 to -0.119 (Table III Panel B three-year column); R6 gross margin
        one-year coefficient corrected from -0.039 to -0.027 (Table VIII col 12,
        t-stat -2.53 was correct); sample-stats text corrected to reflect that
        10.44% is the at-least-one share (6.57% exactly one, 3.87% at least two)
        per p. 3508. All other locators, coefficients, t-stats, equations (1)-(8),
        and frontmatter verified correct.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Added classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) from a fresh PDF read; existing results and
        sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) re-checked against the source PDF; all axes
        confirmed correct - selection-on-observables matches the within-firm FE
        design with no instrument or quasi-experiment; new-fact and measurement
        match the paper's contributions; esg-reputation and learning match the
        two channels explicitly tested in Sections III and VI; introducesData
        correctly absent; dataType [market, accounting, text] and n confirmed
        against p. 3508.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the page's already-verified Core-results table and
        relatesTo edges; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; all ten entries confirmed correct against Tables
        III-XIV (values, t-stats, signs, directions); R3 upper bound -0.119
        reconciled against body text p. 3511 (authors write "approximately
        -0.119", table shows -0.110 as the maximum - body text is the stated
        magnitude, no change made); resultType new-finding consistent with
        primarily novel analyst-expectations facts and no overturned prior.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13498
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: >-
        license[].content-version=vor,
        URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
        delay-in-days=0, start=2025-09-30; no Creative Commons licence present
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the valuation model used to
decompose ESG shocks into cash-flow and discount-rate components, and the
regression specifications behind each finding: enough to know what was found
and how, without reading the full 56 pages. To replicate or extend, read the
original at [doi.org/10.1111/jofi.13498](https://doi.org/10.1111/jofi.13498).

## TL;DR

Using RepRisk ESG incident data matched to IBES consensus analyst forecasts
across 9,737 firms in 49 countries (2008-2019, 81,749 ESG incidents), the
paper shows that negative ESG news triggers a significant, approximately
parallel downward shift in analyst EPS forecasts over all horizons from one
quarter to three years. The revision reflects primarily expected sales declines
(anticipated customer withdrawal) rather than higher costs, consistent with
the customer-demand channel emphasized in Servaes and Tamayo (2013) and
corroborated by retail store evidence in Duan, Li, and Michaely (2024). A
dividend discount decomposition following the framework of Hommel, Landier,
and Thesmar (2023) shows that forecast revisions can account for essentially
all of the negative stock-price reaction to ESG incidents, while implied
discount rates do not change significantly. This is consistent with Berk and
van Binsbergen (2024), who argue theoretically that ESG divestment has no
detectable cost-of-capital effect. The paper uses ESG news events from
RepRisk rather than ESG ratings (which suffer from the disagreement documented
by Berg, Koelbel, and Rigobon (2022)) because news events provide cleaner
identifiable shocks. Glosner (2021) documents that negative ESG shocks predict
negative future returns, suggesting underreaction; this paper studies the
analyst expectations channel that underlies that pattern. Analysts who
downward-adjust EPS forecasts following ESG incidents reduce their forecast
errors relative to those who do not, confirming the revisions are rational.
The paper also shows that the ESG effect on earnings forecasts persists over
longer horizons than effects from other negative events, consistent with the
permanent-shock interpretation suggested by Pedersen, Fitzgibbons, and Pomorski
(2021) for the cash flow channel of ESG information.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Negative ESG incidents cause significant **parallel downward revision in EPS forecasts at all horizons** (Q1 through three years); the term structure is approximately flat | Table III Panel A, p. 3512; Figure 2, p. 3521 | Q1: -0.142\*\*\* (t=-2.09); one-year: -0.130\*\*\* (t=-3.08); two-year: -0.148\*\*\* (t=-3.76); three-year: -0.157\*\*\* (t=-4.18) |
| R2 | ESG incidents cause a significant **decline in stock returns and analyst-implied price target revisions** of similar magnitude to EPS revisions | Table III Panel A cols. 9-10, p. 3512 | PTG: -0.168\*\*\* (t=-6.20); Return: -0.177\*\*\* (t=-5.08) |
| R3 | **Multiple incidents amplify the effect**: firms with at least two incidents in months [t-6,t] see EPS declines roughly twice as large as firms with one incident | Table III Panel B, p. 3513 | 1 incident: -0.001 to -0.119 across horizons; 2+ incidents: -0.113 to -0.277 across horizons |
| R4 | **Social incidents have the strongest and most persistent effect** on EPS forecasts; environmental incidents are less significant; governance incidents also significant but smaller | Table IV Panels A-C, pp. 3514-3515 | S incidents one-year: -0.175\*\*\* (t=-4.23); G incidents one-year: -0.150\*\*\* (t=-3.13); E incidents one-year: -0.100 (t=-1.70, n.s.) |
| R5 | ESG incidents have a **longer-lived term structure** than other types of negative corporate events: the three-year impact is 21% higher than the one-year impact, while for other KD negative events the three-year impact is 42% lower than the one-year impact | Figure 2 p. 3521; Table VII p. 3523 | Three-year/one-year ratio: 1.21 for ESG vs. 0.58 for average KD events; F-test rejects equal term structures (p < 0.01) |
| R6 | **ESG-induced EPS revisions are driven primarily by expected sales declines** (not cost increases): sales forecast revisions are consistently negative across all horizons; gross margin revisions are smaller and less significant | Table VIII Panel A, p. 3524-3525 | Sales one-year: -0.036\*\*\* (t=-3.81); two-year: -0.055\*\*\* (t=-4.75); avg. decline ~0.051% per year; gross margin one-year: -0.027\*\* (t=-2.53) |
| R7 | **Cash flow changes, not discount rate changes, account for observed firm value declines**: a dividend discount decomposition shows the EPS-forecast-implied value change covers the stock return; implied discount rates do not change significantly | Table IX p. 3529 | At [t,t+3]: market return -0.30% (t=-1.84), forecast-implied value change -0.41% (t=-2.16); discount rate change -0.01% (t=-0.11, n.s.) |
| R8 | **Effect is stronger for smaller firms** and stronger (though not significantly so) for B2C industries with high advertising intensity | Table XI p. 3539; Table XII p. 3541 | Large-firm interaction coefficient 0.670\*\*\* (t=5.39) in EPS regressions, implying small-firm effect roughly 0.67 p.p. larger; B2C interaction negative and economically meaningful at one- and two-year horizons |
| R9 | **Realized firm earnings and sales decline after ESG incidents**: net income decreases by 8.8% to 11.8% and sales by 1.2% to 4.2% in the year(s) following incidents, confirming analysts are correct | Table XIII Panels A-B, pp. 3543-3544 | Earnings [t-1 to t]: -0.088\*\*\* (t=-4.79); [t-1 to t+1]: -0.118\*\*\* (t=-4.79); Sales [t-1 to t+1]: -0.026\*\*\* (t=-6.66) |
| R10 | **Analysts who downward-adjust EPS forecasts after ESG incidents reduce their forecast errors**: interaction of downward adjustment and ESG incident is negative and significant for annual and two/three-year horizons | Table XIV p. 3547 | One-year horizon: -0.002\*\* (t=-2.84); two-year: -0.003\*\*\* (t=-3.56); three-year: -0.004\*\*\* (t=-3.98) |

**Overall (paper's conclusion).** Negative ESG news generates a permanent
downward shift in analyst earnings expectations driven primarily by anticipated
customer withdrawal (reduced future sales), not by higher costs. This cash flow
effect can quantitatively account for most of the negative stock-price response
to ESG incidents, while no significant change in cost of capital is detected.
The downward revisions are rational: realized earnings and sales drop after ESG
incidents, and analysts who revise downward make more accurate forecasts.

## Theory / model

The paper has no structural economic model. The theoretical framework is a
dividend discount decomposition to separate cash-flow from discount-rate
effects of ESG shocks on firm value.

**Hypotheses tested.** ESG information can affect firm value through two
channels: (1) a *cash flow channel*, where ESG incidents signal lower future
earnings because customers avoid firms with poor ESG profiles, or because the
firm cannot instantaneously adjust its production technology; and (2) a
*discount rate channel*, where divestment by ESG-conscious investors raises
the cost of capital.

**Gordon growth-formula pass.** As a first pass (Section IV.A, p. 3527), the
equity value of firm $$i$$ at time $$t$$ follows Gordon's formula for a growing
perpetuity:

$$
PV_{it} = \frac{b_i F_t\text{EPS}_{i,t+1}}{r_{it} - g_{it}} \tag{3}
$$

where $$b_i$$ is the payout ratio, $$F_t\text{EPS}_{i,t+1}$$ is the one-year
earnings forecast, $$r_{it}$$ is the discount rate, and $$g_{it}$$ is the
expected earnings growth rate. The theoretical firm-level return induced by an
ESG information shock is

$$
\frac{\Delta PV_{it}}{PV_{it}} = \frac{\Delta F_t\text{EPS}_{i,t+1}}{F_t\text{EPS}_{i,t+1}} - \frac{\Delta r_{it} - \Delta g}{r_{it} - g_{it}}
$$

Because Table III shows that the ESG impact on LTG is economically and
statistically insignificant (column (8)), the growth term drops out and
changes in earnings forecasts should equal changes in firm value. The
similarity between the EPS revision coefficient and the stock return
coefficient (Table III Panel A, cols. (5)-(7) vs. (10)) confirms this.

**Discounted dividends decomposition.** The more formal approach (Section IV.B,
pp. 3527-3528) uses the present value of near-term earnings payouts:

$$
\frac{PV_{it}(r_{it})}{b_i} = \frac{F_t\text{EPS}_{i,t+1}}{(1+r_{it})^{\theta_{it}}} + \frac{F_t\text{EPS}_{i,t+2}}{(1+r_{it})^{\theta_{it}+1}} + \frac{F_t\text{EPS}_{i,t+3}}{(1+r_{it})^{\theta_{it}+2}} + \frac{1}{(1+r_{it})^{\theta_{it}+2}} \cdot \frac{(1+g_t)F_t\text{EPS}_{i,t+3}}{r_{it}-g_t} \tag{4}
$$

where $$\theta_{it}$$ is the fraction of the fiscal year remaining, $$b_i$$ is the
rolling-average industry payout ratio, and $$g_t$$ is the expected long-run
nominal GDP growth from macro forecasters. The implied discount rate $$r_{it}$$ is
the solution to

$$
PV_{it}(r_{it}) = P_{it} \tag{5}
$$

where $$P_{it}$$ is the observed stock price. The authors compute the forecast-
implied value change when EPS forecasts are updated at each post-event window,
holding $$r_{it}$$ fixed, and compare it to the actual market return and to
changes in the implied discount rate (Table IX, p. 3529).

## Method

The paper applies a standard panel fixed-effects framework augmented with an
event-study design for the valuation decomposition. It does not propose a new
method. The approach builds on `panel-regression` and `event-study`.

**Baseline analyst reaction regression.** For each forecast horizon $$h$$,
equation (1) (p. 3509) is estimated:

$$
\frac{\Delta F_t\text{EPS}_{i,t+h}}{\text{abs}(F_{t-1}\text{EPS}_{i,t+h})} = \alpha + \beta \, \mathbf{1}[\text{ESG incidents in } [t-6,t]] + \gamma_{\text{Country}\times\text{Industry}\times t} + \sigma_i + \epsilon_{i,t} \tag{1}
$$

The dependent variable is the month-over-month change in consensus EPS
forecast scaled by the absolute value of the prior month's consensus forecast.
The main independent variable is an indicator equal to one if RepRisk reports
at least one ESG incident in the six months prior to month $$t$$. The
specification includes firm fixed effects ($$\sigma_i$$) and industry-by-country-
by-month fixed effects ($$\gamma_{\text{Country}\times\text{Industry}\times t}$$).
Standard errors are double-clustered at the firm and month levels.

**Mechanism regressions.** The same specification as equation (1) is estimated
replacing the EPS forecast change with the change in consensus sales forecasts
($$\frac{\Delta F_t\text{Sales}_{i,t+h}}{F_{t-1}\text{Sales}_{i,t+h}}$$) and
the change in gross margin forecasts
($$\frac{\Delta F_t\text{GrossMargin}_{i,t+h}}{F_{t-1}\text{GrossMargin}_{i,t+h}}$$)
to separate the sales from the cost channel (Table VIII, p. 3524).

**Term structure comparison.** To compare ESG incidents with other negative
corporate events, equation (2) (p. 3521) is estimated pooling horizons and
testing whether the slope of the term structure differs:

$$
\frac{\Delta F_t\text{EPS}_{i,t+h}}{\text{abs}(F_{t-1}\text{EPS}_{i,t+h})} = \alpha + \beta \, \mathbf{1}[\text{ESG incidents in } [t-6,t]] + \eta \, \mathbf{1}[\text{KD Negative Events in } [t-6,t]] + \gamma_{\text{Country}\times\text{Industry}\times t} + \sigma_i + \epsilon_{i,t} \tag{2}
$$

**Event-study for the valuation decomposition.** Equation (6) (p. 3528)
estimates how the forecast-implied value change, actual return, and implied
discount rate evolve over months $$s = 0, 1, \ldots, 6$$ following an ESG
event month:

$$
y_{t,t+s} = \alpha + \beta \, \mathbf{1}[\text{ESG incidents in month } t] + \gamma_{\text{Country}\times\text{Industry}\times t} + \text{Controls} + \epsilon_{i,t} \tag{6}
$$

Controls include firm size and book-to-market quintile dummies. Standard errors
are double-clustered at the firm and month level.

**Realized fundamentals regression.** To test whether analysts are correct,
equation (7) (p. 3538) uses annual data:

$$
\frac{Y_{i,t+h} - Y_{i,t-1}}{Y_{i,t-1}} = \alpha + \beta \, \mathbf{1}[\text{ESG incidents between year } t-1 \text{ and } t] + \gamma_{\text{Country}\times\text{Industry}\times t} + \sigma_i + \epsilon_{i,t} \tag{7}
$$

where $$Y_{i,t}$$ denotes realized annual earnings, sales, or gross margin.

**Analyst accuracy regression.** Equation (8) (p. 3545) uses the analyst-firm
panel to compare forecast accuracy for analysts who do versus do not downward-
adjust following ESG incidents:

$$
\frac{|FEPS_{i,e,j,t} - EPS_{i,e}| - |FEPS_{i,e,j,t-1} - EPS_{i,e}|}{|EPS_{i,e}|} = \alpha + \eta \, \text{DownwardAdj}_{i,e,j,t} + \beta \, \text{DownwardAdj}_{i,e,j,t} \times \mathbf{1}[\text{ESG incidents of firm } i \text{ in } [t-6,t]] + \gamma_{i,e,t} + \epsilon_{i,e,j,t} \tag{8}
$$

where $$FEPS_{i,e,j,t}$$ is analyst $$j$$'s EPS forecast for firm $$i$$ earnings
announcement $$e$$ in month $$t$$, and $$\gamma_{i,e,t}$$ indicates firm-by-earnings-
announcement-by-month fixed effects.

## Empirical specifications

All regressions use panel data at the firm-month level (or firm-year for the
realized-fundamentals tests). The headline specifications are:

- **EPS/Sales/GrossMargin forecast regressions (R1, R3, R4, R5, R6, R8)**:
  Equation (1) with firm FE and industry-by-country-by-month FE, double-
  clustered standard errors, horizon $$h$$ = Q1, Q2, Q3, Q4, one-year,
  two-year, three-year. Sample: 2008-2019, global, 9,737 firms in 49 countries.
  EPS observations: 2,976,889; sales: 2,831,931; gross margin: 1,442,110.
  The indicator for ESG incidents is cumulated over months $$[t-6,t]$$ (the
  main specification; Internet Appendix Tables IA.III-IV show robustness to
  $$[t-3,t]$$ and $$[t-9,t]$$). The ESG incident variable has 10.44% of
  firm-months with at least one incident (6.57% exactly one, 3.87% at least two).

- **Term structure test (R5)**: Equation (2) pools one-, two-, and three-year
  horizons; the F-test in columns (4)-(5) of Table VII (p. 3523) rejects equal
  slopes for ESG vs. average KD events (p < 0.01).

- **Valuation decomposition event study (R7)**: Equation (6), US firms only
  (needed for the payout-ratio and growth rate computation). Table IX (p. 3529)
  reports cumulative event-window coefficients for windows $$[t,t]$$ through
  $$[t,t+6]$$. Standard errors double-clustered by firm and month.

- **Realized outcomes (R9)**: Equation (7) at the firm-year level, annual data,
  firm FE and country-by-industry-by-year FE. Dependent variable is percentage
  change in earnings, sales, or gross margin over one- and two-year windows.

- **Analyst accuracy (R10)**: Equation (8), analyst-firm panel. Firm-by-
  earnings-announcement-by-month FE. Observations: 2.6M (Q1) to 3.2M (three
  years). Results are negative and significant for annual and longer horizons.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| RepRisk ESG incident data | Main independent variable: daily negative ESG incidents at firm level, 2007-2019, 28 ESG issue categories, novelty/severity/reach scores | [RepRisk](/wiki/licensed/reprisk/) (licensed) |
| IBES consensus analyst forecasts | Dependent variable: EPS, sales, gross margin, LTG, and price target consensus forecasts at firm-month level, quarterly and annual horizons | [I/B/E/S](/wiki/licensed/ibes/) (licensed) |
| CRSP / Compustat (via WRDS) | Stock returns (daily), firm fundamentals (annual), book-to-market, market cap, payout ratios | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Capital IQ Key Developments | Comparison non-ESG corporate events (153 types); identify 33 types with significant negative EPS impact | No page yet |
| Refinitiv (Asset4), Morningstar Sustainalytics, MSCI ESG scores | Validation that RepRisk incidents correlate with major ESG ratings (Appendix) | No page yet |

Sample: January 2008 to December 2019 (monthly). Final sample: 744,858 unique
firm-month observations; 9,737 firms in 49 countries; 81,749 ESG incidents.
EPS forecasts: 2,976,889 observations; sales: 2,831,931; LTG: 253,735; PTG: 688,899.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13498) if you are:
studying the cash-flow versus discount-rate channel for ESG-related firm value
changes; working with RepRisk data and need to understand its term structure
and heterogeneity properties; building models of ESG-driven analyst
expectations; or extending the analysis to additional horizons, industries,
or event types beyond the 33 KD categories examined. The tables above provide
exact locators for each result.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025.
This distillation was extracted by an LLM on 2026-06-03 and is **not
human-verified or independently reproduced**. The paper is paywalled; only
extracts are reproduced here.

> Derrien, Francois, Philipp Kruger, Augustin Landier, and Tianhao Yao.
> "ESG News, Future Cash Flows, and Firm Value."
> *The Journal of Finance* 80, no. 6 (December 2025): 3499-3554.
> DOI: 10.1111/jofi.13498. Published by Wiley on behalf of the American
> Finance Association. All rights reserved. Extract-only reproduction.
