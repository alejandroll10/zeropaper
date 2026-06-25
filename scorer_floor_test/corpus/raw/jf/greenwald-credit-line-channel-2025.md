---
title: "The Credit Line Channel: Greenwald, Krainer & Paul (2025)"
description: >-
  Distilled: Using confidential U.S. loan-level supervisory data (FR Y-14Q),
  Greenwald, Krainer, and Paul document that the COVID-19 surge in bank credit
  was driven by large firms drawing existing credit lines, which crowded out
  term lending to smaller firms and amplified the decline in aggregate
  investment. A calibrated structural model quantifies the credit line channel
  as the transmission mechanism. J. Finance 2025, paywalled. Eight core results
  with source locators, datasets used, the model, and the method.
sidebar:
  label: Greenwald-Krainer-Paul 2025
  order: 1
tags: [paper-summary, macro, credit-markets, bank-lending, firm-heterogeneity,
       corporate-finance, financial-accelerator, covid-19, panel-regression,
       instrumental-variables, peer-reviewed, unreplicated,
       data:fr-y14q, data:wrds, data:orbis-bvd]
paper:
  authors: Daniel L. Greenwald, John Krainer, Pascal Paul
  authorList:
    - { family: Greenwald, given: Daniel L., affiliation: NYU Stern School of Business }
    - { family: Krainer, given: John, orcid: 0000-0002-6902-7282, affiliation: Board of Governors of the Federal Reserve }
    - { family: Paul, given: Pascal, orcid: 0000-0002-0456-671X, affiliation: Federal Reserve Bank of San Francisco }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3137-3183
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13486
  jel:
    codes: [G21, G32, E44]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Banking stability, regulation, efficiency']
  dataAccess: proprietary-confidential
  outcome:
    - bank term lending to small firms
    - total firm debt
    - firm capital expenditures
    - aggregate investment
  outcomeClass: [credit-supply, firm-real-outcomes]
  license: >-
    Paywalled; Wiley VOR licence only (not CC). Crossref license[].URL =
    http://onlinelibrary.wiley.com/termsAndConditions#vor, content-version vor,
    delay-in-days 0, start 2025-08-27. No open-access or CC licence found.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site; Crossref VOR terms only, no CC, confirmed 2026-06-03)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 0
  methods:
    role: both
    family: structural
    buildsFrom: [panel-regression, instrumental-variables, difference-in-differences, method-of-simulated-moments]
    identification: natural-experiment
  contributionType: [new-fact, new-theory]
  mechanisms: [intermediary-constraint, financial-constraint]
  scope:
    region: US
    assetClass: corporate loans (bank credit lines and term loans)
    period: 2012-Q3..2020-Q4
    frequency: quarterly
    dataType: [administrative, accounting]
    granularity: [firm, transaction]
    n: "207,505 distinct firm TINs; 4,496,353 loan facility observations"
  findings:
    - { ref: R1, outcome: bank term lending to small firms, metric: coefficient, value: "committed credit $2,231B; used credit $941B; ratio 2.37x; top 10% hold 71% of undrawn credit", direction: positive }
    - { ref: R2, outcome: bank term lending to small firms, metric: coefficient, value: "96% of 2020:Q1 credit increase flowed to top 10% firms; large firms' credit line drawdowns explain 77% of total increase", direction: positive }
    - { ref: R3, outcome: bank term lending to small firms, metric: coefficient, value: "-1.96 (SE 0.72) baseline; -2.28 (SE 0.65) extended maturity FE; -2.74 (SE 0.93) loan purpose FE; -3.63 at h=2", direction: negative }
    - { ref: R4, outcome: bank term lending to small firms, metric: coefficient, value: "-3.05 (SE 1.05) on delta CL Usage; interaction with Cap-Buffer +1.25 (SE 0.36)", direction: negative }
    - { ref: R5, outcome: total firm debt, metric: coefficient, value: "-2.63 (SE 0.69) all firms; -2.61 (SE 0.68) small firms; 0.97 (SE 5.72) large firms", direction: mixed, vsBenchmark: "small firms negative, large firms null" }
    - { ref: R6, outcome: firm capital expenditures, metric: coefficient, value: "IV beta_capex 0.03 (SE 0.01) small firms; IV beta_cash 0.07 (SE 0.01) small firms; large firms not significant", direction: positive, vsBenchmark: "large firms null" }
    - { ref: R7, outcome: aggregate investment, metric: pp-effect, value: "investment at t=1: -3.3% Credit Lines vs -1.9% Term Loans; 74% larger decline", direction: negative, vsBenchmark: "Term Loans counterfactual economy" }
    - { ref: R8, outcome: aggregate investment, metric: pp-effect, value: "investment decline 3.2 pp more without intervention in Credit Lines economy vs 0.6 pp more in Term Loans economy", direction: positive, vsBenchmark: "Term Loans counterfactual economy without Fed SMCCF" }
  resultType: new-finding
  relatesTo:
    - { cite: 'Khwaja and Mian (2008)', doi: '10.1257/aer.98.4.1413', relation: builds-on, note: 'firm fixed effect approach to isolate credit supply shifts, applied here to the bank-firm Y14 panel' }
    - { cite: 'Ivashina and Scharfstein (2010)', doi: '10.1016/j.jfineco.2009.12.001', relation: extends, note: 'similar drawdown pattern in the 2007-09 crisis; this paper provides actual drawdown measures and crowding-out regressions' }
    - { cite: 'Bernanke, Gertler, and Gilchrist (1999)', relation: builds-on, note: 'financial accelerator framework that motivates the structural model' }
    - { cite: 'Chodorow-Reich (2014)', doi: '10.1093/qje/qjt031', relation: builds-on, note: 'employment effects of credit disruptions; shared approach of tracing firm-level crowding out to real outcomes' }
    - { cite: 'Chodorow-Reich et al. (2022)', doi: '10.1016/j.jfineco.2021.06.035', relation: cites, note: 'contemporaneous evidence that smaller firms also drew less of their unused capacity during COVID-19' }
    - { cite: 'Acharya and Steffen (2020)', relation: cites, note: 'corporate dash for cash at the start of COVID-19; complementary evidence on drawdown motives' }
    - { cite: 'Sufi (2009)', relation: builds-on, note: 'bank lines of credit in corporate finance: allocation by creditworthiness and moral hazard' }
    - { cite: 'Darmouni and Siani (2025)', doi: '10.1016/j.jmoneco.2024.103728', relation: tests, note: 'bond market stimulus results confirmed by the model: direct effect on investment is modest, indirect credit-line channel is large' }
  openQuestions:
    - 'How much the strength of the credit line channel varies with macroeconomic and banking sector conditions more broadly, beyond the specific COVID-19 shock (Conclusion, p. 3178).'
    - 'Microfounding the existence and pricing of credit lines is left to future work; the paper takes credit line spreads as exogenous (footnote 19, p. 3159).'
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: >-
        Full text read (pp. 3137-3183); eight results extracted from the PDF.
        Not human-verified. Not reproduced. Replication code referenced in the
        paper (Supporting Information) but not run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF; all
        eight result rows confirmed correct (Table I p.3144, Figure 5 p.3149,
        Tables III-V pp.3152-3157, Figure 7 p.3175, IA Figure IA.6 p.3176);
        all equations (1-15, A.20) verified term-by-term; no errors found.
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
        introducesData, data-scope) re-checked against the source PDF; corrected
        identification from 'instrument' to 'natural-experiment' (primary design
        is the Khwaja-Mian COVID-19 bank-firm FE natural experiment, pp.3150-3151;
        IV in eqs.3-5 is secondary); all other axes confirmed correct.
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
        against the source PDF; R1-R2 confirmed (Table I p.3144, Figure 5 p.3149);
        R3 value string corrected (col 2 extended-maturity-FE = -2.28 SE 0.65 was
        missing; -2.74 SE 0.93 is col 3 loan-purpose FE, not "extended FE");
        R4-R8 confirmed (Tables IV-V pp.3155-3157, Figure 7 p.3175, IA Figure IA.6
        p.3176); resultType new-finding defensible given headline contribution.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13486
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: >-
        license[0].content-version=vor,
        URL=http://onlinelibrary.wiley.com/termsAndConditions#vor,
        delay-in-days=0, start=2025-08-27. No CC licence entry found.
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the structural model, and the
empirical specifications: enough to know what it found and how, without
reading all 47 pages. To replicate or extend, read the full source at the
[original](https://doi.org/10.1111/jofi.13486).

## TL;DR

The paper uses confidential FR Y-14Q loan-level data covering over 200,000
U.S. firms across 2012-2020 to establish that the COVID-19 surge in bank
credit was driven almost entirely by large firms drawing down existing credit
line commitments, a pattern reminiscent of the 2007-09 crisis documented by
Ivashina and Scharfstein (2010). Banks that experienced larger credit line
drawdowns reduced their term lending supply more (crowding out), especially
to smaller firms that rely on term loans. The identification approach adapts
Khwaja and Mian (2008) to the Y14 panel. Smaller firms could not replace this
lost credit and consequently cut investment and cash holdings, echoing the
real-effects mechanism in Chodorow-Reich (2014). A calibrated structural model
with two firm types (constrained/term-loan-only and unconstrained/credit-line
access) shows that the predetermined pricing of credit lines is the key
mechanism: as unconstrained firms borrow heavily at fixed credit line spreads
(an insurance device documented by Sufi (2009) and Acharya and Steffen (2020)),
banks face tighter capital requirements and raise spreads on term loans,
redirecting credit away from constrained firms. The financial accelerator
framework of Bernanke, Gertler, and Gilchrist (1999) motivates the modeling
approach. The model also reveals that the Fed's bond market intervention had
large indirect effects via credit-line repayment, confirming and extending the
cross-sectional evidence of Darmouni and Siani (2025). Contemporaneous evidence
that smaller firms drew less of their unused capacity is provided by
Chodorow-Reich et al. (2022). In aggregate, the decline in investment is more
than 70% larger with credit lines than in a counterfactual economy without
them, even though aggregate bank-firm credit increases.

## Core results

Magnitudes and significance are as reported. `\*\*` = 5%, `\*\*\*` = 1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Undrawn credit line commitments are nearly 40% larger than total used bank credit (lines + term loans combined); top 10% of firms hold 71% of undrawn credit | Table I, p. 3144; Figure 3, p. 3146 | Committed credit = $2,231B; used credit = $941B; ratio 2.37x; Lorenz curve for unused credit is far more bowed than for used credit |
| R2 | 96% of the credit increase during 2020:Q1 flowed to the top 10% of firms by size, driven by drawdowns of existing credit lines | Figure 5, p. 3149 | Change in existing credit lines by large firms explains 77% of the total increase; bottom 90% of firms saw only modest increases |
| R3 | Banks with larger credit line drawdowns contracted term lending more; coefficient on delta Credit Line Usage = -1.96 to -2.74 across specifications | Table III col. (1)-(3), p. 3152 | beta_h=0 = -1.96\*\* (SE 0.72) baseline; -2.74\*\*\* (SE 0.93) with extended FE and controls; effects intensify through 2020:Q3 (-3.63\*\*, col. 5) |
| R4 | Banks with lower pre-crisis capital buffers restricted term lending more in response to drawdowns | Table IV, p. 3155 | Coefficient on delta CL Usage = -3.05\*\*\* (SE 1.05); interaction with Cap-Buffer = +1.25\*\*\* (SE 0.36); deposit inflows do not offset the crowding out (col. 7) |
| R5 | Firms exposed to banks with larger drawdowns experienced reductions in total debt; effect is concentrated in small firms | Table V col. (1)-(2), p. 3157 | OLS beta = -2.63\*\*\* (SE 0.69); small firms: -2.61\*\*\* (SE 0.68); large firms: 0.97 (SE 5.72), indistinguishable from zero |
| R6 | Small firms cut capital expenditures and cash holdings when total debt fell; 12 cents and 24 cents less per $1 decline in debt | Table V col. (4), (7), p. 3157 | IV beta_capex = 0.03\*\* (SE 0.01) for small firms; IV beta_cash = 0.07\*\*\* (SE 0.01); large firms' effects not significant |
| R7 | In the calibrated structural model, the decline in investment is 74% larger in the Credit Lines economy than in the Term Loans counterfactual | Figure 7, p. 3175 | Investment at t=1: -3.3% (Credit Lines) vs -1.9% (Term Loans); bank loans +33.0% vs +3.0%; aggregate corporate bonds lower in Credit Lines economy |
| R8 | The Fed's bond market intervention (SMCCF) raised constrained firm investment via indirect credit-line spillovers; the policy effect is more than five times larger in the Credit Lines economy | Internet Appendix Figure IA.6, referenced p. 3176 | Investment decline at t=1 is 3.2 pp more without intervention in Credit Lines economy vs only 0.6 pp more in Term Loans economy; constrained firm debt moves from +4.4% to -6.3% without the policy |

**Overall (paper's conclusion).** Credit lines are central to macroeconomic
shock transmission. Their predetermined pricing insulates large firms from
rising spreads, concentrating credit drawdowns among the least financially
constrained firms. This crowds out term lending to small, bank-dependent
firms and amplifies the decline in aggregate investment despite increasing
total bank-firm credit. Cross-sectional access to pre-committed credit has
quantitatively first-order aggregate consequences.

## Theory / model

The model has three household types: constrained entrepreneurs (type C),
unconstrained entrepreneurs (type U), and savers (type S). Entrepreneur
type $$j$$ has exponential utility over dividends $$C_{j,t}$$ (eq. 6, p. 3159):

$$
U_{j,t} = E_t \sum_{k=0}^{\infty} \beta_j^k \frac{(1 - \exp(-\zeta_D C_{j,t}))}{\zeta_D}. \tag{6}
$$

Firm type $$j$$ produces output with a Cobb-Douglas technology:

$$
Y_{j,t} = Z_t K_{j,t-1}^{\alpha} \bar{N}_j^{1-\alpha},
$$

where $$Z_t$$ is aggregate TFP, $$K_{j,t-1}$$ is capital, and $$\bar{N}_j$$ is fixed
labor. The representative firm of type $$j$$ maximizes firm value (eq. 11, p. 3163):

$$
V_{j,t} = D_{j,t} + \exp(\tilde{a}_t) \eta_{A,j} \frac{A_{j,t}^{1-\zeta_A}}{1-\zeta_A} + E_t\!\left[\Lambda_{j,t+1} V_{j,t+1}\right], \tag{11}
$$

where $$D_{j,t}$$ is dividends, $$A_{j,t}$$ is cash (with precautionary utility
weight $$\eta_{A,j}$$ and curvature $$\zeta_A$$), and the SDF is

$$
\Lambda_{j,t+1} = \beta_j \exp(-\zeta_D (C_{j,t+1} - C_{j,t})). \tag{12}
$$

The firm's budget constraint (eq. 13, p. 3164) is:

$$
D_{j,t} = \underbrace{(1-\tau)(Y_{j,t} - wN_j)}_{\text{after-tax profit}} + \underbrace{(1-(1-\tau)\delta)\tilde{Q}_{j,t} K_{j,t-1}}_{\text{old capital}} + \bar{\pi}^{-1} A_{j,t-1}
- \bar{\pi}^{-1}\!\left[(1-\tau)r_{t-1} + \nu + \kappa_j \Gamma_{\omega,j}(\tilde{\omega}_{j,t})\right] B_{j,t-1} - (1-\tau)S_{j,t-1}
- Q_{j,t} K_{j,t} - A_{j,t} + B_{j,t}^*, \tag{13}
$$

where $$\kappa_j \Gamma_{\omega,j}(\tilde\omega_{j,t})$$ are expected violation costs
(the covenant channel), $$B_{j,t}^*$$ is new debt, and $$S_{j,t}$$ tracks promised
spread payments. The covenant violation threshold is (eq. 10, p. 3163):

$$
\tilde\omega_{j,t} = \frac{\bar\pi^{-1} B_{j,t-1}}{\theta X_{j,t}}, \tag{10}
$$

with smoothed EBITDA $$X_{j,t} = (1-\rho_X)(Y_{j,t} - wN_j) + \rho_X \bar\pi^{-1} X_{j,t-1}$$
(eq. 8, p. 3162).

The bank holds capital $$k_t$$ and faces the capital requirement (eq. 14, p. 3164):

$$
k_t \geq \chi^B \underbrace{(B_{C,t}^{\text{loan}} + B_{U,t}^{\text{loan}})}_{\text{used credit}} + \chi^L \underbrace{(\bar{L} - B_{U,t}^{\text{loan}})}_{\text{undrawn lines}}, \tag{14}
$$

where $$\chi^B = 0.08$$ and $$\chi^L = 0.04$$ match Basel risk weights. The bank
maximizes (eq. 15, p. 3165):

$$
v_t = \underbrace{d_t}_{\text{dividends}} - \left(\frac{\eta_k}{\bar{k}^{\zeta_L}}\right) \frac{k_t^{1+\zeta_L}}{1+\zeta_L} + E_t\!\left[\Lambda_{S,t+1} v_{t+1}\right]. \tag{15}
$$

In equilibrium the short-term spread on loans to constrained firms is
$$s_{C,t}^{\text{loan}} = (1+r)\chi^B \eta_k k_t^{\zeta_L}$$ (eq. A.20, p. 3180), so credit
line drawdowns that raise $$k_t$$ directly raise spreads on term loans to
constrained firms, generating the crowding-out mechanism.

**Identification.** The paper takes the existence and pricing of credit lines
as exogenous, calibrated to the data. The COVID-19 shock is modeled as a
combination of three AR(1) processes: a negative TFP shock ($$\varepsilon_{Z,1}
= -0.1059$$), a positive cash-demand shock ($$\varepsilon_{a,1} = 0.3227$$), and a
positive corporate bond spread shock ($$\varepsilon_{s,1} = 0.1408\%$$), calibrated
to match aggregate data patterns.

## Method

The paper uses two complementary methods: a reduced-form credit-supply
regression (building on `panel-regression` and `instrumental-variables`) and a
structural general equilibrium model estimated via `method-of-simulated-moments`
targeting empirical regression coefficients.

**Descriptive regression (equation 1, p. 3146).** To document the cross-sectional
distribution of undrawn capacity, the paper regresses:

$$
\frac{\text{Unused Credit}_{i,t}}{\text{Committed Credit}_{i,t}} = \alpha_t + \tau_k + \beta \boldsymbol{X}_{i,t-4} + u_{i,t}. \tag{1}
$$

Time FE $$\alpha_t$$, industry FE $$\tau_k$$, lagged firm characteristics $$\boldsymbol{X}_{i,t-4}$$
include size, age, public status, EBITDA, leverage, tangible assets, and
investment grade. This builds on `panel-regression`.

**COVID credit supply specification (equation 2, p. 3150).** The paper adapts
the Khwaja and Mian (2008) firm fixed effect approach to the Y14 data:

$$
\frac{L_{i,t+h}^{j,k} - L_{i,t-1}^{j,k}}{0.5(L_{i,t+h}^{j,k} + L_{i,t-1}^{j,k})} = \alpha_{i,k}^h + \beta^h \frac{\Delta\text{Credit Line Usage}_t^j}{\text{Assets}_{t-1}^j} + \gamma^h X_{i,t-1}^j + u_{i,h}^{j,k} \tag{2}
$$

for $$h = 0, 1, \ldots$$ quarters after 2019:Q4. $$L_{i,t}^{j,k}$$ is term lending from
bank $$j$$ to firm $$i$$ of loan type $$k$$. The symmetric growth rate in the LHS
bounds the variable in $$[-2, 2]$$ and handles zero observations. The firm-credit-type FE
$$\alpha_{i,k}^h$$ absorbs all common demand shifts, so $$\beta^h$$ captures credit
supply. Sample: firms with term loans only (excluding cases where the same firm
has both term loans and credit lines at the same bank), 2019:Q4 to 2020:Q1-Q4.

**Firm outcome specification (equations 3-5, pp. 3156-3158).** Total debt
growth for firm $$i$$ is regressed on credit line exposure:

$$
\frac{D_{i,t+1} - D_{i,t-1}}{0.5(D_{i,t+1} + D_{i,t-1})} = \alpha_m + \beta \,\text{CL Exposure}_{i,t} + \gamma X_{i,t-1} + u_{i,t+1}, \tag{3}
$$

where $$\text{CL Exposure}_{i,t} = \sum_{j=1}^J \omega_{i,t-1}^j \left(\frac{\Delta\text{Credit Line Usage}_t^j}{\text{Assets}_{t-1}^j}\right)$$ (eq. 4, p. 3156) weights bank-level
drawdowns by each firm's borrowing share. The two-stage IV specification (eq. 5,
p. 3158) uses $$\text{CL Exposure}_{i,t}$$ and $$\sum_j \omega_{i,t-1}^j$$ as
instruments to recover the causal effect of debt changes on investment and cash:

$$
y_{i,t+1} = \bar\alpha_m + \bar\beta \frac{D_{i,t+1} - D_{i,t-1}}{0.5(D_{i,t+1}+D_{i,t-1})} + \bar\gamma X_{i,t-1} + \bar{u}_{i,t+1}, \tag{5}
$$

where $$y$$ is either CAPEX/Assets or $$\Delta\text{Cash}/\text{Assets}$$. Industry FE
and firm controls throughout; standard errors clustered by bank.

## Empirical specifications

**Unused capacity distribution (R1, Table II, p. 3147).** Regression (1) on
156,010 observations from 31,209 firms, 2012:Q3-2019:Q4. $$R^2 = 0.27$$. All
coefficients statistically significant at 1%.

**COVID credit supply (R2-R4, Table III, p. 3152).** Regression (2) at $$h=0$$
on the multilender subsample, 2019:Q4-2020:Q1. Baseline: 1,678 observations,
749 firms, 28 banks; FE: Firm $\times$ Rate type. Extended FE (col. 2): Firm
$\times$ Rate $\times$ Remaining Maturity bins; loan purpose FE (col. 3).
The crowding-out coefficient $$\beta^0$$ is -1.96 to -2.74 and significant at
the 5-1% level. Columns (4)-(6) extend to $$h=1,2,3$$: effects intensify through
2020:Q3 (-3.63\*\*) then abate by 2020:Q4 once credit lines are repaid.

**Capital buffer heterogeneity (R4, Table IV, p. 3155).** Regression (2) with
the interaction of delta CL Usage and bank Cap-Buffer (voluntary capital above
the regulatory minimum). Three specifications adding bank controls and their
interactions; main coefficient -3.05 to -4.62, interaction with Cap-Buffer
+1.25 to +3.34, all significant. Deposit inflow coefficient near zero (col. 7),
rejecting liquidity as the mechanism in favor of bank capital requirements.

**Firm outcomes (R5-R6, Table V, p. 3157).** Regression (3) OLS: 3,164 firm-quarter
observations; beta = -2.63\*\*\* for all firms. IV regressions (eq. 5) on 2,717
observations; first-stage F-stat 248 (all firms), 183 (small). Small firm CAPEX
coefficient 0.03\*\* (SE 0.01); large firm coefficient -0.02 (SE 0.14). Small
firm cash coefficient 0.07\*\*\* (SE 0.01). Industry FE (two-digit NAICS) throughout.

**Structural model (R7-R8).** Calibrated to match three regression coefficients
from Table V (columns 2, 4, 7) exactly; key parameters reported in Table VI
(p. 3168). TFP, cash-demand, and bond spread shocks calibrated to match
COVID-19 aggregate data patterns. Counterfactual: Term Loans economy where
unconstrained firms cannot access credit lines.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| FR Y-14Q (H.1 schedule, BHCs) | Primary loan-level data: committed and used credit by type (credit line vs. term loan), firm financials, quarterly 2012:Q3-2020:Q4; 207,505 distinct TINs | [FR Y-14Q](/wiki/datasets/fr-y14q/) (proprietary-confidential) |
| Compustat | Financial statements for public firms; replaces BHC-collected financials for public firms | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| Orbis (Bureau van Dijk) | Financial statements for private firms; supplements Y14 BHC-collected data for private firms | [Orbis (BvD)](/wiki/licensed/orbis-bvd/) (licensed) |
| Federal Reserve H.8 releases | Aggregate U.S. commercial bank balance sheet series; used for Figure 1 context | No page yet |

Sample: 2012:Q3-2020:Q4, quarterly. Descriptive analysis: 2012:Q3-2019:Q4
(pre-COVID "normal times"). COVID credit supply regressions: 2019:Q4-2020:Q4.
Firm outcome regressions: 2019:Q2-2020:Q2. 207,505 distinct firm TINs total;
3,222 are public; the rest are private, making this substantially broader than
typical corporate finance samples. 28 BHCs in the credit supply sample.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13486) if you are:
studying credit channel transmission and want the full set of robustness
checks (Internet Appendix Tables IA.V-IA.XII); building or calibrating a
structural model of bank-firm credit with heterogeneous borrowers; studying
the Federal Reserve's corporate bond purchase programs and their indirect
effects; or extending the analysis to different crisis episodes or bank
regulatory environments. Table VI (p. 3168) contains the full calibration;
Figure 7 (p. 3175) shows the aggregate impulse responses.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025,
pp. 3137-3183. DOI: [10.1111/jofi.13486](https://doi.org/10.1111/jofi.13486).
This distillation was extracted by an LLM on 2026-06-03 and is **not
human-verified or independently reproduced**. The paper is paywalled (Wiley
VOR terms only; no CC licence); this page contains only extracted findings
and equations, not the verbatim text. To cite:

> Greenwald, Daniel L., John Krainer, and Pascal Paul.
> "The Credit Line Channel."
> *The Journal of Finance* 80, no. 6 (December 2025): 3137-3183.
> DOI: 10.1111/jofi.13486. © 2025 the American Finance Association.
