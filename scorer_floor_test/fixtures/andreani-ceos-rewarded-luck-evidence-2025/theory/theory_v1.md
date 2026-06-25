# Asymmetric Pay-for-Luck under Weak Pay Scrutiny: A Tax-Windfall Test of Rent Extraction

## One-sentence contribution
A one-off, exogenous corporate tax-rate cut changes CEO compensation through a rent-extraction channel: weakly scrutinized CEOs are rewarded for windfall tax gains but not penalized for windfall tax losses, an asymmetry optimal contracting cannot produce.

## Setup

### Environment
- **Agents.** Firms (principals/shareholders) and CEOs (agents). Compensation is set under either an optimal-contracting regime or a rent-extraction regime, distinguished empirically by the degree of external pay scrutiny a firm faces.
- **Shock primitive.** A national tax-rate cut (35% → 21%) forces a one-time remeasurement of deferred tax balances. Firms with large net deferred tax liabilities (DTL) book a one-off gain; firms with large net deferred tax assets (DTA) book a one-off loss. The sign and size of the windfall are determined by a firm's *pre-existing* stock of deferred tax balances, which reflect past transactions, not current managerial effort.
- **Luck conditions (assumptions that make the shock "luck").** (i) The trigger is a government decision exogenous to managers; (ii) the reform was largely unanticipated and passed in under three months, making firm influence/anticipation implausible; (iii) the firm-specific windfall is mechanically pinned by past balances, not present effort.
- **Two competing frameworks tested.**
  - *Optimal (efficient) contracting:* pay should respond only to performance attributable to managerial effort; one-off tax windfalls unrelated to managerial actions should not move pay.
  - *Rent extraction:* CEOs with limited pay scrutiny extract maximal compensation. Its distinguishing predictions are (i) pay responds to luck factors beyond CEO control, (ii) the response is asymmetric (good luck rewarded, bad luck not penalized), and (iii) it is concentrated where pay scrutiny is weak.
- **Pay Scrutiny primitive.** A composite external-monitoring index, built as the first principal component of five beginning-of-year firm proxies: market value, liquidity, trading volume, nonzero-return days, and analyst coverage. Internal-governance proxies are argued to have lost discriminating power post-regulatory homogenization, motivating a market-based external measure.

## Analysis

### Key result
The test is a triple-difference (DDD) panel regression of CEO compensation in fiscal year $t$ (eq. 1):

$$
\begin{aligned}
\text{Total Comp}_t = \;& \beta_0 + \beta_1 \text{Tax Shock}_t + \beta_2 \text{DTA}_{t-1} + \beta_3 \text{Tax Shock}_t \times \text{DTA}_{t-1} \\
& + \beta_4 \text{DTL}_{t-1} + \beta_5 \text{Tax Shock}_t \times \text{DTL}_{t-1} + \beta_6 \text{Pay Scrutiny}_{t-1} \\
& + \beta_7 \text{Tax Shock}_t \times \text{Pay Scrutiny}_{t-1} + \beta_8 \text{DTA}_{t-1} \times \text{Pay Scrutiny}_{t-1} \\
& + \beta_9 \text{Tax Shock}_t \times \text{DTA}_{t-1} \times \text{Pay Scrutiny}_{t-1} + \beta_{10} \text{DTL}_{t-1} \times \text{Pay Scrutiny}_{t-1} \\
& + \beta_{11} \text{Tax Shock}_t \times \text{DTL}_{t-1} \times \text{Pay Scrutiny}_{t-1} \\
& + \gamma' X_{t-1} + \theta' \lambda_j + \pi' \tau_t + \phi' \tau_t \times \text{DTA}_{t-1} + \psi' \tau_t \times \text{DTL}_{t-1} + \varepsilon_t
\end{aligned} \tag{1}
$$

where $\text{Tax Shock}_t = 1$ for fiscal years ending between 31 Dec 2017 and 31 Mar 2019; $\text{DTA}_{t-1}$ and $\text{DTL}_{t-1}$ are beginning-of-year deferred tax assets and liabilities scaled by total assets; $X_{t-1}$ is a control vector (size, profitability, past returns, book-to-price, idiosyncratic volatility, leverage, log CEO age, log CEO tenure); $\lambda_j$ is firm fixed effects; $\tau_t$ is calendar-year fixed effects; standard errors clustered by firm.

The primary objects of interest are the double interaction $\text{Tax Shock} \times \text{DTL}$ (pay for windfall gains), the double interaction $\text{Tax Shock} \times \text{DTA}$ (pay for windfall losses), and their triple interactions with Pay Scrutiny.

Pay Scrutiny is the first principal component of the five external proxies (it accounts for 78% of their variation):
$$
\text{Pay Scrutiny}_j = \text{PC}_1(\text{Market Value}_j, \text{Liquidity}_j, \text{Trading Volume}_j, \text{Nonzero Return Days}_j, \text{Analyst Coverage}_j)
$$
with each proxy min-max normalized to $[0,1]$ and the component re-normalized to $[0,1]$.

