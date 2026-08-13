# E2E Flow Evaluation: 文件导出

## Outcome

- Workflow state: `DONE`
- Delivery status: `planned`
- Test readiness: `blocked`
- Validation: Passed
- Knowledge writes: 0
- Knowledge pollution: 0 detected

`DONE` 表示 QA 分析工作流已经走完，不表示需求已经可开发、可验收或测试已就绪。当前所有用例都受未解决规格问题阻塞。

## Flow Metrics

| Metric | Result |
|---|---:|
| Raw Evidence | 1 |
| Context files loaded | 3 |
| Unrelated files loaded | 0 |
| Unknowns | 7 |
| Test Focus | 8 |
| Generated test designs | 8 |
| Test Focus mapping | 8 / 8 |
| Executable cases | 0 |
| Blocked cases | 8 |
| Knowledge merge decisions | 1 SKIP |
| Knowledge CREATE / UPDATE / DEPRECATE | 0 / 0 / 0 |

## What Worked

1. Progressive Context Loading 生效：只读取 Requirement、Knowledge Index 和 System Overview，没有递归扫描空 Knowledge 或历史 Change。
2. Evidence / Assumption 边界生效：没有自行确定 CSV、Excel、同步、异步、权限或数据量规则。
3. Analysis → Cases 追踪生效：8 个 `TF-*` 均映射到 `TC-*` 和 Coverage 状态。
4. Knowledge Pollution 防护生效：过于宽泛的候选被 `SKIP`，没有为了完成流程创建空模块或无价值 Knowledge。
5. 状态门禁能够阻止空模板直接冒充正式产物。

## Findings

### P0 — Test readiness 与 workflow completion 原来混淆

原状态只有 `DONE`，无法表达所有测试用例均被 Unknown 阻塞。本次已增加独立的 `test_readiness`：

- `ready`：全部 Test Focus 已覆盖；
- `partial`：部分覆盖或部分阻塞；
- `blocked`：全部被规格或外部条件阻塞；
- `unknown`：尚未形成 Coverage。

### P1 — Skill 绑定曾存在部分写入风险

绑定器原来先写 `skill-bindings.json`，再创建 Adapter。Adapter 创建失败会留下“配置显示已绑定、实际不可发现”的半完成状态。本次已改为 Adapter 成功后再提交绑定配置，并增加失败测试。

### P1 — 默认 Skill 只能做框架验证

默认 Skill 能维持事实边界和追踪关系，但不是最终组织级分析/用例标准。真实 `requirements-analysis-plus` 和 `testcase-writer-plus` 恢复后，应使用 `bind --replace` 替换并重新跑本 Change 对比产物质量。

### P1 — 当前编排仍由 Agent 驱动

`qa.py` 负责工作区、状态和机械校验，不直接调用 Coding Agent 的 Skill。优点是 Agent-neutral；缺点是没有单命令全自动执行和统一运行日志。后续可增加 `run-log.md`，记录每阶段实际 Skill、Git commit、输入文件和执行时间，而不绑定某家 Agent API。

### P2 — `NORMALIZED` 对纯文本需求语义偏重

本次原始输入已是 Markdown，无需转换，但仍要经过 `NORMALIZED` 状态。建议未来将该阶段改名为 `INPUT_READY`，表示输入已经登记且“按需完成标准化”，避免让用户误以为所有输入必须转换。

### P2 — 结构门禁不等于语义质量评审

当前脚本能发现空模板、缺失 `TF-*`、无 Coverage、无 Merge Decision 等机械问题，但不能判断分析结论是否真正专业。需求分析仍需要 Agent 语义自检或独立 Review Skill。

## Recommendation

框架可以进入下一轮真实需求验证，但暂不应宣称生产就绪。下一步优先级：

1. 恢复并绑定两份真实 Skill；
2. 使用包含 PRD 和技术方案的真实需求重新 E2E；
3. 增加跨阶段 `run-log.md`；
4. 用第二个相关需求验证第一次 Knowledge 是否真正被复用；
5. 再决定是否将 `NORMALIZED` 改为 `INPUT_READY`。

