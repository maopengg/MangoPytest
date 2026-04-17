# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品构造器 - Pydantic 版本 (L2 构造器层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
产品构造器 - L2 构造器层

接收 L3 Entity，调用 to_api_payload() 后传给 L1
"""

from typing import Any, Dict, List, Optional

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from auto_tests.bdd_api_mock.data_factory.entities.product_pydantic import ProductEntity
from core.base import PydanticBuilder


class ProductBuilder(PydanticBuilder[ProductEntity]):
    """
    产品构造器 - L2 构造器层
    
    对应 /products 接口
    
    使用示例：
        # 使用 Entity 创建产品
        product = ProductEntity.default()
        builder = ProductBuilder(token="xxx")
        created = builder.create_entity(product)
        
        # 便捷方法
        product = builder.create(name="iPhone", price=6999.0)
    """
    
    ENTITY_CLASS = ProductEntity
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 Builder
        
        @param token: 认证 token
        """
        super().__init__(token=token)
    
    def create_entity(self, entity: ProductEntity) -> ProductEntity:
        """
        创建产品实体
        
        @param entity: L3 ProductEntity
        @return: 创建后的 ProductEntity（包含 id 等响应字段）
        """
        payload = entity.to_api_payload()  # L3 提供
        result = bdd_api_mock.product.create_product(**payload)
        
        if result.get("code") == 200:
            # 更新 entity 的响应字段
            entity.update_from_response(result["data"])
            self._track_entity(entity)
            return entity
        
        raise RuntimeError(f"Failed to create product: {result.get('message')}")
    
    def get_by_id(self, product_id: int) -> Optional[ProductEntity]:
        """
        根据 ID 获取产品
        
        @param product_id: 产品 ID
        @return: ProductEntity 或 None
        """
        result = bdd_api_mock.product.get_product(product_id)
        
        if result.get("code") == 200:
            return ProductEntity.from_response(result["data"])
        
        return None
    
    def get_all(self) -> List[ProductEntity]:
        """
        获取所有产品
        
        @return: ProductEntity 列表
        """
        result = bdd_api_mock.product.get_products()
        
        if result.get("code") == 200:
            return [ProductEntity.from_response(data) for data in result.get("data", [])]
        
        return []
    
    def update(self, entity: ProductEntity) -> ProductEntity:
        """
        更新产品
        
        @param entity: L3 ProductEntity（必须包含 id）
        @return: 更新后的 ProductEntity
        """
        if entity.id is None:
            raise ValueError("Entity must have id to update")
        
        payload = entity.to_api_payload()
        result = bdd_api_mock.product.update_product(entity.id, **payload)
        
        if result.get("code") == 200:
            entity.update_from_response(result["data"])
            return entity
        
        raise RuntimeError(f"Failed to update product: {result.get('message')}")
    
    def _delete_entity(self, entity: ProductEntity) -> None:
        """
        删除实体
        
        @param entity: 要删除的产品实体
        """
        if entity.id:
            bdd_api_mock.product.delete_product(entity.id)
