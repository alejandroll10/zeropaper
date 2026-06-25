---
title: "Pricing Poseidon: Kruttli, Roth Tran & Watugala (2025)"
description: >-
  Distilled: Firms in hurricane landfall regions experience implied volatility
  increases of up to 18%, reflecting persistent impact uncertainty that takes
  months to resolve; investors systematically underreact to this uncertainty
  until Hurricane Sandy (2012) served as a salient learning event. J. Finance
  2025, CC BY-NC 4.0. Seven core results with source locators, datasets used,
  the theoretical model, and the empirical specifications.
sidebar:
  label: Kruttli-RothTran-Watugala 2025
  order: 1
tags: [paper-summary, climate-finance, asset-pricing, options, volatility,
       extreme-weather, hurricanes, difference-in-differences, panel-regression,
       text-as-data, peer-reviewed, unreplicated,
       data:wrds, data:optionmetrics, data:noaa-hurricane, data:nets, data:refinitiv-transcripts]
paper:
  authors: Mathias S. Kruttli, Brigitte Roth Tran, Sumudu W. Watugala
  authorList:
    - { family: Kruttli, given: Mathias S., orcid: "0000-0003-1589-6578", affiliation: Kelley School of Business, Indiana University }
    - { family: Roth Tran, given: Brigitte, orcid: "0000-0003-3123-315X", affiliation: Federal Reserve Bank of San Francisco }
    - { family: Watugala, given: Sumudu W., orcid: "0000-0003-4074-8163", affiliation: Kelley School of Business, Indiana University }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 783–832
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13416
  jel:
    codes: [G12, G14, Q54]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Market Dynamics and Volatility
    - Financial Markets and Investment Strategies
    - Insurance and Financial Risk Management
  dataAccess: licensed-commercial
  outcome:
    - implied volatility of firm stock options around hurricane landfall
    - volatility risk premium (VRP) of hit firms relative to controls
    - cumulative abnormal stock returns of hit firms
    - analyst call discussion frequency about hurricane channels
  outcomeClass: [security-returns, asset-prices]
  license: "CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0, start 2025-01-13)"
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "blocked-paywall (Wiley site wrapper; CC BY-NC VOR licence confirmed in Crossref DOI metadata 2026-06-06)"
  redistribution: extract-only (CC BY-NC 4.0 permits non-commercial reproduction; PDF not hosted in this batch)
  resultsCount: 7
  citedByCount: 63

  methods:
    role: both
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, panel-regression, event-study, text-classification]
    identification: natural-experiment
  contributionType: [new-fact, new-theory, measurement]
  mechanisms: [learning, behavioral-bias, information-asymmetry]
  scope:
    region: US
    assetClass: US equities (non-financial, Amex/NASDAQ/NYSE)
    period: 1996-01..2019-12
    frequency: daily
    dataType: [market, text, other]
    granularity: [firm, security]
    n: "3,254 unique firms; 37 hurricane landfalls (1996-2019); ~38,886 firm-hurricane observations (200-mile radius sample)"

  findings:
    - ref: R1
      outcome: implied volatility of firm stock options around hurricane landfall
      metric: coefficient
      value: "lambda = 7.676 (t=3.178) for 200-mile radius, one month post-landfall; up to 17.728 (t=1.883) for 50-mile radius"
      direction: positive
      vsBenchmark: "change relative to pre-inception IV of control firms with zero landfall exposure"
    - ref: R2
      outcome: implied volatility of firm stock options around hurricane landfall
      metric: coefficient
      value: "IV effect significant for up to ~3 months (60 trading days) post-landfall; peaks at ~8% one month after landfall (Figure 5, Panel A)"
      direction: positive
      vsBenchmark: "IV gradually declines from peak ~30 trading days after landfall but remains significant for just over three months"
    - ref: R3
      outcome: volatility risk premium (VRP) of hit firms relative to controls
      metric: coefficient
      value: "VRP lambda = -6.035 (t=-4.414) for 200-mile, one week post-landfall; up to -21.463 (t=-2.139) for 50-mile radius (Table IV)"
      direction: negative
      vsBenchmark: "negative VRP indicates IV understates subsequent realized volatility; investors underreact"
    - ref: R4
      outcome: volatility risk premium (VRP) of hit firms relative to controls
      metric: coefficient
      value: "Post-Sandy interaction (Table V): at one week, +4.620 (t=1.651, col 1) to +3.677 (t=1.761, col 2), mostly insignificant; at one month, +7.572*** (t=3.132, col 5); net VRP effect turns 1.9-6.0% positive at longer horizons in post-Sandy subsample"
      direction: positive
      vsBenchmark: "Pre-Sandy VRP remains significantly negative for ~1.5 months; post-Sandy VRP not distinguishable from zero (Figure 6)"
    - ref: R5
      outcome: cumulative abnormal stock returns of hit firms
      metric: car
      value: "Pre-Sandy: lambda = -0.022 to 0.127, all insignificant (t-stats -0.039 to 0.188); Post-Sandy: +4.599*** (t=3.157, 20-day) to +6.965*** (t=4.258, 40-day) (Table VII)"
      direction: mixed
      vsBenchmark: "No return premium pre-Sandy; positive and significant return premium post-Sandy (Panel B)"
    - ref: R6
      outcome: analyst call discussion frequency about hurricane channels
      metric: coefficient
      value: "200-mile: 4.037 total hurricane paragraphs (t=9.544); by channel: business interruption 1.157 (t=6.131), physical damages 1.520 (t=6.859), insurance 0.369 (t=2.445), supply 0.213 (t=2.193), demand 0.574 (t=4.106) (Table VI)"
      direction: positive
      vsBenchmark: "50-mile: 15 additional paragraphs over 6 months; physical damages and business interruption dominate"
    - ref: R7
      outcome: implied volatility of firm stock options around hurricane landfall
      metric: coefficient
      value: "Pre-landfall forecast: IV increases up to 22% when wind speed probability reaches 50% (Table VIII, col. 5); statistically significant across all days and probability thresholds"
      direction: positive
      vsBenchmark: "IV response increases with both proximity to landfall (days) and forecast probability; seasonal forecasts show no significant response (Table IX)"

  resultType: new-finding

  relatesTo:
    - { cite: "Bloom (2009)", doi: '10.3982/ecta6248', relation: builds-on, note: "uses implied volatility as the measure of expected uncertainty, following Bloom's (2009) definition of uncertainty as expected volatility" }
    - { cite: "Kelly, Pastor, and Veronesi (2016)", doi: '10.1111/jofi.12406', relation: extends, note: "adapts their VRP methodology from international index options to single-stock options for extreme weather events" }
    - { cite: "Merton (1987)", doi: '10.1111/j.1540-6261.1987.tb04565.x', relation: builds-on, note: "theoretical framework extends Merton (1987) to show idiosyncratic volatility can be priced when investors are underdiversified" }
    - { cite: "Pastor and Veronesi (2012)", doi: '10.1111/j.1540-6261.2012.01746.x', relation: cites, note: "defines uncertainty in the spirit of Pastor and Veronesi (2012, 2013) as expected volatility of unpredictable disturbances" }
    - { cite: "Jurado, Ludvigson, and Ng (2015)", doi: '10.1257/aer.20131193', relation: cites, note: "uncertainty definition consistent with Jurado, Ludvigson, and Ng (2015)" }
    - { cite: "Lochstoer and Muir (2022)", doi: '10.1111/jofi.13120', relation: cites, note: "VRP definition and underreaction interpretation follows Lochstoer and Muir (2022)" }
    - { cite: "Sautner, van Lent, Vilkov, and Zhang (2023a)", relation: cites, note: "uses analyst call transcripts to measure firm-level climate exposure as in Sautner et al. (2023a, 2023b)" }
    - { cite: "Malmendier and Nagel (2016)", doi: '10.1093/qje/qjv037', relation: cites, note: "personal experience hypothesis for Sandy's saliency effect follows Malmendier and Nagel (2016) on inflation experiences" }

  openQuestions:
    - "Whether the saliency channel via Sandy generalizes to other unfamiliar extreme weather events (floods, wildfires) in locations that have not previously experienced major hurricanes; the paper documents one salient event and leaves generalization open (p. 829)."
    - "Whether investors can distinguish between the short-term forecast responses (which the paper shows are priced) and longer-term seasonal forecasts (which are not priced), and how the pricing of climate risks evolves as climate change shifts the distribution of extreme events (p. 824, p. 829)."
    - "How mandatory climate-risk disclosures by firms about their business continuity plans, insurance coverage, and supply chain exposures could reduce uncertainty and improve pricing efficiency (p. 787, p. 829)."

  replicationCode:
    status: available

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: "2026-06-06", role: extracted, note: "Full text read (pp. 783-832); seven core results extracted from the PDF. Not human-verified. Not reproduced. Replication code referenced at end of paper but not run here." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: "2026-06-06", role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; fixed R4 Core results row (Table V one-week post-Sandy interaction corrected from 4.599/t=3.157 to 4.620/t=1.651; the 4.599/t=3.157 value belongs to Table VII) and R4/R5 findings values (cross-table mix of Table V and Table VII magnitudes corrected; R5 range lower bound corrected to 4.599 t=3.157 at 20 days). All equations (eqs 1-11) verified term-by-term; no other errors found." }

  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13416", checked: "2026-06-06", by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-01-13" }
