---
title: "Social Connectedness in Bank Lending: Rehbein & Rother (2025)"
description: >-
  Distilled: Using Facebook's Social Connectedness Index, Rehbein and Rother
  show that bank lending volumes, borrower-friendly loan terms, and bank
  profitability all increase with social connectedness between bank and borrower
  counties, while fintech lending is unaffected. Review of Financial Studies
  2025, paywalled. Eight core results with source locators, datasets used, the
  empirical model, and three formal specifications.
sidebar:
  label: Rehbein-Rother 2025
  order: 1
tags: [paper-summary, banking, credit-supply, social-networks, geographic-lending,
       information-asymmetry, panel-regression, peer-reviewed, unreplicated,
       data:cra-ffiec, data:hmda, data:fannie-freddie, data:call-reports,
       data:facebook-sci]
paper:
  authors: Oliver Rehbein, Simon Rother
  authorList:
    - { family: Rehbein, given: Oliver, affiliation: Vienna University of Economics and Business }
    - { family: Rother, given: Simon, affiliation: University of Mannheim }
  year: 2025
  venue: The Review of Financial Studies 38(9), September 2025, 2759–2809
  venueShort: Rev. Financ. Stud. 2025
  doi: 10.1093/rfs/hhaf014
  jel:
    codes: [D82, D83, G21, O16, L14, Z13]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Corporate Finance and Governance', 'Banking stability, regulation, efficiency', 'Microfinance and Financial Inclusion']
  dataAccess: public
  outcome:
    - county-to-county SME loan volume
    - county-to-county mortgage loan volume
    - mortgage interest rate
    - mortgage loan-to-value ratio
    - mortgage delinquency and default rates
    - bank return on assets
    - bank return on equity
    - bank nonperforming loan ratio
    - borrower-county GDP growth
    - borrower-county employment
  outcomeClass: [credit-supply, firm-financing, firm-real-outcomes]
  license: Oxford University Press standard publication reuse rights (confirmed via Crossref DOI metadata; content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days 0, start 2025-03-07)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Oxford Academic site; not machine-fetchable without institutional access; checked 2026-06-06)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 9
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, difference-in-differences]
    identification: natural-experiment
  contributionType: [new-fact, measurement]
  mechanisms: [information-asymmetry, moral-hazard]
  scope:
    region: US
    assetClass: corporate loans (SMEs), residential mortgages
    period: 2000-01..2018-12
    frequency: annual
    dataType: [administrative, accounting]
    granularity: [firm, individual, aggregate]
    n: "9,144,627 county pairs (loan-volume analysis); 1,268,200 loans (loan-term analysis); 18,914 bank-quarters (bank profitability analysis); 3,021 counties (real-effects analysis)"
  findings:
    - ref: R1
      outcome: county-to-county SME loan volume
      metric: elasticity
      value: "0.64 (Table 3, column 11, full controls); 0.91 in baseline (Table 2, column 1)"
      direction: positive
      vsBenchmark: "elasticity stable across broad array of geographic and economic controls; omitted-variable argument (Oster 2019) rules out spurious correlation"
    - ref: R2
      outcome: county-to-county mortgage loan volume
      metric: elasticity
      value: "1.10*** (Table 2, column 8)"
      direction: positive
      vsBenchmark: "mortgage elasticity similar to SME elasticity; robust to alternative clustering and HQ-based bank location"
    - ref: R3
      outcome: mortgage interest rate
      metric: sd-effect
      value: "1 SD increase in log(social connectedness) lowers interest rate by 1 bp (coefficient -0.497, Table 7 column 2; SD = 2.1)"
      direction: negative
      vsBenchmark: "more favorable terms than borrowers in low-connectedness county pairs"
    - ref: R4
      outcome: mortgage delinquency and default rates
      metric: pp-effect
      value: "1 SD increase in log(SCI) associated with 0.8 pp lower delinquency (coefficient -0.004, Table 7 col 3) and 0.4 pp lower default (coefficient -0.002, Table 7 col 4)"
      direction: negative
      vsBenchmark: "delinquency falls 8% relative to mean of 10%; default falls 20% relative to mean of 2%"
    - ref: R5
      outcome: bank return on assets
      metric: sd-effect
      value: "1 SD increase in log(portfolio social connectedness) raises ROA by 0.07 pp (coefficient 0.05, Table 10 panel A column 1; SD = 1.4)"
      direction: positive
      vsBenchmark: "effect is larger for heavy lenders (interaction 0.04*, Table 10 panel B col 1)"
    - ref: R6
      outcome: bank return on equity
      metric: sd-effect
      value: "1 SD increase in log(portfolio social connectedness) raises ROE by 1.04 pp (coefficient 0.74, Table 10 panel A column 2; SD = 1.4)"
      direction: positive
    - ref: R7
      outcome: borrower-county GDP growth
      metric: elasticity
      value: "baseline coefficient 1.719*** (SE 0.553, Table 12 col 2); 10% increase in social proximity raises GDP growth by ~0.3 pp at 95th-pct small-firm share (Table 12 col 3, interaction 1.660+0.060·19 per 100)"
      direction: positive
      vsBenchmark: "effect negligible for counties dominated by large firms; identified via shale-boom IV (Table 13)"
    - ref: R8
      outcome: borrower-county employment
      metric: elasticity
      value: "10% increase in social proximity raises employment by 0.21% (Table 12, column 4); twice as large in high-small-firm counties"
      direction: positive
      vsBenchmark: "effect confirmed with shale-boom IV for shocked banks (Table 13, columns 4-5)"
  resultType: new-finding
  relatesTo:
    - { cite: 'Bailey et al. (2018b)', relation: builds-on, note: 'introduces the Facebook Social Connectedness Index used as the main explanatory variable' }
    - { cite: 'Kuchler et al. (2022)', relation: extends, note: 'applies the social-proximity-to-institutions approach from institutional investors to banks' }
    - { cite: 'Degryse and Ongena (2005)', doi: '10.1111/j.1540-6261.2005.00729.x', relation: tests, note: 'social connectedness subsumes and reduces the coefficient on physical distance in lending' }
    - { cite: 'Agarwal and Hauswald (2010)', doi: '10.1093/rfs/hhq001', relation: tests, note: 'soft-information channel for distance effects in lending also operates via social connectedness' }
    - { cite: 'Haselmann, Schoenherr, and Vig (2018)', doi: '10.1086/697742', relation: cites, note: 'favoritism in elite networks as a competing mechanism to information-based lending' }
    - { cite: 'Gilje, Loutskina, and Strahan (2016)', doi: '10.1111/jofi.12387', relation: builds-on, note: 'shale-boom liquidity shocks used as IV for bank lending potential to address reverse causality' }
    - { cite: 'Gilje (2019)', relation: builds-on, note: 'shale-boom county boom exposure measure used to construct IV for real-effects analysis' }
    - { cite: 'Loutskina and Strahan (2011)', doi: '10.1093/rfs/hhq142', relation: extends, note: 'bank profitability model extended with portfolio social connectedness' }
    - { cite: 'Oster (2019)', relation: cites, note: 'coefficient-stability argument used to rule out omitted-variable explanations' }
  openQuestions:
    - "Whether social connectedness reflects primarily an information channel or a favoritism/discrimination channel: bank profitability increases suggest information may dominate, but the two mechanisms are observationally similar in many specifications (pp. 2784, 2801)."
    - "The long-run welfare implications for borrowers in low-connectedness regions, who may be systematically excluded from credit markets: the paper documents aggregate benefits but acknowledges distributional concerns (p. 2801)."
    - "How the role of social connectedness in lending evolves as online and algorithm-based lending expands, given that fintech lending is already unrelated to connectedness (p. 2784)."
  replicationCode:
    url: https://doi.org/10.7910/DVN/T3G5MD
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 2759-2809); eight results extracted with locators from Tables 2, 3, 4, 5, 7, 8, 10, 12, 13. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; four fixes applied: (1) R1 SE in Core results corrected from 0.05 to 0.06 (Table 3 col 11); (2) R7 Core results magnitude reworded from '1.66 pp' (confounded coefficient with effect) to '~0.3 pp at 95th-pct small-firm share'; (3) equation 7 summation index corrected from Σ_j to Σ_i; (4) JEL codes corrected from [G21, G14, R12] to [D82, D83, G21, O16, L14, Z13] per paper abstract."
  licenceVerification:
    - source: Crossref REST API works/10.1093/rfs/hhaf014
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-03-07; this is OUP standard reuse rights, NOT CC BY; paper is paywalled"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the economic hypotheses (information channel vs. favoritism), and the main empirical specifications with equations: enough to understand what was found and how, without reading all 51 pages. To replicate or extend it, see the full source at the [original](https://doi.org/10.1093/rfs/hhaf014) and the replication archive at the Harvard Dataverse.

