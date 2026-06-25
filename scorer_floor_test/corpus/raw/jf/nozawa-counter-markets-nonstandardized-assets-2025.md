---
title: "OTC Markets for Nonstandardized Assets: Nozawa & Tsoy (2025)"
description: >-
  Distilled: Nozawa and Tsoy build a search-and-bargaining model of OTC markets
  for nonstandardized assets, deriving that bargaining delays are hump-shaped in
  unobserved asset quality and asset turnover is U-shaped. Empirical tests on
  corporate bonds (TRACE, 2002-2020) and commercial real estate (CoStar,
  1998-2022) confirm the U-shaped liquidity pattern; a placebo test on agency
  MBS finds no such pattern. J. Finance 2025, paywalled. Seven core results with
  source locators, datasets used, the model, and the method.
sidebar:
  label: Nozawa-Tsoy 2025
  order: 1
tags: [paper-summary, market-microstructure, otc-markets, search-frictions,
       corporate-bonds, real-estate, market-liquidity, structural,
       peer-reviewed, unreplicated, data:trace, data:costar]
paper:
  authors: Yoshio Nozawa, Anton Tsoy
  authorList:
    - { family: Nozawa, given: Yoshio, orcid: "0000-0002-6395-2688", affiliation: University of Toronto }
    - { family: Tsoy, given: Anton, affiliation: University of Toronto }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2831–2873
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13483
  jel:
    codes: [G12, G14, D83]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Banking stability, regulation, efficiency
    - Housing Market and Economics
    - Financial Markets and Investment Strategies
  dataAccess: licensed-commercial
  outcome:
    - asset turnover / trading frequency in OTC markets
    - bargaining delay (days to complete a trade)
    - bid-ask spread in corporate bond markets
    - days to sell commercial real estate
  outcomeClass: [asset-prices, security-returns]
  license: >-
    Paywalled; Wiley version-of-record terms (confirmed via Crossref DOI
    metadata: content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-08-26). Copyright 2025 the American Finance Association.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/AFA site; confirmed paywalled via Crossref licence metadata 2026-06-05)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 0

  methods:
    role: both
    contributes: otc-nonstandardized-search-bargaining
    family: structural
    buildsFrom: [search-bargaining-otc]
    identification: descriptive
  contributionType: [new-theory, new-fact]
  mechanisms: [search-frictions, information-asymmetry, liquidity]
  scope:
    region: US
    assetClass: corporate bonds, commercial real estate, agency MBS
    period: 1998-01..2022-09
    frequency: mixed
    dataType: [market, accounting, other]
    granularity: [security, transaction]
    n: "TRACE corporate bonds Jul 2002-Dec 2020; CoStar CRE sales 15 US cities 1998Q1-2022Q3"

  findings:
    - ref: R1
      outcome: asset turnover in corporate bond OTC market
      metric: level
      value: "Extreme deciles (1st and 10th) turnover significantly higher than middle; t(10-min)=7.99, t(1-min)=3.37"
      direction: positive
      vsBenchmark: U-shaped vs middle decile; middle decile turnover near trough
    - ref: R2
      outcome: trading volume in corporate bond OTC market
      metric: level
      value: "Extreme deciles significantly higher volume than middle; t(10-min)=5.43, t(1-min)=1.50 (marginal)"
      direction: positive
      vsBenchmark: U-shaped pattern across excess-bond-premium deciles (Figure 2)
    - ref: R3
      outcome: zero-trade days in corporate bond OTC market
      metric: level
      value: "Middle deciles have more zero-trade days than extremes; t(1-max)=-2.41, t(10-max)=-4.84"
      direction: negative
      vsBenchmark: hump-shaped zero-trade days consistent with U-shaped turnover (Figure 2)
    - ref: R4
      outcome: bid-ask spread in corporate bond OTC market
      metric: basis-points
      value: "U-shaped bid-ask spread; t(10-min)=9.15, t(1-min)=2.88"
      direction: positive
      vsBenchmark: U-shaped pattern across excess-bond-premium deciles (Figure 2)
    - ref: R5
      outcome: asset turnover in corporate bond OTC market
      metric: level
      value: "Post-Volcker period exhibits more pronounced U-shaped volume pattern than pre-Volcker; turnover and bid-ask spread patterns similar across subperiods"
      direction: positive
      vsBenchmark: Volcker subperiod (Apr 2014-Dec 2020) vs pre-Volcker (Jul 2002-Mar 2014), Figure 3
    - ref: R6
      outcome: days to sell commercial real estate
      metric: level
      value: "Hump-shaped: difference between 7th decile (max) and 1st decile = 24 days (t=5.65); difference between 7th and 10th decile = 32 days (t=9.46)"
      direction: positive
      vsBenchmark: hump-shaped days-to-sell vs unobserved quality decile (Figure 4)
    - ref: R7
      outcome: days to sell commercial real estate (MBS placebo)
      metric: level
      value: "No significant differences in MBS volume, turnover, or zero-trade days across unexplained-yield-spread deciles; t-stats all below 2.0 in absolute value for volume and turnover"
      direction: none
      vsBenchmark: no U-shaped pattern for agency MBS (Figure 6); confirms nonstandardization is key driver

  resultType: new-finding

  relatesTo:
    - { cite: "Duffie, Garleanu & Pedersen (2005)", relation: builds-on, note: "Standard OTC search model that paper extends with bargaining delays from nonstandardization" }
    - { cite: "Duffie, Garleanu & Pedersen (2007)", doi: '10.1093/rfs/hhm037', relation: extends, note: "Extends the risk-aversion extension; k=0 coincides with their equilibrium when investors cannot search during bargaining (Section I.B of Internet Appendix)" }
    - { cite: "Tsoy (2018)", doi: '10.3982/te2543', relation: builds-on, note: "Companion paper on bilateral bargaining with two-sided private information that characterizes the limit PBE used here" }
    - { cite: "Tsoy (2019)", relation: builds-on, note: "Further companion on the same bargaining game, providing the closed-form price and delay equations (12) and (13)" }
    - { cite: "Gilchrist & Zakrajsek (2012)", doi: '10.1257/aer.102.4.1692', relation: cites, note: "Excess bond premium used as the proxy for unobserved corporate bond quality theta" }
    - { cite: "Garmaise & Moskowitz (2004)", doi: '10.1093/rfs/hhg037', relation: cites, note: "Tax assessment as public benchmark for CRE property values; motivates the price-assessment ratio approach" }

  openQuestions:
    - "The model abstracts from investors' portfolio choices and assumes each investor holds at most one asset; generalizing to portfolio choice would be interesting (p. 2837)."
    - "Self-sustained illiquidity equilibria (where liquidity begets illiquidity) are ruled out by the continuity assumption on v and c; whether such equilibria arise in practice is left open (p. 2841 fn. 12)."
    - "The analysis focuses on corporate bonds and CRE; extending and testing the model's implications for other highly nonstandardized OTC markets (e.g., derivatives, structured products) is an open direction (p. 2865)."

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: >-
        Full text read (pp. 2831-2873, including appendix proofs). Seven results
        extracted from Figures 2-6 and associated t-statistics reported in the
        paper. Model equations (1)-(32) transcribed from the source PDF. Not
        human-verified. Not reproduced.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all 7 Core-results rows confirmed correct. Fixed: R1 and R5 metric corrected from return-spread to level (outcome is turnover rate, not a return spread); Method Step 1 equation reference corrected from (14) to (27) (the displayed I(L,Lambda_s) formula is Proposition 1 eq. 27, the uniform-distribution specialization of Lemma 1 eq. 14)."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13483
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-26; no CC licence; copyright AFA"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the structural model it proposes (OTC search and bargaining over nonstandardized assets), and the empirical tests with the key equations: enough to know what it found and how, without reading all 43 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13483).

