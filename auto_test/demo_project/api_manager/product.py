# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 13:56
# @Author : 毛鹏
from urllib.parse import urljoin

from models.api_model import ApiDataModel
from tools.base_request.request_tool import RequestTool
from tools.decorator.response import request_data


class ProductAPI(RequestTool):
    """产品API - 对应 /products 接口"""

    def __init__(self):
        super().__init__()
        self._host = "http://localhost:8003"

    def set_host(self, host: str):
        """设置API服务器地址"""
        self._host = host.rstrip('/')

    def _get_url(self, path: str) -> str:
        """获取完整URL"""
        return urljoin(self._host + "/", path)

    def create_product(self, data: ApiDataModel) -> ApiDataModel:
        """
        创建产品接口
        POST /products
        @param data: ApiDataModel (包含 name, price, description)
        @return: ApiDataModel
        """
        data.request.url = self._get_url("products")
        return self.http(data)

    def get_all_products(self, data: ApiDataModel) -> ApiDataModel:
        """
        获取所有产品接口
        GET /products
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("products")
        return self.http(data)

    def get_product_by_id(self, data: ApiDataModel) -> ApiDataModel:
        """
        根据ID获取产品接口
        GET /products?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("products")
        return self.http(data)

    def update_product_info(self, data: ApiDataModel) -> ApiDataModel:
        """
        更新产品信息接口
        PUT /products?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("products")
        return self.http(data)

    def delete_product(self, data: ApiDataModel) -> ApiDataModel:
        """
        删除产品接口
        DELETE /products?id={id}
        @param data: ApiDataModel
        @return: ApiDataModel
        """
        data.request.url = self._get_url("products")
        return self.http(data)
