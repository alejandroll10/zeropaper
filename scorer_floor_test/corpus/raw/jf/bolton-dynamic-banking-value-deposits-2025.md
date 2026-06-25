---
title: "Dynamic Banking and the Value of Deposits: Bolton, Li, Wang & Yang (2025)"
description: >-
  Distilled: A continuous-time structural model shows that banks cannot fully
  control deposit flows under leverage regulation, so deposit inflows can hurt
  shareholder value when equity capital is low, the deposit marginal q turns
  negative, and lending falls. J. Finance 2025, paywalled. Six core results
  with source locators, the model (HJB with deposit-dynamics state variable),
  and the method (ODE solution with boundary conditions).
sidebar:
  label: Bolton-Li-Wang-Yang 2025
  order: 1
tags: [paper-summary, banking, bank-regulation, deposits, leverage, monetary-policy,
       structural, peer-reviewed, unreplicated]
paper:
  authors: Patrick Bolton, Ye Li, Neng Wang, Jinqiang Yang
  authorList:
    - { family: Bolton, given: Patrick, orcid: "0000-0002-3401-553X", affiliation: Imperial College Business School, CEPR, and ECGI }
    - { family: Li, given: Ye, orcid: "0000-0001-8492-1808", affiliation: University of Washington (Foster School of Business) }
    - { family: Wang, given: Neng, orcid: "0000-0001-9854-8194", affiliation: Cheung Kong Graduate School of Business }
    - { family: Yang, given: Jinqiang, affiliation: Shanghai University of Finance and Economics }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2063–2105
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13454
  jel:
    codes: [G21, G28, E43]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Banking stability, regulation, efficiency", "Economic theories and models", "Global Financial Crisis and Policies"]
  dataAccess: public
  outcome:
    - bank shareholder value (deposit marginal q)
    - optimal deposit rate
    - optimal lending (loan-to-capital ratio)
    - equity issuance frequency and timing
  outcomeClass: [bank-funding, credit-supply, firm-financing]
  license: >-
    Wiley VOR terms and conditions (confirmed via Crossref DOI metadata:
    content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    start 2025-04-23); paywalled, not CC.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley publisher site, 2026-06-05)"
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 10

  methods:
    role: theory
    family: structural
    buildsFrom: [hjb-optimal-stopping, value-function-iteration]
  contributionType: [new-theory]
  mechanisms: [intermediary-constraint, financial-constraint, liquidity]

  scope:
    region: theoretical
    assetClass: bank balance sheet (loans, deposits, equity, wholesale bonds)

  relatesTo:
    - { cite: "Drechsler, Savov & Schnabl (2017)", relation: builds-on, note: "deposit-flow sensitivity to the deposit rate and deposit spread r-i as a key profitability measure" }
    - { cite: "Drechsler, Savov & Schnabl (2021)", relation: builds-on, note: "deposits as long-duration sticky liabilities without interest-rate risk; the paper incorporates deposit-flow risk instead" }
    - { cite: "Leland (1994a)", relation: builds-on, note: "dynamic capital structure with diffusion asset risk; extended here to include stochastic deposit liabilities" }
    - { cite: "Merton (1969)", relation: builds-on, note: "portfolio choice with risky assets; bank's lending problem is cast as a portfolio problem given long-term funds K+X" }
    - { cite: "Diamond & Dybvig (1983)", relation: builds-on, note: "departure: bank runs not modeled; deposit inflow risk (not outflow) is the focus under equity issuance costs" }
    - { cite: "Brunnermeier & Sannikov (2014)", relation: builds-on, note: "macro-finance portfolio approach; this paper adds deposits as a state variable alongside equity" }

  openQuestions:
    - "Introducing interest-rate risk by allowing banks to hold long-term debt; SVB episode illustrates the relevance (p. 2099)."
    - "Generating sharp changes in deposit marginal q for both large inflows and large outflows by making loans illiquid, adding a new state variable (ratio of liquid assets to deposits) and requiring a PDE for the value function (p. 2099-2100)."
    - "Incorporating the banking model into macroeconomic models of safe asset demand where r is endogenous, so that banks' demand for risk-free bonds drives down r in general equilibrium (p. 2100)."

  replicationCode:
    status: available

  findings:
    - ref: R1
      outcome: deposit marginal q (marginal value of deposits to shareholders)
      metric: level
      value: "positive and ~0.11 for 80% of stationary distribution of k; turns sharply negative (down to -0.18) as k approaches the equity issuance lower boundary"
      direction: mixed
      vsBenchmark: "baseline r=1%, Figure 4 Panel A / Figure 5 Panel A (pp. 2087-2088)"
    - ref: R2
      outcome: optimal lending (loan-to-capital ratio A/K)
      metric: level
      value: "A/K rises from ~0 near the lower boundary k to ~14 (capital requirement limit) as k increases; capital requirement binds about 7% of the time"
      direction: positive
      vsBenchmark: "Figure 1 Panel B / Figure 3 Panel B (pp. 2084-2086); A/K under r=2% exceeds r=1% at all k (Figure 9 Panel B, p. 2094)"
    - ref: R3
      outcome: marginal value of equity capital v'(k)
      metric: level
      value: "v'(k) is ~7 near k=underbar (equity issuance boundary, 0.052); between 1.022 and 1.029 for 25% of stationary distribution; above 1.08 for 5.5% of the time"
      direction: positive
      vsBenchmark: "Figure 1 Panel A / Figure 3 Panel A (pp. 2084-2086); rises sharply near equity issuance boundary"
    - ref: R4
      outcome: optimal lending under SLR relaxation (5% to 4%)
      metric: level
      value: "A/K is higher immediately (short-run) under 4% SLR; but long-run A/K distribution is lower under 4% SLR than 5% SLR (Panel B, Figure 7 crosses below Panel B solid line)"
      direction: mixed
      vsBenchmark: "Figure 7 Panel A and B (p. 2091); relaxing SLR raises short-run lending but reduces long-run risk-taking per unit of equity"
    - ref: R5
      outcome: deposit marginal q under SLR relaxation
      metric: level
      value: "SLR relaxation (5% to 4%) raises deposit marginal q for low-k banks; deposit marginal q turns even more negative near the new (lower) equity issuance boundary"
      direction: mixed
      vsBenchmark: "Figure 8 Panel A (p. 2092-2093); deposit rate rises after SLR relaxation (Panel B)"
    - ref: R6
      outcome: optimal lending in low-interest-rate environment (r=1% vs r=2%)
      metric: level
      value: "Under r=1% the bank reduces lending per unit of equity (A/K lower at all c.d.f.(k)) relative to r=2%; deposit rate is less than 0.8 percentage points higher under r=2% than r=1%"
      direction: negative
      vsBenchmark: "Figure 9 Panel A and B (p. 2094); lower r reduces flexibility to manage deposit risk so bank reduces A/K"

  resultType: new-finding

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full PDF read (pp. 2063-2105); six results extracted from a pure-theory paper with numerical calibration. Not human-verified. Not reproduced. Replication code is referenced at the end of the paper but has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; two errors fixed: (1) eq. 13 SLR boundary denominator corrected from ξ_L^{-1}-1 to 1-ξ_L^{-1} (sign flip); (2) equity issuance cost formula corrected from garbled dH=ψ_0 dF+ψ_1 X dF/X to dH=ψ_1 dF+ψ_0 X dt per PDF p. 2075. All six Core-results rows, all quantitative magnitudes, and all remaining equations verified correct."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13454
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, start=2025-04-23; paywalled Wiley VOR terms, not CC"
  rightsSignalConflict: false