## TL;DR

Nozawa and Tsoy study over-the-counter markets where assets differ in unobserved quality. They extend the Duffie, Garleanu, and Pedersen (2005) model (and its risk-aversion variant in Duffie, Garleanu, and Pedersen (2007)) with two-sided private information during bargaining: once matched, buyers and sellers privately learn their own values (correlated with asset quality) but not their counterparty's. This two-sided information structure generates bargaining delays that are hump-shaped in the unobserved quality of the asset, which translates into a novel, testable prediction: asset turnover is U-shaped in quality. Extreme-quality assets trade quickly (both sides concede early), while intermediate-quality assets experience long negotiations (both sides wait for a better offer). The theory also implies that the opaque OTC structure supports trading of a wide variety of assets (extensive margin), while centralization of trading concentrates liquidity in the most-liquid assets and can harm the extensive margin. Empirical tests using corporate bond TRACE data (2002-2020) and commercial real estate CoStar data (1998-2022) confirm the U-shaped pattern; a placebo on agency MBS (highly standardized) finds no such pattern.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Corporate bond turnover is U-shaped** in excess bond premiums: extreme deciles have significantly higher turnover than middle deciles | Figure 2, p. 2858 | t(10-min)=7.99; t(1-min)=3.37; consistent U-shaped pattern |
| R2 | **Corporate bond trading volume is U-shaped** in excess bond premiums: extreme deciles trade more per month in dollar terms | Figure 2, p. 2858 | t(10-min)=5.43; t(1-min)=1.50 (marginal); U-shape visible |
| R3 | **Zero-trade days are hump-shaped**: middle decile bonds spend more days without transactions than extreme deciles | Figure 2, p. 2858 | t(1-max)=-2.41; t(10-max)=-4.84; hump pattern mirrors U-shaped turnover |
| R4 | **Bid-ask spreads are U-shaped** in excess bond premiums: extreme deciles have higher spreads than middle | Figure 2, p. 2858 | t(10-min)=9.15; t(1-min)=2.88 |
| R5 | **Post-Volcker period shows more pronounced U-shaped volume** than pre-Volcker; as dealer intermediation capacity shrinks, bilateral negotiation matters more | Figure 3, p. 2859 | Post-Volcker (Apr 2014-Dec 2020) volume shows sharper U; turnover and bid-ask similar across subperiods |
| R6 | **Commercial real estate days to sell is hump-shaped** in unobserved property quality: mid-quality properties take longest to sell | Figure 4, p. 2861 | 7th decile max minus 1st decile = 24 days (t=5.65); 7th minus 10th decile = 32 days (t=9.46); both significant |
| R7 | **Placebo test on agency MBS finds no U-shaped pattern**: volume, turnover, and zero-trade days show no significant variation across unexplained yield spread deciles | Figure 6, p. 2864 | All t-stats below 2.0 in absolute value for volume and turnover; confirms nonstandardization drives the nonlinearity |

