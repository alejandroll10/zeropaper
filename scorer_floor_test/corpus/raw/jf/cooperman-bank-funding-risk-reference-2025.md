---
title: "Bank Funding Risk, Reference Rates, and Credit Supply: Cooperman, Duffie, Luck, Wang & Yang (2025)"
description: >-
  Distilled: Credit-sensitive reference rates like LIBOR mitigate banks' debt-overhang
  cost from revolving credit commitments; the transition to risk-free SOFR increases
  expected draw costs by about 15 bps and reduces equilibrium credit line commitments
  by roughly 6%, with effects concentrated at high-debt-overhang banks. J. Finance 2025,
  paywalled. Six core results with source locators, datasets used, the equilibrium model
  of credit line provision, and the empirical method.
sidebar:
  label: Cooperman et al. 2025
  order: 1
tags: [paper-summary, banking, credit-supply, bank-funding, reference-rates, libor-sofr,
       revolving-credit, panel-regression, peer-reviewed, unreplicated,
       data:fr-2052a, data:fr-y14q, data:fred]
paper:
  authors: Harry Cooperman, Darrell Duffie, Stephan Luck, Zachry Wang, Yilin (David) Yang
  authorList:
    - { family: Cooperman, given: Harry, affiliation: Federal Reserve Bank of New York }
    - { family: Duffie, given: Darrell, orcid: "0000-0002-1212-7004", affiliation: Stanford Graduate School of Business }
    - { family: Luck, given: Stephan, orcid: "0000-0002-0928-8165", affiliation: Federal Reserve Bank of New York }
    - { family: Wang, given: Zachry, affiliation: Stanford Graduate School of Business }
    - { family: Yang, given: Yilin (David), orcid: "0000-0001-8169-5470", affiliation: City University of Hong Kong }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 5–56
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13411
  jel:
    codes: [G21, G12, E44]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Banking stability, regulation, efficiency
    - Global Financial Crisis and Policies
    - Housing Market and Economics
  dataAccess: proprietary-confidential
  outcome:
    - equilibrium credit line commitments (line limit)
    - expected drawn credit (quantity drawn)
    - credit line spread over reference rate
    - welfare from credit line provision
  outcomeClass: [credit-supply, bank-funding, firm-financing]
  license: >-
    Paywalled (Crossref license block: content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days=0, start=2024-12-20; no open-access licence found).
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley OnlineLibrary, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 5

  methods:
    role: both
    family: structural
    buildsFrom: [panel-regression, difference-in-differences, gmm]
    identification: natural-experiment
  contributionType: [new-theory, new-fact]
  mechanisms: [debt-overhang, intermediary-constraint, financial-constraint]

  scope:
    region: US
    assetClass: corporate revolving credit lines (C&I lending)
    period: 2007-12..2022-04
    frequency: mixed
    dataType: [administrative, accounting, market]
    granularity: [firm, aggregate]
    n: "20 largest U.S. BHCs (monthly FR 2052a, July 2017-April 2022); 30 banks weekly FR 2416, Dec 2007-May 2009"

  findings:
    - ref: R1
      outcome: deposit response per dollar of drawdown (COVID episode)
      metric: coefficient
      value: "0.94 cents of corporate deposits per dollar of drawdown (Table IV Panel A, col. 1, coeff on Delta Draws = 0.07, coeff on Delta Draws x COVID = 0.94; total 0.94+0.07=1.01 during COVID)"
      direction: positive
      vsBenchmark: "near zero net new external funding needed during COVID vs. substantial wholesale funding raised during GFC"
    - ref: R2
      outcome: wholesale funding raised per dollar of drawdown (GFC episode)
      metric: coefficient
      value: "~$4 in wholesale funding per $1 increase in C&I lending during GFC post-Lehman (Table V col. 3, Delta C&I loans x Lehman: 4.33*** (0.41) in levels; col. 4 normalized Lehman interaction: 0.90* (0.47) per unit assets)"
      direction: positive
      vsBenchmark: "no deposit offset during GFC unlike COVID; banks forced to raise costly external funding"
    - ref: R3
      outcome: equilibrium credit line commitments (LIBOR-to-SOFR transition, baseline bank)
      metric: pp-effect
      value: "-5.87% reduction in aggregate credit line limit (Table VI, baseline theta=1.0, D=0.2)"
      direction: negative
      vsBenchmark: "+4.64% for low-debt-overhang bank (theta=0.5, D=0.75); -11.36% for high-debt-overhang bank (theta=1.5, D=0.1)"
    - ref: R4
      outcome: expected drawn credit (LIBOR-to-SOFR transition, baseline bank)
      metric: pp-effect
      value: "-2.77% reduction in expected drawn credit (Table VI, baseline)"
      direction: negative
      vsBenchmark: "+1.12% for low-debt-overhang; -5.20% for high-debt-overhang"
    - ref: R5
      outcome: credit line spread over reference rate (LIBOR-to-SOFR transition)
      metric: basis-points
      value: "+51.7 bps increase in drawn spread s* for baseline bank (Table VI, baseline); ~15 bps increase in expected cost of drawn credit (p. 6)"
      direction: positive
      vsBenchmark: "spread must rise to price the higher expected debt-overhang cost under SOFR relative to LIBOR"
    - ref: R6
      outcome: welfare from credit line provision (LIBOR-to-SOFR transition)
      metric: pp-effect
      value: "-2.62% welfare reduction for baseline bank; -4.98% for high-debt-overhang; +1.16% for low-debt-overhang (Table VI)"
      direction: negative
      vsBenchmark: "welfare-maximizing reference rate has ~72% of the credit sensitivity of LIBOR for baseline bank"

  resultType: new-finding

  relatesTo:
    - { cite: "Ivashina and Scharfstein (2010)", doi: '10.1016/j.jfineco.2009.12.001', relation: builds-on, note: "documents elevated credit line drawdowns during GFC; paper confirms this and contrasts with COVID pattern" }
    - { cite: "Kashyap, Rajan, and Stein (2002)", doi: '10.1111/1540-6261.00415', relation: builds-on, note: "liquidity coinsurance synergy between deposits and credit lines; paper adds a debt-overhang complementarity channel" }
    - { cite: "Jermann (2019)", doi: '10.2139/ssrn.3361942', relation: cites, note: "LIBOR-linked loan revenues act as insurance against bank funding risk; paper extends to equilibrium credit provision" }
    - { cite: "Gatev and Strahan (2006)", doi: '10.1111/j.1540-6261.2006.00857.x', relation: cites, note: "flight-to-safety deposit inflows during stress; relevant to the deposit-offset mechanism in the model" }
    - { cite: "Acharya and Mora (2015)", doi: '10.1111/jofi.12182', relation: cites, note: "banks subject to heavy drawdowns during GFC faced funding pressures; consistent with paper's empirical findings" }
    - { cite: "Berndt, Duffie, and Zhu (2023)", doi: '10.1111/fmii.12172', relation: cites, note: "proposes AXI as an alternative credit-sensitive reference rate; discussed in the conclusion" }

  openQuestions:
    - "How the industrial organization of banking relationships (sticky borrower-bank matches) affects general equilibrium credit provision after the LIBOR-SOFR transition; a broader GE analysis is beyond the scope of the paper (p. 40)."
    - "Whether stress-test capital requirements should incorporate the impact of line draws on bank balance sheets under risk-free reference rates, to limit the crowding out of term lending (pp. 40-41)."
    - "Whether the welfare-maximizing credit-sensitive reference rate differs from AXI or other proposed alternatives, given the limited adoption of such alternatives as of 2025 (pp. 41-42)."

  replicationCode:
    status: none

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: >-
        Full PDF read (pp. 5-56, J. Finance Vol. 80 No. 1 Feb 2025). All results
        extracted from Tables IV-VI and Figures 5-7 with page locators. Not
        human-verified. Not reproduced. Confidential FR 2052a and FR Y-14Q data
        are not accessible for reproduction.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; two
        fixes applied: (1) R2 normalized Lehman interaction corrected from
        0.89*** (0.15) to 0.90* (0.47) per Table V col. 4; (2) Berndt, Duffie,
        and Zhu year corrected from (2024) to (2023) per the references list
        (the AXI paper is the 2023 FMII article, not the 2024 AER forthcoming).
        All other locators and magnitudes (Tables IV, V, VI; eqs. 1, 7, 8, 9,
        10, 11, 12, 13, 14, 15) confirmed correct against the PDF.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13411
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-20; no CC or open-access licence present"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the equilibrium model of credit line provision, and the empirical evidence on how banks fund credit drawdowns: enough to know what it found and how, without reading all 52 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13411).

