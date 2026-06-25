---
title: "Worker Runs: Hoffmann & Vladimirov (2025)"
description: >-
  Distilled: Hoffmann and Vladimirov model how firms design compensation
  contracts to prevent contagious collective worker departures ("worker runs"),
  showing that dilutable output-dependent pay and asymmetric compensation
  structures resolve the coordination problem at no extra cost. J. Finance 2025,
  CC BY-NC 4.0. Six core results with source locators, the model equations, and
  the key propositions.
sidebar:
  label: Hoffmann-Vladimirov 2025
  order: 1
tags: [paper-summary, corporate-finance, compensation, labor, theory, peer-reviewed,
       unreplicated]
paper:
  authors: Florian Hoffmann, Vladimir Vladimirov
  authorList:
    - { family: Hoffmann, given: Florian, orcid: "0000-0002-1147-0652", affiliation: KU Leuven }
    - { family: Vladimirov, given: Vladimir, orcid: "0000-0003-0747-4834", affiliation: "University of Amsterdam and CEPR" }
  year: 2025
  venue: "The Journal of Finance 80(2), April 2025, 937-979"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13424
  jel:
    codes: [G30, G32, J33]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics:
    - Banking stability, regulation, efficiency
    - Corporate Finance and Governance
    - Taxation and Compliance Studies
  dataAccess: public
  outcome:
    - firm's expected worker compensation cost
    - worker retention probability (full vs. partial)
    - optimal compensation structure (output-dependent vs. output-independent share)
  outcomeClass: [labor-careers-health, firm-financing]
  license: >-
    CC BY-NC 4.0 (confirmed via Crossref DOI metadata: content-version vor,
    URL http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days 0,
    start 2025-01-30)
  licenseShort: CC BY-NC 4.0
  access: open
  machineAccess: "open-access (Wiley/JF CC BY-NC 4.0 VOR; confirmed via Crossref 2026-06-06)"
  redistribution: extract-only (CC BY-NC 4.0 permits non-commercial reproduction; PDF not hosted in this batch)
  resultsCount: 6
  citedByCount: 6
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, repeated-game, mechanism-design]
  contributionType: [new-theory]
  mechanisms: [agency, moral-hazard]
  scope:
    region: theoretical
    assetClass: human capital (teams of skilled workers)
  findings:
    - ref: R1
      outcome: firm's expected worker compensation cost
      metric: coefficient
      value: "Coordination problem resolved at zero additional cost relative to the relaxed (no-friction) benchmark when the monotonicity-in-retention constraint is slack (Proposition 3)"
      direction: none
      vsBenchmark: same cost as frictionless benchmark
    - ref: R2
      outcome: optimal compensation structure (output-dependent vs. output-independent share)
      metric: coefficient
      value: "Optimal dilution degree strictly increasing in equilibrium share of output-dependent pay (Corollary 1); dilution achieved by making output-dependent pay decreasing in retention for complements, output-independent pay decreasing in retention for substitutes (Corollary 2)"
      direction: positive
    - ref: R3
      outcome: firm's expected worker compensation cost
      metric: coefficient
      value: "Symmetric contracts conditioning on overall retention n are cheaper than asymmetric contracts that cannot condition on n, unless the shadow cost of the monotonicity-in-retention constraint under optimal symmetric contracting is sufficiently high (Lemma 3)"
      direction: negative
      vsBenchmark: symmetric-n contracts weakly dominate asymmetric-i contracts absent binding feasibility
    - ref: R4
      outcome: firm's expected worker compensation cost
      metric: coefficient
      value: "When optimal symmetric contracting entails positive coordination costs, there always exists an asymmetric contract that strictly reduces expected compensation costs (Proposition 7)"
      direction: negative
      vsBenchmark: strictly lower than optimal symmetric contract
    - ref: R5
      outcome: optimal compensation structure (output-dependent vs. output-independent share)
      metric: coefficient
      value: "Under optimal asymmetric contracts, higher-ranked workers (those whose decision to stay is independent of fewer coworkers) receive a higher share of output-independent pay; the lowest-ranked worker earns strictly positive rent for all shock realizations above the lower bound (Proposition 5)"
      direction: positive
    - ref: R6
      outcome: firm's expected worker compensation cost
      metric: coefficient
      value: "Combining asymmetric compensation (contracting on worker identity i) with symmetric dilutable contracts (contracting on retention n) always weakly reduces coordination costs relative to either tool used alone; when optimal symmetric contracting has positive coordination costs this combination strictly reduces costs (Proposition 7 + Lemma 3)"
      direction: negative
      vsBenchmark: strictly lower coordination costs than either tool alone when symmetric contracting is costly
  resultType: new-finding
  relatesTo:
    - { cite: "Diamond and Dybvig (1983)", doi: '10.1086/261155', relation: builds-on, note: "Worker runs modeled as a coordination failure analogous to bank runs; same structure of multiple self-fulfilling equilibria" }
    - { cite: "Goldstein and Pauzner (2005)", doi: '10.1111/j.1540-6261.2005.00762.x', relation: builds-on, note: "Demand-deposit contracts and bank-run probability; worker-run model is the labor-market analog" }
    - { cite: "Winter (2004)", doi: '10.1257/0002828041464434', relation: extends, note: "Extends Winter's asymmetric contracting results by allowing differences in compensation structure (type of pay), not just level, as the instrument" }
    - { cite: "Halac, Kremer, and Winter (2020)", doi: '10.1257/aer.20190234', relation: extends, note: "Extends their heterogeneous-investor capital-raising model to the worker-retention setting, adding the coordination friction" }
    - { cite: "Oyer (2004)", doi: '10.1111/j.1540-6261.2004.00674.x', relation: builds-on, note: "Optimal output-dependent pay matches workers' on-the-job pay to their outside options; dilution design follows this matching motive" }
  openQuestions:
    - "How to extend the model to non-full-retention policies when workers do not observe the shock precisely, and to richer renegotiation environments (discussed informally in Section IV.C and Internet Appendix, pp. 963-965)."
    - "Empirical tests of Implications 1-3 require identifying the sensitivity of workers' outside options to systematic shocks and proxies for how quickly firms can fill vacancies; suitable proxies are noted but not constructed (pp. 966, 969)."
    - "The interaction between worker-run risk and talent acquisition (hiring) is set aside; extending the model to cover both the retention and the recruitment margin is stated as outside the paper's scope (p. 944)."
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: >-
        Full PDF read (pp. 937-979); model equations, propositions, corollaries,
        and empirical implications extracted. Not human-verified. Not reproduced.
        This is a theory paper; no empirical results, so findings[] entries report
        the quantitative/qualitative comparative statics from the propositions.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; two fixes applied: (1) eq. (13) corrected: the garbled ratio p(eps,N)/p(eps,N)*p(eps,N)/p(eps,i) replaced with the correct p(eps,N)/p(eps_lo,N)*p(eps_lo,N)/p(eps_lo,i) using the lower-bound eps_lo as in the PDF (p. 959); (2) removed new-fact from contributionType (pure theory paper, no empirical regularity established). All proposition/lemma locators (R1-R6), equation terms, and frontmatter facts confirmed against the PDF."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13424
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc/4.0/, delay-in-days=0, start=2025-01-30"
  rightsSignalConflict: false
