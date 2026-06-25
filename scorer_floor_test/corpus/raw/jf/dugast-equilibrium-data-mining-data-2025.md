---
title: "Equilibrium Data Mining and Data Abundance: Dugast & Foucault (2025)"
description: >-
  Distilled: A rational-expectations equilibrium model shows that data abundance
  (a larger data frontier) always raises price informativeness but can reduce
  data miners' search intensity and the capital allocated to quant funds, with
  asset managers' average performance being hump-shaped in both the data
  frontier and search costs. J. Finance 2025, CC BY-NC 4.0. Seven core results
  with source locators, the model equations, and the equilibrium derivation.
sidebar:
  label: Dugast-Foucault 2025
  order: 1
tags: [paper-summary, asset-pricing, information-economics, market-microstructure,
       quant-funds, institutional-investors, peer-reviewed, unreplicated]
paper:
  authors: "Jérôme Dugast, Thierry Foucault"
  authorList:
    - { family: Dugast, given: "Jérôme", orcid: "0000-0001-8233-8627", affiliation: "Universite Paris-Dauphine, PSL, CNRS, DRM Finance" }
    - { family: Foucault, given: Thierry, affiliation: "HEC Paris" }
  year: 2025
  venue: "The Journal of Finance 80(1), February 2025, 211-258"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13397
  jel:
    codes: [G14, G23, D83]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Complex Systems and Time Series Analysis", "Economic theories and models", "Financial Markets and Investment Strategies"]
  dataAccess: public
  outcome:
    - allocation of capital between quant funds and discretionary funds
    - data miners' equilibrium search intensity
    - asset price informativeness
    - asset managers' average gross excess return
    - dispersion in asset managers' performance
  outcomeClass: [security-returns, fund-behavior, asset-prices]
  license: "CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0, start 2024-10-27; corroborated by artifact p.211 Creative Commons Attribution-NonCommercial License notice)"
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "open-access PDF available via HAL (hal-04390540, 2026-06-06)"
  redistribution: extract-only (CC BY-NC 4.0; non-commercial restriction; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 15
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, information-channel-fg]
  contributionType: [new-theory, new-fact]
  mechanisms: [information-asymmetry, learning]
  scope:
    region: theoretical
    assetClass: risky asset (theoretical)
  proposedVocab:
    - { axis: topic, term: information-economics, def: "Study of how agents acquire, process, and trade on information, and how information production affects prices, market efficiency, and the allocation of resources.", aliases: [information-production, endogenous-information] }
    - { axis: topic, term: quant-funds, def: "Quantitative asset management: funds that use data-driven, statistical, or machine-learning methods to generate trading signals, as opposed to discretionary (judgmental) funds.", aliases: [quantitative-investors, data-miners-funds] }
  findings:
    - ref: R1
      outcome: equilibrium asset price and optimal manager position
      metric: coefficient
      value: "An asset manager's optimal position is proportional to the gap between her signal and the price; the equilibrium price is a sufficient statistic for aggregate demand (Prop. 1, eqs. 11-13)"
      direction: none
    - ref: R2
      outcome: price informativeness
      metric: coefficient
      value: "Price informativeness always increases with average signal quality, and therefore with data miners' search intensity tau* (Lemma 1, eq. 14)"
      direction: positive
    - ref: R3
      outcome: data miners' equilibrium search intensity
      metric: coefficient
      value: "Lower search cost c always raises tau*, capital allocated to quants mu*, average signal quality, and price informativeness; tau* converges to its max as c approaches 0 (Prop. 4)"
      direction: negative
    - ref: R4
      outcome: data miners' equilibrium search intensity
      metric: coefficient
      value: "A larger data frontier reduces tau* and capital to quants once it exceeds a threshold, because the price-informativeness effect dominates the hidden-gold-nugget effect (Prop. 5)"
      direction: negative
    - ref: R5
      outcome: price informativeness
      metric: coefficient
      value: "Pushing back the data frontier always raises average signal quality and price informativeness, even when it lowers quant search intensity; informativeness is bounded above (Prop. 5)"
      direction: positive
    - ref: R6
      outcome: active managers' average gross excess return
      metric: coefficient
      value: "Average gross excess return is hump-shaped in search cost c and in the data frontier; the big-data revolution first raises, then lowers, average active performance (Corollary 1, Fig. 3)"
      direction: mixed
    - ref: R7
      outcome: equilibrium expert and data-miner fees
      metric: coefficient
      value: "Under Nash bargaining, data miners charge no rents; experts' fees are set by their scarcity and decline as data miners' search intensity rises, whether from lower c or a larger data frontier (Corollary 6, eqs. 39-41)"
      direction: negative
  resultType: new-finding
  relatesTo:
    - { cite: "Garleanu and Pedersen (2018)", doi: '10.1111/jofi.12696', relation: builds-on, note: "Baseline model structure: investors allocate capital to informed and uninformed managers; framework for Nash-bargaining over fees (Section VI)" }
    - { cite: "Grossman and Stiglitz (1980)", relation: builds-on, note: "Noisy rational-expectations equilibrium and the measure of price informativeness used throughout (eq. 14)" }
    - { cite: "Verrecchia (1982)", doi: '10.2307/1913389', relation: extends, note: "Endogenous information-precision choice; Dugast-Foucault extend to allow extensive margin (capital allocation) and an endogenous data frontier" }
    - { cite: "Stambaugh (2020)", relation: cites, note: "Related finding that skill improvements reduce average active manager performance (Corollary 1 discussion, p. 233)" }
    - { cite: "Abis (2022)", relation: tests, note: "Empirical evidence on quant vs discretionary fund performance and growth used to motivate and corroborate model predictions (pp. 212-213, 242)" }
    - { cite: "Pastor, Stambaugh, and Taylor (2015)", doi: '10.1016/j.jfineco.2014.11.008', relation: cites, note: "Evidence on active managers' average performance and industry size; model predictions for negative size-performance relation match their findings (pp. 232, 241)" }
    - { cite: "Han and Sangiorgi (2018)", doi: '10.1016/j.jet.2018.01.021', relation: cites, note: "Related model of information acquisition as a search problem; key difference is that Dugast-Foucault allow both intensive and extensive margins to vary (p. 217)" }
    - { cite: "Banerjee and Breon-Drish (2021)", doi: '10.1093/rfs/hhab029', relation: cites, note: "Investor alternates between searching and not; Dugast-Foucault differ in that uncertainty is over signal quality, not foregone trading opportunities (p. 217)" }
  openQuestions:
    - "The model treats signal quality as perfectly known once a predictor is discovered, but in practice investors face uncertainty about whether their model will generalize out-of-sample; extending to uncertain signal quality is noted as outside the scope (p. 220, fn. 10)."
    - "The equilibrium with endogenous fund capacities (decreasing returns to scale with non-extreme cost functions) is noted as significantly more complex and not fully solved (p. 241, Section II.E.2 of Internet Appendix)."
    - "The paper proposes but does not conduct empirical tests exploiting cross-sectional variation in funds' exposure to alternative data sets (via industry or asset-class holdings) as natural experiments for the data-frontier shock (pp. 243-244)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-06", role: extracted, note: "Full text read (pp. 211-258 plus appendix proofs pp. 245-252); seven results extracted. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: "2026-06-06", role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all seven result rows confirmed; eq. 26 locator corrected from 'eq. 25-26, pp. 228-229' to 'eq. A26, p. 250 Appendix' to match the appendix formula actually displayed." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13397", checked: "2026-06-06", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2024-10-27" }
  rightsSignalConflict: false
