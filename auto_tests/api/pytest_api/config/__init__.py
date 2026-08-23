"""按 ENV 加载 pytest_api 的多环境配置。"""

import json
import os
from typing import Union

from core.base import BaseConfig

from .settings import DevConfig, PreConfig, ProdConfig, PytestApiMockConfig, TestConfig


def _resolve_env() -> str:
    if env := os.getenv("ENV"):
        return env.lower()

    if test_env_json := os.getenv("TEST_ENV"):
        try:
            for item in json.loads(test_env_json):
                if item.get("project") == "pytest_api":
                    return {
                        "DEV": "dev",
                        "TEST": "test",
                        "PRE": "pre",
                        "PROD": "prod",
                    }.get(item.get("test_environment"), "test")
        except (TypeError, ValueError, json.JSONDecodeError):
            pass

    from auto_tests.api.pytest_api import DEFAULT_ENV

    return DEFAULT_ENV.name.lower()


_CONFIG_MAPPING = {
    "dev": DevConfig,
    "test": TestConfig,
    "pre": PreConfig,
    "prod": ProdConfig,
}


def get_config(
    env: str | None = None,
) -> Union[DevConfig, TestConfig, PreConfig, ProdConfig]:
    return _CONFIG_MAPPING.get((env or _resolve_env()).lower(), TestConfig)()


settings = get_config()
engine = settings.engine
SessionLocal = settings.SessionLocal
Base = settings.Base

__all__ = [
    "BaseConfig",
    "PytestApiMockConfig",
    "DevConfig",
    "TestConfig",
    "PreConfig",
    "ProdConfig",
    "get_config",
    "settings",
    "engine",
    "SessionLocal",
    "Base",
]
