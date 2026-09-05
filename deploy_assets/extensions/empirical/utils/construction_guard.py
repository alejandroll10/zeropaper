#!/usr/bin/env python3
"""Mechanically check that a result receipt's tabular artifacts carry evidence
of having been derived from the inputs the receipt fingerprinted.

Every other Stage 3a gate checks artifact *form*: the receipt verifies, the
bundle re-renders, the clean-room rebuild reproduces digests, the headline
replicator recomputes one to five tagged numbers. None of them looks at whether
the other rows were derived from anything at all. A ledger whose per-row
provenance fields are constant placeholders satisfies the entire receipt chain,
and the only thing that catches it is the empirics audit, after a full build.

The ground truth here is the receipt itself. `results_pipeline.py` fingerprints
every declared producer input, recording a SHA-256 for each regular file inside
a declared directory. So the digest of everything the producer read is already
recorded, mechanically, by a trusted component the producer does not author,
and a row that names one of those inputs can be held to it: the content digest
that row claims must be the digest of the input that row names. That check
needs no schema, no vocabulary, and no second agent.

Only DECLARED PRODUCER INPUTS bind. The producer's own code, renderer, plan,
bundle, and output artifacts are things it authored or emitted, so a row naming
one of those and quoting its digest shows nothing about deriving anything from
a source, and must not collect the verdict reserved for real binding. A bare
name shared by two declared inputs does not bind either, since the name cannot
say which file the row meant.

Note what binding is *not*: a test that the claimed digest appears somewhere in
the receipt. Set membership is the weaker fallback, used only where a row names
no declared input, and a column checkable only that way is reported as a warning
rather than a pass.

What the binding actually forces is that the producer opened and hashed the file
each row names. It cannot read the digests out of the receipt: the trusted runner
fingerprints and writes the receipt only after the producer has exited. The one
exception is a producer that declares an *earlier* receipt as an input, which the
data-first release run does by design -- see LIMITATIONS.md.

What this module deliberately does NOT do
-----------------------------------------
It does not attempt regex byte-evidence ("the bytes at the row's stated
locator match a pattern the spec expects there"). An independent adversarial
review of that check found it forces very little work: a ~30-line script that
scans each source document for the spec regex, takes the first match's span,
and pairs it with an honestly computed digest satisfies it on 98% of documents
in 0.12s, with most matches landing in page furniture shared verbatim across
unrelated documents. Rejecting matches inside `<head>` and flagging byte spans
reused across rows defeats that particular script and nothing more general.
The residual guarantee -- *some* span in the right document matched *some*
pattern -- is not worth the spec machinery it costs. See LIMITATIONS.md.

More generally: passing this guard means the artifact carries evidence of
having been derived from the receipt's inputs. It does not mean the derivation
is correct, and it is not a proof of derivation. A producer willing to spend
real effort defeats every check here. The point is narrower and still worth
having: the cheap fabrication modes -- constant placeholder fills, prose tokens
in locator fields, content hashes that match nothing -- become cheap to detect,
seconds of local computation instead of a full build plus an LLM audit. The
empirics audit still owns correctness.

Never imports, executes, or trusts analyzed producer code.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable


SCHEMA_VERSION = 1

# A column is treated as carrying content digests once this share of its
# non-empty cells parse as one. Below it, digest-shaped cells are incidental.
DIGEST_COLUMN_SHARE = 0.5
# A constant *_locator column is a construction failure rather than a warning
# only once there are enough rows for constancy to be unambiguous.
LOCATOR_CONSTANCY_ROWS = 10
# A column self-selects as a source reference once this share of its distinct
# values resolves to a declared input; below it, a lone coincidental match in
# a free-text column must not turn the whole column into a failure.
PATH_COLUMN_SHARE = 0.5
# Artifacts larger than this are refused rather than silently skipped.
DEFAULT_MAX_BYTES = 512 * 1024 * 1024

DIGEST_CELL = re.compile(r"(?:sha256:)?([0-9a-f]{64})\Z")
RECORDED_DIGEST = re.compile(r"sha256:([0-9a-f]{64})\Z")
LOCATOR_TOKENS = {"locator", "locators"}
CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
NAME_SEPARATOR = re.compile(r"[^A-Za-z0-9]+")
LOCATOR_SEPARATORS = set(":#@/")
DELIMITERS = {".csv": ",", ".tsv": "\t", ".psv": "|"}


class GuardError(RuntimeError):
    """A receipt or artifact is missing, unreadable, or malformed."""


def _load_json(path: Path) -> Any:
    try:
        # utf-8-sig: a byte-order mark must not abort the run before any check.
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise GuardError(f"cannot read {path}: {exc}") from exc
    try:
        return json.loads(text)
    except ValueError as exc:
        raise GuardError(f"{path} is not valid JSON: {exc}") from exc


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise GuardError(f"cannot fingerprint {path}: {exc}") from exc
    return digest.hexdigest()


def _recorded_digest(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = RECORDED_DIGEST.fullmatch(value)
    return match.group(1) if match else None


def _snapshot_files(record: Any) -> list[tuple[str, str]]:
    """Return (project-relative path, bare hex digest) for one fingerprint record.

    A file record contributes itself. A directory record contributes its own
    manifest digest under the directory path plus every regular file inside it.
    """
    if not isinstance(record, dict):
        raise GuardError("receipt fingerprint record is not an object")
    raw = record.get("path")
    if not isinstance(raw, str) or not raw:
        raise GuardError("receipt fingerprint record has no path")
    digest = _recorded_digest(record.get("sha256"))
    if digest is None:
        raise GuardError(f"receipt fingerprint for {raw} has no usable digest")
    found = [(raw, digest)]
    if record.get("kind") == "directory":
        entries = record.get("entries")
        if not isinstance(entries, list):
            raise GuardError(f"receipt directory fingerprint {raw} has no entries")
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("kind") != "file":
                continue
            entry_path = entry.get("path")
            entry_digest = _recorded_digest(entry.get("sha256"))
            if not isinstance(entry_path, str) or entry_digest is None:
                raise GuardError(f"malformed directory entry under {raw}")
            found.append((f"{raw}/{entry_path}", entry_digest))
    return found


def _project_file(root: Path, relative: str) -> Path:
    """Resolve a receipt-declared path, refusing anything outside the project.

    The trusted runner normalizes and rejects escaping paths before it writes a
    receipt, so this cannot trigger on a receipt that runner produced. The guard
    reads receipts as untrusted input anyway: it is the component that would be
    handed a hand-edited one.
    """
    parts = PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or any(
            part in {"", ".", ".."} for part in parts):
        raise GuardError(f"receipt declares a path outside the project: {relative}")
    return root.joinpath(*parts)


def _reference_map(files: list[tuple[str, str]]) -> tuple[dict[str, str], set[str]]:
    """Names that identify exactly one fingerprinted file, and those that do not.

    Built in two passes so the result cannot depend on the order the receipt
    happens to list its records: whether a name is ambiguous is a fact about the
    name, not about where it appears.
    """
    references: dict[str, str] = {}
    ambiguous: set[str] = set()
    by_path: dict[str, set[str]] = {}
    by_basename: dict[str, set[str]] = {}
    for path, digest in files:
        by_path.setdefault(path, set()).add(digest)
        by_basename.setdefault(PurePosixPath(path).name, set()).add(digest)
    for path, digests in by_path.items():
        # Two records declaring one path with different digests cannot both be
        # right, and silently keeping either would make binding depend on order.
        if len(digests) == 1:
            references[path] = next(iter(digests))
        else:
            ambiguous.add(path)
    for basename, digests in by_basename.items():
        if basename in by_path:
            continue
        if len(digests) == 1:
            references[basename] = next(iter(digests))
        else:
            ambiguous.add(basename)
    return references, ambiguous


def _producer_run(receipt: Any) -> dict[str, Any]:
    if not isinstance(receipt, dict):
        raise GuardError("receipt is not an object")
    producer = receipt.get("producer_run")
    if not isinstance(producer, dict):
        raise GuardError("receipt has no producer_run")
    return producer


def receipt_evidence(receipt: Any) -> dict[str, Any]:
    """Collect the digest and path universe the receipt itself vouches for."""
    producer = _producer_run(receipt)
    sections: dict[str, list[tuple[str, str]]] = {}
    for key in ("inputs", "code", "renderer_code", "artifacts"):
        values = producer.get(key)
        if values is None:
            sections[key] = []
            continue
        if not isinstance(values, list):
            raise GuardError(f"producer_run.{key} is not an array")
        collected: list[tuple[str, str]] = []
        for record in values:
            collected.extend(_snapshot_files(record))
        sections[key] = collected
    for key in ("plan", "bundle"):
        record = producer.get(key)
        sections[key] = _snapshot_files(record) if isinstance(record, dict) else []

    digests: set[str] = set()
    for collected in sections.values():
        for _path, digest in collected:
            digests.add(digest)

    # Binding targets are the DECLARED INPUTS -- and, separately, this receipt's
    # own OUTPUT ARTIFACTS, tracked apart from them. The producer's code, plan,
    # and bundle bind to nothing: a row naming one of those and quoting its
    # digest demonstrates nothing about deriving anything from a source, and
    # would collect the strong row-scoped verdict for doing so.
    #
    # Artifacts are kept as their own universe because a producer controls its
    # own outputs' bytes. A row may legitimately name an artifact and quote that
    # artifact's digest -- that is what a release manifest is -- but it earns a
    # different, weaker label than binding to a source, and it still has to name
    # the specific artifact whose digest it quotes.
    input_files: list[tuple[str, str]] = []
    for record in producer.get("inputs") if isinstance(producer.get("inputs"), list) else []:
        collected = _snapshot_files(record)
        # A directory is not a binding target; its files are.
        input_files.extend(collected[1:] if record.get("kind") == "directory" else collected)
    artifact_files: list[tuple[str, str]] = []
    for record in producer.get("artifacts") if isinstance(producer.get("artifacts"), list) else []:
        collected = _snapshot_files(record)
        artifact_files.extend(
            collected[1:] if record.get("kind") == "directory" else collected
        )
    reference_digests, ambiguous = _reference_map(input_files)
    artifact_references, artifact_ambiguous = _reference_map(artifact_files)

    input_groups: list[tuple[str, list[tuple[str, str]]]] = []
    for record in producer.get("inputs") if isinstance(producer.get("inputs"), list) else []:
        collected = _snapshot_files(record)
        # A file record is a group of one; without this it would contribute no
        # coverage finding at all, so nothing would report that a declared input
        # file is cited by no row.
        input_groups.append((
            collected[0][0],
            collected[1:] if record.get("kind") == "directory" else collected,
        ))
    return {
        "sections": sections,
        "input_groups": input_groups,
        "reference_digests": reference_digests,
        "artifact_references": artifact_references,
        "ambiguous_references": sorted(ambiguous),
        "ambiguous_artifact_references": sorted(artifact_ambiguous),
        "digests": digests,
    }


def _artifact_targets(producer: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    """Every regular file the receipt declares as a producer artifact."""
    targets: list[dict[str, Any]] = []
    values = producer.get("artifacts")
    if not isinstance(values, list):
        raise GuardError("producer_run.artifacts is not an array")
    for record in values:
        if not isinstance(record, dict):
            raise GuardError("producer_run.artifacts entry is not an object")
        raw = record.get("path")
        if not isinstance(raw, str):
            raise GuardError("producer_run.artifacts entry has no path")
        if record.get("kind") == "file":
            targets.append({"path": raw, "sha256": _recorded_digest(record.get("sha256"))})
            continue
        for entry_path, entry_digest in _snapshot_files(record)[1:]:
            targets.append({"path": entry_path, "sha256": entry_digest})
    for target in targets:
        target["absolute"] = _project_file(root, target["path"])
    return targets


def read_rows(path: Path, max_bytes: int) -> tuple[list[str], list[list[str]]] | None:
    """Normalize a delimited or JSON-lines artifact into a header plus rows.

    Returns None for anything this guard cannot read as a table, which is not
    an error: figures, bundles, and prose reports are simply out of scope.
    """
    suffix = path.suffix.lower()
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise GuardError(f"cannot stat {path}: {exc}") from exc
    if size > max_bytes:
        raise GuardError(
            f"{path} is {size} bytes, above the {max_bytes}-byte guard limit; "
            "raise --max-bytes deliberately rather than skipping the check"
        )
    if suffix in {".jsonl", ".ndjson"}:
        return _read_json_lines(path)
    if suffix == ".json":
        return _read_json_table(path)
    if suffix not in DELIMITERS:
        return None
    try:
        # utf-8-sig so a byte-order mark does not become part of the first
        # column's name and hide that column from every check below.
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, delimiter=DELIMITERS[suffix])
            try:
                header = next(reader)
            except StopIteration:
                return None
            rows = [row for row in reader if row]
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        raise GuardError(f"cannot read {path} as a table: {exc}") from exc
    if not header or not any(name.strip() for name in header):
        return None
    return header, rows


def _rows_from_objects(records: list[Any]) -> tuple[list[str], list[list[str]]] | None:
    header: list[str] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            return None
        for key in record:
            if isinstance(key, str) and key not in seen:
                seen.add(key)
                header.append(key)
    if len(header) < 2:
        return None
    rows: list[list[str]] = []
    for record in records:
        rows.append([
            "" if record.get(key) is None else str(record.get(key, ""))
            for key in header
        ])
    return header, rows


def _read_json_lines(path: Path) -> tuple[list[str], list[list[str]]] | None:
    records: list[Any] = []
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(json.loads(line))
                except ValueError as exc:
                    raise GuardError(f"{path} line {number} is not valid JSON: {exc}") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise GuardError(f"cannot read {path}: {exc}") from exc
    return _rows_from_objects(records) if records else None


def _read_json_table(path: Path) -> tuple[list[str], list[list[str]]] | None:
    value = _load_json(path)
    if not isinstance(value, list) or not value:
        return None
    return _rows_from_objects(value)


def _columns(header: list[str], rows: list[list[str]]
             ) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Column values keyed by name, with repeated names kept rather than dropped.

    Silently keeping only the first of two same-named columns would exempt the
    second from every check below, which is a free bypass for anything willing
    to emit a duplicate header.
    """
    columns: dict[str, list[str]] = {}
    seen: dict[str, int] = {}
    for index, name in enumerate(header):
        occurrence = seen.get(name, 0) + 1
        seen[name] = occurrence
        key = name if occurrence == 1 else f"{name}#{occurrence}"
        columns[key] = [row[index] if index < len(row) else "" for row in rows]
    duplicates = {name: count for name, count in seen.items() if count > 1}
    return columns, duplicates


