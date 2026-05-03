# -*- coding: utf-8 -*-
"""
Factories 数据工厂层 - pytest-factoryboy

只保留 BaseFactory 基类，具体的 Spec 定义已移到 specs/ 目录
BaseFactory 延迟获取数据库会话，不依赖具体项目配置
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    """Factory 基类 - SQLAlchemy 版本，自动保存到数据库"""

    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """延迟获取数据库会话，避免模块级别依赖项目配置"""
        from factory.alchemy import SQLAlchemyOptions
        if cls._meta.sqlalchemy_session is None:
            from auto_tests.bdd_api_mock.config import settings
            cls._meta.sqlalchemy_session = settings.SessionLocal()
        return super()._create(model_class, *args, **kwargs)
