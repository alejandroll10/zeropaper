---
title: "Privacy and Team Incentives: Buffa, Liu & White (2025)"
description: >-
  Distilled: When compensation contracts are bilateral and private, principals
  contracting with complementary-effort teams face a commitment problem that
  depresses incentive pay. Delegating contracting authority to the most skilled
  agent (team leader) mitigates the problem via an observability effect, and
  dominates centralized contracting when effort intensity is high enough or
  agents are sufficiently asymmetric. The Journal of Finance 2025, paywalled.
  Seven core results with source locators, no estimation, pure theory with
  a banking-syndicate application.
sidebar:
  label: Buffa-Liu-White 2025
  order: 1
tags: [paper-summary, contract-theory, team-incentives, moral-hazard, organizational-design,
       banking-syndicates, pay-transparency, peer-reviewed, unreplicated]
paper:
  authors: Andrea M. Buffa, Qing Liu, Lucy White
  authorList:
    - { family: Buffa, given: Andrea M., affiliation: University of Colorado Boulder }
    - { family: Liu, given: Qing, orcid: "0000-0001-5286-4423", affiliation: City University of Hong Kong }
    - { family: White, given: Lucy, affiliation: Boston University }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3443-3497
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13496
  jel:
    codes: [D86, M52, G21]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Law, Economics, and Judicial Systems
    - Experimental Behavioral Economics Studies
    - Auction Theory and Applications
  dataAccess: public
  outcome:
    - total compensation budget for a team project
    - allocation of compensation budget across team members
    - principal expected payoff under centralized vs. delegated contracting
  outcomeClass: [labor-careers-health]
  license: >-
    Paywalled (Crossref license: content-version vor,
    URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-10-15; no CC licence found)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley Online Library; Crossref VOR terms confirmed 2026-06-03)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 0

  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, promotion-contest]
  contributionType: [new-theory]
  mechanisms: [moral-hazard, agency, information-asymmetry]

  scope:
    region: theoretical

  relatesTo:
    - { cite: "Holmstrom (1982)", relation: builds-on, note: "benchmark result that public contracts with team moral hazard can achieve first-best; this paper studies the polar-private case (p. 3482)" }
    - { cite: "Segal (1999)", doi: '10.1162/003355399556016', relation: builds-on, note: "analysis of principal's incentive to deviate from efficient trade profile when contract offers are privately observed (p. 3483)" }
    - { cite: "Aghion and Tirole (1997)", doi: '10.1086/262063', relation: builds-on, note: "double-sided moral hazard where delegation encourages agent effort; here efforts are complements and the principal makes no effort contribution (p. 3484)" }
    - { cite: "DeMarzo and Kaniel (2023)", doi: '10.1111/jofi.13260', relation: cites, note: "KUJ-preferences model where private contracts worsen externalities; contrasts with present paper's finding that pay transparency raises levels and reduces inequality unless efforts are very substitutable (p. 3484)" }
    - { cite: "Halac et al. (2021)", doi: '10.1257/aer.20200555', relation: cites, note: "related model where public distribution but private realization of pay packages rules out bad equilibria; principal can commit to bias in that paper (p. 3481)" }
    - { cite: "Cullen and Pakzad-Hurson (2023)", doi: '10.3982/ecta19788', relation: cites, note: "asymmetric-information bargaining where full transparency lowers pay inequality, contrasting with present paper's result when efforts are complementary (p. 3481)" }
    - { cite: "Megginson and Weiss (1991)", doi: '10.1111/j.1540-6261.1991.tb03770.x', relation: cites, note: "underwriter market share as proxy for investment banker reputation, used to operationalize relative skill alpha in the banking-syndicate application (p. 3471)" }
    - { cite: "Carter and Manaster (1990)", doi: '10.1111/j.1540-6261.1990.tb02426.x', relation: cites, note: "tombstone-based reputation ranking for IPO underwriters, second proxy for relative skill alpha (p. 3471)" }

  openQuestions:
    - "The paper takes the privacy of contracts as given and does not endogenize why firms keep contracts private; exploring the equilibrium rationale for contractual privacy (e.g. envy) is identified as future work (p. 3486)."
    - "The trade-offs between transparency and opacity for teams with unequal talent, balancing effort induction against envy costs, are left for future theoretical and experimental investigation (p. 3486)."
    - "The application to production networks (star vs. ring structures, skill, and network formation) is left for future research (p. 3482)."

  proposedVocab:
    - { axis: topic, term: contract-theory, def: "Theoretical analysis of optimal contract design under moral hazard, hidden action, or incomplete contracting.", aliases: [contracting-theory] }
    - { axis: topic, term: team-incentives, def: "Models of incentive provision when multiple agents contribute to a joint output and effort complementarities create cross-agent externalities.", aliases: [team-moral-hazard] }
    - { axis: topic, term: organizational-design, def: "Analysis of how the hierarchical or ownership structure of an organization affects incentives, delegation, and welfare.", aliases: [hierarchy, delegation] }
    - { axis: topic, term: pay-transparency, def: "Policy or institution governing whether compensation contracts are observable by parties other than the direct signatories.", aliases: [wage-transparency, compensation-transparency] }
    - { axis: topic, term: banking-syndicates, def: "Empirical and theoretical analysis of the structure of syndicates that underwrite loans, bonds, or equity issuances, including lead-bank choice and fee concentration.", aliases: [underwriting-syndicates, loan-syndicates] }
    - { axis: topic, term: moral-hazard, def: "Hidden-action problem where an agent's effort is unobservable and the principal designs contracts to provide appropriate incentives.", aliases: [hidden-action] }

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Full text read (pp. 3443-3497 plus Appendix pp. 3486-3494). Seven results
        extracted from the source PDF. Not human-verified. Not reproduced. Pure
        theory paper; no replication code mentioned.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; all
        seven Core results rows confirmed correct (Propositions 1-6 and Figure 7
        equations match PDF eqs. 9, 14, 21, A11, Prop 5, 29/32, and Figure 7
        caption). One equation error fixed: principal payoff written as
        v=(1-b)π^θ corrected to v=(1-b)π (p. 3451). All other equations
        term-by-term verified correct.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: Added classification axes (identification, contributionType, mechanisms, introducesData, data-scope) from a fresh PDF read; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: Classification axes (identification, contributionType, mechanisms, introducesData, data-scope) re-checked against the source PDF; all axes confirmed correct - theory paper, no identification field (correctly omitted), contributionType [new-theory] accurate, mechanisms [moral-hazard, agency, information-asymmetry] all invoked in the model, introducesData correctly absent, scope region:theoretical correct with no data fields.
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the page's already-verified Core-results table and
        relatesTo edges; existing results and sections unchanged. Pure theory
        paper with no empirical estimation: findings[] and resultType both omitted
        per template rules (all Core-results rows are propositions, not estimated
        coefficients or statistics).
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; omission of both fields confirmed correct - all
        seven Core-results rows are analytical propositions (no estimated
        coefficients or statistics), methods.role is theory, and relatesTo edges
        are builds-on/cites only, so neither findings[] nor resultType applies
        per template rules.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13496
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: >-
        license[].content-version=vor,
        URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
        delay-in-days=0, start=2025-10-15. No CC licence block found.

  rightsSignalConflict: false
