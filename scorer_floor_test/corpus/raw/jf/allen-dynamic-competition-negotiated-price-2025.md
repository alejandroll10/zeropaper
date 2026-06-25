---
title: "Dynamic Competition in Negotiated Price Markets: Allen & Li (2025)"
description: >-
  Distilled: Using Canadian mortgage contract data, Allen and Li document an
  "invest-and-harvest" pricing pattern and build a structural dynamic model of
  price negotiation with search and switching frictions to quantify market
  frictions and study counterfactual policies. J. Finance 2025, CC BY-NC 4.0.
  Eight core results with source locators, datasets used, the model, and the
  estimation method.
sidebar:
  label: Allen-Li 2025
  order: 1
tags: [paper-summary, household-finance, mortgages, search-frictions, switching-costs,
       structural, market-microstructure, panel-regression, peer-reviewed, unreplicated,
       data:transunion-canada, data:osfi-canada]
paper:
  authors: Jason Allen and Shaoteng Li
  authorList:
    - { family: Allen, given: Jason, orcid: "0000-0003-2558-9061", affiliation: "Bank of Canada and University of Wisconsin-Madison" }
    - { family: Li, given: Shaoteng, orcid: "0009-0006-2418-5144", affiliation: "Bank of Canada" }
  year: 2025
  venue: The Journal of Finance 80(1), February 2025, 561-614
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13408
  jel:
    codes: [G21, D83, L13]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Economic theories and models", "Merger and Competition Analysis", "Consumer Market Behavior and Pricing"]
  dataAccess: proprietary-confidential
  outcome:
    - mortgage interest rate paid by borrowers
    - lender switching probability at renewal
    - borrower total financing cost (interest plus search/switching costs)
    - lender investment incentive (continuation value of winning)
  outcomeClass: [household-finance, firm-financing, market-microstructure]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2024-12-13; corroborated by artifact p.561 Creative Commons
    Attribution-NonCommercial License notice)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "open-access PDF available via Wiley Online Library (doi:10.1111/jofi.13408, confirmed 2026-06-06)"
  redistribution: extract-only (CC BY-NC 4.0 permits noncommercial reproduction; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 4

  methods:
    role: both
    contributes: dynamic-negotiated-price-game
    family: structural
    buildsFrom: [blp-demand, gmm, panel-regression, search-bargaining-otc]
    identification: structural

  contributionType: [new-theory, new-fact, measurement]

  mechanisms: [search-frictions, switching-costs, market-power]

  scope:
    region: Canada
    assetClass: residential mortgages
    period: 2014-01..2019-07
    frequency: mixed
    dataType: [administrative, market]
    granularity: [individual, transaction]
    n: "34,554 contracts in final estimation sample (17,277 purchase + 15,627 loyal renewal + 1,650 switch renewal); 771,101 contracts in full cross-section"

  findings:
    - ref: R1
      outcome: lender switching probability at renewal
      metric: probability
      value: "9.55% of renewing borrowers switch lenders; loyal renewers pay 4.0 bps more than new borrowers; switchers pay 7.9 bps less than loyal renewers"
      direction: positive
      vsBenchmark: "loyalty premium = 8.53 bps; Table I, p. 569"
    - ref: R2
      outcome: mortgage interest rate paid by borrowers
      metric: coefficient
      value: "Loyal renewal dummy: +4.00 bps (SE 0.29); switch renewal dummy: -3.93 bps (SE 0.49) vs purchase baseline; Table II col (1), p. 570"
      direction: positive
      vsBenchmark: invest-and-harvest pattern confirmed in OLS; R-squared = 0.72
    - ref: R3
      outcome: borrower total financing cost (interest plus search/switching costs)
      metric: level
      value: "Average search cost $386 per borrower (1.3% of average interest cost); average switching cost $462 (new) and $829 (first-time renewers); average investment incentive $843 per borrower; Table IV, p. 588"
      direction: positive
      vsBenchmark: benchmark dynamic model; lender annual discount factor 0.93
    - ref: R4
      outcome: borrower total financing cost (interest plus search/switching costs)
      metric: pp-effect
      value: "Removing both frictions saves borrowers 1.4% (origination) and 2.5% (renewal) in total cost in the dynamic model; static model overpredicts savings at 3.0% and 4.6%; Table VIII Panel C, p. 597"
      direction: negative
      vsBenchmark: "static model overpredicts consumer gains by ~2x; interaction effect: joint removal saves 58% (30%) more than sum of individual effects at origination (renewal)"
    - ref: R5
      outcome: borrower total financing cost (interest plus search/switching costs)
      metric: pp-effect
      value: "Removing switching costs alone: new borrowers pay $203 more in interest (+0.2% total cost); renewers save $189 (-0.6% total cost); Table VIII col (2), p. 597"
      direction: mixed
      vsBenchmark: "new borrowers worse off because lender investment incentive drops; renewers better off; static model always predicts savings; V drops from $0.806 to $0.253 at origination (Table VIII Panel A)"
    - ref: R6
      outcome: lender investment incentive (continuation value of winning)
      metric: level
      value: "Investment incentive V averages $842.5 (SD $287.3); increasing in switching cost and decreasing in number of lenders; interaction: effect of switching cost on V is stronger when search costs are high; Table IV p. 588, Table V col (2) p. 590"
      direction: positive
      vsBenchmark: forward-looking model needed; static model sets V = 0
    - ref: R7
      outcome: borrower total financing cost (interest plus search/switching costs)
      metric: pp-effect
      value: "25-year FRM vs 5-year FRM: borrowers save on average $213 in interest cost and $344 in total cost per origination in dynamic model; lenders earn $423 more in total profits over 25 years; Table IX, p. 602"
      direction: negative
      vsBenchmark: "static model predicts lenders earn $1,163 less; dynamic model reverses sign because lender investment incentives fall with long-term contracts"
    - ref: R8
      outcome: lender switching probability at renewal
      metric: pp-effect
      value: "Mortgage stress test at renewal: unqualified borrowers (10.2% of sample) experience 22 bps higher interest rates and 7.8% higher total costs at renewal; switching probability falls from 20.2% to 3.0%; lender profit from unqualified renewer quadruples; Table XI, p. 606"
      direction: negative
      vsBenchmark: "unintended consequence: anticipatory effect raises lender investment incentive from $982 to $3,967 at origination; lowers origination costs 4.6% for affected borrowers but increases financial distress risk"

  resultType: new-finding

  relatesTo:
    - { cite: "Woodward and Hall (2012)", doi: '10.1257/aer.102.7.3249', relation: builds-on, note: "motivates auction approach to modelling mortgage price negotiation" }
    - { cite: "Allen, Clark, and Houde (2019)", doi: '10.1086/701684', relation: extends, note: "extends their origination-only model to a full dynamic repeated-interaction framework with renewals and switching costs" }
    - { cite: "Dube, Hitsch, and Rossi (2009)", relation: builds-on, note: "switching costs in dynamic frameworks; consistent with their finding that switching costs can lower equilibrium prices" }
    - { cite: "Shcherbakov (2016)", doi: '10.1111/1756-2171.12131', relation: builds-on, note: "dynamic switching-cost framework; paper extends to include search frictions and negotiated prices" }
    - { cite: "Honka (2014)", doi: '10.1111/1756-2171.12073', relation: builds-on, note: "simultaneous search and switching costs in auto insurance; paper differs by adding supply-side forward-looking responses and negotiated pricing" }
    - { cite: "Agarwal et al. (2023a)", doi: '10.17016/feds.2023.007', relation: cites, note: "HARP strengthened incumbency advantage in U.S. mortgage refinancing; consistent with invest-and-harvest mechanism" }

  openQuestions:
    - "Extension to markets with endogenous refinancing decisions (e.g., U.S. mortgage market) and asymmetric information in small-business lending, which require additional institutional modeling (p. 608)."
    - "Whether the broker channel should be incorporated; the paper excludes broker-intermediated mortgages (30% of originations) because broker-lender relationships, broker pricing strategies, and broker compensation require their own dynamic game (pp. 568-569)."
    - "The paper abstracts from persistent unobserved heterogeneity in search or switching costs; an adverse selection problem would arise if lenders observe borrowers searching or switching and adjust pricing, which the authors argue is unlikely given the credit bureau data context but do not formally rule out (p. 576, footnote 16)."

  replicationCode:
    status: none

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: >-
        Full PDF read (pp. 561-614, 54 pages); eight results extracted from
        Tables I-XII and Figures 1-5. Model equations transcribed from
        pp. 573-582 (eqs. 1-15). Not human-verified. Not reproduced.

    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against source PDF; all 8 Core results
        rows confirmed against Tables I-IV, VIII-IX, XI-XII; one magnitude error fixed:
        R5 investment incentive V at origination (no switching costs) corrected from
        $0.226 to $0.253 per Table VIII Panel A; all model equations (eqs. 1-15)
        verified term-by-term against pp. 574-582; parametric specifications on pp. 583-584
        confirmed; no em-dashes or colorful adjectives found.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13408
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2024-12-13"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the dynamic structural model of
price negotiation with search and switching frictions, and the maximum
likelihood estimation procedure: enough to know what it found and how, without
reading all 54 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13408).

