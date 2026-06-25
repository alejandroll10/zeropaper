---
title: "Conflicting Priorities: Donaldson, Gromb & Piacentino (2025)"
description: >-
  Distilled: A theory of why firms use secured debt, unsecured debt, and
  negative pledge covenants together, despite covenants being defeated by
  collateral priority. The model shows covenants and collateral are
  complementary tools: collateral implements efficient dilution that covenants
  alone cannot, while covenants commit the borrower not to use collateral when
  dilution is inefficient. The optimal debt structure is multilayered, consistent
  with observed covenant violations and waivers. J. Finance 2025, paywalled.
  Five core propositions with source locators, the three-date model, and the
  mechanism.
sidebar:
  label: Donaldson-Gromb-Piacentino 2025
  order: 1
tags: [paper-summary, corporate-finance, debt-structure, covenants, collateral,
       financial-contracting, peer-reviewed, unreplicated]
paper:
  authors: Jason Roderick Donaldson, Denis Gromb, Giorgia Piacentino
  authorList:
    - { family: Donaldson, given: Jason Roderick, affiliation: "USC and CEPR" }
    - { family: Gromb, given: Denis, orcid: "0000-0003-0792-0566", affiliation: "HEC Paris (deceased)" }
    - { family: Piacentino, given: Giorgia, affiliation: "USC, NBER, CEPR, and ECGI" }
  year: 2025
  venue: "The Journal of Finance 80(3), June 2025, 1739-1768"
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13445
  jel:
    codes: [G32, G33, G28]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Law, Economics, and Judicial Systems", "Public-Private Partnership Projects"]
  dataAccess: public
  outcome:
    - efficient investment in Project 1 (first-best policy)
    - optimal debt structure (face values of secured and unsecured debt, covenant fraction)
  outcomeClass: [firm-financing]
  license: >-
    Wiley VOR terms and conditions (confirmed via Crossref DOI metadata:
    content-version vor, URL http://onlinelibrary.wiley.com/termsAndConditions#vor,
    delay-in-days 0, start 2025-04-09); no CC licence found; paywalled.
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/Journal of Finance site, 2026-06-06)
  redistribution: extract-only
  resultsCount: 5
  citedByCount: 18
  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, real-options]
  contributionType: [new-theory]
  mechanisms: [agency, collateral, financial-constraint, moral-hazard]
  scope:
    region: theoretical
  relatesTo:
    - { cite: "Ayotte and Bolton (2011)", doi: '10.1093/rfs/hhr053', relation: extends, note: "extends their analysis of negative pledge covenants and priority rights to allow for efficient dilution and renegotiation" }
    - { cite: "Hart and Moore (1995)", relation: builds-on, note: "the spirit of using hard claims to constrain investment while retaining flexibility follows Hart and Moore (1995)" }
    - { cite: "Donaldson, Gromb, and Piacentino (2020a)", doi: '10.1016/j.jfineco.2019.05.005', relation: extends, note: "extends the collateral-overhang result of their earlier paper by allowing covenants as an additional instrument" }
    - { cite: "Rampini and Viswanathan (2013)", doi: '10.1016/j.jfineco.2013.03.002', relation: cites, note: "collateral and capital structure evidence cited in empirical discussion" }
    - { cite: "Bebchuk and Fried (1996)", doi: '10.2307/797243', relation: cites, note: "policy debate about strong priority of secured claims addressed by the model" }
  openQuestions:
    - "Whether a fuller analysis allowing renegotiation with subcoalitions of parties and multiple creditor types changes the main results (p. 1752, Section III.A)."
    - "Whether the prediction that covenant use decreases and collateral use increases with asset tangibility can be tested directly; the paper notes the predictions are consistent with indirect evidence but have not been directly tested (p. 1755-1756)."
    - "Whether the analysis extends cleanly to more than two quality levels without the simplifying assumption that the sign of projects' value and their cash flow/pledgeability are correlated (p. 1753-1754, Section III.B)."
  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1739-1768 plus appendices); five propositions extracted with PDF locators. Pure theory paper: no empirical data, no findings[] block. Not human-verified. Not reproduced." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; all five proposition locators and all ten equations (eqs. 1-10, pp. 1743-1750) verified term-by-term against the PDF -- no errors found." }
  licenceVerification:
    - { source: "Crossref REST API works/10.1111/jofi.13445", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-04-09; no CC licence; paywalled." }
  rightsSignalConflict: false
---

**What this is.** The paper's five main propositions, the three-date model
with its key equations, and the mechanism linking collateral, covenants, and
investment efficiency: enough to understand what it proved and how, without
reading all 30 pages. To replicate or extend it, read the full source at the
[original](https://doi.org/10.1111/jofi.13445).

## TL;DR

The paper develops a theory of debt structure in which collateral and negative
pledge covenants are complementary tools for managing the over/underinvestment
trade-off. A borrower faces two frictions: limited pledgeability (private
benefits cannot be pledged) and nonexclusive contracting (covenants can be
violated by taking on new secured debt that retains priority). Because
collateral trumps covenants, negative pledge covenants have no teeth on their
own: a new secured debt issue retains its priority even when it violates a
covenant. Yet covenants are useful: the threat of acceleration, though
generally not credible when all debt is covenant-protected, becomes credible
when only some debt is. The optimal debt structure is multilayered, combining
secured and unsecured debt with and without covenants, and it is always
first-best efficient in equilibrium. Covenants are violated and waived on the
equilibrium path, consistent with observed practice.

## Core results

Propositions are the primary units; locators point into the source PDF.

| # | Result | Locator | Key condition |
|---|---|---|---|
| R1 | Unsecured debt implements first-best | Prop. 1, p. 1747, eq. (5)-(6) | Private benefit of low-quality project $$Y_1^L \le Y_1^*$$, or total expected cash flows exceed funding needs; else overinvestment temptation prevents efficiency |
| R2 | Secured debt implements first-best | Prop. 2, p. 1748, eq. (7)-(8) | $$X_1^H \ge X_1^L$$: high-quality project has higher pledgeable cash flow; "mild" underinvestment problem |
| R3 | Covenants are irrelevant when all debt is covenant-protected | Prop. 3, p. 1749, eq. (9) | Acceleration threat is self-defeating: forcing liquidation subsidizes secured debt without deterring overinvestment; covenants have no bite unless $$\phi \le \phi^*$$ |
| R4 | Mix of covenant-protected and unprotected debt implements first-best | Prop. 4, p. 1750, eq. (10) | $$X_1^L \ge X_1^H$$: "severe" underinvestment problem; covenant fraction $$\phi$$ must be small enough that acceleration is credible only when Q=L |
| R5 | Equilibrium debt structure is first-best efficient | Prop. 5, p. 1751 | Always achievable; instrument choice (secured vs. covenant-protected unsecured) depends on severity of underinvestment problem |

**Overall (paper's conclusion).** Collateral and covenants implement
efficiency only in concert: covenants commit the borrower not to use
collateral when dilution is inefficient (bad dilution); collateral is needed
to break that commitment and engage in good dilution when covenants would
otherwise block efficient investment. Covenant violations and waivers are
on-path, not failures of contracting. The results speak to the policy debate
on debt priority: strong priority rules are useful because they let borrowers
dilute when, but only when, it is efficient to do so.

## Theory / model

The model has three dates $$t \in \{0, 1, 2\}$$ and a borrower B with two
sequential projects (Section I, pp. 1743-1746). Closest in spirit to this
paper is Ayotte and Bolton (2011), who also study negative pledge covenants
and property versus priority rights. The paper extends that analysis by
rationalizing covenant violations and waivers, and by showing covenants and
collateral are complementary rather than substitutes. The framework follows
Hart and Moore (1995) in using hard claims (debt) to constrain investment.
The collateral-overhang problem analyzed in Donaldson, Gromb, and Piacentino
(2020a) is the baseline: this paper adds covenants as an additional instrument
alongside collateral. Policy implications connect to the debate in Bebchuk
and Fried (1996) about the efficiency of strong priority for secured creditors.
Collateral and capital structure evidence from Rampini and Viswanathan (2013)
is cited in the empirical discussion (p. 1756).

**Projects.** Project 0 costs $$I_0$$ at Date 0 and succeeds with probability
$$p$$, yielding cash flow $$X_0 > 0$$ and private benefit $$Y_0 > 0$$; its value is
positive (eq. 1, p. 1743):

$$
p(X_0 + Y_0) > I_0. \tag{1}
$$

Project 1 costs $$I_1$$ at Date 1, succeeds with probability $$p$$, and yields
cash flow $$X_1^Q > 0$$ and private benefit $$Y_1^Q > 0$$ depending on quality
$$Q \in \{H, L\}$$ revealed at Date 1. Project 1 has positive value only if
$$Q = H$$ (eq. 2, p. 1744):

$$
p(X_1^H + Y_1^H) > I_1 > p(X_1^L + Y_1^L). \tag{2}
$$

**Frictions.** Two frictions generate a role for both collateral and covenants
(Section I.B, p. 1744):
1. *Limited pledgeability*: private benefits $$Y_t$$ cannot be pledged to
   creditors; only cash flows $$X_t$$ are pledgeable.
2. *Nonexclusive contracting*: existing creditors cannot prevent B from
   contracting with new creditors at Date 1.

**Instruments.** Three financing instruments exist (pp. 1744-1745):
1. *Secured debt*: face value $$F^s$$, collateral gives absolute priority over
   unsecured claims.
2. *Unsecured debt*: face value $$F^u$$, no collateral.
3. *Covenant-protected (unsecured) debt*: unsecured but grants the right to
   accelerate if B takes on new secured debt.

**Priority rules.** Secured debt has priority over unsecured; earlier secured
debt has priority over later secured debt; earlier unsecured (or accelerated)
debt has priority over later unsecured debt (p. 1745).

**Assumptions.** Under the efficient investment policy, expected cash flows
exceed funding needs (Assumption 1, eq. 3, p. 1746):

$$
pX_0 - I_0 + q(pX_1^H - I_1) \ge 0. \tag{3}
$$

Liquidation value suffices to repay secured debt needed to finance Project 1
(Assumption 2, eq. 4, p. 1746):

$$
p\!\left(X_0 + X_1^Q\right) > \frac{I_1}{p}. \tag{4}
$$

The first-best policy is to undertake both projects and invest in Project 1
if and only if $$Q = H$$ (Lemma 1, p. 1746). The paper derives conditions on
the debt structure at Date 0 under which this first-best is achieved as a
subgame perfect equilibrium.

**Key tension.** Unsecured debt allows dilution at Date 1 by new secured
creditors, which relaxes financial constraints (good dilution when $$Q = H$$)
but also enables overinvestment (bad dilution when $$Q = L$$). Secured debt
at Date 0 limits dilution capacity, preventing bad dilution but potentially
causing underinvestment. The central result is that a multilayered structure
combining instruments can implement the first-best whenever either instrument
alone cannot.

## Method

The paper uses a three-date contracting model solved by backward induction to
subgame perfect equilibrium, with competitive creditors who earn zero profit
in equilibrium (Section I.C, p. 1745). All contracts, including covenant
violations, are observable. B has full bargaining power in renegotiations
(p. 1746). The solution method is to:

1. Characterize the Date 1 subgame equilibrium given any Date 0 debt structure
   (which instruments, what face values, what covenant fraction $$\phi$$).
2. Derive necessary and sufficient conditions on the Date 0 debt structure for
   the first-best to obtain in every subgame.
3. Show that a date-0 structure satisfying those conditions always exists
   (Proposition 5).

The model builds on `principal-agent` contracting with nonexclusivity (no
exclusivity is enforceable via covenants because new secured debt retains
priority regardless of covenant violations). It uses `real-options` logic
in the sense that the right to dilute existing debt is like an option held by
the borrower; the debt structure determines when that option is valuable and
when it should be exercised.

**Covenant irrelevance result (Proposition 3).** If all unsecured debt at
Date 0 is covenant-protected (fraction $$\phi = 1$$), the acceleration threat is
generically not credible. The covenant-protected creditor's benefit from
acceleration (leapfrogging unprotected unsecured debt) is zero when $$\phi = 1$$
because there is no unprotected unsecured debt to leapfrog. The threshold
fraction at which acceleration becomes credible is (eq. 9, p. 1749):

$$
\phi^* := 1 - \frac{(1-p)I_1/p}{p(X_0 + X_1^L - I_1/p)} \in (0,1). \tag{9}
$$

Acceleration is credible only if $$\phi \le \phi^*$$. Above $$\phi^*$$, covenants
have no bite.

**Proposition 4 condition.** For covenants (at fraction $$\phi \le \phi^*$$) to
implement the first-best when secured debt cannot, a sufficient (and under
additional conditions necessary) condition is (eq. 10, p. 1750):

$$
X_1^L \ge X_1^H. \tag{10}
$$

This says negative-value projects ($$Q = L$$) have larger pledgeable cash flows
than positive-value projects ($$Q = H$$). Intuitively, the covenant-protected
creditor has more to gain from accelerating against a bad project (larger cash
flows to grab) than a good one, making the threat selective.

## Empirical specifications

This is a pure theory paper with no empirical estimation. Section IV
(pp. 1754-1756) describes empirical relevance and new predictions.

**Consistency with stylized facts.** The model is consistent with four
documented patterns (p. 1754-1755):
- Well-capitalized/highly rated firms rely heavily on unsecured debt (consistent
  with Proposition 1 and Rauh and Sufi (2010) and Benmelech, Kumar, and
  Rajan (2024)).
- Negative pledge covenants are common in roughly 44% of debt contracts
  (consistent with Proposition 4 and Billett, King, and Mauer (2007) and
  Ivashina and Vallee (2018)).
- Covenants are frequently violated and renegotiated or waived (consistent with
  Proposition 5; citations include Beneish and Press (1993, 1995) and
  Dichev and Skinner (2002)).
- Covenants in some debt decrease the yield on other debt by reducing default
  risk (consistent with Proposition 4; Bradley and Roberts (2015)).

**Untested predictions.** Propositions 1-5 imply four new predictions not yet
directly tested (Predictions 1-4, pp. 1755-1756):
- Firms more exposed to underinvestment (growth opportunities, high fixed costs,
  nonredeployable assets) use covenants more.
- Firms more exposed to overinvestment (distressed firms, declining industries)
  use collateral more.
- Collateral use increases and covenant use decreases with asset tangibility.
- Covenant use decreases with the costs associated with asset sales (less
  redeployable, harder to value, more firm-specific assets).

## Datasets used

This is a pure theory paper. No datasets are used in the analysis. The
empirical discussion in Section IV cites existing empirical studies (Billett,
King, and Mauer (2007); Rauh and Sufi (2010); Benmelech, Kumar, and Rajan
(2024); Beneish and Press (1993, 1995)) but does not reanalyze any data.

| Dataset | Role in paper | Wiki page |
|---|---|---|
| None (theory paper) | N/A | N/A |

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13445) if you are:
building models of debt structure with multiple creditors and priority rules;
analyzing why negative pledge covenants exist despite being defeated by
collateral priority; studying the design of optimal debt contracts when
pledgeability is limited and contracting is nonexclusive; or working on the
policy debate about the efficiency of strong priority for secured creditors.
The proofs in Appendix A (Lemmas A.1-A.18, pp. 1757-1763) are the formal
foundation for all five propositions.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(3), June 2025, pp. 1739-1768.
DOI: 10.1111/jofi.13445. Published under Wiley VOR terms; no CC licence.
This distillation was extracted by an LLM on 2026-06-06 and is **not
human-verified or independently reproduced**. Extract-only: the verbatim PDF
is not hosted here.

> Donaldson, Jason Roderick, Denis Gromb, and Giorgia Piacentino.
> "Conflicting Priorities: A Theory of Covenants and Collateral."
> *The Journal of Finance* 80, no. 3 (June 2025): 1739-1768.
> DOI: 10.1111/jofi.13445. © 2025 the American Finance Association.
