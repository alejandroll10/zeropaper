---
title: "Segmented Arbitrage: Siriwardane, Sunderam & Wallen (2025)"
description: >-
  Distilled: across 32 arbitrage spreads in equity, fixed income, and foreign
  exchange markets (2010-2020), the average pairwise correlation is only 22%,
  far below what canonical intermediary asset pricing models predict. The paper
  attributes this to two distinct forms of segmentation: funding segmentation
  (certain trades rely on specific unsecured vs. secured funding sources) and
  balance-sheet segmentation (intermediaries specialize in certain trades, so
  idiosyncratic balance-sheet shocks move specific spreads). J. Finance 2025,
  paywalled. Nine core results with source locators, datasets used, and the
  theory tested.
sidebar:
  label: Siriwardane-Sunderam-Wallen 2025
  order: 1
tags: [paper-summary, asset-pricing, arbitrage, limits-to-arbitrage, intermediary-asset-pricing, fixed-income, foreign-exchange, equities, panel-regression, event-study, svar, peer-reviewed, unreplicated, data:bloomberg, data:cftc-cot, data:markit-cds, data:crane-mmf, data:preqin, data:gsw-yields, data:cboe-options, data:wrds]
paper:
  authors: Emil N. Siriwardane, Adi Sunderam, Jonathan Wallen
  authorList:
    - { family: Siriwardane, given: "Emil N.", affiliation: "Harvard University and NBER" }
    - { family: Sunderam, given: Adi, affiliation: "Harvard University and NBER" }
    - { family: Wallen, given: Jonathan, affiliation: "Harvard University" }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2543–2590
  venueShort: J. Finance 2025
  licenseShort: paywalled
  resultsCount: 9
  citedByCount: 4
  jel:
    codes: [G12, G14, G23]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Banking stability, regulation, efficiency', 'Economic theories and models']
  dataAccess: licensed-commercial
  outcome:
    - arbitrage spread levels
    - pairwise correlation of arbitrage spreads
    - differential sensitivity of unsecured vs. secured spreads to funding shocks
  outcomeClass: [asset-prices]
  doi: 10.1111/jofi.13469
  license: 'Wiley VOR terms (confirmed via Crossref DOI metadata: content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0, start 2025-08-04); artifact p.2543 states © 2025 the American Finance Association; no Creative Commons licence found'
  access: paywalled
  machineAccess: 'blocked-paywall (Wiley/Journal of Finance site; checked 2026-05-31)'
  redistribution: 'extract-only; paywalled Wiley VOR licence does not permit mirroring'
  methods:
    role: both
    contributes: segmented-arbitrage
    family: reduced-form-causal
    buildsFrom: [sign-restricted-svar, panel-regression, difference-in-differences, instrumental-variables]
    identification: natural-experiment
  contributionType: [new-fact, new-theory]
  mechanisms: [limits-to-arbitrage, intermediary-constraint, liquidity]
  scope:
    region: US
    assetClass: equity futures, fixed income, foreign exchange (32 arbitrage spreads)
    period: 2010-01..2020-02
    frequency: mixed
    dataType: [market, accounting]
    granularity: [security, aggregate]
    n: "32 arbitrage spreads, daily 2010-2020; 496 pairwise spread combinations"
  findings:
    - { ref: R1, outcome: pairwise correlation of arbitrage spreads, metric: correlation, value: "mean rho = 0.22, SD = 0.30; 90% of pairs reject H0: rho > 0.67", direction: negative, vsBenchmark: "below single-factor integrated-intermediary model prediction (perfect correlation)" }
    - { ref: R2, outcome: pairwise correlation of arbitrage spreads, metric: correlation, value: "short-tenor mean rho = 0.19; 10 PCs needed to explain 90% of variation", direction: negative, vsBenchmark: "below single-factor model prediction; persists within same-tenor trades" }
    - { ref: R3, outcome: pairwise correlation of arbitrage spreads, metric: correlation, value: "average rho of supply shocks = 16%; 1% upper bound on quarterly supply-shock correlations = 37%", direction: negative, vsBenchmark: "below integrated-intermediary model; supply shocks weakly correlated across trades" }
    - { ref: R4, outcome: differential sensitivity of unsecured vs. secured spreads to funding shocks, metric: coefficient, value: "unsecured beta(TED) = 0.49 (t=4.58); secured beta(TED) = 0.07 (t=1.33, insig.); approx 7x more sensitive", direction: positive, vsBenchmark: "unsecured spreads load strongly on TED; secured spreads do not" }
    - { ref: R5, outcome: arbitrage spread levels, metric: basis-points, value: "beta = 11.77 (t=2.47); dynamic estimate at reform month (j=0) is 18.03 bps, rising to peak of 20.70 bps at j=2 (two months after reform)", direction: positive, vsBenchmark: "unsecured spreads rise following 2016 MMF reform; secured spreads unaffected" }
    - { ref: R6, outcome: arbitrage spread levels, metric: coefficient, value: "OLS coef = -0.55 (t=-3.86); IV coef = -1.09 (t=-2.25) for equity SF", direction: negative, vsBenchmark: "Fidelity IPrime MMF outflows widen equity SF spreads; no effect on secured spreads" }
    - { ref: R9, outcome: arbitrage spread levels, metric: coefficient, value: "secured beta = -0.66 (t=-3.04); unsecured beta = 0.00 (t=0.01)", direction: negative, vsBenchmark: "FI hedge fund losses predict higher secured spreads; no effect on unsecured spreads" }
  resultType: overturns
  relatesTo:
    - { cite: 'He & Krishnamurthy (2013)', doi: '10.1257/aer.103.2.732', relation: contradicts, note: 'canonical single-constraint intermediary model predicts perfect spread correlation; data show mean pairwise rho = 0.22 (Table II, p. 2560)' }
    - { cite: 'Garleanu & Pedersen (2011)', doi: '10.1093/rfs/hhr027', relation: contradicts, note: 'margin-based asset pricing with integrated funding implies one- or two-factor spread structure; rejected by high-dimensional factor structure (Figure 3, p. 2562)' }
    - { cite: 'Du, Tepper & Verdelhan (2018)', doi: '10.1111/jofi.12620', relation: builds-on, note: 'CIP spread construction and FX arbitrage measurement methodology (p. 2554)' }
    - { cite: 'Uhlig (2005)', doi: '10.1016/j.jmoneco.2004.05.007', relation: builds-on, note: 'sign-restricted SVAR used to separate supply from demand shocks (pp. 2564-2566)' }
    - { cite: 'Anderson, Du & Schlusche (2019)', relation: builds-on, note: '2016 MMF reform event study design (pp. 2570-2573)' }
    - { cite: 'Siriwardane (2019)', doi: '10.1111/jofi.12777', relation: builds-on, note: 'intermediary specialization in credit derivatives (p. 2547)' }
  openQuestions:
    - 'How long segmentation persists: the paper shows quarterly supply-shock correlations have a 1% upper bound of 37%, indicating relatively slow but nonzero capital flows across segments (pp. 2587-2588).'
    - 'Whether segmentation is more pronounced in risky-asset markets where agency problems are more severe; the paper notes its arbitrages are relatively straightforward to execute (p. 2588).'
    - 'What determines the boundaries of the firm for financial intermediaries: why certain trades are grouped together in a market segment (p. 2588).'
  replicationCode:
    status: available
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13469
      checked: 2026-05-31
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[0].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-04; no CC licence present'
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-05-31
      role: extracted
      note: Full text read (pp. 2543–2590 of the PDF on disk); all results extracted from the PDF with table/figure/page locators. Not human-verified. Not reproduced. Replication code is published as Supporting Information but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-05-31
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; verdict pass.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-01
      role: extracted
      note: 'Augment pass. Added methods, scope, relatesTo, openQuestions, replicationCode, proposedVocab frontmatter blocks, and three formal body sections (Theory / model, Method, Empirical specifications) with equations transcribed from pp. 2548-2553 and 2564-2586 of the source PDF read this session. Core results table and prior extraction/verification entries are unchanged. New formal sections are extracted, not yet re-verified.'
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-01
      role: verified
      note: 'All 9 core result rows re-checked against the source PDF (Tables II–VII, Figures 3–8); all locators and magnitudes confirmed correct. Equations 1–13 verified term-by-term: subscripts, signs, summation limits, and matrix entries all match the PDF. No errors found; no edits required.'
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
        introducesData, data-scope) re-checked against the source PDF; all axes
        confirmed correct -- natural-experiment identification via 2016 MMF reform
        DiD is the primary design, new-fact and new-theory contribution types match,
        mechanisms (limits-to-arbitrage, intermediary-constraint, liquidity/funding)
        are all invoked, introducesData correctly absent, and scope fields faithful
        to the 32-spread daily 2010-2020 sample; no edits required.
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
        against the source PDF; R5 value corrected -- "peaks at 18.03 bps at
        reform month" replaced with the accurate dynamic profile (18.03 at j=0,
        peak 20.70 at j=2 per Table IV col.2 p.2573); all other entries
        (R1-R4, R6, R9) confirmed correct; resultType=overturns consistent with
        contradicts edges to He & Krishnamurthy (2013) and Garleanu & Pedersen
        (2011).
  rightsSignalConflict: false
