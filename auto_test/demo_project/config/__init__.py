# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 配置中心 - 统一配置入口
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
配置中心

使用方式:
    from auto_test.demo_project.config import settings

    # 获取API host
    api_host = settings.API.host

    # 获取数据库配置
    db_host = settings.DATABASE.host

切换环境:
    通过环境变量 ENV 来切换配置:
    export ENV=dev  # 开发环境
    export ENV=test  # 测试环境
    export ENV=pre  # 预发布环境
    export ENV=prod  # 生产环境
"""

import os
from typing import Optional

from .settings import BaseSettings


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
    优先从环境变量获取，默认为dev
    """
    env = os.environ.get("ENV", "dev").lower()
    return ENV_MAP.get(env, "dev")


def load_settings(env: Optional[str] = None) -> BaseSettings:
    """
    加载指定环境的配置

    @param env: 环境名称，不传则自动获取
    @return: 配置实例
    """
    if env is None:
        env = get_current_env()

    if env == "dev":
        from .dev import settings as dev_settings
        return dev_settings
    elif env == "test":
        from .test import settings as test_settings
        return test_settings
    elif env == "pre":
        from .pre import settings as pre_settings
        return pre_settings
    elif env == "prod":
        from .prod import settings as prod_settings
        return prod_settings
    else:
        # 默认返回开发环境配置
        from .dev import settings as dev_settings
        return dev_settings


# 当前环境配置实例
settings = load_settings()


# 便捷导出
__all__ = [
    "settings",
    "BaseSettings",
    "load_settings",
    "get_current_env",
]
