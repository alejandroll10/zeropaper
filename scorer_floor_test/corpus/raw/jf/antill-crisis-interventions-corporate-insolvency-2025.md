---
title: "Crisis Interventions in Corporate Insolvency: Antill & Clayton (2025)"
description: >-
  Distilled: A general-equilibrium model shows that optimal insolvency
  interventions can favor either liquidation or reorganization depending on
  which externality dominates: a fire-sale externality (fewer liquidations
  optimal) or a collateral externality (more liquidations optimal). J. Finance
  2025, paywalled. Six core results with source locators, the model, and
  the propositions with their equations.
sidebar:
  label: Antill-Clayton 2025
  order: 1
tags: [paper-summary, corporate-finance, insolvency, bankruptcy, financial-intermediation,
       structural, peer-reviewed, unreplicated]
paper:
  authors: Samuel Antill, Christopher Clayton
  authorList:
    - { family: Antill, given: Samuel, affiliation: Harvard Business School }
    - { family: Clayton, given: Christopher, orcid: "0000-0002-0900-0686", affiliation: Yale School of Management }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 875-910
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13421
  jel:
    codes: [G33, G21, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Corporate Insolvency and Governance', 'Banking stability, regulation, efficiency', 'Corporate Finance and Governance']
  dataAccess: licensed-commercial
  outcome:
    - socially optimal liquidation threshold for insolvent firms
    - direction and magnitude of optimal liquidation tax or subsidy
    - welfare effects of macroprudential regulation, bailouts, and debt subordination
  outcomeClass: [firm-financing, credit-supply]
  license: >-
    Wiley VoR terms (http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-01-30); not CC; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site, 2026-06-06)
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 3
  methods:
    role: theory
    family: structural
    buildsFrom: [principal-agent, dynamic-general-equilibrium]
  contributionType: [new-theory, new-fact]
  mechanisms: [collateral, financial-constraint, fire-sale-externality]
  scope:
    region: US, Japan (comparative statics applied to historical crises)
    assetClass: corporate loans, insolvent firm assets
    dataType: [accounting, administrative]
    granularity: [aggregate, firm]
    n: "Table II: country-year aggregate statistics, Japan 1990-2005 and US 2020-2023"
  findings:
    - ref: R1
      outcome: socially optimal liquidation threshold for insolvent firms
      metric: coefficient
      value: "V* = delta_*(gamma + c) - (delta_* - 1) xi_gamma * gamma (Prop. 2, eq. 17, p. 890); V* >= V_P when fire-sale dominates; V* <= V_P when collateral externality dominates"
      direction: mixed
      vsBenchmark: privately optimal threshold V_P = delta_P(gamma + c) (Prop. 1, eq. 13, p. 888)
    - ref: R2
      outcome: direction and magnitude of optimal liquidation tax or subsidy
      metric: coefficient
      value: "tau = (gamma + c) delta_P (1 - M) + (M delta_P - 1) xi_gamma * gamma (Prop. 3, eq. 19, p. 893); tau < 0 (subsidy) when higher d_0, c, t, or lower gamma"
      direction: mixed
      vsBenchmark: "Decentralizes social optimum; sign flips with which externality dominates"
    - ref: R3
      outcome: socially optimal liquidation threshold for insolvent firms
      metric: coefficient
      value: "Japan crisis: all four comparative-static factors (higher d_0 = 126.8% vs 80.9% GDP, lower EBIT/Rev = 5.5% vs 14%, higher bank share = 83.5% vs 38%, lower GDP growth = 0.1% vs 1.8%) point to liquidation subsidies optimal for Japan vs reorganization subsidies for US (Table II, p. 905)"
      direction: negative
      vsBenchmark: "US COVID crisis features higher profitability, lower leverage, lower bank lending share, higher growth - model predicts reorganization subsidies for US"
    - ref: R4
      outcome: welfare effects of macroprudential regulation, bailouts, and debt subordination
      metric: coefficient
      value: "Optimal bank debt tax = tau_0^b = (M-1) delta_P (Prop. 5, p. 897); complementary to liquidation subsidies; both target collateral externality through M"
      direction: positive
      vsBenchmark: "Macroprudential regulation targets collateral externality only, not fire-sale; bailouts to banks weakly dominate bailouts to firms (Prop. 6, p. 899)"
    - ref: R5
      outcome: welfare effects of macroprudential regulation, bailouts, and debt subordination
      metric: coefficient
      value: "Marginal social welfare of bailout: delta_* to banks or distressed firms; (1 - phi*t/(1-phi)) * delta_* to solvent firms (Prop. 6, p. 899); banks weakly dominate solvent firms"
      direction: positive
      vsBenchmark: "Bailout to bank = bailout to distressed firm via collateral multiplier M; targeted to secured creditors in heterogeneous-banks extension"
    - ref: R6
      outcome: socially optimal liquidation threshold for insolvent firms
      metric: coefficient
      value: "With heterogeneous banks (phi_1 < phi_2): V_* = delta_*^1 c + delta_*^2 gamma - (delta_*^2 - 1) xi_gamma * gamma (eq. 23, p. 901); optimal seniority bifurcates banks into secured (high-phi, liquidate) and distressed (low-phi, reorganize) creditors"
      direction: mixed
      vsBenchmark: "Heterogeneous collateral constraints shift optimum toward reorganization relative to homogeneous case; seniority structure substitutes in part for direct intervention"
  resultType: new-finding
  relatesTo:
    - { cite: "Shleifer and Vishny (1992)", doi: '10.1111/j.1540-6261.1992.tb04661.x', relation: builds-on, note: "Fire-sale externality as the motive for planners to avoid liquidations; their mechanism is one of two externalities in this model" }
    - { cite: "Corbae and D'Erasmo (2021a)", doi: '10.3982/ecta16930', relation: extends, note: "GE model with both reorganization and liquidation in bankruptcy, but without collateral constraints or fire-sale externalities" }
    - { cite: "Corbae and D'Erasmo (2021b)", relation: extends, note: "Constrained banking sector GE model studying government interventions, but without nonfinancial corporate insolvency" }
    - { cite: "Diamond (1984)", doi: '10.2307/2297430', relation: builds-on, note: "Banks' comparative advantage in firm monitoring, modeled via the transaction cost t for household-firm lending" }
    - { cite: "Caballero, Hoshi, and Kashyap (2008)", doi: '10.1257/aer.98.5.1943', relation: tests, note: "Zombie lending and depressed restructuring in Japan; model comparative statics match Japan vs US crisis empirical patterns" }
    - { cite: "Philippon (2021)", relation: extends, note: "Mechanism-design approach preventing inefficient liquidations without blanket bailouts; this paper adds fire-sale and collateral externalities" }
  openQuestions:
    - "Static model precludes rigorous analysis of temporary versus permanent shocks; future work should model dynamic state variables to study multi-period policy effects (p. 907)."
    - "Future liquidation values could endogenously determine bank asset values, opening additional channels through which liquidations affect welfare in a dynamic framework (p. 907)."
    - "Two testable implications (bank collateral constraints bind when borrowing rates are high; high-phi banks more likely to liquidate a given asset) await empirical validation (pp. 906-907)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 875-910 plus Table II, Propositions 1-6); six results extracted from the PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all six core-result locators and magnitudes confirmed correct; all equations (eqs. 1-23, Props. 1-6) verified term-by-term; dataAccess corrected from public to licensed-commercial (Compustat used via WRDS)." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13421", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-30; not CC, paywalled" }
