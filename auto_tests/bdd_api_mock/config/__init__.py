# -*- coding: utf-8 -*-
"""
bdd_api_mock 配置管理模块

统一管理所有配置，包括 API、数据库、SQLAlchemy 等

使用示例：
    from auto_tests.bdd_api_mock.config import settings

    # 获取配置
    url = settings.BASE_URL
    db_url = settings.DB_URL

    # 获取数据库会话
    session = settings.SessionLocal()
    try:
        # 执行数据库操作
        pass
    finally:
        session.close()
"""

from core.base import BaseConfig
from .settings import MockAPISettings, settings, engine, SessionLocal, Base

__all__ = [
    "BaseConfig",  # 从 core.base 导出
    "MockAPISettings",  # 本项目配置类
    "settings",  # 默认配置实例
    "engine",  # SQLAlchemy 引擎
    "SessionLocal",  # 会话工厂
    "Base",  # 声明基类
]
