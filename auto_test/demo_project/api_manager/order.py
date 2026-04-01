# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏
from urllib.parse import urljoin

import requests


class OrderAPI:
    """订单API - 对应 /orders 接口"""

    def __init__(self):
        self._host = "http://localhost:8003"
        self._token = None

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip("/")

    def set_token(self, token: str):
        """设置认证token"""
        self._token = token

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {}
        if self._token:
            headers["X-Token"] = self._token
        return headers

    def create_order(self, product_id: int, quantity: int, user_id: int) -> dict:
        """
        创建订单接口
        POST /orders
        @param product_id: 产品ID
        @param quantity: 数量
        @param user_id: 用户ID
        @return: 响应字典
        """
        url = self._get_url("orders")
        response = requests.post(
            url,
            json={"product_id": product_id, "quantity": quantity, "user_id": user_id},
            headers=self._get_headers(),
        )
        return response.json()

    def get_all_orders(self) -> dict:
        """
        获取所有订单接口
        GET /orders
        @return: 响应字典
        """
        url = self._get_url("orders")
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_order_by_id(self, order_id: int) -> dict:
        """
        根据ID获取订单接口
        GET /orders/{order_id}
        @param order_id: 订单ID
        @return: 响应字典
        """
        url = self._get_url(f"orders/{order_id}")
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def update_order_info(self, order_id: int, **kwargs) -> dict:
        """
        更新订单信息接口
        PUT /orders?id={order_id}
        @param order_id: 订单ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        url = self._get_url("orders")
        response = requests.put(url, params={"id": order_id}, json=kwargs, headers=self._get_headers())
        return response.json()

    def delete_order(self, order_id: int) -> dict:
        """
        删除订单接口
        DELETE /orders?id={order_id}
        @param order_id: 订单ID
        @return: 响应字典
        """
        url = self._get_url("orders")
        response = requests.delete(url, params={"id": order_id}, headers=self._get_headers())
        return response.json()
