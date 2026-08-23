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
        """从项目现有 ``config/.env.*`` 发现可选运行配置。"""
        project = self.get(project_id, require_enabled=False)
        config_dir = project.root / "config"
        labels = {"dev": "开发环境", "test": "测试环境", "pre": "预发布环境", "prod": "生产环境"}
        order = {"dev": 0, "test": 1, "pre": 2, "prod": 3}
        raw_profiles = {
            path.name.removeprefix(".env."): self._safe_env_values(path)
            for path in config_dir.glob(".env.*") if path.is_file()
        }
        profiles = []
        for environment, values in raw_profiles.items():
            inherited_from = ""
            effective = values.copy()
            if environment in {"test", "pre"} and not effective and "prod" in raw_profiles:
                effective = raw_profiles["prod"].copy()
                inherited_from = "prod"
            profiles.append({
                "id": environment,
                "label": labels.get(environment, environment),
                "file": f"config/.env.{environment}",
                "inherits": inherited_from,
                "summary": effective,
            })
        return tuple(sorted(profiles, key=lambda item: (order.get(item["id"], 99), item["id"])))

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
