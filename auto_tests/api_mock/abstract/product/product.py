# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class ProductAPI:
    """产品管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def create_product(self, name: str, price: float, description: str, stock: int) -> Dict[str, Any]:
        """
        创建产品接口
        @param name: 产品名称
        @param price: 产品价格
        @param description: 产品描述
        @param stock: 库存数量
        @return: 响应数据字典
        """
        product_data = {
            "name": name,
            "price": price,
            "description": description,
            "stock": stock
        }
        response = self.client.post("/products", json=product_data)
        return response.data

    def get_all_products(self) -> Dict[str, Any]:
        """
        获取所有产品接口
        @return: 响应数据字典
        """
        response = self.client.get("/products")
        return response.data

    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        根据ID获取产品接口
        @param product_id: 产品ID
        @return: 响应数据字典
        """
        response = self.client.get("/products", params={"id": product_id})
        return response.data

    def update_product_info(self, product_id: int, name: str, price: float, 
                            description: str, stock: int) -> Dict[str, Any]:
        """
        更新产品信息接口
        @param product_id: 产品ID
        @param name: 产品名称
        @param price: 产品价格
        @param description: 产品描述
        @param stock: 库存数量
        @return: 响应数据字典
        """
        update_data = {
            "name": name,
            "price": price,
            "description": description,
            "stock": stock
        }
        response = self.client.put(f"/products/{product_id}", json=update_data)
        return response.data

    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """
        删除产品接口
        @param product_id: 产品ID
        @return: 响应数据字典
        """
        response = self.client.delete(f"/products/{product_id}")
        return response.data
