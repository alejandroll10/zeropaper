# One-Sided vs Two-Sided Kernel Identification of Return-Predictability Pockets

## One-sentence contribution
The claim that U.S. aggregate stock-market return predictability is time-varying and identifiable ex ante via "pockets" is an artefact of a two-sided (lookahead) kernel in the pocket-identification step; restricting that step to information available before the forecast date collapses average integral R-squared by roughly 20-fold and erases the in-pocket/out-of-pocket predictability difference and the associated market-timing gains.

## Setup

### Environment
- **Object under study.** Predictability of the excess return on the aggregate U.S. equity market, evaluated at daily and monthly frequency over 1926–2016 (sample start varies by predictor).
- **Predictors.** A vector of standard time-series predictors: dividend–price ratio (dp), 3-month T-bill rate (tbl), term spread (tsp), and realized variance (rvar), plus principal-component and combination forecasts.
- **Forecasting model.** Returns follow a time-varying-coefficient predictive regression (eq. 1):

$$
r_{t+1} = x_t' \beta_t + \epsilon_{t+1} \tag{1}
$$

where $r_{t+1}$ is the excess market return, $x_t$ the predictor vector, $\beta_t$ time-varying coefficients, and $\sigma_t^2 = E[\epsilon_{t+1}^2 \mid x_t]$ permits conditional heteroskedasticity.

- **Coefficient estimation.** The $\beta_t$ are estimated by a local-constant kernel regression (eq. 2):