## TL;DR

Using anonymized Canadian mortgage contract data linked with credit bureau
records (January 2014 to July 2019), Allen and Li document an "invest-and-harvest"
pricing pattern: lenders charge loyal renewers 4 bps more than new
borrowers, while switchers pay 7.9 bps less than stayers. To explain these
patterns, they build a T-period dynamic game of price negotiation in which
borrowers face search and switching frictions and lenders are forward-looking,
competing aggressively ex ante to build a customer base (invest) and
extracting rents later (harvest). Structural estimation yields average
search costs of \$386, switching costs of \$462 (new) and \$829 (renewers), and
lender investment incentives of \$843 per borrower. Counterfactual experiments
show that dynamic competition attenuates the anticompetitive effects
of market frictions relative to static model predictions, and that the
mortgage stress test unintentionally distorts lender pricing strategies.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Invest-and-harvest pricing documented**: loyal renewers pay 4.0 bps more than new borrowers; switchers pay 7.9 bps less; only 9.55% of renewers switch | Table I, p. 569 | Loyalty premium = 8.53 bps; switching rate at renewal = 9.55% |
| R2 | **OLS confirms invest-and-harvest**: loyal renewal dummy +4.00 bps; switch renewal dummy -3.93 bps vs purchase baseline, controlling for borrower and contract characteristics | Table II col (1), p. 570 | R-squared = 0.72; bond rates, FSA house prices, lender FE, year and region FE included |
| R3 | **Structural estimates**: average per-borrower search cost \$386 (1.3% of interest cost); average switching cost \$462 (new), \$829 (renewers); average lender investment incentive \$843; lender annual discount factor 0.93 | Table III, p. 587; Table IV, p. 588 | Likelihood ratio test rejects static model (delta=0) at 0.1% level; LR statistic = 91.39 |
| R4 | **Dynamic model predicts smaller consumer gains from removing frictions than static model**: removing both frictions saves borrowers 1.4% at origination and 2.5% at renewal (dynamic); static model overpredicts at 3.0% and 4.6% | Table VIII Panel C, p. 597 | Joint removal saves 58% (30%) more than sum of individual effects at origination (renewal): interaction effect |
| R5 | **Removing switching costs alone hurts new borrowers** (+0.2% total cost) because lender investment incentives fall; renewers benefit (-0.6%); static model always predicts savings for both | Table VIII col (2), p. 597 | Investment incentive V drops to \$0.253 from \$0.806 at origination when switching costs removed |
| R6 | **Investment incentive is driven by both frictions**: average V = \$843; increasing in switching cost; effect of switching cost on V is stronger when search costs are high | Table IV, p. 588; Table V col (2), p. 590 | Interaction coefficient (next-period switching cost x next-period search cost) = 0.39 (SE 0.0038), R-squared = 0.96 |
| R7 | **25-year FRMs benefit all players in the dynamic model**: borrowers save \$344 in total cost; lenders earn \$423 more over 25 years; static model reverses sign, predicting lenders earn \$1,163 less | Table IX, p. 602 | Dynamic model: interest rate indifference spread = 1.79 bps; static = 10.14 bps; both far below observed 91 bps swap-adjusted spread |
| R8 | **Mortgage stress test at renewal unintentionally distorts pricing**: unqualified borrowers (10.2%) pay 22 bps more and incur 7.8% higher total costs; switching rate falls from 20.2% to 3.0%; lender investment incentive at origination quadruples to \$3,967 | Table XI, p. 606; Table XII, p. 607 | Anticipatory effect lowers origination rates 4.6% for affected borrowers but share of borrowers in financial distress (GDS>39%) rises from 4.69% to 5.81% |

