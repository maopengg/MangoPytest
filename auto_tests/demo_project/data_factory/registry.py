# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据构造器注册中心
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Dict, Type

from core.base import BaseBuilder


class BuilderRegistry:
    """
    构造器注册中心
    用于管理和获取各种数据构造器
    """

    _builders: Dict[str, Type[BaseBuilder]] = {}

    @classmethod
    def register(cls, name: str, builder_class: Type[BaseBuilder]):
        """
        注册构造器
        @param name: 构造器名称
        @param builder_class: 构造器类
        """
        cls._builders[name] = builder_class

    @classmethod
    def get(cls, name: str) -> Type[BaseBuilder]:
        """
        获取构造器类
        @param name: 构造器名称
        @return: 构造器类
        """
        if name not in cls._builders:
            raise KeyError(f"构造器 '{name}' 未注册")
        return cls._builders[name]

    @classmethod
    def create(cls, name: str, **kwargs) -> BaseBuilder:
        """
        创建构造器实例
        @param name: 构造器名称
        @param kwargs: 构造器参数
        @return: 构造器实例
        """
        builder_class = cls.get(name)
        return builder_class(**kwargs)

    @classmethod
    def list_builders(cls) -> Dict[str, Type[BaseBuilder]]:
        """列出所有已注册的构造器"""
        return cls._builders.copy()

    @classmethod
    def unregister(cls, name: str):
        """注销构造器"""
        if name in cls._builders:
            del cls._builders[name]


def register_builder(name: str):
    """
    构造器注册装饰器
    用法：
    @register_builder("user")
    class UserBuilder(BaseBuilder):
        ...
    """

    def decorator(builder_class: Type[BaseBuilder]):
        BuilderRegistry.register(name, builder_class)
        return builder_class

    return decorator
