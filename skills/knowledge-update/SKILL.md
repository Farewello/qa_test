---
name: knowledge-update
description: 在需求分析和测试用例完成后，将本次 Change 中有 Evidence 的稳定系统认知合并回 Project Knowledge。处理知识沉淀、规则变更、冲突、废弃、QA 风险或任务收尾时必须使用；执行 Knowledge Merge 而非简单追加，禁止把推测、Unknown、Assumption 或测试用例写成事实。
---

# Knowledge Update

目标是让 Project Knowledge 随需求演进，同时防止知识污染和自相矛盾。

## 前置条件

- `analysis.md` 已通过 `standards/analysis-quality-gate.md`；
- 测试用例已经生成；
- Requirement 和必要 Technical Evidence 可定位；
- `state.json` 中 `delivery_status` 已明确，无法确认时使用 `planned`；
- 当前 Knowledge 已通过索引定位，不递归读取无关模块。

## 输入优先级

按可靠性从高到低使用：

1. Requirement 明确规定；
2. Technical Design 明确说明；
3. 发布记录、接口契约或可验证运行证据；
4. 多个可靠 Evidence 一致支持的结论；
5. `analysis.md` 中带 Evidence 的 Confirmed Facts。

测试用例不是系统事实 Evidence。缺陷只有在被确认并具有可靠证据后，才能成为 QA Risk Knowledge。

## 输出

- 对 `knowledge/` 执行最小必要 Patch；
- 生成或更新 `changes/{REQ}/knowledge-update.md`；
- 必要时更新模块 `overview.md`；
- 只有新增模块、路由关键词或依赖入口变化时更新 `knowledge/INDEX.md`；
- 成功后将 `workflow_state` 更新为 `KNOWLEDGE_UPDATED`。

## Merge 算法

### 1. 提取 Knowledge Candidates

从 Analysis 和 Evidence 中提取：

- 新增业务规则；
- 状态机变化；
- 权限或数据规则；
- 接口和模块依赖变化；
- 已确认的 QA 风险、失败模式或兼容性行为；
- 旧知识的失效或适用条件变化。

### 2. 资格判断

候选知识必须同时满足：

- 项目特定；
- 对未来 QA 任务可复用；
- Scope 明确；
- 有可定位 Evidence；
- 不是 Agent 推测、Unknown、Assumption、临时数据或一次性实施细节。

不满足时执行 `SKIP`，并记录原因。

### 3. 定位现有知识

通过 `knowledge/INDEX.md` 和模块入口定位同一 Scope 的现有 Knowledge。搜索：

- 相同 Knowledge ID；
- 相同 Entity / Action / State；
- 语义相同的重复规则；
- 新旧行为互斥的冲突规则；
- 被新规则缩小或扩大的适用条件。

### 4. 决定操作

- `CREATE`：没有等价知识，且候选满足写入资格。
- `UPDATE`：同一事实的条件、效果、Evidence 或验证时间变化。
- `DEPRECATE`：旧事实已失效或被新规则替代。
- `SKIP`：重复、证据不足、一次性信息或无法裁决冲突。

不得保留两条相互冲突的 active Knowledge。

### 5. 决定状态

- `delivery_status=planned` 或无法确认生效：新知识使用 `planned`。
- 有可靠发布或生效 Evidence：使用 `active`。
- 被替代或确认失效：使用 `deprecated`，并指向替代知识。
- 需求取消：不得把该需求的 planned 知识提升为 active。

### 6. 应用最小 Patch

遵循 `standards/knowledge-schema.md`：

- 每条知识拥有唯一稳定 ID；
- 保留 Fact、Conditions、Effects、Evidence、Last verified；
- 修改原知识而不是在文件末尾追加冲突段落；
- 不复制长篇 Requirement 或 Technical Design 原文。

### 7. 记录审计结果

按照 `standards/templates/knowledge-update.md` 记录每个候选的操作、目标、Evidence 和结果。无法自动裁决的冲突必须留在 Conflicts 中，并执行 `SKIP`。

## 完成校验

执行：

```powershell
python scripts/qa.py validate-knowledge
python scripts/qa.py validate --change {REQ}
```

校验失败时修复结构或撤销不合格候选，不得通过删除 Evidence 要求来绕过校验。

