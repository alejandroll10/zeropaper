#!/usr/bin/env python3
"""Construction guard: does a fabricated ledger fail and an honest one pass?

The failure this guards against is not hypothetical. Four consecutive Stage 3a
attempts in the field shipped a ledger whose per-row provenance fields were
constant placeholders and whose claimed content hashes matched no source
document, and it passed receipt verify, re-render, clean-room rebuild, and the
independent headline gate every time. The fixtures below reproduce that shape.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
GUARD = REPO / "deploy_assets/extensions/empirical/utils/construction_guard.py"
SPEC = importlib.util.spec_from_file_location("construction_guard", GUARD)
assert SPEC is not None and SPEC.loader is not None
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


def digest_of(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class GuardFixture(unittest.TestCase):
    """A sealed corpus of source documents plus a receipt that fingerprints it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.corpus = self.root / "data" / "corpus"
        self.corpus.mkdir(parents=True)
        self.documents: dict[str, bytes] = {}
        for index in range(10):
            name = f"doc_{index:02d}.html"
            payload = f"<html><body>decision {index} taken on 2026-0{index % 9 + 1}-01</body></html>".encode()
            (self.corpus / name).write_bytes(payload)
            self.documents[name] = payload
        (self.root / "output" / "stage3a").mkdir(parents=True)
        (self.root / "code").mkdir()
        (self.root / "code" / "build.py").write_text("# producer\nrows = []\n", encoding="utf-8")

    def write_ledger(self, name: str, rows: list[dict[str, str]]) -> Path:
        path = self.root / "output" / "stage3a" / name
        header = list(rows[0])
        lines = [",".join(header)]
        lines.extend(",".join(row[column] for column in header) for row in rows)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def receipt(self, ledger: Path) -> Path:
        entries = sorted(
            (
                {"path": name, "kind": "file", "sha256": f"sha256:{digest_of(payload)}"}
                for name, payload in self.documents.items()
            ),
            key=lambda entry: entry["path"],
        )
        directory_digest = digest_of(
            json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
        )
        code = self.root / "code" / "build.py"
        receipt = {
            "kind": "result",
            "receipt_version": 2,
            "supersedes": [],
            "render_run": None,
            "producer_run": {
                "command": ["python3", "code/build.py"],
                "plan": {
                    "path": "output/stage3a/results.plan.json", "kind": "file",
                    "sha256": f"sha256:{digest_of(b'plan')}",
                },
                "bundle": {
                    "path": "output/stage3a/results.json", "kind": "file",
                    "sha256": f"sha256:{digest_of(b'bundle')}",
                },
                "code": [{
                    "path": "code/build.py", "kind": "file",
                    "sha256": f"sha256:{digest_of(code.read_bytes())}",
                }],
                "inputs": [{
                    "path": "data/corpus", "kind": "directory",
                    "sha256": f"sha256:{directory_digest}", "entries": entries,
                }],
                "renderer_code": [],
                "artifacts": [{
                    "path": f"output/stage3a/{ledger.name}", "kind": "file",
                    "sha256": f"sha256:{digest_of(ledger.read_bytes())}",
                }],
                "exhibits": [],
                "reproducibility": "exact",
                "environment": {},
            },
        }
        path = self.root / "output" / "stage3a" / "results.receipt.json"
        path.write_text(json.dumps(receipt), encoding="utf-8")
        return path

    def run_guard(self, receipt: Path, *extra: str) -> tuple[int, dict]:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", str(GUARD), "--project-root", str(self.root),
             "check", "--receipt", str(receipt), *extra],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(completed.returncode, 2, completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def statuses(self, report: dict, check: str) -> list[str]:
        return [f["status"] for f in report["findings"] if f["check"] == check]

    def honest_rows(self) -> list[dict[str, str]]:
        rows = []
        for index, (name, payload) in enumerate(sorted(self.documents.items())):
            rows.append({
                "row_id": str(index),
                "source_document": name,
                "payload_sha256": digest_of(payload),
                "decision_locator": f"{digest_of(payload)}:32:48",
                "heading_type": "operative" if index % 2 else "supplementary",
            })
        return rows


class HonestLedgerTest(GuardFixture):
    def test_derived_ledger_passes_every_check(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["failure_count"], 0)
        self.assertEqual(self.statuses(report, "claimed-digest-provenance"), ["PASS"])
        self.assertEqual(self.statuses(report, "source-reference-resolution"), ["PASS"])
        self.assertEqual(self.statuses(report, "input-coverage"), ["PASS"])

    def test_all_success_outcome_column_warns_and_never_fails(self) -> None:
        """The check that gets switched off on day one if it fails good work."""
        rows = self.honest_rows()
        for row in rows:
            row["parser_disposition"] = "parsed_agree"
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        constant = [f for f in report["findings"] if f["check"] == "constant-column"]
        self.assertEqual([f["column"] for f in constant], ["parser_disposition"])
        self.assertEqual(constant[0]["status"], "WARN")

    def test_directory_artifact_entries_are_scanned(self) -> None:
        """The data-first release shape: the relations live inside a directory."""
        release = self.root / "output" / "dataset" / "release_v1"
        release.mkdir(parents=True)
        rows = self.honest_rows()
        header = list(rows[0])
        (release / "ledger.csv").write_text(
            "\n".join([",".join(header)] + [",".join(r[c] for c in header) for r in rows]) + "\n",
            encoding="utf-8",
        )
        (release / "README.md").write_text("# release\n", encoding="utf-8")
        ledger = self.write_ledger("ledger.csv", rows)
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        entries = sorted(
            (
                {"path": child.name, "kind": "file",
                 "sha256": f"sha256:{digest_of(child.read_bytes())}"}
                for child in release.iterdir()
            ),
            key=lambda entry: entry["path"],
        )
        receipt["producer_run"]["artifacts"].append({
            "path": "output/dataset/release_v1", "kind": "directory",
            "sha256": f"sha256:{digest_of(b'dir')}", "entries": entries,
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])
        self.assertIn("output/dataset/release_v1/ledger.csv", report["artifacts_scanned"])
        self.assertIn("output/dataset/release_v1/README.md", report["artifacts_not_tabular"])

    def test_receipt_path_escaping_the_project_is_refused(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"][0]["path"] = "output/../../escape.csv"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, "-I", "-S", str(GUARD), "--project-root", str(self.root),
             "check", "--receipt", str(receipt_path)],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("outside the project", completed.stderr)


class FabricatedLedgerTest(GuardFixture):
    def test_hashes_matching_no_source_document_fail(self) -> None:
        rows = self.honest_rows()
        for index, row in enumerate(rows):
            row["payload_sha256"] = digest_of(f"invented {index}".encode())
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 1)
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(finding["binding"], "row-scoped")
        self.assertEqual(len(finding["mismatched_examples"]), 5)

    def test_rows_citing_documents_outside_the_corpus_fail(self) -> None:
        rows = self.honest_rows()
        rows[0]["source_document"] = "doc_99.html"
        rows[1]["source_document"] = "doc_98.html"
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 1)
        finding = next(
            f for f in report["findings"] if f["check"] == "source-reference-resolution"
        )
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(sorted(finding["unresolved_examples"]), ["doc_98.html", "doc_99.html"])

    def test_prose_token_in_a_locator_column_fails_when_constant(self) -> None:
        rows = self.honest_rows()
        for row in rows:
            row["decision_locator"] = "operative-policy-token"
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 1)
        finding = next(f for f in report["findings"] if f["check"] == "degenerate-locator")
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(finding["value"], "operative-policy-token")

    def test_varying_prose_locator_warns_rather_than_failing(self) -> None:
        rows = self.honest_rows()
        for index, row in enumerate(rows):
            row["decision_locator"] = "operative" if index % 2 else "supplementary"
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        finding = next(f for f in report["findings"] if f["check"] == "degenerate-locator")
        self.assertEqual(finding["status"], "WARN")

    def test_partial_corpus_resolution_warns_with_the_share(self) -> None:
        rows = [row for row in self.honest_rows() if int(row["row_id"]) < 3]
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        finding = next(f for f in report["findings"] if f["check"] == "input-coverage")
        self.assertEqual(finding["status"], "WARN")
        self.assertEqual((finding["cited"], finding["files"]), (3, 10))

    def test_column_empty_on_every_row_warns(self) -> None:
        rows = self.honest_rows()
        for row in rows:
            row["parsed_action_time"] = ""
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        empty = [f for f in report["findings"] if f["check"] == "empty-column"]
        self.assertEqual([f["column"] for f in empty], ["parsed_action_time"])


