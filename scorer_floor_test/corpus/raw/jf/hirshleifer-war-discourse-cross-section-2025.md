---
title: "War Discourse and the Cross Section: Hirshleifer, Mai & Pukthuanthong (2025)"
description: >-
  Distilled: a war-discourse factor (WarFac) derived from 7 million New York Times
  articles via semisupervised topic modelling predicts the cross section of stock
  returns with a significant, negative return premium across six broad sets of test
  assets. J. Finance 2025, paywalled. Eight core results with source locators,
  datasets used, the model, and the method with defining equations.
sidebar:
  label: Hirshleifer-Mai-Pukthuanthong 2025
  order: 1
tags: [paper-summary, asset-pricing, anomalies, text-as-data, factors, disaster-risk, return-predictability, fama-macbeth, portfolio-sort, peer-reviewed, unreplicated, data:nyt-news, data:wrds, data:ken-french, data:open-source-asset-pricing]
paper:
  authors: David Hirshleifer, Dat Mai, Kuntara Pukthuanthong
  authorList:
    - { family: Hirshleifer, given: David, affiliation: "Marshall School of Business, University of Southern California" }
    - { family: Mai, given: Dat, affiliation: "MKT MediaStats, LLC" }
    - { family: Pukthuanthong, given: Kuntara, affiliation: "Trulaske College of Business, University of Missouri-Columbia" }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3589–3637
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13482
  license: 'Paywalled. © 2025 the American Finance Association (asserted on artifact p. 3589). Crossref DOI metadata returns license content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start 2025-09-01; Wiley standard terms, not an open licence.'
  licenseShort: paywalled
  access: paywalled
  machineAccess: 'blocked-paywall (Wiley/Crossref vor terms; checked 2026-05-31)'
  redistribution: 'extract-only. © American Finance Association; no CC licence; redistribution not permitted.'
  dataAccess: licensed-commercial
  outcome:
    - cross-sectional stock returns
    - expected return premium on WarFac betas across test-asset sets
  outcomeClass: [security-returns]
  resultsCount: 8
  citedByCount: 5
  jel:
    codes: [G12, G14, G41]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Market Dynamics and Volatility', 'Financial Risk and Volatility Modeling']
  methods:
    role: both
    contributes: warfac
    family: descriptive
    buildsFrom: [slda-topic-model, fama-macbeth, ar1-innovation]
    identification: descriptive
  contributionType: [new-method, new-fact, measurement]
  mechanisms: [behavioral-bias, disaster-risk-premium]
  scope:
    region: US
    assetClass: US equities
    period: 1926-07..2018-12
    frequency: monthly
    dataType: [text, market]
    granularity: [security]
    n: "up to 4,964 portfolios as test assets; 532 months (Jul 1972-Dec 2016) for main pricing tests; ~7M NYT articles (Jan 1871-Oct 2019)"
  findings:
    - { ref: R1, outcome: cross-sectional stock returns, metric: coefficient, value: "lambda = -1.33%/mo (t = -2.87) standalone; -0.47% with all benchmark factors", direction: negative, vsBenchmark: "vs FF6, M4, DHS, Q5 multifactor benchmarks" }
    - { ref: R2, outcome: expected return premium on WarFac betas across test-asset sets, metric: coefficient, value: "lambda ranges -0.66%/mo (t = -2.25) to -3.32%/mo (t = -3.42) across six test-asset sets", direction: negative }
    - { ref: R3, outcome: cross-sectional stock returns, metric: r-squared, value: "single-factor R-squared = 62% for ML portfolios; adding WarFac to FF6 raises R-squared by 34%", direction: positive, vsBenchmark: "beats FF6 (41%), M4 (40%), DHS (35%), Q5 (58%) as single factor" }
    - { ref: R4, outcome: cross-sectional stock returns, metric: coefficient, value: "WarFac lambda -1.33%/mo to -3.32%/mo, significant across all six test-asset sets with traded factors included", direction: negative, vsBenchmark: "incremental to MKT, SMB, HML, RMW, CMA, MOM, mispricing factors" }
    - { ref: R5, outcome: cross-sectional stock returns, metric: coefficient, value: "WarFac: -1.04%/mo (HXZ long-short), -2.76%/mo (ML portfolios) with NVIX and GPR included; NVIX and GPR insignificant", direction: negative, vsBenchmark: "incremental to NVIX and GPR uncertainty indexes" }
    - { ref: R6, outcome: cross-sectional stock returns, metric: coefficient, value: "lambda(WarFac) = -0.24%/mo (t = -1.89) alone in 30-industry portfolios; -0.32%/mo (t = -2.39) jointly with CrisisFac", direction: negative, vsBenchmark: "incremental to CrisisFac and CWarFac" }
    - { ref: R7, outcome: expected return premium on WarFac betas across test-asset sets, metric: sharpe-ratio, value: "annualized Sharpe ratio = 1.73; monthly average return = -3.32%, monthly SD = 6.64%", direction: positive, vsBenchmark: "highest among all factors in the sample" }
  resultType: new-finding
  relatesTo:
    - { cite: 'Hirshleifer, Mai & Pukthuanthong (2025)', doi: '10.1093/rfs/hhae081', relation: extends, note: 'extends the War index used there for aggregate return prediction to cross-sectional pricing (p. 3590)' }
    - { cite: 'Barro (2006, 2009)', relation: tests, note: 'tests the rare-disaster risk cross-sectional prediction; war-sensitive assets earn lower premia consistent with the model (p. 3601)' }
    - { cite: 'Manela & Moreira (2017)', doi: '10.1016/j.jfineco.2016.01.032', relation: contradicts, note: 'NVIX does not command a significant return premium across all six test-asset sets; WarFac is incremental to NVIX (Table IV, p. 3623)' }
    - { cite: 'Caldara & Iacoviello (2022)', doi: '10.1257/aer.20191823', relation: contradicts, note: 'GPR index does not command a significant return premium across all six test-asset sets (Table IV, p. 3623)' }
    - { cite: 'Berkman, Jacobsen & Lee (2011)', doi: '10.1016/j.jfineco.2011.02.019', relation: extends, note: 'WarFac provides incremental predictive power beyond CrisisFac for industry portfolios (Table V, p. 3626)' }
    - { cite: 'Bryzgalova, Huang & Julliard (2023)', relation: tests, note: 'uses their ML-based nonlinear portfolios as test assets; WarFac explains 62% of cross-sectional variance there (Table II Panel D, p. 3617)' }
  openQuestions:
    - 'Whether the rational rare-disaster and behavioral-overweighting interpretations can be distinguished; both are observationally consistent with a negative return premium on WarFac (p. 3634).'
    - 'Whether WarFac + can be reliably separated from WarFac - as distinct economic channels; the paper finds both price assets but with differing coverage across test-asset sets (p. 3633).'
  replicationCode:
    status: upon-request
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full text read (pp. 3589–3637 of the print PDF). Eight results extracted from the paywalled PDF. Not human-verified. Not reproduced. Data and code available upon request from the authors (per p. 3603 fn. 16).
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-01
      role: extracted
      note: Augment pass. Added methods, scope, relatesTo, openQuestions, replicationCode, proposedVocab frontmatter blocks, and three formal body sections (Theory / model, Method, Empirical specifications) with equations transcribed from pp. 3596-3603, 3625, 3628-3629 of the source PDF read this session. Core results table preserved verbatim from the verified version. New formal sections are extracted, not yet re-verified by paper-verifier.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-01
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF (all 49 pages read); equations 1-9 verified term-by-term against PDF pp. 3602-3603, 3625, 3628-3629; one fix applied - R1 multifactor R² range corrected from 59-77% to 51-77% (PDF p. 3610 gives FF6 59%, M4 65%, DHS 51%, Q5 77%); all other magnitudes, t-stats, and locators confirmed correct.
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
        applied - added new-method to contributionType (methods.role is both,
        and the sLDA-based cross-sectional war factor construction is a proposed
        method); identification=descriptive, mechanisms, scope confirmed correct;
        introducesData correctly absent (War index introduced in companion RFS
        paper, not here).
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
        against the source PDF; all seven entries confirmed correct - R1 lambda
        -1.33%/t=-2.87 (Table I Panel A), R2 range -0.66% to -3.32% (Table I
        all panels), R3 R-squared 62% (Table II Panel D), R4 lambda range
        (Table III), R5 WarFac -1.04% and -2.76% with NVIX/GPR (Table IV),
        R6 -0.24% and -0.32% (Table V Panel A), R7 SR=1.73/mean=-3.32%/SD=6.64%
        (p. 3627); resultType=new-finding defensible given headline contribution
        is a genuinely new cross-sectional war risk premium; no fixes applied.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13482
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-09-01. No CC licence present. Copyright: © 2025 the American Finance Association (artifact p. 3589).'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, datasets, and theory: enough
to know what it found without reading all 49 pages. To replicate or extend
it, consult the [original](https://doi.org/10.1111/jofi.13482) (paywalled)
or request data and code from the authors.

## TL;DR

Using 7,000,000 *New York Times* articles spanning 1871 to 2019, the paper
builds a monthly war-discourse index (*War*) via a semisupervised topic model
(sLDA, one seed word: *war*), then defines the war factor WarFac as the
AR(1) innovation in *War*. Loadings on WarFac significantly and negatively
predict expected returns across six sets of test assets covering up to 4,964
portfolios (138 HXZ long-short anomalies, 1,372 HXZ single-sorted, 904 CZ
single-sorted, 360 ML-based nonlinear, and 128 and 2,190 own-constructed
portfolios), with a monthly return premium ranging from about -0.66% to
-3.32% per month. WarFac is incremental to the Fama-French six-factor model
and to news-based uncertainty indexes (NVIX, GPR). A mimicking portfolio
(WMP) earns an annualised Sharpe ratio of 1.73 and passes the Pukthuanthong
et al. (2019) factor-identification protocol and the Giglio-Xiu three-pass test.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.
Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | WarFac commands a **significant negative return premium** on 138 HXZ long-short anomaly portfolios | Table I Panel A, Table II Panel A, p. 3607–3611 | λ = -1.33%/mo (t = -2.87\*\*\*) standalone; remains -0.47%\*\* with all FF6+M4+DHS+Q5 factors; R² = 48% as single factor vs 51–77% for multifactor benchmarks (FF6 59%, M4 65%, DHS 51%, Q5 77%) |
| R2 | WarFac return premium is **negative and significant for all six sets** of test assets; consistently ranks in the top three among 11 nontraded factors | Table I (all panels), p. 3607–3610 | λ ranges from -0.66%\*\* (HXZ single-sorted, t = -2.25) to -3.32%\*\*\* (ML portfolios, t = -3.42); no other nontraded factor achieves this across all six sets |
| R3 | WarFac **explains 62% of cross-sectional variance** in ML-based nonlinear portfolio returns as a single factor, outperforming FF6 (41%), M4 (40%), DHS (35%), Q5 (58%) | Table II Panel D, p. 3617–3618 | Single-factor R² = 62%; adding WarFac to FF6 raises R² by 34%; common pricing error falls from 3.3% to near zero |
| R4 | WarFac return premium is **incremental to traded factors** (WMP, MKT, SMB, HML, RMW, CMA, MOM and mispricing factors); CMA and WarFac are the only factors significant across all six test-asset sets | Table III (all panels), p. 3619–3622 | WarFac: -1.33%\*\*\* to -3.32%\*\*\* depending on test assets; CMA also consistently significant; WMP -2.19%\*\* to -3.32%\*\*\* |
| R5 | WarFac is **incremental to NVIX and GPR** uncertainty indexes; NVIX and GPR do not command significant return premia across all test assets | Table IV (all panels), p. 3623–3624 | With all three factors, WarFac: -1.04%\*\* (HXZ long-short), -2.76%\* (ML portfolios); NVIX_War2Fac: insignificant for HXZ and ML; GPRFac: insignificant across all panels |
| R6 | WarFac **prices industry portfolios** with a negative premium, incremental to the CrisisFac (crisis event counts) of Berkman et al. (2011) | Table V, p. 3626 | 30-industry portfolios: λ(WarFac) = -0.24%\* (t = -1.89) alone; -0.32%\*\* (t = -2.39) with CrisisFac and CWarFac jointly; 49-industry: -0.28%\*\* (t = -2.16) in joint specification |
| R7 | WMP (the traded mimicking portfolio for WarFac) has a **Sharpe ratio of 1.73**, the highest among all factors in the sample, and generates significant alphas against all benchmark factor models | §V.A and Internet Appendix Table IA.III, p. 3627–3628 | Monthly average return = -3.32%, monthly SD = 6.64%; annualised Sharpe = 1.73; monthly alpha vs all factors ≈ 3.10%\*\*\* (t-stat in Internet Appendix); WMP passes three-pass test and factor-identification protocol |
| R8 | WarFac **captures a distinct tail risk**: return premium survives after controlling for CAPM beta, bear beta, downside beta, VIX beta, volatility beta, jump beta, coskewness, skewness beta, tail beta, and idiosyncratic volatility | §VII.A and Internet Appendix Table IA.VII, p. 3632 | WarFac premium remains significant with all tail-risk mimicking portfolios included; it is the only nontraded factor with a significant beta return premium on HXZ single-sorted portfolios in this horse race |

**Overall (paper's conclusion, p. 3634).** Loadings on the war-discourse factor
strongly predict the cross section of stock returns with a negative premium,
consistent with rational rare-disaster hedging (good hedges earn low premia)
or with behavioral overweighting of war prospects (war-sensitive stocks are
overpriced). The war premium is incremental to all standard factor models
and to other news-based uncertainty measures, and is driven by factual war
news rather than opinion articles.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| *New York Times* full text, Jan 1871–Oct 2019 (~7M articles) | Source corpus for sLDA topic modelling; constructs the *War* index | no page yet; proprietary/licensed archive |
| CRSP monthly stock returns and characteristics | Returns for all six test-asset sets; underlying portfolio construction data | [WRDS / CRSP / Compustat](/wiki/licensed/wrds/) (licensed) |
| Compustat | Firm fundamentals for anomaly characteristic construction | [WRDS / CRSP / Compustat](/wiki/licensed/wrds/) (licensed) |
| Hou, Xue & Zhang (2020) HXZ anomaly portfolios (138 long-short, 1,372 single-sorted) | Primary test-asset sets; Jul 1972–Dec 2016 | no page yet; available from HXZ replication files |
| Chen & Zimmermann (2022) single-sorted portfolios (904) | Third test-asset set; available from open-source-asset-pricing project | [Open Source Asset Pricing](/wiki/datasets/open-source-asset-pricing/) |
| Bryzgalova, Huang & Julliard (2023) ML-based nonlinear portfolios (360) | Fourth test-asset set; tree-based nonlinear portfolios | no page yet |
| Ken French Data Library (size, B/M, momentum portfolios) | Basis assets for WMP time-series mimicking; Fama-French factor benchmarks | [Ken French Data Library](/wiki/datasets/ken-french/) |
| Berkman, Jacobsen & Lee (2011) crisis event counts | CrisisFac and CWarFac benchmarks for §IV.B industry tests; data from sites.duke.edu/icbdata | no page yet |
| NVIX (Manela & Moreira 2017) | Benchmark news-based uncertainty index; horse-race test in §IV.A | no page yet |
| GPR index (Caldara & Iacoviello 2022) | Benchmark geopolitical risk index; horse-race test in §IV.A | no page yet |

Sample period for asset pricing tests: Jul 1972–Dec 2016 (532 months). *War* index: Jan 1871–Oct 2019.

## Theory / model

This paper has no original structural model. It tests two competing,
observationally equivalent theoretical frameworks:

1. **Rational rare-disaster risk** (Barro 2006, 2009; Gourio 2008; Gabaix
   2012, p. 3601): investors demand a risk premium for bearing war-related
   disaster risk. Assets that pay off when war risk is high are good hedges
   and therefore command lower expected returns. A negative cross-sectional
   return premium on WarFac betas is the central prediction.

2. **Behavioral overweighting** (Daniel, Hirshleifer & Subrahmanyam 2001;
   Tversky & Kahneman 1992 cumulative prospect theory, p. 3601): investors
   overweight the probability of rare salient disasters such as war,
   overvaluing stocks that do well under high war risk, so those stocks
   subsequently earn lower returns. The same negative premium arises for
   behavioral reasons.

The paper tests both frameworks by constructing a text-based proxy for
investor attention to war risk rather than relying on realized war events,
which have small sample sizes. Identification rests on the rolling-forward
estimation of the sLDA model and the AR(1) residual (WarFac), which ensures
only past information is used at each point in time, avoiding look-ahead
bias (p. 3591).

## Method

The method has two components: (1) constructing the *War* index via
semisupervised topic modelling (sLDA), and (2) building WarFac as the
innovation in *War* via a rolling AR(1). It builds on `slda-topic-model`
and `ar1-innovation`. The *War* index used here is the same one that the
companion aggregate-return study of Hirshleifer, Mai, and Pukthuanthong
(2025, Review of Financial Studies) uses; this paper extends it to
cross-sectional pricing (p. 3590).

**sLDA topic model (pp. 3596-3598).** Each month $$t$$, the model is estimated
on all *New York Times* articles in the preceding 120 months (the rolling
window $$[t-119, t]$$). Using Gibbs sampling, the model infers, for each
document $$d$$, the document-topic distribution $$\theta_d$$ (a vector of topic
probabilities) and, for each topic $$k$$, the topic-word distribution
$$\phi_k$$ (a vector of word probabilities). The seed word for the War topic
is *war* (a single word, for parsimony and to avoid researcher discretion
in seed-word selection). The global monthly weight of topic $$k$$ in month
$$t$$ is the length-weighted average across all articles $$d$$ in month $$t$$:

$$
\text{War}_t = \frac{1}{\sum_d \text{len}_d} \sum_d \text{len}_d \cdot \theta_{d,k=\text{War}}
$$

- $$\text{len}_d$$ is article length in n-gram count.

The rolling window allows
topic-word distributions $$\phi_k$$ to shift with language over time, which
is essential for a corpus spanning 1871 to 2019 (p. 3597).

**AR(1) innovation (p. 3603, equations 3 and 4).** Following Berkman,
Jacobsen & Lee (2011), Liu & Matthies (2022), and Giglio & Xiu (2021),
WarFac is defined as the residual from a rolling AR(1) fit to *War*,
estimated at each month $$t$$ using data from 1926 to $$t$$ to avoid
look-ahead bias:

$$
\text{War}_t = \rho_0 + \rho \cdot \text{War}_{t-1} + u_t \tag{3}
$$

$$
\text{WarFac}_t = u_t \tag{4}
$$

The AR(1) coefficients $$(\rho_0, \rho)$$ are re-estimated each month on the
growing window of available data. Results are robust to using an ARMA(1,1)
residual or a rolling-regression residual (pp. 3591, 3603 fn. 13).

**War-mimicking portfolio (WMP).** The traded version of WarFac is
constructed using the cross-sectional approach of Lehmann & Modest (1988):
the slope from the monthly second-pass cross-sectional regression of
asset returns on WarFac betas is the monthly WMP return (p. 3627). As a
robustness check, the time-series approach projects WarFac onto the space
of excess returns of 360 tree-based portfolios plus basis assets:

$$
\text{WarFac}_t = \alpha + \beta' R^e_t + \epsilon_t \tag{8}
$$

$$
\text{WMP}_t = \hat{\beta}' R^e_t \tag{9}
$$

- $$R^e$$ is the vector of excess returns on basis assets.
- $$\hat{\beta}$$ is estimated by OLS on the full sample.

## Empirical specifications

All asset pricing tests use monthly data, July 1972 to December 2016
(T = 532 months for WarFac; T = 522 for tests including NVIX_War and GPR).

**First pass: factor loadings (eq. 1, p. 3602).** For each test asset
$$i = 1, \ldots, N$$, excess returns are regressed on a vector of factors $$F_t$$
in a multivariate time-series regression:

$$
R^e_{it} = \alpha_i + \beta_{iF}' F_t + \epsilon_{it}, \quad i = 1, \ldots, N \tag{1}
$$

The paper reports $$\text{avg}(|t|)$$ (average absolute beta t-statistic) and the
number of assets with $$|t| \geq 1.65$$ (the 5% one-sided threshold). This
first pass is run for each of the six test-asset sets separately.

**Second pass: cross-sectional return premium (eq. 2, p. 3602).** Time-series
average excess returns are regressed cross-sectionally on the estimated factor
loadings:

$$
\bar{R}^e_{i} = \lambda_0 + \beta_{iF}' \lambda_F + e_i \tag{2}
$$

- $$\lambda_F$$ is the vector of return premium slopes.
- Standard errors are Shanken (1992) corrected.
- The paper reports $$\lambda$$ and its $$t$$-statistic, cross-sectional $$R^2 = 1 - \sigma^2_e / \sigma^2_{\mu}$$, and mean absolute pricing error $$\text{MAPE} = |\bar{e}|$$.
- Under rational pricing, $$\lambda_0 = 0$$.

**Industry portfolios: rolling Fama-MacBeth with betas (eqs. 5-6, p. 3625).**
For the industry pricing tests (§IV.B), betas are estimated over a rolling
60-month window for excess returns on factor $$X$$ (WarFac, CrisisFac, or
CWarFac) plus market, size, and value controls:

$$
R^e_{it} = \alpha_i + \beta_{it} X_t + \beta^{\text{MKT}}_{it} \text{MKT}_t + \beta^{\text{SMB}}_{it} \text{SMB}_t + \beta^{\text{HML}}_{it} \text{HML}_t + \epsilon_{it}, \quad \text{window: } t\text{-}59 \text{ to } t \tag{5}
$$

Cross-sectional betas are ranked into quintiles each month $$t$$ and rescaled
to $$[0, 1]$$. The monthly return premium is estimated by:

$$
R^e_{it} = \lambda_{0t} + \lambda_t \beta_{i,t-1} + \lambda^{\text{MKT}}_t \beta^{\text{MKT}}_{i,t-1} + \lambda^{\text{SMB}}_t \beta^{\text{SMB}}_{i,t-1} + \lambda^{\text{HML}}_t \beta^{\text{HML}}_{i,t-1} + e_{it} \tag{6}
$$

- Time-series averages of $$\lambda_t$$ are reported; statistical significance uses Newey-West (1987) standard errors.
- Sample period for industry tests: July 1926 to December 2018 (T = 1,110 months for Panels A and B of Table V, p. 3626).

**WMP spanning test (eq. 7, p. 3628).**

$$
\text{WMP}_t = \alpha + \beta' F_t + \epsilon_t \tag{7}
$$

- $$F_t$$ is the vector of benchmark traded factors.
- $$\alpha$$ measures whether WMP expands the mean-variance frontier.
- Monthly alpha of WMP against all factors combined is approximately 3.10%, significant at the 1% level (Internet Appendix Table IA.III, p. 3628).

## When to read the full paper

Use the original at [doi.org/10.1111/jofi.13482](https://doi.org/10.1111/jofi.13482)
(paywalled) if you are: replicating (data and code available from authors on
request per fn. 16); extending the sLDA war-discourse methodology to other
corpora or time periods; doing a literature review where the full robustness
battery (seed-word variants, ARMA(1,1), sLDA vs LDA comparisons, tail-risk
horse races) matters; or auditing a specific coefficient. The locators above
point to the exact table.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025,
pp. 3589–3637. © 2025 the American Finance Association. This distillation
was extracted by an LLM on 2026-05-31 and is **not human-verified or
independently reproduced**. The underlying article is paywalled; no verbatim
PDF is hosted here.

> Hirshleifer, David, Dat Mai, and Kuntara Pukthuanthong. "War Discourse and
> the Cross Section of Expected Stock Returns." *The Journal of Finance* 80,
> no. 6 (December 2025): 3589–3637. DOI: 10.1111/jofi.13482.
> © 2025 the American Finance Association. Extract-only; redistribution
> of the original article is subject to Wiley/AFA terms.
