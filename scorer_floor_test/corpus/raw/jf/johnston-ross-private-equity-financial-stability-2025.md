---
title: "Private Equity and Financial Stability: Johnston-Ross, Ma & Puri (2025)"
description: >-
  Distilled: Using proprietary FDIC failed-bank bidding data and a quasi-random
  close-bid design, Johnston-Ross, Ma, and Puri show that PE investors filled the
  capital gap in the 2008 crisis by acquiring riskier failed banks that incumbent
  banks avoided, and that PE-acquired banks outperformed on branch preservation,
  deposit growth, small business lending, and regional employment recovery.
  J. Finance 2025, paywalled. Seven core results with source locators, datasets
  used, the empirical design, and the estimating equations.
sidebar:
  label: Johnston-Ross-Ma-Puri 2025
  order: 1
tags: [paper-summary, banking, private-equity, financial-stability, bank-failures,
       natural-experiment, panel-regression, peer-reviewed, unreplicated,
       data:fdic-failed-bank, data:call-reports, data:fdic-summary-of-deposits,
       data:sba-loans, data:qwi-census, data:preqin]
paper:
  authors: Emily Johnston-Ross, Song Ma, Manju Puri
  authorList:
    - { family: Johnston-Ross, given: Emily, affiliation: "Federal Deposit Insurance Corporation" }
    - { family: Ma, given: Song, orcid: "0000-0001-8582-4735", affiliation: "Yale University and NBER" }
    - { family: Puri, given: Manju, affiliation: "Duke University and NBER" }
  year: 2025
  venue: "The Journal of Finance 80(1), February 2025, 163-210"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13399
  jel:
    codes: [G21, G28, G34]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - "Banking stability, regulation, efficiency"
    - "Corporate Finance and Governance"
    - "Global Financial Crisis and Policies"
  dataAccess: proprietary-confidential
  outcome:
    - bank branch closure probability post-acquisition
    - deposit growth in failed-bank branches
    - small business lending quantity and pricing
    - regional employment and income growth
  outcomeClass: [credit-supply, firm-real-outcomes, bank-funding]
  license: >-
    Wiley VOR terms and conditions (not open access); no CC licence found in
    Crossref metadata (license URL: http://onlinelibrary.wiley.com/termsAndConditions#vor,
    content-version vor, delay-in-days 0, start 2024-11-27). Paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley Online Library; confirmed via Crossref metadata 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 6

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [logit-regression, panel-regression, difference-in-differences]
    identification: natural-experiment

  contributionType: [new-fact, new-data]
  introducesData: true

  mechanisms: [financial-constraint, information-asymmetry, agency]

  scope:
    region: US
    assetClass: "bank loans, deposits (failed commercial banks)"
    period: 2009-01..2014-12
    frequency: annual
    dataType: [administrative, accounting, market]
    granularity: [firm, individual, transaction]
    n: "456 failed banks resolved 2009-2014; quasi-random sample of 48 close-bid auctions"

  findings:
    - ref: R1
      outcome: bank branch closure probability post-acquisition
      metric: pp-effect
      value: "-14.8 pp (t-stat implied by SE=0.037, coef=-0.148***)"
      direction: negative
      vsBenchmark: "73.6% lower than the 20.1% mean branch closure rate (Table VI col 1, quasi-random sample)"
    - ref: R2
      outcome: bank branch closure probability post-acquisition
      metric: pp-effect
      value: "-7.0 pp (coef=-0.070**, SE=0.029)"
      direction: negative
      vsBenchmark: "PE-acquired banks less likely to close and exit a county entirely vs bank acquirers (Table VI col 2)"
    - ref: R3
      outcome: deposit growth in failed-bank branches
      metric: pp-effect
      value: "35.6 pp higher three-year deposit growth (coef=0.356***, SE=0.111)"
      direction: positive
      vsBenchmark: "vs bank-acquired branches in same county, quasi-random sample (Table VII col 2)"
    - ref: R4
      outcome: small business lending quantity
      metric: pp-effect
      value: "32% higher growth in SBA loan number (coef=0.320**, SE=0.112)"
      direction: positive
      vsBenchmark: "vs bank-acquired counties, quasi-random sample (Table VIII Panel A col 1)"
    - ref: R5
      outcome: small business lending pricing
      metric: basis-points
      value: "SBA loan interest rate 32 bp lower (coef=-0.323*, SE=0.147)"
      direction: negative
      vsBenchmark: "5% below the noncond. mean of 6.42%; counties with PE-acquired failed banks (Table VIII Panel A col 3)"
    - ref: R6
      outcome: regional employment and income growth
      metric: pp-effect
      value: "6.5 pp higher employment growth (coef=0.065**, SE=0.029); 1.5 pp higher total income growth (coef=0.015***, SE=0.006)"
      direction: positive
      vsBenchmark: "counties with PE-acquired vs bank-acquired failed banks, quasi-random sample (Table IX Panel A)"
    - ref: R7
      outcome: FDIC loss share claims
      metric: coefficient
      value: "coef=-0.015 (t=-0.544), statistically indistinguishable from zero"
      direction: none
      vsBenchmark: "PE acquirers do not cost the FDIC more in loss share claims than bank acquirers (Table X col 1)"

  resultType: new-finding

  relatesTo:
    - { cite: "Granja, Matvos & Seru (2017)", doi: '10.1111/jofi.12512', relation: builds-on, note: "adopts their failed-bank resolution framework and the key insight that local bank capitalization determines acquirer identity" }
    - { cite: "Bernstein, Lerner & Mezzanotti (2019)", doi: '10.1093/rfs/hhy078', relation: builds-on, note: "documents PE liquidity-provision role during the crisis; this paper extends to failed-bank resolution" }
    - { cite: "Hotchkiss, Smith & Stromberg (2021)", doi: '10.1093/rof/rfac005', relation: builds-on, note: "PE expertise in distressed turnarounds is a proposed channel for positive bank performance" }
    - { cite: "Egan, Lewellen & Sunderam (2022)", relation: builds-on, note: "bank value decomposition framework used to attribute deposit gains to pricing, branch network, and productivity" }

  openQuestions:
    - "Whether PE participation in failed-bank resolution would replicate in future crises with different regulatory environments or PE fund structures, given that the OCC shelf-charter program was specific to the 2008 period (p. 204)."
    - "The extent to which positive effects are driven by regulatory scrutiny unique to PE acquirers (higher capital requirements, restrictions on affiliate lending) versus genuine operational expertise, since the two cannot be fully separated in the data (p. 203)."
    - "Whether results generalize beyond the US to emerging economies where government bank ownership is higher and the regulatory framework differs (p. 169)."

  replicationCode:
    status: available

  licenceVerification:
    - source: "Crossref REST API works/10.1111/jofi.13399"
      checked: 2026-06-06
      by: "paper-distiller (claude-sonnet-4-6)"
      found: "license[0].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-11-27; no CC licence present; paywalled."

  extraction:
    - by: "paper-distiller (claude-sonnet-4-6)"
      date: 2026-06-06
      role: extracted
      note: "Full PDF read (pp. 163-210); seven core results extracted with table/figure locators. Crossref and OpenAlex metadata confirmed. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core results rows confirmed exact (Table VI cols 1-2, Table VII col 2, Table VIII Panel A cols 1 and 3, Table IX Panel A cols 2-3, Table X col 1); Equations (1) and (2) confirmed term-by-term; relatesTo body citations confirmed; no em-dashes; no errors found."
