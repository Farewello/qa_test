---
name: requirements-analysis-default
description: 从受控的 context.md 和已列明 Evidence 生成保守、可追踪的 QA Requirement Analysis。仅用于项目框架验证或真实需求分析 Skill 尚未接入时；遇到信息不足必须输出 Unknown，不得推测业务事实，也不得生成正式测试用例。
---

# Default Requirement Analysis

这是可替换的最小默认实现，用于验证工作流，不代表组织最终需求分析标准。

## 输入

读取当前 Change 的：

1. `context.md`；
2. `context.md` 的 Analysis Input Set 明确列出的文件；
3. `standards/analysis-quality-gate.md`。

不要递归读取整个 `knowledge/` 或其他历史 Change。

## 输出

生成 `analysis.md`，至少包含：

- Requirement Goal；
- Confirmed Existing Behavior；
- Confirmed New Behavior；
- Affected Modules；
- Business / State / Permission / Data / Interface / Dependency Impact；
- Failure、Boundary、Concurrency、Async、Security、Compatibility；
- Regression Scope；
- Unknowns、Assumptions、Questions；
- 带 `TF-001` 形式稳定 ID 的 Test Focus；
- Knowledge Candidates。

## 分析规则

- 只把有 Evidence 的内容写入 Confirmed。
- 只有需求明确表示“新增、修改或保持”时，才断言 Existing/New Behavior。
- 输入只有功能标题时，把格式、范围、权限、数据量、同步方式、安全要求和失败行为列为 Unknown。
- QA 常见风险可以成为 Test Focus，但要标注“候选验证场景”，不能写成系统已有事实。
- 不因信息不足停止产出；生成可审阅的分析，并将受阻测试点关联到对应 `UNK-*`。
- 不生成正式测试步骤和预期结果。