class ReviewRegressionTest(GuardFixture):
    """Cases an independent adversarial review found the first version missed."""

    def test_digest_copied_from_the_receipt_for_the_wrong_row_fails(self) -> None:
        """Set membership alone costs a fabricator one copy-paste and no hashing.

        Every fingerprinted digest sits in the receipt as plaintext, so a row can
        carry a real corpus digest that belongs to a different document. Only
        binding the digest to the source the row itself names catches that.
        """
        rows = self.honest_rows()
        real = [row["payload_sha256"] for row in rows]
        for index, row in enumerate(rows):
            row["payload_sha256"] = real[(index + 1) % len(real)]
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 1)
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(finding["binding"], "row-scoped")
        self.assertEqual(finding["rows_bound_to_their_own_source"], 0)
        self.assertTrue(finding["mismatched_examples"])

    def test_camel_case_locator_is_still_treated_as_a_locator(self) -> None:
        rows = self.honest_rows()
        for row in rows:
            row["decisionLocator"] = "operative-policy-token"
            del row["decision_locator"]
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 1)
        finding = next(f for f in report["findings"] if f["check"] == "degenerate-locator")
        self.assertEqual((finding["column"], finding["status"]), ("decisionLocator", "FAIL"))

    def test_duplicate_header_does_not_exempt_the_second_column(self) -> None:
        rows = self.honest_rows()
        header = list(rows[0]) + ["payload_sha256"]
        path = self.root / "output" / "stage3a" / "ledger.csv"
        lines = [",".join(header)]
        for index, row in enumerate(rows):
            lines.append(",".join(
                [row[column] for column in header[:-1]] + [digest_of(f"fake {index}".encode())]
            ))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, report = self.run_guard(self.receipt(path))
        self.assertEqual(code, 1)
        self.assertEqual(
            [f["column"] for f in report["findings"] if f["check"] == "duplicate-column"],
            ["payload_sha256"],
        )
        failed = [
            f for f in report["findings"]
            if f["check"] == "claimed-digest-provenance" and f["status"] == "FAIL"
        ]
        self.assertEqual([f["column"] for f in failed], ["payload_sha256#2"])

    def test_byte_order_mark_does_not_hide_a_column_from_its_override(self) -> None:
        rows = self.honest_rows()
        for index, row in enumerate(rows):
            row["payload_sha256"] = digest_of(f"normalized {index}".encode())
        header = ["payload_sha256"] + [c for c in rows[0] if c != "payload_sha256"]
        path = self.root / "output" / "stage3a" / "ledger.csv"
        body = [",".join(header)]
        body.extend(",".join(row[column] for column in header) for row in rows)
        path.write_text("\ufeff" + "\n".join(body) + "\n", encoding="utf-8")
        code, report = self.run_guard(
            self.receipt(path), "--digest-scope", "payload_sha256=derived"
        )
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual((finding["column"], finding["status"]), ("payload_sha256", "WARN"))


