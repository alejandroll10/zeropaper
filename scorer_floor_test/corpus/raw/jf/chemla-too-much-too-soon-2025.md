---
title: "Too Much, Too Soon, for Too Long: Chemla, Rivera & Shi (2025)"
description: >-
  Distilled: In a general equilibrium model with dynamic moral hazard and
  endogenous outside options, competitive executive compensation is
  inefficiently high, front-loaded, and associated with excessive managerial
  tenure. J. Finance 2025, CC BY 4.0. Six core results with source locators,
  the model, and the method.
sidebar:
  label: Chemla-Rivera-Shi 2025
  order: 1
tags: [paper-summary, executive-compensation, corporate-governance, agency, moral-hazard,
       general-equilibrium, theory, open-access, cc-by, peer-reviewed, unreplicated]
paper:
  authors: Gilles Chemla, Alejandro Rivera, Liyan Shi
  authorList:
    - { family: Chemla, given: Gilles, orcid: "0000-0002-7369-9241", affiliation: Imperial College Business School, DRM/CNRS, CEPR }
    - { family: Rivera, given: Alejandro, orcid: "0000-0001-5836-3902", affiliation: University of Texas at Dallas }
    - { family: Shi, given: Liyan, affiliation: Carnegie Mellon University Tepper School of Business, CEPR }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2921–2970
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13470
  jel:
    codes: [G34, J33, D62]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Economic theories and models", "Corporate Finance and Governance", "Experimental Behavioral Economics Studies"]
  dataAccess: public
  outcome:
    - equilibrium level of executive compensation
    - timing of executive pay (deferral)
    - managerial turnover rate
    - credit line limits and long-term debt levels
  outcomeClass: [labor-careers-health, firm-financing]
  license: >-
    CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0,
    start 2025-07-30; corroborated by artifact p.2921 open access notice)
  licenseShort: CC BY 4.0
  access: open
  machineAccess: blocked-paywall (Wiley site wrapper; CC-BY VOR licence confirmed in Crossref DOI metadata 2026-06-05)
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 6
  citedByCount: 5
  methods:
    role: theory
    family: structural
    buildsFrom: [principal-agent, promotion-contest, dynamic-general-equilibrium, compensation-externality-ge]
  contributionType: [new-theory, new-fact]
  mechanisms: [moral-hazard, agency, search-frictions]
  scope:
    region: theoretical
  relatesTo:
    - { cite: "DeMarzo and Sannikov (2006)", doi: '10.1111/j.1540-6261.2006.01002.x', relation: extends, note: "embeds the DeMarzo-Sannikov dynamic contracting framework in a general equilibrium with endogenous outside options and a compensation externality" }
    - { cite: "Bolton and Scharfstein (1990)", relation: builds-on, note: "two-period two-state moral hazard setup used as the illustrative model in Section I" }
    - { cite: "Biais et al. (2007)", doi: '10.1111/j.1467-937x.2007.00425.x', relation: builds-on, note: "continuous-time limit of the binary cash flow setup, used to ground the full dynamic model" }
    - { cite: "Dicks (2012)", doi: '10.1093/rfs/hhs055', relation: builds-on, note: "welfare criterion (maximize shareholder value) and static compensation externality model that motivates the general equilibrium approach" }
    - { cite: "Acharya and Volpin (2010)", doi: '10.1093/rof/rfp002', relation: cites, note: "static governance externality model in which one firm's effort benefits others via agents' outside options" }
    - { cite: "Gabaix and Landier (2008)", doi: '10.1162/qjec.2008.123.1.49', relation: cites, note: "frictionless assortment theory of executive compensation; this paper shows competitive markets can generate overcompensation without rent extraction" }
    - { cite: "Falato, Li, and Milbourn (2015)", doi: '10.1287/mnsc.2014.2024', relation: cites, note: "documents empirically that CEO pay increases significantly when executives move to a new firm" }
  openQuestions:
    - "Whether managerial heterogeneity and learning about manager quality (via signaling upon termination) would mitigate or amplify the compensation externality identified here (p. 2957)."
    - "Whether the equilibrium features different compensation patterns and capital structures when managers can take long-horizon actions observable only in the distant future (p. 2957)."
    - "What policy interventions would address the inefficiencies in settings where firms and managers can also engage in risk-taking, as in financial services (p. 2957)."
  findings:
    - ref: R1
      outcome: equilibrium level of executive compensation
      metric: coefficient
      value: "W0* > W0^p; in baseline calibration equilibrium W0* approx 15.4 vs planner W0^p = kA = 5.3 (Figure 4, Panel B, p. 2946)"
      direction: positive
      vsBenchmark: equilibrium compensation roughly 3x the socially optimal level in baseline calibration
    - ref: R2
      outcome: timing of executive pay (deferral)
      metric: probability
      value: "S*(W0*) = 0.78 > 0.65 = S^p(W0^p); front-loading proxy is higher in equilibrium (manager receives first payment sooner) (p. 2946)"
      direction: negative
      vsBenchmark: equilibrium deferral is less than socially optimal; pay arrives 20% sooner in equilibrium
    - ref: R3
      outcome: managerial turnover rate
      metric: probability
      value: "T*(W0*) = 0.17 < 0.21 = T^p(W0^p); implied annual turnover rate 2.2% in baseline (Table I and p. 2946)"
      direction: negative
      vsBenchmark: equilibrium turnover rate 19% below socially optimal rate
    - ref: R4
      outcome: credit line limits and long-term debt levels
      metric: level
      value: "CL* < CL^p and D* < D^p (Proposition 5, p. 2942); equilibrium capital structure features lower credit line limits and less long-term debt than the social optimum"
      direction: negative
      vsBenchmark: equilibrium credit lines and debt below planner optimum because compensation must be excessively high and front-loaded
    - ref: R5
      outcome: equilibrium level of executive compensation
      metric: coefficient
      value: "Increasing manager bargaining power beta from 0 to 0.25 more than doubles compensation W0* (Figure 9, Panels B-C, p. 2955); shareholder value falls disproportionately"
      direction: positive
      vsBenchmark: higher managerial bargaining power amplifies overcompensation because stronger outside options worsen the externality
    - ref: R6
      outcome: equilibrium level of executive compensation
      metric: coefficient
      value: "Equilibrium overcompensation W0* - W0^p is increasing in moral hazard severity lambda and cash-flow volatility sigma (Figure 5, p. 2947); industries with higher lambda or sigma show larger shareholder value gaps"
      direction: positive
      vsBenchmark: moral hazard severity amplifies the gap between equilibrium and socially optimal compensation
  resultType: new-finding
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-05, role: extracted, note: "Full text read (pp. 2921-2970); six results extracted from the source PDF. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-05, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; one locator error fixed: R5 Core-results table cited Lemma 6/eq.(23) at p. 2954, corrected to p. 2955 (Lemma 6 is on p. 2955, not p. 2954). All six results, all equations in Theory/Model/Method sections, calibration parameters (Table I, p. 2943), and equilibrium/planner magnitudes (p. 2946) verified against the PDF. No em-dashes, no colorful adjectives. All relatesTo cites locatable in the body. outcomeClass buckets on-registry." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13470", checked: 2026-06-05, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-07-30" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the model it builds on (dynamic principal-agent contracting embedded in a general equilibrium with endogenous outside options), and its main propositions: enough to know what it found and how, without reading all 50 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13470).

