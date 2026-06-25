---
title: "Propagation of Cyberattacks through the Financial System: Kotidis & Schreft (2025)"
description: >-
  Distilled: Using confidential Federal Reserve data on a multiday cyberattack on a
  technology service provider, Kotidis and Schreft (2025) quantify first-, second-,
  and third-round propagation effects through the Fedwire payment system, finding
  that business continuity plans and Federal Reserve support materially mitigated
  the disruption. J. Finance 2025, U.S. Government work, public domain in the USA.
  Eight core results with source locators, datasets used, the empirical framework,
  and the estimating equations.
sidebar:
  label: Kotidis-Schreft 2025
  order: 1
tags: [paper-summary, cybersecurity, financial-stability, payment-systems, banking,
       contagion, difference-in-differences, panel-regression, peer-reviewed,
       unreplicated, data:fedwire, data:fed-funds-confidential,
       data:discount-window-confidential, data:call-reports, data:tsp-user-list]
paper:
  authors: Antonis Kotidis, Stacey L. Schreft
  authorList:
    - { family: Kotidis, given: Antonis, orcid: "0000-0003-0109-6254", affiliation: "Board of Governors of the Federal Reserve System" }
    - { family: Schreft, given: Stacey L., affiliation: "Center for Financial Policy, Robert H. Smith School of Business, University of Maryland" }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3313–3358
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13475
  jel:
    codes: [G21, E42, G28]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ["Banking stability, regulation, efficiency", "Blockchain Technology Applications and Security", "Islamic Finance and Banking Studies"]
  dataAccess: proprietary-confidential
  outcome:
    - Fedwire payments sent by user banks (number and value)
    - Fedwire payments received by exposed nonuser banks
    - discount window borrowing probability of exposed receiver-banks
    - federal funds market borrowing by exposed large receiver-banks
    - reserve levels of large exposed receiver-banks
  outcomeClass: [bank-funding]
  license: >-
    U.S. Government work; in the public domain in the USA (stated on artifact p. 3313).
    Crossref DOI metadata shows license content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days=0, start=2025-08-27. The Wiley VOR T&C governs the article
    outside the USA; the public-domain statement covers domestic use.
  licenseShort: public domain (USA)
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/J. Finance site, 2026-06-03)"
  redistribution: extract-only (U.S. Government work; public domain in the USA; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 5
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, event-study]
    identification: natural-experiment
  contributionType: [new-fact]
  mechanisms: [liquidity, networks]
  scope:
    region: US
    assetClass: bank payment flows (Fedwire)
    period: confidential (multiday event, disclosed only as occurring after 2015)
    frequency: daily
    dataType: [administrative]
    granularity: [transaction, firm]
    n: "546,631 sender-receiver-pair-day observations (first-round); 58,357 receiver-bank-day observations (second-round); 304,663 observations (third-round)"
  relatesTo:
    - { cite: "Eisenbach, Kovner & Lee (2022)", relation: builds-on, note: "uses their depository-institution-level RSSD aggregation of Fedwire payment flows and their framework for cyber risk in the US financial system" }
    - { cite: "Duffie & Younger (2019)", relation: tests, note: "finds that the 12 largest US banks had sufficient reserves to withstand the attack, consistent with Duffie and Younger (2019) on wholesale funding cyber runs" }
    - { cite: "Afonso, Kovner & Schoar (2011)", doi: "10.1111/j.1540-6261.2011.01670.x", relation: builds-on, note: "relies on their finding that banks depend heavily on incoming payments to fund outgoing payments; uses Furfine (1999) algorithm following their approach" }
    - { cite: "Acemoglu, Ozdaglar & Tahbaz-Salehi (2015)", doi: "10.1257/aer.20130456", relation: builds-on, note: "places event in the literature on systemic risk and stability in financial networks" }
    - { cite: "Crosignani, Macchiavelli & Silva (2023)", doi: '10.1016/j.jfineco.2022.12.002', relation: cites, note: "other paper quantifying an actual cyber event (NotPetya) through supply chains; the TSP attack differs by being financial-sector focused and multiday" }
    - { cite: "Bertrand, Duflo & Mullainathan (2004)", doi: "10.1162/003355304772839588", relation: builds-on, note: "standard errors two-way clustered at sender-bank and day level following their guidance on DiD standard errors" }
  openQuestions:
    - "Whether omitted variable bias from matching of low-quality bank customers to TSPs with poor cybersecurity can be fully ruled out; a robustness test restricts nonusers to a competing TSP of similar size but causality is not fully established (p. 3317)."
    - "The extent to which the muted third-round effect would change under a more systemic TSP (one of the largest banks as customers) is not quantified; the paper notes the result is sensitive to which TSP is targeted (p. 3333)."
    - "Long-run effects on the TSP's customer base and competitive dynamics in the TSP market are not fully identified; departures after the attack may partly reflect unobservable pre-existing deterioration in the TSP's cybersecurity (p. 3353)."
  findings:
    - { ref: R1, outcome: "Fedwire payments sent by user banks (number and value)", metric: coefficient, value: "-0.395*** (number, day 1); -45% value day 1; -13% number mid-period; -10% number last day", direction: negative }
    - { ref: R2, outcome: "Fedwire payments sent by user banks (number and value)", metric: pp-effect, value: "0.3% of all Fedwire payments disrupted (observed) vs. 0.6% counterfactual without BCPs", direction: positive, vsBenchmark: "counterfactual no-BCP scenario (twice the observed disruption)" }
    - { ref: R3, outcome: "Fedwire payments sent by user banks (number and value)", metric: coefficient, value: "small users -63% value day 1; large users -26% value day 1", direction: mixed, vsBenchmark: "large users vs. small users relative to nonusers" }
    - { ref: R4, outcome: "Fedwire payments received by exposed nonuser banks", metric: coefficient, value: "-0.689*** (SE 0.109) on day 1; -0.403*** mid-period; -0.059 last day", direction: negative }
    - { ref: R5, outcome: "Fedwire payments received by exposed nonuser banks", metric: coefficient, value: "large receivers -0.389** (SE 0.183); small receivers -0.667*** (SE 0.112) on day 1", direction: mixed, vsBenchmark: "large receiver-banks vs. small receiver-banks" }
    - { ref: R6, outcome: "discount window borrowing probability of exposed receiver-banks", metric: coefficient, value: "small low-reserve: 0.025*** (SE 0.006); small high-reserve: 0.014** (SE 0.005); large: -0.165** (SE 0.066)", direction: mixed, vsBenchmark: "small banks more likely, large banks less likely to borrow" }
    - { ref: R7, outcome: "reserve levels of large exposed receiver-banks", metric: coefficient, value: "-18.095*** (SE 3.735) on log(Reserves) day 1; -6.749 mid-period (insignificant)", direction: negative }
    - { ref: R8, outcome: "Fedwire payments received by exposed nonuser banks", metric: coefficient, value: "-0.267* (SE 0.141) day 1; 0.050 mid-period (insig.); -0.020 last day (insig.); large banks +1.692** last day", direction: mixed }
  resultType: new-finding
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: "Full text read (pp. 3313-3358); eight results extracted from the PDF. Not human-verified. Not reproduced. Confidential Federal Reserve data cannot be reproduced outside the Fed."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; R3 locator corrected (col.(4) only, not col.(4) and (6)) and colorful-adjective language removed; all other rows and equations confirmed correct."
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
        Classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) re-checked against the source PDF; removed
        introducesData (paper uses existing Fed administrative data, not a new
        source), removed new-data from contributionType (same reason), removed
        market from scope.dataType (all data are administrative records, no
        market prices used); identification=natural-experiment, mechanisms and
        granularity confirmed correct.
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
        against the source PDF; all eight entries confirmed correct against Tables
        II, IV, V, VII, IX, X; resultType=new-finding is defensible as the
        headline is the first ex-post event quantification, with the tests edge
        for Duffie-Younger (2019) being a secondary confirmation, not the headline
        contribution.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13475
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-27; artifact p. 3313 states 'This article is a U.S. Government work and is in the public domain in the USA'"
  rightsSignalConflict: false
  proposedVocab:
    - { axis: topic, term: cybersecurity, def: "Research on cyberattacks, ransomware, and related operational disruptions in financial markets and the banking system.", aliases: [cyber-risk, cyberattack] }
    - { axis: topic, term: payment-systems, def: "Research on interbank payment infrastructure (Fedwire, CHIPS, SWIFT), intraday liquidity, and payment-system resilience.", aliases: [payment-infrastructure, fedwire-payments] }
    - { axis: topic, term: financial-stability, def: "Research on systemic risk, contagion, and the resilience of financial institutions and markets.", aliases: [systemic-risk, contagion-financial] }
