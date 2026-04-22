# -*- coding: utf-8 -*-
"""
数据提交 Spec - factory_boy
"""

import factory
import random
from datetime import datetime

from auto_tests.bdd_api_mock.factories import BaseFactory
from auto_tests.bdd_api_mock.entities.data.data_entity import DataSubmissionEntity


class DataSubmissionSpec(BaseFactory):
    """数据提交 Spec"""
    class Meta:
        model = DataSubmissionEntity

    # 基本字段
    name = factory.Sequence(lambda n: f"AUTO-DATA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{n:04d}")
    value = factory.LazyFunction(lambda: random.randint(1, 10000))
    submitter_id = None
    source_ip = factory.LazyFunction(lambda: f"192.168.1.{random.randint(1, 255)}")
    created_at = factory.LazyFunction(datetime.now)
