#!/usr/bin/env python3
"""Finalize and verify paper-facing result bundles and rendered exhibits.

The utility deliberately does not prescribe table layouts or plotting libraries.
It records the actual analysis/render commands, fingerprints declared inputs and
outputs, and fails closed when any recorded byte becomes stale.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import select
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


RECEIPT_VERSION = 1
RUN_PLAN_VERSION = 1
PAPER_RECEIPT_VERSION = 2
REGISTRY_VERSION = 1
AUDIT_INPUT_VERSION = 1
REGISTRY_PATH = "process_log/results_registry.json"
PAPER_RECEIPT_PATH = "process_log/paper_evidence.receipt.json"
LOCK_PATH = "process_log/results_pipeline.lock"
TRANSACTION_PATH = "process_log/results_pipeline.transaction.json"
TRANSACTION_BACKUP_PATH = "process_log/.results_pipeline-transaction-backup"
AUDIT_NAMESPACE = "output/evidence"
RESULT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
FORBIDDEN_PARTS = {".env"}
CITATION_COMMANDS = {
    "cite", "cites", "parencite", "parencites", "textcite", "textcites",
    "footcite", "footcites", "footcitetext", "smartcite", "smartcites",
    "supercite", "autocite", "autocites", "fullcite", "footfullcite",
    "citeauthor", "citetitle", "citeyear", "citedate", "citeurl", "citefield",
    "volcite", "volcites", "pvolcite", "pvolcites", "fvolcite", "fvolcites",
    "ftvolcite", "ftvolcites", "svolcite", "svolcites", "tvolcite", "tvolcites",
    "avolcite", "avolcites", "citep", "citet", "citealp", "citealt",
    "citeyearpar", "citenum",
}
CITATION_RE = re.compile(
    r"\\(?P<command>" + "|".join(
        sorted((re.escape(item) for item in CITATION_COMMANDS), key=len, reverse=True)
    ) + r")\*?(?![A-Za-z])"
    r"(?P<arguments>(?:(?:\s*\[[^\]]*\]){0,2}\s*\{[^}]+\})+)",
    flags=re.IGNORECASE,
)
CITATION_FAMILY_RE = re.compile(r"\\(?P<command>[A-Za-z@]*cite[A-Za-z@]*)\*?")
CITE_KEY_RE = re.compile(r"^[A-Za-z0-9_:.+/-]+$")
NON_OCCURRENCE_CITATION_COMMANDS = {"nocite", "citestyle", "setcitestyle"}
RUNTIME_ENV_KEYS = {
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "TZ", "TERM",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
    "BUNDLE_HTTP_PROXY", "BUNDLE_HTTPS_PROXY", "BUNDLE_NO_PROXY",
    "BUNDLE_SSL_CA_CERT", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "UF_API_KEY",
    "DEEPINFRA_TOKEN", "LOCAL_LLM_API_KEY", "LOCAL_LLM_BASE_URL", "LOCAL_LLM_MODEL",
    "PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "CUDA_VISIBLE_DEVICES",
}
INTERNAL_ENV_KEYS = {"RESULTS_BUNDLE_PATH", "RESULTS_EXHIBIT_ROOT"}
SECRET_ENV_KEYS = {
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "UF_API_KEY", "DEEPINFRA_TOKEN",
    "LOCAL_LLM_API_KEY",
}
NETWORK_ENV_KEYS = {
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
    "BUNDLE_HTTP_PROXY", "BUNDLE_HTTPS_PROXY", "BUNDLE_NO_PROXY",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "UF_API_KEY", "DEEPINFRA_TOKEN",
    "LOCAL_LLM_API_KEY", "LOCAL_LLM_BASE_URL", "LOCAL_LLM_MODEL",
}


class EvidenceError(RuntimeError):
    pass


_LOCK_DESCRIPTOR: int | None = None


@contextmanager
def project_lock(root: Path) -> Iterable[None]:
    """Serialize every utility command for one project."""
    global _LOCK_DESCRIPTOR
    _, process_log = project_path(root, "process_log")
    if not process_log.is_dir():
        raise EvidenceError("process_log/ must be a real directory")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(process_log / Path(LOCK_PATH).name, flags, 0o600)
    except OSError as exc:
        raise EvidenceError(f"cannot open results pipeline lock: {exc}") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EvidenceError("results pipeline lock must be one regular file")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        _LOCK_DESCRIPTOR = descriptor
        yield
    finally:
        _LOCK_DESCRIPTOR = None
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _reject_constant(value: str) -> None:
    raise EvidenceError(f"non-finite JSON number is forbidden: {value}")


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle, parse_constant=_reject_constant)
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot read valid JSON from {path}: {exc}") from exc


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                             allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"cannot serialize receipt {path}: {exc}") from exc
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def project_path(root: Path, raw: str, *, must_exist: bool = True) -> tuple[str, Path]:
    if not isinstance(raw, str) or not raw:
        raise EvidenceError("paths must be non-empty strings")
    posix = PurePosixPath(raw.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise EvidenceError(f"path must be project-relative without traversal: {raw!r}")
    if any(part in FORBIDDEN_PARTS for part in posix.parts):
        raise EvidenceError(f"credential-bearing path may not enter a result receipt: {raw!r}")
    normalized = posix.as_posix()
    candidate = root.joinpath(*posix.parts)
    current = root
    for part in posix.parts:
        current = current / part
        if current.is_symlink():
            raise EvidenceError(f"symlink path is forbidden in result provenance: {normalized}")
        if not current.exists():
            break
    if must_exist and not candidate.exists():
        raise EvidenceError(f"declared path does not exist: {normalized}")
    return normalized, candidate


def reject_audit_namespace(raw: str, where: str) -> None:
    if raw == AUDIT_NAMESPACE or raw.startswith(AUDIT_NAMESPACE + "/"):
        raise EvidenceError(
            f"{where} may not use reserved audit namespace {AUDIT_NAMESPACE}/"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def fingerprint(root: Path, raw: str) -> dict[str, Any]:
    normalized, path = project_path(root, raw)
    mode = path.lstat().st_mode
    if stat.S_ISREG(mode):
        return {"path": normalized, "kind": "file", "sha256": sha256_file(path)}
    if not stat.S_ISDIR(mode):
        raise EvidenceError(f"only regular files/directories may be fingerprinted: {normalized}")
    entries: list[dict[str, Any]] = []
    for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
        relative = child.relative_to(path).as_posix()
        if child.is_symlink():
            raise EvidenceError(f"symlink inside declared directory is forbidden: {normalized}/{relative}")
        child_mode = child.lstat().st_mode
        if stat.S_ISDIR(child_mode):
            entries.append({"path": relative, "kind": "directory"})
            continue
        if not stat.S_ISREG(child_mode):
            raise EvidenceError(f"special file inside declared directory: {normalized}/{relative}")
        entries.append({"path": relative, "kind": "file", "sha256": sha256_file(child)})
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "path": normalized,
        "kind": "directory",
        "sha256": f"sha256:{hashlib.sha256(encoded).hexdigest()}",
        "entries": entries,
    }


def fingerprint_many(root: Path, values: Iterable[str]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for raw in values:
        normalized, _ = project_path(root, raw)
        if normalized in seen:
            raise EvidenceError(f"duplicate declared path: {normalized}")
        seen.add(normalized)
        result.append(fingerprint(root, normalized))
    return result


def object_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _require_keys(obj: dict[str, Any], required: set[str], allowed: set[str], where: str) -> None:
    missing = sorted(required - obj.keys())
    extra = sorted(obj.keys() - allowed)
    if missing:
        raise EvidenceError(f"{where} missing required keys: {', '.join(missing)}")
    if extra:
        raise EvidenceError(f"{where} has unsupported keys: {', '.join(extra)}")


def _string_list(value: Any, where: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise EvidenceError(f"{where} must be {'a non-empty' if nonempty else 'an'} array")
    if any(not isinstance(item, str) or not item for item in value):
        raise EvidenceError(f"{where} entries must be non-empty strings")
    if len(value) != len(set(value)):
        raise EvidenceError(f"{where} contains duplicates")
    return value


def paths_overlap(first: str, second: str) -> bool:
    left = PurePosixPath(first).parts
    right = PurePosixPath(second).parts
    shorter = min(len(left), len(right))
    return left[:shorter] == right[:shorter]


def overlapping_pair(first: Iterable[str], second: Iterable[str], *, same: bool = False
                     ) -> tuple[str, str] | None:
    left = list(first)
    right = left if same else list(second)
    for left_index, left_path in enumerate(left):
        start = left_index + 1 if same else 0
        for right_path in right[start:]:
            if paths_overlap(left_path, right_path):
                return left_path, right_path
    return None


def validate_bundle(bundle: Any, root: Path) -> dict[str, Any]:
    if not isinstance(bundle, dict):
        raise EvidenceError("result bundle must be a JSON object")
    required = {"schema_version", "producer", "results", "artifacts", "renderer", "exhibits"}
    _require_keys(bundle, required, required | {"metadata"}, "bundle")
    if (isinstance(bundle["schema_version"], bool) or
            not isinstance(bundle["schema_version"], int) or
            bundle["schema_version"] != 1):
        raise EvidenceError(f"unsupported result schema_version: {bundle['schema_version']!r}")

    producer = bundle["producer"]
    if not isinstance(producer, dict):
        raise EvidenceError("producer must be an object")
    _require_keys(producer, {"name", "code", "inputs", "reproducibility"},
                  {"name", "code", "inputs", "reproducibility", "notes"}, "producer")
    if not isinstance(producer["name"], str) or not producer["name"]:
        raise EvidenceError("producer.name must be a non-empty string")
    producer_code = _string_list(producer["code"], "producer.code", nonempty=True)
    producer_inputs = _string_list(producer["inputs"], "producer.inputs")
    producer["code"] = [project_path(root, raw)[0] for raw in producer_code]
    producer["inputs"] = [project_path(root, raw)[0] for raw in producer_inputs]
    if len(producer["code"]) != len(set(producer["code"])):
        raise EvidenceError("producer.code contains normalized duplicates")
    if len(producer["inputs"]) != len(set(producer["inputs"])):
        raise EvidenceError("producer.inputs contains normalized duplicates")
    if producer["reproducibility"] not in {"exact", "bounded", "captured"}:
        raise EvidenceError("producer.reproducibility must be exact, bounded, or captured")
    if "notes" in producer and not isinstance(producer["notes"], str):
        raise EvidenceError("producer.notes must be a string")

    results = bundle["results"]
    if not isinstance(results, dict) or not results:
        raise EvidenceError("results must be a non-empty object")
    result_allowed = {"description", "value", "unit", "display", "uncertainty",
                      "artifact", "selector", "metadata"}
    for result_id, result in results.items():
        if not isinstance(result_id, str) or not RESULT_ID_RE.fullmatch(result_id):
            raise EvidenceError(f"invalid result id: {result_id!r}")
        if not isinstance(result, dict):
            raise EvidenceError(f"results.{result_id} must be an object")
        _require_keys(result, {"description"}, result_allowed, f"results.{result_id}")
        if not isinstance(result["description"], str) or not result["description"]:
            raise EvidenceError(f"results.{result_id}.description must be non-empty")
        if "value" not in result and "artifact" not in result:
            raise EvidenceError(f"results.{result_id} needs value and/or artifact")
        if "artifact" in result and (not isinstance(result["artifact"], str) or not result["artifact"]):
            raise EvidenceError(f"results.{result_id}.artifact must be a path string")
        for string_key in ("unit", "selector"):
            if string_key in result and not isinstance(result[string_key], str):
                raise EvidenceError(f"results.{result_id}.{string_key} must be a string")
        for object_key in ("display", "uncertainty", "metadata"):
            if object_key in result and not isinstance(result[object_key], dict):
                raise EvidenceError(f"results.{result_id}.{object_key} must be an object")

    artifacts = bundle["artifacts"]
    if not isinstance(artifacts, list):
        raise EvidenceError("artifacts must be an array")
    artifact_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise EvidenceError(f"artifacts[{index}] must be an object")
        _require_keys(artifact, {"path", "description"}, {"path", "description", "media_type"},
                      f"artifacts[{index}]")
        if not isinstance(artifact["description"], str) or not artifact["description"]:
            raise EvidenceError(f"artifacts[{index}].description must be non-empty")
        if "media_type" in artifact and not isinstance(artifact["media_type"], str):
            raise EvidenceError(f"artifacts[{index}].media_type must be a string")
        normalized, _ = project_path(root, artifact["path"])
        if not normalized.startswith("output/"):
            raise EvidenceError(f"artifacts[{index}].path must be under output/")
        reject_audit_namespace(normalized, f"artifacts[{index}].path")
        if normalized in artifact_paths:
            raise EvidenceError(f"duplicate artifact path: {normalized}")
        artifact_paths.add(normalized)
        artifact["path"] = normalized
    for result_id, result in results.items():
        if "artifact" in result:
            normalized, _ = project_path(root, result["artifact"])
            if normalized not in artifact_paths:
                raise EvidenceError(
                    f"results.{result_id}.artifact is not declared in artifacts: {normalized}"
                )
            result["artifact"] = normalized

    renderer = bundle["renderer"]
    if not isinstance(renderer, dict):
        raise EvidenceError("renderer must be an object")
    _require_keys(renderer, {"code"}, {"code", "notes"}, "renderer")
    renderer_code = _string_list(renderer["code"], "renderer.code")
    renderer["code"] = [project_path(root, raw)[0] for raw in renderer_code]
    if len(renderer["code"]) != len(set(renderer["code"])):
        raise EvidenceError("renderer.code contains normalized duplicates")
    if "notes" in renderer and not isinstance(renderer["notes"], str):
        raise EvidenceError("renderer.notes must be a string")

    exhibits = bundle["exhibits"]
    if not isinstance(exhibits, list):
        raise EvidenceError("exhibits must be an array")
    exhibit_ids: set[str] = set()
    exhibit_paths: set[str] = set()
    for index, exhibit in enumerate(exhibits):
        if not isinstance(exhibit, dict):
            raise EvidenceError(f"exhibits[{index}] must be an object")
        _require_keys(exhibit, {"id", "kind", "path", "description", "result_ids"},
                      {"id", "kind", "path", "description", "result_ids"},
                      f"exhibits[{index}]")
        exhibit_id = exhibit["id"]
        if not isinstance(exhibit_id, str) or not RESULT_ID_RE.fullmatch(exhibit_id):
            raise EvidenceError(f"invalid exhibit id: {exhibit_id!r}")
        if exhibit_id in exhibit_ids:
            raise EvidenceError(f"duplicate exhibit id: {exhibit_id}")
        exhibit_ids.add(exhibit_id)
        if exhibit["kind"] not in {"table", "figure"}:
            raise EvidenceError(f"exhibits[{index}].kind must be table or figure")
        if not isinstance(exhibit["description"], str) or not exhibit["description"]:
            raise EvidenceError(f"exhibits[{index}].description must be non-empty")
        normalized, _ = project_path(root, exhibit["path"], must_exist=False)
        if not normalized.startswith("output/"):
            raise EvidenceError(f"exhibits[{index}].path must be under output/")
        reject_audit_namespace(normalized, f"exhibits[{index}].path")
        if normalized in exhibit_paths:
            raise EvidenceError(f"duplicate exhibit path: {normalized}")
        exhibit_paths.add(normalized)
        exhibit["path"] = normalized
        result_ids = _string_list(exhibit["result_ids"], f"exhibits[{index}].result_ids",
                                  nonempty=True)
        missing_results = sorted(set(result_ids) - results.keys())
        if missing_results:
            raise EvidenceError(
                f"exhibits[{index}] references unknown results: {', '.join(missing_results)}"
            )
    if exhibits and not renderer["code"]:
        raise EvidenceError("renderer.code must be non-empty when exhibits are declared")
    overlap = overlapping_pair(artifact_paths, exhibit_paths)
    if overlap is not None:
        raise EvidenceError(
            "artifact and exhibit paths must be disjoint: " + " / ".join(overlap)
        )
    internal_overlap = overlapping_pair(artifact_paths | exhibit_paths,
                                        artifact_paths | exhibit_paths, same=True)
    if internal_overlap is not None:
        raise EvidenceError("declared output paths must be disjoint: " +
                            " / ".join(internal_overlap))
    if "metadata" in bundle and not isinstance(bundle["metadata"], dict):
        raise EvidenceError("metadata must be an object")
    return bundle


def bundle_and_path(root: Path, raw: str) -> tuple[dict[str, Any], str, Path]:
    normalized, path = project_path(root, raw)
    reject_audit_namespace(normalized, "result bundle")
    return validate_bundle(load_json(path), root), normalized, path


def actual_command(values: list[str]) -> list[str]:
    command = list(values)
    if command and command[0] == "--":
        command.pop(0)
    if not command:
        raise EvidenceError("a command is required after --")
    if any("\x00" in item for item in command):
        raise EvidenceError("command arguments may not contain NUL")
    return command


def supervised_command(command: list[str], *, cwd: Path,
                       environment: dict[str, str]) -> int:
    """Run one process group under a lock-free supervisor tied to this parent."""
    if not hasattr(os, "fork"):
        raise EvidenceError("isolated results execution requires POSIX process supervision")
    read_fd, write_fd = os.pipe()
    supervisor = os.fork()
    if supervisor == 0:
        try:
            os.close(write_fd)
            if _LOCK_DESCRIPTOR is not None:
                os.close(_LOCK_DESCRIPTOR)
            child = subprocess.Popen(
                command, cwd=cwd, env=environment, close_fds=True,
                start_new_session=True, stdin=subprocess.DEVNULL,
            )
            while True:
                returncode = child.poll()
                if returncode is not None:
                    os._exit(min(returncode, 253) if returncode >= 0
                             else min(128 - returncode, 253))
                readable, _, _ = select.select([read_fd], [], [], 0.02)
                if readable and os.read(read_fd, 1) == b"":
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait()
                    remove_abandoned_workspace(cwd)
                    os._exit(254)
        except BaseException:
            os._exit(253)
    os.close(read_fd)
    try:
        _, status = os.waitpid(supervisor, 0)
    finally:
        os.close(write_fd)
    return os.waitstatus_to_exitcode(status)


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def venv_base_roots(venv: Path, root: Path) -> list[Path]:
    """Return external interpreter roots needed by a relocatable project venv."""
    config = venv / "pyvenv.cfg"
    if not config.is_file() or config.is_symlink():
        return []
    home: Path | None = None
    try:
        for line in config.read_text(encoding="utf-8").splitlines():
            key, separator, value = line.partition("=")
            if separator and key.strip().lower() == "home":
                candidate = Path(value.strip())
                if candidate.is_absolute():
                    home = candidate.resolve()
                break
    except OSError as exc:
        raise EvidenceError(f"cannot inspect project venv runtime: {exc}") from exc
    candidates: list[Path] = []
    if home is not None:
        candidates.append(home.parent if home.name.lower() == "bin" else home)
    for name in ("python3", "python"):
        executable = venv / "bin" / name
        if executable.exists():
            resolved = executable.resolve()
            if not _inside(resolved, venv):
                candidates.append(resolved.parent.parent)
            break
    roots: list[Path] = []
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate == Path("/") or _inside(candidate, root) or _inside(root, candidate):
            raise EvidenceError("project venv base runtime must not expose the project root")
        if candidate.exists() and candidate not in roots:
            roots.append(candidate)
    return roots


def isolated_runtime(command: list[str], root: Path, cwd: Path,
                     environment: dict[str, str]) -> tuple[
                         list[str], dict[str, str], Path | None, list[Path]
                     ]:
    """Map a project venv to a neutral path and remove live-project path access."""
    rewritten = list(command)
    venv = root / ".venv"
    if venv.is_symlink():
        raise EvidenceError("project .venv must not be a symlink")
    has_venv = venv.is_dir()
    original_path = environment.get("PATH", os.defpath)
    resolved = shutil.which(rewritten[0], path=original_path)
    executable = Path(resolved) if resolved is not None else Path(rewritten[0])
    if not executable.is_absolute():
        executable = root / executable
    neutral_venv = Path("/results-runtime-venv")
    if (len(rewritten) >= 4 and Path(rewritten[0]).name.lower() in {"uv", "uv.exe"}
            and rewritten[1:3] == ["run", "python"] and has_venv):
        rewritten = [str(neutral_venv / "bin/python3"), *rewritten[3:]]
    elif has_venv and _inside(executable, venv):
        rewritten[0] = str(neutral_venv / executable.relative_to(venv))
    elif _inside(executable, root):
        raise EvidenceError("the command runtime must be the project .venv or a system executable")
    root_text = str(root)
    if any(root_text in argument for argument in rewritten[1:]):
        raise EvidenceError(
            "isolated producer/renderer command arguments may not contain the project-root path"
        )
    path_parts: list[str] = []
    if has_venv:
        path_parts.append(str(neutral_venv / "bin"))
    for raw in original_path.split(os.pathsep):
        if not raw:
            continue
        candidate = Path(raw)
        if _inside(candidate, root):
            continue
        if raw not in path_parts:
            path_parts.append(raw)
    clean = {key: value for key, value in environment.items()
             if key in RUNTIME_ENV_KEYS or key in INTERNAL_ENV_KEYS}
    clean["PATH"] = os.pathsep.join(path_parts)
    clean["PWD"] = str(cwd)
    runtime_home = environment.get("HOME", str(cwd / ".runtime-home"))
    clean["HOME"] = runtime_home
    clean["TMPDIR"] = str(cwd / ".runtime-tmp")
    clean["XDG_CACHE_HOME"] = str(cwd / ".runtime-cache")
    clean["MPLCONFIGDIR"] = str(cwd / ".runtime-cache/matplotlib")
    clean["PYTHONDONTWRITEBYTECODE"] = "1"
    if has_venv:
        clean["VIRTUAL_ENV"] = str(neutral_venv)
    else:
        clean.pop("VIRTUAL_ENV", None)
    for raw in (clean["TMPDIR"], clean["XDG_CACHE_HOME"], clean["MPLCONFIGDIR"]):
        Path(raw).mkdir(parents=True, exist_ok=True)
    runtime_roots = venv_base_roots(venv, root) if has_venv else []
    return rewritten, clean, (venv if has_venv else None), runtime_roots


def reject_credential_leak(workspace: Path, environment: dict[str, str]) -> None:
    """Reject literal provider credentials in any staged source or output byte stream."""
    secrets = {value.encode() for key, value in environment.items()
               if key in SECRET_ENV_KEYS and len(value) >= 8}
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy",
                "https_proxy", "all_proxy", "BUNDLE_HTTP_PROXY",
                "BUNDLE_HTTPS_PROXY"):
        raw = environment.get(key)
        if raw:
            try:
                encoded_password = urlsplit(raw).password
                password = unquote(encoded_password) if encoded_password else None
            except ValueError:
                password = None
            if password and len(password) >= 8:
                secrets.add(password.encode())
    if not secrets:
        return
    for path in workspace.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        tails = {secret: b"" for secret in secrets}
        try:
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    for secret in secrets:
                        combined = tails[secret] + chunk
                        if secret in combined:
                            raise EvidenceError(
                                f"staged evidence contains a literal provider credential: {path}"
                            )
                        tails[secret] = combined[-max(0, len(secret) - 1):]
        except OSError as exc:
            raise EvidenceError(f"cannot scan staged evidence for credentials: {path}: {exc}") from exc


def selected_dotenv_credentials(project_root: Path,
                                 selected: set[str]) -> dict[str, str]:
    """Read only explicitly authorized provider secrets from the project .env."""
    if not selected:
        return {}
    dotenv = project_root / ".env"
    try:
        metadata = dotenv.lstat()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise EvidenceError(f"cannot inspect project .env: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise EvidenceError("project .env must be a regular non-symlink file")
    try:
        lines = dotenv.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"cannot read project .env: {exc}") from exc
    values: dict[str, str] = {}
    assignment = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = assignment.fullmatch(stripped)
        if match is None or match.group(1) not in selected:
            continue
        key, raw = match.groups()
        if raw.startswith(("'", '"')):
            quote = raw[0]
            escaped = False
            closing: int | None = None
            for index, character in enumerate(raw[1:], start=1):
                if quote == '"' and character == "\\" and not escaped:
                    escaped = True
                    continue
                if character == quote and not escaped:
                    closing = index
                    break
                escaped = False
            if closing is None:
                raise EvidenceError(
                    f"unterminated provider credential in .env line {line_number}"
                )
            tail = raw[closing + 1:].strip()
            if tail and not tail.startswith("#"):
                raise EvidenceError(
                    f"unsupported provider credential syntax in .env line {line_number}"
                )
            value = raw[1:closing]
            if quote == '"':
                escapes = {r'\"': '"', r"\\": "\\", r"\n": "\n", r"\r": "\r", r"\t": "\t"}
                value = re.sub(
                    r'\\["\\nrt]', lambda item: escapes[item.group(0)], value
                )
        else:
            value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
        values[key] = value
    return values


def execute(command: list[str], cwd: Path, *, bundle_path: str | None = None,
            extra_environment: dict[str, str] | None = None,
            project_root: Path | None = None,
            allow_network: bool = True,
            provider_credentials: set[str] | None = None) -> None:
    environment = os.environ.copy()
    environment["PWD"] = str(cwd)
    environment.pop("OLDPWD", None)
    if bundle_path is not None:
        environment["RESULTS_BUNDLE_PATH"] = bundle_path
    if extra_environment is not None:
        environment.update(extra_environment)
    selected_credentials = provider_credentials or set()
    if not selected_credentials.issubset(SECRET_ENV_KEYS):
        raise EvidenceError("unsupported provider credential capability")
    if project_root is not None:
        for key, value in selected_dotenv_credentials(
                project_root, selected_credentials).items():
            if not environment.get(key):
                environment[key] = value
    for key in SECRET_ENV_KEYS:
        if key not in selected_credentials:
            environment.pop(key, None)
    if not allow_network:
        for key in NETWORK_ENV_KEYS:
            environment.pop(key, None)
    runtime_venv: Path | None = None
    runtime_roots: list[Path] = []
    if project_root is not None:
        command, environment, runtime_venv, runtime_roots = isolated_runtime(
            command, project_root, cwd, environment
        )
    sandboxed_command: list[str]
    bubblewrap = shutil.which("bwrap")
    sandbox_exec = shutil.which("sandbox-exec")
    if project_root is not None and bubblewrap is not None:
        sandboxed_command = [
            bubblewrap, "--die-with-parent", "--new-session", "--unshare-pid",
            "--as-pid-1",
        ]
        system_roots = [Path(raw) for raw in
                        ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc")]
        for path in system_roots:
            raw = str(path)
            if Path(raw).exists():
                sandboxed_command.extend(["--ro-bind", raw, raw])
        sandboxed_command.extend(["--proc", "/proc", "--dev", "/dev", "--dir", "/tmp"])
        for raw in ("/sys",):
            if Path(raw).exists():
                sandboxed_command.extend(["--ro-bind", raw, raw])
        if runtime_venv is not None:
            sandboxed_command.extend(["--ro-bind", str(runtime_venv), "/results-runtime-venv"])
        for runtime_root in runtime_roots:
            if not any(_inside(runtime_root, system_root) for system_root in system_roots):
                sandboxed_command.extend(
                    ["--ro-bind", str(runtime_root), str(runtime_root)]
                )
        runtime_home = Path(environment["HOME"])
        for relative in (".local/state/zeropaper/wrds", ".cache/zeropaper/wrds"):
            service_path = runtime_home / relative
            if service_path.exists() and not service_path.is_symlink():
                sandboxed_command.extend(["--ro-bind", str(service_path), str(service_path)])
        sandboxed_command.extend(["--tmpfs", str(project_root)])
        sandboxed_command.extend([
            "--bind", str(cwd), str(cwd), "--chdir", str(cwd), "--", *command
        ])
    elif project_root is not None and sandbox_exec is not None:
        def literal(raw: str) -> str:
            return raw.replace("\\", "\\\\").replace('"', '\\"')
        # Homebrew Python routinely loads sibling formulae through absolute
        # /opt/homebrew paths, so its runtime closure cannot be represented by
        # only the interpreter keg named in pyvenv.cfg.  The project-overlap
        # guard below keeps this broad read root from exposing project data.
        read_roots = ["/System", "/Library", "/usr", "/bin", "/sbin", "/dev",
                      "/etc", "/private/etc", "/opt"]
        if any(_inside(project_root, Path(raw)) for raw in read_roots):
            raise EvidenceError(
                "macOS results execution requires the project outside system runtime roots"
            )
        if runtime_venv is not None:
            read_roots.append(str(runtime_venv))
            environment["VIRTUAL_ENV"] = str(runtime_venv)
            environment["PATH"] = environment["PATH"].replace(
                "/results-runtime-venv", str(runtime_venv)
            )
            command = [item.replace("/results-runtime-venv", str(runtime_venv))
                       for item in command]
        read_roots.extend(str(path) for path in runtime_roots)
        runtime_home = Path(environment["HOME"])
        for relative in (".local/state/zeropaper/wrds", ".cache/zeropaper/wrds"):
            service_path = runtime_home / relative
            if service_path.exists() and not service_path.is_symlink():
                if (_inside(project_root, service_path) or
                        _inside(service_path, project_root)):
                    raise EvidenceError(
                        "macOS WRDS runtime path must not overlap the project root"
                    )
                read_roots.append(str(service_path))
        read_rules = " ".join(f'(subpath "{literal(raw)}")' for raw in read_roots)
        profile = (
            '(version 1) (deny default) (allow process*) '
            + ('(allow network*) ' if allow_network else '') +
            '(allow sysctl-read) (allow mach-lookup) (allow ipc-posix-shm) '
            f'(allow file-read* {read_rules} (subpath "{literal(str(cwd))}")) '
            f'(allow file-write* (subpath "{literal(str(cwd))}"))'
        )
        sandboxed_command = [sandbox_exec, "-p", profile, *command]
    elif project_root is not None:
        raise EvidenceError(
            "isolated results execution requires bwrap (Linux) or sandbox-exec (macOS)"
        )
    else:
        sandboxed_command = command
    returncode = supervised_command(sandboxed_command, cwd=cwd, environment=environment)
    if returncode != 0:
        raise EvidenceError(f"command failed with exit {returncode}: {command!r}")
    reject_credential_leak(cwd, environment)


def command_entrypoint(command: list[str]) -> str:
    executable = Path(command[0]).name.lower()
    if executable in {"python", "python3", "python.exe", "python3.exe", "rscript", "julia"}:
        if len(command) < 2 or command[1].startswith("-"):
            raise EvidenceError("commands must execute a script file, not inline/module code")
        raw = command[1]
    elif executable in {"bash", "sh", "zsh"}:
        if len(command) < 2 or command[1].startswith("-"):
            raise EvidenceError("shell commands must execute a declared script file")
        raw = command[1]
    elif executable in {"uv", "uv.exe"}:
        if (len(command) < 4 or command[1] != "run" or
                Path(command[2]).name.lower() not in {"python", "python3", "python.exe",
                                                       "python3.exe"} or
                command[3].startswith("-")):
            raise EvidenceError("uv commands must have the form: uv run python <script>")
        raw = command[3]
    else:
        raise EvidenceError(
            "unsupported command launcher; use python, Rscript, julia, "
            "bash/sh/zsh <script>, or uv run python <script>"
        )
    posix = PurePosixPath(raw.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts:
        raise EvidenceError("executed script entrypoint must be a project-relative path")
    return posix.as_posix()


def command_uses_declared_code(command: list[str], code_paths: list[str], where: str) -> None:
    entrypoint = command_entrypoint(command)
    if entrypoint not in code_paths:
        raise EvidenceError(
            f"{where} command entrypoint is not a declared code path: {entrypoint}"
        )


def temporary_absent_path(path: Path, label: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.{label}.", dir=path.parent)
    os.close(fd)
    os.unlink(raw)
    return Path(raw)


def validate_run_plan(value: Any, root: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError("run plan must be a JSON object")
    required = {"plan_version", "producer_code", "producer_inputs", "artifacts",
                "renderer_code", "exhibits"}
    _require_keys(value, required, required | {"provider_credentials"}, "run plan")
    if (isinstance(value["plan_version"], bool) or
            not isinstance(value["plan_version"], int) or
            value["plan_version"] != RUN_PLAN_VERSION):
        raise EvidenceError(f"unsupported run plan version: {value['plan_version']!r}")
    for key in ("producer_code", "producer_inputs", "renderer_code"):
        paths = _string_list(value[key], f"run plan.{key}",
                             nonempty=(key == "producer_code"))
        value[key] = [project_path(root, raw)[0] for raw in paths]
        if len(value[key]) != len(set(value[key])):
            raise EvidenceError(f"run plan.{key} contains normalized duplicates")
    for key in ("artifacts", "exhibits"):
        paths = _string_list(value[key], f"run plan.{key}")
        value[key] = [project_path(root, raw, must_exist=False)[0] for raw in paths]
        if any(not raw.startswith("output/") for raw in value[key]):
            raise EvidenceError(f"run plan.{key} paths must be under output/")
        for raw in value[key]:
            reject_audit_namespace(raw, f"run plan.{key}")
        if len(value[key]) != len(set(value[key])):
            raise EvidenceError(f"run plan.{key} contains normalized duplicates")
    if value["exhibits"] and not value["renderer_code"]:
        raise EvidenceError("run plan.renderer_code must be non-empty when exhibits are declared")
    value["provider_credentials"] = _string_list(
        value.get("provider_credentials", []), "run plan.provider_credentials"
    )
    if (len(value["provider_credentials"]) != len(set(value["provider_credentials"])) or
            not set(value["provider_credentials"]).issubset(SECRET_ENV_KEYS)):
        raise EvidenceError("run plan.provider_credentials contains unsupported values")
    outputs = set(value["artifacts"]) | set(value["exhibits"])
    overlap = overlapping_pair(outputs, outputs, same=True)
    if overlap is not None:
        raise EvidenceError("run-plan output paths must be disjoint: " + " / ".join(overlap))
    return value


def remove_generated_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _copy_evidence_path(source: Path, destination: Path) -> None:
    """Copy with copy-on-write cloning where the filesystem supports it."""
    def clone_file(raw_source: str, raw_destination: str) -> str:
        source_path = Path(raw_source)
        destination_path = Path(raw_destination)
        try:
            source_fd = os.open(source_path, os.O_RDONLY)
            try:
                destination_fd = os.open(
                    destination_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                try:
                    fcntl.ioctl(destination_fd, 0x40049409, source_fd)  # Linux FICLONE
                finally:
                    os.close(destination_fd)
            finally:
                os.close(source_fd)
            shutil.copystat(source_path, destination_path, follow_symlinks=False)
        except OSError:
            destination_path.unlink(missing_ok=True)
            shutil.copy2(source_path, destination_path)
        return str(destination_path)

    if source.is_dir():
        shutil.copytree(source, destination, copy_function=clone_file)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        clone_file(str(source), str(destination))


def workspace_exists(workspace: Path) -> bool:
    return workspace.exists() or workspace.is_symlink()


def remove_abandoned_workspace(workspace: Path) -> None:
    """Iteratively remove one utility host-temp tree without following links."""
    if not workspace_exists(workspace):
        return
    temp_root = Path(tempfile.gettempdir()).resolve(strict=True)
    if (workspace.parent.resolve(strict=True) != temp_root or
            not workspace.name.startswith("results-workspace-") or
            workspace.is_symlink()):
        raise EvidenceError("refusing to remove an unsafe results workspace path")
    directory_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                       getattr(os, "O_NOFOLLOW", 0))
    temp_fd = os.open(temp_root, directory_flags)
    root_fd: int | None = None
    try:
        expected = os.stat(workspace.name, dir_fd=temp_fd, follow_symlinks=False)
        if not stat.S_ISDIR(expected.st_mode):
            raise EvidenceError("results workspace root is not a real directory")
        os.chmod(
            workspace.name, stat.S_IRWXU,
            dir_fd=temp_fd, follow_symlinks=False,
        )
        root_fd = os.open(workspace.name, directory_flags, dir_fd=temp_fd)
        opened = os.fstat(root_fd)
        if (not stat.S_ISDIR(opened.st_mode) or
                (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)):
            raise EvidenceError("results workspace changed during cleanup")
        os.fchmod(root_fd, stat.S_IRWXU)
        directories: list[str] = []
        with os.scandir(root_fd) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    directories.append(entry.name)
                else:
                    os.unlink(entry.name, dir_fd=root_fd)
        while directories:
            name = directories.pop()
            expected_child = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
            if not stat.S_ISDIR(expected_child.st_mode):
                raise EvidenceError("results workspace directory changed during cleanup")
            os.chmod(
                name, stat.S_IRWXU,
                dir_fd=root_fd, follow_symlinks=False,
            )
            child_fd = os.open(name, directory_flags, dir_fd=root_fd)
            try:
                opened_child = os.fstat(child_fd)
                if ((opened_child.st_dev, opened_child.st_ino) !=
                        (expected_child.st_dev, expected_child.st_ino)):
                    raise EvidenceError("results workspace directory changed during cleanup")
                os.fchmod(child_fd, stat.S_IRWXU)
                with os.scandir(child_fd) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            while True:
                                moved = ".results-cleanup-" + os.urandom(12).hex()
                                try:
                                    os.stat(moved, dir_fd=root_fd, follow_symlinks=False)
                                except FileNotFoundError:
                                    break
                            os.rename(
                                entry.name, moved,
                                src_dir_fd=child_fd, dst_dir_fd=root_fd,
                            )
                            directories.append(moved)
                        else:
                            os.unlink(entry.name, dir_fd=child_fd)
            finally:
                os.close(child_fd)
            os.rmdir(name, dir_fd=root_fd)
        os.close(root_fd)
        root_fd = None
        os.rmdir(workspace.name, dir_fd=temp_fd)
    finally:
        if root_fd is not None:
            os.close(root_fd)
        os.close(temp_fd)


@contextmanager
def workspace_cleanup_guard(workspace: Path) -> Iterable[None]:
    """Keep a lock-free guardian alive until the entire workspace context closes."""
    if not hasattr(os, "fork"):
        raise EvidenceError("isolated results execution requires POSIX cleanup supervision")
    read_fd, write_fd = os.pipe()
    guardian = os.fork()
    if guardian == 0:
        try:
            os.close(write_fd)
            if _LOCK_DESCRIPTOR is not None:
                os.close(_LOCK_DESCRIPTOR)
            while True:
                try:
                    marker = os.read(read_fd, 1)
                    break
                except InterruptedError:
                    continue
            os.close(read_fd)
            if marker == b"":
                while workspace_exists(workspace):
                    try:
                        remove_abandoned_workspace(workspace)
                    except (EvidenceError, OSError):
                        time.sleep(0.05)
        finally:
            os._exit(0)
    os.close(read_fd)
    try:
        yield
    finally:
        try:
            if not workspace_exists(workspace):
                try:
                    os.write(write_fd, b"1")
                except BrokenPipeError:
                    pass
        finally:
            os.close(write_fd)
        while True:
            try:
                os.waitpid(guardian, 0)
                break
            except InterruptedError:
                continue


@contextmanager
def isolated_workspace(root: Path, source_paths: Iterable[str],
                       output_paths: Iterable[str]) -> Iterable[Path]:
    """Run untrusted computation in a fresh view containing only declared inputs."""
    normalized_sources: list[str] = []
    for raw in dict.fromkeys(source_paths):
        normalized, _ = project_path(root, raw)
        normalized_sources.append(normalized)
    source_set = set(normalized_sources)
    overlap = overlapping_pair(source_set, source_set, same=True)
    if overlap is not None:
        raise EvidenceError(
            "isolated workspace sources must not overlap: " + " / ".join(overlap)
        )
    workspace = Path(tempfile.mkdtemp(prefix="results-workspace-"))
    with workspace_cleanup_guard(workspace):
        try:
            for raw in normalized_sources:
                _, source = project_path(root, raw)
                destination = workspace.joinpath(*PurePosixPath(raw).parts)
                _copy_evidence_path(source, destination)
            for raw in dict.fromkeys(output_paths):
                normalized, destination = project_path(workspace, raw, must_exist=False)
                if destination.exists() or destination.is_symlink():
                    raise EvidenceError(f"isolated output overlaps a source: {normalized}")
                destination.parent.mkdir(parents=True, exist_ok=True)
            yield workspace
        finally:
            remove_abandoned_workspace(workspace)


def publish_workspace_path(root: Path, workspace: Path, raw: str) -> None:
    """Copy one isolated output beside its final target, then publish atomically."""
    normalized, source = project_path(workspace, raw)
    _, destination = project_path(root, normalized, must_exist=False)
    if destination.exists() or destination.is_symlink():
        raise EvidenceError(f"publication target appeared during isolated run: {normalized}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged = temporary_absent_path(destination, "publish")
    try:
        _copy_evidence_path(source, staged)
        _, checked = project_path(root, normalized, must_exist=False)
        if checked.exists() or checked.is_symlink():
            raise EvidenceError(f"publication target changed before commit: {normalized}")
        os.replace(staged, checked)
    finally:
        if staged.exists() or staged.is_symlink():
            remove_generated_path(staged)


def _safe_restore_destination(root: Path, destination: Path) -> None:
    """Prepare a project-contained destination without following child-made links."""
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise EvidenceError(f"restore target escapes project root: {destination}") from exc
    if not relative.parts:
        raise EvidenceError("refusing to restore over the project root")
    current = root
    for part in relative.parts[:-1]:
        candidate = current / part
        if candidate.is_symlink() or (candidate.exists() and not candidate.is_dir()):
            remove_generated_path(candidate)
        if not candidate.exists():
            candidate.mkdir()
        current = candidate
    if destination.exists() or destination.is_symlink():
        remove_generated_path(destination)


def _restore_target(root: Path, raw: str) -> tuple[str, Path]:
    """Resolve a journal path lexically so recovery can remove hostile symlinks."""
    if not isinstance(raw, str) or not raw:
        raise EvidenceError("transaction paths must be non-empty strings")
    posix = PurePosixPath(raw.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise EvidenceError(f"invalid path in results transaction journal: {raw!r}")
    if any(part in FORBIDDEN_PARTS for part in posix.parts):
        raise EvidenceError(f"credential path in results transaction journal: {raw!r}")
    normalized = posix.as_posix()
    return normalized, root.joinpath(*posix.parts)


def _restore_evidence_path(root: Path, source: Path, destination: Path) -> None:
    _safe_restore_destination(root, destination)
    _copy_evidence_path(source, destination)


def _clear_transaction_files(root: Path) -> None:
    _, journal = project_path(root, TRANSACTION_PATH, must_exist=False)
    _, backup = project_path(root, TRANSACTION_BACKUP_PATH, must_exist=False)
    if backup.exists() or backup.is_symlink():
        remove_generated_path(backup)
    if journal.exists() or journal.is_symlink():
        remove_generated_path(journal)


def recover_transaction(root: Path) -> None:
    """Recover a parent-owned publication interrupted after every child exited."""
    _, journal = project_path(root, TRANSACTION_PATH, must_exist=False)
    _, backup_root = project_path(root, TRANSACTION_BACKUP_PATH, must_exist=False)
    if not (journal.exists() or journal.is_symlink() or
            backup_root.exists() or backup_root.is_symlink()):
        return
    if not journal.exists() or journal.is_symlink() or not journal.is_file():
        raise EvidenceError("results transaction journal is missing or unsafe; operator recovery required")
    value = load_json(journal)
    if not isinstance(value, dict):
        raise EvidenceError("malformed results transaction journal; operator recovery required")
    required = {"transaction_version", "phase", "cleanup_paths", "backups",
                "registry_before"}
    _require_keys(value, required, required, "results transaction journal")
    if (isinstance(value["transaction_version"], bool) or
            not isinstance(value["transaction_version"], int) or
            value["transaction_version"] != 1 or
            value["phase"] not in {"preparing", "prepared", "committed", "rolled_back"}):
        raise EvidenceError("unsupported results transaction journal; operator recovery required")
    if not isinstance(value["cleanup_paths"], list) or not isinstance(value["backups"], list):
        raise EvidenceError("malformed results transaction journal; operator recovery required")
    for raw in value["cleanup_paths"]:
        _restore_target(root, raw)
    backup_names: list[str] = []
    for item in value["backups"]:
        if (not isinstance(item, dict) or set(item) != {"path", "backup"} or
                not isinstance(item["path"], str) or
                not isinstance(item["backup"], str) or
                not re.fullmatch(r"[0-9]+", item["backup"])):
            raise EvidenceError("malformed results transaction journal; operator recovery required")
        _restore_target(root, item["path"])
        backup_names.append(item["backup"])
    if len(backup_names) != len(set(backup_names)):
        raise EvidenceError("duplicate results transaction backups; operator recovery required")
    # A prepared transaction may have changed receipt and registry bytes before
    # the process died. Validate structure first, restore, then authenticate.
    load_registry(root, candidate=value["registry_before"], verify_receipt_bytes=False)
    if value["phase"] in {"preparing", "committed", "rolled_back"}:
        _clear_transaction_files(root)
        return
    if not backup_root.exists() or backup_root.is_symlink() or not backup_root.is_dir():
        raise EvidenceError("results transaction backup is missing or unsafe; operator recovery required")
    rollback_lifecycle_transaction(root, value)


def rollback_lifecycle_transaction(root: Path, value: dict[str, Any]) -> None:
    """Roll back with the parent's trusted in-memory transaction description."""
    _, backup_root = project_path(root, TRANSACTION_BACKUP_PATH, must_exist=False)
    for raw in value["cleanup_paths"]:
        normalized, destination = _restore_target(root, raw)
        _safe_restore_destination(root, destination)
        if destination.exists() or destination.is_symlink():
            raise EvidenceError(f"failed to remove interrupted output: {normalized}")
    for item in value["backups"]:
        if (not isinstance(item, dict) or not isinstance(item.get("path"), str) or
                not isinstance(item.get("backup"), str) or
                not re.fullmatch(r"[0-9]+", item["backup"])):
            raise EvidenceError("malformed path in results transaction journal")
        _, destination = _restore_target(root, item["path"])
        source = backup_root / item["backup"]
        if not source.exists() or source.is_symlink():
            raise EvidenceError("results transaction backup is missing; operator recovery required")
        _restore_evidence_path(root, source, destination)
    atomic_json(root / REGISTRY_PATH, value["registry_before"])
    load_registry(root)
    terminal = dict(value)
    terminal["phase"] = "rolled_back"
    atomic_json(root / TRANSACTION_PATH, terminal)
    _clear_transaction_files(root)


