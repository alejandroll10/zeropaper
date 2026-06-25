---
title: "Venture Capital and Startup Agglomeration: Chen & Ewens (2025)"
description: >-
  Distilled: Using the Volcker Rule as a natural experiment, Chen and Ewens
  show that bank withdrawal from VC limited partnerships caused fewer and smaller
  VC funds in high-bank-exposure states, reduced startup financing and valuations,
  and induced startups to migrate to VC hubs (CA, MA, NY), directly implicating
  the local supply of venture capital in startup geographic concentration. J.
  Finance 2025, paywalled. Eight core results with source locators, datasets
  used, the identification strategy (DiD on Volcker Rule exposure), and the
  estimating specifications.
sidebar:
  label: Chen-Ewens 2025
  order: 1
tags: [paper-summary, venture-capital, entrepreneurship, agglomeration, geography,
       financial-constraints, difference-in-differences, panel-regression,
       peer-reviewed, unreplicated,
       data:call-reports, data:venturesource, data:pitchbook, data:edgar, data:preqin]
paper:
  authors: Jun Chen, Michael Ewens
  authorList:
    - { family: Chen, given: Jun, orcid: "0000-0003-2360-3712", affiliation: University of Illinois Chicago }
    - { family: Ewens, given: Michael, orcid: "0000-0002-6968-8451", affiliation: Columbia Business School }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2153–2198
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13451
  jel:
    codes: [G24, R12, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Private Equity and Venture Capital", "Firm Innovation and Growth", "Entrepreneurship Studies and Influences"]
  dataAccess: licensed-commercial
  outcome:
    - number and size of VC funds raised by state
    - startup financing round size
    - startup pre-money valuation
    - probability of startups migrating to VC hubs
  outcomeClass: [firm-financing, firm-dynamics]
  license: "Wiley VOR terms (not CC); paywalled (Crossref license URL: http://onlinelibrary.wiley.com/termsAndConditions#vor, content-version vor, delay-in-days 0, start 2025-04-01)"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site, confirmed via Crossref DOI metadata 2026-06-05)"
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 10
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, instrumental-variables]
    identification: natural-experiment
  contributionType: [new-fact]
  mechanisms: [financial-constraint, information-asymmetry]
  scope:
    region: US
    assetClass: venture capital funds and VC-backed startups
    period: 2010-01..2018-12
    frequency: annual
    dataType: [administrative, accounting, other]
    granularity: [aggregate, firm]
    n: "1,617 VC funds; 11,048 VC-backed startups; 35 states; 2010-2018"
  findings:
    - ref: R1
      outcome: number of VC funds raised by state
      metric: coefficient
      value: "Bank Expo x Post = -0.036** (SE 0.013); implies 11% fewer VC funds per 1-SD increase in bank exposure"
      direction: negative
      vsBenchmark: pre-Volcker parallel trends confirmed; no pre-treatment differential in 2010-2012 (Table IV)
    - ref: R2
      outcome: total VC capital raised by state
      metric: coefficient
      value: "Bank Expo x Post = -0.013*** (SE 0.006); implies 9% less total VC capital raised per 1-SD increase in bank exposure"
      direction: negative
    - ref: R3
      outcome: VC fund size (for funds that did close)
      metric: coefficient
      value: "Bank Expo x Post = -0.281* (SE 0.141) to -0.305** (SE 0.145); 22% smaller fund size per 1-SD increase in bank exposure (moving from NY to MO)"
      direction: negative
    - ref: R4
      outcome: probability of raising a follow-on fund post-Volcker Rule
      metric: probability
      value: "Bank Expo = -0.030*** (SE 0.010) by 2014; -0.055** (SE 0.027) by 2018; mean dep. var. 0.514 by 2018"
      direction: negative
      vsBenchmark: consistently negative across all event windows 2014-2018 (Table III Panel C)
    - ref: R5
      outcome: startup first-round VC financing (capital raised)
      metric: coefficient
      value: "Bank Expo x Post = -0.089*** (SE 0.027); 7% smaller first-round financing per 1-SD increase in bank exposure"
      direction: negative
    - ref: R6
      outcome: startup pre-money valuation at first VC financing
      metric: coefficient
      value: "Bank Expo x Post = -0.112*** (SE 0.040); 9% lower pre-money valuation per 1-SD increase in bank exposure (approximately $1.3 million)"
      direction: negative
    - ref: R7
      outcome: probability of startup migrating headquarters to California
      metric: probability
      value: "Bank Expo x Post = 0.117*** (SE 0.018); 30% increase relative to sample mean per 1-SD increase in bank exposure"
      direction: positive
      vsBenchmark: null effect for migration to non-VC-hub states (Table VIII Panel C, placebo)
    - ref: R8
      outcome: probability of startup migrating to any VC hub (CA, MA, NY)
      metric: probability
      value: "Bank Expo x Post = 0.175*** (SE 0.041); 24% increase relative to sample mean per 1-SD increase in bank exposure"
      direction: positive
      vsBenchmark: null for non-VC hubs; significant differential treatment effect confirmed (Table VIII Panel B vs C)
  resultType: new-finding
  relatesTo:
    - { cite: "Kortum and Lerner (2000)", relation: builds-on, note: "LP supply shocks as instruments for VC activity; this paper uses a similar logic via the Volcker Rule shock to bank LPs" }
    - { cite: "Hochberg and Rauh (2013)", doi: '10.1093/rfs/hhs128', relation: builds-on, note: "LP home bias in VC; local bias is the mechanism through which bank LP loss maps to region-specific VC shortfalls" }
    - { cite: "Gonzalez-Uribe (2020)", doi: '10.1016/j.jfineco.2019.05.017', relation: extends, note: "exploits LP supply shocks to identify VC effects; this paper extends to geographic clustering and startup migration" }
    - { cite: "Chen et al. (2010)", doi: '10.1016/j.jue.2009.09.013', relation: builds-on, note: "geographic concentration and local bias in VC investing; underpins the identification assumption" }
    - { cite: "Gompers and Lerner (2000)", doi: '10.1016/s0304-405x(99)00052-5', relation: builds-on, note: "fund inflows drive private equity valuations; this paper confirms analogous valuation changes for local startups" }
    - { cite: "Samila and Sorenson (2011)", doi: '10.1162/rest_a_00066', relation: extends, note: "endowment LP returns as VC supply instrument; this paper uses bank LPs and the Volcker Rule as a cleaner regional shock" }
  openQuestions:
    - "Whether the documented startup agglomeration effects are permanent or whether regions recover their VC ecosystems over longer post-Volcker horizons than the 2014-2018 window studied (p. 2195)."
    - "Whether angel financing or accelerators fully substitute for local VC supply shortfalls; the data are incomplete and the authors cannot conclusively rule out substitution (p. 2192, footnote 48)."
    - "The welfare consequences of VC-driven startup migration: while migration to hubs provides capital access, it may also reduce local innovation and talent pools in affected regions (p. 2195, Internet Appendix Table IA.XIII on local patents)."
  replicationCode:
    url: "https://github.com/michaelewens/Banks-In-VC"
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full PDF read (pp. 2153-2198, 46 pages); eight core results extracted from Tables III, VI, VIII; equations transcribed from p. 2170 (eq. 1). Not human-verified. Not reproduced. Replication code available at https://github.com/michaelewens/Banks-In-VC." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-05, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; one fix applied: R1 significance corrected from *** to ** (Table III Panel A col.(1) shows -0.036** at 5% level, not 1%)." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13451", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-04-01. Not a CC licence; Wiley standard VOR terms only." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, identification strategy, and estimating equations: enough to understand what it found and how, without reading all 46 pages. To replicate or extend, read the original at [https://doi.org/10.1111/jofi.13451](https://doi.org/10.1111/jofi.13451). Replication data are at [https://github.com/michaelewens/Banks-In-VC](https://github.com/michaelewens/Banks-In-VC).

