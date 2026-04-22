# -*- coding: utf-8 -*-
"""
报销申请 Spec - factory_boy
"""

import factory
import uuid
import random
from datetime import datetime
from decimal import Decimal

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.factories.specs.user.user_spec import UserSpec
from auto_tests.bdd_api_mock.entities.reimbursement.reimbursement_entity import ReimbursementEntity


class ReimbursementSpec(BaseFactory):
    """报销申请 Spec"""
    class Meta:
        model = ReimbursementEntity
        exclude = ("_user",)

    # 关联实体 - 自动创建
    _user = factory.SubFactory(UserSpec)

    # 外键字段
    user_id = factory.SelfAttribute("_user.id")

    # 基本字段
    reimb_no = factory.LazyFunction(lambda: f"RMB{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4].upper()}")
    amount = factory.LazyFunction(lambda: Decimal(str(random.uniform(100, 10000))).quantize(Decimal("0.01")))
    reason = factory.LazyAttribute(lambda o: f"报销原因 - {o.reimb_no}")
    category = factory.Iterator(["general", "travel", "meal", "office", "equipment"])
    attachments = None
    status = "pending"
    current_step = 1
    submitted_at = factory.LazyFunction(datetime.now)
    completed_at = None
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

    # Trait
    class Params:
        dept_approved = factory.Trait(
            status="dept_approved",
            current_step=2,
        )
        dept_rejected = factory.Trait(
            status="dept_rejected",
            current_step=1,
            completed_at=factory.LazyFunction(datetime.now),
        )
        finance_approved = factory.Trait(
            status="finance_approved",
            current_step=3,
        )
        ceo_approved = factory.Trait(
            status="ceo_approved",
            current_step=4,
            completed_at=factory.LazyFunction(datetime.now),
        )
        paid = factory.Trait(
            status="paid",
            current_step=4,
            completed_at=factory.LazyFunction(datetime.now),
        )