**Overall (paper's conclusion).** Dynamic competition attenuates the
anticompetitive effects of search and switching costs: each friction is less
harmful when the other is also present (interaction effect), and lenders'
forward-looking investment incentives lower current prices more than a static
model predicts. A static framework therefore systematically overpredicts
consumer gains from removing frictions and misidentifies who benefits from
policy changes. The invest-and-harvest pattern is consistent with
Dube, Hitsch, and Rossi (2009) and Shcherbakov (2016), who find switching
costs can lower equilibrium prices in dynamic frameworks. The paper extends
Allen, Clark, and Houde (2019) (origination-only) to a full repeated-interaction
setting. Identification uses an English auction approximation following
Woodward and Hall (2012) and Allen, Clark, and Houde (2019). The framework for
jointly modelling search and switching follows Honka (2014) but adds
supply-side forward-looking responses and negotiated pricing. The stress-test
results are analogous to Agarwal et al. (2023a), who document that HARP
unintentionally strengthened incumbency advantages in U.S. mortgage refinancing.

## Theory / model

Consider a borrower seeking a mortgage with a fixed rate for $$m$$ years,
amortizing over $$T \times m$$ years. The game has $$T$$ periods. In each period
$$t$$, the home bank $$h^t$$ (the lender from the previous period, or a
premortgage-relationship lender at $$t=1$$) moves first. The period is divided
into two stages: (i) an initial quote stage, and (ii) a negotiation stage.

**Borrower preferences** (p. 574, eq. 1). The borrower chooses the lender
$$j$$ from choice set $$n^t$$ that maximizes expected present value:

$$
\max_{j \in n^t} \; v^t_j - p^t_j + \rho U^{t+1}_j, \tag{1}
$$

where $$v^t_j$$ is the borrower's valuation for lender $$j$$'s mortgage,
$$p^t_j$$ is the interest payment, $$\rho$$ is the borrower's discount factor,
and $$U^{t+1}_j$$ is the continuation value of being attached to lender $$j$$
next period. Products are homogeneous except for a switching disutility $$\lambda^t$$:

$$
v^t_j = \begin{cases} \bar{v}^t, & j = h^t \\ \bar{v}^t - \lambda^t, & \text{otherwise.} \end{cases}
$$

**Lending costs** (p. 575). Lender $$j$$'s cost in period $$t$$ is:

$$
c^t_j = \begin{cases} c^t, & j = h^t \text{ in initial quote stage} \\ c^t + \omega^t_j, & \text{otherwise,} \end{cases}
$$

where $$c^t \sim F(\cdot)$$ is the common funding cost (observable to lenders
but not the econometrician), and $$\omega^t_j \sim G(\cdot)$$ is a mean-zero
IID idiosyncratic match-value component drawn at the negotiation stage.

**Negotiation stage: English auction** (p. 577, eqs. 2-5). With $$n^t \geq 2$$
lenders in the choice set, lenders compete in a descending procurement auction.
Lender $$j$$ stays in the auction so long as the present value of winning exceeds
the present value of losing (p. 577, eq. 2):

$$
\bar{b}^t - (c^t + \omega^t_j) + \delta W^{t+1}_j \geq \delta L^{t+1}_j, \tag{2}
$$

where $$\delta$$ is the lender discount factor, $$W^{t+1}_j$$ is the continuation
value of winning, and $$L^{t+1}_j$$ is the continuation value of losing. The
weakly dominant strategy is to bid one's reservation value. Lender $$j$$'s
equilibrium drop-out bid (p. 577, eq. 3) is:

$$
b^t_j(c^t, \omega^t_j) = c^t + \omega^t_j - \delta(W^{t+1} - L^{t+1}). \tag{3}
$$

The term $$V^{t+1} \equiv W^{t+1} - L^{t+1}$$ is the net continuation value (investment
incentive): lenders bid below cost in period $$t$$ to secure the incumbency
advantage in period $$t+1$$. The equilibrium price given the state vector $$s^t$$
is (p. 578, eq. 5):

$$
p^{t*}(s^t) = \begin{cases}
c^t - \delta V^{t+1} + \omega^t_{(2)} + \lambda, & \omega_{h^t} - \lambda = \omega^t_{(1)} \\
c^t - \delta V^{t+1} + \omega^t_{(2)}, & \omega_{h^t} - \lambda \leq \omega^t_{(2)},
\end{cases} \tag{5}
$$

where $$\omega_{h^t}$$ is the home bank's idiosyncratic match value and
$$\omega^t_{(k)}$$ denotes the $$k$$th-order statistic among the rival banks'
adjusted costs. The home bank charges more when it ranks first in expected
utility (first line), capturing the switching cost $$\lambda$$ as a rent.

**Initial quote stage** (p. 578-580, eqs. 6-12). Given the home bank's initial
offer $$p^t_0$$, the borrower's expected gain from searching $$l$$ lenders
(relative to accepting) is:

$$
\Delta^t_l = \begin{cases}
0, & l = 1 \\
p^t_0 - \lambda - (c^t - \delta V^{t+1} + E[\omega^t_{(2)} | n^t = l]), & l = 2, 3, \ldots, N,
\end{cases} \tag{6}
$$

and the expected marginal benefit of adding lender $$l$$ to the choice set is
$$\kappa^t_l \equiv \Delta^t_l - \Delta^t_{l-1}$$ (eq. 7). The borrower chooses
choice set size to maximize net expected benefit of searching (eq. 8):

$$
n^t = \text{argmax}_l \; \Delta^t_l - (l-1)\kappa^t, \quad l = 1, 2, \ldots, N. \tag{8}
$$

The home bank anticipates search probabilities and sets the optimal initial
quote $$p^{t*}_0$$ to maximize expected profit (eq. 11-12):

$$
\underbrace{p^{t*}_0 - c^t + \delta W^{t+1}}_{\text{Profit from } p_0}
= \underbrace{E[\pi^{t*}_h | n^t = 2]}_{\text{Auction profit}}
+ \underbrace{\Delta^{t*}_2}_{\text{Rent from } H(\cdot)},
\tag{12}
$$

showing that the optimal initial price equals the expected auction profit plus
the rents the home bank can extract from search frictions.

**Continuation values** (p. 581-582, eqs. 13-15). The investment incentive
$$V^t = W^t - L^t$$ is determined by the search cost distribution $$H(\cdot)$$,
the idiosyncratic cost distribution $$G(\cdot)$$, the switching cost $$\lambda$$,
and the number of available lenders $$N$$:

$$
V^t = [1 - H(\Delta^{t*}_2)]\bigl(\Delta^{t*}_2 + E[\max\{\omega_{-h^t} - (\omega_{h^t} - \lambda), 0\} | n^t = 2]\bigr) + \sum_{l=2}^N \Pr(n^t = l) E[\max\{\omega_{-h^t} - (\omega_{h^t} - \lambda), 0\} | n^t = l] - \sum_{l=2}^N \Pr(n^t = l) \frac{l-1}{N-1} E[\max\{\omega^t_{-j} - \omega^t_j, 0\} | n^t = l]. \tag{15}
$$

Since $$V^t$$ depends only on the distributions $$H(\cdot)$$, $$G(\cdot)$$, $$\lambda$$,
and $$N$$, which are assumed time-invariant, $$V^t$$ does not depend on future
continuation values, greatly simplifying the solution.

**Equilibrium** is a Markov perfect equilibrium: (i) the home bank sets
$$p^{t*}_0$$ to maximize expected profit; (ii) the borrower sets $$n^t$$ to maximize
net search benefit; (iii) lenders in the choice set bid $$b^t_j(\cdot)$$ as in
eq. (3).

## Method

The model is estimated by maximum likelihood on a sample of 34,554 Canadian
mortgage contracts. The method builds on `blp-demand` (parametric demand)
and `search-bargaining-otc` (price as second-order statistic from an English
auction). The structural approach is required because search decisions are
unobserved: only the final contract rate, the home bank's identity, and the
switching decision are observed.

**Parametric specification** (p. 583-584). Per-unit common cost $$c^t_i$$ is
drawn from a Normal distribution $$N(\mathbf{x}_i^t \boldsymbol{\beta}, \sigma_c^2)$$,
where $$\mathbf{x}_i^t$$ includes credit score, outstanding balance, bond rate,
amortization, income, house price, and year/region fixed effects. The
idiosyncratic cost for lender $$j$$ in the negotiation stage is $$M_i^t \omega_{i,j}$$,
where $$\omega_{i,j} \sim \text{T1EV}(\gamma \sigma_\omega, \sigma_\omega)$$ (Type 1 Extreme Value).

Search costs follow an exponential distribution with a mean determined by
the borrower's age, credit score, and FSA-level income (p. 584):

$$
H_i(\kappa) = 1 - \exp\!\left(-\frac{\kappa}{\alpha_i}\right), \quad
\alpha_i = \exp(\alpha_0 + \alpha_{\text{credit}} \, \text{Credit}_i + \alpha_{\text{inc}} \, \text{Income}_i + \alpha_{\text{age}} \, \text{Age}_i).
$$

Switching costs are a linear function of borrower type, origination amount,
age, credit score, and income (p. 584):

$$
\lambda_i = \lambda_0 + \lambda_{\text{new}} + M_i^1 \times (\lambda_{\text{credit}} \, \text{Credit}_i + \lambda_{\text{inc}} \, \text{Income}_i + \lambda_{\text{age}} \, \text{Age}_i).
$$

The vector $$(\sigma_c, \sigma_\omega, \delta, \boldsymbol{\alpha}, \boldsymbol{\beta}, \boldsymbol{\lambda})$$
is estimated by maximizing the likelihood of observed switching decisions and
interest rates given the equilibrium of the model. The likelihood ratio test
rejects the static model ($$\delta = 0$$) at the 0.1% significance level
(LR statistic = 91.39; Table III, p. 587).

**Identification** (p. 584-585). Search and switching frictions are separately
identified because they have different effects on the correlation between the
number of lenders ($$N$$) and switching probability. Search costs reduce
pass-through from $$N$$ to the number of quotes $$n$$; switching costs do not.
Variation in $$N$$ across local markets (FSA-level) and variation in borrower
characteristics that differentially predict search versus switching costs
enable separation of the two frictions. The lenders' discount factor $$\delta$$
is identified by the relationship between amortization period and price
(p. 585-586): longer amortization implies larger outstanding balance at
renewal and hence stronger investment incentives.

## Empirical specifications

The paper combines descriptive reduced-form evidence with structural estimation.

**Descriptive evidence (R1, R2).** OLS regressions of mortgage rates and
switching decisions on borrower/contract characteristics (Table II, p. 570),
with bond rates, FSA house prices, transaction volume, lender fixed effects,
and year and region fixed effects as controls. The estimating equation for
rates is:

$$
\text{Rate}_{it} = \alpha + \mathbf{x}_{it} \boldsymbol{\gamma} + \text{BondRate}_t + \text{HousePrice}_{fsa} + \text{LenderFE} + \text{Year} + \text{RegionFE} + \varepsilon_{it},
$$

with standard errors clustered at the FSA level. For switching probability,
the linear probability model replaces rate as the outcome.

**Structural estimation and model fit (R3, R6).** Maximum likelihood
estimation over 34,554 observations. Parameters estimated: $$(\sigma_c, \sigma_\omega, \delta, \boldsymbol{\alpha}, \boldsymbol{\beta}, \boldsymbol{\lambda})$$. Model fit is assessed by simulating 1,000 samples of 34,554 borrowers from the benchmark and single-friction models and comparing the distribution of predicted switching probabilities and interest rates to the data (Figure 4, p. 595). The benchmark dual-friction model reproduces data patterns; single-friction models fail (Table VII, p. 593).

**Counterfactual exercises (R4, R5, R7, R8).** Simulate 100,000 borrowers
from the estimated dynamic model under alternative market structures (no
switching cost; no search cost; no frictions; 25-year FRM; mortgage stress test).
For each, solve the equilibrium home bank offer, borrower search decision, and
auction outcome; compute total financing cost (interest plus search/switching
costs incurred). Panel C of Table VIII (p. 597) sums origination and renewal
costs to obtain the lifetime comparison.

**Reduced-form validation of mechanisms (R6).** OLS of the investment
incentive on model-estimated search costs, switching costs, and their
interaction (Table V, p. 590), using the full final sample of 34,554 contracts.
Column (3) shows interest rate is decreasing in the estimated investment
incentive (-7.74 per unit, SE 1.09), consistent with the forward-looking
pricing mechanism.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| TransUnion credit bureau data (Canada) | Monthly credit bureau records for Canadian population: borrower characteristics (age, credit score, address at FSA level, nonmortgage debt), mortgage identity, switching activities, financial inquiries | no page yet |
| OSFI / federally regulated lender administrative data | Contract-level mortgage information: lender identity, loan size, funding date, monthly payment, outstanding balance, mortgage rate, amortization, LTV, total debt-servicing ratio | no page yet |
| 2016 FSA-level demographic data | Population and average household income at the forward sortation area (FSA) level | no page yet |
| Teranet quarterly FSA-level house price index | Local house price controls | no page yet |

Sample: January 2014 to July 2019 (cross-section of new borrowers and first-time renewers). Final estimation sample: 34,554 contracts (17,277 purchase, 15,627 loyal renewal, 1,650 switch renewal). Restricted to insured FRM-5Y contracts, excluding broker transactions, movers, and contracts without matching administrative data.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13408) if you are:
studying mortgage market competition, search and switching frictions in
negotiated-price markets, or the welfare implications of market frictions
in the presence of forward-looking firms; extending the framework to markets
with endogenous refinancing (U.S.) or broker intermediation; or designing
counterfactual macroprudential policy experiments using a structural dynamic
model. The locators above point to the exact tables and figures for
each result.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(1). This distillation
was extracted by an LLM on 2026-06-06 and is **not human-verified or
independently reproduced**. The CC BY-NC 4.0 licence permits noncommercial
reproduction; the verbatim PDF is not hosted in this batch.

> **Citation.** Allen, Jason, and Shaoteng Li.
> "Dynamic Competition in Negotiated Price Markets."
> *The Journal of Finance* 80, no. 1 (February 2025): 561-614.
> DOI: 10.1111/jofi.13408. © 2024 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an extract-only distillation by the Institute for Automated Research;
> it does not reproduce the full text and is for noncommercial research purposes only.
