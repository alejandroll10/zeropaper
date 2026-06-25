---
title: "Arbitrage Capital of Global Banks: Anderson, Du & Schlusche (2025)"
description: >-
  Distilled: The 2016 U.S. money market fund reform cut banks' unsecured
  wholesale funding by about $600 billion; global banks responded by cutting
  liquid arbitrage positions (IOER and CIP arbitrage), not loan supply. J.
  Finance 2025, U.S. Government work (public domain in USA). Eight core
  results with source locators, datasets used, the model, and the
  identification strategy.
sidebar:
  label: Anderson-Du-Schlusche 2025
  order: 1
tags: [paper-summary, banking, wholesale-funding, arbitrage, money-markets,
       monetary-policy, financial-regulation, panel-regression,
       instrumental-variables, peer-reviewed, unreplicated,
       data:dtcc, data:fr2420, data:fr2644, data:n-mfp, data:dealscan,
       data:wrds]
paper:
  authors: Alyssa Anderson, Wenxin Du, Bernd Schlusche
  authorList:
    - { family: Anderson, given: Alyssa G., orcid: "0009-0004-7342-7942", affiliation: Federal Reserve Board }
    - { family: Du, given: Wenxin, orcid: "0000-0002-7069-5974", affiliation: Harvard Business School }
    - { family: Schlusche, given: Bernd, affiliation: Federal Reserve Board }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2591–2638
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13478
  jel:
    codes: [G21, G28, E52]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Banking stability, regulation, efficiency
    - Global Financial Crisis and Policies
    - Economic Theory and Policy
  dataAccess: proprietary-confidential
  outcome:
    - potential arbitrage capital (IOER and CIP) as a share of total assets
    - IOER arbitrage position (proxy) as a share of total assets
    - total bank assets and cash balances
    - loan provision
    - bank funding costs (unsecured wholesale funding rates)
  outcomeClass: [bank-funding, credit-supply, asset-prices]
  license: >-
    U.S. Government work, public domain in the USA (per artifact p.2591:
    "This article is a U.S. Government work and is in the public domain in
    the USA"); Crossref DOI metadata records Wiley termsAndConditions#vor
    (content-version vor, delay-in-days 0, start 2025-08-18) with no CC
    licence; rights signal conflict noted.
  licenseShort: public domain (US Gov)
  access: paywalled
  machineAccess: blocked-paywall (Wiley site wrapper; publisher page returns
    paywalled abstract, 2026-06-05)
  redistribution: extract-only (U.S. Government work public domain in USA;
    Crossref records Wiley ToC only; conflict noted; conservatively extract-only
    pending resolution)
  resultsCount: 8
  citedByCount: 3
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables]
    identification: instrument
  contributionType: [new-fact, measurement]
  mechanisms: [intermediary-constraint, limits-to-arbitrage, liquidity]
  scope:
    region: global (US-based entities of 58 global banks)
    assetClass: wholesale funding markets (federal funds, Eurodollars, CD, CP, repo)
    period: 2015-10..2017-06
    frequency: daily
    dataType: [market, administrative, accounting]
    granularity: [firm, transaction]
    n: "58 global banks; daily transaction-level data; 232 bank-quarter observations in main regressions"
  findings:
    - ref: R1
      outcome: potential arbitrage capital (IOER and CIP) as a share of total assets
      metric: coefficient
      value: "0.90 (IV, SE 0.28), significant at 1%"
      direction: positive
      vsBenchmark: 1% decline in prime MMF unsecured funding -> 0.9% decline in IOER arbitrage capital (Table I, Panel B col. 1)
    - ref: R2
      outcome: potential arbitrage capital (IOER and CIP) as a share of total assets
      metric: coefficient
      value: "0.91 (IV, SE 0.28), significant at 1%"
      direction: positive
      vsBenchmark: 1% decline in prime MMF unsecured funding -> 0.91% decline in CIP arbitrage capital (Table I, Panel B col. 2)
    - ref: R3
      outcome: IOER arbitrage position (proxy) as a share of total assets
      metric: coefficient
      value: "0.84 (IV, SE 0.25), significant at 1%; IOER arbitrageurs: interaction coefficient 0.85 (SE 0.17)"
      direction: positive
      vsBenchmark: 1% decline in prime MMF funding -> 0.84% decline in IOER arbitrage position; arbitrageurs respond ~4x more (Table I, Panel B cols. 3-4)
    - ref: R4
      outcome: total bank assets and cash balances
      metric: coefficient
      value: "Total assets: 0.83 (IV, SE 0.14), p<0.01; cash: 0.76 (IV, SE 0.14), p<0.01; loans: 0.03 (not significant)"
      direction: positive
      vsBenchmark: 1% decline in prime MMF funding -> 0.83% decline in total assets, 0.76% in cash; loans insignificant (Table IV)
    - ref: R5
      outcome: loan provision
      metric: coefficient
      value: "0.03 (SE 0.03), not significant; syndicated loan origination also insignificant"
      direction: none
      vsBenchmark: no significant loan reduction vs. European debt crisis 2011-2012 where coefficient >0.2 (Table IV; Internet Appendix Table IA.XIII)
    - ref: R6
      outcome: bank funding costs (unsecured wholesale funding rates)
      metric: basis-points
      value: "-4.99 (IV, SE 1.57) bps for tenors >=6 months; insignificant for tenors <6 months"
      direction: negative
      vsBenchmark: 1% decline in unsecured funding -> ~5 bps rise in long-term funding rates (>=6M); ED and CD show significant negative price effects (Table VI)
    - ref: R7
      outcome: IOER arbitrage position (proxy) as a share of total assets
      metric: coefficient
      value: "LCR2 banks: 1.05 (SE 0.11), p<0.01; LCR3 banks: 1.61 (SE 0.52), p<0.01; LCR1 banks: 0.02 (not significant)"
      direction: positive
      vsBenchmark: banks with tightest LCR constraint (lowest HQLA/unsecured funding ratio) cut arbitrage 80x more than high-HQLA banks (Table VIII)
    - ref: R8
      outcome: IOER arbitrage position (proxy) as a share of total assets
      metric: coefficient
      value: "Quarter-end unsecured MMF holdings fell from ~$170B in 2015Q4 to ~$30B in 2016Q4; share of unsecured QE effects in total QE effects fell from ~0.6 to ~0.1"
      direction: negative
      vsBenchmark: muted quarter-end window-dressing consistent with reduced arbitrage positions post-reform (Figure 8)
  resultType: new-finding
  relatesTo:
    - { cite: "Ivashina, Scharfstein & Stein (2015)", doi: '10.1093/qje/qjv017', relation: contradicts, note: "that paper finds loan reduction in response to MMF funding shock (European debt crisis 2011-2012); this paper finds no loan reduction for the 2016 MMF reform, attributing the difference to post-GFC LCR regulations" }
    - { cite: "Du, Tepper & Verdelhan (2018)", doi: '10.1111/jofi.12620', relation: builds-on, note: "CIP arbitrage framework and persistent CIP deviations used as motivation for CIP arbitrage capital measure" }
    - { cite: "Bech & Klee (2011)", doi: '10.1016/j.jmoneco.2011.05.007', relation: builds-on, note: "IOER arbitrage mechanics and segmentation in the federal funds market" }
    - { cite: "Keating & Macchiavelli (2017)", doi: '10.17016/feds.2017.124', relation: extends, note: "IOER arbitrage in post-crisis money markets; this paper measures quantity of arbitrage capital and positions directly" }
    - { cite: "Goldsmith-Pinkham, Sorkin & Swift (2020)", doi: '10.1257/aer.20181047', relation: builds-on, note: "Bartik instrument diagnostic tests followed throughout the paper" }
    - { cite: "Correa, Sapriza & Zlate (2016)", relation: contradicts, note: "finds bank lending channel during European sovereign crisis; not found here for 2016 MMF reform" }
  openQuestions:
    - "Whether liquidity risk migrates from large global banks (which have become more resilient to wholesale funding dry-ups) to smaller banks and nonbank financial institutions as large global banks improve their liquidity profiles under Basel III (p. 2635)."
    - "How deposit outflows composed primarily of retail or more stable institutional deposits (rather than wholesale funding) would affect credit supply, given the distinct LCR treatment of stable insured deposits vs. unsecured wholesale funding (p. 2635)."
    - "The potential effects of the July 2023 MMF reform (mandatory liquidity fees on prime MMFs) on global banks' wholesale funding mix and arbitrage capital, which is the direct next application of this paper's framework (p. 2635)."
  replicationCode:
    status: available
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13478
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-18; no CC licence in Crossref; artifact p.2591 asserts U.S. Government work, public domain in USA"
  rightsSignalConflict: true
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full PDF read (pp. 2591-2638); eight results extracted from tables and figures with locators. Not human-verified. Not reproduced. Replication code is referenced in the paper (Supporting Information) but has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; one fix applied: LCR3 significance corrected from ** (p<0.05) to *** (p<0.01) in both findings[] value and Core results table (Table VIII, p. 2633 shows three stars); all equations and specifications verified term-by-term; all other R1-R8 magnitudes, SEs, and locators confirmed correct. Removed introducesData and new-data from contributionType: the paper builds its arbitrage-capital measure from existing supervisory and regulatory sources (FR 2420/2644, DTCC, N-MFP), not a new dataset or source."
---