## TL;DR

The paper asks whether local VC supply drives the geographic concentration of high-growth startups in the United States. The identification lever is the Volcker Rule (implemented December 2013): banking entities were prohibited from investing in VC funds as limited partners (LPs), and this restriction fell disproportionately on Midwestern and Southern states where banks had historically been a larger share of VC fund capital (bank exposure up to 25% of LP capital in some states, below 5% in CA). Using a difference-in-differences design, the paper shows that states more exposed to the bank LP shock experienced: (1) fewer and smaller VC funds; (2) smaller startup financing rounds, lower pre-money valuations, and increased pre-VC financing; and (3) a 24-30% increase in startups migrating to VC hubs (CA, MA, NY), but no increase in migration to non-VC-hub states. The migration evidence directly links local VC supply to startup agglomeration.

## Core results

Magnitudes and significance as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. "1-SD increase in bank exposure" corresponds to moving from a low-exposure state (e.g., New York) to a high-exposure state (e.g., Wisconsin or Missouri). Regression coefficients are multiplied by 100 in the migration tables (Table VIII). Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Fewer VC funds** in high-exposure states after Volcker Rule | Table III Panel A col.(1), p. 2173 | Bank Expo x Post = -0.036\*\* (SE 0.013); 11% fewer VC funds per 1-SD bank exposure increase |
| R2 | **Less total VC capital raised** in high-exposure states | Table III Panel A col.(5), p. 2173 | Bank Expo x Post = -0.013\*\*\* (SE 0.006); 9% less total VC capital per 1-SD increase |
| R3 | **Smaller VC funds** (intensive margin) in high-exposure states | Table III Panel B col.(1)-(2), p. 2174 | Bank Expo x Post = -0.281\* to -0.305\*\*; 22% smaller fund size per 1-SD increase (NY to MO) |
| R4 | **Lower probability of raising a follow-on fund** for pre-Volcker VC firms | Table III Panel C, p. 2174 | Bank Expo = -0.030\*\*\* to -0.055\*\*; by 2018, 10pp lower probability against mean of 51.4% |
| R5 | **Startups raise 7% smaller first VC rounds** in high-exposure states | Table VI Panel A col.(1), p. 2180 | Bank Expo x Post = -0.089\*\*\* (SE 0.027); 7% smaller first-round VC financing per 1-SD increase |
| R6 | **Startup pre-money valuations 9% lower** (approx. $1.3M) in high-exposure states | Table VI Panel B col.(1), p. 2180 | Bank Expo x Post = -0.112\*\*\* (SE 0.040); 9% lower pre-money valuation per 1-SD increase |
| R7 | **Startups 30% more likely to migrate to CA** from high-exposure states post-Volcker | Table VIII Panel A col.(1), p. 2184 | Bank Expo x Post = 0.117\*\*\* (SE 0.018); null for non-VC-hub states (placebo Panel C) |
| R8 | **24% more likely to migrate to any VC hub** (CA, MA, NY) from high-exposure states | Table VIII Panel B col.(1), p. 2185-2186 | Bank Expo x Post = 0.175\*\*\* (SE 0.041); differential vs. non-VC-hub confirmed significant |

