# -*- coding: utf-8 -*-
"""
财务审批 Spec - pytest-factoryboy
"""

import factory
from pytest_factoryboy import register
from datetime import datetime

from core.base.baseFactory import BaseFactory
from auto_tests.bdd_api_mock.data_factory.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.data_factory.specs.approval.dept_approval_spec import (
    DeptApprovalSpec,
)
from auto_tests.bdd_api_mock.data_factory.entities.approval.finance_approval_entity import (
    FinanceApprovalEntity,
)


@register
class FinanceApprovalSpec(BaseFactory):
    """财务审批 Spec"""

    class Meta:
        model = FinanceApprovalEntity
        exclude = ("_dept_approval", "_approver")

    # 关联实体 - 自动创建
    _dept_approval = factory.SubFactory(DeptApprovalSpec)
    _approver = factory.SubFactory(UserSpec, is_finance=True)

    # 外键字段
    reimbursement_id = factory.SelfAttribute("_dept_approval.reimbursement_id")
    dept_approval_id = factory.SelfAttribute("_dept_approval.id")
    approver_id = factory.SelfAttribute("_approver.id")

    # 基本字段
    approval_no = factory.LazyFunction(
        lambda: f"FA{datetime.now().strftime('%Y%m%d%H%M%S')}{__import__('uuid').uuid4().hex[:4].upper()}"
    )
    status = "approved"
    comment = factory.LazyAttribute(lambda o: f"财务审批意见 - {o.approval_no}")
    finance_check_passed = True
    approved_at = factory.LazyFunction(datetime.now)
    created_at = factory.LazyFunction(datetime.now)

    # Trait
    class Params:
        rejected = factory.Trait(
            status="rejected",
            comment="财务审批拒绝",
            finance_check_passed=False,
        )
