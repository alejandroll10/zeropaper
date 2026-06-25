---
title: "Going for Broke: de Jong, Kooijmans & Koudijs (2025)"
description: >-
  Distilled: Using 18th-century Dutch plantation mortgage-backed securities,
  this paper shows high-reputation banks originated better mortgages and issued
  securities retaining 17.5 percentage points more value during market collapse,
  with the effect attenuated when bankers were shielded from downside risk or
  had short-run profit focus. J. Finance 2025, CC BY-NC-ND 4.0. Eight core
  results with source locators, datasets used, the model (banker reputation and
  MBS quality), and the method (mediation analysis, OLS with MBS fixed effects).
sidebar:
  label: de Jong-Kooijmans-Koudijs 2025
  order: 1
tags: [paper-summary, financial-intermediation, securitization, bank-reputation,
       mortgage-backed-securities, panel-regression, historical-finance, peer-reviewed,
       unreplicated]
paper:
  authors: Abe de Jong, Tim Kooijmans, Peter Koudijs
  authorList:
    - { family: de Jong, given: Abe, orcid: "0000-0002-2809-5465", affiliation: University of Groningen and Monash Business School }
    - { family: Kooijmans, given: Tim, affiliation: National Taiwan University }
    - { family: Koudijs, given: Peter, affiliation: NYU Stern and Erasmus School of Economics }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3263–3312
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13503
  jel:
    codes: [G24, G21, N23]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Banking stability, regulation, efficiency
    - Housing Market and Economics
    - Financial Markets and Investment Strategies
  dataAccess: hand-collected
  outcome:
    - MBS secondary market price (percentage of par value)
    - mortgage quality at origination (LTV, borrower type, loan-to-fundamental ratio)
    - merchant bank trading volume post-bust
  outcomeClass: [asset-prices, credit-risk]
  license: 'CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0, start 2025-10-06; corroborated by artifact p.3263 CC Attribution-NonCommercial-NoDerivs notice)'
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: 'open-access PDF available via handle hdl.handle.net/11370/42677b1f-7ec6-4f7b-a06b-709820371c17 (confirmed via OpenAlex, 2026-06-03)'
  redistribution: extract-only (CC BY-NC-ND 4.0 permits sharing with attribution but no derivatives; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 0
  methods:
    role: both
    family: reduced-form-causal
    buildsFrom: [panel-regression, difference-in-differences, fama-macbeth]
    identification: selection-on-observables
  contributionType: [new-fact, new-data, new-theory]
  mechanisms: [information-asymmetry, moral-hazard, agency]
  introducesData: true
  scope:
    region: Dutch Republic / Suriname
    assetClass: plantation mortgage-backed securities
    period: 1750..1796
    frequency: mixed
    dataType: [market, accounting, administrative]
    granularity: [firm, security, transaction]
    n: "46 MBS, 23 merchant banks, 4,605 auction transactions (price regressions); 315 mortgages, 26 banks (mortgage quality analysis)"
  findings:
    - { ref: R1, outcome: mortgage quality at origination (LTV, borrower type, loan-to-fundamental ratio), metric: coefficient, value: "-0.06*** (t = -2.67)", direction: negative, vsBenchmark: "high-rep vs low-rep LTV during boom; negative = lower (better) LTV for high-rep" }
    - { ref: R2, outcome: mortgage quality at origination (LTV, borrower type, loan-to-fundamental ratio), metric: coefficient, value: "nonelite agent boom diff -0.22** (t = -2.08); nonelite borrower boom diff -0.35*** (t = -3.58)", direction: negative, vsBenchmark: "high-rep vs low-rep nonelite agent/borrower fractions during boom; negative = fewer nonelite for high-rep" }
    - { ref: R3, outcome: MBS secondary market price (percentage of par value), metric: coefficient, value: "17.46*** (t = 5.10)", direction: positive, vsBenchmark: "high-rep MBS vs low-rep MBS price at auction" }
    - { ref: R4, outcome: MBS secondary market price (percentage of par value), metric: coefficient, value: "continuous office value 24.25*** (t = 5.14)", direction: positive, vsBenchmark: "alternative continuous reputation measure vs binary high-rep dummy" }
    - { ref: R5, outcome: MBS secondary market price (percentage of par value), metric: pp-effect, value: "joint ACME 10.29 (p = 0.10); mediators explain 73% of 17.46 pp gap", direction: positive, vsBenchmark: "mortgage characteristics as mediators vs direct reputation effect" }
    - { ref: R6, outcome: MBS secondary market price (percentage of par value), metric: pp-effect, value: "boom approx. 6 pp; bust 1778 approx. 35 pp", direction: positive, vsBenchmark: "high-rep vs low-rep MBS price gap across boom and bust periods" }
    - { ref: R7, outcome: MBS secondary market price (percentage of par value), metric: coefficient, value: "short-run focus direct coeff -9.34*** (se = 3.09); short-run focus x office value -28.22* (se = 14.84); married-into-wealth x office value -24.80* (se = 12.38)", direction: negative, vsBenchmark: "reputation effect attenuated for bankers with short-run focus or married into wealth" }
    - { ref: R8, outcome: merchant bank trading volume post-bust, metric: pp-effect, value: "59% lower post-1770 ABE trading volume for below-median MBS performers", direction: negative, vsBenchmark: "below-median vs above-median MBS performers in post-1770 ABE trading volume" }
  resultType: overturns
  relatesTo:
    - { cite: 'Griffin, Lowery & Saretto (2014)', doi: '10.1093/rfs/hhu030', relation: contradicts, note: 'that paper finds high-reputation banks issued worse MBS in the 2000s; this paper argues the difference stems from limited personal downside exposure and short-termism of modern bankers' }
    - { cite: 'Piskorski, Seru & Witkin (2015)', doi: '10.1111/jofi.12271', relation: contradicts, note: 'that paper shows similar misrepresentation rates regardless of reputation in modern RMBS; this setting shows reputation can matter when bankers bear long-run reputational losses personally' }
    - { cite: 'Winton & Yerramilli (2021)', doi: '10.1093/rfs/hhab012', relation: builds-on, note: 'model of reputation as disciplining device for security issuance quality; this paper provides historical evidence consistent with their framework' }
    - { cite: 'Hartman-Glaser (2017)', relation: cites, note: 'signaling / pooling equilibrium in asset sales where reputation can lead to adverse-selection outcomes; cited as theoretical counterpoint' }
    - { cite: 'de Jong, Kooijmans & Koudijs (2023)', doi: '10.1017/s002205072300027x', relation: builds-on, note: 'companion paper documenting the 18th-century plantation MBS data set from Suriname used here' }
    - { cite: 'Flandreau & Flores (2009)', doi: '10.1017/S0022050709001089', relation: cites, note: '19th-century sovereign bond market showing high- and low-reputation banks specialized in different risk tiers; same general reputation-quality link' }
  openQuestions:
    - 'Whether the reputation mechanism documented here generalizes to modern financial markets where limited liability, bailout expectations, and short-term bonuses reduce bankers personal exposure to reputational losses (pp. 3308-3309).'
    - 'Whether the results reflect reputation or skill: the paper rules out observable skill proxies explaining more than 17-27% of the effect, but cannot fully separate the two (pp. 3304-3306).'
    - 'The role of investor sophistication and belief heterogeneity: the paper rules out overoptimism as the primary driver by showing investors were from the top wealth quantiles, but a behavioral component cannot be entirely excluded (pp. 3304-3308).'
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: "Full text read (pp. 3263-3312); eight results extracted from the CC-BY-NC-ND PDF. Not human-verified. Not reproduced."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against source PDF; fixed R1 (wiki had Low Rep Preboom LTV values instead of High Rep Boom), fixed R4 (ABE vol col-4 was 1.63* t=0.85 not 7.03; N deeds col-5 was 2.10 t=2.03 not 4.29**), corrected Prediction 5 direction (low delta_b, not high, corresponds to short-run focus per Lemma 1 and Prediction 5)."
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
        introducesData, data-scope) re-checked against the source PDF; fixed
        identification from natural-experiment to selection-on-observables
        (no quasi-random shock; the paper uses a predetermined 1742 census
        reputation proxy in OLS with year and MBS FE, and explicitly disclaims
        an instrument - all other axes confirmed correct).
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
        against the source PDF; fixed R7 value field (parenthetical figures are
        standard errors, not t-stats; relabeled se= accordingly per Table V Panel B);
        fixed resultType from new-finding to overturns (two explicit contradicts edges
        to Griffin et al. 2014 and Piskorski et al. 2015 drive the headline contribution);
        R1-R6 and R8 magnitudes and directions confirmed correct.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13503
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-10-06'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the stylized model motivating the empirical analysis, and the estimating specifications with their equations: enough to know what was found and how, without reading all 50 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13503).

