## Source
- The Paris Club Dataset (1956-2026): Sovereign Debt Restructuring Agreements
- Harvard Dataverse: https://doi.org/10.7910/DVN/BBWLO8 (V2, released 2026-05-18)
- No authentication, no API key, no registration. License CC BY 4.0
- Authors: van der Zaag (Utrecht), van Mourik (NYU), Blackmon (Penn State).
  Scraper source (GPL-3.0): https://github.com/grimelda/openparisclub
- Agreement-level record of every restructuring negotiated through the Paris Club
  of official bilateral creditors: **543 agreements, 102 debtor countries**, first
  agreement 1956-05-16 (Argentina). The headline "USD 863bn treated" is **wrong as
  published** — repair the amounts before using them and you get USD 609bn (first
  gotcha below)
- Built by scraping the `traitements` pages of clubdeparis.org, then hand-cleaned:
  previously unpublished 2022-2024 agreements added manually, the Feb-Oct 2025
  website restructure absorbed (both old and new URLs are carried — `url` plus
  `url_2026` in the tabular/xlsx files, the same new URL named `url_new` in the
  network file)
- Supersedes the Cheng, Diaz-Cassou & Erce (2016) Paris Club dataset: extends it
  through the COVID/DSSI era and adds meeting-level metadata (chairs, debtor
  delegation heads, observers) that no prior dataset carries

## How to use

### Download (whole dataset, ~2.3 MB, no key)
```python
import io, zipfile, urllib.request
import pandas as pd

URL = ("https://dataverse.harvard.edu/api/access/dataset/:persistentId/"
       "?persistentId=doi:10.7910/DVN/BBWLO8")
z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(URL).read()))
z.namelist()
# ParisClub_Data_Tabular.csv, ParisClub_Data_Long.csv, ParisClub_Data_Network.csv,
# ParisClub_Data.xlsx, Methodology.pdf, README.md
```
Cache the extracted files in `data/` after the first fetch and record the
Dataverse version (V2 today) — this is the reproducible artifact, not the live
Paris Club website.

Single files need a numeric datafile id that **changes between dataset
versions** — resolve it, never hardcode it:
```bash
curl -sL "https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/BBWLO8" \
| python3 -c "import json,sys; [print(f['dataFile']['id'], f['dataFile']['filename']) for f in json.load(sys.stdin)['data']['latestVersion']['files']]"
# then https://dataverse.harvard.edu/api/access/datafile/<id>?format=original
```

### The four layouts
| File | Shape | Use |
|------|-------|-----|
| `ParisClub_Data_Tabular.csv` | 545 rows x 43 cols, one row per agreement | the workhorse panel |
| `ParisClub_Data_Long.csv` | 13,644 rows, `url / Debtor / Key / Value` | full free-text fields, machine reading |
| `ParisClub_Data_Network.csv` | 9,666 edges, `source / relationship / target / url / Value (MUSD)` | creditor-debtor-observer network (`Creditor to` 4,996; `Observing nation` 2,895; `Observing institution` 1,775) |
| `ParisClub_Data.xlsx` | 4 sheets (`metadata`, `data_tabular`, `data_long`, `data_network`), types preserved **+ cell notes on manual edits** | the authoritative copy |

### Load and clean the agreement panel
```python
pc = pd.read_csv(z.open("ParisClub_Data_Tabular.csv"))
pc = pc.dropna(subset=["Debtor"])          # 545 -> 543: two rows are entirely blank

def musd(s):                                # amounts ship as strings: "M$ 105.35"
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9.\-]", "", regex=True),
                         errors="coerce")
for c in ["Treatment Amount [MUSD]", "Treatment Canceled [MUSD]",
          "Treatment Rescheduled [MUSD]", "Total External Debt [MUSD]",
          "External Debt due to Paris Club [MUSD]"]:
    pc[c] = musd(pc[c])
pc["date"] = pd.to_datetime(pc["Date of treatment"], errors="coerce")
# 543 agreements, 1956-05-16 -> 2024-08-10
```

