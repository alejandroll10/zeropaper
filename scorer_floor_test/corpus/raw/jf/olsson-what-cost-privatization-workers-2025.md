---
title: "What Is the Cost of Privatization for Workers?: Olsson & Tag (2025)"
description: >-
  Distilled: Using Swedish administrative data covering two decades, this paper
  shows that privatization of state-owned enterprises imposes wage losses of
  5-9% and raises unemployment by 12%, while firm-level productivity rises
  35.7%; government transfers offset roughly half the worker income losses.
  J. Finance 2025, CC BY-NC 4.0. Eight core results with source locators,
  datasets used, the identification strategy, and the estimating equations.
sidebar:
  label: Olsson-Tag 2025
  order: 1
tags: [paper-summary, privatization, labor-economics, firm-dynamics, panel-regression,
       difference-in-differences, peer-reviewed, unreplicated,
       data:lisa-sweden, data:fek-sweden]
paper:
  authors: Martin Olsson and Joacim Tag
  authorList:
    - { family: Olsson, given: Martin, orcid: "0000-0001-6486-1780", affiliation: Research Institute of Industrial Economics (IFN) }
    - { family: Tag, given: Joacim, orcid: "0000-0002-4924-2479", affiliation: Research Institute of Industrial Economics (IFN) and Hanken School of Economics }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2107-2151
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13462
  jel:
    codes: [J31, G38, L33]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Labor market dynamics and wage inequality
    - Fiscal Policy and Economic Growth
    - Retirement, Disability, and Employment
  dataAccess: proprietary-confidential
  outcome:
    - worker wage income following privatization
    - worker unemployment incidence following privatization
    - government transfers to displaced workers
    - firm-level productivity (value-added per employee)
    - firm-level profitability (ROA)
  outcomeClass: [labor-careers-health, firm-real-outcomes]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-05-30; open access facilitated by Hanken Svenska
    Handelshogskolan as part of the Wiley - FinELib agreement)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: open-access PDF available (Wiley OnlineLibrary, doi 10.1111/jofi.13462, confirmed 2026-06-05)
  redistribution: extract-only (CC BY-NC 4.0 permits reuse for non-commercial purposes with attribution; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 8

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, matching]
    identification: natural-experiment

  contributionType: [new-fact, measurement]

  mechanisms:
    - agency
    - moral-hazard

  scope:
    region: Sweden
    assetClass: state-owned enterprise workers and firms
    period: 1990-01..2017-12
    frequency: annual
    dataType: [administrative, accounting]
    granularity: [individual, firm]
    n: "63,231 matched treated workers (70,079 treated workers identified); 368 privatized firms; 1,414,270 worker-year observations"

  findings:
    - ref: R1
      outcome: worker wage income following privatization
      metric: coefficient
      value: "-0.079 (t = -2.96), -5.8% short run, -9.3% medium run, -8.4% long run"
      direction: negative
      vsBenchmark: "relative to matched control workers in non-privatized SOEs (Table II)"
    - ref: R2
      outcome: worker unemployment incidence following privatization
      metric: pp-effect
      value: "1.3 pp (t = 5.16), +12.4% vs pre-privatization mean; short run 1.1 pp, medium 1.2 pp, long run 1.5 pp"
      direction: positive
      vsBenchmark: "relative to matched control workers (Table II)"
    - ref: R3
      outcome: government transfers to displaced workers
      metric: coefficient
      value: "0.119 (t = 5.82), +11.9% increase; offsets roughly half the income loss"
      direction: positive
      vsBenchmark: "total income effect only -3.5% (Table II, col 4) vs -7.9% wage effect"
    - ref: R4
      outcome: firm-level productivity (value-added per employee)
      metric: coefficient
      value: "109.5 KSEK (t = 2.77), +35.7% full period; log-productivity +11.5% (t = 2.03)"
      direction: positive
      vsBenchmark: "relative to matched control firms in non-privatized SOEs (Table V)"
    - ref: R5
      outcome: firm-level employment (number of employees)
      metric: coefficient
      value: "-0.163 (t = -2.82), -16.3% full period; job destruction rate +10.9 pp (t = 4.92)"
      direction: negative
      vsBenchmark: "relative to matched control firms (Table V)"
    - ref: R6
      outcome: firm-level profitability (ROA)
      metric: pp-effect
      value: "+2.1 pp (t = 1.82), marginally significant; +321.3% from near-zero baseline"
      direction: positive
      vsBenchmark: "relative to matched control firms (Table V)"
    - ref: R7
      outcome: business ownership rate among former SOE workers
      metric: basis-points
      value: "+6.3 bps (96.8%, t = 3.61), driven by limited liability company formation; +20 bps in long run (131.7%, t = 3.52)"
      direction: positive
      vsBenchmark: "relative to control workers; self-employment unchanged (Table III)"
    - ref: R8
      outcome: firm-level productivity conditional on CEO replacement
      metric: coefficient
      value: "+31.4% (t = 2.00) when CEO replaced; unchanged (t = 0.81) when CEO stays"
      direction: positive
      vsBenchmark: "productivity gain concentrated in privatizations with CEO departure (Table VI)"

  resultType: new-finding

  relatesTo:
    - { cite: "Megginson and Netter (2001)", relation: extends, note: "extends the firm-level privatization literature to quantify worker-level income and unemployment costs using matched administrative data" }
    - { cite: "Bastos, Monteiro, and Straume (2014)", doi: '10.1093/oep/gpu017', relation: tests, note: "tests whether wages rise (as in Portugal) or fall after privatization; finds they fall in Sweden, consistent with different wage-setting institutions" }
    - { cite: "Arnold (2022)", doi: '10.1257/app.20190428', relation: replicates, note: "corroborates the Brazilian evidence of wage declines post-privatization; Swedish magnitudes are smaller (~8% vs ~25%)" }
    - { cite: "Shleifer and Summers (1988)", relation: tests, note: "tests the breach-of-implicit-contracts hypothesis; CEO replacement drives employment and payroll reductions, consistent with the mechanism" }
    - { cite: "Brown, Earle, and Vakhitov (2006)", doi: '10.1086/499547', relation: replicates, note: "corroborates wage declines and job destruction documented for Ukraine; uses matched stacked DiD rather than standard TWFE" }
    - { cite: "Olsson and Tag (2017)", relation: builds-on, note: "prior work by the same authors on private equity, layoffs, and job polarization, extending the matched employer-employee design to privatization" }

  openQuestions:
    - "The paper cannot measure consumer surplus effects from changes in price or quality of goods and services post-privatization, limiting a full social welfare assessment (pp. 2146-2147)."
    - "Government revenues from the sale of state-owned assets are not observable in the anonymous registry data, preventing an exact calculation of the fiscal surplus (p. 2147)."
    - "External validity beyond Sweden and similar advanced economies (Scandinavian countries, large European countries with strong social safety nets) is uncertain; developing-country settings may differ substantially (pp. 2122-2123)."

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full PDF read (pp. 2107-2151); all results extracted with table/figure locators. Not human-verified. Not reproduced. Replication code is referenced in Supporting Information but has not been run here." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; two fixes applied: R7 business-ownership magnitude corrected from 14.7 bps to 6.3 bps (Table III full-period coefficient 0.00063 = 6.3 bps); introducesData: true removed (paper uses existing Statistics Sweden registries, no new dataset introduced)."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13462", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-05-30" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, identification strategy, and estimating equations extracted from the source: enough to know what privatization costs workers and why, without reading all 45 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13462).

