#!/usr/bin/env python3
"""Tests for the data-first Gate-2 scope-digest helper (issue #345)."""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HELPER = REPO / "deploy_assets/extensions/empirical/utils/spec_audit_scope.py"
SPEC = importlib.util.spec_from_file_location("spec_audit_scope", HELPER)
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)

FAILURES = []


def check(label, condition):
    print(("PASS " if condition else "FAIL ") + label)
    if not condition:
        FAILURES.append(label)


SPEC_V1 = """# Event Dataset

## One-sentence contribution
An open dataset.

## Inclusion rules
Every FOMC statement listed on the Board archive.

```markdown
## Not a heading
```

## Validation plan
**Class sources:** ["fed_archive", "newswire"]

## Release plan
Offline release.
"""

RIGHTS_V1 = {"schema_version": 1, "dataset_version": 1,
             "sources": [{"source_id": "fed_archive", "redistribution": "open",
                          "evidence": {"url": "u", "terms": "t", "checked_at": "2026-09-01"}}]}


def run(*args):
    return subprocess.run([sys.executable, str(HELPER), *args], capture_output=True, text=True)


def report_with(block):
    return ("# Dataset Specification Audit v1\n\n## Assessment by dimension\n### 1. x\nok\n\n"
            "## Scope digests\n```json\n" + json.dumps(block, indent=2) + "\n```\n\n## Verdict\n\n"
            "**Verdict:** REVISE\n")


