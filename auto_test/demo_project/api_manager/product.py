# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品API - 使用 Core APIClient
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from auto_test.demo_project.core.api.client import APIClient


class ProductAPI:
    """产品API - 对应 /products 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def create_product(
        self,
        name: str,
        price: float,
        description: str = None,
        stock: int = 0,
    ) -> dict:
        """
        创建产品接口
        POST /products
        @param name: 产品名称
        @param price: 产品价格
        @param description: 产品描述
        @return: 响应字典
        """
        data = {"name": name, "price": price, "stock": stock}
        if description:
            data["description"] = description
        response = self._client.post("/products", data=data)
        return response.data

    def get_all_products(self) -> dict:
        """
        获取所有产品接口
        GET /products
        @return: 响应字典
        """
        response = self._client.get("/products")
        return response.data

    def get_product_by_id(self, product_id: int) -> dict:
        """
        根据ID获取产品接口
        GET /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        response = self._client.get("/products", params={"id": product_id})
        return response.data

    def update_product_info(self, product_id: int, **kwargs) -> dict:
        """
        更新产品信息接口
        PUT /products?id={product_id}
        @param product_id: 产品ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self._client.put(f"/products/{product_id}", data=kwargs)
        return response.data

    def delete_product(self, product_id: int) -> dict:
        """
        删除产品接口
        DELETE /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        response = self._client.delete(f"/products/{product_id}")
        return response.data

            
        
            
        