---
title: "Are CEOs Rewarded for Luck: Andreani, Ellahie & Shivakumar (2025)"
description: >-
  Distilled: Using the 2017 Tax Cuts and Jobs Act as a quasi-natural experiment,
  the paper shows that weakly scrutinized CEOs are compensated for one-off
  windfall tax gains (deferred tax liability remeasurement) but not penalized for
  corresponding tax losses, consistent with rent extraction rather than optimal
  contracting. J. Finance 2025, CC BY-NC-ND 4.0. Six core results with source
  locators, datasets used, the empirical design, and the estimating equations.
sidebar:
  label: Andreani-Ellahie-Shivakumar 2025
  order: 1
tags: [paper-summary, executive-compensation, corporate-governance, pay-for-luck,
       tax-policy, rent-extraction, panel-regression, difference-in-differences,
       peer-reviewed, unreplicated, data:wrds]
paper:
  authors: Martina Andreani, Atif Ellahie, Lakshmanan Shivakumar
  authorList:
    - { family: Andreani, given: Martina, affiliation: INSEAD }
    - { family: Ellahie, given: Atif, orcid: "0000-0002-5241-8578", affiliation: University of Utah }
    - { family: Shivakumar, given: Lakshmanan, orcid: "0000-0003-1492-2033", affiliation: London Business School }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2255–2302
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13448
  jel:
    codes: [G34, M12, H25]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Corporate Taxation and Avoidance
    - Auditing, Earnings Management, Governance
    - Corporate Finance and Governance
  dataAccess: licensed-commercial
  outcome:
    - CEO total compensation (log)
    - CEO discretionary compensation (log)
    - CEO fixed salary (log)
  outcomeClass: [labor-careers-health]
  license: >-
    CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0,
    start 2025-04-09)
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley Online Library, 2026-06-05)"
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 7

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, factor-analysis-pca]
    identification: natural-experiment

  contributionType: [new-fact, new-method]
  mechanisms: [agency, moral-hazard]

  scope:
    region: US
    assetClass: US equities (S&P 1500 / ExecuComp universe)
    period: 2013-01..2019-12
    frequency: annual
    dataType: [accounting, market, administrative]
    granularity: [firm, individual]
    n: "9,225 firm-year observations, 2,081 unique firms, January 2013 to December 2019"

  findings:
    - ref: R1
      outcome: CEO total compensation (log)
      metric: coefficient
      value: "Tax Shock x NDTL = 2.17 (t=2.40); Tax Shock x NDTL x Pay Scrutiny = -3.81 (t=-2.68); Table III col (2)"
      direction: positive
      vsBenchmark: "effect concentrated in low-scrutiny CEOs; sum of coefficients is significantly positive; sum including Pay Scrutiny=1 is insignificant"
    - ref: R2
      outcome: CEO total compensation (log)
      metric: coefficient
      value: "Tax Shock x DTL = 3.311 (t=3.20 in col 2 Table IV); Tax Shock x DTL x Pay Scrutiny = -5.814 (t=-3.62)"
      direction: positive
      vsBenchmark: "firm in 3rd DTL quartile paid CEO 19.7% more than firm in 1st quartile; ~$790,000 for median-pay CEO"
    - ref: R3
      outcome: CEO total compensation (log)
      metric: coefficient
      value: "Tax Shock x DTA = insignificant across all columns; F-test p-value = 0.000 rejects Tax Shock x DTA = -Tax Shock x DTL; Table IV col (2)-(4)"
      direction: none
      vsBenchmark: "asymmetric: tax gains rewarded but tax losses not penalized regardless of pay scrutiny level"
    - ref: R4
      outcome: CEO discretionary compensation (log)
      metric: coefficient
      value: "Tax Shock x DTL col (6) Table IV = 6.61 (t=3.69); Tax Shock x DTL x Pay Scrutiny = -7.18 (t=-1.97); fixed comp Tax Shock x DTL = 0.802 (t=3.23) but economically much smaller"
      direction: positive
      vsBenchmark: "windfall reward concentrated in discretionary (variable) pay; fixed salary effect is substantially smaller in magnitude"
    - ref: R5
      outcome: CEO total compensation (log)
      metric: coefficient
      value: "CFO Tax Shock x DTL = 2.32 (t=2.21) Table VIII col (1); Other NEOs Tax Shock x DTL and interactions all insignificant col (2)"
      direction: positive
      vsBenchmark: "windfall reward observed in CEO and CFO pay but not in other named executive officers"
    - ref: R6
      outcome: CEO total compensation (log)
      metric: coefficient
      value: "Within-calendar-year identification: Tax Shock x DTL increases in magnitude and significance in col (4) vs col (2)-(3) Table IV"
      direction: positive
      vsBenchmark: "staggered fiscal-year identification confirms main result; parallel-trends assumption supported (no pre-trends)"

  resultType: overturns

  relatesTo:
    - { cite: "Bertrand and Mullainathan (2001)", doi: '10.1162/00335530152466269', relation: tests, note: "paper tests their pay-for-luck finding using a cleaner exogenous luck shock (TCJA windfall) rather than market/industry returns" }
    - { cite: "Garvey and Milbourn (2006)", doi: '10.1016/j.jfineco.2004.01.006', relation: tests, note: "provides cleaner evidence consistent with their asymmetric pay-for-luck prediction: gains rewarded, losses not penalized" }
    - { cite: "Daniel, Li, and Naveen (2020)", doi: '10.1093/rfs/hhz057', relation: contradicts, note: "show earlier pay-for-luck evidence is not robust; this paper restores the asymmetric finding using a different and cleaner luck measure" }
    - { cite: "Blanchard, Lopez-de-Silanes, and Shleifer (1994)", doi: '10.1016/0304-405x(94)90009-4', relation: builds-on, note: "earlier paper on cash windfalls and CEO compensation in 11 firms; this paper is a large-sample extension using tax windfalls" }

  openQuestions:
    - "Whether pay-for-luck patterns in other windfall settings (not TCJA) follow the same rent-extraction logic, since the TCJA is a unique shock and cannot generalize directly (p. 2294)."
    - "How shareholder-value-maximization theories should be amended to explain why it is optimal to reward weakly scrutinized CEOs for windfall tax gains but not penalize them for windfall tax losses (p. 2294)."

  replicationCode:
    status: available

  proposedVocab:
    - { axis: topic, term: pay-for-luck, def: "Whether executives are compensated for performance driven by factors beyond their control (luck), as opposed to their own effort or decisions.", aliases: [luck-based-pay, windfall-compensation] }
    - { axis: topic, term: rent-extraction, def: "CEOs using limited monitoring to extract compensation above optimal contracting levels, especially for gains unrelated to their actions.", aliases: [managerial-rent-extraction] }
    - { axis: topic, term: executive-compensation, def: "CEO and other senior executive pay levels, structure, and determinants.", aliases: [ceo-pay, executive-pay] }
    - { axis: topic, term: corporate-governance, def: "Internal and external mechanisms that monitor and constrain managerial behavior on behalf of shareholders.", aliases: [firm-governance, governance] }
    - { axis: topic, term: tax-policy, def: "Government tax laws and reforms and their effects on firm and individual behavior.", aliases: [tax-reform, tcja] }

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full PDF read (pp. 2255-2302, JF Vol. 80 No. 4 August 2025); six results extracted from Tables III-VIII. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; two fixes applied: R2 locator corrected from col (4) to col (2) with correct values 3.311 (t=3.20) and -5.814 (t=-3.62); R4 fixed-comp overclaim corrected (0.802** is significant, not insignificant) and star mismatch fixed (** not ***)."

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13448
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-04-09"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the quasi-natural experiment it exploits (TCJA 2017 deferred-tax remeasurement), the triple-difference estimating equation, and the evidence for asymmetric pay-for-luck: enough to know what it found and how, without reading all 48 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13448).

