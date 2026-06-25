---
title: "Would Order-By-Order Auctions Be Competitive: Ernst, Spatt & Sun (2025)"
description: >-
  Distilled: A theoretical model comparing brokers' routing (current U.S. equity
  market structure) to SEC-proposed order-by-order auctions for retail trades
  shows that auctions improve allocative efficiency but worsen retail investor
  welfare in illiquid stocks due to the winner's curse. J. Finance 2025,
  CC BY-NC-ND 4.0. Six core results with source locators, the model
  (inventory-cost common-value auction), and the method (linear symmetric
  equilibrium).
sidebar:
  label: Ernst-Spatt-Sun 2025
  order: 1
tags: [paper-summary, market-microstructure, market-design, auction-theory,
       retail-order-flow, equity-trading, peer-reviewed, unreplicated]
paper:
  authors: Thomas Ernst, Chester Spatt, Jian Sun
  authorList:
    - { family: Ernst, given: Thomas, orcid: "0000-0002-4687-1667", affiliation: Robert H. Smith School of Business, University of Maryland }
    - { family: Spatt, given: Chester, affiliation: Tepper School of Business, Carnegie Mellon University }
    - { family: Sun, given: Jian, orcid: "0000-0002-2782-3926", affiliation: Lee Kong Chian School of Business, Singapore Management University }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 1879-1927
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13449
  jel:
    codes: [G12, G14, G18]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Auction Theory and Applications", "Consumer Market Behavior and Pricing", "Supply Chain and Inventory Management"]
  dataAccess: public
  outcome:
    - retail investor welfare (expected equilibrium spread)
    - wholesaler (market maker) profit
    - total welfare (spread minus inventory cost)
    - allocative efficiency of order routing
  outcomeClass: [asset-prices, market-microstructure]
  license: "CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0, start 2025-05-13; artifact p.1879 states Creative Commons Attribution-NonCommercial-NoDerivs License)"
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access (Wiley via CC BY-NC-ND 4.0 VOR licence confirmed in Crossref DOI metadata 2026-06-05)"
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 3

  methods:
    role: theory
    family: theory
    buildsFrom: [search-bargaining-otc]
    contributes: brokers-routing-vs-obo-auction-model
  contributionType: [new-theory, new-fact]
  mechanisms: [information-asymmetry, market-power, liquidity]
  scope:
    region: US
    assetClass: US equities (retail order flow)
  findings:
    - ref: R1
      outcome: total welfare (spread minus inventory cost)
      metric: coefficient
      value: "W_total(1) - W_total(p) = (1-p)*(N-1)/(N+1)*c2/2 > 0 for any p < 1 (Proposition 2, p. 1889)"
      direction: positive
      vsBenchmark: order-by-order auctions always yield higher total welfare than brokers' routing
    - ref: R2
      outcome: wholesaler profit
      metric: coefficient
      value: "W_W(1) - W_W(p) = (1-p)*(c1+Nc2)/[N(1+N)] > 0 for any p < 1 (Proposition 2, p. 1889)"
      direction: positive
      vsBenchmark: wholesalers earn strictly more under order-by-order auctions than brokers' routing
    - ref: R3
      outcome: retail investor welfare (expected equilibrium spread)
      metric: coefficient
      value: "W_I(1) < W_I(p) if and only if N(N-3) > 2*c1/c2 (Proposition 2, p. 1889)"
      direction: mixed
      vsBenchmark: "investor welfare is higher under order-by-order auctions only when N is large enough and c1/c2 is low enough; otherwise brokers' routing is better for investors"
    - ref: R4
      outcome: retail investor welfare (expected equilibrium spread)
      metric: coefficient
      value: "When institutional traders have no information advantage (delta_c=0) and N_0 >= n_0, investor welfare W_I^OBO > W_I^BR; when N_0 <= n_1, W_W^BR > W_W^OBO (Proposition 6, p. 1893)"
      direction: mixed
      vsBenchmark: "investor welfare favors order-by-order auctions for large N_0; wholesaler welfare always favors brokers' routing above n_1 threshold"
    - ref: R5
      outcome: retail investor welfare (expected equilibrium spread)
      metric: coefficient
      value: "When adverse selection is severe (delta_c > delta-bar) and pi_I is in (pi_1, pi_3), investor welfare must be strictly lower under entry of institutional traders (Proposition 9, Remark 1, p. 1899)"
      direction: negative
      vsBenchmark: "institutional trader entry with information advantage reduces total liquidity providers and harms investor welfare vs. case with entry disallowed"
    - ref: R6
      outcome: allocative efficiency of order routing
      metric: coefficient
      value: "Under heterogeneous stocks (extension), equilibrium spread under brokers' routing averages over stock types; high-c0 investors are worse off and low-c0 investors are better off switching to order-by-order auctions (Lemma 4, pp. 1907-1908)"
      direction: mixed
      vsBenchmark: "cross-subsidization under brokers' routing smooths spreads across stocks; order-by-order auctions remove this cross-subsidy, creating winners and losers among retail investors"
  resultType: new-finding
  relatesTo:
    - { cite: "Easley, Kiefer & O'Hara (1996)", relation: builds-on, note: "PFOF and adverse selection in retail order routing motivate the model setup (p. 1884)" }
    - { cite: "Baldauf, Mollner & Yueshen (2024)", doi: '10.1016/j.jfineco.2024.103807', relation: builds-on, note: "retail investors less correlated than institutional traders, motivating lower adverse selection assumption (p. 1880)" }
    - { cite: "Ernst, Spatt & Sun (2024)", doi: '10.2139/ssrn.4749232', relation: extends, note: "companion empirical paper on retail liquidity programs (RLPs) showing limited bidding in volatile or illiquid markets (pp. 1882, 1886, 1909)" }
    - { cite: "Milgrom and Weber (1982)", doi: '10.2307/1911865', relation: builds-on, note: "revenue equivalence and winner's curse theory for common-value auctions underpins the comparison of ex-ante vs. ex-post competition (p. 1883)" }
    - { cite: "Bernhardt and Hughson (1997)", doi: '10.1093/rfs/10.1.69', relation: cites, note: "order splitting in the duopoly market-maker competition (p. 1884)" }
    - { cite: "Biais, Martimort and Rochet (2000)", doi: '10.1111/1468-0262.00138', relation: cites, note: "common-value auctions with multiple informed market makers (p. 1884)" }
    - { cite: "Klemperer (2018)", doi: '10.2307/j.ctv3hh4pm', relation: builds-on, note: "classical common-value auction with linear equilibrium; baseline model follows this framework (p. 1885)" }
    - { cite: "Menezes and Monteiro (2004)", doi: '10.1093/019927598x.001.0001', relation: builds-on, note: "tractable framework for common-value auctions with linear equilibrium (p. 1885)" }
    - { cite: "Dyhrberg, Shkilko and Werner (2022)", doi: '10.2139/ssrn.4313095', relation: cites, note: "retail trading volume data and market structure evidence used in empirical implications discussion (pp. 1882, 1909)" }
  openQuestions:
    - "Whether brokers could optimally bundle orders across stocks (e.g., by restricting auctions to subsets) to restore cross-subsidization and improve investor welfare; the paper shows bundling does not improve investor profit under brokers' routing (footnote 15, p. 1906)."
    - "Whether the formal model results generalize when PFOF is explicitly modeled as part of the broker's objective rather than incorporated into the combined spread metric (footnotes 3-4, pp. 1886-1887)."
    - "How the equilibrium and welfare outcomes change under realistic auction timing (100-300 ms proposed by SEC) where the NBBO may move during the auction; see Battalio and Jennings (2023) cited at p. 1886."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-05", role: extracted, note: "Read full PDF (pages 1-35); not human-verified; not reproduced. Theory paper with no empirical data; all results are propositions and lemmas derived analytically." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: "2026-06-05", role: verified, note: "Locators and reported magnitudes re-checked against source PDF; one fix applied: R5 findings[] value corrected from 'N_0 is in (pi_1, pi_3)' to 'pi_I is in (pi_1, pi_3)'; pi_I is the opportunity cost scalar in Proposition 9, not the count N_0." }
  licenceVerification:
    - { source: "Crossref REST works/10.1111/jofi.13449", checked: "2026-06-05", by: "paper-distiller (claude-sonnet-4-6)", found: "license[0]: content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-05-13T00:00:00Z. Artifact first page states: Creative Commons Attribution-NonCommercial-NoDerivs License. CC BY-NC-ND 4.0 confirmed; no redistribution or modification rights." }
