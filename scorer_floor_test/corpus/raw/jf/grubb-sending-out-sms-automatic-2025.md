---
title: "Sending Out an SMS: Grubb, Kelly, Nieboer, Osborne & Shaw (2025)"
description: >-
  Distilled: At-scale field experiments at major U.K. banks show that automatic
  enrollment into just-in-time overdraft text alerts reduces unarranged overdraft
  and unpaid item charges 17% to 19% and arranged overdraft charges 4% to 8%,
  implying potential annual market-wide savings of GBP 170 million to GBP 240
  million. J. Finance 2025, CC BY 4.0. Eight core results with source locators,
  datasets used, the identification strategy, and the estimating specification.
sidebar:
  label: Grubb-Kelly-Nieboer-Osborne-Shaw 2025
  order: 1
tags: [paper-summary, household-finance, consumer-finance, behavioral-finance,
       randomized, field-experiment, open-access, cc-by, peer-reviewed, unreplicated,
       panel-regression]
paper:
  authors: Michael D. Grubb, Darragh Kelly, Jeroen Nieboer, Matthew Osborne, Jonathan Shaw
  authorList:
    - { family: Grubb, given: Michael D., orcid: "0000-0001-9885-2225", affiliation: Boston College }
    - { family: Kelly, given: Darragh, affiliation: Google }
    - { family: Nieboer, given: Jeroen, affiliation: Deliveroo }
    - { family: Osborne, given: Matthew, orcid: "0000-0002-8949-5673", affiliation: "University of Toronto, UTM Department of Management and Rotman School of Management" }
    - { family: Shaw, given: Jonathan, affiliation: "UK Financial Conduct Authority and Institute for Fiscal Studies" }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 467–514
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13404
  jel:
    codes: [G21, D18, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Mobile Crowdsensing and Crowdsourcing
    - Human Mobility and Location-Based Analysis
    - Personal Information Management and User Behavior
  dataAccess: proprietary-confidential
  outcome:
    - monthly overdraft charges (arranged overdraft, unarranged overdraft, unpaid item)
    - days in overdraft per month
    - number of overdraft episodes
    - account logins and transfers following an alert
  outcomeClass: [household-finance]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2024-12-26; corroborated by artifact p.467 Creative Commons
    Attribution License notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access PDF available (Wiley OnlineLibrary, 2026-06-06)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 4
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, instrumental-variables]
    identification: randomized
  contributionType: [new-fact, new-data]
  introducesData: true
  mechanisms: [behavioral-bias, participation-frictions]
  scope:
    region: UK
    assetClass: retail bank current accounts (overdraft facilities)
    period: 2017-05..2018-03
    frequency: monthly
    dataType: [administrative, experimental]
    granularity: [individual, transaction]
    n: "1.1 million banking customers across Banks A and B; 6 months pretreatment + 5 months posttreatment"
  findings:
    - ref: R1
      outcome: total monthly overdraft and unpaid-item charges
      metric: pp-effect
      value: "Treatment 1 (Bank A just-in-time AOD): -0.528 GBP/month (8.0% reduction); Treatment 4 (Bank B just-in-time UOD+UI): -0.399 GBP/month (3.8% reduction); Treatment 6 (Bank B just-in-time UOD only): -0.557 GBP/month (19% reduction)"
      direction: negative
      vsBenchmark: "all stand-alone just-in-time alerts significant at 1%; effect sizes 3-19% of baseline charges (Table V, p. 487)"
    - ref: R2
      outcome: monthly arranged overdraft charges
      metric: pp-effect
      value: "Treatment 1 (Bank A AOD just-in-time): -0.529 GBP/month (8.4% reduction, p=0.00003); Treatment 2 (Bank B AOD just-in-time): -0.302 GBP/month (3.8%, p=0.00006); Treatment 3 (Bank B AOD early-warning): -0.194 GBP/month (2.4%, p=0.002)"
      direction: negative
      vsBenchmark: "all three stand-alone AOD alerts significant at 1% (Table V, p. 487)"
    - ref: R3
      outcome: monthly overdraft charges (total)
      metric: pp-effect
      value: "Incremental early-warning alerts (Treatments 7-9 postmandate) have statistically insignificant effects; Treatment 9 postmandate: -0.035 GBP/month (0.9%), s.e. 0.052"
      direction: none
      vsBenchmark: "incremental early-warning alerts not distinguishable from zero; stand-alone early-warning alert (premandate) reduces charges by 22-38p/month (Table VI, col. 6, p. 489)"
    - ref: R4
      outcome: days in overdraft per month
      metric: pp-effect
      value: "Treatment 1: -0.499 days/month (8.7%); Treatment 4: -0.063 days/month (15%); Treatment 6: -0.081 days/month (21%)"
      direction: negative
      vsBenchmark: "all stand-alone alerts reduce days in overdraft significantly at 1% (Table VI, p. 489)"
    - ref: R5
      outcome: monthly overdraft charges by overdraft frequency subgroup
      metric: coefficient
      value: "Rare overdrafters (Treatment 1): -0.09 GBP/month (39% effect size); Occasional: -0.67 GBP/month (25%); Frequent: -1.30 GBP/month (5.8%)"
      direction: negative
      vsBenchmark: "absolute benefit rises with overdraft propensity; all three groups significant at 1% for Treatment 1 (Table VIII, p. 493)"
    - ref: R6
      outcome: same-day account logins following alert
      metric: pp-effect
      value: "Treatment 1 day-0 effect: 0.495 additional logins (53% increase over baseline of 0.93 logins); Treatments 9 and 10: 0.27 and 0.13 additional logins"
      direction: positive
      vsBenchmark: "alert raises logins by 10-53% on day of receipt across treatments (Table X, p. 498)"
    - ref: R7
      outcome: same-day account transfers following alert
      metric: pp-effect
      value: "Treatment 1 day-0 effect: 0.272 additional transfers (52% increase over baseline of 0.53); average transfer value ~GBP 465; each alert triggers up to 0.27 transfers"
      direction: positive
      vsBenchmark: "primary mechanism for avoiding overdraft charges is same-day fund transfers, not reduced spending (Table XII, p. 500)"
    - ref: R8
      outcome: probability of exceeding overdraft threshold days in a month
      metric: probability
      value: "Treatment 1: -3.71pp (11%) reduction in probability of any overdraft days; -3.03pp (11%) for over-3-day threshold; -2.58pp (10%) for over-5-day threshold"
      direction: negative
      vsBenchmark: "alerts significantly reduce overdraft across all day-count thresholds 0-15; effects stable in relative terms (Table IX, p. 496-497)"
  resultType: new-finding
  relatesTo:
    - { cite: "Ben-David, Mintz & Sade (2021)", relation: extends, note: "closest prior work on overdraft e-mail alerts; Grubb et al. find larger effects (17-19% vs 3-9%) consistent with higher SMS open rates" }
    - { cite: "Stango & Zinman (2009)", relation: builds-on, note: "inattention hypothesis for overdraft borrowing motivating the alert intervention" }
    - { cite: "Stango & Zinman (2014)", doi: '10.1093/rfs/hhu008', relation: tests, note: "fee salience via surveys does not affect account inflows; alerts do affect inflows via transfers" }
    - { cite: "Agarwal et al. (2015)", relation: cites, note: "CARD Act did not generate waterbed effects; cited as optimistic prior for alerts not triggering bank fee increases" }
  openQuestions:
    - "Whether banks will raise other overdraft charges to offset lost revenue from mandated alert-driven reductions; the paper is optimistic but notes this is left for future work (p. 508)."
    - "Why consumer spending is relatively inelastic to overdraft alerts and whether higher-balance early-warning thresholds would improve effectiveness (p. 504, 507-508)."
    - "Whether alternative interventions such as automatic sweep accounts would further reduce overdraft borrowing that persists even after alerts are active (p. 507)."
  replicationCode:
    status: none
  proposedVocab:
    - { axis: topic, term: consumer-finance, def: "Retail financial products and consumer protection policy, including overdraft, credit cards, payday lending, and household borrowing behavior.", aliases: [retail-finance, consumer-protection] }
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 467-514 plus appendix); eight results extracted from the source PDF. Not human-verified. Not reproduced. FCA-owned bank transaction data used in this paper are proprietary-confidential and not publicly available."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; all 8 Core results rows confirmed against Tables V, VI, VIII, IX, X, XII; equations (1)-(3) verified term-by-term; one fix applied: IV first-stage F-statistic corrected from 10,300,000 to 10,300,300 (Table X caption)."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13404
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2024-12-26"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the identification strategy (two randomized controlled trials at major U.K. banks), the estimating specification (DiD with individual and month fixed effects), and the behavioral mechanism evidence: enough to know what it found and how, without reading all 48 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13404).

