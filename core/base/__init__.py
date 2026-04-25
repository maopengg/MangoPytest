# -*- coding: utf-8 -*-
"""
Core Base - 核心基础类模块

提供项目通用的基础类和接口：
- config: 配置管理基类
- base_builder: Builder基类
- base_entity: 实体基类
- pydantic_base: Pydantic实体基类
- builder_context: Builder执行上下文
- pydantic_builder: Pydantic Builder基类
- base_strategy: 策略基类
- strategy_result: 策略执行结果
"""

from .config import BaseConfig
from .base_builder import BaseBuilder
from .base_entity import BaseEntity
from .pydantic_base import PydanticEntity
from .builder_context import BuilderContext
from .pydantic_builder import PydanticBuilder
from .base_strategy import BaseStrategy
from .strategy_result import StrategyResult

__all__ = [
    "BaseConfig",
    "BaseBuilder",
    "BaseEntity",
    "PydanticEntity",
    "BuilderContext",
    "PydanticBuilder",
    "BaseStrategy",
    "StrategyResult",
]
