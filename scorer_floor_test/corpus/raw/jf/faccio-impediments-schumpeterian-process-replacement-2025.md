---
title: "Impediments to the Schumpeterian Process: Faccio & McConnell (2025)"
description: >-
  Distilled: Using hand-assembled data on the 20 largest firms across up to 75
  countries from circa 1910, Faccio and McConnell find that political connections
  are the primary impediment to the replacement of large firms, but only when
  accompanied by cross-border barriers to trade and capital flows. The Journal
  of Finance 80(6) 2025, CC BY 4.0. Eight core results with source locators,
  datasets used, the identification strategy, and the empirical specifications.
sidebar:
  label: Faccio-McConnell 2025
  order: 1
tags: [paper-summary, corporate-governance, political-economy, creative-destruction,
       firm-dynamics, panel-regression, difference-in-differences, event-study,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:worldscope, data:compustat-global]
paper:
  authors: Mara Faccio, John J. McConnell
  authorList:
    - { family: Faccio, given: Mara, orcid: "0000-0002-4433-7989", affiliation: Purdue University (Mitch Daniels School of Business) }
    - { family: McConnell, given: John J., orcid: "0000-0002-7681-7143", affiliation: Purdue University (Mitch Daniels School of Business) }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3359–3399
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13481
  jel:
    codes: [G34, O16, D72]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Corporate Finance and Governance
    - Firm Innovation and Growth
    - Innovation and Knowledge Management
  dataAccess: hand-collected
  outcome:
    - probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018
    - probability that a large Italian firm remains among the 20 largest following the exogenous loss of political connections
  outcomeClass: [firm-dynamics]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-08-20; corroborated by artifact p. 3359 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-03)
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 0

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, difference-in-differences, probit-regression]
    identification: natural-experiment
  contributionType: [new-fact, new-data]
  mechanisms: [political-capture]
  introducesData: true

  scope:
    region: global
    assetClass: large non-financial and financial firms (privately held and publicly traded)
    period: 1900-01..2018-12
    frequency: annual
    dataType: [accounting, other]
    granularity: [firm, aggregate]
    n: "1,115 firms (60 countries, circa 1910); 30,891 firm-years (47 countries, 2000 Worldscope panel); 3,835 obs / 226 firms (Italy DiD, 1921-1971)"

  relatesTo:
    - { cite: "Fogel, Morck & Yeung (2008)", doi: '10.1016/j.jfineco.2007.06.004', relation: extends, note: "extends their 44-country, 2-decade evidence to 75 countries over up to a century and investigates the mechanisms" }
    - { cite: "Faccio (2006)", doi: "10.1257/000282806776157704", relation: builds-on, note: "uses Faccio (2006)'s definition and data on politically connected firms for the 2000 sample" }
    - { cite: "Rajan & Zingales (2003)", doi: '10.1016/s0304-405x(03)00125-9', relation: tests, note: "tests their interest-group theory that incumbents require both trade and capital barriers to entrench their positions" }
    - { cite: "Akcigit, Baslandze & Lotti (2023)", doi: '10.3982/ecta18338', relation: cites, note: "cited for formal model predicting politically connected firms are more likely to remain large only when regulatory barriers (wedges) are large" }
    - { cite: "Faccio & McConnell (2024)", doi: "10.1111/fima.12489", relation: builds-on, note: "uses their Italy dataset documenting the exogenous severing of political connections at the fall of fascism" }
    - { cite: "Braggion & Moore (2013)", relation: cites, note: "cited as prior evidence that politically connected firms in late Victorian Britain are not the best firms" }

  openQuestions:
    - "The paper does not identify which specific policies (tariffs, capital controls, industry regulations) politically connected firms lobby for; future work could trace the exact regulatory mechanisms (p. 3396)."
    - "The circa 1910 sample covers book equity for 60 countries but political connections data for only 19 countries; broader political-connection data could sharpen the cross-country analysis (p. 3363)."
    - "Whether the results generalize to countries and periods outside the samples analyzed, in particular to the post-2018 era (p. 3396)."

  findings:
    - { ref: R1, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: probability, value: "13.6% unconditional survival rate (1,115 firms, 60 countries)", direction: none }
    - { ref: R2, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: coefficient, value: "0.0959** (p = 0.018)", direction: positive, vsBenchmark: "10% unconditional rate for connected-country firms" }
    - { ref: R3, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: coefficient, value: "0.0825*** to 0.1059*** across specifications", direction: positive, vsBenchmark: "baseline with state ownership, industry, and size centile fixed effects" }
    - { ref: R4, outcome: probability that a large Italian firm remains among the 20 largest following the exogenous loss of political connections, metric: coefficient, value: "-0.0927*** (p = 0.009)", direction: negative, vsBenchmark: "pre-1944 connected firms vs. unconnected firms (DiD)" }
    - { ref: R5, outcome: probability that an Italian firm is politically connected in 1911 (selection model for firm quality among connected firms), metric: coefficient, value: "ROE coeff. = -0.0267* (p = 0.087); M/B coeff. = 0.0168 (p = 0.592)", direction: negative, vsBenchmark: "unconnected Italian firms in 1911 selection model" }
    - { ref: R6, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: coefficient, value: "0.0257* to 0.0384** (political connections)", direction: positive, vsBenchmark: "2.2% unconditional rate in 2000-2018 sample" }
    - { ref: R7, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: coefficient, value: "PC x Openness coeff. = -0.0667*** (p = 0.002)", direction: negative, vsBenchmark: "closed-economy baseline (trade and capital flows both restricted)" }
    - { ref: R8, outcome: probability that a large firm circa 1910 (or 2000) remains among the 20 largest in its country in 2018, metric: coefficient, value: "GDP growth on fraction remaining large coeff. = -0.4628 (p = 0.021); implied 4.24 to 7.17 pp higher GDP growth absent political connections", direction: negative, vsBenchmark: "sample median per capita GDP growth of 26.98% (2001-2021)" }
  resultType: confirms

  replicationCode:
    status: none

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: "Full text read (pp. 3359-3399); eight results extracted from the CC-BY PDF. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF Tables I-VIII; two fixes applied: R4 magnitude corrected from -0.1070** (p=0.011) to -0.0927*** (p=0.009) per Table IV col. (1), and empirical-specs significance stars corrected from *** to ** for R6 upper bound 0.0384."
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Added classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) from a fresh PDF read; existing results and
        sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Classification axes re-checked against the source PDF; fixed two issues:
        removed market-power from mechanisms (market dominance is the outcome, not
        the channel - political-capture is the genuine mechanism the paper argues
        for) and removed literal false from rightsSignalConflict (field must be
        omitted when not true per template rules); identification=natural-experiment,
        contributionType=[new-fact,new-data], introducesData=true, and data-scope
        all confirmed correct against PDF.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the page's already-verified Core-results table and
        relatesTo edges; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; one fix applied - R5 outcome corrected from the
        firm-survival outcome to the actual Table III Panel B dependent variable
        (probability of being politically connected in 1911, a selection model);
        all seven other magnitudes and directions confirmed correct against PDF.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13481
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-08-20"

