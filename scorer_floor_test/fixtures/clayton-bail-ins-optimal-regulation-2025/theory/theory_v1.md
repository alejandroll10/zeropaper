# Three-Period Dynamic Contracting Model of Bank Liability Structure

## One-sentence contribution
In a three-period dynamic contracting model with fire-sale externalities, the privately optimal bank contract combines short-term standard debt and long-term bail-in debt, while the social optimum jointly regulates the level and composition of debt — rationalizing a leverage cap plus a TLAC requirement satisfiable with bail-in debt, with bail-ins replacing bailouts as the recapitalization tool.

## Setup

### Environment
Three periods ($t = 0, 1, 2$), a unit continuum of banks, penniless investors, and arbitrageurs. Banks invest in a firm of variable scale $Y_0 = A_0 + I_0 > 0$ using their own equity $A_0 > 0$ and investor funds $I_0 \ge 0$.

- **Project quality shocks.** At each of dates 1 and 2, the bank experiences a stochastic quality shock $R_t \in [\underline{R}, \overline{R}]$ adjusting project scale to $Y_t = R_t Y_{t-1}$, so final scale is $Y_2 = R_1 R_2 Y_0$. The project pays one unit of consumption good per unit of final scale at date 2 and no dividend at date 1. Shocks $R_t$ are independent and idiosyncratic with densities $f_t(R_t \mid e_{t-1}) = e_{t-1} f_{tH}(R_t) + (1 - e_{t-1}) f_{tL}(R_t)$.
- **Effort and MLRP.** Date 0 effort is continuous, $e_0 \in [0,1]$; date 1 effort is binary, $e_1 \in \{0,1\}$. Higher effort increases the quality of the return distribution. The model assumes the monotone likelihood ratio property (MLRP): $\Lambda_t(R_t) \equiv f_{tH}(R_t) / f_{tL}(R_t)$ is increasing in $R_t$.
- **Private benefits.** The banker's date 0 private benefit is $B_0(e_0) Y_0$, with $B_0$ decreasing and concave and $B_0(1) = 0$. The date 1 private benefit is $(1 - e_1) B_1 Y_1$ for $0 < B_1 < 1$.
- **Resource constraints** along history $(R_1, R_2)$:

 $$c_1(R_1) + x_1(R_1) = \alpha(R_1) \gamma R_1 Y_0, \tag{1}$$
 $$c_2(R_1, R_2) + x_2(R_1, R_2) = (1 - \alpha(R_1)) R_1 R_2 Y_0. \tag{2}$$

 Limited liability requires $c_1(R_1), c_2(R_1, R_2) \ge 0$.
- **Investor participation** (break-even):

 $$Y_0 - A_0 \le \mathbb{E}\bigl[x(R_1) \mid e_0 = e_0^*\bigr]. \tag{6}$$

- **Fire sale / liquidation price.** A representative arbitrageur with borrowing constraints generates a fire-sale externality. The equilibrium liquidation price $\gamma$ satisfies the market-clearing condition:

 $$\gamma(\Omega) = \frac{\partial \mathcal{F}(\Omega)}{\partial \Omega}, \quad \Omega = \int_{\underline{R}}^{\overline{R}} \alpha(R_1) R_1 f_1(R_1 \mid e_0^*) \, dR_1. \tag{16}$$

 When $\partial^2 \mathcal{F} / \partial \Omega^2 < 0$, more liquidations reduce the price (the fire sale). The liquidation price elasticity is $\sigma = -(\Omega / \gamma)(\partial \gamma / \partial \Omega)$.

## Analysis

### Key result
**Date 1 incentive compatibility** — high effort $e_1^*(R_1) = 1$ is incentive compatible if:

$$\mathbb{E}[c_2(R_1, R_2)(\Lambda_2(R_2) - 1) \mid e_1 = 0] \ge B_1 R_1 Y_0. \tag{9}$$

**Date 0 optimal effort** satisfies:

$$-B_0'(e_0^*) Y_0 = \mathbb{E}_0[c(R_1)(\Lambda_1(R_1) - 1) \mid e_0 = 0]. \tag{12}$$

**Proposition 1 (privately optimal contract).** The liability structure has three regions: liquidation ($R_1 \le R_\ell^p$), bail-in write-down ($R_\ell^p < R_1 \le R_u^p$), and no write-down ($R_1 > R_u^p$). It is implemented with short-term standard debt of face value $(1-b)R_\ell^p Y_0$ and long-term bail-in debt of face value $(1-b)(R_u^p - R_\ell^p)Y_0$. The privately optimal thresholds $R_\ell^p$ and $R_u^p$ satisfy:

$$\underbrace{\frac{1 - \Lambda_1(R_\ell^p)}{(1 - e_0^*) + e_0^* \Lambda_1(R_\ell^p)} \frac{1}{|B_0''(e_0^*)|}}_{\text{Incentive Provision}} b \lambda G = \underbrace{b + \lambda(1 - b - \gamma)}_{\text{Liquidation Costs}}, \tag{20}$$

$$\underbrace{\frac{F_{1L}(R_u^p) - F_{1H}(R_u^p)}{|B_0''(e_0^*)|}}_{\text{Incentive Provision}} \lambda G = \underbrace{(\lambda - 1)(1 - F_1(R_u^p \mid e_0^*))}_{\text{Investor Repayment}}, \tag{21}$$

where $\lambda > 1$ is the Lagrange multiplier on the investor participation constraint and
$G = \int_{\underline{R}}^{R_\ell^p} \gamma R_1 (f_{1H}(R_1) - f_{1L}(R_1)) dR_1 + \int_{R_\ell^p}^{\overline{R}} (1-b) \min\{R_1, R_u^p\} (f_{1H}(R_1) - f_{1L}(R_1)) dR_1$.

**Proposition 2 (necessity of all three ingredients).** If $B_0(e_0) = 0$: bail-in debt alone suffices. If $B_1 = 0$: long-term debt alone suffices. If $\gamma = 1$: standard debt alone suffices. All three ingredients (initial incentive problem, continuation incentive problem, costly liquidation) are needed for the combined standard-plus-bail-in structure.

**Proposition 3 (social optimum, Equations 24-28).** The planner's optimum satisfies the same structural equations as the private optimum but with wedge terms $+\tau_\ell^s$ and $-\tau_u^s$ on the right-hand sides of Equations (24) and (25):

$$\tau_\ell^s = \left(1 - \frac{1 - \Lambda_1(R_\ell^s)}{(1 - e_0^s) + e_0^s \Lambda_1(R_\ell^s)} \frac{1}{|B_0''(e_0^s)|} b L^s\right) \lambda^s \sigma \gamma^s \ge 0, \tag{26}$$

$$\tau_u^s = \frac{F_{1L}(R_u^s) - F_{1H}(R_u^s)}{|B_0''(e_0^s)|} L^s \sigma \gamma^s \ge 0. \tag{27}$$

Socially optimal thresholds satisfy $R_\ell^s \le R_\ell^p$ and $R_u^s \le R_u^p$ (less standard debt and less total debt than private banks).

**Proposition 4 (bail-ins dominate bailouts under commitment).** With planner commitment over bailouts, no bailouts ($T_0 = T_1 = 0$) is Pareto efficient; bailouts are redundant recapitalization when bail-ins are available.

**Proposition 5 (no commitment, Equation 29).** Without planner commitment, the planner does not bail out banks if total liquidation losses are high enough: $(1 - \gamma(\Omega)) \Omega Y_0 \le F$ (Equation 29). For any $F \ge 0$, Pareto-efficient debt levels $(R_\ell^s, R_u^s)$ result in no banks being bailed out; welfare is strictly increasing in $F$ because higher $F$ relaxes the no-bailout constraint.

### Proof
This is a pure theory paper; the "proof" is the model's stated derivation, not an empirical identification argument.

- **Pledgeability reduction (Lemma 1).** The binary date 1 effort problem reduces to a Holmstrom and Tirole (1997) style pledgeability constraint. The optimal contract sets $x_1(R_1) = 0$ and repays investors on date 2 at a threshold $R_2^u(R_1)$. Date 1 high effort is incentive compatible iff $c(R_1) \ge b R_1 Y_0$, where $b = \int_{\overline{R}_2^u}^{\overline{R}} [R_2 - \overline{R}_2^u] f_{2H}(R_2) dR_2$ is a constant (Equation 18).
- **Mapping to promised liabilities.** Actual-repayment contracts map to promised "face value" liabilities $L(R_1)$: if $L(R_1) \le (1-b)R_1 Y_0$ the bank avoids liquidation; if $L(R_1) > (1-b)R_1 Y_0$ the bank is liquidated with actual repayment $\gamma R_1 Y_0$.
- **Private optimum.** Characterize the set of feasible contracts (limited liability, resource constraints (1)-(2), investor participation (6), repayment monotonicity, incentive compatibility (9), (12)), then maximize bank expected utility subject to those constraints; the first-order conditions yield thresholds $R_\ell^p$, $R_u^p$ via Equations (20)-(21) (Proposition 1).
- **Social optimum.** Re-solving with the planner internalizing the fire-sale externality (the dependence of $\gamma$ on aggregate liquidations $\Omega$ via Equation 16) adds the wedges $\tau_\ell^s, \tau_u^s$ of Equations (26)-(27), reflecting the social cost of liquidations $\lambda^s \sigma \gamma^s$ (Proposition 3).
- **Bailouts vs. bail-ins.** Under commitment, both bailouts and bail-ins can achieve the same state contingencies in bank debt contracts, so no bailouts is Pareto efficient (Proposition 4). Without commitment, the no-bailout constraint (Equation 29) holds at Pareto-efficient debt levels for any $F \ge 0$ (Proposition 5).

