---
title: "Long-Horizon Exchange Rate Expectations: Kremens, Martin & Varela (2025)"
description: >-
  Distilled: Two-year-ahead survey forecasts of financial professionals
  successfully predict currency appreciation both in and out of sample, with
  estimated slope coefficients close to one. Three macro-finance variables
  (quanto-implied risk premium, real exchange rate, current account-to-GDP)
  explain most of the variation in survey expectations, with no residual
  "secret sauce." J. Finance 2025, paywalled. Eight core results with source
  locators, datasets used, the theoretical framework (SDF-based UIP identity),
  and the main empirical specifications.
sidebar:
  label: Kremens-Martin-Varela 2025
  order: 1
tags: [paper-summary, exchange-rates, currency-risk-premia, uip, survey-expectations,
       international-finance, panel-regression, time-series-forecasting,
       peer-reviewed, unreplicated, data:fred, data:consensus-economics,
       data:markit-quanto, data:imf-ifs, data:bis-rer]
paper:
  authors: Lukas Kremens, Ian W. R. Martin, Liliana Varela
  authorList:
    - { family: Kremens, given: Lukas, affiliation: University of Washington }
    - { family: Martin, given: Ian W. R., affiliation: London School of Economics }
    - { family: Varela, given: Liliana, affiliation: London School of Economics and CEPR }
  year: 2025
  venue: The Journal of Finance 80(6), December 2025, 3695–3724
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13504
  jel:
    codes: [F31, G15, G17]
    assignedBy: claude-opus-4-8
    date: 2026-06-05
  topics:
    - Exchange Rate Expectations and Forecasting
    - Currency Risk Premia and UIP
    - Survey Expectations in International Finance
  dataAccess: licensed-commercial
  outcome:
    - realized currency appreciation (24-month horizon)
    - realized currency excess returns (24-month horizon)
    - survey-based excess return expectations
  outcomeClass: [security-returns, expectations]
  license: >-
    Paywalled (Wiley Terms and Conditions; Crossref license[].content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0,
    start=2025-09-29; no open-access or CC licence found)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley/Journal of Finance site; confirmed via Crossref DOI metadata 2026-06-03)
  redistribution: extract-only
  resultsCount: 8
  citedByCount: 4

  methods:
    role: applies-method
    family: descriptive
    buildsFrom: [panel-regression, time-series-forecasting, fama-macbeth, quanto-implied-risk-premium]
    identification: descriptive
  contributionType: [new-fact, measurement]
  mechanisms: [risk-sharing, intermediary-constraint]

  scope:
    region: global
    assetClass: foreign exchange (six high-income currency pairs vs USD)
    period: 1994-12..2021-03
    frequency: monthly
    dataType: [market, survey]
    granularity: [security]
    n: "672 currency-months (post-GFC baseline); 1,340 currency-months (full sample, 1994-2021)"

  relatesTo:
    - { cite: 'Kremens and Martin (2019)', doi: '10.1257/aer.20180019', relation: extends, note: 'extends their quanto-implied risk premium (QRP) as an FX predictor; this paper adds survey expectations as a complementary and stronger univariate predictor' }
    - { cite: 'Meese and Rogoff (1983)', doi: '10.1016/0022-1996(83)90017-x', relation: contradicts, note: 'survey forecasts outperform the random walk benchmark out of sample at the two-year horizon' }
    - { cite: 'Hansen and Hodrick (1980)', doi: '10.1086/260910', relation: builds-on, note: 'early UIP regression framework and block-bootstrap standard error approach' }
    - { cite: 'Lustig, Roussanov and Verdelhan (2011)', doi: '10.1093/rfs/hhr068', relation: cites, note: 'Dollar and Carry factor loadings used as alternative FX predictors' }
    - { cite: 'Lustig, Roussanov and Verdelhan (2014)', doi: '10.1016/j.jfineco.2013.12.005', relation: cites, note: 'countercyclical currency risk premia and carry factor loadings as alternative predictors' }
    - { cite: 'Dahlquist and Penasse (2022)', doi: '10.1111/jofi.13190', relation: cites, note: 'real exchange rate as a missing risk premium predictor, used here as a competitor variable' }
    - { cite: 'Gabaix and Maggiori (2015)', doi: '10.1093/qje/qjv016', relation: cites, note: 'capital flows and intermediary constraints view of exchange rate determination' }
    - { cite: 'Nagel and Xu (2023)', doi: '10.1016/j.jfineco.2023.103713', relation: contradicts, note: 'their finding that survey forecasts are poor predictors below one year is confirmed; this paper documents the opposite at two-year horizons' }

  openQuestions:
    - "Why long-horizon forecasts outperform short-horizon forecasts in predicting short-run currency movements, despite being produced by the same institutions; the paper offers two speculative explanations (forecaster composition, different clienteles/objectives) but does not resolve the puzzle (p. 3721-3722)."
    - "Whether the findings extend to emerging market currencies, where IRD measurement is noisier; Table IA.V in the Internet Appendix shows suggestive evidence but the baseline excludes them (pp. 3705, fn. 10)."
    - "Whether VIX's additional forecasting power relative to survey expectations reflects a genuine omission in long-horizon models or simply captures short-term market stress not embedded in two-year forecasts (p. 3721)."

  findings:
    - { ref: R1, outcome: realized currency excess returns (24-month horizon), metric: r-squared, value: "Survey R-squared = 15.7%; QRP = 11.6%; RER = 10.4%; VIX = 8.5%; IRD = 1.7%", direction: positive, vsBenchmark: beats all alternative univariate predictors (QRP, RER, VIX, IRD) in post-GFC sample }
    - { ref: R2, outcome: realized currency appreciation (24-month horizon), metric: coefficient, value: "SXR coefficient = 0.726-0.837 (SE 0.212-0.251); R-squared = 16.9-19.2%", direction: positive, vsBenchmark: R-squared rises from 3.1% (IRD-only baseline) to 16.9-19.2% }
    - { ref: R3, outcome: realized currency appreciation (24-month horizon), metric: oos-r-squared, value: "Dollar-based OOS R-squared = 19.15%; dollar-neutral = 14.99%; bootstrapped p-value = 8.81% / 3.37%", direction: positive, vsBenchmark: beats random walk (Meese and Rogoff 1983) out of sample }
    - { ref: R4, outcome: survey-based excess return expectations, metric: r-squared, value: "R-squared = 53.6% (all variables, col 7); trivariate (QRP+RER+CA/GDP) = 52.8%", direction: positive }
    - { ref: R5, outcome: realized currency appreciation (24-month horizon), metric: coefficient, value: "Residual SXR coefficient = 0.177 (SE 0.232)", direction: none, vsBenchmark: residual unexplained by QRP, RER, CA/GDP has no predictive power }
    - { ref: R6, outcome: realized currency excess returns (24-month horizon), metric: coefficient, value: "SXR* coefficients: 1M = 0.088 (0.067), 3M = 0.093 (0.102), 12M = 0.237 (0.215), 24M = 0.726 (0.212); R-squared rises from 0.011 to 0.157", direction: mixed, vsBenchmark: near-zero at short horizons vs significant at 24-month horizon }
    - { ref: R7, outcome: realized currency excess returns (24-month horizon), metric: coefficient, value: "24M forecasts predicting 1M RXR*: coefficient = 1.548 (0.857), R-squared = 0.018; 1M forecasts predicting 24M RXR*: coefficient = 0.007 (0.009), R-squared = 0.019", direction: mixed, vsBenchmark: long-horizon forecasts predict short-run realizations; short-horizon forecasts do not predict long-run realizations }
    - { ref: R8, outcome: realized currency appreciation (24-month horizon), metric: coefficient, value: "3-to-24-month forward expectation coefficient = 0.188 (0.087); 3-month spot forecast coefficient = -0.062 (0.086)", direction: mixed, vsBenchmark: forward component of long-horizon forecast is predictive; spot short-horizon component is not }
  resultType: overturns

  replicationCode:
    status: available

  proposedVocab:
    - { axis: topic, term: exchange-rates, def: "Empirical and theoretical work on exchange rate determination, UIP, and currency return predictability.", aliases: [foreign-exchange, fx-rates] }
    - { axis: topic, term: survey-expectations, def: "Studies using survey-based forecasts of financial or economic variables to test rational expectations or forecast exchange rates, stock returns, or macro quantities.", aliases: [survey-forecasts, professional-forecasts] }
    - { axis: topic, term: currency-risk-premia, def: "Cross-sectional or time-series variation in expected returns on currency positions; includes carry trade, UIP deviations, and the forward premium puzzle.", aliases: [fx-risk-premium, forward-premium-puzzle, uip-deviations] }

  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-03
      role: extracted
      note: "Full text read (pp. 3695-3724, 30 pages); eight results extracted from the source PDF. Not human-verified. Not reproduced. Replication code is referenced in the paper (Supporting Information) but has not been run here."
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-03
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; R4 corrected (coefficients and R-squared 53.6% belong to col 7 not col 8; removed overclaim of 'from 0' baseline); R7 corrected (1M not 3M forecasts predicting 24M RXR*); all other rows, equations, and frontmatter confirmed against PDF."
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
        confirmed correct; removed pre-existing literal-false rightsSignalConflict
        (schema violation, key must be omitted when false).
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
        against the source PDF; all eight entries confirmed correct against their
        PDF tables (R1 Table II, R2 Table I Panel A, R3 Table III, R4 Table IV,
        R5 Table V, R6-R7 Table VIII Panel A, R8 Table IX); resultType overturns
        consistent with headline contradicts edge vs Meese-Rogoff; no fixes required.

  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13504
      checked: 2026-06-03
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-09-29; no CC license found; paper is paywalled"

