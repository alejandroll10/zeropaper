---
title: "The Stock Market and Bank Risk-Taking: Falato & Scharfstein (2025)"
description: >-
  Distilled: Banks that go public (IPO) increase risk as measured by confidential
  CAMELS supervisory ratings, relative to a matched control group of banks that
  filed but withdrew their IPOs. The increase in risk boosts short-term ROE but
  reduces it four years out, consistent with stock-market short-termism driving
  bank risk. J. Finance 2025, paywalled. Eight core results with source locators,
  datasets, the theoretical mechanism (Stein 1989 short-termism), and the
  difference-in-differences estimating equations.
sidebar:
  label: Falato-Scharfstein 2025
  order: 1
tags: [paper-summary, banking, risk-taking, short-termism, corporate-governance,
       difference-in-differences, panel-regression, instrumental-variables,
       peer-reviewed, unreplicated,
       data:nic-fed, data:stbl-fed, data:call-reports, data:ibes, data:thomson-13f]
paper:
  authors: Antonio Falato, David Scharfstein
  authorList:
    - { family: Falato, given: Antonio, affiliation: Federal Reserve Board }
    - { family: Scharfstein, given: David, affiliation: Harvard Business School and NBER }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3223–3261
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13502
  jel:
    codes: [G21, G32, G34]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Financial Markets and Investment Strategies
    - Banking stability, regulation, efficiency
    - Insurance and Financial Risk Management
  dataAccess: proprietary-confidential
  outcome:
    - composite CAMELS supervisory rating
    - likelihood of a weak CAMELS rating
    - bank asset quality (A rating in CAMELS)
    - STBL loan risk rating
    - Tier 1 capital ratio
    - volatile liabilities ratio
    - return on equity (short-run and long-run)
  outcomeClass: [credit-risk, bank-funding, firm-real-outcomes]
  license: >-
    Wiley standard terms-of-use (paywalled; not CC); license block in Crossref
    DOI metadata: content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-10-06
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/JF site; confirmed via Crossref metadata 2026-06-03)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 1
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, instrumental-variables, panel-regression, matching]
    identification: natural-experiment
  contributionType: [new-fact]
  mechanisms: [behavioral-bias, agency]
  scope:
    region: US
    assetClass: US commercial banks (depository institutions)
    period: 1990-01..2012-12
    frequency: quarterly
    dataType: [market, accounting, administrative]
    granularity: [firm, transaction]
    n: "178,980 bank-quarters (7,166 banks); IPO sample 8,237 bank-quarters (276 BHCs)"
  relatesTo:
    - { cite: 'Stein (1989)', doi: '10.2307/2937861', relation: tests, note: 'the paper tests the short-termism prediction that public market pressure induces managers to boost short-run earnings at the expense of long-run value' }
    - { cite: 'Bernstein (2015)', doi: '10.1111/jofi.12275', relation: builds-on, note: 'follows Bernstein (2015) in using withdrawn IPO filings as the control group for identifying IPO effects on firm behavior' }
    - { cite: 'Seru (2014)', doi: '10.1016/j.jfineco.2013.11.001', relation: builds-on, note: 'follows Seru (2014) in the DD identification logic of comparing firms that completed versus withdrew transactions' }
    - { cite: 'Bolton, Scheinkman & Xiong (2006)', doi: '10.1111/j.1467-937X.2006.00388.x', relation: builds-on, note: 'equity compensation leads to short-termism when managers exploit market overvaluation of short-term performance' }
    - { cite: 'Kwan (2004)', relation: contradicts, note: 'earlier cross-sectional study finds no significant risk differences by ownership status, possibly because it uses ex-post performance rather than ex-ante supervisory CAMELS ratings' }
    - { cite: 'DellAriccia, Laeven & Suarez (2017)', doi: '10.1111/jofi.12467', relation: cites, note: 'cited for using STBL loan risk data in banking research' }
    - { cite: 'Brochet, Loumioti & Serafeim (2015)', doi: '10.1007/s11142-015-9329-8', relation: builds-on, note: 'CEO Short-Term Disclosure measure based on frequency of short-term horizon words on earnings calls and in 10-K filings' }
  openQuestions:
    - 'What effect does the increase in risk-taking incentives of publicly traded banks have on privately held banks? If public banks increase credit supply, private banks may respond by taking more risk to compete, or reduce supply to stabilize (p. 3254).'
    - 'Do similar stock-market risk-taking incentives exist in other nonbank financial intermediaries such as institutional bond funds and insurance companies? (p. 3254).'
    - 'What are the regulatory implications? Should compensation schemes require managers to hold stock for longer periods to mitigate short-term risk-taking incentives, and is the risk documented here socially excessive? (pp. 3254-3255).'
  findings:
    - { ref: R1, outcome: composite CAMELS supervisory rating, metric: coefficient, value: "0.316*** (SE 0.114); ~0.5 within-bank SD", direction: positive }
    - { ref: R2, outcome: likelihood of a weak CAMELS rating, metric: pp-effect, value: "0.088*** (SE 0.024)", direction: positive, vsBenchmark: equal to unconditional mean probability of weak CAMELS rating }
    - { ref: R3, outcome: composite CAMELS supervisory rating, metric: coefficient, value: "2SLS 0.343** (SE 0.145) composite; 0.104*** (SE 0.033) weak CAMELS", direction: positive }
    - { ref: R4, outcome: bank asset quality (A rating in CAMELS), metric: coefficient, value: "A-rating DD 0.316** (SE 0.167); STBL loan risk DD 0.403*** (SE 0.125)", direction: positive }
    - { ref: R5, outcome: Tier 1 capital ratio, metric: coefficient, value: "C,L-ratings DD 0.254** (SE 0.115); Risk-rating DD 0.308*** (SE 0.111)", direction: positive }
    - { ref: R6, outcome: volatile liabilities ratio, metric: coefficient, value: "RWA/A DD 0.371*** (SE 0.116); Tier 1 capital DD -0.010*** (SE 0.003); Volatile Liabilities DD 0.039*** (SE 0.008)", direction: mixed }
    - { ref: R7, outcome: return on equity (short-run and long-run), metric: coefficient, value: "ROE t+4q = 0.007** (SE 0.003); ROE t+16q = -0.013** (SE 0.006); E-rating DD t+16 = 0.363*** (SE 0.157); LLP/Loans DD = -0.006*** (SE 0.001)", direction: mixed }
    - { ref: R8, outcome: composite CAMELS supervisory rating, metric: coefficient, value: "Triple-DD CEO short-term disclosure 0.669** (SE 0.327); inst. investor turnover 0.071** (SE 0.029); crisis ROE interaction -0.028*** (SE 0.002)", direction: mixed }
  resultType: confirms
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Full text read (pp. 3223-3262, J. Finance vol. 80 no. 6 December 2025).
        Eight results extracted from the source PDF. Not human-verified. Not
        reproduced. Replication code is stated as available in supporting
        information.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; all
        eight core result rows confirmed correct (R1-R8 coefficients, SEs, and
        significance stars match Tables III-VIII, X); equations 1-3 and the
        triple-DD and performance-dynamics specifications verified term-by-term;
        one fix applied: Empirical specifications section incorrectly stated
        Table X Panel A used the "full 178,980 bank-quarter universe" when it
        uses the pre-crisis window (90,733 observations).
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
        introducesData, data-scope) re-checked against the source PDF; one fix
        applied - granularity corrected from [firm, security] to [firm,
        transaction] because STBL regressions use loan-level observations and
        no security-level unit of observation appears in any regression.
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
        against the source PDF; all eight entries confirmed correct - R1-R8
        coefficients, SEs, and significance stars match Tables III-VIII and X
        exactly, directions are accurate, and resultType=confirms is consistent
        with the primary relatesTo=tests edge on Stein (1989) whose prediction
        the paper supports; no fixes required.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13502
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: >-
        license[].content-version=vor,
        URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
        delay-in-days=0, start=2025-10-06. This is Wiley standard terms-of-use,
        not a Creative Commons licence. Paper is paywalled.
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the short-termism mechanism it tests,
and the difference-in-differences specifications with their equations: enough to
know what it found and how, without reading all 40 pages. To replicate or extend
it, read the full source at the [original](https://doi.org/10.1111/jofi.13502).

## TL;DR

Using confidential CAMELS supervisory ratings from the Federal Reserve, the paper
shows that banks increase risk after going public relative to a matched control
group of banks that filed for an IPO but withdrew it. The baseline difference-in-
differences (DD) estimate implies that going public raises the composite CAMELS
rating by 0.316 on a 1-5 scale (about half a within-bank standard deviation) and
raises the probability of a weak CAMELS rating (3 or above) by 8.8 percentage
points, roughly equal to the unconditional sample mean. The increase in risk
shows up both in observable balance sheet measures (higher risk-weighted assets,
less Tier 1 capital, more volatile liabilities) and in confidential supervisory
assessments that investors cannot observe, consistent with the Stein (1989) model
of short-termism in which managers boost unobservable hard-to-detect risks to
raise short-term earnings and stock prices. The risk increase is larger for banks
with higher institutional investor turnover, higher CEO short-term disclosure, and
larger equity option grants of shorter duration. Banks that went public before the
2007-2009 financial crisis underperformed significantly during the crisis.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF (page numbers from the journal article).

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Going public raises the composite CAMELS rating (higher = riskier) in the IPO sample | Table III Panel A col. (1), p. 3236 | DD coefficient = 0.316\*\*\* (SE 0.114); ~0.5 within-bank SD |
| R2 | Going public raises the probability of a weak CAMELS rating (3 or above) | Table III Panel A col. (2), p. 3236 | DD coefficient = 0.088\*\*\* (SE 0.024); equal to unconditional mean probability |
| R3 | 2SLS-IV using banking sector stock returns in the two months after announcement as instrument confirms the result | Table III Panel B cols. (1)-(2), p. 3237 | 2SLS coefficient = 0.343\*\* (SE 0.145) for composite CAMELS; 0.104\*\*\* (SE 0.033) for weak CAMELS |
| R4 | Asset risk (CAMELS A rating and STBL loan risk) rises after public transition | Table IV Panel A, p. 3242 | A-rating DD = 0.316\*\* (SE 0.167); STBL DD = 0.403\*\*\* (SE 0.125) in IPO sample |
| R5 | Financing risk (capital adequacy and liquidity in CAMELS; risk sensitivity) also rises after public transition | Table IV Panel B, p. 3242 | C,L-ratings DD = 0.254\*\* (SE 0.115); Risk-rating DD = 0.308\*\*\* (SE 0.111) in IPO sample |
| R6 | Observable balance sheet measures confirm risk increase: RWA/A rises and Tier 1 capital falls after IPO | Table V Panels A and B, p. 3244 | RWA/A DD = 0.371\*\*\* (SE 0.116); Tier 1 capital DD = -0.010\*\*\* (SE 0.003); Volatile Liabilities DD = 0.039\*\*\* (SE 0.008) |
| R7 | ROE rises 70 bps by quarter +4 but falls 130 bps below pre-transition level by year +4; earnings quality (CAMELS E) deteriorates; discretionary loan loss provisions fall post-IPO | Table VII Panels A and B, pp. 3247-3248 | ROE change at t+4 quarters = 0.007\*\* (SE 0.003); at t+16 quarters = -0.013\*\* (SE 0.006); E-rating DD at t+16 = 0.363\*\*\* (SE 0.157); LLP/Loans DD = -0.006\*\*\* (SE 0.001) |
| R8 | Risk increase is larger for banks with higher institutional investor turnover, more short-term CEO disclosure, higher equity option grant values, and shorter-duration option grants; banks that went public before the crisis underperformed significantly during 2007-2009 | Table VIII, p. 3250; Table X Panel B, p. 3253 | Triple-DD on CEO short-term disclosure = 0.669\*\* (SE 0.327); institutional investor turnover = 0.071\*\* (SE 0.029); crisis ROE interaction for full sample = -0.028\*\*\* (SE 0.002) |

**Overall (paper's conclusion).** Access to public equity markets causes banks to
increase risk. The mechanism is consistent with short-termism: public listing
introduces pressure from stock market investors and compensation incentives that
lead banks to boost short-run earnings by taking hard-to-observe risks, at the
expense of long-run performance. The finding has implications for both
compensation regulation and the wisdom of governance reforms that enhance
shareholder power, since good governance coupled with stock-market pressure may
increase rather than decrease risk in banking.

## Theory / model

The paper has no formal structural model. It is organized around the short-termism
channel first formalized by Stein (1989). In that model, stock market investors
rationally attribute higher current earnings to both a permanent and a transitory
shock. Because earnings embed news about long-run value, managers who care about
the short-term stock price have incentives to cut hard-to-observe long-run
investments and boost short-term earnings, even at the expense of long-run value.
In banking, the easiest way to raise short-term earnings is to take more risk:
loosen lending standards, increase loan yields, rely on cheaper but less stable
wholesale funding. These actions increase current earnings but create future credit
and rollover risks.

An alternative behavioral version due to La Porta (1996) holds that investors
overextrapolate current earnings, reinforcing the managerial incentive to boost
them. In both cases the prediction is the same: banks that place greater weight
on short-term stock price performance should take more risk after going public.

In Bolton, Scheinkman & Xiong (2006), equity compensation also leads to
short-termism because managers exploit the market's overvaluation of short-term
performance. Earlier cross-sectional work by Kwan (2004) and Nichols, Wahlen &
Wieland (2009) finds no significant risk differences between public and private
banks, but that work relies on ex-post performance measures rather than ex-ante
supervisory CAMELS ratings, which may explain why it misses the effect
documented here (p. 3252).

The two key empirical predictions are:

1. Going public raises ex-ante supervisory risk (CAMELS), especially on
   dimensions that investors cannot easily observe.
2. The risk increase should be larger for banks more subject to short-term pressure
   (higher institutional investor turnover, higher CEO short-term disclosure, more
   short-duration equity compensation) and should boost short-run ROE at the cost
   of long-run underperformance (p. 3225).

**Identification strategy.** The concern is that IPOs are endogenous: banks may go
public in response to growth opportunities that are also correlated with a riskier
environment. The paper addresses this by using a difference-in-differences (DD)
design in which the control group is banks that announced but then withdrew their
IPO filings (following Bernstein (2015) and Seru (2014)). The idea is that both
groups intended to go public for the same reasons, so comparing within-bank changes
in risk for treated banks to those of control banks differences out the selection
concern. The paper verifies that treated and control banks have parallel pre-trends
in CAMELS and are balanced on all observable characteristics except size (p. 3233,
Table II). As a further check, the paper instruments IPO completion with S&P
banking sector index returns in the two months after the announcement (Bernstein
(2015) instrument): deals announced when bank stocks are doing poorly are less
likely to be completed.

## Method

The paper applies three main estimators. It builds on `difference-in-differences`
as the primary causal design, `instrumental-variables` (2SLS) for robustness, and
`panel-regression` with `matching` for sensitivity.

**Baseline DD estimator (equation 1, p. 3232).** For each bank $$i$$ and year-quarter
$$t$$, the estimating equation is:

$$
\text{RISK}_{it} = \beta_1 \times \text{After}_{it} + \beta_2 \times \text{After}_{it} \times \text{Treatment}_i + \gamma \times Z_{it} + \mu_t + \alpha_i + \epsilon_{it} \tag{1}
$$

where $$\text{RISK}$$ is the composite CAMELS rating (1-5) or the weak CAMELS indicator;
$$\text{After}_{it}$$ equals one for all bank-quarters after the IPO announcement date;
$$\text{Treatment}_i$$ equals one for banks that completed the IPO (zero for withdrawn
filers); $$Z_{it}$$ is bank size (log total assets); $$\mu_t$$ is year-quarter fixed
effects; and $$\alpha_i$$ is bank fixed effects. Standard errors are clustered at the
BHC level. The coefficient of interest is $$\beta_2$$, the difference-in-differences
estimate.

**2SLS-IV estimator (equations 2 and 3, p. 3238).** To address residual selection
concerns, the paper instruments deal completion with banking sector stock returns
in the two months after the announcement. The second-stage is:

$$
\text{RISK}_i^{\text{Post}} = \beta_1 \widehat{\text{CompletedIPO}}_i + \gamma_1 \text{RISK}_i^{\text{Pre}} + \gamma_2 Z_i + \mu_t + \epsilon_i \tag{2}
$$

where $$\text{RISK}_i^{\text{Post}}$$ is the average risk proxy after the announcement and
$$\text{RISK}_i^{\text{Pre}}$$ is the pre-announcement average. The first stage is:

$$
\text{CompletedIPO}_i = \beta_2 \cdot S\&P\text{BankReturns}_i + \gamma_3 \text{RISK}_i^{\text{Pre}} + \gamma_4 Z_i + \mu_t + \epsilon_i \tag{3}
$$

where $$S\&P\text{BankReturns}_i$$ is the S&P bank index return in the two months after
the announcement. The exclusion restriction is that these short-window returns are
uncorrelated with longer-term bank-specific risk decisions.

**Triple-DD estimator (cross-sectional heterogeneity, p. 3250).** To test whether
the risk increase is greater for banks with stronger short-term incentives, the
paper estimates:

$$
\text{RISK}_{it} = \beta_1 \text{After}_{it} + \beta_2 \text{After}_{it} \times \text{Treatment}_i + \beta_3 \text{After}_{it} \times \text{Treatment}_i \times X_i + \beta_4 \text{After}_{it} \times X_i + \gamma Z_{it} + \gamma_1 \text{After}_{it} \times Z_{it} + \mu_t + \alpha_i + \varepsilon_{it}
$$

where $$X_i$$ is the cumulative density of a short-termism proxy (institutional
investor turnover, CEO short-term disclosure, equity option value or duration).
The term $$\text{After}_{it} \times X_i$$ cannot be identified from $$\text{After}_{it} \times
\text{Treatment}_i \times X_i$$ because $$X_i$$ does not vary within private banks, so
it drops out of the estimation.

## Empirical specifications

All main regressions use quarterly Call Report and supervisory data for U.S.
commercial banks held by BHCs, 1990-2012, restricted to a 10-year pre-crisis
window (1997-2006) for baseline tests. Standard errors are clustered at the BHC
level. The key specifications and their links to the core results are:

- **Baseline DD on composite CAMELS and weak CAMELS (R1, R2).** Spec (1) in Table
  III, Panel A: equation (1) above with bank FE, year-quarter FE, supervisor FE,
  and log total assets; IPO sample of 406 completed and 122 withdrawn banks; 8,237
  bank-quarter observations.

- **Subcomponent supervisory ratings (R4, R5).** Table IV Panels A and B: same
  specification (1) applied to the A rating (asset quality), STBL loan risk
  rating, C and L combined (capital adequacy and liquidity), and the risk
  sensitivity rating. Identifies which dimensions of the CAMELS deteriorate.

- **Balance sheet DD (R6).** Table V: equation (1) with RWA/A, residential real
  estate loans to total loans, Tier 1 capital ratio, and volatile liabilities
  as outcomes. Confirms risk increase is visible in observable data.

- **Robustness via controlling for observables (Table VI).** Adds the balance
  sheet risk measures as controls to the supervisory rating regressions; the
  treatment effect remains significant, confirming that hidden risk
  (unobservable to investors) is the source of the CAMELS deterioration.

- **Performance dynamics (R7, Table VII).** Calendar-time specification:
  $$Y_{t+N} - Y_{t-1} = \beta_1 \text{Treatment}_i + \gamma Z_{it} + \mu_t + \alpha_i + \varepsilon_{it}$$ tracking the change in
  quarterly ROE and the E rating at horizons N = 1, 4, 8, and 16 quarters
  post-announcement; and DD regressions of discretionary LLP/loans, loan loss
  provisions to delinquencies, IBES long-term EPS growth forecast, and earnings
  restatements.

- **Triple-DD on mechanism (R8, Table VIII).** Interacts the treatment effect
  with CEO short-term disclosure (Brochet, Loumioti & Serafeim (2015) frequency-
  of-short-term-horizon-words measure from earnings calls and 10-K MD&A sections),
  institutional investor turnover, equity option B-S value, and option grant
  duration.

- **M&A robustness (Table III Panel A cols. 3-4).** Replicates the main result
  using the Completed M&As Sample (1,631 banks, 10,312 observations), where
  treatment is acquisition by a publicly traded BHC and control is other
  acquisitions that do not change ownership status. Coefficients are smaller
  (0.098\*\*\* for composite CAMELS, M&A sample) but strongly significant.

- **Broader cross-section and financial crisis (Table X).** OLS and FE regressions
  of CAMELS on a public BHC dummy in the merged BHC-Commercial Bank Sample
  restricted to the pre-crisis window (90,733 bank-quarter observations);
  Public BHC dummy coefficient = 0.089\*\*\* (FE, p. 3253). Triple-DD
  on crisis ROE: After\*Treatment\*Crisis = -0.028\*\*\* (full IPO sample, p. 3253).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| NIC (National Information Center), Federal Reserve | Confidential CAMELS supervisory ratings (composite and components); BHC ownership and public listing history | no page yet |
| STBL (Survey of Terms of Business Lending), Federal Reserve | Confidential loan-level risk ratings for C&I loans (1 to 5 scale); 1997-2012; used by DellAriccia, Laeven & Suarez (2017) and others | no page yet |
| Call Reports (Reports of Condition and Income), FDIC/Federal Reserve | Balance sheet variables: total assets, RWA, Tier 1 capital, deposits, loans, volatile liabilities; 1990-2012 | no page yet |
| SDC New Issues / S&P Capital IQ / SNL Financial Capital Offerings | Lists of completed and withdrawn bank IPO filings; 1990-2012 | no page yet |
| CRSP-FRB Link (New York Fed) | Stock market listing history for BHC public/private status | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| IBES (Institutional Brokers' Estimate System) | Equity analysts' consensus long-term EPS growth forecasts for newly public banks | [I/B/E/S](/wiki/licensed/ibes/) (licensed) |
| Thomson-Reuters Institutional Holdings (13F) | Institutional investor portfolio turnover; 1990-2012 | [Thomson 13F (s34)](/wiki/licensed/thomson-13f/) (licensed) |
| Riskmetrics / Capital IQ | Employee stock option grant data (B-S value, duration) | no page yet |

Sample: 178,980 bank-quarter observations for 7,166 (3,251) unique banks (BHCs);
IPO identification sample 17,754 bank-quarter observations for 528 unique
commercial banks (276 BHCs), 1990-2012; baseline tests use the 10-year window
1997-2006 (8,237 observations, Table I p. 3231). CAMELS ratings are quarterly.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13502) if you are:
studying bank risk regulation and the role of stock market incentives;
replicating the DD design with confidential supervisory data (the Internet
Appendix has additional robustness tables and placebo tests);
building on the short-termism mechanism in nonbank financial intermediaries;
or extending the analysis to international banking systems or post-crisis periods.
The locators above point to the exact tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025, pp. 3223-3261.
DOI: [10.1111/jofi.13502](https://doi.org/10.1111/jofi.13502). Paywalled; Wiley
standard terms-of-use (not CC). This distillation was extracted by an LLM on
2026-06-03 and is **not human-verified or independently reproduced**.

> Falato, Antonio, and David Scharfstein. "The Stock Market and Bank Risk-Taking."
> *The Journal of Finance* 80, no. 6 (December 2025): 3223-3261.
> DOI: 10.1111/jofi.13502. Extract-only: no redistribution of the verbatim article.