def _names_a_locator(name: str) -> bool:
    """Whether a word of this column's name is literally `locator`.

    An exact name token is the shape the field failure had
    (`operative_decision_locator`), and it is the only shape where constancy is
    unambiguous enough to hard-fail. Matching the substring instead would fail
    `capital_allocator_id` and `translocator_id` — ordinary columns that can be
    legitimately constant — and excluding those by name needs a list of words
    containing `locator` that could never be complete. A guard that fails honest
    work gets switched off, so this is the safe direction.

    The cost is a name like `decisionlocator` or `decision_locater`, which
    escapes to the name-blind constant-column warning rather than stopping the
    build. That residual is recorded in LIMITATIONS.md.
    """
    spaced = CAMEL_BOUNDARY.sub(" ", name)
    tokens = {token.casefold() for token in NAME_SEPARATOR.split(spaced) if token}
    return bool(tokens & LOCATOR_TOKENS)


def _finding(check: str, status: str, **detail: Any) -> dict[str, Any]:
    finding = {"check": check, "status": status}
    finding.update(detail)
    return finding


def _reference_columns(columns: dict[str, list[str]], evidence: dict[str, Any]
                       ) -> dict[str, list[str]]:
    """Columns that name declared inputs or this receipt's own artifacts.

    A column self-selects: a lone coincidental match in a free-text column must
    not turn that column into a source reference and fail everything else in it.
    """
    known = evidence["reference_digests"].keys() | evidence["artifact_references"].keys()
    selected: dict[str, list[str]] = {}
    for name, values in columns.items():
        present = [value.strip() for value in values if value.strip()]
        if not present:
            continue
        distinct = set(present)
        resolved = distinct & known
        if resolved and len(resolved) >= PATH_COLUMN_SHARE * len(distinct):
            selected[name] = values
    return selected


