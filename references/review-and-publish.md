# 只读技术复核与飞书交付（Stage 3）

## 1. 独立只读技术复核契约（Stage 3）

完成活人正文初稿后，新开一次独立只读复核（Antigravity 环境经 `invoke-codex.ps1 -Mode audit` 派 Codex；单 Codex 环境必须新开独立只读会话，绝不复用 Stage 2 写稿会话）：

- **Codex 只查硬伤**：芯片引脚复用冲突、时钟/采样/总线负载计算错误、Flash 擦写与 ECC 约束违规、RTOS 中断优先级违规、协议方向/字节序/CRC 算错。
- **Codex 禁止做的事**：禁止改写中文口述腔调，禁止往正文里塞“本方案/冻结/设计基线/推演语态”或叠甲尾句，禁止把调试案例退回“如果出现…我会…”。
- **两级分级**：只修会导致技术硬伤或算错数的**阻塞项**；风格偏好记为建议，不挡交付。最多 2 轮止损。

## 2. 自动检查与飞书写入验收

1. **跑双脚本硬检查**：
   - 对全部紫色口述正文运行 `python -X utf8 scripts/lint_spoken_prose.py <口述文件>`，确保 **0 硬错误**（零制作标签、零内部黑话泄漏、零叠甲尾句），并逐项清理 AI 味告警；
   - 含团队真实面经时运行 `python -X utf8 scripts/validate_real_interview_discovery.py <work>/real_interview_discovery.json --package <work>/real_interview_package.json` 及 `python -X utf8 scripts/validate_real_interview_package.py <work>/real_interview_package.json --archive-file <学员原题档案导出的 XML/文本>`，确保学员原题档案 **0 条内部复盘链接泄漏**；完整任务同步通过 `validate_clarification_gate.py` 与 `validate_small_batch_plan.py`。
2. **飞书发布原则**：
   - 默认维护一份飞书活稿，优先使用 `lark-cli docs +update` 局部更新，严禁覆盖用户近期手动微调；
   - 替换全文时保护既有图片 token 与文末真实面经原题档案卡片；
   - 写回后**必须重新 `docs +fetch --detail full` 复读核验**（`--detail simple` / `with-ids` 会剥离颜色标签）：检查紫色/灰色样式、配图数量与位置、表格、代码块、标题层级、0 硬错误、0 残留黑话。
3. **封版归档与权限**：用户明确确认封版后，用局部 `block_replace` 把唯一飞书活稿链接更新回《嵌入式简历项目库》对应条目的“项目手稿”处，并按团队规范核对学员只读权限（如组织内可读 + 3 个 SVIP 群静默只读 `need_notification=false`）。
