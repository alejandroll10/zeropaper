---
title: "Allocation of Socially Responsible Capital: Green & Roth (2025)"
description: >-
  Distilled: This paper develops a tractable equilibrium framework in which
  social and commercial investors compete to finance entrepreneurs with varying
  profit and social value profiles. It shows that values-aligned ESG strategies
  are inefficient at creating social impact and identifies alternative
  impact-aligned strategies that both increase welfare and financial returns.
  Supported by a laboratory experiment documenting heterogeneous social
  preferences. J. Finance 2025, paywalled. Five core results with source
  locators, the model, method, and empirical specifications.
sidebar:
  label: Green-Roth 2025
  order: 1
tags: [paper-summary, esg, sustainable-finance, social-investing, impact-investing,
       theory, mechanism-design, peer-reviewed, unreplicated]
paper:
  authors: Daniel Green, Benjamin N. Roth
  authorList:
    - { family: Green, given: Daniel, orcid: "0000-0003-1934-6725", affiliation: Harvard Business School }
    - { family: Roth, given: Benjamin N., orcid: "0000-0001-5795-1139", affiliation: Harvard Business School }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 755–781
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13425
  jel:
    codes: [G11, G12, D62]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Fiscal Policy and Economic Growth
    - Financial Literacy, Pension, Retirement Analysis
    - Corporate Social Responsibility Reporting
  dataAccess: hand-collected
  introducesData: true
  outcome:
    - social welfare created by capital allocation
    - investor willingness to pay for values alignment vs. impact alignment
    - share of investors with impact-aligned vs. values-aligned preferences
  outcomeClass: [social-welfare, fund-behavior]
  license: "Wiley VOR terms (http://onlinelibrary.wiley.com/termsAndConditions#vor); paywalled; confirmed via Crossref DOI metadata content-version vor, delay-in-days 0, start 2025-01-22"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley Online Library; confirmed paywalled 2026-06-06)"
  redistribution: extract-only
  resultsCount: 5
  citedByCount: 35
  methods:
    role: both
    family: theory
    buildsFrom: [mechanism-design, latent-class-logit]
    identification: descriptive
  contributionType: [new-theory, new-data, new-fact]
  mechanisms: [demand-elasticity, information-asymmetry]
  scope:
    region: US
    period: 2023-11..2023-11
    frequency: mixed
    dataType: [experimental, survey]
    granularity: [individual]
    n: "389 participants (Prolific, November 2023, US-based stock-market investors)"
  findings:
    - ref: R1
      outcome: investor willingness to pay for values alignment vs. impact alignment
      metric: coefficient
      value: "Class 2 (values-aligned): WTP Values = $0.724*** (SE 0.053), WTP Impact = -$0.167*** (SE 0.058), share = 28.8%; Class 3 (impact-aligned): WTP Values = $0.060 (SE 0.048), WTP Impact = $0.903*** (SE 0.045), share = 34.4%"
      direction: mixed
      vsBenchmark: "Class 1 (commercial): WTP Values = $0.197***, WTP Impact = $0.166***; share = 36.8% (Table I, p. 777)"
    - ref: R2
      outcome: share of investors with impact-aligned vs. values-aligned preferences
      metric: probability
      value: "30% of participants identified by choice data as values-aligned self-reported impact-aligned preferences; 95% of respondents have modal class membership probability over 80%"
      direction: positive
      vsBenchmark: "Among 389 participants: 125 self-identified as impact-aligned, 144 as values-aligned, 120 as purely financial (p. 778)"
    - ref: R3
      outcome: share of values-aligned investors who revise choices when shown impact-aligned alternative
      metric: probability
      value: "109 out of 231 participants (approximately 47%) revised their choice when shown that an alternative would increase both impact and financial return"
      direction: positive
      vsBenchmark: "59% of participants picked values-aligned option in at least one of six key scenarios (p. 779)"
    - ref: R4
      outcome: social welfare created by capital allocation
      metric: level
      value: "Values-aligned investors in equilibrium generate zero additional social value when they finance firms that commercial capital would have funded anyway; financial concession transfers rents to entrepreneurs rather than expanding socially valuable projects"
      direction: none
      vsBenchmark: "Model Proposition 2: deviating to fund unfinanced firms increases both social welfare and investor financial return (pp. 768-769)"
    - ref: R5
      outcome: social welfare created by capital allocation
      metric: level
      value: "Impact-aligned investors finance only non-commercially viable firms (Lemma 3); negative assortative matching: higher-altruism investors finance lower social-value firms to avoid displacing lower-altruism investors from high social-value firms (Proposition 1)"
      direction: positive
      vsBenchmark: "vs. values-aligned investors who exhibit positive assortative matching (Lemma 1); impact-aligned strategies generate strictly positive social value (pp. 765-766)"
  resultType: new-finding
  relatesTo:
    - { cite: "Pastor, Stambaugh & Taylor (2021)", doi: '10.1016/j.jfineco.2020.12.011', relation: builds-on, note: "equilibrium model of sustainable investing in which values-aligned tilts can shift capital allocation" }
    - { cite: "Pedersen, Fitzgibbons & Pomorski (2021)", doi: '10.1016/j.jfineco.2020.11.001', relation: builds-on, note: "ESG-efficient frontier: investors with ESG preferences can tilt portfolios without sacrificing mean-variance efficiency" }
    - { cite: "Oehmke & Opp (2024)", doi: '10.1093/restud/rdae048', relation: contradicts, note: "they show social investors cannot generate social impact because they would rather not invest than invest in improved but still polluting firms; this paper shows competition between investors to hold valuable investments is the key mechanism, distinct from their model" }
    - { cite: "Broccardo, Hart & Zingales (2022)", doi: '10.1086/720516', relation: builds-on, note: "exit vs. voice: engagement and tilting strategies as alternatives to divestment" }
    - { cite: "Landier & Lovo (2023)", relation: builds-on, note: "ESG investing: how to optimize impact via activist strategies" }
    - { cite: "Bonnefon et al. (2023)", relation: extends, note: "experimental elicitation of willingness to pay for social attributes; this paper adds heterogeneity and impact-alignment distinction" }
    - { cite: "Brest, Gilson & Wolfson (2019)", doi: '10.2139/ssrn.3150347', relation: builds-on, note: "enterprise impact: how investors can (and cannot) create social value" }
  openQuestions:
    - "How exactly each form of incomplete information (about social value, profitability, other investors' strategies, or available social capital) affects impact-aligned investment strategies and equilibrium capital allocation is left for future research (p. 773)."
    - "The model omits risk-aversion and diversification motives; incorporating them would allow impact-aligned investors to also invest in some commercially viable firms to reduce portfolio risk without social impact, modifying the negative assortative matching result (p. 764)."
    - "The baseline model features a fixed universe of firms; a richer treatment of endogenous firm entry could change the social-value implications of values-aligned investing (p. 762)."
  replicationCode:
    status: available
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 755-781); five results extracted from the source PDF. Not human-verified. Not reproduced. Replication code referenced in the Supporting Information." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against source PDF (pp. 760-779); all five Core-result rows confirmed; one equation error fixed: eq. (2) LHS summation index corrected from E to bar-E (financed entrepreneurs), matching PDF p. 761." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13425", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-22; paywalled, not CC" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the equilibrium model of social investor competition, and the laboratory experiment documenting investor preference heterogeneity: enough to understand what it found and how, without reading all 27 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13425).

