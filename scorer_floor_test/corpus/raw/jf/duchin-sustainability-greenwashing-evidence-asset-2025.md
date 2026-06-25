---
title: "Sustainability or Greenwashing: Duchin, Gao & Xu (2025)"
description: >-
  Distilled: Firms divest pollutive plants in response to environmental
  pressures without any reduction in pollution levels, consistent with a
  greenwashing divestiture strategy. Sellers gain higher ESG ratings and lower
  EPA enforcement costs while buyers are firms with weaker environmental
  pressures and pre-existing business ties to the sellers. J. Finance 2025,
  CC BY 4.0. Nine core results with source locators, datasets used, the
  conceptual framework, and the empirical specifications.
sidebar:
  label: Duchin-Gao-Xu 2025
  order: 1
tags: [paper-summary, esg, greenwashing, environmental-finance, industrial-pollution,
       corporate-governance, divestitures, asset-pricing, panel-regression,
       difference-in-differences, event-study, text-as-data,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:wrds, data:edgar, data:epa-tri, data:kld, data:reprisk]
paper:
  authors: Ran Duchin, Janet Gao, Qiping Xu
  authorList:
    - { family: Duchin, given: Ran, orcid: "0000-0003-4996-6845", affiliation: Boston College, Carroll School of Management }
    - { family: Gao, given: Janet, orcid: "0000-0001-9960-7053", affiliation: Georgetown University, McDonough School of Business }
    - { family: Xu, given: Qiping, orcid: "0000-0003-2983-5100", affiliation: University of Illinois Urbana-Champaign, Gies College of Business }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 699-754
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13412
  jel:
    codes: [G34, G14, Q52]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Corporate Social Responsibility Reporting
    - Energy, Environment, Economic Growth
    - Housing Market and Economics
  dataAccess: licensed-commercial
  outcome:
    - likelihood of divesting pollutive plants
    - pollution levels at divested and buyer/seller plants
    - sellers' ESG ratings following divestitures
    - EPA enforcement actions and costs following divestitures
    - divestiture announcement CARs
    - buyer versus seller gains from trade
  outcomeClass: [firm-real-outcomes, firm-financing, social-welfare]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2024-12-30; corroborated by artifact p.699 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley OnlineLibrary, confirmed via Crossref DOI metadata 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 9
  citedByCount: 108

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, difference-in-differences, event-study, probit-regression, text-classification]
    identification: natural-experiment

  contributionType: [new-fact, measurement]

  mechanisms:
    - information-asymmetry
    - esg-reputation
    - agency

  scope:
    region: US
    assetClass: US industrial plants (EPA TRI pollutive establishments)
    period: 2000-01..2020-12
    frequency: annual
    dataType: [market, accounting, administrative, text]
    granularity: [firm, industry, transaction]
    n: "888 pollutive plant divestitures; 1,056,361 plant-chemical-year observations; 19,459 firm-year observations"

  findings:
    - ref: R1
      outcome: likelihood of divesting pollutive plants
      metric: pp-effect
      value: "1-SD increase in Pressure Index -> 0.6 pp higher divestiture likelihood (= 0.3 x 2.109); 32% relative to sample mean of 1.9 pp (Table III, col 5)"
      direction: positive
      vsBenchmark: "54% relative magnitude for Pressure Index vs sample mean (Table II, col 1)"
    - ref: R2
      outcome: likelihood of divesting pollutive plants
      metric: pp-effect
      value: "Interquartile increase in total toxic release raises sensitivity of divestitures to Pressure Index by 7.7 (= 2.569 x 3), -> 2.3 pp higher divestiture likelihood (Table III Panel B, col 2)"
      direction: positive
    - ref: R3
      outcome: likelihood of divesting pollutive plants
      metric: coefficient
      value: "Environmental Event coefficient = 1.077** (SE 0.542), Table IV col 2; 1.1 pp increase in divestiture probability; no pre-trends in Figure 2"
      direction: positive
    - ref: R4
      outcome: pollution levels at divested and buyer/seller plants
      metric: coefficient
      value: "Divested x Post coefficients statistically indistinguishable from zero across all 8 specifications in Table VI Panels A and B; GDID and stacked DID; Total Pollution and Pollution Intensity"
      direction: none
      vsBenchmark: "Null result: no pollution decline at sold plants or combined buyer-seller portfolio"
    - ref: R5
      outcome: sellers' ESG ratings following divestitures
      metric: coefficient
      value: "Seller (Pollutive) x Post: CSR Score +0.302* (Table XI, Panel A col 2); Environmental Score +0.234*** (col 6); env score increase = 160% of sample mean of 0.16"
      direction: positive
    - ref: R6
      outcome: EPA enforcement actions and costs following divestitures
      metric: pp-effect
      value: "Enforcement Action: -5 pp (Table XI Panel B col 3), vs sample mean 7 pp; Enforcement Cost falls to ~3.6% of original level (e^-3.33 ~ 0.036)"
      direction: negative
    - ref: R7
      outcome: divestiture announcement CARs
      metric: car
      value: "Interquartile increase in pollution -> 3 to 4 pp higher CAR[-1,+1]; sample average CAR = 2.5 pp (Table XII, all cols significant at 5%)"
      direction: positive
    - ref: R8
      outcome: buyer versus seller gains from trade
      metric: level
      value: "Top-pollution-quartile divestitures: buyers earn ~$400M higher value gains than sellers (market model, Figure 6 Panels A-B)"
      direction: positive
      vsBenchmark: "Buyers earn more for more pollutive plants; sellers earn more for least pollutive plants (~$600-700M higher)"
    - ref: R9
      outcome: likelihood of divesting pollutive plants
      metric: coefficient
      value: "Pressure Index x Info. Asymmetry: positive and significant across all 5 proxies in Table VIII (e.g., #Segments 0.823**, #Industries 2.102**, #Subsidiaries 0.018*, #Layers 1.773**, %Blockholders -5.610*)"
      direction: positive
      vsBenchmark: "Effect absent for divestitures of nonpollutive assets (Table XIV)"

  resultType: new-finding

  relatesTo:
    - { cite: "Broccardo, Hart & Zingales (2022)", doi: '10.1086/720516', relation: builds-on, note: "framework on divestment by socially responsible investors as motivation for green-pressure mechanisms" }
    - { cite: "Hartzmark & Sussman (2019)", doi: '10.1111/jofi.12841', relation: builds-on, note: "evidence that investor ESG preferences generate real responses by firms" }
    - { cite: "Starks, Venkat & Zhu (2017)", doi: '10.2139/ssrn.3049943', relation: builds-on, note: "pension fund ESG preferences and their effect on firm behavior" }
    - { cite: "Hart & Zingales (2017)", doi: '10.1561/108.00000022', relation: builds-on, note: "firms should maximize shareholder welfare, not market value - motivates prosocial pressure framework" }
    - { cite: "Coase (1937)", doi: '10.1111/j.1468-0335.1937.tb00002.x', relation: builds-on, note: "Coasean framework for variation in environmental costs inducing reallocation of pollutive assets across firm boundaries" }
    - { cite: "Jovanovic & Braguinsky (2004)", doi: '10.1257/000282804322970698', relation: builds-on, note: "real-asset-market model implying market clears by transferring pollutive assets from high- to low-pressure firms" }
    - { cite: "Gormley & Matsa (2011)", relation: builds-on, note: "corporate responses to liability risk as precedent for response-to-environmental-pressure framework" }

  openQuestions:
    - "Whether the growing trend of pollutive asset divestitures in recent years will eventually generate long-term pollution reductions that cannot yet be observed within the 2000-2020 sample window (p. 748)."
    - "The relative importance of the several non-mutually exclusive channels generating gains from pollutive asset trades: regulatory cost reduction, information-acquisition cost reduction, and reallocation across ESG-preference heterogeneous investors (p. 749)."
    - "Whether the scope-3 toxic emissions loophole exploited by greenwashing divestitures along supply chains will be closed by future regulatory or rating-agency reforms (p. 749)."

  replicationCode:
    status: available

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 699-754, all tables and figures). Nine results extracted from the PDF. Not human-verified. Not reproduced. Replication code referenced in the paper (Supporting Information) but not run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (Tables II-VI, VIII-XII, Figure 6); three fixes applied: CSR Score significance corrected from ** to * (Table XI Panel A col 2) in R5 findings, core-results table, and empirical-specs section; introducesData removed (paper merges existing sources, no new source introduced); contributionType new-data removed for same reason."

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13412
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2024-12-30"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the conceptual framework it builds on (Coasean real-asset-market equilibrium with heterogeneous environmental pressures), and the empirical strategy (multilogit, DID Poisson, stacked DID, BERT text analysis, event-study CARs): enough to know what it found and how, without reading all 56 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13412).