---

**What this is.** The paper's core results, the SDF-based UIP identity it uses, and the main regression specifications: enough to know what it found and how, without reading all 30 pages. To replicate or extend it, read the full source at [doi:10.1111/jofi.13504](https://doi.org/10.1111/jofi.13504).

## TL;DR

Using monthly Consensus Economics surveys of financial professionals (six high-income currencies against the dollar, December 1994 to March 2019), the paper shows that two-year-ahead exchange rate expectations successfully predict realized currency appreciation both in and out of sample, with slope coefficients statistically close to one and R-squared values around 16-19%. Survey forecasts beat the random walk benchmark of Meese and Rogoff (1983) out of sample, and are the strongest univariate predictor, outperforming the quanto-implied risk premium (QRP) of Kremens and Martin (2019), the real exchange rate predictor emphasized by Dahlquist and Penasse (2022), VIX, and capital flow proxies including the current account variable linked to Gabaix and Maggiori (2015). Three macro-finance variables (QRP, RER, current account-to-GDP) together explain most of the cross-currency and time-series variation in survey expectations, with no residual "secret sauce" from forecasters beyond these observables. The paper also confirms the finding of Nagel and Xu (2023) that short-horizon (one- and three-month) survey forecasts have near-zero predictive power, but documents that long-horizon forecasts predict short-run realizations while short-horizon forecasts do not. The factor loadings on the Dollar and Carry factors of Lustig, Roussanov and Verdelhan (2011, 2014) are included as alternative predictor variables but explain substantially less variation than survey expectations.

