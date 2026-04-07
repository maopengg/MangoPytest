# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单实体 - Pydantic 版本 (L3 实体层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
订单实体 - L3 实体层

使用 Pydantic 定义数据模型，提供 to_api_payload() 方法
"""

from typing import Any, Dict, Optional

from pydantic import Field

from core.base import PydanticEntity


class OrderEntity(PydanticEntity):
    """
    订单实体 - L3 实体层
    
    Attributes:
        id: 订单ID（响应字段，创建后填充）
        product_id: 产品ID（请求字段）
        user_id: 用户ID（请求字段）
        quantity: 数量（请求字段）
        total_price: 总价（响应字段）
        status: 订单状态（响应字段）
    """
    
    # 请求字段
    product_id: int = Field(default=0, gt=0, description="产品ID")
    user_id: int = Field(default=0, gt=0, description="用户ID")
    quantity: int = Field(default=1, gt=0, description="数量")
    
    # 响应字段
    total_price: float = Field(default=0.0, description="总价")
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为 API 请求体
        
        @return: API 请求体字典
        """
        return {
            "product_id": self.product_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
        }
    
    # ==================== 业务逻辑方法 ====================
    
    def is_pending(self) -> bool:
        """检查是否待支付"""
        return self.status == "pending"
    
    def is_paid(self) -> bool:
        """检查是否已支付"""
        return self.status == "paid"
    
    def is_shipped(self) -> bool:
        """检查是否已发货"""
        return self.status == "shipped"
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.status == "completed"
    
    def can_cancel(self) -> bool:
        """检查是否可以取消"""
        return self.status in ["pending", "paid"]
    
    def calculate_total(self, product_price: float) -> float:
        """计算总价"""
        return product_price * self.quantity
    
    # ==================== 工厂方法 ====================
    
    @classmethod
    def default(cls) -> "OrderEntity":
        """创建默认订单"""
        return cls(
            product_id=1,
            user_id=1,
            quantity=1,
        )
    
    @classmethod
    def with_product(cls, product_id: int, quantity: int = 1) -> "OrderEntity":
        """使用指定产品创建订单"""
        return cls(
            product_id=product_id,
            user_id=1,
            quantity=quantity,
        )
    
    @classmethod
    def bulk(cls, product_id: int, quantity: int) -> "OrderEntity":
        """创建批量订单"""
        return cls(
            product_id=product_id,
            user_id=1,
            quantity=quantity,
        )
