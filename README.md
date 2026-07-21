# create-embedded-project-interview-manuscript

把嵌入式项目资料整理成正式、完整、适合学员学习和面试表达的中文项目手稿。

Skill 可以读取简历项目、飞书文档、DOCX、软硬件设计说明书、代码、原理图、日志、测试记录和真实面经。它会先完成最小澄清门并统一项目事实，再生成产品展示、设计资料预览、从需求到交付流程、完整口述问答、设计取舍以及三个深度调试案例；有真实面经时，主稿提供一题一答的考前突击章节，全部原题与来源另行无损归档。

## 成稿特点

1. **最小澄清门**：能查证的内容自行查证，技术参数和路线由架构师裁决；只有职责、产品形态或项目边界仍无法确定时，才一次询问一个问题。
2. **先看到产品**：设备、可穿戴、机器人、仪器和终端项目打开后第一屏就是产品形态。没有实物素材时，使用 ImageGen 生成克制、物理可行的写实产品展示图，不用文本路线图代替。
3. **先看到设计资料**：项目背景之后直接提供软件、硬件详细设计说明书的 PDF 预览和同版本 Word 下载，不把附件堆到文末。
4. **正式紫色回答**：30/90 秒介绍、技术问答和调试案例的完整回答统一使用紫色文本，不显示“可直接口述回答”“标准答案”等培训标签。
5. **纯 ImageGen 工程配图**：架构、任务、协议、状态、资源和调试机制按需生成工程图；禁止 ASCII、代码块、Mermaid、SVG 或本地重绘冒充最终配图。
6. **三个深度调试案例**：每份完整手稿恰好保留三个高质量案例，逐个按证据区分真实复盘、故障注入或设计推演，完整讲清现象、排查证据、根因、修改和验证。
7. **真实面经分层交付**：主稿将同一回答逻辑合并成一道正式问题，每题只给一份完整口述回答；全部真实面试记录、原题、顺序和来源保存在独立原题档案。
8. **封版后归档**：学员手稿确认完成后，更新简历项目库中对应项目描述旁的唯一手稿入口；旧稿链接直接替换，不创建重复项目或多个“最终版”。

## 和软硬件设计方案一起使用

建议先用 [create-hw-sw-design-docs](https://github.com/xingmou123/create-hw-sw-design-docs) 生成或校准正式的软件、硬件详细设计说明书，再调用本 Skill 生成项目手稿。

前者负责定义系统和工程基线，后者负责把产品形态、设计方案、职责、数据流、问答与调试案例整理成学员可直接使用的手稿。两者必须使用同一套芯片、接口、协议、参数、交付阶段和职责口径。

## 安装

```powershell
git clone https://github.com/xingmou123/create-embedded-project-interview-manuscript.git "$env:USERPROFILE\.codex\skills\create-embedded-project-interview-manuscript"
```

## 使用

在 Codex 中调用：

```text
$create-embedded-project-interview-manuscript
```

示例：

```text
使用 $create-embedded-project-interview-manuscript，根据这份简历项目、软硬件设计文档和飞书资料，创建正式项目面试手稿。
```

## 默认阅读顺序

1. 产品形态与项目背景
2. 软件、硬件详细设计资料（PDF 预览 + Word 下载）
3. 学习准备
4. 30 秒与 90 秒项目介绍
5. 从需求到交付的标准开发流程
6. 系统架构与职责边界
7. 分层技术问答
8. 三个深度调试案例
9. 设计取舍与项目收束
10. 真实面试问题与完整回答，以及独立原题档案入口

问题数量不固定。Skill 会按照项目的真实技术主线决定是否包含 BLE、Bootloader、控制算法、低功耗、工业通信或其他专题，不为了套模板强行添加模块。

## 文件说明

- `SKILL.md`：主工作流和交付门槛
- `references/clarification-gate.md`：最小澄清门、全局证据策略和单问单答规则
- `references/project-ledger.md`：项目事实、工程参数和冲突口径
- `references/interview-coverage-matrix.md`：简历职责、术语与取舍覆盖检查
- `references/debugging-cases.md`：三个调试案例的生成和验收规范
- `references/real-interview-evidence.md`：真实面经取证、问题归并、完整回答与无损原题档案
- `references/manuscript-style-and-delivery.md`：文档顺序、紫色回答、飞书与附件交付规则
- `references/engineering-figures-imagegen.md`：开篇产品图和工程机制图的 ImageGen 规范
- `references/project-library-archive.md`：手稿封版后登记到简历项目库的唯一入口、写入与复读规则
- `scripts/validate_clarification_gate.py`：封版前检查澄清项是否全部解决
- `scripts/validate_real_interview_package.py`：校验原题计数、正式问题映射、单答案与唯一档案入口

## License

MIT