def prepare_lifecycle_transaction(root: Path, *, cleanup_paths: Iterable[str],
                                  restore_paths: Iterable[str],
                                  registry_before: dict[str, Any]) -> dict[str, Any]:
    """Durably record how to roll back a multi-file lifecycle publication."""
    recover_transaction(root)
    _, journal = project_path(root, TRANSACTION_PATH, must_exist=False)
    _, backup_root = project_path(root, TRANSACTION_BACKUP_PATH, must_exist=False)
    if journal.exists() or backup_root.exists():
        raise EvidenceError("another results transaction is already prepared")
    cleanup = []
    for raw in dict.fromkeys(cleanup_paths):
        normalized, _ = project_path(root, raw, must_exist=False)
        cleanup.append(normalized)
    backups: list[dict[str, str]] = []
    restore_sources: list[Path] = []
    for index, raw in enumerate(dict.fromkeys(restore_paths)):
        normalized, source = project_path(root, raw)
        backups.append({"path": normalized, "backup": str(index)})
        restore_sources.append(source)
    transaction = {
        "transaction_version": 1,
        "phase": "preparing",
        "cleanup_paths": cleanup,
        "backups": backups,
        "registry_before": registry_before,
    }
    atomic_json(journal, transaction)
    try:
        backup_root.mkdir(mode=0o700)
        for index, source in enumerate(restore_sources):
            backup = backup_root / str(index)
            _copy_evidence_path(source, backup)
        transaction["phase"] = "prepared"
        atomic_json(journal, transaction)
        return transaction
    except BaseException:
        _clear_transaction_files(root)
        raise


