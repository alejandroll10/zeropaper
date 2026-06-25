---
title: "Personal Communication in an Automated World: Laudenbach & Siegel (2025)"
description: >-
  Distilled: Personal two-way phone communication between a bank agent and a
  delinquent borrower increases timely repayment by 34.4 percentage points,
  reduces default by 23.8 percentage points, and reduces loan termination by
  12.4 percentage points, identified via an IV exploiting random day-of-first-call
  variation. Evidence from a large German bank's early collection call center,
  Jan-Jun 2012, N=3,448 POS loan borrowers. J. Finance 2025, paywalled. Seven
  core results with source locators, datasets used, the model (IV framework),
  and the method (2SLS + MTE estimation).
sidebar:
  label: Laudenbach-Siegel 2025
  order: 1
tags: [paper-summary, consumer-finance, household-finance, banking, lending-relationships,
       panel-regression, instrumental-variables, peer-reviewed, unreplicated]
paper:
  authors: Christine Laudenbach, Stephan Siegel
  authorList:
    - { family: Laudenbach, given: Christine, orcid: "0000-0002-2452-5683", affiliation: "Goethe University Frankfurt, Leibniz Institute SAFE, CESifo" }
    - { family: Siegel, given: Stephan, orcid: "0000-0002-7938-6940", affiliation: "Foster School of Business, University of Washington, CESifo" }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 515-559
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13388
  jel:
    codes: [G21, G51, D91]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - FinTech, Crowdfunding, Digital Finance
    - Islamic Finance and Banking Studies
    - Banking stability, regulation, efficiency
  dataAccess: proprietary-confidential
  outcome:
    - probability of timely loan repayment within 45 days of delinquency
    - probability of default (90+ days overdue)
    - probability of loan termination by bank
    - probability of future delinquency
  outcomeClass: [household-finance, credit-risk]
  license: "Wiley VOR terms (not CC; paywall; content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0, start 2024-11-28; confirmed via Crossref DOI metadata 2026-06-06)"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site; confirmed via Crossref metadata 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 8

  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [instrumental-variables, panel-regression]
    identification: instrument

  contributionType: [new-fact, new-data]
  mechanisms: [behavioral-bias, moral-hazard]
  introducesData: true

  scope:
    region: Germany
    assetClass: consumer installment loans (POS loans)
    period: 2012-01..2014-08
    frequency: mixed
    dataType: [administrative]
    granularity: [individual, transaction]
    n: "3,448 delinquent POS borrowers (main sample); 2,499 overdraft borrowers (extension); 245 borrowers + 13 agents (survey sample)"

  findings:
    - ref: R1
      outcome: probability of timely loan repayment within 45 days of delinquency
      metric: pp-effect
      value: "+34.4 pp (2SLS, SE=0.089, p<0.01)"
      direction: positive
      vsBenchmark: "vs. untreated borrowers receiving only written letters; OLS estimate +20.1 pp"
    - ref: R2
      outcome: probability of default (90+ days overdue)
      metric: pp-effect
      value: "-23.8 pp (2SLS, SE=0.077, p<0.01)"
      direction: negative
      vsBenchmark: "vs. untreated borrowers; OLS estimate -12.1 pp"
    - ref: R3
      outcome: probability of loan termination by bank
      metric: pp-effect
      value: "-12.4 pp (2SLS, SE=0.046, p<0.01)"
      direction: negative
      vsBenchmark: "vs. untreated borrowers; OLS estimate -7.2 pp"
    - ref: R4
      outcome: probability of timely loan repayment within 45 days of delinquency
      metric: pp-effect
      value: "ATE: +16.6 to +20.1 pp (polynomial and semiparametric MTE models)"
      direction: positive
      vsBenchmark: "vs. LATE/2SLS of +34.4 pp; ATEs are roughly half the size (Table V, Panel B)"
    - ref: R5
      outcome: probability of loan termination by bank
      metric: pp-effect
      value: "-23.5 pp for Termination: Overall (vs. -12.4 pp for Termination: Now); F-test p=0.021 for equality"
      direction: negative
      vsBenchmark: "treatment effect on overall loan termination almost doubles that on immediate termination (Table XI, Panel A)"
    - ref: R6
      outcome: probability of future delinquency
      metric: pp-effect
      value: "-7.9 pp (OLS, SE=0.019, p<0.01); delta=1.97 for Oster (2019) robustness"
      direction: negative
      vsBenchmark: "conditional on resolving the initial delinquency; time to next delinquency delayed by ~29 days (Table XI, Panel B)"
    - ref: R7
      outcome: probability of timely loan repayment within 45 days of delinquency
      metric: pp-effect
      value: "+1 SD in Likeable Voice associated with +4 pp payment probability (OLS, p<0.10)"
      direction: positive
      vsBenchmark: "agent voice likeability effect controlling for agent age/gender and borrower/loan characteristics (Table X)"

  resultType: new-finding

  relatesTo:
    - { cite: "Karlan, Morten & Zinman (2015)", doi: '10.1177/237946151500100204', relation: extends, note: "shows personal touch in text reminders (name of loan officer) raises repayment; this paper moves from text to live two-way voice communication" }
    - { cite: "Berg (2015)", doi: '10.1093/rfs/hhv040', relation: cites, note: "documents value of human risk assessment for mortgage lending quality" }
    - { cite: "Bursztyn et al. (2019)", doi: '10.1086/701605', relation: cites, note: "moral/reputational incentive messages increase credit card repayment among delinquent Indonesian borrowers" }
    - { cite: "Drexler & Schoar (2014)", doi: '10.1287/mnsc.2014.1957', relation: cites, note: "loan officer turnover reduces borrower future loan access" }
    - { cite: "Petersen & Rajan (1994)", doi: '10.1111/j.1540-6261.1994.tb04418.x', relation: cites, note: "foundational paper on benefits of lending relationships for screening and monitoring" }
    - { cite: "Heckman & Vytlacil (1999)", doi: '10.1073/pnas.96.8.4730', relation: builds-on, note: "local IV / marginal treatment effect framework used to estimate MTEs and ATEs" }

  openQuestions:
    - "Whether the results generalize to robocalls (automated calls with recorded messages) or whether the presence of an actual human is essential; recent experimental evidence (Marechal et al. (2021)) suggests human presence may matter (p. 556)."
    - "External validity beyond early-stage delinquency collection and beyond Germany's regulatory and cultural context; the study covers only the early collection stage and borrowers not in bankruptcy proceedings (p. 555)."
    - "Whether extending the treatment to currently unreached borrowers (those with very high unobservable resistance) would yield larger or smaller average effects, given that MTEs are increasing in unobservable resistance (p. 542)."

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-06", role: extracted, note: "Full PDF read (pp. 515-559, all tables and figures); seven results extracted from the paywalled PDF. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core-results rows confirmed correct (Tables III, IV, V, X, XI). Fixed two errors: (1) selection equation mis-tagged as equation (2), but it is inline prose on p. 536, not a numbered equation; PDF equation (2) is the heterogeneous-TE outcome model; tag and description corrected. (2) German Default coefficient in Empirical specifications missing its negative sign (-0.320*** per Table IX); corrected."

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13388", checked: "2026-06-06", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-11-28. NOT a CC licence. Paywalled." }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the institutional setup, the IV design, and the empirical specifications with the key equations: enough to know what it found and how, without reading all 45 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13388).

