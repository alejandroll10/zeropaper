#!/usr/bin/env python3
"""Fingerprint the inputs covered by a headline-replicator verdict.

The manifest binds a replication result to the complete project-local code
surface and the exact Headline claims section of the empirical report. It
never imports or executes analyzed producer code; lifecycle checks invoke the
template-owned canonical results validator in an isolated interpreter.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterable


SCHEMA_VERSION = 3
ALGORITHM = "sha256"
DEFAULT_REPORT = Path("output/stage3a/empirical_analysis.md")
DEFAULT_RESULT = Path("output/stage3a/empirics_verify_result.json")
RESULTS_REGISTRY = Path("process_log/results_registry.json")
RESULTS_LOCK = Path("process_log/results_pipeline.lock")
ANALYSIS_NAME = re.compile(r"^empirical_analysis(?:_v[A-Za-z0-9][A-Za-z0-9_.-]*)?\.md$")
VERIFIER_NAME = re.compile(r"^empirics_verify(?:_v[A-Za-z0-9][A-Za-z0-9_.-]*)?\.py$")
TOLERANCE_CLASSES = {
    "returns_spreads_coefficients": ("relative", 0.01),
    "moments": ("relative", 0.005),
    "counts": ("absolute", 1.0),
    "bounded_statistics": ("absolute", 0.005),
    "t_statistics": ("absolute", 0.05),
}


class ManifestError(RuntimeError):
    """A manifest input or stored result is missing, unsafe, or malformed."""


def _regular_file_bytes(path: Path, project_root: Path) -> bytes:
    try:
        relative = path.relative_to(project_root)
    except ValueError as exc:
        raise ManifestError(f"input escapes project root: {path}") from exc
    if not relative.parts or any(part in {"", ".", ".."} for part in relative.parts):
        raise ManifestError(f"input escapes project root: {path}")
    current = project_root
    for part in relative.parts:
        current /= part
        try:
            metadata = current.lstat()
        except FileNotFoundError as exc:
            raise ManifestError(f"required input is missing: {relative.as_posix()}") from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise ManifestError(f"input path contains a symlink: {relative.as_posix()}")
    if not stat.S_ISREG(metadata.st_mode):
        raise ManifestError(f"input is not a regular file: {relative.as_posix()}")
    return path.read_bytes()


@contextmanager
def _results_read_lock(project_root: Path) -> Iterable[None]:
    """Keep results publication outside a complete lifecycle/freshness verdict."""
    process_log = project_root / RESULTS_LOCK.parent
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        directory_descriptor = os.open(process_log, directory_flags)
    except OSError as exc:
        raise ManifestError(f"cannot open results pipeline lock directory: {exc}") from exc
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(RESULTS_LOCK.name, flags, dir_fd=directory_descriptor)
    except OSError as exc:
        os.close(directory_descriptor)
        raise ManifestError(f"cannot open results pipeline lock: {exc}") from exc
    os.close(directory_descriptor)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ManifestError("results pipeline lock must be one regular file")
        fcntl.flock(descriptor, fcntl.LOCK_SH)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _validated_analysis_path(value: str | Path) -> Path:
    raw = value.as_posix() if isinstance(value, Path) else value
    if not isinstance(raw, str):
        raise ManifestError("headline_claims.path must be a string")
    candidate = PurePosixPath(raw)
    if (
        candidate.is_absolute()
        or candidate.parts[:2] != ("output", "stage3a")
        or len(candidate.parts) != 3
        or not ANALYSIS_NAME.fullmatch(candidate.name)
    ):
        raise ManifestError(f"unsupported empirical analysis path: {raw}")
    return Path(*candidate.parts)


# Results-pipeline artifacts that the stage doc derives from each analysis
# stem by replacing ".md" (RESULT_PLAN / RESULT_BUNDLE / RESULT_RECEIPT).
# They necessarily share the analysis-name prefix and are first-class
# evidence, not namespace pollution. Longest suffixes first.
_RESULT_SIBLING_SUFFIXES = (
    "_results.receipt.json",
    "_results.plan.json",
    "_results.json",
)
_EXECUTION_SIBLING_SUFFIX = "_execution.json"


def _is_analysis_results_sibling(name: str) -> bool:
    for suffix in _RESULT_SIBLING_SUFFIXES:
        if name.endswith(suffix):
            stem = name[: -len(suffix)]
            return ANALYSIS_NAME.fullmatch(f"{stem}.md") is not None
    return False


def _is_analysis_execution_sibling(name: str) -> bool:
    if not name.endswith(_EXECUTION_SIBLING_SUFFIX):
        return False
    stem = name[: -len(_EXECUTION_SIBLING_SUFFIX)]
    return ANALYSIS_NAME.fullmatch(f"{stem}.md") is not None


def artifact_paths(analysis_path: Path) -> dict[str, str]:
    analysis_path = _validated_analysis_path(analysis_path)
    stem = analysis_path.stem
    suffix = stem.removeprefix("empirical_analysis")
    return {
        "analysis": analysis_path.as_posix(),
        "verify_script": f"output/stage3a/verification/empirics_verify{suffix}.py",
        "verify_result": f"output/stage3a/empirics_verify_result{suffix}.json",
        "pass_candidate": f"output/stage3a/empirics_verify_result{suffix}.json.candidate",
    }


def _code_surface(project_root: Path) -> list[Path]:
    """Return every regular file under code/."""
    code_root = project_root / "code"
    _regular_file_bytes(code_root / "empirical.py", project_root)
    discovered: list[Path] = []
    def fail_walk(error: OSError) -> None:
        raise ManifestError(f"cannot enumerate complete code surface: {error}")

    for directory, names, filenames in os.walk(
        code_root, followlinks=False, onerror=fail_walk
    ):
        directory_path = Path(directory)
        for name in names:
            child = directory_path / name
            if child.is_symlink():
                relative = child.relative_to(project_root).as_posix()
                raise ManifestError(f"input path contains a symlink: {relative}")
        for name in filenames:
            child = directory_path / name
            _regular_file_bytes(child, project_root)
            discovered.append(child)
    return sorted(discovered, key=lambda path: path.relative_to(project_root).as_posix())


def _validate_verification_namespace(project_root: Path) -> None:
    """Verifier programs are self-contained files; reject hidden dependencies."""
    verification_root = project_root / "output" / "stage3a" / "verification"
    try:
        entries = list(verification_root.iterdir())
    except (FileNotFoundError, NotADirectoryError, PermissionError) as exc:
        raise ManifestError(f"cannot enumerate verification namespace: {exc}") from exc
    for entry in entries:
        relative = entry.relative_to(project_root).as_posix()
        metadata = entry.lstat()
        if entry.name == "__pycache__" and stat.S_ISDIR(metadata.st_mode):
            # An execution byproduct of running/importing a verifier, not a
            # hidden dependency: verifiers never read bytecode caches.
            continue
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISREG(metadata.st_mode)
            or VERIFIER_NAME.fullmatch(entry.name) is None
        ):
            raise ManifestError(
                f"verification namespace contains a dependency or invalid artifact: {relative}"
            )


def _markdown_headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return ATX headings outside CommonMark fenced code blocks."""
    headings: list[tuple[int, int, str]] = []
    fence_character: str | None = None
    fence_length = 0
    for index, line in enumerate(lines):
        content = line.rstrip("\n")
        if fence_character is not None:
            closing = rf"^ {{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*$"
            if re.match(closing, content):
                fence_character = None
                fence_length = 0
            continue
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content)
        if fence and (fence.group(1)[0] != "`" or "`" not in fence.group(2)):
            fence_character = fence.group(1)[0]
            fence_length = len(fence.group(1))
            continue
        heading = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$", content)
        if heading:
            title = (heading.group(2) or "").strip()
            title = re.sub(r"[ \t]+#+[ \t]*$", "", title)
            headings.append((index, len(heading.group(1)), title))
    return headings


