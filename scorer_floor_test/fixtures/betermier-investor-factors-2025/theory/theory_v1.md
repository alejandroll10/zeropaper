# Investor Pricing Factors (IPF)

> This is an empirical paper (contributionType: new-method, new-fact;
> resultType: new-finding). Per the reconstruction rules, the "Proof" section
> below states the paper's identifying argument and spanning derivation rather
> than a formal theorem proof, and the draft mixes a formal spanning condition
> with a reduced-form mechanism.

## One-sentence contribution

Pricing factors recovered from individual investors' equity holdings (Norway,
1997-2017) — specifically a two-factor model of the market plus a combined
age-wealth portfolio (AW) — price the cross section of Norwegian equity returns
out-of-sample and absorb established firm-based factors.

## Setup

### Environment

Primitives, from "Theory / model":

- A cross section of J stocks with excess return vector $R^e$, expected excess
 return vector $\mu$, and variance-covariance matrix $\Sigma$.
- A risk-free rate $R_f$ (empirically the 1-month NIBOR).
- The market portfolio $m$.
- A population of heterogeneous individual investors, each $i$ holding an equity
 portfolio $\omega^i$. Investors are grouped into $G = 90$ groups by age (12),
 wealth (12), permanent real income (12), gender (2), education (3), region (9),
 industry (17), and occupation (9).
- Each group portfolio $\omega^g = \sum_{i \in I_g} w^g_i\,\omega^i$ with
 equity-wealth weights $w^g_i = E^i / \sum_{i'\in I_g} E^{i'}$ (eq. 14).

Tangency portfolio (eq. 1): for J stocks,

$$
\tau = \frac{1}{\phi}\,\Sigma^{-1}(\mu - R_f\mathbf{1}), \qquad
\phi = \mathbf{1}'\Sigma^{-1}(\mu - R_f\mathbf{1}) > 0.
$$

Every stock's risk premium satisfies (eq. 2)

$$
\mu_j - R_f = \phi\,(\Sigma\tau)_j = b_{j,\tau}(\mu_\tau - R_f),
$$

so pricing the tangency portfolio is equivalent to pricing all stocks.

Assumption 1 (spanning): there exist N long-short investor portfolios
$\pi^1,\ldots,\pi^N$ extractable from the sample such that
$\tau \in \operatorname{Span}[m,\pi^1,\ldots,\pi^N]$.

## Analysis

### Key result

When Assumption 1 holds, the tangency portfolio is a linear combination of the
market and the N investor portfolios (eq. 4):

$$
\tau = m + \sum_{n=1}^{N}\eta_n\,\pi^n,
$$

and every stock's risk premium satisfies a multifactor pricing equation
(Proposition 1, eq. 6):

$$
\mu_j - R_f = \beta_{j,M}(\mu_M - R_f) + \sum_{n=1}^{N}\beta_{j,n}\,E(p_n),
$$

where $p_n = (\pi^n)'R^e$ is the return on the n-th Investor Pricing Factor (IPF)
and $(\beta_{j,M},\beta_{j,1},\ldots,\beta_{j,N})'$ is the vector of OLS
coefficients of stock j's return on the (N+1) factors.

Proposition 1 also implies a stock's CAPM alpha satisfies (eq. 7):

$$
a_{j,M} = \phi\sum_{n=1}^{K}\eta_n\,(b_{j,n} - b_{j,M}\,b_{M,n})\,\sigma_n^2,
$$

with $b_{j,n} = \operatorname{cov}(R^e_j,p_n)/\sigma_n^2$ and
$b_{M,n} = \operatorname{cov}(\text{MKT},p_n)/\sigma_n^2$.

The preferred empirical specification (IPF*, eq. 23) is the two-factor
model market + AW:

$$
R^e_{j,t} = \alpha_j + \beta_{j,\text{MKT}}\,\text{MKT}_t + \beta_{j,\text{AW}}\,AW_t + v_{j,t},
$$

with $\alpha_j = 0$ for all j if IPF* is correctly specified.

### Proof

(Identifying argument, as the page presents it — no formal theorem proof is
given for the empirical claims.) The chain is:

1. Equivalence (eqs. 1-2): pricing $\tau$ prices the whole cross section.
2. Recovery: under Assumption 1's spanning condition, $\tau$ is recoverable as a
 linear combination of the market and extractable long-short investor
 portfolios (eq. 4), yielding the multifactor pricing relation (eq. 6) and the
 CAPM-alpha expression (eq. 7).
3. Choice of characteristics: two theoretical models (Section I.D) motivate age and wealth as the IPF sorting characteristics — an
 ICAPM with heterogeneous CRRA investors (eq. 17, deviation by age and
 income-to-wealth ratio) and a sentiment model (eq. 18, deviation by functions
 of age and wealth). Both predict portfolio deviations from $\tau$ that load on
 age and wealth.
4. Construction: PCA on the $G\times G$ variance-covariance matrix of the 90
 group portfolios (eqs. 19-20); the first two PCs explain 80% of
 cross-sectional variance; PC1 maps to the market (R2 = 0.62), PC2 to the
 combined age-wealth portfolio (R2 = 0.55).