---

**What this is.** The paper's core propositions, the model it builds on (a noisy rational-expectations equilibrium with two types of asset managers), and the mechanism it establishes (the price-informativeness effect dominates the hidden-gold-nugget effect for a large enough data frontier): enough to know what it found and how, without reading all 48 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13397).

## TL;DR

The paper builds a rational-expectations equilibrium model to study how the big data revolution affects the market for active asset management. Two types of managers coexist: "experts" (discretionary funds) with a fixed signal precision, and "data miners" (quant funds) who discover predictors through a sequential search process. The key finding is that the two dimensions of the big data revolution, lower information-processing costs ($$c$$) and a larger data frontier ($$\tau_{dm}^{\text{max}}$$, reflecting more available data sets), have asymmetric and sometimes opposite effects. Reducing search costs always raises data miners' search intensity and capital allocated to quants. But a larger data frontier can reduce quant search intensity and the allocation to quants once it is large enough, because greater price informativeness erodes the value of any given signal. Despite this, a larger data frontier always raises price informativeness. Asset managers' average gross performance is hump-shaped in both $$c$$ and $$\tau_{dm}^{\text{max}}$$, implying the big data revolution should eventually erode active managers' performance.

## Core results

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | An asset manager's optimal position is proportional to the gap between her signal and the asset price; the equilibrium price is a sufficient statistic for the aggregate demand | Proposition 1, eq. 11-13, p. 223 | Trading aggressiveness $$\beta(\tau) = \frac{\tau}{\rho \sigma_\omega^2}$$; equilibrium price $$p^* = \lambda(\tau^*) \xi$$ where $$\lambda(\tau^*) \equiv \frac{\bar{\tau}^2}{\bar{\tau}^2 + \rho^2 \sigma_\omega^4 \sigma_\eta^2}$$ |
| R2 | Price informativeness always increases with average signal quality and therefore with data miners' search intensity $$\tau^*$$ | Lemma 1, eq. 14, p. 224 | $$\mathcal{I}(\tau^*; \tau_{dm}^{\text{max}}) = \text{Var}[\omega \mid p^*]^{-1} = \sigma_\omega^{-2} + \bar{\tau}^2 / (\rho^2 \sigma_\omega^4 \sigma_\eta^2)$$; strictly increasing in $$\tau^*$$ |
| R3 | A decrease in data miners' search costs $$c$$ always increases data miners' equilibrium search intensity $$\tau^*$$, raising capital allocated to quants ($$\mu^*$$), average signal quality, and price informativeness | Proposition 4, p. 227 | $$\partial \tau^* / \partial c < 0$$; $$\tau^*$$ converges to $$\tau_{dm}^{\text{max}}$$ as $$c \to 0$$; capital to data miners $$\mu^* = \Gamma(\tau^*)$$ increases with $$\tau^*$$ |
| R4 | A larger data frontier ($$\tau_{dm}^{\text{max}}$$) reduces data miners' search intensity $$\tau^*$$ and capital allocated to quants ($$\mu^*$$) once $$\tau_{dm}^{\text{max}}$$ exceeds a threshold $$\tau^{tr}(c)$$, because the price informativeness effect dominates the hidden gold-nugget effect | Proposition 5, p. 227 | Threshold $$\tau^{tr}(c)$$ exists for all $$c > 0$$; for $$\tau_{dm}^{\text{max}} > \tau^{tr}(c)$$: $$\partial \tau^* / \partial \tau_{dm}^{\text{max}} < 0$$ and $$\partial \mu^* / \partial \tau_{dm}^{\text{max}} < 0$$ |
| R5 | Despite reducing quant search intensity when $$\tau_{dm}^{\text{max}}$$ is large, a push back of the data frontier always raises average signal quality $$\bar{\tau}$$ and therefore price informativeness $$\mathcal{I}$$; price informativeness is bounded above as $$\tau_{dm}^{\text{max}} \to \infty$$ | Proposition 5, p. 227 | $$\partial \mathcal{I} / \partial \tau_{dm}^{\text{max}} > 0$$ always; $$\mathcal{I}$$ bounded above as $$\tau_{dm}^{\text{max}} \to \infty$$ (Assumption 1 + proof) |
| R6 | Asset managers' average gross excess return is hump-shaped in search costs $$c$$ and in the data frontier $$\tau_{dm}^{\text{max}}$$; the big data revolution is predicted to first raise, then reduce, average active management performance | Corollary 1, Figure 3, pp. 232-233 | $$\mathbb{E}[\bar{R}^e(\tau)] = \frac{1}{W_0 \rho} \left( \frac{1}{\bar{\tau}} + \frac{\bar{\tau}}{\rho^2 \sigma_\omega^2 \sigma_\eta^2} \right)^{-1}$$; peaks at $$\bar{\tau} = \rho \sigma_\omega \sigma_\eta$$; hump-shaped in $$c$$ and $$\tau_{dm}^{\text{max}}$$ |
| R7 | In the fee extension (Nash bargaining, $$\kappa > 0$$), data miners charge no rents; experts' fees are set by their scarcity and decline when data miners' search intensity rises, whether from lower $$c$$ or a data-frontier increase that raises $$\tau^*$$ | Corollary 6, Section VI, eq. 39-41, pp. 237-238 | $$f_{dm}^* = 0$$; $$f_{ex}^*(\tau) = \kappa(w(\tau) - w(\tau^*))$$; experts' fees decline with a fall in $$c$$ and decline (for low-skill experts) or may rise (high-skill experts) with $$\tau_{dm}^{\text{max}}$$ |

