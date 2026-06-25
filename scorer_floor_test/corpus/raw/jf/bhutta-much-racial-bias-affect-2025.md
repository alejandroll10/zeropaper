---
title: "How Much Does Racial Bias Affect Mortgage Lending: Bhutta, Hizmo & Ringo (2025)"
description: >-
  Distilled: Using confidential HMDA data for 2018-2019, this paper finds that
  standard underwriting factors explain most racial denial disparities, leaving
  a residual 1 to 2 percentage point excess denial gap that is itself at least
  partially explained by unobserved risk factors rather than discrimination.
  J. Finance 2025, U.S. Government work (public domain). Seven core results
  with source locators, datasets used, the model, and the empirical specifications.
sidebar:
  label: Bhutta-Hizmo-Ringo 2025
  order: 1
tags: [paper-summary, household-finance, mortgage-lending, discrimination, fair-lending,
       panel-regression, peer-reviewed, unreplicated, data:hmda, data:nsmo]
paper:
  authors: Neil Bhutta, Aurel Hizmo, Daniel Ringo
  authorList:
    - { family: Bhutta, given: Neil, affiliation: Federal Reserve Bank of Philadelphia }
    - { family: Hizmo, given: Aurel, affiliation: Federal Reserve Board }
    - { family: Ringo, given: Daniel, orcid: "0000-0001-6203-9961", affiliation: Federal Reserve Board }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1463-1496
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13444
  jel:
    codes: [G21, J15, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Housing Market and Economics", "Names, Identity, and Discrimination Research", "Spatial and Panel Data Analysis"]
  dataAccess: proprietary-confidential
  outcome:
    - mortgage denial rate by race and ethnicity
    - excess denial rate (unexplained denial gap relative to White applicants)
    - borrower satisfaction with lender service quality
  outcomeClass: [household-finance, credit-supply]
  license: "U.S. Government work; in the public domain in the USA (per PDF p.1463 copyright notice)"
  licenseShort: public domain (US Gov)
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/JF site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 22
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables]
    identification: selection-on-observables
  contributionType: [new-fact, measurement]
  mechanisms: [information-asymmetry]
  scope:
    region: US
    assetClass: residential mortgages
    period: 2018-01..2019-12
    frequency: mixed
    dataType: [administrative, survey]
    granularity: [individual, transaction]
    n: "~9 million mortgage applications (full AUS-processed sample); 35,162 NSMO respondents"
  findings:
    - ref: R1
      outcome: mortgage denial rate by race and ethnicity
      metric: pp-effect
      value: "Raw Black-White denial gap before controls: Black denial rate 18%, White 8% (10 pp gap); Table I, p.1474"
      direction: positive
    - ref: R2
      outcome: excess denial rate (unexplained denial gap relative to White applicants)
      metric: pp-effect
      value: "Black 2.0 pp, Hispanic 0.9 pp, Asian 1.4 pp excess denial after full FICO-LTV-DTI-AUS controls; Table II col.(3)"
      direction: positive
      vsBenchmark: "vs. Munnell et al. (1996) benchmark of ~8 pp excess denials for Black/Hispanic"
    - ref: R3
      outcome: excess denial rate (unexplained denial gap relative to White applicants)
      metric: correlation
      value: "Correlation between lender strictness and Black excess denials: 0.63; Hispanic: 0.50; Asian: 0.65; Figure 2"
      direction: positive
      vsBenchmark: "stricter lenders have largest excess minority denial rates, consistent with unobserved risk overlays"
    - ref: R4
      outcome: excess denial rate (unexplained denial gap relative to White applicants)
      metric: pp-effect
      value: "AUS excess denial for Black applicants: 1.5 pp after full controls (Table II col.(5)), suggesting racial gaps in unobserved risk factors considered by AUS"
      direction: positive
    - ref: R5
      outcome: excess denial rate (unexplained denial gap relative to White applicants)
      metric: coefficient
      value: "Racially charged search rate interaction with Black excess denials: 0.002** (s.e. 0.001); similar pattern in AUS excess denials (Table IV col.3 vs col.6), suggesting unobserved risk rather than discrimination"
      direction: positive
    - ref: R6
      outcome: borrower satisfaction with lender service quality
      metric: pp-effect
      value: "Black borrowers 4.5 pp more likely to report processing delays (Table V col.1, p<0.01), 9.6 pp more likely to have postponed closing (col.2, p<0.01)"
      direction: negative
      vsBenchmark: "vs. White borrowers; outcome mean = 0.16 and 0.21 respectively"
    - ref: R7
      outcome: borrower satisfaction with lender service quality
      metric: pp-effect
      value: "Black borrowers 7.1 pp less likely to be very satisfied with lender (Table V col.6, p<0.001); Asian borrowers 11.3 pp less satisfied"
      direction: negative
      vsBenchmark: "vs. non-Hispanic White borrowers; outcome mean = 0.78"
  resultType: overturns
  relatesTo:
    - { cite: "Munnell et al. (1996)", relation: contradicts, note: "find ~8 pp excess denials for Black and Hispanic applicants in 1990s Boston; this paper finds only 1-2 pp with modern HMDA data, suggesting substantial progress in fair lending" }
    - { cite: "Bartlett et al. (2022)", doi: '10.1016/j.jfineco.2021.05.047', relation: tests, note: "estimate 7-10 pp denial gaps without conditioning on credit score and other risk factors; this paper conditions on these and finds much smaller residual gaps" }
    - { cite: "Giacoletti, Heimer & Yu (2025)", relation: tests, note: "find 7 pp Black-White gap without credit score/LTV/DTI controls; estimate at least half reflects disparate treatment; this paper's evidence points more to unobserved risk" }
    - { cite: "Bhutta and Hizmo (2020)", doi: '10.1093/rfs/hhaa047', relation: extends, note: "earlier paper on minority mortgage pricing disparities; this paper provides parallel evidence on denial disparities using expanded HMDA" }
    - { cite: "Fuster et al. (2019)", doi: '10.1093/rfs/hhz018', relation: builds-on, note: "identification of fintech lenders used to test whether algorithmic lending reduces discrimination" }
    - { cite: "Arnold, Dobbie & Yang (2018)", doi: '10.1093/qje/qjy012', relation: builds-on, note: "judge-specific propensity-to-release framework adapted here as lender-specific strictness measure" }
  openQuestions:
    - "Whether the racial gaps in unobserved risk characteristics (u) that the AUS considers are due to prior discriminatory treatment in labor or other markets, which is beyond the scope of this paper (p. 1464, 1468)."
    - "Whether lender overlays on unobservable characteristics are justified as a business necessity or constitute disparate impact discrimination: the paper documents their existence but does not adjudicate their legality (p. 1473, Section IV.B.2)."
    - "The extent to which differential discouragement at the pre-application stage contributes to overall racial disparities in mortgage credit access: the paper finds limited evidence of this but notes data limitations (p. 1491, Section V.A)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-06", role: extracted, note: "Read PDF in full (34 pages, JF Vol.80 No.3 June 2025, pp.1463-1496); extracted all equations, tables, and results; not human-verified; not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; one fix applied: R7 Black coefficient corrected from 6.1 pp to 7.1 pp (Table V col.6 shows -0.071***, not -0.061); all other rows, equations (1)-(4), and specs confirmed correct."
  licenceVerification:
    - { source: "Crossref works/10.1111/jofi.13444", checked: "2026-06-06", by: "paper-distiller (claude-sonnet-4-6)", found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-04-09. PDF p.1463 states: 'This article is a U.S. Government work and is in the public domain in the USA.' No CC licence in Crossref; public domain status from PDF copyright notice." }
---

**What this is.** This is a machine-distilled skeleton of the paper. Read the [original (DOI 10.1111/jofi.13444)](https://doi.org/10.1111/jofi.13444) to replicate or extend.

## TL;DR

Using confidential expanded HMDA data for 2018-2019 (nearly 9 million applications), the paper finds that observable applicant risk factors (credit score, LTV, DTI, AUS recommendation) explain most of the racial and ethnic gaps in mortgage denial rates. The residual "excess denial" gap is 2 percentage points for Black applicants and roughly 1 pp for Hispanic and Asian applicants, substantially smaller than the 8 pp gaps found by Munnell et al. (1996) or the 7-10 pp estimated by Bartlett et al. (2022) without controlling for credit score and other underwriting factors. Giacoletti, Heimer and Yu (2025) estimate a similar 7 pp raw gap and argue at least half reflects discrimination; this paper's evidence points more to unobserved risk. Cross-sectional evidence on lender strictness shows that stricter lenders have larger excess minority denial rates, consistent with tighter overlays on unobserved risk factors rather than discriminatory intent. Indirect tests (fintech lenders, market competition, regional racial animus) do not yield clear evidence of discrimination. The paper also revisits findings from Bhutta and Hizmo (2020) on minority mortgage pricing, and extends them by examining denial disparities using the newly expanded HMDA data. A separate analysis using NSMO survey data finds that minority borrowers report substantially worse service quality, suggesting a dimension of disparate treatment in service delivery that is not captured by denial statistics.

## Core results

| # | Result | Locator | Magnitude as reported |
|---|---|---|---|
| R1 | Raw Black-White denial gap before any controls | Table I, p.1474 | Black denial rate 18%, White 8%; raw gap 10 pp |
| R2 | Excess denial after full FICO-LTV-DTI-AUS-lender controls | Table II col.(3), p.1475 | Black 2.0 pp\*\*, Hispanic 0.9 pp\*\*, Asian 1.4 pp\*\* (s.e. 0.001) |
| R3 | Lender strictness correlation with excess minority denials | Figure 2 right panels, p.1480 | r = 0.63 (Black), 0.50 (Hispanic), 0.65 (Asian) vs. lender strictness for Whites |
| R4 | AUS excess denial for Black applicants (unobserved risk signal) | Table II col.(5), p.1475 | 1.5 pp\*\* (s.e. 0.001), suggesting racial gaps in AUS-observed-but-HMDA-unobserved risk |
| R5 | Racial animus correlation test for discrimination | Table IV col.(3) vs col.(6), p.1488 | Racially charged search rate interaction: 0.002\*\* for lender and AUS excess denials alike, suggesting unobserved risk rather than discrimination |
| R6 | Minority borrower service quality: processing and closing delays | Table V cols.(1)-(2), p.1493 | Black: 4.5 pp more likely to report processing delays\*\*\*, 9.6 pp more likely to have postponed closing\*\*\* |
| R7 | Minority borrower satisfaction with lender | Table V col.(6), p.1493 | Black 7.1 pp less likely to be very satisfied with lender\*\*\*; Asian 11.3 pp less\*\*\* |

**Overall (paper's conclusion).** The paper concludes that disparate treatment plays a much smaller role in generating mortgage denial disparities than the 1990s benchmark of Munnell et al. (1996) suggests, implying significant progress in fair lending over 30 years. The 1-2 pp excess denials overstate actual discrimination because unobserved risk factors that vary by race and ethnicity (and that stricter lenders screen for) explain at least part of the residual gap. Service quality disparities, however, are a documented and underexplored dimension of differential treatment.

## Theory / model

The paper has no formal economic model. It defines disparate treatment structurally as a difference in expected credit decisions across race/ethnicity for otherwise identical applicants.

Let the binary AUS recommendation be:

$$D_{AUS} = g(X, u), \tag{1}$$

where $$g(\cdot)$$ is a deterministic function of risk characteristics $$X$$ observable in HMDA and other risk characteristics $$u$$ unobserved in HMDA (see Section I, p.1472 for the full DU factor list).

Lender $$i$$'s binary denial decision is:

$$D^{i}_{Lender} = h_i(X^*, u, w, r) + e, \tag{2}$$

where $$h_i(\cdot)$$ may differ from $$g(\cdot)$$; $$X^*$$ is a potentially updated value of $$X$$ after verification; $$w$$ is lender-specific overlays beyond AUS; $$r$$ is race/ethnicity; and $$e$$ is idiosyncratic human error. Lender $$i$$ engages in disparate treatment against Black relative to White applicants if (p.1473):

$$\int h_i(X^*, u, w, \text{Black})\, dF_B(X^*, u, w) > \int h_i(X^*, u, w, \text{White})\, dF_B(X^*, u, w), \tag{3}$$

where $$F_B(\cdot)$$ is the joint CDF of underwriting factors for the Black applicant population. The identification challenge is separating $$r$$ (illegal discrimination) from $$u$$ and $$w$$ (unobserved but potentially race-correlated risk factors).

## Method

The key methodological innovation is the **lender strictness measure**, constructed as the lender fixed effect from a denial regression run exclusively on White applicants (equation (2) controls, p.1478). This measure isolates lender-specific overlay policies from any differential treatment of minorities by construction. The paper then correlates lender strictness with lender-specific excess minority denial rates (estimated with lender-varying race/ethnicity coefficients) as an indirect test of whether unobserved risk drives excess denials. The approach is analogous to the judge-specific propensity-to-release design of Arnold, Dobbie and Yang (2018) and Arnold, Dobbie and Hull (2022).

Fintech identification follows Fuster et al. (2019): a lender is coded as fintech if it appears on that paper's fintech list. Market concentration is proxied by the top-4 lenders' county market share. Racial animus is measured by the racially charged search rate from Stephens-Davidowitz (2014), standardized to mean zero and unit variance. These three cross-sectional dimensions are interacted with race/ethnicity in equation (2) to test whether excess denials are systematically higher in settings where discrimination would be easier or more prevalent (Table IV).

## Empirical specifications

**Main denial regression (Table II).** The estimating equation is a linear probability model regressing an indicator of lender denial on race/ethnicity dummies and controls (p.1475-1476):

$$D^{i}_{Lender,j} = \alpha_r \cdot \mathbf{1}[\text{race}_j = r] + \beta' X_j + \delta_l + \varepsilon_j, \tag{4}$$

where $$j$$ indexes applications; $$r$$ indexes race/ethnicity relative to non-Hispanic White; $$X_j$$ includes the FICO-LTV-DTI grid (interactions of credit score bins, LTV bins, and DTI bins; see Table II notes for exact bin definitions), AUS denial recommendation (interacted with loan purpose and program), county-by-month fixed effects, loan amount bins, co-applicant indicator, and income bins (all covariates interacted with program and loan purpose); $$\delta_l$$ is a lender fixed effect. Standard errors are clustered at the lender and county levels. Columns (1) to (3) vary the control set progressively; column (3) is the preferred full specification.

**AUS denial regression (Table II, cols. 4-5).** The dependent variable switches to the AUS denial indicator $$D_{AUS,j}$$, with the same right-hand side. Because AUS is color-blind by design, residual racial gaps in AUS recommendations reflect unobserved risk factors $$u$$ correlated with race (p.1477-1478).

**Lender-specific excess denials and strictness correlation (Figure 2, Table III).** For the 100 largest lenders, the race/ethnicity coefficients are allowed to vary by lender (i.e., the full col.(3) specification with lender-varying race/ethnicity slopes). These lender-specific excess denial estimates are plotted against lender strictness (lender FE from White-only denial regression). The correlation coefficient is reported (p.1481).

**Loan performance validation (Figure 4).** For 48 Ginnie Mae issuers matched to HMDA, the paper regresses 60-day delinquency within one year of origination on lender strictness. Residual riskiness is the lender FE from a delinquency regression controlling for flexible functions of DTI, LTV, credit score, and month dummies. Both raw and residual riskiness are negatively correlated with strictness, validating that strictness captures real overlay policies (p.1484-1486).

**Indirect tests for discrimination (Table IV).** The baseline specification (col.(3) of Table II) is augmented with interactions between race/ethnicity and (i) fintech indicator, (ii) top-4 lender county market share, and (iii) racially charged Google search rate, estimated separately for lender denials and AUS denials (p.1486-1489).

**Service quality regressions (Table V).** OLS regressions using NSMO individual-level data with controls including loan type, loan purpose, loan amount, credit score, income, LTV, self-employment status, co-applicant status, loan term, 11 LTV categories, 6 credit score categories, and 8 loan amount categories; all fully interacted with program and loan purpose. Survey fixed effects and county fixed effects included. Heteroskedasticity-robust standard errors. Outcomes are binary (processing delays, closing date postponement, satisfaction dummies), p.1492-1493.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| HMDA (confidential, expanded 2018-2019) | Main denial analysis: ~9 million applications with credit score, LTV, DTI, AUS recommendation | [/wiki/datasets/hmda/](/wiki/datasets/hmda/) |
| National Survey of Mortgage Originations (NSMO) | Survey component of NMDB; borrower satisfaction and service quality analysis (N=35,162) | [NSMO](/wiki/datasets/nsmo/) |
| National Mortgage Database (NMDB) | Provides inquiry data for pre-application discouragement analysis; links HMDA to credit bureau records | no page yet |
| Ginnie Mae securitization pool data | Loan performance (delinquency) validation for 48 matched issuers, 2018-2019 originations | no page yet |

**Sample:** First-lien, 30-year fixed-rate mortgages on owner-occupied single-family properties; 2018-2019; applications through one of three main AUS (DU, LPA, TOTAL); excludes jumbo loans and withdrawn/incomplete applications. Final AUS-processed sample: ~8.9 million applications. NSMO subsample: 35,162 respondents for service quality regressions.

## When to read the full paper

Read the paper if you are studying racial disparities in mortgage credit, the role of automated underwriting in fair lending, or methods for detecting discrimination in lending outcomes. Table II is the key excess denial table; Figure 2 and Table III document the lender strictness channel; Table IV presents the indirect discrimination tests; Table V covers service quality. The Internet Appendix (referenced throughout) contains additional robustness checks, the pre-application discouragement analysis, and the interest rate gap replication.

## Attribution and rights

This article is a U.S. Government work and is in the public domain in the USA (per PDF p.1463 copyright notice: "Published 2025. This article is a U.S. Government work and is in the public domain in the USA."). The Wiley/JF Crossref record carries the Wiley terms-and-conditions URL rather than a CC licence. Extract-only: not reproduced or human-verified here. LLM-distilled; not reproduced.

> Bhutta, Neil, Aurel Hizmo, and Daniel Ringo (2025). "How Much Does Racial Bias Affect Mortgage Lending? Evidence from Human and Algorithmic Credit Decisions." *The Journal of Finance* 80(3): 1463-1496. DOI: 10.1111/jofi.13444.
