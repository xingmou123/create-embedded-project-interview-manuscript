# 最小澄清门

在生成正文、写回飞书、导出 DOCX 或修改正式附件之前，先完成本门禁。它内置 `grill-me` 的单问单答方式，但只追问真正需要用户决定的事项；能够查证或能够由资深架构师完成的工作，不交给用户。

## 全局证据策略

除非项目资料或用户对具体项目有明确、可追溯的确认，直接采用以下证据策略，不重复询问：

- 小批量量产只作为工程设计目标，不声称项目已经完成小批量交付；
- 调试案例逐个按证据分类，无法证实为真实历史时使用故障注入或设计推演语态；
- 量化结果逐项核验，无法证实时写作设计参数或未核实数据。

这些策略不授权虚构交付成熟度、故障历史、实测结果、命名客户、认证证书、项目日期、团队规模或个人职责。

## 先查证，再判断，最后才询问

把不确定项分成三类：

1. **可查证事实**：优先读取现有文件、代码、原理图、日志、测试记录、飞书最新 revision 或官方资料。能够查到时直接采用，不询问用户。
2. **架构师决策**：缺失的采样率、周期、缓存、阈值、超时、重试、任务资源、带宽、功耗和验收阈值，由执行者按照小批量量产经验选定最终值，并完成计算与裕量校核。技术路线冲突由执行者结合项目证据、官方约束和工程合理性裁决，不把 A/B/C 方案重新丢给用户。
3. **用户决策**：只有经过查证和工程判断后仍无法消除，而且会改变个人职责、产品物理形态或项目边界的冲突，才进入询问。

文字长短、章节顺序、配图位置、常规接口参数和其他不改变上述三类边界的事项，不得触发询问。

真实面经的收录范围、记录与原题计数、正式问题归并、主问题与嵌套追问、行业差异是否会改变答案以及正式问答的补强位置，均由执行者按 `real-interview-evidence.md` 判断，不触发用户询问。

## 单问单答

触发用户决策时，执行以下流程：

1. 每次只问一个问题，先解决会影响后续判断的上游问题；
2. 问题中给出推荐答案及简短理由，不让用户从空白开始设计；
3. 等待用户回答后冻结该决定，不换一种说法重复确认；
4. 继续查证和裁决剩余事项，只在仍满足“用户决策”条件时再问下一题；
5. 全部问题解决后，给出一份只包含目标、范围、已冻结决定和验收条件的简短确认稿；这一步只确认执行范围，不重新询问已经冻结的决定；
6. 用户确认可以执行后再正式生成或写回；确认前不得创建正式正文、图片、附件或修改活稿。

如果没有任何用户决策项，直接执行，不增加仪式性的“是否开始”确认。

## 架构师补全数字

缺少技术数字时直接选择一个最终值，不写宽泛区间。至少说明：

- 该值约束什么对象；
- 它依据的器件、协议、负载或量产经验；
- 最坏情况如何计算；
- 仍保留多少时序、带宽、RAM、Flash、功耗或可靠性裕量。

推导结果写入项目口径底稿。正文只呈现面试需要的最终值和依据，不暴露“估算、假设、待确认”等内部制作状态。

## 内部预检清单

需要落盘或完整封版时，在项目 `work` 目录保存 `clarification_gate.json`，并使用本 Skill 目录下的 `scripts/validate_clarification_gate.py` 验证。结构如下：

```json
{
  "version": 1,
  "project": "项目名",
  "global_defaults": {
    "delivery_maturity": "small_batch_design_target",
    "debugging_case_nature": "evidence_driven",
    "provided_quantitative_results": "evidence_driven"
  },
  "explicit_overrides": [],
  "questions_asked": false,
  "brief_confirmed": true,
  "issues": [
    {
      "id": "CG-001",
      "category": "engineering_parameter",
      "summary": "确定 BLE 单包应用层负载",
      "resolution": "architect",
      "decision": "根据协商 MTU 扣除协议开销后定值",
      "source_ref": "DEC-004",
      "status": "resolved"
    }
  ]
}
```

`category` 只使用：`source_fact`、`engineering_parameter`、`technical_route`、`personal_responsibility`、`product_form`、`project_boundary`。

`resolution` 只使用：`source`、`architect`、`user`。`source_fact` 只能由资料解决；`engineering_parameter` 和 `technical_route` 由资料或架构师解决；只有 `personal_responsibility`、`product_form`、`project_boundary` 可以进入用户询问。

`global_defaults` 必须保留上述三个固定策略。具体项目有证据支持的状态写入 `explicit_overrides`，每项记录 `field`、`value` 和 `source_ref`；同一字段只能覆盖一次。成熟度可覆盖为 `prototype`、`engineering_validation`、`small_batch` 或 `mass_production`；三个案例性质一致时可整体覆盖为 `confirmed_real`、`fault_injection` 或 `design_inference`，不一致时在项目底稿逐案记录；量化结果整体可覆盖为 `confirmed_real`、`design_parameter` 或 `unverified`，混合状态仍在项目底稿逐项记录。存在 `pending` 或 `unresolved`、用户已被询问但没有对应决定、确认稿尚未确认、全局策略缺失或覆盖没有明确来源时，禁止继续正式交付。

没有发生询问时，将 `questions_asked` 设为 `false`，`brief_confirmed` 设为 `true`，表示本次无需额外确认即可通过门禁。

该清单仅用于内部预检，不进入学员可见文档。
