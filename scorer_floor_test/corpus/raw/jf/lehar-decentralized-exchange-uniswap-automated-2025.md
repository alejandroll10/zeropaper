---
title: "Decentralized Exchange: Lehar & Parlour (2025)"
description: >-
  Distilled: Lehar and Parlour build a theoretical model of Uniswap's
  automated market maker (AMM), characterize equilibrium liquidity-pool size
  as a trade-off between fee revenue and adverse-selection (picking-off) risk,
  and show empirically that AMM pools are larger when volatility is lower and
  uninformed trading is higher, that AMM liquidity is more stable than limit-order
  book liquidity during extreme market events, and that Uniswap price impact is
  lower than Binance for low-volatility tokens. J. Finance 2025, paywalled.
  Four core results with source locators, datasets used, the model (constant-product
  AMM + limit-order-book comparison), and the estimating specifications.
sidebar:
  label: Lehar-Parlour 2025
  order: 1
tags: [paper-summary, market-microstructure, defi, decentralized-exchange, automated-market-maker,
       liquidity-provision, cryptocurrency, peer-reviewed, unreplicated,
       data:uniswap-blockchain]
paper:
  authors: Alfred Lehar, Christine A. Parlour
  authorList:
    - { family: Lehar, given: Alfred, orcid: "0000-0002-0806-1129", affiliation: Haskayne School of Business, University of Calgary }
    - { family: Parlour, given: Christine A., affiliation: Haas School of Business, UC Berkeley }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 321-374
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13405
  jel:
    codes: [G12, G14, G23]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Financial Markets and Investment Strategies", "Complex Systems and Time Series Analysis", "Credit Risk and Financial Regulations"]
  dataAccess: public
  outcome:
    - liquidity pool size on Uniswap
    - relative price impact of AMM vs. limit order book
    - liquidity stability during extreme market events
    - gas fees and fee revenue during price volatility
  outcomeClass: [market-microstructure, asset-prices]
  license: "Paywalled; Wiley VOR terms (http://onlinelibrary.wiley.com/termsAndConditions#vor); copyright 2024 the American Finance Association"
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Wiley/Journal of Finance site; confirmed 2026-06-06)"
  redistribution: extract-only
  resultsCount: 4
  citedByCount: 88
  methods:
    role: both
    contributes: amm-equilibrium-pool-size
    family: structural
    buildsFrom: [panel-regression, gmm]
    identification: descriptive
  contributionType: [new-theory, new-fact]
  mechanisms: [information-asymmetry, liquidity, search-frictions]
  scope:
    region: global (Ethereum blockchain)
    assetClass: cryptocurrency token pairs
    period: 2018-11..2022-12
    frequency: mixed
    dataType: [market, other]
    granularity: [transaction, security]
    n: "95.8 million Uniswap interactions; 105,098 liquidity pools; 1,525 pools in reduced econometric sample"
  findings:
    - ref: R1
      outcome: liquidity pool size on Uniswap
      metric: coefficient
      value: "Std.Dev FX Rate: -0.152*** to -0.249*** across 6 specs (col 1: -0.201*** se 0.0419; col 2: -0.249*** se 0.0499; col 6: -0.152*** se 0.0484); Reversals: 49.18*** (13.68); Number Trades: 6.633*** (2.088); R2=0.21-0.55"
      direction: negative
      vsBenchmark: volatility reduces pool size; uninformed trading (reversals, trade count) raises it (Table II, p. 341)
    - ref: R2
      outcome: liquidity stability during extreme market events
      metric: probability
      value: "Only 2% of liquidity withdrawn during 41% ETH price drop (May 19, 2021); 17% of liquidity withdrawn in the extreme event overall; gas fees spike 1.71 USD (10%) on high-return days; fee revenue rises 17.7 USD per day on high-return days"
      direction: positive
      vsBenchmark: AMM liquidity far more stable than limit-order-book liquidity during flash-crash-type events (Table III, p. 344; Figure 9, p. 343)
    - ref: R3
      outcome: relative price impact of AMM vs. limit order book
      metric: coefficient
      value: "rPI intercept significant and positive (col 1: 4.080***; col 2: 4.956***; col 3: 3.126***; col 8: 3.963***); Pancake Swap dummy: -2.497*** to -3.085*** across pool-FE specs; Std.Dev FX Rate negative and significant; Reversal Volume positive and significant"
      direction: negative
      vsBenchmark: "Binance price impact higher than Uniswap on average; gap narrows after Binance integrates PancakeSwap (AMM clone) in March 2022 (Table IV, p. 352)"
    - ref: R4
      outcome: relative price impact of AMM vs. limit order book
      metric: coefficient
      value: "Relative volatility rV: Pancake Swap dummy -7.756*** (col 9) to -18.16*** (col 8); intercept col 1: 33.95***; col 2: 39.00***; col 8: 30.47***; col 9: 25.91***; R2=0.416-0.677"
      direction: positive
      vsBenchmark: "Price impact more volatile on Binance than Uniswap; volatility gap drops significantly after PancakeSwap integration (Table V, p. 353)"
  resultType: new-finding
  relatesTo:
    - { cite: "Glosten (1994)", doi: '10.1111/j.1540-6261.1994.tb02450.x', relation: builds-on, note: "Limit-order-book equilibrium framework with adverse selection; AMM differs by pro rata payoff sharing and no strategic pricing" }
    - { cite: "Capponi and Jia (2021)", relation: tests, note: "Model of AMM with competition among arbitrageurs; Lehar-Parlour focus on liquidity supply side and pool-size equilibrium" }
    - { cite: "Angeris and Chitra (2020)", doi: '10.1145/3419614.3423251', relation: builds-on, note: "General framework showing constant-function market makers can reflect true prices and bound minimum value" }
    - { cite: "Barbon and Ranaldo (2021)", relation: extends, note: "Compares transaction costs on DEX and Binance for five token pairs; Lehar-Parlour provide more extensive data across many tokens" }
    - { cite: "Biais, Foucault, and Moinas (2015)", relation: cites, note: "High-frequency trading and externalities in market competition" }
  openQuestions:
    - "The model is single period and does not speak to pool dynamics; multiple-period or dynamic extensions would be needed to fully characterize intertemporal liquidity provision strategies (p. 343, conclusion)."
    - "Tokens traded on a CEX vs. a DEX differ in custody risk and DeFi usability, making a complete welfare comparison between AMM and limit-order-book trading venues difficult; comprehensive gas-fee accounting is not included in the model (pp. 347-348)."
    - "The analysis focuses on Uniswap V1 and V2; the concentrated-liquidity V3 protocol introduced in 2021 would require an extended framework (implicit throughout; V3 not analyzed)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-06", role: extracted, note: "Full PDF read (pp. 321-374 plus appendices); four results extracted from Tables II-V and Figures 9, 13. Model equations from Sections I-II and Appendix A. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: "2026-06-06", role: verified, note: "Locators and reported magnitudes re-checked against source PDF; equations (1)-(5), (16)-(20), Propositions 1-5 all confirmed correct term-by-term; fixed R1 Std.Dev FX Rate range (was -0.201 to -0.249, correct full-range is -0.152 to -0.249 across all 6 specs per Table II); fixed R3 Pancake Swap range (was -2.963 to -3.085, corrected to -2.497 to -3.085 per Table IV); fixed R4 intercept and Pancake ranges to include all columns per Table V; corrected observation counts for R3/R4 specs (24,963 in full-sample col vs. 24,224 with pancake dummy); all other locators, magnitudes, signs, and significance stars confirmed." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13405", checked: "2026-06-06", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-20; no CC licence found; copyright 2024 the American Finance Association (PDF p. 321)" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model (constant-product AMM and limit-order-book comparison), and the empirical specifications: enough to know what it found and how, without reading the full 54-page paper. To replicate or extend, read the original at [doi.org/10.1111/jofi.13405](https://doi.org/10.1111/jofi.13405).

