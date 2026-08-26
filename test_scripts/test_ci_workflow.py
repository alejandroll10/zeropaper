"""Regression tests for the parallel CI test topology."""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "dev-instruction-sync.yml"

TEST_JOBS = {
    "mirrors",
    "results_pipeline",
    "evidence_assembly",
    "runtime",
    "table_gate",
    "source_policy",
    "ownership",
    "setup_integration",
    "characterization",
}

PRE_SPLIT_INVOCATIONS = {
    "bash test_scripts/test_table_legibility.sh":
        "bash test_scripts/test_table_legibility.sh",
    "bash test_scripts/test_setup_config.sh":
        "bash test_scripts/test_setup_config.sh",
    "bash test_scripts/test_setup_cleanup.sh":
        "bash test_scripts/test_setup_cleanup.sh",
    "bash test_scripts/test_setup_source_policy.sh":
        "bash test_scripts/test_setup_source_policy.sh",
    "bash test_scripts/test_setup_ownership.sh":
        "bash test_scripts/test_setup_ownership.sh",
    "python3 test_scripts/test_results_pipeline.py":
        "python3 test_scripts/test_results_pipeline.py",
    "bash test_scripts/test_results_evidence_assembly.sh":
        "bash test_scripts/test_results_evidence_assembly.sh",
    "python3 test_scripts/test_deepvest.py":
        "python3 test_scripts/test_deepvest.py",
    "python3 deploy_assets/scripts/test_empirical_input_manifest.py":
        "python3 deploy_assets/scripts/test_empirical_input_manifest.py",
    "python -m unittest -v test_scripts.test_llm_client_backends":
        "python -m unittest -v test_scripts.test_llm_client_backends",
    "python3 deploy_assets/scripts/test_assemble_codex_subagents.py":
        "python3 deploy_assets/scripts/test_assemble_codex_subagents.py",
    "bash deploy_assets/scripts/test_codex_driver_watchdog.sh":
        "bash deploy_assets/scripts/test_codex_driver_watchdog.sh",
    "bash deploy_assets/scripts/test_codex_native_live.sh":
        "bash deploy_assets/scripts/test_codex_native_live.sh",
    "python3 deploy_assets/scripts/test_wrds_unix_socket.py":
        "python3 deploy_assets/scripts/test_wrds_unix_socket.py",
    "bash deploy_assets/scripts/test_wrds_auth_latch.sh":
        "bash deploy_assets/scripts/test_wrds_auth_latch.sh",
    "bash deploy_assets/scripts/test_launch_wrds_prestart.sh":
        "bash deploy_assets/scripts/test_launch_wrds_prestart.sh",
    "bash deploy_assets/scripts/test_wrds_turn_survival.sh":
        "bash deploy_assets/scripts/test_wrds_turn_survival.sh",
    "bash deploy_assets/scripts/test_launch_wrds_opencode.sh":
        "bash deploy_assets/scripts/test_launch_wrds_opencode.sh",
    "python3 deploy_assets/scripts/test_ibes_skill.py":
        "python3 deploy_assets/scripts/test_ibes_skill.py",
    "bash test_scripts/test_setup_publish.sh":
        "bash test_scripts/test_setup_publish.sh",
    "bash test_scripts/test_seeded_gate4_assembly.sh":
        "bash test_scripts/test_seeded_gate4_assembly.sh",
    "bash test_scripts/test_stage0_discovery_cap.sh":
        "bash test_scripts/test_stage0_discovery_cap.sh",
    "python test_scripts/test_setup_characterization.py": (
        'python test_scripts/test_setup_characterization.py '
        '--actual "${{ runner.temp }}/setup-characterization/actual.json" '
        '--artifacts-dir "${{ runner.temp }}/setup-characterization/artifacts"'
    ),
    "python -m unittest -v test_scripts.test_sync_dev_instructions":
        "python -m unittest -v test_scripts.test_sync_dev_instructions",
    "bash scripts/sync_dev_instructions.sh":
        "bash scripts/sync_dev_instructions.sh",
}


def load_jobs() -> dict[str, dict[str, Any]]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    return workflow["jobs"]


def job_script(job: dict[str, Any]) -> str:
    return "\n".join(
        str(step.get("run", "")) for step in job.get("steps", [])
    )


class CiWorkflowTest(unittest.TestCase):
    def test_preserves_every_pre_split_invocation_exactly_once(self):
        lines = [
            line.strip()
            for job_id, job in load_jobs().items()
            if job_id != "verify"
            for line in job_script(job).splitlines()
        ]
        for prefix, expected in PRE_SPLIT_INVOCATIONS.items():
            with self.subTest(invocation=expected):
                matching = [line for line in lines if line.startswith(prefix)]
                self.assertEqual(matching, [expected])

    def test_mirror_diff_gate_is_exact(self):
        scripts = [
            step.get("run", "")
            for step in load_jobs()["mirrors"]["steps"]
        ]
        gates = [script for script in scripts if "git diff --cached" in script]
        self.assertEqual(len(gates), 1)
        self.assertIn(
            "if ! git diff --cached --exit-code HEAD -- "
            "AGENTS.md .agents/skills; then\n",
            gates[0],
        )
        self.assertNotIn("|| true", gates[0])

    def test_expensive_suites_run_in_independent_jobs(self):
        jobs = load_jobs()
        owners = {}
        for command in (
            "test_results_pipeline.py",
            "test_results_evidence_assembly.sh",
            "test_setup_source_policy.sh",
            "test_setup_ownership.sh",
            "test_setup_publish.sh",
            "test_setup_characterization.py",
        ):
            matching = [
                job_id for job_id, job in jobs.items()
                if command in job_script(job)
            ]
            self.assertEqual(len(matching), 1, command)
            owners[command] = matching[0]
        self.assertEqual(len(set(owners.values())), len(owners), owners)

    def test_aggregate_gate_requires_every_parallel_job(self):
        jobs = load_jobs()
        self.assertEqual(set(jobs) - {"verify"}, TEST_JOBS)
        self.assertEqual(set(jobs["verify"]["needs"]), TEST_JOBS)
        self.assertEqual(jobs["verify"]["name"], "Verify generated mirrors")
        self.assertIn("always()", str(jobs["verify"]["if"]))
        for job_id in TEST_JOBS:
            self.assertNotIn("needs", jobs[job_id], job_id)

    def test_aggregate_script_accepts_only_all_success(self):
        jobs = load_jobs()
        script = jobs["verify"]["steps"][0]["run"]
        results = {
            job_id: {"result": "success", "outputs": {}}
            for job_id in TEST_JOBS
        }

        environment = os.environ | {"TEST_JOB_RESULTS": json.dumps(results)}
        completed = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

        for result in ("failure", "cancelled", "skipped"):
            with self.subTest(result=result):
                rejected = {
                    job_id: value.copy() for job_id, value in results.items()
                }
                rejected["ownership"]["result"] = result
                environment["TEST_JOB_RESULTS"] = json.dumps(rejected)
                completed = subprocess.run(
                    ["bash", "-c", script],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=environment,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(f"ownership: {result}", completed.stdout)


if __name__ == "__main__":
    unittest.main()
