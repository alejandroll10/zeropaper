## Source
- Paper: Chen, Lopez-Lira & Zimmermann, "Peer-reviewed theory does not help predict the cross-section of stock returns"
- GitHub: https://github.com/chenandrewy/flex-mining
- Data: https://drive.google.com/drive/folders/1SZe_aF4ZNvK4ZRx2jQUE1j19KQvBaqWr
- No authentication required (public Google Drive)

## How to download

### Option 1: gdown (preferred — downloads entire folder)
```python
import gdown
import os

# Download the full dataset
url = 'https://drive.google.com/drive/folders/1SZe_aF4ZNvK4ZRx2jQUE1j19KQvBaqWr'
gdown.download_folder(url, output='data/flex-mining/', remaining_ok=True)
```

### Option 2: Download specific files by ID
```python
import gdown

# Data-mined long-short returns (equal-weighted)
gdown.download(id='FILE_ID', output='data/flex-mining/DataMinedLongShortReturnsEW.csv')

# Data-mined long-short returns (value-weighted)
gdown.download(id='FILE_ID', output='data/flex-mining/DataMinedLongShortReturnsVW.csv')
```

### Option 3: Download signal theory classification
```python
import pandas as pd
# Direct from GitHub (small file)
url = 'https://raw.githubusercontent.com/chenandrewy/flex-mining/main/DataInput/SignalsTheoryChecked.csv'
signals = pd.read_csv(url)
```

## What the data contains

### Data-mined strategies (~30,000)
- Monthly long-short portfolio returns from all possible CRSP/Compustat accounting ratios
- Both equal-weighted (EW) and value-weighted (VW)
- Covers the full universe of ~29,000 candidate ratios constructible from Compustat items
- Each ratio sorted into decile portfolios monthly

### Signal theory classification
- Maps each CZ published signal to whether it has a theoretical justification
- Categories: theory-motivated vs. purely empirical
- Used to test whether theory-motivated signals outperform data-mined alternatives

### Key datasets in the Google Drive folder
| File/Folder | Description |
|------------|-------------|
| `DataMinedStrategies/DataMinedLongShortReturnsEW.csv` | EW long-short returns for ~30K strategies |
| `DataMinedStrategies/DataMinedLongShortReturnsVW.csv` | VW long-short returns for ~30K strategies |
| `Risk-vs/` | Risk vs. mispricing decomposition results |

## Standard operations

- **Benchmark published vs data-mined:** Compare CZ published signal returns against the distribution of data-mined returns. Are published signals in the right tail?
- **Sufficiency test:** How much of the cross-sectional return variation is captured by the published set vs. the full data-mined set?
- **Pre-publication test:** Do data-mined strategies that overlap with later-published signals show different return patterns before vs. after publication?
- **Theory value test:** Do theory-motivated signals outperform purely empirical ones, conditional on data-mining performance?

## Performance tips
- The full dataset is large (~500MB+). Download once to `data/flex-mining/` and cache.
- For quick exploration, start with the signal classification CSV (small, from GitHub).
- Load large CSVs with `pd.read_csv(..., usecols=[...])` to avoid memory issues.

## Rules
- **Cache locally.** Download to `data/flex-mining/` once. Don't re-download.
- **State which dataset.** Always report EW vs VW, sample period, and any filters.
- **gdown required.** Install with `pip install gdown` if not available.
