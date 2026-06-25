---
title: "Build or Buy? Human Capital and Corporate Diversification: Beaumont, Hebert & Lyonnet (2025)"
description: >-
  Distilled: Using French administrative data, this paper shows that firms enter distant sectors
  by acquisition (buy) rather than organically (build) because building human capital in distant
  sectors requires costly organizational integration of new workers. Review of Financial Studies
  2025, CC BY 4.0. Seven core results with source locators, datasets used, the identification
  design (shift-share IV), and the estimating equations.
sidebar:
  label: Beaumont-Hebert-Lyonnet 2025
  order: 1
tags: [paper-summary, corporate-diversification, human-capital, mergers-acquisitions,
       organizational-economics, panel-regression, instrument, peer-reviewed, unreplicated,
       data:sdc-platinum, data:insee-dads, data:insee-lifi, data:insee-tax-files,
       data:bureau-van-dijk-zephyr]
paper:
  authors: Paul Beaumont, Camille Hebert, Victor Lyonnet
  authorList:
    - { family: Beaumont, given: Paul, orcid: "0000-0001-8065-3260", affiliation: McGill University }
    - { family: Hebert, given: Camille, affiliation: University of Toronto }
    - { family: Lyonnet, given: Victor, orcid: "0009-0005-4572-1586", affiliation: University of Michigan }
  year: 2025
  venue: The Review of Financial Studies 38(5), 2025, 1333–1367
  venueShort: Rev. Fin. Stud. 2025
  doi: 10.1093/rfs/hhaf004
  jel:
    codes: [L25, J24, J30, G34]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Firm Innovation and Growth", "Entrepreneurship Studies and Influences"]
  dataAccess: proprietary-confidential
  outcome:
    - probability of acquiring (buy) vs organic entry (build) into a new sector
    - post-entry employment growth in new sector
    - post-entry sales performance in new sector
    - investment in organizational skills around diversification
  outcomeClass: [firm-real-outcomes, firm-dynamics]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL https://creativecommons.org/licenses/by/4.0/, delay-in-days 90,
    start 2025-04-21)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF via Oxford Academic (confirmed 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 5
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, instrumental-variables, event-study, difference-in-differences]
    identification: instrument
  contributionType: [new-fact, new-data, measurement]
  mechanisms: [organizational-complexity, participation-frictions]
  introducesData: true
  scope:
    region: France
    assetClass: private firms (all sectors except financial, agricultural, public)
    period: 2003-01..2014-12
    frequency: annual
    dataType: [administrative, accounting, market]
    granularity: [firm, individual]
    n: "61,228 firm-sector-year entries in regression sample (full dataset: 127,185 build + 2,415 buy = 129,600 over 2003-2014)"
  findings:
    - ref: R1
      outcome: probability of acquiring (buy) vs organic entry (build) into a new sector
      metric: pp-effect
      value: "0.39 pp per 1-SD increase in HC distance (col. 1, Table 3); equal to ~20% of unconditional buy probability; significant at 5%"
      direction: positive
      vsBenchmark: OLS baseline with sector-of-origin x entry x year FE
    - ref: R2
      outcome: probability of acquiring (buy) vs organic entry (build) into a new sector
      metric: pp-effect
      value: "0.26 pp per 1-SD increase in HC Bartik (col. 1, Table 4); ~13% of unconditional buy probability; significant at 5%"
      direction: positive
      vsBenchmark: shift-share IV (HC Bartik) causal estimate; consistent with OLS
    - ref: R3
      outcome: post-entry employment growth in new sector
      metric: coefficient
      value: >-
        Build firms: +0.532*** top-5-occupation employment growth per 1-SD HC distance (Table 5 Panel A, col. 2);
        Buy firms: +0.045 (insignificant, Table 5 Panel B, col. 2);
        difference significant at 1%
      direction: positive
      vsBenchmark: build vs buy difference in top-5-occupation employment response to HC distance
    - ref: R4
      outcome: post-entry employment growth in new sector
      metric: pp-effect
      value: >-
        Build firms hire 0.5 pp more from external labor markets per 1-SD HC distance
        (Table 6 Panel A, col. 3, significant at 5%);
        Buy firms hire 4.7 pp fewer externally per 1-SD HC distance
        (Table 6 Panel B, col. 3, significant at 5%); difference at 1%
      direction: mixed
      vsBenchmark: external vs internal labor market hires around entry
    - ref: R5
      outcome: probability of acquiring (buy) vs organic entry (build) into a new sector
      metric: pp-effect
      value: "HC distance effect significant only for firms with low organizational skills (Table 8): low top-layers coef = 0.013*** vs high = 0.018 (insignificant); low SG&A coef = 0.012*** vs high = 0.025 (insignificant)"
      direction: positive
      vsBenchmark: subsample by organizational skill tercile; effect concentrated in low-skill firms
    - ref: R6
      outcome: investment in organizational skills around diversification
      metric: pp-effect
      value: >-
        Build firms: +6.6 pp increase in SG&A wage share per 1-SD HC distance
        (Table 9 col. 1, significant at 1%); +0.369 pp top-layers share (col. 3, sig. at 1%);
        Buy firms: no significant investment in org skills (cols. 2, 4)
      direction: positive
      vsBenchmark: build vs buy; difference significant at 1%
    - ref: R7
      outcome: post-entry sales performance in new sector
      metric: coefficient
      value: >-
        Build firms: coef -1.160*** on HC distance in log(Sales) (Table 11 Panel A, col. 1; ~23% lower sales per 1-SD HC distance);
        sales growth -0.217*** (col. 2); survival rate -0.166*** (col. 3);
        Buy firms: no significant effect (Panel B); build vs buy difference significant at 1%
      direction: negative
      vsBenchmark: build firms underperform for at least 3 years; buy firms unaffected by HC distance
  resultType: new-finding
  relatesTo:
    - { cite: "Hoberg and Phillips (2018)", doi: '10.1287/mnsc.2016.2693', relation: builds-on, note: "prior evidence on human capital as determinant of which sector firms enter (product language similarity)" }
    - { cite: "Boehm, Dhingra, and Morrow (2022)", relation: builds-on, note: "comparative advantage framework for firm diversification and resource requirements" }
    - { cite: "Tate and Yang (2024)", doi: '10.1093/rfs/hhad056', relation: builds-on, note: "human factor in acquisitions and cross-industry labor mobility" }
    - { cite: "Neffke and Henning (2013)", relation: builds-on, note: "skill relatedness and firm diversification; sector-level HC overlap" }
    - { cite: "Ouimet and Zarutskie (2020)", doi: '10.1142/s2010139220500111', relation: cites, note: "acquiring labor as motive for M&A; firms buy to obtain human capital they cannot build" }
    - { cite: "Prescott and Visscher (1980)", doi: '10.1086/260879', relation: builds-on, note: "organizational capital as the cost of integrating new workers; foundational motivation for integration cost channel" }
    - { cite: "Lazear (2009)", doi: '10.1086/648671', relation: builds-on, note: "skill-weights approach defining firm human capital as combination of occupation-specific skills" }
    - { cite: "Goldsmith-Pinkham, Sorkin, and Swift (2020)", doi: '10.1257/aer.20181047', relation: cites, note: "Bartik instrument methodology; paper follows Borusyak-Hull-Jaravel shock-based identification instead" }
    - { cite: "Borusyak, Hull, and Jaravel (2022)", relation: builds-on, note: "quasi-experimental shift-share research design used for HC Bartik instrument" }
  openQuestions:
    - "Whether the build-or-buy HC distance mechanism generalizes beyond France to other institutional settings with different labor market flexibility and firm-size distributions (p. 1364)."
    - "The role of target firms' organizational skills (as distinct from acquirer skills) in post-merger integration success, which the paper's sample of diversified acquisitions does not fully address (p. 1363, fn. 30)."
    - "Whether the effect of organizational skills on the build-or-buy decision holds for large firms, which the paper finds drive the relationship primarily through small firms (p. 1360)."
  replicationCode:
    url: "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GL9BIM"
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 1333-1367); seven results extracted from Tables 3-12 and figures. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core-results rows confirmed against Tables 3-12. Fixed: JEL codes (added missing J30); R3 finding corrected from col. 1 total employment to col. 2 top-5-occupation result matching the core-results table locator; R7 finding clarified to show raw coefficient vs per-SD effect (~23% lower sales per 1-SD HC distance); outcomeClass replaced firm-financing with firm-dynamics (paper studies entry modes, not capital structure); mechanisms replaced agency/financial-constraint with organizational-complexity/participation-frictions (paper's channel is integration cost of new workers); scope.n corrected to distinguish regression sample (61,228) from full dataset (127,185 build + 2,415 buy). Equations 1-3 and HC distance formula verified term-by-term against PDF."
  licenceVerification:
    - source: "Crossref REST API works/10.1093/rfs/hhaf004"
      checked: 2026-06-06
      by: "paper-distiller (claude-sonnet-4-6)"
      found: "license[].content-version=vor, URL=https://creativecommons.org/licenses/by/4.0/, delay-in-days=90, start=2025-04-21"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the human capital distance measure it introduces, and the
causal identification design (shift-share IV): enough to know what it found and how, without reading
all 35 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1093/rfs/hhaf004).