## TL;DR

Revolving corporate credit lines create a debt-overhang cost for bank shareholders: because borrowers draw more heavily when funding markets are stressed, banks must sometimes fund drawdowns with expensive unsecured wholesale debt, diluting legacy shareholders. Credit-sensitive reference rates like LIBOR partially offset this by reducing borrower incentives to draw precisely when bank funding costs are high. The LIBOR-to-SOFR transition removes this offset. Using a calibrated equilibrium model and confidential Federal Reserve data (FR 2052a, FR Y-14Q), the authors show that SOFR-linked lines lead to higher spreads (about 15 bps), smaller credit line commitments (roughly 6% lower for a baseline bank), and a 2.6% welfare loss. The adverse impact is offset at banks that expect drawn funds to be left on deposit, which happened at large universal banks during COVID but not at regional banks during the GFC.

The paper relates to Kashyap, Rajan, and Stein (2002), who identify the liquidity coinsurance synergy between deposits and credit lines; the authors add a new debt-overhang complementarity channel to this synergy. It also extends Jermann (2019), who shows LIBOR-linked loan revenues insure banks against funding risk, to an equilibrium credit provision setting. Empirically, it builds on Ivashina and Scharfstein (2010) on GFC drawdowns, Acharya and Mora (2015) on bank funding pressures, and Gatev and Strahan (2006) on flight-to-safety deposit inflows. In the conclusion, the authors discuss the AXI credit-sensitive reference rate proposed by Berndt, Duffie, and Zhu (2023) as a potential LIBOR successor.

