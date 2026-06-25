---
title: "CEO Stress, Aging, and Death: Borgschulte, Guenzel, Liu & Malmendier (2025)"
description: >-
  Distilled: Managerial stress from industry distress shocks accelerates
  visible aging by roughly one year and raises CEO mortality hazard by ~15%,
  equivalent to 1.1 years of additional chronological age; antitakeover laws
  that reduce monitoring intensity imply a two-year longevity gain. J. Finance
  2025, CC BY 4.0. Eight core results with source locators, datasets used, the
  empirical strategy (DiD apparent-aging + stratified Cox hazard), and the
  identifying variation.
sidebar:
  label: Borgschulte-Guenzel-Liu-Malmendier 2025
  order: 1
tags: [paper-summary, corporate-governance, health-economics, executive-compensation,
       difference-in-differences, survival-analysis, machine-learning,
       open-access, cc-by, peer-reviewed, unreplicated,
       data:wrds, data:gettyimages-ceo-photos, data:ancestry-death-records,
       data:forbes-executive-compensation]
paper:
  authors: Mark Borgschulte, Marius Guenzel, Canyao Liu, Ulrike Malmendier
  authorList:
    - { family: Borgschulte, given: Mark, orcid: 0000-0003-1422-8201, affiliation: University of Illinois Urbana-Champaign }
    - { family: Guenzel, given: Marius, affiliation: University of Pennsylvania (Wharton School) }
    - { family: Liu, given: Canyao, orcid: 0000-0003-3291-247X, affiliation: Hudson River Trading }
    - { family: Malmendier, given: Ulrike, orcid: 0000-0002-2786-4365, affiliation: University of California, Berkeley }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3401–3442
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13497
  jel:
    codes: [G34, M12, I12]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics: ['Employment and Welfare Studies', 'Global Health Care Issues', 'Insurance and Financial Risk Management']
  dataAccess: hand-collected
  outcome:
    - CEO apparent-age gap (apparent minus chronological age)
    - CEO mortality hazard rate
    - CEO life expectancy
  outcomeClass: [labor-careers-health]
  license: 'CC BY 4.0 (confirmed via Crossref DOI metadata: content-version vor, URL http://creativecommons.org/licenses/by/4.0/, delay-in-days 0, start 2025-10-07)'
  licenseShort: CC BY 4.0
  access: open
  machineAccess: 'open-access (CC BY VOR confirmed via Crossref DOI metadata 2026-06-03)'
  redistribution: extract-only (CC BY 4.0 permits mirroring; PDF not hosted in this batch)
  resultsCount: 8
  citedByCount: 1
  methods:
    role: applies-method
    family: reduced-form-causal
    buildsFrom: [difference-in-differences, event-study, panel-regression, survival-analysis]
    identification: natural-experiment
  contributionType: [new-fact, new-data, measurement]
  mechanisms: [agency, occupational-stress]
  introducesData: true
  scope:
    region: US
    assetClass: US equities (Fortune 1000 / Forbes Executive Compensation survey firms)
    period: 1975-01..2017-10
    frequency: annual
    dataType: [market, accounting, administrative, other]
    granularity: [individual, firm]
    n: "3,002 CEO images (453 CEOs) for aging analysis; 1,900 CEOs, 58,034 CEO-year observations for mortality analysis"
  relatesTo:
    - { cite: 'Bertrand and Mullainathan (2003)', relation: builds-on, note: 'antitakeover-law variation as a proxy for CEO monitoring intensity' }
    - { cite: 'Gibbons and Murphy (1992)', relation: builds-on, note: 'CEO Mortality Data Set extends their Forbes Executive Compensation Surveys 1975-1991' }
    - { cite: 'Babina (2020)', relation: builds-on, note: 'industry distress definition: 30% decline in median 2-year forward stock return' }
    - { cite: 'Karpoff and Wittry (2018)', doi: '10.1111/jofi.12600', relation: tests, note: 'BC law exogeneity and identification robustness checks largely replicated here' }
    - { cite: 'Sullivan and Von Wachter (2009)', relation: cites, note: 'job displacement raises mortality hazard 10-15%, compared to industry distress here' }
    - { cite: 'Antipov et al. (2016)', relation: builds-on, note: 'Oxford/VGG deep CNN for apparent-age estimation used as ML tool' }
    - { cite: 'Cox (1972)', relation: builds-on, note: 'stratified proportional hazards model underlying the mortality analysis' }
  openQuestions:
    - 'Whether managers below the CEO tier suffer larger health costs given additional financial vulnerability, and how hierarchy level interacts with health consequences (p. 3436).'
    - 'Whether aspiring CEOs are over- or under-confident about the health costs and whether anticipated costs affect selection into CEO positions (p. 3406).'
    - 'Which specific job characteristics and decisions (e.g., layoffs, downsizings) are the most health-damaging within the CEO role (p. 3436).'
    - 'Whether heightened workplace stress adversely affects marriage, divorce, and parenting, which the paper leaves for future research (p. 3437).'
  findings:
    - { ref: R1, outcome: CEO apparent-age gap (apparent minus chronological age), metric: coefficient, value: "+0.806 years (SE 0.382, **)", direction: positive }
    - { ref: R2, outcome: CEO apparent-age gap (apparent minus chronological age), metric: coefficient, value: "0.634 (insig.) in 2007-2011; 1.049** to 1.183*** from 2012 onward", direction: mixed }
    - { ref: R3, outcome: CEO mortality hazard rate, metric: hazard-ratio, value: "exp(0.136) = 1.145; equivalent to 1.1 years older", direction: positive }
    - { ref: R4, outcome: CEO mortality hazard rate, metric: coefficient, value: "-0.198 to -0.234 (** to ***); average -0.217", direction: negative, vsBenchmark: "no BC law protection" }
    - { ref: R5, outcome: CEO mortality hazard rate, metric: coefficient, value: "-0.037 to -0.040 (***); average -0.039 per additional year of BC law", direction: negative, vsBenchmark: "no BC law protection" }
    - { ref: R6, outcome: CEO life expectancy, metric: hazard-ratio, value: "BC law mortality rate shift equivalent to CEO 2 years younger; pay effect insignificant and positive", direction: mixed, vsBenchmark: "unprotected CEO of same chronological age" }
    - { ref: R7, outcome: CEO mortality hazard rate, metric: probability, value: "67% of distressed CEOs die within 30 years of appointment; 1-year mortality 1.337% (nondistressed) vs 1.532% (distressed)", direction: negative }
    - { ref: R8, outcome: CEO life expectancy, metric: probability, value: "25% cumulative mortality: ~25 years (no BC) vs ~28-30 years (BC) after appointment", direction: positive, vsBenchmark: "same-era no-BC cohort" }
  resultType: new-finding
  replicationCode:
    status: none
  proposedVocab:
    - { axis: topic, term: health-economics, def: 'Economic analysis of health outcomes, mortality, aging, or the health effects of labor market conditions.', aliases: [health-and-labor-economics] }
    - { axis: topic, term: corporate-governance, def: 'Study of how ownership structure, board design, takeover markets, and managerial incentives shape firm and individual outcomes.', aliases: [governance] }
    - { axis: topic, term: executive-compensation, def: 'Incentive pay, compensation structure, and career concerns of C-suite executives.', aliases: [ceo-compensation, managerial-incentives] }
  extraction:
    - { by: paper-distiller (claude-sonnet-4-6), date: 2026-06-03, role: extracted, note: 'Full text read (pp. 3401-3442); eight results extracted from the CC-BY PDF. Not human-verified. Not reproduced.' }
    - { by: paper-verifier (claude-sonnet-4-6), date: 2026-06-03, role: verified, note: 'Locators and reported magnitudes re-checked against the source PDF; one fix applied: R7 nondistressed Kaplan-Meier milestone corrected from ~33 to ~32 years (PDF p. 3426 states "approximately 32 years"); all other rows, equations, and frontmatter facts confirmed.' }
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
        introducesData, data-scope) re-checked against the source PDF; all axes
        confirmed correct - natural-experiment identification supported by DiD
        and BC law quasi-experiments, new-fact/new-data/measurement contribution
        types all substantiated, occupational-stress and agency mechanisms both
        invoked, introducesData true for two hand-collected datasets, and
        data-scope fields match reported sample sizes exactly.
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
        against the source PDF; all eight entries confirmed correct - R1 0.806**
        matches Table III col.(1), R2 range 0.634/1.049-1.183 matches cols.(3)-(4),
        R3 average coefficient 0.136 and hazard ratio 1.145 match Table IV, R4/R5
        BC law ranges and averages match Table V cols.(1)-(8), R6/R8 KM milestones
        and R7 mortality rates confirmed from PDF pp.3426-3433; resultType
        new-finding correct given all relatesTo edges are builds-on/tests/cites with
        no headline contradicts or replicates; no fixes applied.
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13497
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: 'license[].content-version=vor, URL=http://creativecommons.org/licenses/by/4.0/, delay-in-days=0, start=2025-10-07'
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the two empirical strategies (DiD
apparent-aging and stratified Cox mortality hazard), and the datasets. Enough to
know what was found and how, without reading the full 42 pages. To replicate or
extend, read the original at [doi.org/10.1111/jofi.13497](https://doi.org/10.1111/jofi.13497).

## TL;DR

Using two quasi-experimental sources of variation in CEO job demands, the paper
documents that managerial stress causes accelerated visible aging and higher
mortality. First, in a difference-in-differences design applied to 3,002 facial
images of Fortune 1000 CEOs during the Great Recession, industry distress
exposure makes CEOs look roughly one year older (eventually 1.1 to 1.2 years
after 2012). Second, in a stratified Cox hazard model on 1,900 CEOs from Forbes
Executive Compensation Surveys (1975 to 1991), industry distress raises the
mortality hazard by about 15%, equivalent to 1.1 fewer years of chronological
life. Third, the staggered passage of antitakeover (Business Combination) laws
across U.S. states in the mid-1980s, which reduced monitoring intensity, is
associated with a 16 to 21% lower mortality hazard per year of BC law
exposure, implying roughly a two-year longevity gain for the average
protected CEO. The effects are of similar magnitude across both stress proxies
and consistent with a causal interpretation: neither compensation nor CEO tenure
fully accounts for the health costs, suggesting the market does not price them in.

## Core results

Magnitudes and significance as reported; `\*`/`\*\*`/`\*\*\*` = 10%/5%/1%.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Industry distress raises CEO apparent age (DiD, post-2006) | Table III col. (1), p. 3420 | +0.806 years (SE 0.382, `\*\*`) |
| R2 | Distress-induced apparent aging grows over time, reaching 1.0-1.2 years at post-2012 horizon | Table III cols. (3)-(4), p. 3420; Figure 4, p. 3418 | 0.634 (insig.) in 2007-2011; 1.049`\*\*` to 1.183`\*\*\*` from 2012 onward |
| R3 | Industry distress raises CEO mortality hazard by ~15% | Table IV (cols. 1-6), p. 3426 | Average hazard coefficient 0.136; hazard ratio exp(0.136) = 1.145; equivalent to 1.1 years older |
| R4 | BC antitakeover law exposure (binary) reduces CEO mortality hazard | Table V cols. (1)-(4), p. 3432 | Coefficients -0.198 to -0.234 (`\*\*` to `\*\*\*`); average -0.217 |
| R5 | Each additional year of BC law exposure reduces mortality hazard ~3.8% | Table V cols. (5)-(8), p. 3432 | Coefficients -0.037 to -0.040 (`\*\*\*`); average -0.039 |
| R6 | BC law protection equivalent to being ~2 years younger; no compensating pay differential found | p. 3433; Internet Appendix Table IA.XXIV | Hazard ratio shift corresponds to mortality rate of a CEO 2 years younger; pay effect insignificant and positive |
| R7 | Kaplan-Meier survival curves: ~67% of distressed CEOs die within 30 years of appointment vs. ~32 years for nondistressed | Figure 5, p. 3425 | Visually left-shifted survival curve; 1-year mortality at median CEO age pushed from 1.337% to 1.532% |
| R8 | BC law Kaplan-Meier: 1980s cohorts with BC exposure right-shifted vs. same-era no-BC cohorts; 1970s and 1980s no-BC curves nearly identical | Figure 6, p. 3431 | 25% cumulative mortality reached ~25 years (no BC) vs. ~28-30 years (BC) after appointment |

**Overall (paper's conclusion).** Heightened job demands in the form of
industry-wide distress and stricter corporate monitoring impose significant
personal health costs on CEOs: faster visible aging and shorter lives. The
effects are of similar magnitude whether identified by economic distress shocks
or by variation in governance intensity from antitakeover laws. For context,
Sullivan and Von Wachter (2009) estimate that job displacement raises the
mortality hazard by 10 to 15% and reduces life expectancy by 1 to 1.5 years
in a general male population; the industry-distress estimate here is of
comparable magnitude, but operates through an opposite channel (more, not
less, work effort). The absence of a compensating pay differential suggests
the market does not fully account for these costs, pointing to an
underappreciated private cost of CEO service.

## Theory / model

The paper has no formal structural model. The economic framework builds on the
notion that work-related stress arises when job demands exceed available coping
resources (Lazarus and Folkman (1984), p. 3403). In the CEO context, this is
operationalized through two contrasting shocks: industry-wide distress
(temporary demand increase) and antitakeover law protection (permanent demand
decrease). Both shocks affect the intensity of CEO job demands without directly
imposing financial hardship on the CEO, which allows identification to isolate
health effects from income effects that confound most stress-and-health
studies. Prior work by Bertrand and Mullainathan (2003) introduced
antitakeover-law variation as a proxy for CEO monitoring intensity; this paper
re-deploys that variation to study health outcomes rather than managerial
behavior.

The biological mechanism is that chronic stress triggers cortisol and other
hormonal responses, causing cellular damage that manifests as visible aging
(p. 3423). Apparent age is validated as a clinical biomarker for mortality
(Christensen et al. (2004), Christensen et al. (2009)): differences between
apparent and chronological age predict short-term and long-term mortality even
when physicians know the chronological age, and correlate with physical
functioning, cognitive performance, and leucocyte telomere length (p. 3413).
The paper's identification tests parallel pre-trends in both the DiD and the
Kaplan-Meier analysis (Figures 4 and 6) and rule out picture-management and
image-selection confounds through a battery of robustness checks.

**Industry distress identification.** An industry is distressed in year $$t$$ if
the median firm's forward-looking two-year stock return falls below $$-30\%$$
(Babina (2020)). The distress indicator for CEO $$j$$ equals 1 if the CEO's
firm was in a distressed industry in 2007, 2008, or both (the Great Recession
crisis years); it does not update after the CEO departs. Treatment status is
orthogonal to pre-crisis aging trends (Figure 4, p. 3418) and to image
sharpness (Internet Appendix Table IA.III).

**Antitakeover law identification.** Business Combination (BC) laws passed
staggered across 33 U.S. states between 1985 and 1997 (Figure 1, p. 3413).
Laws apply by state of incorporation, not state of headquarters, reducing
concern that local economic conditions drive the results. The constitutionality
of BC laws was established by a 1989 federal ruling, strengthening the
exogeneity argument (p. 3412).

## Method

**Part 1: Apparent-age estimation.** Apparent age is estimated from CEO facial
images using the deep CNN of Antipov et al. (2016), trained on more than
250,000 images and winner of the 2016 ChaLearn Looking At People competition
(p. 3414). The model is an ensemble of 11 sub-networks (bagging in the style of
Breiman (1996)) and outputs a $$100 \times 1$$ probability vector over ages 0 to 99;
the apparent-age point estimate is the expected value of this distribution.
The software is validated within the CEO context by comparing 250 random pairs
of CEO images to human assessments; agreement is ~70% overall and ~90% when the
software-estimated age gap is in the top tercile (p. 3414).

The outcome variable is the apparent-age gap:

$$
\text{Apparent Age Gap}_{i,j,t} = \widehat{\text{Apparent Age}}_{i,j,t} - \text{Chronological Age}_{j,t}
$$

where $$i$$ indexes an image, $$j$$ a CEO, and $$t$$ a time bin (p. 3418).

**Part 2: Cox proportional hazards model.** Mortality is estimated using
stratified Cox (1972) proportional hazards models. CEOs enter the risk set
when they take office and exit at death or the October 1, 2017 censoring date.
The baseline hazard $$\lambda_{0,j}(t)$$ is allowed to vary across Fama and French
(1997) 49 industries (p. 3424).

## Empirical specifications

**Apparent-aging DiD (R1, R2).** The pre-versus-post graphical test uses
time-bin indicators interacted with the distress indicator (equation 1, p. 3418):

$$
\text{Apparent Age Gap}_{i,j,t} = \beta_0 + \sum_{\substack{t \in T \\ t \neq 2005\text{-}06}} \beta_{1,t} \cdot \text{Industry Distress}_j \times \mathbb{1}_t + \boldsymbol{\beta}_2' \mathbf{X}_{i,j,t} + \delta_t + \theta_j + \varepsilon_{i,j,t} \tag{1}
$$

The main regression collapses post-crisis to a single indicator (equation 2,
p. 3419):

$$
\text{Apparent Age Gap}_{i,j,t} = \beta_0 + \beta_1 \cdot \text{Industry Distress}_j \times \mathbb{1}_{[t > 2006]} + \boldsymbol{\beta}_2' \mathbf{X}_{i,j,t} + \delta_t + \theta_j + \varepsilon_{i,j,t} \tag{2}
$$

where $$\mathbf{X}_{i,j,t}$$ includes image-level controls for smile, mood,
self-confidence, style, side face, logo, glasses, magazine quality, lighting,
natural pose, pre-2007 industry shock experience, and pre-2007 CEO tenure.
CEO fixed effects $$\theta_j$$ absorb time-invariant facial characteristics.
Standard errors are clustered at the three-digit SIC level. Observations are
weighted by image sharpness (Laplacian). Sample: 3,002 images of 453 CEOs.

**Mortality hazard, industry distress (R3, R7).** The Cox hazard model
stratified by FF49 industry is (equation 3, p. 3424):

$$
\ln \lambda(t \mid \text{Industry Distress}_{i,t}, \mathbf{X}_{i,t}) = \ln \lambda_{0,j}(t) + \beta \cdot \text{Industry Distress}_{i,t} + \boldsymbol{\delta}' \mathbf{X}_{i,t} \tag{3}
$$

where $$\text{Industry Distress}_{i,t}$$ equals 1 if CEO $$i$$ has experienced industry
distress (forward-looking 2-year median firm return $$< -30\%$$) in year $$t$$ or any
prior year. Controls include chronological age, linear or fixed time effects,
and state-of-headquarters location fixed effects. Sample: 1,900 CEOs, 58,034
CEO-year observations; standard errors clustered at 3-digit SIC.

**Mortality hazard, BC law indicator (R4, R6, R8).** The BC law binary
specification is (equation 4, p. 3429):

$$
\ln \lambda(t \mid BC_{i,t}, \mathbf{X}_{i,t}) = \ln \lambda_{0,j}(t) + \beta \cdot I(BC_{i,t}) + \boldsymbol{\delta}' \mathbf{X}_{i,t} \tag{4}
$$

**Mortality hazard, BC cumulative exposure (R5).** The cumulative-exposure
specification counts years of BC law coverage until year $$t$$ (equation 5,
p. 3430):

$$
\ln \lambda(t \mid BC_{i,t}, \mathbf{X}_{i,t}) = \ln \lambda_{0,j}(t) + \beta \cdot BC_{i,t} + \boldsymbol{\delta}' \mathbf{X}_{i,t} \tag{5}
$$

The BC analyses restrict to CEOs appointed before the BC laws were enacted
(1,605 CEOs) to address selection; standard errors are clustered at the
state-of-incorporation level. Both BC specifications add a first-generation
antitakeover law exposure control following Karpoff and Wittry (2018).

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| CEO Apparent Aging Data Set: 3,002 Getty Images / Google Images photos of 453 Fortune 1000 CEOs (2006 cohort), dated images, 2000-2016 | Outcome (apparent-age gap); identified by ML apparent-age CNN | No page yet |
| CEO Mortality Data Set: Forbes Executive Compensation Surveys 1975-1991 (Gibbons and Murphy (1992)); hand-collected birth and death dates from Ancestry.com for 2,361 of 2,720 CEOs at 1,501 firms; tenure from Execucomp and NYT "Business People" | Outcome (mortality/longevity); treatment (industry distress, BC law exposure) | [Forbes exec comp](/wiki/datasets/forbes-executive-compensation/) |
| CRSP (via WRDS): stock returns, PERMNO identifiers, historical SIC codes; used to construct annual industry-distress panel | Industry distress definition (median 2-year forward return < -30%) and sample restriction | [WRDS / CRSP](/wiki/licensed/wrds/) (licensed) |
| Compustat (via WRDS): assets, employees; Comphist / Compustat Snapshot for historical state of incorporation | Firm controls; historical state-of-incorporation for BC law assignment | [WRDS / Compustat](/wiki/licensed/wrds/) (licensed) |
| BC law passage dates, by state: Cheng, Nagar, and Rajan (2004); Cain, McKeon, and Solomon (2017); Karpoff and Wittry (2018) | Treatment variable (BC law indicator and cumulative exposure) | No page yet |
| Antipov et al. (2016) deep CNN apparent-age software (Oxford VGG architecture) | Apparent-age estimation from facial photos | No page yet |
| Human Mortality Database (2019) | Benchmark mortality rates for economic significance comparisons | No page yet |

Sample periods: apparent-aging analysis, 2000-2016 (images) / Fortune 1000 cohort 2006; mortality analysis, 1975-2017 (CEO-year panel, censoring October 1, 2017).

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13497) if you are:
extending the apparent-aging ML approach to other executive samples or
professional groups (see Section II and Internet Appendix Section II.A for the
CNN architecture and image-processing details); replicating the mortality
analysis (full robustness tables are in Internet Appendix Sections III-IV, with
22+ additional specifications); studying the BC law / antitakeover
identification in detail (Sections IV.D and Internet Appendix Tables
IA.XIX-IA.XXIII follow Karpoff and Wittry (2018) exhaustively); or examining
the pay-and-health compensating-differential calibration (Section IV.E and
Internet Appendix Section IV).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6), December 2025,
pp. 3401-3442. This distillation was extracted by an LLM on 2026-06-03 and is
**not human-verified or independently reproduced**. The CC BY 4.0 licence
permits mirroring; the verbatim PDF is not hosted in this batch.

> **Attribution (CC BY 4.0).** Borgschulte, Mark, Marius Guenzel, Canyao Liu,
> and Ulrike Malmendier. "CEO Stress, Aging, and Death."
> *The Journal of Finance* 80, no. 6 (December 2025): 3401–3442.
> DOI: 10.1111/jofi.13497. © 2025 The Author(s).
> Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
> This page is an **adaptation** by the Institute for Automated Research:
> core results extracted and re-expressed; **changes were made**.