## TL;DR

The paper studies the market for pollutive industrial plants. Using 888 divestitures of EPA Toxic Release Inventory (TRI) plants from 2000 to 2020, the authors show that: (i) firms facing stronger environmental pressures (ESG ratings, pension fund holdings, Democratic-leaning counties, RepRisk incidents) are significantly more likely to divest pollutive plants; (ii) buyers face weaker environmental pressures and have preexisting supply-chain or joint-venture ties with sellers; (iii) despite these transfers, pollution levels do not decline at sold plants or across the combined buyer-seller portfolio; (iv) sellers gain substantially in ESG ratings, EPA enforcement cost reductions, and announcement returns, while disclosing improved environmental performance in conference calls; and (v) buyers capture higher gains in the most pollutive deals. The evidence is consistent with a greenwashing strategy: firms exploit information frictions to cosmetically redraw firm boundaries along their value chains without achieving real environmental improvements.

## Core results

Magnitudes and significance are as reported; `\*\*`/`\*\*\*` = 5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Environmental pressures increase the propensity to divest pollutive plants; divestiture is the dominant response relative to closure or abatement | Table III Panel A, p. 717; Table II, p. 715 | Pressure Index: 0.6 pp higher divestiture likelihood per 1-SD (32% relative); ESG rating (Rated): 1.2 pp more likely to divest; Env. Event: +141% relative magnitude vs. other responses |
| R2 | Pollution levels amplify the sensitivity: heavier polluters are significantly more likely to divest in response to environmental pressures | Table III Panel B, p. 717 | Interquartile rise in total toxic release raises sensitivity of divestitures to Pressure Index by 7.7 (= 2.569 x 3), implying 2.3 pp higher divestiture likelihood per 1-SD increase in Pressure Index |
| R3 | Quasi-exogenous RepRisk environmental incidents sharply increase divestiture likelihood without pretrends | Table IV, p. 719; Figure 2, p. 720 | Env. Event coefficient = 1.077\*\* (SE 0.542); probability of divesting rises by ~1.5 pp immediately after incident (Figure 2); social/governance events have no effect |
| R4 | Pollution does not decline at divested plants or across the combined buyer-seller portfolio following divestitures | Table VI Panels A-B, pp. 723-724; Figures 3-4, pp. 725-726 | All Divested x Post coefficients statistically indistinguishable from zero; result holds in GDID and stacked regressions, for total pollution and intensity, with and without state/industry-year FE |
| R5 | Sellers' ESG and environmental ratings increase substantially following divestitures | Table XI Panel A, p. 738 | CSR Score: +0.302\* (GDID); Environmental Score: +0.234\*\*\* (GDID, stacked); environmental score gain = ~160% of sample mean |
| R6 | EPA enforcement actions and compliance costs decline sharply for sellers following divestitures | Table XI Panel B, pp. 738-739 | Enforcement action probability: -5 pp (vs. sample mean 7 pp); average enforcement costs fall to ~3.6% of pre-divestiture level (e^-3.33) |
| R7 | Announcement CARs are higher for divestitures of more pollutive plants, consistent with market recognition of gains from offloading pollution | Table XII, p. 742 | Interquartile increase in pollution -> 3 to 4 pp higher CAR[-1,+1]; sample average CAR = 2.5 pp; results hold for market and FF benchmarks |
| R8 | In the most pollutive deals, buyers capture ~$400M more value than sellers; pattern reverses for least pollutive deals | Figure 6, p. 744 | Top-pollution-quartile divestitures: buyers earn ~$400M higher gains (market model); bottom-quartile: sellers earn $600-700M more than buyers; consistent with comparative advantage in operating pollutive assets |
| R9 | More opaque firms (higher information asymmetry) are more likely to divest pollutive plants in response to environmental pressures | Table VIII, p. 731 | Pressure Index x #Segments: 0.823\*\*; x #Industries: 2.102\*\*; x #Subsidiaries: 0.018\*; x #Layers: 1.773\*\*; x %Blockholders: -5.610\*; all significant at 10% or better |

