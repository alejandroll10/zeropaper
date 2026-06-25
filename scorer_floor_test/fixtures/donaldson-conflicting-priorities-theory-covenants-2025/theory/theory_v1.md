# Conflicting Priorities: A Theory of Covenants and Collateral

## One-sentence contribution

Collateral and negative pledge covenants are complementary tools for managing the over/underinvestment trade-off: collateral implements efficient dilution that covenants alone cannot, while covenants commit the borrower not to use collateral when dilution is inefficient, so the optimal debt structure is multilayered and first-best efficient.

## Setup

### Environment

Three dates $t \in \{0, 1, 2\}$ (Section I). A borrower B has two sequential projects.

**Projects.**
- Project 0 costs $I_0$ at Date 0, succeeds with probability $p$, and yields cash flow $X_0 > 0$ and private benefit $Y_0 > 0$. It has positive value (eq. 1):

$$
p(X_0 + Y_0) > I_0. \tag{1}
$$

- Project 1 costs $I_1$ at Date 1, succeeds with probability $p$, and yields cash flow $X_1^Q > 0$ and private benefit $Y_1^Q > 0$ depending on quality $Q \in \{H, L\}$ revealed at Date 1. Project 1 has positive value only if $Q = H$ (eq. 2):

$$
p(X_1^H + Y_1^H) > I_1 > p(X_1^L + Y_1^L). \tag{2}
$$

**Frictions** (Section I.B):
1. *Limited pledgeability*: private benefits $Y_t$ cannot be pledged to creditors; only cash flows $X_t$ are pledgeable.
2. *Nonexclusive contracting*: existing creditors cannot prevent B from contracting with new creditors at Date 1.

**Instruments**:
1. *Secured debt*: face value $F^s$; collateral gives absolute priority over unsecured claims.
2. *Unsecured debt*: face value $F^u$; no collateral.
3. *Covenant-protected (unsecured) debt*: unsecured but grants the right to accelerate if B takes on new secured debt.

**Priority rules**: secured debt has priority over unsecured; earlier secured over later secured; earlier unsecured (or accelerated) over later unsecured.

**Assumptions.** Under the efficient investment policy, expected cash flows exceed funding needs (Assumption 1, eq. 3):

$$
pX_0 - I_0 + q(pX_1^H - I_1) \ge 0. \tag{3}
$$

Liquidation value suffices to repay the secured debt needed to finance Project 1 (Assumption 2, eq. 4):

$$
p\!\left(X_0 + X_1^Q\right) > \frac{I_1}{p}. \tag{4}
$$

The first-best policy is to undertake both projects and invest in Project 1 if and only if $Q = H$ (Lemma 1). Contracts, including covenant violations, are observable; B has full bargaining power in renegotiation; competitive creditors earn zero profit (Section I.C).

## Analysis

### Key result

Five propositions (Core results):

- **R1 / Prop. 1 (eqs. 5-6):** Unsecured debt implements first-best when the private benefit of the low-quality project satisfies $Y_1^L \le Y_1^*$ (or total expected cash flows exceed funding needs); otherwise an overinvestment temptation prevents efficiency.
- **R2 / Prop. 2 (eqs. 7-8):** Secured debt implements first-best when $X_1^H \ge X_1^L$ (the high-quality project has higher pledgeable cash flow); a "mild" underinvestment problem.
- **R3 / Prop. 3 (eq. 9):** Covenants are irrelevant when all unsecured debt is covenant-protected ($\phi = 1$); the acceleration threat is self-defeating. Acceleration becomes credible only if $\phi \le \phi^*$, where

$$
\phi^* := 1 - \frac{(1-p)I_1/p}{p(X_0 + X_1^L - I_1/p)} \in (0,1). \tag{9}
$$

- **R4 / Prop. 4 (eq. 10):** A mix of covenant-protected and unprotected debt implements first-best in the "severe" underinvestment case, under the sufficient (and, under additional conditions, necessary) condition

$$
X_1^L \ge X_1^H. \tag{10}
$$

- **R5 / Prop. 5:** The equilibrium debt structure is always first-best efficient; instrument choice (secured vs. covenant-protected unsecured) depends on the severity of the underinvestment problem.

### Proof

A faithful sketch of the page's stated derivation (Method, Section I.C and). The model is solved by backward induction to subgame perfect equilibrium:

1. Characterize the Date 1 subgame equilibrium given any Date 0 debt structure (which instruments, what face values, what covenant fraction $\phi$).
2. Derive necessary and sufficient conditions on the Date 0 debt structure for the first-best (Lemma 1) to obtain in every subgame.
3. Show a Date 0 structure satisfying those conditions always exists (Proposition 5).

The covenant-irrelevance argument (Proposition 3): when $\phi = 1$ there is no unprotected unsecured debt to leapfrog, so the covenant-protected creditor's benefit from acceleration is zero and the threat is not credible; the credibility threshold is $\phi^*$ (eq. 9). The covenant-effectiveness argument (Proposition 4): under $X_1^L \ge X_1^H$ (eq. 10) the covenant-protected creditor gains more from accelerating against a bad project (larger pledgeable cash flows to grab) than a good one, making the acceleration threat selective. The formal foundation is Appendix A (Lemmas A.1-A.18).

### Economic mechanism

Because collateral trumps covenants, a new secured debt issue retains its priority even when it violates a covenant, so negative pledge covenants have no teeth on their own. Unsecured debt allows dilution at Date 1 by new secured creditors: this relaxes financial constraints (good dilution when $Q = H$) but also enables overinvestment (bad dilution when $Q = L$). Secured debt at Date 0 limits dilution capacity, preventing bad dilution but potentially causing underinvestment. The acceleration threat, generally not credible when all debt is covenant-protected, becomes credible when only some debt is ($\phi \le \phi^*$). Collateral and covenants therefore implement efficiency only in concert: covenants commit the borrower not to use collateral when dilution is inefficient (bad dilution), and collateral is needed to break that commitment and engage in good dilution when covenants would otherwise block efficient investment.

## Comparative statics

Directional / heterogeneity results reported by the page (Core results and Section IV):

- Covenant effectiveness requires the covenant fraction to satisfy $\phi \le \phi^*$ (eq. 9); above $\phi^*$ covenants have no bite.
- The covenant route applies in the "severe" underinvestment case ($X_1^L \ge X_1^H$, eq. 10); the secured-debt route applies in the "mild" case ($X_1^H \ge X_1^L$).
- Firms more exposed to underinvestment (growth opportunities, high fixed costs, nonredeployable assets) use covenants more.
- Firms more exposed to overinvestment (distressed firms, declining industries) use collateral more.
- Collateral use increases and covenant use decreases with asset tangibility.
- Covenant use decreases with the costs associated with asset sales (less redeployable, harder to value, more firm-specific assets).

## Connection to literature

- **Ayotte and Bolton (2011)** (extends): they study negative pledge covenants and property versus priority rights; this paper extends their analysis to allow for efficient dilution and renegotiation, rationalizing covenant violations and waivers and showing covenants and collateral are complementary rather than substitutes.
- **Hart and Moore (1995)** (builds-on): the spirit of using hard claims (debt) to constrain investment while retaining flexibility follows them.
- **Donaldson, Gromb, and Piacentino (2020a)** (extends): extends their collateral-overhang result by adding covenants as an additional instrument alongside collateral.
- **Rampini and Viswanathan (2013)** (cites): collateral and capital structure evidence cited in the empirical discussion.
- **Bebchuk and Fried (1996)** (cites): the policy debate about strong priority of secured claims, which the model addresses (strong priority is useful because it lets borrowers dilute when, but only when, it is efficient).

## Implications

Headline findings (Core results-conclusion and Section IV):

- The optimal debt structure is multilayered, combining secured and unsecured debt with and without covenants, and is always first-best efficient in equilibrium (Prop. 5).
- Covenants are violated and waived on the equilibrium path, consistent with observed practice, not as failures of contracting.
- Consistency with stylized facts: well-capitalized/highly rated firms rely heavily on unsecured debt (Rauh and Sufi (2010); Benmelech, Kumar, and Rajan (2024)); negative pledge covenants appear in roughly 44% of debt contracts (Billett, King, and Mauer (2007); Ivashina and Vallee (2018)); covenants are frequently violated and renegotiated or waived (Beneish and Press (1993, 1995); Dichev and Skinner (2002)); covenants in some debt decrease the yield on other debt by reducing default risk (Bradley and Roberts (2015)).
- New untested predictions (Predictions 1-4): covenant use rises with underinvestment exposure; collateral use rises with overinvestment exposure; collateral use increases and covenant use decreases with asset tangibility; covenant use decreases with the costs of asset sales.
- Policy: strong priority rules for secured creditors are useful because they let borrowers dilute when, but only when, it is efficient (speaks to Bebchuk and Fried (1996)).
