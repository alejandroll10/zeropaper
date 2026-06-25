---
title: "Green Window Dressing: Parise & Rubin (2025)"
description: >-
  Distilled: ESG mutual funds strategically inflate their ESG factor loadings
  in the 10 days before mandatory portfolio disclosure, then revert to
  higher-return, lower-ESG holdings after filing. Three complementary tests
  (factor loadings, return gap, and stock-level CARs) all confirm the behavior,
  which boosts Morningstar sustainability ratings and attracts investor flows.
  J. Finance 2025, CC BY-NC 4.0. Eight core results with source locators,
  datasets used, the identification design, and the estimating specifications.
sidebar:
  label: Parise-Rubin 2025
  order: 1
tags: [paper-summary, esg, sustainable-investing, mutual-funds, window-dressing,
       panel-regression, event-study, asset-pricing, peer-reviewed, unreplicated,
       data:wrds, data:morningstar, data:trucost, data:ken-french, data:edgar]
paper:
  authors: Gianpaolo Parise, Mirco Rubin
  authorList:
    - { family: Parise, given: Gianpaolo, orcid: "0000-0001-8296-0619", affiliation: Tilburg University and CEPR }
    - { family: Rubin, given: Mirco, orcid: "0009-0000-6418-1734", affiliation: EDHEC Business School }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3555-3588
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13499
  jel:
    codes: [G23, G11, Q56]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ["Sustainable Investing and ESG", "Mutual Fund Portfolio Disclosure", "Asset Management Incentives"]
  dataAccess: licensed-commercial
  outcome:
    - fund ESG factor loading (beta on ESG index)
    - fund return gap (realized minus counterfactual disclosed-portfolio return)
    - ESG stock cumulative abnormal returns around disclosure dates
    - Morningstar sustainability rating (globe score)
    - three-month net fund flows
  outcomeClass: [fund-behavior, security-returns]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-09-29; corroborated by artifact p.3555 Creative Commons
    Attribution-NonCommercial License notice)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC-BY-NC VOR licence confirmed in Crossref DOI metadata 2026-06-03)
  redistribution: extract-only (CC BY-NC 4.0 prohibits commercial redistribution; PDF not hosted)
  resultsCount: 8
  citedByCount: 7
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, event-study, fama-macbeth]
    identification: natural-experiment
  contributionType: [new-fact, measurement]
  mechanisms: [agency, information-asymmetry]
  scope:
    region: US
    assetClass: US equity mutual funds
    period: 2016-03..2022-12
    frequency: daily
    dataType: [market, accounting]
    granularity: [individual, security]
    n: "223 ESG active equity mutual funds; 4,063 fund-event observations (main test)"
  findings:
    - { ref: R1, outcome: "fund ESG factor loading (beta on ESG index)", metric: coefficient, value: "0.120*** (SE 0.044) for 10-day pre-disclosure window", direction: positive }
    - { ref: R2, outcome: "fund ESG factor loading (beta on ESG index)", metric: pp-effect, value: "46% increase over baseline ESG exposure (0.12 / 0.26)", direction: positive }
    - { ref: R3, outcome: "fund return gap (realized minus counterfactual disclosed-portfolio return)", metric: coefficient, value: "Pre: -0.014*** bps/day (SE 0.003); Post: +0.010*** bps/day (SE 0.004)", direction: mixed, vsBenchmark: "pre-disclosure negative vs post-disclosure positive gap relative to disclosed portfolio" }
    - { ref: R4, outcome: "ESG stock cumulative abnormal returns around disclosure dates", metric: car, value: "+0.20% cumulative at event time 0 in [-3, +3] window, reversing to near zero by +3 days", direction: positive, vsBenchmark: "ESG stocks above market model benchmark pre-quarter-end, reverting after" }
    - { ref: R5, outcome: "Morningstar sustainability rating (globe score)", metric: pp-effect, value: "2.1 pp (SE 0.009)** without fund FE; 1.5 pp (SE 0.006)*** with fund FE", direction: positive }
    - { ref: R6, outcome: "three-month net fund flows", metric: coefficient, value: "0.482** pp (SE 0.201) all funds; 0.653** pp institutional (SE 0.275); 0.152 retail (SE 0.358, not significant)", direction: positive, vsBenchmark: "institutional-client funds drive the flow response; retail insignificant" }
    - { ref: R7, outcome: "fund ESG factor loading (beta on ESG index)", metric: pp-effect, value: "High fees: +6.7 pp*** (SE 0.021); Low fees: -5.2 pp*** (SE 0.013); Star: +2.7 pp** (SE 0.011); Laggard: +7.7 pp*** (SE 0.015)", direction: mixed, vsBenchmark: "window dressing propensity varies by fund fee tier and performance rank" }
    - { ref: R8, outcome: "fund ESG factor loading (beta on ESG index)", metric: coefficient, value: "Pre-2016 ESG beta change: not significant; ESG index funds: not significant", direction: none, vsBenchmark: "no effect before March 2016 or for passive ESG vehicles" }
  resultType: overturns
  relatesTo:
    - { cite: "Kacperczyk, Sialm & Zheng (2008)", doi: '10.1016/j.jfineco.2008.09.001', relation: builds-on, note: "return-gap methodology used to compare realized vs. disclosed-portfolio returns (Section II.B)" }
    - { cite: "Agarwal, Gay & Ling (2014)", doi: '10.1093/rfs/hhu045', relation: builds-on, note: "traditional window dressing framework and portfolio disclosure timing design" }
    - { cite: "Hartzmark & Sussman (2019)", doi: '10.1111/jofi.12841', relation: builds-on, note: "documents investor response to Morningstar sustainability ratings that motivates the ESG rating incentive (p. 3578)" }
    - { cite: "Muñoz, Ortiz & Vicente (2022)", doi: '10.1016/j.frl.2022.103109', relation: contradicts, note: "finds no window dressing using end-of-month vs. quarter-end comparison; this paper shows that approach relies on invalid assumptions (p. 3558)" }
    - { cite: "Kempf & Osthoff (2008)", doi: "10.1111/j.1468-036X.2007.00402.x", relation: contradicts, note: "finds no green window dressing pre-2016; this paper reconciles by showing behavior started with Morningstar ratings in March 2016 (p. 3565)" }
    - { cite: "Fama & French (1993)", doi: "10.1016/0304-405x(93)90023-5", relation: cites, note: "FF3 risk model used in robustness tests (Internet Appendix Section III)" }
  openQuestions:
    - "Whether non-ESG mutual funds also window dress at meaningful scale: the paper finds a positive but statistically insignificant effect for non-ESG funds, leaving open how widespread the behavior is (p. 3585)."
    - "Why ESG beta changes are asymmetric around disclosure (gradual increase before, sharp decrease after) for smaller funds: quarter-end investor flows explain part of the pattern but not all, and the smallest funds cannot be fully tested due to limited daily flow data (p. 3583-3584)."
    - "Whether green window dressing harms end investors: the paper documents fund managers can close the performance gap with unconstrained funds but cannot generate CAPM alpha through this strategy (p. 3584)."
  replicationCode:
    status: available
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13499
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-09-29"
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: "Full text read (pp. 3555-3588); eight results extracted from the CC-BY-NC PDF. Not human-verified. Not reproduced. Replication code referenced in the paper (Supporting Information) but has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all eight result rows confirmed correct (Table II, IV, V, VI, VII, Figure 4 values and SEs match); equations 1-7 verified term-by-term; relatesTo cites all locatable in body; no em-dashes or colorful adjectives found; no fixes required."
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
        introducesData, data-scope) re-checked against the source PDF; fixed
        scope.granularity from [security, firm] to [individual, security] --
        primary unit is fund (individual), secondary is stock (security); all
        other axes confirmed correct.
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
        against the source PDF; all eight findings[] values confirmed correct
        against Tables II, IV, V, VI, VII and Figure 4; fixed resultType from
        new-finding to overturns -- the page carries two contradicts edges
        (Munoz et al. 2022 and Kempf-Osthoff 2008) and the headline contribution
        directly overturns the prior claim that green window dressing does not occur.
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification design, and the
estimating specifications: enough to know what it found and how, without reading
all 34 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13499).