**Overall (paper's conclusion).** The real asset market allows firms to respond to environmental pressures by divesting pollutive plants along their supply chains, thereby improving ESG ratings and reducing regulatory compliance costs without losing access to the assets and without reducing overall pollution. These findings are more consistent with a greenwashing strategy than with genuine environmental improvement: ESG rating agencies, environmental regulators, and prosocial investors fail to recognize that divestitures of pollutive assets are ineffective conduits for reducing industrial pollution.

## Theory / model

The paper has no formal mathematical model. It develops a conceptual framework built on the Coase (1937) insight that variation in environmental costs across firms will induce some firms to sell and others to buy pollutive assets. The key predictions come from three premises:

1. Firms that face stronger environmental pressures (from investors, regulators, or the public) find it optimal to divest pollutive assets; firms that face weaker pressures find it optimal to hold or acquire them. Environmental pressures stem from prosocial preferences of stakeholders: Hart and Zingales (2017) argue firms should maximize shareholder welfare, Hartzmark and Sussman (2019) show investor ESG preferences generate real firm responses, Starks, Venkat, and Zhu (2017) document the role of pension funds in pressing firms on ESG, and Broccardo, Hart, and Zingales (2022) model how prosocial investors use divestment as a mechanism. In a real-asset-market equilibrium following Jovanovic and Braguinsky (2004), the market clears by transferring pollutive assets from high-pressure to low-pressure firms.

2. Information asymmetry is a prerequisite for greenwashing. Corporate managers can exploit information frictions - outsiders' difficulty monitoring firm-level environmental performance - to divest pollutive assets cosmetically along supply chains that maintain their access to the divested assets, without actual abatement. Following Demsetz and Lehn (1985) and Duchin, Matsusaka, and Ozbas (2010), more complex ownership and organizational structures raise the information costs outsiders incur, making greenwashing divestiture more feasible (and therefore more prevalent) in such firms. Gormley and Matsa (2011) provide a precedent for firms responding to external liability risk by restructuring asset ownership.

3. Business ties (supply chain relations and joint ventures) between buyers and sellers lower counterparty risk and information asymmetry, making it rational for sellers to divest to connected buyers who can return the plant's output to the seller at lower cost. This predicts that connected firms are more likely to be buyers and that the likelihood of selling to a connected buyer increases when that buyer faces weaker environmental pressures (Table IX Panel B, p. 733).

**Identification strategy.** The primary concern is that environmental pressures are correlated with omitted firm characteristics. The paper's main causal design exploits quasi-exogenous variation from RepRisk environmental risk incidents, arguing that firms cannot fully control the annual timing of such incidents (Table IV, Figure 2). The resulting within-firm, time-series estimates confirm no pretrends and an immediate divestiture response. Pollution analyses use generalized DID (Poisson with plant-chemical FE + chemical-year FE) and stacked DID that matches each divested plant to never-divested plants in the same NAICS3 industry and state, saturating regressions with cohort-interactive FEs to address heterogeneous treatment-timing bias.

## Method

The paper applies four estimating methods:

**Multilogit for firm responses (R1).** The firm chooses among four mutually exclusive responses to environmental pressure: divestiture, plant closure, enhanced abatement, or no action. Marginal effects of each environmental pressure measure are reported, scaled by the sample mean of each outcome to produce the "Rel. Magnitude" statistic (Table II, p. 715).

**Linear probability and Poisson panel regressions for divestiture determinants (R1-R3, R9).** The baseline seller-side regression (equation 1, p. 716) is:

$$
\text{Divest}_{i,t} = \beta \, \text{Pressure}_{i,t} + \phi_{j,t} + \epsilon_{i,t} \tag{1}
$$

where $$i$$ is a publicly listed TRI-plant-owning firm, $$j$$ denotes the industry, $$t$$ the year, and $$\phi_{j,t}$$ are industry-year fixed effects. The dependent variable equals 100 if firm $$i$$ sells at least one TRI plant in year $$t$$. Standard errors are clustered by firm. Pollution-level interactions, information-asymmetry interactions, and connected-firm pressure interactions follow the same structure with additional firm fixed effects where noted.

**Generalized DID and stacked regressions for pollution changes (R4).** The plant-chemical-year DiD specification (equation 2, p. 722) is:

$$
\text{Pollution}_{i,c,t} = \beta \, \text{Divested}_i \times \text{Post}_{i,t} + \alpha_{i,c} + \tau_{c,t} + \epsilon_{i,c,t} \tag{2}
$$

where $$i$$ is the plant, $$c$$ the chemical type, $$\alpha_{i,c}$$ are plant-chemical fixed effects, and $$\tau_{c,t}$$ are chemical-year fixed effects. Poisson regressions handle skewness. Stacked regressions match each divested plant to never-divested controls in the same NAICS3-state cell, saturating with cohort-plant-chemical, cohort-chemical-year, cohort-state-year, and cohort-industry-year interactive FEs to address heterogeneous treatment-timing (De Chaisemartin and d'Haultfoeuille (2020), Sun and Abraham (2021)). A dynamic version (equation 3, p. 723) decomposes $$\text{Post}_{i,t}$$ into annual event-time dummies from $$k \geq -3$$.

**BERT text classification for conference call analysis (R5-R6 mechanism, Section IV.C).** A BERT NLP model (Devlin et al. (2019)) is trained on 1,000 manually classified sentences from conference calls using a SASB environmental keyword dictionary. The model classifies each sentence-group containing environmental keywords as expressing positive or negative environmental sentiment. The DID specification (equation 4, p. 734) regresses positive/negative disclosure indicators on $$\text{Seller(Pollutive)}_f \times \text{Post}_{f,t}$$ with firm and year FEs.

**Event-study CARs (R7-R8).** Cumulative abnormal returns are measured in a three-day window $$\text{CAR}[-1,+1]$$ relative to the market model and the Fama-French three-factor model. Buyer gains minus seller gains are computed as the product of each firm's market capitalization and its $$\text{CAR}[-1,+1]$$.

## Empirical specifications

The paper's headline empirical tests are:

**Multilogit (Table II, p. 715; R1).** Sample: all public TRI-plant-owning firms, 12,764 obs. Firm Char controls include Tobin's Q, Leverage, Cash Holdings, Tangibility. Industry-year FEs. Robust SE. Pseudo-R² = 0.017-0.026 across pressure measures.

**Seller propensity regressions (Table III, p. 717; R1-R2).** Sample: Panel A, 11,295-18,826 firm-years; Panel B, 11,742-12,084 firm-years. Industry-year FEs; firm characteristics. SE clustered by firm. R² = 0.056-0.079. The key result: Pressure Index coefficient = 2.110\*\*\* (SE 0.593) in Panel A; Pressure Index x Pollution (interquartile quantity) = 2.568\*\*\* (SE 0.615) in Panel B.

**Within-firm divestiture response to RepRisk incidents (Table IV, p. 719; R3).** Sample: 11,243-11,629 firm-years. Firm FE + Year FE + Industry-Year FE. SE clustered by firm. Environmental Event coefficient = 1.074\*-1.133\*\* (SE 0.615-0.544); social and governance events insignificant.

**Buyer vs. seller environmental pressure comparison (Table V, p. 721).** Deal-level regression; 968-1,776 observations. Buyer indicator is negative and significant for all environmental pressure measures: Public -0.055\*\*, Rated -0.047\*\*, Democratic HQ -0.054\*\*, Env. Event -0.052\*\*, Pressure Index -0.059\*\*\*.

**Pollution DiD (Table VI, p. 723-724; R4).** Sample: Panel A, 992,313-3,994,695 plant-chemical-years; Panel B, 872,163-9,431,650 plant-chemical-years. Plant-chemical FE + chemical-year FE + state-year FE + industry-year FE. All Divested x Post estimates insignificant; power analysis shows specifications can detect effects of 2-3% of sample SD (Internet Appendix Table IA.II).

**Conference call disclosure DiD (Table X, p. 735; R5 mechanism).** Sample: 33,873-237,867 firm-year conference calls. Firm FE + Year FE + Industry-Year FE. Seller(Pollutive) x Post: Positive Env. Disclosure = 0.062\*\* (stacked, SE 0.031), ~5.6 pp or 47% of sample mean (12 pp). Negative disclosure: insignificant.

**ESG ratings and enforcement costs DiD (Table XI, p. 738-739; R5-R6).** Panel A (ESG): 29,273-133,621 obs; CSR Score +0.302\* (GDID), +0.941\* (stacked); Env. Score +0.234\*\*\* (GDID), +0.245\*\*\* (stacked). Panel B (Enforcement): 5,495-129,439 obs; Enforcement Action -0.048\*\*\* to -0.073\*\*\*; Enforcement Cost (Poisson) -2.708\*\*\* to -4.376\*\*\*.

**Announcement CARs (Table XII, p. 742; R7).** Sample: 246-278 deal-level observations (public sellers). Past Pollution (Quartile) coefficient = 0.010\*\*-0.013\*\* across all four specifications. R² = 0.307-0.429.

**Business ties (Table IX, p. 733; R9 mechanism).** Panel A: Operationally Related coefficient = 0.651\*\*\* (SE 0.099) in matched-pair regression; Buyer of Pollutive Assets coefficient = 0.069\*\*\* in new-relationship regression. Panel B: Pressure Index, Connected Firms' Min = -0.007\* to -0.009\*\*.

**Nonpollutive asset placebo (Table XIV, p. 746).** All headline effects are absent for divestitures of nonpollutive assets across all five panels, confirming that findings are specific to pollutive divestiture and not generic divestiture effects.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| EPA Toxic Release Inventory (TRI) | Plant-chemical-level toxic emissions (total pollution, pollution intensity, abatement activities); 2000-2020; 1,056,361 plant-chemical-year obs | [EPA TRI](/wiki/datasets/epa-tri/) |
| SDC Mergers and Acquisitions database | Divestitures and spin-offs of industrial plants; 888 pollutive deals 2000-2020 | [no page yet] |
| KLD / MSCI ESG database | ESG ratings (CSR Score, Environmental Score); coverage of public U.S. firms | [WRDS](/wiki/licensed/wrds/) (licensed) |
| RepRisk ESG Business Intelligence | Environmental, social, governance risk incidents; starting 2007 | [RepRisk](/wiki/licensed/reprisk/) (licensed) |
| MIT Election Data and Science Lab | County-level presidential vote share for Democratic HQ classification | [no page yet] |
| Thomson Reuters Street Events (SE) | Conference call transcripts; management presentations; starting 2001 | [no page yet] |
| EPA Enforcement and Compliance History Online (ECHO) | EPA enforcement actions and compliance costs | [no page yet] |
| Compustat (WRDS) | Firm financials (Q, Leverage, Cash Holdings, Tangibility); segment data; ownership structure | [WRDS](/wiki/licensed/wrds/) (licensed) |
| CRSP (WRDS) | Equity returns for announcement CARs and market capitalization | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Factset / Compustat Segment | Supply chain relationships | [WRDS](/wiki/licensed/wrds/) (licensed) |
| Orbis | Subsidiary and organizational layer data | [no page yet] |
| 13-F filings (SEC) | Institutional investor holdings (pension funds, blockholders) | [EDGAR](/wiki/datasets/edgar/) |

Sample period: 2000-2020 (annual). Plant-chemical-year sample: 1,056,361 observations. Firm-year sample: 19,459 observations.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13412) if you are: (i) studying whether environmental divestitures by public firms reduce actual pollution or are primarily cosmetic; (ii) investigating the role of ESG ratings and regulatory enforcement in incentivizing greenwashing; (iii) analyzing real-asset-market equilibria with heterogeneous environmental preferences; (iv) replicating the BERT-based conference call text analysis; or (v) studying gains from trade in pollutive-asset divestitures and the role of buyer-seller business ties. The Internet Appendix contains detailed matching procedures (Section I.B), minimum detectable effect estimates (Table IA.II), and numerous robustness tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Duchin, Ran, Janet Gao, and Qiping Xu.
> "Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution."
> *The Journal of Finance* 80, no. 2 (April 2025): 699-754.
> DOI: 10.1111/jofi.13412. © 2024 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