def commit_lifecycle_transaction(root: Path) -> None:
    _, journal = project_path(root, TRANSACTION_PATH)
    transaction = load_json(journal)
    if not isinstance(transaction, dict) or transaction.get("phase") != "prepared":
        raise EvidenceError("cannot commit a transaction outside prepared phase")
    transaction["phase"] = "committed"
    atomic_json(journal, transaction)
    _clear_transaction_files(root)


@contextmanager
def lifecycle_transaction(root: Path, *, cleanup_paths: Iterable[str],
                          restore_paths: Iterable[str],
                          registry_before: dict[str, Any]) -> Iterable[None]:
    """Durably roll back incomplete multi-file lifecycle publication."""
    transaction = prepare_lifecycle_transaction(
        root, cleanup_paths=cleanup_paths, restore_paths=restore_paths,
        registry_before=registry_before,
    )
    try:
        yield
    except BaseException:
        rollback_lifecycle_transaction(root, transaction)
        raise
    commit_lifecycle_transaction(root)


def execute_fresh_exhibits(command: list[str], root: Path, bundle: dict[str, Any],
                           bundle_path: str,
                           *, expected: list[dict[str, Any]] | None = None,
                           publish: bool = True) -> list[str]:
    paths: list[tuple[str, Path]] = []
    live_exhibit_snapshots: list[dict[str, Any]] = []
    for exhibit in bundle["exhibits"]:
        raw, path = project_path(root, exhibit["path"], must_exist=False)
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(f"exhibit target must be a regular file: {raw}")
            live_exhibit_snapshots.append(fingerprint(root, raw))
        paths.append((raw, path))
    artifact_paths = [entry["path"] for entry in bundle["artifacts"]]
    sources = [bundle_path, *artifact_paths, *bundle["renderer"]["code"]]
    source_snapshots = fingerprint_many(root, sources)
    with isolated_workspace(root, sources, []) as workspace:
        stage = workspace / ".results-exhibits"
        stage.mkdir()
        execute(
            command, workspace, bundle_path=bundle_path,
            extra_environment={"RESULTS_EXHIBIT_ROOT": str(stage)},
            project_root=root,
            allow_network=False,
            provider_credentials=set(),
        )
        source_failures = compare_snapshot(
            workspace, source_snapshots, "isolated renderer source"
        )
        if source_failures:
            raise EvidenceError("renderer mutated its isolated declared sources: " +
                                "; ".join(source_failures))
        live_failures = compare_snapshot(root, live_exhibit_snapshots, "live exhibit")
        if live_failures:
            raise EvidenceError("project exhibits changed outside isolated renderer: " +
                                "; ".join(live_failures))
        for raw, _ in paths:
            _, staged = project_path(stage, raw, must_exist=False)
            if not staged.exists() or staged.is_symlink() or not staged.is_file():
                raise EvidenceError(f"renderer did not freshly stage regular exhibit: {raw}")
        if expected is not None:
            expected_by_path = {entry["path"]: entry for entry in expected}
            for raw, _ in paths:
                if fingerprint(stage, raw) != expected_by_path.get(raw):
                    raise EvidenceError(f"fresh render differs from recorded bytes at {raw}")
        if publish:
            for raw, _ in paths:
                _, destination = project_path(root, raw, must_exist=False)
                if destination.exists() or destination.is_symlink():
                    remove_generated_path(destination)
                publish_workspace_path(root, stage, raw)
    return [raw for raw, _ in paths]