**What this is.** The paper's core results, the arbitrage capital framework it develops, and the Bartik IV identification strategy: enough to know what it found and how, without reading all 48 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13478).

## TL;DR

The 2016 U.S. money market fund (MMF) reform required institutional prime funds to adopt floating NAV, triggering a roughly $600 billion shift in unsecured wholesale funding away from global banks. Using granular daily supervisory transaction-level data on wholesale funding instruments (federal funds, Eurodollars, commercial paper, CDs, repos) for 58 top-tier global banks, the paper documents that banks hold about $1.5 trillion in potential "arbitrage capital": unsecured wholesale funding deployed in interest-on-excess-reserves (IOER) arbitrage (borrow short-term dollars below the IOER rate, park at the Fed) and covered interest parity (CIP) arbitrage (borrow dollars, lend in FX forward/swap markets). The primary response to the funding shock was a cutback in these liquid arbitrage positions, not a reduction in loan provision. This overturns the traditional bank lending channel prediction for this episode, and is attributed to post-GFC Basel III LCR regulations that effectively require unsecured wholesale funding to be invested in high-quality liquid assets.

## Core results

Magnitudes and significance are as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | MMF reform significantly reduced **IOER arbitrage capital**: 1% decline in prime MMF unsecured funding -> 0.9% decline in potential IOER arbitrage capital | Table I Panel B col. 1, p. 2613 | IV coeff. 0.90 (SE 0.28)\*\*\* |
| R2 | MMF reform significantly reduced **CIP arbitrage capital**: 1% decline in prime MMF unsecured funding -> 0.91% decline in potential CIP arbitrage capital | Table I Panel B col. 2, p. 2613 | IV coeff. 0.91 (SE 0.28)\*\*\* |
| R3 | **IOER arbitrage position** declined; IOER arbitrageurs responded ~4x more than non-arbitrageurs | Table I Panel B cols. 3-5, p. 2613 | Full sample: 0.84 (SE 0.25)\*\*\*; arbitrageur interaction: 0.85 (SE 0.17)\*\*\* |
| R4 | Bank **total assets and cash** declined significantly; **loans** did not | Table IV cols. 1-3, p. 2620 | Total assets: 0.83 (SE 0.14)\*\*\*; cash: 0.76 (SE 0.14)\*\*\*; loans: 0.03 (SE 0.03), not significant |
| R5 | **No evidence of loan reduction** from MMF reform (contrast: European debt crisis 2011-2012 shows significant loan reduction) | Table IV col. 3, p. 2620; Internet Appendix Table IA.XIII | MMF reform: loans coeff. 0.03 (not sig.); European crisis: coeff. >0.20 and significant |
| R6 | **Funding costs rose** for longer-tenor unsecured instruments: ~5 bps increase for maturities >=6 months per 1% funding decline | Table VI col. 2, p. 2625 | IV coeff. -4.99 bps (SE 1.57)\*\*\*; <6M tenors insignificant |
| R7 | **LCR-constrained banks** (lowest HQLA/unsecured funding ratio) cut arbitrage positions most; high-HQLA banks show no significant response | Table VIII, p. 2633 | LCR2: 1.05 (SE 0.11)\*\*\*; LCR3: 1.61 (SE 0.52)\*\*\*; LCR1: 0.02 (not sig.) |
| R8 | **Quarter-end window-dressing** in unsecured funding declined markedly: share of unsecured quarter-end effects in total quarter-end effects fell from ~0.6 (2015Q4) to ~0.1 (2016Q4) | Figure 8, p. 2627 | Unsecured QE-end effects: ~$170B in 2015Q4 to ~$30B in 2016Q4 |

