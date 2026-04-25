# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API Mock 配置模块
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
API Mock 配置模块

使用方式:
    from auto_tests.api_mock.config import get_config, settings
    
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


def _get_default_env() -> str:
    """
    获取默认环境
    
    从 project_config.py 读取 MOCK_API 项目的环境配置
    如果失败则返回空字符串
    """
    try:
        from auto_tests.project_config import get_project_environment, ProjectEnum
        from core.enums.tools_enum import EnvironmentEnum
        
        env_enum = get_project_environment(ProjectEnum.MOCK_API)
        env_map = {
            EnvironmentEnum.DEV: 'dev',
            EnvironmentEnum.TEST: 'test',
            EnvironmentEnum.PRE: 'pre',
            EnvironmentEnum.PRO: 'prod',
        }
        return env_map.get(env_enum, '')
    except Exception:
        return ''


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
        env: 环境名称 (dev/test/pre/prod)，如果为None则从环境变量或 project_config.py 读取
        
    Returns:
        对应环境的配置实例
        
    Raises:
        ValueError: 如果环境未设置且无法从 project_config.py 读取
        
    Example:
        >>> config = get_config("dev")
        >>> print(config.BASE_URL)
        http://localhost:8003
    """
    if env is None:
        # 优先从环境变量读取
        env = os.getenv("ENV")
        if not env:
            # 尝试从 project_config.py 读取
            env = _get_default_env()
            if not env:
                raise ValueError(
                    "未设置测试环境。请通过以下方式之一设置：\n"
                    "1. 设置环境变量：export ENV=dev 或 set ENV=dev\n"
                    "2. 在 project_config.py 中配置 PROJECT_ENVIRONMENT"
                )
    
    config_class = _config_mapping.get(env.lower(), DevConfig)
    return config_class()


# 全局配置实例（根据环境变量或 project_config.py 自动加载）
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
