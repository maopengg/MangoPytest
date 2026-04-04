# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 产品API - 使用 Core APIClient
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from .base import DemoProjectBaseAPI


class ProductAPI(DemoProjectBaseAPI):
    """产品API - 对应 /products 接口"""

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
        response = self.client.post("/products", json=data)
        return response.data

    def get_all_products(self) -> dict:
        """
        获取所有产品接口
        GET /products
        @return: 响应字典
        """
        response = self.client.get("/products")
        return response.data

    def get_product_by_id(self, product_id: int) -> dict:
        """
        根据ID获取产品接口
        GET /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        response = self.client.get("/products", params={"id": product_id})
        return response.data

    def update_product_info(self, product_id: int, **kwargs) -> dict:
        """
        更新产品信息接口
        PUT /products?id={product_id}
        @param product_id: 产品ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self.client.put(f"/products/{product_id}", json=kwargs)
        return response.data

    def delete_product(self, product_id: int) -> dict:
        """
        删除产品接口
        DELETE /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        response = self.client.delete(f"/products/{product_id}")
        return response.data
