"""商品域 L3 测试数据实体。"""

from pydantic import BaseModel, ConfigDict


class ProductEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str
    name: str
    price: float
    stock: int

    def create_payload(self) -> dict:
        return self.model_dump()
