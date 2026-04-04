# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机异常 - 使用统一异常体系
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
状态机异常模块

使用统一的异常体系，从 exceptions 导入基础异常类
"""

from exceptions import ApiError, DataError

# 为了保持向后兼容，提供别名
StateMachineError = DataError
InvalidTransitionError = ApiError
InvalidStateError = ApiError
TransitionHookError = ApiError

__all__ = [
    'StateMachineError',
    'InvalidTransitionError',
    'InvalidStateError',
    'TransitionHookError',
]
