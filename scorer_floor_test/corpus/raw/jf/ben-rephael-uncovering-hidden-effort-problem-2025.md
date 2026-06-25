---
title: "Uncovering the Hidden Effort Problem: Ben-Rephael, Carlin, Da & Israelsen (2025)"
description: >-
  Distilled: Uses minute-by-minute Bloomberg platform activity to construct a
  new measure of executive workday length (AWL) and shows that greater effort
  by CEOs and CFOs predicts positive earnings surprises, higher cumulative
  abnormal returns of 25-50 bps per one-hour AWL increase (persisting 4-10
  weeks), and lower CDS spreads. Weather-based IV confirms causality.
  J. Finance 2025, CC BY 4.0. Eight core results with source locators,
  datasets used, the model, and the method.
sidebar:
  label: Ben-Rephael et al. 2025
  order: 1
tags: [paper-summary, corporate-governance, executive-compensation, moral-hazard,
       agency, earnings-announcements, abnormal-returns, panel-regression,
       instrumental-variables, open-access, cc-by, peer-reviewed, unreplicated,
       data:wrds, data:edgar, data:ibes]
paper:
  authors: Azi Ben-Rephael, Bruce I. Carlin, Zhi Da, Ryan D. Israelsen
  authorList:
    - { family: Ben-Rephael, given: Azi, affiliation: Rutgers Business School }
    - { family: Carlin, given: Bruce I., orcid: "0000-0002-3789-3151", affiliation: Jones School of Business, Rice University }
    - { family: Da, given: Zhi, orcid: "0000-0003-2815-1516", affiliation: Mendoza College of Business, University of Notre Dame }
    - { family: Israelsen, given: Ryan D., affiliation: Broad College of Business, Michigan State University }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1261-1311
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13429
  jel:
    codes: [G34, J33, M52]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Financial Markets and Investment Strategies', 'Auditing, Earnings Management, Governance', 'Credit Risk and Financial Regulations']
  dataAccess: proprietary-confidential
  outcome:
    - standardized unexpected earnings (SUE)
    - cumulative abnormal stock returns (CAR) around earnings announcements
    - CDS spread (credit default swap spread)
    - executive average workday length (AWL) response to compensation kinks and peer competition
  outcomeClass: [firm-real-outcomes, security-returns, credit-risk, labor-careers-health]
  license: "CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-02-17; corroborated by artifact p.1261 Creative Commons Attribution License notice)"
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley online library, doi redirect, 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 9
  methods:
    role: both
    contributes: bloomberg-awl-effort-measure
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, fama-macbeth, event-study]
    identification: instrument
  contributionType: [new-data, new-fact, measurement]
  introducesData: true
  mechanisms: [moral-hazard, agency]
  scope:
    region: US
    assetClass: US equities, corporate CDS
    period: 2017-09..2020-12
    frequency: quarterly
    dataType: [market, accounting, administrative, other]
    granularity: [firm, individual]
    n: "252 named executives, 520 executive-year observations (Bloomberg effort sample); 1,128 executive-quarter observations (CAR regressions); 574 observations over 89 executives and 57 firms (CDS sample)"
  findings:
    - ref: R1
      outcome: standardized unexpected earnings (SUE)
      metric: coefficient
      value: "0.075** to 0.086*** per hour of AWL (Table IV, specs 1-6, all industries); spec 7 (nonfinancial only) = 0.069**; 1-SD increase in AWL leads to 0.11 SD increase in SUE"
      direction: positive
    - ref: R2
      outcome: cumulative abnormal stock returns (CAR) around earnings announcements
      metric: car
      value: "1-hour increase in AWL associated with 1-day CAR of 27.35 bps; plateaus at 30-50 bps for 4-10 weeks (Table V, Panel A)"
      direction: positive
    - ref: R3
      outcome: cumulative abnormal stock returns (CAR) around earnings announcements
      metric: car
      value: "Nonfinancial firms: 1-hour AWL increase associated with 1-day CAR of 43.91 bps, rising to 80-100 bps at 7-10 weeks (Table V, Panel B)"
      direction: positive
      vsBenchmark: effect larger for nonfinancial firms than full sample
    - ref: R4
      outcome: long-short calendar-time portfolio return (High_Effort minus Low_Effort)
      metric: alpha
      value: "Risk-adjusted long-short portfolio return = 7.33 bps/day (37 bps over five days); raw High minus Low = 7.198* bps/day (Table VI)"
      direction: positive
    - ref: R5
      outcome: CDS spread (credit default swap spread)
      metric: basis-points
      value: "1-hour increase in AWL associated with CDS spread reduction of -0.879 to -1.50 bps in the next quarter (Table VII, specs 1-4)"
      direction: negative
    - ref: R6
      outcome: standardized unexpected earnings (SUE)
      metric: coefficient
      value: "2SLS second stage: predicted AWL coefficient on SUE ranges 0.058*** to 0.097** across 8 specifications (Table X, Panel B); spec (1) = 0.093*** (SE=0.028)"
      direction: positive
      vsBenchmark: IV magnitudes consistent with OLS, confirming causality
    - ref: R7
      outcome: executive average workday length (AWL) response to compensation kinks
      metric: coefficient
      value: "Interaction Pct_cash_perf * Target_1_pct = 21.07** to 22.72** hours change in AWL (Table XV); executives near EPS bonus targets increase effort significantly"
      direction: positive
    - ref: R8
      outcome: executive average workday length (AWL) response to peer competition
      metric: coefficient
      value: "10% increase in peer firm sales growth associated with 0.25-0.45 more hours/day of AWL over next quarter; Lag1_%Chng_PeerSales = 0.025** (SE=0.011) full sample, 0.045*** (SE=0.015) nonfinancial firms (Table XVI)"
      direction: positive
  resultType: new-finding
  replicationCode:
    status: available
  relatesTo:
    - { cite: "Murphy (1999)", doi: '10.1016/s0165-4101(01)00013-1', relation: builds-on, note: "motivates the paper: argues it is impossible to study how executive effort affects firm value because effort is unobservable" }
    - { cite: "Yermack (2014)", doi: '10.1016/j.jfineco.2014.04.008', relation: builds-on, note: "studies leisure (vacation, golf) as a proxy for the flip side of effort provision; complements this paper's work-effort measure" }
    - { cite: "Healy (1985)", doi: '10.1016/0165-4101(85)90029-1', relation: tests, note: "tests whether compensation kinks (bonus floors and caps) affect executive behavior; finds AWL increases near targets, consistent with Healy (1985)" }
    - { cite: "Bandiera et al. (2020)", doi: '10.1086/705331', relation: builds-on, note: "CEO time use measured via direct monitoring; this paper uses publicly observable platform activity instead" }
    - { cite: "Biggerstaff, Cicero, and Puckett (2017)", doi: '10.1287/mnsc.2016.2452', relation: builds-on, note: "study CEO shirking via leisure (golf); complement to the effort-provision angle here" }
  openQuestions:
    - "Whether the Bloomberg AWL measure captures all forms of executive effort or only office-based, computer-intensive work (noted implicitly in the data-validation discussion, pp. 1262-1277; executives doing physical or off-platform work are not captured)."
    - "Whether the weather IV fully satisfies the exclusion restriction for financial firms, whose supply chains are less weather-sensitive; the paper repeats the analysis for financial firms in Internet Appendix Tables IA.IX-IA.X (p. 1297) and finds similar results but acknowledges the limitation."
    - "How the effort-firm-value link changes in post-2020 remote-work environments, where Bloomberg online status may no longer reflect physical presence at the office (COVID period excluded from main analysis, p. 1268)."
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full PDF read (pp. 1261-1311, 51 pages); all eight results extracted from tables with page locators. Not human-verified. Not reproduced. Replication code is referenced on p. 1311 and available from the publisher."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF for all 8 rows and all equations; fixed R1 AWL range (0.075-0.086 corrected to 0.069-0.086 across all 7 specs), R6 SUE range (0.067-0.097 corrected to 0.058-0.097 across 8 specs), R6 CAR horizon label (4-Week corrected to 15-Day for 61.67 bps value), R2/R3/R6 parenthetical labels corrected from t-stat to SE (table caption confirms SE), R8 SE pairing (0.045 SE corrected from 0.013 to 0.015), and removed 2 colorful adjective instances of 'novel'."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13429
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-02-17"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the effort measure it constructs, and the main empirical specifications: enough to know what it found and how, without reading all 51 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13429).

