from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_clarification_gate import validate as validate_clarification  # noqa: E402
from lint_spoken_prose import lint_text  # noqa: E402
from validate_real_interview_discovery import validate as validate_discovery  # noqa: E402
from validate_real_interview_package import validate as validate_interviews  # noqa: E402
from validate_small_batch_plan import validate as validate_small_batch  # noqa: E402


class ClarificationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "version": 1,
            "project": "demo",
            "global_defaults": {
                "engineering_design": "production_ready_complete",
                "delivery_maturity": "small_batch_design_target",
                "debugging_case_nature": "evidence_driven",
                "provided_quantitative_results": "evidence_driven",
            },
            "explicit_overrides": [],
            "questions_asked": False,
            "brief_confirmed": True,
            "issues": [],
        }

    def test_evidence_driven_defaults_pass(self) -> None:
        self.assertEqual(validate_clarification(self.payload), [])

    def test_production_design_requirement_cannot_be_omitted(self) -> None:
        del self.payload["global_defaults"]["engineering_design"]

        errors = validate_clarification(self.payload)

        self.assertTrue(any("engineering_design" in error for error in errors))

    def test_concept_design_cannot_replace_completed_design(self) -> None:
        self.payload["global_defaults"]["engineering_design"] = "concept_only"

        errors = validate_clarification(self.payload)

        self.assertTrue(any("production_ready_complete" in error for error in errors))

    def test_actual_prototype_stage_does_not_lower_design_requirement(self) -> None:
        self.payload["explicit_overrides"] = [
            {"field": "delivery_maturity", "value": "prototype", "source_ref": "project_record"}
        ]

        self.assertEqual(validate_clarification(self.payload), [])

        del self.payload["global_defaults"]["engineering_design"]
        self.assertTrue(validate_clarification(self.payload))

    def test_design_requirement_cannot_be_overridden(self) -> None:
        self.payload["explicit_overrides"] = [
            {"field": "engineering_design", "value": "concept_only", "source_ref": "old_brief"}
        ]

        errors = validate_clarification(self.payload)

        self.assertTrue(any("field is invalid: engineering_design" in error for error in errors))


class SpokenProseLintTests(unittest.TestCase):
    def test_short_direct_answer_passes(self) -> None:
        content = (
            "我把开锁和交互拆开了。F411 管鉴权、电机和安全传感器；"
            "ESP32-S3 管屏幕、摄像头和网络。理由很直接：界面或 Wi-Fi 卡住，"
            "门仍然要能开。两边只交换命令和状态，最后由 F411 决定是否驱动电机。"
        )

        errors, _warnings = lint_text(content)

        self.assertEqual(errors, [])

    def test_production_label_fails_and_density_requires_review(self) -> None:
        content = (
            "完整回答：这个项目把安全控制和交互联网分成两个执行域，"
            "STM32F411 和 FreeRTOS 负责 FM17550、UART、DMA、SecurityManager、"
            "MotorTask 和 Bootloader，ESP32-S3 负责 Wi-Fi、BLE、LVGL、摄像头和视频，"
            "同时还要处理版本管理、状态同步、日志记录和故障恢复。"
        )

        errors, warnings = lint_text(content)

        self.assertTrue(any("production label" in error for error in errors))
        self.assertTrue(any("too many technical names" in warning for warning in warnings))


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

    def _add_followup(self, parent_id: str) -> str:
        record = self.payload["records"][0]
        order = len(record["questions"]) + 1
        raw_id = f"RAW-{order:03d}"
        question_id = f"Q-IE-{len(self.payload['questions']) + 1:03d}"
        record["questions"].append(
            {
                "id": raw_id,
                "order": order,
                "text": "进一步的真实追问",
                "disposition": "nested_followup",
                "question_id": question_id,
            }
        )
        question = copy.deepcopy(self.payload["questions"][0])
        question.update(
            id=question_id,
            kind="nested_followup",
            parent_id=parent_id,
            raw_ids=[raw_id],
        )
        self.payload["questions"].append(question)
        self.payload["archive_document"]["declared_question_count"] += 1
        return question_id

    def test_followup_cannot_be_its_own_parent(self) -> None:
        question_id = self._add_followup("Q-IE-001")
        self.payload["questions"][-1]["parent_id"] = question_id

        errors = validate_interviews(self.payload)

        self.assertTrue(any("parent cycle" in error for error in errors))

    def test_followup_cycle_is_rejected(self) -> None:
        first = self._add_followup("Q-IE-001")
        second = self._add_followup(first)
        self.payload["questions"][-2]["parent_id"] = second

        errors = validate_interviews(self.payload)

        self.assertTrue(any("parent cycle" in error for error in errors))

    def test_multilevel_followups_pass_in_any_list_order(self) -> None:
        first = self._add_followup("Q-IE-001")
        self._add_followup(first)
        self.payload["questions"].reverse()

        self.assertEqual(validate_interviews(self.payload), [])

    def test_followup_parent_must_be_an_existing_id(self) -> None:
        self._add_followup("Q-IE-001")
        for parent_id in ("missing-question", None, [], {}):
            with self.subTest(parent_id=parent_id):
                self.payload["questions"][-1]["parent_id"] = parent_id
                errors = validate_interviews(self.payload)
                self.assertTrue(any("reference an existing question" in error for error in errors))

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

    def test_archive_desensitization_rejects_leaked_urls_and_headers(self) -> None:
        from validate_real_interview_package import validate_archive_desensitization

        clean = "<h1>原题档案</h1><p>收录范围：2 份真实复盘、10 条原题。</p><p>1. 讲一下 FOC 电流采样。</p>"
        self.assertEqual(validate_archive_desensitization(clean), [])

        leaked = '<p>原始来源：<a href="https://twd6onxsxva.feishu.cn/docx/abc123">某复盘</a></p>'
        errors = validate_archive_desensitization(leaked)
        self.assertTrue(any("leaks 1 URL" in err for err in errors))
        self.assertTrue(any("原始来源" in err for err in errors))


class SmallBatchPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = {
            "version": 1,
            "project": "demo",
            "evidence_status": "design_target",
            "source_ref": "architect_small_batch_baseline",
            "profile": "industrial_terminal",
            "lot_quantity": 30,
            "first_article_quantity": 3,
            "production_test_quantity": 30,
            "burn_in_quantity": 10,
            "burn_in_hours": 72,
            "burn_in_test": {
                "purpose": "检查持续通信及日志轮转时的资源积累和阻塞。",
                "conditions": "24 V供电、25±2°C，100帧/s收发，每帧64字节，日志每24小时轮转。",
                "duration_basis": "覆盖3个完整的24小时轮转周期，共72小时；用途是软件长稳筛查。",
                "sample_basis": "2组5位工装并行运行10台，覆盖首件和后续装配样本；不作寿命外推。",
                "pass_criteria": ["非预期复位为0次", "记录丢失为0条"],
            },
            "first_pass_yield_target_pct": 90,
            "final_acceptance_target_pct": 98,
            "critical_failure_limit": 0,
            "traceability_target_pct": 100,
            "traceability_fields": [
                "序列号",
                "硬件版本",
                "固件版本",
                "产测时间",
            ],
            "release_criteria": ["全检通过", "重大故障为 0", "追溯完整"],
            "lot_hold_conditions": ["同类故障连续出现 2 台", "安全故障"],
            "project_specific_rationale": "按工业终端装配离散性与长稳资源确定。",
            "visible_manuscript": {
                "direct_question_present": True,
                "numbers_present": True,
                "design_targets_labeled": True,
                "unverified_results_claimed": False,
            },
        }

    def test_concrete_plan_passes(self) -> None:
        self.assertEqual(validate_small_batch(self.payload), [])

    def test_duration_has_no_arbitrary_eight_hour_floor(self) -> None:
        for hours in (0.5, 4, 72, 168):
            with self.subTest(hours=hours):
                self.payload["burn_in_hours"] = hours
                self.payload["burn_in_test"]["duration_basis"] = (
                    f"按专项测试方案给定的循环数和负载持续{hours}小时，完整长稳测试另行覆盖。"
                )
                self.assertEqual(validate_small_batch(self.payload), [])

    def test_duration_must_be_finite_and_positive(self) -> None:
        for hours in (0, -1, float("nan"), float("inf"), float("-inf"), True, "72", None):
            with self.subTest(hours=hours):
                self.payload["burn_in_hours"] = hours
                errors = validate_small_batch(self.payload)
                self.assertTrue(any("burn_in_hours must be a finite positive number" in e for e in errors))

    def test_test_rationale_cannot_be_omitted(self) -> None:
        del self.payload["burn_in_test"]
        errors = validate_small_batch(self.payload)
        self.assertTrue(any("burn_in_test must be an object" in e for e in errors))

    def test_test_purpose_conditions_and_basis_are_required(self) -> None:
        for field in ("purpose", "conditions", "duration_basis", "sample_basis"):
            with self.subTest(field=field):
                payload = copy.deepcopy(self.payload)
                payload["burn_in_test"][field] = " "
                errors = validate_small_batch(payload)
                self.assertTrue(any(f"burn_in_test.{field}" in e for e in errors))

    def test_repeated_items_do_not_count_as_different_checks(self) -> None:
        for field in ("traceability_fields", "release_criteria", "lot_hold_conditions"):
            with self.subTest(field=field):
                payload = copy.deepcopy(self.payload)
                payload[field] = [payload[field][0]] * len(payload[field])
                errors = validate_small_batch(payload)
                self.assertTrue(any(f"{field} contains duplicate items" in e for e in errors))

    def test_formatting_does_not_disguise_duplicate_items(self) -> None:
        self.payload["release_criteria"] = ["CRC通过", " ＣＲＣ 通 过。", "追溯完整"]
        errors = validate_small_batch(self.payload)
        self.assertTrue(any("release_criteria contains duplicate items" in e for e in errors))

    def test_burn_in_criteria_must_be_nonempty_and_distinct(self) -> None:
        for criteria in ([], [" "], ["。"], [None], ["非预期复位为0次", "非预期复位为0次。"]):
            with self.subTest(criteria=criteria):
                self.payload["burn_in_test"]["pass_criteria"] = criteria
                errors = validate_small_batch(self.payload)
                self.assertTrue(any("burn_in_test.pass_criteria" in e for e in errors))

    def test_all_units_must_receive_production_test(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["production_test_quantity"] = 20

        errors = validate_small_batch(payload)

        self.assertTrue(any("must equal lot_quantity" in error for error in errors))

    def test_missing_batch_number_fails(self) -> None:
        payload = copy.deepcopy(self.payload)
        del payload["lot_quantity"]

        errors = validate_small_batch(payload)

        self.assertTrue(any("lot_quantity must be an integer" in error for error in errors))

    def test_unverified_results_cannot_be_claimed(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["visible_manuscript"]["unverified_results_claimed"] = True

        errors = validate_small_batch(payload)

        self.assertTrue(any("unverified_results_claimed" in error for error in errors))


class RealInterviewDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source_url = "https://example.com/interview"
        self.payload = {
            "version": 1,
            "project": "demo",
            "search_completed": True,
            "library_roots": [
                {
                    "role": "designated_real_interview_library",
                    "name": "嵌入式大厂面经合集",
                    "url": "https://example.com/library",
                    "status": "read",
                    "snapshot_ref": "revision-12",
                }
            ],
            "queries": [
                {"text": "工业网关", "kind": "product", "result_count": 2},
                {"text": "STM32 FreeRTOS", "kind": "technical", "result_count": 2},
                {"text": "UART DMA", "kind": "technical", "result_count": 1},
                {"text": "OTA HardFault", "kind": "technical", "result_count": 1},
            ],
            "available_candidate_count": 1,
            "candidates": [
                {
                    "label": "某公司一面",
                    "source_url": self.source_url,
                    "status": "read",
                    "scope": "similar_stack",
                    "raw_question_count": 2,
                    "reason": "包含 FreeRTOS 与 DMA 实际追问。",
                }
            ],
            "selected_source_urls": [self.source_url],
            "no_match_reason": None,
        }
        self.package = {
            "records": [
                {
                    "source_url": self.source_url,
                    "questions": [
                        {"id": "RAW-001", "disposition": "core_question"},
                        {"id": "RAW-002", "disposition": "archive_only"},
                    ],
                }
            ]
        }

    def test_completed_library_search_passes(self) -> None:
        self.assertEqual(validate_discovery(self.payload, self.package), [])

    def test_missing_archive_only_question_is_detected(self) -> None:
        self.package["records"][0]["questions"].pop()

        errors = validate_discovery(self.payload, self.package)

        self.assertTrue(any("contains 1 raw questions" in error for error in errors))

    def test_one_source_can_contain_multiple_records(self) -> None:
        second_question = self.package["records"][0]["questions"].pop()
        self.package["records"].append(
            {"source_url": self.source_url, "questions": [second_question]}
        )

        self.assertEqual(validate_discovery(self.payload, self.package), [])

    def test_equal_total_does_not_hide_per_source_mismatch(self) -> None:
        other_url = "https://example.com/second-interview"
        candidate = copy.deepcopy(self.payload["candidates"][0])
        candidate.update(source_url=other_url, raw_question_count=1)
        self.payload["candidates"].append(candidate)
        self.payload["selected_source_urls"].append(other_url)
        self.payload["available_candidate_count"] = 2
        removed = self.package["records"][0]["questions"].pop()
        self.package["records"].append(
            {"source_url": other_url, "questions": [removed, {"id": "RAW-003"}]}
        )

        errors = validate_discovery(self.payload, self.package)

        self.assertEqual(sum("raw_question_count" in error for error in errors), 2)

    def test_package_record_must_expose_raw_questions(self) -> None:
        del self.package["records"][0]["questions"]

        errors = validate_discovery(self.payload, self.package)

        self.assertTrue(any("questions must be an array" in error for error in errors))

    def test_library_root_must_be_read(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["library_roots"][0]["status"] = "not_opened"

        errors = validate_discovery(payload)

        self.assertTrue(any("status must be read" in error for error in errors))

    def test_available_candidates_cannot_be_skipped(self) -> None:
        payload = copy.deepcopy(self.payload)
        payload["available_candidate_count"] = 5
        payload["candidates"] = []
        payload["selected_source_urls"] = []
        payload["no_match_reason"] = "未发现匹配来源"

        errors = validate_discovery(payload)

        self.assertTrue(any("at least 5 inspected records" in error for error in errors))

    def test_package_sources_must_match_discovery(self) -> None:
        package = {"records": [{"source_url": "https://example.com/other"}]}

        errors = validate_discovery(self.payload, package)

        self.assertTrue(any("must exactly match" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
