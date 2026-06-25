---
title: "Test Assets and Weak Factors: Giglio, Xiu & Zhang (2025)"
description: >-
  Distilled: Giglio, Xiu, and Zhang show that weak factors and test asset
  selection are deeply connected, and introduce Supervised Principal Component
  Analysis (SPCA), an iterative procedure that screens test assets by
  correlation with the target factor before applying PCA, enabling consistent
  risk premium estimation even when some latent factors are weak. J. Finance
  2025, paywalled. Eight core results with source locators, datasets used,
  the model (linear factor model with weak factors), and the method (SPCA
  algorithm) with its defining equations.
sidebar:
  label: Giglio-Xiu-Zhang 2025
  order: 1
tags: [paper-summary, asset-pricing, factors, factor-models, weak-factors,
       risk-premia, panel-regression, fama-macbeth, peer-reviewed, unreplicated,
       data:open-source-asset-pricing, data:ken-french]
paper:
  authors: Stefano Giglio, Dacheng Xiu, Dake Zhang
  authorList:
    - { family: Giglio, given: Stefano, orcid: "0000-0002-7703-2671", affiliation: Yale School of Management }
    - { family: Xiu, given: Dacheng, orcid: "0000-0002-2250-0861", affiliation: University of Chicago Booth School of Business }
    - { family: Zhang, given: Dake, orcid: "0000-0001-9508-8209", affiliation: Antai College of Economics and Management, Shanghai Jiao Tong University }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 259–319
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13415
  jel:
    codes: [G12, C38, C55]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Financial Markets and Investment Strategies", "Credit Risk and Financial Regulations", "Monetary Policy and Economic Impact"]
  dataAccess: public
  outcome:
    - risk premium estimates of tradable and nontradable factors
    - out-of-sample hedging R-squared of factor-mimicking portfolios
    - Sharpe ratio of SPCA-recovered SDF
  outcomeClass: [security-returns]
  license: >-
    Paywalled: Wiley/AFA standard terms (content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2024-12-18; no CC licence found in Crossref metadata).
    Copyright 2024 the American Finance Association.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/AFA site; Crossref DOI resolves but full text is behind subscription, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 36

  methods:
    role: both
    contributes: spca
    family: descriptive
    buildsFrom: [fama-macbeth, factor-analysis-pca, lasso]
    identification: descriptive
  contributionType: [new-method, new-theory, new-fact]
  scope:
    region: US
    assetClass: US equity portfolios
    period: 1976-03..2020-12
    frequency: monthly
    dataType: [market, accounting]
    granularity: [security, aggregate]
    n: "901 test portfolios (Chen-Zimmermann) + 49 industry portfolios, 1976m3-2020m12"
  findings:
    - ref: R1
      outcome: risk premium estimates of tradable and nontradable factors
      metric: basis-points
      value: "Market RP (SPCA, p=3-11): 68-74 bps/month, close to average excess return of 74/62 bps (train/eval); all four p values statistically indistinguishable from average excess return"
      direction: positive
      vsBenchmark: "consistent with model-free average excess return; PCA-based methods give similar estimates for strong factors like market"
    - ref: R2
      outcome: risk premium estimates of tradable and nontradable factors
      metric: basis-points
      value: "Momentum RP (SPCA, p=3): 112 bps/month; HML RP: 37-50 bps/month; Intermediary Capital RP varies across p=3-11 (e.g., ~100-116 bps for p=5-11)"
      direction: positive
      vsBenchmark: "SPCA estimates are never statistically different from model-free average excess return for tradable factors at 5% level (except QMJ at p=3)"
    - ref: R3
      outcome: risk premium estimates of tradable and nontradable factors
      metric: basis-points
      value: "Almost all nontradable factors (liquidity, IP growth, three uncertainty factors, term spread, credit spread, unemployment, sentiment, oil, consumption) show risk premia statistically indistinguishable from zero at most p values; intermediary capital factor is a notable exception with significantly positive RP (paper text: p.305-306)"
      direction: none
      vsBenchmark: "nontradable factors systematically harder to hedge with equity portfolios; positive out-of-sample R-squared is achieved for intermediary capital and some uncertainty factors"
    - ref: R4
      outcome: out-of-sample hedging R-squared of factor-mimicking portfolios
      metric: r-squared
      value: "Market factor: out-of-sample R-squared above 0.98 for all p and q combinations; CMA: above 50% for most p and q; Momentum: above 70% for p >= 3 with SPCA vs. >= 6 factors needed for PCA to reach same level"
      direction: positive
      vsBenchmark: "SPCA achieves comparable or higher out-of-sample R-squared than PCA with fewer factors, especially for factors with weak cross-sectional exposures"
    - ref: R5
      outcome: out-of-sample hedging R-squared of factor-mimicking portfolios
      metric: r-squared
      value: "Momentum hedging: SPCA out-of-sample R-squared falls from 86% to 77% when momentum-sorted test assets are removed; PCA R-squared falls from 76% to 48% (same experiment). Profitability: SPCA from 71% to 60%; PCA from 41% to 14%"
      direction: positive
      vsBenchmark: "SPCA degrades much less than PCA when the most informative test assets for a factor are removed from the cross section, confirming robustness to weak factors"
    - ref: R6
      outcome: risk premium estimates of tradable and nontradable factors
      metric: basis-points
      value: "SPCA bias for weak factor V in simulations: -6.6 bps (T=120), -3.4 bps (T=240), -3.1 bps (T=480); PCA bias for V: -37 bps (T=120), -35 bps (T=240), -14 bps (T=480); RMSE for SPCA: 20.9, 14.6, 10.3 bps"
      direction: none
      vsBenchmark: "SPCA has substantially smaller bias and RMSE than PCA, rpPCA, Lasso, Ridge, and two-pass estimators for the weak factor V in scenario (f) of Table I"
    - ref: R7
      outcome: Sharpe ratio of SPCA-recovered SDF
      metric: sharpe-ratio
      value: "SPCA SDF out-of-sample Sharpe ratio: 0.193 (T=120), 0.226 (T=240), 0.241 (T=480); theoretical value = 0.256; PCA: 0.084, 0.110, 0.227; rpPCA: 0.134, 0.192, 0.242"
      direction: positive
      vsBenchmark: "SPCA achieves out-of-sample Sharpe ratio closest to theoretical optimum (0.256) in all sample sizes; outperforms PCA, PLS, Lasso, Ridge (Table III)"
    - ref: R8
      outcome: Sharpe ratio of SPCA-recovered SDF
      metric: sharpe-ratio
      value: "CAPM diagnosed as missing multiple risk factors: SPCA Sharpe ratio grows from ~0.5 to ~1.4+ as p increases from 1 to 20 factors (CZ data), far above the dashed CAPM Sharpe of 0.46. FF3, FF5 also diagnosed as missing factors. FF5+Momentum+BAB+QMJ (Panel E) best approximates the SPCA Sharpe frontier but misspecification remains visible in CZ data"
      direction: positive
      vsBenchmark: "SPCA Sharpe ratio exceeds observable factor model Sharpe ratios for all five models examined (CAPM, FF3, FF5, FF5+Mom, FF5+Mom+BAB+QMJ), indicating missing factors"
  resultType: new-finding
  relatesTo:
    - { cite: "Giglio and Xiu (2021)", doi: '10.1086/714090', relation: extends, note: "SPCA extends the PCA-based risk premium estimator of Giglio and Xiu (2021) by adding a supervised screening step that selects informative test assets; the benchmark estimator (Algorithm 1) is from that paper" }
    - { cite: "Kan and Zhang (1999)", doi: '10.1111/0022-1082.00102', relation: builds-on, note: "Kan and Zhang (1999) establish that inference from Fama-MacBeth regressions with useless factors breaks down; Giglio, Xiu, and Zhang show the same problem arises in latent factor models" }
    - { cite: "Kozak, Nagel, and Santosh (2020)", doi: '10.1016/j.jfineco.2019.06.008', relation: tests, note: "Kozak, Nagel, and Santosh (2020) propose Lasso/Ridge SDF shrinkage; the paper proves these are consistent for SDF recovery but less efficient than SPCA, and inconsistent for risk premia under weak factors" }
    - { cite: "Lettau and Pelger (2020)", doi: '10.1016/j.jeconom.2019.08.012', relation: contradicts, note: "Lettau and Pelger (2020) propose rpPCA for weak factors; the paper shows rpPCA is inconsistent for risk premia in the weak-factor setting the paper studies" }
    - { cite: "Fama and French (1993)", doi: '10.1016/0304-405x(93)90023-5', relation: tests, note: "FF3 and FF5 models are evaluated as candidate observable factor models using SPCA diagnosis; both are found to miss important pricing factors" }
    - { cite: "Chen and Zimmermann (2022)", doi: '10.1561/104.00000112', relation: cites, note: "Chen and Zimmermann (2022) provide the main test asset cross section (901 characteristic-sorted portfolios plus 49 industry portfolios) used in the empirical analysis" }
    - { cite: "Hou, Xue, and Zhang (2020)", relation: cites, note: "Hou, Xue, and Zhang (2020) provide the alternative 1,672-portfolio test asset cross section used for robustness" }
    - { cite: "Bai and Ng (2002)", doi: '10.1111/1468-0262.00392', relation: builds-on, note: "Bai and Ng (2002) establish the standard large-N, large-T approximate factor model that SPCA extends to the weak-factor setting" }
  openQuestions:
    - "Whether SPCA can be extended to scenarios where exposures to a factor are uniformly small across all test assets, in which case no subset I_0 of informative assets exists and the paper acknowledges no estimator can recover the factor (p. 272)."
    - "A comprehensive study of optimal frequency: the paper studies monthly data following the literature and leaves analysis at other frequencies to future work (p. 297, footnote 42)."
    - "How SPCA performs with time-varying betas, which the paper sets aside by using portfolio test assets with approximately constant factor exposures (p. 267)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 259-319); eight results extracted from Tables I-IV and Figures 1-9. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against source PDF; equations 1-11 verified term-by-term (correct); Table I R6 values confirmed; Table III R7 values confirmed; Figure 8 R5 values confirmed; Figure 9 R8 values confirmed; R2 magnitude row corrected (HML range 37-50 bps from Table IV; Momentum p=11 range end clarified; unverifiable Intermed Cap 93-128 claim downgraded to table-supported range); mechanisms field removed (paper invokes no standard economic mechanism channel); all cites locatable in body." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13415", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-18; no Creative Commons licence present; paywalled AFA/Wiley standard terms only" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it builds on (the linear factor model with weak factors), and the method it contributes (SPCA) with the defining equations: enough to know what it found and how, without reading all 61 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13415).

