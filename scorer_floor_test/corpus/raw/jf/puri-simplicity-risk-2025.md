---
title: "Simplicity and Risk: Puri (2025)"
description: >-
  Distilled: This paper introduces and axiomatizes a preference for simplicity
  in choice under risk, showing that participants' measured risk aversion and
  dominance violations increase with lottery complexity (number of outcomes),
  holding moments fixed, and that no canonical behavioral theory fully captures
  this. J. Finance 2025, paywalled. Six core results with source locators,
  the simplicity representation model with axioms, and the experimental design.
sidebar:
  label: Puri 2025
  order: 1
tags: [paper-summary, behavioral-finance, decision-theory, risk-preferences,
       experimental-economics, peer-reviewed, unreplicated]
paper:
  authors: Indira Puri
  authorList:
    - { family: Puri, given: Indira, affiliation: "Stern School of Business, New York University" }
  year: 2025
  venue: The Journal of Finance 80(2), April 2025, 1029-1080
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13417
  jel:
    codes: [D81, G41, C91]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Decision-Making and Behavioral Economics", "Economic theories and models", "Complex Systems and Time Series Analysis"]
  dataAccess: hand-collected
  introducesData: true
  outcome:
    - measured risk aversion (CRRA parameter) by lottery complexity
    - dominance violation frequency by number of outcomes
    - certainty equivalents for lotteries with 2, 4, 8, and 16 outcomes
    - complexity aversion (differences-in-differences axiom satisfaction rate)
  outcomeClass: [household-finance]
  license: >-
    Wiley VOR licence (content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2024-12-30); not CC-licensed; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site; confirmed via Crossref DOI metadata 2026-06-06)
  redistribution: extract-only
  resultsCount: 6
  citedByCount: 25
  methods:
    role: both
    contributes: simplicity-representation
    family: theory
    buildsFrom: [randomized-survey-experiment]
    identification: randomized
  contributionType: [new-theory, new-fact, new-data]
  mechanisms: [behavioral-bias]
  scope:
    region: US
    period: 2022-09..2022-10
    frequency: mixed
    dataType: [experimental]
    granularity: [individual]
    n: "582 participants (Amazon Mechanical Turk, preregistered)"
  findings:
    - ref: R1
      outcome: "measured risk aversion (CRRA parameter) by lottery complexity"
      metric: coefficient
      value: "CRRA alpha: 0.67 [0.38,1.00] at 2 outcomes; 1.38 [1.05,1.71] at 4; 3.21 [2.68,3.84] at 8; 5.93 [5.06,7.07] at 16 outcomes"
      direction: positive
      vsBenchmark: "increases from 0.67 to 5.93 within-subject from 2 to 16 outcomes (Figure 1, p. 1030)"
    - ref: R2
      outcome: "dominance violation frequency by number of outcomes"
      metric: probability
      value: "3.9% at 2 outcomes; 4.4% at 4; 5.2% at 8; 6.4% at 16 outcomes"
      direction: positive
      vsBenchmark: "violations 1.5x more frequent at 16 than at 2 outcomes; increase marginally significant at p=0.08 (Figure 2, p. 1040)"
    - ref: R3
      outcome: "complexity aversion (differences-in-differences axiom satisfaction rate)"
      metric: probability
      value: "84-90% of participants satisfy axiom for at least 2/3 pairs at each 2 vs n comparison; 57-59% strictly satisfy for at least 1 of 3 pairs"
      direction: positive
      vsBenchmark: "axiom satisfaction significantly above 50% random-clicking rate at p<0.01 (Table I, p. 1039)"
    - ref: R4
      outcome: "complexity aversion magnitude (c - c' dollar spread)"
      metric: level
      value: "$0.005 for 2 vs 4 outcomes; $0.012 for 2 vs 8; $0.146 for 2 vs 16 outcomes"
      direction: positive
      vsBenchmark: "difference between 2 vs 4 and 2 vs 8 statistically significant at p<0.01; more than twice the average RRP (p. 1039)"
    - ref: R5
      outcome: "measured risk aversion (CRRA parameter) by lottery complexity"
      metric: coefficient
      value: "Cognitive ability gap in CRRA alpha: 0.86 at 2 outcomes (marginal p<0.1); 2.02 at 8 outcomes (p<0.05); 3.83 at 16 outcomes (p<0.05)"
      direction: positive
      vsBenchmark: "low-cognitive-ability individuals highly complexity averse at 8 and 16 outcomes; pattern absent for high-cognitive-ability group (Figure 3, p. 1042)"
    - ref: R6
      outcome: "measured risk aversion (CRRA parameter) by lottery complexity"
      metric: coefficient
      value: "Separability test: alpha estimates 0.11 (SE 0.07) at 8 outcomes and 0.21 (SE 0.17) at 16 outcomes when complexity costs explicitly controlled; difference from 2.7 gap when uncontrolled"
      direction: none
      vsBenchmark: "alpha estimates not statistically distinguishable across complexity levels once C(n) controlled, supporting separability (p. 1043)"
  resultType: new-finding
  relatesTo:
    - { cite: "Tversky and Kahneman (1992)", doi: '10.1007/bf00122574', relation: tests, note: "CPT residuals significantly correlated with number of outcomes (slope 0.03, p<0.01); CPT cannot capture complexity aversion" }
    - { cite: "Kahneman and Tversky (1979)", doi: '10.2307/1914185', relation: tests, note: "PT residuals also significantly correlated with number of outcomes (slope 0.05, p<0.01); PT cannot explain simplicity behavior" }
    - { cite: "Bordalo, Gennaioli, and Shleifer (2012)", doi: '10.1093/qje/qjs018', relation: tests, note: "Salience residuals positive and significant; salience cannot capture dominance violations" }
    - { cite: "Sims (2003)", doi: '10.1016/s0304-3932(03)00029-1', relation: tests, note: "Canonical rational inattention model: best-fitting information cost lambda does not increase in complexity; RI cannot explain mean effects" }
    - { cite: "Gabaix (2014)", doi: '10.1093/qje/qju024', relation: tests, note: "Sparsity: moments held fixed so most important variables are identical across complexity levels; sparsity cannot explain results" }
    - { cite: "Woodford (2012)", doi: '10.1257/aer.102.3.41', relation: tests, note: "Cognitive noise with ignorance prior correction: increasing risk aversion pattern remains after correcting for 5-50% weight on ignorance prior" }
    - { cite: "Goodman and Puri (2023)", relation: cites, note: "Applies simplicity preferences to retail binary options, finding complexity premia in two-outcome lotteries" }
    - { cite: "Fudenberg and Puri (2022a)", doi: '10.1257/pandp.20221091', relation: cites, note: "Extends simplicity framework to combine CPT and simplicity in a heterogeneous-agent setting" }
  openQuestions:
    - "Whether cognitive mechanisms underlying simplicity preferences are inherent to the counting measure or generalize to other notions of complexity such as language effects in company filings (p. 1052)."
    - "Whether the theory applies to incentive schemes with many piecewise-linear components (e.g. 401(k) employer match) and how complexity interacts with institutional details (p. 1052)."
    - "Extension to probability-based notions of complexity: the axiomatic restrictions rule these out for consistency, but they may exist empirically (Footnote 21, p. 1050)."
  replicationCode:
    status: none
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1029-1058 + conclusion); six results extracted from the PDF. Not human-verified. Not reproduced. Preregistered experiment (AEA RCT Registry Trial ID 10136)." }
    - by: "paper-verifier (claude-sonnet-4-6)"
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; all six Core-results rows confirmed (R1-R6 magnitudes, CIs, and p-values match PDF exactly); equations (1)-(3) and Axiom 1 formula verified term-by-term; outcomeClass corrected (removed off-registry 'expectations', kept 'household-finance')."
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13417", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2024-12-30; not CC-licensed; paywalled" }
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the simplicity representation model with its axioms, and the experimental design: enough to know what it found and how, without reading all 52 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13417).