def _row_reference_digests(reference_columns: dict[str, list[str]],
                           evidence: dict[str, Any], row_count: int
                           ) -> tuple[list[set[str]], list[set[str]]]:
    """Per row, the digests of the inputs and of the artifacts that row names."""
    from_inputs: list[set[str]] = [set() for _ in range(row_count)]
    from_artifacts: list[set[str]] = [set() for _ in range(row_count)]
    for values in reference_columns.values():
        for index, value in enumerate(values):
            if index >= row_count:
                break
            name = value.strip()
            digest = evidence["reference_digests"].get(name)
            if digest is not None:
                from_inputs[index].add(digest)
            digest = evidence["artifact_references"].get(name)
            if digest is not None:
                from_artifacts[index].add(digest)
    return from_inputs, from_artifacts


def check_digest_provenance(
    artifact: str, columns: dict[str, list[str]], evidence: dict[str, Any],
    derived_scopes: set[str], row_inputs: list[set[str]], row_artifacts: list[set[str]],
) -> list[dict[str, Any]]:
    """A claimed content digest must be the digest of a source the row names.

    Membership in the receipt's whole digest set is the weaker fallback, used
    only where a row names no source this receipt declares. It has to be the
    fallback rather than the rule: every fingerprinted digest sits in the
    receipt as plaintext, so satisfying a set-membership test costs a producer
    one copy-paste and no hashing at all. Binding the digest to the row's own
    reference is what makes the claim cost something to make.

    The column self-selects by value shape, not by name, and that is deliberate:
    name-gating would let a producer escape the check by renaming the column.
    """
    findings: list[dict[str, Any]] = []
    for name, values in columns.items():
        present = [value.strip() for value in values if value.strip()]
        if not present:
            continue
        claimed = [
            (index, match.group(1))
            for index, value in enumerate(values)
            if value.strip() and (match := DIGEST_CELL.fullmatch(value.strip()))
        ]
        if not claimed or len(claimed) < DIGEST_COLUMN_SHARE * len(present):
            continue

        bound_to_input = 0
        bound_to_artifact = 0
        named_input = 0
        named_artifact = 0
        unbound: list[str] = []
        unresolved: set[str] = set()
        fallback = 0
        for index, digest in claimed:
            inputs = row_inputs[index] if index < len(row_inputs) else set()
            artifacts = row_artifacts[index] if index < len(row_artifacts) else set()
            named_input += bool(inputs)
            named_artifact += bool(artifacts)
            if inputs or artifacts:
                if digest in inputs:
                    bound_to_input += 1
                elif digest in artifacts:
                    bound_to_artifact += 1
                else:
                    unbound.append(digest)
            else:
                # The row names nothing this receipt declares, so the only check
                # left is membership in its digest set — a weaker claim.
                fallback += 1
                if digest not in evidence["digests"]:
                    unresolved.add(digest)

        if fallback == len(claimed):
            binding = "set-membership"
        elif fallback:
            binding = "partial"
        else:
            # Classify by what the digests actually bound to, not by what the
            # rows merely mentioned: a row naming both an input and an artifact
            # while binding only to the artifact is a manifest row, and calling
            # the column `mixed` would tell the audit it contains provenance
            # rows that are not there. Where nothing bound at all there is no
            # binding to describe, so fall back to what the rows named.
            if bound_to_input or bound_to_artifact:
                from_sources, from_artifacts = bound_to_input, bound_to_artifact
            else:
                from_sources, from_artifacts = named_input, named_artifact
            if not from_artifacts:
                binding = "row-scoped"
            elif not from_sources:
                # Every row quotes the digest of one of this receipt's own
                # outputs: a manifest of the build, not a provenance claim.
                binding = "self-manifest"
            else:
                binding = "mixed"
        detail = {
            "artifact": artifact,
            "column": name,
            "binding": binding,
            "digest_cells": len(claimed),
            "rows_bound_to_their_own_source": bound_to_input,
            "rows_bound_to_an_own_artifact": bound_to_artifact,
            "rows_naming_nothing_declared": fallback,
            "mismatched_examples": sorted(set(unbound))[:5],
            "unresolved_examples": sorted(unresolved)[:5],
            "non_digest_cells": len(present) - len(claimed),
        }
        if not unbound and not unresolved:
            if binding == "row-scoped":
                findings.append(_finding("claimed-digest-provenance", "PASS", **detail))
            elif binding == "self-manifest":
                findings.append(_finding(
                    "claimed-digest-provenance", "PASS",
                    note="every row names one of this receipt's own artifacts and "
                         "quotes that artifact's digest — a manifest of the build "
                         "rather than a provenance claim about any source",
                    **detail,
                ))
            elif binding == "mixed":
                findings.append(_finding(
                    "claimed-digest-provenance", "PASS",
                    note="every row is bound to something it names; some rows name a "
                         "declared input and others name one of this receipt's own "
                         "artifacts, so the column mixes provenance and manifest rows",
                    **detail,
                ))
            else:
                # Set membership is satisfiable by copying a digest out of the
                # receipt, so a column that could only be checked that way has
                # not earned a clean pass; say so rather than imply the stronger
                # guarantee was tested.
                findings.append(_finding(
                    "claimed-digest-provenance", "WARN",
                    note=("no row names anything this receipt declares, so the digests "
                          if binding == "set-membership" else
                          "some rows name nothing this receipt declares, so those digests "
                          ) +
                         "were checked only for membership in the receipt's digest set — "
                         "a weaker claim than being the digest of the source the row names",
                    **detail,
                ))
        elif f"{artifact}:{name}" in derived_scopes or name in derived_scopes:
            findings.append(_finding(
                "claimed-digest-provenance", "WARN",
                note="column declared as carrying derived digests; neither binding "
                     "to the row's source nor receipt membership is required",
                **detail,
            ))
        elif unbound:
            findings.append(_finding(
                "claimed-digest-provenance", "FAIL",
                note="rows claim a content digest that is not the digest of the "
                     "source those rows name; if the specification says this column "
                     "hashes derived content, that is what --digest-scope declares",
                **detail,
            ))
        else:
            findings.append(_finding(
                "claimed-digest-provenance", "FAIL",
                note="digests claimed for content the producer never hashed; if the "
                     "specification says this column hashes derived content, that is "
                     "what --digest-scope declares",
                **detail,
            ))
    return findings