## TL;DR

At a large German bank in 2012, delinquent POS loan borrowers who spoke with a randomly assigned bank agent were significantly more likely to repay their overdue loan within 45 days than those who received only a standard written letter. Using the day of the first call attempt (Saturday vs. Monday) as an instrumental variable for whether a borrower actually spoke with an agent (*Talk*), the paper finds that personal two-way communication increases timely repayment by 34.4 percentage points, decreases the probability of default by 23.8 percentage points, and decreases immediate loan termination by 12.4 percentage points. The treatment effect is concentrated among borrowers who are harder to reach, marginal treatment effects increase in unobservable resistance, and average treatment effects (ATEs) are roughly half the size of the LATE. The likeability of the agent's voice is a significant predictor of payment, consistent with the prosocial or promise-keeping channel rather than a simple reminder effect. The effect persists: speaking with an agent also reduces future delinquency probability by 7.9 percentage points.

## Core results

Magnitudes and significance are as reported; \*\*\*/\*\*/\* = 1%/5%/10%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Personal communication increases timely repayment by 34.4 pp** (2SLS, N=3,448) | Table IV, Panel A, col. (1), p. 534 | Talk coef. = 0.344\*\*\* (SE=0.089); OLS = 0.201\*\*\* (SE=0.021) |
| R2 | **Personal communication reduces default by 23.8 pp** (2SLS) | Table IV, Panel A, col. (2), p. 534 | Talk coef. = -0.238\*\*\* (SE=0.077); OLS = -0.121\*\*\* (SE=0.016) |
| R3 | **Personal communication reduces immediate loan termination by 12.4 pp** (2SLS) | Table IV, Panel A, col. (3), p. 534 | Talk coef. = -0.124\*\*\* (SE=0.046); OLS = -0.072\*\*\* (SE=0.015) |
| R4 | **Average treatment effects are roughly half the LATE**: ATE for Payment = +16.6 to +20.1 pp | Table V, Panel B, p. 538 | ATE (polynomial) = 0.201\*\*\* (SE=0.053); ATE (semipar.) = 0.166\*\*\* (SE=0.046) |
| R5 | **Treatment effect on overall loan termination almost doubles** when looking beyond the initial delinquency | Table XI, Panel A, p. 553 | Talk coef. = -0.235\*\*\* (Termination: Overall, SE=0.069) vs. -0.124\*\*\* (Termination: Now); F-test p=0.021 |
| R6 | **Personal communication reduces future delinquency probability by 7.9 pp** and delays the next delinquency by ~29 days | Table XI, Panel B, p. 553 | OLS: Talk coef. = -0.079\*\*\* (SE=0.019); Oster (2019) delta=1.97 (>1, endogeneity unlikely) |
| R7 | **Agent voice likeability raises payment probability by 4 pp per 1-SD increase**, supporting the prosocial channel | Table X, p. 551 | OLS (survey sample, N=135): Likeable Voice (adjusted) coef. = 0.261\*\* (SE=0.040, wild bootstrap p) |

