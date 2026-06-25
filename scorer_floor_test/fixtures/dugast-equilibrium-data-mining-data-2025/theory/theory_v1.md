# Equilibrium Data Mining and Data Abundance

## One-sentence contribution
Data abundance (a larger data frontier $$\tau_{dm}^{\text{max}}$$) always raises asset price informativeness but can reduce data miners' search intensity and the capital allocated to quant funds, so the two dimensions of the big data revolution — lower processing costs $$c$$ and a larger data frontier — have asymmetric and sometimes opposite effects, with active managers' average performance hump-shaped in both.

## Setup

### Environment
A rational-expectations equilibrium model with four periods (Figure 1). Period 0: investors (mass one, capital $$W_0$$) allocate savings to either an "expert" (discretionary fund) or a "data miner" (quant fund), as in Garleanu and Pedersen (2018). Period 1: data miners conduct sequential search for a predictor. Period 2: trading occurs. Period 3: the risky-asset payoff $$\omega \sim \mathcal{N}(0, \sigma_\omega^2)$$ is realized.

Primitives:
- All managers receive a noisy signal $$s_{\tau_i} = \omega + \tau_i^{-1/2}\varepsilon_i$$, $$\varepsilon_i \sim \mathcal{N}(0, \sigma_\omega^2)$$ (eq. 1), where $$\tau_i$$ is signal precision ("quality").
- Experts' skill $$\tau$$ is fixed, drawn from c.d.f. $$\Gamma(\cdot)$$ (density $$\gamma(\cdot)$$) on $$[0, \tau_{ex}^{\text{max}}]$$.
- Data miners discover a predictor by sequential search: each round costs $$c$$ and yields a precision draw $$\tau \sim \Phi(\cdot)$$ on $$[0, \tau_{dm}^{\text{max}}]$$ (eq. 2), with $$\Phi(\tau) = \Psi(\tau)/\Psi(\tau_{dm}^{\text{max}})$$. The data frontier $$\tau_{dm}^{\text{max}}$$ is the maximum attainable precision from available data sets; larger $$\tau_{dm}^{\text{max}}$$ = data abundance.
- A data miner with stopping threshold $$\tau_i^*$$ stops when a draw exceeds $$\tau_i^*$$; per-round stopping likelihood $$\Lambda(\tau_i^*; \tau_{dm}^{\text{max}}) = 1 - \Phi(\tau_i^*)$$ (eq. 3). $$\tau^*$$ is the "search intensity."
- Capital allocation: $$\mu$$ is the fraction of investor capital to data miners. Investors observe experts' skills, allocate to experts with skill $$\tau \geq \underline{\tau}$$ (marginal expert) until capacity, rest to data miners. In a stable interior equilibrium $$\mu^* = \Gamma(\tau^*)$$ (eq. 8), with marginal expert skill $$= \tau^*$$.
- Trading market as in Vives (1995): noise traders with aggregate demand $$\eta \sim \mathcal{N}(0, \sigma_\eta^2)$$; risk-neutral dealers post $$p^* = \mathbb{E}[\omega \mid D(p^*)]$$ (eq. 4). Managers have CARA risk aversion $$\rho$$. Price informativeness measured by inverse residual payoff variance (Grossman and Stiglitz 1980; Verrecchia 1982).
- Manager $$i$$'s client wealth: $$W_{i,j} = W_0 + x_i(s_{\tau_i}, p)(\omega - p) - (n_i c)\mathbb{1}_{\{j=dm\}}$$ (eq. 5), $$n_i$$ = number of search rounds.
- Investor utility from an expert of skill $$\tau$$: $$H(\tau) = \mathbb{E}[-\exp(-\rho(W_0 + x_i(s_{\tau_i}, p)(\omega - p)))]$$ (eq. 6); from a data miner of intensity $$\tau_i^*$$: $$V(\tau_i^*) = \mathbb{E}[-\exp(-\rho(W_0 + x_i(\omega - p)))] \times \mathbb{E}[\exp(\rho(n_i c))]$$ (eq. 7), the second factor being the expected utility cost of exploration.

## Analysis

### Key result
The equilibrium is characterized in three steps.

