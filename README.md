# create-embedded-project-interview-manuscript

把嵌入式项目资料整理成一份学员看得懂、能直接讲给面试官听的中文项目面试手稿。

它可以读取简历项目、飞书文档、DOCX、软硬件设计方案、代码、原理图、日志和测试记录，统一项目口径后生成项目介绍、技术问答、学员备注、设计取舍以及三个深度调试案例。

## 核心内容

1. **完整 QA**：从 30 秒、90 秒项目介绍一路覆盖到简历职责、重要术语和设计取舍。每条简历职责都有直接问题，回答按口语习惯编写，可以直接用于面试表达。
2. **清晰好学**：先讲架构、执行域和数据流，再进入局部原理。口述回答保持简洁，只有真正难懂或容易混淆的地方才增加学员备注。
3. **三个调试案例**：每个项目先建立 6～10 个候选故障，再选出三个最能体现调试能力的案例。每个案例都要讲清现象、排查证据、根因、修改和验证，不能只换芯片名套模板。

## 和软硬件设计方案一起使用

建议先用 [create-hw-sw-design-docs](https://github.com/xingmou123/create-hw-sw-design-docs) 整理正式的软件、硬件设计方案，再使用本 Skill 生成项目面试手稿。

前者负责把系统设计完整，后者负责把设计讲清楚、问透，并转换成学员可以学习和口述的内容。两项 Skill 配合使用，可以得到一套口径一致的设计文档和项目手稿。

## 安装

把本仓库复制或克隆到 Codex skills 目录：

```powershell
git clone https://github.com/xingmou123/create-embedded-project-interview-manuscript.git "$env:USERPROFILE\.codex\skills\create-embedded-project-interview-manuscript"
```

如果该目录已经存在，先备份或改用其他目录，不要直接覆盖本地修改。

## 使用

在 Codex 中调用：

```text
$create-embedded-project-interview-manuscript
```

然后提供项目资料和目标。例如：

```text
使用 $create-embedded-project-interview-manuscript，根据这份简历项目和软硬件设计文档，生成一份学员可直接学习和口述的项目面试手稿。
```

也可以直接给出 Skill 文件路径：

```text
[$create-embedded-project-interview-manuscript](path/to/SKILL.md) 根据这些项目资料生成面试手稿。
```

## 默认手稿结构

1. 项目定位和一句话技术路线
2. 30 秒与 90 秒口述版
3. 架构、执行域、数据流和职责边界
4. 沿项目主线展开的技术问答
5. 三个深度实战调试案例
6. 反向追问与设计取舍

问题数量不固定。Skill 会根据项目实际内容决定是否包含 BLE、Bootloader、控制算法、低功耗、工业通信等章节，不会为了套模板强行添加模块。

## 文件说明

- `SKILL.md`：主工作流和交付门槛
- `references/project-ledger.md`：项目事实、工程参数和冲突口径
- `references/interview-coverage-matrix.md`：简历职责、术语与取舍覆盖检查
- `references/debugging-cases.md`：三个调试案例的选题和验收规范
- `references/manuscript-style-and-delivery.md`：口述风格、排版、飞书与 DOCX 交付规则

## License

MIT
