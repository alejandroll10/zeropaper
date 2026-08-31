#!/usr/bin/env python3
"""Validate and compare parsimonious empirical analysis contracts.

This module intentionally validates scientific identity and graph closure, not a
catalogue of estimators.  The values inside each definition remain open JSON.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SECTIONS = ("inputs", "samples", "variables", "procedures", "inference", "outputs")


class ContractError(RuntimeError):
    pass


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ContractError(f"non-finite JSON number: {value}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read valid JSON from {path}: {exc}") from exc


def semantic_digest(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractError(f"value is not canonical JSON: {exc}") from exc
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _json_equal(left: Any, right: Any) -> bool:
    return semantic_digest(left) == semantic_digest(right)


def _keys(value: Any, required: set[str], allowed: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{where} must be an object")
    missing = sorted(required - value.keys())
    extra = sorted(value.keys() - allowed)
    if missing:
        raise ContractError(f"{where} missing required keys: {', '.join(missing)}")
    if extra:
        raise ContractError(f"{where} has unsupported keys: {', '.join(extra)}")
    return value


def _identifier(value: Any, where: str) -> str:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        raise ContractError(f"{where} must be a lowercase stable identifier")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{where} must be a non-empty string")
    return value


def _substantive(value: Any, where: str) -> Any:
    if value is None or isinstance(value, bool):
        raise ContractError(f"{where} must contain a substantive value")
    if isinstance(value, str) and not value.strip():
        raise ContractError(f"{where} must not be empty")
    if isinstance(value, (list, dict)) and not value:
        raise ContractError(f"{where} must not be empty")
    return value


def _id_map(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{where} must be an object keyed by stable IDs")
    for key, item in value.items():
        _identifier(key, f"{where} key")
        if not isinstance(item, dict):
            raise ContractError(f"{where}.{key} must be an object")
    return value


def _sections(value: Any, where: str, *, complete: bool) -> dict[str, Any]:
    required = set(SECTIONS) if complete else set()
    obj = _keys(value, required, set(SECTIONS), where)
    for section in SECTIONS:
        if section in obj:
            _id_map(obj[section], f"{where}.{section}")
    return obj


def _string_ids(value: Any, where: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise ContractError(f"{where} must be {'a non-empty' if nonempty else 'an'} array")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_identifier(item, f"{where}[{index}]"))
    if len(result) != len(set(result)):
        raise ContractError(f"{where} contains duplicates")
    return result


def _references(value: dict[str, Any], key: str, available: Iterable[str], where: str,
                *, required: bool = False) -> list[str]:
    if key not in value:
        if required:
            raise ContractError(f"{where}.{key} is required")
        return []
    refs = _string_ids(value[key], f"{where}.{key}", nonempty=required)
    missing = sorted(set(refs) - set(available))
    if missing:
        raise ContractError(f"{where}.{key} references unknown IDs: {', '.join(missing)}")
    return refs


def _decision_domain(value: Any, where: str) -> Any:
    if isinstance(value, list):
        if not value:
            raise ContractError(f"{where} must not be empty")
        return value
    domain = _keys(
        value, {"type"},
        {"type", "minimum", "maximum", "exclusive_minimum", "exclusive_maximum"},
        where,
    )
    if domain["type"] not in {"number", "integer"}:
        raise ContractError(f"{where}.type must be number or integer")
    bounds = [key for key in (
        "minimum", "maximum", "exclusive_minimum", "exclusive_maximum"
    ) if key in domain]
    for key in bounds:
        bound = domain[key]
        if isinstance(bound, bool) or not isinstance(bound, (int, float)):
            raise ContractError(f"{where}.{key} must be numeric")
    if "minimum" in domain and "exclusive_minimum" in domain:
        raise ContractError(f"{where} cannot have minimum and exclusive_minimum")
    if "maximum" in domain and "exclusive_maximum" in domain:
        raise ContractError(f"{where} cannot have maximum and exclusive_maximum")
    if not ({"minimum", "exclusive_minimum"} & set(domain)):
        raise ContractError(f"{where} numeric domain needs a lower bound")
    if not ({"maximum", "exclusive_maximum"} & set(domain)):
        raise ContractError(f"{where} numeric domain needs an upper bound")
    lower = domain.get("minimum", domain.get("exclusive_minimum"))
    upper = domain.get("maximum", domain.get("exclusive_maximum"))
    if lower is not None and upper is not None and lower >= upper:
        raise ContractError(f"{where} lower bound must be below upper bound")
    return domain


def _decision_allows(domain: Any, realization: Any) -> bool:
    if isinstance(domain, list):
        return any(
            semantic_digest(realization) == semantic_digest(candidate)
            for candidate in domain
        )
    if isinstance(realization, bool) or not isinstance(realization, (int, float)):
        return False
    if domain["type"] == "integer" and not isinstance(realization, int):
        return False
    if "minimum" in domain and realization < domain["minimum"]:
        return False
    if "exclusive_minimum" in domain and realization <= domain["exclusive_minimum"]:
        return False
    if "maximum" in domain and realization > domain["maximum"]:
        return False
    if "exclusive_maximum" in domain and realization >= domain["exclusive_maximum"]:
        return False
    return True


def _count_map(value: Any, where: str) -> dict[str, Any]:
    counts = _id_map(value, where)
    if not counts:
        raise ContractError(f"{where} must not be empty")
    for count_id, count in counts.items():
        count_where = f"{where}.{count_id}"
        _keys(count, {"value", "unit"}, {"value", "unit"}, count_where)
        if isinstance(count["value"], bool) or not isinstance(
                count["value"], (int, float)):
            raise ContractError(f"{count_where}.value must be numeric")
        if count["value"] < 0:
            raise ContractError(f"{count_where}.value must be nonnegative")
        _text(count["unit"], f"{count_where}.unit")
    return counts


def validate_baseline(value: Any) -> dict[str, Any]:
    obj = _keys(
        value, {"schema_version", "record_kind", "baseline_id", "definitions"},
        {"schema_version", "record_kind", "baseline_id", "definitions", "notes"},
        "baseline",
    )
    if obj["schema_version"] != 1 or isinstance(obj["schema_version"], bool):
        raise ContractError("baseline.schema_version must be 1")
    if obj["record_kind"] != "project_baseline":
        raise ContractError("baseline.record_kind must be project_baseline")
    _identifier(obj["baseline_id"], "baseline.baseline_id")
    _sections(obj["definitions"], "baseline.definitions", complete=False)
    if "notes" in obj:
        _text(obj["notes"], "baseline.notes")
    return obj


def _validate_sample(sample_id: str, sample: dict[str, Any], inputs: set[str]) -> None:
    where = f"contract.effective.samples.{sample_id}"
    required = {"population", "observation_unit", "observation_key", "time", "steps", "step_order"}
    _keys(sample, required, required | {
        "frequency", "window", "details", "purpose", "variant_of", "variant_reason"
    }, where)
    for key in ("population", "observation_unit"):
        _text(sample[key], f"{where}.{key}")
    if not isinstance(sample["observation_key"], (str, list)):
        raise ContractError(f"{where}.observation_key must be a string or array")
    _substantive(sample["observation_key"], f"{where}.observation_key")
    if isinstance(sample["observation_key"], list) and any(
            not isinstance(item, str) or not item.strip()
            for item in sample["observation_key"]):
        raise ContractError(f"{where}.observation_key entries must be non-empty strings")
    if (isinstance(sample["observation_key"], list) and
            len(sample["observation_key"]) != len(set(sample["observation_key"]))):
        raise ContractError(f"{where}.observation_key contains duplicates")
    if not isinstance(sample["time"], dict) or not sample["time"]:
        raise ContractError(f"{where}.time must be a non-empty open object")
    for key in ("frequency", "window"):
        if key in sample:
            _substantive(sample[key], f"{where}.{key}")
    steps = _id_map(sample["steps"], f"{where}.steps")
    if not steps:
        raise ContractError(f"{where}.steps must not be empty")
    order = _string_ids(sample["step_order"], f"{where}.step_order")
    if set(order) != set(steps):
        raise ContractError(f"{where}.step_order must contain every step exactly once")
    available = set(inputs)
    for step_id in order:
        step = steps[step_id]
        _keys(step, {"description", "uses", "produces", "rule"},
              {"description", "uses", "produces", "rule", "settings", "purpose"},
              f"{where}.steps.{step_id}")
        _text(step["description"], f"{where}.steps.{step_id}.description")
        _substantive(step["rule"], f"{where}.steps.{step_id}.rule")
        uses = _string_ids(step["uses"], f"{where}.steps.{step_id}.uses", nonempty=True)
        missing = sorted(set(uses) - available)
        if missing:
            raise ContractError(
                f"{where}.steps.{step_id}.uses references unavailable IDs: {', '.join(missing)}"
            )
        produces = _string_ids(
            step["produces"], f"{where}.steps.{step_id}.produces", nonempty=True
        )
        overlap = sorted(set(produces) & available)
        if overlap:
            raise ContractError(f"{where}.steps.{step_id} redefines IDs: {', '.join(overlap)}")
        available.update(produces)


def _validate_procedure_graph(procedures: dict[str, Any], samples: set[str],
                              variables: set[str], inference: set[str]) -> None:
    dependencies: dict[str, set[str]] = {}
    for procedure_id, procedure in procedures.items():
        where = f"contract.effective.procedures.{procedure_id}"
        required = {"target", "method", "sample_ids", "variable_ids", "inference_id", "result_ids"}
        allowed = required | {
            "procedure_ids", "estimand", "design", "assumptions", "settings",
            "decision_rules", "seed", "tuning", "purpose", "details",
            "variant_of", "variant_reason",
        }
        _keys(procedure, required, allowed, where)
        _text(procedure["target"], f"{where}.target")
        _text(procedure["method"], f"{where}.method")
        _references(procedure, "sample_ids", samples, where, required=True)
        _references(procedure, "variable_ids", variables, where)
        inf = _identifier(procedure["inference_id"], f"{where}.inference_id")
        if inf not in inference:
            raise ContractError(f"{where}.inference_id references unknown ID: {inf}")
        _string_ids(procedure["result_ids"], f"{where}.result_ids", nonempty=True)
        dependencies[procedure_id] = set(
            _references(procedure, "procedure_ids", procedures, where)
        )
        if "decision_rules" in procedure:
            rules = _id_map(procedure["decision_rules"], f"{where}.decision_rules")
            for rule_id, rule in rules.items():
                _keys(rule, {"description", "allowed"}, {"description", "allowed"},
                      f"{where}.decision_rules.{rule_id}")
                _text(rule["description"], f"{where}.decision_rules.{rule_id}.description")
                _decision_domain(
                    rule["allowed"], f"{where}.decision_rules.{rule_id}.allowed"
                )
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ContractError(f"procedure dependency cycle includes {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in dependencies[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in procedures:
        visit(node)


def _pointer_escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _baseline_deviation_paths(definitions: dict[str, Any],
                              effective: dict[str, Any]) -> set[str]:
    """Return identity-level baseline changes, excluding genuinely new definitions."""
    result: set[str] = set()
    for section, baseline_items in definitions.items():
        for item_id, baseline_item in baseline_items.items():
            pointer = f"/effective/{_pointer_escape(section)}/{_pointer_escape(item_id)}"
            if (item_id not in effective[section] or
                    not _json_equal(effective[section][item_id], baseline_item)):
                result.add(pointer)
        for item_id, item in effective[section].items():
            if item_id not in baseline_items and item.get("variant_of") in baseline_items:
                result.add(
                    f"/effective/{_pointer_escape(section)}/{_pointer_escape(item_id)}"
                )
    return result


def validate_contract(value: Any, baseline: Any) -> dict[str, Any]:
    baseline = validate_baseline(baseline)
    obj = _keys(
        value,
        {"schema_version", "record_kind", "analysis_id", "purpose", "baseline", "effective", "deviations"},
        {"schema_version", "record_kind", "analysis_id", "purpose", "baseline", "effective", "deviations", "reference_analysis_id", "notes"},
        "contract",
    )
    if obj["schema_version"] != 1 or isinstance(obj["schema_version"], bool):
        raise ContractError("contract.schema_version must be 1")
    if obj["record_kind"] != "analysis_contract":
        raise ContractError("contract.record_kind must be analysis_contract")
    _identifier(obj["analysis_id"], "contract.analysis_id")
    _text(obj["purpose"], "contract.purpose")
    if "reference_analysis_id" in obj:
        _identifier(obj["reference_analysis_id"], "contract.reference_analysis_id")
        if obj["reference_analysis_id"] == obj["analysis_id"]:
            raise ContractError("contract.reference_analysis_id cannot equal analysis_id")
    baseline_ref = _keys(obj["baseline"], {"path", "semantic_digest"},
                         {"path", "semantic_digest"}, "contract.baseline")
    _text(baseline_ref["path"], "contract.baseline.path")
    if baseline_ref["semantic_digest"] != semantic_digest(baseline):
        raise ContractError("contract.baseline.semantic_digest does not match baseline")
    effective = _sections(obj["effective"], "contract.effective", complete=True)
    for section in SECTIONS:
        if not effective[section]:
            raise ContractError(f"contract.effective.{section} must not be empty")
    inputs = set(effective["inputs"])
    samples = set(effective["samples"])
    variables = set(effective["variables"])
    inference = set(effective["inference"])
    procedures = effective["procedures"]
    outputs = effective["outputs"]
    for input_id, input_value in effective["inputs"].items():
        where = f"contract.effective.inputs.{input_id}"
        _keys(input_value, {"description", "access", "snapshot"},
              {"description", "access", "snapshot", "disclosure", "purpose", "variant_of", "variant_reason", "details"}, where)
        _text(input_value["description"], f"{where}.description")
        _substantive(input_value["access"], f"{where}.access")
        _substantive(input_value["snapshot"], f"{where}.snapshot")
    for sample_id, sample in effective["samples"].items():
        _validate_sample(sample_id, sample, inputs)
    for variable_id, variable in effective["variables"].items():
        where = f"contract.effective.variables.{variable_id}"
        _keys(variable, {"definition", "input_ids", "timing", "unit", "construction", "missing_policy", "roles"},
              {"definition", "input_ids", "timing", "unit", "construction", "missing_policy", "roles", "purpose", "variant_of", "variant_reason", "details"}, where)
        _text(variable["definition"], f"{where}.definition")
        _references(variable, "input_ids", inputs, where, required=True)
        _string_ids(variable["roles"], f"{where}.roles", nonempty=True)
        for key in ("timing", "unit", "construction", "missing_policy"):
            _substantive(variable[key], f"{where}.{key}")
    for inference_id, inference_value in effective["inference"].items():
        where = f"contract.effective.inference.{inference_id}"
        _keys(
            inference_value, {"method", "uncertainty_target"},
            {"method", "uncertainty_target", "cluster_dimensions", "resampling",
             "corrections", "repetitions", "seed", "multiplicity", "details",
             "purpose", "variant_of", "variant_reason"}, where,
        )
        _text(inference_value["method"], f"{where}.method")
        _text(inference_value["uncertainty_target"], f"{where}.uncertainty_target")
        for key in ("cluster_dimensions", "resampling", "corrections", "repetitions",
                    "seed", "multiplicity"):
            if key in inference_value:
                _substantive(inference_value[key], f"{where}.{key}")
    _validate_procedure_graph(procedures, samples, variables, inference)
    owned: set[str] = set()
    for output_id, output in outputs.items():
        where = f"contract.effective.outputs.{output_id}"
        _keys(output, {"description", "procedure_ids", "target", "unit", "presentation"},
              {"description", "procedure_ids", "target", "contrast", "unit", "presentation", "operands", "comparability", "purpose", "variant_of", "variant_reason", "details"}, where)
        _text(output["description"], f"{where}.description")
        _references(output, "procedure_ids", procedures, where, required=True)
        _substantive(output["target"], f"{where}.target")
        _text(output["unit"], f"{where}.unit")
        if not isinstance(output["presentation"], dict) or not output["presentation"]:
            raise ContractError(f"{where}.presentation must be a non-empty object")
        if "operands" in output:
            operands = output["operands"]
            if not isinstance(operands, list) or not operands:
                raise ContractError(f"{where}.operands must be a non-empty array")
            for index, operand in enumerate(operands):
                _keys(operand, {"receipt", "result_id"}, {"receipt", "result_id"},
                      f"{where}.operands[{index}]")
                _text(operand["receipt"], f"{where}.operands[{index}].receipt")
                _identifier(operand["result_id"], f"{where}.operands[{index}].result_id")
            if "comparability" not in output:
                raise ContractError(f"{where}.comparability is required with operands")
            _substantive(output["comparability"], f"{where}.comparability")
        owned.add(output_id)
    declared = set()
    for procedure in procedures.values():
        declared.update(procedure["result_ids"])
    if declared != owned:
        raise ContractError("procedure result_ids must equal effective.outputs IDs")
    for procedure_id, procedure in procedures.items():
        for result_id in procedure["result_ids"]:
            if procedure_id not in outputs[result_id]["procedure_ids"]:
                raise ContractError(
                    f"procedure/output edge is one-sided: {procedure_id} -> {result_id}"
                )
    for result_id, output in outputs.items():
        for procedure_id in output["procedure_ids"]:
            if result_id not in procedures[procedure_id]["result_ids"]:
                raise ContractError(
                    f"procedure/output edge is one-sided: {result_id} -> {procedure_id}"
                )

    definitions = baseline["definitions"]
    for section in SECTIONS:
        baseline_items = definitions.get(section, {})
        effective_items = effective[section]
        for item_id, baseline_item in baseline_items.items():
            if (item_id in effective_items and
                    not _json_equal(effective_items[item_id], baseline_item)):
                raise ContractError(
                    f"baseline-owned ID changed in place: effective.{section}.{item_id}; use a new ID with variant_of"
                )
        for item_id, item in effective_items.items():
            if item_id in baseline_items:
                continue
            variant_of = item.get("variant_of")
            if variant_of is not None:
                _identifier(variant_of, f"effective.{section}.{item_id}.variant_of")
                if variant_of not in baseline_items:
                    raise ContractError(f"effective.{section}.{item_id}.variant_of is not a baseline ID")
                _text(item.get("variant_reason"), f"effective.{section}.{item_id}.variant_reason")
            elif "purpose" not in item:
                raise ContractError(f"new effective.{section}.{item_id} needs purpose or variant_of")
            else:
                _text(item["purpose"], f"effective.{section}.{item_id}.purpose")
            stripped = {key: val for key, val in item.items()
                        if key not in {"purpose", "variant_of", "variant_reason"}}
            for baseline_id, baseline_item in baseline_items.items():
                baseline_stripped = {
                    key: val for key, val in baseline_item.items()
                    if key not in {"purpose", "variant_of", "variant_reason"}
                }
                if _json_equal(stripped, baseline_stripped):
                    raise ContractError(
                        f"effective.{section}.{item_id} relabels baseline ID {baseline_id} without a scientific change"
                    )

    changes = _baseline_deviation_paths(definitions, effective)
    explained: set[str] = set()
    if not isinstance(obj["deviations"], list):
        raise ContractError("contract.deviations must be an array")
    for index, deviation in enumerate(obj["deviations"]):
        where = f"contract.deviations[{index}]"
        _keys(deviation, {"paths", "reason"}, {"paths", "reason"}, where)
        _text(deviation["reason"], f"{where}.reason")
        if not isinstance(deviation["paths"], list) or not deviation["paths"]:
            raise ContractError(f"{where}.paths must be a non-empty array")
        for path in deviation["paths"]:
            if not isinstance(path, str) or not path.startswith("/effective/"):
                raise ContractError(f"{where}.paths entries must be /effective JSON pointers")
            if path in explained:
                raise ContractError(f"deviation path is explained twice: {path}")
            explained.add(path)
    if changes != explained:
        missing = sorted(changes - explained)
        extra = sorted(explained - changes)
        detail = []
        if missing:
            detail.append("unexplained: " + ", ".join(missing))
        if extra:
            detail.append("not changed: " + ", ".join(extra))
        raise ContractError("deviations do not exactly cover baseline differences (" + "; ".join(detail) + ")")
    return obj


def validate_execution(value: Any, contract: dict[str, Any]) -> dict[str, Any]:
    obj = _keys(value, {"schema_version", "analysis_id", "contract_digest", "samples", "procedures"},
                {"schema_version", "analysis_id", "contract_digest", "samples", "procedures", "notes"},
                "execution summary")
    if obj["schema_version"] != 1 or isinstance(obj["schema_version"], bool):
        raise ContractError("execution summary.schema_version must be 1")
    if obj["analysis_id"] != contract["analysis_id"]:
        raise ContractError("execution summary.analysis_id differs from contract")
    if obj["contract_digest"] != semantic_digest(contract):
        raise ContractError("execution summary.contract_digest differs from contract")
    samples = _id_map(obj["samples"], "execution summary.samples")
    procedures = _id_map(obj["procedures"], "execution summary.procedures")
    if set(samples) != set(contract["effective"]["samples"]):
        raise ContractError("execution summary samples must equal contract samples")
    if set(procedures) != set(contract["effective"]["procedures"]):
        raise ContractError("execution summary procedures must equal contract procedures")
    for sample_id, sample in samples.items():
        where = f"execution summary.samples.{sample_id}"
        _keys(
            sample, {"observed_time", "key_diagnostics", "steps"},
            {"observed_time", "key_diagnostics", "steps", "notes"}, where,
        )
        if not isinstance(sample["observed_time"], dict) or not sample["observed_time"]:
            raise ContractError(f"{where}.observed_time must be a non-empty object")
        for key, value in sample["observed_time"].items():
            _text(key, f"{where}.observed_time key")
            _substantive(value, f"{where}.observed_time.{key}")
        diagnostics = _keys(
            sample["key_diagnostics"], {"is_unique", "duplicate_key_count"},
            {"is_unique", "duplicate_key_count", "details"},
            f"{where}.key_diagnostics",
        )
        if not isinstance(diagnostics["is_unique"], bool):
            raise ContractError(f"{where}.key_diagnostics.is_unique must be boolean")
        duplicate = diagnostics["duplicate_key_count"]
        _keys(
            duplicate, {"value", "unit"}, {"value", "unit"},
            f"{where}.key_diagnostics.duplicate_key_count",
        )
        if (isinstance(duplicate["value"], bool) or
                not isinstance(duplicate["value"], int) or
                duplicate["value"] < 0):
            raise ContractError(
                f"{where}.key_diagnostics.duplicate_key_count.value "
                "must be a nonnegative integer"
            )
        _text(
            duplicate["unit"], f"{where}.key_diagnostics.duplicate_key_count.unit"
        )
        if diagnostics["is_unique"] != (duplicate["value"] == 0):
            raise ContractError(
                f"{where}.key_diagnostics uniqueness contradicts duplicate_key_count"
            )
        steps = _id_map(sample["steps"], f"{where}.steps")
        expected_steps = contract["effective"]["samples"][sample_id]["steps"]
        if set(steps) != set(expected_steps):
            raise ContractError(f"{where}.steps must equal contract sample steps")
        for step_id, step in steps.items():
            step_where = f"{where}.steps.{step_id}"
            _keys(
                step, {"counts", "flow", "fingerprint"},
                {"counts", "flow", "fingerprint", "notes"}, step_where,
            )
            counts = _count_map(step["counts"], f"{step_where}.counts")
            flow = _keys(
                step["flow"], {"inputs", "outputs"}, {"inputs", "outputs"},
                f"{step_where}.flow",
            )
            contract_step = expected_steps[step_id]
            for direction, expected_ids in (
                    ("inputs", contract_step["uses"]),
                    ("outputs", contract_step["produces"])):
                mapping = flow[direction]
                if not isinstance(mapping, dict) or set(mapping) != set(expected_ids):
                    raise ContractError(
                        f"{step_where}.flow.{direction} must map every declared "
                        f"{'uses' if direction == 'inputs' else 'produces'} ID"
                    )
                for data_id, count_id in mapping.items():
                    count_id = _identifier(
                        count_id, f"{step_where}.flow.{direction}.{data_id}"
                    )
                    if count_id not in counts:
                        raise ContractError(
                            f"{step_where}.flow.{direction}.{data_id} references "
                            f"unknown count {count_id}"
                        )
            if (not isinstance(step["fingerprint"], str) or
                    DIGEST_RE.fullmatch(step["fingerprint"]) is None):
                raise ContractError(f"{step_where}.fingerprint must be a SHA-256 digest")
    for procedure_id, realized in procedures.items():
        where = f"execution summary.procedures.{procedure_id}"
        _keys(realized, {"fixed_settings", "decisions", "counts"},
              {"fixed_settings", "decisions", "seed", "tuning", "counts", "notes"}, where)
        if not _json_equal(
                realized["fixed_settings"],
                contract["effective"]["procedures"][procedure_id].get("settings", {})):
            raise ContractError(f"{where}.fixed_settings differs from contract settings")
        decisions = realized["decisions"]
        if not isinstance(decisions, dict):
            raise ContractError(f"{where}.decisions must be an object")
        rules = contract["effective"]["procedures"][procedure_id].get("decision_rules", {})
        if set(decisions) != set(rules):
            raise ContractError(f"{where}.decisions must realize every declared decision rule")
        for rule_id, realization in decisions.items():
            if not _decision_allows(rules[rule_id]["allowed"], realization):
                raise ContractError(f"{where}.decisions.{rule_id} is outside its allowed domain")
        procedure = contract["effective"]["procedures"][procedure_id]
        for key in ("seed", "tuning"):
            if (key in realized) != (key in procedure):
                raise ContractError(f"{where}.{key} presence differs from contract")
            if key in procedure and not _json_equal(realized[key], procedure[key]):
                raise ContractError(f"{where}.{key} differs from contract")
        _count_map(realized["counts"], f"{where}.counts")
    return obj


def lineage_projection(contract: dict[str, Any], execution: dict[str, Any],
                       result_ids: Iterable[str]) -> dict[str, Any]:
    return {
        "analysis_id": contract["analysis_id"],
        "baseline_digest": contract["baseline"]["semantic_digest"],
        "contract_digest": semantic_digest(contract),
        "execution_summary_digest": semantic_digest(execution),
        "result_ids": sorted(result_ids),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", nargs="?")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--execution")
    parser.add_argument("--scaffold", metavar="OUTPUT")
    parser.add_argument("--analysis-id")
    parser.add_argument("--purpose")
    parser.add_argument("--reference-analysis-id")
    args = parser.parse_args(argv)
    try:
        baseline_path = Path(args.baseline)
        baseline = validate_baseline(load_json(baseline_path))
        if args.scaffold:
            if args.contract is not None or args.execution is not None:
                raise ContractError("--scaffold cannot be combined with a contract or execution")
            analysis_id = _identifier(args.analysis_id, "--analysis-id")
            purpose = _text(args.purpose, "--purpose")
            effective = {section: copy.deepcopy(
                baseline["definitions"].get(section, {})
            ) for section in SECTIONS}
            scaffold: dict[str, Any] = {
                "schema_version": 1,
                "record_kind": "analysis_contract",
                "analysis_id": analysis_id,
                "purpose": purpose,
                "baseline": {
                    "path": args.baseline,
                    "semantic_digest": semantic_digest(baseline),
                },
                "effective": effective,
                "deviations": [],
            }
            if args.reference_analysis_id:
                scaffold["reference_analysis_id"] = _identifier(
                    args.reference_analysis_id, "--reference-analysis-id"
                )
            output = Path(args.scaffold)
            try:
                with output.open("x", encoding="utf-8") as handle:
                    json.dump(scaffold, handle, indent=2, sort_keys=True)
                    handle.write("\n")
            except FileExistsError as exc:
                raise ContractError(f"scaffold output already exists: {output}") from exc
            except OSError as exc:
                raise ContractError(f"cannot write scaffold {output}: {exc}") from exc
            print(json.dumps({"scaffold": str(output)}, sort_keys=True))
            return 0
        if args.contract is None:
            raise ContractError("a contract path is required unless --scaffold is used")
        contract = validate_contract(load_json(Path(args.contract)), baseline)
        output: dict[str, Any] = {"contract_digest": semantic_digest(contract)}
        if args.execution:
            execution = validate_execution(load_json(Path(args.execution)), contract)
            output["execution_summary_digest"] = semantic_digest(execution)
        print(json.dumps(output, sort_keys=True))
        return 0
    except ContractError as exc:
        print(f"analysis_contract: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
