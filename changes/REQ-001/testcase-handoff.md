# Test Case Generation Handoff

## Primary Input

- Requirement Analysis: `analysis.md`

## Test Focus

| ID | Focus | Priority | Analysis reference |
|---|---|---|---|
| TF-001 | 发起文件导出 | P0 | `analysis.md#12-test-focus` |
| TF-002 | 导出范围与查询条件一致 | P0 | `analysis.md#12-test-focus` |
| TF-003 | 权限、租户隔离与脱敏 | P0 | `analysis.md#12-test-focus` |
| TF-004 | 空数据、边界和大数据量 | P1 | `analysis.md#12-test-focus` |
| TF-005 | 格式、编码和特殊字符 | P1 | `analysis.md#12-test-focus` |
| TF-006 | 重复、并发和数据快照 | P1 | `analysis.md#12-test-focus` |
| TF-007 | 生成与下载失败处理 | P1 | `analysis.md#12-test-focus` |
| TF-008 | 客户端兼容性 | P2 | `analysis.md#12-test-focus` |

## Relevant Knowledge

- `knowledge/INDEX.md`：确认当前没有可复用的文件导出业务 Knowledge。

## Necessary Evidence

- `input/requirement.md`

## Unknowns

- UNK-001～UNK-007 均未解决，详见 `analysis.md#9-unknowns`。

## Generation Constraints

- 不重新执行完整需求分析。
- 不读取未列出的历史 Change 或 Knowledge。
- 不把文件格式、导出范围、权限、数据量或异步机制补成事实。
- 所有用例只能作为设计级用例，并明确标记受哪些 Unknown 阻塞。
- 每个 P0 Test Focus 必须有用例映射。

