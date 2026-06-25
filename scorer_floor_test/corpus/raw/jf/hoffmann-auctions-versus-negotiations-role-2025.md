---
title: "Auctions versus Negotiations: Hoffmann & Vladimirov (2025)"
description: >-
  Distilled: When payments can have a contingent component (equity, royalties,
  performance bonuses), a seller facing fewer bidders in optimally structured
  negotiations can earn strictly higher revenue than an auction with one more
  competing bidder. The key driver is bargaining power over the payment
  structure, not reserve-price setting. J. Finance 2025, CC BY-NC 4.0. Six
  core results with source locators, the model, and the formal propositions.
sidebar:
  label: Hoffmann-Vladimirov 2025
  order: 1
tags: [paper-summary, market-design, auctions, mergers-acquisitions, contract-theory,
       theory, open-access, peer-reviewed, unreplicated]
paper:
  authors: Florian Hoffmann, Vladimir Vladimirov
  authorList:
    - { family: Hoffmann, given: Florian, orcid: "0000-0002-1147-0652", affiliation: KU Leuven }
    - { family: Vladimirov, given: Vladimir, orcid: "0000-0003-0747-4834", affiliation: "University of Amsterdam and CEPR" }
  year: 2025
  venue: "The Journal of Finance 80(3), June 2025, 1769-1813"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13446
  jel:
    codes: [D44, G34, D82]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Auction Theory and Applications", "Digital Platforms and Economics", "Corporate Finance and Governance"]
  dataAccess: public
  outcome:
    - seller expected revenue under negotiations vs. auctions
    - optimal payment structure (cash vs. contingent mix)
    - conditions under which negotiations dominate competition
  outcomeClass: [market-microstructure, firm-dynamics]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-04-07; corroborated by artifact p.1769 Creative Commons
    Attribution-NonCommercial License notice)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "blocked-paywall (Wiley site wrapper; CC BY-NC VOR licence confirmed in Crossref DOI metadata 2026-06-06)"
  redistribution: extract-only (CC BY-NC 4.0 permits reproduction for non-commercial purposes; PDF not hosted in this batch)
  resultsCount: 6
  citedByCount: 2
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, bayesian-persuasion]
  contributionType: [new-theory]
  mechanisms: [information-asymmetry]
  scope:
    region: theoretical
  relatesTo:
    - { cite: "Bulow & Klemperer (1996)", relation: contradicts, note: "overturns their cash-auction result: with general payment structures negotiations can beat one more competing bidder" }
    - { cite: "Myerson (1981)", doi: '10.1287/moor.6.1.58', relation: builds-on, note: "revenue equivalence theorem underlies the auction revenue comparison" }
    - { cite: "DeMarzo, Kremer & Skrzypacz (2005)", doi: '10.1257/0002828054825475', relation: builds-on, note: "security-bid auctions with general payment structure in the competition benchmark" }
    - { cite: "Inderst & Vladimirov (2019)", doi: '10.1287/mnsc.2018.3076', relation: extends, note: "extends their rent-extraction efficiency trade-off to allow general payment structures in negotiations" }
    - { cite: "Liu & Bernhardt (2021)", doi: '10.1111/jofi.13018', relation: extends, note: "extends their full-surplus extraction result to binary cash flows and general securities" }
    - { cite: "Boone & Mulherin (2007)", doi: '10.1111/j.1540-6261.2007.01225.x', relation: tests, note: "motivating empirical fact that negotiations with few bidders are at least as common as auctions in M&A without lower premia" }
  openQuestions:
    - "Full characterization of the unrestricted optimal selling mechanism with general security payments and multiple bidders when bidders' virtual valuation is not monotone in type (p. 1793, footnote 20)."
    - "Extensions to two-sided private information where the seller also has private information about asset quality, and how the seller's information-revelation incentive interacts with mechanism choice (p. 1801)."
    - "Quantitative analysis of common values, seller risk aversion, and external financing constraints as additional factors shaping the negotiations-versus-competition choice (p. 1800-1801, Internet Appendix)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1769-1813 plus appendix); six results extracted from the PDF. Not human-verified. Not reproduced. Pure theory paper: no empirical data, no findings[] axis." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all six proposition locators and equation terms confirmed correct. Fixed: removed moral-hazard from mechanisms (paper is adverse-selection/hidden-type, not hidden-action); removed new-fact from contributionType (pure theory, no empirical regularity introduced); replaced firm-financing with firm-dynamics in outcomeClass (paper is about selling mechanism design in M&A/patent contexts, not firm capital structure)." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13446", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-04-07" }
  rightsSignalConflict: false