## TL;DR

The paper introduces a preference for simplicity in choice under risk: people value having fewer outcomes in a lottery above and beyond what moments capture. In a preregistered online experiment (n = 582, Amazon Mechanical Turk, September to October 2022), participants provided certainty equivalents for lotteries with 2, 4, 8, and 16 outcomes, held similar in mean, variance, skewness, and range. Estimated CRRA risk aversion nearly triples from two to eight outcomes and nearly quadruples from two to sixteen outcomes. Dominance violations increase with complexity. An axiom characterizing simplicity (differences-in-differences complexity aversion) is satisfied by 84 to 90 percent of participants. None of the canonical theories tested (CPT, PT, salience, sparsity, rational inattention, cognitive noise, varying probability weighting) fully captures these patterns. The paper also axiomatizes and characterizes the simplicity representation and generalizes it to capture obfuscation, computation, and language effects.

## Core results

Magnitudes and significance are as reported; `\*` = 5%/10% level. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Measured CRRA risk aversion increases with lottery complexity**, holding moments fixed | Figure 1, p. 1030; §I.C, p. 1037 | CRRA alpha: 0.67 [0.38, 1.00] at 2 outcomes; 1.38 [1.05, 1.71] at 4; 3.21 [2.68, 3.84] at 8; 5.93 [5.06, 7.07] at 16 outcomes |
| R2 | **Dominance violations increase with lottery complexity** | Figure 2, p. 1040; §I.E | 3.9% at 2 outcomes; 4.4% at 4; 5.2% at 8; 6.4% at 16 outcomes; increase from 2 to 16 marginally significant (p = 0.08) |
| R3 | **Characterizing axiom satisfied by 84-90% of participants** (differences-in-differences complexity aversion) | Table I, p. 1039; §I.D | 50.4% satisfy axiom in 3/3 pairs (2 vs 4), 52.5% (2 vs 8), 59.4% (2 vs 16); 57-59% strictly satisfy for at least 1/3 pair; significantly above 50% random rate (p < 0.01) |
| R4 | **Complexity aversion is monotonic and economically large**: average c - c' spread exceeds twice the study's average relative risk premium for 2 vs 16 | §I.D, p. 1039 | \$0.005 for 2 vs 4 outcomes; \$0.012 for 2 vs 8; \$0.146 for 2 vs 16; difference between 2 vs 4 and 2 vs 8 significant at p < 0.01 |
| R5 | **Cognitive ability and complexity aversion are negatively correlated**: low-cognitive-ability individuals show much larger increases in measured risk aversion as complexity increases | Figure 3, p. 1042; §I.F | CRRA gap (low vs high cognitive ability): 0.86 at 2 outcomes (p < 0.1); 2.02 at 8 outcomes (p < 0.05); 3.83 at 16 outcomes (p < 0.05) |
| R6 | **Risk aversion and complexity aversion are largely separable**: once complexity costs are explicitly controlled, estimated CRRA alpha is stable across complexity levels | §I.G, p. 1043 | With C(n) controlled: alpha = 0.11 (SE 0.07) at 8 outcomes, 0.21 (SE 0.17) at 16; numerically similar and not statistically distinguishable; far below the 2.7-point gap when complexity is ignored |