## TL;DR

ESG mutual fund managers inflate their portfolio ESG exposure in the 10 days
before mandatory quarterly disclosure, only to reverse those positions
afterward. The paper calls this "green window dressing." Three independent
empirical tests all point to the same behavior: (1) fund ESG betas (loadings on
the Morningstar U.S. Sustainability Total Return Index) rise by 0.12 in the
10 days before filing and revert to prior levels immediately after; (2) funds
earn a negative return gap of -1.4 bps per day before disclosure (underperforming
the portfolio they are about to report) but a positive gap of +1.0 bp per day
after (outperforming the just-disclosed portfolio); and (3) ESG stocks earn
cumulative abnormal returns of +0.20% in the three days before quarter-end
filings, which reverse completely afterward. Green window dressing positively
affects Morningstar sustainability ratings and attracts net fund flows,
particularly from institutional investors. The behavior is absent before March
2016 (when Morningstar introduced sustainability ratings) and is not present for
passive ESG vehicles, confirming active management is required.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | ESG funds increase their ESG beta by 0.12 in the 10 days before mandatory disclosure, reverting to baseline immediately after | Table II, p. 3564 | Pre-disclosure: $$\overline{\Delta\beta}_{-}^{ESG}$$ = 0.120\*\*\* (SE 0.044) for 10-day window; post-disclosure: 0.026 (SE 0.050), not significant |
| R2 | The pre-disclosure ESG beta rise corresponds to a 46% increase over the baseline ESG exposure from the prior month (estimated at 0.26) | Table II footnote, p. 3565 | $$0.12 / 0.26 \approx 46\%$$; market beta falls by 0.107\*\*\* (SE 0.039) concurrently |
| R3 | Funds earn a negative pre-disclosure return gap of -1.4 bps/day, then a positive post-disclosure gap of +1.0 bp/day, with post-disclosure gap driven by lower ESG beta on realized vs. counterfactual returns | Table IV, p. 3570 | Pre: GAP = -0.014\*\*\* (SE 0.003); Post: +0.010\*\*\* (SE 0.004); post-disclosure ESG beta of actual returns (0.127) is 0.047\*\*\* lower than counterfactual ESG beta (0.174) |
| R4 | ESG stocks generate cumulative abnormal returns of +0.20% in the three days before fund portfolio disclosure, which reverse completely after | Figure 4, p. 3575 | CARs peak at roughly +0.20% at event time 0 in the [-3, +3] window; decline to near zero by +3 days; 95% CIs reported |
| R5 | A one-standard-deviation increase in pre-disclosure ESG exposure raises the probability of receiving a five-globe Morningstar rating by 2.1 pp (between funds) and 1.5 pp (within fund) | Table VI, p. 3579 | 2.1 pp (SE 0.009)\*\* without fund FE; 1.5 pp (SE 0.006)\*\*\* with fund FE; reduces probability of one-globe rating by 1.1 pp\*\* (without fund FE) |
| R6 | Green window dressers attract significantly more fund flows: a one-standard-deviation increase in pre-disclosure ESG exposure raises three-month net flows by 0.48 pp, driven entirely by institutional-client funds | Table VII, p. 3580 | All funds: 0.482\*\* (SE 0.201); Institutional: 0.653\*\* (SE 0.275); Retail: 0.152 (SE 0.358), not significant |
| R7 | High-fee funds are 6.7 pp more likely and low-fee funds are 5.2 pp less likely to window dress; star and laggard funds are each more likely to window dress than mid-ranked funds | Table V, p. 3577 | High fees: 0.067\*\*\* (SE 0.021); Low fees: -0.052\*\*\* (SE 0.013); Star fund: 0.027\*\* (SE 0.011); Laggard: 0.077\*\*\* (SE 0.015); PRI signatory: 0.035\*\* (SE 0.014) |
| R8 | Green window dressing is absent before March 2016 (no Morningstar sustainability ratings) and absent for ESG ETFs and index funds; ESG funds also reduce CO2 (pollution) exposure before disclosure | Internet Appendix Tables IA.I (col. 2-4), p. 3565 | Pre-2016 ESG beta change: not significant; ESG index funds: no significant increase; pollution factor beta also declines pre-disclosure (Table IA.X) |

