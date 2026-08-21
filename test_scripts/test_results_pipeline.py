#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import venv
from pathlib import Path


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
               'inputs': ['data/input.txt'], 'reproducibility': 'exact'},
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
        report = self.call(
            "verify", "--receipt", "output/stagex/results.receipt.json", "--rerender"
        )
        self.assertEqual(json.loads(report.stdout)["status"], "PASS")
        all_report = self.call("verify-all", "--require-one", "--rerender")
        self.assertEqual(json.loads(all_report.stdout)["status"], "PASS")

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

    def test_project_venv_can_use_an_external_base_runtime(self) -> None:
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
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

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

    def test_paper_with_no_computed_evidence_can_bind(self) -> None:
        self.add_paper_audit()
        self.bind_paper()
        report = self.call(
            "verify-paper", "--receipt", "process_log/paper_evidence.receipt.json",
            "--rerender",
        )
        self.assertEqual(json.loads(report.stdout)["status"], "PASS")

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
            "backups": [{"path": "data/input.txt", "backup": "0"}],
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
        self.assertIn("no byte-bound prior characterization", completed.stderr)

    def test_unchanged_citation_can_reuse_bound_characterization(self) -> None:
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
        self.call(
            "bind-paper", "--audit-input", "output/evidence/audit_input_second.json",
            "--summary", "output/evidence/audit_second.json",
            "--report", "output/evidence/audit_second.md",
            "--citation-summary", "output/evidence/citations_second.json",
            "--citation-report", "output/evidence/citations_second.md",
            "--receipt", "process_log/paper_evidence.receipt.json",
            "--checkpoint", "stage5-second",
        )

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
        self.assertIn("retired result receipt bytes are stale", completed.stderr)

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
        self.assertIn("would overwrite result lifecycle evidence", completed.stderr)
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
