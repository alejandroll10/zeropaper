## Source
- Meta (Facebook) Social Connectedness Index (SCI), distributed via the
  Humanitarian Data Exchange (HDX)
- HDX dataset: https://data.humdata.org/dataset/social-connectedness-index
- No authentication, no API key (some sub-files are Google Drive links)
- Paper: Bailey, Cao, Kuchler, Stroebel & Wong, "Social Connectedness:
  Measurement, Determinants, and Effects", JEP 2018, 32(3):259-280
- Snapshot per release (not a panel) — the index measures the relative
  probability of a Facebook friendship link between two areas

## How to use

**Finding the download links.** HDX assigns each resource a per-upload UUID, so
there is no stable hand-writable CSV URL. WebFetch the dataset page
(https://data.humdata.org/dataset/social-connectedness-index) and read the
`download` links for the resource you want (`country.csv`, `us_counties.csv`,
etc.), or download them from the page in a browser. Cache everything in `data/`
after the first fetch — the files are large and the host is slow. GADM2 and
ZCTA-level files are Google Drive links on the same page — fetch those manually.

### Country-to-country (small)
```python
import pandas as pd
df = pd.read_csv("data/country.csv")   # 31,684 data rows
# Columns: user_country, friend_country, user_region, friend_region, scaled_sci
```

### US county-to-county (large, ~245 MB)
```python
df = pd.read_csv("data/us_counties.csv")   # 10,265,616 rows
# user_region / friend_region are 5-digit FIPS county codes
```

## Key gotchas
- **`scaled_sci` is a rescaled relative measure, not a count or probability.**
  Each file is rescaled so its own maximum equals 1e9. Use it for relative
  comparisons *within* a file only.
- **NOT comparable across files or vintages.** The per-file max rescaling means
  county-level values and country-level values (or two different release dates)
  are on different scales — never pool or compare raw `scaled_sci` across files.
- **Symmetric, both directions stored.** Each area pair appears as (A,B) and
  (B,A); dedup if you need unique pairs.
- **Diagonal included and dominates.** Self-pairs (user_region == friend_region)
  are present and are by far the largest values (within-area connectedness). Drop
  the diagonal for any between-area analysis or it swamps the distribution.
- **Region codes differ by file** — 5-digit FIPS for US counties, GADM codes for
  the GADM2 file, ZCTA for the ZIP file, ISO-style country codes for `country.csv`.
  Check the columns per file before merging.
- **Snapshot, not a panel** — a single cross-section per release; do not treat
  multiple downloads as a time series without confirming methodology consistency.

## Standard operations
- Social-distance / exposure measures: SCI-weighted average of a remote-area
  variable (e.g. SCI-weighted local shock as an out-of-region exposure
  instrument), after dropping the diagonal.
- Network controls: normalize each origin area's `scaled_sci` row to sum to 1 to
  get connection shares before weighting.
- Always report which file/vintage you used, that `scaled_sci` is relative and
  file-specific, and whether you dropped self-pairs.
