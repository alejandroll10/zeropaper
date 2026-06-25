---
title: "Regulatory Fragmentation: Kalmenovitz, Lowry & Volkova (2025)"
description: >-
  Distilled: Using the full text of the Federal Register (1994-2019), the paper
  constructs a firm-specific measure of regulatory fragmentation and documents
  that fragmentation increases firm costs (SG&A +4.3% SD), reduces productivity
  (TFP -3.6% SD) and profitability (ROA -5.3% to -5.9% SD), slows growth, deters
  entry, and pushes out small firms, with inconsistency across agencies driving more
  harm than mere duplication. J. Finance 2025, paywalled. Seven core results with
  source locators, datasets used, the measurement framework, and the estimating
  specifications.
sidebar:
  label: Kalmenovitz-Lowry-Volkova 2025
  order: 1
tags: [paper-summary, regulation, regulatory-burden, text-as-data, firm-real-outcomes,
       firm-financing, panel-regression, peer-reviewed, unreplicated,
       data:federal-register, data:wrds, data:edgar]
paper:
  authors: Joseph Kalmenovitz, Michelle Lowry, Ekaterina Volkova
  authorList:
    - { family: Kalmenovitz, given: Joseph, orcid: "0009-0001-6843-6703", affiliation: University of Rochester }
    - { family: Lowry, given: Michelle, orcid: "0000-0003-0703-8952", affiliation: Drexel University }
    - { family: Volkova, given: Ekaterina, orcid: "0000-0002-6589-0433", affiliation: University of Melbourne }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1081-1126
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13423
  jel:
    codes: [G38, L51, D73]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Political Influence and Corporate Strategies"]
  dataAccess: licensed-commercial
  outcome:
    - SG&A expenses (overhead costs)
    - total factor productivity (TFP)
    - return on assets (ROA)
    - sales growth
    - asset growth
    - industry entry (IPOs) and exit rates
    - lobbying expenditures
  outcomeClass: [firm-real-outcomes, firm-financing]
  license: "Wiley VOR terms and conditions (paywalled); no Creative Commons licence detected in Crossref metadata"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley Online Library, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 42
  introducesData: true
  methods:
    role: both
    contributes: regulatory-fragmentation-measure
    family: descriptive
    buildsFrom: [lda-topic-model, panel-regression, fama-macbeth]
    identification: selection-on-observables
  contributionType: [new-data, new-fact, measurement]
  mechanisms: [organizational-complexity, market-power]
  scope:
    region: US
    assetClass: US public firms
    period: 1995-01..2019-12
    frequency: annual
    dataType: [text, accounting, market, administrative]
    granularity: [firm, aggregate]
    n: "60,573 company-year observations (CRSP/Compustat, 1995-2019)"
  findings:
    - ref: R1
      outcome: SG&A expenses
      metric: coefficient
      value: "0.043*** (SE 0.015) with year+company FE; 0.055*** (SE 0.014) with industry x year+company FE"
      direction: positive
      vsBenchmark: one-SD increase in regulatory fragmentation; normalized coefficients
    - ref: R2
      outcome: total factor productivity (TFP)
      metric: coefficient
      value: "-0.036** (SE 0.016) with year+company FE; -0.032* (SE 0.018) with industry x year+company FE"
      direction: negative
      vsBenchmark: one-SD increase in regulatory fragmentation; normalized coefficients
    - ref: R3
      outcome: return on assets (ROA)
      metric: coefficient
      value: "-0.059*** (SE 0.013) with year+company FE; -0.053*** (SE 0.015) with industry x year+company FE"
      direction: negative
      vsBenchmark: one-SD increase in regulatory fragmentation; normalized coefficients
    - ref: R4
      outcome: sales growth
      metric: coefficient
      value: "-0.099*** (SE 0.017) with year+company FE; -0.110*** (SE 0.022) with industry x year+company FE"
      direction: negative
      vsBenchmark: one-SD increase in regulatory fragmentation; normalized coefficients
    - ref: R5
      outcome: asset growth
      metric: coefficient
      value: "-0.143*** (SE 0.024) with year+company FE; -0.139*** (SE 0.027) with industry x year+company FE"
      direction: negative
      vsBenchmark: one-SD increase in regulatory fragmentation; normalized coefficients
    - ref: R6
      outcome: industry entry (IPOs) and exit rates
      metric: coefficient
      value: "IPOs: -0.050*** (SE 0.014); small-firm exit +0.036** (SE 0.016); large-firm exit -0.046** (SE 0.018); total peers -0.035*** (SE 0.008)"
      direction: negative
      vsBenchmark: "fragmentation deters entry (fewer IPOs), accelerates small-firm exit, retains large firms; net industry shrinkage"
    - ref: R7
      outcome: lobbying expenditures
      metric: coefficient
      value: "log(Lobbying $): -0.106*** (SE 0.032) with year+company FE; -0.102** (SE 0.038) with industry x year FE"
      direction: negative
      vsBenchmark: "fragmentation reduces lobbying, consistent with lower regulatory-capture effectiveness when oversight is dispersed"
  resultType: new-finding
  relatesTo:
    - { cite: "Kalmenovitz (2023)", doi: '10.1093/rfs/hhad001', relation: extends, note: "same FR-based approach to regulatory intensity; this paper adds the fragmentation (multi-agency) dimension" }
    - { cite: "Stigler (1971)", doi: '10.2307/3003160', relation: tests, note: "tests public-choice theory that regulation serves incumbents; fragmentation cuts lobbying, inconsistent with pure capture" }
    - { cite: "Agarwal et al. (2014)", doi: '10.1093/qje/qju003', relation: builds-on, note: "evidence on inconsistency across banking regulators; this paper formalizes fragmentation measurement across all sectors" }
    - { cite: "Hoberg and Phillips (2016)", doi: '10.1086/688176', relation: cites, note: "text-based product market similarity scores used to define product-market peers for entry/exit analysis" }
    - { cite: "Lowry, Michaely and Volkova (2020)", doi: '10.1093/rfs/hhaa007', relation: cites, note: "LDA methodology on SEC/firm text applied here to the Federal Register" }
  openQuestions:
    - "The paper lacks an exogenous shock that randomly shifts regulatory fragmentation across firms; causal identification therefore rests on saturated fixed effects and placebo tests rather than a natural experiment (p. 1085)."
    - "The analysis is limited to the flow of regulatory activity captured in the Federal Register and does not model the full stock of existing regulation or enforcement actions, which may carry additional fragmentation effects (p. 1085)."
    - "Agency-level analysis is at the agency-year level; individual-level data do not identify which specific rules employees work on, limiting the test of empire-building incentives (p. 1120)."
  replicationCode:
    url: "http://www.evolkova.info/data/fragmentation/"
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full PDF read (pp. 1081-1126, 46 pages); seven results extracted from Tables IV, V, VIII, X. Not human-verified. Not reproduced. Replication data posted by authors at evolkova.info."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; one fix applied: R6 large-firm exit significance corrected from *** to ** (Table VIII col 4, SE 0.018, two stars in PDF); all other locators, coefficients, SEs, and equations confirmed correct."
  licenceVerification:
    - source: "Crossref REST API works/10.1111/jofi.13423"
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-30; no Creative Commons licence present"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the measurement framework (LDA-based regulatory fragmentation measure), and the regression specifications: enough to know what it found and how, without reading all 46 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13423). Firm-year data are publicly available at [evolkova.info](http://www.evolkova.info/data/fragmentation/).

