#!/usr/bin/env python3
"""Validate that the designated real-interview library was actually searched."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_QUERY_KINDS = {"product", "technical"}
ALLOWED_SCOPES = {"direct", "same_product", "similar_stack", "excluded"}
SELECTED_SCOPES = ALLOWED_SCOPES - {"excluded"}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(
    payload: dict[str, Any], package: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []

    if payload.get("version") != 1:
        errors.append("version must be 1")
    if not is_nonempty_string(payload.get("project")):
        errors.append("project must be a non-empty string")
    if payload.get("search_completed") is not True:
        errors.append("search_completed must be true")

    roots = payload.get("library_roots")
    if not isinstance(roots, list) or not roots:
        errors.append("library_roots must be a non-empty array")
        roots = []
    for index, root in enumerate(roots):
        prefix = f"library_roots[{index}]"
        if not isinstance(root, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if root.get("role") != "designated_real_interview_library":
            errors.append(
                f"{prefix}.role must be designated_real_interview_library"
            )
        if not is_nonempty_string(root.get("name")):
            errors.append(f"{prefix}.name must be a non-empty string")
        if not is_nonempty_string(root.get("url")):
            errors.append(f"{prefix}.url must be a non-empty string")
        if root.get("status") != "read":
            errors.append(f"{prefix}.status must be read")
        if not is_nonempty_string(root.get("snapshot_ref")):
            errors.append(f"{prefix}.snapshot_ref must be a non-empty string")

    queries = payload.get("queries")
    if not isinstance(queries, list) or len(queries) < 4:
        errors.append("queries must contain at least 4 entries")
        queries = []

    query_texts: set[str] = set()
    query_kinds: set[str] = set()
    for index, query in enumerate(queries):
        prefix = f"queries[{index}]"
        if not isinstance(query, dict):
            errors.append(f"{prefix} must be an object")
            continue
        text = query.get("text")
        kind = query.get("kind")
        result_count = query.get("result_count")
        if not is_nonempty_string(text):
            errors.append(f"{prefix}.text must be a non-empty string")
        elif text in query_texts:
            errors.append(f"duplicate query text: {text}")
        else:
            query_texts.add(text)
        if kind not in ALLOWED_QUERY_KINDS:
            errors.append(f"{prefix}.kind is invalid: {kind}")
        else:
            query_kinds.add(kind)
        if not isinstance(result_count, int) or isinstance(result_count, bool):
            errors.append(f"{prefix}.result_count must be an integer")
        elif result_count < 0:
            errors.append(f"{prefix}.result_count must not be negative")

    if "product" not in query_kinds:
        errors.append("queries must include at least one product query")
    if sum(1 for query in queries if isinstance(query, dict) and query.get("kind") == "technical") < 2:
        errors.append("queries must include at least two technical queries")

    available = payload.get("available_candidate_count")
    if not isinstance(available, int) or isinstance(available, bool) or available < 0:
        errors.append("available_candidate_count must be a non-negative integer")
        available = 0

    candidates = payload.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates must be an array")
        candidates = []
    required_inspections = min(5, available)
    if len(candidates) < required_inspections:
        errors.append(
            f"candidates must contain at least {required_inspections} inspected records"
        )

    candidate_urls: set[str] = set()
    selected_urls_from_candidates: set[str] = set()
    for index, candidate in enumerate(candidates):
        prefix = f"candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{prefix} must be an object")
            continue
        label = candidate.get("label")
        source_url = candidate.get("source_url")
        scope = candidate.get("scope")
        raw_question_count = candidate.get("raw_question_count")
        if not is_nonempty_string(label):
            errors.append(f"{prefix}.label must be a non-empty string")
        if not is_nonempty_string(source_url):
            errors.append(f"{prefix}.source_url must be a non-empty string")
        elif source_url in candidate_urls:
            errors.append(f"duplicate candidate source_url: {source_url}")
        else:
            candidate_urls.add(source_url)
        if candidate.get("status") != "read":
            errors.append(f"{prefix}.status must be read")
        if scope not in ALLOWED_SCOPES:
            errors.append(f"{prefix}.scope is invalid: {scope}")
        elif scope in SELECTED_SCOPES and is_nonempty_string(source_url):
            selected_urls_from_candidates.add(source_url)
        if not isinstance(raw_question_count, int) or isinstance(
            raw_question_count, bool
        ):
            errors.append(f"{prefix}.raw_question_count must be an integer")
        elif raw_question_count < 0:
            errors.append(f"{prefix}.raw_question_count must not be negative")
        elif scope in SELECTED_SCOPES and raw_question_count == 0:
            errors.append(
                f"{prefix}.raw_question_count must be positive for selected scope"
            )
        if not is_nonempty_string(candidate.get("reason")):
            errors.append(f"{prefix}.reason must be a non-empty string")

    selected = payload.get("selected_source_urls")
    if not isinstance(selected, list):
        errors.append("selected_source_urls must be an array")
        selected = []
    selected_urls = {url for url in selected if is_nonempty_string(url)}
    if len(selected_urls) != len(selected):
        errors.append("selected_source_urls contains empty or duplicate values")
    if selected_urls != selected_urls_from_candidates:
        errors.append(
            "selected_source_urls must exactly match non-excluded candidate sources"
        )

    no_match_reason = payload.get("no_match_reason")
    if selected_urls and no_match_reason not in (None, ""):
        errors.append("no_match_reason must be empty when sources were selected")
    if not selected_urls and not is_nonempty_string(no_match_reason):
        errors.append("no_match_reason is required when no source was selected")

    if package is not None:
        records = package.get("records")
        if not isinstance(records, list):
            errors.append("package.records must be an array")
            records = []
        package_urls = {
            record.get("source_url")
            for record in records
            if isinstance(record, dict) and is_nonempty_string(record.get("source_url"))
        }
        if package_urls != selected_urls:
            errors.append(
                "package record source URLs must exactly match selected_source_urls"
            )

        package_question_counts: Counter[str] = Counter()
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            source_url = record.get("source_url")
            if not is_nonempty_string(source_url):
                continue
            raw_questions = record.get("questions")
            if not isinstance(raw_questions, list):
                errors.append(f"package.records[{index}].questions must be an array")
                continue
            # One source document may contain several distinct interview records.
            package_question_counts[source_url] += len(raw_questions)

        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                continue
            source_url = candidate.get("source_url")
            if not is_nonempty_string(source_url) or source_url not in selected_urls:
                continue
            count = candidate.get("raw_question_count")
            if isinstance(count, int) and not isinstance(count, bool):
                actual = package_question_counts[source_url]
                if count != actual:
                    errors.append(
                        f"candidates[{index}].raw_question_count is {count}, "
                        f"but package contains {actual} raw questions for {source_url}"
                    )

    return errors


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value must be an object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest", type=Path, help="path to real_interview_discovery.json"
    )
    parser.add_argument(
        "--package", type=Path, help="optional real_interview_package.json"
    )
    args = parser.parse_args()

    try:
        payload = load_json(args.manifest)
        package = load_json(args.package) if args.package else None
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

    errors = validate(payload, package)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print("PASS: real-interview discovery manifest is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
