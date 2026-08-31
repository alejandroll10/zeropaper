#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / "deploy_assets/templates/utils/results_pipeline/analysis_contract.py"
RUNNER = REPO / "deploy_assets/templates/utils/results_pipeline/results_pipeline.py"
SPEC = importlib.util.spec_from_file_location("analysis_contract", HELPER)
assert SPEC is not None and SPEC.loader is not None
contract_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract_module)
RUNNER_SPEC = importlib.util.spec_from_file_location("results_pipeline", RUNNER)
assert RUNNER_SPEC is not None and RUNNER_SPEC.loader is not None
runner_module = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(runner_module)


def baseline() -> dict:
    return {
        "schema_version": 1,
        "record_kind": "project_baseline",
        "baseline_id": "paper.v1",
        "definitions": {},
    }


def contract() -> dict:
    value = {
        "schema_version": 1,
        "record_kind": "analysis_contract",
        "analysis_id": "main",
        "purpose": "Estimate the paper's primary empirical contrast.",
        "baseline": {"path": "output/analysis_specs/baseline_v1.json", "semantic_digest": ""},
        "effective": {
            "inputs": {
                "panel": {
                    "description": "Frozen test panel", "access": "local",
                    "snapshot": "fixture-v1", "purpose": "Primary observations",
                }
            },
            "samples": {
                "main": {
                    "population": "Eligible observations", "observation_unit": "row",
                    "observation_key": ["id", "date"], "time": {"start": "2020-01-01", "end": "2020-12-31"},
                    "steps": {
                        "filter": {
                            "description": "Apply declared eligibility", "uses": ["panel"],
                            "produces": ["analysis_panel"], "rule": "value is observed",
                        }
                    },
                    "step_order": ["filter"], "purpose": "Primary estimation sample",
                }
            },
            "variables": {
                "outcome": {
                    "definition": "Observed value", "input_ids": ["panel"],
                    "timing": "contemporaneous", "unit": "points", "construction": "identity",
                    "missing_policy": "excluded by sample step", "roles": ["outcome"],
                    "purpose": "Primary outcome",
                }
            },
            "procedures": {
                "estimate": {
                    "target": "Mean outcome", "method": "arithmetic mean", "sample_ids": ["main"],
                    "variable_ids": ["outcome"], "inference_id": "plain",
                    "result_ids": ["main.mean"], "settings": {"weights": "none"},
                    "decision_rules": {"fallback": {"description": "Fallback action", "allowed": ["none", "winsorize"]}},
                    "purpose": "Primary estimate",
                }
            },
            "inference": {
                "plain": {
                    "method": "descriptive", "uncertainty_target": "none",
                    "purpose": "No sampling inference in fixture",
                }
            },
            "outputs": {
                "main.mean": {
                    "description": "Mean observed value", "procedure_ids": ["estimate"],
                    "target": "mean", "unit": "points", "presentation": {"decimals": 1},
                    "purpose": "Headline result",
                }
            },
        },
        "deviations": [],
    }
    value["baseline"]["semantic_digest"] = contract_module.semantic_digest(baseline())
    return value


def execution() -> dict:
    value = {
        "schema_version": 1,
        "analysis_id": "main",
        "contract_digest": contract_module.semantic_digest(contract()),
        "samples": {
            "main": {
                "observed_time": {"start": "2020-01-01", "end": "2020-12-31"},
                "key_diagnostics": {
                    "is_unique": True,
                    "duplicate_key_count": {"value": 0, "unit": "keys"},
                },
                "steps": {"filter": {
                    "counts": {
                        "rows.in": {"value": 3, "unit": "observations"},
                        "rows.out": {"value": 3, "unit": "observations"},
                    },
                    "flow": {
                        "inputs": {"panel": "rows.in"},
                        "outputs": {"analysis_panel": "rows.out"},
                    },
                    "fingerprint": "sha256:" + "0" * 64,
                }},
            }
        },
        "procedures": {
            "estimate": {
                "fixed_settings": {"weights": "none"},
                "decisions": {"fallback": "none"},
                "counts": {"rows": {"value": 3, "unit": "observations"}},
            }
        },
    }
    return value


