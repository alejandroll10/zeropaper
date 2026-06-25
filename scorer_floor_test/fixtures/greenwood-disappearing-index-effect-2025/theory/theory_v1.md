# Demand-Curve Price-Impact Decomposition of the Disappearing Index Effect

## One-sentence contribution
The abnormal return around S&P 500 additions and deletions fell from roughly 7-16% in the 1990s to statistically indistinguishable from zero in the 2010s, and this decline is driven not by changing firm composition but by the growing share of migrations from the S&P MidCap 400 (whose forced selling offsets S&P 500 forced buying) and a factor-of-~20 decline in the demand-curve multiplier M (price impact per unit demand shock).

## Setup

### Environment
The paper has no formal theoretical model; it uses a simple structural equation as the organizing framework. A stock added to (or removed from) the S&P 500 experiences a mechanical demand shock from index-tracking funds. Price impact is modeled as a constant-elasticity demand curve hit by that shock. The primitives are: an event-level demand shock $D_{it}$ (percentage of market capitalization bought on addition or sold on deletion), a multiplier $M$ (minus one over the demand elasticity), and the resulting percentage price change (CAR). The naive prediction is that because indexation grew (index-tracking assets from near zero to ~7% of market cap), the demand shock $D$ grew, so price impact should have grown. The documented decline implies $M$ must have fallen.

## Analysis

### Key result
Price impact is modeled as (equation 1):

$$\text{Price Impact}_{it} = M \times D_{it} \tag{1}$$

where $\text{Price Impact}_{it}$ is the percentage change in price, $D_{it}$ is the percentage of market capitalization bought (addition) or sold (deletion), and $M$ is minus one over the demand elasticity.

Taking means by decade and separating migrations (which face offsetting demand from MidCap trackers) from direct additions gives the decomposition (equation 4):

$$\overline{\text{CAR}} = M \times \bar{D} = M \times \left(w \cdot \bar{D}_{\text{Migrations}} + (1 - w) \cdot \bar{D}_{\text{NonMigrations}} \right) \tag{4}$$

where $w$ is the fraction of additions/deletions that are migrations and $\bar{D}_{\text{Migrations}}$, $\bar{D}_{\text{NonMigrations}}$ are the respective average net demand shocks. $M$ is backed out as the ratio of average CAR to the average weighted demand shock, separately by decade beginning in 1995 (when MidCap data start).

Event-level abnormal return is the market-adjusted CAR (equation 2):

$$\text{CAR}_{it} = R_{it} - R_{S\&P\,500, t} \tag{2}$$

### Proof
This is an empirical (descriptive) paper; there is no formal proof. The identifying argument is stated as follows. The paper documents time-series variation in event-study CARs by decade and uses the structural decomposition (equation 4) to separate two channels: (i) the demand-shock channel — the rising share $w$ of migrations from the S&P MidCap 400, where MidCap trackers' forced selling offsets S&P 500 trackers' forced buying, lowering net $\bar{D}$; and (ii) the multiplier channel — a fall in $M$, inferred as $\overline{\text{CAR}}/\bar{D}$ by decade (Table V) and via an interacted regression with characteristic controls (equation 5; Table VI). The composition channel is tested by regressing CAR on demeaned firm characteristics plus decade fixed effects (equation 3) and checking whether the decade effects shrink. The paper states explicitly that it is descriptive with no causal identification design; the variation exploited is the historical widening of passive ownership and the exogenous timing of S&P 500 inclusion decisions.

Composition regression (equation 3):

$$\text{CAR}_{it} = b_1 \text{Turn}_{i,t-1} + b_2 \text{Size}_{i,t-1} + b_3 \text{WZ}_{i,t-1} + b_4 \text{Cover}_{i,t-1} + \sum_{k=1}^{4} \gamma_k \mathbf{1}_{\text{era}=k} + e_{it} \tag{3}$$

Multiplier regression (equation 5):

$$\text{CAR}_{it} = b_1 \text{Turn}_{i,t-1} + b_2 \text{Size}_{i,t-1} + b_3 \text{WZ}_{i,t-1} + b_4 \text{Cover}_{i,t-1} + \sum_{k=1}^{3} \gamma_k \mathbf{1}_{\text{era}=k} \times D_{\text{era}=k} + e_{it} \tag{5}$$

The $\gamma_k$ in equation 5 estimate $M$ per decade after controlling for firm characteristics.

