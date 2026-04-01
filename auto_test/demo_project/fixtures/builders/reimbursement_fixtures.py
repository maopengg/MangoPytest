# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请模块fixtures (D级)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator

from auto_test.demo_project.data_factory.builders.reimbursement import (
    ReimbursementBuilder,
)


@pytest.fixture
def reimbursement_builder(authenticated_client) -> ReimbursementBuilder:
    """
    报销申请Builder Fixture
    提供ReimbursementBuilder实例用于创建和管理报销申请数据

    使用示例:
        def test_example(reimbursement_builder):
            reimbursement = reimbursement_builder.create(user_id=1, amount=100.00)
            assert reimbursement is not None
    """
    builder = ReimbursementBuilder(token=authenticated_client.token)
    yield builder
    # 清理创建的数据
    builder.cleanup()


@pytest.fixture
def created_reimbursement(reimbursement_builder) -> dict:
    """
    预创建的报销申请Fixture
    提供一个已创建的报销申请数据

    使用示例:
        def test_with_reimbursement(created_reimbursement):
            assert created_reimbursement["status"] == "pending"
    """
    reimbursement = reimbursement_builder.create(
        user_id=1, amount=1000.00, reason="差旅报销 - fixture"
    )
    return reimbursement


@pytest.fixture
def pending_reimbursement(reimbursement_builder) -> dict:
    """
    pending状态的报销申请Fixture
    提供一个待审批的报销申请
    """
    return reimbursement_builder.create(user_id=1, amount=500.00, reason="待审批报销")


@pytest.fixture
def multiple_reimbursements(reimbursement_builder) -> list:
    """
    多个报销申请Fixture
    提供多个已创建的报销申请数据
    """
    reimbursements = []
    for i in range(3):
        reimbursement = reimbursement_builder.create(
            user_id=1, amount=100.00 * (i + 1), reason=f"批量报销 {i + 1}"
        )
        reimbursements.append(reimbursement)
    return reimbursements
