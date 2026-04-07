# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品实体 - Pydantic 版本 (L3 实体层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
产品实体 - L3 实体层

使用 Pydantic 定义数据模型，提供 to_api_payload() 方法
"""

from typing import Any, Dict, Optional

from pydantic import Field

from core.base import PydanticEntity


class ProductEntity(PydanticEntity):
    """
    产品实体 - L3 实体层
    
    Attributes:
        id: 产品ID（响应字段，创建后填充）
        name: 产品名称（请求字段）
        price: 价格（请求字段）
        description: 描述（请求字段，可选）
        stock: 库存（请求字段，可选）
        category: 分类（请求字段，可选）
    """
    
    # 请求字段
    name: str = Field(default="", min_length=1, description="产品名称")
    price: float = Field(default=0.0, gt=0, description="价格")
    description: str = Field(default="", description="描述")
    stock: int = Field(default=0, ge=0, description="库存")
    category: str = Field(default="", description="分类")
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为 API 请求体
        
        @return: API 请求体字典
        """
        payload = {
            "name": self.name,
            "price": self.price,
        }
        # 可选字段只在有值时添加
        if self.description:
            payload["description"] = self.description
        if self.stock > 0:
            payload["stock"] = self.stock
        if self.category:
            payload["category"] = self.category
        return payload
    
    # ==================== 业务逻辑方法 ====================
    
    def is_in_stock(self) -> bool:
        """检查是否有库存"""
        return self.stock > 0
    
    def can_order(self, quantity: int = 1) -> bool:
        """检查是否可以订购指定数量"""
        return self.stock >= quantity
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def default(cls) -> "ProductEntity":
        """创建默认产品"""
        import uuid
        return cls(
            name=f"Product_{uuid.uuid4().hex[:8]}",
            price=99.99,
            description="Default product",
            stock=100,
            category="general",
        )
    
    @classmethod
    def with_price(cls, price: float) -> "ProductEntity":
        """创建指定价格的产品"""
        import uuid
        return cls(
            name=f"Product_{uuid.uuid4().hex[:8]}",
            price=price,
            stock=100,
        )
    
    @classmethod
    def out_of_stock(cls) -> "ProductEntity":
        """创建无库存产品"""
        import uuid
        return cls(
            name=f"OutOfStock_{uuid.uuid4().hex[:8]}",
            price=99.99,
            stock=0,
        )
