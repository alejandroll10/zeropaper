---
title: "Does Saving Cause Borrowing: Medina & Pagel (2025)"
description: >-
  Distilled: A large-scale field experiment with 3.1 million Mexican bank customers
  shows that saving nudges increase savings and reduce spending but leave credit card
  borrowing unchanged, evidence more consistent with self- or partner-control
  explanations for the coholding puzzle than with transactions-convenience models.
  J. Finance 2025, paywalled. Seven core results with source locators, datasets used,
  the conceptual models, and the causal-forest method with its estimating equations.
sidebar:
  label: Medina-Pagel 2025
  order: 1
tags: [paper-summary, household-finance, coholding, nudges, savings, credit-cards,
       behavioral-finance, causal-forests, panel-regression, randomized,
       peer-reviewed, unreplicated, data:banorte-experiment]
paper:
  authors: Paolina C. Medina, Michaela Pagel
  authorList:
    - { family: Medina, given: Paolina C., orcid: "0000-0001-5431-8565", affiliation: C.T. Bauer College of Business, University of Houston }
    - { family: Pagel, given: Michaela, orcid: "0000-0002-6536-1312", affiliation: Washington University in St. Louis, Olin Business School }
  year: 2025
  venue: The Journal of Finance 80(5), October 2025, 2689–2738
  venueShort: J. Finance 2025
  doi: 10.1111/jofi.13466
  jel:
    codes: [D14, G51, C93]
    assignedBy: claude-sonnet-4-6
    date: 2026-06-05
  topics:
    - Financial Literacy, Pension, Retirement Analysis
    - Housing Market and Economics
    - Decision-Making and Behavioral Economics
  dataAccess: proprietary-confidential
  outcome:
    - monthly credit card interest charges
    - checking account balance (savings)
    - monthly spending (ATM withdrawals, card spending, transfers)
    - probability of rolling over credit card debt
  outcomeClass: [household-finance]
  license: >-
    Paywalled (Wiley VOR terms and conditions; license[].content-version=vor,
    URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0,
    start=2025-07-02; no CC licence found in Crossref metadata)
  licenseShort: paywalled
  access: paywalled
  machineAccess: blocked-paywall (Wiley site; confirmed from Crossref DOI metadata 2026-06-05)
  redistribution: extract-only
  resultsCount: 7
  citedByCount: 3
  methods:
    role: both
    family: reduced-form-causal
    buildsFrom: [panel-regression, causal-forest]
    identification: randomized
  contributionType: [new-fact, new-method, new-theory]
  mechanisms: [behavioral-bias, participation-frictions, self-partner-control]
  introducesData: true
  scope:
    region: Mexico
    assetClass: household checking accounts and credit cards
    period: 2019-09..2019-11
    frequency: monthly
    dataType: [administrative, market]
    granularity: [individual, transaction]
    n: "3,054,503 individuals (experimental pool); 362,223 with a credit card"
  findings:
    - ref: R1
      outcome: monthly spending
      metric: pp-effect
      value: "-0.8% (full sample, p<0.05); -1.9% (credit card holders, p<0.01)"
      direction: negative
      vsBenchmark: reduction from base of 17,870 MXN (full sample) and 31,998 MXN (credit card holders)
    - ref: R2
      outcome: checking account balance (savings)
      metric: pp-effect
      value: "+0.6% (full sample, p<0.01); +1.1% (credit card holders, p<0.05)"
      direction: positive
      vsBenchmark: increase from base of 19,913 MXN (full sample) and 35,657 MXN (credit card holders)
    - ref: R3
      outcome: monthly credit card interest charges
      metric: pp-effect
      value: "-0.20% (coeff -0.002, SE 0.008, p insignificant); 95% CI rules out increases >1.4% or decreases >1.8% (Table IV Panel B)"
      direction: none
      vsBenchmark: "null effect on aggregate borrowing; less than 21% of the spending reduction reflected in reduced credit card debt (less than 16% in new debt)"
    - ref: R4
      outcome: monthly spending
      metric: pp-effect
      value: "-7.22% (top quartile of predicted treatment effects, N=150,177; base 34,969 MXN)"
      direction: negative
      vsBenchmark: top-quartile subgroup via causal forest; corresponds to 2,524 MXN decrease
    - ref: R5
      outcome: checking account balance (savings)
      metric: pp-effect
      value: "+4.93% (top quartile of predicted treatment effects; base 39,174 MXN)"
      direction: positive
      vsBenchmark: corresponds to 1,932 MXN increase; 95% CI rules out borrowing increases/decreases of more than 11.23 MXN (6.98 MXN)
    - ref: R6
      outcome: monthly credit card interest charges
      metric: pp-effect
      value: "-1.01% (SE=2.21%, p insignificant); upper CI 6.98 MXN; less than 14% of spending reduction reflected in interest"
      direction: none
      vsBenchmark: null effect holds in top quartile of spending predicted treatment effects and in top quartile of saving predicted treatment effects
    - ref: R7
      outcome: monthly spending
      metric: pp-effect
      value: "Message 4 (money-box/lock-away message): -9.0% on spending (p<0.01), +6.9% on savings (p<0.01); significantly larger than short-term and long-term message groups at 10% level"
      direction: negative
      vsBenchmark: Message 4 outperforms short-term and long-term message categories; borrowing null for all individual messages (Table VIII)
  resultType: new-finding
  relatesTo:
    - { cite: "Gross and Souleles (2002)", doi: '10.1162/003355302753399472', relation: builds-on, note: "first documentation of the coholding puzzle in US data; this paper seeks to identify the mechanisms behind it" }
    - { cite: "Telyukova (2013)", relation: tests, note: "transactions-convenience model predicts decreased borrowing when patience rises; empirical results are inconsistent with that prediction" }
    - { cite: "Bertaut, Haliassos, and Reiter (2009)", doi: '10.1093/rof/rfn033', relation: tests, note: "self- or partner-control model predicts less comovement between saving and borrowing; results are more consistent with this channel" }
    - { cite: "Druedahl and Jorgensen (2018)", doi: '10.3982/qe604', relation: tests, note: "credit-limit-chasing model yields same predictions as transactions-convenience model; both are inconsistent with the null borrowing effect" }
    - { cite: "Gorbachev and Luengo-Prado (2019)", doi: '10.1162/rest_a_00752', relation: tests, note: "credit-limit-chasing model; similarly inconsistent with the observed null borrowing response" }
    - { cite: "Athey, Tibshirani, and Wager (2019)", doi: '10.1353/obs.2019.0001', relation: builds-on, note: "causal forests used for heterogeneous treatment effect prediction and overfitting-safe subgroup selection" }
    - { cite: "Beshears et al. (2022)", relation: contradicts, note: "automatic 401(k) enrollment raises credit card debt; in contrast, informational nudges here do not increase borrowing" }
    - { cite: "Beshears et al. (2024)", doi: '10.3386/w32100', relation: contradicts, note: "pension auto-enrollment raises unsecured and mortgage debt; informational nudges in this paper leave borrowing unchanged" }
    - { cite: "Gathergood and Olafsson (2024)", doi: '10.1093/rfs/hhae016', relation: cites, note: "transaction-level evidence on coholding prevalence and persistence in Iceland" }
  openQuestions:
    - "Whether the treatment's effects on saving and spending would persist beyond the seven-week intervention window; the paper cannot determine whether the preference shock from the nudge is permanent or temporary (p. 2728)."
    - "Whether the increase in savings among credit card holders comes from individuals who were already saving (intensive margin of coholding) or from those newly starting to save (extensive margin); Tables IA.IV and IA.V provide suggestive but not definitive evidence (p. 2723)."
    - "Whether treating only the most responsive individuals (top 5% of predicted treatment effects) would result in different policy conclusions from the perspective of the government (not just the bank), since profit-maximizing targeting and social-welfare targeting may conflict (p. 2734)."
  replicationCode:
    status: available
  extraction:
    - by: paper-distiller (claude-sonnet-4-6)
      date: 2026-06-05
      role: extracted
      note: >-
        Full text read (pp. 2689-2738); seven results extracted from the PDF.
        Not human-verified. Not reproduced. Replication code referenced in
        supporting information but not run here.
    - by: paper-verifier (claude-sonnet-4-6)
      date: 2026-06-05
      role: verified
      note: "Locators and reported magnitudes re-checked against the source PDF; two fixes applied: (1) methods.buildsFrom corrected from [panel-regression, instrumental-variables] to [panel-regression, causal-forest] (no IV design in this paper); (2) R3 findings[].value corrected from the Table V subgroup estimate (-1.01%, SE 2.21%) to the Table IV aggregate estimate (-0.20%, coeff -0.002, SE 0.008) and vsBenchmark corrected from <14% to <21% (aggregate claim, p. 2712). All other locators, magnitudes, equations, and classification axes verified correct against the PDF."
  licenceVerification:
    - source: Crossref REST API works/10.1111/jofi.13466
      checked: 2026-06-05
      by: paper-distiller (claude-sonnet-4-6)
      found: "license[].content-version=vor, URL=http://onlinelibrary.wiley.com/termsAndConditions#vor, delay-in-days=0, start=2025-07-02; no Creative Commons licence found"
  rightsSignalConflict: false
