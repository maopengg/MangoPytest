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

    def environment_profiles(self, project_id: str) -> tuple[dict, ...]:
        """返回注册代码明确允许执行的环境，不根据文件名推断。"""
        project = self.get(project_id, require_enabled=False)
        declared = PROJECT_REGISTRY[project_id].get("environments", {})
        profiles = []
        for environment, metadata in declared.items():
            config_file = metadata["config_file"]
            config_path = (project.root / config_file).resolve()
            if not config_path.is_relative_to(project.root) or not config_path.is_file():
                raise ValueError(f"项目 {project_id} 的环境配置不存在: {config_file}")
            profiles.append({
                "id": environment,
                "label": metadata.get("label", environment),
                "file": config_file,
                "inherits": "",
                "summary": self._safe_env_values(config_path),
            })
        return tuple(profiles)

    @staticmethod
    def _safe_env_values(path: Path) -> dict[str, str]:
        allowed = {"BASE_URL", "BROWSER", "HEADLESS", "LOG_LEVEL", "MOCK_TIMEOUT", "MOCK_RETRY_TIMES"}
        result = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() in allowed:
                result[key.strip()] = value.strip()
        return result

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
