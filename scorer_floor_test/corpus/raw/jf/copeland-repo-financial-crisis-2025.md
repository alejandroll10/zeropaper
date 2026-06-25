---
title: "Repo over the Financial Crisis: Copeland & Martin (2025)"
description: >-
  Distilled: Using new confidential data covering all four segments of the U.S.
  repo market (bilateral and tri-party, interdealer and dealer-to-client), this
  paper documents that the 2008 decline in repo activity was largest in bilateral
  (MIX) segments and disproportionately concentrated in Treasury-backed repos,
  and was driven by a pullback in securities-driven market-making trades rather
  than by counterparty credit concerns. J. Finance 2025, U.S. Government work /
  public domain. Six core results with source locators, datasets used, and the
  empirical specifications.
sidebar:
  label: Copeland-Martin 2025
  order: 1
tags: [paper-summary, repo-markets, financial-crisis, market-microstructure,
       money-markets, panel-regression, peer-reviewed, unreplicated,
       data:fr2004c, data:ficc-gcf-repo, data:markit-cds]
paper:
  authors: Adam Copeland and Antoine Martin
  authorList:
    - { family: Copeland, given: Adam, orcid: "0000-0001-6906-6241", affiliation: Federal Reserve Bank of New York }
    - { family: Martin, given: Antoine, orcid: "0000-0002-3263-7669", affiliation: Swiss National Bank }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 911–936
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13406
  jel:
    codes: [G01, G12, G23]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Banking stability, regulation, efficiency', 'Global Financial Crisis and Policies', 'Economic Theory and Policy']
  dataAccess: proprietary-confidential
  outcome:
    - repo activity by market segment and asset class
    - association between dealer counterparty risk and MIX repo volume
    - correlation between repo and reverse repo flows by segment
  outcomeClass: [bank-funding, asset-prices]
  license: >-
    U.S. Government work, public domain in the USA (stated p. 911: "This article
    is a U.S. Government work and is in the public domain in the USA."). Crossref
    DOI metadata records license URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor (content-version vor,
    delay-in-days 0, start 2025-02-10), which is the Wiley standard paywalled
    terms; the public-domain assertion on the artifact takes precedence for U.S.
    readers.
  licenseShort: U.S. Government work (public domain, USA)
  access: paywalled
  machineAccess: blocked-paywall (Wiley site, 2026-06-06)
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 4

  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [panel-regression]
    identification: descriptive

  contributionType: [new-fact, new-data]
  introducesData: true

  mechanisms: [intermediary-constraint, liquidity]

  scope:
    region: US
    assetClass: US repo market (Treasury, agency debt, agency MBS, corporate bonds)
    period: 2008-07..2008-12
    frequency: weekly
    dataType: [administrative, market]
    granularity: [firm, transaction]
    n: "18 primary dealers, 21 weeks (378 observations); aggregate FR 2004C weekly 2004-2013"

  findings:
    - ref: R1
      outcome: repo activity by market segment and asset class
      metric: pp-effect
      value: "Total repo fell from $4,646B (pre-crisis) to $3,848B (crisis), -17%; Treasury repo fell -20% ($470B); All-other asset classes fell -15% ($328B)"
      direction: negative
      vsBenchmark: Treasury repo declined more than all-other asset classes despite flight-to-quality narrative (Table I, p. 920)
    - ref: R2
      outcome: repo activity by market segment and asset class
      metric: pp-effect
      value: "MIX ID segment: -24%; MIX DtC segment: -31%; GC ID segment: +7%; GC DtC segment: -10%; Treasury MIX ID: -23%; Treasury MIX DtC: -37%; Treasury GC ID: +52%; Treasury GC DtC: +7%"
      direction: mixed
      vsBenchmark: Bilateral (MIX) segments contracted sharply while GC (tri-party) segments held up or grew (Table II, p. 921)
    - ref: R3
      outcome: association between dealer counterparty risk and MIX repo volume
      metric: coefficient
      value: "CDS regression: coeff on delta CDS = -3.757 (SE 12.733), insignificant; R-squared = 0.029 (Table IV, col 1, p. 925); CP regression: coeff on CP = 0.0346 (SE 0.0554), insignificant (Table V, col 1, p. 927)"
      direction: none
      vsBenchmark: No statistically significant link between dealer credit-risk measures and MIX repo; counterparty credit concerns not the driver
    - ref: R4
      outcome: correlation between repo and reverse repo flows by segment
      metric: coefficient
      value: "Pre-crisis: MIX Repo on MIX Revr coeff = 0.59*** (SE 0.10); crisis period interaction PL x delta MIX Revr = -0.17 (SE 0.11, insignificant); DtC GC: PL x delta MIX Revr = 0.20** (SE 0.09) (Table VI, p. 929)"
      direction: mixed
      vsBenchmark: MIX repo-reverse-repo correlation falls for large dealers post-Lehman; DtC GC correlation rises, indicating pivot to cash-driven trades
    - ref: R5
      outcome: correlation between repo and reverse repo flows by segment
      metric: coefficient
      value: "Large dealer interaction: PL x Large x delta MIX Revr = -0.60* (SE 0.33); PL x Large x delta MIX Revr for DtC GC = 0.70** (SE 0.30) (Table VII, p. 931)"
      direction: mixed
      vsBenchmark: Large dealers drive the change; small dealers show no significant shift in strategy
    - ref: R6
      outcome: repo activity by market segment and asset class
      metric: level
      value: "On-the-run Treasury repo fell from $286B (Q2 2008) to $131B (Q4 2008), a decline of $155B (Figure 4, p. 933)"
      direction: negative
      vsBenchmark: Confirms securities-driven market-making as the source of decline; on-the-run Treasuries are almost exclusively used in securities-driven trades

  resultType: new-finding

  relatesTo:
    - { cite: 'Gorton and Metrick (2012)', doi: '10.1016/j.jfineco.2011.03.016', relation: contradicts, note: 'GM document rising haircuts as evidence of a generalized run on repo; this paper finds the bilateral decline was not driven by counterparty credit risk and that Treasury repo (the safest) fell most' }
    - { cite: 'Gorton, Metrick, and Ross (2020)', doi: '10.1257/pandp.20201100', relation: tests, note: 'GMR document a large decline in net repo funding to banks; this paper provides segment-level decomposition showing most of the decline is in MIX (bilateral) segments' }
    - { cite: 'Copeland, Martin, and Walker (2014)', doi: '10.1111/jofi.12205', relation: extends, note: 'prior work showed tri-party repo (DtC GC) held up; this paper adds the bilateral MIX segments and interdealer data to give a comprehensive cross-segment view' }
    - { cite: 'Krishnamurthy, Nagel, and Orlov (2014)', doi: '10.1111/jofi.12168', relation: extends, note: 'prior work analyzed DtC funding trades in TPR; this paper adds the MIX segment and shows MIX had far larger declines' }
    - { cite: 'Musto, Nini, and Schwarz (2018)', doi: '10.1093/rfs/hhy022', relation: cites, note: 'document price effects (illiquidity of Treasuries); this paper documents the corresponding quantity decline in securities-driven Treasury repo' }

  openQuestions:
    - "Whether the decline was due to clients reducing risk-taking or to a problem in dealers' intermediation capacity cannot be determined from quantities alone; future research should disentangle these two channels (p. 934)."
    - "The paper considers quantities only; the associated price effects (illiquidity of Treasuries) are documented elsewhere and the interaction between quantity and price dynamics is not modeled (p. 913)."

  replicationCode:
    status: available

  proposedVocab:
    - { axis: topic, term: repo-markets, def: "Repurchase agreement (repo) market structure, activity, and stress; covers bilateral, tri-party, GC, and MIX segments.", aliases: [repo-market, repurchase-agreements] }
    - { axis: topic, term: money-markets, def: "Short-term funding markets including repo, commercial paper, and money-market funds.", aliases: [short-term-funding, wholesale-funding] }

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 911-936); six results extracted from the PDF. Not human-verified. Not reproduced. Replication code is referenced in the paper (Supporting Information) but has not been run here." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against source PDF (Tables I-VII, Figure 4, equations 1-9, pp. 920-931, 933); one fix applied: Treasury repo dollar decline corrected from -$472B to -$470B (Table I, p. 920); all other locators, magnitudes, signs, and equation terms confirmed correct." }

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13406
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-02-10. Artifact p.911 states: 'This article is a U.S. Government work and is in the public domain in the USA.' Crossref URL is Wiley standard paywalled terms; public-domain statement on artifact takes precedence for US readers."

  rightsSignalConflict: true