---

**What this is.** The paper's core results, the theoretical frameworks it tests (transactions-convenience and self/partner-control models), and the causal-forest method with its estimating equations: enough to know what it found and how, without reading the full 50 pages. To replicate or extend it, read the original at [doi.org/10.1111/jofi.13466](https://doi.org/10.1111/jofi.13466).

## TL;DR

Using a randomized field experiment in which 3.1 million customers of Mexican bank Banorte were sent SMS saving nudges for seven weeks, this paper asks whether encouraging savings causes individuals to also borrow more. The authors first develop two classes of theoretical models (transactions-convenience and self/partner-control) and show they make distinguishable predictions about the joint responses of spending, saving, and borrowing to a patience shock. Using causal forests to handle treatment effect heterogeneity, the most responsive individuals (top quartile) reduce monthly spending by 7.2% (roughly 2,524 MXN) and increase checking account balances by 4.9% (roughly 1,932 MXN). However, credit card interest charges change by a precisely estimated zero: less than 14% of the spending reduction is reflected in lower credit card interest payments, and the confidence interval rules out a borrowing increase of more than 11 MXN for every 1,932 MXN saved. This null borrowing response is more consistent with self- or partner-control models than with transactions-convenience models, and it implies that saving nudges exacerbate coholding of low-interest savings and high-interest debt.

