# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 百度 UI 测试配置模块
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
百度 UI 测试配置模块

使用方式:
    from auto_tests.ui_baidu.config import get_config, settings
    
    # 获取当前环境配置
    config = get_config()
    print(config.BASE_URL)
    
    # 或者直接使用全局配置实例
    print(settings.BASE_URL)
"""

import os
from typing import Union

from .settings import BaiduUIConfig, DevConfig, TestConfig, PreConfig, ProdConfig


def _get_default_env() -> str:
    """
    获取默认环境
    
    优先从 project_config.py 读取 BAIDU 项目的环境配置
    如果失败则使用 'dev' 作为默认值
    """
    try:
        from auto_tests.project_config import get_project_environment, ProjectEnum
        from core.enums.tools_enum import EnvironmentEnum
        
        env_enum = get_project_environment(ProjectEnum.BAIDU)
        env_map = {
            EnvironmentEnum.DEV: 'dev',
            EnvironmentEnum.TEST: 'test',
            EnvironmentEnum.PRE: 'pre',
            EnvironmentEnum.PRO: 'prod',
        }
        return env_map.get(env_enum, 'dev')
    except Exception:
        return 'dev'


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
    """
    if env is None:
        # 优先从环境变量读取，如果没有则从 project_config.py 读取
        env = os.getenv("ENV") or _get_default_env()
    
    config_class = _config_mapping.get(env.lower(), DevConfig)
    return config_class()


# 全局配置实例（根据环境变量或 project_config.py 自动加载）
settings = get_config()

__all__ = [
    "BaiduUIConfig",
    "DevConfig",
    "TestConfig", 
    "PreConfig",
    "ProdConfig",
    "get_config",
    "settings",
]
