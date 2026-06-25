# Excess Mortgage Denial Decomposition via Underwriting Controls and Lender Strictness

> This is an empirical (reduced-form causal) paper with no formal economic model.
> Per the reconstruction protocol, the "Proof" section below states the paper's
> identifying argument rather than a formal derivation, and the "Setup" describes
> the reduced-form decision framework the paper writes down (equations (1)-(4)).

## One-sentence contribution

Using confidential expanded 2018-2019 HMDA data, observable underwriting factors (credit score, LTV, DTI, AUS recommendation) explain most of the racial/ethnic gap in mortgage denial rates, leaving a residual "excess denial" gap of 1-2 percentage points that is itself at least partially explained by race-correlated unobserved risk factors rather than discrimination.

## Setup

### Environment

The paper has no formal economic model; it defines disparate treatment structurally as a difference in expected credit decisions across race/ethnicity for otherwise identical applicants. Primitives:

- Applicants indexed by $j$, each with race/ethnicity $r$ (relative to non-Hispanic White), risk characteristics $X$ observable in HMDA, and additional risk characteristics $u$ unobserved in HMDA.
- A binary automated underwriting system (AUS) recommendation:
 $$D_{AUS} = g(X, u), \tag{1}$$
 where $g(\cdot)$ is a deterministic function of risk characteristics (Section I lists the full DU factor list).
- Lender $i$'s binary denial decision:
 $$D^{i}_{Lender} = h_i(X^*, u, w, r) + e, \tag{2}$$
 where $h_i(\cdot)$ may differ from $g(\cdot)$; $X^*$ is a potentially updated value of $X$ after verification; $w$ is lender-specific overlays beyond AUS; $r$ is race/ethnicity; $e$ is idiosyncratic human error.

Assumption defining the object of interest: lender $i$ engages in disparate treatment against Black relative to White applicants if:
$$\int h_i(X^*, u, w, \text{Black})\, dF_B(X^*, u, w) > \int h_i(X^*, u, w, \text{White})\, dF_B(X^*, u, w), \tag{3}$$
where $F_B(\cdot)$ is the joint CDF of underwriting factors for the Black applicant population. The identification challenge is separating $r$ (illegal discrimination) from $u$ and $w$ (unobserved but potentially race-correlated risk factors).

## Analysis

### Key result

The main estimating equation is a linear probability model (Table II):
$$D^{i}_{Lender,j} = \alpha_r \cdot \mathbf{1}[\text{race}_j = r] + \beta' X_j + \delta_l + \varepsilon_j, \tag{4}$$
where $j$ indexes applications; $r$ indexes race/ethnicity relative to non-Hispanic White; $X_j$ includes the FICO-LTV-DTI grid, AUS denial recommendation (interacted with loan purpose and program), county-by-month fixed effects, loan amount bins, co-applicant indicator, and income bins (all interacted with program and loan purpose); $\delta_l$ is a lender fixed effect; standard errors are clustered at the lender and county levels.

Main estimate (Table II col.(3), preferred full specification): after full FICO-LTV-DTI-AUS-lender controls, excess denial $\alpha_r$ is 2.0 pp for Black, 0.9 pp for Hispanic, 1.4 pp for Asian applicants (s.e. 0.001). This compares with a raw Black-White denial gap of 10 pp before controls (Black 18%, White 8%; Table I).

### Proof

(Identifying argument, as the page states it — no formal proof.) Identification is by selection-on-observables. The argument proceeds in two parts:

1. **Decomposition.** Equation (4) progressively conditions on the underwriting factors lenders use. Columns (1)-(3) vary the control set; the residual race coefficient $\alpha_r$ in column (3) measures the denial gap not explained by observed risk. The raw 10 pp gap collapses to 1-2 pp once the FICO-LTV-DTI grid and AUS recommendation are included.

