---
title: "Thirty Years of Change: Guernsey, Guo, Liu & Serfling (2025)"
description: >-
  Distilled: Using a new machine-learning-constructed dataset covering nearly
  all U.S. public firms from 1991 to 2020, this paper documents that classified
  (staggered) board usage has not declined overall; rather, its life-cycle
  dynamics have changed substantially by decade and IPO cohort, driven by
  falling collective-action costs and rising innovation-related investment. J.
  Finance 2025, paywalled. Seven core results with source locators, datasets
  used, the empirical design, and the ML data-construction method.
sidebar:
  label: Guernsey-Guo-Liu-Serfling 2025
  order: 1
tags: [paper-summary, corporate-governance, takeover-defenses, classified-boards,
       firm-life-cycle, panel-regression, difference-in-differences, event-study,
       machine-learning, peer-reviewed, unreplicated,
       data:wrds, data:edgar, data:thomson-13f]
paper:
  authors: Scott Guernsey, Feng Guo, Tingting Liu, Matthew Serfling
  authorList:
    - { family: Guernsey, given: Scott, affiliation: University of Tennessee, Haslam College of Business }
    - { family: Guo, given: Feng, orcid: "0000-0001-7785-8388", affiliation: Iowa State University, Ivy College of Business }
    - { family: Liu, given: Tingting, orcid: "0000-0002-4717-6519", affiliation: University of Tennessee, Haslam College of Business }
    - { family: Serfling, given: Matthew, orcid: "0000-0003-4454-095X", affiliation: University of Tennessee, Haslam College of Business }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2971–3020
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13485
  jel:
    codes: [G34, G30, G14]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Corporate Finance and Governance
    - Corporate Insolvency and Governance
    - Corporate Governance and Law
  dataAccess: licensed-commercial
  outcome:
    - probability of having a classified board (life-cycle pattern)
    - probability of board declassification
    - Tobin's Q (firm value)
    - cumulative abnormal return around declassification announcement
    - operating return on assets after board declassification
  outcomeClass: [firm-real-outcomes, security-returns]
  license: >-
    Paywalled (Crossref licence block: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-08-22; Wiley publisher terms, not CC)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/Journal of Finance, 2026-06-05)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 9
  methods:
    role: both
    contributes: rf-classified-board-classifier
    family: descriptive
    buildsFrom: [panel-regression, difference-in-differences, event-study, matching, probit-regression, text-classification]
    identification: natural-experiment
  contributionType: [new-data, new-fact, measurement]
  introducesData: true
  mechanisms: [agency, information-asymmetry]
  scope:
    region: US
    assetClass: US equities (nearly all public firms)
    period: 1991-01..2020-12
    frequency: annual
    dataType: [market, accounting, text, administrative]
    granularity: [firm]
    n: "137,032 firm-year observations (66,262 classified-board, 70,770 unitary)"
  findings:
    - ref: R1
      outcome: probability of having a classified board (life-cycle pattern)
      metric: probability
      value: "Non-S&P 1500 firms with a classified board: 42% (early 1990s) rising to 51.8% (2019-2020); S&P 500 firms: from 60% (1995-96) to 12.2% (2019-2020)"
      direction: mixed
      vsBenchmark: opposite trends for index vs non-index firms; prior ISS-based studies only see the S&P decline
    - ref: R2
      outcome: probability of having a classified board (life-cycle pattern)
      metric: probability
      value: "1991-2000 decade: life-cycle decline is flat to slight (youngest firms aged 0-1 at ~50%, oldest aged >= 16 at ~51%); 2011-2020 decade: 72.8% for youngest, 33.0% for oldest (aged >= 16)"
      direction: negative
      vsBenchmark: "life-cycle slope steepened across decades; coefficient on age >=16 in full sample: -8.6pp (t significant at 1%)"
    - ref: R3
      outcome: probability of board declassification
      metric: probability
      value: "1991-2000: declassification rate flat at 0.6%-1.1% per year across all age groups; 2001-2010: ages >= 16 at 3.3%; 2011-2020: ages >= 2 uniformly higher than prior decade, with ages >= 16 at 3.5%"
      direction: positive
      vsBenchmark: mature firms now declassify at 3-4x the rate of the 1990s (Figure 3, p. 2992)
    - ref: R4
      outcome: probability of having a classified board (life-cycle pattern)
      metric: probability
      value: "After joining S&P 1500 in 2011-2020 cohort: statistically significant negative coefficients on post-treatment indicators; no such effect in 1991-2000 or 2001-2010 cohorts (Figure 8, p. 3006)"
      direction: negative
      vsBenchmark: joining index caused declassification only in the most recent decade; mature firms (age >= 5) drive the effect
    - ref: R5
      outcome: Tobin's Q (firm value)
      metric: coefficient
      value: "Age 0: CB coefficient = +0.161 (t=2.76) in full sample 1991-2020; ages 2 and older: negative and significant (t-stats from -2.23 to -3.87). 1990s and 2000s show similar reversal; 2010s decade: only age 3-4 is significant (-0.210, t=-2.02), reversal otherwise disappears (Table V, p. 3009-3010)"
      direction: mixed
      vsBenchmark: value-reversal pattern flattens in 2010s, consistent with more optimal adjustment reducing the friction
    - ref: R6
      outcome: cumulative abnormal return around declassification announcement
      metric: car
      value: "CAR[-2,+2] positive but statistically insignificant across full sample (p-value=0.588); significantly positive 5.9%-6.1% in 1999-2000 only (Figure 9, p. 3013)"
      direction: none
      vsBenchmark: strong market approval only in 1999-2000; near-zero thereafter, consistent with pre-anticipation in recent decades
    - ref: R7
      outcome: operating return on assets after board declassification
      metric: coefficient
      value: "1991-2000: operating ROA improves in years after declassification, concentrated in mature firms; 2001-2010 and 2011-2020: no statistically significant change in ROA post-declassification (Figure 10, p. 3014)"
      direction: positive
      vsBenchmark: performance improvement only in first decade, implying classified boards were maintained too long in the 1990s
  resultType: new-finding
  relatesTo:
    - { cite: "Johnson, Karpoff & Yi (2022)", doi: '10.1093/rfs/hhab113', relation: extends, note: "extends their life-cycle value-reversal framework to all public firms and across three decades, showing the reversal has diminished in the 2010s" }
    - { cite: "Field and Lowry (2022)", doi: '10.1016/j.jfineco.2022.06.004', relation: extends, note: "corroborates and extends their finding that IPO-era classified board adoption is increasing; adds decade and cohort decomposition" }
    - { cite: "Cremers, Litov & Sepe (2017)", doi: '10.1016/j.jfineco.2017.08.003', relation: contradicts, note: "the declining-classified-board narrative they document holds only in the S&P 1500; the paper shows non-index firms have seen rising classified board usage" }
    - { cite: "Guernsey, Sepe & Serfling (2022)", doi: '10.1016/j.jfineco.2021.12.009', relation: builds-on, note: "builds on and formalizes the RF classifier approach to classified board identification introduced there" }
  openQuestions:
    - "The paper cannot establish causality between trends in collective-action costs / R&D intensity and trends in classified board usage because no valid instrument or natural experiment cleanly identifies these mechanisms (p. 2975)."
    - "Future work could use the RF classifier methodology to construct comprehensive data sets for other components of the E-index (other takeover defenses) and investigate their life-cycle dynamics (p. 3016)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full PDF read (pp. 2971-3020); seven results extracted from tables and figures. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-05, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core-results rows confirmed. Fixed equation (2): removed spurious double-summation over p and corrected bracketing to match Table III caption. Fixed outcomeClass: replaced firm-financing with security-returns (CARs and Tobin's Q are primary outcomes)." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13485", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[0]: content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-22. Wiley publisher terms, not CC; paper is paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's core findings, the ML data-construction method, and the empirical design: enough to know what it found and how, without reading all 50 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13485).

