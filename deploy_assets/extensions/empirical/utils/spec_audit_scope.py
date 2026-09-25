#!/usr/bin/env python3
"""Scope digests for the data-first Gate-2 spec audit (issue #345).

The dataset-specification audit (``mechanism-auditor``, spec-audit role) may
carry a dimension's prior clean assessment forward across a mutate when the
change cannot bear on it.  That judgment belongs to the auditor, reading the
actual diff; this helper only makes the byte-level facts mechanical and
identical across firings, so no firing has to split a document by hand or
trust anyone's statement of what changed.

``digest`` prints the JSON block every audit report records under
``## Scope digests``: the whole spec's SHA-256, one SHA-256 per ``## `` section
(fenced code is never split), the rights inventory's digest with its
per-version ``dataset_version`` field removed (the field changes on every
mutate by construction and carries no rights content), and the digests of the
pilot report, problem statement, and build report.

``compare`` reads a prior report's block, which also records the spec and
rights paths it digested, and proves the files at those paths are the ones that
report audited.  It then compares
digests it recomputes from those files (never the recorded section or rights
values) with the current ones, and prints which sections and inputs differ,
followed by the unified diffs of the two specs and of the two rights
inventories.  Input files (pilot report, problem statement, build report) are
not versioned, so their prior side is the recorded value; a mis-recorded value
can only read as a change.  Exit status 2 means carry-forward is unavailable
(missing or malformed block, a prior file that no longer matches its recorded
digest, an unparseable document); the auditor then audits in full.

``sections --doc FILE`` prints one SHA-256 per ``## `` section of any markdown
document, split by the same rule.  The data-first Stage 3a auditors use it to
key carry-forward on the construction plan's ``## Class: <id>`` and
``## Shared construction`` sections instead of the whole plan, so a replan that
touches one class does not reset every other class's carried evidence.

``depth --prior-report P --report R`` enforces the one-hop carry bound (issue
#349): it reads each ``### N.`` paragraph under ``## Assessment by dimension``
in both audit reports and exits 1 if any dimension is marked carried
(``Carried from v…`` or ``Sites carried from v…``) in both.  The orchestrator
runs it, so the bound does not rest on the auditor's own discipline.

``acceptance-carries --report R`` reads the ``## Scope digests`` table of a
Stage 3a data-integrity, data-selection, or coverage report and exits 1 if any
row was carried (``Evidence`` cell ``carried (round k)``) over a source probe
that is not the source's own update marker (``Source probe`` cell not starting
``marker:``).  Carried evidence over a marker-less source may ride through
repair rounds but never reaches acceptance (issue #347): an in-place value
revision at such a source changes neither the cache bytes nor the identifier
list, so the orchestrator re-fires the auditor in full before activation.

``census-carry --prior-certificate C --prior-certificate-sha256 H --spec S --rights R --dataset-version N
--out O`` re-binds an accepted PASS coverage certificate to a new spec version
without re-running the census.  It checks ``C`` against its accepted digest
``H``, proves the prior certificate's recorded
spec and rights files are the bytes it certified, then requires every spec
section to be byte-identical between that spec and ``S`` except the few the
census cannot depend on (``CENSUS_BLIND_SECTIONS``: contribution sentence,
fact-portfolio plan, incumbent comparison, release plan, construction
partition, live services), and the two rights inventories to be identical
apart from ``dataset_version``.  The census reads the whole specification, so
the check is an allow-list of what may differ, never a list of what it reads.
Only then does it write ``O``: the prior certificate with its version and
spec/rights bindings updated and a ``carried_from`` record naming the
certificate it copied.  Exit 1 means not eligible (run the census); exit 2
means an unreadable or invalid input.  Source drift since the census is caught
by the coverage-auditor's live re-enumeration on every Stage 3a firing,
carried or not.
"""

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = 1
BLOCK_HEADING = "## Scope digests"
INPUT_NAMES = ("pilot_report", "problem_statement", "build_report")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


class ScopeError(Exception):
    pass