2. **Attributing the residual to unobserved risk $u$ rather than to discrimination $r$.** The AUS is color-blind by design, so re-running (4) with the AUS denial indicator $D_{AUS,j}$ as the dependent variable (Table II cols. 4-5) isolates residual gaps that can only reflect unobserved risk $u$ correlated with race. The Black AUS excess denial is 1.5 pp (Table II col.(5)), indicating race-correlated unobserved risk inside the AUS-considered factors. The **lender strictness measure** — the lender fixed effect from a denial regression run only on White applicants — isolates overlay policy $w$ from any minority treatment by construction; lender-specific excess minority denials correlate positively with strictness (r = 0.63 Black, 0.50 Hispanic, 0.65 Asian; Figure 2), consistent with stricter overlays on unobserved risk rather than discriminatory intent. Indirect tests interacting race with fintech, market concentration, and racial-animus search rates (Table IV) do not yield clear evidence of discrimination.

### Economic mechanism

Race-correlated risk characteristics unobserved in HMDA ($u$) — and considered by automated underwriting and by lenders' overlays ($w$) — generate part of the residual denial gap that conditioning on observed factors leaves behind. Because the AUS is color-blind, a residual gap in AUS recommendations can only come from $u$; because strictness is measured on White applicants only, a positive strictness/excess-denial correlation indicates overlays screening unobserved risk rather than differential treatment of minorities. The contribution-type is new-fact/measurement via an information-asymmetry mechanism (race-correlated unobserved risk).

## Comparative statics

- Stricter lenders have the largest excess minority denial rates: correlation with strictness 0.63 (Black), 0.50 (Hispanic), 0.65 (Asian) (Figure 2, R3), positive direction.
- AUS excess denial for Black applicants is 1.5 pp after full controls (Table II col.(5), R4), positive — race-correlated unobserved risk inside AUS factors.
- Racially-charged-search-rate interaction with Black excess denials is 0.002** (s.e. 0.001), similar for lender and AUS excess denials (Table IV col.3 vs col.6, R5), positive — pattern consistent with unobserved risk rather than discrimination.
- Service quality (NSMO): Black borrowers 4.5 pp more likely to report processing delays and 9.6 pp more likely to have postponed closing (Table V cols.1-2, R6; outcome means 0.16, 0.21), negative-for-borrower direction.
- Satisfaction (NSMO): Black borrowers 7.1 pp less likely to be very satisfied; Asian borrowers 11.3 pp less satisfied (Table V col.6, R7; outcome mean 0.78), negative-for-borrower direction.

## Connection to literature

- **Munnell et al. (1996)** [contradicts] — found ~8 pp excess denials for Black/Hispanic applicants in 1990s Boston; this paper finds only 1-2 pp with modern HMDA data, suggesting substantial progress in fair lending.
- **Bartlett et al. (2022)** [tests] — estimate 7-10 pp denial gaps without conditioning on credit score and other risk factors; this paper conditions on these and finds much smaller residual gaps.
- **Giacoletti, Heimer & Yu (2025)** [tests] — find a 7 pp Black-White gap without credit score/LTV/DTI controls and estimate at least half reflects disparate treatment; this paper's evidence points more to unobserved risk.
- **Bhutta and Hizmo (2020)** [extends] — earlier paper on minority mortgage pricing disparities; this paper provides parallel evidence on denial disparities using expanded HMDA.
- **Fuster et al. (2019)** [builds-on] — fintech-lender identification used to test whether algorithmic lending reduces discrimination.
- **Arnold, Dobbie & Yang (2018)** [builds-on] — judge-specific propensity-to-release framework adapted here as the lender-specific strictness measure.

## Implications

- Raw Black-White denial gap is 10 pp before controls (Black 18%, White 8%); Table I (R1).
- Excess denial after full controls: Black 2.0 pp, Hispanic 0.9 pp, Asian 1.4 pp; Table II col.(3) (R2) — vs. Munnell et al. (1996) ~8 pp benchmark.
- Stricter lenders have larger excess minority denials (Figure 2 correlations) (R3) — consistent with unobserved-risk overlays.
- AUS excess denial for Black applicants 1.5 pp (R4) — race-correlated unobserved risk in AUS factors.
- Racial-animus interaction pattern consistent with unobserved risk rather than discrimination (R5).
- Minority borrowers report substantially worse service quality: processing/closing delays (R6) and lower satisfaction (R7).
