#!/usr/bin/env python3
"""Characterize setup.sh's complete local-deployment output.

The setup refactor tracked by issue #255 is deliberately behavior-preserving.
This test builds a matrix of supported deployment shapes, validates and then
normalizes the three intentional per-deployment values (fingerprint, date, and
git revision), and compares every resulting file, permission mode, symlink,
and empty directory with a committed hash inventory.

The harness runs setup.sh from an isolated source shim so a developer's
gitignored .env is never copied into the fixtures or allowed to affect them; a
separate synthetic canary covers that branch.  Use --actual to write a
candidate inventory and --artifacts-dir to retain complete trees and logs.
Updating the committed baseline is an explicit --update-golden operation and
always covers the full matrix.
"""

from __future__ import annotations

import argparse
import concurrent.futures
from contextlib import contextmanager
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any
import uuid


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_PATH = Path(__file__).resolve().parent / "fixtures" / "setup_characterization.json"

# The first 22 cases enumerate every currently supported
# variant × mode × extension-set assembly shape.  The remaining cases exercise
# the orthogonal flags where they materially change deployed output, including
# interactions with both extension families and the llm_cognition auto-imply,
# plus supported legacy spellings and order-sensitive repeated flags.
CASES: dict[str, tuple[str, ...]] = {
    # No --variant flag: finance is the parser default.  The destination is
    # still explicit here; default project naming has its own exact CLI probe.
    "finance_default_variant": (),
    "finance_base": ("--variant", "finance"),
    "finance_empirical": ("--variant", "finance", "--ext", "empirical"),
    "finance_theory_llm": ("--variant", "finance", "--ext", "theory_llm"),
    "finance_both_extensions": (
        "--variant", "finance", "--ext", "empirical", "--ext", "theory_llm",
    ),
    "finance_both_extensions_reverse": (
        "--variant", "finance", "--ext", "theory_llm", "--ext", "empirical",
    ),
    "finance_empirical_first": ("--variant", "finance", "--mode", "empirical-first"),
    "finance_empirical_first_theory_llm": (
        "--variant", "finance", "--mode", "empirical-first", "--ext", "theory_llm",
    ),
    "finance_report": ("--variant", "finance", "--mode", "report"),
    "finance_report_empirical": (
        "--variant", "finance", "--mode", "report", "--ext", "empirical",
    ),
    "finance_report_theory_llm": (
        "--variant", "finance", "--mode", "report", "--ext", "theory_llm",
    ),
    "finance_report_both_extensions": (
        "--variant", "finance", "--mode", "report",
        "--ext", "empirical", "--ext", "theory_llm",
    ),
    "finance_report_both_extensions_reverse": (
        "--variant", "finance", "--mode", "report",
        "--ext", "theory_llm", "--ext", "empirical",
    ),
    "macro_base": ("--variant", "macro"),
    "macro_empirical": ("--variant", "macro", "--ext", "empirical"),
    "macro_theory_llm": ("--variant", "macro", "--ext", "theory_llm"),
    "macro_both_extensions": (
        "--variant", "macro", "--ext", "empirical", "--ext", "theory_llm",
    ),
    "macro_report": ("--variant", "macro", "--mode", "report"),
    "macro_report_empirical": (
        "--variant", "macro", "--mode", "report", "--ext", "empirical",
    ),
    "macro_report_theory_llm": (
        "--variant", "macro", "--mode", "report", "--ext", "theory_llm",
    ),
    "macro_report_both_extensions": (
        "--variant", "macro", "--mode", "report",
        "--ext", "empirical", "--ext", "theory_llm",
    ),
    "llm_cognition_base": ("--variant", "llm_cognition"),
    "llm_cognition_measurement_first": (
        "--variant", "llm_cognition", "--mode", "measurement-first",
    ),
    "llm_cognition_report": ("--variant", "llm_cognition", "--mode", "report"),
    "llm_cognition_report_theory_llm": (
        "--variant", "llm_cognition", "--mode", "report", "--ext", "theory_llm",
    ),
    "finance_seed": ("--variant", "finance", "--seed"),
    "finance_faithful_empirical_light_halt": (
        "--variant", "finance", "--ext", "empirical", "--faithful",
        "--light", "--halt-on-core-bypass",
    ),
    "finance_manual_both_extensions": (
        "--variant", "finance", "--manual",
        "--ext", "empirical", "--ext", "theory_llm",
    ),
    "finance_light": ("--variant", "finance", "--light"),
    "finance_halt_on_core_bypass": (
        "--variant", "finance", "--halt-on-core-bypass",
    ),
    "finance_report_light": (
        "--variant", "finance", "--mode", "report", "--light",
    ),
    "llm_cognition_faithful": ("--variant", "llm_cognition", "--faithful"),
    "llm_cognition_manual": ("--variant", "llm_cognition", "--manual"),
    "llm_cognition_light_halt": (
        "--variant", "llm_cognition", "--light", "--halt-on-core-bypass",
    ),
    "finance_legacy_variant": ("--variant", "finance_llm"),
    "finance_legacy_theory_flag": ("--variant", "finance", "--theory-llm"),
    "finance_duplicate_extensions": (
        "--variant", "finance",
        "--ext", "empirical", "--ext", "empirical",
        "--theory-llm", "--ext", "theory_llm",
    ),
    "finance_explicit_no_publish": ("--variant", "finance", "--no-publish"),
    "finance_synthetic_env": ("--variant", "finance", "--ext", "empirical"),
}

