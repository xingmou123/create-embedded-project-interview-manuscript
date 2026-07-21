from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_clarification_gate import validate as validate_clarification  # noqa: E402
from validate_real_interview_package import validate as validate_interviews  # noqa: E402


class ClarificationGateTests(unittest.TestCase):
    def test_evidence_driven_defaults_pass(self) -> None:
        payload = {
            "version": 1,
            "project": "demo",
            "global_defaults": {
                "delivery_maturity": "small_batch_design_target",
                "debugging_case_nature": "evidence_driven",
                "provided_quantitative_results": "evidence_driven",
            },
            "explicit_overrides": [],
            "questions_asked": False,
            "brief_confirmed": True,
            "issues": [],
        }

        self.assertEqual(validate_clarification(payload), [])


class RealInterviewPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "version": 1,
            "main_document": {
                "archive_entry_count": 1,
                "raw_question_blocks": 0,
                "forbidden_labels_found": [],
            },
            "archive_document": {
                "declared_record_count": 1,
                "declared_question_count": 2,
                "declared_source_count": 1,
                "answers_generated": False,
                "preserves_original_order": True,
                "deduplicated": False,
            },
            "records": [
                {
                    "id": "REC-001",
                    "label": "某公司一面",
                    "source_url": "https://example.com/source",
                    "questions": [
                        {
                            "id": "RAW-001",
                            "order": 1,
                            "text": "问题一",
                            "disposition": "core_question",
                            "question_id": "Q-IE-001",
                        },
                        {
                            "id": "RAW-002",
                            "order": 2,
                            "text": "问题二",
                            "disposition": "archive_only",
                            "question_id": None,
                        },
                    ],
                }
            ],
            "questions": [
                {
                    "id": "Q-IE-001",
                    "title": "正式问题",
                    "kind": "core_question",
                    "parent_id": None,
                    "raw_ids": ["RAW-001"],
                    "displayed_occurrence_count": 1,
                    "representative_sources": ["某公司一面"],
                    "answer_logic": "一套完整回答逻辑",
                    "answer_blocks": 1,
                    "source_lines": 1,
                }
            ],
        }

    def test_consistent_package_passes(self) -> None:
        self.assertEqual(validate_interviews(self.payload), [])

    def test_displayed_count_is_recomputed(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["questions"][0]["displayed_occurrence_count"] = 2

        errors = validate_interviews(payload)

        self.assertTrue(any("displayed_occurrence_count must be 1" in error for error in errors))

    def test_archive_only_question_cannot_enter_main(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["questions"][0]["raw_ids"].append("RAW-002")

        errors = validate_interviews(payload)

        self.assertTrue(any("archive_only" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
