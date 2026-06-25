---
title: "Banks, Low Interest Rates, and Monetary Policy Transmission: Wang (2025)"
description: >-
  Distilled: A structural model of banks as dual credit and liquidity providers
  shows that secular declines in nominal interest rates compress deposit spreads,
  tighten banks' financial constraints, and reduce long-run bank credit supply,
  with loan spreads rising to offset lost deposit income. Cross-sectional bank-level
  evidence from U.S. Call Reports (2000-2014) confirms the mechanism. J. Finance
  2025, paywalled. Four core results with source locators, datasets used, the
  model, and the empirical specifications.
sidebar:
  label: Wang 2025
  order: 1
tags: [paper-summary, banking, monetary-policy, interest-rates, credit-supply,
       deposit-spreads, panel-regression, peer-reviewed, unreplicated,
       data:call-reports, data:fdic]
paper:
  authors: Olivier Wang
  authorList:
    - { family: Wang, given: Olivier, affiliation: New York University, Stern School of Business }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1379–1416
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13436
  jel:
    codes: [G21, E43, E52]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Banking stability, regulation, efficiency", "Monetary Policy and Economic Impact", "Economic Theory and Policy"]
  dataAccess: public
  outcome:
    - bank loan spreads
    - bank equity and retained earnings growth
    - bank loan growth
    - deposit spreads
  outcomeClass: [credit-supply, bank-funding, firm-financing]
  license: >-
    Wiley VOR terms and conditions (content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-03-09); paywalled, no CC licence detected in Crossref metadata.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley Online Library, 2026-06-06)
  redistribution: extract-only
  resultsCount: 4
  citedByCount: 13
  methods:
    role: both
    family: structural
    buildsFrom: [panel-regression, deposit-dynamics-diffusion]
    identification: natural-experiment
  contributionType: [new-theory, new-fact]
  mechanisms: [intermediary-constraint, liquidity, financial-constraint]
  scope:
    region: US
    assetClass: commercial bank loans and deposits
    period: 1984-01..2018-12
    frequency: quarterly
    dataType: [accounting, administrative]
    granularity: [firm, aggregate]
    n: "4,387 commercial banks (cross-sectional regressions 2000-2014); aggregate quarterly 1997Q2-2018Q2"
  findings:
    - ref: R1
      outcome: deposit spreads
      metric: coefficient
      value: "Loan spread widened by ~1 pp and deposit spread narrowed by ~1 pp between 1997Q2 and 2018Q2 (Figure 8, p. 1409); total loan-deposit spread stable at ~4-6%"
      direction: negative
      vsBenchmark: deposit spread fell ~1 pp while loan spread rose ~1 pp, sum stable
    - ref: R2
      outcome: bank equity and retained earnings growth
      metric: coefficient
      value: "delta(RetainedEarnings)/equity: 0.177*** (SE 0.027); delta(Equity)/equity: 0.340*** (SE 0.072) per unit of predicted liability spread decline (Table II, p. 1413)"
      direction: positive
      vsBenchmark: "low deposit-beta banks (more spread compression) had significantly lower retained earnings and equity growth 2000-2014"
    - ref: R3
      outcome: bank loan growth
      metric: coefficient
      value: "delta(Loans)/loans: 0.291*** (SE 0.067) per unit of predicted liability spread decline (Table II, p. 1413)"
      direction: positive
      vsBenchmark: "low deposit-beta banks had significantly lower loan growth 2000-2014"
    - ref: R4
      outcome: bank loan spreads
      metric: coefficient
      value: "-0.317*** (SE 0.045) per unit of predicted liability spread decline (Table II, p. 1413); i.e. a larger predicted decline in deposit spread predicts a larger increase in loan spreads"
      direction: negative
      vsBenchmark: "low deposit-beta banks saw larger increases in loan spreads 2000-2014"
  resultType: new-finding
  relatesTo:
    - { cite: "Drechsler, Savov & Schnabl (2017)", doi: '10.1093/qje/qjx019', relation: builds-on, note: "deposit spread beta framework and competition between money and deposits; this paper extends it to a GE model with credit frictions" }
    - { cite: "Drechsler, Savov & Schnabl (2021)", doi: '10.1111/jofi.13013', relation: extends, note: "stability of the NIM; this paper decomposes NIM into loan and deposit spreads and shows they offset each other" }
    - { cite: "Abadi, Brunnermeier & Koby (2023)", doi: '10.1257/aer.20190150', relation: contradicts, note: "in that paper money is irrelevant at positive rates and harmful lending effects require negative rates; here harmful effects arise at positive rates via the deposit spread channel" }
    - { cite: "Gertler & Kiyotaki (2010)", doi: '10.1016/b978-0-444-53238-1.00011-9', relation: builds-on, note: "workhorse bank model with limited pledgeability and leverage constraints adapted here to include dual lending and liquidity roles" }
    - { cite: "Di Tella & Kurlat (2021)", doi: '10.1257/mac.20180379', relation: cites, note: "banks' exposure to monetary policy with maturity mismatch and liquidity premia on deposits" }
  openQuestions:
    - "Whether deposit market power (Drechsler-Savov-Schnabl-style imperfect competition) and leverage constraints can be jointly embedded in a tractable GE model; the paper notes this as a valuable extension (p. 1392)."
    - "How allowing for lower risk weights on bonds (beyond the supplemental leverage ratio treatment) affects the constrained and unconstrained lending regimes (p. 1401)."
    - "The model's aggregate quantity predictions are difficult to reconcile with the data because U.S. bank assets grew relative to GDP during low-rate periods; the paper attributes this to a demand trend and suggests future work (pp. 1400-1401)."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1379-1416); four results extracted from the PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all four Core-results rows confirmed against Table II (p. 1413) and Figure 8 (p. 1409); all equations (eqs. 1, 2, 4, 7, 9, 13, 14), the leverage ratio (Lemma 1), calibration (Table I), replicating-portfolio formula, and cross-sectional regression (eq. 18) verified term-by-term; no errors found." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13436", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-09; no Creative Commons licence detected; paywalled" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the structural model it builds (banks as dual credit and liquidity providers), and the empirical specifications: enough to know what it found and how, without reading all 38 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13436).

