# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: A Module Fixtures - A模块构造器 fixtures (Payment)
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
A Module Fixtures 模块

提供 A模块（付款层）构造器 fixtures：
- payment_builder: 付款单构造器

A模块依赖 B模块（Reimbursement）
"""

from typing import Generator

import pytest

from auto_tests.demo_project.data_factory.builders import PaymentBuilder
from auto_tests.demo_project.data_factory.builders.base_builder import BuilderContext


@pytest.fixture
def payment_builder(test_token) -> Generator[PaymentBuilder, None, None]:
    """
    付款单构造器 fixture
    
    返回一个配置好的 PaymentBuilder 实例
    测试结束后自动清理
    
    使用示例：
        def test_create_payment(payment_builder):
            payment = payment_builder.create(amount=5000)
            assert payment.id is not None
    """
    context = BuilderContext(cascade_cleanup=False, auto_prepare_deps=True)
    builder = PaymentBuilder(
        token=test_token,
        context=context
    )

    yield builder

    # 自动清理
    builder.cleanup()


@pytest.fixture
def paid_payment(payment_builder):
    """
    已付款付款单 fixture
    
    返回一个已付款的付款单
    
    使用示例：
        def test_with_paid_payment(paid_payment):
            assert paid_payment.status == "paid"
    """
    payment = payment_builder.create_paid(
        amount=5000,
        payee="供应商A"
    )
    return payment


# 导出
__all__ = [
    "payment_builder",
    "paid_payment",
]