This paper builds on Glosten (1994), the canonical model of limit-order-book efficiency under adverse selection, and extends the comparison to AMMs. It tests against Capponi and Jia (2021), who model AMM competition among arbitrageurs. It also draws on Angeris and Chitra (2020), who show constant-function market makers can reflect true prices. The empirical price-impact results complement Barbon and Ranaldo (2021), who compare DEX and Binance transaction costs for five token pairs. The analysis of HFT and strategic liquidity provision relates to Biais, Foucault, and Moinas (2015).

## TL;DR

Lehar and Parlour analyze Uniswap, the largest decentralized exchange, as a new model of liquidity provision. In an automated market maker (AMM), liquidity suppliers passively post capital into pools rather than actively setting prices; price impact is determined mechanically by a bonding curve. The paper develops a model showing that equilibrium pool size trades off fee revenue against picking-off risk: pools are larger when token volatility is lower and noise trading is higher. Using 95.8 million Uniswap transactions from November 2018 to December 2022 across 105,098 liquidity pools, the paper finds that (i) pool size decreases in volatility and increases in uninformed trading, consistent with theory; (ii) AMM liquidity is substantially more stable than limit-order-book liquidity during extreme market events; (iii) price impact on Uniswap is lower than on Binance (a centralized exchange) for low-volatility, noise-dominated tokens; and (iv) Binance price impact becomes less volatile and converges toward Uniswap after integrating PancakeSwap, an AMM clone, in March 2022. The paper also shows conditions under which the AMM dominates a limit-order market and documents absence of long-lived arbitrage opportunities.