---

**What this is.** The paper's core propositions, the model it builds on (a
seller choosing between depth and breadth of bidder competition when payments
can be contingent), and the theoretical mechanism it contributes: enough to
know what it found and how, without reading all 45 pages. To replicate or
extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13446).

## TL;DR

The paper develops a theory of auctions versus negotiations that allows for
general (state-contingent) payment structures. A seller choosing between
optimal negotiations with a small group of bidders and an ascending-bid
auction with one more bidder can strictly prefer negotiations - even against
the benchmark result of Bulow and Klemperer (1996) that auctions dominate. The key
driver is not the reserve price but bargaining power over the payment
structure: when the asset is complementary to bidder productivity (synergies
increase in types), negotiating for contingent payments (equity, royalties,
performance bonuses) extracts more rent than cash competition. The paper
builds on the rent-extraction efficiency trade-off studied by Inderst and
Vladimirov (2019), extends the full-surplus extraction result of Liu and
Bernhardt (2021) to general securities, and uses the security-bid auction
framework of DeMarzo, Kremer, and Skrzypacz (2005). The motivating empirical
fact that negotiations with few bidders are as common as auctions without
lower premia comes from Boone and Mulherin (2007). The auction revenue
benchmark draws on Myerson (1981)'s revenue equivalence theorem. Negotiations
dominate if the type distribution is sufficiently dispersed, absolute
valuations are high, and the complementarity condition holds.