## TL;DR

The paper embeds a continuous-time dynamic moral hazard problem (in the spirit of DeMarzo and Sannikov (2006)) into a general equilibrium economy where outside options for managers and liquidation values for firms are endogenously determined by equilibrium compensation. Firms compete for managers by promising deferred pay ("carrots") backed by termination threats ("sticks"). The framework builds on the two-period binary setup of Bolton and Scharfstein (1990) and the continuous-time limit of Biais et al. (2007). The welfare criterion follows Dicks (2012) (maximize shareholder value). In contrast to static governance externality models such as Acharya and Volpin (2010) and frictionless assortment theories of executive compensation such as Gabaix and Landier (2008), the central finding here is that competitive markets generate overcompensation even without rent extraction. Evidence that executive pay rises sharply when CEOs move to a new firm (Falato, Li, and Milbourn (2015)) motivates the focus on endogenous outside options. The resulting competitive equilibrium is inefficient: firms fail to internalize the effect of their compensation packages on the outside options of managers at other firms. This "compensation externality" leads to executives being paid too much (overcompensation), too soon (insufficient deferral), and keeping their jobs for too long (excessively low turnover), while the associated capital structure features excessively low credit line limits and long-term debt.

## Core results

Magnitudes and significance are as reported. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Equilibrium compensation exceeds the social optimum** (overcompensation): firms fail to internalize that raising pay increases the manager's outside option, reducing the effectiveness of termination for all other firms | Corollary 2, p. 2940; Figure 4 Panel B, p. 2946 | In the baseline calibration, equilibrium initial compensation W0\* is approximately 15.4 vs the planner's W0^p = kA = 5.3; equilibrium compensation roughly 3x the planner level |
| R2 | **Insufficient deferral**: overcompensation is front-loaded; managers receive their first payment sooner in equilibrium than under the social optimum | Proposition 4, eq. (19)-(20), p. 2941; p. 2946 | Front-loading proxy S\*(W0\*) = 0.78 > 0.65 = S^p(W0^p); manager paid roughly 20% sooner in equilibrium than optimal |
| R3 | **Excessively long tenure**: overcompensation causes the manager's continuation value to drift upward faster, reducing the likelihood of hitting the termination threshold | Proposition 4, eq. (20), p. 2941; p. 2946 | T\*(W0\*) = 0.17 < 0.21 = T^p(W0^p); equilibrium forced-turnover rate 2.2% per year vs the planner's higher rate |
| R4 | **Capital structure distortion**: the equilibrium compensation contract is implemented with excessively low credit line limits and long-term debt relative to the social optimum | Proposition 5, p. 2942 | CL\* < CL^p and D\* < D^p; debt and credit lines are lower in equilibrium because high, front-loaded compensation requires low debt instruments to remain incentive-compatible |
| R5 | **Managerial bargaining power amplifies overcompensation**: as managers capture a larger share of the surplus, equilibrium compensation more than doubles and shareholder value falls disproportionately | Lemma 6, eq. (23), p. 2955; Figure 9, p. 2955 | Raising manager bargaining power beta from 0 to 0.25 more than doubles W0\*; shareholder value decreases disproportionately because higher pay raises manager outside options, further undermining termination threats |
| R6 | **Moral hazard severity and cash-flow volatility amplify the distortions**: industries with higher lambda or sigma see a larger gap between equilibrium and optimal compensation, more front-loading, and less turnover | Section IV.C, Figures 5-7, pp. 2947-2950 | The shareholder value gap F(W0^p; R^p, L^p) - F(W0\*; R\*, L\*) is increasing in lambda and sigma; compensation W0\* rises steeply in lambda while the planner's W0^p stays near kA |