---

**What this is.** The paper's core model, its key propositions on the value and management of bank deposits under leverage regulation, and the numerical findings: enough to know what it derives and why, without reading all 43 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13454).

## TL;DR

Bolton, Li, Wang, and Yang (2025) propose a continuous-time structural model of a bank that maximizes risk-neutral shareholder value while facing two uncontrollable random processes: asset return shocks and deposit flow shocks. The central state variable is the ratio of equity capital to deposits, $$k_t = K_t / X_t$$. Because depositors freely move money in and out, the bank cannot perfectly control $$X_t$$, distinguishing it from nondepository intermediaries and nonfinancial firms. Under equity issuance costs and leverage regulations (the supplementary leverage ratio, SLR), deposit inflows can lower $$k_t$$ and push it toward a costly equity issuance boundary. As a result, the marginal value of deposits (the deposit marginal $$q$$) turns sharply negative when $$k_t$$ is low, the bank reduces its deposit rate toward the zero lower bound (ZLB), and lending falls rather than rises. The model relates to Merton (1969) in casting the bank's problem as a portfolio choice, extends the dynamic capital structure approach of Leland (1994a) and Brunnermeier and Sannikov (2014) to include stochastic deposit liabilities, and departs from Diamond and Dybvig (1983) by focusing on deposit inflow risk (not runs) under equity issuance costs. Unlike Drechsler, Savov, and Schnabl (2021), who treat deposits as long-duration liabilities without interest-rate risk, the paper incorporates deposit flow risk as the central friction. The model explains why (i) banks did not expand lending during the COVID-19 deposit surge, (ii) the SLR relaxation stimulated lending only in the short run, (iii) a low risk-free rate compresses banks' deposit management flexibility, and (iv) the deposit rate and loan growth co-move positively with bank capitalization.