## TL;DR

Olivier Wang develops a tractable general-equilibrium model in which commercial banks earn income from two distinct spreads: a loan spread (credit provision) and a deposit spread (liquidity provision). Because deposits compete with publicly issued money (cash/currency), lower nominal interest rates reduce the opportunity cost of holding cash, compress the deposit spread that banks earn, and reduce their retained earnings and equity. Once the nominal rate falls below a threshold $$\tilde{i}$$ (calibrated at roughly 8% in the baseline), the economy enters a "constrained lending regime" where lower deposit income tightens banks' leverage constraints, shrinks loan supply, and forces loan spreads to rise. The paper provides aggregate time-series evidence that the U.S. loan-deposit spread has been stable while its composition shifted (deposit spread down, loan spread up) and cross-sectional bank-level evidence that banks with stickier deposit rates (lower deposit beta, meaning more spread compression) experienced lower retained earnings, equity, loan growth, and higher loan spreads between 2000 and 2014.

## Core results

Magnitudes are as reported. `***`/`**`/`*` = 1%/5%/10%. Locators point to the source PDF (pages are printed page numbers 1379-1416).

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | The maturity-adjusted loan-deposit spread is stable but its composition shifted: deposit spread fell ~1 pp, loan spread rose ~1 pp over 1997-2018 | Figure 8, p. 1409 | Total spread ~4-6%, stable from 1997Q2-2018Q2; deposit spread fell from ~2% to ~1%; loan spread rose by ~1 pp |
| R2 | Banks with lower deposit-rate pass-through (lower "expense beta") experienced significantly lower retained earnings and equity growth 2000-2014 | Table II, p. 1413 | Coefficient on predicted liability spread decline: retained earnings 0.177\*\*\* (SE 0.027); equity 0.340\*\*\* (SE 0.072); N = 4,387 |
| R3 | Low-deposit-beta banks also had significantly lower loan growth 2000-2014, consistent with the leverage-constraint channel | Table II, p. 1413 | Coefficient on predicted liability spread decline: loans 0.291\*\*\* (SE 0.067); N = 4,387 |
| R4 | Low-deposit-beta banks also had significantly larger increases in loan spreads 2000-2014 | Table II, p. 1413 | Coefficient on predicted liability spread decline: loan spread -0.317\*\*\* (SE 0.045); N = 4,387 |

