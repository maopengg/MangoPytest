# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 枚举模块 - 包含所有项目枚举定义
# @Time   : 2023-08-07 11:11
# @Author : 毛鹏
from enum import Enum


class BaseEnum(Enum):
    """基础枚举类，提供通用的三个方法"""

    @classmethod
    def get_option(cls):
        return [{'key': key, 'title': value} for key, value in cls.obj().items()]

    @classmethod
    def get_value(cls, key: int):
        return cls.obj().get(key)

    @classmethod
    def get_key(cls, value):
        all_values = cls.obj().values()

        # 判断目标值是否存在于字典的值列表中
        if value in all_values:
            # 如果存在，则使用keys()函数获取该值对应的键列表
            keys_with_target_value = [k for k, v in cls.obj().items() if v == value]

            for key in keys_with_target_value:
                return key

    @classmethod
    def reversal_obj(cls):
        return {v: k for k, v in cls.obj().items()}


# 导出 demo_project 专用枚举（方便使用方导入）
from core.enums.demo_enum import (
    # 配置相关
    CreateStrategy,
    Environment,
    # 实体相关
    EntityStatus,
    CreateStrategyAuto,
    DependencyLevel,
    # 血缘相关
    LineageNodeType,
    LineageRelation,
    ImpactLevel,
    # 变体矩阵相关
    VariantStatus,
)

__all__ = [
    'BaseEnum',
    # demo_project 枚举
    'CreateStrategy', 'Environment',
    'EntityStatus', 'CreateStrategyAuto', 'DependencyLevel',
    'LineageNodeType', 'LineageRelation', 'ImpactLevel',
    'VariantStatus',
]