---

**What this is.** The paper's core results, the theoretical model it builds, and the empirical specifications: enough to know what it found and how, without reading all 50 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13416).

## TL;DR

Extreme weather events generate substantial firm-level uncertainty. Using single-stock options on firms with establishments in hurricane landfall regions (1996-2019, 37 hurricanes, 3,254 firms), the paper documents that implied volatilities rise up to 18% after a hurricane hit and remain elevated for several months, reflecting slow resolution of impact uncertainty. Despite these large increases in expected volatility, investors systematically underreact: the volatility risk premium (VRP) is significantly negative for hit firms, meaning ex ante implied volatility understates subsequent realized volatility (following the VRP definition of Lochstoer and Muir (2022)). This underreaction diminishes after Hurricane Sandy (2012), a salient event that struck the US financial center. Post-Sandy, hurricane uncertainty is priced efficiently and generates a positive expected return premium, consistent with personal experience effects documented by Malmendier and Nagel (2016). Textual analysis of analyst calls (using transcript methodology following Sautner, van Lent, Vilkov, and Zhang (2023a)) identifies five channels of uncertainty: business interruption, physical damages, insurance, supply, and demand.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Implied volatility increases significantly after hurricane landfall** for exposed firms; effect is largest close to the hurricane eye | Table III, p. 806 | 200-mile: lambda = 7.676 (t=3.178) at one month; 100-mile: 9.408 (t=2.801); 50-mile: 17.728\* (t=1.883) at one month post-landfall |
| R2 | **Impact uncertainty persists for about three months** after landfall; IV peaks at ~1 month and declines but remains significant | Figure 5 Panel A, p. 808 | IV effect significant for ~60 trading days (three months) post-landfall; peaks at ~8% around 30 trading days; discussion of hurricanes in analyst calls remains elevated for ~3 months (Panel B) |
| R3 | **Investors underreact to hurricane uncertainty before Sandy**: VRP of hit firms is significantly negative, implying implied volatility understates realized volatility | Table IV, p. 810 | 200-mile: VRP lambda = -6.035\*\*\* (t=-4.414) at one week; -5.315\*\*\* (t=-3.043) at one month; 50-mile: -21.463\*\*\* (t=-2.139) at one week |
| R4 | **After Hurricane Sandy, underreaction diminishes**: VRP effect reverses; post-Sandy hit firms price the uncertainty correctly or at a premium | Table V, p. 812; Figure 6, p. 813 | Post-Sandy interaction: at one week, +4.620 (t=1.651, insignificant); at one month, +7.572\*\*\* (t=3.132, col 5); net VRP effect turns 1.9-6.0% positive in post-Sandy period; pre-Sandy VRP negative for ~30 trading days |
| R5 | **Hurricane uncertainty affects expected returns only post-Sandy**: pre-Sandy CAR is insignificant; post-Sandy CAR is significantly positive for exposed firms | Table VII, p. 819 | Pre-Sandy: lambda = -0.022 to 0.127, all insignificant; Post-Sandy (x PostSandy): lambda = +4.599\*\*\* (t=3.157, 20-day col 1) to +6.965\*\*\* (t=4.258, 40-day col 7) |
| R6 | **Five economic channels drive hurricane uncertainty**: business interruption and physical damages dominate; insurance uncertainty is also significant | Table VI, p. 815 | 200-mile: total hurricane paragraphs +4.037\*\*\* (t=9.544); business interruption +1.157\*\*\* (t=6.131), physical damages +1.520\*\*\* (t=6.859), insurance +0.369\*\* (t=2.445) per unit of landfall exposure over 6 months |
| R7 | **Investors react to pre-landfall forecasts**: IV rises by up to 22% when storm wind speed probability reaches 50%; investors do not react to seasonal hurricane forecasts | Table VIII, p. 821; Table IX, p. 823 | Forecast exposure coefficient increases from ~4.6% (1%, one day out) to 21.6%\*\*\* (50%, one day out); seasonal forecasts: all interaction coefficients insignificant |