## Core results

Magnitudes and significance are as reported; `\*`, `\*\*`, `\*\*\*` = 10%, 5%, 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | During COVID, each dollar of credit line drawdown is associated with **94 cents deposited at the same bank**, insulating shareholders from funding costs | Table IV Panel A, col. 1, p. 24-25 | Coeff. on Delta Draws x COVID = 0.94\*\*\* (0.34); baseline coeff. on Delta Draws = 0.07 (0.04); total = ~1.01 during COVID |
| R2 | During the GFC (post-Lehman), each dollar of C&I loan growth required **~$4 of new wholesale funding** (no deposit offset) | Table V col. 3-4, p. 28 | Coeff. on DeltaC&ILoans x Lehman = 4.33\*\*\* (0.41) in levels (col. 3); normalized Lehman interaction = 0.90\* (0.47) per unit assets (col. 4) |
| R3 | LIBOR-to-SOFR transition reduces equilibrium **aggregate credit line commitments by 5.9%** for baseline bank | Table VI col. Baseline, p. 38; Figure 5 right, p. 34 | -5.87% (baseline theta=1.0, D=0.2); range: +4.64% (low-overhang) to -11.36% (high-overhang) |
| R4 | Transition reduces **expected drawn credit by 2.77%** for baseline bank | Table VI, p. 38 | -2.77% (baseline); +1.12% (low-overhang); -5.20% (high-overhang) |
| R5 | The equilibrium **spread on drawn credit rises ~15 bps** and the drawn-rate spread rises 51.7 bps over the reference rate for baseline bank | Table VI, p. 38; p. 6 | Change in drawn spread s\* = +51.7 bps; expected cost of drawn credit rises ~15 bps; SOFR lines ~24 bps more expensive than LIBOR lines in normal times (Figure 5 left, p. 34) |
| R6 | **Welfare falls 2.62%** for baseline bank; the welfare-maximizing reference rate has ~72% of LIBOR's credit sensitivity | Table VI, p. 38; p. 39 | Welfare change: -2.62% baseline, -4.98% high-debt-overhang, +1.16% low-debt-overhang; optimal lambda\* = 0.72 for baseline |

