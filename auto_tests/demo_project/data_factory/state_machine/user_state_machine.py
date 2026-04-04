# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户实体状态机定义
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
用户实体状态机

状态流转：
    active <-> locked <-> inactive
    
    active → locked: 用户登录失败3次
    active → inactive: 用户主动注销
    locked → active: 管理员解锁
    locked → inactive: 用户注销（被锁定状态下）
    inactive → active: 用户重新激活

使用示例：
    from auto_tests.demo_project.data_factory.state_machine import UserStateMachine
    
    # 创建用户（初始状态为 active）
    user = UserEntity(username="test", password="123456")
    print(user.status)  # "active"
    
    # 锁定用户
    user.lock()  # active -> locked
    
    # 解锁用户
    user.unlock()  # locked -> active
    
    # 注销用户
    user.deactivate()  # active -> inactive
"""

from .state_machine import StateMachine, State


class UserStateMachine(StateMachine):
    """
    用户状态机
    
    管理用户账户的生命周期状态
    """

    # 状态定义
    STATES = [
        State("active", description="正常状态，可以登录", is_initial=True),
        State("locked", description="锁定状态，暂时无法登录"),
        State("inactive", description="注销状态，无法登录")
    ]

    # 状态转换规则
    TRANSITIONS = {
        "active": ["locked", "inactive"],
        "locked": ["active", "inactive"],
        "inactive": ["active"]
    }

    # 状态字段名
    STATE_FIELD = "status"


# 便捷的状态检查方法
def is_active(entity) -> bool:
    """检查用户是否处于正常状态"""
    return getattr(entity, "status", None) == "active"


def is_locked(entity) -> bool:
    """检查用户是否处于锁定状态"""
    return getattr(entity, "status", None) == "locked"


def is_inactive(entity) -> bool:
    """检查用户是否处于注销状态"""
    return getattr(entity, "status", None) == "inactive"