## TL;DR

The 2017 Tax Cuts and Jobs Act (TCJA) lowered the U.S. corporate tax rate from 35% to 21%, generating one-off book gains for firms with large deferred tax liabilities and book losses for firms with large deferred tax assets. Because these gains and losses arise from past firm transactions, are exogenous to current managerial effort, and vary heterogeneously across firms even within industries, they are a clean "luck" shock to earnings. Using a triple-difference (DDD) panel regression on 9,225 firm-year observations (2,081 U.S. firms, 2013-2019), the paper finds that CEOs facing weak external pay scrutiny receive significantly higher total compensation in the TCJA transition period when their firms have larger deferred tax liabilities (windfall gains), but are not penalized when their firms have larger deferred tax assets (windfall losses). CEOs facing high pay scrutiny show no such association. The asymmetry is concentrated in discretionary (variable) pay, is observed in CEO and CFO pay but not in other named executive officers, and is not explained by investment incentives, political activities, talent retention, or catch-up for underpaid CEOs. The results support the rent-extraction view of executive compensation (Bertrand and Mullainathan (2001)) and challenge optimal contracting theories. The paper also provides cleaner evidence for the asymmetric pay-for-luck pattern predicted by Garvey and Milbourn (2006) and restores credibility to findings challenged by Daniel, Li, and Naveen (2020). It extends the earlier analysis of cash windfalls and CEO pay in Blanchard, Lopez-de-Silanes, and Shleifer (1994) to a large-sample setting with a TCJA-specific identification strategy.