## TL;DR

Green and Roth (2025) build a tractable competitive equilibrium model in which social investors (who care about financial returns and social value) and commercial investors compete to finance entrepreneurs. The central insight is that values-aligned ESG strategies, which dominate real-world socially responsible investing, are inefficient at creating social welfare: they displace commercial capital that would have funded the same firms anyway, and competition among social investors transfers rents to entrepreneurs rather than funding new socially valuable projects. Impact-aligned strategies, which prioritize investments where the social investor is pivotal, generate strictly positive social welfare and higher financial returns.

The paper contributes to a growing literature on social preferences in asset markets. Pastor, Stambaugh, and Taylor (2021) and Pedersen, Fitzgibbons, and Pomorski (2021) study equilibrium models in which values-aligned tilts shift capital toward socially preferred firms. Oehmke and Opp (2024) show social investors cannot generate impact because they would rather not invest than fund an improved but still polluting company; the present paper shows competition among social investors to hold valuable investments is the key friction, distinct from that mechanism. Broccardo, Hart, and Zingales (2022) argue that engagement and tilting strategies (exit vs. voice) are more effective than divestment. Landier and Lovo (2023) study how ESG investing can be optimized for impact. On the empirical side, Bonnefon et al. (2023) conduct an experiment distinguishing values alignment from impact alignment; this paper adds explicit preference heterogeneity and shows investors may mis-operationalize preferences. The enterprise-impact concept builds on Brest, Gilson, and Wolfson (2019).