SYNTHETIC_ENV_CASES = {"finance_synthetic_env"}
SYNTHETIC_ENV = """# Synthetic characterization input — never use real credentials
OPENAI_API_KEY=synthetic-openai-canary
CUSTOM_LOCAL_ONLY=preserve-this-value
SEC_EDGAR_EMAIL=synthetic@example.invalid
"""

# These commands are safe even if validation regresses: every one remains in
# --local mode and targets the harness's temporary deployment root.  Exact
# diagnostics and exit codes are characterized because parser/validation
# behavior is part of the configuration extraction planned in issue #255.
CLI_FAILURE_CASES: dict[str, tuple[str, ...]] = {
    "missing_variant_value": ("--variant",),
    "missing_extension_value": ("--ext",),
    "missing_mode_value": ("--mode",),
    "unknown_option": ("--definitely-not-an-option",),
    "unknown_variant": ("--variant", "not_a_variant"),
    "unknown_extension": ("--variant", "finance", "--ext", "not_an_extension"),
    "unknown_mode": ("--variant", "finance", "--mode", "not-a-mode"),
    "seed_and_faithful": ("--variant", "finance", "--seed", "--faithful"),
    "manual_and_seed": ("--variant", "finance", "--manual", "--seed"),
    "report_and_manual": ("--variant", "finance", "--mode", "report", "--manual"),
    "report_and_seed": ("--variant", "finance", "--mode", "report", "--seed"),
    "macro_empirical_first": ("--variant", "macro", "--mode", "empirical-first"),
    "finance_measurement_first": ("--variant", "finance", "--mode", "measurement-first"),
    "llm_cognition_empirical": ("--variant", "llm_cognition", "--ext", "empirical"),
    "publish_and_local": ("--variant", "finance", "--publish"),
    "publish_and_no_publish": ("--variant", "finance", "--publish", "--no-publish"),
}

# These must omit --local to reach publish-only validation.  Their destination
# is created before invocation, so if a guard regresses the production path
# still stops at its existing-target check before clone/init/publish.
PRODUCTION_CLI_FAILURE_CASES: dict[str, tuple[tuple[str, ...], dict[str, str]]] = {
    "publish_report": (
        ("--variant", "finance", "--mode", "report", "--publish"),
        {},
    ),
    "publish_empty_org": (
        ("--variant", "finance", "--publish"),
        {"PUBLISH_ORG": ""},
    ),
    "publish_invalid_visibility": (
        ("--variant", "finance", "--publish"),
        {"PUBLISH_VISIBILITY": "not-a-visibility"},
    ),
}

