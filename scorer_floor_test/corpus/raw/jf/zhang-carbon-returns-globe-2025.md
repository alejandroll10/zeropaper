---
title: "Carbon Returns across the Globe: Zhang (2025)"
description: >-
  Distilled: After correcting for the data release lag of carbon emissions, the
  brown-minus-green return (the carbon premium) turns significantly negative in
  the United States and insignificant globally, overturning prior findings; the
  apparent premium stems from forward-looking sales information embedded in
  emissions data rather than a true risk premium. J. Finance 2025, CC BY 4.0.
  Eight core results with source locators, datasets used, and the empirical
  specifications.
sidebar:
  label: Zhang 2025
  order: 1
tags: [paper-summary, asset-pricing, esg, climate-finance, carbon-risk, factors,
       portfolio-sort, fama-macbeth, panel-regression, open-access, cc-by,
       peer-reviewed, unreplicated,
       data:wrds, data:ken-french, data:fred, data:trucost]
paper:
  authors: Shaojun Zhang
  authorList:
    - { family: Zhang, given: Shaojun, orcid: "0000-0001-9272-0248", affiliation: "Fisher College of Business, The Ohio State University" }
  year: 2025
  venue: "The Journal of Finance 80(1), February 2025, 615-645"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13402
  jel:
    codes: [G12, G14, Q54]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - "Atmospheric and Environmental Gas Dynamics"
    - "Climate Change Policy and Economics"
    - "Energy, Environment, and Transportation Policies"
  dataAccess: licensed-commercial
  outcome:
    - cross-sectional stock returns sorted by carbon intensity
    - carbon return spread (brown-minus-green portfolio return)
    - FF6-adjusted alpha of carbon-sorted portfolios
  outcomeClass: [security-returns]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2024-10-21)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available via Wiley (onlinelibrary.wiley.com/doi/pdfdirect/10.1111/jofi.13402, confirmed via OpenAlex 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 147
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [portfolio-sort, fama-macbeth, panel-regression]
    identification: descriptive
  contributionType: [new-fact, measurement]
  mechanisms: [demand-elasticity]
  scope:
    region: global
    assetClass: global equities
    period: 2009-06..2021-12
    frequency: monthly
    dataType: [market, accounting]
    granularity: [security, firm]
    n: "206,025 U.S. firm-months (baseline regression); 608,678 firm-months for DM global regression (Table X)"
  findings:
    - ref: R1
      outcome: carbon return spread (brown-minus-green portfolio return)
      metric: return-spread
      value: "-0.39% per month (scope 1, value-weighted, U.S.); -0.27% per month (scope 2, value-weighted, U.S.)"
      direction: negative
      vsBenchmark: "negative vs zero; sign opposite to the positive carbon premium reported in Bolton and Kacperczyk (2021, 2023)"
    - ref: R2
      outcome: FF6-adjusted alpha of carbon-sorted portfolios
      metric: alpha
      value: "-0.40% per month (scope 1, t=-2.51); -0.34% per month (scope 2, t=-2.40)"
      direction: negative
      vsBenchmark: "significant at 5%; contrasts with positive alpha in prior studies using contemporaneous or short-lag emissions"
    - ref: R3
      outcome: cross-sectional stock returns sorted by carbon intensity
      metric: coefficient
      value: "-0.19% per SD (scope 1, t=-2.52); -0.21% per SD (scope 2, t=-2.46) in WLS regression"
      direction: negative
      vsBenchmark: "negative after controlling for beta, size, BM, ROA, asset growth, momentum, leverage, log PPE, IVol, sales growth, EPS growth, energy exposures"
    - ref: R4
      outcome: carbon return spread (brown-minus-green portfolio return)
      metric: return-spread
      value: "-0.06% per month (scope 1 alpha, global, insignificant, t=-0.74); -0.03% (scope 2 alpha, t=-0.43)"
      direction: none
      vsBenchmark: "insignificant globally vs significant negative in the U.S."
    - ref: R5
      outcome: FF6-adjusted alpha of carbon-sorted portfolios
      metric: alpha
      value: "-0.44% (scope 1) and -0.34% per month (scope 2) for G7+AUS (t=-7.24, t=-6.10); -0.40% and -0.33% for developed markets (DM, t=-9.52, t=-8.36); +0.20% and +0.06% for emerging markets (EM)"
      direction: negative
      vsBenchmark: "negative and significant in developed markets; zero or positive in emerging markets"
    - ref: R6
      outcome: cross-sectional stock returns sorted by carbon intensity
      metric: coefficient
      value: "Scope 1 emissions growth: +0.28% per SD (t=5.98) [Table IX]; Log emissions: +0.22% per SD (t=2.06) when using contemporaneous (same-year) emissions [Table IX]; H-L portfolio return: +0.47%/month (scope 1, t=3.25) [Table VIII Panel A]"
      direction: positive
      vsBenchmark: "positive before controlling for sales information; turns negative after adding log sales and sales growth as controls"
    - ref: R7
      outcome: carbon return spread (brown-minus-green portfolio return)
      metric: return-spread
      value: "Climate concern (sustainable flow): -0.10% and -0.15% per SD change in scope 1 and 2 carbon return; earnings-day return: +0.79% per SD (scope 1)"
      direction: mixed
      vsBenchmark: "cash flow news accounts for up to 7% of carbon return variation; climate concerns explain negative carbon returns in developed markets"
    - ref: R8
      outcome: cross-sectional stock returns sorted by carbon intensity
      metric: coefficient
      value: "Policy tightness: +0.13% per SD increase in scope 1 carbon return (t=2.12); renewable energy share: +0.20% per SD (t=2.60)"
      direction: positive
      vsBenchmark: "countries with tighter climate policies exhibit higher (less negative) carbon returns, consistent with a risk premium for policy risk"
  resultType: overturns
  relatesTo:
    - { cite: "Bolton and Kacperczyk (2021)", relation: contradicts, note: "paper shows their positive carbon premium is driven by forward-looking sales information, not a risk premium; replicates their methodology and finds negative carbon returns once the data release lag is applied" }
    - { cite: "Bolton and Kacperczyk (2023)", doi: '10.1111/jofi.13272', relation: contradicts, note: "reinterprets cross-country carbon return variation as climate concern shocks rather than expected return differences; shows their positive global carbon premium disappears after correcting for data release lag" }
    - { cite: "Fama and French (1992)", doi: '10.1111/j.1540-6261.1992.tb04398.x', relation: builds-on, note: "uses the six-factor model (FF6) to risk-adjust carbon-sorted portfolio returns" }
    - { cite: "Hou, Karolyi and Kho (2011)", doi: '10.1093/rfs/hhr013', relation: builds-on, note: "applies their outlier screen for international stock returns" }
    - { cite: "Pastor, Stambaugh and Taylor (2021)", relation: tests, note: "provides evidence consistent with their transition-period framework, where carbon returns can be negative during the transition to carbon-aware equilibrium" }
    - { cite: "Fama and French (2017)", relation: builds-on, note: "uses their international five-factor model and its region-specific factors for global portfolio analysis" }
  openQuestions:
    - "How carbon transition risk will be priced once the transition to carbon-aware equilibrium is complete and investors have fully incorporated carbon information; the paper notes equilibrium carbon returns may remain muted for an extended period as the transition continues (p. 644)."
    - "The role of additional research to enhance understanding and refine the impact of climate policy transitions on asset prices, especially for markets at different stages of climate concern adoption (p. 644)."
  replicationCode:
    status: available
  proposedVocab:
    - { axis: topic, term: climate-finance, def: "Research on the pricing of climate-related risks (carbon transition, physical climate, ESG) in financial markets.", aliases: [carbon-risk, esg-pricing, climate-risk-pricing] }
    - { axis: topic, term: esg, def: "Environmental, social, and governance investing strategies and their return implications.", aliases: [esg-investing, sustainable-investing, responsible-investing] }
  licenceVerification:
    - source: "Crossref REST API works/10.1111/jofi.13402"
      checked: 2026-06-06
      by: "paper-distiller (claude-sonnet-4-6)"
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2024-10-21"
  extraction:
    - by: "paper-distiller (claude-sonnet-4-6)"
      date: 2026-06-06
      role: extracted
      note: "Read full PDF (pp. 615-645). Core results, specifications, and equations extracted from Tables IV-XI and Figures 1-3. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (Tables IV-XI, equations 1-8); fixed R6 locator (Panel B -> Panel A) and magnitude (0.41% -> 0.47% from Table VIII Panel A); fixed R5 findings G7+AUS values (scope 1: -0.44%, scope 2: -0.34%, not -0.40%/-0.40%); corrected mechanisms (esg-reputation -> demand-elasticity); all other rows and equations confirmed correct."
---

**What this is.** The paper's core results, the data methodology, and the empirical specifications that overturn prior findings on the carbon premium: enough to know what it found and how, without reading all 31 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13402).

## TL;DR

The paper revisits the carbon return, defined as the return spread between high-carbon-intensity (brown) and low-carbon-intensity (green) firms. Prior studies find a positive carbon premium. Zhang (2025) shows this premium arises from forward-looking sales information embedded in emissions data rather than a true ex ante risk premium. After applying the actual data release lag (median 10 months for U.S., 12 months for international), the carbon return turns significantly negative in the United States (brown firms underperform green firms) and is insignificant globally. Developed markets exhibit more negative carbon returns due to stronger growth in climate concerns; countries with tighter climate policies show higher carbon returns consistent with pricing policy risk.

## Core results

Magnitudes and significance are as reported in the paper; `\*\*`/`\*\*\*` = 5%/1%. The sample is June 2009 to December 2021.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **U.S. carbon return is significantly negative**: brown firms underperform green firms after applying the data release lag | Table IV, Panel A, p. 628 | Value-weighted H-L return: -0.39%/month (scope 1, t=-2.47); -0.27%/month (scope 2, t=-1.87) |
| R2 | **FF6-adjusted alphas are significantly negative** for U.S. carbon-sorted portfolios | Table IV, Panel A, p. 628 | Alpha: -0.40%/month (scope 1, t=-2.51); -0.34%/month (scope 2, t=-2.40) |
| R3 | **WLS regression confirms negative carbon return** in the U.S. cross-section | Table VI, cols. 1-2, p. 632 | Scope 1: -0.19% per SD (t=-2.52); scope 2: -0.21% per SD (t=-2.46) |
| R4 | **Global carbon return is insignificant** on average across all countries | Table VII, Panel A, p. 633 | Value-weighted alpha: -0.06% (scope 1, t=-0.74); -0.03% (scope 2, t=-0.43) |
| R5 | **Developed markets (DM) have more negative carbon returns than emerging markets (EM)** | Table X, Panel A, p. 640 | DM alpha: -0.40% (scope 1, t=-9.52); EM alpha: +0.20% (scope 1, t=3.55) |
| R6 | **Positive carbon premium in prior studies is explained by forward-looking sales information**: once contemporaneous sales growth is controlled, positive emissions-return relation disappears | Table VIII Panel A and Table IX, pp. 635-637 | Contemporaneous scope 1 delta-emissions return: +0.47%/month (H-L, t=3.25); after controlling for same-period sales growth: insignificant (-0.03%, -0.24%, +0.10% within sales terciles) |
| R7 | **Climate concern shocks explain cross-country carbon return variation**: a 1-SD increase in sustainable flow lowers scope 1 carbon return by 0.10%/month | Table XI, Panel A, p. 642 | Sustainable flow: -0.10% (scope 1, t=-1.37); climate concern: -0.11% (scope 1, t=-1.68); earnings-day return: +0.79% (scope 1, t=8.53) |
| R8 | **Tighter climate policies associated with higher carbon returns**: countries with higher policy tightness earn 0.13% more per SD in carbon returns | Table XI, Panel B, p. 642 | Policy tightness: +0.13% per SD (t=2.12); renewable energy share: +0.20% per SD (t=2.60); civil law dummy: +0.55% (t=3.38) |

**Overall (paper's conclusion).** The positive carbon premium documented in prior studies arises from forward-looking firm sales information contained in emissions rather than a risk premium for carbon transition exposure. After properly accounting for data release lags, brown stocks underperform green stocks in the United States, consistent with ongoing investor shifts toward carbon-aware investing. Globally, carbon returns vary substantially across countries as a function of climate concern shocks, cash flow news, and local policy tightness.

## Theory / model

The paper has no formal equilibrium model. Instead, it operates within two theoretical frameworks that motivate the empirical tests.

**Framework 1: Carbon risk premium in equilibrium.** Following Bolton and Kacperczyk (2021) and Pastor, Stambaugh and Taylor (2021), brown firms face greater policy exposure during the transition to net zero and should in equilibrium earn higher expected returns. Empirically, this predicts a positive carbon premium. The paper tests this prediction using point-in-time emissions data. Bolton and Kacperczyk (2023) interpret cross-country variation in carbon returns as expected return differences driven by the global pricing of carbon transition risk; this paper reinterprets that variation as reflecting climate concern shocks and in-sample cash flow news rather than ex ante risk premia.

**Framework 2: Transition period with investor preference shifts.** During an ongoing transition to a carbon-aware equilibrium, investor preference shifts and unanticipated demand for green assets can generate negative realized carbon returns. The paper's cross-country evidence is consistent with this channel: developed markets where climate concerns have grown most have the most negative realized carbon returns.

**Identification of forward-looking bias.** The key identification idea is that emissions are derived from firm sales via IPCC emission factors (p. 624, equation 1):

$$
\text{Emissions} = \text{Activity Data} \times \text{Emission Factor} \tag{1}
$$

Because emissions scale nearly linearly with sales (regression R-squared up to 71% for U.S. scope 1, Table III), emissions released during fiscal year $$t$$ contain information about firm sales in year $$t$$. Prior studies that link returns to contemporaneous or one-month-lagged emissions effectively exploit this forward-looking sales signal. The paper's correction is to use point-in-time emissions based on actual Trucost release dates, with a median lag of 10 months (U.S.) and 12 months (international) from the fiscal year-end (Figure 1, p. 624).

## Method

The paper applies two standard empirical approaches from the asset pricing toolkit: portfolio sorts and panel regressions. Both are applied using point-in-time emissions data based on actual Trucost data release dates to eliminate forward-looking bias.

**Emission scale regressions** (Table III). To document the link between emissions and sales, the paper runs at the firm-year level (p. 624, equation 2):

$$
\log \text{Emission}_{it} = \alpha + \beta \log \text{Sales}_{it} + \varepsilon_{it}, \qquad
\Delta \text{Emission}_{it} = \alpha + \beta \Delta \text{Sales}_{it} + \varepsilon_{it} \tag{2}
$$

Standard errors are double-clustered at firm and year levels.

**Carbon intensity and firm characteristics regression** (Table III, Panel B, p. 626, equation 3):

$$
\text{Intensity}_{it} = \alpha + \beta \cdot \text{Characteristics}_{it} + \varepsilon_{it} \tag{3}
$$

where $$\text{Intensity}_{it}$$ is the scope 1 or 2 log carbon intensity available to investors at time $$t$$ and $$\text{Characteristics}_{it}$$ includes beta, size, book-to-market, ROA, asset growth, momentum, leverage, log PPE, IVol, sales growth, EPS growth, and commodity exposures.

**Portfolio sorts** follow Bolton and Kacperczyk (2021). For each month $$t$$, stocks are sorted into tercile portfolios by carbon intensity. Value-weighted monthly returns at $$t+1$$ are calculated. The high-minus-low (H-L) portfolio takes a long position in the most carbon-intensive tercile (H) and short in the least (L). Alphas are obtained by regressing H-L returns on FF6 factors (Fama and French (2018): market, SMB, HML, RMW, CMA, MOM). The U.S. sample screens common stocks following Fama and French (1992) conventions. For the international sample, stocks are screened following Hou, Karolyi and Kho (2011) to minimize outlier effects.

**Country-level portfolio sorts** (Section IV, equation 7, p. 639): for the cross-country analysis, each country's long-short return is obtained by regressing on regional FF6 factors (Fama and French (2017)):

$$
r_{it} = \alpha_i + \beta_i \text{factors}_{it} + \varepsilon_{it} \tag{7}
$$

where $$r_{it}$$ is the value-weighted long-short carbon return in country $$i$$ and $$\text{factors}_{it}$$ are FF6 factors for each region.

## Empirical specifications

**Baseline U.S. return regression** (equation 4, p. 630):

$$
r_{it} = \alpha + \beta \text{Intensity}_{it-1} + \gamma \text{Controls}_{it-1} + \nu_t + \varepsilon_{it} \tag{4}
$$

Run at the firm-month level with time fixed effects. Standard errors are double-clustered at firm and month levels. Weighted least squares is used to reduce influence from small stocks. Carbon measures are standardized to zero mean and unit variance so coefficients represent the monthly return change per one-SD increase in carbon footprint. Controls include beta, size, book-to-market, ROA, asset growth, momentum, leverage, log PPE, IVol, sales growth, EPS growth, and exposures to oil, natural gas, and commodity returns estimated over a 60-month rolling window. Results in Table VI (p. 632): scope 1 coefficient -0.19 (t=-2.52), scope 2 coefficient -0.21 (t=-2.46).

**Contemporaneous emissions regression** replicating Bolton and Kacperczyk (2021) (equation 5, p. 636):

$$
r_{it} = \alpha + \beta \text{Carbon}_{it} + \gamma \text{Controls}_{it-1} + \delta_k + \nu_t + \varepsilon_{it} \tag{5}
$$

where $$\text{Carbon}_{it}$$ is contemporaneous (same-year) log emissions growth or log emissions, with industry fixed effects $$\delta_k$$. Emissions growth is strongly positively associated with contemporaneous stock returns (Table IX, column 1: scope 1 coefficient +0.28, t=5.98).

**Sales-controlled contemporaneous regression** (equation 6, p. 636):

$$
r_{it} = \alpha + \beta \text{Carbon}_{it} + \beta \mathbf{Sales}_{it} + \gamma \text{Controls}_{it-1} + \nu_t + \varepsilon_{it} \tag{6}
$$

where $$\mathbf{Sales}_{it}$$ includes log sales and sales growth during the same emission period. After controlling for sales information, carbon emissions and emissions growth are no longer positively associated with returns and tend to be negative, consistent with the baseline result (Table IX, columns 5-6).

**Cross-country carbon return variation regression** (equation 8, p. 641):

$$
r_{it}^s = a + b \cdot X_{it-1} + \kappa \cdot Y_{it} + \nu_t + e_{it} \tag{8}
$$

where abnormal carbon returns $$r_{it}^s = \alpha_i + \varepsilon_{it}$$ are from equation (7), $$X_{it-1}$$ is lagged country characteristics (log GDP per capita, sustainable flow, climate concern), and $$Y_{it}$$ is contemporaneous cash flow shocks (earnings-day return, analyst EPS revision, sales growth). Standard errors are clustered at the monthly level. Results in Table XI (p. 642).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Trucost (S&P) | Firm-level annual carbon emissions (scope 1 and 2, tCO2e), with actual data release dates; primary emissions source | [Trucost](/wiki/licensed/trucost/) (licensed) |
| CRSP | Monthly stock returns, market capitalization, share prices; U.S. equities sample | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat (U.S.) | Firm accounting fundamentals: book-to-market, ROA, asset growth, leverage, PPE, EPS growth, sales growth | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Compustat Global | Firm accounting fundamentals for international sample; primary security on primary exchange | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Ken French Data Library | FF6 factor returns (market, SMB, HML, RMW, CMA, MOM) for factor adjustment; regional factors | [Ken French library](/wiki/datasets/ken-french/) |
| FRED (St. Louis Fed) | Natural gas price, Brent oil price, and commodity index used to estimate commodity exposures | [FRED](/wiki/datasets/fred/) |
| World Bank | Country-level GDP per capita and socioeconomic controls | No page yet |
| World Risk Poll (Lloyd's Register Foundation 2020) | Country-level climate concern measure (fraction perceiving climate change as very or somewhat serious threat) | No page yet |
| Climate Change Performance Index | Country-level climate policy tightness score | No page yet |
| Morningstar Sustainable Funds | Country-level quarterly sustainable investor flows as fraction of market cap | No page yet |

Sample: June 2009 to December 2021 (U.S. and global). U.S. sample: 211,495 firm-month observations; global: ~92,790 (country-industry-time regressions).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13402) if you are: studying or replicating the carbon premium literature and need the full methodology for correcting the data release lag (Section I.C, pp. 622-627); conducting international/cross-country analysis of carbon returns and need the country-level dispersion results (Section IV, pp. 639-643); assessing whether prior evidence on the carbon premium is robust to proper timing of emissions data; or working on climate policy's effect on asset prices. Table IV (p. 628) is the key U.S. result; Table VII (p. 633) is the global result; Table XI (p. 642) is the cross-country driver analysis.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Zhang, Shaojun. "Carbon Returns across the Globe."
> *The Journal of Finance* 80, no. 1 (February 2025): 615-645.
> DOI: 10.1111/jofi.13402. © 2024 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