The result that distinguishes the two frameworks: in the transition period, $\text{Tax Shock} \times \text{DTL} > 0$ for low-scrutiny firms (windfall gains rewarded), the triple interaction $\text{Tax Shock} \times \text{DTL} \times \text{Pay Scrutiny} < 0$ (the reward vanishes under high scrutiny), and $\text{Tax Shock} \times \text{DTA}$ is statistically indistinguishable from zero (windfall losses not penalized), with the gain–loss asymmetry rejected as symmetric by an F-test.

### Proof
This is an empirical paper: it states no formal proof but an *identification argument*, transcribed here as the analogue of the proof. Identification rests on the windfall being luck (the three luck conditions above), so any pay response to $\text{Tax Shock} \times \text{DTL}$ or $\text{Tax Shock} \times \text{DTA}$ cannot reflect rewards for effort in the transition window. Firm fixed effects ($\lambda_j$) absorb time-invariant firm pay levels; calendar-year fixed effects ($\tau_t$) absorb common time shocks; $\tau_t \times \text{DTA}$ and $\tau_t \times \text{DTL}$ terms absorb differential time trends correlated with deferred-tax exposure. A sharper *within-calendar-year* design (Section's col-4 specification) exploits the staggering of the transition window across fiscal year-ends: adding calendar-year-by-DTA and calendar-year-by-DTL fixed effects compares pay across firms whose statements are more vs. less likely to reflect the tax effect within the same calendar year. Pre-trend interactions show no differential DTA/DTL compensation trend before the shock, supporting parallel trends. The triple-difference with Pay Scrutiny separates rent extraction (effect concentrated at low scrutiny) from optimal contracting (which predicts no windfall response at any scrutiny level).

### Economic mechanism
Under weak external monitoring, a CEO can capture compensation tied to gains the firm realizes by luck without bearing symmetric downside when luck is adverse, because setting pay downward is more visible/contestable than withholding an upward adjustment. Optimal contracting filters out luck symmetrically and so predicts no windfall response; the observed gain-reward-without-loss-penalty, conditional on weak scrutiny, is the signature of rent extraction. External pay scrutiny is the disciplining force: where investors and analysts watch closely, the windfall-pay link disappears.

## Comparative statics
- **By scrutiny (gains).** Reward for windfall gains is decreasing in Pay Scrutiny: positive at low scrutiny, absent at high scrutiny (triple interaction negative).
- **Gain vs. loss asymmetry.** Pay responds positively to windfall gains (DTL) but does not respond to windfall losses (DTA); symmetry is rejected.
- **By pay component.** The windfall reward is concentrated in discretionary (variable) pay; the fixed-salary response is positive but substantially smaller in magnitude.
- **By executive type.** Present for CEOs and CFOs; absent for other named executive officers.
- **Robustness of sign.** The within-calendar-year design strengthens, not weakens, the windfall-gain coefficient.

## Connection to literature
- **Bertrand and Mullainathan (2001)** — established pay-for-luck using market/industry returns and a rent-extraction interpretation; this design *tests* that interpretation with a cleaner, plausibly exogenous luck shock and a market-based external-scrutiny proxy generalizing their internal-governance measures.
- **Garvey and Milbourn (2006)** — predicted asymmetric pay-for-luck (gains rewarded, losses not penalized); this design provides cleaner evidence *consistent with* that asymmetry.
- **Daniel, Li, and Naveen (2020)** — argued earlier pay-for-luck evidence is not robust; this design *contradicts* that conclusion by restoring the asymmetric finding under a different, cleaner luck measure.
- **Blanchard, Lopez-de-Silanes, and Shleifer (1994)** — small-sample study of cash windfalls and CEO pay; this design *builds on* it as a large-sample extension using tax windfalls.

## Implications
- In the transition period, weakly scrutinized CEOs earn significantly more when their firm has larger net deferred tax liabilities (windfall gains); the effect is absent for high-scrutiny CEOs ($\text{Tax Shock} \times \text{NDTL} = 2.17$, $t=2.40$; $\text{Tax Shock} \times \text{NDTL} \times \text{Pay Scrutiny} = -3.81$, $t=-2.68$).
- Separating DTA from DTL, CEO pay is positively associated with DTL in low-scrutiny firms: a firm in the 3rd DTL quartile pays its CEO 19.7% more than one in the 1st quartile (≈ \$790,000 for the median-pay CEO); $\text{Tax Shock} \times \text{DTL} = 3.311$ ($t=3.20$), $\text{Tax Shock} \times \text{DTL} \times \text{Pay Scrutiny} = -5.814$ ($t=-3.62$).
- CEO pay is not reduced for windfall tax losses: $\text{Tax Shock} \times \text{DTA}$ is insignificant throughout, and an F-test ($p=0.000$) rejects equality of the DTA and DTL magnitudes.
- The reward concentrates in discretionary pay: $\text{Tax Shock} \times \text{DTL}$ (discretionary) $= 6.61$ ($t=3.69$) vs. fixed comp $= 0.802$ ($t=3.23$), substantially smaller; discretionary triple interaction $= -7.175$ ($t=-1.97$).
- The reward is specific to CEOs and CFOs (CFO $\text{Tax Shock} \times \text{DTL} = 2.32$, $t=2.21$), not other named executive officers (all insignificant).
- The within-calendar-year identification confirms the main result (DTL coefficient strengthens) with no pre-trends.
