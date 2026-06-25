---
title: "Regulating Over-the-Counter Markets: Lee & Wang (2025)"
description: >-
  Distilled: Lee and Wang embed dealer cream skimming via price discrimination into
  a Glosten-Milgrom framework and show that restricting OTC dealer discrimination
  worsens aggregate volume and average spreads yet can raise utilitarian welfare
  whenever adverse selection risk is low, via a novel cheap-substitution mechanism.
  J. Finance 2025, CC BY 4.0. Six core results with source locators, datasets used
  (theoretical; empirical patterns in Internet Appendix), the model, and the method.
sidebar:
  label: Lee-Wang 2025
  order: 1
tags: [paper-summary, market-microstructure, otc-markets, regulation, price-discrimination,
       market-design, theory, peer-reviewed, unreplicated, open-access, cc-by]
paper:
  authors: Tomy Lee, Chaojun Wang
  authorList:
    - { family: Lee, given: Tomy, orcid: "0009-0007-1524-9553", affiliation: Central European University }
    - { family: Wang, given: Chaojun, orcid: "0000-0002-1632-1728", affiliation: Wharton School, University of Pennsylvania }
  year: 2025
  venue: The Journal of Finance 80(4), August 2025, 1929–1962
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13461
  jel:
    codes: [G14, G18, D62]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Banking stability, regulation, efficiency
    - Financial Markets and Investment Strategies
    - Economic theories and models
  dataAccess: public
  outcome:
    - utilitarian welfare of traders
    - aggregate trade volume
    - average bid-ask spread
    - OTC market share
  outcomeClass: [asset-prices, social-welfare]
  license: "CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-05-30; corroborated by artifact p.1929 Creative Commons Attribution License notice)"
  licenseShort: CC BY 4.0
  access: open
  machineAccess: "open-access CC BY (Wiley/Crossref confirmed 2026-06-05)"
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 6
  citedByCount: 0

  methods:
    role: theory
    family: theory
    buildsFrom: [search-bargaining-otc]
  contributionType: [new-theory, new-fact]
  mechanisms: [information-asymmetry, search-frictions, market-power]
  scope:
    region: theoretical
    assetClass: OTC-traded assets (US equities cited in empirical appendix)
  relatesTo:
    - { cite: "Glosten and Milgrom (1985)", doi: '10.1016/0304-405x(85)90044-3', relation: builds-on, note: "baseline exchange framework; OTC dealer observes trader label before quoting, exchange dealer does not" }
    - { cite: "Seppi (1990)", doi: '10.1111/j.1540-6261.1990.tb05081.x', relation: builds-on, note: "introduces venue choice between OTC and exchange from which the model takes the OTC-vs-exchange setup" }
    - { cite: "Desgranges and Foucault (2005)", doi: '10.1016/j.jeconbus.2005.09.001', relation: builds-on, note: "endogenous dealer-client concentration of adverse selection risk on exchanges" }
    - { cite: "Bolton, Santos, and Scheinkman (2016)", doi: '10.1111/jofi.12385', relation: contradicts, note: "in their framework cream skimming raises welfare via origination effort; here it reduces welfare whenever adverse selection risk is low" }
    - { cite: "Akerlof (1970)", doi: '10.2307/1879431', relation: extends, note: "extends to imperfect labels showing cheap substitution reverses in the standard Akerlof framework because private values are correlated with common values there" }
    - { cite: "Bergemann, Brooks, and Morris (2015)", doi: '10.1257/aer.20130848', relation: extends, note: "with no adverse selection any outcome is achievable under price discrimination; this paper shows adverse selection gives robust welfare guidance" }
  openQuestions:
    - "Price discovery within each market is monotonically increasing in informed ratio β, but analyzing aggregate price discovery across OTC and exchange requires a stance on how quotes are aggregated; left for future work (p. 1948)."
    - "How welfare is affected by price impact (Vives (2011)) and sniping by fast traders (Budish, Cramton, and Shim (2015)) when these frictions coexist with OTC price discrimination (p. 1948)."
  findings:
    - ref: R1
      outcome: utilitarian welfare of traders
      metric: coefficient
      value: "Welfare rises for all μ < μ_l and falls for all μ > μ_h under any commonly used distribution F; single cutoff under quasiconcave ΔW (Proposition 2, p. 1939)"
      direction: mixed
      vsBenchmark: "restriction raises welfare iff mass of informed traders μ is sufficiently small"
    - ref: R2
      outcome: aggregate trade volume
      metric: coefficient
      value: "Restricting the OTC dealer always strictly reduces aggregate volume V and widens average spread S̄ for all μ > 0, under any distribution with decreasing ΔV (Proposition 2(e), p. 1939)"
      direction: negative
      vsBenchmark: "volume and spread are poor welfare indicators; welfare can rise even as volume falls"
    - ref: R3
      outcome: utilitarian welfare of traders
      metric: coefficient
      value: "Optimal Pigouvian tax T* attains strictly higher welfare than closing the OTC market for any (α, θ, γ); under F = U[0,1] T* is unique (Proposition 5, p. 1944)"
      direction: positive
      vsBenchmark: "partial tax always dominates full OTC closure"
    - ref: R4
      outcome: utilitarian welfare of traders
      metric: coefficient
      value: "WSR > 1 implies raising T raises W; WSR < 1 implies cutting T raises W; under F = U[0,1] iterating the WSR rule converges to T* (Proposition 6, p. 1945)"
      direction: positive
      vsBenchmark: "WSR = S_E/S_O · |dV_E/dV_O|; computable from trade volumes and bid-ask spreads without structural estimation"
    - ref: R5
      outcome: OTC market share
      metric: coefficient
      value: "OTC market share V_O/V is strictly decreasing in informed ratio μ under condition (7) satisfied by uniform and beta distributions; high OTC share is not evidence against restriction (Proposition 4, p. 1942)"
      direction: negative
      vsBenchmark: "restriction raises welfare precisely where OTC market share is high, contradicting the industry argument that high OTC share signals OTC efficiency"
    - ref: R6
      outcome: average bid-ask spread
      metric: coefficient
      value: "Exchange market share V_E/V and exchange spread S_E are positively correlated across U.S.-listed equities (Section VI.C Internet Appendix); OTC spread S_O < S_N < S_E always (Proposition 1(c), p. 1937)"
      direction: positive
      vsBenchmark: "empirical pattern corroborates the model prediction that adverse selection jointly drives exchange share and spread"
  resultType: new-finding

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Read full PDF (pp. 1929-1962 + appendix proofs); all results from propositions and figures in the paper. Not human-verified; not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-05, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; two errors fixed: O_LI denominator was (1-θ), corrected to (1-γ) per PDF p.1934; R6 spread ordering was S_O < S_E < S_N, corrected to S_O < S_N < S_E per Proposition 1(c) p.1937." }
  licenceVerification:
    - { source: "Crossref works/10.1111/jofi.13461", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[0]: content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-05-30" }
---

**What this is.** This is the distilled skeleton of Lee and Wang (2025), "Regulating Over-the-Counter Markets," J. Finance 80(4): 1929-1962. It extracts the model, propositions, and key theoretical results with PDF locators. Read the [original paper](https://doi.org/10.1111/jofi.13461) to replicate or extend.

## TL;DR

Lee and Wang (2025) embed dealer cream skimming via price discrimination into the standard Glosten and Milgrom (1985) exchange model, allowing the OTC dealer to observe a public label (Likely Informed vs. Likely Uninformed) before quoting. The venue-choice between OTC and exchange follows Seppi (1990); the label-dependent pricing and cream skimming also relate to Desgranges and Foucault (2005), who show how dealer-client relationships concentrate adverse selection on exchanges. In equilibrium LI traders go to the exchange and LU traders go to the OTC market. The paper's central finding is that restricting the dealer's ability to discriminate across labels always reduces aggregate volume and widens the average spread, yet can raise utilitarian welfare whenever adverse selection risk (the mass of informed traders) is low. The mechanism is "cheap substitution": pooling causes uninformed traders with larger hedging benefits (previously on the exchange) to enter while uninformed traders with smaller benefits (previously in the OTC market) exit, and the entrants more than offset the exiters in welfare terms when adverse selection risk is low. This contradicts Bolton, Santos, and Scheinkman (2016), who find cream skimming raises welfare via origination effort incentives. The model also contrasts with Akerlof (1970): the paper shows cheap substitution reverses in that standard framework because private and common values are perfectly correlated there. On the price discrimination side, Bergemann, Brooks, and Morris (2015) show that without adverse selection any welfare outcome is achievable; this paper shows adverse selection provides robust guidance. The paper derives an optimal Pigouvian tax on OTC trades and a simple implementable "WSR Rule" based on the ratio of exchange to OTC spreads and volume changes, without requiring knowledge of structural parameters.

## Core results

| # | Result | Locator | Magnitude as reported |
|---|---|---|---|
| R1 | Welfare effect of restricting OTC dealer: raises welfare when informed mass μ is small, lowers it when μ is large | Proposition 2, pp. 1938-1939 | Single cutoff under quasiconcave ΔW; any commonly used F satisfies conditions |
| R2 | Volume and spread always worsen under restriction | Proposition 2(e), p. 1939 | Aggregate volume V strictly falls and average spread S̄ strictly widens for all μ > 0, under any distribution with decreasing ΔV |
| R3 | Optimal Pigouvian tax dominates OTC closure | Proposition 5, p. 1944 | T\* strictly raises welfare above closing the OTC market for any (α, θ, γ); unique under U[0,1] |
| R4 | WSR Rule implements T\* without structural estimation | Proposition 6, pp. 1944-1945 | WSR(T) > 1: raise T; WSR(T) < 1: cut T; WSR = 1 at T\*; WSR ≡ \|S\_E dV\_E / (S\_O dV\_O)\| |
| R5 | High OTC market share is not evidence against restriction | Proposition 4, pp. 1942-1943 | OTC share V\_O/V is decreasing in μ; restriction raises welfare exactly where OTC share is high |
| R6 | Empirical: exchange spread and exchange share positively correlated across U.S. equities | Internet Appendix §VI.C | Positive correlation of quoted spread with exchange market share corroborates model prediction |

**Overall (paper's conclusion).** Trading costs, volumes, and market shares can all mislead regulators because cheap substitution decouples these aggregates from welfare. The adverse selection parameter β, not aggregate volume or OTC share, is the correct policy signal. When β is low, restricting OTC price discrimination strictly improves welfare and the optimal tax can be approximated by the WSR statistic computed from observable trade data.

## Theory / model

The paper has no empirical design; the identification is structural (model restrictions). The model and propositions are the core content.

**Setup.** A continuum of risk-neutral traders may trade an indivisible asset in a three-stage game (Figure 2, p. 1935). The asset pays $$v \in \{-1, +1\}$$ with equal probability. A mass μ of traders are informed (private binary signal $$s_i = v$$ with probability α and $$-v$$ otherwise; α is signal accuracy). A mass 1 of uninformed traders each draw a hedging benefit $$b_i \overset{\text{iid}}{\sim} F$$ with support $$[0,1]$$. Each trader is publicly labeled $$\ell_i \in \{\text{LI}, \text{LU}\}$$; the odds of being informed conditional on label LI exceed the unconditional odds:

$$\mathcal{O}_{LI} = \frac{\theta\mu}{1-\gamma} > \mu > \frac{(1-\theta)\mu}{\gamma} = \mathcal{O}_{LU}$$

where $$\theta < 1$$ is the probability an informed trader is labeled LI and $$\gamma < 1$$ is the probability an uninformed trader is labeled LU.

**Equilibrium.** Each trader chooses to buy, sell, or exit on the exchange, over the counter, or not trade (Definition 1, p. 1936). The OTC dealer observes the label $$\ell_i$$ before quoting; the exchange dealer does not and sets a single unconditional spread. The zero-profit condition for the dealer posting spread $$s$$ when the informed ratio in her pool is $$\beta$$ is (p. 1937, Eq. 2):

$$\underbrace{s \cdot (1 - F(s))}_{\text{Profit from uninformed}} = \underbrace{(2\alpha - 1 - s)^+ \cdot \beta}_{\text{Loss to informed traders}} \tag{2}$$

The unique solution $$S(\beta)$$ is increasing in $$\beta$$.

**Proposition 1 (equilibrium spreads, p. 1937).** The exchange spread is $$S_E = S\!\left(\frac{\theta}{1-\gamma}\mu\right)$$; the OTC spread for LU traders is $$S_O = S\!\left(\frac{1-\theta}{\gamma}\mu\right)$$ and for LI traders is $$S_E$$. LI traders choose the exchange, LU traders choose the OTC market. The exchange spread strictly exceeds the OTC spread: $$S_E > S_N > S_O$$ where $$S_N = S(\mu)$$ is the no-OTC spread.

**Welfare and volume.** Welfare $$W$$ equals the sum of hedging benefits of uninformed traders who trade. The average bid-ask spread is $$\bar{S} \propto 1/V$$. Two quantities characterize the restriction's effect (pp. 1937-1938):

$$\Delta_V(\beta) := -\!\left(\int_{S(\beta)}^1 f(s)\,ds\right)' = S'(\beta)\cdot f(S(\beta)) \tag{3}$$

$$\Delta_W(\beta) := -\!\left(\int_{S(\beta)}^1 sf(s)\,ds\right)' = \Delta_V(\beta)\cdot S(\beta) \tag{4}$$

Marginal volume $$\Delta_V$$ is the fall in uninformed trade per unit increase in $$\beta$$; marginal welfare $$\Delta_W$$ equals $$\Delta_V$$ times the marginal exiter's hedging benefit $$\bar{b}(\text{exiters}) = S(\beta)$$.

**Proposition 2 (main result, pp. 1938-1939).** For any commonly used distribution F, restricting the OTC dealer:
- (a)-(c): raises welfare W if $$\mu < \mu_l$$ (small informed mass) and lowers W if $$\mu > \mu_h$$;
- (d): if $$\Delta_W$$ is strictly quasiconcave, the two cutoffs collapse to one: restriction raises W iff $$\mu < \underline{\mu}$$;
- (e): always strictly reduces aggregate volume V and strictly widens average spread $$\bar{S}$$.

**Proposition 3 (sufficient conditions, p. 1941).** $$\Delta_W$$ is strictly quasiconcave iff

$$\frac{(2\alpha-1)(1-F(x))}{xf(x)(2\alpha-1-x)^2} - \frac{1}{2\alpha-1-x} \quad\text{is strictly quasiconvex on }(0,2\alpha-1). \tag{5}$$

Any Beta(a, b) distribution satisfies (5) for all $$a,b > 0$$.

**Proposition 4 (market shares, pp. 1942-1943).** Under condition (7) (satisfied by uniform and beta distributions), OTC share $$V_O/V$$ is strictly decreasing in $$\mu$$. Therefore restricting the OTC dealer raises welfare precisely where the OTC market share is high, directly overturning the industry argument that high OTC share signals OTC efficiency.

## Method

This is a pure theory paper with no structural estimation. The solution method is closed-form zero-profit conditions plus comparative statics via the Implicit Function Theorem and integral inequalities. Proofs are in the Appendix (pp. 1949-1962).

**Pigouvian tax characterization.** A lump-sum tax $$T$$ on OTC trades shifts the dealer zero-profit conditions to (pp. 1943-1944):

$$S_O(T)\cdot\left[1-F(S_O(T))+\beta_O\right]\gamma = (2\alpha-1)\beta_O\gamma + T \tag{8}$$

$$S_E(T)\cdot\left[1-F(S_E(T))+\beta_E\right](1-\gamma) = (2\alpha-1)\beta_E\cdot(1-\gamma) - T \tag{9}$$

All implementations that raise the same gross revenue T are equivalent. The optimal Pigouvian tax T\* maximizes welfare W. Proposition 5 (p. 1944) shows T\* strictly dominates OTC market closure.

**WSR Rule (Proposition 6, p. 1945).** Define the Weighted Spread Ratio:

$$\text{WSR}(T) := \left|\frac{S_E(T)\,dV_E(T)}{S_O(T)\,dV_O(T)}\right| \tag{10}$$

The welfare-increasing direction of T is: raise T when WSR > 1 (cheap substitution dominates), cut T when WSR < 1 (volume effect dominates). The optimal tax satisfies WSR(T\*) = 1. The ratio $$S_E/S_O$$ is observable as the ratio of exchange to OTC spreads; $$|dV_O/dV_E|$$ is the ratio of volume changes before and after a policy perturbation.

## Empirical specifications

The paper is theoretical; there is no estimation. The Internet Appendix (Sections V and VI) documents supporting empirical patterns without a causal design.

**Empirical pattern 1 (Internet Appendix §V).** The exchange's market share and spread are positively correlated because both are driven by the informed ratio β. As β rises, the OTC market absorbs more informed traders so the exchange spread rises and OTC share rises mechanically.

**Empirical pattern 2 (Internet Appendix §VI.C).** The total market share of exchanges and their quoted spreads are positively correlated across U.S.-listed equities, corroborating the model prediction (p. 1933). This is documented as a novel empirical pattern, not a causal test.

The paper explicitly leaves causal estimation of the welfare effects of OTC restrictions for future work.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| U.S. equity market microstructure data (quoted spreads, exchange market share) | Empirical corroboration in Internet Appendix §VI.C | no page yet |

The core model is theoretical; no large dataset is used for estimation.

## When to read the full paper

Read Lee and Wang (2025) when:
- Designing or evaluating OTC market regulations (post-trade transparency, name give-up rules, blockchain record-keeping proposals discussed in the Internet Appendix §I);
- Studying how to implement a Pigouvian tax on OTC trading without needing structural estimates of adverse selection risk, using the WSR Rule;
- Understanding why aggregate volume, average spread, and OTC market share are unreliable welfare indicators in two-venue markets;
- Modeling OTC-versus-exchange venue choice with imperfect trader labels in a Glosten-Milgrom framework.

The key propositions (Propositions 2, 4, 5, 6) are in §II and §III (pp. 1938-1945). Appendix proofs are pp. 1949-1962.

## Attribution and rights

This article is open access under CC BY 4.0. The canonical citation is:

> Lee, Tomy and Chaojun Wang. "Regulating Over-the-Counter Markets." *The Journal of Finance* 80, no. 4 (August 2025): 1929-1962. https://doi.org/10.1111/jofi.13461

Copyright 2025 The Authors. Published by Wiley Periodicals LLC on behalf of American Finance Association. Open access funding provided by Central European University Private University - CEU GmbH/KEMO.

This page is LLM-distilled by the IAR paper-distiller (claude-sonnet-4-6). It is not human-verified and the results have not been independently reproduced. Extract-only; the original PDF is not mirrored here (CC BY 4.0 permits redistribution by any party with proper attribution).
