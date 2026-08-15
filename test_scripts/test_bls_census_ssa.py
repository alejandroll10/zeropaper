"""Offline SSA bundle regression plus an explicit opt-in upstream check.

Run from the template repository:

    PYTHONPATH=deploy_assets/extensions/empirical \
      python3 test_scripts/test_bls_census_ssa.py

From a non-datacenter network, add ``SSA_LIVE_REFRESH=1`` to compare the
official live page with the bundle. A 403 is a failed refresh check, not a
skip and not evidence that the bundle is current.
"""
import json
import os
import shutil
import tempfile
from unittest.mock import patch

import pandas as pd

from utils import bls_census_utils as bls


class _FakeResponse:
    def __init__(self, text):
        self._payload = text.encode("utf-8")

    def read(self):
        return self._payload


def _assert_same_table(expected, actual):
    pd.testing.assert_frame_equal(expected, actual, check_dtype=True)
    assert actual.attrs["table_year"] == expected.attrs["table_year"]
    assert (
        actual.attrs["trustees_report_year"]
        == expected.attrs["trustees_report_year"]
    )


def _table_html(frame, title=True):
    heading = (
        "<h2>Period Life Table, 2023, as used in the 2026 Trustees Report</h2>"
        if title else ""
    )
    return heading + frame.to_html(index=False)


def _expect_runtime_error(call, text):
    try:
        call()
    except RuntimeError as exc:
        assert text in str(exc), f"expected {text!r} in {exc!r}"
    else:
        raise AssertionError(f"expected RuntimeError containing {text!r}")


