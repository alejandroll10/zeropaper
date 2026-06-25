---
title: "The Global Credit Spread Puzzle: Huang, Nozawa & Shi (2025)"
description: >-
  Distilled: Structural credit risk models systematically underpredict
  investment-grade corporate bond spreads over government bonds and swap rates
  across eight developed economies, constituting a global credit spread puzzle.
  Incorporating endogenous bond market illiquidity via a He-Milbradt search
  model substantially mitigates the puzzle and raises individual-bond
  cross-sectional fit in every country. J. Finance 2025, CC BY-NC-ND 4.0.
  Eight core results with source locators, datasets used, the models (BC, CDG,
  HM), and the estimating specifications.
sidebar:
  label: Huang-Nozawa-Shi 2025
  order: 1
tags: [paper-summary, asset-pricing, credit-risk, fixed-income, corporate-bonds,
       structural-models, liquidity, international, peer-reviewed, unreplicated,
       data:wrds, data:markit]
paper:
  authors: Jing-Zhi Huang, Yoshio Nozawa, Zhan Shi
  authorList:
    - { family: Huang, given: Jing-Zhi, orcid: "0000-0001-8769-9130", affiliation: Smeal College of Business, Penn State University }
    - { family: Nozawa, given: Yoshio, orcid: "0000-0002-6395-2688", affiliation: Rotman School of Management, University of Toronto }
    - { family: Shi, given: Zhan, orcid: "0000-0002-1265-0356", affiliation: PBC School of Finance, Tsinghua University }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 101–162
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13409
  jel:
    codes: [G12, G15, G14]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Credit Risk and Financial Regulations', 'Banking stability, regulation, efficiency', 'Financial Distress and Bankruptcy Prediction']
  dataAccess: licensed-commercial
  outcome:
    - corporate bond yield spreads over swap rates (investment-grade)
    - corporate bond yield spreads over government bond yields (investment-grade)
    - mean pricing error of structural credit models
    - cross-sectional R-squared of individual IG bond spreads
  outcomeClass: [asset-prices, credit-risk]
  license: >-
    CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0,
    start 2024-12-20; corroborated by artifact p.101 Creative Commons
    Attribution-NonCommercial-NoDerivs License notice)
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "blocked-paywall (Wiley site wrapper; CC BY-NC-ND VOR licence confirmed in Crossref DOI metadata 2026-06-06)"
  redistribution: extract-only (CC BY-NC-ND 4.0 permits sharing but prohibits derivatives and commercial use; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 14
  methods:
    role: both
    family: structural
    buildsFrom: [affine-term-structure, search-bargaining-otc, gmm]
    identification: descriptive
  contributionType: [new-fact, new-method, measurement]
  mechanisms: [liquidity, search-frictions, intermediary-constraint]
  scope:
    region: global
    assetClass: investment-grade corporate bonds
    period: 1997-01..2017-12
    frequency: monthly
    dataType: [market, accounting]
    granularity: [security, firm]
    n: "corporate bonds from eight developed economies (AUS, CAN, FRA, DEU, ITA, JPN, GBR, USA), 1997-2017 (2003 start for ITA, 2007 for AUS); U.S. bond sample 1987-2015"
  findings:
    - ref: R1
      outcome: corporate bond yield spreads over swap rates (investment-grade)
      metric: basis-points
      value: "BC model MPE significantly negative for 53 of 72 IG/country/d bins (17+19+17 across three d estimates); at country level underpredicts for 17 of 24 IGctry/d bins (Panel A, Table V, p.126)"
      direction: negative
      vsBenchmark: model underpredicts observed IG spread; MPE < 0 means model-implied < data
    - ref: R2
      outcome: corporate bond yield spreads over swap rates (investment-grade)
      metric: basis-points
      value: "MPEs in bps for AA+, A, BBB in GBR: (-27, -39, -92) under BC(dFS); AUS: (-98, -125, -151) under BC(dFS) (Table IV, Panel A, pp.122-123)"
      direction: negative
      vsBenchmark: BC model underpredicts IG spreads in AUS, CAN, GBR, ITA, USA; puzzle disappears in JPN
    - ref: R3
      outcome: corporate bond yield spreads over swap rates (investment-grade)
      metric: basis-points
      value: "CDG model still underpredicts mean IG spread for 16 of 24 IG/country bins and 6 of 8 IGctry groups, compared with 17 and 6 under BC(dFS) (Table IV, pp.122-124; Table IX Panel A1, p.151)"
      direction: negative
      vsBenchmark: CDG adds stationary leverage; overall improvement limited; GCSP robust to CDG
    - ref: R4
      outcome: corporate bond yield spreads over swap rates (investment-grade)
      metric: basis-points
      value: "HM model reduces bins with significantly negative MPE from 17 under BC(dFS) to 6 under HM(dFS); UK MPEs narrow from (-27,-39,-92) to (1,13,-26); AUS from (-98,-125,-151) to (6,-15,-10) (Table IV, p.122; Table V, p.126)"
      direction: negative
      vsBenchmark: HM model substantially mitigates GCSP; puzzle disappears in FRA, DEU, ITA, USA under industrial issuers
    - ref: R5
      outcome: cross-sectional R-squared of individual IG bond spreads
      metric: r-squared
      value: "HM R2 ranges 34%-79% (AUS: 79%; FRA: 34%) vs BC R2 19%-35% (AUS: 19%; CAN: 35%) in bond-level panel regressions (Table IX Panel A2, p.152)"
      direction: positive
      vsBenchmark: HM model substantially raises cross-sectional R2 over BC model in every country
    - ref: R6
      outcome: cross-sectional R-squared of individual IG bond spreads
      metric: r-squared
      value: "Time-series correlation rho^IG under HM(dFS) ranges 0.65 (FRA) to 0.94 (GBR) vs 0.55 (FRA) to 0.90 (GBR) under BC(dFS) (Table IX Panel A3, p.152)"
      direction: positive
      vsBenchmark: HM model also better captures time-series variation in average IG spreads in every country
    - ref: R7
      outcome: corporate bond yield spreads over government bond yields (investment-grade)
      metric: basis-points
      value: "Government bond yield-based CSP is stronger: BC underpredicts for 67 of 72 IG/country/d bins vs 53 for swap-rate-based CSP (Table IX Panel B1, p.153)"
      direction: negative
      vsBenchmark: government bond yield-based puzzle stronger than swap rate-based; HM mitigates but poses larger challenge
    - ref: R8
      outcome: cross-sectional R-squared of individual IG bond spreads
      metric: r-squared
      value: "Under HM(dFS, Govt), R2 ranges from 0.08 (CAN) to 0.75 (AUS); under BC(dFS, Govt), R2 ranges 0.02 (CAN) to 0.30 (ITA) (Table IX Panel B2, p.153)"
      direction: positive
      vsBenchmark: HM model raises R2 for government bond yield-based spreads in every country except JPN
  resultType: new-finding
  relatesTo:
    - { cite: "Huang and Huang (2012)", doi: '10.1093/rapstu/ras011', relation: extends, note: "global extension of their finding that structural models underpredict U.S. IG corporate-Treasury spreads (the original U.S. credit spread puzzle)" }
    - { cite: "Black and Cox (1976)", doi: '10.1111/j.1540-6261.1976.tb01891.x', relation: builds-on, note: "BC model is the baseline structural model with flat default boundary for coupon-bearing bonds" }
    - { cite: "Collin-Dufresne and Goldstein (2001)", relation: tests, note: "CDG model with stationary leverage is tested as an improvement to BC; GCSP is found robust to it" }
    - { cite: "He and Milbradt (2014)", doi: '10.3982/ecta11039', relation: builds-on, note: "HM model is a reduced-form variant of their endogenous liquidity model; adapted to isolate search-frictions liquidity component" }
    - { cite: "Feldhutter and Schaefer (2018)", doi: '10.1093/rfs/hhy032', relation: tests, note: "FS method for estimating default boundary d is implemented and compared; main GCSP finding is robust to their method" }
    - { cite: "Bai, Goldstein, and Yang (2020)", doi: '10.1016/j.jfineco.2020.02.009', relation: tests, note: "BGY method for estimating d is compared; conclusions robust across all three d estimates" }
    - { cite: "Duffie, Garleanu, and Pedersen (2005)", relation: builds-on, note: "OTC search-frictions framework underlying the secondary market liquidity model" }
  openQuestions:
    - "Country-level search parameter estimates are used for all bonds; credit-rating- or sector-specific estimates could better capture heterogeneity in corporate bond illiquidity across countries (p.158)."
    - "The HM model captures spread levels but its capacity to account for variation in credit spread changes warrants further investigation; only 6-31% of spread-change variation is explained by structural models (p.158, footnote 24)."
    - "Additional credit risk channels such as stochastic asset volatility may also improve model performance (p.159, footnote 25)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 101-162); eight results extracted from Tables IV, V, IX (pp. 122-153). Not human-verified. Not reproduced. Replication code is referenced in the paper (p.162 Supporting Information) but has not been run here." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all eight Core-results rows confirmed against Tables IV (pp. 122-124), V (pp. 126-127), and IX (pp. 151-153); equations (1)-(6), (10), (13), (14) verified term-by-term against PDF pp. 112-113, 137, 139-141; no errors found." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13409", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2024-12-20" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the models it tests (Black-Cox, Collin-Dufresne-Goldstein, He-Milbradt), and the specifications behind each result: enough to know what it found and how, without reading all 62 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13409).

## TL;DR

The paper asks whether the U.S. credit spread puzzle (CSP) extends globally. Huang and Huang (2012) documented that structural models underpredict U.S. IG corporate-Treasury spreads; this paper tests whether the same pattern holds outside the United States. Using security-level pricing data on IG corporate bonds from eight developed economies and global default data, the authors implement two standard pure-default structural models (Black and Cox (1976) and Collin-Dufresne and Goldstein (2001)) and a reduced-form variant of the He and Milbradt (2014) model with endogenous bond market illiquidity, building on the OTC search-and-bargaining framework of Duffie, Garleanu, and Pedersen (2005). The default boundary is estimated via three methods including those of Feldhutter and Schaefer (2018) and Bai, Goldstein, and Yang (2020). The paper finds robust evidence that pure default-risk structural models tend to underpredict IG credit spreads over swap rates and, even more so, over government bond yields in all countries except Japan, establishing a "global credit spread puzzle" (GCSP). The CDG model improves overall performance but does not resolve the puzzle. However, incorporating endogenous OTC search-and-bargaining frictions into the BC model substantially mitigates the GCSP and raises the model's cross-sectional R-squared for individual IG bond spreads in every country from 19-35% (BC model) to 34-79% (HM model).

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **BC model significantly underpredicts IG credit spreads over swap rates** across most IG/country groups; constitutes a global credit spread puzzle | Table IV, pp. 122-123; Table V, p. 126; Table IX Panel A1, p. 151 | Significantly negative MPE for 53 of 72 IG/country/d bins; at country level, underpredicts for 17 of 24 IGctry/d bins |
| R2 | **Underprediction is substantial in AUS, CAN, GBR, ITA, and USA**; BC model overpredicts for most JPN groups | Table IV Panel A, pp. 122-123 | AUS MPEs for AA+, A, BBB under BC(dFS): (-98, -125, -151) bps; GBR: (-27, -39, -92) bps; JPN AA+: +12.6 bps |
| R3 | **GCSP is robust to the CDG model with stationary leverage ratios**; CDG improves mean pricing but still underpredicts for 16 of 24 IG/country bins | Table IV (CDG rows), pp. 122-124; Table IX Panel A1, p. 151 | CDG underpredicts for 16 IG/country bins vs 17 for BC(dFS); underpredicts for 6 of 8 IGctry groups vs 6 for BC(dFS) |
| R4 | **HM model with endogenous illiquidity substantially mitigates the GCSP**: bins with significantly negative MPE drop from 17 (BC) to 6 (HM) | Table IV (HM rows) pp. 122-123; Table V p. 126; Table IX Panel A1, p. 151 | GBR MPEs narrow from (-27,-39,-92) to (1,13,-26) bps; AUS from (-98,-125,-151) to (6,-15,-10) bps; puzzle disappears in FRA, DEU, ITA, and USA for industrial issuers excluding negative spreads |
| R5 | **HM model substantially raises cross-sectional R2** for individual IG bond spreads in every country | Table IX Panel A2, p. 152 | HM R2: 34% (FRA) to 79% (AUS); BC R2: 19% (AUS) to 35% (CAN); slope coefficient closer to 1 under HM in every country except AUS |
| R6 | **HM model also captures time-series variation in IG spreads better** than BC or CDG in every country | Table IX Panel A3, p. 152 | Time-series correlation rho^IG under HM(dFS): 0.65 (FRA) to 0.94 (GBR) vs 0.55 (FRA) to 0.90 (GBR) under BC(dFS) |
| R7 | **Government bond yield-based GCSP is stronger** than the swap rate-based version and poses a tougher challenge to the HM model | Table IX Panel B1, p. 153 | BC underpredicts for 67 of 72 IG/country/d bins (govt) vs 53 (swap); HM overcomes underprediction for only 9 of 21 IG/country bins (govt) vs 13 of 19 bins (swap, excl. neg. spreads) |
| R8 | **HM model raises R2 for government yield-based spreads** in every country except JPN; gains are largest in AUS and ITA | Table IX Panel B2, p. 153 | R2 under HM(dFS, Govt): 0.08 (CAN) to 0.75 (AUS); R2 under BC(dFS, Govt): 0.02 (CAN) to 0.30 (ITA) |

**Overall (paper's conclusion).** Pure default-risk structural models underestimate IG corporate bond credit spreads in global developed bond markets, especially over government bond yields. Incorporating mean-reverting leverage (CDG) provides limited relief. Incorporating OTC search-and-bargaining frictions (HM) substantially mitigates the GCSP for both swap rate-based and government bond yield-based spreads, and improves the cross-sectional fit of individual bond spreads in every country, suggesting that corporate bond illiquidity is a central missing ingredient in standard structural pricing models.

## Theory / model

The paper tests two classes of structural models.

**Baseline: Black-Cox (BC) model** (p. 110-112). Consider a corporate bond with fixed maturity $$T$$, face value $$K$$, and continuous coupon rate $$c$$. Default occurs when firm value falls to a flat default boundary for the first time before or at $$T$$. Under constant risk-free rate $$r$$, the bond price at time $$t$$ is (equation (1), p. 112):

$$
D^{BC}(t, T) = \frac{cK}{r} + e^{-r(T-t)} K \left(1 - \frac{c}{r}\right)(1 - \pi^Q(t,T)) + K\!\left(R - \frac{c}{r}\right) G(t,T), \tag{1}
$$

where $$\pi^Q(t,T)$$ is the risk-neutral default probability over $$(t, T]$$, $$G(t,T)$$ is the time-$$t$$ price of the Arrow-Debreu default claim, and $$R$$ is the state-dependent recovery rate. The model-implied yield $$y(t,T)$$ solves:

$$
D^{BC}(t,T) = \frac{cK}{y}\left(1 - e^{-y(T-t)}\right) + Ke^{-y(T-t)}, \tag{2}
$$

and the model-implied credit spread is $$s^{BC}(t,T) = y(t,T) - r$$.

**CDG model** (p. 136-137). Collin-Dufresne and Goldstein (2001) augment the BC model to allow stationary leverage ratios. The total debt level $$K_t$$ follows the process (equation (4), p. 137):

$$
d\ln K_t = \kappa\left[-\nu - \ln(K_t/A_t)\right]dt, \tag{4}
$$

where $$\kappa$$ controls the speed at which log-leverage reverts to the target ratio under the risk-neutral measure: $$\ln(\bar{L}^Q) \equiv \frac{-r + \delta + (\sigma^A)^2/2}{\kappa} - \nu$$. Parameters $$\kappa$$, $$\nu$$, and $$\bar{L}^Q$$ are estimated via GMM on single-name CDS spreads for each country.

**HM model with endogenous illiquidity** (Section IV, pp. 138-148). The paper adapts the He and Milbradt (2014) framework to study the incremental effect of OTC search-and-bargaining frictions. L-type investors (hit by liquidity shocks, holding-cost $$\chi$$) and H-type investors (not hit) trade the bond at Poisson intensities $$\lambda$$ (customer-to-dealer) and $$\beta$$ (backward L-to-H transition). The H-type and L-type bond valuation functions $$D_H(t,T)$$ and $$D_L(t,T)$$ satisfy (equation (5), p. 139):

$$
\begin{bmatrix} D_H(t,T) \\ D_L(t,T) \end{bmatrix} = Z^{-1} \begin{bmatrix} c \\ c - \chi \end{bmatrix} K + e^{-Z(T-t)}\!\left(\begin{bmatrix} K \\ K \end{bmatrix} - Z^{-1}\begin{bmatrix} c \\ c-\chi \end{bmatrix}\! K\right)(1 - \pi^Q(t,T)) + U G(t,T) U^{-1}\!\left(\begin{bmatrix} R_H K \\ R_L K \end{bmatrix} - Z^{-1}\begin{bmatrix} c \\ c-\chi \end{bmatrix}\! K\right), \tag{5}
$$

where $$Z$$ is the $$2\times 2$$ matrix of liquidity-adjusted discount factors, $$U$$ diagonalizes $$Z$$, $$\{R_H, R_L\}$$ are type-dependent recovery rates, and $$\pi^Q(t,T)$$ and $$G(t,T)$$ are the same risk-neutral default objects as in the BC model. Specifically:

$$
Z = \begin{bmatrix} r + \xi & -\xi \\ -\lambda\beta & r + \lambda\beta \end{bmatrix} = U \cdot \begin{bmatrix} \widetilde{r}_1 & 0 \\ 0 & \widetilde{r}_2 \end{bmatrix} \cdot U^{-1}, \tag{6}
$$

where $$\xi$$ is the liquidity shock intensity, $$\lambda$$ is the investor-to-dealer meeting intensity, and $$\beta$$ is the bargaining power of investors vis-a-vis dealers. The bid price is $$D_B^{HM}(t,T) = \beta D_H(t,T) + (1-\beta) D_L(t,T)$$ (equation (10), p. 139). The model shares the same $$\mathbb{P}$$-measure default probabilities as BC, so the HM model-implied yield spread decomposes into a BC-implied credit component and a liquidity component from search frictions.

**Identification.** The paper is a descriptive empirical study: no causal claim is made. The BC/CDG models are calibrated to historical default and equity data (no estimation of pricing errors from causal variation). The HM search parameters $$\theta^S = \{\xi, \lambda, \beta, \chi_k, \chi_c\}$$ are estimated country-by-country by minimizing the sum of squared fitting errors to observed BGN proportional bid-ask spreads (equation (14), p. 141), keeping firm-level BC fundamentals fixed. The BC and HM models share the same $$\mathbb{P}$$-measure default probability, so their yield differential isolates the incremental contribution of search frictions.

## Method

The paper evaluates three nested structural models:

1. **BC model** (pure default risk): firm-level parameters $$K/A_t$$, $$\sigma^A$$, $$\delta$$ estimated at the bond-level from Compustat/equity data; country-level Sharpe ratio SR estimated as median across Compustat firms; default boundary $$d$$ estimated via three methods (FS, BGY, HNS) matching physical default probabilities to historical data.

2. **CDG model** (stationary leverage): augments BC with GMM estimation of $$\kappa$$, $$\nu$$, $$\bar{L}^Q$$ using single-name CDS spreads at 1, 2, 3, 5, 7, and 10 years by country and rating (Table VII, p. 137).

3. **HM model** (endogenous illiquidity): fixes BC firm fundamentals and estimates the five search-friction parameters $$\theta^S$$ at the country level by least squares on proportional BGN bid-ask spreads (equation (14), p. 141):

$$
\widehat{\theta}^S = \arg\min_{\theta^S} \sum_t \sum_i \left(\phi(t, T_i; \theta^S) - \phi_{i,T_i}^{obs}\right)^2, \tag{14}
$$

where the model-implied proportional bid-ask spread is $$\phi(t,T;\theta^S) = \frac{D_A^{HM}(t,T) - D_B^{HM}(t,T)}{(D_A^{HM}(t,T) + D_B^{HM}(t,T))/2}$$ (equation (13), p. 141).

Asset volatility $$\sigma^A$$ is estimated following Schaefer and Strebulaev (2008) (equation (3), p. 113):

$$
\sigma^A_{i,t} = \sqrt{(1 - L_{i,t})^2 (\sigma^E_{i,t})^2 + L_{i,t}^2 (\sigma^D_{i,t})^2 + 2(1-L_{i,t}) L_{i,t} \sigma^E_{i,t} \sigma^D_{i,t} \rho^{ED}_{i,t}}, \tag{3}
$$

where $$L_{i,t}$$ is quasi-market leverage, $$\sigma^E_{i,t}$$ is annualized equity volatility from daily stock returns, $$\sigma^D_{i,t}$$ is debt volatility, and $$\rho^{ED}_{i,t}$$ is the stock-bond return correlation.

## Empirical specifications

**Mean pricing error (MPE) test (R1-R4, R7).** The headline test computes the mean pricing error for each credit rating/country/$$d$$-estimate bin:

$$
\text{MPE} = \overline{s^M(t,T)} - \overline{s^{obs}(t,T)},
$$

where $$s^M$$ is model-implied spread and $$s^{obs}$$ is observed spread (over swap rates or government bond yields). The MPE is computed for 72 IG/country/$$d$$ bins (24 country-rating bins times three $$d$$ estimates) and 24 IGctry/$$d$$ bins (country-level aggregates). Standard errors are clustered by bond issue; significance reported at 1%, 5%, 10% two-tailed. The test is run on: (i) the full sample including negative credit spreads; (ii) excluding observations with negative spreads over swap rates; (iii) industrial issuers only. Main results in Tables IV (bond-level, pp. 122-124) and V (country-level, pp. 126-127). Summary in Table IX (pp. 151-153).

**Bond-level panel regression (R5, R8).** To assess the cross-sectional fit of individual IG bond spreads, the paper runs panel regressions of monthly observed spreads on model-implied counterparts for each country, recovering the slope coefficient and $$R^2$$:

$$
s^{obs}_{i,t} = a + b \cdot s^M_{i,t} + \varepsilon_{i,t},
$$

with standard errors clustered by bond issue (Table IX Panels A2 and B2, p. 152-153). The slope under BC($$d^{FS}_{swap}$$) ranges from 0.28 (FRA) to 0.87 (AUS), with $$R^2$$ from 0.19 to 0.35. Under HM, the slope is closer to one in every country except AUS, and $$R^2$$ rises to 0.34-0.79.

**Time-series correlation test (R6).** The time-series correlation $$\rho^{IG}$$ between monthly mean observed and predicted IG spreads is computed for each country-model pair. Under BC($$d^{FS}_{swap}$$), $$\rho^{IG}$$ ranges from 0.55 (FRA) to 0.90 (GBR). Under HM($$d^{FS}_{swap}$$), $$\rho^{IG}$$ ranges from 0.65 (FRA) to 0.94 (GBR) (Table IX Panel A3, p. 152).

**Search-friction parameter validation.** The estimated HM search parameters $$\widehat{\theta}^S$$ are validated against independent empirical proxies (Figure 6, pp. 144-145): $$\widehat{\xi}$$ (liquidity shock intensity) correlates positively with the mutual fund share of corporate bond ownership; $$\widehat{\chi}_k + \bar{c}\widehat{\chi}_c$$ (holding cost) correlates with forced-selling costs at rating downgrades and index exclusions; $$\widehat{\lambda}$$ (dealer-meeting intensity) correlates with the scaled number of dealers quoting each bond from the Markit Bond Pricing Database; $$\widehat{\beta}$$ (bargaining power) is negatively correlated with downgrade frequency.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| ICE BofAML Global Corporate Index and High Yield Index (via Mercury/Bank of America ML) | Monthly bond prices, credit ratings, maturity for IG and HY bonds in 8 countries | No page yet |
| Compustat Global / Compustat NA | Firm balance sheet data (book debt, market equity, book-to-market); merged by issuer name to bond data | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| CRSP (U.S.) | Stock prices and returns for U.S. firms | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Bloomberg (BGN bid-ask prices, bond characteristics, shareholder data) | Identification of callability, seniority, security; screening of state-owned firms; proportional bid-ask spreads for HM estimation | [Bloomberg](/wiki/licensed/bloomberg/) (licensed) |
| Markit Bond Pricing Database | Daily trader quotes for individual bonds; number of dealers quoting each bond | [Markit bond pricing](/wiki/licensed/markit/) (licensed) |
| Markit single-name CDS spreads | Five-year CDS spreads for CDG GMM estimation; CDS-implied LGD proxies | [Markit CDS](/wiki/licensed/markit-cds/) (licensed) |
| Moody's Default and Recovery Database (DRD) | Historical issuer-weighted default and recovery rates by rating category and region (1970-2017) | No page yet |
| IHS Markit Bond Pricing Database | Number of distinct quotes and contributing dealers (for lambda proxy) | [Markit bond pricing](/wiki/licensed/markit/) (licensed) |
| Global Financial Data (stock market indexes by country) | TOPIX (JPN), FTSE100 (GBR), DAX (DEU), CAC40 (FRA), FTSE MIB (ITA), TSX Composite (CAN), S&P/ASX200 (AUS) for SR estimation | No page yet |
| OECD macroeconomic data | Macroeconomic covariates for pricing error regressions | [data:fred](/wiki/datasets/fred/) (partial; OECD is a separate source) |
| FRED (Federal Reserve Economic Data) | Additional macroeconomic variables | [FRED](/wiki/datasets/fred/) |
| Lehman Brothers Fixed Income Database + ML U.S. Corporate Bond Database | U.S. corporate bond prices 1987-2015 for U.S. subsample | No page yet |
| Barclays Live (swap rates) | IRS LIBOR swap rates for default-free benchmark construction | No page yet |

Sample: January 1997 to December 2017 for non-U.S. countries (except Italy from 2003 and Australia from 2007); 1987-2015 for U.S. bonds. Monthly frequency.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13409) if you are: replicating the global CSP evidence across multiple countries and rating categories (Tables IV, V for country-by-country MPEs); implementing the HM bond pricing model outside the U.S. (Section IV and Tables VIII, IX for parameter estimates and model validation); building structural credit models for non-U.S. markets; decomposing corporate bond yield spreads into default and liquidity components across eight economies; or examining cross-sectional determinants of IG bond spreads using panel regressions by country.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY-NC-ND 4.0 licence permits sharing with attribution for non-commercial purposes; no derivatives; the verbatim PDF is not hosted in this batch.

> **Citation.** Huang, Jing-Zhi, Yoshio Nozawa, and Zhan Shi.
> "The Global Credit Spread Puzzle."
> *The Journal of Finance* 80, no. 1 (February 2025): 101-162.
> DOI: 10.1111/jofi.13409. © 2024 The Author(s).
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page is a distillation by the Institute for Automated Research: core results extracted and re-expressed; extract-only, not reproduced.