**Trading equilibrium (Proposition 1, eqs. 11–13).** Each manager's demand is proportional to her signal minus the price:
$$
x^*(s_\tau, p) = \beta(\tau)(s_\tau - p), \qquad \beta(\tau) = \frac{\tau}{\rho \sigma_\omega^2} \tag{11}
$$
The equilibrium price is a sufficient statistic for aggregate demand:
$$
p^* = \mathbb{E}[\omega \mid D(p^*)] = \lambda(\tau^*)\xi, \qquad \xi \equiv \omega + \rho \sigma_\omega^2 \bar{\tau}(\tau^*; \tau_{dm}^{\text{max}})^{-1}\eta, \qquad \lambda(\tau^*) \equiv \frac{\bar{\tau}^2}{\bar{\tau}^2 + \rho^2 \sigma_\omega^4 \sigma_\eta^2} \tag{12-13}
$$
Price informativeness (Lemma 1, eq. 14):
$$
\mathcal{I}(\tau^*; \tau_{dm}^{\text{max}}) \equiv \text{Var}[\omega \mid p^*]^{-1} = \frac{1}{\sigma_\omega^2} + \frac{\bar{\tau}(\tau^*; \tau_{dm}^{\text{max}})^2}{\rho^2 \sigma_\omega^4 \sigma_\eta^2} \tag{14}
$$
strictly increasing in average signal quality $$\bar{\tau}$$, hence in $$\tau^*$$.

**Equilibrium data mining (Proposition 2).** Trading value of a quality-$$\tau$$ signal (Lemma 2, eq. 16):
$$
g(\tau, \tau^*) = -\left(1 + \frac{\tau}{\sigma_\omega^2 \mathcal{I}(\tau^*; \tau_{dm}^{\text{max}})}\right)^{-\frac{1}{2}} \tag{16}
$$
Continuation value after rejecting a predictor of quality $$\hat{\tau}_i$$ (eq. 18):
$$
J(\hat{\tau}_i, \tau^*) = \frac{\exp(\rho c)\Lambda(\hat{\tau}_i; \tau_{dm}^{\text{max}})}{1 - \exp(\rho c)(1 - \Lambda(\hat{\tau}_i; \tau_{dm}^{\text{max}}))} \times \mathbb{E}_\phi[g(\tau, \tau^*) \mid \hat{\tau}_i \leq \tau \leq \tau_{dm}^{\text{max}}] \tag{18}
$$
In symmetric equilibrium, $$\tau^*$$ solves $$g(\tau^*, \tau^*) = J(\tau^*, \tau^*)$$, which reduces to:
$$
F(\tau^*) = \exp(-\rho c) \tag{21}
$$
with
$$
F(\tau^*) \equiv \int_{\tau^*}^{\tau_{dm}^{\text{max}}} r(\tau, \tau^*)\phi(\tau)d\tau + (1 - \Lambda(\tau^*; \tau_{dm}^{\text{max}})), \quad r(\tau, \tau^*) \equiv \left(\frac{\tau^* + \sigma_\omega^2 \mathcal{I}}{\tau + \sigma_\omega^2 \mathcal{I}}\right)^{\frac{1}{2}} \tag{22-23}
$$
Proposition 2: this equation has a unique solution $$\tau^* \in (0, \tau_{dm}^{\text{max}})$$ whenever $$F(0) < \exp(-\rho c)$$.

**Full equilibrium (Proposition 3).** Combining the trading equilibrium, the data-mining condition, and the capital-allocation condition $$\mu^* = \Gamma(\tau^*)$$ (eq. 8) gives the full equilibrium.

