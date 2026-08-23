from __future__ import annotations

from pathlib import Path

from auto_tests.project_registry import PROJECT_REGISTRY
from core.execution.models import ProjectDescriptor


class ProjectCatalog:
    def __init__(self, repository_root: Path | None = None) -> None:
        self.repository_root = (repository_root or Path(__file__).resolve().parents[2]).resolve()

    def all(self) -> tuple[ProjectDescriptor, ...]:
        return tuple(self._build(key, value) for key, value in PROJECT_REGISTRY.items())

    def enabled(self) -> tuple[ProjectDescriptor, ...]:
        return tuple(item for item in self.all() if item.enabled)

    def get(self, project_id: str, *, require_enabled: bool = True) -> ProjectDescriptor:
        if project_id not in PROJECT_REGISTRY:
            raise ValueError(f"未知项目: {project_id}")
        project = self._build(project_id, PROJECT_REGISTRY[project_id])
        if require_enabled and not project.enabled:
            raise ValueError(f"项目 {project_id} 已禁用: {project.reason}")
        if not project.root.is_dir():
            raise ValueError(f"项目目录不存在: {project.root}")
        return project

    def _build(self, project_id: str, config: dict) -> ProjectDescriptor:
        root = (self.repository_root / "auto_tests" / config["path"]).resolve()
        allowed = (self.repository_root / "auto_tests").resolve()
        if not root.is_relative_to(allowed):
            raise ValueError(f"项目路径越界: {project_id}")
        project_name = config["project_name"]
        project_type = config["type"]
        return ProjectDescriptor(
            id=project_id,
            name=getattr(project_name, "value", str(project_name)),
            kind=getattr(project_type, "name", str(project_type)).lower(),
            root=root,
            enabled=bool(config["enabled"]),
            reason=config.get("reason", ""),
        )
