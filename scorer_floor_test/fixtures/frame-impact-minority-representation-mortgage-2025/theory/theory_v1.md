# Loan-Officer Soft Information and Minority Mortgage Access

## One-sentence contribution

Minority mortgage borrowers face lower completion, approval, and origination rates and higher default rates when their applications are handled by White loan officers, but these gaps shrink — and the default premium disappears — when the loan officer is also a minority, a pattern consistent with minority officers holding an informational advantage rather than with taste-based favoritism.

## Setup

### Environment

The unit of analysis is a home-purchase mortgage application $i$ opened at a branch office $b$ on day of week $d$ in calendar week $w$ and handled by one loan officer. Each application has a borrower minority indicator $\mathbf{1}\{\text{Minority}\}_i$ and a loan-officer minority indicator $\mathbf{1}\{\text{Minority Officer}\}_i$. Loan-officer race/ethnicity is not directly observed and is imputed (see Proof).

Two competing hypotheses organize the analysis:

- **Hypothesis 1 (information advantage).** Minority loan officers have better soft information about minority borrowers. They can help such borrowers assemble stronger applications, achieve higher approval rates, and originate loans that perform better (lower default).
- **Hypothesis 2 (taste-based discrimination).** White loan officers apply stricter standards to minority borrowers out of taste. This predicts lower approvals *and* lower defaults for White-officer-handled minority loans (a stricter cutoff screens out marginal borrowers).

The two hypotheses are separated by examining approval and default jointly. Information advantage predicts lower approvals *and higher* defaults for White-officer-handled minority loans: if creditworthy minority borrowers are disproportionately excluded, the approved pool selected by a less-informed officer is adversely selected relative to the pool an informed minority officer would select.

## Analysis

### Key result

The main estimating equation is a linear probability model (eq. 2):

$$
Y_i = \beta_1 \mathbf{1}\{\text{Minority}\}_i + \beta_2 \mathbf{1}\{\text{Minority Officer}\}_i + \beta_3 \mathbf{1}\{\text{Minority}\}_i \times \mathbf{1}\{\text{Minority Officer}\}_i + \gamma' X_i + \varepsilon_i \tag{2}
$$

where $Y_i$ is, in turn, application completion, approval (conditional on completion), all-in origination, or default (90+ days delinquent). The parameter of interest is $\beta_3$, the differential effect of a minority loan officer on outcomes for minority versus White applicants. Standard errors are two-way clustered by lender and county.

The estimated signs are: $\beta_1<0$ for completion/approval/origination and $\beta_1>0$ for default (minority borrowers fare worse under White officers); $\beta_3>0$ for completion/approval/origination and $\beta_3<0$ for default (a minority officer narrows or eliminates the gap).

### Proof

This is an empirical identification argument, not a formal proof; the section states the identifying strategy as the draft presents it.

Loan-officer race/ethnicity is inferred with the Bayesian Improved First Name Surname Geocoding (BIFSG) method. For surname $s$, first name $f$, and ZIP code $z$, the posterior probability of race group $r$ is (eq. 1):

$$
p(r \mid s, f, z) = \frac{p(r \mid s)\, p(f \mid r)\, p(z \mid r)}{\sum_{r=1}^{6} p(r \mid s)\, p(f \mid r)\, p(z \mid r)} \tag{1}
$$

with $p(r\mid s)$ from a Census surname list, $p(f\mid r)$ from a first-name-by-race list, and $p(z\mid r)$ from Census ZIP-code demographics; each officer is assigned the modal race group.

Endogenous matching of officers to borrowers is the central identification concern, addressed two ways:

1. **Tight fixed effects.** Branch-year and branch-year-officer fixed effects isolate within-officer, within-branch variation in how the *same* officer treats minority versus White applicants. Under branch-year-officer FE the $\beta_2$ term is absorbed and only $\beta_3$ is identified.
2. **Day-of-week instrument.** For application $i$, the instrument is the share of applications at the same branch and same day of week over the prior 12 weeks handled by minority officers:

