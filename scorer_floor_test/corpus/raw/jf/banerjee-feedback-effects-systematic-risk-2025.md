---
title: "Feedback Effects and Systematic Risk Exposures: Banerjee, Breon-Drish & Smith (2025)"
description: >-
  Distilled: Models feedback effects when managers learn discount rates (not just
  cash flows) from stock prices, applied to climate-exposed investment. Shows cash-flow
  and price maximization both fail to maximize welfare because neither internalizes
  hedging and risk-sharing benefits of investment. J. Finance 2025, paywalled.
  Seven core results with source locators, the model equations, and the equilibrium
  investment rules under each objective.
sidebar:
  label: Banerjee-Breon-Drish-Smith 2025
  order: 1
tags: [paper-summary, asset-pricing, feedback-effects, climate-risk, esg, corporate-investment,
       theory, peer-reviewed, unreplicated]
paper:
  authors: Snehal Banerjee, Bradyn M. Breon-Drish, Kevin M. Smith
  authorList:
    - { family: Banerjee, given: Snehal, orcid: "0000-0003-3269-5188", affiliation: University of Michigan, Ann Arbor }
    - { family: Breon-Drish, given: Bradyn M., orcid: "0000-0003-4713-1668", affiliation: University of California San Diego }
    - { family: Smith, given: Kevin M., orcid: "0000-0002-6736-4779", affiliation: Stanford University }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 981-1028
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13427
  jel:
    codes: [G12, G14, G31]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ['Financial Markets and Investment Strategies', 'Capital Investment and Risk Analysis', 'Corporate Finance and Governance']
  dataAccess: public
  outcome:
    - corporate investment in systematic-risk-exposed projects
    - investor welfare under feedback effects
    - probability of investment as a function of project greenness
  outcomeClass: [firm-real-outcomes, security-returns]
  license: "Wiley VOR terms and conditions (http://onlinelibrary.wiley.com/termsAndConditions#vor); paywalled; no CC licence found in Crossref metadata"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley site; Crossref VOR licence only, no open-access URL; checked 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 11
  methods:
    role: theory
    family: theory
    buildsFrom: [real-options, principal-agent]
  contributionType: [new-theory]
  mechanisms: [information-asymmetry, risk-sharing]
  scope:
    region: theoretical
    assetClass: equity (climate-exposed projects)
  findings:
    - ref: R1
      outcome: firm investment under cash-flow maximization
      metric: coefficient
      value: "Higher climate exposure |alpha| makes the price a noisier signal: Prob(invest) falls for ex-ante profitable projects (mu_theta > c) and rises for ex-ante unprofitable ones (Prop. 3, eq. 22)"
      direction: mixed
    - ref: R2
      outcome: firm investment under price maximization
      metric: coefficient
      value: "An additional variance-of-NPV channel reverses the pattern: climate exposure can raise investment in ex-ante unprofitable projects and lower it in profitable ones (Prop. 4, eq. 23 part v)"
      direction: mixed
    - ref: R3
      outcome: investment under cash-flow vs price maximization
      metric: coefficient
      value: "Cash-flow maximization yields more investment than price maximization iff the discount-rate premium exceeds the profitability advantage (Corollary 1, eq. 24)"
      direction: none
    - ref: R4
      outcome: investment relative to the welfare optimum
      metric: coefficient
      value: "With homogeneous investor exposures, price maximization always underinvests (s_P - s_W = (1/2)(gamma/tau_eta)n > 0); cash-flow maximization underinvests iff eq. 34 holds, overinvests otherwise (Prop. 5)"
      direction: negative
    - ref: R5
      outcome: welfare-implementing weight on price in the manager's objective
      metric: coefficient
      value: "The welfare optimum is implemented by a manager maximizing a weighted average of expected price and expected cash flows, with weight delta in (0,1) iff the profitability condition holds (Prop. 6, eq. 40)"
      direction: none
    - ref: R6
      outcome: investment relative to the welfare optimum
      metric: coefficient
      value: "With heterogeneous exposures and zero endowment (n = 0), welfare always requires investment, yet both cash-flow and price maximization underinvest (Prop. 7, eq. 42)"
      direction: negative
    - ref: R7
      outcome: welfare effect of price feedback
      metric: coefficient
      value: "Feedback lowers welfare when firm size n is small or risk-sharing gains are large (tau_zeta small), despite always improving the manager's own objective (Prop. 8)"
      direction: negative
  resultType: new-finding
  relatesTo:
    - { cite: "Bond, Edmans & Goldstein (2012)", doi: '10.1146/annurev-financial-110311-101826', relation: builds-on, note: "survey of feedback effects distinguishing FPE and RPE; paper provides the first feedback model with manager learning about discount rates" }
    - { cite: "Goldstein (2023)", relation: builds-on, note: "recent survey of feedback effects literature; authors contrast their setting against this literature's risk-neutral baseline" }
    - { cite: "Dow & Rahi (2003)", doi: '10.1086/375254', relation: builds-on, note: "risk-averse investor feedback model with risk-neutral pricing; authors extend by endogenizing discount rate learning and market completeness" }
    - { cite: "Pastor, Stambaugh & Taylor (2021)", relation: builds-on, note: "green assets carry lower expected returns as climate hedges; paper provides a feedback mechanism microfoundation for green discount rates" }
    - { cite: "Spence (1975)", doi: '10.2307/3003237', relation: cites, note: "analogy for why price-maximization leads to underinvestment: marginal vs average disutility of risk" }
  openQuestions:
    - "Whether results extend to settings with both public and private information signals about firms' climate risk exposures, which would allow assessment of the merits of climate disclosure (p. 1013)."
    - "How multiple dimensions of systematic risk fundamentals (as in Goldstein and Yang (2019) and Goldstein, Schneemeier, and Yang (2020)) interact with climate-exposed investments (p. 1013)."
    - "How dynamics and multiple traded assets influence managers' ability to infer discount rate information from prices (p. 1013)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 981-1028, Propositions 1-8, Corollary 1, welfare analysis); seven results extracted from a paywalled PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; R2 sign corrected (+ not - on alpha*gamma*tau_Z*mu_Z/tau_eta term in Prop. 4 part v); contributionType new-fact removed (pure theory paper, no empirical facts); all other locators, equations, and proposition statements confirmed." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13427", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-01-30; no CC licence present" }
  rightsSignalConflict: false
