---
title: "Scope, Scale, and Concentration: Hoberg & Phillips (2025)"
description: >-
  Distilled: Using doc2vec text analysis of firm 10-Ks, Hoberg and Phillips
  document that U.S. firms expanded their product market scope by 50-70% from
  1989 to 2017, primarily through acquisitions and R&D rather than capital
  expenditures, with scope expansion raising firm valuations by 29.5% of the
  interquartile range while leaving traditional Herfindahl-Hirschman Index
  concentration measures flat once scope is accounted for. J. Finance 2025,
  paywalled. Eight core results with source locators, datasets used, the
  method (D2V-Scope), and the empirical specifications with equations.
sidebar:
  label: Hoberg-Phillips 2025
  order: 1
tags: [paper-summary, corporate-finance, industrial-organization, firm-dynamics,
       text-as-data, panel-regression, peer-reviewed, unreplicated,
       data:wrds, data:edgar, data:tnic]
paper:
  authors: Gerard Hoberg, Gordon M. Phillips
  authorList:
    - { family: Hoberg, given: Gerard, orcid: "0000-0001-5104-9689", affiliation: University of Southern California Marshall School of Business }
    - { family: Phillips, given: Gordon M., orcid: "0000-0002-0782-2504", affiliation: Dartmouth College and National Bureau of Economic Research }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 415-466
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13400
  jel:
    codes: [G30, L10, L25]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Corporate Finance and Governance', 'Firm Innovation and Growth', 'Industrial Organization and Market Structure']
  dataAccess: licensed-commercial
  outcome:
    - firm product market scope (D2V-Scope, NAICS-Scope)
    - firm valuation (market-to-book ratio)
    - acquisition and R&D investment rates
    - industry concentration (HHI)
  outcomeClass: [firm-real-outcomes, firm-financing, firm-dynamics]
  license: >-
    Paywalled: Wiley VOR terms and conditions (content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2024-11-04); not CC-licensed.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/Journal of Finance site, checked 2026-06-06)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 55
  methods:
    role: both
    contributes: d2v-scope
    family: descriptive
    buildsFrom: [panel-regression, instrumental-variables, fama-macbeth]
    identification: instrument
  contributionType: [new-fact, measurement]
  mechanisms: [market-power, organizational-complexity]
  scope:
    region: US
    assetClass: US equities (Compustat public firms)
    period: 1989-01..2017-12
    frequency: annual
    dataType: [market, accounting, text]
    granularity: [firm, industry]
    n: "101,535 firm-year observations"
  findings:
    - ref: R1
      outcome: firm product market scope (D2V-Scope)
      metric: level
      value: "D2V-Scope increased from ~6 in 1989 to ~11 in 2017, roughly 50-70% over the sample; NAICS-Scope also increased substantially (Figure 1, p. 434)"
      direction: positive
      vsBenchmark: Compustat segment count flat at ~1.4-1.5 over same period
    - ref: R2
      outcome: firm product market scope (D2V-Scope)
      metric: probability
      value: "53% of all operating industry pairs are in the highest decile of horizontal TNIC similarity; 15.6% in the next decile (Table VII, p. 439)"
      direction: positive
      vsBenchmark: consistent with related (not diversified) scope expansion
    - ref: R3
      outcome: acquisition and R&D investment rates
      metric: pp-effect
      value: "25th to 75th percentile scope increase: acquisition probability rises 6.55 pp (22.7% of mean); divestiture probability falls 4.15 pp (32.9% of mean); R&D/Assets rises 0.82 pp (15.5% of mean); CAPX coefficient insignificant (Table XII, p. 448)"
      direction: positive
      vsBenchmark: no significant CAPX link; scope financed via intangible/redeployable assets
    - ref: R4
      outcome: firm valuation (market-to-book ratio)
      metric: coefficient
      value: "2SLS: Valuation coefficient on D2V-Scope = 0.100 (t=5.22); 25th-75th pct scope increase associated with M/B increase of 0.31, representing 29.5% of IQR and 21% of SD of firm M/B (Table XIII row 1, p. 451)"
      direction: positive
      vsBenchmark: contrast to conglomerate discount in Lang and Stulz (1994) and Berger and Ofek (1995)
    - ref: R5
      outcome: firm valuation (market-to-book ratio)
      metric: coefficient
      value: "Sales growth coefficient on D2V-Scope = 0.034 (t=5.96); Asset growth = 0.046 (t=8.55); OI/Assets coefficient insignificant t=-0.44 (Table XIII rows 2-4, p. 451)"
      direction: positive
      vsBenchmark: positive sales/asset growth but no ROA impact, consistent with expansion into still-profitable but lower-ROA industries
    - ref: R6
      outcome: D2V-Scope predictive power for profitability
      metric: r-squared
      value: "D2V segments in-sample adj R2 = 31.6% vs Compustat 23.7% (OI/Assets); out-of-sample adj R2 D2V = 3.8% vs Compustat 2.9% (Table IX, p. 443)"
      direction: positive
      vsBenchmark: D2V segments more informative than Compustat segments for predicting profitability
    - ref: R7
      outcome: industry concentration (HHI)
      metric: level
      value: "Scope-adjusted HHI flat since 1997 at ~0.11-0.14; traditional SIC HHI increased from ~0.19 to ~0.28 over 1989-2016 (Figure 5, p. 459)"
      direction: none
      vsBenchmark: scope-adjusted HHI does not increase, in contrast to unadjusted HHI trend
    - ref: R8
      outcome: acquisition and R&D investment rates
      metric: coefficient
      value: "Equity issuance coefficient on D2V-Scope = 0.009 (t=7.23); Debt issuance = 0.002 (t=0.73, insignificant); Dividends/Assets = -0.001 (t=-2.22); equity issuance rises 3.1 pp (65.3% of mean) from 25th to 75th percentile scope (Table XV, p. 453)"
      direction: positive
      vsBenchmark: scope expansion financed by equity not debt, consistent with intangible-asset collateral constraint
  resultType: new-finding
  relatesTo:
    - { cite: 'Hoberg and Phillips (2016)', doi: '10.1086/688176', relation: extends, note: 'extends the TNIC text-based industry classification to measure product market scope across multiple industries per firm via doc2vec' }
    - { cite: 'Lang and Stulz (1994)', relation: contradicts, note: 'paper finds scope expansion raises valuations, contradicting the conglomerate discount result' }
    - { cite: 'Berger and Ofek (1995)', doi: '10.1016/0304-405x(94)00798-6', relation: contradicts, note: 'paper finds higher valuation for multi-industry firms, contradicting their diversification discount' }
    - { cite: 'Kim and Kung (2017)', doi: '10.1093/rfs/hhv076', relation: builds-on, note: 'uses their BEA capital flows table methodology to measure localized asset redeployability as the first IV for scope incentives' }
    - { cite: 'Grullon, Larkin, and Michaely (2019)', doi: '10.1093/rof/rfz007', relation: tests, note: 'shows scope-adjusted HHI is flat since 1997, challenging their finding of rising US industry concentration' }
    - { cite: 'Maksimovic and Phillips (2002)', doi: '10.1111/1540-6261.00440', relation: builds-on, note: 'efficiency-based view of multi-industry operations that motivates the scope-expansion-as-NPV-positive hypothesis' }
  openQuestions:
    - "Lack of segment-level sales data for D2V segments requires reliance on textual prevalence as weight rather than actual sales; future work could improve weight accuracy (p. 460)."
    - "Scope data covers only U.S. publicly traded firms; accounting for private and foreign firms could alter concentration conclusions (p. 457)."
    - "Future NLP advances may allow a single-step procedure to identify multiple industry locations from business descriptions, improving parsimony and accuracy (p. 460)."
    - "Scope can increase anticompetitive conduct through product bundling or barriers to entry; distinguishing scope-driven market power from horizontal concentration is left for future research (p. 457, 460)."
  replicationCode:
    status: available
  proposedVocab:
    - { axis: topic, term: economies-of-scope, def: "Cost or revenue complementarities allowing a firm to operate efficiently across related product markets.", aliases: [scope-economies, multi-market-scope] }
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full PDF read (pp. 415-466, all tables and figures); DOI confirmed via Crossref; OpenAlex enrichment fetched. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all 8 Core results rows confirmed (Tables VII, IX, XI-XIII, XV and Figures 1, 4-5); equations 1-5 and B1 checked term-by-term; one fix: erroneous topics entry 'Italy: Economic History and Contemporary Issues' corrected to 'Industrial Organization and Market Structure'." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13400", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-11-04; NOT CC-licensed, paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the new D2V-Scope measure it constructs, and the two-stage instrumental variable framework used to identify the effect of scope on corporate policies and performance: enough to know what it found and how, without reading the full 52 pages. To replicate or extend it, read the full source at [doi.org/10.1111/jofi.13400](https://doi.org/10.1111/jofi.13400).

## TL;DR

Hoberg and Phillips use doc2vec text analysis of firm 10-Ks to measure firm product market scope across 300 D2V industries. The average U.S. firm's scope increased by roughly 50 to 70% from 1989 to 2017, driven primarily by acquisitions and R&D rather than capital expenditures, while Compustat segment counts stayed flat. Scope expansion is positively related to firm valuation (a 25th-to-75th percentile scope increase raises market-to-book by 0.31, or 29.5% of the interquartile range), contradicting the conglomerate discount in the prior literature. Traditional industry concentration (HHI) appears to rise over this period, but scope-adjusted HHI is flat since 1997, suggesting that firms increasingly compete across more overlapping markets.

## Core results

Magnitudes and significance are as reported; `\*` = 5%, `\*\*` = 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Average D2V-Scope increased roughly 50-70%** from 1989 to 2017 while Compustat segment counts remained flat | Figure 1 (middle and upper panels), p. 434 | D2V-Scope rises from ~6 to ~11; NAICS-Scope also rises; Compustat segments stable at ~1.4-1.5 |
| R2 | **Modern multi-industry firms operate in closely related industries**: 53% of all operating industry pairs are in the highest horizontal TNIC similarity decile | Table VII, Panel A, p. 439 | 52.8% of pairs (all firms) in most-similar decile; 15.6% in next decile; least-similar decile only 1.7% |
| R3 | **Scope incentives raise acquisitions and R&D but not CAPX**: 2SLS using peer-based redeployability and opportunity set as instruments | Table XII, pp. 447-448 | Acquisition probability +6.55 pp (t=3.5); Divestiture -4.15 pp (t=-2.9); R&D/Assets +0.82 pp (t=3.4); CAPX coefficient = 0.000, t=-0.06 |
| R4 | **Scope expansion increases firm valuation** by 0.31 M/B points from 25th to 75th percentile, representing 29.5% of the interquartile range | Table XIII row 1, p. 451 | 2SLS coefficient on D2V-Scope = 0.100 (t=5.22); contradicts the conglomerate discount of Lang and Stulz (1994) and Berger and Ofek (1995) |
| R5 | **Scope raises sales and asset growth but not ROA**, consistent with expansion into still-profitable but lower-profitability industries | Table XIII rows 2-4, p. 451 | Sales growth coefficient = 0.034 (t=5.96); Asset growth = 0.046 (t=8.55); OI/Assets = -0.001 (t=-0.44, n.s.) |
| R6 | **D2V segments are more informative than Compustat segments** for predicting profitability in-sample and out-of-sample | Table IX, p. 443 | D2V adj R2 = 31.6% vs Compustat 23.7% (OI/Assets, in-sample); out-of-sample D2V adj R2 = 3.8% vs Compustat 2.9% |
| R7 | **Scope-adjusted HHI is flat since 1997**; the apparent rise in traditional HHI is explained by firms operating in more overlapping markets | Figures 4, 5, pp. 458-459 | Scope-adjusted HHI stable at ~0.11-0.14 since 1997; traditional SIC HHI rose from ~0.19 to ~0.28 over 1989-2016 |
| R8 | **Scope expansion is financed by equity issuance, not debt**, consistent with intangible and redeployable assets lacking collateral value | Table XV, p. 453 | Equity issuance +3.1 pp (65.3% of mean) from 25th to 75th pct scope (t=7.23); Debt issuance coefficient = 0.002 (t=0.73, n.s.) |

**Overall (paper's conclusion).** The 21st-century firm is a high-scope firm that serves multiple related product markets through flexible production, innovation, and acquisition, all without increasing formal Compustat segments. This scope expansion creates value, is consistent with economies of scope (not agency-driven conglomeration), and, once accounted for, explains most of the apparent rise in industry concentration. Traditional Compustat-based measures substantially understate the scope of modern U.S. firms.

## Theory / model

The paper has no formal structural model. Its theoretical motivation draws on the economies-of-scope literature (Panzar and Willig (1977, 1981); Teece (1980); Maksimovic and Phillips (2002)) and the agency-cost view of diversification (Jensen (1986); Lang and Stulz (1994); Berger and Ofek (1995)). The paper empirically distinguishes between two views:

1. **Scope-as-synergy**: Firms with redeployable assets and related product-market opportunities expand scope at low cost, generating positive NPV. This predicts higher valuations for high-scope firms.
2. **Scope-as-agency**: Managers empire-build into unrelated markets, generating a diversification discount. This predicts lower valuations.

The paper's findings support the synergy view. The paper additionally models Compustat segment underreporting: managers evaluating related industries holistically do not report them as separate segments, so segment counts do not rise with scope. This is confirmed by a regression (Table VI, p. 436) showing that Compustat segments are negatively associated with the number of highly related D2V industry pairs a firm operates in (average coefficient -0.019, t=-4.32), while positively associated with weakly related (average coefficient 0.166, t=6.41) and unrelated pairs.

**Identification.** The paper uses a two-stage instrumental variable (2SLS) strategy (described in Section V.A-B, pp. 446-450). The two instruments for scope are:

- **Sectoral Redeployment Potential**: the average cosine similarity of the asset utilization vectors between the NAICS industry of the focal firm's close peers and the NAICS industries of the firm's more distant peers, following the BEA capital flows methodology of Kim and Kung (2017). High values mean close-peer assets can be cheaply redeployed to distant-peer markets (eq. 3, p. 423). First-stage coefficient = 1.156 (t=3.74; Table XI row 1, p. 447).
- **Sectoral Opportunity Set Potential**: one minus the HHI of the NAICS industries served by the focal firm's distant peers (eq. 4, p. 424). High values mean distant peers span a wide set of markets, indicating a thick scope-expansion opportunity set. First-stage coefficient = 2.124 (t=11.94; Table XI row 1, p. 447).

Both instruments are constructed from characteristics of peers who are not the focal firm itself, reducing first-degree endogeneity concerns.

## Method

**D2V-Scope construction** (the paper's headline methodological contribution; Appendix B, pp. 463-464). The measure uses a doc2vec embedding model trained on 10-K Item 1 business descriptions from all Compustat firms in the base year 1997. The 300-dimensional vector space represents each firm's product offering. Five steps:

1. Run k-means clustering on single-segment firm vectors to identify 450 candidate industries; add word2vec dialects (vocabulary) for each cluster.
2. Prune 150 boilerplate or redundant clusters to obtain 300 D2V industries.
3. Compute term-specific weights $$w_{k,n}$$ for each word $$n$$ in industry $$k$$ as:

$$
w_{k,n} = (\text{cosine similarity of word } n \text{ to centroid } k) \times (\text{word-specific HHI across industries}) \tag{B.Step 3}
$$

4. Compute each firm $$i$$'s exposure to industry $$k$$ in year $$t$$ (equation B1, p. 464):

$$
E_{i,k,t} = \frac{\sum_{n=1}^{N} B_{i,k,n,t} \cdot w_{k,n}}{\sum_{n=1}^{N} w_{k,n}} \tag{B1}
$$

where $$B_{i,k,n,t} = 1$$ if the firm uses word $$n$$ of industry $$k$$'s dialect in year $$t$.

5. Tag firm $$i$$ as operating in industry $$k$$ if $$E_{i,k,t} \geq \bar{E}$$, where the threshold $$\bar{E}$$ is fixed at the 2% granularity level from the 1997 base year. D2V-Scope is the count of industries exceeding this threshold.

**Alternative: NAICS-Scope** (Section II.A.2, pp. 421-422) uses 311 four-digit NAICS industry descriptions from the 2017 NAICS manual. The overlap ratio for firm $$i$$ in industry $$j$$ in year $$t$$ is (equation 1, p. 421):

$$
Q_{i,j,t,\text{NAICS}} = \frac{\#\text{words overlapping in } D_{\text{NAICS},j} \text{ and } V_{i,t}}{\#\text{words in } D_{\text{NAICS},j}} \tag{1}
$$

NAICS-Scope is then the count of industries above a fixed threshold $$\bar{Q}_{\text{NAICS}}$$ (eq. 2, p. 422):

$$
\text{NAICS-Scope}_{i,t} = \sum_{j=1}^{K} \text{Indicator}\{Q_{i,j,t,\text{NAICS}} > \bar{Q}_{\text{NAICS}}\} \tag{2}
$$

**Redeployability instruments.** Local asset redeployability is the weighted average cosine similarity of asset utilization vectors across industries spanned by close and distant peers (equation 3, p. 423):

$$
\text{LocalAssetRedep}_{i,t} = \sum_{j,k: s,t, j \neq k \in \text{NAICS-4}} F_{i,t,j,\text{near}} \cdot F_{i,t,k,\text{distant}} \left\langle \frac{A_j}{A_j \cdot \mathbf{1}} \cdot \frac{A_k}{A_k \cdot \mathbf{1}} \right\rangle \tag{3}
$$

The opportunity set instrument is one minus the HHI of the distribution of distant-peer NAICS-4 industries (equation 4, p. 424):

$$
\text{LocalScopeExpOppSet}_{i,t} = 1 - \sum_{j \in \text{NAICS-4}} F_{i,t,j,\text{distant}}^2 \tag{4}
$$

## Empirical specifications

All regressions include firm and year fixed effects; standard errors are clustered by firm. The headline two-stage specification (Sections V.B and V.C, pp. 446-453) is:

**First stage** (Table XI, p. 447): For firm $$i$$ and year $$t$$,

$$
\text{Scope}_{i,t} = \alpha + \beta_1 \cdot \text{SectRedepPot}_{i,t} + \beta_2 \cdot \text{SectOppSetPot}_{i,t} + \gamma X_{i,t-1} + \mu_i + \mu_t + \varepsilon_{i,t} \tag{FS}
$$

where $$X_{i,t-1}$$ includes log assets, log age, market-to-book (in some specs), and TNIC HHI. With D2V-Scope as the dependent variable: $$\hat{\beta}_1 = 1.156$$ (t=3.74), $$\hat{\beta}_2 = 2.124$$ (t=11.94). The instruments are strong (Kleibergen-Paap r-k statistic significant at 1%) and Hansen J-tests are not rejected at 5% for most outcome variables.

**Second stage** (Tables XII-XV, pp. 448-453): The instrumented scope variable is used as the regressor in the outcome equation:

$$
y_{i,t} = \alpha + \delta \cdot \widehat{\text{Scope}}_{i,t} + \gamma X_{i,t-1} + \mu_i + \mu_t + \varepsilon_{i,t} \tag{SS}
$$

Key second-stage results with D2V-Scope instrumented:

- **Investment** (Table XII): Acquirer dummy $$\hat{\delta}$$ = 0.019 (t=3.45); Target dummy = -0.012 (t=-2.89); R&D/Assets = 0.002 (t=3.40); CAPX/Assets = 0.000 (t=-0.06); Vertical integration = 0.002 (t=12.88).
- **Outcomes** (Table XIII): Valuation = 0.100 (t=5.22); Sales growth = 0.034 (t=5.96); Asset growth = 0.046 (t=8.55); OI/Assets = -0.001 (t=-0.44).
- **Financing** (Table XV): Equity issuance = 0.009 (t=7.23); Debt issuance = 0.002 (t=0.73); Dividends/Assets = -0.001 (t=-2.22).

**Profitability validation** (Table IX, p. 443): Generalized fixed effects model estimating industry-level profitability parameters $$\mu_{k,t}$$:

$$
\text{OIassets}_{i,t} = \sum_{k=1}^{300} \omega_{i,k,t} \cdot \mu_{k,t} + \varepsilon_{i,t} \tag{5}
$$

where $$\omega_{i,k,t}$$ is the textual exposure weight for D2V (or the fraction of sales for Compustat). D2V segments yield in-sample adjusted R2 of 31.6% vs. 23.7% for Compustat on single-segment firms (OI/Assets).

**Scope-concentration link** (Section VI, pp. 455-459): Scope-adjusted HHIs computed using D2V industry assignments and textual-intensity weights; scope-adjusted HHI is flat since 1997 (Figures 4 and 5), while traditional SIC HHI rises. A secondary granularity-based approach loads firm product descriptions onto SIC-2 (broad) vs. SIC-3 (narrow) vocabulary over time, confirming firms operate at coarser granularity in later years.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Compustat annual fundamentals (WRDS) | Assets, R&D, CAPX, profitability, segments, financing; main panel 1989-2017 | [WRDS](/wiki/licensed/wrds/) (licensed) |
| SEC EDGAR 10-K filings (Item 1) | Source text for D2V-Scope and NAICS-Scope construction; all Compustat firm-years with 10-K | [EDGAR](/wiki/datasets/edgar/) |
| TNIC / Hoberg-Phillips (2016) | Industry classification for peer identification; pairwise similarity used for instruments and scope validation | [TNIC](/wiki/datasets/tnic/) |
| SDC Platinum | Acquisition and divestiture events (acquirer dummy, target dummy) | [no page yet] |
| BEA capital flows tables (1997) | 180-asset utilization vectors for 123 BEA industries, used to compute local asset redeployability instrument | [no page yet] |
| Venture Expert (VentureXpert) | VC funding similarity measure: startup business descriptions for computing VC funding similarity | [no page yet] |
| NAICS Manual (2017) | 963-page NAICS manual with 311 four-digit industry descriptions used to construct NAICS-Scope | [no page yet] |

Sample: 101,535 firm-year observations, 1989-2017 annual. SIC 6000-6999 (financials) and 4900-4949 (utilities) excluded. Firms required to have sales and assets of at least $1 million in both current and prior year.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13400) if you are: constructing D2V-Scope or NAICS-Scope measures (Appendix B gives the full five-step algorithm); studying the relationship between firm scope and industry concentration; testing whether scope-adjusted HHI changes the interpretation of the rising-concentration literature (Grullon, Larkin, and Michaely (2019)); or using the peer-based redeployability and opportunity set instruments for scope endogeneity. The locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. Pages 415-466. DOI: 10.1111/jofi.13400. Published by Wiley on behalf of the American Finance Association. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled; only extracts are reproduced here under fair-use commentary.

> Hoberg, Gerard, and Gordon M. Phillips. "Scope, Scale, and Concentration: The 21st-Century Firm."
> *The Journal of Finance* 80, no. 1 (February 2025): 415-466.
> DOI: 10.1111/jofi.13400. © 2024 the American Finance Association.
> Paywalled. This page is an extract-only summary by the Institute for Automated Research.
