---
title: "Social Security and Trends in Wealth Inequality: Catherine, Miller & Sarin (2025)"
description: >-
  Distilled: When Social Security wealth is properly included, top wealth shares
  in the United States have not meaningfully increased since 1989, overturning the
  finding of large inequality growth based on marketable-wealth-only measures.
  Social Security grew from $7.2 trillion in 1989 to $40.6 trillion in 2019 and
  now represents nearly 50% of the wealth of the bottom 90%. J. Finance 2025,
  paywalled. Eight core results with source locators, datasets used, the model,
  and the empirical method.
sidebar:
  label: Catherine-Miller-Sarin 2025
  order: 1
tags: [paper-summary, household-finance, wealth-inequality, social-security,
       pensions, measurement, descriptive, peer-reviewed, unreplicated,
       data:scf, data:dfa]
paper:
  authors: Sylvain Catherine, Max Miller, Natasha Sarin
  authorList:
    - { family: Catherine, given: Sylvain, affiliation: University of Pennsylvania }
    - { family: Miller, given: Max, affiliation: Harvard Business School }
    - { family: Sarin, given: Natasha, affiliation: Yale University }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1497–1531
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13440
  jel:
    codes: [H55, D31, E21]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Housing, Finance, and Neoliberalism
    - Global Health Care Issues
  dataAccess: public
  outcome:
    - top wealth shares (top 10% and top 1%) inclusive of Social Security wealth
    - aggregate Social Security wealth by valuation method
    - decomposition of Social Security wealth growth
  outcomeClass: [household-finance, macro-aggregates]
  license: >-
    Wiley standard VoR terms (http://onlinelibrary.wiley.com/termsAndConditions#vor);
    confirmed via Crossref DOI metadata: content-version vor, delay-in-days 0,
    start 2025-04-07. No open-access or CC licence detected.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/J. Finance site, checked 2026-06-06)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 9
  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [life-cycle-model, method-of-simulated-moments]
    identification: descriptive
  contributionType: [new-fact, measurement]
  mechanisms: [risk-sharing, participation-frictions]
  scope:
    region: US
    assetClass: household wealth (marketable + Social Security)
    period: 1989-01..2019-12
    frequency: annual
    dataType: [survey, administrative]
    granularity: [individual, aggregate]
    n: "Triennial SCF waves 1989-2019 plus Forbes 400 supplement; 10,000 simulated earnings paths per survey year-gender-age cell"
  findings:
    - ref: R1
      outcome: top 10% wealth share inclusive of Social Security
      metric: pp-effect
      value: "+1.0 pp (1989-2019, risk-free valuation); +1.7 pp (risk-adjusted valuation)"
      direction: positive
      vsBenchmark: marketable-wealth-only top 10% share rose 9.5 pp over same period (Table III Panel A)
    - ref: R2
      outcome: top 1% wealth share inclusive of Social Security
      metric: pp-effect
      value: "+1.5 pp (risk-free valuation); +1.9 pp (risk-adjusted valuation)"
      direction: positive
      vsBenchmark: marketable-wealth-only top 1% share rose 6.4 pp over same period (Table III Panel A)
    - ref: R3
      outcome: aggregate Social Security wealth
      metric: level
      value: "$7.2 trillion (1989) to $40.6 trillion (2019), risk-free valuation; approximately $35 trillion risk-adjusted in 2019"
      direction: positive
      vsBenchmark: total log growth of 1.746 log points; yield-curve change accounts for 48.3% of growth (Table I)
    - ref: R4
      outcome: Social Security wealth share of bottom 90% total wealth
      metric: probability
      value: "26.0% in 1989; 49.8% in 2019 (risk-adjusted valuation)"
      direction: positive
      vsBenchmark: Social Security nearly doubled its share of bottom 90% total wealth over 30 years (Figure 5)
    - ref: R5
      outcome: top 10% wealth share, policy-risk robustness (40% benefit cut)
      metric: pp-effect
      value: "+4.3 pp (top 10%), +3.4 pp (top 1%) under high-cost benefit-cut scenario"
      direction: positive
      vsBenchmark: marketable-wealth-only rise of 9.5 pp / 6.4 pp; Social Security still substantially attenuates the trend (Table III Panel B, Figure 7)
    - ref: R6
      outcome: top 10% wealth share, 3% liquidity-premium robustness
      metric: pp-effect
      value: "+4.7 pp (top 10%), +3.6 pp (top 1%) with 3% liquidity discount"
      direction: positive
      vsBenchmark: still less than half the marketable-wealth-only rise; aggregate SS wealth halved but attenuation persists (Table III Panel C, Figure 8)
    - ref: R7
      outcome: top 10% wealth share, heterogeneous discount rates
      metric: pp-effect
      value: "+4.2 pp (top 10%), +3.2 pp (top 1%)"
      direction: positive
      vsBenchmark: approximately half the rise observed without Social Security; spread increased 2019 vs 1989, reducing redistributive impact (Figure 11)
    - ref: R8
      outcome: top 10% and top 1% wealth shares, NPV concept
      metric: pp-effect
      value: "-3.0 pp (top 10%), -0.2 pp (top 1%) change 1989-2019"
      direction: negative
      vsBenchmark: under NPV concept SS wealth is initially negative for young workers, then grows; top-share trend reversed vs accrued-benefits concept (Figure 12)
  resultType: overturns
  relatesTo:
    - { cite: "Saez & Zucman (2016)", doi: '10.1093/qje/qjw004', relation: contradicts, note: "baseline marketable-wealth series shows top 1% share growing by 6.4 pp (28.6% to 35.7%), which Social Security inclusion reduces to 1.5-1.9 pp" }
    - { cite: "Smith, Zidar & Zwick (2020)", doi: '10.3386/w29374', relation: contradicts, note: "alternative capitalization-based top-wealth series similarly overstated once Social Security is included (Figure 14)" }
    - { cite: "Feldstein (1974)", doi: '10.1086/260246', relation: builds-on, note: "foundational result that wealth is more equally distributed when Social Security is included; this paper extends to 30-year trend" }
    - { cite: "Feldstein (1976)", doi: '10.1080/01621459.1976.10480950', relation: builds-on, note: "early evidence on Social Security and the distribution of wealth" }
    - { cite: "Greenwald et al. (2021)", doi: '10.3386/w28613', relation: tests, note: "their finding that declining interest rates drive rising marketable wealth inequality is substantially attenuated once SS duration effects are included" }
    - { cite: "Benzoni, Collin-Dufresne, and Goldstein (2007)", doi: '10.1111/j.1540-6261.2007.01271.x', relation: builds-on, note: "cointegration of labor and stock markets used to derive market beta of wage-indexed Social Security cash flows (Section IV)" }
    - { cite: "Guvenen et al. (2021)", doi: '10.3982/ecta14603', relation: builds-on, note: "rich income process calibrated from their estimates of U.S. lifetime earnings moments" }
  openQuestions:
    - "The paper excludes other public-wealth programs (Medicare, Medicaid, disability insurance) that also accrue disproportionately to the bottom of the distribution; including them would likely further attenuate measured inequality (p. 1529)."
    - "Human capital is excluded from the wealth concept; its inclusion would also bear on lifetime consumption inequality and inequality trends (pp. 1503-1504, 1529)."
    - "Social Security's unique illiquidity raises open questions about its optimal program design and the degree to which private valuation diverges from social valuation; a fuller private-valuation exercise accounting for longevity and idiosyncratic income insurance is left to future work (p. 1525)."
  replicationCode:
    status: available
  proposedVocab:
    - { axis: topic, term: wealth-inequality, def: "Distribution of household wealth across the wealth distribution, typically measured by top-share statistics", aliases: [wealth-concentration] }
    - { axis: topic, term: social-security, def: "U.S. Social Security old-age retirement program; also used generically for public pension systems", aliases: [public-pension, ssa] }
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-06, role: extracted, note: "Full text read (pp. 1497-1531 of the source PDF); eight results extracted with locators from figures, tables, and text. Not human-verified. Not reproduced. Replication code linked in the published article's Supporting Information." }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all eight Core results rows confirmed against Table III (p. 1518), Figure 3 (p. 1512), Figure 5 (p. 1517), Figure 7 (p. 1520), Figure 8 (p. 1521), Figure 11 (p. 1525), Figure 12 (p. 1526), and Table I (p. 1515); equations 1, 2, 3b, 6, 7, 10, 14, 15, 16, 18 verified term-by-term; frontmatter authors, year, venue, DOI, resultsCount, and relatesTo locatability all confirmed; no em-dashes or colorful adjectives found; no errors corrected." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13440", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-04-07. No CC licence present; classified paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the measurement model (Social Security wealth valuation), and the empirical method (SCF wealth-share construction plus earnings simulation): enough to understand what it found and how, without reading all 35 pages. To replicate or extend, read the full source at the [original](https://doi.org/10.1111/jofi.13440).

## TL;DR

Recent work by Saez and Zucman (2016) and others documents large increases in U.S. wealth inequality over the past three decades based on measures that exclude Social Security. This paper shows that when Social Security is properly included, top wealth shares have not meaningfully changed since 1989. Social Security wealth grew from $7.2 trillion in 1989 to $40.6 trillion in 2019 and now constitutes nearly 50% of the total wealth of the bottom 90%. The result is robust to potential benefit cuts, liquidity discounts, heterogeneous discount rates, and alternative accrued-benefit definitions. The main driver of Social Security's growth is falling interest rates, which disproportionately raised the present value of the long-duration, wage-indexed cash flows that low- and middle-class households hold. The paper builds on Feldstein (1974) and Feldstein (1976), who showed that total wealth inclusive of Social Security is more equally distributed than marketable wealth alone, and extends that insight to document how the difference has grown over 30 years. It also directly challenges the finding in Greenwald et al. (2021) that falling interest rates drove rising marketable wealth inequality, showing that once Social Security's own long-duration assets are included the inequality trend is substantially reversed.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Top 10% wealth share rises only 1.0 pp (risk-free) or 1.7 pp (risk-adjusted) once Social Security is included**, vs. 9.5 pp for marketable wealth alone | Figure 3 Panel A, p. 1512; Table III Panel A, p. 1518 | Top 10% share: marketable wealth +9.5 pp; risk-free +1.0 pp; risk-adjusted +1.7 pp (1989-2019) |
| R2 | **Top 1% wealth share rises only 1.5 pp (risk-free) or 1.9 pp (risk-adjusted)**, vs. 6.4 pp for marketable wealth | Figure 3 Panel B, p. 1512; Table III Panel A, p. 1518 | Top 1% share: marketable wealth +6.4 pp; risk-free +1.5 pp; risk-adjusted +1.9 pp |
| R3 | **Aggregate Social Security wealth grew from $7.2 trillion to $40.6 trillion (1989-2019)**, a 5.6x increase; largest contributor is the falling yield curve (45.8-48.3% of log growth) | Figure 2, p. 1511; Table I, p. 1515 | Log total growth 1.746; yield-curve change accounts for 0.843 (risk-free) of that log growth |
| R4 | **Social Security wealth rose from 26.0% to 49.8% of the total wealth of the bottom 90%** between 1989 and 2019 | Figure 5, p. 1517 | Bottom 90% SS share: 26.0% (1989) to 49.8% (2019) under risk-adjusted valuation |
| R5 | **Even under the most conservative policy-risk scenario (40% across-the-board benefit cut)**, top 10% and top 1% shares rise by only 4.3 and 3.4 pp, less than half the marketable-wealth trend | Figure 7, p. 1520; Table III Panel B, p. 1518 | Top 10% +4.3 pp, top 1% +3.4 pp under high-cost benefit cut vs. marketable +9.5/+6.4 pp |
| R6 | **A 3% liquidity discount halves aggregate SS wealth** but the attenuation of inequality trends persists: top 10% +4.7 pp, top 1% +3.6 pp | Figure 8, p. 1521; Table III Panel C, p. 1518 | Top 10% +4.7 pp, top 1% +3.6 pp even after 3% liquidity premium discount |
| R7 | **Heterogeneous discount rates** (borrowing rates for constrained households) raise the top 10% and top 1% increases to 4.2 and 3.2 pp, still approximately half the marketable-wealth trend | Figure 11, p. 1525; Table III Panel C | Top 10% +4.2 pp, top 1% +3.2 pp under heterogeneous private discounting |
| R8 | **Under the NPV wealth concept** (benefits minus future taxes), the top 10% and top 1% shares actually declined by 3.0 and 0.2 pp between 1989 and 2019, because NPV SS wealth was low or negative for young workers in the high-rate 1989 environment | Figure 12, p. 1526 | Top 10% NPV change: -3.0 pp; top 1% NPV change: -0.2 pp |

**Overall (paper's conclusion).** Prior studies find large increases in U.S. wealth inequality based on marketable wealth measures. When Social Security is incorporated, top wealth shares have not increased since 1989. The top wealth estimates may still be overstated because the paper excludes programs like disability insurance and Medicare, which accrue disproportionately to the bottom of the wealth distribution. Public transfer programs make the U.S. economy more progressive, and inequality estimates need to reflect this (p. 1529).

## Theory / model

The paper has no formal equilibrium model; instead it derives a valuation framework for Social Security wealth and tests how its inclusion changes measured wealth inequality. The tested hypotheses are:

1. When Social Security's accrued benefit value is included in household wealth, top wealth shares are substantially lower and their trend since 1989 is much smaller than estimates based on marketable wealth alone.
2. Social Security grew disproportionately relative to marketable wealth primarily because of falling interest rates, which inflate the present value of its long-duration wage-indexed cash flows that constitute the bulk of low- and middle-class wealth.

**Retiree Social Security wealth** (p. 1505, equation 1). For a retiree observed in year $$t$$, Social Security wealth $$S_{it}$$ is the present value of future nominal benefits $$B_{it}$$ adjusted for CPI-indexed growth and survival probabilities $$m_{itk}$$:

$$
S_{it} = \sum_{s=t}^{T} \left( \prod_{k=t}^{s-1} (1 - m_{itk}) \right) \frac{B_{it}}{(1 + r_{ts})^{s-t}} \frac{\mathbb{E}[P_s]}{P_t} \tag{1}
$$

**Accrued Social Security wealth for workers** (p. 1507, equation 7). The accrued benefits concept values benefits proportional to past tax contributions:

$$
S_{it} = \frac{\text{Past Taxes}_{it}}{\text{Past Taxes}_{it} + \text{Future Taxes}_{it}} \sum_{s=t+1}^{T} \frac{\mathbb{E}[B_{is}]}{(1 + r_{ts})^{s-t}} \tag{7}
$$

where future and past taxes are present-valued at the appropriate discount rate (equations 8-9, p. 1507). Past taxes are grossed up using the realized return on 30-year Treasury bonds to convert them to present-value terms.

**Alternative NPV concept** (p. 1508, equation 10):

$$
S_{it} = \sum_{s=t+1}^{T} \frac{\mathbb{E}[B_{is} - T_{is}]}{(1 + r_{ts})^{s-t}} \tag{10}
$$

This values Social Security as the stream of net expected transfers, which can be negative for young workers in high-rate environments.

## Method

**Earnings simulation for workers.** Earnings are modeled as the product of an aggregate wage index $$L_{1,t}$$ and an idiosyncratic component $$L_{2,it}$$ (p. 1505, equation 2):

$$
L_{it} = L_{1,t} \cdot L_{2,it} \tag{2}
$$

The idiosyncratic component evolves via a rich income process (equations 3a-3g, pp. 1505-1506) calibrated to Guvenen et al. (2021). The process has a persistent component $$z_t^i$$ following an AR(1):

$$
z_t^i = \rho z_{t-1}^i + \eta_t^i \tag{3b}
$$

with innovations from a mixture of normals, transitory shocks from a second mixture, and nonemployment shocks with exponentially distributed duration. 10,000 earnings paths are simulated per survey year-gender-age cell and matched to SCF respondents.

**Indexed taxable earnings and benefits** (equations 4-6, pp. 1506-1507). Payroll taxes are 10.6% of earnings up to the Social Security wage base $$SSWB_t$$. The Average Indexed Monthly Earnings (AIYE) is the average of the best 35 years of indexed earnings. Benefits are a piecewise-linear concave function of AIYE reflecting Social Security's progressive design:

$$
B_{it} = \frac{P_{t}}{P_{t_i+60}} \begin{cases} 0.9 \cdot \text{AIYE}_i & \text{if } \text{AIYE}_i < b_{1,c_i} \\ 0.9 \cdot b_{1,c_i} + 0.32(\text{AIYE}_i - b_{1,c_i}) & \text{if } b_{1,c_i} \le \text{AIYE}_i < b_{2,c_i} \\ 0.9 \cdot b_{1,c_i} + 0.32(b_{2,c_i} - b_{1,c_i}) + 0.15(\text{AIYE}_i - b_{2,c_i}) & \text{if } b_{2,c_i} \le \text{AIYE}_i \end{cases} \tag{6}
$$

**Risk adjustment for macroeconomic risk.** Because Social Security benefits are wage-indexed, they are exposed to aggregate labor market risk. Assuming cointegration of labor and stock markets (Benzoni, Collin-Dufresne, and Goldstein (2007)), the market beta of a cash flow proportional to $$L_{1,t+n}$$ is (p. 1513, equation 14):

$$
\beta_t^{L_{1,n}} = \left(1 - \frac{\phi}{\kappa}\right)\left(1 - e^{-\kappa n}\right) \tag{14}
$$

and the expected return on this cash flow under no-arbitrage is (equation 15):

$$
\mathbb{E}_t\left[r_t^{L_{1,n}}\right] = \beta_t^{L_{1,n}}(\mu - r) + r \tag{15}
$$

Parameters are calibrated at $$\kappa = 0.16$$, $$\phi = 0.08$$ (from Benzoni, Collin-Dufresne, and Goldstein (2007)), and equity premium $$\mu - r = 0.06$$. The risk-adjusted discount factor for a cash flow proportional to $$L_{1,n}$$ paid in year $$k$$ is (equation 16, p. 1513):

$$
\chi_{t,n,k} \approx \left[\prod_{s=t}^{n} \left(1 + \beta_s^{L_{1,n}}(\mu - r) + r_{ts}\right) \prod_{s=n+1}^{k}(1 + r_{ts})\right]^{-1} \tag{16}
$$

**Heterogeneous discount rates** (equations 17-18, p. 1523). Unconstrained households (no debt, liquid or illiquid assets above thresholds) are discounted at the risk-adjusted forward rate. Constrained households face their opportunity cost of debt, estimated via Tobit regressions of balance-weighted interest rate spreads by income quintile, age, and year:

$$
f_{h,a,q,t}^{\text{constrained}} = \begin{cases} f_{t,h}^{\text{risk-adj}} & \text{with prob. } p_{a+h-1,q,t} \\ f_{t,h}^{\text{risk-free}} + s_{a+h-1,q,t} & \text{with prob. } 1 - p_{a+h-1,q,t} \end{cases} \tag{18}
$$

## Empirical specifications

**Top wealth share construction.** Marketable wealth shares are constructed from the SCF using the net worth variable (assets minus liabilities), supplemented by Forbes 400 data for the top 0.01% following Saez and Zucman (2016), and augmented with DFA data on defined benefit pension obligations. Total wealth shares add the simulated Social Security wealth $$S_{it}$$ to each household's net worth. The share of total wealth held by the top 10% and top 1% is computed after ranking by the relevant total-wealth concept (not by marketable wealth, so the ranked groups can differ by specification).

**Decomposition of Social Security wealth growth** (Table I, p. 1515). The log per-capita Social Security wealth change is additively decomposed by:
1. Change in the yield curve (holding age distribution, survival, and policy at 1989 values)
2. Shift in the age distribution (holding yield curve at 2019 values)
3. Change in life expectancy
4. Social Security expansion and other factors (scope of taxable earnings, benefit formulas)

Each contribution is identified by sequential substitution of 2019 for 1989 parameters.

**Robustness (Table III, p. 1518):** Results are checked under (i) benefit cuts calibrated to SSA actuarial cost scenarios (low, intermediate, high), (ii) tax hikes on bottom 90% or bottom 99%, (iii) liquidity premiums of 1-3%, (iv) heterogeneous household discount rates, (v) declining wage growth, (vi) alternative accrued-benefits definitions (pro-rata by age, stop-working), and (vii) the NPV valuation. The headline attenuation of inequality trends is unchanged across all specifications.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Survey of Consumer Finances (SCF), triennial 1989-2019 | Marketable wealth shares; Social Security wealth for retirees; earnings-match base for workers | [no page yet] |
| Forbes 400 list | Supplement to extend wealth distribution to the top 0.01% following Saez and Zucman (2016) | [no page yet] |
| Distributional Financial Accounts (DFA), Federal Reserve Board | Aggregate value of defined benefit pension obligations by wealth group | [DFA](/wiki/datasets/dfa/) |
| Federal Reserve zero-coupon yield curve (Treasury notes, up to 30 years) | Discount rates for Social Security cash flows; forward rate extrapolation beyond 30 years | [no page yet] |
| SSA Annual Reports and actuarial projections | Calibration of Social Security parameters (bend points, wage base, benefit formulas, cost scenarios) | [no page yet] |
| Human Mortality Database (HMD), 1989-2017 | Survival probabilities by gender, calibrated and adjusted for income-based life expectancy differences | [no page yet] |
| Health Inequality Project (HIP) | Income-based life expectancy differences used to adjust survival probabilities | [no page yet] |
| Guvenen et al. (2021) income process estimates | Calibration of idiosyncratic earnings dynamics for the 10,000-path simulation | [no page yet] |

Sample: SCF waves 1989, 1992, 1995, 1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019 (triennial). Social Security wealth simulated using 10,000 earnings paths per survey year-gender-age cell.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13440) if you are: (i) replicating wealth inequality estimates that include public programs; (ii) assessing how changes in interest rates affect the distribution of total household wealth; (iii) designing or evaluating Social Security reform scenarios (the robustness section covers benefit cuts, tax hikes, liquidity premiums, and heterogeneous discounting); or (iv) comparing U.S. wealth inequality across studies that use different wealth concepts (Figure 14 directly overlays this paper's SS-inclusive estimates on SCF, Saez and Zucman (2016), and Smith, Zidar, and Zwick (2020) series). Table III and Figures 7-13 contain the full robustness battery.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3). This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled; only extracts are reproduced here consistent with fair use.

> Catherine, Sylvain, Max Miller, and Natasha Sarin. "Social Security and Trends in Wealth Inequality." *The Journal of Finance* 80, no. 3 (June 2025): 1497-1531. DOI: 10.1111/jofi.13440. © 2025 the American Finance Association.
