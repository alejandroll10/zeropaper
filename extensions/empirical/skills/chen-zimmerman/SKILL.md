---
name: chen-zimmerman
description: Open Source Asset Pricing dataset (Chen & Zimmerman 2022). Firm-level anomaly signals, updated monthly. Use for cross-sectional calibration, testing anomaly predictions, and constructing characteristic-sorted portfolios.
user-invocable: true
argument-hint: [signal-name or "list"]
allowed-tools: Bash, Read, Write, WebFetch
---

## Source
- Paper: Chen & Zimmerman (2022), "Open Source Cross-Sectional Asset Pricing", Review of Financial Studies
- GitHub: https://github.com/OpenSourceAP/CrossSection
- Data: https://drive.google.com/drive/folders/1EP6oEabyZRamveGNyzYU0u6qJ-N43Qfq
- The GitHub README is the source of truth for current schema, signal list, and download links

## How to use

### Step 1: Check for package
```bash
pip install openassetpricing 2>/dev/null && echo "Package available" || echo "Use direct download"
```

### Step 2a: If package exists
```python
import openassetpricing as oap
# Follow package documentation
```

### Step 2b: Direct download (fallback)
```python
import pandas as pd
# Download signed predictors CSV from Google Drive or GitHub releases
# Check the GitHub README for current download links — they may change
# The file is large (~500MB+). Download once, cache locally in data/
```

### Step 3: Read the GitHub README
Before using the data, always fetch the current README for schema updates:
```bash
curl -s https://raw.githubusercontent.com/OpenSourceAP/CrossSection/master/README.md | head -200
```

## What the data contains
- Firm-month panel with CRSP permno and date
- ~200 pre-computed anomaly signals from the literature
- Each signal maps to an original paper and is categorized (value, momentum, profitability, etc.)
- Signals are standardized and ready for portfolio sorts or cross-sectional regressions

## Standard operations
- **Portfolio sorts**: form decile portfolios each month on a signal, compute value-weighted returns
- **Long-short spread**: go long top decile, short bottom decile
- **Fama-MacBeth**: regress returns on multiple signals cross-sectionally
- **Alpha**: regress long-short portfolio on FF5 to get characteristic-adjusted alpha
- **Replication**: compare your model's predicted cross-section to the empirical one
- **Signal zoo**: test whether your model's mechanism maps to any known anomaly

## Notes
- Data is updated periodically — always check dates
- Signals require CRSP/Compustat merge, which is already done in this dataset
- For proprietary data underlying the signals, you'd need WRDS access
- Always state which signals you use, the sample period, and weighting scheme