---

**What this is.** The paper's core propositions, the equilibrium investment rules, and the welfare results: enough to know what it found and how, without reading all 48 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13427).

## TL;DR

The paper builds a rational-expectations feedback model in which a manager learns both cash-flow news and discount-rate news from the stock price when deciding whether to invest in a project exposed to a systematic risk factor (climate risk). This extends the feedback effects literature surveyed by Bond, Edmans, and Goldstein (2012) and Goldstein (2023), and the risk-averse feedback models of Dow and Rahi (2003), to settings where the manager also learns about the factor risk premium. A cash-flow-maximizing manager treats discount-rate variation as noise; a price-maximizing manager internalizes it. This difference reverses how project "greenness" affects investment: higher climate exposure reduces investment under cash-flow maximization (noisier price signal) but can raise it under price maximization (more volatile NPV makes ex-ante unattractive projects more likely to become desirable). Neither objective maximizes investor welfare, because neither manager internalizes the hedging and risk-sharing benefits of investment in climate-exposed assets, a mechanism related to Pastor, Stambaugh, and Taylor (2021) on green asset pricing. The paper derives welfare-maximizing rules and shows when feedback reduces rather than improves welfare. The welfare gap between price maximization and welfare maximization is analogous to the quality-choice distortion in Spence (1975): the price reflects marginal disutility of the last share, while welfare depends on average disutility across all shares.

## Core results