## Core results

Magnitudes and qualitative characterizations are as reported from the numerical solution. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Deposit marginal q is positive for well-capitalized banks but turns sharply negative near the equity issuance boundary | Figure 4 Panel A, p. 2087; Figure 5 Panel A, p. 2088 | Deposit marginal q ~0.11 for 80% of stationary distribution of k; drops to ~-0.18 as k approaches the equity issuance lower boundary (~0.052) |
| R2 | Loan-to-capital ratio is procyclical in bank capitalization; capital requirement binds about 7% of the time | Figure 1 Panel B, p. 2084; Figure 3 Panel B, p. 2086 | A/K rises from ~0 at the lower boundary to ~14 (capital requirement ceiling) as k increases; capital requirement binds 7% of the time; SLR binds far more frequently |
| R3 | Marginal value of equity capital is sharply elevated near the equity issuance boundary, casting a long shadow | Figure 1 Panel A, p. 2084; Figure 3 Panel A, p. 2086 | v'(k) reaches ~7 at k = underbar (0.052); stays between 1.022 and 1.029 for 25% of stationary time; exceeds 1.08 for 5.5% of stationary time |
| R4 | Relaxing the SLR raises lending immediately but reduces long-run risk-taking per unit of equity, contrary to conventional wisdom | Figure 7 Panel A and B, p. 2091 | Under 4% SLR, A/K is higher in Panel A (given k) but lower in Panel B (against stationary c.d.f.) than under 5% SLR; tightening SLR generates reach-for-yield over the long run |
| R5 | Relaxing the SLR raises deposit marginal q and deposit rates, stimulating deposit-taking; but deposit marginal q becomes more negative near the new lower equity issuance boundary | Figure 8 Panel A and B, pp. 2092-2093 | Deposit rate jumps up under 4% SLR; region where ZLB binds shrinks; deposit marginal q is negative before the regulatory change, turns even more negative near the new lower boundary |
| R6 | Lower risk-free rate reduces bank lending (counterintuitive): bank reduces A/K because it has less room to manage deposit risk via the deposit spread | Figure 9 Panel A and B, p. 2094 | At r=1% vs r=2%, the deposit rate is less than 0.8 pp higher under r=2%; A/K is lower at all quantiles of k under r=1% than r=2% |