## Core results

Magnitudes and significance are as reported. All treatment effects are proportional (exp(beta)-1), estimated via Poisson regression with strata fixed effects and robust standard errors. Locators point into the source PDF.

| # | Result | Locator | Magnitude |
|---|---|---|---|
| R1 | Saving nudges **reduce spending** for all subjects and for credit card holders | Table IV, Panels A and B, p. 2713 | Full sample: -0.8% from base 17,870 MXN (\*); credit card holders: -1.9% from base 31,998 MXN (\*\*\*) |
| R2 | Saving nudges **increase checking account balances** (savings) | Table IV, Panels A and B, p. 2713 | Full sample: +0.6% from base 19,913 MXN (\*\*); credit card holders: +1.1% from base 35,657 MXN (\*\*) |
| R3 | **Borrowing is unchanged**: monthly credit card interest is a precisely estimated zero for the whole sample | Table IV, Panel B, col. (3), p. 2713 | -0.002, SE 0.008, base 215.91 MXN; upper CI rules out increase >1.4% or decrease >1.8% |
| R4 | In the top quartile of predicted spending treatment effects, **spending falls 7.22%** | Table V, Panel A, col. (1), p. 2718 | -7.22%\*\*\* (SE 1.33%) from base 34,969 MXN; decrease of ~2,524 MXN; N=150,177 |
| R5 | In the same subgroup, **savings rise 4.93%** | Table V, Panel A, col. (2), p. 2718 | +4.93%\*\*\* (SE 1.28%) from base 39,174 MXN; increase of ~1,932 MXN |
| R6 | **Credit card interest is a null in the high-response subgroup**: upper CI rules out more than 6.98 MXN increase per cycle; null holds also for the top savings quartile | Table V, Panel A, col. (3); Table VI, Panel A, col. (3), pp. 2718, 2721 | -1.01% (SE 2.21%), base 210 MXN; <14% of spending reduction reflected in lower interest; null for rolled-over debt and payments |
| R7 | **Message 4 (mental accounting/lock-away) produces the largest effects** on spending and saving; borrowing is null for every individual message | Table VIII, pp. 2726, and p. 2727 | Msg 4: -9.0%\*\*\* spending (SE 2.3%), +6.9%\*\*\* savings (SE 2.4%), -0.6% interest (SE 2.8%, insignificant); significantly larger than short-term and long-term pooled at 10% |

