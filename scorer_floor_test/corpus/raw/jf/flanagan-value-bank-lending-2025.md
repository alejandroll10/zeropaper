---
title: "The Value of Bank Lending: Flanagan (2025)"
description: >-
  Distilled: Using novel realized cash flows for 8,100 syndicated term loans
  (1992-2014) and a private-equity-style risk-adjustment methodology, Flanagan
  (2025) finds that banks earn 177 bps annualized gross risk-adjusted returns on
  loan cash flows, add roughly $75 million of value annually per loan portfolio,
  and that shareholders receive near-zero net risk-adjusted returns once lending
  expenses are deducted. J. Finance 2025, CC BY-NC 4.0. Eight core results
  with source locators, datasets used, the economic framework, the method
  (risk-adjusted profit adapted from Gupta and Van Nieuwerburgh (2021)), and
  empirical specifications.
sidebar:
  label: Flanagan 2025
  order: 1
tags: [paper-summary, banking, credit-supply, financial-intermediation,
       panel-regression, peer-reviewed, unreplicated,
       data:wrds, data:dealscan, data:edgar]
paper:
  authors: Thomas Flanagan
  authorList:
    - { family: Flanagan, given: Thomas, affiliation: "Fisher College of Business, The Ohio State University" }
  year: 2025
  venue: "The Journal of Finance 80(4), August 2025, 2017-2061"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13465
  jel:
    codes: [G21, G12, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - "Banking stability, regulation, efficiency"
    - "Corporate Finance and Governance"
    - "Financial Intermediation and Value Creation"
  dataAccess: licensed-commercial
  outcome:
    - risk-adjusted profit (RAP) of syndicated bank loan cash flows
    - annualized risk-adjusted return on bank loan portfolios
    - net risk-adjusted return to bank shareholders from lending
  outcomeClass: [credit-supply, firm-financing]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-05-28; corroborated by artifact p.2017 Creative Commons
    Attribution-NonCommercial License notice)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "open-access PDF available via Wiley (confirmed via Crossref OA metadata 2026-06-05)"
  redistribution: extract-only (CC BY-NC 4.0 permits reproduction for non-commercial use; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 1
  methods:
    role: both
    contributes: rap-bank-loans
    family: descriptive
    buildsFrom: [panel-regression, fama-macbeth]
    identification: descriptive
  contributionType: [new-method, new-data, new-fact]
  mechanisms: [information-asymmetry, moral-hazard, financial-constraint, intermediary-constraint]
  introducesData: true
  scope:
    region: US
    assetClass: syndicated corporate loans
    period: 1992-07..2014-03
    frequency: quarterly
    dataType: [market, accounting, administrative]
    granularity: [firm, transaction]
    n: "8,125 senior term loans to U.S. public borrowers, originated 1992Q3-2014Q1"
  findings:
    - ref: R1
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "RAP = $0.032 per $1 invested; annualized RAP (psi) = 177 bps"
      direction: positive
      vsBenchmark: "compared to public-market benchmark replicating portfolio (risk-free + BBB/HY + stock factors); Table II Panel B col (2), p. 2037"
    - ref: R2
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "Financially constrained borrowers (top quartile): annualized RAP = 242 bps; bottom quartile: 126 bps; H-L difference = 117 bps***"
      direction: positive
      vsBenchmark: "93% higher annualized RAP for top vs bottom financial-constraint quartile; Table III, p. 2041"
    - ref: R3
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "Short-maturity loans: annualized RAP = 235 bps; long-maturity: 154 bps; H-L = -81 bps***"
      direction: positive
      vsBenchmark: "53% higher annualized RAP for shorter vs longer maturity loans; Table IV, p. 2043"
    - ref: R4
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "High industry fixed costs: annualized RAP = 217 bps; low: 151 bps; H-L = 66 bps***"
      direction: positive
      vsBenchmark: "44% higher annualized RAP for high vs low fixed-cost industries; Table IV, p. 2043"
    - ref: R5
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "High EBC tightness: annualized RAP = 244 bps; low: 166 bps; H-L = 78 bps***"
      direction: positive
      vsBenchmark: "earnings-based covenant tightness associated with higher RAP, consistent with monitoring; Table IV, p. 2043"
    - ref: R6
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: coefficient
      value: "L4.RAP coefficient = 0.101*** (SE 0.032); L8.RAP = 0.080** (0.033); L12.RAP = 0.126*** (0.032); L16.RAP = 0.089*** (0.024)"
      direction: positive
      vsBenchmark: "bank-level RAP persists 1-4 years ahead; Dollar Value-Added is a stronger predictor (R2 ~0.30 vs 0.14); Table VI, p. 2048"
    - ref: R7
      outcome: net risk-adjusted return to bank shareholders from lending
      metric: basis-points
      value: "-5 bps net risk-adjusted return to shareholders (statistically indistinguishable from zero); commercial lending noninterest expense = 182 bps (113 bps staff comp + 69 bps other)"
      direction: none
      vsBenchmark: "gross RAP of 177 bps fully absorbed by lending expenses; Table VII, p. 2050"
    - ref: R8
      outcome: risk-adjusted profit (RAP) of syndicated bank loan cash flows
      metric: basis-points
      value: "Corporate bond placebo: annualized RAP Ann = 0.015 (SE 0.102), not significantly different from zero; loan RAP = 177 bps***"
      direction: none
      vsBenchmark: "methodology correctly prices corporate bonds near zero, validating the loan RAP estimate; Table VIII Panel B, p. 2053"
  resultType: new-finding
  relatesTo:
    - { cite: "Gupta and Van Nieuwerburgh (2021)", doi: '10.1111/jofi.13073', relation: extends, note: "adapts their strip-by-strip private equity RAP methodology to bank loan cash flows with loan-balance instruments and statistical inference" }
    - { cite: "Begenau and Stafford (2019)", doi: '10.2139/ssrn.3095550', relation: tests, note: "reconciles their finding of near-zero shareholder value from banking with classic theories by showing gross RAP is positive but absorbed by lending expenses" }
    - { cite: "Berk and van Binsbergen (2015)", doi: '10.1016/j.jfineco.2015.05.002', relation: builds-on, note: "applies their Dollar Value-Added framework to bank loan portfolios for persistence tests" }
    - { cite: "Korteweg and Nagel (2016)", doi: '10.1111/jofi.12390', relation: builds-on, note: "uses their private equity benchmark fund construction for loan benchmark funds" }
    - { cite: "James (1987)", doi: '10.1016/0304-405x(87)90003-1', relation: cites, note: "classic evidence that bank borrowers benefit through stock market valuation; used to validate cross-sectional results" }
    - { cite: "Leland and Pyle (1977)", doi: '10.2307/2326770', relation: builds-on, note: "classic theory that banks create value through information production and monitoring, motivating the study" }
    - { cite: "Diamond (1984)", doi: '10.2307/2297430', relation: builds-on, note: "delegated monitoring theory underpinning the cross-sectional financial-constraint predictions" }
    - { cite: "Holmstrom and Tirole (1997)", doi: '10.1162/003355397555316', relation: builds-on, note: "intermediary incentive compatibility constraint motivating why banks must capture cash flow present value to cover screening costs" }
    - { cite: "Philippon (2010)", doi: '10.1257/mac.2.3.158', relation: cites, note: "competitive equilibrium model where banks capture present value of loan cash flows to compensate employees; near-zero net shareholder returns confirm this model" }
  openQuestions:
    - "Whether the findings generalize to smaller, private-firm loans and non-syndicated C&I loans, where informational frictions may differ (p. 2022, 2029)."
    - "Whether the methodology can separately identify the systemic-risk externality of bank lending, which is not captured by the loan RAP measure (p. 2022)."
    - "How lending expenses and net risk-adjusted returns differ for loan types other than syndicated term loans to public firms (p. 2057)."
  replicationCode:
    status: available
  licenceVerification:
    - source: "Crossref REST API works/10.1111/jofi.13465"
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-05-28"
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full text read (pp. 2017-2061); eight results extracted from the CC-BY-NC PDF. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all eight Core-results rows confirmed. Fixed equation (3): corrected superscript on LHS from tilde-R^k to tilde-R^i to match PDF p. 2032. Fixed topics: replaced erroneous 'Housing Market and Economics' with 'Financial Intermediation and Value Creation' (paper is G21/G12/G28)."
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the economic framework it builds on, and the risk-adjustment method it adapts from private equity to bank loans, with the defining equations: enough to know what it found and how, without reading all 45 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13465).