def main():
    print("[1] section split")
    keys = [k for k, _ in scope.split_sections(SPEC_V1)]
    check("fenced '## ' line does not start a section",
          keys == ["(preamble)", "One-sentence contribution", "Inclusion rules", "Validation plan", "Release plan"])
    check("sections reassemble the document byte for byte",
          "".join(t for _, t in scope.split_sections(SPEC_V1)) == SPEC_V1)
    indented = scope.split_sections("x\n   ## B\ny\n    ## not a heading\n")
    check("up to three spaces of indent still start a section, four do not",
          [k for k, _ in indented] == ["(preamble)", "B"])
    dup = scope.split_sections("## A\nx\n## A\ny\n")
    check("repeated heading stays addressable", [k for k, _ in dup] == ["(preamble)", "A", "A#2"])

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        spec1, spec2 = tmp / "theory_draft_v1.md", tmp / "theory_draft_v2.md"
        rights1, rights2 = tmp / "source_rights_s1_v1.json", tmp / "source_rights_s1_v2.json"
        pilot = tmp / "idea_prototype.md"
        spec1.write_text(SPEC_V1)
        rights1.write_text(json.dumps(RIGHTS_V1))
        pilot.write_text("pilot\n")
        common = ["--pilot-report", str(pilot)]

        print("[2] digest")
        out = run("digest", "--spec", str(spec1), "--rights", str(rights1), *common)
        check("digest exits 0", out.returncode == 0)
        block = json.loads(out.stdout)
        check("digest records inputs, absent ones as null",
              block["inputs"]["pilot_report"].startswith("sha256:") and block["inputs"]["build_report"] is None)
        report = tmp / "mechanism_audit_v1.md"
        report.write_text(report_with(block))

        print("[3] compare: one-section mutate, version-only rights change")
        spec2.write_text(SPEC_V1.replace("Offline release.", "Offline release, no credentials."))
        rights2.write_text(json.dumps(dict(RIGHTS_V1, dataset_version=2), indent=4))
        cmp_args = ["compare", "--prior-report", str(report), "--spec", str(spec2), "--rights", str(rights2), *common]
        out = run(*cmp_args)
        check("compare exits 0", out.returncode == 0)
        summary = json.loads(out.stdout.split("--- unified diff")[0])
        check("only the edited section changed", summary["sections_changed"] == ["Release plan"]
              and not summary["sections_added"] and not summary["sections_removed"]
              and not summary["section_order_changed"])
        check("dataset_version bump and reformatting leave rights unchanged", summary["rights_changed"] is False)
        check("unchanged inputs are not reported", summary["inputs_changed"] == [])
        check("unified diff is printed", "+Offline release, no credentials." in out.stdout)
        check("rights diff is printed and empty", out.stdout.rstrip().endswith("(prior rights -> current rights) ---"))

        print("[4] compare: real rights change and a changed input")
        changed = json.loads(json.dumps(RIGHTS_V1))
        changed["sources"][0]["redistribution"] = "restricted"
        rights2.write_text(json.dumps(changed))
        pilot2 = tmp / "idea_prototype_2.md"
        pilot2.write_text("pilot, revised\n")
        out = run("compare", "--prior-report", str(report),
                  "--spec", str(spec2), "--rights", str(rights2), "--pilot-report", str(pilot2))
        summary = json.loads(out.stdout.split("--- unified diff")[0])
        check("classification change is a rights change", summary["rights_changed"] is True)
        check("rights diff shows the reclassification", '+   "redistribution": "restricted"' in out.stdout)
        check("changed pilot is reported", summary["inputs_changed"] == ["pilot_report"])
        out = run("compare", "--prior-report", str(report), "--spec", str(spec2),
                  "--rights", str(rights1), *common, "--build-report", str(pilot))
        summary = json.loads(out.stdout.split("--- unified diff")[0])
        check("a build report appearing is a changed input", summary["inputs_changed"] == ["build_report"])

        print("[5] compare: section added and reordered")
        spec2.write_text(SPEC_V1.replace("## Release plan", "## Construction staging\nnone\n\n## Release plan"))
        summary = json.loads(run(*cmp_args).stdout.split("--- unified diff")[0])
        check("added section is reported", summary["sections_added"] == ["Construction staging"])
        check("the section before an insertion is unchanged", summary["sections_changed"] == [])
        swapped = SPEC_V1.replace("## Validation plan\n**Class sources:** [\"fed_archive\", \"newswire\"]\n\n", "")
        swapped += "\n## Validation plan\n**Class sources:** [\"fed_archive\", \"newswire\"]\n\n"
        spec2.write_text(swapped)
        summary = json.loads(run(*cmp_args).stdout.split("--- unified diff")[0])
        check("reordering is reported", summary["section_order_changed"] is True)

        print("[6] compare refuses: carry-forward unavailable")
        spec1.write_text(SPEC_V1 + "edited after audit\n")
        out = run(*cmp_args)
        check("prior spec edited after its audit exits 2", out.returncode == 2 and "not the document" in out.stderr)
        spec1.write_text(SPEC_V1)
        forged = json.loads(json.dumps(block))
        forged["sections"][2][1] = "sha256:" + "0" * 64
        report.write_text(report_with(forged))
        check("recorded section digests that disagree with the prior spec exit 2", run(*cmp_args).returncode == 2)
        rights1.write_text(json.dumps(dict(RIGHTS_V1, sources=[])))
        report.write_text(report_with(block))
        out = run(*cmp_args)
        check("prior rights edited after its audit exits 2", out.returncode == 2 and "inventory" in out.stderr)
        rights1.write_text(json.dumps(RIGHTS_V1))
        report.write_text(report_with(dict(block, spec_sha256="sha256:XYZ")))
        check("malformed digest exits 2", run(*cmp_args).returncode == 2)
        report.write_text("# Audit\n\n## Verdict\nREVISE\n")
        check("report without a digest block exits 2", run(*cmp_args).returncode == 2)
        report.write_text(report_with(dict(block, schema_version=99)))
        check("unknown schema_version exits 2", run(*cmp_args).returncode == 2)
        bad = dict(block, sections=block["sections"] + [block["sections"][0]])
        report.write_text(report_with(bad))
        check("duplicate section keys exit 2", run(*cmp_args).returncode == 2)
        report.write_text(report_with(block))
        rights2.write_text("{not json")
        check("unparseable rights exits 2", run(*cmp_args).returncode == 2)

        plan = tmp / "empirical_plan.md"
        plan.write_text("# Plan\n\n## Shared construction\nspine\n\n## Class: fomc\nA\n```\n## Class: fake\n```\n\n## Class: cpi\nB\n")
        out = run("sections", "--doc", str(plan))
        first = json.loads(out.stdout) if out.returncode == 0 else {}
        keys = [k for k, _ in first.get("sections", [])]
        check("sections splits a plan into its level-2 sections, fences unsplit",
              keys == ["(preamble)", "Shared construction", "Class: fomc", "Class: cpi"])
        plan.write_text(plan.read_text().replace("\nB\n", "\nB2\n"))
        second = json.loads(run("sections", "--doc", str(plan)).stdout)
        changed = [a[0] for a, b in zip(first["sections"], second["sections"]) if a[1] != b[1]]
        check("editing one class changes only that class's section digest", changed == ["Class: cpi"])
        check("sections on a missing file exits 2", run("sections", "--doc", str(tmp / "absent.md")).returncode == 2)

        def audit(paras):
            dims = "".join(f"### {i}. Dim {i}\n{p}\n" for i, p in enumerate(paras, 1))
            return "# Audit\n\n## Assessment by dimension\n" + dims + "\n## Verdict\nPLAUSIBLE\n"
        pr, cr = tmp / "prior_audit.md", tmp / "cur_audit.md"
        pr.write_text(audit(["Clean.", "Carried from v1. Clean.", "Clean."]))
        cr.write_text(audit(["Carried from v2. Clean.", "Fresh read.", "Sites carried from v2. Clean."]))
        out = run("depth", "--prior-report", str(pr), "--report", str(cr))
        check("depth passes when no dimension is carried twice", out.returncode == 0)
        cr.write_text(audit(["Clean.", "Carried from v1. Clean.", "Clean."]))
        out = run("depth", "--prior-report", str(pr), "--report", str(cr))
        check("depth rejects a whole-dimension carry of a carried paragraph",
              out.returncode == 1 and json.loads(out.stdout)["carried_twice"] == [2])
        cr.write_text(audit(["Clean.", "Sites carried from v2. Clean.", "Clean."]))
        check("depth rejects a site-level carry of a carried paragraph",
              run("depth", "--prior-report", str(pr), "--report", str(cr)).returncode == 1)
        pr.write_text(audit(["Clean.", "Sites carried from v1. Clean.", "Clean."]))
        cr.write_text(audit(["Clean.", "Carried from v2. Clean.", "Clean."]))
        check("depth rejects a carry following a site-level carry",
              run("depth", "--prior-report", str(pr), "--report", str(cr)).returncode == 1)
        cr.write_text(audit(["**Carried from v2.** Clean.", "Clean.", "Clean."]))
        check("depth on a decorated carry mark exits 2 instead of reading it as fresh",
              run("depth", "--prior-report", str(pr), "--report", str(cr)).returncode == 2)
        cr.write_text(audit(["Clean.", "Clean."]))
        check("depth on mismatched dimension sets exits 2",
              run("depth", "--prior-report", str(pr), "--report", str(cr)).returncode == 2)
        cr.write_text("# Audit\n\n## Verdict\nPLAUSIBLE\n")
        check("depth on a report without assessments exits 2",
              run("depth", "--prior-report", str(pr), "--report", str(cr)).returncode == 2)

        def scope_report(rows, header="| Universe | Cache sha256 | Source probe | Evidence |"):
            table = "\n".join([header, "|---|---|---|---|", *rows])
            return "# Data Selection Audit — round 3\n\n## Findings\n\n## Scope digests\n" + table + "\n\n## Verdict rationale\nok\n"
        rep = tmp / "selection_audit.md"
        rep.write_text(scope_report(["| crsp | sha256:aa | marker: 2026-09-01 | carried (round 1) |",
                              "| fomc | sha256:bb | ids-sha256:cc | live |"]))
        out = run("acceptance-carries", "--report", str(rep))
        check("acceptance-carries passes marker-probed carries and live rows",
              out.returncode == 0 and json.loads(out.stdout)["carried_without_marker"] == [])
        rep.write_text(scope_report(["| crsp | sha256:aa | `marker: v7` | **carried (round 1)** |",
                              "| fomc | sha256:bb | ids-sha256:cc | carried (round 2) |"]))
        out = run("acceptance-carries", "--report", str(rep))
        check("acceptance-carries flags a carry over an identifier-list probe",
              out.returncode == 1 and json.loads(out.stdout)["carried_without_marker"] == ["fomc"])
        rep.write_text(scope_report(["| cache.parquet | sha256:aa | carried (round 1) |"],
                             header="| Cache path | Cache sha256 | Evidence |").replace("|---|---|---|---|", "|---|---|---|"))
        out = run("acceptance-carries", "--report", str(rep))
        check("acceptance-carries flags a carry in a table with no probe column",
              out.returncode == 1 and json.loads(out.stdout)["carried_without_marker"] == ["cache.parquet"])
        rep.write_text("# Audit\n\n## Findings\nnone\n")
        check("acceptance-carries on a report without a scope table exits 2",
              run("acceptance-carries", "--report", str(rep)).returncode == 2)
        rep.write_text(scope_report(["| crsp | sha256:aa | marker: x |"]))
        check("acceptance-carries on a ragged row exits 2",
              run("acceptance-carries", "--report", str(rep)).returncode == 2)

    print()
    print("[census-carry] re-bind a PASS certificate when only census-blind sections changed")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        commit = "## Exact coverage commitments\n**Commitment IDs:** [\"fomc\"]\n### commitment_id: fomc\nall statements\n"
        spec1, spec2, spec3 = tmp / "v1.md", tmp / "v2.md", tmp / "v3.md"
        spec1.write_text("# D\n\n## Inclusion rules\nold\n\n" + commit + "\n## Fact-portfolio plan\nold fact\n")
        spec2.write_text("# D\n\n## Inclusion rules\nold\n\n" + commit + "\n## Fact-portfolio plan\nnew fact\n")
        spec3.write_text("# D\n\n## Inclusion rules\nold\n\n" + commit.replace("all statements", "all minutes") + "\n## Fact-portfolio plan\nold fact\n")
        r1, r2 = tmp / "r1.json", tmp / "r2.json"
        r1.write_text(json.dumps(RIGHTS_V1))
        r2.write_text(json.dumps(dict(RIGHTS_V1, dataset_version=2)))
        cert = {"schema_version": 1, "dataset_version": 1, "status": "PASS",
                "dataset_spec": {"path": str(spec1), "sha256": scope._sha256(spec1.read_bytes())},
                "rights_inventory": {"path": str(r1), "sha256": scope._sha256(r1.read_bytes())},
                "commitments": [{"commitment_id": "fomc"}]}
        c1 = tmp / "c1.json"
        c1.write_text(json.dumps(cert))
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec2),
                  "--rights", str(r2), "--dataset-version", "2", "--out", str(tmp / "c2.json"))
        check("a fact-portfolio-only change with unchanged rights carries (exit 0)", out.returncode == 0)
        new = json.loads((tmp / "c2.json").read_text())
        check("carried certificate is bound to the new spec, rights, and version",
              new["dataset_version"] == 2 and new["dataset_spec"]["path"] == str(spec2)
              and new["dataset_spec"]["sha256"] == scope._sha256(spec2.read_bytes())
              and new["rights_inventory"]["sha256"] == scope._sha256(r2.read_bytes())
              and new["carried_from"]["sha256"] == scope._sha256(c1.read_bytes())
              and new["commitments"] == cert["commitments"])
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec2),
                  "--rights", str(r2), "--dataset-version", "2", "--out", str(tmp / "c2.json"))
        check("existing output path is refused (exit 2)", out.returncode == 2)
        dup = tmp / "dup.md"
        dup.write_text(spec2.read_text() + "\n" + commit)
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()),
                  "--spec", str(dup), "--rights", str(r2), "--dataset-version", "3", "--out", str(tmp / "c10.json"))
        check("a spec with two commitment sections is refused (exit 2)", out.returncode == 2)
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec3),
                  "--rights", str(r2), "--dataset-version", "3", "--out", str(tmp / "c3.json"))
        check("changed commitment section is not eligible (exit 1)",
              out.returncode == 1 and not (tmp / "c3.json").exists())
        spec4 = tmp / "v4.md"
        spec4.write_text("# D\n\n## Inclusion rules\nnew wording\n\n" + commit + "\n## Fact-portfolio plan\nold fact\n")
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec4),
                  "--rights", str(r2), "--dataset-version", "4", "--out", str(tmp / "c8.json"))
        check("a changed census-relevant section outside the commitments is not eligible (exit 1)",
              out.returncode == 1 and "Inclusion rules" in out.stderr)
        r3 = tmp / "r3.json"
        r3.write_text(json.dumps(dict(RIGHTS_V1, sources=[])))
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec2),
                  "--rights", str(r3), "--dataset-version", "3", "--out", str(tmp / "c4.json"))
        check("changed rights content is not eligible (exit 1)", out.returncode == 1)
        spec1.write_text(spec1.read_text() + "tampered\n")
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", scope._sha256(c1.read_bytes()), "--spec", str(spec2),
                  "--rights", str(r2), "--dataset-version", "3", "--out", str(tmp / "c5.json"))
        check("certified spec no longer matching its digest is not eligible (exit 1)", out.returncode == 1)
        out = run("census-carry", "--prior-certificate", str(c1), "--prior-certificate-sha256", "sha256:" + "0" * 64,
                  "--spec", str(spec2), "--rights", str(r2), "--dataset-version", "3", "--out", str(tmp / "c9.json"))
        check("a certificate not matching the accepted digest is not eligible (exit 1)", out.returncode == 1)
        c6 = tmp / "c6.json"
        c6.write_text(json.dumps(dict(cert, status="GAPS")))
        out = run("census-carry", "--prior-certificate", str(c6), "--prior-certificate-sha256", scope._sha256(c6.read_bytes()), "--spec", str(spec2),
                  "--rights", str(r2), "--dataset-version", "3", "--out", str(tmp / "c7.json"))
        check("a non-PASS certificate is not eligible (exit 1)", out.returncode == 1)

    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {FAILURES}")
        return 1
    print("all spec_audit_scope checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
