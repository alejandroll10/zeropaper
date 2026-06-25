# Managerial Capital and Financial Frictions: An Executive Financial-Education Experiment

## One-sentence contribution
A randomized 18-hour MBA-style corporate-finance course for top executives of medium and large firms in a high-friction economy causes firms to reduce working capital (chiefly by collecting receivables faster), redeploy the freed cash into capital expenditure, and raise return on assets — identifying managerial financial expertise as a binding, malleable constraint on firm performance.

## Setup

### Environment
The setting is a population of private medium and large firms operating in an economy with severe financial frictions and wide heterogeneity in the financial expertise of top executives. In a frictionless Modigliani-Miller world, financial-policy choices are value-irrelevant; once frictions bind, the firm's ability to make optimal financial decisions can affect firm value. The primitive treated as variable is the financial human capital ("managerial capital") of the executive, holding the executive-firm match fixed.

Agents: top executives (CEOs/CFOs) who choose firm financial policies (working-capital management, capital structure, investment, risk management) under a constraint on their own financial knowledge. The intervention relaxes that knowledge constraint for a randomly selected subset of executives.

Two hypotheses structure the design:
1. Education-to-policy channel: providing financial education to top executives causes changes in firm financial policies.
2. Policy-to-performance channel: those policy changes improve firm performance, because pre-treatment policies were suboptimal owing to a managerial-capital constraint.

The design is built to separate the learning channel from two competing explanations drawn from prior literature: signaling (Spence (1973)) — under which education would only reveal pre-existing ability and induce no real policy change — and networking — under which any effect would come from contacts formed at the course rather than from acquired knowledge.

## Analysis

### Key result
The paper has no formal structural model; the analytical object is the intention-to-treat (ITT) effect of randomized assignment to financial education, identified by a difference-in-differences (DID) comparison. The estimating equation, for a firm-level outcome $Y_{it}$, is:

$$
Y_{it} = \alpha + \beta_1\,\text{Treatment}_i \times \text{Post}_t + \beta_2\,\text{Treatment}_i + \beta_3\,\text{Post}_t + X_{it} + \gamma_i + \gamma_t + \varepsilon_{it} \tag{1}
$$

where $\text{Treatment}_i$ indicates random assignment to the course, $\text{Post}_t$ equals one in the first post-treatment year-end, $\gamma_i$ are firm fixed effects, $\gamma_t$ are year fixed effects, and $X_{it}$ are optional controls. The coefficient of interest is $\beta_1$, the ITT effect; standard errors are clustered at the business-group level (the level of randomization).

The headline results are: $\beta_1 < 0$ for working capital / assets; $\beta_1 < 0$ for accounts receivable / sales (the dominant component driver); $\beta_1 > 0$ for capital expenditure / assets; and $\beta_1 > 0$ for return on assets (ROA).

### Proof
This is an empirical paper, so the "proof" is the identifying argument, not a derivation. Randomized assignment of the course makes $\text{Treatment}_i$ independent of potential outcomes, so the DID estimate of $\beta_1$ is the causal ITT effect under the parallel-trends assumption between assigned-treated and assigned-control firms. ITT (rather than treatment-on-treated) is used so that post-randomization non-attendance does not select the sample; all assigned firms are retained regardless of attendance.

Identification exploits staggered course delivery: cohort 1 receives the course first; cohort 2 (the control) receives the same course later. The post-treatment window for estimation is the first year-end after cohort 1 is treated and before cohort 2 is treated. Randomization was stratified by industry and conducted at the business-group level to limit cross-firm contamination. Two competing channels are addressed by design: the RCT breaks endogenous executive-firm matching, so a pure signaling account (Spence (1973)) predicts no policy change; and a separate networking event organized for the control group shows that networking alone does not reproduce the working-capital or ROA changes. Persistence is assessed by replacing $\text{Post}_t$ with one-, two-, and three-year post-treatment indicators (the three-year horizon is confounded because the control group is treated by then). Sample-selection threats from attrition in the hand-collected data are bounded with Lee (2009) bounds, and a pseudo-external subsample restricts hand-collected outcomes to firms also covered by external data.

### Economic mechanism
In an economy where financial frictions bind, the quality of a firm's financial decisions is value-relevant, and executives' financial expertise is a scarce input ("managerial capital"). Many executives operate with suboptimal working-capital policies — notably slow collection of receivables — because they lack the relevant financial knowledge, not because slow collection is optimal. Teaching capital-budgeting, capital-structure, working-capital, and risk-management content relaxes this knowledge constraint. Executives then tighten receivables collection, freeing internal cash; because the firms are financially constrained, that internal cash is redeployed into capital expenditure rather than dissipated, and the improved allocation raises ROA. The effect being concentrated among executives without prior finance experience is consistent with learning (acquiring new knowledge) rather than signaling or networking being the operative channel.

## Comparative statics
Directional and heterogeneity results, with reported signs:
- Working capital / assets: negative ITT effect (≈ -0.4 to -0.5 SD).
- Accounts receivable / sales: negative, the dominant driver of the working-capital reduction (≈ -0.39 to -0.88 SD; collection period falls ≈ 39 to 97 days from a pretreatment mean of 179 days).
- Capital expenditure / assets: positive (≈ 9 to 13 pp; ≈ 0.45 to 0.63 SD).
- ROA: positive (≈ 0.67 to 1.09 SD; significant at 5%).
- Sales: no detected negative effect (faster collection does not come at the cost of lost sales).
- Persistence: working-capital and ROA effects hold over a two-year post-treatment window; three-year estimates are insignificant (control group treated by then).
- Heterogeneity: ROA effects larger for smaller firms, lower-leverage firms, and executives without prior finance experience.

## Connection to literature
- Bertrand and Schoar (2003) — documents that CEO/manager characteristics shape firm financial policies (non-experimental); this work builds on it by supplying experimental evidence for the expertise-to-policy link.
- Custódio and Metzger (2014) — non-experimental evidence that financial-expert CEOs follow financial theory and adopt better financial policies; this work builds on it, providing a causal counterpart.
- Bloom et al. (2013) — management-practices RCT for manufacturing plants; this work extends that training literature from operational practices to financial practices and to top executives of larger firms.
- Bruhn and Zia (2013) — business-training RCT for microentrepreneurs; this work extends it from microentrepreneurs to top executives of medium and large firms.
- Spence (1973) — signaling theory of education; this work tests it, providing evidence that the education effect operates through improved decision-making rather than signaling.

## Implications
- Working capital falls in treated firms relative to controls (≈ -0.4 to -0.5 SD).
- The reduction is driven by faster accounts-receivable collection (≈ -0.39 to -0.88 SD; ≈ 39 to 97 fewer collection days).
- Capital expenditure rises (≈ 9 to 13 pp of assets): freed cash is invested.
- ROA increases (≈ 0.67 to 1.09 SD), significant at 5%, and persists for two years.
- Survey evidence corroborates policy change: 55% of treated vs 7% of control firms implemented at least one financial-policy change (working-capital gap 25.6 pp, significant at 1%).
- Effects concentrate among smaller firms, lower-leverage firms, and executives without prior finance experience, consistent with a learning channel.
