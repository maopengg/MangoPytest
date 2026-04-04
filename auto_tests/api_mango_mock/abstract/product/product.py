# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏

from auto_tests.api_mango_mock import base_data
from core.models.api_model import ApiDataModel
from core.api.request_tool import RequestTool
from core.decorators import request_data


class ProductAPI(RequestTool):
    base_data = base_data

    @request_data(7)
    def create_product(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建产品接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(8)
    def get_all_products(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有产品接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(9)
    def get_product_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取产品接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(10)
    def update_product_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新产品信息接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)

    @request_data(11)
    def delete_product(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除产品接口
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        return self.http(data)