A laboratory experiment with 389 participants confirms significant investor heterogeneity, with about 34% holding impact-aligned preferences, 29% holding values-aligned preferences, and 37% being purely financially motivated. Moreover, roughly 47% of participants who initially chose values-aligned options revised their choices when shown an alternative offering higher impact and higher financial return, suggesting widespread mis-operationalization of impact preferences.

## Core results

Magnitudes and significance are as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Three latent investor classes: commercial (36.8%), values-aligned (28.8%), impact-aligned (34.4%); classes sharply differ in WTP for values vs. impact | Table I, p. 777 | Class 2 (values): WTP Values = $0.724\*\*\*, WTP Impact = -$0.167\*\*\*; Class 3 (impact): WTP Values = $0.060, WTP Impact = $0.903\*\*\* |
| R2 | 30% of participants classified as values-aligned by revealed preferences self-report impact-aligned preferences; preference mis-operationalization is widespread | §IV.B.2, p. 778 | 30% of revealed-values-aligned investors self-reported impact alignment; 95% of respondents have modal class membership probability above 80% |
| R3 | Nearly half of investors who chose values-aligned options revised when shown impact-improving alternative with equal or higher financial return | §IV.B.2, p. 779 | 109 out of 231 (approx. 47%) revised their choice in the follow-up; 59% selected values-aligned option in at least one of six test scenarios |
| R4 | Values-aligned investors create zero net social value in equilibrium: financial concessions bid up prices of firms that commercial capital would have funded, transferring rents to entrepreneurs | Proposition 2, §II.D, p. 768 | Model result (no point estimate): deviation to fund unfinanced firm weakly increases both total welfare and investor's financial return; commercial firms earn zero marginal social value |
| R5 | Impact-aligned investors exhibit negative assortative matching: higher-altruism investors fund lower social-value firms to preserve space for lower-altruism investors at high social-value opportunities | Proposition 1, §II.B, p. 766 | Model result (no point estimate): for firms with equal profit, higher altruism investor matches with lower social-value firm; contrast with values-aligned positive assortative matching (Lemma 1) |

