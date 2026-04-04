# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品构造器 - 对应 /products 接口
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Dict, Any, List

from auto_tests.demo_project.api_manager import demo_project
from core.base import BaseBuilder
from ...registry import register_builder


@register_builder("product")
class ProductBuilder(BaseBuilder):
    """
    产品构造器
    对应 /products 接口 (POST, GET, PUT, DELETE)
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token=token, factory=factory)
        # 设置token到API模块
        if token:
            demo_project.product.set_token(token)

    def build(self, name: str = None, price: float = None,
              description: str = None, stock: int = 100, **kwargs) -> Dict[str, Any]:
        """
        构造产品数据（不调用API）
        @return: 产品数据字典
        """
        return {
            "name": name or f"Product {uuid.uuid4().hex[:6]}",
            "price": price or 99.99,
            "description": description or f"Test product description {uuid.uuid4().hex[:4]}",
            "stock": stock,
        }

    def create(self, name: str = None, price: float = None,
               description: str = None, stock: int = 100, **kwargs) -> Dict[str, Any]:
        """
        创建产品
        @return: 创建的产品数据
        """
        product_data = self.build(name, price, description, stock)

        result = demo_project.product.create_product(
            name=product_data["name"],
            price=product_data["price"],
            description=product_data["description"],
            stock=product_data["stock"],
        )

        if result.get("code") == 200:
            created_product = result["data"]
            return created_product
        return None

    def get_all(self) -> List[Dict[str, Any]]:
        """
        获取所有产品
        @return: 产品列表
        """
        result = demo_project.product.get_all_products()
        if result.get("code") == 200:
            return result["data"]
        return []

    def get_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        根据ID获取产品
        @param product_id: 产品ID
        @return: 产品数据
        """
        result = demo_project.product.get_product_by_id(product_id)
        if result.get("code") == 200:
            return result["data"]
        return None

    def update(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新产品信息
        @param product_id: 产品ID
        @param product_data: 产品数据
        @return: 更新后的产品数据
        """
        result = demo_project.product.update_product_info(
            product_id=product_id,
            **product_data
        )
        if result.get("code") == 200:
            return result["data"]
        return None

    def delete(self, product_id: int) -> bool:
        """
        删除产品
        @param product_id: 产品ID
        @return: 是否删除成功
        """
        result = demo_project.product.delete_product(product_id)
        if result.get("code") == 200:
            return True
        return False
