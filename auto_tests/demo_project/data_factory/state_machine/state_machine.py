# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机模块 - 向后兼容入口
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
状态机模块 - 向后兼容入口

注意：所有状态机基类已从 core.base 导入
请使用新的导入方式：from core.base import State, Transition, TransitionResult, StateMachine
"""

# 从 core.base 导入所有状态机基类
from core.base import (
    State,
    Transition,
    TransitionResult,
    StateMachine,
)

# 导出异常（保持向后兼容）
from .exceptions import (
    StateMachineError,
    InvalidTransitionError,
    InvalidStateError,
    TransitionHookError,
)

__all__ = [
    # 状态机基类
    'State',
    'Transition',
    'TransitionResult',
    'StateMachine',
    # 异常
    'StateMachineError',
    'InvalidTransitionError',
    'InvalidStateError',
    'TransitionHookError',
]
