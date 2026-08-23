#!/usr/bin/env python3
"""Regression checks for the load-bearing IBES data guidance."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WRDS_SKILL = ROOT / "templates/skill_bodies/empirical/wrds.md"
IBES_SKILL = ROOT / "templates/skill_bodies/empirical/ibes.md"
METADATA = ROOT / "templates/skill_metadata/empirical_skills.json"


def code_after_heading(markdown: str, heading: str) -> str:
    """Return the first fenced Python block after an exact Markdown heading."""
    section = markdown.split(heading, 1)
    if len(section) != 2:
        raise AssertionError(f"missing heading: {heading}")
    code = re.search(r"```python\n(.*?)```", section[1], re.DOTALL)
    if code is None:
        raise AssertionError(f"missing Python block after: {heading}")
    return code.group(1)


class IbesSkillGuidanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wrds = WRDS_SKILL.read_text(encoding="utf-8")
        cls.ibes = IBES_SKILL.read_text(encoding="utf-8")
        cls.metadata = json.loads(METADATA.read_text(encoding="utf-8"))["ibes"]

    def test_generic_wrds_recipe_uses_unadjusted_summary(self) -> None:
        code = code_after_heading(self.wrds, "### Analyst forecast dispersion")
        self.assertIn("FROM ibes.statsumu_epsus", code)
        self.assertNotIn("FROM ibes.statsum_epsus", code)
        self.assertIn("curcode", code)
        self.assertIn("estflag = 'P'", code)

    def test_dedicated_queries_enforce_their_own_guards(self) -> None:
        summary = code_after_heading(self.ibes, "### Consensus dispersion (no actual required)")
        actuals = code_after_heading(self.ibes, "### Actuals for an annual forecast-error design")
        detail = code_after_heading(
            self.ibes, "### Detail issuance, activation, and confirmation timestamps"
        )

        self.assertIn("FROM ibes.statsumu_epsus", summary)
        self.assertIn("estflag = 'P'", summary)
        self.assertIn("FROM ibes.actu_epsus", actuals)
        self.assertIn("pdicity = 'ANN'", actuals)
        self.assertNotIn("actualf", actuals)
        self.assertRegex(
            detail,
            r"ORDER BY\s+anndats DESC NULLS LAST, anntims DESC NULLS LAST,\s+"
            r"actdats DESC NULLS LAST, acttims DESC NULLS LAST,\s+"
            r"revdats DESC NULLS LAST, revtims DESC NULLS LAST,\s+"
            r"report_curr ASC NULLS LAST, pdf ASC NULLS LAST,\s+"
            r"value ASC NULLS LAST",
        )

    def test_dedicated_skill_carries_silent_error_guards(self) -> None:
        required = (
            "statsumu_epsus",
            "detu_epsus",
            "actu_epsus",
            "wrdsapps.ibcrsphist",
            "score <= 2",
            "sdate",
            "edate",
            "report_curr",
            "curr_act",
            "pdicity = 'ANN'",
            "cfacshr_estimate_date / cfacshr_actual_report_date",
            "`pdf`",
            "`estflag`",
            "`actualf`",
            "nonexistent join column",
            "parent-versus-consolidated",
            "not as the revision",
            "never its review date",
            "both a non-trading",
            "actual report date to the last CRSP",
            "trading day on or before that date",
        )
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, self.ibes)

    def test_guidance_does_not_claim_universal_dispersion_direction(self) -> None:
        self.assertIn("do not claim a universal", self.ibes)
        self.assertNotIn("mechanically inflates", self.ibes)

    def test_metadata_surfaces_the_required_join_dimensions(self) -> None:
        descriptions = [self.metadata["description"], self.metadata["codex"]["description"]]
        for description in descriptions:
            with self.subTest(description=description[:40]):
                self.assertIn("pdicity", description)
                self.assertIn("currency", description)
                self.assertIn("estflag", description)
                self.assertIn("announce/activation", description)
                self.assertIn("confirmations", description)
                self.assertIn("wrdsapps.ibcrsphist", description)


if __name__ == "__main__":
    unittest.main(verbosity=2)