class RoundTwoRegressionTest(GuardFixture):
    """Cases the second adversarial review found the first fix missed."""

    def test_naming_the_producers_own_code_does_not_earn_a_row_scoped_pass(self) -> None:
        """Binding must be to declared inputs, not to anything in the receipt.

        A row that names the producer's own source file and quotes that file's
        digest demonstrates nothing about deriving anything from a source, and
        must not collect the verdict reserved for genuine binding.
        """
        code_digest = digest_of((self.root / "code" / "build.py").read_bytes())
        rows = []
        for index in range(10):
            rows.append({
                "row_id": str(index),
                "source_document": "code/build.py",
                "payload_sha256": code_digest,
            })
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertNotEqual(finding["status"], "PASS")
        self.assertEqual(finding["binding"], "set-membership")
        self.assertEqual(finding["rows_bound_to_their_own_source"], 0)

    def test_basename_shared_by_two_input_directories_does_not_bind(self) -> None:
        second = self.root / "data" / "other"
        second.mkdir(parents=True)
        collision = b"<html>a different document</html>"
        (second / "doc_00.html").write_bytes(collision)
        rows = self.honest_rows()
        for row in rows:
            row["source_document"] = "doc_00.html"
            row["payload_sha256"] = digest_of(collision)
        ledger = self.write_ledger("ledger.csv", rows)
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["inputs"].append({
            "path": "data/other", "kind": "directory",
            "sha256": f"sha256:{digest_of(b'other')}",
            "entries": [{"path": "doc_00.html", "kind": "file",
                         "sha256": f"sha256:{digest_of(collision)}"}],
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(finding["binding"], "set-membership")
        self.assertEqual(finding["rows_bound_to_their_own_source"], 0)

    def test_locator_without_a_word_break_degrades_to_the_constant_warning(self) -> None:
        """The deliberate limit of matching an exact name token.

        Matching the substring instead would hard-fail `translocator_id`, and
        excluding such words needs a list that can never be complete. So this
        name escapes the stop and lands on the name-blind constant warning,
        which is the direction that does not fail honest work.
        """
        rows = self.honest_rows()
        for row in rows:
            row["decisionlocator"] = "operative-policy-token"
            del row["decision_locator"]
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(
            [f["column"] for f in report["findings"] if f["check"] == "degenerate-locator"],
            [],
        )
        constant = [
            f for f in report["findings"]
            if f["check"] == "constant-column" and f["column"] == "decisionlocator"
        ]
        self.assertEqual([f["status"] for f in constant], ["WARN"])

    def test_ordinary_word_containing_locator_is_never_hard_failed(self) -> None:
        for column in ("capital_allocator_id", "translocator_id"):
            with self.subTest(column=column):
                rows = self.honest_rows()
                for row in rows:
                    row[column] = "CONST-00042"
                ledger = self.write_ledger("ledger.csv", rows)
                code, report = self.run_guard(self.receipt(ledger))
                self.assertEqual(code, 0, report["findings"])
                self.assertEqual(
                    {f["column"] for f in report["findings"]
                     if f["check"] == "degenerate-locator"},
                    {"decision_locator"},
                )

    def test_byte_order_mark_in_a_json_artifact_does_not_abort_the_run(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        lines = self.root / "output" / "stage3a" / "rows.jsonl"
        lines.write_text(
            "\ufeff" + "\n".join(
                json.dumps({"row_id": row["row_id"], "payload_sha256": row["payload_sha256"]})
                for row in self.honest_rows()
            ) + "\n",
            encoding="utf-8",
        )
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"].append({
            "path": "output/stage3a/rows.jsonl", "kind": "file",
            "sha256": f"sha256:{digest_of(lines.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertIn("output/stage3a/rows.jsonl", report["artifacts_scanned"])

    def test_declared_input_file_no_row_cites_is_reported(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        (self.root / "data" / "lookup.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        receipt["producer_run"]["inputs"].append({
            "path": "data/lookup.csv", "kind": "file",
            "sha256": f"sha256:{digest_of((self.root / 'data' / 'lookup.csv').read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])
        uncited = [
            f for f in report["findings"]
            if f["check"] == "input-coverage" and f["input"] == "data/lookup.csv"
        ]
        self.assertEqual([f["status"] for f in uncited], ["WARN"])

    def test_header_repeated_three_times_reports_every_occurrence(self) -> None:
        rows = self.honest_rows()
        header = ["row_id", "row_id", "row_id"]
        path = self.root / "output" / "stage3a" / "ledger.csv"
        body = [",".join(header)]
        body.extend(",".join([row["row_id"]] * 3) for row in rows)
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        code, report = self.run_guard(self.receipt(path))
        finding = next(f for f in report["findings"] if f["check"] == "duplicate-column")
        self.assertEqual(finding["occurrences"], 3)


class RoundThreeRegressionTest(GuardFixture):
    """Cases the third adversarial review found the second fix missed."""

    def _collision_receipt(self, ledger: Path, *, file_input_first: bool) -> Path:
        """A standalone input whose path equals a corpus file's basename."""
        control = self.root / "doc_00.html"
        control.write_bytes(b"<html>unrelated control file</html>")
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        control_record = {
            "path": "doc_00.html", "kind": "file",
            "sha256": f"sha256:{digest_of(control.read_bytes())}",
        }
        corpus = receipt["producer_run"]["inputs"]
        receipt["producer_run"]["inputs"] = (
            [control_record] + corpus if file_input_first else corpus + [control_record]
        )
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return receipt_path

    def test_basename_colliding_with_a_declared_path_binds_the_same_either_order(
            self) -> None:
        """Whether a reference is ambiguous is not a fact about receipt ordering.

        Deciding it while walking the input list made the outcome depend on
        which record came first, so the same collision was caught in one order
        and silently accepted in the other.
        """
        verdicts = []
        for file_input_first in (True, False):
            rows = self.honest_rows()
            for row in rows:
                row["source_document"] = "doc_00.html"
            ledger = self.write_ledger("ledger.csv", rows)
            receipt = self._collision_receipt(ledger, file_input_first=file_input_first)
            _code, report = self.run_guard(receipt)
            finding = next(
                f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
            )
            verdicts.append((finding["status"], finding["binding"]))
        self.assertEqual(verdicts[0], verdicts[1])

    def test_ambiguous_basename_is_named_in_the_report(self) -> None:
        second = self.root / "data" / "other"
        second.mkdir(parents=True)
        collision = b"<html>a different document</html>"
        (second / "doc_00.html").write_bytes(collision)
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["inputs"].append({
            "path": "data/other", "kind": "directory",
            "sha256": f"sha256:{digest_of(b'other')}",
            "entries": [{"path": "doc_00.html", "kind": "file",
                         "sha256": f"sha256:{digest_of(collision)}"}],
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        _code, report = self.run_guard(receipt_path)
        self.assertEqual(report["ambiguous_input_names"], ["doc_00.html"])

    def test_manifest_of_the_receipts_own_outputs_is_not_a_standing_warning(self) -> None:
        """The data-first release manifest shape, which recurs on every run."""
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        manifest = self.root / "output" / "stage3a" / "manifest.csv"
        manifest.write_text(
            "file,sha256\nledger.csv," + digest_of(ledger.read_bytes()) + "\n",
            encoding="utf-8",
        )
        receipt["producer_run"]["artifacts"].append({
            "path": "output/stage3a/manifest.csv", "kind": "file",
            "sha256": f"sha256:{digest_of(manifest.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"]
            if f["check"] == "claimed-digest-provenance"
            and f["artifact"] == "output/stage3a/manifest.csv"
        )
        self.assertEqual((finding["status"], finding["binding"]), ("PASS", "self-manifest"))

    def test_byte_order_mark_on_the_receipt_itself_is_read(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt_path.write_text(
            "\ufeff" + receipt_path.read_text(encoding="utf-8"), encoding="utf-8"
        )
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])


class RoundFourRegressionTest(GuardFixture):
    """Cases the fourth adversarial review found the third fix missed."""

    def test_decoy_artifact_digests_cannot_launder_a_fabricated_ledger(self) -> None:
        """A producer controls its own outputs' bytes, so naming one proves nothing.

        Passing a column merely because every digest in it is *some* artifact of
        this receipt is cheaper to fabricate than the set-membership case it was
        meant to improve on: emit a decoy file, point the provenance column at
        its digest, collect a clean pass. Binding has to be per row either way.
        """
        decoy = self.root / "output" / "stage3a" / "decoy.txt"
        decoy.write_text("producer-controlled bytes\n", encoding="utf-8")
        rows = self.honest_rows()
        for row in rows:
            row["payload_sha256"] = digest_of(decoy.read_bytes())
            row["source_document"] = ""
        ledger = self.write_ledger("ledger.csv", rows)
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"].append({
            "path": "output/stage3a/decoy.txt", "kind": "file",
            "sha256": f"sha256:{digest_of(decoy.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        _code, report = self.run_guard(receipt_path)
        finding = next(
            f for f in report["findings"]
            if f["check"] == "claimed-digest-provenance"
            and f["artifact"] == "output/stage3a/ledger.csv"
        )
        self.assertNotEqual(finding["status"], "PASS")
        self.assertNotEqual(finding["binding"], "self-manifest")
        self.assertEqual(finding["rows_bound_to_an_own_artifact"], 0)

    def test_one_path_declared_twice_with_conflicting_digests_does_not_bind(self) -> None:
        rows = self.honest_rows()
        for row in rows:
            row["source_document"] = "data/corpus/doc_00.html"
        ledger = self.write_ledger("ledger.csv", rows)
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["inputs"].append({
            "path": "data/corpus/doc_00.html", "kind": "file",
            "sha256": f"sha256:{digest_of(b'a conflicting fingerprint')}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        _code, report = self.run_guard(receipt_path)
        self.assertIn("data/corpus/doc_00.html", report["ambiguous_input_names"])
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(finding["rows_bound_to_their_own_source"], 0)


class RoundFiveRegressionTest(GuardFixture):
    """Cases the fifth adversarial review found: labels that misdescribed a check."""

    def _mixed_receipt(self, ledger: Path, sibling: Path) -> Path:
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"].append({
            "path": f"output/stage3a/{sibling.name}", "kind": "file",
            "sha256": f"sha256:{digest_of(sibling.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        return receipt_path

    def test_column_bound_partly_to_inputs_and_partly_to_artifacts_passes(self) -> None:
        """Every row is bound to something it names; nothing fell back.

        Reporting this as the set-membership warning told the audit that rows had
        been checked only for membership, which was the opposite of what happened.
        """
        sibling = self.root / "output" / "stage3a" / "sibling.csv"
        sibling.write_text("a,b\n1,2\n", encoding="utf-8")
        rows = self.honest_rows()
        for row in rows[:5]:
            row["source_document"] = "sibling.csv"
            row["payload_sha256"] = digest_of(sibling.read_bytes())
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self._mixed_receipt(ledger, sibling))
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"]
            if f["check"] == "claimed-digest-provenance"
            and f["artifact"] == "output/stage3a/ledger.csv"
        )
        self.assertEqual((finding["status"], finding["binding"]), ("PASS", "mixed"))
        self.assertEqual(finding["rows_bound_to_their_own_source"], 5)
        self.assertEqual(finding["rows_bound_to_an_own_artifact"], 5)
        self.assertEqual(finding["rows_naming_nothing_declared"], 0)
        self.assertNotIn("membership", finding.get("note", ""))

    def test_rows_naming_nothing_are_reported_as_the_weak_check(self) -> None:
        rows = self.honest_rows()
        for row in rows:
            row["source_document"] = ""
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual((finding["status"], finding["binding"]), ("WARN", "set-membership"))
        self.assertEqual(finding["rows_naming_nothing_declared"], len(rows))

    def test_artifact_basename_collision_is_reported_as_an_artifact(self) -> None:
        """An artifact collision under an input-only field name misdirects the audit."""
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        for index, folder in enumerate(("one", "two")):
            target = self.root / "output" / "stage3a" / folder
            target.mkdir(parents=True)
            (target / "manifest.csv").write_text(f"a,b\n{index},{index}\n", encoding="utf-8")
            receipt["producer_run"]["artifacts"].append({
                "path": f"output/stage3a/{folder}", "kind": "directory",
                "sha256": f"sha256:{digest_of(folder.encode())}",
                "entries": [{
                    "path": "manifest.csv", "kind": "file",
                    "sha256": f"sha256:{digest_of((target / 'manifest.csv').read_bytes())}",
                }],
            })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        _code, report = self.run_guard(receipt_path)
        self.assertEqual(report["ambiguous_artifact_names"], ["manifest.csv"])
        self.assertEqual(report["ambiguous_input_names"], [])


class RoundSixRegressionTest(GuardFixture):
    """Cases the sixth adversarial review found: labels read from the wrong signal."""

    def test_naming_an_input_but_binding_to_an_artifact_is_not_called_mixed(self) -> None:
        """`mixed` must mean the column really carries both kinds of row.

        Classifying on what a row mentions rather than on what its digest bound
        to labels a pure manifest column `mixed`, which tells the audit there are
        provenance rows in it to judge when there are none.
        """
        sibling = self.root / "output" / "stage3a" / "sibling.csv"
        sibling.write_text("a,b\n1,2\n", encoding="utf-8")
        rows = self.honest_rows()
        for row in rows:
            row["artifact_name"] = "sibling.csv"
            row["payload_sha256"] = digest_of(sibling.read_bytes())
        ledger = self.write_ledger("ledger.csv", rows)
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"].append({
            "path": "output/stage3a/sibling.csv", "kind": "file",
            "sha256": f"sha256:{digest_of(sibling.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"]
            if f["check"] == "claimed-digest-provenance"
            and f["artifact"] == "output/stage3a/ledger.csv"
        )
        self.assertEqual(finding["binding"], "self-manifest")
        self.assertEqual(finding["rows_bound_to_their_own_source"], 0)

    def test_some_rows_naming_nothing_is_reported_as_partial(self) -> None:
        rows = self.honest_rows()
        for row in rows[:5]:
            row["source_document"] = ""
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(self.receipt(ledger))
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual((finding["status"], finding["binding"]), ("WARN", "partial"))
        self.assertEqual(finding["rows_naming_nothing_declared"], 5)
        self.assertEqual(finding["rows_bound_to_their_own_source"], 5)
        self.assertIn("were checked only for membership", finding["note"])


class OverrideAndIntegrityTest(GuardFixture):
    def test_derived_digest_override_downgrades_to_a_recorded_warning(self) -> None:
        rows = self.honest_rows()
        for index, row in enumerate(rows):
            row["payload_sha256"] = digest_of(f"normalized span {index}".encode())
        ledger = self.write_ledger("ledger.csv", rows)
        code, report = self.run_guard(
            self.receipt(ledger), "--digest-scope", "payload_sha256=derived"
        )
        self.assertEqual(code, 0, report["findings"])
        finding = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(finding["status"], "WARN")
        self.assertEqual(report["declared_derived_digest_columns"], ["payload_sha256"])

    def test_artifact_edited_after_the_receipt_fails(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt = self.receipt(ledger)
        ledger.write_text(ledger.read_text() + "99,doc_00.html,x,y,z\n", encoding="utf-8")
        code, report = self.run_guard(receipt)
        self.assertEqual(code, 1)
        self.assertEqual(self.statuses(report, "artifact-drift"), ["FAIL"])

    def test_banned_construction_on_the_producer_surface_fails(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt = self.receipt(ledger)
        (self.root / "code" / "build.py").write_text(
            "# producer\nLINK = 'literal-link-token'  # dead but banned\n", encoding="utf-8"
        )
        code, report = self.run_guard(receipt, "--forbid-token", "literal-link-token")
        self.assertEqual(code, 1)
        finding = next(f for f in report["findings"] if f["check"] == "forbidden-token")
        self.assertEqual(finding["status"], "FAIL")
        self.assertEqual(finding["hits"][0]["line"], 2)

    def test_report_is_written_where_the_orchestrator_can_forward_it(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        receipt = self.receipt(ledger)
        code, report = self.run_guard(receipt)
        self.assertEqual(code, 0, report["findings"])
        written = Path(report["report_path"])
        self.assertTrue(written.is_file())
        self.assertEqual(json.loads(written.read_text())["status"], "PASS")
        self.assertNotIn("empirical_analysis", written.as_posix())

    def test_non_tabular_artifacts_are_reported_not_silently_dropped(self) -> None:
        ledger = self.write_ledger("ledger.csv", self.honest_rows())
        figure = self.root / "output" / "stage3a" / "figure.png"
        figure.write_bytes(b"\x89PNG\r\n\x1a\n")
        receipt_path = self.receipt(ledger)
        receipt = json.loads(receipt_path.read_text())
        receipt["producer_run"]["artifacts"].append({
            "path": "output/stage3a/figure.png", "kind": "file",
            "sha256": f"sha256:{digest_of(figure.read_bytes())}",
        })
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        code, report = self.run_guard(receipt_path)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["artifacts_not_tabular"], ["output/stage3a/figure.png"])


RUNNER = REPO / "deploy_assets/templates/utils/results_pipeline/results_pipeline.py"

PRODUCER = """import csv, hashlib, json, os, pathlib
FABRICATE = __FABRICATE__
root = pathlib.Path.cwd()
corpus = root / 'data/corpus'
rows = []
for index, document in enumerate(sorted(corpus.iterdir())):
    payload = document.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    rows.append({
        'row_id': str(index),
        'source_document': document.name,
        'payload_sha256': digest,
        'decision_locator': digest + ':10:20',
        'heading_type': 'operative' if index % 2 else 'supplementary',
    })
if FABRICATE:
    for row in rows:
        row['payload_sha256'] = hashlib.sha256(row['row_id'].encode()).hexdigest()
        row['decision_locator'] = 'operative-policy-token'
        row['heading_type'] = 'other'
ledger = root / 'output/stagex/ledger.csv'
with ledger.open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
bundle = {
  'schema_version': 1,
  'producer': {'name': 'ledger', 'code': ['code/analyze.py'],
               'inputs': ['data/corpus'], 'reproducibility': 'captured'},
  'results': {'ledger.rows': {'description': 'Ledger row count', 'value': str(len(rows))}},
  'artifacts': [{'path': 'output/stagex/ledger.csv', 'description': 'Row ledger',
                 'media_type': 'text/csv'}],
  'renderer': {'code': []},
  'exhibits': []
}
(root / os.environ['RESULTS_BUNDLE_PATH']).write_text(json.dumps(bundle, indent=2) + '\\n')
"""


class RealReceiptIntegrationTest(unittest.TestCase):
    """The guard must parse receipts as results_pipeline.py actually writes them.

    Every other test here hand-builds a receipt, so every one of them would keep
    passing if the guard's reading of the real fingerprint format were wrong.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        (self.root / "code").mkdir()
        (self.root / "process_log").mkdir()
        (self.root / "output" / "stagex").mkdir(parents=True)
        corpus = self.root / "data" / "corpus"
        corpus.mkdir(parents=True)
        for index in range(12):
            (corpus / f"doc_{index}.html").write_text(
                f"<html><body>decision {index}</body></html>", encoding="utf-8"
            )
        (self.root / "process_log/results_registry.json").write_text(
            json.dumps({"kind": "result_registry", "registry_version": 1,
                        "active": [], "pending": [], "retired": [],
                        "receipt_fingerprints": {}}) + "\n", encoding="utf-8"
        )
        (self.root / "output/stagex/results.plan.json").write_text(json.dumps({
            "plan_version": 1,
            "producer_code": ["code/analyze.py"],
            "producer_inputs": ["data/corpus"],
            "artifacts": ["output/stagex/ledger.csv"],
            "renderer_code": [],
            "exhibits": [],
        }) + "\n", encoding="utf-8")

    def produce(self, *, fabricate: bool) -> Path:
        (self.root / "code/analyze.py").write_text(
            PRODUCER.replace("__FABRICATE__", "True" if fabricate else "False"),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "run",
             "--plan", "output/stagex/results.plan.json",
             "--bundle", "output/stagex/results.json",
             "--receipt", "output/stagex/results.receipt.json",
             "--caller-allowance-seconds", "3600", "--",
             sys.executable, "code/analyze.py"],
            cwd=self.root, text=True, capture_output=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return self.root / "output/stagex/results.receipt.json"

    def guard(self, receipt: Path) -> tuple[int, dict]:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", str(GUARD), "--project-root", str(self.root),
             "check", "--receipt", str(receipt)],
            capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(completed.returncode, 2, completed.stderr)
        return completed.returncode, json.loads(completed.stdout)

    def test_honest_producer_passes_against_a_real_receipt(self) -> None:
        code, report = self.guard(self.produce(fabricate=False))
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["artifacts_scanned"], ["output/stagex/ledger.csv"])
        digest = next(
            f for f in report["findings"] if f["check"] == "claimed-digest-provenance"
        )
        self.assertEqual(digest["status"], "PASS")
        self.assertEqual(digest["binding"], "row-scoped")
        self.assertEqual(digest["rows_bound_to_their_own_source"], 12)
        coverage = next(f for f in report["findings"] if f["check"] == "input-coverage")
        self.assertEqual(coverage["status"], "PASS")
        self.assertEqual(coverage["input"], "data/corpus")

    def test_fabricating_producer_fails_against_a_real_receipt(self) -> None:
        code, report = self.guard(self.produce(fabricate=True))
        self.assertEqual(code, 1)
        failed = {f["check"] for f in report["findings"] if f["status"] == "FAIL"}
        self.assertIn("claimed-digest-provenance", failed)
        self.assertIn("degenerate-locator", failed)


if __name__ == "__main__":
    unittest.main()