**Overall (paper's conclusion).** The two dimensions of the big data revolution, lower data-processing costs and data abundance, have the same effect on the allocation of capital to quants when $$\tau_{dm}^{\text{max}} \leq \tau^{tr}(c)$$ (both increase $$\mu^*$$) but opposite effects when $$\tau_{dm}^{\text{max}} > \tau^{tr}(c)$$ (lower $$c$$ raises $$\mu^*$$; larger $$\tau_{dm}^{\text{max}}$$ reduces $$\mu^*$$). The model predicts that the rise of quant funds driven by both forces should eventually reverse as data abundance grows, and that average active management performance is eventually eroded by greater price informativeness. Distinguishing these two dimensions of the big data revolution is therefore essential for empirical analysis.

## Theory / model

The model has four periods (Figure 1, p. 218). Period 0: investors (mass one) allocate savings $$W_0$$ to either an expert or a data miner, as in Garleanu and Pedersen (2018). Period 1: data miners conduct sequential search for a predictor. Period 2: trading occurs. Period 3: the risky asset payoff $$\omega \sim \mathcal{N}(0, \sigma_\omega^2)$$ is realized.

**Signals.** All asset managers receive a noisy signal before trading (eq. 1, p. 218):

$$
s_{\tau_i} = \omega + \tau_i^{-1/2} \varepsilon_i, \qquad \varepsilon_i \sim \mathcal{N}(0, \sigma_\omega^2) \tag{1}
$$

where $$\tau_i$$ is signal precision ("quality"). Experts' skill $$\tau$$ is fixed and drawn from cumulative distribution $$\Gamma(\cdot)$$ (density $$\gamma(\cdot)$$) on $$[0, \tau_{ex}^{\text{max}}]$$. Data miners discover their predictor through search: each round costs $$c$$ and yields a precision draw $$\tau \sim \Phi(\cdot)$$ on $$[0, \tau_{dm}^{\text{max}}]$$ (eq. 2, p. 219):

$$
\Phi(\tau) = \Pr(\tilde{\tau} \leq \tau) = \frac{\Psi(\tau)}{\Psi(\tau_{dm}^{\text{max}})}, \qquad \tau \in [0, \tau_{dm}^{\text{max}}] \tag{2}
$$

The data frontier $$\tau_{dm}^{\text{max}}$$ captures the maximum attainable signal precision from available data sets; higher $$\tau_{dm}^{\text{max}}$$ reflects data abundance. A data miner with stopping threshold $$\tau_i^*$$ stops when her draw exceeds $$\tau_i^*$$, so the likelihood of stopping in a given round is:

$$
\Lambda(\tau_i^*; \tau_{dm}^{\text{max}}) \equiv \Pr(\tau \in [\tau_i^*, \tau_{dm}^{\text{max}}]) = 1 - \Phi(\tau_i^*) \tag{3}
$$

A higher $$\tau_i^*$$ means more demanding search (fewer stops per round on average), so $$\tau^*$$ is called the "search intensity."

**Capital allocation.** Let $$\mu$$ denote the fraction of investor capital allocated to data miners. Investors observe experts' skills and anticipate data miners' search strategy. They optimally allocate to experts with skill $$\tau \geq \underline{\tau}$$ (the marginal expert) until each expert is at capacity. The rest goes to data miners. In a stable interior equilibrium (Proposition 3, eq. 8, p. 222):

$$
\mu^* = \Gamma(\tau^*) \tag{8}
$$

where $$\tau^*$$ is data miners' equilibrium search intensity, and the marginal expert skill equals $$\tau^*$$.

**Trading.** The market for the risky asset is as in Vives (1995): noise traders with aggregate demand $$\eta \sim \mathcal{N}(0, \sigma_\eta^2)$$ trade alongside asset managers. Price informativeness is measured by the inverse of residual payoff variance, following Grossman and Stiglitz (1980) and Verrecchia (1982). Risk-neutral dealers post a price equal to their expectation of the payoff conditional on aggregate demand (eq. 4, p. 221):

$$
p^* = \mathbb{E}[\omega \mid D(p^*)] \tag{4}
$$

Asset managers have constant absolute risk aversion $$\rho$$. Asset manager $$i$$ returns to her client (eq. 5, p. 221):

$$
W_{i,j} = W_0 + x_i(s_{\tau_i}, p)(\omega - p) - (n_i c)\mathbb{1}_{\{j=dm\}} \tag{5}
$$

where $$n_i$$ is the number of search rounds conducted. Investor utility from trading with an expert of skill $$\tau$$ is (eq. 6, p. 221):

$$
H(\tau) = \mathbb{E}\left[ -\exp\left( -\rho(W_0 + x_i(s_{\tau_i}, p)(\omega - p)) \right) \right] \tag{6}
$$

and investor utility from trading with a data miner of search intensity $$\tau_i^*$$ is (eq. 7, p. 221):

$$
V(\tau_i^*) = \underbrace{\mathbb{E}\left[ -\exp\left(-\rho(W_0 + x_i(s_{\tau_i}, p)(\omega - p))\right) \right]}_{\text{Expected utility from trading}} \times \underbrace{\mathbb{E}\left[\exp(\rho(n_i c))\right]}_{\text{Expected utility cost of exploration}} \tag{7}
$$

## Method

The paper characterizes the equilibrium in three steps.

**Step 1: Trading equilibrium (Proposition 1, p. 223).** Taking $$\tau^*$$ (and hence $$\mu^*$$) as given, the paper solves for the trading equilibrium. In equilibrium, each asset manager's demand is proportional to her signal minus the price (eq. 11):

$$
x^*(s_\tau, p) = \beta(\tau)(s_\tau - p), \qquad \beta(\tau) = \frac{\tau}{\rho \sigma_\omega^2} \tag{11}
$$

The equilibrium price (eq. 12) is:

$$
p^* = \mathbb{E}[\omega \mid D(p^*)] = \lambda(\tau^*)\xi, \qquad \xi \equiv \omega + \rho \sigma_\omega^2 \bar{\tau}(\tau^*; \tau_{dm}^{\text{max}})^{-1} \eta \tag{12}
$$

where $$\bar{\tau}(\tau^*; \tau_{dm}^{\text{max}})$$ is the average signal quality across all asset managers and $$\lambda(\tau^*)$$ is defined in eq. 13. Price informativeness is (eq. 14, p. 224):

$$
\mathcal{I}(\tau^*; \tau_{dm}^{\text{max}}) \equiv \text{Var}[\omega \mid p^*]^{-1} = \frac{1}{\sigma_\omega^2} + \frac{\bar{\tau}(\tau^*; \tau_{dm}^{\text{max}})^2}{\rho^2 \sigma_\omega^4 \sigma_\eta^2} \tag{14}
$$

**Step 2: Equilibrium data mining (Proposition 2, p. 225).** The trading value of a signal of quality $$\tau$$ is (Lemma 2, eq. 16, p. 224):

$$
g(\tau, \tau^*) = -\left(1 + \frac{\tau}{\sigma_\omega^2 \mathcal{I}(\tau^*; \tau_{dm}^{\text{max}})}\right)^{-\frac{1}{2}} \tag{16}
$$

A data miner's continuation value after finding and then rejecting a predictor of quality $$\hat{\tau}_i$$ is (eq. 17-18, pp. 224-225):

$$
J(\hat{\tau}_i, \tau^*) = \frac{\exp(\rho c) \Lambda(\hat{\tau}_i; \tau_{dm}^{\text{max}})}{1 - \exp(\rho c)(1 - \Lambda(\hat{\tau}_i; \tau_{dm}^{\text{max}}))} \times \mathbb{E}_\phi\left[g(\tau, \tau^*) \mid \hat{\tau}_i \leq \tau \leq \tau_{dm}^{\text{max}}\right] \tag{18}
$$

In a symmetric equilibrium, $$\tau^*$$ solves $$g(\tau^*, \tau^*) = J(\tau^*, \tau^*)$$, which reduces to (eq. 21, p. 225):

$$
F(\tau^*) = \exp(-\rho c), \tag{21}
$$

where

$$
F(\tau^*) \equiv \int_{\tau^*}^{\tau_{dm}^{\text{max}}} r(\tau, \tau^*)\phi(\tau)d\tau + (1 - \Lambda(\tau^*; \tau_{dm}^{\text{max}})), \qquad r(\tau, \tau^*) \equiv \left(\frac{\tau^* + \sigma_\omega^2 \mathcal{I}(\tau^*; \tau_{dm}^{\text{max}})}{\tau + \sigma_\omega^2 \mathcal{I}(\tau^*; \tau_{dm}^{\text{max}})}\right)^{\frac{1}{2}} \tag{22-23}
$$

Proposition 2 establishes that this equation has a unique solution $$\tau^* \in (0, \tau_{dm}^{\text{max}})$$ whenever $$F(0) < \exp(-\rho c)$$.

**Step 3: Full equilibrium (Proposition 3, p. 226).** Combining Steps 1 and 2 with the capital-allocation condition $$\mu^* = \Gamma(\tau^*)$$ (eq. 8) yields the full equilibrium characterization. The model is solved analytically under the parameterization $$\Phi(\tau) = \frac{1-(1+\tau)^{-3/2}}{1-(1+\tau_{dm}^{\text{max}})^{-3/2}}$$ and $$\Gamma(\tau) = 1-(1+\tau)^{-3/2}$$ for numerical illustrations (Figure 2, p. 230).

The decomposition of the data-frontier effect (eq. A26, p. 250 Appendix; related text at eq. 25, pp. 228-229) separates the hidden gold-nugget effect (a larger $$\tau_{dm}^{\text{max}}$$ raises the value of the best possible predictor) from the price informativeness effect (more data raises $$\mathcal{I}$$, reducing the value of any given signal). The second term captures the price informativeness effect:

$$
\frac{\partial F}{\partial \tau_{dm}^{\text{max}}} = \underbrace{\phi(\tau_{dm}^{\text{max}})(r(\tau_{dm}^{\text{max}}, \tau^*) - \mathbb{E}_\phi[\min\{1, r(\tau, \tau^*)\}])}_{<0: \text{Gold Nugget Effect}} + \underbrace{\left(\int_{\tau^*}^{\tau_{dm}^{\text{max}}} \frac{\partial r(\tau, \tau^*)}{\partial \mathcal{I}} \phi(\tau)d\tau\right) \frac{\partial \mathcal{I}}{\partial \tau_{dm}^{\text{max}}}}_{>0: \text{Informativeness Effect}} \tag{26}
$$

When $$\tau_{dm}^{\text{max}}$$ is large enough, the positive informativeness effect dominates, so $$\partial F / \partial \tau_{dm}^{\text{max}} > 0$$ and $$\tau^*$$ decreases with $$\tau_{dm}^{\text{max}}$$ (Proposition 5).

## Empirical specifications

This is a pure theory paper. It derives no estimating equations and runs no regressions. The empirical implications are summarized in Table I (p. 243), which characterizes the directional effects of lower search costs ($$c \searrow$$) and data abundance ($$\tau_{dm}^{\text{max}} \nearrow$$) on:

- Allocation of capital to data miners ($$\mu^*$$): increases with lower $$c$$; hump-shaped in $$\tau_{dm}^{\text{max}}$$
- Price informativeness ($$\mathcal{I}$$): always increases with both shocks
- Average signal quality ($$\bar{\tau}$$): always increases with both shocks
- Data miners' relative performance ($$RP$$): increases with $$\tau_{dm}^{\text{max}}$$ (Corollary 4); ambiguous with lower $$c$$
- Within-group performance dispersion ($$\Delta R_\alpha$$): decreases with lower $$c$$; increases with $$\tau_{dm}^{\text{max}}$$ above threshold (Corollaries 2-3)
- Average performance ($$\mathbb{E}[\bar{R}^e]$$): hump-shaped in both $$c$$ and $$\tau_{dm}^{\text{max}}$$ (Corollary 1)

Section VII (pp. 242-244) suggests three types of empirical tests: (i) cross-sectional variation in quant and discretionary fund holdings to capture differential exposure to alternative data (shocks to $$\tau_{dm}^{\text{max}}$$), exploiting the finding of Abis (2022) that quant funds grew from 6.1% to 18.6% of U.S. equity AUM between 2000 and 2017; (ii) regulatory changes that reduce information processing costs (e.g., the SEC's XBLR mandate lowering $$c$$ for IT-intensive funds, consistent with evidence from Zhao (2021) that this mandate reduced the performance gap between quant and discretionary funds); and (iii) the introduction of cloud computing (e.g., Amazon Web Services in 2006) as shocks to $$c$$. Measurement of signal quality $$\tau$$ follows Proposition 1: the theoretical coefficient from regressing a fund's holdings $$x^*(s_\tau, p^*)$$ on $$\omega - p^*$$ is $$\beta(\tau) = \tau / (\rho \sigma_\omega^2)$$ (eq. 45, p. 244), which is strictly positive for informed managers and increases with skill. The paper also relates to evidence from Pastor, Stambaugh, and Taylor (2015) that the size of the active management industry is negatively related to funds' performance. Han and Sangiorgi (2018) and Banerjee and Breon-Drish (2021) model information acquisition as search but analyze different questions; the key distinction here is the simultaneous variation in both the intensive and extensive margins. Stambaugh (2020) documents a related result that improved manager skills reduce average performance, which the model endogenizes through the price informativeness channel.

## Datasets used

This paper uses no empirical datasets. All results are derived analytically from the theoretical model. Numerical illustrations use the parametric family $$\Phi(\tau) = \frac{1-(1+\tau)^{-3/2}}{1-(1+\tau_{dm}^{\text{max}})^{-3/2}}$$ and $$\Gamma(\tau) = 1-(1+\tau)^{-3/2}$$, with calibrated values for $$\rho$$, $$\sigma_\omega$$, $$\sigma_\eta$$, $$W_0$$, and $$c$$ (Figures 2-6, pp. 230-239).

| Dataset | Role in paper | Wiki page |
|---|---|---|
| No empirical data used | Theory paper only | n/a |

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13397) if you are: building a model of quant fund behavior in equilibrium; studying the welfare effects of the big data revolution on price efficiency and active management; looking for testable predictions on the cross-sectional variation in fund performance as a function of data availability; or extending the model to allow learning about signal quality (fn. 10, p. 220) or non-extreme decreasing returns to scale (Section II.E, Internet Appendix). The appendix (pp. 245-252) contains the full proofs of all propositions.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY-NC 4.0 licence permits sharing with attribution for non-commercial purposes; the verbatim PDF is not hosted in this batch.

> **Citation.** Dugast, Jérôme, and Thierry Foucault.
> "Equilibrium Data Mining and Data Abundance."
> *The Journal of Finance* 80, no. 1 (February 2025): 211-258.
> DOI: 10.1111/jofi.13397. CC BY-NC 4.0.
> This page is an extract by the Institute for Automated Research: core results
> re-expressed for research reference; **changes were made**.
