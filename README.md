# QA Knowledge Project

这是一个 Git-native、Agent-neutral 的 QA 知识项目。它复用已有的需求分析 Skill 和测试用例生成 Skill，并补充：

- 最小充分上下文发现；
- 需求分析与用例生成之间的稳定交接；
- 可审计的知识合并；
- Change 状态和结构校验。

## 快速开始

```powershell
python scripts/qa.py doctor
python scripts/qa.py bind requirement-analysis C:\path\to\requirement-analysis\SKILL.md
python scripts/qa.py bind testcase-generation C:\path\to\testcase-generation\SKILL.md
python scripts/qa.py new REQ-102 --title "增加已支付订单取消能力"
python scripts/qa.py status REQ-102
python scripts/qa.py validate --change REQ-102
```

在两份现有 Skill 尚未绑定前，可以创建 Change，但不能把任务推进到需求分析和用例生成阶段。

## 核心边界

- `changes/{REQ}/input/` 保存原始 Evidence。
- `changes/{REQ}/analysis.md` 保存需求分析结果。
- `knowledge/` 只保存有 Evidence、稳定、可复用的系统认知。
- 测试用例、Agent 推测和 Assumption 不能作为系统事实写入 Knowledge。