**Overall (paper's conclusion).** Saving nudges increase savings and reduce spending among the most responsive individuals, but the additional savings are not used to repay credit card debt; the null effect on borrowing is consistent with self- or partner-control explanations for coholding and inconsistent with predictions from transactions-convenience or credit-limit-chasing models. This contrasts with automatic enrollment interventions studied by Beshears et al. (2022) and Beshears et al. (2024), where pension auto-enrollment raises credit card and mortgage debt; the absence of such an offset here aligns with Gathergood and Olafsson (2024), who document that most coholding is modest and relatively short-lived. The causal-forest approach also illustrates that traditional strata-based heterogeneity analysis is subject to severe overfitting bias, overstating borrowing reductions by more than an order of magnitude.

## Theory / model

The paper develops two classes of two-period conceptual frameworks to map theoretical predictions onto empirical moments and formalize the hypothesis tests. No formal structural estimation is performed; the models are used to derive the sign of comparative statics that the experiment can test. The coholding puzzle was first documented by Gross and Souleles (2002). The liquidity-premia class encompasses the transactions-convenience model of Telyukova (2013) and the credit-limit-chasing models of Druedahl and Jorgensen (2018), Gorbachev and Luengo-Prado (2019), and Fulford (2015). The self-or-partner-control class follows Bertaut, Haliassos, and Reiter (2009) and Vihriala (2019).

**Liquidity-premia model (transactions convenience).** An agent allocates initial endowment $$x_1$$ to period-1 consumption $$c_1$$ and is required to carry a minimum cash amount $$x$$ for transaction purposes. Borrowing $$b_1$$ is available at interest rate $$r$$. The period-1 maximization problem (p. 2695) is:

$$
\max_{c_1} \{ \log(c_1) + \delta \log(x_1 - c_1 - r b_1) \} \tag{Transactions model}
$$

where $$b_1 := f_{b_1}(c_1) = \begin{cases} c_1 - x_1 + x & \text{if } c_1 - x_1 + x > 0 \\ 0 & \text{otherwise} \end{cases}$$ and $$\delta \in (0,1)$$ is the discount factor. The agent coholds when

$$
x_1 - \frac{1}{\delta+1} x_1 + \frac{r}{(\delta+1)(1+r)} x < x \tag{1}
$$

and the optimal consumption and borrowing satisfy $$c_1^* = \frac{1}{\delta+1} x_1 - \frac{r}{(\delta+1)(1+r)} x$$ and $$b_1^* = c_1^* - x_1 + x$$.

Proposition 1 (p. 2695): if agents cohold and become more patient (higher $$\delta$$), consumption decreases and debt decreases by the same amount: $$\frac{\partial b_1^*}{\partial \delta} = \frac{\partial c_1^*}{\partial \delta} < 0$$. Proposition 2 (p. 2696): if cash needs $$x$$ increase, borrowing increases by almost the same amount: $$\frac{\partial b_1^*}{\partial x} = 1 - \frac{r}{(\delta+1)(1+r)} > 0$$. Thus in any liquidity-premia or credit-limit-chasing model, saving nudges interpreted as a patience shock predict lower spending AND lower debt, while cash-need shocks predict higher debt.

**Self- or partner-control model.** A patient party (discount factor $$\delta$$) hides an amount $$x \geq 0$$ from an impatient party (discount factor $$\beta \in (\beta, \delta)$$). The impatient party perceives their period-1 endowment as $$x_1 - ax$$, where $$a \in (0,1]$$ is the fraction of hidden cash that is invisible to them. The impatient party maximizes (p. 2698):

$$
\max_{c_1} \{ \log(c_1) + \beta \log(x_1 - ax - c_1 - r b_1) \} \tag{Self-control model}
$$

subject to $$b_1 := f_{b_1}(c_1) = \begin{cases} c_1 - x_1 + x & \text{if } c_1 - x_1 + x > 0 \\ 0 & \text{otherwise} \end{cases}$$. If the impatient agent coholds, optimal consumption is $$c_1^* = \frac{1}{\beta+1} x_1 - \frac{r+a}{(\beta+1)(1+r)} x$$ and borrowing is $$b_1^* = c_1^* - x_1 + x$$.

The patient party chooses $$x$$ to maximize $$\max_x \{ \log(f_{c_1^*}(x)) + \delta \log(x_1 - f_{c_1^*}(x) - r f_{b_1^*}(x)) \}$$. The coholding condition is:

$$
x_1 - x_1 \frac{1}{1+\delta} \left( \delta \frac{1+r}{r+a} - \frac{\beta + r\beta}{a - r\beta} \right) - \frac{1}{\beta+1} x_1 + \frac{r+a}{(\beta+1)(1+r)} x_1 \frac{1}{1+\delta} \left( \delta \frac{1+r}{r+a} - \frac{\beta+r\beta}{a-r\beta} \right) < 0 \tag{2}
$$

and the optimal hidden cash is $$x^* = x_1 \frac{1}{1+\delta} \left( \delta \frac{1+r}{r+a} - \frac{\beta+r\beta}{a-r\beta} \right)$$.

Proposition 3 (p. 2699): if the patient self becomes more patient (higher $$\delta$$), hidden assets increase ($$\frac{\partial x^*}{\partial \delta} > 0$$) and if the impatient self becomes more impatient (lower $$\beta$$), hidden assets also increase ($$\frac{\partial x^*}{\partial \beta} < 0$$). Proposition 4 (p. 2700): if the patient self increases hidden assets $$x$$, the impatient party's consumption decreases, especially when more assets can be hidden ($$\frac{\partial c_1^*}{\partial x} < 0$$ and $$\frac{\partial^2 c_1^*}{\partial x \partial a} < 0$$), while the sensitivity of borrowing to hidden cash is $$\frac{\partial b_1^*}{\partial x} = \frac{\partial c_1^*}{\partial x} + 1$$, which is less than one and can be near zero if $$\frac{\partial c_1^*}{\partial x} \approx -1$$.

The key distinguishing prediction: in the self- or partner-control model, a nudge that increases patience or hidden cash raises savings but produces far less comovement between saving and borrowing (slope of borrowing on savings ranges from 0.55 to 0.77 across calibrations) than the transactions-convenience model (slope always close to one).

## Method

The identification design is a large-scale randomized controlled trial at Banorte, a top-five Mexican bank. From a pool of 3,054,503 customers meeting three eligibility requirements (payroll account, average daily balance at least 50 MXN over two prior months, valid cell phone), 357,567 were randomly assigned to a control group. The remaining 2,696,936 were assigned to one of seven saving-nudge SMS messages sent bi-weekly over seven weeks (September 13 to November 1, 2019). Randomization was stratified on income quartile, age quartile, bank tenure, baseline savings, digital-banking dummy, ATM transaction median, credit card dummy, and debit card transaction terciles, balancing on 161 pretreatment variables (Table IA.I).

**Aggregate treatment effects.** The primary estimating equation (equation 3, p. 2711) is a Poisson regression for proportional effects:

$$
Y_i = \exp\{\alpha_s + \beta \cdot \text{treatment}_i + \epsilon_i\} \tag{3}
$$

where $$\alpha_s$$ are randomization-block fixed effects, $$\text{treatment}_i$$ is a dummy for receiving any of the seven messages, and $$\beta$$ yields proportional treatment effects $$\exp(\beta) - 1$$. Following Chen and Roth (2024) and Cohn, Liu, and Wardlaw (2022), this handles zero outcomes consistently. For binary variables, a linear probability model is used. Robust standard errors throughout.

**Heterogeneous treatment effects via causal forests.** To avoid overfitting when searching for the most responsive subgroup, the paper applies generalized random forests following Athey, Tibshirani, and Wager (2019). For each of the three outcomes (spending, savings, borrowing), a pilot forest with 2,000 trees is trained on all 161 pretreatment variables; a second forest is trained on variables with importance above 1%. Treatment heterogeneity is tested using the Chernozhukov et al. (2018) calibration test. Cross-fitted rankings over five folds assign each observation to a quartile of predicted treatment effects, and actual treatment effects are estimated using Poisson regression within each quartile. The test detects significant heterogeneity for spending and saving but no heterogeneity for borrowing across all subgroups, supporting the null effect on credit card debt.

## Empirical specifications

**Main specification (aggregate effects, Table IV).** Equation (3) is estimated for monthly spending (ATM withdrawals + card transactions + transfers), checking account balance (average daily balance), and monthly credit card interest charges. For credit card outcomes, the dependent variable is the average of interest charges over the two billing cycles intersecting the treatment window (September and October 2019); a robustness check uses November and December cycles for carryover effects. The specification includes strata fixed effects; robust standard errors are clustered at the individual level. Sample: all 3,054,503 individuals (Panel A), 362,223 credit card holders (Panel B), 152,016 individuals with a credit card who paid interest at baseline (Panel C).

**High-response subgroup specification (Tables V and VI).** Equation (3) is re-estimated within the top quartile of the distribution of predicted treatment effects on spending (N=150,177) or saving (N=151,834), identified by the causal forest. This is the horse race: do those who most reduce spending or increase savings show any change in borrowing? The confidence intervals are compared directly to the spending/saving changes to bound the fraction of the saving/spending effect that could be explained by debt.

**Spending composition (Table VII).** The spending reduction is decomposed into deposits, ATM withdrawals, card spending, and outgoing transfers, with the same Poisson specification. About half of the reduction comes from ATM withdrawals (consistent with hiding cash from family sharing pressures) and half from card spending.

**Message-level specification (Table VIII).** Equation (3) is run separately for each of the seven messages, then messages are grouped into short-term, long-term, and mental-accounting (Message 4) categories. Differences in effects across categories are tested via interaction terms.

**Overfitting illustration (Table X).** The sample is divided into 6,104 strata-blocks. Treatment effects on spending are computed per block, then the top quartile of blocks (by treatment effect) is identified. Causal forest estimates for the same top-quartile subgroup are compared to the block-sorted estimates to show that the block-sort inflates the spending reduction from 7% to 38% and spuriously shows decreased borrowing.

All specifications use robust standard errors. No clustering by branch or region (individual-level randomization). Winsorization at 1st and 99th percentiles for continuous variables; credit card balances, interest charges, and credit limits winsorized only for credit card holders.

## Datasets used

| Dataset | Role in paper | Wiki page |
|---|---|---|
| Banorte proprietary bank-account panel | Checking account balances, credit card interest charges, transaction-level spending (ATM, card, transfers), credit card balance and limit, deposits, payments; 161 pretreatment variables | No page yet |
| Banorte credit bureau pulls (bimonthly) | Non-Banorte credit card balances for substitution check; aggregate credit exposure | No page yet |
| OECD PPP conversion rates (2019) | Convert MXN to USD PPP for reporting; 1 MXN = 0.107 USD PPP | No page yet |

Sample: 3,054,503 individual bank customers at Banorte, Mexico; experiment conducted September 13 to November 1, 2019 (seven weeks). Credit card subsample: 362,223 holders; interest-paying subsample: 152,016. All financial variables measured in Mexican Pesos (MXN); 1 MXN = 0.107 USD PPP.

## When to read the full paper

Read the [original](https://doi.org/10.1111/jofi.13466) if you are:
- building or testing models of the coholding puzzle in other settings (the theoretical framework in Section I with Propositions 1-4 is the formal foundation);
- applying causal forests to heterogeneous treatment effects in large RCTs (Sections II.D and III.F provide the most detailed methodological discussion and the overfitting comparison);
- studying the effectiveness of saving nudges or SMS-based financial interventions, especially unintended balance-sheet effects;
- replicating or extending the empirical results (the Internet Appendix contains additional robustness tables IA.I through IA.XII referenced throughout).

## Attribution and rights

Source: peer-reviewed, *The Journal of Finance* 80(5), October 2025, pp. 2689-2738. DOI: 10.1111/jofi.13466. This distillation was extracted by an LLM (claude-sonnet-4-6) on 2026-06-05 and is **not human-verified or independently reproduced**. The paper is paywalled; no CC licence was found in Crossref metadata. Extract-only: no PDF is hosted here.

> Medina, Paolina C., and Michaela Pagel. "Does Saving Cause Borrowing? Implications for the Coholding Puzzle." *The Journal of Finance* 80, no. 5 (October 2025): 2689-2738. DOI: 10.1111/jofi.13466. Published by Wiley on behalf of the American Finance Association. All rights reserved.
