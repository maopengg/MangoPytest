# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API Mock 配置模块
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
API Mock 配置模块

使用方式:
    from auto_tests.api.simple_api.config import get_config, settings
    
    # 获取当前环境配置
    config = get_config()
    print(config.BASE_URL)
    
    # 或者直接使用全局配置实例
    print(settings.BASE_URL)

环境变量设置:
    通过设置 ENV 环境变量来切换环境:
    - dev: 开发环境
    - test: 测试环境
    - pre: 预发布环境
    - prod: 生产环境

    示例:
        export ENV=dev  # Linux/Mac
        set ENV=dev     # Windows
"""

import os
from typing import Union

from .settings import ApiMockConfig, DevConfig, TestConfig, PreConfig, ProdConfig


def _resolve_env() -> str:
    """环境优先级: ENV 环境变量 > DEFAULT_ENV"""
    env = os.getenv("ENV")
    if env:
        return env.lower()
    from auto_tests.api.simple_api import DEFAULT_ENV
    return DEFAULT_ENV.name.lower()


# 配置类映射
_config_mapping = {
    "dev": DevConfig,
    "test": TestConfig,
    "pre": PreConfig,
    "prod": ProdConfig,
}


def get_config(env: str = None) -> Union[DevConfig, TestConfig, PreConfig, ProdConfig]:
    """
    根据环境获取对应的配置实例
    
    Args:
        env: 环境名称 (dev/test/pre/prod)，如果为None则从环境变量或 DEFAULT_ENV 读取

    Returns:
        对应环境的配置实例
        
    Example:
        >>> config = get_config("dev")
        >>> print(config.BASE_URL)
        http://localhost:8003
    """
    if env is None:
        env = _resolve_env()

    config_class = _config_mapping.get(env.lower(), TestConfig)
    return config_class()


# 全局配置实例（根据环境变量或 DEFAULT_ENV 自动加载）
settings = get_config()

__all__ = [
    "ApiMockConfig",
    "DevConfig",
    "TestConfig", 
    "PreConfig",
    "ProdConfig",
    "get_config",
    "settings",
]
