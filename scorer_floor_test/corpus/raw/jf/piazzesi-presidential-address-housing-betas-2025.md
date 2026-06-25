---
title: "Presidential Address: Housing Betas: Piazzesi (2025)"
description: >-
  Distilled: Housing betas (the stock-market beta of housing returns) were
  negative before the Global Financial Crisis and turned positive after it,
  despite highly correlated cashflow growth rates across the two asset
  classes. A heterogeneous-agent model with segmented and credit-connected
  markets explains the pre-GFC puzzle. J. Finance 2025, paywalled. Eight
  core results with source locators, the model (OLG segmented-markets Lucas
  tree), and the propositions on negative comovement.
sidebar:
  label: Piazzesi 2025
  order: 1
tags: [paper-summary, asset-pricing, housing, macro, real-estate, comovement,
       credit-markets, overlapping-generations, structural, peer-reviewed,
       unreplicated, data:shiller-data,
       data:flow-of-funds, data:nipa, data:corelogic]
paper:
  authors: Monika Piazzesi
  authorList:
    - { family: Piazzesi, given: Monika, affiliation: "Stanford University, CEPR & NBER" }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3103–3136
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.70000
  jel:
    codes: [G12, R31, E44]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Housing Market and Economics', 'Financial Literacy, Pension, Retirement Analysis']
  dataAccess: licensed-commercial
  outcome:
    - housing beta (stock-market beta of housing returns over decade-long holding periods)
    - comovement of stock and housing returns
    - price-dividend ratios for stocks and housing
    - return on levered housing
  outcomeClass: [asset-prices, security-returns]
  license: >-
    Wiley VOR terms (http://onlinelibrary.wiley.com/termsAndConditions#vor);
    confirmed via Crossref DOI metadata content-version vor, delay-in-days 0,
    start 2025-10-17. No Creative Commons licence found; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site wrapper; confirmed paywalled via Crossref DOI metadata 2026-06-03)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 2
  methods:
    role: both
    contributes: segmented-markets-housing-beta
    family: structural
    buildsFrom: [overlapping-generations, life-cycle-model, segmented-markets-lucas-tree]
    identification: structural
  contributionType: [new-fact, new-theory]
  mechanisms: [collateral, risk-sharing]
  scope:
    region: US
    assetClass: US equities and residential real estate
    period: 1930-01..2024-12
    frequency: annual
    dataType: [market, accounting]
    granularity: [aggregate, individual]
    n: "annual, 1930-2024 (returns and cashflows)"
  findings:
    - { ref: R1, outcome: "housing beta (stock-market beta of housing returns over decade-long holding periods)", metric: beta, value: "roughly -0.2 to 0 in 1960s-1990s; peaks near +1 around 2020", direction: mixed, vsBenchmark: "negative pre-GFC, positive post-GFC" }
    - { ref: R2, outcome: "comovement of stock and housing returns", metric: correlation, value: "80% pre-GFC (1930-GFC subsample); 59% full sample (1939-2024)", direction: positive }
    - { ref: R3, outcome: "return on levered housing", metric: beta, value: "below -1 during 1980s-1990s", direction: negative, vsBenchmark: "more negative than unlevered housing beta" }
    - { ref: R4, outcome: "housing beta (stock-market beta of housing returns over decade-long holding periods)", metric: return-spread, value: "cross-sectional annualized capital gains span -40% to +60%; avg 6.7%/yr (San Francisco) vs 40 bp (Huntsville)", direction: mixed }
  resultType: new-finding
  relatesTo:
    - { cite: 'Piazzesi and Schneider (2016)', doi: '10.1016/bs.hesmac.2016.06.003', relation: builds-on, note: 'survey of the housing and macroeconomics literature that motivates studying stocks and housing jointly (p. 3103)' }
    - { cite: 'Piazzesi and Schneider (2007)', relation: builds-on, note: 'search model for momentum traders in housing; the current paper extends the heterogeneous-agent framework (p. 3111)' }
    - { cite: 'Landvoigt, Piazzesi and Schneider (2015)', doi: '10.1257/aer.20111662', relation: builds-on, note: 'San Diego housing markets model with segmented markets and credit; quantitative predecessor to the two-type OLG framework here (p. 3112)' }
    - { cite: 'Piazzesi and Schneider (2008)', doi: '10.7208/chicago/9780226092126.003.0005', relation: builds-on, note: 'inflation illusion, credit, and asset pricing; multi-country evidence on 1970s housing boom and stock slump (p. 3125)' }
    - { cite: 'Jorda, Schularick and Taylor (2019)', relation: cites, note: 'document a high Sharpe ratio of one for aggregate housing returns in U.S. postwar data (p. 3114)' }
    - { cite: 'Campbell and Viceira (1999)', relation: builds-on, note: 'derive the Merton portfolio weight as an approximate solution to the log portfolio problem; adopted in household optimization here (p. 3117)' }
    - { cite: 'Mankiw and Weil (1989)', relation: cites, note: 'Baby Boom demographics and the 1970s-80s housing surge; candidate for post-GFC positive comovement via higher savings (p. 3127)' }
    - { cite: 'Iacoviello (2005)', doi: '10.1257/0002828054201477', relation: cites, note: 'house prices, borrowing constraints, and monetary policy; cited for single-market credit-channel quantitative work (p. 3124)' }
  openQuestions:
    - 'How to quantitatively assess which channels (credit demand, credit supply, demographics, institutional investors, foreign investors) matter most empirically; the paper establishes qualitative mechanisms only (p. 3128).'
    - 'Extension to additional OLG cohorts is needed: with two-period lifetimes credit flows only from young stockholders to young homebuyers, while household portfolio data show bonds are held primarily by older households (p. 3128).'
    - 'Jointly analyzing time variation in long bond betas and housing betas, since bond betas reflect borrowing costs and can amplify negative housing betas, is left for future work (p. 3128).'
    - 'Incorporating idiosyncratic risk in individual housing returns and extending to defaultable debt would capture the appropriate risk-return trade-off that households face (p. 3128).'
    - 'Treating financial intermediaries as non-veils: banks and nonbanks channel credit and face their own balance-sheet constraints, which is a potential source of time variation in betas (p. 3128).'
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-03, role: extracted, note: "Full text read (pp. 3103-3136 plus appendices A-D); eight results extracted from the source PDF. Not human-verified. Not reproduced." }
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; one fix applied: equation (4) log argument parenthesised (wiki had log applied to R̃ alone rather than the full portfolio return R̃ α + R(1−α)); all 8 result rows, frontmatter facts, relatesTo body mentions, and no-em-dash rule confirmed correct."
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Added classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) from a fresh PDF read; existing results and
        sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Classification axes (identification, contributionType, mechanisms,
        introducesData, data-scope) re-checked against the source PDF; two fixes
        applied - removed demand-elasticity from mechanisms (paper invokes credit
        market channel via asymmetric portfolio weights, not demand-based asset
        pricing) and added individual to scope.granularity (CoreLogic
        individual-house transaction data used in Figure 6 / R4).
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-04
      role: extracted
      note: >-
        Added the effectiveness axis (findings[] per Core-results row,
        resultType) built from the page's already-verified Core-results table and
        relatesTo edges; existing results and sections unchanged.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-04
      role: verified
      note: >-
        Effectiveness axis (findings[] values/direction, resultType) re-checked
        against the source PDF; one fix applied - R4 direction corrected from
        positive to mixed (the idiosyncratic capital gains spread spans -40% to
        +60% per year, not a unidirectional positive effect); R1/R2/R3 values
        and directions confirmed against Figures 2-3 and p. 3108 text; resultType
        new-finding confirmed consistent with all relatesTo edges being
        builds-on or cites (no contradicts or replicates edge).
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.70000
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-10-17; no Creative Commons licence entry found'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the stylized facts on housing betas,
and the segmented-markets model that explains the pre-GFC puzzle: enough to know
what it found and how, without reading all 34 pages. To replicate or extend it,
read the full source at the [original](https://doi.org/10.1111/jofi.70000).

## TL;DR

The paper documents that housing returns had a *negative* stock-market beta from
the postwar period until the Global Financial Crisis, and a *positive* beta
thereafter, while the cashflow growth rates of stocks and housing comove
positively throughout. This "housing beta puzzle" is a challenge for
representative-agent models, which predict positive return comovement for assets
with similar cashflows. A two-type OLG model with segmented stock and housing
markets connected through a collateralized bond market resolves the puzzle:
homebuyers are poorer per unit of their future housing dividends than
stockholders, so they borrow using houses as collateral. Aggregate bad news
triggers either a credit demand channel (unconstrained homebuyers cut borrowing
sharply while stockholders cut supply only modestly, raising house prices and
cutting stock prices) or a credit supply channel (constrained homebuyers are
pinned at the collateral limit while stockholders flee to safety, expanding
credit supply, cutting the interest rate, and raising house prices as stock
prices fall). Both channels produce negative return comovement. Post-GFC shifts
(wealthier homebuyers, institutional housing investors, foreign Treasury demand)
weaken credit and market segmentation, moving the economy toward positive
comovement.

## Core results

Magnitudes are as reported; locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Housing betas (slope from regression of 10-year housing returns on 10-year stock returns, two-sided exponential decay kernel) were **mostly negative or zero before the GFC** and turned strongly positive after it | Figure 2, p. 3109 | Housing beta: roughly -0.2 to 0 in 1960s-1990s; peaks near +1 around 2020; levered housing beta even more negative pre-GFC (below -1 during 1980s-1990s) |
| R2 | **Cashflow growth rates of stocks and housing comove positively** throughout the sample, with correlation 80% pre-GFC and 59% for the full sample | Figure 3, p. 3110 | Correlation of 10-year real cashflow growth rates: 80% for 1930-GFC subsample, 59% full sample 1939-2024 |
| R3 | **Levered housing return has an even more negative beta** before the GFC than unlevered housing, because borrowing costs are lower during housing booms | Figure 2, p. 3109; Figure 5, p. 3113 | Levered housing beta reaches below -1 during the 1980s-1990s (Figure 2, green line); Panel A of Figure 5 shows real 10-year Treasury returns are negative during the 1950s, 1970s, and 2020s when house prices rise |
| R4 | Homebuyers' **idiosyncratic housing risk is large**: cross-sectional standard deviation of annualized capital gains spans -40% to +60% per year in San Francisco and similar volatility in Huntsville, AL | Figure 6, p. 3114 | Distribution is right-skewed and more dispersed post-GFC; average capital gain 6.7%/yr (San Francisco) vs 40 bp (Huntsville) over the last decade per CoreLogic data |
| R5 | **Proposition 1** (p. 3121): if homebuyers have lower savings per unit of cashflows than stockholders (Assumption A), homebuyers borrow from stockholders in equilibrium; credit market connects the two segmented markets | p. 3121 | Qualitative; follows from $$f(0) > 0$$ under Assumption A: excess credit demand is positive at the no-credit benchmark |
| R6 | **Proposition 2** (p. 3122): bad news about the aggregate economy generates negative return comovement. (i) Unconstrained homebuyers: higher uncertainty $$\sigma^2$$ raises the stock price-dividend ratio and lowers the housing price-dividend ratio, with credit declining; (ii) constrained homebuyers: bad news shifts credit supply down (flight to safety by stockholders), increasing credit, raising house prices, and lowering stock prices | p. 3122 | Qualitative proposition; mechanism is the asymmetric sensitivity of levered homebuyers vs. unleveraged stockholders to aggregate uncertainty |
| R7 | **Proposition 3** (p. 3125): forces that weaken the credit channel generate positive comovement. Equal savings-to-dividends ratios across types eliminate credit and negative comovement (part i); scaling household savings by $$\lambda > 1$$ raises both price-dividend ratios (part ii); population growth $$n$$ reduces the effective discount rate and raises both price-dividend ratios (part iii) | p. 3125-3126 | Qualitative; wealthier homebuyers post-GFC, demographic aging, institutional and foreign investors are the candidate empirical counterparts |
| R8 | **In the 2000s housing boom**, negative comovement is consistent with the data: house prices rose while stock returns declined (Figure 1, p. 3108); both the credit demand channel (laxer collateral, buyer optimism expanding credit demand) and a credit supply shifter (securitization, subprime expansion) were active | Figure 1, p. 3108; §III.B, p. 3124 | Annual data 1955-2024 show the shaded house-price boom episodes (1970s, 2000s, 2020s) coincide with stock market slumps |

**Overall (paper's conclusion).** Representative-agent models predict positive
return comovement for assets with similar cashflows; the data show the opposite
before the GFC. A segmented-markets model with collateralized credit explains
the puzzle. Post-GFC positive comovement reflects weakened credit and
segmentation from demographics, institutional investors, and foreign capital.

## Theory / model

The paper builds on a two-asset Lucas-tree benchmark and then extends it to a
heterogeneous-agent, segmented-markets economy. The motivation for studying
stocks and housing jointly draws on Piazzesi and Schneider (2016), who survey
the housing and macroeconomics literature. Landvoigt, Piazzesi and Schneider
(2015) develop a quantitative predecessor model for the San Diego housing
market with segmented markets and credit. Piazzesi and Schneider (2007) model
momentum traders in housing with a search framework. Piazzesi and Schneider
(2008) document the inflation illusion and credit channel for the 1970s
housing boom and stock slump across 12 OECD countries. Jorda, Schularick and
Taylor (2019) document a Sharpe ratio near one for aggregate housing returns
in U.S. postwar data, used here to contextualize idiosyncratic risk.
Mankiw and Weil (1989) linked Baby Boom demographics to the 1970s housing
surge, a candidate for post-GFC comovement via higher savings. Iacoviello
(2005) studies house prices and borrowing constraints in a monetary business
cycle model, cited as a quantitative single-market predecessor.

**Benchmark: representative-agent Lucas trees (Section I.C, p. 3109).**
Aggregate output $$Y_t$$ grows at log rate (equation 1, p. 3109):

$$
g_t := \log Y_t - \log Y_{t-1}, \quad g_t \stackrel{\text{iid}}{\sim} N(\mu, \sigma^2). \tag{1}
$$

The representative agent has log utility $$\sum_{t=0}^\infty \beta^t \log C_t$$.
Two long-lived assets pay cashflows $$D_t^s$$ (stocks) and $$D_t^h$$ (housing); the
Euler equation for asset $$i = s, h$$ is (equation 2, p. 3110):

$$
P_t^i = E_t\!\left[\beta \frac{C_t}{C_{t+1}}\bigl(D_{t+1}^i + P_{t+1}^i\bigr)\right]. \tag{2}
$$

Since both assets share the same cashflow growth, the model implies perfectly
positively comovving returns, in contradiction to Figure 1. Time-varying
discount rates (incorporating Cochrane (2011), Bansal and Yaron (2004), and
habit formation) generate positive comovement in valuation ratios and therefore
do not resolve the puzzle (p. 3111).

**Segmented-markets OLG model (Section III, p. 3115).** There are two types of
households: fraction $$\delta_s$$ trade only stocks plus bonds; fraction $$\delta_h$$
trade only housing plus bonds, with $$\delta_s + \delta_h = 1$$. In an OLG
framework, young households of type $$i$$ receive labor income $$w_{i,t} Y_t$$, save
their entire income, and consume only when old. Stocks and housing trade only
within type. Each young household solves (equation 3, p. 3116):

$$
\max E[\log c_{i,t+1}] \quad \text{s.t.} \quad p_{i,t}\theta_{i,t} + b_{i,t} = w_{i,t}, \tag{3}
$$
$$
c_{i,t+1} = (p_{i,t+1} + d_{i,t+1})\theta_{i,t} + b_{i,t} R,
$$
$$
\phi\, p_{i,t+1}\theta_{i,t} \geq -R\, b_{i,t},
$$

where $$\theta_{i,t}$$ is the share of the Lucas tree purchased, $$b_{i,t}$$ is bond
holdings, $$R$$ is the gross interest rate, and the last inequality is the
collateral constraint (the loan cannot exceed fraction $$\phi$$ of the future asset
value). Rewriting in portfolio weights $$\alpha_{i,t} = p_{i,t}\theta_{i,t}/w_{i,t}$$
(equation 4, p. 3117):

$$
\max_{\alpha_{i,t}\leq R/(R-\phi)} E_t\!\left[\log\!\left(\tilde{R}_{t+1}^i\, \alpha_{i,t} + R(1-\alpha_{i,t})\right)\right]. \tag{4}
$$

The optimal portfolio weight (equation 5, p. 3117) is:

$$
\alpha_{i,t} \approx \min\!\left\{\frac{\frac{1}{v^i} + \mu - r}{\sigma^2},\; \frac{R}{R-\phi}\right\}. \tag{5}
$$

When the collateral constraint does not bind, the weight equals the Merton
weight (Campbell and Viceira (1999)). The **Gordon Growth formula** for the
price-dividend ratio (equation 7, p. 3118) is:

$$
v_i = \frac{1}{r - \mu + \sigma^2 \alpha_i}, \tag{7}
$$

where $$\sigma^2 \alpha_i$$ is the risk premium. The **credit supply function**
(equation 8, p. 3118) is obtained from the stock Gordon Growth formula:

$$
r_s(Q) = \frac{d_s}{\delta_s w_s - Q} + \mu - \sigma^2 \frac{\delta_s w_s - Q}{\delta_s w_s}, \tag{8}
$$

and the **credit demand function** from the housing Gordon Growth formula
(equation 9, p. 3119) is:

$$
r_h(Q) = \frac{d_h}{\delta_h w_h + Q} + \mu - \sigma^2 \frac{\delta_h w_h + Q}{\delta_h w_h}. \tag{9}
$$

Equilibrium credit $$Q^*$$ solves $$f(Q) = r_h(Q) - r_s(Q) = 0$$ (equation 10,
p. 3119). When homebuyers hit the collateral constraint, credit demand becomes
(equation 11, p. 3120):

$$
r_h(Q) = \phi\, \frac{\delta_h w_h + Q}{Q} - 1. \tag{11}
$$

**Assumption A** (p. 3120): homebuyers have lower savings per unit of cashflows
than stockholders: $$\delta_h w_h / d_h < \delta_s w_s / d_s$$.

**Proposition 1** (p. 3121): if Assumption A holds, homebuyers borrow from
stockholders in equilibrium ($$Q^* > 0$$).

**Proposition 2** (p. 3122): under Assumption A, bad news about the whole
economy generates negative return comovement in housing and stock price-dividend
ratios, through either a credit demand channel (part i, unconstrained
homebuyers) or a credit supply channel (part ii, constrained homebuyers).

**Proposition 3** (p. 3125): forces that reduce credit and segmentation move
comovement toward positive: equal savings-to-dividends ratios, higher overall
savings (part ii), or population growth (part iii) all raise both price-dividend
ratios together.

## Method

This is primarily a theoretical paper. The model is solved analytically in
steady state. Key steps:

1. Impose constant price-dividend ratios in steady state (all shares of
   aggregate output are constant: cashflows, labor income).
2. Derive the Gordon Growth formulas (equations 7-9) for each asset class
   from the market-clearing conditions and the optimal portfolio weights.
3. Derive the credit supply function from stockholders' Gordon Growth formula
   and the credit demand function from homebuyers' Gordon Growth formula;
   show these are respectively upward- and downward-sloping in credit $$Q$$
   (Figure 7, p. 3119).
4. Establish existence and uniqueness of equilibrium using the intermediate
   value theorem and monotonicity of the excess demand function $$f(Q)$$
   (Appendix A, pp. 3129).
5. Characterize comparative statics via the implicit function theorem, with
   formal proofs in Appendices B-D (pp. 3129-3133).

The paper builds on `overlapping-generations` (two-period OLG with constant
savings rates) and `life-cycle-model` (portfolio choice over a finite
horizon). The housing beta is measured empirically using a two-sided
exponential-decay kernel regression of 10-year real housing returns on a
constant and 10-year real stock returns (10% weight on observations five years
in the past or future), as described on p. 3108 and displayed in Figure 2.

## Empirical specifications

There is no formal econometric specification in the traditional sense; the
empirical contribution is measurement and stylized facts. The key estimating
procedure is:

**Housing beta (R1, R3, Figure 2):** The stock-market beta of housing is
estimated as the slope from a local regression:

$$
\tilde{r}_{t}^h = a + \beta_t^h\, \tilde{r}_{t}^s + \varepsilon_t,
$$

where $$\tilde{r}_t^h$$ and $$\tilde{r}_t^s$$ are real 10-year geometric mean returns
on housing and stocks, the regression is estimated with a two-sided exponential
decay kernel (10% weight at horizon 5 years), and $$\beta_t^h$$ is the
time-varying slope. Sample: annual, 1955-2024 (Figure 2, p. 3109).

**Cashflow growth correlation (R2, Figure 3):** The correlation of real
10-year cashflow growth rates on stocks (S&P 500 dividends) and housing (NIPA
housing services expenditure) is computed over the same annual sample 1930-2024.
The 10-year rates are geometric means reported per year (p. 3107).

**Levered housing return (R3, Figure 5):** Levered housing return equals the
housing return minus borrowing costs, with borrowing costs proxied by real
10-year Treasury returns scaled by 80% (reflecting the typical down payment)
to match the leverage of mortgage-financed housing (p. 3107, p. 3113).

**Idiosyncratic capital gains (R4, Figure 6):** Cross-sectional distribution
of idiosyncratic capital gains on individual houses in San Francisco, CA and
Huntsville, AL from CoreLogic individual transaction data. Idiosyncratic gain
= individual house gain minus the location-specific average gain over the
same holding period (p. 3114).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| S&P 500 index (Shiller website: shillerdata.com, file ie_data.xls) | Real 10-year stock returns and dividend growth (cashflows); end-of-year values 1930-2024 | [Shiller data](/wiki/datasets/shiller-data/) |
| Financial Accounts of the United States (Fed, table B101/B104) | Value of residential real estate held by households; capital gains computed net of residential fixed investment (table F6); annual 1946-2024 | no page yet |
| NIPA (BEA, tables 2.4.4 line 50, 2.4.5 lines 25 and 47) | Housing cashflows (dollar expenditure on housing services, including imputed rents); price index for nondurables and services; annual 1929-2024 | [NIPA / FRED](/wiki/datasets/fred/) |
| 10-year Treasury returns (Shiller website) | Proxy for mortgage borrowing costs (multiplied by 0.8 for typical down payment); annual 1940-2024 | [Shiller data](/wiki/datasets/shiller-data/) |
| American Housing Survey (HUD) | Average homeowner tenure (15.1 yr in 1980, 11.5 yr in 2021), share of buyers with mortgage, share of first-time buyers, mortgage payment as share of income (Figure 4, p. 3112) | no page yet |
| CoreLogic individual transaction data | Cross-sectional distribution of idiosyncratic capital gains on individual houses in San Francisco, CA and Huntsville, AL (Figure 6, p. 3114) | [CoreLogic](/wiki/licensed/corelogic/) (licensed) |

Sample: primarily annual, U.S., 1930-2024 (returns and cashflows); housing leverage data 1975-2022 (Figure 4).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.70000) if you are: studying
why housing and stock returns move in opposite directions before 2008; building
models of segmented housing and stock markets connected through credit; analyzing
how demographics, institutional investors, or foreign capital affect the
stock-housing return relationship; or extending the theoretical channels
(defaultable debt, idiosyncratic risk, multi-cohort OLG) identified on
p. 3128. The appendices (pp. 3129-3133) contain formal proofs of all
propositions.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was
extracted by an LLM on 2026-06-03 and is **not human-verified or independently
reproduced**. The paper is paywalled (Wiley VOR terms); extract-only.

> Piazzesi, Monika. "Presidential Address: Housing Betas."
> *The Journal of Finance* 80, no. 6 (December 2025): 3103-3136.
> DOI: 10.1111/jofi.70000. © 2025 the American Finance Association.
> Paywalled; this page contains only extracted summary and analysis.
