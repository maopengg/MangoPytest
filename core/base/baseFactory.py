# -*- coding: utf-8 -*-
"""
Factories 数据工厂层 - pytest-factoryboy

只保留 BaseFactory 基类，具体的 Spec 定义已移到 specs/ 目录
"""

import factory
from factory.alchemy import SQLAlchemyModelFactory

from auto_tests.bdd_api_mock.config import settings


class BaseFactory(SQLAlchemyModelFactory):
    """Factory 基类 - SQLAlchemy 版本，自动保存到数据库"""

    class Meta:
        abstract = True
        sqlalchemy_session = settings.SessionLocal()
        sqlalchemy_session_persistence = "commit"
