# Private Contracts and Delegated Team Incentives

## One-sentence contribution

When a principal compensates two complementary-effort agents through bilateral private contracts, she cannot commit to high incentive pay; delegating contracting authority to the more skilled agent partially restores commitment through an observability effect and dominates centralized private contracting once effort intensity is high enough.

## Setup

### Environment

There are two dates and three risk-neutral players with limited liability. A principal hires two agents to implement a single risky project. Agent $i = 1, 2$ exerts unobservable effort $e_i \geq 0$. Project output $X$ is Bernoulli (eq. 1):

$$
X(e_1, e_2) = \begin{cases} 1 & \text{with prob. } \pi(e_1, e_2) \\ 0 & \text{with prob. } 1 - \pi(e_1, e_2) \end{cases} \tag{1}
$$

The success probability is a Cobb-Douglas team-effort function (eq. 2):

$$
\pi(e_1, e_2) = \left(e_1^\alpha e_2^{1-\alpha}\right)^\theta \tag{2}
$$

where $\theta > 0$ is the elasticity of expected output to the team-effort aggregate $e_1^\alpha e_2^{1-\alpha}$, and $\alpha \geq 1/2$ is the relative skill of agent 1 (the more skilled agent). The product $\alpha(1-\alpha)$ is an inverse measure of skill heterogeneity. The effort cost is (eq. 3):

$$
c(e_i) = \kappa e_i^\gamma, \quad \kappa, \gamma > 0, \quad \gamma > \theta, \quad \kappa \geq 1 \tag{3}
$$

The principal's payoff, net of the total compensation budget $b$, is $v = (1-b)\pi(e_1,e_2)$. Each agent's payoff is expected compensation minus effort cost: $u_1 = \phi b\,(e_1^\alpha e_2^{1-\alpha})^\theta - \kappa e_1^\gamma$ and $u_2 = (1-\phi)b\,(e_1^\alpha e_2^{1-\alpha})^\theta - \kappa e_2^\gamma$, where $\phi$ is agent 1's share of the budget.

The key ratio $\rho \equiv \theta/\gamma \in (0,1)$ is *effort intensity*: the elasticity of expected output to team effort relative to the cost elasticity. Two contracting schemes are compared:

- *Centralized contracting*: the principal offers contracts to both agents privately; each agent observes only his own offer.
- *Delegated contracting*: the principal offers a total budget $b$ to the more skilled agent (the "Agent"), who sub-contracts with the less skilled agent (the "Subagent"). The Agent observes both contracts; the Subagent observes only his own offer.

Contracts are bilateral and private (observed only by their two signatories) unless otherwise stated. Section I.B nests partial transparency: agents observe each other's contracts with probability $\lambda \in [0,1]$, with the fully private and fully public cases at $\lambda = 0$ and $\lambda = 1$.

## Analysis

### Key result

**Proposition 1 (public-contract benchmark).** Under public (second-best) contracts the optimal budget equals effort intensity and the optimal allocation equals relative skill:
$$ b^* = \rho, \qquad \phi^* = \alpha. $$
The four structural parameters collapse to two, $\rho$ and $\alpha$.

**Proposition 2 (centralized private contracts).** Under private centralized contracts the budget is distorted downward and the allocation is skewed toward the more skilled agent:
$$ b^C = \rho - \frac{\alpha(1-\alpha)(2-\rho)\rho^2}{1-\alpha(1-\alpha)\rho^2} < b^*, $$
$$ \phi^C = \alpha + \frac{(\alpha-1/2)\,2\alpha(1-\alpha)\rho}{1-2\alpha(1-\alpha)\rho} \geq \alpha = \phi^*. $$
Both distortions grow with $\alpha(1-\alpha)$ (skill heterogeneity) and with $\rho$.

