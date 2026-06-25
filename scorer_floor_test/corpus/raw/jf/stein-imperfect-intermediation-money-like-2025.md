---
title: "Imperfect Intermediation of Money-Like Assets: Stein & Wallen (2025)"
description: >-
  Distilled: T-bill rates fall below the Fed's RRP rate because money funds
  substitute imperfectly between T-bills and RRP, with heterogeneous and
  state-dependent elasticity, and because corporate treasurers demand T-bills
  as pledgeable collateral. When T-bill supply shrinks enough to drive elastic
  funds to a corner, remaining less-elastic funds become marginal, and supply
  shocks have an order-of-magnitude larger impact on T-bill rates. J. Finance
  2025, paywalled. Eight core results with source locators, the theoretical
  model, and the empirical specifications.
sidebar:
  label: Stein-Wallen 2025
  order: 1
tags: [paper-summary, money-markets, fixed-income, intermediary-asset-pricing,
       collateral, treasury-bills, monetary-policy, panel-regression,
       instrumental-variables, peer-reviewed, unreplicated,
       data:crane-mmf, data:wrds]
paper:
  authors: Jeremy C. Stein, Jonathan Wallen
  authorList:
    - { family: Stein, given: Jeremy C., affiliation: Harvard University and NBER }
    - { family: Wallen, given: Jonathan, affiliation: Harvard Business School }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3185–3221
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13500
  jel:
    codes: [E43, G12, G23]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Banking stability, regulation, efficiency', 'Economic theories and models', 'Economic Theory and Policy']
  dataAccess: licensed-commercial
  outcome:
    - RRP-bill spread (one-month T-bill rate minus expected RRP rate)
    - money fund T-bill portfolio weight
    - sensitivity of T-bill rates to T-bill supply shocks
  outcomeClass: [bank-funding, asset-prices]
  license: >-
    Paywalled (Wiley standard terms; Crossref license[].content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days=0, start=2025-10-14; no CC licence found)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley publisher site, 2026-06-03)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 0

  methods:
    role: both
    contributes: heterogeneous-elasticity-intermediation
    family: theory
    buildsFrom: [panel-regression, instrumental-variables]
    identification: instrument
  contributionType: [new-theory, new-fact]
  mechanisms: [demand-elasticity, intermediary-constraint, collateral, limits-to-arbitrage]

  scope:
    region: US
    assetClass: US Treasury bills, money market instruments
    period: 2013-09..2024-06
    frequency: monthly
    dataType: [market, accounting]
    granularity: [aggregate, firm, security]
    n: "130 monthly obs (money market); 2,730 firm-years (corporate collateral)"

  relatesTo:
    - { cite: 'Nagel (2016)', doi: '10.1093/qje/qjw028', relation: builds-on, note: 'liquidity premium on near-money assets; T-bills as near-money with collateral value' }
    - { cite: 'Duffie (2010)', doi: '10.1111/j.1540-6261.2010.01569.x', relation: builds-on, note: 'slow-moving capital as a general source of pricing frictions in financial markets' }
    - { cite: 'He and Krishnamurthy (2013)', doi: '10.1257/aer.103.2.732', relation: builds-on, note: 'intermediary asset pricing where intermediary wealth/constraints drive risk premia' }
    - { cite: 'Fleckenstein and Longstaff (2024)', doi: '10.1111/jofi.13371', relation: builds-on, note: 'Treasury richness and collateral demand for Treasuries' }
    - { cite: 'Siriwardane, Sunderam and Wallen (2025)', doi: '10.1111/jofi.13469', relation: cites, note: 'law-of-one-price violations weakly integrated across markets; segmented arbitrage' }
    - { cite: 'Bech and Klee (2011)', doi: '10.1016/j.jmoneco.2011.05.007', relation: cites, note: 'limited access to IORB created a wedge between IORB and fed funds; partial segmentation example' }
    - { cite: "d'Avernas and Vandeweyer (2024)", relation: cites, note: 'Treasury bill shortages and pricing of short-term assets' }

  openQuestions:
    - 'Whether money funds will behave more elastically in a future T-bill scarcity episode given gradual learning in the first episode; the model implies even if they do, the collateral-driven corner mechanism means spreads can still become large (p. 3216).'
    - 'Whether the collateral-demand channel for corporate treasurers is structural and durable or varies with derivatives regulation and margin rules; direct evidence on the primitive determinants is suggestive but not conclusive (pp. 3187-3188, 3204).'
    - 'Extending the intermediary-heterogeneity framework to other asset markets (e.g. long-term bonds, QE effects) where observing corner status of individual intermediaries is harder (p. 3216).'

  replicationCode:
    status: available

  findings:
    - { ref: R1, outcome: RRP-bill spread (one-month T-bill rate minus expected RRP rate), metric: basis-points, value: "6 bps (non-scarce); 37 bps (scarce Apr 2022-Apr 2023); spike to ~160 bps (Mar-Apr 2023)", direction: positive }
    - { ref: R2, outcome: money fund T-bill portfolio weight, metric: correlation, value: "order of magnitude less variable; nearly uncorrelated with actual", direction: none, vsBenchmark: "investor-flows-only counterfactual vs actual T-bill share" }
    - { ref: R3, outcome: money fund T-bill portfolio weight, metric: coefficient, value: "5.885*** (0.98); R-sq 14%; N=4,449 fund-quarters", direction: positive, vsBenchmark: "100 bp return increase raises AUM by 5.9 pp (economically small)" }
    - { ref: R4, outcome: corporate Treasury holdings share, metric: coefficient, value: "3.481** (1.57); R-sq 0.15; N=2,730 firm-years", direction: positive, vsBenchmark: "1-SD derivatives exposure raises Treasury share 1.8 pp vs 7.6% mean" }
    - { ref: R5, outcome: money fund T-bill portfolio weight, metric: coefficient, value: "IV -6.19*** (2.24); first stage -2.20*** (0.59); N=90 monthly obs", direction: negative, vsBenchmark: "vs OLS -0.94; IV ~7x larger in absolute value" }
    - { ref: R6, outcome: money fund T-bill portfolio weight, metric: coefficient, value: "median elasticity 7.4 (IQR 4.4-10.1); Treasury funds 5.4, govt 7.2, prime 8.6", direction: mixed, vsBenchmark: "fund-level IV elasticities; Treasury funds significantly less elastic than prime funds" }
    - { ref: R7, outcome: sensitivity of T-bill rates to T-bill supply shocks, metric: coefficient, value: "interaction -4.484** (1.83); unconditional IV -0.656*** (0.21); full sample N=127", direction: negative, vsBenchmark: "7x amplification in scarce vs non-scarce regime" }
    - { ref: R8, outcome: RRP-bill spread (one-month T-bill rate minus expected RRP rate), metric: return-spread, value: "153 bps yield gap; pre-June maturities avg ~4.4% vs RRP ~5.05%; avg spread 81 bps", direction: negative, vsBenchmark: "pre-debt-ceiling T-bills vs post-deadline T-bills at June 1 2023 cutoff" }
  resultType: new-finding

  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-03, role: extracted, note: "Full text read (pp. 3185-3222); eight results extracted. Not human-verified. Not reproduced. Replication code referenced in paper (Supporting Information) but not run here." }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-03, role: verified, note: "Locators and reported magnitudes re-checked against source PDF; all eight result rows verified correct against cited tables and figures; all equations (1)-(25) checked term-by-term with no errors found; frontmatter authors/year/venue/resultsCount correct; relatesTo body-mention locatability confirmed for all seven edges; no em-dashes or null values detected." }
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
        confirmed correct - instrument identification (IV on Treasury supply),
        [new-theory, new-fact] contribution, four mechanism slugs all registry-matched
        and PDF-supported, introducesData absent (no new source), and scope fields
        faithful to Tables I-IV; no corrections required.
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
        against the source PDF; fixed R4 outcome field (was "RRP-bill spread",
        corrected to "corporate Treasury holdings share" per Table III); all
        other values/directions/metrics confirmed against PDF figures and tables.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13500
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-10-14; no Creative Commons licence present'

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical model of heterogeneous-elasticity intermediation, and the empirical specifications that test it: enough to know what was found and how, without reading the full 38 pages. To replicate or extend, read the original at [doi.org/10.1111/jofi.13500](https://doi.org/10.1111/jofi.13500).

## TL;DR

Stein and Wallen (2025) study why the one-month T-bill rate regularly falls below the rate on the Fed's reverse repurchase (RRP) facility, even though both are overnight-equivalent, credit-risk-free, government-backed instruments. The RRP-bill spread is a stark violation of the near-money premium logic of Nagel (2016), who shows T-bills command a liquidity premium precisely because they are more money-like. Stein and Wallen build and test a model with two types of investors: money funds (which have direct RRP access) and corporate treasurers (which do not). The model has three frictions: (i) money fund AUM is exogenously fixed (segmentation from outside investors, consistent with Bech and Klee (2011) showing limited access creates persistent rate wedges), (ii) corporate treasurers value T-bills for pledgeability as derivatives collateral, related to the Treasury richness documented by Fleckenstein and Longstaff (2024), and (iii) money funds substitute imperfectly and heterogeneously between T-bills and RRP, echoing the slow-moving capital mechanism of Duffie (2010). As the most-elastic money funds exhaust their T-bill holdings and reach a corner, the remaining less-elastic funds become marginal. Supply shocks then hit T-bill rates seven times harder than when funds are not constrained. Related evidence on law-of-one-price violations across segmented markets is provided by Siriwardane, Sunderam and Wallen (2025). The broader intermediary asset pricing literature, including He and Krishnamurthy (2013) who model aggregate intermediary wealth as the key state variable, typically focuses on a single representative intermediary; this paper shows that heterogeneity across intermediaries is equally important. Supply-side T-bill scarcity and its pricing consequences are documented in d'Avernas and Vandeweyer (2024). The mechanism described here was the key driver of the large yield dislocations during the 2023 debt-ceiling episode, when more than 90% of money fund AUM was already at a corner.

## Core results

Magnitudes and significance are as reported. `\*`, `\*\*`, `\*\*\*` = 10%, 5%, 1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | One-month T-bill rates fell well below expected RRP rates for most of June 2021 to May 2023, with the gap frequently exceeding 50 bps and spiking to over 160 bps during the March-April 2023 debt-ceiling uncertainty | Figure 1, p. 3186; Figure 3, p. 3199 | Average RRP-bill spread 6 bps in Region 2 (non-scarce periods); 37 bps in scarce period (April 2022 to April 2023); spike to ~160 bps in March-April 2023 |
| R2 | Flows from outside investors into money funds explain very little of the variation in aggregate T-bill portfolio weight; virtually all substitution from T-bills to RRP is driven by active portfolio rebalancing by money fund managers | Figure 4, p. 3201 | Counterfactual (investor-flows-only) portfolio share is an order of magnitude less variable than actual share; the two series are nearly uncorrelated |
| R3 | Money fund investor flows are almost insensitive to fund returns: a 100 bp increase in returns raises fund AUM by only 5.9 percentage points per quarter | Table II, column (4), p. 3202 | Coefficient 5.885\*\*\* (0.98); adjusted R-squared 14%; N = 4,449 fund-quarters |
| R4 | Corporate derivatives exposure is associated with a significantly larger Treasury share in liquid assets: a one-standard-deviation increase in derivatives exposure raises the Treasury share by 1.8 percentage points, relative to a 7.6% mean | Table III, column (3), p. 3203 | Coefficient 3.481\*\* (1.57); adjusted R-squared 0.15; N = 2,730 firm-years, 2004-2021 |
| R5 | IV estimate of aggregate money fund elasticity of substitution: a 1 bp increase in the RRP-bill spread due to a supply-driven decrease in T-bills causes money funds to decrease their T-bill portfolio weight by 6.2%, or 79 bps of portfolio weight | Table IV, column (3), p. 3206 | IV coefficient -6.19\*\*\* (2.24); first stage: 1% increase in Treasury supply decreases spread by 2.20\*\*\* (0.59) bps; N = 90 monthly observations |
| R6 | Fund-level elasticities are highly heterogeneous: median elasticity is 7.4 (interquartile range 4.4 to 10.1); Treasury funds (most restrictive mandate) have average elasticity 5.4 vs. government funds 7.2 and prime funds 8.6 | Figure 6, p. 3209 | Kernel density of fund-level IV elasticities estimated on September 2013 to March 2021; Treasury funds significantly less elastic than government and prime funds |
| R7 | When T-bills are scarce (April 2022 to April 2023), a 1% decrease in instrumented T-bill supply causes the RRP-bill spread to increase by 4.5 bps, about seven times the unconditional estimate of 0.66 bps | Table V, column (4), p. 3212 | Interaction coefficient Scarce T-Bills x Delta T-Bill: -4.484\*\* (1.83); unconditional IV: -0.656\*\*\* (0.21); full sample September 2013 to June 2024 |
| R8 | T-bills maturing before June 1, 2023 (the projected debt-ceiling date) yielded on average 153 bps less over May 2023 than T-bills maturing on June 1, 2023; average RRP-bill spread for pre-June maturities was 81 bps | Figure 10, p. 3215 | Discontinuity in T-bill yield curve at June 1, 2023 maturity cutoff; T-bills maturing in May 2023 averaged ~4.4%, vs. RRP rate ~5.05%; June maturities showed a positive RRP-bill spread reflecting default risk |

**Overall (paper's conclusion).** Even in a simple and transparent setting, frictions in financial intermediation create economically significant and time-varying spreads between money-like assets. Heterogeneity in intermediary elasticity is the central mechanism: as more-elastic intermediaries are driven to corners, their departure leaves only less-elastic intermediaries as the marginal market participants, amplifying the rate impact of supply and demand shocks. This state-dependence has broad implications for evaluating QE programs and other policy interventions whose market impact is implicitly assumed to be constant over time.

## Theory / model

The model (Section I, pp. 3191-3195) has a total supply of T-bills $$S$$ held by money funds or corporate treasurers. Money funds also have access to the RRP facility; treasurers cannot access RRP and can only hold T-bills or private repo. Aggregate money fund AUM is exogenously fixed at $$A$$.

**Treasurers' collateral demand.** Corporate treasurers derive collateral benefits from T-bills. Their demand for T-bills is an increasing function of the RRP-bill spread (p. 3192):

$$
X(r_b - r_p), \quad \text{with } X(\cdot) \text{ increasing}
$$

where $$r_b$$ is the T-bill rate and $$r_p$$ is the (exogenous) RRP rate. Because private repo and RRP rates are nearly identical in the data, the model writes treasurer demand as $$X(r_b)$$ for simplicity.

**Money fund preferences.** Fund $$i$$ splits its portfolio between T-bills (weight $$T_i \in [0,1]$$) and RRP (weight $$1 - T_i$$) with utility (equation (1), p. 3192):

$$
U_i = r_b T_i + r_p (1 - T_i) + V_i(T_i) \tag{1}
$$

The term $$V_i(T_i)$$ is an increasing concave nonpecuniary benefit from holding T-bills, capturing idiosyncratic preferences (fund mandates, window-dressing, etc.). The paper uses the functional form (equation (2), p. 3192):

$$
V_i(T_i) = \frac{T_i - \frac{1}{2} T_i^2}{b_i} \tag{2}
$$

where $$b_i$$ is the elasticity parameter. Less elastic funds have smaller $$b_i$$; more elastic funds have larger $$b_i$$. The elasticity parameter $$b_i$$ is distributed uniformly on $$[b_L, b_H]$$ with $$b_L > 0$$.

**Optimal portfolio.** The first-order condition for an interior optimum is (equation (3), p. 3193):

$$
(r_p - r_b) = V_i'(T_i) = \frac{1 - T_i}{b_i} \tag{3}
$$

yielding fund $$i$$'s optimal T-bill share in an interior solution (equation (4), p. 3193):

$$
T_i^* = 1 - b_i (r_p - r_b) \tag{4}
$$

**Three regions.** The model's solution is characterized by three regions as T-bill supply $$S$$ shrinks:

- *Region 1 (ample supply):* $$r_b \geq r_p$$; all money funds hold only T-bills; market-clearing pins the spread at zero or negative: $$X(r_b) = S - A$$ (equation (5), p. 3193).
- *Region 2 (moderate scarcity):* Some funds are at an interior; the market-clearing condition is $$X(r_b) = S - A\theta(r_b) T^{**}$$ (equation (11), p. 3194), where $$\theta(r_b)$$ is the fraction of funds still holding T-bills (equation (12), p. 3194):

$$
\theta(r_b) = \frac{b_U - b_L}{b_H - b_L} \tag{12}
$$

The sensitivity of the T-bill rate to supply changes in Region 2b (Case 2b, where the most elastic fund is already at the corner) is (equation (13), p. 3194):

$$
\frac{dr_b}{dS} = \frac{1}{X'(r_b) + A\theta\!\left(\frac{b_U + b_L}{2}\right)} \tag{13}
$$

This sensitivity increases continuously ($$\frac{d^2 r_b}{dS\, d\theta} < 0$$) as fewer funds remain in the T-bill market.

- *Region 3 (extreme scarcity):* All money funds are at corners holding only RRP. Market clearing is entirely determined by treasurer collateral demand: $$X(r_b) = S$$ (equation (14), p. 3195), and the sensitivity is:

$$
\frac{dr_b}{dS} = \frac{1}{X'(r_b)} \tag{15}
$$

The transition from Region 2 to Region 3 is the key amplification mechanism documented empirically.

## Method

The paper combines a partial-equilibrium theoretical model with instrumental-variable panel regressions. It builds on `panel-regression` and `instrumental-variables` as its core estimation primitives.

**Instrument for the RRP-bill spread.** The key endogeneity concern is that T-bill supply may respond to money fund demand. The paper instruments monthly changes in the RRP-bill spread using monthly log differences in the privately-held supply of all Treasuries (not just T-bills), on the grounds that Treasury auction timing follows a "regular and predictable" schedule (citing Garbade (2007)) and total Treasury supply is not driven by money fund demand dynamics (p. 3206-3207, Table IV).

First-stage specification (equation (23), p. 3207):

$$
\Delta \text{Spread}_t = \alpha + \beta \Delta \text{Treasury}_t + \epsilon_t \tag{23}
$$

**Aggregate elasticity regression.** The estimating equation for the aggregate T-bill portfolio weight of the money fund sector (equation (22), p. 3205):

$$
\Delta w_{\text{Bills},t} = \alpha - \beta \Delta \text{Spread}_t + \epsilon_t \tag{22}
$$

where $$\Delta w_{\text{Bills},t}$$ is the log difference in the aggregate T-bill portfolio weight. The IV estimate (Table IV, column (3)) delivers $$\hat\beta = 6.19$$.

**Supply-shock amplification regression.** The headline test of state-dependence (equation (24), p. 3212):

$$
\Delta \text{Spread}_t = \alpha + \beta_0 \Delta \text{TBill Supply}_t + \beta_1 \text{Scarce TBills}_t + \gamma \Delta \text{TBill Supply}_t \times \text{Scarce TBills}_t + \varepsilon_t \tag{24}
$$

The interaction term $$\gamma$$ captures the incremental sensitivity when T-bills are scarce. A continuous version replaces the dummy with *Constrained Share* (equation (25), p. 3213):

$$
\Delta \text{Spread}_t = \alpha + \beta_0 \Delta \text{TBill Supply}_t + \beta_1 \text{Constrained Share}_t + \gamma \Delta \text{TBill Supply}_t \times \text{Constrained Share}_t + \varepsilon_t \tag{25}
$$

where *Constrained Share* is the AUM-weighted fraction of funds with less than 5% T-bill weight and at least 10% weight in either RRP or T-bills.

**Flow decomposition.** To test the segmentation assumption, the paper decomposes dollar changes in T-bill holdings into an investor-flow component and a managerial rebalancing component (equations (16)-(20), pp. 3200-3201):

$$
\Delta D_{\text{Bill},i,t} = w_{\text{Bill},i,t} A_{i,t} - w_{\text{Bill},i,t-1} A_{i,t-1} \tag{16}
$$

$$
\text{IFlow}_{\text{Bill},i,t} = w_{\text{Bill},i,t-1} (A_{i,t} - A_{i,t-1}) \tag{17}
$$

$$
\text{MFlow}_{\text{Bill},i,t} = \Delta D_{\text{Bill},i,t} - \text{IFlow}_{\text{Bill},i,t} \tag{18}
$$

The counterfactual T-bill portfolio share driven only by investor flows is constructed as (equation (20), p. 3201):

$$
\widetilde{\text{Ratio}}_t = \frac{\tilde{D}_{\text{Bill},t}}{\tilde{D}_{\text{Bill},t} + D_{\text{RRP},t}} \tag{20}
$$

**Corporate collateral regression.** For the collateral-demand channel (equation (21), p. 3202):

$$
w_{UST,i,t} = \alpha_i + \beta \, \text{Deriv}_{i,t-1} + \varepsilon_{i,t} \tag{21}
$$

where $$w_{UST,i,t}$$ is firm $$i$$'s Treasury holdings share and $$\text{Deriv}_{i,t-1}$$ is lagged derivatives exposure (absolute value of P&L on derivatives / total assets). Standard errors are clustered by firm; OLS with time, industry, and time-by-industry fixed effects.

## Empirical specifications

**Aggregate elasticity (R5, Table IV, p. 3206).** Monthly time-series, September 2013 to March 2021 (N = 90). LHS: log change in aggregate money fund T-bill portfolio weight. RHS: change in the RRP-bill spread (instrumented by log change in privately-held Treasury supply). First stage F is implicit in the significant first-stage coefficient (-2.20 bps per 1% Treasury supply increase). Standard errors are robust to heteroskedasticity. The IV coefficient of -6.19 rises by almost an order of magnitude relative to OLS (-0.94), consistent with demand-side endogeneity biasing the OLS toward zero.

**Supply-shock amplification (R7, Table V, p. 3212).** Monthly time-series, September 2013 to June 2024 (N = 127; excludes May-June 2023 for debt-ceiling effects). LHS: change in RRP-bill spread. RHS: instrumented change in T-bill supply, scarce-T-bills indicator (April 2022 to April 2023), and their interaction. Unconditional IV: -0.656\*\*\* (0.21) bps per 1% supply change. Interaction with scarce indicator: -4.484\*\* (1.83). Total effect when scarce: -(0.656 + 4.484) = -5.1 bps per 1% supply decrease (i.e., a 7x amplification). Column (5) with continuous constrained-share interaction shows that when 91% of funds are constrained (April 2023), a 1% supply decrease increases the spread by 6.0 bps, vs. 1.5 bps when 24% are constrained (May 2022).

**Corporate collateral demand (R4, Table III, p. 3203).** Annual firm-year panel, 193 large U.S. non-financial corporates, 2004-2021 (N = 2,730). LHS: Treasury holdings share (Treasury + agency securities / Treasury + agency + cash equivalents + money fund shares). RHS: lagged derivatives exposure (absolute P&L / total assets), firm size, industry and time fixed effects. One-standard-deviation increase in derivatives exposure (0.516%) is associated with a 1.8 percentage-point higher Treasury share (column (3)). Standard errors are clustered by firm.

**Investor flow sensitivity (R3, Table II, p. 3202).** Monthly and quarterly, September 2013 to June 2024 (N = 13,434 monthly; 4,449 quarterly). LHS: investor flows as a percentage of lagged fund AUM. RHS: contemporaneous fund return. Coefficient in AUM-weighted quarterly specification (column 4): 5.885\*\*\* (0.98). The economic implication: during the scarce period (April 2022 to April 2023) when the spread averaged 37 bps, a fund invested entirely in RRP would receive only 2.2 percentage points more quarterly inflows than a T-bill-invested fund.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Crane Data LLC (monthly money fund holdings and AUM) | T-bill and RRP portfolio weights, fund-level elasticity estimation, AUM decomposition | [Crane Data](/wiki/licensed/crane-mmf/) (licensed) |
| Federal Reserve (NY) - RRP program data | RRP counterparty identities, RRP take-up amounts, administered RRP rate | No page yet |
| Bloomberg (secondary market yields) | One-month T-bill yields, OIS rates for maturity adjustment | [Bloomberg](/wiki/licensed/bloomberg/) (licensed) |
| Federal Reserve (effective Fed Funds rate) | Maturity adjustment for expected one-month RRP return; monetary policy benchmarks | No page yet |
| U.S. Treasury / Federal Reserve (Treasury supply) | Privately-held outstanding Treasuries (instrument for T-bill supply shocks) | No page yet |
| Compustat (annual) via WRDS | Derivatives P&L, firm size, corporate bond and Treasury holdings for large non-financial firms, 2001-2021 | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Darmouni and Mota (2024) - corporate securities holdings | Cash and securities holdings for 200 largest U.S. public non-financial firms, 2001-2021 | No page yet |

Sample for the main money-market analysis: monthly, September 30, 2013 to June 30, 2024 (130 months). Sample for corporate collateral analysis: annual firm-year panel, 2004-2021.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13500) if you are: studying the T-bill market microstructure or the Fed's RRP facility design; analyzing how intermediary heterogeneity shapes asset price sensitivity to supply shocks; calibrating the impact of Treasury debt management decisions on short-term rates; or extending the framework to other asset classes where identifying which intermediaries are at corners is feasible. The exact model equations and Appendix A derivation of equation (13) are the load-bearing technical content.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025. Wiley, paywalled. This distillation was extracted by an LLM on 2026-06-03 and is **not human-verified or independently reproduced**. Extract-only; the verbatim PDF is not hosted here.

> Stein, Jeremy C., and Jonathan Wallen. "The Imperfect Intermediation of Money-Like Assets."
> *The Journal of Finance* 80, no. 6 (December 2025): 3185–3221.
> DOI: 10.1111/jofi.13500. © 2025 the American Finance Association.