---

**What this is.** The paper's core propositions, the model it builds, and the
compensation design results: enough to understand what it found and how, without
reading all 43 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13424).

## TL;DR

Hoffmann and Vladimirov develop a theory of "worker runs": because workers
privately observe a firm-wide productivity shock, and because a departing
skilled worker reduces the value of remaining workers' output-dependent pay,
an initial departure can trigger further departures even from an otherwise
healthy firm. The modeling of collective turnover as a coordination failure is
similar to the bank-run literature of Diamond and Dybvig (1983) and Goldstein
and Pauzner (2005). Unlike bank runs, however, standard remedies such as
deposit insurance have no direct labor-market analog, so the paper focuses on
compensation design instead. The paper shows that firms can design compensation
contracts to prevent such contagious collective turnover at no extra cost
relative to a frictionless benchmark. The key instruments are (i) making
compensation "dilutable" (promising workers more when others leave) to smooth
workers' expected pay across retention scenarios, and (ii) offering ex-ante
identical workers differently structured contracts (asymmetric compensation) to
ensure that a critical subset always stays, removing the strategic
complementarity for the rest. The asymmetric contracting results extend Winter
(2004) and Halac, Kremer, and Winter (2020) by studying differences in
compensation structure rather than compensation level. The dilution results
build on Oyer (2004)'s insight that firms optimally match workers'
on-the-job pay to their outside options. The paper characterizes optimal
symmetric and asymmetric contracts and derives empirically testable implications
for dilution, compensation structure, and worker targeting.

