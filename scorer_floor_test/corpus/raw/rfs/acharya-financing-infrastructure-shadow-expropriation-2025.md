---
title: "Financing Infrastructure in the Shadow of Expropriation: Acharya, Parlatore & Sundaresan (2025)"
description: >-
  Distilled: A theory of optimal infrastructure financing under double moral hazard
  (private-sector operator shirking and government expropriation of project returns).
  The second-best contract features government guarantees to financiers, government
  coinvestment, development rights, and tax subsidies, matching observed practice in
  public-private partnerships. Review of Financial Studies 2025, paywalled. Seven
  core results with source locators, the model equations, and the method.
sidebar:
  label: Acharya-Parlatore-Sundaresan 2025
  order: 1
tags: [paper-summary, infrastructure, public-private-partnerships, contract-theory,
       moral-hazard, corporate-finance, peer-reviewed, unreplicated]
paper:
  authors: Viral V. Acharya, Cecilia Parlatore, Suresh Sundaresan
  authorList:
    - { family: Acharya, given: Viral V., orcid: "0000-0002-8925-4239", affiliation: "Stern School of Business, New York University; NBER; CEPR; ECGI" }
    - { family: Parlatore, given: Cecilia, orcid: "0009-0008-1656-1263", affiliation: "Stern School of Business, New York University; NBER; CEPR" }
    - { family: Sundaresan, given: Suresh, orcid: "0000-0003-0227-0509", affiliation: "Graduate School of Business, Columbia University" }
  year: 2025
  venue: The Review of Financial Studies 38(5), 2025, 1368–1418
  venueShort: Rev. Fin. Stud. 2025
  doi: 10.1093/rfs/hhaf007
  jel:
    codes: [D82, G30, G32, G38, H20, H54]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-06
  topics: ["Public-Private Partnership Projects"]
  dataAccess: hand-collected
  introducesData: true
  outcome:
    - feasibility and scale of infrastructure projects
    - optimal government guarantee to financiers
    - optimal government coinvestment
    - optimal return promised to financiers
  outcomeClass: [firm-financing, firm-real-outcomes]
  license: >-
    Oxford Standard Publication Reuse Rights (confirmed via Crossref DOI metadata:
    content-version vor, URL https://academic.oup.com/pages/standard-publication-reuse-rights,
    delay-in-days 0, start 2025-01-24). Paywalled; not open access.
  licenseShort: paywalled
  access: paywalled
  machineAccess: "blocked-paywall (Oxford Academic / OUP, 2026-06-06)"
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 2

  methods:
    role: theory
    family: theory
    buildsFrom: [principal-agent, mechanism-design]

  contributionType: [new-theory, new-fact]

  mechanisms: [moral-hazard, agency, financial-constraint]

  scope:
    region: theoretical (with India case evidence)
    assetClass: infrastructure projects (public-private partnerships)

  relatesTo:
    - { cite: "Holmstrom and Tirole (1998)", doi: '10.1086/250001', relation: builds-on, note: "operator effort model: high/low effort determines project success probability, private benefit from shirking" }
    - { cite: "Jensen and Meckling (1976)", doi: '10.1016/0304-405x(76)90026-x', relation: builds-on, note: "private benefits from shirking motivate the operator's moral hazard problem" }
    - { cite: "Myers (1997)", relation: builds-on, note: "debt overhang idea applied to government expropriation reducing ex ante investment capacity" }
    - { cite: "Perotti (1995)", relation: cites, note: "credible privatization as a contracting commitment device; contrasted with authors' approach" }
    - { cite: "Martimort and Sand-Zantman (2006)", doi: '10.1111/j.1756-2171.2006.tb00056.x', relation: cites, note: "delegated management contract under asymmetric information; contrasted with authors' approach" }
    - { cite: "Repullo and Suarez (1998)", doi: '10.1093/rfs/11.1.163', relation: cites, note: "double moral hazard in venture capital contracting" }
    - { cite: "Mehta and Thomas (2022)", relation: cites, note: "NHAI litigation evidence consistent with double moral hazard in Indian highway contracting" }
    - { cite: "Lewis and Bajari (2014)", doi: '10.1093/restud/rdu002', relation: cites, note: "contractor moral hazard in Minnesota highway procurement" }
    - { cite: "Gardner and Henry (2023)", doi: '10.1257/jel.20221530', relation: cites, note: "government moral hazard limiting infrastructure investment globally" }

  openQuestions:
    - "Whether the model's insights extend to public goods beyond physical infrastructure, such as public health infrastructure and vaccine development, where similar double moral hazard problems arise (pp. 1403-1404)."
    - "How to build fiscal capacity and strengthen governance of institutions in developing economies to close infrastructure gaps, since third-party guarantees alone do not tackle double moral hazard (pp. 1402-1403)."
    - "The optimal design when both the operator and financiers can coinvest and the distribution of development rights interacts with the government's fiscal capacity constraints (pp. 1395-1397)."

  findings:
    - { ref: R1, outcome: feasibility and scale of infrastructure projects, metric: probability, value: "double moral hazard renders projects infeasible (extensive margin) or limits scale (intensive margin); feasibility threshold Gamma-bar = (1-p_h)*A_g + R-underbar where both A_o and A_g matter", direction: negative, vsBenchmark: "single moral hazard benchmarks (Prop. 1, Prop. 2): operator MH alone limits feasibility only; government MH alone limits neither" }
    - { ref: R2, outcome: optimal government guarantee to financiers, metric: coefficient, value: "K_g* = A_g + R-underbar - (R - A_o) > 0 when Gamma-bar <= (R-A_o) < Gamma_R; decreasing in (R-A_o) and increasing in A_g and C", direction: positive, vsBenchmark: "zero guarantee is insufficient when double moral hazard is present (Prop. 4)" }
    - { ref: R3, outcome: optimal government coinvestment, metric: level, value: "I_g* = 0 for (R-A_o) < Gamma_I; I_g* > 0 and increasing in (R-A_o) for Gamma_I <= (R-A_o) < Gamma*; I_g* = K-bar_0 for Gamma_R <= (R-A_o) < Gamma*", direction: positive, vsBenchmark: "pecking order: guarantees first, coinvestment second (Prop. 4)" }
    - { ref: R4, outcome: optimal return promised to financiers, metric: coefficient, value: "R_f = R-underbar for low (R-A_o); R_f strictly > R-underbar and increasing in (R-A_o) for Gamma_R <= (R-A_o) < Gamma* (Prop. 4c)", direction: positive, vsBenchmark: "R_f > minimum required return only when IRF binds simultaneously with ICG" }
    - { ref: R5, outcome: optimal government guarantee to financiers, metric: coefficient, value: "dK_g*/dC > 0; dR_f*/dC <= 0: higher government benefit from expropriating requires higher guarantees and lower coupon to financiers (Prop. 5)", direction: positive, vsBenchmark: "developing-economy governments face higher C, need higher guarantees but have less fiscal capacity" }
    - { ref: R6, outcome: feasibility and scale of infrastructure projects, metric: level, value: "dI*/dK-bar_0 >= dI*/dK-bar_1 >= 0; project scale increases with both K-bar_0 and K-bar_1; feasibility threshold independent of K-bar_0 and K-bar_1 (Prop. 6)", direction: positive, vsBenchmark: "fiscal resources expand scale but not feasibility; timing matters: K-bar_0 weakly dominates K-bar_1 (Prop. 7)" }
    - { ref: R7, outcome: feasibility and scale of infrastructure projects, metric: probability, value: "94% of Indian stressed thermal power plant failures (2007-2011) attributable to public or private moral hazard; 72% due to public moral hazard, 22% due to private moral hazard, 6% unclassified (Table 5, p. 1400)", direction: positive, vsBenchmark: "double moral hazard prevalence confirmed in developing-economy data" }

  resultType: new-finding

  replicationCode:
    status: none

  proposedVocab:
    - { axis: topic, term: public-private-partnerships, def: "Contractual arrangements between a government and private operators/financiers to develop and manage infrastructure projects, combining public and private capital.", aliases: [ppp, infrastructure-ppp] }
    - { axis: topic, term: infrastructure, def: "Physical public-use capital (roads, bridges, power plants, water systems) whose financing is the focus of the paper.", aliases: [infrastructure-finance] }
    - { axis: topic, term: contract-theory, def: "Theoretical study of optimal contract design under incentive constraints (moral hazard, limited commitment).", aliases: [contracting] }

  extraction:
    - { by: "paper-distiller (claude-sonnet-4-6)", date: 2026-06-06, role: extracted, note: "Full text read (pp. 1368-1418); seven results extracted. Not human-verified. Not reproduced. Paper is pure theory with descriptive evidence (India case study); no replication code generated." }
    - { by: "paper-verifier (claude-sonnet-4-6)", date: 2026-06-06, role: verified, note: "Locators and reported magnitudes re-checked against the source PDF; fixed JEL codes (added G30, G38, H20 missing from PDF p. 1368); corrected findings R6 and Core table R5: dI*/dK-bar_1 was stated < 0 but PDF Prop. 6b gives dI*/dK-bar_1 >= 0 (both fiscal resources weakly increase scale); all equations (ICO, ICG, IRF, IRG, ICG, NDK, NDR, scale formula, Eq. 1) verified term-by-term against PDF; India evidence magnitudes (Table 5: 72%/22%/6%; Table 4: 94%) confirmed; no em-dashes or colorful adjectives found." }

  licenceVerification:
    - { source: "Crossref REST API works/10.1093/rfs/hhaf007", checked: 2026-06-06, by: "paper-distiller (claude-sonnet-4-6)", found: "license[].content-version=vor, URL=https://academic.oup.com/pages/standard-publication-reuse-rights, delay-in-days=0, start=2025-01-24. Standard OUP reuse rights, not Creative Commons." }

  rightsSignalConflict: false
