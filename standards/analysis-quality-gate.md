# Requirement Analysis Quality Gate

需求分析 Skill 可以保留自己的输出格式，但 `analysis.md` 必须能够明确回答以下语义问题。

## 必需语义

- 需求目标是什么？
- 已确认的 Existing Behavior 是什么？
- 已确认的 New Behavior 是什么？
- 哪些模块、角色、状态、接口、数据和上下游依赖受到影响？
- 正常、异常、边界、权限、并发、异步和兼容性风险是什么？
- 回归范围是什么？
- 哪些结论来自现有 Knowledge？
- 哪些内容仍是 Unknown、Assumption 或待确认问题？
- 用例生成需要覆盖哪些 Test Focus？

## 标识约定

为 Test Focus 分配稳定 ID：

```text
TF-001
TF-002
...
```

为 Unknown 分配稳定 ID：

```text
UNK-001
UNK-002
...
```

用例生成和覆盖追踪依赖这些 ID，但不强制分析 Skill 使用特定 Markdown 标题。

## 失败条件

满足任一条件时不得进入用例生成：

- Existing Behavior 与 New Behavior 混淆；
- 把 Assumption 写成确定事实；
- 缺少影响模块或依赖分析；
- 没有可追踪的 Test Focus；
- 关键 Evidence 缺失但没有记录 Unknown；
- 需求分析阶段已经生成大量正式测试用例，导致职责重叠。