---

**What this is.** The paper's core results, the data sources it introduces, and
the empirical specifications it runs: enough to know what it found and how,
without reading all 26 pages. To replicate or extend it, read the original at
[doi.org/10.1111/jofi.13406](https://doi.org/10.1111/jofi.13406).

## TL;DR

Using new confidential data that cover all four segments of the U.S. repo
market (interdealer and dealer-to-client, general collateral and mixed), the
paper documents three facts about the 2007-2009 Global Financial Crisis: (1)
the decline in repo activity was far larger in bilateral (MIX) segments than
in tri-party (GC) segments; (2) more than half the decline was
concentrated in Treasury-backed repos, the safest and most liquid asset class,
contradicting the flight-to-quality narrative; and (3) the decline was
not correlated with measures of dealer counterparty credit risk (CDS spreads,
CP rates), but was instead driven by a pullback in securities-driven
market-making trades by large securities dealers. The paper uses a
securities-dealer panel and a seemingly unrelated regression (SUR) design
to trace the repo decline to a reduction in back-to-back securities-driven
trades entered by large dealers, particularly after the Lehman Brothers
bankruptcy.

## Core results

Magnitudes and significance are as reported; `\*` = 10%, `\*\*` = 5%, `\*\*\*` = 1%. Locators
point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Treasury repo fell more than other asset classes** despite the flight-to-quality narrative | Table I, p. 920 | Total repo -17% (-$798B pre-crisis to crisis); Treasury -20% (-$470B); All others -15% (-$328B); agency MBS only -1% |
| R2 | **MIX (bilateral) segments contracted sharply; GC (tri-party) segments were stable or grew** | Table II, p. 921 | MIX ID: -24%; MIX DtC: -31%; GC ID: +7%; GC DtC: -10%. For Treasuries: MIX ID: -23%; MIX DtC: -37%; GC ID: +52%; GC DtC: +7% |
| R3 | **CDS and CP spreads have no statistically significant association with MIX repo activity**; counterparty credit concerns do not explain the decline | Table IV, p. 925; Table V, p. 927 | CDS coeff = -3.757 (SE 12.733), p>0.10; R² = 0.029. CP coeff = 0.035 (SE 0.055), p>0.10 |
| R4 | **Post-Lehman, the association between MIX repo and MIX reverse repo falls, while MIX reverse repo and DtC GC repo become correlated** for large dealers, indicating a pivot to cash-driven trades | Table VI, p. 929 | PL × delta MIX Revr coeff in MIX repo: -0.17 (insig.); PL × delta MIX Revr coeff in DtC GC repo: 0.20\*\* (SE 0.09) |
| R5 | **Large dealers drive the change**: the post-Lehman drop in securities-driven repo is concentrated among above-median dealers | Table VII, p. 931 | PL × Large × delta MIX Revr in MIX repo: -0.60\* (SE 0.33); in DtC GC repo: +0.70\*\* (SE 0.30); no significant change for small dealers |
| R6 | **On-the-run Treasury repo, a direct proxy for securities-driven trades, fell $155 billion** (54%) from Q2 to Q4 2008; this decline is concentrated at large dealers | Figure 4, p. 933 | From $286B (Q2 2008) to $131B (Q4 2008); distribution narrows, with the 75th percentile falling more than the median or 25th percentile |

**Overall (paper's conclusion).** The massive decline in repo over the
financial crisis was driven primarily by a pullback in securities-driven trades
that support Treasury market-making by securities dealers, not by a generalized
disruption in funding conditions or by clients fleeing dealers out of
counterparty credit concerns. Copeland and Martin (2025) and Copeland, Martin,
and Walker (2014) jointly show that the GC (funding) segment remained stable,
so funding disruptions did occur but were institution-specific (Bear Stearns,
Lehman Brothers), not market-wide. The extent of true funding disruption was
considerably smaller than the decline in overall repo activity implies.

## Theory / model

The paper has no formal model. Its identification strategy rests on the
institutional structure of the repo market: the U.S. repo market is segmented
into four segments that differ in clearing platform and in whether they
accommodate securities-driven versus cash-driven trades (pp. 914-915).

**Key institutional distinction.** The general collateral (GC) segment
settles on the tri-party platform. By design, all GC trades are
cash-driven: parties agree only on an asset class, not a specific security,
so the GC segment cannot support securities-driven price-discovery trades.
The mixed (MIX) bilateral segment accommodates both cash-driven and
securities-driven trades. This segmentation means that changes in
MIX activity capture changes in both motives, while changes in GC activity
capture only changes in cash-driven (funding) motives.

**Tested hypotheses.** Given the segmentation above, the paper tests three
hypotheses:

1. Whether the decline in repo was disproportionately in MIX (bilateral)
   versus GC (tri-party) segments. Gorton and Metrick (2012) and Gorton,
   Metrick, and Ross (2020) document large aggregate haircut increases and
   net-repo declines at banks; Copeland, Martin, and Walker (2014) and
   Krishnamurthy, Nagel, and Orlov (2014) find that DtC GC (tri-party)
   activity held up. This paper unifies both views by showing MIX segments
   drove most of the decline.
2. Whether the decline was correlated with measures of dealer counterparty
   credit risk (a "run on repo" hypothesis in the spirit of Gorton and
   Metrick (2012)).
3. Whether, post-Lehman, the statistical association between dealers' MIX
   repo and MIX reverse repo weakened while the MIX reverse repo and DtC GC
   repo association strengthened (a pivot-to-cash-driven-trades hypothesis).
   Musto, Nini, and Schwarz (2018) document the corresponding price effects
   in Treasuries; this paper documents the associated quantity decline in
   securities-driven Treasury repo.

## Method

The paper applies two estimation strategies: aggregate descriptive comparisons
across periods and segments, and a dealer-level panel regression.

**Aggregate analysis.** Using FR 2004C data (a weekly Federal Reserve survey of
primary dealers) plus FICC GCF Repo and FICC DVP service data, the paper
constructs average daily repo outstanding by segment and asset class for the
pre-crisis period (July 1 to September 13, 2008) and the crisis period
(October 15 to December 17, 2008), then computes differences. This is a
descriptive before-after comparison with no causal identification design
(p. 919).

**Dealer-level panel: counterparty credit risk.** The paper estimates four
OLS regressions (equations 1-4, p. 924) relating changes in MIX repo to
contemporaneous or lagged changes in CDS spreads, plus Treasury-related
controls. Standard errors are clustered at the dealer level (18 dealers, 21
weeks, 378 observations). The specifications are (pp. 924-926):

$$
\Delta \text{MIXRepo}_{i,t} = \alpha_0 + \alpha_1 \Delta \text{CDS}_{i,t} + \Delta X_t \beta_0 + \varepsilon^1_{i,t} \tag{1}
$$

$$
\Delta \text{MIXRepo}_{i,t} = \alpha_2 + \alpha_3 \Delta \text{CDS}_{i,t-1} + \Delta X_t \beta_1 + \varepsilon^2_{i,t} \tag{2}
$$

and log-level variants (equations 3 and 4). The CP spread regressions
(equations 5 and 6, p. 926) are:

$$
\log(\text{MIXRepo})_{i,t} = \alpha_0 + \beta_0 \text{CP}_{i,t} + \log X_t \gamma_0 + \eta_i + \varepsilon^1_{i,t} \tag{5}
$$

$$
\Delta \log(\text{MIXRepo})_{i,t} = \alpha_1 + \beta_1 \Delta \text{CP}_{i,t} + \Delta \log X_t \gamma_1 + \varepsilon^2_{i,t} \tag{6}
$$

**Dealer-level panel: repo flow analysis.** The paper estimates a seemingly
unrelated regression (SUR) system (equations 7-9, p. 928) with three
left-hand side variables: change in MIX repo, change in DtC GC repo,
and change in ID GC repo. The key right-hand side variables are MIX
reverse repo and ID GC reverse repo, interacted with a post-Lehman
dummy (PL) to allow strategies to differ across the two periods:

$$
\Delta \text{MIXRepo}_{j,t} = \alpha_0 + \alpha_1 \Delta \text{MIXRevr}_{j,t} + \alpha_2 PL_t + \alpha_3 PL_t \cdot \Delta \text{MIXRevr}_{j,t} + \Delta X_t \beta_0 + \varepsilon^0_{j,t} \tag{7}
$$

$$
\Delta \text{DtC\text{-}GCRepo}_{j,t} = \alpha_4 + \alpha_5 \Delta \text{MIXRevr}_{j,t} + \alpha_6 \Delta \text{ID\text{-}GCRevr}_{j,t} + \alpha_7 PL_t + \alpha_8 PL_t \cdot \Delta \text{MIXRevr}_{j,t} + \alpha_9 PL_t \cdot \Delta \text{ID\text{-}GCRevr}_{j,t} + \Delta X_t \beta_1 + \varepsilon^1_{j,t} \tag{8}
$$

$$
\Delta \text{ID\text{-}GCRepo}_{j,t} = \alpha_{10} + \alpha_{11} \Delta \text{MIXRevr}_{j,t} + \alpha_{12} \Delta \text{ID\text{-}GCRevr}_{j,t} + \alpha_{13} PL_t + \alpha_{14} PL_t \cdot \Delta \text{MIXRevr}_{j,t} + \alpha_{15} PL_t \cdot \Delta \text{ID\text{-}GCRevr}_{j,t} + \Delta X_t \beta_2 + \varepsilon^2_{j,t} \tag{9}
$$

SUR allows correlated error terms across the three equations. Standard
errors are clustered at the dealer level. The 288-observation sample
reflects 18 dealers over the full weekly sample. Table VII repeats the
cross-sectional analysis with dealer-size and domestic/foreign dummy
interactions.

## Empirical specifications

**Sample.** Dealer-level weekly data covering July 1 to December 17, 2008
(excluding two quarter-end weeks and the week of Lehman's bankruptcy),
leaving 21 weeks and 18 primary dealers (378 observations for the CDS panel,
288 for the SUR after excluding Lehman Brothers). The pre-crisis period is
July 1 to September 13; the crisis period is October 15 to December 17.

**Counterparty-risk regressions (R3).** OLS with four specifications
(level and log, contemporaneous and lagged CDS; level and change in CP).
Controls: net Treasury bill issuance, net coupon issuance, Federal Reserve
SOMA operations, total UST holdings by the Fed. Standard errors clustered
at the dealer level. The R-squared statistics are very low (0.013-0.031),
and all CDS and CP coefficients are statistically insignificant, confirming
no systematic relationship between dealer risk measures and MIX repo
(Tables IV-V, pp. 925, 927).

**SUR repo-flow regressions (R4, R5).** The identifying variation is the
differential post-Lehman change in the association between a dealer's
repo and reverse repo activity across segments. The PL interaction terms
capture this change. The null hypothesis tested is that these associations
did not change after Lehman; rejection implies dealers shifted strategies.
Table VII adds size (large vs small) and location (domestic vs foreign)
dummies to capture heterogeneous responses (p. 930).

**On-the-run Treasury repo (R6).** Using the FR 2004SI survey (a
special-purpose data collection), the paper tracks repo involving
specifically identified on-the-run Treasuries, which are almost never used
in cash-driven transactions. The time series of aggregate on-the-run
Treasury repo and the cross-sectional distribution across dealers are
plotted in Figure 4 (p. 933) as direct evidence of the securities-driven
trade decline.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| FR 2004C (Federal Reserve weekly survey of primary dealers) | Primary source for repo and reverse repo outstanding by asset class; covers all primary dealers at weekly frequency, 2004-2013 | No page yet |
| FICC GCF Repo Service data (dealer-level daily, licensed via FRBNY) | Interdealer GC segment repo and reverse repo by asset class at dealer level | No page yet |
| FICC DVP Service data (aggregate-level daily) | Interdealer MIX segment repo; aggregate only | No page yet |
| DtC TPR (tri-party repo) data (confidential, from FRBNY) | Dealer-to-client GC segment repo by dealer and asset class | No page yet |
| Markit Group CDS spreads (five-year modified restructuring, USD) | Proxy for dealer counterparty credit risk; matched to 13 of 18 dealers | [Markit CDS](/wiki/licensed/markit-cds/) (licensed) |
| DTCC commercial paper interest rates (confidential) | Dealer-level weekly CP interest rates; proxy for dealer counterparty risk | No page yet |
| FR 2004SI (special-purpose survey) | On-the-run Treasury repo activity by primary dealer; direct proxy for securities-driven trades | No page yet |

Sample: second half of 2008 (July-December) for dealer-level analysis;
2004-2013 for aggregate FR 2004C time series. Weekly frequency. 18-19
primary dealers (Lehman excluded from panel analysis).

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13406) if you are: analyzing
the drivers of repo market stress during the 2007-2009 GFC; studying the
comparative resilience of tri-party versus bilateral repo markets; investigating
the role of securities dealers as intermediaries in Treasury market-making;
or examining whether the March 2020 Treasury market disruptions share
mechanisms with the 2008 crisis (the paper's conclusion draws this parallel
explicitly). The Internet Appendix contains additional robustness tables
(IA.II) and a map of the U.S. repo market (Section III).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pages 911-936.
DOI: 10.1111/jofi.13406. This article is a U.S. Government work and is in the
public domain in the USA (as stated on p. 911 of the artifact). Crossref
records Wiley standard terms; the artifact's public-domain notice takes
precedence for U.S. readers. This distillation was extracted by an LLM on
2026-06-06 and is **not human-verified or independently reproduced**.
Extract-only: the verbatim PDF is not hosted here.

> **Citation.** Copeland, Adam, and Antoine Martin. "Repo over the Financial
> Crisis." *The Journal of Finance* 80, no. 2 (April 2025): 911-936.
> DOI: 10.1111/jofi.13406.