def check_path_provenance(
    artifact: str, reference_columns: dict[str, list[str]], evidence: dict[str, Any]
) -> list[dict[str, Any]]:
    """A column that names receipt-declared inputs must name only those."""
    findings: list[dict[str, Any]] = []
    known = evidence["reference_digests"].keys() | evidence["artifact_references"].keys()
    for name, values in reference_columns.items():
        distinct = sorted({value.strip() for value in values if value.strip()})
        unresolved = [value for value in distinct if value not in known]
        detail = {
            "artifact": artifact,
            "column": name,
            "distinct_referenced": len(distinct),
            "resolved": len(distinct) - len(unresolved),
            "unresolved_examples": unresolved[:5],
        }
        if unresolved:
            findings.append(_finding(
                "source-reference-resolution", "FAIL",
                note="rows cite sources absent from the receipt's declared inputs "
                     "and artifacts",
                **detail,
            ))
        else:
            findings.append(_finding("source-reference-resolution", "PASS", **detail))
    return findings


def check_column_degeneracy(
    artifact: str, columns: dict[str, list[str]], row_count: int
) -> list[dict[str, Any]]:
    """Empty and constant columns.

    Both are warnings, never failures. Constant-ness is legitimate on an
    all-success outcome column, and an optional field can honestly be empty
    throughout; a guard that fails those gets switched off the first day. Only
    the binding specification knows which columns promised a vocabulary, and
    the producer must not be the one to say. These are forwarded to the audit
    as attention, not routed as construction failures.
    """
    findings: list[dict[str, Any]] = []
    if row_count < 2:
        return findings
    for name, values in columns.items():
        present = [value.strip() for value in values if value.strip()]
        if not present:
            findings.append(_finding(
                "empty-column", "WARN", artifact=artifact, column=name, rows=row_count,
                note="declared column carries no value on any row",
            ))
            continue
        distinct = set(present)
        if len(distinct) == 1 and len(present) == row_count:
            findings.append(_finding(
                "constant-column", "WARN", artifact=artifact, column=name,
                value=next(iter(distinct))[:200], rows=row_count,
                note="single value on every row; a failure only if the "
                     "specification declared a multi-value vocabulary here",
            ))
    return findings


