---
title: "Does Floor Trading Matter: Brogaard, Ringgenberg & Roesch (2025)"
description: >-
  Distilled: Using the COVID-19 suspension of NYSE floor trading on March 23,
  2020 as a natural experiment, this paper finds that human floor traders
  significantly improve market quality: their removal raises proportional
  effective spreads by roughly 9 basis points (more than 70% of the
  pre-closure mean) and increases Hasbrouck pricing errors by approximately
  6%. J. Finance 2025, CC BY 4.0. Seven core results with source locators,
  datasets used, the DiD identification design, and the mechanism tests.
sidebar:
  label: Brogaard-Ringgenberg-Roesch 2025
  order: 1
tags: [paper-summary, market-microstructure, liquidity, algorithmic-trading,
       floor-trading, natural-experiment, difference-in-differences,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:wrds, data:taq]
paper:
  authors: Jonathan Brogaard, Matthew C. Ringgenberg, Dominik Roesch
  authorList:
    - { family: Brogaard, given: Jonathan, orcid: "0000-0001-5612-289X", affiliation: University of Utah }
    - { family: Ringgenberg, given: Matthew C., orcid: "0000-0002-3013-2085", affiliation: University of Utah }
    - { family: Roesch, given: Dominik, affiliation: State University of New York at Buffalo }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 375–414
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13401
  jel:
    codes: [G14, G12, G10]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Financial Markets and Investment Strategies', 'Corporate Finance and Governance', 'Monetary Policy and Economic Impact']
  dataAccess: licensed-commercial
  outcome:
    - proportional effective spreads (PESPR) on NYSE stocks
    - Hasbrouck (1993) pricing errors
    - auction price deviation from midpoint
  outcomeClass: [market-microstructure, asset-prices]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2024-10-27; corroborated by artifact p. 375 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley/OpenAlex direct PDF link confirmed 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 28

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, matching]
    identification: natural-experiment

  contributionType: [new-fact, measurement]

  mechanisms: [information-asymmetry, liquidity]

  scope:
    region: US
    assetClass: US equities (NYSE and NASDAQ common stocks)
    period: 2020-03-16..2020-06-23
    frequency: daily
    dataType: [market]
    granularity: [security, transaction]
    n: "approx. 1,600 NYSE-listed stocks (main closure window); 552-553 stocks in within-exchange specifications"

  findings:
    - ref: R1
      outcome: proportional effective spreads (PESPR) on NYSE stocks
      metric: basis-points
      value: "8.92 bps increase (t=7.90) in PESPR for NYSE vs. matched NASDAQ stocks after floor closure (Table III, Panel A, col. 2); 1.46% increase (t=2.68) in within-stock NYSE-vs-off-NYSE specification (Table III, Panel B, col. 2)"
      direction: positive
      vsBenchmark: "pre-closure unconditional mean PESPR of 12 bps for NYSE stocks; 8.92 bps = more than 70% increase"
    - ref: R2
      outcome: Hasbrouck (1993) pricing errors
      metric: coefficient
      value: "6.28*** (t=4.68) increase in Log|PricingError| for NYSE vs. NASDAQ matched stocks (Table IV, Panel A, col. 2); 2.39* (t=1.84) increase in within-stock specification (Table IV, Panel B, col. 1)"
      direction: positive
      vsBenchmark: "approx. 6% increase (Panel A) and approx. 2% increase (Panel B) relative to control; consistent across specifications"
    - ref: R3
      outcome: proportional effective spreads (PESPR) on NYSE stocks
      metric: coefficient
      value: "Intraday: largest effects at 9:30-10:00 window (8.16***, t=5.38) and 10:00-10:30 (5.69***, t=6.69); effects decline monotonically and are insignificant from 12:00 onward (Table V, Panels A-B)"
      direction: positive
      vsBenchmark: "Floor traders matter most immediately after the opening auction; midday and afternoon coefficients near zero"
    - ref: R4
      outcome: proportional effective spreads (PESPR) on NYSE stocks
      metric: coefficient
      value: "Triple interaction Complex x Treated x After = 17.45*** (t=7.33); floor traders matter more when stock-specific information complexity is high (Table V, Panel C)"
      direction: positive
      vsBenchmark: "Treated x After alone = -11.94*** (t=-7.84); floor trading value is concentrated in informationally complex stocks"
    - ref: R5
      outcome: auction price deviation from midpoint
      metric: basis-points
      value: "Opening auction: Treated x After ranges from 34 to 47 bps (significant at 1-5%) across columns (1)-(4) of Table VI; Closing auction: Treated x After = 32 bps (Table VI, cols. 5-8)"
      direction: positive
      vsBenchmark: "Closing auction unconditional mean approx. 32 bps; floor closure implies approx. 100% increase in closing price deviation"
    - ref: R6
      outcome: proportional effective spreads (PESPR) on NYSE stocks
      metric: coefficient
      value: "Around reopenings: Treated x Open1 = 0.27 (t=0.72, insignificant); Treated x Open2 = -4.85*** (t=-6.69) - spreads improve only after second reopening when DMMs return in person (Table VII, Panel A)"
      direction: negative
      vsBenchmark: "No reversal at first reopening (D orders resume); strong reversal at second reopening (in-person DMM interaction resumes)"
    - ref: R7
      outcome: auction price deviation from midpoint
      metric: basis-points
      value: "Around reopenings: Treated x Open1 = -20.50** (t=-2.45) significant improvement at opening auction; no significant improvement at second reopening (Table VIII, cols. 1-4)"
      direction: negative
      vsBenchmark: "Auction quality improves at first reopening (D orders) but not second; continuous trading improves at second reopening only"

  resultType: new-finding

  relatesTo:
    - { cite: 'Bessembinder, Hao & Zheng (2020)', doi: '10.1093/rfs/hhz040', relation: builds-on, note: 'DMM participation leads to better market quality on NYSE; this paper isolates the floor broker channel separately from DMM activity' }
    - { cite: 'Clark-Joseph, Ye & Zi (2017)', doi: '10.1016/j.jfineco.2017.09.001', relation: builds-on, note: 'designated market makers still matter; this paper focuses on floor brokers as the separately identified treatment group' }
    - { cite: 'Hu & Murphy (2020)', doi: '10.2139/ssrn.3600230', relation: tests, note: 'Hu and Murphy find NYSE closing auction quality is worse than NASDAQ, attributing it to floor traders; this paper finds the opposite - floor closure worsens auction quality' }
    - { cite: 'Madhavan & Panchapagesan (2000)', doi: '10.1093/rfs/13.3.627', relation: extends, note: 'designated dealers improve price discovery at open over fully automated markets; confirmed here with floor broker/DMM in-person interaction as the channel' }
    - { cite: 'Battalio, Ellul & Jennings (2007)', relation: builds-on, note: 'reputation effects in floor trading; personal relationships between specialists and floor brokers lower informational asymmetries' }
    - { cite: 'Benveniste, Marcus & Wilhelm (1992)', doi: '10.1016/0304-405x(92)90025-s', relation: builds-on, note: 'personal relationships between specialists and brokers can lower informational asymmetries that improve market quality' }
    - { cite: 'Jegadeesh & Wu (2022)', doi: '10.1016/j.jfineco.2021.12.003', relation: extends, note: 'NYSE closing auctions better than NASDAQ due to D orders; consistent with first-reopening result here that D orders matter for auctions' }

  openQuestions:
    - "Whether algorithms would eventually adapt to replicate floor-trader information-transfer benefits over longer horizons than the two-year window examined (p. 410, Limitations section)."
    - "Whether the SUTVA assumption holds: other liquidity providers on off-NYSE venues may have changed behavior in response to the floor closure, which would bias the within-exchange treatment estimate (p. 410)."
    - "Whether effects differ in less liquid or smaller stocks outside the sample's $500 million market-cap floor (p. 385, §I.C)."

  replicationCode:
    status: available

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: >-
        Full text read (pp. 375-414, 40 pages); seven results extracted from
        Tables III-IX of the CC-BY PDF. Crossref and OpenAlex metadata fetched
        this session. Not human-verified. Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; all
        seven Core results rows confirmed against Tables III-VIII (pp. 394-408),
        all equations (eqs. 1-7 and reopening specification) verified term-by-term
        against the PDF; no errors found, no fixes required.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13401
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2024-10-27"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, identification design, estimating
equations, and mechanism tests: enough to know what it found and how, without
reading all 40 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13401).

