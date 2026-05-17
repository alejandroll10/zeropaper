## Source
- **SCF — Survey of Consumer Finances** (Federal Reserve, triennial
  1989–2022). Cross-sectional household balance sheets: net worth, income,
  IRA/401(k)/DB-pension wealth by age and cohort. Public-use files at
  predictable URLs under `https://www.federalreserve.gov/econres/files/`,
  **no key**. Every survey carries **five multiply-imputed implicates**.
- **HRS — Health & Retirement Study** (RAND HRS Longitudinal File). The
  gold-standard individual-level panel for retirement timing, return-to-
  work, and Social Security claiming (biennial since 1992; rollover events
  need the detailed-pension stems — see the HRS scope limit below).
  **Registration-walled**: free account + data-use agreement +
  bulk download at https://hrsdata.isr.umich.edu. The helper reads a
  user-placed extract; it never fails silently.
- **PSID** is out of scope here (large/complex — issue #5 marks it lower
  priority); use FRED/SCF/HRS for the retirement-and-wealth questions PSID
  would otherwise serve.
- Zero overlap with WRDS/CRSP; both free. Use for retirement timing,
  IRA/401(k) balances by cohort, wealth distribution, and household-finance
  micro-validation (e.g. pairing HRS individual retirement timing with
  macro Bartik shifters from the `bls-census` or
  `form-5500` skills).

## Setup

```python
from utils.hrs_scf_utils import (
    scf_summary, scf_full, scf_replicate_weights,
    scf_combine_implicates, scf_retirement_by_cohort,
    load_rand_hrs, hrs_retirement_panel,
)
```

No keys. Every fetch is memoised to `data/hrs_scf/*.parquet` (CSV fallback
if pyarrow is missing). Public-use SCF years are immutable once released —
cache hits are safe; pass `refresh=True` only to re-pull.

## How to use

### SCF Summary Extract (no key) — start here

```python
df = scf_summary(2022)        # analysis-ready derived variables
# rows = households x 5 implicates; key cols:
#   yy1 (household id), y1 (implicate id = yy1*10+m), wgt (pop weight),
#   age, agecl, networth, income, retqliq (IRA + thrift/401k-type),
#   reteq, irakh, ...
```

`scf_summary(year)` is the file most household-finance papers use (~350
constructed variables). Valid years: 1989, 1992, 1995, 1998, 2001, 2004,
2007, 2010, 2013, 2016, 2019, 2022.

**Retirement-account variables** (the issue-#5 headline; verified present
in the 2022 summary extract — definitions follow the SCF codebook).
`irakh` and `thrift` are **components of `retqliq`** — use `retqliq` for a
total, or the components to decompose; never sum them together:

| Variable | What |
|----------|------|
| `retqliq` | Quasi-liquid retirement: IRA/Keogh + account-type (401k/403b/thrift/SRA) + lump-sum-expected pensions. **The headline retirement-balance field.** |
| `irakh` | IRA + Keogh balances (**a component of `retqliq`**) |
| `thrift` | Account-type pension balances (401k/403b/thrift/SRA), current + past jobs (**a component of `retqliq`**) |
| `reteq` | Total retirement equity (`retqliq` + annuitized / in-pay-status account pensions) |
| `penacctwd` | Withdrawals taken from pension accounts |
| `ssretinc` | Social Security + retirement income (annual flow) |
| `futpen` / `currpen` | Future (not-yet-received) / currently-received pension benefits |
| `anypen` | Has any pension coverage (0/1) |
| `annuit` | Annuity value (not retirement-account specific) |

**Age class** `agecl` (the grouping the cohort helpers use): `1`=<35,
`2`=35–44, `3`=45–54, `4`=55–64, `5`=65–74, `6`=75+. Other categoricals:
`edcl` 1–4 (no-HS / HS / some-college / college), `racecl4` 1–4
(white / black / hispanic / other), `married` 1/2, `lf` 0/1.

### IRA/401(k) balances by cohort (one call)

```python
ret = scf_retirement_by_cohort(2022)            # MI-correct, by age class
# columns: agecl, age_band, retqliq, irakh, thrift, reteq, ...
ret = scf_retirement_by_cohort(2022, vars=["retqliq", "irakh"],
                               stat="mean")
```

This is the headline use case — it pulls `scf_summary`, restricts to the
verified retirement-variable set, computes the implicate-combined statistic
by `agecl`, and attaches the readable `age_band` label. Use it instead of
hand-rolling `scf_combine_implicates` for retirement balances.

### The #1 silent SCF error: implicates and weight scaling

The SCF is multiply imputed — **five implicates** per household, stacked.
The weight `wgt` is constructed so that **summing it over all five
implicates returns the U.S. household population** (~131.3M in 2022).
Summing `wgt` over a *single* implicate returns ~1/5 of the population.

- A weighted **mean or share** over the full stacked file with `wgt` is
  numerically correct as-is — do **not** also divide by 5, and do **not**
  compute it on one implicate.
