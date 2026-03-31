# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class OrderAPI(RequestTool):
    """订单API - 对应 /orders 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_order(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建订单接口
        POST /orders
        @param data: ApiDataModel (包含 product_id, quantity, user_id)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("orders")
        return self.http(data)

    def get_all_orders(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有订单接口
        GET /orders
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("orders")
        return self.http(data)

    def get_order_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取订单接口
        GET /orders/{order_id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("orders")
        return self.http(data)

    def update_order_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新订单信息接口
        PUT /orders?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("orders")
        return self.http(data)

    def delete_order(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除订单接口
        DELETE /orders?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("orders")
        return self.http(data)
