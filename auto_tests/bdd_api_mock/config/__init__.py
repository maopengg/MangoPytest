# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: BDD API Mock 配置模块
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
BDD API Mock 配置模块

使用方式:
    from auto_tests.bdd_api_mock.config import get_config, settings
    
    # 获取当前环境配置
    config = get_config()
    print(config.BASE_URL)
    
    # 或者直接使用全局配置实例
    print(settings.BASE_URL)
    
    # 获取数据库会话
    session = config.SessionLocal()
    try:
        # 执行数据库操作
        pass
    finally:
        session.close()

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

from core.base import BaseConfig
from .settings import (
    BddApiMockConfig,
    DevConfig,
    TestConfig,
    PreConfig,
    ProdConfig,
)


def _resolve_env() -> str:
    """环境优先级: ENV 环境变量 > TEST_ENV > DEFAULT_ENV"""
    env = os.getenv("ENV")
    if env:
        return env.lower()
    test_env_json = os.getenv("TEST_ENV")
    if test_env_json:
        try:
            import json
            test_env_list = json.loads(test_env_json)
            for item in test_env_list:
                if item.get("project") == "bdd_api_mock":
                    env_enum = item.get("test_environment")
                    env_map = {"DEV": "dev", "TEST": "test", "PRE": "pre", "PRO": "prod"}
                    env = env_map.get(env_enum, "")
                    if env:
                        return env
        except Exception:
            pass
    from auto_tests.bdd_api_mock import DEFAULT_ENV
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

    config_class = _config_mapping.get(env.lower(), DevConfig)
    return config_class()


# 全局配置实例（根据环境变量或 DEFAULT_ENV 自动加载）
settings = get_config()

# 导出常用对象（保持向后兼容）
engine = settings.engine
SessionLocal = settings.SessionLocal
Base = settings.Base

__all__ = [
    "BaseConfig",  # 从 core.base 导出
    "BddApiMockConfig",  # 基础配置类
    "DevConfig",  # 开发环境配置
    "TestConfig",  # 测试环境配置
    "PreConfig",  # 预发布环境配置
    "ProdConfig",  # 生产环境配置
    "get_config",  # 获取配置函数
    "settings",  # 默认配置实例
    "engine",  # SQLAlchemy 引擎
    "SessionLocal",  # 会话工厂
    "Base",  # 声明基类
]