## TL;DR

The paper runs at-scale field experiments at two large U.K. retail banks (Banks A and B) with a combined sample of 1.1 million banking customers in 2017 to 2018. Customers are automatically enrolled into various overdraft text alert treatments; a control group receives only the alerts already required by regulation. All tested stand-alone alerts (both just-in-time and early-warning) significantly reduce the overdraft charges they target by 2% to 19%, with just-in-time alerts reducing unarranged overdraft and unpaid item (UOD and UI) charges by 17% to 19% and arranged overdraft (AOD) charges by 4% to 8%. These findings directly informed FCA regulation expanded to all U.K. banks in 2019. Incremental early-warning alerts layered on top of existing just-in-time alerts show no statistically detectable effect. The primary mechanism is that alerts prompt customers to log into their accounts and transfer funds on the same day, rather than cut spending. Alerts help customers across the income and overdraft-frequency distribution, with absolute benefits highest for heavy overdrafters.

## Core results

Magnitudes are as reported; `\*\*`/`\*\*\*` = 5%/1% significance. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Stand-alone just-in-time alerts reduce total monthly charges by 3-19%** across both banks | Table V Panel A, p. 487 | Treatment 1 (Bank A AOD alert): -0.528 GBP/month total (8.0%)\*\*\*; Treatment 4 (Bank B UOD+UI): -0.399 GBP/month (3.8%)\*\*\*; Treatment 6 (Bank B UOD only): -0.557 GBP/month (19%)\*\*\* |
| R2 | **Just-in-time AOD alerts reduce AOD charges 4-8%**; early-warning AOD alert reduces them 2.4% | Table V Panel A, p. 487 | Treatment 1: -0.529 GBP/month (8.4%)\*\*\*; Treatment 2: -0.302 GBP/month (3.8%)\*\*\*; Treatment 3: -0.194 GBP/month (2.4%)\*\*\* |
| R3 | **Incremental early-warning alerts have statistically insignificant effects** on charges once just-in-time alerts are in place | Table V Panel B, p. 488; Table VI col. 7, p. 489 | Treatments 7-9 postmandate: point estimates near zero, not statistically significant; 95% CI rules out effects larger than 14p/month postmandate |
| R4 | **Alerts reduce days in overdraft** by 4-21% per month across stand-alone treatments | Table VI, p. 489 | Treatment 1: -0.499 days/month (8.7%)\*\*\*; Treatment 4: -0.063 days/month (15%)\*\*\*; Treatment 6: -0.081 days/month (21%)\*\*\* |
| R5 | **Absolute benefit rises with overdraft propensity**; low-income and heavy overdrafters both benefit from alerts | Tables VII-VIII, pp. 492-493 | Frequent overdrafters: -1.30 GBP/month AOD (Treatment 1)\*\*\*; Rare overdrafters: -0.09 GBP/month (39% effect size)\*\*\*; all account-inflow terciles show significant reductions |
| R6 | **Alerts raise same-day account logins by 10-53%** on the day they are received | Table X, p. 498 | Treatment 1 (AOD just-in-time): +0.495 logins on day 0 (53% increase); Treatment 9 (early-warning, premandate): +0.27 logins; Treatment 10 (UI): +0.13 logins |
| R7 | **Primary mechanism is fund transfers**, not spending cuts; each alert triggers up to 0.27 same-day transfers averaging GBP 465 | Table XII, p. 500; Table XI, p. 499 | Treatment 1: +0.272 transfers on day 0 (52% increase, average value GBP 465 per transfer, GBP 126 per alert); debit card reduction economically small (-0.08 transactions) |
| R8 | **Alerts reduce the probability of exceeding overdraft thresholds** at all day counts from 0 to 15 days in a month | Table IX, pp. 496-497 | Treatment 1: -3.71pp (11%) for any overdraft day; -3.03pp (11%) for over 3 days; -2.58pp (10%) for over 5 days; -1.74pp (8.4%) for over 10 days |

