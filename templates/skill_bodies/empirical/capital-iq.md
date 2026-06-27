## Source
- **S&P Capital IQ (CIQ)** — earnings-call **transcripts** (component-level
  text), Key Developments events, and company financials. On WRDS the data lives
  under the `ciq` / `ciq_transcripts` (and related `ciq_*`) schemas.
- This skill is for the **transcripts** use case: firm-level earnings-call text
  for textual measures (tone, topic, disclosure timing), linked to Compustat via
  `gvkey`.

> **⚠ Licensed, and gated by entitlement.** Capital IQ is a paid S&P product. The
> full `ciq` / `ciq_transcripts` schemas are **not on the default WRDS
> entitlement** used by this pipeline — a live check returns *permission denied*
> on `ciq.wrds_transcript_detail` and `ciq_transcripts.ciqtranscriptcomponent`;
> only `ciqsamp_*` **sample** schemas are readable. So by default you cannot pull
> CIQ transcripts here. Two real paths exist: (a) an **operator-supplied
> pre-built transcript export** placed in `data/` (the normal path for this
> pipeline — see below), or (b) running the WRDS recipe **on an account that is
> entitled to CIQ** (documented below for provenance). Never redistribute CIQ
> data or treat it as a free/public source.

## Working path: an operator-supplied transcript export (take as given)
The pipeline does **not** fetch or host CIQ data. If your project uses Capital IQ
transcripts, the operator places a pre-built export in the project — treat that
file as the source of truth and **do not attempt to re-pull from WRDS**.

- **Expected location:** `data/transcripts/` (e.g. a `*.csv` or, better, a
  converted `*.parquet`). Confirm the file exists before planning a transcript
  measure; if it is absent, the transcript leg is unavailable — say so, don't
  fabricate a WRDS pull.
- **Grain:** one row per **transcript component** (a single speaker turn), not one
  row per call. A call = many components ordered by `componentorder`.
- **Typical columns** (a `wrds_transcript_detail` × `ciqtranscriptcomponent`
  join, already done):

  | Column | Meaning |
  |--------|---------|
  | `gvkey`, `year` | Compustat link + calendar year — the merge keys |
  | `companyid` | CIQ company id |
  | `transcriptid` | one call/transcript |
  | `transcriptcomponentid` | row-level id for the component (speaker turn) |
  | `componentorder` | order of the speaker turn within the call |
  | `transcriptcomponenttypeid` | turn type (presentation vs Q&A vs operator) |
  | `transcriptpersonid` | speaker id (`1` = operator boilerplate) |
  | `componenttext` | the actual spoken text |
  | `mostimportantdateutc` | the call date |
  | `transcriptcreationdate_utc` | when the transcript was created |