$$
\hat{\beta}_t = \operatorname*{arg\,min}_{\beta_0} \sum_{s=1}^{T} K_{hT}(s-t)\,[r_{s+1} - x_s' \beta_0]^2 \tag{2}
$$

with kernel weights $K_{hT}(u) = K(u/hT)/(hT)$ and bandwidth $h$ (a 2.5-year bandwidth in this step). The coefficient stage uses a one-sided Epanechnikov kernel (eq. 3):

$$
K(u) = \tfrac{3}{2}(1 - u^2)\cdot \mathbf{1}\{-1 < u < 0\} \tag{3}
$$

so only data before $t$ receives positive weight; the $\beta_t$ estimation is genuinely out-of-sample.

- **Assumption.** The two estimation frameworks compared below are identical in every primitive (predictors, bandwidths, performance metrics) except the kernel used in the second (pocket-identification) stage. Any difference in results is therefore attributable to the kernel type alone.

## Analysis

### Key result
A "pocket" is a period in which the kernel forecast outperforms the prevailing-mean benchmark. Define the squared-error differential (eq. 4):

$$
\text{SED}_t = (r_t - \bar{r}_{t|t-1})^2 - (r_t - \hat{r}_{t|t-1})^2 \tag{4}
$$

where $\bar{r}_{t|t-1}$ is the prevailing-mean forecast, $\hat{r}_{t|t-1}$ the kernel forecast; positive $\text{SED}_t$ means the kernel model has smaller forecast error that period. A pocket begins when the fitted SED trend is positive (eq. 5):

$$
\widehat{\text{SED}}_t = \gamma_{0,t} + \gamma_{1,t}\, t > 0 \tag{5}
$$

The identifying claim is that $\gamma_{0,t}, \gamma_{1,t}$ should be estimated with a one-sided Epanechnikov kernel and one-year bandwidth, so that pocket membership at $t$ depends only on pre-$t$ information. The result: when eq. (5) is instead estimated with a two-sided 24-month symmetric window (12 months before and 12 months after $t$), the identification draws on data unavailable at forecast time, and the resulting in-pocket predictability is a lookahead artefact. Under the correctly one-sided identification, in-pocket predictability is statistically indistinguishable from out-of-pocket predictability.

### Proof
This is a methodological audit and replication; there is no formal theorem to prove. The identifying argument is a two-framework comparison. The complete analysis is run twice with all parameters held fixed; only the kernel in the eq. (5) pocket-identification stage differs (one-sided vs two-sided). Because the kernel type is the sole deviation, the contrast between the two runs isolates the effect of the lookahead bias. The mechanism by which a two-sided kernel induces bias is direct: weighting observations after $t$ when classifying $t$ as in- or out-of-pocket leaks future return information into the classification, converting an out-of-sample procedure into an in-sample one. The empirical magnitudes below quantify the resulting difference.

### Economic mechanism
A two-sided kernel in the pocket-identification step assigns positive weight to data both before and after the forecast date. Classifying period $t$ as a predictability "pocket" therefore uses information that would not have been available to a forecaster at $t$. This in-sample leakage manufactures apparent ex-ante predictability: pockets are labelled where returns subsequently turned out to be forecastable. Once identification is restricted to pre-$t$ information (one-sided kernel), the labelling can no longer exploit the future, pockets shrink to near one-day artefacts, and predictability inside pockets matches that outside.

## Comparative statics
- **Kernel type (one-sided vs two-sided), daily integral R-squared.** Mean integral R² falls from {dp 1.51%, tbl 1.70%, tsp 2.92%, rvar 2.77%} (two-sided) to {dp 0.18%, tbl 0.09%, tsp 0.09%, rvar 0.28%} (one-sided): roughly a 20-fold collapse. Direction: predictability decreasing in correct (one-sided) identification.
- **In-pocket Clark–West t-statistics.** Two-sided in-pocket CW (unrestricted): dp 3.00***, tbl 4.75***, tsp 3.04***; one-sided: dp −0.47, tbl 0.10, tsp −1.06. Significance vanishes under correction.
- **Market-timing economics.** Average Sharpe ratio drops from 0.71 (two-sided) to 0.44 (one-sided), below the prevailing-mean benchmark of 0.46; annualised in-pocket alphas fall from 0.76–6.38% to −0.44–2.51%.
- **Out-of-pocket performance (two-sided code).** Out-of-pocket CW t-stats are significantly negative at 10%: dp −1.62, tbl −1.33, tsp −1.52, rvar −1.77 — the benchmark beats the kernel model out-of-pocket even under the original code.
- **Bandwidth/window robustness.** Across 2-, 2.5-, 3-year coefficient windows and 6-, 12-, 18-month SED windows, the corrected code yields no significant in-pocket CW statistic in any configuration.
- **Frequency.** Monthly data replicate the daily pattern: strong two-sided in-pocket CW (tbl 3.55***, tsp 2.44**) becomes insignificant one-sided (dp 0.90, tbl 1.22, tsp 0.57, rvar 1.01).
- **Partial exception.** Factor portfolios (SMB, HML) retain some time-varying predictability under the one-sided kernel, though weaker than under the two-sided approach; the aggregate equity market is the null.

## Connection to literature
- **Farmer, Schmidt & Timmermann (2023)** [replicates] — established the "pockets of predictability" finding for aggregate market returns using kernel regressions. This work audits their published replication package, locates a two-sided kernel in the pocket-identification step where the text specifies one-sided, and shows that correcting it removes the predictability the original documents.
- **Campbell & Thompson (2008)** [builds-on] — supplies the economic restrictions on forecasts (non-negative return forecasts, sign-consistent slope coefficients) used here as forecast-restriction variants.
- **Clark & West (2007)** [builds-on] — supplies the CW out-of-sample forecast-comparison test used as the primary statistical performance metric against the prevailing-mean benchmark.

## Implications
- The original two-sided code reproduces the prior "pockets" result exactly: daily in-pocket mean integral R² 1.48–3.70%, with strong in-pocket/out-of-pocket asymmetry.
- Correcting to a one-sided kernel collapses predictability ~20-fold; pockets become ~20x more frequent, ~10x shorter, and far less predictable.
- In-pocket CW t-statistics that commonly exceed 3–4 under the two-sided code become insignificant for nearly all 27 model–predictor combinations under correction.
- Market-timing Sharpe ratio falls to 0.44 (below the 0.46 benchmark); in-pocket alphas mostly lose significance.
- The benchmark prevailing-mean model beats the kernel model out-of-pocket even under the original two-sided code.
- No bandwidth/window configuration of the corrected code recovers in-pocket predictability.
- Monthly data confirm the daily null.
- Factor returns (SMB, HML) are a partial exception retaining some predictability; the aggregate market predictability does not survive.
