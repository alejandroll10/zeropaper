---
title: "Household Portfolios and Retirement Saving: Parker, Schoar, Cole & Simester (2025)"
description: >-
  Distilled: Using account-level data on millions of U.S. middle-class investors from 2006
  to 2018, this paper documents that equity shares rose 10 percentage points relative to the
  1990s, became hump-shaped over the life cycle, and were driven largely by the Pension
  Protection Act of 2006 and the adoption of target date funds as default options. Retirement
  contribution rates, by contrast, changed little. J. Finance 2025, CC BY 4.0. Seven core
  results with source locators, datasets used, the identification design (difference-in-differences
  around PPA 2006), and the estimating equations.
sidebar:
  label: Parker-Schoar-Cole-Simester 2025
  order: 1
tags: [paper-summary, household-finance, life-cycle, retirement, pension, target-date-funds,
       default-options, portfolio-sort, panel-regression, difference-in-differences,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:wrds]
paper:
  authors: Jonathan A. Parker, Antoinette Schoar, Allison Cole, Duncan Simester
  authorList:
    - { family: Parker, given: Jonathan A., affiliation: MIT Sloan School of Management and NBER }
    - { family: Schoar, given: Antoinette, affiliation: MIT Sloan School of Management and NBER }
    - { family: Cole, given: Allison, orcid: "0000-0003-4393-464X", affiliation: Arizona State University }
    - { family: Simester, given: Duncan, orcid: "0000-0003-2758-0116", affiliation: MIT Sloan School of Management }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2739–2787
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13473
  jel:
    codes: [G11, G51, G52]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Housing Market and Economics
    - Insurance, Mortality, Demography, Risk Management
  dataAccess: proprietary-confidential
  outcome:
    - equity share of investable wealth over the life cycle
    - effect of TDF default adoption (PPA 2006) on portfolio equity share
    - retirement contribution rate over the life cycle
  outcomeClass: [household-finance]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-08-12; corroborated by artifact p. 2739 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-05)
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 5

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, difference-in-differences]
    identification: natural-experiment

  contributionType: [new-fact, measurement]

  mechanisms: [participation-frictions, behavioral-bias]

  scope:
    region: US
    assetClass: household retirement and brokerage portfolios
    period: 2006-01..2018-12
    frequency: annual
    dataType: [administrative]
    granularity: [individual]
    n: "millions of investors, trillions of dollars in investable wealth, 2006-2018 (annual)"

  findings:
    - ref: R1
      outcome: equity share of investable wealth over the life cycle
      metric: pp-effect
      value: "average equity share 71.0% in 2016 (median 77.3%); 10pp higher than 1990s (Ameriks and Zeldes 2004 report ~58% with no age trend); hump-shaped from ~74% at age 25-27 to ~55% at age 64-65 in cross-section (Figure 5)"
      direction: positive
      vsBenchmark: 10pp above 1990s baseline; SCF reports only 54.5% (Table III)
    - ref: R2
      outcome: equity share of investable wealth over the life cycle
      metric: pp-effect
      value: "within-person: equity share rises ~7% from age 25 to 50, then falls ~7% from 50 to 65, producing a hump-shaped life-cycle profile (Figure 6); in 1990s, equity shares were flat or upward-sloping with age"
      direction: positive
      vsBenchmark: reverses flat/upward-sloping pattern of 1990s documented in Ameriks and Zeldes (2004)
    - ref: R3
      outcome: equity share of investable wealth over the life cycle
      metric: pp-effect
      value: "younger cohorts hold higher equity shares at every overlapping age than older cohorts; cohorts born after 1970 have 15-20pp higher equity shares by 2018 than those born around 1945 (Figure 7)"
      direction: positive
      vsBenchmark: monotone increase in average equity share across cohorts born before ~age 40
    - ref: R4
      outcome: effect of TDF default adoption (PPA 2006) on portfolio equity share
      metric: pp-effect
      value: "age 25-35 enrollees at firms switching to TDF default: +5.5pp equity share in first two years (Table IV col. 1, coeff. 0.0552, SE 0.0907); +6pp for bottom income tercile; <2pp for top income tercile"
      direction: positive
      vsBenchmark: enrollees two years before vs. two years after PPA, same firm; firm fixed effects
    - ref: R5
      outcome: effect of TDF default adoption (PPA 2006) on portfolio equity share
      metric: pp-effect
      value: "age 55-65 enrollees at firms switching to TDF default: -13.2pp equity share in first two years (Table IV col. 1, coeff. -0.1325, SE 0.0012); consistent with TDF glidepath reducing equity for near-retirees"
      direction: negative
      vsBenchmark: same DiD design; TDF glidepath lowers equity for older workers
    - ref: R6
      outcome: effect of TDF default adoption (PPA 2006) on portfolio equity share
      metric: pp-effect
      value: "five-year medium-run effect: age 25-34 five-year treatment interaction coefficient 0.0134 (~1.3pp still above control at year 5, down from 0.0363 peak at year 2); age 55-65 five-year treatment interaction coefficient -0.0564 (~5.6pp still below control at year 5, down from -0.1321 trough at year 1); paper text approximates these as 'nearly 3%' and '2%' respectively, referring to graphical predicted-equity-share gaps in Figure 10 (Table V col. 4 and 7)"
      direction: mixed
      vsBenchmark: convergence over five years as control group adopts TDF-like allocations voluntarily
    - ref: R7
      outcome: retirement contribution rate over the life cycle
      metric: pp-effect
      value: "contribution rates increase from ~4.6% at age 25 to ~8.5% at age 65 (cross-section, Figure 11 Panel A); within-person increase of ~5% over working life (Figure 11 Panel B); PPA 2006 has negative initial effect of -0.43% for young and -1.2% for old, fading to near zero after five years (Table VI and VII)"
      direction: positive
      vsBenchmark: PPA has negligible long-run effect on saving rates; portfolio changes are much larger

  resultType: new-finding

  relatesTo:
    - { cite: 'Ameriks and Zeldes (2004)', relation: contradicts, note: 'documents that 1990s equity shares were flat/upward-sloping with age at ~58%; this paper shows 2006-2018 shares are 10pp higher and hump-shaped, reversing the earlier pattern' }
    - { cite: 'Campbell (2016)', doi: '10.1257/aer.p20161127', relation: builds-on, note: 'survey of household finance motivating the study of retirement plan design on saving and portfolio allocation' }
    - { cite: 'Madrian and Shea (2001)', doi: '10.1162/003355301753265543', relation: builds-on, note: 'early evidence that default investment options in 401(k) plans strongly affect participation and allocation decisions' }
    - { cite: 'Mitchell and Utkus (2022)', relation: extends, note: 'Vanguard-based evidence on TDF effects; this paper uses a different large financial institution and focuses on life-cycle patterns and PPA causal effects' }
    - { cite: 'Gomes et al. (2018)', relation: tests, note: 'optimal consumption-saving model predicting significant contribution shortfall; consistent with this paper finding contribution rates below model prescriptions' }
    - { cite: 'Parker, Schoar and Sun (2023)', doi: '10.1111/jofi.13258', relation: cites, note: 'companion paper on TDF growth and aggregate implications; used here for context on industry evolution' }

  openQuestions:
    - "The sample comes from a single financial services firm, so results may be driven in part by firm-specific plan designs or investor selection; representativeness relative to the full U.S. population of retirement investors is only approximately confirmed via SCF comparisons (p. 2754-2755)."
    - "The analysis conditions on plan participants; it cannot directly measure whether the PPA changed total participation rates or the composition of who chooses to participate, which could confound the DiD estimates (p. 2765)."
    - "Whether the causal effects of the PPA and TDF adoption documented here persist over longer horizons beyond five years, and whether they generalize to the full population including very high- and very low-wealth households excluded by the RI sample restriction, remains open (p. 2784)."

  replicationCode:
    status: available
    note: "Replication code listed as supporting information (Appendix S1 / Replication code, p. 2787); hosted at Wiley publisher website alongside the article."

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: >-
        Full text read (pp. 2739-2787); seven results extracted from the CC-BY PDF.
        Crossref and OpenAlex metadata fetched this session. Not human-verified.
        Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; R1-R5 and R7
        confirmed correct against Tables III-IV and VI-VII and Figures 5-6. R6 magnitude
        corrected: distiller reported "~3pp / ~2pp" from paper text approximations, but
        Table V col.(4) 5-year coefficient is 0.0134 (~1.3pp) and col.(7) is -0.0564
        (~5.6pp); paper text likely derives its approximate figures from Figure 10 predicted
        equity share gaps. Equations 1-3 verified term-by-term against PDF pp. 2756, 2765,
        2769. replicationCode.status corrected from none to available (p. 2787 lists
        replication code as supporting information).

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13473
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-12"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification design exploiting the Pension
Protection Act of 2006 as a natural experiment, and the estimating equations: enough to know
what it found and how, without reading all 49 pages. To replicate or extend the analysis, read
the full source at the [original](https://doi.org/10.1111/jofi.13473).

## TL;DR

Using account-level data from a large U.S. financial institution on millions of middle-class
investors (2006 to 2018), the paper documents three facts. First, middle-class investors hold
roughly 71% of their investable wealth in equities, about 10 percentage points more than in the
1990s. Second, the life-cycle profile of equity shares is now hump-shaped: investors increase
their stock allocation from age 25 to around 50 and then reduce it as they approach retirement,
a pattern absent before 2000. Third, retirement contribution rates have increased steadily with
age by about 4% to 5% over working lives and are stable across cohorts. The PPA of 2006, which
permitted target date funds (TDFs) as qualified default investment alternatives, is shown to
have caused the portfolio changes, particularly for younger and lower-income workers, while
having little persistent effect on contribution rates. The savings behavior documented here is
broadly consistent with prescriptive life-cycle portfolio models, unlike the 1990s patterns.

## Core results

Magnitudes and significance are as reported; locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Average equity share of investable wealth is 71%, 10pp above the 1990s, and inversely related to age in the cross-section** | Table III Panel A, p. 2753; Figure 5, p. 2757 | Mean equity share 71.0% (median 77.3%) in 2016; cross-sectional age gradient from ~74% at ages 25-27 to ~55% at ages 64-65; SCF shows only 54.5% (underreporting argued) |
| R2 | **Within-person, equity shares follow a hump-shaped life-cycle: up ~7% from age 25 to 50, down ~7% from 50 to 65**; in the 1990s the profile was flat or upward-sloping | Figure 6, p. 2759; Figure 9 bottom panel, p. 2763 | Person fixed effects regression shows monotone rise then fall; 1990s comparison (Ameriks and Zeldes (2004)) shows opposite pattern; McKenzie (2006) double-differencing confirms the hump |
| R3 | **Younger cohorts hold higher equity shares at every overlapping age**; each cohort born later has 15-20pp more in equities by 2018 than those born around 1945 | Figure 7, p. 2760; Figure 8, p. 2761 | Monotone cohort shift in equity shares for births before age 40; cohorts with high initial TDF share show steeper hump-shaped profiles |
| R4 | **TDF adoption as QDIA (PPA 2006) raises equity share of young new enrollees by ~5.5pp (age 25-35) and ~6pp for low-income workers** | Table IV col. (1) and (3), pp. 2766-2767 | Treated coefficient 0.0552 (SE 0.0907) for full sample; 0.0599 bottom income tercile; <2% for top income tercile; firm fixed effects DiD, two-year window |
| R5 | **Same TDF default reduces equity share of older new enrollees by ~13pp (age 55-65)**, consistent with TDF glidepath moving near-retirees out of stocks | Table IV col. (1), pp. 2766-2767 | Interaction Age 55 to 65 x Treatment: -0.1325 (SE 0.0012); effect is robust to controlling for income and restricting to those with no prior retirement assets |
| R6 | **Medium-run (5-year) effect: treated young workers' 5-year coefficient 0.0134 (~1.3pp above control); treated older workers' 5-year coefficient -0.0564 (~5.6pp below control)**, declining from year-1 peak/trough as control group converges voluntarily | Table V col. (4) and (7), pp. 2770-2771 | Year-0 through Year-5 treatment interaction coefficients trace declining but persistent gap; paper text approximates these as "~3%" (young) and "~2%" (old), likely based on Figure 10 predicted-equity-share comparisons |
| R7 | **Retirement contribution rates rise ~4-5pp over working lives and are stable across cohorts; PPA had a transitory negative effect of -0.4% to -1.2% on contribution rates, fading to near zero after five years** | Figure 11, pp. 2774-2775; Table VI col. (1), p. 2778; Table VII col. (1), p. 2780 | Realized contribution rate increases from ~4.6% at age 25 to ~8.5% at age 65 (cross-section); within-person increase ~5%; PPA DiD coefficient -0.0043 at year of treatment, converges to ~0 by year 5 |

**Overall (paper's conclusion).** The rise of TDFs following the PPA of 2006 caused middle-class
American investors to hold more equity earlier in their careers and to progressively de-risk as
they approach retirement, bringing the life-cycle portfolio profile closer to prescriptive
life-cycle models. This rebalancing occurred largely via portfolio composition changes, not
changes in saving rates. The PPA provisions intended to raise contribution rates had little
lasting effect, leaving open whether regulatory design of retirement plans is an effective tool
for increasing saving quantities.

## Theory / model

The paper has no formal utility or equilibrium model; it instead tests hypotheses derived from
the life-cycle portfolio-choice literature against administrative panel data. The paper's
identification logic and the hypotheses it tests are as follows.

**Life-cycle portfolio hypotheses.** The paper is motivated by Campbell (2016), who surveys how
financial product design and regulation can improve household financial well-being.
Classical models (Merton (1969), Samuelson (1969)) imply
constant portfolio allocations in scale-invariant settings. Richer models with non-tradable
human capital that declines with age (Viceira (2001), Heaton and Lucas (2000), Campbell and
Viceira (2002), Gomes, Michaelides, and Zhang (2020)) recommend reducing risky asset holdings
over the working life. TDFs embed exactly this prescription: a glidepath that holds ~90% in
equity roughly 20 years before retirement and reduces to 40-50% at target retirement date.
The paper's first hypothesis is that current life-cycle profiles of equity shares are broadly
consistent with these prescriptions, in contrast to the 1990s patterns documented by Ameriks
and Zeldes (2004).

**PPA identification assumption.** The Pension Protection Act of 2006 permitted TDFs as
Qualified Default Investment Alternatives (QDIAs) in employer-sponsored defined-contribution
plans. The key assumption is that employees' employment decisions were not affected by whether
their employer adopted a TDF as QDIA: workers were typically unaware of plan feature changes
at the time of hiring, chose jobs on many other dimensions, and employer selection of a TDF
default was driven by liability concerns (the safe harbor provision), not worker characteristics
(pp. 2764-2765). Workers at the same employer enrolling in the two years before the switch serve
as the control group; those enrolling in the two years after serve as the treated group.
The design follows the tradition of Madrian and Shea (2001), who showed that default investment
options have large effects on 401(k) choices. Mitchell and Utkus (2022) use Vanguard data to
document similar TDF effects; this paper extends that work using a different large institution
and focusing on life-cycle patterns and causal PPA effects.

**Contribution rate hypotheses.** Optimal saving models (Gomes et al. (2018), Poterba (2014))
predict significant shortfalls in U.S. retirement saving. The paper tests whether the PPA's
provisions intended to raise saving (autoenrollment, autoescalation) had measurable effects on
the realized rate at which employees saved. Broader aggregate implications of TDF growth are
analyzed in Parker, Schoar and Sun (2023).

## Method

The main empirical strategy is a difference-in-differences (DiD) design exploiting the Pension
Protection Act of 2006. The two estimating equations are given in Sections III.A and III.B of
the paper.

**Short-run DiD (equation 2, p. 2765).** For workers starting a new job between 2005 and 2008
and observed for the first two years, the specification is:

$$
y_{ift} = \beta_1 \times D_{\text{treated}} + \beta_2 \times D_{\text{treated}} \times \text{AgeEnrolled}_i
+ \beta_3 \times \text{AgeEnrolled}_i + \lambda_f + \epsilon_{ift}, \tag{2}
$$

where $$y_{ift}$$ is the portfolio equity share (or reported contribution rate) of individual
$$i$$ starting at firm $$f$$ in year $$t = 0$$; $$D_{\text{treated}}$$ equals one if the worker
enrolled after the firm adopted a TDF as its default (in 2007 or 2008); $$\text{AgeEnrolled}_i$$
is a vector of 10-year age-group indicators at enrollment, included both alone and interacted
with the treatment to capture the age-heterogeneous TDF glidepath effect; and $$\lambda_f$$ is
a firm fixed effect so the comparison is within-employer across the two cohorts. Standard errors
are clustered at the household level.

**Medium-run DiD (equation 3, p. 2769).** To track dynamics over five years after enrollment:

$$
y_{ift} = \beta_1 \times D_{\text{treated}} + \beta_2 \times D_{\text{treated}} \times \text{AgeEnrolled}_i
+ \beta_3 \times \text{AgeEnrolled}_i
+ \beta_4 \times D_{\text{treated}} \times \lambda_t + \beta_5 \times \lambda_t + \lambda_f + \epsilon_{ift}, \tag{3}
$$

where $$\lambda_t$$ are year fixed effects and their interaction with treatment captures how the
treatment gap evolves year by year. Separate regressions by age group replace the interacted
$$\text{AgeEnrolled}$$ terms.

**Life-cycle descriptive regressions (equation 1, p. 2756).** Cross-sectional and within-person
regressions of equity share on age-group indicators document the cross-sectional age profile and
the within-cohort life-cycle hump:

$$
y_{it} = \boldsymbol{\beta}_1' \mathbf{Age}_{it} + \beta_2 \, Inc_{it} + \epsilon_{it}, \tag{1}
$$

where $$\mathbf{Age}_{it}$$ is a vector of three-year age-group indicators and $$Inc_{it}$$ is
the log deviation of the individual's income from the sample mean income. Person fixed effects
are added for the within-person version (Figure 6, Figure 11 Panel B). The McKenzie (2006)
double-differencing method is also applied as a robustness check to recover pure age effects
free of cohort and time effects (Internet Appendix Section II).

## Empirical specifications

**Descriptive life-cycle profiles (R1, R2, R3).** The full RI sample of investors aged 25-65
observed annually from 2006 to 2018 (millions of individual-year observations). The cross-
sectional regression (eq. 1) uses age-group dummies with and without a log-income control;
the within-person version adds person fixed effects. Cohort analysis splits by 10-year birth
cohorts (Figure 7). For R2, the McKenzie (2006) approach differences within-cohort over
adjacent ages, then differences again over time, to eliminate cohort and time effects and
identify the second partial derivative of the age profile (Internet Appendix II). Standard
errors are clustered at the individual level (and at the employer level in robustness checks,
Internet Appendix Table IA.XI).

**Short-run PPA DiD (R4, R5).** Sample restricted to workers who started a new job 2005-2008,
observed for two years. Treatment defined as enrollment in 2007 or 2008 at an employer that
switched its default to a TDF. Control: enrollment in 2005 or 2006 at the same employer.
Firm fixed effects absorb all employer-level differences. The key identifying variation is the
timing of the plan-level switch relative to enrollment date. Columns (3)-(4) of Table IV
repeat the analysis by income tercile; columns (5)-(6) restrict to those with no prior
retirement assets at the institution. The portfolio equity share is the dependent variable
for R4 and R5; the reported contribution rate for R7.

**Medium-run PPA DiD (R6, R7).** Same base sample, extended to track individuals for five
years after enrollment. Year-of-treatment and year-after interactions (eq. 3) trace convergence
between treated and control. Columns (4) and (7) of Table V split by age at enrollment (25-34
vs. 55-65); columns (4) and (7) of Table VII do the same for contribution rates. Standard
errors are clustered at the household level throughout.

**Robustness checks.** (i) Restricting the contribution-rate PPA sample to 2007 enrollees
only (Table IA.XXIV) to reduce financial-crisis confounds. (ii) Using price-constant equity
shares that ignore passive price appreciation (Internet Appendix Table IA.IX). (iii) Repeating
DiD with standard errors clustered at the employer (Table IA.XVII). (iv) The ex-ante designated
equity share as an alternative equity-share measure (Table IA.X).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Proprietary account-level administrative data from a large U.S. financial services company | Primary data: individual portfolios, contribution rates, demographics, employer identifier, 2006-2018 | No page yet |
| Survey of Consumer Finances (SCF), 2016 wave | Comparison sample of U.S. retirement investors (RIs) for calibration and validation of representativeness | No page yet |
| Administrative data from Ameriks and Zeldes (2004) | 1990s comparison for life-cycle equity share patterns | No page yet |

The paper's headline results are derived entirely from proprietary account-level data provided by
a single unnamed financial services firm. Reproducing the results requires access to that
confidential dataset, which is not publicly available.

Sample scope: investors aged 25-65 with retirement wealth in the middle 80% of the age-adjusted
distribution (retirement investors, RIs), observed annually from December 2006 to December 2018.
Sample covers millions of individuals and trillions of dollars in investable wealth (Table II,
p. 2750).

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13473) if you are:
studying the design of 401(k) plans and the life-cycle portfolio implications of TDF defaults;
calibrating or testing life-cycle portfolio-choice or saving models against administrative
microdata; investigating the effects of the Pension Protection Act of 2006 on investor behavior;
or interested in the representativeness of SCF survey data relative to administrative data on
portfolio equity shares. The Internet Appendix (available on the Journal of Finance website)
contains 25+ robustness tables, estimation moments, and the McKenzie (2006) double-differencing
reconstruction.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was extracted by an
LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY 4.0
licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Parker, Jonathan A., Antoinette Schoar, Allison Cole, and
> Duncan Simester. "Household Portfolios and Retirement Saving over the Life Cycle."
> *The Journal of Finance* 80, no. 5 (October 2025): 2739-2787.
> DOI: 10.1111/jofi.13473. (C) 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
