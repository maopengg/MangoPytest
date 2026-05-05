# -*- coding: utf-8 -*-
"""
Factories 数据工厂层 - pytest-factoryboy

只保留 BaseFactory 基类，具体的 Spec 定义已移到 specs/ 目录
BaseFactory 延迟获取数据库会话，不依赖具体项目配置
"""

import importlib

import factory
from factory.alchemy import SQLAlchemyModelFactory


def _find_settings_module(cls) -> str | None:
    """
    自动查找子类的 config 模块路径。

    从子类所在包开始，逐级向上查找，返回第一个存在 config 子模块的路径。
    例如类在 auto_tests.foo.data_factory.specs.x.y.ZSpec：
      1) auto_tests.foo.data_factory.specs.x.y.config
      2) auto_tests.foo.data_factory.specs.x.config
      3) auto_tests.foo.data_factory.specs.config
      4) auto_tests.foo.data_factory.config
      5) auto_tests.foo.config
      ...
    """
    parts = cls.__module__.split(".")
    # 从最深层开始逐级向上查找
    for i in range(len(parts) - 1, 0, -1):
        candidate = ".".join(parts[:i]) + ".config"
        try:
            importlib.import_module(candidate)
            return candidate
        except ImportError:
            continue
    return None


class BaseFactory(SQLAlchemyModelFactory):
    """Factory 基类 - SQLAlchemy 版本，自动保存到数据库"""

    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """延迟获取数据库会话"""
        if cls._meta.sqlalchemy_session is None:
            # 1. 优先用子类显式指定的 _settings_module
            settings_module = getattr(cls, '_settings_module', None)
            # 2. 未指定则自动查找
            if settings_module is None:
                settings_module = _find_settings_module(cls)
            if settings_module is None:
                raise RuntimeError(
                    f"{cls.__name__} 未定义 _settings_module 且无法自动发现 config 模块，"
                    f"请在类中添加: _settings_module = 'your.project.config'"
                )

            settings = importlib.import_module(settings_module)
            cls._meta.sqlalchemy_session = settings.SessionLocal()

        return super()._create(model_class, *args, **kwargs)
