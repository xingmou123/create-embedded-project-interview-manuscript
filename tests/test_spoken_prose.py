from __future__ import annotations

import sys
import subprocess
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lint_spoken_prose import lint_text  # noqa: E402


class SpokenProseBoundaryTests(unittest.TestCase):
    def test_short_production_label_is_not_silently_skipped(self) -> None:
        for content in ("完整回答：", "<p><b>可直接口述回答</b></p>"):
            with self.subTest(content=content):
                errors, _ = lint_text(content)
                self.assertTrue(any("production label" in item for item in errors))

    def test_label_headers_are_rejected_across_supported_formats(self) -> None:
        for content in (
            "标准答案：先检查电源。",
            "完整回答: 先检查电源。",
            "**标准答案**：先检查电源。",
            "- **核心亮点：**故障恢复。",
            "### 高分话术",
            "1. 【面试官意图】定位问题。",
            "[记忆口诀]先检查电源。",
            '<p><b>标准答案：</b><span>先检查电源。</span></p>',
        ):
            with self.subTest(content=content):
                errors, _ = lint_text(content)
                self.assertTrue(any("production label" in item for item in errors))

    def test_ordinary_mentions_are_not_mistaken_for_labels(self) -> None:
        for content in (
            "这类故障没有唯一的标准答案，需要根据供电波形和复位原因定位。",
            "标准答案不是固定的一种，需要结合实际负载分析。",
            "这里完整回答了数据怎样交接，没有省略异常处理。",
            "面试官意图需要结合问题理解。",
            "所谓“高分话术”不能代替设计依据。",
            "文档中不再设置‘核心亮点’标签。",
        ):
            with self.subTest(content=content):
                errors, _ = lint_text(content)
                self.assertEqual(errors, [])

    def test_empty_or_textless_input_fails(self) -> None:
        for content in (
            "", " \t\r\n", "\ufeff", "<p></p>",
            "<p><span>&nbsp; </span></p>",
            '<fragment><p><img src="diagram.png" /></p></fragment>',
        ):
            with self.subTest(content=content):
                errors, _ = lint_text(content)
                self.assertTrue(any("no spoken answer text" in item for item in errors))

    def test_brief_answer_is_not_rejected_as_empty(self) -> None:
        errors, _ = lint_text("不能。")
        self.assertEqual(errors, [])

    def test_cli_exit_status_matches_the_reported_result(self) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts/lint_spoken_prose.py"
        cases = (
            ("", 1, "no spoken answer text"),
            ("这类故障没有唯一的标准答案，需要检查供电。", 0, "PASS:"),
            ("标准答案：先检查供电。", 1, "production label"),
        )
        for content, expected_code, message in cases:
            with self.subTest(content=content):
                result = subprocess.run(
                    [sys.executable, "-X", "utf8", str(script), "-"],
                    input=content, capture_output=True, text=True, encoding="utf-8",
                    check=False,
                )
                self.assertEqual(result.returncode, expected_code, result.stderr)
                self.assertIn(message, result.stdout)
                if expected_code:
                    self.assertNotIn("PASS:", result.stdout)

    def test_dense_narrative_requires_review_not_automatic_rejection(self) -> None:
        content = (
            "写入顺序要反过来：先写完整页，再读回检查；"
            "随后写入提交标记，最后更新元数据；"
            "恢复时先检查记录，再决定加载哪个版本。"
        )
        errors, warnings = lint_text(content)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)

    def test_required_identifiers_remain_a_review_hint(self) -> None:
        errors, warnings = lint_text(
            "复核这份故障现场需要区分 PC、LR、MSP、PSP、CFSR、HFSR、"
            "MMFAR、BFAR 和 EXC_RETURN 各自的含义。"
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("technical names" in item for item in warnings))

    def test_repeated_conditional_voice_is_not_a_truthfulness_error(self) -> None:
        errors, warnings = lint_text(
            "<p>如果出现数据中断，我会先看接收计数。</p>"
            "<p>如果出现采样延迟，我会检查数据年龄。</p>"
            "<p>如果出现掉电重启，我会检查有效记录。</p>"
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("paragraphs start" in item for item in warnings))

    def test_plain_technical_words_are_not_forbidden_labels(self) -> None:
        errors, _ = lint_text("验收标准包含数据完整性和故障恢复。若边界条件改变，需要重新验证。")
        self.assertEqual(errors, [])

    def test_ai_prose_smells_are_flagged_as_warnings(self) -> None:
        errors, warnings = lint_text(
            "这套设计——其实靠三步落地：第一，把电流限幅；第二，停止积分；第三，彻底封死所有反弹。"
        )
        self.assertEqual(errors, [])
        self.assertTrue(any("em-dash" in item for item in warnings))
        self.assertTrue(any("第一/第二/第三" in item for item in warnings))
        self.assertTrue(any("彻底封死" in item for item in warnings))

    def test_internal_jargon_and_defensive_leaks_are_hard_errors(self) -> None:
        for content in (
            "本方案采用双缓冲切槽。",
            "上述参数属于冻结的设计基线。",
            "导走后重武装缓存，因此不声称提供加密。",
            "未实测环节保持推演语态，不拿计划目标冒充成绩。",
        ):
            with self.subTest(content=content):
                errors, _ = lint_text(content)
                self.assertTrue(any("internal/defensive leak" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