---

**What this is.** The paper's core results, datasets, and theory: enough to
know what it found without reading all 48 pages. To replicate or extend it,
obtain the full source via the
[DOI](https://doi.org/10.1111/jofi.13469) (paywalled).

## TL;DR

Using daily data on 32 no-arbitrage spreads across equity, fixed income, and
foreign exchange markets over January 2010 to February 2020, the paper
documents that the average pairwise correlation of arbitrage spreads is only
0.22, far below what integrated-intermediary models predict. The paper argues
this reflects two types of segmentation: (i) funding segmentation, where
certain trades (equity spot-futures, equity options box, CIP) rely on
unsecured funding while others rely on secured (repo) funding, so that shocks
to unsecured funding markets raise unsecured spreads but not secured ones; and
(ii) balance-sheet segmentation, where intermediaries specialize in certain
trades, so idiosyncratic balance-sheet shocks (JPMorgan London Whale 2012,
Deutsche Bank CDS exit 2014) move specific arbitrage spreads but not others.
A sign-restricted SVAR shows the high-dimensional factor structure of spreads
is driven largely by weakly correlated supply shocks on the arbitrageur side.

## Core results

Magnitudes and significance are as reported; `*`/`**` = 10%/5%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Average pairwise correlation of arbitrage spreads is 22%**, far below the single-factor benchmark | Table II Panel A, p. 2560 | Mean ρ = 0.22, SD = 0.30; 75th pctile = 0.42; 90% of pairs reject H₀: ρ > 0.67 (p = 0.00); N = 496 pairs |
| R2 | **Low correlations persist even within same-tenor trades**, ruling out measurement error and noise-trader risk | Table II Panels B–D, pp. 2560–2561; Figure 3, p. 2562 | Short-tenor mean ρ = 0.19; after 1-month moving average, 10 PCs needed to explain 90% of variation; overnight IOER–GCF pair ρ = 23% |
| R3 | **Supply shocks from sign-restricted SVAR are weakly correlated** (avg 16% pairwise), not demand shocks | Figure 4, p. 2567 | Average ρ of supply shocks across all futures-based trades = 16%; average ρ of demand shocks also 16%; supply shocks within equity SF cluster higher at 62%; 1% upper bound on quarterly supply-shock correlations = 37% |
| R4 | **Unsecured arbitrages load strongly on TED spread; secured arbitrages do not** | Table III, p. 2569 | Unsecured β(TED) = 0.49\*\* (t = 4.58); secured β(TED) = 0.07 (t = 1.33, insignificant); unsecured spreads approximately 7× more sensitive to TED than secured |
| R5 | **2016 MMF reform raised unsecured arbitrage spreads by ~12 bps; secured spreads unaffected** | Table IV col. (1), p. 2573; Figure 5, p. 2571 | β = 11.77\*\* (t = 2.47); dynamic estimates show initial spike of 18.03\*\* at reform month, elevated for 3+ months; pass-through ≈ 0.59, matching OLS TED coefficient |
| R6 | **Fidelity IPrime MMF outflows specifically move equity spot-futures spreads but not other unsecured or secured spreads** | Table V, p. 2575 | OLS: Fidelity flows coef = −0.55\*\* (t = −3.86) for equity SF; IV estimate = −1.09\*\* (t = −2.25); CIP/Box coef = −0.14\* (t = −1.84, significant at 10% only); secured coef = 0.01 (insignificant) |
| R7 | **JPMorgan London Whale balance-sheet shock raised equity spot-futures spreads relative to other unsecured spreads** | Figure 7C, p. 2582 | Equity SF spreads significantly higher vs. other unsecured arbitrages following March 1, 2012 and June 13, 2012; widening persisted for several months; JPM CP rates unchanged, ruling out funding channel |
| R8 | **Deutsche Bank's 2014 CDS market exit raised CDS-bond arbitrage spreads relative to other secured spreads** | Figure 8B, p. 2584 | Effect significant at 5%; relative widening persisted over 5 months; other secured and unsecured arbitrage spreads unaffected |
| R9 | **Fixed-income hedge fund losses predict future increases in secured (not unsecured) arbitrage spreads** | Table VII, p. 2586 | Secured β(FI Arb HF Return\_{t-1}) = −0.66\*\* (t = −3.04); unsecured β = 0.00 (t = 0.01); driven by Treasury-swap and CDS-bond sub-strategies |

**Overall (paper's conclusion).** Riskless arbitrage is segmented. Both
funding segmentation (unsecured vs. secured funding markets) and balance-sheet
segmentation (intermediary specialization) drive low correlations across
arbitrage spreads. The evidence implies that intermediary asset pricing models
most naturally describe individual market segments rather than capital markets
as a whole.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Bloomberg (spot rates, FX forwards, OIS rates, futures prices, Treasury yields, inflation swaps, CDS via Markit) | Construction of all 32 arbitrage spreads; FX CIP, equity spot-futures, Treasury spot-futures, Treasury-swap, TIPS-Treasury series | [Bloomberg](/wiki/licensed/bloomberg/) (licensed) |
| van Binsbergen, Diamond & Grotteria (2019) box rates extended by authors using CBOE SPX options data | Equity options (box arbitrage) spreads at 6-, 12-, 18-month tenors | No page yet |
| Markit (cash bond and CDS pricing) | CDS-bond basis construction for IG and HY bonds | [Markit bond pricing](/wiki/licensed/markit/) / [Markit CDS](/wiki/licensed/markit-cds/) (licensed) |
| CFTC Commitments of Traders (Traders in Financial Futures, weekly) | Quantities data on positions by dealer, hedge fund, and asset-manager type for futures-based trades | [CFTC COT](/wiki/datasets/cftc-cot/) |
| Crane data / SEC Form N-MFP | MMF total net assets and holdings, for MMF reform analysis | [Crane Data](/wiki/licensed/crane-mmf/) (licensed) |
| Preqin Pro Hedge Fund Database | Hedge fund returns data; fixed-income arbitrage strategy flag | [Preqin](/wiki/licensed/preqin/) (licensed) |
| Federal Reserve yield curve models (Gurkaynak, Sack, Wright 2007/2010) | Zero-coupon constant-maturity Treasury and TIPS yields for TIPS-Treasury arbitrage | No page yet |
| CRSP / Compustat (via WRDS) | Supporting equity holdings data (Y-9C bank trading book filings cited; CRSP implied for stock characteristics) | [WRDS / CRSP / Compustat](/wiki/licensed/wrds/) (licensed) |
| Coalition Greenwich / S&P (qualitative) | JPMorgan equity derivatives market share since 2015 (cited contextual fact) | No page yet |

The CIP spread construction and FX arbitrage measurement follow the
methodology of Du, Tepper, and Verdelhan (2018).

Sample: 32 arbitrage spreads, daily, January 1, 2010 to February 29, 2020
(post-GFC, pre-Covid). CDS-bond and Treasury-swap series start Sep 2011 for
some maturities. CFTC quantity data weekly from July 2010.

## Theory / model

The paper develops a stylized model (Section I, pp. 2548-2553) in which a
unit measure of competitive, atomistic arbitrageurs (intermediaries) trade
N riskless arbitrage trades. The arbitrageur's objective is (eq. 1, p. 2549):

$$
\max_{q_{n,t},\, V_{k,t}} \sum_{n=1}^{N} q_{n,t} \left( s_{n,t} - \sum_l w_{n,l} f_{l,t} \right)
- \frac{1}{2} \sum_{k=1}^{K} c_{k,t} V_{k,t}^2
$$

where $$s_{n,t}$$ is the arbitrage spread on trade $$n$$ at time $$t$$, $$q_{n,t}$$
is the quantity supplied, $$w_{n,l}$$ is the fraction of trade $$n$$ funded from
source $$l$$ (with cost $$f_{l,t}$$ in excess of zero), $$V_{k,t}$$ is the
aggregate scale of activities under balance-sheet constraint $$k$$, and
$$c_{k,t}$$ is the marginal cost of meeting constraint $$k$$. Market clearing
requires $$q_{n,t} = a_{n,t}$$ (inelastic outside demand).

**Canonical benchmarks.** Under balance-sheet and funding integration with a
single balance-sheet constraint ($$c_{k,t} = 0$$ for $$k > 1$$, $$f_{l,t} = 0$$
for all $$l$$), the equilibrium spread is (eq. 2, p. 2550):

$$
s_{n,t} = v_{n,1} c_{1,t} V_{1,t} = v_{n,1} c_{1,t} \left( \sum_n a_{n,t} v_{n,1} \right)
$$

All spreads move with the single factor $$c_{1,t} V_{1,t}$$ and are perfectly
correlated. This is the prediction the data contradict: the canonical
single-constraint intermediary model of He and Krishnamurthy (2013) implies
perfect spread correlation, whereas the mean pairwise correlation is 0.22.
Under a single frictional funding factor with balance-sheet
integration ($$c_{k,t} = 0$$, $$v_{n,k} = 0$$, $$f_{n,1} > 0$$, $$f_{n,l} = 0$$
for $$l > 1$$), spreads are $$s_{n,t} = w_{n,1} f_{1,t}$$ -- again a one-factor
structure. Under integration with many constraints ($$L = 1$$, $$K > 0$$) spreads
have a K+1 factor structure (eq. 3, p. 2550). The margin-based asset pricing
of Garleanu and Pedersen (2011), in which integrated funding implies a one- or
two-factor spread structure, is contradicted by the high-dimensional factor
structure documented in the data:

$$
s_{n,t} = w_{n,1} f_{1,t} + \sum_{k=1}^{K} v_{n,k} c_{k,t} V_{k,t}
$$

**Funding segmentation.** When trades $$n = 1,\ldots,N_1$$ can use only source
$$l = 1$$ and trades $$n = N_1+1,\ldots,N$$ can use only source $$l = 2$$, the
equilibrium is (eq. 4, p. 2551):

$$
s_{n,t} = \begin{cases} w_{n,1} f_{1,t} & \text{if } n \leq N_1 \\ w_{n,2} f_{2,t} & \text{if } N_1 < n \end{cases}
$$

Cross-group correlation equals only $$\rho(f_{1,t}, f_{2,t})$$ (eq. 5, p. 2551):

$$
\rho(s_{n_1,t},\, s_{n_2,t}) = \begin{cases} 1 & \text{if } n_1, n_2 \leq N_1 \text{ or } N_1 < n_1, n_2 \\ \rho(f_{1,t}, f_{2,t}) & \text{if } n_1 \leq N_1,\; n_2 > N_1 \end{cases}
$$

**Balance-sheet segmentation.** When arbitrageurs in group I specialize in
trades $$n = 1,\ldots,N_1$$ and group $$\tilde{I}$$ in trades $$n = N_1+1,\ldots,N$$, with
different marginal balance-sheet costs, equilibrium spreads are (eq. 6,
p. 2552). The premise that intermediaries specialize draws on evidence of
intermediary specialization in credit derivatives in Siriwardane (2019):

$$
s_{n,t} = \begin{cases} \epsilon_{n,i} + v_{n,1} c_{1,t}^{I} V_{1,t}^{I} & \text{if } n \leq N_1 \\ \epsilon_{n,j} + v_{n,1} c_{1,t}^{\tilde{I}} V_{1,t}^{\tilde{I}} & \text{if } N_1 < n \end{cases}
$$

The correlation between spreads of the two groups depends on (i) correlation
of balance-sheet shocks across groups, (ii) correlation of demand shocks, and
(iii) cross terms (eq. 7, p. 2552):

$$
\rho(s_{1,t}, s_{2,t}) = \rho(c_{1,t}^{I},\, c_{1,t}^{\tilde{I}}) \times \rho(a_{1,t}, a_{2,t})
+ \rho(c_{1,t}^{I},\, a_{2,t}) \times \rho(c_{1,t}^{\tilde{I}},\, a_{1,t})
$$

The model is not estimated structurally; it organizes the empirical tests by
providing testable signatures: funding segmentation implies covariance between
certain spreads and certain funding rates; balance-sheet segmentation implies
covariance between certain spreads and specific intermediary balance-sheet
costs.

## Method

The paper applies four methods, each addressing a different identification
challenge, building on `sign-restricted-svar`, `panel-regression`,
`differences-in-differences`, and `instrumental-variables`.

**Sign-restricted SVAR (supply vs. demand decomposition, Section II.C).** For
each futures-based trade $$i$$, let $$Y_t = [s_t \;\; q_t]'$$ be the vector of the
spread and quantity (gross open interest). The structural VAR is (eq. 8,
p. 2565):

$$
B Y_t = A_0 + A_1 Y_{t-1} + \epsilon_t, \qquad \epsilon_t = [\epsilon_{s,t} \;\; \epsilon_{d,t}]'
$$

The reduced form is $$Y_t = \Phi_0 + \Phi_1 Y_{t-1} + u_t$$ where
$$\Phi_0 = B^{-1} A_0$$, $$\Phi_1 = B^{-1} A_1$$, and the residual covariance
$$\Sigma_u$$ depends on $$B$$. Sign restrictions on the impact matrix identify
the structural shocks (eq. 9, p. 2565):

$$
\begin{bmatrix} u_{s,t} \\ u_{q,t} \end{bmatrix}
= \underbrace{\begin{bmatrix} - & + \\ + & + \end{bmatrix}}_{B^{-1}}
\begin{bmatrix} \epsilon_{s,t} \\ \epsilon_{d,t} \end{bmatrix}
$$

A supply shock ($$\epsilon_s$$) lowers spreads and raises quantities; a demand
shock ($$\epsilon_d$$) raises both. The sign-restricted SVAR used to separate
supply from demand shocks builds on Uhlig (2005). Estimation follows Arias,
Rubio-Ramirez, and
Waggoner (2018): Bayesian Normal-Wishart prior, 1,000 draws from the posterior
using Cholesky decomposition of $$\Sigma_u$$. The model is estimated separately
for each trade; the correlations of supply and demand shocks across trades are
computed from the median-draw shock series.

**Panel OLS: funding sensitivity (Section III.B, Table III).** The baseline
funding regression relates monthly changes in arbitrage-implied riskless rates
to Treasury yield changes and TED spread changes (eq. 10, p. 2569):

$$
\Delta r_{i,j,t} = \alpha_{i,j} + \beta_1 \Delta y_{j,t} + \beta_2 \Delta \text{TED}_t + \epsilon_{i,j,t}
$$

- $$r_{i,j,t}$$ is the implied riskless rate for trade $$i$$ in strategy $$j$$
- $$y_{j,t}$$ is the maturity-matched Treasury yield
- $$\text{TED}_t$$ is the maturity-matched LIBOR minus Treasury spread (proxy for unsecured funding costs)
- Standard errors are clustered by strategy-month.

## Empirical specifications

**Spec 1: MMF reform DiD (R5, eq. 11, p. 2572).** Baseline differences-in-
differences estimating the 2016 MMF reform impact on unsecured vs. secured
spreads, using daily data, trade and time fixed effects, clustered by trade
and date. The 2016 MMF reform event study design builds on Anderson, Du, and
Schlusche (2019):

$$
s_{i,t} = \alpha_i + \alpha_t + \beta \cdot \mathbf{1}[i \in \text{Unsecured}] \cdot \mathbf{1}[t \geq \text{October2016}] + \epsilon_{i,t}
$$

- $$s_{i,t}$$ is the absolute value of the arbitrage spread for trade $$i$$ on date $$t$$
- $$\mathbf{1}[i \in \text{Unsecured}]$$ equals 1 for CIP, box, and equity spot-futures trades
- $$\mathbf{1}[t \geq \text{October2016}]$$ equals 1 on or after the reform month
- Fixed effects: trade ($$\alpha_i$$) and time ($$\alpha_t$$); SE clustered by trade and date

Column (1) of Table IV (p. 2573) reports $$\beta = 11.77^{**}$$ (t = 2.47).
A dynamic version replaces the single post-reform indicator with monthly
leads and lags to trace the time profile of adjustment.

**Spec 2: IV for equity repo funding (R6, Table V, p. 2575).** The baseline
augments eq. (10) with flows into Fidelity IPrime MMFs. The IV instrument is
passive flows (eq. on p. 2575):

$$
Z_t = F_t \times L_{t-3}^{I}
$$

- $$F_t$$ is total flow into all Fidelity MMFs
- $$L_{t-3}^{I}$$ is the lagged share of Fidelity MMF assets that are IPrime
- Standard errors are clustered by strategy-month

The IV estimate (column 4, Table V) of the
equity spot-futures spread on Fidelity flows is $$\beta = -1.09^{**}$$ (t = -2.25);
the CIP/box and secured spread coefficients are indistinguishable from zero.

**Spec 3: London Whale dynamic DiD (R7, eq. 12, p. 2583).** In a weekly panel
of unsecured arbitrage spreads, the event study estimates relative widening of
equity spot-futures vs. other unsecured spreads around the March 1 and June
13, 2012 event dates:

$$
s_{i,t} = \alpha_i + \alpha_t + \sum_{j=-4}^{24} \beta_j \cdot \mathbf{1}[i \in \text{Equity SF}] \cdot \mathbf{1}[t = j] + \epsilon_{i,t}
$$

- $$j$$ indexes weeks since the first event date
- $$\alpha_i$$, $$\alpha_t$$ are trade and time fixed effects

Panel C of Figure 7 (p. 2582) shows equity
spot-futures spreads were significantly elevated relative to other unsecured
spreads for several months following each event date.

**Spec 4: Hedge fund balance-sheet forecasting regression (R9, eq. 13,
p. 2585).** Monthly changes in spread levels on lagged hedge fund returns:

$$
\Delta s_{i,t} = \alpha + \beta\, r_{t-1}^{H} + \epsilon_{i,t}
$$

- $$r_{t-1}^{H}$$ is the lagged monthly return of Barclay's fixed-income arbitrage hedge fund index (standardized to mean zero, unit variance)

Table VII (p. 2586) shows $$\beta = -0.66^{**}$$ (t = -3.04) for secured spreads and
$$\beta = 0.00$$ (t = 0.01) for unsecured spreads; the effect is concentrated
in Treasury-swap and CDS-bond sub-strategies.

## When to read the full paper

Obtain the article via [DOI 10.1111/jofi.13469](https://doi.org/10.1111/jofi.13469)
if you are: evaluating the cross-market structure of limits to arbitrage;
testing intermediary asset pricing models across market segments; studying
the 2016 MMF reform's effects on derivatives markets; replicating the SVAR
decomposition or the event studies; or checking specific coefficient estimates
in the Internet Appendix. The locators above point to the exact tables and
figures. For "what did this paper find," the table above is the intended
default.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5), October 2025,
pp. 2543–2590. DOI: 10.1111/jofi.13469. © 2025 the American Finance
Association. Published by Wiley under the Wiley VOR terms; paywalled.

This distillation was extracted by an LLM on 2026-05-31 and is **not
human-verified or independently reproduced**. Extraction is extract-only:
core results and locators reproduced for research commentary; no verbatim
reproduction of substantial portions. Contact the publisher for reuse rights.

> Siriwardane, Emil N., Adi Sunderam, and Jonathan Wallen. "Segmented
> Arbitrage." *The Journal of Finance* 80, no. 5 (October 2025): 2543–2590.
> DOI: 10.1111/jofi.13469.