## TL;DR

On March 23, 2020, the NYSE suspended floor trading because of COVID-19, moving
to fully electronic trading. Using this abrupt, exogenous shock in a
difference-in-differences framework, the paper shows that human floor traders
improve market quality. Removing them raises proportional effective spreads by
roughly 9 basis points (more than 70% relative to the pre-closure mean) and
increases Hasbrouck pricing errors by about 6%, with the effects largest
immediately after the open when information arrival is highest. Two partial
reopenings (May 26 and June 17, 2020) allow the authors to distinguish between
two non-mutually-exclusive mechanisms: (i) in-person information transfer
between floor brokers and designated market makers (DMMs), and (ii) floor-only
D-order types. Continuous trading quality improves only after the second
reopening (DMMs return in person), while auction quality improves after the
first (D orders resume). Floor trading matters in the age of algorithms.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Effective spreads increase significantly** for NYSE stocks after floor closure, under both identification strategies | Table III Panel A col. 2 (p. 394); Table III Panel B col. 2 (p. 395) | NYSE vs. NASDAQ: +8.92 bps (t=7.90); within-stock NYSE vs. off-NYSE: +1.46% (t=2.68); stable across all fixed-effect specs |
| R2 | **Pricing errors increase** for NYSE stocks after floor closure, indicating worse price efficiency | Table IV Panel A cols. 1-2 (p. 396); Table IV Panel B col. 1 (p. 396) | NYSE vs. NASDAQ: +6.28\*\*\* (t=4.68) in log pricing error; within-stock: +2.39\* (t=1.84); approx. 6% and 2% increases respectively |
| R3 | **Effects are strongest immediately after the opening auction** (9:30-10:00 am) and decline monotonically through the trading day | Table V Panels A-B (pp. 398-399) | 9:30-10:00: +8.16\*\*\* (t=5.38); 10:00-10:30: +5.69\*\*\* (t=6.69); coefficients near zero from 12:00 onward |
| R4 | **Floor traders matter more when stock-specific information is higher**: triple interaction with information complexity is positive and significant | Table V Panel C (p. 399) | Complex x Treated x After = +17.45\*\*\* (t=7.33); confirms information-transfer channel |
| R5 | **Opening and closing auction quality deteriorates** after floor closure; price deviations increase for both auction types | Table VI (pp. 400-401) | Opening: +34 to +47 bps (Treated x After, all significant); Closing: +32 bps (approx. 100% increase relative to unconditional mean) |
| R6 | **Continuous trading spreads improve only at the second reopening** (DMMs return in person), not the first (D orders resume); D orders are not the continuous-trading mechanism | Table VII Panel A col. 2 (p. 404); Table VII Panel B col. 2 (p. 405) | Treated x Open1 = +0.27 (t=0.72, insignificant); Treated x Open2 = -4.85\*\*\* (t=-6.69) |
| R7 | **Auction quality improves at the first reopening** (when D orders resume) but not the second; D orders are the auction mechanism | Table VIII (pp. 407-408) | Treated x Open1 = -20.50\*\* to -20.68\*\* for opening auction (significant); Treated x Open1 for closing auction = -3.74\*\*\* to -4.00\*\*\*; second reopening insignificant for auctions |

