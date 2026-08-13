import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "qa.py"
SPEC = importlib.util.spec_from_file_location("qa_cli", MODULE_PATH)
qa = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(qa)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    (tmp_path / "standards" / "templates").mkdir(parents=True)
    (tmp_path / "standards" / "skill-bindings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bindings": {
                    "requirement-analysis": {
                        "status": "unbound",
                        "skill_name": None,
                        "skill_file": None,
                    },
                    "testcase-generation": {
                        "status": "unbound",
                        "skill_name": None,
                        "skill_file": None,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    templates = {
        "context.md": "# Context Discovery\n",
        "testcase-handoff.md": "# Test Case Generation Handoff\n",
        "coverage.md": "# Analysis Coverage\n",
        "knowledge-update.md": "# Knowledge Update\n",
    }
    for name, content in templates.items():
        (tmp_path / "standards" / "templates" / name).write_text(
            content, encoding="utf-8"
        )
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "knowledge" / "INDEX.md").write_text(
        "# Knowledge Index\n", encoding="utf-8"
    )
    return tmp_path


def test_new_change_creates_isolated_workspace(project: Path) -> None:
    change_dir = qa.create_change(project, "REQ-102", "已支付订单取消")

    state = json.loads((change_dir / "state.json").read_text(encoding="utf-8"))
    assert state["requirement_id"] == "REQ-102"
    assert state["title"] == "已支付订单取消"
    assert state["workflow_state"] == "NEW"
    assert state["delivery_status"] == "planned"
    assert state["test_readiness"] == "unknown"
    assert (change_dir / "input").is_dir()
    assert (change_dir / "normalized").is_dir()
    assert (change_dir / "testcases").is_dir()
    assert (change_dir / "context.md").exists()
    assert (change_dir / "testcase-handoff.md").exists()


@pytest.mark.parametrize("requirement_id", ["../oops", "REQ/1", "", "a b"])
def test_new_change_rejects_unsafe_id(project: Path, requirement_id: str) -> None:
    with pytest.raises(ValueError):
        qa.create_change(project, requirement_id, "bad")


def test_bind_project_skill_uses_repo_relative_path_and_creates_adapters(
    project: Path,
) -> None:
    source = project / "source-skill"
    source.mkdir()
    original = "---\nname: existing-cases\ndescription: writes cases\n---\n\n# Body\n"
    (source / "SKILL.md").write_text(original, encoding="utf-8")
    (source / "reference.md").write_text("reference", encoding="utf-8")

    binding = qa.bind_skill(
        project, "testcase-generation", source / "SKILL.md", replace=False
    )

    bound_file = project / binding["skill_file"]
    assert binding["skill_file"] == "source-skill/SKILL.md"
    assert "source_hint" not in binding
    assert bound_file.read_text(encoding="utf-8") == original
    assert binding["status"] == "bound"
    assert binding["skill_name"] == "existing-cases"
    for provider in (".agents", ".claude"):
        adapter = project / provider / "skills" / "existing-cases" / "SKILL.md"
        assert "../../../source-skill/SKILL.md" in adapter.read_text(encoding="utf-8")


def test_bind_external_skill_vendors_without_persisting_absolute_source(
    project: Path,
) -> None:
    source = project.parent / f"{project.name}-external-skill"
    source.mkdir()
    (source / "SKILL.md").write_text(
        "---\nname: external-analysis\ndescription: analyzes requirements\n---\n",
        encoding="utf-8",
    )

    binding = qa.bind_skill(
        project, "requirement-analysis", source / "SKILL.md", replace=False
    )

    assert binding["skill_file"] == "skills/external/requirement-analysis/SKILL.md"
    assert "source_hint" not in binding
    assert not any(qa.WINDOWS_ABSOLUTE_PATH.search(str(value)) for value in binding.values())


def test_bind_skill_rejects_missing_skill(project: Path) -> None:
    with pytest.raises(FileNotFoundError):
        qa.bind_skill(
            project,
            "requirement-analysis",
            project / "missing" / "SKILL.md",
            replace=False,
        )


def test_bind_skill_does_not_commit_binding_when_adapter_creation_fails(
    project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = project / "source-analysis"
    source.mkdir()
    (source / "SKILL.md").write_text(
        "---\nname: analysis-default\ndescription: analysis\n---\n", encoding="utf-8"
    )

    def fail_adapter(*args: object, **kwargs: object) -> None:
        raise PermissionError("adapter denied")

    monkeypatch.setattr(qa, "_write_adapter", fail_adapter)
    with pytest.raises(PermissionError):
        qa.bind_skill(
            project, "requirement-analysis", source / "SKILL.md", replace=False
        )

    data = json.loads(
        (project / "standards" / "skill-bindings.json").read_text(encoding="utf-8")
    )
    assert data["bindings"]["requirement-analysis"]["status"] == "unbound"


def test_validate_change_enforces_artifacts_by_state(project: Path) -> None:
    change_dir = qa.create_change(project, "REQ-103", "状态门禁")
    state_path = change_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["workflow_state"] = "ANALYZED"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    result = qa.validate_change(project, "REQ-103")

    assert any("analysis.md" in error for error in result.errors)


def test_context_ready_does_not_require_analysis_skill_binding(project: Path) -> None:
    change_dir = qa.create_change(project, "REQ-104", "上下文可独立完成")
    state_path = change_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["workflow_state"] = "CONTEXT_READY"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    result = qa.validate_change(project, "REQ-104")

    assert not any("需求分析 Skill 尚未绑定" in error for error in result.errors)
    assert any("context.md 尚未形成有效上下文" in error for error in result.errors)


def test_analyzed_state_rejects_empty_analysis_template(project: Path) -> None:
    change_dir = qa.create_change(project, "REQ-105", "空分析门禁")
    (change_dir / "context.md").write_text(
        "# Context Discovery\n\n| L1 | input/requirement.md | 当前需求 | 文件导出 |\n",
        encoding="utf-8",
    )
    (change_dir / "analysis.md").write_text("# Requirement Analysis\n", encoding="utf-8")
    data = json.loads(
        (project / "standards" / "skill-bindings.json").read_text(encoding="utf-8")
    )
    data["bindings"]["requirement-analysis"].update(
        {"status": "bound", "skill_name": "default", "skill_file": "dummy/SKILL.md"}
    )
    (project / "standards" / "skill-bindings.json").write_text(
        json.dumps(data), encoding="utf-8"
    )
    state = json.loads((change_dir / "state.json").read_text(encoding="utf-8"))
    state["workflow_state"] = "ANALYZED"
    (change_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")

    result = qa.validate_change(project, "REQ-105")

    assert any("analysis.md 缺少可追踪 Test Focus" in error for error in result.errors)


def test_portable_path_validation_rejects_absolute_control_plane_path(
    project: Path,
) -> None:
    (project / "README.md").write_text(
        "bind C:\\Users\\Someone\\skill\\SKILL.md", encoding="utf-8"
    )

    result = qa.validate_portable_paths(project)

    assert any("绝对路径" in error for error in result.errors)


@pytest.mark.parametrize(
    "statuses,expected",
    [
        (["Covered", "Covered"], "ready"),
        (["Covered", "Blocked"], "partial"),
        (["Blocked", "Blocked"], "blocked"),
        ([], "unknown"),
    ],
)
def test_infer_test_readiness(statuses: list[str], expected: str) -> None:
    assert qa.infer_test_readiness(statuses) == expected


def test_validate_knowledge_detects_duplicate_ids_and_missing_evidence(
    project: Path,
) -> None:
    module = project / "knowledge" / "modules" / "order"
    module.mkdir(parents=True)
    (module / "rules.md").write_text(
        """# Rules

### ORD-RULE-001 | one
- Status: active
- Scope: Order
- Fact: one
- Evidence:
  - changes/REQ-404/input/missing.md
- Last verified: 2026-08-13

### ORD-RULE-001 | duplicate
- Status: active
- Scope: Order
- Fact: duplicate
- Evidence:
  - changes/REQ-404/input/missing.md
- Last verified: 2026-08-13
""",
        encoding="utf-8",
    )

    result = qa.validate_knowledge(project)

    assert any("重复 Knowledge ID" in error for error in result.errors)
    assert any("Evidence 路径不存在" in error for error in result.errors)