### Economic mechanism
Banks face an initial (date 0) and a continuation (date 1) monitoring incentive problem. In the presence of fire sales from liquidations, the privately optimal contract pairs short-term standard debt — which forces liquidation in bad states and provides strong incentives — with long-term bail-in debt — which avoids the resource costs of liquidation by writing down to pledgeable income. Bail-in debt combines the incentive properties of equity with the cash-flow-transfer properties of standard debt, making it superior to outside equity as a loss-absorbing instrument. A planner that internalizes the fire-sale externality intervenes in both the level and the composition of debt: it prefers less standard debt (a leverage cap) and less total debt (a TLAC requirement satisfiable with bail-in debt). Because bail-ins can replicate the recapitalization role of bailouts, bailouts become redundant, and statutory provisions that raise the cost of bailouts (higher $F$) improve welfare by relaxing the no-bailout constraint.

## Comparative statics
- Socially optimal thresholds satisfy $R_\ell^s \le R_\ell^p$ and $R_u^s \le R_u^p$: the planner uses less standard debt and less total debt than private banks (R2).
- Wedges $\tau_\ell^s \ge 0$ and $\tau_u^s \ge 0$, reflecting the social cost of liquidations $\lambda^s \sigma \gamma^s$ (R2).
- Welfare is strictly increasing in the cost of bailouts $F$ (R5).
- Ingredient ablations (Proposition 2 / R3): $B_0(e_0)=0 \Rightarrow$ bail-in debt alone; $B_1=0 \Rightarrow$ long-term debt alone; $\gamma=1 \Rightarrow$ standard debt alone.

## Connection to literature
- **Innes (1990)** — builds-on: the three-period incentive model of bank lending with unobservable effort is a repeated version of Innes (1990).
- **Holmstrom and Tirole (1997)** — builds-on: the pledgeability-constraint approach reduces the date 1 binary effort problem.
- **Keister and Mitkov (2023)** — cites: banks may not write down deposit creditors if anticipating government bailouts, motivating mandatory bail-ins.
- **Chari and Kehoe (2016)** — cites: costly state verification showing standard debt is renegotiation-proof; bail-ins reduce the level of standard debt.
- **Walther and White (2020)** — cites: precautionary bail-ins can signal adverse information and cause bank runs, motivating public-information bail-in rules.
- **Bolton and Oehmke (2019)** — cites: bank resolution and structure of global banks; demand-based explanation for standard debt.
- **Farhi and Tirole (2012)** — cites: collective moral hazard and systemic bailouts; bailout commitment benchmark.
- **Dewatripont and Tirole (1994)** — cites: theory of debt and equity as a foundational contracting framework.
- **Davila and Korinek (2018)** — cites: pecuniary externalities make fire sales Pareto inefficient, motivating macroprudential policy; this paper extends it to the bank contracting setting.

## Implications
- R1: The privately optimal contract uses both standard and bail-in debt — three regions (liquidation, bail-in write-down, no write-down), implemented with standard debt of face value $(1-b)R_\ell^p Y_0$ and bail-in debt of face value $(1-b)(R_u^p - R_\ell^p)Y_0$ (Proposition 1, Corollary 1).
- R2: The social optimum has the same structure as the private optimum but with additional wedges on standard and total debt; the planner uses less standard debt and less total debt ($R_\ell^s \le R_\ell^p$, $R_u^s \le R_u^p$) (Proposition 3).
- R3: All three model ingredients are needed for bail-in debt to be part of the optimal contract (Proposition 2).
- R4: With planner commitment, the socially optimal contract with no bailouts is Pareto efficient; bailouts are redundant when bail-ins are available (Proposition 4).
- R5: Without commitment, Pareto-efficient debt levels eliminate bailouts entirely; welfare is increasing in the cost of bailouts $F$ (Proposition 5).