## Core results

Propositions and results are as stated in the paper. Locators point into the
source PDF.

| # | Result | Locator | Content |
|---|---|---|---|
| R1 | Dilutable or fixed-wage contracts always resolve the coordination problem at zero extra cost versus the frictionless benchmark | Propositions 2-3, pp. 950-953 | Optimal contract sets expected compensation constant in retention level n for each shock realization (W(eps,n) = W(eps,N) for all n), achieved by dilution whenever the output-dependent component is positive |
| R2 | Optimal degree of dilution increases in the equilibrium share of output-dependent pay and in the sensitivity of firm success to retention | Corollaries 1-2, pp. 954-955; Figure 2, p. 955 | Dilution through decreasing output-dependent pay (complements case) or decreasing output-independent pay (substitutes case); both w(n) and delta-w(n) move to achieve smoothing |
| R3 | Symmetric contracts conditioning on overall retention n are weakly cheaper than asymmetric contracts that cannot condition on n | Lemma 3, p. 962 | Conditioning on n allows off-equilibrium promises to differ from equilibrium pay, fully absorbing coordination costs; asymmetric-only contracts must resolve coordination on-equilibrium, which is costlier |
| R4 | When symmetric contracting entails positive coordination costs, combining asymmetric structure with dilution strictly reduces expected costs | Proposition 7, p. 962 | Offering the optimal symmetric contract to N-1 workers and the relaxed-problem contract to worker N halves per-worker coordination cost; generally yields strictly lower total cost |
| R5 | Under optimal asymmetric contracts, higher-ranked workers receive a higher share of output-independent pay and do not necessarily earn more rent | Proposition 5, pp. 959-960 | Higher-ranked workers' decision to stay must be independent of more coworkers, so their output-dependent pay is more mispriced by the coordination friction; firm compensates with safer output-independent pay |
| R6 | Workers retained with higher probability in asymmetric retention policies optimally receive higher output-independent pay when shocks are idiosyncratic; higher output-dependent pay when shocks are systematic with outside options more sensitive than firm output | Internet Appendix Propositions IA.2, IA.5, p. 964 | Compensation-type allocation responds to which friction dominates: coordination (pushes toward fixed pay) vs. noncontractibility of the shock (pushes toward output-dependent pay for high-retention workers) |

