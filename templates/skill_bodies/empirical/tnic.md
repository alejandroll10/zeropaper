## Source
- Hoberg & Phillips Text-based Network Industry Classifications (TNIC)
- Website: https://hobergphillips.tuck.dartmouth.edu/industryclass.htm
- No authentication, no registration, no API key
- Papers: Hoberg & Phillips, "Product Market Synergies and Competition in Mergers
  and Acquisitions", RFS 2010, 23(10):3773-3811; "Text-Based Network Industries
  and Endogenous Product Differentiation", JPE 2016, 124(5):1423-1465
- Recomputed annually from firms' 10-K product descriptions; coverage is
  10-K-bound (firms that file a 10-K with a parseable product description)

## How to use

### Download TNIC-3 (recommended)
```python
import io, zipfile, urllib.request
import pandas as pd

url = "https://hobergphillips.tuck.dartmouth.edu/idata/tnic3_data.zip"
raw = urllib.request.urlopen(url).read()          # ~151 MB zip
z = zipfile.ZipFile(io.BytesIO(raw))
df = pd.read_csv(z.open("tnic3_data.txt"), sep="\t")
# Columns: year, gvkey1, gvkey2, score
# 27,161,831 rows, 1988-2023
```
Cache the extracted `.txt` in `data/` after the first download — it is large and
the host is slow.

### Products available
| File | What it is |
|------|-----------|
| `tnic3_data.zip` | TNIC-3 — pairwise similarity, ~3-digit-SIC granularity (**recommended**) |
| `tnic2_data.zip` | TNIC-2 — coarser threshold |
| `tnicfic_data.zip` | FIC — Fixed (transitive) Industry Classifications, with industry codes |
| (site) | Hoberg-Phillips product market fluidity, TSIMM, and other firm-year measures |

## Key gotchas
- **It is a network, not a partition.** TNIC gives each firm its *own* set of
  rivals; pairs are non-transitive (A~B and B~C does not imply A~C) and there is
  **no industry code** to group on. Do not treat it like SIC/NAICS. Use FIC if
  you need a transitive classification with codes.
- **Identifier is Compustat `gvkey`** (two columns, `gvkey1`/`gvkey2`). Merge to
  CRSP via the CRSP-Compustat link, not directly on permno.
- **`score` is excess-over-threshold, not raw cosine similarity.** It is the
  cosine similarity minus the inclusion threshold, so the distribution starts
  near 0 — values are not comparable to raw cosine similarities from other text
  pipelines.
- **Symmetric, both directions stored.** Each rival pair appears twice
  (gvkey1,gvkey2) and (gvkey2,gvkey1). Dedup with `gvkey1 < gvkey2` for
  pair-level work; keep both directions if you need each firm's full rival row.
- **Self-pairs present** (gvkey1 == gvkey2) with an empty/blank score — drop them.
- **Recomputed annually**, so a firm's rival set and scores change year to year;
  always merge on `year`.

## Standard operations
- Firm-year competition intensity: sum or count of `score` over a firm's rivals
  in a given year (the TNIC total similarity / number-of-rivals measures).
- Peer-firm controls: average a characteristic over each firm's TNIC rivals
  (text-based peer benchmark instead of SIC-industry mean).
- Product-market-distance instruments and merger/synergy analysis (the RFS 2010
  application).
- Always state TNIC-3 vs TNIC-2 vs FIC, the sample years, and the gvkey dedup
  convention you used.