### Proof
The page presents a formal derivation (full proofs in the appendix). Sketch as the page states it:
- Step 1 (Prop. 1): take $$\tau^*$$ (hence $$\mu^*$$) as given; solve the CARA-normal trading equilibrium for demand (eq. 11), price (eq. 12), $$\lambda$$ (eq. 13), and informativeness (eq. 14).
- Step 2 (Prop. 2): derive the trading value of a signal (Lemma 2, eq. 16) and the search continuation value (eqs. 17–18); the indifference/optimal-stopping condition $$g(\tau^*,\tau^*) = J(\tau^*,\tau^*)$$ reduces to $$F(\tau^*) = \exp(-\rho c)$$ (eq. 21); existence/uniqueness of $$\tau^* \in (0,\tau_{dm}^{\text{max}})$$ under $$F(0)<\exp(-\rho c)$$.
- Step 3 (Prop. 3): impose $$\mu^* = \Gamma(\tau^*)$$ to close the model.
- The data-frontier comparative statics (Props. 4–5) follow from differentiating $$F$$. The decomposition (eq. A26 Appendix; related text at eq. 25) separates the hidden gold-nugget effect (larger $$\tau_{dm}^{\text{max}}$$ raises the value of the best possible predictor) from the price-informativeness effect (more data raises $$\mathcal{I}$$, lowering the value of any given signal):
$$
\frac{\partial F}{\partial \tau_{dm}^{\text{max}}} = \underbrace{\phi(\tau_{dm}^{\text{max}})(r(\tau_{dm}^{\text{max}}, \tau^*) - \mathbb{E}_\phi[\min\{1, r(\tau, \tau^*)\}])}_{<0:\ \text{Gold Nugget Effect}} + \underbrace{\left(\int_{\tau^*}^{\tau_{dm}^{\text{max}}} \frac{\partial r(\tau, \tau^*)}{\partial \mathcal{I}} \phi(\tau)d\tau\right) \frac{\partial \mathcal{I}}{\partial \tau_{dm}^{\text{max}}}}_{>0:\ \text{Informativeness Effect}} \tag{26}
$$
When $$\tau_{dm}^{\text{max}}$$ is large enough, the positive informativeness effect dominates, so $$\partial F/\partial \tau_{dm}^{\text{max}} > 0$$ and $$\tau^*$$ decreases with $$\tau_{dm}^{\text{max}}$$ (Prop. 5). Numerical illustrations use $$\Phi(\tau) = \frac{1-(1+\tau)^{-3/2}}{1-(1+\tau_{dm}^{\text{max}})^{-3/2}}$$ and $$\Gamma(\tau) = 1-(1+\tau)^{-3/2}$$ (Figure 2).

### Economic mechanism
Two dimensions of the big data revolution act on the market for active management. Lower processing cost $$c$$ makes each search round cheaper, so data miners search more demanding predictors (higher $$\tau^*$$), raising signal quality, capital to quants, and informativeness. A larger data frontier $$\tau_{dm}^{\text{max}}$$ has two opposing forces: the hidden gold-nugget effect (better best-possible predictors raise the value of searching) versus the price-informativeness effect (more data in aggregate raises price informativeness, which erodes the trading value of any given signal). Once $$\tau_{dm}^{\text{max}}$$ is large, the informativeness effect dominates, so data abundance reduces search intensity and capital to quants — yet because average signal quality still rises, price informativeness always increases.

