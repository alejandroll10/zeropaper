---
title: "Raising Capital from Investor Syndicates: Luo (2025)"
description: >-
  Distilled: An entrepreneur raising capital from a syndicate can use contract
  design to shape whether investors communicate truthfully or strategically
  persuade each other, explaining why flat contracts suit low-quality projects
  while hierarchical (differential-return) contracts suit high-quality ones.
  J. Finance 2025, CC BY-NC-ND 4.0. Six core results with source locators,
  the game-theoretic model, and the formal equilibrium characterizations.
sidebar:
  label: Luo 2025
  order: 1
tags: [paper-summary, corporate-finance, syndication, venture-capital, information-asymmetry,
       cheap-talk, contract-theory, peer-reviewed, unreplicated]
paper:
  authors: Dan Luo
  authorList:
    - { family: Luo, given: Dan, orcid: "0009-0006-1414-5739", affiliation: Chinese University of Hong Kong Business School }
  year: 2025
  venue: The Journal of Finance 80(3), June 2025, 1815–1869
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13453
  jel:
    codes: [G24, D82, G32]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Private Equity and Venture Capital", "Auction Theory and Applications", "Corporate Finance and Governance"]
  dataAccess: public
  outcome:
    - optimal syndicate structure (flat vs hierarchical)
    - entrepreneur expected profit
    - investor return differential in hierarchical contract
    - project acceptance probability
  outcomeClass: [firm-financing]
  license: "CC BY-NC-ND 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days 0, start 2025-04-10; corroborated by artifact p.1815 CC BY-NC-ND notice)"
  licenseShort: CC BY-NC-ND 4.0
  access: open
  machineAccess: "open-access (CC BY-NC-ND; Wiley online library, 2026-06-06)"
  redistribution: extract-only (CC BY-NC-ND prohibits derivatives and commercial reuse)
  resultsCount: 6
  citedByCount: 2
  methods:
    role: theory
    family: theory
    buildsFrom: [bayesian-persuasion, principal-agent]
  contributionType: [new-theory]
  mechanisms: [information-asymmetry, agency]
  scope:
    region: theoretical
    assetClass: private equity and syndicated loans (stylized)
  relatesTo:
    - { cite: "Segal (1999)", doi: '10.1162/003355399556016', relation: builds-on, note: "contracting-with-externalities literature on strategic risk in coordination games" }
    - { cite: "Kamenica and Gentzkow (2011)", doi: '10.1257/aer.101.6.2590', relation: builds-on, note: "Bayesian persuasion framework; principal commits to an information policy to influence receiver posteriors" }
    - { cite: "Brander, Amit, and Antweiler (2002)", doi: '10.1111/j.1430-9134.2002.00423.x', relation: tests, note: "second-opinion motivation for syndication; paper shows a distinct persuasion motive independent of information gathering" }
    - { cite: "Halac, Kremer, and Winter (2020)", doi: '10.1257/aer.20190234', relation: builds-on, note: "multiagent contracting with coordination and assurance; this paper contrasts by using communication rather than coordination failure" }
    - { cite: "Caillaud and Tirole (2007)", doi: '10.1257/aer.97.5.1877', relation: builds-on, note: "information cascades via planners information design; paper introduces persuasion cascades via strategic communication" }
  openQuestions:
    - "Whether the results extend to settings in which investors can observe each other's acceptance decisions sequentially rather than simultaneously, which could change the equilibrium communication and persuasion structure (p. 1831 fn. 16)."
    - "Whether the persuasion-based motivation for hierarchical contracts survives if information signals are binary (two-state signal structure removes the partial-pooling channel the paper requires, p. 1825)."
    - "Extensions to settings where the cost of strategic communication (reputation loss, legal liability) varies continuously with the content of misrepresentation, beyond the binary-cost model in Propositions 11-12 (pp. 1847-1848)."
  findings:
    - ref: R1
      outcome: optimal syndicate structure (flat vs hierarchical)
      metric: probability
      value: "flat no-enthusiast contract optimal when P0(alpha-1)/(1-P0) <= (1/2)(2-m)/(1-m)^2; hierarchical all-enthusiast contract optimal otherwise (Proposition 3, p. 1832)"
      direction: positive
      vsBenchmark: flat contract dominates for low ex ante quality; hierarchical dominates for high quality
    - ref: R2
      outcome: entrepreneur expected profit
      metric: level
      value: "U_all = P0(alpha-1) - (1-P0)(1 - m/2); U_no = P0[1-(1-m)^2](alpha-1); hierarchical preferred iff P0(alpha-1)/(1-P0) > (1/2)(2-m)/(1-m)^2 (Proposition 3, p. 1832)"
      direction: positive
      vsBenchmark: hierarchical contract raises profit by allowing persuasion to substitute for costly high promised returns to all investors
    - ref: R3
      outcome: investor return differential in hierarchical contract
      metric: basis-points
      value: "Return difference r1-r2 = m(1-P0)/P0 in the baseline two-investor case (Proposition 3 and §VI.C, p. 1847)"
      direction: positive
      vsBenchmark: "differential decreasing in prior probability P0 of good project; increasing in probability m that lead investor observes project type"
    - ref: R4
      outcome: investor return differential in hierarchical contract
      metric: coefficient
      value: "With communication cost eta >= (1/2)(1-P0)m(1-m), flat contracts always optimal; with eta < threshold, hierarchical contract has return difference (1-P0)m/P0 + 2*eta/(P0*(1-m)) (Proposition 11, p. 1847)"
      direction: positive
      vsBenchmark: communication cost increases the return differential needed to sustain hierarchical structure
    - ref: R5
      outcome: project acceptance probability
      metric: probability
      value: "As P0 or alpha increases, acceptance probability weakly increases and optimal structure switches from flat to hierarchical (Proposition 9, p. 1845); Berg (2018): ~80% acceptance for large bank loans; Gompers et al. (2020): 5 of 101 VC deals advance to due diligence (~5%)"
      direction: positive
      vsBenchmark: flat VC-style syndicates (low acceptance probability ~ 5%) vs hierarchical loan syndicates (high acceptance probability ~ 80%) consistent with model predictions
    - ref: R6
      outcome: optimal syndicate structure (flat vs hierarchical)
      metric: probability
      value: "With N investors, hierarchical all-enthusiast contract sets r_i = 1 + (1-P0)/P0 * (1-m)^(i-1); as N increases, flat no-enthusiast contract preferred for strictly more projects (Proposition 8, p. 1844)"
      direction: mixed
      vsBenchmark: "more investors makes no-enthusiast flat contracts relatively more attractive because surplus loss from unfunded uncertain projects shrinks faster under flat structure"
  resultType: new-finding
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-06
      role: extracted
      note: "Full text read (pp. 1815-1869, all propositions and proofs). Not human-verified. Not reproduced. No replication code for this theory paper."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-06
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; three fixes applied: (1) removed erroneous identification: structural field (paper is role: theory, field must be omitted), (2) corrected Proposition 1 second-case condition from r_1>=1/P_0 > r_2 to the PDF's r_1>=1/P_0 and r_2<1+(1-P_0)/P_0*(1-m_1), (3) corrected Gompers et al. statistic from '5 funded' / 'reach a term sheet' to '5 of 101 advance to due diligence' as stated in the PDF (p. 1845). All proposition formulas (Props 3, 8, 9, 10, 11, 12) and U^all/U^no expressions verified correct."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13453
      checked: 2026-06-06
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://creativecommons.org/licenses/by-nc-nd/4.0/, delay-in-days=0, start=2025-04-10"
  rightsSignalConflict: false