## TL;DR

The paper asks whether bank reputation can improve security quality in opaque markets. It studies 37 Amsterdam merchant banks that securitized West Indian plantation mortgages between 1753 and 1772, the first large-scale mortgage-backed securities market on record. High-reputation banks (measured by the rental value of their office premises, capturing outside business at stake) originated better-quality mortgages and issued securities that retained on average 17.5 percentage points more value during the market collapse. Virtually all of this premium can be traced to better mortgage characteristics at origination, not ex-post behavior. The reputation effect is significantly attenuated for bankers who were married into wealth (shielded from downside risk) or who had a short-run profit focus (partner died with a minor heir). These findings are consistent with a partial-equilibrium model predicting that reputation disciplines behavior only when bankers are personally exposed to long-run reputational losses.

The results contrast sharply with evidence from modern securitization markets. Griffin, Lowery, and Saretto (2014) show that high-reputation banks continued issuing large volumes of poorly performing MBS in the 2000s. Piskorski, Seru, and Witkin (2015) find that similar misrepresentation rates prevailed regardless of bank reputation in modern RMBS. The paper argues these modern failures reflect structural differences: limited liability, bailout expectations, and short-term incentives removed the personal downside exposure that makes reputation effective. On the theoretical side, Winton and Yerramilli (2021) model reputation as a disciplining device in originate-to-distribute lending, providing the framework this paper empirically supports. Hartman-Glaser (2017) shows how reputation can instead lead to pooling equilibria where opportunistic types mimic good types, a channel this paper finds limited evidence for in the historical setting. The companion data paper, de Jong, Kooijmans, and Koudijs (2023), documents the plantation MBS data set and provides evidence on the full intermediation chain. Flandreau and Flores (2009) document a related reputation-quality link in 19th-century sovereign bond markets.

