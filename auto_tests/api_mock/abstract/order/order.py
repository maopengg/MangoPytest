# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 订单管理API - 不依赖Excel装饰器
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from typing import Dict, Any, Optional

from core.api.client import APIClient


class OrderAPI:
    """订单管理API类 - 直接调用API，不依赖Excel"""

    def __init__(self, base_url: str = "http://43.142.161.61:8003", headers: Dict = None):
        self.client = APIClient(base_url=base_url)
        if headers:
            self.client.headers = headers

    def create_order(self, user_id: int, product_id: int, quantity: int, 
                     total_price: float, status: str = "pending") -> Dict[str, Any]:
        """
        创建订单接口
        @param user_id: 用户ID
        @param product_id: 产品ID
        @param quantity: 数量
        @param total_price: 总价
        @param status: 订单状态
        @return: 响应数据字典
        """
        order_data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price,
            "status": status
        }
        response = self.client.post("/orders", json=order_data)
        return response.data

    def get_all_orders(self) -> Dict[str, Any]:
        """
        获取所有订单接口
        @return: 响应数据字典
        """
        response = self.client.get("/orders")
        return response.data

    def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
        """
        根据ID获取订单接口
        @param order_id: 订单ID
        @return: 响应数据字典
        """
        response = self.client.get("/orders", params={"id": order_id})
        return response.data

    def update_order_info(self, order_id: int, user_id: int, product_id: int,
                          quantity: int, total_price: float, status: str) -> Dict[str, Any]:
        """
        更新订单信息接口
        @param order_id: 订单ID
        @param user_id: 用户ID
        @param product_id: 产品ID
        @param quantity: 数量
        @param total_price: 总价
        @param status: 订单状态
        @return: 响应数据字典
        """
        update_data = {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total_price": total_price,
            "status": status
        }
        response = self.client.put(f"/orders/{order_id}", json=update_data)
        return response.data

    def delete_order(self, order_id: int) -> Dict[str, Any]:
        """
        删除订单接口
        @param order_id: 订单ID
        @return: 响应数据字典
        """
        response = self.client.delete(f"/orders/{order_id}")
        return response.data
