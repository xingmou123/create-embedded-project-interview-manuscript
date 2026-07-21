#!/usr/bin/env python3
"""Validate the manuscript clarification gate before formal delivery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = {
    "source_fact",
    "engineering_parameter",
    "technical_route",
    "personal_responsibility",
    "product_form",
    "project_boundary",
}
ALLOWED_RESOLUTIONS = {"source", "architect", "user"}
USER_DECISION_CATEGORIES = {
    "personal_responsibility",
    "product_form",
    "project_boundary",
}
EXPECTED_DEFAULTS = {
    "delivery_maturity": "small_batch_design_target",
    "debugging_case_nature": "evidence_driven",
    "provided_quantitative_results": "evidence_driven",
}
ALLOWED_OVERRIDE_VALUES = {
    "delivery_maturity": {
        "prototype",
        "engineering_validation",
        "small_batch",
        "mass_production",
    },
    "debugging_case_nature": {
        "confirmed_real",
        "fault_injection",
        "design_inference",
    },
    "provided_quantitative_results": {
        "confirmed_real",
        "design_parameter",
        "unverified",
    },
}
ALLOWED_RESOLUTIONS_BY_CATEGORY = {
    "source_fact": {"source"},
    "engineering_parameter": {"source", "architect"},
    "technical_route": {"source", "architect"},
    "personal_responsibility": {"source", "user"},
    "product_form": {"source", "user"},
    "project_boundary": {"source", "user"},
}


def require_type(data: dict[str, Any], key: str, expected: type) -> Any:
    if key not in data:
        raise ValueError(f"missing required field: {key}")
    value = data[key]
    if type(value) is not expected:
        raise ValueError(f"{key} must be {expected.__name__}")
    return value


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    try:
        version = require_type(payload, "version", int)
        project = require_type(payload, "project", str)
        defaults = require_type(payload, "global_defaults", dict)
        overrides = require_type(payload, "explicit_overrides", list)
        questions_asked = require_type(payload, "questions_asked", bool)
        brief_confirmed = require_type(payload, "brief_confirmed", bool)
        issues = require_type(payload, "issues", list)
    except ValueError as exc:
        return [str(exc)]

    if version != 1:
        errors.append("version must be 1")
    if not project.strip():
        errors.append("project must not be empty")
    for key, expected in EXPECTED_DEFAULTS.items():
        if defaults.get(key) != expected:
            errors.append(f"global_defaults.{key} must be {expected}")

    override_fields: set[str] = set()
    for index, override in enumerate(overrides):
        prefix = f"explicit_overrides[{index}]"
        if not isinstance(override, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("field", "value", "source_ref"):
            value = override.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{key} must be a non-empty string")
        field = override.get("field")
        if isinstance(field, str) and field not in EXPECTED_DEFAULTS:
            errors.append(f"{prefix}.field is invalid: {field}")
        elif isinstance(field, str):
            if field in override_fields:
                errors.append(f"{prefix}.field is duplicated: {field}")
            override_fields.add(field)
            value = override.get("value")
            if isinstance(value, str) and value not in ALLOWED_OVERRIDE_VALUES[field]:
                errors.append(f"{prefix}.value is invalid for {field}: {value}")
    if not brief_confirmed:
        errors.append("brief must be confirmed or marked not required before delivery")

    has_user_decision = False
    for index, issue in enumerate(issues):
        prefix = f"issues[{index}]"
        if not isinstance(issue, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = [
            key
            for key in ("id", "category", "summary", "resolution", "decision", "source_ref", "status")
            if key not in issue
        ]
        if missing:
            errors.append(f"{prefix} missing fields: {', '.join(missing)}")
            continue

        category = issue["category"]
        resolution = issue["resolution"]
        status = issue["status"]

        if not isinstance(category, str):
            errors.append(f"{prefix}.category must be str")
        elif category not in ALLOWED_CATEGORIES:
            errors.append(f"{prefix}.category is invalid: {category}")
        if not isinstance(resolution, str):
            errors.append(f"{prefix}.resolution must be str")
        elif resolution not in ALLOWED_RESOLUTIONS:
            errors.append(f"{prefix}.resolution is invalid: {resolution}")
        if not isinstance(status, str):
            errors.append(f"{prefix}.status must be str")
        elif status != "resolved":
            errors.append(f"{prefix}.status must be resolved")
        if isinstance(resolution, str) and resolution == "user":
            has_user_decision = True
            if isinstance(category, str) and category not in USER_DECISION_CATEGORIES:
                errors.append(f"{prefix} asks the user about a non-user decision")
            if not questions_asked:
                errors.append(f"{prefix} records a user decision but questions_asked is false")
        if (
            isinstance(category, str)
            and category in ALLOWED_RESOLUTIONS_BY_CATEGORY
            and isinstance(resolution, str)
            and resolution in ALLOWED_RESOLUTIONS
            and resolution not in ALLOWED_RESOLUTIONS_BY_CATEGORY[category]
        ):
            errors.append(f"{prefix}.resolution {resolution} is not allowed for {category}")

        for key in ("id", "summary", "decision", "source_ref"):
            value = issue[key]
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}.{key} must be a non-empty string")

    if questions_asked and not has_user_decision:
        errors.append("questions_asked is true but no user decision is recorded")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to clarification_gate.json")
    args = parser.parse_args()

    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1

    if not isinstance(payload, dict):
        print("FAIL: top-level JSON value must be an object")
        return 1

    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("PASS: clarification gate is resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