## TL;DR

The paper hand-collects minute-by-minute Bloomberg online status for 252 named executives (CEOs, CFOs, and other top executives) at public U.S. companies, 2017 to 2020. From this it constructs the Average Workday Length (AWL), a measure of workday span derived via an EM-based Gaussian mixture model of intraday platform activity. The paper then shows that higher AWL predicts better firm outcomes across multiple dimensions: positive earnings surprises (SUE), higher cumulative abnormal stock returns (25-50 bps per one-hour AWL increase, persisting 4-10 weeks), and lower credit default swap spreads. A weather-based instrumental variable confirms the causal direction. The paper also revisits classic agency questions: executives near their bonus EPS targets increase effort, and peer-firm sales growth (not own sales growth) drives subsequent effort, consistent with competition and peer pressure motivating harder work.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Higher AWL predicts higher SUE**: a 1-SD increase in AWL raises SUE by 0.11 SD | Table IV, p. 1283; text p. 1282 | AWL coefficient = 0.069\*\* to 0.086\*\*\* across all specifications; specs 1-6 (all industries): 0.075\*\* to 0.086\*\*\*; spec 7 (nonfinancial firms only): 0.069\*\* |
| R2 | **AWL predicts higher CARs** around earnings announcements: a 1-hour increase raises the 1-day post-announcement CAR by 27.35 bps, with the effect plateauing at 30-50 bps over 4-10 weeks | Table V, Panel A, p. 1284-1285 | 1-Day coefficient = 27.35\* (SE=14.01); 4-10 Week coefficients range from 32 to 49 bps\*\* |
| R3 | **Effect is larger for nonfinancial firms**: 1-hour increase in AWL associated with 43.91 bps at 1-day, rising to 80-100 bps over 7-10 weeks | Table V, Panel B, pp. 1285-1286 | 1-Day = 43.91\* (SE=19.33); 7-Week = 91.33\*\* (SE=27.33); 10-Week = 104.38\*\*\* (SE=26.61) |
| R4 | **Calendar-time long-short portfolio on extreme AWL changes yields 7.33 bps/day** risk-adjusted (37 bps over five days), statistically significant | Table VI, p. 1287 | Risk-adjusted H-L = 7.330\*\*\* (SE=3.129); High-Effort alpha = 4.579\*\*\* (SE=1.569) |
| R5 | **Higher AWL reduces the firm's CDS spread**: a 1-hour increase in AWL is associated with a -0.879 to -1.50 bps reduction in the next quarter's CDS spread | Table VII, p. 1289 | Spec (1) coefficient = -0.879\*\* (SE=0.380); spec (4) = -1.504\*\*\* (SE=0.600) including executive FE |
| R6 | **Weather-instrumented AWL (2SLS) confirms causality**: predicted AWL coefficient on SUE is positive and significant across all IV specifications; CAR effects grow over time and are significant from week 2 onward | Tables X-XI-XIII, pp. 1295-1303 | 2SLS second stage on SUE (Table X Panel B): range 0.058\*\*\* to 0.097\*\* across 8 specs; spec (1) = 0.093\*\*\* (SE=0.028), specs (7)-(8) = 0.067\*\*\* (SE=0.022/0.025); 2SLS CAR at 15-Day horizon = 61.67\*\*\* bps (SE=18.52), 4-Week = 81.78\*\*\* bps (SE=23.90) (Table XIII) |
| R7 | **Locus of control matters**: executives near bonus EPS targets significantly increase effort in H2 of the fiscal year; when the bonus is far outside their locus of control, effort declines | Table XV, p. 1307 | Interaction Pct\_cash\_perf \* Target\_1\_pct = 21.07\*\* (SE=7.25) to 22.72\*\* (SE=7.72) hours change in AWL; consistent with Healy (1985) |
| R8 | **Peer competition drives effort**: a 10% increase in peer-firm sales growth raises executive AWL by 0.25-0.45 hours/day over the next quarter; own-firm sales growth has no significant effect | Table XVI, p. 1308 | Lag1\_%Chng\_PeerSales coefficient = 0.025\*\* (SE=0.011) in full sample (spec 2); 0.045\*\*\* (SE=0.015) in nonfinancial firms (spec 8); Lag1\_%Chng\_Sales coefficient insignificant |

