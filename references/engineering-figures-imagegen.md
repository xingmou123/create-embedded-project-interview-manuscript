# 项目面试手稿的纯 ImageGen 工程配图规范

本规范继承 `create-hw-sw-design-docs` 的工程配图标准，并针对项目面试手稿收敛为“少而关键、紧贴问题、能帮助学员讲清机制”。创建、改写、补图、换图或正式交付手稿时必须读取并执行。

## 目录

- [1. 图源与事实边界](#1-图源与事实边界)
- [2. 配图计划](#2-配图计划)
- [3. 纯 ImageGen 约束](#3-纯-imagegen-约束)
- [4. 统一视觉语言](#4-统一视觉语言)
- [5. 提示词模板](#5-提示词模板)
- [5.1 开篇写实产品图](#51-开篇写实产品图)
- [5.2 工程关系图](#52-工程关系图)
- [6. 生成、筛选与迭代](#6-生成筛选与迭代)
- [7. 资产与内部证据](#7-资产与内部证据)
- [8. 插入与验收](#8-插入与验收)

## 1. 图源与事实边界

先锁定项目主路线，再规划图片。所有图中的模块、接口、方向、状态、数值和职责都必须来自 `project-ledger.md` 的单一口径。

图源只允许两类：

1. 用户提供或权威来源的真实照片、板卡图、原理图、波形、日志、界面截图和测量图。这些是来源图，不得伪装成自定义图。
2. 使用内置 `imagegen` 新生成的自定义解释图。

没有真实素材时，工程机制、PCB 分区、协议、状态和调试路径使用抽象模块框与工程符号；产品总览、佩戴方式和 HUD 视角可以生成克制的产品展示图，用来让学员看懂整机形态与使用方式。先检查用户已经提供的附件和工作区；没有实物、板卡、原理图、截图、Logo 或参考图时直接使用 ImageGen，不把“是否有素材”作为澄清问题。只有用户明确要求必须使用某份尚未提供的真实素材时，才请求补充。可见文档不写“概念图”“非实物”“真实样机照片”等来源提示，生成图也不能被口述成现场照片或测试证据。

禁止把旧设计图直接当成正确答案。软硬件设计文档用于提取要表达的架构和机制；复用来源图前必须核对当前项目路线，普通解释图应按本规范重新用 ImageGen 生成。

## 2. 配图计划

搭建手稿章节时建立内部表格：

| 图号 | 目标章节 | 理解难点 | 图型 | 核心路线/关系 | ImageGen 提示词摘要 | 插入位置 | 图注 |
|---|---|---|---|---|---|---|---|

主架构图用于第一遍看懂系统，只画端到端核心路线和责任边界。复杂项目继续从软硬件设计内容中选择真正降低理解成本的机制图：

- 多处理器、设备/App/网关/云端的执行域与职责边界；
- 数据从采集、缓冲、处理、判断、传输到显示/执行的完整路线；
- RTOS 任务、事件、队列、DMA、回调和缓冲所有权；
- BLE、CAN、UART、XCP、UDS、HTTP 等协议的分帧、重组和链路分工；
- 状态机、超时、断连、降级和恢复路径；
- 内存、功耗、性能或资源约束之间的关系；
- 从需求澄清、接口冻结、实现验证到小批量交付的项目开发流程；
- 三个调试案例中的证据切分、根因链或验证路径。

典型跨端完整项目通常需要 3～6 张高价值图；简单单 MCU 项目可以只有 1～2 张。数量不是验收目标，但多执行域、协议、状态和案例全部只靠长段文字时，视为配图不足。

每张图紧跟它解释的标题或导语，不把所有图片堆在文档开头或末尾。总架构图通常放在 30/90 秒介绍之后；任务图、协议图、状态图和案例图放在对应问题组或案例附近。

设备、可穿戴、机器人、仪器和终端项目还必须单独规划一张开篇产品图。它放在第一个一级标题正下方，负责回答“这个东西具体长什么样、怎么佩戴或安装、和哪些配套端一起工作”。它不是总架构图，不能用抽象模块框替代。

## 3. 纯 ImageGen 约束

所有自定义解释图必须使用内置 `imagegen`。最终插入资产必须是被选中的 ImageGen 原图或字节一致的无损复制。

禁止使用或混入：

- 纯文本/ASCII 路线图和代码块；
- Mermaid、PlantUML、SVG、飞书画板、HTML/Canvas、PIL 或本地脚本图；
- 以 ImageGen 结果为底稿后本地改字、改箭头、裁剪、拼接、重排、重绘或调色；
- 与当前任务无关的历史生成图片。

飞书或 Word 只允许无损上传与显示缩放。图中文字、箭头、模块或布局不正确时，拒绝该候选并重新生成；不能靠正文解释错误，也不能本地修补。

## 4. 统一视觉语言

每张工程解释图遵守以下不可妥协的风格：

- 白色或极浅灰背景；
- 图内不放大标题，标题只写在文档图注；
- 深青色或深蓝灰表示正常主路径；
- 浅灰表示中性边界或从属关系；
- 橙色只表示异常、回退、降级或恢复；
- 中文为主，英文只保留真实技术标识，如 `ESP32-S3`、`BLE GATT`、`FastAPI`、`CRC`、`MTU`、`Frame ID`、`PSRAM`；
- 标签短、字号可读、留白充足、线条细且统一；
- 主架构图通常控制在 4～5 个子系统块，每块只保留 3～5 个短标签；
- 只画核心箭头，不画所有内部依赖。

产品展示图遵守同一套克制视觉语言：产品、手机和车内环境只用于交代使用关系，不做广告海报，不添加品牌 Logo，不伪造序列号、测试标签、仪器读数或生产现场证据。PCB 自研路线已经锁定时，工程图必须明确“自研主板”边界，不能画成开发板、杜邦线或模块堆叠。

禁止装饰图标、科技海报、发光效果、重渐变、重阴影、饱和多色、长句、密集字段、营销式构图和英文-only 图。

## 5. 提示词模板

产品形态和工程机制使用不同的 ImageGen 类型。开篇产品图使用 `product-mockup`；架构、协议、状态和资源关系使用 `infographic-diagram`。不要把写实产品图提示词和精确工程图提示词混在同一张图里。

### 5.1 开篇写实产品图

```text
Use case: product-mockup
Asset type: opening product visualization for a formal Chinese embedded-project interview manuscript
Primary request: Create a photorealistic, physically plausible visualization of <产品/系统>. The viewer must immediately understand <设备本体、佩戴/安装方式、配套端和环境关系>.
Scene/backdrop: <安全、受控、符合项目实际的使用场景>
Subject details: <锁定的外形、主机、显示/交互、手机/上位机/网关/接口>; show no unsupported hardware
Style/medium: restrained industrial product photography, realistic materials and optics, engineering-documentation aesthetic rather than advertising
Composition/framing: 16:9 landscape; product is the primary subject; supporting devices remain clearly visible; no large title inside the image
Lighting: natural or soft neutral light; accurate shadows; no neon glow
Color palette/materials: neutral industrial colors with restrained project accent colors
Text constraints: no paragraphs; avoid in-image labels unless a very short verified technical label is essential
Avoid: brand logos, serial numbers, VIN/license plates, production labels, copyrighted UI, fake test readings, sci-fi holograms, bulky VR headset when the project is smart glasses, exposed development boards, Dupont wires, invented sensors/interfaces, marketing-poster layout, watermark, and unsafe operation.
```

按项目补充以下约束：

- 跨端系统不能只生成单品照；必须让设备本体与手机、上位机、网关或接口的使用关系可见。
- 车载场景默认车辆静止或处于封闭、受控的测试状态；人物不边驾驶边操作电脑，笔记本和手机需要安全固定。
- 可穿戴设备必须符合真实重量、光学位置、佩戴尺度和人体工学；智能眼镜不能画成 VR 头显或悬浮全息屏。
- 自研 PCB 已锁定时，不展示开发板、杜邦线和模块堆叠；除非正文确实说明外壳打开，否则产品图不暴露板卡。
- HUD 只显示少量经过确认的变量或状态，避免长文本和看似真实的测试编号。生成图不得被当作样机、路试或量产证据。

产品图原图检查必须覆盖：外形物理可行、佩戴/安装关系正确、配套端齐全、环境安全、没有新增硬件、没有品牌与伪证据、没有科幻/广告风格。任一项不合格就重生。

### 5.2 工程关系图

使用 `imagegen` 的 `infographic-diagram` 类型，按以下结构组织提示词。不要照抄示例路线，必须替换为项目底稿锁定的真实路线。

```text
Use case: infographic-diagram
Asset type: formal Chinese embedded-project interview manuscript engineering figure
Primary request: Create a clean <图型> for <项目>. Show exactly <模块/状态数量> and the locked route: <逐项写出真实路线>.
Scene/backdrop: pure white background with generous whitespace
Style/medium: restrained vector-like engineering diagram, thin lines, flat shapes, consistent spacing, no poster styling
Composition/framing: 16:9 landscape; <从左到右 / 从上到下 / 泳道 / 状态布局>; only core arrows
Color palette: deep teal for normal paths; white or very light gray subsystem fills; dark blue-gray text; orange only for exception/fallback/recovery
Text (verbatim):
"<逐条列出必须准确渲染的短标签>"
Constraints: render every quoted label verbatim; Chinese-first typography; no title inside the image; no decorative icons; no logo; no watermark; no glow; no gradients; no heavy shadows; no extra modules; no extra arrows; no invented labels; no long paragraphs. For engineering diagrams, use abstract blocks and symbols. For approved product-overview or HUD-view figures, show only the locked product relationships and never add serial numbers, test stickers, measurement evidence, factory scenes, or unsupported hardware details.
```

主架构图追加以下限制：

```text
Keep the diagram to four or five subsystem blocks. Show the core route, not a component inventory. Put secondary detail in the manuscript body or a later mechanism figure.
```

状态/恢复图追加以下限制：

```text
Use deep teal solid arrows for the normal state path and orange dashed arrows only for timeout, disconnect, error, fallback, or recovery. Do not draw theoretical transitions that are not part of the locked design.
```

协议/分帧图追加以下限制：

```text
Keep field names and arrow direction exact. If detailed fields would become unreadable, use numbered callouts and explain the numbers in the document instead of adding tiny text.
```

开发流程图追加以下限制：

```text
Show the project-specific lifecycle in chronological order. Each stage has one short action label and one short deliverable label. Use review gates between stages and orange return arrows only for failed reviews. Do not turn the figure into a generic circular process poster.
```

## 6. 生成、筛选与迭代

1. 先对一张小图执行文件输出预检，确认本次生成产生了新的图片文件。
2. 每张图生成后检查原图，不以缩略图判断。
3. 逐项检查：文字、箭头、核心路线、模块数量、颜色语义、中文可读性、图内标题、装饰元素和虚构内容。协议图必须逐行对照 `INT-ID`，状态图必须区分持续状态与瞬时事件/覆盖层，流程图必须核对阶段先后、评审门和回退位置。
4. 候选有一项错误就拒绝。下一轮只针对一个主要问题收紧提示词，例如缩短标签、减少模块或明确箭头方向。
5. 多次生成仍无法保证精确关系时，删去不可靠细节，把细节放进正文/表格；如果核心关系仍不可靠，则不插图并报告阻塞，不能切换到本地绘图。

生成来源和 SHA-256 只能证明图片是 ImageGen 原图，不能证明工程语义正确。最终候选必须再做一次隔离复核：复核者只拿项目口径底稿、接口方向合同和候选原图，不读取生成提示词；让复核者反向列出模块、角色、方向、状态、正常路径与异常路径。反向结果与底稿任一项不一致时拒绝该图。

拒绝条件包括：乱码或自创文字、箭头方向错误、路线冲突、多余模块、图内大标题、装饰图标、橙色用于正常路径、颜色过多、长句、科技海报风格、把自研主板画成开发板/模块拼接、产品形态不符合人体工学、危险操作，以及任何会被误当成测试证据或生产记录的细节。

## 7. 资产与内部证据

项目使用的最终图片必须从 `$CODEX_HOME/generated_images/...` 无损复制到项目工作区，不能只引用生成缓存。不得覆盖已有资产，使用稳定且可区分的版本文件名。

内部保留配图证据，不写入学员可见手稿：图号、提示词摘要、候选数量、选中原图路径、最终资产路径、两者 SHA-256、拒绝原因、隔离语义复核结果和允许操作（通常为 `copy only`）。复制后校验两份文件的 SHA-256 一致。

## 8. 插入与验收

- 每张图使用文档外部图注，例如 `图 3-1 系统数据流与职责边界`；图内不重复标题。
- 开篇产品图位于第一个一级标题正下方，先于项目背景长文；它不能被抽象架构图或孤立的 HUD 截图替代。
- 替换旧图时，先插入并定位新图，再删除旧图，最后回读确认只剩新图。
- 飞书写回后检查图片紧跟目标章节、宽度合适、图注存在、旧图和文本路线图已删除。
- 全文检查不存在 `<pre>`/代码块承载的路线图，不存在“Plain Text”式架构图。
- 图、30/90 秒介绍、紫色回答和三个案例必须使用同一项目口径。
- 未执行配图计划、未检查原图、未插入对应章节或仍有错误箭头/文字时，不得宣称正式交付。