## TL;DR

Giglio, Xiu, and Zhang show that weak factors and test asset selection are two faces of the same problem: a factor is weak precisely in the cross section of test assets chosen by the researcher. They propose Supervised Principal Component Analysis (SPCA), a procedure that screens test assets by their correlation with the factor of interest $$g_t$$ at each iteration before extracting a principal component. This ensures that only assets with nontrivial exposure to the relevant factor are used, effectively strengthening the factor within the selected subset and enabling consistent risk premium estimation even when some latent SDF factors are weak or when some priced factors are omitted. Applied to a large cross section of 901 to 1,672 characteristic-sorted equity portfolios (1976 to 2020), SPCA estimates risk premia close to model-free averages for tradable factors, achieves substantially higher out-of-sample hedging $$R^2$$ than PCA for factors with weak exposures, and diagnoses that standard observable factor models (CAPM, FF3, FF5) miss important latent pricing factors.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **SPCA gives risk premia consistent with model-free averages for the market factor**, a strong factor, across all tuning parameters | Table IV, p. 300; Figure 5, Panel A, p. 302 | Market RP estimates 68-74 bps/month for p = 3, 5, 7, 11; average excess return 74/62 bps (train/eval); never statistically different at 5% |
| R2 | **SPCA risk premia are consistent with model-free averages for all tradable factors** (with minor exceptions); the intermediary capital factor has a significant positive RP even among nontradables | Table IV, pp. 300-301; Figure 5, pp. 302; Figure 6, p. 303 | Momentum RP ~112 bps (p=3) varying across p=3-11; HML RP 37-50 bps; liquidity factor RP 70-95 bps out-of-sample (p.305) |
| R3 | **Almost all nontradable macro factors (IP growth, uncertainty, consumption, term spread, credit, oil) have risk premia indistinguishable from zero**; equity markets cannot span their variation | Table IV, pp. 300-301; Figure 6, p. 303 | Positive out-of-sample $$R^2$$ is rare for macro nontradables; LN1/LN2 macro factors: $$R^2$$ near zero or negative; Liquidity: $$R^2$$ 0-4% |
| R4 | **SPCA out-of-sample hedging $$R^2$$ is higher or equal to PCA's, often with fewer factors** | Figure 5, pp. 302; Figure 6, p. 303 | Market: $$R^2 > 0.98$$ for all p, q; Momentum: SPCA reaches $$R^2 > 70\%$$ with p=3; PCA needs p >= 6; Intermediary Cap: SPCA $$R^2 \approx 50\%$$, PCA much lower |
| R5 | **SPCA degrades little when informative test assets are removed**; PCA degrades sharply | Figure 8, p. 311 | Momentum: SPCA $$R^2$$ from 86% to 77% without momentum assets; PCA from 76% to 48%. Profitability: SPCA 71% to 60%; PCA 41% to 14% |
| R6 | **In simulations, SPCA has far smaller bias than PCA, rpPCA, Ridge, Lasso, and two-pass estimators** for weak factors | Table I, p. 293 | Weak factor V bias: SPCA -3.4 bps vs PCA -35 bps at T=240; RMSE 14.6 vs 36.5 bps; PLS ranks second among alternatives |
| R7 | **SPCA achieves out-of-sample Sharpe ratios closest to the theoretical optimum** (0.256) among all estimators in SDF recovery simulations | Table III, p. 295 | SPCA SR: 0.193 (T=120), 0.226 (T=240), 0.241 (T=480); PCA: 0.084, 0.110, 0.227; rpPCA: 0.134, 0.192, 0.242 |
| R8 | **SPCA diagnoses that CAPM, FF3, and FF5 all miss important pricing factors**: SPCA Sharpe ratio grows well above each model's own Sharpe ratio as additional latent factors are extracted | Figure 9, p. 315 | Market (CAPM) Sharpe = 0.46; SPCA SR grows from ~0.5 to ~1.4+ with 1-20 factors (CZ data); FF5+MOM+BAB+QMJ best but still misspecified in CZ data |

