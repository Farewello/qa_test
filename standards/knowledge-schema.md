# Knowledge Schema

Knowledge 使用 Markdown 保存。每条知识必须是有稳定 ID 的原子、可引用、可演进单元。

## 推荐格式

```md
### ORD-RULE-003 | 已支付订单允许取消

- Type: business-rule
- Status: planned
- Scope: Order / Cancellation / PAID
- Fact: PAID 状态订单允许用户主动取消。
- Conditions: 订单尚未进入发货流程。
- Effects: 触发异步退款和库存释放。
- Effective from: REQ-102，发布时间待确认
- Evidence:
  - changes/REQ-102/input/requirement.md#已支付订单取消
  - changes/REQ-102/input/technical-design.md#退款流程
- Last verified: 2026-08-13
- Supersedes: ORD-RULE-001
```

## 字段规则

- ID：模块前缀、知识类型和序号组成，在仓库内唯一。
- Type：`business-rule`、`state`、`interface`、`dependency`、`risk`、`permission`、`data-rule` 等。
- Status：`planned`、`active` 或 `deprecated`。
- Scope：用于检索和冲突检测的最小业务范围。
- Fact：单一、明确、可验证的系统认知。
- Evidence：至少一个可定位的项目内证据路径。
- Last verified：最近一次被可靠 Evidence 确认的日期。
- Supersedes：只在替代旧知识时使用。

## 写入资格

同时满足以下条件才允许自动写入：

- 项目特定；
- 对未来 QA 任务有复用价值；
- Scope 清晰；
- 有明确 Evidence；
- 不是 Agent 推测、测试用例、临时数据或未确认 Assumption。