## Core results

Magnitudes and significance are as reported; `**`/`***` = 5%/1%. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | **Survey expectations are the best univariate predictor** of 24-month realized currency excess returns, with R-squared exceeding all competing variables in the post-GFC sample | Table II, p. 3708 | Survey R-squared = 15.7%; runner-up QRP = 11.6%; RER = 10.4%; VIX = 8.5%; beta-HML = 7.2%; IRD = 1.7%; beta-dollar = 0.9%; CA/GDP = 0.0% |
| R2 | **Survey coefficients are close to one and statistically significant** in panel regressions of realized currency appreciation on survey excess return expectations, controlling for interest rate differentials | Table I Panel A cols (2)-(3), p. 3704 | SXR coefficient = 0.726-0.837 (standard errors 0.212-0.251); R-squared rises from 3.1% (IRD only) to 16.9-19.2% |
| R3 | **Survey forecasts beat the random walk out of sample** at the 24-month horizon, both dollar-based and dollar-neutral, with bootstrapped p-values below 5% | Table III cols (1)-(2), p. 3709 | Dollar-based R-squared-OOS = 19.15%; dollar-neutral = 14.99%; bootstrapped p-value = 8.81% / 3.37% respectively |
| R4 | **QRP, RER, and CA-to-GDP together explain over half the variation in survey expectations** in the post-GFC sample; the full multivariate specification raises R-squared to 53.6% | Table IV col (7), p. 3711 | R-squared = 53.6% (col 7, all variables); trivariate (QRP+RER+CA/GDP only, col 8) R-squared = 52.8%; QRP coefficient = 3.056\*\*\* (0.239), RER = -1.763\*\* (0.678), CA/GDP = -1.274\*\* (0.386) in col (7) |
| R5 | **No "secret sauce"**: the residual component of survey expectations not explained by QRP, RER, CA/GDP has no predictive power for realized returns | Table V col (3), p. 3713 | Coefficient on epsilon(SXR) = 0.177 (SE 0.232), statistically indistinguishable from zero; fitted value coefficient = 1.414 (0.832) |
| R6 | **Short-horizon survey forecasts (1- and 3-month) have near-zero predictive power** for short-run realized returns; the pattern reverses at 12- and 24-month horizons | Table VIII Panel A cols (1)-(4), p. 3718 | SXR\* coefficients at 1M = 0.088 (0.067), 3M = 0.093 (0.102), 12M = 0.237 (0.215), 24M = 0.726 (0.212); R-squared rises from 0.011 to 0.157 |
| R7 | **Long-horizon forecasts predict short-run realizations, but short-horizon forecasts do not predict long-run realizations** | Table VIII Panel A cols (5)-(10), p. 3718 | 24M forecasts predicting 1M RXR\*: coefficient = 1.548 (0.857), R-squared = 0.018; 1M forecasts predicting 24M RXR\*: coefficient = 0.007 (0.009), R-squared = 0.019 |
| R8 | **Forward expectations (3-to-24 month) predict short-run realizations**; spot short-horizon forecasts do not | Table IX col (5), p. 3719 | Coefficient on 3-to-24-month forward expectation predicting 3-month RCA = 0.188 (0.087), significant; coefficient on 3-month spot forecast = -0.062 (0.086), near zero |

