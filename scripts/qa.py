#!/usr/bin/env python3
"""Git-native QA Knowledge Project 的无依赖脚手架和结构校验器。"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Iterable


ROLE_NAMES = ("requirement-analysis", "testcase-generation")
WORKFLOW_STATES = (
    "NEW",
    "NORMALIZED",
    "CONTEXT_READY",
    "ANALYZED",
    "CASES_GENERATED",
    "KNOWLEDGE_UPDATED",
    "DONE",
)
DELIVERY_STATUSES = ("unknown", "planned", "implemented", "released", "cancelled")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
KNOWLEDGE_HEADING = re.compile(
    r"^###\s+([A-Z][A-Z0-9-]+)\s*\|[^\n]*\n(?P<body>.*?)(?=^###\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在：{path}") from None
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 无效：{path}: {exc}") from exc


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def load_bindings(root: Path) -> dict:
    data = read_json(root / "standards" / "skill-bindings.json")
    if data.get("schema_version") != 1 or not isinstance(data.get("bindings"), dict):
        raise ValueError("standards/skill-bindings.json schema 无效")
    return data


def validate_requirement_id(requirement_id: str) -> None:
    if not ID_PATTERN.fullmatch(requirement_id):
        raise ValueError(
            "Requirement ID 只能包含字母、数字、点、下划线和连字符，且长度为 1-64"
        )


def create_change(root: Path, requirement_id: str, title: str) -> Path:
    validate_requirement_id(requirement_id)
    if not title.strip():
        raise ValueError("需求标题不能为空")

    change_dir = root / "changes" / requirement_id
    if change_dir.exists():
        raise FileExistsError(f"Change 已存在：{change_dir}")

    (change_dir / "input").mkdir(parents=True)
    (change_dir / "normalized").mkdir()
    (change_dir / "testcases").mkdir()

    bindings = load_bindings(root)["bindings"]
    today = date.today().isoformat()
    state = {
        "schema_version": 1,
        "requirement_id": requirement_id,
        "title": title.strip(),
        "workflow_state": "NEW",
        "delivery_status": "planned",
        "analysis_skill": bindings["requirement-analysis"].get("skill_name"),
        "testcase_skill": bindings["testcase-generation"].get("skill_name"),
        "created_at": today,
        "updated_at": today,
    }
    write_json(change_dir / "state.json", state)

    (change_dir / "sources.md").write_text(
        "# Sources\n\n"
        "| ID | Path | Type | Purpose | Notes |\n"
        "|---|---|---|---|---|\n",
        encoding="utf-8",
    )

    templates = root / "standards" / "templates"
    shutil.copy2(templates / "context.md", change_dir / "context.md")
    shutil.copy2(
        templates / "testcase-handoff.md", change_dir / "testcase-handoff.md"
    )
    shutil.copy2(templates / "coverage.md", change_dir / "testcases" / "coverage.md")
    shutil.copy2(templates / "knowledge-update.md", change_dir / "knowledge-update.md")

    current = root / "changes" / ".current"
    current.write_text(requirement_id + "\n", encoding="utf-8")
    return change_dir


def parse_skill_name(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    match = re.search(r"(?m)^name:\s*[\"']?([^\"'\r\n]+)[\"']?\s*$", text)
    if not match:
        raise ValueError(f"SKILL.md 缺少 YAML frontmatter name：{skill_file}")
    name = match.group(1).strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        raise ValueError(f"Skill name 无效：{name}")
    return name


def _safe_remove_vendored(destination: Path, external_root: Path) -> None:
    resolved_destination = destination.resolve()
    resolved_root = external_root.resolve()
    if resolved_root not in resolved_destination.parents:
        raise ValueError(f"拒绝删除非 vendored Skill 目录：{destination}")
    shutil.rmtree(destination)


def _write_adapter(root: Path, provider_dir: str, skill_name: str, target: str) -> None:
    adapter = root / provider_dir / "skills" / skill_name / "SKILL.md"
    adapter.parent.mkdir(parents=True, exist_ok=True)
    provider = "Codex" if provider_dir == ".agents" else "Claude Code"
    adapter.write_text(
        "---\n"
        f"name: {skill_name}\n"
        f"description: 项目绑定的现有 QA Skill：{skill_name}。具体触发条件以 canonical SKILL.md 为准。\n"
        "---\n\n"
        f"完整读取并执行项目根目录下的 `{target}`。"
        f"该文件是 vendored 原始 Skill，本文件仅用于 {provider} 项目级发现。\n",
        encoding="utf-8",
    )


def bind_skill(
    root: Path, role: str, skill_file: Path, *, replace: bool = False
) -> dict:
    if role not in ROLE_NAMES:
        raise ValueError(f"未知 Skill role：{role}")
    skill_file = skill_file.resolve()
    if not skill_file.is_file():
        raise FileNotFoundError(f"Skill 文件不存在或链接失效：{skill_file}")
    if skill_file.name.lower() != "skill.md":
        raise ValueError("绑定路径必须指向 SKILL.md")

    skill_name = parse_skill_name(skill_file)
    external_root = root / "skills" / "external"
    destination = external_root / role
    if destination.exists():
        if not replace:
            raise FileExistsError(
                f"角色 {role} 已有 vendored Skill；如需替换请显式使用 --replace"
            )
        _safe_remove_vendored(destination, external_root)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skill_file.parent, destination)
    vendored_file = destination / "SKILL.md"
    relative = vendored_file.relative_to(root).as_posix()

    data = load_bindings(root)
    binding = data["bindings"][role]
    binding.update(
        {
            "status": "bound",
            "skill_name": skill_name,
            "skill_file": relative,
            "source_hint": str(skill_file),
        }
    )
    write_json(root / "standards" / "skill-bindings.json", data)
    _write_adapter(root, ".agents", skill_name, relative)
    _write_adapter(root, ".claude", skill_name, relative)
    return binding


def change_state(root: Path, requirement_id: str) -> tuple[Path, dict]:
    validate_requirement_id(requirement_id)
    change_dir = root / "changes" / requirement_id
    return change_dir, read_json(change_dir / "state.json")


def transition_change(
    root: Path,
    requirement_id: str,
    workflow_state: str,
    delivery_status: str | None = None,
) -> dict:
    if workflow_state not in WORKFLOW_STATES:
        raise ValueError(f"无效 workflow state：{workflow_state}")
    if delivery_status is not None and delivery_status not in DELIVERY_STATUSES:
        raise ValueError(f"无效 delivery status：{delivery_status}")

    change_dir, state = change_state(root, requirement_id)
    current_index = WORKFLOW_STATES.index(state["workflow_state"])
    next_index = WORKFLOW_STATES.index(workflow_state)
    if next_index > current_index + 1:
        raise ValueError("不能跳过工作流阶段")
    if next_index < current_index:
        raise ValueError("不能通过 transition 回退阶段；请修复产物后保留审计记录")

    validation = validate_change(root, requirement_id, target_state=workflow_state)
    if not validation.ok:
        raise ValueError("目标阶段门禁失败：" + "；".join(validation.errors))

    state["workflow_state"] = workflow_state
    if delivery_status is not None:
        state["delivery_status"] = delivery_status
    state["updated_at"] = date.today().isoformat()
    write_json(change_dir / "state.json", state)
    return state


def _require_file(result: ValidationResult, path: Path, label: str) -> None:
    if not path.is_file():
        result.errors.append(f"缺少 {label}：{path}")


def validate_change(
    root: Path, requirement_id: str, *, target_state: str | None = None
) -> ValidationResult:
    result = ValidationResult()
    try:
        change_dir, state = change_state(root, requirement_id)
    except (FileNotFoundError, ValueError) as exc:
        result.errors.append(str(exc))
        return result

    state_name = target_state or state.get("workflow_state")
    if state_name not in WORKFLOW_STATES:
        result.errors.append(f"未知 workflow_state：{state_name}")
        return result
    if state.get("delivery_status") not in DELIVERY_STATUSES:
        result.errors.append(f"未知 delivery_status：{state.get('delivery_status')}")

    level = WORKFLOW_STATES.index(state_name)
    _require_file(result, change_dir / "state.json", "state.json")
    _require_file(result, change_dir / "sources.md", "sources.md")
    if level >= WORKFLOW_STATES.index("CONTEXT_READY"):
        _require_file(result, change_dir / "context.md", "context.md")
    if level >= WORKFLOW_STATES.index("ANALYZED"):
        bindings = load_bindings(root)["bindings"]
        if bindings["requirement-analysis"].get("status") != "bound":
            result.errors.append("需求分析 Skill 尚未绑定")
        _require_file(result, change_dir / "analysis.md", "analysis.md")
    if level >= WORKFLOW_STATES.index("CASES_GENERATED"):
        bindings = load_bindings(root)["bindings"]
        if bindings["testcase-generation"].get("status") != "bound":
            result.errors.append("用例生成 Skill 尚未绑定")
        _require_file(result, change_dir / "testcase-handoff.md", "testcase-handoff.md")
        _require_file(result, change_dir / "testcases" / "coverage.md", "coverage.md")
        case_files = [
            path
            for path in (change_dir / "testcases").glob("*")
            if path.is_file() and path.name != "coverage.md"
        ]
        if not case_files:
            result.errors.append("testcases/ 中没有现有用例生成 Skill 的输出")
    if level >= WORKFLOW_STATES.index("KNOWLEDGE_UPDATED"):
        _require_file(result, change_dir / "knowledge-update.md", "knowledge-update.md")
        result.merge(validate_knowledge(root))
    return result


def _extract_evidence_paths(body: str) -> Iterable[str]:
    evidence = re.search(
        r"(?m)^- Evidence:\s*$\n(?P<items>(?:\s{2,}-\s+.*(?:\n|$))+)", body
    )
    if not evidence:
        return []
    paths = []
    for line in evidence.group("items").splitlines():
        value = re.sub(r"^\s*-\s+", "", line).strip().strip("`")
        if value:
            paths.append(value)
    return paths


def validate_knowledge(root: Path) -> ValidationResult:
    result = ValidationResult()
    knowledge_root = root / "knowledge"
    if not (knowledge_root / "INDEX.md").is_file():
        result.errors.append("缺少 knowledge/INDEX.md")
        return result

    seen: dict[str, Path] = {}
    required_fields = ("Status", "Scope", "Fact", "Evidence", "Last verified")
    for path in knowledge_root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in KNOWLEDGE_HEADING.finditer(text):
            knowledge_id = match.group(1)
            body = match.group("body")
            if knowledge_id in seen:
                result.errors.append(
                    f"重复 Knowledge ID {knowledge_id}：{seen[knowledge_id]} 和 {path}"
                )
            else:
                seen[knowledge_id] = path
            for field in required_fields:
                if not re.search(rf"(?m)^- {re.escape(field)}:\s*\S*", body):
                    result.errors.append(f"{knowledge_id} 缺少字段 {field}：{path}")
            for evidence_path in _extract_evidence_paths(body):
                local_path = evidence_path.split("#", 1)[0].strip()
                if not local_path:
                    continue
                if re.match(r"^[a-z]+://", local_path, re.IGNORECASE):
                    result.warnings.append(
                        f"{knowledge_id} 使用外部 Evidence，无法离线校验：{local_path}"
                    )
                elif not (root / Path(local_path)).exists():
                    result.errors.append(
                        f"{knowledge_id} Evidence 路径不存在：{local_path}"
                    )
    return result


def validate_adapters(root: Path) -> ValidationResult:
    result = ValidationResult()
    canonical = {
        "context-discovery": "skills/context-discovery/SKILL.md",
        "knowledge-update": "skills/knowledge-update/SKILL.md",
    }
    for name, target in canonical.items():
        if not (root / target).is_file():
            result.errors.append(f"缺少 canonical Skill：{target}")
        for provider in (".agents", ".claude"):
            adapter = root / provider / "skills" / name / "SKILL.md"
            if not adapter.is_file():
                result.errors.append(f"缺少 {provider} adapter：{adapter}")
            elif target not in adapter.read_text(encoding="utf-8"):
                result.errors.append(f"Adapter 未指向 canonical Skill：{adapter}")

    try:
        bindings = load_bindings(root)["bindings"]
    except (FileNotFoundError, ValueError) as exc:
        result.errors.append(str(exc))
        return result
    for role in ROLE_NAMES:
        binding = bindings.get(role)
        if not isinstance(binding, dict):
            result.errors.append(f"缺少 Skill binding：{role}")
            continue
        if binding.get("status") == "bound":
            skill_file = binding.get("skill_file")
            skill_name = binding.get("skill_name")
            if not skill_file or not (root / skill_file).is_file():
                result.errors.append(f"绑定的 Skill 文件不存在：{role}: {skill_file}")
            for provider in (".agents", ".claude"):
                adapter = root / provider / "skills" / str(skill_name) / "SKILL.md"
                if not adapter.is_file():
                    result.errors.append(f"绑定 Skill 缺少 {provider} adapter：{adapter}")
        else:
            result.warnings.append(f"{role} 尚未绑定")
    return result


def print_result(result: ValidationResult) -> int:
    for warning in result.warnings:
        print(f"WARN: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print("OK")
        return 0
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="创建独立 Change workspace")
    new.add_argument("requirement_id")
    new.add_argument("--title", required=True)

    bind = sub.add_parser("bind", help="将现有 Skill vendoring 并绑定到标准角色")
    bind.add_argument("role", choices=ROLE_NAMES)
    bind.add_argument("skill_file", type=Path)
    bind.add_argument("--replace", action="store_true")

    status = sub.add_parser("status", help="查看 Change 状态")
    status.add_argument("requirement_id")

    transition = sub.add_parser("transition", help="通过门禁后推进 Change 状态")
    transition.add_argument("requirement_id")
    transition.add_argument("workflow_state", choices=WORKFLOW_STATES)
    transition.add_argument("--delivery-status", choices=DELIVERY_STATUSES)

    validate = sub.add_parser("validate", help="校验项目或指定 Change")
    validate.add_argument("--change")

    sub.add_parser("validate-knowledge", help="校验 Knowledge ID、字段和 Evidence")
    sub.add_parser("validate-adapters", help="校验 canonical Skill、绑定和适配层")
    sub.add_parser("doctor", help="检查框架、Skill 绑定和 Knowledge")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = project_root()
    try:
        if args.command == "new":
            path = create_change(root, args.requirement_id, args.title)
            print(path)
            return 0
        if args.command == "bind":
            binding = bind_skill(root, args.role, args.skill_file, replace=args.replace)
            print(json.dumps(binding, ensure_ascii=False, indent=2))
            return 0
        if args.command == "status":
            _, state = change_state(root, args.requirement_id)
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        if args.command == "transition":
            state = transition_change(
                root,
                args.requirement_id,
                args.workflow_state,
                args.delivery_status,
            )
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        if args.command == "validate-knowledge":
            return print_result(validate_knowledge(root))
        if args.command == "validate-adapters":
            return print_result(validate_adapters(root))
        if args.command == "validate":
            result = ValidationResult()
            result.merge(validate_adapters(root))
            result.merge(validate_knowledge(root))
            if args.change:
                result.merge(validate_change(root, args.change))
            return print_result(result)
        if args.command == "doctor":
            result = ValidationResult()
            result.merge(validate_adapters(root))
            result.merge(validate_knowledge(root))
            return print_result(result)
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
