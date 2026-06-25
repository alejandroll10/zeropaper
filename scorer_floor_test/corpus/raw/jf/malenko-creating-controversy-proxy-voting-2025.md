---
title: "Creating Controversy in Proxy Voting Advice: Malenko, Malenko & Spatt (2025)"
description: >-
  Distilled: A profit-maximizing proxy advisor optimally produces fully informative
  research reports but partially informative, asymmetrically biased vote recommendations
  that favor the a priori unlikely alternative, increasing the incidence of close,
  contentious votes to enhance the value of its advice. J. Finance 2025, CC BY-NC-ND 4.0.
  Seven core results with source locators, the information-design model, and the Bayesian
  persuasion method with its defining equations.
sidebar:
  label: Malenko-Malenko-Spatt 2025
  order: 1
tags: [paper-summary, corporate-governance, proxy-voting, information-design,
       shareholder-voting, peer-reviewed, unreplicated]
paper:
  authors: Andrey Malenko, Nadya Malenko, Chester Spatt
  authorList:
    - { family: Malenko, given: Andrey, affiliation: Boston College }
    - { family: Malenko, given: Nadya, affiliation: Boston College }
    - { family: Spatt, given: Chester, affiliation: Carnegie Mellon University }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 2303–2354
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13438
  jel:
    codes: [G34, D82, D83]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Game Theory and Applications", "Auction Theory and Applications", "Political Influence and Corporate Strategies"]
  dataAccess: public
  outcome:
    - proxy advisor vote recommendation design (informativeness and bias)
    - probability of a close (split) shareholder vote
    - subscriber demand for proxy advisory research reports
  outcomeClass: [social-welfare]
  license: >-
    CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0,
    start 2025-03-16; corroborated by artifact p.2303 Creative Commons
    Attribution-NonCommercial-NoDerivs License notice)
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access PDF available via Wiley online library (2026-06-05)"
  redistribution: extract-only (CC BY-NC-ND 4.0 does not permit mirroring or adaptation)
  resultsCount: 7
  citedByCount: 3
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, bayesian-persuasion]
  contributionType: [new-theory, new-fact]
  mechanisms: [information-asymmetry, agency]
  scope:
    region: US
    assetClass: corporate shareholder votes
  relatesTo:
    - { cite: "Kamenica and Gentzkow (2011)", doi: '10.1257/aer.101.6.2590', relation: builds-on, note: "Bayesian persuasion framework; advisor's problem is an information-design problem with Bayes plausibility constraint (concavification)" }
    - { cite: "Rayo and Segal (2010)", doi: '10.1086/657922', relation: builds-on, note: "information design by a sender who maximizes a function of the receiver's posterior" }
    - { cite: "Malenko and Shen (2016)", doi: '10.1093/rfs/hhw070', relation: cites, note: "empirical evidence on ISS recommendations and shareholder voting outcomes used to corroborate the model" }
    - { cite: "Iliev and Lowry (2015)", doi: '10.1093/rfs/hhu062', relation: cites, note: "evidence that larger shareholders are less likely to follow blanket recommendations, consistent with high-v_i active-voter prediction" }
    - { cite: "Ertimur, Ferri, and Oesch (2013)", doi: '10.1111/1475-679x.12024', relation: cites, note: "content of ISS research reports and variability in concerns when ISS issues a negative recommendation" }
  openQuestions:
    - "How the model's mechanism changes when shareholders can coordinate (communication among shareholders is assumed away due to acting-in-concert rules; p. 2340)."
    - "Whether results hold when information acquisition by the advisor is costly and the signal is noisy (analyzed in Internet Appendix Section IV.C but kept separate from the baseline; pp. 2341-2342)."
    - "Optimal recommendation design when shareholders have ideological preferences that counteract prior beliefs (Section V.B / Internet Appendix Section IV.F; p. 2339)."
  findings:
    - ref: R1
      outcome: proxy advisor vote recommendation design
      metric: probability
      value: "Optimal public recommendation is binary {0,1} (against/for); when priors are sufficiently asymmetric and q < 1/2, the recommendation against the prior is given more often than the true probability that the proposal is value-decreasing (Proposition 4, p. 2325)"
      direction: positive
      vsBenchmark: partially informative recommendation dominates fully informative and uninformative designs when priors are asymmetric
    - ref: R2
      outcome: probability of a close (split) shareholder vote
      metric: probability
      value: "Average probability of a split vote is maximized by a partially informative recommendation; for sufficiently asymmetric priors (e.g. mu = 0.8, q = 0.01) the controversial negative recommendation induces posterior mu_0 close to 0.5, generating a high split-vote probability (Figure 3 Panel B, p. 2323)"
      direction: positive
      vsBenchmark: exceeds the split-vote probability under any fully informative or uninformative recommendation
    - ref: R3
      outcome: proxy advisor vote recommendation design
      metric: probability
      value: "When priors are close to 0.5 (mu in (1/2 - eps, 1/2 + eps)), the optimal public recommendation is uninformative (Proposition 5, p. 2327); ISS board-declassification recommendations are always positive with zero negative recommendations 2010-2019, consistent with uninformative design"
      direction: none
      vsBenchmark: uninformative design optimal near mu = 0.5 because split votes already likely without intervention
    - ref: R4
      outcome: subscriber demand for proxy advisory research reports
      metric: probability
      value: "Shareholder i subscribes iff v_i >= f / V(q, S); optimal fee f = V(q,S) H^{-1}(1-q), inducing fraction q of subscribers; more controversial recommendations (higher split-vote probability) raise V and thereby raise willingness to pay (Proposition 3, eq. 11, p. 2321)"
      direction: positive
      vsBenchmark: controversy in recommendations increases report demand relative to uninformative or fully informative recommendations
    - ref: R5
      outcome: proxy advisor vote recommendation design
      metric: probability
      value: "A fully informative private research report (R = {0,1}, r = theta) is optimal for the advisor (Proposition 8, p. 2330); adding noise to the report weakly lowers each subscriber's willingness to pay"
      direction: positive
      vsBenchmark: fully informative report dominates any noisy report for the advisor's profit
    - ref: R6
      outcome: probability of a close (split) shareholder vote
      metric: probability
      value: "Positive (pro-prior) recommendations are rubber-stamped: ISS positive recommendations on say-on-pay proposals receive 93% average support with no proposal failures; negative recommendations result in 69% average support and 11% chance of proposal failing (Section III.G, p. 2335)"
      direction: mixed
      vsBenchmark: "positive recommendations: near-unanimous support; negative recommendations: substantial dispersion and ~11% failure rate, consistent with model prediction"
    - ref: R7
      outcome: proxy advisor vote recommendation design
      metric: probability
      value: "With a ban on recommendations, the advisor targets a higher fraction of subscribers q_uninf > q* (Proposition A1, p. 2343); at moderate v_H (e.g. v_H = 5), ban raises correct-decision probability from 92.5% to 95.65% via more subscribers; at high v_H (e.g. v_H = 7), ban reduces correct-decision probability to 90.3% < 92.5% (Example A1, p. 2344)"
      direction: mixed
      vsBenchmark: ban on recommendations has ambiguous welfare effects depending on the distribution of shareholder valuations
  resultType: new-finding
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full text read (pp. 2303-2354 plus Appendices A-B); seven results extracted with locators from the PDF. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all seven Core-results rows confirmed correct (Propositions 4, 5, 8, empirical stats at p. 2335, and Example A1 at p. 2344 match). Equations (1-2, 7, 8-13) verified term-by-term against PDF. One fix applied: removed off-registry outcomeClass value firm-real-outcomes (the paper studies recommendation design and voting patterns, not firm real outcomes); outcomeClass set to social-welfare (information design and voting welfare, not fund behavior)."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13438
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-03-16"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the information-design model, and the Bayesian persuasion method it builds on, with the defining equations: enough to know what it found and how, without reading all 52 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13438).

