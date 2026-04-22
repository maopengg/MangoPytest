# -*- coding: utf-8 -*-
"""
bdd_api_mock 配置管理

统一管理所有配置，包括：
- API 基础 URL
- 数据库配置
- SQLAlchemy 引擎和会话
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from core.base import BaseConfig


class MockAPISettings(BaseConfig):
    """Mock API 测试配置

    继承自 core.base.BaseConfig，提供项目特定的配置
    """

    # API 基础 URL
    BASE_URL: str = "http://43.142.161.61:8003"

    # 数据库配置
    DB_HOST: str = "43.142.161.61"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "mP123456&"
    DB_NAME: str = "mango_mock"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 SQLAlchemy
        self._init_db()

    def _init_db(self):
        """初始化数据库连接"""
        # 创建引擎
        self.engine = create_engine(
            self.DB_URL,
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=False,
        )

        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # 声明基类
        self.Base = declarative_base()

    def get_db_session(self):
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


# 全局配置实例
settings = MockAPISettings()

# 导出常用对象（保持向后兼容）
engine = settings.engine
SessionLocal = settings.SessionLocal
Base = settings.Base