def check_locator_columns(
    artifact: str, columns: dict[str, list[str]], row_count: int
) -> list[dict[str, Any]]:
    """A field named as a locator must be able to locate something per row."""
    findings: list[dict[str, Any]] = []
    for name, values in columns.items():
        if not _names_a_locator(name):
            continue
        present = [value.strip() for value in values if value.strip()]
        if not present:
            continue
        distinct = set(present)
        if len(distinct) == 1 and row_count >= LOCATOR_CONSTANCY_ROWS:
            findings.append(_finding(
                "degenerate-locator", "FAIL", artifact=artifact, column=name,
                value=next(iter(distinct))[:200], rows=row_count,
                note="one locator value across every row locates nothing per row",
            ))
            continue
        addressable = [
            value for value in distinct
            if any(character in LOCATOR_SEPARATORS for character in value)
            or any(character.isdigit() for character in value)
        ]
        if not addressable:
            findings.append(_finding(
                "degenerate-locator", "WARN", artifact=artifact, column=name,
                value=sorted(distinct)[0][:200], distinct_values=len(distinct),
                note="locator values carry no offset, identifier, or separator; "
                     "prose token rather than an address",
            ))
        else:
            findings.append(_finding(
                "degenerate-locator", "PASS", artifact=artifact, column=name,
                distinct_values=len(distinct),
            ))
    return findings