## TL;DR

Rehbein and Rother exploit geographic variation in the Facebook Social Connectedness Index (SCI) to show that bank lending is shaped by the social ties between bank and borrower counties. A 10% increase in social connectedness between counties raises cross-county SME loan volumes by roughly 6-9% and mortgage loan volumes by a similar margin, after controlling for physical distance, cultural dissimilarity, and a broad set of geographic and economic factors. The relationship is stronger when screening incentives are high (e.g., no government guarantee, not securitized) and is absent for fintech lenders whose decisions are algorithm-based. Loans to high-connectedness borrowers carry lower interest rates, lower LTV ratios, and lower delinquency and default rates. Banks with more socially connected loan portfolios have higher ROA and ROE. At the aggregate level, borrower counties more socially proximate to bank regions receive more lending and experience higher GDP growth and employment, especially if they are small-firm intensive, an effect confirmed by a shale-boom natural experiment.

## Core results

Magnitudes and significance are as reported in the paper; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | County-to-county **SME loan volume increases strongly with social connectedness**; the relationship persists across a broad array of geographic and economic controls | Table 2, col. 1 (baseline); Table 3, col. 11 (full controls), pp. 2773-2775 | Baseline elasticity 0.91\*\*\* (SE 0.06); with all controls 0.64\*\*\* (SE 0.06); R2 rises from 0.70 to 0.91, leaving little room for further omitted-variable attenuation |
| R2 | **Mortgage loan volumes** also strongly increase with social connectedness | Table 2, col. 8, p. 2773 | Elasticity 1.10\*\*\* (SE 0.05); robust to OLS, alternative clustering, HQ-based bank location |
| R3 | High social connectedness is associated with **lower interest rates** on originated mortgages | Table 7, col. 2, p. 2787 | Coefficient on log(SCI) = -0.497\* (SE 0.259); 1-SD increase in log(SCI) lowers rate by ~1 bp |
| R4 | High social connectedness predicts **lower delinquency and default rates** | Table 7, cols. 3-4, p. 2787 | Delinquency coefficient -0.004\*\*\* (SE 0.000); default coefficient -0.002\*\* (SE 0.000); 1-SD change implies 0.8 pp lower delinquency and 0.4 pp lower default |
| R5 | **Bank ROA** increases with portfolio social connectedness | Table 10, Panel A, col. 1, p. 2793 | Coefficient 0.05\*\*\* (SE 0.02); 1-SD increase (1.4 log-units) raises ROA by 0.07 pp; effect larger for heavy SME lenders |
| R6 | **Bank ROE** increases significantly with portfolio social connectedness | Table 10, Panel A, col. 2, p. 2793 | Coefficient 0.74\*\*\* (SE 0.27); 1-SD increase raises ROE by 1.04 pp; nonperforming loans decrease (coefficient -0.35\*\*\*, SE 0.10) |
| R7 | Borrower counties more socially proximate to bank regions experience **higher real GDP growth**, particularly in small-firm counties | Table 12, cols. 2-3, p. 2797 | Baseline coefficient 1.719\*\*\* (SE 0.553); 10% increase in social proximity raises GDP growth by ~0.3 pp for counties at 95th percentile of small-firm share (= 10·(1.660+0.060·19)/100); confirmed with shale-boom IV (Table 13, col. 3) |
| R8 | **Employment** also rises with social proximity to bank regions, concentrated in small-firm counties | Table 12, cols. 4-5, p. 2797; Table 13, cols. 4-5, p. 2800 | 10% higher social proximity: coefficient 0.021\*\*\* (SE 0.006) on log(employment); twice as large at high small-firm-share counties; shale-boom IV confirms effect |

