# -*- coding: utf-8 -*-
"""
API调用日志 Spec - pytest-factoryboy
"""

import factory
from pytest_factoryboy import register
from datetime import datetime

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.entities.system.api_log_entity import APILogEntity


@register
class APILogSpec(BaseFactory):
    """API调用日志工厂"""

    class Meta:
        model = APILogEntity

    request_id = factory.Sequence(lambda n: f"req_{n:08d}")
    method = factory.Iterator(["GET", "POST", "PUT", "DELETE"])
    path = factory.Iterator(
        [
            "/api/v1/users",
            "/api/v1/products",
            "/api/v1/orders",
            "/api/v1/reimbursements",
        ]
    )
    query_params = None
    request_body = None
    response_body = None
    status_code = factory.Iterator([200, 201, 400, 404, 500])
    user_id = factory.Sequence(lambda n: n)
    client_ip = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    duration_ms = factory.Iterator([10, 50, 100, 200, 500])
    created_at = factory.LazyFunction(datetime.now)