## Core results

Magnitudes and significance as reported; `\*\*` / `\*\*\*` = 5% / 1%. All regressions include firm and year fixed effects and standard errors clustered by firm. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Weakly monitored CEOs earn significantly more in the TCJA period when their firm has larger net deferred tax liabilities (windfall gains); effect absent for high-scrutiny CEOs | Table III col (2)-(3), p. 2275 | Tax Shock x NDTL = 2.17 (t=2.40)\*\*; Tax Shock x NDTL x Pay Scrutiny = -3.81 (t=-2.68)\*\*\*; effect absent at Pay Scrutiny = 1 |
| R2 | Separating DTA from DTL: CEO pay is positively associated with deferred tax liabilities (windfall gains) in the TCJA period, concentrated in low-scrutiny firms; a firm in the 3rd DTL quartile pays CEO 19.7% more than a firm in the 1st quartile | Table IV col (2), p. 2276-2278 | Tax Shock x DTL = 3.311 (t=3.20)\*\*\*; Tax Shock x DTL x Pay Scrutiny = -5.814 (t=-3.62)\*\*\* |
| R3 | CEO pay is not reduced for windfall tax losses (DTA remeasurement); the gain-loss asymmetry is statistically significant (F-test p=0.000) | Table IV col (2)-(4), p. 2276, 2278 | Tax Shock x DTA coefficients all statistically insignificant; F-test rejects equality of Tax Shock x DTA and Tax Shock x DTL magnitudes |
| R4 | The windfall pay-for-luck is concentrated in discretionary (variable) pay; the fixed salary effect is substantially smaller in magnitude | Table IV col (5)-(6), p. 2276-2279 | Tax Shock x DTL (Disc. Comp) = 6.61 (t=3.69)\*\*\*; Tax Shock x DTL (Fixed Comp) = 0.802 (t=3.23)\*\* and substantially smaller in magnitude; Tax Shock x DTL x Pay Scrutiny (Disc. Comp) = -7.175 (t=-1.97)\* |
| R5 | The reward is specific to CEOs and CFOs, not shared broadly with other named executive officers | Table VIII col (1)-(2), p. 2287 | CFO: Tax Shock x DTL = 2.32 (t=2.21)\*\*; Other NEOs: Tax Shock x DTL and all three-way interactions insignificant |
| R6 | Within-calendar-year identification exploiting staggered fiscal years confirms results; no pre-trend in DTA/DTL compensation prior to TCJA | Table IV col (4), p. 2278-2279 | Results robust; interaction of calendar-year FE with DTA and DTL show no differential pre-trends |

