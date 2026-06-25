---
title: "Uncertainty, Contracting, and Beliefs in Organizations: Dicks & Fulghieri (2025)"
description: >-
  Distilled: In a multidivisional firm, uncertainty aversion by managers creates
  endogenous disagreement that raises incentive costs; HQ can hedge this by
  designing contracts with cross-divisional exposure (equity or relative-performance
  pay), improving effort and aligning beliefs. Review of Financial Studies 2025,
  paywalled. Five core results with source locators, the model with its key
  equations, and the method.
sidebar:
  label: Dicks-Fulghieri 2025
  order: 1
tags: [paper-summary, contract-theory, executive-compensation, organizational-economics,
       uncertainty, moral-hazard, peer-reviewed, unreplicated]
paper:
  authors: David L. Dicks, Paolo Fulghieri
  authorList:
    - { family: Dicks, given: David L., orcid: "0000-0001-7036-2638", affiliation: Baylor University }
    - { family: Fulghieri, given: Paolo, affiliation: "University of North Carolina, CEPR, and ECGI" }
  year: 2025
  venue: The Review of Financial Studies 38(7), 2025, 2182-2225
  venueShort: Rev. Financ. Stud. 2025
  doi: 10.1093/rfs/hhaf005
  jel:
    codes: [D86, D81, J33]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: [Complex Systems and Decision Making]
  dataAccess: public
  outcome:
    - optimal incentive contract structure in multidivisional firms
    - pay-performance sensitivity under uncertainty
    - prevalence of equity-based vs relative-performance compensation
  outcomeClass: [labor-careers-health]
  license: "Oxford standard publication reuse rights (confirmed via Crossref DOI metadata: content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days 0, start 2025-03-14)"
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Oxford Academic, 2026-06-06)
  redistribution: extract-only
  resultsCount: 5
  citedByCount: 4

  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, mechanism-design]

  contributionType: [new-theory]
  mechanisms: [moral-hazard, information-asymmetry, learning, belief-endogeneity]

  scope:
    region: theoretical
    assetClass: executive compensation contracts

  relatesTo:
    - { cite: "Holmstrom (1979)", doi: '10.2307/3003320', relation: builds-on, note: "standard principal-agent moral hazard framework the paper extends to uncertainty aversion" }
    - { cite: "Gilboa and Schmeidler (1989)", doi: '10.1016/0304-4068(89)90018-9', relation: builds-on, note: "maxmin expected utility (MEU) and uncertainty hedging axiom underlying the model" }
    - { cite: "Hansen and Sargent (2001)", doi: '10.1257/aer.91.2.60', relation: builds-on, note: "relative entropy criterion used to define the parametric core beliefs set" }
    - { cite: "Dicks and Fulghieri (2019)", relation: extends, note: "earlier working paper (risk-neutral agents) extended here to risk-averse division managers" }
    - { cite: "Dicks and Fulghieri (2021)", doi: '10.1093/rfs/hhaa065', relation: extends, note: "companion RFS paper on uncertainty and innovation; same MEU-with-relative-entropy approach" }
    - { cite: "Holmstrom (1982)", relation: builds-on, note: "moral hazard in teams; paper rules out synergies in the basic model following this benchmark" }
    - { cite: "Holmstrom and Milgrom (1987)", doi: '10.2307/1913238', relation: builds-on, note: "linearity of optimal contracts under CARA utility; this paper derives linear contracts in the same spirit" }
    - { cite: "Miao and Rivera (2016)", doi: '10.3982/ecta13127', relation: cites, note: "robust contracts in continuous time; alternative uncertainty formulation" }

  openQuestions:
    - "Extending the model to multitasking settings, as in Holmstrom and Milgrom (1991), and examining the interaction of uncertainty with task assignment and optimal compensation (Conclusion, p. 2218)."
    - "Examining the impact of uncertainty on organization design; plausibility that high-uncertainty organizations have flatter structures for uncertainty hedging purposes (Conclusion, p. 2218)."
    - "A full general-equilibrium analysis of optimal corporate hedging policy combining financial, real, and contractual hedging, and their interactions (Section 5.1, p. 2214)."
    - "Examining matching of heterogeneous agents to heterogeneous firms in a labor-market equilibrium (Conclusion, p. 2218)."

  replicationCode:
    status: none

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 2182-2225); five results extracted from the paywalled PDF. Not human-verified. Not reproduced. No replication code stated by authors (Code Availability statement p. 2218)." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all five Core-results rows confirmed correct (Theorem 1 p. 2201, Corollary 1 p. 2203, Theorem 3 p. 2207, Theorem 4 p. 2209, Lemma 5/Theorem 5 p. 2213, Theorem 7 p. 2215); all equations (eqs. 1, 3, 5, 6, 7, 8, 10, 11, 20, 21, 25) verified term-by-term; three fixes applied: removed off-registry outcomeClass 'firm-financing' (paper studies incentive contracts, not capital structure), removed methods.identification field (omitted for role:theory papers per classification rules), and removed contributionType 'new-fact' (paper explains known stylized facts theoretically but introduces no new empirical regularity)." }

  licenceVerification:
    - { source: "Crossref REST API works/10.1093/rfs/hhaf005", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-03-14; Oxford standard reuse rights, not CC" }

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical model with its key
equations, and the method: enough to know what it found and how, without reading
all 44 pages. To replicate or extend it, read the full source at
[https://doi.org/10.1093/rfs/hhaf005](https://doi.org/10.1093/rfs/hhaf005).

## TL;DR

Dicks and Fulghieri study optimal incentive contracts in a two-division firm where
headquarters (HQ) and division managers are uncertainty averse in the sense of
Gilboa and Schmeidler (1989): they hold a set of admissible priors and evaluate
random variables by their worst-case expected utility. The paper extends the
classical moral hazard framework of Holmstrom (1979) and the linearity results of
Holmstrom and Milgrom (1987) to settings where agents lack a single prior on
the probability distribution of cash flows. Uncertainty creates two novel costs.
First, an "incentive effect": conservative beliefs about own division productivity
suppress effort, requiring higher pay-performance sensitivity. Second, an
"uncertainty discount": HQ and division managers disagree on the value of
compensation contracts because their positions in the hierarchy give them
different exposures to uncertainty, making participation constraints more costly.
The key insight is that HQ can partly resolve both costs by designing contracts
with cross-divisional exposure. Linking pay to the other division's output hedges
division managers' uncertainty, improves beliefs, and lowers incentive costs.
This motive for cross-pay is present even when divisions are uncorrelated, in
contrast to the informativeness principle of Holmstrom (1982). When uncertainty
is large enough, optimal contracts are pure equity (equal beta and gamma, beta = gamma),
which dominates relative-performance pay irrespective of cash-flow correlation,
unlike the prediction of Miao and Rivera (2016) for uncertainty-neutral agents.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Cross-division pay is optimal even absent correlation**, violating the informativeness principle; uncertainty aversion motivates uncertainty hedging through equity or relative-performance contracts | Theorem 1, p. 2201; Corollary 1, p. 2203 | Optimal cross-division exposure $$\lvert\gamma_d\rvert = \xi_d \beta_d > 0$$ whenever division managers face uncertainty ($$\eta > 0$$); pay-performance sensitivity $$\beta_d = 1/(1 + 3(1 - \hat{q}^d_d/q_d)) < 1$$ and effort are both decreasing in $$\eta$$ (eq. 20) |
| R2 | **Equity-based pay is optimal over relative-performance pay when uncertainty is sufficiently large** ($$\eta > \tilde{\eta}$$), irrespective of cash-flow correlation | Corollary 1(ii), p. 2203; Theorem 3, p. 2207; Theorem 4, p. 2209 | Pure equity contract: $$\beta_d = \gamma_d$$ with $$\beta + \gamma < 1$$ for $$\eta > 2\ln(3/2)$$; holds even for positively correlated divisions where standard theory predicts $$\gamma < 0$$ (relative performance) |
| R3 | **HQ uncertainty aversion makes relative-performance contracts even more costly**; the HQ uncertainty discount adds disagreement that raises the cost of having HQ hold a "short" position in the relative-performance hedge | Theorem 3, p. 2207; Section 4.1, pp. 2206-2208 | Pay-performance sensitivity $$\beta_d = \gamma_d = 1/(1+3(1-\hat{q}^d_d/\hat{q}^{HQ}_d)) < 1$$, with pay-performance sensitivity increasing in HQ uncertainty $$\eta^{HQ}$$ (Figure 5); pure equity optimal whenever $$\eta > \eta^{HQ} + 2\ln(3/2)$$ |
| R4 | **Internal hedging (cross-division pay) dominates external benchmarks** for uncertainty hedging; with large HQ uncertainty, optimal contracts exclude external hedges entirely | Lemma 5, p. 2213; Theorem 5, p. 2213 | HQ weakly prefers contract $$(\beta, \lvert\psi\rvert, 0)$$ over $$(\beta, 0, \lvert\psi\rvert)$$ when choosing between internal (division B) and external (variable C) hedges; if $$\eta^{HQ} > \tilde{\eta}^{HQ}$$, optimal contracts set $$\psi = 0$$ (no external hedge) |
| R5 | **Synergies reinforce the optimality of equity-based pay**; for any uncertainty level there exists a synergy threshold above which pure equity is optimal | Theorem 7, p. 2215 | For any $$\eta \geq 0$$ there is a threshold $$\bar{\zeta}$$ such that for all $$\zeta > \bar{\zeta}$$, the optimal contract has $$\gamma = \beta$$; at $$\eta = 0$$, pure equity is optimal only when $$\zeta = 1$$ (perfect effort substitutes) |

**Overall (paper's conclusion).** Uncertainty aversion provides a unifying
explanation for three otherwise puzzling compensation practices: the prevalence of
equity-based pay for lower-level managers (even when risk-bearing arguments do not
support it), the rarity of relative-performance contracts especially in high-uncertainty
environments such as young and innovative firms, and the optimism gradient
whereby senior managers hold systematically more favorable beliefs about firm
prospects than rank-and-file employees.

## Theory / model

The paper's model is a one-period, two-division firm. There are two divisions
$$d \in \{A, B\}$$, each run by a division manager supervised by HQ.

**Cash flows and effort.** Each division's cash flow is:

$$
Y_d = \mu_d + \varepsilon_d, \quad \text{where} \quad \mu_d = a_d q_d \tag{p. 2189}
$$

Division cash flows $$(Y_A, Y_B)$$ have a joint normal distribution $$N(\mu, \Sigma)$$
with homoscedastic variance $$\sigma^2$$ and correlation $$\rho$$. Effort $$a_d \in \mathbb{R}_+$$
affects the mean; the cost is $$c_d(a_d) = \tfrac{1}{2\theta_d} a_d^2$$, where $$\theta_d$$
is efficiency of effort. Division managers have CARA utility $$U(w) = -e^{-r w}$$
with coefficient $$r$$; HQ is risk neutral (in the base model).

**Linear incentive contracts.** HQ offers linear contracts. Division manager $$d$$'s
compensation is:

$$
w_d(Y) = s_d + \beta_d Y_d + \gamma_d Y_{d'} \tag{p. 2192}
$$

where $$s_d$$ is a fixed base pay, $$\beta_d$$ is pay-performance sensitivity on own
division output, and $$\gamma_d$$ is cross-division ("cross-pay") exposure. Setting
$$\gamma_d > 0$$ gives an equity component; $$\gamma_d < 0$$ gives relative-performance pay.

**Uncertainty aversion (MEU, Gilboa and Schmeidler (1989)).** Both HQ and division
managers are uncertainty averse: they evaluate payoffs by minimizing expected utility
over a set of admissible priors $$\mathcal{P}$$:

$$
\mathcal{U} = \min_{p \in \mathcal{P}} E_p[U(w)] \tag{eq. 1, p. 2190}
$$

The core beliefs set is defined using the relative entropy (Kullback-Leibler
divergence) of candidate distribution $$\hat{P}(x)$$ relative to reference $$P(x)$$
(Hansen and Sargent (2001)):

$$
R\!\left(\hat{P}(x) \,\middle|\, P(x)\right) \equiv \int \hat{p}(x) \ln\!\left(\frac{\hat{p}(x)}{p(x)}\right) dx \tag{eq. 3, p. 2190}
$$

The admissible set is $$\mathcal{P}(P) \equiv \{\hat{P}: R(\hat{P}(x)|P(x)) \leq \eta^P\}$$,
where $$\eta^P$$ is the uncertainty parameter. A higher $$\eta^P$$ means greater uncertainty
aversion and a larger set of admissible beliefs.

**Parametric approximation.** For tractability (following Dicks and Fulghieri (2019,
2021)), the core beliefs set for agent $$i \in \{HQ, A, B\}$$ is approximated as:

$$
K^i(q) \equiv \left\{\hat{q}^i \,\middle|\, D(\chi^i_A) + D(\chi^i_B) \leq \eta^i\right\}, \quad \chi^i_d = \left|\frac{\hat{q}^i_d - q_d}{q_d}\right|, \quad D(\chi) = -\ln(1-\chi) \tag{eq. 11, p. 2195}
$$

where $$\hat{q}^i_d$$ is agent $$i$$'s belief about division $$d$$'s productivity and $$q_d$$
is the reference productivity. This set is strictly convex with smooth boundaries,
guaranteeing that beliefs respond to changes in compensation contracts.

**Division manager utility.** Given beliefs $$\hat{q}^d$$ and action $$a$$, division
manager $$d$$'s certainty-equivalent utility is:

$$
u_d(\hat{q}^d, a) \equiv E\!\left[w_d|\hat{q}^d, a\right] - \frac{r}{2} Var(w_d) - c_d(a_d) \tag{eq. 5, p. 2192}
$$

where $$Var(w_d) = \sigma^2(\beta_d^2 + 2\rho\beta_d\gamma_d + \gamma_d^2)$$. The key feature
is that the expected wage $$E[w_d|\hat{q}^d, a]$$ depends on division managers'
beliefs about productivity of both divisions (through own-pay $$\beta_d$$ and
cross-pay $$\gamma_d$$), while $$Var(w_d)$$ does not.

## Method

The paper derives analytical solutions to a minimax contracting problem. HQ
maximizes expected profits subject to division managers' incentive constraints
(IC) and participation constraints (PC), while both HQ and managers minimize
over their worst-case beliefs. The problem is:

$$
\max_{\{w_d, a_d\}} \min_{\hat{q}^{HQ} \in K^{HQ}} \pi(\hat{q}^{HQ}) \equiv \sum_{d \in \{A,B\}} E\!\left[Y_d(a_d) - w_d|\hat{q}^{HQ}\right] \tag{eq. 6, p. 2193}
$$

subject to the division managers' IC constraints:

$$
\max_{a_d} \min_{\hat{q}^d \in K^d} u_d(\hat{q}^d, a) \equiv E\!\left[w_d|\hat{q}^d, a_d, a_{d'}\right] - \frac{r}{2}Var(w_d) - c_d(a_d) \tag{eq. 7, p. 2193}
$$

and PC constraints:

$$
\min_{\hat{q}^d \in K^d} u_d(\hat{q}^d, a_d, a_{d'}) \geq u_0 = 0 \tag{eq. 8, p. 2193}
$$

The solution strategy is three-step: (1) characterize how contracts determine
beliefs via Lemma 2; (2) derive equilibrium effort from beliefs via Lemma 3;
(3) characterize optimal contracts by substituting the binding PC into the
objective, yielding the reduced-form HQ payoff (eq. 10, p. 2194):

$$
\pi = \sum_{d \in \{A,B\}} \left\{E(Y_d(a_d)|\hat{q}^{HQ}_d) - \frac{r}{2}Var(w_d) - c_d(a_d) - \left(E[w_d|\hat{q}^d,a] - E[w_d|\hat{q}^{HQ}_d,a]\right)\right\} \tag{eq. 10, p. 2194}
$$

The fourth term is the "uncertainty discount" arising from belief disagreement;
it is novel and central to the paper's results.

**Key analytical result (Theorem 1).** With uncertainty-neutral HQ and
uncertainty-averse risk-neutral division managers, optimal contracts set
$$H_d = 1$$ (uncertainty-hedging ratio equal to one), where
$$H_d \equiv |\gamma_d| a_{d'} q_{d'} / (\beta_d a_d q_d)$$.
Optimal pay-performance sensitivity is:

$$
\beta_d = \frac{1}{1 + 3\!\left(1 - \hat{q}^d_d/q_d\right)} < 1, \quad |\gamma_d| = \xi_d \beta_d \tag{eq. 20, p. 2201}
$$

with $$\xi_d \equiv \frac{a_{d'} q_{d'}}{a_d q_d}$$. Both $$\beta_d$$ and effort $$a_d$$ are
decreasing in uncertainty $$\eta$$. Under symmetry, pure equity is optimal:
$$\beta = \gamma < 1$$.

**Theorem 2** (risk-averse division managers) shows that the optimal contract must
satisfy (eq. 21, p. 2203):

$$
\beta_d a_d q_d + r\sigma^2 \beta_d^2 = |\gamma_d| a_{d'} q_{d'} + r\sigma^2 \gamma_d^2 \tag{eq. 21}
$$

equating the total expected cost to HQ of a division manager's exposure to each
division, regardless of the correlation $$\rho$$. Cross-pay is always non-zero,
$$\gamma_d \neq 0$$, even when divisions are uncorrelated.

**Theorem 3** (uncertainty-averse HQ) yields pure equity at sufficiently high
uncertainty:

$$
\beta_d = \gamma_d = \frac{1}{1 + 3(1 - \hat{q}^d_d/\hat{q}^{HQ}_d)} < 1 \tag{eq. 25, p. 2207}
$$

Relative-performance pay creates a short position for HQ in the other division,
amplifying the beliefs disagreement between HQ (long position) and division
managers (short position), raising the uncertainty discount and making equity
strictly preferred.

The proofs use the envelope theorem applied to the minimax problem, with
closed-form first-order conditions derived under the parametric beliefs
approximation (eq. 11). The proofs of Theorems 1 and 2 appear in the appendix
(pp. 2218-2221); Theorems 3, 4, 5, and 7 proofs are in the supplemental materials.

## Datasets used

This paper is purely theoretical. It introduces no dataset.

| Dataset | Role in paper | Wiki page |
|---|---|---|
| No empirical data used | Theory paper with numerical illustrations only | N/A |

The empirical illustrations use baseline parameter values $$q_A = q_B = 10$$,
$$\theta_A = \theta_B = 2$$, $$\sigma = 10$$, $$r = 1$$ (stated in Section 2 footnotes,
p. 2195 and Figures 1-7).

## When to read the full paper

Use the [original](https://doi.org/10.1093/rfs/hhaf005) if you are:
designing incentive contracts under Knightian uncertainty or ambiguity aversion;
trying to explain equity-based compensation for division managers or rank-and-file
employees; studying why relative-performance pay is rare in practice despite
its theoretical benefits; or extending the model to multitasking, labor-market
equilibrium, or organization design with uncertainty. Theorem 1 (p. 2201) and
Corollary 1 (p. 2203) are the key analytical results; Figure 3 and Figure 6
(pp. 2204, 2210) illustrate optimal contracts under uncorrelated and correlated
cash flows respectively.

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(7), 2025.
This distillation was extracted by an LLM on 2026-06-06 and is **not
human-verified or independently reproduced**. The paper is published under
Oxford University Press standard reuse rights (paywalled). Extract-only.

> Dicks, David L., and Paolo Fulghieri. "Uncertainty, Contracting, and Beliefs
> in Organizations." *The Review of Financial Studies* 38, no. 7 (2025): 2182-2225.
> DOI: 10.1093/rfs/hhaf005.