---

**What this is.** The paper's core results, the empirical design (DiD with confidential Federal Reserve data), and the estimating equations: enough to know what was found and how, without reading all 46 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13475).

## TL;DR

This paper is the first to quantify propagation of an actual multiday cyberattack on a major technology service provider (TSP) to the banking sector through the Fedwire payment system. The attack impaired user banks' ability to send payments (first-round effect): on the worst day, users sent 33% fewer payments by number (45% by value) relative to nonusers. Business continuity plans (BCPs) and Fedwire extended hours reduced this by more than half. Exposed nonuser banks (receiver-banks) experienced a liquidity shortfall from reduced incoming payments (second-round effect), which they addressed by borrowing in the discount window or federal funds market, drawing down reserves, and sending payments during extended Fedwire hours. These actions averted broader contagion (third-round effect). Large banks responded more effectively than small ones throughout.

## Core results

Magnitudes and significance are as reported; `*`/`**`/`***` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Users sent significantly fewer payments than nonusers on every day of the attack (first-round effect) | Table II col. (3) and (7), p. 3332 | First day: -33% in number (t-stat implied by -0.395\*\*\*); -45% in value. Mid-period: -13% (number), -19% (value). Last day: -10% (number), -16% (value). All significant at 1%. |
| R2 | Without BCPs (no switching to alternative Fedwire access methods), the first-day drop would have been 100% for users and system-wide disruption would have been twice as large | §V.B, pp. 3333-3334 | Share of all Fedwire payments disrupted: 0.3% observed (0.45%\*0.6%); counterfactual 0.6% (0.6%\*1.0%). |
| R3 | Large users sent substantially fewer payments than small users did relative to nonusers; large users sent 26% fewer payments by value on the first day, versus 63% fewer for small users | Table IV col. (4), pp. 3337-3338 | Small users: -63% value, first day (col. (4) row 1). Large users: -26% (sum of rows 1 and 3, col. (4)). Difference statistically significant. |
| R4 | A 1-percentage-point increase in a receiver-bank's exposure to users is associated with a 0.7% decrease in incoming payments on the first day of the attack (second-round effect) | Table V col. (1), p. 3342 | Coefficient -0.689\*\*\* (SE 0.109). Effect halves in the mid-period (-0.403\*\*\*) and is insignificant on the last day (-0.059). |
| R5 | The contagion was larger for small receiver-banks than large ones; exposure to large users protected large receivers because large users' BCPs were more effective | Table V col. (2)-(3), p. 3342; Table VI, pp. 3344-3345 | Large receivers: -0.389\*\* (SE 0.183) on day 1. Small receivers: -0.667\*\*\* (SE 0.112). Receivers primarily exposed to large users experienced smaller or reversed drops (Table VI). |
| R6 | Exposed small receiver-banks with low reserves were more likely to borrow at the discount window; a 1-pp increase in exposure raised the probability of discount-window borrowing by 0.03% on day 1 | Table VII col. (6), p. 3347 | Coefficient 0.025\*\*\* (SE 0.006). For small banks with high reserves: 0.014\*\* (SE 0.005). Large banks: -0.165\*\* (SE 0.066), i.e., less likely. |
| R7 | Large exposed receivers with high reserves drew them down; a 1-pp increase in exposure is associated with an 18% decrease in reserves on the first day | Table IX col. (1), p. 3350 | Coefficient -18.095\*\*\* (SE 3.735) on log(Reserves). Mid-period -6.749 (insignificant). |
| R8 | Exposed receiver-banks sufficiently compensated for the liquidity shortfall and sent normal payments; no significant third-round effect on payment outflows was detected | Table X col. (1) and (3), p. 3351 | Exposure \* First Day coefficient -0.267\* (SE 0.141); mid-period 0.050 (insignificant); last day -0.020 (insignificant). Large banks sent significantly more payments on the last day (coefficient 1.692\*\*, col. (2)). |

