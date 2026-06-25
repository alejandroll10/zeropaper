---
title: "Financial Education of Executives: Custodio, Mendes & Metzger (2025)"
description: >-
  Distilled: An RCT with 92 medium and large Mozambican firms shows that an
  18-hour MBA-style corporate finance course for top executives causes firms to
  reduce working capital by 0.4 to 0.5 standard deviations (driven mainly by
  shorter accounts receivable collection periods), generating cash that is
  channeled into capital expenditure and raising ROA by 0.6 to 1.1 standard
  deviations. J. Finance 2025, CC BY 4.0. Eight core results with source
  locators, datasets used, the identification strategy, and the estimating
  equations.
sidebar:
  label: Custodio-Mendes-Metzger 2025
  order: 1
tags: [paper-summary, managerial-capital, corporate-finance, financial-education,
       working-capital, firm-performance, developing-economies, randomized,
       panel-regression, difference-in-differences, open-access, cc-by,
       peer-reviewed, unreplicated]
paper:
  authors: "Cláudia Custódio, Diogo Mendes, and Daniel Metzger"
  authorList:
    - { family: Custódio, given: Cláudia, orcid: "0000-0003-4048-0312", affiliation: "Imperial College London, CEPR, ECGI" }
    - { family: Mendes, given: Diogo, orcid: "0000-0002-9441-4671", affiliation: "Stockholm School of Economics and SHoF" }
    - { family: Metzger, given: Daniel, orcid: "0000-0002-6949-4817", affiliation: "Rotterdam School of Management and ECGI" }
  year: 2025
  venue: "The Journal of Finance 80(5), October 2025, 2875–2920"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13476
  jel:
    codes: [G30, G31, O16]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - "Financial Literacy, Pension, Retirement Analysis"
    - "Financial Reporting and Valuation Research"
    - "Working Capital and Financial Performance"
  dataAccess: hand-collected
  outcome:
    - working capital to assets ratio
    - accounts receivable to sales
    - capital expenditure to assets
    - return on assets (ROA)
    - implemented changes in financial policies (survey)
  outcomeClass: [firm-real-outcomes, firm-financing]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-08-18; corroborated by p. 2875 open-access notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "blocked-paywall (Wiley site wrapper; CC BY VOR licence confirmed in Crossref DOI metadata 2026-06-05)"
  redistribution: "extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)"
  resultsCount: 8
  citedByCount: 6

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression]
    identification: randomized

  contributionType: [new-fact, new-data]
  introducesData: true

  mechanisms:
    - financial-constraint
    - learning

  scope:
    region: Mozambique
    assetClass: private medium and large enterprises
    period: 2008-01..2019-12
    frequency: annual
    dataType: [accounting, survey, administrative]
    granularity: [firm]
    n: "92 firms (45 treatment, 47 control); up to 89 with financial data; sample period 2008-2017 for main outcomes"

  findings:
    - ref: R1
      outcome: working capital to assets ratio
      metric: sd-effect
      value: "-0.4 to -0.5 SD (coefficient -0.157 to -0.298, SD = 0.45)"
      direction: negative
      vsBenchmark: treated vs control firms, DID intention-to-treat; control-group mean 0.07 (Table II)
    - ref: R2
      outcome: accounts receivable to sales
      metric: sd-effect
      value: "-0.39 to -0.88 SD (coefficient -0.106 to -0.266, SD = 0.27)"
      direction: negative
      vsBenchmark: treated vs control, DID; dominant driver of working capital reduction (Table V)
    - ref: R3
      outcome: capital expenditure to assets
      metric: pp-effect
      value: "9 to 13 pp (coefficient 0.095 to 0.133, SD = 0.21)"
      direction: positive
      vsBenchmark: treated vs control, DID; approximately 0.45 to 0.63 SD increase (Table IV)
    - ref: R4
      outcome: return on assets (ROA)
      metric: sd-effect
      value: "0.67 to 1.09 SD increase (coefficient 0.140 to 0.229, SD = 0.21)"
      direction: positive
      vsBenchmark: treated vs control, DID; statistically significant at 5% level (Table IV)
    - ref: R5
      outcome: implemented changes in financial policies (survey)
      metric: pp-effect
      value: "55% of treated firms changed at least one policy vs 7% of control firms; working capital gap 25.6 pp (significant at 1%)"
      direction: positive
      vsBenchmark: treatment vs control 15 months post-intervention (Table III)
    - ref: R6
      outcome: working capital to assets ratio
      metric: sd-effect
      value: "Persistent: -0.249 SD (1-year), -0.165 SD (2-year) post-treatment (coefficients -0.249 and -0.165)"
      direction: negative
      vsBenchmark: effects persist over 2-year posttreatment window, 3-year estimate insignificant (Table VI)
    - ref: R7
      outcome: return on assets (ROA)
      metric: sd-effect
      value: "Persistent: coefficient 0.280 (1-year), 0.324 (2-year), 0.138 (3-year, insignificant)"
      direction: positive
      vsBenchmark: ROA effects hold over 2-year posttreatment window (Table VI)
    - ref: R8
      outcome: return on assets (ROA)
      metric: sd-effect
      value: "Treatment effect more pronounced for smaller firms and firms with lower leverage (Figure 3)"
      direction: positive
      vsBenchmark: firms without prior finance executive experience benefit most; consistent with learning as the mechanism

  resultType: new-finding

  relatesTo:
    - { cite: "Bloom et al. (2013)", relation: extends, note: "paper extends management-practices RCT literature (28 Indian plants) to financial practices of large firms in developing economies" }
    - { cite: "Custódio and Metzger (2014)", doi: '10.1016/j.jfineco.2014.06.002', relation: builds-on, note: "builds on non-experimental evidence that financial expert CEOs follow financial theory and have better financial policies" }
    - { cite: "Bertrand and Schoar (2003)", doi: '10.1162/003355303322552775', relation: builds-on, note: "builds on evidence that CEO characteristics shape firm financial policies" }
    - { cite: "Bruhn and Zia (2013)", doi: '10.1080/19439342.2013.780090', relation: extends, note: "extends business training RCT literature from microentrepreneurs to top executives of medium and large firms" }
    - { cite: "Spence (1973)", doi: '10.2307/1882010', relation: tests, note: "provides experimental evidence that finance education effects go beyond signaling by improving actual decision making" }

  openQuestions:
    - "Whether the findings generalize beyond Mozambique to other developing economies or to developed countries with well-functioning financial markets (p. 2916)."
    - "Whether online courses at low cost can achieve similar results to the in-person 18-hour MBA-style format tested here (p. 2917)."
    - "The exact learning channel (instructor-led vs peer learning vs networking) remains difficult to fully disentangle (p. 2913)."
    - "Long-run effects on capital structure and valuation practices, which were stated as intended by participants but not confirmed in accounting data (pp. 2878, 2898)."

  replicationCode:
    status: available

  proposedVocab:
    - { axis: topic, term: managerial-capital, def: "The skills, knowledge, and expertise of managers as a factor of production affecting firm decisions and performance.", aliases: [management-capital, managerial-skills] }

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-05", role: extracted, note: "Full PDF read (pp. 2875-2920); eight results extracted from Tables II-VI and Figure 3. Not human-verified. Not reproduced. Replication code referenced in the paper (Supporting Information) but not run here." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; one fix: R3 Table IV col. 8 CapEx coefficient significance corrected from *** to ** (t-stat 0.133/0.052 ≈ 2.56, below 1% threshold); all other locators, coefficients, SD conversions, persistence estimates (Table VI), and equation (1) terms confirmed correct."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13476", checked: "2026-06-05", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-18" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the RCT identification strategy, and the estimating equations from a field experiment on financial education for top executives in Mozambique: enough to know what was found and how, without reading all 46 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13476).

