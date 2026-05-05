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
        """延迟获取数据库会话，从子类 _settings_module 读取配置"""
        if cls._meta.sqlalchemy_session is None:
            # 获取子类定义的 settings 模块路径
            settings_module = getattr(cls, '_settings_module', None)
            if settings_module is None:
                raise RuntimeError(
                    f"{cls.__name__} 未定义 _settings_module，"
                    f"请在类中添加: _settings_module = 'your.project.config'"
                )
            
            # 动态导入 settings 模块
            import importlib
            settings = importlib.import_module(settings_module)
            cls._meta.sqlalchemy_session = settings.SessionLocal()
        
        return super()._create(model_class, *args, **kwargs)
