# create-embedded-project-interview-manuscript（V3 活人解耦版）

将嵌入式项目资料整理成**硬账扎实、学完 OTA 课程的学员能彻底看懂、脱稿讲出来像一线老工程师**的正式中文项目面试手稿。

## 为什么升级到 V3（三段物理拆开）

旧版 130 KB 规则把“算硬账、写人话、审漏洞”全堆进同一个上下文，模型注意力被合规禁令吃光，反而容易写出“本方案 / 冻结 / 设计基线 / 重武装 / 不声称…”等规格书翻译腔和叠甲尾句。

V3 将整套技能压减到 **1 份主流程 + 3 份精简参考（~15 KB）**，并用三段解耦 + Python 硬拦截守住质量：

1. **Stage 1：硬账定案、纯 ImageGen 配图与面经脱敏**（[engineering-spec.md](references/engineering-spec.md)）：先把 6 笔量产硬账算准，用 Codex `image_gen` 生成高清全中文工程图并逐张目视核验，检索团队面经库生成**零内部链接的脱敏原题档案**。
2. **Stage 2：纯净上下文盲写活人口述**（[human-voice.md](references/human-voice.md)）：首选 Gemini 主笔（单 Codex 环境必须新开独立干净会话），彻底隔离内部 JSON 门禁与黑话；文首用老师自然开场（`先说几句这份手稿怎么看`），配齐学前物理大白话 + 2–3 段精简代码/报文 + 核心题 `如果接着追问：`（拒绝 AI 模板速记卡/打卡表），默认打透 **1 则旗舰级深度量产调试案例**（证据对照表 + 4–5 连深追拆解）。
3. **Stage 3：Codex 只读审硬伤 + 自动拦截 + 飞书实测复读**（[review-and-publish.md](references/review-and-publish.md)）：Codex `audit` 只挑物理/寄存器/时序/协议硬伤、禁改中文腔调；`lint_spoken_prose.py` 硬拦截制作标签、内部黑话与叠甲尾句；`validate_real_interview_package.py --archive-file` 硬拦截学员原题档案链接泄漏；飞书写回后强制 `--detail full` 复读验收。

## 安装与调用

```powershell
git clone https://github.com/xingmou123/create-embedded-project-interview-manuscript.git "$env:USERPROFILE\.codex\skills\create-embedded-project-interview-manuscript"
```

```text
使用 $create-embedded-project-interview-manuscript，根据这份简历项目与资料创建正式项目面试手稿。
```

## 目录结构

- `SKILL.md`：V3 三段解耦流水线、完整骨架与 5 条不可妥协红线
- `references/engineering-spec.md`：Stage 1 — 6 笔硬账、纯 ImageGen 配图与面经脱敏红线
- `references/human-voice.md`：Stage 2 — 活人口述原则、OTA 三件套、默认 1 则旗舰深案与 3 组正反例
- `references/review-and-publish.md`：Stage 3 — Codex 只读技术复核、双脚本校验与飞书 `--detail full` 验收
- `scripts/`：5 个校验脚本（`lint_spoken_prose.py`、`validate_real_interview_package.py`、`validate_real_interview_discovery.py`、`validate_clarification_gate.py`、`validate_small_batch_plan.py`）
- `tests/`：单元测试（`pytest -q`）

## License

MIT