**Overall (paper's conclusion).** Values-aligned investment strategies, which resemble the construction of conventional ESG and emissions-reduction portfolios, have limited impact because they simply displace commercial investors who would have supported some socially valuable firms anyway. The financial concession made by values-aligned investors is wasteful, transferring rents to entrepreneurs rather than funding new social value. Impact-aligned investment strategies, which prioritize firms that could not attract commercial capital, generate greater social impact and higher financial returns. The empirical evidence confirms that a substantial share of real investors have impact-aligned preferences but are incorrectly operationalizing those preferences through values-aligned strategies.

## Theory / model

The model has two types of players: a finite set $$E$$ of entrepreneurs and a finite set $$S$$ of social investors. Each entrepreneur $$i$$ holds a project requiring one unit of capital that generates profit $$\pi_i \in \mathbb{R}^+$$ and social value $$w_i \in \mathbb{R}$$, both publicly observable (pp. 760-761). There is also an elastic commercial capital market supplying financing at required rate $$r^C$$.

A contract specifies a transfer $$r_i$$ (cost of capital) from the entrepreneur to the investor; entrepreneur utility is $$\pi_i - r_i$$. Social welfare is $$W = \sum_{i \in \bar{E}} w_i$$ where $$\bar{E}$$ is the set of financed entrepreneurs (p. 762).

**Values-aligned investors** maximize the sum of their financial return and the social value of the firm they finance (eq. 1, p. 760):

$$
r_i + \theta_i w_i \tag{1}
$$

where $$\theta_i \in \{\theta^1, \ldots, \theta^K\} \subset \mathbb{R}^+$$ is investor $$i$$'s altruism strength.

**Impact-aligned investors** maximize their financial return and the effect of their investment on aggregate social welfare (eq. 2, p. 761):

$$
r_i + \theta_i \sum_{j \in \bar{E}} w_j = (r_i + \theta_i w_i) + \theta_i \sum_{j \in \bar{E} \setminus i} w_j \tag{2}
$$

where $$\bar{E}$$ is the set of entrepreneurs that receive financing. The key difference is that impact-aligned investors internalize consequences for all funded firms, not just the one they own.

**Equilibrium concept.** Pure-strategy subgame perfect equilibrium: in the acceptance stage, each entrepreneur accepts the contract maximizing their share of profits; in the offer stage, each investor chooses the contract maximizing their utility among contracts that will be accepted (p. 762).

**Key lemmas for values-aligned investors.** Lemma 1 (p. 763): investors and entrepreneurs exhibit positive assortative matching (higher altruism $$\theta_i$$ matches with higher social value $$w_i$$). Lemma 2 (p. 763): cost of capital is decreasing in social value $$w_i$$. The incentive compatibility condition is

$$
r_i + \theta_i w_i \geq r_j + \theta_i w_j \tag{3}
$$

meaning no social investor prefers to undercut another social investor.

**Proposition 1** (p. 766): Impact-aligned investors exhibit negative assortative matching. Among firms with fixed profit $$\pi$$, higher altruism investors finance firms with lower social value $$w_i$$. The incentive compatibility condition for impact-aligned investors is

$$
\pi_i + \theta_i w_i \geq r^C \tag{4}
$$

**Enterprise impact** (p. 770): the enterprise impact of firm $$i$$ is $$e_i \equiv w_i - v_i$$, where $$v_i$$ is the social value of the capital employed by the investor who supports firm $$i$$. Proposition 3 states that increasing firm profitability $$\pi_i$$ (holding $$w_i$$ fixed) weakly increases enterprise impact because a more profitable firm can attract commercial capital, freeing scarce socially motivated capital for other uses.

## Method

The paper combines two methods: a complete-information equilibrium model solved analytically, and a laboratory experiment estimated with a latent class logit model.

**Analytical model.** The baseline model is solved for pure-strategy subgame perfect equilibrium using an offer-then-accept timing (§I.C, p. 761). The equilibrium is characterized by lemmas and propositions derived from the incentive compatibility conditions (eqs. 3 and 4 above). Section III extends the baseline to a model of incomplete information in which $$\pi_i$$ and $$w_i$$ are public signals of expected private types $$(\pi^i, w^i) \in \{\pi^L, \pi^H\} \times \{w^L, w^H\}$$. Under Proposition 4, impact-aligned investors in the incomplete-information model finance all firms $$(\pi_i, w_i)$$ satisfying

$$
w_i \geq \bar{u}^S / \theta, \quad \pi_i \leq \bar{\pi}(w_i) \equiv 1 - \left(\bar{u}^S - \pi^L\right) / (\theta w_i) \tag{5}
$$

where $$\bar{u}^S$$ is the threshold utility of the marginal social investor (p. 772).

The model builds on `mechanism-design` in the game-theoretic sense (investor-offer, entrepreneur-accept timing), characterizing equilibrium investment strategies and welfare properties. Internet appendix extensions include endogenous commercial cost of capital (§I.A), endogenous firm responses (§I.C), and atomistic investors in the limit (§II.C.11).

**Laboratory experiment.** Individual utility of investor $$j$$ owning stock $$k$$ is modeled as (p. 776):

$$
u_{j,k} = \beta^r_{c_j} r_k + \beta^v_{c_j} w_k + \beta^i_{c_j} w_k p_k + \epsilon_{j,k}
$$

where $$r_k$$ is the stock's financial return, $$w_k$$ is its social value (charitable donation), $$p_k \in \{0,1\}$$ indicates whether the investor's purchase is pivotal for the donation, $$c_j$$ is the latent class of investor $$j$$, and $$\epsilon_{j,k}$$ follows a Type I extreme value distribution.

With $$C = 3$$ latent classes, the model is estimated as a `latent-class-logit` (following Heckman and Singer (1984) and Greene and Hensher (2003)): class membership probabilities $$\pi_c$$ and class-specific preference parameters $$\beta_c$$ are jointly estimated by maximum likelihood. Willingness to pay for values alignment is $$\beta^v / \beta^r$$ and for impact alignment is $$\beta^i / \beta^r$$.

## Empirical specifications

**Survey design.** In November 2023, 400 US-based stock-market investors were recruited via the Prolific platform; 11 were dropped for failing attention checks, leaving $$n = 389$$. Participants completed $$S = 14$$ pairwise investment scenarios plus 3 attention checks in random order. For each scenario $$s$$, participants chose between two stocks $$k$$ and $$k'$$ with attributes: financial return $$r_k \in \{\$3.00, \$3.50, \$4.00, \$4.50\}$$, charitable donation $$w_k \in \{\$0.50, \$1.00, \$1.50, \$2.00\}$$, and pivotality indicator $$p_k \in \{0, 1\}$$.

The aggregate social value generated by the participant's choice is (p. 775):

$$
w^{agg} = w_k i_k^{p_k} + w_{k'} (1 - i_k)^{p_{k'}}
$$