## TL;DR

A profit-maximizing proxy advisory firm sells research reports to institutional investors and issues public vote recommendations. The paper shows that the advisor's optimal strategy combines two distinct elements: a fully informative (unbiased) private research report for subscribers, and a partially informative, asymmetrically biased public vote recommendation that favors the a priori unlikely alternative too often. By recommending against the likely outcome more often than its probability warrants, the advisor induces close, contentious shareholder votes, raising the value of its advice and thereby the willingness to pay for the research report. The paper calls this "creating controversy." The model is cast as an information design problem following Rayo and Segal (2010) and Kamenica and Gentzkow (2011). The result rationalizes the proxy advisory industry's one-size-fits-all approach, explains the rubber-stamping pattern documented in Malenko and Shen (2016) (positive ISS recommendations receive 93% average support on say-on-pay), explains why negative recommendations generate dispersed votes, and suggests that the active voting behavior of large institutional investors studied by Iliev and Lowry (2015) is consistent with rational adjustment for recommendation bias.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Optimal public recommendation is binary and partially informative**: the advisor recommends against the a priori likely alternative too often, inducing a controversial posterior near 0.5 | Proposition 4, pp. 2325-2326 | When mu >= mu_0(q), recommendation s = 0 is given with probability (1-mu)/(1-mu_0(q)) > Pr(theta=0) = 1-mu; more often than warranted by the true probability the proposal is value-decreasing |
| R2 | **Maximizing the average probability of a split vote is the objective**: controversial recommendations raise the split-vote probability, increasing subscribers' willingness to pay for the report | Eq. (12)-(14), pp. 2321-2322; Figure 3, p. 2323 | Concavification of Pr(Piv\|q, mu_s) over mu_s, subject to the Bayes plausibility constraint, yields the advisor's optimal policy; for q = 0.01 and mu = 0.8, partially informative recommendation raises split-vote probability above that of any other policy |
| R3 | **Near mu = 0.5, optimal recommendation is uninformative**: close votes are already likely without intervention, so information design has no benefit | Proposition 5, p. 2327; Section III.E, p. 2334 | ISS board-declassification positive recommendations: 100% of cases 2010-2019 (zero negative), yet shareholder support averages 73.7%, consistent with uninformative design prediction |
| R4 | **Subscriber demand rises with controversy**: the fee the advisor can charge equals V(q, S) H^{-1}(1-q); a higher average split-vote probability V raises willingness to pay | Proposition 3, eq. (11), p. 2321; eq. (9)-(10), p. 2320 | Shareholder i subscribes iff v_i >= f/V(q, S); the controversy mechanism converts a higher split-vote probability directly into higher revenue per subscriber |
| R5 | **Fully informative private research report is optimal**: noise in the report weakly lowers subscribers' willingness to pay | Proposition 8, p. 2330 | Any signal that induces a posterior of exactly 1/2 for the subscriber is worthless; the advisor can always combine signals to eliminate such posteriors, and the remaining signals achieve full informativeness |
| R6 | **Rubber-stamping of pro-prior recommendations, dispersion under anti-prior recommendations**: ISS say-on-pay positive recommendations receive 93% average support with no failures; negative recommendations receive 69% average support with 11% failure probability | Section III.G, p. 2335; Table IA.I (Internet Appendix) | About 500 close votes per year (40%-60% support) occur when ISS recommends against management; close votes are extremely rare when ISS agrees with management |
| R7 | **Ban on recommendations has ambiguous welfare effects**: it removes the bias but reduces information for nonsubscribers; whether the net effect is positive depends on the distribution of shareholder valuations v_i | Proposition A1, p. 2343; Example A1, p. 2344 | For v_H = 5: ban raises correct-decision probability from 92.5% to 95.65% (positive effect dominates); for v_H = 7: ban lowers it to 90.3% < 92.5% (negative effect dominates) |