**Overall (paper's conclusion).** Executive effort, as measured by Bloomberg workday length, has a positive and statistically significant effect on earnings surprises and cumulative abnormal stock returns around earnings announcements. This effect is not anticipated by equity market participants, since it is not embedded in prices prior to announcements. Executive effort is also associated with lower credit default swap spreads. Weather-based IV supports a causal interpretation. Agency analysis shows that effort responds to compensation incentive structures and to competition, confirming the relevance of the classic principal-agent framework for executive behavior.

## Theory / model

The paper has no formal structural model; it tests a principal-agent hypothesis about hidden effort. The motivation is drawn from the standard moral hazard framework: because executive effort is unobservable to outsiders, financial markets cannot price it directly, and investigators cannot use standard regression tools to test whether effort raises firm value (Murphy (1999)). The paper's identifying insight is that Bloomberg platform activity is publicly observable and provides a plausible proxy for the work habits of executives who spend most of their day doing activities other than using Bloomberg.

The paper positions itself as a complement to Yermack (2014) and Biggerstaff, Cicero, and Puckett (2017), who study the flip side of executive effort by examining leisure activities (vacation travel, golf habits) and their association with firm underperformance. Rather than measuring absence, this paper measures presence via workday length. Bandiera et al. (2020) measure CEO time use via direct monitoring and diary-based methods; this paper instead exploits publicly observable platform activity to avoid observer effects.

The paper's agency hypotheses (Section III) are:

1. **Locus of control (Healy (1985))**: executives increase effort when earning a bonus is within their locus of control (near the target) and decrease effort when it is far outside (Degeorge, Patel, and Zeckhauser (1999); Murphy (2000)). The within-executive design (changes in AWL from H1 to H2 within a fiscal year) makes this causal.

2. **Peer competition**: an increase in market share of competing firms should reduce the focal firm's relative standing and motivate more effort. The paper tests whether peer-firm sales growth (lagged one and two quarters) predicts subsequent executive AWL while own sales growth does not.

The identification strategy for the main results (Sections II.A-II.B) is a weather-based IV: day-level "feels like" temperature near the executive's headquarters (from Weather Underground, 2017 Q3 to 2019 Q4) is used to classify good-weather and bad-weather days within each quarter and location. Good weather in warm months (Q2-Q3) is associated with shorter workdays (approximately 12 minutes less per day, Table VIII), providing exogenous variation in AWL that is uncorrelated with the firm's business activity.

## Method

**AWL construction (Section I.C, pp. 1277-1280).** The effort measure is derived from minute-by-minute Bloomberg online status. For each executive-year, the paper observes the probability $$P^j_{\min}$$ that the executive is logged in at minute $$j \in J \equiv \{12{:}00\,\text{am},\ldots, 11{:}59\,\text{pm}\}$$. A probability density function is constructed as

$$
p^i_{\min} = \frac{P^i_{\min}}{\sum_J P^j_{\min}} \tag{1}
$$

This pdf is modeled as a mixture of two normal distributions (morning and afternoon sessions), with means $$\mu_1, \mu_2$$ ($$\mu_2 > \mu_1$$) and variances $$\sigma_1^2, \sigma_2^2$$, mixing weight $$q$$:

$$
\mu_{1,2} = q\mu_1 + (1-q)\mu_2
$$

$$
\sigma_{1,2}^2 = q\sigma_1^2 + (1-q)\sigma_2^2 + q(1-q)(\mu_2 - \mu_1)^2
$$

An EM algorithm (sklearn GaussianMixture, convergence threshold 0.001) estimates all five parameters $$(\hat{q}, \hat{\mu}_1, \hat{\mu}_2, \hat{\sigma}_1^2, \hat{\sigma}_2^2)$$ for each executive-year. The average workday length is then:

$$
AWL = (\hat{\mu}_2 - \hat{\mu}_1) + \hat{\sigma}_1 + \hat{\sigma}_2 \tag{2}
$$

The mean AWL across 520 executive-year observations is 9.47 hours (SD 2.10). The measure is validated via: (i) Bloomberg activity patterns consistent with a 9am-5pm workday, (ii) near-zero activity during firm events (analyst days, investor days: 100% of executives inactive), (iii) cell phone geolocation data for a subset of three executives (AWL from Bloomberg and AWL from geolocation agree closely: 8.0 vs 7.88 hours for one executive).

**Weather instrument (Section II.B, pp. 1288-1294).** The first-stage regression is:

$$
AWL_{j,y,q} = \alpha + \beta\,\text{WeatherAWL}_{j,y,q} + \vartheta_{j,y,q} \tag{3}
$$

where

$$
\text{WeatherAWL}_{j,y,q} = \left[W_{\text{Good},j,y,q}\,AWL(\text{good})_{j,q} + W_{\text{Bad},j,y,q}\,AWL(\text{bad})_{j,q}\right]
$$

is the weighted average of good-weather and bad-weather AWLs across all years in the sample. The second-stage regression is:

$$
Y_{j,y,q} = \delta + \varphi\,\widehat{AWL}_{j,y,q} + \varepsilon_{j,y,q} \tag{4}
$$

where $$\widehat{AWL}_{j,y,q} = \hat{\alpha} + \hat{\beta}\,\text{WeatherAWL}_{j,y,q}$$ is the fitted value from the first stage and $$Y_{j,y,q}$$ is the outcome variable (SUE, CAR, etc.). The method draws on `instrumental-variables` (2SLS), with `panel-regression` for the OLS baseline.

**Portfolio construction (Section II.A, p. 1287).** Calendar-time portfolios are formed around earnings announcements. The High-Effort portfolio on a given day includes stocks whose executives' AWL change (relative to four quarters prior) is in the top 10% across all executives with the same fiscal quarter-end, and whose earnings announcement occurred within the past five trading days. The Low-Effort portfolio is defined analogously (bottom 10%). Portfolio returns are value-weighted using market capitalization; Fama-French three-factor alphas are computed using a rolling year of past daily returns.

## Empirical specifications

**SUE regressions (Tables IV, X; pp. 1283, 1295-1296).** The OLS estimating equation is:

$$
SUE_{j,q} = \alpha_j + \beta\,AWL_{j,q} + \gamma\,\log\_\text{purchase}_{j,q} + \delta\,\log\_\text{sell}_{j,q} + \theta\,\mathbf{X}_{j,q} + \varepsilon_{j,q} \tag{5}
$$

where $$SUE_{j,q}$$ is standardized unexpected earnings, $$AWL_{j,q}$$ is measured during the fiscal quarter, $$\alpha_j$$ is an individual executive fixed effect, insider trading controls $$(\log\_\text{purchase}, \log\_\text{sell}, \log\_\text{purchase\_all}, \log\_\text{sell\_all})$$ capture private information, and $$\mathbf{X}_{j,q}$$ includes firm characteristics (size, leverage, productivity, Tobin's Q). Standard errors are clustered by executive. N = 980 (full sample); N = 459 (nonfinancial only). Data sources: Bloomberg (AWL), I/B/E/S (EPS), SEC Edgar (insider trading), Fama-French (industry definitions), CRSP/Compustat (firm characteristics).

**CAR regressions (Tables V, XIII; pp. 1284-1285, 1302-1303).** Cumulative abnormal returns are computed using the Fama-French three-factor model over rolling 50-trading-day windows from day 1 through day 50 post-announcement (1 through 10 weeks). The regression is:

$$
CAR_{j,q,d} = \alpha_j + \beta\,AWL_{j,q} + \gamma\,SUE_{j,q} + \delta\,\text{InsiderTrading}_{j,q} + \varepsilon_{j,q,d} \tag{6}
$$

Individual executive fixed effects are included. N = 1,128 executive-quarter observations. Standard errors are clustered by executive. For 2SLS (Table XIII), $$AWL_{j,q}$$ is replaced by $$\widehat{AWL}_{j,q}$$ from the weather first stage.

**CDS spread regressions (Table VII; p. 1289).** An AR(1)-style specification regresses next-quarter CDS spread on current AWL and current spread:

$$
\text{Spread}_{j,q+1} = \alpha_j + \beta\,AWL_{j,q} + \gamma\,\text{Spread}_{j,q} + \delta\,\text{InsiderTrading}_{j,q} + \theta\,\mathbf{X}_{j,q} + \varepsilon_{j,q} \tag{7}
$$

N = 574 observations from 89 executives at 57 firms (those with active five-year CDS contracts). Executive and year-fixed effects included in some specifications. Standard errors clustered by executive. CDS data from DataStream.

**Agency regressions (Tables XV-XVI; pp. 1307-1308).** Locus of control: change in AWL from H1 to H2 is regressed on the interaction between $$\text{Pct\_cash\_perf}$$ (fraction of cash bonus based on accounting metrics) and $$\text{Target\_1\_pct}$$ (indicator for H1 EPS within 1% of the annual EPS bonus target), plus firm characteristics and fixed effects. N = 91 executives. Competition: AWL in quarter $$t$$ is regressed on lagged own-firm and peer-firm sales growth (quarterly, four-quarter growth rate), with executive and year fixed effects, N = 1,256.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Bloomberg Professional (hand-collected platform activity) | Primary effort measure: minute-by-minute online status for 2,734 executives (2017-2020), matched to 252 named executives at public firms | No page yet |
| CRSP monthly stock returns and market data | Stock returns for CAR computation; market capitalization for value-weighting | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat quarterly fundamentals | Firm characteristics (size, leverage, Tobin's Q, productivity, EPS) | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| I/B/E/S (IBES) earnings estimates | EPS actuals and forecasts for SUE construction | [WRDS / IBES](/wiki/licensed/wrds/) (licensed) |
| SEC EDGAR (insider trading filings) | Executive open-market purchases and sales (Form 4) for insider trading controls | [SEC EDGAR](/wiki/datasets/edgar/) |
| DataStream (CDS spreads) | Five-year CDS spread data for 57 firms | No page yet |
| ISS Incentive Lab | Compensation contract data (proxy statements) for 252 executives at 174 firms | No page yet |
| Weather Underground | Historical daily weather ("feels like" temperature) for executive HQ locations, 2017 Q3-2019 Q4, used as instrument | No page yet |
| Reveal Mobile (geolocation) | Cell phone geolocation data for validation of AWL measure (anecdotal, 3 executives) | No page yet |
| Factiva (event transcripts) | Identification of executive presence at analyst days, investor days, and conferences | No page yet |
| Kenneth French Data Library | Fama-French 3-factor portfolios for CAR and alpha computation; FF-12 industry definitions | [Ken French library](/wiki/datasets/ken-french/) |
| Bloomberg corporate events calendar (EVTS function) | Event dates and types (earnings calls, analyst days, investor days, etc.) for personal-use validation | No page yet |

Sample: September 2017 to December 2019 (main effort sample; COVID period used only for validation). 252 executives, 520 executive-year observations; 1,128 executive-quarter observations for CAR regressions; 574 CDS observations.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13429) if you are: measuring executive effort using alternative proxies (the AWL construction algorithm is fully described in Section I.C); studying compensation contract design and incentive effects (Section III.A); interested in peer-competition effects on managerial behavior (Section III.B); or building on the Bloomberg platform data to study executive attention. The Internet Appendix contains extensive robustness tables (winsorized AWL, financial-only subsample, alternative weather windows).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Ben-Rephael, Azi, Bruce I. Carlin, Zhi Da, and Ryan D. Israelsen.
> "Uncovering the Hidden Effort Problem."
> *The Journal of Finance* 80, no. 2 (April 2025): 1261-1311.
> DOI: 10.1111/jofi.13429. © 2025 The Authors.
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
