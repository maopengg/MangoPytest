# -*- coding: utf-8 -*-
"""
系统健康状态 Spec
"""

import factory
import random

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.entities.system import HealthEntity


class HealthSpec(BaseFactory):
    """系统健康状态 Spec"""
    class Meta:
        model = HealthEntity

    # 基础字段
    status = "healthy"
    version = factory.Sequence(lambda n: f"1.0.{n}")
    uptime = factory.LazyAttribute(lambda _: random.randint(3600, 86400 * 30))  # 1小时到30天
    checks = factory.LazyAttribute(lambda _: {
        "database": {"status": "ok", "response_time": "10ms"},
        "cache": {"status": "ok", "response_time": "5ms"},
        "disk": {"status": "ok", "free_space": "80%"},
    })

    # Trait: 不健康状态
    class Params:
        unhealthy = factory.Trait(
            status="unhealthy",
            checks=factory.LazyAttribute(lambda _: {
                "database": {"status": "error", "response_time": "5000ms"},
                "cache": {"status": "ok", "response_time": "5ms"},
            })
        )
        degraded = factory.Trait(
            status="degraded",
            checks=factory.LazyAttribute(lambda _: {
                "database": {"status": "warning", "response_time": "200ms"},
                "cache": {"status": "ok", "response_time": "5ms"},
            })
        )