def check_input_coverage(
    evidence: dict[str, Any], referenced_digests: set[str], referenced_names: set[str]
) -> list[dict[str, Any]]:
    """How much of each declared input directory the artifacts actually cite.

    A warning, never a failure: a legitimately filtered relation covers a small
    share of its corpus, and nothing available to this guard distinguishes that
    from a producer that resolved a fifth of the documents and invented the
    rest. The number is the point -- it is forwarded to the audit, which has
    the specification and can say which one it is looking at.
    """
    findings: list[dict[str, Any]] = []
    for root, files in evidence["input_groups"]:
        if not files:
            continue
        cited = [
            (path, digest) for path, digest in files
            if digest in referenced_digests
            or path in referenced_names
            or PurePosixPath(path).name in referenced_names
        ]
        detail = {
            "input": root,
            "files": len(files),
            "cited": len(cited),
            "share": round(len(cited) / len(files), 4),
        }
        if len(cited) == len(files):
            findings.append(_finding("input-coverage", "PASS", **detail))
        else:
            findings.append(_finding(
                "input-coverage", "WARN",
                note="declared input files no artifact row cites",
                **detail,
            ))
    return findings


def check_forbidden_tokens(
    root: Path, evidence: dict[str, Any], tokens: list[str]
) -> list[dict[str, Any]]:
    """Contract-banned constructions must be absent from the producer surface.

    Opt-in and specification-supplied: the guard has no way to know what a
    given contract banned, and inventing a list here would be the producer
    writing its own check by another route. Dead code counts -- a banned
    surrogate left unreachable is still a banned surrogate.
    """
    findings: list[dict[str, Any]] = []
    if not tokens:
        return findings
    surface = sorted({
        path for path, _digest in
        evidence["sections"]["code"] + evidence["sections"]["renderer_code"]
    })
    hits: list[dict[str, Any]] = []
    for relative in surface:
        target = _project_file(root, relative)
        if not target.is_file():
            continue
        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise GuardError(f"cannot read declared code {relative}: {exc}") from exc
        for number, line in enumerate(text.splitlines(), start=1):
            for token in tokens:
                if token in line:
                    hits.append({"path": relative, "line": number, "token": token})
    if hits:
        findings.append(_finding(
            "forbidden-token", "FAIL", tokens=tokens, hits=hits[:20],
            total_hits=len(hits),
            note="contract-banned construction present on the producer surface",
        ))
    else:
        findings.append(_finding("forbidden-token", "PASS", tokens=tokens))
    return findings


