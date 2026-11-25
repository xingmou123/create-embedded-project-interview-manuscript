#!/usr/bin/env python3
"""Check spoken answer prose: production labels, internal jargon leaks, and
defensive disclaimers are hard errors; density smells are warnings for human review.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from collections import Counter
from pathlib import Path


FORBIDDEN_LABELS = (
    "完整回答",
    "可直接口述回答",
    "标准答案",
    "面试官意图",
    "核心亮点",
    "高分话术",
    "记忆口诀",
    "自测题",
)
# Internal Skill/Codex jargon and defensive disclaimer patterns forbidden in learner prose
FORBIDDEN_LEAKS = (
    "本方案",
    "冻结数值",
    "冻结的",
    "锁定设计",
    "设计基线",
    "推演语态",
    "验收门槛语态",
    "检索并复读",
    "重武装",
    "单一口径",
    "不声称",
    "不宣称",
    "不能据此证明",
    "写成已经通过",
    "说成已经",
    "不拿计划目标冒充",
)
GENERIC_STARTS = (
    "这个项目",
    "针对这个问题",
    "首先",
    "我会先",
    "如果出现",
    "在这个项目中",
)
SEQUENCE_WORDS = ("先", "再", "然后", "同时", "最后", "接下来")
AI_SMELL_PATTERNS = (
    ("em-dash", re.compile(r"——")),
    ("第一/第二/第三", re.compile(r"第一[，,、：:].*第二[，,、：:].*第三")),
    ("彻底封死", re.compile(r"彻底封死|彻底杜绝|完美解决|全面赋能")),
)
LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_.+/-]*")
TAG = re.compile(r"<[^>]+>")
PARAGRAPH = re.compile(r"(?is)<p\b[^>]*>(.*?)</p>")
SENTENCE = re.compile(r"[^。！？!?]+[。！？!?]?")


def visible_length(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def extract_paragraphs(content: str) -> list[str]:
    matches = PARAGRAPH.findall(content)
    raw_paragraphs = matches if matches else re.split(r"\n\s*\n|\r?\n", content)
    paragraphs: list[str] = []
    for raw in raw_paragraphs:
        text = html.unescape(TAG.sub("", raw))
        text = re.sub(r"\s+", " ", text).strip().lstrip("\ufeff").strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def find_production_label(paragraph: str) -> str | None:
    candidate = re.sub(r"^(?:#{1,6}\s+|[-+*]\s+|\d+[.)、]\s+)", "", paragraph)
    candidate = re.sub(r"[*_`]", "", candidate).strip()
    for label in FORBIDDEN_LABELS:
        if candidate.startswith((f"【{label}】", f"[{label}]")):
            return label
        if candidate.startswith(label):
            remainder = candidate[len(label):].lstrip()
            if not remainder or remainder.startswith(("：", ":")):
                return label
    return None


def lint_text(content: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    paragraphs = extract_paragraphs(content)
    if not paragraphs:
        return ["no spoken answer text was found in the input"], warnings
    start_counts: Counter[str] = Counter()

    for index, paragraph in enumerate(paragraphs, start=1):
        prefix = f"P{index}"
        label = find_production_label(paragraph)
        if label is not None:
            errors.append(f"{prefix}: contains production label {label!r}")

        for leak in FORBIDDEN_LEAKS:
            if leak in paragraph:
                errors.append(f"{prefix}: contains internal/defensive leak {leak!r}")

        for smell_name, pattern in AI_SMELL_PATTERNS:
            if pattern.search(paragraph):
                warnings.append(f"{prefix}: AI prose smell ({smell_name})")

        paragraph_length = visible_length(paragraph)
        if paragraph_length > 260:
            warnings.append(f"{prefix}: paragraph may be too dense ({paragraph_length} chars)")
        elif paragraph_length > 220:
            warnings.append(f"{prefix}: paragraph is long ({paragraph_length} chars)")

        semicolons = paragraph.count("；") + paragraph.count(";")
        if semicolons >= 2:
            warnings.append(f"{prefix}: uses {semicolons} semicolons; review checklist density")

        sequence_text = paragraph.replace("优先", "").replace("首先", "")
        sequence_count = paragraph.count("首先") + sum(
            sequence_text.count(word) for word in SEQUENCE_WORDS
        )
        if sequence_count >= 5:
            warnings.append(f"{prefix}: uses {sequence_count} sequencing words in one paragraph")
        elif sequence_count == 4:
            warnings.append(f"{prefix}: sequencing is dense ({sequence_count} markers)")

        latin_tokens = set(LATIN_TOKEN.findall(paragraph))
        if len(latin_tokens) > 8:
            warnings.append(f"{prefix}: introduces too many technical names ({len(latin_tokens)})")
        elif len(latin_tokens) > 6:
            warnings.append(f"{prefix}: technical-name density is high ({len(latin_tokens)})")

        for sentence_index, sentence in enumerate(SENTENCE.findall(paragraph), start=1):
            length = visible_length(sentence)
            if length > 80:
                warnings.append(f"{prefix}/S{sentence_index}: sentence is too long ({length} chars)")
            elif length > 68:
                warnings.append(f"{prefix}/S{sentence_index}: sentence is long ({length} chars)")

        for start in GENERIC_STARTS:
            if paragraph.startswith(start):
                start_counts[start] += 1

        contrast_count = sum(
            paragraph.count(pattern) for pattern in ("不仅", "而且", "既", "也", "不是", "而是")
        )
        if contrast_count >= 6:
            warnings.append(f"{prefix}: contrast scaffolding is overused")

    for start, count in start_counts.items():
        if count >= 3:
            warnings.append(f"document: {count} paragraphs start with {start!r}")

    return errors, warnings


def read_input(path_text: str) -> str:
    if path_text == "-":
        return sys.stdin.read()
    return Path(path_text).read_text(encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="UTF-8 XML/text path, or - for stdin")
    args = parser.parse_args()

    errors, warnings = lint_text(read_input(args.input))
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARN: {item}")

    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: no hard prose issues; {len(warnings)} warning(s) require review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
