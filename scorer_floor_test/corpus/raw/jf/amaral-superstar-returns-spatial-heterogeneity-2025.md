---
title: "Superstar Returns: Amaral, Dohmen, Kohl & Schularick (2025)"
description: >-
  Distilled: Large metropolitan areas earn about 95 to 100 basis points less
  per year in total housing returns than the rest of the same country, driven by
  persistently lower rental yields that more than offset their well-known capital
  gain advantage. The return gap is rationalized as compensation for higher
  idiosyncratic and covariance risk in smaller, less liquid housing markets.
  J. Finance 2025, CC BY 4.0. Seven core results with source locators, datasets
  used, the theoretical framework (CAPM-style covariance pricing plus
  idiosyncratic risk), and the empirical specifications.
sidebar:
  label: Amaral-Dohmen-Kohl-Schularick 2025
  order: 1
tags: [paper-summary, housing, real-estate, asset-pricing, spatial-economics,
       urban-economics, risk-return, panel-regression, new-fact, new-data,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:gyourko-mayer-sinai, data:corelogic, data:zillow,
       data:jst-macrohistory, data:msci-real-estate]
paper:
  authors: Francisco Amaral, Martin Dohmen, Sebastian Kohl, Moritz Schularick
  authorList:
    - { family: Amaral, given: Francisco, affiliation: University of Zurich and Swiss Finance Institute }
    - { family: Dohmen, given: Martin, orcid: "0000-0003-2450-9189", affiliation: Macro Finance Lab, University of Bonn }
    - { family: Kohl, given: Sebastian, orcid: "0000-0002-8358-6021", affiliation: MPIfG Cologne and FU Berlin }
    - { family: Schularick, given: Moritz, affiliation: Kiel Institute for the World Economy and Sciences Po Paris }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 3057–3094
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13479
  jel:
    codes: [G12, R30, E21]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ['Housing Market and Economics', 'Housing, Finance, and Neoliberalism', 'Regional Economics and Spatial Analysis']
  dataAccess: licensed-commercial
  outcome:
    - total housing returns by city size (log points per year)
    - rental yields by city size
    - capital gains by city size
    - idiosyncratic housing price risk by MSA size
    - covariance of housing returns with income growth by MSA size
  outcomeClass: [asset-prices, household-finance]
  license: 'CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-08-19; corroborated by artifact p.3057 Creative Commons Attribution License notice)'
  licenseShort: CC BY 4.0
  access: open
  machineAccess: 'blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-05)'
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 0
  methods:
    role: both
    family: descriptive
    buildsFrom: [panel-regression, fama-macbeth]
    identification: descriptive
  contributionType: [new-data, new-fact, measurement]
  introducesData: true
  mechanisms: [risk-sharing, liquidity]
  scope:
    region: global (15 OECD countries)
    assetClass: residential real estate
    period: 1870-01..2018-12
    frequency: annual
    dataType: [market, accounting, administrative, other]
    granularity: [aggregate, individual]
    n: "27 cities in 15 OECD countries (main sample, 1950-2018); 316 U.S. MSAs (1950-2018); 42 West German cities (1975-2018)"
  findings:
    - ref: R1
      outcome: total housing returns by city size (log points per year)
      metric: basis-points
      value: "large cities earn -95 to -100 bps per year vs. national portfolio (Table III Panel A: difference = -0.95***, SE 0.23); vs. rest-of-country difference = -1.04*** (SE 0.26)"
      direction: negative
      vsBenchmark: national housing portfolio and rest-of-country portfolio, 1950-2018
    - ref: R2
      outcome: rental yields by city size
      metric: basis-points
      value: "rental returns in 27 large cities average 3.55 log points vs. 4.94 national; difference = -1.39*** (SE 0.04); vs. rest-of-country = -1.65*** (SE 0.05) (Table III Panel A)"
      direction: negative
      vsBenchmark: national and rest-of-country averages, 1950-2018
    - ref: R3
      outcome: capital gains by city size
      metric: basis-points
      value: "capital gains in 27 large cities = 2.25 log points vs. 1.82 national; difference = +0.43* (SE 0.23); vs. rest-of-country = +0.61** (SE 0.26) (Table III Panel A)"
      direction: positive
      vsBenchmark: national and rest-of-country averages; capital gain advantage dominated by rental yield gap
    - ref: R4
      outcome: total housing returns by city size (log points per year)
      metric: basis-points
      value: "316 U.S. MSAs: large vs. rest total return = -0.52*** (SE 0.15); large vs. small = -0.80*** (SE 0.20) (Table V)"
      direction: negative
      vsBenchmark: rest-of-sample and smallest 5% of U.S. MSAs, 1950-2018
    - ref: R5
      outcome: total housing returns by city size (log points per year)
      metric: basis-points
      value: "42 West German cities: large vs. rest total return = -0.45* (SE 0.25); large vs. small = -0.57* (SE 0.35) (Table VII)"
      direction: negative
      vsBenchmark: rest-of-sample and smallest 5% of German cities, 1975-2018
    - ref: R6
      outcome: covariance of housing returns with income growth by MSA size
      metric: coefficient
      value: "large MSAs vs. rest: covariance difference = -0.55** (SE 0.273, multiplied by 10,000); large vs. small = -1.94*** (SE 0.573) (Table VIII, row 1)"
      direction: negative
      vsBenchmark: smaller MSAs; large cities have significantly lower covariance risk
    - ref: R7
      outcome: idiosyncratic housing price risk by MSA size
      metric: probability
      value: "idiosyncratic risk in smallest MSAs = 12.34% of sales price; largest MSAs = 9.28%; roughly 25% lower in largest MSAs (Figure 7); time on market in large vs. small MSAs = -29.67*** days (SE 9.918) (Table IX)"
      direction: negative
      vsBenchmark: smallest MSAs; large cities show lower idiosyncratic risk and higher liquidity
  resultType: overturns
  relatesTo:
    - { cite: 'Gyourko, Mayer & Sinai (2013)', doi: '10.1016/j.jue.2014.02.003', relation: extends, note: 'extends their U.S. MSA superstars data to 2018 and adds international comparison; shows rental yields offset their documented capital gain advantage' }
    - { cite: 'Jorda, Schularick & Taylor (2019)', relation: extends, note: 'extends their national housing return series to the city level and constructs rest-of-country portfolios from their national data' }
    - { cite: 'Demers & Eisfeldt (2022)', doi: '10.1111/1540-6229.12353', relation: contradicts, note: 'overturns the view that large coastal U.S. cities are better investments; rental return differences are larger and more persistent than capital gain differences' }
    - { cite: 'Giacoletti (2021)', doi: '10.1093/rfs/hhab033', relation: builds-on, note: 'uses their approach to estimate idiosyncratic housing price risk from transaction-level data' }
    - { cite: 'Piazzesi & Schneider (2016)', relation: cites, note: 'cited for the importance of local non-diversifiable housing portfolios and covariance with consumption' }
  openQuestions:
    - 'Whether the return differential also holds at finer geographic scales within cities, and how within-city heterogeneity interacts with the city-size gradient (p. 3091).'
    - 'The mechanism behind lower covariance risk in large cities cannot be fully pinned down with available decadal income data; higher-frequency consumption data by region would be needed to disentangle the covariance channel (pp. 3086-3087).'
    - 'The interplay between the spatial return gap and wealth inequality dynamics across households located in different cities warrants further study (p. 3091).'
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-05, role: extracted, note: "Full text read (pp. 3057-3094); seven results extracted from Tables III, V, VII, VIII, IX and Figure 7. Not human-verified. Not reproduced." }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-05, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core-results rows confirmed correct. Fixed: removed spurious '(5, adapted)' equation tag on panel regression (PDF eq 5 is the idiosyncratic risk equation, p.3087, not the panel spec); corrected resultType from new-finding to overturns (contradicts edge present)." }
  licenceVerification:
    - { source: Crossref REST API works/10.1111/jofi.13479, checked: 2026-06-05, by: paper-distiller (claude-sonnet-4-6), found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-19' }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it builds on (CAPM-style covariance pricing of housing risk), and the empirical design with the estimating specifications: enough to know what it found and how, without reading all 38 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13479).

## TL;DR

The paper introduces the first comprehensive city-level data set on housing returns for 15 OECD countries over up to 150 years (27 cities, balanced panel after 1950) and documents a new stylized fact: large metropolitan areas earn persistently lower total returns on housing than the rest of the country, roughly 95 to 100 basis points per year. Higher capital gains in large cities are more than offset by lower rental yields. This finding is confirmed for all 316 U.S. MSAs (1950-2018) and 42 West German cities (1975-2018). The paper rationalizes the pattern in a rational-expectations equilibrium: large cities are safer investments, with lower covariance between housing returns and local income growth and lower idiosyncratic price risk (because their housing markets are more liquid). Smaller, riskier locations must offer higher expected returns to attract capital.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Large cities earn persistently lower total housing returns** than the national portfolio and the rest of the country | Table III Panel A, p. 3072 | 27-city average difference vs. national: -0.95\*\*\* log points/year (SE 0.23); vs. rest-of-country: -1.04\*\*\* (SE 0.26); N = 1,767 |
| R2 | **Rental returns are the driver**: large cities have significantly lower rental yields that more than offset their capital gain advantage | Table III Panel A, p. 3072 | Rental return difference vs. national: -1.39\*\*\* (SE 0.04); vs. rest-of-country: -1.65\*\*\* (SE 0.05) |
| R3 | **Capital gains are higher in large cities**, but not enough to reverse the total return gap | Table III Panel A, p. 3072 | Capital gain difference vs. national: +0.43\* (SE 0.23); vs. rest-of-country: +0.61\*\* (SE 0.26) |
| R4 | **U.S. MSA evidence confirms the pattern**: large vs. small MSAs differ by -0.80 log points/year in total returns | Table V, p. 3077 | Large (top 5%) vs. rest: -0.52\*\*\* (SE 0.15); large vs. small (bottom 5%): -0.80\*\*\* (SE 0.20); N = 2,184 |
| R5 | **German city evidence confirms the pattern**: large vs. small German cities show the same negative return gap | Table VII, p. 3081 | Large (top 5%) vs. rest: -0.45\* (SE 0.25); large vs. small: -0.57\* (SE 0.35); N = 1,848 |
| R6 | **Covariance risk is lower in large cities**: housing return-income growth covariance is significantly smaller in large MSAs than in small ones | Table VIII row 1, p. 3086 | Large vs. rest: -0.55\*\* (SE 0.273, x10,000); large vs. small: -1.94\*\*\* (SE 0.573); N = 316 MSAs |
| R7 | **Idiosyncratic risk and illiquidity are higher in small cities**: sales-level idiosyncratic risk is roughly 25% higher in smallest MSAs; time on market is ~30 days longer | Figure 7 p. 3088; Table IX p. 3090 | Idiosyncratic risk: smallest MSAs 12.34%, largest 9.28% of sales price; time on market: large vs. small = -29.67\*\*\* days (SE 9.918) |

**Overall (paper's conclusion).** The conventional wisdom that large superstar cities are the best places to invest in residential real estate is overturned once rental yields are included. Capital gains favor large cities, but rental yields are persistently lower there, so total returns are lower by roughly 1 percentage point per year. This overturns the view in Demers and Eisfeldt (2022), who focused on local-market price volatility and found no significant return differences across U.S. MSAs (their sample excluded the 1970s period of high rental yields). The finding is also consistent with evidence on within-city return gradients, and extends the national housing return evidence of Jorda, Schularick & Taylor (2019) to the city level. The equilibrium framework follows the logic of Piazzesi and Schneider (2016): large cities are diversified, liquid, and less exposed to local income shocks, so investors require a lower risk premium. Riskier smaller locations must compensate with higher total expected returns.

## Theory / model

The paper has no new formal theory but applies the standard consumption CAPM pricing equation to housing markets. For a utility-maximizing household the excess expected log return on a housing asset equals a risk-premium proportional to the asset's covariance with consumption growth (p. 3085, equation 4):

$$
\ln \mathbb{E}[R_{t+1}] - \ln R_f = \gamma \, Cov\!\left[\ln\!\left(\frac{C_{t+1}}{C_t}\right),\, \ln R_{t+1} - \ln R_f\right] \tag{4}
$$

where $$R_{t+1}$$ is the total return, $$R_f$$ the risk-free rate, $$\gamma > 0$$ the coefficient of risk aversion, and $$C_{t+1}/C_t$$ is consumption growth (approximated by regional income growth due to data availability). An asset with higher co-movement with future income provides less insurance against income shocks and must earn a higher return. If large cities have lower covariance with local income, they are safer hedges and should earn lower returns.

A second channel is idiosyncratic risk. Because housing is large, indivisible, and illiquid, and most households own a single property, idiosyncratic price shocks are not diversified away. As Giacoletti (2021) and Sagi (2021) show, idiosyncratic volatility is priced in housing and is directly related to housing market illiquidity. The paper thus tests two predictions: (i) covariance of housing returns with income is lower in large cities, and (ii) idiosyncratic housing price risk is lower in large (more liquid) cities.

The equilibrium identity linking national, city, and rest-of-country returns through population weights (equation 3, p. 3069) is:

$$
\text{National return}_t = w_{t-1} \times \text{Large-city return}_t + (1 - w_{t-1}) \times \text{RoC return}_t \tag{3}
$$

where $$w$$ is the relative weight of the large city in the national housing series. This allows rest-of-country (RoC) returns to be backed out from national series and city-level data.

Total housing return decomposition, used throughout (equation 1, p. 3065):

$$
\text{Total return}_t = \underbrace{\frac{P_t - P_{t-1}}{P_{t-1}}}_{\text{Capital gain}} + \underbrace{\frac{R_t(1-c)}{P_{t-1}}}_{\text{Net rent return}} \tag{1}
$$

where $$P_t$$ is the house price at time $$t$$, $$R_t$$ the gross rent, and $$c$$ the share of operating costs in gross rent. Rental return series are constructed using the rent-price approach (equation 2, p. 3065):

$$
\frac{RI_{t+1}}{HPI_{t+1}} = \left(\frac{RI_{t+1}/RI_t}{HPI_{t+1}/HPI_t}\right) \frac{RI_t}{HPI_t} \tag{2}
$$

anchored to 2018 MSCI benchmark rent-price ratios and extrapolated backward using the ratio of the rent index to the house price index growth rates.

## Method

The paper's methodological contribution is data construction rather than a new estimator. The estimation strategy uses two variants:

**Paired t-tests (main international analysis, Tables III and IV).** For each of the 27 city-country pairs, the paper computes the average annual city-level log return and the average national return for the same country and period (post-1950 for the main analysis). Differences are paired by country. Standard errors are reported in parentheses. The null is equality of city and national means. This is not an OLS regression with fixed effects; it is a direct comparison of city-level to population-weighted national averages, with the rest-of-country (RoC) series derived by subtracting the large-city contribution from the national series.

**Random effects panel regression (U.S. MSA and German city sub-samples, Tables V-VII).** For the cross-section of cities within a country, the paper estimates:

$$
y_{s,t} = \alpha + \beta \cdot \mathbf{1}[\text{large city}]_s + \lambda_t + \varepsilon_{s,t}
$$

where $$y_{s,t}$$ is the dependent variable (log capital gain, log rental yield, or log total return) for city (MSA) $$s$$ in decade $$t$$, $$\mathbf{1}[\text{large city}]_s$$ is a dummy for being at or above the 95th percentile of the city population distribution, and $$\lambda_t$$ are year fixed effects. Standard errors are clustered at the city level. This is the `panel-regression` estimator from the registry.

**Idiosyncratic risk estimation (equation 5, p. 3087):**

$$
\Delta p_{l,i,t} = \Delta v_{l,t} + BX_i + \sigma_{l,\text{idiosyncratic}}\, \varepsilon_{i,t} \tag{5}
$$

where $$\Delta p_{l,i,t}$$ is the log capital gain on sale of property $$i$$ in MSA $$l$$ at time $$t$$, $$\Delta v_{l,t}$$ is the growth in local county house prices (FHFA/Zillow), $$BX_i$$ is a vector of house and transaction characteristics (including zip-code and time fixed effects), and $$\sigma_{l,\text{idiosyncratic}}$$ is the standard deviation of the sales-specific shock, estimated as the residual component. The estimator follows Giacoletti (2021).

## Empirical specifications

**Main specification (international panel, R1-R3).** The comparison is between the 27-city population-weighted average and the national housing portfolio return (Jorda, Schularick & Taylor (2019), extended to 2018), and separately the rest-of-country (RoC) portfolio. Paired t-tests on the time-series average of the annual city minus national (or city minus RoC) return difference. Sample: 1950-2018 (N=1,767 city-year obs). Standard errors computed from the paired differences. The result: -0.95\*\*\* log points per year (SE 0.23) total return gap vs. national; -1.04\*\*\* (SE 0.26) vs. RoC (Table III Panel A, p. 3072).

**U.S. MSA sub-sample (R4).** Gyourko, Mayer & Sinai (2013) extended to 2018 via American Community Survey data. 316 MSAs, decadal frequency 1950-2018. Random effects panel regression of log capital gain, log rental yield, and log total return on a large-MSA dummy (top 5% by 1950 population) and decade fixed effects; SE clustered at the MSA level. For total returns: large vs. rest = -0.52\*\*\* (SE 0.15), large vs. small = -0.80\*\*\* (SE 0.20); N=2,184 (Table V, p. 3077).

**German cities sub-sample (R5).** 42 West German cities 1975-2018 from Immobilienverband Deutschland (IVD) market reports. Random effects panel regression analogous to U.S. specification. Large cities = top 5% by 1975 population. Total return: large vs. rest = -0.45\* (SE 0.25), large vs. small = -0.57\* (SE 0.35); N=1,848 (Table VII, p. 3081).

**Covariance risk test (R6).** MSA-specific covariances computed as $$Cov_s = Cov(R_s - R_f, y_s)$$ over decadal periods 1950-2018, where $$R_s$$ is total log housing return and $$y_s$$ is log income growth from U.S. Census. Cross-sectional regression of covariance on a large-MSA dummy and robust SE. Result: large MSAs have significantly lower covariance with income growth (Table VIII, p. 3086). The identification is descriptive: no causal design.

**Idiosyncratic risk test (R7).** Corelogic repeat-sales transaction data for 248 U.S. MSAs 1990-2020. Residual idiosyncratic risk estimated following Giacoletti (2021) (equation 5). Liquidity proxied by median time on market and asking price discount from Zillow.com for 277 MSAs 2012-2020 (Table IX, p. 3090).

**Robustness.** Results hold (i) pre- and post-1990 sub-periods (Table IV Panel B), (ii) with alternative rental yield benchmarks from Numbeo and country-specific sources (Table IV Panel A), (iii) excluding rent-control periods and different tax regimes, (iv) using nominal series, (v) with outlier exclusion (top/bottom 5% annual returns), and (vi) using annual Agorastos et al. (2024) hedonic series for 21 U.S. cities 1920-2006 (Table VI).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Authors' new city-level housing return database (27 cities, 15 OECD countries, 1870-2018) | Main international analysis: house price indices, rent indices, total returns | No page yet (hand-collected from yearbooks, tax records, notaries, newspapers, MSCI) |
| Gyourko, Mayer & Sinai (2013) MSA database extended to 2018 via ACS | U.S. cross-section analysis: 316 MSAs, decadal returns 1950-2018 | [Superstar Cities (GMS)](/wiki/datasets/gyourko-mayer-sinai/) |
| German IVD / RDM market reports (42 cities, 1975-2018; 127 cities, 1992-2018) | German city cross-section: annual housing returns | No page yet |
| Jorda, Schularick & Taylor (2019) macro-history database | National housing return benchmarks for 15 OECD countries | No page yet |
| MSCI real estate investor yield data | 2018 rental yield benchmark for main data set | [no page yet](/wiki/datasets/) |
| Corelogic deeds / repeat-sales transaction data (248 MSAs, 1990-2020) | Idiosyncratic housing price risk estimation | [CoreLogic](/wiki/licensed/corelogic/) (licensed) |
| FHFA county house price indices + Zillow.com MSA data (277 MSAs, 2012-2020) | Liquidity proxies (time on market, asking price discount) and county price controls | [Zillow research](/wiki/datasets/zillow/) |
| Agorastos, Gray, Lyons & Shertzer (2024) hedonic series (21 U.S. cities, 1920-2006) | Long-run robustness for U.S. sub-sample | No page yet |

Sample: main international analysis 1950-2018 (balanced panel), with some series starting 1870. U.S. MSA analysis decadal 1950-2018; German cities annual 1975-2018.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13479) if you are: studying within-asset-class return heterogeneity across locations; building spatial housing pricing models; replicating the long-run city-level return series for a specific country (the Data Appendix details all sources); extending the U.S. MSA or German city analysis; or examining the role of housing risk in household portfolio choice. Detailed robustness tables (rent control, alternative benchmarks, outlier exclusion) are in the Internet Appendix.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Amaral, Francisco, Martin Dohmen, Sebastian Kohl, and Moritz Schularick.
> "Superstar Returns? Spatial Heterogeneity in Returns to Housing."
> *The Journal of Finance* 80, no. 5 (October 2025): 3057–3094.
> DOI: 10.1111/jofi.13479. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
