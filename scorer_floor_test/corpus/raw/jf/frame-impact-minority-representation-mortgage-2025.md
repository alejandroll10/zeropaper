---
title: "Minority Representation at Mortgage Lenders: Frame, Huang, Jiang, Lee, Liu, Mayer & Sunderam (2025)"
description: >-
  Distilled: Using new data linking U.S. mortgage applications to individual
  loan officers via NMLS and confidential HMDA, the paper shows that minority
  borrowers face lower completion, approval, and origination rates when matched
  with White loan officers, but these gaps shrink substantially under minority
  loan officers, and that minority-officer-matched loans also default less,
  consistent with an informational advantage rather than favoritism. J. Finance
  2025, paywalled. Eight core results with source locators, datasets used, the
  identification strategy, and the estimating equations.
sidebar:
  label: Frame et al. 2025
  order: 1
tags: [paper-summary, household-finance, mortgage-lending, racial-disparities,
       discrimination, information-asymmetry, panel-regression, peer-reviewed,
       unreplicated, data:hmda, data:nmls, data:fha]
paper:
  authors: W. Scott Frame, Ruidi Huang, Erica Xuewei Jiang, Yeonjoon Lee, Will Shuo Liu, Erik J. Mayer, Adi Sunderam
  authorList:
    - { family: Frame, given: W. Scott, affiliation: Structured Finance Association }
    - { family: Huang, given: Ruidi, orcid: "0000-0002-6061-5889", affiliation: Southern Methodist University, Cox School of Business }
    - { family: Jiang, given: Erica Xuewei, affiliation: University of Southern California, Marshall School of Business }
    - { family: Lee, given: Yeonjoon, orcid: "0000-0002-5010-8277", affiliation: Federal Reserve Bank of Richmond }
    - { family: Liu, given: Will Shuo, affiliation: City University of Hong Kong }
    - { family: Mayer, given: Erik J., orcid: "0000-0003-0730-8529", affiliation: University of Wisconsin-Madison, Wisconsin School of Business }
    - { family: Sunderam, given: Adi, affiliation: Harvard Business School }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1209–1260
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13428
  jel:
    codes: [G21, J15, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Housing Market and Economics
    - Banking stability, regulation, efficiency
    - Racial Disparities in Financial Markets
  dataAccess: proprietary-confidential
  outcome:
    - mortgage application completion rate
    - mortgage application approval rate (conditional on completion)
    - all-in origination rate
    - mortgage default rate (90+ days delinquent)
  outcomeClass: [household-finance, credit-supply]
  license: >-
    Paywalled. Copyright 2025 the American Finance Association. Article contributed
    to by U.S. Government employees; their portion is in the public domain in the USA
    (p. 1209). Crossref licence field: vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0.
    No CC licence found in metadata.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site, 2026-06-06)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 11
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, difference-in-differences]
    identification: instrument
  contributionType: [new-fact, new-data, measurement]
  mechanisms: [information-asymmetry, disparate-treatment]
  introducesData: true
  scope:
    region: US
    assetClass: residential mortgages
    period: 2012-01..2019-12
    frequency: mixed
    dataType: [administrative, accounting]
    granularity: [individual, transaction]
    n: "~5.65 million HMDA applications (2018-2019); ~3.37 million FHA originations (2012-2018) for default analysis"
  findings:
    - ref: R1
      outcome: mortgage application completion rate
      metric: pp-effect
      value: "minority applicants 1.9 pp less likely to complete under same White loan officer (branch-year-officer FE, col. 2, Table III)"
      direction: negative
      vsBenchmark: gap reduced by 1.1 pp when loan officer is a minority
    - ref: R2
      outcome: mortgage application approval rate (conditional on completion)
      metric: pp-effect
      value: "high-discretion minority applicants 2.9 pp less likely to be approved under White loan officers (col. 5, Table III)"
      direction: negative
      vsBenchmark: gap 1.2 pp smaller under minority loan officers (about 40% reduction)
    - ref: R3
      outcome: all-in origination rate
      metric: pp-effect
      value: "minority applications 5 pp less likely to originate under White loan officers (col. 7, Table III)"
      direction: negative
      vsBenchmark: gap 2.5 pp smaller under minority loan officers (about 50% reduction)
    - ref: R4
      outcome: mortgage application approval rate (conditional on completion)
      metric: pp-effect
      value: "IV estimate: high-discretion minority approval gap 3.6 pp under White officers; minority-officer interaction reduces gap by 3.6 pp (Table IV, Panel C, col. 3)"
      direction: negative
      vsBenchmark: IV slightly larger than OLS (1.2 pp OLS vs 3.6 pp IV for minority-officer interaction)
    - ref: R5
      outcome: mortgage default rate (90+ days delinquent)
      metric: pp-effect
      value: "minority borrowers with White loan officers default 1.8 pp more than White borrowers with White officers (OLS, col. 1, Table V)"
      direction: positive
      vsBenchmark: interaction Minority x Minority Officer = -2.2 pp (col. 1), eliminating minority default premium
    - ref: R6
      outcome: mortgage default rate (90+ days delinquent)
      metric: pp-effect
      value: "IV: minority borrowers with White officers default 1.7 pp more; interaction Minority x Minority Officer = -5.2 pp (col. 4, Table V)"
      direction: positive
      vsBenchmark: minority default premium fully eliminated under minority loan officers in IV
    - ref: R7
      outcome: mortgage application approval rate (conditional on completion)
      metric: pp-effect
      value: "same-race/ethnicity pairing: triple interaction Minority x Min. Off. x Same Race = +0.8 pp approval (Table VII, Panel A, col. 1); High Non-English Share triple interaction = +0.5 pp (Panel B, col. 2, one star)"
      direction: positive
      vsBenchmark: effect insignificant for different-race minority-officer pairings
    - ref: R8
      outcome: mortgage application completion rate
      metric: coefficient
      value: "Minority loan officer share (BIFSG-inferred) at mortgage lenders averages 15%, well below minority share in U.S. labor force (29.3% for financial managers); slope of LO minority share on ZIP minority share < 1 (Figure 1)"
      direction: negative
      vsBenchmark: minorities most underrepresented in ZIP codes with highest minority population share
  resultType: new-finding
  relatesTo:
    - { cite: "Munnell et al. (1996)", relation: builds-on, note: "founding documentation of racial disparities in mortgage approval rates; this paper adds loan officer race as a supply-side explanation" }
    - { cite: "Bhutta, Hizmo & Ringo (2024)", doi: '10.21799/frbp.wp.2024.09', relation: extends, note: "minority approval gap largely explained by observed risk factors; this paper shows residual gap explained by loan officer race via soft information" }
    - { cite: "Fisman, Paravisini & Vig (2017)", doi: '10.1257/aer.20120942', relation: builds-on, note: "cultural proximity in credit (India); this paper extends the cultural-proximity channel to the competitive U.S. mortgage market with hard information dominance" }
    - { cite: "Ambrose, Conklin & Lopez (2021)", doi: '10.1093/rfs/hhaa087', relation: extends, note: "broker and borrower race affect mortgage cost; this paper extends to loan officers and approval/origination/default outcomes at market scale" }
    - { cite: "Bartlett et al. (2022)", doi: '10.1016/j.jfineco.2021.05.047', relation: tests, note: "FinTech lenders reduce racial disparities; this paper finds minority-officer effect is weakest at FinTech lenders, consistent with less scope for soft information" }
  openQuestions:
    - "Whether the informational advantage of minority loan officers stems from pre-existing knowledge or from lower costs of acquiring information about minority borrowers; the paper documents the pattern but cannot distinguish between these mechanisms (pp. 1251, 1254)."
    - "Whether the results generalize beyond the mortgage market to other lending settings with more soft information, such as small business lending, where the paper speculates effects could be larger (p. 1254)."
    - "The equilibrium determinants of minority representation among loan officers are outside the scope of the analysis; the paper notes it is hard to substitute experienced White officers or cross-lender matching for adequate minority officer supply (p. 1252)."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1209-1260, J. Finance Vol. 80 No. 2 April 2025). Eight results extracted from Tables III, IV, V, VII. Not human-verified. Not reproduced. Confidential HMDA and FHA data used in the paper are proprietary and were not accessed here." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; R1-R6 and R8 pass; R7 High Non-English Share interaction corrected from +0.005** (0.002) to +0.005* (0.003) per Table VII Panel B col. 2; Z instrument formula tag (3) removed (unnumbered in PDF, only the first-stage regression is eq. 3); spurious Italy topic replaced with Racial Disparities in Financial Markets; equation (1) BIFSG, equation (2) LPM, and first-stage eq. (3) all verified term-by-term against PDF." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13428", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0; no CC licence in metadata. PDF p.1209 copyright: 2025 American Finance Association; U.S. Government employee work in public domain in USA. Classified as paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the datasets it links, and the estimating equations: enough to know what it found and how, without reading all 52 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13428).

