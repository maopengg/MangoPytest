# -*- coding: utf-8 -*-
"""
文件 Spec - pytest-factoryboy
"""

import factory
from pytest_factoryboy import register
from datetime import datetime

from core.base.baseFactory import BaseFactory
from auto_tests.bdd_api_mock.data_factory.entities.file.file_entity import FileEntity


@register
class FileSpec(BaseFactory):
    """文件 Spec"""

    class Meta:
        model = FileEntity

    # 基本字段
    file_id = factory.LazyFunction(lambda: __import__("uuid").uuid4().hex)
    filename = factory.Sequence(
        lambda n: f"AUTO-FILE-{datetime.now().strftime('%Y%m%d%H%M%S')}-{n:04d}.txt"
    )
    original_name = factory.LazyAttribute(lambda o: o.filename)
    content_type = factory.Iterator(
        ["text/plain", "application/pdf", "image/png", "application/json"]
    )
    size = factory.LazyFunction(
        lambda: __import__("random").randint(1024, 10485760)
    )  # 1KB - 10MB
    file_path = factory.LazyAttribute(lambda o: f"/uploads/{o.file_id}/{o.filename}")
    uploader_id = None
    download_count = 0
    created_at = factory.LazyFunction(datetime.now)
