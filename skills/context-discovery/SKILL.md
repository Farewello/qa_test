---
name: context-discovery
description: 为 QA 需求分析发现最小充分上下文。处理新需求、PRD、技术方案或准备调用需求分析 Skill 时必须使用；负责输入识别、Knowledge 路由、依赖扩展、Evidence 缺口和受控扩读，不负责完成需求分析或生成测试用例。
---

# Context Discovery

目标是找到完成当前 QA 需求分析所需的最小充分上下文，而不是读取尽可能多的文件。

## 输入

- `changes/{REQ}/state.json`
- `changes/{REQ}/input/` 中的当前 Requirement Evidence
- `changes/{REQ}/sources.md`
- `knowledge/INDEX.md`
- 已存在的 `changes/{REQ}/context.md`（增量扩读时）

## 输出

更新 `changes/{REQ}/context.md`，格式参考 `standards/templates/context.md`。

只允许额外更新：

- `sources.md`：登记输入文件、类型和用途；
- `normalized/`：在原始输入不便消费时保存提取文本；
- `state.json`：上下文完成后将 `workflow_state` 更新为 `CONTEXT_READY`。

不得修改 `analysis.md`、`testcases/` 或 `knowledge/`。

## 工作流

### 1. 识别当前需求

从用户指令、`state.json` 和 Requirement Evidence 中提取：

- Entity；
- Action；
- State；
- Role；
- 显式模块；
- 业务关键词；
- 疑似权限、数据、接口、异步、兼容和依赖信号。

原始输入可以是文本、Markdown、图片、PDF、Word 或其他文档。需要提取时，将标准化文本写入 `normalized/`，保留原始文件不变，并在 `sources.md` 中建立对应关系。

### 2. 执行一级路由

读取 `knowledge/INDEX.md`，根据 Requirement Signals 选择候选模块。

如果索引没有匹配模块：

- 不递归扫描整个 Knowledge；
- 将模块知识缺口写入 `context.md`；
- 使用当前 Evidence 继续分析；
- 不为推测中的模块创建 Knowledge 文件。

### 3. 读取模块入口

优先读取候选模块的 `overview.md`。根据入口给出的路由条件，只选择与当前需求有关的专题文件：

- 业务规则变化读取 `rules.md`；
- 状态变化读取 `states.md`；
- 接口变化读取 `interfaces.md`；
- 上下游影响读取 `dependencies.md`；
- QA 风险读取 `risks.md`。

不要机械读取该模块下的所有文件。

### 4. 受控扩展依赖

仅在已读 Knowledge 或当前 Evidence 出现明确触发关系时扩展依赖。例如：

```text
Order cancel
→ triggers refund
→ read Payment refund knowledge
```

每次扩读前在 Expansion Decisions 中说明：

- 候选内容；
- Read 或 Skip；
- 为什么该内容会改变需求分析结论或测试范围。

### 5. 按需回溯 Evidence

只有以下情况才读取技术方案具体章节或历史 Change：

- Knowledge 无法确认关键行为；
- Existing Knowledge 存在冲突；
- 当前需求明确修改历史行为；
- 需要解释兼容逻辑或规则来源；
- 需求分析 Skill 提出了明确的 Additional Context Request。

优先读取可定位章节，不默认读取长文档全文。

### 6. 区分事实和未知项

- 有可靠 Evidence 支持的内容写入 Confirmed Facts。
- 无法确认的内容写入 Evidence Gaps 或 Unknowns。
- 不得把 QA 常见风险自动写成本系统已存在的事实。
- 可以把常见风险作为分析提示，但必须标为待验证。

### 7. 判断停止

满足以下条件时停止扩读：

- 能解释 Existing Behavior 和目标 New Behavior；
- 能识别主要影响模块和明确依赖；
- 能列出关键风险与信息缺口；
- 继续读取其他文件不会显著改变分析结论；
- 已形成明确的 Analysis Input Set。

如果仍不足，只提出下一项最小读取请求，不创建未经授权的事实。

## 与需求分析 Skill 的交接

调用 `standards/skill-bindings.json` 中绑定的 `requirement-analysis` Skill，向它提供：

1. `context.md`；
2. Analysis Input Set 中明确列出的文件；
3. 输出位置 `analysis.md`；
4. Unknown 不得视为事实的约束。

绑定状态不是 `bound` 时停止并报告，不得临时编造需求分析 Skill。