def snapshot_bundle(root: Path, bundle: dict[str, Any], bundle_path: str,
                    command: list[str], plan_path: str,
                    code_snapshot: list[dict[str, Any]],
                    input_snapshot: list[dict[str, Any]],
                    renderer_snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    artifacts = [entry["path"] for entry in bundle["artifacts"]]
    return {
        "command": command,
        "plan": fingerprint(root, plan_path),
        "bundle": fingerprint(root, bundle_path),
        "code": code_snapshot,
        "inputs": input_snapshot,
        "renderer_code": renderer_snapshot,
        "artifacts": fingerprint_many(root, artifacts),
        "reproducibility": bundle["producer"]["reproducibility"],
    }


def snapshot_render(root: Path, bundle: dict[str, Any], command: list[str]) -> dict[str, Any]:
    exhibit_paths = [entry["path"] for entry in bundle["exhibits"]]
    return {
        "command": command,
        "code": fingerprint_many(root, bundle["renderer"]["code"]),
        "exhibits": fingerprint_many(root, exhibit_paths),
    }


def result_receipt_supersedes(root: Path, receipt_raw: str,
                              receipt: dict[str, Any] | None = None) -> list[str]:
    """Return the immutable replacement relation recorded by one result receipt."""
    if receipt is None:
        _, receipt_path_value = project_path(root, receipt_raw)
        receipt = load_json(receipt_path_value)
    if not isinstance(receipt, dict):
        raise EvidenceError(f"malformed result receipt: {receipt_raw}")
    values = _string_list(receipt.get("supersedes"), f"result receipt {receipt_raw}.supersedes")
    normalized: list[str] = []
    for raw in values:
        value, _ = result_receipt_path(root, raw)
        if value != raw:
            raise EvidenceError(
                f"result receipt {receipt_raw}.supersedes contains a non-normalized path"
            )
        if value == receipt_raw:
            raise EvidenceError(f"result receipt {receipt_raw} cannot supersede itself")
        normalized.append(value)
    if len(normalized) != len(set(normalized)):
        raise EvidenceError(f"result receipt {receipt_raw}.supersedes contains duplicates")
    return normalized


def compare_snapshot(root: Path, recorded: list[dict[str, Any]], label: str) -> list[str]:
    failures: list[str] = []
    for expected in recorded:
        raw = expected.get("path")
        if not isinstance(raw, str):
            failures.append(f"{label}: receipt entry has no path")
            continue
        try:
            current = fingerprint(root, raw)
        except EvidenceError as exc:
            failures.append(f"{label}: {exc}")
            continue
        if current != expected:
            failures.append(f"{label}: stale bytes at {raw}")
    return failures


def verify_receipt(root: Path, receipt_path: Path, *, rerender: bool) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    if (not isinstance(receipt, dict) or receipt.get("kind") != "result" or
            isinstance(receipt.get("receipt_version"), bool) or
            receipt.get("receipt_version") != RECEIPT_VERSION):
        raise EvidenceError(f"not a results receipt v{RECEIPT_VERSION}: {receipt_path}")
    producer = receipt.get("producer_run")
    if not isinstance(producer, dict):
        raise EvidenceError(f"receipt missing producer_run: {receipt_path}")
    receipt_raw = receipt_path.relative_to(root).as_posix()
    result_receipt_supersedes(root, receipt_raw, receipt)
    failures: list[str] = []
    for key in ("plan", "bundle", "code", "inputs", "renderer_code", "artifacts"):
        value = producer.get(key)
        entries = [value] if key in {"plan", "bundle"} and isinstance(value, dict) else value
        if not isinstance(entries, list):
            failures.append(f"producer_run.{key}: malformed receipt field")
        else:
            failures.extend(compare_snapshot(root, entries, f"producer_run.{key}"))
    bundle_field = producer.get("bundle")
    bundle: dict[str, Any] | None = None
    if isinstance(bundle_field, dict) and isinstance(bundle_field.get("path"), str):
        try:
            bundle, _, _ = bundle_and_path(root, bundle_field["path"])
            plan_field = producer.get("plan")
            if not isinstance(plan_field, dict) or not isinstance(plan_field.get("path"), str):
                raise EvidenceError("producer_run.plan is malformed")
            plan = validate_run_plan(load_json(root / plan_field["path"]), root)
            if (bundle["producer"]["code"] != plan["producer_code"] or
                    bundle["producer"]["inputs"] != plan["producer_inputs"] or
                    bundle["renderer"]["code"] != plan["renderer_code"] or
                    [entry["path"] for entry in bundle["artifacts"]] != plan["artifacts"] or
                    [entry["path"] for entry in bundle["exhibits"]] != plan["exhibits"]):
                failures.append("producer bundle no longer matches its pre-run plan")
            producer_command = producer.get("command")
            if (not isinstance(producer_command, list) or not producer_command or
                    any(not isinstance(item, str) for item in producer_command)):
                failures.append("producer_run.command: malformed receipt field")
            else:
                command_uses_declared_code(
                    producer_command, bundle["producer"]["code"], "producer"
                )
        except EvidenceError as exc:
            failures.append(f"bundle schema: {exc}")

    render = receipt.get("render_run")
    if bundle is not None and bundle["exhibits"]:
        if not isinstance(render, dict):
            failures.append("render_run: missing for bundle with declared exhibits")
        else:
            render_command = render.get("command")
            if (not isinstance(render_command, list) or not render_command or
                    any(not isinstance(item, str) for item in render_command)):
                failures.append("render_run.command: malformed receipt field")
            else:
                try:
                    command_uses_declared_code(
                        render_command, bundle["renderer"]["code"], "renderer"
                    )
                except EvidenceError as exc:
                    failures.append(str(exc))
            for key in ("code", "exhibits"):
                entries = render.get(key)
                if not isinstance(entries, list):
                    failures.append(f"render_run.{key}: malformed receipt field")
                else:
                    failures.extend(compare_snapshot(root, entries, f"render_run.{key}"))
    if failures:
        return {"receipt": str(receipt_path.relative_to(root)), "status": "STALE",
                "failures": failures}

    if rerender and bundle is not None and bundle["exhibits"]:
        command = render.get("command") if isinstance(render, dict) else None
        if not isinstance(command, list) or not command or any(not isinstance(x, str) for x in command):
            return {"receipt": str(receipt_path.relative_to(root)), "status": "STALE",
                    "failures": ["render_run.command: malformed receipt field"]}
        try:
            execute_fresh_exhibits(
                command, root, bundle, bundle_field["path"], expected=render["exhibits"],
                publish=False,
            )
        except EvidenceError as exc:
            return {"receipt": str(receipt_path.relative_to(root)), "status": "STALE",
                    "failures": [f"rerender: {exc}"]}
        post_failures: list[str] = []
        for key in ("plan", "bundle", "code", "inputs", "renderer_code", "artifacts"):
            value = producer[key]
            entries = [value] if key in {"plan", "bundle"} else value
            post_failures.extend(compare_snapshot(root, entries, f"post-render producer_run.{key}"))
        post_failures.extend(compare_snapshot(root, render["code"], "post-render render_run.code"))
        post_failures.extend(compare_snapshot(root, render["exhibits"],
                                              "post-render render_run.exhibits"))
        if post_failures:
            return {"receipt": str(receipt_path.relative_to(root)), "status": "STALE",
                    "failures": post_failures}
    return {"receipt": str(receipt_path.relative_to(root)), "status": "PASS", "failures": []}


def resolve_root(raw: str) -> Path:
    root = Path(raw).resolve()
    if not root.is_dir():
        raise EvidenceError(f"project root is not a directory: {root}")
    return root


def receipt_path(root: Path, raw: str) -> tuple[str, Path]:
    normalized, path = project_path(root, raw, must_exist=False)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise EvidenceError(f"receipt target must be a regular file: {normalized}")
    return normalized, path


def result_receipt_path(root: Path, raw: str) -> tuple[str, Path]:
    normalized, path = receipt_path(root, raw)
    if not normalized.startswith("output/") or not normalized.endswith("results.receipt.json"):
        raise EvidenceError(
            "result receipt path must be under output/ and end with results.receipt.json"
        )
    reject_audit_namespace(normalized, "result receipt")
    return normalized, path


def evidence_artifact_path(root: Path, raw: str, *, must_exist: bool = False) -> tuple[str, Path]:
    normalized, path = project_path(root, raw, must_exist=must_exist)
    if not normalized.startswith("output/evidence/"):
        raise EvidenceError("audit artifacts must be under output/evidence/")
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise EvidenceError(f"audit artifact must be a regular file: {normalized}")
    return normalized, path


def empty_registry() -> dict[str, Any]:
    return {"kind": "result_registry", "registry_version": REGISTRY_VERSION,
            "active": [], "pending": [], "retired": [],
            "receipt_fingerprints": {}}


def load_registry(root: Path, *, candidate: dict[str, Any] | None = None,
                  verify_receipt_bytes: bool = True
                  ) -> tuple[dict[str, Any], Path]:
    _, path = project_path(root, REGISTRY_PATH, must_exist=False)
    if candidate is None:
        if not path.exists():
            raise EvidenceError(f"missing durable result registry: {REGISTRY_PATH}")
        value = load_json(path)
    else:
        value = candidate
    if (not isinstance(value, dict) or value.get("kind") != "result_registry" or
            isinstance(value.get("registry_version"), bool) or
            value.get("registry_version") != REGISTRY_VERSION):
        raise EvidenceError(f"malformed result registry: {REGISTRY_PATH}")
    _require_keys(value, {"kind", "registry_version", "active", "pending", "retired",
                          "receipt_fingerprints"},
                  {"kind", "registry_version", "active", "pending", "retired",
                          "receipt_fingerprints"},
                  "result registry")
    active = _string_list(value["active"], "result registry.active")
    if len(active) != len(set(active)):
        raise EvidenceError("result registry.active contains duplicate receipts")
    pending = value["pending"]
    if not isinstance(pending, list):
        raise EvidenceError("result registry.pending must be an array")
    pending_paths: list[str] = []
    for index, entry in enumerate(pending):
        where = f"result registry.pending[{index}]"
        if not isinstance(entry, dict):
            raise EvidenceError(f"{where} must be an object")
        _require_keys(entry, {"receipt", "supersedes"}, {"receipt", "supersedes"}, where)
        normalized, _ = result_receipt_path(root, entry["receipt"])
        if normalized != entry["receipt"]:
            raise EvidenceError(f"{where}.receipt is not normalized")
        supersedes = _string_list(entry["supersedes"], f"{where}.supersedes")
        for raw in supersedes:
            old, _ = result_receipt_path(root, raw)
            if old != raw:
                raise EvidenceError(f"{where}.supersedes contains a non-normalized path")
            if old not in active:
                raise EvidenceError(f"{where}.supersedes names a non-active receipt")
        if normalized in supersedes:
            raise EvidenceError(f"{where} cannot supersede itself")
        pending_paths.append(normalized)
    retired = value["retired"]
    if not isinstance(retired, list):
        raise EvidenceError("result registry.retired must be an array")
    retired_paths: list[str] = []
    for index, entry in enumerate(retired):
        where = f"result registry.retired[{index}]"
        if not isinstance(entry, dict):
            raise EvidenceError(f"{where} must be an object")
        _require_keys(entry, {"receipt", "reason", "last_fingerprint"},
                      {"receipt", "reason", "last_fingerprint", "superseded_by"}, where)
        for key in ("receipt", "reason"):
            if not isinstance(entry[key], str) or not entry[key]:
                raise EvidenceError(f"{where}.{key} must be a non-empty string")
        normalized, _ = result_receipt_path(root, entry["receipt"])
        if normalized != entry["receipt"]:
            raise EvidenceError(f"{where}.receipt is not normalized")
        last = entry["last_fingerprint"]
        if not isinstance(last, dict) or last.get("path") != normalized:
            raise EvidenceError(f"{where}.last_fingerprint is malformed")
        if verify_receipt_bytes:
            try:
                current = fingerprint(root, normalized)
            except EvidenceError as exc:
                raise EvidenceError(f"retired result receipt is unavailable: {exc}") from exc
            if current != last:
                raise EvidenceError(f"retired result receipt bytes are stale: {normalized}")
        if "superseded_by" in entry:
            superseded, _ = result_receipt_path(root, entry["superseded_by"])
            if superseded != entry["superseded_by"]:
                raise EvidenceError(f"{where}.superseded_by is not normalized")
        retired_paths.append(normalized)
    if len(retired_paths) != len(set(retired_paths)):
        raise EvidenceError("result registry.retired contains duplicate receipts")
    if (set(active) & set(retired_paths) or set(active) & set(pending_paths) or
            set(retired_paths) & set(pending_paths)):
        raise EvidenceError("result registry lists a receipt in multiple lifecycle states")
    if len(pending_paths) != len(set(pending_paths)):
        raise EvidenceError("result registry.pending contains duplicate receipts")
    for raw in active:
        normalized, _ = result_receipt_path(root, raw)
        if normalized != raw:
            raise EvidenceError("result registry.active contains a non-normalized path")
    expected_fingerprints = set(active) | set(pending_paths)
    receipt_fingerprints = value["receipt_fingerprints"]
    if (not isinstance(receipt_fingerprints, dict) or
            set(receipt_fingerprints) != expected_fingerprints):
        raise EvidenceError(
            "result registry.receipt_fingerprints must exactly cover active/pending receipts"
        )
    for raw, expected in receipt_fingerprints.items():
        if not isinstance(expected, dict) or expected.get("path") != raw:
            raise EvidenceError(
                f"result registry receipt fingerprint is malformed: {raw}"
            )
        if verify_receipt_bytes:
            try:
                current = fingerprint(root, raw)
            except EvidenceError as exc:
                raise EvidenceError(f"registered result receipt is unavailable: {exc}") from exc
            if current != expected:
                raise EvidenceError(f"registered result receipt bytes are stale: {raw}")
    return value, path


def validate_registration_plan(root: Path, receipt_raw: str,
                               supersedes: list[str]) -> tuple[dict[str, Any], Path, list[str]]:
    registry, path = load_registry(root)
    active: list[str] = registry["active"]
    if registry["pending"]:
        raise EvidenceError(
            "retire or activate the existing pending result receipt before starting another run"
        )
    unavailable = (set(active) |
                   {entry["receipt"] for entry in registry["pending"]} |
                   {entry["receipt"] for entry in registry["retired"]})
    if receipt_raw in unavailable:
        raise EvidenceError(f"result receipt path already has lifecycle history: {receipt_raw}")
    normalized_supersedes: list[str] = []
    for raw in supersedes:
        normalized, _ = result_receipt_path(root, raw)
        if normalized == receipt_raw:
            raise EvidenceError("a receipt cannot supersede itself")
        if normalized not in active:
            raise EvidenceError(f"superseded receipt is not active: {normalized}")
        project_path(root, normalized)
        normalized_supersedes.append(normalized)
    if len(normalized_supersedes) != len(set(normalized_supersedes)):
        raise EvidenceError("--supersedes contains duplicate receipts")
    return registry, path, normalized_supersedes


def activate_result_receipt(root: Path, receipt_raw: str) -> None:
    registry, path = load_registry(root)
    matches = [entry for entry in registry["pending"] if entry["receipt"] == receipt_raw]
    if len(matches) != 1:
        raise EvidenceError(f"result receipt is not pending activation: {receipt_raw}")
    supersedes = matches[0]["supersedes"]
    recorded_supersedes = result_receipt_supersedes(root, receipt_raw)
    if recorded_supersedes != supersedes:
        raise EvidenceError(
            f"pending replacement relation disagrees with receipt: {receipt_raw}"
        )
    for raw in supersedes:
        if raw not in registry["active"]:
            raise EvidenceError(f"pending superseded receipt is no longer active: {raw}")
    registry["pending"] = [entry for entry in registry["pending"]
                           if entry["receipt"] != receipt_raw]
    registry["active"].append(receipt_raw)
    registry["active"].sort()
    load_registry(root, candidate=registry)
    atomic_json(path, registry)


def command_init_registry(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    _, path = project_path(root, REGISTRY_PATH, must_exist=False)
    if path.exists():
        raise EvidenceError(f"result registry already exists: {REGISTRY_PATH}")
    _, output = project_path(root, "output")
    if any(output.rglob("*results.receipt.json")):
        raise EvidenceError("cannot initialize registry after result receipts exist")
    atomic_json(path, empty_registry())
    print(json.dumps({"status": "INITIALIZED", "registry": REGISTRY_PATH}, sort_keys=True))
    return 0


def command_retire(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    if not isinstance(args.reason, str) or not args.reason.strip():
        raise EvidenceError("retirement reason must be non-empty")
    receipt_raw, _ = result_receipt_path(root, args.receipt)
    registry, path = load_registry(root)
    pending_match = any(entry["receipt"] == receipt_raw for entry in registry["pending"])
    if receipt_raw not in registry["active"] and not pending_match:
        raise EvidenceError(f"cannot retire receipt outside active/pending state: {receipt_raw}")
    if receipt_raw in registry["active"]:
        blockers = [entry["receipt"] for entry in registry["pending"]
                    if receipt_raw in entry["supersedes"]]
        if blockers:
            raise EvidenceError(
                "cannot retire an active receipt while pending replacements supersede it: " +
                ", ".join(blockers)
            )
        active_replacements = [
            raw for raw in registry["active"]
            if raw != receipt_raw and
            receipt_raw in result_receipt_supersedes(root, raw)
        ]
        if active_replacements:
            if args.superseded_by is None or args.superseded_by not in active_replacements:
                raise EvidenceError(
                    "retiring a predecessor requires --superseded-by naming its active "
                    "replacement: " + ", ".join(active_replacements)
                )
        registry["active"].remove(receipt_raw)
    registry["pending"] = [entry for entry in registry["pending"]
                           if entry["receipt"] != receipt_raw]
    recorded_fingerprint = registry["receipt_fingerprints"].pop(receipt_raw)
    retired_entry = {
        "receipt": receipt_raw,
        "reason": args.reason.strip(),
        "last_fingerprint": recorded_fingerprint,
    }
    if args.superseded_by is not None:
        superseded_by, _ = result_receipt_path(root, args.superseded_by)
        if superseded_by == receipt_raw or superseded_by not in registry["active"]:
            raise EvidenceError("--superseded-by must name a different active receipt")
        if receipt_raw not in result_receipt_supersedes(root, superseded_by):
            raise EvidenceError(
                "--superseded-by receipt does not declare this predecessor"
            )
        retired_entry["superseded_by"] = superseded_by
    registry["retired"].append(retired_entry)
    load_registry(root, candidate=registry)
    atomic_json(path, registry)
    print(json.dumps({"status": "RETIRED", "receipt": receipt_raw}, sort_keys=True))
    return 0


def require_active_receipt(root: Path, raw: str) -> tuple[str, Path]:
    normalized, path = result_receipt_path(root, raw)
    registry, _ = load_registry(root)
    if normalized not in registry["active"]:
        raise EvidenceError(f"result receipt is not active: {normalized}")
    project_path(root, normalized)
    return normalized, path


def require_renderable_receipt(root: Path, raw: str) -> tuple[str, Path, bool]:
    normalized, path = result_receipt_path(root, raw)
    registry, _ = load_registry(root)
    is_pending = any(entry["receipt"] == normalized for entry in registry["pending"])
    if normalized not in registry["active"] and not is_pending:
        raise EvidenceError(f"result receipt is neither active nor pending: {normalized}")
    project_path(root, normalized)
    return normalized, path, is_pending


def snapshot_paths(entries: Any) -> set[str]:
    if not isinstance(entries, list):
        return set()
    return {entry["path"] for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("path"), str)}


def lifecycle_reserved_paths(root: Path, registry: dict[str, Any], *,
                             include_active: bool = True,
                             include_pending: bool = True,
                             include_retired: bool = True) -> set[str]:
    receipt_paths = list(registry["active"]) if include_active else []
    if include_pending:
        receipt_paths.extend(entry["receipt"] for entry in registry["pending"])
    if include_retired:
        receipt_paths.extend(entry["receipt"] for entry in registry["retired"])
    reserved = set(receipt_paths)
    for receipt_raw in receipt_paths:
        _, receipt = project_path(root, receipt_raw)
        value = load_json(receipt)
        producer = value.get("producer_run") if isinstance(value, dict) else None
        if not isinstance(producer, dict):
            raise EvidenceError(f"lifecycle receipt is malformed: {receipt_raw}")
        bundle = producer.get("bundle")
        if isinstance(bundle, dict) and isinstance(bundle.get("path"), str):
            reserved.add(bundle["path"])
        plan = producer.get("plan")
        if isinstance(plan, dict) and isinstance(plan.get("path"), str):
            reserved.add(plan["path"])
        reserved |= snapshot_paths(producer.get("code"))
        reserved |= snapshot_paths(producer.get("inputs"))
        reserved |= snapshot_paths(producer.get("renderer_code"))
        reserved |= snapshot_paths(producer.get("artifacts"))
        render = value.get("render_run")
        if isinstance(render, dict):
            reserved |= snapshot_paths(render.get("code"))
            reserved |= snapshot_paths(render.get("exhibits"))
    return reserved


def command_run(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    command = actual_command(args.command)
    entrypoint = command_entrypoint(command)
    plan_raw, plan_path = project_path(root, args.plan)
    reject_audit_namespace(plan_raw, "run plan")
    plan = validate_run_plan(load_json(plan_path), root)
    if entrypoint not in plan["producer_code"]:
        raise EvidenceError("producer command entrypoint is not declared in the pre-run plan")
    bundle_raw, bundle_target = project_path(root, args.bundle, must_exist=False)
    if not bundle_raw.startswith("output/"):
        raise EvidenceError("result bundle path must be under output/")
    reject_audit_namespace(bundle_raw, "result bundle")
    receipt_raw, target = result_receipt_path(root, args.receipt)
    if bundle_target.exists():
        raise EvidenceError(f"new result bundle path already exists: {bundle_raw}")
    if target.exists():
        raise EvidenceError(f"new result receipt path already exists: {receipt_raw}")
    if bundle_raw == receipt_raw:
        raise EvidenceError("bundle and receipt paths must be different")
    registry, registry_path, supersedes = validate_registration_plan(
        root, receipt_raw, args.supersedes
    )
    reserved = lifecycle_reserved_paths(
        root, registry, include_active=True, include_pending=False, include_retired=False
    )
    historical_reserved = lifecycle_reserved_paths(
        root, registry, include_active=False, include_pending=True, include_retired=True
    )
    collision = overlapping_pair({plan_raw, bundle_raw, receipt_raw} | set(plan["artifacts"]) |
                                 set(plan["exhibits"]), reserved)
    if collision is not None:
        raise EvidenceError("new run would overwrite active evidence: " + " / ".join(collision))
    # Code may be a shared dependency used by many versioned attempts. Plans,
    # outputs, and receipts are attempt-owned and can never be reused.
    attempt_namespace = ({plan_raw, bundle_raw, receipt_raw} | set(plan["artifacts"]) |
                         set(plan["exhibits"]))
    historical_collision = overlapping_pair(attempt_namespace, historical_reserved)
    if historical_collision is not None:
        raise EvidenceError(
            "new run would reuse a pending/retired attempt namespace: " +
            " / ".join(historical_collision)
        )
    declared_paths = ({plan_raw, bundle_raw, receipt_raw} | set(plan["producer_code"]) |
                      set(plan["producer_inputs"]) | set(plan["renderer_code"]) |
                      set(plan["artifacts"]) | set(plan["exhibits"]))
    if overlapping_pair({bundle_raw, receipt_raw}, declared_paths - {bundle_raw, receipt_raw}) is not None:
        raise EvidenceError("bundle/receipt paths must not overlap declared evidence paths")
    source_paths = ({plan_raw} | set(plan["producer_code"]) |
                    set(plan["producer_inputs"]) | set(plan["renderer_code"]))
    output_source_overlap = overlapping_pair(
        set(plan["artifacts"]) | set(plan["exhibits"]), source_paths
    )
    if output_source_overlap is not None:
        raise EvidenceError("run outputs must not overlap declared code/inputs/plan: " +
                            " / ".join(output_source_overlap))
    for raw in plan["artifacts"] + plan["exhibits"]:
        _, output = project_path(root, raw, must_exist=False)
        if output.exists():
            raise EvidenceError(f"declared run output already exists before analysis: {raw}")
    plan_snapshot = fingerprint(root, plan_raw)
    code_snapshot = fingerprint_many(root, plan["producer_code"])
    input_snapshot = fingerprint_many(root, plan["producer_inputs"])
    renderer_snapshot = fingerprint_many(root, plan["renderer_code"])
    registry_snapshot = fingerprint(root, REGISTRY_PATH)
    active_snapshots = [fingerprint(root, raw) for raw in registry["active"]]
    active_failures: list[str] = []
    replaceable_prefixes = (
        "producer_run.code:", "producer_run.inputs:",
        "producer_run.renderer_code:", "render_run.code:",
    )
    for raw in registry["active"]:
        failures = verify_receipt(root, root / raw, rerender=False)["failures"]
        if failures and (not supersedes or
                         any(not item.startswith(replaceable_prefixes) for item in failures)):
            active_failures.extend(f"{raw}: {item}" for item in failures)
    if active_failures:
        raise EvidenceError("active evidence is stale before analysis: " + "; ".join(active_failures))
    registry_before = json.loads(json.dumps(registry))
    workspace_sources = [plan_raw, *plan["producer_code"], *plan["producer_inputs"],
                         *plan["renderer_code"]]
    workspace_outputs = [bundle_raw, *plan["artifacts"], *plan["exhibits"]]
    with isolated_workspace(root, workspace_sources, workspace_outputs) as workspace:
        execute(
            command, workspace, bundle_path=bundle_raw, project_root=root,
            provider_credentials=set(plan["provider_credentials"]),
        )
        isolated_source_failures = compare_snapshot(
            workspace, [plan_snapshot, *code_snapshot, *input_snapshot, *renderer_snapshot],
            "isolated producer source",
        )
        if isolated_source_failures:
            raise EvidenceError("analysis mutated its isolated declared sources: " +
                                "; ".join(isolated_source_failures))
        _, staged_bundle = project_path(workspace, bundle_raw, must_exist=False)
        if not staged_bundle.exists():
            raise EvidenceError("analysis command did not freshly create RESULTS_BUNDLE_PATH")
        created_exhibits = []
        for raw in plan["exhibits"]:
            _, exhibit_path = project_path(workspace, raw, must_exist=False)
            if exhibit_path.exists() or exhibit_path.is_symlink():
                created_exhibits.append(raw)
        if created_exhibits:
            raise EvidenceError(
                "analysis wrote renderer-owned exhibit paths: " + ", ".join(created_exhibits)
            )
        bundle = validate_bundle(load_json(staged_bundle), workspace)
        command_uses_declared_code(command, bundle["producer"]["code"], "producer")
        if (bundle["producer"]["code"] != plan["producer_code"] or
                bundle["producer"]["inputs"] != plan["producer_inputs"] or
                bundle["renderer"]["code"] != plan["renderer_code"] or
                [entry["path"] for entry in bundle["artifacts"]] != plan["artifacts"] or
                [entry["path"] for entry in bundle["exhibits"]] != plan["exhibits"]):
            raise EvidenceError("result bundle does not exactly match the pre-run plan")
        own_paths = (set(bundle["producer"]["code"]) |
                     set(bundle["producer"]["inputs"]) |
                     {entry["path"] for entry in bundle["artifacts"]} |
                     {entry["path"] for entry in bundle["exhibits"]})
        if overlapping_pair({bundle_raw, receipt_raw}, own_paths) is not None:
            raise EvidenceError("bundle/receipt paths must not overlap declared evidence paths")
        output_paths = ({entry["path"] for entry in bundle["artifacts"]} |
                        {entry["path"] for entry in bundle["exhibits"]})
        collisions = overlapping_pair(output_paths, reserved)
        if collisions is not None:
            raise EvidenceError(
                "new run would overwrite active evidence: " + " / ".join(collisions)
            )
        precommit_failures = compare_snapshot(root, [plan_snapshot], "run plan")
        precommit_failures.extend(compare_snapshot(root, code_snapshot, "pre-run producer code"))
        precommit_failures.extend(compare_snapshot(root, input_snapshot, "pre-run producer inputs"))
        precommit_failures.extend(compare_snapshot(root, renderer_snapshot,
                                                   "pre-run renderer code"))
        precommit_failures.extend(compare_snapshot(root, [registry_snapshot], "results registry"))
        precommit_failures.extend(compare_snapshot(root, active_snapshots, "active receipt"))
        for raw in registry["active"]:
            failures = verify_receipt(root, root / raw, rerender=False)["failures"]
            if failures and (not supersedes or
                             any(not item.startswith(replaceable_prefixes)
                                 for item in failures)):
                precommit_failures.extend(failures)
        if precommit_failures:
            raise EvidenceError("declared or active evidence changed during analysis: " +
                                "; ".join(precommit_failures))
        transaction = prepare_lifecycle_transaction(
            root,
            cleanup_paths=[bundle_raw, receipt_raw, *plan["artifacts"]],
            restore_paths=[], registry_before=registry_before,
        )
        try:
            for raw in plan["artifacts"]:
                publish_workspace_path(root, workspace, raw)
            publish_workspace_path(root, workspace, bundle_raw)
            bundle, bundle_raw, _ = bundle_and_path(root, bundle_raw)
            receipt = {
                "kind": "result",
                "receipt_version": RECEIPT_VERSION,
                "supersedes": supersedes,
                "producer_run": snapshot_bundle(
                    root, bundle, bundle_raw, command, plan_raw,
                    code_snapshot, input_snapshot, renderer_snapshot
                ),
                "render_run": None,
            }
            atomic_json(target, receipt)
            registry["pending"].append({"receipt": receipt_raw, "supersedes": supersedes})
            registry["receipt_fingerprints"][receipt_raw] = fingerprint(root, receipt_raw)
            load_registry(root, candidate=registry)
            atomic_json(registry_path, registry)
        except BaseException:
            rollback_lifecycle_transaction(root, transaction)
            raise
        commit_lifecycle_transaction(root)
    status = "PENDING_RENDER" if bundle["exhibits"] else "PENDING_ACTIVATION"
    print(json.dumps({"status": status, "receipt": args.receipt}, sort_keys=True))
    return 0


def command_render(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    receipt_raw, target, is_pending = require_renderable_receipt(root, args.receipt)
    receipt = load_json(target)
    if (not isinstance(receipt, dict) or receipt.get("kind") != "result" or
            isinstance(receipt.get("receipt_version"), bool) or
            receipt.get("receipt_version") != RECEIPT_VERSION):
        raise EvidenceError(f"not a results receipt v{RECEIPT_VERSION}: {args.receipt}")
    producer = receipt.get("producer_run")
    bundle_field = producer.get("bundle") if isinstance(producer, dict) else None
    if not isinstance(bundle_field, dict) or not isinstance(bundle_field.get("path"), str):
        raise EvidenceError("receipt has no usable producer bundle")
    preliminary = verify_receipt(root, target, rerender=False)
    # A missing or stale render_run is exactly what this command refreshes; every
    # producer-side condition must still stop before presentation code executes.
    non_render_failures = [failure for failure in preliminary["failures"]
                           if not failure.startswith("render_run")]
    if non_render_failures:
        raise EvidenceError("producer receipt is stale: " + "; ".join(non_render_failures))
    bundle, _, _ = bundle_and_path(root, bundle_field["path"])
    command = actual_command(args.command)
    command_uses_declared_code(command, bundle["renderer"]["code"], "renderer")
    prior_render = receipt.get("render_run")
    expected_exhibits: list[dict[str, Any]] | None = None
    if not is_pending:
        if not isinstance(prior_render, dict):
            raise EvidenceError("active receipt has no immutable render record")
        if prior_render.get("command") != command:
            raise EvidenceError(
                "active receipt may be rerendered only with its exact recorded command"
            )
        recorded_exhibits = prior_render.get("exhibits")
        if not isinstance(recorded_exhibits, list):
            raise EvidenceError("active receipt has malformed recorded exhibits")
        expected_exhibits = recorded_exhibits
    registry_before, registry_path = load_registry(root)
    existing_exhibits: list[str] = []
    absent_exhibits: list[str] = []
    for exhibit in bundle["exhibits"]:
        raw, path = project_path(root, exhibit["path"], must_exist=False)
        (existing_exhibits if path.exists() else absent_exhibits).append(raw)
    transaction = prepare_lifecycle_transaction(
        root, cleanup_paths=absent_exhibits,
        restore_paths=[receipt_raw, *existing_exhibits],
        registry_before=json.loads(json.dumps(registry_before)),
    )
    try:
        execute_fresh_exhibits(
            command, root, bundle, bundle_field["path"],
            expected=expected_exhibits,
        )
        rendered_snapshot = snapshot_render(root, bundle, command)
        # Rendering must not mutate the evidence it consumes.
        producer_failures: list[str] = []
        for key in ("plan", "bundle", "code", "inputs", "renderer_code", "artifacts"):
            value = producer[key]
            entries = [value] if key in {"plan", "bundle"} else value
            producer_failures.extend(compare_snapshot(root, entries, f"producer_run.{key}"))
        if producer_failures:
            raise EvidenceError("renderer mutated producer evidence: " +
                                "; ".join(producer_failures))
        if is_pending:
            receipt["render_run"] = rendered_snapshot
            atomic_json(target, receipt)
            registry_after = json.loads(json.dumps(registry_before))
            registry_after["receipt_fingerprints"][receipt_raw] = fingerprint(
                root, receipt_raw
            )
            load_registry(root, candidate=registry_after)
            atomic_json(registry_path, registry_after)
            final = verify_receipt(root, target, rerender=False)
            if final["failures"]:
                raise EvidenceError("cannot record stale rendered receipt: " +
                                    "; ".join(final["failures"]))
        elif rendered_snapshot != prior_render:
            raise EvidenceError("active rerender changed immutable render metadata")
    except BaseException:
        rollback_lifecycle_transaction(root, transaction)
        raise
    commit_lifecycle_transaction(root)
    print(json.dumps({"status": "RENDERED_PENDING" if is_pending else "RERENDERED",
                      "receipt": args.receipt}, sort_keys=True))
    return 0


def command_activate(args: argparse.Namespace) -> int:
    """Activate one reviewed pending receipt before pointer handoff and retirement."""
    root = resolve_root(args.project_root)
    receipt_raw, target, is_pending = require_renderable_receipt(root, args.receipt)
    if not is_pending:
        raise EvidenceError(f"result receipt is already active: {receipt_raw}")
    report = verify_receipt(root, target, rerender=False)
    if report["failures"]:
        raise EvidenceError("cannot activate stale result receipt: " +
                            "; ".join(report["failures"]))
    registry_before, _ = load_registry(root)
    pending_entry = next(
        entry for entry in registry_before["pending"] if entry["receipt"] == receipt_raw
    )
    transaction = prepare_lifecycle_transaction(
        root, cleanup_paths=[], restore_paths=[],
        registry_before=json.loads(json.dumps(registry_before)),
    )
    try:
        activate_result_receipt(root, receipt_raw)
    except BaseException:
        rollback_lifecycle_transaction(root, transaction)
        raise
    commit_lifecycle_transaction(root)
    print(json.dumps({"status": "ACTIVE", "receipt": receipt_raw,
                      "supersedes_to_retire": pending_entry["supersedes"]}, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    _, target, _ = require_renderable_receipt(root, args.receipt)
    result = verify_receipt(root, target, rerender=args.rerender)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def command_verify_all(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    paths = discover_result_receipts(root)
    if args.require_one and not paths:
        result = {"status": "STALE", "receipts": [],
                  "failures": ["no result receipts found under output/"]}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    reports: list[dict[str, Any]] = []
    failures: list[str] = []
    for path in paths:
        try:
            report = verify_receipt(root, path, rerender=args.rerender)
        except EvidenceError as exc:
            report = {"receipt": str(path.relative_to(root)), "status": "STALE",
                      "failures": [str(exc)]}
        reports.append(report)
        failures.extend(f"{report['receipt']}: {item}" for item in report["failures"])
    result = {"status": "PASS" if not failures else "STALE", "receipts": reports,
              "failures": failures}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


def discover_result_receipts(root: Path) -> list[Path]:
    registry, _ = load_registry(root)
    _, output = project_path(root, "output")
    if not output.is_dir():
        raise EvidenceError("output/ must be a real directory")
    candidates = sorted(output.rglob("*results.receipt.json"))
    disk_paths = {path.relative_to(root).as_posix(): path for path in candidates}
    active = set(registry["active"])
    pending = {entry["receipt"] for entry in registry["pending"]}
    retired = {entry["receipt"] for entry in registry["retired"]}
    undeclared = sorted(set(disk_paths) - active - pending - retired)
    missing = sorted((active | pending | retired) - set(disk_paths))
    if undeclared:
        raise EvidenceError("result receipts absent from registry: " + ", ".join(undeclared))
    if missing:
        raise EvidenceError("registry-declared result receipts are missing: " + ", ".join(missing))
    retired_failures: list[str] = []
    for entry in registry["retired"]:
        retired_failures.extend(compare_snapshot(
            root, [entry["last_fingerprint"]], "retired receipt history"
        ))
    if retired_failures:
        raise EvidenceError("retired receipt history is stale: " + "; ".join(retired_failures))
    if pending:
        raise EvidenceError(
            "pending result receipts must render or be explicitly retired before audit: " +
            ", ".join(sorted(pending))
        )
    retired_by_path = {entry["receipt"]: entry for entry in registry["retired"]}
    incomplete_handoffs: list[str] = []
    invalid_handoffs: list[str] = []
    for replacement in sorted(active):
        for predecessor in result_receipt_supersedes(root, replacement):
            if predecessor in active:
                incomplete_handoffs.append(f"{replacement} -> {predecessor}")
                continue
            retired_entry = retired_by_path.get(predecessor)
            if retired_entry is None or retired_entry.get("superseded_by") != replacement:
                invalid_handoffs.append(f"{replacement} -> {predecessor}")
    if incomplete_handoffs:
        raise EvidenceError(
            "activated replacement handoff is incomplete; update the stage pointer and "
            "retire each predecessor with --superseded-by: " +
            ", ".join(incomplete_handoffs)
        )
    if invalid_handoffs:
        raise EvidenceError(
            "active replacement has no matching retired predecessor record: " +
            ", ".join(invalid_handoffs)
        )
    paths: list[Path] = []
    for raw in sorted(active):
        path = disk_paths[raw]
        value = load_json(path)
        if not isinstance(value, dict) or value.get("kind") != "result":
            raise EvidenceError(f"reserved result-receipt path is not a result receipt: {path}")
        paths.append(path)
    return paths


def uncomment_latex(text: str) -> str:
    return "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0]
                     for line in text.splitlines())


def resolve_latex_dependency(root: Path, paper: Path, current: Path, raw: str,
                             extensions: tuple[str, ...], *, required: bool) -> Path | None:
    raw = raw.strip()
    if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
        if required:
            raise EvidenceError(f"dynamic LaTeX dependency cannot be audited: {raw!r}")
        return None
    candidates: list[Path] = []
    for base in (paper, current.parent):
        candidate = base / raw
        choices = ([candidate] if candidate.suffix else
                   [candidate, *(candidate.with_suffix(ext) for ext in extensions)])
        candidates.extend(choices)
    for candidate in candidates:
        if candidate.exists():
            try:
                normalized_candidate = Path(os.path.abspath(candidate))
                relative = normalized_candidate.relative_to(root.absolute()).as_posix()
            except ValueError as exc:
                raise EvidenceError(f"LaTeX dependency escapes the project: {raw}") from exc
            _, checked = project_path(root, relative)
            if not checked.is_file():
                raise EvidenceError(f"LaTeX dependency is not a regular file: {relative}")
            return checked
    if required:
        raise EvidenceError(f"cannot resolve LaTeX dependency from {current}: {raw}")
    return None


def citation_occurrences(text: str, relative: str) -> list[dict[str, Any]]:
    """Inventory supported citation commands and reject every unknown cite-family command."""
    recognized_spans: list[tuple[int, int]] = []
    citations: list[dict[str, Any]] = []
    for ordinal, match in enumerate(CITATION_RE.finditer(text), start=1):
        recognized_spans.append(match.span())
        line_number = text.count("\n", 0, match.start()) + 1
        groups = re.findall(r"\{([^}]+)\}", match.group("arguments"))
        command = match.group("command").lower()
        if command == "citefield":
            if len(groups) != 2:
                raise EvidenceError(
                    f"malformed citefield command at {relative}:{line_number}"
                )
            groups = groups[:1]
        elif command.endswith("volcite") or command.endswith("volcites"):
            if len(groups) < 2 or len(groups) % 2:
                raise EvidenceError(
                    f"malformed volume citation at {relative}:{line_number}"
                )
            groups = groups[1::2]
        keys = [key.strip() for group in groups
                for key in group.split(",") if key.strip()]
        if not keys or any(not CITE_KEY_RE.fullmatch(key) for key in keys):
            raise EvidenceError(
                f"dynamic or malformed citation key at {relative}:{line_number}"
            )
        paragraph_start = text.rfind("\n\n", 0, match.start()) + 2
        paragraph_end = text.find("\n\n", match.end())
        if paragraph_end < 0:
            paragraph_end = len(text)
        claim_text = re.sub(r"\s+", " ", text[paragraph_start:paragraph_end]).strip()
        citations.append({
            "occurrence_id": f"{relative}:{line_number}:cite{ordinal}",
            "cite_keys": keys,
            "claim_text": claim_text,
        })
    for match in CITATION_FAMILY_RE.finditer(text):
        command = match.group("command").lower()
        if command in NON_OCCURRENCE_CITATION_COMMANDS:
            continue
        if not any(start <= match.start() < end for start, end in recognized_spans):
            line_number = text.count("\n", 0, match.start()) + 1
            raise EvidenceError(
                f"unsupported citation-family command \\{command} at "
                f"{relative}:{line_number}"
            )
    return citations


def paper_dependency_graph(root: Path) -> tuple[list[str], list[dict[str, Any]]]:
    paper = root / "paper"
    if not paper.is_dir() or paper.is_symlink():
        raise EvidenceError("paper/ must be a real directory before binding an evidence audit")
    roots = [paper / "main.tex"]
    appendix = paper / "internet_appendix.tex"
    if appendix.exists():
        roots.append(appendix)
    if not roots[0].is_file():
        raise EvidenceError("paper/main.tex is required for evidence binding")
    pending = list(roots)
    paths: set[str] = set()
    citations: list[dict[str, Any]] = []
    seen_sources: set[Path] = set()
    while pending:
        current = pending.pop()
        relative = current.relative_to(root).as_posix()
        if current in seen_sources:
            continue
        seen_sources.add(current)
        project_path(root, relative)
        paths.add(relative)
        text = uncomment_latex(current.read_text(encoding="utf-8"))
        citations.extend(citation_occurrences(text, relative))
        unsupported = re.search(
            r"\\(?:(?:import|subimport|inputfrom|includefrom|subinputfrom|subincludefrom|"
            r"graphicspath|DTLloaddb|loadglsentries)\s*\{|"
            r"CatchFile(?:Def|Edef)(?![A-Za-z@])|openin(?![A-Za-z@]))",
            text,
        )
        if unsupported:
            raise EvidenceError(
                f"unsupported dynamic LaTeX dependency command in {relative}: "
                f"{unsupported.group(0)}"
            )
        if current.suffix.lower() != ".tex":
            # Local package/class bytes are bound, and their static local
            # dependencies are followed. Parameterized macro bodies are
            # ignored (for example a wrapper's `\includegraphics{#1}`), since
            # their concrete invocation is visible in a document source.
            for match in re.finditer(
                    r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
                for raw in match.group(1).split(","):
                    raw = raw.strip()
                    if any(token in raw for token in ("\\", "{", "}", "#")):
                        raise EvidenceError(
                            f"dynamic local package dependency in {relative}: {raw!r}"
                        )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, (".sty",), required=False
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
                        pending.append(dependency)
            for match in re.finditer(
                    r"\\documentclass\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
                raw = match.group(1).strip()
                if any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic local class dependency in {relative}: {raw!r}"
                    )
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".cls",), required=False
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
                    pending.append(dependency)
            guarded_files: set[str] = set()
            for match in re.finditer(
                    r"\\(?:Input)?IfFileExists\s*\{([^}]+)\}", text):
                raw = match.group(1).strip()
                if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic conditional dependency cannot be audited in {relative}: {raw!r}"
                    )
                guarded_files.add(PurePosixPath(raw).as_posix())
                dependency = resolve_latex_dependency(
                    root, paper, current, raw,
                    (".tex", ".sty", ".cls", ".cfg", ".def", ".bib", ".pdf", ".png"),
                    required=False,
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
                    if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                        pending.append(dependency)
            static_patterns: tuple[tuple[str, tuple[str, ...]], ...] = (
                (r"\\(?:input|include|subfile)(?![A-Za-z])\s*\{([^}]+)\}",
                 (".tex", ".sty", ".cls", ".cfg", ".def")),
                (r"\\(?:lstinputlisting|VerbatimInput)\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
                 (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
                (r"\\inputminted\s*(?:\[[^\]]*\]\s*)?\{[^}]+\}\s*\{([^}]+)\}",
                 (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
                (r"\\(?:csvreader|pgfplotstableread|pgfplotstabletypeset)"
                 r"\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
                 (".csv", ".tsv", ".txt", ".dat")),
                (r"\\addplot(?:3)?\+?(?:\s*\[[^\]]*\])?\s+table"
                 r"(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}",
                 (".csv", ".tsv", ".txt", ".dat")),
                (r"\\addplot(?:3)?\+?(?:\s*\[[^\]]*\])?\s+file\s*\{([^}]+)\}",
                 (".csv", ".tsv", ".txt", ".dat")),
                (r"\\includegraphics\*?\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
                 (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps")),
                (r"\\includepdf\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
                 (".pdf",)),
            )
            for pattern, extensions in static_patterns:
                for match in re.finditer(pattern, text):
                    raw = match.group(1).strip()
                    if any(token in raw for token in ("\\", "{", "}", "#")):
                        definition_prefix = text[max(0, match.start() - 24):match.start()]
                        if re.search(r"\\(?:g|x|e)?def\s*$", definition_prefix):
                            # This is the command token being defined, not a
                            # file read (for example `\def\includegraphics`).
                            continue
                        raise EvidenceError(
                            "dynamic local package/class dependency cannot be audited in "
                            f"{relative}: {raw!r}"
                        )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, extensions, required=False
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
                        if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                            pending.append(dependency)
            for match in re.finditer(
                    r"\\(?:bibliography|addbibresource)\s*"
                    r"(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
                for raw in match.group(1).split(","):
                    raw = raw.strip()
                    if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                        raise EvidenceError(
                            f"dynamic bibliography dependency in {relative}: {raw!r}"
                        )
                    guarded = raw in guarded_files or (
                        not PurePosixPath(raw).suffix and f"{raw}.bib" in guarded_files
                    )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, (".bib",), required=not guarded
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
            continue
        for match in re.finditer(
                r"\\(?:input|include|subfile)(?![A-Za-z])\s*"
                r"(?:\{([^}]+)\}|([^\s%{}]+))", text):
            dependency = resolve_latex_dependency(
                root, paper, current, match.group(1) or match.group(2),
                (".tex",), required=True
            )
            assert dependency is not None
            pending.append(dependency)
        guarded_files: set[str] = set()
        for match in re.finditer(r"\\(?:Input)?IfFileExists\s*\{([^}]+)\}", text):
            raw = match.group(1).strip()
            if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                raise EvidenceError(
                    f"dynamic IfFileExists dependency cannot be audited in {relative}: {raw!r}"
                )
            guarded_files.add(PurePosixPath(raw).as_posix())
            dependency = resolve_latex_dependency(
                root, paper, current, raw,
                (".tex", ".bib", ".sty", ".cls", ".pdf", ".png"), required=False
            )
            if dependency is not None:
                paths.add(dependency.relative_to(root).as_posix())
                if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                    pending.append(dependency)
        data_patterns: tuple[tuple[str, tuple[str, ...]], ...] = (
            (r"\\(?:lstinputlisting|VerbatimInput)\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
             (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
            (r"\\inputminted\s*(?:\[[^\]]*\]\s*)?\{[^}]+\}\s*\{([^}]+)\}",
             (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
            (r"\\(?:csvreader|pgfplotstableread|pgfplotstabletypeset)"
             r"\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}",
             (".csv", ".tsv", ".txt", ".dat")),
            (r"\\addplot(?:3)?\+?(?:\s*\[[^\]]*\])?\s+table"
             r"(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}",
             (".csv", ".tsv", ".txt", ".dat")),
            (r"\\addplot(?:3)?\+?(?:\s*\[[^\]]*\])?\s+file\s*\{([^}]+)\}",
             (".csv", ".tsv", ".txt", ".dat")),
        )
        for pattern, extensions in data_patterns:
            for match in re.finditer(pattern, text):
                dependency = resolve_latex_dependency(
                    root, paper, current, match.group(1), extensions, required=True
                )
                assert dependency is not None
                paths.add(dependency.relative_to(root).as_posix())
        for match in re.finditer(
                r"\\includegraphics\*?\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
            dependency = resolve_latex_dependency(
                root, paper, current, match.group(1),
                (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps"), required=True
            )
            assert dependency is not None
            paths.add(dependency.relative_to(root).as_posix())
        for match in re.finditer(
                r"\\includepdf\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
            dependency = resolve_latex_dependency(
                root, paper, current, match.group(1), (".pdf",), required=True
            )
            assert dependency is not None
            paths.add(dependency.relative_to(root).as_posix())
        for match in re.finditer(
                r"\\(?:bibliography|addbibresource)\s*"
                r"(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
            for raw in match.group(1).split(","):
                raw = raw.strip()
                if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic bibliography dependency in {relative}: {raw!r}"
                    )
                guarded = raw in guarded_files or (
                    not PurePosixPath(raw).suffix and f"{raw}.bib" in guarded_files
                )
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".bib",), required=not guarded
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
        for match in re.finditer(
                r"\\(?:usepackage|RequirePackage)\s*"
                r"(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
            for raw in match.group(1).split(","):
                raw = raw.strip()
                if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic package dependency in {relative}: {raw!r}"
                    )
                explicit_local = "/" in raw or PurePosixPath(raw).suffix == ".sty"
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".sty",), required=explicit_local
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
                    pending.append(dependency)
        for match in re.finditer(
                r"\\documentclass\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}", text):
            raw = match.group(1).strip()
            if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                raise EvidenceError(f"dynamic class dependency in {relative}: {raw!r}")
            explicit_local = "/" in raw or PurePosixPath(raw).suffix == ".cls"
            dependency = resolve_latex_dependency(
                root, paper, current, raw, (".cls",), required=explicit_local
            )
            if dependency is not None:
                paths.add(dependency.relative_to(root).as_posix())
                pending.append(dependency)
        for match in re.finditer(r"\\bibliographystyle\s*\{([^}]+)\}", text):
            raw = match.group(1).strip()
            if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                raise EvidenceError(
                    f"dynamic bibliography-style dependency in {relative}: {raw!r}"
                )
            explicit_local = "/" in raw or PurePosixPath(raw).suffix == ".bst"
            dependency = resolve_latex_dependency(
                root, paper, current, raw, (".bst",), required=explicit_local
            )
            if dependency is not None:
                paths.add(dependency.relative_to(root).as_posix())
    return sorted(paths), citations


def paper_source_paths(root: Path) -> list[str]:
    return paper_dependency_graph(root)[0]


def expected_result_exhibits(root: Path, result_paths: list[Path],
                             paper_paths: list[str]) -> list[str]:
    included = set(paper_paths)
    expected: set[str] = set()
    for receipt_path_value in result_paths:
        receipt = load_json(receipt_path_value)
        producer = receipt.get("producer_run") if isinstance(receipt, dict) else None
        bundle_field = producer.get("bundle") if isinstance(producer, dict) else None
        if not isinstance(bundle_field, dict) or not isinstance(bundle_field.get("path"), str):
            raise EvidenceError(f"receipt has no usable producer bundle: {receipt_path_value}")
        bundle, _, _ = bundle_and_path(root, bundle_field["path"])
        expected.update(entry["path"] for entry in bundle["exhibits"]
                        if entry["path"] in included)
    return sorted(expected)


def validate_audit_input(root: Path, path: Path, checkpoint: str) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise EvidenceError("audit input must be an object")
    required = {"kind", "audit_input_version", "checkpoint", "paper_sources",
                "result_receipts", "results_registry", "citation_occurrences",
                "included_result_exhibits", "digest"}
    _require_keys(value, required, required, "audit input")
    if (value["kind"] != "paper_audit_input" or
            isinstance(value["audit_input_version"], bool) or
            value["audit_input_version"] != AUDIT_INPUT_VERSION):
        raise EvidenceError(f"not a paper audit input v{AUDIT_INPUT_VERSION}")
    if value["checkpoint"] != checkpoint:
        raise EvidenceError("audit input checkpoint mismatch")
    unsigned = {key: item for key, item in value.items() if key != "digest"}
    if value["digest"] != object_digest(unsigned):
        raise EvidenceError("audit input digest is invalid")
    failures: list[str] = []
    for key in ("paper_sources", "result_receipts"):
        if not isinstance(value[key], list):
            raise EvidenceError(f"audit input {key} must be an array")
        failures.extend(compare_snapshot(root, value[key], f"audit input {key}"))
    registry = value["results_registry"]
    if not isinstance(registry, dict):
        raise EvidenceError("audit input results_registry must be a fingerprint")
    failures.extend(compare_snapshot(root, [registry], "audit input results_registry"))
    current_receipts = [path.relative_to(root).as_posix()
                        for path in discover_result_receipts(root)]
    recorded_receipts = [entry.get("path") for entry in value["result_receipts"]]
    if sorted(recorded_receipts) != sorted(current_receipts):
        failures.append("active result receipt inventory changed after audit preparation")
    current_paper, current_citations = paper_dependency_graph(root)
    recorded_paper = [entry.get("path") for entry in value["paper_sources"]
                      if isinstance(entry, dict)]
    if recorded_paper != current_paper:
        failures.append("transitive paper dependency inventory changed after audit preparation")
    if value["citation_occurrences"] != current_citations:
        failures.append("citation occurrence inventory changed after audit preparation")
    if value["included_result_exhibits"] != expected_result_exhibits(
            root, [root / raw for raw in current_receipts], current_paper):
        failures.append("included result-exhibit inventory changed after audit preparation")
    if failures:
        raise EvidenceError("audit input is stale: " + "; ".join(failures))
    return value


def command_prepare_audit(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    output_raw, output_path = evidence_artifact_path(root, args.output)
    if not output_raw.endswith(".json"):
        raise EvidenceError("prepared audit input path must end with .json")
    registry, _ = load_registry(root)
    collision = overlapping_pair({output_raw}, lifecycle_reserved_paths(root, registry))
    if collision is not None:
        raise EvidenceError(
            "audit output would overwrite result lifecycle evidence: " +
            " / ".join(collision)
        )
    result_paths = discover_result_receipts(root)
    reports = [verify_receipt(root, path, rerender=True) for path in result_paths]
    failures = [f"{report['receipt']}: {failure}" for report in reports
                for failure in report["failures"]]
    if failures:
        raise EvidenceError("cannot prepare audit from stale results: " + "; ".join(failures))
    paper_sources, citation_occurrences = paper_dependency_graph(root)
    result_receipts = [path.relative_to(root).as_posix() for path in result_paths]
    payload = {
        "kind": "paper_audit_input",
        "audit_input_version": AUDIT_INPUT_VERSION,
        "checkpoint": args.checkpoint,
        "paper_sources": fingerprint_many(root, paper_sources),
        "result_receipts": fingerprint_many(root, result_receipts),
        "results_registry": fingerprint(root, REGISTRY_PATH),
        "citation_occurrences": citation_occurrences,
        "included_result_exhibits": expected_result_exhibits(
            root, result_paths, paper_sources
        ),
    }
    payload["digest"] = object_digest(payload)
    atomic_json(output_path, payload)
    validate_audit_input(root, output_path, args.checkpoint)
    print(json.dumps({"status": "PREPARED", "input": output_raw,
                      "digest": payload["digest"], "checkpoint": args.checkpoint},
                     sort_keys=True))
    return 0


def command_verify_audit_input(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    input_raw, input_path = evidence_artifact_path(root, args.input, must_exist=True)
    value = validate_audit_input(root, input_path, args.checkpoint)
    print(json.dumps({"status": "PASS", "input": input_raw,
                      "digest": value["digest"], "checkpoint": args.checkpoint},
                     sort_keys=True))
    return 0


def validate_audit_report(path: Path, checkpoint: str, audit_input_digest: str,
                          label: str) -> None:
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
                 if line.strip()]
    except OSError as exc:
        raise EvidenceError(f"cannot read {label} audit report: {exc}") from exc
    verdict_lines = [line for line in lines if line.startswith("VERDICT:")]
    checkpoint_lines = [line for line in lines if line.startswith("CHECKPOINT:")]
    digest_lines = [line for line in lines if line.startswith("AUDIT_INPUT_DIGEST:")]
    expected = ["VERDICT: PASS", f"CHECKPOINT: {checkpoint}",
                f"AUDIT_INPUT_DIGEST: {audit_input_digest}"]
    if (lines[:3] != expected or verdict_lines != [expected[0]] or
            checkpoint_lines != [expected[1]] or digest_lines != [expected[2]]):
        raise EvidenceError(
            f"{label} audit report must contain one consistent PASS/checkpoint/digest header"
        )
    for index, line in enumerate(lines[:-1]):
        if re.fullmatch(r"#{1,6}\s+verdict", line, flags=re.IGNORECASE):
            if lines[index + 1].upper() != "PASS":
                raise EvidenceError(f"{label} audit report contains a conflicting verdict")


def validate_audit_summary(value: Any, checkpoint: str, *, label: str = "evidence") -> None:
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} audit summary must be an object")
    required = {"verdict", "checkpoint", "blocking_findings"}
    missing = sorted(required - value.keys())
    if missing:
        raise EvidenceError(f"{label} audit summary missing keys: {', '.join(missing)}")
    if value["verdict"] != "PASS":
        raise EvidenceError(f"cannot bind non-PASS {label} audit: {value['verdict']!r}")
    if value["checkpoint"] != checkpoint:
        raise EvidenceError(
            f"audit checkpoint mismatch: expected {checkpoint!r}, got {value['checkpoint']!r}"
        )
    if value["blocking_findings"] != []:
        raise EvidenceError("PASS audit must have an empty blocking_findings array")


def validate_citation_summary(value: Any, checkpoint: str, audit_input_path: str,
                              audit_input_digest: str,
                              expected_occurrences: list[dict[str, Any]],
                              prior_claims: list[dict[str, Any]]) -> None:
    validate_audit_summary(value, checkpoint, label="citation")
    assert isinstance(value, dict)
    required = {"verdict", "checkpoint", "blocking_findings", "audit_input_path",
                "audit_input_digest", "citation_claims", "fresh_checks",
                "reused_bound_checks"}
    _require_keys(value, required, required, "citation audit summary")
    if (value["audit_input_path"] != audit_input_path or
            value["audit_input_digest"] != audit_input_digest):
        raise EvidenceError("citation audit summary is bound to the wrong audit input")
    claims = value["citation_claims"]
    if not isinstance(claims, list):
        raise EvidenceError("citation_claims must be an array")
    seen_occurrences: set[str] = set()
    expected_by_id = {entry["occurrence_id"]: entry
                      for entry in expected_occurrences}
    prior_signatures = {
        object_digest({key: claim.get(key) for key in
                       ("claim_text", "cite_keys", "status", "sources")})
        for claim in prior_claims if isinstance(claim, dict)
    }
    fresh = 0
    reused = 0
    for index, claim in enumerate(claims):
        where = f"citation_claims[{index}]"
        if not isinstance(claim, dict):
            raise EvidenceError(f"{where} must be an object")
        claim_keys = {"occurrence_id", "anchor", "claim_text", "cite_keys", "status",
                      "sources", "verification"}
        _require_keys(claim, claim_keys, claim_keys, where)
        for key in ("occurrence_id", "anchor", "claim_text"):
            if not isinstance(claim[key], str) or not claim[key]:
                raise EvidenceError(f"{where}.{key} must be a non-empty string")
        cite_keys = _string_list(claim["cite_keys"], f"{where}.cite_keys", nonempty=True)
        occurrence = claim["occurrence_id"]
        if occurrence not in expected_by_id:
            raise EvidenceError(f"{where}.occurrence_id is not in the audited paper")
        if claim["anchor"] != occurrence:
            raise EvidenceError(f"{where}.anchor must equal its mechanical occurrence_id")
        expected = expected_by_id[occurrence]
        if cite_keys != expected["cite_keys"]:
            raise EvidenceError(f"{where}.cite_keys do not match the LaTeX citation occurrence")
        if claim["claim_text"] != expected["claim_text"]:
            raise EvidenceError(f"{where}.claim_text does not match the audited paper paragraph")
        if claim["status"] not in {"FAITHFUL", "TOPICAL"}:
            raise EvidenceError(f"{where}.status cannot appear in a PASS audit")
        sources = claim["sources"]
        if not isinstance(sources, list) or len(sources) != len(cite_keys):
            raise EvidenceError(f"{where}.sources must contain exactly one entry per cite key")
        source_keys: list[str] = []
        for source_index, source in enumerate(sources):
            source_where = f"{where}.sources[{source_index}]"
            if not isinstance(source, dict):
                raise EvidenceError(f"{source_where} must be an object")
            _require_keys(source, {"cite_key", "pointer"}, {"cite_key", "pointer"},
                          source_where)
            if (not isinstance(source["cite_key"], str) or not source["cite_key"] or
                    not isinstance(source["pointer"], str) or not source["pointer"]):
                raise EvidenceError(
                    f"{source_where}.cite_key and .pointer must be non-empty strings"
                )
            if not re.fullmatch(
                    r"(?:https?://\S+|doi:10\.\S+|openalex:W\d+)", source["pointer"],
                    flags=re.IGNORECASE):
                raise EvidenceError(
                    f"{source_where}.pointer must be an exact URL, DOI, or OpenAlex work id"
                )
            source_keys.append(source["cite_key"])
        if sorted(source_keys) != sorted(cite_keys) or len(source_keys) != len(set(source_keys)):
            raise EvidenceError(f"{where}.sources must map each cite key exactly once")
        if occurrence in seen_occurrences:
            raise EvidenceError(f"duplicate citation use in {where}")
        seen_occurrences.add(occurrence)
        if claim["verification"] == "fresh":
            fresh += 1
        elif claim["verification"] == "reused":
            signature = object_digest({key: claim.get(key) for key in
                                       ("claim_text", "cite_keys", "status", "sources")})
            if signature not in prior_signatures:
                raise EvidenceError(
                    f"{where} claims reuse but has no byte-bound prior characterization"
                )
            reused += 1
        else:
            raise EvidenceError(f"{where}.verification must be fresh or reused")
    for key in ("fresh_checks", "reused_bound_checks"):
        if isinstance(value[key], bool) or not isinstance(value[key], int) or value[key] < 0:
            raise EvidenceError(f"{key} must be a non-negative integer")
    if value["fresh_checks"] + value["reused_bound_checks"] != len(claims):
        raise EvidenceError(
            "fresh_checks + reused_bound_checks must equal citation_claims length"
        )
    if value["fresh_checks"] != fresh or value["reused_bound_checks"] != reused:
        raise EvidenceError("citation check counts do not match per-claim verification labels")
    if seen_occurrences != set(expected_by_id):
        missing = sorted(set(expected_by_id) - seen_occurrences)
        raise EvidenceError("citation audit omitted occurrences: " + ", ".join(missing))


def validate_evidence_summary(value: Any, checkpoint: str, audit_input_path: str,
                              audit_input_digest: str,
                              expected_exhibits: list[str]) -> list[str]:
    validate_audit_summary(value, checkpoint)
    assert isinstance(value, dict)
    required = {"verdict", "checkpoint", "blocking_findings", "audit_input_path",
                "audit_input_digest", "mechanical_command", "result_receipts_checked",
                "result_bearing_exhibits_checked", "expository_exemptions",
                "exceptional_direct_results"}
    _require_keys(value, required, required, "evidence audit summary")
    if (value["audit_input_path"] != audit_input_path or
            value["audit_input_digest"] != audit_input_digest):
        raise EvidenceError("evidence audit summary is bound to the wrong audit input")
    expected_command = (
        "python3 code/utils/results_pipeline/results_pipeline.py verify-all --rerender"
    )
    if value["mechanical_command"] != expected_command:
        raise EvidenceError("evidence audit summary has the wrong mechanical_command")
    receipts = _string_list(value["result_receipts_checked"],
                            "result_receipts_checked")
    checked_exhibits = _string_list(value["result_bearing_exhibits_checked"],
                                    "result_bearing_exhibits_checked")
    if checked_exhibits != expected_exhibits:
        raise EvidenceError("result-bearing exhibit inventory does not match paper dependencies")
    for key in ("expository_exemptions", "exceptional_direct_results"):
        _string_list(value[key], key)
    return receipts


def command_bind_paper(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    if args.receipt != PAPER_RECEIPT_PATH:
        raise EvidenceError(f"paper receipt path must be exactly {PAPER_RECEIPT_PATH}")
    audit_input_raw, audit_input_path = evidence_artifact_path(
        root, args.audit_input, must_exist=True
    )
    summary_raw, summary_path = evidence_artifact_path(root, args.summary, must_exist=True)
    report_raw, report_path = evidence_artifact_path(root, args.report, must_exist=True)
    citation_summary_raw, citation_summary_path = evidence_artifact_path(
        root, args.citation_summary, must_exist=True
    )
    citation_report_raw, citation_report_path = evidence_artifact_path(
        root, args.citation_report, must_exist=True
    )
    result_paths = discover_result_receipts(root)
    result_reports = [verify_receipt(root, path, rerender=True) for path in result_paths]
    failures = [f"{item['receipt']}: {failure}" for item in result_reports
                for failure in item["failures"]]
    if failures:
        raise EvidenceError("result provenance is stale: " + "; ".join(failures))
    # Nothing below this line executes paper/result producer code. Validate and
    # fingerprint the exact post-rerender bytes that will be bound.
    audit_input = validate_audit_input(root, audit_input_path, args.checkpoint)
    checked_receipts = validate_evidence_summary(
        load_json(summary_path), args.checkpoint, audit_input_raw, audit_input["digest"],
        audit_input["included_result_exhibits"]
    )
    validate_audit_report(report_path, args.checkpoint, audit_input["digest"], "evidence")
    _, target = receipt_path(root, PAPER_RECEIPT_PATH)
    prior_claims: list[dict[str, Any]] = []
    if target.exists():
        prior_receipt = load_json(target)
        prior_summary = None
        if (isinstance(prior_receipt, dict) and
                prior_receipt.get("kind") == "paper_evidence" and
                not isinstance(prior_receipt.get("receipt_version"), bool) and
                prior_receipt.get("receipt_version") == PAPER_RECEIPT_VERSION):
            prior_summary = prior_receipt.get("citation_audit_summary")
        if isinstance(prior_summary, dict) and not compare_snapshot(
                root, [prior_summary], "prior citation audit summary"):
            prior_value = load_json(root / prior_summary["path"])
            if isinstance(prior_value, dict) and isinstance(prior_value.get("citation_claims"), list):
                prior_claims = prior_value["citation_claims"]
    validate_citation_summary(
        load_json(citation_summary_path), args.checkpoint,
        audit_input_raw, audit_input["digest"], audit_input["citation_occurrences"],
        prior_claims
    )
    validate_audit_report(citation_report_path, args.checkpoint, audit_input["digest"],
                          "citation")
    discovered_receipts = [path.relative_to(root).as_posix() for path in result_paths]
    if sorted(checked_receipts) != sorted(discovered_receipts):
        raise EvidenceError(
            "evidence audit receipt inventory does not match discovered result receipts"
        )
    receipt = {
        "kind": "paper_evidence",
        "receipt_version": PAPER_RECEIPT_VERSION,
        "checkpoint": args.checkpoint,
        "audit_input": fingerprint(root, audit_input_raw),
        "audit_summary": fingerprint(root, summary_raw),
        "audit_report": fingerprint(root, report_raw),
        "citation_audit_summary": fingerprint(root, citation_summary_raw),
        "citation_audit_report": fingerprint(root, citation_report_raw),
        "results_registry": audit_input["results_registry"],
        "paper_sources": audit_input["paper_sources"],
        "result_receipts": audit_input["result_receipts"],
    }
    final_failures: list[str] = []
    singleton_fields = {"audit_input", "audit_summary", "audit_report",
                        "citation_audit_summary", "citation_audit_report",
                        "results_registry"}
    for key, value in receipt.items():
        if key in {"kind", "receipt_version", "checkpoint"}:
            continue
        entries = [value] if key in singleton_fields else value
        final_failures.extend(compare_snapshot(root, entries, f"pre-bind {key}"))
    if final_failures:
        raise EvidenceError("bytes changed during paper binding: " + "; ".join(final_failures))
    atomic_json(target, receipt)
    print(json.dumps({"status": "BOUND", "receipt": args.receipt,
                      "checkpoint": args.checkpoint}, sort_keys=True))
    return 0


def verify_paper_receipt(root: Path, path: Path, *, rerender: bool) -> dict[str, Any]:
    receipt = load_json(path)
    if (not isinstance(receipt, dict) or receipt.get("kind") != "paper_evidence" or
            isinstance(receipt.get("receipt_version"), bool) or
            receipt.get("receipt_version") != PAPER_RECEIPT_VERSION):
        raise EvidenceError(f"not a paper-evidence receipt v{PAPER_RECEIPT_VERSION}: {path}")
    failures: list[str] = []
    audit_fields = {"audit_input", "audit_summary", "audit_report",
                    "citation_audit_summary", "citation_audit_report",
                    "results_registry"}
    for key in ("audit_input", "audit_summary", "audit_report", "citation_audit_summary",
                "citation_audit_report", "results_registry", "paper_sources",
                "result_receipts"):
        value = receipt.get(key)
        entries = [value] if key in audit_fields and isinstance(value, dict) else value
        if not isinstance(entries, list):
            failures.append(f"{key}: malformed receipt field")
        else:
            failures.extend(compare_snapshot(root, entries, key))
    if not failures:
        try:
            audit_input_path = root / receipt["audit_input"]["path"]
            validate_audit_input(root, audit_input_path, receipt.get("checkpoint"))
        except (EvidenceError, KeyError, TypeError) as exc:
            failures.append(f"audit_input: {exc}")
    if not failures and rerender:
        for result_entry in receipt["result_receipts"]:
            raw = result_entry["path"]
            _, result_path = project_path(root, raw)
            report = verify_receipt(root, result_path, rerender=True)
            failures.extend(f"{raw}: {failure}" for failure in report["failures"])
        if not failures:
            for key in ("audit_input", "audit_summary", "audit_report",
                        "citation_audit_summary", "citation_audit_report",
                        "results_registry", "paper_sources", "result_receipts"):
                value = receipt[key]
                entries = [value] if key in audit_fields else value
                failures.extend(compare_snapshot(root, entries, f"post-render {key}"))
        if not failures:
            try:
                validate_audit_input(root, root / receipt["audit_input"]["path"],
                                     receipt.get("checkpoint"))
            except (EvidenceError, KeyError, TypeError) as exc:
                failures.append(f"post-render audit_input: {exc}")
    return {"receipt": str(path.relative_to(root)),
            "checkpoint": receipt.get("checkpoint"),
            "status": "PASS" if not failures else "STALE", "failures": failures}


def command_verify_paper(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    if args.receipt != PAPER_RECEIPT_PATH:
        raise EvidenceError(f"paper receipt path must be exactly {PAPER_RECEIPT_PATH}")
    _, path = project_path(root, PAPER_RECEIPT_PATH)
    result = verify_paper_receipt(root, path, rerender=args.rerender)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    init_registry = subparsers.add_parser(
        "init-registry", help="initialize the durable registry for a manual project"
    )
    init_registry.add_argument("--project-root", default=".")
    init_registry.set_defaults(func=command_init_registry)

    run = subparsers.add_parser("run", help="execute analysis and record its result bundle")
    run.add_argument("--project-root", default=".")
    run.add_argument("--plan", required=True)
    run.add_argument("--bundle", required=True)
    run.add_argument("--receipt", required=True)
    run.add_argument("--supersedes", action="append", default=[])
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=command_run)

    render = subparsers.add_parser("render", help="execute a bundle-only renderer and record exhibits")
    render.add_argument("--project-root", default=".")
    render.add_argument("--receipt", required=True)
    render.add_argument("command", nargs=argparse.REMAINDER)
    render.set_defaults(func=command_render)

    activate = subparsers.add_parser(
        "activate", help="activate one scientifically accepted pending result receipt"
    )
    activate.add_argument("--project-root", default=".")
    activate.add_argument("--receipt", required=True)
    activate.set_defaults(func=command_activate)

    retire = subparsers.add_parser(
        "retire", help="explicitly retire an active result receipt without deleting it"
    )
    retire.add_argument("--project-root", default=".")
    retire.add_argument("--receipt", required=True)
    retire.add_argument("--reason", required=True)
    retire.add_argument("--superseded-by")
    retire.set_defaults(func=command_retire)

    verify = subparsers.add_parser("verify", help="verify one receipt and optionally regenerate exhibits")
    verify.add_argument("--project-root", default=".")
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--rerender", action="store_true")
    verify.set_defaults(func=command_verify)

    verify_all = subparsers.add_parser("verify-all", help="verify all result receipts under output/")
    verify_all.add_argument("--project-root", default=".")
    verify_all.add_argument("--rerender", action="store_true")
    verify_all.add_argument("--require-one", action="store_true")
    verify_all.set_defaults(func=command_verify_all)

    prepare_audit = subparsers.add_parser(
        "prepare-audit", help="freeze the exact paper/result bytes supplied to both auditors"
    )
    prepare_audit.add_argument("--project-root", default=".")
    prepare_audit.add_argument("--output", required=True)
    prepare_audit.add_argument("--checkpoint", required=True)
    prepare_audit.set_defaults(func=command_prepare_audit)

    verify_audit_input = subparsers.add_parser(
        "verify-audit-input", help="verify an audit input still matches current bytes"
    )
    verify_audit_input.add_argument("--project-root", default=".")
    verify_audit_input.add_argument("--input", required=True)
    verify_audit_input.add_argument("--checkpoint", required=True)
    verify_audit_input.set_defaults(func=command_verify_audit_input)

    bind_paper = subparsers.add_parser(
        "bind-paper", help="bind a PASS semantic audit to exact paper and result bytes"
    )
    bind_paper.add_argument("--project-root", default=".")
    bind_paper.add_argument("--audit-input", required=True)
    bind_paper.add_argument("--summary", required=True)
    bind_paper.add_argument("--report", required=True)
    bind_paper.add_argument("--citation-summary", required=True)
    bind_paper.add_argument("--citation-report", required=True)
    bind_paper.add_argument("--receipt", required=True)
    bind_paper.add_argument("--checkpoint", required=True)
    bind_paper.set_defaults(func=command_bind_paper)

    verify_paper = subparsers.add_parser(
        "verify-paper", help="verify a bound semantic paper-evidence receipt"
    )
    verify_paper.add_argument("--project-root", default=".")
    verify_paper.add_argument("--receipt", required=True)
    verify_paper.add_argument("--rerender", action="store_true")
    verify_paper.set_defaults(func=command_verify_paper)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = resolve_root(args.project_root)
        if args.subcommand == "init-registry":
            _, process_log = project_path(root, "process_log", must_exist=False)
            if not process_log.exists():
                process_log.mkdir(mode=0o700)
        with project_lock(root):
            recover_transaction(root)
            return args.func(args)
    except EvidenceError as exc:
        print(f"results_pipeline: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