def _headline_section(raw: bytes, report_path: Path) -> bytes:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ManifestError(f"report is not UTF-8: {report_path.as_posix()}") from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines(keepends=True)
    starts = [
        index
        for index, level, title in _markdown_headings(lines)
        if level == 2 and title == "Headline claims"
    ]
    if not starts:
        raise ManifestError(f"missing '## Headline claims' section in {report_path.as_posix()}")
    if len(starts) > 1:
        raise ManifestError(f"multiple '## Headline claims' sections in {report_path.as_posix()}")
    start = starts[0]
    end = len(lines)
    for index, level, _title in _markdown_headings(lines):
        if index > start and level <= 2:
            end = index
            break
    # Normalize only newline representation.  Whitespace and wording remain
    # binding so normalization cannot hide a substantive edit.
    return "".join(lines[start:end]).encode("utf-8")


def _headline_entries(section: bytes, report_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw_line in section.decode("utf-8").splitlines():
        if "[HEADLINE]" not in raw_line:
            continue
        match = re.search(r"\[claim_id:\s*([a-z][a-z0-9_]*)\s*\]", raw_line)
        if match is None:
            raise ManifestError(
                f"headline row lacks a snake_case claim_id in {report_path.as_posix()}"
            )
        claim_id = match.group(1)
        if claim_id in seen:
            raise ManifestError(f"duplicate headline claim_id: {claim_id}")
        seen.add(claim_id)
        claim_text = raw_line.strip()
        value_match = re.search(
            r"\[reported_value:\s*([-+]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?)\s*\]",
            raw_line,
        )
        if value_match is None:
            raise ManifestError(f"headline claim {claim_id} lacks [reported_value: ...]")
        reported_value = float(value_match.group(1))
        if not math.isfinite(reported_value):
            raise ManifestError(f"headline claim {claim_id} has non-finite reported_value")
        tolerance_match = re.search(
            r"\[tolerance_class:\s*([a-z][a-z0-9_]*)\s*\]", raw_line
        )
        if tolerance_match is None or tolerance_match.group(1) not in TOLERANCE_CLASSES:
            raise ManifestError(
                f"headline claim {claim_id} lacks a valid [tolerance_class: ...]"
            )
        entries.append(
            {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "reported_value": reported_value,
                "tolerance_class": tolerance_match.group(1),
            }
        )
    if not entries:
        raise ManifestError(f"headline section has no [HEADLINE] rows in {report_path.as_posix()}")
    return entries[:8]


def build_manifest(project_root: Path, analysis_path: Path = DEFAULT_REPORT) -> dict[str, Any]:
    project_root = project_root.resolve()
    analysis_path = _validated_analysis_path(analysis_path)
    report_path = project_root / analysis_path
    files: dict[str, str] = {}
    for source in _code_surface(project_root):
        relative = source.relative_to(project_root).as_posix()
        files[relative] = _sha256(_regular_file_bytes(source, project_root))
    headline_section = _headline_section(
        _regular_file_bytes(report_path, project_root), analysis_path
    )
    headline_digest = _sha256(headline_section)
    verifier = artifact_paths(analysis_path)
    _validate_verification_namespace(project_root)
    verifier_path = Path(verifier["verify_script"])
    verifier_digest = _sha256(
        _regular_file_bytes(project_root / verifier_path, project_root)
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "algorithm": ALGORITHM,
        "code_files": files,
        "headline_claims": {
            "path": analysis_path.as_posix(),
            "sha256": headline_digest,
            "entries": _headline_entries(headline_section, analysis_path),
        },
        "verification_script": {
            "path": verifier_path.as_posix(),
            "sha256": verifier_digest,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["combined_sha256"] = _sha256(canonical)
    return payload


def _validate_manifest(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError("input_manifest must be a JSON object")
    if value.get("schema_version") != SCHEMA_VERSION or value.get("algorithm") != ALGORITHM:
        raise ManifestError("unsupported input_manifest schema or algorithm")
    if not isinstance(value.get("code_files"), dict):
        raise ManifestError("input_manifest.code_files must be an object")
    if not value["code_files"] or any(
        not isinstance(path, str) or not isinstance(digest, str)
        for path, digest in value["code_files"].items()
    ):
        raise ManifestError("input_manifest.code_files entries are malformed")
    headline = value.get("headline_claims")
    if (
        not isinstance(headline, dict)
        or not isinstance(headline.get("sha256"), str)
        or not isinstance(headline.get("entries"), list)
        or not headline["entries"]
    ):
        raise ManifestError("input_manifest.headline_claims is malformed")
    _validated_analysis_path(headline.get("path"))
    entry_ids: set[str] = set()
    for entry in headline["entries"]:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("claim_id"), str)
            or not isinstance(entry.get("claim_text"), str)
            or not entry["claim_text"]
            or isinstance(entry.get("reported_value"), bool)
            or not isinstance(entry.get("reported_value"), (int, float))
            or not math.isfinite(entry["reported_value"])
            or entry.get("tolerance_class") not in TOLERANCE_CLASSES
            or entry["claim_id"] in entry_ids
        ):
            raise ManifestError("input_manifest headline entry is malformed")
        entry_ids.add(entry["claim_id"])
    verifier = value.get("verification_script")
    expected_verifier = artifact_paths(Path(headline["path"]))["verify_script"]
    if (
        not isinstance(verifier, dict)
        or verifier.get("path") != expected_verifier
        or not isinstance(verifier.get("sha256"), str)
    ):
        raise ManifestError("input_manifest.verification_script is malformed")
    if not isinstance(value.get("combined_sha256"), str):
        raise ManifestError("input_manifest.combined_sha256 is missing")
    digests = [
        *value["code_files"].values(),
        headline["sha256"],
        verifier["sha256"],
        value["combined_sha256"],
    ]
    if any(len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest) for digest in digests):
        raise ManifestError("input_manifest contains a malformed SHA-256 digest")
    payload = {key: item for key, item in value.items() if key != "combined_sha256"}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if _sha256(canonical) != value["combined_sha256"]:
        raise ManifestError("input_manifest combined digest does not match its contents")
    return value


def _validate_pass_claims(
    result: dict[str, Any],
    expected_entries: list[dict[str, Any]],
) -> None:
    claims = result.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ManifestError("PASS replicator result must contain at least one claim")
    valid_path_classes = {
        "different_merge_key",
        "different_aggregation_order",
        "raw_source_not_cache",
        "alternative_estimator_package",
        "no_alternative_path_exists",
    }
    expected_ids = [entry["claim_id"] for entry in expected_entries]
    if [claim.get("claim_id") if isinstance(claim, dict) else None for claim in claims] != expected_ids:
        raise ManifestError("replicator PASS claims do not exactly match headline claim_ids")
    for claim, expected in zip(claims, expected_entries):
        if not isinstance(claim, dict):
            raise ManifestError("replicator PASS claim row must be an object")
        claim_id = claim.get("claim_id")
        if claim.get("claim_text") != expected["claim_text"]:
            raise ManifestError(f"replicator PASS claim_text does not match {claim_id}")
        if claim.get("agree") is not True or claim.get("path_class") not in valid_path_classes:
            raise ManifestError("replicator PASS claim is unagreed or has an invalid path_class")
        for field in ("reported_value", "replicated_value", "relative_delta"):
            number = claim.get(field)
            if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(number):
                raise ManifestError(f"replicator PASS claim has invalid {field}")
        reported = float(claim["reported_value"])
        replicated = float(claim["replicated_value"])
        if reported != float(expected["reported_value"]):
            raise ManifestError(f"replicator reported_value does not match headline {claim_id}")
        computed_relative_delta = abs(replicated - reported) / max(abs(reported), 1e-15)
        if float(claim["relative_delta"]) != computed_relative_delta:
            raise ManifestError(f"replicator relative_delta is inconsistent for {claim_id}")
        tolerance_class = claim.get("tolerance_class")
        raw_tolerance = claim.get("tolerance")
        if (
            tolerance_class != expected["tolerance_class"]
            or tolerance_class not in TOLERANCE_CLASSES
            or isinstance(raw_tolerance, bool)
            or not isinstance(raw_tolerance, (int, float))
            or not math.isfinite(raw_tolerance)
        ):
            raise ManifestError(f"replicator tolerance_class is invalid for {claim_id}")
        tolerance_type, tolerance = TOLERANCE_CLASSES[tolerance_class]
        if claim.get("tolerance_type") != tolerance_type or not math.isclose(
            float(raw_tolerance), tolerance, rel_tol=0, abs_tol=0
        ):
            raise ManifestError(f"replicator tolerance is invalid for {claim_id}")
        observed_delta = (
            computed_relative_delta
            if tolerance_type == "relative"
            else abs(replicated - reported)
        )
        if observed_delta > tolerance:
            raise ManifestError(f"replicator agree is inconsistent with tolerance for {claim_id}")
        if not isinstance(claim.get("path_description"), str) or not claim["path_description"]:
            raise ManifestError("replicator PASS claim lacks path_description")
    warnings = result.get("untagged_warnings")
    if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
        raise ManifestError("replicator result untagged_warnings must be a string array")
    run_payload = {
        "claims": [
            {
                "claim_id": claim["claim_id"],
                "replicated_value": float(claim["replicated_value"]),
            }
            for claim in claims
        ]
    }
    expected_run_digest = _sha256(
        json.dumps(run_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    if result.get("verification_run_sha256") != expected_run_digest:
        raise ManifestError("replicator PASS does not match its finalized verifier run")


def finalize_pass(
    project_root: Path,
    analysis_path: Path,
    candidate_path: Path,
    result_path: Path,
) -> dict[str, Any]:
    """Run the verifier once and atomically derive, rather than trust, a PASS."""
    project_root = project_root.resolve()
    analysis_path = _validated_analysis_path(analysis_path)
    derived = artifact_paths(analysis_path)
    expected_result = Path(derived["verify_result"])
    expected_candidate = Path(derived["pass_candidate"])
    supplied_result = result_path if not result_path.is_absolute() else result_path.relative_to(project_root)
    if supplied_result != expected_result:
        raise ManifestError(
            f"result path must be the derived per-analysis path {expected_result.as_posix()}"
        )
    supplied_candidate = (
        candidate_path
        if not candidate_path.is_absolute()
        else candidate_path.relative_to(project_root)
    )
    if supplied_candidate != expected_candidate:
        raise ManifestError(
            f"candidate path must be the derived per-analysis path {expected_candidate.as_posix()}"
        )
    candidate_absolute = project_root / expected_candidate
    destination = project_root / expected_result
    if candidate_absolute == destination:
        raise ManifestError("PASS candidate path must differ from the final result path")
    try:
        candidate = json.loads(_regular_file_bytes(candidate_absolute, project_root))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"PASS candidate is not valid JSON: {exc}") from exc
    if not isinstance(candidate, dict):
        raise ManifestError("PASS candidate must be a JSON object")
    evidence = candidate.get("path_evidence")
    warnings = candidate.get("untagged_warnings", [])
    if not isinstance(evidence, list) or not isinstance(warnings, list) or any(
        not isinstance(item, str) for item in warnings
    ):
        raise ManifestError("PASS candidate path_evidence/warnings are malformed")

    verifier_relative = Path(derived["verify_script"])
    verifier_absolute = project_root / verifier_relative
    _regular_file_bytes(verifier_absolute, project_root)
    manifest_before_run = build_manifest(project_root, analysis_path)
    try:
        completed = subprocess.run(
            [sys.executable, "-B", str(verifier_absolute)],
            cwd=project_root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,
        )
    except subprocess.TimeoutExpired as exc:
        raise ManifestError("verification script exceeded the 600-second finalization timeout") from exc
    if completed.returncode != 0:
        diagnostic = completed.stderr.decode("utf-8", errors="replace").strip()[-500:]
        raise ManifestError(
            f"verification script exited {completed.returncode}"
            + (f": {diagnostic}" if diagnostic else "")
        )
    try:
        run = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ManifestError("verification script stdout is not one JSON object") from exc
    run_claims = run.get("claims") if isinstance(run, dict) else None
    if not isinstance(run_claims, list):
        raise ManifestError("verification script stdout lacks a claims array")

    manifest = build_manifest(project_root, analysis_path)
    if manifest["combined_sha256"] != manifest_before_run["combined_sha256"]:
        raise ManifestError(
            "verification execution changed a bound code/headline/verifier input; "
            "rerun only after inputs are stable"
        )
    entries = manifest["headline_claims"]["entries"]
    expected_ids = [entry["claim_id"] for entry in entries]
    if [item.get("claim_id") if isinstance(item, dict) else None for item in run_claims] != expected_ids:
        raise ManifestError("verification script claims do not exactly match headline claim_ids")
    if [item.get("claim_id") if isinstance(item, dict) else None for item in evidence] != expected_ids:
        raise ManifestError("PASS candidate evidence does not exactly match headline claim_ids")

    claims: list[dict[str, Any]] = []
    valid_path_classes = {
        "different_merge_key",
        "different_aggregation_order",
        "raw_source_not_cache",
        "alternative_estimator_package",
        "no_alternative_path_exists",
    }
    canonical_run_claims: list[dict[str, Any]] = []
    for entry, run_claim, path_evidence in zip(entries, run_claims, evidence):
        replicated = run_claim.get("replicated_value")
        if isinstance(replicated, bool) or not isinstance(replicated, (int, float)) or not math.isfinite(replicated):
            raise ManifestError(f"verification script emitted invalid replicated_value for {entry['claim_id']}")
        if (
            path_evidence.get("path_class") not in valid_path_classes
            or not isinstance(path_evidence.get("path_description"), str)
            or not path_evidence["path_description"]
        ):
            raise ManifestError(f"PASS candidate has invalid path evidence for {entry['claim_id']}")
        reported = float(entry["reported_value"])
        replicated = float(replicated)
        relative_delta = abs(replicated - reported) / max(abs(reported), 1e-15)
        tolerance_class = entry["tolerance_class"]
        tolerance_type, tolerance = TOLERANCE_CLASSES[tolerance_class]
        observed_delta = relative_delta if tolerance_type == "relative" else abs(replicated - reported)
        if observed_delta > tolerance:
            raise ManifestError(f"verification disagreement exceeds tolerance for {entry['claim_id']}")
        canonical_run_claims.append(
            {"claim_id": entry["claim_id"], "replicated_value": replicated}
        )
        claims.append(
            {
                "claim_id": entry["claim_id"],
                "claim_text": entry["claim_text"],
                "reported_value": reported,
                "replicated_value": replicated,
                "relative_delta": relative_delta,
                "agree": True,
                "tolerance_class": tolerance_class,
                "tolerance": tolerance,
                "tolerance_type": tolerance_type,
                "path_description": path_evidence["path_description"],
                "path_class": path_evidence["path_class"],
            }
        )
    run_payload = {"claims": canonical_run_claims}
    run_digest = _sha256(
        json.dumps(run_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    result = {
        "verdict": "PASS",
        "finalized_by": "empirical_input_manifest.py",
        "verification_run_sha256": run_digest,
        "input_manifest": manifest,
        "claims": claims,
        "untagged_warnings": warnings,
    }
    _validate_pass_claims(result, entries)
    candidate_absolute.unlink()
    current_parent = project_root
    for part in expected_result.parent.parts:
        current_parent /= part
        try:
            metadata = current_parent.lstat()
        except FileNotFoundError as exc:
            raise ManifestError(
                f"result parent is missing: {expected_result.parent.as_posix()}"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ManifestError(
                f"result parent is not a real directory: {expected_result.parent.as_posix()}"
            )
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
            json.dump(result, temporary, indent=2, sort_keys=True)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_name, destination)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass
    return {"status": "FINALIZED", "result": expected_result.as_posix(), **result}


def compare_result(
    project_root: Path,
    result_path: Path,
    expected_analysis: Path | None = None,
) -> dict[str, Any]:
    absolute_result = result_path if result_path.is_absolute() else project_root / result_path
    try:
        result = json.loads(_regular_file_bytes(absolute_result, project_root.resolve()))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"replicator result is not valid JSON: {exc}") from exc
    if not isinstance(result, dict) or result.get("verdict") != "PASS":
        raise ManifestError("replicator result does not record verdict PASS")
    if result.get("finalized_by") != "empirical_input_manifest.py":
        raise ManifestError("replicator PASS was not finalized by the manifest utility")
    expected = _validate_manifest(result.get("input_manifest"))
    _validate_pass_claims(result, expected["headline_claims"]["entries"])
    stored_analysis = _validated_analysis_path(expected["headline_claims"]["path"])
    if expected_analysis is not None:
        required_analysis = _validated_analysis_path(expected_analysis)
        if stored_analysis != required_analysis:
            raise ManifestError(
                "input_manifest covers "
                f"{stored_analysis.as_posix()}, not required {required_analysis.as_posix()}"
            )
    current = build_manifest(project_root, stored_analysis)
    expected_files = expected["code_files"]
    current_files = current["code_files"]
    changed_files = sorted(
        path
        for path in set(expected_files) | set(current_files)
        if expected_files.get(path) != current_files.get(path)
    )
    headline_changed = (
        expected["headline_claims"]["sha256"]
        != current["headline_claims"]["sha256"]
    )
    verifier_changed = (
        expected["verification_script"]["sha256"]
        != current["verification_script"]["sha256"]
    )
    unchanged = expected["combined_sha256"] == current["combined_sha256"]
    return {
        "status": "UNCHANGED" if unchanged else "CHANGED",
        "expected_sha256": expected["combined_sha256"],
        "current_sha256": current["combined_sha256"],
        "changed_code_files": changed_files,
        "headline_claims_changed": headline_changed,
        "verification_script_changed": verifier_changed,
    }


def _results_inventory(project_root: Path) -> list[dict[str, Any]]:
    """Query the canonical validator in an import-isolated, bytecode-free process."""
    utility = project_root / "code" / "utils" / "results_pipeline" / "results_pipeline.py"
    _regular_file_bytes(utility, project_root)
    try:
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                str(utility),
                "inspect-registry",
                "--project-root",
                str(project_root),
                "--artifact-prefix",
                "output/stage3a/empirical_analysis",
            ],
            cwd=project_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ManifestError(f"cannot run canonical results contract: {exc}") from exc
    if completed.returncode != 0:
        diagnostic = completed.stderr.strip() or completed.stdout.strip()
        raise ManifestError(
            f"canonical results contract rejected lifecycle evidence: {diagnostic}"
        )
    try:
        inventory = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ManifestError("canonical results contract returned malformed JSON") from exc
    if (
        not isinstance(inventory, dict)
        or set(inventory) != {"receipts"}
        or not isinstance(inventory["receipts"], list)
    ):
        raise ManifestError("canonical results contract returned malformed inventory")
    return inventory["receipts"]


def _analysis_lifecycle(
    project_root: Path,
) -> tuple[
    dict[Path, dict[str, str]],
    dict[str, tuple[Path, str]],
    set[str],
]:
    """Resolve analysis and result-sibling ownership through the canonical contract."""
    try:
        lifecycle: dict[Path, dict[str, str]] = {}
        declared_results: dict[str, tuple[Path, str]] = {}
        receipt_paths: set[str] = set()
        for receipt in _results_inventory(project_root):
            receipt_raw = receipt["receipt"]
            state = receipt["lifecycle"]
            referenced_paths = receipt["referenced_paths"]
            if not isinstance(referenced_paths, list) or any(
                not isinstance(path, str) for path in referenced_paths
            ):
                raise ManifestError(
                    f"canonical results contract returned malformed path inventory: "
                    f"{receipt_raw}"
                )
            receipt_paths.update(referenced_paths)
            execution_summary_paths = receipt["execution_summary_paths"]
            if not isinstance(execution_summary_paths, list) or any(
                not isinstance(path, str) for path in execution_summary_paths
            ):
                raise ManifestError(
                    f"canonical results contract returned malformed execution-summary "
                    f"inventory: {receipt_raw}"
                )
            if (
                receipt["pending_supersedes"] is not None
                and receipt["receipt_supersedes"] != receipt["pending_supersedes"]
            ):
                raise ManifestError(
                    f"pending registry/receipt supersedes mismatch: {receipt_raw}"
                )
            empirical_artifacts: list[tuple[Path, dict[str, Any]]] = []
            empirical_execution_artifacts: list[tuple[Path, dict[str, Any]]] = []
            for artifact_entry in receipt["artifacts"]:
                artifact = artifact_entry["recorded"]
                raw_path = artifact["path"]
                candidate = PurePosixPath(raw_path)
                if (
                    candidate.parts[:2] == ("output", "stage3a")
                    and len(candidate.parts) == 3
                    and ANALYSIS_NAME.fullmatch(candidate.name)
                ):
                    empirical_artifacts.append(
                        (_validated_analysis_path(raw_path), artifact_entry)
                    )
                elif (
                    candidate.parts[:2] == ("output", "stage3a")
                    and len(candidate.parts) == 3
                    and _is_analysis_execution_sibling(candidate.name)
                ):
                    empirical_execution_artifacts.append(
                        (Path(*candidate.parts), artifact_entry)
                    )
                elif raw_path.startswith("output/stage3a/empirical_analysis"):
                    raise ManifestError(
                        f"receipt artifact occupies the reserved analysis namespace: {raw_path}"
                    )
            if not empirical_artifacts:
                continue
            if len(empirical_artifacts) != 1:
                raise ManifestError(
                    f"result receipt owns multiple empirical analyses: {receipt_raw}"
                )
            analysis_path, artifact_entry = empirical_artifacts[0]
            if artifact_entry["current"] != artifact_entry["recorded"]:
                raise ManifestError(
                    f"receipt analysis fingerprint does not match current bytes: "
                    f"{analysis_path.as_posix()}"
                )
            if analysis_path in lifecycle:
                prior = lifecycle[analysis_path]["receipt"]
                raise ManifestError(
                    f"analysis is owned by multiple result receipts: "
                    f"{analysis_path.as_posix()} ({prior}, {receipt_raw})"
                )
            lifecycle[analysis_path] = {
                "lifecycle": state,
                "receipt": receipt_raw,
            }
            expected_execution = analysis_path.with_name(
                analysis_path.stem + _EXECUTION_SIBLING_SUFFIX
            )
            for execution_path, artifact_entry in empirical_execution_artifacts:
                if execution_path != expected_execution:
                    raise ManifestError(
                        "receipt execution summary does not match its empirical analysis: "
                        f"{execution_path.as_posix()}"
                    )
                if execution_summary_paths.count(execution_path.as_posix()) != 1:
                    raise ManifestError(
                        "receipt execution summary is not uniquely declared by v3 lineage: "
                        f"{execution_path.as_posix()}"
                    )
                if artifact_entry["current"] != artifact_entry["recorded"]:
                    raise ManifestError(
                        "receipt execution-summary fingerprint does not match current bytes: "
                        f"{execution_path.as_posix()}"
                    )
            for label in ("plan", "bundle"):
                if receipt[label]["current"] != receipt[label]["recorded"]:
                    raise ManifestError(
                        f"receipt {label} fingerprint does not match current bytes: "
                        f"{receipt[label]['recorded']['path']}"
                    )
            owned_results = [
                (receipt_raw, "receipt"),
                (receipt["plan"]["recorded"]["path"], "plan"),
                (receipt["bundle"]["recorded"]["path"], "bundle"),
                *(
                    (path.as_posix(), "execution")
                    for path, _ in empirical_execution_artifacts
                ),
            ]
            for result_path, role in owned_results:
                prior_owner = declared_results.get(result_path)
                owner = (analysis_path, role)
                if prior_owner is not None and prior_owner != owner:
                    raise ManifestError(
                        f"result artifact has conflicting empirical receipt ownership: "
                        f"{result_path}"
                    )
                declared_results[result_path] = owner
        return lifecycle, declared_results, receipt_paths
    except ManifestError:
        raise
    except Exception as exc:
        raise ManifestError(f"canonical results contract rejected lifecycle evidence: {exc}") from exc


def _check_all_locked(project_root: Path) -> dict[str, Any]:
    stage_root = project_root / "output" / "stage3a"
    analyses: list[Path] = []
    artifact_errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    try:
        stage_metadata = stage_root.lstat()
        if stat.S_ISLNK(stage_metadata.st_mode) or not stat.S_ISDIR(stage_metadata.st_mode):
            raise ManifestError("Stage 3a artifact namespace is not a real directory")
    except (ManifestError, OSError) as exc:
        return {
            "status": "CHANGED",
            "analyses": [],
            "warnings": [],
            "artifact_errors": [
                {
                    "path": "output/stage3a",
                    "error": f"cannot enumerate Stage 3a artifact namespace: {exc}",
                }
            ],
        }
    try:
        lifecycle, declared_results, receipt_paths = _analysis_lifecycle(project_root)
    except (ManifestError, OSError) as exc:
        return {
            "status": "CHANGED",
            "analyses": [],
            "warnings": [],
            "artifact_errors": [
                {
                    "path": RESULTS_REGISTRY.as_posix(),
                    "error": f"cannot resolve analysis lifecycle: {exc}",
                }
            ],
        }
    try:
        stage_entries = sorted(stage_root.iterdir())
    except OSError as exc:
        return {
            "status": "CHANGED",
            "analyses": [],
            "warnings": [],
            "artifact_errors": [
                {
                    "path": "output/stage3a",
                    "error": f"cannot enumerate Stage 3a artifact namespace: {exc}",
                }
            ],
        }
    for candidate in (
        entry for entry in stage_entries if entry.name.startswith("empirical_analysis")
    ):
        if (
            _is_analysis_results_sibling(candidate.name)
            or _is_analysis_execution_sibling(candidate.name)
        ):
            # A declared RESULT_PLAN/BUNDLE/RECEIPT triple is owned by the
            # results pipeline's receipt checks.  A regular plan can also be
            # present before its runner publishes anything, or remain after a
            # pre-publication failure.  It is inert without a receipt, so
            # report that state without blocking unrelated live analyses.
            # Undeclared bundles/receipts and every non-regular object remain
            # namespace pollution.
            relative = candidate.relative_to(project_root)
            try:
                metadata = candidate.lstat()
                for suffix in (*_RESULT_SIBLING_SUFFIXES, _EXECUTION_SIBLING_SUFFIX):
                    if candidate.name.endswith(suffix):
                        analysis_name = candidate.name[: -len(suffix)] + ".md"
                        matched_suffix = suffix
                        break
                analysis_path = relative.parent / analysis_name
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                    raise ManifestError(
                        "analysis results artifact is not a real regular file"
                    )
                owner = declared_results.get(relative.as_posix())
                if (
                    owner is None
                    and matched_suffix == "_results.plan.json"
                    and relative.as_posix() not in receipt_paths
                ):
                    warnings.append(
                        {
                            "path": relative.as_posix(),
                            "warning": (
                                "unbound pre-publication plan is not live result evidence"
                            ),
                        }
                    )
                    continue
                expected_role = {
                    "_results.receipt.json": "receipt",
                    "_results.plan.json": "plan",
                    "_results.json": "bundle",
                    _EXECUTION_SIBLING_SUFFIX: "execution",
                }[matched_suffix]
                if owner != (analysis_path, expected_role):
                    raise ManifestError(
                        "analysis results artifact is not declared in its expected "
                        "receipt role"
                    )
            except (ManifestError, OSError) as exc:
                artifact_errors.append(
                    {"path": relative.as_posix(), "error": str(exc)}
                )
            continue
        relative = candidate.relative_to(project_root)
        try:
            metadata = candidate.lstat()
            validated = _validated_analysis_path(relative)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise ManifestError("analysis artifact is not a real regular file")
            if validated not in lifecycle:
                raise ManifestError(
                    "analysis artifact is absent from result-registry receipt artifacts"
                )
            analyses.append(validated)
        except (ManifestError, OSError) as exc:
            artifact_errors.append(
                {
                    "path": relative.as_posix(),
                    "error": str(exc),
                }
            )
    if not analyses and not artifact_errors:
        raise ManifestError("no empirical analysis files found")
    checks: list[dict[str, Any]] = []
    all_unchanged = not artifact_errors
    expected_results: set[str] = set()
    expected_scripts: set[str] = set()
    for analysis in analyses:
        paths = artifact_paths(analysis)
        expected_results.add(paths["verify_result"])
        expected_scripts.add(paths["verify_script"])
        lifecycle_entry = lifecycle[analysis]
        if lifecycle_entry["lifecycle"] == "retired":
            checks.append(
                {
                    **paths,
                    **lifecycle_entry,
                    "status": "EXCLUDED_RETIRED",
                }
            )
            continue
        try:
            comparison = compare_result(
                project_root,
                Path(paths["verify_result"]),
                analysis,
            )
            status = comparison["status"]
            entry = {**paths, **lifecycle_entry, **comparison}
        except (ManifestError, OSError) as exc:
            status = "ERROR"
            entry = {
                **paths,
                **lifecycle_entry,
                "status": status,
                "error": str(exc),
            }
        all_unchanged = all_unchanged and status == "UNCHANGED"
        checks.append(entry)
    # A "<verify_result>.candidate" is finalize-pass's documented intermediate:
    # written on replicator PASS, unlinked on successful finalization, and
    # legitimately present between those two points (or after a failed
    # finalize, which the per-analysis ERROR entry already surfaces).
    expected_candidates = {f"{result}.candidate" for result in expected_results}
    for candidate in (
        entry for entry in stage_entries if entry.name.startswith("empirics_verify_result")
    ):
        relative = candidate.relative_to(project_root).as_posix()
        try:
            metadata = candidate.lstat()
            regular = stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
        except OSError:
            regular = False
        if (
            relative not in expected_results and relative not in expected_candidates
        ) or not regular:
            artifact_errors.append(
                {"path": relative, "error": "orphan or invalid verifier result artifact"}
            )
            all_unchanged = False
    verification_root = stage_root / "verification"
    if verification_root.is_symlink() or (
        verification_root.exists() and not verification_root.is_dir()
    ):
        artifact_errors.append(
            {
                "path": verification_root.relative_to(project_root).as_posix(),
                "error": "verification artifact namespace is not a real directory",
            }
        )
        all_unchanged = False
    elif verification_root.is_dir():
        try:
            verification_entries = sorted(verification_root.iterdir())
        except OSError as exc:
            artifact_errors.append(
                {
                    "path": verification_root.relative_to(project_root).as_posix(),
                    "error": f"cannot enumerate verification artifact namespace: {exc}",
                }
            )
            all_unchanged = False
            verification_entries = []
        for candidate in verification_entries:
            relative = candidate.relative_to(project_root).as_posix()
            try:
                metadata = candidate.lstat()
                regular = stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode)
                if candidate.name == "__pycache__" and stat.S_ISDIR(metadata.st_mode):
                    continue
            except OSError:
                regular = False
            if (
                relative not in expected_scripts
                or VERIFIER_NAME.fullmatch(candidate.name) is None
                or not regular
            ):
                artifact_errors.append(
                    {"path": relative, "error": "orphan or invalid verifier script artifact"}
                )
                all_unchanged = False
    return {
        "status": "UNCHANGED" if all_unchanged else "CHANGED",
        "analyses": checks,
        "warnings": warnings,
        "artifact_errors": artifact_errors,
    }


def check_all(
    project_root: Path,
    emit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Check all analyses under one shared lease, including optional emission."""
    project_root = project_root.resolve()
    try:
        with _results_read_lock(project_root):
            output = _check_all_locked(project_root)
            if emit is not None:
                emit(output)
            return output
    except (ManifestError, OSError) as exc:
        output = {
            "status": "CHANGED",
            "analyses": [],
            "warnings": [],
            "artifact_errors": [
                {
                    "path": RESULTS_LOCK.as_posix(),
                    "error": f"cannot hold stable analysis lifecycle: {exc}",
                }
            ],
        }
        if emit is not None:
            emit(output)
        return output


def _emit_json(output: dict[str, Any]) -> None:
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    sys.stdout.flush()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot = subparsers.add_parser("snapshot", help="print the current input manifest")
    snapshot.add_argument("--analysis", type=Path, default=DEFAULT_REPORT)
    paths = subparsers.add_parser("paths", help="print per-analysis verifier artifact paths")
    paths.add_argument("--analysis", type=Path, default=DEFAULT_REPORT)
    compare = subparsers.add_parser("compare", help="compare current inputs with a replicator result")
    compare.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    compare.add_argument("--analysis", type=Path, help="require the result to cover this analysis file")
    finalize = subparsers.add_parser(
        "finalize-pass", help="run the verifier and atomically derive a validated PASS result"
    )
    finalize.add_argument("--analysis", type=Path, default=DEFAULT_REPORT)
    finalize.add_argument("--candidate", type=Path, required=True)
    finalize.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    subparsers.add_parser("check-all", help="check every canonical/versioned empirical analysis")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            output = build_manifest(args.project_root, args.analysis)
        elif args.command == "paths":
            output = artifact_paths(args.analysis)
        elif args.command == "compare":
            output = compare_result(args.project_root.resolve(), args.result, args.analysis)
        elif args.command == "finalize-pass":
            output = finalize_pass(
                args.project_root, args.analysis, args.candidate, args.result
            )
        else:
            check_all(args.project_root.resolve(), emit=_emit_json)
            return 0
    except (ManifestError, OSError) as exc:
        print(f"empirical_input_manifest: {exc}", file=sys.stderr)
        return 2
    _emit_json(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
