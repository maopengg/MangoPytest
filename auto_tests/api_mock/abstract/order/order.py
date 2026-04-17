# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:57
# @Author : 毛鹏

from auto_tests.api_mock import base_data
from core.models.api_model import ApiDataModel
from core.api.request_tool import RequestTool
from core.decorators import request_data


class OrderAPI(RequestTool):
    base_data = base_data

    @request_data(12)
    def create_order(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建订单接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(13)
    def get_all_orders(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有订单接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(14)
    def get_order_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取订单接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(15)
    def update_order_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新订单信息接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(16)
    def delete_order(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除订单接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