def main():
    with patch.object(
        bls.urllib.request,
        "urlopen",
        side_effect=AssertionError("offline SSA load attempted a network request"),
    ):
        bundled = bls.ssa_period_life_table()[0]

    assert bundled.shape == (120, 7)
    assert isinstance(bundled.columns, pd.MultiIndex)
    assert bundled.columns.tolist() == list(bls._SSA_LEGACY_COLUMNS)
    assert bundled[("Exact age", "Exact age")].tolist() == list(range(120))
    assert bundled.attrs["bundled"] is True
    assert bundled.attrs["table_year"] == 2023
    assert bundled.attrs["trustees_report_year"] == 2026
    assert bundled.attrs["source_url"] == bls._SSA_SOURCE_URL
    assert len(bundled.attrs["csv_sha256"]) == 64

    # Exercise the refresh parser without a network dependency. to_html()
    # recreates the same two-row header contract as SSA's table.
    fixture_html = _table_html(bundled)
    with patch.object(
        bls.urllib.request, "urlopen", return_value=_FakeResponse(fixture_html)
    ):
        parsed = bls.ssa_period_life_table(refresh=True)[0]
    assert parsed.attrs["bundled"] is False
    _assert_same_table(bundled, parsed)

    # A custom URL preserves the pre-bundle raw multi-table return and
    # URL-keyed cache behavior, without imposing SSA's default schema.
    custom_url = "https://example.invalid/table.html"
    custom_html = (
        "<table><tr><th>x</th></tr><tr><td>1</td></tr></table>"
        "<table><tr><th>y</th></tr><tr><td>2</td></tr></table>"
    )
    with tempfile.TemporaryDirectory(prefix="ssa-custom-cache-test.") as tmp:
        with (
            patch.object(bls, "_DATA_DIR", tmp),
            patch.object(
                bls.urllib.request,
                "urlopen",
                return_value=_FakeResponse(custom_html),
            ),
        ):
            custom_tables = bls.ssa_period_life_table(custom_url)
        assert len(custom_tables) == 2
        assert custom_tables[0].columns.tolist() == ["x"]
        assert custom_tables[1].columns.tolist() == ["y"]

        with (
            patch.object(bls, "_DATA_DIR", tmp),
            patch.object(
                bls.urllib.request,
                "urlopen",
                side_effect=AssertionError("custom URL cache miss"),
            ),
        ):
            cached_custom = bls.ssa_period_life_table(custom_url)
        assert len(cached_custom) == 1
        assert cached_custom[0].columns.tolist() == ["x"]

    vintage_html = fixture_html.replace(
        "Period Life Table, 2023, as used in the 2026 Trustees Report",
        "Period Life Table, 2024, as used in the 2027 Trustees Report",
    )
    with patch.object(
        bls.urllib.request, "urlopen", return_value=_FakeResponse(vintage_html)
    ):
        changed_vintage = bls.ssa_period_life_table(refresh=True)[0]
    assert changed_vintage.attrs["table_year"] == 2024
    assert changed_vintage.attrs["trustees_report_year"] == 2027
    try:
        _assert_same_table(bundled, changed_vintage)
    except AssertionError:
        pass
    else:
        raise AssertionError("live refresh comparison accepted a changed vintage")

    drift_html = (
        "<h2>Period Life Table, 2024, as used in the 2027 Trustees Report</h2>"
        "<table><tr><th>age</th><th>value</th></tr>"
        "<tr><td>0</td><td>1</td></tr></table>"
    )
    with patch.object(
        bls.urllib.request, "urlopen", return_value=_FakeResponse(drift_html)
    ):
        _expect_runtime_error(
            lambda: bls.ssa_period_life_table(refresh=True), "schema changed"
        )

    renamed = bundled.copy()
    renamed_columns = list(renamed.columns)
    renamed_columns[1] = ("Male", "Mortality chance a")
    renamed.columns = pd.MultiIndex.from_tuples(renamed_columns)
    with patch.object(
        bls.urllib.request,
        "urlopen",
        return_value=_FakeResponse(_table_html(renamed)),
    ):
        _expect_runtime_error(
            lambda: bls.ssa_period_life_table(refresh=True), "unexpected headers"
        )

    bad_ages = bundled.copy()
    bad_ages.iloc[-1, 0] = 118
    with patch.object(
        bls.urllib.request,
        "urlopen",
        return_value=_FakeResponse(_table_html(bad_ages)),
    ):
        _expect_runtime_error(
            lambda: bls.ssa_period_life_table(refresh=True), "exact ages 0-119"
        )

    with patch.object(
        bls.urllib.request,
        "urlopen",
        return_value=_FakeResponse(_table_html(bundled, title=False)),
    ):
        _expect_runtime_error(
            lambda: bls.ssa_period_life_table(refresh=True),
            "cannot identify table vintage",
        )

    canonical, _ = bls._load_bundled_ssa_period_table()
    negative_lives = canonical.copy()
    negative_lives.loc[119, "male_number_of_lives"] = -1
    _expect_runtime_error(
        lambda: bls._validate_ssa_canonical(negative_lives, "negative fixture"),
        "invalid male survivor counts",
    )
    infinite_expectancy = canonical.copy()
    infinite_expectancy.loc[50, "female_life_expectancy"] = float("inf")
    _expect_runtime_error(
        lambda: bls._validate_ssa_canonical(infinite_expectancy, "inf fixture"),
        "non-finite numeric fields",
    )
    inconsistent = canonical.copy()
    inconsistent.loc[50, "male_death_probability"] = 0.5
    _expect_runtime_error(
        lambda: bls._validate_ssa_canonical(inconsistent, "recurrence fixture"),
        "probability/survivor recurrence",
    )

    with tempfile.TemporaryDirectory(prefix="ssa-bundle-test.") as tmp:
        for name in ("period_life_table_2023.csv", "provenance.json"):
            shutil.copy2(os.path.join(bls._SSA_BUNDLE_DIR, name), tmp)
        temp_provenance = os.path.join(tmp, "provenance.json")

        with open(os.path.join(tmp, "period_life_table_2023.csv"), "a") as fh:
            fh.write("\n")
        with (
            patch.object(bls, "_SSA_BUNDLE_DIR", tmp),
            patch.object(bls, "_SSA_PROVENANCE_FILE", temp_provenance),
        ):
            _expect_runtime_error(
                bls._load_bundled_ssa_period_table, "checksum does not match"
            )

        shutil.copy2(
            os.path.join(
                os.path.dirname(bls.__file__),
                "ssa_oact",
                "period_life_table_2023.csv",
            ),
            tmp,
        )
        with open(temp_provenance, encoding="utf-8") as fh:
            unsafe = json.load(fh)
        unsafe["csv_file"] = "../period_life_table_2023.csv"
        with open(temp_provenance, "w", encoding="utf-8") as fh:
            json.dump(unsafe, fh)
        with (
            patch.object(bls, "_SSA_BUNDLE_DIR", tmp),
            patch.object(bls, "_SSA_PROVENANCE_FILE", temp_provenance),
        ):
            _expect_runtime_error(
                bls._load_bundled_ssa_period_table, "unsafe csv_file path"
            )

    print(
        "PASS: bundled SSA table is offline, checksummed, schema-compatible, "
        "and refresh validation fails closed"
    )

    if os.getenv("SSA_LIVE_REFRESH") == "1":
        live = bls.ssa_period_life_table(refresh=True)[0]
        _assert_same_table(bundled, live)
        print("PASS: live SSA page matches the bundled vintage and values")
    else:
        print("SKIP: live SSA comparison not requested (set SSA_LIVE_REFRESH=1)")


if __name__ == "__main__":
    main()