- **Semantics already baked into a standard export** (so don't re-impose blindly,
  but know they're there): earnings calls only (`keydeveventtypeid = 48`),
  deduplicated to the **earliest** transcript per `gvkey`×call-date, operator
  turns (`transcriptpersonid = 1`) dropped. If you need raw/duplicate/non-earnings
  data, confirm which export variant you have.

### Loading the export (validated recipe)
The export is **tens of GB** with a free-text field, so loading has three traps —
all handled below. Never `pd.read_csv()` the whole file.

```python
import polars as pl

CSV = "data/transcripts/ConferenceCallsData_all.csv"
# TRAP 1: componenttext has embedded newlines & commas — a real CSV parser is
#         mandatory; line tools (wc -l / awk / sed) mis-split rows.
# TRAP 2: id columns are float-formatted ints ("18749.0"), which break dtype
#         inference — read every id/text column as Utf8, cast later.
IDCOLS = ['transcriptcomponentid','transcriptid','componentorder',
          'transcriptcomponenttypeid','transcriptpersonid','componenttext',
          'companyid','gvkey','year']
schema = {c: pl.Utf8 for c in IDCOLS}

# Stream-filter to your firm set without materializing 15.7 GB (~14s for a few gvkeys):
keep = ['gvkey','year','transcriptid','componentorder','transcriptpersonid',
        'componenttext','mostimportantdateutc']
df = (pl.scan_csv(CSV, schema_overrides=schema)
        .filter(pl.col('gvkey').is_in(my_gvkeys))     # pass your listed-universe gvkeys
        .select(keep)
        .collect(engine='streaming'))

# TRAP 3: gvkey is inconsistently formatted in the export — some zero-padded
#         ('028378'), some not ('63643'), some float-suffixed. Normalize BEFORE
#         joining to Compustat or the merge silently drops rows.
df = df.with_columns(
    pl.col('gvkey').str.replace(r'\.0$','').str.zfill(6).alias('gvkey'))

df.write_parquet("data/transcripts/calls_subset.parquet")   # cache; re-read from here
```

After caching, **aggregate components → call level** (concatenate `componenttext`
ordered by `componentorder` per `transcriptid`, dropping `transcriptpersonid = 1`
operator turns) before joining to a firm-quarter panel.

## WRDS build recipe (for an entitled account only — provenance)
This is how a standard transcript export is produced. It requires a WRDS login
**entitled to Capital IQ**; on the default entitlement every query below returns
permission-denied (use the operator-supplied file instead).

1. **Metadata** from `ciq.wrds_transcript_detail` — keep earnings calls
   (`keydeveventtypeid = 48`), valid `companyid`/`transcriptid`, in-range dates;
   deduplicate to the earliest transcript per company×call-date. (Note: the WRDS
   detail table is keyed on `companyid`/`transcriptid`; the `gvkey` link is added
   via the CIQ↔Compustat crosswalk — it is not a column on
   `wrds_transcript_detail` itself.)
2. **Text** from `ciq_transcripts.ciqtranscriptcomponent`, filtered to the
   selected `transcriptid`s, dropping `transcriptpersonid = 1` (operator), ordered
   by `componentorder`.
3. Merge text to metadata and write out (the result is the export described
   above). Pulling the full component table is heavy — iterate over `gvkey`/
   `transcriptid` batches rather than one unbounded query.

A **direct S&P Capital IQ API** (key-gated, non-WRDS) is the other entitled route;
it is account-specific and out of scope for this skill.

## Gotchas
- **Entitlement first.** Assume CIQ is *not* reachable on WRDS here; the working
  source is the operator file. Don't burn a turn on `ciq_transcripts` — it is
  permission-denied. `ciqsamp_*` exists for shape-checking only.
- **Component grain ≠ call grain.** Aggregate components to a call before
  firm-period analysis; a naive row count counts speaker turns, not calls.
- **Drop operator turns** (`transcriptpersonid = 1`) and decide on
  presentation-vs-Q&A (`transcriptcomponenttypeid`) explicitly for any tone/topic
  measure.
- **gvkey is the link — normalize it or lose rows silently.** In the export
  `gvkey` is inconsistently formatted (zero-padded vs not, sometimes `.0`-
  suffixed floats). Strip `\.0$` and `zfill(6)` before joining to Compustat;
  otherwise the merge drops the unpadded firms with no error. Also confirm
  whether you used the deduplicated (earliest) or all-transcripts variant — they
  give different call counts.
- **Don't use line tools on the export.** `componenttext` contains embedded
  newlines, so `wc -l` / `awk` / `sed` mis-count and mis-split rows — always go
  through a CSV parser with quote handling.
- **Licensed data.** No provenance badge; cite S&P Capital IQ; never commit the
  data or a download link to the repo (it is gitignored under `data/`).

## Rules
- **Take the export as given.** Use the operator-supplied file in `data/`; do not
  fetch, host, or redistribute CIQ data, and do not embed access links.
- **Filter + parquet-cache** before any analysis; never load the full export.
- **Aggregate to call level** (per `transcriptid`) and drop operator turns.
- **State the sample:** export variant (earnings-only? deduped?), date range,
  number of firms/calls, and that the data is licensed S&P Capital IQ.
- **If the file is absent, the transcript measure is unavailable** — report that
  rather than attempting an unentitled WRDS pull.
