# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 配置中心 - 统一配置入口
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
配置中心

使用方式:
    from auto_tests.pytest_api_mock.config import settings

    # 当前环境
    env = settings.ENV.value

    # API host
    host = settings.HOST

切换环境:
    通过环境变量 ENV 来切换配置:
    set ENV=dev   # 开发环境
    set ENV=test  # 测试环境
    set ENV=pre   # 预发布环境
    set ENV=prod  # 生产环境
"""

import os
from typing import Optional

from .settings import BaseConfig, Settings, settings as global_settings

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


def load_settings(env: Optional[str] = None) -> BaseConfig:
    """
    加载指定环境配置

    @param env: 环境名称，不传则自动获取
    @return: 当前环境配置对象
    """
    if env:
        os.environ["ENV"] = env
        global_settings.reload()
    return global_settings.config


# 对外统一暴露 Settings 实例（兼容历史用法）
settings: Settings = global_settings

# 便捷导出
__all__ = [
    "settings",
    "Settings",
    "BaseConfig",
    "load_settings",
    "get_current_env",
]
