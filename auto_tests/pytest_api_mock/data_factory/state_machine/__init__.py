# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机模块 - 实体状态管理
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
状态机模块（State Machine）

提供实体状态管理功能，支持：
- 状态转换规则定义
- 转换验证
- 转换钩子（before/after/around）
- 状态历史记录
- 智能工厂方法

使用示例：
    from auto_tests.pytest_api_mock.data_factory.state_machine import StateMachine, State

    # 定义状态机
    class UserStateMachine(StateMachine):
        STATES = ["active", "locked", "inactive"]
        TRANSITIONS = {
            "active": ["locked", "inactive"],
            "locked": ["active", "inactive"],
            "inactive": ["active"]
        }

    # 在实体中使用
    user = UserEntity(username="test")
    user.transition_to("locked")  # active -> locked
    user.transition_to("inactive")  # locked -> inactive
"""

from .user_state_machine import UserStateMachine, is_active, is_locked, is_inactive

__all__ = [
    "UserStateMachine",
    # 便捷函数
    "is_active",
    "is_locked",
    "is_inactive",
]
