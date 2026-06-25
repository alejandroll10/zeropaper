---
title: "Term Structure in a Heterogeneous Monetary Union: Costain, Nuno & Thomas (2025)"
description: >-
  Distilled: Costain, Nuno, and Thomas build an arbitrage-based affine term
  structure model for a two-country monetary union with sovereign default risk,
  showing that the credit risk premium accounts for roughly three-quarters of the
  Italy-Germany sovereign spread, and that ECB PEPP asset purchases compressed
  Italian yields primarily through a default risk extraction channel rather than
  the standard duration risk channel. J. Finance 2025, paywalled. Six core
  results with source locators, datasets used, the model, and the method.
sidebar:
  label: Costain-Nuno-Thomas 2025
  order: 1
tags: [paper-summary, fixed-income, term-structure, sovereign-debt, monetary-policy,
       asset-pricing, structural, peer-reviewed, unreplicated,
       data:datastream, data:ecb-data-warehouse]
paper:
  authors: James Costain, Galo Nuno, Carlos Thomas
  authorList:
    - { family: Costain, given: James, affiliation: Bank of Spain }
    - { family: Nuno, given: Galo, affiliation: Bank of Spain }
    - { family: Thomas, given: Carlos, orcid: "0000-0002-8333-6436", affiliation: Bank of Spain }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2389-2434
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13463
  jel:
    codes: [G12, E43, E58]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - European Monetary and Fiscal Policies
    - Global Financial Crisis and Policies
    - Monetary Policy and Economic Impact
  dataAccess: licensed-commercial
  outcome:
    - euro-area sovereign bond yields (Germany and Italy)
    - Italy-Germany sovereign spread decomposition
    - yield curve shifts around PEPP announcement
  outcomeClass: [asset-prices, macro-aggregates]
  license: >-
    Wiley VOR terms and conditions (paywalled); confirmed via Crossref DOI
    metadata content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-05-28. Not CC-licensed.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley Online Library; confirmed paywalled via Crossref licence metadata 2026-06-05)"
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 0

  methods:
    role: both
    contributes: heterogeneous-monetary-union-atsm
    family: structural
    buildsFrom: [affine-term-structure, extended-kalman-filter, method-of-simulated-moments]
    identification: structural

  contributionType: [new-theory, new-fact]

  mechanisms:
    - credit-inflation-channel
    - intermediary-constraint
    - risk-sharing

  scope:
    region: euro area (Germany and Italy)
    assetClass: sovereign bonds
    period: 1999-01..2022-12
    frequency: monthly
    dataType: [market, administrative]
    granularity: [aggregate, security]
    n: "Monthly zero-coupon yields at 1m, 1Y, 5Y, 10Y, 20Y maturities for Germany and Italy, Jan 1999-Dec 2022; plus two-day window around PEPP announcement (March 18-20, 2020)"

  findings:
    - ref: R1
      outcome: Italy-Germany 10-year sovereign spread
      metric: basis-points
      value: "Long-run model spread = 79 bps; expected default loss = 22 bps (28%); credit risk premium = 62 bps (78%)"
      direction: positive
      vsBenchmark: credit risk premium accounts for ~3/4 of the total 10-year spread (Table II, p. 2419)
    - ref: R2
      outcome: Germany 10-year term premium
      metric: basis-points
      value: "Model term premium = 142 bps (vs. data term premium ~125 bps); Sharpe ratio model 0.57 vs. data 0.51"
      direction: positive
      vsBenchmark: model overpredicts long-run term premium slightly (142 vs. 125 bps in data); Sharpe ratio well matched (Table II, p. 2419)
    - ref: R3
      outcome: yield curve shift on PEPP announcement (Italian bonds)
      metric: basis-points
      value: "Italian 10Y yield fell ~71 bps on March 18-20, 2020; model-predicted decline = 71 bps; credit risk premium accounts for 81% of decline at 10-year maturity"
      direction: negative
      vsBenchmark: model matches observed -71 bps in data; credit risk extraction dominates duration extraction (Figure 6, p. 2424; Table III, p. 2427)
    - ref: R4
      outcome: yield curve shift on PEPP announcement (German bonds)
      metric: basis-points
      value: "German 10Y yield changed by roughly -10 bps (model); small, nonmonotonic observed shift"
      direction: negative
      vsBenchmark: much smaller effect on German yields than Italian; consistent with asymmetric default-risk channel (Figure 6, p. 2424)
    - ref: R5
      outcome: Italy-Germany sovereign spread (robustness across calibrations)
      metric: basis-points
      value: "Credit risk premium share of spread: 74% in long run, 81% for PEPP impact, robust across 12 alternative parameterizations (Table III, p. 2427)"
      direction: positive
      vsBenchmark: low-risk-aversion and low-haircut calibrations are implausible and worsen model fit (Table III, p. 2427)
    - ref: R6
      outcome: impact of pandemic outbreak on Italian yields
      metric: basis-points
      value: "Model predicts ~120-160 bps upward shift across all maturities of Italian yields from pandemic fiscal shock; driven mainly by credit risk premium increase (Figure 9, p. 2431)"
      direction: positive
      vsBenchmark: out-of-sample check (not used in estimation); model broadly matches observed pandemic shock in magnitude (Figure 9, p. 2431)

  resultType: new-finding

  relatesTo:
    - { cite: "Vayanos and Vila (2021)", doi: '10.3386/w29875', relation: extends, note: "extends their single-country preferred-habitat ATSM to a two-country monetary union with sovereign default risk" }
    - { cite: "Duffie and Singleton (1999)", doi: '10.1093/rfs/12.4.687', relation: builds-on, note: "uses their log-affine pricing of defaultable bonds with a fractional recovery assumption" }
    - { cite: "Greenwood and Vayanos (2014)", doi: '10.1093/rfs/hht133', relation: tests, note: "tests and extends their duration risk extraction channel; finds default risk extraction is the primary channel in the euro area" }
    - { cite: "Hamilton and Wu (2012)", relation: tests, note: "tests their one-factor ATSM with ELB; extends to include default risk channel for peripheral euro-area bonds" }
    - { cite: "Calvo (1988)", relation: builds-on, note: "self-fulfilling rollover crisis mechanism that endogenizes the default probability in Section II" }
    - { cite: "Cole and Kehoe (2000)", doi: '10.1111/1467-937x.00123', relation: builds-on, note: "self-fulfilling debt crises framework used to model rollover crisis default decision" }
    - { cite: "Corsetti and Dedola (2016)", doi: '10.1111/jeea.12184', relation: extends, note: "extends their two-period monetary-fiscal interaction model to a fully dynamic ATSM environment" }

  openQuestions:
    - "The analytical ATSM solution requires a deterministic (time-varying but non-stochastic) default probability, which implies a constant sovereign spread across maturities in steady state, at odds with the empirically upward-sloping spread term structure; extending to stochastic default probability would require a fully numerical solution (pp. 2393, 2422)."
    - "The model assumes a single Peripheral country (Italy), abstracting from diversification across multiple peripheral issuers; this limits scope for cross-country spillovers within the Periphery (p. 2408, fn. 21)."
    - "The analysis could be applied to further analyze different designs for balance sheet expansions and reductions in a monetary union (p. 2432)."

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Read full PDF (46 pages); all locators confirmed against tables, figures, and equations in the paper. Not human-verified; not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-05, role: verified, note: "Locators and magnitudes re-checked against PDF; fixed three errors: (1) dataAccess upgraded from public to licensed-commercial (Datastream is a licensed commercial source), (2) findings[R2].value corrected to cite data term premium ~125 bps rather than total data yield 247 bps, (3) eq. 30 notation corrected from \\zeta(\\tau) to \\varsigma(\\tau) matching the PDF (\\zeta is already used for the remittance-rule coefficient)." }

  licenceVerification:
    - { source: "Crossref works/10.1111/jofi.13463", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-05-28. Not CC-licensed; paywalled." }
---

**What this is.** This is an LLM-distilled skeleton of the paper; read the
[original](https://doi.org/10.1111/jofi.13463) to replicate or extend. Not
human-verified; not reproduced.

## TL;DR

Costain, Nuno, and Thomas build an arbitrage-based affine term structure model
(ATSM) for a two-country monetary union (Core = Germany, Periphery = Italy)
where the Peripheral sovereign faces rollover-crisis default risk. The model
extends Vayanos and Vila (2021) to a multicountry setting with sovereign
default risk, building on Duffie and Singleton (1999) for defaultable bond
pricing. It decomposes yields into four components: expectations, term premium,
expected default loss, and credit risk premium. Calibrated to German and Italian
zero-coupon yields from 1999 to 2022, the model finds that the credit risk
premium accounts for roughly three-quarters of the long-run Italy-Germany
sovereign spread. For the ECB PEPP announcement of March 18, 2020, which
drove a ~71 bps fall in Italian 10-year yields, the model attributes about
four-fifths of the sovereign spread compression to a reduction in the credit
risk premium via a *default risk extraction channel*, not the conventional
duration risk channel identified in Greenwood and Vayanos (2014) and
Hamilton and Wu (2012).

## Core results

| # | Result | Locator | Magnitude as reported |
|---|---|---|---|
| R1 | Credit risk premium dominates the long-run IT-DE 10Y sovereign spread | Table II, p. 2419; Figure 5, p. 2420 | Model spread = 79 bps; expected default loss = 22 bps (28%); credit risk premium = 62 bps (78%); data spread = 126 bps |
| R2 | Model matches German 10Y term premium and Sharpe ratio | Table II, p. 2419; Figure 4, p. 2418 | Model TP = 142 bps vs. data term premium ~125 bps; model Sharpe 0.57, data 0.51 |
| R3 | PEPP announcement: 81% of IT yield decline attributed to credit risk premium | Figure 6, p. 2424; Table III, p. 2427 | Observed IT 10Y decline = 71 bps (March 18-20, 2020); model matches at calibration; credit risk premium share = 81% across robustness checks |
| R4 | PEPP announcement: small effect on German yields, consistent with asymmetry | Figure 6, p. 2424 | German 10Y: roughly -10 bps (model); nonmonotonic, small observed shift; asymmetry explained by default risk channel operating only on Peripheral bonds |
| R5 | Credit risk premium dominance is robust across 12 alternative calibrations | Table III, p. 2427 | CRP share: 74% long-run, 81% PEPP impact; low-gamma and low-delta calibrations worsen model fit substantially |
| R6 | Pandemic shock (out-of-sample): model predicts large upward shift in Italian yields | Figure 9, p. 2431 | Model-predicted shift = 120-160 bps across maturities; broadly matches observed Feb-to-Mar 2020 data; mainly driven by credit risk premium increase |

**Overall (paper's conclusion).** The paper proposes a model in which default
risk opens a novel *default risk extraction channel* for central bank asset
purchases, allowing large-scale parallel yield curve shifts like those observed
in Italy during the Covid-19 pandemic. Asset purchases compress both the credit
risk premium (by extracting defaultable bonds from private markets) and the
expected default loss (endogenously, by relieving fiscal pressure). The
duration risk channel is secondary in the euro-area context. The model
identifies that credit risk premia, not expected losses, dominate sovereign
spreads, and that the flexible PEPP design substantially enhanced its impact
relative to the earlier, rigid APP.

## Theory / model

The economy has two countries (Core and Periphery) in continuous time with an
infinite horizon. Core issues risk-free bonds; Periphery may partially default
on its obligations (Section I, pp. 2395-2408).

**Short-rate process.** The instantaneous riskless rate $$r_t$$ follows an
Ornstein-Uhlenbeck process (eq. 1, p. 2396):

$$dr_t = \kappa(\bar{r} - r_t)dt + \sigma dB_t \tag{1}$$

**Bond prices.** Conjecture that bond prices are log-affine:

$$P_t(\tau) = e^{-[A_t(\tau)r_t + C_t(\tau)]}, \quad P_t^*(\tau) = e^{-[A_t^*(\tau)r_t + C_t^*(\tau)]} \tag{8}$$

where $$\tau$$ is maturity, $$P_t(\tau)$$ is the Peripheral bond price, and
$$P_t^*(\tau)$$ is the Core bond price (p. 2398).

**Yield decomposition (Proposition 1, p. 2400, eq. 16-17).** Peripheral
yields $$y_t(\tau)$$ decompose into four affine components:

$$y_t(\tau) = \underbrace{\frac{1}{\tau}\mathbb{E}_t\int_0^\tau r_{t+s}ds}_{y_t^{EX}(\tau)} + \underbrace{\frac{1}{\tau}\mathbb{E}_t\int_0^\tau \left\{A_{t+s}(\tau-s)\lambda_{t+s} - \frac{\sigma^2}{2}[A_{t+s}(\tau-s)]^2\right\}ds}_{y_t^{TP}(\tau)} + \underbrace{\frac{1}{\tau}\mathbb{E}_t\int_0^\tau \delta\psi_{t+s}ds}_{y_t^{DL}(\tau)} + \underbrace{\frac{1}{\tau}\mathbb{E}_t\int_0^\tau \xi_{t+s}ds}_{y_t^{CR}(\tau)} \tag{16}$$

where $$\psi_t$$ is the Peripheral default arrival rate, $$\delta$$ is the
haircut, and $$\xi_t = \gamma\psi_t\delta^2\int_0^\infty X_t(\tau)d\tau$$
is the credit risk premium price (eqs. 13, 15, pp. 2399-2400).

**Proposition 2 (low default risk, p. 2401).** When $$\psi \to 0$$, term
premia are equalized across countries and depend only on the *aggregate* net
bond supply in the monetary union, so Core and Peripheral term premia move
symmetrically with ECB purchases.

**Proposition 3 (default risk shifts short yields, p. 2402-2403).** In the
ergodic distribution with constant default rate, the Peripheral yield is:

$$y_t(\tau) = (\psi\delta + \bar{\xi}) + \frac{(1+\Xi)(1-e^{-\hat\kappa\tau})}{\tau\hat\kappa}r_t + \frac{\int_0^\tau [A(u)(\kappa\bar{r}+\bar\lambda) - \frac{1}{2}\sigma^2[A(u)]^2]du}{\tau} \tag{\text{Prop. 3}}$$

where $$\lim_{\tau\to 0}y_t(\tau) = (1+\Xi)r_t + (\psi\delta + \bar\xi)$$,
so the default-related constant $$\psi\delta + \bar\xi$$ shifts the entire
Peripheral yield curve in parallel, including the short end, independent of
changes in the short-term riskless rate (p. 2403).

**Endogenous default (Section II, pp. 2403-2408).** Following Corsetti and
Dedola (2016), the paper models rollover crises as in Calvo (1988) and Cole
and Kehoe (2000). In a rollover crisis (arrival rate $$\eta$$), the Peripheral
government compares the cost of repayment $$V_0^R$$ (discounted emergency
taxation) to the cost of default $$V_0^D$$ (fixed restructuring cost $$\chi$$)
and defaults if $$V_0^R > V_0^D$$:

$$\mathbb{P}(\text{default at time }0|\text{crisis}) \approx \Phi(V_0^R) \tag{25}$$

The unconditional default rate is $$\psi_t = \eta\Phi_t$$, where fiscal
pressure $$F_t$$ (eq. 29) aggregates primary deficits, bond redemptions, and
central bank remittances. Central bank purchases reduce $$F_t$$ (via
remittances), hence reduce $$\psi_t$$, reinforcing both duration and default
risk extraction (eq. 26-29, pp. 2405-2407).

## Method

The paper solves for equilibrium in two stages.

**One-factor analytical solution (Section I).** Market clearing (eq. 7,
p. 2397) combined with the arbitrageurs' first-order conditions (eqs. 10-13)
yields two integral equations for the factor loadings $$\lambda_t$$ (price of
interest-rate risk) and $$\xi_t$$ (price of default risk):

$$\lambda_t = \gamma\sigma^2\int_0^\infty\left[(S_t(\tau)-Z_t(\tau))A_t(\tau) + (S_t^*(\tau)-Z_t^*(\tau))A_t^*(\tau)\right]d\tau \tag{14}$$

$$\xi_t = \gamma\psi_t\delta^2\int_0^\infty (S_t(\tau)-Z_t(\tau))d\tau \tag{15}$$

When $$\psi_t$$ is a deterministic function of time, both sides of (15) are
affine in $$r_t$$, yielding time-varying affine solutions $$\lambda_t = \Lambda_t r_t + \bar\lambda_t$$ and $$\xi_t = \Xi_t r_t + \bar\xi_t$$.

**Multifactor quantitative model (Section III, pp. 2408-2416).** For
calibration, the model adds two mean-zero PH demand shifters $$\varepsilon_t^h$$
and $$\varepsilon_t^{h*}$$ to capture PH demand fluctuations:

$$Z_t(\tau) = h(\tau) - \varsigma(\tau)\varepsilon_t^h + \tau\alpha(\tau)(y_t(\tau) - \hat\delta\psi_t) \tag{30}$$

The factor vector $$q_t \equiv [r_t, \varepsilon_t^h, \varepsilon_t^{h*}]^\top$$
follows a multivariate Ornstein-Uhlenbeck process:

$$dq_t = -K(q_t - \bar{r}\mathcal{E}_1)dt + \Sigma dB_t \tag{31}$$

Bond prices remain log-affine in $$q_t$$: $$P_t(\tau) = e^{-[A_t(\tau)^\top q_t + C_t(\tau)]}$$, $$P_t^*(\tau) = e^{-[A_t^*(\tau)^\top q_t + C_t^*(\tau)]}$$ (eq. 32, p. 2409).

**Calibration.** Two-step procedure: (i) directly calibrate observable
parameters including the OU parameters of $$r_t$$ (mean $$\bar{r} = 1.22\%$$,
$$\kappa = 0.062$$, $$\sigma = 63$$ bps), fiscal variables, and Eurosystem
purchase paths from ECB data; (ii) estimate the remaining 10 parameters
(Table I, p. 2416) by minimizing a distance criterion over long-run yield
moments (1999-2022) and the two-day PEPP announcement window shift. The
numerical solution uses finite-difference methods for the time-varying PDE
system.

## Empirical specifications

**Long-run moments target.** The distance criterion minimizes the sum of
squared deviations between model ergodic distribution and data for (Section
III.C, pp. 2413-2414):

- Mean yields on 1m, 1Y, 5Y, 10Y German bonds and 1Y, 5Y, 10Y Italian bonds
- Standard deviations of yields at same maturities (both countries)
- Within-country correlations between 1Y and 10Y yields (Germany and Italy)
- Cross-country correlation of 1Y yields and cross-country correlation of 10Y yields

All yields expressed in annualized percentage points. Sample: January 1999 to
December 2022 (monthly zero-coupon yields from Datastream).

**PEPP announcement target.** The second component of the distance criterion
matches the observed yield curve shifts (March 18 to March 20, 2020) for 1m,
1Y, 5Y, 10Y, and 20Y German and Italian bonds. The model compares equilibrium
yields under the pre-PEPP and post-PEPP fiscal/purchase scenarios (Section
III.C, p. 2414). The scale of the Italian yield shift pins down the elasticity
parameter $$\theta$$ (slope of the default rate with respect to fiscal
pressure).

**Robustness (Table III, p. 2427).** For each of 12 alternative
parameterizations (varying $$\kappa$$, $$\sigma$$, $$\delta$$, $$\gamma$$,
$$\psi$$, $$\theta$$, $$\hat{r}+\phi$$, $$\sigma_h$$, $$\alpha_h$$, $$\zeta=0$$
cases), the paper reports model fit (sum of squared deviations), credit risk
premium share of the total default compensation in the long run and in the
PEPP episode, and mean 10Y yields for Germany and Italy. The benchmark credit
risk premium share of 74% (long run) and 81% (PEPP) is robust across all
plausible calibrations.

**Pandemic out-of-sample test (Figure 9, p. 2431).** The model compares
average weekly German and Italian zero-coupon yields from February 13-19, 2020
to those from March 12-18, 2020, four weeks later. These observations are not
used in estimation and serve as an out-of-sample check.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| German and Italian zero-coupon sovereign bond yields (Datastream) | Main estimation targets: yields at 1m, 1Y, 5Y, 10Y, 20Y maturities, Jan 1999-Dec 2022; also two-day PEPP announcement window | [no page yet](/wiki/datasets/) |
| ECB and Eurosystem bond holdings (ECB Data Portal / official ECB publications) | Calibrate net bond supply and Eurosystem purchase paths for APP and PEPP; maturity distribution of Eurosystem holdings as of July 2021 | [ECB Data Portal](/wiki/datasets/ecb-data-warehouse/) |
| Banco de Espana fiscal projections (in-house debt sustainability model) | Long-run fiscal forecasts for Italy and Germany (primary deficits, debt, interest) extended from two-year-ahead Eurosystem projections | [no page yet](/wiki/datasets/) |
| Eser et al. (2023) PH demand estimates | Calibrate the fraction of sovereign debt held by preferred-habitat investors (44.2% of net debt for each country) | [no page yet](/wiki/datasets/) |
| Cruces and Trebesch (2013) haircut evidence | Fix haircut parameter $$\delta = 0.25$$ consistent with international evidence on sovereign defaults | [no page yet](/wiki/datasets/) |

**Sample.** Monthly data, January 1999 to December 2022. For the PEPP
announcement, the estimation window is two trading days (March 18-20, 2020).

## When to read the full paper

Read the original if you are:

- Modeling the term structure of sovereign spreads in the euro area and need
  a tractable affine framework with credit risk.
- Studying how ECB asset purchase programs (APP, PEPP) transmit to yields in
  heterogeneous monetary unions via the default risk channel.
- Seeking the yield decomposition into expectations, term premium, expected
  default loss, and credit risk premium (Proposition 1, Table II for numbers).
- Interested in the identification strategy: Germany's negligible default risk
  identifies risk aversion from the term premium; Italy adds the spread to
  identify the long-run default rate and credit risk premium (pp. 2392, 2417-2421).
- Working on fiscal-monetary interactions with rollover crises, building on
  Calvo (1988) and Cole and Kehoe (2000) in a dynamic ATSM setting.

The key quantitative tables are Table I (estimated parameters), Table II
(10Y yield decomposition and Sharpe ratios), Table III (robustness), and
Table IV (conditional Sharpe ratios around the PEPP). Figures 4-9 document
model fit to long-run moments, the PEPP announcement, and the pandemic shock.

## Attribution and rights

Costain, James, Galo Nuno, and Carlos Thomas. "The Term Structure of Interest
Rates in a Heterogeneous Monetary Union." *The Journal of Finance* 80(4),
August 2025, 2389-2434. DOI: 10.1111/jofi.13463.

Published under Wiley VOR terms (paywalled). Rights held by the American
Finance Association. This page contains only distilled extracts (tables,
equations, and findings with locators). LLM-distilled; not human-verified;
not reproduced.
