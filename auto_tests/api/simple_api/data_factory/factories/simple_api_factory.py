"""L3：生成以 AUTO_ 开头的简单 API 测试数据。"""

import uuid

from auto_tests.api.simple_api.data_factory.entities import SimpleApiEntity
from auto_tests.api.simple_api.data_factory.specs import SimpleApiSpec


class SimpleApiFactory:
    def __init__(self, spec: SimpleApiSpec):
        self.spec = spec

    def build(self) -> SimpleApiEntity:
        unique = uuid.uuid4().hex[:12]
        return SimpleApiEntity(
            run_name=f"AUTO_API_SIMPLE_{unique}",
            nonexistent_run_id=str(uuid.uuid4()),
            tenant_id=self.spec.tenant_id,
            username=self.spec.username,
            nonexistent_username=f"AUTO_NOT_EXISTS_{unique}",
            password=self.spec.password,
            wrong_password=self.spec.wrong_password,
            product_sku=f"AUTO_SKU_{unique}",
            product_name=f"{self.spec.product_name}_{unique}",
            updated_price=self.spec.updated_price,
        )