**Overall (paper's conclusion).** Social connectedness between bank and borrower regions is a distinct and economically important dimension of the geography of bank lending. It is not subsumed by physical or cultural distance and explains lending patterns consistent with both an information channel and favoritism, though the bank profitability result suggests that on average information reduction rather than favoritism is the dominant mechanism.

## Theory / model

The paper has no single formal theoretical model. It motivates the analysis with two competing hypotheses.

**Information hypothesis.** Social connections reduce information asymmetries between bank and borrower regions. Loan officers in socially connected counties obtain soft information about local economic conditions (through their own or their networks' acquaintances in the borrower region) and can make better lending decisions. Formally, if social connectedness $$\text{SCI}_{i,j}$$ increases, the precision of banks' private signal about borrowers in region $$j$$ rises. Better-screened borrowers receive lower rates and have lower delinquency; banks earn higher ROA. This prediction aligns with the classical framework of Diamond (1984) and Boot (2000) on delegated monitoring.

**Favoritism hypothesis.** Social connections may also lead to conscious or unconscious preferential treatment of borrowers in connected regions. Haselmann, Schoenherr, and Vig (2018) document rent-seeking in elite networks; the paper considers whether a similar mechanism operates at the population level. Unlike the information channel, favoritism predicts that banks' loan profitability might not improve (and could fall) if resources flow to less creditworthy but socially connected borrowers. The paper tests both channels by examining loan terms, loan performance, and bank profitability jointly (Section 2.6).

**Identification logic.** The social connectedness measure (Facebook SCI, equation 1, p. 2766) is cross-sectional (2016) and predetermined relative to the 2017 lending outcomes in the baseline. It is not randomly assigned, so the authors proceed in two ways. First, they add an extensive set of geographic and economic controls including the physical and cultural distance controls emphasized by Degryse and Ongena (2005) and Agarwal and Hauswald (2010), and use the Oster (2019) coefficient-stability argument to rule out omitted-variable bias. Second, for the real-effects results (Section 5.2), they exploit shale-boom liquidity shocks (Gilje, Loutskina, and Strahan (2016); Gilje (2019)) as a natural experiment: unanticipated increases in deposits at shale-exposed bank branches raise lending potential for banks with branches in boom counties, and counties socially connected to those banks receive more lending, without being directly affected by the boom.

## Method

**Social connectedness measure.** The SCI is introduced by Bailey et al. (2018b) and defined at the county-pair level as (equation 1, p. 2766):

$$
\text{social connectedness}_{i,j} = \frac{\text{number of friendship links}_{i,j}}{\text{population}_i \cdot \text{population}_j} \cdot \text{scaling factor}
$$

It quantifies the relative probability that a person in county $$i$$ is acquainted with a person in county $$j$$. The log of this variable is the main regressor throughout.

**Baseline loan-volume specification.** County-pair-level Poisson pseudo-maximum-likelihood (PPML) regression (equation 2, p. 2770):

$$
\text{volume of loans}_{i,j} = \exp\!\left[\beta \cdot \log(\text{social connectedness})_{i,j} + \gamma_1 \cdot \log(\text{physical distance})_{i,j} + \gamma_2 \cdot \text{cultural distance}_{i,j} + M_{i,j} + \alpha_i + \alpha_j\right] \cdot \epsilon_{i,j}
$$

where $$\alpha_i$$ and $$\alpha_j$$ are bank-county and borrower-county fixed effects, $$M_{i,j}$$ is a vector of county-pair controls (same-state FE, common-border FE, percentile FE for commuting, migration, trade, industry-share differentials, GDP and unemployment differentials, highway travel costs, and flight-and-drive time). Standard errors are clustered at the bank-county and borrower-county levels. PPML is used because loan volumes are non-negative and often zero; it accommodates heteroskedasticity and yields consistent elasticity estimates. The coefficient $$\beta$$ is the elasticity of loan volume with respect to social connectedness.

**Loan-type heterogeneity.** For the screening-incentive tests, the estimation adds county-pair-by-loan-type observations (equation 3, p. 2781):

$$
\text{volume of mortgage loans}_{i,j,k} = \exp\!\left[\beta \cdot \log(\text{social connectedness})_{i,j} \cdot \text{loan type}_k + \text{distance percentile FE}_{i,j} \cdot \text{loan type}_k + \alpha_{i,j}\right] \cdot \epsilon_{i,j,k}
$$

where $$k$$ indexes loan types (guaranteed, securitized, low-LTV, fintech), and county-pair fixed effects $$\alpha_{i,j}$$ absorb all time-invariant pair characteristics.

**Portfolio social connectedness (bank-profitability analysis).** Each bank's portfolio social connectedness is defined as the loan-weighted average of cross-county connectedness (equation 5, p. 2790):

$$
\text{portfolio social connectedness}_{b,y} = \sum_i \sum_j \text{social connectedness}_{i,j} \cdot \frac{\#\,\text{loans}_{b,i,j,y}}{\text{total}\,\#\,\text{loans}_{b,y}}
$$

Bank profitability is then regressed on this measure, extending the Loutskina and Strahan (2011) empirical model of bank performance (equation 6, p. 2791):

$$
\text{profitability}_{b,s,t} = \beta \cdot \log(\text{portfolio social connectedness})_{b,t} + \gamma_1 \cdot \log(\text{portfolio physical distance})_{b,t} + \gamma_2 \cdot \text{portfolio cultural distance}_{b,t} + \gamma_3 \cdot \text{loan concentration}_{b,t} + \gamma_4 \cdot \text{further bank controls}_{b,t} + \alpha_s + \alpha_t + \epsilon_{b,s,t}
$$

**Social proximity to banks (real-effects analysis).** Equation 7 (p. 2794) weights total bank assets in county $$i$$ by social connectedness:

$$
\text{social proximity to banks}_{j,t} = \sum_i \text{social connectedness}_{i,j} \cdot \text{total bank assets}_{i,t}
$$

Real outcomes in county $$j$$ are regressed on lagged log(social proximity to banks), controlling for physical and cultural proximity to banks, county and year fixed effects, and industry-share controls (equation 8, p. 2796).

**Shale-boom IV.** Bank exposure to shale-boom liquidity windfalls (equations 9-11, pp. 2799-2800) instruments lending potential. County $$i$$'s boom exposure is the share-weighted average of its banks' shale-boom exposures; county $$j$$'s social proximity to shocked banks replaces social proximity to all banks in the IV regressions (Table 13).

## Empirical specifications

**Section 2 (loan volumes, county pairs):** PPML on the full 9.1-million-pair cross-section (2017 lending data, 2016 SCI). Main estimates: Table 2 (baseline, columns 1-8), Table 3 Panel A (progressive controls, columns 1-11 for SME loans; columns 12 for mortgages). Heterogeneity by county type: Table 4 (five county-type interactions, PPML, N = 7,022,043). Heterogeneity by loan type: Table 5 (fintech vs. traditional banks, guaranteed, securitized, low-LTV; PPML, N = 11,870,270 for mortgage-by-type pairs). All columns include bank-county and borrower-county FE; columns with controls add same-state, common-border, and percentile FE.

**Section 3 (loan terms and performance, loan level):** OLS on 1,268,200 Fannie Mae/Freddie Mac 30-year fixed-rate mortgages originated 2000-2008, observed until 2018 (equation 4, p. 2785). Outcomes: LTV (col. 1), interest rate in bp (col. 2), delinquency indicator (col. 3), default indicator (col. 4). Controls include FICO score, DTI, first-time buyer indicator, log(loan amount), LTV (for performance columns), bank origination-year and borrower-state origination-year FE, and physical/cultural distance percentile FE. Standard errors clustered at bank-county and borrower-county.

Interest rate dispersion (Section 3.3): OLS at the county-pair level, dependent variable is the within-pair SD of interest rates (Table 8); controls include same-state, common-border, and percentile FE for physical and cultural distance. N = 6,999 county pairs with at least four loans.

**Section 4 (bank profitability, bank-quarter level):** OLS on 18,914 bank-quarter observations (844 banks, 2009-2017). Outcomes: ROA, ROE, % NPL (Table 10 Panels A and B). Controls: bank-state and year FE, log(portfolio physical distance), portfolio cultural distance, loan concentration, and further bank-level controls (log total assets, securities/assets, real estate loans/assets, C&I loans/assets, unused commitments/assets, letters of credit/assets, deposits/assets, interest expenses/deposits).

**Section 5 (real effects, county-year level):** OLS on 3,021 counties, 2009-2017 (N = 24,152-24,161). Outcomes: log(loan volume), real GDP growth, log(employment) (Table 12). Shale-boom IV regressions replace social proximity to all banks with social proximity to shocked banks (Table 13, N = 22,047-22,053). Controls: county and year FE, log(physical and cultural proximity to banks), industry-share controls, commuting/migration controls for employment. Standard errors clustered at the county level.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Facebook Social Connectedness Index (Bailey et al. 2018b) | Main explanatory variable; county-pair relative probability of Facebook friendship | [Facebook SCI](/wiki/datasets/facebook-sci/) |
| Community Reinvestment Act (CRA) data, FFIEC | County-to-county SME loan volumes for 2017 (and 2004-2018 for time series); bank-level loan counts | [CRA (FFIEC)](/wiki/datasets/cra-ffiec/) |
| Home Mortgage Disclosure Act (HMDA) data, FFIEC | County-to-county mortgage loan volumes for 2017; loan-type classification | [HMDA](/wiki/datasets/hmda/) |
| Fannie Mae and Freddie Mac Single Family Loan-Level Datasets | Loan-level mortgage data (2000-2008 originations, observed through 2018): LTV, interest rate, FICO, DTI, delinquency, default | [Fannie / Freddie loan-level](/wiki/datasets/fannie-freddie/) |
| FDIC Call Reports | Bank profitability (ROA, ROE, % NPL) and bank characteristics (2009-2017); branch-location data for assigning loans to bank counties | [Call Reports](/wiki/datasets/call-reports/) |
| NBER county distance database | Physical distance (as-the-crow-flies, miles) between county centroids | No page yet |
| Bureau of Economic Analysis | County-level real GDP growth and industry-share data | No page yet |
| Bureau of Labor Statistics | County-level employment; unemployment differentials | No page yet |
| U.S. Census Bureau | Commuting, migration, common-border, and county-level population data | No page yet |
| National Transportation Center / Oak Ridge | Highway travel costs and flight-and-drive time between county pairs | No page yet |
| Gilje, Loutskina & Strahan (2016) / Gilje (2019) | Shale-boom well counts and bank branch locations in boom counties for IV construction | No page yet |

Sample summary: cross-sectional county-pair analysis uses 2016 SCI and 2017 CRA/HMDA lending data, covering over 9 million county pairs. Loan-level analysis: 1,268,200 mortgages originated 2000-2008. Bank-profitability analysis: 844 banks, 2009-2017. Real-effects analysis: 3,021 counties, 2009-2017.

## When to read the full paper

Read the [original](https://doi.org/10.1093/rfs/hhaf014) if you are: studying the geographic determinants of bank lending beyond physical distance; researching social networks and credit markets; applying the Facebook SCI to a new financial context; building a social-proximity-to-institutions measure analogous to Kuchler et al. (2022); evaluating the information-vs.-favoritism debate in relationship banking; or designing a shale-boom IV for bank lending. The replication archive at Harvard Dataverse (https://doi.org/10.7910/DVN/T3G5MD) covers all tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(9), September 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled (Oxford University Press standard reuse rights; not CC); this page is extract-only.

> Rehbein, Oliver, and Simon Rother. "Social Connectedness in Bank Lending." *The Review of Financial Studies* 38, no. 9 (September 2025): 2759-2809. DOI: 10.1093/rfs/hhaf014.
