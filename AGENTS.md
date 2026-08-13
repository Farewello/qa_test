# QA 分析与用例项目

## 目标

本项目只保留三项核心能力：需求分析、测试用例生成、知识更新。所有产物均为 Markdown，便于 Codex、Claude Code 和人工共同维护。

## 目录

```text
requirements/                 可选的原始需求文档
technical-docs/               可选的技术文档
changes/{CHANGE-ID}/          本次分析与更新记录
testcases/{CHANGE-ID}/        最终测试用例
knowledge/                    有证据、可复用的项目知识
skills/                       Agent-neutral Skill
.agents/skills/               Codex Skill 入口
.claude/skills/               Claude Code Skill 入口
```

## 资料关系

- 一个 Change 可以引用 0 到多个需求文档、0 到多个技术文档。
- 需求文档、技术文档和 Change 不要求同名，也不要求一一对应。
- 没有需求文档或技术文档时，允许以用户直接描述作为 Evidence。
- 不为缺失的资料创建空占位文档；`analysis.md` 只登记实际使用的 Evidence。
- `requirements/` 和 `technical-docs/` 是资料库，不得默认全量读取。

## 标准流程

1. 确定 `CHANGE-ID`；若用户未提供，使用简短且唯一的 ID。
2. 使用 `requirement-analysis`，按需读取实际资料和 `knowledge/INDEX.md`，输出 `changes/{CHANGE-ID}/analysis.md`。
3. 使用 `testcase-generation`，根据分析输出 `testcases/{CHANGE-ID}/cases.md`。
4. 使用 `knowledge-update`，只合并有 Evidence 的稳定认知，并输出 `changes/{CHANGE-ID}/update.md`。

不得跳过需求分析直接生成正式用例。

## 渐进式上下文

按以下顺序读取，达到足以作出可靠结论时立即停止：

1. 本文件和用户当前输入；
2. 当前 Change 明确引用的需求、技术文档；
3. `knowledge/INDEX.md` 及命中的知识文件；
4. 只有发生冲突、兼容性问题或明确依赖时，才读取其他资料或历史 Change。

不得递归扫描全部 Knowledge、需求、技术文档或历史 Change。实际读取路径及用途记录在 `analysis.md` 的 `Context Used` 中。

## 证据规则

- 需求、技术文档、接口契约、发布记录和用户直接输入都可以作为 Evidence。
- 测试用例、Agent 推测、Unknown 和 Assumption 不能作为系统事实。
- 信息不足时输出 `UNK-*`，不得用通用经验补成已确认业务规则。
- Knowledge 更新使用 `CREATE / UPDATE / DEPRECATE / SKIP`，并保留 Evidence 路径。

## 完成条件

- `changes/{CHANGE-ID}/analysis.md` 包含 Evidence、Context Used、影响、风险、Unknown 和 `TF-*`。
- `testcases/{CHANGE-ID}/cases.md` 中每条用例通过 `Covers: TF-*` 建立追踪关系；受阻项明确引用 `UNK-*`。
- `changes/{CHANGE-ID}/update.md` 记录 Knowledge 合并或跳过原因。
