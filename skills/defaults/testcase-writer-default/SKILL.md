---
name: testcase-writer-default
description: 从 testcase-handoff.md 和 analysis.md 生成可追踪的 Markdown 测试用例与覆盖矩阵。仅用于项目框架验证或真实用例生成 Skill 尚未接入时；不得重新从零分析需求，不得将 Unknown 转成确定前提。
---

# Default Test Case Writer

这是可替换的最小默认实现，用于验证 Analysis → Cases 接口，不代表组织最终用例格式。

## 输入

只读取：

1. `testcase-handoff.md`；
2. `analysis.md`；
3. Handoff 中明确列出的 Knowledge 和 Evidence。

## 输出

生成：

- `testcases/cases.md`；
- `testcases/coverage.md`。

每个用例至少包含：ID、关联 Test Focus、优先级、类型、前置条件、步骤、预期结果和 Unknown 依赖。

## 生成规则

- 每个 P0 Test Focus 必须映射到至少一个用例或明确标记 `Blocked`。
- 需求明确的行为生成可执行用例。
- 依赖未明确规格的行为生成设计级用例，并在前置条件中引用 `UNK-*`，覆盖状态标记 `Blocked`。
- 不自行补充文件格式、权限、大小限制、超时时间等数值。
- 不修改 `analysis.md`、Requirement Evidence 或 `knowledge/`。
- 覆盖状态只能使用 `Covered`、`Partial`、`Blocked`、`Not covered`。

