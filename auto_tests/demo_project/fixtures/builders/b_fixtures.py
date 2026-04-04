# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: B Module Fixtures - B模块构造器 fixtures (Reimbursement)
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
B Module Fixtures 模块

提供 B模块（报销层）构造器 fixtures：
- reimb_builder: 报销单构造器

B模块依赖 C模块（Budget）和 D模块（User/Org）
"""

from typing import Generator

import pytest

from auto_tests.demo_project.data_factory.builders import ReimbursementBuilder
from auto_tests.demo_project.data_factory.builders.base_builder import BuilderContext


@pytest.fixture
def reimb_builder(test_token) -> Generator[ReimbursementBuilder, None, None]:
    """
    报销单构造器 fixture
    
    返回一个配置好的 ReimbursementBuilder 实例
    测试结束后自动清理
    
    使用示例：
        def test_create_reimbursement(reimb_builder):
            reimb = reimb_builder.create(user_id=1, amount=1000)
            assert reimb.id is not None
    """
    context = BuilderContext(cascade_cleanup=False, auto_prepare_deps=True)
    builder = ReimbursementBuilder(
        token=test_token,
        context=context
    )

    yield builder

    # 自动清理
    builder.cleanup()


@pytest.fixture
def approved_reimbursement(reimb_builder, employee_user):
    """
    已审批报销单 fixture
    
    返回一个已审批通过的报销单
    
    使用示例：
        def test_with_approved_reimb(approved_reimbursement):
            assert approved_reimbursement.status == "approved"
    """
    reimb = reimb_builder.create_approved(
        user_id=employee_user.id or 1,
        amount=5000,
        reason="测试报销"
    )
    return reimb


# 导出
__all__ = [
    "reimb_builder",
    "approved_reimbursement",
]
