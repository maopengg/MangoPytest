"""L3：简单 API 场景使用的测试数据实体。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleApiEntity:
    run_name: str
    nonexistent_run_id: str
    tenant_id: str
    username: str
    nonexistent_username: str
    password: str
    wrong_password: str
    product_sku: str
    product_name: str
    updated_price: float