**Overall (paper's conclusion).** Just-in-time overdraft alerts provide large consumer benefits without offsetting harm: automatic enrollment is the key because active opt-in rates were below 8% prior to mandates. Alerts eliminate less than half of overdraft charges arising from inattention, so scope remains for further interventions. The FCA expanded the CMA's mandate for just-in-time UOD and UI alerts to cover more banks in 2019 and added a mandate for just-in-time AOD alerts, based directly on these findings.

## Theory / model

The paper has no formal structural model. The tested hypothesis is the **inattention hypothesis**: consumers overdraft not because they value credit above its cost, but because they are unaware of their current account balance at the time of transactions (Stango and Zinman (2009), Armstrong and Vickers (2012)). If inattention is the primary friction, then real-time text alerts that notify customers when their balance approaches or crosses an overdraft threshold should allow customers to take corrective action (transfer funds, cut spending) and avoid overdraft charges.

The only prior study of overdraft alert experiments is the contemporaneous work of Ben-David, Mintz, and Sade (2021), who study e-mail alerts sent by the personal finance application Mint. The present study finds larger effects (17-19% vs. 3-9%), consistent with text messages being opened by 99% of recipients while Mint e-mails are opened by only 28-31% of users (p. 472). In contrast to Stango and Zinman (2014), who find that raising overdraft fee salience via a survey question does not affect account inflows, this paper shows that just-in-time text alerts do affect inflows via same-day transfers.

A secondary hypothesis motivates early-warning alerts specifically: by warning customers before the overdraft threshold is crossed, they have more time to cut spending rather than react after the fact. The paper also considers the "waterbed effect" (Agarwal et al. (2015)): mandated reductions in overdraft charges might cause banks to raise other fees, partially offsetting consumer benefits. No evidence for or against this is available from the experimental data; it is left as a question for future work (p. 508).

The **identification strategy** is randomized assignment. Two large U.K. retail banks randomly assigned eligible customers (those with a valid mobile number who incurred overdraft charges and whose balance dropped below GBP 1,000 in the prior six months) to treatment and control groups. Bank A used stratified (block) randomization on key pretreatment variables; Bank B used simple random sampling. Balance on pretreatment observables is verified in Internet Appendix Table IA.XXII. The FCA served as a pre-registration authority: trial dates and sample sizes were agreed in a "Terms of Reference" document before the experiments began (Section IX of the Internet Appendix). An ethics review board approved the protocol (p. 478).

## Method

The primary estimator is an intent-to-treat (ITT) difference-in-differences specification with individual and month fixed effects. The estimating equation is (equation 1, p. 484):

$$
Y_{i,t} = \beta_1 \text{Treatment}_i \times I(t \geq 7) + \beta_2 \text{Treatment}_i \times I(t = 7) + \eta_i + \mu_t + \epsilon_{i,t} \tag{1}
$$

where $$Y_{i,t}$$ is the outcome variable for individual $$i$$ in month $$t$$, $$\text{Treatment}_i$$ is an indicator equal to one if customer $$i$$ was assigned to the treatment group, $$I(t \geq 7)$$ is an indicator for the treatment period (months 7-11), $$I(t = 7)$$ is an indicator for the first treatment month (included separately because observed overdraft charges lag by approximately 25 days due to billing cycles), $$\eta_i$$ are individual fixed effects, $$\mu_t$$ are month fixed effects, and $$\epsilon_{i,t}$$ is an error term. Standard errors are clustered by individual and month. The parameter of interest is $$\beta_1$$, the ITT effect of being automatically enrolled into the treatment alert.

For treatments 4 and 6, which use a staggered-rollout design (design B2 in Figure 3), months 10 and 11 are excluded because all units are treated in those months, following the approach of Goodman-Bacon (2021) who shows that the standard DiD estimate is hard to interpret when treatment effects vary over time.

The behavioral-response analysis uses a second specification to measure same-day account activity following alerts (equation 2, p. 496):

$$
Y_{i,t} = \sum_{k=-3}^{3} \gamma_k (k\text{-Days.after.predicted.alert}_{i,t}) + \lambda \text{Treatment}_i \times I(t \geq 7)
+ \sum_{k=-3}^{3} \beta_k (k\text{-Days.after.alert}_{i,t}) + \eta_i + \mu_t + \epsilon_{i,t} \tag{2}
$$

where $$k\text{-Days.after.alert}_{i,t}$$ equals one if and only if day $$t$$ falls $$k$$ days after the first treatment alert customer $$i$$ received. The indicator for actual alert arrival is instrumented by the predicted alert arrival interacted with treatment (equation 3, p. 497):

$$
k\text{-Days.after.predicted.alert}_{i,t} \times \text{Treatment}_i \times I(t \geq 7) \tag{3}
$$

This IV is needed because receiving an alert is endogenous to opt-in and opt-out decisions, and predicted-alert indicators have measurement error. Customer ($$\eta_i$$) and day ($$\mu_t$$) fixed effects are included; standard errors are clustered by customer and day.

## Empirical specifications

**Main treatment effects (R1-R2, Table V).** The headline specification is equation (1) estimated separately for each of the 11 treatments, with outcomes: (i) observed AOD charges, (ii) UOD and UI charges (sum), and (iii) total charges. Observed charges are deducted from individual accounts once per billing cycle. Effect sizes are reported as $$-100 \cdot \hat{\beta}_1 / \text{baseline mean}$$ where baseline mean is the control group mean in the treatment period. Sample sizes range from 64,654 customers (Treatment 6) to 274,471 (Treatment 10). Adjusted $$R^2$$ ranges from 0.36 to 0.78, reflecting the absorbing power of individual fixed effects.

**Secondary outcomes (R3-R4, Table VI).** The same specification is applied to inferred charges, number of unpaid items, days in overdraft per month, number of overdraft episodes (by length), and number of zero-day overdraft episodes. For treatment 9, pre- and post-mandate periods are estimated separately (design A) to distinguish the stand-alone from incremental alert effect.

**Heterogeneity (R5, Tables VII-VIII).** The main specification is re-estimated within subsamples split by (i) pretreatment account inflows tercile (proxy for income: GBP 0-1,500, GBP 1,500-3,000, GBP 3,000+/month) and (ii) pretreatment overdraft propensity (rare, occasional, frequent overdrafters based on the pretreatment median of positive charges).

**Distribution of days in overdraft (R8, Table IX).** The specification is re-estimated with the binary outcome that days in overdraft exceed thresholds $$d \in \{0, 3, 5, 10, 15, 20, 25, \text{full month}\}$$. Effects are reported in percentage points. Standard errors cluster by customer and month. Stand-alone treatments only.

**Behavioral response (R6-R7, Tables X-XII).** Equations (2)-(3) estimated at Bank A on daily outcomes: number of account logins, number of debit card transactions, and number of account transfers, in the six-day window around alert arrival. IV first-stage F-statistics exceed 10,300,300. Effects are relative to a baseline day defined as four or more days before the first predicted treatment alert.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| FCA-commissioned bank transaction panel (Banks A and B), 2017-2018 | RCT treatment and control data: monthly overdraft charges (AOD, UOD, UI), daily account logins, debit card transactions, transfers; 1.1 million customers, 11 months | No page yet (proprietary-confidential FCA data) |
| FCA representative 6-bank panel, 2015 | Descriptive statistics on U.K. current account market: 1,366,355 accounts, overdraft charges by bank (Table II) | No page yet (proprietary-confidential FCA data) |
| U.K. Competition and Markets Authority (CMA) 2016 data | Context on overdraft usage: over two-thirds of accounts have an overdraft facility; 50% to 60% of days in overdraft avoidable via savings or credit cards | No page yet |
| Follow-up consumer survey (linked to Banks A and B experiments) | Survey of enrolled customers on alert attitudes, actions taken, and reasons for opting out (Internet Appendix Section I) | No page yet |

Sample: treatment period is November 2017 to March 2018 (months 7-11); pretreatment period is May to October 2017 (months 1-6). The FCA-commissioned data include all current accounts held by sampled customers and all their transactions during the sample period.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13404) if you are: designing or evaluating overdraft alert mandates in any jurisdiction; studying the role of inattention in consumer borrowing behavior; building on randomized experiments at U.K. banks under FCA auspices (the Internet Appendix contains the full treatment table, survey details, and all additional robustness tables); or interested in how at-scale field experiments can directly inform regulation. The behavioral-response tables (Tables X-XII) are the most detailed evidence on how alerts mechanically reduce charges.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Grubb, Michael D., Darragh Kelly, Jeroen Nieboer, Matthew Osborne, and Jonathan Shaw.
> "Sending Out an SMS: Automatic Enrollment Experiments for Overdraft Alerts."
> *The Journal of Finance* 80, no. 1 (February 2025): 467–514.
> DOI: 10.1111/jofi.13404. © 2024 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
