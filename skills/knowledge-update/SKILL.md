---
name: knowledge-update
description: 在需求分析和测试用例完成后，将有 Evidence、稳定且可复用的项目认知合并到 knowledge/，并记录 CREATE、UPDATE、DEPRECATE 或 SKIP 决策。任务收尾、规则变更或知识沉淀时使用。
---

# Knowledge Update

读取当前 `analysis.md`、其中登记的 Evidence 和 `knowledge/INDEX.md`，对 `knowledge/` 执行最小必要修改，并输出 `changes/{CHANGE-ID}/update.md`。

## 写入资格

候选认知必须同时满足：

- 项目特定且对未来 QA 工作可复用；
- Scope 明确；
- 有可定位 Evidence；
- 不是推测、Unknown、Assumption、临时数据或测试用例。

## 合并规则

- `CREATE`：新增合格认知。
- `UPDATE`：修改同一认知的事实、条件、效果或 Evidence。
- `DEPRECATE`：旧认知已失效或被替代。
- `SKIP`：重复、证据不足、一次性信息或冲突无法裁决。

不得保留相互冲突的 active Knowledge。只在新增路由时更新 `knowledge/INDEX.md`，不要创建空模块。

## 更新记录

`update.md` 记录汇总、每项决策、目标文件、Evidence、结果或跳过原因，以及索引是否变化。测试用例不能作为系统事实的 Evidence。
