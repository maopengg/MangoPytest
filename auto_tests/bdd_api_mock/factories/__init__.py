# -*- coding: utf-8 -*-
"""
Factories 数据工厂层 - factory_boy
"""

import factory
from auto_tests.bdd_api_mock.config import SessionLocal


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory 基类"""

    class Meta:
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"
