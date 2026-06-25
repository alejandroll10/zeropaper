---
title: "Value without Employment: Barkai & Panageas (2025)"
description: >-
  Distilled: Young firms have sharply reduced their contribution to
  aggregate employment since the early 1980s, yet their contribution to
  aggregate sales and market capitalization has remained stable, implying a
  rising average-to-marginal revenue product of labor (ARPL-to-MRPL ratio).
  A calibrated model of dynamic firm heterogeneity shows this single shift
  jointly explains the labor share decline, muted investment-share response,
  and declining job flows, while predicting only a modest (~8%) long-run drop
  in aggregate consumption. J. Finance 2025, CC BY 4.0. Eight core results
  with source locators, datasets used, the model (dynamic firm heterogeneity
  with monopolistic competition), and the method with equations.
sidebar:
  label: Barkai-Panageas 2025
  order: 1
tags: [paper-summary, business-dynamism, labor-share, markups, firm-dynamics,
       macro-finance, panel-regression, open-access, cc-by, peer-reviewed,
       unreplicated, data:wrds, data:pitchbook, data:nets, data:census, data:nipa]
paper:
  authors: Simcha Barkai, Stavros Panageas
  authorList:
    - { family: Barkai, given: Simcha, affiliation: Carroll School of Management, Boston College }
    - { family: Panageas, given: Stavros, affiliation: Anderson School of Management, UCLA }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3725-3770
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13505
  jel:
    codes: [E24, D24, L11]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Economic Theory and Policy', 'Firm Innovation and Growth', 'Economic Theory and Institutions']
  dataAccess: licensed-commercial
  outcome:
    - employment share of young-firm IPO cohorts
    - market-value share of young-firm IPO cohorts
    - sales share of young-firm IPO cohorts
    - aggregate labor share of value added
    - aggregate consumption (long-run steady state)
  outcomeClass: [firm-real-outcomes, macro-aggregates]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-10-07; corroborated by artifact p. 3725 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-03)
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 2
  methods:
    role: both
    contributes: arpl-mrpl-dynamics
    family: structural
    buildsFrom: [panel-regression, dynamic-general-equilibrium, real-options]
    identification: structural
  contributionType: [new-fact, new-theory]
  mechanisms: [market-power]
  scope:
    region: US
    assetClass: US equities, private firms, establishments
    period: 1985-01..2019-12
    frequency: annual
    dataType: [market, accounting, administrative]
    granularity: [aggregate, firm]
    n: "7,565 firms, 82,823 firm-years (Compustat 1985-2014); 213,792 acquisitions (NETS 1998-2014)"
  relatesTo:
    - { cite: 'Decker et al. (2016a)', relation: builds-on, note: 'documents declining business dynamism and young-firm employment contribution that this paper reconciles with VC-industry strength (pp. 3728, 3769)' }
    - { cite: 'De Loecker, Eeckhout & Mongey (2021)', doi: '10.3386/w28761', relation: builds-on, note: 'jointly explain labor share decline and declining dynamism via rising markups; this paper differs by using a dynamic model and presenting new empirical evidence on the employment-value divergence (pp. 3730, 3768)' }
    - { cite: 'Barkai (2020)', doi: '10.1111/jofi.12909', relation: builds-on, note: 'prior evidence of declining labor and capital shares; used here to calibrate the markup increase since the mid-1980s (pp. 3752, 3768)' }
    - { cite: 'Haltiwanger et al. (2017)', doi: '10.7208/chicago/9780226454108.001.0001', relation: builds-on, note: 'data on employment growth dispersion for young firms used to calibrate productivity volatility sigma (p. 3753)' }
    - { cite: 'De Loecker, Eeckhout & Unger (2020)', doi: '10.1093/qje/qjz041', relation: cites, note: 'markup estimates used as sector-level inputs to the multisector model (p. 3767)' }
    - { cite: 'Akcigit & Ates (2023)', doi: '10.1086/724289', relation: contradicts, note: 'this paper argues that the decline in young-firm employment is not mirrored in market values or sales, contradicting a purely "weakness" narrative (pp. 3728-3729)' }
    - { cite: 'Decker et al. (2020)', doi: '10.1257/aer.20190680', relation: builds-on, note: 'declining responsiveness of firms to idiosyncratic shocks; the model captures this as lower xi* for new-type firms (pp. 3757-3758)' }
    - { cite: 'Gutierrez & Philippon (2017)', doi: '10.1353/eca.2017.0013', relation: cites, note: 'investmentlessness; consistent with the models prediction of a muted decline in the investment share (p. 3756)' }
  openQuestions:
    - 'Whether the rise in the ARPL-to-MRPL ratio reflects primarily higher markups, lower labor intensity, or sectoral shifts toward high-markup sectors: the paper distinguishes these three channels analytically but cannot conclusively identify which dominates empirically (pp. 3727-3728, 3764-3767).'
    - 'Whether the muted consumption effect holds if adjustment costs, financial frictions, or welfare differences between workers and firm owners are added to the model: the paper abstracts from these (pp. 3767-3768).'
    - 'The NETS data do not permit measurement of sales growth separately from employment growth at the establishment level because sales are imputed from industry-level ratios, limiting the ability to confirm the revenue-employment divergence in the broader (non-Compustat) universe (p. 3741).'
  findings:
    - { ref: R1, outcome: employment share of young-firm IPO cohorts, metric: coefficient, value: "log employment contribution 0.71 lower for 2010-2014 cohort vs 1985-1989; log sales contribution 0.11 lower; log market-value contribution 0.07 higher", direction: negative, vsBenchmark: "1985-1989 cohort bin baseline" }
    - { ref: R2, outcome: market-value share of young-firm IPO cohorts, metric: coefficient, value: "normalized log ratio rises by ~0.8 log points for 2010-2014 cohort vs 1985-1989", direction: positive, vsBenchmark: "1985-1989 cohort bin (normalized to 0)" }
    - { ref: R3, outcome: market-value share of young-firm IPO cohorts, metric: coefficient, value: "deflated exit values comparable or larger for each successive cohort at the same age (except 1995-1999 dot-com outlier)", direction: positive, vsBenchmark: "predecessor cohorts at same cohort age" }
    - { ref: R4, outcome: employment share of young-firm IPO cohorts, metric: coefficient, value: "YoungAcquirer: -0.024** to -0.039***; YoungAcquirer x Post-2005: -0.148*** to -0.161***", direction: negative }
    - { ref: R5, outcome: aggregate labor share of value added, metric: coefficient, value: "model labor share 0.60 to 0.54 (data: 0.60 to 0.54); young-firm employment share ~22% to ~8% (data: ~18% to ~10%); job creation and destruction each decline ~4-5 pp", direction: mixed, vsBenchmark: "data moments from 1983 calibration baseline" }
    - { ref: R6, outcome: aggregate consumption (long-run steady state), metric: elasticity, value: "pass-through factor ~12%; 40% drop in new-firm output implies 4.8% consumption decline", direction: negative }
    - { ref: R7, outcome: aggregate consumption (long-run steady state), metric: coefficient, value: "-8.1% long-run consumption decline (markup-driven worst-case scenario)", direction: negative, vsBenchmark: "~40-50% employment decline benchmark" }
    - { ref: R8, outcome: aggregate consumption (long-run steady state), metric: coefficient, value: "dC^SS/C^SS = -0.081; Term 1 = -0.047; Term 2 = -0.142; Term 3 = -0.016; Term 4 = +0.124", direction: mixed }
  resultType: overturns
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: Full text read (pp. 3725-3770); eight results extracted from the CC-BY PDF. Not human-verified. Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: Locators and reported magnitudes re-checked against the source PDF; one fix applied - R4 Post-2005 interaction lower bound corrected from -0.148 to -0.145 (Table III, p. 3744); all other magnitudes, locators, equations (eqs. 2, 6, 7, 8, 12, 13, 15, 16, 17, 23, 30), and frontmatter confirmed correct.
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
        introducesData, data-scope) re-checked against the source PDF;
        mechanisms set to [market-power] (the rising-markups channel, pp. 3727,
        3747-3749, 3752, 3760-3764). A declining labor-intensity (alpha) driver
        was considered but reconciled out of the mechanisms axis as a
        production-technology characteristic, not an economic channel; all
        other axes confirmed correct.
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
        against the source PDF; R4 Post-2005 interaction lower bound corrected
        from -0.145 to -0.148 in findings[], Core-results table, and Empirical
        specifications body (Table III col 1 = -0.148, PDF p. 3744 text confirms
        "between 0.148 and 0.161"); all other values confirmed correct.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13505
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-10-07'
  rightsSignalConflict: false
  proposedVocab:
    - { axis: topic, term: business-dynamism, def: 'Research studying trends in firm entry and exit rates, job creation and destruction, and the contribution of young firms to aggregate employment and growth.', aliases: [firm-dynamism, declining-dynamism] }
    - { axis: topic, term: markups, def: 'Price-cost markups charged by firms; used as a measure of market power and linked to the labor share, rents, and capital intensity.', aliases: [price-cost-markups, market-power] }
    - { axis: topic, term: macro-finance, def: 'Research at the intersection of macroeconomics and finance, linking aggregate quantities (output, consumption, labor share) to firm-level or asset-market quantities.', aliases: [macro-finance-link] }