---

**What this is.** The paper's core results, the identification strategy (including the Italy quasi-experiment), and the empirical specifications with real equations: enough to know what it found and how, without reading all 41 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13481).

## TL;DR

Faccio and McConnell ask what prevents the "destructive" part of Schumpeter's creative destruction: why do large incumbent firms so often fail to be replaced by new large firms? This extends the 44-country, 2-decade evidence of Fogel, Morck, and Yeung (2008) to 75 countries and up to a century, investigating the mechanisms behind the lack of replacement. Using hand-assembled data on the 20 largest firms in 60 countries circa 1910 and Worldscope data for 47 countries in 2000, they track which firms remain among the largest in 2018. Intrafirm innovation (new technology, patents, R&D) has at most a secondary role. Bank-board interlocks matter over the shorter 2000-2018 period but not over the century-long horizon. Political connections are the most robust predictor: a politically connected large firm circa 1910 is roughly 9.6 percentage points more likely to remain among the 20 largest in its country in 2018 than an unconnected firm of equal size, and the effect is concentrated in countries closed to cross-border trade and capital flows. This is consistent with the formal model of Akcigit, Baslandze, and Lotti (2023) predicting that connected firms remain large only when regulatory wedges are sufficiently large. A quasi-natural experiment using the fall of fascism in Italy, documented in Faccio and McConnell (2024), confirms that the connection is causal: firms whose political connections were exogenously severed experienced a large, statistically significant drop in the probability of remaining among the 20 largest. The result that politically connected Italian firms are of average or below-average quality is also consistent with Braggion and Moore (2013)'s evidence on late Victorian Britain.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Only 13.6% of the 20 largest firms circa 1910 remain among the 20 largest in their country in 2018; over the century replacement is the norm | Table I Panel A, p. 3367; p. 3366 | 13.6% unconditional survival rate across 60 countries (1,115 firms); 152 firms remain large in all three treatment groups |
| R2 | Political connections (circa 1910) increase the probability of remaining large by 9.59 percentage points vs. an unconditional rate of 10% for connected-country firms; New tech is insignificant | Table II col. (4), p. 3370 | Political connections coeff. = 0.0959\*\* (p-value 0.018); New tech coeff. = -0.0027 (p = 0.368) |
| R3 | The political-connections effect is robust to controlling for state ownership, industry, and size centile fixed effects; bank-board interlocks are insignificant over the century | Table II cols. (6)-(9), pp. 3370-3372 | Political connections coeff. ranges 0.0825\*\*\* to 0.1059\*\*\* across specifications; bank-board interlocks coeff. not statistically significant in col. (3) |
| R4 | Italy quasi-experiment: after the fall of fascism (1944), formerly politically connected firms became disproportionately less likely to remain among the 20 largest; implied counterfactual replacement rate is -18% to +36% of observed difference | Table IV col. (1), p. 3377; p. 3379 | Fascist x Post Fascism coeff. = -0.0927\*\*\* (p = 0.009); difference-in-differences sample mean Y for connected firms pre-1944 = 0.1283 |
| R5 | Politically connected firms in Italy are not the best firms: ROE is marginally significantly negative and M/B is similar to unconnected firms | Table III Panel B cols. (1)-(4), pp. 3374-3375 | ROE coeff. = -0.0267\* (p = 0.087) in col. (1); M/B coeff. = 0.0168 (p = 0.592) in col. (3) |
| R6 | In the 2000-2018 sample, political connections increase the probability of remaining among the 20 largest by 2.6 to 4.3 percentage points vs. an unconditional rate of 2.2%; patents and R&D are also significant but smaller in magnitude | Table V cols. (1)-(5), pp. 3382-3383 | Political connections coeff. = 0.0257\* to 0.0384\*\*; patents coeff. = 0.0056\*\*; R&D/TA coeff. = 0.0082\*\* |
| R7 | Political connections interact negatively and significantly with openness: the effect of connections on remaining large is attenuated and disappears in open economies (both trade and capital flows required) | Table VII col. (2), p. 3387; Table VIII col. (1), p. 3388 | Table VII: Political connections x Openness Ind. level coeff. = -0.5034\* (p = 0.050); Table VIII: Political connections x Openness coeff. = -0.0667\*\*\* (p = 0.002) |
| R8 | Back-of-envelope: absent political connections, per capita GDP growth 2001-2021 would have been 4.24 to 7.17 percentage points higher than the sample median of 26.98% | p. 3380 | Regression coeff. of GDP growth on fraction remaining large = -0.4628 (p = 0.021); counterfactual replacement rate gap = 2.47 to 4.18 percentage points |

