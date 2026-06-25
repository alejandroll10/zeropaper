---
title: "Intermediary Leverage Shocks and Funding Conditions: Fontaine, Garcia & Gungor (2025)"
description: >-
  Distilled: Broker-dealer aggregate leverage responds to both demand and supply
  disturbances with opposite effects on expected returns and funding conditions.
  Disentangling the two shocks resolves sign puzzles on raw leverage risk across
  equity, bond, and option markets and confirms intermediary constraints as a
  priced source of risk. J. Finance 2025, paywalled. Seven core results with
  source locators, datasets used, the econometric model, and the structural VAR
  identification procedure.
sidebar:
  label: Fontaine-Garcia-Gungor 2025
  order: 1
tags: [paper-summary, asset-pricing, intermediary-asset-pricing, factor-models,
       market-microstructure, liquidity, peer-reviewed, unreplicated,
       data:wrds, data:fred]
paper:
  authors: "Jean-Sebastien Fontaine, Rene Garcia, Sermin Gungor"
  authorList:
    - { family: Fontaine, given: "Jean-Sebastien", orcid: "0000-0001-9346-4645", affiliation: Bank of Canada }
    - { family: Garcia, given: "Rene", orcid: "0000-0003-2780-2671", affiliation: "Universite de Montreal and Toulouse School of Economics" }
    - { family: Gungor, given: Sermin, orcid: "0000-0003-4941-9120", affiliation: Bank of Canada }
  year: 2025
  venue: "The Journal of Finance 80(1), February 2025, pp. 57-99"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13407
  jel:
    codes: [G12, G14, G23]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Markets and Investment Strategies
    - Corporate Finance and Governance
    - Banking stability, regulation, efficiency
  dataAccess: licensed-commercial
  outcome:
    - cross-sectional expected excess returns on equities, bonds, and options
    - price of leverage demand and supply risk
    - stock market liquidity (Amihud illiquidity)
  outcomeClass:
    - security-returns
    - asset-prices
  license: >-
    Paywalled (Wiley VOR; license block content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0,
    start=2024-12-23; no CC licence detected in Crossref metadata)
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/JF, checked 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 7

  methods:
    role: both
    contributes: leverage-demand-supply-decomposition
    family: structural
    buildsFrom: [panel-regression, fama-macbeth, sign-restricted-svar, instrumental-variables]
    identification: instrument

  contributionType: [new-method, new-fact, measurement]

  mechanisms:
    - intermediary-constraint
    - liquidity
    - demand-elasticity

  scope:
    region: US
    assetClass: "US equities, Treasury bonds, corporate bonds, S&P 500 index options"
    period: 1986-01..2021-12
    frequency: quarterly
    dataType: [market, accounting]
    granularity: [aggregate, security]
    n: "~125 test assets across equities, bonds, and options; quarterly data 1986Q2-2021Q4"

  findings:
    - ref: R1
      outcome: price of leverage demand and supply risk
      metric: coefficient
      value: "lambda = 2.12 (95% CI [1.38, 3.55]); R-squared = 0.921 (CI [0.78, 0.98])"
      direction: positive
      vsBenchmark: R-squared rises from 84% (raw leverage + market) to 92% with demand/supply decomposition
    - ref: R2
      outcome: cross-sectional expected excess returns on equities, bonds, and options
      metric: return-spread
      value: "lambda_s = 4.05 (t=2.56) for supply shocks; lambda_d = -4.47 (t=-2.38) for demand shocks (Table I cols 2-3)"
      direction: positive
      vsBenchmark: supply-shock price positive and demand-shock price negative, as predicted; raw leverage price ambiguous in sign
    - ref: R3
      outcome: cross-sectional expected excess returns on equities, bonds, and options
      metric: r-squared
      value: "R-squared = 90.5% for supply-only; 88.6% for demand-only; 93.1% combined with symmetry (Table I)"
      direction: positive
      vsBenchmark: vs. 7.9% R-squared for raw leverage alone (Table I col 1)
    - ref: R4
      outcome: cross-sectional expected excess returns on equities, bonds, and options
      metric: coefficient
      value: "lambda = 2.04 (t=2.85) for equities; 2.04 (t=3.72) for bonds; 2.22 (t=2.55) for options (Table II)"
      direction: positive
      vsBenchmark: consistent sign and magnitude across three asset classes; raw leverage price negative and insignificant for options
    - ref: R5
      outcome: price of leverage demand and supply risk
      metric: coefficient
      value: "lambda = 1.86 (t=2.20, Table VI col 4) using AEM test assets; supply shock price 3.25 (t=2.11), demand shock price -4.54 (t=-1.68)"
      direction: positive
      vsBenchmark: confirms AEM's positive leverage price; supply betas have larger dispersion in AEM sample
    - ref: R6
      outcome: stock market liquidity (Amihud illiquidity)
      metric: coefficient
      value: "Supply shocks: illiquidity coefficients negative, significant, monotone from -42.8 (t=-1.79) for least-liquid to -0.001 (t=-2.40) for most-liquid portfolio (Table V Panel A)"
      direction: negative
      vsBenchmark: demand shocks yield insignificant illiquidity coefficients; raw leverage negative but never significant at 5%
    - ref: R7
      outcome: price of leverage demand and supply risk
      metric: r-squared
      value: "Uncentered R-squared = 48% for model-implied vs OLS price of raw leverage across asset classes (Figure 8)"
      direction: positive
      vsBenchmark: predicted sign of raw leverage price correct in every asset class

  resultType: new-finding

  relatesTo:
    - { cite: "Adrian, Etula & Muir (2014)", doi: '10.1111/jofi.12189', relation: extends, note: "decomposes AEM's raw leverage factor into demand and supply shocks; explains why AEM's price-of-risk sign and magnitude vary across studies" }
    - { cite: "Brunnermeier & Pedersen (2009)", doi: '10.1093/rfs/hhn098', relation: tests, note: "verifies their prediction that leverage supply shocks drive market liquidity, while demand shocks do not" }
    - { cite: "He, Kelly & Manela (2017)", doi: '10.1016/j.jfineco.2017.08.002', relation: extends, note: "explains sign reversals in their cross-asset price-of-leverage-risk estimates as mixtures of demand and supply betas" }
    - { cite: "Goldberg (2020)", doi: '10.1111/jofi.12991', relation: builds-on, note: "closely related identification of inventory demand and supply shocks in Treasury markets" }
    - { cite: "Goldberg & Nozawa (2021)", relation: builds-on, note: "related identification for corporate bond markets; supply shocks more persistent, consistent with this paper" }
    - { cite: "Fontaine & Garcia (2012)", relation: builds-on, note: "FG funding-conditions measure constructed here as one of three components of the FUND instrument" }
    - { cite: "Du, Hebert & Huber (2022)", doi: '10.1093/rfs/hhac050', relation: cites, note: "show leverage constraints do not always bind; consistent with demand shocks operating away from constraint" }

  openQuestions:
    - "What deeper structural models explain why leverage demand shocks have weak correlations with market liquidity and why the nonlinearity or asymmetry may be significant, especially around the 2008-2009 and 2020 crises (p. 94)."
    - "How to quantify the relative importance of demand- and supply-side mechanisms across asset classes and what the underlying economic mechanisms are for each type of shock (p. 96)."
    - "Whether additional data and deeper economic modeling can determine the degree of asymmetry in prices of risk (i.e., whether symmetry holds), which the current sample is largely uninformative about (p. 84)."

  replicationCode:
    status: none

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 57-99); seven results extracted from Tables I-VI and Figures 4-8. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; one error fixed: R5 symmetric lambda corrected from 1.90 to 1.86 (Table VI col 4) in the Core results table, findings value, and Empirical specifications section; all equations (1)-(22) verified term-by-term; all other locators and magnitudes confirmed."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13407", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[0].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-23; no Creative Commons licence detected" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the econometric model of leverage demand and supply shocks, and the structural VAR identification strategy with its defining equations: enough to know what it found and how, without reading 43 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13407).