5. Extraction: IPFs are zero-investment long-short portfolios
 $\pi^n = \sum_g z^g_n\,\omega^g$ with $\sum_g z^g_n = 0$ (eq. 15). The age
 portfolio is long ages 70-75, short ages 18-30; the wealth portfolio is long
 the top 1%, short the bottom 10-30%; AW = ½(AGE + WEALTH); returns
 $AW_t = (\pi_{\text{AW},t-1})'R^e_t$ net of NIBOR.
6. Test: spanning regressions (Tables II-IV) and out-of-sample bootstrap Sharpe
 ratios (eq. 24 following Fama-French 2018 and Kozak-Nagel-Santosh 2020) verify
 AW earns a CAPM alpha, spans firm factors, and beats firm-factor models
 out-of-sample.

### Economic mechanism

Individual investor portfolios contain recoverable pricing information because
investors deviate from the tangency portfolio in ways linked to age and wealth.
Two complementary channels are invoked (mechanisms: risk-sharing,
behavioral-bias):

- Hedging / risk-sharing (ICAPM, eq. 17): younger investors and those with more
 human-capital/income risk and debt tilt away from the tangency portfolio;
 mature and wealthy investors hold portfolios closer to $\tau$ and earn higher
 CAPM alphas.
- Sentiment / behavioral bias (eq. 18): sentiment covaries with age and wealth,
 generating a reduced-form factor structure on the same characteristics.

The two channels jointly drive investor tilts toward the age-wealth pricing
factor.

## Comparative statics

Directional / heterogeneity results as reported (Core results, findings[]):

- Factor tilts rise monotonically with age and wealth, from -0.3 (investors
 under 30) to +0.1 (ages 70-75), ~1.2%/yr average return difference (R6;
 Figure 2 +). Direction: positive in age/wealth.
- Tilt determinants (R7; Table VII): income beta -0.051 (t = -6.40),
 debt indicator -0.047 (t = -5.55) [hedging channel, reduce tilt]; finance
 occupation +0.627 (t = 34.60), stock-market experience +0.026 (t = 7.58)
 [sophistication/sentiment, raise tilt]; male dummy -0.156 (t = -15.00).
 Direction: mixed.
- Long-leg vs short-leg stock characteristics (R8; Table VIII): long
 leg has higher median market cap (973M vs 483M NOK), book-to-market (0.90 vs
 0.66), profitability (0.06 vs 0.05); short leg has higher CAPM beta (1.02 vs
 0.73), volatility (0.18 vs 0.08), and turnover. Direction: mixed.
- AW CAPM beta is negative: -0.12 (t = -6.96) (R2; Table II col. 2).

## Connection to literature

One line per relatesTo edge:

- Merton (1973), builds-on: ICAPM framework grounds the theoretical spanning
 condition; investor deviation portfolios map to hedging demands.
- Balasubramaniam, Campbell, Ramadorai & Ranish (2023), builds-on: their
 documented strong factor structure in individual investor portfolios motivates
 the PCA grouping approach.
- Kozak, Nagel & Santosh (2020), builds-on: covariance shrinkage used in the
 bootstrap Sharpe ratio estimation (eq. 24).
- Fama & French (2018), builds-on: bootstrap out-of-sample Sharpe ratio
 evaluation methodology.
- Betermier, Calvet & Sodini (2017), extends: extends life-cycle links between
 demographics and value-factor tilts from Swedish households into a full IPF
 extraction framework.
- Koijen & Yogo (2019), tests: IPF* also prices the institutional investor
 portfolio held on the OSE (Internet Appendix Table IA.VIII;).

## Implications

Headline empirical findings, from Core results (R1-R8):

1. Two PCs explain 80% of cross-sectional variation in group portfolio holdings;
 PC1 tracks the market (R2 = 0.62), PC2 the age-wealth portfolio (R2 = 0.55)
 (R1; Table I).
2. The combined age-wealth factor (AW) earns a significant CAPM alpha of 32
 bps/month (3.8%/yr, t = 3.16) (R2; Table II).
3. AW spans firm factors: alpha remains 24 bps/month (t = 2.55) after all five FF
 factors (R3; Table III).
4. IPF* prices established firm factors: adding AW to the market renders
 momentum, profitability, and investment alphas statistically insignificant and
 reduces them ~40% (R4; Table IV).
5. Out-of-sample Sharpe ratio of IPF* (0.45) exceeds all firm-factor models
 (0.19-0.40) and is 45% above the market (0.31) (R5; Table V).
6. Factor tilts increase monotonically with age and wealth (-0.3 to +0.1; ~1.2%/yr
 return difference) (R6; Figure 2 +).
7. Debt and income beta reduce tilts (hedging); finance occupation, stock-market
 experience, and female gender raise tilts (sophistication/sentiment) (R7;
 Table VII).
8. Long-leg AW stocks have higher market cap, book-to-market, and profitability;
 short-leg stocks have higher CAPM beta, volatility, and turnover (R8; Table
 VIII).