**Overall (paper's conclusion).** Political connections are the most robust impediment to the Schumpeterian process of large-firm replacement, but only when cross-border barriers to trade and capital are in place. Intrafirm innovation plays a secondary role at most over the century-long horizon. The Italy quasi-experiment confirms causality. The implied macroeconomic cost is substantial: absent political-connection-enabled entrenchment, long-run per capita GDP and TFP growth would have been materially higher.

## Theory / model

The paper has no formal structural model. It organizes competing hypotheses from Schumpeter, Brandeis, and Steffens and tests them empirically.

**Hypothesis 1 (Schumpeter 1942).** Large firms can remain dominant by reinventing themselves through intrafirm innovation. Tested via the new-tech indicator (circa 1910), patents, R&D, and productivity (2000 sample).

**Hypothesis 2 (Brandeis 1914, 1934).** Large firms remain large through bank-board interlocking directorates that allow them to restrict access to domestic capital and suppress entry. Tested via the count of bank-board interlocks per firm.

**Hypothesis 3 (Steffens 1906).** Large firms remain large by capturing the political process to obtain regulations that suppress entry. Tested via the political connections indicator.

**The Rajan-Zingales mechanism.** Following Rajan and Zingales (2003), a necessary condition for domestic political capture to be effective is that cross-border competition is also restricted. When the economy is open to both cross-border trade flows and cross-border capital flows, it is difficult for domestic incumbents to entrench their positions even with political connections, because foreign entrants bypass domestic restrictions. The paper therefore examines a triple interaction:

$$
\text{Pr}(\text{Top 20 in 2018}) = \alpha + \beta_1 \text{PC}_{i} + \beta_2 (\text{PC}_{i} \times \text{Openness}_{c}) + \gamma X_{it} + \delta_c + \varepsilon_{it} \tag{T1}
$$

where $$\text{PC}_{i}$$ is an indicator for political connections, $$\text{Openness}_{c}$$ is the interaction of trade flows and capital flows at the country (or country-industry) level, $$X_{it}$$ includes size, age, innovation proxies, and $$\delta_c$$ are country fixed effects. The prediction is $$\beta_2 < 0$$: political connections enable entrenchment only in closed economies.

**Identification strategy (Italy quasi-experiment).** The fall of fascism in 1943-1944 plausibly exogenously severed political connections: fascist politicians became ineligible for office, and post-WWII laws prohibited companies from having politicians as officers and directors. The paper exploits this shock in a difference-in-differences framework, comparing firms with fascist political connections to firms without, before and after 1944. The subset of connections involving directors appointed as life Senators by the King provides further exogeneity (the firm did not choose to be connected; the King appointed the Senator).

## Method

The paper applies linear probability models of firm survival in the top-20 ranking and difference-in-differences estimation. It builds on `panel-regression`, `difference-in-differences`, and `probit-regression` primitives.

**Linear probability models (LPM) for the circa 1910 and 2000 samples.** The estimator is OLS. The dependent variable is a binary indicator for whether a firm that was among the 20 largest in its country in 1910 (or 2000) is also among the 20 largest in 2018. All variables other than binary indicators are standardized. Standard errors are robust (circa 1910) or double-clustered at the firm and year level (Italy panel). The specification family is:

$$
Y_{i,2018} = \alpha + \beta_1 \ln(\text{BookEquity}_{i,t_0}) + \beta_2 \ln(\text{FirmAge}_{i,t_0}+1) + \beta_3 \text{NewTech}_{i} + \beta_4 \text{PC}_{i} + \beta_5 \text{BB\_Interlocks}_{i} + \delta_c + \delta_{\text{ind}} + \varepsilon_i \tag{M1}
$$

where $$t_0 \in \{1910, 2000\}$$, $$\delta_c$$ are country fixed effects, and $$\delta_{\text{ind}}$$ are industry fixed effects (included in selected specifications).

**Difference-in-differences for the Italy panel.** The dependent variable is an indicator for being among the 20 largest Italian firms, measured 20 years ahead (p. 3376). The key regressor is the interaction of a time-invariant indicator for fascist political connections and an indicator for years 1944 and after:

$$
Y_{i,t+20} = \alpha + \beta \left(\text{Fascist}_i \times \text{Post Fascism}_t\right) + \gamma_1 \ln(\text{BookEquity}_{it}) + \gamma_2 \ln(\text{FirmAge}_{it}+1) + \delta_i + \delta_{\text{ind}} + \delta_t + \varepsilon_{it} \tag{M2}
$$

where $$\delta_i$$ are firm fixed effects, $$\delta_{\text{ind}}$$ are industry fixed effects, and $$\delta_t$$ are year fixed effects. Standard errors are double-clustered at the firm and year level. The sample runs from 1921 (first year fascists were elected) to 1971 (last year of imita.db data).

**Productivity measure.** For the 2000 sample, total factor productivity is constructed using the Olley-Pakes (1996) method following Kogan et al. (2017) and the Stata code of Imrohoroglu and Tuzel (2014) (p. 3366).

## Empirical specifications

**Circa 1910 baseline (R2, R3).** LPM of the probability of being among the 20 largest firms in 2018, on a sample of 1,115 firms from 60 countries, with country fixed effects and optionally industry fixed effects. Key regressors: standardized ln(Book Equity), standardized ln(Firm Age), New Tech indicator, Political Connections indicator, ln(Bank-Board Interlocks + 1), State-owned enterprise indicator. Robust standard errors. Specifications are progressively augmented from col. (1) to (9) of Table II (p. 3370).

**Italy 1911 selection model (R5).** LPM explaining the probability of being politically connected in 1911, on 793 Italian firms with book equity at least 1 million Italian lira. Regressors include ln(Book Equity), ln(Net Income), ln(Firm Age), New Tech, University Town, ROE, M/B, publicly traded indicator. Specifications (1)-(4) of Table III Panel B (p. 3374) add industry and location fixed effects.

**Italy difference-in-differences (R4).** Specification (M2) above. The main sample in col. (1) of Table IV (p. 3377) has 3,835 observations and 226 unique firms (publicly traded in Milan), 1921-1971. Robustness checks in cols. (3)-(6) isolate connections involving King-appointed Senators and exclude firms subject to post-fascism retaliation.

**Openness interaction (R7).** Tables VII and VIII augment the baseline specification with a triple interaction term $$\text{PC}_i \times \text{Trade}_c \times \text{Capital Flows}_c$$ where trade is (Imports + Exports)/GDP and capital flows are proxied by telephones per 100 people in 1914 (Kingsbury 1915) or by the dollar value of foreign M&A as a fraction of total M&A (Thomson ONE). Cols. (3)-(5) of both tables provide falsification tests using only trade or only capital flows. Standard errors are robust (circa 1910) or clustered at country level (2000 sample).

**2000 baseline (R6).** LPM of the probability of being among the 20 largest in 2018, on Worldscope firms from 47 countries in 2000. Regressors parallel the 1910 specifications plus patents, R&D/TA, productivity (Olley-Pakes), M/B, ROE, leverage, diversification, industry change 2000-2018, and a not-in-WS-2018 indicator for survivorship. Country, four-digit SIC industry, and country x industry fixed effects are added progressively; cols. (3)-(9) of Table V (pp. 3382-3383). Political connections coeff. = 0.0257\* to 0.0384\*\*.

**Back-of-envelope growth regression (R8).** Country-level OLS regressing per capita GDP growth (2001-2021, World Bank) on the fraction of firms remaining large (1910-2018). 57 observations. Regression coefficient = -0.4628 (p = 0.021), Table IV.IA (Internet Appendix, p. 3380 text). TFP growth (Feenstra, Inklaar, and Timmer 2015 Penn World Table 10.1) regression yields coefficient = -0.2486 (p = 0.083), 49 countries.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Hand-assembled business directories (56 sources, circa 1900-1925) | 20 largest firms per country circa 1910 (60 countries, 1,115 firms); book equity, founding year, political connections, bank-board interlocks | No page yet |
| Worldscope | 20 largest publicly traded firms per country in 2000 (47 countries) and 2018; book equity, financial data, firm identifiers | [no page yet](/wiki/datasets/) |
| Faccio (2006) political connections database | Political connections indicator for 2000 sample, 47 countries | No page yet |
| imita.db (IMprese ITAliane Data Base) | Italian publicly traded and private firms 1921-1971 (archival volumes by Credito Italiano) | No page yet |
| Il Taccuino dell'Azionista (1942, 1947 editions) | Supplement imita.db for 1941-1945 Italian firms | No page yet |
| Bena et al. (2017) patent data | Patents granted per firm in 2000 (Worldscope firms) | No page yet |
| World Bank World Development Indicators | Trade flows (imports + exports)/GDP; per capita GDP growth 2001-2021 | No page yet |
| Thomson ONE Banker M&A data | Foreign M&A fraction at country-industry level for capital flows proxy; M&A deal value 2000-2018 | No page yet |
| Penn World Table 10.1 (Feenstra, Inklaar, Timmer 2015) | TFP growth 2001-2019 for back-of-envelope calculation | No page yet |
| Capital IQ | Board member biographies to assess persistence of political connections in the 2000s for circa 1910 connected firms | No page yet |

Sample circa 1910: 1,115 firms, 60 countries, minimum 10 firms per country; book equity measured 1900-1925. Sample 2000: 30,891 firm-year observations for the full 47-country Worldscope panel (Table I Panel B, p. 3368). Italy DiD panel: 3,835 observations, 226 unique firms (main specification), 1921-1971.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13481) if you are: studying the long-run dynamics of corporate market power and the barriers that perpetuate it; building on the Rajan-Zingales framework for the interaction of political connections with trade and capital openness; using the Italy fascism quasi-experiment to identify causal effects of political connections on firm outcomes; or working on cross-country corporate governance with historical data going back to 1910. The Internet Appendix (available at the journal's online version) contains the list of 60 countries, 56 data sources, and variable definitions.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was extracted by an LLM on 2026-06-03 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Faccio, Mara, and John J. McConnell.
> "Impediments to the Schumpeterian Process in the Replacement of Large Firms."
> *The Journal of Finance* 80, no. 6 (December 2025): 3359–3399.
> DOI: 10.1111/jofi.13481. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
