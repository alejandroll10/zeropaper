---
title: "Bail-Ins, Optimal Regulation, and Crisis Resolution: Clayton & Schaab (2025)"
description: >-
  Distilled: In a tractable three-period dynamic contracting model with fire-sale
  externalities, the privately optimal bank contract combines short-term standard
  debt and long-term bail-in debt; the social optimum calls for joint regulation
  of both the level and composition of debt, rationalizing a leverage cap plus a
  TLAC requirement that can be satisfied with bail-in debt. Bail-ins replace
  bailouts as a recapitalization tool even without planner commitment. Review of
  Financial Studies 2025, paywalled. Five core results with source locators, the
  model, and its key propositions with equations.
sidebar:
  label: Clayton-Schaab 2025
  order: 1
tags: [paper-summary, banking, financial-regulation, capital-structure, bail-ins,
       bank-resolution, optimal-contracting, peer-reviewed, unreplicated]
paper:
  authors: Christopher Clayton, Andreas Schaab
  authorList:
    - { family: Clayton, given: Christopher, orcid: "0000-0002-0900-0686", affiliation: Yale School of Management and NBER }
    - { family: Schaab, given: Andreas, affiliation: "UC Berkeley" }
  year: 2025
  venue: The Review of Financial Studies 38(9), 2025, 2810-2843
  venueShort: Rev. Financ. Stud. 2025
  doi: 10.1093/rfs/hhaf002
  jel:
    codes: [G28, G33]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Insurance and Financial Risk Management"]
  dataAccess: public
  outcome:
    - optimal bank liability structure (standard debt vs. bail-in debt)
    - socially optimal composition and level of bank debt
    - welfare effect of bail-in regulation vs. bailouts
  outcomeClass: [firm-financing, credit-risk]
  license: "Oxford standard publication reuse rights (all rights reserved, paywalled; content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights, start 2025-03-18, delay-in-days 0)"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Oxford Academic site, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 5
  citedByCount: 2
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, mechanism-design]
  contributionType: [new-theory]
  mechanisms: [moral-hazard, fire-sale-externality, agency]
  scope:
    region: theoretical
    assetClass: bank debt (standard debt and bail-in debt)
  relatesTo:
    - { cite: "Innes (1990)", doi: '10.1016/0022-0531(90)90066-s', relation: builds-on, note: "three-period incentive model of bank lending with unobservable effort is a repeated version of Innes (1990)" }
    - { cite: "Holmstrom and Tirole (1997)", doi: '10.1162/003355397555316', relation: builds-on, note: "pledgeability constraint approach from Holmstrom and Tirole (1997) reduces date 1 binary effort problem" }
    - { cite: "Keister and Mitkov (2023)", doi: '10.1016/j.jet.2023.105672', relation: cites, note: "banks may not write down deposit creditors if anticipating government bailouts, motivating mandatory bail-ins" }
    - { cite: "Chari and Kehoe (2016)", doi: '10.1257/aer.20150157', relation: cites, note: "costly state verification showing standard debt is renegotiation-proof; bail-ins reduce level of standard debt" }
    - { cite: "Walther and White (2020)", doi: '10.1093/rfs/hhaa032', relation: cites, note: "precautionary bail-ins can signal adverse information and cause bank runs, motivating public-information bail-in rules" }
    - { cite: "Bolton and Oehmke (2019)", doi: '10.1093/rfs/hhy123', relation: cites, note: "bank resolution and structure of global banks; demand-based explanation for standard debt" }
    - { cite: "Farhi and Tirole (2012)", doi: '10.1257/aer.102.1.60', relation: cites, note: "collective moral hazard and systemic bailouts; bailout commitment benchmark" }
    - { cite: "Dewatripont and Tirole (1994)", relation: cites, note: "theory of debt and equity as foundational contracting framework" }
    - { cite: "Davila and Korinek (2018)", doi: '10.1093/restud/rdx010', relation: cites, note: "pecuniary externalities make fire sales Pareto inefficient, motivating macroprudential policy" }
  openQuestions:
    - "Extension to longer-horizon models in which liquidations would still be costly but strong incentive devices while bail-ins would be weaker incentive devices; policy implications of pledging contracts that induce future shirking after low returns (p. 2840)."
    - "Extension to severable banker: if the banker can be fired without liquidating the bank, governments might prefer costly firings and bail-ins as high-powered incentive devices rather than liquidations (p. 2841)."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Read PDF in full (pp. 2810-2843 + conclusion + references); all propositions, equations, and locators drawn directly from the PDF. Not human-verified; not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all five core-result locators, all model equations (1, 2, 6, 9, 12, 16, 18, 20, 21, 26, 27, 29), and Propositions 1-5 confirmed correct. Fixed: removed JEL code G21 (not listed in PDF abstract; PDF states only G28 and G33)." }
  licenceVerification:
    - { source: "Crossref works/10.1093/rfs/hhaf002", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[]: content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights, start 2025-03-18, delay-in-days 0. Oxford standard reuse rights; not CC; paywalled." }
---

**What this is.** This is a distilled skeleton of the paper for search and navigation. Read the
[original at Oxford Academic](https://doi.org/10.1093/rfs/hhaf002) to replicate or extend.

## TL;DR

Clayton and Schaab build a tractable three-period dynamic contracting model of bank liability
structure in the tradition of Innes (1990). Banks face an initial and a continuation monitoring
incentive problem. In the presence of fire sales from liquidations, the privately optimal contract
combines short-term standard debt (which forces liquidation in bad states and provides strong
incentives) and long-term bail-in debt (which avoids resource costs of liquidation by writing
down to pledgeable income). A social planner that internalizes the fire-sale externality
intervenes in both the level and the composition of debt: it prefers less standard debt (a
leverage cap / maximum leverage requirement) and less total debt (a TLAC requirement satisfiable
with bail-in debt). The model shows that bail-ins replace bailouts as a recapitalization tool
and that statutory provisions increasing the cost of bailouts improve welfare, providing a unified
rationalization of postcrisis regulation. The framework connects to demand-based explanations of
standard debt (Bolton and Oehmke (2019); Walther and White (2020)) and extends the macroprudential
literature on pecuniary externalities from Davila and Korinek (2018) to the bank contracting
setting.

## Core results

| # | Result | Locator | Magnitude as reported |
|---|---|---|---|
| R1 | Privately optimal contract uses both standard and bail-in debt | Proposition 1, Corollary 1, pp. 2822-2825 | Liability structure has three regions: liquidation ($$R_1 \le R_\ell^p$$), bail-in write-down ($$R_\ell^p < R_1 \le R_u^p$$), and no write-down ($$R_1 > R_u^p$$); implemented with short-term standard debt face value $$(1-b)R_\ell^p Y_0$$ and long-term bail-in debt face value $$(1-b)(R_u^p - R_\ell^p)Y_0$$ |
| R2 | Social optimum has same structure as private optimum but with additional wedges on standard and total debt | Proposition 3, Equations (24)-(28), pp. 2827-2829 | Socially optimal thresholds $$R_\ell^s \le R_\ell^p$$ and $$R_u^s \le R_u^p$$: planner uses less standard debt and less total debt than private banks; wedges $$\tau_\ell^s \ge 0$$ and $$\tau_u^s \ge 0$$ reflect social cost of liquidations $$\lambda^s \sigma \gamma^s$$ |
| R3 | All three model ingredients (initial incentive problem, continuation incentive problem, costly liquidation) are needed for bail-in debt to be part of the optimal contract | Proposition 2, p. 2826 | If $$B_0(e_0) = 0$$: bail-in debt alone suffices. If $$B_1 = 0$$: long-term debt alone suffices. If $$\gamma = 1$$: standard debt alone suffices. All three ingredients are needed for the combined structure |
| R4 | With planner commitment over bailouts, bail-ins dominate bailouts: the socially optimal contract with no bailouts is Pareto efficient | Proposition 4, p. 2832 | No bailouts ($$T_0 = T_1 = 0$$) is Pareto efficient; bailouts are redundant recapitalization when bail-ins are available; both instruments can achieve same state contingencies in bank debt contracts |
| R5 | Without planner commitment, Pareto-efficient debt levels still eliminate bailouts entirely; welfare is increasing in the cost of bailouts F | Proposition 5, p. 2834 | For any $$F \ge 0$$, Pareto-efficient debt levels $$(R_\ell^s, R_u^s)$$ result in no banks being bailed out; welfare is strictly increasing in F because higher F relaxes the no-bailout constraint (Equation 29) |

**Overall (paper's conclusion).** The paper provides a single contracting framework that
rationalizes both a maximum leverage requirement and a TLAC requirement as jointly optimal
responses to fire sale externalities. Bail-in debt is the instrument of choice because it
combines the incentive properties of equity with the cash-flow transfer properties of standard
debt, making it superior to outside equity as a loss-absorbing instrument. Bail-ins replace
bailouts in the regulatory toolkit; statutory provisions that increase the cost of engaging
in bailouts complement bail-in regulation by allowing looser regulatory constraints while
still preventing bailouts in equilibrium.

## Theory / model

The model has three periods ($$t = 0, 1, 2$$), a unit continuum of banks, penniless investors,
and arbitrageurs. Banks invest in a firm of variable scale $$Y_0 = A_0 + I_0 > 0$$ using their
own equity $$A_0 > 0$$ and investor funds $$I_0 \ge 0$$ (p. 2815).

**Project quality shocks.** At each of dates 1 and 2, the bank experiences a stochastic
quality shock $$R_t \in [\underline{R}, \overline{R}]$$ that adjusts project scale to
$$Y_t = R_t Y_{t-1}$$, so final scale is $$Y_2 = R_1 R_2 Y_0$$. The project pays one unit
of the consumption good per unit of final scale at date 2 but yields no dividend on date 1.
Shocks $$R_t$$ are independent and idiosyncratic with densities (p. 2815):

$$f_t(R_t | e_{t-1}) = e_{t-1} f_{tH}(R_t) + (1 - e_{t-1}) f_{tL}(R_t).$$

**Effort and MLRP.** Date 0 effort is continuous, $$e_0 \in [0,1]$$; date 1 effort is binary,
$$e_1 \in \{0,1\}$$. Higher effort increases the quality of the return distribution.
The paper assumes the monotone likelihood ratio property (MLRP): the likelihood ratio
$$\Lambda_t(R_t) \equiv f_{tH}(R_t) / f_{tL}(R_t)$$ is increasing in $$R_t$$.

**Private benefits.** The banker's date 0 private benefit is $$B_0(e_0) Y_0$$, where
$$B_0$$ is decreasing and concave with $$B_0(1) = 0$$. The banker's date 1 private
benefit is $$(1 - e_1) B_1 Y_1$$ for $$0 < B_1 < 1$$ (p. 2816).

**Resource constraints.** Along a history $$(R_1, R_2)$$, investor repayment $$x_1(R_1)$$,
$$x_2(R_1, R_2)$$ and bank consumption $$c_1(R_1)$$, $$c_2(R_1, R_2)$$ satisfy (p. 2817):

$$c_1(R_1) + x_1(R_1) = \alpha(R_1) \gamma R_1 Y_0, \tag{1}$$

$$c_2(R_1, R_2) + x_2(R_1, R_2) = (1 - \alpha(R_1)) R_1 R_2 Y_0. \tag{2}$$

Limited liability requires $$c_1(R_1), c_2(R_1, R_2) \ge 0$$.

**Investor participation constraint.** Investors must at least break even (p. 2818):

$$Y_0 - A_0 \le \mathbb{E}\bigl[x(R_1) \mid e_0 = e_0^*\bigr]. \tag{6}$$

**Fire sale and liquidation price.** A representative arbitrageur with borrowing constraints
generates a fire sale externality. The equilibrium liquidation price $$\gamma$$ satisfies the
market-clearing condition (pp. 2820-2821):

$$\gamma(\Omega) = \frac{\partial \mathcal{F}(\Omega)}{\partial \Omega}, \quad \Omega = \int_{\underline{R}}^{\overline{R}} \alpha(R_1) R_1 f_1(R_1 | e_0^*) \, dR_1. \tag{16}$$

When $$\partial^2 \mathcal{F} / \partial \Omega^2 < 0$$, more liquidations reduce the price,
creating the fire sale. The liquidation price elasticity is
$$\sigma = -(\Omega / \gamma)(\partial \gamma / \partial \Omega)$$.

**Date 1 incentive compatibility.** High effort $$e_1^*(R_1) = 1$$ is incentive compatible
if (p. 2818):

$$\mathbb{E}[c_2(R_1, R_2)(\Lambda_2(R_2) - 1) \mid e_1 = 0] \ge B_1 R_1 Y_0. \tag{9}$$

**Date 0 optimal effort.** The bank's optimal date 0 effort $$e_0^*$$ satisfies (p. 2819):

$$-B_0'(e_0^*) Y_0 = \mathbb{E}_0[c(R_1)(\Lambda_1(R_1) - 1) \mid e_0 = 0]. \tag{12}$$

## Method

This is a pure theory paper. The model is solved by characterizing the set of feasible contracts
(satisfying limited liability, resource constraints, investor participation, repayment monotonicity,
and incentive compatibility at both dates), then finding the contract that maximizes bank expected
utility subject to those constraints.

**Pledgeability reduction (Lemma 1, p. 2822).** The binary date 1 effort problem reduces to
a Holmstrom and Tirole (1997) style pledgeability constraint. The optimal contract sets
$$x_1(R_1) = 0$$ and repays investors on date 2 at a threshold $$R_2^u(R_1)$$. Bank
high effort on date 1 is incentive compatible if and only if $$c(R_1) \ge b R_1 Y_0$$,
where $$b = \int_{\overline{R}_2^u}^{\overline{R}} [R_2 - \overline{R}_2^u] f_{2H}(R_2) dR_2$$
is a constant (p. 2822, Equation 18).

**Mapping to promised liabilities.** The paper maps actual-repayment contracts to promised
"face value" liabilities $$L(R_1)$$: if $$L(R_1) \le (1-b)R_1 Y_0$$ the bank avoids
liquidation; if $$L(R_1) > (1-b)R_1 Y_0$$ the bank is liquidated with actual repayment
$$\gamma R_1 Y_0$$ (p. 2822).

**First-order conditions for the private optimum (Proposition 1, pp. 2822-2823).** The
privately optimal liquidation threshold $$R_\ell^p$$ and total debt threshold $$R_u^p$$
satisfy:

$$\underbrace{\frac{1 - \Lambda_1(R_\ell^p)}{(1 - e_0^*) + e_0^* \Lambda_1(R_\ell^p)} \frac{1}{|B_0''(e_0^*)|}}_{\text{Incentive Provision}} b \lambda G = \underbrace{b + \lambda(1 - b - \gamma)}_{\text{Liquidation Costs}}, \tag{20}$$

$$\underbrace{\frac{F_{1L}(R_u^p) - F_{1H}(R_u^p)}{|B_0''(e_0^*)|}}_{\text{Incentive Provision}} \lambda G = \underbrace{(\lambda - 1)(1 - F_1(R_u^p | e_0^*))}_{\text{Investor Repayment}}, \tag{21}$$

where $$\lambda > 1$$ is the Lagrange multiplier on the investor participation constraint and
$$G = \int_{\underline{R}}^{R_\ell^p} \gamma R_1 (f_{1H}(R_1) - f_{1L}(R_1)) dR_1 + \int_{R_\ell^p}^{\overline{R}} (1-b) \min\{R_1, R_u^p\} (f_{1H}(R_1) - f_{1L}(R_1)) dR_1$$.

**Social planner's first-order conditions (Proposition 3, pp. 2827-2828).** The planner's
optimum satisfies the same structural equations as the private optimum but with wedge terms
$$+\tau_\ell^s$$ and $$-\tau_u^s$$ on the right-hand sides of Equations (24) and (25):

$$\tau_\ell^s = \left(1 - \frac{1 - \Lambda_1(R_\ell^s)}{(1 - e_0^s) + e_0^s \Lambda_1(R_\ell^s)} \frac{1}{|B_0''(e_0^s)|} b L^s\right) \lambda^s \sigma \gamma^s \ge 0, \tag{26}$$

$$\tau_u^s = \frac{F_{1L}(R_u^s) - F_{1H}(R_u^s)}{|B_0''(e_0^s)|} L^s \sigma \gamma^s \ge 0, \tag{27}$$

where $$\sigma$$ is the liquidation price elasticity and $$\gamma^s$$ is the equilibrium
liquidation price. The wedge $$\tau_\ell^s$$ reflects the social cost of additional
liquidations induced by standard debt; $$\tau_u^s$$ reflects the social cost of more
total debt through the indirect effort channel.

**No-bailout constraint (Proposition 5, p. 2833).** In the case without planner commitment,
the planner does not bail out banks if the total losses from liquidations are high enough:

$$(1 - \gamma(\Omega)) \Omega Y_0 \le F. \tag{29}$$

## Empirical specifications

This is a pure theory paper with no empirical component. There are no regressions,
no estimation equations, and no data. The paper characterizes optimal contracts and regulatory
instruments analytically. The special case of linear private benefits ($$B_0(e_0) = b_0(1-e_0)$$)
is worked out in Internet Appendix B.3 as a closed-form tractable illustration.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| None | Pure theory paper; no data used | N/A |

## When to read the full paper

Read Clayton and Schaab (2025) if you are designing or evaluating:

- Optimal bank capital structure rules combining leverage caps and TLAC requirements
- The comparison between bail-in debt and outside equity as loss-absorbing instruments (Proposition 2 and Section 2.2.1), extending Dewatripont and Tirole (1994)
- The rationale for statutory provisions that increase the cost of bailouts, such as Dodd-Frank Act restrictions (Section 4.2); connects to Farhi and Tirole (2012) and Chari and Kehoe (2016)
- The good bank / bad bank approach to resolving large banks with partial liquidations (Section 5.2)
- The connection between the incentive-based explanation and the result of Keister and Mitkov (2023) that anticipated bailouts suppress bail-in debt issuance
- The connection between the incentive-based and demand-based (safety premium) explanations for the coexistence of standard and bail-in debt (Section 5.3)

## Attribution and rights

Clayton, C., and A. Schaab. 2025. "Bail-Ins, Optimal Regulation, and Crisis Resolution."
*The Review of Financial Studies* 38(9): 2810-2843. https://doi.org/10.1093/rfs/hhaf002.

Published by Oxford University Press on behalf of The Society for Financial Studies. All rights
reserved. For commercial re-use contact reprints@oup.com. This page is an LLM-distilled
summary (extract-only); it is not human-verified and has not been reproduced. Read the original
at the DOI above.