## TL;DR

The paper reports an RCT with 92 medium and large Mozambican firms: 45 were randomly assigned to receive a free 18-hour MBA-style corporate finance course (covering capital budgeting, capital structure, working capital management, and risk management) in May 2017; 47 were assigned to a control group that received the same course later. Using difference-in-differences on panel accounting data (2008-2017) and a 15-month follow-up survey, the authors find that treated firms significantly reduced working capital (by 0.4 to 0.5 standard deviations), primarily through faster collection of accounts receivable (0.4 to 1 standard deviation reduction). The freed-up cash was invested: capital expenditures increased by 9 to 13 percentage points of assets. Firm performance improved substantially: ROA rose by 0.67 to 1.09 standard deviations, with effects persisting over two years. No negative effect on sales is found. The learning channel (rather than networking) is the most plausible mechanism: executives without prior finance experience benefit most.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Working capital falls significantly** in treated firms relative to controls | Table II, p. 2895 | Coefficient on Treatment x Post ranges from -0.157\* (col. 2) to -0.298\*\*\* (col. 4, external sample); full-sample preferred spec: -0.222\*\* (col. 3). Corresponds to -0.4 to -0.5 SD (SD = 0.45) |
| R2 | **Accounts receivable drives the working capital reduction** (collection period falls by 39 to 97 days) | Table V, p. 2902 | A/R coefficient: -0.106\* (col. 1, OLS) to -0.266\*\*\* (col. 2, firm FE); corresponds to -0.39 to -0.88 SD (SD = 0.27). Inventory coefficient: -0.037 to -0.058, less robust |
| R3 | **Capital expenditure rises significantly**: freed-up cash is invested | Table IV, p. 2900, cols. 7-9 | Coefficient 0.095\*\* (col. 7) to 0.133\*\* (col. 8); approximately 0.45 to 0.63 SD increase (SD = 0.21) |
| R4 | **Firm ROA increases by 0.14 to 0.23** in the post-treatment period | Table IV, p. 2900, cols. 10-12 | Coefficient 0.140\*\* (col. 11, firm FE) to 0.229\*\* (col. 10, OLS); significant at 5%; equivalent to 0.67 to 1.09 SD of ROA (SD = 0.21) |
| R5 | **Survey evidence confirms policy changes**: 55% of treated vs 7% of control firms implemented at least one financial policy change; working capital gap 25.6 pp (significant at 1%) | Table III, p. 2897 | Open-ended responses: 29% treated vs 4% control changed working capital management (diff. 25.6\*\*\*). Combined open- and close-ended: 77% vs 52% (diff. 25.7\*\*) |
| R6 | **Working capital effects persist two years** after the intervention | Table VI, p. 2906, col. 1 | Post-1-year coefficient: -0.249\*\* (full sample); post-2-year: -0.165\*\*; post-3-year: not significant (due to control group being treated) |
| R7 | **ROA effects persist two years** and are directionally positive through year three | Table VI, p. 2906, col. 4 | Post-1-year: 0.280\*\*; post-2-year: 0.324\*\*; post-3-year: 0.138 (not significant) |
| R8 | **Heterogeneous effects**: firms with smaller size, lower leverage, and executives without prior finance experience benefit most from the program | Figure 3, p. 2904 | Point estimates for ROA uniformly positive across all subgroups; significantly more pronounced for small firms vs large and for executives without prior finance experience |