**Overall (paper's conclusion).** Fund managers use quarterly disclosure as a
coordination device: by holding greener portfolios only when portfolios are
publicly observable, they can earn higher sustainability ratings and attract
more capital while holding less constrained, higher-yielding portfolios
between disclosures. Green window dressing does not generate CAPM alpha and
effectively delegates the ESG constraint to disclosure dates only.

## Theory / model

The paper has no formal theoretical model. It offers an economic rationale
based on two incentives for fund managers operating under imperfect monitoring.

The identification relies on the fact that Morningstar sustainability ratings
are determined primarily by disclosed quarterly portfolio holdings: a fund's ESG
profile is assessed based on the ESG scores of the stocks it holds at the
disclosure date. Because funds only need to disclose once per quarter, the
mandate to hold ESG stocks is effectively binding four times a year. This
asymmetric observability creates an incentive to hold ESG-aligned stocks
precisely when positions are observable and to substitute toward higher-yielding
non-ESG assets when they are not. Hartzmark and Sussman (2019) document that
investor flows strongly respond to Morningstar sustainability ratings, providing
the economic motive.

Prior work yields conflicting results. Muñoz, Ortiz, and Vicente (2022) compare
end-of-month to quarter-end holdings and find no window dressing, but the paper
shows their approach relies on the invalid assumption that voluntarily disclosed
month-end holdings are free of strategic manipulation. Kempf and Osthoff (2008)
find no green window dressing in the period before Morningstar sustainability
ratings; this paper reconciles that finding by showing that the behavior emerged
only after March 2016, when Morningstar introduced its globe ratings.

**Null hypothesis (eq. 4, p. 3562).** The identifying assumption is that in the
absence of green window dressing, ESG betas are stable from the pre-event
control window to the pre-event window:

$$
H_0: \; \Delta\beta_{-,i,e}^{ESG} \equiv \beta_{-,i,e}^{ESG} - \beta_{0,i,e}^{ESG} = 0, \quad \forall \; i = 1, \ldots, N \text{ and } e = 1, \ldots, E \tag{4}
$$

**Placebo and falsification evidence.** Three falsification tests validate the
design: (i) random disclosure dates produce no ESG beta increase (Internet
Appendix Table IA.1, col. 1); (ii) the period January 2010 to February 2016,
before Morningstar sustainability ratings, shows no significant effect (col. 2);
and (iii) passive ESG ETFs and index funds, which do not actively manage
portfolios, show no pre-disclosure ESG beta increase (cols. 3-4, p. 3565-3566).
Together these confirm the behavior is driven by active management responding
to the incentive created by Morningstar ratings.

## Method

The method applies three independent identification strategies to a sample of
223 U.S.-domiciled ESG active equity mutual funds over March 2016 to December
2022.

**Test 1: Factor-loading comparison around disclosure (Section I.B, pp. 3561-3563).**
This is the central design. The paper builds on `panel-regression` by estimating
fund-level two-factor regressions on symmetric windows around each mandatory
quarterly filing date $$t_e$$. The pre-disclosure regression (eq. 1, p. 3561):

$$
R_{i,t} = \alpha_{-,i,e} + \beta_{-,i,e}^{MKT} MKT_t + \beta_{-,i,e}^{ESG} ESG_t + \varepsilon_{i,t}, \quad t \in [t_e - n, \; t_e - 1] \tag{1}
$$

and the post-disclosure regression (eq. 2, p. 3561):

$$
R_{i,t} = \alpha_{+,i,e} + \beta_{+,i,e}^{MKT} MKT_t + \beta_{+,i,e}^{ESG} ESG_t + \varepsilon_{i,t}, \quad t \in [t_e + 2, \; t_e + n + 1] \tag{2}
$$

where $$R_{i,t}$$ is the daily return of fund $$i$$ on day $$t$$, $$MKT_t$$ is
the Kenneth French daily market return, and $$ESG_t$$ is the return on the
Morningstar U.S. Sustainability Total Return Index. Both regressions exclude the
disclosure date itself and the following trading day. The control window is the
entire second month of the fiscal quarter, excluding its first and last trading
days (eq. 3, p. 3562):

$$
R_{i,t} = \alpha_{0,i,e} + \beta_{0,i,e}^{MKT} MKT_t + \beta_{0,i,e}^{ESG} ESG_t + \varepsilon_{i,t}, \quad t \in \mathcal{T}_{0,e} \tag{3}
$$

The test statistic is the cross-fund, cross-event average change in ESG beta
(eq. 5, p. 3563):

$$
\overline{\Delta\hat{\beta}_{-}^{ESG}} \equiv \frac{1}{N \cdot E} \sum_{i=1}^{N} \sum_{e=1}^{E} \Delta\hat{\beta}_{-,i,e}^{ESG} \tag{5}
$$

where $$\Delta\hat{\beta}_{-,i,e}^{ESG} \equiv \hat{\beta}_{-,i,e}^{ESG} - \hat{\beta}_{0,i,e}^{ESG}$$. Inference uses a wild bootstrap (Internet Appendix Section I) to account for residual cross-sectional correlation.

The baseline uses $$n = 10$$ trading days; robustness uses $$n = 5$$ and $$n = 15$$.

**Test 2: Return gap (Section II.B, pp. 3569-3572).** Building on
Kacperczyk, Sialm, and Zheng (2008) and the portfolio-disclosure timing design
of Agarwal, Gay, and Ling (2014), the daily return gap for fund $$i$$ is
(eq. 7, p. 3570):

$$
GAP_{i,t} = R_{i,t} - \underbrace{\bigl(R_{i,t}^H - EXP_{i,t}\bigr)}_{R_{i,t}^C} \tag{7}
$$

where $$R_{i,t}$$ is the net-of-fees realized fund return, $$R_{i,t}^H$$ is the
return on a hypothetical buy-and-hold portfolio invested in the disclosed
quarter-end positions, and $$EXP_{i,t}$$ are fund fees. A fund that holds its
disclosed positions exactly earns $$GAP_{i,t} = 0$$; negative values indicate
pre-disclosure positioning away from what will be reported.

**Test 3: ESG stock event study (Section II.C, pp. 3574-3575).**
The paper estimates cumulative abnormal returns on ESG stocks around the four
annual filing dates (March 31, June 30, September 30, December 31). Abnormal
returns use a market model estimated on a 100-day window ending 50 days before
each event; CARs are computed in the [-3, +3] day window. The equally-weighted
portfolio covers all ESG-eligible stocks disclosed by sample funds.

**Trading cost estimation (Section II.A, pp. 3566-3569).** Trading costs are
measured using the Abdi and Ranaldo (2017) "CHL" two-day corrected effective
spread (eq. 6, p. 3566):

$$
\hat{\kappa}_{two\text{-}day,j,t} = \frac{1}{D_t} \sum_{d=1}^{D_t} \hat{\kappa}_{j,d}, \quad \hat{\kappa}_{j,d} = \sqrt{\max\!\bigl\{4(\text{cls}_{j,d} - \text{mid}_{j,d})(\text{cls}_{j,d} - \text{mid}_{j,d+1}),\, 0\bigr\}} \tag{6}
$$

High-ESG stocks have average effective spreads of 0.86% versus 0.98% for
non-high-ESG stocks, making them about 12% cheaper to trade.

## Empirical specifications

All main results use OLS on the panel of 223 ESG active equity mutual funds
over March 2016 to December 2022 (223 funds, 5,793 non-ESG funds available as
comparison group; Table I, p. 3560). The identifying variation is temporal
(within-fund, across-event), not cross-sectional.

**Factor-loading specification (R1, R2, R8).** Separate time-series regressions
(eqs. 1-3) are estimated per fund per event. The cross-event average change
(eq. 5) is the test statistic. Bootstrap inference accounts for cross-sectional
correlation. Sample: 4,063 fund-event observations (Panel A, Table II, p. 3564).
Standard errors in parentheses from the wild bootstrap.

**Return gap specification (R3).** OLS of $$GAP_{i,t}$$ on event-time indicators,
separately for the 10-day pre-disclosure window $$[-10, -1]$$ and post-disclosure
window $$[2, 11]$$. Bootstrapped standard errors. 23,320 fund-day observations.
ESG beta comparison: two-factor model on $$[2, 11]$$ post-disclosure window,
comparing betas on realized and counterfactual returns (2,332 observations,
Table IV, p. 3570).

**Rating specification (R5).** Linear probability model regressing $$I(\text{Five globes})_{t+2}$$ and $$I(\text{One globe})_{t+2}$$ on standardized $$\Delta\hat{\beta}_{-,i,t}^{ESG}$$:

- Column (1): time fixed effects only; column (2): time + fund fixed effects.
- Standard errors clustered at fund level. 2,656 observations (Table VI, p. 3579).

**Fund characteristics and window dressing propensity (R7).** Linear probability
model regressing $$\text{Window dresser}_{t+1}$$ on fund characteristics (fees,
past performance decile, size, disclosure frequency, PRI status, retail investor
share). Time fixed effects throughout. Standard errors clustered at fund level.
3,519 observations (Table V, p. 3577).

**Fund flow specification (R6).** OLS of three-month net flows (in %) on
standardized $$\Delta\hat{\beta}_{-,i}^{ESG}$$, fund size, family size, expense
ratio, and lagged performance. Time fixed effects. Split by retail vs. institutional
clientele (50% retail asset cutoff). 3,795 observations (Table VII, p. 3580).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP mutual fund data (returns, portfolio holdings, TNA, turnover) | Fund returns, portfolio holdings, quarterly disclosure events, fund characteristics | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Morningstar sustainability ratings and fund identifiers | ESG fund classification, five-globe sustainability rating outcome variable, fund category | No page yet |
| Morningstar U.S. Sustainability Total Return Index (MSEGUSTU) | ESG factor ($$ESG_t$$) in two-factor fund-return regressions | No page yet |
| Trucost CO2 emissions | Pollution factor (robustness: pollution exposure before disclosure, Table IA.X) | [Trucost](/wiki/licensed/trucost/) (licensed) |
| Kenneth French data library | Daily market factor ($$MKT_t$$), Fama-French factors in robustness tests | [Ken French library](/wiki/datasets/ken-french/) |
| SEC EDGAR N-PORT filings | Mandated quarterly portfolio disclosure dates | [SEC EDGAR](/wiki/datasets/edgar/) |

Sample: 223 ESG active equity mutual funds, March 2016 to December 2022. Comparison group: 5,793 non-ESG U.S. domestic equity mutual funds (Internet Appendix Section III). Portfolio holdings matched with CRSP daily stock returns for 89% of fund assets (median fund, p. 3570 fn.18).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13499) if you are:
replicating the bootstrap inference procedure (Internet Appendix Section I);
applying trade imputation to recover intra-quarter holdings (Internet Appendix
Section II, using the Bongaerts, van Brakel, and van Dijk (2024) methodology);
testing for green window dressing in non-ESG funds (Internet Appendix Table
IA.XVII); studying the asymmetry in ESG beta changes for small vs. large funds
(Section IV.C, Table IA.XII); or studying broader ESG fund performance using
the Fama and French (1993) five-factor model (Internet Appendix Table IA.XVI).
Locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was
extracted by an LLM on 2026-06-03 and is **not human-verified or independently
reproduced**. The CC BY-NC 4.0 licence permits sharing and adaptation for
non-commercial purposes; the verbatim PDF is not hosted here.

> **Citation.** Parise, Gianpaolo, and Mirco Rubin. "Green Window Dressing."
> *The Journal of Finance* 80, no. 6 (December 2025): 3555-3588.
> DOI: 10.1111/jofi.13499. © 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an extract by the Institute for Automated Research:
> core results and specifications summarized; **changes were made**.
