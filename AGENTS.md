# QA Knowledge Project Instructions

## 项目目标

本项目使用结构化 Knowledge、历史 Change 和可复用 Skills，为 QA 需求分析和测试用例生成提供长期外部记忆。核心资产必须保持 Agent-neutral、Git-native 和可审计。

## 核心路径

- Skill 绑定：`standards/skill-bindings.json`
- Knowledge 一级入口：`knowledge/INDEX.md`
- 当前需求工作区：`changes/{requirement-id}/`
- Agent-neutral Skills：`skills/`
- 质量门禁与模板：`standards/`
- 机械校验：`python scripts/qa.py`

## 标准工作流

处理需求时严格按以下顺序执行：

1. 确定 Requirement ID 和 `changes/{REQ}/`。
2. 读取 `state.json`、当前 Requirement Evidence 和 `knowledge/INDEX.md`。
3. 使用 `context-discovery` 找到最小充分上下文，生成 `context.md`。
4. 调用 `standards/skill-bindings.json` 中绑定的现有需求分析 Skill，生成 `analysis.md`。
5. 按 `standards/analysis-quality-gate.md` 校验分析结果；上下文不足时回到步骤 3 精确扩读。
6. 生成 `testcase-handoff.md`，只列出用例生成确实需要的 Analysis、Knowledge 和 Evidence。
7. 调用绑定的现有用例生成 Skill，将结果写入 `testcases/`。
8. 生成 `testcases/coverage.md`，追踪 Test Focus 与测试用例的覆盖关系。
9. 使用 `knowledge-update` 执行 Knowledge Merge，生成 `knowledge-update.md`。
10. 运行 `python scripts/qa.py validate --change {REQ}`，通过后更新任务状态。

不得跳过 Requirement Analysis 直接生成测试用例。

`workflow_state=DONE` 只表示 QA 工作流已经结束。必须同时读取 `test_readiness`：`ready` 表示全部 Test Focus 已覆盖，`partial` 表示部分覆盖或阻塞，`blocked` 表示全部用例受 Unknown 或外部条件阻塞。

## Progressive Context Loading

按以下层级逐步加载，不得默认递归读取全部 Knowledge 或全部历史 Change：

- L0：本文件。
- L1：当前 Change、Requirement Evidence、`knowledge/INDEX.md`。
- L2：相关模块的 `overview.md` 和本次问题确实需要的专题知识。
- L3：存在明确触发关系的依赖模块。
- L4：仅在 Knowledge 不足、冲突或需要兼容性证据时读取技术方案具体章节或历史 Change。

每次扩读都必须在 `context.md` 中写明路径、原因和关键发现。

## Existing Skill Integration

- 不复制、不改写现有需求分析 Skill 和用例生成 Skill 的内部流程。
- 两个 Skill 被视为黑盒，通过 `standards/skill-bindings.json` 绑定。
- 需求分析 Skill 的受控入口是 `context.md`，正式输出是 `analysis.md`。
- 用例生成 Skill 的受控入口是 `testcase-handoff.md`，不得默认从原始需求重新分析。
- 如果绑定状态不是 `bound`，停止对应阶段并明确报告缺少的 Skill。

## Evidence 与 Knowledge

- Evidence：PRD、截图、技术方案、接口说明、发布记录、历史 Change 等原始或近原始材料。
- Knowledge：从 Evidence 提炼出的、稳定、可复用、面向未来 QA 任务的系统认知。
- Agent 推测、Unknown、Assumption、临时实现细节和测试用例不能直接成为 Knowledge。
- 新需求尚未生效时，相关 Knowledge 状态只能是 `planned`。
- Knowledge 更新必须执行 CREATE / UPDATE / DEPRECATE / SKIP，不得只做 Append。
- 每条 Knowledge 必须有稳定 ID、状态、Scope、Fact、Evidence 和 Last verified。

## 完成条件

Change 标记为 `DONE` 前必须满足：

- `analysis.md` 通过质量门禁；
- 测试用例已经生成；
- 所有 P0 Test Focus 在 `coverage.md` 中有结果；
- Knowledge 候选已完成 Merge 或记录 SKIP 原因；
- 项目校验通过；
- Unknown 和 Assumption 没有被写成确定事实。