## Core results

Magnitudes and significance are as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | High-reputation banks originated mortgages with lower LTVs during the boom | Table II, p. 3293 | LTV boom: high-rep ~0.56 vs low-rep 0.62 (SD 0.09); difference -0.06\*\*\* (t = -2.67) |
| R2 | High-reputation banks used elite agents and borrowers more during the boom | Table II, p. 3293 | Nonelite agent boom diff: -0.22\*\* (t = -2.08); nonelite borrower boom diff: -0.35\*\*\* (t = -3.58) |
| R3 | MBS issued by high-reputation banks retained 17.5 percentage points more value in the bust | Table III col. (1), p. 3295 | High-reputation dummy coeff: 17.46\*\*\* (t = 5.10); R² = 0.72; N = 4,605 transactions, 46 MBS |
| R4 | The reputation-price gap is robust to all alternative reputation measures | Table III cols. (2)-(9), p. 3295 | Continuous office value: 24.25\*\*\* (t = 5.14); city government: 14.17\*\*\* (t = 5.85); log ABE vol: 1.63\* (t = 0.85); log N deeds: 2.10 (t = 2.03) |
| R5 | Mortgage characteristics at origination mediate 73% of the reputation-price gap | Table IV Panel B, p. 3300 | Joint ACME: 10.29 (p = 0.10); remaining direct effect after all mediators becomes statistically insignificant |
| R6 | The reputation-price gap is small (about 6 pp) during the boom and large (about 35 pp) during the bust | Figure 5 Panel A, p. 3297 | Boom difference approx. 6 pp (yield diff approx. 34 bps); bust 1778 difference approx. 35 pp (yield diff approx. 895 bps) |
| R7 | Reputational effects are attenuated for bankers with short-run focus or married into wealth | Table V Panel B, p. 3301 | Short-run focus: direct coeff -9.34\*\*\* (t = 3.09); interaction short-run focus x office value: -28.22\* (t = 14.84); married-into-wealth x office value: -24.80\* (t = 12.38) |
| R8 | Banks with poor MBS performance suffered a 59% post-1770 decline in Amsterdam Bank of Exchange trading volume | Figure 6, p. 3303; Section VI.B Internet Appendix | Controlling for time and bank FE, post-1770 ABE trading volume 59% lower for below-median MBS performers |

