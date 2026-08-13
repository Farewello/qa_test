# QA Knowledge Project

这是一个 Git-native、Agent-neutral 的 QA 知识项目。它复用已有的需求分析 Skill 和测试用例生成 Skill，并补充：

- 最小充分上下文发现；
- 需求分析与用例生成之间的稳定交接；
- 可审计的知识合并；
- Change 状态和结构校验。

## 快速开始

```powershell
python scripts/qa.py doctor
python scripts/qa.py new REQ-102 --title "增加已支付订单取消能力"
python scripts/qa.py status REQ-102
python scripts/qa.py validate --change REQ-102
```

仓库已绑定两个项目内默认 Skill，用于框架验证。真实 Skill 到位后，先将完整 Skill 目录放入项目，例如 `skills/incoming/`，再使用相对路径替换：

```powershell
python scripts/qa.py bind requirement-analysis skills/incoming/requirements-analysis-plus/SKILL.md --replace
python scripts/qa.py bind testcase-generation skills/incoming/testcase-writer-plus/SKILL.md --replace
python scripts/qa.py validate-paths
```

默认 Skill 不代表最终组织级需求分析和测试用例规范。

## 核心边界

- `changes/{REQ}/input/` 保存原始 Evidence。
- `changes/{REQ}/analysis.md` 保存需求分析结果。
- `knowledge/` 只保存有 Evidence、稳定、可复用的系统认知。
- 测试用例、Agent 推测和 Assumption 不能作为系统事实写入 Knowledge。
- `workflow_state=DONE` 仅表示工作流完成；是否可执行测试由 `test_readiness` 判断。

## 已验证示例

`changes/REQ-001/` 使用仅包含“文件导出”的极简需求跑完了整个流程。其最终状态为：

```text
workflow_state = DONE
delivery_status = planned
test_readiness = blocked
```

这表示分析和用例设计已经完成，但规格不足，测试尚不可执行。详细评估见 `changes/REQ-001/evaluation.md`。