## Core results

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | If the seller can extract the full surplus in bilateral negotiations, her expected revenue is **strictly higher** than from an auction with two cash-bidding competitors | Proposition 1(i), p. 1780 | With uniform $$\theta$$, bilateral negotiations yield $$\Pi^{fb}_{neg} = (\alpha_Y - \alpha_N + \frac{1}{2}(\beta_Y - \beta_N))\Delta x$$ versus auction $$\Pi_{comp} = (\alpha_Y - \alpha_N + \frac{1}{3}(\beta_Y - \beta_N))\Delta x$$; negotiations up to 50% higher in Example 1 |
| R2 | Full-surplus extraction requires the seller to negotiate for **contingent payments**: the first-best contract has $$\Delta w^{fb} > 0$$ and is feasible iff valuations are increasing in productivity (complements case, $$\beta_Y/\beta_N \in (1, \alpha_Y/\alpha_N]$$) | Proposition 1(ii), pp. 1779-1780 | The first-best contract is $$\{w^{fb}, \Delta w^{fb}\}$$ with $$\Delta w^{fb} = (1-\beta_N/\beta_Y)\Delta x > 0$$ and $$w^{fb} = \alpha_Y(\beta_N/\beta_Y - \alpha_N/\alpha_Y)\Delta x$$ |
| R3 | In the **substitutes case** ($$v'(\theta) < 0$$), an auction with one more bidder always yields higher expected revenue than optimal negotiations | Proposition 2, p. 1786 | In substitutes, seller optimally demands pure cash in negotiations (Lemma 2) and bidders choose cash in auctions (Lemma 3), so payment structure is irrelevant; Bulow-Klemperer result applies directly |
| R4 | In the complements case ($$v'(\theta) > 0$$) when full surplus extraction is infeasible, **efficient bilateral negotiations dominate competition** if and only if the Gini coefficient $$G$$ of the productivity-type distribution satisfies $$G \geq \frac{\alpha_Y/\alpha_N - 1}{\beta_Y/\beta_N - 1}$$ | Proposition 3, equation (20), p. 1788 | Condition is always satisfied if $$\alpha_Y/\alpha_N \geq 1/G$$; always holds for any $$\beta_Y/\beta_N > \alpha_Y/\alpha_N$$ if $$\alpha_Y/\alpha_N \geq 1/G$$ |
| R5 | **Setting the payment structure takes precedence** over setting a reserve price in the seller's pecking order: bargaining power over the payment structure has equilibrium value on its own, but bargaining power over the reserve price is valuable only when combined with payment-structure power | Proposition 5, p. 1791 | Formally, $$\Pi^r_{neg}$$ is always smaller than $$\Pi_{comp}$$, while $$\Pi^{s+r}_{neg}$$ can be larger than $$\Pi_{comp}$$, and $$\Pi^s_{neg}$$ can also be larger than $$\Pi_{comp}$$ |
| R6 | The optimal selling mechanism with $$n \geq 2$$ bidders is a **two-stage mechanism**: Stage 1 is a standard English auction to identify the highest valuation bidder; Stage 2 is a take-it-or-leave-it offer with the seller's preferred payment structure to the last remaining bidder | Proposition 6, p. 1793 | The Stage 2 offer is: complements case with full surplus extractable, demands $$\omega^{FB}$$; otherwise demands $$w = 0$$, $$\Delta w = (1 - p_{N}(\tilde\theta)/p_Y(\tilde\theta))\Delta x$$ at the optimal reserve |

**Overall (paper's conclusion).** Negotiations over payments are valuable in
many corporate finance settings. The paper resolves the theoretical puzzle
that negotiations are widely observed even when their revenue advantage over
auctions is difficult to explain with reserve prices alone. The key value
driver in negotiations is bargaining power over the mix of cash and contingent
pay, not the reserve price. Negotiations are more likely to dominate when the
asset creates higher synergies at more productive types, valuations are
dispersed, and the type-independent component of valuations is high relative
to the total upside.

## Theory / model

The paper studies a single seller (she) selling an indivisible asset to $$n$$
risk-neutral bidders (they/he) indexed $$i = 1, \ldots, n$$. The asset can be a
takeover target, patent, or employee's human capital. All parties are
risk-neutral and there is no discounting.

**Project cash flows and bidder types.** Each bidder $$i$$ has a productivity
(quality) type $$\theta_i$$ drawn independently from distribution $$F$$ on
$$[0, 1]$$. The project either fails (cash flow $$x \geq 0$$) or succeeds (cash
flow $$x + \Delta x > x$$). The probability of success depends on bidder type
and whether the bidder acquires the asset ($$a_i = Y$$) or not ($$a_i = N$$),
with the linear specification (equation (2), p. 1776):

$$
p_{a}(\theta) = \alpha_a + \beta_a \theta, \quad a \in \{Y, N\}, \quad \theta \in [0,1], \tag{2}
$$

where $$\alpha_a, \beta_a > 0$$ and $$\alpha_a + \beta_a \leq 1$$. A bidder's
expected cash flow under allocation $$a$$ is $$X_a(\theta) = x + p_a(\theta)\Delta x$$,
strictly increasing in $$\theta$$. A bidder's valuation is his willingness to
pay for the asset (equation (1), p. 1776):

$$
v(\theta) := X_Y(\theta) - X_N(\theta) = (p_Y(\theta) - p_N(\theta))\Delta x. \tag{1}
$$

The **complements case** arises if $$\beta_Y/\beta_N > 1$$ so that $$v'(\theta) > 0$$
(more productive types have higher willingness to pay). The **substitutes
case** arises if $$\beta_Y/\beta_N < 1$$ so that $$v'(\theta) < 0$$.

**Payment contracts.** Payments can be in general securities. If bidder $$i$$
acquires the asset, he pays the seller $$w_i$$ in the low-cash-flow state and
$$w_i + \Delta w_i$$ in the high-cash-flow state. Here $$w_i$$ is the cash
payment, $$\Delta w_i \geq 0$$ is the contingent payment, and the payment
structure is captured by the ratio $$\omega_i = \Delta w_i/(w_i + \Delta w_i)$$.
Examples of contingent payments include royalties, stock options, and
performance bonuses.

The seller's expected payment from a contract $$\omega = \{w, \Delta w\}$$ when
the buyer's type is $$\theta$$ is (p. 1779):

$$
\pi(\theta, \omega) := w + p_Y(\theta)\Delta w.
$$

Full surplus extraction requires $$\pi(\theta, \omega) = v(\theta)$$ for all
$$\theta$$, which from equation (3) (p. 1779) gives:

$$
w + p_Y(\theta)\Delta w = (p_Y(\theta) - p_N(\theta))\Delta x \quad \text{for all } \theta. \tag{3}
$$

The first-best contract solving (3) is (equations (4)-(5), p. 1779):

$$
\Delta w^{fb} = \left(1 - \frac{\beta_N}{\beta_Y}\right)\Delta x, \tag{4}
$$

$$
w^{fb} = \alpha_Y\left(\frac{\beta_N}{\beta_Y} - \frac{\alpha_N}{\alpha_Y}\right)\Delta x. \tag{5}
$$

This contract is feasible ($$w^{fb}, \Delta w^{fb} \geq 0$$) if and only if
$$\beta_Y/\beta_N \in (1, \alpha_Y/\alpha_N]$$, that is, in the complements case but
not too steeply.

**Game structure.** At $$t = 0$$ the seller decides between (i) negotiations:
choosing the optimal mechanism for the $$n$$ bidders already present, including
setting the payment structure; or (ii) competition: attracting one more bidder
so that $$n + 1$$ bidders compete in a standard ascending-bid (English) auction
where bidders choose their own payment structure. Cash flows are realized at
$$t = 1$$ and the winning bidder pays according to the agreed contract (pp.
1777-1778).

## Method

The paper's solution method is mechanism design with state-contingent payments
and bilateral-contract analysis under asymmetric information, building on
`principal-agent` contracting and elements of `bayesian-persuasion` (the
seller's mechanism design with general securities).

**Optimal negotiations (seller designs the mechanism).** The seller maximizes
expected revenue over a menu of contracts $$W$$, with the set of accepting types
$$\Theta_W \subseteq [0,1]$$. The seller's problem (equation (6), p. 1781) is:

$$
\max_W \int_{\Theta_W} \pi(\theta, \omega_\theta)\,dF(\theta) + \int_{[0,1]\setminus\Theta_W} \underline{w}\,dF(\theta), \tag{6}
$$

subject to feasibility ($$w_\theta, \Delta w_\theta \geq 0$$), individual
rationality, and incentive compatibility. Participation requires (equations
(7)-(8), p. 1781):

$$
v(\theta) - \pi(\theta, \omega_\theta) = \max_{\omega \in W} v(\theta) - \pi(\theta, \omega) \geq 0 \quad \text{for all } \theta \in \Theta_W, \tag{7}
$$

$$
\max_{\omega \in W} v(\theta) - \pi(\theta, \omega) < 0 \quad \text{for all } \theta \notin \Theta_W. \tag{8}
$$

The cutoff type $$\tilde\theta(\omega)$$ indifferent between acquiring and not is
(equation (9), p. 1782):

$$
\tilde\theta(\omega) := \frac{w + \alpha_N \Delta x - \alpha_Y(\Delta x - \Delta w)}{\beta_Y(\Delta x - \Delta w) - \beta_N \Delta x}. \tag{9}
$$

The seller's information rent for type $$\theta > \tilde\theta$$ under the
contingent-only contract ($$w = 0$$) is (equation (10), p. 1782):

$$
v(\theta) - \pi(\theta, \omega) = (\theta - \tilde\theta)\beta_Y \left(\underbrace{\left(1 - \frac{\beta_N}{\beta_Y}\right)\Delta x}_{= \Delta w^{fb}} - \Delta w\right). \tag{10}
$$

**Competition (bidders choose payment structure).** The English auction
establishes a reservation price that each active bidder must match. Remaining
active bidders choose whether to compete in cash or other securities, subject
to the seller's acceptance constraint (equation (12), p. 1785):

$$
\int_0^1 \pi(\theta, \omega)\,d\widetilde{F}(\theta|\omega) \geq \underline{w}. \tag{12}
$$

The equilibrium outcome is given by Lemma 3: with $$n \geq 2$$ bidders, they
optimally offer pure cash payments ($$w > 0$$, $$\Delta w = 0$$), and the winner
pays the second-highest valuation (p. 1785-1786). The seller's expected revenue
is the expected valuation of the bidder with the second-highest valuation
(equation (16), p. 1787):

$$
\Pi_{comp} = \int_0^1 v(\theta)\, 2(1 - F(\theta))\,dF(\theta). \tag{16}
$$

**Revenue difference decomposition.** Taking the difference between
$$\Pi_{neg}(0)$$ (efficient negotiations without a reserve price) and
$$\Pi_{comp}$$ (equations (17)-(19), p. 1787):

$$
\Pi_{neg}(0) - \Pi_{comp} = \int_0^1 v'(\theta)F(\theta)(1-F(\theta))\,d\theta - \int_0^1 \varrho(\theta, 0)\,dF(\theta), \tag{19}
$$

where the first term is positive in the complements case ($$v'(\theta) > 0$$)
and equals $$\Pi^{fb}_{neg} - \Pi_{comp}$$, while the second term is the
bidder's expected information rent in negotiations. Negotiations dominate iff
the rent is sufficiently small, which is governed by condition (20).

## Empirical specifications

This is a pure-theory paper. There are no regressions, datasets, or empirical
specifications. The paper's propositions are established by analytical proofs
in the Appendix (pp. 1801-1813). The paper does derive comparative statics and
testable implications for M&A, patent licensing, and employee compensation.

**Key theoretical comparative statics (Proposition 4, p. 1790).** The revenue
advantage of efficient bilateral negotiations $$\Pi_{neg}(0) - \Pi_{comp}$$ is
higher if:

(i) The bidders' productivity type distribution becomes more dispersed in the
sense of a mean-preserving spread (higher Gini coefficient $$G$$), because more
dispersed valuations lower the auction revenue $$\Pi_{comp}$$ (the second-highest
valuation falls in expectation) while leaving $$\Pi_{neg}(0)$$ unchanged.

(ii) The type-independent component of bidders' valuations, captured by
$$\alpha_Y/\alpha_N$$, is higher, because higher $$\alpha_Y/\alpha_N$$ allows the
seller to demand a larger contingent payment $$\Delta w$$ acceptable to all
types, moving closer to the full-rent extraction contract $$\Delta w^{fb}$$.

**Necessary and sufficient condition for negotiations to dominate (equation (20),
p. 1788):**

$$
G := \frac{\int_0^1 F(\theta)(1-F(\theta))\,d\theta}{\int_0^1 \theta\,dF(\theta)} \geq \frac{\beta_Y/\beta_N\,/\,\alpha_Y/\alpha_N - 1}{\beta_Y/\beta_N - 1}, \tag{20}
$$

where $$G \in (0,1)$$ is the Gini coefficient of the productivity-type
distribution $$F$$. This condition is always satisfied if $$\alpha_Y/\alpha_N \geq 1/G$$.

**Multi-bidder extension (Proposition 7, p. 1794-1795).** The condition for
efficient negotiations with $$n$$ bidders to dominate competition with $$n+1$$
bidders in the complements case (equation (21), p. 1795):

$$
\frac{\int_0^1 F(y)^n (1-F(y))\,dy}{\int_0^1 \left(\int_y^1 \frac{\alpha_Y(q-y)}{\alpha_Y + \beta_Y y} dF(q)\right)(n-1)F(y)^{n-2}\,dF(y)} \geq \frac{\beta_Y/\beta_N\,/\,\alpha_Y/\alpha_N - 1}{\beta_Y/\beta_N - 1}. \tag{21}
$$

This condition holds for any $$\beta_Y/\beta_N > \alpha_Y/\alpha_N$$ if
$$\alpha_Y/\alpha_N \geq 1/G_n$$, where $$G_n$$ is explicitly defined in the
Appendix.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| None (pure theory) | All results are derived analytically | N/A |

No empirical data were used. The paper's claims are theoretical propositions
derived from the formal model. Testable implications for M&A, patent licensing,
and compensation are discussed in Section VII (pp. 1796-1800).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13446) if you are:
studying optimal mechanism design with general security payments; designing
M&A sale processes and evaluating when negotiations versus auctions maximize
revenue; modeling patent licensing or employee compensation negotiation;
extending the framework to seller private information, common values, or
risk aversion (Internet Appendix); or checking the full formal proofs
(Appendix, pp. 1801-1813).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025. This
distillation was extracted by an LLM on 2026-06-06 and is **not
human-verified or independently reproduced**. The CC BY-NC 4.0 licence
permits reproduction for non-commercial purposes; the verbatim PDF is not
hosted in this batch.

Citation: Hoffmann, Florian, and Vladimir Vladimirov.
"Auctions versus Negotiations: The Role of the Payment Structure."
*The Journal of Finance* 80, no. 3 (June 2025): 1769-1813.
DOI: 10.1111/jofi.13446. © 2025 The Author(s).
Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
This page is an **adaptation** by the Institute for Automated Research:
core results extracted and re-expressed; **changes were made**.
