# Changes

每个需求使用独立目录 `changes/{requirement-id}/`。

使用以下命令创建工作区：

```powershell
python scripts/qa.py new REQ-102 --title "需求标题"
```

不要手工复制其他 Change 作为模板，避免携带旧 Evidence、Unknown 或状态。