CLI_TEXT_SUCCESS_CASES: dict[str, tuple[str, ...]] = {
    "short_help": ("-h",),
    "long_help": ("--help",),
}


def prepare_isolated_source(root: Path, name: str, synthetic_env: bool = False) -> Path:
    """Create the minimal --local source tree, never copying the real .env."""
    source = root / name
    source.mkdir()
    for name in ("setup.sh", "VERSION", "LICENSE", ".env.example"):
        candidate = REPO_ROOT / name
        if candidate.exists():
            shutil.copy2(candidate, source / name)
    (source / "deploy_assets").symlink_to(REPO_ROOT / "deploy_assets", target_is_directory=True)
    if synthetic_env:
        synthetic_path = source / ".env"
        synthetic_path.write_text(SYNTHETIC_ENV)
        # write_text() obeys the caller's umask, but setup's `cp` preserves the
        # source mode.  Pin the synthetic input so the fixed subprocess umask
        # truly makes permission characterization caller-independent.
        synthetic_path.chmod(0o644)
    return source


def fixed_umask_command(argv: list[str]) -> list[str]:
    # A fixed umask makes complete permission-mode characterization portable.
    # The positional-argument wrapper avoids interpolating any path into shell
    # source: after the label, "$@" is exactly the argv beginning with `bash`.
    return ["bash", "-c", 'umask 022; exec "$@"', "setup-characterization", *argv]


def setup_command(source: Path, output: Path, args: tuple[str, ...]) -> list[str]:
    setup_argv = [
        "bash", str(source / "setup.sh"), str(output),
        "--local", "--no-model-probe", *args,
    ]
    return fixed_umask_command(setup_argv)


def run_case(source: Path, deployment_root: Path, log_root: Path,
             name: str, args: tuple[str, ...]) -> Path:
    output = deployment_root / name
    result = subprocess.run(
        setup_command(source, output, args),
        cwd=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_root.mkdir(exist_ok=True)
    (log_root / f"{name}.log").write_text(result.stdout)
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-30:])
        raise RuntimeError(f"{name} failed with exit {result.returncode}:\n{tail}")
    return output