**Proposition 3 (delegated private contracts).** Under delegation the budget distortion is smaller and the budget is always closer to second best than under centralized contracting (Lemma 1, $b^C < b^D < b^*$):
$$ b^D = \rho - \alpha_A(1-\alpha_A)\rho^2 < b^*, \qquad \phi^D_A = \alpha_A + (1-\alpha_A)(1-\rho), $$
where $\alpha_A$ is the relative skill of the delegated Agent.

**Proposition 4 (whom to delegate to).** For any $\alpha > 1/2$ the principal prefers to delegate to the more skilled agent: $v^D_{A=1} > v^D_{A=2}$. The result follows because an auxiliary function $g(\alpha,\Delta) > 1$ for all $\alpha \in (1/2,1)$ and $\Delta \in (0, 1-\alpha)$ (Appendix eq. A11).

**Proposition 5 (delegation vs. centralization).** Delegation dominates centralized contracting iff effort intensity is high enough, $\rho > \bar{\rho}(\alpha)$, and is Pareto-improving iff $\rho > \tilde{\rho}(\alpha)$, with
$$ 1/2 < \tilde{\rho}(\alpha) < \bar{\rho}(\alpha) < 1/(2\alpha). $$
Both thresholds decrease in $\alpha$.

**Proposition 6 (partial transparency).** Under centralized contracting, more transparency (higher $\lambda$) raises the budget and reduces the skew toward the more skilled agent; under delegation the allocation is invariant in $\lambda$:
$$ b^C(\lambda) = \rho - \frac{(1-\lambda)\alpha(1-\alpha)\rho^2(1-\rho)(2-\rho)}{(1-\rho)\bigl(1-\alpha(1-\alpha)\rho^2\bigr)+\lambda\alpha(1-\alpha)\rho^2(2-\rho)}, $$
$$ \phi^D_A(\lambda) = \alpha_A\rho + (1-\rho) \ \text{(invariant in } \lambda). $$
Delegation is optimal iff $\lambda < \bar{\lambda}$ for a unique $\bar{\lambda} \in (0,1)$.

### Proof

