---
title: "Investor Factors: Betermier, Calvet, Knupfer & Kvaerner (2025)"
description: >-
  Distilled: pricing factors built from individual investor holdings (Norway
  1997-2017); a two-factor model of the market plus a combined age-wealth
  portfolio prices the cross section of Norwegian equities out-of-sample and
  absorbs established firm factors. J. Finance 2025, paywalled. Eight core
  results with source locators, datasets used, the model, and the method
  with defining equations.
sidebar:
  label: Betermier et al. 2025
  order: 1
tags: [paper-summary, asset-pricing, factors, household-finance, equities, portfolio-sort, panel-regression, peer-reviewed, unreplicated, data:titlon-ose, data:vps-norway, data:statistics-norway]
paper:
  authors: Sebastien Betermier, Laurent E. Calvet, Samuli Knupfer, Jens Soerlie Kvaerner
  authorList:
    - { family: Betermier, given: Sebastien, affiliation: Desautels School of Management, McGill University }
    - { family: Calvet, given: Laurent E., affiliation: SKEMA Business School, University Cote d'Azur, and CEPR }
    - { family: Knupfer, given: Samuli, affiliation: Aalto University School of Business, BI Norwegian Business School, and Research Institute of Industrial Economics (IFN) }
    - { family: Kvaerner, given: Jens Soerlie, affiliation: BI Norwegian Business School and Tilburg University }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2789–2830
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13474
  license: 'Paywalled; Crossref DOI metadata returns only the Wiley terms-and-conditions VOR licence (content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0, start 2025-08-07). No Creative Commons licence found. Copyright 2025 the American Finance Association.'
  licenseShort: paywalled
  access: paywalled
  machineAccess: 'blocked-paywall (Wiley/AFA site; checked via Crossref metadata 2026-05-31)'
  redistribution: extract-only
  dataAccess: proprietary-confidential
  outcome:
    - cross-sectional stock returns (Norwegian equities)
    - investor portfolio tilts toward the age-wealth factor
  outcomeClass: [security-returns, household-finance]
  resultsCount: 8
  citedByCount: 0
  jel:
    codes: [G12, G11, G51]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Corporate Finance and Governance']
  methods:
    role: both
    contributes: investor-pricing-factors
    family: descriptive
    buildsFrom: [sdf-projection, portfolio-sort]
    identification: descriptive
  contributionType: [new-method, new-fact]
  mechanisms: [behavioral-bias, risk-sharing]
  scope:
    region: Norway
    assetClass: Norwegian equities (OSE)
    period: 1997-02..2017-12
    frequency: monthly
    dataType: [market, accounting, administrative]
    granularity: [individual, security]
    n: "308,000 investors/month on average; 535 stocks; 251 months"
  findings:
    - { ref: R1, outcome: cross-sectional stock returns (Norwegian equities), metric: r-squared, value: "PC1+PC2: 80% of variance; market R2=0.62 on PC1, AW R2=0.55 on PC2", direction: positive }
    - { ref: R2, outcome: cross-sectional stock returns (Norwegian equities), metric: alpha, value: "0.32%/month (3.8%/yr), t=3.16", direction: positive, vsBenchmark: "vs. CAPM (market-only)" }
    - { ref: R3, outcome: cross-sectional stock returns (Norwegian equities), metric: alpha, value: "0.24%/month, t=2.55", direction: positive, vsBenchmark: "survives all five FF factors" }
    - { ref: R4, outcome: cross-sectional stock returns (Norwegian equities), metric: alpha, value: "MOM alpha reduced from 0.77% to 0.43% (t=1.04); RMW from 0.73% to 0.46% (t=1.42); CMA from 0.52% to 0.32% (t=0.99)", direction: none, vsBenchmark: "firm-factor alphas under IPF* vs. CAPM" }
    - { ref: R5, outcome: investor portfolio tilts toward the age-wealth factor, metric: sharpe-ratio, value: "IPF* OOS SR=0.45; best firm model (FIRM-6)=0.40; market=0.31", direction: positive, vsBenchmark: "beats all firm-factor models (0.19-0.40 range) and market (0.31)" }
    - { ref: R6, outcome: investor portfolio tilts toward the age-wealth factor, metric: coefficient, value: "tilt range [-0.3, +0.1] over life cycle; ~1.2%/yr average return difference", direction: positive }
    - { ref: R7, outcome: investor portfolio tilts toward the age-wealth factor, metric: coefficient, value: "income beta -0.051 (t=-6.40); debt -0.047 (t=-5.55); finance occupation +0.627 (t=34.60); stock mkt experience +0.026 (t=7.58); male dummy -0.156 (t=-15.00)", direction: mixed }
    - { ref: R8, outcome: cross-sectional stock returns (Norwegian equities), metric: beta, value: "long-leg CAPM beta 0.73 vs. short-leg 1.02; long-leg volatility 0.08 vs. short-leg 0.18; long-leg mkt cap 973M NOK vs. 483M NOK", direction: mixed, vsBenchmark: "long leg vs. short leg of AW portfolio" }
  resultType: new-finding
  relatesTo:
    - { cite: 'Merton (1973)', doi: '10.2307/1913811', relation: builds-on, note: 'ICAPM framework grounds the theoretical spanning condition; investor deviation portfolios map to hedging demands (pp. 2802-2803)' }
    - { cite: 'Balasubramaniam, Campbell, Ramadorai & Ranish (2023)', doi: '10.1111/jofi.13220', relation: builds-on, note: 'strong factor structure in individual investor portfolios motivates the PCA grouping approach (p. 2792)' }
    - { cite: 'Kozak, Nagel & Santosh (2020)', doi: '10.1016/j.jfineco.2019.06.008', relation: builds-on, note: 'covariance shrinkage in bootstrap Sharpe ratio estimation (eq. 24, p. 2815)' }
    - { cite: 'Fama & French (2018)', doi: '10.1016/j.jfineco.2018.02.012', relation: builds-on, note: 'bootstrap out-of-sample Sharpe ratio evaluation methodology (p. 2815)' }
    - { cite: 'Betermier, Calvet & Sodini (2017)', relation: extends, note: 'extends life-cycle links between demographics and value-factor tilts from Swedish households to a full IPF extraction framework (p. 2821)' }
    - { cite: 'Koijen & Yogo (2019)', relation: tests, note: 'IPF* also prices the institutional investor portfolio held on the OSE (Internet Appendix Table IA.VIII; p. 2826)' }
  openQuestions:
    - 'The methodology is presented as general but tested only on Norwegian equities; extension to other asset classes (private equity, bonds) and other countries where holdings data exist is left for future research (p. 2827).'
    - 'Whether interdependencies between the hedging and sentiment channels driving investor tilts can be separately identified, as Kozak, Nagel, and Santosh (2018) suggest they may interact (p. 2827).'
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full PDF read (pp. 2789-2830, 42 pages). All results extracted from the PDF with table/figure/page locators. Not human-verified. Not reproduced. Replication code is listed as Supporting Information at the publisher site but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-01
      role: extracted
      note: Augment pass. Added methods, scope, relatesTo, openQuestions, replicationCode, proposedVocab frontmatter blocks. Replaced the old Theory tested section with three formal body sections (Theory / model, Method, Empirical specifications) with equations transcribed from pp. 2795-2822 of the source PDF read this session. Core results table and all verified locators are unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-01
      role: verified
      note: 'Locators and reported magnitudes re-checked against source PDF (all 42 pages read); all 8 Core results rows confirmed. Two fixes applied: (1) gamma formula in eq. 24 corrected (removed spurious 0.5 coefficient; PDF footnote 26 gives gamma = tr(Sigma_p) / [T(E[SR])^2] with E[SR] = 0.5 as the selected value); (2) wealth portfolio locator changed from "(eq. 21, p. 2808)" to "(text, p. 2808)" (eq. 21 is the AW combination formula, not the wealth portfolio definition).'
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
        applied - removed demand-elasticity from mechanisms (paper invokes
        hedging/risk-sharing and sentiment/behavioral-bias channels only, not
        inelastic-demand-based asset pricing).
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
        against the source PDF; one fix applied - R8 direction corrected from
        positive to mixed (Table VIII reports multiple stock characteristics that
        go in opposite directions between long and short legs: long leg has higher
        mkt cap, BtM, profitability but lower CAPM beta and volatility than short
        leg); all other seven findings[] values and directions confirmed against
        their PDF tables; resultType new-finding retained as defensible given the
        IPF methodology is genuinely first-of-its-kind.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13474
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[0].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-07. No CC licence present. Copyright: 2025 the American Finance Association.'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, datasets, and theory: enough to
know what it found without reading all 42 pages. For replication or extension,
read the full source at the [original](https://doi.org/10.1111/jofi.13474)
(paywall).

## TL;DR

Using complete administrative stockholdings of Norwegian individual investors
(308,000 investors/month, Feb 1997 to Dec 2017, 535 OSE stocks), the paper
derives theoretical conditions under which investor portfolio holdings reveal
pricing factors for the cross section of equity returns. It then constructs
Investor Pricing Factors (IPFs) by sorting investors into 90 groups by age,
wealth, and other characteristics. A two-factor model consisting of the market
(MKT) and a combined age-wealth portfolio (AW) prices both Norwegian equities
and established firm-based factors, while IPFs outperform firm-factor models
out-of-sample. Portfolio tilts toward the age-wealth factor are positively
linked to financial sophistication and negatively linked to debt and
macroeconomic income risk, consistent with joint hedging and sentiment
channels.

## Core results

Magnitudes and significance are as reported; `**`/`***` = 5%/1%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Two PCs explain 80% of cross-sectional variation** in group portfolio holdings; PC1 tracks the market (R2 = 0.62), PC2 tracks the combined age-wealth portfolio (R2 = 0.55) | Table I, p. 2807 | PC1 alone: 72% of variance; PC1+PC2: 80%; market R2=0.62 on PC1, AW R2=0.55 on PC2 |
| R2 | The combined age-wealth factor (AW) earns a **significant CAPM alpha** of 32 bps/month (3.8%/yr) after controlling for the market | Table II col. (2), p. 2810 | alpha = 0.32%, t = 3.16; CAPM beta on AW = -0.12, t = -6.96 |
| R3 | AW **spans firm factors**: its alpha remains 24 bps/month (sig. 5%) even after controlling for all five FF factors (size, value, momentum, profitability, investment) | Table III col. (5), p. 2813 | alpha = 0.24, t = 2.55; adj. R2 rises from 0.16 to 0.29 but AW alpha never insignificant |
| R4 | IPF\* **prices established firm factors**: adding AW to the market renders momentum, profitability, and investment alphas statistically insignificant and reduces them by ~40% | Table IV, p. 2814 | MOM alpha: 0.77% (CAPM) vs. 0.43% (IPF\*); RMW: 0.73% vs. 0.46%; CMA: 0.52% vs. 0.32%; all three IPF\* alphas statistically insignificant (MOM t=1.04, RMW t=1.42, CMA t=0.99) |
| R5 | **Out-of-sample Sharpe ratio** of IPF\* (0.45) exceeds all firm-factor models (0.19-0.40 range) and is 45% above the market (0.31) | Table V, p. 2817 | IPF\* OOS SR = 0.45; 3-factor age+wealth model = 0.51; best firm model (FIRM-6) = 0.40; market = 0.31; OS/IS ratio for IPF\* = 0.67 vs. 0.43 for all-firm model |
| R6 | Factor tilts **increase monotonically with age and wealth**: tilt rises from -0.3 (investors under 30) to +0.1 (70-75), equivalent to ~1.2%/yr average return difference | Figure 2 + p. 2821 | Tilt range [-0.3, +0.1] over life cycle; 0.4 x 3% = 1.2%/yr gap; holds for new entrants mimicking experienced investors within cohort |
| R7 | **Debt and income beta reduce tilts** (hedging channel) while finance occupation, stock market experience, and female gender raise tilts (sophistication/sentiment channel) | Table VII, p. 2823 | Income beta coef = -0.051 (t = -6.40); debt = -0.047 (t = -5.55); finance occup. = 0.627 (t = 34.60); stock mkt. experience = 0.026 (t = 7.58); male dummy = -0.156 (t = -15.00) |
| R8 | Stocks in the **long leg of AW have higher market cap, book-to-market, and profitability** than short-leg stocks; short-leg stocks have higher CAPM beta (1.02 vs. 0.73), volatility (0.18 vs. 0.08), and turnover | Table VIII, p. 2825 | Long-leg median mkt cap 973M NOK vs. 483M NOK; BtM 0.90 vs. 0.66; profitability 0.06 vs. 0.05; CAPM beta 0.73 vs. 1.02; volatility 0.08 vs. 0.18 |

**Overall (paper's conclusion).** Individual investor portfolios contain
recoverable pricing information. The market and the combined age-wealth
portfolio (long mature/wealthy, short young/less-wealthy investors) form a
parsimonious two-factor model that prices the Norwegian cross section, absorbs
firm factors, and outperforms firm-factor models out-of-sample. Hedging and
sentiment jointly drive investor tilts toward the pricing factor.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Titlon (Oslo Stock Exchange database) | Stock prices, returns, shares outstanding for 535 OSE stocks, 1997-2017 | [Titlon (OSE)](/wiki/licensed/titlon-ose/) (licensed) |
| VPS (Norwegian Central Securities Depository) | Complete individual investor stockholdings at monthly frequency, 300,000+ investors | no page yet |
| Statistics Norway (Statistisk sentralbyra) | Investor demographics, balance sheets, income, wealth from tax records; annual 1997-2017 | no page yet |
| OSE market index (Norwegian market portfolio) | Benchmark factor; market-cap-weighted portfolio of OSE stocks | no page yet |

Sample: 308,000 individual investors per month on average; 535 unique stocks; 251 months (Feb 1997 to Dec 2017).

## Theory / model

The paper's central theoretical object is the tangency portfolio, which prices
the cross section of excess stock returns. For J stocks with excess return
vector $$R^e$$, expected return vector $$\mu$$, and variance-covariance matrix
$$\Sigma$$, the tangency portfolio has weights (eq. 1, p. 2795):

$$
\tau = \frac{1}{\phi} \Sigma^{-1} (\mu - R_f \mathbf{1}), \qquad \phi = \mathbf{1}' \Sigma^{-1} (\mu - R_f \mathbf{1}) > 0
$$

Every stock's risk premium satisfies $$\mu_j - R_f = \phi \, (\Sigma \tau)_j = b_{j,\tau} (\mu_\tau - R_f)$$, so pricing the tangency portfolio is equivalent to
pricing all stocks (eq. 2, p. 2795).

**Spanning condition.** The key insight is that the researcher can recover the
tangency portfolio from investor portfolio holdings when Assumption 1 holds
(p. 2796): there exist N long-short investor portfolios $$\pi^1, \ldots, \pi^N$$
extracted from the sample such that

$$
\tau \in \operatorname{Span}[ m, \pi^1, \ldots, \pi^N ],
$$

where $$m$$ is the market portfolio and $$\operatorname{Span}[\cdot]$$ denotes the set of all linear
combinations. When this holds, the tangency portfolio is a linear combination
(eq. 4, p. 2796):

$$
\tau = m + \sum_{n=1}^{N} \eta_n \, \pi^n,
$$

and every stock's risk premium satisfies a multifactor pricing equation
(Proposition 1, eq. 6, p. 2797):

$$
\mu_j - R_f = \beta_{j,M} (\mu_M - R_f) + \sum_{n=1}^{N} \beta_{j,n} \, E(p_n),
$$

where $$p_n = (\pi^n)' R^e$$ is the return on the n-th IPF and
$$(\beta_{j,M}, \beta_{j,1}, \ldots, \beta_{j,N})'$$ is the vector of OLS regression
coefficients of stock j's return on the (N+1) factors.

Proposition 1 also implies that a stock's CAPM alpha satisfies (eq. 7, p. 2798):

$$
a_{j,M} = \phi \sum_{n=1}^{K} \eta_n (b_{j,n} - b_{j,M} \, b_{M,n}) \sigma_n^2,
$$

where $$b_{j,n} = \operatorname{cov}(R^e_j, p_n) / \sigma_n^2$$ and $$b_{M,n} = \operatorname{cov}(\text{MKT}, p_n) / \sigma_n^2$$.
Stocks in low demand (positive net exposure $$b_{j,n} - b_{j,M} \, b_{M,n}$$ with
$$\eta_n > 0$$) are underpriced relative to CAPM and tend to have low market betas.

**Theoretical foundations for age and wealth as IPF characteristics.** The paper
derives the spanning condition under two complementary models (Section I.D,
pp. 2802-2804):

1. ICAPM (Merton 1973, Breeden 1979) with heterogeneous investors: each investor
   i has CRRA utility and holds a portfolio deviating from the tangency by
   hedging demands. Under a Taylor approximation, the portfolio factor structure is
   (eq. 17, p. 2803):

   $$
   \omega^i_t = \tau_t - (T - 1 - A^i_t) \, d^1_t - (L^i_t / W^i_t) \, d^2_t,
   $$

   where $$A^i_t$$ is investor age, $$L^i_t / W^i_t$$ is the income-to-wealth ratio,
   and $$d^1_t, d^2_t$$ are deviation portfolios. Mature and wealthy investors hold
   portfolios closer to $$\tau$$ and therefore earn higher CAPM alphas.

2. Sentiment model (Fedyk, Heyerdahl-Larsen, and Walden 2013): sentiment covaries
   with age and wealth, yielding a reduced-form factor structure (eq. 18, p. 2804):

   $$
   \omega^i_t = \tau_t - f_1(A^i_t) \, d^1_t - f_2(W^i_t) \, d^2_t.
   $$

   Both frameworks predict age and wealth as natural IPF sorting characteristics.

## Method

The construction has two parts: grouping investors into a factor structure and
extracting priced long-short portfolios. It builds on `sdf-projection` (the
tangency-spanning condition) and `portfolio-sort` (investor sorting by
socioeconomic characteristics).

**Step 1: Factor structure of investor portfolios.** The strong factor structure
in individual investor portfolios documented by Balasubramaniam, Campbell,
Ramadorai, and Ranish (2023) motivates the PCA grouping approach. $$G = 90$$ investor groups are
formed annually by age (12 groups), wealth (12 groups), permanent real income
(12 groups), gender (2), education (3), region (9), industry (17), and
occupation (9). For group g with investor equity-wealth weights $$w^g_i$$, the
group portfolio is (eq. 14, p. 2801):

$$
\omega^g = \sum_{i \in I_g} w^g_i \, \omega^i, \qquad w^g_i = E^i \Big/ \sum_{i' \in I_g} E^{i'}.
$$

PCA is applied to the $$G \times G$$ variance-covariance matrix of the $$G = 90$$ group
portfolio holdings, $$\Omega'_t \Omega_t / J_t$$, to obtain principal components
$$PC_{k,t}$$ (eq. 19-20, p. 2806). The first two PCs explain 80% of the
cross-sectional variance in group holdings.

**Step 2: Extracting IPFs as long-short portfolios.** An IPF is a zero-investment
long-short portfolio $$\pi^n$$ formed as a weighted average of group portfolios
(eq. 15, p. 2802):

$$
\pi^n = \sum_{g=1}^{G} z^g_n \, \omega^g, \qquad \sum_{g=1}^{G} z^g_n = 0.
$$

The age portfolio $$\pi_{\text{AGE},t}$$ is long investors aged 70-75 and short investors
aged 18-30 (equal weights -1/2 on groups 1 and 2). The wealth portfolio
$$\pi_{\text{WEALTH},t}$$ is long the top 1% wealthiest investors and short the bottom
10%-30% of wealth (text, p. 2808). The combined age-wealth portfolio is:

$$
\pi_{\text{AW},t} = \tfrac{1}{2} \left( \pi_{\text{AGE},t} + \pi_{\text{WEALTH},t} \right).
$$

Returns on the IPFs are computed as $$AW_t = (\pi_{\text{AW},t-1})' R^e_t$$ (net of the
1-month Norwegian Interbank Offered Rate, NIBOR, as risk-free rate; p. 2810).

**Out-of-sample Sharpe ratio evaluation.** The bootstrap procedure (eq. 24,
p. 2815) follows Fama and French (2018): 100,000 bootstrap draws of $$T = 251$$
months from the factor return panel are used. The in-sample covariance matrix is
shrunk as $$\hat{\Sigma}_p = \Sigma_p + \gamma I$$ ($$\gamma = \operatorname{tr}(\Sigma_p) / (T \, E[\text{SR}]^2)$$, with $$E[\text{SR}] = 0.5$$ selected) following Kozak, Nagel, and Santosh (2020), and the tangency portfolio
is $$\hat{\tau} = \hat{\Sigma}_p^{-1} \mu_p / (\mathbf{1}' \hat{\Sigma}_p^{-1} \mu_p)$$. Out-of-sample SR
is computed on the hold-out months not drawn in each simulation.

## Empirical specifications

**PC factor-structure regression (R1; Table I, p. 2807).** The stock weight in
PC k is regressed monthly on the market, age, and wealth portfolio weights (OLS,
eq. 22, p. 2809):

$$
PC_{j,k,t} = a^k_t + \lambda^k_{\text{MKT},t} \, m_{j,t} + \lambda^k_{\text{AGE},t} \, \pi_{\text{AGE},j,t} + \lambda^k_{\text{WEALTH},t} \, \pi_{\text{WEALTH},j,t} + \epsilon^k_{j,t}, \qquad j = 1,\ldots,J_t.
$$

Time-average $$R^2$$ reported over 2005-2017. Identifies PC1 with market ($$R^2 = 0.62$$)
and PC2 with combined age-wealth factor ($$R^2 = 0.55$$).

**IPF alpha and beta regressions (R2, R3; Tables II-III, pp. 2810-2813).** Monthly
OLS spanning regressions of IPF returns on the market and/or firm factors,
February 1997 to December 2017 (T = 251):

$$
AW_t = \alpha + \beta_{\text{MKT}} \, \text{MKT}_t + [\beta_{\text{SMB}} \, \text{SMB}_t + \beta_{\text{HML}} \, \text{HML}_t + \beta_{\text{MOM}} \, \text{MOM}_t + \beta_{\text{RMW}} \, \text{RMW}_t + \beta_{\text{CMA}} \, \text{CMA}_t] + v_t.
$$

Five Fama-French firm factors (SMB, HML, RMW, CMA) and momentum (MOM) are
constructed from Norwegian equities using standard accounting and price data
(Internet Appendix Section III.B). Newey-West standard errors are not mentioned;
heteroskedasticity-robust t-statistics are reported.

**Firm-factor alpha regressions under IPF* (R4; Table IV, p. 2814).** Each firm
factor $$F_t \in \{\text{SMB}, \text{HML}, \text{MOM}, \text{RMW}, \text{CMA}\}$$ is regressed on the market and AW:

$$
F_t = \alpha_F + \beta_{F,\text{MKT}} \, \text{MKT}_t + \beta_{F,\text{AW}} \, AW_t + v_t.
$$

AW absorbs ~40% of momentum, profitability, and investment alphas, rendering
them statistically insignificant at the 5% level (MOM t = 1.04, RMW t = 1.42,
CMA t = 0.99; Table IV columns 2, 6, 8, 10).

**IPF* stock-level multifactor model (eq. 23, p. 2811).** The preferred two-factor
model (labelled IPF*) for each stock j:

$$
R^e_{j,t} = \alpha_j + \beta_{j,\text{MKT}} \, \text{MKT}_t + \beta_{j,\text{AW}} \, AW_t + v_{j,t},
$$

where $$\alpha_j = 0$$ for all j if IPF* is correctly specified.

**Portfolio tilt regression (R6, R7; Table VII, p. 2823).** This extends the
life-cycle links between demographics and value-factor tilts that Betermier,
Calvet, and Sodini (2017) documented for Swedish households into a full IPF
extraction framework. The panel regression of
investor i's tilt toward IPF AW is run at annual frequency, 2004-2017 (N = 911,432
investor-years):

$$
\text{TILT}^i_{\text{AW},t} = \delta_t + \theta' \chi^i_t + \xi^i,
$$

- $$\text{TILT}^i_{\text{AW},t} = \sum_{j=1}^{J_i} \omega^i_{j,t} \, D_{j,\text{AW},t}$$ with $$D_{j,\text{AW},t} = +1 / -1$$ if stock j is in the long / short leg of AW (eq. 25, p. 2819).
- $$\chi^i_t$$ is a vector of investor characteristics (income beta, debt indicator, stock market experience, finance occupation, gender, Oslo residence, top management dummy).
- $$\delta_t$$ are year fixed effects with additional age-group and wealth-group fixed effects.
- Standard errors clustered by calendar year x investor level.

## When to read the full paper

Read the full source if you are: constructing IPFs for other markets or asset
classes; extending the spanning-condition theory to institutional holdings;
using the bootstrap out-of-sample Sharpe methodology (Section III.C) for
factor evaluation; auditing specific coefficients in Tables III-VIII; or
reviewing the Internet Appendix robustness tests (alternative age/wealth
cutoffs, institutional portfolio pricing), where IPF* also prices the
institutional investor portfolio held on the OSE, the pricing question
studied by Koijen and Yogo (2019). The locators above point to the
exact tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5), October 2025.
Copyright 2025 the American Finance Association. This distillation was
extracted by an LLM on 2026-05-31 and is **not human-verified or independently
reproduced**. The paper is paywalled; only extracts are reproduced here under
fair use for scholarly commentary.

> Betermier, Sebastien, Laurent E. Calvet, Samuli Knupfer, and Jens Soerlie
> Kvaerner. "Investor Factors." *The Journal of Finance* 80, no. 5 (October
> 2025): 2789-2830. DOI: 10.1111/jofi.13474. Copyright 2025 the American
> Finance Association. All rights reserved. This page contains an
> extract-only distillation by the Institute for Automated Research; the
> verbatim article is available at the publisher site.