def _sha256(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _read_bytes(path):
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise ScopeError(f"cannot read {path}: {exc}") from exc


def split_sections(text):
    """Return [(key, text)] for the preamble and each level-2 section.

    A section runs from its ``## `` heading line up to the next one.  Lines
    inside fenced code blocks never start a section.  Keys are the heading
    lines; a repeated heading gets a ``#n`` suffix so every section stays
    addressable instead of silently merging with its namesake.
    """
    sections = [["(preamble)", []]]
    fence = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None and stripped.startswith("## ") and len(line) - len(stripped) <= 3:
            sections.append([stripped.rstrip("\r\n")[3:].strip(), []])
            sections[-1][1].append(line)
            continue
        sections[-1][1].append(line)
    seen = {}
    result = []
    for key, lines in sections:
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            key = f"{key}#{seen[key]}"
        result.append((key, "".join(lines)))
    return result


def canonical_rights(path):
    raw = _read_bytes(path)
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        raise ScopeError(f"rights inventory {path} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ScopeError(f"rights inventory {path} is not a JSON object")
    payload.pop("dataset_version", None)
    return json.dumps(payload, sort_keys=True, indent=1, ensure_ascii=False) + "\n"


def rights_digest(path):
    return _sha256(canonical_rights(path).encode("utf-8"))


def digest(spec, rights, inputs):
    raw = _read_bytes(spec)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScopeError(f"spec {spec} is not UTF-8: {exc}") from exc
    return {
        "schema_version": SCHEMA_VERSION,
        "spec_path": str(spec),
        "rights_path": str(rights),
        "spec_sha256": _sha256(raw),
        "sections": [[key, _sha256(body.encode("utf-8"))] for key, body in split_sections(text)],
        "rights_sha256_without_dataset_version": rights_digest(rights),
        "inputs": {
            name: (_sha256(_read_bytes(inputs[name])) if inputs.get(name) else None)
            for name in INPUT_NAMES
        },
    }


def document_sections(doc):
    raw = _read_bytes(doc)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScopeError(f"document {doc} is not UTF-8: {exc}") from exc
    return {
        "doc_path": str(doc),
        "doc_sha256": _sha256(raw),
        "sections": [[key, _sha256(body.encode("utf-8"))] for key, body in split_sections(text)],
    }


CARRY_MARK = re.compile(r"^(?:Sites carried|Carried) from v\d+\.")
NEAR_MISS = re.compile(r"carried from v\d", re.IGNORECASE)


def dimension_marks(report):
    """Map dimension number -> whether its paragraph opens with a carry mark."""
    raw = _read_bytes(report)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScopeError(f"report {report} is not UTF-8: {exc}") from exc
    body = dict(split_sections(text)).get("Assessment by dimension")
    if body is None:
        raise ScopeError(f"report {report} has no '## Assessment by dimension' section")
    marks, current = {}, None
    for line in body.splitlines()[1:]:
        heading = re.match(r"###\s+(\d+)\.", line)
        if heading:
            current = int(heading.group(1))
            if current in marks:
                raise ScopeError(f"report {report} repeats dimension {current}")
            marks[current] = None
        elif current is not None and marks[current] is None and line.strip():
            first = line.strip()
            marked = bool(CARRY_MARK.match(first))
            if not marked and NEAR_MISS.search(first[:60]):
                raise ScopeError(f"report {report} dimension {current} opens with a malformed carry mark: {first[:60]!r}")
            marks[current] = marked
    if not marks or any(v is None for v in marks.values()):
        raise ScopeError(f"report {report} has an empty or missing dimension paragraph")
    return marks


def depth(prior_report, report):
    prior, current = dimension_marks(prior_report), dimension_marks(report)
    if set(prior) != set(current):
        raise ScopeError("prior and current reports assess different dimension sets")
    violations = sorted(d for d in current if current[d] and prior[d])
    return {"carried_now": sorted(d for d in current if current[d]),
            "carried_twice": violations}


PROBE_MARKER = re.compile(r"[`*]*marker:", re.IGNORECASE)


def _table_cells(line):
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def acceptance_carries(report):
    """Rows carried over a probe other than a source update marker."""
    raw = _read_bytes(report)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScopeError(f"report {report} is not UTF-8: {exc}") from exc
    body = dict(split_sections(text)).get("Scope digests")
    if body is None:
        raise ScopeError(f"report {report} has no '{BLOCK_HEADING}' section")
    rows = [cells for cells in map(_table_cells, body.splitlines()[1:]) if cells is not None]
    if len(rows) < 2 or not all(set(c) <= set("-: ") for c in rows[1]):
        raise ScopeError(f"report {report}: '{BLOCK_HEADING}' holds no markdown table")
    header = [cell.lower() for cell in rows[0]]
    if "evidence" not in header:
        raise ScopeError(f"report {report}: scope table has no Evidence column")
    evidence = header.index("evidence")
    probe = header.index("source probe") if "source probe" in header else None
    unmarked = []
    for cells in rows[2:]:
        if len(cells) != len(header):
            raise ScopeError(f"report {report}: scope table row has {len(cells)} cells, "
                             f"header has {len(header)}")
        if not cells[evidence].strip("`* ").lower().startswith("carried"):
            continue
        if probe is None or not PROBE_MARKER.match(cells[probe]):
            unmarked.append(cells[0])
    return unmarked


def read_block(report):
    """Parse the first ```json fence after the report's Scope digests heading."""
    text = _read_bytes(report).decode("utf-8", errors="replace")
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == BLOCK_HEADING)
    except StopIteration:
        raise ScopeError(f"{report} has no '{BLOCK_HEADING}' section") from None
    body = None
    for i in range(start + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## "):
            break
        if stripped == "```json":
            end = next((j for j in range(i + 1, len(lines)) if lines[j].strip() == "```"), None)
            if end is None:
                raise ScopeError(f"{report}: unterminated json fence under '{BLOCK_HEADING}'")
            body = "\n".join(lines[i + 1:end])
            break
    if body is None:
        raise ScopeError(f"{report}: no ```json block under '{BLOCK_HEADING}'")
    try:
        block = json.loads(body)
    except ValueError as exc:
        raise ScopeError(f"{report}: scope digest block is not valid JSON: {exc}") from exc
    if not isinstance(block, dict) or block.get("schema_version") != SCHEMA_VERSION:
        raise ScopeError(f"{report}: scope digest block has an unsupported schema_version")
    sections = block.get("sections")
    if (not isinstance(sections, list)
            or not all(isinstance(s, list) and len(s) == 2 and all(isinstance(v, str) for v in s)
                       for s in sections)
            or len({s[0] for s in sections}) != len(sections)):
        raise ScopeError(f"{report}: scope digest block has malformed sections")
    for field in ("spec_path", "rights_path"):
        if not isinstance(block.get(field), str) or not block[field]:
            raise ScopeError(f"{report}: scope digest block lacks {field}")
    digests = [block.get("spec_sha256"), block.get("rights_sha256_without_dataset_version")]
    digests += [s[1] for s in sections]
    inputs = block.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != set(INPUT_NAMES):
        raise ScopeError(f"{report}: scope digest block has malformed inputs")
    digests += [v for v in inputs.values() if v is not None]
    if not all(isinstance(d, str) and DIGEST.fullmatch(d) for d in digests):
        raise ScopeError(f"{report}: scope digest block has a malformed digest")
    return block


def compare(prior_report, spec, rights, inputs):
    recorded = read_block(prior_report)
    prior_spec, prior_rights = recorded["spec_path"], recorded["rights_path"]
    # Recompute the prior side from the audited files themselves; the recorded
    # block only has to agree with them, it is never the source of truth.
    prior = digest(prior_spec, prior_rights, {})
    if prior["spec_sha256"] != recorded["spec_sha256"] or prior["sections"] != recorded["sections"]:
        raise ScopeError(
            f"{prior_spec} does not match the spec digests recorded in {prior_report}; "
            "it is not the document that report audited")
    if prior["rights_sha256_without_dataset_version"] != recorded["rights_sha256_without_dataset_version"]:
        raise ScopeError(
            f"{prior_rights} does not match the rights digest recorded in {prior_report}; "
            "it is not the inventory that report audited")
    prior["inputs"] = recorded["inputs"]
    prior_raw = _read_bytes(prior_spec)
    current = digest(spec, rights, inputs)
    before = dict(prior["sections"])
    after = dict(current["sections"])
    changed = [key for key in after if key in before and after[key] != before[key]]
    summary = {
        "spec_identical": current["spec_sha256"] == prior["spec_sha256"],
        "sections_changed": changed,
        "sections_added": [key for key in after if key not in before],
        "sections_removed": [key for key in before if key not in after],
        "section_order_changed": [k for k in (s[0] for s in prior["sections"]) if k in after]
        != [k for k in (s[0] for s in current["sections"]) if k in before],
        "rights_changed": current["rights_sha256_without_dataset_version"]
        != prior["rights_sha256_without_dataset_version"],
        "inputs_changed": [name for name in INPUT_NAMES if current["inputs"][name] != prior["inputs"][name]],
    }
    diff = difflib.unified_diff(
        prior_raw.decode("utf-8", errors="replace").splitlines(keepends=True),
        _read_bytes(spec).decode("utf-8", errors="replace").splitlines(keepends=True),
        fromfile=str(prior_spec), tofile=str(spec))
    rights_diff = difflib.unified_diff(
        canonical_rights(prior_rights).splitlines(keepends=True),
        canonical_rights(rights).splitlines(keepends=True),
        fromfile=f"{prior_rights} (without dataset_version)", tofile=f"{rights} (without dataset_version)")
    return summary, "".join(diff), "".join(rights_diff)


CENSUS_BLIND_SECTIONS = frozenset({
    "One-sentence contribution", "Fact-portfolio plan", "Incumbent comparison",
    "Release plan", "Construction partition", "Trusted-run live services",
})


class NotEligible(Exception):
    pass


def _census_relevant_sections(path):
    raw = _read_bytes(path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScopeError(f"spec {path} is not UTF-8: {exc}") from exc
    sections = split_sections(text)
    if [key.split("#")[0] for key, _ in sections].count("Exact coverage commitments") != 1:
        raise ScopeError(f"spec {path} must have exactly one '## Exact coverage commitments' section")
    return {key: body for key, body in sections if key.split("#")[0] not in CENSUS_BLIND_SECTIONS}


def census_carry(prior_certificate, prior_sha256, spec, rights, dataset_version, out):
    raw = _read_bytes(prior_certificate)
    if _sha256(raw) != prior_sha256:
        raise NotEligible(f"{prior_certificate} does not match the accepted certificate digest")
    try:
        cert = json.loads(raw)
    except ValueError as exc:
        raise ScopeError(f"certificate {prior_certificate} is not valid JSON: {exc}") from exc
    if not isinstance(cert, dict) or cert.get("schema_version") != 1:
        raise ScopeError(f"certificate {prior_certificate} is not a schema-version-1 object")
    if cert.get("status") != "PASS":
        raise NotEligible(f"prior certificate status is {cert.get('status')!r}, not PASS")
    bindings = {}
    for field in ("dataset_spec", "rights_inventory"):
        entry = cert.get(field)
        if not (isinstance(entry, dict) and isinstance(entry.get("path"), str)
                and isinstance(entry.get("sha256"), str) and DIGEST.fullmatch(entry["sha256"])):
            raise ScopeError(f"certificate {prior_certificate} has a malformed {field} binding")
        if _sha256(_read_bytes(entry["path"])) != entry["sha256"]:
            raise NotEligible(f"{entry['path']} no longer matches the certificate's {field} digest")
        bindings[field] = entry["path"]
    before = _census_relevant_sections(bindings["dataset_spec"])
    after = _census_relevant_sections(spec)
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    if changed:
        raise NotEligible(f"sections the census may depend on changed: {changed}")
    if canonical_rights(bindings["rights_inventory"]) != canonical_rights(rights):
        raise NotEligible("rights inventory differs from the certified one beyond dataset_version")
    if Path(out).exists():
        raise ScopeError(f"{out} already exists; allocate a fresh certificate serial")
    carried = dict(cert)
    carried["dataset_version"] = dataset_version
    carried["dataset_spec"] = {"path": str(spec), "sha256": _sha256(_read_bytes(spec))}
    carried["rights_inventory"] = {"path": str(rights), "sha256": _sha256(_read_bytes(rights))}
    carried["carried_from"] = {"path": str(prior_certificate), "sha256": _sha256(raw)}
    Path(out).write_text(json.dumps(carried, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return carried["carried_from"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("digest", "compare"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--spec", required=True)
        cmd.add_argument("--rights", required=True)
        cmd.add_argument("--pilot-report")
        cmd.add_argument("--problem-statement")
        cmd.add_argument("--build-report")
        if name == "compare":
            cmd.add_argument("--prior-report", required=True)
    sections_cmd = sub.add_parser("sections")
    sections_cmd.add_argument("--doc", required=True)
    carries_cmd = sub.add_parser("acceptance-carries")
    carries_cmd.add_argument("--report", required=True)
    depth_cmd = sub.add_parser("depth")
    depth_cmd.add_argument("--prior-report", required=True)
    depth_cmd.add_argument("--report", required=True)
    carry_cmd = sub.add_parser("census-carry")
    carry_cmd.add_argument("--prior-certificate", required=True)
    carry_cmd.add_argument("--prior-certificate-sha256", required=True)
    carry_cmd.add_argument("--spec", required=True)
    carry_cmd.add_argument("--rights", required=True)
    carry_cmd.add_argument("--dataset-version", required=True, type=int)
    carry_cmd.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    if args.command == "census-carry":
        try:
            origin = census_carry(args.prior_certificate, args.prior_certificate_sha256, args.spec, args.rights,
                                  args.dataset_version, args.out)
        except NotEligible as exc:
            print(f"spec_audit_scope: not eligible: {exc}; run the census", file=sys.stderr)
            return 1
        except ScopeError as exc:
            print(f"spec_audit_scope: {exc}; run the census", file=sys.stderr)
            return 2
        print(json.dumps({"carried_from": origin}, indent=2))
        return 0
    if args.command == "acceptance-carries":
        try:
            unmarked = acceptance_carries(args.report)
        except ScopeError as exc:
            print(f"spec_audit_scope: {exc}; re-fire the auditor in full", file=sys.stderr)
            return 2
        print(json.dumps({"carried_without_marker": unmarked}, indent=2))
        return 1 if unmarked else 0
    if args.command == "depth":
        try:
            result = depth(args.prior_report, args.report)
        except ScopeError as exc:
            print(f"spec_audit_scope: {exc}; carry depth unverifiable", file=sys.stderr)
            return 2
        print(json.dumps(result, indent=2))
        return 1 if result["carried_twice"] else 0
    if args.command == "sections":
        try:
            print(json.dumps(document_sections(args.doc), indent=2))
        except ScopeError as exc:
            print(f"spec_audit_scope: {exc}; carry-forward unavailable, audit in full", file=sys.stderr)
            return 2
        return 0
    inputs = {
        "pilot_report": args.pilot_report,
        "problem_statement": args.problem_statement,
        "build_report": args.build_report,
    }
    try:
        if args.command == "digest":
            print(json.dumps(digest(args.spec, args.rights, inputs), indent=2))
        else:
            summary, diff, rights_diff = compare(
                args.prior_report, args.spec, args.rights, inputs)
            print(json.dumps(summary, indent=2))
            print("--- unified diff (prior spec -> current spec) ---")
            sys.stdout.write(diff)
            print("--- unified diff (prior rights -> current rights) ---")
            sys.stdout.write(rights_diff)
    except ScopeError as exc:
        print(f"spec_audit_scope: {exc}; carry-forward unavailable, audit in full", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