---

**What this is.** The paper's core results, the economic model connecting the
ARPL-to-MRPL ratio to aggregate trends, and the key equations: enough to
understand what it found and why, without reading all 46 pages. To replicate
or extend, read the full source at [doi.org/10.1111/jofi.13505](https://doi.org/10.1111/jofi.13505).

## TL;DR

Young firms' employment contribution has fallen sharply since the early 1980s,
but their contributions to aggregate sales and stock market value have not
fallen similarly. The ratio of market-value contribution to employment
contribution of young-firm IPO cohorts has more than doubled over 1985 to 2014
(Figure 1, p. 3734). Pitchbook exit-value data and NETS establishment-level
data corroborate this pattern for the broader universe of firms. The divergence
implies a rising average-to-marginal revenue product of labor (ARPL-to-MRPL
ratio) for recent young-firm cohorts: these firms earn similar or greater
revenues per dollar of market value while employing far fewer workers.

The paper introduces this feature into a standard model of dynamic firm
heterogeneity (monopolistic competition, heterogeneous productivity, endogenous
bankruptcy), shows it jointly explains a large set of empirical trends including
the labor share decline, and then proves analytically that a 40% drop in
young-firm employment contribution translates into only a 4.8% drop in
steady-state consumption (under the base-case assumption that the shift
reflects lower labor intensity). Even in the worst case where the shift
reflects a rise in economic rents, the long-run consumption decline is bounded
at 8.1%, roughly five times smaller than the employment decline.

## Core results

Magnitudes and significance are as reported; `**`/`***` = 5%/1%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Employment contribution of recent IPO cohorts fell, but market-value and sales contributions did not show a similar decline | Figure 1, Panels A-D, pp. 3733-3734 | Log employment contribution of 2010-2014 cohort bin is 0.71 lower than 1985-1989 cohort bin; log sales contribution is only 0.11 lower; log market-value contribution is 0.07 higher |
| R2 | The ratio of market-value contribution to employment contribution has more than doubled | Figure 1, Panel D, p. 3734 | Normalized log ratio (1985-1989 = 0) rises by about 0.8 log points for the 2010-2014 cohort bin relative to the earliest cohort |
| R3 | Recent cohort deflated exit values (Pitchbook) are at least as large as those of earlier cohorts, controlling for age | Figures 3-4, pp. 3737-3738 | With the exception of the 1995-1999 cohort (dot-com era outlier), each successive cohort bin has deflated exit values similar to or larger than its predecessors at the same cohort age |
| R4 | Young firms (post-2005) exhibit slower employment growth at acquired establishments relative to older acquirers, conditional on year, industry, state, and establishment age and size | Tables II-IV, pp. 3743-3745 | Young Acquirer coefficient: -0.024\*\* to -0.039\*\*\* in the first specification (Table II); Young Acquirer x Post-2005 interaction: -0.148\*\*\* to -0.161\*\*\* (Table III); coefficient is stable with establishment age and size controls (Table IV) |
| R5 | A single change in the ARPL-to-MRPL ratio (modeled as a rise in rent share, i.e., lower xi\*) simultaneously reproduces the labor share decline, stable investment share, falling young-firm employment share, declining job creation and destruction, and rising market-value-to-employment ratio | Figures 6-9, pp. 3755-3758 | Model labor share declines from 0.60 to 0.54 (data: 0.60 to 0.54); young-firm employment share falls from ~22% to ~8% (data: ~18% to ~10%); investment share remains roughly flat; job creation and destruction rates each decline by ~4-5 pp |
| R6 | The elasticity of steady-state consumption to a decline in young-firm output is approximately 12%, so a 40% drop in new-firm output implies only a 4.8% decline in consumption | pp. 3727, 3761 | Under base-case parameters (xi = 0.93, alpha = 0.62), the pass-through factor (1 - xi) / (alpha xi) is approximately 12%; a 40% drop in new-firm output implies a 4.8% consumption decline |
| R7 | In the worst case (rise in economic rents), the long-run consumption decline from the observed dynamics is bounded at 8.1% | pp. 3727-3728, 3764 | Markup-driven scenario (Barkai (2020) estimates): 8.1% drop in steady-state consumption between old and new steady states, which is roughly five times smaller than the 40-50% decline in young-firm employment |
| R8 | The multisector model quantifies the total steady-state consumption impact at -8.1%, with the main negative term being the rent-share channel (-14.2%), partially offset by positive factor-reallocation effects (+12.4%) | Table VI, p. 3767 | dC^SS/C^SS = -0.081; Term 1 (new-firm output) = -0.047; Term 2 (rents) = -0.142; Term 3 (factor intensity) = -0.016; Term 4 (factor reallocation) = +0.124 |

**Overall (paper's conclusion).** Young firms are not weaker than their
predecessors in terms of value creation, only in terms of employment creation.
This divergence implies a higher ARPL-to-MRPL ratio for recent cohorts.
Attributing this shift to a rise in rents (as in Decker et al. (2016a),
De Loecker, Eeckhout, and Mongey (2021)) provides a unified explanation for
the labor share decline, declining business dynamism, and declining job
flows. Akcigit and Ates (2023) document the same dynamism trends; this paper
argues those trends are not mirrored in market values and thus cannot be
interpreted as pure firm weakness. Decker et al. (2020) show that firms have
become less responsive to idiosyncratic shocks; the model captures this as
lower $$\xi^*$$ for new-type firms, implying a reduced standard deviation of
employment changes for new cohorts. De Loecker, Eeckhout, and Unger (2020)
provide the sector-level markup estimates used in the multisector model
calibration. Gutierrez and Philippon (2017) document investmentlessness;
consistent with the model, the investment share responds only modestly.
Haltiwanger et al. (2017) provide employment growth dispersion data used
to calibrate productivity volatility $$\sigma$$. Even under this
worst-case interpretation, large declines in young-firm employment imply
only moderate long-run declines in aggregate consumption, because a substantial
part of the decline in new-firm output is an amplified transitory factor
adjustment rather than a permanent loss.

## Theory / model

The economic setting is monopolistic competition with heterogeneous
intermediate-goods producers (Section II, pp. 3746-3750). Time is
continuous. A representative final-goods firm assembles intermediate inputs
using a Kimball (1995) aggregator (eq. 7, p. 3747):

$$
1 = \int_{i \in I} \mathcal{Y}\!\left(\frac{y_{it}}{Y_t}\right) di \tag{7}
$$

where $$y_{it}$$ is the quantity of intermediate good $$i$$ at time $$t$$, $$Y_t$$ is
aggregate output, and $$\mathcal{Y}(\cdot)$$ satisfies $$\mathcal{Y}(1)=1$$,
$$\mathcal{Y}'>0$$, $$\mathcal{Y}''<0$$. In the Dixit-Stiglitz special case
$$\mathcal{Y}(x) = x^{\xi}$$ with $$\xi \in (0,1)$$, this reduces to the familiar
CES aggregator (eq. 8, p. 3747):

$$
Y_t = \left(\int_{i \in I} y_{it}^{\xi}\, di\right)^{1/\xi}. \tag{8}
$$

Each intermediate producer uses a Cobb-Douglas production function
(eq. 12, p. 3748):

$$
y_{it} = Z_{it} k_{it}^{1-\alpha_i} l_{it}^{\alpha_i}, \tag{12}
$$

where $$l_{it}$$ is labor, $$k_{it}$$ is capital, $$\alpha_i \in (0,1)$$ is the
labor intensity (allowed to vary across firms), and $$Z_{it}$$ is
firm-specific productivity following a geometric Brownian motion
(eq. 13, p. 3748):

$$
dZ_{it} = \mu Z_{it}\, dt + \sigma Z_{it}\, dW_{it}. \tag{13}
$$

Firms must also pay a fixed overhead labor cost $$\bar{l}$$ per unit time (the
"operating leverage" that drives endogenous bankruptcy). They face an
exogenous death shock at rate $$\lambda > 0$$. The first-order conditions for
capital and labor equate marginal revenue products to factor prices
(eqs. 15-16, p. 3749):

$$
(1-\alpha_i)\!\left(1 - \frac{1}{\varepsilon_i}\right) p_{it} Z_{it}
  k_{it}^{-\alpha_i} l_{it}^{\alpha_i} = r_t^K, \tag{15}
$$

$$
\alpha_i\!\left(1 - \frac{1}{\varepsilon_i}\right) p_{it} Z_{it}
  k_{it}^{1-\alpha_i} l_{it}^{\alpha_i - 1} = w_t, \tag{16}
$$

where $$\varepsilon_i \equiv -\mathcal{Y}^{\prime}\!\left(\frac{y_{it}}{Y_t}\right) /
\!\left[\frac{y_{it}}{Y_t} \mathcal{Y}^{\prime\prime}\!\left(\frac{y_{it}}{Y_t}\right)\right]$$
is the absolute demand elasticity. In the Dixit-Stiglitz case,
$$\xi_i = 1 - \frac{1}{\varepsilon_i}$$ is the sum of factor shares, and the
markup is $$\frac{1}{\xi_i} - 1$$. The ARPL-to-MRPL ratio for firm $$i$$
follows directly from (16) (eq. 17, p. 3749):

$$
\frac{\frac{p_{it} y_{it}}{l_{it}}}{\frac{\partial(p_{it} y_{it})}{\partial l_{it}}} = \frac{1}{\xi_i \alpha_i}. \tag{17}
$$

A high ARPL-to-MRPL ratio therefore corresponds to a small $$\xi_i$$ (large
rent share) or a small $$\alpha_i$$ (low labor intensity), or both.

**Representative household.** The household maximizes (p. 3750):

$$
\mathrm{E}_t\!\left(\int_t^{\infty} u(C_s) e^{-\rho(s-t)}\, ds\right),
\quad u(C) = \frac{C^{1-\gamma}}{1-\gamma},
$$

with discount rate $$\rho > 0$$ and inverse IES $$\gamma > 0$$. Goods market
clearing requires $$C_t + I_t = Y_t$$; capital evolves as
$$\dot{K}_t = -\delta K_t + I_t$$.

**Identification and counterfactual.** Section II.D (pp. 3751-3754) considers
a transition experiment where from time $$t_0$$ onward a fraction
$$1 - e^{-\vartheta(t-t_0)}$$ of arriving firms are "new-type" with
$$\xi^* < \xi$$. The model is calibrated to match the labor share and employment
volatility of young firms from $$t_0 = 1983$$ onward (Table V, p. 3753).

## Method

The paper combines two methods: a descriptive-empirical analysis of cohort
contributions (applied to Compustat, Pitchbook, and NETS) and a dynamic
structural model solved analytically in steady state plus numerically along
the transition path.

The paper builds on `dynamic-general-equilibrium` (the Kimball-aggregator
model with Cobb-Douglas production and GBM productivity) and `panel-regression`
(the NETS establishment-level switcher regressions). The analytical steady-state
solution exploits a time-age-cohort decomposition and the Kimball demand
structure to obtain closed-form expressions for wages, output, and the
cross-sectional distribution of productivity (eqs. 19-22, pp. 3750-3751).

**ARPL-to-MRPL decomposition.** Equation (6) (p. 3746) expresses the
ARPL-to-MRPL ratio as a function of two elasticities:

$$
\frac{\text{ARPL}_i}{\text{MRPL}_i} = \frac{1}{1 + \frac{y_i}{p_i}\frac{\partial p_i}{\partial y_i}}
  \times \frac{1}{\frac{l_i}{y_i}\frac{\partial y_i}{\partial l_i}} = \frac{1}{1+\text{markup}^{-1}} \times \frac{1}{\text{labor intensity}}. \tag{6}
$$

**Lemma 1 (cohort divergence, p. 3739).** Under a time-age-cohort
decomposition, the discrepancy between the log change in market-value
contribution and the log change in employment contribution of young firms
equals the log change in the (employment-weighted) ARPL-to-MRPL ratio of
young firms versus the whole economy (eq. 2, p. 3739):

$$
\Delta\!\log\!\left(\frac{P_{t,t}}{\sum_{s \leq t} P_{t,s}}\right)
  - \Delta\!\log\!\left(\frac{l_{t,t}}{\sum_{s \leq t} l_{t,s}}\right)
  = \Delta\!\log\!\left(\frac{\sum_{i,t} \omega^i_{t,t}(\delta^i_{t,t}-1)}{\sum_{i,s \leq t}\omega^i_{t,s}(\delta^i_{t,s}-1)}\right), \tag{2}
$$

where $$\delta^i_{t,s} \equiv \frac{p^i_{t,s} y^i_{t,s} / l^i_{t,s}}{w_t}$$
is the ARPL-to-MRPL ratio of firm $$i$$ born at time $$s$$.

**Proposition 1 (aggregate implications, p. 3760).** In the single-sector
economy, as the discount rate $$\rho \to 0$$, the percentage change in
steady-state consumption is (eq. 23, p. 3760):

$$
\frac{dC^{SS}}{C^{SS}} = \frac{1}{\alpha}\frac{1-\xi}{\xi}\frac{dY^{\text{new}}}{Y^{\text{new}}}
  - \left(\frac{1-\xi}{1-\xi(1-\alpha)}\right)\frac{d\alpha}{\alpha}
  + \frac{1}{\alpha}(G - D)\frac{d\xi}{\xi}, \tag{23}
$$

where $$G \equiv \int_{z^*}^{\infty}(\tilde{g}(z) - \tilde{m}(z))\log y(z)\,dz$$
and $$D \equiv (1 + \frac{1}{\xi}) + \alpha\frac{\xi(1-\alpha)}{1-\xi(1-\alpha)} - (1-\alpha)$$,
with $$\tilde{g}(z)$$ and $$\tilde{m}(z)$$ the stationary and entering revenue
distributions. The factor $$\frac{1-\xi}{\alpha\xi}$$ in the first term is
approximately 12% under baseline parameters, quantifying why a large drop in
new-firm output passes through only modestly to consumption.

**Proposition 2 (multisector, p. 3765)** generalizes (23) to $$N^S$$ sectors
with sector-specific $$\xi^S$$ and $$\alpha^S$$ (eq. 30, p. 3765), adding a
fourth term that captures factor reallocation across sectors.

## Empirical specifications

Three separate empirical exercises establish the employment-value divergence.

**Compustat cohort contributions (Section I.A, pp. 3731-3734).** The paper
forms five-year IPO cohort bins for all Compustat nonfinancial U.S. public
firms founded within 10 years of their IPO, 1985 to 2014 (7,565 firms, 82,823
firm-year observations). Employment, sales, and market-value contributions of
each cohort are expressed as shares of aggregate totals among all Compustat
firms in the same year and summed within bins (Figure 1). No regression
estimator is used here; the results are descriptive cohort-share series.

**Pitchbook exit values (Section I.B, pp. 3735-3738).** For firms exiting by
IPO or M&A, post-money valuations are deflated by aggregate stock market
capitalization and traced by cohort age. This is also a descriptive exercise,
not a regression.

**NETS establishment switchers (Section I.D, pp. 3740-3745).** The headline
regression is:

$$
\log L_{t+1} - \log L_{t-1} = \beta_1\,\text{YoungAcquirer}_{it}
  + \beta_2\,(\text{YoungAcquirer}_{it} \times \text{Post-2005})
  + \gamma_t + \delta_{j \times k \times s} + \varepsilon_{it}, \tag{OLS}
$$

where the dependent variable is the log change in employment from year $$t-1$$
(before acquisition) to year $$t+1$$ (after acquisition) for a target
establishment. YoungAcquirer equals one if the acquiring firm is less than
eight years old. Fixed effects include year $$\gamma_t$$ and year
$$\times$$ four-digit SIC $$\times$$ state $$\delta_{j \times k \times s}$$. Standard
errors are clustered by year $$\times$$ SIC4 $$\times$$ state. Sample: 213,792
acquisitions, 1998 to 2014 (Table I, p. 3743).

The first specification (Table II) pools the full sample. The main specification
(Table III) adds the YoungAcquirer $$\times$$ Post-2005 interaction term. Table IV
adds establishment age bin dummies and log-employment in year $$t-1$$ as
controls to address differential selection by young acquirers.

Results: YoungAcquirer coefficient = -0.024`**` to -0.039`***`; Post-2005
interaction = -0.148`***` to -0.161`***` (Tables II-III); results are stable
with age and size controls (Table IV).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Compustat (via WRDS) | U.S. public firm employment, sales, and market value by IPO cohort bin, 1985-2014 | [WRDS](/wiki/licensed/wrds/) (licensed) |
| PitchBook | Exit valuations (IPO and M&A) for private and public U.S. firms by founding-year cohort, 1990-2019 | [PitchBook](/wiki/licensed/pitchbook/) (licensed) |
| National Establishment Time Series (NETS) | Establishment-level employment and ownership changes (acquirer age), 1998-2014; 213,792 acquisitions | [NETS](/wiki/licensed/nets/) (licensed) |
| Census Business Dynamics Statistics (BDS) | Aggregate employment share of young firms (ages 0-5), firm-size distribution, job creation and destruction rates, 1983-2019 | [U.S. Census Bureau public data products](/wiki/datasets/census/) |
| BEA National Accounts (GDP-by-Industry, Fixed Asset Tables) | Labor share, investment share, and value added by sector for model calibration and multisector analysis | [NIPA](/wiki/datasets/nipa/) |

Sample for Compustat analysis: 7,565 firms, 82,823 firm-year observations,
1985-2014, annual frequency. NETS sample: 213,792 acquisitions, 1998-2014.
BDS and BEA coverage: 1983-2019 (model transition period).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13505) if you are:
studying the connection between business dynamism and the labor share and want
the analytical propositions; examining the welfare implications of rising
markups or declining labor intensity; building a calibrated model of firm
dynamics with heterogeneous markups; or using the NETS switcher design to
measure young-firm employment behavior. The Internet Appendix contains proofs,
the elastic labor supply extension, the numerical algorithm for the transition
path, and sector-level parameter estimates.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025. This
distillation was extracted by an LLM on 2026-06-03 and is **not
human-verified or independently reproduced**. The CC BY 4.0 licence permits
mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Barkai, Simcha, and Stavros Panageas.
> "Value without Employment."
> *The Journal of Finance* 80, no. 6 (December 2025): 3725-3770.
> DOI: 10.1111/jofi.13505. Copyright 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