**Overall (paper's conclusion).** Deposit-taking is a double-edged sword: it lowers funding costs in normal times, but deposit inflows under leverage regulation drive up leverage and can trigger costly equity issuance. When the bank is close to its equity issuance boundary, it reduces deposit rates to the ZLB, cuts lending, and holds safe assets. Banks in low-interest-rate environments have less flexibility to control deposit flows, amplifying this mechanism and explaining patterns observed after the Global Financial Crisis and the COVID-19 pandemic.

## Theory / model

The model features a single bank maximizing risk-neutral shareholder value. Two state variables govern the bank's balance sheet: the deposit stock $$X_t$$ and equity capital $$K_t$$. The bank controls five variables: the risky loan book $$A_t$$, bond issuance $$B_t$$, deposit rate $$i_t$$, dividends $$dU_t$$, and equity issuance $$dF_t$$. The resource constraint is $$A_t = K_t + X_t + B_t$$ (p. 2072, eq. 3).

**Deposit dynamics** (p. 2070, eq. 1): The deposit stock evolves as a diffusion process partially controlled by the bank via the deposit rate:

$$
dX_t = -X_t(\delta_X \, dt - \sigma_X \, d\mathcal{W}_t^X) + X_t \, n(i_t) \, dt \tag{1}
$$

where $$\mathcal{W}_t^X$$ is a standard Brownian motion, $$\delta_X$$ is the drift of payment flows out of the bank, $$\sigma_X$$ is the deposit flow volatility, and $$n(i_t) = \omega_0 + \omega_1(i_t - r)$$ is the deposit demand function (eq. 21, p. 2079): raising the deposit rate above the risk-free rate $$r$$ attracts deposits, lowering it repels them. The deposit rate is bounded below by zero: $$i_t \geq 0$$.

**Bank equity dynamics** (p. 2072, eq. 2): Bank equity evolves as

$$
dK_t = A_t \left[(r + \alpha_A) \, dt + \sigma_A \, d\mathcal{W}_t^A\right] - B_t r \, dt - X_t i_t \, dt - C(n(i_t), X_t) \, dt - dU_t + dF_t \tag{2}
$$

where $$\alpha_A$$ is the bank's excess return on lending, $$\sigma_A$$ is asset return volatility, $$\phi \, dt$$ is the instantaneous covariance between deposit and asset shocks ($$d\mathcal{W}^X$$ and $$d\mathcal{W}^A$$), and $$C(n(i_t), X_t) = c(n(i_t)) X_t$$ is the cost of maintaining the deposit franchise.

**Homogeneity and the HJB equation.** The functional forms imply the shareholder value function is homogeneous of degree one: $$V(X, K) = v(k) X$$ where $$k \equiv K/X$$ (eq. 9, p. 2075). Within the dividend/issuance boundaries $$[\underline{k}, \overline{k}]$$ the HJB equation for the scaled value function $$v(k)$$ is (eq. 10, p. 2075):

$$
\rho v(k) = \max_{\pi^A, i} \left\{ [v(k) - v'(k)k]\left[-\delta_X + n(i)\right] + \tfrac{1}{2} v''(k) k^2 \sigma_X^2 + v'(k)(1+k)\left(r + \pi^A \alpha_A\right) + \tfrac{1}{2} v''(k)(1+k)^2 (\pi^A \sigma_A)^2 - v'(k)[i + c(n(i))] - v''(k) k(1+k) \pi^A \sigma_A \sigma_X \phi \right\} \tag{10}
$$

where $$\pi^A = A/(X+K)$$ is the portfolio weight on risky assets, $$\rho > r$$ is the shareholders' discount rate. The deposit marginal $$q$$ equals $$V_X(X,K) = v(k) - v'(k)k$$ and the equity marginal $$q$$ equals $$V_K(X,K) = v'(k)$$.

**Regulatory constraints.** The capital requirement (eq. 6, p. 2073) restricts the risky asset-to-equity ratio: $$A_t / K_t \leq \xi_K$$ (baseline $$\xi_K = 14.3$$). The supplementary leverage ratio (SLR, eq. 7-8, pp. 2073-2076) imposes a lower bound on $$k$$:

$$
k \geq \underline{k} \equiv \frac{1}{1 - \xi_L^{-1}} - 1 \tag{13}
$$

with $$\xi_L = 20$$ in the baseline (implying $$\underline{k} \approx 0.05$$). This is the equity issuance boundary; hitting it requires the bank to raise costly external equity.

**Equity issuance costs.** Equity issuance costs are $$dH_t = \psi_1 dF_t + \psi_0 X_t \, dt$$, where $$\psi_1 = 5\%$$ is the proportional cost per dollar issued and $$\psi_0 = 0.14\%$$ is a fixed flow cost proportional to the deposit stock size (governing how frequently equity issuance is triggered). The bank maximizes (eq. 5, p. 2073):

$$
V_0 = \max_{\{A,B,i,U,F\}} \mathbb{E}\left[\int_{t=0}^{\tau} e^{-\rho t}(dU_t - dF_t - dH_t)\right] \tag{5}
$$

where $$\tau$$ is the stochastic closing time (when regulatory constraints are violated).

## Method

The model is solved numerically as an ODE boundary value problem. The homogeneity reduction to the one-dimensional $$v(k)$$ transforms the two-dimensional HJB into the ordinary differential equation (10), which is solved over the interval $$[\underline{k}, \overline{k}]$$ using shooting/iteration.

**Optimal risky asset allocation.** The first-order condition from (10) for $$\pi^A$$ yields the optimal loan-to-capital ratio (eq. 18, p. 2077):

$$
\frac{A}{K} = \frac{\alpha_A}{\gamma(k) \sigma_A^2} + \frac{\sigma_X}{\sigma_A} \phi \tag{18}
$$

where $$\gamma(k) \equiv -v''(k)k / v'(k)$$ is the bank's endogenous relative risk-aversion (eq. 19, p. 2078), derived from the curvature of the value function. Even though shareholders are risk-neutral, $$\gamma(k) > 0$$ because equity issuance costs make the bank endogenously risk-averse. The hedging term $$(\sigma_X / \sigma_A)\phi$$ reflects the deposit risk as a natural hedge for the asset-side shock when $$\phi > 0$$.

**Optimal deposit rate.** The first-order condition for $$i$$ from (10) yields the q-theory formula for the optimal deposit rate (eq. 23, p. 2079):

$$
i = r + \frac{V_X(X,K)/V_K(X,K) - 1/\omega_1}{\omega_1 \theta} - \frac{\omega_0}{\omega_1} = r + \frac{(v(k) - v'(k)k)/v'(k) - 1/\omega_1}{\omega_1 \theta} - \frac{\omega_0}{\omega_1} \tag{23}
$$

The deposit rate rises in the ratio of deposit marginal q to equity marginal q. When $$V_X / V_K$$ is high (deposits are more valuable than equity), the bank sets a high $$i_t$$ to attract deposits. When $$V_X$$ falls near $$\underline{k}$$, the bank reduces $$i_t$$ toward zero.

**Boundary conditions.** At the equity issuance boundary $$\underline{k}$$: value-matching $$v(\underline{k} + m) = 1 + \psi_1$$ (eq. 14) and smooth-pasting $$v'(\underline{k}) = 1 + \psi_1$$. At the dividend boundary $$\overline{k}$$: $$v'(\overline{k}) = 1$$ (eq. 16) and supercontact condition $$v''(\overline{k}) = 0$$ (eq. 17, p. 2077). The paper builds on `hjb-optimal-stopping` techniques from Leland (1994a) and `value-function-iteration` for the numerical ODE solution.

## Empirical specifications

This is a pure-theory paper with a calibrated numerical solution; there are no econometric regressions or estimated equations. The authors calibrate the model to match empirical moments of U.S. banking data (Table I, p. 2082), including:

- Average return on assets of 1.04% (matching $$\alpha_A = 0.2\%$$ at baseline parameters, FRED data).
- Average deposit-to-assets ratio of 92% (matching $$\phi = 0.8$$, consistent with Drechsler, Savov, and Schnabl (2017)).
- Average equity issuance frequency of once every four years (matching $$\psi_0 = 0.14\%$$, consistent with Baron (2020)).
- Average bank deposit growth rate of 1.9% per quarter (matching $$\omega_0 = 0.06$$, consistent with Lin (2019)).
- Average return on equity of 11% (matching $$\theta = 0.5$$).

**Comparative statics and applications.** The paper analyzes two applications numerically:

1. **Leverage regulation (Section IV.A):** Compares model solutions under SLR of 5% vs. 4%, tracing the immediate (given $$k$$) and long-run (stationary distribution of $$k$$) effects on $$A/K$$, deposit marginal $$q$$, deposit rate, and equity issuance frequency (Figures 7 and 8, pp. 2091-2093).

2. **Low-interest-rate environment (Section IV.B):** Compares model solutions under $$r = 1\%$$ vs. $$r = 2\%$$ (adjusting $$\rho$$ by 1% to control for the wedge $$\rho - r$$), tracing effects on deposit rate and $$A/K$$ against the stationary c.d.f. of $$k$$ (Figure 9, p. 2094). Drechsler, Savov, and Schnabl (2017) document that a lower $$r$$ compresses the deposit spread $$r - i$$ and constrains banks; this paper shows the mechanism via imperfect deposit flow control.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Federal Reserve Economic Data (FRED) | Calibration targets: average Fed funds rate, return on assets of U.S. banks | [FRED](/wiki/datasets/fred/) |

The paper is theoretical with a calibrated numerical solution. All key moments (average ROA 1.04%, deposit-to-asset ratio 92%, equity issuance frequency, deposit growth 1.9%/quarter) are cited from published empirical papers (Baron (2020), Lin (2019), Drechsler, Savov, and Schnabl (2017)) and FRED aggregate statistics; no proprietary microdata are used.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13454) if you are: (i) building a model of bank balance-sheet management where deposit risk matters alongside equity issuance costs; (ii) analyzing the short-run vs. long-run effects of leverage regulation (SLR) on bank lending and risk-taking; (iii) studying why low interest rates reduce bank lending (the deposit-management-flexibility channel); (iv) studying the COVID-19 episode of massive deposit inflows and the SLR exemption. The Internet Appendix contains the extension with reserve requirements, the jump-risk model, and the negative deposit rate case.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4), August 2025. Published by Wiley on behalf of the American Finance Association. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The publisher licence is Wiley VOR terms (paywalled); extract-only reproduction applies.

> Bolton, Patrick, Ye Li, Neng Wang, and Jinqiang Yang.
> "Dynamic Banking and the Value of Deposits."
> *The Journal of Finance* 80, no. 4 (August 2025): 2063–2105.
> DOI: [10.1111/jofi.13454](https://doi.org/10.1111/jofi.13454).
> © 2025 the American Finance Association.
> This page is an extract-only distillation by the Institute for Automated Research; no reproduction of the full text.