---

**What this is.** The paper's core propositions, the game-theoretic model, and
the formal equilibrium characterizations with exact equation locators: enough
to understand what it found and how, without reading all 55 pages. To replicate
or extend it, read the original at [https://doi.org/10.1111/jofi.13453](https://doi.org/10.1111/jofi.13453).

## TL;DR

An entrepreneur raising capital from multiple investors uses contract design to
govern how investors communicate. Each investor privately observes a signal
about the project and then sends cheap-talk messages to the others before
deciding to invest. The key insight is that the shape of the contract, flat
(identical returns) or hierarchical (differential returns), determines whether
investors have aligned interests and communicate truthfully, or divergent
interests and strategically persuade each other.

For projects with low ex ante quality, the entrepreneur prefers a flat contract:
investors truthfully share information, screening out bad projects, but never
invest when the project type is uncertain. For high-quality projects, the
entrepreneur prefers a hierarchical contract: the lead investor (promised more)
persuades others to invest even under uncertainty, raising the acceptance rate
at the cost of information rents. This provides a new motivation for investor
syndicates distinct from risk-sharing (the "second opinion" motivation of Brander, Amit, and Antweiler (2002)), or capital constraints:
allowing persuasion between investors. The paper also derives persuasion
cascades in the N-investor case and testable implications linking return
differentials to project quality and information softness.

## Core results

Locators point into the source PDF. All results are theoretical propositions.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Optimal contract is flat when ex ante quality is low, hierarchical when high**: threshold on $$P_0(\alpha-1)/(1-P_0)$$ determines the switch | Proposition 3, p. 1832 | Flat (no-enthusiast) when $$\frac{P_0(\alpha-1)}{1-P_0} \leq \frac{1}{2}\frac{2-m}{(1-m)^2}$$; hierarchical (all-enthusiast) otherwise |
| R2 | **Entrepreneur's expected profits**: hierarchical contract is preferred when surplus from uncertain projects is high enough to cover persuasion cost | Proposition 3, p. 1832 | $$U^{all} = P_0(\alpha-1) - (1-P_0)(1-m/2)$$; $$U^{no} = P_0[1-(1-m)^2](\alpha-1)$$ |
| R3 | **Return differential in hierarchical contract equals $$m(1-P_0)/P_0$$**: decreasing in prior probability of a good project and increasing in lead investor's signal precision | Proposition 3 and §VI.C, p. 1847 | Return difference $$r_1 - r_2 = m(1-P_0)/P_0$$; investor 1 gets $$r_1 = 1/P_0$$, investor 2 gets $$r_2 = 1 + (1-P_0)(1-m)/P_0$$ |
| R4 | **Communication costs raise the required return differential** and eventually make flat contracts always optimal | Proposition 11, p. 1847 | If communication cost $$\eta \geq \frac{1}{2}(1-P_0)m(1-m)$$, flat always optimal; else hierarchical return difference $$= (1-P_0)m/P_0 + 2\eta/(P_0(1-m))$$ |
| R5 | **Empirical prediction**: flat syndicates suit high-screening, low-acceptance settings (VC); hierarchical suits high-acceptance settings (syndicated loans) | Proposition 9 + §VI.A, p. 1845 | Acceptance probability ~80% for large bank loans (Berg (2018)); ~5% for VC deals (Gompers et al. (2020)); model predicts hierarchical for loans, flat for VC |
| R6 | **With N investors, persuasion cascades emerge**: returns are decreasing down the hierarchy; more investors makes no-enthusiast flat contracts optimal for more projects | Proposition 8, p. 1844 | Hierarchical: $$r_i = 1 + \frac{1-P_0}{P_0}(1-m)^{i-1}$$; $$U^{all} = P_0\left[\alpha - 1 - \frac{1-P_0}{P_0}\cdot\frac{1-(1-m)^N}{Nm}\right]$$ |

**Overall (paper's conclusion).** The model provides a unified theory of
investor syndicate formation and internal structure grounded in strategic
communication. Hierarchical contracts are optimal not because they bring in
more capital or information, but because they create conflicts of interest that
induce persuasion and raise acceptance rates on high-quality uncertain projects.
The communication channel explains why VC syndicates are flat (screening
orientation, low acceptance) and loan syndicates are hierarchical (persuasion
orientation, high acceptance), and predicts that return differentials decrease
with project quality and increase with information softness.

## Theory / model

The baseline model (Section II, p. 1821) has a penniless entrepreneur ("she")
who owns a project requiring total investment normalized to one. There are two
investors ("he"), each contributing one half. The project is either good
(generating return $$\alpha > 1$$) or bad (generating zero). The prior probability
of a good project is $$P_0$$.

Each investor $$i$$ privately observes the project type with probability $$m$$ and
nothing with probability $$1-m$$. Observation $$O_i \in \{G, B, \varnothing\}$$.
The entrepreneur publicly proposes a contract $$\{r_1, r_2\}$$ where $$r_i$$ is the
promised return to investor $$i$$ per unit of capital if the project is good.
After observing their signals, investors simultaneously send cheap-talk messages
and simultaneously make acceptance decisions.

**Investor $$i$$'s expected return from accepting** in state $$(O_i, O_j)$$ (p. 1826):

$$
\Pi_i(O_i, O_j) \triangleq \Pr[\text{project is good} \mid O_i, O_j] \cdot r_i - 1
$$

**Investor $$i$$'s expected utility from accepting** given strategies $$(\gamma_j, a_j)$$ (p. 1826):

$$
U_i(O_i, \theta_j; a_j, \gamma_i, \gamma_j) \triangleq \sum_{O_j \in \{G,\varnothing,B\}} \Pr[O_j \mid O_i, \theta_j; \gamma_j] \times \Pi_i(O_i, O_j) \times \mathbf{1}(f_i + f_j \cdot a_j(O_j, \gamma_i(O_i)) \geq 1)
$$

where $$\Pr[O_j \mid O_i, \theta_j; \gamma_j]$$ is investor $$i$$'s Bayes posterior about investor $$j$$'s observation after seeing $$j$$'s message $$\theta_j$$.

**Definition 1** (p. 1826): A contract is *flat* if all investors receive identical
returns ($$r_1 = r_2$$) and *hierarchical* if they receive different returns
($$r_1 > r_2$$).

**Equilibrium refinements** (p. 1827): The paper uses pure-strategy perfect
Bayesian equilibria (PBE) with three refinements: (SIB) an investor believes
the project is surely good (bad) upon observing $$G$$ ($$B$$), irrespective of
the other's message; (Weak Dominance) investors do not use weakly dominated
acceptance strategies; and (Pareto Dominance) investors do not play
Pareto-dominated equilibria.

**Key mechanism.** Under a hierarchical contract with $$r_1 > r_2$$, investor 1
prefers to invest even when the project type is uncertain $$(\varnothing, \varnothing)$$, but
investor 2 does not. Investor 1 therefore has an incentive to persuade investor
2 by pooling his messages for $$G$$ and $$\varnothing$$. Investor 2, receiving this pooled
message, perceives the project as more likely good and invests. The proof that
observation $$B$$ is always credibly revealed (Lemma 1, p. 1828) ensures that bad
projects are screened out in all equilibria.

## Method

This is a pure theory paper. The method is construction of a game-theoretic
model and characterization of its equilibria by backward induction and the
equilibrium refinements above. The solution builds on the `bayesian-persuasion`
framework (Kamenica and Gentzkow (2011)) and the `principal-agent` literature
on multiagent contracting (Segal (1999), Halac, Kremer, and Winter (2020)).
The persuasion-cascade mechanism differs from informational cascades driven by
planners' information design (Caillaud and Tirole (2007)), in that agents here
communicate strategically via cheap talk rather than Bayes-rational observational
learning.

**Step 1.** For any proposed contract, characterize the unique investment outcome
$$\hat{I}$$ (the set of observation states in which the project is implemented) via
Proposition 1 (p. 1829). The set $$\hat{I}$$ is:

$$
\hat{I} \triangleq \{(O_1, O_2) \mid [a_1^*(O_1, \gamma_2^*(O_2)), a_2^*(O_2, \gamma_1^*(O_1))]\cdot[f_1,f_2]^T \geq 1\}
$$

Under the refinements, Proposition 1 shows: if $$r_1 < 1/P_0$$, $$\hat{I} = \{(O_1,O_2) \mid O_1=G \text{ or } O_2=G\}$$ (screening);
if $$r_1 \geq 1/P_0$$ and $$r_2 < 1 + \frac{1-P_0}{P_0}(1-m_1)$$, $$\hat{I} = \{(O_1,O_2) \mid O_2=G\}$$;
if $$r_1 \geq 1/P_0$$ and $$r_2 \geq 1 + \frac{1-P_0}{P_0}(1-m_1)$$, $$\hat{I} = \{(O_1,O_2) \mid O_1 \neq B \text{ and } O_2 \neq B\}$$ (persuasion).

**Step 2.** Characterize which investors are *enthusiastic* (Definition 3, p. 1830):
investor $$i$$ is enthusiastic if in all equilibria he accepts whenever no investor
observes $$B$$. Proposition 2 (p. 1830) pins down $$\hat{N}$$, the number of
enthusiastic investors, as a function of promised returns.

**Step 3.** Show (Lemma 3, p. 1831) that the optimal contract must be either
all-enthusiast or no-enthusiast; partial-enthusiast contracts are dominated.

**Step 4.** Characterize the optimal contract (Proposition 3) by comparing the
entrepreneur's expected profits from each type. Define $$U^{all}$$ and $$U^{no}$$:

$$
U^{all} \triangleq P_0(\alpha-1) - (1-P_0)\!\left(1-\frac{m}{2}\right), \qquad U^{no} \triangleq P_0\!\left[1-(1-m)^2\right](\alpha-1)
$$

The entrepreneur prefers the hierarchical all-enthusiast contract
$$\left(\frac{1}{P_0},\ 1+\frac{1-P_0}{P_0}(1-m)\right)$$ when $$U^{all} \geq U^{no}$$, i.e., when

$$
\frac{P_0(\alpha-1)}{1-P_0} \geq \frac{1}{2}\cdot\frac{2-m}{(1-m)^2},
$$

and the flat no-enthusiast contract $$(1,1)$$ otherwise (Proposition 3, p. 1832).

## Empirical specifications

This is a theory paper with no estimation. The paper derives testable
implications in Section VI (pp. 1844-1848), connecting the model to empirical
regularities in syndicate structures.

**Application to syndicate structures (Proposition 9, p. 1845; R5 above).** The
model predicts that as project acceptance probability increases (higher $$P_0$$
or $$\alpha$$), optimal syndicate structure switches from flat to hierarchical.
According to Berg (2018), acceptance probability for large bank loans is near
80%; Gompers et al. (2020) find that only 5 of 101 VC deals considered advance
to due diligence, suggesting acceptance near 5%. The model predicts hierarchical for
bank loan syndicates and flat for VC syndicates, consistent with empirical
observation: most VC syndicates invest at the same valuation (flat), while loan
syndicates have lead arrangers earning higher fees (hierarchical).

**Underwriting and strategic communication (§VI.B, p. 1846).** The model
interprets underwriting fees as the mechanism implementing hierarchical contracts.
The prediction that hierarchical structures generate communication problems
between lead investors and others is consistent with legal cases: the IFE Fund
v. Goldman Sachs International (Petkovic (2008)) case documents Goldman's
suppression of unfavorable reports to maintain syndicate participation, consistent
with the equilibrium pooling behavior of the enthusiastic investor in the model.

**Testable implications for return differences (Propositions 10-12, pp. 1847-1848).**

Proposition 10: Return difference $$r_1 - r_2 = m(1-P_0)/P_0$$ is decreasing in
the prior probability $$P_0$$ of a good project and increasing in the lead
investor's signal probability $$m$$. This implies that high-risk projects with low
acceptance probability should have larger fee differentials between lead and
participant lenders.

Proposition 11: With communication cost $$\eta$$, return difference in hierarchical
contracts equals $$(1-P_0)m/P_0 + 2\eta/(P_0(1-m))$$, which is increasing in $$\eta$$.

Proposition 12: With information softness parameter $$\lambda$$ (fraction of $$G$$
observations that cannot be credibly revealed), return difference equals

$$
\frac{1-P_0}{P_0}\cdot\frac{m\lambda}{m\lambda + 1 - m},
$$

which is increasing in $$\lambda$$: softer information makes persuasion more
effective, requiring a smaller return premium to make the lead enthusiastic,
but investor 2 demands less in equilibrium because investor 1's persuasion is
more informative.

## Datasets used

This is a theory paper with no primary dataset. Empirical regularities cited
for motivation and discussion:

| Source | Role in paper | Wiki page |
|---|---|---|
| DealScan (Pitchbook) | Syndicated loan and VC deal statistics: "78% of loans in the DealScan universe were syndicated, 65% of VC deals" (§VI.A, p. 1845) | [DealScan](/wiki/licensed/dealscan/) / [PitchBook](/wiki/licensed/pitchbook/) (licensed) |
| Berg (2018) (large German bank) | Loan acceptance probability ~80% for loans above EUR 1 million | no page yet |
| Gompers et al. (2020) | VC deal acceptance statistics: 101 deals considered, 5 advanced to due diligence (implying ~5% acceptance) | no page yet |

No estimation, no regression, no data sample. All results are derived from the
theoretical model.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13453) if you are:
building a model of multiagent contracting with cheap talk;
studying the economic rationale for hierarchy in syndicates or inside firms;
extending the persuasion-cascade framework to more-than-two agents; or
testing the model's predictions on return differentials across syndicate types.
The proofs for all propositions are in Appendix A (pp. 1849-1869).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025, pp. 1815-1869.
This distillation was extracted by an LLM on 2026-06-06 and is **not
human-verified or independently reproduced**. The CC BY-NC-ND 4.0 licence
permits sharing with attribution but prohibits derivatives and commercial reuse;
the verbatim PDF is not hosted here.

> Luo, Dan. "Raising Capital from Investor Syndicates with Strategic Communication."
> *The Journal of Finance* 80, no. 3 (June 2025): 1815-1869.
> DOI: 10.1111/jofi.13453. © 2025 The Author(s).
> Published by Wiley on behalf of the American Finance Association.
> Licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
> This page is an **extract and summary** by the Institute for Automated Research;
> no modifications to the results or equations are represented as the author's words.
