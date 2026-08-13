---
name: requirement-analysis
description: 对新需求、变更说明、PRD 或技术方案进行可追踪的 QA 需求分析。需要识别最小充分上下文、影响、风险、未知项和测试重点时使用；即使没有需求文档或技术文档，也可基于用户直接输入进行保守分析。
---

# Requirement Analysis

为当前 Change 生成 `changes/{CHANGE-ID}/analysis.md`。

## 输入与读取顺序

1. 用户当前描述；
2. 用户明确指定的 `requirements/`、`technical-docs/` 文件；
3. `knowledge/INDEX.md` 及其命中的知识文件；
4. 仅在冲突、兼容性或依赖确实影响结论时读取其他资料。

需求和技术文档均为可选且可以是多份。不得因为资料缺失而创建空文档，也不得默认扫描整个资料库、Knowledge 或历史 Change。

## 输出结构

`analysis.md` 至少包含：

- Status 与 Test Readiness；
- Evidence：只列实际资料；无文档时登记用户直接输入；
- Context Used：路径、用途、关键发现；
- Goal、Confirmed Existing Behavior、Confirmed New Behavior；
- Affected Modules 与业务、状态、权限、数据、接口、依赖影响；
- Failure、Boundary、Concurrency、Async、Security、Compatibility；
- Regression Scope；
- Unknowns、Assumptions、Questions；
- 带稳定 `TF-*` ID 和优先级的 Test Focus；
- Knowledge Candidates。

## 规则

- 只有 Evidence 支持的内容才写入 Confirmed。
- 信息不足时继续输出可审阅分析，将缺口标为 `UNK-*`。
- 通用 QA 风险可以列为候选验证场景，但不得写成系统已存在事实。
- 受 Unknown 阻塞的 Test Focus 必须引用对应 `UNK-*`。
- 本 Skill 不生成正式测试步骤。
