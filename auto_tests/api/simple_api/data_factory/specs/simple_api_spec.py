"""L3：简单 API 场景的数据规格。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleApiSpec:
    tenant_id: str = "tenant-a"
    username: str = "employee"
    password: str = "password123"
    wrong_password: str = "AUTO_WRONG_PASSWORD"
    product_name: str = "AUTO_SIMPLE_PRODUCT"
    updated_price: float = 22.5