**Overall (paper's conclusion).** Personal, two-way communication between a bank agent and a delinquent borrower significantly increases the probability that the delinquency is resolved and that default and loan termination are avoided. The effect is unlikely to operate mainly through payment reminders or the bank's monitoring signal; evidence on agent voice likeability, German-vs.-non-German borrowers, and persistence beyond the initial delinquency all point to the personal or prosocial dimension of the phone conversation as the key channel.

The paper situates itself in a literature on banking relationships (Petersen and Rajan (1994), Drexler and Schoar (2014)) and on behavioral interventions for delinquent borrowers (Karlan, Morten, and Zinman (2015), Bursztyn et al. (2019)). Berg (2015) documents that human risk assessment improves loan quality, providing context for the value of the human element studied here.

## Theory / model

The paper has no formal structural model. The identification framework is an IV design with two instruments.

**Conceptual setup.** All borrowers in the sample receive a written letter from the bank informing them of the delinquency and requesting payment within two weeks. Treated borrowers (*Talk* = 1) additionally speak with a randomly assigned bank agent during the phone conversation. The agent may not convey additional information beyond the letter, may not change loan terms, and may not accept payment over the phone. Differences in payment behavior between treated and untreated borrowers are therefore due to the FORM of communication (personal vs. impersonal), not to information content or loan modification.

**Potential mechanisms discussed (Section III, pp. 543-552):**
1. Payment reminder / attention to the bank's enforcement process (ruled out by finding no differential effect by outstanding loan amount and no effect of borrower surprise about the call, Table VI and Table VII).
2. Personalized monitoring through a follow-up call (ruled out as the primary driver: 65-90% of the treatment effect obtains without a follow-up call, Table VIII).
3. Prosocial / promise-keeping behavior: a likeable agent voice significantly raises payment (Table X), and German borrowers (lower social distance) benefit more than non-German borrowers (Table IX, significant for *Default*). This channel is consistent with the literature on prosocial behavior and its sensitivity to social distance.

**Heterogeneous treatment effects (Section II.C, pp. 535-542).** The paper uses the Heckman-Vytlacil (1999, 2001, 2005) marginal treatment effect (MTE) framework. Borrower *i* speaks with an agent if their propensity score exceeds their unobservable resistance $$U_i$$ (prose on p. 536, not a numbered equation):

$$
Talk_i = \mathbf{1}\{f(X_i, Z_i) > V_i\}
$$

where $$Z_i$$ are the instruments (day-of-first-call indicators) and $$V_i$$ is unobservable resistance. The MTE characterizes the treatment effect as a function of unobservable resistance $$U_i$$ (the quantile of $$V_i$$), stated as equation (3) in the paper (p. 536):

$$
MTE(X_i = x, U_i = u) = \gamma + x(\beta_{T=1} - \beta_{T=0}) + E[\mathcal{E}_{T=1,i} - \mathcal{E}_{T=0,i} \mid U_i = u] \tag{3}
$$

MTEs are increasing in unobservable resistance: borrowers who are harder to reach respond more to the phone conversation than easy-to-reach borrowers, ruling out positive selection into treatment.

## Method

The paper uses linear IV (two-stage least squares) as the primary estimator, with the Heckman-Vytlacil MTE framework for heterogeneous treatment effects, and OLS for the mechanism and long-run tests where instruments are not available.

**IV approach (Section II.B, pp. 531-532).** The estimating equation (equation 1, p. 531) is:

$$
Y_i = \alpha + \gamma \, Talk_i + \beta X_i + L + M + \mathcal{E}_i \tag{1}
$$

where $$Y_i \in \{Payment_i, Default_i, Termination_i\}$$, $$Talk_i$$ is the endogenous indicator for whether the borrower spoke with a bank agent, $$X_i$$ is a vector of borrower and loan characteristics, $$L$$ are location fixed effects, and $$M$$ are month fixed effects. Standard errors are clustered at the location level.

The instruments are *First Call Saturday* (= 1 if the borrower's first call attempt falls on a Saturday) and *First Call Monday* (= 1 if Monday). The bank treats Saturday and Monday as a single day with random assignment by an auto-dialer, giving overall reachability rates of 96% (Saturday) vs. 43% (Monday) vs. 71% (Tuesday-Friday) as documented in Figure 3 (p. 529). The first-stage F-statistic is 155.92 (full sample, Table III, p. 533), well above Stock-Yogo (2005) thresholds.

**MTE estimation.** The Andresen (2018) *mtefe* estimator is used with both a parametric second-order polynomial approximation and a semiparametric approximation. Standard errors are bootstrapped with 100 repetitions, accounting for location-level clustering. ATEs are recovered by averaging MTEs over the [0, 1] interval of $$U_i$$, with the identifying assumption that MTEs are zero for $$U_i < 0.40$$ (i.e., no reversal of effect for always-takers).

## Empirical specifications

All main results use the linear IV (2SLS) specification above. Below are the key specifications tied to the core results.

**Main 2SLS (R1-R3, Table IV Panel A, p. 534):** Outcome $$Y_i \in \{Payment, Default, Termination:Now\}$$ regressed on $$Talk_i$$ instrumented by *(First Call Saturday, First Call Monday)*, controlling for installment amount, initial loan amount, interest rate, repayment term, time since origination, gender, national origin, age, age squared, employment status, month FE, and location FE. N = 3,448. Standard errors clustered at location.

**Robustness subsample (Table IV Panel B, p. 535):** Restricted to borrowers whose files enter the call center on a Thursday and who are first called on Saturday or Monday (N = 432), so the instruments are entirely generated by the auto-dialer's random Saturday/Monday assignment. Results are qualitatively similar but slightly smaller in magnitude.

**Heterogeneous treatment effects (Table V, pp. 537-538):** Equation 2 allows $$\beta$$ to interact with $$Talk$$; $$\beta_{T=1} - \beta_{T=0}$$ captures differential treatment effects by observable characteristics. No significant heterogeneity found for most observables; retired borrowers and older borrowers benefit less.

**Mechanism: loan amount split (Table VI, p. 544):** 2SLS estimated separately for borrowers with below- and above-median outstanding loan amount (N = 1,724 each). No significant difference in Talk coefficients (p-value for equality reported), ruling out a simple reminder/attention effect.

**Mechanism: follow-up call counterfactual (Table VIII, p. 548):** Two alternative outcomes (*Payment: Alt. 1* and *Payment: Alt. 2*) absorb the contribution of the follow-up call. 2SLS on these alternatives gives Talk coefficients of 0.223\*\* and 0.310\*\*\*, or 65% and 90% of the baseline 0.344\*\*\*, confirming the follow-up call accounts for at most 35% of the total effect.

**Mechanism: nationality (Table IX, p. 549):** 2SLS split by German (N = 2,745) vs. non-German (N = 703) borrowers. The Talk effect on *Default* is -0.320\*\*\* for Germans vs. 0.025 for non-Germans (p-value for equality = 0.016), consistent with social distance moderating the prosocial channel.

**Mechanism: agent voice likeability (Table X, p. 551):** OLS on survey sample (N = 135) regressing *Payment* on *Likeable Voice (adjusted)* (rater-adjusted fraction of raters rating agent's voice 4 or 5 out of 5), controlling for agent age, agent gender, borrower characteristics, loan characteristics, call duration, and whether it is a first call. Wild bootstrap t-approach with 1,000 repetitions accounts for the small number of agent clusters.

**Long-run effects (Table XI, pp. 553-554):** 2SLS for *Termination: Overall* (any termination by August 2014); OLS for *Future Delinquency*, *Time to Next Delinquency*, and *Termination: Later* on the subsample of borrowers who resolve the initial delinquency (N = 3,092), with Oster (2019) delta computed to assess endogeneity concern.

**External validity: overdraft borrowers (Table XII, p. 556):** Same IV specification applied to N = 2,499 overdraft facility borrowers (distinct from POS sample). Talk increases payment by 20.4 pp and reduces default and termination by 15.3 pp and 12.2 pp, respectively, all significant at 10%.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Proprietary administrative loan data, large German bank (POS loans, Jan-Jun 2012) | Main sample: 3,448 first-time delinquent POS borrowers; borrower characteristics, loan terms, call center records, payment outcomes through Aug 2014 | No page yet |
| Proprietary administrative loan data, large German bank (overdraft borrowers, Jan-Jun 2012) | External validity sample: 2,499 overdraft borrowers with existing bank relationship | No page yet |
| Survey of call center agents (February 2016) | Agent assessments of 245 borrower conversations; voice recordings of 8 agents rated by 6-7 raters for likeability | No page yet |

Sample scope: POS loan data from a large German bank, one of Germany's top-5 retail banks by assets, with 1,000+ branches and 10 million+ retail customers. Borrowers are first-time delinquent POS loan holders with a valid phone number, no prior bank relationship, not in bankruptcy, entering the call center pool January-June 2012. Outcome follow-up through August 2014 (~2.5 years after delinquency).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13388) if you are:
studying the value of human vs. automated customer communication; evaluating early collection call center policies; applying the Heckman-Vytlacil MTE framework to estimate ATEs from IV complier effects; studying how social distance and agent characteristics mediate behavioral treatment effects; or comparing German POS and overdraft loan markets. Table IV (p. 534) is the headline result; Table XI (p. 553) has the long-run effects; Table X (p. 551) has the voice likeability evidence.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025. Published online November 28, 2024. DOI: [10.1111/jofi.13388](https://doi.org/10.1111/jofi.13388). Copyright 2024 the American Finance Association. Paywalled. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract-only; no PDF hosted here.

> Laudenbach, Christine, and Stephan Siegel. "Personal Communication in an Automated World: Evidence from Loan Repayments." *The Journal of Finance* 80, no. 1 (February 2025): 515-559. DOI: 10.1111/jofi.13388.