## TL;DR

The paper constructs a novel classified board dataset covering nearly all U.S. public firms from 1991 to 2020 using a Random Forest (RF) Classifier applied to DEF 14A proxy filings from SEC EDGAR, yielding roughly three times more firm-year observations than commercial databases like ISS. Using this dataset, the paper documents three decades of change in how firms use classified (staggered) boards over their life cycles. In the 1990s, classified board usage was sticky across the life cycle, consistent with high collective-action costs preventing optimal adjustment. Since 2001, and especially in the 2010s, firms have become increasingly likely to declassify their boards as they mature. The value-reversal pattern linking classified boards to firm value (positive for young firms, negative for mature ones) that was strong in the 1990s and 2000s has largely disappeared in the 2010s, suggesting classified board adjustments have become more optimal. Mechanisms investigated include rising R&D intensity among young firms, growing passive institutional ownership, falling bid-ask spreads, and increased hedge fund activism.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Classified board usage has NOT declined overall: non-S&P 1500 firms increased from 42% to 51.8% (1991-2020), even as S&P 500 firms fell from 60% to 12.2% | Figures 1A2, p. 2985; text p. 2986 | Non-S&P 1500: +9.8pp over 30 years; S&P 500: -47.8pp; divergence masked in ISS-only samples |
| R2 | Life-cycle slope of classified board usage steepened across decades: in the 1990s it was essentially flat; in the 2011-2020 decade it dropped from 72.8% to 33.0% across age groups | Table II (col. 1,4,8), pp. 2989-2990; Figure 2, p. 2988 | Full-sample age >=16 coefficient: -8.6pp\*\*\*; 2011-2020 IPO cohort age >=16 coefficient: -5.8pp\*\*\* |
| R3 | Board declassification rates have increased substantially over time: mature firms (age >= 16) declassify at 3.5% per year in the 2010s vs 0.6-1.1% in the 1990s | Figure 3, p. 2992 | Approximately 3-5x higher annual declassification rates for mature firms in the 2010s vs 1990s |
| R4 | Being added to the S&P 1500 caused declassification only in the 2011-2020 decade: propensity-matched DiD shows significant negative post-treatment CB coefficients for this cohort but not the prior two | Figure 8, p. 3006 | Statistically significant negative coefficients in t+1 to t+3 for 2011-2020 cohort (90% CI excludes zero); no effect in 1991-2000 or 2001-2010 |
| R5 | The classified-board value-reversal pattern (positive for young firms, negative for mature ones) was present in the 1990s and 2000s but largely disappeared in the 2010s | Table V, pp. 3009-3010 | Age 0: CB = +0.161\*\*\* (full sample); age >= 2: CB negative and significant (up to t=-3.87). In 2010s, only age 3-4 remains significant (-0.210\*\*); all older age groups insignificant |
| R6 | Market response to declassification announcements was significantly positive in 1999-2000 (CAR = 5.9%-6.1%) but has been statistically insignificant across the rest of the sample period | Figure 9, p. 3013 | Full-sample CAR[-2,+2]: positive but p-value = 0.588; 1999-2000 CARs significantly positive and largest in any two-year window |
| R7 | Declassifying the board improved operating ROA in the 1990s (especially for mature firms) but not in the 2000s or 2010s | Figure 10, p. 3014 | 1991-2000 cohort: positive post-treatment ROA shifts visible in matched DiD; 2001-2010 and 2011-2020: coefficients cluster near zero with wide confidence intervals |