### Repair the x100 amount error (do this before any amount analysis)
```python
import re
TXT = re.compile(r"(\d[\d .]*),(\d{1,2})(?!\d)\s*(million|billion)?", re.I)
def from_text(t):                     # value implied by the agreement's own prose
    m = TXT.search(str(t))
    if not m: return None
    v = float(m.group(1).replace(" ", "").replace(".", "") + "." + m.group(2))
    return v * 1000 if (m.group(3) or "").lower() == "billion" else v

implied = pc["Amounts treated"].map(from_text)
bad = implied.notna() & pc["Treatment Amount [MUSD]"].notna() & \
      ((pc["Treatment Amount [MUSD]"] / implied).round(1) == 100.0)
pc.loc[bad, "Treatment Amount [MUSD]"] = implied[bad]   # 41 rows, 2020-05..2022-06
# total treated now USD 609.1bn, not the published 863.4bn
```
The repair is tight, and the check that matters is panel-wide rather than
DSSI-specific — the defect can only arise where the prose uses a decimal comma,
so the question is whether anything outside that set is also wrong. It isn't. Of
the 98 decimal-comma rows the ratio distribution is strictly bimodal at 1.0 and
100.0 (no 10x or 1000x cases). Of the other 445 rows, 18 carry no amount in the
prose at all (`"-"` or blank), 425 match their prose exactly, and the only two
discrepancies are Sierra Leone's sub-$10k DSSI amendments rounding to `M$ 0.00`.
Space-separated (`"$22 073 million"`) and period-decimal (`"$105.35 million"`)
prose parsed correctly throughout.

Two things the repair block does **not** fix:
- **The network file's `Value (MUSD)` carries the same inflated numbers** on all
  41 affected agreements. Repair it the same way (join on `url`) before doing any
  value-weighted network analysis.
- **`Treatment Rescheduled [MUSD]`, `Total External Debt [MUSD]`, and `External
  Debt due to Paris Club [MUSD]`** are populated on exactly one affected row —
  Suriname 2022-06-22 — and that row is corrupted a second way as well: its prose
  reads `"US$ 98,3 million of which being due to Paris Club"`, which was parsed
  into `Total External Debt = M$ 1.00` and `External Debt due to Paris Club =
  M$ 983.00`. Total external debt below the Paris Club share is impossible, so
  check for it directly:

```python
chk = pc[["Total External Debt [MUSD]", "External Debt due to Paris Club [MUSD]"]].dropna()
bad_debt = chk[chk.iloc[:, 0] < chk.iloc[:, 1]]     # 113 pairs populated; 1 violation
```
Drop the NaNs first — both columns are mostly empty, and comparisons against NaN
are False, so the un-dropped version reports violations on clean rows too.

### Creditor-agreement panel
```python
cr = (pc.assign(creditor=pc["Participating creditors"].fillna("").str.split(";"))
        .explode("creditor"))
cr["creditor"] = cr["creditor"].str.strip()
cr = cr[cr["creditor"] != ""]     # 4,996 creditor-agreement rows, 32 distinct creditors
```
This reproduces the `Creditor to` edges of the network file exactly; use the
network file directly if you also want observer edges (IMF 405, World Bank 395,
UNCTAD 354, OECD 310 appearances) — but repair its `Value (MUSD)` first, which
carries the same x100 error.

## Key gotchas
- **41 agreements carry a `Treatment Amount [MUSD]` exactly 100x too large, and
  the dataset's own USD 863bn headline inherits the error.** The Paris Club pages
  write DSSI-era amounts with a European decimal comma (`"$351,60 million"`); the
  scraper stripped the comma on some rows, turning $351.60M into $35,160M. It is
  a bug, not a notation question: of the 98 rows whose prose uses a decimal comma,
  57 were parsed correctly and 41 were multiplied by 100 — the ratio distribution
  is exactly bimodal at 1.0 and 100.0, and the inflated values are absurd on their
  face (Yemen's 2020 DSSI deferral becomes $35bn against ~$7bn of total external
  debt). All 41 fall between 2020-05-15 and 2022-06-22. They contribute $256.9bn
  of the published $863.4bn total but should contribute $2.6bn; corrected, the
  dataset totals **USD 609.1bn** (of which the 444 non-DSSI agreements are
  $604.4bn). That lands next to the USD 610bn the authors' own `Methodology.pdf`
  reports for their 484-agreement pre-DSSI baseline, where the published $863bn
  does not — a magnitude check rather than an identity, since the two agreement
  counts differ. The network file's
  `Value (MUSD)` repeats the same inflated numbers on all 41. Run the repair block
  above before any amount analysis, and never quote 863bn.
- **Amounts are rounded to two decimals in millions, so anything under USD 10k
  reads as `M$ 0.00`** (Sierra Leone's two 2021 DSSI amendments, `"$0,002 million"`
  and `"$0,003 million"`). Zero in an amount column can mean "tiny", not "none".
- **`Treatment Canceled [MUSD]` is populated for only 84 of 543 agreements (0%
  before 1990, 22% after).** Treating missing as zero manufactures a debt-relief
  series that does not exist. Cancellation is only meaningful from the Toronto
  terms (1988) onward — before that virtually every agreement was rescheduling
  only — so pre-1990 blanks are arguably zero, but post-1990 blanks are *unknown*
  and must stay `NaN`. Any "official debt relief" measure built off this column
  needs the missingness stated in the paper.