**Overall (paper's conclusion).** The NYSE floor suspension degraded market
quality across multiple dimensions: liquidity (spreads), price efficiency
(pricing errors), and auction quality. The partial reopening evidence shows two
non-mutually-exclusive mechanisms are at work. During continuous trading, the
floor facilitates in-person information transfer between floor brokers and DMMs
that electronic markets cannot replicate; this channel reverses with the second
reopening, consistent with theoretical predictions by Benveniste, Marcus and
Wilhelm (1992) and the empirical evidence in Battalio, Ellul and Jennings
(2007) that personal relationships lower informational asymmetries. During
auctions, D orders (accessible only to floor traders) improve auction outcomes;
this channel reverses with the first reopening, consistent with Jegadeesh and
Wu (2022). The results address the debate sparked by Hu and Murphy (2020), who
found NYSE closing auction quality worse than NASDAQ and attributed it to floor
traders; here, floor traders are shown to improve auction quality and liquidity.
Bessembinder, Hao and Zheng (2020) and Clark-Joseph, Ye and Zi (2017) document
the value of DMM participation; this paper separately identifies floor brokers
as an additional, distinct channel. The price-discovery role of designated
dealers confirmed here is consistent with Madhavan and Panchapagesan (2000).
Overall, human floor traders remain valuable intermediaries even in the
algorithmic trading era.

## Theory / model

The paper has no formal structural model. The identification argument begins
with an additive model of market quality (eq. 1, p. 387):

$$
E[\text{MarketQuality}_{0,i,e,t} \mid i, e, t] = \rho_e + \lambda_t + \Gamma_i + \alpha_{i,t} \tag{1}
$$

where $$\rho_e$$ captures the exchange effect, $$\lambda_t$$ an aggregate time
effect, $$\Gamma_i$$ a time-invariant firm effect, and $$\alpha_{i,t}$$ time-varying
firm-level shocks. Observed market quality is then (eq. 2, p. 387):

$$
\text{MarketQuality}_{i,e,t} = \rho_e + \lambda_t + \Gamma_i + \alpha_{i,t} + \beta \cdot \mathbf{1}_{\text{FloorTrading}} + \xi_{i,e,t} \tag{2}
$$

where $$\mathbf{1}_{\text{FloorTrading}}$$ equals 1 if floor trading is suspended
and 0 otherwise; $$\beta$$ is the treatment effect of interest. The canonical
DiD estimator compares treated minus control before and after (eqs. 3-4,
p. 387-388), recovering $$\beta$$ when the parallel trends assumption holds,
i.e., when time-varying shocks to control firms ($$\alpha_{j,t}$$) evolve as in
treatment firms ($$\alpha_{i,t}$$).

The two tested mechanisms follow from three observable changes caused by the
floor closure: (i) loss of in-person interaction between DMMs and floor brokers,
(ii) loss of manual auction operation, and (iii) loss of special floor-only
order types (D orders). The staggered partial reopenings isolate each channel:
first reopening restores D orders but not in-person interaction; second
reopening restores in-person interaction and manual auctions.

## Method

The paper applies two difference-in-differences strategies using the same
additive model, differing in the control group.

**Approach 1: NYSE vs. matched NASDAQ stocks** (eq. 5, p. 389). The control
group is NASDAQ-listed stocks matched on price, trading volume, market
capitalization, and Fama-French 48-industry classification using one-to-one
nearest-neighbor propensity score matching (PSM) without replacement. The
treatment indicator is 1 if the stock is listed on NYSE after March 23, 2020:

$$
y_{i,e,t} = \beta \mathbf{1}_{i,e,t} + \lambda_t + \Gamma_i + \gamma C_{i,e,t} + \epsilon_{i,e,t} \tag{5}
$$

where $$y_{i,e,t}$$ is the market quality measure, $$\mathbf{1}_{i,e,t}$$
equals 1 for NYSE-listed stocks after March 23, $$\lambda_t$$ and $$\Gamma_i$$ are
date and firm fixed effects, and $$C_{i,e,t}$$ is a vector of controls (log
trading volume, parity trading volume). Standard errors are clustered by firm.

**Approach 2: Within-stock variation across exchanges** (eq. 6, p. 391). The
same NYSE-listed stocks are compared across trading venues, using trades in
the same stock on other exchanges (IEX, NASDAQ, BZX, etc.) as the control.
This includes firm x date fixed effects ($$\kappa_{it}$$) to absorb time-varying
firm-level shocks:

$$
y_{i,e,t} = \beta D_{i,e,t} + \kappa_{i,t} + \gamma C_{i,e,t} + \epsilon_{i,e,t} \tag{6}
$$

where $$D_{i,e,t}$$ equals 1 if firm $$i$$ is NYSE-listed, trading on the NYSE,
after March 23, 2020. The firm x date fixed effects absorb any time-varying
firm-level response to COVID-19, so confounders must differentially affect
NYSE vs. off-NYSE trading in the same stock around March 23 to bias the
estimate.

Both strategies use `difference-in-differences` and `panel-regression`
building blocks. The matching step uses `matching` (PSM). The market quality
measures are: proportional effective spread (PESPR), Hasbrouck (1993) pricing
error, and auction price deviation (eq. 7, p. 400):

$$
|\text{Deviation\%}| = 2 \times |\log(\text{trade}) - \log(\text{mid})| = 2 \times |\log(\text{trade}/\text{mid})| \tag{7}
$$

where log(trade) is the log auction trade price and log(mid) is the last
midpoint price from continuous trading. Higher values indicate worse auction
quality. Information complexity (Panel C of Table V) is measured as
$$1 - R^2$$ from a regression of each stock's return on the contemporaneous SPY
return within each half-hour interval (from Morck, Yeung, and Yu (2000)).

## Empirical specifications

**Main closure window** (Tables III-VI): two-week window from March 16 to March
27, 2020 (one week before, one week after the March 23 floor closure). Sample:
approximately 1,600 NYSE-listed stocks (PSM approach) or 552-553 NYSE-listed
stocks with sufficient off-exchange trading (within-stock approach). Results
are robust to a larger window encompassing all of 2020-2021 (Internet Appendix
Table IA.II).

**Spread regression (R1, Table III):** Dependent variable is PESPR in
percentage of midpoint. PESPR on NYSE is computed from NYSE quotes and trades
only; PESPR off-NYSE is from NBBO excluding NYSE. Specifications range from
stock fixed effects only (col. 1) to stock + day fixed effects (col. 2) to
adding price and log volume controls (col. 3-4 for Panel A; col. 3-5 for
Panel B). The treatment coefficient of 8.92 bps in Panel A and 1.46% in
Panel B are stable across all specifications, supporting identification
assumptions.

**Pricing error regression (R2, Table IV):** Dependent variable is
$$\log|\text{PricingError}_{i,e,t}|$$, the Hasbrouck (1993) measure estimated
following Rosch, Subrahmanyam, and Van Dijk (2017). Specifications mirror
Table III. Panel A coefficient of 6.28 (t=4.68) implies approximately 6%
increase in pricing errors; Panel B coefficient of 2.39 (t=1.84) implies
approximately 2% increase.

**Intraday spread regression (R3-R4, Table V):** Equation mirrors eq. 6 with
PESPR computed within each 30-minute interval from 9:30 to 16:00. Panel A
(morning) and Panel B (afternoon) show results by half-hour. Panel C includes
a triple interaction with information complexity (1 - R2), with stock x day
fixed effects.

**Auction deviation regression (R5, Table VI):** Dependent variable is
$$|\text{Deviation\%}|$$ for opening and closing auctions. Equation follows eq.
5 with stock and day fixed effects; additional control for D-order volume in
cols. 3-4 (opening) and cols. 7-8 (closing). Specification confirms D orders
are not the primary driver of auction deterioration.

**Reopening regressions (R6-R7, Tables VII-VIII):** Two-week window centered
around each of the two partial reopenings (May 26 and June 17, 2020). The
estimating equation for continuous trading (Table VII) includes two treatment
indicators (Open1, Open2) interacted with Treated; stock x event fixed effects
absorb different aggregate conditions across reopenings:

$$
\text{PESPR}_{i,e,t} = \beta_1(\text{Treated}_{i,e,t} \times \text{Open1}_{i,e,t}) + \beta_2(\text{Treated}_{i,e,t} \times \text{Open2}_{i,e,t}) + \beta_3 \text{Treated} + \beta_4 \text{Open1} + \beta_5 \text{Open2} + \gamma C_{i,e,t} + FE + \epsilon_{i,e,t}
$$

The analogous form applies to auctions (Table VIII). A negative and significant
$$\beta_2$$ (Open2) with insignificant $$\beta_1$$ (Open1) for continuous trading
identifies in-person interaction as the mechanism. A negative and significant
$$\beta_1$$ (Open1) with insignificant $$\beta_2$$ for auctions identifies D orders
as the auction mechanism.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP (Center for Research in Security Prices) | Stock prices, dollar trading volume (thousands USD), market capitalization; used to construct the matched sample and identify NYSE vs. NASDAQ stocks | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| NYSE TAQ (Trade and Quotes) via WRDS Intraday Indicators | Proportional quoted spreads (PQSPR), proportional effective spreads (PESPR), and Hasbrouck pricing errors; the main market quality measures for both identification strategies | [TAQ](/wiki/licensed/taq/) (licensed) |
| OneMarket Data (OneTick software) | Intraday TAQ data for within-exchange comparisons (PESPR computed separately by exchange for each 30-minute interval); NYSE data provided directly | no page yet |

Sample: main closure window March 16-27, 2020 (10 trading days); reopening windows May 18-June 1 and June 10-23, 2020 (10 trading days each). The sample starts with 3,447 US common stocks (CRSP share code 10 or 11) listed on NYSE (1,256) or NASDAQ (2,191) in December 2019, excluding stocks with more than one share class (431) or market cap below $500 million (1,412), yielding approximately 1,600 equities (Table I, p. 386).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13401) if you are:
comparing market quality across trading mechanisms (hybrid vs. fully electronic
exchanges); designing or evaluating floor-trading regulation; studying the role
of human intermediaries and in-person information exchange in modern markets;
or extending the DiD design to other exchange structure changes. The partial
reopening evidence (Tables VII-IX) is especially useful for separating
information-transfer from order-type mechanisms. The Internet Appendix (20
robustness measures from WRDS Intraday Indicators) provides a comprehensive
falsification suite.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. This
distillation was extracted by an LLM on 2026-06-06 and is **not human-verified
or independently reproduced**. The CC BY 4.0 licence permits mirroring; the
verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Brogaard, Jonathan, Matthew C. Ringgenberg,
> and Dominik Roesch. "Does Floor Trading Matter?" *The Journal of Finance*
> 80, no. 1 (February 2025): 375-414. DOI: 10.1111/jofi.13401.
> (C) 2024 The Author(s). Licensed under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