---

**What this is.** This is a machine-distilled skeleton of the original paper. Read the full paper at [doi:10.1111/jofi.13449](https://doi.org/10.1111/jofi.13449) to replicate or extend the analysis.

## TL;DR

Ernst, Spatt, and Sun (2025) build a theoretical model comparing two mechanisms for executing segregated retail equity orders: the current system of brokers' routing (where retail brokers route to a wholesaler based on aggregate execution quality) and order-by-order auctions (the SEC's proposed Rule 615, where any market participant bids on each individual order). In the baseline model, order-by-order auctions always improve total welfare and wholesaler profits relative to brokers' routing because they ensure the lowest-cost market maker always gets the order (first-best allocation). However, the common-value nature of the auction amplifies the winner's curse: market makers bid conservatively because winning reveals that all rivals had higher cost signals. This reduces competition relative to brokers' routing for retail investors, particularly in illiquid stocks (where the common-value component of inventory cost is large) or when the number of bidders is small. The paper extends the model to analyze institutional trader entry, endogenous participation, alternative information structures, and cross-stock subsidization under heterogeneous stocks.

## Core results

| # | Result | Locator | Magnitude as reported |
|---|---|---|---|
| R1 | Total welfare is always higher under order-by-order auctions than brokers' routing | Proposition 2, p. 1889 | $$W_{total}(1) - W_{total}(p) = (1-p)\frac{N-1}{N+1}\frac{c_2}{2} > 0$$ for all $$p < 1$$ |
| R2 | Wholesalers earn strictly higher profits under order-by-order auctions | Proposition 2, p. 1889 | $$W_W(1) - W_W(p) = (1-p)\frac{c_1 + Nc_2}{N(1+N)} > 0$$ for all $$p < 1$$ |
| R3 | Retail investor welfare is higher under order-by-order auctions only if N is large enough or correlation is low enough | Proposition 2, p. 1889 | $$W_I(1) < W_I(p) \iff N(N-3) > 2\frac{c_1}{c_2}$$; investor welfare can go either way |
| R4 | With institutional traders (no information advantage), more institutional traders raise total and investor welfare but hurt wholesalers | Propositions 5-6, pp. 1892-1894 | $$\widetilde{W}^{OBO}_{total}$$ and $$\widetilde{W}^{OBO}_I$$ increasing in $$N_0$$; $$\widetilde{W}^{OBO}_W$$ decreasing in $$N_0$$ |
| R5 | With severe information asymmetry, institutional trader entry always leads to lower investor welfare | Proposition 9, Remark 1, p. 1899 | When $$\pi_I \in (\pi_1, \pi_3)$$ and $$\delta_c > \underline{\delta}$$: investor welfare strictly lower when institutional entry is allowed |
| R6 | Cross-subsidization under brokers' routing means heterogeneous investors have mixed welfare effects from switching to auctions | Lemma 4, pp. 1907-1908 | High-$$c_0$$ (illiquid stock) investors worse off; low-$$c_0$$ (liquid stock) investors better off under order-by-order auctions |