## Core results

Magnitudes as reported; `\*\*\*` = 1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Pool size decreases in volatility and increases in uninformed trading** | Table II, p. 341 | Std.Dev FX Rate coefficient: -0.152\*\*\* to -0.249\*\*\* across 6 specs (col 1: -0.201; col 2: -0.249; col 3: -0.204; col 4: -0.163; col 5: -0.158; col 6: -0.152); Reversals: 49.18\*\*\* (13.68); Number Trades: 6.633\*\*\* (2.088); R2 = 0.21-0.55 |
| R2 | **AMM liquidity is stable during extreme market events**; gas fees and fee revenue both increase, discouraging withdrawal | Table III, p. 344; Figure 9, p. 343 | Only 2% of ETH-stablecoin liquidity withdrawn during 41% ETH price crash (May 19, 2021); gas fees rise 1.71 USD (10%) and fee revenue rises 17.7 USD on high-return days |
| R3 | **Uniswap price impact is lower than Binance** on average; gap narrows after Binance integrates AMM clone PancakeSwap | Table IV, p. 352 | rPI intercept significant and positive across cols (col 1: 4.080\*\*\*; col 2: 4.956\*\*\*; col 3: 3.126\*\*\*; col 8: 3.963\*\*\*); Pancake Swap dummy -2.497\*\*\* to -3.085\*\*\* across pool-FE specs; effect stronger at low volatility and medium trade sizes |
| R4 | **Price impact is more volatile on Binance than Uniswap**; volatility gap drops after PancakeSwap integration | Table V, p. 353 | Relative volatility rV intercept: col 1: 33.95\*\*\*; col 2: 39.00\*\*\*; col 8: 30.47\*\*\*; col 9: 25.91\*\*\*; Pancake Swap dummy: col 1: -13.63\*\*\*; col 8: -18.16\*\*\*; col 9: -7.756\*\*\*; pattern holds for low exchange-rate volatility and medium trade sizes |

**Overall (paper's conclusion).** Uniswap's AMM mechanism successfully provides stable, predictable liquidity at lower and less volatile price impact than a centralized limit-order book for asset pairs with lower volatility and more noise trading. The equilibrium pool size adjusts so that fee revenue compensates liquidity suppliers for adverse selection, and gas fees on the blockchain act as a commitment device that discourages strategic withdrawal during market turmoil.

## Theory / model

The model has a single asset with current value $$p_0$$. With probability $$\alpha$$, an innovation occurs and the value jumps to $$p_0 + \sigma$$ or $$p_0 - \sigma$$ with equal probability; otherwise the value remains at $$p_0$$. Three agents interact: risk-neutral liquidity suppliers, a liquidity demander (noise trader) who trades a fixed quantity $$q$$, and an informed arbitrageur who trades whenever profitable.

**Constant-product bonding curve.** For a pool with $$E_0$$ units of ETH and $$T_0$$ tokens, the bonding curve constant is (eq. 1, p. 326):

$$
k := T_1 \cdot E_1 = T_0 \cdot E_0. \tag{1}
$$

Any trade must stay on this curve. When a trader buys $$t$$ tokens by depositing $$e$$ ETH, the fee $$\tau$$ is collected, the post-trade ETH pool becomes $$E' = E + (1-\tau)e$$, and the post-trade token balance is (eq. 2, p. 327):

$$
T' = \frac{T \cdot E}{E'} = \frac{T \cdot E}{E + (1-\tau)e}. \tag{2}
$$