**Overall (paper's conclusion).** Hurricanes generate substantial, slow-to-resolve firm-level uncertainty that investors price with systematic underreaction until a particularly salient event (Sandy) improved informational efficiency. Idiosyncratic extreme weather shocks affect firms' cost of capital, which amplifies their real effects by tightening financing constraints when capital is most needed for rebuilding. Markets are unlikely to efficiently price unfamiliar climatic risks without direct experience.

## Theory / model

The paper adapts Merton (1987) to show how extreme weather uncertainty can affect expected returns even when the shock is purely idiosyncratic. This builds on the theoretical insight that idiosyncratic volatility can be priced when investors are underdiversified, formalized by Levy (1978) and Merton (1987). The theoretical framework (Internet Appendix Section I, summarized on p. 798-802) distinguishes two components of uncertainty, with uncertainty defined as expected volatility in the spirit of Bloom (2009), Pastor and Veronesi (2012), and Jurado, Ludvigson, and Ng (2015):

**Impact uncertainty.** When a firm is hit by an extreme weather event, its one-period return is (equation 3, p. 798):

$$
\tilde{R}_{i,t+1} = \bar{R}_i + b_i \tilde{Y}_{t+1} + \sigma_i \tilde{\epsilon}_{i,t+1} + \tilde{g}_{i,t+1}
$$

where $$\tilde{g}_{i,t+1}$$ is a random variable capturing the impact of the event on firm $$i$$, distributed with mean $$\mu_{g,i}$$ and variance $$\sigma_{g,i}^2$$. The term $$\sigma_{g,i}^2$$ captures impact uncertainty: the variance of the unpredictable disturbance once the event is known to have occurred.

**Incidence uncertainty.** Before the event occurs, there is also uncertainty about whether the event will hit. Expanding the return specification to include a Bernoulli hit indicator $$\tilde{\theta}_{i,t+1} \sim B(1,\phi)$$ (equation 4, p. 801):

$$
\tilde{R}_{i,t+1} = \bar{R}_i + b_i \tilde{Y}_{t+1} + \sigma_i \tilde{\epsilon}_{i,t+1} + \tilde{g}_{i,t+1} \tilde{\theta}_{i,t+1}
$$

The total return variance is then (equation 5, p. 801):

$$
\text{Var}_t(\tilde{R}_{i,t+1}) = b_i^2 + \sigma_i^2 + \sigma_{g,i}^2 \phi + \mu_{g,i}^2 \phi(1-\phi)
$$

where $$\sigma_{g,i}^2 \phi$$ is the expected impact uncertainty and $$\mu_{g,i}^2 \phi(1-\phi)$$ is the incidence uncertainty. Incidence uncertainty is highest when $$\phi = 0.5$$.

**Cost-of-capital channel.** In the extended Merton (1987) framework (Internet Appendix Section I), when investors hold underdiversified portfolios, shocks to expected idiosyncratic volatility affect the equity risk premium. The expected return on firm $$i$$ increases when the idiosyncratic variance of hit firms rises relative to control firms, providing the theoretical basis for the return premium tests in Section III.D.

**Identification logic.** The key identification assumption is that the timing and geographic incidence of hurricanes are exogenous to firm-specific conditions. Because a hurricane affects a subset of US firms (those in the landfall region), it creates a within-event treatment/control split: exposed firms experience higher uncertainty, unexposed firms serve as controls. Hurricanes are identified in real time via NOAA data, so the landfall region is known to investors as it happens.

## Method

The paper uses a **continuous-treatment difference-in-differences** (DiD) design at the firm-hurricane level, pooling 37 hurricane events from 1996-2019. The key methodological choices are:

**Firm exposure measurement.** Firm $$i$$'s exposure to hurricane $$h$$ is its share of establishments in the hurricane landfall region (equation 6, p. 802):

$$
\textit{LandfallRegionExposure}_{i,R,h} = \sum_c (\textit{FirmCountyExposure}_{i,c} \times I_{c \in L_{R,h}})
$$

where $$\textit{FirmCountyExposure}_{i,c}$$ is the share of firm $$i$$'s establishments in county $$c$$, and $$I_{c \in L_{R,h}}$$ is an indicator for county $$c$$ being within radius $$R$$ of the hurricane eye at landfall. The main analysis uses $$R = 200$$ miles, validated against smaller radii (100, 50 miles).

**Implied volatility measure.** Average implied volatility across options at the nearest-to-maturity expiry $$M$$, which adapts the measure used by Kelly, Pastor, and Veronesi (2016) for options on international stock indices to the single-stock setting (equation 1, p. 795):

$$
IV_{i,t} = IV_{i,t,M} = \frac{1}{Z} \sum_{z=1}^Z IV_{i,z,t,M}
$$

for $$Z$$ valid options satisfying: standard settlement; positive open interest; positive bid price and bid-ask spread; non-missing IV; 7-200 calendar days to expiry; $$|\delta| \in [0.2, 0.5]$$. Options are slightly out-of-the-money for liquidity. Model-based (binomial tree) implied volatilities from OptionMetrics are used; results are robust to model-free IV (Internet Appendix Section IV).

**Volatility risk premium.** VRP is the difference between ex ante implied and ex post realized volatility over the remaining life of the option (equation 2, p. 796):

$$
VRP_{i,t} = VRP_{i,t,M} = IV_{i,t,M} - RV_{i,t,M}
$$

A negative VRP for hit firms relative to controls means investors underestimate future realized volatility, consistent with underreaction.

The `difference-in-differences` and `panel-regression` estimation approaches, the `text-classification` dictionary methodology for analyst calls, and the `event-study` design for CARs are the core technical primitives.

## Empirical specifications

**Baseline implied volatility regression (Section III.A, eq. 7, p. 804).** For each hurricane entering as a separate time period:

$$
\log\!\left(\frac{IV_{i,T_L^h+\tau}}{IV_{i,T_0^h-1}}\right) = \lambda_{L,R,\tau} \cdot \textit{LandfallRegionExposure}_{i,R,h} + \pi_h + \psi_{\textit{Ind}} + \epsilon_{i,h,\tau}
$$

Dependent variable: log change in implied volatility from the day before hurricane inception ($$T_0^h - 1$$) to $$\tau$$ trading days after landfall. $$\pi_h$$ are hurricane fixed effects (equivalent to time FEs with one period per hurricane). $$\psi_{\textit{Ind}}$$ are industry FEs or industry x time FEs. Standard errors clustered by county (each firm assigned to its largest-establishment county). Ties R1 and R2.

**VRP regression (Section III.B, eq. 8, p. 807):**

$$
\overline{VRP}_{i,T_L^h+\tau} = \lambda^{VRP}_{L,R,\tau} \cdot \textit{LandfallRegionExposure}_{i,R,h} + \pi_h + \Psi_i + \epsilon_{i,h,\tau}
$$

Dependent variable: average VRP from landfall to $$\tau$$ days after. $$\Psi_i$$ is a firm fixed effect (absorbs level differences in VRP across firms; cannot use pre-inception subtraction because realized volatility over remaining option life already includes the hurricane). Ties R3-R4.

**Post-Sandy interaction (Table V):** Equation (8) augmented with $$\textit{LandfallRegionExposure}_{i,R,h} \times \textit{PostSandy}_h$$, where $$\textit{PostSandy}_h = 1$$ for hurricanes from 2013 onward.

**Abnormal return regression (Section III.D, eq. 10, p. 818):**

$$
CAR_{i,h,T_L^h+\tau:T_L^h+\tau+\textit{ReturnHorizon}} = \lambda^{Ret}_{L,R,\tau} \cdot \textit{LandfallRegionExposure}_{i,R,h} + \pi_h + \psi_{\textit{Ind}} + \epsilon_{i,h,\tau}
$$

CARs are relative to the Fama and French (2015) five-factor model, estimated in first stage using 120 trading days before hurricane inception. Starting point $$\tau = 30$$ (when IV peaks). Return horizons of 20, 30, 40 trading days. Ties R5.

**Economic channels regression (Section III.C, eq. 9, p. 814):**

$$
\textit{HurricaneDiscussions}_{i,T_L^h+120} = \lambda^{EC}_{L,R} \cdot \textit{LandfallRegionExposure}_{i,R,h} + \pi_h + \psi_{\textit{Ind}} + \varepsilon_{i,h}
$$

Dependent variable: number of analyst call paragraphs discussing hurricane and one of five economic channels (business interruption, physical damages, insurance, supply, demand) over 120 trading days after landfall. Dictionary-based classification with LDA validation. Ties R6.

**Forecast path regression (Section III.E, eq. 11, p. 820):**

$$
\log\!\left(\frac{IV_{i,T_L^h-\Gamma}}{IV_{i,T_0^h-1}}\right) = \lambda_{F,P,\Gamma} \cdot \textit{ForecastExposure}_{i,P,T_L^h-\Gamma} + \pi_h + \psi_{\textit{Ind}} + \epsilon_{i,h,\Gamma}
$$

Dependent variable: log IV change from inception to $$\Gamma$$ days before landfall. $$\textit{ForecastExposure}$$ is share of firm establishments in counties with forecast wind speed probability $$\geq P$$. Estimated for $$\Gamma \in \{1,\ldots,5\}$$ days and $$P \in \{1\%, 10\%, 20\%, 40\%, 50\%\}$$. Ties R7.

All regressions cluster standard errors by county (Petersen (2009)) based on each firm's largest establishment share.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| NOAA hurricane track data (National Hurricane Center) | Identifies 37 hurricane landfalls (1996-2019), eye location at 6-hour intervals, wind speed probability forecast advisories, seasonal outlook probabilities | [NOAA hurricanes](/wiki/datasets/noaa-hurricane/) |
| NETS (National Establishment Time Series) | Firm establishment locations by county, annual frequency; used to construct LandfallRegionExposure | [NETS](/wiki/licensed/nets/) (licensed) |
| OptionMetrics (single-stock options) | Daily implied volatilities and VRP for US-listed firms; data 1996-2019 | no page yet |
| CRSP/Compustat Merged (via WRDS) | Stock returns, market capitalization, SIC codes, share prices for sample construction and CAR estimation | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Refinitiv (now LSEG) analyst call transcripts | Transcripts of analyst-investor-management calls; textual analysis of hurricane channels over 120 days post-landfall; data 2002-2019, 28 hurricanes | no page yet |
| S&P Global Market Intelligence | State-level property and casualty insurance premiums (Section IV.E extension only) | no page yet |

Sample: 1996-2019 (linked sample start = 1996, first year OptionMetrics data available); 3,254 unique firms; 1,799 hit firms (at least one hurricane with establishment share >= 25%); ~38,886 firm-hurricane observations at 200-mile radius baseline.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13416) if you are: examining the theoretical proof that idiosyncratic volatility can be priced (Internet Appendix Section I); studying VRP dynamics and the robustness of the model-free IV results (Internet Appendix Sections III-IV); exploring industry heterogeneity, tail effects (Section IV.D), or the insurance firm extension (Section IV.E); or extending the methodology to floods, snowstorms, or tornadoes (Table X). The locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The CC BY-NC 4.0 licence permits non-commercial reproduction with attribution.

> **Attribution (CC BY-NC 4.0).** Kruttli, Mathias S., Brigitte Roth Tran, and Sumudu W. Watugala.
> "Pricing Poseidon: Extreme Weather Uncertainty and Firm Return Dynamics."
> *The Journal of Finance* 80, no. 2 (April 2025): 783-832.
> DOI: 10.1111/jofi.13416. © 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