---

**What this is.** The paper's core results, the empirical design (quasi-random close-bid identification), and the estimating equations: enough to know what was found and how, without reading the full 48 pages. To replicate or extend, read the original at [doi.org/10.1111/jofi.13399](https://doi.org/10.1111/jofi.13399).

## TL;DR

Using proprietary FDIC failed-bank bidding records for 482 bank failures resolved between 2009 and 2014, Johnston-Ross, Ma, and Puri document that PE investors systematically acquired the riskier, more undercapitalized failed banks in regions where neighboring banks were also distressed, filling a funding gap that incumbent banks could not. A close-bid quasi-random design (48 auctions where the PE and bank bids differed by less than 5% of assets) shows that PE-acquired banks subsequently closed fewer branches, grew deposits 35 percentage points faster over three years, expanded small business lending by 32%, lowered SBA loan rates by about 32 basis points, and supported faster regional employment and income growth, all without incurring higher FDIC loss-share claims. PE investors held failed banks for 6.5 years on average before selling, mostly to local banks, earning roughly a 12% IRR.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | PE-acquired bank branches are **14.8 pp less likely to close** within three years post-acquisition | Table VI, col (1), p. 190; quasi-random sample | coef = -0.148\*\*\* (SE = 0.037); base rate = 20.1%; 73.6% reduction |
| R2 | PE-acquired banks are **7.0 pp less likely to close and exit a county entirely** | Table VI, col (2), p. 190 | coef = -0.070\*\* (SE = 0.029) |
| R3 | **Deposit growth 35.6 pp higher** in PE-acquired banks over three years post-acquisition | Table VII, col (2), p. 193; quasi-random sample, two-failed-bank county pairs | coef = 0.356\*\*\* (SE = 0.111) |
| R4 | **SBA loan count grows 32% more** in counties where PE acquires the failed bank | Table VIII, Panel A, col (1), p. 196 | coef = 0.320\*\* (SE = 0.112); R2 = 0.797 |
| R5 | **SBA loan interest rates 32 bp lower** in PE-acquired counties | Table VIII, Panel A, col (3), p. 196 | coef = -0.323\* (SE = 0.147); noncond. mean = 6.42% |
| R6 | **Employment 6.5 pp higher and total personal income 1.5 pp higher** in PE-acquired counties | Table IX, Panel A, cols (2) and (3), p. 197 | employment coef = 0.065\*\* (SE = 0.029); income coef = 0.015\*\*\* (SE = 0.006) |
| R7 | **PE-acquired banks do not claim more FDIC loss-share losses** than bank acquirers | Table X, col (1), p. 199 | coef = -0.015 (t = -0.544), indistinguishable from zero |

