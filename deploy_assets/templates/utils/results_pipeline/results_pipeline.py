#!/usr/bin/env python3
"""Finalize and verify paper-facing result bundles and rendered exhibits.

The utility deliberately does not prescribe table layouts or plotting libraries.
It records the actual analysis/render commands, fingerprints declared inputs and
outputs, and fails closed when any recorded byte becomes stale.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import secrets
import select
import signal
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable
from urllib.parse import unquote, urlsplit


RECEIPT_VERSION = 2
EMPIRICAL_RECEIPT_VERSION = 3
ENVIRONMENT_CAPTURE_VERSION = 1
RUN_PLAN_VERSION = 1
PAPER_RECEIPT_VERSION = 4
REGISTRY_VERSION = 1
AUDIT_INPUT_VERSION = 1
EMPIRICAL_AUDIT_INPUT_VERSION = 2
REGISTRY_PATH = "process_log/results_registry.json"
PAPER_RECEIPT_PATH = "process_log/paper_evidence.receipt.json"
LOCK_PATH = "process_log/results_pipeline.lock"
TRANSACTION_PATH = "process_log/results_pipeline.transaction.json"
TRANSACTION_BACKUP_PATH = "process_log/.results_pipeline-transaction-backup"
AUDIT_NAMESPACE = "output/evidence"
RESULT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
CITATION_COMMANDS = {
    "cite", "cites", "parencite", "parencites", "textcite", "textcites",
    "footcite", "footcites", "footcitetext", "smartcite", "smartcites",
    "supercite", "autocite", "autocites", "fullcite", "footfullcite",
    "citeauthor", "citetitle", "citeyear", "citedate", "citeurl", "citefield",
    "volcite", "volcites", "pvolcite", "pvolcites", "fvolcite", "fvolcites",
    "ftvolcite", "ftvolcites", "svolcite", "svolcites", "tvolcite", "tvolcites",
    "avolcite", "avolcites", "citep", "citet", "citealp", "citealt",
    "citeyearpar", "citenum", "citename", "citelist", "notecite",
    "pnotecite", "fnotecite", "supercites", "footcitetexts",
    "citetalias", "citepalias", "bibentry",
}
CITATION_COMMAND_PATTERN = "|".join(
    sorted((re.escape(item) for item in CITATION_COMMANDS), key=len, reverse=True)
)
CITATION_COMMAND_TOKEN_RE = re.compile(
    r"\\(?P<command>" + CITATION_COMMAND_PATTERN + r")\*?(?![A-Za-z])",
    flags=re.IGNORECASE,
)
CITATION_FAMILY_RE = re.compile(
    r"\\(?P<command>[A-Za-z@]*cite[A-Za-z@]*)\*?", flags=re.IGNORECASE
)
CQUOTE_COMMAND_TOKEN_RE = re.compile(
    r"\\(?P<command>(?:(?:foreign)?(?:text|block)|"
    r"hyphen(?:text|block)|hybridblock)cquote)\*?(?![A-Za-z])",
    flags=re.IGNORECASE,
)
CQUOTE_FAMILY_RE = re.compile(
    r"\\(?P<command>[A-Za-z@]*cquote[A-Za-z@]*)\*?", flags=re.IGNORECASE
)
CITE_KEY_RE = re.compile(r"^[A-Za-z0-9_:.+/-]+$")
NON_OCCURRENCE_CITATION_COMMANDS = {
    "nocite", "citestyle", "setcitestyle", "defcitealias", "citetext",
}
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
CAPTURED_RUNTIME_ENV_KEYS = {
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "TZ",
    "PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "CUDA_VISIBLE_DEVICES",
}
DEPENDENCY_MANIFEST_PATHS = (
    ".python-version", ".tool-versions", "pyproject.toml", "uv.lock",
    "requirements.txt", "renv.lock", "Project.toml", "Manifest.toml",
    ".arpipeline/update_inputs/deps/core.txt",
    ".arpipeline/update_inputs/deps/ssj.txt",
    ".arpipeline/update_inputs/deps/extensions/empirical.txt",
    ".arpipeline/update_inputs/deps/extensions/theory_llm.txt",
)
MAX_ENVIRONMENT_CAPTURE_FILE_BYTES = 64 * 1024 * 1024
MAX_ENVIRONMENT_CAPTURE_TOTAL_BYTES = 64 * 1024 * 1024
MAX_ENVIRONMENT_CAPTURE_FILES = 20_000
MAX_ENVIRONMENT_CAPTURE_ENTRIES = 20_000
MAX_ENVIRONMENT_CAPTURE_TEXT_BYTES = 16_384
MAX_VENV_LIBRARY_ENTRIES = 512
MAX_VENV_SITE_PACKAGES_ENTRIES = 16_384


class EvidenceError(RuntimeError):
    pass


class _EnvironmentCaptureBudget:
    """Bound trusted-parent environment inspection work per snapshot."""

    def __init__(self) -> None:
        self.bytes = 0
        self.files = 0
        self.entries = 0
        self.forbidden_inodes: set[tuple[int, int]] = set()

    def reserve(self, size: int, display_path: str) -> None:
        if size > MAX_ENVIRONMENT_CAPTURE_FILE_BYTES:
            raise EvidenceError(
                f"runtime file exceeds the environment capture per-file limit: {display_path}"
            )
        if self.files + 1 > MAX_ENVIRONMENT_CAPTURE_FILES:
            raise EvidenceError("environment capture file-count limit exceeded")
        if self.bytes + size > MAX_ENVIRONMENT_CAPTURE_TOTAL_BYTES:
            raise EvidenceError("environment capture aggregate byte limit exceeded")
        self.files += 1
        self.bytes += size

    def observe_entry(self, where: str) -> None:
        if self.entries + 1 > MAX_ENVIRONMENT_CAPTURE_ENTRIES:
            raise EvidenceError(
                f"environment capture directory-entry limit exceeded: {where}"
            )
        self.entries += 1


_LOCK_DESCRIPTOR: int | None = None
_SOURCE_LEASE_BROKEN = False


def _mark_source_lease_broken(_signal_number: int, _frame: Any) -> None:
    """Record a host-side attempt to open a bound source for writing."""
    global _SOURCE_LEASE_BROKEN
    _SOURCE_LEASE_BROKEN = True


@contextmanager
def project_lock(root: Path) -> Iterable[None]:
    """Serialize every utility command for one project."""
    global _LOCK_DESCRIPTOR
    _, process_log = project_path(root, "process_log")
    process_log_descriptor = _open_directory_path(process_log)
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(
            Path(LOCK_PATH).name, flags, 0o600, dir_fd=process_log_descriptor
        )
    except OSError as exc:
        os.close(process_log_descriptor)
        raise EvidenceError(f"cannot open results pipeline lock: {exc}") from exc
    os.close(process_log_descriptor)
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


@contextmanager
def project_read_lock(root: Path) -> Iterable[None]:
    """Hold the shared side of the existing results lock without creating files."""
    _, lock_path = project_path(root, LOCK_PATH)
    descriptor = _open_entry_read(lock_path)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EvidenceError("results pipeline lock must be one regular file")
        fcntl.flock(descriptor, fcntl.LOCK_SH)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _reject_constant(value: str) -> None:
    raise EvidenceError(f"non-finite JSON number is forbidden: {value}")


def _forbidden_part(part: str) -> bool:
    folded = part.casefold()
    return folded == ".git" or folded.startswith(".env")


def _validate_descendant_name(name: str, parent: Path) -> None:
    """Reject names that cannot be represented safely in receipt path fields."""
    try:
        name.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise EvidenceError(
            f"directory entry name is not valid UTF-8 under {parent}"
        ) from exc
    if "\\" in name or any(ord(character) < 32 for character in name):
        raise EvidenceError(
            "control characters and backslashes are forbidden in directory entries: "
            f"{parent / name}"
        )


def _open_directory_path(path: Path) -> int:
    """Open a directory through held no-follow descriptors for every component."""
    absolute = Path(os.path.abspath(path))
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(os.sep, flags)
    try:
        for part in absolute.parts[1:]:
            expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(expected.st_mode):
                raise EvidenceError(f"directory path component is not a directory: {path}")
            child = os.open(part, flags, dir_fd=descriptor)
            opened = os.fstat(child)
            if ((opened.st_dev, opened.st_ino) !=
                    (expected.st_dev, expected.st_ino)):
                os.close(child)
                raise EvidenceError(f"directory changed while opening: {path}")
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException as exc:
        os.close(descriptor)
        if isinstance(exc, EvidenceError):
            raise
        if isinstance(exc, OSError):
            raise EvidenceError(f"cannot open directory without following links {path}: {exc}") from exc
        raise


def _open_or_create_directory_path(path: Path) -> int:
    """Open/create a directory tree through held no-follow descriptors."""
    absolute = Path(os.path.abspath(path))
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    descriptor = os.open(os.sep, flags)
    try:
        for part in absolute.parts[1:]:
            try:
                expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                os.mkdir(part, 0o777, dir_fd=descriptor)
                os.fsync(descriptor)
                expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(expected.st_mode):
                raise EvidenceError(f"directory path component is not a directory: {path}")
            child = os.open(part, flags, dir_fd=descriptor)
            opened = os.fstat(child)
            if ((opened.st_dev, opened.st_ino) !=
                    (expected.st_dev, expected.st_ino)):
                os.close(child)
                raise EvidenceError(f"directory changed while opening: {path}")
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException as exc:
        os.close(descriptor)
        if isinstance(exc, EvidenceError):
            raise
        if isinstance(exc, OSError):
            raise EvidenceError(
                f"cannot create/open directory without following links {path}: {exc}"
            ) from exc
        raise


def _open_entry_read(path: Path) -> int:
    """Open a file or directory while anchoring every ancestor descriptor."""
    parent = _open_directory_path(path.parent)
    descriptor: int | None = None
    try:
        expected = os.stat(path.name, dir_fd=parent, follow_symlinks=False)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        if stat.S_ISDIR(expected.st_mode):
            flags |= getattr(os, "O_DIRECTORY", 0)
        descriptor = os.open(path.name, flags, dir_fd=parent)
        opened = os.fstat(descriptor)
        if ((opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)):
            raise EvidenceError(f"path changed while opening: {path}")
        return descriptor
    except BaseException as exc:
        if descriptor is not None:
            os.close(descriptor)
        if isinstance(exc, EvidenceError):
            raise
        if isinstance(exc, OSError):
            raise EvidenceError(f"cannot open path without following links {path}: {exc}") from exc
        raise
    finally:
        os.close(parent)


def _open_regular_read(path: Path) -> int:
    """Open one non-symlink regular file without blocking on a FIFO."""
    try:
        descriptor = _open_entry_read(path)
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EvidenceError(f"expected one non-aliased regular file: {path}")
        return descriptor
    except BaseException as exc:
        if "descriptor" in locals():
            os.close(descriptor)
        if isinstance(exc, EvidenceError):
            raise EvidenceError(
                f"cannot open one non-aliased regular file {path}: {exc}"
            ) from exc
        if isinstance(exc, OSError):
            raise EvidenceError(
                f"cannot open one non-aliased regular file {path}: {exc}"
            ) from exc
        raise


def read_utf8(path: Path, label: str) -> str:
    try:
        descriptor = _open_regular_read(path)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            return handle.read()
    except EvidenceError:
        raise
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"cannot read {label} from {path}: {exc}") from exc


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise EvidenceError(f"duplicate JSON object key: {key!r}")
        value[key] = item
    return value


def _parse_json_text(value: str, path: Path) -> Any:
    try:
        return json.loads(
            value, parse_constant=_reject_constant,
            object_pairs_hook=_unique_json_object,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"cannot read valid JSON from {path}: {exc}") from exc


def load_json(path: Path) -> Any:
    return _parse_json_text(read_utf8(path, "JSON"), path)


def load_json_snapshot(root: Path, raw: str) -> tuple[Any, dict[str, Any]]:
    """Parse and fingerprint the same bytes from one anchored file descriptor."""
    normalized, path = project_path(root, raw)
    descriptor = _open_regular_read(path)
    try:
        chunks: list[bytes] = []
        digest = hashlib.sha256()
        for chunk in iter(lambda: os.read(descriptor, 1024 * 1024), b""):
            chunks.append(chunk)
            digest.update(chunk)
    finally:
        os.close(descriptor)
    try:
        text = b"".join(chunks).decode("utf-8")
    except UnicodeError as exc:
        raise EvidenceError(f"cannot read valid JSON from {path}: {exc}") from exc
    snapshot = {
        "path": normalized,
        "kind": "file",
        "sha256": f"sha256:{digest.hexdigest()}",
    }
    return _parse_json_text(text, path), snapshot


def fsync_directory(path: Path) -> None:
    """Make one directory-entry update durable, with controlled failures."""
    descriptor: int | None = None
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        os.fsync(descriptor)
    except OSError as exc:
        raise EvidenceError(f"cannot durably synchronize directory {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def ensure_directory_durable(path: Path) -> None:
    """Create a directory tree and durably publish every new ancestor."""
    missing: list[Path] = []
    current = path
    while not current.exists():
        missing.append(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise EvidenceError(f"cannot create directory {path}: {exc}") from exc
    if not path.is_dir() or path.is_symlink():
        raise EvidenceError(f"expected a real directory: {path}")
    for created in reversed(missing):
        fsync_directory(created)
        fsync_directory(created.parent)


def atomic_json(path: Path, value: Any) -> None:
    try:
        payload = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                             allow_nan=False) + "\n"
    except (TypeError, ValueError) as exc:
        raise EvidenceError(f"cannot serialize receipt {path}: {exc}") from exc
    parent_descriptor: int | None = None
    temporary: str | None = None
    try:
        _validate_descendant_name(path.name, path.parent)
        if path.name in {"", ".", ".."}:
            raise EvidenceError(f"invalid JSON publication name: {path.name!r}")
        parent_descriptor = _open_or_create_directory_path(path.parent)
        temporary = f".{path.name}.{secrets.token_hex(16)}"
        fd = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_descriptor,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        current_parent = _open_directory_path(path.parent)
        try:
            anchored = os.fstat(parent_descriptor)
            current = os.fstat(current_parent)
            if ((anchored.st_dev, anchored.st_ino) !=
                    (current.st_dev, current.st_ino)):
                raise EvidenceError(f"publication directory changed: {path.parent}")
        finally:
            os.close(current_parent)
        os.replace(
            temporary, path.name,
            src_dir_fd=parent_descriptor, dst_dir_fd=parent_descriptor,
        )
        os.fsync(parent_descriptor)
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"cannot publish receipt {path}: {exc}") from exc
    finally:
        if temporary is not None and parent_descriptor is not None:
            try:
                os.unlink(temporary, dir_fd=parent_descriptor)
            except FileNotFoundError:
                pass
        if parent_descriptor is not None:
            os.close(parent_descriptor)


def project_path(root: Path, raw: str, *, must_exist: bool = True) -> tuple[str, Path]:
    if not isinstance(raw, str) or not raw:
        raise EvidenceError("paths must be non-empty strings")
    if any(ord(character) < 32 for character in raw):
        raise EvidenceError(f"control characters are forbidden in project paths: {raw!r}")
    posix = PurePosixPath(raw.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise EvidenceError(f"path must be project-relative without traversal: {raw!r}")
    if any(_forbidden_part(part) for part in posix.parts):
        raise EvidenceError(f"credential-bearing path may not enter a result receipt: {raw!r}")
    normalized = posix.as_posix()
    if normalized == ".":
        raise EvidenceError(f"path must name a project entry, not the project root: {raw!r}")
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
    folded = raw.casefold()
    namespace = AUDIT_NAMESPACE.casefold()
    if folded == namespace or folded.startswith(namespace + "/"):
        raise EvidenceError(
            f"{where} may not use reserved audit namespace {AUDIT_NAMESPACE}/"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        descriptor = _open_regular_read(path)
        with os.fdopen(descriptor, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise EvidenceError(f"cannot fingerprint regular file {path}: {exc}") from exc
    return f"sha256:{digest.hexdigest()}"


def walk_directory(path: Path, *, hash_files: bool = False, root_fd: int | None = None
                   ) -> list[tuple[str, Path, os.stat_result, str | None]]:
    """Enumerate through held no-follow descriptors with depth-bounded FD use."""
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    root_fd = os.dup(root_fd) if root_fd is not None else _open_directory_path(path)
    found: list[tuple[str, Path, os.stat_result, str | None]] = []
    try:
        root_names = sorted(os.listdir(root_fd))
    except OSError as exc:
        os.close(root_fd)
        raise EvidenceError(f"cannot inspect declared directory {path}: {exc}") from exc
    stack: list[tuple[int, PurePosixPath, list[str], int]] = [
        (root_fd, PurePosixPath(), root_names, 0)
    ]
    try:
        while stack:
            directory_fd, prefix, names, index = stack[-1]
            if index >= len(names):
                os.close(directory_fd)
                stack.pop()
                continue
            name = names[index]
            stack[-1] = (directory_fd, prefix, names, index + 1)
            _validate_descendant_name(name, path / prefix)
            relative = prefix / name
            child = path.joinpath(*relative.parts)
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as exc:
                raise EvidenceError(f"cannot inspect directory entry {child}: {exc}") from exc
            digest: str | None = None
            if stat.S_ISDIR(info.st_mode):
                try:
                    child_fd = os.open(name, flags, dir_fd=directory_fd)
                except OSError as exc:
                    raise EvidenceError(f"cannot open declared directory {child}: {exc}") from exc
                try:
                    opened = os.fstat(child_fd)
                    if ((opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)):
                        raise EvidenceError(f"directory changed while inspecting {child}")
                    found.append((relative.as_posix(), child, info, None))
                    try:
                        child_names = sorted(os.listdir(child_fd))
                    except OSError as exc:
                        os.close(child_fd)
                        raise EvidenceError(
                            f"cannot inspect declared directory {child}: {exc}"
                        ) from exc
                    stack.append((child_fd, relative, child_names, 0))
                except BaseException:
                    if not any(frame[0] == child_fd for frame in stack):
                        try:
                            os.close(child_fd)
                        except OSError:
                            pass
                    raise
                continue
            if hash_files and stat.S_ISREG(info.st_mode):
                file_flags = (os.O_RDONLY | os.O_NONBLOCK |
                              getattr(os, "O_NOFOLLOW", 0))
                try:
                    file_fd = os.open(name, file_flags, dir_fd=directory_fd)
                except OSError as exc:
                    raise EvidenceError(f"cannot fingerprint {child}: {exc}") from exc
                try:
                    opened = os.fstat(file_fd)
                    if ((opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)
                            or opened.st_nlink != 1):
                        raise EvidenceError(
                            "file changed or is not one non-aliased regular file "
                            f"while fingerprinting {child}"
                        )
                    file_digest = hashlib.sha256()
                    for chunk in iter(lambda: os.read(file_fd, 1024 * 1024), b""):
                        file_digest.update(chunk)
                    digest = f"sha256:{file_digest.hexdigest()}"
                finally:
                    os.close(file_fd)
            found.append((relative.as_posix(), child, info, digest))
    except BaseException:
        for descriptor, *_ in stack:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    return sorted(found, key=lambda entry: entry[0])


def fingerprint(root: Path, raw: str) -> dict[str, Any]:
    normalized, path = project_path(root, raw)
    descriptor = _open_entry_read(path)
    try:
        info = os.fstat(descriptor)
        if stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1:
                raise EvidenceError(
                    f"expected one non-aliased regular file while fingerprinting: {normalized}"
                )
            digest = hashlib.sha256()
            for chunk in iter(lambda: os.read(descriptor, 1024 * 1024), b""):
                digest.update(chunk)
            return {"path": normalized, "kind": "file",
                    "sha256": f"sha256:{digest.hexdigest()}"}
        if not stat.S_ISDIR(info.st_mode):
            raise EvidenceError(f"only regular files/directories may be fingerprinted: {normalized}")
        entries: list[dict[str, Any]] = []
        for relative, child, child_info, child_digest in walk_directory(
                path, hash_files=True, root_fd=descriptor):
            if any(_forbidden_part(part) for part in PurePosixPath(relative).parts):
                raise EvidenceError(
                    f"credential-bearing descendant may not enter result provenance: "
                    f"{normalized}/{relative}"
                )
            if stat.S_ISLNK(child_info.st_mode):
                raise EvidenceError(
                    f"symlink inside declared directory is forbidden: {normalized}/{relative}"
                )
            child_mode = child_info.st_mode
            if stat.S_ISDIR(child_mode):
                entries.append({"path": relative, "kind": "directory"})
                continue
            if not stat.S_ISREG(child_mode):
                raise EvidenceError(
                    f"special file inside declared directory: {normalized}/{relative}"
                )
            assert child_digest is not None
            entries.append({"path": relative, "kind": "file", "sha256": child_digest})
    finally:
        os.close(descriptor)
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


def _analysis_contract_module() -> Any:
    """Load the sibling helper even when this script runs under python -I -S."""
    path = Path(__file__).with_name("analysis_contract.py")
    spec = importlib.util.spec_from_file_location("_iar_analysis_contract", path)
    if spec is None or spec.loader is None:
        raise EvidenceError(f"cannot load empirical contract validator: {path}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, RuntimeError) as exc:
        raise EvidenceError(f"cannot load empirical contract validator: {exc}") from exc
    return module


def validate_empirical_plan(root: Path, plan: dict[str, Any], *, completed: bool
                            ) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    """Validate contract/input closure and, after execution, realization summaries."""
    analyses = plan.get("analyses")
    if not isinstance(analyses, dict) or not analyses:
        raise EvidenceError("empirical run plan.analyses must be a non-empty object")
    helper = _analysis_contract_module()
    validated: dict[str, dict[str, Any]] = {}
    projections: list[dict[str, Any]] = []
    covered_inputs: set[str] = set()
    baseline_digests: set[str] = set()
    summary_paths: set[str] = set()
    for analysis_id, declaration in analyses.items():
        if not isinstance(analysis_id, str) or RESULT_ID_RE.fullmatch(analysis_id) is None:
            raise EvidenceError(f"invalid empirical analysis id: {analysis_id!r}")
        where = f"run plan.analyses.{analysis_id}"
        if not isinstance(declaration, dict):
            raise EvidenceError(f"{where} must be an object")
        _require_keys(
            declaration, {"contract", "execution_summary", "input_bindings"},
            {"contract", "execution_summary", "input_bindings"}, where,
        )
        contract_raw, contract_path = project_path(root, declaration["contract"])
        summary_raw, summary_path = project_path(
            root, declaration["execution_summary"], must_exist=completed
        )
        if contract_raw not in plan["producer_inputs"]:
            raise EvidenceError(f"{where}.contract must be a producer input")
        if summary_raw not in plan["artifacts"]:
            raise EvidenceError(f"{where}.execution_summary must be a declared artifact")
        if summary_raw in plan["renderer_inputs"]:
            raise EvidenceError(f"{where}.execution_summary must be audit-only")
        if summary_raw in summary_paths:
            raise EvidenceError("each empirical analysis needs its own execution summary")
        summary_paths.add(summary_raw)
        try:
            contract_value = load_json(contract_path)
            baseline_ref = contract_value.get("baseline") if isinstance(contract_value, dict) else None
            baseline_raw_value = baseline_ref.get("path") if isinstance(baseline_ref, dict) else None
            baseline_raw, baseline_path = project_path(root, baseline_raw_value)
            if baseline_raw not in plan["producer_inputs"]:
                raise EvidenceError(f"{where} baseline must be a producer input")
            baseline = load_json(baseline_path)
            contract = helper.validate_contract(contract_value, baseline)
        except (helper.ContractError, TypeError) as exc:
            raise EvidenceError(f"{where}: {exc}") from exc
        if contract["analysis_id"] != analysis_id:
            raise EvidenceError(f"{where}.contract analysis_id differs from its plan key")
        if contract["baseline"]["path"] != baseline_raw:
            raise EvidenceError(f"{where}.contract baseline path is not normalized")
        baseline_digests.add(contract["baseline"]["semantic_digest"])
        covered_inputs.update({contract_raw, baseline_raw})
        bindings = declaration["input_bindings"]
        if not isinstance(bindings, dict) or set(bindings) != set(contract["effective"]["inputs"]):
            raise EvidenceError(f"{where}.input_bindings must cover every contract input ID")
        normalized_bindings: dict[str, list[str]] = {}
        for input_id, paths in bindings.items():
            values = _string_list(paths, f"{where}.input_bindings.{input_id}", nonempty=True)
            normalized = [project_path(root, raw)[0] for raw in values]
            if len(normalized) != len(set(normalized)):
                raise EvidenceError(f"{where}.input_bindings.{input_id} has normalized duplicates")
            missing = sorted(set(normalized) - set(plan["producer_inputs"]))
            if missing:
                raise EvidenceError(f"{where}.input_bindings names undeclared inputs: {', '.join(missing)}")
            normalized_bindings[input_id] = normalized
            covered_inputs.update(normalized)
        declaration["contract"] = contract_raw
        declaration["execution_summary"] = summary_raw
        declaration["input_bindings"] = normalized_bindings
        validated[analysis_id] = contract
        if completed:
            try:
                execution = helper.validate_execution(load_json(summary_path), contract)
            except helper.ContractError as exc:
                raise EvidenceError(f"{where}.execution_summary: {exc}") from exc
            projection = helper.lineage_projection(contract, execution, [])
            projection.update({
                "baseline_path": baseline_raw,
                "contract_path": contract_raw,
                "execution_summary_path": summary_raw,
            })
            projections.append(projection)
    if len(baseline_digests) != 1:
        raise EvidenceError("all analyses in one empirical run must use one baseline")
    uncovered = sorted(set(plan["producer_inputs"]) - covered_inputs)
    if uncovered:
        raise EvidenceError(
            "empirical producer inputs lack analysis/input ownership: " + ", ".join(uncovered)
        )
    if completed:
        for raw in plan["renderer_inputs"]:
            _, path = project_path(root, raw)
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(
                    "empirical renderer_inputs must name individual regular files: " + raw
                )
    return validated, projections


def validate_empirical_execution(root: Path, plan: dict[str, Any],
                                 contracts: dict[str, dict[str, Any]]
                                 ) -> list[dict[str, Any]]:
    """Validate fresh producer-owned summaries without reopening pinned inputs."""
    helper = _analysis_contract_module()
    projections: list[dict[str, Any]] = []
    for analysis_id, contract in contracts.items():
        summary_raw = plan["analyses"][analysis_id]["execution_summary"]
        _, summary_path = project_path(root, summary_raw)
        try:
            execution = helper.validate_execution(load_json(summary_path), contract)
        except helper.ContractError as exc:
            raise EvidenceError(
                f"run plan.analyses.{analysis_id}.execution_summary: {exc}"
            ) from exc
        projection = helper.lineage_projection(contract, execution, [])
        projection.update({
            "baseline_path": contract["baseline"]["path"],
            "contract_path": plan["analyses"][analysis_id]["contract"],
            "execution_summary_path": summary_raw,
        })
        projections.append(projection)
    return projections


def validate_empirical_bundle(bundle: dict[str, Any], contracts: dict[str, dict[str, Any]],
                              projections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ownership: dict[str, set[str]] = {analysis_id: set() for analysis_id in contracts}
    for result_id, result in bundle["results"].items():
        analysis_id = result.get("analysis_id")
        if analysis_id not in contracts:
            raise EvidenceError(f"results.{result_id}.analysis_id is missing or unknown")
        ownership[analysis_id].add(result_id)
    for analysis_id, contract in contracts.items():
        expected = set(contract["effective"]["outputs"])
        if ownership[analysis_id] != expected:
            raise EvidenceError(
                f"results owned by {analysis_id} differ from its contract outputs"
            )
        for result_id, output in contract["effective"]["outputs"].items():
            result = bundle["results"][result_id]
            expected_projection = {
                "description": output["description"],
                "unit": output["unit"],
                "display": output["presentation"],
            }
            actual_projection = {
                "description": result["description"],
                "unit": result.get("unit"),
                "display": result.get("display"),
            }
            if object_digest(actual_projection) != object_digest(expected_projection):
                raise EvidenceError(
                    f"results.{result_id} presentation differs from its contract output"
                )
    for index, exhibit in enumerate(bundle["exhibits"]):
        elements = exhibit.get("elements")
        if not isinstance(elements, dict) or not elements:
            raise EvidenceError(f"exhibits[{index}].elements must be a non-empty object")
        union: list[str] = []
        for element_id, result_ids in elements.items():
            if not isinstance(element_id, str) or RESULT_ID_RE.fullmatch(element_id) is None:
                raise EvidenceError(f"exhibits[{index}].elements has invalid element ID")
            union.extend(_string_list(
                result_ids, f"exhibits[{index}].elements.{element_id}", nonempty=True
            ))
        if len(union) != len(set(union)):
            raise EvidenceError(f"exhibits[{index}].elements assigns a result more than once")
        if set(union) != set(exhibit["result_ids"]):
            raise EvidenceError(f"exhibits[{index}].result_ids must equal the elements union")
    by_id = {item["analysis_id"]: item for item in projections}
    for analysis_id, result_ids in ownership.items():
        by_id[analysis_id]["result_ids"] = sorted(result_ids)
    return [by_id[analysis_id] for analysis_id in sorted(by_id)]


def effective_renderer_inputs(bundle: dict[str, Any]) -> list[str]:
    return bundle["renderer"].get(
        "inputs", [artifact["path"] for artifact in bundle["artifacts"]]
    )


def extend_empirical_identity_index(
        contracts: dict[str, dict[str, Any]],
        identities: dict[tuple[str, str], str] | None = None,
        *, scope: str) -> dict[tuple[str, str], str]:
    """Make stable definition IDs mean one canonical object across analyses."""
    if identities is None:
        identities = {}
    for contract in contracts.values():
        for section, definitions in contract["effective"].items():
            for definition_id, definition in definitions.items():
                key = (section, definition_id)
                digest = object_digest(definition)
                prior = identities.get(key)
                if prior is not None and prior != digest:
                    raise EvidenceError(
                        f"stable empirical ID {section}.{definition_id} has "
                        f"conflicting definitions {scope}; use a new ID"
                    )
                identities[key] = digest
    return identities


def lifecycle_receipt(
        root: Path, registry: dict[str, Any], receipt_raw: str) -> dict[str, Any]:
    """Load receipt bytes against either their live or retired registry fingerprint."""
    expected = registry["receipt_fingerprints"].get(receipt_raw)
    if expected is None:
        expected = next(
            (entry["last_fingerprint"] for entry in registry["retired"]
             if entry["receipt"] == receipt_raw),
            None,
        )
    if expected is None:
        raise EvidenceError(f"result receipt is not registered: {receipt_raw}")
    receipt, snapshot = load_json_snapshot(root, receipt_raw)
    if snapshot != expected:
        raise EvidenceError(f"registered result receipt bytes are stale: {receipt_raw}")
    if not isinstance(receipt, dict):
        raise EvidenceError(f"malformed result receipt: {receipt_raw}")
    return receipt


def empirical_operand_handoff_terminals(
        root: Path, registry: dict[str, Any]) -> dict[str, str]:
    """Map every accepted receipt to the active receipt terminating its handoff chain."""
    terminals = {raw: raw for raw in registry["active"]}
    retired = {entry["receipt"]: entry for entry in registry["retired"]}
    visiting: set[str] = set()

    def terminal(raw: str) -> str | None:
        if raw in terminals:
            return terminals[raw]
        entry = retired.get(raw)
        if entry is None or "superseded_by" not in entry:
            return None
        if raw in visiting:
            raise EvidenceError("retired empirical evidence handoff contains a cycle")
        visiting.add(raw)
        successor = entry["superseded_by"]
        successor_receipt = lifecycle_receipt(root, registry, successor)
        if raw not in result_receipt_supersedes(
                root, successor, successor_receipt):
            raise EvidenceError(
                f"retired empirical evidence has an invalid handoff: {raw} -> {successor}"
            )
        result = terminal(successor)
        visiting.remove(raw)
        if result is not None:
            terminals[raw] = result
        return result

    for raw in retired:
        terminal(raw)
    return terminals


def empirical_operand_eligible_receipts(
        root: Path, registry: dict[str, Any]) -> set[str]:
    """Return active evidence plus retired evidence on an accepted handoff chain."""
    return set(empirical_operand_handoff_terminals(root, registry))


def empirical_operand_snapshot_failures(
        root: Path, receipt: dict[str, Any], where: str) -> list[str]:
    """Check the full intrinsic evidence closure behind an external operand."""
    failures: list[str] = []
    producer = receipt["producer_run"]
    for key in ("plan", "bundle", "code", "inputs", "renderer_code", "artifacts"):
        value = producer[key]
        entries = [value] if key in {"plan", "bundle"} else value
        failures.extend(compare_snapshot(root, entries, f"{where} producer_run.{key}"))
    render = receipt["render_run"]
    if render is not None:
        for key in ("code", "exhibits"):
            failures.extend(compare_snapshot(
                root, render[key], f"{where} render_run.{key}"
            ))
    return failures


def validate_empirical_relationships(root: Path, receipt_raw: str,
                                     plan: dict[str, Any],
                                     contracts: dict[str, dict[str, Any]], *,
                                     eligible_receipts: Iterable[str] | None = None,
                                     _validated_receipts: set[str] | None = None,
                                     _visiting_receipts: set[str] | None = None) -> None:
    """Resolve local analysis references and receipt-qualified comparison operands."""
    extend_empirical_identity_index(contracts, scope="within one receipt")
    current_results = {
        result_id
        for contract in contracts.values()
        for result_id in contract["effective"]["outputs"]
    }
    reference_dependencies: dict[str, set[str]] = {
        analysis_id: set() for analysis_id in contracts
    }
    result_dependencies: dict[str, set[str]] = {
        result_id: set() for result_id in current_results
    }
    eligible = set(eligible_receipts) if eligible_receipts is not None else None
    validated_receipts = (
        _validated_receipts if _validated_receipts is not None else set()
    )
    visiting_receipts = (
        _visiting_receipts if _visiting_receipts is not None else {receipt_raw}
    )
    external_cache: dict[str, dict[str, Any]] = {}
    external_receipts: dict[str, dict[str, Any]] = {}
    external_bundle_paths: dict[str, str] = {}
    for analysis_id, contract in contracts.items():
        reference_id = contract.get("reference_analysis_id")
        if reference_id is not None and reference_id not in contracts:
            raise EvidenceError(
                f"analysis {analysis_id} reference_analysis_id is not an analysis "
                "in the same receipt"
            )
        if reference_id is not None:
            reference_dependencies[analysis_id].add(reference_id)
        bound_paths = {
            path
            for paths in plan["analyses"][analysis_id]["input_bindings"].values()
            for path in paths
        }
        for result_id, output in contract["effective"]["outputs"].items():
            for index, operand in enumerate(output.get("operands", [])):
                where = f"analysis {analysis_id} output {result_id} operand {index}"
                operand_raw, operand_path = result_receipt_path(root, operand["receipt"])
                if operand_raw != operand["receipt"]:
                    raise EvidenceError(f"{where} receipt path is not normalized")
                operand_result = operand["result_id"]
                if operand_raw == receipt_raw:
                    if operand_result == result_id:
                        raise EvidenceError(f"{where} directly references its own result")
                    if operand_result not in current_results:
                        raise EvidenceError(f"{where} references an unknown current result")
                    result_dependencies[result_id].add(operand_result)
                    continue
                if operand_raw not in bound_paths:
                    raise EvidenceError(
                        f"{where} receipt must be bound to this analysis input"
                    )
                if eligible is not None and operand_raw not in eligible:
                    raise EvidenceError(
                        f"{where} receipt is not eligible empirical comparison evidence"
                    )
                if operand_raw not in external_cache:
                    if not operand_path.exists():
                        raise EvidenceError(f"{where} receipt does not exist")
                    operand_receipt = validate_receipt_contract(root, operand_path)
                    external_receipts[operand_raw] = operand_receipt
                    stale = empirical_operand_snapshot_failures(
                        root, operand_receipt, f"{where} receipt"
                    )
                    if stale:
                        raise EvidenceError(
                            f"{where} receipt evidence is stale: " + "; ".join(stale)
                        )
                    if (operand_receipt["receipt_version"] == EMPIRICAL_RECEIPT_VERSION
                            and operand_raw not in validated_receipts):
                        if operand_raw in visiting_receipts:
                            raise EvidenceError(
                                f"{where} receipt comparison dependency contains a cycle"
                            )
                        operand_plan_path = operand_receipt["producer_run"]["plan"]["path"]
                        operand_plan = validate_run_plan(
                            load_json(root / operand_plan_path), root
                        )
                        operand_contracts, _ = validate_empirical_plan(
                            root, operand_plan, completed=True
                        )
                        visiting_receipts.add(operand_raw)
                        try:
                            validate_empirical_relationships(
                                root, operand_raw, operand_plan, operand_contracts,
                                eligible_receipts=eligible,
                                _validated_receipts=validated_receipts,
                                _visiting_receipts=visiting_receipts,
                            )
                        finally:
                            visiting_receipts.remove(operand_raw)
                        validated_receipts.add(operand_raw)
                    bundle_snapshot = operand_receipt["producer_run"]["bundle"]
                    bundle_path = bundle_snapshot["path"]
                    external_bundle_paths[operand_raw] = bundle_path
                    operand_bundle, _, _ = bundle_and_path(root, bundle_path)
                    external_cache[operand_raw] = operand_bundle["results"]
                if external_bundle_paths[operand_raw] not in bound_paths:
                    raise EvidenceError(
                        f"{where} receipt bundle must be bound to this analysis input"
                    )
                if operand_result not in external_cache[operand_raw]:
                    raise EvidenceError(f"{where} references an unknown result")
                result = external_cache[operand_raw][operand_result]
                if "value" not in result:
                    artifact_raw = result["artifact"]
                    if artifact_raw not in bound_paths:
                        raise EvidenceError(
                            f"{where} result artifact must be bound to this analysis input"
                        )
                    snapshots = [
                        snapshot for snapshot in
                        external_receipts[operand_raw]["producer_run"]["artifacts"]
                        if snapshot.get("path") == artifact_raw
                    ]
                    if len(snapshots) != 1:
                        raise EvidenceError(f"{where} result artifact lacks one receipt snapshot")
                    stale_artifact = compare_snapshot(
                        root, snapshots, f"{where} result artifact"
                    )
                    if stale_artifact:
                        raise EvidenceError(
                            f"{where} result artifact is stale: " +
                            "; ".join(stale_artifact)
                        )

    def reject_cycles(graph: dict[str, set[str]], label: str) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise EvidenceError(f"{label} cycle includes {node}")
            if node in visited:
                return
            visiting.add(node)
            for dependency in graph[node]:
                visit(dependency)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    reject_cycles(reference_dependencies, "reference_analysis_id")
    reject_cycles(result_dependencies, "current-receipt comparison operand")


def empirical_operand_receipt_closure(
        root: Path, registry: dict[str, Any], receipt_raw: str, *,
        eligible: set[str], memo: dict[str, set[str]],
        visiting: set[str] | None = None) -> set[str]:
    """Return every external receipt below one empirical receipt's operand DAG."""
    if receipt_raw in memo:
        return memo[receipt_raw]
    if visiting is None:
        visiting = set()
    if receipt_raw in visiting:
        raise EvidenceError(
            f"empirical receipt comparison dependency contains a cycle at {receipt_raw}"
        )
    visiting.add(receipt_raw)
    receipt_value = lifecycle_receipt(root, registry, receipt_raw)
    if receipt_value.get("receipt_version") != EMPIRICAL_RECEIPT_VERSION:
        visiting.remove(receipt_raw)
        memo[receipt_raw] = set()
        return set()
    _, receipt_path = result_receipt_path(root, receipt_raw)
    receipt = validate_receipt_contract(root, receipt_path)
    plan_snapshot = receipt["producer_run"]["plan"]
    stale = compare_snapshot(
        root, [plan_snapshot], f"empirical dependency {receipt_raw} plan"
    )
    if stale:
        raise EvidenceError("; ".join(stale))
    plan = validate_run_plan(load_json(root / plan_snapshot["path"]), root)
    contracts, _ = validate_empirical_plan(root, plan, completed=True)
    direct = {
        operand["receipt"]
        for contract in contracts.values()
        for output in contract["effective"]["outputs"].values()
        for operand in output.get("operands", [])
        if operand["receipt"] != receipt_raw
    }
    ineligible = sorted(direct - eligible)
    if ineligible:
        raise EvidenceError(
            f"active empirical dependency {receipt_raw} cites ineligible evidence: " +
            ", ".join(ineligible)
        )
    closure = set(direct)
    for cited_raw in direct:
        closure.update(empirical_operand_receipt_closure(
            root, registry, cited_raw, eligible=eligible, memo=memo,
            visiting=visiting,
        ))
    visiting.remove(receipt_raw)
    memo[receipt_raw] = closure
    return closure


