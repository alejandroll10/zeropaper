---
title: "Persuading Investors: Hu & Ma (2025)"
description: >-
  Distilled: Using machine learning to process 1,139 startup pitch videos across
  visual, vocal, and verbal dimensions, this paper finds that more positive pitch
  delivery (the Pitch Factor) raises accelerator funding probability by 3 pp
  (35.2% from baseline), yet funded startups with higher positivity underperform
  on every long-run measure, consistent with inaccurate investor beliefs (80%)
  and preference-based taste (20%) as the mechanism. J. Finance 2025, paywalled.
  Seven core results with source locators, datasets used, the model, and the method.
sidebar:
  label: Hu-Ma 2025
  order: 1
tags: [paper-summary, entrepreneurial-finance, venture-capital, persuasion, text-as-data,
       machine-learning, panel-regression, gender, behavioral-bias, peer-reviewed,
       unreplicated, data:crunchbase, data:pitchbook, data:wayback-machine]
paper:
  authors: Allen Hu, Song Ma
  authorList:
    - { family: Hu, given: Allen, orcid: "0009-0000-4852-0644", affiliation: Sauder School of Business, University of British Columbia }
    - { family: Ma, given: Song, orcid: "0000-0001-8582-4735", affiliation: Yale University }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2639–2688
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13471
  jel:
    codes: [G24, G41, D83]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics: ["Financial Markets and Investment Strategies"]
  dataAccess: hand-collected
  outcome:
    - probability of receiving accelerator funding
    - long-term startup performance (employment, VC raised, IPO/acquisition)
    - investor beliefs about startup success probability
  outcomeClass: [firm-financing, firm-real-outcomes, expectations]
  license: >-
    Paywalled (Crossref license: content-version vor, URL
    http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days 0,
    start 2025-08-14; not CC-licensed)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site, checked 2026-06-05)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 16

  methods:
    role: both
    contributes: pitch-factor-video-ml
    family: ml
    buildsFrom: [text-classification, panel-regression, factor-analysis-pca]
    identification: selection-on-observables
  contributionType: [new-method, new-data, new-fact]
  mechanisms: [behavioral-bias, information-asymmetry]
  introducesData: true
  scope:
    region: US
    assetClass: startup equity (accelerator investments)
    period: 2010-01..2019-12
    frequency: mixed
    dataType: [market, text, other]
    granularity: [firm, individual]
    n: "1,139 pitch videos; 102 MBA subjects in the experiment"

  findings:
    - ref: R1
      outcome: probability of receiving accelerator funding
      metric: pp-effect
      value: "0.030 marginal effect (SE 0.007); 3 pp increase per 1-SD rise in Pitch Factor, or 35.2% from baseline rate of 8.52%"
      direction: positive
      vsBenchmark: robust to controlling for textual content measures (Table III, cols 1-5)
    - ref: R2
      outcome: probability of receiving accelerator funding
      metric: r-squared
      value: "Full-video Pitch Factor Shapley-Owen R2 contribution 66.55% vs first-slice 16.78% and random-slice 16.66% (Table VI Panel A col 6)"
      direction: positive
      vsBenchmark: full-video Pitch Factor dominates thin-sliced measures; 4x larger R2 share
    - ref: R3
      outcome: probability of receiving accelerator funding
      metric: pp-effect
      value: "Women-only teams: 0.218 (SE 0.061); men-only teams: 0.016 (SE 0.009); difference significant at 10% (p=0.058, Table IX)"
      direction: positive
      vsBenchmark: women penalized 9x more than men per 1-SD below average Pitch Factor in single-gender teams; women irrelevant in mixed-gender teams
    - ref: R4
      outcome: long-term startup employment
      metric: coefficient
      value: "-0.071 (SE 0.018), full sample N=1,139 (Table VIII Panel A col 1)"
      direction: negative
      vsBenchmark: higher Pitch Factor predicts lower employment; confirms investor bias not rational updating
    - ref: R5
      outcome: long-term VC fundraising probability
      metric: coefficient
      value: "-0.009 (SE 0.003), full sample; -0.033 (SE 0.014), invested subsample N=270 (Table VIII)"
      direction: negative
      vsBenchmark: funded startups with higher positivity raise less follow-on VC
    - ref: R6
      outcome: investor beliefs about startup success probability
      metric: pp-effect
      value: "P(alive|invested) mu: 0.023 (SE 0.010); realized alive|invested: -0.099 (SE 0.055); miscalibration magnitude 0.122 (Table X)"
      direction: positive
      vsBenchmark: investors overestimate survival of high-Pitch-Factor startups by 12.2 pp vs realized outcomes
    - ref: R7
      outcome: probability of receiving accelerator funding
      metric: probability
      value: "Inaccurate-beliefs channel contributes 79.2%; taste/preference channel contributes 20.8% of total persuasion effect (Table XI col 4 + decomposition p. 2682; kappa=0.061, beliefs-mediated bias=0.232)"
      direction: positive
      vsBenchmark: inaccurate-beliefs channel 4x larger than taste/preference channel

  resultType: new-finding

  relatesTo:
    - { cite: "DellaVigna and Gentzkow (2010)", relation: builds-on, note: "framework distinguishing beliefs vs taste channels in persuasion; applied here to VC investment" }
    - { cite: "Bernstein, Korteweg, and Laws (2017)", relation: extends, note: "randomized experiment on hard information in VC; this paper adds nonverbal delivery as an independent channel" }
    - { cite: "Ewens and Townsend (2020)", relation: extends, note: "documents gender bias in VC; this paper shows pitch-delivery features mediate the bias" }
    - { cite: "Kaplan and Sorensen (2021)", relation: tests, note: "boards overweight interpersonal skills in CEO hiring; analogous finding in VC pitch delivery" }
    - { cite: "Gompers et al. (2020)", relation: cites, note: "passion is top-3 VC selection criterion; motivates focusing on positivity/warmth in pitches" }
    - { cite: "Huang et al. (2023)", relation: extends, note: "static first-impression photos from Shark Tank; this paper uses full dynamic video and controls pitch content" }

  openQuestions:
    - "Whether the same delivery-bias mechanism operates for professional (institutional) investors and settings beyond early-stage accelerators; the authors note the taste channel may be underestimated when subjects and investors do not interact in person (p. 2682)."
    - "How to connect inaccurate belief formation more closely to behavioral models such as categorical/coarse thinking (Fryer and Jackson (2008)) or failure to account for repeated information (DeMarzo, Vayanos, and Zwiebel (2003)), stated as promising directions (p. 2682)."
    - "Extending the video-based approach to capture additional behaviors such as gestures and speech fluency, and to multi-player sequential persuasion settings (p. 2683)."

  replicationCode:
    status: available

  proposedVocab:
    - { axis: topic, term: entrepreneurial-finance, def: "Financing of early-stage ventures: accelerator investment, angel/VC selection, and startup performance.", aliases: [startup-finance, venture-finance] }
    - { axis: topic, term: persuasion, def: "Nonverbal or noncontent features of communication that influence receiver decisions, distinct from the informational content of the message.", aliases: [nonverbal-communication, pitch-delivery] }

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: >-
        Full PDF read (pp. 2639-2688); seven results extracted from Tables III,
        VI, VIII, IX, X, XI. Not human-verified. Not reproduced.
        Replication code is referenced at end of paper but has not been run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: >-
        Locators and reported magnitudes re-checked against the source PDF;
        all seven Core-results rows confirmed correct (Tables III, VI, VIII,
        IX, X, XI); equations (1), (3)-(7) and Oster identified-set values
        verified term-by-term; one fix applied: body table R3 description
        changed from "14x" to "9x" to match the PDF's explicit characterization
        (p. 2643) and align with frontmatter findings and TL;DR.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13471
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-08-14; NOT a CC licence"

  rightsSignalConflict: false