**Overall (paper's conclusion).** The compensation externality arises because firms are price-takers with respect to the equilibrium outside option: when an individual firm raises pay to maximize its own shareholders' value, it inadvertently increases the outside option for all managers, making termination less effective as an incentive device across the economy. The resulting equilibrium is inefficient even when firms hold all bargaining power and are well-intentioned. A benevolent planner can achieve Pareto improvements by coordinating future compensation down, restoring termination effectiveness without harming managers.

## Theory / model

The model has two parts: an illustrative two-period binary setup (Section I, pp. 2926-2930) and the full continuous-time infinite-horizon model (Section II, pp. 2931-2937).

**Two-period setup (Section I).** The economy has a continuum of risk-neutral firms and managers. Each period, a project generates a binary cash flow: high ($$y > 0$$) with probability $$p$$ or zero with probability $$1-p$$. The manager privately observes realized cash flows and can divert them, receiving a fraction $$\lambda \in (0, 1]$$ of diverted funds. Limited liability requires all compensation payments to be nonneg.

The one-period (static) optimal contract is $$\Gamma^S = \{\tilde{x}, c_H, c_L\}$$ where the firm pays $$c_H = \lambda y$$ if reported cash flow is high and $$c_L = 0$$ otherwise. Outside values satisfy (p. 2927, eq. (1)):

$$
R = \tilde{x}\delta\lambda\mu - \kappa_A \quad \text{and} \quad L = \tilde{x}(1-\lambda)\mu - \kappa_P. \tag{1}
$$

For the two-period dynamic contract $$\Gamma^D = \{x, c\}$$ (continuation probability in the low state $$x$$, period-1 high-state compensation $$c$$), the principal maximizes shareholder value subject to the incentive-compatibility constraint (p. 2929, eq. (2)):

$$
\text{IC-1}: \quad c + \delta\lambda\mu \geq x\delta\lambda\mu + (1 - x)R + \lambda y. \tag{2}
$$

This IC shows that termination threats (setting $$x < 1$$) reduce the cost of incentive provision in the high state by an amount $$\delta\lambda\mu - R$$ that depends critically on the manager's outside option $$R$$. **When $$R$$ is high (outside options are lucrative), termination becomes less effective**, so firms must compensate more.

**Lemma 1** (p. 2929): When agent termination cost $$\kappa_A > \tfrac{1-p}{p}\kappa_P$$, agents are terminated after poor performance and expected compensation is $$(\delta + \delta^2)\lambda\mu - \delta\kappa_A$$; shareholder value is $$2(1-\lambda)\mu + p\kappa_A - (1-p)\kappa_P$$.

**Lemma 2** (p. 2930): If moral hazard is sufficiently severe ($$p\delta\lambda > (1-p)(1-\lambda)$$), the equilibrium features overcompensation. The planner sets outside options to zero by shutting down new matches; shareholders gain up to $$\Delta\mu$$ where $$\Delta \equiv p\delta\lambda - (1-p)(1-\lambda)$$.

**Full continuous-time model (Section II).** Time is continuous and infinite, $$t \in [0, \infty)$$. Cash flows follow

$$
dY_t = \mu\, dt + \sigma\, dB_t,
$$

where $$B_t$$ is a standard Brownian motion. The manager privately observes cumulative cash flows $$Y = \{Y_t\}_{t \geq 0}$$ while the firm relies on reported cash flows $$\hat{Y}$$. The manager can divert $$dY_t - d\hat{Y}_t$$ and receive a fraction $$\lambda$$ of diverted funds. Firms discount at rate $$r$$; managers discount at $$\gamma > r$$ (managers are impatient).

The firm's initial value under contract $$\Gamma = (C, \tau)$$ (cumulative compensation process and termination time) is (p. 2932):

$$
F_0(\hat{Y}; \Gamma) \equiv \mathbb{E}\!\left[\int_0^\tau e^{-rt}(d\hat{Y}_t - dC_t) + e^{-r\tau}L\right].
$$

The manager's initial value is:

$$
W_0(\hat{Y}; \Gamma) \equiv \mathbb{E}\!\left[\int_0^\tau e^{-\gamma t}\!\left(dC_t + \lambda(dY_t - d\hat{Y}_t)\right) + e^{-\gamma\tau}R\right].
$$

The optimal contract solves (p. 2933, eqs. (3)-(5)):

$$
\max_{W_0, \Gamma} F_0(Y; \Gamma) \tag{3}
$$

subject to the promise-keeping constraint $$W_0(Y; \Gamma) = W_0$$ and the incentive-compatibility constraint $$W_t(Y; \Gamma) \geq W_t(\hat{Y}; \Gamma)$$ for all $$t \in [0, \tau]$$.

The equilibrium conditions pin down the endogenous outside option $$R^*$$ and liquidation value $$L^*$$ (p. 2934, eqs. (6)-(7)):

$$
R^* = W_0^* - \kappa_A, \tag{6}
$$

$$
L^* = F_0^* - \kappa_P. \tag{7}
$$

**Proposition 1** (p. 2937, eq. (16)): Under Assumption 1, the unique equilibrium compensation level $$W_0^*$$ satisfies

$$
F'(W_0^*; R^*, L^*) = 0. \tag{16}
$$

The firm maximizes its value function at the interior point where the marginal value of promised compensation is zero, taking outside options as given.

**Proposition 3** (Social Optimum, p. 2939, eq. (18)): The socially optimal compensation $$W_0^p$$ satisfies

$$
F'(W_0^p; R^p, L^p) + \frac{\partial}{\partial R}F(W_0^p; R^p, L^p) \leq 0. \tag{18}
$$

The second term, $$\frac{\partial}{\partial R}F < 0$$, is the general equilibrium effect: a $1 increase in compensation raises managers' outside options by $1, reducing firm value. Firms in equilibrium set $$F'(W_0^*) = 0$$, ignoring this negative externality, so $$W_0^* > W_0^p$$ (Corollary 2).

## Method

This is a theory paper. The solution method combines:

1. **Optimal contract characterization via the HJB/ODE.** Following DeMarzo and Sannikov (2006), the firm's value function $$F(W; R, L)$$ is characterized by an ODE (Corollary 1, p. 2936, eqs. (11)-(13)):

$$
rF(W; R, L) = \mu + \gamma W F'(W; R, L) + \tfrac{1}{2}\lambda^2\sigma^2 F''(W; R, L), \quad R \leq W < \bar{W}, \tag{11}
$$

$$
F'(W; R, L) = -1, \quad W \geq \bar{W}, \tag{12}
$$

with boundary conditions $$F(R; R, L) = L$$ and $$rF(\bar{W}; R, L) = \mu - \gamma\bar{W}$$. The optimal contract (Lemma 3, p. 2935) specifies:

- **(i) Pay-for-performance:** $$dW_t = \gamma W_t\, dt - dC_t + \lambda(dY_t - \mu\, dt)$$.
- **(ii) Deferral:** payments only when $$W_t \geq \bar{W}$$.
- **(iii) Termination:** $$\tau = \min\{t \mid W_t = R\}$$.

The ODE is solved numerically; existence and uniqueness of the equilibrium are established analytically (Propositions 1, Appendix D-E, pp. 2961-2965).

2. **Equilibrium fixed-point.** The equilibrium $$(R^*, L^*)$$ is found as a fixed point of eqs. (6) and (7) given the solution to the firm's contracting problem. Proposition 1 shows that the FOC $$F'(W_0^*) = 0$$ pins down the unique interior equilibrium.

3. **Calibration.** Parameters are calibrated to data moments (Table I, p. 2943): $$r = 0.04$$ (annual interest rate), $$\gamma = 0.09$$ (manager discount rate), $$\mu = 10$$ (normalization), $$\sigma = 9$$ (matching 10-15% fraction with operating losses), $$\lambda = 0.29$$ (moral hazard; Ward (2023)), $$\kappa_P = 15$$ (6% CEO replacement cost; Taylor (2010)), $$\kappa_A = 5.3$$ (2.2% forced turnover rate; Taylor (2010)).

The model is extended in Section V to incorporate: (i) noncompete clauses (Lemma 4), (ii) endogenous termination costs via a search framework (Lemma 5), (iii) Nash bargaining (Lemma 6, eq. (22)-(23)), and (iv) forward-looking firm liquidation values (Lemma 7).

## Empirical specifications

This is a pure theory and calibration paper with no regression analysis. There are no panel regressions, no instrumental variable designs, and no event studies. The "empirical" content consists of:

- **Calibration targets** matched to observed moments: fraction of firms with operating losses, annual interest rates, manager discount rate (Ward (2023), Chen et al. (2023)), forcing-turnover rate (Taylor (2010), Eisfeldt and Kuhnen (2013), Jenter and Kanaan (2015)), and CEO replacement costs (Taylor (2010)).
- **Quantitative comparative statics** (Figures 5-9, pp. 2947-2955): the model computes equilibrium versus planner outcomes as each parameter ($$\lambda$$, $$\kappa_A$$, $$\kappa_P$$, $$\beta$$) varies, holding others at calibrated values from Table I.
- **Welfare comparisons**: the gap $$F(W_0^p; R^p, L^p) - F(W_0^*; R^*, L^*)$$ is computed numerically (Figures 3-4) and reported as the gain from planner intervention.

The paper generates the following testable empirical predictions (Section IV.C, pp. 2947-2950): (1) CEO overcompensation is more severe in industries with more mobile managers (lower $$\kappa_A$$) or higher CEO replacement costs for firms (higher $$\kappa_P$$); (2) overcompensation, insufficient deferral, and excessive tenure are most pronounced in industries with high cash-flow volatility or severe moral hazard; (3) the credit line limits and long-term debt of firms are excessively low in equilibrium.

## Datasets used

This is a pure theory paper. It does not use empirical datasets directly. Calibration relies on parameter estimates reported in the literature:

| Source | Role in paper | Wiki page |
|---|---|---|
| Ward (2023) estimates of CEO discount rate and moral hazard parameter | Calibrate $$\gamma = 0.09$$ and $$\lambda = 0.29$$ (Table I) | No page yet |
| Taylor (2010) structural estimates of CEO replacement costs and turnover | Calibrate $$\kappa_P = 15$$ (6% replacement cost) and $$\kappa_A = 5.3$$ (2.2% forced turnover) | No page yet |
| Chen et al. (2023) manager discount rate estimates | Cross-check for $$\gamma$$ (11% estimate; paper uses 9%) | No page yet |
| Eisfeldt and Kuhnen (2013); Jenter and Kanaan (2015) | Cross-check for forced turnover rate lower bound (1.6-2.8%) | No page yet |

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13470) if you are: (a) building or extending a dynamic contracting model in a general equilibrium setting; (b) analyzing the policy implications of executive compensation externalities (noncompete clauses, pay transparency mandates); (c) studying the connection between optimal incentive contracts and capital structure in the spirit of DeMarzo and Sannikov (2006); or (d) replicating the quantitative calibration and comparative statics (Figures 2-9). The Internet Appendix contains proofs of renegotiation-proofness and the tax-implementation of the social optimum as an equilibrium.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The CC BY 4.0 licence permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Chemla, Gilles, Alejandro Rivera, and Liyan Shi.
> "Too Much, Too Soon, for Too Long: The Dynamics of Competitive Executive Compensation."
> *The Journal of Finance* 80, no. 5 (October 2025): 2921-2970.
> DOI: 10.1111/jofi.13470. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