---

**What this is.** The paper's core propositions, the GE model it builds, and the comparative statics behind its policy conclusions: enough to know what it found and how, without reading all 36 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13421).

## TL;DR

Antill and Clayton (2025) build a two-period general-equilibrium model with collateral-constrained banks to study the optimal resolution of insolvent firms. The model features two externalities that work in opposite directions: (i) a fire-sale externality following Shleifer and Vishny (1992) (more liquidations depress asset prices, reducing all banks' recovery) and (ii) a collateral externality (reorganizations tie up bank balance sheets, congesting lending capacity and raising borrowing rates). Banks have a monitoring advantage over households in firm lending, as in Diamond (1984). The paper shows that socially optimal policy can encourage either more or fewer liquidations relative to the private equilibrium depending on which externality dominates. A simple uniform tax or subsidy on liquidations decentralizes the optimum without requiring the planner to know individual firms' long-run values. The framework extends and complements earlier GE insolvency models of Corbae and D'Erasmo (2021a) and Corbae and D'Erasmo (2021b), and the mechanism-design approach of Philippon (2021). Applied to aggregate statistics for Japan's nonperforming loan crisis (studied empirically by Caballero, Hoshi, and Kashyap (2008)) and the U.S. COVID crisis, the model predicts that optimal policy would have subsidized liquidation in Japan and subsidized reorganization in the United States, consistent with observed policy responses.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | The socially optimal liquidation rule is a threshold rule; its threshold differs from the privately optimal threshold in two ways: (i) a fire-sale externality pushes the social threshold below the private threshold (fewer liquidations) and (ii) a collateral externality pushes it above (more liquidations). | Prop. 2, eq. 17, p. 890 | $$V_* = \delta_*(\gamma + c) - (\delta_* - 1)\xi_\gamma\gamma$$; relative to $$V_P = \delta_P(\gamma + c)$$ (Prop. 1) |
| R2 | A uniform liquidation tax $$\tau$$ decentralizes the social optimum; optimal intervention favors liquidation subsidies ($$\tau < 0$$) when corporate distress is high (large $$c$$, $$d_0$$), bank monitoring advantage large (high $$t$$), or fire-sale prices are low (low $$\gamma$$). Lower fire-sale prices can sometimes call for more, not fewer, liquidations. | Prop. 3-4, eqs. 19-20, pp. 893-894 | $$\tau = (\gamma + c)\delta_P(1-M) + (M\delta_P - 1)\xi_\gamma\gamma$$; $$\tau < 0$$ if $$\tilde\xi_\gamma < (1 + c/\gamma)\phi t/(p\bar g + \bar u)(1 - \phi(1+t))pd_0$$ |
| R3 | Relative to the U.S. COVID crisis, Japan's nonperforming-loan crisis featured higher corporate leverage (126.8% vs 80.9% of GDP), lower firm profitability (EBIT/Rev = 5.5% vs 14%), higher bank lending share (83.5% vs 38%), and lower GDP growth (0.1% vs 1.8%); all four comparative-static factors imply liquidation subsidies were optimal for Japan and reorganization subsidies for the United States. | Table II, pp. 904-906; §VI | Model qualitative comparative statics applied to Table II statistics |
| R4 | Ex ante macroprudential regulation (a debt tax on banks of $$\tau_0^b = (M-1)\delta_P$$) complements ex post liquidation subsidies: both target the collateral externality. Macroprudential regulation does NOT directly target the fire-sale externality (Envelope Theorem). | Prop. 5, p. 897 | Socially optimal equity satisfies $$\Psi'(A_0) = \delta_*$$; debt tax $$\tau_0^b = (M-1)\delta_P > 0$$ |
| R5 | Bailouts to banks (weakly) dominate bailouts to solvent firms in welfare terms because banks obtain an additional collateral multiplier benefit; bailouts to distressed firms equal bailouts to banks conditional on an insolvency rule. | Prop. 6, pp. 899-900 | Marginal welfare: $$\delta_*$$ for banks or distressed firms; $$(1 - \phi t/(1-\phi))\delta_*$$ for solvent firms |
| R6 | With heterogeneous banks (varying collateral haircuts $$\phi_b$$), the optimal seniority structure bifurcates banks: high-$$\phi$$ banks become secured creditors (liquidate and lend) while low-$$\phi$$ banks become distressed lenders (reorganize); bailouts should go to secured creditors. | §IV.D, eq. 23, p. 901 | $$V_* = \delta_*^1 c + \delta_*^2\gamma - (\delta_*^2 - 1)\xi_\gamma\gamma$$ with $$\delta_*^2 > \delta_*^1$$ |

**Overall (paper's conclusion).** Optimal crisis interventions in insolvency need not favor reorganization. When bank lending capacity is tight (the collateral externality dominates), subsidizing more liquidations improves welfare by freeing balance-sheet capacity for new lending to solvent firms. The optimal Pigouvian tax or subsidy is simple, uniform, and does not require firm-specific information. Macro-prudential regulation and bailouts are natural complements to insolvency interventions, but they target only the collateral externality, not the fire-sale externality; insolvency policy must handle both.

## Theory / model

The model has two dates (date one and date two) and four types of agents: firms, banks, arbitrageurs, and households (pp. 881-886).

**Firms.** A fraction $$p$$ of firms are solvent; each has a project worth $$v_S$$ at date two and an investment opportunity $$I_S$$. Solvent firms maximize date-two cash flows net of debt repayment (eq. 1, p. 883):

$$
\max_{I_S} \; g_S(I_S) - \frac{I_S}{Q_S} + v_S - d_0 \tag{1}
$$

with first-order condition $$g'_S(I_S) = Q_S^{-1}$$ (eq. 2, p. 883). A fraction $$1-p$$ of firms are insolvent with idiosyncratic long-run payoff $$v \in [\underline{v}, \bar{v}]$$ and a date-one operating loss $$c \geq 0$$ that must be paid to avoid liquidation.

**Banks.** Banks choose new household borrowing $$B_1$$, loans to solvent firms $$D_1$$, and an insolvency resolution rule $$\rho(v) \in [0,1]$$ (the probability that a firm with viability $$v$$ is liquidated). The bank budget constraint (eq. 3, p. 884) is:

$$
pD_1 + (1-p)\!\int (1-\rho(v))\,c\,f(v)\,dv \;\leq\; B_1 - b_0 + (1-p)\!\int \rho(v)\,\gamma\,f(v)\,dv \tag{3}
$$

An agency friction limits bank borrowing from households via a collateral constraint (eq. 4, p. 884):

$$
B_1 \leq \phi\,Q_B\;p\!\left(d_0 + \frac{D_1}{Q_S}\right) \tag{4}
$$

Banks maximize equity value (eq. 5, p. 885):

$$
\max_{B_1,D_1,\rho} \; p\!\left(\frac{D_1}{Q_S} + d_0\right) + (1-p)\!\int (1-\rho(v))\,v\,f(v)\,dv - \frac{B_1}{Q_B} \tag{5}
$$

**Households.** Households maximize utility over date-one consumption (eq. 7, p. 886):

$$
\max_{B_H, D_H} \; u\!\left(e - B_H - p(1+t)D_H\right) + \frac{B_H}{Q_B} + p\,\frac{D_H}{Q_S} \tag{7}
$$

with first-order conditions (eqs. 8-9, p. 887):

$$
u'\!\left(e - B_H - p(1+t)D_H\right) = \frac{1}{Q_B}, \qquad u'\!\left(\cdot\right) = \frac{1}{(1+t)Q_S} \tag{8-9}
$$

Market clearing requires $$D_1 + D_H = I_S$$, $$(1-p)\int \rho(v)f(v)dv = L$$, and $$B_H = B_1$$ (eqs. 10-12, p. 887).

**Social planner objective.** The planner maximizes aggregate utilitarian welfare (p. 890):

$$
p\bigl(g_S(I_S) + v_S\bigr) + (1-p)\!\int(1-\rho(v))\,v\,f(v)\,dv + a(L) - \gamma L + u\!\left(e - B_1 - p(1+t)D_H\right)
$$

## Method

**Private equilibrium: Proposition 1** (p. 888). In any competitive equilibrium, the bank's privately optimal liquidation rule is a threshold rule $$\rho(v) = \mathbf{1}(v \leq V_P)$$ where

$$
V_P = \delta_P\,(\gamma + c), \qquad \delta_P = \underbrace{\frac{1}{Q_S}}_{\text{Direct}} + \underbrace{\frac{\phi\frac{Q_B}{Q_S}}{1 - \phi\frac{Q_B}{Q_S}}}_{\text{Collateral Multiplier}} \times \underbrace{\left(\frac{1}{Q_S} - \frac{1}{Q_B}\right)}_{\text{Excess Return}} \tag{13-14}
$$

The effective return $$\delta_P$$ is the bank's marginal value of an additional date-one dollar, combining the direct return from lending and the shadow value of collateral (which lets banks borrow more from households).

**Social optimum: Proposition 2** (p. 890). The socially optimal liquidation rule is also a threshold rule $$\rho(v) = \mathbf{1}(v \leq V_*)$$ where

$$
V_* = \underbrace{\delta_*(\gamma + c)}_{\text{Weakly Bigger than } V_P} - \underbrace{(\delta_* - 1)\xi_\gamma\gamma}_{\text{Fire-Sale Externality} \geq 0} \tag{17}
$$

$$
M = \left[1 - \frac{\sigma_S\sigma_H\phi t}{\bigl(p(1+t)\sigma_H + \sigma_S\bigr)\bigl(1-\phi(1+t)\bigr)}\,pQ_B d_0\right]^{-1} \geq 1 \tag{18}
$$

The social effective return is $$\delta_* = M\delta_P$$, where $$M \geq 1$$ captures the collateral multiplier effect that banks do not internalize. The elasticity $$\xi_\gamma \equiv -(L/\gamma)\partial\gamma/\partial L \geq 0$$ measures how much each additional liquidation depresses the fire-sale price.

**Decentralization: Proposition 3** (p. 893). The liquidation tax or subsidy that decentralizes the social optimum is

$$
\tau = \underbrace{(\gamma + c)\delta_P(1-M)}_{\text{Subsidy component}} + \underbrace{(M\delta_P - 1)\xi_\gamma\gamma}_{\text{Tax component}} \tag{19}
$$

The subsidy component (negative) reflects the collateral externality; the tax component (positive) reflects the fire-sale externality. Under Assumption 1 (log production, log utility, iso-elastic arbitrageur demand), a sufficient condition for $$\tau < 0$$ (subsidize liquidations) is (eq. 20, p. 894):

$$
\tilde\xi_\gamma < \left(1 + \frac{c}{\gamma}\right)\frac{\phi t}{(p\bar g + \bar u)(1-\phi(1+t))}\,pd_0 \tag{20}
$$

## Empirical specifications

The paper does not run regressions. The empirical section (§VI, pp. 903-907) applies the model's comparative statics to aggregate statistics for two historical crises. The approach is as follows:

1. **Data.** Country-year-quarter panel from the IMF for corporate debt/GDP; country-quarter panel from FRED for bank lending and bond market shares; country-quarter GDP growth rates; firm-year Compustat North America and Compustat Global data for EBIT/Revenue ratios. Sample: Japan 1990-2005 and US 2020-2023 (Table II, p. 905).

2. **Mapping parameters to observables.** Each model parameter ($$d_0$$, $$c$$, $$t$$, $$\bar g$$) is mapped to an observable aggregate statistic. Proposition 4's sufficient condition for $$\tau < 0$$ (eq. 20) then yields a qualitative prediction about the direction of optimal intervention in each crisis.

3. **Four comparative-static dimensions.** (i) Corporate leverage $$d_0$$: Japan 126.8% of GDP vs. US 80.9%, so higher $$d_0$$ favors liquidation subsidies. (ii) Firm profitability (proxy for $$c$$): EBIT/Revenue Japan 5.5% vs. US 14%, so lower profitability (higher $$c$$) favors liquidation subsidies. (iii) Bank lending share (proxy for $$t$$): Japan 83.5% vs. US 38%, so higher $$t$$ favors liquidation subsidies. (iv) GDP growth (proxy for $$\bar g$$): Japan 0.1% vs. US 1.8%, so lower growth (more permanent shock) favors liquidation subsidies.

All four factors point in the same direction: the model predicts liquidation subsidies were optimal for Japan and reorganization subsidies for the United States, consistent with Japan's Takenaka Plan (which promoted liquidations of nonperforming loans) and U.S. COVID-era policies (which promoted reorganization).

The two testable empirical implications offered for future work are: (a) bank capital requirements bind more tightly when corporate interest rates are high; (b) banks with higher pledgeability $$\phi_b$$ are more likely to liquidate a given distressed firm (pp. 906-907).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| IMF International Financial Statistics | Country-year corporate debt/GDP for Japan (1990-2005) and US (2020-2023) | No page yet |
| FRED (Federal Reserve Bank of St. Louis) | Country-quarter bank lending and bond market shares; quarterly GDP growth rates | [FRED](/wiki/datasets/fred/) |
| Compustat North America | Firm-year EBIT and Revenue for large US firms (2020-2023) | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Compustat Global | Firm-year EBIT and Revenue for large Japanese firms (1990-2005) | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |

Sample: Japan crisis defined as 1990-2005 (Caballero, Hoshi, and Kashyap (2008)); US COVID crisis defined as March 2020 to May 2023.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13421) if you are: designing insolvency interventions and need the full set of propositions and Internet Appendix extensions (acquisitions by arbitrageurs or solvent firms, endogenous $$p$$, distinct liquidation deadweight losses); studying the interaction between macroprudential regulation and insolvency rules; or extending the framework to dynamic models with temporary versus permanent shocks. The locators above point to the exact propositions and equations.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pp. 875-910. DOI: [10.1111/jofi.13421](https://doi.org/10.1111/jofi.13421). Published by Wiley on behalf of the American Finance Association; paywalled (Wiley VoR terms; not CC). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract-only; the verbatim PDF is not hosted here.

> Antill, Samuel, and Christopher Clayton. "Crisis Interventions in Corporate Insolvency." *The Journal of Finance* 80, no. 2 (April 2025): 875-910. DOI: 10.1111/jofi.13421. © 2025 the American Finance Association.
