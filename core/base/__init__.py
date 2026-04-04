# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 基类模块 - 所有项目基类集中管理
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
统一基类模块

集中管理所有基类，包括：
- 实体基类 (BaseEntity)
- Builder基类 (BaseBuilder)
- Strategy基类 (BaseStrategy)
- Scenario基类 (BaseScenario)
- 数据构建器基类 (BaseDataBuilder)
- 数据工厂基类 (DataFactoryBase)
- 测试分层基类 (UnitTest, IntegrationTest, E2ETest)

使用方式：
    from core.base import BaseEntity, BaseBuilder, BaseStrategy
"""

from .base_builder import BaseBuilder
# 实体基类
from .base_entity import BaseEntity
from .base_strategy import BaseStrategy
from .strategy_result import StrategyResult
# Builder相关
from .builder_context import BuilderContext
# 测试分层基类（从 layering_base.py 导入）
from .layering_base import (
    TestLayer,
    UnitTest,
    IntegrationTest,
    E2ETest,
    TestContext,
    TestCaseResult,
    TestLayerType,
)
# 状态机基类（从 state_machine.py 导入）
from .state_machine import (
    State,
    Transition,
    TransitionResult,
    StateMachine,
)

# Web UI 基类（从 web_base.py 导入）
from .web_base import WebBaseObject

__all__ = [
    # 实体基类
    "BaseEntity",
    # 策略相关
    "StrategyResult",
    "BaseStrategy",
    # Builder相关
    "BuilderContext",
    "BaseBuilder",
    # 测试分层基类
    "TestLayer",
    "UnitTest",
    "IntegrationTest",
    "E2ETest",
    "TestContext",
    "TestCaseResult",
    "TestLayerType",
    # 状态机基类
    "State",
    "Transition",
    "TransitionResult",
    "StateMachine",
    # Web UI 基类
    "WebBaseObject",
]
