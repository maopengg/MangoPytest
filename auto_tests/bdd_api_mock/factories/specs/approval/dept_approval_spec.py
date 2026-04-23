# -*- coding: utf-8 -*-
"""
部门审批 Spec - pytest-factoryboy
"""

import factory
from pytest_factoryboy import register
from datetime import datetime

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.factories.specs.reimbursement.reimbursement_spec import (
    ReimbursementSpec,
)
from auto_tests.bdd_api_mock.entities.approval.dept_approval_entity import (
    DeptApprovalEntity,
)


@register
class DeptApprovalSpec(BaseFactory):
    """部门审批 Spec"""

    class Meta:
        model = DeptApprovalEntity
        exclude = ("_reimbursement", "_approver")

    # 关联实体 - 自动创建
    _reimbursement = factory.SubFactory(ReimbursementSpec)
    _approver = factory.SubFactory(UserSpec, is_manager=True)

    # 外键字段
    reimbursement_id = factory.SelfAttribute("_reimbursement.id")
    approver_id = factory.SelfAttribute("_approver.id")

    # 基本字段
    approval_no = factory.LazyFunction(
        lambda: f"DA{datetime.now().strftime('%Y%m%d%H%M%S')}{__import__('uuid').uuid4().hex[:4].upper()}"
    )
    status = "approved"
    comment = factory.LazyAttribute(lambda o: f"部门审批意见 - {o.approval_no}")
    approved_at = factory.LazyFunction(datetime.now)
    created_at = factory.LazyFunction(datetime.now)

    # Trait
    class Params:
        rejected = factory.Trait(
            status="rejected",
            comment="审批拒绝",
        )
