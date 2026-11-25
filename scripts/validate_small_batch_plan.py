#!/usr/bin/env python3
"""Validate a concrete small-batch production plan for a manuscript."""

from __future__ import annotations

import argparse
import json
import math
import unicodedata
from pathlib import Path
from typing import Any


ALLOWED_EVIDENCE_STATUS = {"design_target", "confirmed_result"}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_number(value: Any) -> bool:
    return (
        isinstance(value, int) and not isinstance(value, bool)
        or isinstance(value, float) and math.isfinite(value)
    )


def validate_distinct_strings(value: Any, field: str, minimum: int) -> list[str]:
    if not isinstance(value, list):
        return [f"{field} must contain at least {minimum} distinct items"]
    errors: list[str] = []
    normalized: list[str] = []
    for item in value:
        if not is_nonempty_string(item):
            errors.append(f"{field} contains an empty or non-string value")
            continue
        key = "".join(unicodedata.normalize("NFKC", item).casefold().split())
        key = key.rstrip("。.;:；：")
        if not key:
            errors.append(f"{field} contains an empty value after normalization")
            continue
        normalized.append(key)
    if len(set(normalized)) != len(normalized):
        errors.append(f"{field} contains duplicate items")
    if len(set(normalized)) < minimum:
        errors.append(f"{field} must contain at least {minimum} distinct items")
    return errors


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("version") != 1:
        errors.append("version must be 1")
    if not is_nonempty_string(payload.get("project")):
        errors.append("project must be a non-empty string")
    if payload.get("evidence_status") not in ALLOWED_EVIDENCE_STATUS:
        errors.append("evidence_status must be design_target or confirmed_result")
    if not is_nonempty_string(payload.get("source_ref")):
        errors.append("source_ref must be a non-empty string")
    if not is_nonempty_string(payload.get("profile")):
        errors.append("profile must be a non-empty string")

    integer_fields = (
        "lot_quantity",
        "first_article_quantity",
        "production_test_quantity",
        "burn_in_quantity",
        "critical_failure_limit",
    )
    for field in integer_fields:
        value = payload.get(field)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{field} must be an integer")

    lot_quantity = payload.get("lot_quantity")
    first_article_quantity = payload.get("first_article_quantity")
    production_test_quantity = payload.get("production_test_quantity")
    burn_in_quantity = payload.get("burn_in_quantity")
    burn_in_hours = payload.get("burn_in_hours")

    if isinstance(lot_quantity, int) and not isinstance(lot_quantity, bool):
        if not 1 <= lot_quantity <= 10000:
            errors.append("lot_quantity must be between 1 and 10000")
        if production_test_quantity != lot_quantity:
            errors.append("production_test_quantity must equal lot_quantity")
        for field, value in (
            ("first_article_quantity", first_article_quantity),
            ("burn_in_quantity", burn_in_quantity),
        ):
            if isinstance(value, int) and not isinstance(value, bool):
                if not 1 <= value <= lot_quantity:
                    errors.append(f"{field} must be between 1 and lot_quantity")

    if not is_number(burn_in_hours) or burn_in_hours <= 0:
        errors.append("burn_in_hours must be a finite positive number")

    burn_in_test = payload.get("burn_in_test")
    if not isinstance(burn_in_test, dict):
        errors.append("burn_in_test must be an object with project-specific test rationale")
        burn_in_test = {}
    for field in ("purpose", "conditions", "duration_basis", "sample_basis"):
        if not is_nonempty_string(burn_in_test.get(field)):
            errors.append(f"burn_in_test.{field} must be a non-empty string")
    errors.extend(validate_distinct_strings(
        burn_in_test.get("pass_criteria"), "burn_in_test.pass_criteria", 1
    ))

    first_pass = payload.get("first_pass_yield_target_pct")
    final_acceptance = payload.get("final_acceptance_target_pct")
    traceability = payload.get("traceability_target_pct")
    for field, value in (
        ("first_pass_yield_target_pct", first_pass),
        ("final_acceptance_target_pct", final_acceptance),
        ("traceability_target_pct", traceability),
    ):
        if not is_number(value):
            errors.append(f"{field} must be a finite number")
        elif not 0 <= value <= 100:
            errors.append(f"{field} must be between 0 and 100")

    if is_number(first_pass) and is_number(final_acceptance):
        if final_acceptance < first_pass:
            errors.append(
                "final_acceptance_target_pct must not be lower than "
                "first_pass_yield_target_pct"
            )
    if payload.get("critical_failure_limit") != 0:
        errors.append("critical_failure_limit must be 0")
    if traceability != 100:
        errors.append("traceability_target_pct must be 100")

    list_requirements = {
        "traceability_fields": 4,
        "release_criteria": 3,
        "lot_hold_conditions": 2,
    }
    for field, minimum in list_requirements.items():
        errors.extend(validate_distinct_strings(payload.get(field), field, minimum))

    if not is_nonempty_string(payload.get("project_specific_rationale")):
        errors.append("project_specific_rationale must be a non-empty string")

    visible = payload.get("visible_manuscript")
    if not isinstance(visible, dict):
        errors.append("visible_manuscript must be an object")
        visible = {}
    for field in (
        "direct_question_present",
        "numbers_present",
        "design_targets_labeled",
    ):
        if visible.get(field) is not True:
            errors.append(f"visible_manuscript.{field} must be true")
    if visible.get("unverified_results_claimed") is not False:
        errors.append(
            "visible_manuscript.unverified_results_claimed must be false"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to small_batch_plan.json")
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

    print("PASS: small-batch manifest is internally consistent; review test rationale against project requirements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