def run_checks(
    root: Path, receipt_path: Path, *, derived_scopes: set[str], forbid_tokens: list[str],
    max_bytes: int,
) -> dict[str, Any]:
    receipt = _load_json(receipt_path)
    producer = _producer_run(receipt)
    evidence = receipt_evidence(receipt)
    findings: list[dict[str, Any]] = []
    scanned: list[str] = []
    skipped: list[str] = []
    referenced_digests: set[str] = set()
    referenced_names: set[str] = set()
    input_names = {
        name
        for _root, files in evidence["input_groups"]
        for path, _digest in files
        for name in (path, PurePosixPath(path).name)
    }

    for target in _artifact_targets(producer, root):
        relative, absolute = target["path"], target["absolute"]
        if not absolute.is_file():
            findings.append(_finding(
                "artifact-present", "FAIL", artifact=relative,
                note="receipt declares an artifact that is not a regular file",
            ))
            continue
        recorded = target.get("sha256")
        if recorded is not None:
            live = _sha256_file(absolute)
            if live != recorded:
                findings.append(_finding(
                    "artifact-drift", "FAIL", artifact=relative,
                    recorded=recorded, live=live,
                    note="artifact bytes differ from the receipt fingerprint; "
                         "the guard would be reporting on unbound content",
                ))
                continue
        table = read_rows(absolute, max_bytes)
        if table is None:
            skipped.append(relative)
            continue
        header, rows = table
        scanned.append(relative)
        columns, duplicates = _columns(header, rows)
        for duplicate, occurrences in sorted(duplicates.items()):
            findings.append(_finding(
                "duplicate-column", "WARN", artifact=relative, column=duplicate,
                occurrences=occurrences,
                note="repeated header name; each occurrence is checked separately "
                     "under a #n suffix",
            ))
        reference_columns = _reference_columns(columns, evidence)
        row_inputs, row_artifacts = _row_reference_digests(
            reference_columns, evidence, len(rows))
        for values in columns.values():
            for value in values:
                stripped = value.strip()
                if not stripped:
                    continue
                match = DIGEST_CELL.fullmatch(stripped)
                if match:
                    if match.group(1) in evidence["digests"]:
                        referenced_digests.add(match.group(1))
                elif stripped in input_names:
                    referenced_names.add(stripped)
        findings.extend(check_digest_provenance(
            relative, columns, evidence, derived_scopes, row_inputs, row_artifacts))
        findings.extend(check_path_provenance(relative, reference_columns, evidence))
        findings.extend(check_column_degeneracy(relative, columns, len(rows)))
        findings.extend(check_locator_columns(relative, columns, len(rows)))

    if scanned:
        findings.extend(check_input_coverage(evidence, referenced_digests, referenced_names))
    findings.extend(check_forbidden_tokens(root, evidence, forbid_tokens))

    failures = [finding for finding in findings if finding["status"] == "FAIL"]
    warnings = [finding for finding in findings if finding["status"] == "WARN"]
    return {
        "schema_version": SCHEMA_VERSION,
        "checked_by": "construction_guard.py",
        "receipt": receipt_path.as_posix(),
        "artifacts_scanned": scanned,
        "artifacts_not_tabular": skipped,
        "declared_derived_digest_columns": sorted(derived_scopes),
        "ambiguous_input_names": evidence["ambiguous_references"],
        "ambiguous_artifact_names": evidence["ambiguous_artifact_references"],
        "forbidden_tokens": forbid_tokens,
        "status": "FAIL" if failures else "PASS",
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "findings": findings,
        "note": (
            "Passing means the artifacts carry evidence of derivation from the "
            "receipt's declared inputs, not that the construction is correct. "
            "Warnings are forwarded to the empirics audit, which owns correctness."
        ),
    }