**Overall (paper's conclusion).** Bank reputation can improve security quality in opaque markets, but only when bankers have substantial personal exposure to long-run reputational losses and are not focused on short-run profits. The evidence from the 18th-century Dutch plantation MBS market shows that high-reputation banks consistently originated better-quality mortgages and that investors suffered far smaller losses on their securities. The contrast with the 2000s RMBS literature is consistent with modern-era limited liability, bailout expectations, and short-term incentives undermining the same mechanism.

## Theory / model

The paper presents a stylized partial-equilibrium model (Section III, pp. 3286-3290) with three types of agents: planters (borrowers), bankers, and investors. Each period a banker originates a loan and sells it to investors.

**Planters.** Plantation $$p$$ has fundamental value $$F_p \in \{\underline{F}, \bar{F}\}$$ with $$\text{Prob}[F_p = \bar{F}] = \pi$$. A planter takes a one-period loan $$\lambda_{p,b,t}$$ from banker $$b$$, paying interest $$R_{b,t}$$ and origination fee $$\varphi$$. The planter's participation constraint pins the fee (eq. 1, p. 3286):

$$
(1 - \varphi) \lambda_{p,b,t} \Omega \geq \bar{R} \lambda_{p,b,t}; \qquad \varphi \equiv \frac{\Omega - \bar{R}}{\Omega}. \tag{1}
$$

Moral hazard: a planter can repay or defraud, taking $$(1-\beta)F_p$$ and leaving nothing. The incentive-compatibility constraint is (eq. 2, p. 3286):

$$
F_p - R_{p,b,t} \lambda_p \geq (1 - \beta) F_p. \tag{2}
$$

This defines maximum loan sizes $$\bar{\lambda} \equiv \frac{\beta}{\bar{R}}\bar{F}$$ (high type) and $$\underline{\lambda} \equiv \frac{\beta}{\bar{R}}\underline{F}$$ (low type) (eq. 3, p. 3286):

$$
\bar{\lambda} \equiv \frac{\beta}{\bar{R}}\bar{F}; \qquad \underline{\lambda} \equiv \frac{\beta}{\bar{R}}\underline{F}. \tag{3}
$$

**Bankers.** Each banker $$b$$ has discount factor $$\delta_b$$, outside activities yielding $$\rho_b$$ per period, and independent wealth $$\omega_b$$. A banker who misrepresents a low-type planter as high-type earns extra fees but loses fraction $$\gamma = 1$$ of outside activities permanently if discovered. The utility loss from falling below the threshold $$\rho_b$$ is quadratic (eq. 4, p. 3287):

$$
U(y, \rho_b) = \begin{cases} y & \text{if } y \geq \rho_b \\ y - A(\rho_b - y)^2 & \text{if } y < \rho_b \end{cases}. \tag{4}
$$

**Market.** The market continues each period with probability $$\zeta_t$$ (unknown; updated by Bayesian learning to $$\mu_{t+1}$$). Bankers learn about an impending end one period before investors.

**Equilibrium types.** Proposition 1 (pp. 3288-3289) shows that in equilibrium two types participate: Good (G) bankers who always provide $$\underline{\lambda}$$ honestly, and Mediocre (M) bankers who provide $$\underline{\lambda}$$ while the market is set to continue but misrepresent if they learn it is ending. The conditions are (eqs. 9-10, p. 3288):

$$
G: \quad \varphi(\bar{\lambda} - \underline{\lambda}) \leq \frac{\delta_b}{1 - \delta_b} \left[\rho_b + A(\rho_b - \omega_b)^2\right] \tag{9}
$$

$$
M: \quad \varphi(\bar{\lambda} - \underline{\lambda}) - \frac{\delta_b}{1-\delta_b} \frac{(1-\delta_b \zeta_t)}{(1-\delta_b \zeta_t (1-\pi))} \varphi \bar{\lambda} \leq \frac{\delta_b}{1-\delta_b}\left[\rho_b + A(\rho_b - \omega_b)^2\right] \leq \varphi(\bar{\lambda}-\underline{\lambda}). \tag{10}
$$

**Key testable predictions.** Prediction 2 (from Proposition 1, Lemma 1): high-reputation banks provide better loans; the gap is especially pronounced when the market is about to end. Prediction 5 (Lemma 1): the effect is attenuated for bankers with high $$\omega_b$$ (married into wealth) or low $$\delta_b$$ (short-run focus, i.e., discounting the future more heavily). Prediction 6 (by design): banks that sold worse MBS see a decline in other activities.

## Method

The paper applies two main estimators: OLS with MBS fixed effects for the price regressions, and average causal mediation effect (ACME) analysis (Baron and Kenny (1986), Imai et al. (2011)) for the mediation analysis.

**Reputation measure.** Bank reputation $$\rho_b$$ is proxied by the rental value of a bank's Amsterdam office block from the 1742 census (Oldewelt (1945)), reflecting outside business activities unrelated to plantation MBS. High-reputation: office value above the median. The measure is verified to correlate with city-government positions, ABE trading volume, and notarial deed counts (Table I, pp. 3274-3275).

**MBS price regression (equation 11, p. 3294).** For each auction transaction between 1768 and 1796:

$$
P_{i,b,t} = \beta \rho_b + \eta_t + \varepsilon_{i,b,t}, \tag{11}
$$

where $$P_{i,b,t}$$ is the price of MBS $$i$$ issued by bank $$b$$ in year $$t$$ as a percentage of par, $$\rho_b$$ is the reputation measure, and $$\eta_t$$ are auction-year fixed effects. Standard errors are clustered at the MBS level (46 clusters). Each transaction is weighted by the inverse of the number of auction transactions for that MBS times its market share, so $$\beta$$ captures the loss a hypothetical investor equally split between high- and low-reputation banks would have experienced.

**Time-path specification (equation 12, p. 3296).** To test Prediction 3, the regression is estimated separately for high- and low-reputation MBS:

$$
P_{i,t} = \eta_t + \varepsilon_{i,t}, \tag{12}
$$

where $$\eta_t$$ are annual averages for each group (same weights as eq. 11). This traces the price divergence over time, showing a small 6 pp gap during the boom (1769-1770) widening to approximately 35 pp in 1778.

**Mediation analysis.** The mediators (mortgage characteristics) are introduced sequentially into equation (11) to estimate the ACME (Imai et al. (2011)). Mediators are: timing of mortgage origination, fraction via nonelite agents, fraction to nonelite borrowers, and average LTF within an MBS. The joint ACME uses block-bootstrapping (10,000 resamples) to compute p-values. Results in Table IV, p. 3299-3300.

## Empirical specifications

**Mortgage quality regressions.** The sample is all mortgages extended 1750-1770 by Amsterdam merchant banks issuing MBS (N = 315, 26 banks). Each observation is weighted by mortgage sum. The specification compares means for high- vs low-reputation banks before (1750-1768) and during (1769-1770) the boom, testing differences-in-differences (Table II, p. 3293). No instrument; identification relies on the timing of low-reputation banks entering the market and the differential change in quality across bank types during the boom period.

Key mortgage quality outcomes:
- LTV (mortgage amount / appraised value): high-rep boom ~0.56 vs. low-rep boom 0.62, diff -0.06\*\*\* (t = -2.67)
- Fraction nonelite borrowers: boom diff -0.35\*\*\*, indicating high-rep banks maintained elite borrower screens during the boom
- LTF (mortgage / fundamental value, a debt-to-income analog): high-rep LTF increased 0.29\*\*\* (t = 2.66) during boom vs low-rep increase 0.50\*\*\* (t = 4.56), diff -0.21 (insignificant but economically large)

**MBS price regression.** Main sample: all MBS by Amsterdam merchant banks up to 1772 for which auction-price data are available (N = 46 MBS, 23 merchant banks; 4,605 auction transactions 1768-1796). Weighted OLS with auction-year FE and MBS-level clustered SE. The baseline result of 17.46 percentage points (t = 5.10) is robust to nine alternative reputation measures (Table III, cols. 1-9, p. 3295), block-bootstrapped SE, different regression weights, and annual-level aggregation.

**Heterogeneity tests (Table V, pp. 3301-3302).** The continuous office value interacted with short-run focus and married-into-wealth dummies:
- Short-run focus (partner died with minor heir) reduces the reputation effect to near zero (interaction coeff -28.22\*, t = 14.84)
- Married into wealth reduces the reputation effect by more than 60% in the price regression (interaction coeff -24.80\*, t = 12.38) and makes it statistically insignificant in the LTF regression

Standard errors are clustered at the bank level (23 or 24 clusters depending on spec).

**Reputational losses (Figure 6, p. 3303).** Post-1770 ABE trading volume is regressed on bank FE and time FE; above-/below-median MBS performers are separated on the estimated bank FE. The 59% post-1770 gap is the difference in log ABE volume between good- and poor-MBS-performance banks, controlling for time trends.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Hand-collected plantation mortgage records (Amsterdam notarial archives, Suriname colonial archives) | Mortgage characteristics: LTV, borrower type, agent type, mortgage sum, appraisal values, loan-to-fundamental ratios; 1750-1770 | No page yet |
| 1742 Amsterdam property census (Oldewelt 1945) | Bank reputation measure: rental value of bank office block | No page yet |
| Amsterdam Bank of Exchange (Wisselbank) account books, 1765-1795 | Bank trading volumes for reputational-loss test (half-yearly) | No page yet |
| MBS secondary-market auction prices (Amsterdam notarial archives) | MBS price outcomes: transaction prices 1768-1796, N = 4,605 transactions over 46 MBS | No page yet |
| Amsterdam estate tax records | Investor wealth distribution and portfolio holdings (N = 889 estates 1768-1796) | No page yet |

Sample: Suriname plantation MBS market, 1753-1796. Core price regressions: 1768-1796, 46 MBS, 23 merchant banks, 4,605 auction transactions. Mortgage analysis: 1750-1770, 315 mortgages, 26 merchant banks.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13503) if you are: studying the conditions under which bank reputation disciplines security quality in opaque markets; researching the history of financial innovation and the first MBS market; examining how banker incentive structures (limited liability, short-termism, wealth shielding) affect security issuance; or building on the mediation analysis framework to separate reputation effects from observable skill. Table III (p. 3295) contains the main price regressions; Tables IV and V (pp. 3298-3302) contain mediation and heterogeneity results; Figure 5 (p. 3297) traces the price gap over time.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was extracted by an LLM on 2026-06-03 and is **not human-verified or independently reproduced**. The CC BY-NC-ND 4.0 licence permits sharing with attribution for non-commercial purposes but no derivatives; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY-NC-ND 4.0).** de Jong, Abe, Tim Kooijmans, and Peter Koudijs.
> "Going for Broke: Bank Reputation and the Performance of Opaque Securities."
> *The Journal of Finance* 80, no. 6 (December 2025): 3263-3312.
> DOI: 10.1111/jofi.13503. © 2025 The Author(s).
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page is a distilled summary by the Institute for Automated Research;
> it is not a reproduction of or derivative from the original article.
