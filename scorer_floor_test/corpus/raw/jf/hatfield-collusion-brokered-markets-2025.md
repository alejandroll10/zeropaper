---
title: "Collusion in Brokered Markets: Hatfield, Kominers & Lowery (2025)"
description: >-
  Distilled: Models collusion in brokered markets (e.g., US residential real
  estate) as a repeated extensive-form game, showing that brokers can sustain
  prices substantially above marginal cost even with many independent agents
  and easy entry, by refusing to work with price deviators within-period. J.
  Finance 2025, paywalled. Six core results with source locators, the model,
  and the equilibrium construction.
sidebar:
  label: Hatfield-Kominers-Lowery 2025
  order: 1
tags: [paper-summary, market-microstructure, real-estate, collusion, market-design,
       repeated-games, theory, peer-reviewed, unreplicated]
paper:
  authors: John William Hatfield, Scott Duke Kominers, Richard Lowery
  authorList:
    - { family: Hatfield, given: John William, orcid: "0000-0002-3339-5059", affiliation: McCombs School of Business, University of Texas at Austin }
    - { family: Kominers, given: Scott Duke, orcid: "0000-0002-7608-6619", affiliation: Harvard Business School and Department of Economics, Harvard University }
    - { family: Lowery, given: Richard, affiliation: McCombs School of Business, University of Texas at Austin }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1417–1462
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13432
  jel:
    codes: [L13, D43, G40]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Economic theories and models
    - Banking stability, regulation, efficiency
    - Digital Platforms and Economics
  dataAccess: public
  outcome:
    - highest sustainable industry profits (buyer and seller prices) in brokered markets
    - effect of rebate bans on collusive prices
    - effect of agency fees on collusive prices
  outcomeClass: [market-microstructure]
  license: >-
    Paywalled; Crossref license record: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-03-18. No open-access licence.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/JF site, checked 2026-06-06)
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 3
  methods:
    role: theory
    family: theory
    buildsFrom: [repeated-game, mechanism-design]
  contributionType: [new-theory]
  mechanisms: [market-power, network-exclusion]
  scope:
    region: US
    assetClass: residential real estate brokerage services
  findings:
    - ref: R1
      outcome: highest sustainable industry profits (buyer and seller prices) in brokered markets
      metric: coefficient
      value: "p*_S = v_S for all market concentrations alpha; p*_B = v_B when alpha >= (1-delta)*kappa_B*kappa_S, falling to a formula strictly above zero as alpha -> 0; lim_{alpha->0}(p*_B + p*_S) = (v_B + v_S)(1 - kappa_S) > 0"
      direction: positive
      vsBenchmark: prices remain bounded away from marginal cost regardless of number of agents; contrast with grim-trigger strategies where prices fall to marginal cost as alpha -> 0 (Theorem 1, Figure 1, p. 1427-1428)
    - ref: R2
      outcome: highest sustainable industry profits (buyer and seller prices) in brokered markets
      metric: coefficient
      value: "Exclusion equilibrium prices: q*_B = v_B - kappa_S(v_B + v_S), q*_S = v_S; as alpha -> 0, exclusion and optimal prices converge (Corollary 1)"
      direction: positive
      vsBenchmark: high-agent-count exclusion equilibrium achieves same prices as the more complex optimal equilibrium of Theorem 1 (Theorem 2, p. 1440-1441)
    - ref: R3
      outcome: highest sustainable industry profits under rebate ban
      metric: coefficient
      value: "With rebate ban, lim_{alpha->0}(p*_B + p*_S) = v_B(1 - kappa_S) + v_S; strictly higher than without rebate ban whenever alpha-hat < kappa_S * v_S/(v_S + (1 - kappa_S)*v_B)"
      direction: positive
      vsBenchmark: rebate bans raise collusive profits when market concentration is low; eliminates rebate bans would reduce (but not eliminate) collusion scope (Theorem 3, p. 1446)
    - ref: R4
      outcome: highest sustainable industry profits under agent specialization with agency fees
      metric: coefficient
      value: "lim_{sigma->0}(p*_B + p*_S) = (v_B + v_S)(1 - kappa_S) + kappa_S*c; strictly higher than without agent specialization"
      direction: positive
      vsBenchmark: agent specialization and agency fees increase collusive profits above the symmetric-agent baseline (Theorem 4, p. 1449)
    - ref: R5
      outcome: highest sustainable industry profits under zero-fees model (seller-proficient agents represent buyers)
      metric: coefficient
      value: "lim_{sigma->0}(p*_B + p*_S) = (v_B + v_S)(1 - kappa_S) + kappa_S*c; industry revenue weakly less than with agency fees"
      direction: negative
      vsBenchmark: eliminating agency fees weakly reduces sustainable industry profits relative to allowing fees (Theorem 5, p. 1451)
    - ref: R6
      outcome: highest sustainable industry profits under zero-fees model (buyer-exclusive agents represent buyers)
      metric: coefficient
      value: "When v_B*(1-kappa_S)/kappa_S < c < v_S, prices to buyers are 0 and sellers are charged below v_S; industry revenue weakly less than under agency fees equilibrium (Corollary 2)"
      direction: negative
      vsBenchmark: eliminating agency fees reduces prices when buyer valuations are sufficiently low relative to seller valuations; consistent with Barwick (2018) decoupling argument (Theorem 6, Corollary 2, p. 1452-1453)
  resultType: new-finding
  relatesTo:
    - { cite: "Abreu (1988)", doi: '10.2307/1911077', relation: builds-on, note: "Simple penal codes for infinitely repeated normal-form games; the paper shows these are not sufficient for repeated extensive-form games (p. 1421)" }
    - { cite: "Mailath, Nocke & White (2017)", doi: '10.1111/iere.12219', relation: builds-on, note: "When and how the punishment must fit the crime in repeated extensive-form games; motivates the more complex equilibrium construction here (p. 1421)" }
    - { cite: "Hsieh and Moretti (2003)", relation: cites, note: "Observe that apparent uniformity of commission rates in US real estate presents an enormous puzzle; this paper provides a theory (p. 1418)" }
    - { cite: "Christie and Schultz (1994)", relation: cites, note: "Documented NASDAQ market makers avoiding odd-eighth quotes; analogous in-period punishment behavior (p. 1419)" }
    - { cite: "Han and Hong (2011)", doi: '10.1198/jbes.2011.08314', relation: tests, note: "Tests rebate bans as anticompetitive; this paper confirms rebate bans raise collusive profits in the framework (p. 1421)" }
    - { cite: "Barwick (2018)", relation: tests, note: "Proposed eliminating agency fees to reduce commissions; Corollary 2 formalizes when this reduces collusive prices (pp. 1422, 1453)" }
    - { cite: "Hatfield et al. (2020)", doi: '10.1086/709953', relation: builds-on, note: "Earlier work on collusion in markets with syndication using repeated extensive-form games (p. 1461)" }
  openQuestions:
    - "Whether the analysis extends to settings with imperfect price observability, where agents cannot perfectly detect price deviations; the paper notes that a small probability of detection is sufficient but does not fully characterize the equilibrium price set in that case (§II.C.4, p. 1444-1445)."
    - "The welfare consequences of the proposed policy reforms (rebate-ban elimination, decoupling agency fees) beyond their effect on collusive prices; in particular, whether eliminating agency fees also reduces allocative efficiency by changing which agents represent buyers and sellers (§III.B, p. 1450-1453)."
    - "Extension to settings in which buyers and sellers can meet agents sequentially or in which agents have heterogeneous capacities; the continuum model abstracts from finite-player dynamics (§I.A, p. 1422)."
  replicationCode:
    status: none
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13432
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-03-18. No CC or open-access licence; standard Wiley paywalled VOR terms."
  rightsSignalConflict: false
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 1417-1462); six core results extracted from the PDF. Not human-verified. Not reproduced. Theory paper with no empirical data."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF (pp. 1417-1453); four fixes applied: (1) simplified payoff second sum corrected p^a_{B,t} to p^a_{S,t} (p. 1425); (2) Theorem 3 middle-piece numerator removed spurious -c term not in PDF eq. (24); (3) mechanisms corrected from [market-power, collateral] to [market-power, network-exclusion]; (4) buildsFrom corrected from [promotion-contest, principal-agent] to [repeated-game, mechanism-design] per pp. 1419-1422; outcomeClass trimmed to [market-microstructure]."
---