**Overall (paper's conclusion).** Contrary to conventional wisdom, classified boards are not going extinct across the U.S. corporate sector; the decline is concentrated in S&P 1500 firms. The life-cycle dynamics of classified board usage have changed profoundly over three decades: from high stickiness in the 1990s to more dynamic adjustment in the 2010s. Evidence on mechanisms suggests that rising R&D intensity among young firms, growing passive institutional ownership that reduced collective-action costs, falling bid-ask spreads, and increased shareholder activism all contributed to this shift. The disappearance of the value-reversal pattern in the 2010s implies that classified board adjustment has become more optimal, reducing the friction that caused firms to maintain this defense too long in earlier decades.

## Theory / model

The paper has no formal theoretical model; instead it organizes its analysis around the cost-benefit framework of Johnson, Karpoff, and Yi (2022) and the related literature on takeover defenses. The tested theoretical propositions are:

**Hypothesis 1 (life-cycle costs and benefits).** A classified board can be value-enhancing for young firms engaged in long-term, information-intensive investments (R&D, intangibles) because it protects managers from short-termist takeover pressure. As firms mature and reduce such investments, the costs of a classified board (managerial entrenchment, reduced monitoring) outweigh its benefits, implying the optimal strategy is to declassify (pp. 2974, 2993).

**Hypothesis 2 (collective-action costs).** High collective-action costs among dispersed shareholders (free-rider problems, heterogeneous time horizons, information asymmetry) prevent optimal declassification even when the defense is value-destroying. Falling collective-action costs over time, driven by rising passive institutional ownership, reduced bid-ask spreads, and increased activist pressure, should enable more dynamic adjustment (pp. 2974-2975, 2993-3001).

**Hypothesis 3 (value reversal).** Because collective-action frictions prevented optimal adjustment in the 1990s and 2000s, the relation between classified boards and firm value should be positive for young firms and negative for mature ones (the value-reversal pattern). As frictions fell in the 2010s, enabling more optimal adjustment, this reversal should diminish (p. 2976).

The paper explicitly states that it cannot establish causality between trends in the mechanism variables and trends in classified board usage, because no valid instrument or natural experiment cleanly identifies the channel (p. 2975).

This paper extends and relates to several prior studies. Cremers, Litov, and Sepe (2017) documented declining classified board usage in S&P 1500 firms; the present paper shows that trend does not hold for the broader population. Field and Lowry (2022) documented increasing classified board adoption at IPO; the present paper adds decade and cohort decomposition of that trend. The RF classifier builds on and formalizes the approach introduced in Guernsey, Sepe, and Serfling (2022).

## Method

**RF Classifier for classified board status.** The core methodological contribution is a five-step machine-learning pipeline that uses text from DEF 14A proxy filings in SEC EDGAR to classify the classified board status of all U.S. public firms from 1991 to 2020, extending the ISS database (which covers only S&P 1500 firms) to the near-universe of public firms (pp. 2978-2982).

The steps are:

1. Obtain all DEF 14A filings from SEC EDGAR with mentions of "elect" or "stagger" (179,942 unique CIK-FDATE pairs; reduced to 110,511 firm-year observations after cleaning).
2. Apply two parallel text-extraction strategies: (i) locate 150-word windows following "Proposal 1. Election of Directors" headings (covers 85.3% of filings), and (ii) keyword search for "class" and "term" in context, finding classified board language in 66.0% of the sample.
3. Build a training sample by merging with ISS data (39,998 DEF 14A filings that match ISS; 80% training, 20% test).
4. Convert text to unigrams and bigrams, apply Porter stemming, retain phrases appearing in at least 1,000 filings (corpus of 2,287 phrases), and run the RF Classifier (tuning: number of trees, max depth, min samples per split/leaf, max features per tree, cross-validated in training sample).
5. Apply the best RF model to predict classified board status for all filings; extend to microfiche-era filings (pre-EDGAR, 1991-1995) via hand collection.

Out-of-sample prediction accuracy is 97.3% (1.5% false negatives, 1.2% false positives). Compared to a refined keyword search, the RF Classifier reduces total error by an 81% improvement (error rate 1.6% vs 8.7% for the refined keyword approach). The 25 most important predictor phrases (accounting for 37.6% of variable importance) include "three year," "three class," and "divid" (from the Porter stemmer, stemming "divided" as in "directors are divided into three classes").

**Empirical designs.** The paper uses several complementary designs:

- OLS panel regressions with firm-age dummies, firm-level controls, industry fixed effects, and/or firm fixed effects (Figures 1-4, Tables II-IV, following Johnson, Karpoff, and Yi (2022)).
- A stacked propensity-score-matched DiD design around S&P 1500 index additions (Figure 8, p. 3006), where matched treatment/control pairs are required to have a classified board in the three years before treatment.
- An OLS firm-value (Tobin's Q) regression with firm controls and industry-year fixed effects, estimated separately by age group and decade (Table V).
- A short-run event study of announcement CARs[-2,+2] around shareholder meeting votes to approve declassification, using the CRSP equal-weighted index as the benchmark (Figure 9, p. 3013).
- A stacked propensity-score-matched DiD for post-declassification operating ROA, using firm-treatment cohort and cohort-year fixed effects (Figure 10).

## Empirical specifications

**Life-cycle OLS (main design, Figures 1-4, Table II).** For each firm $$i$$ in year $$t$$, the primary estimating equation is (p. 2985):

$$
CB_{it} = \sum_{t=1991}^{2020} \beta_t \text{Year}_t \left(\text{or } \sum_{a=0}^{\geq 16} \omega_a \text{Age}_{it}\right) + \Gamma X_{it} + \eta_k + \gamma_i + \varepsilon_{it} \tag{1}
$$

where $$CB_{it}$$ equals one if firm $$i$$ has a classified board in year $$t$$; $$\text{Year}_t$$ is a year-group indicator; $$\text{Age}_{it}$$ is an age-group indicator (years since IPO, grouped 0-1, 2-3, 4-5, 6-7, 8-10, 11-15, $$\geq 16$$); $$X_{it}$$ includes $$\text{Ln}(\text{MVE}_{t-1})$$, $$\text{IO}_t$$, $$\text{Delaware}_t$$, and $$\text{S\&P 1500}_t$$; $$\eta_k$$ are two-digit SIC industry fixed effects; and $$\gamma_i$$ are firm fixed effects. Regressions for Figures 1-4 are estimated separately for each decade or IPO cohort. Standard errors are clustered by firm throughout. The dependent variable for declassification regressions (Figure 3) is $$\text{Declass}_{it}$$, which equals one if the firm had a classified board in $$t-1$$ but not in $$t$$.

**Mechanism regressions (Tables III-IV, Figures 6-7).** Same specification as equation (1) but with the dependent variable replaced by passive institutional ownership (Big Three IO, Quasi IO), bid-ask spread ($$\text{Ln}(\text{Bid-Ask Spread})_{it}$$), hedge fund activism, or the likelihood of receiving a shareholder proposal to declassify. Table III adds interactions of age groups with five-year period dummies:

$$
CB_{it} = \sum_{t=1991}^{2020} \left[\beta_t (\text{IndexIO}_{it} \times \text{Year}_t) + v_t (\text{NonIndexIO}_{it} \times \text{Year}_t)\right] + \Gamma X_{it} + \gamma_i + \tau_t + \varepsilon_{it} \tag{2}
$$

where $$\text{IndexIO}_{it}$$ is Big Three or quasi-indexer ownership (normalized by one standard deviation).

**S&P 1500 DiD (Figure 8).** A stacked DiD with propensity-score matching (logit on $$\text{Ln}(\text{MVE})$$, $$\text{IO}$$, $$\text{Delaware}$$; caliper 0.025; matched within two-digit SIC and fiscal year). For treatment cohort $$j$$ and event time $$t$$:

$$
CB_{ijt} = \sum_{t=-3}^{3} \beta_t (\text{Treat}_{ij} \times \text{Time}_{jt}) + \gamma_{ij} + \delta_{jt} + \Gamma X_{ij} \times \text{Post}_{jt} + \varepsilon_{ijt} \tag{3}
$$

where $$\text{Time}_{jt-1}$$ is the excluded base year, $$\gamma_{ij}$$ are firm-treatment-cohort fixed effects, and $$\delta_{jt}$$ are treatment-cohort-year fixed effects. The matched sample has 624 treatment and 1,159 control firms.

**Tobin's Q regressions (Table V).** OLS with the dependent variable $$\text{Tobin's Q}_{it} = (\text{prcc\_f} \times \text{csho} + \text{at} - \text{ceq}) / \text{at}$$, estimated separately for each of seven age groups (0, 1, 2, 3-4, 5-6, 7-9, $$\geq 10$$) and four sample periods (full, 1991-2000, 2001-2010, 2011-2020). Controls and industry-year fixed effects are included; standard errors are clustered by firm.

**Event study CARs (Figure 9).** Market model estimated over the [-210,-11] trading-day window before each declassification meeting date (857 meetings, 1995-2020), using the CRSP equal-weighted index. CARs computed over [-2,+2]. Coefficients regress CAR on year dummies with and without firm-level controls and SIC2 fixed effects; 90% confidence intervals based on firm-clustered standard errors.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CRSP monthly stock returns | Market value of equity (MVE), stock return data, event study benchmark index | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat annual fundamentals | Book value of assets, Tobin's Q construction, firm characteristics | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| SEC EDGAR DEF 14A filings | Text input to the RF Classifier; classified board status for all public firms | [SEC EDGAR](/wiki/datasets/edgar/) |
| ISS (RiskMetrics / IRRC) governance database | Training labels for the RF Classifier; classified board status for S&P 1500 firms | No page yet |
| Thomson Reuters 13-F institutional holdings | Institutional ownership (IO), Big Three IO, quasi-indexer IO | [Thomson 13F (s34)](/wiki/licensed/thomson-13f/) (licensed) |
| Voting Analytics (ISS / Diligent) | Shareholder proposals to declassify boards, 2003-2020 | No page yet |
| Hedge fund activism data (Brav, Jiang & Kim) | Hedge fund targeting by firm-year, 1994-2018 | No page yet |
| Wall Street Journal articles | Media attention to corporate governance; keyword search, 1998-2020 | No page yet |

Sample: 137,032 firm-year observations, 1991-2020 (annual frequency). Classified board sample: 66,262 firm-years. Unitary board sample: 70,770 firm-years. The dataset introduced by the paper (classified board status for nearly all public firms via RF Classifier + hand-collection) covers roughly 3x the firm-year observations of commercial databases.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13485) if you are:
studying the evolution of corporate governance defenses over long horizons across the full population of public firms (not just index firms); interested in the RF Classifier methodology for extending ISS-type governance data to the full public-firm universe; testing the value-reversal hypothesis of Johnson, Karpoff, and Yi (2022) with a more comprehensive sample; or investigating the role of passive institutional ownership and shareholder activism in governance change. Table II (p. 2990) contains the primary life-cycle regressions; Table V (pp. 3009-3010) contains the firm-value results; Figures 1-3 (pp. 2985-2992) display the decade-by-decade and cohort-by-cohort patterns.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). The licence is Wiley publisher terms (not CC); this page is extract-only. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**.

> Guernsey, Scott, Feng Guo, Tingting Liu, and Matthew Serfling. "Thirty Years of Change: The Evolution of Classified Boards." *The Journal of Finance* 80, no. 5 (October 2025): 2971–3020. DOI: 10.1111/jofi.13485.
