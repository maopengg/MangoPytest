# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class ProductAPI:
    """产品API - 对应 /products 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_product(self, name: str, price: float, description: str = None) -> dict:
        """
        创建产品接口
        POST /products
        @param name: 产品名称
        @param price: 产品价格
        @param description: 产品描述
        @return: 响应字典
        """
        url = self._get_url("products")
        data = {"name": name, "price": price}
        if description:
            data["description"] = description
        response = requests.post(url, json=data)
        return response.json()

    def get_all_products(self) -> dict:
        """
        获取所有产品接口
        GET /products
        @return: 响应字典
        """
        url = self._get_url("products")
        response = requests.get(url)
        return response.json()

    def get_product_by_id(self, product_id: int) -> dict:
        """
        根据ID获取产品接口
        GET /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        url = self._get_url("products")
        response = requests.get(url, params={"id": product_id})
        return response.json()

    def update_product_info(self, product_id: int, **kwargs) -> dict:
        """
        更新产品信息接口
        PUT /products?id={product_id}
        @param product_id: 产品ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        url = self._get_url("products")
        response = requests.put(url, params={"id": product_id}, json=kwargs)
        return response.json()

    def delete_product(self, product_id: int) -> dict:
        """
        删除产品接口
        DELETE /products?id={product_id}
        @param product_id: 产品ID
        @return: 响应字典
        """
        url = self._get_url("products")
        response = requests.delete(url, params={"id": product_id})
        return response.json()
