# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-01-18 14:05
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mango_mock.abstract.product.product import ProductAPI
from core.models.api_model import ApiDataModel
from tools.base_request.case_tool import CaseTool
from tools.decorator.response import case_data
from tools.obtain_test_data import ObtainTestData


@allure.epic('演示-API自动化-常规API-MockAPI服务')
class TestProduct(ProductAPI, CaseTool):
    test_data: ObtainTestData = ObtainTestData()

    @case_data([24, 25, 26, 27])
    def test_01(self, data: ApiDataModel):
        data = self.create_product(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([28, 29, 30, 31])
    def test_02(self, data: ApiDataModel):
        if data.test_case.id in [28, 29]:
            # 获取所有产品
            data = self.get_all_products(data)
        elif data.test_case.id in [30, 31]:
            # 根据ID获取产品
            data = self.get_product_by_id(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([32, 33, 34])
    def test_03(self, data: ApiDataModel):
        data = self.update_product_info(data)
        assert data.response.response_dict.get('message') is not None

    @case_data([35, 36, 37])
    def test_04(self, data: ApiDataModel):
        data = self.delete_product(data)
        assert data.response.response_dict.get('message') is not None


if __name__ == '__main__':
    pytest.main(['-v', 'test_product.py'])