## TL;DR

Using exhaustive French administrative data on all firms entering new sectors from 2003 to 2014,
the paper shows that firms acquire incumbents (buy) rather than develop resources organically
(build) when their existing human capital is far from the target sector. The key friction is
integration cost: building human capital requires not just hiring workers with the right skills
but also investing organizational capacity to train, manage, and assign them to tasks. Firms with
limited organizational skills face particularly high build costs and are the primary drivers of the
result. Post-entry, firms that build in distant sectors underperform for at least three years;
firms that buy are unaffected by the human capital distance to the entry sector, consistent with
acquiring already-operational human capital that avoids integration costs.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point
into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | HC distance between a firm and the entry sector is positively associated with the probability of buying (OLS) | Table 3, col. 1, p. 1345 | +0.39 pp per 1-SD increase in HC distance; ~20% of the unconditional buy probability; sig. at 5% |
| R2 | HC Bartik instrument confirms causal effect of HC distance on buy probability | Table 4, col. 1, p. 1350 | +0.26 pp per 1-SD HC Bartik; ~13% of unconditional buy probability; sig. at 5% |
| R3 | Firms that build hire more workers in entry-sector occupations; firms that buy downsize non-key occupations | Table 5, Panel A col. 2 and Panel B col. 2, p. 1352 | Build: +0.532\*\*\* in top-5 occupations per 1-SD HC distance; Buy: 0.045 (insignificant); difference sig. at 1% |
| R4 | Build firms hire from external labor markets; buy firms do not assimilate target workforce | Table 6, col. 3, p. 1354 | Build: +0.5 pp external hires per 1-SD HC distance (sig. at 5%); Buy: -4.7 pp; difference sig. at 1% |
| R5 | The build-or-buy HC distance effect is driven by firms with low organizational skills | Table 8, p. 1357 | Low top-layers: coef = 0.013\*\*\*; high top-layers: coef = 0.018 (insig.); similarly for SG&A and HR presence |
| R6 | Firms that build in distant sectors invest more in organizational skills; buy firms do not | Table 9, col. 1 and col. 3, p. 1358 | Build: +6.6 pp SG&A wage share (sig. at 1%), +0.369 pp top-layers share (sig. at 1%) per 1-SD HC distance; Buy: insig. |
| R7 | Build firms in distant sectors underperform for at least 3 years post-entry; buy firms are unaffected by HC distance | Table 11, Panel A col. 1, p. 1362 | Build: coef -1.160\*\*\* on HC distance in log(Sales) (~23% lower per 1-SD); Buy: +0.037 (insig.); survival rate build -0.166\*\*\*; difference in sales sig. at 1% |

