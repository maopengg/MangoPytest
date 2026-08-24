from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit

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
                "runtime_options": self._runtime_options(project_id, config_path),
            })
        return tuple(profiles)

    def environment_ids(self, project_id: str) -> tuple[str, ...]:
        """返回项目注册表明确声明的可执行环境。"""

        return tuple(profile["id"] for profile in self.environment_profiles(project_id))

    def validate_runtime_overrides(self, project_id: str, values: dict[str, str]) -> dict[str, str]:
        """Validate and normalize only options explicitly declared by the project."""
        declared = {
            option["key"]: option
            for option in PROJECT_REGISTRY[project_id].get("runtime_options", ())
        }
        unknown = set(values) - set(declared)
        if unknown:
            raise ValueError(f"项目 {project_id} 不允许临时覆盖配置: {', '.join(sorted(unknown))}")
        normalized = {}
        for key, raw_value in values.items():
            if len(raw_value) > 2000 or "\x00" in raw_value:
                raise ValueError(f"配置 {key} 内容不合法")
            option, value = declared[key], raw_value.strip()
            field_type = option["type"]
            if field_type == "url":
                parsed = urlsplit(value)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"配置 {key} 必须是 http/https 地址")
            elif field_type == "integer":
                try:
                    number = int(value)
                except ValueError as exc:
                    raise ValueError(f"配置 {key} 必须是整数") from exc
                if not option.get("min", number) <= number <= option.get("max", number):
                    raise ValueError(f"配置 {key} 超出允许范围")
                value = str(number)
            elif field_type == "boolean":
                if value.lower() not in {"true", "false"}:
                    raise ValueError(f"配置 {key} 必须是 true 或 false")
                value = value.lower()
            elif field_type == "select":
                if value not in option["choices"]:
                    raise ValueError(f"配置 {key} 不在允许选项中")
            normalized[key] = value
        return normalized

    def _runtime_options(self, project_id: str, config_path: Path) -> list[dict]:
        configured = self._safe_env_values(config_path)
        return [
            {**option, "value": configured.get(option["key"], option.get("default", ""))}
            for option in PROJECT_REGISTRY[project_id].get("runtime_options", ())
        ]

    @staticmethod
    def _safe_env_values(path: Path) -> dict[str, str]:
        allowed = {
            "BASE_URL", "BROWSER", "BROWSER_PATH", "HEADLESS", "IMPLICIT_WAIT",
            "TRACE_ENABLED", "LOG_LEVEL", "MOCK_TIMEOUT", "MOCK_RETRY_TIMES",
        }
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