## TL;DR

The paper asks: do banks produce real value through lending, and who captures it? Using a novel dataset of realized cash flows for 8,100+ U.S. syndicated term loans (1992-2014), Flanagan adapts the Gupta and Van Nieuwerburgh (2021) private equity risk-adjustment method to estimate the risk-adjusted profit (RAP) of bank loans relative to public-market benchmarks. Banks earn on average 177 basis points annualized gross risk-adjusted returns, consistent with providing valuable screening and monitoring services. These returns are larger when borrowers face more severe financing frictions and when banks invest more resources in lending services. Bank-level RAP also persists over time, indicating skill heterogeneity. However, once commercial lending expenses (182 bps, primarily staff compensation) are deducted, shareholders receive near-zero net risk-adjusted returns, consistent with competitive equilibrium: the present value of loan cash flows covers lending costs, not shareholder rents.

## Core results

Magnitudes and significance are as reported; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%. Locators point into the source PDF (pp. 2017-2061).

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Baseline gross RAP: banks earn 177 bps annualized** risk-adjusted returns on syndicated loan cash flows | Table II Panel B col (2), p. 2037 | RAP = $0.032 per $1 invested; annualized psi = 1.77%\*\*\* (SE 0.059) |
| R2 | **Higher RAP for financially constrained borrowers**: top vs bottom financial-constraint quartile earns 93% higher annualized RAP | Table III, p. 2041 | Top-quartile psi = 2.42%\*\*\*, bottom = 1.26%\*\*\*; H-L = 1.17%\*\*\* (SE 0.22) |
| R3 | **Shorter-maturity loans earn 53% higher annualized RAP**, consistent with a fixed cost of screening | Table IV, p. 2043 | Low-maturity psi = 2.35%\*\*\*, high-maturity = 1.54%\*\*\*; H-L = -0.81%\*\*\* (SE 0.26) |
| R4 | **Loans to high fixed-cost industries earn 44-47% higher RAP**, consistent with greater irreversibility requiring more screening | Table IV, p. 2043 | High fixed-cost psi = 2.17%\*\*\*, low = 1.51%\*\*\*; H-L = 0.66%\*\*\* (SE 0.18) |
| R5 | **Tighter earnings-based covenants (EBC) earn higher RAP**, consistent with monitoring intensity; higher renegotiation probability earns lower RAP (substitution) | Table IV, p. 2043 | High EBC tightness psi = 2.44%\*\*\*, low = 1.66%\*\*\*; H-L = 0.78%\*\*\* (SE 0.25) |
| R6 | **Bank-level RAP persists 1-4 years ahead**; Dollar Value-Added is a stronger persistence predictor than RAP alone | Table VI, p. 2048 | L4.RAP = 0.101\*\*\* (SE 0.032); L4.DVA = 0.473\*\*\* (SE 0.121); R2 for DVA ~0.30 vs ~0.14 for RAP |
| R7 | **Shareholders receive near-zero net risk-adjusted returns** after deducting commercial lending expenses of 182 bps | Table VII, p. 2050 | Net psi = approx -5 bps, statistically indistinguishable from zero; 113 bps staff comp + 69 bps other expenses |
| R8 | **Corporate bond placebo confirms methodology**: risk-adjusting corporate bond cash flows yields near-zero RAP, validating the loan estimates | Table VIII Panel B, p. 2053 | Corporate bond RAP Ann = 0.015 (SE 0.102), not significant; full-sample risk-free return = 2.77%\*\*\* is eliminated by risk adjustment |

