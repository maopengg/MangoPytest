# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单API - 使用 Core APIClient
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from auto_test.demo_project.core.api.client import APIClient


class OrderAPI:
    """订单API - 对应 /orders 接口"""

    def __init__(self):
        self._client = APIClient(base_url="http://localhost:8003")

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._client.set_base_url(host)

    def set_token(self, token: str):
        """设置认证token"""
        self._client.set_auth_token(token)

    def create_order(self, product_id: int, quantity: int, user_id: int) -> dict:
        """
        创建订单接口
        POST /orders
        @param product_id: 产品ID
        @param quantity: 数量
        @param user_id: 用户ID
        @return: 响应字典
        """
        response = self._client.post(
            "/orders",
            data={"product_id": product_id, "quantity": quantity, "user_id": user_id}
        )
        return response.data

    def get_all_orders(self) -> dict:
        """
        获取所有订单接口
        GET /orders
        @return: 响应字典
        """
        response = self._client.get("/orders")
        return response.data

    def get_order_by_id(self, order_id: int) -> dict:
        """
        根据ID获取订单接口
        GET /orders/{order_id}
        @param order_id: 订单ID
        @return: 响应字典
        """
        response = self._client.get(f"/orders/{order_id}")
        return response.data

    def update_order_info(self, order_id: int, **kwargs) -> dict:
        """
        更新订单信息接口
        PUT /orders?id={order_id}
        @param order_id: 订单ID
        @param kwargs: 更新字段
        @return: 响应字典
        """
        response = self._client.put(f"/orders/{order_id}", data=kwargs)
        return response.data

    def delete_order(self, order_id: int) -> dict:
        """
        删除订单接口
        DELETE /orders?id={order_id}
        @param order_id: 订单ID
        @return: 响应字典
        """
        response = self._client.delete(f"/orders/{order_id}")
        return response.data