**Overall (paper's conclusion).** Order-by-order auctions improve allocative efficiency and total welfare, but the winner's curse leads market makers to bid conservatively, extracting more rent from retail investors. Investor welfare is lower under order-by-order auctions for illiquid stocks and when the number of participating bidders is small. The entry of informed institutional traders can further reduce competition and harm investors. Cross-subsidization under brokers' routing insulates investors in high-cost stocks, and removing it via auctions creates distributional losers among retail investor populations with illiquid holdings.

## Theory / model

The paper has no empirical estimation. All results are derived analytically from the following model.

**Theoretical antecedents.** The inventory cost structure and the common-value auction framework build on Menezes and Monteiro (2004) and Klemperer (2018), who develop tractable linear equilibria for common-value first-price auctions (p. 1885). The winner's curse logic draws on Milgrom and Weber (1982), who show that bidder profit is lower when new information is common rather than independent (p. 1883). Related prior work on competing market makers includes Bernhardt and Hughson (1997) (order splitting in duopoly) and Biais, Martimort and Rochet (2000) (common-value auctions with informed traders), both cited on p. 1884. The baseline motivation for retail order segmentation draws on Easley, Kiefer and O'Hara (1996) (PFOF and adverse selection, p. 1884) and Baldauf, Mollner and Yueshen (2024) (retail investors less correlated, p. 1880). Ernst, Spatt and Sun (2024) provide companion empirical evidence on retail liquidity programs (p. 1882).

**Setup (Section I, p. 1886).** Two dates: time 0 and time 1, no discounting. Three types: a retail investor, a broker, and $$N \geq 2$$ ex-ante identical risk-neutral wholesalers $$i \in \{1, 2, \ldots, N\}$$. The broker minimizes the bid-ask spread paid by the investor. At time 0, the broker receives a one-unit sell order and sends it to one wholesaler.

**Inventory cost (eq. 1, p. 1887):**

$$\zeta_i = c_0 + c_1 \frac{1}{N}\sum_{j=1}^{N} y_j + c_2 y_i \tag{1}$$

where $$c_0, c_1, c_2 > 0$$. The term $$c_0$$ is the unconditional expected inventory cost (common to all). The term $$c_1 \frac{1}{N}\sum_j y_j$$ is the common-value component (aggregate cost shock). The term $$c_2 y_i$$ is the private-value component. Each wholesaler $$i$$ receives i.i.d. cost shocks $$y_i \sim U[-\frac{1}{2}, \frac{1}{2}]$$.

**Information (Assumption 1, p. 1887).** Each wholesaler $$i$$ observes a noisy signal $$w_i$$ about $$y_i$$: with probability $$p$$, $$w_i = y_i$$; with probability $$1-p$$, $$w_i \sim U[-\frac{1}{2}, \frac{1}{2}]$$ (independent noise). Under brokers' routing: $$p < 1$$. Under order-by-order auctions: $$p = 1$$. The broker allocates to the wholesaler submitting the lowest spread.

**Welfare definitions (p. 1889).** Wholesaler expected profit is $$W_W(p) = \frac{p(c_1 + Nc_2)}{N(1+N)}$$. Investor expected welfare is $$W_I(p) = -\left[c_0 + p\frac{2c_1 - (N-3)Nc_2}{2N(1+N)}\right]$$. Total welfare is $$W_{total}(p) = W_W(p) + W_I(p) = -\left(c_0 - p\frac{N-1}{N+1}\frac{c_2}{2}\right)$$.

**Institutional traders extension (Section II, p. 1890).** With $$N_0 \geq 2$$ institutional traders who additionally observe $$\tilde{c}_0 \in \{c_0 - \delta_c, c_0 + \delta_c\}$$ (the common component), the inventory cost is:

$$\tilde{\zeta}_i = \tilde{c}_0 + c_1 \frac{1}{\tilde{N}}\sum_{j=1}^{\tilde{N}} y_j + c_2 y_i \tag{2}$$

where $$\tilde{N}$$ is total active market makers. The key result: when $$\delta_c > \underline{\delta}$$, institutional traders crowd out wholesalers from high-quality (low-cost, $$\tilde{c}_0 = c_0 - \delta_c$$) orders, as their lowest possible spread remains below the highest possible wholesaler spread. Market segmentation emerges: only institutional traders compete for low-cost orders, while both types compete for high-cost orders.

## Method

The paper solves for linear symmetric equilibria analytically throughout. There is no estimation.

**Equilibrium strategy (Proposition 1, p. 1888).** For any $$p \in [0,1]$$, there exists a linear symmetric equilibrium in which wholesaler $$i$$'s spread is:

$$s(w_i; p) = K_0(p) + K_1(p) w_i$$

where:

$$K_0(p) = c_0 + \frac{p}{2N}\left[c_1\left(\frac{1}{N} + \frac{N-1}{2} - \frac{1}{2}\right) + c_2\right]$$

$$K_1(p) = \frac{N-1}{N} p \left[c_1\left(\frac{1}{2} + \frac{1}{N}\right) + c_2\right]$$

The intercept $$K_0(p)$$ is the equilibrium spread when $$w_i = 0$$ (no private signal); the slope $$K_1(p)$$ captures the responsiveness to the signal. At $$p = 1$$ (order-by-order auctions), the slope is maximized: heterogeneous bids create more rent for market makers. At $$p \to 0$$ (no signal), all spreads converge and competition intensifies.

**Winner's curse intuition.** The common-value component $$c_1 \frac{1}{N}\sum_j y_j$$ is the same for all market makers. Winning the auction reveals that all rivals had higher signals (i.e., higher cost shocks), making the common value worse for the winner than the unconditional expectation. This winner's curse is proportional to $$\frac{c_1}{c_2}$$: when the common component is large relative to the private component, the winner's curse is severe, market makers shade bids more conservatively, and investor welfare deteriorates.

**Equilibrium with institutional traders (Propositions 4 and 7).** With no information advantage ($$\delta_c = 0$$), replacing $$N$$ by $$N + N_0$$ in Proposition 1 gives the equilibrium. With severe information advantage ($$\delta_c > \underline{\delta}$$), the equilibrium features two distinct bidding strategies: institutional traders use $$\tilde{s}^+(y;\delta_c)$$ for high-cost orders and $$\tilde{s}^-(y;\delta_c)$$ for low-cost orders, while wholesalers use $$\tilde{s}^+(y;\delta_c)$$ only (they are outbid on low-cost orders regardless of their signal).

**Heterogeneous stocks extension (Proposition 15, p. 1906).** Under brokers' routing with a distribution $$G(c_0, c_1, c_2)$$ of stock characteristics, wholesalers compete before observing individual order characteristics, so they submit a single equilibrium strategy using average characteristics $$(\bar{c}_0, \bar{c}_1, \bar{c}_2)$$ as arguments in the $$K_0, K_1$$ formulas. Under order-by-order auctions, characteristics are observed and the Proposition 1 equilibrium applies order-by-order. This generates cross-subsidization: brokers' routing taxes liquid (low-cost) stocks to subsidize illiquid (high-cost) stocks.

## Empirical specifications

This paper is purely theoretical. There are no regressions, no data, and no calibration exercises. Section IV (pp. 1908-1909) discusses empirical implications and qualitative consistency with related empirical findings (Ernst, Spatt, and Sun (2024); Dyhrberg, Shkilko, and Werner (2022)), but no formal empirical test is conducted.

The key comparative statics are:

- Total welfare difference: $$W_{total}(1) - W_{total}(p) = (1-p)\frac{N-1}{N+1}\frac{c_2}{2}$$, increasing in the private-value share $$c_2$$ and in $$N$$ (Proposition 2).
- Investor welfare favors order-by-order auctions iff $$N(N-3) > 2\frac{c_1}{c_2}$$, i.e., the number of bidders is large and the common-value fraction $$\frac{c_1}{c_2}$$ is small (Proposition 2).
- With endogenous entry under severe adverse selection (Proposition 9): allowing institutional trader entry leads to weakly fewer total liquidity providers and strictly lower investor welfare when both wholesalers and institutional traders coexist in equilibrium.
- Cross-subsidization threshold (Lemma 4): investors with order characteristics $$c_0 > \bar{c}_0$$ (illiquid stocks), $$c_1 > \bar{c}_1$$, or $$c_2 < \bar{c}_2$$ (when $$N > 3$$) are worse off switching from brokers' routing to order-by-order auctions.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| None | Theory paper; no data used | n/a |

The paper's empirical discussion references Dyhrberg, Shkilko, and Werner (2022) (SEC 605 reports on retail vs. institutional volume) and Ernst, Spatt, and Sun (2024) (retail liquidity program bidding data), but neither dataset is used in this paper's analysis.

## When to read the full paper

Read Ernst, Spatt, and Sun (2025) if you are:
- Studying the theoretical welfare implications of the SEC's Rule 615 (order-by-order auction) proposal for retail equity order flow.
- Interested in the interplay of common-value auctions, winner's curse, and market competition in financial market design.
- Analyzing cross-subsidization effects in brokers' routing and how they affect heterogeneous retail investors with different portfolio compositions.
- Working on auction theory with asymmetric bidders: the institutional-trader extension (Section II) provides a tractable linear-equilibrium model with asymmetric information.
- Evaluating policy tradeoffs between allocative efficiency (favors order-by-order auctions) and retail investor welfare (ambiguous, depends on $$N$$ and $$\frac{c_1}{c_2}$$).

The key propositions are Proposition 2 (pp. 1889-1890, baseline welfare comparison) and Proposition 9 (pp. 1898-1900, endogenous entry with adverse selection).

## Attribution and rights

Thomas Ernst, Chester Spatt, Jian Sun, "Would Order-By-Order Auctions Be Competitive?", *The Journal of Finance*, vol. 80, no. 4 (August 2025), pp. 1879-1927. DOI: 10.1111/jofi.13449.

Published under a Creative Commons Attribution-NonCommercial-NoDerivs (CC BY-NC-ND 4.0) licence. This page is an LLM-distilled extract (not human-verified, not reproduced). The original article is available at [https://doi.org/10.1111/jofi.13449](https://doi.org/10.1111/jofi.13449). Extract only; the CC BY-NC-ND 4.0 licence does not permit redistribution of modified or derivative copies.