---

**What this is.** The paper's core results, the method it contributes (a three-V video-processing pipeline with Pitch Factor construction), and the experiment identifying the mechanism: enough to know what it found and how, without reading all 50 pages. To replicate or extend it, read the full source at the [original](https://doi.org/10.1111/jofi.13471).

## TL;DR

The paper asks whether how entrepreneurs deliver a pitch, not just what they say, influences venture investment decisions. Using machine learning to process 1,139 startup pitch videos from five major US accelerators (2010-2019), the authors measure persuasion delivery across three dimensions (visual facial expressions, vocal tone, and verbal word choice) and combine them into a single *Pitch Factor*. A one-standard-deviation increase in Pitch Factor raises accelerator funding probability by 3 percentage points (35.2% from baseline). Yet funded startups with higher positivity systematically underperform on employment, follow-on VC, and IPO/acquisition outcomes. An experiment with 102 MBA students shows that approximately 80% of the persuasion effect runs through inaccurate belief formation (investors mistakenly think passionate pitchers are more likely to succeed) and 20% through taste-based preferences, broadly following the mechanisms framework of DellaVigna and Gentzkow (2010). Gender matters: investors penalize women 9 times more than men for being one standard deviation below average in pitch positivity, building on the gender-bias evidence of Ewens and Townsend (2020), but women are essentially overlooked when co-presenting with men.

