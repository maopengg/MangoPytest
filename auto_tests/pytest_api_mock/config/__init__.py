# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Pytest API Mock 配置中心 - 统一配置入口
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
Pytest API Mock 配置中心

使用方式:
    from auto_tests.pytest_api_mock.config import settings

    # 当前环境
    env = settings.ENV

    # API host
    host = settings.BASE_URL

切换环境:
    通过环境变量 ENV 来切换配置:
    set ENV=dev   # 开发环境
    set ENV=test  # 测试环境
    set ENV=pre   # 预发布环境
    set ENV=prod  # 生产环境
"""

import os
from typing import Optional

from .settings import (
    BaseConfig,
    PytestApiMockConfig,
    DevConfig,
    TestConfig,
    PreConfig,
    ProdConfig,
)

# 环境映射
ENV_MAP = {
    "dev": "dev",
    "development": "dev",
    "test": "test",
    "testing": "test",
    "pre": "pre",
    "staging": "pre",
    "prod": "prod",
    "production": "prod",
}


def get_current_env() -> str:
    """
    获取当前环境
    优先从环境变量获取，默认为 test
    """
    env = os.environ.get("ENV", "test").lower()
    return ENV_MAP.get(env, "test")


def load_config(env: Optional[str] = None) -> PytestApiMockConfig:
    """
    加载指定环境配置

    @param env: 环境名称，不传则自动获取
    @return: 当前环境配置对象
    """
    if env:
        os.environ["ENV"] = env

    current_env = get_current_env()

    config_map = {
        "dev": DevConfig,
        "test": TestConfig,
        "pre": PreConfig,
        "prod": ProdConfig,
    }

    config_class = config_map.get(current_env, TestConfig)
    return config_class()


# 全局配置实例（延迟加载）
_settings: Optional[PytestApiMockConfig] = None


def get_settings() -> PytestApiMockConfig:
    """获取全局配置实例"""
    global _settings
    if _settings is None:
        _settings = load_config()
    return _settings


# 对外统一暴露 settings 实例（兼容历史用法）
settings: PytestApiMockConfig = get_settings()

# 兼容旧版导入的别名
load_settings = load_config
get_config = load_config


def sync_host_from_env(env: str) -> str:
    """
    从环境配置同步host
    @param env: 环境名称 (dev/test/pre/prod)
    @return: 对应环境的 BASE_URL
    """
    config = load_config(env)
    return config.BASE_URL

# 便捷导出
__all__ = [
    "settings",
    "get_settings",
    "load_config",
    "load_settings",      # 兼容旧版
    "get_config",         # 兼容旧版
    "sync_host_from_env", # 兼容旧版
    "get_current_env",
    "BaseConfig",
    "PytestApiMockConfig",
    "DevConfig",
    "TestConfig",
    "PreConfig",
    "ProdConfig",
]