where $$i_k$$ indicates investment in stock $$k$$. One of 14 decisions was randomly selected for real-life payment, ensuring incentive compatibility.

**Latent class logit estimation.** The utility model with $$C = 3$$ classes is estimated by maximum likelihood on the pairwise choice data. Standard errors are in parentheses; significance at 1%/5%/10% is denoted `\*\*\*`/`\*\*`/`\*`. The model produces class-specific WTP estimates and class membership probabilities.

**Mis-operationalization test.** Six of the 14 scenarios were structured so that one choice is consistent only with values-aligned preferences (requires accepting lower financial return and lower social impact for higher values alignment). Participants who chose the values-aligned option in any of the six scenarios were given follow-up questions asking if they would revise their choice given information that the alternative offers higher social impact at equal or higher financial return (§IV.B.2, p. 778).

**No standard regression specification.** The paper presents no panel or cross-sectional regression with fixed effects; the empirical section relies entirely on the latent class logit and the descriptive revision rates from the follow-up exercise.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Prolific online survey / laboratory experiment (November 2023, n = 389) | Elicits revealed preferences for values alignment vs. impact alignment across 14 pairwise investment scenarios; identifies three latent investor classes and measures revision behavior | no page yet (author-collected primary data) |

Sample: 389 US-based stock-market investors recruited on Prolific in November 2023; 14 pairwise investment scenarios plus 3 attention checks per participant.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13425) if you are: building theoretical models of ESG investing or impact investing, especially ones that endogenize competition between social investors; evaluating whether values-aligned portfolio strategies (ESG tilt, exclusion screens) can generate social welfare; designing experiments or surveys to elicit social investing preferences; or studying negative assortative matching in two-sided markets with altruistic agents. The formal proofs and Internet Appendix extensions (endogenous commercial cost of capital, continuous firm production functions, atomistic investors) are in the supporting information.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled (Wiley VOR terms); extract-only.

Green, Daniel, and Benjamin N. Roth. "The Allocation of Socially Responsible Capital." *The Journal of Finance* 80, no. 2 (April 2025): 755–781. DOI: 10.1111/jofi.13425. © 2025 the American Finance Association.