## Core results

Magnitudes and significance are as reported; `\*\*\*`/`\*\*`/`\*` = 1%/5%/10%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Pitch Factor strongly predicts funding**: 1-SD increase raises funding probability by 3 pp (35.2% from 8.52% baseline) | Table III col 1, p. 2661 | Marginal effect 0.030 (SE 0.007)\*\*\*; stable across content controls in cols 2-5 |
| R2 | **Full-video Pitch Factor dominates thin-sliced and single-channel measures**: contributes 66.55% of R2 in Shapley-Owen decomposition, versus 16.78% (first-word slice) and 16.66% (random slice) | Table VI Panel A col 6, p. 2667 | Full-video Pitch Factor R2 contribution is 4x that of thin-sliced alternatives |
| R3 | **Gender asymmetry**: the penalty for being 1-SD below average in pitch positivity is 9x larger for women than for men in single-gender teams (coefficients 0.218 vs 0.016); women are statistically irrelevant in mixed-gender teams | Table IX cols 1-4, p. 2675 | Women coeff 0.218 (SE 0.061)\*\*\*; men 0.016 (SE 0.009)\*; pooled difference p=0.058; mixed-gender women coeff -0.002 (SE 0.025) |
| R4 | **High-positivity funded startups grow more slowly**: Pitch Factor negatively predicts employment among all startups | Table VIII Panel A col 1, p. 2673 | Coefficient -0.071 (SE 0.018)\*\*\* (inverse-hyperbolic-sine employment) |
| R5 | **Funded high-positivity startups raise less follow-on VC**: Pitch Factor negatively predicts VC fundraising | Table VIII Panels A-B col 2, p. 2673 | Panel A (full sample): -0.009 (SE 0.003)\*\*\*; Panel B (invested subsample N=270): -0.033 (SE 0.014)\*\* |
| R6 | **Investors form inaccurate beliefs**: in experiment, subjects overestimate survival of high-Pitch-Factor startups by 12.2 pp vs realized outcomes | Table X cols 1, 5, p. 2680 | Predicted mu coefficient 0.023\*\*; realized coefficient -0.099\*; miscalibration = 0.122 |
| R7 | **Beliefs vs taste decomposition**: inaccurate beliefs account for 79.2% and taste/preference for 20.8% of total persuasion effect | Table XI col 4, p. 2681; p. 2682 | Taste kappa=0.061; beliefs-mediated bias=0.232; total bias=0.293 |