## TL;DR

Using Swedish administrative data from 1990 to 2017, the paper traces workers and firms through 553 privatization events involving 70,079 incumbent workers. Privatization raises unemployment by 12% and cuts wages by 5-9%, with losses persisting up to eight years. The Swedish social safety net cushions roughly half the income loss through increased transfers (unemployment benefits and activity support). At the firm level, employment falls 16% and the job destruction rate rises 11 percentage points, while productivity increases 35.7% and profitability improves by 2.1 percentage points. Productivity gains occur only when the CEO is replaced, consistent with governance changes breaching implicit labor contracts and enabling workforce reallocation. Rough cost-benefit calculations show productivity gains from privatization outweigh worker income losses by a factor of two to six.

## Core results

Magnitudes and significance as reported; `*`/`**`/`***` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Workers experience persistent wage declines** after privatization; wages fall 5.8% short-run, 9.3% medium-run, and 8.4% long-run | Table II, p. 2124 | Avg. effect -7.9% (t = -2.96); short run -5.8% (t = -3.47); medium run -9.3% (t = -4.13); long run -8.4% (t = -2.23) |
| R2 | **Unemployment incidence rises persistently** by ~12-14% relative to pre-privatization levels | Table II, p. 2124 | Full period +1.3 pp (t = 5.16), +12.4% vs baseline; short run +1.1 pp (10.5%); medium run +1.2 pp (11.4%); long run +1.5 pp (14.3%) |
| R3 | **Government transfers offset roughly half the wage income loss**; total income drops only 3.5% despite a 7.9% wage cut | Table II, p. 2124 | Transfers up 11.9% (t = 5.82); total income effect -3.5% (t = -1.52) full period; -2.9% to -4.3% in sub-periods |
| R4 | **Firm productivity rises 35.7%** (or 11.5% using log specification); gains driven by the top 75th-90th percentiles | Table V, p. 2134; Table IA.VI | Full period avg. effect +109.5 KSEK (t = 2.77); log-productivity +11.5% (t = 2.03) |
| R5 | **Firm employment falls 16.3%** through higher job destruction, with total payroll down 12.2% | Table V, p. 2134 | Employee count -16.3% (t = -2.82); job destruction rate +10.9 pp (t = 4.92); job creation rate unchanged (t = -1.40); payroll -12.2% (t = -2.15) |
| R6 | **Firm profitability (ROA) improves by 2.1 percentage points** from a near-zero baseline | Table V, p. 2134 | ROA +2.1 pp (t = 1.82), +321.3% from mean of 0.007 |
| R7 | **Business ownership among former SOE workers doubles**, rising ~97-132% over eight years; effect driven by limited liability company formation, not self-employment | Table III, p. 2127 | Business owner rate +6.3 bps (96.8%, t = 3.61) full period; +20 bps long run (131.7%, t = 3.52) |
| R8 | **Productivity gains occur only when the CEO is replaced**; firms where the CEO stays show no productivity improvement | Table VI, p. 2138 | Productivity: CEO leaves +31.4% (t = 2.00); CEO stays +12.8% (t = 0.81); CEO replacement also associated with greater employment and payroll reductions (Table IA.VII) |

