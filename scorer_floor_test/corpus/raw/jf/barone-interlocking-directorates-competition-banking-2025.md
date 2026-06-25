---
title: "Interlocking Directorates and Competition in Banking: Barone, Schivardi & Sette (2025)"
description: >-
  Distilled: Exploiting Italy's 2011 Monti Decree, which unexpectedly banned
  shared board members among competing banks, the paper finds that prohibiting
  interlocks reduced corporate loan interest rates by 14 to 32 basis points on
  previously interlocked relationships, with larger drops for high-quality
  firms and high-market-share networks, and a subsequent increase in price
  dispersion consistent with competitive pricing. J. Finance 2025, CC BY 4.0.
  Seven core results with source locators, datasets used, the identification
  strategy, and the estimating specifications with equations.
sidebar:
  label: Barone-Schivardi-Sette 2025
  order: 1
tags: [paper-summary, banking, competition, corporate-lending, interlocking-directorates,
       panel-regression, difference-in-differences, natural-experiment,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:bank-of-italy-credit-register, data:cerved]
paper:
  authors: Guglielmo Barone, Fabiano Schivardi, Enrico Sette
  authorList:
    - { family: Barone, given: Guglielmo, affiliation: University of Bologna }
    - { family: Schivardi, given: Fabiano, orcid: "0000-0001-7708-1011", affiliation: "Libera Università Internazionale degli Studi Sociali Guido Carli (LUISS)" }
    - { family: Sette, given: Enrico, affiliation: Bank of Italy and CEPR }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 1963–2016
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13464
  jel:
    codes: [G21, G28, L41]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Banking stability, regulation, efficiency
    - Corporate Finance and Governance
    - Global Financial Crisis and Policies
  dataAccess: proprietary-confidential
  outcome:
    - corporate loan interest rate (revolving credit lines)
    - price dispersion across loan relationships
    - firm investment rate
    - firm employment growth (wage bill growth)
    - firm sales growth
    - granted credit quantity
  outcomeClass: [firm-financing, credit-supply, firm-real-outcomes]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-05-27; corroborated by artifact p. 1963 open-access notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available at Wiley Online Library (doi: 10.1111/jofi.13464, confirmed 2026-06-05)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 13
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, instrumental-variables]
    identification: natural-experiment
  contributionType: [new-fact]
  mechanisms: [market-power, information-asymmetry, networks]
  scope:
    region: Italy
    assetClass: corporate loans (revolving credit lines)
    period: 2011-01..2014-12
    frequency: quarterly
    dataType: [administrative, accounting]
    granularity: [firm, transaction]
    n: "3,561,068 firm-bank-quarter observations; 192,732 unique firms; 604 banks"
  findings:
    - ref: R1
      outcome: corporate loan interest rate
      metric: basis-points
      value: "-14 bps (Table V col. 5, most saturated; firm-bank, firm-quarter, bank-quarter FE); -32 bps (Table V col. 2, baseline with firm and bank controls)"
      direction: negative
      vsBenchmark: "1.5% of average pre-reform rate (14 bps / 9.3%); lower bound estimate from fully saturated spec"
    - ref: R2
      outcome: corporate loan interest rate
      metric: basis-points
      value: "-29.2 bps at peak (three years after reform, Figure 4)"
      direction: negative
      vsBenchmark: "3.1% of average pre-reform rate at peak"
    - ref: R3
      outcome: price dispersion across loan relationships
      metric: pp-effect
      value: "0.067 pp increase in within-province SD of rates on treated relationships post-reform (Table VIII col. 1); 0.100 pp in fully saturated spec (col. 2)"
      direction: positive
      vsBenchmark: "treated relationships had 25 bps lower SD than controls pre-reform; SD converges post-reform (F-stat p=0.000)"
    - ref: R4
      outcome: corporate loan interest rate
      metric: basis-points
      value: "High-quality (low-leverage) firms see 16 bps larger drop than low-quality firms (Table IX, Panel A col. 2)"
      direction: negative
      vsBenchmark: "creditworthy firms benefit most: 16 bps differential for leverage; 13 bps for ROA; 12 bps for liquidity; 13 bps for Z-score"
    - ref: R5
      outcome: corporate loan interest rate
      metric: basis-points
      value: "High-market-share networks: Treated*Post = -0.232 (Table IX Panel B col. 1); Treated*Post*Low = +0.177; implying low-market-share networks have ~17 bps smaller drop"
      direction: negative
      vsBenchmark: "larger network market share implies stronger pre-reform collusion and larger post-reform rate decline"
    - ref: R6
      outcome: firm investment rate
      metric: pp-effect
      value: "1.056 pp increase for a firm with all treated credit (Table XII col. 1); 0.843 pp with firm and bank controls (col. 2)"
      direction: positive
      vsBenchmark: "4.5% of SD of investment rate; aggregate investment rate of sample firms increased by ~0.3 pp per year"
    - ref: R7
      outcome: firm sales growth
      metric: pp-effect
      value: "1.538 pp increase (Table XII col. 5); 1.593 pp with controls (col. 6); wage bill growth 0.757 pp (col. 3)"
      direction: positive
      vsBenchmark: "6.6% of SD of sales growth; 3.9% of SD of wage bill growth"
  resultType: new-finding
  relatesTo:
    - { cite: "Geng, Gopalakrishna & Huang (2021)", doi: '10.2139/ssrn.3973387', relation: cites, note: "also exploit staggered U.S. state-level ID law changes to show IDs reduce competition, particularly for R&D firms" }
    - { cite: "Colombo (2022)", doi: '10.2139/ssrn.4361055', relation: cites, note: "U.S. airline evidence that two directors sharing a third-company appointment reduces supply and raises prices" }
    - { cite: "Faia, Mayer & Pezone (2022)", relation: cites, note: "same Save Italy decree on Italian listed firm stock returns" }
    - { cite: "Azar, Schmalz & Tecu (2018)", doi: '10.1111/jofi.12698', relation: cites, note: "common ownership raises airline ticket prices 3-7%; benchmark for effect size comparison" }
    - { cite: "Khwaja & Mian (2008)", doi: '10.1257/aer.98.4.1413', relation: builds-on, note: "firm-quarter fixed effects strategy to identify bank loan supply using multiple lending relationships" }
    - { cite: "Crawford, Pavanini & Schivardi (2018)", doi: '10.1257/aer.20150487', relation: cites, note: "information asymmetry can intensify credit rationing in more competitive markets" }
    - { cite: "Stiglitz & Weiss (1981)", relation: cites, note: "credit rationing theory motivating the credit-quantity analysis" }
  openQuestions:
    - "Whether results generalize beyond Italy's corporate credit market to other bank lending markets or other financial sectors with different ownership structures (p. 2004)."
    - "The precise mechanism by which board-level coordination translates to branch-level loan pricing, given that loan officers may be unaware of IDs (p. 1968-1969)."
    - "Whether the information-sharing channel of IDs, while dominated by the collusion effect in this setting, plays a role in other markets where asymmetric information is more severe (p. 2001-2002)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full PDF read (pp. 1963-2016). Results extracted from Tables V, VI, VII, VIII, IX, X, XI, XII and Figure 4. Not human-verified. Not reproduced. Data from Bank of Italy supervisory and credit registers are proprietary-confidential." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (Tables V, VIII, IX, XII, Figure 4, equations 1-8). Fixed: R4 body-table sign for Treated*Post*Low leverage coefficient corrected from +0.155 to -0.155 (PDF Table IX Panel A col. 2); vsBenchmark liquidity differential corrected from 13 bps to 12 bps; removed introducesData: true (paper uses existing BoI data, introduces no new source); removed new-data from contributionType; replaced colorful superlative in When-to-read section."
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13464", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-05-27" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification strategy, and the estimating specifications with equations: enough to understand what the reform caused and how it was measured, without reading all 54 pages. To replicate or extend, read the full source at [doi.org/10.1111/jofi.13464](https://doi.org/10.1111/jofi.13464).

## TL;DR

The paper exploits Italy's "Save Italy" Monti Decree of December 2011 (Article 36), which unexpectedly banned shared board members (SBMs) among competing banks, as a natural experiment to identify the causal effect of interlocking directorates (IDs) on corporate loan pricing. Using a difference-in-differences design on 3.5 million firm-bank-quarter observations from the Italian Credit Register (2011Q1-2014Q4), and including a full set of firm-quarter and bank-quarter fixed effects to control for all time-varying unobserved heterogeneity at both the firm and bank level, the paper finds that prohibiting IDs reduced corporate loan interest rates by 14 to 32 basis points on treated relationships relative to controls. The effect grows to 29.2 bps at the peak (three years after reform), price dispersion on treated loans increases post-reform (consistent with a shift away from collusive uniform pricing), high-quality firms benefit most, networks with larger market share show the largest drops, and firms more exposed to interlocked banks improve investment, employment, and sales after the reform.

## Core results

Magnitudes and significance are as reported; `\*p < 0.10`, `\*\*p < 0.05`, `\*\*\*p < 0.01`. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Prohibiting IDs reduced corporate loan rates on treated relationships by 14-32 bps** (depending on fixed-effect saturation level) | Table V, p. 1985 | Preferred specification (col. 5, firm-bank + firm-quarter + bank-quarter FE): -0.139\*\*\* (0.041); baseline (col. 2, firm and bank controls + FE): -0.317\*\*\* (0.079) |
| R2 | **Effect builds over time; rate drop reaches 29.2 bps at the peak** three years after reform; no pre-trend detected | Figure 4, p. 1987 | Quarterly DiD coefficients significant from Q4 post-reform onward; cumulative drop by quarter 12 of approximately -0.30 percentage points |
| R3 | **Price dispersion on treated relationships increases post-reform**: consistent with a competitive shift; dispersion was 25 bps lower on treated loans pre-reform | Table VIII, p. 1993 | Treated\*Post = 0.067\*\* (col. 1) to 0.100\*\*\* (col. 2); pre-reform dispersion convergence confirmed (F-test p=0.000) |
| R4 | **High-quality (creditworthy) firms benefit disproportionately** from the reform: low-leverage firms see 16 bps larger rate drop | Table IX Panel A, p. 1995 | Treated\*Post\*Low interaction for leverage: -0.155\*\*\* (0.036); for ROA: +0.125\*\*\* (0.033); for liquidity: +0.116\*\*\* (0.036); for Z-score: +0.127\*\*\* (0.047) |
| R5 | **Networks with higher market share show larger rate drops**, consistent with stronger pre-reform collusion | Table IX Panel B, p. 1995 | Treated\*Post = -0.232\*\*\* (0.053) for high-market-share; Treated\*Post\*Low = +0.177\*\*\* (0.057) |
| R6 | **Investment rate increases for firms more exposed to interlocked banks**: 1.056 pp per unit share of treated credit | Table XII, p. 2003 | Treated\*Post = 1.056\*\* (0.492) without controls; 0.843\* (0.490) with controls; aggregate investment rate of sample firms up by ~0.3 pp/year |
| R7 | **Sales and employment grow for firms more exposed to treated banks** post-reform: 1.5 pp more sales growth; 0.8 pp more wage bill growth | Table XII, p. 2003 | Sales: Treated\*Post = 1.538\*\*\* (0.514), 1.593\*\*\* (0.513) with controls; wage bill: 0.757\* (0.413), 0.779\* (0.415) |

**Overall (paper's conclusion).** Prohibiting IDs among competing banks has competition-enhancing effects: it reduces the interest rates firms pay on corporate loans, increases price dispersion consistent with a breakup of collusive pricing, and translates into better real outcomes for borrowers. The effect is stronger for networks with greater market power and for firms that can better exploit improved outside options. The reform had no negative effect on credit supply, ruling out the credit-rationing mechanism. These results support stricter enforcement of ID bans.

## Theory / model

The paper has no formal mathematical model. It uses standard collusion theory as the organizing framework: IDs can facilitate collusion among competing banks by creating a direct channel for information exchange about prices and market strategies, making deviations from a collusive strategy more easily detectable and punishment more credible (Stigler (1964), Green and Porter (1984)). Under this view, shared board members (SBMs) are particularly effective collusion devices because SBMs in executive positions have direct access to pricing information and control over lending policies (p. 1968-1969).

The paper relates to three contemporaneous studies that also document anticompetitive effects of firm interconnections. Geng, Gopalakrishna, and Huang (2021) exploit staggered U.S. state-level ID law changes to show IDs reduce competition, particularly for R&D-intensive firms. Colombo (2022) studies the U.S. airline market and finds that shared appointments in a third company reduce supply and raise prices. Azar, Schmalz, and Tecu (2018) document that common ownership among airlines raises ticket prices 3-7%, providing a benchmark for effect-size comparison. The paper also uses the firm-quarter fixed-effect strategy from Khwaja and Mian (2008) to isolate bank loan supply. Faia, Mayer, and Pezone (2022) study the same Save Italy decree's effect on Italian listed firms' stock returns. Crawford, Pavanini, and Schivardi (2018) show that credit rationing via Stiglitz and Weiss (1981) can intensify in more competitive markets, motivating the paper's credit-quantity analysis.

The theory generates several comparative statics that the paper tests:

1. If collusion raises prices uniformly, the rate drop post-reform should be larger for banks with greater combined market share (stronger market power pre-reform).
2. If collusion reduces price dispersion (to prevent detection of deviations), dispersion should increase after the ban.
3. If more creditworthy firms have better outside options in a competitive market, they should gain more from the reform.
4. If IDs facilitate information sharing that reduces adverse selection, credit quantity should not fall post-reform; if anything, the results show credit is stable or slightly increasing.

The paper uses the Italian antitrust authority's practice of defining markets at the NUTS 3 provincial level (110 provinces, average radius 30 km, broadly comparable to U.S. counties) and requires that a network of interlocked banks jointly hold above 20% market share in a province to define treatment (p. 1972-1973).

## Method

The identification strategy exploits the Monti Decree (Law Decree 201/2011 of December 6, 2011), passed unexpectedly by the newly formed Monti government in the context of Italy's sovereign debt crisis. The decree was unanticipated because it was drafted under acute fiscal pressure and overcame intense banking-sector lobbying that had previously blocked similar regulation. Article 36 prohibited individuals from simultaneously holding governing-body positions in two competing banking groups, and required compliance by April 2012. This constitutes an exogenous breakup of network connections not driven by bank pricing strategies.

The two key features that make identification credible are (p. 1974-1977):

1. Firms typically borrow from multiple banks, so a given firm can have loans that are "treated" (from a bank in an interlocked network in that province) and "control" (from banks in the same province outside any network) within the same quarter. This allows the inclusion of full firm-quarter fixed effects that absorb all time-varying observed and unobserved firm-level heterogeneity.
2. A given bank can have treated loans in provinces where it belongs to a network and control loans in provinces where it does not. This allows the inclusion of full bank-quarter fixed effects that absorb all time-varying bank-level heterogeneity, including any effects of the Eurozone sovereign debt crisis or other monetary policy measures that affect banks differentially.

The treatment indicator $$TR_{ijp}$$ is time-invariant, equal to one if bank $$j$$'s loans to firms in province $$p$$ satisfy three conditions in all four quarters before the decree (pp. 1972-1974): (i) bank $$j$$ belongs to an interlocked network in province $$p$$; (ii) bank $$j$$ and at least one connected counterpart each have at least 1% individual market share in $$p$$; and (iii) the network's combined market share in $$p$$ exceeds 20%.

## Empirical specifications

**Baseline DiD (equation 1, p. 1975).** The estimating equation is

$$
r_{ijpt} = \alpha_0 + \alpha_1 POST_t + \alpha_2 TR_{ijp} + \alpha_3 TR_{ijp} \times POST_t + \alpha_4' \mathbf{X}_{ijt} + D_{ijpt} + \epsilon_{ijpt}, \tag{1}
$$

where $$r_{ijpt}$$ is the gross interest rate on revolving credit lines that bank $$j$$ charges firm $$i$$ in province $$p$$ in quarter $$t$$; $$POST_t$$ is a dummy equal to one from 2012Q1 onward; $$TR_{ijp}$$ is the time-invariant treatment dummy; $$\mathbf{X}_{ijt}$$ is a vector of time-varying firm and bank characteristics (lagged one period); and $$D_{ijpt}$$ denotes combinations of fixed effects. The causal parameter of interest is $$\alpha_3$$: the within-firm-quarter, within-bank-quarter drop in rates on treated relationships post-reform.

The preferred specification (Table V, column 5) includes firm-bank, firm-quarter, and bank-quarter fixed effects, so $$\alpha_3$$ is identified purely from within-firm-bank variation over time. Standard errors are clustered at the bank-province level.

Sample: 3,561,068 firm-bank-quarter observations, 2011Q1-2014Q4 (four preperiod quarters, twelve postperiod quarters). 29% of observations are treated.

**Price dispersion regression (equation 2, p. 1992).** To test the collusion-consistent prediction that treated loans show less price dispersion before the reform and more after, the paper constructs the province-quarter standard deviation of rates separately for treated and control loans:

$$
\sigma_{pct} = \sqrt{\frac{1}{n_{pct}} \sum_{i,j \in pc} (r_{ijpt} - \bar{r}_{pct})^2},
$$

and estimates:

$$
\sigma_{pct} = \gamma_0 + \gamma_1 POST_t + \gamma_2 TR_{pc} + \gamma_3 TR_{pc} \times POST_t + Dum_{pct} + e_{pct}, \tag{2}
$$

where $$TR_{pc}$$ is an indicator for treated province-category cells. Results reported in Table VIII (p. 1993).

**Heterogeneity specification (equation 3, p. 1993).** To test comparative statics on firm and network characteristics:

$$
r_{ijpt} = \beta_0 + \beta_1 TR_{ijp} \times POST_t + \beta_2 TR_{ijp} \times POST_t \times HET_{ij} + D_{it} + D_{jt} + D_{ij} + \eta_{ijpt}, \tag{3}
$$

where $$HET_{ij}$$ is a low-dummy (equal to one for values at or below the median) for a firm or network characteristic measured before the reform. Firm characteristics include size, leverage, ROA, liquidity, and Z-score; network characteristics include market share, number of connected banks, HHI, market share gap, and multimarket contacts (Table IX, p. 1995).

**Spillover regression (equation 5, p. 1998).** To test for within-province and within-bank spillovers from treated to control loans:

$$
r_{ijpt} = \theta_0 + \theta_1 POST_t + \theta_2 Z_{jp} + \theta_3 Z_{jp} \times POST_t + \theta_4' \mathbf{X}_{ijt} + D_{ijpt} + u_{ijpt}, \tag{5}
$$

where $$Z_{jp}$$ is a province-level or bank-level share of interlocked credit. No evidence of spillovers is found (Table A.VI).

**Firm-level rate and credit-quantity regressions (equations 6-8, pp. 1999-2000).** The firm-level average interest rate is the credit-weighted average across lenders:

$$
r_{it} = \sum_j \frac{loan_{ijt}}{\sum_j loan_{ijt}} r_{ijt}, \tag{6}
$$

and the share of treated credit at the firm level is:

$$
ShTr_i = \frac{\sum_j TR_{ij} \times loan_{ij,2011Q4}}{\sum_j loan_{ij,2011Q4}}. \tag{7}
$$

The estimating equation at the firm level is:

$$
r_{it} = \beta_0 + \beta_1 Post_t + \beta_2 ShTr_i + \beta_3 ShTr_i \times POST_t + \beta_4' \mathbf{X}_{it} + Dum_i + Dum_t + \eta_{it}. \tag{8}
$$

A firm with all treated credit records a ~30 bps drop in interest rates (Table X, p. 2000), confirming the relationship-level results are not offset by reallocation across lenders. The same structure is used with log-granted credit as the dependent variable for quantity analysis (Table XI) and with investment rate, wage bill growth, and sales growth for real effects (Table XII).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Italian Credit Register (Bank of Italy) | Quarterly firm-bank loan quantities and gross interest rates on revolving credit lines (overdraft facilities) for relationships with total lending above 75,000 euros; 2011Q1-2014Q4; 3.5 million firm-bank-quarters | No page yet |
| Or.So. Database (Bank of Italy) | Register of bank board members at quarterly frequency; identifies SBMs holding multiple appointments on competing bank boards | No page yet |
| Supervisory Reports (Bank of Italy) | Unconsolidated and consolidated balance-sheet data for individual banks and banking groups; provincial-level market shares; quarterly | No page yet |
| Cerved | Firm balance sheets and income statements for all Italian incorporated companies; provides ROA, leverage, liquidity, size, Z-score for firm controls and firm-level real-outcome regressions | [no page yet](/wiki/datasets/) |

Sample period: 2011Q1-2014Q4 (16 quarters, quarterly frequency). 192,732 unique firms; 604 banks at group level. Treatment defined in the four quarters before the reform (2011Q1-Q4). The Italian Credit Register is a proprietary administrative database with access restricted to researchers affiliated with the Bank of Italy.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13464) if you are: studying the competitive effects of board interconnections (the paper applies a natural-experiment DiD design in the corporate lending setting); extending the analysis to other lending markets, countries, or forms of firm interconnection; interested in the robustness tables (Tables VI, VII) testing alternative market-share thresholds, alternative pre-period lengths, net vs. gross rates, and closed samples; or seeking the collusion-mechanism evidence (Section V: price dispersion in Table VIII; heterogeneity by network characteristics in Table IX Panel B; and the bargaining-power analysis in Table A.V and equation 4).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Barone, Guglielmo, Fabiano Schivardi, and Enrico Sette.
> "Interlocking Directorates and Competition in Banking."
> *The Journal of Finance* 80, no. 4 (August 2025): 1963-2016.
> DOI: 10.1111/jofi.13464. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