**Overall (paper's conclusion).** Mitigating collective contagious turnover
poses additional challenges relative to individual turnover and requires
different compensation solutions. The tools the paper proposes, making
compensation dilutable or offering asymmetric contracts, can be easily
implemented with equity-based pay, profit-sharing bonus pools, retention
bonuses, and title-linked pay differences that are already common in practice
(pp. 970).

## Theory / model

The baseline model (Section I, pp. 943-945) has a firm that hires $$N \geq 2$$
risk-neutral workers at $$t = 0$$. The firm's only asset is a project that
generates cash flows at $$t = 2$$: $$x > 0$$ if the project fails and $$x + \Delta x$$
with $$\Delta x > 0$$ if it succeeds. The probability of success at interim date
$$t = 1$$ depends on an exogenous shock $$\varepsilon$$ (drawn from distribution $$G$$
with support $$[\underline{\varepsilon}, \bar{\varepsilon}]$$) and on the number of workers $$n$$
retained until $$t = 2$$ (p. 943, eq. 1):

$$
p(\varepsilon, n) = \alpha(n) + \beta(\varepsilon)\gamma(n), \tag{1}
$$

with $$\beta(\varepsilon), \beta'(\varepsilon) > 0$$ for all $$\varepsilon$$ and $$\gamma(n) > 0$$ for all
$$n$$, so both the shock and retention increase the probability of success.
Workers observe the shock $$\varepsilon$$ privately at $$t = 1$$ and decide
simultaneously whether to stay or take an outside option of value
$$\underline{w}(\varepsilon) \geq 0$$.

Each worker $$i$$ is offered a compensation contract
$$C_i = (w_i(n), \Delta w_i(n))_{n=1}^{N}$$, which specifies output-independent pay
$$w_i(n)$$ and output-dependent pay $$\Delta w_i(n)$$ conditional on the number $$n$$
of workers retained. The firm's objective is to minimize workers' expected
equilibrium rent (expected compensation minus outside option) subject to
achieving full retention as the unique equilibrium at $$t = 1$$.

The expected surplus of retaining $$n$$ workers is (p. 944, eq. 2):

$$
\Omega(\varepsilon, n) := x + p(\varepsilon, n)\Delta x - n\underline{w}(\varepsilon), \tag{2}
$$

which the paper assumes is positive and nondecreasing in $$n$$ for all $$\varepsilon$$
(retaining more workers is always efficient).

**Worker runs as coordination failure.** For symmetric contracts
$$C_i = C$$, workers play a coordination game at $$t = 1$$. Workers' expected
on-the-job compensation is $$W(\varepsilon, n) := w(n) + p(\varepsilon, n)\Delta w(n)$$,
which increases in $$n$$ whenever output-dependent pay is positive. This creates
strategic complementarities: a worker is more likely to stay if others stay,
since the firm's success probability and thus the value of her equity/bonus
increases with retention. Proposition 1 (p. 947) characterizes the resulting
equilibrium structure. A worker-run equilibrium, in which all workers leave,
exists whenever

$$
W(\varepsilon, N) \geq \underline{w}(\varepsilon) > W(\varepsilon, 1), \tag{3}
$$

that is, staying is attractive only when all others stay but not when alone.
Under condition (3) a full-retention equilibrium also exists, and the
worker-run equilibrium is Pareto-dominated by it.

**Monotonicity-in-retention constraint** (Assumption 1, p. 952): To rule out
unrealistic contracts that reward workers for inducing coworkers to leave, the
paper imposes that workers' expected on-the-job pay must be nondecreasing in
the number of retained workers: $$W_i(\varepsilon, n) \geq W_i(\varepsilon, n-1)$$ for
all $$(\varepsilon, n)$$ and $$i$$. This constraint limits the degree of dilution.

**Dilutability** (Definition 1, p. 948): Compensation of worker $$i$$ is
dilutable at $$(\varepsilon, n)$$ if, holding the success probability constant at any
$$\hat{p} \in [p(\varepsilon, n-1), p(\varepsilon, n)]$$, expected compensation
$$\hat{W}_i(\hat{p}, n) := w_i(n) + \hat{p}\Delta w_i(n)$$ decreases in
retention (eq. 4):

$$
\hat{W}_i(\hat{p}, n) - \hat{W}_i(\hat{p}, n-1)
= w_i(n) - w_i(n-1) + \hat{p}[\Delta w_i(n) - \Delta w_i(n-1)] < 0. \tag{4}
$$

Equity-based pay exhibits this dilutability because the firm's equity "pie" is
shared among fewer workers when some depart, so each remaining worker's
percentage stake rises even as the total pie shrinks.

## Method

This is a contract-theory paper with no econometric estimation. The solution
method is backward induction in a three-period ($$t = 0, 1, 2$$) game with
incomplete information (the shock $$\varepsilon$$ is private), building on
`principal-agent`, `repeated-game`, and `mechanism-design` techniques.

The firm's optimization at $$t = 0$$ is to design contracts that implement full
retention as the unique equilibrium at $$t = 1$$ at minimum expected
compensation cost. For symmetric contracts, this reduces to Problem 1 (p. 950,
eqs. 5-6):

$$
\min_{C \in \mathbf{C}^f} \int_{\underline{\varepsilon}}^{\bar{\varepsilon}}
[w(N) + p(\varepsilon, N)\Delta w(N) - \underline{w}(\varepsilon)] \, dG(\varepsilon) \tag{5}
$$

$$
\text{subject to} \quad W(\varepsilon, n) = w(n) + p(\varepsilon, n)\Delta w(n)
\geq \underline{w}(\varepsilon) \quad \forall (\varepsilon, n). \tag{6}
$$

Constraint (6) is the full-retention participation constraint requiring staying
to be dominant for all shock realizations and all retention levels. Together
with the monotonicity-in-retention constraint (Assumption 1), this implies
that optimal contracts satisfy (p. 952, eq. 7):

$$
W(\varepsilon, N) \geq \ldots \geq W(\varepsilon, 1) \geq \underline{w}(\varepsilon)
\quad \forall (\varepsilon, n). \tag{7}
$$

Workers' equilibrium rent can be decomposed as the sum of incremental rents
(p. 952, eq. 8):

$$
R(\varepsilon, N) := [W(\varepsilon,N) - W(\varepsilon,N-1)] + \ldots + [W(\varepsilon,1) - \underline{w}(\varepsilon)] \geq 0. \tag{8}
$$

The key insight is that minimizing total expected rent pushes as many
incremental rents to zero as possible, making expected compensation constant in
$$n$$: $$W(\varepsilon, n) = W(\varepsilon, N)$$ for all $$(\varepsilon, n)$$. This requires
choosing the output-dependent component $$\Delta w(n)$$ to offset the retention
sensitivity of $$p(\varepsilon, n)$$ (pp. 952-953, eqs. 9-10):

$$
\Delta w(n-1) = \frac{\gamma(n)}{\gamma(n-1)} \Delta w(n), \tag{9}
$$

$$
w(n-1) = w(n) + \left[\alpha(n) - \alpha(n-1)\frac{\gamma(n)}{\gamma(n-1)}\right] \Delta w(n). \tag{10}
$$

For asymmetric contracts (Section IV), each worker $$i$$ (indexed by rank in
the iterative dominance ordering) faces Problem 2 (p. 959, eq. 12):

$$
\min_{\{w_i, \Delta w_i\}_{i=1}^{N} \in \mathbf{C}^f} \sum_{i=1}^{N}
\int_{\underline{\varepsilon}}^{\bar{\varepsilon}} [W_i(\varepsilon, N) - \underline{w}(\varepsilon)] \, dG(\varepsilon)
\quad \text{s.t.} \quad (11) \; \forall i, \tag{12}
$$

where the participation constraint for worker $$i$$ at rank $$i$$ is (eq. 11):

$$
W_i(\varepsilon, i) = w_i + p(\varepsilon, i)\Delta w_i \geq \underline{w}(\varepsilon) \quad \forall \varepsilon. \tag{11}
$$

Worker $$i$$'s expected rent under idiosyncratic risk is (p. 959, eq. 13):

$$
\int_{\underline{\varepsilon}}^{\bar{\varepsilon}} [W_i(\varepsilon, N) - \underline{w}] \, dG(\varepsilon)
= \int_{\underline{\varepsilon}}^{\bar{\varepsilon}} (\underline{w} - w_i)
\left(\frac{p(\varepsilon, N)}{p(\underline{\varepsilon}, N)} \cdot \frac{p(\underline{\varepsilon}, N)}{p(\underline{\varepsilon}, i)} - 1\right) dG(\varepsilon). \tag{13}
$$

The ratio $$p(\underline{\varepsilon}, N)/p(\underline{\varepsilon}, i)$$ is decreasing in rank $$i$$, so
higher-ranked workers (lower $$i$$) misprice output-dependent pay more,
making output-independent pay relatively cheaper for the firm.

## Empirical specifications

This is a theory paper. It has no econometric estimation. Section V
(pp. 966-969) translates the propositions into testable cross-sectional
implications.

**Implication 1** (p. 966): When firms relying on hard-to-replace skilled
workers pay with output-dependent compensation, they should make that
compensation dilutable. The degree of dilution is higher when (i) firm
performance is more sensitive to retention and (ii) the share of
output-dependent pay is higher.

**Implication 2** (p. 967): Dilution provisions are more likely to be tied to
output-dependent pay ($$\Delta w(n)$$ decreasing in $$n$$) if technological shocks
increase firm productivity more at higher retention levels (complements), and
to output-independent pay ($$w(n)$$ decreasing in $$n$$) if shocks increase
productivity more at lower retention levels (substitutes).

**Implication 3** (p. 969): (i) Firms can lower the cost of preventing worker
runs by offering identical workers different compensation types, with
higher-ranked workers receiving a higher share of output-independent pay and
lower-ranked workers a higher share of output-dependent pay. Resource-constrained
firms especially benefit. (ii) If firms seek to retain some workers with higher
probability, they should optimally pay those workers with a higher share of
output-independent pay when shocks are idiosyncratic; with a higher share of
dilutable performance/equity-based pay when outside options are more sensitive
than firm output to common shocks.

Tests of these implications require identifying sensitivity of workers' outside
options to systematic shocks (proxied by comovement with closely related peer
firms, using Hoberg and Phillips (2016) network similarity scores), and the
share of output-dependent pay (proxied by proportion of equity-based pay per
Bergman and Jenter (2007)). Time-vesting equity implements the dilution pattern
of Panel A.3 of Figure 2; equity buyback agreements implement Panel A.1;
retention bonuses implement Panels B and C (p. 968).

## Datasets used

This is a theoretical paper. No datasets are used for estimation. The
paper references management and industry survey evidence to motivate the
setting (turnover contagion studies, industry reports on quit rates and
replacement costs) but does not analyze microdata.

| Dataset / Source | Role | Wiki page |
|---|---|---|
| Industry surveys and management studies (cited in motivation) | Motivational evidence on quit rates, contagion, and replacement costs | No page yet |

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13424) if you are: building
a model of collective turnover or contagious labor-market dynamics; designing
compensation contracts for teams of skilled workers in startups or professional
services; studying the retention properties of equity-based versus fixed pay or
bonus pools; or extending the model to richer information structures (global
games refinements) and renegotiation environments, which are analyzed in the
Internet Appendix.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025, pp. 937-979.
DOI: [10.1111/jofi.13424](https://doi.org/10.1111/jofi.13424).

This distillation was extracted by an LLM on 2026-06-06 and is **not
human-verified or independently reproduced**. The CC BY-NC 4.0 licence permits
non-commercial reproduction with attribution; the verbatim PDF is not hosted
in this batch.

> **Attribution (CC BY-NC 4.0).** Hoffmann, Florian, and Vladimir Vladimirov.
> "Worker Runs." *The Journal of Finance* 80, no. 2 (April 2025): 937-979.
> DOI: 10.1111/jofi.13424. (c) 2025 The Author(s).
> Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