---

**What this is.** The core propositions and their economic logic from a pure
theory paper on team contracting under private contracts, with an
application to banking syndicates: enough to know what it proves and how,
without reading all 55 pages. To replicate or extend it, read the full
source at [https://doi.org/10.1111/jofi.13496](https://doi.org/10.1111/jofi.13496).

## TL;DR

When compensation contracts are bilateral (observed only by the two parties
who sign them), a principal contracting with two complementary-effort agents
cannot commit to paying her agents enough: any promise of a high bonus to
one agent can be secretly reneged on, and rational agents anticipate this,
so equilibrium effort falls below the second-best (public-contracts)
optimum. The paper shows that delegating contracting to the most skilled
agent (the "Agent") who then sub-contracts with the less skilled agent (the
"Subagent") partially solves this commitment problem via an *observability
effect*: the Agent now observes the Subagent's contract and so is not
afraid of the principal reducing the Subagent's incentives. The cost is a
*self-interest effect*: the Agent skews the budget toward himself. Delegation
dominates centralized private contracting when the project's effort
intensity $$\rho = \theta/\gamma$$ is above a threshold
$$\bar{\rho}(\alpha)$$ that decreases with the skill gap $$\alpha - 1/2$$
between the agents. Applied to banking syndicates, the theory predicts when
sole mandates, fee concentration, and hierarchical structures are optimal.

## Core results

Magnitudes and significance are as reported (pure theory; all results are
propositions or lemmas). Locators point into the source PDF.

| # | Result | Locator | Magnitude / statement |
|---|---|---|---|
| R1 | Under **public contracts** (second best), the optimal compensation budget equals effort intensity and the optimal allocation equals relative skill. | Proposition 1, p. 3453 | $$b^* = \rho,\; \phi^* = \alpha$$ exactly; four structural parameters collapse to two: $$\rho \equiv \theta/\gamma$$ and $$\alpha$$. |
| R2 | Under **centralized private contracts**, the budget is distorted downward and the allocation skewed toward the more skilled agent. | Proposition 2, p. 3456 | $$b^C = \rho - \frac{\alpha(1-\alpha)(2-\rho)\rho^2}{1-\alpha(1-\alpha)\rho^2} < b^*$$; $$\phi^C = \alpha + \frac{(\alpha-1/2)2\alpha(1-\alpha)\rho}{1-2\alpha(1-\alpha)\rho} \geq \alpha = \phi^*$$. Distortions grow with $$\alpha(1-\alpha)$$ (skill heterogeneity) and $$\rho$$. |
| R3 | Under **delegated private contracts** (principal contracts with one Agent, who sub-contracts), the budget distortion is smaller but the allocation distortion may be larger or smaller. | Proposition 3, p. 3460 | $$b^D = \rho - \alpha_A(1-\alpha_A)\rho^2 < b^*$$; $$\phi^D_A = \alpha_A + (1-\alpha_A)(1-\rho)$$. Budget always closer to second best than under centralized: $$b^C < b^D < b^*$$ (Lemma 1). |
| R4 | The principal **prefers to delegate to the more skilled agent**; delegation to the less skilled agent entails a larger allocation distortion that dominates. | Proposition 4, p. 3462 | For any $$\alpha > 1/2$$, $$v^D_{A=1} > v^D_{A=2}$$, where $$v^D_{A=i}$$ is the principal's expected payoff when agent $$i$$ is the Agent. The result follows because $$g(\alpha,\Delta) > 1$$ for all $$\alpha \in (1/2,1)$$ and $$\Delta \in (0,1-\alpha)$$ (Appendix eq. A11, p. 3489). |
| R5 | Delegation **dominates centralized contracting iff effort intensity is high enough**: $$\rho > \bar{\rho}(\alpha)$$; it is also Pareto-improving iff $$\rho > \tilde{\rho}(\alpha)$$, with $$1/2 < \tilde{\rho}(\alpha) < \bar{\rho}(\alpha) < 1/(2\alpha)$$. Both thresholds decrease with $$\alpha$$. | Proposition 5, p. 3468; Figure 4, p. 3469 | Delegation preferred when observability effect (from $$\rho$$ large) overcomes self-interest effect; delegation is Pareto-improving for a wider parameter region than where principal strictly prefers it. |
| R6 | With **partial transparency** (agents observe each other's contracts with probability $$\lambda$$), more transparency raises the compensation budget and reduces the skew toward the more skilled agent under centralized contracting but leaves the allocation unchanged under delegation. Delegation is optimal iff $$\lambda < \bar{\lambda}$$ for a unique threshold $$\bar{\lambda} \in (0,1)$$. | Proposition 6, pp. 3474-3475; Figure 5, p. 3476 | $$b^C(\lambda) = \rho - \frac{(1-\lambda)\alpha(1-\alpha)\rho^2(1-\rho)(2-\rho)}{(1-\rho)(1-\alpha(1-\alpha)\rho^2)+\lambda\alpha(1-\alpha)\rho^2(2-\rho)}$$; $$\phi^D_A(\lambda) = \alpha_A\rho + (1-\rho)$$ (invariant in $$\lambda$$). |
| R7 | When agents' efforts are **more substitutable** (CES probability function with $$\nu > 0$$), the delegation region *expands*: sole mandates are more likely to be awarded as bank efforts become more substitutable. | Section IV.C, Figure 7, p. 3479 | For baseline parameters $$\alpha=0.75, \rho=0.55$$: centralized contracting preferred when $$\nu < 0.35$$; delegation optimal for $$\nu > 0.35$$. |

**Overall (paper's conclusion).** With bilateral private contracts, the
principal faces a credibility problem that distorts team incentives
downward. Delegating contracting to the most skilled team member can
restore efficiency when effort intensity is high. The theory delivers novel,
testable predictions for banking syndicates: sole mandates (delegation) are
more likely for firm-commitment deals, colder markets, less well-known
issuers, larger skill gaps between underwriters, and when private
compensation components are relatively more important.

## Theory / model

The economic environment (Section I, p. 3448) has two dates and three
risk-neutral players with limited liability. A principal hires two agents
to implement a risky project. Agent $$i = 1, 2$$ exerts unobservable effort
$$e_i \geq 0$$. Project output $$X$$ is Bernoulli (p. 3448, eq. 1):

$$
X(e_1, e_2) = \begin{cases} 1 & \text{with prob. } \pi(e_1, e_2) \\ 0 & \text{with prob. } 1 - \pi(e_1, e_2) \end{cases} \tag{1}
$$

The success probability follows a Cobb-Douglas team-effort function (p. 3449, eq. 2):

$$
\pi(e_1, e_2) = \left(e_1^\alpha e_2^{1-\alpha}\right)^\theta \tag{2}
$$

where $$\theta > 0$$ is the elasticity of expected output to team effort
$$e_1^\alpha e_2^{1-\alpha}$$, and $$\alpha \geq 1/2$$ captures the relative
skill of agent 1 (more skilled). The product $$\alpha(1-\alpha)$$ is an
inverse measure of skill heterogeneity. The effort cost is (p. 3449, eq. 3):

$$
c(e_i) = \kappa e_i^\gamma, \quad \kappa, \gamma > 0, \quad \gamma > \theta, \quad \kappa \geq 1 \tag{3}
$$

The principal's payoff (if the project succeeds) net of the total compensation
budget $$b$$ is $$v = (1-b)\pi(e_1,e_2)$$ (p. 3451). Each agent's payoff is
expected compensation minus effort cost: $$u_1 = \phi b (e_1^\alpha e_2^{1-\alpha})^\theta - \kappa e_1^\gamma$$ and $$u_2 = (1-\phi)b(e_1^\alpha e_2^{1-\alpha})^\theta - \kappa e_2^\gamma$$.

The key ratio $$\rho \equiv \theta/\gamma \in (0,1)$$ captures *effort intensity*:
how elastic expected output is to team effort, relative to the cost
elasticity. Proposition 1 shows this is the only determinant of the optimal
second-best compensation budget when contracts are public.

**Two contracting schemes** (Section III, p. 3454; Figure 1, p. 3450):

- *Centralized contracting*: principal offers contracts to both agents
  privately. Each agent observes only his own offer.
- *Delegated contracting*: principal offers a total budget $$b$$ to the Agent
  (the more skilled agent), who then sub-contracts with the Subagent. The
  Agent observes both contracts; the Subagent observes only his own offer.

**Commitment problem.** With public contracts, Proposition 1 establishes the
second-best optimum $$(b^*, \phi^*) = (\rho, \alpha)$$ as the benchmark. When
contracts are private, the principal can secretly renege on the promised
high-incentive contract for one agent: agent $$i$$ cannot observe agent $$j$$'s
contract, so he cannot verify whether the indirect effort externality he
expects is actually being provided. This destroys the indirect-incentive
channel and depresses the equilibrium budget (Proposition 2, p. 3456).

## Method

The paper's method is theoretical (pure theory, no estimation). Equilibria
are solved by backward induction in a two-period game, using the
**Perfect Bayesian Equilibrium (PBE)** with *passive beliefs* (agents do not
revise beliefs about the other agent's effort when receiving an out-of-equilibrium
offer, p. 3455). The solution procedure is:

1. Given the compensation budget $$b$$ and allocation $$\phi$$, solve each agent's
   incentive-compatibility (IC) constraint for optimal effort (equations 4-5
   in the public case, 10-12 in the centralized private case, 15-18 in the
   delegated case).
2. Impose equilibrium: each agent's conjecture about the other's effort equals
   the equilibrium effort level.
3. Solve the principal's program for $$(b^*, \phi^*)$$ (or the Agent's
   allocation program for $$\phi_A^D$$ in the delegated case).

The paper builds on `principal-agent` and `promotion-contest` frameworks.
The key technical contribution is formalizing the *observability effect* vs.
the *self-interest effect* of delegation, both deriving from the same
bilateral-privacy assumption.

For the banking-syndicate application, the model is extended to **partial
transparency** via a mixing parameter $$\lambda \in [0,1]$$ (Proposition 6,
p. 3474): agents observe each other's contracts with probability $$\lambda$$.
The fully private and fully public cases are nested at $$\lambda = 0$$ and
$$\lambda = 1$$ respectively. A **CES probability function** (eq. 33, p. 3478)
$$\pi(e_1,e_2) = (\alpha e_1^\nu + (1-\alpha)e_2^\nu)^\theta$$ with
substitutability parameter $$\nu$$ nests the Cobb-Douglas as $$\nu \to 0^+$$.

## Empirical specifications

This is a pure theory paper; there is no econometric estimation. The
paper's empirical content is a set of *qualitative comparative-statics
predictions* for banking syndicates (Section IV, pp. 3470-3482), which
can be taken to data. The key mappings from model to data are:

- **Degree of centralization / delegation**: fraction of banks in the top tier
  of a syndicate hierarchy. More banks in the top tier = more centralized
  (the issuer deals directly with each rather than routing through a lead bank).
  A more concentrated distribution of underwriting fees (high HHI among top-tier
  banks) is an alternative delegation measure (p. 3471).
- **Relative skill** $$\alpha$$: proxied by standard underwriter reputation
  measures: Megginson and Weiss (1991) market-share rank; Carter and Manaster
  (1990) tombstone-based rank.
- **Effort intensity** $$\rho$$: harder-to-sell deals have higher $$\rho$$.
  Proxies include: firm-commitment vs. best-efforts underwriting; market
  "coldness" (volume of deals in the quarter); issuer credit quality / cash flows;
  issuer name recognition (p. 3472).
- **Degree of transparency** $$\lambda$$: higher when publicly-disclosed fees
  or spreads dominate compensation; lower when side benefits (e.g., future
  business from the issuer, allocation of underpriced shares) are a large
  share of total compensation (p. 3475).

**Testable predictions** from Propositions 5-6 and the CES extension:

1. Sole mandates (delegation) are more likely when the issue is firm-commitment,
   in colder markets, from less well-known issuers, and for lower-rated debt.
2. Fee income is more concentrated among a few top-tier banks when
   (a) underwriters' skill is more asymmetric, (b) the deal is harder to place,
   and (c) private compensation components are relatively more important.
3. More pay transparency (higher $$\lambda$$) increases total underwriting
   spreads and reduces the share of the highest-reputation bank(s) under
   centralized (joint-mandate) structures.
4. Sole mandates become *more* likely as bank effort substitutability increases
   (CES result, Figure 7, p. 3479).

## Datasets used

This is a theoretical paper. No dataset is used for estimation. The
application to banking syndicates references the following empirical
literature for operationalizing model parameters:

| Reference / proxy | Role in paper | Wiki page |
|---|---|---|
| Megginson and Weiss (1991) underwriter reputation (market-share rank) | Proxy for relative skill $$\alpha$$ in syndicate application | No page yet |
| Carter and Manaster (1990) tombstone rank | Alternative proxy for relative skill $$\alpha$$ | No page yet |
| Syndicate structure data (fraction of banks in top tier; HHI of fees) | Observable proxy for degree of delegation | No page yet |

No quantitative empirical exercise is conducted in the paper itself.

## Relation to prior work

The paper builds on several strands of the literature. Holmstrom (1982)
establishes that public contracts with team moral hazard can in principle
achieve first-best outcomes, which this paper uses as a conceptual
benchmark (p. 3482). Segal (1999) analyzes the principal's incentive to
deviate from an efficient trade profile when contract offers are privately
observed, and characterizes the optimal mechanism when agents' messages to
the principal can be made contingent on other agents' messages; this paper
complements that analysis by showing delegation can solve the commitment
problem (p. 3483). Aghion and Tirole (1997) study a double-sided moral
hazard problem where delegation encourages a single agent's effort; the
key difference here is that two agents' efforts are complements and the
principal makes no direct effort contribution, so delegation operates
through a different channel (p. 3484).

On pay transparency, Halac et al. (2021) analyze a model where the
principal can commit to the public distribution but keeps the realization
of pay packages private, ruling out bad equilibria; their model differs
in that the principal can commit to non-discriminatory pay, which she
cannot in the present paper (p. 3481). Cullen and Pakzad-Hurson (2023)
show that full pay transparency lowers pay inequality by reducing the
principal's bargaining power; this contrasts with the present paper's
finding that transparency raises pay levels and reduces inequality only
when efforts are highly substitutable (p. 3481). DeMarzo and Kaniel
(2023) build a model where agents have "keeping up with the Joneses"
(KUJ) preferences and private contracts worsen externalities; in
equilibrium agents' KUJ preferences result in less negative optimal
compensation on peer output, providing a rationale for "payment for luck"
(p. 3484).

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13496) if you are:
building a model of team contracting with private contracts; interested in
the formal proofs of the propositions (Appendix pp. 3486-3494 and Internet
Appendix); extending the theory to endogenous privacy, dynamic contracts, or
more than two agents; or calibrating the banking-syndicate predictions to
data (the comparative-statics section, IV.B, pp. 3475-3480 maps model
parameters to observables). The Internet Appendix derives CES equilibria in
full generality and provides robustness under non-passive beliefs.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025, pp.
3443-3497. DOI: 10.1111/jofi.13496. Copyright 2025 the American Finance
Association. This article is paywalled; no CC licence was found in Crossref
metadata. This distillation is **extract-only** under fair-use principles:
core results and equations reproduced for research commentary purposes.
Distilled by an LLM (claude-sonnet-4-6) on 2026-06-03. **Not
human-verified. Not independently reproduced.**

> Buffa, Andrea M., Qing Liu, and Lucy White. "Privacy and Team Incentives."
> *The Journal of Finance* 80, no. 6 (December 2025): 3443-3497.
> DOI: 10.1111/jofi.13496. Copyright 2025 the American Finance Association.