**Overall (paper's conclusion).** Firms buy primarily when they cannot build: 98% of diversifying
entries are organic (build), and buy entries are concentrated in distant sectors. Building human
capital is costly because it requires organizational skills to integrate new workers, not just the
right hires. Firms that buy avoid these costs and reach profitability faster in new sectors.
Organizational skills are therefore non-rival: they allow firms to profitably enter multiple
sectors.

## Theory / model

The paper has no formal theoretical model but builds on two testable hypotheses derived from the
organizational economics literature (Prescott and Visscher (1980)). The framing of human capital
as a combination of occupation-specific skills follows Lazear (2009). The diversification
direction literature finds firms enter sectors requiring similar resources (Neffke and Henning (2013);
Hoberg and Phillips (2018); Boehm, Dhingra, and Morrow (2022); Tate and Yang (2024)).
The M&A motive of acquiring human capital is developed by Ouimet and Zarutskie (2020).

**Hypothesis 1 (build vs buy):** If building human capital requires integrating new workers
(training, managing, assigning to tasks), the cost of building increases with the level of
required human capital investment, proxied by HC distance to the entry sector. Therefore, firms
should be more likely to buy in distant sectors and more likely to build in close sectors.

**Hypothesis 2 (organizational skills):** Firms with limited organizational skills face higher
integration costs, so the HC distance effect on buy probability should be stronger for
low-organizational-skill firms. Moreover, firms that build in distant sectors should invest more
in organizational skills to reduce integration costs.

The paper defines the HC distance between firm $$g$$ and sector $$n$$ as one minus the cosine
similarity between the firm's occupation wage-share vector and the incumbent representative firm's
occupation wage-share vector (pp. 1340-1341):

$$
\text{HC distance}_{g,n} = 1 - \frac{\sum_i s_{g,i} \cdot s_{n,i}}{\sqrt{\sum_i s_{g,i}^2} \sqrt{\sum_i s_{n,i}^2}}, \tag{--}
$$

where $$s_{g,i}$$ is the share of firm $$g$$'s wage bill going to workers in occupation $$i$$, and
$$s_{n,i}$$ is the share of the sector $$n$$ wage bill in occupation $$i$$, computed by consolidating
all single-sector firms in the sector. HC distance ranges from 0 (identical workforce composition)
to 1 (no overlapping occupations). The paper uses 414 four-digit PCS-ESE occupation codes from
the French matched employer-employee data set (DADS, p. 1340).

## Method

The primary empirical tool is an OLS linear probability model of the build-or-buy decision, with
the shift-share IV (HC Bartik) used to establish causality. The paper exploits the richness of
the French employer-employee data to construct firm-level occupation vectors unavailable in
standard M&A databases.

**OLS baseline** (eq. 1, p. 1344). The main specification compares firms in the same sector of
origin that enter the same new sector in the same year:

$$
\mathbf{1}(\text{Buy})_{g,n,t} = \lambda_{n,o,t} + \delta \cdot \text{HC distance}_{g,n,t-1} + \beta X_{g,n,t-1} + \varepsilon_{g,n,t}, \tag{1}
$$

where $$\mathbf{1}(\text{Buy})_{g,n,t}$$ is one if firm $$g$$ acquires an incumbent in sector $$n$$ at
year $$t$$ and zero if it builds. The fixed effects $$\lambda_{n,o,t}$$ are sector of origin $$o$$
times entry sector $$n$$ times year $$t$$ fixed effects, absorbing all sector-pair-year factors
(synergies, barriers to entry, demand shocks). Controls $$X_{g,n,t-1}$$ include firm size, value
added, number of occupations, cash holdings, tangible assets, and total wages, all scaled by
workers. Standard errors are double-clustered at the sector of origin and sector of entry.

**Shift-share instrument (HC Bartik)** (eq. 2-3, p. 1348). To address omitted time-varying
firm factors, the paper constructs an instrument that captures variation in HC distance due to
changes in incumbent firms' human capital, holding firms' workforce composition fixed at their
2003 values:

$$
\text{HC Bartik}_{g,n} = \sum_i \hat{s}_{g,i,03} \cdot \Delta \hat{s}_{n,i,03,11}, \tag{2}
$$

where $$\Delta \hat{s}_{n,i,03,11} = \hat{s}_{n,i,11} - \hat{s}_{n,i,03}$$ is the change in the
normalized occupation share of sector $$n$$ from 2003 to 2011. This is equivalently:

$$
\text{HC Bartik}_{g,n} = -(\text{HC distance}^{03}_{g,n,11} - \text{HC distance}^{03}_{g,n,03}), \tag{3}
$$

so a high HC Bartik value means sector $$n$$ has become less distant from firm $$g$$ over 2003-2011.
Identification follows Borusyak, Hull, and Jaravel (2022): the shocks (occupation-level workforce
changes $$\Delta \hat{s}_{n,i,03,11}$$) are the source of variation and the shares ($$\hat{s}_{g,i,03}$$)
are the weights. The identification differs from the exposure-share approach of
Goldsmith-Pinkham, Sorkin, and Swift (2020). The identification assumption is that long-term
changes in incumbents' workforce composition are uncorrelated with firm-level unobservables.
The paper validates this assumption by regressing shocks on potential observable confounders
following Xu (2022).

**Event study around entry** (eq. 5-6, pp. 1351, 1361). For employment and performance outcomes,
the paper estimates dynamic regressions from $$t-4$$ to $$t+3$$ around entry, separately for firms
above and below the HC distance median, plotting coefficient paths to show the timing and
persistence of effects. Specifications include sector-of-origin, sector-of-entry, and year fixed
effects; standard errors are double-clustered.

## Empirical specifications

**Main build-or-buy regression (R1, R2).** The OLS specification (eq. 1) is estimated on 61,228
firm-sector-year observations from 2005 to 2014 (firms with at least 20 workers and at least 1%
of entry-year sales in the new sector). Table 3 reports four specifications: baseline sector-triplet
FE (col. 1), adding size-quartile FE (col. 2), adding main-sector FE to account for synergies
(col. 3), and adding firm FE to exploit within-firm variation across sectors (col. 4). The HC
distance coefficient is positive and significant at 5% across all four. The IV specification
(Table 4) is estimated on the 2011-2014 subsample (after the 2003-2011 shock period); Column 1
uses sector-of-origin by entry FE; column 2 adds sector-of-origin by entry by year FE.

**Employment decomposition (R3, R4).** Table 5 regresses 3-year employment growth ($$t-1$$ to $$t+3$$)
and its decomposition into top-5-occupation growth and other-occupation growth on HC distance,
separately for build (Panel A) and buy (Panel B) entries surviving 3 years post-entry. Table 6
further decomposes total employment growth into internal flows (from other subsidiaries) and
external flows (from outside the firm), revealing that builds rely exclusively on external hiring.
All specifications include sector-of-origin, sector-of-entry, and year FE; errors double-clustered.

**Labor market tightness and contract type (channels for R1).** Table 7 splits the main
regression by local labor market (LLM) tightness tercile (Panel A, 2010-2014 subsample) and by
fraction of permanent contracts tercile (Panel B). The HC distance effect on buy probability is
significant only in the tightest LLM tercile (coef = 0.023\*\*) and in the highest permanent-contract
tercile (coef = 0.024\*), consistent with higher build costs when hiring is harder.

**Organizational skills heterogeneity (R5, R6).** Table 8 splits the sample by three proxies for
organizational skills: (i) fraction of top-layer managers in the wage bill (Caliendo, Monte, and
Rossi-Hansberg (2015)), (ii) SG&A-related occupations wage share, and (iii) presence of any HR
worker. The HC distance effect is significant only for the lowest-skill tercile in all three
measures. Table 9 regresses the change in SG&A wage share, top-layers share, and HR adoption
between $$t-1$$ and $$t$$ on HC distance, separately for builds (Panel A) and buys (Panel B), finding
investment only among build entries.

**Post-entry performance (R7).** Table 11 regresses log(Sales), sales growth rate, survival
indicator, change in operating income per worker, and return on assets at $$t+3$$ on HC distance
for build entries (Panel A) and buy entries (Panel B). Table 12 adds an interaction between HC
distance and organizational skill indicators for build entries, finding that high-organizational-
skill firms suffer 20% lower sales vs 30% for low-skill firms in distant sectors (coefficient
on interaction HC distance x High SG&A = 0.245\*\*, Table 12 col. 1, p. 1363).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| French matched employer-employee data (DADS - Declarations Annuelles des Donnees Sociales) | Firm-level workforce composition by 4-digit occupation code (414 codes); used to compute HC distance | No page yet |
| French ownership links data (LIFI - Enquete sur les Liaisons financieres entre societes) | Identifies business group structure and subsidiaries; links firms to M&A targets | No page yet |
| French tax files (BIC - Benefices Industriels et Commerciaux) | Balance sheets and income statements at subsidiary level; firm-level controls | No page yet |
| French sales breakdown data (EAE/VAC - Enquete Annuelle des Entreprises / Ventilation des Ventes par Activite) | Identifies firm entries into new sectors (sales by sector, 3-digit SIC); sample period 2003-2014 | No page yet |
| SDC Platinum (M&A deals) | M&A transaction data (acquirer, target, deal date, ownership stakes) for buy entries 2003-2014 | [SDC Platinum](/wiki/licensed/sdc-platinum/) (licensed) |
| Bureau van Dijk Zephyr (M&A deals) | Supplementary M&A data matched with French administrative records; 7,165 M&A deals, 4,139 acquirers | No page yet |
| Pole emploi (French unemployment agency) occupational tightness | Local labor market (LLM) tightness measure by occupation; 348 LLMs, used for Table 7 robustness | No page yet |

Sample: 61,228 firm-sector-year entries from 2005 to 2014 (127,185 build; 2,415 buy). Administrative
data covers all French firms with at least 20 workers from 2003 to 2014.

## When to read the full paper

Use the [original](https://doi.org/10.1093/rfs/hhaf004) if you are:
studying the determinants of the build-versus-buy choice in diversification; measuring human
capital distance between firms and sectors; replicating the shift-share IV (HC Bartik) design
for workforce composition shocks; understanding how organizational skills affect labor integration
costs in M&As; or extending the analysis to non-French settings. The locators above point to the
exact tables.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(5), 2025. This distillation was
extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**.
The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Beaumont, Paul, Camille Hebert, and Victor Lyonnet.
> "Build or Buy? Human Capital and Corporate Diversification."
> *The Review of Financial Studies* 38, no. 5 (2025): 1333-1367.
> DOI: 10.1093/rfs/hhaf004. (C) 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