**Overall (paper's conclusion).** The 2016 MMF reform reduced the availability of potential arbitrage capital for global banks. Contrary to the traditional bank lending channel, banks did not reduce their credit supply, but instead cut down their liquid arbitrage positions: the IOER arbitrage and the CIP arbitrage. Banks that had tighter LCR constraints and a higher reliance on arbitrage activity (IOER arbitrageurs) responded most strongly. The use of unsecured wholesale funding as arbitrage capital makes large global banks more resilient to negative wholesale funding shocks, as they can swiftly reduce arbitrage positions in response to wholesale funding dry-ups. However, this business model shift also reduces the usefulness of short-term wholesale funding for maturity and liquidity transformation.

This result contrasts with Ivashina, Scharfstein, and Stein (2015), who find significant loan reduction following MMF funding shocks during the European debt crisis (2011-2012), before Basel III LCR regulations were in place. It also contrasts with Correa, Sapriza, and Zlate (2016), who document the bank lending channel during the European sovereign crisis. The IOER arbitrage framework builds on Bech and Klee (2011) and Keating and Macchiavelli (2017); the CIP arbitrage motivation comes from Du, Tepper, and Verdelhan (2018). The Bartik identification follows Goldsmith-Pinkham, Sorkin, and Swift (2020).

## Theory / model

The paper has no formal equilibrium model. It develops two measurement frameworks for arbitrage capital and positions, and uses them to study the transmission of a funding shock.

**IOER arbitrage.** A bank engages in IOER arbitrage by raising unsecured dollar funding at a rate below the IOER rate and parking the proceeds as reserves at the Federal Reserve. The potential IOER arbitrage capital for bank $$i$$ at time $$t$$ is defined as the total outstanding unsecured wholesale funding borrowed at a rate below the IOER rate (equation 1, p. 2602):

$$
Y_{i,t}^{\text{IOER}} = \sum_{n,k} y_{i,n,k,t} \left[ y_{i,n,k,t} \, | \, r_{i,n,k,t-n} < r_{t-n}^{\text{IOER}} \right], \tag{1}
$$

where $$y_{i,n,k,t}$$ denotes the outstanding amount at time $$t$$ for instrument $$k$$ with remaining maturity $$n$$ issued by bank $$i$$, and $$r_{i,n,k,t-n}$$ denotes the issuing rate on the issuance date $$t-n$$. A proxy for the IOER arbitrage position is then:

$$
Q_{i,t}^{\text{IOER}} = \min(\text{ExcessReserves}_{i,t},\, Y_{i,t}^{\text{IOER}}),
$$

where $$\text{ExcessReserves}_{i,t}$$ denotes excess reserve balances held at the Federal Reserve by bank $$i$$ at time $$t$$ (p. 2603).

**CIP arbitrage.** A bank engages in CIP arbitrage by borrowing unsecured dollars at a rate below the swapped yen rate and lending the dollars in the FX forward/swap markets. The swapped yen rate in dollars is (p. 2603):

$$
r_{n,t}^{\yen \to \$} = r_{n,t}^{\yen} - \rho_{n,t}^{\yen \to \$},
$$

where $$r_{n,t}^{\yen}$$ is the yen OIS rate with tenor $$n$$ and $$\rho_{n,t}^{\yen \to \$}$$ is the FX forward premium to swap yen into dollars. Analogously to equation (1), potential CIP arbitrage capital is (equation 2, p. 2603):

$$
Y_{i,t}^{\text{CIP}} = \sum_{n,k} y_{i,n,k,t} \left[ y_{i,n,k,t} \, | \, r_{i,n,k,t-n} < r_{n,t-n}^{\yen \to \$} \right]. \tag{2}
$$

**Identification logic.** The key challenge is that changes in equilibrium quantities could reflect both MMF funding supply shocks and banks' own demand for funding. The paper isolates the funding supply shock via a Bartik-style shift-share instrument. The exclusion restriction is that banks' preform exposure shares to different prime fund complexes are uncorrelated with unobserved bank-level demand shocks. The paper follows the Goldsmith-Pinkham, Sorkin, and Swift (2020) diagnostic protocol and shows pre-trend tests pass (Figure 7, p. 2618).

## Method

**Baseline OLS regression.** The benchmark OLS specification regresses changes in bank $$i$$'s outcome variable $$\Delta Y_{i,t}$$ on changes in prime funds' holdings of bank $$i$$'s unsecured debt, normalized by 2014 total assets $$\text{Asset}_{i,0}$$ (p. 2611):

$$
\Delta Y_{i,t} / \text{Asset}_{i,0} = \alpha + \beta \,\Delta \text{hold}_{i,t}^{\text{Unsec}} / \text{Asset}_{i,0} + \epsilon_{i,t}.
$$

Changes are quarterly over the reform implementation period (October 2015 to October 2016), using four non-quarter-end quarterly windows to avoid window-dressing contamination. All specifications include time fixed effects; standard errors are clustered at the bank level.

**Bartik IV.** To isolate the supply shock from banks' funding demand, the Bartik-style shift-share instrument for $$\Delta \text{hold}_{i,t}^{\text{Unsec}} / \text{Asset}_{i,0}$$ is (equation 3, p. 2611):

$$
\hat{B}_{i,t} = \sum_j \text{Share}_{i,j,0} \cdot \text{Shift}_{j,t} = \sum_j (s_{i,j,0} / \text{Asset}_{i,0}) \times \Delta\text{aum}_{j,t}, \tag{3}
$$

where $$s_{i,j,0}$$ is the lagged (May 2014) share of bank $$i$$ in fund complex $$j$$'s portfolio, and $$\Delta\text{aum}_{j,t}$$ is the change in AUM of all prime funds within complex $$j$$. The instrument exploits the pooled-exposure design: banks with higher preform exposure to funds that suffered larger AUM losses received larger funding shocks, independently of their own demand. The "share" component captures preform exposure; the "shift" component (aggregate AUM changes at the fund complex level) is not attributable to individual bank funding demand. Banks borrow from 84 fund complexes, so the Bartik is a weighted average of 84 individual instruments.

**Leave-one-out variant.** To address concerns that a bank's own demand shifts the aggregate AUM of a fund complex, the paper also implements a leave-one-out estimator (equation 4, p. 2619):

$$
\tilde{B}_{i,t} = \sum_j (s_{i,j,0} / \text{Asset}_{i,0}) \times \Delta(\text{aum}_{j,t} - \text{aum}_{i,j,t}). \tag{4}
$$

Results are very similar to the baseline Bartik.

**Arbitrage profit regressions.** The volume-weighted IOER arbitrage profit is (p. 2628):

$$
\pi_t^{\text{IOER}} = \sum_{i,n,k} (y_{i,n,k} / Y_{i,t}^{\text{IOER}})(r_{t-n}^{\text{IOER}} - r_{i,n,k,t-n}). \tag{5 (unnumbered in paper)}
$$

Changes in daily average arbitrage profits are then regressed on daily changes in potential arbitrage capital, with a post-reform indicator and an interaction, for both IOER and CIP arbitrage:

$$
\Delta \pi_t^{\text{IOER}} = \alpha + \beta \,\Delta Y_t^{\text{IOER}} + \gamma \,\text{Post}_t + \delta \,\text{Post}_t \times \Delta Y_t^{\text{IOER}} + \epsilon_t. \tag{5}
$$

$$
\Delta \pi_{n,t}^{\text{CIP}} = \alpha + \beta \,\Delta Y_t^{\text{CIP}} + \gamma \,\text{Post}_t + \delta \,\text{Post}_t \times \Delta Y_t^{\text{CIP}} + \epsilon_t. \tag{6}
$$

## Empirical specifications

**Sample.** 58 global banks that frequently trade with U.S. prime MMFs (accounting for ~90% of total prime fund holdings of bank securities). Quarterly observations from October 2015 to October 2016 (four quarters), avoiding quarter-ends. Main regression samples: N = 232 (all banks x four quarters). Balance sheet regressions use 200 observations (50 banks with FR 2644 data).

**Main specifications (Tables I, IV, V, VI, VIII).**

- **Arbitrage capital and positions (Table I).** Dependent variable: quarterly change in potential IOER capital (col. 1), CIP capital (col. 2), or IOER arbitrage position proxy (cols. 3-5) as share of 2014 total assets. Regressor: quarterly change in prime funds' unsecured holdings of bank debt as share of 2014 assets. Time fixed effects; SEs clustered at bank level. Reported for both OLS (Panel A) and Bartik IV (Panel B).

- **Balance sheet adjustments (Table IV).** IV regressions of quarterly changes in balance sheet items (total assets, cash, loans, securities, FF and repo, other assets on asset side; total liabilities, borrowing, deposits, trading liabilities, other liabilities, net-due-to on liability side) on the Bartik-instrumented change in prime-fund unsecured holdings. Sample: U.S.-based entities (FR 2644), N = 200. Time FE; SEs clustered at bank.

- **Intraoffice positions (Table V).** IV regressions decomposing the change in the net-due-to (NDT) position into the Eurodollar (ED) component and the residual, and comparing NDT, ED, and IOER arbitrage position responses. IOER arbitrageur interaction shows ED market is the key source for IOER arbitrage funding.

- **Funding costs (Table VI).** IV cross-sectional regressions of changes in funding rates (for each instrument and benchmark tenor from overnight to 12M) on changes in prime-fund unsecured holdings. Instrument-type and tenor fixed effects; SEs clustered at bank. Separate estimates by instrument type (ED, FF, CD, CP).

- **LCR heterogeneity (Table VIII).** Banks sorted into three LCR-proxy terciles; baseline IOER arbitrage position regression repeated separately for each tercile and interacted. Banks with lowest HQLA/unsecured funding ratio show strongest response.

- **Arbitrage profits (Table VII).** Daily time-series regressions of changes in volume-weighted arbitrage profits on daily changes in aggregate arbitrage capital, with Post dummy and interaction. Estimated separately for non-month-ends, month-ends, quarter-ends (QE), and non-QE month-ends for IOER; and by CIP tenor (1W, 1M, 3M) and QE/non-QE for CIP.

All regressions include time fixed effects. Standard errors are clustered at the bank level for cross-sectional regressions and are robust for time-series regressions.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| DTCC Solutions LLC (CP transactions) | Commercial paper transaction-level data (issuer, volume, rate, maturity) for unsecured funding and arbitrage capital measurement | No page yet |
| FR 2420 Report of Selected Money Market Rates | Daily transaction-level data on federal funds (FF), Eurodollars (ED), and negotiable certificates of deposit (CD) for U.S. banks and FBOs; backbone of IOER and CIP arbitrage capital measures | No page yet |
| FRBNY tri-party repo data | Position-level tri-party repo data to measure secured funding from MMFs | No page yet |
| FR 2644 Weekly Report (Selected Assets and Liabilities) | Weekly bank balance sheet data for U.S.-based entities (domestic banks and FBO branches); key asset and liability categories | No page yet |
| Federal Reserve Board reserve balance data | Daily excess reserve balances by bank; used to construct IOER arbitrage position proxy | No page yet |
| N-MFP (SEC Monthly Schedule of Portfolio Holdings) | Month-end MMF portfolio holdings at security level; AUM per fund; used to construct Bartik shares and shifts | [Form N-MFP](/wiki/datasets/n-mfp/) |
| Dealscan (Refinitiv) | Dollar-denominated syndicated loan origination by sample banks (lead arranger credit); used to test loan supply response | [DealScan](/wiki/licensed/dealscan/) (licensed) |
| SNL Financial | Bank holding company total assets in 2014 for normalization; also credit ratings and CET1 ratios | No page yet |
| Bloomberg (JPY OIS rates) | Dollar-yen OIS rates at granular maturities to construct swapped yen rate and CIP arbitrage profit | No page yet |

Sample: October 2015 to June 2017 (daily); main regression period October 2015 to October 2016. 58 global banks, comprising ~90% of total prime fund holdings of bank securities. Banks had at least 100 transactions with all U.S. MMFs and total assets of at least $100 billion in 2014.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13478) if you are: studying the post-GFC role of unsecured wholesale funding and arbitrage in banks' business models; evaluating credit channel transmission of funding shocks in a post-Basel III regulatory environment; applying Bartik shift-share designs in banking contexts (the paper follows the Goldsmith-Pinkham, Sorkin, and Swift (2020) protocol closely); analyzing IOER or CIP arbitrage dynamics and their relationship to unconventional monetary policy and excess reserves; or assessing the likely effects of the 2023 SEC MMF reform on global bank funding. The locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5), pp. 2591-2638. The PDF states "This article is a U.S. Government work and is in the public domain in the USA." Crossref DOI metadata records the Wiley termsAndConditions#vor licence with no CC designation; a rights signal conflict exists. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. Treated as extract-only pending licence clarification.

> Anderson, Alyssa, Wenxin Du, and Bernd Schlusche. "Arbitrage Capital of Global Banks."
> *The Journal of Finance* 80, no. 5 (October 2025): 2591–2638. DOI: 10.1111/jofi.13478.
