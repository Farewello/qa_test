# QA Test

这是一个面向 Coding Agent 的轻量 QA 项目，用于完成：

1. 需求分析；
2. 最终测试用例生成；
3. 有证据的项目知识更新。

## 核心路径

| 路径 | 作用 | 是否必需 |
|---|---|---|
| `requirements/` | 保存 PRD、用户故事、需求说明等原始资料 | 否 |
| `technical-docs/` | 保存技术方案、接口说明、数据设计等资料 | 否 |
| `changes/{CHANGE-ID}/analysis.md` | 当前变更的需求分析 | 是 |
| `testcases/{CHANGE-ID}/cases.md` | 可交付的最终测试用例 | 是 |
| `changes/{CHANGE-ID}/update.md` | Knowledge 更新审计记录 | 是 |
| `knowledge/INDEX.md` | 项目知识路由入口 | 是 |

需求和技术文档是独立资料源，不强制一一对应。例如，同一个 Change 可以只有需求、只有技术文档、同时引用多份资料，或者仅使用用户当前描述。

## 使用方式

向 Agent 提供 `CHANGE-ID` 和现有资料路径，然后要求执行完整流程。示例：

```text
处理 CHG-102：
- 需求：requirements/REQ-88/requirement.md
- 技术文档：technical-docs/EXPORT-2/api.md
- 输出需求分析、最终用例并更新 Knowledge
```

没有文档时可直接提交：

```text
处理 CHG-103：支持文件导出。没有需求和技术文档，请按现有信息完成分析和用例设计。
```

Agent 的详细执行规则见 `AGENTS.md`。`changes/REQ-001/` 和 `testcases/REQ-001/` 是“文件导出”极简输入的已验证示例；由于规格不足，用例被明确标记为受阻，而不是补造业务规则。
