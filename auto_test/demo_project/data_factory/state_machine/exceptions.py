# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机异常定义
# @Time   : 2026-04-01
# @Author : 毛鹏


class StateMachineError(Exception):
    """状态机基础异常"""
    pass


class InvalidTransitionError(StateMachineError):
    """无效状态转换异常"""

    def __init__(self, from_state: str, to_state: str, allowed_states: list = None):
        self.from_state = from_state
        self.to_state = to_state
        self.allowed_states = allowed_states or []

        message = f"无效的状态转换: '{from_state}' -> '{to_state}'"
        if allowed_states:
            message += f"，允许的目标状态: {allowed_states}"

        super().__init__(message)


class InvalidStateError(StateMachineError):
    """无效状态异常"""

    def __init__(self, state: str, valid_states: list):
        self.state = state
        self.valid_states = valid_states

        message = f"无效的状态: '{state}'，有效状态: {valid_states}"
        super().__init__(message)


class TransitionHookError(StateMachineError):
    """状态转换钩子执行异常"""

    def __init__(self, hook_name: str, from_state: str, to_state: str, original_error: Exception = None):
        self.hook_name = hook_name
        self.from_state = from_state
        self.to_state = to_state
        self.original_error = original_error

        message = f"状态转换钩子执行失败: {hook_name} ({from_state} -> {to_state})"
        if original_error:
            message += f"，原始错误: {original_error}"

        super().__init__(message)