**Overall (paper's conclusion).** PE investors complemented incumbent banks in the failed-bank market by acquiring the riskier, harder-to-sell banks that local banks were unwilling or unable to acquire. They stabilized those banks, preserved branch networks, grew deposits, increased small business lending, and contributed to regional economic recovery, without generating excess costs for the FDIC. PE participation in failed-bank resolution helped reduce the FDIC's cost of crisis resolution by an estimated $3.63 billion (roughly 5% of the DIF's total crisis losses).

## Theory / model

The paper has no formal structural model. It tests two complementary hypotheses motivated by the PE literature and the institutional setting of FDIC failed-bank auctions.

**Hypothesis 1 (Complementary selection).** PE investors have higher risk tolerance and more stable funding than distressed local banks, so they should bid on and acquire the riskier segment of the failed-bank market that incumbent banks cannot or will not purchase. The prediction is that PE-acquired banks are more undercapitalized, have riskier loan portfolios (higher C&D and OREO shares), lower profitability, and are located in regions where neighboring banks are also in distress (pp. 163-165).

**Hypothesis 2 (Positive turnaround).** PE investors' expertise in distressed firms (Hotchkiss, Smith, and Stromberg (2021)) and their more stable funding (Bernstein, Lerner, and Mezzanotti (2019)) allow them to turn around failed banks, so PE-acquired banks should outperform bank-acquired failed banks on branch stability, deposit growth, lending, and real outcomes. The paper also draws on the bank value decomposition framework of Egan, Lewellen, and Sunderam (2022) to attribute deposit gains across pricing, branch network, and productivity channels (pp. 194-195). The confounding threat is selection: PE acquires worse banks, so raw comparisons would understate or reverse the effect (p. 186).

**Identification strategy.** The paper resolves the selection problem via a close-bid quasi-random design developed on the foundation of Granja, Matvos, and Seru (2017), who show that local bank capitalization is the key determinant of failed-bank acquirer identity. For failed banks bid on by both PE investors and banks, the paper restricts to auctions where the winner's margin over the cover bid is less than 5% of total bank assets. Within this subsample, whether a PE investor or a bank wins the auction is treated as quasi-random, and Table V shows that the 25 PE-won and 23 bank-won banks in the sample are statistically identical across dozens of pre-auction characteristics (Table V, pp. 188-189).

## Method

**PE-acquisition probability (Section III).** Equation (1) (p. 177) is a logit regression:

$$
\Pr(PE = 1) = \Phi\!\left(\alpha + \beta \cdot X_i + \gamma \cdot \text{Control}_i + \theta_t + \varepsilon_i\right) \tag{1}
$$

where $$X_i$$ is a bank characteristic (tier 1 capital ratio, core deposits, net interest margin, C&D loans, OREO), $$\text{Control}_i$$ includes log total assets, and $$\theta_t$$ are year-quarter fixed effects. The sample is the cross-section of 456 failed banks resolved 2009-2014. Marginal effects at the sample mean are reported (Table III). The builds from `logit-regression` for the selection analysis and from `panel-regression` for the performance analysis.

**Post-acquisition performance (Section IV).** Equation (2) (p. 187) is a local linear panel regression:

$$
\text{Performance}_{b,i,t,z} = \alpha + \beta \cdot PE_i + \gamma \cdot \text{Control}_i + \theta_{t \times z} + \varepsilon_i \tag{2}
$$

where $$\text{Performance}$$ is the outcome (branch closure indicator, deposit growth, SBA loan count/amount/rate, employment growth, income growth) for branch $$b$$ of failed bank $$i$$ that failed in year $$t$$ in region $$z$$, $$PE_i$$ equals 1 if a PE investor won the auction, and $$\theta_{t \times z}$$ are state-by-failed-year fixed effects absorbing local time trends. Standard errors are double-clustered at the state and failed-year levels. The estimation uses the quasi-random subsample (48 auctions) as the preferred specification.

## Empirical specifications

**Selection analysis (Table III).** Cross-sectional logit on 456 failed banks with failed year-quarter fixed effects and robust standard errors. Panel A: dependent variable = PE acquired (1/0); regressors = bank-level health measures (tier 1 ratio, core deposits, net interest margin, C&D loans, OREO). Panel B: same but regressors = neighboring bank health measures (neighboring tier 1 ratio, noncurrent loans, OREO, number of large local banks, number of failed banks in state). Ties results to R1-R2 (Table III, pp. 180-182).

**Branch closures (Table VI).** Panel regression at the branch level. The preferred specification (columns 1-2) uses the quasi-random sample. Dependent variable: indicator = branch closed within three years, or branch closed and county exited. Controls include tier 1 capital, core deposits, C&D loans, OREO, and log assets. Fixed effects: state x failed-year. Standard errors double-clustered at state and failed-year levels (Table VI, p. 190).

**Deposit growth (Table VII).** Panel regression at the bank-county level. Dependent variable: one-year or three-year change in branch-level deposits. For PE acquirers using shelf charters, all branches in the local region are counted; for inflatable charters or multiple acquisitions, combined PE and acquirer branches are included to address consolidation effects. An alternative specification restricts to counties where the acquirer has no pre-existing branch (columns 5-6, confirming results hold without overlap) (Table VII, p. 193).

**Small business lending (Table VIII).** County-level regression on three-year growth in SBA 7(a) loan number, amount, interest rate, and average loan size. Quasi-random sample: 276 county observations. Full sample: 2,181 observations. State x failed-year fixed effects, double-clustered standard errors. Specification matches equation (2) (Table VIII, pp. 195-196).

**Regional economic recovery (Table IX).** County-level panel on three-year growth in startup employment (Census QWI, firm age 0-1), total employment, total personal income (IRS SOI), and per capita income. Same fixed effects and SE clustering as Table VIII. Both quasi-random (276 obs) and full sample (2,181 obs) reported (Table IX, p. 197).

**Loss share claims (Table X).** Bank-level regression on aggregate claimed loss rate (total losses / covered assets) and incurred loss rate (losses net of FDIC reimbursements). Uses proprietary FDIC loss-share portfolio data. Controls match equation (1). State and failed-year fixed effects. 304 observations (full); 38 observations in quasi-random subsample (Table X, p. 199).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| FDIC proprietary failed-bank bidding data (P&A transaction records, bid values, acquirer identities, FDIC least-cost estimates) | Core identification: close-bid quasi-random design; failed-bank selection analysis | no page yet |
| FDIC Call Reports (Consolidated Reports of Condition and Income) | Failed-bank and neighboring-bank financial characteristics (tier 1 capital, loan composition, deposits) | [Call Reports](/wiki/datasets/call-reports/) |
| FDIC Summary of Deposits (SOD) | Branch-level deposit balances and locations for closure and deposit growth analysis | [FDIC Summary of Deposits](/wiki/datasets/fdic-summary-of-deposits/) |
| FDIC Reports of Structure Change | Branch openings/closings; county exit analysis | no page yet |
| FDIC proprietary loss-share data | Loss-share claims by acquirer type; Table X | no page yet |
| Preqin (PE fund data) | PE fund size, vintage, first-time fund indicator; consortium-level PE ownership | [Preqin](/wiki/licensed/preqin/) (licensed) |
| RateWatch | Branch-level deposit interest rates for deposit rate analysis (Panel B, Table VII) | no page yet |
| U.S. Census Quarterly Workforce Indicators (QWI) | County-level startup employment and total employment for regional recovery analysis | [QWI](/wiki/datasets/qwi-census/) |
| IRS Statistics of Income (SOI) | County-level personal income and per capita income | no page yet |
| Small Business Administration (SBA) 7(a) loan data | Number, amount, interest rate, and average size of small business loans by county | [SBA loans](/wiki/datasets/sba-loans/) |
| S&P Global Market Intelligence | PE exit deal values and IPO data; IRR calculation | no page yet |

Sample: 456 failed banks resolved via Purchase and Assumption transactions 2009-2014; 62 PE-acquired, 393 bank-acquired (27 excluded: no least-cost bid or bridge-bank status). Quasi-random sample: 48 banks from close-bid auctions (bid difference below 5% of total bank assets), of which 25 PE-acquired and 23 bank-acquired.

## When to read the full paper

Read the original (link above) if you are: (i) building a related quasi-random design for financial-institution interventions and want the balance test methodology (Table V, pp. 187-189); (ii) studying how PE ownership structures (shelf vs. inflatable charters, BHC formation) interact with bank regulation; (iii) quantifying the FDIC cost savings from PE participation (the $3.63 billion back-of-envelope, pp. 202-203); or (iv) studying the management channel via hand-collected CEO characteristics (Table XII, p. 202). The Internet Appendix (referenced at p. 210) contains additional robustness tables (IA.I through IA.XIII) and the replication code.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. Published by Wiley on behalf of the American Finance Association. Copyright 2024 the American Finance Association. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled; no CC licence is present in the Crossref metadata. This page contains extracted summary information only (extract-only).

> Johnston-Ross, Emily, Song Ma, and Manju Puri. "Private Equity and Financial Stability: Evidence from Failed-Bank Resolution in the Crisis." *The Journal of Finance* 80, no. 1 (February 2025): 163-210. DOI: 10.1111/jofi.13399.