**Overall (paper's conclusion).** SPCA resolves the weak factor problem in empirical asset pricing by treating factor weakness as a property of the test assets rather than the factor itself. It consistently estimates risk premia and recovers the SDF in the presence of weak, omitted, and mismeasured factors, and provides a diagnostic tool for observable factor models. Empirically, nearly all nontradable macro factors have risk premia statistically indistinguishable from zero in equity markets, while standard observable factor models miss important latent pricing factors.

## Theory / model

The paper studies a standard linear latent factor model. Suppose an $$N \times 1$$ vector of test asset excess returns $$r_t$$ follows (equation 1, p. 266):

$$
r_t = \beta\gamma + \beta v_t + u_t, \qquad \mathbb{E}(v_t) = \mathbb{E}(u_t) = 0 \text{ and } \text{cov}(v_t, u_t) = 0, \tag{1}
$$

where $$\beta$$ is an $$N \times p$$ matrix of factor exposures, $$v_t$$ is a $$p \times 1$$ vector of factor innovations ($$v_t = f_t - \mu_f$$), and $$u_t$$ is an $$N \times 1$$ vector of idiosyncratic errors. Factors $$f_t$$ may be latent or observable. The SDF in terms of latent factor innovations is (equation 2, p. 266):

$$
m_t = 1 - \gamma^\top \Sigma_v^{-1} v_t, \tag{2}
$$

and the tradable SDF representation in terms of test asset excess returns is (equation 3, p. 266):

$$
\tilde{m}_t = 1 - b^\top (r_t - \mathbb{E}(r_t)), \tag{3}
$$

where $$b$$ satisfies $$\mathbb{E}(r_t) = \Sigma b$$ and $$\Sigma = \text{cov}(r_t)$$. The observable factor proxy vector $$g_t$$ is linked to the latent factors by (equation 4, p. 267):

$$
g_t = \xi + \eta v_t + z_t, \tag{4}
$$

where $$\xi = \mathbb{E}(g_t)$$, $$\eta$$ is a $$d \times p$$ matrix of factor loadings of $$g_t$$ on $$v_t$$, and $$z_t$$ is measurement error orthogonal to $$v_t$$. The risk premium of $$g_t$$ is $$\gamma_g = -\text{cov}(m_t, g_t) = \eta\gamma$$.

**Definition of weak factors.** A factor is strong relative to a cross section of $$N$$ test assets when the eigenvalues $$\lambda_i(\beta^\top\beta)$$ grow at rate $$N$$ for all $$i = 1, \ldots, p$$ (the standard "pervasive" assumption of Bai and Ng (2002)). A factor is weak when some $$\lambda_i(\beta^\top\beta)$$ grow at a slower rate than $$N$$. The necessary condition for consistency of PCA-based risk premium estimation in the multi-factor case is (equation 6, p. 275):

$$
N / (\lambda_{\min}(\beta^\top\beta) T) \to 0. \tag{6}
$$

When this fails for even one factor, the PCA estimator of Giglio and Xiu (2021) is inconsistent for risk premia (Proposition 1, p. 270, establishes this in the single-factor case). The same breakdown occurs in the observable-factor context studied by Kan and Zhang (1999), who showed that Fama-MacBeth regressions with useless factors produce invalid inference. Rank deficiency in the beta matrix produces the same failure even when each factor is individually strong (equation 7 example, p. 275).

## Method

SPCA is an iterative selection-and-projection procedure. It adds a supervised screening step (Step S1) to the PCA-based risk premium estimator of Giglio and Xiu (2021). For the single-factor case (Algorithm 2, p. 273):

- **S1 (Selection).** Select a subset $$\hat{I} \subset \langle N \rangle$$ of test assets by correlation with $$g_t$$:
$$
\hat{I} = \left\{ i \mid T^{-1} \| \bar{R}_{[i]} \bar{G}^\top \| \geq c_q \right\},
$$
where $$c_q$$ is the $$(1-q)$$-quantile of the absolute covariances $$\{ T^{-1} | \bar{R}_{[i]} \bar{G}^\top | \}_{i \in \langle N \rangle}$$. Only the top $$qN$$ assets are kept.
- **S2.** Run Steps S1 to S3 of the PCA-based Algorithm 1 on the selected return matrix $$\bar{R}_{[\hat{I}]}$$, $$\bar{G}$$, and $$p = 1$$.

The output is $$\hat{\gamma}_g^{\text{SPCA}} := \hat{\eta}\hat{\gamma}$$.

For the general multifactor case, SPCA iterates selection and projection (Algorithm 3, p. 277). At each step $$k$$:

**(S1.a)** Select $$\hat{I}_k$$ using covariance with residuals of $$G_{(k)}$$:
$$
\hat{I}_k = \left\{ i \mid T^{-1} \| (\bar{R}_{(k)})_{[i]} \bar{G}_{(k)}^\top \|_{\text{MAX}} \geq c_q^{(k)} \right\}. \tag{9}
$$

**(S1.b)** Apply Algorithm 1 to $$(\bar{R}_{(k)})_{[\hat{I}_k]}$$ and $$\bar{G}_{(k)}$$ to extract the $$k$$-th latent factor $$\hat{V}_{(k)}$$.

**(S1.c)** Project $$\bar{R}_{(k)}$$ onto $$\hat{V}_{(k)}$$ to obtain $$\hat{\beta}_{(k)}$$.

**(S1.d)** Update residuals: $$\bar{R}_{(k+1)} = \bar{R}_{(k)} - \hat{\beta}_{(k)}\hat{V}_{(k)}^\top$$, $$\bar{G}_{(k+1)} = \bar{G}_{(k)} - \hat{\eta}_{(k)}\hat{\gamma}_{(k)}$$.

Stop at $$k = \hat{p}$$ when $$c_q^{(k)} < c$$ for threshold $$c$$ (equation 10). The final risk premium estimate is $$\hat{\gamma}_g^{\text{SPCA}} = \sum_{k=1}^{\hat{p}} \hat{\eta}_{(k)}\hat{\gamma}_{(k)}$$.

**Consistency (Theorem 1, p. 279).** Under mild moment conditions, if $$\log(NT)(N_0^{-1} + T^{-1}) \to 0$$ and tuning parameters satisfy:
$$
c \to 0, \quad c^{-1}(\log NT)^{1/2}(q^{-1/2}N^{-1/2} + T^{-1/2}) \to 0, \quad qN/N_0 \to 0, \tag{11}
$$
then $$\hat{\gamma}_g^{\text{SPCA}} \xrightarrow{P} \eta\gamma$$. Theorem 2 (p. 280) additionally gives a CLT: $$\sqrt{T}(\hat{\gamma}_g^{\text{SPCA}} - \eta\gamma) \xrightarrow{d} \mathcal{N}(0, \Phi)$$ under stronger conditions including $$\lambda_{\min}(\eta^\top\eta) \gtrsim 1$$, i.e., $$g_t$$ contains at least as many variables as true factors.

**Comparison with alternatives.** The Ridge estimator (Kozak, Nagel, and Santosh (2020)) converges at rate $$(N+T)/(\lambda_p T)$$, which fails when condition (6) fails (Theorem 4a, p. 286). The Lasso estimator is consistent but at a slower rate $$\|b\|_1 \sqrt{\log N / T}$$ (Theorem 4b). Lettau and Pelger (2020) propose risk-premium PCA (rpPCA) for weak factors, but the paper shows rpPCA is inconsistent for risk premia in the multifactor weak-factor setting studied here (Internet Appendix Section I). SPCA combines factor structure (via PCA) with supervision (via screening), achieving the $$T^{-1/2}$$ rate without requiring the strong sparsity assumption.

Tuning parameters $$p$$ (number of factors) and $$\lfloor qN \rfloor$$ (number of selected assets) are chosen by three-fold cross-validation, maximizing the time-series $$R^2$$ of the hedging portfolio for $$g_t$$ in the training sample.

## Empirical specifications

The empirical analysis uses monthly data from March 1976 to December 2020, split into training (first half) and evaluation (second half) subsamples. Two test asset universes are used:

- **Main (Chen and Zimmermann (2022)):** 901 characteristic-sorted portfolios (as many as each anomaly's original paper used, 2 to 10 sorts) plus 49 industry portfolios from Ken French. The CZ data use the April 2021 release.
- **Robustness (Hou, Xue, and Zhang (2020)):** 1,672 portfolios sorted by characteristics (momentum, value, investment, profitability, intangibles, frictions).

Factors studied include eight tradable factors (market excess return, HML, SMB, RMW, CMA, momentum, BAB, QMJ) and twelve nontradable factors (liquidity, intermediary capital, IP growth, three LN macro principal components, three Jurado-Ludvigson-Ng uncertainty indexes, term spread, credit spread, unemployment, two sentiment indexes, oil, consumption growth). All factor data are at the monthly frequency.

**Risk premium estimation (Table IV, R1-R3).** SPCA is applied factor-by-factor ($$d=1$$, each factor as its own $$g_t$$) and jointly ($$d=p$$, all factors simultaneously) with $$p \in \{3, 5, 7, 11\}$$. For each $$(p, q)$$ pair, SPCA: (i) selects $$\lfloor qN \rfloor$$ assets with the largest absolute covariance with $$g_t$$; (ii) runs PCA on those assets to extract $$p$$ factors; (iii) uses Fama-MacBeth-type time-series regressions to estimate risk premia. The out-of-sample $$R^2$$ of the hedging portfolio for $$g_t$$ is reported in the evaluation half.

**SDF diagnosis (Figure 9, R8).** For each observable factor model $$g_t$$ (CAPM; the Fama and French (1993) three-factor model FF3; FF5; FF5+Momentum; FF5+Momentum+BAB+QMJ), SPCA extracts up to 20 latent factors using $$g_t$$ as supervisor. The out-of-sample Sharpe ratio of the SPCA-based SDF (right-hand side of equation 20, p. 288) is compared to the Sharpe ratio of $$g_t$$. A SPCA Sharpe ratio exceeding the model's own Sharpe indicates missing factors.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Chen and Zimmermann (2022) open-source asset pricing library | Main test asset cross section: 901 characteristic-sorted equity portfolios, April 2021 release, 1976m3-2020m12 | [Open Source Asset Pricing](/wiki/datasets/open-source-asset-pricing/) (no page yet) |
| Hou, Xue, and Zhang (2020) replicating anomalies library | Robustness test asset cross section: 1,672 characteristic-sorted portfolios | No page yet |
| Ken French Data Library | 49 industry portfolios (added to CZ cross section); Fama-French factor returns (FF3, FF5) for benchmarking | [Ken French library](/wiki/datasets/ken-french/) |
| Tradable factor returns (market, SMB, HML, RMW, CMA, BAB, QMJ, momentum) | Observable factor proxies $$g_t$$ for risk premium estimation | No page yet |
| Nontradable factor series (liquidity, intermediary capital, IP growth, LN macro PCs, uncertainty, sentiment, term, credit, unemployment, oil, consumption) | Nontradable observable factor proxies $$g_t$$; sources include Pastor-Stambaugh, AQR, FRED, Ludvigson-Ng, Jurado-Ludvigson-Ng, Baker-Wurgler, national accounts | No page yet |

Sample: monthly, 1976m3-2020m12 (about 537 months). Training: 1976m3-1998m7; evaluation: 1998m8-2020m12 (approximately equal halves).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13415) if you are:
estimating risk premia for a potentially weak factor and need a consistent estimator robust to omitted factors and measurement error; diagnosing whether an observable factor model (CAPM, FF3, FF5, or richer) spans the SDF; extending the asymptotic inference results (Theorems 1-2, 4-5) to new DGPs; or applying SPCA to asset classes or frequencies beyond the monthly US equity setting studied here. The locators above point to the key tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. Copyright 2024 the American Finance Association. Paywalled; extract-only. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**.

> Giglio, Stefano, Dacheng Xiu, and Dake Zhang. "Test Assets and Weak Factors."
> *The Journal of Finance* 80, no. 1 (February 2025): 259-319.
> DOI: 10.1111/jofi.13415. Copyright 2024 the American Finance Association.
> This page is an **extract** by the Institute for Automated Research;
> paywalled source, extract-only rights.
