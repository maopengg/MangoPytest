# -*- coding: utf-8 -*-
"""
总经理审批 Spec - factory_boy
"""

import factory
import uuid
from datetime import datetime

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.factories.specs.approval.finance_approval_spec import FinanceApprovalSpec
from auto_tests.bdd_api_mock.entities.approval.ceo_approval_entity import CEOApprovalEntity


class CEOApprovalSpec(BaseFactory):
    """总经理审批 Spec"""
    class Meta:
        model = CEOApprovalEntity
        exclude = ("_finance_approval", "_approver")

    # 关联实体 - 自动创建
    _finance_approval = factory.SubFactory(FinanceApprovalSpec)
    _approver = factory.SubFactory(UserSpec, is_ceo=True)

    # 外键字段
    reimbursement_id = factory.SelfAttribute("_finance_approval.reimbursement_id")
    finance_approval_id = factory.SelfAttribute("_finance_approval.id")
    approver_id = factory.SelfAttribute("_approver.id")

    # 基本字段
    approval_no = factory.LazyFunction(lambda: f"CA{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}")
    status = "approved"
    comment = factory.LazyAttribute(lambda o: f"总经理审批意见 - {o.approval_no}")
    approved_at = factory.LazyFunction(datetime.now)
    created_at = factory.LazyFunction(datetime.now)

    # Trait
    class Params:
        rejected = factory.Trait(
            status="rejected",
            comment="总经理审批拒绝",
        )
