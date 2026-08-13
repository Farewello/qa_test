# Knowledge Index

这是 Project Knowledge 的一级 Router。默认只读取本文件，不得递归扫描整个 `knowledge/`。

## System

| Area | Purpose | Read when | Path |
|---|---|---|---|
| System overview | 系统边界和模块导航 | 首次分析项目需求或无法识别模块时 | `system/overview.md` |

## Modules

当前尚未注册真实业务模块。只有获得可靠 Evidence 并形成可复用认知后，才创建模块目录并在这里登记。

## Cross-module Concerns

当前尚未注册跨模块专题。不要为了目录完整创建空文件。

## Routing Rules

1. 从需求中识别 Entity、Action、State、Role 和显式模块。
2. 根据本索引选择模块 `overview.md`。
3. 根据模块入口只读取本次需要的规则、状态、接口、依赖或风险文件。
4. 只有依赖关系被实际触发时才扩展到其他模块。
5. Knowledge 信息不足、冲突或需要兼容性证据时，才回溯历史 Change 或技术方案。