## TL;DR

The paper introduces the concept of regulatory fragmentation: the regulation of a single topic by multiple federal agencies. Using the full text of the Federal Register (783,950 documents, 1994-2019), it applies Latent Dirichlet Allocation (LDA) to identify 100 regulatory topics and measure which agencies regulate each. It then matches these topics to firm-level 10-K filings to build a firm-specific, time-varying exposure measure. Across 60,573 firm-year observations (CRSP/Compustat, 1995-2019), higher regulatory fragmentation is associated with significantly higher SG&A costs, lower total factor productivity, lower profitability, slower sales and asset growth, less industry entry, and greater exit of small firms. Inconsistency across agencies (not just redundancy) drives the harm. Agency incentives, proxied by unexplained promotion activity, predict more fragmentation.

## Core results

Magnitudes and significance are as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. All variables are normalized so coefficients reflect a one-standard-deviation change. Independent variables are lagged one period. Standard errors clustered at the Fama-French 48-industry level.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Regulatory fragmentation raises SG&A expenses**: higher fragmentation is associated with significantly higher overhead costs in both year+company and industry x year+company FE specifications | Table IV, cols (1)/(4), p. 1106 | Coefficient on Regulatory Fragmentation: 0.043\*\*\* (SE 0.015) [year+co FE]; 0.055\*\*\* (SE 0.014) [ind x yr+co FE] |
| R2 | **Regulatory fragmentation reduces TFP**: a one-SD increase in fragmentation is followed by a 3.2-3.6% SD decrease in total factor productivity | Table IV, cols (2)/(5), p. 1106 | -0.036\*\* (SE 0.016) [year+co FE]; -0.032\* (SE 0.018) [ind x yr+co FE] |
| R3 | **Regulatory fragmentation lowers profitability (ROA)**: the effect ranges from -5.3% to -5.9% of a SD | Table IV, cols (3)/(6), p. 1106 | -0.059\*\*\* (SE 0.013) [year+co FE]; -0.053\*\*\* (SE 0.015) [ind x yr+co FE] |
| R4 | **Regulatory fragmentation slows sales growth**: a one-SD increase is followed by a 9.9-11.0% SD decrease in sales growth | Table V, cols (1)/(4), p. 1109 | -0.099\*\*\* (SE 0.017) [year+co FE]; -0.110\*\*\* (SE 0.022) [ind x yr+co FE] |
| R5 | **Regulatory fragmentation slows asset growth**: a one-SD increase is followed by a 13.9-14.3% SD decrease in asset growth | Table V, cols (2)/(5), p. 1109 | -0.143\*\*\* (SE 0.024) [year+co FE]; -0.139\*\*\* (SE 0.027) [ind x yr+co FE] |
| R6 | **Regulatory fragmentation deters entry and increases small-firm exit**: fragmentation reduces new IPOs, raises small-firm exit rates, and has a net negative effect on industry size; large firms benefit from the resulting barriers | Table VIII, p. 1115 | IPOs: -0.050\*\*\* (SE 0.014); small-firm exit: +0.036\*\* (SE 0.016); large-firm exit: -0.046\*\* (SE 0.018); total peers: -0.035\*\*\* (SE 0.008); all industry x year+company FE |
| R7 | **Regulatory fragmentation reduces lobbying**: firms reduce lobbying as fragmentation rises, consistent with lower returns to regulatory capture when oversight is dispersed across many agencies | Table X, cols (1)/(3), p. 1118 | log(Lobbying $): -0.106\*\*\* (SE 0.032) [year+co FE]; -0.102\*\* (SE 0.038) [ind x yr FE]; n = ~14,983 |

