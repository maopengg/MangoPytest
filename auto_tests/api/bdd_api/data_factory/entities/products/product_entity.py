"""商品域 L3 测试数据实体。"""

from pydantic import BaseModel, ConfigDict


class ProductEntity(BaseModel):
    """描述提交给接口的商品数据，包括用于负向测试的非法价格。"""

    model_config = ConfigDict(extra="forbid")

    sku: str
    name: str
    price: float
    stock: int

    def create_payload(self) -> dict:
        return self.model_dump()