## TL;DR

Using a new panel that links 5.65 million U.S. home purchase mortgage applications (2018-2019 HMDA) to the individual loan officers who handled them (via NMLS), Frame, Huang, Jiang, Lee, Liu, Mayer, and Sunderam (2025) establish two facts: (1) minorities are significantly underrepresented among loan officers (15% minority share versus 29-39% in comparable white-collar professions), and (2) minority borrowers are about 2 percentage points less likely to have their applications completed, 1.2-3 percentage points less likely to be approved (for high-discretion applications), and 2.5 percentage points less likely to originate a loan when handled by White loan officers. These gaps shrink substantially when the loan officer is also a minority. Critically, default rates on minority loans originated by White officers are 1.7-2.2 percentage points higher than for White borrowers, while minority-officer-matched minority loans default at the same rate as comparable White borrower loans. The pattern is consistent with minority loan officers having an informational advantage in handling minority borrower applications, rather than simple favoritism.

The paper contributes to three strands of the literature. First, it adds to the long tradition beginning with Munnell et al. (1996) on racial disparities in mortgage approval. Bhutta, Hizmo, and Ringo (2024) show the approval gap is largely explained by observed risk factors; this paper shows the residual gap is explained by the absence of minority loan officers who can supply soft information. Second, it extends the cultural-proximity credit result of Fisman, Paravisini, and Vig (2017) from Indian banks to the U.S. mortgage market, where automated underwriting and hard information dominate. Third, it complements Ambrose, Conklin, and Lopez (2021) and Bartlett et al. (2022): the minority-officer effect is strongest at small banks and weakest at FinTech lenders, consistent with FinTech reducing scope for loan-officer soft information.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Minority applicants are **1.9 pp less likely to complete** applications under White loan officers (within-officer comparison); gap is **1.1 pp smaller** under minority officers | Table III, cols. (1)-(2), p. 1224 | Minority: beta = -0.019\*\*\* (0.001); Minority x Minority Officer: beta = +0.011\*\*\* (0.002) |
| R2 | For high-discretion applications, minority applicants are **2.9 pp less likely to be approved** under White loan officers; gap is **1.2 pp smaller** under minority officers | Table III, col. (5)-(6), pp. 1224-1227 | Minority: -0.029\*\*\* (0.002); Minority x Minority Officer: +0.012\*\*\* (0.003) in col. (5) |
| R3 | In all-in origination rates, minority applications are **5 pp less likely to originate** under White loan officers; gap is **2.5 pp smaller** (about 50%) under minority officers | Table III, cols. (7)-(8), p. 1224 | Minority: -0.050\*\*\* (0.002); Minority x Minority Officer: +0.025\*\*\* (0.003) in col. (7) |
| R4 | IV estimates (day-of-week instrument): high-discretion minority approval gap is **3.6 pp** under White officers, and minority-officer interaction **fully offsets the gap** | Table IV, Panel C, col. (3), p. 1233 | Minority: -0.031\*\*\* (0.003); Minority x Minority Officer: +0.036\*\*\* (0.016) |
| R5 | FHA default analysis (OLS): minority borrowers with White officers default **1.8 pp more**; Minority x Minority Officer interaction is **-2.2 pp**, eliminating the excess default rate | Table V, col. (1), p. 1237 | Minority: +0.018\*\*\* (0.001); Minority x Minority Officer: -0.022\*\*\* (0.002) |
| R6 | FHA default IV: minority borrowers with White officers default **1.7 pp more**; IV interaction is **-5.2 pp**, fully eliminating the excess | Table V, col. (4), p. 1237 | Minority: +0.017\*\*\* (0.002); Minority x Minority Officer: -0.052\*\*\* (0.025) |
| R7 | Cross section of mechanism: effect concentrated in **same-race/ethnicity pairings** and in counties with a **high share of non-native English speakers** and **low college share** | Table VII, Panel A cols. (1),(3), pp. 1241-1243; Panel B cols. (2),(3) | Same Race triple interaction: +0.008\*\*\* (0.003); High Non-English Share triple interaction: +0.005\* (0.003) |
| R8 | Minorities are **underrepresented** among loan officers: 15% of loan officers are minorities versus 60.7% White (2019), while minorities are 39.3% of the U.S. labor force; minority share systematically below local population share | Table I, Panel A, p. 1219; Figure 1, p. 1221 | 84.6% White, 8.9% Hispanic, 1.8% Black, 4.7% Asian among N=255,277 loan officers |