**Overall (paper's conclusion).** The secular decline in nominal interest rates hurts long-run bank credit supply even well above the zero lower bound. Because deposits compete with publicly issued money, lower nominal rates compress banks' deposit-spread income, weakening their financial constraints and reducing lending. The short-run and long-run effects of rate cuts differ: a rate cut can stimulate lending on impact via capital-gain revaluation of long-term assets, but permanently reduces lending in the long run once deposit incomes fall. The model has normative implications for the optimal inflation target, calling for a departure from the Friedman rule.

## Theory / model

The model features discrete time $$t = 0, 1, \ldots$$. Banks intermediate between two household types: savers (unconstrained) and borrowers (bank-dependent). Banks hold two types of assets (bonds and loans of maturity $$k \in \{1,\ldots,K\}$$) and two types of liabilities (deposits). Savers maximize lifetime utility and solve (p. 1385):

$$
\max_{c_t, a_{t+1}, m_{t+1}, d_{t+1}} \sum_{t=0}^{\infty} \beta^t U(c_t, x(m_t, d_t))
$$

$$
\text{s.t.} \quad c_t + \frac{1}{1+r_t}\left[\Omega_{t+1} + i_t m_{t+1} + s_t^d d_{t+1}\right] \leq A_t \bar{n}^s + \Omega_t + \text{Div}_t + T_t^s, \tag{1}
$$

where $$\Omega_t = a_t + m_t + d_t$$ is total financial wealth, $$i_t$$ is the nominal rate (the liquidity premium on money), $$s_t^d = \frac{1+r_t}{1+r_t^d} - 1$$ is the deposit spread. The liquidity aggregator $$x(m,d)$$ is strictly increasing, homothetic, and concave (Assumption 1, p. 1386). The standard CES specification is:

$$
x(m, d) = \left[\alpha^{1/\epsilon} m^{\frac{\epsilon-1}{\epsilon}} + (1-\alpha)^{1/\epsilon} d^{\frac{\epsilon-1}{\epsilon}}\right]^{\frac{\epsilon}{\epsilon-1}}, \tag{9}
$$

where $$\epsilon$$ is the elasticity of substitution between money and deposits.

Bank equity at the beginning of period $$t$$ is (p. 1387, eq. 2):

$$
e_t(i) \equiv \sum_{k=0}^{K-1} \frac{l_{t,t+k}(i)}{(1+r_{t,t+k}^l)^k} + a_t(i) - d_t(i), \tag{2}
$$

where the first term values outstanding loans at market yields. Banks are subject to a leverage constraint $$\text{liab}_t \leq \bar{\phi}_t e_t$$ (eq. 4), arising from limited pledgeability (Assumption 4: banks can pledge only a fraction $$\theta < 1$$ of date-$$t+1$$ assets). By Lemma 1 (p. 1388), in equilibrium the leverage ratio satisfies:

$$
\bar{\phi}_t = \frac{\theta(1+r_t^l)/(1+r_t^d)}{1 - \theta(1+r_t^l)/(1+r_t^d)}.
$$

The excess return on bank equity is the key object linking spreads to lending capacity (p. 1389, eq. 7):

$$
\nu_t = \underbrace{\bar{\phi}_t \frac{s_t^d}{1+s_t^d}}_{\text{excess return from liquidity provision}} + \underbrace{(1+\bar{\phi}_t) s_t^l}_{\text{excess return from credit provision}}. \tag{7}
$$

The steady-state real rate is pinned by fundamentals: $$r^* = G/\beta - 1$$ (p. 1393). The Fisher equation (p. 1394, eq. 13) implies:

$$
1 + i = (1 + \pi)(1 + r^*) = (1 + \pi)\frac{G}{\beta}. \tag{13}
$$

**Proposition 1** (p. 1394): When money and deposits are strict gross substitutes, there exists a positive threshold $$\tilde{i}$$ such that the economy is in the constrained lending regime if and only if $$i < \tilde{i}$$. In the constrained regime, a decline in $$i$$ lowers bank equity, deposits, leverage, and lending, while the deposit spread $$s^d$$ falls and the loan spread $$s^l$$ rises.

**Proposition 2** (p. 1395): The threshold $$\tilde{i}$$ satisfies:

$$
\tilde{i} = \frac{\nu}{1+\nu}\frac{1-\theta}{\theta} \Phi\!\left(\frac{\chi_{\min}}{\chi}\right), \tag{14}
$$

where $$\Phi$$ is an increasing function of the liquidity aggregator. The threshold increases with banks' required excess return $$\nu$$, decreases with pledgeability $$\theta$$, and decreases with liquidity benefits $$\chi$$. In the baseline calibration (Table I, p. 1398: $$G=1.02$$, $$\beta=0.98$$, $$\pi=2\%$$, $$\epsilon=8$$, $$\rho=0.2$$, $$\theta=0.85$$), $$\tilde{i} \approx 8\%$$.

**Proposition 3** (p. 1396): For $$i < \tilde{i}$$, both the deposit-rate and loan-rate pass-throughs are increasing functions of $$i$$ (convexity): at lower rates, a further rate decline compresses deposit spreads more per unit because the deposit beta $$\beta^d(i) = 1 - s^d(i)/i$$ is an increasing function of $$i$$.

**Proposition 4** (p. 1404): With only short-term loans ($$K=1$$), a permanent decline in $$i$$ always initially reduces lending relative to the previous steady state, because there is no maturity-mismatch-driven capital-gain revaluation channel.

**Proposition 5** (p. 1406-1407): With heterogeneous deposit markets differing in the relative preference for cash vs deposits (parameters $$\alpha, \chi$$), the long-run pass-through of the common nominal rate to the deposit rate is lower in markets with a stronger relative preference for cash, and a common rate decline leads to a larger increase in loan spreads and larger contraction in lending in those markets.

## Method

The model is a structural general equilibrium model with flexible prices and full employment (Definition 1, p. 1389). It is studied analytically via steady-state conditions and propositions proved in the Internet Appendix, and numerically via a baseline calibration (Table I, p. 1398). Transitional dynamics are obtained numerically.

The aggregate equity return identity (eq. 7) is the unifying device: it decomposes the excess return on bank equity into the deposit-spread leverage component and the loan-spread leverage component. Because the net payout rate $$\rho$$ pins the steady-state return $$\nu = \beta/(1-\rho) - 1$$ (eq. 12, p. 1393), an exogenous decline in $$s^d$$ must be offset by an endogenous rise in $$s^l$$ or a fall in leverage and equity.

The model builds on `panel-regression` for the empirical part and on the bank capital framework of Gertler and Kiyotaki (2010). The deposit competition mechanism follows the deposit-spread framework of Drechsler, Savov, and Schnabl (2017), extended to a two-sided bank balance sheet and a financial-constraint channel. The paper relates to Drechsler, Savov, and Schnabl (2021) on NIM stability, which it decomposes into offsetting loan and deposit spreads. It contrasts with Abadi, Brunnermeier, and Koby (2023), where money is irrelevant at positive rates and harmful lending effects arise only at negative rates. Di Tella and Kurlat (2021) study related bank exposure to monetary policy with maturity mismatch and liquidity premia on deposits.

## Empirical specifications

**Aggregate evidence (Section III.A, pp. 1409-1411).** To decompose the total loan-deposit spread into a loan spread and a deposit spread, the paper constructs a Treasury replicating portfolio that matches the maturity structure of the bank loan portfolio, using Call Report data on repricing maturity bins. The yield on the replicating portfolio at date $$t$$ is (p. 1410):

$$
R_t^{\text{Treas}} = y_{t-1}^{ST} \omega_{t-1}^{ST} + y_{t-10}^{LT}\left(1 - \omega_{t-1}^{ST}\right),
$$

where $$\omega_{t-1}^{ST}$$ is the share of loans repricing within one year and $$y^{ST}$$ ($$y^{LT}$$) is the one-year (ten-year) Treasury yield. The "loan spread" (red area in Figure 8, p. 1409) is the difference between the effective loan yield and the replicating Treasury yield, capturing credit and liquidity premia net of duration. The "deposit spread" (blue area) is the replicating Treasury yield minus the effective deposit rate. Sample: 1997Q2-2018Q2, all U.S. commercial banks (Call Reports and FDIC Quarterly Banking Profile).

**Cross-sectional evidence (Section III.B, pp. 1411-1413).** The paper constructs a bank-level "expense beta" $$\beta_i$$ by estimating a separate time-series regression for each bank $$i$$:

$$
\Delta \text{IntExp}_{it} = \alpha_i + \sum_{\tau=0}^{3} \beta_{i,\tau} \Delta ffr_{t-\tau} + \epsilon_{it}, \tag{implied by eq. 18}
$$

in the 1984-2000 pre-period, where $$\text{IntExp}_{it}$$ is interest expense over total assets and $$ffr$$ is the Fed funds rate. The "expense beta" $$\beta_i = \sum_{\tau=0}^{3} \beta_{i,\tau}$$ measures historical deposit-rate sensitivity: a low $$\beta_i$$ bank has stickier deposit rates and thus experiences more spread compression when rates fall. Using this, the paper constructs the predicted change in liability spread from the 2000-2014 rate decline:

$$
\widehat{\Delta \text{LiabilitySpread}}_{i,00-14} = (1 - \beta_i)(ffr_{2014} - ffr_{2000}).
$$

The main cross-sectional regression is then (p. 1412, eq. 18):

$$
\frac{y_{i,2014} - y_{i,2000}}{y_{i,2000}} = \alpha + \delta\, \widehat{\Delta\text{LiabilitySpread}}_{i,00-14} + \Gamma' \text{controls}_i + \epsilon_i, \tag{18}
$$

for outcomes $$y \in \{\text{retained earnings}, \text{equity}, \text{loans}, \text{loan spread}\}$$ (for spreads, the left-hand side is $$y_{i,2014} - y_{i,2000}$$). Controls include 2000Q4 leverage and the deposit-asset ratio. Standard errors are block-bootstrapped by quarter (1,000 iterations). Sample: 4,387 U.S. commercial banks with at least 20 quarterly observations for $$\text{IntExp}_{it}$$ in 1984-2000.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Call Reports (Federal Reserve / FFIEC) | Quarterly income and balance sheet data for all U.S. commercial banks; repricing maturity structure for replicating portfolio construction; bank-level interest expense and loan/deposit rates | no page yet |
| FDIC Quarterly Banking Profile | Aggregate U.S. commercial bank data cross-checking the Call Report series | [FDIC QBP / financials](/wiki/datasets/fdic/) |
| Federal Reserve H.15 / Fed funds rate | Policy rate series for expense-beta estimation and spread decomposition | no page yet |

Sample: 4,387 U.S. commercial banks; aggregate quarterly series 1997Q2-2018Q2; expense-beta pre-period 1984-2000.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13436) if you are: building a model of bank credit supply with liquidity frictions; studying the transmission of secular interest-rate declines to credit markets; interpreting NIMs and loan-deposit spreads in the data; or analyzing the optimal long-run inflation target from a banking-system perspective. Internet Appendix Section II details the calibration (Table I). Internet Appendix Section III contains extensions (role of money, endogenous equity issuance, operating costs, firm investment).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. Paywalled; no Creative Commons licence detected. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract-only: reproducing the verbatim text requires a subscription or library access.

> Wang, Olivier. "Banks, Low Interest Rates, and Monetary Policy Transmission."
> *The Journal of Finance* 80, no. 3 (June 2025): 1379–1416.
> DOI: [10.1111/jofi.13436](https://doi.org/10.1111/jofi.13436).
> © 2025 the American Finance Association.