**Overall (paper's conclusion).** The transition from LIBOR to SOFR increases the ex-ante expected cost banks must charge on revolving credit, reducing the equilibrium supply of credit lines. The magnitude depends on how much of future drawdowns banks expect to receive back as deposits. The adverse effect is concentrated at high-funding-spread, low-deposit-retention banks (predominantly large regional banks), while well-capitalized banks with strong deposit franchises may gain market share. The welfare-maximizing reference rate is more credit-sensitive than risk-free SOFR but need not be as credit-sensitive as LIBOR.

## Theory / model

The model has a three-date structure (Figure 1, p. 11). At time 0, a bank offers a menu of credit line contracts $$\{(L, s(L)) : L \geq 0\}$$ distinguishing line size $$L$$ and contractual spread $$s(L)$$ over the floating reference rate $$R$$. The credit-sensitive rate is $$R = r + W$$ (LIBOR form, for credit-spread benchmark $$W$$); the risk-free rate is $$R = r$$ (SOFR form). At time 1, the reference rate $$R$$, the bank's unsecured wholesale credit spread $$S$$, and the borrower's liquidity shock $$\psi$$ are realized. The borrower draws $$q \leq L$$ and deposits $$d \leq q$$ at the same bank. At time 2, the bank is solvent or not.

The borrower's optimal draw quantity solves (eq. 1, p. 13):

$$
Q(L) = \underset{0 \leq q \leq L}{\sup} \; b(q, \psi) - q\delta(1 + R + s(L)) \tag{1}
$$

where $$b(q, \psi)$$ is a reduced-form liquidity benefit with marginal benefit $$b_x(x, y)$$ increasing, differentiable, and strictly concave in $$x$$. The optimal draw has a threshold structure: $$Q(L) = L$$ if the marginal liquidity benefit is high enough, and $$Q(L) = B(\delta(1+R+s(L)), \psi)$$ where $$B(\cdot, y)$$ is the inverse of $$b_x(\cdot, y)$$.

The market value of credit lines to **legacy bank shareholders** is (Proposition 1, eq. 7, p. 14):

$$
G(L) = p_1\bigl(\delta Q(L)(1+R+s(L)) - Q(L)\bigr) - p_1\delta(1-\varphi-C)Q(L)S - (1-p_1)CQ(L) \tag{7}
$$

where $$p_1 = P_1(X \geq 0)$$ is the bank's solvency probability at time 1, $$\varphi = d/q$$ is the fraction of drawn funds deposited at the bank, $$C$$ is the regulatory capital ratio, and $$S$$ is the bank's unsecured wholesale credit spread. The second term is the **debt-overhang cost**: the bank must fund $$(1-\varphi-C)Q(L)$$ of drawdowns with expensive new wholesale debt at spread $$S$$. Under Bertrand competition ($$E[G(L)] = 0$$), the equilibrium spread is (eq. 8, p. 14):

$$
s(L) = \frac{E\bigl[p_1 Q(L)\bigl(1 - \delta(1+R) + \delta(1-\varphi-C)S\bigr) + (1-p_1)CQ(L)\bigr]}{E\bigl[\delta p_1 Q(L)\bigr]} \tag{8}
$$

This spread rises in $$\text{Cov}(S, Q(L))$$: the key debt-overhang wedge. A credit-sensitive reference rate ($$R = r+W$$ with $$W \approx S$$) reduces drawdowns exactly when $$S$$ is high, cutting this covariance. A risk-free reference rate removes this attenuation.

**Identification.** The empirical section uses the GFC (Ivashina and Scharfstein (2010)) and COVID recession as quasi-natural experiments that shift the LIBOR-OIS spread to historically extreme levels, allowing the authors to compare how banks funded drawdowns under each episode. The calibrated model is then identified by fitting the distribution of credit line utilization in the FR Y-14Q data across normal times and the COVID recession.

## Method

The paper proceeds in three steps. First, the equilibrium model of Section II identifies the theoretical mechanism. Second, confidential FR 2052a and FR Y-14Q data are used empirically to pin down bank funding cost composition and drawdown funding, building on `panel-regression` and `difference-in-differences`. Third, the model is calibrated via nonlinear least squares to historical LIBOR-linked credit line behavior and the model is used to simulate the LIBOR-to-SOFR transition.

**Calibration of borrower demand.** The liquidity benefit is specified as (eq. 11, p. 30):

$$
b(q, \psi) = \frac{\psi^\alpha q^{1-\alpha}}{1-\alpha} \tag{11}
$$

for price elasticity $$1/\alpha$$, baseline $$\alpha = 1/25$$ (elasticity of 25). The optimal draw is therefore (eq. 13, p. 33):

$$
Q(L) = \min\!\bigl((K(W) + \epsilon)^+(1+R+s)^{-1/\alpha}, L\bigr) \tag{13}
$$

where $$K(W)$$ is the common component of the borrower liquidity shock (a nonlinear increasing function of LIBOR-OIS spread $$W$$) and $$\epsilon$$ is an idiosyncratic shock. The deposited fraction of drawn funds is a logistic function of LIBOR-OIS (eq. 12, p. 32):

$$
\Phi(x) = \frac{D}{1+e^{-m(x-w_0)}} \tag{12}
$$

with baseline parameters $$D = 0.2$$, $$m = 0.1$$, $$w_0 = 146.1$$ bps. The risk-neutral probability of a GFC-like crisis is set to $$p = 4\%$$, calibrated to daily LIBOR-OIS observations from January 2005 to April 2021.

**Aggregate equilibrium quantities** in the continuum-of-borrowers model satisfy (eq. 14-15, p. 33):

$$
M \cdot E[Q(L) \mid W] = M \cdot E\!\left[\min\!\left((K(W)+\epsilon)^+(1+R+s)^{-1/\alpha}, L\right) \;\middle|\; W\right] \tag{14}
$$

$$
P[Q(L) = L \mid W] = P\!\left[(K(W)+\epsilon)^+(1+R+s)^{-1/\alpha} \geq L \;\middle|\; W\right] \tag{15}
$$

## Empirical specifications

**Funding of drawdowns during COVID (eq. 9, p. 24).** Using monthly FR 2052a data (20 largest BHCs, July 2017 to April 2022, $$N = 1{,}111$$, 20 banks), the authors estimate:

$$
\Delta y_{bt} = \tau_t + \gamma_b + \beta_1 \Delta\text{Drawdowns}_{bt} + \beta_2 \Delta\text{Drawdowns}_{bt} \times \text{COVID}_t + \epsilon_{bt} \tag{9}
$$

where $$y_{bt}$$ is the change in corporate deposits, FHLB advances, unsecured wholesale funding, or total deposits. $$\text{COVID}_t$$ takes the value one during March and April 2020. Bank and time fixed effects are included. Robust standard errors are clustered at the bank level. The coefficient $$\beta_1 + \beta_2$$ measures the marginal funding response per dollar of drawdown during COVID; $$\beta_1$$ measures the non-COVID response (Table IV, p. 25).

**Funding of drawdowns during GFC (eq. 10, p. 27).** Using weekly FR 2416 data (30 commercial banks, December 2007 to May 2009, $$N = 1{,}765$$), the authors estimate:

$$
y_{bt} = \tau_t + \gamma_b + \beta_1 \Delta C\&I\text{Loans}_{bt} + \beta_2 \times \Delta C\&I\text{Loans}_{bt} \times \text{Lehman}_t + \epsilon_{bt} \tag{10}
$$

where $$\text{Lehman}_t$$ takes value one from September 15, 2008 through end of 2008. The dependent variable is either total deposits or wholesale short-term funding (WHSLE). Month and bank fixed effects. Robust standard errors (Table V, p. 28).

Both regressions test whether drawdowns generated deposit inflows (low marginal funding cost) or required new wholesale funding (high marginal funding cost). During COVID, banks needed essentially no new external funding because drawdowns were left on deposit; during the GFC, the same drawdowns forced banks to raise costly wholesale debt.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| FR 2052a (Federal Reserve confidential) | Daily/monthly bank balance sheet, funding composition by counterparty and product type; main panel for COVID empirics (20 BHCs, July 2017-April 2022) | no page yet |
| FR Y-14Q Schedule H1 (corporate loans) and H2 (CRE) | Loan-level credit commitments and utilization; calibration target for borrower demand and line draw distribution | [FR Y-14Q](/wiki/datasets/fr-y14q/) (confidential) |
| FR 2416 (Federal Reserve, weekly) | Weekly balance sheet for 30 banks; GFC drawdown-funding regression (Dec 2007-May 2009) | no page yet |
| FR 2420 (Federal Reserve, transaction-based) | Corporate deposit and wholesale funding rates (overnight rates, CDs, fed funds); sensitivity of funding costs to LIBOR-OIS | no page yet |
| FRED | LIBOR-OIS spread, SOFR, effective federal funds rate | [FRED](/wiki/datasets/fred/) |
| FR Y-9C / bank call reports | Public balance sheet data merged with FR 2052a for context | no page yet |
| FHLB Des Moines historical fixed-rate advance file | FHLB advance rates for funding cost benchmark | no page yet |
| Bloomberg | Long-term bank debt floating-rate and LIBOR-referenced shares | no page yet |

Sample: Empirical analysis spans December 2007 to April 2022; calibration uses LIBOR-OIS observations from January 2005 to April 2021.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13411) if you are: (i) pricing revolving credit facilities under SOFR to account for debt-overhang costs, and want the calibrated equilibrium spread formula (Section IV.B); (ii) studying bank balance sheet dynamics during the GFC vs. COVID using FR 2052a or FR 2416 data (Sections III.E-F and Tables III-V); (iii) evaluating alternative credit-sensitive reference rates such as AXI, BSBY, or Ameribor from a welfare-maximizing standpoint (Section V); or (iv) studying how bank capitalization and deposit franchise strength mediate the impact of reference-rate transition on credit supply heterogeneity (Section IV.C and Table VI).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025, pp. 5-56. Accepted March 4, 2024; published online December 20, 2024. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled (Wiley/AFA); only textual extracts are reproduced here.

> Cooperman, Harry, Darrell Duffie, Stephan Luck, Zachry Wang, and Yilin (David) Yang.
> "Bank Funding Risk, Reference Rates, and Credit Supply."
> *The Journal of Finance* 80, no. 1 (February 2025): 5-56.
> DOI: [10.1111/jofi.13411](https://doi.org/10.1111/jofi.13411).
> © 2024 the American Finance Association. All rights reserved.
> This page presents distilled extracts only; redistribution of the verbatim article is not permitted.