**Overall (paper's conclusion).** Minority loan officers have an informational advantage in processing applications from minority borrowers: they achieve higher approval rates and lower default rates simultaneously, a pattern inconsistent with taste-based discrimination. The underrepresentation of minorities among loan officers therefore reduces minority access to credit, and this effect persists even in the hard-information-intensive U.S. mortgage market where automated underwriting systems dominate.

## Theory / model

The paper has no formal model. The paper's identification strategy rests on two testable hypotheses:

**Hypothesis 1 (supply-side discrimination / information advantage).** If minority loan officers have better soft information about minority borrowers, they can help those borrowers complete stronger applications, achieve higher approval rates, and generate loans that perform better (lower defaults). This is the authors' preferred interpretation.

**Hypothesis 2 (taste-based discrimination).** If White loan officers discriminate against minority borrowers based on taste, they would apply stricter standards: minority borrowers handled by White officers would have lower approval rates (as observed) but also lower default rates (the paper's Table V rules this out; default rates are in fact higher for minority loans handled by White officers).

The paper tests the hypotheses by examining approval and default rates jointly. Taste-based discrimination predicts lower approvals AND lower defaults for White-officer-handled minority loans. Information advantage predicts lower approvals AND higher defaults (because excluded minority borrowers are creditworthy, so the approved pool selected by stricter White officers is adversely selected relative to the approved pool selected by informed minority officers). The data match the information-advantage prediction.

**Identification.** Endogenous matching of loan officers to borrowers is a central concern. Two approaches address it:

1. Tight fixed effects: branch-year and branch-year-officer fixed effects isolate within-officer, within-branch variation in how the same officer treats minority versus White applicants.
2. Day-of-the-week instrument (Section II.C, pp. 1228-1234): exogenous variation in whether a minority officer handles a specific application is generated by minority officer work schedules.

## Method

**BIFSG race imputation** (pp. 1215-1216). Loan officer race/ethnicity is not observed in NMLS. The paper applies the Bayesian Improved First Name Surname Geocoding (BIFSG) method of Voicu (2018) to infer each officer's race/ethnicity. For surname $$s$$, first name $$f$$, and ZIP code $$z$$, the posterior probability of belonging to race group $$r$$ is (equation 1, p. 1215):

$$
p(r \mid s, f, z) = \frac{p(r \mid s) \times p(f \mid r) \times p(z \mid r)}{\sum_{r=1}^{6} p(r \mid s) \times p(f \mid r) \times p(z \mid r)} \tag{1}
$$

where $$p(r \mid s)$$ is the probability of belonging to race group $$r$$ given surname (from the 2010 Census surname list), $$p(f \mid r)$$ is the probability of having first name $$f$$ given race $$r$$ (from the Tzioumis 2018 list), and $$p(z \mid r)$$ is the probability of being in ZIP code $$z$$ given race $$r$$ (from the 2010 Census). Officers are assigned to the race group with the highest posterior probability.

**Day-of-the-week instrument** (pp. 1228-1229). For application $$i$$ opened at branch office $$b$$ on day of the week $$d$$ in week $$w$$, the instrument is the share of applications at the same branch on the same day of the week during the prior 12 weeks ($$w - 12$$ to $$w - 1$$) handled by minority officers:

$$
Z_{i,b,d,w} = \frac{\text{\#Minority Officer Applications}_{b,d,w-12 \to w-1}}{\text{\#Applications}_{b,d,w-12 \to w-1}}
$$

The first stage regresses an indicator for the application being handled by a minority officer on the instrument, branch-week fixed effects, day-of-the-week fixed effects, and controls (p. 1228):

$$
\mathbf{1}\{\text{Minority Officer}\}_{i,b,d,w} = \alpha_{b,w} + \beta Z_{i,b,d,w} + \gamma' \mathbf{X}_{i,b,d,w} + \varepsilon_{i,b,d,w} \tag{3}
$$

First-stage F-statistics exceed 15 across all samples (Table IV, Panel A). Covariate balance tests (Table IV, Panel B) show the instrument is uncorrelated with borrower age, income, loan amount, FICO, LTV, DTI, and AUS recommendation code.

## Empirical specifications

The main estimating equation (equation 2, p. 1223) is a linear probability model:

$$
Y_i = \beta_1 \mathbf{1}\{\text{Minority}\}_i + \beta_2 \mathbf{1}\{\text{Minority Officer}\}_i + \beta_3 \mathbf{1}\{\text{Minority}\}_i \times \mathbf{1}\{\text{Minority Officer}\}_i + \gamma' X_i + \varepsilon_i \tag{2}
$$

where $$Y_i$$ is in turn: application completion, approval (conditional on completion), all-in origination, or default (90+ days delinquent). The parameter of interest is $$\beta_3$$, the differential effect of having a minority loan officer on outcomes for minority versus White applicants. Standard errors are two-way clustered by lender and county.

**Application-level specifications (Table III, pp. 1223-1228):**

- Columns (1) and (3), (5), (7): branch-year fixed effects and property-county fixed effects, plus Basic App Controls (loan type indicators, 10-year age bins, income-to-MSA-median centile bins, log(loan amount), jumbo indicator, joint application indicator). This exploits cross-officer variation within the same branch-year.
- Columns (2) and (4), (6), (8): replace branch-year FE with branch-year-officer FE, so identification is within-officer (comparing how the same officer treats minority versus White applicants). The $$\beta_2$$ coefficient on Minority Officer is absorbed; only $$\beta_3$$ is identified.
- For approval regressions (cols. 3-6), the sample is restricted to completed applications and the Extended App Controls add FICO-bin, LTV-bin, and DTI-bin indicators (all interacted with loan type) plus AUS output code fixed effects. The sample is further split into "low-discretion" (AUS approval rate > 90%) and "high-discretion" (AUS approval rate <= 90%) applications.

**FHA default specification (Table V, p. 1237):** The dependent variable is an indicator for the FHA loan ever becoming 90+ days delinquent. Controls (FHA Controls) include log(loan amount), income-to-MSA centile bins, FICO-bin, LTV-bin, DTI-bin (all interacted with loan type), interest rate, first-time buyer indicator, branch-year FE, property-county FE, and origination-month FE. The IV variant uses branch-month FE and day-of-the-week FE with the same instrument $$Z_{i,b,d,w}$$ recalculated on FHA loans at the branch over prior 12 months.

**Mechanism tests (Tables VII-IX, pp. 1240-1251):** Same base specification augmented with triple interactions for: same-race/ethnicity pairing, low-income borrower, small bank, FinTech lender, rural county, high non-English share, low college share (Table VII); loan officer minority application share and experience (Table VIII); and linear hard information variables (credit score, DTI) to test differential reactions to hard information (Table IX).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| NMLS Consumer Access (2012-2019) | Nationwide loan officer panel: name, employer, work address, career history; source for BIFSG race imputation | [NMLS](/wiki/datasets/nmls/) |
| Confidential HMDA (2018-2019, Federal Reserve) | Mortgage applications matched to loan officers via NMLS ID; includes FICO, LTV, DTI, AUS code (added to confidential version from 2018) | [no page yet] |
| FHA insured mortgage data (2000-2018, FHA/Federal Reserve) | Population of FHA single-family originations; used for default analysis (90+ days delinquent through 2019-Q3) | [FHA](/wiki/datasets/fha/) |
| Black Knight McDash (matched to HMDA 2018-2019) | Monthly performance data; 60-day default within 24 months of origination; 36% match of HMDA approved mortgages | [no page yet] |
| U.S. Census Bureau (ZIP code level) | Demographic and economic characteristics (minority population share, PIPC, population density, non-English share, college share) | [no page yet] |

Sample: HMDA analysis covers 5.65 million first-lien 30-year fixed-rate home purchase mortgage applications (owner-occupied single-family properties) in 2018-2019, after filters. FHA default sample: ~3.37 million loans originated 2012-2018, tracked through 2019-Q3.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13428) if you are: studying the supply-side determinants of racial disparities in mortgage lending; evaluating the role of soft information in a setting dominated by hard information and automated underwriting; assessing whether minority officer representation has welfare-improving effects via credit expansion with no increase in default; or working on fair lending policy or the economics of racial diversity in financial services. The Internet Appendix (18+ tables) contains the BIFSG validation, subsample analyses by race/ethnicity pairing, shopping behavior robustness, and additional mechanism tests.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025. Copyright 2025 the American Finance Association; portions contributed by U.S. Government employees are in the public domain in the USA. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The underlying confidential HMDA and FHA microdata are proprietary and were not accessed here. Extract-only; no PDF hosted.

> Frame, W. Scott, Ruidi Huang, Erica Xuewei Jiang, Yeonjoon Lee, Will Shuo Liu, Erik J. Mayer, and Adi Sunderam.
> "The Impact of Minority Representation at Mortgage Lenders."
> *The Journal of Finance* 80, no. 2 (April 2025): 1209-1260.
> DOI: 10.1111/jofi.13428.
