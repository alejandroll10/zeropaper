---
title: "The Actual Retail Price of Equity Trades: Schwarz, Barber, Huang, Jorion & Odean (2025)"
description: >-
  Distilled: A controlled trading experiment across six brokerage accounts at five brokers
  finds that mean account-level round-trip costs range from 7 to 46 basis points for
  identical simultaneous market orders, and that the entire cross-broker execution
  difference is attributable to market centers giving systematically different execution
  to different brokers for the same trades, not to broker venue-routing choices or
  payment for order flow. J. Finance 2025, CC BY-NC 4.0. Six core results with source
  locators, datasets used, the empirical design, and the regression specifications.
sidebar:
  label: Schwarz-Barber-Huang-Jorion-Odean 2025
  order: 1
tags: [paper-summary, market-microstructure, payment-for-order-flow, retail-trading,
       broker-execution, equities, panel-regression, experimental, peer-reviewed,
       unreplicated, data:wrds, data:taq]
paper:
  authors: Christopher Schwarz, Brad Barber, Xing Huang, Philippe Jorion, Terrance Odean
  authorList:
    - { family: Schwarz, given: Christopher G., orcid: "0000-0002-1466-8357", affiliation: University of California, Irvine }
    - { family: Barber, given: Brad M., affiliation: University of California, Davis }
    - { family: Huang, given: Xing, orcid: "0000-0003-4531-3070", affiliation: Washington University in St. Louis }
    - { family: Jorion, given: Philippe, orcid: "0000-0002-6727-7827", affiliation: University of California, Irvine }
    - { family: Odean, given: Terrance, orcid: "0000-0003-4747-9461", affiliation: University of California, Berkeley }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2507–2541
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13467
  jel:
    codes: [G12, G14, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ['Financial Markets and Investment Strategies', 'Auditing, Earnings Management, Governance', 'Corporate Finance and Governance']
  dataAccess: licensed-commercial
  outcome:
    - price improvement relative to NBBO (percent and cents per share)
    - round-trip transaction costs (basis points)
  outcomeClass: [asset-prices, household-finance]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-07-25; artifact p. 2507 states Creative Commons
    Attribution-NonCommercial License)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site; CC BY-NC VOR confirmed in Crossref metadata 2026-06-05)
  redistribution: extract-only (CC BY-NC 4.0 permits sharing with attribution for non-commercial use; PDF not hosted in this batch)
  resultsCount: 6
  citedByCount: 3
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [panel-regression, event-study]
    identification: randomized
  contributionType: [new-data, new-fact, measurement]
  introducesData: true
  mechanisms: [information-asymmetry, market-power]
  scope:
    region: US
    assetClass: US equities
    period: 2021-12..2022-06
    frequency: daily
    dataType: [market, administrative, experimental]
    granularity: [security, transaction]
    n: "74,801 trades (85,417 placed; 74,801 after filters) across 6 broker accounts, 128 stocks, Dec 21 2021 to Jun 9 2022"
  findings:
    - ref: R1
      outcome: price improvement relative to NBBO (percent of NBBO spread)
      metric: return-spread
      value: "TD Ameritrade 47.2%, Fidelity 35.8%, E*Trade 36.1%, Robinhood 26.8%, IBKR Lite 19.5%, IBKR Pro 18.8%; overall mean 31% of NBBO"
      direction: positive
      vsBenchmark: midpoint execution = 50% NBBO; NBBO execution = 0%
    - ref: R2
      outcome: round-trip transaction costs (basis points)
      metric: basis-points
      value: "TD Ameritrade -7.2 bps, Fidelity -19.7 bps, E*Trade -23.4 bps, Robinhood -31.4 bps, IBKR Lite -44.3 bps, IBKR Pro -46.2 bps"
      direction: mixed
      vsBenchmark: range of 39 bps between best (TD) and worst (IBKR Pro); worst-case NBBO execution = -61.9 bps
    - ref: R3
      outcome: price improvement relative to NBBO (percent of NBBO spread)
      metric: return-spread
      value: "TD vs RH: 20.5 pp (t=63.10**); TD vs IBKR Pro: 28.5 pp (t=47.36**); FD vs ET: -1.4 pp (t=-1.29, insignificant)"
      direction: mixed
      vsBenchmark: pairwise differences across all six accounts; most pairs significant at 1%
    - ref: R4
      outcome: price improvement relative to NBBO (percent of NBBO spread)
      metric: return-spread
      value: "Same-venue parallel trades (TD vs RH, same venue): TD PI = 47.4%, RH PI = 24.9%, diff = 22.5 pp; different-venue trades: diff = 22.5 pp"
      direction: positive
      vsBenchmark: PI difference is identical for same-venue and different-venue trade pairs, showing routing is not the driver
    - ref: R5
      outcome: price improvement relative to NBBO (percent of NBBO spread)
      metric: coefficient
      value: "Broker fixed effects alone: R2 = 15.5%; adding OIB deciles raises R2 to 25.3%; adding venue and stock FEs raises R2 to 27.6%. Broker dummy coefficients (vs TD baseline): FD = -0.113**, ET = -0.111**, RH = -0.204**, IBKR Lite = -0.278**, IBKR Pro = -0.284**"
      direction: negative
      vsBenchmark: "broker FEs absorbed by OIB variation: OIB decile range spans 0.31-0.36 of NBBO, similar to 0.28 broker range"
    - ref: R6
      outcome: price improvement relative to NBBO (percent of NBBO spread)
      metric: correlation
      value: "PFOF ranges from $0.00 to $0.215 cents/share across brokers; PI ranges from $2.78 to $7.84 cents/share; PFOF is ~1 order of magnitude smaller than PI; rank order of PI is not explained by PFOF rank"
      direction: none
      vsBenchmark: Fidelity and IBKR Pro both have PFOF=0 but rank differently on PI; rank correlation between PFOF and PI is not positive
  resultType: new-finding
  relatesTo:
    - { cite: 'Bakos et al. (2005)', doi: '10.1287/isre.1050.0064', relation: extends, note: 'earlier experiment at 3 brokers/1999; found no difference in overall PI across brokers; this paper uses 6 accounts, 5 brokers, and a much larger sample in the PFOF era' }
    - { cite: 'Kothari, So & Johnson (2021)', doi: '10.2139/ssrn.3976300', relation: cites, note: 'documents Robinhood PI = 33% NBBO for small trades using TAQ; this paper uses actual known trade direction' }
    - { cite: 'Levy (2022)', relation: extends, note: '1,000-trade experiment comparing Robinhood and TD Ameritrade; this paper uses 6 accounts, more heterogeneous PFOF, and identifies the within-venue mechanism' }
    - { cite: 'Kyle (1985)', doi: '10.2307/1913210', relation: cites, note: 'adverse selection / information asymmetry as the theoretical basis for spread variation and toxic order flow' }
    - { cite: 'Battalio & Holden (2001)', doi: '10.1016/s1386-4181(00)00015-x', relation: cites, note: 'one-for-one model of PFOF and PI; this paper tests and rejects PFOF as the primary driver' }
    - { cite: 'Eaton et al. (2022)', doi: '10.1016/j.jfineco.2022.08.002', relation: cites, note: 'broker-level order flow toxicity evidence from Robinhood outages; consistent with order flow quality as a driver of PI differences' }
  openQuestions:
    - "Whether variation in PI across brokers is explained by differences in the quality of order flow (toxicity as measured by price impact), which cannot be directly tested because the experiment's simultaneously-placed trades have the same price impact across brokers (pp. 2534-2537, §VI.B)."
    - "Whether the findings extend to limit orders, large institutional trades, and non-equity asset classes; the experiment covers only small market orders in U.S. equities during the day (pp. 2538, §VII)."
    - "Whether additional disclosure under SEC Rule 605 (expanded to include odd lots and broker-level breakdowns) would improve competition and close execution gaps; this is stated as the main policy implication and is not tested (pp. 2538-2539, §VII)."
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: "Full PDF read (pp. 2507-2541); six core results extracted with table/figure locators. Not human-verified. Not reproduced. Replication code is referenced in the paper (Supporting Information) but has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; R1-R6 magnitudes confirmed; corrected R2 locator from p. 2511 to p. 2529 for the $2.8B figure; corrected methods.family from descriptive to reduced-form-causal and methods.identification from descriptive to randomized (paper runs a controlled trading experiment that makes causal claims about the source of execution differences)."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13467
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-07-25"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the trading experiment design, and the regression
specifications that identify the source of price execution variation across brokers: enough to
know what was found and how, without reading all 35 pages. To replicate or extend, read the
full source at the [original](https://doi.org/10.1111/jofi.13467).

## TL;DR

The paper runs a controlled trading experiment opening six brokerage accounts at five major
U.S. retail brokers (TD Ameritrade, Fidelity, E\*Trade, Robinhood, Interactive Brokers Pro
and Lite) and placing approximately 85,000 simultaneous identical market orders in 128 stocks
over six months (December 2021 to June 2022). Mean price improvement (PI) relative to the
National Best Bid and Offer (NBBO) ranges from 47% of the NBBO spread (TD Ameritrade) to 19%
(IBKR Lite), and average round-trip costs range from 7 basis points to 46 basis points. The
key finding is that all of this variation is attributable to the same market centers (off-exchange
wholesalers) giving systematically different execution to different brokers for identical trades,
not to broker routing decisions or payment for order flow (PFOF). PFOF, whose variation across
brokers is an order of magnitude smaller than PI variation, explains almost none of the
cross-broker execution differences.

## Core results

Magnitudes and significance are as reported; `**` = 1%, `*` = 5%. Locators point into the
source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Cross-broker PI ranges from 19% to 47% of NBBO**, with mean round-trip costs from 7 to 46 bps; off-exchange execution averages 31% of NBBO vs. 17% for exchange trades | Table IV, p. 2527; Figure 1, p. 2510 | TD: PI\% = 47.2%, cost = -7.2 bps; FD: 35.8%, -19.7 bps; ET: 36.1%, -23.4 bps; RH: 26.8%, -31.4 bps; IB Lite: 19.5%, -44.3 bps; IB Pro: 18.8%, -46.2 bps |
| R2 | **Round-trip cost differences are economically large**: TD-to-worst-broker gap is 39 bps; 1 bp of aggregate retail trading cost equals ~$2.8 billion annually | Table IV, p. 2527; p. 2529 | Round-trip costs: TD -7.2 bps, IBKR Pro -46.2 bps; midpoint-execution benchmark = 0 bps; NBBO execution = -61.9 bps |
| R3 | **All pairwise broker differences are statistically significant** at the 1% level (except FD vs. ET, insignificant); execution quality varies highly significantly across all six accounts | Table V, p. 2529 | TD-RH diff = 20.5 pp (t=63.10\*\*); TD-IBKR Pro = 28.5 pp (t=47.36\*\*); FD-ET = -1.4 pp (t=-1.29, n.s.) |
| R4 | **The same market center (venue) gives systematically different execution to different brokers** for the exact same trade; routing venue choice does not explain the execution gap | Table VII, p. 2532 | TD vs. RH at same venue: PI diff = 22.5 pp; at different venues: PI diff = 22.5 pp; identical across venue conditions for all broker pairs |
| R5 | **OIB (order flow toxicity) can generate variation consistent with observed execution differences**, but broker fixed effects remain after controlling for OIB and venue/stock fixed effects | Table VIII, p. 2536 | Broker-FE model: R2 = 15.5%; OIB adds 10 pp; FE on RH vs. TD baseline = -0.204\*\* (robust to venue and stock FEs) |
| R6 | **PFOF does not explain cross-broker PI variation**: the rank order of execution quality is unrelated to PFOF levels, and PFOF per share is ~1/30th the size of PI per share | Figure 4, p. 2535; Table IV, p. 2527 | PFOF range: $0.000-$0.215 cents/share; PI range: $2.78-$7.84 cents/share; Fidelity (PFOF=0) has better execution than Robinhood (PFOF=$0.215/share) |

**Overall (paper's conclusion).** Retail investors trading "free" through commission-zero brokers
face real execution costs that differ by as much as 39 basis points per round trip across
identical simultaneous orders. The source of this dispersion is not broker routing but
wholesaler-level pricing: the same off-exchange market centers give different execution to
different brokers for the same trades. Payment for order flow explains almost none of the
variation. Better disclosure of execution quality at the broker level, particularly through
an expansion of SEC Rule 605 and Rule 606 reporting, is the proposed remedy.

## Theory / model

The paper has no formal model. The theoretical framework draws on three mechanisms from the
market microstructure literature:

**Adverse selection and order toxicity (Kyle (1985), Battalio and Holden (2001)).** Off-exchange
wholesalers profit from uninformed retail order flow. If order flow from a given broker is more
"toxic" (more directional, more informed), wholesalers face higher inventory risk and protect
themselves by offering lower PI. The paper tests whether observed OIB variation can account for
the PI variation across brokers.

**Inventory management (Stoll (1978)).** Dealers face costs from absorbing order imbalances. High
one-sided order flow from a broker creates inventory risk, leading to higher effective spreads.

**Competitive incentives and scale.** Wholesalers compete for order flow and cater to broker
objectives. Brokers with larger order-flow volumes (e.g., TD Ameritrade, which has more than
double the daily average trades of other brokers in the experiment) may receive better execution
because wholesalers compete more aggressively for their flow.

**Prior experimental evidence.** Bakos et al. (2005) ran an earlier experiment at three brokers
in 1999 and found no difference in overall PI, though total trading costs (including commissions)
differed. Kothari, So & Johnson (2021) study Robinhood trades in TAQ and report average PI of
33% NBBO for small trades using the actual known trade direction. Levy (2022) compares 1,000
trades at Robinhood and TD Ameritrade, finding a similar ranking to this paper. Eaton et al. (2022)
provide independent evidence that broker-level order flow toxicity affects market quality using
Robinhood platform outages as a natural experiment.

**Identification strategy.** The paper explicitly trades simultaneously across all broker accounts
in the same stock at the same time, so any latency difference is controlled by construction (and
verified empirically). This design isolates broker-level treatment effects from stock and time
variation. The within-venue test (Table VII) separates venue-routing from within-venue execution
differences.

## Method

The core identification relies on a **controlled trading experiment** rather than observational
data.

**Stock selection.** The CRSP universe (4,037 names as of June 2021) is stratified into 128 bins
by market capitalization, liquidity (share turnover), volatility, and price, with one stock
randomly selected per bin. Stocks with share price below $1 are excluded. The paper also
includes four high-retail-interest stocks (AMC, Tesla, Nio, Aurora Cannabis), several mega-caps
(Apple, Bank of America, NVIDIA, ExxonMobil, Google, Visa), and the top four Robinhood "mover"
stocks each week (pp. 2521-2522).

**Trade execution.** For API-accessible brokers (TD Ameritrade, Robinhood, E\*Trade, IBKR Pro),
trades are placed programmatically, randomizing submission order across buy and sell sides to
remove latency bias. For Fidelity and IBKR Lite, trades are placed manually in parallel.
Target order size is $100 per trade (full shares rounded to nearest whole share); robustness
checks use $1,000 and $5,000 targets. Positions are closed within 30 minutes. The experiment
runs from December 21, 2021 to June 9, 2022 (113 trading days). After filters (TAQ
matchability, 2-second simultaneity window, price $>$1), the final sample is 74,801 trades
(pp. 2522-2524).

**Price improvement (PI) measures** (equations 1a-b, p. 2518):

$$
\text{PI\$}_{\text{buy}} = \text{NBO} - P \quad \text{and} \quad \text{PI\$}_{\text{sell}} = P - \text{NBB} \tag{1a}
$$

$$
\text{PI\%} = \frac{\text{PI\$}}{\text{NBBO Spread}} \tag{1b}
$$

**Effective spread** (equations 2a-b, p. 2518):

$$
\text{ES\$}_{\text{buy}} = 2 \times (P - P_{\text{mid}}) \quad \text{and} \quad \text{ES\$}_{\text{sell}} = 2 \times (P_{\text{mid}} - P) \tag{2a}
$$

$$
\text{ES\%} = \frac{\text{ES\$}}{\text{NBBO Spread}} \tag{2b}
$$

where $$P$$ is the execution price, NBO (NBB) is the national best offer (bid), and $$P_{\text{mid}}$$
is the NBBO midpoint. Round-trip transaction costs are computed using midpoint prices at entry
and exit as the benchmark.

**Routing-venue data.** Under SEC Rule 606(b)(1), brokers must provide customer-specific routing
data upon request. The paper requests and obtains these data, identifying each trade's execution
venue, enabling the within-venue test in Table VII (p. 2532).

## Empirical specifications

**Pairwise broker comparison (R1-R3).** The headline result compares unconditional means of
PI\% across broker accounts (Table IV, p. 2527). Statistical significance is assessed via
Table V (pairwise differences), which reports mean PI\% differences for matched parallel
trades with standard errors clustered by stock:

$$
\text{PI\%}_{i,b} - \text{PI\%}_{i,b'} \quad \text{for each matched trade pair } (b, b') \tag{}
$$

The two-sample test uses only matched (simultaneous) trades between each broker pair.

**Same-venue vs. different-venue decomposition (R4).** Table VII splits all pairwise matched
trades into "Same" (both brokers routed to the same wholesale venue) and "Different" (routed to
distinct venues). The comparison tests whether the PI gap is driven by venue routing or by
within-venue differences:

$$
\overline{\text{PI\%}}_{\text{Broker A}} - \overline{\text{PI\%}}_{\text{Broker B}} \bigg|_{\text{Same venue}} \quad \text{vs.} \quad \overline{\text{PI\%}}_{\text{Broker A}} - \overline{\text{PI\%}}_{\text{Broker B}} \bigg|_{\text{Different venue}}
$$

Standard errors are clustered by stock (Table VII, p. 2532).

**Multivariate regression (R5).** Table VIII (p. 2536) regresses PI\% on broker account
dummies (TD Ameritrade omitted) and deciles of off-exchange order imbalance (OIB), separately
for buys and sells, with progressive addition of venue and stock fixed effects:

$$
\text{PI\%}_{i,j,t} = \sum_{b \neq \text{TD}} \beta_b \cdot \mathbf{1}[\text{Broker} = b]
+ \sum_{k=1}^{10} \gamma_k^{\text{Buy}} \cdot \text{OIB}_{k,t}^{\text{Buy}}
+ \sum_{k=1}^{10} \delta_k^{\text{Sell}} \cdot \text{OIB}_{k,t}^{\text{Sell}}
+ \text{FE} + \varepsilon_{i,j,t} \tag{}
$$

where OIB is computed as buy minus sell off-exchange orders in the same stock during the minute
of the trade, scaled by their sum (from TAQ, code "D"), assigned to deciles. Four models are
estimated: (1) broker FEs only, (2) broker FEs + OIB deciles, (3) + venue FEs, (4) + stock FEs.
Standard errors are clustered by stock.

**PFOF analysis (R6).** PFOF is obtained from SEC Rule 606 reports. The per-share PFOF is
plotted against per-share PI (Figure 4, p. 2535) to assess rank-order and magnitude
correspondence. No regression is estimated; the test is visual and descriptive, motivated by
the finding that PFOF ($0.001-$0.003/share) is an order of magnitude smaller than PI
($0.028-$0.078/share).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Authors' own trading experiment (85,417 trades in 6 broker accounts) | Primary outcome: execution price, PI, round-trip cost per trade | No page yet |
| TAQ (Trade and Quote Database) | Match trades to exchange/off-exchange execution; compute OIB; obtain execution venue codes | [TAQ](/wiki/licensed/taq/) (licensed) |
| CRSP (Center for Research in Security Prices) | Stock selection: universe stratification by market cap, liquidity, volatility, price | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| SEC Rule 606 reports (broker routing reports) | PFOF per share by broker and venue; routing shares to each wholesale venue | No page yet |
| SEC Rule 605 reports (market center execution reports) | Venue-level execution quality benchmarks (fraction with PI, average PI amounts) | No page yet |

Sample: December 21, 2021 to June 9, 2022 (113 trading days). 128 stocks; 74,801 trades in
the final cleaned sample ($15.4 million notional). Six broker accounts: TD Ameritrade, Fidelity,
E\*Trade, Robinhood, IBKR Lite, IBKR Pro. Order target: $100 per trade, market orders only.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13467) if you are:
studying retail market microstructure or the effects of PFOF; evaluating broker execution
quality methodologies or designing similar trading experiments; assessing the policy implications
of SEC Rule 605/606 disclosure reform; or interested in the within-venue vs. between-venue
decomposition of execution quality (Table VII is the key table). The Internet Appendix contains
additional robustness results (trade size sensitivity, latency tests, stock-by-stock
distributions).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5), October 2025. This distillation was
extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**.
The CC BY-NC 4.0 licence permits sharing with attribution for non-commercial use; the verbatim
PDF is not hosted in this batch.

> Schwarz, Christopher, Brad Barber, Xing Huang, Philippe Jorion, and Terrance Odean.
> "The 'Actual Retail Price' of Equity Trades."
> *The Journal of Finance* 80, no. 5 (October 2025): 2507-2541.
> DOI: 10.1111/jofi.13467. © 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