**Overall (paper's conclusion).** People have preferences for simplicity distinct from other drivers of choice under risk. Observed risk aversion increases with lottery complexity, and dominance violations rise with complexity. Measured cognitive ability and complexity aversion are negatively correlated at higher complexity levels. None of the canonical behavioral-finance models tested (Tversky and Kahneman (1992) CPT; Kahneman and Tversky (1979) PT; Bordalo, Gennaioli, and Shleifer (2012) salience; Sims (2003) / Woodford (2012) rational inattention/cognitive noise; Gabaix (2014) sparsity) fully captures simplicity-seeking behavior. The simplicity representation is axiomatized and generalizes to nonrisk settings including computation and language complexity. Goodman and Puri (2023) and Fudenberg and Puri (2022a) are companion papers applying this framework to binary options and heterogeneous-agent settings respectively.

## Theory / model

The model has no formal model of asset markets; instead, it axiomatizes a preference over money lotteries. The underlying space is simple money lotteries $$\Delta\mathbb{R}$$. A preference $$\succeq$$ on $$\Delta\mathbb{R}$$ is assumed to be transitive, complete, and defined on simple lotteries (no compound lotteries in the space; Definition 1, p. 1034).

**Definition 1 (Simplicity Representation, p. 1034).** A preference $$\succeq$$ on money lotteries $$\Delta\mathbb{R}$$ is said to have a **simplicity representation** if, for any two lotteries $$p, q$$,

$$
p \succ q \iff \sum u(x)p(x) - C(\#p) > \sum u(x)q(x) - C(\#q), \tag{1}
$$

where $$u$$ is a continuous, strictly increasing, unbounded below Bernoulli utility, $$\#p$$ is the number of outcomes in lottery $$p$$, and $$C : \mathbb{N} \to \mathbb{R}$$ is a weakly increasing complexity cost function. This is an as-if representation and makes no claims about mechanism or welfare.

**Characterizing Axiom: Differences-in-Differences Complexity Aversion (Axiom 1, p. 1038).** The main axiom states that, when comparing a larger and smaller support lottery, the larger support lottery's appeal should increase by more when complexity differences are removed. Formally, consider lotteries $$p, q \in \Delta X$$, $$\#p \geq \#q$$, with certainty equivalents (CEs) $$\delta_p, \delta_q$$. For any $$\alpha \in (0, 1)$$ and any lottery $$r$$ whose support includes all outcomes in $$p, q, \delta_p$$, and $$\delta_q$$:

$$
\gamma\!\left(\tfrac{1}{2}p + \tfrac{1}{2}\delta_q\right) + (1-\gamma)r \succeq \gamma\!\left(\tfrac{1}{2}q + \tfrac{1}{2}\delta_p\right) + (1-\gamma)r. \tag{2}
$$

Mixing equalizes the complexity of both sides; the axiom says the more complex lottery $$p$$ benefits more from this equalization. It is a joint test of complexity aversion and separability.

**Theorem 1 (Characterization, p. 1048).** A preference $$\succeq$$ on $$\Delta\mathbb{R}$$ admits a Simplicity Representation if and only if it satisfies:
- Axiom 1 (Differences-in-differences complexity aversion)
- Axiom 2 (Monotonicity): $$x > y \Rightarrow \delta_x \succ \delta_y$$
- Axiom 3 (Same-Support Independence and Continuity): for lotteries with the same support, EU-type mixing axioms hold
- Axiom 4 (Singleton Continuity)
- Axiom 5 (Singleton Unboundedness)

The proof proceeds in three steps (p. 1048): (i) fix support $$Z$$ and apply Herstein and Milnor (1953) results to obtain EU restricted to same-support lotteries; (ii) use the same-support axiom to show the Bernoulli utility is support-independent ($$u_Z = u_{Z'}$$ for all $$Z, Z'$$); (iii) construct $$C$$ via an iterative algorithm using Axiom 1 to show complexity cost is well-defined independent of the specific lottery used.

**Uniqueness (Proposition 1, p. 1049).** The representation is unique up to an affine transformation: if $$(u, C)$$ and $$(u', C')$$ are two simplicity representations, then there exist $$\xi > 0, \beta \in \mathbb{R}$$ such that $$u' = \xi u + \beta$$ and $$C' = \xi C$$.

**Generalization (Definition 3, p. 1050).** The paper generalizes to cognitive tiers $$\mathbb{T} \subseteq \mathbb{R}$$: a **general simplicity representation** replaces $$\#p$$ with $$\text{Tier}(p)$$, capturing obfuscation, computation, and language effects. The representation is:

$$
p \succ q \iff \sum u(x)p(x) - C(\text{Tier}(p)) > \sum u(x)q(x) - C(\text{Tier}(q)). \tag{3}
$$

## Method

The experiment uses a preregistered design (AEA RCT Registry Trial ID 10136) run on Amazon Mechanical Turk in September to October 2022. There are two modules:

**Risk-aversion module (§I.C, p. 1037).** Participants provide certainty equivalents (CEs) for 32 lotteries using the standard multiple price list (MPL) procedure with enforced single switching (Holt and Laury 2002). Each MPL has six evenly spaced choices from 50 cents below the lottery's lowest payoff to the lottery's highest payoff. Participants are randomly assigned to this module or the axiom module. Lotteries have $$N \in \{2, 4, 8, 16\}$$ outcomes (8 lotteries per complexity level), generated to have similar means, variances, skewness, and ranges across complexity levels (Appendix A.1).

The CRRA utility is $$U(p) = \sum p(x) \frac{x^{1-\alpha}}{1-\alpha}$$, $$\alpha \geq 0$$. The econometric model follows Bruhin, Epper, and Fehr-Duda (2010): observed CE for individual $$i$$ on lottery $$l$$ is

$$
ce_{i,l} = \hat{ce}_l(\theta) + \epsilon_{i,l}, \quad \epsilon_{i,l} \sim N(0, \sigma_{i,l}), \quad \sigma_{i,l} = \xi_i |\text{range}(l)|,
$$

where each individual has their own error variance term $$\xi_i$$. Estimated using maximum likelihood via expectation-maximization (Appendix A.3, p. 1056). Confidence intervals via bootstrap with 1,000 iterations.

**Axiom module (§I.D, p. 1038).** Participants test Axiom 1 (differences-in-differences complexity aversion) via a five-step procedure: elicit CEs for two lotteries, construct a mixed lottery equating their complexity, elicit CEs for both mixed versions, and test whether $$c \geq c'$$. Three pairs each of 2 vs 4, 2 vs 8, and 2 vs 16 outcome lotteries.

**Cognitive ability.** Participants complete Raven's Advanced Progressive Matrices (APM), Set I, at end of survey. High vs low cognitive ability split at median Raven's score (10/12 in both modules). Paid \$0.25 per correct Raven's question.

**Data quality.** Workers in the US with at least 95% approval rating and at least 100 prior completed tasks; three comprehension checks; average payment \$9.33 for 23 minutes. Final sample: 582 participants (48% female, 54% below age 40, 60% college educated).

## Empirical specifications

The headline empirical results all come from the preregistered experimental design. There are no panel regressions with fixed effects; the primary inferential procedure is structural CRRA estimation by complexity level plus OLS checks on residuals of alternative models.

**R1: CRRA estimation by complexity level.** For each number of outcomes $$n \in \{2, 4, 8, 16\}$$, fit the CRRA model to the CEs of the $$n$$-outcome lotteries only, pooling individuals. Standard errors clustered by individual; bootstrap confidence intervals. Report $$\alpha$$ separately for each $$n$$ and test whether $$\alpha$$ is constant across $$n$$; the increase from 2 to 16 is the main finding.

**R2: Dominance violations.** Code dominance violation as 1 if the participant's stated CE for lottery $$l$$ is strictly less than the lowest possible outcome of $$l$$. Regress violation indicator on number of outcomes, clustering standard errors by individual. Separately, regress on log(number of outcomes). Marginal significance at $$p = 0.08$$ for the increase from 2 to 16.

**R3: Axiom satisfaction rate.** For each pair of 2 vs $$n$$-outcome lotteries, code whether the participant satisfies $$c \geq c'$$ (Axiom 1 test). Compute fraction of participants satisfying axiom in 0/3, 1/3, 2/3, 3/3 pairs. Test whether fraction satisfying axiom for $$\geq 2/3$$ pairs differs from 50% (random-clicking) and from 100% (expected utility), using a two-sided binomial test at $$p < 0.01$$.

**R5: Cognitive ability heterogeneity.** Split sample at median Raven's score. Re-estimate CRRA $$\alpha$$ separately by cognitive ability group for each complexity level. Test whether the difference between low and high groups is statistically significant at $$p < 0.1$$ and $$p < 0.05$$.

**R6: Separability test.** From the axiom module, recover dollar utility spreads $$c - c'$$ for pairs at $$n = 8$$ and $$n = 16$$ vs $$n = 2$$. Convert to complexity cost differences $$C(8) - C(2)$$ and $$C(16) - C(2)$$ (Appendix A.8). Use maximum likelihood to jointly estimate $$C(2)$$ and $$\alpha$$ controlling for complexity cost. If separable, estimated $$\alpha$$ should be stable across $$n$$; report $$\alpha$$ and $$C(2)$$ for $$n = 8$$ and $$n = 16$$.

**Alternative theory tests (§II, pp. 1043-1047).** For CPT, PT, salience, rational inattention, sparsity, and cognitive noise: fit the model to the risk-aversion module data, extract residuals, and regress residuals on number of outcomes. A positive and significant slope rejects the alternative. Also test whether the probability weighting parameter varies significantly by complexity (it does not). These tests are described fully in §II and appendices A.9-A.13.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Author-collected experimental data (AMT, preregistered, September to October 2022) | Certainty equivalents and axiom-module choices for 582 participants across 2/4/8/16-outcome lotteries | No page yet |

Sample: 582 US participants on Amazon Mechanical Turk, September to October 2022. Two modules: risk-aversion (32 lotteries, 8 per complexity level) and axiom module (12 lotteries, 3 per complexity level).

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13417) if you are: (i) axiomatizing or extending simplicity preferences to new settings (language, computation, obfuscation: §III.C, Definitions 2-3); (ii) applying simplicity theory to financial product design, portfolio choice, or incentive schemes (§IV); (iii) seeking the full suite of alternative-theory tests against CPT, PT, salience, sparsity, rational inattention, and cognitive noise (§II and Appendices A.9-A.13); or (iv) looking for the formal proofs and generalized representation theorems (Internet Appendix IA.A). The locators above point to the exact figures and tables.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(2), April 2025. This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or independently reproduced**. The paper is paywalled (Wiley VOR licence; not CC); only extracts reproduced here under fair use.

> Puri, Indira. "Simplicity and Risk." *The Journal of Finance* 80, no. 2 (April 2025): 1029-1080. DOI: 10.1111/jofi.13417. © 2024 the American Finance Association. Paywalled; extract-only.