The token received by the trader is $$t = T - T'$$ (eq. 3), and the terms of trade in ETH per token are (eq. 4):

$$
p^{tot} = \frac{e}{t} = \frac{e}{T} + \frac{E}{(1-\tau)T}. \tag{4}
$$

In the limit as $$e \to 0$$, the spread relative to the fundamental $$p_0$$ is:

$$
\lim_{e \to 0} \frac{p^{tot}}{p_0} = \frac{ET}{ET(1-\tau)} = \frac{1}{1-\tau}. \tag{5}
$$

**Limit-order-book equilibrium.** Competing liquidity suppliers choose private investment $$\gamma_i$$ (e.g., co-location speed) at cost $$I(\gamma) = a\gamma^2$$ to become the monopolist with probability $$\gamma_i(1 - \gamma_j)$$. In symmetric equilibrium (Proposition 1, p. 330):

$$
\gamma^* = \frac{(1-\alpha)\sigma q}{2a + \sigma q(1-\alpha)}.
$$

A monopolist posts at $$p_0 + \sigma$$ (sell) and $$p_0 - \sigma$$ (buy), earning $$(1-\alpha)\sigma$$. With two competing suppliers, each earns zero and prices are $$p_0 + \alpha\sigma$$ and $$p_0 - \alpha\sigma$$ (Lemma 2, p. 330).

**AMM equilibrium pool size.** In the AMM, liquidity provision is non-rivalrous and payoffs are shared pro rata. There is no incentive for private investment. The equilibrium pool size (Proposition 2, p. 333, eq. 16) balances fee revenue from the noise trader against picking-off losses from the arbitrageur:

$$
T_0 = q \left[ \sqrt{1 + \frac{(1-\alpha)^2 \tau^2 p_0^2}{\alpha^2 \omega^2}} - \frac{(1-\alpha)\tau p_0}{\alpha \omega} \right], \tag{16}
$$

where $$\omega = \sqrt{p_0(p_0+\sigma)(1+\tau)} + \sqrt{\frac{p_0(p_0-\sigma)}{1+\tau}} - 2p_0$$. The equilibrium pool size is linear in noise-trade volume $$q$$, decreasing in innovation size $$\sigma$$, and decreasing in innovation probability $$\alpha$$ (Proposition 3, p. 339).

**AMM vs. limit-order-book trading costs.** Expected cost per unit on the limit-order book is (Proposition 4, p. 345):

$$
E(c^{\text{limit}}) = \sigma((1-\eta)\alpha + \eta),
$$

where $$\eta = 2\gamma^*(1-\gamma^*)$$ is the probability of facing a monopolist. Expected cost on the AMM is:

$$
E(c^{\text{AMM}}) = p_0 \left(\frac{(1+\tau)\lambda^b - (1-\tau)\lambda^s}{2}\right),
$$

where $$\lambda^b(\tau, \alpha, \sigma) > 1$$ and $$\lambda^s(\tau, \alpha, \sigma) < 1$$ are functions of equilibrium pool size. Proposition 5 shows the limit-order book does not universally dominate the AMM: there exists a critical innovation probability $$\alpha^*$$ below which the AMM is strictly preferred, and conditional on trade quantity, price impact is more volatile in the limit-order book.

## Method

The paper combines a stylized two-market equilibrium model with reduced-form panel regressions.

**Structural model.** Equilibrium is derived analytically for both markets. The AMM equilibrium pool size (equation 16) is the closed-form solution to the indifference condition in equation (A10) (Appendix A, p. 358). The model builds on the `amm-equilibrium-pool-size` framework, which is the paper's primary methodological contribution.

**Panel regressions for pool size (R1).** The estimating equation (eq. 17, p. 340) is at the pool-day level:

$$
\text{pool size} = a + b_1 \sigma_{fx} + b_2 \mathbf{1}_{\text{airdrop}} + b_3 \text{noise trading}, \tag{17}
$$