---

**What this is.** The core results, model equations, and propositions from this theory paper
on optimal infrastructure financing under double moral hazard: enough to understand what the
contract looks like and why, without reading all 50 pages. To replicate or extend it, read
the full source at the [original](https://doi.org/10.1093/rfs/hhaf007).

## TL;DR

The paper develops a principal-agent model of public-private partnerships (PPPs) in which
two moral hazard problems interact: a private-sector operator shirks if not given sufficient
incentives, and a government expropriates project cash flows if its incentive to do so
outweighs the cost. This double moral hazard simultaneously limits the feasibility (extensive
margin) and scale (intensive margin) of infrastructure projects, explaining persistent
infrastructure gaps globally. The second-best optimal financing contract combines
(a) government guarantees to financiers against project failure to discipline the government's
expropriation incentive, (b) direct government coinvestment when the project return is
sufficiently high, (c) development rights to private parties, and (d) tax subsidies.
These features match institutional arrangements common in practice (TIFIA, UK Infrastructure
Bank, Hong Kong MTR, etc.). India evidence shows 72% of stressed coal-power-plant failures
are attributable to public moral hazard.

The paper relates to three literature strands. On government expropriation and growth, Myers
(1997) establishes the debt overhang idea that motivated sovereign debt dynamics; here it applies
to private infrastructure. On infrastructure financing specifically, Perotti (1995) shows
credible privatization as a commitment device, and Martimort and Sand-Zantman (2006) characterize
optimal delegated management contracts; neither features double moral hazard. On double moral
hazard contracting under agency problems, Repullo and Suarez (1998) study venture capital, and
Bolton and Dewatripont (2004) is a standard text reference. India evidence is consistent with
Lewis and Bajari (2014) (contractor moral hazard in Minnesota highway procurement) and Gardner
and Henry (2023) (government moral hazard limiting infrastructure investment globally).

## Core results

Magnitudes and statements are as reported in propositions and tables; locators point to the
source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Double moral hazard limits feasibility and scale jointly**; neither moral hazard alone causes both problems | Props. 1-3, pp. 1382-1385; Table 1, p. 1385 | Three feasibility thresholds: (i) if $$(R-A_o) < \underline{\Gamma}$$, project unfunded absent government MH; (ii) if $$\underline{\Gamma} \leq (R-A_o) < \overline{\Gamma}$$, project unfunded due to government MH; (iii) otherwise funded but at limited scale when $$(R-A_o) < \Gamma^*$$ |
| R2 | **Optimal financing contract requires government guarantees** $$K_g > 0$$ when $$(R-A_o) \leq \Gamma^*$$; guarantees decrease in project return net of operator agency rent | Prop. 4, pp. 1386-1387; Figure 4, p. 1388 | $$K_g^* = A_g + \underline{R} - (R-A_o)$$ for $$\overline{\Gamma} \leq (R-A_o) < \Gamma_R$$; decreasing in $$(R-A_o)$$, positive throughout the region |
| R3 | **Pecking order: guarantees precede coinvestment**; government coinvestment $$I_g > 0$$ only when project return is sufficiently high relative to moral hazard severity | Prop. 4, pp. 1386-1387; Figure 4, p. 1388 | $$I_g^* = 0$$ for $$(R-A_o) < \Gamma_I$$; $$I_g^* > 0$$ and rising for $$\Gamma_I \leq (R-A_o) < \Gamma^*$$; maximal $$I_g^* = \bar{K}_0$$ at $$\Gamma_R$$ |
| R4 | **Higher government benefit from expropriating** ($$C$$) requires larger guarantees and a lower coupon; expropriation risk is worse in high-$$C$$ (developing-economy) settings | Prop. 5, p. 1389 | $$\partial K_g^*/\partial C > 0$$ and $$\partial R_f^*/\partial C \leq 0$$; developing economies need higher guarantees but their fiscal limits make these harder to provide |
| R5 | **Government fiscal resources increase scale but not feasibility**; resources available at the investment stage (date 0) weakly dominate those at the cash flow stage (date 1) | Props. 6-7, pp. 1389-1390 | $$\partial I^*/\partial \bar{K}_0 \geq \partial I^*/\partial \bar{K}_1 \geq 0$$; feasibility thresholds $$\overline{\Gamma}$$ and $$\underline{\Gamma}$$ independent of $$\bar{K}_0, \bar{K}_1$$ (Prop. 6a: $$\partial\overline{\Gamma}/\partial\bar{K}_0 = \partial\overline{\Gamma}/\partial\bar{K}_1 = 0$$) |
| R6 | **Development rights and tax subsidies** improve feasibility and scale; it is always optimal to set the tax-sharing rate $$\tau = 1$$ (fully share tax revenue with private sector) | Prop. 10-11, pp. 1395-1397 | Development rights $$D$$ and externalities $$X$$ raise $$\overline{\Gamma}$$ and $$I^*$$; distribution of rights to operator vs. financiers depends on which constraint is binding |
| R7 | **India evidence confirms double moral hazard**: 72% of stressed thermal power plant failures 2007-2011 due to public (government) moral hazard, 22% private, 6% unclassified | Table 5, p. 1400; Tables 2-3, p. 1398 | 34 stressed plants; 1,165 NHAI cases (40% of 2,912 highway disputes); government as petitioner in 123 of 139 arbitration-related cases |

**Overall (paper's conclusion).** The double moral hazard problem jointly limits the feasibility
and scale of privately financed infrastructure, explaining global infrastructure gaps. The
second-best optimal contract features government guarantees, coinvestment, development rights,
and tax subsidies in a pecking order determined by project return relative to agency rents.
These features are prevalent in practice. Third-party multilateral guarantees do not substitute
for government guarantees because they do not discipline the government's expropriation
incentive; building fiscal capacity and governance is more effective for closing infrastructure
gaps in developing economies.

## Theory / model

The model has three players: (a) the **government**, (b) a private **operator** who builds and
manages the project, and (c) private **financiers**. An infrastructure project has constant
returns to scale up to a maximum scale $$\bar{I}$$; total investment $$I = I_f + I_g$$ where
$$I_f$$ is from financiers and $$I_g$$ from the government. The per-unit payoff is $$R > 1$$ if
successful and zero otherwise. The model runs over four stages (Section 1, p. 1375, Figure 2
p. 1376): an **investment** stage (financial contract set), a **gestation** stage (operator
appointed, operational contract set), an **operating** stage (operator exerts effort), and a
**cash flow** stage (payoffs distributed).

**Operator's moral hazard.** Following Holmstrom and Tirole (1998), the operator exerts
high or low effort (p. 1376). High effort yields success probability $$p_h \in (0,1)$$, low effort
$$p_l < p_h$$. Let $$\Delta p \equiv p_h - p_l$$. Low effort gives the operator a private nonpecuniary
benefit $$BI$$ as in Jensen and Meckling (1976). If the project succeeds the operator receives $$R_o I$$;
if it fails the operator receives zero. The operator's incentive compatibility constraint (ICO)
is (p. 1379):

$$
p_h R_o I \geq p_l R_o I + BI \tag{ICO}
$$

Rearranging gives the familiar Holmstrom-Tirole (1998) condition: the operator requires an
agency rent of at least

$$
R_o \geq A_o \equiv \frac{B}{\Delta p}
$$

**Government's moral hazard.** The government can expropriate the operator's cash flows
by setting user fees below the contractual level (p. 1376). If the government expropriates, it
receives a net benefit $$CI$$ (with $$C > 0$$ in economies with weak institutions, $$C < 0$$
otherwise). The government will agree not to expropriate $$A_o$$ if its incentive compatibility
constraint (ICG) holds (p. 1380):

$$
p_h R_g - (1-p_h)K_g \geq p_l (R - R_f + C) - (1-p_l)K_g \tag{ICG}
$$

Rewriting:

$$
K_g + R_g \geq A_g \equiv \frac{p_l(A_o + C)}{\Delta p}
$$

where $$A_g$$ is the government's agency rent. Since $$C > -A_o$$ and $$p_l > 0$$, Assumption 1c
($$C > -B/\Delta p$$) ensures $$A_g > 0$$: double moral hazard is present whenever $$B > 0$$.

**Key structural insight (Section 2.2.3, p. 1383).** The government agency rent $$A_g$$ is
increasing in the operator agency rent $$A_o$$: the two moral hazards are intertwined. A higher
$$A_o$$ means the operator needs more cash flows in the success state, leaving less for the
government and sharpening the government's expropriation incentive.

**Payoff structure (Figure 3, p. 1378).** If the project succeeds (probability $$p$$):
financiers receive $$R_f I$$, operator $$R_o I$$, government $$R_g I \equiv (R - R_f - R_o) I$$.
If it fails (probability $$1-p$$): financiers receive guarantee $$K_g I$$, operator zero,
government $$-K_g I$$. The government has fiscal resources $$\bar{K}_0$$ at date 0 and $$\bar{K}_1$$
at date 1.

## Method

This is a pure theory paper; the method is constrained optimization (mechanism design).
The planner maximizes the net present value of the infrastructure project subject to incentive
compatibility constraints for the operator (ICO) and the government (ICG), individual
rationality constraints for the financiers (IRF) and the government (IRG), and no-default
(fiscal) constraints on government guarantees (NDK) and promised returns (NDR). The full
program is (Section 2.3, p. 1384):

$$
\max_{I_g \in [0,\bar{K}_0],\, I_f \geq 0,\, K_g \geq 0,\, R_f \geq \underline{R}} (p_h R - r)(I_g + I_f)
$$

subject to:

$$
(1-p_h)K_g + p_h R_f \geq r \frac{I_f}{I_f + I_g} \tag{IRF}
$$

$$
(1-p_h)K_g + p_h R_f + r \frac{I_g}{I_f + I_g} \leq p_h(R - A_o) \tag{IRG}
$$

$$
K_g + (R - A_o - R_f) \geq A_g \tag{ICG}
$$

$$
K_g(I_f + I_g) \leq \bar{K}_1 + \bar{K}_0 - I_g \tag{NDK}
$$

$$
R_f(I_f + I_g) \leq (R - A_o)(I_f + I_g) + \bar{K}_1 + \bar{K}_0 - I_g \tag{NDR}
$$

$$
I_g + I_f \leq \bar{I} \tag{MS}
$$

The total project scale is determined by the government guarantee via the NDK constraint:

$$
I = \min\!\left\{ \frac{\bar{K}_1 + \bar{K}_0 - I_g}{K_g},\; \bar{I} \right\}
$$

The paper proves eleven propositions by characterizing the optimal contract in three cases
depending on which constraints bind (Appendix A.2, pp. 1406-1408): (Case 1) ICG binds and
IRF is slack; (Case 2) ICG and IRF bind simultaneously; (Case 3) project is at maximal scale.
The full optimal contract formulas are given in equations (A1)-(A4) (pp. 1408-1409).

Extensions in Section 3 solve the program with: (i) costly state verification microfounding
$$\underline{R}$$ (Section 3.1); (ii) government's limited commitment to financiers with
default penalty $$\Phi$$ (Section 3.2, Prop. 8); (iii) random contract enforcement
(probability $$\delta$$ of enforcement, Section 3.3); (iv) private-party coinvestment by the
operator (Section 3.4, Prop. 9); and (v) development rights $$D$$ and government externalities
$$X$$ (Section 3.5, Props. 10-11). The extension with limited commitment and externalities
solves the program (Appendix B, p. 1410):

$$
\max_{I_g \geq 0,\, I_f \geq 0,\, K_g \geq 0,\, R_f \geq \underline{R},\, D_f \in [0,D]} (p_h(R+X+D) - r)(I_g + I_f)
$$

subject to modified IRF, IRG, ICG, NDK-LC, NDR-LC, and MS constraints, yielding a maximum
feasible project scale:

$$
\bar{I} = \frac{r\bar{K}_0 + (1-p_h)\min\!\{\Phi, \bar{K}_1\} + p_h\Phi}{(r - p_h D)} \tag{Eq. 1}
$$

## Empirical specifications

This paper has no econometric specifications. The empirical content is a structured case
study of two Indian infrastructure sectors serving as illustration of double moral hazard.

**Highway contracting in India (Section 4.1.1, pp. 1397-1399).** Data from Mehta and
Thomas (2022) on 2,912 highway contractual disputes 2007-2020 involving the National Highway
Authority of India (NHAI). Tables 2-3 (p. 1398) classify disputes by project lifecycle phase
and litigation driver. Key finding: 66% of disputes arise in the postaward/construction phase
(consistent with operating-stage moral hazard); NHAI is the petitioner in 123 of 139
arbitration-related cases and the defendant in 75 of 90 payment-related cases, consistent with
government moral hazard in payments.

**Stressed thermal power plants in India (Section 4.1.2, pp. 1398-1400).** Hand-collected
data on 34 stressed coal-fueled power plants initiated 2007-2011, sourced from monthly Broad
Status Reports of the Central Electricity Authority. Table 4 (p. 1399) shows 94% of failures
occur in the postaward/construction phase. Table 5 (p. 1400) classifies each plant's cause of
failure into private moral hazard (22%) and public moral hazard (72%), with 6% unclassified.
No regression or econometric test is performed; the classification is based on qualitative
case-by-case analysis (Appendix B1).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| NHAI litigation data (Mehta and Thomas 2022) | Illustrative evidence of double moral hazard in highway contracting | No page yet |
| Central Electricity Authority Broad Status Reports (hand-collected) | 34 stressed coal-fueled power plants; cause-of-failure classification | No page yet |

The paper introduces the 34-plant hand-collected dataset for the Indian power sector stress
episode (2007-2015). No quantitative empirical estimation is performed on either dataset.

## When to read the full paper

Read the [original](https://doi.org/10.1093/rfs/hhaf007) if you are: designing or evaluating
government guarantee programs for infrastructure; studying PPP contract design in settings
with weak institutions; extending the model to stochastic government expropriation or
multilateral guarantors; or seeking the formal proofs of Propositions 1-11 and the full
characterization of the optimal contract (Appendix A-B, pp. 1404-1411).

## Attribution and rights

Source: peer-reviewed, *The Review of Financial Studies* 38(5), 2025. Published by Oxford
University Press on behalf of the Society for Financial Studies. All rights reserved; paywalled.
This distillation was extracted by an LLM on 2026-06-06 and is **not human-verified or
independently reproduced**. Extract-only; no PDF hosted.

> Acharya, Viral V., Cecilia Parlatore, and Suresh Sundaresan.
> "Financing Infrastructure in the Shadow of Expropriation."
> *The Review of Financial Studies* 38, no. 5 (2025): 1368-1418.
> DOI: 10.1093/rfs/hhaf007. © The Author(s) 2025. Published by Oxford University Press.