def _default_report(receipt_path: Path) -> Path:
    name = receipt_path.name
    for suffix in (".receipt.json", ".json"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return receipt_path.parent / "construction_guard" / f"{name}.json"


def _parse_scope(values: Iterable[str]) -> set[str]:
    scopes: set[str] = set()
    for raw in values:
        column, separator, kind = raw.rpartition("=")
        if not separator or kind != "derived" or not column:
            raise GuardError(
                f"--digest-scope expects [<artifact>:]<column>=derived, got {raw!r}"
            )
        scopes.add(column)
    return scopes


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check receipt artifacts for evidence of derivation from declared inputs."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="run every guard against one result receipt")
    check.add_argument("--receipt", type=Path, required=True)
    check.add_argument("--report", type=Path, help="where to write the JSON report")
    check.add_argument(
        "--digest-scope", action="append", default=[], metavar="[ARTIFACT:]COLUMN=derived",
        help="declare that a digest column hashes derived content rather than a "
             "declared input, so membership in the receipt's digest set is not "
             "required. Supply only where the binding specification says so; the "
             "override is recorded in the report and read by the empirics audit.",
    )
    check.add_argument(
        "--forbid-token", action="append", default=[], metavar="TOKEN",
        help="a construction the binding contract bans from the producer surface",
    )
    check.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        root = args.project_root.resolve()
        report = run_checks(
            root, args.receipt,
            derived_scopes=_parse_scope(args.digest_scope),
            forbid_tokens=list(args.forbid_token),
            max_bytes=args.max_bytes,
        )
        destination = args.report or _default_report(args.receipt)
        report["report_path"] = destination.as_posix()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except GuardError as exc:
        print(f"construction_guard: {exc}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
