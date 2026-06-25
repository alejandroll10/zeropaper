# Dynamic Banking with Deposit-Flow Risk under Leverage Regulation

## One-sentence contribution
Because a bank cannot fully control deposit flows, deposit inflows raise leverage and can *destroy* shareholder value when equity capital is low — turning the marginal value of deposits negative and causing lending to fall rather than rise under leverage regulation.

## Setup

### Environment
A single bank maximizes risk-neutral shareholder value in continuous time while facing two uncontrollable random processes: asset-return shocks and deposit-flow shocks. The balance sheet has two state variables — the deposit stock $X_t$ and equity capital $K_t$ — and the bank controls five variables: the risky loan book $A_t$, bond issuance $B_t$, the deposit rate $i_t$, dividends $dU_t$, and equity issuance $dF_t$. The resource (balance-sheet) constraint is

$$A_t = K_t + X_t + B_t \tag{3}$$

Deposits evolve as a diffusion that the bank only partially controls via the deposit rate:

$$dX_t = -X_t(\delta_X\,dt - \sigma_X\,d\mathcal{W}^X_t) + X_t\,n(i_t)\,dt \tag{1}$$

where $\mathcal{W}^X_t$ is a standard Brownian motion, $\delta_X$ is the drift of payment outflows, $\sigma_X$ the deposit-flow volatility, and $n(i_t) = \omega_0 + \omega_1(i_t - r)$ is deposit demand (eq. 21): raising $i_t$ above the risk-free rate $r$ attracts deposits, lowering it repels them. The deposit rate faces a zero lower bound, $i_t \ge 0$. Crucially, because depositors freely move money in and out, the bank cannot perfectly control $X_t$ — distinguishing it from nondepository intermediaries and nonfinancial firms.

Equity evolves as

$$dK_t = A_t\big[(r+\alpha_A)\,dt + \sigma_A\,d\mathcal{W}^A_t\big] - B_t r\,dt - X_t i_t\,dt - C(n(i_t), X_t)\,dt - dU_t + dF_t \tag{2}$$

where $\alpha_A$ is the excess return on lending, $\sigma_A$ is asset-return volatility, $\phi\,dt$ is the instantaneous covariance between deposit and asset shocks, and $C(n(i_t), X_t) = c(n(i_t))X_t$ is the cost of maintaining the deposit franchise.

Two regulatory constraints bind. A capital requirement caps the risky-asset-to-equity ratio, $A_t/K_t \le \xi_K$ (baseline $\xi_K = 14.3$, eq. 6). A supplementary leverage ratio (SLR) imposes a lower bound on $k \equiv K/X$:

$$k \ge \underline{k} \equiv \frac{1}{1 - \xi_L^{-1}} - 1 \tag{13}$$

with $\xi_L = 20$ in the baseline (so $\underline{k} \approx 0.05$). Hitting $\underline{k}$ forces costly external equity issuance, with cost $dH_t = \psi_1\,dF_t + \psi_0 X_t\,dt$, where $\psi_1 = 5\%$ is the proportional issuance cost and $\psi_0 = 0.14\%$ is a fixed flow cost proportional to deposit size. The bank solves

$$V_0 = \max_{\{A,B,i,U,F\}}\mathbb{E}\Big[\int_{t=0}^{\tau} e^{-\rho t}(dU_t - dF_t - dH_t)\Big] \tag{5}$$

with $\rho > r$ the shareholders' discount rate and $\tau$ the stochastic closing time.

## Analysis

### Key result
The functional forms make the value function homogeneous of degree one, $V(X,K) = v(k)\,X$ with $k \equiv K/X$ (eq. 9). The two-dimensional problem collapses to a one-dimensional HJB equation for $v(k)$ on the inaction interval $[\underline{k}, \overline{k}]$:

$$\rho v(k) = \max_{\pi^A, i}\Big\{ [v(k) - v'(k)k]\big[-\delta_X + n(i)\big] + \tfrac12 v''(k)k^2\sigma_X^2 + v'(k)(1+k)(r + \pi^A\alpha_A) + \tfrac12 v''(k)(1+k)^2(\pi^A\sigma_A)^2 - v'(k)[i + c(n(i))] - v''(k)k(1+k)\pi^A\sigma_A\sigma_X\phi \Big\} \tag{10}$$

where $\pi^A = A/(X+K)$ is the portfolio weight on risky assets. The **deposit marginal $q$** is $V_X(X,K) = v(k) - v'(k)k$ and the **equity marginal $q$** is $V_K(X,K) = v'(k)$. The central result is that the deposit marginal $q$ is positive for well-capitalized banks but turns negative as $k \to \underline{k}$: an extra dollar of deposits *reduces* shareholder value when the bank is near its equity-issuance boundary.

The first-order conditions of (10) give the optimal lending and deposit-rate rules:

$$\frac{A}{K} = \frac{\alpha_A}{\gamma(k)\sigma_A^2} + \frac{\sigma_X}{\sigma_A}\phi \tag{18}$$

$$i = r + \frac{(v(k)-v'(k)k)/v'(k) - 1/\omega_1}{\omega_1\theta} - \frac{\omega_0}{\omega_1} \tag{23}$$

where $\gamma(k) \equiv -v''(k)k/v'(k)$ is the bank's endogenous relative risk aversion (eq. 19).

### Proof
The derivation reduces the two-state stochastic control problem to an ODE via the degree-one homogeneity of $V$. Writing $V(X,K)=v(k)X$ and substituting the deposit and equity laws of motion (1)–(2) into the dynamic-programming equation yields the scalar HJB (10) for $v(k)$ on $[\underline{k},\overline{k}]$. Maximizing the right-hand side of (10) pointwise: the FOC in $\pi^A$ gives the portfolio rule (18), in which the first term is a Merton-style mean-variance demand scaled by the endogenous risk aversion $\gamma(k)=-v''(k)k/v'(k)$ and the second term $(\sigma_X/\sigma_A)\phi$ is a deposit-hedging demand; the FOC in $i$ gives the $q$-theory deposit-rate rule (23), increasing in the ratio of deposit marginal $q$ to equity marginal $q$. The free-boundary problem is closed by value-matching $v(\underline{k}+m) = 1+\psi_1$ and smooth-pasting $v'(\underline{k}) = 1+\psi_1$ at the issuance boundary (eq. 14), and $v'(\overline{k}) = 1$ (eq. 16) with the supercontact condition $v''(\overline{k}) = 0$ (eq. 17) at the dividend boundary. The sign of the deposit marginal $q = v(k)-v'(k)k$ follows from the shape of $v$: near $\underline{k}$ the marginal value of equity $v'(k)$ rises sharply (equity is scarce because issuance is imminent and costly), so $v'(k)k$ exceeds $v(k)$ and the deposit marginal $q$ turns negative. Even though shareholders are risk-neutral, $\gamma(k) > 0$ because equity issuance costs make the bank endogenously risk-averse.

### Economic mechanism
Deposit-taking is a double-edged sword. In normal times deposits are a cheap funding source and the deposit marginal $q$ is positive. But the bank cannot stop deposits from flowing in, and an inflow raises the deposit stock $X$ relative to equity $K$, lowering $k$ and pushing the bank toward the SLR-implied equity-issuance boundary $\underline{k}$. Because issuing equity is costly, the shadow value of equity $v'(k)$ rises steeply as $k$ falls, and an extra dollar of deposits — by consuming scarce leverage capacity — destroys shareholder value: the deposit marginal $q$ goes negative. The bank responds by cutting the deposit rate toward the zero lower bound (to repel inflows), reducing lending, and holding safe assets. Because the deposit rate cannot fall below zero and a low risk-free rate compresses the deposit spread $r - i$, banks in low-rate environments have less room to manage deposit flows, amplifying the mechanism.

## Comparative statics
- **Loan-to-capital ratio vs. capitalization ($k$):** $A/K$ rises from $\sim 0$ near $\underline{k}$ to $\sim 14$ (the capital-requirement ceiling) as $k$ increases — procyclical in capitalization. The capital requirement binds about 7% of the time; the SLR binds far more frequently.
- **Marginal value of equity $v'(k)$:** reaches $\sim 7$ at $k = \underline{k} \approx 0.052$; stays between 1.022 and 1.029 for 25% of stationary time; exceeds 1.08 for 5.5% of the time — a long shadow cast by the issuance boundary.
- **SLR relaxation (5%→4%), lending:** $A/K$ is *higher* in the short run (given $k$) but *lower* in the long run (against the stationary c.d.f. of $k$); a tighter SLR generates reach-for-yield over the long run.
- **SLR relaxation, deposits:** raises deposit marginal $q$ and the deposit rate for low-$k$ banks (shrinking the ZLB region), but the deposit marginal $q$ becomes *more* negative near the new, lower issuance boundary.
- **Lower risk-free rate ($r=1\%$ vs $r=2\%$):** the bank *reduces* $A/K$ at all quantiles of $k$ under $r=1\%$; the deposit rate is less than 0.8 pp higher under $r=2\%$ — less flexibility to manage deposit risk lowers lending.

## Connection to literature
- **Merton (1969)** — portfolio choice with risky assets; the bank's lending problem is cast as a portfolio problem over long-term funds $K+X$, with (18) inheriting the mean-variance form.
- **Leland (1994a)** — dynamic capital structure with diffusion asset risk; extended here to add stochastic deposit liabilities and a deposit-flow state variable.
- **Brunnermeier and Sannikov (2014)** — macro-finance portfolio approach; this model adds deposits as a state variable alongside equity.
- **Drechsler, Savov, and Schnabl (2017)** — deposit-flow sensitivity to the deposit rate and the deposit spread $r-i$ as a profitability measure; used here to motivate deposit demand $n(i)$ and the low-rate compression channel.
- **Drechsler, Savov, and Schnabl (2021)** — treat deposits as long-duration sticky liabilities without interest-rate risk; this model instead makes deposit-flow risk the central friction.
- **Diamond and Dybvig (1983)** — departs from the run-based view: bank runs are not modeled; deposit *inflow* risk under equity-issuance costs is the focus.

## Implications
1. Deposit marginal $q$ is positive ($\sim 0.11$) for 80% of the stationary distribution of $k$ but drops sharply negative (to $\sim -0.18$) as $k$ approaches the equity-issuance boundary ($\sim 0.052$).
2. The loan-to-capital ratio $A/K$ is procyclical in capitalization, rising from $\sim 0$ to $\sim 14$; the capital requirement binds about 7% of the time.
3. The marginal value of equity is sharply elevated near the issuance boundary (reaching $\sim 7$), casting a long shadow over bank behavior.
4. Relaxing the SLR raises lending immediately but lowers long-run risk-taking per unit of equity — tightening the SLR generates long-run reach-for-yield.
5. Relaxing the SLR raises deposit marginal $q$ and deposit rates and shrinks the ZLB region, but makes the deposit marginal $q$ more negative near the new lower boundary.
6. A lower risk-free rate reduces bank lending: with $r=1\%$ vs $r=2\%$, $A/K$ is lower at all quantiles of $k$ because the bank has less room to manage deposit risk via the deposit spread.