The equilibria are solved by backward induction in a two-period game using Perfect Bayesian Equilibrium with passive beliefs (an agent does not revise his belief about the other's effort upon receiving an out-of-equilibrium offer). The procedure: (i) given $(b,\phi)$, solve each agent's incentive-compatibility constraint for optimal effort (eqs. 4–5 in the public case, 10–12 in the centralized private case, 15–18 in the delegated case); (ii) impose equilibrium so each agent's conjecture about the other's effort equals the equilibrium effort; (iii) solve the principal's program for $(b^*,\phi^*)$, or the Agent's allocation program for $\phi^D_A$ in the delegated case.

Proposition 1 follows from the public-contract program: the team-effort aggregate makes $\rho$ the sole determinant of the optimal budget and $\alpha$ the optimal share. Proposition 2 follows because, with private contracts, agent $i$ cannot observe agent $j$'s contract and so cannot verify the indirect effort externality he expects; the principal can secretly renege on a promised high-incentive contract, which destroys the indirect-incentive channel and depresses the equilibrium budget. Proposition 3 follows because, under delegation, the Agent observes the Subagent's contract and therefore does not fear a reduction in the Subagent's incentives (the observability effect), shrinking the budget distortion; the Agent, however, skews the allocation toward himself (the self-interest effect). Proposition 4 compares the two principal payoffs and reduces to the inequality $g(\alpha,\Delta) > 1$ (Appendix eq. A11). Proposition 5 compares the principal's payoff under delegation and centralization and shows the observability effect overtakes the self-interest effect above the thresholds $\bar\rho(\alpha)$ and $\tilde\rho(\alpha)$. Proposition 6 substitutes the mixing parameter $\lambda$ into the centralized and delegated programs (the CES extension's equations 29/32 generalize this) and signs the comparative statics. The full proofs are in the Appendix and Internet Appendix.

### Economic mechanism

With bilateral private contracts the principal faces a commitment problem: because each agent observes only his own contract, a promise of high incentive pay to one agent can be secretly reneged on, and rational agents anticipate this, so equilibrium effort and the equilibrium budget fall below the second-best optimum. Delegating contracting to the more skilled agent introduces an *observability effect* — the Agent now observes the Subagent's contract and so no longer fears that the principal will quietly cut the Subagent's incentives — which raises the budget toward second best. The offsetting *self-interest effect* is that the Agent allocates the budget partly toward himself. When effort intensity $\rho$ is high, the observability effect dominates the self-interest effect, so delegation is preferred; the dominance threshold falls as the skill gap $\alpha - 1/2$ widens.

## Comparative statics

- Centralized budget distortion $b^* - b^C$ and allocation skew $\phi^C - \phi^*$ both increase in skill heterogeneity $\alpha(1-\alpha)$ and in effort intensity $\rho$.
- The budget ordering $b^C < b^D < b^*$ holds always (Lemma 1): delegation is always closer to second best on the budget margin.
- The principal strictly prefers delegation iff $\rho > \bar\rho(\alpha)$; delegation is Pareto-improving over a wider region, iff $\rho > \tilde\rho(\alpha)$, with $\tilde\rho < \bar\rho$. Both thresholds decrease in $\alpha$.
- Under centralized contracting, raising transparency $\lambda$ raises the budget $b^C(\lambda)$ and reduces the skew toward the more skilled agent; under delegation the allocation $\phi^D_A(\lambda)$ is invariant in $\lambda$. Delegation is optimal iff $\lambda < \bar\lambda$.
- With more substitutable efforts (CES probability function, substitutability $\nu > 0$, nesting Cobb-Douglas as $\nu \to 0^+$), the delegation region expands. For $\alpha = 0.75, \rho = 0.55$: centralized contracting is preferred for $\nu < 0.35$ and delegation is optimal for $\nu > 0.35$.

## Connection to literature

- **Holmstrom (1982)** — establishes that public contracts with team moral hazard can in principle achieve first best; used here as the conceptual benchmark against which the polar private-contract case is studied.
- **Segal (1999)** — analyzes the principal's incentive to deviate from an efficient trade profile when offers are privately observed; this model complements it by showing delegation can solve the commitment problem.
- **Aghion and Tirole (1997)** — double-sided moral hazard in which delegation encourages a single agent's effort; here two agents' efforts are complements and the principal makes no effort contribution, so delegation operates through a different channel.
- **Halac et al. (2021)** — public distribution but private realization of pay packages rules out bad equilibria with principal commitment; differs because here the principal cannot commit to non-discriminatory pay.
- **Cullen and Pakzad-Hurson (2023)** — full pay transparency lowers pay inequality by reducing the principal's bargaining power; contrasts with the present result that transparency raises pay levels and reduces inequality only when efforts are highly substitutable.
- **DeMarzo and Kaniel (2023)** — keeping-up-with-the-Joneses preferences under which private contracts worsen externalities; contrasts with the present finding on how privacy interacts with pay levels and inequality.
- **Megginson and Weiss (1991)** — underwriter market-share reputation measure, used to operationalize relative skill $\alpha$ in the banking-syndicate application.
- **Carter and Manaster (1990)** — tombstone-based underwriter reputation rank, a second proxy for relative skill $\alpha$.

## Implications

Mapped to banking syndicates, the comparative statics yield qualitative, testable predictions:

1. Sole mandates (delegation) are more likely for firm-commitment deals, in colder markets, from less well-known issuers, and for lower-rated debt.
2. Fee income is more concentrated among a few top-tier banks when underwriters' skill is more asymmetric, when the deal is harder to place, and when private compensation components are relatively more important.
3. More pay transparency (higher $\lambda$) raises total underwriting spreads and reduces the share of the highest-reputation bank(s) under centralized (joint-mandate) structures.
4. Sole mandates become more likely as bank-effort substitutability increases (CES result).