## TL;DR

Broker-dealer aggregate leverage responds to both demand shocks (customers seeking immediacy) and supply shocks (financiers relaxing funding constraints). These two shocks both raise leverage but shift the intermediaries' marginal value of wealth in opposite directions: supply shocks improve funding conditions and carry a positive price of risk; demand shocks tighten funding conditions and carry a negative price of risk. A parsimonious two-shock structural model with a funding-conditions instrument achieves a cross-sectional R-squared of 92% over equities, bonds, and options, versus 8% for raw leverage alone. Disentangling the shocks also resolves why raw leverage carries positive price-of-risk estimates in bond markets but negative (or insignificant) ones in option markets, and why leverage is largely uncorrelated with stock market liquidity in the data.

## Core results

Magnitudes and significance are as reported; `\*` = 5%, `\*\*` = 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Price of symmetric leverage demand/supply risk is significant with 92% cross-sectional fit | Figure 4, p. 77; text p. 76 | lambda = 2.12 (95% CI [1.38, 3.55]); R-squared = 92.1% (CI [78%, 98%]) |
| R2 | Supply shock price is positive and demand shock price is negative, as predicted, across all test assets | Table I cols (2)-(3), p. 80 | lambda_s = 4.05 (t=2.56); lambda_d = -4.47 (t=-2.38); raw leverage alone (col 1) lambda_l = 4.56 (t=2.45) but R-squared only 7.9% |
| R3 | Decomposing leverage raises cross-sectional R-squared from 8% to 90%-93% | Table I, p. 80 | R-squared: col (1) raw = 7.9%; col (2) supply only = 90.5%; col (3) demand only = 88.6%; col (4) symmetric = 93.1% |
| R4 | Price-of-risk magnitude is consistent across equities, bonds, and options when demand/supply shocks are used | Table II, p. 85 | Equities: lambda = 2.04 (t=2.85); Bonds: 2.04 (t=3.72); Options: 2.22 (t=2.55); raw leverage price negative and insignificant for options |
| R5 | Model confirms AEM's result using AEM's own test assets, reconciling the weaker but positive raw leverage price they find | Table VI, p. 95 | lambda = 1.86 (t=2.20) symmetric; supply price 3.25 (t=2.11); demand price -4.54 (t=-1.68); R-squared = 82% |
| R6 | Leverage supply shocks have a significant negative effect on stock illiquidity (improve liquidity), while demand shocks do not | Table V Panel A, pp. 93-94 | Supply coefficients: -42.8 (t=-1.79) to -0.001 (t=-2.40) monotonically across illiquidity deciles; demand shocks insignificant in every portfolio |
| R7 | Model explains why raw leverage price of risk switches sign across asset classes: supply betas dominate in bonds, demand betas dominate in options | Figure 8, p. 91; Table IV Panel B, p. 90 | Uncentered R-squared = 48% for model vs. OLS estimates of raw leverage price; sign correct in every asset class |

