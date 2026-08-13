---
name: testcase-generation
description: 根据 changes/{CHANGE-ID}/analysis.md 生成可追踪的最终测试用例。需要把 TF-* 测试重点转成正常、异常、边界、安全、兼容或可靠性用例，并保留 Unknown 阻塞关系时使用。
---

# Test Case Generation

读取 `changes/{CHANGE-ID}/analysis.md`，输出 `testcases/{CHANGE-ID}/cases.md`。

只有当分析不足以设计用例时，才读取分析中明确登记的 Evidence 或 Knowledge；不得从零重新分析需求。

## 用例字段

每条用例至少包含：

- 用例 ID 和标题；
- `Covers: TF-*`；
- Priority、Type、Status；
- Preconditions；
- Steps；
- Expected；
- Unknown dependency（没有则写 `None`）。

## 规则

- 每个 P0 Test Focus 至少映射一条用例。
- 已明确的行为生成可执行用例。
- 依赖未知规格的行为仍可形成设计级用例，但 `Status` 必须为 `Blocked` 并引用 `UNK-*`。
- 不补造文件格式、权限、阈值、超时等业务细节。
- 覆盖关系直接写入 `Covers`，不再单独维护覆盖矩阵。
- 不修改需求分析、原始资料或 Knowledge。