$$
Z_{i,b,d,w} = \frac{\#\text{Minority-Officer Applications}_{b,d,\,w-12\to w-1}}{\#\text{Applications}_{b,d,\,w-12\to w-1}}
$$

The first stage (eq. 3) regresses the minority-officer indicator on $Z$ with branch-week FE, day-of-week FE, and controls:

$$
\mathbf{1}\{\text{Minority Officer}\}_{i,b,d,w} = \alpha_{b,w} + \beta Z_{i,b,d,w} + \gamma' \mathbf{X}_{i,b,d,w} + \varepsilon_{i,b,d,w} \tag{3}
$$

First-stage F-statistics exceed 15 across samples, and covariate-balance tests show $Z$ is uncorrelated with borrower age, income, loan amount, FICO, LTV, DTI, and the automated-underwriting recommendation code.

### Economic mechanism

If minority officers acquire or already hold soft information about minority applicants that White officers lack, they can (a) coach applicants toward completion and stronger files, and (b) approve creditworthy minority borrowers a less-informed officer would reject. The joint observation — minority-officer matching *raises* approval/origination while *lowering* default — is the discriminating prediction: a taste-based cutoff would lower both. The information channel implies the White-officer-approved minority pool is adversely selected, so its realized default is higher.

## Comparative statics

Reported directional/heterogeneity results:

- **Approval/origination gap shrinks under minority officers.** $\beta_3>0$: completion gap 1.1 pp smaller; high-discretion approval gap 1.2 pp smaller; origination gap 2.5 pp smaller.
- **Default premium reverses under minority officers.** $\beta_3<0$ for default: the minority default premium is eliminated when the officer is a minority.
- **Effect concentrated in same-race/ethnicity pairings** (triple interaction $+0.008$) and in counties with a high share of non-native English speakers ($+0.005$) and low college share.
- **Effect strongest at small banks, weakest at FinTech lenders**, consistent with FinTech reducing the scope for officer soft information.
- **Minorities are underrepresented among loan officers** (about 15% minority share versus a substantially higher minority share of comparable white-collar professions), with officer minority share rising less than one-for-one with local minority population share.

## Connection to literature

- **Munnell et al. (1996)** — founding documentation of racial disparities in mortgage approval; this draft builds on it by adding loan-officer race as a supply-side explanation.
- **Bhutta, Hizmo & Ringo (2024)** — show the approval gap is largely explained by observed risk factors; this draft extends them by showing the residual gap is explained by the absence of minority officers who supply soft information.
- **Fisman, Paravisini & Vig (2017)** — cultural proximity in credit (Indian banks); this draft extends the cultural-proximity channel to the U.S. mortgage market where hard information and automated underwriting dominate.
- **Ambrose, Conklin & Lopez (2021)** — broker and borrower race affect mortgage cost; this draft extends to loan officers and to approval/origination/default outcomes at market scale.
- **Bartlett et al. (2022)** — FinTech lenders reduce racial disparities; this draft tests that channel, finding the minority-officer effect weakest at FinTech lenders, consistent with less scope for soft information.

## Implications

- Minority applicants are about 1.9 pp less likely to complete applications under White officers; the gap is 1.1 pp smaller under minority officers.
- High-discretion minority applicants are about 2.9 pp less likely to be approved under White officers; the gap is about 1.2 pp smaller under minority officers (about 40% of the gap).
- Minority applications are about 5 pp less likely to originate under White officers; the gap is about 2.5 pp smaller (about 50%) under minority officers.
- Under the day-of-week IV, the high-discretion minority approval gap is 3.6 pp under White officers and the minority-officer interaction fully offsets it.
- In FHA default analysis, minority borrowers with White officers default about 1.7–1.8 pp more than White borrowers with White officers; the minority-officer interaction (−2.2 pp OLS, −5.2 pp IV) eliminates the excess.
- Minority underrepresentation among loan officers therefore reduces minority credit access even in a hard-information-intensive market.