def active_empirical_operand_dependents(
        root: Path, registry: dict[str, Any], targets: Iterable[str]
        ) -> dict[str, list[str]]:
    """Find active empirical receipts whose complete operand DAG cites a target."""
    target_set = set(targets)
    dependents = {raw: [] for raw in target_set}
    terminals = empirical_operand_handoff_terminals(root, registry)
    eligible = set(terminals)
    memo: dict[str, set[str]] = {}
    for dependent_raw in registry["active"]:
        if dependent_raw in target_set:
            continue
        cited = empirical_operand_receipt_closure(
            root, registry, dependent_raw, eligible=eligible, memo=memo
        )
        for cited_raw in cited:
            terminal = terminals.get(cited_raw)
            if cited_raw in target_set:
                dependents[cited_raw].append(dependent_raw)
            elif terminal in target_set:
                dependents[terminal].append(dependent_raw)
    return dependents


def enforce_empirical_spec_immutability(root: Path, spec_paths: Iterable[str],
                                        registry: dict[str, Any]) -> None:
    """Never let replacement waivers turn a baseline or contract path mutable."""
    specs = set(spec_paths)
    receipt_paths = list(registry["active"])
    receipt_paths.extend(entry["receipt"] for entry in registry["pending"])
    receipt_paths.extend(entry["receipt"] for entry in registry["retired"])
    for receipt_raw in receipt_paths:
        _, receipt_path_value = result_receipt_path(root, receipt_raw)
        raw_receipt = load_json(receipt_path_value)
        if (not isinstance(raw_receipt, dict) or
                raw_receipt.get("receipt_version") != EMPIRICAL_RECEIPT_VERSION):
            continue
        receipt = validate_receipt_contract(root, receipt_path_value)
        for item in receipt["lineage"]:
            specs.update({item["baseline_path"], item["contract_path"]})
    current = {raw: fingerprint(root, raw) for raw in specs}
    for receipt_raw in receipt_paths:
        _, receipt_path_value = result_receipt_path(root, receipt_raw)
        raw_receipt = load_json(receipt_path_value)
        if (not isinstance(raw_receipt, dict) or
                raw_receipt.get("receipt_version") != EMPIRICAL_RECEIPT_VERSION):
            continue
        receipt = validate_receipt_contract(root, receipt_path_value)
        for snapshot in receipt["producer_run"]["inputs"]:
            raw = snapshot.get("path") if isinstance(snapshot, dict) else None
            if raw in current and snapshot != current[raw]:
                raise EvidenceError(
                    f"empirical baseline/contract path changed in place after receipt "
                    f"binding: {raw} (bound by {receipt_raw})"
                )


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
    if (not isinstance(producer["reproducibility"], str) or
            producer["reproducibility"] not in {"exact", "bounded", "captured"}):
        raise EvidenceError("producer.reproducibility must be exact, bounded, or captured")
    if "notes" in producer and not isinstance(producer["notes"], str):
        raise EvidenceError("producer.notes must be a string")

    results = bundle["results"]
    if not isinstance(results, dict) or not results:
        raise EvidenceError("results must be a non-empty object")
    result_allowed = {"description", "value", "unit", "display", "uncertainty",
                      "artifact", "selector", "metadata", "analysis_id"}
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
        if "analysis_id" in result and (
                not isinstance(result["analysis_id"], str) or
                RESULT_ID_RE.fullmatch(result["analysis_id"]) is None):
            raise EvidenceError(f"results.{result_id}.analysis_id must be a stable ID")
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
    _require_keys(renderer, {"code"}, {"code", "notes", "inputs"}, "renderer")
    renderer_code = _string_list(renderer["code"], "renderer.code")
    renderer["code"] = [project_path(root, raw)[0] for raw in renderer_code]
    if len(renderer["code"]) != len(set(renderer["code"])):
        raise EvidenceError("renderer.code contains normalized duplicates")
    if "notes" in renderer and not isinstance(renderer["notes"], str):
        raise EvidenceError("renderer.notes must be a string")
    if "inputs" in renderer:
        renderer_inputs = _string_list(renderer["inputs"], "renderer.inputs")
        renderer["inputs"] = [project_path(root, raw)[0] for raw in renderer_inputs]
        if len(renderer["inputs"]) != len(set(renderer["inputs"])):
            raise EvidenceError("renderer.inputs contains normalized duplicates")
        if not set(renderer["inputs"]).issubset(artifact_paths):
            raise EvidenceError("renderer.inputs must be a subset of artifacts")

    exhibits = bundle["exhibits"]
    if not isinstance(exhibits, list):
        raise EvidenceError("exhibits must be an array")
    exhibit_ids: set[str] = set()
    exhibit_paths: set[str] = set()
    for index, exhibit in enumerate(exhibits):
        if not isinstance(exhibit, dict):
            raise EvidenceError(f"exhibits[{index}] must be an object")
        _require_keys(exhibit, {"id", "kind", "path", "description", "result_ids"},
                      {"id", "kind", "path", "description", "result_ids", "elements"},
                      f"exhibits[{index}]")
        exhibit_id = exhibit["id"]
        if not isinstance(exhibit_id, str) or not RESULT_ID_RE.fullmatch(exhibit_id):
            raise EvidenceError(f"invalid exhibit id: {exhibit_id!r}")
        if exhibit_id in exhibit_ids:
            raise EvidenceError(f"duplicate exhibit id: {exhibit_id}")
        exhibit_ids.add(exhibit_id)
        if (not isinstance(exhibit["kind"], str) or
                exhibit["kind"] not in {"table", "figure"}):
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
                       environment: dict[str, str],
                       pass_fds: tuple[int, ...] = ()
                       ) -> tuple[int, bytes, bytes, bool]:
    """Run one process group, capturing bounded output under a parent-death guard."""
    if not hasattr(os, "fork"):
        raise EvidenceError("isolated results execution requires POSIX process supervision")
    capture_limit = 1024 * 1024
    stdout_capture = tempfile.TemporaryFile()
    stderr_capture = tempfile.TemporaryFile()
    read_fd, write_fd = os.pipe()
    supervisor = os.fork()
    if supervisor == 0:
        try:
            os.close(write_fd)
            if _LOCK_DESCRIPTOR is not None:
                os.close(_LOCK_DESCRIPTOR)
            child = subprocess.Popen(
                command, cwd=cwd, env=environment, close_fds=True,
                pass_fds=pass_fds,
                start_new_session=True, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for descriptor in pass_fds:
                os.close(descriptor)
            assert child.stdout is not None and child.stderr is not None
            streams = {
                child.stdout.fileno(): stdout_capture.fileno(),
                child.stderr.fileno(): stderr_capture.fileno(),
            }
            totals = {descriptor: 0 for descriptor in streams}
            overflow = False
            for descriptor in streams:
                os.set_blocking(descriptor, False)
            while True:
                watched = [read_fd, *streams]
                readable, _, _ = select.select(watched, [], [], 0.02)
                if read_fd in readable and os.read(read_fd, 1) == b"":
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    child.wait()
                    remove_abandoned_workspace(cwd)
                    os._exit(254)
                for descriptor in list(streams):
                    if descriptor not in readable:
                        continue
                    try:
                        chunk = os.read(descriptor, 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        streams.pop(descriptor)
                        continue
                    remaining = capture_limit - totals[descriptor]
                    if remaining > 0:
                        written = chunk[:remaining]
                        os.write(streams[descriptor], written)
                        totals[descriptor] += len(written)
                    if len(chunk) > max(0, remaining):
                        overflow = True
                returncode = child.poll()
                if returncode is not None and not streams:
                    if overflow:
                        os._exit(252)
                    os._exit(min(returncode, 251) if returncode >= 0
                             else min(128 - returncode, 251))
        except BaseException:
            os._exit(253)
    os.close(read_fd)
    write_open = True
    try:
        if pass_fds:
            while True:
                waited, status = os.waitpid(supervisor, os.WNOHANG)
                if waited == supervisor:
                    break
                if _SOURCE_LEASE_BROKEN:
                    os.close(write_fd)
                    write_open = False
                    _, status = os.waitpid(supervisor, 0)
                    break
                time.sleep(0.02)
        else:
            _, status = os.waitpid(supervisor, 0)
    finally:
        if write_open:
            os.close(write_fd)
    stdout_capture.seek(0)
    stderr_capture.seek(0)
    stdout = stdout_capture.read()
    stderr = stderr_capture.read()
    stdout_capture.close()
    stderr_capture.close()
    return os.waitstatus_to_exitcode(status), stdout, stderr, (
        os.waitstatus_to_exitcode(status) == 252
    )


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _sha256_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _runtime_descriptor_identity(descriptor: int, display_path: str,
                                 resolved_path: str,
                                 budget: _EnvironmentCaptureBudget,
                                 *, link_target: str | None = None,
                                 require_unaliased: bool = False) -> dict[str, Any]:
    """Hash a securely opened runtime descriptor within the capture budget."""
    try:
        before = os.fstat(descriptor)
        if (not stat.S_ISREG(before.st_mode) or
                (require_unaliased and before.st_nlink != 1)):
            raise EvidenceError(f"runtime file is not regular: {display_path}")
        if (before.st_dev, before.st_ino) in budget.forbidden_inodes:
            raise EvidenceError(
                f"credential-bearing file may not enter environment capture: {display_path}"
            )
        budget.reserve(before.st_size, display_path)
        digest = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise EvidenceError(f"runtime file truncated while captured: {display_path}")
            digest.update(chunk)
            remaining -= len(chunk)
        after = os.fstat(descriptor)
        identity_before = (
            before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
            before.st_ctime_ns,
        )
        identity_after = (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if identity_before != identity_after:
            raise EvidenceError(f"runtime file changed while captured: {display_path}")
        result: dict[str, Any] = {
            "path": display_path,
            "resolved_path": resolved_path,
            "sha256": f"sha256:{digest.hexdigest()}",
            "size": before.st_size,
        }
        if link_target is not None:
            result["link_target"] = link_target
        return result
    finally:
        os.close(descriptor)


def _host_file_identity(path: Path, display_path: str,
                        budget: _EnvironmentCaptureBudget, *,
                        expose_resolved_path: bool = False,
                        allowed_root: Path | None = None) -> dict[str, Any]:
    """Fingerprint one host runtime file without executing project-controlled code."""
    try:
        requested = path.absolute()
        resolved = requested.resolve(strict=True)
        if allowed_root is not None:
            resolved_allowed_root = allowed_root.resolve(strict=True)
            if not _inside(resolved, resolved_allowed_root):
                raise EvidenceError(
                    f"runtime metadata resolves outside its environment: {display_path}"
                )
        link_target = os.readlink(requested) if requested.is_symlink() else None
        descriptor = _open_entry_read(resolved)
    except (OSError, RuntimeError) as exc:
        raise EvidenceError(f"cannot inspect runtime file {display_path}: {exc}") from exc
    resolved_display = (str(resolved) if expose_resolved_path or
                        Path(display_path).is_absolute() else display_path)
    return _runtime_descriptor_identity(
        descriptor, display_path, resolved_display, budget, link_target=link_target
    )


def _optional_runtime_file(path: Path, display_path: str, *,
                           allowed_root: Path | None = None,
                           budget: _EnvironmentCaptureBudget) -> dict[str, Any] | None:
    try:
        path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise EvidenceError(f"cannot inspect runtime file {display_path}: {exc}") from exc
    return _host_file_identity(
        path, display_path, budget, allowed_root=allowed_root
    )


def _metadata_name_version(path: Path, allowed_root: Path,
                           budget: _EnvironmentCaptureBudget
                           ) -> tuple[str | None, str | None]:
    """Read only the bounded RFC-822 header needed for package name/version."""
    try:
        resolved = path.resolve(strict=True)
        if not _inside(resolved, allowed_root.resolve(strict=True)):
            return None, None
        descriptor = _open_entry_read(resolved)
    except (EvidenceError, OSError, RuntimeError):
        return None, None
    try:
        before = os.fstat(descriptor)
        maximum = 4 * 1024 * 1024
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            return None, None
        if (before.st_dev, before.st_ino) in budget.forbidden_inodes:
            raise EvidenceError(
                f"credential-bearing file may not enter environment capture: {path}"
            )
        budget.reserve(before.st_size, str(path))
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                return None, None
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if (len(raw) > maximum or
                (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
                 before.st_ctime_ns) !=
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns,
                 after.st_ctime_ns)):
            return None, None
    finally:
        os.close(descriptor)
    name: str | None = None
    version: str | None = None
    for line in raw.decode("utf-8", errors="replace").splitlines():
        if not line:
            break
        key, separator, value = line.partition(":")
        if not separator:
            continue
        folded = key.strip().casefold()
        if folded == "name" and name is None:
            candidate = value.strip()
            if (len(candidate) <= 512 and
                    not any(ord(character) < 32 for character in candidate)):
                name = candidate
        elif folded == "version" and version is None:
            candidate = value.strip()
            if (len(candidate) <= 512 and
                    not any(ord(character) < 32 for character in candidate)):
                version = candidate
    return name, version


def _bounded_directory_paths(path: Path, maximum: int, where: str,
                             budget: _EnvironmentCaptureBudget) -> list[Path]:
    """Enumerate a resolved directory through a held descriptor with a hard cap."""
    descriptor = _open_directory_path(path)
    names: list[str] = []
    try:
        with os.scandir(descriptor) as entries:
            for entry in entries:
                budget.observe_entry(where)
                _validate_descendant_name(entry.name, path)
                names.append(entry.name)
                if len(names) > maximum:
                    raise EvidenceError(f"too many entries while capturing {where}")
    except OSError as exc:
        raise EvidenceError(f"cannot enumerate {where}: {exc}") from exc
    finally:
        os.close(descriptor)
    return [path / name for name in sorted(names, key=lambda value: (value.casefold(), value))]


def _venv_site_packages(venv: Path, budget: _EnvironmentCaptureBudget) -> list[Path]:
    venv_root = venv.resolve()
    candidates: list[Path] = []
    for lib_name in ("lib", "lib64"):
        library = venv / lib_name
        try:
            library.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise EvidenceError(f"cannot inspect project venv library {library}: {exc}") from exc
        try:
            resolved_library = library.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise EvidenceError(f"cannot resolve project venv library {library}: {exc}") from exc
        if not _inside(resolved_library, venv_root):
            raise EvidenceError(f"project venv library resolves outside its environment: {library}")
        try:
            children = _bounded_directory_paths(
                resolved_library, MAX_VENV_LIBRARY_ENTRIES,
                f"project venv library {library}", budget,
            )
        except (NotADirectoryError, PermissionError, OSError) as exc:
            raise EvidenceError(f"cannot enumerate project venv library {library}: {exc}") from exc
        for child in children:
            if child.name.startswith("python"):
                candidates.append(child / "site-packages")
    candidates.append(venv / "Lib" / "site-packages")
    result: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            candidate.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise EvidenceError(
                f"cannot inspect project venv site-packages {candidate}: {exc}"
            ) from exc
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise EvidenceError(
                f"cannot resolve project venv site-packages {candidate}: {exc}"
            ) from exc
        if not _inside(resolved, venv_root):
            raise EvidenceError(
                f"project venv site-packages resolves outside its environment: {candidate}"
            )
        if not resolved.is_dir():
            raise EvidenceError(f"project venv site-packages is not a directory: {candidate}")
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    return result


def _capture_python_venv(root: Path, budget: _EnvironmentCaptureBudget
                         ) -> dict[str, Any] | None:
    """Capture installed Python distribution metadata without importing packages."""
    venv = root / ".venv"
    try:
        if not venv.is_dir() or venv.is_symlink():
            return None
    except OSError:
        return None
    venv_root = venv.resolve()
    config = _optional_runtime_file(
        venv / "pyvenv.cfg", ".venv/pyvenv.cfg",
        allowed_root=venv_root, budget=budget,
    )
    distributions: list[dict[str, Any]] = []
    path_configuration: list[dict[str, Any]] = []
    for site_packages in _venv_site_packages(venv, budget):
        try:
            site_display = site_packages.relative_to(root).as_posix()
        except ValueError:
            site_display = str(site_packages)
        try:
            children = _bounded_directory_paths(
                site_packages, MAX_VENV_SITE_PACKAGES_ENTRIES,
                f"project venv site-packages {site_display}", budget,
            )
        except OSError as exc:
            path_configuration.append({"path": site_display, "error": str(exc)})
            continue
        for child in children:
            folded = child.name.casefold()
            if folded.endswith((".pth", ".egg-link")) or folded in {
                    "sitecustomize.py", "usercustomize.py"}:
                record = _optional_runtime_file(
                    child, f"{site_display}/{child.name}",
                    allowed_root=venv_root, budget=budget,
                )
                if record is not None:
                    path_configuration.append(record)
                continue
            if not folded.endswith((".dist-info", ".egg-info")):
                continue
            metadata_path: Path | None = None
            try:
                child_is_file = child.is_file()
            except OSError:
                child_is_file = False
            if child_is_file and folded.endswith(".dist-info"):
                raise EvidenceError(
                    f"project venv dist-info entry must be a directory: {child}"
                )
            if child_is_file:
                metadata_path = child
            else:
                for candidate in (child / "METADATA", child / "PKG-INFO"):
                    try:
                        if candidate.is_file():
                            metadata_path = candidate
                            break
                    except OSError:
                        continue
            name, version = ((None, None) if metadata_path is None
                             else _metadata_name_version(
                                 metadata_path, venv_root, budget
                             ))
            files: dict[str, dict[str, Any]] = {}
            if child_is_file:
                record = _optional_runtime_file(
                    child, f"{site_display}/{child.name}",
                    allowed_root=venv_root, budget=budget,
                )
                if record is not None:
                    files["PKG-INFO"] = record
            else:
                for filename in ("METADATA", "PKG-INFO", "RECORD", "direct_url.json",
                                 "INSTALLER", "entry_points.txt"):
                    record = _optional_runtime_file(
                        child / filename, f"{site_display}/{child.name}/{filename}",
                        allowed_root=venv_root, budget=budget,
                    )
                    if record is not None:
                        files[filename] = record
            distributions.append({
                "location": f"{site_display}/{child.name}",
                "name": name,
                "version": version,
                "metadata_files": files,
            })
    distributions.sort(key=lambda item: (item["location"].casefold(), item["location"]))
    path_configuration.sort(key=lambda item: (item["path"].casefold(), item["path"]))
    return {
        "configuration": config,
        "distributions": distributions,
        "path_configuration": path_configuration,
    }


def _capture_dependency_manifests(root: Path, budget: _EnvironmentCaptureBudget
                                  ) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in DEPENDENCY_MANIFEST_PATHS:
        path = root / raw
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise EvidenceError(f"cannot inspect dependency manifest {raw}: {exc}") from exc
        if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
            raise EvidenceError(f"dependency manifest is a directory: {raw}")
        parent_fd, name = _open_relative_parent(root, raw, create=False)
        descriptor: int | None = None
        try:
            expected = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if not stat.S_ISREG(expected.st_mode) or expected.st_nlink != 1:
                raise EvidenceError(
                    f"dependency manifest must be one non-aliased regular file: {raw}"
                )
            flags = (os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) |
                     getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
            descriptor = os.open(name, flags, dir_fd=parent_fd)
            opened = os.fstat(descriptor)
            if ((opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino)):
                raise EvidenceError(f"dependency manifest changed while opening: {raw}")
            capture_descriptor = descriptor
            descriptor = None
            records.append(_runtime_descriptor_identity(
                capture_descriptor, raw, raw, budget, require_unaliased=True
            ))
        except OSError as exc:
            raise EvidenceError(f"cannot inspect dependency manifest {raw}: {exc}") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(parent_fd)
    return records


def _credential_file_inodes(root: Path, budget: _EnvironmentCaptureBudget
                            ) -> set[tuple[int, int]]:
    """Identify root `.env*` files so aliases cannot become hash oracles."""
    descriptor = _open_directory_path(root.resolve())
    identities: set[tuple[int, int]] = set()
    try:
        with os.scandir(descriptor) as entries:
            for entry in entries:
                budget.observe_entry("project root")
                if not entry.name.casefold().startswith(".env"):
                    continue
                try:
                    info = entry.stat(follow_symlinks=False)
                except OSError as exc:
                    raise EvidenceError(
                        f"cannot inspect credential-bearing project file {entry.name}: {exc}"
                    ) from exc
                if not stat.S_ISREG(info.st_mode):
                    raise EvidenceError(
                        f"credential-bearing project path must be a regular file: {entry.name}"
                    )
                identities.add((info.st_dev, info.st_ino))
    except OSError as exc:
        raise EvidenceError(f"cannot enumerate project root for environment capture: {exc}") from exc
    finally:
        os.close(descriptor)
    return identities


def _libc_identity() -> tuple[str, str]:
    """Return libc identity without scanning or executing the captured launcher."""
    try:
        raw = os.confstr("CS_GNU_LIBC_VERSION")
    except (OSError, ValueError):
        raw = None
    if raw:
        name, separator, version = raw.partition(" ")
        return name, version if separator else ""
    if sys.platform == "darwin":
        return "libSystem", ""
    return "", ""


UV_PYTHON_LAUNCHERS = {"python", "python3", "python.exe", "python3.exe"}


def _uv_python_run(command: list[str], has_venv: bool) -> bool:
    return bool(
        has_venv and len(command) >= 4 and
        Path(command[0]).name.casefold() in {"uv", "uv.exe"} and
        command[1].casefold() == "run" and
        Path(command[2]).name.casefold() in UV_PYTHON_LAUNCHERS
    )


def _venv_python_launcher(venv: Path, requested: str) -> Path:
    folded = Path(requested).name.casefold()
    names = [folded]
    if folded.endswith(".exe"):
        names.append(folded[:-4])
    names.extend(("python3", "python"))
    for name in dict.fromkeys(names):
        candidate = venv / "bin" / name
        try:
            if candidate.is_file():
                return candidate.absolute()
        except OSError:
            continue
    return (venv / "bin" / names[0]).absolute()


def _runtime_search_path(root: Path, environment: dict[str, str],
                         has_venv: bool) -> str:
    parts: list[str] = []
    if has_venv:
        parts.append(str(root / ".venv/bin"))
    for raw in environment.get("PATH", os.defpath).split(os.pathsep):
        if not raw:
            continue
        candidate = Path(raw)
        if not candidate.is_absolute() or _inside(candidate, root):
            continue
        if raw not in parts:
            parts.append(raw)
    return os.pathsep.join(parts)


def resolved_runtime_executable(command: list[str], root: Path,
                                environment: dict[str, str]) -> Path:
    """Resolve the launcher exactly as isolated_runtime will select it."""
    venv = root / ".venv"
    has_venv = venv.is_dir() and not venv.is_symlink()
    if _uv_python_run(command, has_venv):
        return _venv_python_launcher(venv, command[2])
    resolved = shutil.which(
        command[0], path=_runtime_search_path(root, environment, has_venv)
    )
    executable = Path(resolved) if resolved is not None else Path(command[0])
    if not executable.is_absolute():
        executable = root / executable
    return executable.absolute()


def capture_execution_environment(root: Path, command: list[str]) -> dict[str, Any]:
    """Capture historical runtime provenance without changing or executing it."""
    environment = os.environ.copy()
    budget = _EnvironmentCaptureBudget()
    budget.forbidden_inodes = _credential_file_inodes(root, budget)
    executable = resolved_runtime_executable(command, root, environment)
    display = (executable.relative_to(root).as_posix()
               if _inside(executable, root) else str(executable))
    uname = os.uname()
    os_release = _optional_runtime_file(
        Path("/etc/os-release"), "/etc/os-release", budget=budget
    )
    libc_name, libc_version = _libc_identity()
    runtime_environment = {
        key: environment[key]
        for key in sorted(CAPTURED_RUNTIME_ENV_KEYS)
        if key in environment
    }
    try:
        oversized_runtime_value = any(
            len(value.encode("utf-8")) > MAX_ENVIRONMENT_CAPTURE_TEXT_BYTES
            for value in runtime_environment.values()
        )
    except UnicodeError as exc:
        raise EvidenceError("captured runtime environment value is not valid UTF-8") from exc
    if oversized_runtime_value:
        raise EvidenceError("captured runtime environment value is too large")
    secrets = credential_literals(environment)
    if any(secret and secret in value
           for value in runtime_environment.values() for secret in secrets):
        raise EvidenceError(
            "captured runtime environment contains a literal provider credential"
        )
    manifest = {
        "launcher": {
            "requested": command[0],
            "executable": _host_file_identity(
                executable, display, budget, expose_resolved_path=True
            ),
        },
        "platform": {
            "system": uname.sysname,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "libc": {"name": libc_name, "version": libc_version},
            "os_release": os_release,
        },
        "runtime_environment": runtime_environment,
        "project_environment": {
            "python_venv": _capture_python_venv(root, budget),
            "dependency_manifests": _capture_dependency_manifests(root, budget),
        },
    }
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    result = {
        "capture_version": ENVIRONMENT_CAPTURE_VERSION,
        "sha256": _sha256_bytes(encoded),
        "manifest": manifest,
    }
    validate_environment_capture(result, "generated environment capture", command)
    return result


def _validate_capture_text(value: Any, where: str, *, maximum: int = 4096,
                           allow_empty: bool = False) -> None:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise EvidenceError(f"{where} is malformed")
    try:
        encoded = value.encode("utf-8")
    except UnicodeError as exc:
        raise EvidenceError(f"{where} is not valid UTF-8") from exc
    if (len(encoded) > maximum or
            any(ord(character) < 32 for character in value)):
        raise EvidenceError(f"{where} is malformed")


def _validate_capture_file(value: Any, where: str,
                           totals: list[Any]) -> None:
    base_keys = {"path", "resolved_path", "sha256", "size"}
    if (not isinstance(value, dict) or
            set(value) not in (base_keys, base_keys | {"link_target"})):
        raise EvidenceError(f"{where} is malformed")
    _validate_capture_text(value["path"], f"{where}.path")
    _validate_capture_text(value["resolved_path"], f"{where}.resolved_path")
    if "link_target" in value:
        _validate_capture_text(value["link_target"], f"{where}.link_target")
    if (not isinstance(value["sha256"], str) or
            re.fullmatch(r"sha256:[0-9a-f]{64}", value["sha256"]) is None):
        raise EvidenceError(f"{where}.sha256 is malformed")
    size = value["size"]
    if (isinstance(size, bool) or not isinstance(size, int) or size < 0 or
            size > MAX_ENVIRONMENT_CAPTURE_FILE_BYTES):
        raise EvidenceError(f"{where}.size is malformed")
    if value["path"] in totals[2]:
        raise EvidenceError(f"{where}.path is duplicated")
    totals[2].add(value["path"])
    totals[0] += 1
    totals[1] += size
    if (totals[0] > MAX_ENVIRONMENT_CAPTURE_FILES or
            totals[1] > MAX_ENVIRONMENT_CAPTURE_TOTAL_BYTES):
        raise EvidenceError(f"{where} exceeds environment capture limits")


def _validate_optional_capture_file(value: Any, where: str,
                                    totals: list[Any]) -> None:
    if value is not None:
        _validate_capture_file(value, where, totals)


def _validate_capture_project_path(value: str, where: str) -> None:
    path = PurePosixPath(value)
    if (path.is_absolute() or path.as_posix() != value or not value or value == "." or
            "\\" in value or "." in path.parts or ".." in path.parts or
            any(_forbidden_part(part) for part in path.parts)):
        raise EvidenceError(f"{where} is not a safe normalized project path")


def validate_environment_capture(value: Any, where: str,
                                 expected_command: list[str] | None = None) -> None:
    if not isinstance(value, dict) or set(value) != {
            "capture_version", "sha256", "manifest"}:
        raise EvidenceError(f"{where} is malformed")
    if (isinstance(value["capture_version"], bool) or
            value["capture_version"] != ENVIRONMENT_CAPTURE_VERSION):
        raise EvidenceError(f"{where}.capture_version is unsupported")
    manifest = value["manifest"]
    if not isinstance(manifest, dict) or set(manifest) != {
            "launcher", "platform", "runtime_environment", "project_environment"}:
        raise EvidenceError(f"{where}.manifest is malformed")
    totals: list[Any] = [0, 0, set()]
    launcher = manifest["launcher"]
    if not isinstance(launcher, dict) or set(launcher) != {"requested", "executable"}:
        raise EvidenceError(f"{where}.manifest.launcher is malformed")
    _validate_capture_text(
        launcher["requested"], f"{where}.manifest.launcher.requested"
    )
    if (expected_command is not None and
            (not expected_command or launcher["requested"] != expected_command[0])):
        raise EvidenceError(f"{where}.manifest.launcher does not match its receipt command")
    _validate_capture_file(
        launcher["executable"], f"{where}.manifest.launcher.executable", totals
    )
    launcher_file = launcher["executable"]
    if Path(launcher_file["path"]).is_absolute():
        if not Path(launcher_file["resolved_path"]).is_absolute():
            raise EvidenceError(f"{where}.manifest.launcher path is malformed")
    else:
        _validate_capture_project_path(
            launcher_file["path"], f"{where}.manifest.launcher.executable.path"
        )
        if (not launcher_file["path"].startswith(".venv/") or
                not Path(launcher_file["resolved_path"]).is_absolute()):
            raise EvidenceError(f"{where}.manifest.launcher path is malformed")
    platform_value = manifest["platform"]
    if not isinstance(platform_value, dict) or set(platform_value) != {
            "system", "release", "version", "machine", "libc", "os_release"}:
        raise EvidenceError(f"{where}.manifest.platform is malformed")
    for key in ("system", "release", "version", "machine"):
        _validate_capture_text(
            platform_value[key], f"{where}.manifest.platform.{key}", allow_empty=True
        )
    libc = platform_value["libc"]
    if not isinstance(libc, dict) or set(libc) != {"name", "version"}:
        raise EvidenceError(f"{where}.manifest.platform.libc is malformed")
    for key in ("name", "version"):
        _validate_capture_text(
            libc[key], f"{where}.manifest.platform.libc.{key}", allow_empty=True
        )
    _validate_optional_capture_file(
        platform_value["os_release"], f"{where}.manifest.platform.os_release", totals
    )
    if (platform_value["os_release"] is not None and
            (platform_value["os_release"]["path"] != "/etc/os-release" or
             not Path(platform_value["os_release"]["resolved_path"]).is_absolute())):
        raise EvidenceError(f"{where}.manifest.platform.os_release path is malformed")
    runtime_environment = manifest["runtime_environment"]
    if (not isinstance(runtime_environment, dict) or
            not set(runtime_environment).issubset(CAPTURED_RUNTIME_ENV_KEYS)):
        raise EvidenceError(f"{where}.manifest.runtime_environment is malformed")
    for key, captured_value in runtime_environment.items():
        _validate_capture_text(
            captured_value, f"{where}.manifest.runtime_environment.{key}",
            maximum=MAX_ENVIRONMENT_CAPTURE_TEXT_BYTES, allow_empty=True,
        )
    project = manifest["project_environment"]
    if not isinstance(project, dict) or set(project) != {
            "python_venv", "dependency_manifests"}:
        raise EvidenceError(f"{where}.manifest.project_environment is malformed")
    python_venv = project["python_venv"]
    if not Path(launcher_file["path"]).is_absolute() and python_venv is None:
        raise EvidenceError(f"{where}.manifest venv launcher has no venv capture")
    if python_venv is not None:
        if not isinstance(python_venv, dict) or set(python_venv) != {
                "configuration", "distributions", "path_configuration"}:
            raise EvidenceError(f"{where}.manifest.project_environment.python_venv is malformed")
        _validate_optional_capture_file(
            python_venv["configuration"],
            f"{where}.manifest.project_environment.python_venv.configuration", totals,
        )
        configuration = python_venv["configuration"]
        if (configuration is not None and
                (configuration["path"] != ".venv/pyvenv.cfg" or
                 configuration["resolved_path"] != configuration["path"])):
            raise EvidenceError(f"{where}.manifest venv configuration path is malformed")
        distributions = python_venv["distributions"]
        if (not isinstance(distributions, list) or
                len(distributions) > MAX_VENV_SITE_PACKAGES_ENTRIES):
            raise EvidenceError(f"{where}.manifest distributions are malformed")
        locations: set[str] = set()
        metadata_names = {
            "METADATA", "PKG-INFO", "RECORD", "direct_url.json",
            "INSTALLER", "entry_points.txt",
        }
        for index, distribution in enumerate(distributions):
            item_where = f"{where}.manifest distributions[{index}]"
            if not isinstance(distribution, dict) or set(distribution) != {
                    "location", "name", "version", "metadata_files"}:
                raise EvidenceError(f"{item_where} is malformed")
            _validate_capture_text(distribution["location"], f"{item_where}.location")
            _validate_capture_project_path(
                distribution["location"], f"{item_where}.location"
            )
            if (not distribution["location"].startswith(".venv/") or
                    not distribution["location"].casefold().endswith(
                        (".dist-info", ".egg-info")
                    )):
                raise EvidenceError(f"{item_where}.location is not venv metadata")
            if distribution["location"] in locations:
                raise EvidenceError(f"{item_where}.location is duplicated")
            locations.add(distribution["location"])
            for key in ("name", "version"):
                if distribution[key] is not None:
                    _validate_capture_text(
                        distribution[key], f"{item_where}.{key}", maximum=512
                    )
            metadata_files = distribution["metadata_files"]
            if (not isinstance(metadata_files, dict) or
                    not set(metadata_files).issubset(metadata_names)):
                raise EvidenceError(f"{item_where}.metadata_files is malformed")
            for key, file_value in metadata_files.items():
                _validate_capture_file(
                    file_value, f"{item_where}.metadata_files.{key}", totals
                )
                _validate_capture_project_path(
                    file_value["path"], f"{item_where}.metadata_files.{key}.path"
                )
                expected_path = f"{distribution['location']}/{key}"
                allowed_paths = {expected_path}
                if (key == "PKG-INFO" and
                        distribution["location"].casefold().endswith(".egg-info")):
                    allowed_paths.add(distribution["location"])
                if (file_value["path"] not in allowed_paths or
                        file_value["resolved_path"] != file_value["path"]):
                    raise EvidenceError(
                        f"{item_where}.metadata_files.{key}.path is malformed"
                    )
        location_list = [item["location"] for item in distributions]
        if location_list != sorted(location_list, key=lambda item: (item.casefold(), item)):
            raise EvidenceError(f"{where}.manifest distributions are not sorted")
        path_configuration = python_venv["path_configuration"]
        if (not isinstance(path_configuration, list) or
                len(path_configuration) > MAX_VENV_SITE_PACKAGES_ENTRIES):
            raise EvidenceError(f"{where}.manifest path configuration is malformed")
        path_names: set[str] = set()
        for index, file_value in enumerate(path_configuration):
            item_where = f"{where}.manifest path_configuration[{index}]"
            _validate_capture_file(file_value, item_where, totals)
            _validate_capture_project_path(file_value["path"], f"{item_where}.path")
            basename = PurePosixPath(file_value["path"]).name.casefold()
            if (not file_value["path"].startswith(".venv/") or
                    not (basename.endswith((".pth", ".egg-link")) or
                         basename in {"sitecustomize.py", "usercustomize.py"}) or
                    file_value["resolved_path"] != file_value["path"]):
                raise EvidenceError(f"{item_where}.path is not venv path configuration")
            if file_value["path"] in path_names:
                raise EvidenceError(f"{item_where}.path is duplicated")
            path_names.add(file_value["path"])
        path_list = [item["path"] for item in path_configuration]
        if path_list != sorted(path_list, key=lambda item: (item.casefold(), item)):
            raise EvidenceError(f"{where}.manifest path configuration is not sorted")
    dependencies = project["dependency_manifests"]
    if not isinstance(dependencies, list) or len(dependencies) > len(DEPENDENCY_MANIFEST_PATHS):
        raise EvidenceError(f"{where}.manifest dependency manifests are malformed")
    dependency_order = {path: index for index, path in enumerate(DEPENDENCY_MANIFEST_PATHS)}
    previous = -1
    for index, file_value in enumerate(dependencies):
        item_where = f"{where}.manifest dependency_manifests[{index}]"
        _validate_capture_file(file_value, item_where, totals)
        _validate_capture_project_path(file_value["path"], f"{item_where}.path")
        if "link_target" in file_value:
            raise EvidenceError(f"{item_where} may not be a symlink")
        position = dependency_order.get(file_value["path"])
        if position is None or position <= previous or file_value["resolved_path"] != file_value["path"]:
            raise EvidenceError(f"{item_where}.path is malformed or out of order")
        previous = position
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if value["sha256"] != _sha256_bytes(encoded):
        raise EvidenceError(f"{where}.sha256 does not match its manifest")


def require_stable_environment(before: dict[str, Any], after: dict[str, Any],
                               phase: str) -> None:
    if before != after:
        raise EvidenceError(f"execution environment changed during {phase}")


def venv_base_roots(venv: Path, root: Path) -> list[Path]:
    """Return external interpreter roots needed by a relocatable project venv."""
    config = venv / "pyvenv.cfg"
    if not config.is_file() or config.is_symlink():
        return []
    home: Path | None = None
    try:
        for line in read_utf8(config, "venv configuration").splitlines():
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
        home = Path.home().resolve()
        user_runtime_prefixes = (
            home / ".local/share/uv/python",
            home / "Library/Application Support/uv/python",
        )
        homebrew_prefixes = (Path("/opt/homebrew"), Path("/usr/local"))
        runtime_root = candidate
        if any(_inside(candidate, prefix) for prefix in user_runtime_prefixes):
            runtime_root = next(
                prefix for prefix in user_runtime_prefixes if _inside(candidate, prefix)
            )
        elif any(_inside(candidate, prefix) for prefix in homebrew_prefixes):
            # Homebrew Python loads sibling formula libraries by absolute path,
            # so binding only the Python keg is insufficient.
            runtime_root = next(
                prefix for prefix in homebrew_prefixes if _inside(candidate, prefix)
            )
        if candidate == Path("/") or _inside(candidate, root) or _inside(root, candidate):
            raise EvidenceError("project venv base runtime must not expose the project root")
        # pyvenv.cfg and the venv's interpreter links are project-writable.
        # Apart from the explicit uv/Homebrew runtime families above, accept
        # only protected system runtime trees; otherwise `home = /tmp` would
        # expose arbitrary host files inside the evidence sandbox.
        if candidate.exists() and runtime_root == candidate:
            current = candidate
            while True:
                info = current.stat()
                if (os.access(current, os.W_OK) or
                        info.st_mode & (stat.S_IWGRP | stat.S_IWOTH)):
                    raise EvidenceError(
                        "project venv base runtime must be a protected system path"
                    )
                if current.parent == current:
                    break
                current = current.parent
        if runtime_root.exists() and runtime_root not in roots:
            if _inside(root, runtime_root):
                raise EvidenceError("project must not live beneath an allowed runtime prefix")
            roots.append(runtime_root)
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
    executable = resolved_runtime_executable(rewritten, root, environment)
    neutral_venv = Path("/results-runtime-venv")
    if _uv_python_run(rewritten, has_venv):
        if not _inside(executable, venv):
            raise EvidenceError("uv Python launcher did not resolve inside the project venv")
        rewritten = [str(neutral_venv / executable.relative_to(venv)), *rewritten[3:]]
    elif has_venv and _inside(executable, venv):
        rewritten[0] = str(neutral_venv / executable.relative_to(venv))
    elif _inside(executable, root):
        raise EvidenceError("the command runtime must be the project .venv or a system executable")
    root_text = str(root)
    if any(root_text in argument for argument in rewritten[1:]):
        raise EvidenceError(
            "isolated producer/renderer command arguments may not contain the project-root path"
        )
    path_parts = [
        (str(neutral_venv / "bin") if has_venv and
         raw == str(venv / "bin") else raw)
        for raw in _runtime_search_path(root, environment, has_venv).split(os.pathsep)
        if raw
    ]
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


def credential_literals(environment: dict[str, str]) -> set[str]:
    """Return every literal spelling of an ambient provider/proxy credential."""
    literals = {
        value for key, value in environment.items()
        if key in SECRET_ENV_KEYS and value
    }
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy",
                "https_proxy", "all_proxy", "BUNDLE_HTTP_PROXY",
                "BUNDLE_HTTPS_PROXY"):
        raw = environment.get(key)
        if not raw:
            continue
        try:
            parsed = urlsplit(raw)
            encoded_username = parsed.username
            encoded_password = parsed.password
        except ValueError:
            encoded_username = None
            encoded_password = None
        userinfo = [
            value for value in (encoded_username, encoded_password) if value
        ]
        if userinfo:
            literals.add(raw)
            for value in userinfo:
                literals.add(value)
                literals.add(unquote(value))
    return literals


def reject_captured_credential_leak(stdout: bytes, stderr: bytes,
                                    environment: dict[str, str]) -> None:
    """Never release a child stream containing an ambient credential literal."""
    secrets = [value.encode() for value in credential_literals(environment) if value]
    if any(secret in stream for secret in secrets for stream in (stdout, stderr)):
        raise EvidenceError("producer/renderer output contains a literal provider credential")


def emit_captured_output(stdout: bytes, stderr: bytes) -> None:
    """Keep the command's stdout machine-readable while preserving safe diagnostics."""
    sink = sys.stderr.buffer
    for label, payload in ((b"producer/renderer stdout", stdout),
                           (b"producer/renderer stderr", stderr)):
        if not payload:
            continue
        sink.write(b"[" + label + b"]\n")
        sink.write(payload)
        if not payload.endswith(b"\n"):
            sink.write(b"\n")
    sink.flush()


def reject_credential_leak(workspace: Path, environment: dict[str, str]) -> None:
    """Reject literal provider credentials in one staged source/output tree or file."""
    secrets = {
        value.encode() for value in credential_literals(environment)
        if len(value) >= 8
    }
    if not secrets:
        return
    paths = [workspace] if workspace.is_file() else workspace.rglob("*")
    for path in paths:
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


def reject_command_credential_leak(command: list[str],
                                   environment: dict[str, str]) -> None:
    """Never serialize provider credentials or proxy passwords in command argv."""
    secrets = credential_literals(environment)
    if any(secret in argument for secret in secrets for argument in command):
        raise EvidenceError("command arguments contain a literal provider credential")


def trusted_sandbox_executable(name: str) -> str | None:
    """Resolve containment only from immutable system locations, never ambient PATH."""
    expected = {
        "bwrap": "/usr/bin/bwrap" if sys.platform.startswith("linux") else None,
        "sandbox-exec": "/usr/bin/sandbox-exec" if sys.platform == "darwin" else None,
    }.get(name)
    if expected is None:
        return None
    try:
        metadata = os.lstat(expected)
    except OSError:
        return None
    if not stat.S_ISREG(metadata.st_mode) or not os.access(expected, os.X_OK):
        return None
    return expected


def bubblewrap_supports_read_only_fd_bind(executable: str) -> bool:
    """Probe the fd-consuming bind primitive required to hide lease fds."""
    try:
        completed = subprocess.run(
            [executable, "--help"], stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=2, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0 and b"--ro-bind-fd" in (
        completed.stdout + completed.stderr
    )


def validate_read_only_bindings(cwd: Path,
                                bindings: list[tuple[int, Path, Path]]) -> None:
    """Validate descriptor-pinned declared sources and their empty mount points."""
    canonical_cwd = cwd.resolve(strict=True)
    descriptors: set[int] = set()
    destinations: list[str] = []
    for descriptor, source, destination in bindings:
        if not isinstance(descriptor, int) or descriptor < 0 or descriptor in descriptors:
            raise EvidenceError("read-only source binding descriptors must be unique")
        descriptors.add(descriptor)
        try:
            source_info = os.fstat(descriptor)
            live_info = os.stat(source, follow_symlinks=False)
        except OSError as exc:
            raise EvidenceError(f"cannot validate read-only source binding: {source}: {exc}") from exc
        if ((source_info.st_dev, source_info.st_ino) !=
                (live_info.st_dev, live_info.st_ino)):
            raise EvidenceError(f"read-only source changed before execution: {source}")
        if not stat.S_ISREG(source_info.st_mode):
            raise EvidenceError(f"read-only source is not a regular file: {source}")
        if source_info.st_nlink != 1:
            raise EvidenceError(f"read-only source is not one non-aliased file: {source}")
        if not destination.is_absolute():
            raise EvidenceError("read-only source destinations must be absolute")
        try:
            relative = destination.relative_to(canonical_cwd).as_posix()
        except ValueError as exc:
            raise EvidenceError("read-only source destination escapes the workspace") from exc
        if relative in {"", "."} or ".." in PurePosixPath(relative).parts:
            raise EvidenceError("read-only source destination must not be the workspace root")
        try:
            destination_info = os.lstat(destination)
        except OSError as exc:
            raise EvidenceError(
                f"cannot inspect read-only source mount point: {destination}: {exc}"
            ) from exc
        if stat.S_ISLNK(destination_info.st_mode):
            raise EvidenceError("read-only source destination must not be a symlink")
        if not stat.S_ISREG(destination_info.st_mode):
            raise EvidenceError("read-only file source requires a file mount point")
        destinations.append(relative)
    overlap = overlapping_pair(destinations, destinations, same=True)
    if overlap is not None:
        raise EvidenceError("read-only source destinations overlap: " + " / ".join(overlap))


def require_source_leases_intact(bindings: list[tuple[int, Path, Path]]) -> None:
    """Fail if the kernel observed a writer against any zero-copy source."""
    if _SOURCE_LEASE_BROKEN:
        raise EvidenceError("declared source write was attempted during execution")
    for descriptor, source, _ in bindings:
        try:
            lease = fcntl.fcntl(descriptor, fcntl.F_GETLEASE)
        except OSError as exc:
            raise EvidenceError(f"cannot verify declared source lease: {source}: {exc}") from exc
        if lease != fcntl.F_RDLCK:
            raise EvidenceError(f"declared source lease broke during execution: {source}")


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
        lines = read_utf8(dotenv, "project .env").splitlines()
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


def ambient_network_is_denied() -> bool:
    """Return true only when inherited policy forbids IPv4 and IPv6 sockets."""
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            probe = socket.socket(family, socket.SOCK_STREAM)
        except PermissionError:
            continue
        except OSError as exc:
            if exc.errno in {errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT}:
                continue
            # Other failures are not evidence of a kernel deny; require the
            # private namespace and fail closed if bwrap cannot create it.
            return False
        probe.close()
        return False
    return True


def execute(command: list[str], cwd: Path, *, bundle_path: str | None = None,
            extra_environment: dict[str, str] | None = None,
            project_root: Path | None = None,
            allow_network: bool = True,
            provider_credentials: set[str] | None = None,
            read_only_bindings: list[tuple[int, Path, Path]] | None = None) -> None:
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
    # Preserve the complete host-side secret vocabulary for the post-run scan.
    # Capability stripping below controls what the child receives; it must not
    # also erase the literals that staged evidence is forbidden to contain.
    credential_scan_environment = environment.copy()
    # Check before authority is stripped: renderers receive no credentials in
    # their environment, but their immutable command record must not disclose
    # a credential inherited by the host process either.
    reject_command_credential_leak(command, environment)
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
    bindings = read_only_bindings or []
    binding_descriptors: tuple[int, ...] = ()
    bubblewrap = trusted_sandbox_executable("bwrap")
    sandbox_exec = trusted_sandbox_executable("sandbox-exec")
    if bindings and (project_root is None or bubblewrap is None or
                     not bubblewrap_supports_read_only_fd_bind(bubblewrap)):
        raise EvidenceError("read-only source bindings require Linux bubblewrap")
    if project_root is not None and bubblewrap is not None:
        validate_read_only_bindings(cwd, bindings)
        sandboxed_command = [
            bubblewrap, "--die-with-parent", "--new-session", "--unshare-pid",
            "--as-pid-1",
        ]
        if not allow_network and not ambient_network_is_denied():
            sandboxed_command.append("--unshare-net")
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
        if allow_network:
            runtime_home = Path(environment["HOME"])
            for relative in (".local/state/zeropaper/wrds", ".cache/zeropaper/wrds"):
                service_path = runtime_home / relative
                if service_path.exists() and not service_path.is_symlink():
                    sandboxed_command.extend(
                        ["--ro-bind", str(service_path), str(service_path)]
                    )
        sandboxed_command.extend(["--tmpfs", str(project_root)])
        sandboxed_command.extend(["--bind", str(cwd), str(cwd)])
        binding_descriptors = tuple(binding[0] for binding in bindings)
        for descriptor, _, destination in bindings:
            sandboxed_command.extend([
                "--ro-bind-fd", str(descriptor), str(destination)
            ])
        sandboxed_command.extend(["--chdir", str(cwd), "--", *command])
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
        if allow_network:
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
            '(allow sysctl-read) (allow ipc-posix-shm) '
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
    returncode, captured_stdout, captured_stderr, output_overflow = supervised_command(
        sandboxed_command, cwd=cwd, environment=environment,
        pass_fds=binding_descriptors,
    )
    reject_captured_credential_leak(
        captured_stdout, captured_stderr, credential_scan_environment
    )
    require_source_leases_intact(bindings)
    if output_overflow:
        raise EvidenceError("producer/renderer output exceeded the 1 MiB per-stream limit")
    emit_captured_output(captured_stdout, captured_stderr)
    if returncode != 0:
        raise EvidenceError(f"command failed with exit {returncode}: {command!r}")
    reject_credential_leak(cwd, credential_scan_environment)
    for _, source, _ in bindings:
        reject_credential_leak(source, credential_scan_environment)


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
    ensure_directory_durable(path.parent)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.{label}.", dir=path.parent)
    os.close(fd)
    os.unlink(raw)
    return Path(raw)


def _dataset_namespace_path(raw: str) -> bool:
    """Reserve output/dataset case-insensitively for case-folding filesystems."""
    folded = raw.casefold()
    return folded == "output/dataset" or folded.startswith("output/dataset/")


def validate_run_plan(value: Any, root: Path, *, require_live_sources: bool = True
                      ) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError("run plan must be a JSON object")
    required = {"plan_version", "producer_code", "producer_inputs", "artifacts",
                "renderer_code", "exhibits"}
    _require_keys(
        value, required,
        required | {"provider_credentials", "network_access", "requires_dataset_release",
                    "dataset_release", "renderer_inputs", "analyses"},
        "run plan",
    )
    if (isinstance(value["plan_version"], bool) or
            not isinstance(value["plan_version"], int) or
            value["plan_version"] != RUN_PLAN_VERSION):
        raise EvidenceError(f"unsupported run plan version: {value['plan_version']!r}")
    for key in ("producer_code", "producer_inputs", "renderer_code"):
        paths = _string_list(value[key], f"run plan.{key}",
                             nonempty=(key == "producer_code"))
        value[key] = [
            project_path(root, raw, must_exist=require_live_sources)[0] for raw in paths
        ]
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
    renderer_inputs = _string_list(
        value.get("renderer_inputs", value["artifacts"]), "run plan.renderer_inputs"
    )
    value["renderer_inputs"] = [
        project_path(root, raw, must_exist=False)[0] for raw in renderer_inputs
    ]
    if len(value["renderer_inputs"]) != len(set(value["renderer_inputs"])):
        raise EvidenceError("run plan.renderer_inputs contains normalized duplicates")
    if not set(value["renderer_inputs"]).issubset(value["artifacts"]):
        raise EvidenceError("run plan.renderer_inputs must be a subset of artifacts")
    value["provider_credentials"] = _string_list(
        value.get("provider_credentials", []), "run plan.provider_credentials"
    )
    if (len(value["provider_credentials"]) != len(set(value["provider_credentials"])) or
            not set(value["provider_credentials"]).issubset(SECRET_ENV_KEYS)):
        raise EvidenceError("run plan.provider_credentials contains unsupported values")
    network_access = value.get("network_access", True)
    if not isinstance(network_access, bool):
        raise EvidenceError("run plan.network_access must be a boolean")
    value["network_access"] = network_access
    requires_dataset_release = value.get("requires_dataset_release", False)
    if not isinstance(requires_dataset_release, bool):
        raise EvidenceError("run plan.requires_dataset_release must be a boolean")
    value["requires_dataset_release"] = requires_dataset_release
    outputs = set(value["artifacts"]) | set(value["exhibits"])
    overlap = overlapping_pair(outputs, outputs, same=True)
    if overlap is not None:
        raise EvidenceError("run-plan output paths must be disjoint: " + " / ".join(overlap))
    dataset_outputs = sorted(
        raw for raw in outputs
        if _dataset_namespace_path(raw)
    )
    release = value.get("dataset_release")
    if release is None:
        if dataset_outputs:
            raise EvidenceError(
                "outputs under output/dataset require run plan.dataset_release"
            )
        return value
    if value["requires_dataset_release"]:
        raise EvidenceError(
            "a dataset release run may not itself require another dataset release"
        )
    if not isinstance(release, dict):
        raise EvidenceError("run plan.dataset_release must be an object")
    release_required = {
        "artifact", "manifest", "rights_inventory", "rights_inventory_sha256",
        "input_provenance", "rights_authority",
        "dataset_version", "analysis_receipt", "producing_receipt",
    }
    _require_keys(release, release_required, release_required, "run plan.dataset_release")
    for key in ("artifact", "manifest", "rights_inventory", "input_provenance",
                "analysis_receipt", "producing_receipt"):
        if not isinstance(release[key], str) or not release[key]:
            raise EvidenceError(f"run plan.dataset_release.{key} must be a path string")
    artifact, _ = project_path(root, release["artifact"], must_exist=False)
    if (artifact.casefold() == "output/dataset" or
            not artifact.casefold().startswith("output/dataset/") or
            artifact != artifact.casefold()):
        raise EvidenceError(
            "run plan.dataset_release.artifact must be a fresh versioned directory "
            "beneath output/dataset/"
        )
    manifest, _ = project_path(root, release["manifest"], must_exist=False)
    if manifest != artifact + "/manifest.json":
        raise EvidenceError(
            "run plan.dataset_release.manifest must be <artifact>/manifest.json"
        )
    for key in ("rights_inventory", "input_provenance"):
        release[key] = project_path(
            root, release[key], must_exist=require_live_sources
        )[0]
        if release[key] not in value["producer_inputs"]:
            raise EvidenceError(
                f"run plan.dataset_release.{key} must be a declared producer input"
            )
    rights_digest = release["rights_inventory_sha256"]
    if (not isinstance(rights_digest, str) or
            re.fullmatch(r"sha256:[0-9a-f]{64}", rights_digest) is None):
        raise EvidenceError(
            "run plan.dataset_release.rights_inventory_sha256 must be a SHA-256 digest"
        )
    if release["rights_authority"] not in {"gate2-state", "manual-caller"}:
        raise EvidenceError(
            "run plan.dataset_release.rights_authority must be gate2-state or "
            "manual-caller"
        )
    release["analysis_receipt"] = result_receipt_path(
        root, release["analysis_receipt"]
    )[0]
    if release["analysis_receipt"] not in value["producer_inputs"]:
        raise EvidenceError(
            "run plan.dataset_release.analysis_receipt must be a declared producer input"
        )
    producing_receipt, _ = project_path(
        root, release["producing_receipt"], must_exist=False
    )
    if not producing_receipt.startswith("output/"):
        raise EvidenceError(
            "run plan.dataset_release.producing_receipt must be beneath output/"
        )
    dataset_version = release["dataset_version"]
    if (isinstance(dataset_version, bool) or not isinstance(dataset_version, int) or
            dataset_version < 1):
        raise EvidenceError(
            "run plan.dataset_release.dataset_version must be a positive integer"
        )
    release["artifact"] = artifact
    release["manifest"] = manifest
    release["producing_receipt"] = producing_receipt
    if dataset_outputs != [artifact]:
        raise EvidenceError(
            "dataset release runs must declare exactly their versioned release directory "
            "under output/dataset and no dataset exhibits"
        )
    if value["artifacts"] != [artifact] or value["exhibits"]:
        raise EvidenceError(
            "dataset release runs must declare exactly one artifact (the release) "
            "and no exhibits"
        )
    if value["network_access"]:
        raise EvidenceError("dataset release runs must set network_access to false")
    if value["provider_credentials"]:
        raise EvidenceError("dataset release runs may not receive provider credentials")
    return value


SOURCE_ID_RE = re.compile(r"[a-z][a-z0-9_-]{0,63}")
RELEASE_FILE_KINDS = {"data", "code", "documentation"}
CODE_INPUT_SUFFIXES = {
    ".bash", ".c", ".cc", ".cpp", ".go", ".h", ".hpp", ".jl", ".js",
    ".lua", ".m", ".pl", ".py", ".r", ".rb", ".rs", ".sh", ".sql",
    ".ts", ".zsh",
}


def _release_relative_path(raw: Any, where: str) -> str:
    if not isinstance(raw, str) or not raw or raw.startswith("/") or "\\" in raw:
        raise EvidenceError(f"{where} must be a relative POSIX path")
    path = PurePosixPath(raw)
    if (path.as_posix() != raw or any(part in {"", ".", ".."} for part in path.parts) or
            any(_forbidden_part(part) for part in path.parts) or
            any(ord(character) < 32 for character in raw)):
        raise EvidenceError(f"{where} is not a safe relative release path: {raw!r}")
    return raw


def _validate_dataset_rights_authority(plan: dict[str, Any], root: Path) -> None:
    """Bind releases to autonomous Gate 2 or an explicit manual caller."""
    release = plan.get("dataset_release")
    if release is None:
        return
    deployment, _ = load_json_snapshot(root, ".deploy_manifest.json")
    manifest_version = (
        deployment.get("manifest_version") if isinstance(deployment, dict) else None
    )
    if (not isinstance(deployment, dict) or
            isinstance(manifest_version, bool) or
            not isinstance(manifest_version, int) or
            manifest_version != 1 or
            deployment.get("mode") != "data-first" or
            not isinstance(deployment.get("flags"), dict) or
            not isinstance(deployment["flags"].get("manual"), bool)):
        raise EvidenceError(
            "dataset releases require a valid data-first deployment manifest"
        )
    manual = deployment["flags"]["manual"]
    expected_authority = "manual-caller" if manual else "gate2-state"
    if release["rights_authority"] != expected_authority:
        raise EvidenceError(
            "dataset release rights_authority disagrees with the deployment mode: "
            f"expected {expected_authority}"
        )
    _, state_path = project_path(
        root, "process_log/pipeline_state.json", must_exist=False
    )
    if manual:
        if state_path.exists():
            raise EvidenceError(
                "manual dataset releases may not invent process_log/pipeline_state.json"
            )
        _, rights_snapshot = load_json_snapshot(root, release["rights_inventory"])
        if rights_snapshot["sha256"] != release["rights_inventory_sha256"]:
            raise EvidenceError(
                "manual caller's rights inventory differs from the accepted plan digest"
            )
        return
    state, _ = load_json_snapshot(root, "process_log/pipeline_state.json")
    if not isinstance(state, dict):
        raise EvidenceError("pipeline state must be a JSON object for a dataset release")
    path_value = state.get("dataset_rights_inventory")
    if not isinstance(path_value, str) or not path_value:
        raise EvidenceError("pipeline state has no Gate-2-accepted rights inventory")
    accepted_path, _ = project_path(root, path_value)
    if accepted_path != release["rights_inventory"]:
        raise EvidenceError(
            "release rights inventory differs from the Gate-2-accepted state pointer"
        )
    expected_digest = state.get("dataset_rights_inventory_sha256")
    if (not isinstance(expected_digest, str) or
            re.fullmatch(r"sha256:[0-9a-f]{64}", expected_digest) is None):
        raise EvidenceError("pipeline state has no valid Gate-2 rights-inventory digest")
    _, rights_snapshot = load_json_snapshot(root, accepted_path)
    if rights_snapshot["sha256"] != expected_digest:
        raise EvidenceError("Gate-2-accepted rights inventory bytes have changed")
    if release["rights_inventory_sha256"] != expected_digest:
        raise EvidenceError(
            "release rights-inventory digest differs from the Gate-2-accepted state digest"
        )
    state_version = state.get("dataset_spec_version")
    theory_version = state.get("theory_version")
    for label, value in (("dataset_spec_version", state_version),
                         ("theory_version", theory_version)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise EvidenceError(f"pipeline state {label} must be a positive integer")
    if state_version != theory_version or theory_version != release["dataset_version"]:
        raise EvidenceError(
            "release dataset version is not the current Gate-2-accepted theory version"
        )


def _validate_dataset_release_sources(
        plan: dict[str, Any], root: Path,
        *, expected_input_snapshots: list[dict[str, Any]] | None = None,
                                      ) -> tuple[dict[str, str], set[str]]:
    """Validate the accepted rights inventory and every isolated release-build input."""
    release = plan.get("dataset_release")
    if release is None:
        return {}, set()
    rights, rights_snapshot = load_json_snapshot(root, release["rights_inventory"])
    if not isinstance(rights, dict):
        raise EvidenceError("dataset rights inventory must be a JSON object")
    rights_required = {"schema_version", "dataset_version", "sources"}
    _require_keys(rights, rights_required, rights_required, "dataset rights inventory")
    if (isinstance(rights["schema_version"], bool) or
            not isinstance(rights["schema_version"], int) or
            rights["schema_version"] != 1):
        raise EvidenceError("dataset rights inventory schema_version must be 1")
    if (isinstance(rights["dataset_version"], bool) or
            not isinstance(rights["dataset_version"], int) or
            rights["dataset_version"] != release["dataset_version"]):
        raise EvidenceError("dataset rights inventory version differs from the release plan")
    if not isinstance(rights["sources"], list) or not rights["sources"]:
        raise EvidenceError("dataset rights inventory.sources must be a non-empty array")
    classifications: dict[str, str] = {}
    for index, source in enumerate(rights["sources"]):
        where = f"dataset rights inventory.sources[{index}]"
        if not isinstance(source, dict):
            raise EvidenceError(f"{where} must be an object")
        required = {"source_id", "redistribution", "evidence"}
        _require_keys(source, required, required, where)
        source_id = source["source_id"]
        if not isinstance(source_id, str) or SOURCE_ID_RE.fullmatch(source_id) is None:
            raise EvidenceError(f"{where}.source_id is invalid")
        if source_id in classifications:
            raise EvidenceError(f"duplicate dataset source_id: {source_id}")
        classification = source["redistribution"]
        if classification not in {"open", "restricted"}:
            raise EvidenceError(f"{where}.redistribution must be open or restricted")
        evidence = source["evidence"]
        if not isinstance(evidence, dict):
            raise EvidenceError(f"{where}.evidence must be an object")
        evidence_required = {"url", "terms", "checked_at"}
        _require_keys(evidence, evidence_required, evidence_required, f"{where}.evidence")
        for key in sorted(evidence_required):
            if not isinstance(evidence[key], str) or not evidence[key].strip():
                raise EvidenceError(f"{where}.evidence.{key} must be non-empty")
        classifications[source_id] = classification

    if rights_snapshot["sha256"] != release["rights_inventory_sha256"]:
        raise EvidenceError("dataset rights inventory differs from its release-plan digest")

    provenance, provenance_snapshot = load_json_snapshot(
        root, release["input_provenance"]
    )
    if expected_input_snapshots is not None:
        expected_by_path = {
            item.get("path"): item for item in expected_input_snapshots
            if isinstance(item, dict)
        }
        for label, snapshot in (("rights inventory", rights_snapshot),
                                ("input provenance", provenance_snapshot)):
            if expected_by_path.get(snapshot["path"]) != snapshot:
                raise EvidenceError(
                    f"dataset {label} parsed bytes differ from producer input snapshot"
                )
    if not isinstance(provenance, dict):
        raise EvidenceError("dataset input provenance must be a JSON object")
    provenance_required = {
        "schema_version", "dataset_version", "rights_inventory", "inputs",
    }
    _require_keys(
        provenance, provenance_required, provenance_required, "dataset input provenance"
    )
    if (isinstance(provenance["schema_version"], bool) or
            not isinstance(provenance["schema_version"], int) or
            provenance["schema_version"] != 1):
        raise EvidenceError("dataset input provenance schema_version must be 1")
    if (isinstance(provenance["dataset_version"], bool) or
            not isinstance(provenance["dataset_version"], int) or
            provenance["dataset_version"] != release["dataset_version"]):
        raise EvidenceError("dataset input provenance version differs from the release plan")
    normalized_rights, _ = project_path(root, provenance["rights_inventory"])
    if normalized_rights != release["rights_inventory"]:
        raise EvidenceError(
            "dataset input provenance names a different rights inventory"
        )
    if not isinstance(provenance["inputs"], list) or not provenance["inputs"]:
        raise EvidenceError("dataset input provenance.inputs must be a non-empty array")
    mapped_paths: set[str] = set()
    mapped_roles: dict[str, str] = {}
    used_open_sources: set[str] = set()
    for index, item in enumerate(provenance["inputs"]):
        where = f"dataset input provenance.inputs[{index}]"
        if not isinstance(item, dict):
            raise EvidenceError(f"{where} must be an object")
        required = {"path", "role", "source_ids"}
        _require_keys(item, required, required, where)
        normalized, _ = project_path(root, item["path"])
        if normalized in mapped_paths:
            raise EvidenceError(f"duplicate dataset release input mapping: {normalized}")
        mapped_paths.add(normalized)
        role = item["role"]
        if role not in {"data", "control"}:
            raise EvidenceError(f"{where}.role must be data or control")
        if role == "control" and normalized != release["analysis_receipt"]:
            raise EvidenceError(
                f"{where} only the paired analysis receipt may be a control input"
            )
        if (normalized != release["analysis_receipt"] and
                PurePosixPath(normalized).suffix.casefold() in CODE_INPUT_SUFFIXES):
            raise EvidenceError(
                f"dataset release code-shaped input must be declared as producer code: "
                f"{normalized}"
            )
        source_ids = _string_list(item["source_ids"], f"{where}.source_ids",
                                  nonempty=(role == "data"))
        if len(source_ids) != len(set(source_ids)):
            raise EvidenceError(f"{where}.source_ids contains duplicates")
        unknown = sorted(set(source_ids) - classifications.keys())
        if unknown:
            raise EvidenceError(f"{where} names unknown source ids: {', '.join(unknown)}")
        if role == "control" and source_ids:
            raise EvidenceError(f"{where} control inputs may not name data sources")
        mapped_roles[normalized] = role
        restricted = sorted(
            source_id for source_id in source_ids
            if classifications[source_id] != "open"
        )
        if restricted:
            raise EvidenceError(
                f"dataset release input {normalized} is restricted: {', '.join(restricted)}"
            )
        used_open_sources.update(source_ids)
    expected_mapped = set(plan["producer_inputs"]) - {
        release["rights_inventory"], release["input_provenance"],
    }
    if mapped_paths != expected_mapped:
        missing = sorted(expected_mapped - mapped_paths)
        extra = sorted(mapped_paths - expected_mapped)
        raise EvidenceError(
            "dataset input provenance must classify every non-manifest producer input "
            f"exactly once (missing={missing}, extra={extra})"
        )
    if not used_open_sources:
        raise EvidenceError("dataset release build has no rights-cleared data input")
    if mapped_roles.get(release["analysis_receipt"]) != "control":
        raise EvidenceError(
            "dataset release analysis_receipt must be classified as a control input"
        )
    return classifications, used_open_sources


def _validate_staged_dataset_release(plan: dict[str, Any], workspace: Path,
                                     classifications: dict[str, str],
                                     used_open_sources: set[str],
                                     producer_code_snapshots: list[dict[str, Any]] | None = None,
                                     producer_entrypoint: str | None = None,
                                     ) -> None:
    """Fail before publication unless every release byte has checked provenance."""
    release = plan.get("dataset_release")
    if release is None:
        return
    _, artifact = project_path(workspace, release["artifact"])
    if not artifact.is_dir() or artifact.is_symlink():
        raise EvidenceError("dataset release artifact must be a real directory")
    _, manifest_path = project_path(workspace, release["manifest"])
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise EvidenceError("dataset release manifest must be a JSON object")
    required = {
        "schema_version", "dataset_version", "producing_receipt",
        "analysis_receipt", "rights_inventory", "rights_inventory_sha256",
        "input_provenance", "rights_authority", "files",
        "build_sources", "build_entrypoints", "schema_document",
    }
    _require_keys(manifest, required, required, "dataset release manifest")
    if (isinstance(manifest["schema_version"], bool) or
            not isinstance(manifest["schema_version"], int) or
            manifest["schema_version"] != 1):
        raise EvidenceError("dataset release manifest schema_version must be 1")
    if (isinstance(manifest["dataset_version"], bool) or
            not isinstance(manifest["dataset_version"], int) or
            manifest["dataset_version"] != release["dataset_version"]):
        raise EvidenceError("dataset release manifest version differs from the release plan")
    if manifest["rights_authority"] != release["rights_authority"]:
        raise EvidenceError(
            "dataset release manifest rights_authority differs from the release plan"
        )
    for key in ("analysis_receipt", "producing_receipt", "rights_inventory",
                "rights_inventory_sha256", "input_provenance"):
        if manifest[key] != release[key]:
            raise EvidenceError(f"dataset release manifest.{key} differs from the release plan")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise EvidenceError("dataset release manifest.files must be a non-empty array")
    declared: dict[str, dict[str, Any]] = {}
    declared_casefold: dict[str, str] = {}
    data_files = 0
    for index, item in enumerate(files):
        where = f"dataset release manifest.files[{index}]"
        if not isinstance(item, dict):
            raise EvidenceError(f"{where} must be an object")
        item_required = {"path", "kind", "sha256", "source_ids"}
        _require_keys(item, item_required, item_required, where)
        raw = _release_relative_path(item["path"], f"{where}.path")
        folded = raw.casefold()
        if folded == "manifest.json":
            raise EvidenceError("dataset release manifest may not checksum itself")
        if raw in declared:
            raise EvidenceError(f"duplicate dataset release file: {raw}")
        if folded in declared_casefold:
            raise EvidenceError(
                "case-fold-colliding dataset release files: "
                f"{declared_casefold[folded]} / {raw}"
            )
        kind = item["kind"]
        if kind not in RELEASE_FILE_KINDS:
            raise EvidenceError(f"{where}.kind is invalid")
        digest = item["sha256"]
        if (not isinstance(digest, str) or
                re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None):
            raise EvidenceError(f"{where}.sha256 is invalid")
        source_ids = _string_list(item["source_ids"], f"{where}.source_ids",
                                  nonempty=(kind == "data"))
        if len(source_ids) != len(set(source_ids)):
            raise EvidenceError(f"{where}.source_ids contains duplicates")
        if kind != "data" and source_ids:
            raise EvidenceError(f"{where} non-data files may not name data sources")
        if kind == "data":
            data_files += 1
            unknown = sorted(set(source_ids) - classifications.keys())
            if unknown:
                raise EvidenceError(f"{where} names unknown source ids: {', '.join(unknown)}")
            restricted = sorted(
                source_id for source_id in source_ids
                if classifications[source_id] != "open"
            )
            if restricted:
                raise EvidenceError(
                    f"dataset release file {raw} names restricted sources: "
                    + ", ".join(restricted)
                )
            undeclared = sorted(set(source_ids) - used_open_sources)
            if undeclared:
                raise EvidenceError(
                    f"dataset release file {raw} names sources absent from release inputs: "
                    + ", ".join(undeclared)
                )
        declared[raw] = item
        declared_casefold[folded] = raw
    if data_files == 0:
        raise EvidenceError("dataset release must contain at least one rights-cleared data file")
    actual: dict[str, str] = {}
    for relative, _, info, digest in walk_directory(artifact, hash_files=True):
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode) or digest is None:
            raise EvidenceError(f"special file inside dataset release: {relative}")
        if relative != "manifest.json":
            actual[relative] = digest
    if set(actual) != set(declared):
        missing = sorted(set(actual) - set(declared))
        absent = sorted(set(declared) - set(actual))
        raise EvidenceError(
            "dataset release manifest must enumerate every file exactly once "
            f"(unlisted={missing}, absent={absent})"
        )
    for raw, digest in actual.items():
        if declared[raw]["sha256"] != digest:
            raise EvidenceError(f"dataset release checksum mismatch: {raw}")
    entrypoints = _string_list(
        manifest["build_entrypoints"], "dataset release manifest.build_entrypoints",
        nonempty=True,
    )
    if len(entrypoints) != len(set(entrypoints)):
        raise EvidenceError("dataset release build_entrypoints contains duplicates")
    if len(entrypoints) != len({raw.casefold() for raw in entrypoints}):
        raise EvidenceError(
            "dataset release build_entrypoints contains case-fold collisions"
        )
    for index, raw in enumerate(entrypoints):
        normalized = _release_relative_path(
            raw, f"dataset release manifest.build_entrypoints[{index}]"
        )
        if normalized not in declared or declared[normalized]["kind"] != "code":
            raise EvidenceError(
                f"dataset release build entrypoint is not a declared code file: {normalized}"
            )
    if producer_code_snapshots is None:
        producer_code_snapshots = fingerprint_many(workspace, plan["producer_code"])
    if (not isinstance(producer_code_snapshots, list) or
            any(not isinstance(item, dict) for item in producer_code_snapshots)):
        raise EvidenceError("dataset release producer code snapshots are malformed")
    source_records = {
        item.get("path"): item for item in producer_code_snapshots
        if item.get("kind") == "file" and isinstance(item.get("path"), str)
    }
    if set(source_records) != set(plan["producer_code"]):
        raise EvidenceError(
            "dataset release producer code snapshots do not cover the run plan"
        )
    build_sources = manifest["build_sources"]
    if not isinstance(build_sources, dict) or set(build_sources) != set(source_records):
        raise EvidenceError(
            "dataset release build_sources must map every producer code file exactly once"
        )
    mapped_build_paths: list[str] = []
    for source_raw in plan["producer_code"]:
        mapped_raw = _release_relative_path(
            build_sources[source_raw],
            f"dataset release manifest.build_sources[{source_raw!r}]",
        )
        if mapped_raw != source_raw:
            raise EvidenceError(
                "dataset release build_sources must preserve producer code paths: "
                f"{source_raw} -> {mapped_raw}"
            )
        if mapped_raw not in declared or declared[mapped_raw]["kind"] != "code":
            raise EvidenceError(
                "dataset release build source does not name a declared code file: "
                + mapped_raw
            )
        if actual[mapped_raw] != source_records[source_raw].get("sha256"):
            raise EvidenceError(
                "dataset release build source is not byte-identical to producer code: "
                f"{source_raw} -> {mapped_raw}"
            )
        mapped_build_paths.append(mapped_raw)
    if (len(mapped_build_paths) != len(set(mapped_build_paths)) or
            len(mapped_build_paths) != len({raw.casefold() for raw in mapped_build_paths})):
        raise EvidenceError("dataset release build_sources targets must be unique")
    declared_code = {
        raw for raw, record in declared.items() if record["kind"] == "code"
    }
    if set(mapped_build_paths) != declared_code:
        raise EvidenceError(
            "dataset release declared code files must exactly equal the packaged build closure"
        )
    if producer_entrypoint not in build_sources:
        raise EvidenceError(
            "dataset release producer command entrypoint is absent from build_sources"
        )
    if build_sources[producer_entrypoint] not in entrypoints:
        raise EvidenceError(
            "dataset release build_entrypoints must include the mapped producer command "
            "entrypoint"
        )
    schema_document = _release_relative_path(
        manifest["schema_document"], "dataset release manifest.schema_document"
    )
    if (schema_document not in declared or
            declared[schema_document]["kind"] != "documentation"):
        raise EvidenceError(
            "dataset release schema_document must name a declared documentation file"
        )


def _remove_entry_at(parent_fd: int, name: str) -> None:
    """Remove one entry beneath an already anchored directory without following links."""
    try:
        info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISDIR(info.st_mode):
        os.unlink(name, dir_fd=parent_fd)
        return
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    child_fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        opened = os.fstat(child_fd)
        if ((opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)):
            raise EvidenceError("directory changed during secure removal")
        for child in os.listdir(child_fd):
            _remove_entry_at(child_fd, child)
    finally:
        os.close(child_fd)
    os.rmdir(name, dir_fd=parent_fd)


def _copy_evidence_path(source: Path, destination: Path, *, source_fd: int | None = None,
                        destination_parent_fd: int | None = None,
                        destination_name: str | None = None) -> None:
    """Durably copy evidence with reflinks and depth-bounded descriptor use."""
    source_root_fd = os.dup(source_fd) if source_fd is not None else _open_entry_read(source)
    destination_root_parent_fd = (
        os.dup(destination_parent_fd)
        if destination_parent_fd is not None
        else _open_directory_path(destination.parent)
    )
    source_info = os.fstat(source_root_fd)
    target_name = destination_name if destination_name is not None else destination.name
    if (not target_name or target_name in {".", ".."} or "/" in target_name
            or "\\" in target_name):
        os.close(source_root_fd)
        os.close(destination_root_parent_fd)
        raise EvidenceError("copy destination must be one directory entry")
    try:
        if stat.S_ISREG(source_info.st_mode):
            if source_info.st_nlink != 1:
                raise EvidenceError(f"source is not one non-aliased regular file: {source}")
            destination_fd: int | None = None
            try:
                destination_fd = os.open(
                    target_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                    getattr(os, "O_NOFOLLOW", 0),
                    0o600, dir_fd=destination_root_parent_fd,
                )
                try:
                    fcntl.ioctl(destination_fd, 0x40049409, source_root_fd)
                except OSError:
                    os.ftruncate(destination_fd, 0)
                    os.lseek(source_root_fd, 0, os.SEEK_SET)
                    while True:
                        chunk = os.read(source_root_fd, 1024 * 1024)
                        if not chunk:
                            break
                        view = memoryview(chunk)
                        while view:
                            written = os.write(destination_fd, view)
                            if written <= 0:
                                raise EvidenceError("short write while copying declared evidence")
                            view = view[written:]
                os.fchmod(destination_fd, stat.S_IMODE(source_info.st_mode))
                os.fsync(destination_fd)
            finally:
                if destination_fd is not None:
                    os.close(destination_fd)
            os.fsync(destination_root_parent_fd)
            return
        if not stat.S_ISDIR(source_info.st_mode):
            raise EvidenceError(
                f"expected one non-aliased regular file or real directory: {source}"
            )

        source_flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
                        getattr(os, "O_NOFOLLOW", 0))
        os.mkdir(target_name, 0o700, dir_fd=destination_root_parent_fd)
        destination_root_fd = os.open(
            target_name, source_flags, dir_fd=destination_root_parent_fd
        )
        try:
            root_names = sorted(os.listdir(source_root_fd))
        except BaseException:
            os.close(destination_root_fd)
            raise
        stack: list[tuple[int, int, PurePosixPath, list[str], int, int]] = [
            (source_root_fd, destination_root_fd, PurePosixPath(),
             root_names, 0, stat.S_IMODE(source_info.st_mode) | stat.S_IRWXU)
        ]
        source_root_fd = -1
        try:
            while stack:
                current_source_fd, current_destination_fd, prefix, names, index, directory_mode = stack[-1]
                if index >= len(names):
                    os.fchmod(current_destination_fd, directory_mode)
                    os.fsync(current_destination_fd)
                    os.close(current_source_fd)
                    os.close(current_destination_fd)
                    stack.pop()
                    continue
                name = names[index]
                stack[-1] = (
                    current_source_fd, current_destination_fd, prefix, names,
                    index + 1, directory_mode,
                )
                _validate_descendant_name(name, source / prefix)
                relative = prefix / name
                if _forbidden_part(name):
                    raise EvidenceError(
                        "credential-bearing descendant may not enter result provenance: "
                        f"{source / relative}"
                    )
                info = os.stat(name, dir_fd=current_source_fd, follow_symlinks=False)
                if stat.S_ISDIR(info.st_mode):
                    child_source_fd = os.open(name, source_flags, dir_fd=current_source_fd)
                    opened = os.fstat(child_source_fd)
                    if ((opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)):
                        os.close(child_source_fd)
                        raise EvidenceError(f"directory changed while copying {source / relative}")
                    os.mkdir(name, 0o700, dir_fd=current_destination_fd)
                    child_destination_fd = os.open(
                        name, source_flags, dir_fd=current_destination_fd
                    )
                    try:
                        child_names = sorted(os.listdir(child_source_fd))
                    except BaseException:
                        os.close(child_source_fd)
                        os.close(child_destination_fd)
                        raise
                    stack.append((
                        child_source_fd, child_destination_fd, relative, child_names, 0,
                        stat.S_IMODE(opened.st_mode) | stat.S_IRWXU,
                    ))
                    continue
                if not stat.S_ISREG(info.st_mode):
                    raise EvidenceError(f"unsupported entry while copying evidence: {source / relative}")
                child_source_fd = os.open(
                    name, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=current_source_fd,
                )
                child_destination_fd: int | None = None
                try:
                    opened = os.fstat(child_source_fd)
                    if ((opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)
                            or opened.st_nlink != 1):
                        raise EvidenceError(
                            f"file changed or is aliased while copying {source / relative}"
                        )
                    child_destination_fd = os.open(
                        name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                        getattr(os, "O_NOFOLLOW", 0), 0o600,
                        dir_fd=current_destination_fd,
                    )
                    try:
                        fcntl.ioctl(child_destination_fd, 0x40049409, child_source_fd)
                    except OSError:
                        while True:
                            chunk = os.read(child_source_fd, 1024 * 1024)
                            if not chunk:
                                break
                            view = memoryview(chunk)
                            while view:
                                written = os.write(child_destination_fd, view)
                                if written <= 0:
                                    raise EvidenceError("short write while copying declared evidence")
                                view = view[written:]
                    os.fchmod(child_destination_fd, stat.S_IMODE(opened.st_mode))
                    os.fsync(child_destination_fd)
                finally:
                    if child_destination_fd is not None:
                        os.close(child_destination_fd)
                    os.close(child_source_fd)
        except BaseException:
            for current_source_fd, current_destination_fd, *_ in stack:
                os.close(current_source_fd)
                os.close(current_destination_fd)
            raise
        os.fsync(destination_root_parent_fd)
    except BaseException:
        try:
            _remove_entry_at(destination_root_parent_fd, target_name)
        except (EvidenceError, OSError):
            pass
        raise
    finally:
        if source_root_fd >= 0:
            os.close(source_root_fd)
        os.close(destination_root_parent_fd)


def _open_relative_parent(root: Path, normalized: str, *, create: bool,
                          repair_non_directories: bool = False) -> tuple[int, str]:
    """Anchor a lexical project-relative parent through no-follow descriptors."""
    parts = PurePosixPath(normalized).parts
    descriptor = _open_directory_path(root)
    flags = (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
             getattr(os, "O_NOFOLLOW", 0))
    try:
        for part in parts[:-1]:
            try:
                expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                if not create:
                    raise EvidenceError(f"project directory does not exist: {normalized}")
                os.mkdir(part, 0o755, dir_fd=descriptor)
                os.fsync(descriptor)
                expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(expected.st_mode):
                if not repair_non_directories:
                    raise EvidenceError(
                        f"project path ancestor is not a directory: {normalized}"
                    )
                _remove_entry_at(descriptor, part)
                os.mkdir(part, 0o755, dir_fd=descriptor)
                os.fsync(descriptor)
                expected = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
            child = os.open(part, flags, dir_fd=descriptor)
            opened = os.fstat(child)
            if ((opened.st_dev, opened.st_ino) !=
                    (expected.st_dev, expected.st_ino)):
                os.close(child)
                raise EvidenceError(f"project path ancestor changed: {normalized}")
            os.close(descriptor)
            descriptor = child
        return descriptor, parts[-1]
    except BaseException:
        os.close(descriptor)
        raise


def _open_project_parent(root: Path, raw: str, *, create: bool) -> tuple[int, str]:
    """Validate a project path, then anchor its parent without following links."""
    normalized, _ = project_path(root, raw, must_exist=False)
    return _open_relative_parent(root, normalized, create=create)


def _remove_project_path(root: Path, raw: str) -> None:
    """Remove one validated project-relative entry through an anchored parent."""
    normalized, _ = project_path(root, raw, must_exist=False)
    try:
        parent_fd, name = _open_relative_parent(root, normalized, create=False)
    except EvidenceError as exc:
        if "does not exist" in str(exc):
            return
        raise
    try:
        _remove_entry_at(parent_fd, name)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


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
                       output_paths: Iterable[str], *,
                       read_only_bindings: list[tuple[int, Path, Path]] | None = None
                       ) -> Iterable[Path]:
    """Run untrusted computation in a fresh view containing only declared inputs."""
    global _SOURCE_LEASE_BROKEN
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
    # macOS commonly spells its physical temp tree through `/var`, a symlink
    # to `/private/var`. Canonicalize this trusted freshly-created directory
    # before the no-follow walker anchors every component.
    workspace = Path(tempfile.mkdtemp(prefix="results-workspace-")).resolve(strict=True)
    binding_start = len(read_only_bindings) if read_only_bindings is not None else 0
    bind_declared_sources = (
        read_only_bindings is not None and
        (binding_bubblewrap := trusted_sandbox_executable("bwrap")) is not None and
        bubblewrap_supports_read_only_fd_bind(binding_bubblewrap)
    )
    previous_sigio: Any = None
    lease_handler_installed = False
    if bind_declared_sources:
        try:
            previous_sigio = signal.getsignal(signal.SIGIO)
            signal.signal(signal.SIGIO, _mark_source_lease_broken)
        except (AttributeError, ValueError):
            bind_declared_sources = False
        else:
            _SOURCE_LEASE_BROKEN = False
            lease_handler_installed = True
    with workspace_cleanup_guard(workspace):
        try:
            canonical_root = root.resolve(strict=True)
            try:
                workspace.relative_to(canonical_root)
            except ValueError:
                pass
            else:
                raise EvidenceError(
                    "isolated workspace temp root must be outside the project"
                )
            try:
                canonical_root.relative_to(workspace)
            except ValueError:
                pass
            else:
                raise EvidenceError(
                    "isolated workspace temp root must not contain the project"
                )
            for raw in normalized_sources:
                _, source = project_path(root, raw)
                destination = workspace.joinpath(*PurePosixPath(raw).parts)
                source_descriptor = _open_entry_read(source)
                destination_parent_descriptor, destination_name = _open_project_parent(
                    workspace, raw, create=True
                )
                try:
                    use_binding = False
                    if (bind_declared_sources and
                            stat.S_ISREG(os.fstat(source_descriptor).st_mode)):
                        source_info = os.fstat(source_descriptor)
                        if source_info.st_nlink != 1:
                            raise EvidenceError(
                                f"source is not one non-aliased regular file: {source}"
                            )
                        try:
                            fcntl.fcntl(source_descriptor, fcntl.F_SETOWN, os.getpid())
                            fcntl.fcntl(
                                source_descriptor, fcntl.F_SETLEASE, fcntl.F_RDLCK
                            )
                        except (AttributeError, OSError):
                            # A live writer, unsupported filesystem, or unavailable
                            # lease means zero-copy cannot preserve snapshot semantics.
                            use_binding = False
                        else:
                            use_binding = True
                    if use_binding:
                        mount_descriptor = os.open(
                            destination_name,
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                            getattr(os, "O_NOFOLLOW", 0),
                            0o600, dir_fd=destination_parent_descriptor,
                        )
                        os.close(mount_descriptor)
                        assert read_only_bindings is not None
                        read_only_bindings.append(
                            (source_descriptor, source, destination)
                        )
                        source_descriptor = -1
                    else:
                        _copy_evidence_path(
                            source, destination, source_fd=source_descriptor,
                            destination_parent_fd=destination_parent_descriptor,
                            destination_name=destination_name,
                        )
                finally:
                    os.close(destination_parent_descriptor)
                    if source_descriptor >= 0:
                        os.close(source_descriptor)
            for raw in dict.fromkeys(output_paths):
                normalized, destination = project_path(workspace, raw, must_exist=False)
                if destination.exists() or destination.is_symlink():
                    raise EvidenceError(f"isolated output overlaps a source: {normalized}")
                destination.parent.mkdir(parents=True, exist_ok=True)
            yield workspace
        finally:
            try:
                remove_abandoned_workspace(workspace)
            finally:
                if read_only_bindings is not None:
                    for descriptor, _, _ in read_only_bindings[binding_start:]:
                        try:
                            fcntl.fcntl(descriptor, fcntl.F_SETLEASE, fcntl.F_UNLCK)
                        except OSError:
                            pass
                        os.close(descriptor)
                    del read_only_bindings[binding_start:]
                if lease_handler_installed:
                    signal.signal(signal.SIGIO, previous_sigio)
                    _SOURCE_LEASE_BROKEN = False