**What this is.** The paper's core model, theorems, and policy implications: enough to know what was proved and how, without reading the full 46 pages. To replicate or extend it, read the original at [doi.org/10.1111/jofi.13432](https://doi.org/10.1111/jofi.13432).

## TL;DR

The paper explains how the U.S. residential real estate brokerage industry can maintain commissions roughly at 6% of the transaction value, far above competitive cost, even though the industry has many independent agents and easy entry. This is the "enormous puzzle" noted by Hsieh and Moretti (2003). Modeled as a repeated extensive-form game, brokers can sustain collusion by refusing to work with any agent who cuts prices within the current period. Because buyers and sellers expect a price deviator to be excluded from the network of other agents, they demand a large discount to work with that agent, making a small price cut unprofitable. This mechanism works even as the number of agents grows arbitrarily large, unlike standard repeated-game models where collusion breaks down as the number of firms increases. The paper also shows that rebate bans and agent specialization supported by agency fees expand the scope for collusion, while eliminating agency fees ("decoupling") can reduce it.

## Core results

Magnitudes are as reported in the theorems and figures; all results hold for discount factor $$\delta \geq \frac{1}{2}$$.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Highest sustainable prices remain bounded away from marginal cost as market concentration approaches zero; seller price equals full seller surplus | Theorem 1, Figure 1, pp. 1427-1428 | $$p^*_S = v_S$$ for all $$\alpha$$; $$\lim_{\alpha \to 0}(p^*_B + p^*_S) = (v_B + v_S)(1 - \kappa_S) > 0$$ |
| R2 | Simple exclusion equilibrium (prices never change after deviations) achieves same prices as optimal equilibrium as concentration goes to zero | Theorem 2, Corollary 1, Figure 3, pp. 1440-1441 | $$q^*_B = v_B - \kappa_S(v_B + v_S)$$, $$q^*_S = v_S$$; $$\lim_{\alpha \to 0}(p^*_B, p^*_S) = (q^*_B, q^*_S)$$ |
| R3 | Rebate bans raise sustainable collusive prices whenever market concentration is sufficiently low | Theorem 3, Figure 4, p. 1446 | With rebate ban: $$\lim_{\alpha \to 0}(p^*_B + p^*_S) = v_B(1-\kappa_S) + v_S$$; strictly higher than without ban when $$\hat\alpha < \kappa_S v_S / (v_S + (1-\kappa_S)v_B)$$ |
| R4 | Agent specialization with agency fees raises industry profits above the symmetric baseline | Theorem 4, Figure 5, p. 1449 | $$\lim_{\sigma \to 0}(p^*_B + p^*_S) = (v_B + v_S)(1-\kappa_S) + \kappa_S c$$, strictly above baseline |
| R5 | Eliminating agency fees when seller-proficient agents represent buyers weakly reduces sustainable profits | Theorem 5, Figure 6, p. 1451 | Industry revenue weakly below the agency-fee equilibrium; limit revenue same only as $$\sigma \to 0$$ |
| R6 | When buyer valuations are sufficiently low relative to sellers, eliminating agency fees reduces both buyer and seller prices; decoupling weakens collusion | Theorem 6, Corollary 2, pp. 1452-1453 | When $$v_B (1-\kappa_S)/\kappa_S < c < v_S$$: buyer price = 0, seller price below $$v_S$$; total revenue strictly below agency-fee equilibrium |

