# SSA OACT period life table bundle

`period_life_table_2023.csv` is the Social Security Administration Office
of the Chief Actuary's 2023 period life table for the Social Security area
population, as used in the 2026 Trustees Report. The canonical source is:

https://www.ssa.gov/oact/STATS/table4c6.html

The normalized columns preserve all seven fields in SSA table 4.C6. The
source page's footnotes define `*_death_probability` as the probability of
dying within one year and `*_number_of_lives` as survivors out of 100,000
born alive. `provenance.json` records the table/report vintage, retrieval
date, row/age/schema contract, rights note, and the CSV's SHA-256 digest.

## Refresh procedure

Ordinary pipeline runs must not refresh this data. From an assembled project,
check for a new SSA vintage on a non-datacenter network with:

```bash
PYTHONPATH=code python3 - <<'PY'
import pandas as pd
from utils.bls_census_utils import ssa_period_life_table

bundled = ssa_period_life_table()[0]
live = ssa_period_life_table(refresh=True)[0]
pd.testing.assert_frame_equal(bundled, live, check_dtype=True)
assert live.attrs["table_year"] == bundled.attrs["table_year"]
assert live.attrs["trustees_report_year"] == bundled.attrs["trustees_report_year"]
print("PASS: live SSA page matches the bundled vintage and values")
PY
```

Template maintainers can run the fuller regression from a template checkout
(these `deploy_assets/` and `test_scripts/` paths are not shipped):

```bash
SSA_LIVE_REFRESH=1 PYTHONPATH=deploy_assets/extensions/empirical \
  python3 test_scripts/test_bls_census_ssa.py
```

The check fails if the live table's headers, ages, vintage, or values differ
from the bundle. When SSA publishes a new vintage:

1. Review the official page and the test's diff; do not accept a schema
   change by position alone.
2. Export the validated live frame to a new
   `period_life_table_<year>.csv` using the seven canonical column names in
   `provenance.json`. Keep the old version in source history; the runtime
   bundle may contain only the new active CSV.
3. Update every field in `provenance.json`, including `csv_file`, vintages,
   retrieval date, row/age/schema contract, and the SHA-256 digest from
   `sha256sum`.
4. Update the constants/tests/docs that name the active vintage, assemble an
   empirical deployment, and rerun both the offline and live checks.

Direct SSA requests may return HTTP 403 from cloud/datacenter egress. That is
a failure to perform the refresh check, never evidence that the bundle is
current; rerun the explicit check from an unblocked network.