## Comparative statics
- Lower search cost $$c$$: $$\partial\tau^*/\partial c < 0$$; raises $$\tau^*$$, $$\mu^* = \Gamma(\tau^*)$$, average signal quality, and price informativeness; $$\tau^* \to \tau_{dm}^{\text{max}}$$ as $$c \to 0$$ (Prop. 4, R3).
- Larger data frontier above threshold $$\tau^{tr}(c)$$: for $$\tau_{dm}^{\text{max}} > \tau^{tr}(c)$$, $$\partial\tau^*/\partial\tau_{dm}^{\text{max}} < 0$$ and $$\partial\mu^*/\partial\tau_{dm}^{\text{max}} < 0$$ (Prop. 5, R4); $$\tau^{tr}(c)$$ exists for all $$c>0$$.
- Price informativeness in the data frontier: $$\partial\mathcal{I}/\partial\tau_{dm}^{\text{max}} > 0$$ always; $$\mathcal{I}$$ bounded above as $$\tau_{dm}^{\text{max}}\to\infty$$ (Prop. 5, R5; Assumption 1).
- Average gross excess return: $$\mathbb{E}[\bar{R}^e(\tau)] = \frac{1}{W_0\rho}\left(\frac{1}{\bar\tau} + \frac{\bar\tau}{\rho^2\sigma_\omega^2\sigma_\eta^2}\right)^{-1}$$, peaks at $$\bar\tau = \rho\sigma_\omega\sigma_\eta$$; hump-shaped in $$c$$ and in $$\tau_{dm}^{\text{max}}$$ (Corollary 1, Fig. 3, R6).
- Capital to quants $$\mu^*$$: increases with lower $$c$$; hump-shaped in $$\tau_{dm}^{\text{max}}$$ (Table I). Same direction under both shocks when $$\tau_{dm}^{\text{max}} \leq \tau^{tr}(c)$$; opposite when $$\tau_{dm}^{\text{max}} > \tau^{tr}(c)$$.
- Data miners' relative performance $$RP$$: increases with $$\tau_{dm}^{\text{max}}$$ (Corollary 4); ambiguous with lower $$c$$ (Table I).
- Within-group performance dispersion $$\Delta R_\alpha$$: decreases with lower $$c$$; increases with $$\tau_{dm}^{\text{max}}$$ above threshold (Corollaries 2–3, Table I).
- Fees (Nash bargaining, $$\kappa>0$$): $$f_{dm}^* = 0$$; $$f_{ex}^*(\tau) = \kappa(w(\tau) - w(\tau^*))$$; experts' fees decline with a fall in $$c$$ and decline (low-skill experts) or may rise (high-skill experts) with $$\tau_{dm}^{\text{max}}$$ (Corollary 6, eqs. 39–41, R7).

## Connection to literature
- Garleanu and Pedersen (2018) — builds-on: baseline structure (investors allocate capital to informed and uninformed managers) and the Nash-bargaining-over-fees framework (Section VI).
- Grossman and Stiglitz (1980) — builds-on: noisy rational-expectations equilibrium and the price-informativeness measure used throughout (eq. 14).
- Verrecchia (1982) — extends: endogenous information-precision choice, extended here to an extensive margin (capital allocation) and an endogenous data frontier.
- Stambaugh (2020) — cites: related result that skill improvements reduce average active-manager performance; here endogenized via the price-informativeness channel (Corollary 1 discussion).
- Abis (2022) — tests: empirical evidence on quant vs. discretionary fund performance and growth (quant funds 6.1% → 18.6% of U.S. equity AUM, 2000–2017) used to motivate and corroborate model predictions.
- Pastor, Stambaugh, and Taylor (2015) — cites: evidence that active-industry size is negatively related to performance; matches the model's negative size–performance prediction.
- Han and Sangiorgi (2018) — cites: model of information acquisition as search; key difference is that this paper varies both intensive and extensive margins.
- Banerjee and Breon-Drish (2021) — cites: investor alternates between searching and not; here uncertainty is over signal quality, not foregone trading opportunities.

## Implications
- R1: An asset manager's optimal position is proportional to the gap between her signal and the price; the equilibrium price is a sufficient statistic for aggregate demand (Prop. 1, eqs. 11–13).
- R2: Price informativeness always increases with average signal quality and therefore with data miners' search intensity $$\tau^*$$ (Lemma 1, eq. 14).
- R3: Lower search cost $$c$$ always raises $$\tau^*$$, capital to quants $$\mu^*$$, average signal quality, and price informativeness; $$\tau^* \to \tau_{dm}^{\text{max}}$$ as $$c\to 0$$ (Prop. 4).
- R4: A larger data frontier reduces $$\tau^*$$ and capital to quants once it exceeds a threshold $$\tau^{tr}(c)$$, because the price-informativeness effect dominates the hidden gold-nugget effect (Prop. 5).
- R5: Pushing back the data frontier always raises average signal quality and price informativeness, even when it lowers quant search intensity; informativeness is bounded above (Prop. 5).
- R6: Average gross excess return is hump-shaped in $$c$$ and in the data frontier; the big-data revolution first raises, then lowers, average active performance (Corollary 1, Fig. 3).
- R7: Under Nash bargaining, data miners charge no rents; experts' fees are set by their scarcity and decline as data miners' search intensity rises, whether from lower $$c$$ or a larger data frontier (Corollary 6, eqs. 39–41).
