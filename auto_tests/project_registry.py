"""自动化 Demo 的唯一项目注册表。"""

from __future__ import annotations

from core.enums import BaseEnum
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum
from core.settings import settings as system_settings


class ProjectEnum(BaseEnum):
    """外部平台使用的项目名称。"""

    SIMPLE_API = "MockAPI服务"
    BDD_API = "bdd_api"
    PYTEST_API = "pytest_api"
    SIMPLE_UI = "MockUI服务"
    BDD_UI = "bdd_ui"
    PYTEST_UI = "pytest_ui"
    SQL = "sql"


API_RUNTIME_OPTIONS = (
    {"key": "BASE_URL", "label": "API 服务地址", "type": "url", "placeholder": "http://host:port"},
    {"key": "MOCK_TIMEOUT", "label": "请求超时（秒）", "type": "integer", "default": "30", "min": 1, "max": 300},
)

UI_RUNTIME_OPTIONS = (
    {"key": "BASE_URL", "label": "测试页面地址", "type": "url", "placeholder": "http://host:port"},
    {"key": "ELEMENT_SOURCE", "label": "元素数据源", "type": "select", "default": "excel", "choices": ["excel", "feishu"]},
    {"key": "BROWSER", "label": "浏览器类型", "type": "select", "default": "chromium", "choices": ["chromium", "edge", "firefox", "webkit"]},
    {"key": "BROWSER_PATH", "label": "浏览器可执行文件路径", "type": "text", "default": "", "placeholder": "留空则自动查找或使用 Playwright 浏览器"},
    {"key": "HEADLESS", "label": "无头模式", "type": "boolean", "default": "true"},
    {"key": "IMPLICIT_WAIT", "label": "操作超时（秒）", "type": "integer", "default": "10", "min": 1, "max": 300},
    {"key": "TRACE_ENABLED", "label": "记录 Playwright Trace", "type": "boolean", "default": "true"},
    {"key": "ELEMENT_HEALING_ENABLED", "label": "启用元素自愈", "type": "boolean", "default": str(system_settings.ELEMENT_HEALING_ENABLED).lower()},
    {"key": "ELEMENT_HEALING_MODE", "label": "元素自愈模式", "type": "select", "default": str(system_settings.ELEMENT_HEALING_MODE), "choices": ["1", "2", "3"]},
    {"key": "AI_ELEMENT_HEALING_ENABLED", "label": "启用 AI 元素修复", "type": "boolean", "default": str(system_settings.AI_ELEMENT_HEALING_ENABLED).lower()},
    {"key": "AI_API_KEY", "label": "AI API Key", "type": "text", "default": system_settings.AI_API_KEY},
    {"key": "AI_BASE_URL", "label": "AI 服务地址", "type": "url", "default": system_settings.AI_BASE_URL},
    {"key": "AI_MODEL", "label": "AI 模型", "type": "text", "default": system_settings.AI_MODEL},
    {"key": "AI_TIMEOUT", "label": "AI 请求超时（秒）", "type": "integer", "default": str(system_settings.AI_TIMEOUT), "min": 1, "max": 300},
    {"key": "AI_SEMANTIC_STRENGTH", "label": "AI 语义定位强度", "type": "integer", "default": str(system_settings.AI_SEMANTIC_STRENGTH), "min": 0, "max": 100},
)
SIMPLE_UI_RUNTIME_OPTIONS = tuple(
    option for option in UI_RUNTIME_OPTIONS if option["key"] != "TRACE_ENABLED"
)


PROJECT_REGISTRY = {
    "simple_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.SIMPLE_API, "path": "api/simple_api", "enabled": True, "runtime_options": API_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "bdd_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.BDD_API, "path": "api/bdd_api", "enabled": True, "runtime_options": API_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "pytest_api": {"type": AutoTestTypeEnum.API, "project_name": ProjectEnum.PYTEST_API, "path": "api/pytest_api", "enabled": True, "runtime_options": API_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "simple_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.SIMPLE_UI, "path": "ui/simple_ui", "enabled": True, "runtime_options": SIMPLE_UI_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "bdd_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.BDD_UI, "path": "ui/bdd_ui", "enabled": True, "runtime_options": UI_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
    "pytest_ui": {"type": AutoTestTypeEnum.UI, "project_name": ProjectEnum.PYTEST_UI, "path": "ui/pytest_ui", "enabled": True, "runtime_options": UI_RUNTIME_OPTIONS, "environments": {"test": {"label": "Mango Mock 测试环境", "config_file": "config/.env.test"}}},
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
