# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态机功能演示
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
状态机功能演示

本示例展示：
1. 状态定义和转换规则
2. 状态转换方法（lock/unlock/deactivate/activate）
3. 状态检查方法（is_active/is_locked/is_inactive）
4. 智能工厂方法（User.active()/locked()/inactive()）
5. 业务行为（登录失败自动锁定）
6. 状态转换历史记录
"""

import sys

sys.path.insert(0, r'd:\code\MangoPytest')

from auto_tests.bdd_api_mock.data_factory.entities import UserEntity
from auto_tests.bdd_api_mock.data_factory.state_machine import UserStateMachine


def demo_basic_state_transition():
    """演示基本状态转换"""
    print("=" * 60)
    print("演示1: 基本状态转换")
    print("=" * 60)

    # 创建用户（初始状态为 active）
    user = UserEntity(
        username="test_user",
        email="test@example.com",
        password="Test@123456"
    )

    print(f"创建用户，初始状态: {user.status}")
    print(f"  - is_active(): {user.is_active()}")
    print(f"  - is_locked(): {user.is_locked()}")
    print(f"  - is_inactive(): {user.is_inactive()}")

    # active -> locked
    print("\n执行 lock()...")
    result = user.lock()
    print(f"  转换结果: {result.success}")
    print(f"  当前状态: {user.status}")
    print(f"  - is_locked(): {user.is_locked()}")

    # locked -> active
    print("\n执行 unlock()...")
    result = user.unlock()
    print(f"  转换结果: {result.success}")
    print(f"  当前状态: {user.status}")
    print(f"  - is_active(): {user.is_active()}")

    # active -> inactive
    print("\n执行 deactivate()...")
    result = user.deactivate()
    print(f"  转换结果: {result.success}")
    print(f"  当前状态: {user.status}")
    print(f"  - is_inactive(): {user.is_inactive()}")

    # inactive -> active
    print("\n执行 activate()...")
    result = user.activate()
    print(f"  转换结果: {result.success}")
    print(f"  当前状态: {user.status}")

    return True


def demo_invalid_transition():
    """演示无效状态转换"""
    print("\n" + "=" * 60)
    print("演示2: 无效状态转换")
    print("=" * 60)

    # 创建已注销用户
    user = UserEntity.inactive(
        username="inactive_user",
        email="inactive@example.com",
        password="Test@123456"
    )

    print(f"用户状态: {user.status}")

    # 尝试注销 -> 锁定（无效转换）
    print("\n尝试执行 lock()（inactive -> locked 是无效转换）...")
    can_lock = user.can_transition_to("locked")
    print(f"  can_transition_to('locked'): {can_lock}")

    result = user.lock()
    print(f"  转换结果: {result.success}")
    print(f"  错误信息: {result.message}")

    # 有效转换：inactive -> active
    print("\n执行 activate()（inactive -> active 是有效转换）...")
    result = user.activate()
    print(f"  转换结果: {result.success}")
    print(f"  当前状态: {user.status}")

    return True


def demo_smart_factory_methods():
    """演示智能工厂方法"""
    print("\n" + "=" * 60)
    print("演示3: 智能工厂方法")
    print("=" * 60)

    # 使用工厂方法创建不同状态的用户
    print("创建 active 状态用户...")
    user1 = UserEntity.active(
        username="active_user",
        email="active@example.com",
        password="Test@123456"
    )
    print(f"  状态: {user1.status}")
    print(f"  登录失败次数: {user1.login_failures}")

    print("\n创建 locked 状态用户...")
    user2 = UserEntity.locked(
        username="locked_user",
        email="locked@example.com",
        password="Test@123456"
    )
    print(f"  状态: {user2.status}")
    print(f"  登录失败次数: {user2.login_failures}")

    print("\n创建 inactive 状态用户...")
    user3 = UserEntity.inactive(
        username="inactive_user",
        email="inactive@example.com",
        password="Test@123456"
    )
    print(f"  状态: {user3.status}")

    return True


def demo_auto_lock_on_login_failure():
    """演示登录失败自动锁定"""
    print("\n" + "=" * 60)
    print("演示4: 登录失败自动锁定")
    print("=" * 60)

    user = UserEntity.active(
        username="auto_lock_user",
        email="auto@example.com",
        password="Test@123456"
    )

    print(f"初始状态: {user.status}")
    print(f"登录失败次数: {user.login_failures}")

    # 模拟登录失败
    print("\n模拟登录失败...")
    for i in range(1, 4):
        locked = user.record_login_failure()
        print(f"  第{i}次失败: login_failures={user.login_failures}, locked={locked}")
        if locked:
            print(f"  用户已被自动锁定！")
            break

    print(f"\n最终状态: {user.status}")
    print(f"is_locked(): {user.is_locked()}")

    # 解锁后重置失败次数
    print("\n执行 unlock()...")
    user.unlock()
    print(f"解锁后状态: {user.status}")
    print(f"登录失败次数: {user.login_failures}")

    return True


def demo_state_history():
    """演示状态转换历史"""
    print("\n" + "=" * 60)
    print("演示5: 状态转换历史")
    print("=" * 60)

    user = UserEntity.active(
        username="history_user",
        email="history@example.com",
        password="Test@123456"
    )

    # 执行多次状态转换
    user.lock()
    user.unlock()
    user.deactivate()
    user.activate()

    # 获取状态机并查看历史
    state_machine = user._state_machine
    history = state_machine.get_state_history()

    print(f"状态转换历史（共{len(history)}次）：")
    for i, record in enumerate(history, 1):
        print(f"  {i}. {record['from']} -> {record['to']} ({record['timestamp']})")

    return True


def demo_state_machine_class_methods():
    """演示状态机类方法"""
    print("\n" + "=" * 60)
    print("演示6: 状态机类方法")
    print("=" * 60)

    # 获取所有状态
    states = UserStateMachine.get_states()
    print(f"所有状态定义：")
    for state in states:
        print(f"  - {state.name}: {state.description}")
        if state.is_initial:
            print(f"    (初始状态)")

    # 获取转换规则
    print(f"\n状态转换规则：")
    for from_state, to_states in UserStateMachine.TRANSITIONS.items():
        print(f"  {from_state} -> {to_states}")

    # 检查转换有效性
    print(f"\n转换有效性检查：")
    print(f"  can_transition('active', 'locked'): {UserStateMachine.can_transition('active', 'locked')}")
    print(f"  can_transition('inactive', 'locked'): {UserStateMachine.can_transition('inactive', 'locked')}")
    print(f"  can_transition('active', 'deleted'): {UserStateMachine.can_transition('active', 'deleted')}")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Entity状态机功能演示")
    print("状态流转: active <-> locked <-> inactive")
    print("=" * 60)

    results = []

    # 运行所有演示
    results.append(("基本状态转换", demo_basic_state_transition()))
    results.append(("无效状态转换", demo_invalid_transition()))
    results.append(("智能工厂方法", demo_smart_factory_methods()))
    results.append(("登录失败自动锁定", demo_auto_lock_on_login_failure()))
    results.append(("状态转换历史", demo_state_history()))
    results.append(("状态机类方法", demo_state_machine_class_methods()))

    # 总结
    print("\n" + "=" * 60)
    print("演示总结")
    print("=" * 60)

    for name, success in results:
        status = "[OK] 成功" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")

    print("\n" + "=" * 60)
    print("状态机特性：")
    print("  - 状态定义和验证")
    print("  - 转换规则管理")
    print("  - 转换钩子支持（before/after/around）")
    print("  - 状态历史记录")
    print("  - 智能工厂方法")
    print("  - 业务行为集成")
    print("=" * 60)


if __name__ == "__main__":
    main()