Magnitudes and significance are as reported. Results are analytical propositions from the theoretical model; no empirical estimation is involved. Locators cite PDF pages.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Under cash-flow maximization, higher project climate exposure (higher \|alpha\|) makes the price a noisier signal, reducing investment for ex-ante profitable projects and increasing it for ex-ante unprofitable ones | Prop. 3, p. 997; Fig. 2, p. 999 | Prob(invest) decreases with tau\_theta and \|alpha\| when mu\_theta > c; increases with tau\_theta and \|alpha\| when mu\_theta < c (eq. 22) |
| R2 | Under price maximization, climate exposure has an additional "variance of NPV" channel that can increase investment for ex-ante unprofitable projects and decrease it for ex-ante profitable ones, creating the opposite pattern relative to cash-flow maximization | Prop. 4, p. 998; Fig. 2, p. 999 | Prob(invest) decreases with greenness alpha iff (mu\_theta - c - (gamma n / tau\_eta) + (alpha gamma tau\_Z mu\_Z) / tau\_eta) sgn(alpha) > 0 (eq. 23, part v) |
| R3 | Cash-flow maximization leads to more investment than price maximization if and only if the discount-rate premium exceeds the ex-ante profitability advantage: (gamma / tau\_eta)(n - alpha mu\_Z) > -(tau\_theta / tau\_p)(mu\_theta - c) | Corollary 1, p. 999 | Threshold condition eq. 24: s\_P > s\_C iff (gamma / tau\_eta)(n - alpha mu\_Z) > -(tau\_theta / tau\_p)(mu\_theta - c) |
| R4 | With homogeneous investor climate exposures, price maximization always leads to underinvestment relative to welfare maximization; cash-flow maximization leads to underinvestment iff the condition in eq. 34 holds, and overinvestment otherwise | Prop. 5, p. 1003; eqs. 34-36, pp. 1003-1005 | Underinvestment gap: s\_P - s\_W = (1/2)(gamma / tau\_eta)n > 0 always; for cash-flow: s\_C - s\_W > 0 iff (gamma / tau\_eta) alpha mu\_Z - (tau\_theta (mu\_theta - c)) / tau\_p - (1/2)(gamma / tau\_eta)n > 0 |
| R5 | The welfare-maximizing rule can be implemented by a manager maximizing a weighted average of expected price and expected cash flows, with weight delta on price; delta is between 0 and 1 iff the ex-ante profitability condition holds | Prop. 6, eqs. 39-40, p. 1006 | delta = [(tau\_p/(tau\_theta + tau\_p))(mu\_theta - c) - (tau\_p/(tau\_theta + tau\_p))(gamma / tau\_eta)(alpha mu\_Z - n/2)] / [(tau\_theta/(tau\_theta + tau\_p))(mu\_theta - c) - ... + (1/2)(gamma / tau\_eta)n] (eq. 40) |
| R6 | With heterogeneous investor exposures and zero share endowment (n = 0), welfare maximization always requires investment; both cash-flow and price maximization lead to underinvestment relative to welfare maximization | Prop. 7, eq. 42, p. 1008 | arg max W(k; s\_p) = 1 for all s\_p when n = 0 and heterogeneous exposures (1/tau\_zeta > 0) |
| R7 | Feedback reduces welfare when firm size n is small or when gains from risk-sharing are large (tau\_zeta small), even though feedback always improves the manager's objective (expected cash flows or price) | Prop. 8, p. 1008; Fig. 3, p. 1009 | Welfare is lower with feedback than without when n -> 0 or tau\_zeta -> 0; the risk-sharing channel is unaffected by n but is the dominant welfare effect in this limit |