**Overall (paper's conclusion).** The Volcker Rule created an unintended natural experiment that reveals a causal role for local VC supply in startup geographic clustering. The loss of bank LPs reduced VC fundraising and startup financing in non-hub regions; startups responded by migrating to VC hubs, exacerbating existing geographic disparities in entrepreneurship. VC funding constraints rather than industry alignment or geographic distance explain the migration direction. VCs outside traditional hubs are financially constrained, and nonlocal VCs cannot fill the gap because of information asymmetry and local bias in investing.

## Theory / model

The paper has no formal structural model. The economic logic rests on two documented facts combined into a causal chain, with testable predictions:

**Fact 1 (LP home bias).** All LP types, including banks, exhibit significant in-state overweighting when investing in VC funds, following the finding of Hochberg and Rauh (2013) on LP home bias in private equity. Table V Panel A (p. 2178) shows that bank LPs allocate 23.2% of investments to in-state VCs, which is 11.5% above the share of all VC investments in the state (benchmark BM1) and 11.9% above the share of all out-of-state investments in the state (BM2). This surpasses all other LP types (pension funds: 20.8%; endowments: 12.6%).

**Fact 2 (geographic heterogeneity in bank LP exposure).** States outside the major VC hubs had historically higher bank LP shares, consistent with the geographic VC concentration documented by Chen et al. (2010). The Midwest and South had bank exposure ratios (bank-years with VC revenue per VC fund raised) of 2.44 and 2.11 respectively, versus 0.84 for the Northeast and 0.57 for the West (Figure 2 Panel A, p. 2168; Table I, p. 2166).

**Causal chain.** If bank LPs are locally biased and the Volcker Rule removes bank LPs disproportionately from non-hub states, then: (1) local VC supply falls more in those states; (2) startups there receive less and cheaper-priced capital; (3) startups facing local VC shortfalls migrate to where VC is available. The approach is analogous to Kortum and Lerner (2000), who assess VC contributions to innovation using supply-side variation, and Gonzalez-Uribe (2020), who uses LP supply shocks to trace VC effects. The migration channel resolves the ex ante ambiguity: VCs could conceivably substitute distant LPs, or nonlocal VCs could fill the gap. The results rule both out, attributing the failure to information asymmetry (a 10% increase in distance between an out-of-state VC and a startup is associated with a 0.5% higher likelihood of requiring a local co-investor; Table XII Panel A, p. 2193). The changes in startup valuations mirror findings in Gompers and Lerner (2000), who show that VC inflows create demand pressure and drive valuation changes.

The paper extends Samila and Sorenson (2011), who instrument VC supply with endowment LP returns at the MSA level; this paper adds a cleaner regional shock via the Volcker Rule.

**Identification assumption.** Parallel trends: high- and low-bank-exposure states evolved similarly in pre-Volcker VC activity (2010-2012). The dynamic estimation in Table IV (p. 2176) confirms pre-trend coefficients for Bank Expo x 2010, 2011, 2012 are all insignificant across outcome variables, with treatment effects emerging only from 2014 onward.

## Method

The primary estimator is a difference-in-differences regression (equation 1, p. 2170). The unit of analysis varies by outcome: state-year (VC fundraising aggregates), VC-fund level (fund size and follow-on), or startup level (financing and migration). The baseline specification is:

$$
Y_{it} = \beta_1 \, \text{Bank Expo}_i \times \text{Post}_t + \beta_2 X_i + \gamma_t + \epsilon_{it} \tag{1}
$$

where $$\text{Bank Expo}_i$$ is the state-level treatment variable measuring VCs' pre-Volcker reliance on banks as LPs (the ratio of aggregate bank-years with VC revenue to the number of VC funds raised in the state over 2001-2013); $$\text{Post}_t = 1$$ for 2014-2018 (the post-Volcker period); $$X_i$$ is a vector of entrepreneurial firm characteristics, state fixed effects, founding year fixed effects, and industry fixed effects; and $$\gamma_t$$ is year fixed effects. The main coefficient of interest is $$\beta_1$$.

The treatment variable is continuous, capturing cross-state variation richer than a binary High/Low split. It builds on `difference-in-differences` and `panel-regression`. Identification relies on the differential shock to LP capital across states: the Volcker Rule's scope for VC funds was unexpected (Congress did not intend to include VC funds), so pre-2014 bank LP distribution was not strategically adjusted in anticipation.

The paper also runs a within-VC-firm analysis (Panel C of Table III): a single-difference regression of whether a pre-Volcker VC firm raised a follow-on fund by year $$t \in \{2014, ..., 2018\}$$ on Bank Expo, controlling for the last pre-Volcker fund vintage year fixed effects.

## Empirical specifications

**VC fundraising (R1-R4).** State-year DiD with state and year fixed effects (Table III Panel A). Dependent variables: ln(1 + number of VC funds), ln(1 + total VC capital raised). State-year-level controls follow Gompers and Lerner (1998): GDP growth, log GDP per capita, house price growth, STEM employment growth. Errors clustered by state. Robustness: exclude California, narrow to 2011-2017, Poisson regression, IHS transformation.

**VC fund size (R3).** VC-fund-level DiD with VC firm fixed effects, vintage year fixed effects, and fund-sequence fixed effects (Table III Panel B). Dependent variable: ln(VC fund size). Errors clustered by state. Sample: 1,617 VC funds, 2010-2018.

**Startup financing (R5-R6).** Startup-year DiD with HQ state fixed effects, financing year fixed effects, founding year fixed effects, Series A or Seed fixed effects, and industry fixed effects (Table VI). Dependent variables: ln(capital raised in first VC round), ln(pre-money valuation), equity sold, ln(syndication size), indicator for pre-VC financing. Sample: 11,048 startups (5,903 for valuation). Errors clustered by startup HQ state.

**Startup migration (R7-R8).** Startup-year DiD at startup level (Table VIII). Dependent variables: dummy for moving HQ to CA (Panel A), to VC hubs CA/MA/NY (Panel B), or to non-VC-hub states (Panel C, placebo). Fixed effects: incorporation state, origin state, year, founding year, industry. Errors clustered by startup initial HQ state. Sample: 56,487 startup-year observations. All regression coefficients multiplied by 100.

$$
Y_{ist} = \beta_1 \, \text{Bank Expo}_s \times \text{Post}_t + \beta_2 X_{is} + \text{FE} + \epsilon_{ist}
$$

The triple-difference specifications (Tables IX-XI) add a third interaction (industry alignment, geographic distance, or VC financing constraints) to explore heterogeneity in migration responses. The geographic distance specification (Table X) finds distance does not explain migration choices post-shock; the VC-funding-constraint specifications (Table XI, Panels A-C) show biotech startups, older startups, and startups in high-VC-funded industries are more likely to migrate.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Call Reports (FFIEC) + FR Y-9Cs (BHC filings) | Construct bank VC revenue series 2001-2013; identify banking entities investing in VC; build treatment variable Bank Expo | [no page yet] |
| VentureSource (CB Insights / Dow Jones) | VC fund characteristics, startup financing rounds, startup HQ state over time; primary VC data 2010-2018 | [no page yet] |
| Pitchbook | VC fund and startup data (robustness checks); LP commitment information | [PitchBook](/wiki/licensed/pitchbook/) (licensed) |
| SEC EDGAR (Form D filings) | Identify startup migration via consecutive business-address changes 2002-2018; 56,487+ startup-year observations | [EDGAR](/wiki/datasets/edgar/) |
| Preqin | LP commitment data for robustness checks (LP home bias analysis, Table V) | [Preqin](/wiki/licensed/preqin/) (licensed) |

Sample: state-year panel covers 35 U.S. states, 2010-2018 (315 state-year observations). VC fund sample: 1,617 funds. Startup sample: 11,048 startups (first Seed or Series A round, $100M); 1,700 identified as having ever moved to a different state.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13451) if you are: studying causal drivers of startup geographic concentration; evaluating the regional impact of financial regulation (Dodd-Frank, Volcker Rule); interested in how LP capital constraints propagate through the VC intermediation chain to real activity; or building on the startup migration literature. The Internet Appendix contains additional robustness tests (Tables IA.I-IA.XIV), including placebo tests on banking sector outcomes, alternative treatment variable constructions, and the LP home-bias theoretical exercise. Replication data and code are at [https://github.com/michaelewens/Banks-In-VC](https://github.com/michaelewens/Banks-In-VC).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4), August 2025. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The paper is paywalled (Wiley VOR terms, not CC-licensed); only core results are extracted here.

> Chen, Jun, and Michael Ewens. "Venture Capital and Startup Agglomeration."
> *The Journal of Finance* 80, no. 4 (August 2025): 2153-2198.
> DOI: 10.1111/jofi.13451. © 2025 the American Finance Association.
> Extract-only: the Wiley VOR licence does not permit redistribution.
