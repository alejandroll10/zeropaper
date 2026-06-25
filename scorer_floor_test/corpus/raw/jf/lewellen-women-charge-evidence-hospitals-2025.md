---
title: "Women in Charge: Lewellen (2025)"
description: >-
  Distilled: Female hospital CEOs make similar financial and investment decisions
  as male peers, respond identically to the 2008 financial crisis, but earn 32%
  lower pay (shrinking to 7.8% within-hospital) and face significantly higher
  turnover after poor performance. J. Finance 2025, paywalled. Seven core results
  with source locators, datasets used, and the empirical specifications.
sidebar:
  label: Lewellen 2025
  order: 1
tags: [paper-summary, labor-careers-health, corporate-governance, gender, executive-compensation,
       ceo-turnover, nonprofit, panel-regression, probit-regression, matching, peer-reviewed,
       unreplicated,
       data:irs-form-990, data:aha-annual-survey, data:hcris, data:dartmouth-atlas, data:cms-quality]
paper:
  authors: Katharina Lewellen
  authorList:
    - { family: Lewellen, given: Katharina, affiliation: Tuck School of Business at Dartmouth }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2199–2253
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13455
  jel:
    codes: [J33, J71, G34]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Gender, Labor, and Family Dynamics
    - Gender Diversity and Inequality
    - Work-Family Balance Challenges
  dataAccess: licensed-commercial
  outcome:
    - female CEO indicator (hospital-CEO matching)
    - hospital financial and investment policies
    - log CEO pay (gender pay gap)
    - pay-for-performance sensitivity
    - CEO turnover probability
  outcomeClass: [labor-careers-health, firm-real-outcomes]
  license: >-
    Wiley Terms and Conditions (version of record); not CC licensed.
    Confirmed via Crossref DOI metadata: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-04-26.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site; confirmed paywalled via Crossref licence metadata 2026-06-05)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 6
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, probit-regression, matching, difference-in-differences]
    identification: natural-experiment
  contributionType: [new-fact, new-data]
  mechanisms: [agency, information-asymmetry]
  introducesData: true
  scope:
    region: US
    assetClass: nonprofit hospitals
    period: 2000-01..2018-12
    frequency: annual
    dataType: [administrative, accounting]
    granularity: [firm, individual]
    n: "25,762 hospital-years (1,981 hospitals); 4,353 CEOs (819 female)"
  findings:
    - ref: R1
      outcome: hospital financing and investment policies (female CEO indicator)
      metric: coefficient
      value: "all coefficients on leverage, cash/assets, securities/assets, investment statistically insignificant across all specifications; can reject decline > 0.70 pp in cash/assets (col. 2 Table II)"
      direction: none
      vsBenchmark: no difference between male and female CEO hospitals in any financial policy
    - ref: R2
      outcome: hospital tilt toward less profitable patients (female CEO indicator)
      metric: coefficient
      value: "Medicaid Ratio, Charity Care, Medicare Ratio all insignificant with hospital FE; Contributions positive at 10% level (0.83 pp per 1-SD increase, col. 8 Table III)"
      direction: none
      vsBenchmark: no systematic tilt toward benevolence-aligned policies
    - ref: R3
      outcome: hospital performance and investment around 2008 financial crisis
      metric: coefficient
      value: "Post_Crisis x Female CEO: growth in services -0.001 (0.008), profit margin -0.003 (0.006), investment -0.002 (0.028); all insignificant (Panel A, Table V)"
      direction: none
      vsBenchmark: "female-led hospitals cut revenues 3.0 pp vs 2.9 pp for males; investment 7.2 pp vs 6.9 pp; all differences insignificant"
    - ref: R4
      outcome: log CEO pay (gender pay gap)
      metric: coefficient
      value: "unconditional gap: -0.322*** (0.037); controlling for size: -0.125*** (0.022); with hospital FE and controls: -0.078** (0.032) (Table VII col. 1-5)"
      direction: negative
      vsBenchmark: "gap of 32.2% unconditional; 12.5% after size control; 7.8% within-hospital with full controls"
    - ref: R5
      outcome: pay-for-performance sensitivity (log CEO pay)
      metric: coefficient
      value: "Female CEO x Perf_Quintile5 (Best): -0.096** (0.046) in col. 4; -0.105** (0.048) with CEO age dummies in col. 5 (Table VIII); gap in PFP: 15.0 pp men vs 5.3 pp women (bottom to top quintile)"
      direction: negative
      vsBenchmark: "men: pay rises 15.0 pp from worst to best quintile; women: 5.3 pp; interaction significant at 5%"
    - ref: R6
      outcome: CEO forced turnover probability
      metric: pp-effect
      value: "Female CEO x Perf_Quintile1 (Worst): marginal effect 3.6 pp higher for women (col. 4 Table IX, significant at 5%); all-turnover gap: 3.2 pp (col. 8 Table IX)"
      direction: positive
      vsBenchmark: "spread in marginal effects bottom-to-top quintile: 5.6 pp for women vs 2.7 pp for men (forced); 8.2 pp vs 4.3 pp (all turnovers)"
    - ref: R7
      outcome: female representation on hospital boards and female CEO share
      metric: coefficient
      value: "Female Directors Non-CEO: 0.146*** (0.043) without hospital FE (col. 2 Table X Panel A); 0.011 (0.034) with hospital FE (col. 4); gender gap in pay not significantly smaller with more female directors (Table X Panel B)"
      direction: none
      vsBenchmark: "correlation disappears with hospital FE; no evidence female boards reduce the gender pay gap"
  resultType: new-finding
  relatesTo:
    - { cite: "Faccio, Marchica & Mura (2016)", relation: contradicts, note: "European private firms led by women take less risk; this paper finds no such effect for US hospital CEOs" }
    - { cite: "Huang & Kisgen (2013)", relation: contradicts, note: "S&P 1500 female executives make fewer acquisitions and less debt; hospital evidence shows no such financing differences" }
    - { cite: "Matsa & Miller (2013)", relation: tests, note: "Norwegian board quota causes labor hoarding; hospital evidence finds no analogous benevolence effect on employment or patient mix" }
    - { cite: "Bertrand & Hallock (2001)", relation: extends, note: "gender gap in top executive pay; paper documents same gap at CEO level in a single-industry panel" }
    - { cite: "Adelino, Lewellen & McCartney (2021)", relation: builds-on, note: "hospital financial health and clinical choices; uses same IRS Form 990 + AHA data infrastructure" }
    - { cite: "Adelino, Lewellen & Sundaram (2015)", relation: builds-on, note: "investment decisions of nonprofit firms from hospitals; same setting" }
  openQuestions:
    - "Whether the pay and turnover patterns reflect true productivity differences versus biased beliefs cannot be determined empirically; the paper cannot disentangle these mechanisms (pp. 2234-2235)."
    - "Whether findings generalize beyond nonprofit hospitals to for-profit firms or other industries, given the unique features of the hospital labor market (p. 2204)."
    - "The analysis does not account for CEO negotiation behavior differences, which could contribute to both the pay gap and the turnover patterns, beyond what controls capture (p. 2227)."
  proposedVocab:
    - { axis: topic, term: nonprofit-governance, def: "Corporate governance of nonprofit organizations: CEO selection, compensation, turnover, board composition, and fiduciary duties in the absence of shareholders.", aliases: [nonprofit-ceo-governance, hospital-governance] }
    - { axis: topic, term: gender-pay-gap, def: "Empirical literature on the difference in compensation between male and female workers, including within-firm and executive-level gaps and their decomposition.", aliases: [gender-wage-gap, executive-gender-gap] }
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: >-
        Full text read (pp. 2199-2253, all tables and figures). Seven results
        extracted from the source PDF. Not human-verified. Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; three fixes applied: (1) R7 col. 4 coefficient sign corrected from -0.011 to 0.011 (Table X Panel A shows positive 0.011); (2) dataAccess corrected from hand-collected to licensed-commercial (AHA Annual Survey is the most restrictive source); (3) blinder-oaxaca-decomposition removed from buildsFrom (not used in the paper)."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13455
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-04-26; paywalled (not CC)"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the datasets it assembles, and the
empirical specifications behind the compensation and turnover findings: enough
to know what it found and how, without reading all 55 pages. To replicate or
extend it, read the full source at [doi:10.1111/jofi.13455](https://doi.org/10.1111/jofi.13455).

## TL;DR

The paper uses 19 years of IRS Form 990 filings for U.S. nonprofit hospitals
(2000-2018) to study female hospital CEOs: what kinds of hospitals they lead,
how they make decisions under stress, and how boards compensate and replace them.
Contrary to the gender-differences literature, female CEOs do not run hospitals
with safer financing, lower investment, or more charitable orientation, and they
respond to the 2008 financial crisis identically to male peers. However, female
CEOs earn 32% lower unconditional pay (7.8% within hospital after controls),
receive flatter pay-for-performance incentives (5.3 pp vs. 15.0 pp pay rise from
bottom to top performance quintile), and are fired more often after poor
performance (3.6 pp higher departure rate in the bottom quintile). The patterns
are consistent with hospital boards perceiving female CEOs as less productive,
whether due to true differences or biased beliefs.

## Core results

Magnitudes and significance are as reported in source tables; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **No evidence female CEOs match or shift hospitals toward safer financing or lower investment**: coefficients on leverage, cash, securities, and investment are statistically insignificant across all specifications | Table II, pp. 2212, 2214 | One-SD increase in leverage raises female CEO probability by an insignificant 0.48 pp (col. 2); can reject a decline of more than 0.70 pp; similar bounds for cash and investment |
| R2 | **No evidence female CEOs lead hospitals with greater charitable orientation**: Medicaid Ratio, Charity Care, and Medicare Ratio are all insignificant with hospital FE; Contributions positive at 10% | Table III, pp. 2213, 2215-2217 | Contributions coefficient: 0.83 pp per 1-SD increase (col. 8); all other benevolence measures insignificant within hospital |
| R3 | **Hospitals with male and female CEOs respond identically to the 2008 financial crisis**: interaction Post\_Crisis x Female is insignificant for revenue, profit margin, investment, employment, salaries, and Medicaid Ratio | Table V, pp. 2221-2222; Figure 3, p. 2222 | Female hospitals cut revenue by 3.0 pp, males by 2.9 pp; profit margin declines 1.6 pp vs. 1.3 pp; investment 7.2 pp vs. 6.9 pp; none of the differences is significant |
| R4 | **Female CEOs earn substantially lower pay**: unconditional gap is 32.2%, falling to 12.5% after controlling for hospital size, and further to 7.8% with hospital FE and full controls | Table VII, p. 2225; Table VI, p. 2224 | Female CEO coefficient: -0.322\*\*\* (col. 1), -0.125\*\*\* (col. 2), -0.078\*\* (col. 5) in log pay regressions |
| R5 | **Pay-for-performance sensitivity is significantly flatter for female than male CEOs**: men's pay rises 15.0 pp from worst to best performance quintile; women's only 5.3 pp | Table VIII, p. 2229; Figure 4, p. 2230 | Female CEO x Perf\_Quintile5: -0.096\*\* (0.046) in col. 4; -0.105\*\* (0.048) with age dummies in col. 5 |
| R6 | **Turnover-performance sensitivity is significantly higher for female CEOs**: incremental departure rate in the bottom quintile is 3.6 pp higher for women than men (forced turnover); 3.2 pp for all turnovers | Table IX, pp. 2232-2233; Figure 5, p. 2233 | Marginal effect of Female CEO x Perf\_Quintile1: 3.6 pp (col. 4, forced, significant at 5%); 3.2 pp (col. 8, all turnovers, significant at 5%) |
| R7 | **Board gender composition does not explain the pay gap**: correlation between female board share and female CEO indicator disappears with hospital FE; the gap is not systematically smaller where female trustees are more common | Table X, pp. 2238-2239 | Female Directors Non-CEO: 0.146\*\*\* (col. 2) without FE; 0.011 (col. 4) with hospital FE; Panel B interaction with gender pay gap insignificant |

**Overall (paper's conclusion).** Hospitals led by male and female CEOs look
similar on observable financial and operational measures, pursue similar
strategies, and respond similarly to external shocks. At the same time,
compensation and turnover decisions are made as though female CEOs are less
productive: they receive lower pay, flatter incentives, and steeper
performance-conditioned dismissal probabilities. The evidence is consistent with
boards holding biased beliefs about CEO ability, though true productivity
differences cannot be ruled out.

## Theory / model

The paper has no formal structural model. The tests are motivated by two classes
of theory:

**Agency and efficiency benchmark for pay.** The paper follows the assignment
models of CEO compensation (Gabaix and Landier (2008), Tervio (2008)) as an
efficiency benchmark: in competitive markets for CEO talent, pay reflects the
CEO's marginal product of skill. A gender gap in pay, under this lens, reflects
a perceived productivity difference. Boards may correctly assess CEO ability
(true skill gap) or may hold biased priors (stereotype-based beliefs), consistent
with Bayesian learning models of CEO turnover (Hermalin and Weisbach (1998),
Taylor (2010)). The unconditional gender gap documented here is broadly consistent
with the findings of Bertrand and Hallock (2001) for S&P 1500 executives, extended
here to the CEO level within a single industry over a longer panel.

**Principal-agent incentive theory.** The moral hazard framework of Holmstrom
and Milgrom (1987) predicts that optimal incentive steepness (pay-for-performance
sensitivity) is higher for less risk-averse, higher-effort, or higher-productivity
CEOs. Flatter incentives for women are consistent with boards perceiving them as
more risk-averse or less productive. The matching between CEO type and board
beliefs also predicts lower firing thresholds for lower-prior-ability CEOs, which
is consistent with the finding that female CEOs are fired more often at the bottom
of the performance distribution.

**Identification.** The core hospital-level regressions exploit within-hospital
variation over time (hospital fixed effects) to absorb time-invariant confounders.
For the financial crisis analysis, k-nearest-neighbor matching on 2007 hospital
attributes creates treatment and control samples that are balanced on observables
immediately prior to the shock, attenuating concerns about selection on trends.
The crisis itself is a plausibly exogenous, unexpected shock to hospital finances
(stock market crash, credit crunch, demand decline via unemployment) that
provides a high-stakes setting where CEO preferences, if present, should be most
visible. The data infrastructure for the crisis analysis follows Adelino,
Lewellen, and McCartney (2021) and Adelino, Lewellen, and Sundaram (2015),
who also use IRS Form 990 and AHA data to study hospital investment and governance
decisions.

The results contradict prior evidence from European private-firm samples. Faccio,
Marchica, and Mura (2016) find that firms led by female CEOs take less risk and
choose safer financing; Huang and Kisgen (2013) find that female executives make
fewer acquisitions and issue less debt. The hospital evidence shows no such
financing or investment differences, consistent with the view that self-selection
into top executive roles reduces or eliminates gender differences in behavior
documented in broader populations (Adams and Funk (2012)). Similarly, Matsa and
Miller (2013) find that Norwegian board quotas lead to labor hoarding, interpreted
as a benevolence effect of female board members; the hospital tests of Medicaid
mix, charity care, and employment response to the crisis find no analogous channel.

## Method

**Hospital fixed-effects panel regressions (Tables II, III, VII, VIII).** The
main estimating equation across all parts of the paper is:

$$
Y_{ht} = \alpha + \beta \, \text{Female}_{ht} + \gamma X_{ht-1} + \mu_h + \tau_t + \varepsilon_{ht} \tag{1}
$$

where $$Y_{ht}$$ is an outcome for hospital $$h$$ in year $$t$$ (leverage, log CEO pay,
Charity Care, etc.), $$\text{Female}_{ht}$$ is an indicator for a female CEO,
$$X_{ht-1}$$ is a vector of lagged hospital controls (log service revenues, profit
margin, growth in services, contributions, density decile of the HSA, system
membership, CEO tenure, and multiple positions), and $$\mu_h$$ and $$\tau_t$$ are
hospital and year fixed effects. Standard errors are clustered at the hospital
level throughout. The coefficient $$\beta$$ identifies the effect from
within-hospital CEO gender transitions (pp. 2213-2214, 2225).

**Matching + DiD for the financial crisis (Table V).** For the crisis test, the
paper constructs a matched sample using k-nearest-neighbor matching ($$k = 3$$,
matching with replacement) on 2007 hospital attributes: service revenues, HSA
population density rank, investment, revenue growth, and system membership.
The matched sample has 134 treated (female CEO in 2007) and 271 control (male CEO
in 2007) hospitals. The estimating equation is:

$$
Y_{ht} = \alpha + \delta \, (\text{Female}_h \times \text{Post\_Crisis}_t) + \mu_h + \tau_t + \varepsilon_{ht} \tag{2}
$$

estimated on the window 2006-2011, where $$\text{Post\_Crisis}_t = 1$$ for 2009-2011.
The coefficient $$\delta$$ is identified from the differential within-hospital change
from pre- to post-crisis between the matched treatment and control groups,
a difference-in-differences design (p. 2220).

**Probit for CEO turnover (Table IX).** The turnover regressions are probit models:

$$
\Pr(\text{Turnover}_{ht} = 1) = \Phi\!\left( \alpha + \beta_1 \, \text{Female}_{ht} + \sum_{q=1}^{4} \beta_q \, \text{Perf\_Quintile}_{qht} + \gamma \, (\text{Female}_{ht} \times \text{Perf\_Quintile1}_{ht}) + \delta X_{ht} + \mu_h + \tau_t \right) \tag{3}
$$

where $$\Phi$$ is the standard normal CDF, performance quintiles are formed by year
and hospital size bin based on the lagged profit margin (Perf\_Quintile5 = best
is excluded; Perf\_Quintile1 = worst is the main interaction), and the equation
is estimated separately for forced turnover (CEO aged 60 or younger at departure)
and all turnover. Marginal effects are reported (pp. 2231-2234).

**Pay-for-performance regressions (Table VIII).** The pay sensitivity analysis
runs OLS of log CEO pay on female dummy, performance quintile indicators, and
their interactions:

$$
\ln(\text{CEO Pay}_{ht}) = \alpha + \beta_1 \, \text{Female}_{ht} + \sum_{q=2}^{5} \beta_q \, \text{Perf\_Quintile}_{qht} + \sum_{q=2}^{5} \gamma_q \, (\text{Female}_{ht} \times \text{Perf\_Quintile}_{qht}) + \delta X_{ht} + \mu_h + \tau_t + \varepsilon_{ht} \tag{4}
$$

where $$\gamma_5$$ on the Female x Perf\_Quintile5 interaction captures the
differential pay-performance slope at the top of the distribution (pp. 2228-2230,
Table VIII).

## Empirical specifications

- **Matching and selection tests (Tables II, III, Sections IV and V).** Panel OLS
  (equation 1) with and without hospital FE; sample 23,611 to 25,513 hospital-years
  depending on completeness. Controls include log service revenue, profit margin,
  growth in services, density HSA, competition rank. Tables II and III report
  coefficients on the female CEO indicator for financial risk (leverage,
  cash/assets, securities/assets, investment) and patient orientation (Medicaid,
  Medicare, Charity Care, Contributions) respectively. The within-hospital
  specifications (cols. with hospital FE) are the headline tests.

- **Financial crisis DiD (Table V).** Matched sample, 2006-2011, hospital and year
  FE, N = 2,251-2,287 hospital-years depending on variable. Dependent variables:
  growth in services, profit margin, investment, growth in personnel, growth in
  salaries, Medicaid Ratio. The interaction Post\_Crisis x Female is the parameter
  of interest in Panel A; Panels B and C show results separately for the treatment
  and control samples.

- **Gender pay gap (Table VII).** Log CEO pay on Female CEO indicator, year FE,
  progressively adding: log service revenues (col. 2), full hospital controls (col.
  3), density and system dummies (col. 4), hospital FE (col. 5), CEO age dummies.
  N = 16,193-20,520 hospital-years depending on pay data availability. Panel B
  replicates for the post-2008 consistent-reporting subsample (2009-2018).

- **Pay-for-performance (Table VIII).** OLS (equation 4), hospital and year FE,
  full controls including tenure and multiple positions; N = 16,193-18,066. Profit
  margin quintiles defined within year x hospital size bin. Robustness: Table
  IA.V adds interactions with size and HSA density to test whether urban/size
  confounds drive the result; coefficients remain significant.

- **Turnover-performance (Table IX).** Probit (equation 3), hospital and year FE,
  full controls; forced turnover sample (age 60 or younger) N = 3,176-18,348; all
  turnover N = 4,030-24,314. Marginal effects reported for Female CEO and the key
  interaction Female CEO x Perf\_Quintile1. Robustness: Table IA.VI includes
  hospital size and density interactions; Table IA.VII documents subsequent career
  outcomes of departing CEOs (11% of male departures become CEOs elsewhere vs.
  6% for female departures, differences often significant).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| IRS Form 990 filings (via Candid/Guidestar 1999-2014; IRS website 2015-2018) | Primary source for hospital financials, CEO/officer names, titles, salaries, board composition; 2000-2018 | [IRS Form 990](/wiki/datasets/irs-form-990/) |
| AHA Annual Survey Database (Dartmouth Institute, 2000-2018) | Hospital services, operations, system affiliation | [AHA Annual Survey](/wiki/licensed/aha-annual-survey/) (licensed) |
| Healthcare Cost Report Information System (HCRIS / CMS, 2011-2018) | Charity Care and Uninsured Discounts spending | [HCRIS](/wiki/datasets/hcris/) |
| Dartmouth Atlas of Health Care | Hospital Service Area (HSA) geographic market definitions; demographic characteristics from 2010 U.S. Census | [Dartmouth Atlas](/wiki/datasets/dartmouth-atlas/) |
| CMS patient outcome metrics (mortality, readmissions, patient satisfaction) | Nonfinancial hospital performance proxies used in supplementary tests; available from 2008-2009 | [CMS quality](/wiki/datasets/cms-quality/) |
| Radaris, LinkedIn, hospital websites (manual collection) | CEO biographical data (age, education, career history) for a subsample of 2,202 CEOs | no page yet |

Sample: 1,981 hospitals and 25,762 hospital-years from 2000 to 2018; 4,353 CEOs
(819 female). Financial ratios are winsorized at the 2% level. CEO compensation
data cover approximately 80% of hospital-year observations. The matched crisis
sample covers 134 female and 271 male CEO hospitals, observed 2006-2011.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13455) if you are: researching
gender gaps in executive compensation or turnover (Tables VII, VIII, IX have
precise specifications and robustness); building on the nonprofit hospital
setting (Internet Appendix Section II has a detailed comparison with for-profit
CEO markets); extending the analysis to other nonprofit sectors; studying
how boards update beliefs about CEO quality (the discussion in Section VI.D
synthesizes the compensation and turnover patterns against learning and agency
theories); or investigating whether board gender composition affects executive
gender outcomes (Table X and the negative result on female directors, Section VII).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4), August 2025, pp. 2199-2253.
Publisher: Wiley on behalf of the American Finance Association. DOI:
10.1111/jofi.13455. Licensed under Wiley Terms and Conditions (paywalled; not
CC licensed). This distillation was extracted by an LLM on 2026-06-05 and is
**not human-verified or independently reproduced**. Extract-only: no PDF hosted.

> Lewellen, Katharina. "Women in Charge: Evidence from Hospitals."
> *The Journal of Finance* 80, no. 4 (August 2025): 2199-2253.
> DOI: 10.1111/jofi.13455. © 2025 the American Finance Association.
