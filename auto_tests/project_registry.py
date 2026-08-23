"""自动化 Demo 的唯一项目注册表。"""

from __future__ import annotations

from core.enums import BaseEnum
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum


class ProjectEnum(BaseEnum):
    """外部平台使用的项目名称。"""

    SIMPLE_API = "MockAPI服务"
    BDD_API = "bdd_api"
    PYTEST_API = "pytest_api"
    SIMPLE_UI = "MockUI服务"
    BDD_UI = "bdd_ui"
    PYTEST_UI = "pytest_ui"
    SQL = "sql"


PROJECT_REGISTRY = {
    "simple_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.SIMPLE_API, "path": "api/simple_api", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "bdd_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.BDD_API, "path": "api/bdd_api", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "pytest_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.PYTEST_API, "path": "api/pytest_api", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "simple_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.SIMPLE_UI, "path": "ui/simple_ui", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "bdd_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.BDD_UI, "path": "ui/bdd_ui", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "pytest_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.PYTEST_UI, "path": "ui/pytest_ui", "enabled": True, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "sql": {
        "type": AutoTestTypeEnum.OTHER,
        "project_name": ProjectEnum.SQL,
        "path": "other/sql",
        "enabled": False,
        "environments": {},
        "reason": "尚未提供可收集的 pytest 用例",
    },
}

PROJECT_ENVIRONMENT = {
    config["project_name"]: EnvironmentEnum.TEST
    for config in PROJECT_REGISTRY.values()
}

# 兼容平台侧仍使用的列表结构；未就绪项目不进入可执行列表。
auto_test_project_config = [
    {"type": config["type"], "project_name": config["project_name"], "dir_name": config["path"]}
    for config in PROJECT_REGISTRY.values()
    if config["enabled"]
]


def enabled_projects() -> tuple[str, ...]:
    return tuple(name for name, config in PROJECT_REGISTRY.items() if config["enabled"])


def get_project_environment(project_name: ProjectEnum | str) -> EnvironmentEnum:
    """返回项目环境；所有未显式配置的项目默认使用 TEST。"""

    return PROJECT_ENVIRONMENT.get(project_name, EnvironmentEnum.TEST)


def set_os_environment(project_name: ProjectEnum | str) -> None:
    """将注册表中的安全默认环境写入 ``ENV``。"""

    import os

    os.environ["ENV"] = get_project_environment(project_name).name.lower()
