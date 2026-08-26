#!/usr/bin/env python3
"""Regression tests for the deployed empirical-input manifest utility."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "extensions"
    / "empirical"
    / "utils"
    / "empirical_input_manifest.py"
)


class EmpiricalInputManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)
        (self.project / "code" / "utils").mkdir(parents=True)
        (self.project / "output" / "stage3a").mkdir(parents=True)
        (self.project / "output" / "stage3a" / "verification").mkdir()
        (self.project / "code" / "empirical.py").write_text(
            "from utils.helper import estimate\n\nprint(estimate())\n"
        )
        (self.project / "code" / "utils" / "__init__.py").write_text("")
        (self.project / "code" / "utils" / "helper.py").write_text(
            "def estimate():\n    return 1.0\n"
        )
        (self.project / "code" / "unrelated.py").write_text("VALUE = 1\n")
        self.report = self.project / "output" / "stage3a" / "empirical_analysis.md"
        self.report.write_text(
            "# Analysis\n\n"
            "## Methodology\n\nOriginal method prose.\n\n"
            "## Headline claims\n\n"
            "- [HEADLINE] [claim_id: main] [reported_value: 1.0] [tolerance_class: returns_spreads_coefficients] The estimate is 1.0.\n\n"
            "### Detail\n\nThis detail is part of the headline section.\n\n"
            "## Assessment\n\nOriginal assessment.\n"
        )
        self.result = self.project / "output" / "stage3a" / "empirics_verify_result.json"
        self.verifier = (
            self.project / "output" / "stage3a" / "verification" / "empirics_verify.py"
        )
        self.verifier.write_text("print('main', 1.0, 1.0, 0.0)\n")
        manifest = self.run_tool("snapshot")
        self.write_pass_result(self.result, manifest)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_tool(self, *arguments: str, check: bool = True) -> dict[str, object]:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--project-root",
                str(self.project),
                *arguments,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check and completed.returncode != 0:
            self.fail(f"tool failed ({completed.returncode}): {completed.stderr}")
        if not check:
            return {"returncode": completed.returncode, "stderr": completed.stderr}
        return json.loads(completed.stdout)

    def compare(self) -> dict[str, object]:
        return self.run_tool("compare", "--result", str(self.result))

    def write_pass_result(self, path: Path, manifest: dict[str, object]) -> None:
        entries = manifest["headline_claims"]["entries"]  # type: ignore[index]
        analysis = manifest["headline_claims"]["path"]  # type: ignore[index]
        paths = self.run_tool("paths", "--analysis", str(analysis))
        expected_result = self.project / str(paths["verify_result"])
        self.assertEqual(path, expected_result)
        verifier = self.project / str(paths["verify_script"])
        run_payload = {
            "claims": [
                {
                    "claim_id": entry["claim_id"],
                    "replicated_value": float(entry["reported_value"]),
                }
                for entry in entries
            ]
        }
        verifier.write_text(
            "import json\n"
            f"print(json.dumps({run_payload!r}))\n"
        )
        candidate = self.project / str(paths["pass_candidate"])
        candidate.write_text(
            json.dumps(
                {
                    "path_evidence": [
                        {
                            "claim_id": entry["claim_id"],
                            "path_description": "independent raw-source reconstruction",
                            "path_class": "raw_source_not_cache",
                        }
                        for entry in entries
                    ],
                    "untagged_warnings": [],
                }
            )
        )
        self.run_tool(
            "finalize-pass",
            "--analysis",
            str(analysis),
            "--candidate",
            str(paths["pass_candidate"]),
            "--result",
            str(paths["verify_result"]),
        )

    def refresh_result(self) -> None:
        manifest = self.run_tool("snapshot")
        self.write_pass_result(self.result, manifest)

    def test_unchanged_inputs(self) -> None:
        comparison = self.compare()
        self.assertEqual(comparison["status"], "UNCHANGED")
        self.assertEqual(comparison["changed_code_files"], [])
        self.assertFalse(comparison["headline_claims_changed"])

    def test_methodology_prose_outside_headline_section_does_not_change_manifest(self) -> None:
        self.report.write_text(
            self.report.read_text()
            .replace("Original method prose.", "Rewritten method prose.")
            .replace("Original assessment.", "Rewritten assessment.")
        )
        self.assertEqual(self.compare()["status"], "UNCHANGED")

    def test_headline_only_change_is_detected(self) -> None:
        self.report.write_text(self.report.read_text().replace("estimate is 1.0", "estimate is 1.1"))
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertTrue(comparison["headline_claims_changed"])
        self.assertEqual(comparison["changed_code_files"], [])

    def test_entrypoint_change_is_detected(self) -> None:
        empirical = self.project / "code" / "empirical.py"
        empirical.write_text(empirical.read_text() + "# repaired\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/empirical.py"])
        self.assertFalse(comparison["headline_claims_changed"])

    def test_imported_local_dependency_change_is_detected(self) -> None:
        helper = self.project / "code" / "utils" / "helper.py"
        helper.write_text("def estimate():\n    return 1.1\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/utils/helper.py"])

    def test_transitively_imported_local_dependency_change_is_detected(self) -> None:
        deep = self.project / "code" / "utils" / "deep.py"
        deep.write_text("VALUE = 1.0\n")
        helper = self.project / "code" / "utils" / "helper.py"
        helper.write_text("from utils.deep import VALUE\n\ndef estimate():\n    return VALUE\n")
        self.refresh_result()
        deep.write_text("VALUE = 1.1\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/utils/deep.py"])

    def test_post_version_entrypoint_change_is_detected(self) -> None:
        post = self.project / "code" / "empirical_post_v2.py"
        post.write_text("from utils.helper import estimate\n\nprint(estimate())\n")
        self.refresh_result()
        post.write_text(post.read_text() + "# repaired\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/empirical_post_v2.py"])

    def test_versioned_analysis_is_bound_and_checked(self) -> None:
        versioned = self.project / "output" / "stage3a" / "empirical_analysis_v2.md"
        versioned.write_text(
            "# Revised analysis\n\n"
            "## Headline claims\n\n"
            "- [HEADLINE] [claim_id: revised] [reported_value: 2.0] [tolerance_class: moments] The revised estimate is 2.0.\n\n"
            "## Assessment\n\nDone.\n"
        )
        analysis = "output/stage3a/empirical_analysis_v2.md"
        versioned_verifier = (
            self.project / "output" / "stage3a" / "verification" / "empirics_verify_v2.py"
        )
        versioned_verifier.write_text("print('revised', 2.0, 2.0, 0.0)\n")
        manifest = self.run_tool("snapshot", "--analysis", analysis)
        versioned_result = (
            self.project / "output" / "stage3a" / "empirics_verify_result_v2.json"
        )
        self.write_pass_result(versioned_result, manifest)
        unchanged = self.run_tool(
            "compare", "--result", str(versioned_result), "--analysis", analysis
        )
        self.assertEqual(unchanged["status"], "UNCHANGED")
        versioned.write_text(versioned.read_text().replace("estimate is 2.0", "estimate is 2.1"))
        changed = self.run_tool(
            "compare", "--result", str(versioned_result), "--analysis", analysis
        )
        self.assertEqual(changed["status"], "CHANGED")
        self.assertTrue(changed["headline_claims_changed"])

    def test_compare_rejects_wrong_required_analysis(self) -> None:
        versioned = self.project / "output" / "stage3a" / "empirical_analysis_v2.md"
        versioned.write_text(self.report.read_text())
        failure = self.run_tool(
            "compare",
            "--result",
            str(self.result),
            "--analysis",
            "output/stage3a/empirical_analysis_v2.md",
            check=False,
        )
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("not required", str(failure["stderr"]))

    def test_artifact_paths_are_distinct_per_analysis(self) -> None:
        canonical = self.run_tool("paths")
        versioned = self.run_tool(
            "paths", "--analysis", "output/stage3a/empirical_analysis_vclaim_2.md"
        )
        self.assertEqual(
            canonical["verify_result"],
            "output/stage3a/empirics_verify_result.json",
        )
        self.assertEqual(
            versioned["verify_result"],
            "output/stage3a/empirics_verify_result_vclaim_2.json",
        )
        self.assertEqual(
            versioned["verify_script"],
            "output/stage3a/verification/empirics_verify_vclaim_2.py",
        )

    def test_check_all_detects_every_result_invalidated_by_code_change(self) -> None:
        analysis = "output/stage3a/empirical_analysis_v2.md"
        versioned = self.project / analysis
        versioned.write_text(self.report.read_text())
        versioned_verifier = (
            self.project / "output" / "stage3a" / "verification" / "empirics_verify_v2.py"
        )
        versioned_verifier.write_text("print('main', 1.0, 1.0, 0.0)\n")
        manifest = self.run_tool("snapshot", "--analysis", analysis)
        versioned_result = (
            self.project / "output" / "stage3a" / "empirics_verify_result_v2.json"
        )
        self.write_pass_result(versioned_result, manifest)
        empirical = self.project / "code" / "empirical.py"
        empirical.write_text(empirical.read_text() + "# final repair\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        statuses = {
            item["analysis"]: item["status"] for item in inventory["analyses"]
        }
        self.assertEqual(statuses["output/stage3a/empirical_analysis.md"], "CHANGED")
        self.assertEqual(statuses[analysis], "CHANGED")

    def test_check_all_rejects_orphan_verifier_artifacts(self) -> None:
        orphan_result = (
            self.project / "output" / "stage3a" / "empirics_verify_result_vorphan.json"
        )
        orphan_script = (
            self.project
            / "output"
            / "stage3a"
            / "verification"
            / "empirics_verify_vorphan.py"
        )
        orphan_result.write_text("{}\n")
        orphan_script.write_text("print('orphan')\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        error_paths = {item["path"] for item in inventory["artifact_errors"]}
        self.assertIn(
            "output/stage3a/empirics_verify_result_vorphan.json", error_paths
        )
        self.assertIn(
            "output/stage3a/verification/empirics_verify_vorphan.py", error_paths
        )

    def test_check_all_rejects_invalid_analysis_namespace_entry(self) -> None:
        invalid = self.project / "output" / "stage3a" / "empirical_analysis_notes.md"
        invalid.write_text("not a pipeline analysis\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertEqual(inventory["artifact_errors"][0]["path"], invalid.relative_to(self.project).as_posix())

    def test_check_all_rejects_reserved_analysis_with_wrong_extension(self) -> None:
        invalid = self.project / "output" / "stage3a" / "empirical_analysis_vignored.txt"
        invalid.write_text("not a valid analysis artifact\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertEqual(
            inventory["artifact_errors"][0]["path"],
            invalid.relative_to(self.project).as_posix(),
        )

    def test_check_all_accepts_results_pipeline_sibling_artifacts(self) -> None:
        # The stage doc derives RESULT_PLAN/BUNDLE/RECEIPT from the analysis
        # stem, so these share the reserved prefix by design (regression:
        # halted_replication_artifact_collision on every first full analysis).
        stage = self.project / "output" / "stage3a"
        for sibling in ("_results.json", "_results.plan.json", "_results.receipt.json"):
            (stage / f"empirical_analysis{sibling}").write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(inventory["status"], "UNCHANGED")

    def test_check_all_rejects_foreign_stem_results_sibling(self) -> None:
        invalid = (
            self.project / "output" / "stage3a" / "empirical_analysis_notes_results.json"
        )
        invalid.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertIn(
            invalid.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_rejects_symlinked_results_sibling(self) -> None:
        target = self.project / "outside_payload.json"
        target.write_text("{}\n")
        planted = (
            self.project / "output" / "stage3a" / "empirical_analysis_results.json"
        )
        planted.symlink_to(target)
        inventory = self.run_tool("check-all")
        self.assertIn(
            planted.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_accepts_expected_pending_candidate(self) -> None:
        # finalize-pass's documented intermediate: written on replicator PASS,
        # unlinked on successful finalization, legitimately present between.
        candidate = (
            self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        )
        candidate.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(inventory["status"], "UNCHANGED")

    def test_check_all_rejects_candidate_for_unknown_analysis(self) -> None:
        orphan = (
            self.project
            / "output"
            / "stage3a"
            / "empirics_verify_result_v9.json.candidate"
        )
        orphan.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertIn(
            orphan.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_and_snapshot_tolerate_verification_pycache(self) -> None:
        # An execution byproduct of importing a verifier module, not a hidden
        # dependency; it previously poisoned finalize-pass and check-all both.
        pycache = (
            self.project / "output" / "stage3a" / "verification" / "__pycache__"
        )
        pycache.mkdir()
        (pycache / "empirics_verify.cpython-312.pyc").write_bytes(b"\x00")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(inventory["status"], "UNCHANGED")
        self.run_tool("snapshot")

    def test_check_all_rejects_symlinked_verification_pycache(self) -> None:
        outside = self.project / "outside_cache"
        outside.mkdir()
        planted = (
            self.project / "output" / "stage3a" / "verification" / "__pycache__"
        )
        planted.symlink_to(outside, target_is_directory=True)
        inventory = self.run_tool("check-all")
        self.assertIn(
            planted.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_classifies_valid_named_nonregular_artifacts(self) -> None:
        self.result.unlink()
        self.result.mkdir()
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            self.result.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_classifies_symlinked_stage_namespace(self) -> None:
        stage_root = self.project / "output" / "stage3a"
        relocated = self.project / "relocated_stage3a"
        stage_root.rename(relocated)
        stage_root.symlink_to(relocated, target_is_directory=True)
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertEqual(inventory["artifact_errors"][0]["path"], "output/stage3a")

    def test_any_project_code_change_is_detected(self) -> None:
        (self.project / "code" / "unrelated.py").write_text("VALUE = 2\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/unrelated.py"])

    def test_unreadable_code_directory_fails_closed(self) -> None:
        hidden = self.project / "code" / "hidden"
        hidden.mkdir()
        (hidden / "payload.py").write_text("VALUE = 1\n")
        hidden.chmod(0)
        try:
            failure = self.run_tool("snapshot", check=False)
        finally:
            hidden.chmod(0o700)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("cannot enumerate complete code surface", str(failure["stderr"]))

    def test_dynamically_loaded_local_dependency_change_is_detected(self) -> None:
        empirical = self.project / "code" / "empirical.py"
        empirical.write_text(
            "import importlib\n\n"
            "helper = importlib.import_module('utils.helper')\n"
            "print(helper.estimate())\n"
        )
        self.refresh_result()
        helper = self.project / "code" / "utils" / "helper.py"
        helper.write_text("def estimate():\n    return 1.1\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/utils/helper.py"])

    def test_non_python_local_dependency_change_is_detected(self) -> None:
        helper = self.project / "code" / "estimate.R"
        helper.write_text("estimate <- function() 1.0\n")
        self.refresh_result()
        helper.write_text("estimate <- function() 1.1\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(comparison["changed_code_files"], ["code/estimate.R"])

    def test_replicator_output_directory_is_not_code_input(self) -> None:
        scratch = self.project / "output" / "stage3a" / "verification"
        verifier = scratch / "empirics_verify_v2.py"
        verifier.write_text("print(1.0)\n")
        self.assertEqual(self.compare()["status"], "UNCHANGED")

    def test_bytecode_change_under_code_is_detected(self) -> None:
        cache = self.project / "code" / "__pycache__"
        cache.mkdir()
        bytecode = cache / "dynamic.cpython-312.pyc"
        bytecode.write_bytes(b"first executable payload")
        self.refresh_result()
        bytecode.write_bytes(b"second executable payload")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertEqual(
            comparison["changed_code_files"],
            ["code/__pycache__/dynamic.cpython-312.pyc"],
        )

    def test_line_ending_normalization_is_the_only_text_normalization(self) -> None:
        self.report.write_bytes(self.report.read_text().replace("\n", "\r\n").encode())
        self.assertEqual(self.compare()["status"], "UNCHANGED")

    def test_heading_inside_fenced_code_does_not_truncate_headline_section(self) -> None:
        self.report.write_text(
            "# Analysis\n\n"
            "## Headline claims\n\n"
            "- [HEADLINE] [claim_id: first] [reported_value: 1.0] [tolerance_class: returns_spreads_coefficients] The first estimate is 1.0.\n\n"
            "```python\n# recomputation note\nvalue = 1.0\n```\n\n"
            "- [HEADLINE] [claim_id: second] [reported_value: 2.0] [tolerance_class: moments] The second estimate is 2.0.\n\n"
            "## Assessment\n\nDone.\n"
        )
        self.refresh_result()
        self.report.write_text(self.report.read_text().replace("estimate is 2.0", "estimate is 9.0"))
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertTrue(comparison["headline_claims_changed"])

    def test_tampered_stored_manifest_fails_closed(self) -> None:
        result = json.loads(self.result.read_text())
        result["input_manifest"]["headline_claims"]["sha256"] = "0" * 64
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("combined digest does not match", str(failure["stderr"]))

    def test_non_pass_result_cannot_reuse_valid_manifest(self) -> None:
        result = json.loads(self.result.read_text())
        result["verdict"] = "FAIL"
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("does not record verdict PASS", str(failure["stderr"]))

    def test_pass_result_requires_claim_evidence(self) -> None:
        result = json.loads(self.result.read_text())
        result["claims"] = []
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("at least one claim", str(failure["stderr"]))

    def test_pass_result_rejects_invented_or_inconsistent_claim(self) -> None:
        result = json.loads(self.result.read_text())
        claim = result["claims"][0]
        claim.update(
            {
                "claim_id": "invented_claim",
                "reported_value": 0.0,
                "replicated_value": 999.0,
                "relative_delta": 0.0,
                "agree": True,
            }
        )
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("do not exactly match", str(failure["stderr"]))

    def test_pass_result_rejects_false_delta_and_agreement(self) -> None:
        result = json.loads(self.result.read_text())
        result["claims"][0].update(
            {
                "replicated_value": 9.0,
                "relative_delta": 0.0,
                "agree": True,
            }
        )
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("relative_delta is inconsistent", str(failure["stderr"]))

    def test_pass_result_rejects_even_a_small_delta_tamper(self) -> None:
        result = json.loads(self.result.read_text())
        result["claims"][0]["relative_delta"] = 5e-13
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("relative_delta is inconsistent", str(failure["stderr"]))

    def test_pass_result_requires_exact_large_reported_value(self) -> None:
        self.report.write_text(
            self.report.read_text().replace(
                "[reported_value: 1.0]",
                "[reported_value: 1000000000000]",
            )
        )
        self.refresh_result()
        result = json.loads(self.result.read_text())
        result["claims"][0]["reported_value"] = 1000000000000.5
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("reported_value does not match", str(failure["stderr"]))

    def test_pass_result_rejects_inflated_or_reclassified_tolerance(self) -> None:
        result = json.loads(self.result.read_text())
        result["claims"][0].update(
            {
                "tolerance_class": "counts",
                "tolerance_type": "absolute",
                "tolerance": 1.0,
            }
        )
        self.result.write_text(json.dumps(result))
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("tolerance_class is invalid", str(failure["stderr"]))

    def test_finalize_pass_runs_verifier_and_derives_result(self) -> None:
        self.verifier.write_text(
            "import json\nprint(json.dumps({'claims': [{'claim_id': 'main', 'replicated_value': 1.0}]}))\n"
        )
        candidate = self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        candidate.write_text(
            json.dumps(
                {
                    "path_evidence": [
                        {
                            "claim_id": "main",
                            "path_description": "independent raw-source reconstruction",
                            "path_class": "raw_source_not_cache",
                        }
                    ],
                    "untagged_warnings": [],
                }
            )
        )
        finalized = self.run_tool(
            "finalize-pass",
            "--candidate",
            str(candidate),
            "--result",
            "output/stage3a/empirics_verify_result.json",
        )
        self.assertEqual(finalized["status"], "FINALIZED")
        self.assertFalse(candidate.exists())
        self.assertEqual(self.compare()["status"], "UNCHANGED")

    def test_finalize_pass_does_not_follow_a_fixed_temp_symlink(self) -> None:
        self.verifier.write_text(
            "import json\nprint(json.dumps({'claims': [{'claim_id': 'main', 'replicated_value': 1.0}]}))\n"
        )
        candidate = self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        candidate.write_text(
            json.dumps(
                {
                    "path_evidence": [
                        {
                            "claim_id": "main",
                            "path_description": "independent raw-source reconstruction",
                            "path_class": "raw_source_not_cache",
                        }
                    ]
                }
            )
        )
        victim = self.project / "victim.txt"
        victim.write_text("untouched\n")
        planted = self.result.with_name(f".{self.result.name}.tmp")
        planted.symlink_to(victim)
        self.run_tool(
            "finalize-pass",
            "--candidate",
            str(candidate),
            "--result",
            "output/stage3a/empirics_verify_result.json",
        )
        self.assertEqual(victim.read_text(), "untouched\n")
        self.assertFalse(self.result.is_symlink())

    def test_finalize_pass_rejects_a_verifier_that_does_not_run(self) -> None:
        self.verifier.write_text("raise SystemExit('broken verifier')\n")
        candidate = self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        candidate.write_text(json.dumps({"path_evidence": [], "untagged_warnings": []}))
        failure = self.run_tool(
            "finalize-pass",
            "--candidate",
            str(candidate),
            "--result",
            "output/stage3a/empirics_verify_result.json",
            check=False,
        )
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("verification script exited", str(failure["stderr"]))

    def test_finalize_pass_cannot_recertify_a_removed_stale_verifier(self) -> None:
        self.report.write_text(
            self.report.read_text().replace(
                "The estimate is 1.0.", "A semantically different beta is 1.0."
            )
        )
        self.verifier.unlink()
        candidate = self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        candidate.write_text(
            json.dumps(
                {
                    "path_evidence": [
                        {
                            "claim_id": "main",
                            "path_description": "independent raw-source reconstruction",
                            "path_class": "raw_source_not_cache",
                        }
                    ]
                }
            )
        )
        failure = self.run_tool(
            "finalize-pass",
            "--candidate",
            str(candidate),
            "--result",
            "output/stage3a/empirics_verify_result.json",
            check=False,
        )
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("required input is missing", str(failure["stderr"]))

    def test_finalize_pass_rejects_inputs_mutated_during_verifier_run(self) -> None:
        self.verifier.write_text(
            "import json\n"
            "from pathlib import Path\n"
            "print(json.dumps({'claims': [{'claim_id': 'main', 'replicated_value': 1.0}]}))\n"
            "Path('code/unrelated.py').write_text('VALUE = 999\\n')\n"
        )
        candidate = self.project / "output" / "stage3a" / "empirics_verify_result.json.candidate"
        candidate.write_text(
            json.dumps(
                {
                    "path_evidence": [
                        {
                            "claim_id": "main",
                            "path_description": "independent raw-source reconstruction",
                            "path_class": "raw_source_not_cache",
                        }
                    ]
                }
            )
        )
        failure = self.run_tool(
            "finalize-pass",
            "--candidate",
            str(candidate),
            "--result",
            "output/stage3a/empirics_verify_result.json",
            check=False,
        )
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("execution changed a bound", str(failure["stderr"]))
        self.assertTrue(candidate.exists())

    def test_finalize_pass_rejects_and_preserves_unrelated_candidate_path(self) -> None:
        unrelated = self.project / "output" / "stage3a" / "unrelated.json"
        unrelated.write_text(json.dumps({"path_evidence": []}))
        failure = self.run_tool(
            "finalize-pass",
            "--candidate",
            str(unrelated),
            "--result",
            "output/stage3a/empirics_verify_result.json",
            check=False,
        )
        self.assertEqual(failure["returncode"], 2)
        self.assertTrue(unrelated.exists())

    def test_verifier_local_dependency_is_rejected(self) -> None:
        helper = self.verifier.parent / "helper.py"
        helper.write_text("VALUE = 1.0\n")
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("verification namespace contains", str(failure["stderr"]))
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            helper.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_verification_script_change_is_detected(self) -> None:
        self.verifier.write_text("print('main', 1.0, 9.0, 8.0)\n")
        comparison = self.compare()
        self.assertEqual(comparison["status"], "CHANGED")
        self.assertTrue(comparison["verification_script_changed"])

    def test_missing_verification_script_fails_closed(self) -> None:
        self.verifier.unlink()
        failure = self.run_tool("compare", "--result", str(self.result), check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("required input is missing", str(failure["stderr"]))

    def test_symlinked_import_fails_closed(self) -> None:
        outside = self.project / "outside.py"
        outside.write_text("def estimate():\n    return 1.0\n")
        helper = self.project / "code" / "utils" / "helper.py"
        helper.unlink()
        helper.symlink_to(outside)
        failure = self.run_tool("snapshot", check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("contains a symlink", str(failure["stderr"]))

    def test_parent_traversal_result_path_fails_closed(self) -> None:
        failure = self.run_tool("compare", "--result", "../outside.json", check=False)
        self.assertEqual(failure["returncode"], 2)
        self.assertIn("escapes project root", str(failure["stderr"]))


if __name__ == "__main__":
    unittest.main()