**Overall (paper's conclusion).** Regulatory fragmentation is a costly but previously undocumented dimension of regulatory burden. The negative effects arise primarily from inconsistency, not mere duplication: effects are weaker when agencies co-author documents (coordinated regulation), and stronger when agencies independently regulate the same topic. Agency promotion incentives are positively linked to rulemaking activity outside core expertise, suggesting empire-building as one mechanism driving fragmentation. These findings extend the regulatory-intensity measurement of Kalmenovitz (2023) by adding the multi-agency dimension, are consistent with the theory of economic regulation of Stigler (1971), draw on the evidence of inconsistency across banking regulators in Agarwal et al. (2014), and apply the LDA methodology of Lowry, Michaely and Volkova (2020).

## Theory / model

The paper has no formal model. The empirical strategy is built on two competing hypotheses about the sign of the fragmentation effect, drawn from the industrial organization literature on regulation.

**Hypothesis 1 (fragmentation is beneficial).** Multiple agencies create regulatory competition, let firms choose the least restrictive regulator, and may enable more efficient regulation via a race to the top. Firms can also focus lobbying on the agency most susceptible to capture. Under this view, higher fragmentation should lower costs and raise productivity and growth.

**Hypothesis 2 (fragmentation is costly).** Multiple agencies create duplicative compliance requirements, and more critically, inconsistent requirements that raise uncertainty. Firms cannot fully anticipate how to resolve discrepancies across agencies. Fragmentation also reduces firms' ability to direct lobbying effort. Under this view, higher fragmentation should raise costs and reduce productivity and growth.

The empirical results uniformly support Hypothesis 2. The paper provides no general equilibrium or structural model; its contribution is the measurement framework and the empirical evidence.

The **identification strategy** relies on within-firm, within-industry variation in regulatory fragmentation over time, with company fixed effects absorbing time-invariant firm heterogeneity and industry x year fixed effects removing industry-wide trends. The main endogeneity concern (firm operational changes causing apparent fragmentation changes) is addressed by: (i) excluding firm-years with industry switches, segment count changes, or asset changes exceeding 20% (Table VII); (ii) 1,000-iteration placebo tests that randomly reassign topics to firms (Figure 7); and (iii) coefficient stability analysis following Oster (2019). The authors acknowledge they lack an exogenous shock that randomly shifts fragmentation across firms (p. 1085).

## Method

**Step 1: Topic identification in the Federal Register.** LDA (Latent Dirichlet Allocation) is applied to the full text of 783,950 FR documents (1994-2019) from the Rules, Proposed Rules, and Notices sections. LDA generates 100 topics; each document receives a topic distribution. Topic labels are assigned using CFR subject classifications. For each topic $$i$$ and year $$t$$, the fraction of words written by agency $$a$$ is:

$$
\omega^2_{i,a,t} = \frac{\text{words by agency } a \text{ on topic } i \text{ in year } t}{\text{total words on topic } i \text{ in year } t} \tag{1 (within AgencyHHI)}
$$

The fragmentation of topic $$i$$ in year $$t$$ across agencies (equation (2), p. 1091) equals one minus the HHI:

$$
\text{Regulatory Fragmentation}_{i,t} = 1 - \text{AgencyHHI}_{i,t} = 1 - \sum_{\text{Agency}} \omega^2_{i,a,t} \tag{2}
$$

Values near zero indicate a single dominant agency; values near one (maximum 0.992 with 121 agencies) indicate dispersion across many agencies.

**Step 2: Measuring firm-level topic exposure.** The same LDA model (trained on FR documents) is applied to each firm's annual 10-K. The fraction of the 10-K devoted to topic $$i$$ in year $$t$$ is $$P_{f,i,t}$$. The dispersion of topics within a firm (equation (3), p. 1091) is:

$$
\text{Dispersion of Topics within Firm}_{f,t} = 1 - \sum_{\text{Topic}} P^2_{f,i,t} \tag{3}
$$

**Step 3: Firm-level regulatory fragmentation.** The main measure (equation (4), p. 1093) is the weighted average of topic-level fragmentation, where weights are each topic's share in the firm's 10-K:

$$
\text{Regulatory Fragmentation}_{f,t} = \sum_{i} P_{f,i,t} \cdot \text{Regulatory Fragmentation}_{i,t} \tag{4}
$$

**Step 4: Regulation quantity control.** To separate fragmentation from sheer regulatory volume, the paper constructs a control for the quantity of regulation (equation (5), p. 1095):

$$
\text{RegulationQuantity}_{f,t} = \sum_{\text{Topic}} P_{f,i,t} \cdot \log(\text{Words}_{i,t}) \tag{5}
$$

This is the weighted average of log(FR words) across topics, weighted by firm relevance.

**Validation.** Two alternative dispersion measures are constructed from FR agency mentions of companies (equation (6), p. 1096) and from 10-K agency mentions by companies (equation (7), p. 1096). Panel D of Table II (p. 1098) shows that the primary measure is significantly positively correlated with both alternatives, with a 1-SD increase in fragmentation associated with a 5.0% increase in agency-mention dispersion in the FR.

## Empirical specifications

The main regression specification (equation (8), p. 1104) is:

$$
y_{f,t+1} = \alpha + \beta \cdot \text{Regulatory Fragmentation}_{f,t} + \vec{X}_{f,t}' \gamma + \tau_t + \theta_k + \mu_f + \varepsilon \tag{8}
$$

where $$y_{f,t+1}$$ is a firm-level outcome (SG&A/AT, TFP, ROA, sales growth, asset growth, Emp/AT), $$\tau_t$$ are year fixed effects, $$\theta_k$$ are industry (Fama-French 48) fixed effects, and $$\mu_f$$ are company fixed effects. The tighter specifications replace $$\tau_t + \theta_k$$ with industry x year fixed effects. All continuous independent variables are winsorized at the 0.5% and 99.5% levels and normalized; standard errors are clustered at the Fama-French 48-industry level. Independent variables are lagged one period.

Firm-level controls $$\vec{X}_{f,t}$$ include: log(Words, 10-K), PPE/AT, EBITDA/AT, log(Sales), Tobin's Q, Dispersion of Topics within Firm, and Regulation Quantity.

**Core outcome regressions (Tables IV and V, pp. 1106, 1109):** The main results are estimated for six outcomes: SG&A/AT (costs), TFP (productivity), ROA (profitability), sales growth, asset growth, and Emp/AT (employment). The baseline coefficient on Regulatory Fragmentation ranges from 0.043 (SG&A, positive) to -0.143 (asset growth, negative) in standardized units (R1-R5).

**Industry composition regressions (Table VIII, p. 1115):** For entry (R6), the dependent variable is the count of new peers (IPOs or industry joiners) in year t+1; for exit, it is the rate of peers in year t no longer present in year t+1, separately for small and large firms (defined by above/below-average assets within Fama-French 48 industry). Product-market peers are defined using Hoberg and Phillips (2016) TNIC-3 similarity scores.

**Channel test: co-authorship (Table IX, p. 1117):** The indicator $$\text{CoAuthored}_{f,t}$$ (above-median exposure to topics where FR documents are co-authored by multiple agencies) is interacted with Regulatory Fragmentation in a fully interacted model. The interaction coefficient is negative (e.g., SG&A: Regulatory Fragmentation x CoAuthored = -0.014**, SE 0.006), confirming that inconsistency (solo-authored, potentially conflicting rules) drives more harm than coordination.

**Lobbying regressions (Table X, p. 1118):** The dependent variable is log(1 + lobbying expenditures in USD millions) and raw lobbying expenditures, from the LobbyView database (Kim (2018)), for 14,983-14,986 company-year observations. Regressions include company and year fixed effects, or industry x year fixed effects.

**Agency incentives (Table XI, p. 1121):** The dependent variable is Unexpected Promotions at agency a in year t+1, constructed as residuals from an employee-level promotion model (controlling for tenure, agency x rank, and occupation fixed effects). The key independent variable is the number of FR words written by the agency in notices (or rules) in year t, and its interaction with the share of words in the agency's top 10 topics. The positive coefficient on Words (e.g., Words in notices: 0.615**, SE 0.234) and the negative coefficient on the interaction with core topics support the view that agency employees are rewarded for expanding rulemaking, particularly outside core areas.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Federal Register (full text, 1994-2019) | Main input; LDA topic model trained on 783,950 documents to measure regulatory fragmentation and quantity | [Federal Register](/wiki/datasets/federal-register/) |
| SEC EDGAR (10-K filings) | Applied LDA model to firm 10-Ks to measure firm-topic exposure $$P_{f,i,t}$$; log(Words, 10-K) control | [EDGAR](/wiki/datasets/edgar/) |
| CRSP / Compustat (via WRDS) | Firm-year outcome variables (SG&A, TFP, ROA, sales, assets, Tobin's Q), sample construction; 60,573 firm-years 1995-2019 | [WRDS](/wiki/licensed/wrds/) (licensed) |
| LobbyView lobbying database | Lobbying expenditures for ~14,983 firm-year observations; from Kim (2018) | No page yet |
| Hoberg-Phillips TNIC-3 | Product-market peer similarity scores for industry composition analysis | No page yet |
| OPM/FOIA employee compensation data | Individual-level compensation and rank for 75 federal agencies; used in agency incentive analysis | No page yet |
| Fragmentation firm-year data (evolkova.info) | Authors' public release of the main regulatory fragmentation measure | No page yet |

Sample: 60,573 company-year observations, 1995-2019 (CRSP/Compustat firms with nonmissing 10-Ks in SEC EDGAR). Frequency: annual.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13423) if you are: building a measure of multi-agency regulatory exposure for a specific sector or firm set; extending the fragmentation analysis to enforcement actions or international regulation; studying the industrial organization of the federal government and agency incentives; or replicating the TFP or sales-growth results, which have the largest magnitudes and require careful construction of the LDA model and Imrohoroglu-Tuzel TFP measure. The Internet Appendix (at the publisher's site) contains additional robustness tables and the LDA methodology details.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled (Wiley VOR terms; no Creative Commons licence). Extract-only.

> Kalmenovitz, Joseph, Michelle Lowry, and Ekaterina Volkova.
> "Regulatory Fragmentation."
> *The Journal of Finance* 80, no. 2 (April 2025): 1081-1126.
> DOI: 10.1111/jofi.13423. © 2025 the American Finance Association.
