---
title: "Forest through the Trees: Bryzgalova, Pelger & Zhu (2025)"
description: >-
  Distilled: Asset Pricing Trees (AP Trees) use decision-tree conditional sorts
  with global SDF-spanning pruning to build interpretable cross-sections of stock
  returns that achieve out-of-sample Sharpe ratios up to three times higher than
  conventional double and triple sorts. J. Finance 2025, CC BY 4.0. Eight core
  results with source locators, datasets used, the model (SDF projection), and the
  method (AP Trees + AP Pruning) with its defining equations.
sidebar:
  label: Bryzgalova-Pelger-Zhu 2025
  order: 1
tags: [paper-summary, asset-pricing, factors, anomalies, cross-section, portfolio-sort, decision-trees, factor-models, machine-learning, open-access, cc-by, peer-reviewed, unreplicated, data:wrds, data:ken-french]
paper:
  authors: Svetlana Bryzgalova, Markus Pelger, Jason Zhu
  authorList:
    - { family: Bryzgalova, given: Svetlana, affiliation: London Business School }
    - { family: Pelger, given: Markus, affiliation: Stanford University }
    - { family: Zhu, given: Jason, affiliation: Microsoft }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2447–2506
  venueShort: J. Finance 2025
  licenseShort: CC BY 4.0
  resultsCount: 8
  citedByCount: 13
  jel:
    codes: [G12, G11, C58]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Market Dynamics and Volatility', 'Corporate Finance and Governance']
  dataAccess: licensed-commercial
  outcome:
    - cross-sectional stock returns
    - out-of-sample Sharpe ratio of managed portfolios
    - SDF alpha against leading factor models
  outcomeClass: [security-returns]
  doi: 10.1111/jofi.13477
  license: 'CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-09-02; corroborated by artifact p.2447 Creative Commons Attribution License notice)'
  access: open
  machineAccess: 'blocked-paywall (Wiley site wrapper; not machine-fetched directly; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-05-31)'
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  methods:
    role: proposes-method
    contributes: ap-trees
    family: ml
    buildsFrom: [decision-trees, conditional-sorts, lasso, ridge-shrinkage, sdf-projection, robust-mean-variance-optimization]
    identification: descriptive
  contributionType: [new-method, new-theory, new-fact]
  scope:
    region: US
    assetClass: US equities (CRSP/Compustat common stocks)
    period: 1964-01..2016-12
    frequency: monthly
    dataType: [market, accounting]
    granularity: [security]
    n: "CRSP common stocks, Jan 1964-Dec 2016 (53 years, monthly)"
  relatesTo:
    - { cite: 'Kozak, Nagel & Santosh (2020)', doi: '10.1016/j.jfineco.2019.06.008', relation: extends, note: 'generalizes their robust SDF recovery by also shrinking the mean, not just the covariance (Prop. 2-3)' }
    - { cite: 'Fama & French (1993)', doi: '10.1016/0304-405x(93)90023-5', relation: contradicts, note: 'standard size/value sorts and their stacked combinations do not span the conditional SDF, so they give a misspecified benchmark' }
    - { cite: 'Gu, Kelly & Xiu (2020)', relation: tests, note: 'AP Trees beat ML return-prediction portfolios (random forest, neural nets) on out-of-sample Sharpe ratio and SDF alpha' }
    - { cite: 'Barillas & Shanken (2016)', doi: '10.1093/rfs/hhw101', relation: builds-on, note: 'spanning arguments underlying the omitted-test-asset misspecification bound (Prop. 1)' }
  openQuestions:
    - 'Whether the SDF-spanning cross-section generalizes beyond US equities to other asset classes and international markets, where the characteristic structure differs: the construction is presented as general but tested only on US stocks (pp. 2450, 2455).'
    - 'How much further the construction improves once additional economic constraints (liquidity, market-cap floors, number of test assets, degree of interactions) are imposed, which the paper notes are feasible but does not fully explore (pp. 2452, 2458).'
  findings:
    - ref: R1
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "AP Trees (10) SR = 0.65, AP Trees (40) SR = 0.69 monthly (test block); TS(32) SR = 0.51, TS(64) SR = 0.53; across 36 three-characteristic cross-sections the AP Tree SR is up to 3x the triple-sort SR"
      direction: positive
      vsBenchmark: up to 3x triple-sort SR across 36 cross-sections (Table I, Table B.II)
    - ref: R2
      outcome: SDF alpha against leading factor models
      metric: alpha
      value: "AP Trees (10): alpha vs FF3 = 0.94 (t=10.11), vs FF5 = 0.81 (t=8.76); TS(32): alpha vs FF3 = 0.75 (t=7.40), vs FF5 = 0.47 (t=5.57)"
      direction: positive
      vsBenchmark: AP Trees alpha significantly larger than triple-sort alpha vs all four factor models; triple-sort SDFs routinely spanned
    - ref: R3
      outcome: cross-sectional stock returns
      metric: r-squared
      value: "AP Trees (10) XS-R2 vs FF5 = 11%; AP Trees (40) XS-R2 vs FF5 = 64%; TS(32) XS-R2 vs FF5 = 91%"
      direction: negative
      vsBenchmark: AP Trees (10) XS-R2 is 80pp below TS(32) vs FF5, confirming AP Trees contain pricing information absent from standard factors
    - ref: R4
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "Dropping interaction nodes reduces AP Tree (10) monthly SR from ~0.4-0.65 to roughly the XSF long-short factor level (~0.2); approximately half the SR is lost"
      direction: positive
      vsBenchmark: interaction nodes account for roughly half of AP Trees SR; removing them halves out-of-sample SR (Figure 8)
    - ref: R5
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "AP Trees monthly SR ~0.4-0.65; V-Trees (variance criterion only) SR ~0.2-0.3; ML prediction-based portfolios (DL-MV, RF-MV) SR ~0.2-0.35; V-Trees 2-3x lower than AP Trees"
      direction: positive
      vsBenchmark: SDF-spanning objective raises SR 2-3x over V-Trees; AP Trees SR at least double ML return-prediction portfolios (Figures 9, 15)
    - ref: R6
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "AP Trees (10) SR = 0.65 vs AP Trees (40) SR = 0.69 (size/OP/investment); 10 portfolios retain roughly 90% of the SR of 40 portfolios (paper's stated characterization, p. 2477)"
      direction: positive
      vsBenchmark: 10 pruned portfolios retain roughly 90% of the SR of 40-portfolio cross-section (Figure 7, Table I)
    - ref: R7
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "AP Trees (10/40) SR ~0.5; best DS25 combination SR ~0.4-0.45; decile-sort SR ~0.3; quintile SR ~0.25; AP Trees raise monthly SR by ~0.1 over best 25x9 double-sort"
      direction: positive
      vsBenchmark: ~20% SR gain over best 25x9 double sorts; 80-100% gain over anomaly-based deciles (Figure 14)
    - ref: R8
      outcome: out-of-sample Sharpe ratio of managed portfolios
      metric: sharpe-ratio
      value: "Liquid-stocks (size quantile above 0.4) AP Trees (10): SR = 0.48, alpha vs FF5 = 0.45 (t=5.70); TS(32) SR = 0.25. Top-600-stocks AP Trees (10): SR = 0.30, alpha vs FF3 = 0.70 (t=5.04), alpha vs FF5 = 0.32 (t=3.87); TS(32) SR = 0.17"
      direction: positive
      vsBenchmark: AP Trees SR roughly double triple-sort SR even excluding microcaps; all AP Tree alphas remain significant at 1% while triple-sort SDFs are routinely spanned (Table III)
  resultType: new-finding
  replicationCode:
    status: available
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13477
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-09-02'
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full text read (pp. 2447–2506); eight results extracted from the CC-BY PDF. Not human-verified. Not reproduced. Replication code is referenced in the paper but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-opus-4-8)
      date: 2026-05-31
      role: extracted
      note: 'Pilot reshape to the deepened schema. Added the methods block (role/contributes/family/buildsFrom), scope, relatesTo, openQuestions, proposedVocab, and three formal body sections (Theory / model, Method, Empirical specifications) with equations transcribed from pp. 2455-2468 of the source PDF read this session (SDF projection, eq. 1, Prop. 1, AP-Pruning Def. 1-2 eq. 2, Prop. 2). The Core results table is unchanged from the verified version above. The new formal sections are extracted, not yet re-verified by paper-verifier.'
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: Added classification axes (identification, contributionType, mechanisms, introducesData, data-scope) from a fresh PDF read; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: Classification axes (identification, contributionType, mechanisms, introducesData, data-scope) re-checked against the source PDF; all axes confirmed correct, no changes needed.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the results table and confirmed against the PDF;
        corrected R8 table magnitude (page had alpha vs FF5 = 0.70 t=5.04,
        which is actually the FF3 alpha; PDF Table III Panel B gives alpha vs
        FF3 = 0.70 t=5.04 and alpha vs FF5 = 0.32 t=3.87); existing results
        and sections otherwise unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; R6 value corrected from "~94%" to "roughly 90%"
        to match the paper's own stated characterization (p. 2477, Figure 7
        discussion); all other finding magnitudes confirmed against Table I
        (p. 2482) and Table III (p. 2490); resultType new-finding confirmed.
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it builds on (the SDF
projected on stock returns), and the method it contributes (AP Trees and AP
Pruning) with the defining equations: enough to know what it found and how,
without reading all 60 pages. To replicate or extend it, read the full source
at the [original](https://doi.org/10.1111/jofi.13477).

## TL;DR

The paper proposes Asset Pricing Trees (AP Trees): a decision-tree method
that groups individual stocks into managed portfolios by conditional
characteristic splits, then selects a sparse subset via global SDF-spanning
pruning (LASSO + robust mean/variance shrinkage). Applied to 10
CRSP/Compustat characteristics (Jan 1964 to Dec 2016, 53 years of monthly
data), AP Trees deliver small cross-sections of 10 to 40 long-only
portfolios whose combined out-of-sample Sharpe ratio is up to three times
higher than conventional double/triple sorts, and whose SDF alpha is
significant against all leading factor models. The key drivers are
(i) modeling characteristic interactions via conditional splits and
(ii) optimizing the SDF-spanning objective rather than return prediction.

## Core results

Magnitudes and significance are as reported; `**`/`***` = 5%/1%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | AP Trees deliver **out-of-sample Sharpe ratios up to three times higher** than conventional triple sorts across all 36 three-characteristic cross-sections | Figure 6, Panel A, p. 2474; Table B.II, p. 2497 | AP Tree SR ranges from ~0.24 to ~0.65 (monthly); triple-sort SR rarely exceeds 0.4; difference is up to 3x for cross-sections including investment, idiosyncratic volatility, or profitability |
| R2 | **AP Tree SDF alphas are large and significant** against FF3, FF5, XSF, and FF11 models; triple-sort SDFs are routinely spanned | Table I, p. 2482; Figure 6, Panel B, p. 2474 | For size/OP/investment: AP Trees (10) α = 0.94 vs FF3 (t=10.11), 0.81 vs FF5 (t=8.76); triple sorts α = 0.75 vs FF3 (t=7.40), 0.47 vs FF5 (t=5.57) |
| R3 | **Cross-sectional fit (XS-R²) is far lower for AP Trees**, confirming they contain pricing information not in standard factor models | Table I, p. 2482 | AP Trees (10) XS-R² vs FF5 = 11%; triple sorts (32) XS-R² vs FF5 = 91%; AP Trees (40) = 64% vs 91% for TS(32) |
| R4 | **Interaction nodes account for roughly half of AP Trees' SR**; removing interactions halves the out-of-sample Sharpe ratio | Figure 8, p. 2478 | AP Tree (10) monthly SR ~0.4–0.65 with interactions; dropping interactions reduces SR to roughly that of XSF long-short factors (~0.2); similar pattern for AP Trees (40) |
| R5 | **SDF-spanning objective drives the result**: V-Trees (same splits, variance criterion only) have 2–3x lower SR; ML return-prediction portfolios (deep learning, random forest) have SR at best half that of AP Trees | Figure 9, p. 2481; Figure 15, p. 2494 | AP Trees monthly SR ~0.4–0.65; V-Trees ~0.2–0.3; DL-MV, RF-MV ~0.2–0.35 across 10-characteristic cross-sections |
| R6 | **10 pruned AP Tree portfolios retain ~90% of the SR** of 40-portfolio cross-sections, showing the quality of the cross-section is not driven by size | Figure 7, p. 2477; Table I, p. 2482 | AP Trees (10) SR = 0.65 vs AP Trees (40) SR = 0.69 for size/OP/investment; 10 portfolios already span ~90% of the SDF |
| R7 | **In the large-dimension setting (10 characteristics), AP Trees raise monthly SR by ~0.1 over the best 25x9 double-sort cross-section** (roughly 20% gain), and 80–100% over anomaly-based deciles | Figure 14, p. 2493; §V | AP Trees (10/40) achieve SR ~0.5; best DS25 combination reaches ~0.4–0.45; decile-sort SR ~0.3; quintile SR ~0.25 |
| R8 | **Microcaps do not drive results**: excluding small caps (size quantile below 0.4) or restricting to the top 600 stocks by market cap, AP Trees still roughly double the SR of triple sorts | Table III, p. 2490 | Top-600-stocks AP Trees (10): SR = 0.30, alpha vs FF3 = 0.70 (t=5.04), alpha vs FF5 = 0.32 (t=3.87); triple sorts SR = 0.17 (TS32) / 0.17 (TS64) |

**Overall (paper's conclusion).** Conventional single/double/triple sorts and
their stacked combinations, including the size and value sorts of Fama and
French (1993), do not span the conditional SDF and so provide an unreliable
and often misspecified benchmark for asset pricing models. AP Trees resolve
this by finding a small,
interpretable, well-diversified cross-section that genuinely spans the
conditional SDF projected on characteristics, enabling better model
evaluation and construction of tradable risk factors.

## Theory / model

The economic object is the stochastic discount factor (SDF) that prices
individual stocks. Under no-arbitrage there is a unique minimum-variance SDF
spanned by individual stock excess returns. Given a set of firm characteristics
$$C_{t-1}$$ (an $$N \times K$$ matrix for $$N$$ stocks, $$K$$ characteristics) as the
conditioning information, the conditional SDF is its projection on individual
stock excess returns $$R_t$$ (p. 2455):

$$
M_t^C = 1 - \sum_{i=1}^N b_{t-1,i} \left( R_{t,i} - \mathbb{E}_{t-1}[R_{t,i}] \right), \qquad b_{t-1,i} = f(C_{t-1,i})
$$

with $$f(\cdot)$$ a general, potentially nonlinear and nonseparable function.
Reduced-form models approximate this dependence with $$J$$ basis functions
$$f_j(\cdot)$$, so $$f(C_{t-1,i}) \sim \sum_j f_j(C_{t-1,i}) w_j$$. That turns the
conditional problem into an unconditional one over $$J$$ managed portfolios
(equation 1, p. 2455):

$$
M_t^C = 1 - \sum_{j=1}^J w_j \left( R^{\text{man}}_{t,j} - \mathbb{E}[R^{\text{man}}_{t,j}] \right), \qquad R^{\text{man}}_{t,j} = \sum_{i=1}^N f_j(C_{t-1,i}) R_{t,i}
$$

There is a one-to-one mapping between the basis functions $$f_j$$ and the managed
portfolios $$R^{\text{man}}$$. Managed portfolios **span** the projected SDF exactly when
their mean-variance-efficient combination achieves the highest Sharpe ratio
(p. 2456); pricing a spanning set is then equivalent to pricing the SDF itself.

The paper's theoretical contribution is a misspecification result. Suppose a
researcher uses only a subset $$R^{\text{select}}$$ of the spanning managed portfolios and
omits $$R^{\text{omit}}$$, then proposes a $$K$$-factor model $$F$$ that prices $$R^{\text{select}}$$
(intercept $$\alpha^{\text{select}} = 0$$). Proposition 1 (p. 2457) bounds the mispricing of
the omitted assets by a Sharpe-ratio gap:

$$
\text{SR}^2(R^{\text{select}}, R^{\text{omit}}) - \text{SR}^2(F)
   \leq {\alpha^{\text{omit}}}' (\Sigma^{\text{omit}})^{-1} \alpha^{\text{omit}}
   \leq \text{SR}^2(R^{\text{select}}, R^{\text{omit}}) - \text{SR}^2(R^{\text{select}}),
$$

with equalities if $$R^{\text{select}}$$ spans the factors, that is, if
$$\text{SR}(R^{\text{select}}) = \text{SR}(R^{\text{select}}, F)$$. In words: a model that perfectly explains the
chosen test assets can still be a grossly misspecified model for individual
stocks if those test assets do not span the SDF. The proof follows the spanning
arguments of Barillas and Shanken (2016) and is given in the Internet Appendix.
This is why the choice of test assets, not just the candidate model, matters,
and it motivates constructing a cross-section that provably spans the SDF.

**Identification.** Fully out-of-sample evaluation with a train / validate /
test split (Figure 5, p. 2472): portfolio selection and tuning are fixed on the
first two blocks before the test block, so there is no look-ahead bias.

## Method

The method has two parts: building the tree-based managed portfolios (AP Trees)
and selecting a sparse spanning subset of them (AP Pruning). It builds on
`decision-trees` and `conditional-sorts` for the portfolios, and on `lasso`,
`ridge-shrinkage`, `sdf-projection`, and `robust-mean-variance-optimization`
for the selection.

**AP Trees.** Stocks are grouped by a sequence of conditional consecutive
splits (median splits at each node, without loss of generality), so each final
and intermediate node is a managed portfolio that traces back to firm
fundamentals (Figure 1, p. 2449). Trees are grown to depth four. With $$M$$
candidate splitting characteristics and depth $$d$$, this yields $$M^d \times 2^d$$
overlapping portfolios that capture up to $$d$$-way interactions. Equivalently,
AP Trees are a nonparametric estimator of the SDF mapping (p. 2463):

$$
f(C_{t-1,i}) = \sum_{j=1}^J w_j \cdot \mathbf{1}\{ C_{t-1,i} \in A_j \}, \qquad \text{regions } A_j \text{ given by the recursive tree nodes}
$$

**AP Pruning.** The naive SDF weights solving $$\mathbb{E}[R^{\text{man}} M^C] = 0$$ are
$$\omega = \Sigma^{-1} \mu$$, whose sample version $$\hat{\omega}_{\text{naive}} = \hat{\Sigma}^{-1}
\hat{\mu}$$ overfits in high dimension. AP Pruning instead selects a sparse set of
tree nodes that span the SDF, with robust moments. Definition 1 (p. 2466), step
one, estimates robust SDF weights on the training data:

$$
\min_{\omega} \; \tfrac{1}{2} \left( \hat{\mu}^{\text{robust}} - \hat{\Sigma}^{\text{robust}} \omega \right)' \left(\hat{\Sigma}^{\text{robust}}\right)^{-1} \left( \hat{\mu}^{\text{robust}} - \hat{\Sigma}^{\text{robust}} \omega \right) + \lambda_1 \|\omega\|_1
$$

$$
\text{with} \quad \hat{\Sigma}^{\text{robust}} = \hat{\Sigma} + \lambda_2 I_N, \qquad \hat{\mu}^{\text{robust}} = \hat{\mu} + \lambda_0 \mathbf{1}
$$

where $$\|\omega\|_1 = \sum_i |w_i|$$, $$\mathbf{1}$$ is a vector of ones, and $$N$$ is the number
of assets. The tuning parameters $$(\lambda_0, \lambda_1, \lambda_2)$$ are chosen on
the validation block to maximize the robust-SDF Sharpe ratio, then performance
is evaluated only on the untouched test block.

Proposition 2 (p. 2468) shows AP Pruning is equivalent to a robust tangency
portfolio (Definition 2, equation 2):

$$
\min_{\omega} \; \tfrac{1}{2} \omega' \hat{\Sigma} \omega + \lambda_1 \|\omega\|_1 + \tfrac{1}{2} \lambda_2 \|\omega\|_2^2
$$

$$
\text{subject to} \quad \omega' \mathbf{1} = 1, \qquad \omega' \left( \hat{\mu} + r_f \mathbf{1} \right) \geq \mu_0 + r_f
$$

The mapping is exact: the LASSO term $$\lambda_1$$ induces sparsity (a small set of
AP Tree basis assets), the target return $$\mu_0$$ corresponds to shrinking the
mean toward its cross-sectional average, and the ridge term $$\lambda_2$$
corresponds to variance shrinkage of the covariance matrix. This generalizes the
robust SDF recovery of Kozak, Nagel, and Santosh (2020), which shrinks only the
covariance, by also shrinking the mean (Proposition 3). Proposition 4 gives a
robust-control reading: the shrinkage solves a minimax problem over joint
estimation uncertainty in means and variances.

## Empirical specifications

Estimation runs on monthly CRSP/Compustat data, January 1964 to December 2016,
split into training (first 20 years), validation (10 years), and out-of-sample
testing (last 23 years). Each headline result is the test-block value of one of
the following constructions, not an OLS regression with fixed effects:

- **Out-of-sample Sharpe ratio (R1, R6, R7, R8).** For a given cross-section,
  the SDF / tangency portfolio is estimated on training, tuned on validation
  (Definition 1-2), then its realized monthly SR is computed on the test block.
  AP Trees are compared against triple sorts, double sorts (25x9), deciles, and
  quintiles of the same characteristics.
- **SDF alpha (R2).** The candidate factor models FF3, FF5, XSF
  (cross-section-specific factors), and FF11 are confronted with each
  cross-section; the SDF alpha is the pricing error of the cross-section's
  implied SDF against the model, with $$t$$-statistics reported (Table I,
  p. 2482; Figure 6 Panel B). Spanning is assessed by whether one
  cross-section's SDF is priced by another's factors.
- **Cross-sectional fit, XS-R² (R3).** The share of cross-sectional variation in
  average managed-portfolio returns explained by the candidate model (Table I).
- **Channel decompositions (R4, R5).** Re-running the construction with
  interaction nodes removed (R4, Figure 8), with a variance-only split criterion
  (V-Trees, R5, Figure 9), and against ML return-prediction portfolios built
  from Gu, Kelly, and Xiu (2020) tools (random forest, neural nets; Figure 15),
  isolating the contribution of interactions and of the SDF-spanning objective.

Robustness reported in the paper: excluding microcaps or restricting to the top
600 stocks by market cap (Table III, p. 2490), and rolling-window time-varying
SDF weights (Figure C.6, p. 2502).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP monthly stock returns and market data | Portfolio returns, market cap, momentum, short-term reversal, idiosyncratic volatility | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat annual fundamentals | Book-to-market, investment, operating profitability, accruals, turnover, long-term reversal | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Kenneth French Data Library | 10 firm-specific characteristic definitions (Table A.I); Fama-French factor returns for benchmarking (FF3, FF5) | [Ken French library](/wiki/datasets/ken-french/) |
| One-month Treasury bill rate | Proxy for the risk-free rate | No page yet |

Sample: January 1964 to December 2016 (53 years, monthly). Training sample: first 20 years; validation: 10 years; testing (out-of-sample): last 23 years.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13477) if you are:
replicating (the Internet Appendix contains formal proofs and additional
robustness); building new cross-sections beyond the 10 characteristics
studied; evaluating whether a candidate factor model spans the SDF; or
extending AP Trees to other asset classes or conditional models. The
locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation
was extracted by an LLM on 2026-05-31 and is **not human-verified or
independently reproduced**. The CC BY 4.0 licence permits mirroring; the
verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Bryzgalova, Svetlana, Markus Pelger, and Jason Zhu.
> "Forest through the Trees: Building Cross-Sections of Stock Returns."
> *The Journal of Finance* 80, no. 5 (October 2025): 2447–2506.
> DOI: 10.1111/jofi.13477. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