**Overall (paper's conclusion).** The evidence supports the rent-extraction view: weakly scrutinized CEOs are paid for good luck but not penalized for bad luck, the pattern is concentrated in discretionary pay and senior executives, it is unrelated to future investments or shareholder payouts, and it cannot be explained by talent retention, political activity, or formulaic compensation plans. Shareholder-value-maximizing theories alone are insufficient to explain the observed pay patterns.

## Theory / model

The paper has no formal structural model. It tests two competing theoretical frameworks using the TCJA shock as a natural experiment:

**Optimal contracting theory** (also called efficient contracting or shareholder-value-based theory): managers should be compensated only for performance attributable to their own effort, not for gains from factors beyond their control. Under this view, CEO pay should not respond to one-off tax windfalls that are unrelated to managerial actions.

**Rent-extraction model** (Bertrand and Mullainathan (2001)): managers with limited pay scrutiny aim to extract maximum compensation from their firms. A key prediction is that pay for luck should be asymmetric: CEOs seek rewards for favorable luck but not penalties for adverse luck. Three empirical conditions distinguish this view: (i) pay for luck factors genuinely beyond CEO control, (ii) asymmetric response (good luck rewarded, bad luck not penalized), and (iii) effect concentrated in firms with weak pay scrutiny.

The identification logic exploits three features of TCJA-driven deferred tax remeasurements (pp. 2257-2258):
1. The trigger (government decision to lower the tax rate) is exogenous to managers' decisions.
2. The TCJA was largely unexpected until Trump's surprise election victory in November 2016 and passed in less than three months, making anticipation or influence by firms implausible.
3. A firm's TCJA gain or loss was determined solely by its pre-existing stock of deferred tax assets and liabilities, which are related to past transactions, not current effort.

These features make TCJA tax effects a clean measure of luck: compensation for these effects cannot reflect rewards for CEO effort or performance in the transition period.

## Method

The paper proposes a novel composite pay-scrutiny measure as a methodological contribution, arguing that post-Sarbanes-Oxley regulatory changes have homogenized internal governance variables (board independence, committee composition) so they no longer differentiate well-governed from poorly-governed firms. The composite proxy focuses on external monitoring by investors.

**Pay Scrutiny construction** (p. 2268): The first principal component is extracted from five firm-level proxies measured at the beginning of each fiscal year. This component explains 78% of the variation in the five proxies:

$$
\text{Pay Scrutiny}_j = \text{PC}_1(\text{Market Value}_j, \text{Liquidity}_j, \text{Trading Volume}_j, \text{Nonzero Return Days}_j, \text{Analyst Coverage}_j)
$$

Each proxy is normalized to the [0, 1] interval by subtracting the minimum and dividing by the range. The component is then re-normalized to [0, 1].

The `factor-analysis-pca` technique (five external monitoring proxies collapsed into one index) builds on the `panel-regression` approach for the causal estimates. The method generalizes the internal-governance proxies of Bertrand and Mullainathan (2001) toward market-based external scrutiny, motivated by post-2006 regulatory changes (Say-on-Pay voting, 2011 SEC mandate) that increased the salience of investor and media monitoring.

## Empirical specifications

The main estimating equation is a triple-difference (DDD) pooled regression for CEO compensation in fiscal year $$t$$ (p. 2266, equation 1):

$$
\text{Total Comp}_t = \beta_0 + \beta_1 \text{Tax Shock}_t + \beta_2 \text{DTA}_{t-1} + \beta_3 \text{Tax Shock}_t \times \text{DTA}_{t-1}
$$

$$
+ \beta_4 \text{DTL}_{t-1} + \beta_5 \text{Tax Shock}_t \times \text{DTL}_{t-1} + \beta_6 \text{Pay Scrutiny}_{t-1}
$$

$$
+ \beta_7 \text{Tax Shock}_t \times \text{Pay Scrutiny}_{t-1} + \beta_8 \text{DTA}_{t-1} \times \text{Pay Scrutiny}_{t-1}
$$

$$
+ \beta_9 \text{Tax Shock}_t \times \text{DTA}_{t-1} \times \text{Pay Scrutiny}_{t-1} + \beta_{10} \text{DTL}_{t-1} \times \text{Pay Scrutiny}_{t-1}
$$

$$
+ \beta_{11} \text{Tax Shock}_t \times \text{DTL}_{t-1} \times \text{Pay Scrutiny}_{t-1}
$$

$$
+ \gamma' X_{t-1} + \theta' \lambda_j + \pi' \tau_t + \phi' \tau_t \times \text{DTA}_{t-1} + \psi' \tau_t \times \text{DTL}_{t-1} + \varepsilon_t \tag{1}
$$

where:
- $$\text{Tax Shock}_t = 1$$ for fiscal years ending between December 31, 2017 and March 31, 2019 (the TCJA transition period); 0 otherwise.
- $$\text{DTA}_{t-1}$$ = beginning-of-year deferred tax assets scaled by book total assets (Compustat `txndba` / `at`).
- $$\text{DTL}_{t-1}$$ = beginning-of-year deferred tax liabilities scaled by book total assets (Compustat `txndbl` / `at`).
- $$X_{t-1}$$ = control vector: log total assets (Size), return on assets (Profitability), size- and industry-adjusted 12-month past returns (Past Returns), book-to-price ratio, idiosyncratic volatility, financial leverage, log CEO age, log CEO tenure.
- $$\lambda_j$$ = firm fixed effects; $$\tau_t$$ = calendar-year fixed effects.
- Standard errors clustered by firm.

**Primary variables of interest:** the double interactions $$\text{Tax Shock} \times \text{DTA}$$ (captures pay for windfall tax losses) and $$\text{Tax Shock} \times \text{DTL}$$ (captures pay for windfall tax gains), and the triple interactions $$\text{Tax Shock} \times \text{DTA} \times \text{Pay Scrutiny}$$ and $$\text{Tax Shock} \times \text{DTL} \times \text{Pay Scrutiny}$$ (capture whether these relationships differ by scrutiny level).

**Within-calendar-year identification (column 4, Table IV, p. 2278-2279):** Because the TCJA transition period is staggered across fiscal years (firms with different year-ends recognize TCJA tax effects in different calendar years), the authors add calendar-year-by-DTA and calendar-year-by-DTL fixed effects. Identification within a calendar year compares CEO compensation across firms whose financial statements are more vs. less likely to reflect TCJA tax effects, holding the calendar year constant. This provides a sharper test and the results strengthen in magnitude and significance.

**Alternative explanations tested (Tables V-X):** The windfall-related pay is decomposed via a two-stage regression to test whether it relates to future CAPX, ROA, share repurchases, or total payout (Table V). Political leanings of CEOs (Table VI), CEO tenure (Table VII), sharing with other executives (Table VIII), underpaid CEOs (Table IX), and talent transferability (Table X) are each tested by extending equation (1) with the relevant interaction terms.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| ExecuComp, S&P Capital IQ People Intelligence, ISS Incentive Lab | CEO and CFO total compensation, fixed salary, discretionary pay; CEO age and tenure | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Compustat North America (annual) | Deferred tax assets (txndba), deferred tax liabilities (txndbl), total assets (at), book equity, ROA, CAPX, dividends, share repurchases, leverage, sales | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| CRSP monthly and daily | Market value of equity, stock returns, trading volume, daily returns for illiquidity and nonzero return days | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| I/B/E/S (Institutional Brokers' Estimate System) | Analyst coverage (number of equity research analysts with EPS forecasts) | [WRDS / I/B/E/S](/wiki/licensed/wrds/) (licensed) |
| Federal Election Commission (FEC) campaign finance database | CEO personal political donations (Republican vs. Democratic leanings) | No page yet |
| Boardex | Board structure (independence of directors, CEO-Chairman separation) | No page yet |
| FactSet | Share ownership data (institutional shareholders, blockholder presence) | No page yet |
| RavenPack | Media scrutiny (firm-specific full-size articles) | No page yet |

Sample: January 2013 to December 2019 (annual frequency). 9,225 firm-year observations from 2,081 unique U.S. firms after excluding three years around CEO turnover events and requiring at least one observation before and during the TCJA transition period.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13448) if you are:
- Evaluating the empirical validity of pay-for-luck models or the rent-extraction view of executive compensation.
- Using the TCJA as a natural experiment for corporate-level or compensation research (institutional details in Section I; variable definitions in Appendix B).
- Building a composite external-monitoring index from market-based proxies (Pay Scrutiny construction, Section III and Appendix B).
- Studying asymmetries in executive pay response to gains vs. losses.
- Extending the analysis to other executive types (CFO, named executive officers) or other windfall settings.

Tables III-IV (main results), Table V (investment/payout tests), and Tables VI-X (alternative explanations) contain the full specification details.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4), August 2025, pp. 2255-2302. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. Licensed CC BY-NC-ND 4.0: use and distribution in any medium permitted provided the original work is properly cited, the use is non-commercial, and no modifications or adaptations are made.

> Andreani, Martina, Atif Ellahie, and Lakshmanan Shivakumar.
> "Are CEOs Rewarded for Luck? Evidence from Corporate Tax Windfalls."
> *The Journal of Finance* 80, no. 4 (August 2025): 2255-2302.
> DOI: 10.1111/jofi.13448. © 2025 The Author(s).
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page extracts core results only; no modifications to the original were made in the excerpts cited above.
