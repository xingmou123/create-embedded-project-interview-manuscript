#!/usr/bin/env python3
"""Validate the real-interview manuscript and lossless archive manifest."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ALLOWED_DISPOSITIONS = {"core_question", "nested_followup", "archive_only"}
ALLOWED_KINDS = {"core_question", "nested_followup"}


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if payload.get("version") != 1:
        errors.append("version must be 1")

    main_document = payload.get("main_document")
    archive_document = payload.get("archive_document")
    records = payload.get("records")
    questions = payload.get("questions")

    if not isinstance(main_document, dict):
        errors.append("main_document must be an object")
        main_document = {}
    if not isinstance(archive_document, dict):
        errors.append("archive_document must be an object")
        archive_document = {}
    if not isinstance(records, list):
        errors.append("records must be an array")
        records = []
    if not isinstance(questions, list):
        errors.append("questions must be an array")
        questions = []

    if main_document.get("archive_entry_count") != 1:
        errors.append("main_document.archive_entry_count must be 1")
    if main_document.get("raw_question_blocks") != 0:
        errors.append("main_document.raw_question_blocks must be 0")
    forbidden = main_document.get("forbidden_labels_found")
    if forbidden != []:
        errors.append("main_document.forbidden_labels_found must be an empty array")

    if archive_document.get("answers_generated") is not False:
        errors.append("archive_document.answers_generated must be false")
    if archive_document.get("preserves_original_order") is not True:
        errors.append("archive_document.preserves_original_order must be true")
    if archive_document.get("deduplicated") is not False:
        errors.append("archive_document.deduplicated must be false")

    record_ids: set[str] = set()
    raw_ids: set[str] = set()
    raw_to_record: dict[str, str] = {}
    raw_to_disposition: dict[str, str] = {}
    raw_to_question: dict[str, str | None] = {}
    source_urls: set[str] = set()

    for record_index, record in enumerate(records):
        prefix = f"records[{record_index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue

        record_id = record.get("id")
        label = record.get("label")
        source_url = record.get("source_url")
        raw_questions = record.get("questions")

        if not is_nonempty_string(record_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if record_id in record_ids:
            errors.append(f"duplicate record id: {record_id}")
        record_ids.add(record_id)

        if not is_nonempty_string(label):
            errors.append(f"{prefix}.label must be a non-empty string")

        if not is_nonempty_string(source_url):
            errors.append(f"{prefix}.source_url must be a non-empty string")
        else:
            source_urls.add(source_url)

        if not isinstance(raw_questions, list):
            errors.append(f"{prefix}.questions must be an array")
            continue
        if not raw_questions:
            errors.append(f"{prefix}.questions must not be empty")

        for raw_index, raw in enumerate(raw_questions):
            raw_prefix = f"{prefix}.questions[{raw_index}]"
            if not isinstance(raw, dict):
                errors.append(f"{raw_prefix} must be an object")
                continue

            raw_id = raw.get("id")
            order = raw.get("order")
            text = raw.get("text")
            disposition = raw.get("disposition")
            question_id = raw.get("question_id")

            if not is_nonempty_string(raw_id):
                errors.append(f"{raw_prefix}.id must be a non-empty string")
                continue
            if raw_id in raw_ids:
                errors.append(f"duplicate raw question id: {raw_id}")
            raw_ids.add(raw_id)
            raw_to_record[raw_id] = record_id

            if order != raw_index + 1:
                errors.append(f"{raw_prefix}.order must preserve 1-based list order")
            if not is_nonempty_string(text):
                errors.append(f"{raw_prefix}.text must be a non-empty string")
            if disposition not in ALLOWED_DISPOSITIONS:
                errors.append(f"{raw_prefix}.disposition is invalid: {disposition}")
                continue

            raw_to_disposition[raw_id] = disposition
            if disposition == "archive_only":
                if question_id not in (None, ""):
                    errors.append(f"{raw_prefix}.question_id must be empty for archive_only")
                raw_to_question[raw_id] = None
            else:
                if not is_nonempty_string(question_id):
                    errors.append(f"{raw_prefix}.question_id is required")
                    raw_to_question[raw_id] = None
                else:
                    raw_to_question[raw_id] = question_id

    question_ids: set[str] = set()
    if raw_ids and not questions:
        errors.append("questions must contain at least one formal question")
    for index, question in enumerate(questions):
        prefix = f"questions[{index}]"
        if not isinstance(question, dict):
            errors.append(f"{prefix} must be an object")
            continue
        question_id = question.get("id")
        if not is_nonempty_string(question_id):
            errors.append(f"{prefix}.id must be a non-empty string")
            continue
        if question_id in question_ids:
            errors.append(f"duplicate formal question id: {question_id}")
        question_ids.add(question_id)

    referenced_raw_ids: list[str] = []
    for index, question in enumerate(questions):
        prefix = f"questions[{index}]"
        if not isinstance(question, dict):
            continue

        question_id = question.get("id")
        kind = question.get("kind")
        parent_id = question.get("parent_id")
        mapped_raw_ids = question.get("raw_ids")

        if not is_nonempty_string(question_id):
            continue
        if not is_nonempty_string(question.get("title")):
            errors.append(f"{prefix}.title must be a non-empty string")
        if not is_nonempty_string(question.get("answer_logic")):
            errors.append(f"{prefix}.answer_logic must be a non-empty string")
        if kind not in ALLOWED_KINDS:
            errors.append(f"{prefix}.kind is invalid: {kind}")
        if kind == "core_question" and parent_id not in (None, ""):
            errors.append(f"{prefix}.parent_id must be empty for core_question")
        if kind == "nested_followup" and parent_id not in question_ids:
            errors.append(f"{prefix}.parent_id must reference an existing question")
        if question.get("answer_blocks") != 1:
            errors.append(f"{prefix}.answer_blocks must be 1")
        if question.get("source_lines") != 1:
            errors.append(f"{prefix}.source_lines must be 1")

        representatives = question.get("representative_sources")
        if not isinstance(representatives, list) or not representatives:
            errors.append(f"{prefix}.representative_sources must be a non-empty array")
        elif any(not is_nonempty_string(item) for item in representatives):
            errors.append(f"{prefix}.representative_sources contains an empty value")

        if not isinstance(mapped_raw_ids, list) or not mapped_raw_ids:
            errors.append(f"{prefix}.raw_ids must be a non-empty array")
            continue
        if len(mapped_raw_ids) != len(set(mapped_raw_ids)):
            errors.append(f"{prefix}.raw_ids contains duplicates")

        valid_raw_ids = [raw_id for raw_id in mapped_raw_ids if raw_id in raw_ids]
        for raw_id in mapped_raw_ids:
            if raw_id not in raw_ids:
                errors.append(f"{prefix}.raw_ids references unknown id: {raw_id}")
                continue
            referenced_raw_ids.append(raw_id)
            if raw_to_question.get(raw_id) != question_id:
                errors.append(f"{prefix} conflicts with {raw_id}.question_id")
            if raw_to_disposition.get(raw_id) != kind:
                errors.append(f"{prefix}.kind conflicts with {raw_id}.disposition")

        occurrence_count = len({raw_to_record[raw_id] for raw_id in valid_raw_ids})
        if question.get("displayed_occurrence_count") != occurrence_count:
            errors.append(
                f"{prefix}.displayed_occurrence_count must be {occurrence_count}"
            )

    reference_counts = Counter(referenced_raw_ids)
    for raw_id, disposition in raw_to_disposition.items():
        count = reference_counts[raw_id]
        if disposition == "archive_only" and count:
            errors.append(f"{raw_id} is archive_only but appears in a formal question")
        if disposition != "archive_only" and count != 1:
            errors.append(f"{raw_id} must appear in exactly one formal question")

    expected_counts = {
        "declared_record_count": len(record_ids),
        "declared_question_count": len(raw_ids),
        "declared_source_count": len(source_urls),
    }
    for field, expected in expected_counts.items():
        if archive_document.get(field) != expected:
            errors.append(f"archive_document.{field} must be {expected}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to real_interview_package.json")
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

    print("PASS: real interview package is internally consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