**Overall (paper's conclusion).** An 18-hour MBA-style executive finance course for top managers of medium and large private firms in Mozambique caused measurable improvements in financial decision making, primarily through better working capital management (faster A/R collection). The resulting cash was channeled into long-term investment, and firm ROA increased substantially and persistently. The evidence suggests that managerial financial expertise is an important constraint on firm performance in environments with severe financial frictions, and that low-cost educational interventions can build managerial capital and relax these constraints.

## Theory / model

The paper has no formal structural model. The theoretical framework is based on the observation that in a frictionless world financial decisions are irrelevant (Modigliani-Miller), but in environments with financial frictions, the ability to make optimal financial decisions can positively affect firm value. Mozambique is chosen as the setting because financial frictions are severe and there is large heterogeneity in financial expertise among top executives.

The paper tests two hypotheses:

1. Providing financial education to top executives causes changes in firm financial policies (the education-to-policy channel).
2. These policy changes improve firm performance, because the pre-treatment policies were suboptimal due to constraints on managerial capital (the policy-to-performance channel).

The paper situates itself relative to two literatures. First, the CEO-characteristics literature (Bertrand and Schoar (2003); Custódio and Metzger (2014)) documents in non-experimental settings that CEOs' financial expertise correlates with more sophisticated financial policies. This paper provides experimental evidence for the same link. Second, the management-practices RCT literature (Bruhn and Zia (2013); Bloom et al. (2013)) shows training effects for microentrepreneurs and small firms; this paper extends it to top executives of medium and large firms and to financial (rather than operational) practices.

The competing explanations the design rules out are:

- **Signaling (Spence (1973))**: if education only signals pre-existing ability, no real change in policies should occur. The RCT design, keeping CEOs matched to their firms while randomly varying education, breaks the endogenous matching that drives signaling effects.
- **Networking**: a separate networking event for the control group (organized around the treatment dates) allows the authors to show that networking per se does not replicate the working capital or ROA changes observed in treated firms (p. 2878).

The identification strategy exploits the staggered delivery of the course: the treatment group (cohort 1) received the course in May 2017; the control group (cohort 2) received it in November 2018/April 2019. The post-treatment window is the year-end 2017 financial data for the treatment group, before the control group was treated. Firm-level randomization was stratified by industry and conducted at the business-group level to minimize contamination.

## Method

The primary estimator is a difference-in-differences (DID) intention-to-treat (ITT) regression. Standard errors are clustered at the business-group level (the level of randomization). The approach builds on `difference-in-differences` and `panel-regression`.

The ITT design avoids post-randomization selection bias: all 92 firms are included regardless of whether the assigned participant actually attended (4 of 45 treatment firms did not attend for idiosyncratic reasons; participation rate 91%).

Two data sources are used:

- **External data** (KPMG "Top 100 Companies in Mozambique" annual reports): externally obtained, independent of study participation, available for 83 of 92 firms. Used for main outcomes (working capital, leverage, ROA, sales).
- **Hand-collected data**: directly requested from firms for supplementary outcomes (A/R, A/P, cash, CapEx). Available for 65 of 92 firms (71%), collected in 2018 and again in 2023.

A pseudo-external sample of supplementary outcomes is constructed by restricting hand-collected data to firms for which external data are also available, to address attrition concerns (p. 2894). Lee bounds (Lee (2009)) are computed for all outcomes to bound treatment effects under nonrandom sample selection (Table VII, p. 2909).

As a complementary estimator for the heterogeneous-effects analysis (Section III.E), ANCOVA is used instead of DID: the post-treatment outcome is regressed on the treatment indicator and the pre-treatment mean of the outcome variable. This approach increases power in settings of low autocorrelation and small samples (McKenzie (2012)).

## Empirical specifications

**Main DID specification (eq. 1, p. 2894).** For a firm-level outcome $$Y_{it}$$:

$$
Y_{it} = \alpha + \beta_1 \times \text{Treatment}_i \times \text{Post}_t + \beta_2 \times \text{Treatment}_i + \beta_3 \times \text{Post}_t + X_{it} + \gamma_i + \gamma_t + \varepsilon_{it} \tag{1}
$$

where $$\text{Treatment}_i$$ is a dummy for assignment to the treatment group (randomized), $$\text{Post}_t$$ equals one in 2017 (the first post-treatment year-end), $$\gamma_i$$ are firm fixed effects, $$\gamma_t$$ are year fixed effects, and $$X_{it}$$ are optional controls (GDP growth interacted with $$\text{Treatment}$$; lagged log size, Mozambican nationality, accounting background, and finance background interacted with $$\text{Post}$$). The coefficient of interest is $$\beta_1$$, the ITT effect. Standard errors are clustered at the business-group level.

The sample period is 2008 to 2017 (full sample) for main outcomes and 2013 to 2017 for supplementary outcomes (hand-collected). Specification (1) in Table II is a cross-sectional OLS without firm or year FE; specification (2) adds firm and year FE; specification (3) adds controls; specification (4) repeats specification (3) on the external-only sample. These four variants are run for each outcome throughout the paper.

**Persistence specification (Table VI, p. 2906).** Specification (3) from Table II is re-estimated replacing $$\text{Post}_t$$ with $$\text{Post}_{t=1\text{yr}}$$, $$\text{Post}_{t=2\text{yr}}$$, and $$\text{Post}_{t=3\text{yr}}$$, corresponding to year-end 2017, 2018, and 2019. Only firms for which data exist in all post-treatment years are included.

**Working capital components (Table V, p. 2902).** The same DID specification is applied to accounts receivable (A/R / Sales), accounts payable (A/P / Assets), and inventories (Inventory / Assets), scaled by one-year lagged sales or assets. The headline result is the A/R effect: coefficient -0.106\* (OLS, col. 1) to -0.266\*\*\* (firm FE + controls, col. 2), corresponding to a reduction in the average collection period of 39 to 97 days from a pretreatment mean of 179 days for treatment firms.

**Heterogeneous effects (Figure 3, p. 2904).** ANCOVA regressions of post-treatment ROA on the treatment indicator, pre-treatment ROA mean, and subgroup indicators (separately for below/above median assets, employment, cash, leverage; Masters-or-higher dummy; prior CFO experience dummy; prior accounting/finance background dummy; discretion-over-policies dummy). Results show larger point estimates for smaller firms, lower-leverage firms, and executives without prior finance experience.

**Robustness.** Randomization-t p-values (Young (2019), Table IA.V); Lee bounds for nonrandom attrition (Table VII); winsorized outcome variables (Figure IA.8); ANCOVA instead of DID (Table IA.VI); bootstrap standard errors following Bloom et al. (2013) (Table IA.VI Panel B); results on balanced panel (Table IA.VII); exclusion of CEO-turnover firms (Table IA.X); alternative scaling of working capital (Table IA.XI).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| KPMG "Top 100 Companies in Mozambique" annual reports (2008-2019) | External accounting data: working capital, sales, leverage, ROA for 83 of 92 firms | No page yet |
| Hand-collected firm financial statements (2013-2019) | Supplementary accounting data: A/R, A/P, cash, CapEx for 65 of 92 firms; collected via face-to-face meetings and email | No page yet |
| Follow-up survey (November 2018) | Survey outcomes: stated policy changes in working capital, valuation, capital structure, and risk management; 15 months post-intervention | No page yet |
| Post-learning exit surveys (May 2017; November 2018/April 2019) | Intentions to change financial policies immediately after attending the course | No page yet |
| KPMG reports (nonparticipating firms) | External-validity benchmark: nonparticipating Mozambican firms for parallel-trend checks | No page yet |

Sample: 92 firms (45 treatment, 47 control) enrolled; up to 89 with at least one year of financial data. Accounting data spans 2008-2019 for external sources and 2013-2019 for hand-collected data. The outcome window for the main test is year-end 2017.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13476) if you are: (i) replicating the ITT estimates or running the Lee bounds / robustness variants (the Internet Appendix contains all supplementary tables); (ii) designing a similar executive education RCT and need the exact course content, recruitment procedure, or survey instruments; (iii) interested in the mechanisms section (V.B) and policy considerations (V.C) for external-validity arguments; or (iv) studying heterogeneous treatment effects by firm size, leverage, or executive background.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Custódio, Cláudia, Diogo Mendes, and Daniel Metzger.
> "The Impact of the Financial Education of Executives on the Financial Practices of Medium and Large Enterprises."
> *The Journal of Finance* 80, no. 5 (October 2025): 2875–2920.
> DOI: 10.1111/jofi.13476. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