**Overall (paper's conclusion).** Disentangling demand and supply disturbances to broker-dealer leverage substantially strengthens evidence for a central role of intermediaries in asset pricing. Both shocks carry consistent and significant prices of risk across equities, bonds, and options, with opposite signs. The mixing of these two shocks in raw leverage explains previously puzzling sign reversals (e.g., in Adrian, Etula, and Muir (2014) and He, Kelly, and Manela (2017)) and the weak correlation between leverage and market liquidity documented by Brunnermeier and Pedersen (2009). Future work is needed to identify the deeper structural mechanisms driving each type of shock and to explain their varying importance across markets.

## Theory / model

The econometric model (Section I, p. 62) represents broker-dealer log leverage $$\text{LEV}$$ as the sum of two independent disturbances (eq. 1, p. 63):

$$
\text{LEV} = \mu_l + b_d e^d + b_s e^s, \tag{1}
$$

where $$b_d, b_s > 0$$ are positive loadings, $$e^d$$ is the leverage demand shock (customers demanding immediacy), and $$e^s$$ is the leverage supply shock (financiers relaxing funding constraints). Both shocks have zero mean and unit variance.

Intermediaries' marginal value of wealth $$\phi$$ is driven by the same shocks in opposite directions (eq. 2, p. 63):

$$
\phi = \gamma + \alpha_d e^d - \alpha_s e^s, \tag{2}
$$

with $$\alpha_d, \alpha_s, \gamma > 0$$. The demand shock $$e^d$$ raises both leverage and marginal value of wealth (tighter funding); the supply shock $$e^s$$ raises leverage but reduces marginal value of wealth (easier funding). Asset $$i$$ earns excess return $$xR_i$$ given by (eq. 3, p. 63):

$$
xR_i = \mu_i + \beta_{i,d} e^d + \beta_{i,s} e^s + e^i, \tag{3}
$$

where $$e^i$$ is an idiosyncratic shock. Intermediaries price assets such that their marginal value of wealth spans the pricing kernel (eq. 4, p. 64):

$$
\mathbb{E}[xR_i] = -\frac{\text{Cov}[\phi, xR_i]}{\mathbb{E}[\phi]}. \tag{4}
$$

Equations (1)-(4) jointly pin down expected returns (eq. 5, p. 64):

$$
\mu_i = \beta_{i,d} \lambda_d + \beta_{i,s} \lambda_s = \beta_i^\top \lambda, \tag{5}
$$

with prices of risk $$\lambda_d = -\alpha_d \gamma^{-1} < 0$$ and $$\lambda_s = \alpha_s \gamma^{-1} > 0$$.

**Implication 1** (p. 64): Risky assets have $$\beta_{i,d} < 0$$ and $$\beta_{i,s} > 0$$, and the corresponding prices of risk $$\lambda_d < 0$$ and $$\lambda_s > 0$$.

The raw leverage factor $$L = \text{LEV} - \mathbb{E}[\text{LEV}] = b_d e^d + b_s e^s$$ is a mix, so the raw leverage beta is (eq. 6, p. 64):

$$
\beta_{i,l} \equiv \frac{\text{Cov}(L, xR_i)}{\text{Var}(L)} = (\sigma_l^2)^{-1}(b_d \beta_{i,d} + b_s \beta_{i,s}), \tag{6}
$$

which can take either sign because it mixes demand and supply betas. The price of raw leverage risk in a cross-section depends on the dispersion and covariance of demand and supply betas (eq. 7, p. 64):

$$
\lambda_l = c(b_s \omega_s^2 \lambda_s + b_d \omega_d^2 \lambda_d + \omega_{ds}(b_s \lambda_d + b_d \lambda_s)), \tag{7}
$$

where $$c = \sigma_l^2 (b^\top \Omega b)^{-1} > 0$$. **Implication 2** (p. 65): the sign of $$\lambda_l$$ depends on the dispersion of demand and supply betas and their correlation, which can differ across asset classes.

To verify the prediction for market liquidity, illiquidity $$\Lambda_i$$ is modeled as proportional to intermediaries' marginal value of wealth (eq. 20, p. 92):

$$
\Lambda_i = \delta_i (\phi - \gamma), \tag{20}
$$

leading to **Implication 3**: supply shocks have negative population coefficients in illiquidity regressions, demand shocks have positive coefficients, and the sign of the raw leverage coefficient is determined by $$(b_d - b_s) \alpha \delta_i$$ (eqs. 21-22, p. 92).

## Method

**Identification.** The identification strategy (Section II.A, pp. 65-67) uses a funding-conditions instrument $$Z$$ that is correlated with both types of shocks:

$$
Z = \mu_Z + a_d e^d - a_s e^s, \tag{8}
$$

$$
u = \begin{bmatrix} u^z \\ u^l \end{bmatrix} = \begin{bmatrix} Z - \mu^z \\ \text{LEV} - \mu^l \end{bmatrix} = \begin{bmatrix} a_d & -a_s \\ b_d & b_s \end{bmatrix} \begin{bmatrix} e^d \\ e^s \end{bmatrix} = Ae. \tag{9}
$$

The variance of observed innovations is $$\text{Var}(u) = AA^\top$$ (eq. 10, p. 66), which provides three restrictions but leaves four parameters $$(a_d, a_s, b_d, b_s)$$ underdetermined. The paper achieves point identification by imposing the economic symmetry restriction $$\lambda_s = -\lambda_d = \lambda > 0$$ (equivalently $$\kappa = 1$$ in $$\lambda_s = -\kappa\lambda_d$$), which links the ratio of reduced-form price-of-risk coefficients to structural parameters (eq. 13, p. 66):

$$
\frac{c_l}{c_z} = \frac{a_s - a_d \kappa}{b_s + b_d \kappa}. \tag{13}
$$

**Identification 1** (p. 67) states: given independent shocks, positive parameters, and symmetric prices of risk, the structural parameters are identified in closed form:

$$
a_d = \frac{\sigma_z^2 \varphi_a}{2a_s}, \quad a_s = \sigma_z \sqrt{\frac{1 \pm \sqrt{1 - \varphi_a^2}}{2}},
\quad b_d = \frac{\sigma_l^2 \varphi_b}{2b_s}, \quad b_s = \sigma_l \sqrt{\frac{1 \pm \sqrt{1 - \varphi_b^2}}{2}}, \tag{14}
$$

where $$\varphi_a, \varphi_b \leq 1$$ depend on $$\text{Var}(u)$$ and $$C$$ (eq. 14, p. 67).

**Estimation procedure** (Section II.C, pp. 69-70). A VAR(1) model is specified for $$y_t = [\text{LEV}_t, Z_t]^\top$$:

$$
y_{t+1} = a + \Phi y_t + u_{t+1}, \tag{17}
$$

estimated by OLS to recover forecast errors $$\hat{u}_{t+1}$$ and their covariance $$\hat{\Sigma}_u$$. The reduced-form coefficient $$\hat{C}$$ is recovered from a cross-sectional OLS regression of average returns $$\mathbb{E}_T[xR_i]$$ on covariances $$\mathbb{E}_T[xR_i u]$$. The matrix $$\hat{A}$$ follows from eq. (14), structural shocks from $$\hat{e}_t = \hat{A}^{-1}\hat{u}_t$$, and the price of risk from $$\hat{\lambda} = \hat{A}^\top \hat{C}$$. Standard errors are from a block bootstrap to account for serial correlation and heteroskedasticity.

**Instrument construction** (Section II.D, p. 70). The funding-conditions proxy $$\mathit{FUND}$$ is the first principal component of three Treasury-market measures: the TED spread ($$\mathit{TED}$$), the Hu, Pan, and Wang (2013) noise measure ($$\mathit{HPW}$$), and the Fontaine and Garcia (2012) term-structure factor ($$\mathit{FG}$$), monthly data January 1986 to December 2021. The approach builds on Goldberg (2020) and Goldberg and Nozawa (2021), who identify demand and supply shocks in Treasury and corporate bond inventory, and is also consistent with Du, Hebert, and Huber (2022), who show leverage constraints do not always bind. A higher $$\mathit{FUND}$$ value signals tighter funding conditions / higher marginal value of intermediary wealth, so it co-moves positively with demand shocks and negatively with supply shocks, as required.

The estimated $$\hat{A}$$ matrix with 95% bootstrap confidence intervals is (eq. 19, p. 74):

$$
\hat{A} = \begin{bmatrix} 0.58 & -0.34 \\ (0.27, 0.77) & -(0.55, 0.02) \\ 5.16 & 3.87 \\ (2.03, 8.35) & (0.78, 7.46) \end{bmatrix}. \tag{19}
$$

## Empirical specifications

**Baseline asset pricing test (R1, R2, R3).** The two-stage Fama-MacBeth regression (Section III.B, pp. 79-81) is estimated on a balanced panel of ~125 test assets (equities, Treasury bonds, corporate bonds, S&P 500 options). First stage: estimate return betas for each asset by regressing excess returns on the identified shocks or on the raw leverage innovation. Second stage (cross-sectional, without a constant as recommended by Shanken 1996 and Kroencke-Thimme 2021): regress average returns on betas to recover the price-of-risk vector $$\hat{\lambda}$$. $$t$$-statistics use Shanken-corrected standard errors. The uncentered $$\bar{R}^2$$ confidence interval follows Lewellen, Nagel, and Shanken (2010).

For the symmetric model (column (4) of Table I), only the difference $$\beta_s - \beta_d$$ enters the second stage (imposing $$\lambda_s = -\lambda_d$$), yielding a parsimonious one-parameter price-of-risk estimate $$\hat{\lambda} = 2.02$$ (close to the structural model's $$\hat{\lambda} = 2.12$$).

**Asset-class regressions (R4).** The same specification run separately on equities (1986-2021, value-weighted), bonds (1986Q2-2021Q4, equally weighted), and options (1986Q2-2021Q4, equally weighted S&P 500 call and put portfolios from Constantinides, Jackwerth, and Savov 2013). Consistent sign and magnitude of $$\hat{\lambda}$$ across classes (Table II, p. 85).

**AEM replication (R5).** Table VI (p. 95) uses AEM's original test assets: 25 size- and book-to-market-sorted FF portfolios, 10 momentum portfolios, and 12 Treasury bonds. The raw leverage factor produces a positive $$\hat{\lambda}_l = 6.16$$ (t=2.64) in column (1), consistent with AEM; the symmetric demand/supply decomposition delivers $$\hat{\lambda} = 1.86$$ (t=2.20) in column (4) with a higher $$\bar{R}^2$$.

**Liquidity regressions (R6).** Panel time-series regressions (Section III.E, pp. 91-94) of quarterly changes in Amihud illiquidity ratios on the identified leverage supply and demand shocks plus contemporaneous market returns, with Newey-West $$t$$-statistics using three lags (Table V, p. 93):

$$
\Delta\text{Illiq}_{i,t} = a + b_i e_t^s + c_i x R_{m,t} + \varepsilon_t \quad \text{(Panel A)},
$$

$$
\Delta\text{Illiq}_{i,t} = a + b_i e_t^d + c_i x R_{m,t} + \varepsilon_t \quad \text{(Panel B)},
$$

$$
\Delta\text{Illiq}_{i,t} = a + b_i \Delta\text{LEV}_t + c_i x R_{m,t} + \varepsilon_t \quad \text{(Panel C)}.
$$

Estimated for 10 illiquidity-decile portfolios (Row I) and 10 volatility-decile portfolios (Row II). Supply-shock coefficients in Panel A are negative, monotone, and significant; demand-shock coefficients in Panel B are insignificant; raw leverage in Panel C is negative but never significant at 5%.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Federal Reserve Flow of Funds (Table L.129) | Quarterly broker-dealer aggregate leverage LEV (total financial assets / book equity), 1986Q2-2021Q4 | [FRED](/wiki/datasets/fred/) (public; Flow of Funds tables) |
| TED spread (EuroDollar LIBOR minus T-bill) | Component of FUND instrument; funding-conditions proxy | No page yet |
| Hu, Pan & Wang (2013) noise measure | Component of FUND instrument; bond yield noise as funding proxy | No page yet |
| Fontaine & Garcia (2012) liquidity factor | Component of FUND instrument; term-structure-based funding measure | No page yet |
| CRSP (via WRDS) | Stock returns and market data for equity test portfolios; Amihud illiquidity construction | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Compustat (via WRDS) | Book-to-market, size for FF25 equity portfolio sorts | [WRDS](/wiki/licensed/wrds/) (licensed) |
| CRSP bond files | Treasury bond returns for 12-bond test-asset panel (2- to 10-year maturities); security-level data | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Constantinides, Jackwerth & Savov (2013) option portfolios | S&P 500 unlevered call and put portfolios (27 each), 1986Q2-2021Q4 | No page yet |
| Corporate bond data | Corporate bond test portfolios sorted on illiquidity, volatility, and funding betas | No page yet |

Sample: January 1986 to December 2021 (monthly for FUND, quarterly for asset pricing tests).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13407) if you are: building intermediary asset pricing models and need the structural identification procedure and closed-form parameter expressions (Section I-II and Internet Appendix Section I); revisiting the sign puzzle in AEM or He, Kelly, and Manela (2017) (Section IV); studying the leverage-liquidity nexus and want the panel illiquidity regression results (Section III.E and Table V); or extending the framework to other asset classes or to a model where the leverage constraint does not always bind.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled (Wiley VOR); only extraction is permitted here.

> Fontaine, Jean-Sebastien, Rene Garcia, and Sermin Gungor.
> "Intermediary Leverage Shocks and Funding Conditions."
> *The Journal of Finance* 80, no. 1 (February 2025): 57-99.
> DOI: [10.1111/jofi.13407](https://doi.org/10.1111/jofi.13407).
> © 2024 the American Finance Association.
> Paywalled; extract-only redistribution.