**Overall (paper's conclusion).** Brokered markets are structurally prone to collusion because the brokerage requirement means that each broker must cooperate with other brokers to complete transactions. This gives incumbents the power to punish price cutters immediately and in-period, so that the gains from deviating vanish even as the number of agents grows large. The result persists under simple exclusion strategies requiring minimal coordination, making it robust to the practical difficulty of fine-tuning punishment across many agents.

## Theory / model

The paper models a brokered market as a repeated extensive-form game played over discrete infinite time with a common discount factor $$\delta \in (0, 1)$$ (p. 1422). There is a finite set of agents $$A$$ with market concentration $$\alpha \equiv \frac{1}{|A|}$$. In each period, a continuum of short-lived buyers $$B_t$$ and sellers $$S_t$$ arrive. Each agent has a buyer capacity $$\kappa_B$$ and a seller capacity $$\kappa_S$$, with $$\kappa_S \leq \kappa_B < \frac{1}{2}$$.

The stage game has four steps (pp. 1422-1424):

1. Each agent $$a$$ posts a buyer price $$p^a_{B,t} \in \mathbb{R}$$ and a seller price $$p^a_{S,t} \in \mathbb{R}$$, publicly observed.
2. Buyers and sellers rank agents and are assigned via random rationing, so no agent represents more than $$\kappa_B$$ buyers or $$\kappa_S$$ sellers.
3. Each agent $$a$$ invites other agents $$\bar{a}$$, including a contingent agency fee $$f^{a \leftarrow \bar{a}}_t \in \mathbb{R}$$ per transaction paid from $$\bar{a}$$'s seller-side commission to $$a$$.
4. Each agent accepts or rejects invitations; the resulting directed network of accepted invitations determines which buyer-seller pairs can be matched.

The agent payoff per period is (pp. 1424-1425):

$$
|\mathbf{B}_t(a)| \sum_{\bar{a} \in A^{a\Rightarrow}_t} \left( |\mathbf{S}_t(\bar{a})| (p^a_{B,t} + f^{a \leftarrow \bar{a}}_t) \right) + |\mathbf{S}_t(a)| \sum_{\bar{a} \in A^{a\leftarrow}_t} \left( |\mathbf{B}_t(\bar{a})| (p^a_{S,t} - f^{\bar{a} \leftarrow a}_t) \right)
$$

which simplifies, as agents in the cooperation phase split profits evenly, to (p. 1425):

$$
|\mathbf{B}_t(a)| \sum_{\bar{a} \in A^{a\Rightarrow}} \left( |\mathbf{S}_t(\bar{a})| (p^a_{B,t} + p^a_{S,t}) \right) + |\mathbf{S}_t(a)| \sum_{\bar{a} \in A^{a\leftarrow}} \left( |\mathbf{B}_t(\bar{a})| (p^a_{S,t} - f^{\bar{a}\leftarrow a}_t) \right).
$$

A key equilibrium refinement is (buyer-and-seller) coordination-proofness: no positive-measure subset of buyers and sellers can jointly deviate to improve all their payoffs (p. 1426). This rules out coordination-failure equilibria in which buyers and sellers refuse to sign up with any agent.

**Identification of the key friction.** The model's main departure from standard Bertrand models is two-sided intermediation: to facilitate a transaction, both the buyer's agent and the seller's agent must agree to work together. A price deviator who cuts prices attracts buyers or sellers away from other agents, but those other agents can refuse network links to the deviator, reducing the probability of a transaction for any buyer or seller who signed up with the deviator. As a result, buyers and sellers demand a large discount from a price deviator, not just a small epsilon discount (p. 1429).

**Theorem 1 (Optimal Collusion, p. 1427).** For $$\delta \geq \frac{1}{2}$$, the highest sustainable industry profits are achieved with prices:

$$
p^*_B = \begin{cases} v_B & \alpha \geq (1-\delta)\kappa_B\kappa_S \\ \dfrac{(1-\delta)\kappa_B(v_B - \kappa_S(v_B+v_S)) + \alpha v_S}{(1-\delta)\kappa_B - \alpha} & \alpha \leq (1-\delta)\kappa_B\kappa_S \end{cases} \tag{1}
$$

$$
p^*_S = v_S. \tag{2}
$$

Moreover, $$\lim_{\alpha \to 0}(p^*_B + p^*_S) = (v_B + v_S)(1 - \kappa_S) > 0$$.

The seller price always equals the full seller surplus $$v_S$$; buyers receive a price below $$v_B$$ because, given that each buyer accesses only $$\kappa_S$$ sellers through a deviating agent, cutting buyer prices is more effective at deterring entry than cutting seller prices.

## Method

The equilibrium is constructed in three phases: a cooperation phase, a $$\hat{a}$$-collusive punishment phase, and a $$\{\hat{a}, a\}$$-collusive punishment phase (p. 1432, Figure 2, p. 1434). This multi-phase construction is necessary because, as Mailath, Nocke, and White (2017) show, simple penal codes sufficient for Abreu (1988)-style infinitely repeated normal-form games are not sufficient in repeated extensive-form games: agents who comply with punishing a deviator must themselves be rewarded in the punishment phase. The paper builds directly on Hatfield et al. (2020), who analyze collusion with syndication using a similar extensive-form repeated-game framework.

**Key quantity: buyer and seller deviation prices.** In the cooperation phase, buyers and sellers are willing to work with a price deviator $$\hat{a}$$ only if the prices $$(\hat{p}^{\hat{a}}_B, \hat{p}^{\hat{a}}_S)$$ satisfy both (p. 1431, eq. 4):

$$
(v_B - \hat{p}^{\hat{a}}_B)\kappa_S \geq v_B - p^*_B \qquad \text{and} \qquad (v_S - \hat{p}^{\hat{a}}_S)\kappa_B \geq v_S - p^*_S.
$$

The highest prices at which buyers and sellers will work with a deviator are therefore (eq. 6, p. 1431):

$$
p^\circ_B = v_B - \frac{1}{\kappa_S}(v_B - p^*_B) \qquad \text{and} \qquad p^\circ_S = v_S - \frac{1}{\kappa_B}(v_S - p^*_S). \tag{6}
$$

Because $$\kappa_S < 1$$, these deviation prices are substantially below $$p^*_B$$ and $$p^*_S$$: the agent must cut prices far enough that buyers and sellers prefer working with a lower-quality network.

**Incentive constraint for non-deviators.** An agent $$a \neq \hat{a}$$ is willing to exclude a price deviator if the discounted future profits from adhering exceed the current gain from working with the deviator (eq. 10-12, pp. 1437-1438):

$$
\frac{\delta}{1-\delta}\frac{\alpha}{1-\alpha}(q^*_B + q^*_S) \geq \frac{\alpha}{1-\alpha}\left[(1-\kappa_S)\kappa_B(p^{\hat{a}}_B + p^*_S) + (1-\kappa_B)\kappa_S(p^*_B + p^{\hat{a}}_S)\right].
$$

This simplifies to the condition $$\delta/(1-\delta) \geq \kappa_B + \kappa_S$$, which holds as long as $$\delta \geq \frac{1}{2}$$. The key observation is that both current profits from working with $$\hat{a}$$ and future profits from adherence are proportional to $$\alpha$$, so the inequality is independent of market concentration.

**Theorem 2 (Exclusion Equilibrium, p. 1440).** For $$\delta \geq \frac{1}{2}$$, there exists an exclusion equilibrium (prices never change after deviations) with prices:

$$
q^*_B = v_B - \kappa_S(v_B + v_S), \qquad q^*_S = v_S. \tag{22, 23}
$$

**Theorem 3 (Rebate Ban, p. 1446).** With a rebate ban (constraint $$p^a_{B,t} \geq 0$$ for all $$a, t$$), for $$\delta \geq \frac{1}{2}$$:

$$
p^*_B = \begin{cases} v_B & \hat\alpha \geq \kappa_S \\ \dfrac{v_B - \kappa_S(v_B + v_S) + \hat\alpha v_S}{1 - \hat\alpha} & \hat\alpha \in \left[\kappa_S \frac{v_S}{v_S + (1-\kappa_S)v_B},\, \kappa_S\right] \\ v_B(1-\kappa_S) & \hat\alpha \leq \kappa_S \frac{v_S}{v_S + (1-\kappa_S)v_B} \end{cases}, \quad p^*_S = v_S, \tag{24, 25}
$$

where $$\hat\alpha = \frac{\alpha}{(1-\delta)\kappa_B}$$. Profits are strictly higher than without a rebate ban whenever $$\hat\alpha < \kappa_S v_S/(v_S + (1-\kappa_S)v_B)$$.

## Empirical specifications

This is a pure-theory paper. There are no regression specifications, data, or empirical tests. The paper provides calibrated numerical examples for Figures 1-7 using parameter values such as $$\delta = 3/4$$, $$v_B = 3$$, $$v_S = 5$$, $$\kappa_B = 1/5$$, $$\kappa_S = 1/6$$, to illustrate how prices vary with market concentration. These figures confirm that buyer prices can be negative for sufficiently low market concentration and that seller prices remain at $$v_S$$ throughout.

The paper applies the model to several policy-relevant cases:

- **Rebate bans** (§III.A): Modeled as the constraint $$p^a_{B,t} \geq 0$$; shown to raise collusive profits for low concentration (Theorem 3). Han and Hong (2011) had argued rebate bans are anticompetitive; the model confirms and formalizes this. Christie and Schultz (1994) documented analogous in-period punishments by NASDAQ market makers via odd-eighth avoidance.
- **Agent specialization and agency fees** (§III.B): A model with buyer-exclusive agents $$A_B$$ and seller-proficient agents $$A_S$$, where seller-proficient agents incur cost $$c \leq v_B$$ to represent buyers. Theorems 4-6 characterize optimal prices. Barwick (2018) proposed eliminating agency fees; Corollary 2 formalizes when this lowers collusive prices.
- **For-sale-by-owner and buyer self-representation** (§III.C): Shown not to resolve collusion because self-representing sellers/buyers can also be excluded by incumbent agents.
- **iBuyers** (§III.D): Predicted to offer the same agency fees as traditional brokers to avoid ostracism (consistent with observed iBuyer behavior).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| U.S. residential real estate industry (stylized facts: 6% commission, observed steering behavior) | Motivating application and empirical context for the model | No page yet |

This is primarily a theory paper. No quantitative datasets are used; all results are derived from the formal model. Motivating facts are sourced from prior empirical work (Hsieh and Moretti (2003), Federal Trade Commission (1983)) and DOJ/FTC reports.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13432) if you are: (i) working on the theory of collusion in intermediated markets and need the proofs in Appendices B-C and the Internet Appendix; (ii) analyzing policy proposals for real estate brokerage (rebate bans, decoupling, MLS reform) and want the formal comparative statics; (iii) extending the model to finite buyers/sellers or to settings where price observability is imperfect (§II.C.4); or (iv) studying other two-sided intermediated markets (municipal bonds, Nasdaq dealer markets, venture capital) where analogous exclusion mechanisms may apply.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. DOI: [10.1111/jofi.13432](https://doi.org/10.1111/jofi.13432). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The article is paywalled; this page reproduces only short extracts for scholarly commentary under fair use. No PDF is hosted.

> Hatfield, John William, Scott Duke Kominers, and Richard Lowery.
> "Collusion in Brokered Markets."
> *The Journal of Finance* 80, no. 3 (June 2025): 1417-1462.
> DOI: 10.1111/jofi.13432. © 2025 the American Finance Association.
> Extract-only; all rights reserved by the publisher.