- A weighted **median / quantile / inequality measure** over the pooled
  stack is **wrong** (these don't commute with stacking). Compute the
  statistic within each implicate and average — use
  `scf_combine_implicates`.

```python
# MI-correct point estimates (computes within each implicate, then averages)
med = scf_combine_implicates(df, ["networth", "retqliq"],
                             by="agecl", stat="median")
mean_nw = scf_combine_implicates(df, "networth", stat="mean")
```

For design-correct **standard errors** the point estimate is not enough —
combine the implicate spread (Rubin's between-imputation variance) with the
SCF bootstrap replicate weights:

```python
rw  = scf_replicate_weights(2022)              # wt1b1..wt1b999 by yy1
full = scf_full(2022, replicates=True)         # full file + replicate cols
```

### SCF Full Public Data Set

```python
full = scf_full(2022)                  # every survey variable (X-coded)
full = scf_full(2022, replicates=True) # merged with replicate weights on yy1
```

Large (~250–290 MB uncompressed) and raw-coded (e.g. `X42001` = raw
weight). Prefer `scf_summary` unless you need a variable the extract omits.

### HRS — RAND HRS Longitudinal File (registration required)

```python
panel = hrs_retirement_panel(version="v2")   # long person x wave panel
wide  = load_rand_hrs(version="v2")          # raw wide RAND HRS file
```

**HRS is registration-walled — this is by design, not a tool limitation.**
To enable it:

1. Register (free) at https://hrsdata.isr.umich.edu, request the **RAND
   HRS Longitudinal File**, accept the data-use agreement.
2. Download + unzip the Stata/SPSS/SAS bundle.
3. Drop the data file (e.g. `randhrs1992_2020v2.dta`) into
   **`data/hrs_scf/hrs/`**.
4. Re-run — the helper reads, caches, and reshapes it.

With no file and no placement, `load_rand_hrs` raises a `RuntimeError`
spelling out these exact steps. **Documented limit:** the HRS host
(`hrsdata.isr.umich.edu`) sits behind CDN bot protection that 403s many
datacenter/cloud IPs even with credentials, so automated download is
unreliable — manual placement is the supported path (same posture as
`ssa.gov` in the `bls-census` skill). This is never a silent failure.

`hrs_retirement_panel()` melts the wide file (RAND stores wave-varying
variables as `r{wave}{stem}` / `h{wave}{stem}`) into a long
`[hhidpn, wave, year, age_years, labor_force, self_rpt_ret, working,
ira_assets, wealth_total, ...]` panel, keeping time-invariant `ra{stem}`
attributes (gender, birth_year, education). `year` is the survey year
(**wave→year: wave 1 = 1992, biennial; wave 15 = 2020** for the V2 file).
Stems absent in your RAND version are **skipped with a printed warning**,
never silently mapped to the wrong column. Override with
`stems={"r": {...}, ...}`.

**Scope limit (documented, not silent):** the shipped stems cover
retirement **timing and stocks** (labour-force status, self-reported
retirement, IRA/pension assets). They do **not** include IRA-**rollover**
/ pension-disposition event variables — those fields are in the HRS
pension and exit modules (and the RAND HRS *detailed pension* files),
**not** the Longitudinal-File curated stems. For rollover analysis,
supply your own `stems=` against a
RAND file that carries them; do not claim rollover results from the
default panel.

## Standard operations

- **Retirement-wealth by cohort (SCF):** `scf_retirement_by_cohort(2022)`
  for the MI-correct IRA/401(k)/pension decomposition across age classes;
  pair with `form-5500` plan-level rollovers and `bls-census` cohort LFPR
  shifters. (Use `form-5500` for the rollover-flow side — SCF/HRS give the
  balance and timing side.)
- **Individual retirement timing (HRS):** `hrs_retirement_panel` →
  hazard of `labor_force`/`self_rpt_ret` transition by age, merged to a
  macro Bartik shifter for the retirement-channel design.
- **Wealth distribution / inequality:** SCF only, and **must** use
  `scf_combine_implicates` (medians and shares of top wealth do not
  commute with implicate stacking) plus replicate-weight SEs.

## Rules
- **SCF is multiply imputed.** State the implicate handling explicitly.
  Means/shares over the stacked file with `wgt` are correct as-is;
  medians/quantiles/inequality require `scf_combine_implicates` (within-
  implicate then averaged). Never divide `wgt` by 5; never compute a
  population total on one implicate.
- **Report SCF standard errors with replicate weights** (`scf_full(year,
  replicates=True)` / `scf_replicate_weights`) plus the between-implicate
  variance — naive SEs understate uncertainty for this dual-frame
  stratified sample.
- **HRS access is registration-walled, by design.** Document in methods
  that the RAND HRS file was obtained under the HRS data-use agreement and
  placed in `data/hrs_scf/hrs/`. Do not claim HRS results without the file
  — the helper raises, it does not fabricate.
- **State your sample.** SCF survey year(s) and product (summary extract
  vs full set); RAND HRS version and waves; weight and implicate handling.
- **Cache aggressively.** Released SCF public-use years are immutable;
  rely on `data/hrs_scf/*.parquet`, pass `refresh=True` only to re-pull.
