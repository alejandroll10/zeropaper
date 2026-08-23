#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import hashlib
import importlib.util
import json
import os
import re
import resource
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import venv
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
UTILITY = REPO / "deploy_assets/templates/utils/results_pipeline/results_pipeline.py"


class ResultsPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "code").mkdir()
        (self.root / "process_log").mkdir()
        (self.root / "data").mkdir()
        (self.root / "output/stagex/tables").mkdir(parents=True)
        (self.root / "data/input.txt").write_text("input-v1\n", encoding="utf-8")
        (self.root / "process_log/results_registry.json").write_text(
            json.dumps({"kind": "result_registry", "registry_version": 1,
                        "active": [], "pending": [], "retired": [],
                        "receipt_fingerprints": {}}) + "\n", encoding="utf-8"
        )
        self.analyze_source = """import json, os, pathlib
root = pathlib.Path.cwd()
artifact = root / 'output/stagex/detail.json'
artifact.write_text(json.dumps({'rows': [1, 2, 3]}) + '\\n')
bundle = {
  'schema_version': 1,
  'producer': {'name': 'test', 'code': ['code/analyze.py'],
               'inputs': ['data/input.txt'], 'reproducibility': 'captured'},
  'results': {'main.mean': {'description': 'Main mean', 'value': '2.0'},
              'main.rows': {'description': 'Underlying rows',
                            'artifact': 'output/stagex/detail.json', 'selector': 'rows'}},
  'artifacts': [{'path': 'output/stagex/detail.json', 'description': 'Detailed rows',
                 'media_type': 'application/json'}],
  'renderer': {'code': ['code/render.py']},
  'exhibits': [{'id': 'main.table', 'kind': 'table',
                'path': 'output/stagex/tables/main.tex',
                'description': 'Main table', 'result_ids': ['main.mean', 'main.rows']}]
}
(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle, indent=2) + '\\n')
"""
        (self.root / "code/analyze.py").write_text(self.analyze_source, encoding="utf-8")
        (self.root / "code/render.py").write_text(
            """import json, os, pathlib, shutil, sys
root = pathlib.Path.cwd()
trigger_root = root / 'output/test-render-triggers'
if (trigger_root / 'noop').exists():
    sys.exit(0)
if (trigger_root / 'corrupt-fail').exists():
    for live_target, replacement_text in [
        (root / 'data/input.txt', 'bad input\\n'),
        (root / 'output/stagex/tables/main.tex', 'bad exhibit\\n'),
        (root / 'process_log/results_registry.json', '{}\\n'),
        (root / 'output/stagex/results.receipt.json', '{}\\n'),
    ]:
        replacement = live_target.with_suffix(live_target.suffix + '.replacement')
        replacement.write_text(replacement_text)
        os.replace(replacement, live_target)
    shutil.rmtree(root / 'process_log/.results_pipeline-transaction-backup')
    sys.exit(7)
bundle = json.loads((root / os.environ['RESULTS_BUNDLE_PATH']).read_text())
value = bundle['results']['main.mean']['value']
target = pathlib.Path(os.environ['RESULTS_EXHIBIT_ROOT']) / 'output/stagex/tables/main.tex'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text('\\\\begin{tabular}{c}\\n' + value + '\\n\\\\end{tabular}\\n')
if (trigger_root / 'mutate-input').exists():
    replacement = root / 'data/input.replacement'
    replacement.write_text('mutated\\n')
    os.replace(replacement, root / 'data/input.txt')
if (trigger_root / 'mutate-during-bind').exists():
    with (root / 'output/evidence/audit.md').open('a') as report:
        report.write('\\n## Verdict\\nREVISE\\n')
""",
            encoding="utf-8",
        )
        self.write_plan("output/stagex/results.plan.json")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def call(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        if args and args[0] == "run" and "--plan" not in args:
            args = (args[0], "--plan", "output/stagex/results.plan.json", *args[1:])
        completed = subprocess.run(
            [sys.executable, str(UTILITY), *args], cwd=self.root,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, expected, completed.stdout + completed.stderr)
        return completed

    def write_plan(self, path: str, *, prefix: str = "output/stagex/",
                   analyze: str = "code/analyze.py", render: str = "code/render.py") -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "plan_version": 1,
            "producer_code": [analyze],
            "producer_inputs": ["data/input.txt"],
            "artifacts": [prefix + "detail.json"],
            "renderer_code": [render],
            "exhibits": [prefix + "tables/main.tex"],
        }) + "\n", encoding="utf-8")

    def record_and_render(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )
        self.call("activate", "--receipt", "output/stagex/results.receipt.json")

    def interrupt_pending_render_publication(self, *, update_registry: bool) -> None:
        receipt_raw = "output/stagex/results.receipt.json"
        code = (
            "import importlib.util, json, os, pathlib\n"
            f"utility = pathlib.Path({str(UTILITY)!r})\n"
            "spec = importlib.util.spec_from_file_location('rp', utility)\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "root = pathlib.Path.cwd()\n"
            "registry, _ = module.load_registry(root)\n"
            f"receipt_raw = {receipt_raw!r}\n"
            "module.prepare_lifecycle_transaction(root, cleanup_paths=[], "
            "restore_paths=[receipt_raw], registry_before=registry)\n"
            "receipt = module.load_json(root / receipt_raw)\n"
            "receipt['render_run'] = {'interrupted': True}\n"
            "module.atomic_json(root / receipt_raw, receipt)\n"
            + (
                "registry['receipt_fingerprints'][receipt_raw] = "
                "module.fingerprint(root, receipt_raw)\n"
                "module.atomic_json(root / module.REGISTRY_PATH, registry)\n"
                if update_registry else ""
            ) +
            "os._exit(9)\n"
        )
        crashed = subprocess.run([sys.executable, "-B", "-c", code], cwd=self.root)
        self.assertEqual(crashed.returncode, 9)

    def assert_results_lock_available(self) -> None:
        lock = self.root / "process_log/results_pipeline.lock"
        descriptor = os.open(lock, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)

    def add_paper_audit(self, *, citation: bool = False, asset: bool = False,
                        listing: bool = False, local_style: bool = False,
                        addplot: bool = False, plural_citation: bool = False,
                        advanced_citations: bool = False,
                        starred_graphic: bool = False,
                        natbib_citations: bool = False,
                        expanded_citations: bool = False,
                        braceless_input: bool = False,
                        conditional_bib: bool = False) -> None:
        (self.root / "paper/sections").mkdir(parents=True, exist_ok=True)
        main_text = ("\\input sections/results\n" if braceless_input else
                     "\\input{sections/results}\n")
        if conditional_bib:
            main_text += "\\IfFileExists{bib.bib}{\\bibliography{bib}}{}\n"
        if listing:
            main_text += "\\lstinputlisting{../data/latex_rows.csv}\n"
        if local_style:
            main_text = "\\usepackage{localaudit}\n" + main_text
        (self.root / "paper/main.tex").write_text(main_text, encoding="utf-8")
        has_results = (self.root / "output/stagex/results.receipt.json").exists()
        results_text = "Table 1 reports the main result.\n"
        if has_results:
            results_text += "\\input{../output/stagex/tables/main}\n"
        if citation:
            results_text += "Prior work reports a related result \\cite{prior}.\n"
        if plural_citation:
            results_text += "Two literatures motivate the design \\autocites{one}{two}.\n"
        if advanced_citations:
            results_text += (
                "Contrasting sources \\cites[see][1]{one}[contra][2]{two}.\n\n"
                "A full source \\fullcite{three}.\n\n"
                "Volume evidence \\volcite[see]{4}[p. 2]{four}.\n"
            )
        if natbib_citations:
            results_text += "Textual \\citet{five}; parenthetical \\citep[see][p. 3]{six}.\n"
        if expanded_citations:
            results_text += (
                "Titles \\citetitle{seven}; fields \\citefield{eight}{title}; "
                "URLs \\citeurl{nine}; numbers \\citenum{ten}.\n"
            )
        if asset:
            results_text += "\\includegraphics{assets/chart.png}\n"
        if starred_graphic:
            results_text += "\\includegraphics*{assets/chart.png}\n"
        if addplot:
            results_text += "\\addplot+ table {../../data/plot.csv};\n"
        (self.root / "paper/sections/results.tex").write_text(results_text, encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        prepared = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "stage5-initial",
        )
        digest = json.loads(prepared.stdout)["digest"]
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        (self.root / "output/evidence/audit.md").write_text(
            f"VERDICT: PASS\nCHECKPOINT: stage5-initial\nAUDIT_INPUT_DIGEST: {digest}\n\n# PASS\n",
            encoding="utf-8"
        )
        (self.root / "output/evidence/audit.json").write_text(
            json.dumps({"verdict": "PASS", "checkpoint": "stage5-initial",
                        "blocking_findings": [],
                        "audit_input_path": "output/evidence/audit_input.json",
                        "audit_input_digest": digest,
                        "mechanical_command": (
                            "python3 code/utils/results_pipeline/results_pipeline.py "
                            "verify-all --rerender"
                        ),
                        "result_receipts_checked": (
                            ["output/stagex/results.receipt.json"] if has_results else []
                        ),
                        "result_bearing_exhibits_checked": (
                            ["output/stagex/tables/main.tex"] if has_results else []
                        ),
                        "expository_exemptions": [], "exceptional_direct_results": []}) + "\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence/citations.md").write_text(
            f"VERDICT: PASS\nCHECKPOINT: stage5-initial\nAUDIT_INPUT_DIGEST: {digest}\n\n# PASS\n",
            encoding="utf-8"
        )
        citation_claims = []
        for occurrence in audit_input["citation_occurrences"]:
            citation_claims.append({
                "occurrence_id": occurrence["occurrence_id"],
                "anchor": occurrence["occurrence_id"],
                "claim_text": occurrence["claim_text"],
                "cite_keys": occurrence["cite_keys"],
                "status": "FAITHFUL",
                "verification": "fresh",
                "sources": [{"cite_key": key,
                             "pointer": "https://doi.org/10.0000/example"}
                            for key in occurrence["cite_keys"]],
            })
        (self.root / "output/evidence/citations.json").write_text(
            json.dumps({"verdict": "PASS", "checkpoint": "stage5-initial",
                        "blocking_findings": [], "citation_claims": citation_claims,
                        "audit_input_path": "output/evidence/audit_input.json",
                        "audit_input_digest": digest,
                        "fresh_checks": len(citation_claims), "reused_bound_checks": 0}) + "\n",
            encoding="utf-8",
        )

    def bind_paper(self, *, expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input.json",
            "--summary", "output/evidence/audit.json",
            "--report", "output/evidence/audit.md",
            "--citation-summary", "output/evidence/citations.json",
            "--citation-report", "output/evidence/citations.md",
            "--receipt", "process_log/paper_evidence.receipt.json",
            "--checkpoint", "stage5-initial", expected=expected,
        )

    def test_round_trip_and_rerender(self) -> None:
        self.record_and_render()
        receipt = json.loads(
            (self.root / "output/stagex/results.receipt.json").read_text(encoding="utf-8")
        )
        self.assertEqual(receipt["receipt_version"], 2)
        for run_key in ("producer_run", "render_run"):
            capture = receipt[run_key]["environment"]
            self.assertEqual(capture["capture_version"], 1)
            encoded = json.dumps(
                capture["manifest"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            self.assertEqual(
                capture["sha256"],
                "sha256:" + hashlib.sha256(encoded).hexdigest(),
            )
            self.assertIn("launcher", capture["manifest"])
            self.assertIn("platform", capture["manifest"])
        report = self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json", "--rerender"
        )
        self.assertEqual(json.loads(report.stdout)["status"], "PASS")
        all_report = self.call("verify-all", "--require-one", "--rerender")
        self.assertEqual(json.loads(all_report.stdout)["status"], "PASS")

    def test_environment_capture_records_installed_metadata_and_detects_change(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        venv_root = self.root / ".venv"
        site_packages = venv_root / "lib/python3.12/site-packages"
        dist_info = site_packages / "example_pkg-1.2.3.dist-info"
        dist_info.mkdir(parents=True)
        (venv_root / "pyvenv.cfg").write_text(
            f"home = {Path(sys.executable).parent}\nversion = 3.12\n",
            encoding="utf-8",
        )
        (dist_info / "METADATA").write_text(
            "Metadata-Version: 2.1\nName: example-pkg\nVersion: 1.2.3\n\n",
            encoding="utf-8",
        )
        (dist_info / "RECORD").write_text("example_pkg/__init__.py,,\n", encoding="utf-8")
        (site_packages / "editable.pth").write_text("/tmp/example-source\n", encoding="utf-8")
        (venv_root / "lib64").symlink_to("lib", target_is_directory=True)
        (self.root / "uv.lock").write_text("version = 1\n", encoding="utf-8")

        before = module.capture_execution_environment(
            self.root, [sys.executable, "code/analyze.py"]
        )
        project_environment = before["manifest"]["project_environment"]
        distributions = project_environment["python_venv"]["distributions"]
        self.assertEqual(
            [(item["name"], item["version"]) for item in distributions],
            [("example-pkg", "1.2.3")],
        )
        self.assertEqual(
            [item["path"] for item in project_environment["dependency_manifests"]],
            ["uv.lock"],
        )
        (dist_info / "METADATA").write_text(
            "Metadata-Version: 2.1\nName: example-pkg\nVersion: 1.2.4\n\n",
            encoding="utf-8",
        )
        after = module.capture_execution_environment(
            self.root, [sys.executable, "code/analyze.py"]
        )
        self.assertNotEqual(before, after)
        with self.assertRaisesRegex(module.EvidenceError, "changed during analysis"):
            module.require_stable_environment(before, after, "analysis")

    def test_environment_capture_does_not_follow_hostile_metadata(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_hostile", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        venv_root = self.root / ".venv"
        dist_info = venv_root / "lib/python3.12/site-packages/hostile-1.dist-info"
        dist_info.mkdir(parents=True)
        (venv_root / "pyvenv.cfg").write_text("version = 3.12\n", encoding="utf-8")
        outside = self.root / "outside-metadata"
        outside.write_text(
            "Name: must-not-leak\nVersion: secret-version-marker\n\n",
            encoding="utf-8",
        )
        (dist_info / "METADATA").symlink_to(outside)
        os.mkfifo(dist_info / "entry_points.txt")

        with self.assertRaisesRegex(
            module.EvidenceError, "resolves outside its environment"
        ) as symlink_failure:
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )
        self.assertNotIn("must-not-leak", str(symlink_failure.exception))
        self.assertNotIn("secret-version-marker", str(symlink_failure.exception))

        (dist_info / "METADATA").unlink()
        (dist_info / "METADATA").write_text(
            "Name: hostile\nVersion: 1\n\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(module.EvidenceError, "runtime file is not regular"):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_rejects_venv_library_outside_venv(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_escape", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        venv_root = self.root / ".venv"
        venv_root.mkdir()
        external_library = self.root / "external-library"
        external_library.mkdir()
        (venv_root / "lib").symlink_to(external_library, target_is_directory=True)

        with self.assertRaisesRegex(
            module.EvidenceError, "venv library resolves outside its environment"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_bounds_manifest_hashing(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_limit", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        manifest = self.root / "uv.lock"
        with manifest.open("wb") as handle:
            handle.seek(module.MAX_ENVIRONMENT_CAPTURE_FILE_BYTES)
            handle.write(b"x")

        with self.assertRaisesRegex(
            module.EvidenceError, "exceeds the environment capture per-file limit"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_uses_effective_venv_launcher(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_launcher", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        bin_dir = self.root / ".venv/bin"
        bin_dir.mkdir(parents=True)
        launcher = bin_dir / "bash"
        launcher.write_text("#!/bin/sh\nexec /bin/bash \"$@\"\n", encoding="utf-8")
        launcher.chmod(0o755)
        python_launcher = bin_dir / "python3"
        python_launcher.write_text("#!/bin/sh\nexec /usr/bin/python3 \"$@\"\n", encoding="utf-8")
        python_launcher.chmod(0o755)
        environment = os.environ.copy()

        capture = module.capture_execution_environment(
            self.root, ["bash", "-c", "true"]
        )
        recorded = capture["manifest"]["launcher"]["executable"]
        self.assertEqual(recorded["resolved_path"], str(launcher.resolve()))
        self.assertEqual(recorded["sha256"], "sha256:" + hashlib.sha256(
            launcher.read_bytes()
        ).hexdigest())
        rewritten, clean, _, _ = module.isolated_runtime(
            ["bash", "-c", "true"], self.root, self.root, environment
        )
        self.assertEqual(rewritten[0], "/results-runtime-venv/bin/bash")
        self.assertEqual(clean["PATH"].split(os.pathsep)[0], "/results-runtime-venv/bin")

        for requested in ("python", "python3", "python.exe", "python3.exe"):
            command = ["uv", "run", requested, "code/analyze.py"]
            uv_capture = module.capture_execution_environment(self.root, command)
            uv_recorded = uv_capture["manifest"]["launcher"]["executable"]
            self.assertEqual(uv_recorded["resolved_path"], str(python_launcher.resolve()))
            uv_rewritten, _, _, _ = module.isolated_runtime(
                command, self.root, self.root, environment
            )
            self.assertEqual(uv_rewritten[0], "/results-runtime-venv/bin/python3")

        python_launcher.write_text(
            f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8"
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            "python3", "code/analyze.py",
        )
        self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            "python3", "code/render.py",
        )
        receipt = json.loads(
            (self.root / "output/stagex/results.receipt.json").read_text(encoding="utf-8")
        )
        expected_hash = "sha256:" + hashlib.sha256(python_launcher.read_bytes()).hexdigest()
        self.assertEqual(
            receipt["producer_run"]["environment"]["manifest"]["launcher"]
            ["executable"]["sha256"],
            expected_hash,
        )
        self.assertEqual(
            receipt["render_run"]["environment"]["manifest"]["launcher"]
            ["executable"]["sha256"],
            expected_hash,
        )

    def test_environment_capture_rejects_dependency_manifest_aliases(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_alias", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        secret = self.root / ".env"
        secret.write_text("SECRET_MARKER=must-not-hash\n", encoding="utf-8")
        manifest = self.root / "uv.lock"
        manifest.symlink_to(".env")

        with self.assertRaisesRegex(
            module.EvidenceError, "dependency manifest must be one non-aliased regular file"
        ) as symlink_failure:
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )
        self.assertNotIn("must-not-hash", str(symlink_failure.exception))

        manifest.unlink()
        os.link(secret, manifest)
        with self.assertRaisesRegex(
            module.EvidenceError, "dependency manifest must be one non-aliased regular file"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_has_aggregate_byte_budget(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_budget", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        size = module.MAX_ENVIRONMENT_CAPTURE_TOTAL_BYTES // 2 + 1
        for name in ("uv.lock", "requirements.txt"):
            with (self.root / name).open("wb") as handle:
                handle.seek(size - 1)
                handle.write(b"x")

        with self.assertRaisesRegex(
            module.EvidenceError, "environment capture aggregate byte limit exceeded"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_rejects_credential_aliases(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_secret", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        secret_value = "provider-secret-marker-123456789"
        with mock.patch.dict(
            os.environ,
            {"OPENAI_API_KEY": secret_value, "OMP_NUM_THREADS": secret_value},
            clear=False,
        ):
            with self.assertRaisesRegex(
                module.EvidenceError,
                "captured runtime environment contains a literal provider credential",
            ) as environment_failure:
                module.capture_execution_environment(
                    self.root, [sys.executable, "code/analyze.py"]
                )
        self.assertNotIn(secret_value, str(environment_failure.exception))

        venv_root = self.root / ".venv"
        dist_info = venv_root / "lib/python3.12/site-packages/alias-1.dist-info"
        dist_info.mkdir(parents=True)
        secret_file = self.root / ".env"
        secret_file.write_text(
            "Name: must-not-leak\nVersion: secret-version-marker\n\n",
            encoding="utf-8",
        )
        os.link(secret_file, dist_info / "METADATA")
        with self.assertRaisesRegex(
            module.EvidenceError, "credential-bearing file may not enter environment capture"
        ) as metadata_failure:
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )
        self.assertNotIn("must-not-leak", str(metadata_failure.exception))
        self.assertNotIn("secret-version-marker", str(metadata_failure.exception))

        (dist_info / "METADATA").unlink()
        launcher = venv_root / "bin/secret-launcher"
        launcher.parent.mkdir()
        os.link(secret_file, launcher)
        launcher.chmod(0o755)
        with self.assertRaisesRegex(
            module.EvidenceError, "credential-bearing file may not enter environment capture"
        ):
            module.capture_execution_environment(
                self.root, ["secret-launcher", "code/analyze.py"]
            )

    def test_environment_capture_does_not_read_growth_beyond_budget(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_growth", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        target = self.root / "growing-runtime"
        target.write_bytes(b"x")
        descriptor = os.open(target, os.O_RDONLY)
        original_read = module.os.read
        read_bytes = 0
        grown = False

        def grow_then_read(fd: int, size: int) -> bytes:
            nonlocal read_bytes, grown
            if not grown:
                grown = True
                with target.open("ab") as handle:
                    handle.write(b"y" * 1024 * 1024)
            payload = original_read(fd, size)
            read_bytes += len(payload)
            return payload

        with mock.patch.object(module.os, "read", side_effect=grow_then_read):
            with self.assertRaisesRegex(module.EvidenceError, "changed while captured"):
                module._runtime_descriptor_identity(
                    descriptor, "growing-runtime", "growing-runtime",
                    module._EnvironmentCaptureBudget(),
                )
        self.assertEqual(read_bytes, 1)

    def test_environment_capture_validates_nested_manifest(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_validate", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        venv_root = self.root / ".venv"
        dist_info = venv_root / "lib/python3.12/site-packages/example-1.dist-info"
        dist_info.mkdir(parents=True)
        (venv_root / "pyvenv.cfg").write_text("version = 3.12\n", encoding="utf-8")
        (dist_info / "METADATA").write_text(
            "Name: example\nVersion: 1\n\n", encoding="utf-8"
        )
        command = [sys.executable, "code/analyze.py"]
        capture = module.capture_execution_environment(
            self.root, command
        )
        module.validate_environment_capture(capture, "capture", command)

        mutations = (
            lambda manifest: manifest.__setitem__("launcher", None),
            lambda manifest: manifest.__setitem__("platform", []),
            lambda manifest: manifest.__setitem__("runtime_environment", "not-an-object"),
            lambda manifest: manifest.__setitem__("project_environment", 17),
            lambda manifest: manifest["launcher"]["executable"].__setitem__("size", True),
            lambda manifest: manifest["launcher"]["executable"].__setitem__(
                "sha256", "sha256:" + "z" * 64
            ),
            lambda manifest: manifest["project_environment"]["python_venv"]
            ["configuration"].update({"path": ".env", "resolved_path": ".env"}),
            lambda manifest: manifest["project_environment"]["python_venv"]
            ["distributions"][0]["metadata_files"]["METADATA"].update(
                {"path": ".env", "resolved_path": ".env"}
            ),
            lambda manifest: manifest["launcher"].__setitem__("requested", "other"),
        )
        for mutate in mutations:
            hostile = json.loads(json.dumps(capture))
            mutate(hostile["manifest"])
            encoded = json.dumps(
                hostile["manifest"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            hostile["sha256"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
            with self.subTest(mutation=mutate):
                with self.assertRaises(module.EvidenceError):
                    module.validate_environment_capture(hostile, "capture", command)

    def test_environment_capture_has_shared_directory_entry_budget(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_entries", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        budget = module._EnvironmentCaptureBudget()
        budget.entries = module.MAX_ENVIRONMENT_CAPTURE_ENTRIES
        with self.assertRaisesRegex(
            module.EvidenceError, "environment capture directory-entry limit exceeded"
        ):
            budget.observe_entry("site-packages")

    def test_environment_capture_rejects_nonregular_env_roots(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_env_shape", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        store = self.root / "credential-store"
        store.write_text(
            "Name: leaked-name\nVersion: leaked-secret\n\n", encoding="utf-8"
        )
        (self.root / ".env").symlink_to(store.name)
        with self.assertRaisesRegex(
            module.EvidenceError, "credential-bearing project path must be a regular file"
        ) as symlink_failure:
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )
        self.assertNotIn("leaked-name", str(symlink_failure.exception))
        self.assertNotIn("leaked-secret", str(symlink_failure.exception))

        (self.root / ".env").unlink()
        (self.root / ".env.d").mkdir()
        with self.assertRaisesRegex(
            module.EvidenceError, "credential-bearing project path must be a regular file"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_accepts_custom_venv_launcher_shape(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_custom", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        launcher = self.root / ".venv/custom/python3"
        launcher.parent.mkdir(parents=True)
        launcher.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        launcher.chmod(0o755)
        command = [".venv/custom/python3", "code/analyze.py"]
        capture = module.capture_execution_environment(self.root, command)
        module.validate_environment_capture(capture, "capture", command)
        self.assertEqual(
            capture["manifest"]["launcher"]["executable"]["path"],
            ".venv/custom/python3",
        )

        hostile = json.loads(json.dumps(capture))
        hostile["manifest"]["project_environment"]["python_venv"] = None
        encoded = json.dumps(
            hostile["manifest"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        hostile["sha256"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
        with self.assertRaisesRegex(module.EvidenceError, "venv launcher has no venv capture"):
            module.validate_environment_capture(hostile, "capture", command)

    def test_environment_capture_rejects_file_form_dist_info(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_dist_file", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        dist_info = self.root / ".venv/lib/python3.12/site-packages/example.dist-info"
        dist_info.parent.mkdir(parents=True)
        dist_info.write_text("Name: example\nVersion: 1\n\n", encoding="utf-8")
        with self.assertRaisesRegex(
            module.EvidenceError, "venv dist-info entry must be a directory"
        ):
            module.capture_execution_environment(
                self.root, [sys.executable, "code/analyze.py"]
            )

    def test_environment_capture_rejects_surrogate_text_controllably(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_capture_surrogate", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        command = [sys.executable, "code/analyze.py"]
        capture = module.capture_execution_environment(self.root, command)
        hostile = json.loads(json.dumps(capture))
        hostile["manifest"]["runtime_environment"]["LANG"] = "\ud800"
        encoded = json.dumps(
            hostile["manifest"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        hostile["sha256"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
        with self.assertRaisesRegex(module.EvidenceError, "not valid UTF-8"):
            module.validate_environment_capture(hostile, "capture", command)

        environment = os.environ.copy()
        environment["LANG"] = "\ud800"
        with mock.patch.object(module.os, "environ", environment):
            with self.assertRaisesRegex(module.EvidenceError, "not valid UTF-8"):
                module.capture_execution_environment(self.root, command)

    def test_results_lock_does_not_conflict_with_launcher_shared_root_lock(self) -> None:
        descriptor = os.open(self.root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            fcntl.flock(descriptor, fcntl.LOCK_SH)
            completed = subprocess.run(
                [sys.executable, str(UTILITY), "verify-all"], cwd=self.root,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2,
            )
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_sandbox_kills_computation_child_with_utility_parent(self) -> None:
        marker = self.root / "output/child-started"
        script = self.root / "code/analyze.py"
        script.write_text(
            "import pathlib, time\n"
            "pathlib.Path('output/child-started').write_text('started\\n')\n"
            "time.sleep(0.8)\n" + self.analyze_source,
            encoding="utf-8",
        )
        process = subprocess.Popen(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        time.sleep(0.15)
        process.kill()
        process.wait(timeout=2)
        process.communicate(timeout=2)
        self.call("verify-all")
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / "output/stagex/results.json").exists())
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())
        self.assertFalse((self.root / "output/stagex/detail.json").exists())

    def test_parent_kill_cleans_workspace_containing_selected_credential(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os, pathlib, time\n"
            "parent = pathlib.Path('locked-parent')\n"
            "secret_dir = parent / 'locked-secret'\n"
            "secret_dir.mkdir(parents=True)\n"
            "(secret_dir / 'credential.txt').write_text(os.environ['OPENAI_API_KEY'])\n"
            "parent.chmod(0)\n"
            "pathlib.Path('producer-ready').write_text('ready')\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        environment = os.environ.copy()
        environment["OPENAI_API_KEY"] = "round15-temp-secret-264"
        process = subprocess.Popen(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        workspace: Path | None = None
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            candidates = set(temp_root.glob("results-workspace-*")) - before
            matches = [path for path in candidates if (path / "producer-ready").exists()]
            if matches:
                workspace = matches[0]
                break
            time.sleep(0.02)
        self.assertIsNotNone(workspace, "producer never wrote the crash credential fixture")
        process.kill()
        process.wait(timeout=2)
        process.communicate(timeout=2)
        deadline = time.monotonic() + 5
        while workspace is not None and workspace.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertIsNotNone(workspace)
        self.assertFalse(workspace.exists(), "supervisor left an abandoned credential workspace")
        self.assert_results_lock_available()

    def test_mode_zero_nested_workspace_is_removed_after_normal_completion(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            "import pathlib\n"
            "parent = pathlib.Path('locked-parent')\n"
            "secret_dir = parent / 'nested'\n"
            "secret_dir.mkdir(parents=True)\n"
            "(secret_dir / 'payload.txt').write_text('payload')\n"
            "parent.chmod(0)\n" + self.analyze_source,
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertEqual(set(temp_root.glob("results-workspace-*")), before)
        self.assert_results_lock_available()

    def test_mode_zero_workspace_root_is_removed_after_normal_exit(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source +
            "pathlib.Path('.').chmod(0)\n",
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=5,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(set(temp_root.glob("results-workspace-*")), before)
        self.assert_results_lock_available()

    def test_parent_kill_removes_mode_zero_workspace_root(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os, pathlib, time\n"
            "pathlib.Path('credential.txt').write_text(os.environ['OPENAI_API_KEY'])\n"
            "pathlib.Path('.').chmod(0)\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        environment = os.environ.copy()
        environment["OPENAI_API_KEY"] = "round17-root-secret-264"
        process = subprocess.Popen(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        workspace: Path | None = None
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            for candidate in set(temp_root.glob("results-workspace-*")) - before:
                if stat.S_IMODE(candidate.lstat().st_mode) == 0:
                    workspace = candidate
                    break
            if workspace is not None:
                break
            time.sleep(0.02)
        self.assertIsNotNone(workspace, "producer never locked the workspace root")
        process.kill()
        process.wait(timeout=2)
        deadline = time.monotonic() + 5
        while workspace is not None and workspace.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        process.communicate(timeout=2)
        self.assertIsNotNone(workspace)
        self.assertFalse(workspace.exists(), "mode-zero workspace root survived cleanup")
        self.assert_results_lock_available()

    def test_deep_workspace_tree_is_removed_after_normal_completion(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os, pathlib\n"
            "pathlib.Path('deep').mkdir()\n"
            "fd = os.open('deep', os.O_RDONLY | os.O_DIRECTORY)\n"
            "for _ in range(1200):\n"
            "    os.mkdir('d', dir_fd=fd)\n"
            "    next_fd = os.open('d', os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)\n"
            "    os.close(fd)\n"
            "    fd = next_fd\n"
            "os.close(fd)\n" + self.analyze_source,
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertEqual(set(temp_root.glob("results-workspace-*")), before)

    def test_parent_kill_removes_deep_workspace_credential(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os, pathlib, time\n"
            "pathlib.Path('deep').mkdir()\n"
            "fd = os.open('deep', os.O_RDONLY | os.O_DIRECTORY)\n"
            "for _ in range(1200):\n"
            "    os.mkdir('d', dir_fd=fd)\n"
            "    next_fd = os.open('d', os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)\n"
            "    os.close(fd)\n"
            "    fd = next_fd\n"
            "secret_fd = os.open('credential.txt', os.O_WRONLY | os.O_CREAT, 0o600, dir_fd=fd)\n"
            "os.write(secret_fd, os.environ['OPENAI_API_KEY'].encode())\n"
            "os.close(secret_fd)\n"
            "os.close(fd)\n"
            "pathlib.Path('producer-ready').write_text('ready')\n"
            "time.sleep(30)\n",
            encoding="utf-8",
        )
        temp_root = Path(tempfile.gettempdir())
        before = set(temp_root.glob("results-workspace-*"))
        environment = os.environ.copy()
        environment["OPENAI_API_KEY"] = "round16-deep-secret-264"
        process = subprocess.Popen(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        workspace: Path | None = None
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            candidates = set(temp_root.glob("results-workspace-*")) - before
            matches = [path for path in candidates if (path / "producer-ready").exists()]
            if matches:
                workspace = matches[0]
                break
            time.sleep(0.02)
        self.assertIsNotNone(workspace, "deep-tree producer fixture did not finish")
        process.kill()
        process.wait(timeout=2)
        process.communicate(timeout=2)
        deadline = time.monotonic() + 10
        while workspace is not None and workspace.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertIsNotNone(workspace)
        self.assertFalse(workspace.exists(), "deep credential workspace survived cleanup")

    def test_workspace_guard_stays_armed_through_parent_cleanup(self) -> None:
        marker = self.root / "output/workspace-guard-path.txt"
        code = (
            "import importlib.util, os, pathlib, time\n"
            f"utility = pathlib.Path({str(UTILITY)!r})\n"
            "spec = importlib.util.spec_from_file_location('rp', utility)\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "root = pathlib.Path.cwd()\n"
            "parent_pid = os.getpid()\n"
            "original_cleanup = module.remove_abandoned_workspace\n"
            "def paused_cleanup(workspace):\n"
            "    if os.getpid() == parent_pid:\n"
            "        (root / 'output/workspace-guard-path.txt').write_text(str(workspace))\n"
            "        time.sleep(30)\n"
            "    original_cleanup(workspace)\n"
            "module.remove_abandoned_workspace = paused_cleanup\n"
            "with module.isolated_workspace(root, ['data/input.txt'], []) as workspace:\n"
            "    (workspace / 'crash-secret.txt').write_text('secret')\n"
        )
        process = subprocess.Popen([sys.executable, "-B", "-c", code], cwd=self.root)
        deadline = time.monotonic() + 5
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(marker.exists(), "workspace guardian fixture did not start")
        workspace = Path(marker.read_text(encoding="utf-8"))
        self.assertTrue((workspace / "crash-secret.txt").exists())
        process.kill()
        process.wait(timeout=2)
        deadline = time.monotonic() + 5
        while workspace.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertFalse(workspace.exists(), "guardian did not clean after parent death")

    @unittest.skipUnless(
        sys.platform.startswith("linux") and shutil.which("bwrap"),
        "Linux bubblewrap PID-namespace check",
    )
    def test_normal_producer_exit_cannot_orphan_background_descendant(self) -> None:
        marker = f"results-pid1-background-{os.getpid()}-{self.root.name}"
        script = self.root / "code/analyze.py"
        script.write_text(
            "import subprocess\n"
            f"subprocess.Popen(['bash', '-c', 'exec -a {marker} sleep 30'], "
            "start_new_session=True)\n" + self.analyze_source,
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        found = subprocess.run(
            ["pgrep", "-f", marker], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if found.returncode == 0:
            for raw in found.stdout.split():
                try:
                    os.kill(int(raw), 9)
                except ProcessLookupError:
                    pass
        self.assertEqual(found.returncode, 1, found.stdout + found.stderr)

    def test_producer_cannot_write_hardcoded_live_project_path(self) -> None:
        (self.root / "paper").mkdir()
        paper = self.root / "paper/main.tex"
        paper.write_text("paper-v1\n", encoding="utf-8")
        registry = self.root / "process_log/results_registry.json"
        before_registry = registry.read_bytes()
        script = self.root / "code/analyze.py"
        script.write_text(
            "import pathlib\n"
            f"for target in [pathlib.Path({str(paper)!r}), "
            f"pathlib.Path({str(registry)!r})]:\n"
            "    try:\n"
            "        target.write_text('corrupt\\n')\n"
            "    except OSError:\n"
            "        pass\n"
            "    else:\n"
            "        raise RuntimeError(f'live project was writable: {target}')\n" +
            self.analyze_source,
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertEqual(paper.read_text(encoding="utf-8"), "paper-v1\n")
        self.assertNotEqual(registry.read_bytes(), before_registry)
        value = json.loads(registry.read_text(encoding="utf-8"))
        self.assertEqual(
            value["pending"][0]["receipt"], "output/stagex/results.receipt.json"
        )
        self.assertFalse(
            (self.root / "process_log/results_pipeline.transaction.json").exists()
        )

    def test_producer_cannot_read_undeclared_live_project_path(self) -> None:
        secret = self.root / "undeclared-secret.txt"
        secret.write_text("UNDECLARED-LIVE-BYTES\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import pathlib\n"
            f"targets = [pathlib.Path({str(secret)!r})]\n"
            f"targets += list(pathlib.Path('/proc').glob('[0-9]*/root{str(secret)}'))\n"
            "for target in targets:\n"
            "    try:\n"
            "        leaked = target.read_text()\n"
            "    except OSError:\n"
            "        continue\n"
            "    raise RuntimeError(f'undeclared live bytes were readable: {leaked!r}')\n" +
            self.analyze_source,
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertNotIn(
            "UNDECLARED-LIVE-BYTES",
            (self.root / "output/stagex/results.json").read_text(encoding="utf-8"),
        )

    def test_producer_gets_no_ambient_environment_or_stdin(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os, sys\n"
            "assert 'ROUND9_DUMMY_SECRET' not in os.environ\n"
            "assert sys.stdin.read() == ''\n" + self.analyze_source,
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["ROUND9_DUMMY_SECRET"] = "dummy-env-secret-264"
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, input="stdin-secret-264", text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_literal_provider_credential_cannot_enter_staged_evidence(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os\n" + self.analyze_source.replace(
                "'schema_version': 1,",
                "'schema_version': 1, 'metadata': "
                "{'leak': os.environ['OPENAI_API_KEY']},",
            ),
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["OPENAI_API_KEY"] = "dummy-provider-secret-264"
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("literal provider credential", completed.stderr)
        self.assertFalse((self.root / "output/stagex/results.json").exists())

    def test_provider_credential_cannot_enter_producer_command_record(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        environment = os.environ.copy()
        secret = "dummy-producer-argv-secret-264"
        environment["OPENAI_API_KEY"] = secret
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py", "--api-key", secret],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("command arguments contain a literal provider credential",
                      completed.stderr)
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())

    def test_provider_credential_cannot_enter_renderer_command_record(self) -> None:
        environment = os.environ.copy()
        secret = "dummy-renderer-argv-secret-264"
        environment["OPENAI_API_KEY"] = secret
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "render", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/render.py", "--api-key", secret],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("command arguments contain a literal provider credential",
                      completed.stderr)
        receipt = json.loads(
            (self.root / "output/stagex/results.receipt.json").read_text(encoding="utf-8")
        )
        self.assertIsNone(receipt["render_run"])
        self.assertNotIn(secret, json.dumps(receipt))

    def test_proxy_password_cannot_enter_command_record(self) -> None:
        environment = os.environ.copy()
        secret = "dummy-proxy-argv-secret-264"
        environment["HTTPS_PROXY"] = (
            "https://proxy-user:dummy-proxy-argv-secret-264@proxy.example:8443"
        )
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py", "--proxy-password", secret],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("command arguments contain a literal provider credential",
                      completed.stderr)
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())

    def test_encoded_proxy_credentials_cannot_enter_command_or_staged_files(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        environment = {
            "HTTPS_PROXY": "http://user:very%40secret@proxy.example:8443"
        }
        for leaked in (
            "very%40secret", "very@secret",
            "http://user:very%40secret@proxy.example:8443",
        ):
            with self.subTest(leaked=leaked):
                with self.assertRaises(module.EvidenceError):
                    module.reject_command_credential_leak(["python3", leaked], environment)
        staged = self.root / "staged-credential"
        staged.mkdir()
        (staged / "leak.txt").write_text(
            "http://user:very%40secret@proxy.example:8443\n", encoding="utf-8"
        )
        with self.assertRaises(module.EvidenceError):
            module.reject_credential_leak(staged, environment)

    def test_token_only_proxy_credentials_cannot_enter_command_or_staged_files(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        environment = {
            "HTTPS_PROXY": "http://token%40only@proxy.example:8443"
        }
        for leaked in (
            "token%40only", "token@only",
            "http://token%40only@proxy.example:8443",
        ):
            with self.subTest(leaked=leaked):
                with self.assertRaises(module.EvidenceError):
                    module.reject_command_credential_leak(["python3", leaked], environment)
        staged = self.root / "staged-token-only-proxy-credential"
        staged.mkdir()
        (staged / "leak.txt").write_text(
            "token@only\n", encoding="utf-8"
        )
        with self.assertRaises(module.EvidenceError):
            module.reject_credential_leak(staged, environment)

    def test_short_ambient_secret_is_rejected_even_when_embedded(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for command in (["python3", "code/test_renderer.py"], ["python3", "test"],
                        ["python3", "--proxy-password=test"]):
            with self.subTest(command=command), self.assertRaises(module.EvidenceError):
                module.reject_command_credential_leak(
                    command, {"OPENAI_API_KEY": "test"}
                )

    def test_stripped_ambient_credential_is_still_scanned_after_execution(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        secret = "dummy-unselected-staged-secret-264"

        def stage_secret(_command: list[str], **_kwargs: object
                         ) -> tuple[int, bytes, bytes, bool]:
            (self.root / "leak.txt").write_text(secret, encoding="utf-8")
            return 0, b"", b"", False

        with (mock.patch.dict(module.os.environ,
                              {"OPENAI_API_KEY": secret}, clear=True),
              mock.patch.object(module, "supervised_command", side_effect=stage_secret)):
            with self.assertRaises(module.EvidenceError):
                module.execute(["/bin/true"], self.root, allow_network=False)

    def test_renderer_receives_no_provider_credentials(self) -> None:
        environment = os.environ.copy()
        environment["OPENAI_API_KEY"] = "dummy-render-secret-264"
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        renderer = self.root / "code/render.py"
        renderer.write_text(
            "import os\n"
            "assert 'OPENAI_API_KEY' not in os.environ\n" +
            renderer.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        run = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        rendered = subprocess.run(
            [sys.executable, str(UTILITY), "render", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/render.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(rendered.returncode, 0, rendered.stdout + rendered.stderr)

    @unittest.skipUnless(
        sys.platform.startswith("linux") and shutil.which("bwrap"),
        "Linux bubblewrap renderer-network check",
    )
    def test_renderer_cannot_reach_host_loopback(self) -> None:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except PermissionError:
            self.skipTest("outer test sandbox forbids loopback sockets")
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        renderer = self.root / "code/render.py"
        renderer.write_text(
            "import socket\n"
            f"probe = socket.socket(); probe.settimeout(1); port = {port}\n"
            "try:\n"
            "    probe.connect(('127.0.0.1', port))\n"
            "except OSError:\n"
            "    pass\n"
            "else:\n"
            "    raise RuntimeError('renderer reached host network')\n"
            "finally:\n"
            "    probe.close()\n" + renderer.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        try:
            self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py",
            )
            self.call(
                "render", "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/render.py",
            )
        finally:
            server.close()

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux bubblewrap command check")
    def test_renderer_bubblewrap_command_unshares_network(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        captured: list[str] = []

        def record(command: list[str], **_kwargs: object
                   ) -> tuple[int, bytes, bytes, bool]:
            captured.extend(command)
            return 0, b"", b"", False

        with (mock.patch.object(module, "trusted_sandbox_executable",
                               side_effect=lambda name: (
                                   "/usr/bin/bwrap" if name == "bwrap" else None
                               )),
              mock.patch.object(module, "ambient_network_is_denied", return_value=False),
              mock.patch.object(module, "supervised_command", side_effect=record),
              mock.patch.object(module, "reject_credential_leak")):
            module.execute(["/bin/true"], self.root, project_root=self.root,
                           allow_network=False)
        self.assertIn("--unshare-net", captured)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux bubblewrap command check")
    def test_renderer_does_not_mount_wrds_service_paths(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        runtime_home = self.root / "host-home"
        wrds_state = runtime_home / ".local/state/zeropaper/wrds"
        wrds_cache = runtime_home / ".cache/zeropaper/wrds"
        wrds_state.mkdir(parents=True)
        wrds_cache.mkdir(parents=True)
        captured: list[str] = []

        def record(command: list[str], **_kwargs: object
                   ) -> tuple[int, bytes, bytes, bool]:
            captured.extend(command)
            return 0, b"", b"", False

        with (mock.patch.dict(module.os.environ, {"HOME": str(runtime_home)}),
              mock.patch.object(module, "trusted_sandbox_executable",
                                side_effect=lambda name: (
                                    "/usr/bin/bwrap" if name == "bwrap" else None
                                )),
              mock.patch.object(module, "ambient_network_is_denied", return_value=False),
              mock.patch.object(module, "supervised_command", side_effect=record),
              mock.patch.object(module, "reject_credential_leak")):
            module.execute(["/bin/true"], self.root, project_root=self.root,
                           allow_network=False)
        self.assertNotIn(str(wrds_state), captured)
        self.assertNotIn(str(wrds_cache), captured)

    def test_macos_sandbox_does_not_grant_keychain_mach_lookup(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        captured: list[str] = []

        def record(command: list[str], **_kwargs: object
                   ) -> tuple[int, bytes, bytes, bool]:
            captured.extend(command)
            return 0, b"", b"", False

        with (mock.patch.object(module.sys, "platform", "darwin"),
              mock.patch.object(module, "trusted_sandbox_executable",
                                side_effect=lambda name: (
                                    "/usr/bin/sandbox-exec"
                                    if name == "sandbox-exec" else None
                                )),
              mock.patch.object(module, "supervised_command", side_effect=record),
              mock.patch.object(module, "reject_credential_leak")):
            module.execute(["/bin/true"], self.root, project_root=self.root,
                           allow_network=False)
        profile = captured[captured.index("-p") + 1]
        self.assertNotIn("(allow mach-lookup)", profile)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux sandbox path check")
    def test_ambient_path_cannot_select_project_sandbox_executable(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        fake_bin = self.root / ".venv/bin"
        fake_bin.mkdir(parents=True, exist_ok=True)
        fake = fake_bin / "bwrap"
        fake.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
        fake.chmod(0o755)
        captured: list[str] = []

        def record(command: list[str], **_kwargs: object
                   ) -> tuple[int, bytes, bytes, bool]:
            captured.extend(command)
            return 0, b"", b"", False

        with (mock.patch.dict(module.os.environ,
                              {"PATH": f"{fake_bin}:/usr/bin:/bin"}),
              mock.patch.object(module, "supervised_command", side_effect=record),
              mock.patch.object(module, "reject_credential_leak")):
            module.execute(["/bin/true"], self.root, project_root=self.root,
                           allow_network=False)
        self.assertEqual(captured[0], "/usr/bin/bwrap")
        self.assertNotIn(str(fake), captured)

    def test_producer_receives_only_plan_selected_provider_credentials(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["UF_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os\n"
            "assert len(os.environ['UF_API_KEY']) == 25\n"
            "assert 'OPENAI_API_KEY' not in os.environ\n" + self.analyze_source,
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["UF_API_KEY"] = "selected-provider-key-264"
        environment["OPENAI_API_KEY"] = "unselected-provider-key-264"
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_producer_imports_only_selected_provider_credential_from_dotenv(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["UF_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / ".env").write_text(
            "UF_API_KEY='selected-dotenv-key-264'\n"
            "OPENAI_API_KEY=unselected-dotenv-key-264\n",
            encoding="utf-8",
        )
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os\n"
            "assert len(os.environ['UF_API_KEY']) == 23\n"
            "assert 'OPENAI_API_KEY' not in os.environ\n" + self.analyze_source,
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment.pop("UF_API_KEY", None)
        environment.pop("OPENAI_API_KEY", None)
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_project_venv_is_mounted_at_neutral_runtime_path(self) -> None:
        venv.create(self.root / ".venv", with_pip=False)
        python = self.root / ".venv/bin/python3"
        site_packages = subprocess.check_output(
            [str(python), "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
            text=True,
        ).strip()
        Path(site_packages, "result_test_dependency.py").write_text(
            "VALUE = 'venv-only'\n", encoding="utf-8"
        )
        script = self.root / "code/analyze.py"
        script.write_text(
            "import result_test_dependency\n"
            "assert result_test_dependency.VALUE == 'venv-only'\n" + self.analyze_source,
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment["VIRTUAL_ENV"] = str(self.root / ".venv")
        environment["PATH"] = str(self.root / ".venv/bin") + os.pathsep + environment["PATH"]
        completed = subprocess.run(
            [sys.executable, str(UTILITY), "run", "--plan",
             "output/stagex/results.plan.json", "--bundle",
             "output/stagex/results.json", "--receipt",
             "output/stagex/results.receipt.json", "--", "python3", "code/analyze.py"],
            cwd=self.root, env=environment, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_project_venv_rejects_project_selected_untrusted_base_runtime(self) -> None:
        venv.create(self.root / ".venv", with_pip=False)
        with tempfile.TemporaryDirectory(
            prefix="external-python-runtime-", dir=self.root.parent
        ) as raw_runtime:
            runtime = Path(raw_runtime)
            (runtime / "bin").mkdir()
            external_python = runtime / "bin/python3"
            external_python.write_text(
                "#!/bin/sh\nexec /usr/bin/python3 \"$@\"\n", encoding="utf-8"
            )
            external_python.chmod(0o755)
            project_python = self.root / ".venv/bin/python3"
            project_python.unlink()
            project_python.symlink_to(external_python)
            config = self.root / ".venv/pyvenv.cfg"
            lines = [
                f"home = {runtime / 'bin'}" if line.lower().startswith("home =") else line
                for line in config.read_text(encoding="utf-8").splitlines()
            ]
            config.write_text("\n".join(lines) + "\n", encoding="utf-8")
            environment = os.environ.copy()
            environment["VIRTUAL_ENV"] = str(self.root / ".venv")
            environment["PATH"] = (
                str(self.root / ".venv/bin") + os.pathsep + environment["PATH"]
            )
            completed = subprocess.run(
                [sys.executable, str(UTILITY), "run", "--plan",
                 "output/stagex/results.plan.json", "--bundle",
                 "output/stagex/results.json", "--receipt",
                 "output/stagex/results.receipt.json", "--", "python3",
                 "code/analyze.py"],
                cwd=self.root, env=environment, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertIn("protected system path", completed.stderr)

    def test_renderer_cannot_replace_live_publication_journal(self) -> None:
        journal = self.root / "process_log/results_pipeline.transaction.json"
        renderer = self.root / "code/render.py"
        renderer.write_text(
            "import pathlib\n"
            "try:\n"
            f"    pathlib.Path({str(journal)!r}).write_text('{{}}\\n')\n"
            "except OSError:\n"
            "    pass\n"
            "else:\n"
            "    raise RuntimeError('live transaction journal was writable')\n" +
            renderer.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )
        self.assertFalse(journal.exists())
        self.call("activate", "--receipt", "output/stagex/results.receipt.json")
        completed = self.call("verify-all", "--rerender")
        self.assertEqual(json.loads(completed.stdout)["status"], "PASS")

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux /proc FD check")
    def test_renderer_does_not_inherit_results_lock_descriptor(self) -> None:
        renderer = self.root / "code/render.py"
        renderer.write_text(
            "import os, pathlib\n"
            "for candidate in pathlib.Path('/proc/self/fd').iterdir():\n"
            "    try:\n"
            "        target = os.readlink(candidate)\n"
            "    except OSError:\n"
            "        continue\n"
            "    if target.endswith('/process_log/results_pipeline.lock'):\n"
            "        raise RuntimeError('untrusted renderer inherited results lock')\n" +
            renderer.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )

    def test_active_receipt_rejects_changed_renderer_command(self) -> None:
        self.record_and_render()
        receipt = self.root / "output/stagex/results.receipt.json"
        exhibit = self.root / "output/stagex/tables/main.tex"
        before_receipt = receipt.read_bytes()
        before_exhibit = exhibit.read_bytes()
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py", "--alt", expected=2,
        )
        self.assertIn("exact recorded command", completed.stderr)
        self.assertEqual(receipt.read_bytes(), before_receipt)
        self.assertEqual(exhibit.read_bytes(), before_exhibit)

    def test_renderer_parent_symlink_is_rejected_before_publication(self) -> None:
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name)
        renderer = self.root / "code/render.py"
        renderer.write_text(
            renderer.read_text(encoding="utf-8").replace(
                "bundle = json.loads",
                "live_parent = root / 'output/stagex/tables'\n"
                "live_parent.rmdir()\n"
                f"live_parent.symlink_to(pathlib.Path({str(outside)!r}), target_is_directory=True)\n"
                "bundle = json.loads",
            ),
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py", expected=2,
        )
        self.assertIn("command failed", completed.stderr)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertTrue((self.root / "output/stagex/tables").is_dir())
        self.assertFalse((self.root / "output/stagex/tables").is_symlink())

    def test_paper_binding_stales_on_prose_change(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        self.bind_paper()
        report = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            "--rerender",
        )
        self.assertEqual(json.loads(report.stdout)["status"], "PASS")
        (self.root / "paper/sections/results.tex").write_text("Changed claim.\n", encoding="utf-8")
        report = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("paper/sections/results.tex", report.stdout)

    def test_non_pass_audit_cannot_bind(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        summary = self.root / "output/evidence/audit.json"
        summary.write_text(
            json.dumps({"verdict": "REVISE", "checkpoint": "stage5-initial",
                        "blocking_findings": ["wrong sign"]}) + "\n",
            encoding="utf-8",
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("cannot bind non-PASS", completed.stderr)

    def test_incomplete_pass_evidence_inventory_cannot_bind(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        summary = self.root / "output/evidence/audit.json"
        value = json.loads(summary.read_text(encoding="utf-8"))
        value["result_receipts_checked"] = []
        summary.write_text(json.dumps(value) + "\n", encoding="utf-8")
        completed = self.bind_paper(expected=2)
        self.assertIn("inventory does not match", completed.stderr)

    def test_non_pass_citation_audit_cannot_bind(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        citation = self.root / "output/evidence/citations.json"
        citation.write_text(
            json.dumps({"verdict": "REVISE", "checkpoint": "stage5-initial",
                        "blocking_findings": ["mischaracterized citation"],
                        "citation_claims": []}) + "\n",
            encoding="utf-8",
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("cannot bind non-PASS", completed.stderr)

    def test_malformed_pass_citation_inventory_cannot_bind(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        citation = self.root / "output/evidence/citations.json"
        value = json.loads(citation.read_text(encoding="utf-8"))
        value["citation_claims"] = [{
            "anchor": "paper/main.tex:1", "claim_text": "Prior work shows X.",
            "cite_keys": ["prior"], "status": "FAITHFUL", "sources": []
        }]
        value["fresh_checks"] = 1
        citation.write_text(json.dumps(value) + "\n", encoding="utf-8")
        completed = self.bind_paper(expected=2)
        self.assertIn("missing required keys", completed.stderr)

    def test_paper_change_between_audit_and_bind_is_rejected(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        (self.root / "paper/sections/results.tex").write_text(
            "Changed after audit.\n", encoding="utf-8"
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("audit input is stale", completed.stderr)

    def test_markdown_revise_cannot_hide_behind_json_pass(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        (self.root / "output/evidence/audit.md").write_text(
            "VERDICT: REVISE\nCHECKPOINT: stage5-initial\n", encoding="utf-8"
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("consistent PASS/checkpoint/digest", completed.stderr)

    def test_bind_requires_distinct_audit_artifacts(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        completed = self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input.json",
            "--summary", "output/evidence/audit.json",
            "--report", "output/evidence/audit.md",
            "--citation-summary", "output/evidence/citations.json",
            "--citation-report", "output/evidence/audit.md",
            "--receipt", "process_log/paper_evidence.receipt.json",
            "--checkpoint", "stage5-initial", expected=2,
        )
        self.assertIn("must be five distinct files", completed.stderr)

    def test_bind_rejects_hardlinked_audit_artifacts(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        citation_report = self.root / "output/evidence/citations.md"
        citation_report.unlink()
        os.link(self.root / "output/evidence/audit.md", citation_report)
        completed = self.bind_paper(expected=2)
        self.assertIn("non-aliased regular file", completed.stderr)

    def test_invalid_utf8_audit_report_is_controlled_failure(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        (self.root / "output/evidence/audit.md").write_bytes(b"\xff\xfe")
        completed = self.bind_paper(expected=2)
        self.assertIn("cannot read evidence audit report", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_unreadable_audit_report_is_controlled_failure(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        report = self.root / "output/evidence/audit.md"
        report.chmod(0)
        try:
            completed = self.bind_paper(expected=2)
        finally:
            report.chmod(0o644)
        self.assertIn("cannot open one non-aliased regular file", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_paper_with_no_computed_evidence_can_bind(self) -> None:
        self.add_paper_audit()
        self.bind_paper()
        report = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            "--rerender",
        )
        self.assertEqual(json.loads(report.stdout)["status"], "PASS")

    def test_verify_paper_revalidates_bound_audit_semantics(self) -> None:
        self.add_paper_audit()
        self.bind_paper()
        summary_path = self.root / "output/evidence/audit.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["verdict"] = "REVISE"
        summary["blocking_findings"] = ["tampered after binding"]
        summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
        receipt_path = self.root / "process_log/paper_evidence.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["audit_summary"]["sha256"] = (
            "sha256:" + hashlib.sha256(summary_path.read_bytes()).hexdigest()
        )
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("cannot bind non-PASS evidence audit", completed.stdout)

    def test_verify_paper_checks_result_receipts_without_rerender(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        self.bind_paper()
        (self.root / "output/stagex/detail.json").write_text(
            '{"rows": [999]}\n', encoding="utf-8"
        )
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("stale bytes at output/stagex/detail.json", completed.stdout)

    def test_verify_paper_cannot_drop_bound_result_inventory(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        self.bind_paper()
        summary_path = self.root / "output/evidence/audit.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["result_receipts_checked"] = []
        summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
        receipt_path = self.root / "process_log/paper_evidence.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["result_receipts"] = []
        receipt["audit_summary"]["sha256"] = (
            "sha256:" + hashlib.sha256(summary_path.read_bytes()).hexdigest()
        )
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        (self.root / "data/input.txt").write_text("changed\n", encoding="utf-8")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("inventory differs from its bound audit input", completed.stdout)

    def test_verify_paper_does_not_self_authorize_citation_reuse(self) -> None:
        self.add_paper_audit(citation=True)
        self.bind_paper()
        summary_path = self.root / "output/evidence/citations.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["citation_claims"][0]["verification"] = "reused"
        summary["fresh_checks"] = 0
        summary["reused_bound_checks"] = 1
        summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
        receipt_path = self.root / "process_log/paper_evidence.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["citation_audit_summary"]["sha256"] = (
            "sha256:" + hashlib.sha256(summary_path.read_bytes()).hexdigest()
        )
        signature = {
            key: summary["citation_claims"][0][key]
            for key in ("claim_text", "cite_keys", "status", "sources")
        }
        receipt["prior_citation_claim_signatures"] = [
            "sha256:" + hashlib.sha256(
                json.dumps(signature, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        ]
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=2,
        )
        self.assertIn("unexpected or missing keys", completed.stderr)

    def test_stale_input_and_exhibit_fail(self) -> None:
        self.record_and_render()
        (self.root / "data/input.txt").write_text("input-v2\n", encoding="utf-8")
        report = self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json", expected=1
        )
        self.assertIn("stale bytes at data/input.txt", report.stdout)

        (self.root / "data/input.txt").write_text("input-v1\n", encoding="utf-8")
        (self.root / "output/stagex/tables/main.tex").write_text("hand edited\n", encoding="utf-8")
        report = self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json", expected=1
        )
        self.assertIn("stale bytes at output/stagex/tables/main.tex", report.stdout)

    def test_control_characters_are_rejected_in_runtime_paths(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["artifacts"] = ["output/stagex/bad\nname.json"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("control characters are forbidden", completed.stderr)

    def test_unreadable_declared_directory_fails_loudly(self) -> None:
        hidden = self.root / "data/hidden"
        hidden.mkdir()
        (hidden / "secret.txt").write_text("secret\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace(
                "'inputs': ['data/input.txt']", "'inputs': ['data']"
            ),
            encoding="utf-8",
        )
        hidden.chmod(0)
        try:
            completed = self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py", expected=2,
            )
        finally:
            hidden.chmod(0o700)
        self.assertRegex(completed.stderr, r"cannot (?:inspect|open) declared directory")
        self.assertNotIn("Traceback", completed.stderr)

    def test_unsafe_descendant_names_fail_before_receipt_publication(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace(
                "'inputs': ['data/input.txt']", "'inputs': ['data']"
            ),
            encoding="utf-8",
        )
        for name in ("bad\nname", "bad\\name"):
            with self.subTest(name=name):
                unsafe = self.root / "data" / name
                unsafe.write_text("unsafe\n", encoding="utf-8")
                try:
                    completed = self.call(
                        "run", "--bundle", "output/stagex/results.json",
                        "--receipt", "output/stagex/results.receipt.json", "--",
                        sys.executable, "code/analyze.py", expected=2,
                    )
                finally:
                    unsafe.unlink(missing_ok=True)
                self.assertIn(
                    "control characters and backslashes are forbidden",
                    completed.stderr,
                )
                self.assertNotIn("Traceback", completed.stderr)
                self.assertFalse(
                    (self.root / "output/stagex/results.receipt.json").exists()
                )

    @unittest.skipIf(os.name == "nt", "byte filenames are POSIX-specific")
    def test_non_utf8_descendant_name_is_a_controlled_prepublication_failure(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace(
                "'inputs': ['data/input.txt']", "'inputs': ['data']"
            ),
            encoding="utf-8",
        )
        raw_name = os.fsencode(self.root / "data") + b"/bad-\xff"
        descriptor = os.open(raw_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(descriptor, b"unsafe\n")
        os.close(descriptor)
        try:
            completed = self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py", expected=2,
            )
        finally:
            os.unlink(raw_name)
        self.assertIn("not valid UTF-8", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())

    def test_init_registry_fails_on_unreadable_output_subtree(self) -> None:
        (self.root / "process_log/results_registry.json").unlink()
        hidden = self.root / "output/unreadable"
        hidden.mkdir()
        hidden.chmod(0)
        try:
            completed = self.call("init-registry", expected=2)
        finally:
            hidden.chmod(0o700)
        self.assertRegex(completed.stderr, r"cannot (?:inspect|open) declared directory")
        self.assertFalse((self.root / "process_log/results_registry.json").exists())

    def test_receipt_shaped_symlink_fails_discovery_and_registry_init(self) -> None:
        shaped = self.root / "output/hiddenresults.receipt.json"
        shaped.symlink_to(self.root / "data/input.txt")
        completed = self.call("verify-all", expected=2)
        self.assertIn("receipt-shaped path", completed.stderr)
        (self.root / "process_log/results_registry.json").unlink()
        completed = self.call("init-registry", expected=2)
        self.assertIn("receipt-shaped path", completed.stderr)

    def test_deep_declared_directory_is_iterative(self) -> None:
        directories: list[Path] = []
        current = self.root / "data/deep"
        current.mkdir()
        directories.append(current)
        for _ in range(1050):
            current = current / "d"
            current.mkdir()
            directories.append(current)
        leaf = current / "leaf.txt"
        leaf.write_text("leaf\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace(
                "'inputs': ['data/input.txt']", "'inputs': ['data']"
            ),
            encoding="utf-8",
        )
        try:
            self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py",
            )
        finally:
            leaf.unlink(missing_ok=True)
            for directory in reversed(directories):
                directory.rmdir()

    def test_wide_declared_directory_uses_depth_bounded_descriptors(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        wide = self.root / "data/wide"
        wide.mkdir()
        for index in range(100):
            (wide / f"d{index:03d}").mkdir()
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        lowered = min(64, hard)
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (lowered, hard))
            snapshot = module.fingerprint(self.root, "data/wide")
            copied = self.root / "wide-copy"
            module._copy_evidence_path(wide, copied)
        finally:
            resource.setrlimit(resource.RLIMIT_NOFILE, (soft, hard))
        self.assertEqual(len(snapshot["entries"]), 100)
        self.assertEqual(len(list(copied.iterdir())), 100)

    def test_fingerprint_rejects_ancestor_swap_after_lexical_validation(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_ancestor", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name)
        (outside / "input.txt").write_text("outside-secret\n", encoding="utf-8")
        original_data = self.root / "data"
        held_data = self.root / "data-held"
        original_open = module._open_directory_path
        swapped = False

        def swap_after_project_path(path: Path) -> int:
            nonlocal swapped
            if not swapped and path == original_data:
                original_data.rename(held_data)
                original_data.symlink_to(outside, target_is_directory=True)
                swapped = True
            return original_open(path)

        try:
            with mock.patch.object(module, "_open_directory_path", side_effect=swap_after_project_path):
                with self.assertRaises(module.EvidenceError):
                    module.fingerprint(self.root, "data/input.txt")
        finally:
            if original_data.is_symlink():
                original_data.unlink()
            if held_data.exists():
                held_data.rename(original_data)
        self.assertTrue(swapped)

    def test_secure_project_removal_does_not_follow_swapped_ancestor(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_remove", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name)
        victim = outside / "main.tex"
        victim.write_text("outside\n", encoding="utf-8")
        local = self.root / "output/stagex/tables/main.tex"
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text("local\n", encoding="utf-8")
        moved = self.root / "output-real"
        original = module.project_path
        swapped = False

        def swap_after_validation(root: Path, raw: str, **kwargs: object):
            nonlocal swapped
            result = original(root, raw, **kwargs)
            if not swapped and raw == "output/stagex/tables/main.tex":
                (self.root / "output").rename(moved)
                (self.root / "output").symlink_to(outside, target_is_directory=True)
                swapped = True
            return result

        with mock.patch.object(module, "project_path", side_effect=swap_after_validation):
            with self.assertRaises(module.EvidenceError):
                module._remove_project_path(self.root, "output/stagex/tables/main.tex")
        self.assertEqual(victim.read_text(encoding="utf-8"), "outside\n")
        (self.root / "output").unlink()
        moved.rename(self.root / "output")
        self.assertEqual(local.read_text(encoding="utf-8"), "local\n")

    def test_copied_directory_retains_owner_cleanup_permissions(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_copy_mode", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = self.root / "data/mode-zero"
        source.mkdir()
        source_fd = module._open_entry_read(source)
        source.chmod(0)
        destination = self.root / "output/stagex/copied"
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            module._copy_evidence_path(source, destination, source_fd=source_fd)
        finally:
            os.close(source_fd)
            source.chmod(0o700)
        self.assertEqual(
            stat.S_IMODE(destination.stat().st_mode) & stat.S_IRWXU,
            stat.S_IRWXU,
        )
        parent_fd = module._open_directory_path(destination.parent)
        try:
            module._remove_entry_at(parent_fd, destination.name)
        finally:
            os.close(parent_fd)
        self.assertFalse(destination.exists())

    def test_isolated_workspace_canonicalizes_symlinked_temp_root(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_temp_alias", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        external_temp = tempfile.TemporaryDirectory()
        self.addCleanup(external_temp.cleanup)
        external_root = Path(external_temp.name)
        physical = external_root / "physical-temp"
        physical.mkdir()
        alias = external_root / "temp-alias"
        alias.symlink_to(physical, target_is_directory=True)
        with mock.patch.object(module.tempfile, "tempdir", str(alias)):
            with module.isolated_workspace(self.root, ["data/input.txt"], []) as workspace:
                self.assertEqual(workspace.parent, physical.resolve())
                self.assertTrue((workspace / "data/input.txt").is_file())

    def test_isolated_workspace_rejects_temp_root_inside_project(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_temp_overlap", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        project_temp = self.root / "data/tmp"
        project_temp.mkdir()
        with mock.patch.object(module.tempfile, "tempdir", str(project_temp)):
            with self.assertRaisesRegex(module.EvidenceError, "outside the project"):
                with module.isolated_workspace(self.root, ["data"], []):
                    self.fail("overlapping temp root was accepted")

    def test_uv_managed_python_runtime_root_is_supported(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_uv_runtime", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        home_temp = tempfile.TemporaryDirectory()
        self.addCleanup(home_temp.cleanup)
        fake_home = Path(home_temp.name)
        runtime = fake_home / ".local/share/uv/python/cpython-3.12"
        (runtime / "bin").mkdir(parents=True)
        interpreter = runtime / "bin/python3"
        interpreter.write_text("runtime\n", encoding="utf-8")
        venv = self.root / ".venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text(
            f"home = {runtime / 'bin'}\n", encoding="utf-8"
        )
        (venv / "bin/python3").symlink_to(interpreter)
        with mock.patch.object(module.Path, "home", return_value=fake_home):
            self.assertEqual(
                module.venv_base_roots(venv, self.root),
                [fake_home / ".local/share/uv/python"],
            )

    def test_active_receipt_cannot_rebaseline_itself_to_changed_input(self) -> None:
        self.record_and_render()
        changed = self.root / "data/input.txt"
        changed.write_text("input-v2\n", encoding="utf-8")
        receipt_path_value = self.root / "output/stagex/results.receipt.json"
        receipt = json.loads(receipt_path_value.read_text(encoding="utf-8"))
        receipt["producer_run"]["inputs"][0]["sha256"] = (
            "sha256:" + hashlib.sha256(changed.read_bytes()).hexdigest()
        )
        receipt_path_value.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        completed = self.call("verify-all", expected=2)
        self.assertIn("registered result receipt bytes are stale", completed.stderr)

    def test_receipt_cannot_delete_its_provenance_inventory(self) -> None:
        self.record_and_render()
        receipt_path = self.root / "output/stagex/results.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        for key in ("code", "inputs", "renderer_code", "artifacts"):
            receipt["producer_run"][key] = []
        receipt["producer_run"]["reproducibility"] = "exact"
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        registry_path = self.root / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["receipt_fingerprints"]["output/stagex/results.receipt.json"] = {
            "path": "output/stagex/results.receipt.json", "kind": "file",
            "sha256": "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        }
        registry_path.write_text(json.dumps(registry) + "\n", encoding="utf-8")
        completed = self.call("verify-all", "--rerender", expected=1)
        self.assertIn("inventory differs from the plan", completed.stdout)

    def test_receipt_directory_snapshot_must_be_structurally_possible(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace(
                "'inputs': ['data/input.txt']", "'inputs': ['data']"
            ),
            encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        receipt_path = self.root / "output/stagex/results.receipt.json"
        original = json.loads(receipt_path.read_text(encoding="utf-8"))

        impossible = json.loads(json.dumps(original))
        entries = [{"path": "missing/child.txt", "kind": "file",
                    "sha256": "sha256:" + "0" * 64}]
        impossible["producer_run"]["inputs"][0]["entries"] = entries
        impossible["producer_run"]["inputs"][0]["sha256"] = (
            "sha256:" + hashlib.sha256(
                json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
        )
        receipt_path.write_text(json.dumps(impossible) + "\n", encoding="utf-8")
        completed = self.call(
            "validate-receipt", "--receipt", "output/stagex/results.receipt.json",
            expected=2,
        )
        self.assertIn("missing or non-directory parent", completed.stderr)

        wrong_digest = json.loads(json.dumps(original))
        wrong_digest["producer_run"]["inputs"][0]["sha256"] = "sha256:" + "f" * 64
        receipt_path.write_text(json.dumps(wrong_digest) + "\n", encoding="utf-8")
        completed = self.call(
            "validate-receipt", "--receipt", "output/stagex/results.receipt.json",
            expected=2,
        )
        self.assertIn("does not match its directory entries", completed.stderr)

    def test_empty_directory_membership_stales_declared_input_directory(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        analysis = self.root / "code/analyze.py"
        analysis.write_text(
            self.analyze_source.replace("['data/input.txt']", "['data']"),
            encoding="utf-8",
        )
        self.record_and_render()
        (self.root / "data/new-empty-directory").mkdir()
        report = self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json", expected=1
        )
        self.assertIn("stale bytes at data", report.stdout)

    def test_renderer_cannot_mutate_evidence(self) -> None:
        renderer = self.root / "code/render.py"
        renderer.write_text(
            renderer.read_text(encoding="utf-8").replace(
                "if (trigger_root / 'mutate-input').exists():", "if True:"
            ), encoding="utf-8",
        )
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py", expected=2,
        )
        self.assertIn("command failed", completed.stderr)
        self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")

    def test_analysis_cannot_bind_post_run_input_bytes(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace(
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                "(root / 'data/input.txt').write_text('input-v2\\n')\n"
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
            ), encoding="utf-8"
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("isolated producer source", completed.stderr)
        self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())
        self.assertFalse((self.root / "output/stagex/detail.json").exists())

    def test_child_output_is_captured_without_corrupting_json_or_leaking_secrets(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            "import os\nprint('progress line')\nprint(os.environ['OPENAI_API_KEY'])\n" +
            self.analyze_source,
            encoding="utf-8",
        )
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["provider_credentials"] = ["OPENAI_API_KEY"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        secret = "provider-secret-output-264"
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": secret}):
            completed = self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py", expected=2,
            )
        self.assertNotIn(secret, completed.stdout + completed.stderr)
        self.assertIn("output contains a literal provider credential", completed.stderr)
        self.assertFalse((self.root / "output/stagex/results.receipt.json").exists())

        script.write_text(
            "print('safe progress')\n" + self.analyze_source,
            encoding="utf-8",
        )
        plan.pop("provider_credentials")
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "PENDING_RENDER")
        self.assertIn("safe progress", completed.stderr)

    def test_declared_directory_rejects_nested_credentials(self) -> None:
        (self.root / "data/.env").write_text("TOKEN=unselected-secret\n", encoding="utf-8")
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace("['data/input.txt']", "['data']"),
            encoding="utf-8",
        )
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = ["data"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("credential-bearing descendant", completed.stderr)
        self.assertFalse((self.root / "output/stagex/detail.json").exists())

    def test_all_dotenv_prefixes_are_forbidden(self) -> None:
        for name in (".envrc", ".env-local", ".ENV", ".Env.production"):
            with self.subTest(name=name):
                secret = self.root / "data" / name
                secret.write_text("TOKEN=unselected-secret\n", encoding="utf-8")
                plan_path = self.root / "output/stagex/results.plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["producer_inputs"] = [f"data/{name}"]
                plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
                completed = self.call(
                    "run", "--bundle", "output/stagex/results.json",
                    "--receipt", "output/stagex/results.receipt.json", "--",
                    sys.executable, "code/analyze.py", expected=2,
                )
                self.assertIn("credential-bearing path", completed.stderr)
                secret.unlink()

    def test_hardlinked_credential_aliases_are_forbidden(self) -> None:
        (self.root / ".env").write_text("OPENAI_API_KEY=supersecretvalue\n", encoding="utf-8")
        for alias in (self.root / "data/input.txt", self.root / "data/nested/alias.txt"):
            with self.subTest(alias=alias):
                alias.parent.mkdir(parents=True, exist_ok=True)
                alias.unlink(missing_ok=True)
                os.link(self.root / ".env", alias)
                plan_path = self.root / "output/stagex/results.plan.json"
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                plan["producer_inputs"] = [
                    "data" if alias.parent.name == "nested" else "data/input.txt"
                ]
                plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
                completed = self.call(
                    "run", "--bundle", "output/stagex/results.json",
                    "--receipt", "output/stagex/results.receipt.json", "--",
                    sys.executable, "code/analyze.py", expected=2,
                )
                self.assertIn("non-aliased regular file", completed.stderr)
                alias.unlink()

    def test_git_credential_store_cannot_be_declared(self) -> None:
        (self.root / ".git").mkdir()
        (self.root / ".git/push-credentials").write_text("token\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_inputs"] = [".git/push-credentials"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("credential-bearing path", completed.stderr)

    def test_analysis_os_replace_cannot_corrupt_input(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace(
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                "replacement = root / 'data/input.replacement'\n"
                "replacement.write_text('input-v2\\n')\n"
                "os.replace(replacement, root / 'data/input.txt')\n"
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
            ), encoding="utf-8"
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("isolated producer source", completed.stderr)
        self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")
        self.assertFalse((self.root / "output/stagex/detail.json").exists())

    def test_rollback_does_not_follow_child_created_parent_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as outside_raw:
            outside = Path(outside_raw)
            outside_input = outside / "input.txt"
            outside_input.write_text("outside-v1\n", encoding="utf-8")
            script = self.root / "code/analyze.py"
            script.write_text(
                self.analyze_source.replace(
                    "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                    "(root / 'data').rename(root / 'data-displaced')\n"
                    f"(root / 'data').symlink_to({str(outside)!r}, target_is_directory=True)\n"
                    "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                ), encoding="utf-8",
            )
            completed = self.call(
                "run", "--bundle", "output/stagex/results.json",
                "--receipt", "output/stagex/results.receipt.json", "--",
                sys.executable, "code/analyze.py", expected=2,
            )
            self.assertIn("isolated producer source", completed.stderr)
            self.assertFalse((self.root / "data").is_symlink())
            self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")
            self.assertEqual(outside_input.read_text(), "outside-v1\n")

    def test_analysis_cannot_mutate_renderer_code(self) -> None:
        script = self.root / "code/analyze.py"
        renderer = self.root / "code/render.py"
        before = renderer.read_bytes()
        script.write_text(
            self.analyze_source.replace(
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                "replacement = root / 'code/render.replacement'\n"
                "replacement.write_text('pass\\n')\n"
                "os.replace(replacement, root / 'code/render.py')\n"
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
            ), encoding="utf-8"
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("isolated producer source", completed.stderr)
        self.assertEqual(renderer.read_bytes(), before)

    def test_analysis_cannot_prewrite_renderer_owned_exhibit(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace(
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
                "(root / 'output/stagex/tables/main.tex').write_text('forged\\n')\n"
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text",
            ), encoding="utf-8"
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("analysis wrote renderer-owned exhibit paths", completed.stderr)
        self.assertFalse((self.root / "output/stagex/tables/main.tex").exists())

    def test_preexisting_declared_output_stops_before_analysis(self) -> None:
        (self.root / "output/stagex/detail.json").write_text("old\n")
        script = self.root / "code/analyze.py"
        script.write_text("pathlib.Path('data/input.txt').write_text('ran\\n')\n" +
                          self.analyze_source, encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("already exists before analysis", completed.stderr)
        self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")

    def test_fifo_plan_fails_without_holding_results_lock(self) -> None:
        plan_path = self.root / "output/stagex/fifo.plan.json"
        os.mkfifo(plan_path)
        completed = self.call(
            "run", "--plan", "output/stagex/fifo.plan.json",
            "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("expected one non-aliased regular file", completed.stderr)
        self.assert_results_lock_available()

    def test_fifo_bundle_fails_without_holding_results_lock(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace(
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle, indent=2) + '\\n')",
                "os.mkfifo(root / os.environ['RESULTS_BUNDLE_PATH'])",
            ),
            encoding="utf-8",
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("expected one non-aliased regular file", completed.stderr)
        self.assert_results_lock_available()

    def test_fifo_artifact_fails_without_holding_results_lock(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(
            self.analyze_source.replace(
                "artifact.write_text(json.dumps({'rows': [1, 2, 3]}) + '\\n')",
                "os.mkfifo(artifact)",
            ),
            encoding="utf-8",
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("expected one non-aliased regular file", completed.stderr)
        self.assert_results_lock_available()

    def test_renderer_only_change_requires_fresh_attempt(self) -> None:
        self.record_and_render()
        with (self.root / "code/render.py").open("a", encoding="utf-8") as handle:
            handle.write("# presentation-only revision\n")
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py", expected=2,
        )
        self.assertIn("producer receipt is stale", completed.stderr)

    def test_reserved_malformed_receipt_fails_closed(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/extra_results.receipt.json").write_text("not json\n")
        completed = self.call("verify-all", expected=2)
        self.assertIn("absent from registry", completed.stderr)

    def test_deleted_active_receipt_fails_closed(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/results.receipt.json").unlink()
        completed = self.call("verify-all", expected=2)
        self.assertIn("registered result receipt is unavailable", completed.stderr)

    def test_shared_producer_code_change_stales_active_receipt(self) -> None:
        self.record_and_render()
        with (self.root / "code/analyze.py").open("a", encoding="utf-8") as handle:
            handle.write("# shared-code revision\n")
        completed = self.call("verify-all", expected=1)
        self.assertIn("producer_run.code", completed.stdout)

    def test_shared_code_change_can_be_replaced_by_fresh_attempt(self) -> None:
        self.record_and_render()
        revised = self.analyze_source.replace(
            "output/stagex/", "output/stagex/v2/"
        ) + "# shared-code revision\n"
        (self.root / "code/analyze.py").write_text(revised, encoding="utf-8")
        self.write_plan(
            "output/stagex/v2/results.plan.json", prefix="output/stagex/v2/",
            analyze="code/analyze.py", render="code/render.py",
        )
        completed = self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json",
            "--supersedes", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "PENDING_RENDER")

    def test_multi_active_shared_code_can_be_replaced_sequentially(self) -> None:
        shared = self.root / "code/shared.py"
        shared.write_text(
            """import json, os, pathlib
root = pathlib.Path.cwd()
bundle_path = pathlib.PurePosixPath(os.environ['RESULTS_BUNDLE_PATH'])
prefix = bundle_path.parent.as_posix()
artifact_path = prefix + '/detail.json'
(root / artifact_path).write_text(json.dumps({'value': 2}) + '\\n')
bundle = {
  'schema_version': 1,
  'producer': {'name': 'shared-test', 'code': ['code/shared.py'],
               'inputs': ['data/input.txt'], 'reproducibility': 'captured'},
  'results': {'main.value': {'description': 'Main value', 'value': '2'}},
  'artifacts': [{'path': artifact_path, 'description': 'Detail',
                 'media_type': 'application/json'}],
  'renderer': {'code': []},
  'exhibits': []
}
(root / bundle_path).write_text(json.dumps(bundle, indent=2) + '\\n')
""", encoding="utf-8",
        )

        def write_shared_plan(stem: str) -> str:
            prefix = f"output/{stem}/"
            self.write_plan(
                prefix + "results.plan.json", prefix=prefix,
                analyze="code/shared.py", render="code/render.py",
            )
            plan_path = self.root / prefix / "results.plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["renderer_code"] = []
            plan["exhibits"] = []
            plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
            return prefix

        def create_active(stem: str) -> None:
            prefix = write_shared_plan(stem)
            self.call(
                "run", "--plan", prefix + "results.plan.json",
                "--bundle", prefix + "results.json",
                "--receipt", prefix + "results.receipt.json", "--",
                sys.executable, "code/shared.py",
            )
            self.call("activate", "--receipt", prefix + "results.receipt.json")

        create_active("one")
        create_active("two")
        with shared.open("a", encoding="utf-8") as handle:
            handle.write("# shared-code revision\n")

        blocked_prefix = write_shared_plan("blocked_without_replacement")
        blocked = self.call(
            "run", "--plan", blocked_prefix + "results.plan.json",
            "--bundle", blocked_prefix + "results.json",
            "--receipt", blocked_prefix + "results.receipt.json", "--",
            sys.executable, "code/shared.py", expected=2,
        )
        self.assertIn("active evidence is stale before analysis", blocked.stderr)

        prefix = write_shared_plan("one_v2")
        completed = self.call(
            "run", "--plan", prefix + "results.plan.json",
            "--bundle", prefix + "results.json",
            "--receipt", prefix + "results.receipt.json",
            "--supersedes", "output/one/results.receipt.json", "--",
            sys.executable, "code/shared.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "PENDING_ACTIVATION")
        self.call("activate", "--receipt", prefix + "results.receipt.json")
        incomplete = self.call("verify-all", expected=2)
        self.assertIn("activated replacement handoff is incomplete", incomplete.stderr)
        blocked_audit = self.call(
            "prepare-audit", "--output", "output/evidence/blocked.json",
            "--checkpoint", "replacement-handoff", expected=2,
        )
        self.assertIn("activated replacement handoff is incomplete", blocked_audit.stderr)
        state_path = self.root / "process_log/pipeline_state.json"
        state_path.write_text(json.dumps({
            "stage_one_result_receipt": prefix + "results.receipt.json",
            "stage_two_result_receipt": "output/two/results.receipt.json",
        }) + "\n", encoding="utf-8")
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["stage_one_result_receipt"],
            prefix + "results.receipt.json",
        )
        self.call(
            "retire", "--receipt", "output/one/results.receipt.json",
            "--reason", "superseded after pointer handoff",
            "--superseded-by", prefix + "results.receipt.json",
        )
        stale_audit = self.call(
            "prepare-audit", "--output", "output/evidence/second_stale.json",
            "--checkpoint", "replacement-handoff", expected=2,
        )
        self.assertIn("output/two/results.receipt.json", stale_audit.stderr)
        self.assertIn("producer_run.code", stale_audit.stderr)
        still_stale = self.call("verify-all", expected=1)
        self.assertIn("output/two/results.receipt.json", still_stale.stdout)
        self.assertIn("producer_run.code", still_stale.stdout)

        second_prefix = write_shared_plan("two_v2")
        completed = self.call(
            "run", "--plan", second_prefix + "results.plan.json",
            "--bundle", second_prefix + "results.json",
            "--receipt", second_prefix + "results.receipt.json",
            "--supersedes", "output/two/results.receipt.json", "--",
            sys.executable, "code/shared.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "PENDING_ACTIVATION")
        self.call("activate", "--receipt", second_prefix + "results.receipt.json")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage_two_result_receipt"] = second_prefix + "results.receipt.json"
        state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")
        self.assertEqual(
            json.loads(state_path.read_text(encoding="utf-8"))["stage_two_result_receipt"],
            second_prefix + "results.receipt.json",
        )
        self.call(
            "retire", "--receipt", "output/two/results.receipt.json",
            "--reason", "superseded after pointer handoff",
            "--superseded-by", second_prefix + "results.receipt.json",
        )
        final = self.call("verify-all")
        self.assertEqual(len(json.loads(final.stdout)["receipts"]), 2)
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\documentclass{article}\n\\begin{document}Checked.\\end{document}\n",
            encoding="utf-8",
        )
        prepared = self.call(
            "prepare-audit", "--output", "output/evidence/final.json",
            "--checkpoint", "replacement-complete",
        )
        self.assertEqual(json.loads(prepared.stdout)["status"], "PREPARED")

    def test_missing_registry_fails_even_when_receipts_are_deleted(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/results.receipt.json").unlink()
        (self.root / "process_log/results_registry.json").unlink()
        completed = self.call("verify-all", expected=2)
        self.assertIn("missing durable result registry", completed.stderr)

    def test_run_cannot_heal_a_deleted_registry(self) -> None:
        self.record_and_render()
        (self.root / "process_log/results_registry.json").unlink()
        completed = self.call(
            "run", "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("missing durable result registry", completed.stderr)

    def test_manual_registry_initialization_is_explicit_and_refuses_history(self) -> None:
        registry = self.root / "process_log/results_registry.json"
        registry.unlink()
        self.call("init-registry")
        value = json.loads(registry.read_text(encoding="utf-8"))
        self.assertEqual(value["pending"], [])
        self.record_and_render()
        registry.unlink()
        completed = self.call("init-registry", expected=2)
        self.assertIn("after result receipts exist", completed.stderr)

    def test_manual_init_bootstraps_process_log_and_full_lifecycle(self) -> None:
        shutil.rmtree(self.root / "process_log")
        self.call("init-registry")
        self.assertTrue((self.root / "process_log/results_pipeline.lock").is_file())
        self.record_and_render()
        completed = self.call("verify-all", "--require-one", "--rerender")
        self.assertEqual(json.loads(completed.stdout)["status"], "PASS")

    def test_project_lock_serializes_and_rejects_a_second_pending_run(self) -> None:
        processes: list[subprocess.Popen[str]] = []
        for name, delay in (("slow", 0.4), ("fast", 0.0)):
            code_path = f"code/{name}.py"
            artifact = f"output/stagex/{name}/detail.json"
            bundle = f"output/stagex/{name}/results.json"
            receipt = f"output/stagex/{name}/results.receipt.json"
            plan = f"output/stagex/{name}/results.plan.json"
            (self.root / f"output/stagex/{name}").mkdir(parents=True)
            (self.root / code_path).write_text(
                "import json, os, pathlib, time\n"
                f"time.sleep({delay})\n"
                "root = pathlib.Path.cwd()\n"
                f"(root / {artifact!r}).write_text('{{}}\\n')\n"
                "value = {'schema_version': 1, 'producer': {'name': 'concurrent', "
                f"'code': [{code_path!r}], 'inputs': ['data/input.txt'], "
                "'reproducibility': 'exact'}, 'results': {'x': {'description': 'x', "
                "'value': 1}}, 'artifacts': [{'path': " + repr(artifact) + ", "
                "'description': 'detail'}], 'renderer': {'code': []}, 'exhibits': []}\n"
                "(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(value) + '\\n')\n",
                encoding="utf-8",
            )
            self.write_plan(plan, prefix=f"output/stagex/{name}/",
                            analyze=code_path, render="code/render.py")
            plan_value = json.loads((self.root / plan).read_text())
            plan_value["renderer_code"] = []
            plan_value["exhibits"] = []
            (self.root / plan).write_text(json.dumps(plan_value) + "\n")
            command = [sys.executable, str(UTILITY), "run", "--plan", plan,
                       "--bundle", bundle, "--receipt", receipt, "--",
                       sys.executable, code_path]
            processes.append(subprocess.Popen(
                command, cwd=self.root, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ))
            if name == "slow":
                import time
                time.sleep(0.05)
        results = [process.communicate(timeout=10) + (process.returncode,)
                   for process in processes]
        self.assertEqual([result[2] for result in results], [0, 2], results)
        self.assertIn("existing pending result receipt", results[1][1])
        self.call("activate", "--receipt", "output/stagex/slow/results.receipt.json")
        self.call(
            "run", "--plan", "output/stagex/fast/results.plan.json",
            "--bundle", "output/stagex/fast/results.json",
            "--receipt", "output/stagex/fast/results.receipt.json", "--",
            sys.executable, "code/fast.py",
        )
        self.call("activate", "--receipt", "output/stagex/fast/results.receipt.json")
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            registry["active"],
            ["output/stagex/fast/results.receipt.json",
             "output/stagex/slow/results.receipt.json"],
        )

    def test_interrupted_parent_publication_recovers_from_valid_journal(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text("paper-v1\n", encoding="utf-8")
        code = (
            "import importlib.util, json, os, pathlib\n"
            f"utility = pathlib.Path({str(UTILITY)!r})\n"
            "spec = importlib.util.spec_from_file_location('rp', utility)\n"
            "module = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(module)\n"
            "root = pathlib.Path.cwd()\n"
            "registry, _ = module.load_registry(root)\n"
            "module.prepare_lifecycle_transaction(root, "
            "cleanup_paths=['output/stagex/crash/results.json', "
            "'output/stagex/crash/results.receipt.json'], restore_paths=[], "
            "registry_before=registry)\n"
            "target = root / 'output/stagex/crash'\n"
            "target.mkdir(parents=True)\n"
            "(target / 'results.json').write_text('{}\\n')\n"
            "(target / 'results.receipt.json').write_text('{}\\n')\n"
            "registry['active'].append('output/stagex/crash/results.receipt.json')\n"
            "module.atomic_json(root / module.REGISTRY_PATH, registry)\n"
            "os._exit(9)\n"
        )
        crashed = subprocess.run([sys.executable, "-B", "-c", code], cwd=self.root)
        self.assertEqual(crashed.returncode, 9)
        self.call("verify-all")
        self.assertEqual(
            (self.root / "paper/main.tex").read_text(encoding="utf-8"), "paper-v1\n"
        )
        self.assertFalse((self.root / "output/stagex/crash/results.json").exists())
        self.assertFalse(
            (self.root / "output/stagex/crash/results.receipt.json").exists()
        )
        self.assertEqual(
            json.loads((self.root / "process_log/results_registry.json").read_text()),
            {"kind": "result_registry", "registry_version": 1,
             "active": [], "pending": [], "retired": [],
             "receipt_fingerprints": {}},
        )
        self.assertFalse(
            (self.root / "process_log/results_pipeline.transaction.json").exists()
        )

    def test_pending_render_crash_after_receipt_write_rolls_back(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        receipt = self.root / "output/stagex/results.receipt.json"
        registry = self.root / "process_log/results_registry.json"
        before_receipt = receipt.read_bytes()
        before_registry = registry.read_bytes()
        self.interrupt_pending_render_publication(update_registry=False)
        self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json",
            expected=1,
        )
        self.assertEqual(receipt.read_bytes(), before_receipt)
        self.assertEqual(registry.read_bytes(), before_registry)
        self.assertFalse(
            (self.root / "process_log/results_pipeline.transaction.json").exists()
        )

    def test_pending_render_crash_after_registry_write_rolls_back(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        receipt = self.root / "output/stagex/results.receipt.json"
        registry = self.root / "process_log/results_registry.json"
        before_receipt = receipt.read_bytes()
        before_registry = registry.read_bytes()
        self.interrupt_pending_render_publication(update_registry=True)
        self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json",
            expected=1,
        )
        self.assertEqual(receipt.read_bytes(), before_receipt)
        self.assertEqual(registry.read_bytes(), before_registry)
        self.assertFalse(
            (self.root / "process_log/results_pipeline.transaction.json").exists()
        )

    def test_preparing_and_terminal_transaction_cleanup_is_idempotent(self) -> None:
        journal = self.root / "process_log/results_pipeline.transaction.json"
        backup = self.root / "process_log/.results_pipeline-transaction-backup"
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        transaction = {
            "transaction_version": 1,
            "phase": "preparing",
            "cleanup_paths": ["output/stagex/never-published.json"],
            "backups": [{"path": "output/stagex/old.json", "backup": "0"}],
            "registry_before": registry,
        }
        journal.write_text(json.dumps(transaction) + "\n", encoding="utf-8")
        backup.mkdir()
        (backup / "partial").write_text("partial\n", encoding="utf-8")
        self.call("verify-all")
        self.assertFalse(journal.exists())
        self.assertFalse(backup.exists())

        transaction["phase"] = "committed"
        journal.write_text(json.dumps(transaction) + "\n", encoding="utf-8")
        self.call("verify-all")
        self.assertFalse(journal.exists())
        self.assertFalse(backup.exists())

    def test_forged_transaction_cannot_remove_non_result_project_files(self) -> None:
        (self.root / "paper").mkdir()
        victim = self.root / "paper/main.tex"
        victim.write_text("keep me\n", encoding="utf-8")
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        journal = self.root / "process_log/results_pipeline.transaction.json"
        backup = self.root / "process_log/.results_pipeline-transaction-backup"
        backup.mkdir()
        journal.write_text(json.dumps({
            "transaction_version": 1,
            "phase": "prepared",
            "cleanup_paths": ["paper/main.tex"],
            "backups": [],
            "registry_before": registry,
        }) + "\n", encoding="utf-8")
        completed = self.call("verify-all", expected=2)
        self.assertIn("outside the result-owned output namespace", completed.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), "keep me\n")
        self.assertTrue(journal.exists())

    def test_inline_python_cannot_claim_trailing_declared_script(self) -> None:
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "-c", "exec(open('code/analyze.py').read())", "code/analyze.py",
            expected=2,
        )
        self.assertIn("inline/module code", completed.stderr)

    def test_prefixed_python_option_cannot_claim_dummy_declared_code(self) -> None:
        dummy = self.root / "-u"
        dummy.write_text("dummy declared bytes\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_code"] = ["-u"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "-u", "-c", "print('bypass')", expected=2,
        )
        self.assertIn("inline/module code", completed.stderr)

    def test_shell_inline_command_cannot_claim_dummy_declared_launcher(self) -> None:
        dummy = self.root / "bash"
        dummy.write_text("dummy declared bytes\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_code"] = ["bash"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            "bash", "-c", "python3 code/analyze.py", expected=2,
        )
        self.assertIn("shell commands must execute a declared script file", completed.stderr)

    def test_env_wrapper_cannot_claim_dummy_declared_launcher(self) -> None:
        dummy = self.root / "env"
        dummy.write_text("dummy declared bytes\n", encoding="utf-8")
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["producer_code"] = ["env"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            "env", "python3", "-c", "print('bypass')", expected=2,
        )
        self.assertIn("unsupported command launcher", completed.stderr)

    def test_live_citation_cannot_be_omitted_from_pass_inventory(self) -> None:
        self.add_paper_audit(citation=True)
        citation = self.root / "output/evidence/citations.json"
        value = json.loads(citation.read_text(encoding="utf-8"))
        value["citation_claims"] = []
        value["fresh_checks"] = 0
        citation.write_text(json.dumps(value) + "\n", encoding="utf-8")
        completed = self.bind_paper(expected=2)
        self.assertIn("omitted occurrences", completed.stderr)

    def test_citation_claim_text_and_pointer_are_mechanically_checked(self) -> None:
        self.add_paper_audit(citation=True)
        citation = self.root / "output/evidence/citations.json"
        value = json.loads(citation.read_text())
        value["citation_claims"][0]["claim_text"] = "Different claim."
        citation.write_text(json.dumps(value) + "\n")
        completed = self.bind_paper(expected=2)
        self.assertIn("claim_text does not match", completed.stderr)

        value["citation_claims"][0]["claim_text"] = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text()
        )["citation_occurrences"][0]["claim_text"]
        value["citation_claims"][0]["sources"][0]["pointer"] = "p. 1"
        citation.write_text(json.dumps(value) + "\n")
        completed = self.bind_paper(expected=2)
        self.assertIn("exact URL, DOI, or OpenAlex", completed.stderr)

    def test_unbound_citation_reuse_is_rejected(self) -> None:
        self.add_paper_audit(citation=True)
        citation = self.root / "output/evidence/citations.json"
        value = json.loads(citation.read_text())
        value["citation_claims"][0]["verification"] = "reused"
        value["fresh_checks"] = 0
        value["reused_bound_checks"] = 1
        citation.write_text(json.dumps(value) + "\n")
        completed = self.bind_paper(expected=2)
        self.assertIn("verification must be fresh", completed.stderr)

    def test_unchanged_citation_still_requires_fresh_verification(self) -> None:
        self.add_paper_audit(citation=True)
        self.bind_paper()
        prepared = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input_second.json",
            "--checkpoint", "stage5-second",
        )
        digest = json.loads(prepared.stdout)["digest"]
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input_second.json").read_text()
        )
        for stem in ("audit_second", "citations_second"):
            (self.root / f"output/evidence/{stem}.md").write_text(
                f"VERDICT: PASS\nCHECKPOINT: stage5-second\n"
                f"AUDIT_INPUT_DIGEST: {digest}\n\n# PASS\n"
            )
        evidence = {
            "verdict": "PASS", "checkpoint": "stage5-second", "blocking_findings": [],
            "audit_input_path": "output/evidence/audit_input_second.json",
            "audit_input_digest": digest,
            "mechanical_command": (
                "python3 code/utils/results_pipeline/results_pipeline.py verify-all --rerender"
            ),
            "result_receipts_checked": [], "result_bearing_exhibits_checked": [],
            "expository_exemptions": [], "exceptional_direct_results": [],
        }
        (self.root / "output/evidence/audit_second.json").write_text(
            json.dumps(evidence) + "\n"
        )
        prior_claim = json.loads(
            (self.root / "output/evidence/citations.json").read_text()
        )["citation_claims"][0]
        claim = dict(prior_claim)
        claim["occurrence_id"] = audit_input["citation_occurrences"][0]["occurrence_id"]
        claim["anchor"] = claim["occurrence_id"]
        claim["verification"] = "reused"
        citation = {
            "verdict": "PASS", "checkpoint": "stage5-second", "blocking_findings": [],
            "audit_input_path": "output/evidence/audit_input_second.json",
            "audit_input_digest": digest, "citation_claims": [claim],
            "fresh_checks": 0, "reused_bound_checks": 1,
        }
        (self.root / "output/evidence/citations_second.json").write_text(
            json.dumps(citation) + "\n"
        )
        completed = self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input_second.json",
            "--summary", "output/evidence/audit_second.json",
            "--report", "output/evidence/audit_second.md",
            "--citation-summary", "output/evidence/citations_second.json",
            "--citation-report", "output/evidence/citations_second.md",
            "--receipt", "process_log/paper_evidence.receipt.json",
            "--checkpoint", "stage5-second",
            expected=2,
        )
        self.assertIn("verification must be fresh", completed.stderr)

    def test_conflicting_markdown_body_verdict_is_rejected(self) -> None:
        self.add_paper_audit()
        digest = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )["digest"]
        (self.root / "output/evidence/audit.md").write_text(
            f"VERDICT: PASS\nCHECKPOINT: stage5-initial\nAUDIT_INPUT_DIGEST: {digest}"
            "\n\n## Verdict\nREVISE\n",
            encoding="utf-8",
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("conflicting verdict", completed.stderr)

    def test_mixed_case_conflicting_audit_markers_are_rejected(self) -> None:
        self.add_paper_audit()
        forms = (
            "Verdict: REVISE",
            "**Verdict:** REVISE",
            "- Verdict: REVISE",
            "- [x] Verdict: REVISE",
            "> Verdict: REVISE",
            "| Verdict | REVISE |\n|---|---|",
            "| Verdict | REVISE | rationale |\n|---|---|---|",
            "Verdict | REVISE\n---|---",
            "| Check | Verdict | Rationale |\n|---|---|---|\n| evidence | REVISE | stale |",
            "| Field | Value |\n|---|---|\n| Verdict | REVISE |",
            "| Verdict |\n|---|\n| REVISE |",
            "- [x] | Verdict |\n  |---|\n  | REVISE |",
            "## Verdict ##\nREVISE",
            "> ### **Verdict** ###\n> REVISE",
            "## Audit  Input  Digest\nwrong",
            "Audit\tInput\tDigest: wrong",
            "| Audit  Input  Digest | wrong |\n|---|---|",
            "Intro | note\n| Check | Verdict |\n|---|---|\n| evidence | REVISE |",
        )
        for relative in ("output/evidence/audit.md", "output/evidence/citations.md"):
            report = self.root / relative
            original = report.read_text(encoding="utf-8")
            for marker in forms:
                with self.subTest(report=relative, marker=marker):
                    report.write_text(original + f"\n{marker}\n", encoding="utf-8")
                    completed = self.bind_paper(expected=2)
                    self.assertTrue(
                        "consistent PASS/checkpoint/digest" in completed.stderr
                        or "conflicting " in completed.stderr,
                        completed.stderr,
                    )
            report.write_text(original, encoding="utf-8")

    def test_markdown_verdict_heading_accepts_case_insensitive_pass(self) -> None:
        self.add_paper_audit()
        for relative in ("output/evidence/audit.md", "output/evidence/citations.md"):
            report = self.root / relative
            report.write_text(
                report.read_text(encoding="utf-8") + "\n## Verdict\nPass\n",
                encoding="utf-8",
            )
        self.bind_paper()

    def test_nested_markdown_verdict_heading_is_rejected(self) -> None:
        self.add_paper_audit()
        report = self.root / "output/evidence/audit.md"
        report.write_text(
            report.read_text(encoding="utf-8") + "\n- ## Verdict\n  - REVISE\n",
            encoding="utf-8",
        )
        completed = self.bind_paper(expected=2)
        self.assertIn("conflicting verdict", completed.stderr)

    def test_transitive_asset_outside_standard_figure_directories_is_bound(self) -> None:
        (self.root / "paper/assets").mkdir(parents=True)
        (self.root / "paper/assets/chart.png").write_bytes(b"png-v1")
        self.add_paper_audit(asset=True)
        self.bind_paper()
        (self.root / "paper/assets/chart.png").write_bytes(b"png-v2")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("paper/assets/chart.png", completed.stdout)

    def test_read_only_paper_verification_creates_no_lock(self) -> None:
        self.add_paper_audit()
        self.bind_paper()
        lock = self.root / "process_log/results_pipeline.lock"
        lock.unlink()
        self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            "--read-only",
        )
        self.assertFalse(lock.exists())
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            "--read-only", "--rerender", expected=2,
        )
        self.assertIn("cannot be combined", completed.stderr)

    def test_read_only_receipt_validation_creates_no_lock(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        lock = self.root / "process_log/results_pipeline.lock"
        lock.unlink()
        self.call(
            "validate-receipt", "--receipt", "output/stagex/results.receipt.json",
            "--read-only",
        )
        self.assertFalse(lock.exists())

    def test_read_only_receipt_validation_does_not_require_historical_input(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        (self.root / "data/input.txt").unlink()
        self.call(
            "validate-receipt", "--receipt", "output/stagex/results.receipt.json",
            "--read-only",
        )

    def test_malformed_snapshot_entries_fail_without_traceback(self) -> None:
        self.add_paper_audit()
        audit_path = self.root / "output/evidence/audit_input.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        valid_audit = json.loads(json.dumps(audit))
        audit["paper_sources"] = ["not-a-fingerprint"]
        unsigned = {key: value for key, value in audit.items() if key != "digest"}
        encoded = json.dumps(
            unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        audit["digest"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
        audit_path.write_text(json.dumps(audit) + "\n", encoding="utf-8")
        completed = self.call(
            "verify-audit-input", "--input", "output/evidence/audit_input.json",
            "--checkpoint", "stage5-initial", expected=2,
        )
        self.assertIn("not a fingerprint object", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

        audit_path.write_text(json.dumps(valid_audit) + "\n", encoding="utf-8")
        self.bind_paper()
        receipt_path = self.root / "process_log/paper_evidence.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["paper_sources"] = ["not-a-fingerprint"]
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("not a fingerprint object", completed.stdout)
        self.assertNotIn("Traceback", completed.stderr)

    def test_non_string_enum_values_fail_without_traceback(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["reproducibility"] = []
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("reproducibility", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_duplicate_json_keys_fail_closed(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        text = plan_path.read_text(encoding="utf-8")
        plan_path.write_text(
            text.replace('"plan_version": 1',
                         '"plan_version": 1, "plan_version": 1', 1),
            encoding="utf-8",
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("duplicate JSON object key", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_duplicate_audit_summary_keys_fail_closed(self) -> None:
        self.add_paper_audit()
        summary = self.root / "output/evidence/audit.json"
        text = summary.read_text(encoding="utf-8")
        summary.write_text(
            text.replace('"verdict": "PASS"',
                         '"verdict": "PASS", "verdict": "PASS"', 1),
            encoding="utf-8",
        )
        completed = self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input.json",
            "--summary", "output/evidence/audit.json",
            "--report", "output/evidence/audit.md",
            "--citation-summary", "output/evidence/citations.json",
            "--citation-report", "output/evidence/citations.md",
            "--receipt", "process_log/paper_evidence.receipt.json",
            "--checkpoint", "stage5-initial", expected=2,
        )
        self.assertIn("duplicate JSON object key", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_paper_receipt_cannot_overwrite_paper_source(self) -> None:
        self.add_paper_audit()
        completed = self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input.json",
            "--summary", "output/evidence/audit.json",
            "--report", "output/evidence/audit.md",
            "--citation-summary", "output/evidence/citations.json",
            "--citation-report", "output/evidence/citations.md",
            "--receipt", "paper/main.tex", "--checkpoint", "stage5-initial",
            expected=2,
        )
        self.assertIn("must be exactly", completed.stderr)
        self.assertEqual((self.root / "paper/main.tex").read_text(encoding="utf-8"),
                         "\\input{sections/results}\n")

    def test_empty_retirement_reason_is_rejected_without_registry_mutation(self) -> None:
        self.record_and_render()
        registry = self.root / "process_log/results_registry.json"
        before = registry.read_bytes()
        completed = self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "   ", expected=2,
        )
        self.assertIn("reason must be non-empty", completed.stderr)
        self.assertEqual(registry.read_bytes(), before)

    def test_retired_attempt_namespace_cannot_be_reused(self) -> None:
        self.record_and_render()
        self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "obsolete attempt",
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/new_results.json",
            "--receipt", "output/stagex/new_results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("reuse a pending/retired attempt namespace", completed.stderr)

    def test_retired_unrendered_attempt_keeps_planned_exhibit_namespace(self) -> None:
        self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py",
        )
        self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "failed before rendering",
        )
        source = self.analyze_source.replace(
            "'code/analyze.py'", "'code/analyze_v2.py'"
        ).replace(
            "output/stagex/detail.json", "output/stagex/v2/detail.json"
        )
        (self.root / "code/analyze_v2.py").write_text(source, encoding="utf-8")
        self.write_plan(
            "output/stagex/v2/results.plan.json", prefix="output/stagex/v2/",
            analyze="code/analyze_v2.py",
        )
        plan_path = self.root / "output/stagex/v2/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["exhibits"] = ["output/stagex/tables/main.tex"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/analyze_v2.py", expected=2,
        )
        self.assertIn("reuse a pending/retired attempt namespace", completed.stderr)

    def test_tampered_retired_receipt_cannot_release_historical_namespace(self) -> None:
        self.record_and_render()
        self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "obsolete attempt",
        )
        receipt_path = self.root / "output/stagex/results.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["producer_run"]["artifacts"] = []
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        registry_path = self.root / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["retired"][0]["last_fingerprint"]["sha256"] = (
            "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        )
        registry_path.write_text(json.dumps(registry) + "\n", encoding="utf-8")
        (self.root / "output/stagex/detail.json").unlink()
        self.write_plan("output/stagex/v2/results.plan.json", prefix="output/stagex/v2/")
        plan_path = self.root / "output/stagex/v2/results.plan.json"
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["artifacts"] = ["output/stagex/detail.json"]
        plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("producer_run.artifacts inventory differs from the plan",
                      completed.stderr)

    def test_boolean_schema_version_is_rejected(self) -> None:
        script = self.root / "code/analyze.py"
        script.write_text(self.analyze_source.replace("'schema_version': 1",
                                                      "'schema_version': True"),
                          encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("unsupported result schema_version", completed.stderr)

    def test_result_owned_paths_cannot_use_reserved_audit_namespace(self) -> None:
        (self.root / "output/evidence").mkdir()
        cases = {
            "plan": ("output/evidence/results.plan.json",
                     "output/stagex/results.json",
                     "output/stagex/results.receipt.json"),
            "bundle": ("output/stagex/results.plan.json",
                       "output/evidence/results.json",
                       "output/stagex/results.receipt.json"),
            "receipt": ("output/stagex/results.plan.json",
                        "output/stagex/results.json",
                        "output/evidence/results.receipt.json"),
        }
        original_plan = self.root / "output/stagex/results.plan.json"
        original_plan_value = json.loads(original_plan.read_text(encoding="utf-8"))
        (self.root / "output/evidence/results.plan.json").write_bytes(
            original_plan.read_bytes()
        )
        for label, (plan, bundle, receipt) in cases.items():
            with self.subTest(label=label):
                completed = self.call(
                    "run", "--plan", plan, "--bundle", bundle,
                    "--receipt", receipt, "--", sys.executable,
                    "code/analyze.py", expected=2,
                )
                self.assertIn("reserved audit namespace", completed.stderr)

        for key in ("artifacts", "exhibits"):
            with self.subTest(label=key):
                plan = json.loads(json.dumps(original_plan_value))
                plan[key] = [f"output/evidence/{key}.json"]
                original_plan.write_text(json.dumps(plan) + "\n", encoding="utf-8")
                completed = self.call(
                    "run", "--plan", "output/stagex/results.plan.json",
                    "--bundle", "output/stagex/results.json",
                    "--receipt", "output/stagex/results.receipt.json", "--",
                    sys.executable, "code/analyze.py", expected=2,
                )
                self.assertIn("reserved audit namespace", completed.stderr)

    def test_prepare_audit_cannot_overwrite_legacy_result_evidence(self) -> None:
        self.record_and_render()
        evidence = self.root / "output/evidence"
        evidence.mkdir()
        collision = evidence / "collision.json"
        shutil.copy2(self.root / "output/stagex/detail.json", collision)
        receipt_path = self.root / "output/stagex/results.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["producer_run"]["artifacts"][0]["path"] = (
            "output/evidence/collision.json"
        )
        receipt_path.write_text(json.dumps(receipt) + "\n", encoding="utf-8")
        registry_path = self.root / "process_log/results_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["receipt_fingerprints"]["output/stagex/results.receipt.json"] = {
            "path": "output/stagex/results.receipt.json",
            "kind": "file",
            "sha256": "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        }
        registry_path.write_text(json.dumps(registry) + "\n", encoding="utf-8")
        before = collision.read_bytes()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/collision.json",
            "--checkpoint", "collision-regression", expected=2,
        )
        self.assertIn("producer_run.artifacts inventory differs from the plan",
                      completed.stderr)
        self.assertEqual(collision.read_bytes(), before)

    def test_prepare_audit_requires_json_output_suffix(self) -> None:
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.md",
            "--checkpoint", "suffix-regression", expected=2,
        )
        self.assertIn("must end with .json", completed.stderr)

    def test_fresh_plan_cannot_reuse_active_evidence_path(self) -> None:
        active_input = self.root / "data/input.txt"
        active_input.write_text(json.dumps({
            "plan_version": 1,
            "producer_code": ["code/analyze.py"],
            "producer_inputs": [],
            "artifacts": ["output/stagex/v2/detail.json"],
            "renderer_code": ["code/render.py"],
            "exhibits": ["output/stagex/v2/tables/main.tex"],
        }) + "\n", encoding="utf-8")
        self.record_and_render()
        completed = self.call(
            "run", "--plan", "data/input.txt",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("new run would overwrite active evidence", completed.stderr)
        self.assertIn("data/input.txt", completed.stderr)

    def test_fractional_run_plan_version_is_rejected(self) -> None:
        plan = self.root / "output/stagex/results.plan.json"
        value = json.loads(plan.read_text(encoding="utf-8"))
        value["plan_version"] = 1.0
        plan.write_text(json.dumps(value) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("unsupported run plan version", completed.stderr)

    def test_run_plan_requires_renderer_when_exhibits_are_declared(self) -> None:
        plan = self.root / "output/stagex/results.plan.json"
        value = json.loads(plan.read_text(encoding="utf-8"))
        value["renderer_code"] = []
        plan.write_text(json.dumps(value) + "\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("renderer_code must be non-empty", completed.stderr)

    def test_run_outputs_must_stay_under_output(self) -> None:
        plan_path = self.root / "output/stagex/results.plan.json"
        original = json.loads(plan_path.read_text(encoding="utf-8"))
        for field, value in (("artifacts", ["data/generated.json"]),
                             ("exhibits", ["paper/generated.tex"])):
            with self.subTest(field=field):
                plan = dict(original)
                plan[field] = value
                plan_path.write_text(json.dumps(plan) + "\n", encoding="utf-8")
                completed = self.call(
                    "run", "--bundle", "output/stagex/results.json",
                    "--receipt", "output/stagex/results.receipt.json", "--",
                    sys.executable, "code/analyze.py", expected=2,
                )
                self.assertIn("must be under output/", completed.stderr)

    def test_pending_receipt_blocks_audit_and_failed_render_preserves_old_active(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/v2/tables").mkdir(parents=True)
        analyze_v2 = self.analyze_source.replace(
            "output/stagex/", "output/stagex/v2/"
        ).replace("code/analyze.py", "code/analyze_v2.py").replace(
            "code/render.py", "code/render_v2.py"
        )
        (self.root / "code/analyze_v2.py").write_text(analyze_v2, encoding="utf-8")
        (self.root / "code/render_v2.py").write_text("pass\n", encoding="utf-8")
        self.write_plan("output/stagex/v2/results.plan.json", prefix="output/stagex/v2/",
                        analyze="code/analyze_v2.py", render="code/render_v2.py")
        self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json",
            "--supersedes", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze_v2.py",
        )
        completed = self.call("verify-all", expected=2)
        self.assertIn("pending result receipts", completed.stderr)
        completed = self.call(
            "render", "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/render_v2.py", expected=2,
        )
        self.assertIn("did not freshly stage", completed.stderr)
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["active"], ["output/stagex/results.receipt.json"])

    def test_invalid_supersession_fails_before_analysis_mutates_active_bytes(self) -> None:
        self.record_and_render()
        receipt = self.root / "output/stagex/results.receipt.json"
        bundle = self.root / "output/stagex/results.json"
        before = (receipt.read_bytes(), bundle.read_bytes())
        completed = self.call(
            "run", "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json",
            "--supersedes", "output/missing/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("superseded receipt is not active", completed.stderr)
        self.assertEqual((receipt.read_bytes(), bundle.read_bytes()), before)

    def test_bind_validates_reports_after_renderer_execution(self) -> None:
        self.record_and_render()
        self.add_paper_audit()
        trigger = self.root / "output/test-render-triggers/mutate-during-bind"
        trigger.parent.mkdir(parents=True, exist_ok=True)
        trigger.write_text("trigger\n")
        before = (self.root / "output/evidence/audit.md").read_bytes()
        self.bind_paper()
        self.assertEqual((self.root / "output/evidence/audit.md").read_bytes(), before)

    def test_explicit_retirement_removes_receipt_from_active_inventory(self) -> None:
        self.record_and_render()
        self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "superseded experiment",
        )
        report = self.call("verify-all")
        self.assertEqual(json.loads(report.stdout)["receipts"], [])

    def test_retired_receipt_history_cannot_be_deleted(self) -> None:
        self.record_and_render()
        self.call("retire", "--receipt", "output/stagex/results.receipt.json",
                  "--reason", "withdrawn")
        (self.root / "output/stagex/results.receipt.json").unlink()
        completed = self.call("verify-all", expected=2)
        self.assertIn("retired result receipt is unavailable", completed.stderr)

    def test_new_run_can_explicitly_supersede_an_active_receipt(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/v2/tables").mkdir(parents=True)
        analyze_v2 = self.analyze_source.replace(
            "output/stagex/", "output/stagex/v2/"
        ).replace("code/analyze.py", "code/analyze_v2.py").replace(
            "code/render.py", "code/render_v2.py"
        )
        (self.root / "code/analyze_v2.py").write_text(analyze_v2, encoding="utf-8")
        render_v2 = (self.root / "code/render.py").read_text(encoding="utf-8").replace(
            "output/stagex/tables/main.tex", "output/stagex/v2/tables/main.tex"
        )
        (self.root / "code/render_v2.py").write_text(render_v2, encoding="utf-8")
        self.write_plan("output/stagex/v2/results.plan.json", prefix="output/stagex/v2/",
                        analyze="code/analyze_v2.py", render="code/render_v2.py")
        self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json",
            "--supersedes", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze_v2.py",
        )
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["active"], ["output/stagex/results.receipt.json"])
        self.assertEqual(registry["pending"][0]["receipt"],
                         "output/stagex/v2/results.receipt.json")
        self.call(
            "render", "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/render_v2.py",
        )
        self.call("activate", "--receipt", "output/stagex/v2/results.receipt.json")
        replacement_receipt = json.loads(
            (self.root / "output/stagex/v2/results.receipt.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            replacement_receipt["supersedes"],
            ["output/stagex/results.receipt.json"],
        )
        incomplete = self.call("verify-all", expected=2)
        self.assertIn("activated replacement handoff is incomplete", incomplete.stderr)
        self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "superseded by output/stagex/v2/results.receipt.json",
            "--superseded-by", "output/stagex/v2/results.receipt.json",
        )
        registry = json.loads(
            (self.root / "process_log/results_registry.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["active"], ["output/stagex/v2/results.receipt.json"])
        self.assertEqual(registry["retired"][0]["receipt"],
                         "output/stagex/results.receipt.json")
        self.assertEqual(registry["retired"][0]["superseded_by"],
                         "output/stagex/v2/results.receipt.json")

    def test_retire_rejects_active_predecessor_of_pending_replacement(self) -> None:
        self.record_and_render()
        (self.root / "output/stagex/v2/tables").mkdir(parents=True)
        analyze_v2 = self.analyze_source.replace(
            "output/stagex/", "output/stagex/v2/"
        ).replace("code/analyze.py", "code/analyze_v2.py").replace(
            "code/render.py", "code/render_v2.py"
        )
        (self.root / "code/analyze_v2.py").write_text(analyze_v2, encoding="utf-8")
        (self.root / "code/render_v2.py").write_text(
            (self.root / "code/render.py").read_text(encoding="utf-8").replace(
                "output/stagex/tables/main.tex", "output/stagex/v2/tables/main.tex"
            ),
            encoding="utf-8",
        )
        self.write_plan(
            "output/stagex/v2/results.plan.json", prefix="output/stagex/v2/",
            analyze="code/analyze_v2.py", render="code/render_v2.py",
        )
        self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json",
            "--supersedes", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze_v2.py",
        )
        registry = self.root / "process_log/results_registry.json"
        before = registry.read_bytes()
        completed = self.call(
            "retire", "--receipt", "output/stagex/results.receipt.json",
            "--reason", "premature", expected=2,
        )
        self.assertIn("pending replacement", completed.stderr)
        self.assertEqual(registry.read_bytes(), before)
        self.call(
            "render", "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/render_v2.py",
        )
        self.call("activate", "--receipt", "output/stagex/v2/results.receipt.json")

    def test_noop_analysis_and_renderer_cannot_reuse_old_outputs(self) -> None:
        self.record_and_render()
        (self.root / "code/analyze.py").write_text("pass\n", encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/noop/results.json",
            "--receipt", "output/stagex/noop/results.receipt.json",
            "--supersedes", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("overwrite active evidence", completed.stderr)

        # Restore the active producer code. An undeclared project-side trigger is
        # invisible inside the renderer workspace, so the recorded render repeats.
        (self.root / "code/analyze.py").write_text(self.analyze_source, encoding="utf-8")
        trigger = self.root / "output/test-render-triggers/noop"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("trigger\n", encoding="utf-8")
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "RERENDERED")

    def test_failed_rerender_keeps_prior_exhibit_bytes(self) -> None:
        self.record_and_render()
        exhibit = self.root / "output/stagex/tables/main.tex"
        before = exhibit.read_bytes()
        trigger = self.root / "output/test-render-triggers/noop"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("trigger\n", encoding="utf-8")
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "RERENDERED")
        self.assertEqual(exhibit.read_bytes(), before)

    def test_failed_renderer_os_replace_restores_inputs_and_prior_exhibit(self) -> None:
        self.record_and_render()
        exhibit = self.root / "output/stagex/tables/main.tex"
        input_path = self.root / "data/input.txt"
        before_exhibit = exhibit.read_bytes()
        before_input = input_path.read_bytes()
        receipt = self.root / "output/stagex/results.receipt.json"
        registry = self.root / "process_log/results_registry.json"
        before_receipt = receipt.read_bytes()
        before_registry = registry.read_bytes()
        trigger = self.root / "output/test-render-triggers/corrupt-fail"
        trigger.parent.mkdir(parents=True)
        trigger.write_text("trigger\n", encoding="utf-8")
        completed = self.call(
            "render", "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/render.py",
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "RERENDERED")
        self.assertEqual(input_path.read_bytes(), before_input)
        self.assertEqual(exhibit.read_bytes(), before_exhibit)
        self.assertEqual(receipt.read_bytes(), before_receipt)
        self.assertEqual(registry.read_bytes(), before_registry)

    def test_new_output_cannot_target_active_input_directory_outside_output(self) -> None:
        plan = json.loads((self.root / "output/stagex/results.plan.json").read_text())
        plan["producer_inputs"] = ["data"]
        (self.root / "output/stagex/results.plan.json").write_text(json.dumps(plan) + "\n")
        (self.root / "code/analyze.py").write_text(
            self.analyze_source.replace("['data/input.txt']", "['data']"), encoding="utf-8"
        )
        self.record_and_render()
        (self.root / "output/stagex/v2").mkdir()
        (self.root / "code/analyze_v2.py").write_text(
            "from pathlib import Path\nPath('data/input.txt').write_text('ran\\n')\n"
        )
        (self.root / "output/stagex/v2/results.plan.json").write_text(json.dumps({
            "plan_version": 1, "producer_code": ["code/analyze_v2.py"],
            "producer_inputs": [], "artifacts": ["data/generated.json"],
            "renderer_code": [], "exhibits": []}) + "\n")
        completed = self.call(
            "run", "--plan", "output/stagex/v2/results.plan.json",
            "--bundle", "output/stagex/v2/results.json",
            "--receipt", "output/stagex/v2/results.receipt.json", "--",
            sys.executable, "code/analyze_v2.py", expected=2,
        )
        self.assertIn("run plan.artifacts paths must be under output/", completed.stderr)
        self.assertEqual((self.root / "data/input.txt").read_text(), "input-v1\n")

    def test_latex_listing_dependency_is_bound(self) -> None:
        (self.root / "data/latex_rows.csv").write_text("x,y\n1,2\n")
        self.add_paper_audit(listing=True)
        self.bind_paper()
        (self.root / "data/latex_rows.csv").write_text("x,y\n3,4\n")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("data/latex_rows.csv", completed.stdout)

    def test_latex_addplot_plus_dependency_is_bound(self) -> None:
        plot = self.root / "data/plot.csv"
        plot.write_text("x,y\n1,2\n")
        self.add_paper_audit(addplot=True)
        self.bind_paper()
        plot.write_text("x,y\n1,3\n")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("data/plot.csv", completed.stdout)

    def test_latex_dependencies_allow_whitespace_before_options(self) -> None:
        assets = self.root / "paper/assets"
        assets.mkdir(parents=True)
        files = {
            "localclass.cls": "\\NeedsTeXFormat{LaTeX2e}\n",
            "localstyle.sty": "\\NeedsTeXFormat{LaTeX2e}\n",
            "refs.bib": "@misc{x, title={X}}\n",
            "assets/chart.png": "png",
            "assets/code.py": "print(1)\n",
            "assets/minted.py": "print(2)\n",
            "assets/rows.csv": "x\n1\n",
            "assets/pages.pdf": "%PDF-1.4\n",
        }
        for raw, content in files.items():
            (self.root / "paper" / raw).write_text(content, encoding="utf-8")
        (self.root / "paper/main.tex").write_text(
            "\\documentclass [10pt] {localclass}\n"
            "\\usepackage [x] {localstyle}\n"
            "\\addbibresource [datatype=bibtex] {refs.bib}\n"
            "\\includegraphics [width=1cm] {assets/chart.png}\n"
            "\\lstinputlisting [language=Python] {assets/code.py}\n"
            "\\inputminted [linenos] {python} {assets/minted.py}\n"
            "\\csvreader [head to column names] {assets/rows.csv}{}{}\n"
            "\\includepdf [pages=1] {assets/pages.pdf}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "whitespace",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        bound = {entry["path"] for entry in value["paper_sources"]}
        self.assertTrue({f"paper/{raw}" for raw in files}.issubset(bound))

    def test_latex_dependencies_parse_balanced_optional_arguments(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "data/code.py").write_text("print(1)\n", encoding="utf-8")
        (self.root / "paper/main.tex").write_text(
            "\\lstinputlisting[caption={Results [baseline]}]{../data/code.py}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "balanced-options",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            "data/code.py", {entry["path"] for entry in value["paper_sources"]}
        )

    def test_external_listing_escape_options_fail_closed_after_balanced_parse(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "data/code.py").write_text(
            "(*@\\input{secret.tex}@*)\n", encoding="utf-8"
        )
        (self.root / "paper/secret.tex").write_text("secret\n", encoding="utf-8")
        (self.root / "paper/main.tex").write_text(
            "\\lstinputlisting[escapeinside={(*@}{@*)}]{../data/code.py}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "external-listing-escape", expected=2,
        )
        self.assertIn("escape-enabled external literal input", completed.stderr)

    @unittest.skipUnless(shutil.which("pdflatex"), "pdflatex recorder check")
    def test_suffix_appending_latex_command_binds_the_file_tex_opens(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "graphic-source.tex").write_text(
            "\\documentclass{article}\\begin{document}graphic\\end{document}\n",
            encoding="utf-8",
        )
        made_graphic = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-jobname=graphic", "graphic-source.tex"],
            cwd=paper, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        self.assertEqual(made_graphic.returncode, 0, made_graphic.stdout)
        (paper / "graphic").write_text("not the graphic TeX opens\n", encoding="utf-8")
        (paper / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\usepackage{graphicx}\n"
            "\\begin{document}\\includegraphics{graphic}\\end{document}\n",
            encoding="utf-8",
        )
        compiled = subprocess.run(
            ["pdflatex", "-recorder", "-interaction=nonstopmode", "-halt-on-error",
             "main.tex"], cwd=paper, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        self.assertEqual(compiled.returncode, 0, compiled.stdout)
        recorder = (paper / "main.fls").read_text(encoding="utf-8", errors="replace")
        self.assertRegex(recorder, r"(?m)^INPUT (?:\./)?graphic\.pdf$")
        self.assertRegex(recorder, r"(?m)^INPUT (?:\./)?graphic$")
        (self.root / "output/evidence").mkdir()
        rejected = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "suffix-resolution", expected=2,
        )
        self.assertIn("ambiguous extensionless and suffixed LaTeX dependency",
                      rejected.stderr)
        (paper / "graphic").unlink()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "suffix-resolution",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        bound = {entry["path"] for entry in value["paper_sources"]}
        self.assertIn("paper/graphic.pdf", bound)
        self.assertNotIn("paper/graphic", bound)

    def test_suffix_appending_dependency_classes_never_prefer_raw_collision(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        paper = self.root / "paper"
        paper.mkdir()
        current = paper / "main.tex"
        current.write_text("", encoding="utf-8")
        for stem, extension in (
            ("local-package", ".sty"), ("local-class", ".cls"),
            ("references", ".bib"), ("bibliography-style", ".bst"),
            ("appendix-pages", ".pdf"), ("figure", ".png"),
        ):
            with self.subTest(extension=extension):
                suffixed = paper / f"{stem}{extension}"
                suffixed.write_text("bound\n", encoding="utf-8")
                resolved = module.resolve_latex_dependency(
                    self.root, paper, current, stem, (extension,), required=True,
                    append_extension=True,
                )
                self.assertEqual(resolved, suffixed)
                raw = paper / stem
                raw.write_text("collision\n", encoding="utf-8")
                with self.assertRaises(module.EvidenceError):
                    module.resolve_latex_dependency(
                        self.root, paper, current, stem, (extension,), required=True,
                        append_extension=True,
                    )
                raw.unlink()

    def test_local_package_bibliography_and_conditional_input_are_transitive(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\documentclass{article}\n\\usepackage{localstyle}\n",
            encoding="utf-8",
        )
        (paper / "localstyle.sty").write_text(
            "\\addbibresource{style-refs.bib}\n"
            "\\InputIfFileExists{hidden.tex}{}{}\n",
            encoding="utf-8",
        )
        (paper / "style-refs.bib").write_text("@misc{x,title={X}}\n", encoding="utf-8")
        (paper / "hidden.tex").write_text("hidden source\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "local-package-transitive",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        bound = {entry["path"] for entry in value["paper_sources"]}
        self.assertTrue({
            "paper/main.tex", "paper/localstyle.sty",
            "paper/style-refs.bib", "paper/hidden.tex",
        }.issubset(bound))

    def test_dotted_packages_nested_classes_and_bibliography_variants_are_transitive(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\documentclass{outer}\\usepackage{foo.bar}\n", encoding="utf-8"
        )
        (paper / "outer.cls").write_text(
            "\\LoadClass{inner}\\RequirePackageWithOptions{nested}\n",
            encoding="utf-8",
        )
        (paper / "inner.cls").write_text("% inner\n", encoding="utf-8")
        (paper / "foo.bar.sty").write_text(
            "\\addglobalbib{global.bib}\\addsectionbib{section.bib}\n",
            encoding="utf-8",
        )
        (paper / "nested.sty").write_text("% nested\n", encoding="utf-8")
        (paper / "global.bib").write_text("@misc{g,title={G}}\n", encoding="utf-8")
        (paper / "section.bib").write_text("@misc{s,title={S}}\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "package-closure",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        bound = {entry["path"] for entry in value["paper_sources"]}
        self.assertTrue({
            "paper/main.tex", "paper/outer.cls", "paper/inner.cls",
            "paper/foo.bar.sty", "paper/nested.sty", "paper/global.bib",
            "paper/section.bib",
        }.issubset(bound))

    def test_local_package_and_class_nested_options_are_transitive(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\documentclass{wrapper}\\begin{document}x\\end{document}\n",
            encoding="utf-8",
        )
        (paper / "wrapper.cls").write_text(
            "\\LoadClass[config={nested[value]}]{inner}\n"
            "\\RequirePackage[config={nested[value]}]{dep}\n",
            encoding="utf-8",
        )
        (paper / "inner.cls").write_text("% inner\n", encoding="utf-8")
        (paper / "dep.sty").write_text("% dep\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "nested-local-options",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        bound = {entry["path"] for entry in value["paper_sources"]}
        self.assertTrue({"paper/inner.cls", "paper/dep.sty"}.issubset(bound))

    def test_nested_optional_default_citation_macro_fails_closed(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\newcommand{\\foo}[1][{x[y]}]{\\cite{smith}}\n"
            "\\foo \\foo\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "nested-citation-default", expected=2,
        )
        self.assertIn("user-defined citation command", completed.stderr)

    def test_local_package_dynamic_file_read_fails_closed(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\documentclass{article}\n\\usepackage{localstyle}\n",
            encoding="utf-8",
        )
        (paper / "localstyle.sty").write_text(
            "\\CatchFileDef\\payload{secret.txt}{}\n", encoding="utf-8"
        )
        (paper / "secret.txt").write_text("reader-affecting bytes\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "local-package-dynamic", expected=2,
        )
        self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_local_package_additional_dynamic_readers_fail_closed(self) -> None:
        paper = self.root / "paper"
        paper.mkdir()
        (paper / "main.tex").write_text(
            "\\documentclass{article}\n\\usepackage{localstyle}\n",
            encoding="utf-8",
        )
        (paper / "secret.txt").write_text("reader-affecting bytes\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        for source in (
            "\\CatchFileEdef\\payload{secret.txt}{}\n",
            "\\newread\\payload\\openin\\payload=secret.txt\n",
        ):
            with self.subTest(source=source):
                (paper / "localstyle.sty").write_text(source, encoding="utf-8")
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "local-package-dynamic", expected=2,
                )
                self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_plural_citation_inventory_includes_every_brace_group(self) -> None:
        self.add_paper_audit(plural_citation=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(audit_input["citation_occurrences"]), 1)
        self.assertEqual(audit_input["citation_occurrences"][0]["cite_keys"], ["one", "two"])

    def test_advanced_biblatex_citation_inventory_is_complete(self) -> None:
        self.add_paper_audit(advanced_citations=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in audit_input["citation_occurrences"]],
            [["one", "two"], ["three"], ["four"]],
        )

    def test_natbib_citation_inventory_is_complete(self) -> None:
        self.add_paper_audit(natbib_citations=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in audit_input["citation_occurrences"]],
            [["five"], ["six"]],
        )

    def test_additional_biblatex_and_natbib_citations_are_inventoried(self) -> None:
        self.add_paper_audit(expanded_citations=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in audit_input["citation_occurrences"]],
            [["seven"], ["eight"], ["nine"], ["ten"]],
        )

    def test_csquotes_biblatex_citations_are_inventoried(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Quoted \\textcquote[see][p. 2]{smith2020}{claim}.\n"
            "Foreign \\foreignblockcquote{french}{jones2021}{long claim}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "csquotes-citations",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["smith2020"], ["jones2021"]],
        )

    def test_csquotes_options_with_braces_do_not_replace_real_key(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Quoted \\textcquote[see \\emph{discussion}]{smith2020}{claim}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "csquotes-braced-option",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["smith2020"]],
        )
        self.assertTrue(value["citation_occurrences"][0]["claim_text"].startswith("Quoted"))

    def test_csquotes_punctuation_and_language_notes_are_inventoried(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Quoted \\textcquote[see][p. 2]{smith2020}[!]{claim}.\n"
            "Foreign \\foreigntextcquote{french}[cf.][p. 3]{jones2021}[?]{texte}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "csquotes-punctuation",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["smith2020"], ["jones2021"]],
        )

    def test_citation_notes_with_braces_do_not_become_keys(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Prior \\cite[see \\emph{discussion}]{smith2020}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "citation-braced-note",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["smith2020"]],
        )

    def test_extended_standard_citation_commands_are_inventoried(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\hyphentextcquote{german}{one}{claim}.\n"
            "\\hyphenblockcquote{french}{two}{claim}.\n"
            "\\hybridblockcquote{spanish}{three}{claim}.\n"
            "\\citename{four}{author} and \\citelist{five}{publisher}.\n"
            "\\notecite{six} \\pnotecite{seven} \\fnotecite{eight}.\n"
            "\\cites(see)(and)[p. 1]{nine}[p. 2]{ten}.\n"
            "\\volcites(see)(and)[cf.]{I}[2]{eleven}{II}[3]{twelve}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "extended-standard-citations",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["one"], ["two"], ["three"], ["four"], ["five"], ["six"],
             ["seven"], ["eight"], ["nine", "ten"], ["eleven", "twelve"]],
        )

    def test_additional_standard_alias_and_plural_citations_are_inventoried(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\supercites{one}{two} \\footcitetexts{three}{four} "
            "\\citetalias{five} \\citepalias{six}.\n"
            "\\defcitealias{five}{Alias}\\citetext{printed text}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "alias-citations",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["one", "two"], ["three", "four"], ["five"], ["six"]],
        )

    def test_natbib_bibentry_binds_key_and_bibliography(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\usepackage{bibentry}\n"
            "\\nobibliography{refs}\n"
            "Prior work: \\bibentry{smith2020}.\n",
            encoding="utf-8",
        )
        (self.root / "paper/refs.bib").write_text(
            "@article{smith2020,title={Bound entry}}\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "bibentry-citation",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["smith2020"]],
        )
        self.assertIn(
            "paper/refs.bib", [item["path"] for item in value["paper_sources"]]
        )

    def test_paired_backslashes_do_not_create_false_commands(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            r"Printed \\cite{ghost} and \\input{ghost}." + "\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "paired-backslashes",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(value["citation_occurrences"], [])

    def test_literal_percent_does_not_hide_live_citation(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Printed \\verb|\\cite{printed}%| then live \\cite{livekey}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "literal-percent",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]],
            [["livekey"]],
        )

    def test_literal_percent_does_not_hide_dynamic_reader(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Printed \\verb|%| then live \\openin0=secret.txt.\n",
            encoding="utf-8",
        )
        (self.root / "paper/secret.txt").write_text("secret\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "literal-percent", expected=2,
        )
        self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_standard_inline_literals_do_not_hide_live_dependencies(self) -> None:
        for literal in (r"\url{https://example.test/a%b}",
                        r"\url{https://example.test/a\}b%20c}",
                        r"\lstinline|printed % text|",
                        r"\Verb|printed % text|",
                        r"\mintinline{tex}|printed % text|",
                        r"\mintinline{tex}{printed % text}",
                        r"\url|https://example.test/a%b|",
                        r"\path|printed % text|",
                        r"\nolinkurl!printed % text!"):
            with self.subTest(literal=literal):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(
                    literal + r" then live \openin0=secret.txt." + "\n",
                    encoding="utf-8",
                )
                (self.root / "paper/secret.txt").write_text("secret\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "inline-literal", expected=2,
                )
                self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_saved_verb_literal_does_not_hide_live_dependencies(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            r"\SaveVerb{saved}|%| then live \openin0=secret.txt." + "\n",
            encoding="utf-8",
        )
        (self.root / "paper/secret.txt").write_text("secret\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "save-verb", expected=2,
        )
        self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_escape_enabled_literal_environment_fails_closed(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\begin{lstlisting}[escapeinside={(*@}{@*)}]\n"
            "printed % text\n\\end{lstlisting}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "escaped-listing", expected=2,
        )
        self.assertIn("escape-enabled lstlisting environment", completed.stderr)

    def test_stateful_literal_configuration_fails_closed(self) -> None:
        sources = (
            r"\lstset{texcl}\begin{lstlisting}hidden\end{lstlisting}",
            r"\lstset{escapechar=|}\begin{lstlisting}|\input{hidden}|\end{lstlisting}",
            "\\lstset{escapeinside% split\n={(*@}{@*)}}\\begin{lstlisting}hidden\\end{lstlisting}",
            "\\lstset% boundary\n{escapeinside={(*@}{@*)}}\\begin{lstlisting}hidden\\end{lstlisting}",
            "\\begin{lstlisting}% boundary\n[escapeinside={(*@}{@*)}]\nhidden\n\\end{lstlisting}",
            "\\lstset{numbers=left,% } fake close\n"
            "escapeinside={(*@}{@*)}}\\begin{lstlisting}"
            "(*@\\input{hidden}@*)\\end{lstlisting}",
            "\\begin{lstlisting}[numbers=left,% ] fake close\n"
            "escapeinside={(*@}{@*)}]\n(*@\\input{hidden}@*)\n"
            "\\end{lstlisting}",
            r"\fvset{commandchars=\\\{\}}\begin{Verbatim}hidden\end{Verbatim}",
            r"\setminted{escapeinside=||}\begin{minted}{tex}hidden\end{minted}",
            r"\setminted[tex]{escapeinside=||}\begin{minted}{tex}hidden\end{minted}",
            r"\lstdefinestyle{danger}{escapeinside={(*@}{@*)}}"
            r"\begin{lstlisting}[style=danger]hidden\end{lstlisting}",
            r"\begin{lstlisting}[style=danger]hidden\end{lstlisting}",
            r"\DefineShortVerb{\|} printed |%| then live \cite{hidden}.",
            r"\lstMakeShortInline| printed |%| then live \cite{hidden}.",
            r"\Verb[commandchars=\\\{\}]|\input{hidden}|",
            r"\SaveVerb[aftersave=\cite{hidden}]{saved}|x|",
            r"\begin{lstlisting}[literate={X}{{\includegraphics{hidden}}}1]"
            r"X\end{lstlisting}",
        )
        for index, source in enumerate(sources):
            with self.subTest(source=source):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(source + "\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output",
                    f"output/evidence/stateful_{index}.json",
                    "--checkpoint", "stateful-literal", expected=2,
                )
                self.assertRegex(
                    completed.stderr,
                    r"unsupported stateful|escape-enabled|options on|SaveVerb options",
                )

    def test_delimited_url_literals_do_not_hide_live_citations(self) -> None:
        for literal in (r"\url|https://example.test/a%b|",
                        r"\url|https://example.test/a\|b%20|",
                        r"\path!printed % text!",
                        r"\path|printed \| delimiter % text|",
                        r"\nolinkurl+printed % text+"):
            with self.subTest(literal=literal):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(
                    literal + r" then live \cite{livekey}." + "\n",
                    encoding="utf-8",
                )
                (self.root / "output/evidence").mkdir(exist_ok=True)
                self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "delimited-url",
                )
                value = json.loads(
                    (self.root / "output/evidence/audit_input.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(
                    [item["cite_keys"] for item in value["citation_occurrences"]],
                    [["livekey"]],
                )

    def test_escaped_url_delimiter_does_not_hide_live_reader(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            r"\url|https://example.test/a\|b%20| then live \openin0=secret.txt." + "\n",
            encoding="utf-8",
        )
        (self.root / "paper/secret.txt").write_text("secret\n", encoding="utf-8")
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "escaped-url-delimiter", expected=2,
        )
        self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_commented_verbatim_delimiters_cannot_hide_live_content(self) -> None:
        for delimiter in (r"\begin{verbatim}", r"\end{verbatim}"):
            with self.subTest(delimiter=delimiter):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(
                    "% " + delimiter + "\n" + r"\openin0=secret.txt" + "\n",
                    encoding="utf-8",
                )
                (self.root / "paper/secret.txt").write_text("secret\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "commented-verbatim", expected=2,
                )
                self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_percent_escape_uses_backslash_parity(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "Escaped \\% keeps \\cite{kept}.\n"
            "Two slashes \\\\% comment hides \\cite{hidden}.\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "percent-parity",
        )
        value = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in value["citation_occurrences"]], [["kept"]]
        )

    def test_unknown_citation_family_command_fails_closed(self) -> None:
        (self.root / "paper/sections").mkdir(parents=True)
        (self.root / "paper/main.tex").write_text(
            "\\input{sections/results}\n", encoding="utf-8"
        )
        (self.root / "paper/sections/results.tex").write_text(
            "Unsupported \\customcite{key}.\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "stage5-initial", expected=2,
        )
        self.assertIn("unsupported citation-family command", completed.stderr)

    def test_mixed_case_unknown_citation_families_fail_closed(self) -> None:
        for command in (r"\customCite{x}", r"\noteCQuote{x}{claim}"):
            with self.subTest(command=command):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(command + "\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "mixed-case-citation-family", expected=2,
                )
                self.assertIn("unsupported citation", completed.stderr)

    def test_standard_display_cquote_environments_are_inventoried(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\begin{displaycquote}[see][p.~2]{plainkey}[!] Plain.\\end{displaycquote}\n\n"
            "\\begin{foreigndisplaycquote}{french}[cf.][]{foreignkey} Foreign."
            "\\end{foreigndisplaycquote}\n\n"
            "\\begin{hyphendisplaycquote}{english}{hyphenkey} Hyphen."
            "\\end{hyphendisplaycquote}\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "display-cquotes",
        )
        audit = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [item["cite_keys"] for item in audit["citation_occurrences"]],
            [["plainkey"], ["foreignkey"], ["hyphenkey"]],
        )

    def test_user_defined_citation_aliases_fail_closed(self) -> None:
        sources = (
            r"\newcommand{\smithref}{\cite{smith2020}} Two \smithref uses.",
            r"\def\basecite#1{\cite{#1}}\let\aliascite=\basecite",
            r"\DeclareCiteCommand{\localref}{}{}{}{}",
            r"\newcommand{\oldref}{\cite{x}}\renewcommand{\oldref}{safe}",
            r"\newcommand{\Foo}{\cite{x}}\newcommand{\foo}{safe}",
            r"\NewDocumentCommand{\xparseRef}{m}{\cite{#1}}",
            r"\RenewDocumentCommand\xparseRef{m}{\cite{#1}}",
            r"\ProvideDocumentCommand{\xparseRef}{m}{\cite{#1}}",
            r"\DeclareDocumentCommand{\xparseRef}{m}{\cite{#1}}",
            r"\NewExpandableDocumentCommand{\xparseRef}{m}{\cite{#1}}",
            r"\newrobustcmd{\smithref}{\cite{smith2020}}",
            r"\renewrobustcmd{\smithref}{\cite{smith2020}}",
            r"\providerobustcmd{\smithref}{\cite{smith2020}}",
            r"\let\priorentry\bibentry Prior \priorentry{smith2020}.",
            r"\newcommand{\priorentry}{\bibentry{smith2020}} Prior \priorentry.",
            r"\newcommand{\priorentry}[1]{\bibentry{#1}} Prior \priorentry{smith2020}.",
            r"\let\priorentry\bibentry\let\olderentry\priorentry",
        )
        for source in sources:
            with self.subTest(source=source):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(source + "\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "citation-alias", expected=2,
                )
                self.assertIn("user-defined citation command", completed.stderr)

    def test_supported_citation_command_redefinition_fails_closed(self) -> None:
        for source in (
            r"\renewcommand{\bibentry}[1]{safe text}",
            r"\def\bibentry#1{safe text}",
        ):
            with self.subTest(source=source):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(source + "\n", encoding="utf-8")
                (self.root / "output/evidence").mkdir(exist_ok=True)
                completed = self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", "citation-redefinition", expected=2,
                )
                self.assertIn("redefinition of supported citation command", completed.stderr)

    def test_declared_graphics_extension_order_fails_closed(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            r"\DeclareGraphicsExtensions{.png,.pdf}\includegraphics{figure}" + "\n",
            encoding="utf-8",
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "graphics-extension-order", expected=2,
        )
        self.assertIn("unsupported dynamic LaTeX dependency", completed.stderr)

    def test_dynamic_bibliography_dependency_fails_closed(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\bibliography{\\bibmacro}\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "stage5-initial", expected=2,
        )
        self.assertIn("dynamic bibliography dependency", completed.stderr)

    def test_braceless_input_is_included_in_paper_graph(self) -> None:
        self.add_paper_audit(braceless_input=True, citation=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            "paper/sections/results.tex",
            [entry["path"] for entry in audit_input["paper_sources"]],
        )
        self.assertEqual(audit_input["citation_occurrences"][0]["cite_keys"], ["prior"])

    def test_braceless_input_in_local_package_is_included(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\documentclass{article}\\usepackage{local}\\begin{document}x\\end{document}\n",
            encoding="utf-8",
        )
        (self.root / "paper/local.sty").write_text(
            "\\input data.tex\n", encoding="utf-8"
        )
        (self.root / "paper/data.tex").write_text(
            "Evidence \\cite{inside}.\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "package-braceless-input",
        )
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            "paper/data.tex", [entry["path"] for entry in audit_input["paper_sources"]]
        )
        self.assertEqual(audit_input["citation_occurrences"][0]["cite_keys"], ["inside"])

    def test_extensionless_input_prefers_the_tex_file(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text("\\input{chapter}\n", encoding="utf-8")
        (self.root / "paper/chapter").write_text("decoy\n", encoding="utf-8")
        (self.root / "paper/chapter.tex").write_text(
            "Actual \\cite{actual}.\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "extensionless-input",
        )
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        paths = [entry["path"] for entry in audit_input["paper_sources"]]
        self.assertIn("paper/chapter.tex", paths)
        self.assertNotIn("paper/chapter", paths)
        self.assertEqual(audit_input["citation_occurrences"][0]["cite_keys"], ["actual"])

    def test_input_if_file_exists_prefers_the_tex_file(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_text(
            "\\InputIfFileExists{choice}{}{}\n", encoding="utf-8"
        )
        (self.root / "paper/choice").write_text("decoy\n", encoding="utf-8")
        (self.root / "paper/choice.tex").write_text(
            "Actual \\cite{conditional}.\n", encoding="utf-8"
        )
        (self.root / "output/evidence").mkdir()
        self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "conditional-extensionless-input",
        )
        audit = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        paths = [entry["path"] for entry in audit["paper_sources"]]
        self.assertIn("paper/choice.tex", paths)
        self.assertNotIn("paper/choice", paths)
        self.assertEqual(audit["citation_occurrences"][0]["cite_keys"], ["conditional"])

    def test_local_package_inputs_preserve_explicit_non_tex_suffixes(self) -> None:
        for braced in (True, False):
            with self.subTest(braced=braced):
                shutil.rmtree(self.root / "paper", ignore_errors=True)
                shutil.rmtree(self.root / "output/evidence", ignore_errors=True)
                (self.root / "paper").mkdir()
                (self.root / "paper/main.tex").write_text(
                    "\\documentclass{article}\\usepackage{local}"
                    "\\begin{document}x\\end{document}\n",
                    encoding="utf-8",
                )
                input_text = "\\input{reader.cfg}\n" if braced else "\\input reader.cfg\n"
                (self.root / "paper/local.sty").write_text(input_text, encoding="utf-8")
                (self.root / "paper/reader.cfg").write_text(
                    "Evidence \\cite{configkey}.\n", encoding="utf-8"
                )
                (self.root / "output/evidence").mkdir(parents=True)
                self.call(
                    "prepare-audit", "--output", "output/evidence/audit_input.json",
                    "--checkpoint", f"local-explicit-suffix-{braced}",
                )
                audit = json.loads(
                    (self.root / "output/evidence/audit_input.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertIn(
                    "paper/reader.cfg",
                    [entry["path"] for entry in audit["paper_sources"]],
                )
                self.assertEqual(
                    audit["citation_occurrences"][0]["cite_keys"], ["configkey"]
                )

    def test_static_iffileexists_allows_absent_optional_bibliography(self) -> None:
        self.add_paper_audit(conditional_bib=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "paper/bib.bib", [entry["path"] for entry in audit_input["paper_sources"]]
        )

    def test_starred_graphic_dependency_is_bound(self) -> None:
        chart = self.root / "paper/sections/assets/chart.png"
        chart.parent.mkdir(parents=True)
        chart.write_bytes(b"png-v1")
        self.add_paper_audit(starred_graphic=True)
        self.bind_paper()
        chart.write_bytes(b"png-v2")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("paper/sections/assets/chart.png", completed.stdout)

    def test_local_style_dependencies_are_recursively_bound(self) -> None:
        (self.root / "data/style_rows.csv").write_text("x\n1\n")
        (self.root / "paper").mkdir()
        (self.root / "paper/localaudit.sty").write_text(
            "\\lstinputlisting{../data/style_rows.csv}\n"
            "Style claim \\citetitle{stylekey}.\n"
        )
        self.add_paper_audit(local_style=True)
        audit_input = json.loads(
            (self.root / "output/evidence/audit_input.json").read_text(encoding="utf-8")
        )
        self.assertEqual(audit_input["citation_occurrences"][0]["cite_keys"], ["stylekey"])
        self.bind_paper()
        (self.root / "data/style_rows.csv").write_text("x\n2\n")
        completed = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            expected=1,
        )
        self.assertIn("data/style_rows.csv", completed.stdout)

    def test_unknown_result_reference_rejected(self) -> None:
        script = self.root / "code/analyze.py"
        text = script.read_text(encoding="utf-8").replace(
            "'result_ids': ['main.mean', 'main.rows']",
            "'result_ids': ['missing.result']",
        )
        script.write_text(text, encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/bad_results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("unknown results", completed.stderr)

    def test_runtime_validator_matches_optional_schema_types(self) -> None:
        script = self.root / "code/analyze.py"
        text = script.read_text(encoding="utf-8").replace(
            "'artifact': 'output/stagex/detail.json', 'selector': 'rows'",
            "'artifact': 'output/stagex/detail.json', 'selector': 7",
        )
        script.write_text(text, encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/invalid_results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("selector must be a string", completed.stderr)

    def test_published_schemas_reject_obvious_path_hazards_and_mark_semantic_boundary(self) -> None:
        schema_root = REPO / "deploy_assets/templates/utils/results_pipeline"
        plan = json.loads((schema_root / "run-plan-v1.schema.json").read_text())
        bundle = json.loads((schema_root / "results-v1.schema.json").read_text())
        for schema in (plan, bundle):
            self.assertIn("Structural preflight only", schema["$comment"])
            project_pattern = re.compile(schema["$defs"]["projectPath"]["pattern"])
            output_pattern = re.compile(schema["$defs"]["outputPath"]["pattern"])
            for dotenv_name in (".env", ".envrc", ".env-local", ".env.production",
                                ".ENV", ".Env.local"):
                self.assertIsNone(project_pattern.fullmatch(f"data/{dotenv_name}/secret"))
                self.assertIsNone(output_pattern.fullmatch(f"output/{dotenv_name}/secret"))
            for bad in ("/abs/file", "../escape", "data/../escape", "data\\escape",
                        ".env", "data/.env.local", ".git/config", ".GIT/config",
                        "data//file"):
                self.assertIsNone(project_pattern.search(bad), bad)
            for bad in ("output/evidence/x.json", "output/EVIDENCE/x.json",
                        "output/../escape", "output/.env",
                        "output/a\\b", "output//x", "output//evidence/x.json",
                        "output/a//b"):
                self.assertIsNone(output_pattern.search(bad), bad)
            self.assertIsNotNone(project_pattern.search("data/input.csv"))
            self.assertIsNotNone(output_pattern.search("output/stage3/results.json"))
        self.assertTrue(bundle["properties"]["artifacts"]["uniqueItems"])
        self.assertTrue(bundle["properties"]["exhibits"]["uniqueItems"])

    def test_invalid_utf8_plan_is_controlled_failure(self) -> None:
        (self.root / "output/stagex/results.plan.json").write_bytes(b"\xff\xfe")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("cannot read JSON", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_invalid_utf8_paper_source_is_controlled_failure(self) -> None:
        (self.root / "paper").mkdir()
        (self.root / "paper/main.tex").write_bytes(b"\xff\xfe")
        (self.root / "output/evidence").mkdir()
        completed = self.call(
            "prepare-audit", "--output", "output/evidence/audit_input.json",
            "--checkpoint", "invalid-utf8", expected=2,
        )
        self.assertIn("cannot read LaTeX source", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_atomic_json_parent_failure_is_controlled(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        blocker = self.root / "blocked"
        blocker.write_text("not a directory\n", encoding="utf-8")
        with self.assertRaisesRegex(module.EvidenceError, "directory"):
            module.atomic_json(blocker / "receipt.json", {"ok": True})

    def test_atomic_json_rejects_parent_ancestor_swap(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_atomic_swap", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        process_log = self.root / "process_log"
        moved = self.root / "process-log-real"
        outside_temp = tempfile.TemporaryDirectory()
        self.addCleanup(outside_temp.cleanup)
        outside = Path(outside_temp.name)
        original = module._open_or_create_directory_path
        swapped = False

        def swap_after_open(path: Path) -> int:
            nonlocal swapped
            descriptor = original(path)
            if not swapped and Path(path) == process_log:
                process_log.rename(moved)
                process_log.symlink_to(outside, target_is_directory=True)
                swapped = True
            return descriptor

        with mock.patch.object(
                module, "_open_or_create_directory_path", side_effect=swap_after_open):
            with self.assertRaises(module.EvidenceError):
                module.atomic_json(process_log / "results_registry.json", {"ok": True})
        self.assertFalse((outside / "results_registry.json").exists())
        process_log.unlink()
        moved.rename(process_log)

    def test_transaction_cleanup_fsyncs_each_removed_entry(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        backup = self.root / module.TRANSACTION_BACKUP_PATH
        backup.mkdir()
        (backup / "0").write_text("backup\n", encoding="utf-8")
        journal = self.root / module.TRANSACTION_PATH
        journal.write_text("{}\n", encoding="utf-8")
        original_fsync = os.fsync
        with mock.patch.object(module.os, "fsync", wraps=original_fsync) as synced:
            module._clear_transaction_files(self.root)
        self.assertGreaterEqual(synced.call_count, 2)

    def test_rollback_cleanup_fsyncs_removed_destination(self) -> None:
        spec = importlib.util.spec_from_file_location("results_pipeline_tested", UTILITY)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        destination = self.root / "output/stagex/cleanup-only.json"
        destination.write_text("published\n", encoding="utf-8")
        original_fsync = os.fsync
        with mock.patch.object(module.os, "fsync", wraps=original_fsync) as synced:
            parent_fd, _ = module._safe_restore_destination(self.root, destination)
            os.close(parent_fd)
        self.assertFalse(destination.exists())
        self.assertGreaterEqual(synced.call_count, 1)

    def test_symlink_and_credentials_rejected(self) -> None:
        (self.root / ".env").write_text("SECRET=x\n")
        script = self.root / "code/analyze.py"
        original = script.read_text(encoding="utf-8")
        script.write_text(original.replace("['data/input.txt']", "['.env']"), encoding="utf-8")
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/env_results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("credential-bearing", completed.stderr)

        script.write_text(original.replace("['data/input.txt']", "['data/link.txt']"),
                          encoding="utf-8")
        (self.root / "data/link.txt").symlink_to(self.root / "data/input.txt")
        plan = json.loads((self.root / "output/stagex/results.plan.json").read_text())
        plan["producer_inputs"] = ["data/link.txt"]
        (self.root / "output/stagex/results.plan.json").write_text(
            json.dumps(plan) + "\n"
        )
        completed = self.call(
            "run", "--bundle", "output/stagex/results.json",
            "--receipt", "output/stagex/link_results.receipt.json", "--",
            sys.executable, "code/analyze.py", expected=2,
        )
        self.assertIn("symlink path is forbidden", completed.stderr)


if __name__ == "__main__":
    unittest.main()