**Overall (paper's conclusion).** Noncontent delivery features of persuasive communication have statistically and economically large effects on early-stage venture investment decisions. These features do not help investors make better decisions; the evidence from both archival data and the experiment suggests a bias, particularly leading investors to form inaccurate beliefs. Passionate pitches lower the investment bar in a way that reduces the portfolio's true average success probability. The result complements Bernstein, Korteweg, and Laws (2017), who show hard information matters in early-stage investment, by adding that soft delivery is an independent channel; it parallels findings in Kaplan and Sorensen (2021) that boards overweight interpersonal communication skills. Survey evidence in Gompers et al. (2020) that passion is a top VC selection criterion provides a direct motivation. The approach differs from Huang et al. (2023) by using full dynamic videos with three-V dimensions rather than static photos.

## Theory / model

The paper has no formal economic model for asset pricing, but it formalizes the mechanism via a threshold investment model with belief and taste channels (pp. 2677-2678, equations 5-6).

Investor $$j$$ makes a binary investment decision about startup $$i$$ using pitch delivery features $$\theta_i$$, beliefs about success probability $$\mu_{ij}$$, and confidence $$\sigma_{ij}$$. The investor's utility index from investing is (equation 5, p. 2677):

$$
U(\mu_{ij}, \sigma_{ij}, \theta_i) \equiv \gamma_\mu \mu_{ij} + \gamma_\sigma \sigma_{ij} + \kappa \theta_i \tag{5}
$$

and the investment rule is $$I_{ij} = \mathbf{1}[U_{ij} \geq \bar{U}]$$, with $$\gamma_\mu > 0$$ (investors prefer believing startups will succeed) and $$\gamma_\sigma < 0$$ for a risk-averse agent. The beliefs channel enters through $$\mu$$ and $$\sigma$$, which depend on hard information $$Q_i$$ and pitch delivery $$\theta_i$$:

$$
\mu_{ij} = \lambda_\mu Q_i + \psi_\mu \theta_i \tag{6a}
$$

$$
\sigma_{ij} = \lambda_\sigma Q_i + \psi_\sigma \theta_i \tag{6b}
$$

Under this framework $$\theta_i$$ enters the investment decision both via beliefs (coefficient $$\psi_\mu \gamma_\mu + \psi_\sigma \gamma_\sigma$$) and via a direct preference/taste effect (coefficient $$\kappa$$). The overall empirical coefficient $$\beta$$ in the investment regression is $$\kappa + \psi_\mu \gamma_\mu + \psi_\sigma \gamma_\sigma$$, which the experiment estimates separately by eliciting $$\mu_{ij}$$ and $$\sigma_{ij}$$ directly.

Beliefs are inaccurate when the sign of $$\psi_\mu$$ in equation (6a) is the opposite of the sign of the relation between $$\theta_i$$ and realized startup outcomes: investors who form higher expectations for high-$$\theta_i$$ startups are systematically wrong.

## Method

The core methodological contribution is a three-step video-processing pipeline that simultaneously extracts visual, vocal, and verbal (three-V) information from full pitch videos.

**Step 1: Information representation.** Videos are decomposed into an image stream (sampled at 10 frames per second using Face++ facial landmark detection) and an audio stream (48 kHz, analyzed by the `pyAudioAnalysis` Python package). Verbal content is extracted via Google Cloud Speech-to-Text, producing a time-stamped transcript (pp. 2651-2654).

**Step 2: Measure construction with ML algorithms.** Three sets of measures are computed per speaker per video frame or sentence segment (Table II, p. 2656; Appendix, p. 2683):

- *Visual*: Face++ categorizes facial emotions into six dimensions (happiness, sadness, anger, fear, disgust, neutral), aggregated to `Visual-Positive` and `Visual-Negative`.
- *Vocal*: `pyAudioAnalysis` extracts 34 audio features; LSTM models (speechemotionrecognition) give `Vocal-Positive`/`Vocal-Negative`; SVM models give `Vocal-Arousal` and `Vocal-Valence`.
- *Verbal*: The Loughran-McDonald Master Dictionary gives `Verbal-Positive`/`Verbal-Negative`; the Nicolas-Bai-Fiske NBF social-psychology dictionary gives `Verbal-Warmth` and `Verbal-Ability`.

**Step 3: Aggregation into Pitch Factor.** All per-frame and per-sentence measures are averaged to the video level, then subjected to principal-components factor analysis. The single factor with the highest eigenvalue is the *Pitch Factor* (p. 2658). Factor loadings confirm it captures overall positivity: `Vocal-Arousal` (+0.91), `Vocal-Valence` (+0.88), `Visual-Positive` (+0.08), `Verbal-Warmth` (+0.06), and negative loadings on all negativity measures. The ML algorithm is cross-validated against 115 Amazon Mechanical Turk raters; the algorithm matches human rankings with 89.5% consistency (p. 2659).

The method builds on `text-classification` (Loughran and McDonald (2011), Nicolas, Bai, and Fiske (2019)) and `panel-regression` for the econometric analysis, and proposes a new multi-modal video-processing technique (`pitch-factor-video-ml`) as its primary methodological contribution.

## Empirical specifications

**Baseline funding regression (Table III).** The headline specification is a logit regression with marginal effects (equation 1, p. 2659):

$$
I(\textit{Invested})_{ijt} = \alpha + \beta \cdot \textit{Pitch Factor}_i + \gamma \cdot \textit{Controls}_i + \delta_j + \varepsilon_{ijt} \tag{1}
$$

where $$I(\textit{Invested})_{ijt} = 1$$ if startup $$i$$ was funded by accelerator $$j$$ in year $$t$$, Pitch Factor is standardized (mean 0, SD 1), and Controls include three sets of textual content variables (idea novelty via BERT similarity to PitchBook and 10-K filings; dictionary-based content indicators for cash flow, employment, technology, etc.; LIWC linguistic features). Accelerator fixed effects $$\delta_j$$ account for cross-accelerator heterogeneity. Standard errors are clustered at the accelerator-year level. Sample: N=1,139 pitch videos (Table III, p. 2661).

**Long-run performance regression (Table VIII).** For performance outcomes the specification is OLS (or logit for binary outcomes), equation (4):

$$
\textit{Performance}_i = \alpha + \beta \cdot \textit{Pitch Factor}_i + \gamma \cdot \textit{Controls}_i + \delta_{\text{FE}} + \varepsilon_i \tag{4}
$$

Performance variables include inverse-hyperbolic-sine of employment, binary VC raised, inverse-hyperbolic-sine of VC amount raised, IPO/acquisition indicator, and website update frequency (Wayback Machine). Controls add firm age, squared firm age, industry FEs, and region FEs. SE clustered at the industry level.

**Gender heterogeneity (Table IX).** Same logit specification as equation (1), run separately for men-only (N=559) and women-only teams (N=310), then pooled with Pitch-Factor-times-gender interaction. For mixed-gender teams (N=270), male and female Pitch Factors are computed separately and entered jointly.

**Experiment investment regression (Table XI).** Logit on experimental investment decisions $$I_{ij}$$ (equation 7, p. 2681):

$$
I_{ij} = \underbrace{\kappa \cdot \theta_i}_{\text{Taste}} + \underbrace{\gamma_\mu \cdot \mu_{ij} + \gamma_\sigma \cdot \sigma_{ij}}_{\text{Beliefs}} + \delta_j + \varepsilon_{ij} \tag{7}
$$

where $$\mu_{ij}$$ and $$\sigma_{ij}$$ are directly elicited subject beliefs about P(alive|invested) and confidence. Subject fixed effects and startup/team and content controls included. SE two-way clustered at startup and subject levels. N=952 experimental investment rounds (102 subjects times 10 videos minus incomplete observations, p. 2679).

**Omitted-variable test (Table VII, Oster 2019).** To test whether omitted founder quality drives results, the authors apply the Oster (2019) delta/R-max test. For the baseline parameterization ($$R^2_{\max} = \min(2.2 R^2_c, 1)$$, $$\delta=1$$), the identified set is [0.021, 0.023], excluding zero. Even at $$\delta=2$$ and $$R^2_{\max}=1$$ the identified set is [0.006, 0.023], rejecting the null. The $$\delta$$ required to make $$\beta_{adj}=0$$ is 8.06 under the baseline parameterization.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| 1,139 startup pitch videos (YouTube, Vimeo, hand-collected) | Primary source of visual, vocal, verbal delivery measures via ML processing | no page yet |
| Crunchbase and PitchBook | Startup characteristics: founding year, industry, location, funding rounds and amounts, investor count | [PitchBook](/wiki/licensed/pitchbook/) (licensed) |
| LinkedIn (via API) | Founder backgrounds: education, work experience, prior entrepreneurship; used for startup/team quality controls | no page yet |
| Wayback Machine (Internet Archive) | Startup survival measure: website update frequency over three years post-application | [Wayback Machine](/wiki/datasets/wayback-machine/) |
| Amazon Mechanical Turk survey | Human validation of Pitch Factor ratings (N=115 raters, 89.5% algorithmic-human consistency) | no page yet |
| Yale SOM MBA experiment (N=102 subjects) | Elicited investor beliefs and investment decisions for mechanism decomposition | no page yet |

Sample: 1,139 accelerator applications to Y Combinator, MassChallenge, 500 Startups, Techstars, and AngelPad, spanning 2010-2019. Startup performance tracked as of July/August 2023.

## When to read the full paper

Use the [original](https://doi.org/10.1111/jofi.13471) if you are: (i) building a video-processing pipeline for economic research and need the detailed ML algorithm and hyperparameter choices (Internet Appendix II); (ii) studying gender bias in VC and need the full heterogeneity analysis across single-gender and mixed-gender teams; (iii) extending the belief-vs-taste decomposition framework to other persuasion settings; or (iv) replicating the sample selection tests (Table V) or the university-incubator robustness sample. The locators above point to the exact tables and figures.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5). This distillation was extracted by an LLM on 2026-06-05 and is **not human-verified or independently reproduced**. The article is paywalled (Wiley terms and conditions for VOR; not CC-licensed). Extract-only.

> Hu, Allen, and Song Ma. "Persuading Investors: A Video-Based Study."
> *The Journal of Finance* 80, no. 5 (October 2025): 2639-2688.
> DOI: 10.1111/jofi.13471. (c) 2025 the American Finance Association.