**Overall (paper's conclusion).** The results support the model's central prediction that two-sided private information about asset quality in OTC markets generates hump-shaped bargaining delays and U-shaped liquidity. The evidence holds for corporate bonds and CRE (both highly nonstandardized) but not for agency MBS (highly standardized), providing a clean placebo test. The model implies that centralization of trading should accompany standardization to avoid liquidity concentrating on a narrow set of assets.

## Theory / model

The model is a continuous-time search-and-bargaining general equilibrium. Asset quality $$\theta \in [0,1]$$ is unobserved and captures heterogeneous payoffs. A unit mass of infinitely lived, risk-neutral investors hold assets with flow payoff $$1 + k\theta$$ ($$k > 0$$ captures payoff heterogeneity; larger $$k$$ means less standardized). Investors experience liquidity shocks that convert high-type (asset holder, no holding cost) to low-type (asset holder, holding cost $$\delta > 0$$) at Poisson rate $$\lambda_d$$, and recover at rate $$\lambda_u$$ (p. 2836-2837).

Low types (sellers) and high types without assets (buyers) search for counterparties. Buyers and sellers meet with Poisson contact intensity $$2\lambda m_b m_s$$. The steady-state balance conditions (p. 2838, equations 1-2) are:

$$
\mu_{lu}(\theta) + \mu_{hu}(\theta) + \mu_{lm}(\theta) = sf(\theta), \quad \forall \theta \in [0,1] \tag{1}
$$

$$
M_{lu}(\varnothing) + M_{hu}(\varnothing) + M_{hm}([0,1]) = 1 - s \tag{2}
$$

Bellman equations for unmatched and matched investors are given by equations (3)-(8) on pp. 2838-2840, where $$rV_{hu}(\varnothing)$$, $$rV_{lu}(\theta)$$, $$rV_{lu}(\varnothing)$$, $$rV_{hu}(\theta)$$ capture the continuation values of buyers without assets, sellers, unmatched low types, and high types with asset $$\theta$$, respectively.

The key innovation is the bargaining structure. Once matched, buyers and sellers privately observe their own types but not their counterparty's. The buyer's type $$\theta^b = \theta + \varepsilon^b$$ and seller's type $$\theta^s = \theta + \varepsilon^s$$ are affiliated, converging to the true quality $$\theta$$ in the limit as noise vanishes. Drawing on Tsoy (2018, 2019), in the limit of frequent offers ($$\Delta \to 0$$) the bargaining game admits a limit of Perfect Bayesian Equilibria with closed-form price and delay outcomes (p. 2841, equations 12-13):

$$
p(\theta) = qv(\theta) + (1-q)c(\theta), \quad \forall \theta \in [0,1] \tag{12}
$$

$$
t(\theta) = \begin{cases} \frac{1}{\rho} \int_0^{\theta} \frac{dp(\tilde\theta)}{p(\tilde\theta) - c(\tilde\theta)}, & \theta \le \theta^* \\ \frac{1}{\rho} \int_\theta^1 \frac{dp(\tilde\theta)}{v(\tilde\theta) - p(\tilde\theta)}, & \theta \ge \theta^* \end{cases} \tag{13}
$$

where $$q \in (0,1)$$ is the seller's bargaining power, $$v(\theta)$$ is the buyer's value, $$c(\theta)$$ is the seller's cost, and $$\theta^*$$ is the quality where seller and buyer roles reverse in who drives the bargaining dynamics (p. 2841). The bargaining delays $$t(\theta)$$ in equation (13) are hump-shaped in $$\theta$$: extreme-quality assets are traded quickly because one side has a dominant incentive to concede; intermediate-quality assets near $$\theta^*$$ involve longer negotiations.

**Proposition 3** (p. 2848) establishes that the effective discount factor $$x(\theta) = \exp\{-\rho t(\theta)\}$$ and the asset turnover $$w(\theta)$$ are U-shaped in $$\theta$$ (equation 29):

$$
w(\theta) = \frac{\lambda_d \Lambda_s \sigma(\theta)}{\lambda_u + \lambda_d + \Lambda_s \sigma(\theta)} x(\theta)^{(\lambda_u + \lambda_d)/\rho} \tag{29}
$$

where $$\Lambda_s$$ is market thickness for sellers and $$\sigma(\theta) \in [0,1]$$ is the probability that a buyer proceeds to bargaining with asset $$\theta$$.

The equilibrium is characterized by (p. 2844-2847): (i) steady-state market thickness $$\Lambda_s$$ from equation (14), (ii) buyers' cutoff on acceptable effective discount factors $$\underline{x} = \bar{x}\Lambda_b / (\rho + \Lambda_b)$$ (equation 24), and (iii) the U-shaped structure of $$x(\theta)$$ from Lemma 3.

Asset prices (Proposition 2, p. 2847, equation 28) embed an illiquidity discount relative to full-information frictionless prices:

$$
p(\theta) = U_s(\theta) + \frac{q\delta}{\rho}\!\left(1+\frac{\lambda_d}{r}\right) - \frac{\delta}{r}\!\left[(1-q)\frac{\lambda_u}{\rho}\frac{\Lambda_b \bar{x}}{\rho+\Lambda_b} + q\frac{\lambda_d}{\rho}\!\left(1 - \frac{\sigma(\theta)\Lambda_s x(\theta)}{\rho + \sigma(\theta)\Lambda_s}\right)\right] \tag{28}
$$

where $$U_s(\theta) \equiv \frac{1}{r}(1+k\theta) - \frac{\delta}{\rho}(1+\lambda_d/r)$$ is the autarky value for the seller.

## Method

The paper is primarily a structural theory paper with an empirical validation component. On the theory side, the equilibrium solution method proceeds in three steps (pp. 2843-2847):

**Step 1.** Derive the steady-state distribution $$\mathbf{M}$$ in closed form via balance equations (A3)-(A4) in the appendix. Lemma 1 establishes that $$\Lambda_s$$ is the unique positive solution to equation (27) (the uniform-distribution specialization of Lemma 1's general equation (14)):

$$
\frac{\Lambda_s}{2\lambda} = \frac{\lambda_u(1-s)}{\lambda_u + \lambda_d} - \frac{\lambda_d s}{\lambda_u + \lambda_d} I(L, \Lambda_s) \tag{27}
$$

where $$I(L, \Lambda_s)$$ is given in the proof.

**Step 2.** Buyers' optimal strategy takes a cutoff form on the effective discount factor $$x(\theta)$$: buyers accept assets with $$x(\theta) > \underline{x}$$, reject those with $$x(\theta) < \underline{x}$$, and mix at equality (Lemma 2, p. 2844, equation 24).

**Step 3.** Lemma 3 (p. 2846, equation 25) pins down the effective discount factor $$x(\theta)$$ as:

$$
x(\theta) = \begin{cases} \exp\{-\rho(c(\theta) - c(0))/(q\delta)\} & \theta \in [0, \check\theta] \\ \exp\{-\rho(v(1) - v(\theta))/((1-q)\delta)\} & \theta \in [\hat\theta, 1] \end{cases} \tag{25}
$$

The equilibrium is then pinned down by solving equations (14) and (24) jointly for $$\underline{x}$$ and $$\Lambda_s$$.

On the empirical side, the paper does not estimate the structural model; it tests the model's reduced-form qualitative prediction (U-shaped liquidity in quality) in two nonstandardized asset classes. The empirical strategy is:

1. Classify assets by a proxy for unobserved quality (excess bond premium for corporate bonds, regression residuals of the price-assessment ratio for CRE, unexplained yield spread for MBS).
2. Form 10 decile portfolios by the quality proxy.
3. Compute equal-weighted average liquidity measures within each decile.
4. Plot and test whether the pattern is U-shaped (bonds) or hump-shaped (days to sell for CRE).

The proxy for unobserved corporate bond quality $$\theta$$ follows Gilchrist and Zakrajsek (2012): the excess bond premium is the difference between observed credit spreads and spreads predicted by public information. For CRE, unobserved quality translates into residual variation in price premiums relative to the tax assessment benchmark: Garmaise and Moskowitz (2004) show that a property's tax assessment serves as a public benchmark for its value (p. 2860). The price-assessment ratio residual comes from estimating equation (30):

$$
P_i / B_i = a + b X_i + \varepsilon_i \tag{30}
$$

where $$P_i$$ is the sale price, $$B_i$$ is the tax assessment, and $$X_i$$ includes property age, floors, square footage, property-type dummies, submarket dummies, building condition, and buyer/seller location dummies (p. 2860). Standard errors in the CRE analysis are clustered at the quarter-submarket-property-type level, computed by block bootstrap (Figure 4 caption, p. 2861). Corporate bond standard errors use Newey and West (1987) with 12 lags (Figure 2 caption, p. 2858).

## Empirical specifications

**Corporate bonds (R1-R5).** TRACE monthly corporate bond transactions (July 2002-December 2020) are merged with Mergent FISD for amount outstanding and credit rating. Nonfinancial issuer firms only. Bonds are sorted monthly into 10 portfolios by their excess bond premium (Gilchrist and Zakrajsek (2012)). Within each portfolio, four liquidity measures are computed: (i) equal-weighted average dollar volume per month, (ii) turnover rate (monthly volume divided by amount outstanding), (iii) number of zero-trade days in the following 12 months, and (iv) bid-ask spread (average sell minus average buy price within a day, scaled by the average). The time-series average of each measure within each decile is then plotted against the decile rank (Figure 2). Subperiod analysis splits at April 2014 following Bao, O'Hara, and Zhou (2018) (Figure 3).

**Commercial real estate (R6).** CoStar data on completed CRE sales across 15 US cities from 1998Q1 to 2022Q3. The liquidity proxy is days to sell (listing date to delisting date). Unobserved quality is the OLS residual from equation (30) estimated city by city. Deals are then classified into 10 decile bins, and the median (not mean, due to skewness) days to sell within each decile is computed. Standard errors are estimated by block bootstrap, clustered at the quarter-submarket-property-type level (Figure 4).

**MBS placebo (R7).** TRACE MBS data (July 2013-July 2021) for Fannie Mae specified-pool 30-year fixed-rate MBS, merged with Refinitive Eikon for MBS characteristics. Unobserved quality proxied by residuals from a regression of yield spreads on MBS characteristics. 10 equal-weighted portfolios of MBS formed analogously to bonds. Liquidity measures as in the bond analysis. No significant U-shaped pattern emerges (Figure 6), consistent with agency MBS being highly standardized.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| TRACE (corporate bonds) | Corporate bond transaction prices, volumes, and dates; Jul 2002-Dec 2020 | [TRACE](/wiki/licensed/trace/) (licensed) |
| Mergent FISD | Amount outstanding and credit rating for corporate bonds | [no page yet] |
| Gilchrist-Zakrajsek excess bond premium | Proxy for unobserved corporate bond quality (theta); computed from TRACE and public information | [no page yet] |
| CoStar CRE | Commercial real estate sale transactions in 15 US cities; 1998Q1-2022Q3; includes price, assessment value, property characteristics | [CoStar](/wiki/licensed/costar/) (licensed) |
| TRACE (agency MBS) | MBS transaction prices and volumes for Fannie Mae specified-pool MBS; Jul 2013-Jul 2021 | [TRACE](/wiki/licensed/trace/) (licensed) |
| Refinitive Eikon | MBS characteristics (issue amount, date) for the placebo MBS analysis | [no page yet] |

Sample coverage: corporate bonds monthly, Jul 2002-Dec 2020; CRE quarterly, 1998Q1-2022Q3; MBS monthly, Jul 2013-Jul 2021.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13483) if you are: building or testing search-and-bargaining models of OTC markets for heterogeneous assets; studying how asset standardization affects market liquidity (including the trade-off between intensive and extensive liquidity margins); analyzing the impact of market reforms (TRACE, Volcker rule, CDS Big Bang) on OTC liquidity; or extending the model to portfolio choice, dynamic standardization, or other nonstandardized asset classes (derivatives, structured products). The Internet Appendix contains additional proofs, robustness checks, and subsample analyses referenced from the main text.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). Copyright 2025 the American Finance Association. Published by Wiley on behalf of the AFA. This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. Reproduction rights: extract-only (paywalled; the Wiley VOR licence does not permit redistribution).

> Nozawa, Yoshio, and Anton Tsoy. "Over-the-Counter Markets for Nonstandardized Assets." *The Journal of Finance* 80, no. 5 (October 2025): 2831-2873. DOI: 10.1111/jofi.13483.