where pool size is daily average USD pool size, $$\sigma_{fx}$$ is the annualized block-by-block exchange-rate volatility (proxy for adverse selection), and noise trading is measured by three proxies: number of trades per day, daily volume, and immediate trade reversals (trades followed within 75% of the same size in the opposite direction). Standard errors are clustered by pool and by day. Robustness: specifications with and without pool-and-day fixed effects.

**Price impact comparison (R3, R4).** Relative price impact is defined as (eq. 18, p. 350):

$$
rPI = \frac{PI_{\text{Binance}}}{PI_{\text{Uniswap}}} - 1, \tag{18}
$$

estimated at the daily level for 43 token pairs cross-listed on both venues. The estimating equation (eq. 19, p. 350) is:

$$
rPI = a + b_1 \mathbf{1}_{\text{pancake}} + b_2 \sigma_{FX} + b_3 \text{trade size} + b_4 \text{trade size}^2 + b_5 \text{noise trading} + \epsilon. \tag{19}
$$

The PancakeSwap dummy $$\mathbf{1}_{\text{pancake}}$$ equals one after March 25, 2022 (when Binance integrated a Uniswap clone). Relative volatility of price impact is defined analogously (eq. 20, p. 351):

$$
rV = \frac{V_{\text{Binance}}}{V_{\text{Uniswap}}} - 1, \tag{20}
$$

using the same specification. Standard errors are clustered by pool and by day.

## Empirical specifications

All regressions are panel (pool-day or pool observations) with standard errors clustered by pool and by day unless noted.

**R1: Pool size and volatility/noise trading.** Pool-day level on 1,525 pools (997,507 observations). Dependent variable: daily average pool size in million USD. Key regressors: exchange-rate volatility (Std.Dev FX Rate, annualized daily sd of block-by-block price changes), airdrop dummy, and three alternative noise-trading proxies (daily USD volume, number of trades, and reversals). Six columns spanning no-FE and pool-and-day FE; R2 = 0.21-0.55 (Table II, p. 341).

**R2: Stability during extreme events.** Analyzed via Figures 9 and Table III. Gas fees and fee revenue are regressed on High Return dummy (absolute daily price change > 10%) and absolute return. Pool fixed effects. 1,303,869 observations. Gas fees rise 1.71 USD on high-return days; fee revenue rises 17.73 USD (Table III, p. 344).

**R3/R4: Relative price impact AMM vs. Binance.** 43 cross-listed token pairs; 24,963 pool-day observations in col (1) of Table IV (pool FE only, full sample without pancake dummy); 24,224 in cols with pancake dummy included; 21,409 in Table V col (1). Specifications with pool FE only and pool-and-day FE. Pre/post-PancakeSwap subsamples in columns (8) and (9) (Table IV, p. 352; Table V, p. 353).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Uniswap V1 and V2 blockchain data (Ethereum) | Primary data: 95.8 million interactions across 105,098 pools; liquidity injections, withdrawals, token swaps Nov 2018-Dec 2022 | [Uniswap on-chain](/wiki/datasets/uniswap-blockchain/) |
| Binance minute-by-minute price data | Price benchmark for USD volume conversion and price impact comparison; 43 cross-listed token pairs | No page yet |
| Ethereum blockchain gas-price data | Gas cost estimation for AMM withdrawal transactions | No page yet |

Sample: November 2, 2018 to December 21, 2022 (Uniswap V1 launch through sample end); reduced econometric sample: 1,525 pools with at least 30 trading days and 100 ETH average balance (59,606,977 observations).

## When to read the full paper

Read the original if you are: building models of AMM or decentralized exchange mechanisms; studying how blockchain-specific costs (gas fees) affect market design and liquidity stability; comparing trading costs across centralized and decentralized venues; analyzing the market-microstructure implications of DeFi protocols; or extending the model to concentrated-liquidity AMMs (Uniswap V3) or multi-pool settings. Exact tables are at pages 341 (pool size), 344 (stability), and 352-353 (price impact comparison).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1), February 2025, pp. 321-374. Copyright 2024 the American Finance Association. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled; only text extracts are reproduced here under fair-use principles.

> Lehar, Alfred, and Christine A. Parlour. "Decentralized Exchange: The Uniswap Automated Market Maker." *The Journal of Finance* 80, no. 1 (February 2025): 321-374. DOI: 10.1111/jofi.13405.