**Overall (paper's conclusion).** Bank loan cash flows have large, economically significant gross risk-adjusted returns that compensate bank employees for their costly screening and monitoring services. The cross-sectional pattern of these returns is consistent with banks providing more valuable intermediation to more financially constrained borrowers. However, shareholders of banks receive approximately zero net risk-adjusted returns from syndicated lending, consistent with competitive provision of lending services and with the model of Philippon (2010). These results help reconcile the empirical literature finding low bank shareholder value (Begenau and Stafford (2019)) with classic theories of banking emphasizing productive lending services (Leland and Pyle (1977), Diamond (1984)).

## Theory / model

The paper has no formal structural model but provides an economic framework (Section I.A, pp. 2025-2027) that motivates the empirical tests and the interpretation of RAP.

**Cost of capital decomposition.** A firm's cost of borrowing via a bond market is

$$
r_{\text{firm,bond}} = r_f + r_{\text{risk}} + \theta_{\text{bond}},
$$

where $$r_f$$ is the risk-free rate, $$r_{\text{risk}}$$ is the risk premium in a frictionless market, and $$\theta_{\text{bond}}$$ is the financing friction specific to the bond market. The cost of a bank loan is

$$
r_{\text{firm,loan}} = r_f + r_{\text{risk}} + \theta_{\text{loan}} + \psi,
$$

where $$\theta_{\text{loan}} \leq \theta_{\text{bond}}$$ (banks mitigate financing frictions through information production and monitoring) and $$\psi \geq 0$$ is the bank's required return for supplying lending services. The incentive compatibility constraint for banks is

$$
\psi - \gamma \geq 0,
$$

where $$\gamma$$ is the cost of compensating loan officers and covering other expenses. In competitive equilibrium $$\psi = \gamma$$, and the borrower takes a loan if the net cost reduction is positive:

$$
(\theta_{\text{bond}} - (\theta_{\text{loan}} + \psi)) \geq 0.
$$

**Total value decomposition.** The total value from mitigated financial frictions decomposes into the present value flowing to the lender and the value flowing to the borrower (pp. 2026-2027). Letting $$X_t$$ be the outstanding principal balance,

$$
\underbrace{\sum_{h=1}^{H} \frac{(\theta_{\text{bond}} - \theta_{\text{loan}}) X_{t-1}}{(1 + r_f + r_{\text{risk}})^h}}_{\text{Total Value}} \approx \underbrace{\sum_{h=1}^{H} \frac{r_{\text{firm,loan}} \cdot X_{h-1} + (X_h - X_{h-1})}{(1 + r_f + r_{\text{risk}} + \theta_{\text{loan}})^h} - X_0}_{\text{Present Value to Lender}} + \underbrace{\sum_{h=1}^{H} \frac{(\theta_{\text{bond}} - (\theta_{\text{loan}} + \psi)) X_{h-1}}{(1 + r_f + r_{\text{risk}})^h}}_{\text{Borrower Value}}.
$$

Empirically, the present value to the lender corresponds directly to the RAP estimated in the paper, and is a lower bound on the total social value generated. The annualized version of this present value is the parameter $$\psi$$ estimated throughout.

**Key hypotheses.** (i) Classic banking theory predicts higher RAP for more financially constrained borrowers, where screening and monitoring provide greater value. Leland and Pyle (1977), Diamond (1984), and Holmstrom and Tirole (1997) all predict banks create value through information production; here, the incentive compatibility condition $$\psi - \gamma \geq 0$$ ties the bank's required spread directly to its lending costs. (ii) Risk-shifting theory predicts the opposite. (iii) Competitive equilibrium predicts near-zero net shareholder returns ($$\psi = \gamma$$). (iv) Persistence in bank-level RAP, in the spirit of Berk and van Binsbergen (2015) for mutual funds, indicates skill heterogeneity in lending services. Indirect evidence from James (1987) and Berger and Udell (1995) shows borrowers benefit from bank lending through higher stock prices and better loan pricing, consistent with the framework.

## Method

The method adapts the Gupta and Van Nieuwerburgh (2021) private equity strip-by-strip risk-adjustment (RAP) methodology to bank loan cash flows, with several extensions. It builds on `panel-regression` and `fama-macbeth` for factor selection and inference.

**Core pricing equation.** Let $$R^k_{t+h}$$ denote the cumulative return on public security $$k$$ from $$t$$ to $$t+h$$. The no-arbitrage pricing equation for the SDF $$M_{t,t+h}$$ is

$$
\text{E}_t[M_{t,t+h} R^k_{t+h}] = 1. \tag{1}
$$

Gupta and Van Nieuwerburgh (2021) estimate the regression

$$
X^i_{t+h} = a_{t+h} + b_h R^k_{t+h} + e^i_{t+h}, \tag{2}
$$

where $$X^i_{t+h}$$ is the cash flow to loan portfolio $$i$$ at horizon $$h$$, normalized to a $1 investment. The key identification assumption is that $$b_h R^k_{t+h}$$ spans all priced risk in the cash flows, so residuals are orthogonal to the SDF.

**Loan benchmark funds.** Because loan principal balances amortize (more than 80% repaid within 4 years, Figure 3, p. 2032), the paper instruments public security returns $$R^k_{t+h}$$ with the loan's outstanding balance $$z^i_t$$, defining instrumented returns $$\tilde{R}^i_{t+h} = R_{t+h} z^i_t$$. Their price satisfies

$$
\text{E}_t[M_{t,t+h} \tilde{R}^i_{t+h}] = \text{E}_t[M_{t,t+h} R_{t+h} z^i_t] = z^i_t. \tag{3}
$$

Two types of benchmark funds implement this (similar in spirit to the benchmark fund construction in Korteweg and Nagel (2016) for venture capital): a *rollover investment benchmark* $$\bar{F}^{i,k}_{t+h}$$ (pays out the change in loan balance and reinvests the rest each period, price = $1 by equation (4)) and a *gain investment benchmark* $$\bar{G}^{i,k}_{t+h}$$ (goes long risky asset and short risk-free bond, accumulates compounded returns, winds down with the loan balance, price = $0 by equation (5)). The main regression is then

$$
X^i_{t+h} = a_{t+h} + \sum_{k=1}^K \left[ b^k \bar{F}^{i,k}_{t+h} + c^k_h \bar{G}^{i,k}_{t+h} \right] + e^i_{t+h}. \tag{6}
$$

**RAP estimation.** The unconditional mean RAP is

$$
\widehat{RAP} = \text{E}[\text{E}_t[\sum_{h=1}^H M_{t,t+h} X^i_{t+h}]] - 1 = \frac{1}{N}\sum_{i=1}^N [\sum_{h=1}^H P^{\$}_{t,h} \hat{a}_{t+h} + \sum_{k=1}^K \hat{b}^k + \sum_{h=1}^H P^{\$}_{t,h} \hat{e}^i_{t+h}] - 1. \tag{8}
$$

The annualized risk-adjusted return is

$$
\hat{\psi} = \frac{\widehat{RAP}}{\text{WAL}}, \tag{9}
$$

where WAL is the weighted-average life of the outstanding loan balance. Inference uses a nonparametric block bootstrap (100 replications) following Driessen, Lin, and Phalippou (2012).

**Risk factors.** The baseline model uses: a risk-free floating-rate rollover benchmark (analogous to a LIBOR-linked bond), a Term factor (10-year Treasury returns), BBB-rated corporate bond returns, HY-rated corporate bond returns, and CRSP value-weighted stock returns plus the bottom-quintile size portfolio. The model's $$R^2 > 0.99$$ (Table II Panel A, p. 2037), indicating benchmark funds span nearly all variation in loan cash flows.

**Noninterest expense hedonic regression.** To estimate net risk-adjusted returns to shareholders, the paper estimates commercial loan expense ratios using the approach of Hanson et al. (2015). For FRY-9C bank holding companies (1994-2014), the pooled regression is

$$
\frac{\text{Expense}_{it}}{\text{Asset}_{it}} = a + \sum_{k=1}^K b^{(k)} \frac{\text{Asset}^{(k)}_{it}}{\text{Asset}_{it}} + \sum_{j=1}^J c^{(j)} \frac{\text{Deposit}^{(j)}_{it}}{\text{Asset}_{it}} + dX_{it} + e_{it}, \tag{10}
$$

estimated with Fama-MacBeth (1973) cross-sectional regressions and Newey-West (1) standard errors. The commercial loan expense ratio is the predicted value for a hypothetical bank investing only in commercial loans with wholesale funding.

## Empirical specifications

All regressions use quarterly loan cash flows normalized to a $1 investment. The main estimating equation is (6) above, estimated by OLS with nonparametric block bootstrap inference.

**Baseline (R1).** Equation (6) is estimated on 259,300 quarterly observations of the full loan sample (8,125 loans, 1992Q3-2014Q1). Factors: Rf (floating-rate rollover), Term, BBB, HY, Stock. Risk-adjusted returns are computed via equation (8), annualized by WAL (equation (9)). The model achieves $$R^2 = 0.991$$ (Table II Panel A), confirming near-complete spanning.

**Financial constraints (R2).** Loans are sorted into four quartile buckets by the first principal component of four financial-constraint indicators (log firm size with negative sign, log firm age with negative sign, Firm Unrated indicator, Firm Issued Bond indicator with negative sign). Equation (6) is estimated separately for each bucket. Differences in bucket-level annualized RAP test whether banks earn more when borrowers face more severe frictions (Table III, p. 2041). The H-L spread is bootstrapped across the two buckets.

**Screening, monitoring, renegotiation (R3-R5).** Loans are sorted by: (i) contractual maturity (above/below bottom and top quartile), (ii) average industry fixed costs (SG&A from Compustat, two-digit SIC), (iii) predicted ex ante renegotiation probability (Prob(Reneg)) using a linear probability model on loan characteristics, and (iv) EBC tightness (Murfin (2012) measure, following Kermani and Ma (2020)). Equation (6) is estimated separately for each half and differences are bootstrapped (Table IV, p. 2043).

**Bank-level persistence (R6).** Bank-level portfolios aggregate individual loan cash flows weighted by lead-lender retention fraction. Equation (7) (the conditional version of equation (6)) yields a time series of bank-level risk-adjusted returns. Panel regressions with quarter-time fixed effects regress these on lags L4, L8, L12, L16 (in quarters), with standard errors clustered by bank (Table VI, p. 2048). Dollar Value-Added is RAP times portfolio size.

**Net shareholder returns (R7).** Commercial lending expense ratios from equation (10) are subtracted from gross annualized RAP to obtain net shareholder risk-adjusted returns (Table VII, p. 2050; Table IA.XXIV in Internet Appendix for bank-level results).

**Placebo validation (R8).** Equation (6) is applied to corporate bond cash flows (fixed-rate, maturities up to 8 years, from Mergent FISD with TRACE transaction prices). Near-zero bond RAP validates the spanning assumption (Table VIII, p. 2053).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Dealscan (Refinitiv Loan Connector) | Loan originations, amortization schedules, interest rate spreads, covenants, lead lender retention; primary source for loan cash flow construction | [DealScan](/wiki/licensed/dealscan/) (licensed) |
| Compustat (via Chava-Roberts 2008 linking file) | Borrower financial characteristics (firm size, age, fixed costs, financial constraints); performance-pricing covenant ratios | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| CRSP | Stock return factors for benchmark fund construction; value-weighted market return; size quintile portfolio | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| SEC EDGAR (10-K, 10-Q, 8-K filings, web-scraped) | Loan prepayment and refinancing dates not in Dealscan; identifies 94% of prepayment dates accurately | [SEC EDGAR](/wiki/datasets/edgar/) |
| FRY-9C bank holding company data | Bank-level expense decomposition (noninterest expense, compensation, other); bank financial constraint measures | no page yet |
| Corporate bankruptcy databases (UCLA, 8-K) | Default identification and recovery rate estimation (industry-by-year LGD from Moody's Annual Default Report) | no page yet |
| Mergent FISD / TRACE | Corporate bond cash flows and transaction prices for placebo validation test | no page yet |
| Federal Reserve / Treasury (yield curve) | Risk-free ZCB term structure for discounting; 3-month T-bill rate as risk-free proxy | no page yet |
| Moody's Annual Default Report | Industry-by-year loss-given-default (LGD) estimates for loan recovery rates | no page yet |

Sample: 8,125 senior floating-rate term loans to U.S. public borrowers, originated 1992Q3-2014Q1. Security returns data cover 1992Q3-2021Q2. Bank-level tests include 31 banks with at least 40 quarters of data.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13465) if you are: building or testing a risk-adjustment methodology for non-traded private credit instruments; studying the distribution of value added between bank shareholders, employees, and borrowers; extending the cross-sectional tests to other loan types (mortgages, small business); or applying the hedonic expense regression of Hanson et al. (2015) to decompose lending costs. The internet appendix contains extensive robustness tests, the loan-matching algorithm, and the simulation exercise.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. Licensed CC BY-NC 4.0; the verbatim PDF is not hosted here.

> **Attribution (CC BY-NC 4.0).** Flanagan, Thomas.
> "The Value of Bank Lending."
> *The Journal of Finance* 80, no. 4 (August 2025): 2017-2061.
> DOI: 10.1111/jofi.13465. © 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
