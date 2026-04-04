# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 构造器实现层
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
构造器实现层

职责：
1. 构造实体数据
2. 调用API创建/更新/删除数据
3. 管理实体生命周期
4. 自动清理创建的数据
5. 【新增】智能依赖解决
6. 【新增】快捷方法支持

使用示例：
    # 从具体模块导入 Builder
    from auto_tests.demo_project.data_factory.builders.user.user_builder import UserBuilder
    from auto_tests.demo_project.data_factory.builders.reimbursement.reimbursement_builder import ReimbursementBuilder

    # 基础用法
    builder = UserBuilder()
    entity = builder.create(username="test", email="test@example.com")

    # 【新增】智能依赖解决 - 自动创建所有依赖
    from auto_tests.demo_project.data_factory.builders.payment.payment_builder import PaymentBuilder
    payment_builder = PaymentBuilder()
    payment = payment_builder.create(amount=5000)  # 自动创建报销单→预算→组织→用户

    # 【新增】快捷方法
    payment = payment_builder.create_paid(amount=5000)  # 创建并付款

    # 清理
    builder.cleanup()
"""

# 只导出基类和枚举，具体 Builder 请从各自模块导入
from core.base import BaseBuilder, BuilderContext
from core.enums.demo_enum import DependencyLevel

__all__ = [
    # 基类和上下文
    "BaseBuilder",
    "BuilderContext",
    "DependencyLevel",
]
