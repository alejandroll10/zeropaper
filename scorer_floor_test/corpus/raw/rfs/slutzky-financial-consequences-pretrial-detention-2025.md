---
title: "Financial Consequences of Pretrial Detention: Slutzky & Xu (2025)"
description: >-
  Distilled: Using quasi-random assignment of court commissioners in Maryland as
  an instrument, this paper finds that pretrial detention causally raises
  household insolvency rates, driven by chapter 7 bankruptcy, judgment liens,
  and foreclosures in areas of declining house prices, with effects spilling
  over to family members rather than defendants themselves. Review of Financial
  Studies 2025, paywalled. Eight core results with source locators, datasets
  used, the identification strategy, and the estimating equations.
sidebar:
  label: Slutzky-Xu 2025
  order: 1
tags: [paper-summary, household-finance, criminal-justice, bankruptcy, foreclosure,
       panel-regression, instrumental-variables, peer-reviewed, unreplicated,
       data:maryland-judiciary, data:pacer-bankruptcy, data:ztrax]
paper:
  authors: Pablo Slutzky, Sheng-Jun Xu
  authorList:
    - { family: Slutzky, given: Pablo, orcid: "0009-0008-3065-9769", affiliation: University of Maryland }
    - { family: Xu, given: Sheng-Jun, orcid: "0000-0002-3852-3953", affiliation: University of Alberta }
  year: 2025
  venue: The Review of Financial Studies 38(11), November 2025, 3329–3373
  venueShort: Rev. Financ. Stud. 2025
  doi: 10.1093/rfs/hhaf009
  jel:
    codes: [D14, G51, K35, K42]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: [Criminal Justice and Corrections Analysis]
  dataAccess: licensed-commercial
  outcome:
    - household chapter 7 bankruptcy rate
    - judgment lien rate
    - household foreclosure rate
    - overall household insolvency rate
  outcomeClass: [household-finance, credit-risk]
  license: "OUP standard publication reuse rights (not CC); confirmed via Crossref DOI metadata: content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days 0, start 2025-01-30"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Oxford Academic site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 0
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [instrumental-variables, panel-regression]
    identification: instrument
  contributionType: [new-fact, new-data]
  introducesData: true
  mechanisms: [financial-constraint, debt-overhang]
  scope:
    region: US
    assetClass: household balance sheets
    period: 2000-01..2016-12
    frequency: mixed
    dataType: [administrative]
    granularity: [individual]
    n: "over 500,000 criminal cases in Maryland District Courts, 2000-2016"
  findings:
    - ref: R1
      outcome: household chapter 7 bankruptcy rate
      metric: pp-effect
      value: "+0.79 pp at 3-year horizon (Table 5, col 5); 30% of baseline mean of 2.65%"
      direction: positive
      vsBenchmark: "null result for chapter 13 bankruptcy across all horizons"
    - ref: R2
      outcome: judgment lien rate
      metric: pp-effect
      value: "+0.56 pp at 3-year horizon (Table 6, col 5); 35% increase relative to sample mean of 1.6%"
      direction: positive
    - ref: R3
      outcome: household foreclosure rate
      metric: pp-effect
      value: "Null in full sample (Table 7A); +2.9 pp at 3-year horizon in negative-HPI subsample (Table 7B, col 5); 23% of mean"
      direction: mixed
      vsBenchmark: "null in positive-HPI subsample, consistent with home equity acting as liquidity buffer"
    - ref: R4
      outcome: overall household insolvency rate
      metric: pp-effect
      value: "+2.4 pp at 3-year horizon (Table 8, col 5); 16% increase relative to mean of 14.8%"
      direction: positive
    - ref: R5
      outcome: overall household insolvency rate
      metric: coefficient
      value: "InsolventDef: 0.0027 (insignificant); InsolventFamily: 0.0075** (Table 9, cols 1-2); family mean 3.4% vs defendant mean 1.6%"
      direction: positive
      vsBenchmark: "effect concentrated in family members, not defendants themselves"
    - ref: R6
      outcome: overall household insolvency rate
      metric: pp-effect
      value: "+4.2 pp at 3-year horizon in commercial bail bond subsample (Table 10, col 1); remains significant at +1.9 pp after dropping commercial bond cases (col 5)"
      direction: positive
      vsBenchmark: "commercial bail bonds amplify but do not solely explain the effect"
    - ref: R7
      outcome: overall household insolvency rate
      metric: pp-effect
      value: "+2.8 pp* for young defendants (col 1, Table 11A); +3.9 pp** for mortgage-financed properties (Table 11B, col 3); +4.1 pp*** for short-maturity mortgages (Table 11B, col 6)"
      direction: positive
      vsBenchmark: "stronger for young defendants consistent with spillover to older cohabitating relatives"
    - ref: R8
      outcome: overall household insolvency rate (name-matched)
      metric: coefficient
      value: "FailToAppear x Detained: +0.0308*** for InsolventDef (Table 13, col 2); +0.0088*** for InsolventFamily (col 3); insignificant for InsolventUnrelated (col 5, -0.0066)"
      direction: positive
      vsBenchmark: "failure to appear amplifies detention's insolvency effect for defendants and family members but not unrelated individuals"
  resultType: new-finding
  relatesTo:
    - { cite: "Dobbie, Goldin & Yang (2018)", doi: '10.1257/aer.20161503', relation: extends, note: "extends their instrument design for commissioner leniency to household financial outcomes rather than conviction and employment" }
    - { cite: "Gupta, Hansman & Frenchman (2016)", doi: '10.1086/688907', relation: builds-on, note: "builds on their evidence that pretrial detention raises conviction rates and reduces formal employment" }
    - { cite: "Dahl, Kostol & Mogstad (2014)", doi: '10.1093/qje/qju019', relation: builds-on, note: "adapts their residualized leave-out mean instrument construction to the commissioner setting" }
    - { cite: "Dobkin et al. (2018)", doi: '10.1257/aer.20161038', relation: tests, note: "finds comparable magnitude (0.79 pp at 3-year bankruptcy horizon) to their hospital-admission bankruptcy estimate (0.4-1.4 pp)" }
    - { cite: "Foote, Gerardi & Willen (2008)", relation: tests, note: "tests their double-trigger hypothesis: foreclosure effect only in negative-HPI areas, consistent with liquidity shock plus negative equity" }
    - { cite: "Gross, Notowidigdo & Wang (2014)", doi: '10.1162/rest_a_00391', relation: cites, note: "source of PACER bankruptcy filing data used in the analysis" }
  openQuestions:
    - "Welfare analysis is precluded by the complexity of the criminal justice system: the authors note they cannot conduct a definitive welfare analysis, as the costs of pretrial detention must be weighed against public safety benefits (p. 3370)."
    - "The income channel cannot be fully separated from the bail-cost channel: defendants who are detained for extended periods also lose labor income and face higher conviction rates, and these mechanisms are only partially disentangled (pp. 3332-3333)."
    - "Effects post-2017 bail reform in Maryland are not studied: the analysis is restricted to 2000-2016 to avoid the confounding shift in commissioner decisions after Court Rule 4-216.1 (p. 3338)."
  replicationCode:
    url: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/MN0GU6"
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 3329-3373); eight results extracted from tables and figures with page locators. Not human-verified. Not reproduced. Replication code referenced at Harvard Dataverse but not run here." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (all tables and equations). Fixed: (1) R7 findings[] magnitudes corrected from wrong +5.5 pp/+6.5 pp to PDF values +2.8 pp*/+3.9 pp**; (2) R8 Core results and findings[] corrected: +0.0308*** belongs to InsolventDef (col 2), not InsolventFamily (col 3 = +0.0088***); (3) R7 Core table mortgage significance *** corrected to **; (4) Table 9 incorrectly labeled OLS, corrected to 2SLS (F=6,305.53); (5) Table 8 overall insolvency mean corrected from 0.3550 (which is the SD) to 0.1479; (6) dataAccess upgraded from public to licensed-commercial (ZTRAX is Zillow proprietary); (7) JEL K42 added (present in abstract, omitted from frontmatter). Equations 1-3 verified term-by-term; all signs, subscripts, and summation indices match PDF."
  licenceVerification:
    - { source: "Crossref REST API works/10.1093/rfs/hhaf009", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-01-30. This is OUP standard reuse rights, NOT a Creative Commons licence." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, identification design, and estimating equations: enough to understand what was found and how, without reading all 45 pages. To replicate or extend, read the original at [https://doi.org/10.1093/rfs/hhaf009](https://doi.org/10.1093/rfs/hhaf009).

## TL;DR

This paper asks whether pretrial detention, which holds individuals in jail before trial because they cannot afford bail, causes subsequent household financial distress. Using Maryland criminal court data (2000-2016) matched to bankruptcy filings from Gross, Notowidigdo, and Wang (2014), foreclosure, and judgment lien records, it exploits the quasi-random assignment of court commissioners to cases as an instrument for detention decisions. A more lenient commissioner reduces the probability of detention, and this variation is unrelated to defendant characteristics. The main finding is that pretrial detention causally increases household insolvency, raising chapter 7 bankruptcy rates by 0.79 percentage points (30% of the mean) and judgment lien rates by 0.56 percentage points (35% of the mean) within three years. Foreclosures increase significantly (2.9 pp, 23% of the mean) only in ZIP codes with declining house prices, consistent with home equity acting as a liquidity buffer. The financial burden falls primarily on family members, not defendants themselves, suggesting cohabiting relatives (parents, partners) posting or guaranteeing bail bear the cost. Commercial bail bonds play a partial role, but insolvency effects persist even in samples that largely eliminate income-loss and criminal-record channels.

## Core results

Magnitudes and significance are as reported; `\*\*` = 5%, `\*\*\*` = 1%. All regressions instrument detention with the residualized leave-out mean commissioner leniency measure (first-stage F-stat exceeds 6,000 unless noted).

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Pretrial detention **raises chapter 7 bankruptcy** at the 1-3 year horizon; null for chapter 13 | Table 5, p. 3353 | +0.44 pp at 1 year\*\*, +0.76 pp at 2 years\*\*, +0.79 pp at 3 years\*\* (30% of 2.65% mean); chapter 13 insignificant at all horizons |
| R2 | Pretrial detention **raises judgment lien rates** at the 3-year horizon | Table 6, p. 3355 | +0.56 pp at 3 years\*\* (35% increase relative to 1.6% mean); insignificant at shorter horizons |
| R3 | **Foreclosure effects are null overall** but large in areas with declining house prices | Table 7, p. 3356 | Full sample: +0.92 pp at 3 years (insignificant); negative-HPI subsample: +2.9 pp\*\* at 3 years (23% of mean); null in positive-HPI subsample |
| R4 | Overall household insolvency (bankruptcy + lien + foreclosure) rises by **2.4 pp at 3 years** | Table 8, p. 3359 | +1.7 pp\*\* at 2 years, +2.4 pp\*\*\* at 3 years (16% of 14.8% mean); clean zero in backward-looking placebo tests (Figure 8) |
| R5 | **Insolvency burden falls on family members**, not defendants | Table 9, p. 3362 | InsolventDef: +0.0027 (insignificant, mean 1.6%); InsolventFamily: +0.0075\*\* (22% of 3.4% mean); InsolventUnrelated: +0.0123 (insignificant) |
| R6 | **Commercial bail bonds amplify but do not fully explain** the insolvency effect | Table 10, p. 3365 | ROR/commercial-bond sample: +4.2 pp\*\*\*; excluding commercial bonds: +1.9 pp\*; effect persists when income-loss and conviction channels are controlled |
| R7 | Insolvency effects are **stronger for younger defendants** and **mortgaged, shorter-maturity properties** | Table 11, p. 3367 | Young defendants (age < 30): +2.8 pp\*; mortgage-financed properties: +3.9 pp\*\*; short-maturity: +4.1 pp\*\*\*; consistent with older relative bearing bail costs |
| R8 | **Failure to appear magnifies** the insolvency effect for defendants and family members via bond forfeiture | Table 13, p. 3369 | FailToAppear x Detained interaction: +0.0308\*\*\* (InsolventDef, col 2); +0.0088\*\*\* (InsolventFamily, col 3); insignificant for InsolventUnrelated (col 5); OLS result, causal interpretation limited |

**Overall (paper's conclusion).** Pretrial detention imposes significant household financial costs that extend beyond the defendant to cohabiting family members, most plausibly through the direct cost of posting or guaranteeing bail. The 3-year bankruptcy effect (0.79 pp) is comparable in magnitude to Dobkin et al. (2018), who find that hospital admissions raise bankruptcy rates by 0.4-1.4 pp. Home equity cushions households from insolvency: the foreclosure effect is concentrated in areas with declining house prices, where households cannot tap equity to meet liquidity shocks. Commercial bail bonds play a partial but not exclusive role. The findings add to the literature on the collateral damage of the criminal justice system and are relevant to ongoing debates about bail reform.

## Theory / model

The paper has no formal economic model. The identification logic and tested hypotheses are as follows.

**Hypotheses tested.** Three potential channels link pretrial detention to household insolvency (pp. 3330-3332):

1. Liquidity shock from bail costs (cash bond, commercial surety bond fee, property bond pledge) borne immediately by the defendant or family.
2. Loss of current income from prolonged detention, reducing the defendant's ability to contribute to household obligations.
3. Long-run income reduction through higher conviction rates and reduced future formal employment, documented by Gupta, Hansman, and Frenchman (2016) and Dobbie, Goldin, and Yang (2018).

The empirical tests are designed to separate these. The commercial bail bond subsample test (Table 10) restricts to cases where defendants obtain immediate release via commercial bonds, which filters out the income-loss channel while preserving the liquidity-shock channel. The finding that insolvency effects persist in this sample (R6) is consistent with the bail-cost mechanism.

**Double-trigger hypothesis for foreclosure.** Foote, Gerardi, and Willen (2008) show that both a liquidity shock and negative home equity are needed for foreclosure. The heterogeneous foreclosure effects (R3) are explicitly framed as a test of this: the liquidity shock from pretrial detention triggers foreclosure only when home equity is insufficient to buffer it (pp. 3356-3358).

**Identification.** Assignment of commissioners to cases in Maryland is treated as quasi-random conditional on court-by-year, ZIP-code-by-year, month, day-of-week, sex, race, and charge fixed effects. The exclusion restriction requires that the commissioner's leniency affects household financial outcomes only through the pretrial detention decision. The paper provides two sets of evidence: (i) the residualized instrument is uncorrelated with all observable defendant and case characteristics (Table 2, column 3; joint F-test p-value = 0.499), and (ii) the first-stage coefficient on the instrument is large and symmetric across subsamples defined by race, sex, age, and geography (Table 3).

## Method

The paper applies an instrumental variables design built on two existing approaches: the leave-out commissioner leniency instrument of Dahl, Kostol, and Mogstad (2014) and Dobbie, Goldin, and Yang (2018), applied to a new outcome domain (household finance). The technique genealogy runs through `instrumental-variables` and `panel-regression`.

**First stage: residualized leave-out mean (p. 3345, Equation 3).** For each commissioner $$j$$ in year $$t$$, the leniency instrument is constructed as:

$$
\text{ReleasedRIV}_{ctj} = \left(\frac{1}{n_{tj} - n_{itj}}\right)\left(\sum_{k=0}^{n_{tj}} \text{Released}^*_{klt} - \sum_{c=0}^{n_{itj}} \text{Released}^*_{ict}\right) \tag{3}
$$

where $$n_{tj}$$ is the total number of cases commissioner $$j$$ sees in year $$t$$, $$n_{itj}$$ is the number involving defendant $$i$$, and $$\text{Released}^*_{ict}$$ is the residual release decision after partialling out defendant and case characteristics $$X_{ict}$$ (Equation 2):

$$
\text{Released}^*_{ict} = \text{Released}_{ic} - \gamma \, X_{ict} = \text{ReleasedRIV}_{ctj} + \epsilon_{ict} \tag{2}
$$

Leaving out cases involving the focal defendant avoids the mechanical correlation that would arise if the instrument included the defendant's own case. The instrument is then transformed into $$\text{DetainedRIV} = 1 - \text{ReleasedRIV}$$ so that results are reported as effects of detention rather than release.

**Second stage (p. 3344, Equation 1).** The primary estimating equation is:

$$
Y_{ict} = \beta_0 + \delta \, \text{Released}_{ic} + X_{ict}\beta + \epsilon_{ict} \tag{1}
$$

where $$Y_{ict}$$ is the cumulative insolvency indicator (bankruptcy, judgment lien, or foreclosure) for individual $$i$$ in case $$c$$ in year $$t$$, $$\text{Released}_{ic}$$ is the endogenous binary treatment variable, and $$X_{ict}$$ is a vector of case- and defendant-level controls. In the 2SLS version, $$\text{DetainedRIV}$$ instruments for $$\text{Detained}_{ic}$$.

**First-stage strength.** The first-stage F-statistic is 13,526 in the main sample (Table 3, col 1; Table 4B), well above the Stock and Yogo (2005) and Olea and Pflueger (2013) thresholds. The coefficient on $$\text{ReleasedRIV}$$ in the first stage is approximately -0.946 (Table 3, col 1), meaning a one-unit increase in the leniency instrument shifts the probability of release by 94.5 percentage points. The coefficient is stable across subsamples (range 0.898 to 1.082, Table 3, cols 2-10).

## Empirical specifications

**Outcome variables.** The insolvency indicators are defined as cumulative dummy variables: $$Y_{ict}^{\tau} = 1$$ if a bankruptcy, judgment lien, or foreclosure occurs within $$\tau$$ periods of the initial hearing date. Horizons are 3 months, 6 months, 1 year, 2 years, and 3 years. Bankruptcy data (PACER) cover 2000-2008; foreclosure and lien data (Maryland Judiciary + ZTRAX) cover 2000-2016.

**Fixed effects and standard errors.** All regressions include court-by-year, ZIP-code-by-year, month, day-of-week, sex, race, and charge fixed effects. Standard errors are clustered at the commissioner level.

**Bankruptcy specifications (Table 5).** The 2SLS regression instrumenting $$\text{Detained}_{ic}$$ with $$\text{DetainedRIV}_{ctj}$$ yields:

| Horizon | Coefficient on Detained | SE | Mean |
|---|---|---|---|
| 3 months | +0.0003 | (0.0013) | 0.0029 |
| 6 months | +0.0005 | (0.0015) | 0.0057 |
| 1 year | +0.0044\*\* | (0.0021) | 0.0110 |
| 2 years | +0.0076\*\* | (0.0031) | 0.0198 |
| 3 years | +0.0079\*\* | (0.0037) | 0.0265 |

First-stage F-stat: 10,004. N = 306,722.

**Judgment lien specifications (Table 6).** Same specification, first-stage F-stat = 13,526, N = 502,546. The coefficient becomes significant at the 3-year horizon (+0.0056\*\*, SE = 0.0023), consistent with liens being a last resort after other repayment channels are exhausted.

**Foreclosure specifications (Table 7).** Full sample (N = 275,325): coefficient at 3 years = +0.0092 (SE = 0.0074), insignificant. Negative-HPI ZIP codes (N = 107,357): +0.0291\*\* at 3 years (SE = 0.0123). Positive-HPI ZIP codes (N = 166,155): -0.0033 (SE = 0.0089), null.

**Overall insolvency (Table 8).** Combines bankruptcy, lien, and foreclosure for the ZTRAX-matched sample (N = 275,325). Coefficient at 3 years: +0.0242\*\*\* (SE = 0.0090), mean = 0.1479 (SD = 0.3550).

**Family spillover specifications (Table 9).** 2SLS (same instrument as benchmark, first-stage F = 6,305.53). Insolvency events are matched using both addresses and full names, separating defendant's name (InsolventDef), family members' names (InsolventFamily), same last name (InsolventName), and unrelated individuals (InsolventUnrelated). N = 275,325, all horizons 3 years.

**Placebo tests.** Figures 4, 5, and 8 plot coefficients at backward-looking horizons (-3 years, -2 years, -1 year, -6 months, -3 months). In all cases the coefficients are small and statistically indistinguishable from zero, confirming the identifying assumption that the instrument is uncorrelated with pre-existing insolvency trends.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Maryland Judiciary public access database | Criminal case records: 1.08 million cases 2000-2016; commissioner ID, release decisions, bail types, charge categories | [Maryland Judiciary](/wiki/datasets/maryland-judiciary/) |
| PACER (Public Access to Court Electronic Records) | Consumer bankruptcy filings 2000-2011: 318,000 filings in Maryland; chapter 7 and chapter 13 type, filing date, address | [PACER](/wiki/datasets/pacer-bankruptcy/) |
| ZTRAX (Zillow Transaction and Assessment Database) | Real estate transactions 1993-2020: 9 million Maryland transactions; foreclosure events post-2007, property-level matching | [ZTRAX](/wiki/licensed/ztrax/) (licensed) |
| Maryland Judiciary civil court records | Judgment lien filings 2000-2020: 386,938 lien filings; plaintiff/defendant address, filing date | [Maryland Judiciary](/wiki/datasets/maryland-judiciary/) |
| Federal Housing Finance Agency HPI | ZIP-code-level annual house price index; used to split sample into negative/positive HPI growth subsamples | No page yet |

Sample: over 500,000 criminal cases in Baltimore City, Montgomery County, and Prince George's County District Courts. 78% from Baltimore City. 81% Black defendants, 83% male, median age 30.

## When to read the full paper

Read the original if you are: studying the economics of the bail system or pretrial detention reform; working on household insolvency and liquidity shocks more broadly; replicating or extending the leave-out commissioner leniency instrument to other outcomes or jurisdictions; or testing the double-trigger hypothesis for foreclosures with a new source of liquidity shocks. Tables 5-9 contain the headline regressions; the Internet Appendix (available on the RFS website) contains robustness tests including a lagged IV, non-residualized IV, apartment-inclusive sample, and absorbing-state tests.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(11), November 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled (OUP standard publication reuse rights); no verbatim reproduction. Access the original at [https://doi.org/10.1093/rfs/hhaf009](https://doi.org/10.1093/rfs/hhaf009).

Citation: Slutzky, Pablo, and Sheng-Jun Xu. "The Financial Consequences of Pretrial Detention." *The Review of Financial Studies* 38, no. 11 (2025): 3329-3373. DOI: 10.1093/rfs/hhaf009.