**Overall (paper's conclusion).** Privatization leads to a reallocation of human capital that contributes to both an increase in firm-level productivity and losses in income for workers. The productivity gains from privatization exceed the associated worker costs (pre-government transfers) by a factor of two to six. Government transfers total 10-30% of the per-worker productivity gains, implying workers could receive full compensation with a residual surplus remaining for distribution between the new firm owners and the government.

## Theory / model

The paper has no formal structural model. The identification logic rests on an event study difference-in-differences framework under a parallel trends assumption.

**Key hypotheses tested.** Privatization has ex ante ambiguous effects on workers. On one hand, better governance raises labor demand, increasing wages and reducing unemployment, consistent with the firm-level survey evidence in Megginson and Netter (2001). On the other hand, new private owners face a profit motive to replace workers who enjoyed state protection, and the ownership change may breach implicit contracts between managers and workers (Shleifer and Summers (1988)), making labor cost reductions more likely. Prior work documents wage declines in Ukraine (Brown, Earle, and Vakhitov (2006)) and Brazil (Arnold (2022)), while Bastos, Monteiro, and Straume (2014) find wage increases in Portugal due to different wage-setting institutions. The productivity gain mechanism is tested by examining whether productivity increases only when the CEO is replaced, consistent with the governance-and-implicit-contract channel. The matching-plus-stacked-DiD approach extends the design used in Olsson and Tag (2017) on private equity buyouts.

**Identification strategy.** The primary concern is selection bias: SOEs that are privatized may differ systematically from those that remain public. The paper addresses this via:

1. A matched comparison group: each treated worker (or firm) is matched one year before privatization to a similar worker (or firm) that remains state-owned, on age, gender, industry, region, and wage (for workers) or industry, region, size, and ROA sign (for firms).
2. A stacked difference-in-differences design (de Chaisemartin and D'Haultfoeuille (2020), Goodman-Bacon (2021)) to handle heterogeneous treatment effects arising from staggered privatization timing across 1997-2017.
3. Pre-trend testing: event-time plots confirm parallel trends in all outcomes for three years before privatization (Figures 3, 4, 5).

A residual concern is anticipation bias (workers sorting out of SOEs before privatization). The paper addresses this by matching one year before the event, and confirms robustness when matching three years earlier (Table IA.VIII).

## Method

The core estimator is a stacked difference-in-differences regression run in event time, combined with cell matching without replacement.

**Matching.** For workers, each of the 70,079 treated workers is matched to one control worker from the 3.3 million non-privatized SOE worker pool on the Cartesian product of age quartile, gender, industry (four broad NACE groups), NUTS1 region, and wage quartile. The match is one-to-one without replacement, yielding 63,231 pairs.

**Worker-level estimating equation.** Let $$Y_{i,f,k,t}$$ be an outcome for worker $$i$$ at firm $$f$$ in event year $$k$$ and calendar year $$t$$, where $$k = 0$$ is the privatization year. The stacked DiD model (equation 1, p. 2121) is:

$$
Y_{i,f,k,t} = \alpha + \pi \, After_k + \gamma D_i + \beta \, After_k \times D_i + \omega_t + X_i + X_f + \varepsilon_{i,f,k,t} \tag{1}
$$

where $$After_k = 1$$ for $$k \geq 0$$; $$D_i = 1$$ for workers in a privatized SOE (treated) and 0 for matched controls; $$\omega_t$$ is calendar year fixed effects; $$X_i$$ includes individual controls (age, gender, immigrant status, labor market experience, tenure, education, municipality, industry, calendar year, and privatization year fixed effects); $$X_f$$ includes firm age, industry, and region fixed effects. $$\beta$$ is the average intention-to-treat effect.

**Dynamic specification.** To trace the time profile, $$After_k$$ is replaced by event-time dummies $$\tau_k$$ for $$k = -3$$ to $$k = +8$$ (equation 2, p. 2121):

$$
Y_{i,f,k,t} = \alpha + \tau_k + \gamma D_i + \sum_{k=-3}^{k=8} \beta_k \, \tau_k \times D_i + \omega_t + X_i + X_f + \varepsilon_{i,f,k,t} \tag{2}
$$

where $$k - 0$$ is the reference period, so $$\beta_k$$ is the average intention-to-treat effect at event time $$k$$.

**Firm-level equation.** The firm-level analog (equation 3, p. 2122) replaces worker subscripts with firm subscripts; $$X_f$$ includes firm age, industry fixed effects, region fixed effects; standard errors are clustered at the firm level:

$$
Y_{f,t} = \alpha + \pi \, After_k + \gamma D_f + \beta \, After_k \times D_f + \omega_t + X_f + \varepsilon_{f,t} \tag{3}
$$

**Employment growth rates.** Following Davis, Haltiwanger, and Schuh (1998), job flows are computed as (equations 4-6, p. 2133):

$$
g_{f,t} = \frac{E_{f,t} - E_{f,t-1}}{0.5 \times (E_{f,t} + E_{f,t-1})}, \quad JDR_{f,t} = |min\{g_{f,t}, 0\}|, \quad JCR_{f,t} = max\{g_{f,t}, 0\} \tag{4-6}
$$

bounded between -2 (exits) and 2 (entries).

Standard errors are clustered at the municipality level for worker-level regressions and at the firm level for firm-level regressions.

## Empirical specifications

All worker-level results (R1-R3, R7) use equation (1) / (2) on 1,414,270 worker-year observations from 63,231 matched pairs (p. 2124, Table II). Firm-level results (R4-R6, R8) use equation (3) on 4,804 firm-year observations from 368 privatized firms matched to 368 control firms (p. 2134, Table V).

**Wage income (R1).** Dependent variable is the log of annual gross salary income via the inverse hyperbolic sine transformation. The pre-privatization mean is 271,080 SEK (~27,108 USD). The full-period DiD coefficient is -0.079 (t = -2.96), -7.9%. Short-run coefficients: -0.058 (t = -3.47, -5.8%), medium-run: -0.093 (t = -4.13, -9.3%), long-run: -0.084 (t = -2.23, -8.4%). The mechanical unemployment channel accounts for only 16.4% of the observed wage cut.

**Unemployment incidence (R2).** Dependent variable is a binary indicator equal to one if the worker was unemployed at any time during the year. The full-period effect is +0.013 (t = 5.16, +1.3 pp, +12.4% vs baseline mean of 0.105). Short-run: +0.011 pp (t = 4.02); medium-run: +0.012 pp (t = 4.27); long-run: +0.015 pp (t = 5.27).

**Government transfers (R3).** Dependent variable is the log of annual gross government transfers (unemployment benefits, activity support, social benefits) via inverse hyperbolic sine. Full-period effect: +0.119 (t = 5.82, +11.9%). Total income (wages plus transfers): -0.035 (t = -1.52, -3.5%), roughly half the wage loss. Transfers break down as: unemployment benefits +11.1% (t = 7.45), activity support payments +4.3% (t = 6.69), social benefit payouts essentially unchanged (-0.02%, t = 0.23) (Table IA.III).

**Firm productivity and employment (R4-R6).** Productivity (value-added per employee) full-period effect: +109.5 KSEK (t = 2.77, +35.7%), driven by the top 75th-90th percentile; log-productivity: +11.5% (t = 2.03). Employment: -16.3% (t = -2.82). Payroll: -12.2% (t = -2.15). ROA: +2.1 pp (t = 1.82). All effects are present in both short and medium run.

**CEO channel (R8).** The sample is split into privatizations where the CEO remains (column 5, Table VI, N = 2,433 observations) and where the CEO departs (column 6, N = 2,278). Productivity effect: CEO stays +12.8% (t = 0.81, insignificant); CEO leaves +31.4% (t = 2.00, significant). The same split is applied to employment and payroll (Table IA.VII).

**Heterogeneity (Section V, Tables VII-IX).** Partial privatizations (28,694 treated workers) show larger effects: wages -16.5% (t = -4.11), unemployment +2.5 pp (42%, t = 5.77). Foreign buyers lead to unemployment increases of +3.2 pp (32%, t = 8.59) versus +0.5 pp for domestic buyers; total income falls -16.6% with foreign buyers (t = -6.07) versus no change for domestic. MBO privatizations show no statistically significant adverse effects. Triple-difference regressions find no differential effects across industries, high-unemployment regions, or recession years (Table IX).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| LISA database (Statistics Sweden, longitudinal integration database for health insurance and labor market studies) | Individual-level annual data on wages, unemployment, transfers, family structure, education, wealth for all Swedish residents aged 15+, 1990-2017 | no page yet |
| Structural Business Statistics (FEK) database (Statistics Sweden) | Firm-level data on employees, payroll, productivity (value-added per employee), ROA, investment ratio, leverage, 1997-2017 | no page yet |
| Wealth Register (Statistics Sweden) | Individual total wealth, risky assets, cash, and debt, 1999-2007; used for household finance outcomes | no page yet |
| Swedish military draft cognitive/noncognitive skill scores | Quality-of-hire measure for male employees; stanine scales for cognitive and noncognitive ability at enlistment | no page yet |

Sample: Sweden, 1990-2017 (individual data) and 1997-2017 (firm data). 553 privatization events identified between 1997 and 2017. 63,231 matched worker pairs (70,079 treated workers, matched from 3.3 million non-privatized SOE workers). 368 matched privatized firms (368 matched control firms).

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13462) if you are: (i) designing privatization policy and want the cost-benefit arithmetic (Table IA.XVI) and the policy intervention discussion (Section V.D); (ii) studying the role of CEO governance changes in driving firm performance post-ownership-change (Table VI and Table IA.VII); (iii) replicating with the stacked DiD design, which requires the event-specific data sets and the matched control construction; (iv) extending the analysis to household finance and entrepreneurship outcomes (Tables III-IV and Section III.B-B.4); or (v) assessing heterogeneity by privatization type, buyer nationality, or macroeconomic conditions (Tables VII-IX).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4), August 2025. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY-NC 4.0 licence permits non-commercial reuse with attribution; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY-NC 4.0).** Olsson, Martin, and Joacim Tag.
> "What Is the Cost of Privatization for Workers?"
> *The Journal of Finance* 80, no. 4 (August 2025): 2107-2151.
> DOI: 10.1111/jofi.13462. (c) 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