**Overall (paper's conclusion).** The cyberattack had a material impact on individual financial institutions directly and indirectly connected to the TSP, but did not impair the overall financial system. BCPs by users and the TSP, combined with Federal Reserve operational support (Fedwire extended hours, discount window lending), were the primary mitigants. Large banks were more agile in implementing BCPs throughout. The TSP lost approximately 11% of its customers in the year after the attack and another 29% the following year, though other developments may have contributed to these departures.

## Theory / model

The paper has no formal economic model. The analysis tests three hypotheses about propagation through the payment network:

1. The cyberattack disrupts user banks' ability to send Fedwire payments (the common-shock, first-round effect), and BCPs partially offset this disruption.
2. Nonuser banks that normally receive payments from users experience a liquidity shortfall (the contagion, second-round effect), because banks rely on incoming payments to fund outgoing payments (building on Afonso, Kovner, and Schoar (2011)).
3. Unless receiver-banks can obtain alternative funding or rely on reserves, their inability to send their own payments creates further contagion to yet other banks (the third-round effect).

The identification strategy is a difference-in-differences design exploiting the common shock to users: the TSP taking its systems offline is a plausibly exogenous shock to user banks only. Nonusers faced no similar operational disruption. The analysis is in the spirit of Eisenbach, Kovner, and Lee (2022), who develop an ex-ante framework for measuring cyber risk in the US financial system; the present paper provides the first ex-post quantification using an actual event. Acemoglu, Ozdaglar, and Tahbaz-Salehi (2015) provide the theoretical backdrop for systemic risk and stability in financial networks.

The main threat to identification is selection: low-quality customers may match to TSPs with poor cybersecurity and also be less adept at implementing BCPs. To mitigate this, robustness tests restrict the control group to banks that use a competing TSP of similar revenue size, and match on log(assets) via propensity-score matching (pp. 3331, 3317). The paper states that full causal identification is not established (p. 3317). The event is also more severe than the hypothetical cyber run analyzed by Duffie and Younger (2019) because it is multiday and involves operational disruption, not only funding pressure. Crosignani, Macchiavelli, and Silva (2023) study propagation of the NotPetya cyberattack through firm supply chains; the present paper differs by focusing on a financial-sector TSP and Fedwire payment contagion.

The payment-network structure matters for the second-round analysis: large receiver-banks were primarily exposed to large users, while small receiver-banks were more uniformly exposed. Because large users implemented BCPs more effectively, large receivers fared better (pp. 3341, 3343).

## Method

The paper applies a panel difference-in-differences estimator to confidential daily transaction-level Fedwire data. There is no proposed novel method; the contribution is the first quantification of actual (not hypothetical) multiday cyberattack propagation using regulatory micro-data. The design builds on `difference-in-differences`, `panel-regression`, and `event-study` techniques.

**First-round estimator (Equation 1, p. 3330).** The dependent variable is the log change in the number or dollar value of Fedwire payments sent by sender-bank $$s$$ to receiver-bank $$r$$ on day $$t$$ relative to the same day one week earlier:

$$
\Delta \log(\text{Payments})_{srt} = \beta_1 \times \text{Users}_s \times \text{FirstDay}_t + \beta_2 \times \text{Users}_s \times \text{MidPeriod}_t + \beta_3 \times \text{Users}_s \times \text{LastDay}_t + FE + \varepsilon_{srt} \tag{1}
$$

where $$\text{Users}_s$$ is one if sender $$s$$ was a user of the TSP, $$\text{FirstDay}_t$$ ($$\text{LastDay}_t$$) is one on the first (last) day of the event, and $$\text{MidPeriod}_t$$ is one between first and last days. Fixed effects are added progressively. The preferred specification includes receiver-bank-by-day and sender-bank-by-receiver-bank fixed effects. Standard errors are two-way clustered at the sender-bank and day level (Bertrand, Duflo, and Mullainathan (2004)).

The log difference uses the day-before-the-same-weekday convention to account for weekly seasonality in Fedwire flows (Treasury settlement days on Thursdays, mid-month, and end-of-month); the upper 99th percentile of transactions is winsorized (p. 3330).

**Second-round estimator (Equation 2, p. 3342).** For exposed receiver-banks, the dependent variable is the log change in the value of incoming Fedwire payments:

$$
\Delta \log(\text{Payments})_{rt} = \sum_{\text{days}} \left( \beta_{\text{day}} \times \text{Exposure}_r \times \text{DayDummy}_t \right) + FE + \varepsilon_{rt} \tag{2}
$$

where $$\text{Exposure}_r$$ is the share of receiver-bank $$r$$'s total incoming payments (over a look-back window before the attack) originating from user banks. The model includes receiver-bank and day fixed effects. Standard errors are two-way clustered at the receiver-bank and day level.

**Third-round estimator (p. 3351).** Table X regresses the log change in the value of payments sent by exposed receiver-banks (now acting as senders) on the same exposure measure interacted with day dummies, controlling for receiver-bank-by-day FE and sender-bank-by-receiver-bank FE. The large-bank triple interaction isolates size heterogeneity.

**Size heterogeneity (Equation 1 extended, pp. 3335-3336).** Equation (1) is augmented with a $$\text{LargeBank}_s$$ dummy and its interactions with the day dummies and the $$\text{Users}$$ dummy to form a triple difference-in-differences. This captures the additional payment drop for small versus large users (Table IV).

## Empirical specifications

**First-round result (R1, Table II).** Specification: Equation (1). Preferred columns (3) and (7) include receiver-bank-by-day FE and sender-bank-by-receiver-bank FE. Three-month window. U.S. G-SIBs excluded from the sender group (included in robustness, Internet Appendix Table IA.I). Sample: all Fedwire sender-receiver pairs with at least one payment in the window; 546,631 observations.

**Mitigant analysis (R2, Table III).** Identical to Table II but payments after 6:30 p.m. are excluded to isolate normal business-hour effects; the extended-hours contribution is inferred by comparison. Table II column (3) vs. Table III column (3): -0.395 vs. -0.393 first-day effect in number; -0.590 vs. -0.695 in value (Table II col. (7) vs. Table III col. (7)), showing extended hours raised value sent by about 5 percentage points.

**Size heterogeneity (R3, Table IV).** Triple DiD version of Equation (1). Dependent variable: log change in value (columns (4)-(6)) or number (columns (1)-(3)) of payments. Large bank is above-sample-average log(assets). Key interaction terms: $$\text{Users} \times \text{LargeBank} \times \text{FirstDay}$$; $$\text{Users} \times \text{FirstDay}$$. Columns (5)-(6) use extended Fedwire hours; (2)-(3) and (5)-(6) include individual user and TSP adaptation controls.

**Second-round: contagion (R4-R5, Table V).** Specification: Equation (2). Dependent variable: $$\Delta \log(\text{Value of Payments received})$$. Three columns: all receivers, large receivers only, small receivers only. Receiver-bank FE and day FE. Two-way clustered at receiver-bank and day. Observations: 58,357 (all), 5,673 (large), 52,684 (small).

**Contagion by user size (R5, Table VI).** Augments Equation (2) with a second exposure layer: the share of the receiver's user-originated payments coming from large versus small users, at threshold levels of 80%, 50%, 20%. This decomposes the asymmetric contagion finding (pp. 3343-3346).

**Discount window borrowing (R6, Table VII).** LPM regression: $$P(\text{DW}_{rt} > 0 | \text{DW}_{t-1} = 0) = \text{Exposure}_r \times \text{DayDummies}_t + \text{ReceiverBank FE} + \text{FedReservDistrict} \times \text{Day FE} + \varepsilon_{rt}$$. Dependent variable is the dummy for first-time discount-window borrowing at time $$t$$ conditional on no prior use at $$t-1$$. Split by bank size and reserve-to-asset ratio (columns (1)-(6)).

**Reserve drawdowns (R7, Table IX).** Regression of $$\log(\text{Reserves}_{rt})$$ on $$\text{Exposure}_r \times \text{DayDummies}_t$$ for the subset of large banks with relatively high reserves (those from Table VIII column (4)). Receiver-bank FE and day FE; 82 observations.

**Third-round: payments sent by exposed receivers (R8, Table X).** Regression of $$\Delta \log(\text{Value of Payments sent})_{rt}$$ on $$\text{Exposure}_r \times \text{DayDummies}_t$$, with receiver-bank-by-day FE and sender-bank-by-receiver-bank FE, 304,663 observations. Extended and normal business hours compared across columns.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Fedwire Funds Service transaction-level data (confidential) | Daily sender-receiver-pair payment flows; treatment and outcome for first- and third-round DiD | No page yet |
| List of users of the TSP (confidential) | Treatment-group indicator (user vs. nonuser); identifies which banks could not access normal TSP services | No page yet |
| Federal funds loan-level data (Furfine algorithm, confidential) | Interbank borrowing outcome for large exposed receiver-banks; cross-checked against FR 2420 and FHLB 10-Ks | No page yet |
| Discount window daily borrowing records (confidential) | Discount-window borrowing outcome for small exposed receiver-banks | No page yet |
| Federal Reserve confidential reserve accounting records | End-of-day reserves held at the Federal Reserve; used for reserve-drawdown analysis (Table IX) | No page yet |
| Call Reports (FFIEC / FDIC) | Balance sheet data (total assets) for size classification | [Call Reports](/wiki/datasets/call-reports/) (public) |

Sample: event window is a confidential multiday period (not disclosed to protect anonymity of the TSP and the event). The three-month analysis window spans the month before, the event days, and the month after. Frequency: daily payment flows; balance sheet data matched at quarterly frequency.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13475) if you are: designing business continuity or third-party risk management requirements for banks or TSPs; studying payment-system contagion and the role of central-bank operational support; extending the empirical design to other cyber events (Internet Appendix Tables IA.I-IA.IV have robustness results and summary statistics); or evaluating whether larger or smaller banks should hold larger liquidity buffers as a first line of defence against operational disruptions. The locators above point to the exact tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025. This distillation was extracted by an LLM on 2026-06-03 and is **not human-verified or independently reproduced**. The underlying data are confidential Federal Reserve records and cannot be reproduced outside the Federal Reserve. Redistribution is extract-only (Wiley VOR terms outside the USA).

> Kotidis, Antonis, and Stacey L. Schreft. "The Propagation of Cyberattacks through the
> Financial System: Evidence from an Actual Event." *The Journal of Finance* 80, no. 6
> (December 2025): 3313-3358. DOI: 10.1111/jofi.13475.
> This article is a U.S. Government work and is in the public domain in the USA.
> Extract-only outside the USA (Wiley VOR terms and conditions).