class AnalysisContractTest(unittest.TestCase):
    def test_valid_contract_and_execution(self) -> None:
        validated = contract_module.validate_contract(contract(), baseline())
        contract_module.validate_execution(execution(), validated)

    def test_cli_works_under_isolated_python(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            baseline_path = root / "baseline.json"
            contract_path = root / "contract.json"
            execution_path = root / "execution.json"
            baseline_path.write_text(json.dumps(baseline()) + "\n", encoding="utf-8")
            contract_path.write_text(json.dumps(contract()) + "\n", encoding="utf-8")
            execution_path.write_text(json.dumps(execution()) + "\n", encoding="utf-8")
            completed = subprocess.run([
                sys.executable, "-I", "-S", str(HELPER), str(contract_path),
                "--baseline", str(baseline_path), "--execution", str(execution_path),
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("contract_digest", json.loads(completed.stdout))

    def test_baseline_definition_cannot_change_in_place(self) -> None:
        base = baseline()
        base["definitions"] = {"variables": {"outcome": contract()["effective"]["variables"]["outcome"]}}
        candidate = contract()
        candidate["baseline"]["semantic_digest"] = contract_module.semantic_digest(base)
        candidate["effective"]["variables"]["outcome"]["unit"] = "percent"
        candidate["deviations"] = [{
            "paths": ["/effective/variables/outcome"], "reason": "Alternative scale",
        }]
        with self.assertRaisesRegex(contract_module.ContractError, "changed in place"):
            contract_module.validate_contract(candidate, base)

    def test_baseline_definition_cannot_be_laundered_under_new_id(self) -> None:
        base = baseline()
        base["definitions"] = deepcopy(contract()["effective"])
        candidate = contract()
        candidate["baseline"]["semantic_digest"] = contract_module.semantic_digest(base)
        candidate["effective"] = deepcopy(base["definitions"])
        clone = deepcopy(base["definitions"]["variables"]["outcome"])
        clone.update({
            "variant_of": "outcome",
            "variant_reason": "Claimed change without a scientific payload change",
        })
        candidate["effective"]["variables"]["outcome.copy"] = clone
        candidate["effective"]["procedures"]["estimate"]["variable_ids"] = [
            "outcome.copy"
        ]
        candidate["deviations"] = [{
            "paths": ["/effective/variables/outcome.copy"],
            "reason": "Claimed variable variant",
        }]
        with self.assertRaisesRegex(contract_module.ContractError, "relabels baseline ID"):
            contract_module.validate_contract(candidate, base)

    def test_scientific_exactness_distinguishes_booleans_from_numbers(self) -> None:
        base = baseline()
        base["definitions"] = deepcopy(contract()["effective"])
        base["definitions"]["procedures"]["estimate"]["settings"] = {"weights": 1}
        candidate = contract()
        candidate["baseline"]["semantic_digest"] = contract_module.semantic_digest(base)
        candidate["effective"] = deepcopy(base["definitions"])
        candidate["effective"]["procedures"]["estimate"]["settings"] = {
            "weights": True
        }
        with self.assertRaisesRegex(contract_module.ContractError, "changed in place"):
            contract_module.validate_contract(candidate, base)

        candidate = contract()
        candidate["effective"]["procedures"]["estimate"]["settings"] = {
            "weights": True
        }
        realized = execution()
        realized["contract_digest"] = contract_module.semantic_digest(candidate)
        realized["procedures"]["estimate"]["fixed_settings"] = {"weights": 1}
        with self.assertRaisesRegex(contract_module.ContractError, "fixed_settings differs"):
            contract_module.validate_execution(realized, candidate)

    def test_sample_construction_spine_cannot_be_empty_or_ambiguous(self) -> None:
        candidate = contract()
        candidate["effective"]["samples"]["main"]["steps"] = {}
        candidate["effective"]["samples"]["main"]["step_order"] = []
        with self.assertRaisesRegex(contract_module.ContractError, "steps must not be empty"):
            contract_module.validate_contract(candidate, baseline())
        candidate = contract()
        candidate["effective"]["samples"]["main"]["observation_key"] = ["id", "id"]
        with self.assertRaisesRegex(contract_module.ContractError, "contains duplicates"):
            contract_module.validate_contract(candidate, baseline())
        realized = execution()
        realized["samples"]["main"]["key_diagnostics"][
            "duplicate_key_count"
        ]["value"] = 0.5
        with self.assertRaisesRegex(contract_module.ContractError, "nonnegative integer"):
            contract_module.validate_execution(realized, contract())

    def test_stable_ids_cannot_conflict_across_analyses(self) -> None:
        first = contract()
        second = contract()
        second["analysis_id"] = "alternate"
        second["effective"]["variables"]["outcome"]["unit"] = "percent"
        with self.assertRaisesRegex(runner_module.EvidenceError, "conflicting definitions"):
            runner_module.extend_empirical_identity_index(
                {"main": first, "alternate": second}, scope="test"
            )

    def test_variant_needs_exact_deviation_coverage(self) -> None:
        base = baseline()
        base["definitions"] = {"inference": {"plain": contract()["effective"]["inference"]["plain"]}}
        candidate = contract()
        candidate["baseline"]["semantic_digest"] = contract_module.semantic_digest(base)
        candidate["effective"]["inference"].pop("plain")
        candidate["effective"]["inference"]["clustered"] = {
            "method": "clustered sandwich", "uncertainty_target": "sampling variation",
            "variant_of": "plain", "variant_reason": "Account for within-id dependence",
        }
        candidate["effective"]["procedures"]["estimate"]["inference_id"] = "clustered"
        paths = ["/effective/inference/plain", "/effective/inference/clustered"]
        candidate["deviations"] = [{"paths": paths, "reason": "Dependence-robust inference"}]
        contract_module.validate_contract(candidate, base)
        candidate["deviations"][0]["paths"].pop()
        with self.assertRaisesRegex(contract_module.ContractError, "deviations do not exactly cover"):
            contract_module.validate_contract(candidate, base)

    def test_adaptive_realization_must_be_predeclared(self) -> None:
        realized = execution()
        realized["procedures"]["estimate"]["decisions"]["fallback"] = "drop-outliers"
        with self.assertRaisesRegex(contract_module.ContractError, "outside its allowed domain"):
            contract_module.validate_execution(realized, contract())

    def test_numeric_adaptive_domain_accepts_only_in_range_realizations(self) -> None:
        candidate = contract()
        candidate["effective"]["procedures"]["estimate"]["decision_rules"][
            "fallback"
        ]["allowed"] = {"type": "number", "minimum": 0.0, "exclusive_maximum": 1.0}
        realized = execution()
        realized["contract_digest"] = contract_module.semantic_digest(candidate)
        realized["procedures"]["estimate"]["decisions"]["fallback"] = 0.25
        contract_module.validate_execution(realized, candidate)
        realized["procedures"]["estimate"]["decisions"]["fallback"] = 1.0
        with self.assertRaisesRegex(contract_module.ContractError, "outside its allowed domain"):
            contract_module.validate_execution(realized, candidate)
        candidate["effective"]["procedures"]["estimate"]["decision_rules"][
            "fallback"
        ]["allowed"] = {"type": "number", "minimum": 0.0}
        with self.assertRaisesRegex(contract_module.ContractError, "upper bound"):
            contract_module.validate_contract(candidate, baseline())
        candidate["effective"]["procedures"]["estimate"]["decision_rules"][
            "fallback"
        ]["allowed"] = {"type": "number", "maximum": 1.0}
        with self.assertRaisesRegex(contract_module.ContractError, "lower bound"):
            contract_module.validate_contract(candidate, baseline())

    def test_finite_adaptive_domain_is_type_aware(self) -> None:
        candidate = contract()
        candidate["effective"]["procedures"]["estimate"]["decision_rules"][
            "fallback"
        ]["allowed"] = [1]
        realized = execution()
        realized["contract_digest"] = contract_module.semantic_digest(candidate)
        realized["procedures"]["estimate"]["decisions"]["fallback"] = True
        with self.assertRaisesRegex(contract_module.ContractError, "outside its allowed domain"):
            contract_module.validate_execution(realized, candidate)
        candidate["effective"]["procedures"]["estimate"]["decision_rules"][
            "fallback"
        ]["allowed"] = [{"choice": [1]}]
        realized["contract_digest"] = contract_module.semantic_digest(candidate)
        realized["procedures"]["estimate"]["decisions"]["fallback"] = {
            "choice": [True]
        }
        with self.assertRaisesRegex(contract_module.ContractError, "outside its allowed domain"):
            contract_module.validate_execution(realized, candidate)

    def test_output_units_and_counts_have_realizable_types(self) -> None:
        candidate = contract()
        candidate["effective"]["outputs"]["main.mean"]["unit"] = {"scale": "points"}
        with self.assertRaisesRegex(contract_module.ContractError, "unit must be a non-empty string"):
            contract_module.validate_contract(candidate, baseline())
        realized = execution()
        realized["procedures"]["estimate"]["counts"]["rows"]["value"] = -1
        with self.assertRaisesRegex(contract_module.ContractError, "nonnegative"):
            contract_module.validate_execution(realized, contract())
        realized = execution()
        realized["samples"]["main"]["steps"]["filter"]["counts"][
            "rows.out"
        ]["value"] = -1
        with self.assertRaisesRegex(contract_module.ContractError, "nonnegative"):
            contract_module.validate_execution(realized, contract())

    def test_output_graph_and_comparison_spine_fail_closed(self) -> None:
        candidate = contract()
        candidate["effective"]["procedures"] = {}
        candidate["effective"]["outputs"] = {}
        with self.assertRaisesRegex(contract_module.ContractError, "procedures must not be empty"):
            contract_module.validate_contract(candidate, baseline())
        candidate = contract()
        candidate["effective"]["outputs"]["main.mean"]["procedure_ids"] = []
        with self.assertRaisesRegex(contract_module.ContractError, "non-empty"):
            contract_module.validate_contract(candidate, baseline())
        candidate = contract()
        candidate["effective"]["outputs"]["main.mean"]["operands"] = [
            {"receipt": "output/prior_results.receipt.json", "result_id": "prior.mean"}
        ]
        candidate["effective"]["outputs"]["main.mean"]["comparability"] = None
        with self.assertRaisesRegex(contract_module.ContractError, "comparability"):
            contract_module.validate_contract(candidate, baseline())

    def test_seed_and_tuning_realizations_must_match(self) -> None:
        candidate = contract()
        candidate["effective"]["procedures"]["estimate"]["seed"] = 7
        candidate["effective"]["procedures"]["estimate"]["tuning"] = {"folds": 5}
        realized = execution()
        realized["contract_digest"] = contract_module.semantic_digest(candidate)
        realized["procedures"]["estimate"].update(
            {"seed": 8, "tuning": {"folds": 5}}
        )
        with self.assertRaisesRegex(contract_module.ContractError, "seed differs"):
            contract_module.validate_execution(realized, candidate)


class EmpiricalRunnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ("code", "data", "process_log", "output/analysis_specs", "output/stage3a"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        (self.root / "data/input.json").write_text("[1, 2, 3]\n", encoding="utf-8")
        (self.root / "output/analysis_specs/baseline_v1.json").write_text(
            json.dumps(baseline()) + "\n", encoding="utf-8"
        )
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(contract()) + "\n", encoding="utf-8"
        )
        (self.root / "process_log/results_registry.json").write_text(
            json.dumps({"kind": "result_registry", "registry_version": 1, "active": [],
                        "active_dataset_release_pairs": {}, "pending": [], "retired": [],
                        "receipt_fingerprints": {}}) + "\n", encoding="utf-8"
        )
        source = f"""import json, os, pathlib
root = pathlib.Path.cwd()
(root / 'output/stage3a/empirical_analysis_v1.md').write_text('empirical report\\n')
(root / 'output/stage3a/main_execution_v1.json').write_text({json.dumps(json.dumps(execution()))} + '\\n')
bundle = {{
  'schema_version': 1,
  'producer': {{'name': 'fixture', 'code': ['code/analyze.py'],
               'inputs': ['data/input.json', 'output/analysis_specs/baseline_v1.json',
                          'output/analysis_specs/main_v1.json'], 'reproducibility': 'captured'}},
  'results': {{'main.mean': {{'description': 'Mean observed value', 'value': 2.0,
                              'unit': 'points', 'display': {{'decimals': 1}},
                              'analysis_id': 'main'}}}},
  'artifacts': [
    {{'path': 'output/stage3a/empirical_analysis_v1.md', 'description': 'Report'}},
    {{'path': 'output/stage3a/main_execution_v1.json', 'description': 'Audit-only execution summary'}}
  ],
  'renderer': {{'code': [], 'inputs': ['output/stage3a/empirical_analysis_v1.md']}},
  'exhibits': []
}}
(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle) + '\\n')
"""
        (self.root / "code/analyze.py").write_text(source, encoding="utf-8")
        self.plan = {
            "plan_version": 1,
            "producer_code": ["code/analyze.py"],
            "producer_inputs": ["data/input.json", "output/analysis_specs/baseline_v1.json", "output/analysis_specs/main_v1.json"],
            "artifacts": ["output/stage3a/empirical_analysis_v1.md", "output/stage3a/main_execution_v1.json"],
            "renderer_code": [], "renderer_inputs": ["output/stage3a/empirical_analysis_v1.md"],
            "exhibits": [], "network_access": False,
            "analyses": {
                "main": {
                    "contract": "output/analysis_specs/main_v1.json",
                    "execution_summary": "output/stage3a/main_execution_v1.json",
                    "input_bindings": {"panel": ["data/input.json"]},
                }
            },
        }
        (self.root / "output/stage3a/results.plan.json").write_text(
            json.dumps(self.plan) + "\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def call(self, command: str, *, expected: int) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run([
            sys.executable, str(RUNNER), command,
            "--plan", "output/stage3a/results.plan.json",
            "--bundle", "output/stage3a/results.json",
            "--receipt", "output/stage3a/results.receipt.json",
            "--", sys.executable, "code/analyze.py",
        ], cwd=self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        return completed

    def test_ordinary_run_rejects_empirical_report(self) -> None:
        self.call("run", expected=2)

    def test_empirical_run_records_v3_lineage_and_hides_summary_from_renderer(self) -> None:
        self.call("run-empirical", expected=0)
        receipt = json.loads((self.root / "output/stage3a/results.receipt.json").read_text())
        self.assertEqual(receipt["receipt_version"], 3)
        self.assertEqual(receipt["lineage"][0]["analysis_id"], "main")
        self.assertEqual(receipt["lineage"][0]["result_ids"], ["main.mean"])
        verified = subprocess.run([
            sys.executable, str(RUNNER), "verify", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results.receipt.json",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        self.assertEqual(json.loads(verified.stdout)["status"], "PASS")

    def test_ordinary_run_cannot_widen_declared_renderer_subset(self) -> None:
        source = (self.root / "code/analyze.py").read_text(encoding="utf-8")
        source = source.replace(
            "output/stage3a/empirical_analysis_v1.md",
            "output/stage3a/generic_report_v1.md",
        )
        source = source.replace(
            "  'renderer': {'code': [], 'inputs': "
            "['output/stage3a/generic_report_v1.md']},",
            "  'renderer': {'code': []},",
        )
        (self.root / "code/analyze.py").write_text(source, encoding="utf-8")
        self.plan.pop("analyses")
        self.plan["artifacts"][0] = "output/stage3a/generic_report_v1.md"
        self.plan["renderer_inputs"] = ["output/stage3a/generic_report_v1.md"]
        (self.root / "output/stage3a/results.plan.json").write_text(
            json.dumps(self.plan) + "\n", encoding="utf-8"
        )
        rejected = self.call("run", expected=2)
        self.assertIn("does not exactly match", rejected.stderr)

    def test_baseline_migration_is_staged_but_blocks_paper_audit(self) -> None:
        self.call("run-empirical", expected=0)
        activated = subprocess.run([
            sys.executable, str(RUNNER), "activate", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results.receipt.json",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(activated.returncode, 0, activated.stdout + activated.stderr)
        second_baseline = baseline()
        second_baseline["baseline_id"] = "paper.v2"
        second_contract = contract()
        second_contract["baseline"] = {
            "path": "output/analysis_specs/baseline_v2.json",
            "semantic_digest": contract_module.semantic_digest(second_baseline),
        }
        (self.root / "output/analysis_specs/baseline_v2.json").write_text(
            json.dumps(second_baseline) + "\n", encoding="utf-8"
        )
        (self.root / "output/analysis_specs/main_v2.json").write_text(
            json.dumps(second_contract) + "\n", encoding="utf-8"
        )
        second_plan = deepcopy(self.plan)
        second_plan["producer_inputs"] = [
            "data/input.json", "output/analysis_specs/baseline_v2.json",
            "output/analysis_specs/main_v2.json",
        ]
        second_plan["artifacts"] = [
            "output/stage3a/empirical_analysis_v2.md",
            "output/stage3a/main_execution_v2.json",
        ]
        second_plan["renderer_inputs"] = ["output/stage3a/empirical_analysis_v2.md"]
        second_plan["analyses"]["main"]["contract"] = "output/analysis_specs/main_v2.json"
        second_plan["analyses"]["main"]["execution_summary"] = "output/stage3a/main_execution_v2.json"
        second_plan["producer_code"] = ["code/analyze_v2.py"]
        (self.root / "output/stage3a/results_v2.plan.json").write_text(
            json.dumps(second_plan) + "\n", encoding="utf-8"
        )
        second_execution = execution()
        second_execution["contract_digest"] = contract_module.semantic_digest(second_contract)
        source = (self.root / "code/analyze.py").read_text(encoding="utf-8")
        source = source.replace("code/analyze.py", "code/analyze_v2.py")
        source = source.replace("baseline_v1.json", "baseline_v2.json")
        source = source.replace("main_v1.json", "main_v2.json")
        source = source.replace("empirical_analysis_v1.md", "empirical_analysis_v2.md")
        source = source.replace("main_execution_v1.json", "main_execution_v2.json")
        old_execution = json.dumps(json.dumps(execution()))
        source = source.replace(old_execution, json.dumps(json.dumps(second_execution)))
        (self.root / "code/analyze_v2.py").write_text(source, encoding="utf-8")
        created = subprocess.run([
            sys.executable, str(RUNNER), "run-empirical", "--project-root", str(self.root),
            "--plan", "output/stage3a/results_v2.plan.json",
            "--bundle", "output/stage3a/results_v2.json",
            "--receipt", "output/stage3a/results_v2_results.receipt.json",
            "--", sys.executable, "code/analyze_v2.py",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
        activated = subprocess.run([
            sys.executable, str(RUNNER), "activate", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results_v2_results.receipt.json",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(activated.returncode, 0, activated.stdout + activated.stderr)
        (self.root / "output/evidence").mkdir()
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text("No exhibits.\n", encoding="utf-8")
        rejected = subprocess.run([
            sys.executable, str(RUNNER), "prepare-audit", "--project-root", str(self.root),
            "--checkpoint", "stage4", "--output", "output/evidence/input.json",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
        self.assertIn("multiple project baselines", rejected.stderr)

    def test_reference_analysis_and_operand_receipts_must_resolve(self) -> None:
        candidate = contract()
        candidate["reference_analysis_id"] = "does.not.exist"
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(candidate) + "\n", encoding="utf-8"
        )
        rejected = self.call("run-empirical", expected=2)
        self.assertIn("same receipt", rejected.stderr)

        candidate = contract()
        candidate["effective"]["outputs"]["main.mean"].update({
            "operands": [{
                "receipt": "output/stage3a/results.receipt.json",
                "result_id": "prior.mean",
            }],
            "comparability": {"alignment": "same unit"},
        })
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(candidate) + "\n", encoding="utf-8"
        )
        (self.root / "output/stage3a/results.plan.json").write_text(
            json.dumps(self.plan) + "\n", encoding="utf-8"
        )
        rejected = self.call("run-empirical", expected=2)
        self.assertIn("unknown current result", rejected.stderr)

        candidate = contract()
        candidate["effective"]["procedures"]["estimate"]["result_ids"] = [
            "main.mean", "main.other",
        ]
        candidate["effective"]["outputs"]["main.mean"].update({
            "operands": [{
                "receipt": "output/stage3a/results.receipt.json",
                "result_id": "main.other",
            }],
            "comparability": {"alignment": "same unit"},
        })
        candidate["effective"]["outputs"]["main.other"] = {
            "description": "Cyclic comparison", "procedure_ids": ["estimate"],
            "target": "comparison", "unit": "points",
            "presentation": {"decimals": 1}, "purpose": "Adversarial cycle",
            "operands": [{
                "receipt": "output/stage3a/results.receipt.json",
                "result_id": "main.mean",
            }],
            "comparability": {"alignment": "same unit"},
        }
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(candidate) + "\n", encoding="utf-8"
        )
        rejected = self.call("run-empirical", expected=2)
        self.assertIn("comparison operand cycle", rejected.stderr)

    def test_bound_contract_path_cannot_change_during_replacement(self) -> None:
        self.call("run-empirical", expected=0)
        activated = subprocess.run([
            sys.executable, str(RUNNER), "activate", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results.receipt.json",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(activated.returncode, 0, activated.stdout + activated.stderr)
        changed = contract()
        changed["notes"] = "illicit in-place edit"
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(changed) + "\n", encoding="utf-8"
        )
        retire_rejected = subprocess.run([
            sys.executable, str(RUNNER), "retire", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results.receipt.json",
            "--reason", "attempt to launder changed contract through retirement",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(
            retire_rejected.returncode, 2,
            retire_rejected.stdout + retire_rejected.stderr,
        )
        self.assertIn("changed in place", retire_rejected.stderr)
        next_plan = deepcopy(self.plan)
        next_plan["artifacts"] = [
            "output/stage3a/empirical_analysis_v2.md",
            "output/stage3a/main_execution_v2.json",
        ]
        next_plan["renderer_inputs"] = ["output/stage3a/empirical_analysis_v2.md"]
        next_plan["analyses"]["main"]["execution_summary"] = (
            "output/stage3a/main_execution_v2.json"
        )
        (self.root / "output/stage3a/results_v2.plan.json").write_text(
            json.dumps(next_plan) + "\n", encoding="utf-8"
        )
        rejected = subprocess.run([
            sys.executable, str(RUNNER), "run-empirical", "--project-root", str(self.root),
            "--plan", "output/stage3a/results_v2.plan.json",
            "--bundle", "output/stage3a/results_v2.json",
            "--receipt", "output/stage3a/results_v2_results.receipt.json",
            "--supersedes", "output/stage3a/results.receipt.json",
            "--", sys.executable, "code/analyze.py",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
        self.assertIn("changed in place", rejected.stderr)

    def test_reference_analysis_graph_must_be_acyclic(self) -> None:
        first = contract()
        first["reference_analysis_id"] = "alternate"
        second = contract()
        second["analysis_id"] = "alternate"
        second["reference_analysis_id"] = "main"
        procedure = second["effective"]["procedures"].pop("estimate")
        procedure["result_ids"] = ["alternate.mean"]
        second["effective"]["procedures"]["alternate.estimate"] = procedure
        output = second["effective"]["outputs"].pop("main.mean")
        output["procedure_ids"] = ["alternate.estimate"]
        second["effective"]["outputs"]["alternate.mean"] = output
        (self.root / "output/analysis_specs/main_v1.json").write_text(
            json.dumps(first) + "\n", encoding="utf-8"
        )
        (self.root / "output/analysis_specs/alternate_v1.json").write_text(
            json.dumps(second) + "\n", encoding="utf-8"
        )
        self.plan["producer_inputs"].append(
            "output/analysis_specs/alternate_v1.json"
        )
        self.plan["artifacts"].append(
            "output/stage3a/alternate_execution_v1.json"
        )
        self.plan["analyses"]["alternate"] = {
            "contract": "output/analysis_specs/alternate_v1.json",
            "execution_summary": "output/stage3a/alternate_execution_v1.json",
            "input_bindings": {"panel": ["data/input.json"]},
        }
        (self.root / "output/stage3a/results.plan.json").write_text(
            json.dumps(self.plan) + "\n", encoding="utf-8"
        )
        rejected = self.call("run-empirical", expected=2)
        self.assertIn("reference_analysis_id cycle", rejected.stderr)

    def test_rejected_pending_receipt_cannot_become_an_operand(self) -> None:
        self.call("run-empirical", expected=0)
        retired = subprocess.run([
            sys.executable, str(RUNNER), "retire", "--project-root", str(self.root),
            "--receipt", "output/stage3a/results.receipt.json",
            "--reason", "substantive audit rejected this pending attempt",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(retired.returncode, 0, retired.stdout + retired.stderr)

        candidate = contract()
        candidate["effective"]["outputs"]["main.mean"].update({
            "operands": [{
                "receipt": "output/stage3a/results.receipt.json",
                "result_id": "main.mean",
            }],
            "comparability": {"alignment": "same unit and population"},
        })
        (self.root / "output/analysis_specs/main_v2.json").write_text(
            json.dumps(candidate) + "\n", encoding="utf-8"
        )
        next_plan = deepcopy(self.plan)
        next_plan["producer_inputs"] = [
            "data/input.json", "output/analysis_specs/baseline_v1.json",
            "output/analysis_specs/main_v2.json",
            "output/stage3a/results.receipt.json", "output/stage3a/results.json",
        ]
        next_plan["artifacts"] = [
            "output/stage3a/empirical_analysis_v2.md",
            "output/stage3a/main_execution_v2.json",
        ]
        next_plan["renderer_inputs"] = ["output/stage3a/empirical_analysis_v2.md"]
        next_plan["analyses"]["main"] = {
            "contract": "output/analysis_specs/main_v2.json",
            "execution_summary": "output/stage3a/main_execution_v2.json",
            "input_bindings": {"panel": [
                "data/input.json", "output/stage3a/results.receipt.json",
                "output/stage3a/results.json",
            ]},
        }
        (self.root / "output/stage3a/results_v2.plan.json").write_text(
            json.dumps(next_plan) + "\n", encoding="utf-8"
        )
        (self.root / "code/analyze.py").write_text(
            (self.root / "code/analyze.py").read_text(encoding="utf-8") +
            "\n# rejected producer changed after retirement\n",
            encoding="utf-8",
        )
        rejected = subprocess.run([
            sys.executable, str(RUNNER), "run-empirical", "--project-root", str(self.root),
            "--plan", "output/stage3a/results_v2.plan.json",
            "--bundle", "output/stage3a/results_v2.json",
            "--receipt", "output/stage3a/results_v2_results.receipt.json",
            "--", sys.executable, "code/analyze.py",
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
        self.assertIn("not eligible empirical comparison evidence", rejected.stderr)

    def test_external_operand_snapshot_check_covers_producer_code(self) -> None:
        self.call("run-empirical", expected=0)
        receipt = runner_module.validate_receipt_contract(
            self.root, self.root / "output/stage3a/results.receipt.json"
        )
        (self.root / "code/analyze.py").write_text(
            (self.root / "code/analyze.py").read_text(encoding="utf-8") +
            "\n# stale producer code\n",
            encoding="utf-8",
        )
        failures = runner_module.empirical_operand_snapshot_failures(
            self.root, receipt, "operand"
        )
        self.assertTrue(
            any("producer_run.code" in failure for failure in failures), failures
        )

    def test_multihop_handoff_and_terminal_retirement_dependency(self) -> None:
        paths = {
            name: f"output/stage3a/{name}_results.receipt.json"
            for name in ("ancestor", "middle", "terminal", "dependent")
        }
        receipts = {
            "ancestor": {"receipt_version": 2, "supersedes": []},
            "middle": {"receipt_version": 2, "supersedes": [paths["ancestor"]]},
            "terminal": {"receipt_version": 2, "supersedes": [paths["middle"]]},
            "dependent": {"receipt_version": 3, "supersedes": []},
        }
        for name, value in receipts.items():
            (self.root / paths[name]).write_text(
                json.dumps(value) + "\n", encoding="utf-8"
            )
        registry = {
            "active": [paths["terminal"], paths["dependent"]],
            "pending": [],
            "retired": [
                {
                    "receipt": paths["ancestor"], "superseded_by": paths["middle"],
                    "last_fingerprint": runner_module.fingerprint(
                        self.root, paths["ancestor"]
                    ),
                },
                {
                    "receipt": paths["middle"], "superseded_by": paths["terminal"],
                    "last_fingerprint": runner_module.fingerprint(
                        self.root, paths["middle"]
                    ),
                },
            ],
            "receipt_fingerprints": {
                raw: runner_module.fingerprint(self.root, raw)
                for raw in (paths["terminal"], paths["dependent"])
            },
        }
        terminals = runner_module.empirical_operand_handoff_terminals(
            self.root, registry
        )
        self.assertEqual(terminals[paths["ancestor"]], paths["terminal"])

        dependent_receipt = {
            "receipt_version": 3,
            "producer_run": {"plan": {"path": "output/stage3a/dependent.plan.json"}},
        }
        (self.root / "output/stage3a/dependent.plan.json").write_text(
            "{}\n", encoding="utf-8"
        )
        dependent_contracts = {"main": {
            "effective": {"outputs": {"comparison": {"operands": [{
                "receipt": paths["ancestor"], "result_id": "ancestor.mean",
            }]}}},
        }}
        with (mock.patch.object(
                runner_module, "validate_receipt_contract",
                return_value=dependent_receipt),
              mock.patch.object(runner_module, "compare_snapshot", return_value=[]),
              mock.patch.object(runner_module, "validate_run_plan", return_value={}),
              mock.patch.object(
                  runner_module, "validate_empirical_plan",
                  return_value=(dependent_contracts, []))):
            dependents = runner_module.active_empirical_operand_dependents(
                self.root, registry, [paths["terminal"]]
            )
        self.assertEqual(
            dependents[paths["terminal"]], [paths["dependent"]]
        )

        nested_raw = "output/stage3a/nested_results.receipt.json"
        (self.root / nested_raw).write_text(
            json.dumps({"receipt_version": 2, "supersedes": []}) + "\n",
            encoding="utf-8",
        )
        receipts["ancestor"] = {
            "receipt_version": 3, "supersedes": [],
            "producer_run": {"plan": {"path": "output/stage3a/ancestor.plan.json"}},
        }
        (self.root / paths["ancestor"]).write_text(
            json.dumps(receipts["ancestor"]) + "\n", encoding="utf-8"
        )
        (self.root / "output/stage3a/ancestor.plan.json").write_text(
            json.dumps({"fixture": "ancestor"}) + "\n", encoding="utf-8"
        )
        (self.root / "output/stage3a/dependent.plan.json").write_text(
            json.dumps({"fixture": "dependent"}) + "\n", encoding="utf-8"
        )
        registry["retired"][0]["last_fingerprint"] = runner_module.fingerprint(
            self.root, paths["ancestor"]
        )
        registry["active"].append(nested_raw)
        registry["receipt_fingerprints"][nested_raw] = runner_module.fingerprint(
            self.root, nested_raw
        )
        ancestor_contracts = {"main": {
            "effective": {"outputs": {"nested.comparison": {"operands": [{
                "receipt": nested_raw, "result_id": "nested.mean",
            }]}}},
        }}

        def validated_receipt(_root: Path, path: Path) -> dict:
            return (receipts["ancestor"] if path.name.startswith("ancestor_")
                    else dependent_receipt)

        def validated_contracts(
                _root: Path, plan: dict, **_kwargs: object
                ) -> tuple[dict, list]:
            return ((ancestor_contracts if plan.get("fixture") == "ancestor"
                     else dependent_contracts), [])

        with (mock.patch.object(
                runner_module, "validate_receipt_contract",
                side_effect=validated_receipt),
              mock.patch.object(runner_module, "compare_snapshot", return_value=[]),
              mock.patch.object(
                  runner_module, "validate_run_plan",
                  side_effect=lambda value, _root: value),
              mock.patch.object(
                  runner_module, "validate_empirical_plan",
                  side_effect=validated_contracts)):
            nested_dependents = runner_module.active_empirical_operand_dependents(
                self.root, registry, [nested_raw]
            )
        self.assertEqual(
            nested_dependents[nested_raw], [paths["dependent"]]
        )


if __name__ == "__main__":
    unittest.main()
