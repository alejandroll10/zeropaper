#!/usr/bin/env python3
"""Regression tests for the deployed empirical-input manifest utility."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "extensions"
    / "empirical"
    / "utils"
    / "empirical_input_manifest.py"
)
RESULTS_UTILITY = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "utils"
    / "results_pipeline"
    / "results_pipeline.py"
)


class EmpiricalInputManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)
        (self.project / "code" / "utils").mkdir(parents=True)
        (self.project / "code" / "utils" / "results_pipeline").mkdir()
        shutil.copy2(
            RESULTS_UTILITY,
            self.project / "code" / "utils" / "results_pipeline" / "results_pipeline.py",
        )
        self.script = self.project / "code" / "utils" / "empirical_input_manifest.py"
        shutil.copy2(SCRIPT, self.script)
        (self.project / "process_log").mkdir()
        (self.project / "process_log" / "results_pipeline.lock").write_bytes(b"")
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
        self.report_text = (
            "# Analysis\n\n"
            "## Methodology\n\nOriginal method prose.\n\n"
            "## Headline claims\n\n"
            "- [HEADLINE] [claim_id: main] [reported_value: 1.0] [tolerance_class: returns_spreads_coefficients] The estimate is 1.0.\n\n"
            "### Detail\n\nThis detail is part of the headline section.\n\n"
            "## Assessment\n\nOriginal assessment.\n"
        )
        self.report = self.project / "output" / "stage3a" / "empirical_analysis.md"
        self.report.write_text(self.report_text)
        (self.project / "code" / "generate_empirical_result.py").write_text(
            "import json, os, pathlib\n"
            "root = pathlib.Path.cwd()\n"
            f"(root / 'output/stage3a/empirical_analysis.md').write_text({self.report_text!r})\n"
            "bundle = {\n"
            "  'schema_version': 1,\n"
            "  'producer': {'name': 'integration-test',\n"
            "               'code': ['code/generate_empirical_result.py'],\n"
            "               'inputs': [], 'reproducibility': 'captured'},\n"
            "  'results': {'main.estimate': {'description': 'Main estimate', 'value': '1.0'}},\n"
            "  'artifacts': [{'path': 'output/stage3a/empirical_analysis.md',\n"
            "                 'description': 'Analysis report', 'media_type': 'text/markdown'}],\n"
            "  'renderer': {'code': []}, 'exhibits': []\n"
            "}\n"
            "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle) + '\\n')\n"
        )
        self.result = self.project / "output" / "stage3a" / "empirics_verify_result.json"
        self.verifier = (
            self.project / "output" / "stage3a" / "verification" / "empirics_verify.py"
        )
        self.verifier.write_text("print('main', 1.0, 1.0, 0.0)\n")
        manifest = self.run_tool("snapshot")
        self.write_pass_result(self.result, manifest)
        self.write_empty_registry()
        self.register_analysis("output/stage3a/empirical_analysis.md", "active")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_tool(self, *arguments: str, check: bool = True) -> dict[str, object]:
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                str(self.script),
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

    def run_results_pipeline(self, *arguments: str) -> dict[str, object]:
        completed = subprocess.run(
            [
                sys.executable,
                str(
                    self.project
                    / "code"
                    / "utils"
                    / "results_pipeline"
                    / "results_pipeline.py"
                ),
                *arguments,
            ],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(
                f"results pipeline failed ({completed.returncode}): "
                f"{completed.stdout}{completed.stderr}"
            )
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

    def file_fingerprint(self, relative: str) -> dict[str, str]:
        data = (self.project / relative).read_bytes()
        return {
            "path": relative,
            "kind": "file",
            "sha256": f"sha256:{hashlib.sha256(data).hexdigest()}",
        }

    def write_empty_registry(self) -> None:
        (self.project / "process_log" / "results_registry.json").write_text(
            json.dumps(
                {
                    "kind": "result_registry",
                    "registry_version": 1,
                    "active": [],
                    "pending": [],
                    "retired": [],
                    "receipt_fingerprints": {},
                },
                indent=2,
            )
            + "\n"
        )

    def synthetic_environment(self, command: list[str]) -> dict[str, object]:
        executable = str(Path(sys.executable).resolve())
        manifest = {
            "launcher": {
                "requested": command[0],
                "executable": {
                    "path": executable,
                    "resolved_path": executable,
                    "sha256": "sha256:" + "0" * 64,
                    "size": 0,
                },
            },
            "platform": {
                "system": "",
                "release": "",
                "version": "",
                "machine": "",
                "libc": {"name": "", "version": ""},
                "os_release": None,
            },
            "runtime_environment": {},
            "project_environment": {
                "python_venv": None,
                "dependency_manifests": [],
            },
        }
        encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        return {
            "capture_version": 1,
            "sha256": f"sha256:{hashlib.sha256(encoded).hexdigest()}",
            "manifest": manifest,
        }

    def register_analysis(
        self,
        analysis: str,
        lifecycle: str,
        *,
        receipt: str | None = None,
        supersedes: list[str] | None = None,
        plan: str | None = None,
        bundle: str | None = None,
    ) -> str:
        analysis_path = Path(analysis)
        receipt = receipt or (
            analysis_path.parent / f"{analysis_path.stem}_results.receipt.json"
        ).as_posix()
        plan = plan or (
            analysis_path.parent / f"{analysis_path.stem}_results.plan.json"
        ).as_posix()
        bundle = bundle or (
            analysis_path.parent / f"{analysis_path.stem}_results.json"
        ).as_posix()
        plan_path = self.project / plan
        bundle_path = self.project / bundle
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        bundle_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "producer_code": ["code/empirical.py"],
                    "producer_inputs": [],
                    "artifacts": [analysis],
                    "renderer_code": [],
                    "exhibits": [],
                }
            )
            + "\n"
        )
        bundle_path.write_text("{}\n")
        command = [sys.executable, "code/empirical.py"]
        receipt_path = self.project / receipt
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(
            json.dumps(
                {
                    "kind": "result",
                    "receipt_version": 2,
                    "supersedes": supersedes or [],
                    "producer_run": {
                        "command": command,
                        "plan": self.file_fingerprint(plan),
                        "bundle": self.file_fingerprint(bundle),
                        "code": [self.file_fingerprint("code/empirical.py")],
                        "inputs": [],
                        "renderer_code": [],
                        "artifacts": [self.file_fingerprint(analysis)],
                        "exhibits": [],
                        "reproducibility": "captured",
                        "environment": self.synthetic_environment(command),
                    },
                    "render_run": None,
                },
                indent=2,
            )
            + "\n"
        )
        registry_path = self.project / "process_log" / "results_registry.json"
        registry = json.loads(registry_path.read_text())
        fingerprint = self.file_fingerprint(receipt)
        if lifecycle == "active":
            registry["active"].append(receipt)
            registry["receipt_fingerprints"][receipt] = fingerprint
        elif lifecycle == "pending":
            registry["pending"].append(
                {"receipt": receipt, "supersedes": supersedes or []}
            )
            registry["receipt_fingerprints"][receipt] = fingerprint
        elif lifecycle == "retired":
            registry["retired"].append(
                {
                    "receipt": receipt,
                    "reason": "retired test attempt",
                    "last_fingerprint": fingerprint,
                }
            )
        else:
            self.fail(f"unsupported lifecycle: {lifecycle}")
        registry_path.write_text(json.dumps(registry, indent=2) + "\n")
        return receipt

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
        self.register_analysis(analysis, "active")
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
        self.assertTrue(
            (self.project / "output/stage3a/empirical_analysis_results.plan.json").is_file()
        )
        self.assertTrue(
            (self.project / "output/stage3a/empirical_analysis_results.json").is_file()
        )
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
            self.project / "output" / "stage3a" / "empirical_analysis_vghost_results.json"
        )
        planted.symlink_to(target)
        inventory = self.run_tool("check-all")
        self.assertIn(
            planted.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_excludes_retired_analysis_without_verifier(self) -> None:
        analysis = "output/stage3a/empirical_analysis_v1_a1.md"
        (self.project / analysis).write_text(self.report.read_text())
        self.register_analysis(analysis, "retired")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "UNCHANGED")
        entries = {item["analysis"]: item for item in inventory["analyses"]}
        self.assertEqual(entries[analysis]["status"], "EXCLUDED_RETIRED")
        self.assertEqual(entries[analysis]["lifecycle"], "retired")

    def test_check_all_checks_pending_analysis(self) -> None:
        analysis = "output/stage3a/empirical_analysis_v2_a2.md"
        (self.project / analysis).write_text(self.report.read_text())
        paths = self.run_tool("paths", "--analysis", analysis)
        (self.project / str(paths["verify_script"])).write_text("print('main', 1.0)\n")
        manifest = self.run_tool("snapshot", "--analysis", analysis)
        self.write_pass_result(self.project / str(paths["verify_result"]), manifest)
        self.register_analysis(analysis, "pending")
        inventory = self.run_tool("check-all")
        entries = {item["analysis"]: item for item in inventory["analyses"]}
        self.assertEqual(entries[analysis]["status"], "UNCHANGED")
        self.assertEqual(entries[analysis]["lifecycle"], "pending")

    def test_check_all_rejects_missing_registry(self) -> None:
        (self.project / "process_log" / "results_registry.json").unlink()
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertEqual(
            inventory["artifact_errors"][0]["path"],
            "process_log/results_registry.json",
        )

    def test_check_all_rejects_registry_with_duplicate_json_key(self) -> None:
        registry_path = self.project / "process_log/results_registry.json"
        registry_path.write_text(
            registry_path.read_text().replace(
                '"active": [', '"active": [],\n  "active": [', 1
            )
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "duplicate JSON object key",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_prepared_results_transaction(self) -> None:
        registry = json.loads(
            (self.project / "process_log/results_registry.json").read_text()
        )
        (self.project / "process_log/.results_pipeline-transaction-backup").mkdir()
        (self.project / "process_log/results_pipeline.transaction.json").write_text(
            json.dumps(
                {
                    "transaction_version": 1,
                    "phase": "prepared",
                    "cleanup_paths": [],
                    "backups": [],
                    "registry_before": registry,
                }
            )
            + "\n"
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "transaction recovery is required",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_receipt_outside_canonical_v2_contract(self) -> None:
        receipt_raw = "output/stage3a/empirical_analysis_results.receipt.json"
        receipt_path = self.project / receipt_raw
        receipt = json.loads(receipt_path.read_text())
        del receipt["producer_run"]["command"]
        receipt_path.write_text(json.dumps(receipt) + "\n")
        registry_path = self.project / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text())
        registry["receipt_fingerprints"][receipt_raw] = self.file_fingerprint(receipt_raw)
        registry_path.write_text(json.dumps(registry) + "\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "producer_run has unexpected or missing keys",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_stale_registry_receipt_fingerprint(self) -> None:
        receipt = self.project / "output/stage3a/empirical_analysis_results.receipt.json"
        receipt.write_text(receipt.read_text() + "\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "receipt bytes are stale",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_changed_declared_bundle(self) -> None:
        bundle = self.project / "output/stage3a/empirical_analysis_results.json"
        bundle.write_text('{"tampered": true}\n')
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "receipt bundle fingerprint does not match current bytes",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_missing_declared_plan(self) -> None:
        plan = self.project / "output/stage3a/empirical_analysis_results.plan.json"
        plan.unlink()
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "declared path does not exist",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_duplicate_analysis_ownership(self) -> None:
        self.register_analysis(
            "output/stage3a/empirical_analysis.md",
            "retired",
            receipt="output/stage3a/duplicate_results.receipt.json",
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            "owned by multiple result receipts",
            inventory["artifact_errors"][0]["error"],
        )

    def test_check_all_rejects_unregistered_analysis(self) -> None:
        orphan = self.project / "output/stage3a/empirical_analysis_vorphan.md"
        orphan.write_text(self.report.read_text())
        inventory = self.run_tool("check-all")
        self.assertIn(
            orphan.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_rejects_valid_stem_orphan_results_sibling(self) -> None:
        orphan = self.project / "output/stage3a/empirical_analysis_vghost_results.json"
        orphan.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertIn(
            orphan.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_rejects_undeclared_sibling_for_registered_analysis(self) -> None:
        analysis = "output/stage3a/empirical_analysis_vowned.md"
        (self.project / analysis).write_text(self.report.read_text())
        paths = self.run_tool("paths", "--analysis", analysis)
        (self.project / str(paths["verify_script"])).write_text("print('main', 1.0)\n")
        manifest = self.run_tool("snapshot", "--analysis", analysis)
        self.write_pass_result(self.project / str(paths["verify_result"]), manifest)
        self.register_analysis(
            analysis,
            "active",
            receipt="output/stage3a/custom_results.receipt.json",
            plan="output/stage3a/custom_results.plan.json",
            bundle="output/stage3a/custom_results.json",
        )
        orphan = self.project / "output/stage3a/empirical_analysis_vowned_results.json"
        orphan.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertIn(
            orphan.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_accepts_receipt_generated_by_results_pipeline(self) -> None:
        self.write_empty_registry()
        for relative in (
            "output/stage3a/empirical_analysis.md",
            "output/stage3a/empirical_analysis_results.json",
            "output/stage3a/empirical_analysis_results.receipt.json",
        ):
            path = self.project / relative
            if path.exists():
                path.unlink()
        plan = self.project / "output/stage3a/empirical_analysis_results.plan.json"
        plan.write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "producer_code": ["code/generate_empirical_result.py"],
                    "producer_inputs": [],
                    "artifacts": ["output/stage3a/empirical_analysis.md"],
                    "renderer_code": [],
                    "exhibits": [],
                }
            )
            + "\n"
        )
        run = self.run_results_pipeline(
            "run",
            "--caller-allowance-seconds",
            "3600",
            "--plan",
            "output/stage3a/empirical_analysis_results.plan.json",
            "--bundle",
            "output/stage3a/empirical_analysis_results.json",
            "--receipt",
            "output/stage3a/empirical_analysis_results.receipt.json",
            "--",
            sys.executable,
            "code/generate_empirical_result.py",
        )
        self.assertEqual(run["status"], "PENDING_ACTIVATION")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(inventory["status"], "UNCHANGED")
        self.assertEqual(inventory["analyses"][0]["lifecycle"], "pending")

    def test_check_all_holds_publication_lock_through_verdict(self) -> None:
        analysis = "output/stage3a/empirical_analysis_vconcurrent.md"
        plan = "output/concurrent_empirical_results.plan.json"
        bundle = "output/stage3a/empirical_analysis_vconcurrent_results.json"
        receipt = "output/stage3a/empirical_analysis_vconcurrent_results.receipt.json"
        producer = self.project / "code/generate_concurrent_result.py"
        producer.write_text(
            "import json, os, pathlib\n"
            "root = pathlib.Path.cwd()\n"
            f"(root / {analysis!r}).write_text({self.report_text!r})\n"
            "payload = {\n"
            "  'schema_version': 1,\n"
            "  'producer': {'name': 'concurrent-test',\n"
            "               'code': ['code/generate_concurrent_result.py'],\n"
            "               'inputs': [], 'reproducibility': 'captured'},\n"
            "  'results': {'main.estimate': {'description': 'Main estimate', 'value': '1.0'}},\n"
            f"  'artifacts': [{{'path': {analysis!r}, 'description': 'Analysis report',\n"
            "                 'media_type': 'text/markdown'}],\n"
            "  'renderer': {'code': []}, 'exhibits': []\n"
            "}\n"
            "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(payload) + '\\n')\n"
        )
        (self.project / plan).write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "producer_code": ["code/generate_concurrent_result.py"],
                    "producer_inputs": [],
                    "artifacts": [analysis],
                    "renderer_code": [],
                    "exhibits": [],
                }
            )
            + "\n"
        )
        registry_path = self.project / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text())
        prior_receipt = registry["active"].pop()
        prior_fingerprint = registry["receipt_fingerprints"].pop(prior_receipt)
        registry["retired"].append(
            {
                "receipt": prior_receipt,
                "reason": "concurrency fixture baseline",
                "last_fingerprint": prior_fingerprint,
            }
        )
        registry_path.write_text(json.dumps(registry, indent=2) + "\n")

        # Pause after namespace enumeration. Without a lease covering the
        # remaining comparisons, the publisher can commit an unseen analysis.
        source = self.script.read_text()
        needle = "        stage_entries = sorted(stage_root.iterdir())\n"
        self.assertIn(needle, source)
        self.script.write_text(
            source.replace(
                needle,
                needle
                + "        (project_root / 'process_log/check_all_scan_ready').write_text('ready\\n')\n"
                + "        __import__('time').sleep(1.0)\n",
                1,
            )
        )
        self.refresh_result()
        marker = self.project / "process_log/check_all_scan_ready"
        marker.unlink(missing_ok=True)

        checker = subprocess.Popen(
            [
                sys.executable,
                "-I",
                "-S",
                str(self.script),
                "--project-root",
                str(self.project),
                "check-all",
            ],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(lambda: checker.kill() if checker.poll() is None else None)
        deadline = time.monotonic() + 5
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(marker.exists(), "check-all did not reach the scan boundary")

        publisher = subprocess.Popen(
            [
                sys.executable,
                str(
                    self.project
                    / "code/utils/results_pipeline/results_pipeline.py"
                ),
                "run",
                "--caller-allowance-seconds",
                "3600",
                "--plan",
                plan,
                "--bundle",
                bundle,
                "--receipt",
                receipt,
                "--",
                sys.executable,
                "code/generate_concurrent_result.py",
            ],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(lambda: publisher.kill() if publisher.poll() is None else None)
        time.sleep(0.2)
        self.assertIsNone(publisher.poll(), "publisher bypassed check-all's shared lease")
        self.assertFalse((self.project / analysis).exists())

        checker_stdout, checker_stderr = checker.communicate(timeout=10)
        self.assertEqual(checker.returncode, 0, checker_stderr)
        inventory = json.loads(checker_stdout)
        self.assertEqual(inventory["status"], "UNCHANGED")
        self.assertNotIn(analysis, {entry["analysis"] for entry in inventory["analyses"]})
        publisher_stdout, publisher_stderr = publisher.communicate(timeout=10)
        self.assertEqual(publisher.returncode, 0, publisher_stdout + publisher_stderr)
        self.assertEqual(json.loads(publisher_stdout)["status"], "PENDING_ACTIVATION")
        self.assertTrue((self.project / analysis).is_file())

    def test_deployed_check_all_does_not_import_project_shadow_module(self) -> None:
        shadow = self.project / "code/utils/secrets.py"
        marker = self.project / "shadow-imported"
        shadow.write_text(
            "from pathlib import Path\nPath('shadow-imported').write_text('executed\\n')\n"
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertFalse(marker.exists())
        self.assertFalse((self.project / "code/utils/__pycache__").exists())

    def test_retired_stale_verifier_does_not_block_live_analysis(self) -> None:
        analysis = "output/stage3a/empirical_analysis_v1_a1.md"
        (self.project / analysis).write_text(self.report.read_text())
        paths = self.run_tool("paths", "--analysis", analysis)
        (self.project / str(paths["verify_script"])).write_text("print('main', 1.0)\n")
        manifest = self.run_tool("snapshot", "--analysis", analysis)
        self.write_pass_result(self.project / str(paths["verify_result"]), manifest)
        self.register_analysis(analysis, "retired")

        empirical = self.project / "code/empirical.py"
        empirical.write_text(empirical.read_text() + "# live repair\n")
        self.refresh_result()
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "UNCHANGED")
        entries = {item["analysis"]: item for item in inventory["analyses"]}
        self.assertEqual(entries[analysis]["status"], "EXCLUDED_RETIRED")

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

    def test_generated_bytecode_converges_after_one_refresh(self) -> None:
        source = self.project / "code/generated_dependency.py"
        source.write_text("VALUE = 1\n")
        self.refresh_result()
        compile_command = [
            sys.executable,
            "-c",
            "import py_compile; py_compile.compile('code/generated_dependency.py', doraise=True)",
        ]
        subprocess.run(compile_command, cwd=self.project, check=True)
        first = self.run_tool("check-all")
        self.assertEqual(first["status"], "CHANGED")
        self.refresh_result()
        subprocess.run(compile_command, cwd=self.project, check=True)
        converged = self.run_tool("check-all")
        self.assertEqual(converged["status"], "UNCHANGED")

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
