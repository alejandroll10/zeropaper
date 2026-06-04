## Source
- SEC **Form ADV** via **IAPD** (Investment Adviser Public Disclosure) —
  free, public, no API key. The registration form every SEC- or
  state-registered investment adviser must file.
- **Not on EDGAR.** Advisers file through the IARD/CRD system, so Form ADV has
  its own identifiers (CRD numbers, `801-`/`802-` file numbers) and its own
  access points. A CIK lookup on `data.sec.gov` returns nothing.
- Home: <https://adviserinfo.sec.gov/> ·
  Bulk data: <https://www.sec.gov/foia-services/frequently-requested-documents/form-adv-data>
- A descriptive `User-Agent` header is courteous and avoids throttling, same as
  EDGAR. Build it from `SEC_EDGAR_NAME` + `SEC_EDGAR_EMAIL` in `.env`.

Use Form ADV for what an adviser *is*: regulated assets under management,
client/employee counts, private-fund details, ownership, disciplinary history,
and a narrative brochure of strategies and fees. It is the standard source for
classifying advisers (hedge-fund vs mutual-fund adviser, private-fund flags).

## How to use

### Option 1 — IAPD firm report (one adviser, PDF)

Every registered firm has a public report addressed by its **CRD number**:

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()
headers = {"User-Agent": f"{os.getenv('SEC_EDGAR_NAME','Research')} "
                         f"{os.getenv('SEC_EDGAR_EMAIL','research@university.edu')}"}

crd = 105631   # Bridgewater Associates
pdf = requests.get(
    f"https://reports.adviserinfo.sec.gov/reports/ADV/{crd}/PDF/{crd}.pdf",
    headers=headers,
)   # 200, application/pdf: the full Form ADV Parts 1 and 2 (human-readable)
```

### Option 2 — Search API (resolve a name to a CRD)

CRD is the join key, so most pipelines start by resolving a firm name:

```python
url = ("https://api.adviserinfo.sec.gov/search/firm"
       f"?query={name}&hl=true&nrows=12&start=0&wt=json")
r = requests.get(url, headers=headers).json()
# Returns matching firms with CRD, SEC number, and location.
# Parallel /search/individual endpoint exists for adviser representatives.
```

### Option 3 — Bulk structured data (the whole population)

For panel work, the SEC publishes the **structured Part 1 data** (check-box
and numeric fields, including Schedule D private-fund rows) as downloadable
archives, plus monthly Part 2 brochure dumps, on the FOIA page:

```
https://www.sec.gov/files/adv-filing-data-20111105-20241231-part1.zip   # ~700 MB
https://www.sec.gov/files/adv-filing-data-20001019-20111104.zip
```

The complete-filing-data archives give every adviser's Part 1 fields over
time — the right tool for classification at scale, rather than scraping PDFs
one CRD at a time.

## What's in each part

| Part | Form | Contents |
|------|------|----------|
| 1A | structured | RAUM, client/employee counts, custody, ownership, disciplinary, Schedule D (incl. private funds) |
| 1B | structured | State-registration items |
| 2A | brochure (PDF) | Narrative: advisory business, fees, strategies, conflicts |
| 2B | supplement (PDF) | Background of individual advisory personnel |
| 3 | Form CRS | Relationship summary for retail clients |

## Gotchas (the ones that bite pipelines)

- **Not on EDGAR; CRD, not CIK.** Form ADV uses CRD/IARD identifiers and
  `801-`/`802-` SEC file numbers. There is no CIK and no `data.sec.gov`
  endpoint. Join to EDGAR-based holdings (13F, N-1A) by name or a hand-built
  CRD↔CIK map, not by a shared key — and document the crosswalk.
- **AUM is regulated AUM (RAUM), gross.** Part 1 Item 5.F reports *regulated*
  assets under management: gross of leverage, including uncalled capital
  commitments for private-fund advisers. It is **not** net AUM and is not
  directly comparable to a 13F dollar value.
- **Three registration regimes, different coverage.** SEC-registered advisers
  (generally >$100M RAUM), **state-registered** advisers (smaller, file with
  states), and **exempt reporting advisers** (ERAs — some private-fund and VC
  advisers) who file only a truncated Form ADV. Do not assume the
  SEC-registered set is the whole universe.
- **Private funds live in Schedule D Section 7.B.1:** one row per reported
  private fund, with a self-classified fund type (hedge fund, private equity,
  etc.). The type is the adviser's own label — treat it as a self-report.
- **Part 2 is prose, not fields.** The brochure (2A) and supplement (2B) are
  narrative PDFs. Strategy, fee, and conflict classification means parsing
  text, not reading a tagged field.
- **Self-reported and as-of the latest amendment.** The live IAPD report shows
  the *current* filing. Advisers must file an annual updating amendment within
  90 days of fiscal year-end, so the "current" report can be up to a year+90
  days stale. For a point-in-time history use the dated bulk archive or
  compilation reports — the live report is current-only and not reproducible
  as history.
- **Bulk filenames embed date ranges.** Archive filenames carry the period they
  cover (e.g. `...20111105-20241231-part1.zip`), so a hard-coded URL goes stale
  as the SEC adds periods. Re-read the FOIA page for current filenames.
- **One adviser advises many funds.** A fund-classification join is
  adviser→funds, often many-to-many; a single ADV does not map one-to-one to a
  mutual fund. Cross-reference fund-level filings (EDGAR N-1A) for the fund side.

## Standard recipes

### Classify advisers/funds at scale
Resolve name → CRD (Option 2), then read Schedule D and Item 5 / Item 7 from
the bulk Part 1 data (Option 3) rather than scraping PDFs — the structured
fields are the classifiable signal.

### Build a point-in-time panel
Use the dated bulk archives for as-of fields; the live IAPD report is
current-only. Always record the **CRD and the as-of date** of the filing you
read — ADV is amended continuously, so an undated pull is not reproducible.

### Link to holdings or returns
Map CRD to the EDGAR CIK (by name) to link an adviser's ADV profile to its 13F
/ N-1A filings (`edgar` skill). There is no shared key, so document the
crosswalk explicitly.

## Rules
- **Credentials/identity only in `.env`** (`SEC_EDGAR_NAME` / `SEC_EDGAR_EMAIL`
  for the User-Agent); never hardcode.
- **RAUM ≠ net AUM.** Always state that the AUM figure is gross regulated AUM.
- **State your sample.** Report registration regime(s) covered, the as-of /
  date range, # advisers, and any CRD↔CIK crosswalk used.
- **Cite the form, adviser, CRD, and source.** E.g. *Bridgewater Associates,
  LP, Form ADV, CRD No. 105631, U.S. SEC, Investment Adviser Public Disclosure
  (IAPD), accessed YYYY-MM-DD.*