- **No column is a unique key.** `url` collides for 52 rows (DSSI extensions were
  treated as separate agreements sharing one scraped page, `.../en_3`); `url +
  Date of treatment` still collides for 4 (Yemen 2022-01-13 twice with different
  amounts, Chad 2021-12-03 twice with identical values — the Chad pair looks like
  a genuine duplicate, cross-check the source page). Do **not** blind-`drop_duplicates`;
  drop the two blank rows, keep 543, and use the row index as the agreement id.
- **Amounts are strings (`"M$ 105.35"`), nominal USD, no deflator, missing for 18
  agreements.** Amounts are as reported at agreement date; any cross-decade
  comparison needs an explicit deflator choice, stated. `Methodology.pdf` §5.3
  documents the text-to-numeric conversion as the dataset's largest known weakness
  and asks users to cross-check critical figures against the linked original PDFs —
  the x100 bug above is the instance of that warning you will actually hit, but it
  may not be the only one.
- **Missingness is structural, not random.** Pre-1990 vs post-1990 non-null rates:
  total external debt 0% / 31%, categories of debt treated 8% / 77%, meeting chair
  11% / 31%, cut-off date 35% / 48%. A complete-case regression silently becomes a
  post-1990 regression — report the effective sample.
- **Country names are free text with no ISO codes** (`DEMOCRATIC REP. OF CONGO`,
  `COTE D'IVOIRE`, `KOREA- REPUBLIC OF`), and creditor identity drifts over 70
  years (USSR -> Russian Federation, Yugoslav successors). Merging to WDI / IMF /
  IDS needs a hand-checked crosswalk, not a name join.
- **Coverage is what the Club *treated*, not exposure.** It excludes non-Paris-Club
  bilateral creditors (China above all), and all private/bond restructurings. A
  claim about "official bilateral debt relief" or "sovereign restructuring" from
  this dataset alone is overclaiming — pair with Cruces-Trebesch / Asonuma-Trebesch
  for commercial restructurings and World Bank IDS for stocks, and say what is
  excluded.
- **`Type of treatment` is blank for 64 agreements** and mixes three different
  things: the low-income concessional ladder (Toronto 28, London 26, Naples 47 +
  Naples 50% 6, Lyon 7, Cologne 41, HIPC Initiative Exit 36), the separate
  lower-middle-income Houston track (35), and the non-concessional Classic 175 and
  Ad Hoc 78. Full distribution sums to 543. Houston is *not* a rung on the
  low-income ladder — it lengthens maturities and permits debt swaps without stock
  reduction — and Classic/Ad Hoc are not points on a generosity scale at all.
- **Manual-edit provenance lives only in the xlsx cell notes** — both CSV exports
  drop them. Anything sensitive to a hand-corrected figure should be checked
  against the linked original PDF (`Attached file`).
- **The title says 1956-2026 but the last dated agreement is 2024-08-10.** That
  end date is the scrape/coverage date. Never describe the panel as running to
  2026, and check `Methodology.pdf` §5 before any "as of" claim.
- **Scrape-based, so it is one website redesign from breaking.** Pin the Dataverse
  version; do not re-scrape clubdeparis.org yourself for a marginal update.

## Standard operations
- Creditor participation and G7/OECD composition over time — `CreditorCount`,
  `CreditorCountG7`, `CreditorCountOECD`, `CreditorPc*` are precomputed per agreement.
- Debtor recidivism: agreements per debtor (Senegal 17, DR Congo 16, Togo 16) and
  time between successive treatments as a serial-restructuring measure.
- Terms generosity over time along the low-income ladder: Toronto -> London ->
  Naples -> Lyon -> Cologne -> HIPC Exit; keep Houston (lower-middle-income) as a
  separate track rather than ordering it against them.
- Event studies on `Date of treatment` (spreads, ratings, growth), noting that the
  agreement date is the *signature* date, not the announcement or entry into force.
- Network structure of official lending from `ParisClub_Data_Network.csv`; dedup
  on `(source, relationship, target, url)` first — 569 of the 9,666 edges repeat
  via the DSSI url collisions (115 of them among the 4,996 `Creditor to` edges,
  454 among observer-nation edges).
- Always report the Dataverse version, the row-cleaning rule you applied, whether
  you applied the x100 amount repair, and the missingness of any amount column you
  use. Cite van der Zaag, van Mourik & Blackmon (2026).