def publish_workspace_path(root: Path, workspace: Path, raw: str) -> None:
    """Copy one isolated output beside its final target, then publish atomically."""
    normalized, source = project_path(workspace, raw)
    source_descriptor = _open_entry_read(source)
    parent_descriptor, destination_name = _open_project_parent(
        root, normalized, create=True
    )
    staged_name = f".{destination_name}.publish.{secrets.token_hex(16)}"
    try:
        try:
            os.stat(destination_name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise EvidenceError(f"publication target appeared during isolated run: {normalized}")
        _copy_evidence_path(
            source, Path(staged_name), source_fd=source_descriptor,
            destination_parent_fd=parent_descriptor, destination_name=staged_name,
        )
        try:
            os.stat(destination_name, dir_fd=parent_descriptor, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise EvidenceError(f"publication target changed before commit: {normalized}")
        os.replace(
            staged_name, destination_name,
            src_dir_fd=parent_descriptor, dst_dir_fd=parent_descriptor,
        )
        os.fsync(parent_descriptor)
    finally:
        try:
            _remove_entry_at(parent_descriptor, staged_name)
        except (EvidenceError, OSError):
            pass
        os.close(parent_descriptor)
        os.close(source_descriptor)


def _safe_restore_destination(root: Path, destination: Path) -> tuple[int, str]:
    """Prepare and anchor a restore destination without following hostile links."""
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise EvidenceError(f"restore target escapes project root: {destination}") from exc
    if not relative.parts:
        raise EvidenceError("refusing to restore over the project root")
    parent_fd, name = _open_relative_parent(
        root, relative.as_posix(), create=True, repair_non_directories=True
    )
    try:
        _remove_entry_at(parent_fd, name)
        os.fsync(parent_fd)
        return parent_fd, name
    except BaseException:
        os.close(parent_fd)
        raise


def _restore_target(root: Path, raw: str) -> tuple[str, Path]:
    """Resolve a journal path lexically so recovery can remove hostile symlinks."""
    if not isinstance(raw, str) or not raw:
        raise EvidenceError("transaction paths must be non-empty strings")
    posix = PurePosixPath(raw.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise EvidenceError(f"invalid path in results transaction journal: {raw!r}")
    if any(_forbidden_part(part) for part in posix.parts):
        raise EvidenceError(f"credential path in results transaction journal: {raw!r}")
    normalized = posix.as_posix()
    return normalized, root.joinpath(*posix.parts)


def _validate_transaction_evidence_path(root: Path, raw: str) -> tuple[str, Path]:
    """Restrict crash recovery to result-owned output paths.

    The journal lives in the project and is therefore not an authentication
    boundary.  Even a structurally valid forged journal must never authorize
    deletion or restoration of paper, code, data, or process-control files.
    """
    normalized, path = _restore_target(root, raw)
    if not normalized.startswith("output/") or normalized == AUDIT_NAMESPACE or \
            normalized.startswith(AUDIT_NAMESPACE + "/"):
        raise EvidenceError(
            "results transaction path is outside the result-owned output namespace: "
            f"{normalized}"
        )
    return normalized, path


def _restore_evidence_path(root: Path, source: Path, destination: Path) -> None:
    parent_fd, name = _safe_restore_destination(root, destination)
    source_fd = _open_entry_read(source)
    try:
        _copy_evidence_path(
            source, destination, source_fd=source_fd,
            destination_parent_fd=parent_fd, destination_name=name,
        )
    finally:
        os.close(source_fd)
        os.close(parent_fd)


def _clear_transaction_files(root: Path) -> None:
    _remove_project_path(root, TRANSACTION_BACKUP_PATH)
    _remove_project_path(root, TRANSACTION_PATH)


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
            not isinstance(value["phase"], str) or
            value["phase"] not in {"preparing", "prepared", "committed", "rolled_back"}):
        raise EvidenceError("unsupported results transaction journal; operator recovery required")
    if not isinstance(value["cleanup_paths"], list) or not isinstance(value["backups"], list):
        raise EvidenceError("malformed results transaction journal; operator recovery required")
    for raw in value["cleanup_paths"]:
        _validate_transaction_evidence_path(root, raw)
    backup_names: list[str] = []
    for item in value["backups"]:
        if (not isinstance(item, dict) or set(item) != {"path", "backup"} or
                not isinstance(item["path"], str) or
                not isinstance(item["backup"], str) or
                not re.fullmatch(r"[0-9]+", item["backup"])):
            raise EvidenceError("malformed results transaction journal; operator recovery required")
        _validate_transaction_evidence_path(root, item["path"])
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
        normalized, destination = _validate_transaction_evidence_path(root, raw)
        parent_fd, name = _safe_restore_destination(root, destination)
        try:
            try:
                os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise EvidenceError(f"failed to remove interrupted output: {normalized}")
        finally:
            os.close(parent_fd)
    for item in value["backups"]:
        if (not isinstance(item, dict) or not isinstance(item.get("path"), str) or
                not isinstance(item.get("backup"), str) or
                not re.fullmatch(r"[0-9]+", item["backup"])):
            raise EvidenceError("malformed path in results transaction journal")
        _, destination = _validate_transaction_evidence_path(root, item["path"])
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
        ensure_directory_durable(backup_root)
        os.chmod(backup_root, 0o700)
        fsync_directory(backup_root)
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
                           publish: bool = True,
                           finalize_while_sources_pinned: (
                               Callable[[dict[str, Any]], None] | None
                           ) = None) -> tuple[list[str], dict[str, Any]]:
    paths: list[tuple[str, Path]] = []
    live_exhibit_snapshots: list[dict[str, Any]] = []
    for exhibit in bundle["exhibits"]:
        raw, path = project_path(root, exhibit["path"], must_exist=False)
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise EvidenceError(f"exhibit target must be a regular file: {raw}")
            live_exhibit_snapshots.append(fingerprint(root, raw))
        paths.append((raw, path))
    artifact_paths = bundle["renderer"].get(
        "inputs", [entry["path"] for entry in bundle["artifacts"]]
    )
    sources = [bundle_path, *artifact_paths, *bundle["renderer"]["code"]]
    source_snapshots = fingerprint_many(root, sources)
    environment_capture = capture_execution_environment(root, command)
    read_only_bindings: list[tuple[int, Path, Path]] = []
    with isolated_workspace(
            root, sources, [], read_only_bindings=read_only_bindings) as workspace:
        stage = workspace / ".results-exhibits"
        stage.mkdir()
        execute(
            command, workspace, bundle_path=bundle_path,
            extra_environment={"RESULTS_EXHIBIT_ROOT": str(stage)},
            project_root=root,
            allow_network=False,
            provider_credentials=set(),
            read_only_bindings=read_only_bindings,
        )
        require_stable_environment(
            environment_capture, capture_execution_environment(root, command),
            "rendering",
        )
        source_failures = compare_isolated_sources(
            root, workspace, source_snapshots, read_only_bindings,
            "isolated renderer source",
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
                _remove_project_path(root, raw)
                publish_workspace_path(root, stage, raw)
        if finalize_while_sources_pinned is not None:
            finalize_while_sources_pinned(environment_capture)
        # execute() checked immediately after the child exited, but validation
        # and publication above can be substantial. A writer remains blocked by
        # the lease until the workspace exits; reject any break observed during
        # that post-execution interval before the caller commits its transaction.
        require_source_leases_intact(read_only_bindings)
    return [raw for raw, _ in paths], environment_capture


def snapshot_bundle(root: Path, bundle: dict[str, Any], bundle_path: str,
                    command: list[str], plan_path: str,
                    code_snapshot: list[dict[str, Any]],
                    input_snapshot: list[dict[str, Any]],
                    renderer_snapshot: list[dict[str, Any]],
                    environment_capture: dict[str, Any]) -> dict[str, Any]:
    artifacts = [entry["path"] for entry in bundle["artifacts"]]
    return {
        "command": command,
        "plan": fingerprint(root, plan_path),
        "bundle": fingerprint(root, bundle_path),
        "code": code_snapshot,
        "inputs": input_snapshot,
        "renderer_code": renderer_snapshot,
        "artifacts": fingerprint_many(root, artifacts),
        "exhibits": [entry["path"] for entry in bundle["exhibits"]],
        "reproducibility": bundle["producer"]["reproducibility"],
        "environment": environment_capture,
    }


def snapshot_render(root: Path, bundle: dict[str, Any], command: list[str],
                    environment_capture: dict[str, Any]) -> dict[str, Any]:
    exhibit_paths = [entry["path"] for entry in bundle["exhibits"]]
    return {
        "command": command,
        "code": fingerprint_many(root, bundle["renderer"]["code"]),
        "exhibits": fingerprint_many(root, exhibit_paths),
        "environment": environment_capture,
    }


def result_receipt_supersedes(root: Path, receipt_raw: str,
                              receipt: dict[str, Any] | None = None) -> list[str]:
    """Return the immutable replacement relation recorded by one result receipt."""
    if receipt is None:
        receipt = load_registered_result_receipt(root, receipt_raw)
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


def load_registered_result_receipt(root: Path, receipt_raw: str) -> dict[str, Any]:
    """Read exact receipt bytes and bind them to the durable registry fingerprint."""
    registry, _ = load_registry(root)
    expected = registry["receipt_fingerprints"].get(receipt_raw)
    if expected is None:
        raise EvidenceError(f"result receipt is not active or pending: {receipt_raw}")
    receipt, snapshot = load_json_snapshot(root, receipt_raw)
    if snapshot != expected:
        raise EvidenceError(f"registered result receipt bytes are stale: {receipt_raw}")
    if not isinstance(receipt, dict):
        raise EvidenceError(f"malformed result receipt: {receipt_raw}")
    return receipt


def compare_snapshot(root: Path, recorded: list[dict[str, Any]], label: str) -> list[str]:
    failures: list[str] = []
    for expected in recorded:
        if not isinstance(expected, dict):
            failures.append(f"{label}: receipt entry is not a fingerprint object")
            continue
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


def compare_isolated_sources(root: Path, workspace: Path,
                             recorded: list[dict[str, Any]],
                             bindings: list[tuple[int, Path, Path]],
                             label: str) -> list[str]:
    """Verify bound regular files live and copied directory sources in workspace."""
    bound_paths = {
        destination.relative_to(workspace).as_posix()
        for _, _, destination in bindings
    }
    bound = [entry for entry in recorded if entry.get("path") in bound_paths]
    copied = [entry for entry in recorded if entry.get("path") not in bound_paths]
    failures = compare_snapshot(root, bound, label) if bound else []
    if copied:
        failures.extend(compare_snapshot(workspace, copied, label))
    return failures


def validate_snapshot_record(root: Path, value: Any, where: str) -> str:
    if not isinstance(value, dict):
        raise EvidenceError(f"{where} must be a fingerprint object")
    kind = value.get("kind")
    expected = {"path", "kind", "sha256"} | ({"entries"} if kind == "directory" else set())
    if (not isinstance(kind, str) or kind not in {"file", "directory"} or
            set(value) != expected):
        raise EvidenceError(f"{where} has malformed fingerprint keys")
    raw = value.get("path")
    if not isinstance(raw, str):
        raise EvidenceError(f"{where}.path must be a string")
    normalized, _ = project_path(root, raw, must_exist=False)
    if normalized != raw:
        raise EvidenceError(f"{where}.path is not normalized")
    digest = value.get("sha256")
    if (not isinstance(digest, str) or
            re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None):
        raise EvidenceError(f"{where}.sha256 is malformed")
    if kind == "directory":
        entries = value["entries"]
        if not isinstance(entries, list):
            raise EvidenceError(f"{where}.entries must be an array")
        prior = ""
        entry_kinds: dict[str, str] = {}
        for index, entry in enumerate(entries):
            entry_where = f"{where}.entries[{index}]"
            if (not isinstance(entry, dict) or
                    not isinstance(entry.get("kind"), str) or
                    entry.get("kind") not in {"file", "directory"}):
                raise EvidenceError(f"{entry_where} is malformed")
            entry_expected = {"path", "kind"} | (
                {"sha256"} if entry["kind"] == "file" else set()
            )
            if set(entry) != entry_expected:
                raise EvidenceError(f"{entry_where} has malformed keys")
            entry_path = entry.get("path")
            entry_posix = PurePosixPath(entry_path) if isinstance(entry_path, str) else None
            if (entry_posix is None or not entry_path or entry_path == "." or
                    "\\" in entry_path or any(ord(character) < 32 for character in entry_path) or
                    entry_posix.is_absolute() or
                    "." in entry_posix.parts or ".." in entry_posix.parts or
                    entry_posix.as_posix() != entry_path or
                    any(_forbidden_part(part) for part in entry_posix.parts) or
                    entry_path <= prior):
                raise EvidenceError(f"{entry_where}.path is malformed or unsorted")
            for depth in range(1, len(entry_posix.parts)):
                parent = PurePosixPath(*entry_posix.parts[:depth]).as_posix()
                if entry_kinds.get(parent) != "directory":
                    raise EvidenceError(
                        f"{entry_where}.path has a missing or non-directory parent {parent}"
                    )
            prior = entry_path
            entry_kinds[entry_path] = entry["kind"]
            if entry["kind"] == "file" and (
                    not isinstance(entry.get("sha256"), str) or
                    re.fullmatch(r"sha256:[0-9a-f]{64}", entry["sha256"]) is None):
                raise EvidenceError(f"{entry_where}.sha256 is malformed")
        encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
        expected_digest = f"sha256:{hashlib.sha256(encoded).hexdigest()}"
        if digest != expected_digest:
            raise EvidenceError(f"{where}.sha256 does not match its directory entries")
    return raw


def validate_receipt_contract(root: Path, receipt_path: Path) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    version = receipt.get("receipt_version") if isinstance(receipt, dict) else None
    expected_keys = {"kind", "receipt_version", "supersedes", "producer_run", "render_run"}
    if version == EMPIRICAL_RECEIPT_VERSION:
        expected_keys.add("lineage")
    if (not isinstance(receipt, dict) or receipt.get("kind") != "result" or
            isinstance(version, bool) or
            version not in {RECEIPT_VERSION, EMPIRICAL_RECEIPT_VERSION} or
            set(receipt) != expected_keys):
        raise EvidenceError("not a structurally valid results receipt v2/v3")
    if version == EMPIRICAL_RECEIPT_VERSION:
        lineage = receipt["lineage"]
        if not isinstance(lineage, list) or not lineage:
            raise EvidenceError("empirical receipt lineage must be a non-empty array")
        prior = ""
        for index, item in enumerate(lineage):
            where = f"lineage[{index}]"
            if not isinstance(item, dict) or set(item) != {
                    "analysis_id", "baseline_path", "baseline_digest",
                    "contract_path", "contract_digest", "execution_summary_path",
                    "execution_summary_digest", "result_ids"}:
                raise EvidenceError(f"{where} is malformed")
            analysis_id = item["analysis_id"]
            if (not isinstance(analysis_id, str) or
                    RESULT_ID_RE.fullmatch(analysis_id) is None or analysis_id <= prior):
                raise EvidenceError("lineage must have unique sorted analysis IDs")
            prior = analysis_id
            for key in ("baseline_digest", "contract_digest", "execution_summary_digest"):
                if (not isinstance(item[key], str) or
                        re.fullmatch(r"sha256:[0-9a-f]{64}", item[key]) is None):
                    raise EvidenceError(f"{where}.{key} is malformed")
            for key in ("baseline_path", "contract_path", "execution_summary_path"):
                normalized = project_path(root, item[key], must_exist=False)[0]
                if normalized != item[key]:
                    raise EvidenceError(f"{where}.{key} is not normalized")
            _string_list(item["result_ids"], f"{where}.result_ids", nonempty=True)
    receipt_raw = receipt_path.relative_to(root).as_posix()
    result_receipt_supersedes(root, receipt_raw, receipt)
    producer = receipt.get("producer_run")
    producer_keys = {"command", "plan", "bundle", "code", "inputs",
                     "renderer_code", "artifacts", "exhibits", "reproducibility",
                     "environment"}
    if not isinstance(producer, dict) or set(producer) != producer_keys:
        raise EvidenceError("receipt producer_run has unexpected or missing keys")
    command = producer["command"]
    if (not isinstance(command, list) or not command or
            any(not isinstance(item, str) for item in command)):
        raise EvidenceError("producer_run.command is malformed")
    recorded_paths: dict[str, list[str]] = {}
    for key in ("code", "inputs", "renderer_code", "artifacts"):
        values = producer[key]
        if not isinstance(values, list):
            raise EvidenceError(f"producer_run.{key} must be an array")
        recorded_paths[key] = [
            validate_snapshot_record(root, value, f"producer_run.{key}[{index}]")
            for index, value in enumerate(values)
        ]
    exhibits = producer["exhibits"]
    if (not isinstance(exhibits, list) or
            any(not isinstance(value, str) for value in exhibits)):
        raise EvidenceError("producer_run.exhibits must be an array of paths")
    recorded_paths["exhibits"] = []
    for index, value in enumerate(exhibits):
        normalized, _ = project_path(root, value, must_exist=False)
        if not normalized.startswith("output/"):
            raise EvidenceError(f"producer_run.exhibits[{index}] must be under output/")
        reject_audit_namespace(normalized, f"producer_run.exhibits[{index}]")
        recorded_paths["exhibits"].append(normalized)
    if len(recorded_paths["exhibits"]) != len(set(recorded_paths["exhibits"])):
        raise EvidenceError("producer_run.exhibits contains duplicate paths")
    plan_raw = validate_snapshot_record(root, producer["plan"], "producer_run.plan")
    validate_snapshot_record(root, producer["bundle"], "producer_run.bundle")
    for key in ("plan", "bundle"):
        if producer[key].get("kind") != "file":
            raise EvidenceError(f"producer_run.{key} must fingerprint one file")
    _, live_plan_path = project_path(root, plan_raw, must_exist=False)
    if live_plan_path.exists():
        plan = validate_run_plan(
            load_json(live_plan_path), root, require_live_sources=False
        )
        expected_paths = {
            "code": plan["producer_code"], "inputs": plan["producer_inputs"],
            "renderer_code": plan["renderer_code"], "artifacts": plan["artifacts"],
            "exhibits": plan["exhibits"],
        }
        for key, expected in expected_paths.items():
            if recorded_paths[key] != expected:
                raise EvidenceError(f"producer_run.{key} inventory differs from the plan")
    if (not isinstance(producer["reproducibility"], str) or
            producer["reproducibility"] not in {"exact", "bounded", "captured"}):
        raise EvidenceError("producer_run.reproducibility is malformed")
    validate_environment_capture(
        producer["environment"], "producer_run.environment", command
    )
    command_uses_declared_code(command, recorded_paths["code"], "producer")
    render = receipt["render_run"]
    if render is not None:
        if not isinstance(render, dict) or set(render) != {
                "command", "code", "exhibits", "environment"}:
            raise EvidenceError("render_run is malformed")
        render_command = render["command"]
        if (not isinstance(render_command, list) or not render_command or
                any(not isinstance(item, str) for item in render_command)):
            raise EvidenceError("render_run.command is malformed")
        render_code = render["code"]
        render_exhibits = render["exhibits"]
        if not isinstance(render_code, list) or not isinstance(render_exhibits, list):
            raise EvidenceError("render_run snapshot arrays are malformed")
        code_paths = [validate_snapshot_record(root, item, f"render_run.code[{index}]")
                      for index, item in enumerate(render_code)]
        exhibit_paths = [
            validate_snapshot_record(root, item, f"render_run.exhibits[{index}]")
            for index, item in enumerate(render_exhibits)
        ]
        if code_paths != recorded_paths["renderer_code"]:
            raise EvidenceError("render_run code inventory differs from producer_run")
        if len(exhibit_paths) != len(set(exhibit_paths)):
            raise EvidenceError("render_run exhibit inventory contains duplicates")
        if exhibit_paths != recorded_paths["exhibits"]:
            raise EvidenceError("render_run exhibit inventory differs from producer_run")
        validate_environment_capture(
            render["environment"], "render_run.environment", render_command
        )
        command_uses_declared_code(render_command, code_paths, "renderer")
    return receipt


def verify_receipt(root: Path, receipt_path: Path, *, rerender: bool,
                   enforce_current_dataset_authority: bool = True
                   ) -> dict[str, Any]:
    receipt = validate_receipt_contract(root, receipt_path)
    version = receipt["receipt_version"]
    producer = receipt.get("producer_run")
    if not isinstance(producer, dict):
        raise EvidenceError(f"receipt missing producer_run: {receipt_path}")
    producer_keys = {"command", "plan", "bundle", "code", "inputs",
                     "renderer_code", "artifacts", "exhibits", "reproducibility",
                     "environment"}
    if set(producer) != producer_keys:
        raise EvidenceError(f"receipt producer_run has unexpected or missing keys: {receipt_path}")
    producer_command_value = producer.get("command")
    validate_environment_capture(
        producer["environment"], "producer_run.environment",
        producer_command_value if isinstance(producer_command_value, list) else None,
    )
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
                    effective_renderer_inputs(bundle) != plan["renderer_inputs"] or
                    [entry["path"] for entry in bundle["artifacts"]] != plan["artifacts"] or
                    [entry["path"] for entry in bundle["exhibits"]] != plan["exhibits"]):
                failures.append("producer bundle no longer matches its pre-run plan")
            expected_snapshots = {
                "code": plan["producer_code"],
                "inputs": plan["producer_inputs"],
                "renderer_code": plan["renderer_code"],
                "artifacts": plan["artifacts"],
            }
            for key, expected_paths in expected_snapshots.items():
                recorded = producer.get(key)
                recorded_paths = ([entry.get("path") for entry in recorded]
                                  if isinstance(recorded, list) and
                                  all(isinstance(entry, dict) for entry in recorded)
                                  else None)
                if recorded_paths != expected_paths:
                    failures.append(
                        f"producer_run.{key}: path inventory differs from plan/bundle"
                    )
            if producer.get("exhibits") != plan["exhibits"]:
                failures.append(
                    "producer_run.exhibits: path inventory differs from plan/bundle"
                )
            if producer.get("reproducibility") != bundle["producer"]["reproducibility"]:
                failures.append(
                    "producer_run.reproducibility differs from the validated bundle"
                )
            producer_command = producer.get("command")
            if (not isinstance(producer_command, list) or not producer_command or
                    any(not isinstance(item, str) for item in producer_command)):
                failures.append("producer_run.command: malformed receipt field")
                producer_entrypoint = None
            else:
                producer_entrypoint = command_entrypoint(producer_command)
            if version == EMPIRICAL_RECEIPT_VERSION:
                contracts, projections = validate_empirical_plan(root, plan, completed=True)
                registry, _ = load_registry(root)
                validate_empirical_relationships(
                    root, receipt_raw, plan, contracts,
                    eligible_receipts=empirical_operand_eligible_receipts(root, registry),
                )
                derived = validate_empirical_bundle(bundle, contracts, projections)
                if derived != receipt["lineage"]:
                    failures.append("receipt lineage differs from live empirical evidence")
                if ("inputs" not in bundle["renderer"] or
                        bundle["renderer"]["inputs"] != plan["renderer_inputs"]):
                    failures.append("empirical renderer input inventory differs from plan")
            elif "analyses" in plan:
                failures.append("empirical plan is bound to a non-empirical receipt")
            release = plan.get("dataset_release")
            if release is not None:
                if release["producing_receipt"] != receipt_raw:
                    failures.append(
                        "dataset release producing_receipt differs from its receipt path"
                    )
                classifications, used_sources = _validate_dataset_release_sources(
                    plan, root, expected_input_snapshots=producer.get("inputs")
                )
                if enforce_current_dataset_authority:
                    _validate_dataset_rights_authority(plan, root)
                _validate_staged_dataset_release(
                    plan, root, classifications, used_sources,
                    producer_code_snapshots=producer.get("code"),
                    producer_entrypoint=producer_entrypoint,
                )
            if producer_entrypoint is not None:
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
            if set(render) != {"command", "code", "exhibits", "environment"}:
                failures.append("render_run: unexpected or missing receipt keys")
            else:
                try:
                    validate_environment_capture(
                        render["environment"], "render_run.environment",
                        render.get("command") if isinstance(render.get("command"), list) else None,
                    )
                except EvidenceError as exc:
                    failures.append(str(exc))
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
            expected_render_paths = {
                "code": bundle["renderer"]["code"],
                "exhibits": [entry["path"] for entry in bundle["exhibits"]],
            }
            for key, expected_paths in expected_render_paths.items():
                recorded = render.get(key)
                recorded_paths = ([entry.get("path") for entry in recorded]
                                  if isinstance(recorded, list) and
                                  all(isinstance(entry, dict) for entry in recorded)
                                  else None)
                if recorded_paths != expected_paths:
                    failures.append(f"render_run.{key}: path inventory differs from bundle")
    elif render is not None:
        failures.append("render_run must be null when the bundle declares no exhibits")
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
            "active": [], "active_dataset_release_pairs": {},
            "pending": [], "retired": [],
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
    had_active_pairs_field = "active_dataset_release_pairs" in value
    # Registries created before paired releases existed have no active pairs.
    value.setdefault("active_dataset_release_pairs", {})
    _require_keys(value, {"kind", "registry_version", "active",
                          "active_dataset_release_pairs", "pending", "retired",
                          "receipt_fingerprints"},
                  {"kind", "registry_version", "active",
                          "active_dataset_release_pairs", "pending", "retired",
                          "receipt_fingerprints"},
                  "result registry")
    active = _string_list(value["active"], "result registry.active")
    if len(active) != len(set(active)):
        raise EvidenceError("result registry.active contains duplicate receipts")
    active_pairs = value["active_dataset_release_pairs"]
    if not isinstance(active_pairs, dict):
        raise EvidenceError("result registry.active_dataset_release_pairs must be an object")
    active_pair_members: set[str] = set()
    for analysis_raw, release_raw in active_pairs.items():
        analysis, _ = result_receipt_path(root, analysis_raw)
        release, _ = result_receipt_path(root, release_raw)
        if analysis != analysis_raw or release != release_raw:
            raise EvidenceError(
                "result registry.active_dataset_release_pairs paths must be normalized"
            )
        if analysis == release or analysis not in active or release not in active:
            raise EvidenceError(
                "result registry active dataset pair must name two distinct active receipts"
            )
        if analysis in active_pair_members or release in active_pair_members:
            raise EvidenceError("active dataset-release pair members must be unique")
        active_pair_members.update({analysis, release})
    pending = value["pending"]
    if not isinstance(pending, list):
        raise EvidenceError("result registry.pending must be an array")
    pending_paths: list[str] = []
    for index, entry in enumerate(pending):
        where = f"result registry.pending[{index}]"
        if not isinstance(entry, dict):
            raise EvidenceError(f"{where} must be an object")
        _require_keys(
            entry, {"receipt", "supersedes"},
            {"receipt", "supersedes", "paired_analysis_receipt"}, where,
        )
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
        paired_analysis = entry.get("paired_analysis_receipt")
        if paired_analysis is not None:
            paired_normalized, _ = result_receipt_path(root, paired_analysis)
            if paired_normalized != paired_analysis:
                raise EvidenceError(f"{where}.paired_analysis_receipt is not normalized")
            if paired_normalized == normalized:
                raise EvidenceError(f"{where} cannot pair a receipt with itself")
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
    if verify_receipt_bytes:
        derived_active_pairs, _ = derive_registry_dataset_release_pairs(
            root, active, pending, receipt_fingerprints
        )
        if not had_active_pairs_field and derived_active_pairs:
            raise EvidenceError(
                "result registry is missing active dataset-release pair identity"
            )
        if active_pairs != derived_active_pairs:
            raise EvidenceError(
                "result registry active dataset-release pair identity disagrees with receipts"
            )
        _, output = project_path(root, "output")
        receipt_entries = [
            (relative, info) for relative, _, info, _ in walk_directory(output)
            if relative.endswith("results.receipt.json")
        ]
        for relative, info in receipt_entries:
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise EvidenceError(
                    "result receipt-shaped path on disk is not one regular "
                    f"non-aliased file: output/{relative}"
                )
        on_disk_receipts = {
            f"output/{relative}" for relative, _ in receipt_entries
        }
        tracked_receipts = set(active) | set(pending_paths) | set(retired_paths)
        if on_disk_receipts != tracked_receipts:
            raise EvidenceError(
                "result registry must exactly inventory every result receipt on disk "
                f"(untracked={sorted(on_disk_receipts - tracked_receipts)}, "
                f"missing={sorted(tracked_receipts - on_disk_receipts)})"
            )
        enforce_empirical_spec_immutability(root, [], value)
    return value, path


def validate_registration_plan(
        root: Path, receipt_raw: str, supersedes: list[str],
        *, paired_pending_receipt: str | None = None,
        pair_role: str | None = None,
        ) -> tuple[dict[str, Any], Path, list[str]]:
    registry, path = load_registry(root)
    active: list[str] = registry["active"]
    if registry["pending"]:
        pending_paths = [entry["receipt"] for entry in registry["pending"]]
        if paired_pending_receipt is None or pending_paths != [paired_pending_receipt]:
            raise EvidenceError(
                "retire or activate the existing pending result receipt before starting "
                "another run (except its bound dataset-release pair)"
            )
        failures = verify_receipt(root, root / paired_pending_receipt, rerender=True)["failures"]
        if failures:
            raise EvidenceError(
                "paired analysis receipt is not fresh and fully rendered: "
                + "; ".join(failures)
            )
        paired_plan = result_receipt_run_plan(root, paired_pending_receipt)
        if paired_plan.get("dataset_release") is not None:
            raise EvidenceError("a dataset release cannot pair with another dataset release")
        if not paired_plan["requires_dataset_release"]:
            raise EvidenceError(
                "paired analysis run plan must set requires_dataset_release to true"
            )
    unavailable = (set(active) |
                   {entry["receipt"] for entry in registry["pending"]} |
                   {entry["receipt"] for entry in registry["retired"]})
    if receipt_raw in unavailable:
        raise EvidenceError(f"result receipt path already has lifecycle history: {receipt_raw}")
    normalized_supersedes: list[str] = []
    active_pairs = registry["active_dataset_release_pairs"]
    active_pair_analyses = set(active_pairs)
    active_pair_releases = set(active_pairs.values())
    for raw in supersedes:
        normalized, _ = result_receipt_path(root, raw)
        if normalized == receipt_raw:
            raise EvidenceError("a receipt cannot supersede itself")
        if normalized not in active:
            raise EvidenceError(f"superseded receipt is not active: {normalized}")
        if normalized in active_pair_analyses | active_pair_releases:
            allowed = ((pair_role == "analysis" and normalized in active_pair_analyses) or
                       (pair_role == "release" and normalized in active_pair_releases))
            if not allowed:
                raise EvidenceError(
                    "dataset-release pair predecessors may only be superseded by the "
                    "same member kind of a replacement pair"
                )
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
    validate_pending_activation_relation(
        root, receipt_raw, supersedes, set(registry["active"])
    )
    registry["pending"] = [entry for entry in registry["pending"]
                           if entry["receipt"] != receipt_raw]
    registry["active"].append(receipt_raw)
    registry["active"].sort()
    load_registry(root, candidate=registry)
    atomic_json(path, registry)


def validate_pending_activation_relation(
        root: Path, receipt_raw: str, pending_supersedes: list[str],
        active: set[str]) -> None:
    """Bind a pending registry edge to its immutable receipt before activation."""
    recorded_supersedes = result_receipt_supersedes(root, receipt_raw)
    if recorded_supersedes != pending_supersedes:
        raise EvidenceError(
            f"pending replacement relation disagrees with receipt: {receipt_raw}"
        )
    unavailable = sorted(set(pending_supersedes) - active)
    if unavailable:
        raise EvidenceError(
            f"pending superseded receipt is no longer active: {', '.join(unavailable)}"
        )


def command_init_registry(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    _, path = project_path(root, REGISTRY_PATH, must_exist=False)
    if path.exists():
        raise EvidenceError(f"result registry already exists: {REGISTRY_PATH}")
    _, output = project_path(root, "output")
    receipt_entries = [entry for entry in walk_directory(output)
                       if entry[0].endswith("results.receipt.json")]
    for relative, _, info, _ in receipt_entries:
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EvidenceError(
                f"result receipt-shaped path is not one regular non-aliased file: "
                f"output/{relative}"
            )
    if receipt_entries:
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
    pending_pairs = pending_dataset_release_pairs(root, registry)
    paired_pending = set(pending_pairs) | set(pending_pairs.values())
    if receipt_raw in paired_pending:
        raise EvidenceError(
            "pending dataset-release pair members must use retire-pair"
        )
    active_pairs = registry["active_dataset_release_pairs"]
    paired_active = set(active_pairs) | set(active_pairs.values())
    if receipt_raw in paired_active:
        raise EvidenceError(
            "active dataset-release pair members must use retire-pair"
        )
    if receipt_raw in registry["active"]:
        dependents = active_empirical_operand_dependents(
            root, registry, [receipt_raw]
        )[receipt_raw]
        if dependents and args.superseded_by is None:
            raise EvidenceError(
                "cannot reject or withdraw empirical evidence used by active "
                "comparison receipts; first activate a replacement and retire with "
                "--superseded-by: " + ", ".join(sorted(dependents))
            )
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
        value = validate_receipt_contract(root, receipt)
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
        exhibits = producer.get("exhibits")
        if not isinstance(exhibits, list) or any(not isinstance(raw, str) for raw in exhibits):
            raise EvidenceError(f"lifecycle receipt has malformed exhibit inventory: {receipt_raw}")
        reserved.update(exhibits)
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
    empirical = bool(getattr(args, "empirical", False))
    empirical_contracts: dict[str, dict[str, Any]] = {}
    if empirical:
        if plan.get("dataset_release") is not None:
            raise EvidenceError("offline dataset release builds use run, not run-empirical")
        empirical_contracts, _ = validate_empirical_plan(root, plan, completed=False)
    else:
        if "analyses" in plan:
            raise EvidenceError("a plan with analyses must use run-empirical")
        empirical_reports = [
            raw for raw in plan["artifacts"]
            if re.fullmatch(
                r"output/stage3a/(?:empirical_analysis|empirical_feasibility)[^/]*\.md",
                raw,
            )
        ]
        if empirical_reports:
            raise EvidenceError(
                "autonomous empirical reports must use run-empirical: " +
                ", ".join(empirical_reports)
            )
    if entrypoint not in plan["producer_code"]:
        raise EvidenceError("producer command entrypoint is not declared in the pre-run plan")
    bundle_raw, bundle_target = project_path(root, args.bundle, must_exist=False)
    if not bundle_raw.startswith("output/"):
        raise EvidenceError("result bundle path must be under output/")
    reject_audit_namespace(bundle_raw, "result bundle")
    receipt_raw, target = result_receipt_path(root, args.receipt)
    if _dataset_namespace_path(bundle_raw) or _dataset_namespace_path(receipt_raw):
        raise EvidenceError(
            "result bundle and receipt paths may not enter the output/dataset namespace"
        )
    if bundle_target.exists():
        raise EvidenceError(f"new result bundle path already exists: {bundle_raw}")
    if target.exists():
        raise EvidenceError(f"new result receipt path already exists: {receipt_raw}")
    if bundle_raw == receipt_raw:
        raise EvidenceError("bundle and receipt paths must be different")
    release = plan.get("dataset_release")
    if release is not None and release["producing_receipt"] != receipt_raw:
        raise EvidenceError(
            "run plan.dataset_release.producing_receipt must equal --receipt"
        )
    plan_snapshot = fingerprint(root, plan_raw)
    code_snapshot = fingerprint_many(root, plan["producer_code"])
    input_snapshot = fingerprint_many(root, plan["producer_inputs"])
    renderer_snapshot = fingerprint_many(root, plan["renderer_code"])
    release_classifications, release_input_sources = (
        _validate_dataset_release_sources(
            plan, root, expected_input_snapshots=input_snapshot
        )
    )
    _validate_dataset_rights_authority(plan, root)
    paired_analysis_receipt = (
        release["analysis_receipt"] if release is not None else None
    )
    registry, registry_path, supersedes = validate_registration_plan(
        root, receipt_raw, args.supersedes,
        paired_pending_receipt=paired_analysis_receipt,
        pair_role=("release" if release is not None else
                   "analysis" if plan["requires_dataset_release"] else None),
    )
    if empirical:
        validate_empirical_relationships(
            root, receipt_raw, plan, empirical_contracts,
            eligible_receipts=empirical_operand_eligible_receipts(root, registry),
        )
        spec_paths = {
            declaration["contract"] for declaration in plan["analyses"].values()
        }
        spec_paths.update(
            contract["baseline"]["path"] for contract in empirical_contracts.values()
        )
        enforce_empirical_spec_immutability(root, spec_paths, registry)
    paired_analysis_supersedes: list[str] = []
    if paired_analysis_receipt is not None:
        paired_entry = next(
            entry for entry in registry["pending"]
            if entry["receipt"] == paired_analysis_receipt
        )
        paired_analysis_supersedes = paired_entry["supersedes"]
    active_pairs = registry["active_dataset_release_pairs"]
    active_release_receipts = set(active_pairs.values())
    replaceable_receipts = set(supersedes) | set(paired_analysis_supersedes)
    replaceable_release_receipts: set[str] = set()
    if plan["requires_dataset_release"]:
        for predecessor in supersedes:
            paired_release = active_pairs.get(predecessor)
            if paired_release is None:
                raise EvidenceError(
                    "replacement dataset analysis must supersede only active paired "
                    f"analysis receipts: {predecessor}"
                )
            replaceable_receipts.add(paired_release)
            replaceable_release_receipts.add(paired_release)
    if release is not None and (supersedes or paired_analysis_supersedes):
        validate_dataset_release_pair_supersession(
            root, paired_analysis_supersedes, supersedes, set(registry["active"])
        )
        replaceable_release_receipts.update(supersedes)
        replaceable_receipts.update(supersedes)
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
    registry_snapshot = fingerprint(root, REGISTRY_PATH)
    active_snapshots = [fingerprint(root, raw) for raw in registry["active"]]
    active_failures: list[str] = []
    replaceable_prefixes = (
        "producer_run.code:", "producer_run.inputs:",
        "producer_run.renderer_code:", "render_run.code:",
    )
    def filter_replacement_failures(raw: str, failures: list[str]) -> list[str]:
        if not replaceable_receipts or raw in active_release_receipts:
            return failures
        return [
            item for item in failures
            if not item.startswith(replaceable_prefixes)
        ]

    # A data-first predecessor pair deliberately remains active until both
    # replacement halves pass.  After Gate 2 advances, its old release is no
    # longer current-authority evidence, so verify that exact registry-derived
    # predecessor intrinsically (receipt/plan/code/input/output/manifest bytes)
    # while exempting only the moving Gate-2 pointer.  The shared-source waiver
    # needed for sequential ordinary replacements never applies to any active
    # dataset-release receipt, whether or not that release is being replaced.
    # Every unrelated active release also receives the ordinary authority check.
    for raw in registry["active"]:
        failures = verify_receipt(
            root, root / raw, rerender=False,
            enforce_current_dataset_authority=(
                raw not in replaceable_release_receipts
            ),
        )["failures"]
        failures = filter_replacement_failures(raw, failures)
        active_failures.extend(f"{raw}: {item}" for item in failures)
    if active_failures:
        raise EvidenceError("active evidence is stale before analysis: " + "; ".join(active_failures))
    registry_before = json.loads(json.dumps(registry))
    workspace_sources = [plan_raw, *plan["producer_code"], *plan["producer_inputs"],
                         *plan["renderer_code"]]
    workspace_outputs = [bundle_raw, *plan["artifacts"], *plan["exhibits"]]
    environment_capture = capture_execution_environment(root, command)
    read_only_bindings: list[tuple[int, Path, Path]] = []
    with isolated_workspace(
            root, workspace_sources, workspace_outputs,
            read_only_bindings=read_only_bindings) as workspace:
        execute(
            command, workspace, bundle_path=bundle_raw, project_root=root,
            allow_network=plan["network_access"],
            provider_credentials=set(plan["provider_credentials"]),
            read_only_bindings=read_only_bindings,
        )
        require_stable_environment(
            environment_capture, capture_execution_environment(root, command),
            "analysis",
        )
        isolated_source_failures = compare_isolated_sources(
            root, workspace,
            [plan_snapshot, *code_snapshot, *input_snapshot, *renderer_snapshot],
            read_only_bindings,
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
        lineage: list[dict[str, Any]] | None = None
        if empirical:
            projections = validate_empirical_execution(
                workspace, plan, empirical_contracts
            )
            lineage = validate_empirical_bundle(bundle, empirical_contracts, projections)
            if ("inputs" not in bundle["renderer"] or
                    bundle["renderer"]["inputs"] != plan["renderer_inputs"]):
                raise EvidenceError(
                    "empirical bundle renderer.inputs differs from run plan.renderer_inputs"
                )
        command_uses_declared_code(command, bundle["producer"]["code"], "producer")
        if (bundle["producer"]["code"] != plan["producer_code"] or
                bundle["producer"]["inputs"] != plan["producer_inputs"] or
                bundle["renderer"]["code"] != plan["renderer_code"] or
                effective_renderer_inputs(bundle) != plan["renderer_inputs"] or
                [entry["path"] for entry in bundle["artifacts"]] != plan["artifacts"] or
                [entry["path"] for entry in bundle["exhibits"]] != plan["exhibits"]):
            raise EvidenceError("result bundle does not exactly match the pre-run plan")
        _validate_staged_dataset_release(
            plan, workspace, release_classifications, release_input_sources,
            producer_code_snapshots=code_snapshot,
            producer_entrypoint=entrypoint,
        )
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
            failures = verify_receipt(
                root, root / raw, rerender=False,
                enforce_current_dataset_authority=(
                    raw not in replaceable_release_receipts
                ),
            )["failures"]
            failures = filter_replacement_failures(raw, failures)
            precommit_failures.extend(failures)
        if precommit_failures:
            raise EvidenceError("declared or active evidence changed during analysis: " +
                                "; ".join(precommit_failures))
        # Re-check the mutable orchestrator state immediately before publication;
        # the rights inventory itself is already covered by the producer-input lease.
        _validate_dataset_rights_authority(plan, root)
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
                "receipt_version": (
                    EMPIRICAL_RECEIPT_VERSION if empirical else RECEIPT_VERSION
                ),
                "supersedes": supersedes,
                "producer_run": snapshot_bundle(
                    root, bundle, bundle_raw, command, plan_raw,
                    code_snapshot, input_snapshot, renderer_snapshot,
                    environment_capture,
                ),
                "render_run": None,
            }
            if lineage is not None:
                receipt["lineage"] = lineage
            atomic_json(target, receipt)
            registry["pending"].append({
                "receipt": receipt_raw,
                "supersedes": supersedes,
                "paired_analysis_receipt": paired_analysis_receipt,
            })
            registry["receipt_fingerprints"][receipt_raw] = fingerprint(root, receipt_raw)
            load_registry(root, candidate=registry)
            atomic_json(registry_path, registry)
            require_source_leases_intact(read_only_bindings)
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
            receipt.get("receipt_version") not in {
                RECEIPT_VERSION, EMPIRICAL_RECEIPT_VERSION
            }):
        raise EvidenceError(f"not a results receipt v2/v3: {args.receipt}")
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
    def finalize_render(environment_capture: dict[str, Any]) -> None:
        rendered_snapshot = snapshot_render(root, bundle, command, environment_capture)
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

    try:
        execute_fresh_exhibits(
            command, root, bundle, bundle_field["path"],
            expected=expected_exhibits,
            finalize_while_sources_pinned=finalize_render,
        )
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
    registry_before, _ = load_registry(root)
    if result_receipt_run_plan(root, receipt_raw)["requires_dataset_release"]:
        raise EvidenceError(
            "analysis receipt requires its dataset release and must use activate-pair"
        )
    release_pairs = pending_dataset_release_pairs(root, registry_before)
    paired_receipts = set(release_pairs) | set(release_pairs.values())
    if receipt_raw in paired_receipts:
        raise EvidenceError(
            "paired analysis/release receipts require activate-pair"
        )
    report = verify_receipt(root, target, rerender=False)
    if report["failures"]:
        raise EvidenceError("cannot activate stale result receipt: " +
                            "; ".join(report["failures"]))
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


def receipt_bound_run_plan(root: Path, receipt_raw: str,
                           expected_receipt: dict[str, Any]) -> dict[str, Any]:
    """Read one plan from the exact registered receipt and plan bytes."""
    receipt, receipt_snapshot = load_json_snapshot(root, receipt_raw)
    if receipt_snapshot != expected_receipt:
        raise EvidenceError(f"registered result receipt bytes are stale: {receipt_raw}")
    producer = receipt.get("producer_run") if isinstance(receipt, dict) else None
    plan_record = producer.get("plan") if isinstance(producer, dict) else None
    plan_raw = plan_record.get("path") if isinstance(plan_record, dict) else None
    if not isinstance(plan_raw, str):
        raise EvidenceError(f"result receipt has no valid run plan: {receipt_raw}")
    validate_snapshot_record(
        root, plan_record, f"result receipt {receipt_raw}.producer_run.plan"
    )
    plan, plan_snapshot = load_json_snapshot(root, plan_raw)
    if plan_snapshot != plan_record:
        raise EvidenceError(f"result receipt run plan has stale bytes: {receipt_raw}")
    return validate_run_plan(plan, root)


def derive_registry_dataset_release_pairs(
        root: Path, active: list[str], pending: list[dict[str, Any]],
        receipt_fingerprints: dict[str, dict[str, Any]],
        ) -> tuple[dict[str, str], dict[str, str]]:
    """Derive pair identity from receipt-bound plans, never from mutable labels."""
    active_plans = {
        raw: receipt_bound_run_plan(root, raw, receipt_fingerprints[raw])
        for raw in active
    }
    active_analyses = {
        raw for raw, plan in active_plans.items()
        if plan["requires_dataset_release"] and plan.get("dataset_release") is None
    }
    active_pairs: dict[str, str] = {}
    for release_raw, plan in active_plans.items():
        release = plan.get("dataset_release")
        if release is None:
            continue
        analysis_raw = release["analysis_receipt"]
        if analysis_raw not in active_analyses or analysis_raw in active_pairs:
            raise EvidenceError(
                "active dataset release has no unique active analysis receipt: "
                f"{release_raw}"
            )
        active_pairs[analysis_raw] = release_raw
    missing_active_releases = sorted(active_analyses - active_pairs.keys())
    if missing_active_releases:
        raise EvidenceError(
            "active dataset-release-requiring analysis has no active release: "
            + ", ".join(missing_active_releases)
        )

    pending_paths = [entry["receipt"] for entry in pending]
    pending_set = set(pending_paths)
    pending_pairs: dict[str, str] = {}
    pending_release_receipts: set[str] = set()
    for entry in pending:
        raw = entry["receipt"]
        plan = receipt_bound_run_plan(root, raw, receipt_fingerprints[raw])
        release = plan.get("dataset_release")
        stored_analysis = entry.get("paired_analysis_receipt")
        if release is None:
            if stored_analysis is not None:
                raise EvidenceError(
                    "non-release pending receipt carries dataset pair identity: " + raw
                )
            continue
        analysis_raw = release["analysis_receipt"]
        if stored_analysis != analysis_raw:
            raise EvidenceError(
                "pending dataset-release pair identity disagrees with receipt-bound plan: "
                + raw
            )
        if analysis_raw not in pending_set or analysis_raw in pending_pairs:
            raise EvidenceError(
                "pending dataset release has no unique pending analysis: " + raw
            )
        pending_pairs[analysis_raw] = raw
        pending_release_receipts.add(raw)
    if set(pending_pairs) & pending_release_receipts:
        raise EvidenceError("pending dataset releases may not form a release chain")
    return active_pairs, pending_pairs


def result_receipt_run_plan(root: Path, receipt_raw: str) -> dict[str, Any]:
    """Load the fresh, receipt-bound run plan named by a live result receipt."""
    registry, _ = load_registry(root)
    expected = registry["receipt_fingerprints"].get(receipt_raw)
    if expected is None:
        raise EvidenceError(f"result receipt is not active or pending: {receipt_raw}")
    return receipt_bound_run_plan(root, receipt_raw, expected)


def pending_dataset_release_pairs(root: Path, registry: dict[str, Any]) -> dict[str, str]:
    """Map each pending analysis receipt to its pending dataset-release receipt."""
    _, pairs = derive_registry_dataset_release_pairs(
        root, registry["active"], registry["pending"],
        registry["receipt_fingerprints"],
    )
    return pairs


def command_retire_pair(args: argparse.Namespace) -> int:
    """Atomically retire both members of one pending or active dataset pair."""
    root = resolve_root(args.project_root)
    if not isinstance(args.reason, str) or not args.reason.strip():
        raise EvidenceError("retirement reason must be non-empty")
    analysis_raw, _ = result_receipt_path(root, args.analysis_receipt)
    release_raw, _ = result_receipt_path(root, args.release_receipt)
    if analysis_raw == release_raw:
        raise EvidenceError("analysis and release receipts must be different")
    registry_before, registry_path = load_registry(root)
    pending_pairs = pending_dataset_release_pairs(root, registry_before)
    is_pending = pending_pairs.get(analysis_raw) == release_raw
    is_active = (
        registry_before["active_dataset_release_pairs"].get(analysis_raw) == release_raw
    )
    if is_pending == is_active:
        raise EvidenceError(
            "receipts are not exactly one pending or active dataset-release pair"
        )
    superseded_by_analysis = args.superseded_by_analysis
    superseded_by_release = args.superseded_by_release
    if (superseded_by_analysis is None) != (superseded_by_release is None):
        raise EvidenceError(
            "paired retirement requires both replacement receipts or neither"
        )
    if is_pending and superseded_by_analysis is not None:
        raise EvidenceError("pending pair retirement cannot name active replacements")
    registry_after = json.loads(json.dumps(registry_before))
    members = {analysis_raw, release_raw}
    replacements: dict[str, str] = {}
    if is_pending:
        registry_after["pending"] = [
            entry for entry in registry_after["pending"]
            if entry["receipt"] not in members
        ]
    else:
        dependents = active_empirical_operand_dependents(
            root, registry_before, members
        )
        dependent_descriptions = [
            f"{raw}: {', '.join(sorted(values))}"
            for raw, values in sorted(dependents.items()) if values
        ]
        if dependent_descriptions and superseded_by_analysis is None:
            raise EvidenceError(
                "cannot reject or withdraw dataset evidence used by active "
                "comparison receipts; first activate a replacement pair and retire "
                "with --superseded-by-analysis/--superseded-by-release: " +
                "; ".join(dependent_descriptions)
            )
        blockers = [
            entry["receipt"] for entry in registry_before["pending"]
            if members & set(entry["supersedes"])
        ]
        if blockers:
            raise EvidenceError(
                "cannot retire an active pair while pending replacements supersede it: "
                + ", ".join(sorted(blockers))
            )
        active = set(registry_before["active"])
        active_replacements = {
            raw: [
                candidate for candidate in sorted(active - members)
                if raw in result_receipt_supersedes(root, candidate)
            ]
            for raw in members
        }
        if any(active_replacements.values()):
            if superseded_by_analysis is None or superseded_by_release is None:
                raise EvidenceError(
                    "retiring a superseded active pair requires both replacement receipts"
                )
            replacement_analysis, _ = result_receipt_path(
                root, superseded_by_analysis
            )
            replacement_release, _ = result_receipt_path(root, superseded_by_release)
            if (replacement_analysis not in active_replacements[analysis_raw] or
                    replacement_release not in active_replacements[release_raw] or
                    registry_before["active_dataset_release_pairs"].get(
                        replacement_analysis
                    ) != replacement_release):
                raise EvidenceError(
                    "--superseded-by pair must name the matching active replacement pair"
                )
            replacements = {
                analysis_raw: replacement_analysis,
                release_raw: replacement_release,
            }
        elif superseded_by_analysis is not None:
            raise EvidenceError("active pair has no declared replacement pair")
        registry_after["active"] = sorted(
            set(registry_after["active"]) - members
        )
        del registry_after["active_dataset_release_pairs"][analysis_raw]
    reason = args.reason.strip()
    for raw in sorted(members):
        retired_entry = {
            "receipt": raw,
            "reason": reason,
            "last_fingerprint": registry_after["receipt_fingerprints"].pop(raw),
        }
        if raw in replacements:
            retired_entry["superseded_by"] = replacements[raw]
        registry_after["retired"].append(retired_entry)
    load_registry(root, candidate=registry_after)
    transaction = prepare_lifecycle_transaction(
        root, cleanup_paths=[], restore_paths=[],
        registry_before=json.loads(json.dumps(registry_before)),
    )
    try:
        atomic_json(registry_path, registry_after)
    except BaseException:
        rollback_lifecycle_transaction(root, transaction)
        raise
    commit_lifecycle_transaction(root)
    print(json.dumps({
        "status": "RETIRED_PAIR",
        "analysis_receipt": analysis_raw,
        "release_receipt": release_raw,
    }, sort_keys=True))
    return 0


def validate_dataset_release_pair_supersession(
        root: Path, analysis_predecessors: list[str],
        release_predecessors: list[str], active: set[str]) -> None:
    """Require replacement analysis/release halves to preserve the same lineage."""
    expected_release_predecessors: set[str] = set()
    for predecessor in analysis_predecessors:
        predecessor_plan = result_receipt_run_plan(root, predecessor)
        if (predecessor_plan.get("dataset_release") is not None or
                not predecessor_plan["requires_dataset_release"]):
            raise EvidenceError(
                "analysis supersession must name only dataset-release-requiring "
                f"analysis receipts: {predecessor}"
            )
        matches = []
        for active_raw in sorted(active):
            active_plan = result_receipt_run_plan(root, active_raw)
            active_release = active_plan.get("dataset_release")
            if (active_release is not None and
                    active_release["analysis_receipt"] == predecessor):
                matches.append(active_raw)
        if len(matches) != 1:
            raise EvidenceError(
                "superseded analysis does not have exactly one active release predecessor: "
                f"{predecessor}"
            )
        expected_release_predecessors.add(matches[0])
    for predecessor in release_predecessors:
        predecessor_plan = result_receipt_run_plan(root, predecessor)
        release = predecessor_plan.get("dataset_release")
        if release is None or release["analysis_receipt"] not in analysis_predecessors:
            raise EvidenceError(
                "release supersession must name only releases paired with the "
                f"analysis predecessors: {predecessor}"
            )
    if set(release_predecessors) != expected_release_predecessors:
        raise EvidenceError(
            "release supersession does not match the analysis pair lineage"
        )


def command_activate_pair(args: argparse.Namespace) -> int:
    """Atomically activate one reviewed data-first analysis/release pair."""
    root = resolve_root(args.project_root)
    analysis_raw, analysis_path = result_receipt_path(root, args.analysis_receipt)
    release_raw, release_path = result_receipt_path(root, args.release_receipt)
    if analysis_raw == release_raw:
        raise EvidenceError("analysis and release receipts must be different")
    registry_before, registry_path = load_registry(root)
    pairs = pending_dataset_release_pairs(root, registry_before)
    if pairs.get(analysis_raw) != release_raw:
        raise EvidenceError("receipts are not one pending dataset-release pair")
    reports = {
        analysis_raw: verify_receipt(root, analysis_path, rerender=True),
        release_raw: verify_receipt(root, release_path, rerender=False),
    }
    failures = [
        f"{raw}: {failure}"
        for raw, report in reports.items()
        for failure in report["failures"]
    ]
    if failures:
        raise EvidenceError("cannot activate stale result pair: " + "; ".join(failures))
    analysis_plan = result_receipt_run_plan(root, analysis_raw)
    release_plan = result_receipt_run_plan(root, release_raw)
    release = release_plan.get("dataset_release")
    if (analysis_plan.get("dataset_release") is not None or
            not analysis_plan["requires_dataset_release"]):
        raise EvidenceError(
            "paired analysis run plan must be a dataset-release-requiring analysis"
        )
    if release is None or release["analysis_receipt"] != analysis_raw:
        raise EvidenceError(
            "paired release run plan must name the exact analysis receipt"
        )
    _validate_dataset_rights_authority(release_plan, root)
    pending_entries = {
        entry["receipt"]: entry for entry in registry_before["pending"]
    }
    active = set(registry_before["active"])
    validate_dataset_release_pair_supersession(
        root,
        pending_entries[analysis_raw]["supersedes"],
        pending_entries[release_raw]["supersedes"],
        active,
    )
    for raw in (analysis_raw, release_raw):
        validate_pending_activation_relation(
            root, raw, pending_entries[raw]["supersedes"], active
        )
    registry_after = json.loads(json.dumps(registry_before))
    registry_after["pending"] = [
        entry for entry in registry_after["pending"]
        if entry["receipt"] not in {analysis_raw, release_raw}
    ]
    registry_after["active"] = sorted(
        set(registry_after["active"]) | {analysis_raw, release_raw}
    )
    active_pairs = registry_after["active_dataset_release_pairs"]
    if (analysis_raw in active_pairs or release_raw in active_pairs.values() or
            analysis_raw in active_pairs.values() or release_raw in active_pairs):
        raise EvidenceError("dataset-release pair member already has an active pairing")
    active_pairs[analysis_raw] = release_raw
    load_registry(root, candidate=registry_after)
    transaction = prepare_lifecycle_transaction(
        root, cleanup_paths=[], restore_paths=[],
        registry_before=json.loads(json.dumps(registry_before)),
    )
    try:
        atomic_json(registry_path, registry_after)
    except BaseException:
        rollback_lifecycle_transaction(root, transaction)
        raise
    commit_lifecycle_transaction(root)
    print(json.dumps({
        "status": "ACTIVE_PAIR",
        "analysis_receipt": analysis_raw,
        "release_receipt": release_raw,
        "supersedes_to_retire": {
            analysis_raw: pending_entries[analysis_raw]["supersedes"],
            release_raw: pending_entries[release_raw]["supersedes"],
        },
    }, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    _, target, _ = require_renderable_receipt(root, args.receipt)
    result = verify_receipt(root, target, rerender=args.rerender)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


def command_validate_receipt(args: argparse.Namespace) -> int:
    root = resolve_root(args.project_root)
    _, target = result_receipt_path(root, args.receipt)
    validate_receipt_contract(root, target)
    print(json.dumps({"status": "VALID", "receipt": args.receipt}, sort_keys=True))
    return 0


def command_inspect_registry(args: argparse.Namespace) -> int:
    """Return validated lifecycle metadata without executing or verifying producers."""
    root = resolve_root(args.project_root)
    prefix, _ = project_path(root, args.artifact_prefix, must_exist=False)
    if not prefix.startswith("output/"):
        raise EvidenceError("artifact inspection prefix must be under output/")
    registry, _ = load_registry(root)
    lifecycle_entries = [
        *((raw, "active", None) for raw in registry["active"]),
        *((entry["receipt"], "pending", entry["supersedes"])
          for entry in registry["pending"]),
        *((entry["receipt"], "retired", None) for entry in registry["retired"]),
    ]
    receipts: list[dict[str, Any]] = []
    for receipt_raw, lifecycle, pending_supersedes in lifecycle_entries:
        _, receipt_path_value = result_receipt_path(root, receipt_raw)
        receipt = validate_receipt_contract(root, receipt_path_value)
        matching_artifacts = []
        for recorded in receipt["producer_run"]["artifacts"]:
            if recorded["path"].startswith(prefix):
                matching_artifacts.append({
                    "recorded": recorded,
                    "current": fingerprint(root, recorded["path"]),
                })
        receipts.append({
            "receipt": receipt_raw,
            "lifecycle": lifecycle,
            "pending_supersedes": pending_supersedes,
            "receipt_supersedes": receipt["supersedes"],
            "plan": {
                "recorded": receipt["producer_run"]["plan"],
                "current": fingerprint(root, receipt["producer_run"]["plan"]["path"]),
            },
            "bundle": {
                "recorded": receipt["producer_run"]["bundle"],
                "current": fingerprint(root, receipt["producer_run"]["bundle"]["path"]),
            },
            "artifacts": matching_artifacts,
        })
    print(json.dumps({"receipts": receipts}, indent=2, sort_keys=True))
    return 0


def reject_unresolved_transaction(root: Path) -> None:
    """Fail a read-only inspection when a normal command must recover state."""
    _, journal = project_path(root, TRANSACTION_PATH, must_exist=False)
    _, backup_root = project_path(root, TRANSACTION_BACKUP_PATH, must_exist=False)
    if (
        journal.exists()
        or journal.is_symlink()
        or backup_root.exists()
        or backup_root.is_symlink()
    ):
        raise EvidenceError(
            "results transaction recovery is required before registry inspection"
        )


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
    candidates: list[Path] = []
    for relative, child, info, _ in walk_directory(output):
        if not relative.endswith("results.receipt.json"):
            continue
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise EvidenceError(
                f"result receipt-shaped path is not one regular non-aliased file: "
                f"output/{relative}"
            )
        candidates.append(child)
    candidates.sort()
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
            "activated replacement handoff is incomplete; complete the caller/stage "
            "handoff and "
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
    """Remove TeX comments while masking literal/verbatim content.

    Static dependency and citation scans must neither stop at a literal percent
    inside ``\\verb`` nor inventory commands printed as examples.
    """
    def masked(raw: str) -> str:
        return "".join("\n" if character == "\n" else " " for character in raw)

    def remove_option_comments(raw: str) -> str:
        """Apply TeX percent-comment parity inside a known option/settings group."""
        cleaned: list[str] = []
        position = 0
        while position < len(raw):
            if raw[position] == "%":
                backslashes = 0
                cursor = position - 1
                while cursor >= 0 and raw[cursor] == "\\":
                    backslashes += 1
                    cursor -= 1
                if backslashes % 2 == 0:
                    newline = raw.find("\n", position)
                    if newline < 0:
                        break
                    cleaned.append("\n")
                    position = newline + 1
                    continue
            cleaned.append(raw[position])
            position += 1
        return "".join(cleaned)

    def balanced_end(start: int, opening: str, closing: str, *,
                     tex_comments: bool = False) -> int | None:
        if start >= len(text) or text[start] != opening:
            return None
        depth = 0
        index = start
        while index < len(text):
            if tex_comments and text[index] == "%":
                preceding = index - 1
                backslashes = 0
                while preceding >= 0 and text[preceding] == "\\":
                    backslashes += 1
                    preceding -= 1
                if backslashes % 2 == 0:
                    newline = text.find("\n", index)
                    if newline < 0:
                        return None
                    index = newline + 1
                    continue
            preceding = index - 1
            backslashes = 0
            while preceding >= 0 and text[preceding] == "\\":
                backslashes += 1
                preceding -= 1
            escaped = backslashes % 2 == 1
            if text[index] == opening and not escaped:
                depth += 1
            elif text[index] == closing and not escaped:
                depth -= 1
                if depth == 0:
                    return index + 1
            index += 1
        return None

    def url_delimited_end(start: int) -> int | None:
        """Find a url.sty delimiter, ignoring escaped control-symbol delimiters."""
        if start >= len(text):
            return None
        delimiter = text[start]
        position = start + 1
        while position < len(text):
            closing = text.find(delimiter, position)
            if closing < 0:
                return None
            preceding = closing - 1
            backslashes = 0
            while preceding >= 0 and text[preceding] == "\\":
                backslashes += 1
                preceding -= 1
            if backslashes % 2 == 0:
                return closing + 1
            position = closing + 1
        return None

    def skip_tex_space_and_comments(start: int) -> int:
        """Skip TeX-ignored whitespace and unescaped percent comments."""
        position = start
        while position < len(text):
            while position < len(text) and text[position].isspace():
                position += 1
            if position >= len(text) or text[position] != "%":
                return position
            preceding = position - 1
            backslashes = 0
            while preceding >= 0 and text[preceding] == "\\":
                backslashes += 1
                preceding -= 1
            if backslashes % 2 == 1:
                return position
            newline = text.find("\n", position)
            if newline < 0:
                return len(text)
            position = newline + 1
        return position

    output: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "\\":
            run_end = index
            while run_end < len(text) and text[run_end] == "\\":
                run_end += 1
            count = run_end - index
            paired = count - (count % 2)
            if paired:
                # Every pair is TeX's ``\\`` control symbol, not the start of
                # a second control word. Mask it so regex scanners cannot begin
                # a false command match at the pair's final backslash.
                output.append(" " * paired)
                index += paired
            if count % 2 == 0:
                continue
            command_start = index
            name_end = command_start + 1
            while name_end < len(text) and text[name_end].isalpha():
                name_end += 1
            command = text[command_start + 1:name_end]
            starred_end = name_end + (name_end < len(text) and text[name_end] == "*")

            if command in {"DefineShortVerb", "MakeShortVerb", "lstMakeShortInline",
                           "lstDeleteShortInline"}:
                raise EvidenceError(
                    f"unsupported stateful TeX short-verbatim command: \\{command}"
                )
            if command == "lstdefinestyle":
                raise EvidenceError(
                    "unsupported stateful TeX listings style definition: \\lstdefinestyle"
                )
            if command in {"lstset", "fvset", "setminted", "setmintedinline"}:
                settings_start = skip_tex_space_and_comments(starred_end)
                if command in {"setminted", "setmintedinline"}:
                    language_end = balanced_end(
                        settings_start, "[", "]", tex_comments=True
                    )
                    if language_end is not None:
                        settings_start = skip_tex_space_and_comments(language_end)
                settings_end = balanced_end(
                    settings_start, "{", "}", tex_comments=True
                )
                settings = remove_option_comments(
                    text[settings_start + 1:settings_end - 1]
                    if settings_end is not None else ""
                )
                if re.search(
                        r"(?:commandchars|escapechar|escapeinside|escapebegin|escapeend|aftersave|style|"
                        r"texcl|texcomments|mathescape|literate|basicstyle|identifierstyle|"
                        r"commentstyle|stringstyle|keywordstyle|numberstyle|emphstyle|moredelim|"
                        r"prebreak|postbreak)(?:\s*=|\s*(?:,|$))|\\[A-Za-z@]+",
                        settings, flags=re.IGNORECASE):
                    raise EvidenceError(
                        f"unsupported stateful TeX literal/escape configuration: \\{command}"
                    )

            begin_end: int | None = None
            environment: str | None = None
            if command == "begin":
                environment_start = skip_tex_space_and_comments(starred_end)
                begin_end = balanced_end(environment_start, "{", "}")
                if begin_end is not None:
                    candidate = text[environment_start + 1:begin_end - 1]
                    if re.fullmatch(r"verbatim\*?|Verbatim|lstlisting|minted", candidate):
                        environment = candidate
            if environment is not None and begin_end is not None:
                option_start = skip_tex_space_and_comments(begin_end)
                option_end = balanced_end(
                    option_start, "[", "]", tex_comments=True
                )
                if option_end is not None:
                    options = remove_option_comments(text[option_start + 1:option_end - 1])
                    if re.search(
                            r"(?:commandchars|escapechar|escapeinside|escapebegin|escapeend|aftersave|style|"
                            r"texcl|texcomments|mathescape|literate|basicstyle|identifierstyle|"
                            r"commentstyle|stringstyle|keywordstyle|numberstyle|emphstyle|moredelim|"
                            r"prebreak|postbreak)(?:\s*=|\s*(?:,|$))|\\[A-Za-z@]+",
                            options, flags=re.IGNORECASE):
                        raise EvidenceError(
                            f"escape-enabled {environment} environment is unsupported "
                            "by the paper dependency audit"
                        )
                closing_token = f"\\end{{{environment}}}"
                closing_match = re.search(
                    rf"(?m)^[ \t]*{re.escape(closing_token)}",
                    text[begin_end:],
                )
                if closing_match is None:
                    end = len(text)
                else:
                    end = begin_end + closing_match.end()
                output.append(masked(text[command_start:end]))
                index = end
                continue

            literal_start = starred_end
            if command in {"lstinline", "Verb", "mintinline", "SaveVerb"}:
                literal_start = skip_tex_space_and_comments(literal_start)
                option_end = balanced_end(literal_start, "[", "]")
                if option_end is not None:
                    raise EvidenceError(
                        f"options on \\{command} are unsupported by the paper dependency audit"
                    )
                    literal_start = option_end
                    while literal_start < len(text) and text[literal_start].isspace():
                        literal_start += 1
            if command == "mintinline":
                language_end = balanced_end(literal_start, "{", "}")
                if language_end is not None:
                    literal_start = skip_tex_space_and_comments(language_end)
            if command == "SaveVerb":
                if option_end is not None:
                    raise EvidenceError(
                        "SaveVerb options are unsupported by the paper dependency audit"
                    )
                name_end = balanced_end(literal_start, "{", "}")
                if name_end is not None:
                    literal_start = skip_tex_space_and_comments(name_end)
                    if literal_start < len(text) and text[literal_start] not in "\r\n":
                        delimiter = text[literal_start]
                        closing = text.find(delimiter, literal_start + 1)
                        literal_end = None if closing == -1 else closing + 1
                        if literal_end is not None:
                            output.append(masked(text[command_start:literal_end]))
                            index = literal_end
                            continue
            if command in {"verb", "Verb", "lstinline", "mintinline"}:
                if literal_start < len(text) and text[literal_start] not in "\r\n":
                    if text[literal_start] == "{":
                        literal_end = balanced_end(literal_start, "{", "}")
                    else:
                        delimiter = text[literal_start]
                        closing = text.find(delimiter, literal_start + 1)
                        literal_end = None if closing == -1 else closing + 1
                    if literal_end is not None:
                        output.append(masked(text[command_start:literal_end]))
                        index = literal_end
                        continue

            if command in {"url", "path", "nolinkurl", "href"}:
                argument_start = skip_tex_space_and_comments(starred_end)
                if argument_start < len(text) and text[argument_start] == "{":
                    argument_end = balanced_end(argument_start, "{", "}")
                elif (command != "href" and argument_start < len(text) and
                      text[argument_start] not in "\r\n"):
                    argument_end = url_delimited_end(argument_start)
                else:
                    argument_end = None
                if argument_end is not None:
                    output.append(masked(text[command_start:argument_end]))
                    index = argument_end
                    continue
            output.append("\\")
            index += 1
            continue
        if text[index] == "%":
            preceding = index - 1
            backslashes = 0
            while preceding >= 0 and text[preceding] == "\\":
                backslashes += 1
                preceding -= 1
            if backslashes % 2 == 0:
                newline = text.find("\n", index)
                if newline == -1:
                    break
                output.append("\n")
                index = newline + 1
                continue
        output.append(text[index])
        index += 1
    return "".join(output)


def resolve_latex_dependency(root: Path, paper: Path, current: Path, raw: str,
                             extensions: tuple[str, ...], *, required: bool,
                             append_extension: bool = False,
                             reject_raw_collision: bool = True,
                             preserve_explicit_suffix: bool = False) -> Path | None:
    raw = raw.strip()
    if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
        if required:
            raise EvidenceError(f"dynamic LaTeX dependency cannot be audited: {raw!r}")
        return None
    candidates: list[Path] = []
    for base in (paper, current.parent):
        candidate = base / raw
        if append_extension:
            # TeX commands such as \includegraphics, \usepackage, and
            # \bibliography append a command-specific suffix before opening.
            # A dot in a package basename is not necessarily its TeX suffix:
            # `\usepackage{foo.bar}` opens `foo.bar.sty`, not `foo.bar`.
            if (preserve_explicit_suffix and candidate.suffix) or \
                    candidate.suffix.lower() in extensions:
                choices = [candidate]
            else:
                choices = [Path(str(candidate) + ext) for ext in extensions]
            if (reject_raw_collision and candidate not in choices and
                    candidate.exists() and any(choice.exists() for choice in choices)):
                raise EvidenceError(
                    "ambiguous extensionless and suffixed LaTeX dependency cannot be "
                    f"audited safely: {raw}"
                )
        elif candidate.suffix:
            choices = [candidate]
        else:
            choices = [candidate, *(candidate.with_suffix(ext) for ext in extensions)]
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


def _latex_skip_space(text: str, position: int) -> int:
    while position < len(text) and text[position].isspace():
        position += 1
    return position


def _latex_balanced_group(text: str, position: int,
                          opening: str) -> tuple[str, int] | None:
    """Parse a static TeX group, honoring brace protection inside options."""
    closing_for = {"{": "}", "[": "]", "(": ")"}
    if opening not in closing_for or position >= len(text) or text[position] != opening:
        return None
    stack = [opening]
    cursor = position + 1
    while cursor < len(text):
        preceding = cursor - 1
        backslashes = 0
        while preceding >= position and text[preceding] == "\\":
            backslashes += 1
            preceding -= 1
        if backslashes % 2:
            cursor += 1
            continue
        character = text[cursor]
        current = stack[-1]
        # TeX braces protect `]`/`)` inside optional arguments. Parentheses
        # and square brackets inside a brace group are ordinary characters;
        # treating all three delimiter families as mutually nested rejects
        # standard listings options such as escapeinside={(*@}{@*)}.
        if character == "{":
            stack.append("{")
        elif character == closing_for[current]:
            stack.pop()
            if not stack:
                return text[position + 1:cursor], cursor + 1
        cursor += 1
    return None


def _latex_command_groups(text: str, token: re.Match[str], count: int,
                          *, optional: bool = True) -> tuple[list[str], int] | None:
    """Parse optional arguments followed by a fixed number of braced arguments."""
    cursor = _latex_skip_space(text, token.end())
    if optional:
        while cursor < len(text) and text[cursor] == "[":
            parsed = _latex_balanced_group(text, cursor, "[")
            if parsed is None:
                return None
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
    groups: list[str] = []
    for _ in range(count):
        parsed = _latex_balanced_group(text, cursor, "{")
        if parsed is None:
            return None
        value, cursor = parsed
        groups.append(value)
        cursor = _latex_skip_space(text, cursor)
    return groups, cursor


def _latex_command_parts(text: str, token: re.Match[str], count: int
                         ) -> tuple[list[str], list[str], int] | None:
    """Return balanced optional and required groups for one static command."""
    cursor = _latex_skip_space(text, token.end())
    options: list[str] = []
    while cursor < len(text) and text[cursor] == "[":
        parsed = _latex_balanced_group(text, cursor, "[")
        if parsed is None:
            return None
        value, cursor = parsed
        options.append(value)
        cursor = _latex_skip_space(text, cursor)
    groups: list[str] = []
    for _ in range(count):
        parsed = _latex_balanced_group(text, cursor, "{")
        if parsed is None:
            return None
        value, cursor = parsed
        groups.append(value)
        cursor = _latex_skip_space(text, cursor)
    return options, groups, cursor


def _iter_latex_group_commands(text: str, command_pattern: str, count: int,
                               *, optional: bool = True
                               ) -> Iterable[tuple[re.Match[str], list[str], int]]:
    token_pattern = re.compile(
        r"\\(?:" + command_pattern + r")\*?(?![A-Za-z])"
    )
    for token in token_pattern.finditer(text):
        parsed = _latex_command_groups(text, token, count, optional=optional)
        if parsed is not None:
            groups, end = parsed
            yield token, groups, end


def _iter_latex_command_parts(text: str, command_pattern: str, count: int
                              ) -> Iterable[tuple[re.Match[str], list[str], list[str], int]]:
    token_pattern = re.compile(r"\\(?:" + command_pattern + r")\*?(?![A-Za-z])")
    for token in token_pattern.finditer(text):
        parsed = _latex_command_parts(text, token, count)
        if parsed is not None:
            options, groups, end = parsed
            yield token, options, groups, end


UNSAFE_EXTERNAL_LITERAL_OPTION_RE = re.compile(
    r"(?:commandchars|escapechar|escapeinside|escapebegin|escapeend|aftersave|style|"
    r"texcl|texcomments|mathescape|literate|basicstyle|identifierstyle|"
    r"commentstyle|stringstyle|keywordstyle|numberstyle|emphstyle|moredelim|"
    r"prebreak|postbreak)(?:\s*=|\s*(?:,|$))|\\[A-Za-z@]+",
    flags=re.IGNORECASE,
)


def reject_external_literal_options(token: re.Match[str], options: list[str],
                                    relative: str) -> None:
    if any(UNSAFE_EXTERNAL_LITERAL_OPTION_RE.search(option) for option in options):
        line = token.string.count("\n", 0, token.start()) + 1
        raise EvidenceError(
            f"escape-enabled external literal input is unsupported at {relative}:{line}"
        )


def _iter_addplot_reads(text: str) -> Iterable[tuple[re.Match[str], str]]:
    token_pattern = re.compile(r"\\addplot(?:3)?\+?(?![A-Za-z])")
    for token in token_pattern.finditer(text):
        cursor = _latex_skip_space(text, token.end())
        if cursor < len(text) and text[cursor] == "[":
            parsed = _latex_balanced_group(text, cursor, "[")
            if parsed is None:
                continue
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
        kind_match = re.match(r"(?:table|file)(?![A-Za-z])", text[cursor:])
        if kind_match is None:
            continue
        cursor = _latex_skip_space(text, cursor + kind_match.end())
        if cursor < len(text) and text[cursor] == "[":
            parsed = _latex_balanced_group(text, cursor, "[")
            if parsed is None:
                continue
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
        parsed = _latex_balanced_group(text, cursor, "{")
        if parsed is not None:
            raw, _ = parsed
            yield token, raw


def _parse_citation_token(text: str, token: re.Match[str]
                          ) -> tuple[list[str], int] | None:
    """Parse supported biblatex/natbib citation items without mining note braces."""
    command = token.group("command").lower()
    cursor = _latex_skip_space(text, token.end())
    if cursor < len(text) and text[cursor] == "(":
        for _ in range(2):
            parsed = _latex_balanced_group(text, cursor, "(")
            if parsed is None:
                return None
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
    plural = command.endswith("cites") or command == "footcitetexts"
    volume = command.endswith("volcite") or command.endswith("volcites")
    metadata = command in {"citefield", "citename", "citelist"}
    key_groups: list[str] = []
    while True:
        for _ in range(2):
            if cursor >= len(text) or text[cursor] != "[":
                break
            parsed = _latex_balanced_group(text, cursor, "[")
            if parsed is None:
                return None
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
        if volume:
            parsed = _latex_balanced_group(text, cursor, "{")
            if parsed is None:
                return None
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
            for _ in range(2):
                if cursor >= len(text) or text[cursor] != "[":
                    break
                parsed = _latex_balanced_group(text, cursor, "[")
                if parsed is None:
                    return None
                _, cursor = parsed
                cursor = _latex_skip_space(text, cursor)
        parsed = _latex_balanced_group(text, cursor, "{")
        if parsed is None:
            return None
        key_group, cursor = parsed
        key_groups.append(key_group)
        cursor = _latex_skip_space(text, cursor)
        if metadata:
            parsed = _latex_balanced_group(text, cursor, "{")
            if parsed is None:
                return None
            _, cursor = parsed
            cursor = _latex_skip_space(text, cursor)
        if not plural or cursor >= len(text) or text[cursor] not in "[{":
            break
    return key_groups, cursor


def citation_occurrences(text: str, relative: str) -> list[dict[str, Any]]:
    """Inventory supported citation commands and reject every unknown cite-family command."""
    recognized_spans: list[tuple[int, int]] = []
    citations: list[dict[str, Any]] = []
    citation_ordinal = 0
    for match in CITATION_COMMAND_TOKEN_RE.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        command = match.group("command").lower()
        parsed = _parse_citation_token(text, match)
        if parsed is None:
            raise EvidenceError(f"malformed {command} command at {relative}:{line_number}")
        groups, command_end = parsed
        recognized_spans.append((match.start(), command_end))
        citation_ordinal += 1
        keys = [key.strip() for group in groups
                for key in group.split(",") if key.strip()]
        if not keys or any(not CITE_KEY_RE.fullmatch(key) for key in keys):
            raise EvidenceError(
                f"dynamic or malformed citation key at {relative}:{line_number}"
            )
        separator = text.rfind("\n\n", 0, match.start())
        paragraph_start = 0 if separator < 0 else separator + 2
        paragraph_end = text.find("\n\n", command_end)
        if paragraph_end < 0:
            paragraph_end = len(text)
        claim_text = re.sub(r"\s+", " ", text[paragraph_start:paragraph_end]).strip()
        citations.append({
            "occurrence_id": f"{relative}:{line_number}:cite{citation_ordinal}",
            "cite_keys": keys,
            "claim_text": claim_text,
            "_position": match.start(),
        })
    cquote_spans: list[tuple[int, int]] = []
    cquote_ordinal = 0
    for match in CQUOTE_COMMAND_TOKEN_RE.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        command = match.group("command").lower()
        language_first = command.startswith(("foreign", "hyphen", "hybrid"))
        cursor = _latex_skip_space(text, match.end())
        groups: list[str] = []
        parsed = True
        if language_first:
            language = _latex_balanced_group(text, cursor, "{")
            if language is None:
                parsed = None
            else:
                language_value, cursor = language
                groups.append(language_value)
                cursor = _latex_skip_space(text, cursor)
        while parsed is not None and cursor < len(text) and text[cursor] == "[":
            note = _latex_balanced_group(text, cursor, "[")
            if note is None:
                parsed = None
                break
            _, cursor = note
            cursor = _latex_skip_space(text, cursor)
        if parsed is not None:
            key_group = _latex_balanced_group(text, cursor, "{")
            if key_group is None:
                parsed = None
            else:
                key_value, cursor = key_group
                groups.append(key_value)
                cursor = _latex_skip_space(text, cursor)
        if parsed is not None and cursor < len(text) and text[cursor] == "[":
            punctuation = _latex_balanced_group(text, cursor, "[")
            if punctuation is None:
                parsed = None
            else:
                _, cursor = punctuation
                cursor = _latex_skip_space(text, cursor)
        if parsed is not None:
            quotation = _latex_balanced_group(text, cursor, "{")
            if quotation is None:
                parsed = None
            else:
                quotation_value, command_end = quotation
                groups.append(quotation_value)
        if parsed is None:
            raise EvidenceError(
                f"malformed citation-bearing cquote at {relative}:{line_number}"
            )
        cquote_spans.append((match.start(), command_end))
        cquote_ordinal += 1
        key_index = 1 if language_first else 0
        key = groups[key_index].strip()
        if not CITE_KEY_RE.fullmatch(key):
            raise EvidenceError(
                f"dynamic or malformed citation key at {relative}:{line_number}"
            )
        separator = text.rfind("\n\n", 0, match.start())
        paragraph_start = 0 if separator < 0 else separator + 2
        paragraph_end = text.find("\n\n", command_end)
        if paragraph_end < 0:
            paragraph_end = len(text)
        claim_text = re.sub(r"\s+", " ", text[paragraph_start:paragraph_end]).strip()
        citations.append({
            "occurrence_id": f"{relative}:{line_number}:cquote{cquote_ordinal}",
            "cite_keys": [key],
            "claim_text": claim_text,
            "_position": match.start(),
        })
    display_pattern = re.compile(
        r"\\begin\s*\{(?P<environment>(?:foreign|hyphen)?displaycquote)\}",
        flags=re.IGNORECASE,
    )
    display_spans: list[tuple[int, int]] = []
    for match in display_pattern.finditer(text):
        line_number = text.count("\n", 0, match.start()) + 1
        environment = match.group("environment").lower()
        language_first = environment.startswith(("foreign", "hyphen"))
        cursor = _latex_skip_space(text, match.end())
        if language_first:
            language = _latex_balanced_group(text, cursor, "{")
            if language is None:
                raise EvidenceError(
                    f"malformed citation-bearing {environment} at {relative}:{line_number}"
                )
            _, cursor = language
            cursor = _latex_skip_space(text, cursor)
        while cursor < len(text) and text[cursor] == "[":
            note = _latex_balanced_group(text, cursor, "[")
            if note is None:
                raise EvidenceError(
                    f"malformed citation-bearing {environment} at {relative}:{line_number}"
                )
            _, cursor = note
            cursor = _latex_skip_space(text, cursor)
        key_group = _latex_balanced_group(text, cursor, "{")
        if key_group is None:
            raise EvidenceError(
                f"malformed citation-bearing {environment} at {relative}:{line_number}"
            )
        key, cursor = key_group
        cursor = _latex_skip_space(text, cursor)
        if cursor < len(text) and text[cursor] == "[":
            punctuation = _latex_balanced_group(text, cursor, "[")
            if punctuation is None:
                raise EvidenceError(
                    f"malformed citation-bearing {environment} at {relative}:{line_number}"
                )
            _, cursor = punctuation
        closing = re.search(
            rf"\\end\s*\{{{re.escape(environment)}\}}", text[cursor:],
            flags=re.IGNORECASE,
        )
        if closing is None:
            raise EvidenceError(
                f"unterminated citation-bearing {environment} at {relative}:{line_number}"
            )
        command_end = cursor + closing.end()
        display_spans.append((match.start(), command_end))
        cquote_ordinal += 1
        key = key.strip()
        if not CITE_KEY_RE.fullmatch(key):
            raise EvidenceError(
                f"dynamic or malformed citation key at {relative}:{line_number}"
            )
        separator = text.rfind("\n\n", 0, match.start())
        paragraph_start = 0 if separator < 0 else separator + 2
        paragraph_end = text.find("\n\n", command_end)
        if paragraph_end < 0:
            paragraph_end = len(text)
        claim_text = re.sub(r"\s+", " ", text[paragraph_start:paragraph_end]).strip()
        citations.append({
            "occurrence_id": f"{relative}:{line_number}:cquote{cquote_ordinal}",
            "cite_keys": [key],
            "claim_text": claim_text,
            "_position": match.start(),
        })
    for match in re.finditer(
            r"\\begin\s*\{(?P<environment>[A-Za-z@]*cquote[A-Za-z@]*)\}",
            text, flags=re.IGNORECASE):
        if not any(start <= match.start() < end
                   for start, end in display_spans):
            line_number = text.count("\n", 0, match.start()) + 1
            raise EvidenceError(
                "unsupported citation-bearing cquote environment "
                f"{match.group('environment')} at {relative}:{line_number}"
            )
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
    for match in CQUOTE_FAMILY_RE.finditer(text):
        if not any(start <= match.start() < end for start, end in cquote_spans):
            line_number = text.count("\n", 0, match.start()) + 1
            raise EvidenceError(
                f"unsupported citation-bearing cquote command "
                f"\\{match.group('command').lower()} at {relative}:{line_number}"
            )
    citations.sort(key=lambda item: item["_position"])
    for citation in citations:
        citation.pop("_position")
    return citations


def reject_citation_macro_definitions(text: str, relative: str) -> None:
    """Fail closed on common user-defined citation-command aliases.

    Static occurrence binding cannot soundly expand arbitrary TeX. Rejecting
    the ordinary LaTeX definition forms prevents a citation hidden behind a
    convenient local alias from being counted only at its definition site.
    """
    # Keep every historical definition. TeX command names are case-sensitive,
    # and a later safe redefinition must not erase evidence that an earlier
    # citation-bearing definition could have been invoked.
    definitions: list[tuple[str, str, int]] = []
    command_pattern = re.compile(
        r"\\(?:newcommand|renewcommand|providecommand|DeclareRobustCommand|"
        r"newrobustcmd|renewrobustcmd|providerobustcmd)\*?",
        flags=re.IGNORECASE,
    )
    for match in command_pattern.finditer(text):
        cursor = _latex_skip_space(text, match.end())
        name: str | None = None
        if cursor < len(text) and text[cursor] == "{":
            parsed_name = _latex_balanced_group(text, cursor, "{")
            if parsed_name is not None and re.fullmatch(
                    r"\s*\\[A-Za-z@]+\s*", parsed_name[0]):
                name = parsed_name[0].strip()
                cursor = _latex_skip_space(text, parsed_name[1])
        else:
            bare = re.match(r"\\[A-Za-z@]+", text[cursor:])
            if bare is not None:
                name = bare.group(0)
                cursor = _latex_skip_space(text, cursor + bare.end())
        if name is None:
            continue
        for _ in range(2):
            if cursor >= len(text) or text[cursor] != "[":
                break
            parsed_option = _latex_balanced_group(text, cursor, "[")
            if parsed_option is None:
                break
            _, cursor = parsed_option
            cursor = _latex_skip_space(text, cursor)
        parsed_body = _latex_balanced_group(text, cursor, "{")
        if parsed_body is None:
            raise EvidenceError(
                f"malformed citation-relevant macro definition at {relative}:"
                f"{text.count(chr(10), 0, match.start()) + 1}"
            )
        definitions.append((
            name,
            parsed_body[0],
            text.count("\n", 0, match.start()) + 1,
        ))
    xparse_pattern = re.compile(
        r"\\(?:New|Renew|Provide|Declare)(?:Expandable)?DocumentCommand"
    )
    for match in xparse_pattern.finditer(text):
        cursor = _latex_skip_space(text, match.end())
        name = None
        if cursor < len(text) and text[cursor] == "{":
            parsed_name = _latex_balanced_group(text, cursor, "{")
            if parsed_name is not None and re.fullmatch(
                    r"\s*\\[A-Za-z@]+\s*", parsed_name[0]):
                name = parsed_name[0].strip()
                cursor = _latex_skip_space(text, parsed_name[1])
        else:
            bare = re.match(r"\\[A-Za-z@]+", text[cursor:])
            if bare is not None:
                name = bare.group(0)
                cursor = _latex_skip_space(text, cursor + bare.end())
        if name is None:
            continue
        parsed_spec = _latex_balanced_group(text, cursor, "{")
        if parsed_spec is None:
            raise EvidenceError(
                f"malformed citation-relevant macro definition at {relative}:"
                f"{text.count(chr(10), 0, match.start()) + 1}"
            )
        cursor = _latex_skip_space(text, parsed_spec[1])
        parsed_body = _latex_balanced_group(text, cursor, "{")
        if parsed_body is None:
            raise EvidenceError(
                f"malformed citation-relevant macro definition at {relative}:"
                f"{text.count(chr(10), 0, match.start()) + 1}"
            )
        definitions.append((
            name,
            parsed_body[0],
            text.count("\n", 0, match.start()) + 1,
        ))
    primitive_pattern = re.compile(
        r"\\(?:def|gdef|edef|xdef)\s*(\\[A-Za-z@]+)[^\{]*\{",
        flags=re.IGNORECASE,
    )
    for match in primitive_pattern.finditer(text):
        body_start = match.end() - 1
        parsed_body = _latex_balanced_group(text, body_start, "{")
        if parsed_body is None:
            raise EvidenceError(
                f"malformed citation-relevant macro definition at {relative}:"
                f"{text.count(chr(10), 0, match.start()) + 1}"
            )
        definitions.append((
            match.group(1),
            parsed_body[0],
            text.count("\n", 0, match.start()) + 1,
        ))
    for match in re.finditer(
            r"\\let\s*(\\[A-Za-z@]+)\s*=?\s*(\\[A-Za-z@]+)", text,
            flags=re.IGNORECASE):
        definitions.append((
            match.group(1), match.group(2),
            text.count("\n", 0, match.start()) + 1,
        ))
    declared = re.search(
        r"\\DeclareCiteCommand\*?\s*\{\s*(\\[A-Za-z@]+)\s*\}", text,
        flags=re.IGNORECASE,
    )
    if declared:
        raise EvidenceError(
            f"user-defined citation command {declared.group(1)} is unsupported at "
            f"{relative}:{text.count(chr(10), 0, declared.start()) + 1}"
        )

    bearing: set[str] = set()
    supported_names = {"\\" + command.lower() for command in CITATION_COMMANDS}
    for name, _body, line in definitions:
        if name.lower() in supported_names:
            raise EvidenceError(
                f"redefinition of supported citation command {name} is unsupported at "
                f"{relative}:{line}"
            )
    changed = True
    while changed:
        changed = False
        for name, body, _ in definitions:
            if name in bearing:
                continue
            direct = (
                CITATION_COMMAND_TOKEN_RE.search(body) is not None
                or any(
                    match.group("command").lower()
                    not in NON_OCCURRENCE_CITATION_COMMANDS
                    for match in CITATION_FAMILY_RE.finditer(body)
                )
                or CQUOTE_FAMILY_RE.search(body) is not None
            )
            alias = any(re.search(re.escape(other) + r"(?![A-Za-z@])", body)
                        for other in bearing)
            if direct or alias:
                bearing.add(name)
                changed = True
    if bearing:
        name = sorted(bearing)[0]
        line_number = min(
            line for defined_name, _body, line in definitions if defined_name == name
        )
        raise EvidenceError(
            f"user-defined citation command {name} is unsupported at "
            f"{relative}:{line_number}; use a supported citation command directly"
        )


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
        text = uncomment_latex(read_utf8(current, "LaTeX source"))
        reject_citation_macro_definitions(text, relative)
        citations.extend(citation_occurrences(text, relative))
        unsupported = re.search(
            r"\\(?:(?:import|subimport|inputfrom|includefrom|subinputfrom|subincludefrom|"
            r"graphicspath|DeclareGraphicsExtensions|DTLloaddb|loadglsentries)\s*\{|"
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
            for _, groups, _ in _iter_latex_group_commands(
                    text, r"usepackage|RequirePackage(?:WithOptions)?", 1):
                for raw in groups[0].split(","):
                    raw = raw.strip()
                    if any(token in raw for token in ("\\", "{", "}", "#")):
                        raise EvidenceError(
                            f"dynamic local package dependency in {relative}: {raw!r}"
                        )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, (".sty",), required=False,
                        append_extension=True,
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
                        pending.append(dependency)
            for _, groups, _ in _iter_latex_group_commands(
                    text, r"documentclass|LoadClass(?:WithOptions)?", 1):
                raw = groups[0].strip()
                if any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic local class dependency in {relative}: {raw!r}"
                    )
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".cls",), required=False,
                    append_extension=True,
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
                    required=False, append_extension=True,
                    reject_raw_collision=False, preserve_explicit_suffix=True,
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
                    if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                        pending.append(dependency)
            static_commands: tuple[
                tuple[str, int, int, tuple[str, ...], bool, bool], ...
            ] = (
                (r"input|include|subfile", 1, 0,
                 (".tex",), True, False),
                (r"lstinputlisting|VerbatimInput", 1, 0,
                 (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r"), False, True),
                (r"inputminted", 2, 1,
                 (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r"), False, True),
                (r"csvreader|pgfplotstableread|pgfplotstabletypeset", 1, 0,
                 (".csv", ".tsv", ".txt", ".dat"), False, True),
                (r"includegraphics", 1, 0,
                 (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps"), True, True),
                (r"includepdf", 1, 0, (".pdf",), True, True),
            )
            parsed_reads: list[
                tuple[re.Match[str], str, tuple[str, ...], bool, bool]
            ] = []
            for (command_pattern, count, path_index, extensions,
                 append_extension, reject_raw_collision) in static_commands:
                for token, options, groups, _ in _iter_latex_command_parts(
                        text, command_pattern, count):
                    if command_pattern in {
                            r"lstinputlisting|VerbatimInput", r"inputminted"}:
                        reject_external_literal_options(token, options, relative)
                    parsed_reads.append(
                        (token, groups[path_index], extensions, append_extension,
                         reject_raw_collision)
                    )
            parsed_reads.extend(
                (token, raw, (".csv", ".tsv", ".txt", ".dat"), False, True)
                for token, raw in _iter_addplot_reads(text)
            )
            for match in re.finditer(
                    r"\\(?:input|include|subfile)(?![A-Za-z])\s*"
                    r"(?:\{([^}]+)\}|([^\s%{}]+))", text):
                parsed_reads.append(
                    (match, match.group(1) or match.group(2), (".tex",), True, False)
                )
            for (token, raw_value, extensions, append_extension,
                 reject_raw_collision) in parsed_reads:
                    raw = raw_value.strip()
                    if any(token in raw for token in ("\\", "{", "}", "#")):
                        definition_prefix = text[max(0, token.start() - 24):token.start()]
                        if re.search(r"\\(?:g|x|e)?def\s*$", definition_prefix):
                            # This is the command token being defined, not a
                            # file read (for example `\def\includegraphics`).
                            continue
                        raise EvidenceError(
                            "dynamic local package/class dependency cannot be audited in "
                            f"{relative}: {raw!r}"
                        )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, extensions, required=False,
                        append_extension=append_extension,
                        reject_raw_collision=reject_raw_collision,
                        preserve_explicit_suffix=(
                            append_extension and extensions == (".tex",)
                        ),
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
                        if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                            pending.append(dependency)
            for _, groups, _ in _iter_latex_group_commands(
                    text, r"bibliography|nobibliography|addbibresource|addglobalbib|addsectionbib", 1):
                for raw in groups[0].split(","):
                    raw = raw.strip()
                    if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                        raise EvidenceError(
                            f"dynamic bibliography dependency in {relative}: {raw!r}"
                        )
                    guarded = raw in guarded_files or (
                        not PurePosixPath(raw).suffix and f"{raw}.bib" in guarded_files
                    )
                    dependency = resolve_latex_dependency(
                        root, paper, current, raw, (".bib",), required=not guarded,
                        append_extension=True,
                    )
                    if dependency is not None:
                        paths.add(dependency.relative_to(root).as_posix())
            continue
        for match in re.finditer(
                r"\\(?:input|include|subfile)(?![A-Za-z])\s*"
                r"(?:\{([^}]+)\}|([^\s%{}]+))", text):
            dependency = resolve_latex_dependency(
                root, paper, current, match.group(1) or match.group(2),
                (".tex",), required=True, append_extension=True,
                reject_raw_collision=False, preserve_explicit_suffix=True,
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
                (".tex", ".bib", ".sty", ".cls", ".pdf", ".png"),
                required=False, append_extension=True,
                reject_raw_collision=False, preserve_explicit_suffix=True,
            )
            if dependency is not None:
                paths.add(dependency.relative_to(root).as_posix())
                if dependency.suffix.lower() in {".tex", ".sty", ".cls", ".cfg", ".def"}:
                    pending.append(dependency)
        data_commands: tuple[tuple[str, int, int, tuple[str, ...]], ...] = (
            (r"lstinputlisting|VerbatimInput", 1, 0,
             (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
            (r"inputminted", 2, 1,
             (".tex", ".txt", ".csv", ".tsv", ".json", ".py", ".r")),
            (r"csvreader|pgfplotstableread|pgfplotstabletypeset", 1, 0,
             (".csv", ".tsv", ".txt", ".dat")),
        )
        for command_pattern, count, path_index, extensions in data_commands:
            for token, options, groups, _ in _iter_latex_command_parts(
                    text, command_pattern, count):
                if command_pattern in {
                        r"lstinputlisting|VerbatimInput", r"inputminted"}:
                    reject_external_literal_options(token, options, relative)
                dependency = resolve_latex_dependency(
                    root, paper, current, groups[path_index], extensions, required=True
                )
                assert dependency is not None
                paths.add(dependency.relative_to(root).as_posix())
        for _, raw in _iter_addplot_reads(text):
            dependency = resolve_latex_dependency(
                root, paper, current, raw,
                (".csv", ".tsv", ".txt", ".dat"), required=True,
            )
            assert dependency is not None
            paths.add(dependency.relative_to(root).as_posix())
        for _, groups, _ in _iter_latex_group_commands(text, r"includegraphics", 1):
            dependency = resolve_latex_dependency(
                root, paper, current, groups[0],
                (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps"), required=True,
                append_extension=True,
            )
            assert dependency is not None
            paths.add(dependency.relative_to(root).as_posix())
        for _, groups, _ in _iter_latex_group_commands(text, r"includepdf", 1):
            dependency = resolve_latex_dependency(
                root, paper, current, groups[0], (".pdf",), required=True,
                append_extension=True,
            )
            assert dependency is not None
            paths.add(dependency.relative_to(root).as_posix())
        for _, groups, _ in _iter_latex_group_commands(
                text, r"bibliography|nobibliography|addbibresource|addglobalbib|addsectionbib", 1):
            for raw in groups[0].split(","):
                raw = raw.strip()
                if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic bibliography dependency in {relative}: {raw!r}"
                    )
                guarded = raw in guarded_files or (
                    not PurePosixPath(raw).suffix and f"{raw}.bib" in guarded_files
                )
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".bib",), required=not guarded,
                    append_extension=True,
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
        for _, groups, _ in _iter_latex_group_commands(
                text, r"usepackage|RequirePackage(?:WithOptions)?", 1):
            for raw in groups[0].split(","):
                raw = raw.strip()
                if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                    raise EvidenceError(
                        f"dynamic package dependency in {relative}: {raw!r}"
                    )
                explicit_local = "/" in raw or PurePosixPath(raw).suffix == ".sty"
                dependency = resolve_latex_dependency(
                    root, paper, current, raw, (".sty",), required=explicit_local,
                    append_extension=True,
                )
                if dependency is not None:
                    paths.add(dependency.relative_to(root).as_posix())
                    pending.append(dependency)
        for _, groups, _ in _iter_latex_group_commands(
                text, r"documentclass|LoadClass(?:WithOptions)?", 1):
            raw = groups[0].strip()
            if not raw or any(token in raw for token in ("\\", "{", "}", "#")):
                raise EvidenceError(f"dynamic class dependency in {relative}: {raw!r}")
            explicit_local = "/" in raw or PurePosixPath(raw).suffix == ".cls"
            dependency = resolve_latex_dependency(
                root, paper, current, raw, (".cls",), required=explicit_local,
                append_extension=True,
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
                root, paper, current, raw, (".bst",), required=explicit_local,
                append_extension=True,
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


def derive_active_empirical_lineage(root: Path, result_paths: list[Path]
                                    ) -> dict[str, Any] | None:
    """Build one receipt-qualified graph for active empirical evidence."""
    registry, _ = load_registry(root)
    eligible_receipts = empirical_operand_eligible_receipts(root, registry)
    analyses: list[dict[str, Any]] = []
    elements: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    unclassified: list[str] = []
    baseline_digests: set[str] = set()
    definition_identities: dict[tuple[str, str], str] = {}
    for receipt_path_value in result_paths:
        receipt_raw = receipt_path_value.relative_to(root).as_posix()
        receipt = validate_receipt_contract(root, receipt_path_value)
        if receipt["receipt_version"] != EMPIRICAL_RECEIPT_VERSION:
            unclassified.append(receipt_raw)
            continue
        plan_path = receipt["producer_run"]["plan"]["path"]
        plan = validate_run_plan(load_json(root / plan_path), root)
        contracts, _ = validate_empirical_plan(root, plan, completed=True)
        extend_empirical_identity_index(
            contracts, definition_identities, scope="across active receipts"
        )
        validate_empirical_relationships(
            root, receipt_raw, plan, contracts,
            eligible_receipts=eligible_receipts,
        )
        bundle_path = receipt["producer_run"]["bundle"]["path"]
        bundle, _, _ = bundle_and_path(root, bundle_path)
        for item in receipt["lineage"]:
            baseline_digests.add(item["baseline_digest"])
            analysis = {"receipt": receipt_raw, **item}
            reference_id = contracts[item["analysis_id"]].get("reference_analysis_id")
            if reference_id is not None:
                analysis["reference"] = {
                    "receipt": receipt_raw, "analysis_id": reference_id,
                }
            analyses.append(analysis)
        for exhibit in bundle["exhibits"]:
            for element_id, result_ids in exhibit["elements"].items():
                elements.append({
                    "receipt": receipt_raw,
                    "exhibit_id": exhibit["id"],
                    "element_id": element_id,
                    "results": [
                        {"receipt": receipt_raw, "result_id": result_id}
                        for result_id in result_ids
                    ],
                })
        for analysis_id, contract in contracts.items():
            for result_id, output in contract["effective"]["outputs"].items():
                if "operands" in output:
                    comparisons.append({
                        "receipt": receipt_raw,
                        "analysis_id": analysis_id,
                        "result_id": result_id,
                        "operands": output["operands"],
                        "comparability": output["comparability"],
                    })
    if len(baseline_digests) > 1:
        raise EvidenceError(
            "active empirical receipts use multiple project baselines; complete the "
            "cumulative migration before paper audit"
        )
    state_path = root / "process_log/pipeline_state.json"
    if state_path.exists():
        state = load_json(state_path)
        stage3a = state.get("stage3a_result_receipt") if isinstance(state, dict) else None
        if stage3a is not None:
            if not isinstance(stage3a, str):
                raise EvidenceError("pipeline_state stage3a_result_receipt is malformed")
            if stage3a not in {path.relative_to(root).as_posix() for path in result_paths}:
                raise EvidenceError("pipeline_state stage3a_result_receipt is not active")
            pointed = load_json(root / stage3a)
            if pointed.get("receipt_version") != EMPIRICAL_RECEIPT_VERSION:
                raise EvidenceError(
                    "pipeline_state stage3a_result_receipt lacks empirical v3 lineage"
                )
    if not analyses:
        return None
    analyses.sort(key=lambda item: (item["receipt"], item["analysis_id"]))
    elements.sort(key=lambda item: (item["receipt"], item["exhibit_id"], item["element_id"]))
    comparisons.sort(key=lambda item: (item["receipt"], item["analysis_id"], item["result_id"]))
    return {
        "baseline_digest": next(iter(baseline_digests)),
        "analyses": analyses,
        "elements": elements,
        "comparisons": comparisons,
        "unclassified_receipts": sorted(unclassified),
    }


def validate_audit_input(root: Path, path: Path, checkpoint: str) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise EvidenceError("audit input must be an object")
    required = {"kind", "audit_input_version", "checkpoint", "paper_sources",
                "result_receipts", "results_registry", "citation_occurrences",
                "included_result_exhibits", "digest"}
    version = value.get("audit_input_version")
    allowed = required | ({"empirical_lineage"}
                          if version == EMPIRICAL_AUDIT_INPUT_VERSION else set())
    _require_keys(value, required, allowed, "audit input")
    if (value["kind"] != "paper_audit_input" or
            isinstance(value["audit_input_version"], bool) or
            version not in {AUDIT_INPUT_VERSION, EMPIRICAL_AUDIT_INPUT_VERSION}):
        raise EvidenceError("not a paper audit input v1/v2")
    if version == EMPIRICAL_AUDIT_INPUT_VERSION and "empirical_lineage" not in value:
        raise EvidenceError("paper audit input v2 requires empirical_lineage")
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
    recorded_receipts = [entry.get("path") for entry in value["result_receipts"]
                         if isinstance(entry, dict)]
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
    current_lineage = derive_active_empirical_lineage(
        root, [root / raw for raw in current_receipts]
    )
    if value.get("empirical_lineage") != current_lineage:
        failures.append("active empirical lineage changed after audit preparation")
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
    empirical_lineage = derive_active_empirical_lineage(root, result_paths)
    payload = {
        "kind": "paper_audit_input",
        "audit_input_version": (
            EMPIRICAL_AUDIT_INPUT_VERSION if empirical_lineage is not None
            else AUDIT_INPUT_VERSION
        ),
        "checkpoint": args.checkpoint,
        "paper_sources": fingerprint_many(root, paper_sources),
        "result_receipts": fingerprint_many(root, result_receipts),
        "results_registry": fingerprint(root, REGISTRY_PATH),
        "citation_occurrences": citation_occurrences,
        "included_result_exhibits": expected_result_exhibits(
            root, result_paths, paper_sources
        ),
    }
    if empirical_lineage is not None:
        payload["empirical_lineage"] = empirical_lineage
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
        raw_lines = [
            line.strip()
            for line in read_utf8(path, f"{label} audit report").splitlines()
        ]
        lines = [line for line in raw_lines if line]
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"cannot read {label} audit report: {exc}") from exc
    expected = ["VERDICT: PASS", f"CHECKPOINT: {checkpoint}",
                f"AUDIT_INPUT_DIGEST: {audit_input_digest}"]
    marker_values = {"VERDICT": [], "CHECKPOINT": [], "AUDIT_INPUT_DIGEST": []}
    prefix_re = re.compile(
        r"^(?:>\s*|#{1,6}\s+|[-+*]\s+|\d+[.)]\s+|\[[ xX]\]\s+)"
    )

    def strip_markdown_prefixes(line: str) -> str:
        candidate = line.strip()
        while True:
            stripped = prefix_re.sub("", candidate, count=1)
            if stripped == candidate:
                return candidate
            candidate = stripped.strip()

    def normalized_marker_label(raw: str) -> str:
        candidate = re.sub(r"\s+#+\s*$", "", raw.strip())
        candidate = candidate.strip("*_` ")
        candidate = candidate.rstrip(":").strip().strip("*_` ")
        return re.sub(r"\s+", "_", candidate.upper())

    def markdown_table_cells(line: str) -> list[str] | None:
        candidate = strip_markdown_prefixes(line)
        if "|" not in candidate:
            return None
        has_outer_pipe = candidate.startswith("|") or candidate.endswith("|")
        if candidate.startswith("|"):
            candidate = candidate[1:]
        if candidate.endswith("|"):
            candidate = candidate[:-1]
        cells = [cell.strip() for cell in candidate.split("|")]
        return cells if len(cells) >= 2 or (has_outer_pipe and len(cells) == 1) else None

    def is_table_separator(cells: list[str] | None) -> bool:
        return bool(cells) and all(
            re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) is not None
            for cell in cells
        )

    def markdown_label_value(line: str) -> tuple[str, str] | None:
        candidate = strip_markdown_prefixes(line)
        label, separator, value = candidate.partition(":")
        if not separator:
            return None
        normalized_label = normalized_marker_label(label)
        if normalized_label not in marker_values:
            return None
        return normalized_label, value.strip().strip("*_` ")

    for line in lines:
        marker = markdown_label_value(line)
        if marker is not None:
            marker_values[marker[0]].append(marker[1])

    def record_horizontal_table_markers(row: list[str]) -> None:
        for column, cell in enumerate(row[:-1]):
            key = normalized_marker_label(cell)
            if key in marker_values:
                marker_values[key].append(row[column + 1].strip("*_` "))

    # Parse every adjacent GFM header/delimiter pair rather than assuming a
    # pipe-containing run begins at its header: CommonMark permits a table to
    # interrupt a preceding pipe-bearing paragraph without a blank line.
    for line_index, raw_line in enumerate(raw_lines):
        cells = markdown_table_cells(raw_line)
        if cells is None or is_table_separator(cells):
            continue
        next_cells = (
            markdown_table_cells(raw_lines[line_index + 1])
            if line_index + 1 < len(raw_lines)
            else None
        )
        if is_table_separator(next_cells):
            marker_columns = [
                (column, normalized_marker_label(cell))
                for column, cell in enumerate(cells)
                if normalized_marker_label(cell) in marker_values
            ]
            body_rows: list[list[str]] = []
            body_index = line_index + 2
            while body_index < len(raw_lines) and raw_lines[body_index]:
                body_cells = markdown_table_cells(raw_lines[body_index])
                if body_cells is None or is_table_separator(body_cells):
                    break
                body_rows.append(body_cells)
                body_index += 1
            if body_rows:
                for row in body_rows:
                    for column, key in marker_columns:
                        value = row[column] if column < len(row) else ""
                        marker_values[key].append(value.strip("*_` "))
            else:
                for column, key in marker_columns:
                    value = cells[column + 1] if column + 1 < len(cells) else ""
                    marker_values[key].append(value.strip("*_` "))
        else:
            record_horizontal_table_markers(cells)
    if (lines[:3] != expected or marker_values["VERDICT"] != ["PASS"] or
            marker_values["CHECKPOINT"] != [checkpoint] or
            marker_values["AUDIT_INPUT_DIGEST"] != [audit_input_digest]):
        raise EvidenceError(
            f"{label} audit report must contain one consistent PASS/checkpoint/digest header"
        )
    heading_expected = {
        "VERDICT": "PASS",
        "CHECKPOINT": checkpoint,
        "AUDIT_INPUT_DIGEST": audit_input_digest,
    }
    for index, line in enumerate(lines):
        candidate = strip_markdown_prefixes(line)
        key = normalized_marker_label(candidate)
        if ":" in candidate or key not in heading_expected:
            continue
        if index + 1 >= len(lines):
            raise EvidenceError(f"{label} audit report contains a conflicting {key.lower()}")
        next_value = strip_markdown_prefixes(lines[index + 1]).strip("*_` ")
        matches = (next_value.upper() == "PASS" if key == "VERDICT"
                   else next_value == heading_expected[key])
        if not matches:
            raise EvidenceError(f"{label} audit report contains a conflicting {key.lower()}")


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
                              expected_occurrences: list[dict[str, Any]]) -> None:
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
    fresh = 0
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
        if (not isinstance(claim["status"], str) or
                claim["status"] not in {"FAITHFUL", "TOPICAL"}):
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
        else:
            raise EvidenceError(f"{where}.verification must be fresh")
    for key in ("fresh_checks", "reused_bound_checks"):
        if isinstance(value[key], bool) or not isinstance(value[key], int) or value[key] < 0:
            raise EvidenceError(f"{key} must be a non-negative integer")
    if value["fresh_checks"] + value["reused_bound_checks"] != len(claims):
        raise EvidenceError(
            "fresh_checks + reused_bound_checks must equal citation_claims length"
        )
    if value["fresh_checks"] != fresh or value["reused_bound_checks"] != 0:
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
    audit_artifacts = {
        audit_input_raw, summary_raw, report_raw,
        citation_summary_raw, citation_report_raw,
    }
    if len(audit_artifacts) != 5:
        raise EvidenceError(
            "audit input, evidence summary/report, and citation summary/report "
            "must be five distinct files"
        )
    audit_identities: list[tuple[int, int]] = []
    for path in (audit_input_path, summary_path, report_path,
                 citation_summary_path, citation_report_path):
        descriptor = _open_regular_read(path)
        try:
            info = os.fstat(descriptor)
            audit_identities.append((info.st_dev, info.st_ino))
        finally:
            os.close(descriptor)
    if len(set(audit_identities)) != 5:
        raise EvidenceError(
            "audit input, evidence summary/report, and citation summary/report "
            "must be five distinct file identities"
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
    validate_citation_summary(
        load_json(citation_summary_path), args.checkpoint,
        audit_input_raw, audit_input["digest"], audit_input["citation_occurrences"]
    )
    validate_audit_report(citation_report_path, args.checkpoint, audit_input["digest"],
                          "citation")
    discovered_receipts = [path.relative_to(root).as_posix() for path in result_paths]
    if sorted(checked_receipts) != sorted(discovered_receipts):
        raise EvidenceError(
            "evidence audit receipt inventory does not match discovered result receipts"
        )
    _, target = receipt_path(root, PAPER_RECEIPT_PATH)
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
    expected_keys = {
        "kind", "receipt_version", "checkpoint", "audit_input", "audit_summary",
        "audit_report", "citation_audit_summary", "citation_audit_report",
        "results_registry", "paper_sources", "result_receipts",
    }
    if set(receipt) != expected_keys:
        raise EvidenceError("paper-evidence receipt has unexpected or missing keys")
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
    def validate_bound_audits() -> list[str]:
        checkpoint = receipt.get("checkpoint")
        if not isinstance(checkpoint, str) or not checkpoint:
            raise EvidenceError("paper receipt checkpoint must be a non-empty string")
        audit_input_raw = receipt["audit_input"]["path"]
        audit_input = validate_audit_input(root, root / audit_input_raw, checkpoint)
        for key in ("results_registry", "paper_sources", "result_receipts"):
            if receipt[key] != audit_input[key]:
                raise EvidenceError(
                    f"paper receipt {key} inventory differs from its bound audit input"
                )
        checked = validate_evidence_summary(
            load_json(root / receipt["audit_summary"]["path"]), checkpoint,
            audit_input_raw, audit_input["digest"],
            audit_input["included_result_exhibits"],
        )
        validate_audit_report(
            root / receipt["audit_report"]["path"], checkpoint,
            audit_input["digest"], "evidence",
        )
        citation_value = load_json(root / receipt["citation_audit_summary"]["path"])
        validate_citation_summary(
            citation_value, checkpoint, audit_input_raw, audit_input["digest"],
            audit_input["citation_occurrences"],
        )
        validate_audit_report(
            root / receipt["citation_audit_report"]["path"], checkpoint,
            audit_input["digest"], "citation",
        )
        expected = sorted(entry["path"] for entry in audit_input["result_receipts"])
        if sorted(checked) != expected:
            raise EvidenceError(
                "evidence audit receipt inventory does not match bound result receipts"
            )
        return expected

    bound_result_paths: list[str] = []
    if not failures:
        try:
            bound_result_paths = validate_bound_audits()
        except (EvidenceError, KeyError, TypeError) as exc:
            failures.append(f"audit semantics: {exc}")
    if not failures:
        for raw in bound_result_paths:
            _, result_path = project_path(root, raw)
            report = verify_receipt(root, result_path, rerender=rerender)
            failures.extend(f"{raw}: {failure}" for failure in report["failures"])
    if not failures and rerender:
        if not failures:
            for key in ("audit_input", "audit_summary", "audit_report",
                        "citation_audit_summary", "citation_audit_report",
                        "results_registry", "paper_sources", "result_receipts"):
                value = receipt[key]
                entries = [value] if key in audit_fields else value
                failures.extend(compare_snapshot(root, entries, f"post-render {key}"))
        if not failures:
            try:
                validate_bound_audits()
            except (EvidenceError, KeyError, TypeError) as exc:
                failures.append(f"post-render audit semantics: {exc}")
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
    run.set_defaults(empirical=False)
    run.set_defaults(func=command_run)

    run_empirical = subparsers.add_parser(
        "run-empirical",
        help="execute empirical analysis with contracts and realization summaries",
    )
    run_empirical.add_argument("--project-root", default=".")
    run_empirical.add_argument("--plan", required=True)
    run_empirical.add_argument("--bundle", required=True)
    run_empirical.add_argument("--receipt", required=True)
    run_empirical.add_argument("--supersedes", action="append", default=[])
    run_empirical.add_argument("command", nargs=argparse.REMAINDER)
    run_empirical.set_defaults(func=command_run, empirical=True)

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

    activate_pair = subparsers.add_parser(
        "activate-pair",
        help="atomically activate one bound data-first analysis/release receipt pair",
    )
    activate_pair.add_argument("--project-root", default=".")
    activate_pair.add_argument("--analysis-receipt", required=True)
    activate_pair.add_argument("--release-receipt", required=True)
    activate_pair.set_defaults(func=command_activate_pair)

    retire_pair = subparsers.add_parser(
        "retire-pair",
        help="atomically retire one pending or active data-first receipt pair",
    )
    retire_pair.add_argument("--project-root", default=".")
    retire_pair.add_argument("--analysis-receipt", required=True)
    retire_pair.add_argument("--release-receipt", required=True)
    retire_pair.add_argument("--reason", required=True)
    retire_pair.add_argument("--superseded-by-analysis")
    retire_pair.add_argument("--superseded-by-release")
    retire_pair.set_defaults(func=command_retire_pair)

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

    validate_receipt_parser = subparsers.add_parser(
        "validate-receipt", help="validate immutable receipt structure without requiring live sources"
    )
    validate_receipt_parser.add_argument("--project-root", default=".")
    validate_receipt_parser.add_argument("--receipt", required=True)
    validate_receipt_parser.add_argument(
        "--read-only", action="store_true",
        help="validate without creating a project lock or recovering transactions",
    )
    validate_receipt_parser.set_defaults(func=command_validate_receipt)

    inspect_registry = subparsers.add_parser(
        "inspect-registry",
        help="validate registry/receipts and return selected lifecycle ownership metadata",
    )
    inspect_registry.add_argument("--project-root", default=".")
    inspect_registry.add_argument("--artifact-prefix", required=True)
    inspect_registry.set_defaults(func=command_inspect_registry)

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
    verify_paper.add_argument(
        "--read-only", action="store_true",
        help="verify without creating the project lock or recovering transactions",
    )
    verify_paper.set_defaults(func=command_verify_paper)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.subcommand in {"run", "run-empirical", "render"}:
        # Printed immediately (and unbuffered) so a caller that kills this
        # process on a short tool timeout still captures the explanation.
        # Child output is intentionally buffered until completion, so interim
        # silence is normal while the run is healthy (#293).
        print(
            f"[results_pipeline] {args.subcommand}: this trusted execution can "
            "take many minutes (networked acquisition builds routinely need "
            "20+). Launch it via a harness-tracked long-allowance job and "
            "poll to terminal status — a short synchronous tool call will "
            "kill it mid-run and discard the whole isolated workspace. "
            "Interim silence is normal: child output is released only at "
            "completion.",
            file=sys.stderr,
            flush=True,
        )
    try:
        root = resolve_root(args.project_root)
        if args.subcommand == "inspect-registry":
            with project_read_lock(root):
                reject_unresolved_transaction(root)
                return args.func(args)
        if args.subcommand in {"verify-paper", "validate-receipt"} and args.read_only:
            if getattr(args, "rerender", False):
                raise EvidenceError("--read-only cannot be combined with --rerender")
            return args.func(args)
        if args.subcommand == "init-registry":
            _, process_log = project_path(root, "process_log", must_exist=False)
            if not process_log.exists():
                ensure_directory_durable(process_log)
                process_log.chmod(0o700)
                fsync_directory(process_log)
        with project_lock(root):
            recover_transaction(root)
            return args.func(args)
    except EvidenceError as exc:
        print(f"results_pipeline: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