**Overall (paper's conclusion).** Proxy advisors have a structural incentive to design biased vote recommendations that create controversy, because close votes increase the relevance and value of their research reports. This incentive is inherent to the core business model of selling information and is independent of any consulting conflict of interest. At the same time, research reports remain fully informative and valuable to subscribers. Proxy advisors' recommendations should therefore not be treated as the appropriate benchmark for evaluating institutional investors' voting behavior; the votes of large, engaged asset managers are a more suitable reference.

## Theory / model

### Setup (Section I, pp. 2311-2316)

A firm has $$N \geq 3$$ (odd) shareholders, each owning one share. A proposal is approved if at least $$\frac{N+1}{2}$$ shareholders vote in favor. Let $$d \in \{0,1\}$$ denote the decision (1 = approve). The proposal's payoff to shareholder $$i$$ is (p. 2312, eq. 1-2):

$$
u_i(d, \theta) = v_i \cdot u(d, \theta), \qquad u(1, \theta) = \begin{cases} 1 & \text{if } \theta = 1 \\ -1 & \text{if } \theta = 0 \end{cases}, \quad u(0, \theta) = 0 \tag{1-2}
$$

where $$\theta \in \{0,1\}$$ is the unknown state and $$v_i \geq 0$$ is shareholder $$i$$'s concern (drawn i.i.d. from distribution $$H(\cdot)$$ on $$[\underline{v}, \bar{v}]$$). The prior is $$\Pr(\theta=1) = \mu \in (0,1)$$.

### Information structure (Section I.B, pp. 2312-2313)

The proxy advisor designs two signals. The **private signal** (research report) $$\mathcal{R} = (R, \{\phi(\cdot|\theta)\}_{\theta \in \{0,1\}})$$ is available only to subscribers. The **public signal** (vote recommendation) $$\mathcal{S} = (S, \{\gamma(\cdot|r)\}_{r \in R})$$ maps the report realization $$r$$ to a public recommendation $$s \in S$$, observable by all shareholders. The paper shows (Proposition 8) that the optimal private signal is fully informative: $$R = \{0,1\}$$ and $$r = \theta$$, so subscribers learn the state with certainty.

### Voting equilibrium (Section II.A, pp. 2316-2319)

Given recommendation $$s$$ (inducing posterior $$\mu_s = \Pr(\theta=1|s)$$) and fraction $$q$$ of subscribers, a nonsubscribing shareholder's equilibrium probability of voting "for" is (Proposition 2, eq. 7, p. 2318):

$$
\pi(q, \mu_s) = \frac{z_s(1-2q) - 1 + \sqrt{(z_s-1)^2 + 4q^2 z_s}}{2(z_s-1)(1-q)}, \qquad z_s \equiv \left(\frac{\mu_s}{1-\mu_s}\right)^{\frac{2}{N-1}} \tag{7}
$$

for $$\mu_s \neq \frac{1}{2}$$. Subscribers vote according to the state: $$a_i = \theta$$. Nonsubscribers condition their vote not only on $$\mu_s$$ but also on the information revealed by the event of being pivotal ("strategic voting").

The value of the report to shareholder $$i$$, conditional on recommendation $$s$$, is $$\frac{v_i}{2} \Pr(\text{Piv}|q, \mu_s)$$, where (eqs. 8-10, p. 2320):

$$
V(q, \mathcal{S}) = \frac{1}{2} \sum_{s \in S} \Pr(\text{Piv}|q, \mu_s) \tau_s, \qquad \tau_s \equiv \mu \gamma(s|1) + (1-\mu)\gamma(s|0) \tag{10}
$$

is the average (pre-recommendation) probability of a shareholder being pivotal, weighted by the frequency of each recommendation.

## Method

The paper solves the advisor's problem by **Bayesian persuasion** (Kamenica and Gentzkow (2011)) applied to a multi-agent, multi-audience setting. The advisor maximizes expected profit $$N q f$$, where $$q$$ is the equilibrium fraction of subscribers and the optimal fee (eq. 11, p. 2321) is:

$$
f = V(q, \mathcal{S}) \cdot H^{-1}(1-q) \tag{11}
$$

Substituting into the profit expression, the advisor solves (eq. 12, 15, pp. 2321-2328):

$$
\max_{q, \mathcal{S}} \; q H^{-1}(1-q) \left( \sum_{s \in S} \Pr(\text{Piv}|q, \mu_s) \tau_s \right) \tag{12}
$$

subject to the **Bayes plausibility constraint**:

$$
\sum_{s \in S} \mu_s \tau_s = \mu \tag{13}
$$

The key step is the **concavification** of the function $$\Pr(\text{Piv}|q, \cdot)$$ over posterior beliefs. For a given $$q$$, the optimal public recommendation design is found by taking the concave closure $$P(q, \mu_s)$$ of $$\Pr(\text{Piv}|q, \mu_s)$$ (Figure 3, p. 2323). Because $$\Pr(\text{Piv}|q, \mu_s)$$ is (by Lemma 1, p. 2322) strictly convex near $$\mu_s = 0$$ and $$\mu_s = 1$$ (for small $$q$$), and strictly concave near $$\mu_s = 1/2$$, the concave closure is achieved by a **binary recommendation** that places mass at $$\mu_0 \in (0, 1/2)$$ (the controversial posterior) and $$\mu_1 = 1$$ (full certainty in the likely direction), or symmetrically.

The method builds on the `principal-agent` framework for the advisor's optimization, and the `bayesian-persuasion` technique for solving the optimal information design. The timeline-consistent property (p. 2313) distinguishes this paper from most Bayesian persuasion models: because the advisor maximizes ex ante profits and has no stake in the vote outcome, the optimal policy is dynamically consistent.

## Empirical specifications

This is a pure-theory paper. The paper does not estimate any econometric specification. Section III (pp. 2330-2336) presents anecdotal and survey evidence to corroborate the mechanism, drawing on:

- **Ertimur, Ferri, and Oesch (2013, 2018)**: variability in ISS research-report severity when negative recommendations are issued; shareholders less likely to vote against management when the report conveys less severe concerns.
- **Case studies**: the 2024 Tesla say-on-pay vote (ISS issued a negative recommendation but the report was more positive; Vanguard and BlackRock voted for, consistent with large-v_i shareholders voting on the report rather than the recommendation; p. 2331).
- **ISS board declassification data**: zero negative ISS recommendations on shareholder proposals to declassify boards from 2010 to 2019, yet average support of 73.7%, consistent with Proposition 5 (uninformative recommendation near mu = 0.5; p. 2334).
- **ISS say-on-pay voting outcomes**: 93% average support with zero failures on positive recommendations; 69% average support and 11% failure rate on negative recommendations (Table IA.I; p. 2335), consistent with rubber-stamping (Proposition 4) and close-vote prediction.
- **Hayne and Vance (2019) interview evidence**: proxy advisor employees confirm that maintaining a consistent proportion of negative recommendations is viewed as a way to stay relevant (Section III.F, p. 2334-2335).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| ISS Voting Analytics (say-on-pay and director elections, 2011-2019) | Empirical corroboration of rubber-stamping and close-vote patterns (Section III.G) | No page yet |
| ISS board-declassification recommendations (2010-2019) | Corroboration of uninformative-recommendation prediction (Section III.E) | No page yet |
| Ertimur, Ferri, and Oesch (2013, 2018) hand-collected ISS reports | Content of research reports vs. recommendations (Section III.A) | No page yet |

The paper has no original data collection. Empirical illustrations use published sources and aggregate statistics from the literature.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13438) if you are: building a structural model of information intermediaries in financial markets; studying proxy advisory regulation (the ban-on-recommendations analysis in Appendix A); analyzing the information content of voting recommendations vs. research reports; or extending the model to costly information acquisition, ideological shareholders, or multi-firm settings (Internet Appendix Sections IV.C, IV.F). The locators above point to the exact propositions and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(4). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY-NC-ND 4.0 licence permits sharing with attribution but does not permit adaptations or commercial use; the verbatim PDF is not hosted here.

> Malenko, Andrey, Nadya Malenko, and Chester Spatt. "Creating Controversy in Proxy Voting Advice." *The Journal of Finance* 80, no. 4 (August 2025): 2303-2354. DOI: 10.1111/jofi.13438. © 2025 The Author(s). Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). This page is a distillation by the Institute for Automated Research: core results extracted and re-expressed; extract-only.