**Overall (paper's conclusion).** Long-horizon survey expectations of financial professionals are broadly rational at the two-year horizon: their slope coefficient is close to one and they outperform the random walk. Three macro-finance variables (QRP, RER, CA/GDP) explain most of their variation, consistent with both risk-based and intermediary-constraints views of exchange rate determination. There is no residual forecaster information ("secret sauce") beyond these observables. The finding that long-horizon models outperform short-horizon models at forecasting short-run outcomes presents a puzzle the paper leaves open.

## Theory / model

The paper has no structural model. It grounds its empirical analysis in the standard no-arbitrage SDF identity and uses it to motivate the predictor variables. The fundamental asset pricing equation for any h-period gross dollar return $$R_{t+h}$$ is (p. 3700, eq. 1-2):

$$
\mathbb{E}_t(M_{t+h} R_{t+h}) = 1 \tag{1}
$$

$$
\mathbb{E}_t R_{t+h} - R^{\$}_{f,t,h} = R^{\$}_{f,t,h} \, \text{cov}_t(-M_{t+h}, R_{t+h}) \tag{2}
$$

where $$M_{t+h}$$ is the h-period SDF and $$R^{\$}_{f,t,h}$$ is the U.S. riskless rate. For a currency trade (convert USD to currency $$i$$, invest at the foreign riskless rate $$R^i_{f,t,h}$$, convert back), the return is $$R_{t+h} = R^i_{f,t,h} e_{i,t+h}/e_{i,t}$$ where $$e_{i,t}$$ is the nominal exchange rate. Substituting into equation (2) gives the UIP identity (p. 3700, eq. 3):

$$
\mathbb{E}_t \frac{e_{i,t+h}}{e_{i,t}} - 1 = \underbrace{\frac{R^{\$}_{f,t,h}}{R^i_{f,t,h}} - 1}_{\text{UIP}} + \underbrace{R^{\$}_{f,t,h} \, \text{cov}_t\!\left(-M_{t+h}, \frac{e_{i,t+h}}{e_{i,t}}\right)}_{\text{residual / risk premium}} \tag{3}
$$

The residual in (3) is the currency risk premium. When the marginal investor has log utility and holds the S&P 500 (so $$M_{t+h} = 1/R_{t+h}$$), the residual vanishes and expected appreciation equals the risk-neutral covariance term QRP (eq. 13, p. 3706):

$$
\mathbb{E}_t \frac{e_{i,t+h}}{e_{i,t}} - \frac{R^{\$}_{f,t,h}}{R^i_{f,t,h}} = \frac{1}{R^{\$}_{f,t,h}} \, \text{cov}^{\mathbb{Q}}_t\!\!\left(\frac{e_{i,t+h}}{e_{i,t}}, R_{t+h}\right) \tag{13}
$$

This motivates QRP as an observable proxy for the currency risk premium (and for survey expectations under rational expectations). RER and CA/GDP enter as additional predictors through their empirical association with either risk factors or intermediary balance-sheet constraints.

**Key definitions.** The paper defines the interest rate differential (IRD), realized currency appreciation (RCA), and survey-based currency appreciation (SCA) at horizon h as (pp. 3700-3701, eqs. 4-7):

$$
\text{IRD}_{i,t,h} = \frac{R^{\$}_{f,t,h}}{R^i_{f,t,h}} - 1, \qquad \text{RCA}_{i,t,h} = \frac{e_{i,t+h}}{e_{i,t}} - 1, \qquad \text{SCA}_{i,t,h} = \tilde{\mathbb{E}}_t \frac{e_{i,t+h}}{e_{i,t}} - 1 \tag{4-7}
$$

where $$\tilde{\mathbb{E}}$$ denotes the survey consensus (simple average across respondents). Currency excess returns are $$\text{RXR}_{i,t,h} = \text{RCA}_{i,t,h} - \text{IRD}_{i,t,h}$$ and survey excess return expectations are $$\text{SXR}_{i,t,h} = \text{SCA}_{i,t,h} - \text{IRD}_{i,t,h}$$ (eqs. 6-8, p. 3701).

The quanto-implied risk premium is constructed from quotes on conventional and quanto forwards on the S&P 500 (eq. 12, p. 3706):

$$
\text{QRP}_{i,t,h} = \frac{Q_{i,t,h} - F_t}{R^i_{f,t,h} P_t} = \frac{1}{R^{\$}_{f,t,h}} \, \text{cov}^{\mathbb{Q}}_t\!\!\left(\frac{e_{i,t+h}}{e_{i,t}}, R_{t+h}\right) \tag{12}
$$

where $$Q_{i,t,h}$$ is the quanto forward price and $$F_t$$ is the conventional S&P 500 forward price.

## Method

The paper applies standard panel regression methods to test predictability of exchange rates and to decompose what drives survey expectations. There is no new estimator. The method builds on `panel-regression` and `time-series-forecasting`.

**Baseline regression.** The in-sample predictability test adds survey excess return expectations to the standard UIP regression (eqs. 9-10, p. 3701):

$$
\text{RCA}_{i,t,h} = \alpha_h + \gamma_1 \text{SXR}_{i,t,h} + \gamma_2 \text{IRD}_{i,t,h} + \varepsilon_{i,t,h} \tag{9}
$$

$$
\text{RXR}_{i,t,h} = \alpha_h + \gamma_1 \text{SXR}_{i,t,h} + \gamma_2 \text{IRD}_{i,t,h} + \varepsilon_{i,t,h} \tag{10}
$$

Under UIP, $$\gamma_1 = 0$$ and $$\gamma_2 = 1$$. The paper assesses success by whether $$\hat{\gamma}_1$$ is positive, economically close to one, and statistically significant. Specifications with currency and time fixed effects are also estimated. Standard errors use a nonparametric block-bootstrap (Footnote 7, p. 3703) building on the approach of Hansen and Hodrick (1980), with blocks of length equal to the forecasting horizon and randomized cross-sectional width to account for overlapping observations and cross-sectional correlation; bootstrapped standard errors are typically 10th/90th percentiles of 10,000 resamples.

**Out-of-sample test.** The out-of-sample R-squared following Goyal and Welch (2008) is (eq. 14, p. 3708):

$$
R^2_{\text{OS}} = 1 - \frac{\sum_i \sum_t (\varepsilon^S_{i,t,t+h})^2}{\sum_i \sum_t (\varepsilon^C_{i,t,t+h})^2} \tag{14}
$$

where the numerator is the survey forecast error and the denominator is the competitor model error (random walk or QRP). A dollar-neutral variant $$\bar{R}^2_{\text{OS}}$$ computes errors relative to currency j for each pair (i, j) to net out dollar appreciation effects (eq. 15, p. 3709).

**What informs expectations.** To test what drives survey expectations, the paper regresses survey excess returns (SXR) on contemporaneous macro-finance variables (eq. 16, p. 3710):

$$
\text{SXR}_{i,t,h} = \alpha_h + \gamma_1 X_{i,t} + \gamma_2 \text{IRD}_{i,t,h} + \varepsilon_{i,t,h} \tag{16}
$$

where $$X_{i,t}$$ includes QRP, RER, VIX, CA/GDP, $$\beta^{\$}$$, and $$\beta^{HML}$$. Standard errors are clustered by time and currency. All predictor variables are standardized to unit standard deviation.

**Horizon analysis.** The paper annualizes variables by $$\text{SCA}^*_{i,t,h} = (12/h)\text{SCA}_{i,t,h}$$ to compare across horizons $$h \in \{1, 3, 12, 24\}$$ months (eq. 18, p. 3717). Forward expectations between horizons h and H are defined as (eq. 19, p. 3718):

$$
\text{sca}^{h,H}_{i,t} = \log\!\left(\frac{1 + \text{SCA}_{i,t,H}}{1 + \text{SCA}_{i,t,h}}\right) = \text{sca}_{i,t,H} - \text{sca}_{i,t,h} \tag{19}
$$

## Empirical specifications

**In-sample predictability (R1-R2).** Panel regressions using equations (9) and (10) at the 24-month horizon, post-GFC sample (December 2009 to March 2019, realizations until March 2021) with N = 672 observations (six currencies times approximately 112 months). The key specification is column (2) of Table I (p. 3704): SXR coefficient = 0.726 (SE 0.212), R-squared = 16.9% for RCA; similar results hold with currency and time fixed effects. Panel B extends to the full sample from December 1994, yielding N = 1,340 and similar coefficients.

**Alternative predictors (R1).** Univariate regressions of realized RXR on each alternative predictor variable separately (Table II, p. 3708). QRP data available only from December 2009 (Markit). Survey expectations achieve R-squared = 15.7% in the post-GFC sample, more than one-third higher than QRP (11.6%) and more than 50% higher than RER (10.4%).

**Out-of-sample performance (R3).** Surveys do not require estimated parameters so the out-of-sample test simply compares survey forecast errors to those of the random walk (RCA = 0) and QRP benchmark. Bootstrapped p-values are computed from the same block-bootstrap procedure as in-sample (Table III, p. 3709).

**Decomposing survey expectations (R4-R5).** Table IV (p. 3711) regresses SXR on QRP, RER, VIX, CA/GDP, $$\beta^{\$}$$, and $$\beta^{HML}$$, with standard errors clustered by time and currency. The trivariate specification (QRP, RER, CA/GDP) explains R-squared = 52.8% of variation in survey expectations. Table V (p. 3713) then tests whether the residual $$\varepsilon(\text{SXR})$$ from this regression predicts realized RCA: the coefficient is 0.177 with SE = 0.232, confirming no secret sauce.

**Horizon comparisons (R6-R8).** Table VIII (p. 3718) runs equation (10) separately for $$h \in \{1, 3, 12, 24\}$$ months and also uses long-horizon forecasts ($$\text{SXR}^*_{24}$$) to predict short-run realizations and vice versa. Table IX (p. 3719) decomposes 24-month expectations into three-month spot forecasts plus forward expectations from month 3 to month 12 and 12 to 24, regressing 24-month log realizations on these components.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Consensus Economics surveys | Monthly consensus forecasts of exchange rates at 1-, 3-, 12-, 24-month horizons; the primary SCA/SXR series | no page yet |
| Markit quanto forwards on S&P 500 | Construction of QRP (risk-neutral covariance between FX and equity); 24-month quotes, December 2009 onward | no page yet |
| Reuters forward exchange rates | Forward discounts / interest rate differentials (IRD) by horizon; used interchangeably with IRD under CIP | no page yet |
| IMF International Financial Statistics (IFS) | Current account balance and capital inflows, both scaled by GDP | [IMF IFS](/wiki/datasets/imf-ifs/) |
| BIS real exchange rate | RER predictor variable | [BIS EER](/wiki/datasets/bis-rer/) |
| FRED (VIX) | 30-day S&P implied volatility index as global risk perception proxy | [FRED](/wiki/datasets/fred/) |
| Lane-Milesi-Ferretti (2018) | Net foreign asset positions-to-GDP for robustness | no page yet |

Sample: six high-income currencies (AUD, CAD, EUR, GBP, JPY, KRW) against USD. Baseline sample: December 2009 to March 2019 (realizations until March 2021), N = 672. Full sample: December 1994 to March 2019, N = 1,340.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13504) if you are: testing the rationality of professional FX forecasters at different horizons; evaluating survey expectations as predictors against model-based alternatives; studying what macro-finance variables drive FX risk premia and expectations; or extending the QRP framework of Kremens and Martin (2019) to a broader set of predictors. The Internet Appendix (Appendix S1) contains data-source details, pre-GFC subsample results, robustness to additional currencies and specifications, and currency-specific slope estimates.

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(6). This distillation was extracted by an LLM on 2026-06-03 and is **not human-verified or independently reproduced**. The paper is paywalled; extract-only redistribution applies.

> Kremens, Lukas, Ian W. R. Martin, and Liliana Varela.
> "Long-Horizon Exchange Rate Expectations."
> *The Journal of Finance* 80, no. 6 (December 2025): 3695-3724.
> DOI: 10.1111/jofi.13504. Copyright 2025 the American Finance Association.
> Paywalled. This page is an extract by the Institute for Automated Research:
> core results summarized; not a substitute for the original.