def run_cli_failure(source: Path, deployment_root: Path, log_root: Path,
                    name: str, args: tuple[str, ...]) -> dict[str, Any]:
    output = deployment_root / name
    result = subprocess.run(
        setup_command(source, output, args),
        cwd=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_root.mkdir(exist_ok=True)
    (log_root / f"cli_{name}.log").write_text(result.stdout)
    if result.returncode == 0:
        raise RuntimeError(f"CLI failure case unexpectedly succeeded: {name}")
    normalized = result.stdout
    for value, marker in (
        (str(output), "<DEPLOYMENT_PATH>"),
        (str(source), "<SOURCE_PATH>"),
        (str(REPO_ROOT), "<REPO_ROOT>"),
        (str(Path.home()), "<HOME>"),
    ):
        normalized = normalized.replace(value, marker)
    return {"args": list(args), "returncode": result.returncode, "output": normalized}


def run_production_cli_failure(
        source: Path, deployment_root: Path, log_root: Path, name: str,
        args: tuple[str, ...], environment: dict[str, str]) -> dict[str, Any]:
    output = deployment_root / name
    output.mkdir()
    command = fixed_umask_command([
        "bash", str(source / "setup.sh"), str(output), "--no-model-probe", *args,
    ])
    process_environment = dict(os.environ)
    # Publishing validation must not depend on the developer/runner's ambient
    # policy.  Start from setup.sh's documented defaults, then apply the one
    # explicit override each case is meant to exercise.
    process_environment.pop("PUBLISH_ORG", None)
    process_environment.pop("PUBLISH_VISIBILITY", None)
    process_environment.update(environment)
    result = subprocess.run(
        command,
        cwd=source,
        env=process_environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_root.mkdir(exist_ok=True)
    (log_root / f"cli_{name}.log").write_text(result.stdout)
    if result.returncode == 0:
        raise RuntimeError(f"production CLI failure case unexpectedly succeeded: {name}")
    normalized = result.stdout
    for value, marker in (
        (str(output), "<DEPLOYMENT_PATH>"),
        (str(source), "<SOURCE_PATH>"),
        (str(REPO_ROOT), "<REPO_ROOT>"),
        (str(Path.home()), "<HOME>"),
    ):
        normalized = normalized.replace(value, marker)
    return {
        "args": list(args),
        "environment": environment,
        "returncode": result.returncode,
        "output": normalized,
    }


def run_text_success(source: Path, log_root: Path,
                     name: str, args: tuple[str, ...]) -> dict[str, Any]:
    result = subprocess.run(
        fixed_umask_command(["bash", str(source / "setup.sh"), *args]),
        cwd=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_root.mkdir(exist_ok=True)
    (log_root / f"cli_{name}.log").write_text(result.stdout)
    if result.returncode != 0:
        raise RuntimeError(f"CLI success case failed with exit {result.returncode}: {name}")
    normalized = result.stdout
    for value, marker in (
        (str(source), "<SOURCE_PATH>"),
        (str(REPO_ROOT), "<REPO_ROOT>"),
        (str(Path.home()), "<HOME>"),
    ):
        normalized = normalized.replace(value, marker)
    return {"args": list(args), "returncode": result.returncode, "output": normalized}


def run_default_project_case(source: Path, log_root: Path) -> Path:
    args = ("--local", "--no-model-probe")
    result = subprocess.run(
        fixed_umask_command(["bash", str(source / "setup.sh"), *args]),
        cwd=source,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_root.mkdir(exist_ok=True)
    (log_root / "cli_default_local_project.log").write_text(result.stdout)
    if result.returncode:
        tail = "\n".join(result.stdout.splitlines()[-30:])
        raise RuntimeError(f"default local-project case failed:\n{tail}")
    output = source / "test_output" / "finance"
    if not output.is_dir():
        raise RuntimeError(f"default local project was not created at {output}")
    return output


def assert_identical_invocation_fingerprint_freshness(
        source: Path, log_root: Path, semver: str, revision: str,
        started_date: str) -> None:
    output = source / "test_output" / "fingerprint_freshness"
    args = ("--variant", "finance")
    command = setup_command(source, output, args)
    fingerprints: list[str] = []
    for attempt in (1, 2):
        result = subprocess.run(
            command,
            cwd=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        log_root.mkdir(exist_ok=True)
        (log_root / f"fingerprint_freshness_{attempt}.log").write_text(result.stdout)
        if result.returncode:
            tail = "\n".join(result.stdout.splitlines()[-30:])
            raise RuntimeError(f"fingerprint freshness attempt {attempt} failed:\n{tail}")
        manifest = json.loads((output / ".deploy_manifest.json").read_text())
        allowed_dates = {
            started_date,
            datetime.now(timezone.utc).date().isoformat(),
        }
        validate_and_normalize_manifest(manifest, semver, revision, allowed_dates)
        fingerprints.append(manifest["deploy_fingerprint"])
    if fingerprints[0] == fingerprints[1]:
        raise RuntimeError(
            "identical setup invocations reused deployment fingerprint: "
            f"{fingerprints[0]}"
        )


def expected_provenance() -> tuple[str, str]:
    semver = (REPO_ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", semver):
        raise RuntimeError(f"VERSION is not a plain semantic version: {semver!r}")
    revision = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]+", revision):
        raise RuntimeError(f"git produced an invalid short revision: {revision!r}")
    return semver, revision


def validate_and_normalize_manifest(manifest: dict[str, Any], semver: str,
                                    revision: str, allowed_dates: set[str]) -> dict[str, Any]:
    fingerprint = manifest.get("deploy_fingerprint")
    try:
        parsed_fingerprint = uuid.UUID(fingerprint)
    except (AttributeError, TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid deployment fingerprint: {fingerprint!r}") from exc
    if parsed_fingerprint.version != 4 or str(parsed_fingerprint) != fingerprint:
        raise RuntimeError(f"deployment fingerprint is not canonical UUIDv4: {fingerprint!r}")

    deploy_date = manifest.get("deploy_date")
    try:
        datetime.strptime(deploy_date, "%Y-%m-%d")
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid UTC deployment date: {deploy_date!r}") from exc
    if deploy_date not in allowed_dates:
        raise RuntimeError(
            f"deployment date {deploy_date!r} is not the harness run date {sorted(allowed_dates)}"
        )

    expected_version = f"{semver}+{revision}"
    if manifest.get("template_version") != expected_version:
        raise RuntimeError(
            "template provenance mismatch: "
            f"expected {expected_version!r}, got {manifest.get('template_version')!r}"
        )

    normalized = dict(manifest)
    normalized["template_version"] = f"{semver}+<GIT_REVISION>"
    normalized["deploy_date"] = "<DEPLOY_DATE>"
    normalized["deploy_fingerprint"] = "<DEPLOY_FINGERPRINT>"
    return normalized


def self_check_provenance_validation(semver: str, revision: str, today: str) -> None:
    valid = {
        "deploy_fingerprint": "123e4567-e89b-42d3-a456-426614174000",
        "deploy_date": today,
        "template_version": f"{semver}+{revision}",
    }
    validate_and_normalize_manifest(valid, semver, revision, {today})
    invalid_values = (
        ("deploy_fingerprint", "constant-not-a-uuid"),
        ("deploy_date", "not-a-date"),
        ("template_version", "broken-provenance"),
    )
    for key, value in invalid_values:
        candidate = dict(valid)
        candidate[key] = value
        try:
            validate_and_normalize_manifest(candidate, semver, revision, {today})
        except RuntimeError:
            continue
        raise RuntimeError(f"provenance validator accepted invalid {key}: {value!r}")


def normalized_bytes(path: Path, relative: str, manifest: dict[str, Any],
                     normalized_manifest: dict[str, Any]) -> bytes:
    raw = path.read_bytes()
    if relative == ".deploy_manifest.json":
        return (json.dumps(normalized_manifest, indent=2) + "\n").encode()

    if relative == "paper/arpipeline.sty":
        text = raw.decode()
        required = (
            rf"\newcommand{{\arpFingerprint}}{{{manifest['deploy_fingerprint']}}}",
            rf"\newcommand{{\arpVersion}}{{{manifest['template_version']}}}",
            rf"\newcommand{{\arpDeployed}}{{{manifest['deploy_date']}}}",
            f"ARPIPELINE-FP-V1::{manifest['deploy_fingerprint']}",
            f"ARPIPELINE-FP-V1::{manifest['template_version']}",
            f"ARPIPELINE-FP-V1::{manifest['deploy_date']}",
        )
        missing = [item for item in required if item not in text]
        if missing:
            raise RuntimeError(f"arpipeline.sty provenance disagrees with manifest: {missing}")
        for key in ("template_version", "deploy_date", "deploy_fingerprint"):
            raw = raw.replace(
                str(manifest[key]).encode(), str(normalized_manifest[key]).encode()
            )

    if relative == ".grok/sandbox.toml":
        raw = raw.replace(str(Path.home()).encode(), b"<HOME>")
    return raw


def characterize_tree(root: Path, semver: str, revision: str,
                      allowed_dates: set[str]) -> dict[str, Any]:
    manifest_path = root / ".deploy_manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"deployment has no manifest: {root}")
    manifest = json.loads(manifest_path.read_text())
    normalized_manifest = validate_and_normalize_manifest(
        manifest, semver, revision, allowed_dates
    )
    sty_path = root / "paper" / "arpipeline.sty"
    if manifest.get("mode") == "report":
        if sty_path.exists():
            raise RuntimeError("report deployment unexpectedly contains paper/arpipeline.sty")
    elif not sty_path.is_file():
        raise RuntimeError("non-report deployment has no paper/arpipeline.sty")

    root_mode = stat.S_IMODE(root.stat().st_mode)
    entries: dict[str, dict[str, Any]] = {".": {"type": "dir", "mode": f"{root_mode:04o}"}}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries[relative] = {"type": "symlink", "target": os.readlink(path)}
        elif path.is_dir():
            mode = stat.S_IMODE(path.stat().st_mode)
            entries[relative] = {"type": "dir", "mode": f"{mode:04o}"}
        elif path.is_file():
            data = normalized_bytes(path, relative, manifest, normalized_manifest)
            mode = stat.S_IMODE(path.stat().st_mode)
            entries[relative] = {
                "type": "file",
                "mode": f"{mode:04o}",
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        else:
            raise RuntimeError(f"unsupported filesystem entry: {path}")

    return {"manifest": normalized_manifest, "entries": entries}


def assert_unique_case_fingerprints(outputs: dict[str, Path]) -> None:
    seen: dict[str, str] = {}
    for name, root in outputs.items():
        manifest_path = root / ".deploy_manifest.json"
        if not manifest_path.is_file():
            raise RuntimeError(f"deployment has no manifest: {root}")
        fingerprint = json.loads(manifest_path.read_text()).get("deploy_fingerprint")
        if fingerprint in seen:
            raise RuntimeError(
                "deployment fingerprint was reused: "
                f"{fingerprint!r} appears in both {seen[fingerprint]} and {name}"
            )
        seen[fingerprint] = name


@contextmanager
def workspace(artifacts_dir: Path | None):
    if artifacts_dir is None:
        with tempfile.TemporaryDirectory(prefix="zeropaper-setup-characterization.") as tmp:
            yield Path(tmp)
        return
    target = artifacts_dir.resolve()
    if target.exists() and any(target.iterdir()):
        raise RuntimeError(f"--artifacts-dir must be absent or empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    yield target


def build_snapshot(selected: list[str], jobs: int, include_cli_contracts: bool,
                   artifacts_dir: Path | None) -> dict[str, Any]:
    started_date = datetime.now(timezone.utc).date().isoformat()
    semver, revision = expected_provenance()
    self_check_provenance_validation(semver, revision, started_date)
    with workspace(artifacts_dir) as temp_root:
        source = prepare_isolated_source(temp_root, "source")
        env_source = prepare_isolated_source(temp_root, "source_with_synthetic_env", True)
        deployments = temp_root / "deployments"
        logs = temp_root / "logs"
        deployments.mkdir()

        outputs: dict[str, Path] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
            futures = {
                executor.submit(
                    run_case,
                    env_source if name in SYNTHETIC_ENV_CASES else source,
                    deployments, logs, name, CASES[name],
                ): name
                for name in selected
            }
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    outputs[name] = future.result()
                    print(f"✓ built {name}", flush=True)
                except Exception:
                    for pending in futures:
                        pending.cancel()
                    raise

        default_output: Path | None = None
        if include_cli_contracts:
            default_source = prepare_isolated_source(temp_root, "source_default_project")
            default_output = run_default_project_case(default_source, logs)
            print("✓ built default_local_project", flush=True)
            freshness_source = prepare_isolated_source(temp_root, "source_fingerprint_freshness")
            assert_identical_invocation_fingerprint_freshness(
                freshness_source, logs, semver, revision, started_date
            )
            print("✓ verified identical-invocation fingerprint freshness", flush=True)

        allowed_dates = {
            started_date,
            datetime.now(timezone.utc).date().isoformat(),
        }
        # UUID syntax is checked per tree below; cross-case uniqueness must be
        # checked before normalization erases the raw values.  A separate
        # sequential probe above rebuilds one identical source+destination argv
        # twice to rule out configuration- or destination-keyed UUIDs.
        uniqueness_outputs = dict(outputs)
        if default_output is not None:
            uniqueness_outputs["default_local_project"] = default_output
        assert_unique_case_fingerprints(uniqueness_outputs)
        cases: dict[str, Any] = {}
        for name in selected:
            cases[name] = {
                "args": list(CASES[name]),
                **characterize_tree(outputs[name], semver, revision, allowed_dates),
            }

        cli_successes: dict[str, Any] = {}
        cli_failures: dict[str, Any] = {}
        if include_cli_contracts:
            assert default_output is not None
            cli_successes["default_local_project"] = {
                "args": ["--local", "--no-model-probe"],
                "resolved_project": "test_output/finance",
                **characterize_tree(default_output, semver, revision, allowed_dates),
            }
            for name, case_args in CLI_TEXT_SUCCESS_CASES.items():
                cli_successes[name] = run_text_success(source, logs, name, case_args)
                print(f"✓ accepted {name}", flush=True)
            failure_deployments = temp_root / "failure_deployments"
            failure_deployments.mkdir()
            for name, case_args in CLI_FAILURE_CASES.items():
                cli_failures[name] = run_cli_failure(
                    source, failure_deployments, logs, name, case_args
                )
                print(f"✓ rejected {name}", flush=True)
            for name, (case_args, environment) in PRODUCTION_CLI_FAILURE_CASES.items():
                cli_failures[name] = run_production_cli_failure(
                    source, failure_deployments, logs, name, case_args, environment
                )
                print(f"✓ rejected {name}", flush=True)

        if artifacts_dir is not None:
            print(f"Preserved deployments and logs in {temp_root}")
        return {
            "schema_version": 3,
            "normalization": [
                "validated UUIDv4 deployment fingerprint",
                "validated current UTC deployment date",
                "validated git revision (semantic VERSION is preserved)",
                "home directory in the generated Grok sandbox profile",
            ],
            "cases": cases,
            "cli_successes": cli_successes,
            "cli_failures": cli_failures,
        }


def print_case_difference(name: str, expected: dict[str, Any], actual: dict[str, Any]) -> None:
    expected_entries = expected["entries"]
    actual_entries = actual["entries"]
    missing = sorted(set(expected_entries) - set(actual_entries))
    extra = sorted(set(actual_entries) - set(expected_entries))
    changed = sorted(
        path for path in set(expected_entries) & set(actual_entries)
        if expected_entries[path] != actual_entries[path]
    )
    print(f"✗ {name}")
    if expected.get("args") != actual.get("args"):
        print(f"  case args changed: {expected.get('args')} -> {actual.get('args')}")
    for label, paths in (("missing", missing), ("extra", extra), ("changed", changed)):
        if paths:
            suffix = " ..." if len(paths) > 20 else ""
            print(f"  {label}: {', '.join(paths[:20])}{suffix}")
    if expected.get("manifest") != actual.get("manifest"):
        before = json.dumps(expected.get("manifest"), indent=2, sort_keys=True).splitlines()
        after = json.dumps(actual.get("manifest"), indent=2, sort_keys=True).splitlines()
        for line in difflib.unified_diff(before, after, fromfile="golden manifest", tofile="actual manifest"):
            print(f"  {line}")


def compare_snapshot(expected: dict[str, Any], actual: dict[str, Any], selected: list[str]) -> bool:
    if expected.get("schema_version") != actual.get("schema_version"):
        print("✗ characterization schema version differs")
        return False
    failed = False
    for name in selected:
        if name not in expected.get("cases", {}):
            print(f"✗ golden inventory has no case named {name}")
            failed = True
        elif expected["cases"][name] != actual["cases"][name]:
            print_case_difference(name, expected["cases"][name], actual["cases"][name])
            failed = True
        else:
            print(f"✓ matched {name}")
    return not failed


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", choices=tuple(CASES),
                        help="run one named case (repeatable); default: full matrix")
    parser.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1),
                        help="parallel setup builds (default: up to 4)")
    parser.add_argument("--actual", type=Path,
                        help="also write the generated inventory to this path")
    parser.add_argument("--artifacts-dir", type=Path,
                        help="preserve complete deployments and logs in an absent/empty directory")
    parser.add_argument("--update-golden", action="store_true",
                        help="replace the committed full-matrix inventory")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    if args.update_golden and args.case:
        parser.error("--update-golden always covers the full matrix; omit --case")
    return args


def main() -> int:
    args = parse_args()
    selected = args.case or list(CASES)
    include_cli_contracts = not args.case
    actual = build_snapshot(selected, args.jobs, include_cli_contracts, args.artifacts_dir)
    if args.actual:
        write_json(args.actual, actual)
        print(f"Wrote actual inventory to {args.actual}")
    if args.update_golden:
        write_json(GOLDEN_PATH, actual)
        print(f"Updated golden inventory: {GOLDEN_PATH}")
        return 0
    if not GOLDEN_PATH.is_file():
        print(f"Golden inventory is missing: {GOLDEN_PATH}", file=sys.stderr)
        print("Run with --update-golden after reviewing the generated deployments.", file=sys.stderr)
        return 2
    expected = json.loads(GOLDEN_PATH.read_text())
    if not args.case and set(expected.get("cases", {})) != set(CASES):
        print("✗ golden case set differs from the maintained matrix")
        print(f"  expected: {sorted(expected.get('cases', {}))}")
        print(f"  current:  {sorted(CASES)}")
        return 1
    expected_cli_failures = set(CLI_FAILURE_CASES) | set(PRODUCTION_CLI_FAILURE_CASES)
    if not args.case and set(expected.get("cli_failures", {})) != expected_cli_failures:
        print("✗ golden CLI-failure set differs from the maintained matrix")
        print(f"  expected: {sorted(expected.get('cli_failures', {}))}")
        print(f"  current:  {sorted(expected_cli_failures)}")
        return 1
    expected_cli_successes = set(CLI_TEXT_SUCCESS_CASES) | {"default_local_project"}
    if not args.case and set(expected.get("cli_successes", {})) != expected_cli_successes:
        print("✗ golden CLI-success set differs from the maintained matrix")
        print(f"  expected: {sorted(expected.get('cli_successes', {}))}")
        print(f"  current:  {sorted(expected_cli_successes)}")
        return 1
    if not compare_snapshot(expected, actual, selected):
        print("Characterization drift detected. Use --actual for the candidate inventory")
        print("and --artifacts-dir with an absent/empty path to preserve deployments and logs.")
        return 1
    if include_cli_contracts and expected.get("cli_successes") != actual.get("cli_successes"):
        print("✗ CLI success contracts changed")
        before = json.dumps(expected.get("cli_successes"), indent=2, sort_keys=True).splitlines()
        after = json.dumps(actual.get("cli_successes"), indent=2, sort_keys=True).splitlines()
        for line in difflib.unified_diff(before, after, fromfile="golden CLI successes", tofile="actual CLI successes"):
            print(line)
        return 1
    if include_cli_contracts and expected.get("cli_failures") != actual.get("cli_failures"):
        print("✗ CLI failure contracts changed")
        before = json.dumps(expected.get("cli_failures"), indent=2, sort_keys=True).splitlines()
        after = json.dumps(actual.get("cli_failures"), indent=2, sort_keys=True).splitlines()
        for line in difflib.unified_diff(before, after, fromfile="golden CLI failures", tofile="actual CLI failures"):
            print(line)
        return 1
    print(f"All {len(selected)} setup characterization case(s) matched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
