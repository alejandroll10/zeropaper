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
ANALYSIS_CONTRACT_UTILITY = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "utils"
    / "results_pipeline"
    / "analysis_contract.py"
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
        shutil.copy2(
            ANALYSIS_CONTRACT_UTILITY,
            self.project / "code" / "utils" / "results_pipeline" / "analysis_contract.py",
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

    def write_empirical_runner_fixture(
        self, *, analysis: str, plan: str, producer: str
    ) -> None:
        input_path = "data/empirical_input.json"
        baseline_path = "output/analysis_specs/baseline_v1.json"
        contract_path = f"output/analysis_specs/{Path(analysis).stem}.contract.json"
        execution_path = analysis.removesuffix(".md") + "_execution.json"
        (self.project / input_path).parent.mkdir(parents=True, exist_ok=True)
        (self.project / input_path).write_text("[1, 2, 3]\n")
        (self.project / baseline_path).parent.mkdir(parents=True, exist_ok=True)
        baseline = {
            "schema_version": 1,
            "record_kind": "project_baseline",
            "baseline_id": "manifest.fixture.v1",
            "definitions": {},
        }

        def semantic_digest(value: object) -> str:
            encoded = json.dumps(
                value, sort_keys=True, separators=(",", ":")
            ).encode()
            return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

        contract = {
            "schema_version": 1,
            "record_kind": "analysis_contract",
            "analysis_id": "main",
            "purpose": "Exercise empirical receipt publication.",
            "baseline": {
                "path": baseline_path,
                "semantic_digest": semantic_digest(baseline),
            },
            "effective": {
                "inputs": {
                    "panel": {
                        "description": "Frozen fixture observations",
                        "access": "local",
                        "snapshot": "fixture-v1",
                        "purpose": "Primary observations",
                    }
                },
                "samples": {
                    "main": {
                        "population": "Fixture observations",
                        "observation_unit": "row",
                        "observation_key": "id",
                        "time": {"start": 1, "end": 3},
                        "steps": {
                            "filter": {
                                "description": "Keep all observations",
                                "uses": ["panel"],
                                "produces": ["analysis_panel"],
                                "rule": "all fixture rows",
                            }
                        },
                        "step_order": ["filter"],
                        "purpose": "Primary estimation sample",
                    }
                },
                "variables": {
                    "outcome": {
                        "definition": "Fixture value",
                        "input_ids": ["panel"],
                        "timing": "contemporaneous",
                        "unit": "points",
                        "construction": "identity",
                        "missing_policy": "none",
                        "roles": ["outcome"],
                        "purpose": "Primary outcome",
                    }
                },
                "procedures": {
                    "estimate": {
                        "target": "Mean outcome",
                        "method": "arithmetic mean",
                        "sample_ids": ["main"],
                        "variable_ids": ["outcome"],
                        "inference_id": "plain",
                        "result_ids": ["main.estimate"],
                        "settings": {"weights": "none"},
                        "purpose": "Primary estimate",
                    }
                },
                "inference": {
                    "plain": {
                        "method": "descriptive",
                        "uncertainty_target": "none",
                        "purpose": "Fixture inference",
                    }
                },
                "outputs": {
                    "main.estimate": {
                        "description": "Mean fixture value",
                        "procedure_ids": ["estimate"],
                        "target": "mean",
                        "unit": "points",
                        "presentation": {"decimals": 1},
                        "purpose": "Headline result",
                    }
                },
            },
            "deviations": [],
        }
        execution = {
            "schema_version": 1,
            "analysis_id": "main",
            "contract_digest": semantic_digest(contract),
            "samples": {
                "main": {
                    "observed_time": {"start": 1, "end": 3},
                    "key_diagnostics": {
                        "is_unique": True,
                        "duplicate_key_count": {"value": 0, "unit": "keys"},
                    },
                    "steps": {
                        "filter": {
                            "counts": {
                                "rows.in": {"value": 3, "unit": "observations"},
                                "rows.out": {"value": 3, "unit": "observations"},
                            },
                            "flow": {
                                "inputs": {"panel": "rows.in"},
                                "outputs": {"analysis_panel": "rows.out"},
                            },
                            "fingerprint": "sha256:" + "0" * 64,
                        }
                    },
                }
            },
            "procedures": {
                "estimate": {
                    "fixed_settings": {"weights": "none"},
                    "decisions": {},
                    "counts": {"rows": {"value": 3, "unit": "observations"}},
                }
            },
        }
        producer_inputs = [input_path, baseline_path, contract_path]
        (self.project / baseline_path).write_text(json.dumps(baseline) + "\n")
        (self.project / contract_path).write_text(json.dumps(contract) + "\n")
        producer_path = self.project / producer
        producer_path.parent.mkdir(parents=True, exist_ok=True)
        producer_path.write_text(
            "import json, os, pathlib\n"
            "root = pathlib.Path.cwd()\n"
            f"(root / {analysis!r}).write_text({self.report_text!r})\n"
            f"(root / {execution_path!r}).write_text({(json.dumps(execution) + chr(10))!r})\n"
            "payload = {\n"
            "  'schema_version': 1,\n"
            f"  'producer': {{'name': 'manifest-test', 'code': [{producer!r}],\n"
            f"               'inputs': {producer_inputs!r}, 'reproducibility': 'captured'}},\n"
            "  'results': {'main.estimate': {'description': 'Mean fixture value',\n"
            "               'value': 1.0, 'unit': 'points',\n"
            "               'display': {'decimals': 1}, 'analysis_id': 'main'}},\n"
            f"  'artifacts': [{{'path': {analysis!r}, 'description': 'Analysis report'}},\n"
            f"                {{'path': {execution_path!r}, 'description': 'Execution summary'}}],\n"
            f"  'renderer': {{'code': [], 'inputs': [{analysis!r}]}}, 'exhibits': []\n"
            "}\n"
            "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(payload) + '\\n')\n"
        )
        (self.project / plan).write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "producer_code": [producer],
                    "producer_inputs": producer_inputs,
                    "artifacts": [analysis, execution_path],
                    "renderer_code": [],
                    "renderer_inputs": [analysis],
                    "exhibits": [],
                    "network_access": False,
                    "analyses": {
                        "main": {
                            "contract": contract_path,
                            "execution_summary": execution_path,
                            "input_bindings": {"panel": [input_path]},
                        }
                    },
                }
            )
            + "\n"
        )

    def register_analysis(
        self,
        analysis: str,
        lifecycle: str,
        *,
        receipt: str | None = None,
        supersedes: list[str] | None = None,
        plan: str | None = None,
        bundle: str | None = None,
        artifacts: list[str] | None = None,
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
        artifacts = artifacts or [analysis]
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
                    "artifacts": artifacts,
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
                        "artifacts": [
                            self.file_fingerprint(path) for path in artifacts
                        ],
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

    def test_check_all_warns_but_accepts_unbound_regular_plan(self) -> None:
        plan = (
            self.project
            / "output/stage3a/empirical_analysis_vretired_a2_results.plan.json"
        )
        plan.write_text("{}\n")
        inventory = self.run_tool("check-all")
        relative = plan.relative_to(self.project).as_posix()
        self.assertEqual(inventory["status"], "UNCHANGED")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(
            inventory["warnings"],
            [
                {
                    "path": relative,
                    "warning": "unbound pre-publication plan is not live result evidence",
                }
            ],
        )

    def test_check_all_rejects_unbound_nonregular_plan(self) -> None:
        target = self.project / "outside_plan.json"
        target.write_text("{}\n")
        plan = (
            self.project
            / "output/stage3a/empirical_analysis_vretired_a3_results.plan.json"
        )
        plan.symlink_to(target)
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            plan.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_rejects_unbound_execution_summary(self) -> None:
        execution = (
            self.project
            / "output/stage3a/empirical_analysis_vorphan_execution.json"
        )
        execution.write_text("{}\n")
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            execution.relative_to(self.project).as_posix(),
            {item["path"] for item in inventory["artifact_errors"]},
        )

    def test_check_all_rejects_reserved_plan_owned_by_nonempirical_receipt(self) -> None:
        report = self.project / "output/ordinary_report.md"
        report.write_text("# Ordinary result\n")
        plan = "output/stage3a/empirical_analysis_vghost_results.plan.json"
        self.register_analysis(
            report.relative_to(self.project).as_posix(),
            "active",
            receipt="output/ordinary_results.receipt.json",
            plan=plan,
            bundle="output/ordinary_results.json",
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            plan,
            {item["path"] for item in inventory["artifact_errors"]},
        )
        self.assertNotIn(plan, {item["path"] for item in inventory["warnings"]})

    def test_check_all_rejects_reserved_plan_used_as_nonempirical_bundle(self) -> None:
        report = self.project / "output/ordinary_report.md"
        report.write_text("# Ordinary result\n")
        bundle = "output/stage3a/empirical_analysis_vghost_results.plan.json"
        self.register_analysis(
            report.relative_to(self.project).as_posix(),
            "active",
            receipt="output/ordinary_results.receipt.json",
            plan="output/ordinary_results.plan.json",
            bundle=bundle,
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["status"], "CHANGED")
        self.assertIn(
            bundle,
            {item["path"] for item in inventory["artifact_errors"]},
        )
        self.assertNotIn(bundle, {item["path"] for item in inventory["warnings"]})

    def test_check_all_rejects_matching_analysis_cross_role_artifacts(self) -> None:
        wrong_roles: list[str] = []
        for label, suffix in (
            ("roleplan", "_results.plan.json"),
            ("roleexecution", "_execution.json"),
        ):
            analysis = f"output/stage3a/empirical_analysis_v{label}.md"
            (self.project / analysis).write_text(self.report_text)
            wrong_role = analysis.removesuffix(".md") + suffix
            self.register_analysis(
                analysis,
                "retired",
                receipt=f"output/{label}_results.receipt.json",
                plan=f"output/{label}_results.plan.json",
                bundle=wrong_role,
            )
            wrong_roles.append(wrong_role)
        inventory = self.run_tool("check-all")
        errors = {item["path"] for item in inventory["artifact_errors"]}
        self.assertTrue(set(wrong_roles).issubset(errors), inventory)
        warnings = {item["path"] for item in inventory["warnings"]}
        self.assertTrue(set(wrong_roles).isdisjoint(warnings))

    def test_check_all_rejects_v2_execution_shaped_artifact(self) -> None:
        analysis = "output/stage3a/empirical_analysis_vv2execution.md"
        execution = analysis.removesuffix(".md") + "_execution.json"
        (self.project / analysis).write_text(self.report_text)
        (self.project / execution).write_text("{}\n")
        self.register_analysis(
            analysis,
            "retired",
            artifacts=[analysis, execution],
        )
        inventory = self.run_tool("check-all")
        self.assertTrue(
            any(
                "not uniquely declared by v3 lineage" in item["error"]
                for item in inventory["artifact_errors"]
            ),
            inventory,
        )

    def test_check_all_rejects_execution_artifact_missing_from_v3_lineage(self) -> None:
        self.write_empty_registry()
        analysis = "output/stage3a/empirical_analysis.md"
        plan = "output/stage3a/empirical_analysis_results.plan.json"
        bundle = "output/stage3a/empirical_analysis_results.json"
        receipt = "output/stage3a/empirical_analysis_results.receipt.json"
        for relative in (analysis, bundle, receipt):
            path = self.project / relative
            if path.exists():
                path.unlink()
        self.write_empirical_runner_fixture(
            analysis=analysis,
            plan=plan,
            producer="code/generate_empirical_result.py",
        )
        run = self.run_results_pipeline(
            "run-empirical",
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
            "code/generate_empirical_result.py",
        )
        self.assertEqual(run["status"], "PENDING_ACTIVATION")
        receipt_path = self.project / receipt
        receipt_value = json.loads(receipt_path.read_text())
        receipt_value["lineage"][0]["execution_summary_path"] = (
            "output/stage3a/custom_execution.json"
        )
        receipt_path.write_text(json.dumps(receipt_value, indent=2) + "\n")
        registry_path = self.project / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text())
        registry["receipt_fingerprints"][receipt] = self.file_fingerprint(receipt)
        registry_path.write_text(json.dumps(registry, indent=2) + "\n")
        inventory = self.run_tool("check-all")
        self.assertTrue(
            any(
                "not uniquely declared by v3 lineage" in item["error"]
                for item in inventory["artifact_errors"]
            ),
            inventory,
        )

    def test_check_all_rejects_plan_inside_receipt_directory_snapshot(self) -> None:
        self.write_empty_registry()
        for relative in (
            "output/stage3a/empirical_analysis.md",
            "output/stage3a/empirical_analysis_results.plan.json",
            "output/stage3a/empirical_analysis_results.json",
            "output/stage3a/empirical_analysis_results.receipt.json",
        ):
            path = self.project / relative
            if path.exists():
                path.unlink()
        orphan = (
            "output/stage3a/"
            "empirical_analysis_vdirectory_results.plan.json"
        )
        (self.project / orphan).write_text("{}\n")
        producer = "code/generate_ordinary_directory_result.py"
        (self.project / producer).write_text(
            "import json, os, pathlib\n"
            "root = pathlib.Path.cwd()\n"
            "report = 'output/ordinary_directory_report.md'\n"
            "(root / report).write_text('# Ordinary result\\n')\n"
            "bundle = {\n"
            "  'schema_version': 1,\n"
            f"  'producer': {{'name': 'directory-test', 'code': [{producer!r}],\n"
            "               'inputs': ['output/stage3a'],\n"
            "               'reproducibility': 'captured'},\n"
            "  'results': {'ordinary.value': {'description': 'Value', 'value': 1}},\n"
            "  'artifacts': [{'path': report, 'description': 'Ordinary report'}],\n"
            "  'renderer': {'code': []}, 'exhibits': []\n"
            "}\n"
            "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle) + '\\n')\n"
        )
        plan = "output/ordinary_directory_results.plan.json"
        (self.project / plan).write_text(
            json.dumps(
                {
                    "plan_version": 1,
                    "producer_code": [producer],
                    "producer_inputs": ["output/stage3a"],
                    "artifacts": ["output/ordinary_directory_report.md"],
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
            plan,
            "--bundle",
            "output/ordinary_directory_results.json",
            "--receipt",
            "output/ordinary_directory_results.receipt.json",
            "--",
            sys.executable,
            producer,
        )
        self.assertEqual(run["status"], "PENDING_ACTIVATION")
        inventory = self.run_tool("check-all")
        self.assertIn(
            orphan,
            {item["path"] for item in inventory["artifact_errors"]},
        )
        self.assertNotIn(orphan, {item["path"] for item in inventory["warnings"]})

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
        self.write_empirical_runner_fixture(
            analysis="output/stage3a/empirical_analysis.md",
            plan="output/stage3a/empirical_analysis_results.plan.json",
            producer="code/generate_empirical_result.py",
        )
        run = self.run_results_pipeline(
            "run-empirical",
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
        paths = self.run_tool(
            "paths", "--analysis", "output/stage3a/empirical_analysis.md"
        )
        manifest = self.run_tool(
            "snapshot", "--analysis", "output/stage3a/empirical_analysis.md"
        )
        self.write_pass_result(
            self.project / str(paths["verify_result"]), manifest
        )
        inventory = self.run_tool("check-all")
        self.assertEqual(inventory["artifact_errors"], [])
        self.assertEqual(inventory["status"], "UNCHANGED")
        self.assertEqual(inventory["analyses"][0]["lifecycle"], "pending")

    def test_check_all_holds_publication_lock_through_verdict(self) -> None:
        analysis = "output/stage3a/empirical_analysis_vconcurrent.md"
        plan = "output/concurrent_empirical_results.plan.json"
        bundle = "output/stage3a/empirical_analysis_vconcurrent_results.json"
        receipt = "output/stage3a/empirical_analysis_vconcurrent_results.receipt.json"
        self.write_empirical_runner_fixture(
            analysis=analysis,
            plan=plan,
            producer="code/generate_concurrent_result.py",
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
                "run-empirical",
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