### Economic mechanism
The index effect grew from the 1980s through the 1990s as passive investing expanded, deepening a predictable, repeated arbitrage opportunity. The market then adapted: active managers, institutional investors, and coordinated trading desks now provide liquidity around index events, absorbing the index demand shock and so eliminating the abnormal return on average — despite continued growth in index-fund assets. Two forces drive the decline: (i) migrations from the S&P MidCap 400, where simultaneous forced selling by MidCap trackers offsets forced buying by S&P 500 trackers (lowering net demand $D$); and (ii) a fall in the multiplier $M$ as non-tracker liquidity providers step in. The paper interprets this as the market adapting to a predictable trading opportunity, consistent with Lo's (2004) adaptive markets hypothesis. Increased predictability of index changes plays only a minor role.

## Comparative statics
- Addition CAR by decade: 1980s 3.4%, 1990s 7.4%, 2000s 5.2%, 2010s 0.8% (declining; 2010s insignificant) (R1).
- Deletion CAR by decade: 1980s -4.6%, 1990s -16.1%, 2000s -12.4%, 2010s -0.6% (declining in magnitude; 2010s insignificant) (R2).
- Migration vs non-migration addition gap widens over time: 3.6pp (1990s) to 7.2pp (2010s); migration CARs go from 6.7% (1990s) to -1.8% (2010s) (R4, direction negative).
- Multiplier $M$ for additions: 6.75 (1995-99), 3.58 (2000-09), 0.37 (2010-20) (declining); for deletions: 10.76, 4.52, 0.70 (declining). Implied elasticity rises in magnitude (additions -0.15 to -2.72; deletions -0.09 to -1.44) (R5).
- Decline in $M$ persists under composition controls and extended front-running windows (factor-of-7 even under the most generous window) (R6, direction negative).
- Pooled cross-index addition effect declines 4.2pp; deletion effect declines 10.3pp, 2000s to 2010s (R7, direction negative).

## Connection to literature
- **Shleifer (1986)** — documents the original S&P 500 index inclusion effect (~3% around announcement) as evidence of downward-sloping demand; this paper builds on it (uses the downward-sloping-demand framing) and documents the effect's disappearance.
- **Harris and Gurel (1986)** — documents price and volume effects of S&P 500 index changes; this paper builds on that event-study foundation.
- **Bennett, Stulz, and Wang (2020)** — first notes the decline in the index inclusion effect between 1997 and 2017; this paper extends the analysis to the full 1980-2020 sample, adds deletions, and provides an economic decomposition.
- **Wurgler and Zhuravskaya (2002)** — provides the arbitrage-risk measure (WZ, CAPM residual variance) used as a control; shows arbitrage risk correlates with index price-impact magnitude; this paper builds on it as a control.
- **McLean and Pontiff (2016)** — documents that anomalies decline after academic publication; this paper analogizes the index-effect decay to this literature.
- **Preston and Soe (2021)** — also documents the decline in index inclusion and deletion effects beginning in 1995; cited as concurrent corroboration.
- **Vijh and Wang (2022)** — documents smaller absolute returns for S&P 500-to-MidCap migrations; cited in support of the migration channel.
- **Chinco and Sammon (2024)** — estimates the passive-ownership share is larger than commonly thought; used to calibrate the size of the index-tracking industry (implying even larger mechanical demand shocks).

## Implications
- The S&P 500 addition CAR fell from 7.4% (1990s) to statistically indistinguishable from zero (0.8%, 2010s); decline of -4.3pp*** from 2000s to 2010s (R1, Table I).
- The S&P 500 deletion CAR collapsed from -16.1% (1990s) / -12.4% (2000s) to -0.6% (2010s, insignificant); decline of +11.8pp*** from 2000s to 2010s (R2, Table I).
- Changing firm composition (turnover, size, arbitrage risk, analyst coverage) explains only a small fraction of the decline; the residual 2010s-vs-1990s decade gap remains large and significant (p=0.000) after controls (R3, Table II).
- Index migrations from the MidCap explain a large portion of the decline in addition returns; the migration-nonmigration gap widens from 3.6pp (1990s) to 7.2pp (2010s) (R4, Table III).
- The demand-curve multiplier $M$ for additions fell by a factor of roughly 20, from 6.75 (1995-99) to 0.37 (2010-20) (R5, Table V).
- The decline in $M$ is robust to composition controls (6.6 to 0.7) and to extended front-running windows (9.1 to 1.3, still a factor-of-7 decline) (R6, Table VI).
- The index-effect decline extends to other index families (Russell 1000/2000, S&P MidCap, SmallCap, Nasdaq 100): pooled addition effect declines 4.2pp (5% sig.), deletion effect 10.3pp (1% sig.), though individual-index results are weaker (R7, Table VIII).