**Overall (paper's conclusion).** Neither cash-flow maximization nor price maximization aligns with welfare maximization because the stock price reflects the marginal disutility of the last outstanding share, not the average disutility across all investors. Investing in a climate-exposed project improves investors' ability to hedge systematic risk (risk-sharing channel) and reduces information uncertainty about climate exposures (value of information channel), but neither channel is fully captured by standard managerial objectives. As a result, both objectives can lead to underinvestment in green projects and, sometimes, overinvestment in brown projects. Incentivizing managers via climate scores can improve welfare even when it reduces stock prices and future profitability.

## Theory / model

The model has four dates (t = 1, 2, 3, 4) and two securities (risk-free and risky). A continuum of CARA investors indexed by i in [0, 1] with risk aversion gamma each have initial endowment of n shares and idiosyncratic climate exposure z\_i = Z + zeta\_i (p. 986). The terminal cash flow per share, given investment choice k in {0, 1}, is (eq. 2, p. 987):

$$
V(k) = A + k\!\left(\theta + \alpha\eta_C + \sqrt{1-\alpha^2}\,\eta_I - c\right)
$$

where $$A \sim N(\mu_A, \tau_A^{-1})$$ are assets in place, $$\theta \sim N(\mu_\theta, \tau_\theta^{-1})$$ is the learnable cash-flow component, $$\eta_C \sim N(0, \tau_\eta^{-1})$$ are climate shocks, $$\eta_I \sim N(0, \tau_\eta^{-1})$$ are idiosyncratic shocks, $$\alpha \in [-1,1]$$ is the project's climate exposure ("greenness"), and c >= 0 is investment cost. Projects with $$\alpha > 0$$ are "green" (cash flows high when climate outcomes are good), projects with $$\alpha < 0$$ are "brown."

Investor i's terminal wealth is (eq. 1, p. 986):

$$
W_i = (n + X_{i1} + X_{i3})V - X_{i3}P_3 - X_{i1}P_1 - z_i\eta_C
$$

Investor i maximizes expected CARA utility (eq. 3, p. 988):

$$
\mathcal{W}_i \equiv \sup_{x \in \mathbb{R}} \mathbb{E}_{i1}\!\left[-e^{-\gamma W_i}\right]
$$

subject to market clearing at each date (eq. 4, p. 988):

$$
\int_i X_{it}\,di = 0
$$

**Two managerial objectives.** A cash-flow-maximizing manager solves (eq. 5, p. 988):

$$
k(P_1) = \arg\max_k \mathbb{E}[V|\mathcal{F}_m]
$$

A price-maximizing manager solves (eq. 6, p. 988):

$$
k(P_1) = \arg\max_k \mathbb{E}[P_3|\mathcal{F}_m]
$$

where $$\mathcal{F}_m = \sigma(P_1)$$ is the manager's information set at date 2.

**The equilibrium.** A threshold equilibrium (Definition 1, p. 991) features prices depending on the sufficient statistic $$s_p = \theta + \frac{1}{\beta}\alpha Z$$, with the price taking a piecewise-linear form: $$P_3 = P_1 = A_1 + B_1 s_p$$ when $$s_p > \bar{s}$$ and $$P_0$$ otherwise. The manager invests if and only if the price exceeds the no-investment price (i.e., $$s_p > \bar{s}$$). The key feature is that $$\beta = \frac{\tau_\eta}{\gamma\alpha}$$ (p. 993), so the price statistic $$s_p$$ mixes cash-flow news ($$\theta$$) and discount-rate news ($$\alpha Z$$), both of which are relevant to the project's NPV.

**The NPV rule under price maximization** (eq. 21, p. 995):

$$
\text{NPV} \equiv s_p - \bar{s}_P = \underbrace{\theta - c}_{\text{cash flows}} - \underbrace{\frac{\gamma}{\tau_\eta}(n - \alpha Z)}_{\text{discount rate}}
$$

The first term is the expected cash flows from the project net of investment costs. The second term is the discount rate: it is higher when the firm is larger (n is higher) and lower (higher) for green (brown) projects when Z > 0. Green projects carry lower discount rates because they reduce investors' aggregate climate exposure.

## Method

The paper uses a rational-expectations equilibrium approach in a CARA-Normal model with four dates and feedback. The solution method is backward induction (p. 1014, Appendix): equilibrium is conjectured in a piecewise-linear form (eq. A.1), then verified by working backwards from t = 4 to t = 1.

At t = 3, given investment decision k, investor i's optimal demand is (eq. 9, p. 992):

$$
X_{i3} = \frac{\mathbb{E}_{i3}[V(k)] + \gamma\mathbb{C}_{i3}(V(k),\eta_C)z_i - P_3}{\gamma\mathbb{V}_{i3}(V(k))} - (n + X_{i1})
$$

Market clearing at t = 3 implies the equilibrium price (eq. 10, p. 992):

$$
P_3 = \mu_A - \frac{\gamma}{\tau_A}n + k\!\left(\theta - c - \frac{\gamma}{\tau_\eta}(n - \alpha Z)\right)
$$

The welfare measure is the ex-ante expected utility of an arbitrary investor (eq. 25-26, pp. 1001-1002):

$$
\mathcal{W} \equiv \mathbb{E}\!\left[-e^{-\gamma W_i(k(s_p))}\right] = \Pr(k=1)\mathbb{E}\!\left[-e^{-\gamma W_i(1)}\big|k=1\right] + \Pr(k=0)\mathbb{E}\!\left[-e^{-\gamma W_i(0)}\big|k=0\right]
$$

The certainty equivalent (eq. 29, p. 1001) decomposes into four channels: a cash flow channel, a nonclimate risk channel, a climate risk channel, and a risk-sharing/value-of-information channel:

$$
CE(k) = \underbrace{\mathbb{E}[V(k)]n}_{\text{cash flow}} - \frac{\gamma}{2}\!\left(\frac{1}{\tau_A} + k^2\!\left(\frac{1}{\tau_\theta} + \frac{1-\alpha^2}{\tau_\eta}\right)\!\right)n^2 - \frac{\gamma}{2\tau_\eta}(\mu_Z - k\alpha n)^2(1+\Gamma) - \frac{1}{\gamma}\log(D(k))
$$

where $$\Gamma(k)$$ captures the amplification of climate risk disutility through exposure heterogeneity (eq. 31, p. 1002) and $$D(k)$$ captures the value of information (eq. 30, p. 1001).

## Empirical specifications

This is a pure theory paper. There are no regressions or empirical specifications. The paper's propositions are proved analytically (Appendix, pp. 1014-1028). The only "empirical" content is calibrated comparative statics in Figures 2 and 3, using parameter values (tau\_theta = tau\_eta = tau\_A = 1, tau\_Z = mu\_Z = 0.5, n = 0.1 for Figure 2; tau\_theta = 0.5, tau\_Z = 3, tau\_zeta = 2, mu\_A = 0, tau\_A = 5, mu\_theta = c = tau\_eta = gamma = mu\_Z = n = alpha = 1 for Figure 3).

**Figure 2 (p. 999).** Compares Prob(invest) vs climate exposure alpha under cash-flow and price maximization. For ex-ante profitable projects (mu\_theta > c, Panel A) and ex-ante unprofitable projects (mu\_theta < c, Panel B). Key finding: in Panel A, the cash-flow rule's probability of investment is U-shaped in alpha while the price rule shows an opposite pattern. The two rules produce qualitatively different comparative statics for greenness.

**Figure 3 (p. 1009).** Plots ex-ante welfare with and without feedback as functions of (i) precision of outside exposures tau\_zeta and (ii) asset supply n. Shows feedback reduces welfare when n is small (Panel B) or when risk-sharing gains are large (Panel A), even though the manager's objective always improves.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| No empirical data used | Pure theory paper; Figures 2-3 use analytical calibrations only | N/A |

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13427) if you are:
building or extending feedback-effects models that incorporate systematic risk factor loadings;
studying how managerial compensation tied to cash flows versus stock prices affects green investment;
interested in the welfare implications of feedback when investors have heterogeneous climate risk exposures;
looking for a tractable CARA-Normal framework linking production-based asset pricing models (Cochrane (1991)) to feedback effects.

The locators above point to the exact propositions. The proofs are in the Appendix (pp. 1014-1028) and Internet Appendix.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pp. 981-1028. DOI: [10.1111/jofi.13427](https://doi.org/10.1111/jofi.13427). Copyright 2025 the American Finance Association. Wiley VOR licence; no CC licence. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. Extract only; the verbatim PDF is not reproduced here.

> Banerjee, Snehal, Bradyn M. Breon-Drish, and Kevin M. Smith. "Feedback Effects and Systematic Risk Exposures." *The Journal of Finance* 80, no. 2 (April 2025): 981-1028. DOI: 10.1111/jofi.13427.
